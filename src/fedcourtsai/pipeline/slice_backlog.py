"""The cells a prediction slice's dockets are owed, read from committed state.

The Court's backlog derivers (:mod:`.pull`) walk the Court's docket alone: its
admission predicates (the salience band, the conference calendar, the cert
anchor) have no meaning on a lower-court docket. A slice
(:mod:`fedcourtsai.prediction_slices`) is a short committed list, so its
backlog is a walk of that list:

* **predict** — a slice docket's open trial event of a moment switched on by
  the day (:func:`fedcourtsai.store.forecastable_event_ids` with
  ``slice_docket``), which some predictor of the slice's population has not
  forecast;
* **evaluate** — a slice docket's resolved trial event that holds a committed
  prediction and lacks some judge of the slice's population.

Both are stamp-free and idempotent the way the Court's are: the fan-out's
already-predicted and already-graded gates read the same ledger, so
re-deriving an unchanged backlog mints nothing once its cells are committed.
A forecast is owed only where provisioning would mint it: a docket last read
longer ago than the Court's backlog bound is held until the refresh reads it
again, and an event the docket's latest snapshot may already decide
(:func:`~fedcourtsai.pipeline.outcome.forward_leakage`, the refusal
provisioning applies) is not owed, since that refusal is a designed skip that
leaves nothing in the ledger and would otherwise be re-minted every round. A
docket out of the predict scope is owed nothing, and a cell that has failed
the per-cell attempt cap is not owed again. A slice with no actor of its own,
or with no moment switched on, owes nothing, and with no slice enabled both
derivations are empty.

The slices' cases ride beside the Court's and outside its per-cycle case cap.
They share the run's cell cap with it
(:func:`fedcourtsai.matrix.cap_predict_cells`).
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from pathlib import Path

from .. import corpus
from ..matrix import CaseRequest, event_has_evaluations, event_has_predictions
from ..prediction_slices import Population
from ..registry import evaluators_for, predictors_for
from ..schemas import Stage
from ..store import forecastable_event_ids
from ..voids import is_voided
from .outcome import forward_leakage
from .pull import BACKLOG_MAX_POLL_AGE_DAYS, _cell_capped


def _dockets(population: Population) -> list[tuple[str, str, int]]:
    """A slice's dockets as ``(case_id, court, docket)``, in case-id order."""
    listed = []
    for case_id in sorted(population.case_ids or ()):
        court, _, docket = case_id.partition("/")
        if docket.isdigit():
            listed.append((case_id, court, int(docket)))
    return listed


def _in_scope(conn: corpus.ReadConnection, case_id: str) -> corpus.CorpusRow | None:
    """The docket's row where the fan-out's scope backstop would keep it."""
    row = corpus.get_row(conn, case_id)
    if row is None or row.predict_excluded or corpus.out_of_scope_reason_full(conn, row):
        return None
    return row


def _mintable(
    conn: corpus.ReadConnection, row: corpus.CorpusRow, events: list[str], *, day: date
) -> list[str]:
    """``events`` less those provisioning would refuse on the docket as stored.

    Nothing where the docket was last read longer ago than the bound (its
    latest snapshot, or the refresh's read stamp where nothing had changed);
    otherwise each event the latest snapshot does not already answer. A docket
    with no stored snapshot keeps its events: provisioning refuses that
    loudly, by name.
    """
    snapshot = corpus.latest_snapshot(conn, row.case_id)
    read_on = max(
        (d for d in (row.last_pulled, snapshot[0] if snapshot else None) if d is not None),
        default=None,
    )
    if read_on is None or (day - read_on).days > BACKLOG_MAX_POLL_AGE_DAYS:
        return []
    if snapshot is None:
        return events
    return [e for e in events if forward_leakage(snapshot[1], row.court, e) is None]


def derive_slice_predict_backlog(
    conn: corpus.ReadConnection,
    data_root: Path,
    predictors_path: Path,
    slices: Mapping[str, Population],
    *,
    max_attempts: int,
    today: date | None = None,
) -> list[CaseRequest]:
    """Each enabled slice's dockets with a forecast some slice predictor owes."""
    day = today or date.today()
    owed: list[CaseRequest] = []
    for slice_id, population in slices.items():
        predictors = [p.id for p in predictors_for(predictors_path, slice_id)]
        if not predictors:
            continue
        for case_id, court, docket in _dockets(population):
            row = _in_scope(conn, case_id)
            if row is None:
                continue
            events = [
                event_id
                for event_id in forecastable_event_ids(
                    conn, court, docket, today=day, slice_docket=True
                )
                if any(
                    not event_has_predictions(data_root, court, docket, event_id, predictor_id=p)
                    and not _cell_capped(
                        data_root, court, docket, event_id, p, max_attempts, seam="predict"
                    )
                    for p in predictors
                )
            ]
            if events:
                events = _mintable(conn, row, events, day=day)
            if events:
                owed.append(CaseRequest(court, docket, tuple(events)))
    return owed


def derive_slice_evaluate_backlog(
    conn: corpus.ReadConnection,
    data_root: Path,
    evaluators_path: Path,
    slices: Mapping[str, Population],
    *,
    max_attempts: int,
) -> list[CaseRequest]:
    """Each enabled slice's dockets with a grading some slice judge owes."""
    owed: list[CaseRequest] = []
    for slice_id, population in slices.items():
        judges = [e.id for e in evaluators_for(evaluators_path, slice_id)]
        if not judges:
            continue
        for case_id, court, docket in _dockets(population):
            if _in_scope(conn, case_id) is None:
                continue
            events = [
                event.event_id
                for event in corpus.events_for_case(conn, case_id)
                if event.resolved
                and event.stage == Stage.trial
                and not is_voided(case_id, event.event_id)
                and event_has_predictions(data_root, court, docket, event.event_id)
                and any(
                    not event_has_evaluations(
                        data_root, court, docket, event.event_id, evaluator_id=judge
                    )
                    and not _cell_capped(
                        data_root, court, docket, event.event_id, judge, max_attempts
                    )
                    for judge in judges
                )
            ]
            if events:
                owed.append(CaseRequest(court, docket, tuple(events)))
    return owed
