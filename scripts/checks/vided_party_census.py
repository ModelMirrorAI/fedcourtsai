"""Census the docket pairs a VIDED party filing ties, and which of them the Court links.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/vided_party_census.py
    ```

it reads the latest stored snapshot of every live-polled SCOTUS cert docket
numbered in the Terms `--first-term` to `--last-term` (two-digit, default 23
to 26) whose lower-court docket number another such docket shares, keys each
as the live poll does (`pipeline.vided.vided_keys`), and reports to the file
named by `CHECK_SUMMARY`:

- how many dockets were read, how many held no snapshot (read this first: a
  run that cannot reach the content store lands every docket here), and how
  many carry a party key;
- the pairs of dockets sharing a party key, and how many of those pairs the
  Court links as `Vide` on either docket's latest snapshot, how many share an
  amicus key as well, and how many neither: the pairs only the party key
  finds;
- the docket numbers of those pairs, and which of them have no disposition.

Only dockets that share a lower-court number are read, whatever court each
names, because a party key carries the case below and no other docket can
match one. The index column is the pre-filter and the payload's own fields
decide the key, court included, so a docket read may still key nothing. A
pair is counted as linked where either docket lists the other as `Vide`.

Counts and docket numbers only reach `CHECK_SUMMARY`, never an entry's text.
Payload reads are fanned across the content store's bounded reader pool
(`pipeline.prefetch.prefetch_by_case`), serial on a local blob. The corpus
vintage comes from `fedcourts corpus-info`, as in `corpus_vintage.py`.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.pipeline import vide_links
from fedcourtsai.pipeline.prefetch import prefetch_by_case
from fedcourtsai.pipeline.vided import is_party_key, vided_keys


@dataclass
class Census:
    read: int = 0
    no_snapshot: int = 0
    keyed: int = 0
    pairs: list[tuple[str, str]] = field(default_factory=list)
    vide: int = 0
    amicus: int = 0
    only: list[tuple[str, str]] = field(default_factory=list)
    undecided: list[str] = field(default_factory=list)


def candidates(conn: corpus.ReadConnection, first: int, last: int) -> dict[str, tuple[str, bool]]:
    """Each docket to read: its number and whether it has a disposition."""
    groups: dict[str, set[str]] = defaultdict(set)
    rows: dict[str, tuple[str, bool]] = {}
    for record in conn.execute(
        "SELECT case_id, docket_number, originating_docket_number, disposition "
        "FROM cases WHERE court = 'scotus' "
        "AND last_live_polled IS NOT NULL AND originating_docket_number IS NOT NULL"
    ):
        number = str(record["docket_number"] or "")
        match = re.fullmatch(r"(\d\d)-\d+", number)
        if match is None or not first <= int(match.group(1)) <= last:
            continue
        case_id = str(record["case_id"])
        rows[case_id] = (number, record["disposition"] is not None)
        for part in re.split(r"[,;]", str(record["originating_docket_number"])):
            lower = part.strip().strip("()").strip().casefold()
            if lower:
                groups[lower].add(case_id)
    wanted = {case_id for members in groups.values() if len(members) > 1 for case_id in members}
    return {case_id: rows[case_id] for case_id in sorted(wanted)}


def run_census(conn: corpus.ReadConnection, first: int, last: int) -> Census:
    census = Census()
    rows = candidates(conn, first, last)
    party: dict[str, set[str]] = {}
    amicus: dict[str, set[str]] = {}
    linked: dict[str, set[str]] = {}
    with prefetch_by_case(
        list(rows),
        lambda case_id: corpus.latest_snapshot(conn, case_id),
        thread_name_prefix="vided",
    ) as stream:
        for case_id, snapshot in stream:
            census.read += 1
            if snapshot is None:
                census.no_snapshot += 1
                continue
            keys = set(vided_keys(snapshot[1]) or [])
            party[case_id] = {key for key in keys if is_party_key(key)}
            amicus[case_id] = keys - party[case_id]
            linked[case_id] = set(vide_links.vide_docket_numbers(snapshot[1]))
    holders = sorted(case_id for case_id, keys in party.items() if keys)
    census.keyed = len(holders)
    for index, one in enumerate(holders):
        for two in holders[index + 1 :]:
            if not party[one] & party[two]:
                continue
            pair = (rows[one][0], rows[two][0])
            census.pairs.append(pair)
            by_court = pair[1] in linked[one] or pair[0] in linked[two]
            by_amicus = bool(amicus[one] & amicus[two])
            census.vide += by_court
            census.amicus += by_amicus
            if not by_court and not by_amicus:
                census.only.append(pair)
                census.undecided += [rows[case][0] for case in (one, two) if not rows[case][1]]
    return census


def render(census: Census, first: int, last: int) -> str:
    dockets = {number for pair in census.pairs for number in pair}
    lines = [
        f"VIDED party census, cert dockets of Terms {first} to {last} "
        + "sharing a lower-court number:",
        f"- dockets read: {census.read} (no stored snapshot: {census.no_snapshot})",
        f"- dockets carrying a party key: {census.keyed}",
        f"- pairs sharing a party key: {len(census.pairs)} over {len(dockets)} dockets",
        f"- of those pairs, linked as Vide: {census.vide}; sharing an amicus key: {census.amicus}",
        f"- pairs only the party key finds: {len(census.only)}",
        *(f"  - {one} and {two}" for one, two in sorted(census.only)),
        "- dockets in those pairs with no disposition: "
        + (", ".join(sorted(set(census.undecided))) or "none"),
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--first-term", type=int, default=23)
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
