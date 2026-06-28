"""The offline ``replay`` engine and the consume path it exercises.

The stub's output is intentionally trivial (the ``denied``/0.0 floor), so it cannot
catch a bug in the code that *consumes* realistic agent output. The committed
cassette under ``tests/cassettes`` is a captured real prediction — a calibrated
grant forecast with panel votes — and these tests drive the consumers over it
offline: the scoring metrics (Brier, vote accuracy) and the leaderboard roll-up.
The realistic numbers are the point; each is contrasted with the degenerate value
the stub would produce.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from fedcourtsai import ids
from fedcourtsai.leaderboard import build_leaderboard
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.cascade import run_cascade
from fedcourtsai.pipeline.runner import (
    ReplayRunner,
    ReplayUnavailable,
    RunRequest,
    get_runner,
)
from fedcourtsai.schemas import Disposition, Evaluation, Prediction, UsageRole
from fedcourtsai.serialize import read_model
from fedcourtsai.store import iter_evaluations
from tests.conftest import FixtureCorpus

CASSETTE = Path(__file__).resolve().parent / "cassettes" / "realistic-grant"

# The captured forecast and the Brier it earns against ca9/101 (actual granted=1):
# (0.82 - 1)^2. The stub would forecast 0.0 and earn the degenerate (0 - 1)^2 = 1.0.
_RECORDED_PROBABILITY = 0.82
_REALISTIC_BRIER = pytest.approx((_RECORDED_PROBABILITY - 1) ** 2)
_STUB_BRIER = 1.0


def _request(role: UsageRole, actor: str, data_root: Path) -> RunRequest:
    return RunRequest(
        role=role,
        court_id="ca9",
        docket_id=101,
        event_id="evt-appeal-disposition",
        actor_id=actor,
        run_id="20230918T120000Z",
        prompt=Path(".github/prompts/predict.md"),
        data_root=data_root,
    )


def test_replay_predict_keeps_the_forecast_and_rebinds_identity(tmp_path: Path) -> None:
    runner = ReplayRunner(cassette_root=CASSETTE)
    written = runner.run(_request(UsageRole.predictor, "codex-baseline", tmp_path))

    prediction = read_model(next(p for p in written if p.suffix == ".json"), Prediction)
    # The recorded forecast is kept verbatim...
    assert prediction.probability == _RECORDED_PROBABILITY
    assert prediction.predicted_disposition == Disposition.granted
    assert [v.judge for v in prediction.votes] == ["berzon", "smith"]
    # ...while the cell identity is rebound to the request (here a different actor).
    assert prediction.predictor_id == "codex-baseline"
    assert prediction.case_id == "ca9/101"
    assert prediction.run_id == "20230918T120000Z"


def test_get_runner_replay_without_cassette_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("FEDCOURTS_REPLAY_ROOT", raising=False)
    with pytest.raises(ReplayUnavailable):
        get_runner("replay")


def test_get_runner_replay_with_cassette_builds_a_replay_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FEDCOURTS_REPLAY_ROOT", str(CASSETTE))
    runner = get_runner("replay")
    assert isinstance(runner, ReplayRunner)
    assert runner.cassette_root == CASSETTE


def test_cascade_over_recorded_prediction_scores_realistically(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`run_cascade(engine="replay")` drives the consume path end to end offline.

    The replayed realistic prediction is scored by the real evaluate code, so the
    evaluation carries a non-degenerate Brier — not the stub floor — and the ledger
    still validates.
    """
    monkeypatch.setenv("FEDCOURTS_REPLAY_ROOT", str(CASSETTE))
    report = run_cascade(
        corpus_db_path=fixture_corpus.db_path,
        data_root=fixture_corpus.data_root,
        config_root=Path("config"),
        court="ca9",
        docket=101,
        engine="replay",
        run_id=ids.run_id(),
    )
    assert report.valid, report.problems
    assert report.evaluations

    evaluation = read_model(next(p for p in report.evaluations if p.suffix == ".json"), Evaluation)
    assert evaluation.correct == 1  # forecast granted, ca9/101 resolved granted
    assert evaluation.brier_score == _REALISTIC_BRIER
    assert evaluation.brier_score != _STUB_BRIER


def test_evaluate_over_recorded_prediction_scores_vote_accuracy(tmp_path: Path) -> None:
    """The votes branch of scoring, which the corpus-built outcome cannot reach.

    The cascade builds its outcome from the corpus (no panel votes), so vote
    accuracy is null there. Scoring the recorded prediction against the recorded
    outcome — which *does* carry votes — exercises that branch: berzon matches,
    smith does not, so accuracy is 0.5.
    """
    runner = ReplayRunner(cassette_root=CASSETTE)
    runner.run(_request(UsageRole.predictor, "claude-baseline", tmp_path))

    events = CasePaths(tmp_path, "ca9", 101).event("evt-appeal-disposition")
    shutil.copyfile(CASSETTE / "outcome.json", events.outcome)

    runner.run(_request(UsageRole.evaluator, "claude-judge", tmp_path))
    evaluation = read_model(
        events.evaluation("claude-judge", "claude-baseline", "20230918T120000Z"), Evaluation
    )
    assert evaluation.vote_accuracy == pytest.approx(0.5)
    assert evaluation.brier_score == _REALISTIC_BRIER
    assert evaluation.correct == 1


def test_leaderboard_rolls_up_recorded_evaluations(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Leaderboard over the evaluations the replay cascade produced.

    With realistic predictions every ranked predictor shows the real accuracy and
    mean Brier, not the stub's degenerate 1.0 — so a regression in the roll-up over
    realistic input would surface here.
    """
    monkeypatch.setenv("FEDCOURTS_REPLAY_ROOT", str(CASSETTE))
    run_cascade(
        corpus_db_path=fixture_corpus.db_path,
        data_root=fixture_corpus.data_root,
        config_root=Path("config"),
        court="ca9",
        docket=101,
        engine="replay",
        run_id=ids.run_id(),
    )
    board = build_leaderboard(iter_evaluations(fixture_corpus.data_root))
    assert board.predictors_ranked >= 1
    for entry in board.entries:
        assert entry.accuracy == pytest.approx(1.0)
        assert entry.mean_brier_score == _REALISTIC_BRIER
        assert entry.mean_brier_score != _STUB_BRIER
