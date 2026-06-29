"""CLI glue for the collect guardrail commands.

The decisions live in :mod:`fedcourtsai.collect` (tested in ``test_collect.py``);
this covers the thin command layer: the path-jail exit code and ``::error::``
text, and the JSON the collect step parses with ``jq``.
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app

runner = CliRunner()


def _write_changes(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "changes.txt"
    path.write_text(text)
    return path


def test_assert_paths_ok_exits_zero(tmp_path: Path) -> None:
    changes = _write_changes(tmp_path, "A\tdata/cases/scotus/1/events/e/x/R/prediction.json\n")
    result = runner.invoke(app, ["assert-paths", "--name-status-file", str(changes)])
    assert result.exit_code == 0
    assert "path jail OK" in result.stdout


def test_assert_paths_violation_exits_one_with_workflow_error(tmp_path: Path) -> None:
    changes = _write_changes(tmp_path, "M\tsrc/fedcourtsai/cli.py\n")
    result = runner.invoke(app, ["assert-paths", "--name-status-file", str(changes)])
    assert result.exit_code == 1
    assert "::error::" in result.output
    assert "outside the data/ jail" in result.output


def test_assert_paths_run_id_scope(tmp_path: Path) -> None:
    changes = _write_changes(tmp_path, "A\tdata/cases/scotus/1/events/e/x/OTHER/prediction.json\n")
    result = runner.invoke(
        app, ["assert-paths", "--name-status-file", str(changes), "--run-id", "R"]
    )
    assert result.exit_code == 1
    assert "not under run id 'R'" in result.output


def _write_cell(root: Path, name: str, **fields: object) -> None:
    cell = root / name
    (cell / "data").mkdir(parents=True)
    (cell / "status.json").write_text(json.dumps(fields))


def test_collect_plan_emits_ready_and_partial_json(tmp_path: Path) -> None:
    base = dict(court="scotus", docket=1, event_id="evt-x", run_id="R")
    _write_cell(
        tmp_path,
        "cell-a",
        actor="claude-baseline",
        produced=True,
        validated=True,
        agent_ok=True,
        **base,
    )
    _write_cell(
        tmp_path,
        "cell-b",
        actor="codex-baseline",
        produced=True,
        validated=False,
        agent_ok=True,
        **base,
    )

    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert plan["ready"]["branch"] == "predict/run-R"
    assert plan["ready"]["artifact_dirs"] == ["cell-a"]
    assert plan["ready"]["draft"] is False
    assert plan["partial"]["artifact_dirs"] == ["cell-b"]
    assert plan["partial"]["draft"] is True


def test_collect_plan_no_cells_emits_nulls(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"ready": None, "partial": None, "skipped": []}


def test_collect_reconcile_plan_emits_per_case_json(tmp_path: Path) -> None:
    _write_cell(
        tmp_path,
        "reconcile-scotus-1",
        court="scotus",
        docket=1,
        run_id="R",
        settled=["evt-petition-disposition"],
        validated=True,
        agent_ok=True,
    )
    _write_cell(
        tmp_path,
        "reconcile-scotus-2",
        court="scotus",
        docket=2,
        run_id="R",
        settled=[],
        validated=False,
        agent_ok=True,
    )

    result = runner.invoke(
        app,
        ["collect-reconcile-plan", "--run-id", "R", "--status-dir", str(tmp_path), "--issue", "7"],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert plan["ready"]["branch"] == "reconcile/run-R"
    assert plan["ready"]["commit_message"].startswith("reconcile:")
    assert plan["ready"]["artifact_dirs"] == ["reconcile-scotus-1"]
    assert "Closes #7" in plan["ready"]["body"]
    # docket 2 settled nothing -> skipped, serialized as court/docket only.
    assert plan["partial"] is None
    assert plan["skipped"] == [{"court": "scotus", "docket": 2}]
