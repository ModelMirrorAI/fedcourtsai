"""The auto-merge guardrail and per-run PR aggregation (:mod:`fedcourtsai.collect`).

These lock the two controls that make a no-human-review auto-merge safe: the
``data/`` path jail (only additions, only under data/, only this run) and the
ready-vs-draft partition that keeps a failed cell out of the auto-merging PR.
"""

from __future__ import annotations

import pytest

from fedcourtsai.collect import (
    CellStatus,
    ExpectedCell,
    PathJailError,
    assert_cleanup_within_jail,
    assert_within_jail,
    cell_artifact_name,
    cell_failures,
    collect_plan,
    feedback_marker,
    parse_name_status,
    render_feedback_comment,
    render_flags,
    render_stall_comment,
)
from fedcourtsai.finalize import FinalizeRole
from fedcourtsai.schemas import AgentFlag, AgentFlags, FlagCategory, FlagSeverity, UsageRole


def _flagset(actor: str, *flags: AgentFlag, case: str = "scotus/1") -> AgentFlags:
    return AgentFlags(
        case_id=case, run_id="R", role=UsageRole.predictor, actor_id=actor, flags=list(flags)
    )


def _cell(
    actor: str,
    *,
    produced: bool = True,
    validated: bool = True,
    agent_ok: bool = True,
    docket: int = 1,
    run_id: str = "R",
) -> CellStatus:
    return CellStatus(
        court="scotus",
        docket=docket,
        event_id="evt-petition-disposition",
        actor=actor,
        run_id=run_id,
        produced=produced,
        validated=validated,
        agent_ok=agent_ok,
        artifact_dir=f"cell-{actor}-{docket}",
    )


# --- path jail -------------------------------------------------------------


def test_additions_under_data_pass() -> None:
    changes = parse_name_status(
        "A\tdata/cases/scotus/1/events/e/predictions/claude-baseline/R/prediction.json\n"
        "A\tdata/cases/scotus/1/events/e/predictions/claude-baseline/R/reasoning.md\n"
    )
    assert_within_jail(changes)  # does not raise


def test_path_outside_data_is_rejected() -> None:
    changes = parse_name_status("A\tsrc/fedcourtsai/cli.py\n")
    with pytest.raises(PathJailError, match="outside the data/ jail"):
        assert_within_jail(changes)


@pytest.mark.parametrize("status", ["M", "D", "R100", "C", "T"])
def test_non_addition_is_rejected(status: str) -> None:
    # Modify/delete/rename/copy/type-change of an existing artifact is append-only
    # violation even when the path is under data/.
    changes = parse_name_status(f"{status}\tdata/cases/scotus/1/events/e/outcome.json\n")
    with pytest.raises(PathJailError, match="data PRs only add files"):
        assert_within_jail(changes)


# --- cleanup jail ----------------------------------------------------------


def test_cleanup_deletions_under_predictions_pass() -> None:
    changes = parse_name_status(
        "D\tdata/cases/scotus/1004191/events/evt-petition-disposition/predictions/codex-baseline/R/prediction.json\n"
        "D\tdata/cases/scotus/1004191/events/evt-petition-disposition/predictions/codex-baseline/R/reasoning.md\n"
    )
    assert_cleanup_within_jail(changes)  # does not raise


def test_cleanup_non_delete_is_rejected() -> None:
    # The sweep only ever removes; adding or editing is a violation.
    changes = parse_name_status(
        "A\tdata/cases/scotus/1/events/e/predictions/codex-baseline/R/prediction.json\n"
    )
    with pytest.raises(PathJailError, match="cleanup PRs only delete files"):
        assert_cleanup_within_jail(changes)


@pytest.mark.parametrize(
    "path",
    [
        # the outcome and the event definition sit beside predictions/, never inside it
        "data/cases/scotus/1/events/evt-petition-disposition/outcome.json",
        "data/cases/scotus/1/events/evt-petition-disposition/event.yaml",
        # a sibling artifact kind (evaluations) and code are both out of bounds
        "data/cases/scotus/1/events/evt-petition-disposition/evaluations/claude-judge/cb/R/evaluation.json",
        "src/fedcourtsai/cli.py",
    ],
)
def test_cleanup_delete_outside_predictions_is_rejected(path: str) -> None:
    changes = parse_name_status(f"D\t{path}\n")
    with pytest.raises(PathJailError, match=r"not under a data/cases/.*predictions/ subtree"):
        assert_cleanup_within_jail(changes)


