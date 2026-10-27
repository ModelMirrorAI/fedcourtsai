"""Hand-worked tests for the selection bounds and the filing simulation.

The estimators (`pipeline.selection_bounds`) publish intervals, so the tests
pin each tier against values worked by hand, including the worked
illustration of filing shares 0.5 against 0.25 at an 80% win rate. The
simulation (`pipeline.filing_simulation`) is checked where its truth is known
exactly: identical sides have no gap, anticipation invents one in the naive
comparison, and a large sample's bounds cover the truth.
"""

from __future__ import annotations

import json
import random
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli
from fedcourtsai.cli import app
from fedcourtsai.pipeline import filing_simulation as sim
from fedcourtsai.pipeline.selection_bounds import (
    Interval,
    OrderRecord,
    SideCounts,
    breakdown_rho,
    cluster_bootstrap,
    imbens_manski_critical_value,
    imbens_manski_interval,
    lee_gap,
    manski_bounds,
    monotone_bounds,
    prediction_trimmed_rate,
    side_counts,
    stratified_breakdown_rho,
    stratified_lee_gap,
    trimmed_rate_bounds,
    trimming_share,
)

runner = CliRunner()


def _records(side: str, stratum: str, wins: int, losses: int, unfiled: int) -> list[OrderRecord]:
    out = [OrderRecord(side, stratum, f"{side}-{stratum}-w{i}", True, True) for i in range(wins)]
    out += [
        OrderRecord(side, stratum, f"{side}-{stratum}-l{i}", True, False) for i in range(losses)
    ]
    out += [OrderRecord(side, stratum, f"{side}-{stratum}-u{i}", False) for i in range(unfiled)]
    return out


def test_tier_one_and_two_bound_the_pool_rate() -> None:
    tier1 = manski_bounds(0.8, 0.25)
    assert tier1.lower == pytest.approx(0.2)
    assert tier1.upper == pytest.approx(0.95)
    tier2 = monotone_bounds(0.8, 0.25)
    assert tier2.lower == pytest.approx(0.2)
    assert tier2.upper == 0.8
    assert manski_bounds(0.8, 1.0) == Interval(0.8, 0.8)
    with pytest.raises(ValueError, match="filing_share"):
        manski_bounds(0.5, 1.5)


def test_the_worked_illustration_bounds_the_always_filer_rate_in_60_to_100() -> None:
    pi = trimming_share(0.5, 0.25)
    assert pi == 0.5
    bounds = trimmed_rate_bounds(0.8, pi)
    assert bounds.lower == pytest.approx(0.6)
    assert bounds.upper == 1.0


def test_trimming_everything_leaves_any_rate() -> None:
    assert trimmed_rate_bounds(0.4, 1.0) == Interval(0.0, 1.0)
    assert trimming_share(0.5, 0.0) == 1.0
    with pytest.raises(ValueError, match="exceeds"):
        trimming_share(0.2, 0.4)


def test_lee_gap_trims_the_less_selective_side_whichever_it_is() -> None:
    # a files half its pool and wins 80%; b files a quarter and wins 50%.
    a = SideCounts(pool=100, decided=50, wins=40)
    b = SideCounts(pool=100, decided=25, wins=12)
    result = lee_gap(a, b, a_name="trump", b_name="biden")
    assert result.less_selective == "trump"
    assert result.trimming_share == 0.5
    assert result.gap.lower == pytest.approx(0.6 - 0.48)
    assert result.gap.upper == pytest.approx(1.0 - 0.48)
    flipped = lee_gap(b, a, a_name="biden", b_name="trump")
    assert flipped.less_selective == "trump"
    assert flipped.gap.lower == pytest.approx(-result.gap.upper)
    assert flipped.gap.upper == pytest.approx(-result.gap.lower)


def test_equal_filing_shares_identify_the_gap_as_a_point() -> None:
    result = lee_gap(SideCounts(10, 5, 4), SideCounts(20, 10, 5))
    assert result.less_selective is None
    assert result.gap.lower == result.gap.upper == pytest.approx(0.3)


def test_rho_widens_the_bounds_and_breakdown_is_where_they_reach_zero() -> None:
    a = SideCounts(pool=100, decided=40, wins=36)
    b = SideCounts(pool=100, decided=40, wins=12)
    assert not lee_gap(a, b).gap.contains(0.0)
    rho = breakdown_rho(a, b)
    assert 0.0 < rho < 1.0
    assert lee_gap(a, b, rho=rho).gap.contains(0.0)
    assert not lee_gap(a, b, rho=rho - 1e-4).gap.contains(0.0)
    wider = lee_gap(a, b, rho=0.2).gap
    assert wider.lower < lee_gap(a, b).gap.lower
    assert wider.upper >= lee_gap(a, b).gap.upper
    # Bounds that already include zero break down at once.
    assert breakdown_rho(SideCounts(10, 5, 3), SideCounts(10, 2, 1)) == 0.0


