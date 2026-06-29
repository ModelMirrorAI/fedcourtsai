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
