"""Census the substantive applications the side-motion carve-out frees, old scan against new.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/side_motion_census.py
    ```

it compares the interim disposal scan as it stood before the side-motion
carve-out — the single pattern the freeze-record entry quotes, held here as
`OLD` — with the current `pipeline.outcome.interim_disposal_signal`, over every
SCOTUS substantive application (`application_kind == "substantive"` on an
application-form docket number), and reports to the file named by
`CHECK_SUMMARY`:

- **pass 1, pending applications** (latest stored snapshot): how many are
  pending, how many hold no snapshot (read this first: a run that cannot reach
  the content store lands every row here), how many the old scan fires on, how
  many the new scan still fires on, and the dockets freed — an upper bound on
  dockets the carve-out unparks, not a count of cells — and, listed after
  pass 2's counts, each freed or still-parked docket's case id, docket number
  and the number of its entries set aside;
- **pass 2, resolved applications** (last snapshot strictly before the
  resolution date): the outcome split, by stored disposition, for **freed**
  (the old scan fires, the new one does not), **still parked** (both fire)
  and **never fired** (the old scan does not), each with `n`; the rows
  skipped for want of a resolution date or a pre-resolution snapshot; and,
  last, each freed application's case id, docket number, disposition and
  set-aside entry count;
- two self-checks: whether `OLD` is still the current base pattern, and how
  many snapshots the new scan fires on where `OLD` does not (the carve-out is
  never wider, so this must be 0).

Every count is printed before either listing, so a summary cut short loses
listing rows before it loses a count. The census exits non-zero, with a
`FAILED:` line naming why, when `OLD` is no longer the base pattern, when the
new scan is wider, or when there are pending applications and every one of
them read as holding no snapshot — what an unaddressed content store produces,
since its read source then answers every read as empty rather than raising.

Pass 1's human leak read — reading each freed entry's text to confirm none is
a disposal of the application — cannot happen here: the entry text is stored
snapshot text, and the summary is posted publicly (docs/corpus-check.md). The
listing gives the identifiers to read it by, locally. Counts and identifiers
only reach `CHECK_SUMMARY`, never an entry's text.

Payload reads are fanned across the content store's bounded reader pool
(`pipeline.prefetch.prefetch_by_case`), serial on a local blob. The corpus
vintage comes from `fedcourts corpus-info`, as in `corpus_vintage.py`; beside
it the summary carries the `text source:` line `fedcourts corpus-info
--text-coverage` prints (bounded by a timeout, since that pass reads document
manifests) and the payload read source this process used. `--no-listings` drops the per-docket
listings.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.pipeline import outcome
from fedcourtsai.pipeline.outcome import entry_descriptions, interim_disposal_signal
from fedcourtsai.pipeline.prefetch import prefetch_by_case

#: The scan before the carve-out, as the freeze-record entry quotes it.
OLD = re.compile(
    r"\b(?:applications?|stays?|injunctions?|vacaturs?|motions?)\b[^.]{0,200}?"
    + r"\b(?:granted|denied|dismissed|withdrawn)\b",
    re.IGNORECASE,
)

BUCKETS = ("freed", "still_parked", "never_fired")


def old_entries(payload: Mapping[str, Any]) -> list[str]:
    return [d for d in entry_descriptions(payload) if OLD.search(d)]


def freed_entries(payload: Mapping[str, Any]) -> list[str]:
    """Every entry the old pattern fires on and the shipped scan does not."""
    return [
        d
        for d in old_entries(payload)
        if interim_disposal_signal({"ProceedingsandOrder": [{"Text": d}]}) is None
    ]


@dataclass(frozen=True)
class Listed:
    case_id: str
    docket_number: str
    label: str
    set_aside: int


@dataclass
class Census:
    pending: int = 0
    no_snapshot: int = 0
    old_fires: int = 0
    new_fires: int = 0
    freed_dockets: int = 0
    pass1: list[Listed] = field(default_factory=list)
    split: dict[str, Counter[str]] = field(
        default_factory=lambda: {bucket: Counter() for bucket in BUCKETS}
    )
    skipped: int = 0
    pass2: list[Listed] = field(default_factory=list)
    wider: int = 0


def substantive_applications(conn: Any) -> list[corpus.CorpusRow]:
    return [
        row
        for row in corpus.iter_rows(conn, court="scotus")
        if row.application_kind == "substantive"
        and corpus.is_scotus_application_form(row.docket_number)
    ]


def _note_wider(census: Census, payload: Mapping[str, Any], fired_old: bool) -> bool:
    fired_new = interim_disposal_signal(payload) is not None
    if fired_new and not fired_old:
        census.wider += 1
    return fired_new


def run_census(conn: Any) -> Census:
    census = Census()
    rows = substantive_applications(conn)
    _pending_pass(conn, rows, census)
    _resolved_pass(conn, rows, census)
    return census


def _pending_pass(conn: Any, rows: list[corpus.CorpusRow], census: Census) -> None:
    """Pass 1: each pending application's latest stored snapshot."""
    pending = {row.case_id: row for row in rows if row.disposition is None}
    census.pending = len(pending)

    def latest(case_id: str) -> tuple[date, dict[str, Any]] | None:
        return corpus.latest_snapshot(conn, case_id)

    with prefetch_by_case(list(pending), latest, thread_name_prefix="side-motion-1") as stream:
        for case_id, snap in stream:
            if snap is None:
                census.no_snapshot += 1
                continue
            payload = snap[1]
            fired_old = bool(old_entries(payload))
            still_fires = _note_wider(census, payload, fired_old)
            if not fired_old:
                continue
            census.old_fires += 1
            census.new_fires += still_fires
            census.freed_dockets += not still_fires
            entries = freed_entries(payload)
            if entries:
                label = "still parked" if still_fires else "FREED"
                row = pending[case_id]
                census.pass1.append(Listed(case_id, row.docket_number, label, len(entries)))


