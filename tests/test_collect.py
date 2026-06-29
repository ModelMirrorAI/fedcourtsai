"""The auto-merge guardrail and per-run PR aggregation (:mod:`fedcourtsai.collect`).

These lock the two controls that make a no-human-review auto-merge safe: the
``data/`` path jail (only additions, only under data/, only this run) and the
ready-vs-draft partition that keeps a failed cell out of the auto-merging PR.
"""

from __future__ import annotations

import pytest

from fedcourtsai.collect import (
    CellStatus,
    PathJailError,
    assert_within_jail,
    collect_plan,
    parse_name_status,
)
from fedcourtsai.finalize import FinalizeRole


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


def test_failed_cell_routed_to_draft_not_ready() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[
            _cell("claude-baseline"),
            _cell("codex-baseline", validated=False),
            _cell("gemini-baseline", produced=False),
        ],
    )
    assert plan.ready is not None
    assert plan.ready.artifact_dirs == ("cell-claude-baseline-1",)
    assert plan.partial is not None
    assert plan.partial.draft is True
    assert plan.partial.branch == "predict/run-R-partial"
    assert set(plan.partial.artifact_dirs) == {"cell-codex-baseline-1", "cell-gemini-baseline-1"}
    # The ready PR points the reader at the companion draft.
    assert "companion draft PR" in plan.ready.body
    # The draft body explains why each cell landed there.
    assert "failed validation" in plan.partial.body
    assert "no output" in plan.partial.body


def test_all_partial_opens_only_draft() -> None:
    plan = collect_plan(
        FinalizeRole.predict,
        run_id="R",
        cells=[_cell("claude-baseline", agent_ok=False)],
    )
    assert plan.ready is None
    assert plan.partial is not None
    assert "agent stopped early" in plan.partial.body


def test_no_cells_opens_nothing() -> None:
    plan = collect_plan(FinalizeRole.predict, run_id="R", cells=[])
    assert plan.ready is None and plan.partial is None


def test_reconcile_role_unsupported_for_now() -> None:
    with pytest.raises(ValueError, match="predict/evaluate"):
        collect_plan(FinalizeRole.reconcile, run_id="R", cells=[])