def test_stratified_breakdown_widens_every_stratum_until_zero_is_inside() -> None:
    records = _records("a", "imm", wins=9, losses=1, unfiled=10) + _records(
        "b", "imm", wins=3, losses=7, unfiled=10
    )
    rho = stratified_breakdown_rho(records, "a", "b")
    assert rho is not None and 0.0 < rho < 1.0
    assert rho == pytest.approx(
        breakdown_rho(SideCounts(20, 10, 9), SideCounts(20, 10, 3)), abs=1e-5
    )
    assert stratified_breakdown_rho(_records("a", "imm", 1, 0, 0), "a", "b") is None


def test_stratified_gap_weights_by_always_filers_and_skips_empty_strata() -> None:
    records = (
        _records("a", "imm", wins=4, losses=0, unfiled=0)
        + _records("b", "imm", wins=2, losses=2, unfiled=0)
        + _records("a", "health", wins=1, losses=1, unfiled=2)
        + _records("b", "health", wins=1, losses=1, unfiled=2)
        + _records("a", "guns", wins=1, losses=0, unfiled=0)
        + _records("b", "guns", wins=0, losses=0, unfiled=3)
    )
    result = stratified_lee_gap(records, "a", "b")
    assert result.skipped == ("guns",)
    by_name = {item.stratum: item for item in result.strata}
    # imm: q 1 and 1, gap 1.0 - 0.5; weight 1 * 8. health: q 0.5 and 0.5, gap 0; weight 0.5 * 8.
    assert by_name["imm"].weight == 8.0
    assert by_name["health"].weight == 4.0
    assert result.gap is not None
    assert result.gap.lower == pytest.approx(0.5 * 8 / 12)
    assert result.gap.upper == pytest.approx(0.5 * 8 / 12)


def test_prediction_trimming_drops_the_lowest_scored_decided_filings() -> None:
    records = [
        OrderRecord("a", 0, "c1", True, False, score=0.1),
        OrderRecord("a", 0, "c2", True, False, score=0.2),
        OrderRecord("a", 0, "c3", True, True, score=0.9),
        OrderRecord("a", 0, "c4", True, True, score=0.8),
        OrderRecord("a", 0, "c5", False, None, score=None),
    ]
    assert prediction_trimmed_rate(records, 0.5) == 1.0
    assert prediction_trimmed_rate(records, 0.0) == 0.5
    assert prediction_trimmed_rate(records, 1.0) is None
    # A half rounds up: 0.5 of 5 decided filings drops 3, and 0.5 of 7 drops 4.
    five = [OrderRecord("a", 0, f"c{i}", True, i >= 3, score=float(i)) for i in range(5)]
    assert prediction_trimmed_rate(five, 0.5) == 1.0
    seven = [OrderRecord("a", 0, f"c{i}", True, i >= 4, score=float(i)) for i in range(7)]
    assert prediction_trimmed_rate(seven, 0.5) == 1.0
    assert prediction_trimmed_rate(seven, 0.4) == 0.75
    with pytest.raises(ValueError, match="score"):
        prediction_trimmed_rate([OrderRecord("a", 0, "c", True, True)], 0.5)


def test_imbens_manski_runs_from_two_sided_to_one_sided() -> None:
    assert imbens_manski_critical_value(0.0, 1.0) == pytest.approx(1.95996, abs=1e-4)
    assert imbens_manski_critical_value(100.0, 1.0) == pytest.approx(1.64485, abs=1e-4)
    estimate = Interval(0.1, 0.3)
    assert imbens_manski_interval(estimate, 0.0, 0.0) == estimate
    wide = imbens_manski_interval(estimate, 0.05, 0.05)
    assert wide.lower < 0.1 and wide.upper > 0.3


