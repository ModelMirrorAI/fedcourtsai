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
        # No cell failed and no matrix census, so no facts-only PR either.
        "facts_only": None,
        "skipped": [],
        "flags": "",
        # A run with no cells has no retrieval to have been throttled, and no
        # blind cell either — nothing to say, on this surface or in a PR body.
        "throttle": "",
        # Nor any cell that asked the corpus for priors, which is not a claim
        # that the priors arrived.
        "prior_availability": "",
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


def _write_retrieval_log(
    root: Path,
    cell: str,
    actor: str,
    *,
    statuses: list[str],
    run_id: str = "R",
    case: str = "1",
    tool: str = "mcp__courtlistener__search",
) -> None:
    # Same shape as a cell's flags.json: the harness writes it under the cell's
    # own data/ subtree, so every artifact also carries every previously
    # committed log.
    log_dir = root / cell / "data" / "cases" / "scotus" / case / "events" / "evt-x" / actor / run_id
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "retrieval_log.json").write_text(
        json.dumps(
            {
                "case_id": f"scotus/{case}",
                "run_id": run_id,
                "role": "predictor",
                "actor_id": actor,
                "engine": "claude-code",
                "calls": [
                    {
                        "tool": tool,
                        "result_capture": ("unobserved" if s == "unobserved" else "captured"),
                        "result_status": s,
                    }
                    for s in statuses
                ],
            }
        )
    )


def _cell_dir(root: Path, cell: str, actor: str, *, run_id: str, case: str, event: str) -> Path:
    path = root / cell / "data" / "cases" / "scotus" / case / "events" / event / actor / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_query_log(
    root: Path,
    cell: str,
    actor: str,
    *,
    run_id: str = "R",
    case: str = "1",
    event: str = "evt-x",
    calls: list[dict[str, object]] | None = None,
) -> None:
    """A cell log whose captured shell ran `fedcourts query`, unless told otherwise."""
    rows = (
        calls if calls is not None else [{"tool": "Bash", "query": "uv run fedcourts query -n 5"}]
    )
    cell_dir = _cell_dir(root, cell, actor, run_id=run_id, case=case, event=event)
    (cell_dir / "retrieval_log.json").write_text(
        json.dumps(
            {
                "case_id": f"scotus/{case}",
                "run_id": run_id,
                "role": "predictor",
                "actor_id": actor,
                "engine": "claude-code",
                "calls": rows,
            }
        )
    )


def _write_tooling(
    root: Path,
    cell: str,
    actor: str,
    *,
    used_corpus_query: bool,
    run_id: str = "R",
    case: str = "1",
    event: str = "evt-x",
) -> None:
    cell_dir = _cell_dir(root, cell, actor, run_id=run_id, case=case, event=event)
    (cell_dir / "tooling.json").write_text(
        json.dumps(
            {
                "case_id": f"scotus/{case}",
                "run_id": run_id,
                "role": "predictor",
                "actor_id": actor,
                "used_corpus_query": used_corpus_query,
            }
        )
    )


def test_collect_plan_names_the_cells_the_corpus_did_not_serve(tmp_path: Path) -> None:
    # The starvation this makes visible fails no cell: a `fedcourts query` that
    # times out leaves a finished prediction built on thinner priors, and the
    # only trace is one line in one cell's tooling report.
    base = dict(court="scotus", docket=1, event_id="evt-x", run_id="R")
    for name, actor in (("cell-a", "claude-baseline"), ("cell-b", "codex-baseline")):
        _write_cell(
            tmp_path, name, actor=actor, produced=True, validated=True, agent_ok=True, **base
        )
    # Asked and did not get it.
    _write_query_log(tmp_path, "cell-a", "claude-baseline")
    _write_tooling(tmp_path, "cell-a", "claude-baseline", used_corpus_query=False)
    # Asked and got it.
    _write_query_log(tmp_path, "cell-b", "codex-baseline", case="2")
    _write_tooling(tmp_path, "cell-b", "codex-baseline", used_corpus_query=True, case="2")
    # Asked, and wrote no report at all: unknown, not starved.
    _write_query_log(tmp_path, "cell-b", "gemini-baseline", case="3")
    # Never asked — outside the denominator entirely.
    _write_query_log(
        tmp_path,
        "cell-a",
        "quiet-baseline",
        case="4",
        calls=[{"tool": "Bash", "query": "uv run fedcourts paths --court scotus"}],
    )
    # A prior run's committed log, carried in every artifact — excluded.
    _write_query_log(tmp_path, "cell-a", "claude-baseline", run_id="Q", case="9")

    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    # The note leaves the process on the plan JSON as well as in the PR body.
    assert "Cells ran a corpus query and reported no corpus use" in plan["prior_availability"]
    body = plan["ready"]["body"]
    assert "1 of 3 cell(s)" in body
    # Named as case/event/actor, so a reader knows which predictions are thin.
    assert "`scotus/1/evt-x/claude-baseline`" in body
    # The report-less cell is unknown rather than starved, and gets its own line.
    assert "Whether the corpus served 1 of 3 cell(s) with a legible attempt cannot be read" in body
    assert "`scotus/3/evt-x/gemini-baseline`" in body


