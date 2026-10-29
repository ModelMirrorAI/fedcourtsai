"""The review hold's auto-release decision for every spend lane, and predict's drain."""

from __future__ import annotations

import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.collect import AUTO_RELEASED_MARKER
from fedcourtsai.config import SpendConfig, load_spend_config
from fedcourtsai.review_hold import (
    HoldDecision,
    MeasuredSpend,
    ReviewHoldConfig,
    Seam,
    count_auto_released,
    decide,
    label_refusal,
    load_review_hold_config,
    measured_spend,
    released_last_day,
    render_summary,
)

ON = ReviewHoldConfig(
    auto_release_usd_per_round=45.0, auto_release_rounds_per_day=4, auto_release_budget_usd=1000.0
)
BACKSTOP = SpendConfig(ceiling_usd=4000.0, window_days=30)
LOW = MeasuredSpend(cells_usd=100.0, summaries_usd=5.0)
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


def _decide(
    plan: dict[str, Any],
    config: ReviewHoldConfig = ON,
    *,
    released_last_day: int | None,
    matrix: dict[str, Any] | None,
    seam: Seam = "predict",
    backstop: SpendConfig | None = BACKSTOP,
    measured: MeasuredSpend | None = LOW,
) -> HoldDecision:
    return decide(
        plan,
        config,
        seam=seam,
        released_last_day=released_last_day,
        matrix=matrix,
        backstop=backstop,
        measured=measured,
    )


# --- auto-release ------------------------------------------------------------


def test_a_round_under_both_caps_is_released() -> None:
    decision = _decide(_plan(spend=40.0), ON, released_last_day=1, matrix=_matrix())
    assert decision.auto_release
    assert "round 2 of 4" in decision.auto_release_reason
    assert (decision.plan_cells, decision.matrix_cells) == (3, 3)


def test_a_round_at_the_per_round_cap_is_released() -> None:
    assert _decide(_plan(spend=45.0), ON, released_last_day=0, matrix=_matrix()).auto_release


def test_a_round_over_the_per_round_cap_is_held() -> None:
    decision = _decide(_plan(spend=45.01), ON, released_last_day=0, matrix=_matrix())
    assert not decision.auto_release
    assert "over the per-round cap" in decision.auto_release_reason


def test_the_daily_cap_holds_the_next_round() -> None:
    decision = _decide(_plan(), ON, released_last_day=4, matrix=_matrix())
    assert not decision.auto_release
    assert "daily cap 4" in decision.auto_release_reason


@pytest.mark.parametrize(
    "config",
    [
        ReviewHoldConfig(),
        ReviewHoldConfig(auto_release_usd_per_round=45.0),
        ReviewHoldConfig(auto_release_rounds_per_day=4),
        ReviewHoldConfig(auto_release_budget_usd=1000.0),
        ReviewHoldConfig(auto_release_usd_per_round=45.0, auto_release_rounds_per_day=4),
    ],
)
def test_either_cap_at_zero_disables_auto_release(config: ReviewHoldConfig) -> None:
    decision = _decide(_plan(), config, released_last_day=0, matrix=_matrix())
    assert not decision.auto_release
    assert "disabled" in decision.auto_release_reason


def test_an_unknown_daily_count_keeps_the_hold() -> None:
    decision = _decide(_plan(), ON, released_last_day=None, matrix=_matrix())
    assert not decision.auto_release
    assert "could not be read" in decision.auto_release_reason


@pytest.mark.parametrize("spend", [None, True, "40", math.nan, math.inf, -1.0])
def test_a_plan_without_a_usable_estimate_keeps_the_hold(spend: object) -> None:
    plan = _plan()
    if spend is None:
        del plan["estimated_spend_usd"]
    else:
        plan["estimated_spend_usd"] = spend
    decision = _decide(plan, ON, released_last_day=0, matrix=_matrix())
    assert not decision.auto_release
    assert decision.estimated_spend_usd is None


# --- what is priced is what runs ----------------------------------------------


def test_a_missing_matrix_keeps_the_hold() -> None:
    decision = _decide(_plan(), ON, released_last_day=0, matrix=None)
    assert not decision.auto_release
    assert "matrix could not be read" in decision.auto_release_reason


@pytest.mark.parametrize("matrix_cells", [2, 4, 0])
def test_a_matrix_that_disagrees_with_the_plan_keeps_the_hold(matrix_cells: int) -> None:
    decision = _decide(_plan(cells=3), ON, released_last_day=0, matrix=_matrix(matrix_cells))
    assert not decision.auto_release
    assert "price is not the price of what runs" in decision.auto_release_reason