def test_run_id_scope_blocks_other_runs() -> None:
    changes = parse_name_status(
        "A\tdata/cases/scotus/1/events/e/predictions/claude-baseline/OTHER/prediction.json\n"
    )
    with pytest.raises(PathJailError, match="not under run id 'R'"):
        assert_within_jail(changes, run_id="R")


def test_run_id_scope_allows_matching_run() -> None:
    changes = parse_name_status(
        "A\tdata/cases/scotus/1/events/e/predictions/claude-baseline/R/prediction.json\n"
    )
    assert_within_jail(changes, run_id="R")


def test_rename_keys_on_new_path() -> None:
    # `git diff --name-status` renames carry old\tnew; we read the new path and the
    # R status (a rename is still not a pure addition).
    changes = parse_name_status("R100\tdata/old.json\tsrc/new.py\n")
    assert changes == [type(changes[0])(status="R", path="src/new.py")]


# --- collect plan ----------------------------------------------------------


def test_all_ready_opens_one_ready_pr_no_draft() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline"), _cell("codex-baseline")],
    )
    assert plan.partial is None
    assert plan.ready is not None
    assert plan.ready.draft is False
    assert plan.ready.branch == "predict/run-R"
    assert plan.ready.artifact_dirs == ("cell-claude-baseline-1", "cell-codex-baseline-1")
    assert "2 prediction(s)" in plan.ready.title


def test_salvageable_cell_drafts_skipped_cell_only_warns() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[
            _cell("claude-baseline"),  # ready
            _cell("codex-baseline", validated=False),  # produced but invalid -> salvage
            _cell("gemini-baseline", produced=False),  # no output -> skipped, not committed
        ],
    )
    assert plan.ready is not None
    assert plan.ready.artifact_dirs == ("cell-claude-baseline-1",)
    # Only the cell that actually produced output is in the draft (committable).
    assert plan.partial is not None
    assert plan.partial.draft is True
    assert plan.partial.branch == "predict/run-R-partial"
    assert plan.partial.artifact_dirs == ("cell-codex-baseline-1",)
    assert "failed validation" in plan.partial.body
    # The no-output cell is reported for a warning, never committed.
    assert tuple(c.actor for c in plan.skipped if isinstance(c, CellStatus)) == ("gemini-baseline",)
    # The ready PR points the reader at the companion draft (salvage count only).
    assert "1 cell(s) need review" in plan.ready.body


def test_all_salvage_opens_only_draft() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline", agent_ok=False)],
    )
    assert plan.ready is None
    assert plan.partial is not None
    assert "agent stopped early" in plan.partial.body
    assert plan.skipped == ()


def test_only_skipped_opens_nothing_but_reports() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline", produced=False)],
    )
    assert plan.ready is None
    assert plan.partial is None
    assert tuple(c.actor for c in plan.skipped if isinstance(c, CellStatus)) == ("claude-baseline",)


def test_no_cells_opens_nothing() -> None:
    plan = collect_plan(FinalizeRole.predict, run_id="R", cells=[])
    assert plan.ready is None
    assert plan.partial is None
    assert plan.skipped == ()


def test_ready_pr_closes_trigger_issue_when_nothing_pending() -> None:
    plan = collect_plan(
        FinalizeRole.predict, run_id="R", cells=[_cell("claude-baseline")], issue=42
    )
    assert plan.ready is not None
    assert "Closes #42" in plan.ready.body


def test_ready_pr_keeps_issue_open_while_a_draft_remains() -> None:
    # A salvageable partial means unfinished work for the run, so the ready PR must
    # not close the trigger issue — the maintainer closes it after the draft.
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline"), _cell("codex-baseline", validated=False)],
        issue=42,
    )
    assert plan.ready is not None
    assert "Closes #42" not in plan.ready.body
    assert plan.partial is not None and "Closes #42" not in plan.partial.body


def test_fully_absent_engine_blocks_issue_close() -> None:
    # An engine at 0/N (e.g. quota) leaves no salvage draft, and the live queue
    # is transition-driven so the gap never re-queues — the ready PR must NOT
    # close the trigger issue, or a third of the board vanishes silently. The
    # issue stays open for a backfill, with the missing engine named.
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[
            _cell("claude-baseline"),
            _cell("gemini-baseline"),
            _cell("codex-baseline", produced=False),  # codex 0/1 -> absent
        ],
        issue=42,
    )
    assert plan.ready is not None
    assert plan.dead_actors == ("codex-baseline",)
    assert "Closes #42" not in plan.ready.body
    assert "codex-baseline" in plan.ready.body and "backfill" in plan.ready.body


