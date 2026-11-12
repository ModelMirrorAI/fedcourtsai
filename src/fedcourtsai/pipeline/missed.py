"""The missed-forecast monitor: classify resolved events the ledger holds no forecast for.

A backstop on the far side of resolution, for any cause. The predict backlog's
case reconciliation (:class:`fedcourtsai.pipeline.pull.CaseReconciliation`)
catches owed work falling out of the derivation while the event is still open;
this catches whatever reaches resolution unforecast anyway — a derivation bug,
a cell that failed every attempt, a round that never ran, a case the salience
pass never scored — by reading committed state after the fact.

Every SCOTUS event the corpus records resolved inside the window, whose
committed predictions do not cover every predictor owed it, is classified once:

- **declined** — the pipeline chose not to forecast it, with the reason:
  ``out_of_scope``, ``non_forecastable_moment``, ``not_funded``,
  ``predictor_not_enabled``, ``resolved_before_a_round``, or
  ``moment_window_closed``;
- **missed** — the pipeline owed it and did not deliver, with the reason:
  ``not_scored`` (in scope and open, but the salience pass never scored the
  case, so no funding decision was ever taken — a pipeline failure, not a
  decline; it is asked before the round rule, so a never-scored event resolved
  the next day is still a miss, the over-report direction),
  ``predictor_never_produced`` (every predictor the gap names is enabled but has
  no committed prediction anywhere — an engine failing every cell, or one just
  enabled), or ``owed_and_unforecast`` (everything else).

**Which predictors are owed.** An enabled predictor is owed an event when its
first committed prediction anywhere is dated on or before the resolution, when
it has **no** committed prediction anywhere (an engine that has never landed a
cell is failing, not absent), or when it has a recorded predict failure on this
very event. Only a predictor whose first prediction postdates the resolution,
with no failure on the event, is not owed — enabling an engine does not make
every earlier event a miss — and an event missing only such predictors is
declined ``predictor_not_enabled``.

An event holding some predictions but not every owed predictor's is a
**partial** gap, classified by the same rules; its missing predictors are named.

**The window is driven from the corpus, not the ledger.** An event the corpus
records resolved is dated from its committed ``outcome.json`` where one exists;
where none does, from the corpus row's decision date, and failing that from the
row's newest observation (a no-earlier-than bound, so it can only place an event
*later* than it resolved — and it moves forward with every poll, so such an
event keeps re-entering the lookback window rather than aging out of it; the
``date_source`` counts say how many rest on it). An in-window event with no
``outcome.json`` is itself reported (``no_outcome_record``) as an
outcome-writer defect: evaluate can never grade it, and a monitor that dated
only from the ledger would never see it.
Events with no date from any source are counted all-time and named where their
row is selected, because they can be placed in no window.

**What is read, and when.** The corpus row and event as they stand *now*, not
as they stood while the event was open — the corpus keeps no history of either.
The directions that leaves, and the one day granularity adds, stated rather
than patched:

- ``salience_selected`` is a latch that normally only sets, so a row selected
  now may have been unselected while the event was open, which can only turn a
  decline into a miss. But the over-selection unlatch can clear it on a pending
  petition, so a row unselected now may have been selected then — an event it
  declines as ``not_funded`` can hide a miss.
- ``predict_excluded`` is two-way (the scope reconcile both sets and clears it)
  and the row-rule scope inputs accrue, so a row out of scope now may have been
  in scope while the event was open, and a decline as ``out_of_scope`` can hide
  a miss. A decline on a *selected* row is reported as a contradiction, since
  selection runs over the in-scope set.
- ``opened_at`` is the docket date of the transition, not the day the pipeline
  first observed it, so ingestion lag makes the round rule *over*-report (a
  miss that no round could have reached) — the safe direction for an alarm.
- An event on an application docket is reachable from the later of its
  ``opened_at`` and the row's ``date_filed``. An application's first entry is
  dated when the papers were submitted, days before the Court dockets it, and
  no docket exists to poll until then. A ``date_filed`` later than the real
  docketing would hide a miss, which is why no other docket form is floored.
- A moment's window can be shorter than the event's open span, at both ends
  (:func:`_forecast_window`). The start is read from a table of instants,
  the end from the docket as stored **now**; where the stored docket cannot
  show the conference that closed a moment, no end is read and the event is
  judged on its resolution date, the over-report direction. Three readings
  can hide a miss instead. The end is read with the admission's own conference
  reading, so where that reading wrongly refused a cell (a conference the
  petition was taken off by an entry it does not recognize) the monitor
  declines the event the refusal cost. A distribution docketed late under an
  earlier date shows a conference now that the admission could not see then.
  And an instant in the table later than the moment's real first admission
  excuses the rounds between the two.
- Events are dated to the day, so merits funding counts a merits event only
  if it opened *before* the resolution day — the one a cert grant mints opens
  on the day the petition resolves. An unrelated event resolving the same day
  a merits event opened is therefore declined ``not_funded`` absent other
  funding, which can hide a miss when it resolved after the merits event
  opened.
- The default window is a lookback from today, so an event whose resolution is
  recorded more than that window after it happened never enters a scheduled
  window; ``--missed-since`` is the way back to it.

Forecastability is asked with :func:`fedcourtsai.store.is_forecastable_moment`,
which drops every limb a disposition trips, so a resolved event is judged by the
kind of moment it was rather than by its decided state.
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType

from .. import corpus, ids
from ..matrix import cell_failure_count, event_has_predictions
from ..paths import CasePaths
from ..registry import enabled_predictors
from ..schemas import Moment, Stage
from ..store import (
    PayloadReader,
    conference_bound_closed_on,
    event_has_claimable_prediction,
    is_forecastable_moment,
    live_payload_reader,
)
from . import moments

#: The UTC times of the scheduled predict rounds — ``run-predict.yml``'s two
#: ``schedule`` crons, daily. A test pins this tuple to the workflow file's daily
#: crons, so a change to them that is not mirrored here fails the suite rather
#: than quietly skewing the ``resolved_before_a_round`` rule.
PREDICT_ROUND_TIMES_UTC: tuple[time, ...] = (time(14, 12), time(17, 32))

#: How far back a scheduled evaluate plan looks for predictionless resolutions.
#: A missed event is re-reported on every plan for this long after it resolves,
#: so one dropped plan or one unread log does not lose it; after that the
#: ``--missed-since`` backfill is the way back to it.
MISSED_LOOKBACK_DAYS = 7


#: The UTC instant the predict fan-out first admitted each moment that was
#: declared, and its events minted, before any cell could be placed on it: the
#: committer time of the merge that carried the moment's process label to
#: ``main`` (``docs/freeze-record.md``, which a test binds each instant to). An
#: event of such a moment could not be forecast earlier, however long it had
#: been open, so the round rule counts no round before it. A moment absent
#: here has been forecast for as long as its events have existed.
MOMENT_FIRST_FORECAST_UTC: Mapping[tuple[Stage, Moment], datetime] = MappingProxyType(
    {
        (Stage.cert, Moment.sg_brief): datetime(2026, 10, 23, 2, 37, 11),
        (Stage.cert, Moment.relist): datetime(2026, 10, 23, 2, 37, 11),
        (Stage.merits, Moment.argued): datetime(2026, 10, 23, 2, 37, 11),
        (Stage.cert, Moment.response_requested): datetime(2026, 10, 29, 14, 16, 26),
    }
)


class Verdict(StrEnum):
    declined = "declined"
    missed = "missed"


class DeclineReason(StrEnum):
    """Why the pipeline declined to forecast a resolved event, by design."""

    out_of_scope = "out_of_scope"
    non_forecastable_moment = "non_forecastable_moment"
    not_funded = "not_funded"
    predictor_not_enabled = "predictor_not_enabled"
    resolved_before_a_round = "resolved_before_a_round"
    moment_window_closed = "moment_window_closed"


class MissReason(StrEnum):
    """Why an owed event went unforecast, where the monitor can say."""

    not_scored = "not_scored"
    predictor_never_produced = "predictor_never_produced"
    owed_and_unforecast = "owed_and_unforecast"


class DateSource(StrEnum):
    """Where an event's resolution date came from, strongest first."""

    outcome = "outcome"
    corpus_decision_date = "corpus_decision_date"
    last_observed = "last_observed"


