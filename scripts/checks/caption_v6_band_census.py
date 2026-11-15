"""Count the rows whose salience band moves from sal-v8 to sal-v9 (caption-v6).

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/caption_v6_band_census.py
    ```

it reads every live-slice row of the salience gate's scored segment that
sal-v8's segment admits (sal-v9's is the same), bands it under both versions,
and appends to the file named by `CHECK_SUMMARY` the corpus vintage, a table of
the moves by status (pending or resolved) and band pair, and the case ids and
docket numbers that move, with each resolved row's disposition, and a count of
the rows carrying an office entry of record at filing on the petitioner side
that caption-v4's party match does not read, split by whether the office is
the side's only counsel of record and by the row's caption-v2 class. caption-v6 can
only move a row into `federal`, so every move is a band → `federal` move.
Counts and identifiers only, never stored text.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.pipeline.caption import (
    _scored_segment,
    petitioner_class_v2,
    sg_counsel_of_record_for_petitioner,
)
from fedcourtsai.pipeline.counsel import office_entries_at_filing
from fedcourtsai.pipeline.salience import scorer

Move = tuple[str, str, str]  # (status, sal-v8 band, sal-v9 band)


Unread = tuple[str, str]  # ("sole" or "shared", caption-v2 class)


def _unread_office_entry(row: corpus.CorpusRow) -> str | None:
    """`sole` or `shared` where caption-v4 leaves an office entry of record unread."""
    if sg_counsel_of_record_for_petitioner(row):
        return None
    of_record = [
        entry
        for entry in row.counsel
        if entry.role == corpus.CounselRole.petitioner and entry.counsel_of_record
    ]
    office = office_entries_at_filing(of_record, filed=row.date_filed)
    if not office:
        return None
    return "sole" if len(office) == len(of_record) else "shared"


def moves(
    db: Path,
) -> tuple[Counter[Move], list[tuple[str, str, str, str, str]], Counter[str], Counter[Unread]]:
    """The band moves, each moved row's identifiers, the frame, and the unread entries."""
    v8, v9 = scorer("sal-v8"), scorer("sal-v9")
    counts: Counter[Move] = Counter()
    moved: list[tuple[str, str, str, str, str]] = []
    frame: Counter[str] = Counter()
    unread: Counter[Unread] = Counter()
    with corpus.connect_readonly(db) as conn:
        for row in corpus.iter_rows(conn, court="scotus"):
            if not corpus.is_live_slice(row) or not _scored_segment(row):
                continue
            if not v8.in_segment(row):
                continue
            status = "pending" if row.disposition is None else "resolved"
            frame[status] += 1
            shape = _unread_office_entry(row)
            if shape is not None:
                unread[(shape, petitioner_class_v2(row))] += 1
            before, after = v8.band(row), v9.band(row)
            if before == after:
                continue
            counts[(status, before, after)] += 1
            moved.append(
                (
                    status,
                    row.docket_number,
                    row.case_id,
                    f"{before} → {after}",
                    row.disposition or "",
                )
            )
    return counts, sorted(moved), frame, unread


def render(
    counts: Counter[Move],
    moved: list[tuple[str, str, str, str, str]],
    frame: Counter[str],
    unread: Counter[Unread],
) -> list[str]:
    lines = [f"Frame: {frame['resolved']} resolved, {frame['pending']} pending.", ""]
    lines += ["| status | sal-v8 band | sal-v9 band | rows |", "| --- | --- | --- | --: |"]
    for (status, before, after), n in sorted(counts.items()):
        lines.append(f"| {status} | {before} | {after} | {n} |")
    lines.append(f"\nTotal: {sum(counts.values())}\n")
    lines += ["| status | docket | case | move | disposition |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| {' | '.join(cells)} |" for cells in moved]
    lines += [
        "",
        "Office entries of record at filing, petitioner side, unread by caption-v4's match:",
        "",
        "| office is | caption-v2 class | rows |",
        "| --- | --- | --: |",
    ]
    lines += [f"| {shape} | {cls} | {n} |" for (shape, cls), n in sorted(unread.items())]
    return lines


def main() -> int:
    summary = os.environ.get("CHECK_SUMMARY")
    if not summary:
        print("CHECK_SUMMARY is unset; name the file to report to", file=sys.stderr)
        return 2
    db = corpus.corpus_db_path(get_settings().corpus_root)
    if not db.exists():
        print(f"no corpus at {db}; corpus-pull first", file=sys.stderr)
        return 1
    info = subprocess.run(
        [sys.executable, "-m", "fedcourtsai.cli", "corpus-info"],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = ["### Rows whose salience band moves from sal-v8 to sal-v9", ""]
    lines += ["`fedcourts corpus-info`:", ""]
    lines += [f"    {line}" for line in info.stdout.splitlines()]
    lines += ["", *render(*moves(db))]
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