def test_the_matrix_is_priced_and_the_larger_price_binds() -> None:
    # The plan claims $1 for ten cells; the matrix's ten claude cells price at
    # the planning rate ($4.27 each), so the round is priced at $42.70.
    decision = _decide(
        _plan(spend=1.0, cells=10),
        ON,
        released_last_day=0,
        matrix=_matrix(10, engine="claude-code"),
    )
    assert decision.estimated_spend_usd == pytest.approx(42.7)
    assert decision.auto_release
    over = _decide(
        _plan(spend=1.0, cells=11),
        ON,
        released_last_day=0,
        matrix=_matrix(11, engine="claude-code"),
    )
    assert not over.auto_release


def test_a_matrix_that_is_not_a_list_of_cells_keeps_the_hold() -> None:
    decision = _decide(_plan(), ON, released_last_day=0, matrix={"include": "x"})
    assert not decision.auto_release
    assert decision.matrix_cells is None


# --- the daily count ----------------------------------------------------------


def test_auto_released_commits_are_counted_once_per_round_across_the_lanes() -> None:
    subjects = [
        f"predict(run 20261012T141200Z): 3 prediction(s) {AUTO_RELEASED_MARKER} (#2400)",
        f"predict(run 20261012T141200Z): 1 prediction(s) {AUTO_RELEASED_MARKER} (#2401)",
        f"predict(run 20261012T173600Z): 2 prediction(s) {AUTO_RELEASED_MARKER}",
        "predict(run 20261012T090000Z): 4 prediction(s) (#2399)",
        "pull: refresh corpus + outcomes (2026-10-12)",
        f"evaluate(run 20261012T150000Z): 3 evaluation(s) {AUTO_RELEASED_MARKER}",
        "evaluate(run 20261012T160000Z): 2 evaluation(s) (#2403)",
        "data(summaries): 7 plain-language case summaries (run 18812345678) "
        + AUTO_RELEASED_MARKER,
        "data(summaries): 2 plain-language case summaries (run 18812349999)",
    ]
    # Two predict rounds, one evaluate round, one summarize round.
    assert count_auto_released(subjects) == 4


def test_one_run_id_in_two_lanes_is_two_rounds() -> None:
    subjects = [
        f"predict(run 20261012T141200Z): 3 prediction(s) {AUTO_RELEASED_MARKER}",
        f"evaluate(run 20261012T141200Z): 3 evaluation(s) {AUTO_RELEASED_MARKER}",
    ]
    assert count_auto_released(subjects) == 2


def test_a_squash_that_takes_the_pr_title_is_counted_too() -> None:
    # A collect PR squashed under its title puts the run id after the count
    # rather than in the scope; `main`'s history keeps the squashes already on
    # it, and they stay inside the window's reach for as long as it looks back.
    subjects = [
        f"predict: 3 prediction(s) (run 20261012T141200Z) {AUTO_RELEASED_MARKER} (#2400)",
        f"predict(run 20261012T141200Z): 3 prediction(s) {AUTO_RELEASED_MARKER} (#2401)",
        f"predict: 2 prediction(s) (run 20261012T173600Z) {AUTO_RELEASED_MARKER}",
        "predict: 1 partial prediction(s) (run 20261012T190000Z) (#2402)",
        f"evaluate: 3 evaluation(s) (run 20261012T150000Z) {AUTO_RELEASED_MARKER}",
        f"evaluate(run 20261012T150000Z): 3 evaluation(s) {AUTO_RELEASED_MARKER}",
    ]
    assert count_auto_released(subjects) == 3


def test_merge_commit_history_counts_each_round_once_whichever_commit_is_in_the_window() -> None:
    # What the commits API returns for `main` once collect PRs land as merge
    # commits: every commit reachable from `main` whose committer date is in
    # the window, second parents included, newest first. The merge commit is
    # dated when the PR landed and the ready commit when it was built, never
    # later, so a PR that waited leaves the marked merge commit alone in the
    # window; a ready commit alone is what an unmarked merge subject leaves.
    # Either counts its round, and both together count it once.
    both = [
        f"predict: 3 prediction(s) (run 20261012T141200Z) {AUTO_RELEASED_MARKER} (#2400)",
        "live: refresh corpus + outcomes (2026-10-12)",
        f"predict(run 20261012T141200Z): 3 prediction(s) {AUTO_RELEASED_MARKER}",
    ]
    merge_only = [
        f"evaluate: 2 evaluation(s) (run 20261012T150000Z) {AUTO_RELEASED_MARKER} (#2401)"
    ]
    ready_only = [f"predict(run 20261012T173600Z): 1 prediction(s) {AUTO_RELEASED_MARKER}"]
    held = [
        "predict: 4 prediction(s) (run 20261012T090000Z) (#2399)",
        "predict(run 20261012T090000Z): 4 prediction(s)",
    ]
    assert count_auto_released(both) == 1
    assert count_auto_released(merge_only) == 1
    assert count_auto_released(ready_only) == 1
    assert count_auto_released(held) == 0
    assert count_auto_released(both + merge_only + ready_only + held) == 3


