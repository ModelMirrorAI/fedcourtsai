"""CLI glue for the collect guardrail commands.

The decisions live in :mod:`fedcourtsai.collect` (tested in ``test_collect.py``);
this covers the thin command layer: the path-jail exit code and ``::error::``
text, and the JSON the collect step parses with ``jq``.
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus
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


def test_assert_cleanup_paths_ok_exits_zero(tmp_path: Path) -> None:
    changes = _write_changes(
        tmp_path,
        "D\tdata/cases/scotus/1004191/events/evt-petition-disposition/predictions/codex-baseline/R/prediction.json\n",
    )
    result = runner.invoke(app, ["assert-cleanup-paths", "--name-status-file", str(changes)])
    assert result.exit_code == 0
    assert "cleanup jail OK" in result.stdout


def test_assert_cleanup_paths_violation_exits_one_with_workflow_error(tmp_path: Path) -> None:
    # A delete outside a predictions subtree (here the event's outcome) is refused.
    changes = _write_changes(
        tmp_path, "D\tdata/cases/scotus/1/events/evt-petition-disposition/outcome.json\n"
    )
    result = runner.invoke(app, ["assert-cleanup-paths", "--name-status-file", str(changes)])
    assert result.exit_code == 1
    assert "::error::" in result.output
    assert "predictions/ subtree" in result.output


def _cleanup_env(tmp_path: Path) -> dict[str, str]:
    """A corpus with one out-of-scope case plus a committed prediction for it."""
    data_root = tmp_path / "data"
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/1004191", court="scotus", docket_number="01-7700")],
        )
    pred_dir = (
        data_root
        / "cases/scotus/1004191/events/evt-petition-disposition/predictions/codex-baseline/RID"
    )
    pred_dir.mkdir(parents=True)
    (pred_dir / "prediction.json").write_text("{}")
    return {"FEDCOURTS_DATA_ROOT": str(data_root), "FEDCOURTS_CORPUS_ROOT": str(corpus_root)}


def test_cleanup_predictions_dry_run_lists_without_deleting(tmp_path: Path) -> None:
    env = _cleanup_env(tmp_path)
    pred_root = Path(env["FEDCOURTS_DATA_ROOT"]) / (
        "cases/scotus/1004191/events/evt-petition-disposition/predictions"
    )
    result = runner.invoke(app, ["cleanup-out-of-scope-predictions"], env=env)
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["removed"] is False
    assert payload["prunable"][0]["case_id"] == "scotus/1004191"
    assert pred_root.exists()  # dry-run leaves the tree intact


def test_cleanup_predictions_apply_removes_dirs(tmp_path: Path) -> None:
    env = _cleanup_env(tmp_path)
    pred_root = Path(env["FEDCOURTS_DATA_ROOT"]) / (
        "cases/scotus/1004191/events/evt-petition-disposition/predictions"
    )
    result = runner.invoke(app, ["cleanup-out-of-scope-predictions", "--apply"], env=env)
    assert result.exit_code == 0
    assert json.loads(result.stdout)["removed"] is True
    assert not pred_root.exists()


def test_cleanup_predictions_fails_loud_without_corpus(tmp_path: Path) -> None:
    env = {
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
        "FEDCOURTS_CORPUS_ROOT": str(tmp_path / "nope"),
    }
    result = runner.invoke(app, ["cleanup-out-of-scope-predictions"], env=env)
    assert result.exit_code == 1
    assert "corpus database is missing" in result.output


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
    assert json.loads(result.stdout) == {
        "ready": None,
        "partial": None,
        "skipped": [],
        "flags": "",
        "feedback_comment": "",
    }


def _write_flags(root: Path, cell: str, actor: str, *, run_id: str = "R", case: str = "1") -> None:
    # A cell's flags.json lands under its data/ subtree, like the agent writes it:
    # predictions/<actor>/<run_id>/, so different (actor, case, run) coexist in one cell.
    flag_dir = (
        root / cell / "data" / "cases" / "scotus" / case / "events" / "evt-x" / actor / run_id
    )
    flag_dir.mkdir(parents=True, exist_ok=True)
    (flag_dir / "flags.json").write_text(
        json.dumps(
            {
                "case_id": f"scotus/{case}",
                "run_id": run_id,
                "role": "predictor",
                "actor_id": actor,
                "flags": [{"category": "data-quality", "severity": "warning", "message": "thin"}],
            }
        )
    )


def test_collect_plan_rolls_up_flag_files(tmp_path: Path) -> None:
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
    _write_flags(tmp_path, "cell-a", "claude-baseline")
    # A blocked cell that produced no judgment still surfaces its flag in the roll-up.
    _write_cell(
        tmp_path,
        "cell-b",
        actor="codex-baseline",
        produced=False,
        validated=False,
        agent_ok=False,
        **base,
    )
    _write_flags(tmp_path, "cell-b", "codex-baseline")
    # A malformed flag file is skipped, not fatal.
    (tmp_path / "cell-a" / "data" / "junk-flags").mkdir()

    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert "🚩 Agent flags (2)" in plan["flags"]
    assert "`codex-baseline`" in plan["flags"]  # the blocked, uncommitted cell's flag still shows
    assert "🚩 Agent flags" in plan["ready"]["body"]
    # The same roll-up is wrapped for the latched agent-feedback issue, marker first.
    assert plan["feedback_comment"].startswith("<!-- agent-feedback-run: predict/R -->")
    assert "🚩 Agent flags" in plan["feedback_comment"]


def test_collect_plan_scopes_flags_to_run_and_dedupes(tmp_path: Path) -> None:
    # Regression for #333: each cell artifact ships the whole data/ tree, so a prior
    # run's committed flags ride along in every cell. They must not inflate this run's
    # roll-up, and a note shipped in more than one cell counts once.
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
        validated=True,
        agent_ok=True,
        **base,
    )
    # This run's flag — counted once even though it rides in both cells' data/ subtrees.
    _write_flags(tmp_path, "cell-a", "claude-baseline")
    _write_flags(tmp_path, "cell-b", "claude-baseline")
    # A prior run's committed flag, carried along in every artifact — excluded.
    _write_flags(tmp_path, "cell-a", "claude-baseline", run_id="Q", case="2")
    _write_flags(tmp_path, "cell-b", "claude-baseline", run_id="Q", case="2")

    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert "🚩 Agent flags (1)" in plan["flags"]
    assert "run `Q`" not in plan["flags"] and "scotus/2" not in plan["flags"]


def test_collect_plan_tolerates_malformed_flag_file(tmp_path: Path) -> None:
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
    bad = tmp_path / "cell-a" / "data"
    bad.mkdir(parents=True, exist_ok=True)
    (bad / "flags.json").write_text("{ not json")

    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["flags"] == ""


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


def test_collect_reconcile_plan_rolls_up_flag_files(tmp_path: Path) -> None:
    # Reconcile flags ride the same channel as predict/evaluate (issue #325).
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
    _write_flags(tmp_path, "reconcile-scotus-1", "codex")

    result = runner.invoke(
        app,
        ["collect-reconcile-plan", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert "🚩 Agent flags" in plan["flags"]
    assert "🚩 Agent flags" in plan["ready"]["body"]
    # Wrapped for the latched agent-feedback issue, keyed on the reconcile role.
    assert plan["feedback_comment"].startswith("<!-- agent-feedback-run: reconcile/R -->")
