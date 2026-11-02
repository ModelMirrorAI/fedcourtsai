"""Count the rows whose salience band moves from sal-v6 to sal-v7 (caption-v4).

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/caption_v4_band_census.py
    ```

it reads every live-slice row of the salience gate's scored segment that
sal-v6's segment admits (sal-v7's is the same), bands it under both versions,
and appends to the file named by `CHECK_SUMMARY` the corpus vintage, a table of
the moves by status (pending or resolved) and band pair, and the case ids and
docket numbers that move, with each resolved row's disposition. caption-v4 can
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
from fedcourtsai.pipeline.caption import _scored_segment
from fedcourtsai.pipeline.salience import scorer

Move = tuple[str, str, str]  # (status, sal-v6 band, sal-v7 band)


def moves(db: Path) -> tuple[Counter[Move], list[tuple[str, str, str, str, str]]]:
    """The band moves, counted, and each moved row's identifiers."""
    v6, v7 = scorer("sal-v6"), scorer("sal-v7")
    counts: Counter[Move] = Counter()
    moved: list[tuple[str, str, str, str, str]] = []
    with corpus.connect_readonly(db) as conn:
        for row in corpus.iter_rows(conn, court="scotus"):
            if not corpus.is_live_slice(row) or not _scored_segment(row):
                continue
            if not v6.in_segment(row):
                continue
            before, after = v6.band(row), v7.band(row)
            if before == after:
                continue
            status = "pending" if row.disposition is None else "resolved"
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
    return counts, sorted(moved)


def render(counts: Counter[Move], moved: list[tuple[str, str, str, str, str]]) -> list[str]:
    lines = ["| status | sal-v6 band | sal-v7 band | rows |", "| --- | --- | --- | --: |"]
    for (status, before, after), n in sorted(counts.items()):
        lines.append(f"| {status} | {before} | {after} | {n} |")
    lines.append(f"\nTotal: {sum(counts.values())}\n")
    lines += ["| status | docket | case | move | disposition |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| {' | '.join(cells)} |" for cells in moved]
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
    lines = ["### Rows whose salience band moves from sal-v6 to sal-v7", ""]
    lines += ["`fedcourts corpus-info`:", ""]
    lines += [f"    {line}" for line in info.stdout.splitlines()]
    lines += ["", *render(*moves(db))]
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
