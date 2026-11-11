"""The forecast-document grade board: ``predicted_reasoning_quality``, rolled up.

Every judge grades every predictor's ``predicted_reasoning.md`` on every stage
(``docs/outcome-decomposition.md``, *Grading the forecast document*). This reads
those grades off the cells :func:`fedcourtsai.store.stratify` already kept — the
leaderboard's own population, with its voids, set-asides, leakage and
forward-claim exclusions applied — and keeps the forward ones.

**The unit is the cell** (case, event, predictor), read by a panel of judges.
Only a judge whose evaluate digest asks for the grade
(:func:`fedcourtsai.validate.asks_predicted_reasoning_grade`) is on the panel: a
null from a prompt that never asked is not a judgment that the record was
silent. Where a predictor's gradings name more than one of its runs, the
earliest run by harness clock is the one read, with its own gradings.

**The mask.** A cell every judge graded enters the means and the coefficients.
A cell every judge left null is counted. A cell the judges split on — some
graded, some null — enters neither and is counted on its own, so a figure holds
only where the panel agreed the record spoke.

**Never pooled** across stages or across judges: each mean and each
coefficient is one judge rubric's (evaluator, digest) on one stage. In the
leave-one-out coefficient the comparator is the mean of the other judges on
the cell as it stands, whatever digests their reads carry.

The stratified pass keeps one grading per (cell, judge) before a run is chosen
here, so on an all-versions build a judge whose kept grading names a later run
is off that cell's panel; a frozen build holds one counted run per cell.

Nothing here is a rank key, a claim total or a headline; the reading rules are
in ``metrics/README.md``.
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal

from .integrity import FORWARD, StratifiedCell, cell_clock
from .leaderboard import kendall_tau_b
from .paths import EventPaths
from .process_version import Rubric, blessing_labels, rubric_of, rubric_order
from .schemas import (
    CountingWindow,
    DocumentGradeAgreement,
    DocumentGradeByCall,
    DocumentGradeFamily,
    DocumentGradeReading,
    DocumentGradeSeries,
    DocumentGradeStage,
    DocumentGradeWithinPredictor,
    Engine,
    Evaluation,
    ForecastDocumentGrades,
    Prediction,
    Stage,
)
from .store import EvaluationKey, evaluation_key, scored_prediction_cell
from .validate import asks_predicted_reasoning_grade

#: The registered count under which no mean and no coefficient is printed: a
#: mean of a handful of anchored grades is two or three documents, not a level.
MINIMUM_CELLS = 10

#: A graded document: (case_id, event_id, predictor_id).
Cell = tuple[str, str, str]

#: One cell's panel: each asking judge's grading of the run that is read.
Panel = dict[str, Evaluation]


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if len(values) >= MINIMUM_CELLS else None


def _spread(values: Sequence[float]) -> float | None:
    return statistics.pstdev(values) if len(values) >= MINIMUM_CELLS else None


def _tau(points: Sequence[tuple[float, float]]) -> float | None:
    return kendall_tau_b(points) if len(points) >= MINIMUM_CELLS else None


def _graded(panel: Panel) -> dict[str, float] | None:
    """The panel's grades where every judge gave one, else ``None``."""
    grades = {
        evaluator: ev.predicted_reasoning_quality
        for evaluator, ev in panel.items()
        if ev.predicted_reasoning_quality is not None
    }
    return grades if len(grades) == len(panel) else None


def _series(
    predictor_id: str, process_window: str | None, panels: Sequence[Panel]
) -> DocumentGradeSeries:
    clean = [panel for panel in panels if _graded(panel) is not None]
    reads = [ev for panel in panels for ev in panel.values()]
    graded_reads = sum(1 for ev in reads if ev.predicted_reasoning_quality is not None)
    null_by_all = sum(
        1
        for panel in panels
        if all(ev.predicted_reasoning_quality is None for ev in panel.values())
    )
    by_rubric: dict[Rubric, list[float]] = defaultdict(list)
    for panel in clean:
        for ev in panel.values():
            if ev.predicted_reasoning_quality is not None:
                by_rubric[rubric_of(ev)].append(ev.predicted_reasoning_quality)
    return DocumentGradeSeries(
        predictor_id=predictor_id,
        process_window=process_window,
        cells=len(panels),
        graded_by_all=len(clean),
        null_by_all=null_by_all,
        split_on_mask=len(panels) - len(clean) - null_by_all,
        reads_graded=graded_reads,
        reads_null=len(reads) - graded_reads,
        readings=[
            DocumentGradeReading(
                evaluator_id=rubric[0],
                digest=rubric[1],
                labels=blessing_labels([rubric]),
                n=len(grades),
                mean=_mean(grades),
            )
            for rubric, grades in sorted(by_rubric.items(), key=lambda item: rubric_order(item[0]))
        ],
    )


