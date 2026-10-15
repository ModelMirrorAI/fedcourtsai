"""collect treats a pre-mint-poll refusal as a designed refusal, and keeps a durable record."""

from dataclasses import replace

from fedcourtsai.collect import (
    CellStatus,
    PreMintRefusal,
    cell_failures,
    collect_plan,
    render_feedback_comment,
)
from fedcourtsai.finalize import FinalizeRole
from tests.test_collect import _cell

_REFUSAL = PreMintRefusal(
    polled_at="2026-10-14T18:20:00Z",
    reason="snapshot entry reads as an interim disposal: 'Application denied as moot.'",
)


def _refused(actor: str, docket: int = 2) -> CellStatus:
    return replace(
        _cell(actor, produced=False, validated=False, agent_ok=False, docket=docket),
        pre_mint_refusal=_REFUSAL,
    )


def test_a_status_json_refusal_reads_back() -> None:
    status = CellStatus.from_dict(
        {
            "court": "scotus",
            "docket": 2,
            "event_id": "evt-motion-disposition",
            "actor": "gemini-baseline",
            "run_id": "R",
            "produced": False,
            "validated": False,
            "agent_ok": False,
            "pre_mint_refusal": {"polled_at": _REFUSAL.polled_at, "reason": _REFUSAL.reason},
        },
        artifact_dir="cell",
    )
    assert status.pre_mint_refusal == _REFUSAL
    plain = CellStatus.from_dict(
        {
            "court": "scotus",
            "docket": 2,
            "event_id": "e",
            "actor": "a",
            "run_id": "R",
            "produced": False,
            "validated": False,
            "agent_ok": False,
        },
        artifact_dir="cell",
    )
    assert plain.pre_mint_refusal is None


def test_a_refused_cell_is_not_a_no_output_failure_or_a_missing_engine() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline"), _refused("gemini-baseline")],
    )

    assert plan.skipped == ()
    assert plan.dead_actors == ()
    assert cell_failures(plan, run_id="R", role=FinalizeRole.predict) == []
    assert [c.actor for c in plan.pre_mint_refusals] == ["gemini-baseline"]


def test_the_refusal_roll_up_rides_the_pr_body_and_the_feedback_comment() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline"), _refused("gemini-baseline"), _refused("codex-baseline")],
    )

    assert plan.ready is not None
    assert "Pre-mint refusals (2)" in plan.ready.body
    assert "`codex-baseline` 1, `gemini-baseline` 1" in plan.pre_mint_refusals_markdown
    assert _REFUSAL.polled_at in plan.pre_mint_refusals_markdown
    assert "Pre-mint refusals (2)" in plan.feedback_comment


def test_a_round_whose_every_cell_was_refused_still_leaves_a_record() -> None:
    plan = collect_plan(FinalizeRole.predict, run_id="R", cells=[_refused("gemini-baseline")])

    # No PR opens and nothing stalled, but the issue comment carries the refusal.
    assert plan.ready is None
    assert plan.partial is None
    assert not plan.stalled
    assert "Pre-mint refusals (1)" in plan.feedback_comment


def test_no_refusals_and_no_flags_posts_no_comment() -> None:
    assert render_feedback_comment(FinalizeRole.predict, "R", "", "") == ""


def test_a_refusal_whose_poll_time_is_not_a_timestamp_reads_as_malformed() -> None:
    for polled_at in ("| injected | row |", "", "yesterday", 7, None):
        assert (
            PreMintRefusal.from_status({"polled_at": polled_at, "reason": _REFUSAL.reason}) is None
        )
    assert PreMintRefusal.from_status({"polled_at": _REFUSAL.polled_at, "reason": "r"})
