"""CLI glue for the workflow commands the YAML now calls.

The decisions live in :mod:`fedcourtsai.authz` / :mod:`fedcourtsai.finalize` (tested
in ``test_authz.py`` / ``test_finalize.py``); this covers the thin command layer:
exit codes, the JSON the finalize step parses with ``jq``, and the ``true``/``false``
workflow-bool parsing.
"""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli
from fedcourtsai.authz import AuthDecision
from fedcourtsai.cli import app

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


def test_finalize_branch_prints_branch() -> None:
    result = runner.invoke(
        app,
        [
            "finalize-branch",
            "--role",
            "predict",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-motion-x",
            "--actor",
            "claude-baseline",
            "--run-id",
            "R",
        ],
    )
    assert result.exit_code == 0
    assert result.stdout.strip() == "predict/ca9-123-evt-motion-x-claude-baseline-R"


def test_finalize_branch_reconcile_ignores_event_and_actor() -> None:
    result = runner.invoke(
        app,
        [
            "finalize-branch",
            "--role",
            "reconcile",
            "--court",
            "ca9",
            "--docket",
            "7",
            "--run-id",
            "R",
        ],
    )
    assert result.stdout.strip() == "reconcile/ca9-7-R"


def test_finalize_pr_emits_open_plan_as_json() -> None:
    result = runner.invoke(
        app,
        [
            "finalize-pr",
            "--role",
            "predict",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-motion-x",
            "--actor",
            "claude-baseline",
            "--run-id",
            "R",
            "--agent-ok",
            "true",
            "--validated",
            "true",
            "--changed",
            "true",
        ],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert plan["action"] == "open"
    assert plan["draft"] is False
    assert plan["title"] == "predict(claude-baseline): ca9/123 — evt-motion-x"


def test_finalize_pr_reconcile_plan() -> None:
    result = runner.invoke(
        app,
        [
            "finalize-pr",
            "--role",
            "reconcile",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--run-id",
            "R",
            "--agent-ok",
            "true",
            "--validated",
            "true",
            "--settled",
            "evt-a,evt-b",
            "--issue",
            "42",
        ],
    )
    plan = json.loads(result.stdout)
    assert plan["action"] == "open"
    assert "Closes #42" in plan["body"]


def test_finalize_pr_rejects_non_boolean_flag() -> None:
    result = runner.invoke(
        app,
        [
            "finalize-pr",
            "--role",
            "predict",
            "--court",
            "ca9",
            "--docket",
            "1",
            "--event",
            "e",
            "--actor",
            "a",
            "--run-id",
            "R",
            "--agent-ok",
            "yes",
            "--validated",
            "true",
            "--changed",
            "true",
        ],
    )
    assert result.exit_code != 0
