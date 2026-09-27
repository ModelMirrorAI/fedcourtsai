"""The missed-forecast monitor: classify resolved events the ledger holds no forecast for.

A backstop on the far side of resolution, for any cause. The predict backlog's
case reconciliation (:class:`fedcourtsai.pipeline.pull.CaseReconciliation`)
catches owed work falling out of the derivation while the event is still open;
this catches whatever reaches resolution unforecast anyway — a derivation bug,
a cell that failed every attempt, a round that never ran — by reading committed
state after the fact.

Every SCOTUS event resolved inside the window whose committed predictions do not
cover every enabled predictor is classified once:

- **declined** — the pipeline chose not to forecast it, with the reason:
  ``out_of_scope``, ``non_forecastable_moment``, ``not_funded``, or
  ``resolved_before_a_round``;
- **missed** — everything else: an event the pipeline owed and did not deliver.

An event holding some predictions but not every enabled predictor's is a
**partial** gap, classified by the same rules; its missing predictors are named.

**What is read, and when.** The corpus row and event as they stand *now*, not
as they stood while the event was open — the corpus keeps no history of either.
Each rule leans the safe way on that:

- Selection is a one-way latch (``salience_selected`` only ever sets, bar a
  sanctioned unlatch), so a row selected now may have been unselected while the
  event was open. Reading it now can only turn a declined event into a missed
  one, never hide a miss.
- The scope latch ``predict_excluded`` and the scope rules only narrow as a
  docket's facts accrue, so a row out of scope now may have been in scope while
  the event was open, and reading it now can hide a miss there. That is the one
  direction this monitor can under-report, and it is stated rather than
  patched: the corpus holds nothing that would say when a latch was set.
- Forecastability is asked with :func:`fedcourtsai.store.is_forecastable_moment`,
  which drops every limb a disposition trips, so a resolved event is judged by
  the kind of moment it was rather than by its decided state.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import StrEnum
from pathlib import Path

from .. import corpus
from ..matrix import cell_failure_count, event_has_predictions
from ..paths import CasePaths
from ..registry import enabled_predictors
from ..schemas import Stage
from ..store import event_has_claimable_prediction, is_forecastable_moment

#: The UTC times of the scheduled predict rounds — ``run-predict.yml``'s two
#: ``schedule`` crons, daily. A test pins this tuple to the workflow file, so a
#: cron change that is not mirrored here fails the suite rather than quietly
#: skewing the ``resolved_before_a_round`` rule.
PREDICT_ROUND_TIMES_UTC: tuple[time, ...] = (time(14, 12), time(17, 32))

#: How far back a scheduled evaluate plan looks for predictionless resolutions.
#: A missed event is re-reported on every plan for this long after it resolves,
#: so one dropped plan or one unread log does not lose it; after that the
#: ``--missed-since`` backfill is the way back to it.
MISSED_LOOKBACK_DAYS = 7


class Verdict(StrEnum):
    declined = "declined"
    missed = "missed"


class DeclineReason(StrEnum):
    """Why the pipeline declined to forecast a resolved event, by design."""

    out_of_scope = "out_of_scope"
    non_forecastable_moment = "non_forecastable_moment"
    not_funded = "not_funded"
    resolved_before_a_round = "resolved_before_a_round"


@dataclass(frozen=True)
class PredictionlessEvent:
    """One resolved event whose committed predictions miss an enabled predictor."""

    case_id: str
    event_id: str
    resolved_at: date
    opened_at: date | None
    missing_predictors: tuple[str, ...]
    partial: bool
    verdict: Verdict
    reason: str
    detail: str

    def as_json(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "event_id": self.event_id,
            "resolved_at": self.resolved_at.isoformat(),
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "missing_predictors": list(self.missing_predictors),
            "partial": self.partial,
            "verdict": self.verdict.value,
            "reason": self.reason,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class PredictionlessReport:
    """What one scan over a resolution window found.

    ``undated`` counts resolved corpus events in ledger cases whose
    ``outcome.json`` could not be read for a resolution date, so they could be
    placed in no window at all. It is reported rather than guessed, because a
    non-zero value is itself something to look at.
    """

    since: date
    until: date
    events: tuple[PredictionlessEvent, ...]
    undated: int = 0

    @property
    def declined(self) -> tuple[PredictionlessEvent, ...]:
        return tuple(e for e in self.events if e.verdict is Verdict.declined)

    @property
    def missed(self) -> tuple[PredictionlessEvent, ...]:
        return tuple(e for e in self.events if e.verdict is Verdict.missed)

    def counts_json(self) -> dict[str, object]:
        """The plan's ``counts.predictionless_resolutions`` block: every count an event count."""
        declined_by_reason = {
            reason.value: sum(1 for e in self.declined if e.reason == reason.value)
            for reason in DeclineReason
        }
        return {
            "since": self.since.isoformat(),
            "until": self.until.isoformat(),
            "predictionless_events": len(self.events),
            "partial_gap_events": sum(1 for e in self.events if e.partial),
            "declined_events": len(self.declined),
            **{f"declined_{reason}_events": n for reason, n in declined_by_reason.items()},
            "missed_events": len(self.missed),
            "missed_partial_gap_events": sum(1 for e in self.missed if e.partial),
            "undated_events": self.undated,
        }

    def detail_json(self) -> dict[str, list[dict[str, object]]]:
        return {
            "missed": [e.as_json() for e in self.missed],
            "declined": [e.as_json() for e in self.declined],
        }


