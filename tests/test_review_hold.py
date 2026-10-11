"""The predict round's auto-release and drain decision."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.config import ReviewHoldConfig, load_review_hold_config
from fedcourtsai.review_hold import decide

ON = ReviewHoldConfig(auto_release_usd_per_round=100.0, auto_release_rounds_per_day=4)


def _plan(
    *,
    spend: float | None = 40.0,
    cells: int = 3,
    deferred: int = 0,
    cap_reached: bool | None = False,
) -> dict[str, Any]:
    """A `predict-plan` document in its real shape: the cell count lives in
    `counts.cell_ledger`, the case cap in `counts.case_reconciliation`
    (``None`` when the cases were named)."""
    plan: dict[str, Any] = {
        "would_mint": [{"cell": n} for n in range(cells)],
        "counts": {
            "provenance": {},
            "cell_ledger": {"deferred_by_cap_cells": deferred, "would_mint_cells": cells},
            "case_reconciliation": (None if cap_reached is None else {"cap_reached": cap_reached}),
        },
    }
    if spend is not None:
        plan["estimated_spend_usd"] = spend
    return plan


# --- auto-release ------------------------------------------------------------


def test_a_round_under_both_caps_is_released() -> None:
    decision = decide(_plan(spend=40.0), ON, released_last_day=1)
    assert decision.auto_release
    assert "round 2 of 4" in decision.auto_release_reason


def test_a_round_at_the_per_round_cap_is_released() -> None:
    assert decide(_plan(spend=100.0), ON, released_last_day=0).auto_release


def test_a_round_over_the_per_round_cap_is_held() -> None:
    decision = decide(_plan(spend=100.01), ON, released_last_day=0)
    assert not decision.auto_release
    assert "over the per-round cap" in decision.auto_release_reason


def test_the_daily_cap_holds_the_next_round() -> None:
    decision = decide(_plan(spend=1.0), ON, released_last_day=4)
    assert not decision.auto_release
    assert "daily cap 4" in decision.auto_release_reason


@pytest.mark.parametrize(
    "config",
    [
        ReviewHoldConfig(),
        ReviewHoldConfig(auto_release_usd_per_round=100.0),
        ReviewHoldConfig(auto_release_rounds_per_day=4),
    ],
)
def test_either_cap_at_zero_disables_auto_release(config: ReviewHoldConfig) -> None:
    decision = decide(_plan(spend=0.0), config, released_last_day=0)
    assert not decision.auto_release
    assert "disabled" in decision.auto_release_reason


def test_an_unknown_daily_count_keeps_the_hold() -> None:
    # Fail closed: a count the workflow could not read is not a count of zero.
    decision = decide(_plan(spend=1.0), ON, released_last_day=None)
    assert not decision.auto_release
    assert "could not be read" in decision.auto_release_reason


@pytest.mark.parametrize("spend", [None, "12.0", True, math.nan, math.inf, -1.0])
def test_a_plan_without_a_usable_estimate_keeps_the_hold(spend: object) -> None:
    # A NaN compares as "not over" any cap, and a negative one is under all of
    # them, so each must read as no estimate rather than as a small one.
    plan = _plan(spend=None)
    if spend is not None:
        plan["estimated_spend_usd"] = spend
    decision = decide(plan, ON, released_last_day=0)
    assert not decision.auto_release
    assert decision.estimated_spend_usd is None


# --- drain -------------------------------------------------------------------


def test_a_cell_cap_deferral_asks_for_another_round() -> None:
    decision = decide(_plan(deferred=12), ON, released_last_day=0)
    assert decision.drain_more
    assert "deferred 12" in decision.drain_reason


def test_a_reached_case_cap_asks_for_another_round() -> None:
    assert decide(_plan(cap_reached=True), ON, released_last_day=0).drain_more


@pytest.mark.parametrize("cap_reached", [False, None])
def test_a_round_no_cap_stopped_asks_for_nothing(cap_reached: bool | None) -> None:
    assert not decide(_plan(cap_reached=cap_reached), ON, released_last_day=0).drain_more


def test_a_round_that_mints_nothing_never_chains() -> None:
    # An empty matrix — a drained backlog, or a guard withholding every cell —
    # must not keep dispatching rounds, whatever the cap fields say.
    decision = decide(_plan(cells=0, deferred=5, cap_reached=True), ON, released_last_day=0)
    assert not decision.drain_more


def test_drain_is_independent_of_auto_release() -> None:
    # A held round that a cap stopped short still asks for the next round; that
    # round renders its own plan and waits on its own hold.
    decision = decide(_plan(spend=500.0, deferred=3), ON, released_last_day=0)
    assert not decision.auto_release
    assert decision.drain_more


# --- config ------------------------------------------------------------------


def test_the_config_defaults_to_disabled_when_the_section_is_absent(tmp_path: Path) -> None:
    (tmp_path / "tracking.yaml").write_text("spend:\n  ceiling_usd: 10\n")
    assert load_review_hold_config(tmp_path) == ReviewHoldConfig()
    assert load_review_hold_config(tmp_path / "missing") == ReviewHoldConfig()


def test_the_config_refuses_a_non_finite_cap(tmp_path: Path) -> None:
    (tmp_path / "tracking.yaml").write_text("review_hold:\n  auto_release_usd_per_round: .inf\n")
    with pytest.raises(ValueError, match="finite"):
        load_review_hold_config(tmp_path)


def test_the_config_reads_its_section(tmp_path: Path) -> None:
    (tmp_path / "tracking.yaml").write_text(
        "review_hold:\n  auto_release_usd_per_round: 75\n  auto_release_rounds_per_day: 3\n"
    )
    assert load_review_hold_config(tmp_path) == ReviewHoldConfig(
        auto_release_usd_per_round=75.0, auto_release_rounds_per_day=3
    )


# --- the command -------------------------------------------------------------


def _run(tmp_path: Path, plan: object, *extra: str) -> Any:
    config_root = tmp_path / "config"
    config_root.mkdir()
    (config_root / "tracking.yaml").write_text(
        "review_hold:\n  auto_release_usd_per_round: 100\n  auto_release_rounds_per_day: 4\n"
    )
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(plan))
    return CliRunner().invoke(
        app,
        ["hold-decision", "--plan-file", str(plan_file), *extra],
        env={"FEDCOURTS_CONFIG_ROOT": str(config_root)},
    )


def test_the_command_prints_the_decision(tmp_path: Path) -> None:
    result = _run(tmp_path, _plan(spend=40.0, deferred=2), "--released-last-day", "0")
    assert result.exit_code == 0, result.output
    decision = json.loads(result.stdout)
    assert decision["auto_release"] is True
    assert decision["drain_more"] is True


def test_the_command_holds_when_the_count_is_omitted(tmp_path: Path) -> None:
    result = _run(tmp_path, _plan(spend=40.0))
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["auto_release"] is False


def test_the_command_refuses_a_plan_that_is_not_an_object(tmp_path: Path) -> None:
    result = _run(tmp_path, [1, 2])
    assert result.exit_code == 1


def test_the_command_refuses_a_negative_count(tmp_path: Path) -> None:
    result = _run(tmp_path, _plan(), "--released-last-day", "-1")
    assert result.exit_code == 1
