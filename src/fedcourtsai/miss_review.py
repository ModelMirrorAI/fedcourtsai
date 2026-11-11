"""The forward miss review: which counted forecasts were wrong, and what they ran on.

The boards say how often a predictor is wrong; this lists the events. It reads
the cells :func:`fedcourtsai.store.stratify` already kept — the leaderboard's
own population, with its voids, set-asides, leakage and forward-claim
exclusions applied — and keeps the forward ones.

One row per (case, event, predictor): the scored prediction re-scored against
the committed outcome by the rule that stamps a grading
(:func:`fedcourtsai.pipeline.evaluate.stage_correct` and
:func:`~fedcourtsai.pipeline.evaluate.stage_brier_score`), never the grading's
stamped ``correct``, so a grading paired with an outcome since superseded
cannot list a miss that is not one — and the review can therefore disagree
with a board figure built on such a grading. A cell that rule leaves unscored
is counted ``unscored`` and reviewed no further. Where a predictor's gradings
name more than one of its runs, the earliest run by harness clock is the one
reviewed, with its own gradings.

A cell **misses** on a wrong call or on a forecast on the wrong side of even
odds, a Brier at or above :data:`WRONG_SIDE_BRIER`. The two differ where the
label vocabulary is finer than the binary: a ``gvr`` called ``granted`` is a
wrong call on the right side of one half. A miss is not an error: a calibrated
forecaster at ``p`` lands on the wrong side at rate ``min(p, 1 - p)``.

Record depth is what the ledger commits about the run: the frozen snapshot
provenance and uptake, and the retrieval log's call count and its count of
self-provisioned fetches. The provisioned document set itself is runner-side
and is not in the ledger, so it is not reported.

Everything here is a count over a small, selected population. Nothing is a
rank key or a claimable figure; the reading rules are in ``metrics/README.md``.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal

from .integrity import FORWARD, StratifiedCell, cell_clock
from .leaderboard import band_key, stage_moment_key
from .paths import EventPaths
from .pipeline.evaluate import scores_finer_reading, stage_brier_score, stage_correct
from .schemas import (
    CountingWindow,
    Evaluation,
    MissEventTally,
    MissReview,
    MissReviewCall,
    MissReviewEvent,
    MissTally,
    Outcome,
    Prediction,
    RetrievalLog,
    Stage,
)
from .serialize import read_model
from .store import EvaluationKey, evaluation_key, scored_prediction_cell

#: A Brier at or above this is on the wrong side: on a binary target it is the
#: score of a forecast exactly at one half, so anything at or past it sat on the
#: wrong side of even odds, or on them.
WRONG_SIDE_BRIER = 0.25

NO_CONTEXT_KEY = "(none)"
NO_JUDGMENT_KEY = "(none)"

_CellKey = tuple[str, str, str]


def _realized(prediction: Prediction, outcome: Outcome, *, interim: bool) -> str:
    """The realized label on the axis the cell is scored on."""
    if outcome.judgment is not None:
        return str(outcome.judgment)
    if interim and scores_finer_reading(prediction) and outcome.interim_reading is not None:
        return str(outcome.interim_reading)
    return str(outcome.actual_disposition)


def _called(prediction: Prediction, outcome: Outcome) -> str:
    """The label the prediction named on that axis, which the outcome picks."""
    if outcome.judgment is not None:
        return str(prediction.judgment) if prediction.judgment is not None else NO_JUDGMENT_KEY
    return str(prediction.predicted_disposition)


def _mean(values: Sequence[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def _log(event: EventPaths, prediction: Prediction) -> RetrievalLog | None:
    path = event.prediction_retrieval_log(prediction.predictor_id, prediction.run_id)
    return read_model(path, RetrievalLog) if path.is_file() else None


def _call(
    gradings: Sequence[Evaluation],
    event: EventPaths,
    run_id: str,
    prediction: Prediction,
    outcome: Outcome,
    window: CountingWindow | None,
    *,
    interim: bool,
) -> MissReviewCall | None:
    """The reviewed row, or ``None`` where the stage's rule leaves the cell unscored."""
    correct = stage_correct(prediction, outcome, interim=interim)
    brier = stage_brier_score(prediction, outcome, interim=interim)
    if correct is None or brier is None:
        return None
    context = prediction.context
    log = _log(event, prediction)
    return MissReviewCall(
        predictor_id=prediction.predictor_id,
        prediction_run_id=run_id,
        process_window=window.label if window is not None else None,
        band=band_key(context),
        call=_called(prediction, outcome),
        probability=prediction.probability,
        brier_score=round(brier, 6),
        wrong_call=not correct,
        wrong_side=brier >= WRONG_SIDE_BRIER,
        snapshot_provenance=context.snapshot_provenance if context is not None else None,
        snapshot_uptake=context.snapshot_uptake if context is not None else None,
        retrieval_calls=len(log.calls) if log is not None else None,
        self_provisioned_fetches=log.self_provisioned_fetches if log is not None else None,
        gradings=len(gradings),
        mean_reasoning_quality=_mean(
            [g.reasoning_quality for g in gradings if g.reasoning_quality is not None]
        ),
        mean_predicted_reasoning_quality=_mean(
            [
                g.predicted_reasoning_quality
                for g in gradings
                if g.predicted_reasoning_quality is not None
            ]
        ),
    )


def missed(call: MissReviewCall) -> bool:
    """Whether a reviewed forecast is a miss: a wrong call or the wrong side of even odds."""
    return call.wrong_call or call.wrong_side


