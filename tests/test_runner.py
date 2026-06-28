"""The offline ``stub`` runner backend produces schema-valid, validatable cells."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.runner import (
    ClaudeCodeRunner,
    CodexRunner,
    EngineFailed,
    EngineUnavailable,
    RunRequest,
    StubRunner,
    _run_subprocess,
    get_runner,
)
from fedcourtsai.schemas import (
    Disposition,
    Engine,
    Evaluation,
    Outcome,
    PredictableEvent,
    Prediction,
    UsageRole,
)
from fedcourtsai.serialize import read_model, write_json, write_yaml

COURT = "ca9"
DOCKET = 64512345
EVENT = "evt-motion-stay"
PREDICTOR = "stub-baseline"
EVALUATOR = "stub-judge"
RUN = "20260628T120000Z"


def _seed_event(data_root: Path) -> None:
    """Write the git event definition the ledger references expect for the case."""
    events = CasePaths(data_root, COURT, DOCKET).event(EVENT)
    write_yaml(
        events.event_file,
        PredictableEvent(
            event_id=EVENT,
            case_id=f"{COURT}/{DOCKET}",
            kind="motion",
            title="Motion to stay pending appeal",
        ),
    )


def _predict_request(data_root: Path, *, run: str = RUN, actor: str = PREDICTOR) -> RunRequest:
    return RunRequest(
        role=UsageRole.predictor,
        court_id=COURT,
        docket_id=DOCKET,
        event_id=EVENT,
        actor_id=actor,
        run_id=run,
        prompt=Path(".github/prompts/predict.md"),
        data_root=data_root,
    )


def _evaluate_request(data_root: Path) -> RunRequest:
    return RunRequest(
        role=UsageRole.evaluator,
        court_id=COURT,
        docket_id=DOCKET,
        event_id=EVENT,
        actor_id=EVALUATOR,
        run_id=RUN,
        prompt=Path(".github/prompts/evaluate.md"),
        data_root=data_root,
    )


def _write_outcome(data_root: Path, disposition: Disposition, granted: int) -> None:
    events = CasePaths(data_root, COURT, DOCKET).event(EVENT)
    write_json(
        events.outcome,
        Outcome(
            case_id=f"{COURT}/{DOCKET}",
            event_id=EVENT,
            resolved_at=date(2026, 6, 28),
            actual_disposition=disposition,
            actual_granted=granted,
        ),
    )


# --- registry ------------------------------------------------------------------


def test_get_runner_returns_the_stub_backend() -> None:
    assert get_runner().backend == "stub"
    assert get_runner("stub").backend == "stub"


def test_get_runner_returns_the_real_engine_backends() -> None:
    assert get_runner("claude-code").backend == "claude-code"
    assert get_runner("codex").backend == "codex"


def test_get_runner_rejects_unknown_backend() -> None:
    with pytest.raises(KeyError, match="unknown runner backend"):
        get_runner("does-not-exist")


# --- agentic engine backends ---------------------------------------------------


class _Recorder:
    """A `command_runner` seam that records the call and returns a canned code."""

    def __init__(self, code: int = 0) -> None:
        self.code = code
        self.argv: list[str] = []
        self.env: dict[str, str] = {}

    def __call__(self, argv: Sequence[str], env: Mapping[str, str]) -> int:
        self.argv = list(argv)
        self.env = dict(env)
        return self.code


def test_claude_runner_builds_the_workflow_env_contract(tmp_path: Path) -> None:
    recorder = _Recorder()
    runner = ClaudeCodeRunner(command_runner=recorder)

    # The agent "writes" the prediction pair the runner then reports.
    request = _predict_request(tmp_path / "data")
    StubRunner().run(request)
    written = runner.run(request)

    # The cell env-var contract is byte-identical to run-predict.yml's export.
    assert recorder.env["COURT_ID"] == COURT
    assert recorder.env["DOCKET_ID"] == str(DOCKET)
    assert recorder.env["EVENT_ID"] == EVENT
    assert recorder.env["PREDICTOR_ID"] == PREDICTOR
    assert recorder.env["RUN_ID"] == RUN
    assert "EVALUATOR_ID" not in recorder.env
    # The command targets the `claude` CLI in print mode with the workflow's args.
    assert recorder.argv[0] == "claude"
    assert "-p" in recorder.argv
    assert "bypassPermissions" in recorder.argv
    assert "claude-opus-4-8" in recorder.argv
    # The registry prompt path rides in the instruction it passes the agent.
    assert ".github/prompts/predict.md" in recorder.argv[recorder.argv.index("-p") + 1]
    # It reports the artifacts the agent left at the canonical paths.
    events = CasePaths(tmp_path / "data", COURT, DOCKET).event(EVENT)
    assert written == sorted([events.prediction(PREDICTOR, RUN), events.reasoning(PREDICTOR, RUN)])


def test_evaluate_uses_the_evaluator_id_env_var(tmp_path: Path) -> None:
    recorder = _Recorder()
    runner = ClaudeCodeRunner(command_runner=recorder)
    runner.run(_evaluate_request(tmp_path / "data"))
    # An evaluate cell tags the actor under EVALUATOR_ID, never PREDICTOR_ID.
    assert recorder.env["EVALUATOR_ID"] == EVALUATOR
    assert "PREDICTOR_ID" not in recorder.env


def test_codex_runner_passes_the_prompt_file(tmp_path: Path) -> None:
    recorder = _Recorder()
    runner = CodexRunner(command_runner=recorder)
    runner.run(_predict_request(tmp_path / "data", actor=PREDICTOR))
    assert recorder.argv[:2] == ["codex", "exec"]
    assert "gpt-5.5" in recorder.argv
    # Codex reads the registry prompt file's contents directly (as the action does).
    assert "You are a **predictor**" in recorder.argv[-1]


def test_nonzero_exit_raises_engine_failed(tmp_path: Path) -> None:
    runner = ClaudeCodeRunner(command_runner=_Recorder(code=1))
    with pytest.raises(EngineFailed, match="exited 1"):
        runner.run(_predict_request(tmp_path / "data"))


def test_missing_binary_raises_engine_unavailable() -> None:
    # The default subprocess executor maps a missing CLI to a clear EngineUnavailable.
    with pytest.raises(EngineUnavailable, match="not on PATH"):
        _run_subprocess(["fedcourts-no-such-binary-xyz"], {})


# --- predict -------------------------------------------------------------------


def test_predict_writes_a_schema_valid_prediction_pair(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    events = CasePaths(data_root, COURT, DOCKET).event(EVENT)

    written = StubRunner().run(_predict_request(data_root))

    assert written == sorted([events.prediction(PREDICTOR, RUN), events.reasoning(PREDICTOR, RUN)])
    assert all(p.is_file() for p in written)

    prediction = read_model(events.prediction(PREDICTOR, RUN), Prediction)
    assert prediction.case_id == f"{COURT}/{DOCKET}"
    assert prediction.event_id == EVENT
    assert prediction.predictor_id == PREDICTOR
    assert prediction.run_id == RUN
    assert prediction.engine == Engine.claude_code
    assert prediction.predicted_disposition == Disposition.denied
    # created_at is derived from the run id, so the stub needs no clock.
    assert prediction.created_at.strftime("%Y%m%dT%H%M%SZ") == RUN
    assert prediction.input_snapshot == (
        f"data/cases/{COURT}/{DOCKET}/record/snapshots/2026-06-28.json"
    )
    assert events.reasoning(PREDICTOR, RUN).read_text().endswith("\n")


def test_predict_is_deterministic(tmp_path: Path) -> None:
    # Same inputs (including the output root) → byte-identical artifacts: no clock,
    # no randomness, so re-running the cell reproduces it exactly.
    data_root = tmp_path / "data"
    prediction = CasePaths(data_root, COURT, DOCKET).event(EVENT).prediction(PREDICTOR, RUN)
    StubRunner().run(_predict_request(data_root))
    first = prediction.read_bytes()
    StubRunner().run(_predict_request(data_root))
    assert prediction.read_bytes() == first


# --- evaluate ------------------------------------------------------------------


def test_evaluate_scores_each_predictor_against_the_outcome(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    events = CasePaths(data_root, COURT, DOCKET).event(EVENT)

    # Two predictors produce predictions, then the event resolves denied.
    StubRunner().run(_predict_request(data_root, actor="stub-baseline"))
    StubRunner().run(_predict_request(data_root, actor="other-predictor"))
    _write_outcome(data_root, Disposition.denied, granted=0)

    written = StubRunner().run(_evaluate_request(data_root))

    # One evaluation pair per predictor.
    assert len(written) == 4
    for predictor in ("stub-baseline", "other-predictor"):
        evaluation = read_model(events.evaluation(EVALUATOR, predictor, RUN), Evaluation)
        assert evaluation.evaluator_id == EVALUATOR
        assert evaluation.predictor_id == predictor
        # The stub predicted denied; the outcome is denied → correct, Brier 0.
        assert evaluation.correct == 1
        assert evaluation.brier_score == 0.0
        assert evaluation.vote_accuracy is None
        md = events.evaluation_dir(EVALUATOR, predictor, RUN) / "evaluation.md"
        assert md.read_text().endswith("\n")


def test_evaluate_brier_tracks_the_outcome(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    events = CasePaths(data_root, COURT, DOCKET).event(EVENT)
    StubRunner().run(_predict_request(data_root))
    # Stub predicts denied / P(granted)=0; a granted outcome makes it wrong.
    _write_outcome(data_root, Disposition.granted, granted=1)

    StubRunner().run(_evaluate_request(data_root))

    evaluation = read_model(events.evaluation(EVALUATOR, PREDICTOR, RUN), Evaluation)
    assert evaluation.correct == 0
    assert evaluation.brier_score == 1.0


def test_evaluate_with_no_outcome_writes_nothing(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    StubRunner().run(_predict_request(data_root))
    # No outcome.json yet: there is nothing to evaluate.
    assert StubRunner().run(_evaluate_request(data_root)) == []


# --- end to end through `fedcourts validate` -----------------------------------


def test_stub_artifacts_pass_validate(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _seed_event(data_root)
    StubRunner().run(_predict_request(data_root))
    _write_outcome(data_root, Disposition.denied, granted=0)
    StubRunner().run(_evaluate_request(data_root))

    result = CliRunner().invoke(app, ["validate", str(data_root)])

    assert result.exit_code == 0, result.output
    assert "valid" in result.output