def test_partial_engine_with_a_single_skip_still_closes() -> None:
    # An engine that produced some cells is not "absent": a single skipped cell
    # of a producing engine is a per-cell gap, not a missing engine, so it does
    # not hold the issue open (kept scoped to the whole-engine case #730 names).
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[
            _cell("codex-baseline", docket=1),  # codex produced here
            _cell("codex-baseline", docket=2, produced=False),  # ...skipped here
        ],
        issue=42,
    )
    assert plan.ready is not None
    assert plan.dead_actors == ()
    assert "Closes #42" in plan.ready.body


def test_render_flags_empty_is_blank() -> None:
    assert render_flags([]) == ""  # a run with no flag files renders nothing


def test_render_flags_orders_loudest_first() -> None:
    md = render_flags(
        [
            _flagset(
                "claude-baseline",
                AgentFlag(category=FlagCategory.scope, message="out of scope?"),
                AgentFlag(
                    category=FlagCategory.blocked,
                    severity=FlagSeverity.blocker,
                    message="no snapshot",
                ),
            )
        ]
    )
    assert "🚩 Agent flags (2)" in md
    # The blocker sorts above the info-level scope note regardless of input order.
    assert md.index("no snapshot") < md.index("out of scope?")
    assert "`claude-baseline`" in md


def test_render_flags_escapes_pipes_and_newlines() -> None:
    md = render_flags([_flagset("a", AgentFlag(category=FlagCategory.other, message="a | b\nc"))])
    # The message stays on one table row: newline collapsed, pipe escaped.
    assert "a \\| b c" in md
    assert "\nc |" not in md


def test_collect_plan_folds_flags_into_ready_body() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline")],
        flags=[
            _flagset("claude-baseline", AgentFlag(category=FlagCategory.data_quality, message="x"))
        ],
    )
    assert plan.ready is not None
    assert "🚩 Agent flags" in plan.ready.body
    assert "🚩 Agent flags" in plan.flags_markdown


def test_collect_plan_folds_flags_into_draft_when_no_ready() -> None:
    # A fully-blocked-but-salvageable run still surfaces its flags on the draft.
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline", agent_ok=False)],
        flags=[_flagset("claude-baseline", AgentFlag(category=FlagCategory.blocked, message="y"))],
    )
    assert plan.ready is None
    assert plan.partial is not None and "🚩 Agent flags" in plan.partial.body


def test_collect_plan_flags_survive_with_no_pr() -> None:
    # Every cell produced nothing -> no PR at all, but the roll-up still travels.
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline", produced=False)],
        flags=[_flagset("claude-baseline", AgentFlag(category=FlagCategory.blocked, message="z"))],
    )
    assert plan.ready is None and plan.partial is None
    assert "🚩 Agent flags" in plan.flags_markdown


# --- agent-feedback tracking issue ------------------------------------------


def test_render_feedback_comment_empty_when_no_flags() -> None:
    # No flags this run -> nothing to post to the latched issue.
    assert render_feedback_comment(FinalizeRole.predict, "R", "") == ""


def test_render_feedback_comment_leads_with_marker_and_header() -> None:
    comment = render_feedback_comment(
        FinalizeRole.evaluate, "20260101T000000Z", "## 🚩 Agent flags"
    )
    # First line is the dedupe marker keyed on role/run, so a re-run posts once.
    assert comment.splitlines()[0] == feedback_marker(FinalizeRole.evaluate, "20260101T000000Z")
    assert "evaluate · run `20260101T000000Z`" in comment
    assert comment.endswith("## 🚩 Agent flags")


def test_feedback_marker_distinguishes_role_and_run() -> None:
    # The marker keys on both stage and run so two stages of the same run, and two
    # runs of the same stage, never collide as "already posted".
    assert feedback_marker(FinalizeRole.predict, "R") != feedback_marker(FinalizeRole.evaluate, "R")
    assert feedback_marker(FinalizeRole.predict, "R1") != feedback_marker(
        FinalizeRole.predict, "R2"
    )


def test_collect_plan_carries_feedback_comment_with_flags() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline")],
        flags=[_flagset("claude-baseline", AgentFlag(category=FlagCategory.scope, message="q"))],
    )
    assert plan.feedback_comment.startswith(feedback_marker(FinalizeRole.predict, "R"))
    assert "🚩 Agent flags" in plan.feedback_comment


def test_collect_plan_feedback_comment_blank_without_flags() -> None:
    plan = collect_plan(FinalizeRole.predict, run_id="R", cells=[_cell("claude-baseline")])
    assert plan.feedback_comment == ""