def _provisioning_key(call: MissReviewCall) -> str:
    if call.self_provisioned_fetches is None:
        return "unlogged"
    return "fetched" if call.self_provisioned_fetches else "none"


def _tallies(pairs: Sequence[tuple[str, MissReviewCall]]) -> dict[str, MissTally]:
    cells: dict[str, int] = defaultdict(int)
    misses: dict[str, int] = defaultdict(int)
    for key, call in pairs:
        cells[key] += 1
        misses[key] += missed(call)
    return {key: MissTally(cells=cells[key], missed=misses[key]) for key in sorted(cells)}


def _event_tally(events: Sequence[MissReviewEvent]) -> MissEventTally:
    return MissEventTally(
        events=len(events),
        missed=sum(any(missed(call) for call in event.calls) for event in events),
        shared=sum(event.shared for event in events),
    )


def build_miss_review(
    cells: Sequence[StratifiedCell],
    data_root: Path,
    *,
    process_scope: Literal["frozen", "all"] = "frozen",
    cell_windows: Mapping[EvaluationKey, CountingWindow] | None = None,
) -> MissReview:
    """The miss review over ``cells``' forward stratum.

    ``cells`` is :func:`fedcourtsai.store.stratify`'s default population. A
    predictor's gradings of an event are grouped by the run each names; the
    earliest run by harness clock is reviewed, with its own gradings. A grading
    whose scored prediction is unreadable is left out, as the leaderboard's
    floor fields leave it out.
    """
    windows = cell_windows or {}
    gradings: dict[_CellKey, list[Evaluation]] = defaultdict(list)
    stages: dict[tuple[str, str], tuple[str, bool]] = {}
    for evaluation, stratum, stage, moment in cells:
        if stratum != FORWARD:
            continue
        key = (evaluation.case_id, evaluation.event_id, evaluation.predictor_id)
        gradings[key].append(evaluation)
        stages[(evaluation.case_id, evaluation.event_id)] = (
            stage_moment_key(stage, moment),
            stage == Stage.interim,
        )

    outcomes: dict[tuple[str, str], Outcome] = {}
    calls: dict[tuple[str, str], list[MissReviewCall]] = defaultdict(list)
    realized: dict[tuple[str, str], str] = {}
    unscored = 0
    for (case_id, event_id, predictor_id), cell_gradings in sorted(gradings.items()):
        event_key = (case_id, event_id)
        paths = EventPaths(data_root / "cases" / case_id / "events" / event_id)
        runs: dict[str, tuple[Prediction, list[Evaluation]]] = {}
        for grading in sorted(cell_gradings, key=lambda g: (g.evaluator_id, g.run_id)):
            scored = scored_prediction_cell(paths.base, predictor_id, grading.prediction_run_id)
            if scored is None:
                continue
            run_dir, prediction = scored
            runs.setdefault(run_dir.name, (prediction, []))[1].append(grading)
        if not runs:
            continue
        run_id = min(runs, key=lambda name: (cell_clock(runs[name][0]), name))
        prediction, run_gradings = runs[run_id]
        if event_key not in outcomes:
            outcomes[event_key] = read_model(paths.outcome, Outcome)
        call = _call(
            run_gradings,
            paths,
            run_id,
            prediction,
            outcomes[event_key],
            windows.get(evaluation_key(run_gradings[0])),
            interim=stages[event_key][1],
        )
        if call is None:
            unscored += 1
            continue
        calls[event_key].append(call)
        realized.setdefault(
            event_key, _realized(prediction, outcomes[event_key], interim=stages[event_key][1])
        )

    events: list[MissReviewEvent] = []
    for event_key in sorted(calls):
        case_id, event_id = event_key
        outcome = outcomes[event_key]
        event_calls = calls[event_key]
        events.append(
            MissReviewEvent(
                case_id=case_id,
                event_id=event_id,
                stage=stages[event_key][0],
                outcome=realized[event_key],
                actual_granted=outcome.actual_granted,
                resolved_at=outcome.resolved_at,
                shared=len(event_calls) > 1 and all(missed(call) for call in event_calls),
                calls=event_calls,
            )
        )

    every_call = [call for event in events for call in event.calls]
    by_stage: dict[str, list[MissReviewEvent]] = defaultdict(list)
    for event in events:
        by_stage[event.stage].append(event)
    return MissReview(
        process_scope=process_scope,
        wrong_side_brier=WRONG_SIDE_BRIER,
        unscored_cells=unscored,
        cells=MissTally(cells=len(every_call), missed=sum(missed(c) for c in every_call)),
        events=_event_tally(events),
        by_predictor=_tallies([(c.predictor_id, c) for c in every_call]),
        by_stage={key: _event_tally(by_stage[key]) for key in sorted(by_stage)},
        by_band=_tallies([(c.band, c) for c in every_call]),
        by_snapshot_provenance=_tallies(
            [(c.snapshot_provenance or NO_CONTEXT_KEY, c) for c in every_call]
        ),
        by_self_provisioning=_tallies([(_provisioning_key(c), c) for c in every_call]),
        missed_events=[event for event in events if any(missed(c) for c in event.calls)],
    )


def miss_review_summary(review: MissReview) -> str:
    """One line for the command's echo and the refresh PR's headline."""
    return (
        f"{review.events.missed} of {review.events.events} forward event(s) hold a miss "
        f"({review.events.shared} shared by every predictor); "
        f"{review.cells.missed} of {review.cells.cells} cell(s) missed"
    )