def test_the_platforms_own_merge_subject_carries_no_round() -> None:
    # A PR merged by hand under the default subject leaves only its ready
    # commit to carry the mark; the default subject itself never counts.
    subjects = [
        "Merge pull request #2400 from ModelMirrorAI/run/predict-20261012T141200Z",
        f"predict(run 20261012T141200Z): 3 prediction(s) {AUTO_RELEASED_MARKER}",
    ]
    assert count_auto_released(subjects[:1]) == 0
    assert count_auto_released(subjects) == 1


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
    decision = _decide(_plan(deferred=6), ON, released_last_day=0, matrix=_matrix())
    assert decision.drain_more
    assert "deferred 6" in decision.drain_reason


def test_a_reached_case_cap_asks_for_another_round() -> None:
    assert _decide(_plan(cap_reached=True), ON, released_last_day=0, matrix=_matrix()).drain_more


@pytest.mark.parametrize("cap_reached", [False, None])
def test_a_round_no_cap_stopped_asks_for_nothing(cap_reached: bool | None) -> None:
    assert not _decide(
        _plan(cap_reached=cap_reached), ON, released_last_day=0, matrix=_matrix()
    ).drain_more


def test_a_round_that_mints_nothing_never_chains() -> None:
    decision = _decide(
        _plan(cells=0, deferred=5, cap_reached=True), ON, released_last_day=0, matrix=_matrix(0)
    )
    assert not decision.drain_more
    assert "mints nothing" in decision.drain_reason


def test_drain_is_independent_of_auto_release() -> None:
    held = _decide(
        _plan(spend=999.0, deferred=2), ReviewHoldConfig(), released_last_day=None, matrix=None
    )
    assert not held.auto_release
    assert held.drain_more


def test_the_summary_says_what_the_round_does() -> None:
    released = render_summary(_decide(_plan(), ON, released_last_day=0, matrix=_matrix()))
    assert "**Auto-released:**" in released
    held = render_summary(_decide(_plan(deferred=2), ON, released_last_day=None, matrix=_matrix()))
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


def test_the_shipped_budget_sits_below_the_shipped_backstop() -> None:
    # A shipped budget at or above the ceiling would hold every round with a
    # named reason rather than fail, so pin the shipped pair here instead: the
    # values the maintainer adopted must actually be able to release a round.
    root = Path(__file__).resolve().parents[1] / "config"
    caps = load_review_hold_config(root)
    backstop = load_spend_config(root)
    if caps.auto_release_budget_usd > 0:
        assert 0 < caps.auto_release_budget_usd < backstop.ceiling_usd
        # The whole daily allowance fits inside the budget, or the last
        # rounds of a day could never release.
        assert (
            caps.auto_release_usd_per_round * caps.auto_release_rounds_per_day
            < caps.auto_release_budget_usd
        )


# --- the command -------------------------------------------------------------

runner = CliRunner()


def _cmd_env(tmp_path: Path, *, ledger: bool = True) -> dict[str, str]:
    config_root = tmp_path / "config"
    config_root.mkdir()
    (config_root / "review-hold.yaml").write_text(
        "auto_release_usd_per_round: 45\nauto_release_rounds_per_day: 4\n"
        + "auto_release_budget_usd: 1000\n"
    )
    (config_root / "tracking.yaml").write_text("spend:\n  ceiling_usd: 4000\n  window_days: 30\n")
    data_root = tmp_path / "data"
    if ledger:
        (data_root / "cases").mkdir(parents=True)
    return {"FEDCOURTS_CONFIG_ROOT": str(config_root), "FEDCOURTS_DATA_ROOT": str(data_root)}


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


# --- the trailing budget -------------------------------------------------------


