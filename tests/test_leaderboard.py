"""Leaderboard aggregation and stratification over a small fixture ledger."""

from datetime import UTC, date, datetime
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.leaderboard import (
    FORWARD,
    PROCEDURAL,
    RETROSPECTIVE,
    Stratum,
    build_leaderboard,
    classify_stratum,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import Disposition, Engine, Evaluation, Leaderboard, Outcome, Prediction
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.store import iter_evaluations, iter_stratified_evaluations

runner = CliRunner()


def _evaluation(predictor_id: str, **kw: object) -> Evaluation:
    base: dict[str, object] = dict(
        case_id="ca9/123",
        event_id="evt-motion-stay",
        predictor_id=predictor_id,
        evaluator_id="eval-a",
        engine=Engine.claude_code,
        run_id="r1",
        created_at=datetime(2026, 6, 24, tzinfo=UTC),
        correct=1,
        brier_score=0.1,
        vote_accuracy=1.0,
        reasoning_quality=0.8,
    )
    base.update(kw)
    return Evaluation.model_validate(base)


def _forward(ev: Evaluation) -> tuple[Evaluation, Stratum]:
    return (ev, FORWARD)


def _retro(ev: Evaluation) -> tuple[Evaluation, Stratum]:
    return (ev, RETROSPECTIVE)


def _write(data_root: Path, ev: Evaluation) -> None:
    court, _, docket = ev.case_id.partition("/")
    path = (
        CasePaths(data_root, court, int(docket))
        .event(ev.event_id)
        .evaluation(ev.evaluator_id, ev.predictor_id, ev.run_id)
    )
    write_json(path, ev)


def _write_cell(
    data_root: Path,
    ev: Evaluation,
    *,
    predicted_at: datetime = datetime(2026, 6, 20, tzinfo=UTC),
    resolved_at: date = date(2026, 6, 23),
    disposition_basis: str = "standard",
) -> None:
    """A full scored cell: evaluation plus the prediction and outcome it targets."""
    _write(data_root, ev)
    court, _, docket = ev.case_id.partition("/")
    event = CasePaths(data_root, court, int(docket)).event(ev.event_id)
    write_json(
        event.prediction(ev.predictor_id, "p1"),
        Prediction(
            case_id=ev.case_id,
            event_id=ev.event_id,
            predictor_id=ev.predictor_id,
            engine=Engine.claude_code,
            run_id="p1",
            created_at=predicted_at,
            input_snapshot="corpus",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
        ),
    )
    write_json(
        event.outcome,
        Outcome.model_validate(
            dict(
                case_id=ev.case_id,
                event_id=ev.event_id,
                resolved_at=resolved_at,
                actual_disposition=Disposition.granted,
                actual_granted=1,
                disposition_basis=disposition_basis,
            )
        ),
    )


def test_classify_stratum_splits_on_resolution_vs_commit() -> None:
    predicted = datetime(2026, 6, 20, 12, 0, tzinfo=UTC)
    # Event resolved after the prediction -> a true forward forecast.
    assert classify_stratum(predicted, date(2026, 6, 23)) == FORWARD
    # Event resolved decades earlier -> retrospective by construction.
    assert classify_stratum(predicted, date(1950, 12, 11)) == RETROSPECTIVE
    # Same-day tie: the within-day ordering is unknowable, so the conservative
    # reading applies and the cell is never presented as forward.
    assert classify_stratum(predicted, date(2026, 6, 20)) == RETROSPECTIVE


def test_empty_ledger_is_empty_board() -> None:
    board = build_leaderboard([])
    assert board.predictors_ranked == 0
    assert board.evaluations_total == 0
    assert board.forward_evaluations == 0
    assert board.retrospective_evaluations == 0
    assert board.entries == []


def test_aggregates_per_predictor_per_stratum() -> None:
    cells = [
        _forward(_evaluation("alpha", correct=1, brier_score=0.1, event_id="evt-a")),
        _retro(
            _evaluation(
                "alpha", correct=0, brier_score=0.3, event_id="evt-b", evaluator_id="eval-b"
            )
        ),
        _forward(_evaluation("beta", correct=1, brier_score=0.2, event_id="evt-a")),
    ]
    board = build_leaderboard(cells)
    assert board.predictors_ranked == 2
    assert board.evaluations_total == 3
    assert board.forward_evaluations == 2
    assert board.retrospective_evaluations == 1
    alpha = next(e for e in board.entries if e.predictor_id == "alpha")
    # The strata never blend: one perfect forward cell, one missed retro cell.
    assert alpha.forward is not None and alpha.retrospective is not None
    assert alpha.forward.accuracy == 1.0
    assert alpha.forward.mean_brier_score == 0.1
    assert alpha.retrospective.accuracy == 0.0
    assert alpha.retrospective.mean_brier_score == 0.3
    assert alpha.evaluators == 2
    # A stratum with no cells is null, never zero-filled.
    beta = next(e for e in board.entries if e.predictor_id == "beta")
    assert beta.retrospective is None


def test_ranking_orders_by_forward_then_retrospective() -> None:
    cells = [
        # No forward cells at all: sorts after everyone with any forward cell,
        # however strong its retrospective numbers.
        _retro(_evaluation("retro-only", correct=1, brier_score=0.05)),
        _forward(_evaluation("low", correct=0, brier_score=0.1)),
        _forward(_evaluation("high", correct=1, brier_score=0.4)),
        _forward(_evaluation("mid-a", correct=1, brier_score=0.5)),
        _forward(_evaluation("mid-b", correct=1, brier_score=0.2)),
    ]
    board = build_leaderboard(cells)
    order = [(e.rank, e.predictor_id) for e in board.entries]
    # Forward accuracy desc; perfect-but-tied predictors split on forward Brier
    # (lower wins); 0-forward-accuracy still beats having no forward cells.
    assert order == [
        (1, "mid-b"),
        (2, "high"),
        (3, "mid-a"),
        (4, "low"),
        (5, "retro-only"),
    ]


def test_missing_optionals_average_only_over_present() -> None:
    cells = [
        _forward(_evaluation("alpha", brier_score=0.2, vote_accuracy=None, reasoning_quality=None)),
        _forward(_evaluation("alpha", brier_score=None, vote_accuracy=0.5, reasoning_quality=0.6)),
    ]
    stratum = build_leaderboard(cells).entries[0].forward
    assert stratum is not None
    assert stratum.mean_brier_score == 0.2
    assert stratum.mean_vote_accuracy == 0.5
    assert stratum.mean_reasoning_quality == 0.6


def test_all_optionals_absent_stay_none() -> None:
    cells = [
        _forward(_evaluation("alpha", brier_score=None, vote_accuracy=None, reasoning_quality=None))
    ]
    stratum = build_leaderboard(cells).entries[0].forward
    assert stratum is not None
    assert stratum.mean_brier_score is None
    assert stratum.mean_vote_accuracy is None
    assert stratum.mean_reasoning_quality is None


def test_iter_evaluations_missing_ledger_is_empty(tmp_path: Path) -> None:
    assert iter_evaluations(tmp_path) == []
    assert iter_stratified_evaluations(tmp_path) == []


def test_iter_evaluations_reads_ledger(tmp_path: Path) -> None:
    _write(tmp_path, _evaluation("alpha", event_id="evt-a"))
    _write(tmp_path, _evaluation("beta", event_id="evt-b"))
    found = iter_evaluations(tmp_path)
    assert {e.predictor_id for e in found} == {"alpha", "beta"}


def test_iter_stratified_evaluations_joins_prediction_and_outcome(tmp_path: Path) -> None:
    # A prediction committed before resolution is forward; one committed after
    # (a different event) is retrospective.
    _write_cell(
        tmp_path,
        _evaluation("alpha", event_id="evt-a"),
        predicted_at=datetime(2026, 6, 20, tzinfo=UTC),
        resolved_at=date(2026, 6, 23),
    )
    _write_cell(
        tmp_path,
        _evaluation("alpha", event_id="evt-b"),
        predicted_at=datetime(2026, 6, 20, tzinfo=UTC),
        resolved_at=date(1950, 12, 11),
    )
    strata = {ev.event_id: stratum for ev, stratum in iter_stratified_evaluations(tmp_path)}
    assert strata == {"evt-a": FORWARD, "evt-b": RETROSPECTIVE}


def test_cli_writes_valid_sorted_leaderboard(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write_cell(data_root, _evaluation("alpha", correct=0, brier_score=0.3, event_id="evt-a"))
    _write_cell(data_root, _evaluation("beta", correct=1, brier_score=0.2, event_id="evt-b"))
    out = tmp_path / "leaderboard.json"
    result = runner.invoke(
        app,
        ["leaderboard", "--out", str(out)],
        env={"FEDCOURTS_DATA_ROOT": str(data_root)},
    )
    assert result.exit_code == 0, result.output
    assert "2 forward / 0 retrospective" in result.output
    board = read_model(out, Leaderboard)
    assert [e.predictor_id for e in board.entries] == ["beta", "alpha"]
    # Deterministic: a second run reproduces the file byte for byte.
    first = out.read_text()
    runner.invoke(
        app,
        ["leaderboard", "--out", str(out)],
        env={"FEDCOURTS_DATA_ROOT": str(data_root)},
    )
    assert out.read_text() == first


def test_mootness_outcome_routes_to_the_procedural_stratum(tmp_path: Path) -> None:
    # A mootness-basis outcome (a Munsingwear vacatur, a dismissal as moot)
    # carries a label that tracks vacatur practice, not cert-worthiness — the
    # cell segments into the procedural stratum regardless of timing, even
    # when the prediction was a true forward forecast.
    ev = _evaluation("p-moot")
    _write_cell(
        tmp_path,
        ev,
        predicted_at=datetime(2026, 6, 20, tzinfo=UTC),
        resolved_at=date(2026, 6, 23),  # timing alone would read forward
        disposition_basis="mootness",
    )
    ((_, stratum),) = iter_stratified_evaluations(tmp_path)
    assert stratum == PROCEDURAL


def test_procedural_cells_aggregate_separately_and_never_rank(tmp_path: Path) -> None:
    # Predictor A: one real forward win. Predictor B: a perfect score that is
    # purely procedural. A must outrank B — procedural accuracy buys no rank —
    # and the totals must report the segmentation.
    board = build_leaderboard(
        [
            (_evaluation("a", correct=1, brier_score=0.1), FORWARD),
            (_evaluation("b", correct=1, brier_score=0.0), PROCEDURAL),
        ]
    )
    assert [e.predictor_id for e in board.entries] == ["a", "b"]
    a, b = board.entries
    assert a.forward is not None and a.procedural is None
    assert b.forward is None and b.retrospective is None
    assert b.procedural is not None and b.procedural.accuracy == 1.0
    assert board.procedural_evaluations == 1
    assert board.evaluations_total == 2
    assert board.forward_evaluations == 1