def test_collect_plan_without_flags_leaves_body_clean() -> None:
    plan = collect_plan(FinalizeRole.predict, run_id="R", cells=[_cell("claude-baseline")])
    assert plan.flags_markdown == ""
    assert plan.ready is not None and "Agent flags" not in plan.ready.body


# --- stall detection (the infrastructure-failure signal) ---------------------


def test_stalled_when_every_cell_died_before_its_agent() -> None:
    # All cells: nothing produced AND the agent step failed — an infrastructure
    # stall (e.g. job-setup failures), not agents declining the work.
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[
            _cell("claude-baseline", produced=False, agent_ok=False),
            _cell("codex-baseline", produced=False, agent_ok=False),
        ],
    )
    assert plan.stalled is True
    assert plan.ready is None and plan.partial is None


def test_not_stalled_when_an_agent_finished_cleanly_without_output() -> None:
    # An agent that ran to completion and produced nothing is a content outcome,
    # not a stall.
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[
            _cell("claude-baseline", produced=False, agent_ok=True),
            _cell("codex-baseline", produced=False, agent_ok=True),
        ],
    )
    assert plan.stalled is False


def test_not_stalled_when_anything_was_produced() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[
            _cell("claude-baseline"),
            _cell("codex-baseline", produced=False, agent_ok=False),
        ],
    )
    assert plan.stalled is False
    # An empty run (no cells at all) is the workflow's zero-artifact branch, not
    # the plan's call — the plan reports it un-stalled.
    assert collect_plan(FinalizeRole.predict, run_id="R", cells=[]).stalled is False


def test_render_stall_comment_names_the_role_and_retry_path() -> None:
    comment = render_stall_comment(FinalizeRole.predict, "https://github.com/o/r/actions/runs/1")
    assert "produced no output" in comment
    assert "https://github.com/o/r/actions/runs/1" in comment
    assert "`run:predict`" in comment  # the re-fire instruction names the label


def test_the_plan_carries_the_judgment_noun_for_each_role() -> None:
    """The collect action renders its per-cell warnings from this, rather than
    re-deriving the role's vocabulary in shell where it could drift from the PR
    title and commit message `_JUDGMENT_NOUN` already names."""
    for role, noun in ((FinalizeRole.predict, "prediction"), (FinalizeRole.evaluate, "evaluation")):
        plan = collect_plan(role, run_id="R", cells=[_cell("claude-baseline")])
        assert plan.noun == noun
        # Same source as the human-facing PR text, so the two cannot disagree.
        assert plan.ready is not None
        assert noun in plan.ready.title


def test_a_transfer_lost_artifact_withholds_the_issue_close() -> None:
    """The sharpest edge of per-artifact download: a lost artifact leaves no
    status.json, so it is invisible to the cell census. Without naming it, a
    partial transfer failure would auto-merge a PR presenting itself as the whole
    run while quietly omitting cells — a loud total loss turned into a quiet
    partial one."""
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline"), _cell("codex-baseline")],
        issue=42,
        missing_artifacts=["predict-gemini-baseline-scotus-1-evt-x"],
    )
    assert plan.ready is not None
    # Every collected cell was ready, so nothing else would have held the issue.
    assert plan.partial is None and not plan.dead_actors
    assert "Closes #42" not in plan.ready.body, "a lost cell must keep the issue open"
    assert "predict-gemini-baseline-scotus-1-evt-x" in plan.ready.body, "name the lost cell"
    assert "re-run the `collect` job" in plan.ready.body, "point at the recovery path"
    assert plan.missing_artifacts == ("predict-gemini-baseline-scotus-1-evt-x",)


def test_a_fully_collected_run_still_closes_its_issue() -> None:
    """The counterpart: the new gate must not make every run hold its issue."""
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline")],
        issue=42,
        missing_artifacts=[],
    )
    assert plan.ready is not None
    assert "Closes #42" in plan.ready.body


def _expected(actor: str, event_id: str = "evt-petition-disposition") -> ExpectedCell:
    """Mirrors `_cell`'s identity so an expected cell can match an observed one."""
    return ExpectedCell(actor=actor, court="scotus", docket=1, event_id=event_id)


def test_a_queued_cell_that_uploaded_nothing_is_named_and_holds_the_issue() -> None:
    """The last invisible gap: a cell that dies before its upload leaves no
    status.json AND no artifact, so neither the census nor the transfer-loss
    list can see it. Only the plan's matrix knows it was ever queued."""
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline")],
        issue=42,
        expected=[_expected("claude-baseline"), _expected("gemini-baseline")],
    )
    assert plan.ready is not None
    assert plan.uncovered_cells == (_expected("gemini-baseline"),)
    assert "Closes #42" not in plan.ready.body
    assert "gemini-baseline" in plan.ready.body
    assert "need a re-queue" in plan.ready.body, (
        "name the remedy, which differs from a lost artifact"
    )