@dataclass(frozen=True)
class PredictionlessEvent:
    """One resolved event whose committed predictions miss a predictor owed it."""

    case_id: str
    event_id: str
    resolved_at: date
    date_source: DateSource
    opened_at: date | None
    missing_predictors: tuple[str, ...]
    partial: bool
    selected: bool
    verdict: Verdict
    reason: str
    detail: str

    @property
    def scope_contradiction(self) -> bool:
        """Declined out of scope on a salience-selected row — selection runs in scope."""
        return self.reason == DeclineReason.out_of_scope and self.selected

    def as_json(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "event_id": self.event_id,
            "resolved_at": self.resolved_at.isoformat(),
            "date_source": self.date_source.value,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "missing_predictors": list(self.missing_predictors),
            "partial": self.partial,
            "selected": self.selected,
            "verdict": self.verdict.value,
            "reason": self.reason,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class UnrecordedResolution:
    """A resolved corpus event with no committed ``outcome.json`` — named, never skipped."""

    case_id: str
    event_id: str
    resolved_at: date | None
    date_source: DateSource | None
    selected: bool

    def as_json(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "event_id": self.event_id,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "date_source": self.date_source.value if self.date_source else None,
            "selected": self.selected,
        }


@dataclass(frozen=True)
class PredictionlessReport:
    """What one scan over a resolution window found.

    ``no_outcome_record`` names every in-window resolved event lacking an
    ``outcome.json``, whatever its coverage. ``undated_all_time`` counts
    resolved events no source could date at all — ledger-wide, not windowed,
    since there is no date to window by — and ``undated_selected`` names those
    on a salience-selected row, the ones that can matter.
    """

    since: date
    until: date
    events: tuple[PredictionlessEvent, ...]
    no_outcome_record: tuple[UnrecordedResolution, ...] = ()
    undated_all_time: int = 0
    undated_selected: tuple[UnrecordedResolution, ...] = ()

    @property
    def declined(self) -> tuple[PredictionlessEvent, ...]:
        return tuple(e for e in self.events if e.verdict is Verdict.declined)

    @property
    def missed(self) -> tuple[PredictionlessEvent, ...]:
        return tuple(e for e in self.events if e.verdict is Verdict.missed)

    @property
    def scope_contradictions(self) -> tuple[PredictionlessEvent, ...]:
        return tuple(e for e in self.events if e.scope_contradiction)

    def counts_json(self) -> dict[str, object]:
        """The plan's ``counts.predictionless_resolutions`` block: every count an event count."""
        return {
            "since": self.since.isoformat(),
            "until": self.until.isoformat(),
            "predictionless_events": len(self.events),
            "partial_gap_events": sum(1 for e in self.events if e.partial),
            "declined_events": len(self.declined),
            **{
                f"declined_{reason.value}_events": sum(
                    1 for e in self.declined if e.reason == reason.value
                )
                for reason in DeclineReason
            },
            "declined_out_of_scope_on_selected_row_events": len(self.scope_contradictions),
            "missed_events": len(self.missed),
            **{
                f"missed_{reason.value}_events": sum(
                    1 for e in self.missed if e.reason == reason.value
                )
                for reason in MissReason
            },
            "missed_partial_gap_events": sum(1 for e in self.missed if e.partial),
            "no_outcome_record_events": len(self.no_outcome_record),
            "no_outcome_record_on_selected_row_events": sum(
                1 for u in self.no_outcome_record if u.selected
            ),
            **{
                f"dated_from_{source.value}_events": sum(
                    1 for e in self.events if e.date_source is source
                )
                for source in DateSource
            },
            "undated_events_all_time": self.undated_all_time,
            "undated_on_selected_row_events_all_time": len(self.undated_selected),
        }

    def detail_json(self) -> dict[str, list[dict[str, object]]]:
        return {
            "missed": [e.as_json() for e in self.missed],
            "declined": [e.as_json() for e in self.declined],
            "no_outcome_record": [u.as_json() for u in self.no_outcome_record],
            "undated_on_selected_row": [u.as_json() for u in self.undated_selected],
        }


def had_a_scheduled_round(
    opened: date, resolved: date, *, not_before: datetime | None = None
) -> bool:
    """Whether a scheduled predict round fell certainly inside the event's open span.

    Both dates are days, not instants, so the span is read at its narrowest: the
    event may have opened at the last moment of ``opened`` and resolved at the
    first of ``resolved``. A round counts only if it falls between those two
    instants — so a same-day or next-day resolution is never flagged on the
    round schedule's account, which is the conservative side for an alarm.

    ``not_before`` is a UTC instant no earlier round counts from: the moment
    was not forecast until then (:data:`MOMENT_FIRST_FORECAST_UTC`).
    """
    earliest = datetime.combine(opened + timedelta(days=1), time.min)
    if not_before is not None and not_before > earliest:
        earliest = not_before
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


def _corpus_date(
    event: corpus.CorpusEvent, row: corpus.CorpusRow | None
) -> tuple[date | None, DateSource | None]:
    """An event's resolution date from the corpus row, for an event with no outcome record.

    The row's decision date for the event's stage — the docket's ``date_decided``
    for a merits event (a granted petition's cert date is not its judgment), the
    petition-stage :func:`fedcourtsai.corpus.resolution_date` otherwise — and
    failing that the row's newest observation, which bounds the resolution from
    above: the corpus cannot have recorded it before it last saw the docket.
    """
    if row is None:
        return None, None
    decided = row.date_decided if event.stage == Stage.merits else corpus.resolution_date(row)
    if decided is not None:
        return decided, DateSource.corpus_decision_date
    observed = [s for s in (row.last_live_polled, row.last_pulled) if s is not None]
    if observed:
        return max(observed), DateSource.last_observed
    return None, None


def _first_prediction_dates(data_root: Path, predictor_ids: list[str]) -> dict[str, date | None]:
    """The date of each predictor's earliest committed prediction anywhere in the ledger.

    Read off the run directory names (UTC run ids), one glob per predictor. A
    predictor is owed a forecast on an event only if it was producing forecasts
    by the time the event resolved; this is the evidence for "it was".
    """
    first: dict[str, date | None] = {}
    cases_root = CasePaths(data_root, "scotus", 0).base.parent.parent
    for pid in predictor_ids:
        earliest: date | None = None
        for path in cases_root.glob(f"*/*/events/*/predictions/{pid}/*/prediction.json"):
            try:
                day = ids.parse_run_id(path.parent.name).date()
            except ValueError:
                continue
            if earliest is None or day < earliest:
                earliest = day
        first[pid] = earliest
    return first


def _merits_funded(events: list[corpus.CorpusEvent], resolved_at: date) -> bool:
    """Whether the case carried a merits event opened before ``resolved_at``.

    The walk funds every event of a case with an open merits event (the Court's
    own selection); an event resolved after such a proceeding opened was
    funded the same way.

    Strictly before: the merits event is minted by the cert grant, which is the
    petition's own resolution, so on a granted petition it opens on exactly the
    day the cert-stage event resolves. Counting that day would read the grant as
    having funded the forecast of itself, and file an unselected grant as a
    pipeline miss rather than a salience decline. The cost is the same-day
    sliver where an unrelated event resolves after a merits event opened that
    morning — an under-report this monitor cannot separate from the grant case
    at the day granularity it dates every event to.
    """
    return any(
        e.stage == Stage.merits and (e.opened_at is None or e.opened_at < resolved_at)
        for e in events
    )


def _forecast_window(
    event: corpus.CorpusEvent,
    event_opened: date,
    row: corpus.CorpusRow,
    resolved_at: date,
    payloads: PayloadReader,
) -> tuple[DeclineReason, str] | None:
    """The decline a full gap earns because no round could reach it, or ``None``.

    Two rules, the plain one first. ``resolved_before_a_round``: no scheduled
    round fell certainly between the day the event could first be polled (its
    ``opened_at``, or on an application docket the later of that and the
    docket's ``date_filed``) and the day it resolved. ``moment_window_closed``:
    rounds ran in that span, but none inside the part of it the moment was
    forecastable for. A moment's window
    opens no earlier than the instant its cells were first admitted
    (:data:`MOMENT_FIRST_FORECAST_UTC`), and a conference-bounded cert moment's
    closes on the first conference that considers the petition after the
    trigger (:func:`fedcourtsai.store.conference_bound_closed_on`): a relist
    forecasts the conference it was relisted for, and the petition's later
    relists and eventual disposition belong to no cell the fan-out would place.
    """
    opened = event_opened
    filed = row.date_filed
    if (
        filed is not None
        and filed > opened
        and corpus.is_scotus_application_form(row.docket_number)
    ):
        opened = filed
    since = (
        f"opened {event_opened.isoformat()}"
        if opened == event_opened
        else f"opened {event_opened.isoformat()} on a docket filed {opened.isoformat()}"
    )
    if not had_a_scheduled_round(opened, resolved_at):
        return (
            DeclineReason.resolved_before_a_round,
            f"{since}, resolved {resolved_at.isoformat()}: "
            "no scheduled predict round fell certainly between",
        )
    spec = moments.spec_for(event.event_id)
    first_forecast = (
        MOMENT_FIRST_FORECAST_UTC.get((spec.stage, spec.moment)) if spec is not None else None
    )
    conference = conference_bound_closed_on(event, through=resolved_at, payloads=payloads)
    closed = conference if conference is not None else resolved_at
    if had_a_scheduled_round(opened, closed, not_before=first_forecast):
        return None
    bounds = []
    if first_forecast is not None and first_forecast > datetime.combine(
        opened + timedelta(days=1), time.min
    ):
        bounds.append(f"the moment was first forecast {first_forecast:%Y-%m-%d %H:%M}Z")
    if conference is not None:
        bounds.append(f"the conference of {conference.isoformat()} closed it")
    return (
        DeclineReason.moment_window_closed,
        f"{since}, resolved {resolved_at.isoformat()}; "
        + " and ".join(bounds)
        + ": no scheduled predict round fell certainly inside the moment's window",
    )


def _classify(  # noqa: PLR0911 - one early return per declared rule
    conn: corpus.ReadConnection,
    data_root: Path,
    event: corpus.CorpusEvent,
    row: corpus.CorpusRow | None,
    *,
    partial: bool,
    owed_missing: tuple[str, ...],
    resolved_at: date,
    payloads: PayloadReader,
) -> tuple[Verdict, str, str]:
    """``(verdict, reason, detail)`` for one predictionless or partial event, first match."""
    if row is None or row.court != "scotus" or row.predict_excluded:
        return Verdict.declined, DeclineReason.out_of_scope, "the case row is latched out of scope"
    scope_reason = corpus.out_of_scope_reason_full(conn, row)
    if scope_reason is not None:
        return Verdict.declined, DeclineReason.out_of_scope, scope_reason
    if event.stage != Stage.merits and corpus.is_ifp_petition(row):
        # A merits grant readmits an IFP docket to scope, but only its merits
        # events: its petition-stage events stay under the IFP exclusion.
        return (
            Verdict.declined,
            DeclineReason.out_of_scope,
            "in-forma-pauperis petition — excluded below the merits stage",
        )
    if not is_forecastable_moment(event, row):
        return (
            Verdict.declined,
            DeclineReason.non_forecastable_moment,
            "not a moment the predict fan-out forecasts",
        )
    court, docket_str = row.case_id.split("/", 1)
    funded = (
        row.salience_selected
        or _merits_funded(corpus.events_for_case(conn, row.case_id), resolved_at)
        or (
            partial
            and event_has_claimable_prediction(data_root, court, int(docket_str), event.event_id)
        )
    )
    if not funded:
        if row.salience_version is None:
            return (
                Verdict.missed,
                MissReason.not_scored,
                "in scope and forecastable, but the salience pass never scored the case",
            )
        return (
            Verdict.declined,
            DeclineReason.not_funded,
            "scored but not selected by the salience pass",
        )
    if not owed_missing:
        return (
            Verdict.declined,
            DeclineReason.predictor_not_enabled,
            "every missing predictor's first committed prediction postdates the resolution",
        )
    # A partial gap is its own proof that a round ran while the event was open:
    # some engine's cell on it was minted and landed. So the round rule, which
    # only guards against flagging an event no round could have reached, is
    # asked of full gaps alone.
    if not partial and event.opened_at is not None:
        unreachable = _forecast_window(event, event.opened_at, row, resolved_at, payloads)
        if unreachable is not None:
            return Verdict.declined, unreachable[0], unreachable[1]
    return Verdict.missed, MissReason.owed_and_unforecast, ""


def _decided_events(
    conn: corpus.ReadConnection,
    row_for: Callable[[str], corpus.CorpusRow | None],
) -> Iterator[corpus.CorpusEvent]:
    """Every SCOTUS event whose question is decided: corpus-resolved, or open on a decided row.

    The second arm is the declared moments detection declined: re-extraction
    never closes a stored event, so such a moment stays **open** on a row that
    records its stage decided (:func:`fedcourtsai.corpus.stage_shows_decided`),
    with no ``outcome.json``. Reading the resolved set alone would drop it from
    ``no_outcome_record`` — and the declined shapes (unreadable, undated, GVR
    and dismissal orders) are outcome-correlated, so the drop would not be
    neutral.

    A merits event closed because its proceeding ended with nothing decided
    (``merits-terminated``) is left out: its question was never decided, so it
    is neither a missed forecast nor a missing outcome, and with no decision
    date it would be dated from the row's newest observation, which moves
    forward on every re-pull.
    """
    for event in corpus.iter_resolved_events(conn, court="scotus"):
        if event.resolved_without_outcome_reason != corpus.NO_OUTCOME_MERITS_TERMINATED:
            yield event
    for event in corpus.open_events_on_decided_rows(conn, court="scotus"):
        spec = moments.spec_for(event.event_id)
        if spec is None:
            continue
        row = row_for(event.case_id)
        if row is not None and corpus.stage_shows_decided(row, spec.stage):
            yield event


def scan_predictionless_resolutions(  # noqa: PLR0912, PLR0915 - one pass, many facts
    conn: corpus.ReadConnection,
    data_root: Path,
    predictors_path: Path,
    *,
    since: date,
    until: date,
) -> PredictionlessReport:
    """Classify every SCOTUS event resolved in ``[since, until]`` that a predictor owed lacks.

    Driven from the corpus — its resolved-event set and the declared moments
    left open on a row that records their stage decided (:func:`_decided_events`)
    — so an event the ledger never recorded is still seen. Dated from the
    event's ``outcome.json`` where the ledger holds one, otherwise from the
    corpus row (:func:`_corpus_date`); an in-window event with no
    ``outcome.json`` is also listed on ``no_outcome_record``.

    Coverage is per enabled predictor (``predictors_path``), but a predictor is
    **owed** an event only if its first committed prediction anywhere predates
    or matches the event's resolution — enabling an engine does not make every
    event resolved before it a miss. An event missing only never-yet-enabled
    predictors is declined ``predictor_not_enabled``. A missing predictor's
    recorded failures at the predict seam are named in a miss's detail, because
    a gap with failures behind it is a cell that ran and failed rather than one
    that never ran, and the two want different remedies.
    """
    predictor_ids = [p.id for p in enabled_predictors(predictors_path)]
    court_dir = CasePaths(data_root, "scotus", 0).base.parent
    try:
        ledger_dockets = set(os.listdir(court_dir))
    except OSError:
        ledger_dockets = set()
    first_dates: dict[str, date | None] | None = None
    found: list[PredictionlessEvent] = []
    unrecorded: list[UnrecordedResolution] = []
    undated_all_time = 0
    undated_selected: list[UnrecordedResolution] = []
    rows: dict[str, corpus.CorpusRow | None] = {}
    payloads = live_payload_reader(conn)

    def row_for(case_id: str) -> corpus.CorpusRow | None:
        if case_id not in rows:
            rows[case_id] = corpus.get_row(conn, case_id)
        return rows[case_id]

    for event in _decided_events(conn, row_for):
        court, docket_str = event.case_id.split("/", 1)
        docket = int(docket_str)
        in_ledger = docket_str in ledger_dockets
        outcome = CasePaths(data_root, court, docket).event(event.event_id).outcome
        outcome_present = in_ledger and outcome.exists()
        resolved_at = _resolved_at(outcome) if outcome_present else None
        source: DateSource | None = DateSource.outcome if resolved_at else None
        recorded = resolved_at is not None
        if not recorded:
            resolved_at, source = _corpus_date(event, row_for(event.case_id))
        row_selected = bool((row := row_for(event.case_id)) and row.salience_selected)
        if resolved_at is None or source is None:
            undated_all_time += 1
            if row_selected:
                undated_selected.append(
                    UnrecordedResolution(event.case_id, event.event_id, None, None, True)
                )
            continue
        if not since <= resolved_at <= until:
            continue
        if not recorded:
            unrecorded.append(
                UnrecordedResolution(
                    event.case_id, event.event_id, resolved_at, source, row_selected
                )
            )
        missing = tuple(
            pid
            for pid in predictor_ids
            if not in_ledger
            or not event_has_predictions(data_root, court, docket, event.event_id, predictor_id=pid)
        )
        if not missing:
            continue
        partial = len(missing) < len(predictor_ids)
        if first_dates is None:
            first_dates = _first_prediction_dates(data_root, predictor_ids)
        failures = {
            pid: n
            for pid in missing
            if in_ledger
            and (n := cell_failure_count(data_root, court, docket, event.event_id, pid, "predict"))
        }
        never_produced = {pid for pid in missing if first_dates.get(pid) is None}
        owed_missing = tuple(
            pid
            for pid in missing
            if pid in never_produced
            or pid in failures
            or ((first := first_dates.get(pid)) is not None and first <= resolved_at)
        )
        verdict, reason, detail = _classify(
            conn,
            data_root,
            event,
            row,
            partial=partial,
            owed_missing=owed_missing,
            resolved_at=resolved_at,
            payloads=payloads,
        )
        reported_missing = owed_missing if verdict is Verdict.missed else missing
        if verdict is Verdict.missed and reason == MissReason.owed_and_unforecast:
            if all(pid in never_produced for pid in owed_missing):
                reason = MissReason.predictor_never_produced
            gap = "missing " + ", ".join(owed_missing) if partial else "no committed prediction"
            owed_failures = {pid: n for pid, n in failures.items() if pid in owed_missing}
            detail = gap + (
                "; recorded predict failures: "
                + ", ".join(f"{pid} x{n}" for pid, n in owed_failures.items())
                if owed_failures
                else ""
            )
            silent = sorted(never_produced & set(owed_missing))
            if silent:
                detail += "; never produced a committed prediction: " + ", ".join(silent)
        if not recorded:
            what = "no readable outcome.json" if outcome_present else "no outcome.json"
            detail = (detail + "; " if detail else "") + (
                f"{what} — dated from the corpus ({source.value})"
            )
        found.append(
            PredictionlessEvent(
                case_id=event.case_id,
                event_id=event.event_id,
                resolved_at=resolved_at,
                date_source=source,
                opened_at=event.opened_at,
                missing_predictors=reported_missing,
                partial=partial,
                selected=row_selected,
                verdict=verdict,
                reason=str(reason),
                detail=detail,
            )
        )
    found.sort(key=lambda e: (e.resolved_at, e.case_id, e.event_id))
    unrecorded.sort(key=lambda u: (u.resolved_at or date.min, u.case_id, u.event_id))
    return PredictionlessReport(
        since=since,
        until=until,
        events=tuple(found),
        no_outcome_record=tuple(unrecorded),
        undated_all_time=undated_all_time,
        undated_selected=tuple(undated_selected),
    )
