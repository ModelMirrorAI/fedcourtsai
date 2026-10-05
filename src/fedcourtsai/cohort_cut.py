"""The counted cohort, cut by the conference each event was distributed for.

``fedcourts conference-set --counted`` reads this. The release write-up
registers a cohort — the petitions distributed for one conference, plus the
CVSG and interim events the same rule re-owed — but nothing in the ledger, the
export or the boards carries a conference: the prediction ``context`` freezes
the band, not the conference. This module joins the two halves. The ledger
supplies the counted population, its band, its counted predictors and its
resolution; the corpus supplies the conference.

**Two conferences, read at two moments, answering two questions.**

- ``conference`` is read **as at each counted cell's cut**: the conference the
  petition was distributed for when its cell was provisioned. It explains a
  cell — which conference the forecast was made against — and is never the
  cohort selector, because whether a reschedule lands before or after a
  re-forecast is a fact about pipeline timing, not about the petition.
- ``conference_at_registration`` (with ``--registered-at``) is read **as at the
  registration day**, and is one input to ``registered``: the reconstruction of
  the registered rule's membership — an event at a re-predict moment that held
  a de-counted cell by that day, was still forward then, and, at the distribution
  moment, was distributed for a conference still ahead. Membership is fixed at
  registration, so a registered petition rescheduled afterwards stays in the
  denominator and the move is disclosed rather than dropping it.

Neither is the current ``distributed_for_conference`` column, which is the live
channel's latest-entry-wins value and moves on every relist or reschedule. Both
are reconstructed from the case's latest live-shaped payload with
:func:`fedcourtsai.pipeline.asof.asof_conference` (entries filed strictly before
the bound). Where no live payload is readable the current column stands in, the
cell says so (``conference_source: current``), and the cut counts the fallbacks
in ``conference_fallbacks`` so a fallback figure can be refused mechanically.

Read-only over both stores: it opens the corpus read-only and writes nothing.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

from . import corpus
from .blinding import latest_prediction_dirs
from .integrity import FORWARD_CLAIM_POLICY, cell_clock
from .paths import CasePaths, EventPaths
from .pipeline import asof
from .pipeline.pull import REPREDICT_MOMENTS
from .process_version import is_frozen
from .schemas import (
    CountedConferenceCell,
    CountedConferenceCut,
    CountedConferenceEvent,
    CountedConferenceTotal,
    ExportCorpusVintage,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    Stage,
)
from .serialize import read_model
from .store import (
    iter_predicted_events,
    normalized_moment,
    normalized_stage,
    prediction_counts,
    scored_prediction_cell,
    stratify,
)

#: The grouping key for an event whose counted cells were cut at different
#: conferences (one predictor provisioned before a relist or reschedule,
#: another after).
MIXED = "mixed"

#: The grouping key for an event no counted cell shows distributed at all, and
#: for a registered event with no counted cell to cut.
UNDISTRIBUTED = "none"

Status = Literal["scored", "resolved_unscored", "pending", "unforecast"]


def cell_bound(prediction: Prediction) -> date | None:
    """The exclusive day bound of what the cell's provisioned snapshot could show.

    The moment's ``cutoff`` where provisioning fixed one — its entries are the
    ones filed strictly before it, the rule
    :func:`~fedcourtsai.pipeline.asof.asof_conference` applies — else the day
    after ``snapshot_date``: an as-stored snapshot is the payload pulled that
    day, so it can carry entries filed on that day and none later. The bound is
    day-grained, so an entry filed on the snapshot's own day after the pull, or
    docketed days after its filing date, is admitted although the cell could
    not have read it; an event whose cells straddle such an entry reads as
    ``mixed`` rather than being placed silently. ``None`` where the prediction
    carries no context.
    """
    context = prediction.context
    if context is None:
        return None
    if context.cutoff is not None:
        return context.cutoff
    return context.snapshot_date + timedelta(days=1)


def _conference(
    payload: dict[str, Any] | None, bound: date | None, current: date | None
) -> tuple[date | None, Literal["asof", "current"]]:
    if payload is not None and bound is not None:
        return asof.asof_conference(payload, bound), "asof"
    return current, "current"


def _cell(
    predictor_id: str,
    run_id: str,
    prediction: Prediction,
    payload: dict[str, Any] | None,
    current: date | None,
) -> CountedConferenceCell:
    bound = cell_bound(prediction)
    context = prediction.context
    conference, source = _conference(payload, bound, current)
    return CountedConferenceCell(
        predictor_id=predictor_id,
        run_id=run_id,
        process_digest=prediction.process_version.digest if prediction.process_version else None,
        bound=bound,
        band=context.band if context is not None else None,
        salience_version=context.salience_version if context is not None else None,
        conference=conference,
        conference_source=source,
    )


def _one(values: Iterable[str | None]) -> str | None:
    """The single value every cell agrees on, or ``None`` where they differ."""
    distinct = set(values)
    return distinct.pop() if len(distinct) == 1 else None


def _group_key(cells: list[CountedConferenceCell]) -> str:
    distinct = {cell.conference for cell in cells}
    if not distinct:
        return UNDISTRIBUTED
    if len(distinct) > 1:
        return MIXED
    (only,) = distinct
    return only.isoformat() if only is not None else UNDISTRIBUTED


def _counted_cells(
    event_paths: EventPaths, graded_runs: dict[str, str]
) -> list[tuple[str, str, Prediction]]:
    """Each predictor's counted cell: the graded run where one is counted, else the staged one.

    A counted grading names the run it scored, and the leaderboard counts that
    run — even where a later run has since been staged — so a predictor with a
    counted grading contributes exactly the run it names. A predictor with
    none contributes its staged run, the one provisioning hands the graders
    (the newest resolvable run, never a later window's cell in place of the
    earliest window's), and only when that run is its predictor's counted
    forecast of the event (:func:`fedcourtsai.store.prediction_counts`).
    """
    staged = latest_prediction_dirs(event_paths)
    cells: list[tuple[str, str, Prediction]] = []
    for predictor_id in sorted(set(staged) | set(graded_runs)):
        if predictor_id in graded_runs:
            found = scored_prediction_cell(
                event_paths.base, predictor_id, graded_runs[predictor_id] or None
            )
            if found is not None:
                cells.append((predictor_id, found[0].name, found[1]))
            continue
        prediction = read_model(staged[predictor_id] / "prediction.json", Prediction)
        if prediction_counts(event_paths.base, predictor_id, prediction):
            cells.append((predictor_id, staged[predictor_id].name, prediction))
    return cells


def _status(predictors: list[str], scored: list[str], outcome: Outcome | None) -> Status:
    if not predictors:
        return "unforecast"
    if outcome is None:
        return "pending"
    return "scored" if scored == predictors else "resolved_unscored"


def _registered(
    *,
    registered_at: date,
    decounted_by_registration: bool,
    stage: str | None,
    moment: str | None,
    outcome: Outcome | None,
    at_registration: date | None,
) -> bool:
    """The registered rule's membership as at ``registered_at``, reconstructed."""
    return bool(
        decounted_by_registration
        and stage is not None
        and moment is not None
        and (Stage(stage), Moment(moment)) in REPREDICT_MOMENTS
        and (outcome is None or outcome.resolved_at >= registered_at)
        and (
            moment != Moment.distribution
            or (at_registration is not None and at_registration >= registered_at)
        )
    )


def counted_by_conference(
    data_root: Path,
    conn: corpus.ReadConnection,
    *,
    vintage: ExportCorpusVintage,
    corpus_sha256: str,
    registered_at: date | None = None,
) -> CountedConferenceCut:
    """Every counted event — and, with ``registered_at``, every registered one.

    A **counted** event is one with at least one counted cell
    (:func:`_counted_cells`). ``scored_predictors`` are the predictors with a
    counted grading, from the same :func:`fedcourtsai.store.stratify` pass the
    leaderboard aggregates, so they are always a subset of ``predictors``.
    ``reowed`` says whether a de-counted or unstamped cell predates the event's
    earliest counted cell: a re-forecast of an earlier round's event rather than
    one the frozen process forecast first.

    With ``registered_at`` each event also carries the registered rule's
    membership as at that day (see the module docstring), and a registered
    event with **no** counted cell is listed too, with empty ``predictors`` and
    ``cells`` — an event every engine failed on is otherwise invisible to a
    completeness count.
    """
    run = stratify(data_root, frozen_only=True, policy=FORWARD_CLAIM_POLICY)
    graded: dict[tuple[str, str], dict[str, str]] = {}
    for evaluation, _stratum, _stage, _moment in run.cells:
        runs = graded.setdefault((evaluation.case_id, evaluation.event_id), {})
        runs[evaluation.predictor_id] = max(
            runs.get(evaluation.predictor_id, ""), evaluation.prediction_run_id or ""
        )

    events: list[CountedConferenceEvent] = []
    payloads: dict[str, tuple[date, dict[str, Any]] | None] = {}
    fallbacks = 0
    for ref in iter_predicted_events(data_root):
        case_id, event_id = ref.case_id, ref.event_id
        court_id, _, docket = case_id.partition("/")
        event_paths = CasePaths(data_root, court_id, int(docket)).event(event_id)
        graded_runs = graded.get((case_id, event_id), {})
        counted = _counted_cells(event_paths, graded_runs)
        # The de-counted cells, by the per-cell rule: in no window, or in a
        # revoked one. The event-aware rule's other uncounted cells are a
        # later window's — one behind a counted earlier-window sibling (a
        # duplicate, not a de-count), or one stamped before the revocation of
        # the earlier window it stood behind, whose revoked sibling is already
        # here and older, so both event-level reads below (any by the
        # registration day, any before the earliest counted cell) are the same.
        decounted = [
            prediction
            for path in sorted(event_paths.predictions_dir.glob("*/*/prediction.json"))
            if not is_frozen((prediction := read_model(path, Prediction)).process_version)
        ]
        decounted_by_registration = registered_at is not None and any(
            cell_clock(p).date() <= registered_at for p in decounted
        )
        if not counted and not decounted_by_registration:
            continue
        event = (
            read_model(event_paths.event_file, PredictableEvent)
            if event_paths.event_file.is_file()
            else None
        )
        stage = normalized_stage(event.kind, event.stage) if event is not None else None
        moment = normalized_moment(stage, event.moment) if event is not None else None
        outcome = (
            read_model(event_paths.outcome, Outcome) if event_paths.outcome.is_file() else None
        )

        row = corpus.get_row(conn, case_id)
        current = row.distributed_for_conference if row is not None else None
        if case_id not in payloads:
            payloads[case_id] = corpus.latest_live_snapshot(conn, case_id)
        found = payloads[case_id]
        payload = found[1] if found is not None else None

        registered: bool | None = None
        at_registration: date | None = None
        registration_fallback = False
        if registered_at is not None:
            at_registration, source = _conference(payload, registered_at, current)
            registration_fallback = source == "current"
            registered = _registered(
                registered_at=registered_at,
                decounted_by_registration=decounted_by_registration,
                stage=stage,
                moment=moment,
                outcome=outcome,
                at_registration=at_registration,
            )
            if not counted and not registered:
                continue

        cells = [
            _cell(predictor_id, run_id, prediction, payload, current)
            for predictor_id, run_id, prediction in counted
        ]
        fallbacks += registration_fallback + sum(
            1 for cell in cells if cell.conference_source == "current"
        )
        earliest = min((cell_clock(p) for _pid, _run, p in counted), default=None)
        predictors = [cell.predictor_id for cell in cells]
        scored = sorted(pid for pid in graded_runs if pid in predictors)
        events.append(
            CountedConferenceEvent(
                case_id=case_id,
                docket_number=row.docket_number if row is not None else None,
                event_id=event_id,
                caption=event.title if event is not None else None,
                stage=stage,
                moment=moment,
                conference=_group_key(cells),
                current_conference=current,
                payload_date=found[0] if found is not None else None,
                band=_one(cell.band for cell in cells),
                bands=sorted({cell.band for cell in cells if cell.band is not None}),
                predictors=predictors,
                scored_predictors=scored,
                reowed=earliest is not None and any(cell_clock(p) < earliest for p in decounted),
                registered=registered,
                conference_at_registration=at_registration,
                resolved=outcome is not None,
                resolved_at=outcome.resolved_at if outcome is not None else None,
                actual_disposition=(
                    str(outcome.actual_disposition)
                    if outcome is not None and outcome.actual_disposition is not None
                    else None
                ),
                status=_status(predictors, scored, outcome),
                cells=cells,
            )
        )

    events.sort(key=lambda e: (e.conference, e.stage or "", e.moment or "", e.case_id, e.event_id))
    return CountedConferenceCut(
        corpus=vintage,
        corpus_sha256=corpus_sha256,
        registered_at=registered_at,
        conference_fallbacks=fallbacks,
        events=events,
        totals=_totals(events),
    )


_TotalKey = tuple[bool | None, str, str | None, str | None, str | None]


def _totals(events: list[CountedConferenceEvent]) -> list[CountedConferenceTotal]:
    """Event counts per (registered, conference, stage, moment, band), split by status."""
    counts: dict[_TotalKey, Counter[str]] = {}
    for event in events:
        key = (event.registered, event.conference, event.stage, event.moment, event.band)
        counts.setdefault(key, Counter())[event.status] += 1
    order = {True: 0, None: 1, False: 2}
    return [
        CountedConferenceTotal(
            registered=registered,
            conference=conference,
            stage=stage,
            moment=moment,
            band=band,
            events=sum(by_status.values()),
            scored=by_status["scored"],
            resolved_unscored=by_status["resolved_unscored"],
            pending=by_status["pending"],
            unforecast=by_status["unforecast"],
        )
        for (registered, conference, stage, moment, band), by_status in sorted(
            counts.items(),
            key=lambda item: (order[item[0][0]], *(part or "" for part in item[0][1:])),
        )
    ]