def test_cluster_bootstrap_moves_whole_controversies() -> None:
    # Every controversy holds two identical orders; a draw that split one would
    # leave an odd count.
    records = [
        OrderRecord("a", 0, f"c{i}", True, i % 2 == 0) for i in range(6) for _ in range(2)
    ] + [OrderRecord("b", 0, f"d{i}", True, True) for i in range(4) for _ in range(2)]

    def statistic(sample: list[OrderRecord]) -> Interval:
        counts: dict[object, int] = {}
        for record in sample:
            counts[(record.side, record.controversy)] = (
                counts.get((record.side, record.controversy), 0) + 1
            )
        assert all(count % 2 == 0 for count in counts.values())
        assert sum(1 for r in sample if r.side == "a") == 12
        rate = side_counts(r for r in sample if r.side == "a").win_rate or 0.0
        return Interval(rate, rate)

    se_lower, se_upper, usable = cluster_bootstrap(
        records, statistic, draws=50, rng=random.Random(1)
    )
    assert usable == 50
    assert se_lower == se_upper > 0.0
    same = cluster_bootstrap(records, statistic, draws=50, rng=random.Random(1))
    assert same == (se_lower, se_upper, usable)


def test_counts_and_records_refuse_impossible_values() -> None:
    with pytest.raises(ValueError):
        SideCounts(pool=3, decided=4, wins=1)
    with pytest.raises(ValueError):
        OrderRecord("a", 0, "c", True, None)
    with pytest.raises(ValueError):
        OrderRecord("a", 0, "c", False, True)


def _small(scenario: sim.Scenario, **changes: Any) -> sim.Scenario:
    fields = {**scenario.__dict__, **changes}
    return sim.Scenario(**fields)


def test_identical_sides_have_no_true_gap() -> None:
    scenario = sim.Scenario(name="same", description="identical sides")
    truth = sim.true_gap(scenario, random.Random(0), orders=5_000)
    assert truth.gap == 0.0
    assert 0.0 < truth.always_filer_share < 1.0


def test_anticipation_invents_a_naive_gap_the_truth_does_not_have() -> None:
    scenario = next(s for s in sim.SCENARIOS if s.name == "anticipation")
    result = sim.run_scenario(
        scenario, runs=40, bootstrap_draws=0, level=0.95, seed=3, reference_orders=5_000
    )
    assert result.true_gap == 0.0
    assert result.mean_naive_gap is not None and result.mean_naive_gap < -0.05
    assert result.mean_filing_share_a > result.mean_filing_share_b


def test_a_large_sample_bounds_cover_the_baseline_truth() -> None:
    scenario = _small(sim.SCENARIOS[0], controversies_per_side=2_000, bootstrap=False)
    result = sim.run_scenario(
        scenario, runs=3, bootstrap_draws=0, level=0.95, seed=5, reference_orders=50_000
    )
    assert result.tier3_coverage == 1.0
    assert result.tier1_coverage_a == result.tier2_coverage_a == 1.0


def test_the_naive_gap_falls_as_perceived_favorability_rises() -> None:
    points = sim.attenuation_series(runs=40, seed=7, reference_orders=5_000, perceived=(0.0, 2.5))
    first, last = points
    assert first.mean_naive_gap is not None and last.mean_naive_gap is not None
    assert last.mean_naive_gap < first.mean_naive_gap
    assert first.true_gap == pytest.approx(last.true_gap, abs=0.02)


def test_the_report_is_deterministic_for_a_seed() -> None:
    scenarios = (_small(sim.SCENARIOS[0], controversies_per_side=10),)
    one = sim.filing_simulation(
        seed=9, runs=3, bootstrap_draws=5, scenarios=scenarios, reference_orders=2_000
    )
    two = sim.filing_simulation(
        seed=9, runs=3, bootstrap_draws=5, scenarios=scenarios, reference_orders=2_000
    )
    assert one == two
    with pytest.raises(ValueError, match="runs"):
        sim.filing_simulation(runs=0)


def test_filing_simulation_command_prints_the_report(monkeypatch: pytest.MonkeyPatch) -> None:
    def quick(**kwargs: Any) -> sim.FilingSimulationReport:
        scenarios = (_small(sim.SCENARIOS[0], controversies_per_side=10),)
        return sim.filing_simulation(scenarios=scenarios, reference_orders=2_000, **kwargs)

    monkeypatch.setattr(cli, "filing_simulation", quick)
    result = runner.invoke(app, ["filing-simulation", "--runs", "2", "--bootstrap-draws", "0"])
    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout.strip().splitlines()[-1])
    assert report["runs"] == 2
    assert [item["name"] for item in report["scenarios"]] == ["baseline"]
    assert "attenuation: A perceives" in result.stderr
    bad = runner.invoke(app, ["filing-simulation", "--runs", "0"])
    assert bad.exit_code == 2