def had_a_scheduled_round(opened: date, resolved: date) -> bool:
    """Whether a scheduled predict round fell certainly inside the event's open span.

    Both dates are days, not instants, so the span is read at its narrowest: the
    event may have opened at the last moment of ``opened`` and resolved at the
    first of ``resolved``. A round counts only if it falls between those two
    instants — so a same-day or next-day resolution is never flagged on the
    round schedule's account, which is the conservative side for an alarm.
    """
    earliest = datetime.combine(opened + timedelta(days=1), time.min)
    latest = datetime.combine(resolved, time.min)
    day = earliest.date()
    while day < resolved:
        for at in PREDICT_ROUND_TIMES_UTC:
            if earliest <= datetime.combine(day, at) < latest:
                return True
        day += timedelta(days=1)
    return False


def _resolved_at(path: Path) -> date | None:
    """The ``resolved_at`` date of one committed ``outcome.json``, or ``None`` if unreadable."""
    try:
        return date.fromisoformat(str(json.loads(path.read_text())["resolved_at"]))
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _classify(
    conn: corpus.ReadConnection,
    data_root: Path,
    event: corpus.CorpusEvent,
    row: corpus.CorpusRow | None,
    *,
    partial: bool,
    resolved_at: date,
) -> tuple[Verdict, str, str]:
    """``(verdict, reason, detail)`` for one predictionless or partial event, first match."""
    if row is None or row.court != "scotus" or row.predict_excluded:
        return Verdict.declined, DeclineReason.out_of_scope, "the case row is latched out of scope"
    scope_reason = corpus.out_of_scope_reason_full(conn, row)
    if scope_reason is not None:
        return Verdict.declined, DeclineReason.out_of_scope, scope_reason
    if not is_forecastable_moment(event, row):
        return (
            Verdict.declined,
            DeclineReason.non_forecastable_moment,
            "not a moment the predict fan-out forecasts",
        )
    court, docket_str = row.case_id.split("/", 1)
    funded = (
        row.salience_selected
        or event.stage == Stage.merits
        or (
            partial
            and event_has_claimable_prediction(data_root, court, int(docket_str), event.event_id)
        )
    )
    if not funded:
        detail = (
            "never scored by the salience pass"
            if row.salience_version is None
            else "scored but not selected by the salience pass"
        )
        return Verdict.declined, DeclineReason.not_funded, detail
    # A partial gap is its own proof that a round ran while the event was open:
    # some engine's cell on it was minted and landed. So the round rule, which
    # only guards against flagging an event no round could have reached, is
    # asked of full gaps alone.
    if (
        not partial
        and event.opened_at is not None
        and not had_a_scheduled_round(event.opened_at, resolved_at)
    ):
        return (
            Verdict.declined,
            DeclineReason.resolved_before_a_round,
            f"opened {event.opened_at.isoformat()}, resolved {resolved_at.isoformat()}: "
            "no scheduled predict round fell certainly between",
        )
    return Verdict.missed, "owed_and_unforecast", ""