def test_a_round_that_lands_exactly_on_the_budget_is_released() -> None:
    # measured $900 + in flight 1 x $45 + this round $40 = $985.
    config = ON.model_copy(update={"auto_release_budget_usd": 985.0})
    measured = MeasuredSpend(cells_usd=880.0, summaries_usd=20.0)
    decision = _decide(
        _plan(spend=40.0), config, released_last_day=1, matrix=_matrix(), measured=measured
    )
    assert decision.auto_release, decision.auto_release_reason
    assert decision.projected_spend_usd == pytest.approx(985.0)
    assert decision.in_flight_bound_usd == pytest.approx(45.0)
    assert "within the $985.00 auto-release budget" in decision.auto_release_reason


def test_a_round_a_cent_over_the_budget_is_held_with_the_arithmetic() -> None:
    config = ON.model_copy(update={"auto_release_budget_usd": 984.99})
    measured = MeasuredSpend(cells_usd=880.0, summaries_usd=20.0)
    decision = _decide(
        _plan(spend=40.0), config, released_last_day=1, matrix=_matrix(), measured=measured
    )
    assert not decision.auto_release
    reason = decision.auto_release_reason
    assert "over the $984.99 auto-release budget" in reason
    # Every figure of the sum is named.
    for figure in ("$985.00", "$900.00", "$880.00", "$20.00", "$45.00", "$40.00"):
        assert figure in reason


def test_the_in_flight_bound_grows_with_the_rounds_released_today() -> None:
    # 800 + 3 x $45 + $40 = $975 fits a $1,000 budget; at measured $830 the
    # same three in-flight rounds leave no room for this one.
    measured = MeasuredSpend(cells_usd=800.0, summaries_usd=0.0)
    assert _decide(_plan(), released_last_day=3, matrix=_matrix(), measured=measured).auto_release
    higher = MeasuredSpend(cells_usd=830.0, summaries_usd=0.0)
    held = _decide(_plan(), released_last_day=3, matrix=_matrix(), measured=higher)
    assert not held.auto_release
    assert held.projected_spend_usd == pytest.approx(830.0 + 135.0 + 40.0)


def test_an_unreadable_ledger_keeps_the_hold() -> None:
    decision = _decide(_plan(), released_last_day=0, matrix=_matrix(), measured=None)
    assert not decision.auto_release
    assert "ledger" in decision.auto_release_reason
    assert decision.projected_spend_usd is None


def test_an_unreadable_backstop_keeps_the_hold() -> None:
    decision = _decide(_plan(), released_last_day=0, matrix=_matrix(), backstop=None)
    assert not decision.auto_release
    assert "tracking.yaml" in decision.auto_release_reason


def test_a_disabled_backstop_keeps_the_hold() -> None:
    decision = _decide(
        _plan(), released_last_day=0, matrix=_matrix(), backstop=SpendConfig(ceiling_usd=0.0)
    )
    assert not decision.auto_release
    assert "backstop is off" in decision.auto_release_reason


@pytest.mark.parametrize("budget", [4000.0, 5000.0])
def test_a_budget_at_or_above_the_ceiling_is_refused_not_adopted(budget: float) -> None:
    config = ON.model_copy(update={"auto_release_budget_usd": budget})
    decision = _decide(_plan(), config, released_last_day=0, matrix=_matrix())
    assert not decision.auto_release
    assert "not below the spend backstop's ceiling $4,000.00" in decision.auto_release_reason


# --- per seam ------------------------------------------------------------------


def _summary_plan(*, high: float | None = 2.5, cases: int = 4) -> dict[str, Any]:
    """A `summarize-plan` document in its real shape: no matrix, a case list."""
    plan: dict[str, Any] = {
        "model": "claude-sonnet-5",
        "cases": [{"case_id": f"scotus/{n}"} for n in range(cases)],
        "estimated_cost_usd_low": 1.0,
    }
    if high is not None:
        plan["estimated_cost_usd_high"] = high
    return plan


def test_an_evaluate_round_is_priced_at_the_evaluate_rates() -> None:
    # Ten claude evaluate cells price at $5.92 each: $59.20, over a $45 cap,
    # though the plan claims $1.
    decision = _decide(
        _plan(spend=1.0, cells=10),
        seam="evaluate",
        released_last_day=0,
        matrix=_matrix(10, engine="claude-code"),
    )
    assert decision.estimated_spend_usd == pytest.approx(59.2)
    assert not decision.auto_release
    released = _decide(
        _plan(spend=1.0, cells=7),
        seam="evaluate",
        released_last_day=0,
        matrix=_matrix(7, engine="claude-code"),
    )
    assert released.auto_release
    assert not released.drain_more
    assert "only a predict round" in released.drain_reason


