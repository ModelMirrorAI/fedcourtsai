"""CLI glue for the trigger-authorization and finalize-produced commands.

The decisions live in :mod:`fedcourtsai.authz` / :mod:`fedcourtsai.finalize` (tested
in ``test_authz.py`` / ``test_finalize.py``); this covers the thin command layer:
exit codes and the ``true``/``false`` the cell's status step reads.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli
from fedcourtsai.authz import AuthDecision
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths

runner = CliRunner()


def test_authorize_trigger_bot_exits_zero() -> None:
    result = runner.invoke(
        app,
        ["authorize-trigger", "--sender-type", "Bot", "--actor", "pipeline[bot]", "--repo", "o/r"],
    )
    assert result.exit_code == 0
    assert "pipeline App handoff" in result.stdout


def test_authorize_trigger_refusal_exits_one_with_workflow_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        cli, "authorize_trigger", lambda *a, **k: AuthDecision(False, "nope; refusing to run.")
    )
    result = runner.invoke(
        app,
        ["authorize-trigger", "--sender-type", "User", "--actor", "x", "--repo", "o/r"],
    )
    assert result.exit_code == 1
    assert "::error::nope; refusing to run." in result.output


def test_finalize_produced_reports_prediction_presence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path))
    args = [
        "finalize-produced",
        "--role",
        "predict",
        "--court",
        "ca9",
        "--docket",
        "1",
        "--event",
        "evt-x",
        "--actor",
        "claude-baseline",
        "--run-id",
        "R",
    ]
    # No prediction yet — only the (absent) scaffold.
    assert runner.invoke(app, args).stdout.strip() == "false"
    # Write the agent's prediction at the canonical path.
    prediction = CasePaths(tmp_path, "ca9", 1).event("evt-x").prediction("claude-baseline", "R")
    prediction.parent.mkdir(parents=True)
    prediction.write_text("{}")
    assert runner.invoke(app, args).stdout.strip() == "true"


def _cell_outputs(role: str) -> list[str]:
    args = [
        "cell-outputs",
        "--role",
        role,
        "--court",
        "ca9",
        "--docket",
        "1",
        "--event",
        "evt-x",
        "--actor",
        "judge" if role == "evaluate" else "claude-baseline",
        "--run-id",
        "R",
    ]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    return result.stdout.strip().splitlines()


def test_cell_outputs_names_the_predict_cells_whole_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The watchdog's completion sentinel, and it must be the *whole* set.

    A short list would let the reaper end a step whose agent was still writing,
    which is the one outcome worse than the destruction it prevents — so the
    files are named through :mod:`fedcourtsai.paths` rather than spelled here,
    and the root the quiescence test walks has to contain every one of them.
    """
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path))
    root, *paths = _cell_outputs("predict")
    events = CasePaths(tmp_path, "ca9", 1).event("evt-x")
    assert Path(root) == events.prediction_dir("claude-baseline", "R")
    assert [Path(p) for p in paths] == [
        events.prediction("claude-baseline", "R"),
        events.reasoning("claude-baseline", "R"),
        events.predicted_reasoning("claude-baseline", "R"),
        events.prediction_retrieval("claude-baseline", "R"),
        events.prediction_tooling("claude-baseline", "R"),
    ]
    assert all(Path(p).is_relative_to(root) for p in paths)


def test_cell_outputs_names_one_pair_per_staged_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An evaluate cell's set is per-candidate, and keyed on the *aliases*.

    The judge writes under the staging alias and the un-aliasing runs in the
    cell's tail, long after the sentinel has to recognize the files — so the
    list is read from the same `record/blinded/` listing the agent is told to
    enumerate. Reading the alias map instead would make the sentinel disagree
    with the contract whenever staging dropped a candidate.
    """
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path))
    case = CasePaths(tmp_path, "ca9", 1)
    for alias in ("candidate-b", "candidate-a"):
        case.blinded_prediction_dir(alias).mkdir(parents=True)
    root, *paths = _cell_outputs("evaluate")
    events = case.event("evt-x")
    assert Path(root) == events.evaluator_dir("judge")
    assert [Path(p) for p in paths] == [
        events.evaluation_retrieval("judge", "R"),
        events.evaluation_tooling("judge", "R"),
        events.evaluation("judge", "candidate-a", "R"),
        events.evaluation_notes("judge", "candidate-a", "R"),
        events.evaluation("judge", "candidate-b", "R"),
        events.evaluation_notes("judge", "candidate-b", "R"),
    ]
    # The judge-level files and the per-candidate ones sit at different depths
    # under one root, which is what the quiescence walk has to cover.
    assert all(Path(p).is_relative_to(root) for p in paths)


def test_cell_outputs_refuses_an_evaluate_cell_with_nothing_staged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No candidates is no completion set, and a vacuous one would be dangerous.

    An empty required-output list is satisfied by an empty tree, so emitting one
    would arm a reaper that fires on the first quiet poll — before the agent has
    written anything. Refusing leaves the watchdog on its deadline alone, which
    is the behaviour without a sentinel at all.
    """
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path))
    result = runner.invoke(
        app,
        [
            "cell-outputs",
            "--role",
            "evaluate",
            "--court",
            "ca9",
            "--docket",
            "1",
            "--event",
            "evt-x",
            "--actor",
            "judge",
            "--run-id",
            "R",
        ],
    )
    assert result.exit_code == 1
    assert "::error::no blinded candidates are staged" in result.output
