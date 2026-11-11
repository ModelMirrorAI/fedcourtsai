"""The forecast-document grade board over a small fixture ledger."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import ops
from fedcourtsai.cli import app
from fedcourtsai.forecast_document_grades import (
    MINIMUM_CELLS,
    build_forecast_document_grades,
    forecast_document_grades_summary,
)
from fedcourtsai.integrity import FORWARD, RETROSPECTIVE, StratifiedCell
from fedcourtsai.process_version import EVALUATE_BLESSING_LABELS
from fedcourtsai.schemas import (
    CentralClaim,
    Disposition,
    Engine,
    Evaluation,
    ForecastDocumentGrades,
    Moment,
    PredictedReasoningReview,
    Prediction,
    ProcessVersion,
    Stage,
    Stratum,
)
from fedcourtsai.serialize import write_json
from fedcourtsai.validate import asks_predicted_reasoning_grade

CASE = "scotus/123"
RUN = "20260601T000000Z"

#: Two evaluate digests the registry blesses under a prompt that asks for the
#: grade, and one it blesses under an earlier prompt that does not.
ASKING = sorted(d for d in EVALUATE_BLESSING_LABELS if asks_predicted_reasoning_grade(d))
NOT_ASKING = sorted(d for d in EVALUATE_BLESSING_LABELS if not asks_predicted_reasoning_grade(d))

REVIEW = PredictedReasoningReview(
    central_claims=[CentralClaim(claim="the petition is denied", status="borne-out", basis="order")]
)
SILENT = PredictedReasoningReview(not_gradeable="the staged record holds no order")


def _predict(
    data_root: Path,
    predictor_id: str,
    event_id: str,
    *,
    engine: Engine = Engine.claude_code,
    case_id: str = CASE,
    run_id: str = RUN,
) -> None:
    run_dir = data_root / "cases" / case_id / "events" / event_id / "predictions" / predictor_id
    write_json(
        run_dir / run_id / "prediction.json",
        Prediction(
            case_id=case_id,
            event_id=event_id,
            predictor_id=predictor_id,
            engine=engine,
            run_id=run_id,
            created_at=datetime(2026, 6, 1, tzinfo=UTC),
            input_snapshot="record/snapshot.json",
            granted=0,
            probability=0.1,
            predicted_disposition=Disposition.denied,
        ),
    )


def _cell(  # noqa: PLR0913 - one keyword per fact a test varies
    predictor_id: str,
    evaluator_id: str,
    event_id: str,
    grade: float | None,
    *,
    engine: Engine = Engine.claude_code,
    digest: str | None = None,
    correct: int = 1,
    case_id: str = CASE,
    stratum: Stratum = FORWARD,
    stage: Stage = Stage.cert,
    prediction_run_id: str = RUN,
) -> StratifiedCell:
    evaluation = Evaluation(
        case_id=case_id,
        event_id=event_id,
        predictor_id=predictor_id,
        evaluator_id=evaluator_id,
        engine=engine,
        run_id="r1",
        prediction_run_id=prediction_run_id,
        created_at=datetime(2026, 6, 24, tzinfo=UTC),
        correct=correct,
        predicted_reasoning_quality=grade,
        predicted_reasoning_review=REVIEW if grade is not None else SILENT,
        process_version=ProcessVersion(
            label="proc-test",
            digest=digest if digest is not None else ASKING[0],
            stamped_at=datetime(2026, 6, 24, tzinfo=UTC),
        ),
    )
    return (evaluation, stratum, stage, Moment.distribution)


def _build(cells: list[StratifiedCell], data_root: Path) -> ForecastDocumentGrades:
    return build_forecast_document_grades(cells, data_root, process_scope="frozen")


def _events(count: int) -> list[str]:
    return [f"evt-{index:02d}" for index in range(count)]


def test_the_registry_holds_a_digest_that_asks_and_one_that_does_not() -> None:
    assert ASKING and NOT_ASKING


def test_an_empty_ledger_grades_nothing(tmp_path: Path) -> None:
    board = _build([], tmp_path)
    assert board.stages == []
    assert board.minimum_cells == MINIMUM_CELLS
    assert "no forward cell" in forecast_document_grades_summary(board)


def test_a_mean_is_one_judges_over_the_cells_every_judge_graded(tmp_path: Path) -> None:
    cells = []
    for index, event_id in enumerate(_events(MINIMUM_CELLS)):
        _predict(tmp_path, "alpha", event_id)
        cells.append(_cell("alpha", "judge-a", event_id, 0.5))
        cells.append(_cell("alpha", "judge-b", event_id, 1.0 if index % 2 else 0.5))

    (stage,) = _build(cells, tmp_path).stages

    assert (stage.stage, stage.cells, stage.cases) == (Stage.cert, MINIMUM_CELLS, 1)
    assert (stage.graded_by_all, stage.null_by_all, stage.split_on_mask) == (MINIMUM_CELLS, 0, 0)
    (series,) = stage.series
    assert (series.predictor_id, series.process_window) == ("alpha", None)
    assert [(r.evaluator_id, r.n, r.mean) for r in series.readings] == [
        ("judge-a", MINIMUM_CELLS, 0.5),
        ("judge-b", MINIMUM_CELLS, 0.75),
    ]
    assert (series.reads_graded, series.reads_null) == (2 * MINIMUM_CELLS, 0)


def test_a_mean_under_the_minimum_prints_its_count_and_no_value(tmp_path: Path) -> None:
    cells = []
    for event_id in _events(MINIMUM_CELLS - 1):
        _predict(tmp_path, "alpha", event_id)
        cells.append(_cell("alpha", "judge-a", event_id, 0.5))

    (stage,) = _build(cells, tmp_path).stages

    (reading,) = stage.series[0].readings
    assert (reading.n, reading.mean) == (MINIMUM_CELLS - 1, None)
    assert stage.agreement[0].tau_b is None


def test_the_mask_counts_null_and_split_cells_and_keeps_them_out_of_the_mean(
    tmp_path: Path,
) -> None:
    for event_id in ("evt-graded", "evt-null", "evt-split"):
        _predict(tmp_path, "alpha", event_id)
    cells = [
        _cell("alpha", "judge-a", "evt-graded", 0.75),
        _cell("alpha", "judge-b", "evt-graded", 0.5),
        _cell("alpha", "judge-a", "evt-null", None),
        _cell("alpha", "judge-b", "evt-null", None),
        _cell("alpha", "judge-a", "evt-split", 1.0),
        _cell("alpha", "judge-b", "evt-split", None),
    ]

    (stage,) = _build(cells, tmp_path).stages

    assert (stage.graded_by_all, stage.null_by_all, stage.split_on_mask) == (1, 1, 1)
    (series,) = stage.series
    assert (series.graded_by_all, series.null_by_all, series.split_on_mask) == (1, 1, 1)
    # The split cell's one grade is a read, and is in no reading's count.
    assert (series.reads_graded, series.reads_null) == (3, 3)
    assert [(r.evaluator_id, r.n) for r in series.readings] == [("judge-a", 1), ("judge-b", 1)]


def test_a_judge_whose_prompt_does_not_ask_is_not_on_the_panel(tmp_path: Path) -> None:
    _predict(tmp_path, "alpha", "evt-a")
    cells = [
        _cell("alpha", "judge-a", "evt-a", 0.75),
        _cell("alpha", "judge-b", "evt-a", None, digest=NOT_ASKING[0]),
    ]

    (stage,) = _build(cells, tmp_path).stages

    # judge-b's null is a prompt that never asked, not a silent record: the
    # cell is graded by all of its one-judge panel, not split.
    assert (stage.graded_by_all, stage.split_on_mask, stage.reads_not_asked) == (1, 0, 1)
    assert [row.evaluator_id for row in stage.agreement] == ["judge-a"]


def test_stages_are_never_pooled_and_only_forward_cells_are_read(tmp_path: Path) -> None:
    for event_id in ("evt-cert", "evt-interim", "evt-retro"):
        _predict(tmp_path, "alpha", event_id)
    cells = [
        _cell("alpha", "judge-a", "evt-cert", 0.75),
        _cell("alpha", "judge-a", "evt-interim", 0.25, stage=Stage.interim),
        _cell("alpha", "judge-a", "evt-retro", 1.0, stratum=RETROSPECTIVE),
    ]

    board = _build(cells, tmp_path)

    assert [(stage.stage, stage.cells) for stage in board.stages] == [
        (Stage.cert, 1),
        (Stage.interim, 1),
    ]


def test_each_rubric_of_one_judge_reads_on_its_own(tmp_path: Path) -> None:
    if len(ASKING) < 2:
        pytest.skip("the registry blesses one asking digest")
    for event_id in ("evt-a", "evt-b"):
        _predict(tmp_path, "alpha", event_id)
    cells = [
        _cell("alpha", "judge-a", "evt-a", 0.25, digest=ASKING[0]),
        _cell("alpha", "judge-a", "evt-b", 0.75, digest=ASKING[1]),
    ]

    (stage,) = _build(cells, tmp_path).stages

    assert [(r.digest, r.n) for r in stage.series[0].readings] == [(ASKING[0], 1), (ASKING[1], 1)]
    assert stage.agreement[0].digests == 2


def test_agreement_is_leave_one_out_with_its_within_predictor_reading(tmp_path: Path) -> None:
    # Two predictors, twelve cells each. Within a predictor both judges give
    # every document the same grade, so nothing orders them there; across the
    # predictors both grade beta above alpha. The pooled coefficient is all
    # predictor tracking, and the within-predictor one is undefined.
    cells = []
    for predictor_id, grade in (("alpha", 0.25), ("beta", 0.75)):
        for event_id in _events(12):
            _predict(tmp_path, predictor_id, event_id)
            cells.append(_cell(predictor_id, "judge-a", event_id, grade))
            cells.append(_cell(predictor_id, "judge-b", event_id, grade))

    (stage,) = _build(cells, tmp_path).stages

    first = stage.agreement[0]
    assert (first.evaluator_id, first.units, first.cases) == ("judge-a", 24, 1)
    assert first.tau_b == pytest.approx(1.0)
    assert first.within_predictor_tau_b is None
    assert [(w.predictor_id, w.units, w.tau_b) for w in first.within_predictor] == [
        ("alpha", 12, None),
        ("beta", 12, None),
    ]


def test_family_and_call_splits_read_each_judges_own_grades(tmp_path: Path) -> None:
    cells = []
    for index, event_id in enumerate(_events(MINIMUM_CELLS)):
        _predict(tmp_path, "own", event_id, engine=Engine.claude_code)
        _predict(tmp_path, "other", event_id, engine=Engine.codex)
        cells.append(_cell("own", "judge-a", event_id, 1.0, correct=1))
        cells.append(_cell("other", "judge-a", event_id, 0.5, correct=index % 2))

    (stage,) = _build(cells, tmp_path).stages

    (family,) = stage.family
    assert (family.engine, family.own_n, family.own_mean) == (Engine.claude_code, 10, 1.0)
    assert (family.other_n, family.other_mean) == (10, 0.5)
    (by_call,) = stage.by_call
    assert (by_call.correct_n, by_call.incorrect_n) == (15, 5)
    assert by_call.correct_mean == pytest.approx((10 * 1.0 + 5 * 0.5) / 15)
    assert by_call.correct_spread is not None and by_call.correct_spread > 0
    assert (by_call.incorrect_mean, by_call.incorrect_spread) == (None, None)


def test_the_earliest_graded_run_of_a_cell_is_the_one_read(tmp_path: Path) -> None:
    later = "20260701T000000Z"
    _predict(tmp_path, "alpha", "evt-a")
    _predict(tmp_path, "alpha", "evt-a", run_id=later)
    cells = [
        _cell("alpha", "judge-a", "evt-a", 0.25),
        _cell("alpha", "judge-b", "evt-a", 1.0, prediction_run_id=later),
    ]

    board = _build(cells, tmp_path)

    assert board.later_run_reads == 1
    (reading,) = board.stages[0].series[0].readings
    assert (reading.evaluator_id, reading.n) == ("judge-a", 1)


def test_a_missing_judge_is_counted(tmp_path: Path) -> None:
    for event_id in ("evt-a", "evt-b"):
        _predict(tmp_path, "alpha", event_id)
    cells = [
        _cell("alpha", "judge-a", "evt-a", 0.5),
        _cell("alpha", "judge-b", "evt-a", 0.5),
        _cell("alpha", "judge-a", "evt-b", 0.5),
    ]

    (stage,) = _build(cells, tmp_path).stages

    assert (stage.cells, stage.graded_by_all, stage.missing_judge) == (2, 2, 1)


def test_the_command_writes_the_board(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    out = tmp_path / "grades.json"
    result = CliRunner().invoke(app, ["forecast-document-grades", "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert "forecast-document-grades [frozen]" in result.output
    assert ForecastDocumentGrades.model_validate_json(out.read_text()).stages == []


def test_the_digest_prints_one_row_per_predictor_per_stage(tmp_path: Path) -> None:
    cells = []
    for index, event_id in enumerate(_events(MINIMUM_CELLS)):
        _predict(tmp_path, "alpha", event_id)
        cells.append(_cell("alpha", "judge-a", event_id, 0.5))
        cells.append(_cell("alpha", "judge-b", event_id, 1.0 if index % 2 else 0.5))
    board = _build(cells, tmp_path)

    lines = ops._document_grade_lines(ops.Vintaged(value=board, vintage="2026-11-11"))
    text = "\n".join(lines)

    assert "### Forecast-document grade" in text
    assert "Graded, not scored" in text
    assert "| cert | alpha | 10 of 10 (0, 0) | judge-a 0.50 (10); judge-b 0.75 (10) |" in text
    assert "Judge agreement on cert" in text
    absent = ops._document_grade_lines(ops.Vintaged(value=None, vintage=None))
    assert "has never landed" in "\n".join(absent)
    assert ops._document_grade_lines(None) == []