def test_an_evaluate_matrix_that_disagrees_with_its_plan_keeps_the_hold() -> None:
    decision = _decide(_plan(cells=3), seam="evaluate", released_last_day=0, matrix=_matrix(2))
    assert not decision.auto_release
    assert "price is not the price of what runs" in decision.auto_release_reason


def test_an_evaluate_round_never_asks_for_a_drain() -> None:
    decision = _decide(
        _plan(deferred=6, cap_reached=True), seam="evaluate", released_last_day=0, matrix=_matrix()
    )
    assert not decision.drain_more


def test_a_summarize_round_is_priced_at_its_plans_upper_estimate() -> None:
    decision = _decide(_summary_plan(high=2.5), seam="summarize", released_last_day=0, matrix=None)
    assert decision.auto_release, decision.auto_release_reason
    assert decision.estimated_spend_usd == pytest.approx(2.5)
    assert decision.plan_cells == 4
    assert decision.matrix_cells is None
    assert not decision.drain_more


def test_a_summarize_round_ignores_any_matrix() -> None:
    decision = _decide(
        _summary_plan(), seam="summarize", released_last_day=0, matrix=_matrix(9, engine="x")
    )
    assert decision.auto_release
    assert decision.estimated_spend_usd == pytest.approx(2.5)


@pytest.mark.parametrize("high", [None, math.nan, -1.0])
def test_a_summarize_plan_without_an_upper_estimate_keeps_the_hold(high: float | None) -> None:
    plan = _summary_plan(high=None)
    if high is not None:
        plan["estimated_cost_usd_high"] = high
    decision = _decide(plan, seam="summarize", released_last_day=0, matrix=None)
    assert not decision.auto_release
    assert "no spend estimate" in decision.auto_release_reason


def test_a_summarize_plan_without_a_case_list_keeps_the_hold() -> None:
    plan = _summary_plan()
    del plan["cases"]
    decision = _decide(plan, seam="summarize", released_last_day=0, matrix=None)
    assert not decision.auto_release
    assert "case list" in decision.auto_release_reason


def test_a_summarize_round_over_the_per_round_cap_is_held() -> None:
    decision = _decide(
        _summary_plan(high=45.01), seam="summarize", released_last_day=0, matrix=None
    )
    assert not decision.auto_release
    assert "over the per-round cap" in decision.auto_release_reason


@pytest.mark.parametrize("seam", ["predict", "evaluate", "summarize"])
def test_the_daily_cap_is_shared_by_every_lane(seam: Seam) -> None:
    plan = _summary_plan() if seam == "summarize" else _plan()
    decision = _decide(plan, seam=seam, released_last_day=4, matrix=_matrix())
    assert not decision.auto_release
    assert "across the lanes (daily cap 4)" in decision.auto_release_reason


def test_the_summary_shows_the_budget_arithmetic() -> None:
    text = render_summary(_decide(_plan(), released_last_day=2, matrix=_matrix()))
    assert "Budget arithmetic (trailing 30-day window)" in text
    assert "| Measured: agent cells (`usage.json`) | $100.00 |" in text
    assert "| Measured: case summaries | $5.00 |" in text
    assert "| In flight: 2 round(s) auto-released in the last 24h x per-round cap | $90.00 |" in (
        text
    )
    assert "| **Projected** | **$235.00** |" in text
    assert "| Auto-release budget | $1,000.00 |" in text
    unknown = render_summary(
        _decide(_plan(), released_last_day=None, matrix=_matrix(), measured=None)
    )
    assert "| **Projected** | **unknown** |" in unknown
    evaluate = render_summary(
        _decide(_plan(), seam="evaluate", released_last_day=0, matrix=_matrix())
    )
    assert "### Hold\n" in evaluate
    assert "further round" not in evaluate


# --- measured spend --------------------------------------------------------------

_USAGE = {
    "actor_id": "claude-baseline",
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0,
    "case_id": "scotus/1",
    "engine": "claude-code",
    "event_id": "evt-cert",
    "input_tokens": 1,
    "model": "claude-opus-5-5",
    "output_tokens": 1,
    "pipeline_sha": "0" * 40,
    "role": "predictor",
    "schema_version": "1.0",
}

NOW = datetime(2026, 10, 17, 12, 0, tzinfo=UTC)


