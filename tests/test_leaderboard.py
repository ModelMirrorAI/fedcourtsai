"""Leaderboard aggregation over a small fixture evaluations ledger."""

from datetime import UTC, datetime
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.leaderboard import build_leaderboard
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import Engine, Evaluation, Leaderboard
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.store import iter_evaluations

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


def _write(data_root: Path, ev: Evaluation) -> None:
    court, _, docket = ev.case_id.partition("/")
    path = (
        CasePaths(data_root, court, int(docket))
        .event(ev.event_id)
        .evaluation(ev.evaluator_id, ev.predictor_id, ev.run_id)
    )
    write_json(path, ev)


def test_empty_ledger_is_empty_board() -> None:
    board = build_leaderboard([])
    assert board.predictors_ranked == 0
    assert board.evaluations_total == 0
    assert board.entries == []


def test_aggregates_per_predictor_and_counts() -> None:
    evals = [
        _evaluation("alpha", correct=1, brier_score=0.1, event_id="evt-a"),
        _evaluation("alpha", correct=0, brier_score=0.3, event_id="evt-b", evaluator_id="eval-b"),
        _evaluation("beta", correct=1, brier_score=0.2, event_id="evt-a"),
    ]
    board = build_leaderboard(evals)
    assert board.predictors_ranked == 2
    assert board.evaluations_total == 3
    alpha = next(e for e in board.entries if e.predictor_id == "alpha")
    assert alpha.accuracy == 0.5
    assert alpha.mean_brier_score == 0.2
    assert alpha.events_scored == 2
    assert alpha.evaluations == 2
    assert alpha.evaluators == 2


def test_ranking_orders_by_accuracy_then_brier() -> None:
    evals = [
        _evaluation("low", correct=0, brier_score=0.1),
        _evaluation("high", correct=1, brier_score=0.4),
        _evaluation("mid-a", correct=1, brier_score=0.5),
        _evaluation("mid-b", correct=1, brier_score=0.2),
    ]
    board = build_leaderboard(evals)
    order = [(e.rank, e.predictor_id) for e in board.entries]
    # Accuracy desc; the three perfect-but-tied predictors split on Brier (lower
    # wins); the 0-accuracy predictor sorts last despite its strong Brier score.
    assert order == [(1, "mid-b"), (2, "high"), (3, "mid-a"), (4, "low")]


def test_missing_optionals_average_only_over_present() -> None:
    evals = [
        _evaluation("alpha", brier_score=0.2, vote_accuracy=None, reasoning_quality=None),
        _evaluation("alpha", brier_score=None, vote_accuracy=0.5, reasoning_quality=0.6),
    ]
    board = build_leaderboard(evals)
    entry = board.entries[0]
    assert entry.mean_brier_score == 0.2
    assert entry.mean_vote_accuracy == 0.5
    assert entry.mean_reasoning_quality == 0.6


def test_all_optionals_absent_stay_none() -> None:
    evals = [_evaluation("alpha", brier_score=None, vote_accuracy=None, reasoning_quality=None)]
    entry = build_leaderboard(evals).entries[0]
    assert entry.mean_brier_score is None
    assert entry.mean_vote_accuracy is None
    assert entry.mean_reasoning_quality is None


def test_iter_evaluations_missing_ledger_is_empty(tmp_path: Path) -> None:
    assert iter_evaluations(tmp_path) == []


def test_iter_evaluations_reads_ledger(tmp_path: Path) -> None:
    _write(tmp_path, _evaluation("alpha", event_id="evt-a"))
    _write(tmp_path, _evaluation("beta", event_id="evt-b"))
    found = iter_evaluations(tmp_path)
    assert {e.predictor_id for e in found} == {"alpha", "beta"}


def test_cli_writes_valid_sorted_leaderboard(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _write(data_root, _evaluation("alpha", correct=0, brier_score=0.3))
    _write(data_root, _evaluation("beta", correct=1, brier_score=0.2))
    out = tmp_path / "leaderboard.json"
    result = runner.invoke(
        app,
        ["leaderboard", "--out", str(out)],
        env={"FEDCOURTS_DATA_ROOT": str(data_root)},
    )
    assert result.exit_code == 0, result.output
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