def test_collect_plan_sees_a_code_mode_cell_s_corpus_attempt(tmp_path: Path) -> None:
    # A code-mode cell runs every command from inside one program, so its
    # corpus attempt reaches the log as a row lifted out of that program's
    # source under the builtin's name. Without this the engine that predicts
    # this way is absent from the note's denominator however often it queried,
    # and the note's engine split reads as "that engine never asks".
    base = dict(court="scotus", docket=1, event_id="evt-x", run_id="R")
    _write_cell(
        tmp_path,
        "cell-a",
        actor="codex-baseline",
        produced=True,
        validated=True,
        agent_ok=True,
        **base,
    )
    _write_query_log(
        tmp_path,
        "cell-a",
        "codex-baseline",
        calls=[
            # The wrapper row: the program's head, which here says nothing
            # about the corpus — the whole point being that the command sits
            # past what this row's own query slice would show.
            {"tool": "exec", "query": "const rows = await Promise.all(reads.map(run));"},
            {
                "tool": "exec_command",
                "query": '{cmd:"uv run fedcourts query --court scotus --limit 5"}',
                "result_capture": "unobserved",
                "result_status": "unobserved",
                "call_source": "code_mode_source",
            },
        ],
    )
    _write_tooling(tmp_path, "cell-a", "codex-baseline", used_corpus_query=False)
    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    body = json.loads(result.stdout)["ready"]["body"]
    assert "1 of 1 cell(s)" in body
    assert "`scotus/1/evt-x/codex-baseline`" in body


def test_collect_plan_counts_two_events_of_one_case_as_two_cells(tmp_path: Path) -> None:
    # A log records the case and the actor but not the event, so a run covering
    # two events of one case for one actor would fold into a single cell — and
    # a note that names cells one by one would silently print one of the two.
    base = dict(court="scotus", docket=1, event_id="evt-a", run_id="R")
    _write_cell(
        tmp_path,
        "cell-a",
        actor="claude-baseline",
        produced=True,
        validated=True,
        agent_ok=True,
        **base,
    )
    for event in ("evt-a", "evt-b"):
        _write_query_log(tmp_path, "cell-a", "claude-baseline", event=event)
        _write_tooling(tmp_path, "cell-a", "claude-baseline", used_corpus_query=False, event=event)
    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    body = json.loads(result.stdout)["ready"]["body"]
    assert "2 of 2 cell(s)" in body
    assert "`scotus/1/evt-a/claude-baseline`" in body
    assert "`scotus/1/evt-b/claude-baseline`" in body


def test_collect_plan_says_nothing_when_every_asking_cell_was_served(tmp_path: Path) -> None:
    # The clean run stays quiet, exactly as the throttle note does: a standing
    # paragraph on a surface read once per run trains the eye to skip it.
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
    _write_query_log(tmp_path, "cell-a", "claude-baseline")
    _write_tooling(tmp_path, "cell-a", "claude-baseline", used_corpus_query=True)
    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert plan["prior_availability"] == ""
    assert "Cells ran a corpus query" not in plan["ready"]["body"]


