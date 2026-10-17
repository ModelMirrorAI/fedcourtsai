"""Census the increment claims a forward cell's run overtook, read from the ledger and the corpus.

Declared in a pull request's description as

    ```corpus-check
    uv run python scripts/checks/increment_timing_census.py
    ```

it walks every process-stamped forward prediction at the checkout carrying a
live increment claim — `response-requested-increment`, `referral-increment` or
`cvsg-increment` whose signal the frozen context did not already show — and
reads how the cell's run sat against the signal
(`set_aside.increment_timing`) twice:

- **ledger**, the reading the scorer and the boards apply: the cell's pre-mint
  poll (with its post-run poll where the first read the signal absent), else
  the committed signal date (`store.increment_signal_day` — the
  response-requested moment's `opened_at`, the outcome's CVSG date; a referral
  has none, so an unpolled referral is unassessable there);
- **corpus**, the check on it: the poll, else the corpus row's
  `response_requested_at` / `cvsg_date`, and for a referral the earliest dated
  referral entry on the case's latest live payload
  (`interim_signals.referral_date`). The latest payload is the one a same-day
  pull overwrote last, so an entry it lacks may still have been on the docket;
  a referral the row records and the payload does not date is counted
  unreadable.

Each reading files a claim `signal-before-run` (masked), `signal-during-run` or
`signal-on-run-day` (set aside), or neither, with the unassessable claims — a signal the record
shows but cannot date — counted apart. Every count (the tally table, the
undated referrals, the disagreeing readings) comes before the per-event
listings. Only counts and identifiers reach `CHECK_SUMMARY`: case ids, event
ids, claim ids, predictor counts and dates, never stored snapshot text, since
the summary is posted publicly (docs/corpus-check.md). The corpus vintage line
comes from `fedcourts corpus-info`, as in `corpus_vintage.py`.

Outside the lane, point `CHECK_SUMMARY` at any file and run it from a checkout
with a pulled corpus.
"""

from __future__ import annotations

import functools
import os
import subprocess
import sys
from collections import Counter, defaultdict
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal, get_args

from fedcourtsai import corpus
from fedcourtsai.config import get_settings
from fedcourtsai.pipeline.cert_signals import proceedings_entries
from fedcourtsai.pipeline.interim_signals import referral_date
from fedcourtsai.schemas import DocketPollRecord, Outcome, Prediction
from fedcourtsai.serialize import read_model
from fedcourtsai.set_aside import TIMED_INCREMENT_CLAIMS, increment_timing, polled_signal
from fedcourtsai.store import cell_polls, increment_signal_day

#: A reading's verdict: the timing (``set_aside.IncrementTiming``),
#: ``unassessable`` (the record shows the signal and cannot date it), or ``clear``.
Verdict = Literal[
    "signal-before-run", "signal-during-run", "signal-on-run-day", "unassessable", "clear"
]


@dataclass(frozen=True)
class LiveClaim:
    """One live increment claim on one forward cell."""

    case_id: str
    event_id: str
    predictor_id: str
    claim_id: str
    resolved: bool
    signal_seen: bool
    ledger: Verdict
    corpus: Verdict


def _live(prediction: Prediction, claim_id: str) -> bool:
    """Whether the frozen context left this increment claim something to forecast."""
    context = prediction.context
    if context is None or not context.signals_observable:
        return False
    if claim_id == "response-requested-increment":
        return context.response_requested is False
    if claim_id == "referral-increment":
        return context.referred_to_court is False
    return context.cvsg_date is None


def _signal_seen(claim_id: str, outcome: Outcome | None) -> bool:
    """Whether the committed outcome records the signal at resolution."""
    if outcome is None:
        return False
    if claim_id == "cvsg-increment":
        return outcome.signals is not None and outcome.signals.cvsg_date is not None
    if outcome.interim_signals is None:
        return False
    if claim_id == "referral-increment":
        return outcome.interim_signals.referred_to_court
    return outcome.interim_signals.response_requested


def _verdict(
    claim_id: str,
    prediction: Prediction,
    poll: DocketPollRecord | None,
    post_poll: DocketPollRecord | None,
    day: Callable[[], date | None],
    seen: bool,
) -> Verdict:
    timing = increment_timing(claim_id, prediction, poll, day, post_poll=post_poll)
    if timing is not None:
        return timing
    if polled_signal(poll, claim_id) is None and day() is None and seen:
        return "unassessable"
    return "clear"


