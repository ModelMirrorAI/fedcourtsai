"""Census the dockets carrying more than one petitioner reply at the cert stage.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/cert_reply_census.py
    ```

it reads the latest stored snapshot of every live-polled SCOTUS cert docket
numbered in the Terms `--first-term` to `--last-term` (two-digit, default 16
to 26) and asks the document selector itself
(`pipeline.documents.select_documents`) for the filings it stores as
`cert-reply`. The bounds are therefore the selector's own: every reply of the
petitioner posting a `Main Document` link, before the grant and before the
first disposition entry, and on a direct appeal the appellant's first answer.
It reports to the file named by `CHECK_SUMMARY`:

- how many dockets were read and how many held no snapshot (read this first:
  a run that cannot reach the content store lands every docket here);
- how many carry one such reply and how many carry more, by count;
- of the dockets carrying more, how many have a later reply that follows an
  opposition filed after the reply before it, and how many have none;
- which of them have no disposition, and their docket numbers.

Counts and docket numbers only reach `CHECK_SUMMARY`, never an entry's text.
Payload reads are fanned across the content store's bounded reader pool
(`pipeline.prefetch.prefetch_by_case`), serial on a local blob. The corpus
vintage comes from `fedcourts corpus-info`, as in `corpus_vintage.py`.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import argparse
import itertools
import os
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.pipeline.documents import (
    KIND_BRIEF_IN_OPPOSITION,
    KIND_CERT_REPLY,
    select_documents,
)
from fedcourtsai.pipeline.prefetch import prefetch_by_case

_ENTRIES = "ProceedingsandOrder"


@dataclass
class Census:
    read: int = 0
    no_snapshot: int = 0
    by_count: Counter[int] = field(default_factory=Counter)
    after_opposition: list[str] = field(default_factory=list)
    no_later_opposition: list[str] = field(default_factory=list)
    undecided: list[str] = field(default_factory=list)


def _entry_index(payload: Mapping[str, Any], url: str) -> int | None:
    """The position of the entry posting ``url``, or ``None``."""
    for index, entry in enumerate(payload.get(_ENTRIES) or []):
        if not isinstance(entry, Mapping):
            continue
        for link in entry.get("Links") or []:
            if isinstance(link, Mapping) and str(link.get("DocumentUrl") or "").strip() == url:
                return index
    return None


def reply_positions(payload: Mapping[str, Any]) -> tuple[list[int], list[int]]:
    """Entry positions of every reply the selector takes, and of every opposition brief."""
    found: dict[str, list[int]] = {KIND_CERT_REPLY: [], KIND_BRIEF_IN_OPPOSITION: []}
    for ref in select_documents(payload):
        if ref.kind in found and (index := _entry_index(payload, ref.url)) is not None:
            found[ref.kind].append(index)
    return found[KIND_CERT_REPLY], found[KIND_BRIEF_IN_OPPOSITION]


def candidates(conn: corpus.ReadConnection, first: int, last: int) -> dict[str, tuple[str, bool]]:
    """Each docket to read: its number and whether it has a disposition."""
    rows: dict[str, tuple[str, bool]] = {}
    for record in conn.execute(
        "SELECT case_id, docket_number, disposition FROM cases "
        "WHERE court = 'scotus' AND last_live_polled IS NOT NULL"
    ):
        number = str(record["docket_number"] or "")
        match = re.fullmatch(r"(\d\d)-\d+", number)
        if match is None or not first <= int(match.group(1)) <= last:
            continue
        rows[str(record["case_id"])] = (number, record["disposition"] is not None)
    return dict(sorted(rows.items()))


def run_census(conn: corpus.ReadConnection, first: int, last: int) -> Census:
    census = Census()
    rows = candidates(conn, first, last)
    with prefetch_by_case(
        list(rows),
        lambda case_id: corpus.latest_snapshot(conn, case_id),
        thread_name_prefix="cert-reply",
    ) as stream:
        for case_id, snapshot in stream:
            census.read += 1
            if snapshot is None:
                census.no_snapshot += 1
                continue
            replies, opposition = reply_positions(snapshot[1])
            census.by_count[len(replies)] += 1
            if len(replies) < 2:
                continue
            number, decided = rows[case_id]
            follows = any(
                earlier < brief < later
                for earlier, later in itertools.pairwise(replies)
                for brief in opposition
            )
            (census.after_opposition if follows else census.no_later_opposition).append(number)
            if not decided:
                census.undecided.append(number)
    return census


def render(census: Census, first: int, last: int) -> str:
    several = sum(count for replies, count in census.by_count.items() if replies > 1)
    lines = [
        f"Cert-stage reply census, cert dockets of Terms {first} to {last}:",
        f"- dockets read: {census.read} (no stored snapshot: {census.no_snapshot})",
        f"- dockets carrying one reply: {census.by_count[1]}",
        f"- dockets carrying more than one: {several}",
        *(
            f"  - {replies} replies: {count}"
            for replies, count in sorted(census.by_count.items())
            if replies > 1
        ),
        "- of those, a later reply follows an opposition filed after the reply before it: "
        + f"{len(census.after_opposition)}",
        f"  - {', '.join(sorted(census.after_opposition)) or 'none'}",
        f"- of those, no opposition between the replies: {len(census.no_later_opposition)}",
        f"  - {', '.join(sorted(census.no_later_opposition)) or 'none'}",
        "- of those, dockets with no disposition: "
        + (", ".join(sorted(census.undecided)) or "none"),
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--first-term", type=int, default=16)
    parser.add_argument("--last-term", type=int, default=26)
    args = parser.parse_args(argv)
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    settings = get_settings()
    db = corpus.corpus_db_path(settings.corpus_root)
    info = subprocess.run(
        [sys.executable, "-m", "fedcourtsai.cli", "corpus-info"],
        capture_output=True,
        text=True,
        check=False,
    )
    with corpus.connect_readonly(db, backend=settings.corpus_backend) as conn:
        census = run_census(conn, args.first_term, args.last_term)
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("`fedcourts corpus-info`:\n\n")
        handle.write(info.stdout)
        handle.write(
            "payload reads: "
            + ("the per-case content store" if corpus.payload_reads_offloaded() else "the blob")
            + "\n\n"
        )
        handle.write(render(census, args.first_term, args.last_term))
    sys.stderr.write(info.stderr)
    if census.read and census.no_snapshot == census.read:
        print("FAILED: every docket read as holding no snapshot", file=sys.stderr)
        return 1
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