def test_collect_plan_trips_on_a_code_mode_cell_that_lifted_nothing(tmp_path: Path) -> None:
    # A code-mode cell reaches everything from inside one program, so rows
    # lifted from that program's source are the only evidence of what it did.
    # None beside a program is either a silent program or a lift that stopped
    # matching the engine's idiom — and the attempt count cannot see either.
    base = dict(court="scotus", docket=1, event_id="evt-x", run_id="R")
    _write_cell(
        tmp_path,
        "cell-a",
        actor="codex-baseline",
        produced=True,
        validated=True,
        agent_ok=True,
        **base,
    )
    _write_query_log(
        tmp_path,
        "cell-a",
        "codex-baseline",
        calls=[{"tool": "exec", "query": "const r = await tools.exec_command({cmd: 'ls'})"}],
    )
    # A code-mode cell whose program DID yield a lifted row is not blind.
    _write_query_log(
        tmp_path,
        "cell-a",
        "codex-seeing",
        case="2",
        calls=[
            {"tool": "exec", "query": "const r = await tools.mcp__courtlistener__search({})"},
            {
                "tool": "mcp__courtlistener__search",
                "result_capture": "unobserved",
                "result_status": "unobserved",
                "call_source": "code_mode_source",
            },
        ],
    )
    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    body = json.loads(result.stdout)["ready"]["body"]
    assert "Code-mode capture may be blind" in body
    # One of the two code-mode cells, not one of nothing: the denominator says
    # this is a ratio over the run's code-mode cells, not a fresh alarm.
    assert "1 of 2 cell(s) that called the freeform" in body


def test_collect_plan_counts_this_run_s_throttled_retrieval(tmp_path: Path) -> None:
    # The starvation surface: read from the cells' harness-captured logs, and
    # scoped and deduped exactly like the flags, because every artifact ships
    # the whole data/ tree and an earlier run's throttling is not this run's.
    base = dict(court="scotus", docket=1, event_id="evt-x", run_id="R")
    for name, actor in (("cell-a", "claude-baseline"), ("cell-b", "codex-baseline")):
        _write_cell(
            tmp_path, name, actor=actor, produced=True, validated=True, agent_ok=True, **base
        )
    _write_retrieval_log(tmp_path, "cell-a", "claude-baseline", statuses=["throttled", "ok"])
    # The same cell's log riding along in the other artifact — counted once.
    _write_retrieval_log(tmp_path, "cell-b", "claude-baseline", statuses=["throttled", "ok"])
    _write_retrieval_log(tmp_path, "cell-b", "codex-baseline", statuses=["ok", "ok"])
    # A prior run's committed log, carried in every artifact — excluded.
    _write_retrieval_log(
        tmp_path, "cell-a", "claude-baseline", statuses=["throttled"], run_id="Q", case="2"
    )
    # A capture-blind cell enters neither side of the ratio; it is counted, and
    # named in the note, as a cell that could not be observed either way.
    _write_retrieval_log(
        tmp_path, "cell-b", "gemini-baseline", statuses=["unobserved", "unobserved"]
    )
    # A BUILTIN row marked throttled must not enter the count on the run path
    # either. The parser's tool gate stops one being minted; this is the same
    # exclusion applied again where the run reads it, so a hand-written or
    # legacy row cannot put a `Read` of a document about rate limits into a
    # figure about the upstream refusing this cell.
    _write_retrieval_log(
        tmp_path,
        "cell-b",
        "builtin-reader",
        statuses=["throttled", "throttled"],
        tool="Read",
    )
    # An unreadable log must never take down the aggregation carrying the run's
    # only copy of its output.
    broken = (
        tmp_path / "cell-a" / "data" / "cases" / "scotus" / "1" / "events" / "evt-x" / "b" / "R"
    )
    broken.mkdir(parents=True)
    (broken / "retrieval_log.json").write_text("{not json")

    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    # The note leaves the process on the plan JSON as well as in the PR body,
    # so the surface that echoes `flags` can echo this beside it.
    assert "Retrieval was throttled this run" in plan["throttle"]
    body = plan["ready"]["body"]
    assert "Retrieval was throttled this run" in body
    assert "1 of 4 manifest-tool result(s)" in body
    assert "1 of 2 cell log(s) whose results were legible" in body
    # The Gemini cell, the builtin-only cell, and the unreadable one: all three
    # unobservable, none of them clean, and counted on the note rather than
    # dropped from it. A log nothing can parse is a cell whose condition nothing
    # can read, which is what the counter means.
    assert "3 further cell(s) captured no result" in body


