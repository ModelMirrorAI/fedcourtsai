"""Count the rows the live rotation's never-polled reserve still owes a poll.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/never_polled_reserve.py
    ```

it counts, per Term and numbering stream (paid below the IFP serial base, IFP
at or above it), every row :func:`fedcourtsai.corpus.never_polled_rows`
qualifies over the pulled corpus — the backlog the reserve drains oldest Term
first — and appends the table and the corpus vintage to the file named by
`CHECK_SUMMARY`. A Term that leaves the table has been drained; a row still
counted under a drained-looking Term is one whose poll failed in transit,
which the live cycle's failed queue names. Counts only, never stored text.

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
from fedcourtsai.supremecourt import IFP_SERIAL_BASE

# Every row the reserve could take: one page, so the scan reads to the end.
_EVERYTHING = 1_000_000


def _stream(docket_number: str) -> str:
    parsed = corpus.normalize_docket_number(docket_number) or ""
    serial = parsed.partition("-")[2]
    if not serial.isdigit():
        return "other"
    return "ifp" if int(serial) >= IFP_SERIAL_BASE else "paid"


def backlog(db: Path, *, term_floor_year: int = 2017) -> Counter[tuple[int, str]]:
    """Qualifying rows by (Term year, stream)."""
    with corpus.connect_readonly(db) as conn:
        rows = corpus.never_polled_rows(
            conn, limit=_EVERYTHING, term_floor_year=term_floor_year, exclude=()
        )
    counts: Counter[tuple[int, str]] = Counter()
    for row in rows:
        year = corpus.scotus_term_year(row.docket_number)
        if year is not None:
            counts[(year, _stream(row.docket_number))] += 1
    return counts


def render(counts: Counter[tuple[int, str]]) -> list[str]:
    lines = ["| Term | paid | IFP | other |", "| --- | --- | --- | --- |"]
    for year in sorted({year for year, _ in counts}):
        cells = [str(counts[(year, stream)]) for stream in ("paid", "ifp", "other")]
        lines.append(f"| OT{year} | " + " | ".join(cells) + " |")
    lines.append(f"\nTotal: {sum(counts.values())}")
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
    lines = ["### Rows the never-polled reserve still owes a poll", ""]
    lines += ["`fedcourts corpus-info`:", ""]
    lines += [f"    {line}" for line in info.stdout.splitlines()]
    lines += ["", *render(backlog(db))]
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