def _write_usage(data_root: Path, run_id: str, created_at: str, cost: float) -> None:
    path = (
        data_root
        / "cases/scotus/1/events/evt-cert/predictions/claude-baseline"
        / run_id
        / "usage.json"
    )
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {**_USAGE, "run_id": run_id, "created_at": created_at, "estimated_cost_usd": cost}
        )
    )


def _write_summary(data_root: Path, day: str, generated_at: str, cost: float | None) -> None:
    path = data_root / "cases/scotus/1/summaries" / f"{day}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    usage = (
        ""
        if cost is None
        else f"usage:\n  input_tokens: 10\n  output_tokens: 1\n  estimated_cost_usd: {cost}\n"
    )
    path.write_text(
        "---\n"
        + "case_id: scotus/1\n"
        + f"snapshot: '{day}'\n"
        + f"record_digest: sha256:{'a' * 64}\n"
        + "model: claude-sonnet-5\n"
        + f"prompt_digest: sha256:{'b' * 64}\n"
        + "body_version: 2\n"
        + f"generated_at: '{generated_at}'\n"
        + usage
        + "---\n\n## In brief\n\nBody.\n"
    )


def test_measured_spend_sums_cells_and_summaries_inside_the_window(tmp_path: Path) -> None:
    _write_usage(tmp_path, "20261010T120000Z", "2026-10-10T12:00:00Z", 10.0)
    _write_usage(tmp_path, "20261001T120000Z", "2026-10-01T12:00:00Z", 5.0)
    _write_usage(tmp_path, "20260901T120000Z", "2026-09-01T12:00:00Z", 100.0)  # outside
    _write_summary(tmp_path, "2026-10-12", "2026-10-12T03:50:00Z", 0.25)
    _write_summary(tmp_path, "2026-10-11", "2026-10-11T03:50:00Z", None)  # no usage recorded
    _write_summary(tmp_path, "2026-09-01", "2026-09-01T03:50:00Z", 9.0)  # outside
    measured = measured_spend(tmp_path, window_days=30, now=NOW)
    assert measured is not None
    assert measured.cells_usd == pytest.approx(15.0)
    assert measured.summaries_usd == pytest.approx(0.25)
    assert measured.total_usd == pytest.approx(15.25)


def test_a_missing_ledger_is_unreadable_not_empty(tmp_path: Path) -> None:
    assert measured_spend(tmp_path, window_days=30, now=NOW) is None
    (tmp_path / "cases").mkdir()
    assert measured_spend(tmp_path, window_days=30, now=NOW) == MeasuredSpend(0.0, 0.0)


def test_a_malformed_usage_row_makes_the_ledger_unreadable(tmp_path: Path) -> None:
    _write_usage(tmp_path, "20261010T120000Z", "2026-10-10T12:00:00Z", 10.0)
    next(tmp_path.rglob("usage.json")).write_text("{not json")
    assert measured_spend(tmp_path, window_days=30, now=NOW) is None


def test_a_malformed_summary_makes_the_ledger_unreadable(tmp_path: Path) -> None:
    (tmp_path / "cases").mkdir()
    _write_summary(tmp_path, "2026-10-12", "2026-10-12T03:50:00Z", 0.25)
    next(tmp_path.rglob("*.md")).write_text("no front matter\n")
    assert measured_spend(tmp_path, window_days=30, now=NOW) is None


# --- the command, per seam and over the ledger -------------------------------------


def _invoke(tmp_path: Path, args: list[str], *, ledger: bool = True) -> dict[str, Any]:
    subjects = tmp_path / "subjects.txt"
    subjects.write_text("")
    result = runner.invoke(
        app,
        [
            "hold-decision",
            *args,
            "--deployments-released",
            "0",
            "--main-subjects-file",
            str(subjects),
        ],
        env=_cmd_env(tmp_path, ledger=ledger),
    )
    assert result.exit_code == 0, result.output
    decision: dict[str, Any] = json.loads(result.stdout)
    return decision


def test_the_command_decides_a_summarize_round_without_a_matrix(tmp_path: Path) -> None:
    plan = tmp_path / "summary-plan.json"
    plan.write_text(json.dumps(_summary_plan()))
    decision = _invoke(tmp_path, ["--plan-file", str(plan), "--seam", "summarize"])
    assert decision["seam"] == "summarize"
    assert decision["auto_release"] is True, decision["auto_release_reason"]
    assert decision["projected_spend_usd"] == pytest.approx(2.5)