def _resolved_pass(conn: Any, rows: list[corpus.CorpusRow], census: Census) -> None:
    """Pass 2: each resolved application's last snapshot before its resolution date."""
    resolved: dict[str, tuple[corpus.CorpusRow, date]] = {}
    for row in rows:
        if row.disposition is None:
            continue
        resolved_on = corpus.resolution_date(row)
        if resolved_on is None:
            census.skipped += 1
            continue
        resolved[row.case_id] = (row, resolved_on)

    def before(case_id: str) -> tuple[date, dict[str, Any]] | None:
        return corpus.snapshot_at(conn, case_id, before=resolved[case_id][1])

    with prefetch_by_case(list(resolved), before, thread_name_prefix="side-motion-2") as stream:
        for case_id, snap in stream:
            if snap is None:
                census.skipped += 1
                continue
            row = resolved[case_id][0]
            payload = snap[1]
            fired_old = bool(old_entries(payload))
            fired_new = _note_wider(census, payload, fired_old)
            if not fired_old:
                bucket = "never_fired"
            elif fired_new:
                bucket = "still_parked"
            else:
                bucket = "freed"
            census.split[bucket][str(row.disposition)] += 1
            if bucket == "freed":
                census.pass2.append(
                    Listed(
                        case_id,
                        row.docket_number,
                        str(row.disposition),
                        len(freed_entries(payload)),
                    )
                )


def old_is_current_base() -> bool:
    """Whether `OLD` is still the shipped base pattern, pattern and flags."""
    current = getattr(outcome, "_INTERIM_DISPOSAL_RE", None)
    return isinstance(current, re.Pattern) and (current.pattern, current.flags) == (
        OLD.pattern,
        OLD.flags,
    )


def failures(census: Census, *, same: bool) -> list[str]:
    """Why this census's figures cannot be read as they stand (empty when they can)."""
    found: list[str] = []
    if not same:
        found.append("the old pattern is no longer the current base pattern")
    if census.wider:
        found.append(f"the new scan fires where the old does not ({census.wider} snapshots)")
    if census.pending and census.no_snapshot == census.pending:
        found.append(
            "every pending application read as holding no snapshot: the payload reads "
            + "reached no stored snapshot (an unaddressed content store reads as empty)"
        )
    return found