def test_a_transfer_lost_cell_is_not_also_counted_as_never_uploaded() -> None:
    """Both gaps are 'absent from the census', but the remedies differ — re-run
    collect vs re-queue. Reporting one cell as both would misdirect the fix."""
    lost = _expected("gemini-baseline")
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline")],
        issue=42,
        expected=[_expected("claude-baseline"), lost],
        missing_artifacts=[cell_artifact_name(FinalizeRole.predict, lost)],
    )
    assert plan.uncovered_cells == (), "a transfer-lost cell is already accounted for"
    assert plan.missing_artifacts == ("predict-gemini-baseline-scotus-1-evt-petition-disposition",)
    assert plan.ready is not None
    assert "re-run the `collect` job" in plan.ready.body
    assert "need a re-queue" not in plan.ready.body


def test_without_a_matrix_the_plan_behaves_exactly_as_before() -> None:
    """`expected=()` must be a no-op, so the census is landable independently of
    the workflow change that supplies it."""
    plan = collect_plan(
        FinalizeRole.predict, run_id="R", cells=[_cell("claude-baseline")], issue=42
    )
    assert plan.uncovered_cells == ()
    assert plan.ready is not None
    assert "Closes #42" in plan.ready.body


def test_expected_cell_parses_both_predictor_and_evaluator_matrices() -> None:
    base = {"court": "scotus", "docket": 1, "event_id": "evt-x"}
    assert ExpectedCell.from_matrix_entry({**base, "predictor_id": "p"}).actor == "p"
    assert ExpectedCell.from_matrix_entry({**base, "evaluator_id": "e"}).actor == "e"
    with pytest.raises(ValueError, match="neither predictor_id nor evaluator_id"):
        ExpectedCell.from_matrix_entry(base)


# --- cell failure facts (the attempt-recording seam) -----------------------


def _expected_docket(actor: str, docket: int) -> ExpectedCell:
    return ExpectedCell(
        actor=actor, court="scotus", docket=docket, event_id="evt-petition-disposition"
    )


def test_cell_failures_one_fact_per_failed_cell_with_coarse_class() -> None:
    # One fact per truly-failed cell: skipped -> no_output, salvage -> partial,
    # uncovered -> died. A ready cell yields nothing. The actor also has a ready
    # cell (docket 1), so it is not a dead engine and no `quota` override applies.
    plan = collect_plan(
        FinalizeRole.evaluate,
        run_id="R",
        cells=[
            _cell("claude-judge", docket=1),  # ready -> no fact
            _cell("claude-judge", docket=2, produced=False),  # skipped -> no_output
            _cell("claude-judge", docket=3, validated=False),  # salvage -> partial
        ],
        expected=[_expected_docket("claude-judge", d) for d in (1, 2, 3, 4)],  # 4 died
    )
    facts = cell_failures(plan, run_id="R", role=FinalizeRole.evaluate)
    assert {f.docket: f.error_class for f in facts} == {2: "no_output", 3: "partial", 4: "died"}
    assert all(
        f.seam == "evaluate" and f.run_id == "R" and f.actor == "claude-judge" for f in facts
    )


def test_cell_failures_quota_class_for_dead_actor_and_excludes_lost() -> None:
    # A dead engine (0 produced) has its failed cells promoted to `quota`. A cell
    # whose artifact merely failed to transfer (missing_artifacts) is re-collectable,
    # not a cell failure, so it yields NO fact.
    lost = _expected_docket("claude-baseline", 9)
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[
            _cell("claude-baseline", docket=1),  # ready -> claude alive
            _cell("gemini-baseline", docket=1, produced=False),  # gemini 0 produced -> dead
        ],
        missing_artifacts=[cell_artifact_name(FinalizeRole.predict, lost)],
        expected=[lost],  # matched by missing_artifacts -> lost, not uncovered
    )
    assert plan.dead_actors == ("gemini-baseline",)
    facts = cell_failures(plan, run_id="R", role=FinalizeRole.predict)
    assert {(f.actor, f.error_class) for f in facts} == {("gemini-baseline", "quota")}


def test_cell_failures_empty_when_run_is_clean() -> None:
    plan = collect_plan(FinalizeRole.predict, run_id="R", cells=[_cell("claude-baseline")])
    assert cell_failures(plan, run_id="R", role=FinalizeRole.predict) == []