def test_the_command_decides_an_evaluate_round(tmp_path: Path) -> None:
    plan, matrix = _files(tmp_path)
    decision = _invoke(
        tmp_path,
        ["--plan-file", str(plan), "--matrix-file", str(matrix), "--seam", "evaluate"],
    )
    assert decision["seam"] == "evaluate"
    assert decision["auto_release"] is True, decision["auto_release_reason"]
    assert decision["drain_more"] is False


def test_the_command_holds_when_the_ledger_is_missing(tmp_path: Path) -> None:
    plan, matrix = _files(tmp_path)
    decision = _invoke(
        tmp_path, ["--plan-file", str(plan), "--matrix-file", str(matrix)], ledger=False
    )
    assert decision["auto_release"] is False
    assert "ledger" in decision["auto_release_reason"]


def test_the_command_refuses_an_unknown_seam(tmp_path: Path) -> None:
    plan, _ = _files(tmp_path)
    result = runner.invoke(app, ["hold-decision", "--plan-file", str(plan), "--seam", "backtest"])
    assert result.exit_code == 1
    assert "--seam" in result.output


# --- the label seam ----------------------------------------------------------------


def _label_plan(*, rows: int = 1200, high: float | None = 24.0) -> dict[str, Any]:
    """A `qp-label-plan` document in its real shape."""
    plan: dict[str, Any] = {"stage": "label", "frame": "petitions", "rows": rows}
    if high is not None:
        plan["estimated_cost_usd_high"] = high
    return plan


def _write_run(
    data_root: Path,
    run_id: str,
    recorded_at: str,
    *,
    outcome: str = "published",
    frame: str = "petitions",
    cost: float = 10.01,
    attempt: int = 1,
) -> None:
    measured = outcome != "incomplete"
    record = {
        "frame": frame,
        "run_id": run_id,
        "run_attempt": attempt,
        "labeler": "claude-code/claude-opus-5-5",
        "model": "claude-opus-5-5",
        "outcome": outcome,
        "batch_rows": 1200,
        "label_lines": 1200,
        "agree": 160 if measured else None,
        "n": 200 if measured else None,
        "rate": 0.8 if measured else None,
        "floor": 0.3 if measured else None,
        "recorded_at": recorded_at,
        "input_tokens": 100,
        "output_tokens": 10,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0,
        "estimated_cost_usd": cost,
    }
    path = data_root / "qp-topics" / "spend" / f"{run_id}-{attempt}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record))


def test_a_label_round_is_priced_from_its_plan_without_a_matrix() -> None:
    decision = _decide(_label_plan(), seam="label", released_last_day=0, matrix=None)
    assert decision.auto_release, decision.auto_release_reason
    assert decision.estimated_spend_usd == pytest.approx(24.0)
    assert decision.plan_cells == 1200
    assert decision.matrix_cells is None
    assert decision.drain_more is False


@pytest.mark.parametrize(
    "plan",
    [_label_plan(rows=0), _label_plan(high=None), {**_label_plan(), "rows": True}],
)
def test_a_label_round_without_a_readable_plan_is_held(plan: dict[str, Any]) -> None:
    assert not _decide(plan, seam="label", released_last_day=0, matrix=None).auto_release


def test_a_label_round_over_the_per_round_cap_is_held() -> None:
    decision = _decide(_label_plan(high=72.0), seam="label", released_last_day=0, matrix=None)
    assert not decision.auto_release
    assert "over the per-round cap" in decision.auto_release_reason


def test_a_label_round_after_a_refusal_waits_for_a_maintainer() -> None:
    reason = "the last petitions labeling run was refused at the reference gate; a retry waits"
    decision = decide(
        _label_plan(),
        ON,
        seam="label",
        released_last_day=0,
        matrix=None,
        backstop=BACKSTOP,
        measured=LOW,
        label_refusal=reason,
    )
    assert not decision.auto_release
    assert decision.auto_release_reason == reason
    # Another seam ignores the label rule.
    summarize = decide(
        _summary_plan(),
        ON,
        seam="summarize",
        released_last_day=0,
        matrix=None,
        backstop=BACKSTOP,
        measured=LOW,
        label_refusal=reason,
    )
    assert summarize.auto_release, summarize.auto_release_reason


