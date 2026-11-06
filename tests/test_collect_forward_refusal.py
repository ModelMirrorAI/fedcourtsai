"""collect treats a resolved-event forward refusal as a designed refusal, and keeps a record."""

from dataclasses import replace

import pytest

from fedcourtsai.collect import (
    FORWARD_REFUSAL_GATES,
    CellStatus,
    ForwardRefusal,
    cell_failures,
    collect_plan,
    render_feedback_comment,
)
from fedcourtsai.finalize import FinalizeRole
from tests.test_collect import _cell

_POLL = ForwardRefusal(
    gate="poll",
    at="2026-10-14T18:20:00Z",
    reason="snapshot entry reads as an interim disposal: 'Application denied as moot.'",
)
_RECORD = ForwardRefusal(
    gate="record",
    at="2026-11-05T21:02:11Z",
    reason="the corpus records evt-brief-response-disposition resolved",
)


def _refused(actor: str, refusal: ForwardRefusal = _POLL, docket: int = 2) -> CellStatus:
    return replace(
        _cell(actor, produced=False, validated=False, agent_ok=False, docket=docket),
        forward_refusal=refusal,
    )


def _status(**extra: object) -> dict[str, object]:
    return {
        "court": "scotus",
        "docket": 2,
        "event_id": "evt-motion-disposition",
        "actor": "gemini-baseline",
        "run_id": "R",
        "produced": False,
        "validated": False,
        "agent_ok": False,
        **extra,
    }


@pytest.mark.parametrize("refusal", [_POLL, _RECORD])
def test_a_status_json_refusal_reads_back(refusal: ForwardRefusal) -> None:
    status = CellStatus.from_dict(_status(forward_refusal=refusal.as_record()), artifact_dir="cell")
    assert status.forward_refusal == refusal
    plain = CellStatus.from_dict(_status(), artifact_dir="cell")
    assert plain.forward_refusal is None
    null = CellStatus.from_dict(_status(forward_refusal=None), artifact_dir="cell")
    assert null.forward_refusal is None


@pytest.mark.parametrize("refusal", [_POLL, _RECORD])
def test_a_refused_cell_is_not_a_no_output_failure_or_a_missing_engine(
    refusal: ForwardRefusal,
) -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline"), _refused("gemini-baseline", refusal)],
    )

    assert plan.skipped == ()
    assert plan.dead_actors == ()
    assert cell_failures(plan, run_id="R", role=FinalizeRole.predict) == []
    assert [c.actor for c in plan.forward_refusals] == ["gemini-baseline"]


def test_a_cell_every_engine_saw_resolved_in_the_corpus_writes_no_failure_fact() -> None:
    # The run that left three no_output attempts on one cell: every engine's
    # provisioning found the corpus already recording the event resolved.
    engines = ("claude-baseline", "codex-baseline", "gemini-baseline")
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_refused(a, _RECORD, docket=9526000634) for a in engines],
    )

    assert cell_failures(plan, run_id="R", role=FinalizeRole.predict) == []
    assert plan.facts_only is None or "9526000634" not in plan.facts_only.body
    assert not plan.stalled
    assert plan.dead_actors == ()
    assert "Forward-gate refusals (3)" in plan.feedback_comment
    assert "| record |" in plan.forward_refusals_markdown


def test_the_refusal_roll_up_rides_the_pr_body_and_the_feedback_comment() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[
            _cell("claude-baseline"),
            _refused("gemini-baseline"),
            _refused("codex-baseline", _RECORD),
        ],
    )

    assert plan.ready is not None
    assert "Forward-gate refusals (2)" in plan.ready.body
    assert "`codex-baseline` 1, `gemini-baseline` 1" in plan.forward_refusals_markdown
    assert _POLL.at in plan.forward_refusals_markdown
    assert "| poll |" in plan.forward_refusals_markdown
    assert "| record |" in plan.forward_refusals_markdown
    assert "Forward-gate refusals (2)" in plan.feedback_comment


def test_a_round_whose_every_cell_was_refused_still_leaves_a_record() -> None:
    plan = collect_plan(FinalizeRole.predict, run_id="R", cells=[_refused("gemini-baseline")])

    # No PR opens and nothing stalled, but the issue comment carries the refusal.
    assert plan.ready is None
    assert plan.partial is None
    assert not plan.stalled
    assert "Forward-gate refusals (1)" in plan.feedback_comment


def test_no_refusals_and_no_flags_posts_no_comment() -> None:
    assert render_feedback_comment(FinalizeRole.predict, "R", "", "") == ""


def test_a_refusal_whose_time_is_not_a_timestamp_reads_as_malformed() -> None:
    for at in ("| injected | row |", "", "yesterday", 7, None):
        assert ForwardRefusal.from_status({"gate": "poll", "at": at, "reason": "r"}) is None
    assert ForwardRefusal.from_status({"gate": "poll", "at": _POLL.at, "reason": "r"})


def test_a_refusal_from_an_unknown_gate_reads_as_malformed() -> None:
    # Only a gate that means "already resolved" exempts a cell: the staleness
    # bound, or any name nobody registered, stays an ordinary no-output cell.
    assert "stale" not in FORWARD_REFUSAL_GATES
    for gate in ("stale", "", None, "| poll |"):
        assert ForwardRefusal.from_status({"gate": gate, "at": _POLL.at, "reason": "r"}) is None