def _loo_points(
    cells: Sequence[Mapping[str, float]], evaluator_id: str
) -> list[tuple[float, float]]:
    """``evaluator_id``'s grade against the mean of the others', per shared cell."""
    points: list[tuple[float, float]] = []
    for grades in cells:
        if evaluator_id not in grades:
            continue
        others = [grade for evaluator, grade in grades.items() if evaluator != evaluator_id]
        if others:
            points.append((grades[evaluator_id], sum(others) / len(others)))
    return points


def _agreement(rubric: Rubric, clean: Mapping[Cell, dict[str, float]]) -> DocumentGradeAgreement:
    """``rubric``'s leave-one-out reading over ``clean``, the cells it read and all graded."""
    evaluator_id = rubric[0]
    shared = [cell for cell, grades in clean.items() if len(grades) > 1]
    by_predictor: dict[str, list[dict[str, float]]] = defaultdict(list)
    for (_, _, predictor_id), grades in clean.items():
        by_predictor[predictor_id].append(grades)
    within = []
    for predictor_id, cells in sorted(by_predictor.items()):
        points = _loo_points(cells, evaluator_id)
        within.append(
            DocumentGradeWithinPredictor(
                predictor_id=predictor_id, units=len(points), tau_b=_tau(points)
            )
        )
    # Read against the pooled coefficient only where every predictor with a
    # shared cell prints: an average over the ones that happen to clear the
    # minimum would set one predictor's coefficient against the pool.
    printed = [w.tau_b for w in within if w.units]
    complete = [tau for tau in printed if tau is not None]
    return DocumentGradeAgreement(
        evaluator_id=evaluator_id,
        digest=rubric[1],
        labels=blessing_labels([rubric]),
        units=len(shared),
        cases=len({cell[0] for cell in shared}),
        tau_b=_tau(_loo_points(list(clean.values()), evaluator_id)),
        within_predictor_tau_b=(
            sum(complete) / len(complete) if complete and len(complete) == len(printed) else None
        ),
        within_predictor=within,
    )


def _family(
    rubric: Rubric,
    panels: Mapping[Cell, Panel],
    clean: Mapping[Cell, dict[str, float]],
    engines: Mapping[Cell, Engine],
) -> DocumentGradeFamily | None:
    evaluator_id = rubric[0]
    own: list[float] = []
    other: list[float] = []
    engine: Engine | None = None
    for cell, grades in clean.items():
        engine = panels[cell][evaluator_id].engine
        (own if engines[cell] == engine else other).append(grades[evaluator_id])
    if engine is None:
        return None
    return DocumentGradeFamily(
        evaluator_id=evaluator_id,
        digest=rubric[1],
        labels=blessing_labels([rubric]),
        engine=engine,
        own_n=len(own),
        own_mean=_mean(own),
        other_n=len(other),
        other_mean=_mean(other),
    )


def _by_call(
    rubric: Rubric, panels: Mapping[Cell, Panel], clean: Mapping[Cell, dict[str, float]]
) -> DocumentGradeByCall:
    evaluator_id = rubric[0]
    groups: dict[int, list[float]] = {0: [], 1: []}
    unscored = 0
    for cell, grades in clean.items():
        correct = panels[cell][evaluator_id].correct
        if correct is None:
            unscored += 1
        else:
            groups[correct].append(grades[evaluator_id])
    return DocumentGradeByCall(
        evaluator_id=evaluator_id,
        digest=rubric[1],
        labels=blessing_labels([rubric]),
        correct_n=len(groups[1]),
        correct_mean=_mean(groups[1]),
        correct_spread=_spread(groups[1]),
        incorrect_n=len(groups[0]),
        incorrect_mean=_mean(groups[0]),
        incorrect_spread=_spread(groups[0]),
        unscored_n=unscored,
    )


