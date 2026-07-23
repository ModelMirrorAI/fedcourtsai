"""CLI glue for the collect guardrail commands.

The decisions live in :mod:`fedcourtsai.collect` (tested in ``test_collect.py``);
this covers the thin command layer: the path-jail exit code and ``::error::``
text, and the JSON the collect step parses with ``jq``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths

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
    result = runner.invoke(
        app,
        ["cleanup-out-of-scope-predictions", "--run-id", "RID", "--issue", "320"],
        env=env,
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["removed"] is False
    assert payload["prunable"][0]["case_id"] == "scotus/1004191"
    # The PR block (branch/title/body) is rendered by the command, not the workflow.
    assert payload["pr"]["branch"] == "cleanup/out-of-scope-predictions-RID"
    assert "Closes #320." in payload["pr"]["body"]
    assert pred_root.exists()  # dry-run leaves the tree intact


def test_cleanup_predictions_empty_emits_null_pr(tmp_path: Path) -> None:
    # No out-of-scope cases -> nothing to prune and no PR to open.
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/2400001", court="scotus", docket_number="24-101")],
        )
    env = {"FEDCOURTS_DATA_ROOT": str(tmp_path / "data"), "FEDCOURTS_CORPUS_ROOT": str(corpus_root)}
    result = runner.invoke(app, ["cleanup-out-of-scope-predictions"], env=env)
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["prunable"] == [] and payload["pr"] is None


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
        "stalled": False,
        "dead_actors": [],
        # Present even on an empty run: the collect action reads the warning
        # noun off the plan rather than re-deriving the role's vocabulary.
        "noun": "prediction",
        "missing_artifacts": [],
        "uncovered_cells": [],
        "cell_failures": [],
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
    # Regression: each cell artifact ships the whole data/ tree, so a prior
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


_CELL = {"court": "scotus", "docket": 1, "event_id": "evt-x", "run_id": "R"}
_READY = {"produced": True, "validated": True, "agent_ok": True}


def _matrix(tmp_path: Path, *actors: str) -> Path:
    path = tmp_path / "plan-matrix.json"
    path.write_text(json.dumps({"include": [{"predictor_id": a, **_CELL} for a in actors]}))
    return path


def test_collect_plan_matrix_file_names_cells_that_uploaded_nothing(tmp_path: Path) -> None:
    """The CLI wiring for the queued-cell census: a matrix entry with no
    corresponding status.json is reported and holds the trigger issue open."""
    cells = tmp_path / "cells"
    _write_cell(cells, "cell-a", actor="claude-baseline", **_CELL, **_READY)
    result = runner.invoke(
        app,
        [
            "collect-plan",
            "--role",
            "predict",
            "--run-id",
            "R",
            "--status-dir",
            str(cells),
            "--issue",
            "42",
            "--matrix-file",
            str(_matrix(tmp_path, "claude-baseline", "gemini-baseline")),
        ],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert [c["actor"] for c in plan["uncovered_cells"]] == ["gemini-baseline"]
    assert "Closes #42" not in plan["ready"]["body"]


def test_collect_plan_missing_file_names_transfer_lost_cells(tmp_path: Path) -> None:
    cells = tmp_path / "cells"
    _write_cell(cells, "cell-a", actor="claude-baseline", **_CELL, **_READY)
    missing = tmp_path / "missing.txt"
    missing.write_text("predict-gemini-baseline-scotus-1-evt-x\n")
    result = runner.invoke(
        app,
        [
            "collect-plan",
            "--role",
            "predict",
            "--run-id",
            "R",
            "--status-dir",
            str(cells),
            "--issue",
            "42",
            "--missing-file",
            str(missing),
        ],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert plan["missing_artifacts"] == ["predict-gemini-baseline-scotus-1-evt-x"]
    assert "Closes #42" not in plan["ready"]["body"]


@pytest.mark.parametrize(
    ("label", "content"),
    [
        ("truncated", '{"include":[{"predictor_id":"claude-base'),
        ("not an object", '["a","b"]'),
        ("entry missing keys", '{"include":[{"court":"scotus"}]}'),
        ("no include key", "{}"),
        ("empty file", ""),
    ],
)
def test_a_malformed_matrix_degrades_the_census_and_never_costs_the_run(
    tmp_path: Path, label: str, content: str
) -> None:
    """The census is advisory; the aggregation alongside it carries the run's
    only copy of its agent output. A matrix that fails to parse must not abort
    `collect-plan` — under `set -euo pipefail` that kills the aggregate step
    before any commit, discarding every cell. It would also be deterministic, so
    a rerun fails identically and strands the run.
    """
    cells = tmp_path / "cells"
    _write_cell(cells, "cell-a", actor="claude-baseline", **_CELL, **_READY)
    bad = tmp_path / "bad-matrix.json"
    bad.write_text(content)
    result = runner.invoke(
        app,
        [
            "collect-plan",
            "--role",
            "predict",
            "--run-id",
            "R",
            "--status-dir",
            str(cells),
            "--issue",
            "42",
            "--matrix-file",
            str(bad),
        ],
    )
    assert result.exit_code == 0, f"{label}: a bad matrix must not abort the aggregation"
    plan = json.loads(result.stdout)
    # The run's actual output still aggregates; only the census is lost.
    assert plan["ready"]["artifact_dirs"] == ["cell-a"]
    assert plan["uncovered_cells"] == []


def test_an_absent_matrix_file_is_simply_no_census(tmp_path: Path) -> None:
    cells = tmp_path / "cells"
    _write_cell(cells, "cell-a", actor="claude-baseline", **_CELL, **_READY)
    result = runner.invoke(
        app,
        [
            "collect-plan",
            "--role",
            "predict",
            "--run-id",
            "R",
            "--status-dir",
            str(cells),
            "--issue",
            "42",
            "--matrix-file",
            str(tmp_path / "does-not-exist.json"),
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["uncovered_cells"] == []


def test_record_cell_failures_writes_run_scoped_facts_and_reruns_overwrite(
    tmp_path: Path,
) -> None:
    """The attempt-recording seam end to end: `collect-plan` decides the failed
    partition and carries it in its JSON; `record-cell-failures` materializes one
    run-scoped `attempt.json` per failed cell. A rerun (same run id) overwrites
    rather than duplicating, so the deriver's ledger count cannot inflate."""
    cells = tmp_path / "cells"
    # A ready cell keeps claude-baseline a live engine; a skipped sibling (docket 2)
    # is the truly-failed cell whose fact we expect.
    _write_cell(cells, "cell-a", actor="claude-baseline", **_CELL, **_READY)
    _write_cell(
        cells,
        "cell-b",
        actor="claude-baseline",
        court="scotus",
        docket=2,
        event_id="evt-x",
        run_id="R",
        produced=False,
        validated=False,
        agent_ok=False,
    )
    plan_json = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(cells)],
    )
    assert plan_json.exit_code == 0
    plan = json.loads(plan_json.stdout)
    assert [f["error_class"] for f in plan["cell_failures"]] == ["no_output"]

    plan_file = tmp_path / "plan.json"
    plan_file.write_text(plan_json.stdout)
    data_root = tmp_path / "data"
    result = runner.invoke(
        app,
        ["record-cell-failures", "--plan-file", str(plan_file), "--data-root", str(data_root)],
    )
    assert result.exit_code == 0

    fact_path = (
        CasePaths(data_root, "scotus", 2).event("evt-x").prediction_attempt("claude-baseline", "R")
    )
    assert fact_path.is_file()
    assert json.loads(fact_path.read_text())["error_class"] == "no_output"
    predictions = fact_path.parent.parent  # predictions/claude-baseline/
    assert len(list(predictions.glob("*/attempt.json"))) == 1

    # Rerun of the same run id overwrites its own fact — no second file.
    assert (
        runner.invoke(
            app,
            ["record-cell-failures", "--plan-file", str(plan_file), "--data-root", str(data_root)],
        ).exit_code
        == 0
    )
    assert len(list(predictions.glob("*/attempt.json"))) == 1