def render(census: Census, *, listings: bool, same: bool | None = None) -> str:
    same = old_is_current_base() if same is None else same
    lines = [
        "side-motion carve-out, old scan against new (SCOTUS substantive applications):",
        "",
        f"- old pattern is the current base pattern: {same}",
        f"- snapshots the new scan fires on and the old does not (must be 0): {census.wider}",
    ]
    lines += [f"- FAILED: {reason}" for reason in failures(census, same=same)]
    lines += [
        "",
        "Pass 1, pending applications (latest stored snapshot):",
        "",
        f"- pending={census.pending} no_snapshot={census.no_snapshot} "
        + f"old_fires={census.old_fires} new_fires={census.new_fires} "
        + f"freed_dockets={census.freed_dockets} "
        + "(an upper bound on dockets the carve-out unparks, not a count of cells)",
        "",
        "Pass 2, resolved applications (last pre-resolution snapshot), outcome split:",
        "",
    ]
    for bucket in BUCKETS:
        counts = census.split[bucket]
        lines.append(
            f"- {bucket}: n={sum(counts.values())} "
            + " ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        )
    lines.append(f"- skipped (no resolution date or no pre-resolution snapshot): {census.skipped}")
    if listings and census.pass1:
        lines += [
            "",
            "Pass 1, dockets with an entry set aside (case, docket, state, entries set aside):",
        ]
        lines += [
            f"- `{item.case_id}` {item.docket_number} {item.label} {item.set_aside}"
            for item in census.pass1
        ]
    if listings and census.pass2:
        lines += [
            "",
            "Pass 2, freed resolved applications (case, docket, disposition, entries set aside):",
        ]
        lines += [
            f"- `{item.case_id}` {item.docket_number} {item.label} {item.set_aside}"
            for item in census.pass2
        ]
    return "\n".join(lines) + "\n"


#: How long the `--text-coverage` read may take before its line is reported unread.
TEXT_SOURCE_TIMEOUT_SECONDS = 300
# The class of the exception a failed run raised, off the last line of its
# traceback. Only the class name reaches the summary, which the lane posts
# publicly: an exception's message can carry a path, a key or docket text.
_EXCEPTION_LINE = re.compile(
    r"^\s*([A-Za-z_][\w.]{0,79}(?:Error|Exception|Exit|Interrupt|Failure))(?::|\s*$)"
)


def failure_class(stderr: str) -> str | None:
    """The exception class a failed run's stderr ends on, or ``None``."""
    for line in reversed(stderr.splitlines()):
        match = _EXCEPTION_LINE.match(line)
        if match:
            return match.group(1)
    return None


def text_source_line() -> str:
    """The `text source:` line `fedcourts corpus-info --text-coverage` prints, alone."""
    try:
        run = subprocess.run(
            [sys.executable, "-m", "fedcourtsai.cli", "corpus-info", "--text-coverage"],
            capture_output=True,
            text=True,
            check=False,
            timeout=TEXT_SOURCE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"text source: not read (timed out after {TEXT_SOURCE_TIMEOUT_SECONDS} s)"
    for line in run.stdout.splitlines():
        if line.startswith("text source:"):
            return line
    raised = failure_class(run.stderr)
    reason = f"exit {run.returncode}: {raised}" if raised else f"exit {run.returncode}"
    return f"text source: not printed ({reason})"


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    listings = "--no-listings" not in args
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
    text_source = text_source_line()
    with corpus.connect_readonly(db, backend=settings.corpus_backend) as conn:
        census = run_census(conn)
    same = old_is_current_base()
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("`fedcourts corpus-info`:\n\n")
        handle.write(info.stdout)
        handle.write(text_source + "\n")
        handle.write(
            "payload reads: "
            + ("the per-case content store" if corpus.payload_reads_offloaded() else "the blob")
            + "\n\n"
        )
        handle.write(render(census, listings=listings, same=same))
    sys.stderr.write(info.stderr)
    if failures(census, same=same):
        return 1
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
