"""The predict round's auto-release and drain decision."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.collect import AUTO_RELEASED_MARKER
from fedcourtsai.review_hold import (
    ReviewHoldConfig,
    count_auto_released,
    decide,
    load_review_hold_config,
    released_last_day,
    render_summary,
)

ON = ReviewHoldConfig(auto_release_usd_per_round=45.0, auto_release_rounds_per_day=4)
ENGINES = ("claude-code", "codex", "gemini")


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


def _matrix(cells: int = 3, *, engine: str | None = None) -> dict[str, Any]:
    """A `predict-matrix` document: one include entry per cell, with its engine."""
    return {
        "include": [
            {"predictor_id": f"p{n}", "engine": engine or ENGINES[n % 3]} for n in range(cells)
        ]
    }


# --- auto-release ------------------------------------------------------------


def test_a_round_under_both_caps_is_released() -> None:
    decision = decide(_plan(spend=40.0), ON, released_last_day=1, matrix=_matrix())
    assert decision.auto_release
    assert "round 2 of 4" in decision.auto_release_reason
    assert (decision.plan_cells, decision.matrix_cells) == (3, 3)


def test_a_round_at_the_per_round_cap_is_released() -> None:
    assert decide(_plan(spend=45.0), ON, released_last_day=0, matrix=_matrix()).auto_release


def test_a_round_over_the_per_round_cap_is_held() -> None:
    decision = decide(_plan(spend=45.01), ON, released_last_day=0, matrix=_matrix())
    assert not decision.auto_release
    assert "over the per-round cap" in decision.auto_release_reason


def test_the_daily_cap_holds_the_next_round() -> None:
    decision = decide(_plan(), ON, released_last_day=4, matrix=_matrix())
    assert not decision.auto_release
    assert "daily cap 4" in decision.auto_release_reason


@pytest.mark.parametrize(
    "config",
    [
        ReviewHoldConfig(),
        ReviewHoldConfig(auto_release_usd_per_round=45.0),
        ReviewHoldConfig(auto_release_rounds_per_day=4),
    ],
)
def test_either_cap_at_zero_disables_auto_release(config: ReviewHoldConfig) -> None:
    decision = decide(_plan(), config, released_last_day=0, matrix=_matrix())
    assert not decision.auto_release
    assert "disabled" in decision.auto_release_reason


def test_an_unknown_daily_count_keeps_the_hold() -> None:
    decision = decide(_plan(), ON, released_last_day=None, matrix=_matrix())
    assert not decision.auto_release
    assert "could not be read" in decision.auto_release_reason


@pytest.mark.parametrize("spend", [None, True, "40", math.nan, math.inf, -1.0])
def test_a_plan_without_a_usable_estimate_keeps_the_hold(spend: object) -> None:
    plan = _plan()
    if spend is None:
        del plan["estimated_spend_usd"]
    else:
        plan["estimated_spend_usd"] = spend
    decision = decide(plan, ON, released_last_day=0, matrix=_matrix())
    assert not decision.auto_release
    assert decision.estimated_spend_usd is None


# --- what is priced is what runs ----------------------------------------------


def test_a_missing_matrix_keeps_the_hold() -> None:
    decision = decide(_plan(), ON, released_last_day=0, matrix=None)
    assert not decision.auto_release
    assert "matrix could not be read" in decision.auto_release_reason


@pytest.mark.parametrize("matrix_cells", [2, 4, 0])
def test_a_matrix_that_disagrees_with_the_plan_keeps_the_hold(matrix_cells: int) -> None:
    decision = decide(_plan(cells=3), ON, released_last_day=0, matrix=_matrix(matrix_cells))
    assert not decision.auto_release
    assert "price is not the price of what runs" in decision.auto_release_reason


def test_the_matrix_is_priced_and_the_larger_price_binds() -> None:
    # The plan claims $1 for ten cells; the matrix's ten claude cells price at
    # the planning rate ($4.27 each), so the round is priced at $42.70.
    decision = decide(
        _plan(spend=1.0, cells=10),
        ON,
        released_last_day=0,
        matrix=_matrix(10, engine="claude-code"),
    )
    assert decision.estimated_spend_usd == pytest.approx(42.7)
    assert decision.auto_release
    over = decide(
        _plan(spend=1.0, cells=11),
        ON,
        released_last_day=0,
        matrix=_matrix(11, engine="claude-code"),
    )
    assert not over.auto_release


def test_a_matrix_that_is_not_a_list_of_cells_keeps_the_hold() -> None:
    decision = decide(_plan(), ON, released_last_day=0, matrix={"include": "x"})
    assert not decision.auto_release
    assert decision.matrix_cells is None


# --- the daily count ----------------------------------------------------------


def test_auto_released_commits_are_counted_once_per_round() -> None:
    subjects = [
        f"predict(run 20261012T141200Z): 3 prediction(s) {AUTO_RELEASED_MARKER} (#2400)",
        f"predict(run 20261012T141200Z): 1 prediction(s) {AUTO_RELEASED_MARKER} (#2401)",
        f"predict(run 20261012T173600Z): 2 prediction(s) {AUTO_RELEASED_MARKER}",
        "predict(run 20261012T090000Z): 4 prediction(s) (#2399)",
        "pull: refresh corpus + outcomes (2026-10-12)",
        f"evaluate(run 20261012T150000Z): 3 evaluation(s) {AUTO_RELEASED_MARKER}",
    ]
    assert count_auto_released(subjects) == 2


def test_a_squash_that_takes_the_pr_title_is_counted_too() -> None:
    # A collect PR with more than one commit squashes under its title, which
    # puts the run id after the count rather than in the scope.
    subjects = [
        f"predict: 3 prediction(s) (run 20261012T141200Z) {AUTO_RELEASED_MARKER} (#2400)",
        f"predict(run 20261012T141200Z): 3 prediction(s) {AUTO_RELEASED_MARKER} (#2401)",
        f"predict: 2 prediction(s) (run 20261012T173600Z) {AUTO_RELEASED_MARKER}",
        "predict: 1 partial prediction(s) (run 20261012T190000Z) (#2402)",
        f"evaluate: 3 evaluation(s) (run 20261012T150000Z) {AUTO_RELEASED_MARKER}",
    ]
    assert count_auto_released(subjects) == 2


@pytest.mark.parametrize(
    ("deployments", "committed", "expected"),
    [(1, 3, 3), (3, 1, 3), (0, 0, 0), (None, 2, None), (2, None, None), (-1, 0, None)],
)
def test_the_stricter_count_binds_and_an_unread_source_holds(
    deployments: int | None, committed: int | None, expected: int | None
) -> None:
    assert released_last_day(deployments, committed) == expected


# --- drain -------------------------------------------------------------------


def test_a_cell_cap_deferral_asks_for_another_round() -> None:
    decision = decide(_plan(deferred=6), ON, released_last_day=0, matrix=_matrix())
    assert decision.drain_more
    assert "deferred 6" in decision.drain_reason


def test_a_reached_case_cap_asks_for_another_round() -> None:
    assert decide(_plan(cap_reached=True), ON, released_last_day=0, matrix=_matrix()).drain_more


@pytest.mark.parametrize("cap_reached", [False, None])
def test_a_round_no_cap_stopped_asks_for_nothing(cap_reached: bool | None) -> None:
    assert not decide(
        _plan(cap_reached=cap_reached), ON, released_last_day=0, matrix=_matrix()
    ).drain_more


def test_a_round_that_mints_nothing_never_chains() -> None:
    decision = decide(
        _plan(cells=0, deferred=5, cap_reached=True), ON, released_last_day=0, matrix=_matrix(0)
    )
    assert not decision.drain_more
    assert "mints nothing" in decision.drain_reason


def test_drain_is_independent_of_auto_release() -> None:
    held = decide(
        _plan(spend=999.0, deferred=2), ReviewHoldConfig(), released_last_day=None, matrix=None
    )
    assert not held.auto_release
    assert held.drain_more


def test_the_summary_says_what_the_round_does() -> None:
    released = render_summary(decide(_plan(), ON, released_last_day=0, matrix=_matrix()))
    assert "**Auto-released:**" in released
    held = render_summary(decide(_plan(deferred=2), ON, released_last_day=None, matrix=_matrix()))
    assert "**Waits on the review hold:**" in held
    assert "**Another round is owed:**" in held


# --- config ------------------------------------------------------------------


def test_the_config_defaults_to_disabled_when_the_file_is_absent(tmp_path: Path) -> None:
    assert load_review_hold_config(tmp_path) == ReviewHoldConfig()
    assert load_review_hold_config(tmp_path / "missing") == ReviewHoldConfig()


def test_the_config_refuses_a_non_finite_cap(tmp_path: Path) -> None:
    (tmp_path / "review-hold.yaml").write_text("auto_release_usd_per_round: .inf\n")
    with pytest.raises(ValidationError):
        load_review_hold_config(tmp_path)


def test_the_config_refuses_a_slipped_decimal(tmp_path: Path) -> None:
    (tmp_path / "review-hold.yaml").write_text("auto_release_usd_per_round: 500\n")
    with pytest.raises(ValidationError):
        load_review_hold_config(tmp_path)


def test_the_config_reads_its_own_file(tmp_path: Path) -> None:
    (tmp_path / "review-hold.yaml").write_text(
        "auto_release_usd_per_round: 25\nauto_release_rounds_per_day: 3\n"
    )
    assert load_review_hold_config(tmp_path) == ReviewHoldConfig(
        auto_release_usd_per_round=25.0, auto_release_rounds_per_day=3
    )


def test_the_tracking_file_no_longer_carries_the_caps(tmp_path: Path) -> None:
    # The caps are spend authority with their own owned file; a stray section in
    # tracking.yaml is not read.
    (tmp_path / "tracking.yaml").write_text(
        "review_hold:\n  auto_release_usd_per_round: 25\n  auto_release_rounds_per_day: 3\n"
    )
    assert load_review_hold_config(tmp_path) == ReviewHoldConfig()


def test_the_shipped_caps_are_off() -> None:
    root = Path(__file__).resolve().parents[1] / "config"
    assert load_review_hold_config(root) == ReviewHoldConfig()


# --- the command -------------------------------------------------------------

runner = CliRunner()


def _cmd_env(tmp_path: Path) -> dict[str, str]:
    config_root = tmp_path / "config"
    config_root.mkdir()
    (config_root / "review-hold.yaml").write_text(
        "auto_release_usd_per_round: 45\nauto_release_rounds_per_day: 4\n"
    )
    return {"FEDCOURTS_CONFIG_ROOT": str(config_root)}


def _files(tmp_path: Path, *, matrix_cells: int = 3) -> tuple[Path, Path]:
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps(_plan()))
    matrix = tmp_path / "matrix.json"
    matrix.write_text(json.dumps(_matrix(matrix_cells)))
    return plan, matrix


def test_the_command_prints_the_decision_and_appends_the_summary(tmp_path: Path) -> None:
    plan, matrix = _files(tmp_path)
    subjects = tmp_path / "subjects.txt"
    subjects.write_text(f"predict(run 20261012T141200Z): 3 prediction(s) {AUTO_RELEASED_MARKER}\n")
    summary = tmp_path / "summary.md"
    summary.write_text("# earlier\n")
    result = runner.invoke(
        app,
        [
            "hold-decision",
            "--plan-file",
            str(plan),
            "--matrix-file",
            str(matrix),
            "--deployments-released",
            "0",
            "--main-subjects-file",
            str(subjects),
            "--summary-file",
            str(summary),
        ],
        env=_cmd_env(tmp_path),
    )
    assert result.exit_code == 0, result.output
    decision = json.loads(result.stdout)
    assert decision["auto_release"] is True
    # The committed count (1) beat the deployment count (0).
    assert decision["released_last_day"] == 1
    assert summary.read_text().startswith("# earlier\n")
    assert "**Auto-released:**" in summary.read_text()


@pytest.mark.parametrize("omitted", ["--deployments-released", "--main-subjects-file"])
def test_the_command_holds_when_either_count_is_omitted(tmp_path: Path, omitted: str) -> None:
    plan, matrix = _files(tmp_path)
    subjects = tmp_path / "subjects.txt"
    subjects.write_text("")
    args = ["hold-decision", "--plan-file", str(plan), "--matrix-file", str(matrix)]
    if omitted != "--deployments-released":
        args += ["--deployments-released", "0"]
    if omitted != "--main-subjects-file":
        args += ["--main-subjects-file", str(subjects)]
    result = runner.invoke(app, args, env=_cmd_env(tmp_path))
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["auto_release"] is False


def test_the_command_holds_on_a_mismatched_matrix(tmp_path: Path) -> None:
    plan, matrix = _files(tmp_path, matrix_cells=5)
    subjects = tmp_path / "subjects.txt"
    subjects.write_text("")
    result = runner.invoke(
        app,
        [
            "hold-decision",
            "--plan-file",
            str(plan),
            "--matrix-file",
            str(matrix),
            "--deployments-released",
            "0",
            "--main-subjects-file",
            str(subjects),
        ],
        env=_cmd_env(tmp_path),
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["auto_release"] is False


def test_the_command_refuses_a_plan_that_is_not_an_object(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    plan.write_text("[]")
    result = runner.invoke(app, ["hold-decision", "--plan-file", str(plan)])
    assert result.exit_code == 1


def test_the_command_refuses_a_negative_count(tmp_path: Path) -> None:
    plan, _ = _files(tmp_path)
    result = runner.invoke(
        app, ["hold-decision", "--plan-file", str(plan), "--deployments-released", "-1"]
    )
    assert result.exit_code == 1