def _stage(
    stage: Stage,
    panels: Mapping[Cell, Panel],
    engines: Mapping[Cell, Engine],
    windows: Mapping[Cell, str | None],
    reads_not_asked: int,
) -> DocumentGradeStage:
    clean = {cell: grades for cell, panel in panels.items() if (grades := _graded(panel))}
    null_by_all = sum(
        1
        for panel in panels.values()
        if all(ev.predicted_reasoning_quality is None for ev in panel.values())
    )
    by_series: dict[tuple[str, str | None], list[Panel]] = defaultdict(list)
    for cell, panel in panels.items():
        by_series[(cell[2], None)].append(panel)
        if (window := windows.get(cell)) is not None:
            by_series[(cell[2], window)].append(panel)
    evaluators = sorted({evaluator for panel in panels.values() for evaluator in panel})
    # One judge rubric at a time: the cells that rubric read, among those every
    # judge on the cell graded.
    rubrics = sorted(
        {rubric_of(ev) for panel in panels.values() for ev in panel.values()}, key=rubric_order
    )
    read_by = {
        rubric: {
            cell: grades
            for cell, grades in clean.items()
            if rubric[0] in panels[cell] and rubric_of(panels[cell][rubric[0]]) == rubric
        }
        for rubric in rubrics
    }
    family = [_family(rubric, panels, read_by[rubric], engines) for rubric in rubrics]
    return DocumentGradeStage(
        stage=stage,
        cells=len(panels),
        cases=len({cell[0] for cell in panels}),
        graded_by_all=len(clean),
        null_by_all=null_by_all,
        split_on_mask=len(panels) - len(clean) - null_by_all,
        missing_judge=sum(1 for panel in panels.values() if len(panel) < len(evaluators)),
        reads_not_asked=reads_not_asked,
        series=[
            _series(predictor_id, window, by_series[(predictor_id, window)])
            for predictor_id, window in sorted(
                by_series, key=lambda key: (key[0], key[1] is not None, key[1] or "")
            )
        ],
        agreement=[_agreement(rubric, read_by[rubric]) for rubric in rubrics],
        family=[row for row in family if row is not None],
        by_call=[_by_call(rubric, panels, read_by[rubric]) for rubric in rubrics],
    )


def build_forecast_document_grades(
    cells: Sequence[StratifiedCell],
    data_root: Path,
    *,
    process_scope: Literal["frozen", "all"],
    cell_windows: Mapping[EvaluationKey, CountingWindow] | None = None,
) -> ForecastDocumentGrades:
    """The grade board over the stratified forward ``cells``.

    ``cell_windows`` names each grading's counting window on a frozen build;
    without it every series is the predictor's pooled one.
    """
    gradings: dict[Stage, dict[Cell, list[Evaluation]]] = defaultdict(lambda: defaultdict(list))
    not_asked: dict[Stage, int] = defaultdict(int)
    for evaluation, stratum, stage, _moment in cells:
        if stratum != FORWARD or stage is None:
            continue
        stamp = evaluation.process_version
        if not asks_predicted_reasoning_grade(stamp.digest if stamp is not None else None):
            not_asked[stage] += 1
            continue
        cell = (evaluation.case_id, evaluation.event_id, evaluation.predictor_id)
        gradings[stage][cell].append(evaluation)

    later_run_reads = 0
    stages: list[DocumentGradeStage] = []
    for stage in sorted(set(gradings) | set(not_asked), key=str):
        panels: dict[Cell, Panel] = {}
        engines: dict[Cell, Engine] = {}
        windows: dict[Cell, str | None] = {}
        for cell, cell_gradings in sorted(gradings[stage].items()):
            case_id, event_id, predictor_id = cell
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
            later_run_reads += len(cell_gradings) - len(run_gradings)
            # One read per judge: the stratified pass keeps one grading per
            # (cell, judge), so the run's gradings are its panel.
            panel: Panel = {grading.evaluator_id: grading for grading in run_gradings}
            panels[cell] = panel
            engines[cell] = prediction.engine
            window = None
            if cell_windows is not None:
                labels = {
                    found.label
                    for grading in panel.values()
                    if (found := cell_windows.get(evaluation_key(grading))) is not None
                }
                window = next(iter(labels)) if len(labels) == 1 else None
            windows[cell] = window
        stages.append(_stage(stage, panels, engines, windows, not_asked[stage]))
    return ForecastDocumentGrades(
        process_scope=process_scope,
        minimum_cells=MINIMUM_CELLS,
        later_run_reads=later_run_reads,
        stages=stages,
    )


def forecast_document_grades_summary(board: ForecastDocumentGrades) -> str:
    """One line for the command's echo and the refresh headline: cells per stage."""
    if not board.stages:
        return "no forward cell read by a judge whose prompt asks for the grade"
    return "; ".join(
        f"{stage.stage!s} {stage.graded_by_all} of {stage.cells} cell(s) graded by all "
        f"({stage.null_by_all} null by all, {stage.split_on_mask} split)"
        for stage in board.stages
    )