def census(data_root: Path, corpus_day: Callable[[str, str], date | None]) -> Iterator[LiveClaim]:
    """Every live increment claim on a process-stamped forward cell, read both ways.

    ``corpus_day(case_id, claim_id)`` is the corpus reading's signal date.
    """
    cases = data_root / "cases"
    for path in sorted(cases.glob("*/*/events/*/predictions/*/*/prediction.json")):
        prediction = read_model(path, Prediction)
        context = prediction.context
        if (
            prediction.process_version is None
            or prediction.claims is None
            or context is None
            or context.mode != "forward"
        ):
            continue
        event_dir = path.parents[3]
        outcome_path = event_dir / "outcome.json"
        outcome = read_model(outcome_path, Outcome) if outcome_path.is_file() else None
        poll, post_poll = cell_polls(path.parent)
        stated = {claim.claim_id for claim in prediction.claims}
        for claim_id in TIMED_INCREMENT_CLAIMS:
            if claim_id not in stated or not _live(prediction, claim_id):
                continue
            seen = _signal_seen(claim_id, outcome)
            ledger_day = functools.partial(increment_signal_day, event_dir, claim_id, outcome)
            corpus_signal = functools.partial(corpus_day, prediction.case_id, claim_id)
            yield LiveClaim(
                case_id=prediction.case_id,
                event_id=prediction.event_id,
                predictor_id=prediction.predictor_id,
                claim_id=claim_id,
                resolved=outcome is not None,
                signal_seen=seen,
                ledger=_verdict(claim_id, prediction, poll, post_poll, ledger_day, seen),
                corpus=_verdict(claim_id, prediction, poll, post_poll, corpus_signal, seen),
            )


_VERDICTS: tuple[Verdict, ...] = get_args(Verdict)


def render(claims: list[LiveClaim], unreadable_referrals: int) -> str:
    """The summary's census section."""
    lines = [
        "increment claims a forward cell's run overtook (every process-stamped forward cell):",
        "",
        "| claim | reading | live | resolved | " + " | ".join(_VERDICTS) + " |",
        "| --- | --- | --- | --- | " + " | ".join("---" for _ in _VERDICTS) + " |",
    ]
    for claim_id in TIMED_INCREMENT_CLAIMS:
        rows = [c for c in claims if c.claim_id == claim_id]
        for reading in ("ledger", "corpus"):
            tally: Counter[str] = Counter(getattr(c, reading) for c in rows)
            resolved: Counter[str] = Counter(getattr(c, reading) for c in rows if c.resolved)
            cells = " | ".join(f"{tally[v]} ({resolved[v]} resolved)" for v in _VERDICTS)
            lines.append(
                f"| `{claim_id}` | {reading} | {len(rows)} | "
                f"{sum(1 for c in rows if c.resolved)} | {cells} |"
            )
    disagree = sorted(
        {
            (c.claim_id, c.case_id, c.event_id, c.ledger, c.corpus)
            for c in claims
            if c.ledger not in (c.corpus, "unassessable")
        }
    )
    lines += [
        "",
        "- referrals the corpus row records and the latest live payload does not date: "
        + f"{unreadable_referrals}",
        f"- ledger and corpus readings that disagree (beyond unassessable): {len(disagree)}",
        "",
    ]
    grouped: dict[tuple[str, str, str, str, str], list[LiveClaim]] = defaultdict(list)
    for c in claims:
        for reading in ("ledger", "corpus"):
            verdict = getattr(c, reading)
            if verdict != "clear":
                grouped[(reading, verdict, c.claim_id, c.case_id, c.event_id)].append(c)
    if grouped:
        lines += [
            "| reading | verdict | claim | case | event | predictors | resolved |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for (reading, verdict, claim_id, case_id, event_id), rows in sorted(grouped.items()):
            lines.append(
                f"| {reading} | {verdict} | `{claim_id}` | `{case_id}` | `{event_id}` | "
                f"{len(rows)} | {rows[0].resolved} |"
            )
    if disagree:
        lines += ["", "Ledger and corpus readings that disagree (beyond unassessable):", ""]
        lines += [f"- `{a}` `{b}` `{e}`: ledger {d}, corpus {f}" for a, b, e, d, f in disagree]
    return "\n".join(lines) + "\n"


def _corpus_reader(conn: Any) -> tuple[Callable[[str, str], date | None], Callable[[], int]]:
    """The corpus reading's signal date, and how many referrals it could not date."""
    unreadable: set[str] = set()

    @functools.cache
    def row(case_id: str) -> corpus.CorpusRow | None:
        return corpus.get_row(conn, case_id)

    @functools.cache
    def payload(case_id: str) -> Mapping[str, Any] | None:
        found = corpus.latest_live_snapshot(conn, case_id)
        return found[1] if found is not None else None

    def day(case_id: str, claim_id: str) -> date | None:
        record = row(case_id)
        if record is None:
            return None
        if claim_id == "response-requested-increment":
            return record.response_requested_at
        if claim_id == "cvsg-increment":
            return record.cvsg_date
        found = payload(case_id)
        dated = referral_date(proceedings_entries(found)) if found is not None else None
        if dated is None and record.referred_to_court:
            unreadable.add(case_id)
        return dated

    return day, lambda: len(unreadable)


def main() -> int:
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
        day, unreadable = _corpus_reader(conn)
        claims = list(census(settings.data_root, day))
        unreadable_referrals = unreadable()
    with Path(summary).open("a", encoding="utf-8") as handle:
        handle.write("`fedcourts corpus-info`:\n\n")
        handle.write(info.stdout)
        handle.write("\n")
        handle.write(render(claims, unreadable_referrals))
    sys.stderr.write(info.stderr)
    return info.returncode


if __name__ == "__main__":
    sys.exit(main())
