"""Workflow finalize decisions (:mod:`fedcourtsai.finalize`).

The branch name, the draft-vs-ready routing, and the PR prose used to be inline
workflow bash; these lock the decisions the ``finalize-branch`` / ``finalize-pr``
commands now own. The branch-name cases in particular guard the production bug
where omitting the case from the ref collided two concurrent cells.
"""

from __future__ import annotations

import pytest

from fedcourtsai.finalize import (
    FinalizePlan,
    FinalizeRole,
    branch_name,
    finalize_judgment,
    finalize_reconcile,
)


def test_judgment_branch_carries_case_event_actor_and_run() -> None:
    # The case + event + actor must all ride in the ref so two cells sharing a
    # second-granular run id never collide (the #210 regression).
    branch = branch_name(
        FinalizeRole.predict,
        "ca9",
        123,
        "20260628T000000Z",
        event="evt-motion-x",
        actor="claude-baseline",
    )
    assert branch == "predict/ca9-123-evt-motion-x-claude-baseline-20260628T000000Z"


def test_two_dockets_same_run_id_get_distinct_branches() -> None:
    common = dict(run_id="R", event="evt-motion-x", actor="claude-baseline")
    a = branch_name(FinalizeRole.predict, "ca9", 1, **common)
    b = branch_name(FinalizeRole.predict, "ca9", 2, **common)
    assert a != b


def test_evaluate_branch_uses_its_role_prefix() -> None:
    branch = branch_name(
        FinalizeRole.evaluate, "ca9", 5, "R", event="evt-motion-x", actor="judge-panel"
    )
    assert branch.startswith("evaluate/")


def test_reconcile_branch_omits_event_and_actor() -> None:
    assert branch_name(FinalizeRole.reconcile, "ca9", 7, "R") == "reconcile/ca9-7-R"


def test_judgment_branch_requires_event_and_actor() -> None:
    with pytest.raises(ValueError):
        branch_name(FinalizeRole.predict, "ca9", 1, "R")


def _judgment(**over: object) -> FinalizePlan:
    base = dict(
        court="ca9",
        docket=123,
        event="evt-motion-x",
        actor="claude-baseline",
        run_id="R",
        changed=True,
        agent_ok=True,
        validated=True,
    )
    base.update(over)
    return finalize_judgment(FinalizeRole.predict, **base)  # type: ignore[arg-type]


def test_no_changes_skips() -> None:
    plan = _judgment(changed=False)
    assert plan.action == "skip"
    assert "produced no changes" in plan.message
    assert "skipping PR" in plan.message


def test_no_changes_after_limit_notes_the_limit() -> None:
    plan = _judgment(changed=False, agent_ok=False)
    assert "before the run hit its turn/time limit" in plan.message


def test_clean_valid_run_opens_ready_pr() -> None:
    plan = _judgment()
    assert plan.action == "open"
    assert plan.draft is False
    assert plan.commit_message == "predict(claude-baseline): ca9/123 evt-motion-x"
    assert plan.title == "predict(claude-baseline): ca9/123 — evt-motion-x"
    assert plan.body == (
        "Automated prediction by `claude-baseline` (run `R`) for event `evt-motion-x`."
    )


def test_clean_invalid_run_is_a_hard_fail() -> None:
    plan = _judgment(validated=False)
    assert plan.action == "fail"
    assert "failed schema validation" in plan.message


def test_unfinished_valid_run_opens_a_draft() -> None:
    plan = _judgment(agent_ok=False)
    assert plan.action == "open"
    assert plan.draft is True
    assert "did not finish" in plan.body


def test_unfinished_invalid_run_opens_a_draft_not_a_fail() -> None:
    # A partial write that fails validation is kept as a draft, never a hard fail.
    plan = _judgment(agent_ok=False, validated=False)
    assert plan.action == "open"
    assert plan.draft is True


def test_evaluate_uses_evaluation_noun() -> None:
    plan = finalize_judgment(
        FinalizeRole.evaluate,
        court="ca9",
        docket=1,
        event="e",
        actor="judge-panel",
        run_id="R",
        changed=True,
        agent_ok=True,
        validated=True,
    )
    assert plan.commit_message.startswith("evaluate(judge-panel):")
    assert plan.body.startswith("Automated evaluation by `judge-panel`")


def test_finalize_judgment_rejects_reconcile_role() -> None:
    with pytest.raises(ValueError):
        finalize_judgment(
            FinalizeRole.reconcile,
            court="ca9",
            docket=1,
            event="e",
            actor="a",
            run_id="R",
            changed=True,
            agent_ok=True,
            validated=True,
        )


def _reconcile(**over: object) -> FinalizePlan:
    base = dict(
        court="ca9",
        docket=123,
        run_id="R",
        settled=("evt-a", "evt-b"),
        agent_ok=True,
        validated=True,
        issue=42,
    )
    base.update(over)
    return finalize_reconcile(**base)  # type: ignore[arg-type]


def test_reconcile_no_settled_events_skips() -> None:
    plan = _reconcile(settled=())
    assert plan.action == "skip"
    assert "no outcome recorded for ca9/123" in plan.message
    assert "nothing to reconcile" in plan.message


def test_reconcile_open_lists_settled_events_and_closes_issue() -> None:
    plan = _reconcile()
    assert plan.action == "open"
    assert plan.draft is False
    assert plan.commit_message == "reconcile: ca9/123 — evt-a,evt-b"
    assert plan.title == "reconcile: ca9/123"
    assert "(evt-a,evt-b)" in plan.body
    assert "Closes #42" in plan.body


def test_reconcile_clean_invalid_is_a_hard_fail() -> None:
    plan = _reconcile(validated=False)
    assert plan.action == "fail"
    assert "failed schema validation" in plan.message


def test_reconcile_unfinished_opens_a_draft_with_before_merging_note() -> None:
    plan = _reconcile(agent_ok=False)
    assert plan.draft is True
    assert "before merging" in plan.body