def scan_predictionless_resolutions(
    conn: corpus.ReadConnection,
    data_root: Path,
    predictors_path: Path,
    *,
    since: date,
    until: date,
) -> PredictionlessReport:
    """Classify every SCOTUS event resolved in ``[since, until]`` that an enabled predictor lacks.

    Driven from the corpus's resolved-event set, dated from the ledger's own
    ``outcome.json`` (the corpus keeps no per-event resolution date). A case
    with no ledger directory holds no outcome record and so no date, and is
    passed over with a single directory listing rather than a stat per event;
    on a SCOTUS corpus that is nearly every resolved event, since the bulk
    history resolved before the ledger existed.

    Coverage is per enabled predictor (``predictors_path``): an event with no
    committed prediction at all is a full gap, one with some but not every
    enabled predictor's is a **partial** gap. A missing predictor's recorded
    failures at the predict seam are named in the detail, because a gap with
    failures behind it is a cell that ran and failed rather than one that never
    ran, and the two want different remedies.
    """
    predictor_ids = [p.id for p in enabled_predictors(predictors_path)]
    court_dir = CasePaths(data_root, "scotus", 0).base.parent
    try:
        ledger_dockets = set(os.listdir(court_dir))
    except OSError:
        ledger_dockets = set()
    found: list[PredictionlessEvent] = []
    undated = 0
    rows: dict[str, corpus.CorpusRow | None] = {}
    for event in corpus.iter_resolved_events(conn, court="scotus"):
        court, docket_str = event.case_id.split("/", 1)
        if docket_str not in ledger_dockets:
            continue
        docket = int(docket_str)
        outcome = CasePaths(data_root, court, docket).event(event.event_id).outcome
        if not outcome.exists():
            undated += 1
            continue
        resolved_at = _resolved_at(outcome)
        if resolved_at is None:
            undated += 1
            continue
        if not since <= resolved_at <= until:
            continue
        missing = tuple(
            pid
            for pid in predictor_ids
            if not event_has_predictions(data_root, court, docket, event.event_id, predictor_id=pid)
        )
        if not missing:
            continue
        partial = event_has_predictions(data_root, court, docket, event.event_id)
        if event.case_id not in rows:
            rows[event.case_id] = corpus.get_row(conn, event.case_id)
        verdict, reason, detail = _classify(
            conn,
            data_root,
            event,
            rows[event.case_id],
            partial=partial,
            resolved_at=resolved_at,
        )
        if verdict is Verdict.missed:
            failures = {
                pid: n
                for pid in missing
                if (
                    n := cell_failure_count(
                        data_root, court, docket, event.event_id, pid, "predict"
                    )
                )
            }
            gap = "missing " + ", ".join(missing) if partial else "no committed prediction"
            detail = gap + (
                "; recorded predict failures: "
                + ", ".join(f"{pid} x{n}" for pid, n in failures.items())
                if failures
                else ""
            )
        found.append(
            PredictionlessEvent(
                case_id=event.case_id,
                event_id=event.event_id,
                resolved_at=resolved_at,
                opened_at=event.opened_at,
                missing_predictors=missing,
                partial=partial,
                verdict=verdict,
                reason=str(reason),
                detail=detail,
            )
        )
    found.sort(key=lambda e: (e.resolved_at, e.case_id, e.event_id))
    return PredictionlessReport(since=since, until=until, events=tuple(found), undated=undated)