def test_collect_plan_never_reads_a_builtin_result_as_a_throttle(tmp_path: Path) -> None:
    # The end-to-end shape of the false positive the tool gate exists for. An
    # evaluate cell is instructed to read the predictor's artifacts, and a
    # starved cell's `reasoning.md` says so in prose; a run where that is the
    # only "throttle" in sight was not throttled at all, and must not commit a
    # PR body claiming it was.
    base = dict(court="scotus", docket=1, event_id="evt-x", run_id="R")
    _write_cell(
        tmp_path,
        "cell-a",
        actor="claude-judge",
        produced=True,
        validated=True,
        agent_ok=True,
        **base,
    )
    _write_retrieval_log(
        tmp_path, "cell-a", "claude-judge", statuses=["throttled", "ok"], tool="Read"
    )
    _write_retrieval_log(tmp_path, "cell-a", "claude-judge", statuses=["ok"], case="2")
    result = runner.invoke(
        app,
        ["collect-plan", "--role", "evaluate", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    plan = json.loads(result.stdout)
    assert "throttled" not in plan["ready"]["body"]
    # The manifest-tool cell beside it was legible and clean, so the run is a
    # genuine zero and says nothing at all — on either surface.
    assert "not observable" not in plan["ready"]["body"]
    assert plan["throttle"] == ""


def test_collect_plan_says_nothing_when_no_cell_was_throttled(tmp_path: Path) -> None:
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
    _write_retrieval_log(tmp_path, "cell-a", "claude-baseline", statuses=["ok", "ok"])
    result = runner.invoke(
        app,
        ["collect-plan", "--role", "predict", "--run-id", "R", "--status-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "throttled" not in json.loads(result.stdout)["ready"]["body"]


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


def test_a_no_artifact_run_emits_a_facts_only_pr_and_records_facts_from_the_matrix(
    tmp_path: Path,
) -> None:
    """The wholesale no-artifact case end to end at the CLI layer: an empty
    status dir plus the plan matrix makes every queued cell `uncovered`, so
    `collect-plan` emits a facts-only PR (no ready, no partial, no `Closes #`)
    and `record-cell-failures` still materializes one fact per cell — exactly
    what the composite's matrix-derived run id feeds when no cell uploaded."""
    empty_status_dir = tmp_path / "cells"  # no status.json under it
    empty_status_dir.mkdir()
    plan_json = runner.invoke(
        app,
        [
            "collect-plan",
            "--role",
            "predict",
            "--run-id",
            "R",
            "--status-dir",
            str(empty_status_dir),
            "--issue",
            "788",
            "--matrix-file",
            str(_matrix(tmp_path, "claude-baseline", "gemini-baseline")),
        ],
    )
    assert plan_json.exit_code == 0
    plan = json.loads(plan_json.stdout)
    assert plan["ready"] is None and plan["partial"] is None
    assert plan["facts_only"]["branch"] == "predict/run-R-facts"
    assert plan["facts_only"]["draft"] is False
    assert "Closes #788" not in plan["facts_only"]["body"]
    assert [f["error_class"] for f in plan["cell_failures"]] == ["died", "died"]

    plan_file = tmp_path / "plan.json"
    plan_file.write_text(plan_json.stdout)
    data_root = tmp_path / "data"
    assert (
        runner.invoke(
            app,
            ["record-cell-failures", "--plan-file", str(plan_file), "--data-root", str(data_root)],
        ).exit_code
        == 0
    )
    facts = list(data_root.glob("cases/scotus/1/events/evt-x/predictions/*/R/attempt.json"))
    assert {f.parent.parent.name for f in facts} == {"claude-baseline", "gemini-baseline"}