def test_the_refusal_rule_reads_the_newest_gated_run_of_the_frame(tmp_path: Path) -> None:
    assert label_refusal(tmp_path, "petitions") is None  # no records at all
    _write_run(tmp_path, "100", "2026-10-01T09:00:00Z", outcome="published")
    assert label_refusal(tmp_path, "petitions") is None
    _write_run(tmp_path, "200", "2026-10-08T09:00:00Z", outcome="refused")
    reason = label_refusal(tmp_path, "petitions")
    assert reason is not None and "petitions labeling run was refused" in reason
    # An incomplete run was never gated: it neither clears nor sets the rule.
    _write_run(tmp_path, "300", "2026-10-15T09:00:00Z", outcome="incomplete")
    assert label_refusal(tmp_path, "petitions") is not None
    # The other frame's record is not this frame's.
    assert label_refusal(tmp_path, "applications") is None
    _write_run(tmp_path, "301", "2026-10-15T09:30:00Z", outcome="refused", frame="applications")
    assert label_refusal(tmp_path, "applications") is not None
    # A newer published run clears it.
    _write_run(tmp_path, "400", "2026-10-22T09:00:00Z", outcome="published")
    assert label_refusal(tmp_path, "petitions") is None


def test_an_unreadable_run_record_keeps_a_label_round_held(tmp_path: Path) -> None:
    _write_run(tmp_path, "100", "2026-10-01T09:00:00Z")
    next((tmp_path / "qp-topics" / "spend").glob("*.json")).write_text("{not json")
    reason = label_refusal(tmp_path, "petitions")
    assert reason is not None and "could not be read" in reason


def test_measured_spend_counts_labeler_runs_by_recorded_at(tmp_path: Path) -> None:
    _write_usage(tmp_path, "20261010T120000Z", "2026-10-10T12:00:00Z", 10.0)
    _write_run(tmp_path, "100", "2026-10-14T09:00:00Z", outcome="refused", cost=9.28)
    _write_run(tmp_path, "101", "2026-10-15T09:00:00Z", outcome="published", cost=10.01)
    _write_run(tmp_path, "50", "2026-09-01T09:00:00Z", cost=60.16)  # outside the window
    measured = measured_spend(tmp_path, window_days=30, now=NOW)
    assert measured is not None
    assert measured.labeler_usd == pytest.approx(19.29)
    assert measured.total_usd == pytest.approx(29.29)


def test_the_hold_summary_and_arithmetic_name_the_labeler_runs() -> None:
    measured = MeasuredSpend(cells_usd=100.0, summaries_usd=5.0, labeler_usd=19.29)
    decision = _decide(
        _label_plan(), seam="label", released_last_day=0, matrix=None, measured=measured
    )
    assert decision.measured_labeler_usd == pytest.approx(19.29)
    assert decision.projected_spend_usd == pytest.approx(148.29)
    assert "labeler runs $19.29" in decision.auto_release_reason
    summary = render_summary(decision)
    assert "| Measured: topic-labeler runs | $19.29 |" in summary
    assert "**$148.29**" in summary


def test_an_auto_released_label_round_is_counted_once_by_run() -> None:
    subjects = [
        "data(qp-topics): batch 11 — 1000 new qp-topic-v0 label(s) by claude-code/claude-opus-5-5 "
        + f"(9000 total) (run 123) {AUTO_RELEASED_MARKER} (#77)",
        "data(qp-topics): spend record of a refused application labeling run, no labels "
        + f"published (run 124) {AUTO_RELEASED_MARKER}",
        f"data(summaries): 3 plain-language case summaries (run 123) {AUTO_RELEASED_MARKER}",
        "data(qp-topics): batch 11 — 1000 new label(s) (run 125)",  # held: no mark
    ]
    # Run 123 is two rounds: one label, one summarize.
    assert count_auto_released(subjects) == 3


def test_the_command_decides_a_label_round_and_reads_the_refusal(tmp_path: Path) -> None:
    plan = tmp_path / "label-plan.json"
    plan.write_text(json.dumps(_label_plan()))
    env = _cmd_env(tmp_path)
    subjects = tmp_path / "subjects.txt"
    subjects.write_text("")
    args = [
        "hold-decision",
        "--plan-file",
        str(plan),
        "--seam",
        "label",
        "--deployments-released",
        "0",
        "--main-subjects-file",
        str(subjects),
    ]
    released = runner.invoke(app, args, env=env)
    assert released.exit_code == 0, released.output
    assert json.loads(released.stdout)["auto_release"] is True
    _write_run(tmp_path / "data", "200", "2026-10-28T09:00:00Z", outcome="refused")
    held = json.loads(runner.invoke(app, args, env=env).stdout)
    assert held["auto_release"] is False
    assert "refused at the reference gate" in held["auto_release_reason"]
