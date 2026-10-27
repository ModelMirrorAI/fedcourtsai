"""A simulation of strategic filing: how it hides or invents a gap, and what the bounds recover.

Analytics only: it reads no corpus, writes nothing, and no cell reads it. It is
the simulation study of the selection-adjusted executive success analysis, and
it exercises the estimators in :mod:`.selection_bounds` on data whose truth is
known.

**Why.** Two administrations' observed emergency-docket win rates can look
alike while the Court treats them differently, or differ while it treats them
alike, because each side decides which adverse orders to bring. A structural
filing model is used here **only to generate data**; nothing is estimated with
it. Each scenario records the true comparable-case gap, the naive gap in
observed win rates, and the tier 1-3 bounds, so the attenuation and the bounds'
coverage can be read off directly.

**Data-generating process**, for each side (administration) ``a``:

1. Draw controversies; each carries a random effect, a salience flag and a
   breadth-of-theory flag, and holds one or more adverse orders. An order's
   latent strength is ``θ = shift_a + u_controversy + e_order``.
2. The Court's true treatment is ``δ_a`` on the log-odds of a government win:
   ``p = logit⁻¹(θ + δ_a)``.
3. The side files when ``p̂ (1 + L) - L + S + κ ε > 0``, where ``p̂`` uses the
   side's *perceived* effect, ``L`` is the precedent cost (a base stake plus an
   extra cost on broad theories), ``S`` is signal value on salient
   controversies, ``ε`` is standard logistic noise, and ``κ`` sets how close the
   rule is to a hard threshold. Where ``signal_heterogeneous`` is set, ``S`` is
   scaled by an exponential draw made independently for each side and each
   order. With signal value on both sides, an order one side files for its
   signal the other may not, so neither side's filings contain the other's and
   monotone filing (A2) fails.
4. A filed order is decided, and the government wins with probability ``p``.

Every filed order is decided: the simulation has no withdrawals.

**The truth.** The comparable-case gap is defined on a reference pool drawn
with no pool shift: each reference order is run through both sides' filing
rules with the same ``ε``, the always-filers are those both would file, and the
gap is the mean of ``logit⁻¹(θ + δ_a) - logit⁻¹(θ + δ_b)`` over them. The
pool-level win rate a side's tier 1 and tier 2 bounds aim at is the mean ``p``
over that side's own simulated pool.

**What one run records.** The naive gap; tier 1 and tier 2 bounds on each
side's pool-level rate; tier 3 bounds stratified by salience and breadth
(:func:`.selection_bounds.stratified_lee_gap`); where bootstrap draws are asked
for, an Imbens-Manski interval from a controversy-level bootstrap; the
breakdown ``rho`` of those stratified bounds; and the prediction-trimmed
estimate from a noisy strength score ``θ + N(0, proxy_sd)``, which never sees
the administration.

**Scenarios.** :data:`SCENARIOS` holds the sweep: a baseline (50
controversies a side, about the observed emergency docket's scale),
anticipation (filing tracks a perceived favorability the Court does not
have), signal-dominated filing (A2 fails), precedent-averse filing, a pool
shift (A1 fails), and the baseline and the pool shift again at 5,000
controversies a side, where sampling noise is small and what is left is
identification. Coverage is what each run measures, not a property the
scenario guarantees: a failed assumption shows where it moves the bounds off
the truth. The truth is always defined on the unshifted pool, which is side
B's. :func:`attenuation_series` holds the
true effects fixed and sweeps one side's perceived favorability.

Seeded and deterministic: the same seed, runs and draws give the same report.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Final

from pydantic import BaseModel, ConfigDict

from .selection_bounds import (
    Interval,
    OrderRecord,
    cluster_bootstrap,
    imbens_manski_interval,
    manski_bounds,
    monotone_bounds,
    prediction_trimmed_rate,
    side_counts,
    stratified_breakdown_rho,
    stratified_lee_gap,
    trimming_share,
)

#: The two sides every scenario compares; gaps are ``rate(A) - rate(B)``.
SIDE_A: Final[str] = "a"
SIDE_B: Final[str] = "b"

#: Reference-pool size for computing a scenario's true comparable-case gap.
REFERENCE_ORDERS: Final[int] = 100_000

#: Perceived-favorability values the attenuation series sweeps for side A.
ATTENUATION_PERCEIVED: Final[tuple[float, ...]] = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5)


@dataclass(frozen=True)
class SideParams:
    """One side's parameters: the Court's true treatment, its own beliefs, and its filing costs."""

    true_effect: float = 0.0
    perceived_effect: float = 0.0
    signal: float = 0.0
    base_cost: float = 1.0
    broad_cost: float = 0.0
    pool_shift: float = 0.0


@dataclass(frozen=True)
class Scenario:
    """A named data-generating process."""

    name: str
    description: str
    a: SideParams = field(default_factory=SideParams)
    b: SideParams = field(default_factory=SideParams)
    controversies_per_side: int = 50
    mean_orders: float = 1.5
    controversy_sd: float = 1.0
    order_sd: float = 0.5
    salient_share: float = 0.3
    broad_share: float = 0.3
    kappa: float = 0.1
    signal_heterogeneous: bool = False
    proxy_sd: float = 0.5
    bootstrap: bool = True


_BASE_A: Final = SideParams(true_effect=0.5, perceived_effect=0.5)
_BASE_B: Final = SideParams(true_effect=0.0, perceived_effect=0.0)
_SHIFTED_A: Final = SideParams(true_effect=0.5, perceived_effect=0.5, pool_shift=2.0)

#: The scenario sweep. Side A is the favored administration in every scenario
#: but anticipation, where the Court treats both alike.
SCENARIOS: Final[tuple[Scenario, ...]] = (
    Scenario(
        name="baseline",
        description=(
            "A is favored (true log-odds gap 0.5) and both sides know it; "
            "no signal or precedent terms"
        ),
        a=_BASE_A,
        b=_BASE_B,
    ),
    Scenario(
        name="anticipation",
        description="The Court treats both alike, but A believes it is favored by 1.0 log-odds",
        a=SideParams(true_effect=0.0, perceived_effect=1.0),
        b=SideParams(true_effect=0.0, perceived_effect=0.0),
    ),
    Scenario(
        name="signal-dominated",
        description=(
            "As baseline, but both sides gain signal value on salient controversies, "
            "drawn independently for each side and order (A2 fails)"
        ),
        a=SideParams(true_effect=0.5, perceived_effect=0.5, signal=0.6),
        b=SideParams(true_effect=0.0, perceived_effect=0.0, signal=0.6),
        signal_heterogeneous=True,
    ),
    Scenario(
        name="precedent-averse",
        description=(
            "As baseline, but both sides bear an extra precedent cost on broad legal theories"
        ),
        a=SideParams(true_effect=0.5, perceived_effect=0.5, broad_cost=1.0),
        b=SideParams(true_effect=0.0, perceived_effect=0.0, broad_cost=1.0),
    ),
    Scenario(
        name="pool-shift",
        description=(
            "As baseline, but A's adverse orders are stronger for the government by 2.0 "
            "log-odds (A1 fails)"
        ),
        a=_SHIFTED_A,
        b=_BASE_B,
    ),
    Scenario(
        name="sample-large",
        description=(
            "Baseline at 5,000 controversies a side (10,000 in all), against baseline's 50 a side"
        ),
        a=_BASE_A,
        b=_BASE_B,
        controversies_per_side=5_000,
        bootstrap=False,
    ),
    Scenario(
        name="pool-shift-large",
        description="The pool shift at 5,000 controversies a side",
        a=_SHIFTED_A,
        b=_BASE_B,
        controversies_per_side=5_000,
        bootstrap=False,
    ),
)


class FilingScenarioResult(BaseModel):
    """One scenario's results, averaged over its runs."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    runs: int
    controversies_per_side: int
    true_gap: float | None
    always_filer_share: float
    mean_filing_share_a: float
    mean_filing_share_b: float
    mean_naive_gap: float | None
    mean_tier3_lower: float | None
    mean_tier3_upper: float | None
    mean_tier3_width: float | None
    tier3_coverage: float | None
    tier3_defined_runs: int
    ci_coverage: float | None
    ci_defined_runs: int
    tier1_coverage_a: float | None
    tier1_coverage_b: float | None
    tier2_coverage_a: float | None
    tier2_coverage_b: float | None
    mean_breakdown_rho: float | None
    mean_prediction_trimmed_error: float | None
    mean_salient_filed_minus_pool_a: float | None
    mean_broad_filed_minus_pool_a: float | None


class AttenuationPoint(BaseModel):
    """One point of the attenuation series: A's perceived favorability against the gaps."""

    model_config = ConfigDict(extra="forbid")

    perceived_effect_a: float
    true_gap: float | None
    mean_naive_gap: float | None


class FilingSimulationReport(BaseModel):
    """The simulation study's report."""

    model_config = ConfigDict(extra="forbid")

    seed: int
    runs: int
    bootstrap_draws: int
    level: float
    reference_orders: int
    scenarios: list[FilingScenarioResult]
    attenuation: list[AttenuationPoint]


def _expit(x: float) -> float:
    if x >= 0.0:
        return 1.0 / (1.0 + math.exp(-x))
    z = math.exp(x)
    return z / (1.0 + z)


def _logistic_noise(rng: random.Random) -> float:
    u = rng.random()
    while u <= 0.0:
        u = rng.random()
    return math.log(u / (1.0 - u))


def _files(
    side: SideParams,
    theta: float,
    salient: bool,
    broad: bool,
    noise: float,
    signal_scale: float,
    kappa: float,
) -> bool:
    perceived = _expit(theta + side.perceived_effect)
    cost = side.base_cost + (side.broad_cost if broad else 0.0)
    signal = side.signal * signal_scale if salient else 0.0
    return perceived * (1.0 + cost) - cost + signal + kappa * noise > 0.0


def _signal_scale(scenario: Scenario, rng: random.Random) -> float:
    return rng.expovariate(1.0) if scenario.signal_heterogeneous else 1.0


@dataclass(frozen=True)
class Truth:
    """A scenario's true comparable-case gap and the always-filer share of the reference pool."""

    gap: float | None
    always_filer_share: float


def true_gap(scenario: Scenario, rng: random.Random, orders: int = REFERENCE_ORDERS) -> Truth:
    """The comparable-case gap on a reference pool with no pool shift."""
    sd = math.hypot(scenario.controversy_sd, scenario.order_sd)
    total = 0.0
    always = 0
    for _ in range(orders):
        theta = rng.gauss(0.0, sd)
        salient = rng.random() < scenario.salient_share
        broad = rng.random() < scenario.broad_share
        noise = _logistic_noise(rng)
        files_a = _files(
            scenario.a, theta, salient, broad, noise, _signal_scale(scenario, rng), scenario.kappa
        )
        files_b = _files(
            scenario.b, theta, salient, broad, noise, _signal_scale(scenario, rng), scenario.kappa
        )
        if files_a and files_b:
            always += 1
            total += _expit(theta + scenario.a.true_effect) - _expit(theta + scenario.b.true_effect)
    return Truth(gap=total / always if always else None, always_filer_share=always / orders)


@dataclass(frozen=True)
class SimulatedOrder:
    """One simulated adverse order, with the truths a run checks against."""

    record: OrderRecord
    theta: float
    true_rate: float
    salient: bool
    broad: bool


def simulate_side(
    scenario: Scenario, side_name: str, side: SideParams, rng: random.Random
) -> list[SimulatedOrder]:
    """One side's pool of adverse orders, filed and decided by the scenario's rule."""
    orders: list[SimulatedOrder] = []
    extra_p = min(1.0, max(0.0, (scenario.mean_orders - 1.0) / 4.0))
    for index in range(scenario.controversies_per_side):
        controversy = f"{side_name}-{index}"
        effect = rng.gauss(0.0, scenario.controversy_sd)
        salient = rng.random() < scenario.salient_share
        broad = rng.random() < scenario.broad_share
        count = 1 + (rng.binomialvariate(4, extra_p) if extra_p > 0.0 else 0)
        for _ in range(count):
            theta = side.pool_shift + effect + rng.gauss(0.0, scenario.order_sd)
            rate = _expit(theta + side.true_effect)
            filed = _files(
                side,
                theta,
                salient,
                broad,
                _logistic_noise(rng),
                _signal_scale(scenario, rng),
                scenario.kappa,
            )
            won = (rng.random() < rate) if filed else None
            record = OrderRecord(
                side=side_name,
                stratum=(salient, broad),
                controversy=controversy,
                decided=filed,
                won=won,
                score=theta + rng.gauss(0.0, scenario.proxy_sd),
            )
            orders.append(SimulatedOrder(record, theta, rate, salient, broad))
    return orders


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _share(hits: Sequence[bool]) -> float | None:
    return sum(hits) / len(hits) if hits else None


def _filed_minus_pool(orders: Sequence[SimulatedOrder], flag: str) -> float | None:
    pool = [order.theta for order in orders if getattr(order, flag)]
    filed = [order.theta for order in orders if getattr(order, flag) and order.record.decided]
    if not pool or not filed:
        return None
    return sum(filed) / len(filed) - sum(pool) / len(pool)


def _prediction_trimmed_gap(records: Sequence[OrderRecord]) -> float | None:
    a = side_counts(record for record in records if record.side == SIDE_A)
    b = side_counts(record for record in records if record.side == SIDE_B)
    q_a, q_b, r_a, r_b = a.filing_share, b.filing_share, a.win_rate, b.win_rate
    if q_a is None or q_b is None or r_a is None or r_b is None:
        return None
    if q_a >= q_b:
        rate = prediction_trimmed_rate(
            [r for r in records if r.side == SIDE_A], trimming_share(q_a, q_b)
        )
        return None if rate is None else rate - r_b
    rate = prediction_trimmed_rate(
        [r for r in records if r.side == SIDE_B], trimming_share(q_b, q_a)
    )
    return None if rate is None else r_a - rate


def _stratified_statistic(records: list[OrderRecord]) -> Interval | None:
    return stratified_lee_gap(records, SIDE_A, SIDE_B).gap


@dataclass
class _RunTally:
    """Per-run values for one scenario, before averaging."""

    filing_a: list[float] = field(default_factory=list)
    filing_b: list[float] = field(default_factory=list)
    naive: list[float] = field(default_factory=list)
    lower: list[float] = field(default_factory=list)
    upper: list[float] = field(default_factory=list)
    covered: list[bool] = field(default_factory=list)
    ci_covered: list[bool] = field(default_factory=list)
    tier1_a: list[bool] = field(default_factory=list)
    tier1_b: list[bool] = field(default_factory=list)
    tier2_a: list[bool] = field(default_factory=list)
    tier2_b: list[bool] = field(default_factory=list)
    breakdown: list[float] = field(default_factory=list)
    trimmed_error: list[float] = field(default_factory=list)
    salient_shift: list[float] = field(default_factory=list)
    broad_shift: list[float] = field(default_factory=list)


def _record_pool_bounds(
    orders: Sequence[SimulatedOrder], tier1: list[bool], tier2: list[bool]
) -> None:
    counts = side_counts(order.record for order in orders)
    q, r = counts.filing_share, counts.win_rate
    if q is None or r is None:
        return
    target = sum(order.true_rate for order in orders) / len(orders)
    tier1.append(manski_bounds(r, q).contains(target))
    tier2.append(monotone_bounds(r, q).contains(target))


def run_scenario(
    scenario: Scenario,
    *,
    runs: int,
    bootstrap_draws: int,
    level: float,
    seed: int,
    reference_orders: int = REFERENCE_ORDERS,
) -> FilingScenarioResult:
    """Simulate one scenario ``runs`` times and average what each run records."""
    rng = random.Random(f"{seed}:{scenario.name}")
    truth = true_gap(scenario, rng, reference_orders)
    tally = _RunTally()
    for index in range(runs):
        orders_a = simulate_side(scenario, SIDE_A, scenario.a, rng)
        orders_b = simulate_side(scenario, SIDE_B, scenario.b, rng)
        records = [order.record for order in orders_a + orders_b]
        counts_a = side_counts(order.record for order in orders_a)
        counts_b = side_counts(order.record for order in orders_b)
        if counts_a.filing_share is not None:
            tally.filing_a.append(counts_a.filing_share)
        if counts_b.filing_share is not None:
            tally.filing_b.append(counts_b.filing_share)
        _record_pool_bounds(orders_a, tally.tier1_a, tally.tier2_a)
        _record_pool_bounds(orders_b, tally.tier1_b, tally.tier2_b)
        if counts_a.win_rate is None or counts_b.win_rate is None:
            continue
        tally.naive.append(counts_a.win_rate - counts_b.win_rate)
        salient_shift = _filed_minus_pool(orders_a, "salient")
        if salient_shift is not None:
            tally.salient_shift.append(salient_shift)
        broad_shift = _filed_minus_pool(orders_a, "broad")
        if broad_shift is not None:
            tally.broad_shift.append(broad_shift)
        trimmed = _prediction_trimmed_gap(records)
        if trimmed is not None and truth.gap is not None:
            tally.trimmed_error.append(trimmed - truth.gap)
        bounds = stratified_lee_gap(records, SIDE_A, SIDE_B).gap
        if bounds is None:
            continue
        tally.lower.append(bounds.lower)
        tally.upper.append(bounds.upper)
        breakdown = stratified_breakdown_rho(records, SIDE_A, SIDE_B)
        if breakdown is not None:
            tally.breakdown.append(breakdown)
        if truth.gap is not None:
            tally.covered.append(bounds.contains(truth.gap))
        if scenario.bootstrap and bootstrap_draws > 0 and truth.gap is not None:
            se_lower, se_upper, usable = cluster_bootstrap(
                records,
                _stratified_statistic,
                draws=bootstrap_draws,
                rng=random.Random(f"{seed}:{scenario.name}:bootstrap:{index}"),
            )
            if usable >= 2:
                interval = imbens_manski_interval(bounds, se_lower, se_upper, level)
                tally.ci_covered.append(interval.contains(truth.gap))
    widths = [upper - lower for lower, upper in zip(tally.lower, tally.upper, strict=True)]
    return FilingScenarioResult(
        name=scenario.name,
        description=scenario.description,
        runs=runs,
        controversies_per_side=scenario.controversies_per_side,
        true_gap=truth.gap,
        always_filer_share=truth.always_filer_share,
        mean_filing_share_a=_mean(tally.filing_a) or 0.0,
        mean_filing_share_b=_mean(tally.filing_b) or 0.0,
        mean_naive_gap=_mean(tally.naive),
        mean_tier3_lower=_mean(tally.lower),
        mean_tier3_upper=_mean(tally.upper),
        mean_tier3_width=_mean(widths),
        tier3_coverage=_share(tally.covered),
        tier3_defined_runs=len(tally.lower),
        ci_coverage=_share(tally.ci_covered),
        ci_defined_runs=len(tally.ci_covered),
        tier1_coverage_a=_share(tally.tier1_a),
        tier1_coverage_b=_share(tally.tier1_b),
        tier2_coverage_a=_share(tally.tier2_a),
        tier2_coverage_b=_share(tally.tier2_b),
        mean_breakdown_rho=_mean(tally.breakdown),
        mean_prediction_trimmed_error=_mean(tally.trimmed_error),
        mean_salient_filed_minus_pool_a=_mean(tally.salient_shift),
        mean_broad_filed_minus_pool_a=_mean(tally.broad_shift),
    )


def attenuation_series(
    *,
    runs: int,
    seed: int,
    reference_orders: int = REFERENCE_ORDERS,
    perceived: Sequence[float] = ATTENUATION_PERCEIVED,
) -> list[AttenuationPoint]:
    """The naive and true gaps as A's perceived favorability rises, true effects at baseline."""
    points: list[AttenuationPoint] = []
    for value in perceived:
        scenario = Scenario(
            name=f"attenuation-{value}",
            description="baseline with A's perceived effect swept",
            a=SideParams(true_effect=_BASE_A.true_effect, perceived_effect=value),
            b=_BASE_B,
            bootstrap=False,
        )
        result = run_scenario(
            scenario,
            runs=runs,
            bootstrap_draws=0,
            level=0.95,
            seed=seed,
            reference_orders=reference_orders,
        )
        points.append(
            AttenuationPoint(
                perceived_effect_a=value,
                true_gap=result.true_gap,
                mean_naive_gap=result.mean_naive_gap,
            )
        )
    return points


def filing_simulation(
    *,
    seed: int = 0,
    runs: int = 200,
    bootstrap_draws: int = 100,
    level: float = 0.95,
    scenarios: Sequence[Scenario] = SCENARIOS,
    reference_orders: int = REFERENCE_ORDERS,
) -> FilingSimulationReport:
    """Run every scenario and the attenuation series."""
    if runs < 1:
        raise ValueError(f"runs must be at least 1; got {runs}")
    if bootstrap_draws < 0:
        raise ValueError(f"bootstrap_draws must be non-negative; got {bootstrap_draws}")
    if not 0.0 < level < 1.0:
        raise ValueError(f"level must lie in (0, 1); got {level}")
    results = [
        run_scenario(
            scenario,
            runs=runs,
            bootstrap_draws=bootstrap_draws,
            level=level,
            seed=seed,
            reference_orders=reference_orders,
        )
        for scenario in scenarios
    ]
    attenuation = attenuation_series(runs=runs, seed=seed, reference_orders=reference_orders)
    return FilingSimulationReport(
        seed=seed,
        runs=runs,
        bootstrap_draws=bootstrap_draws,
        level=level,
        reference_orders=reference_orders,
        scenarios=results,
        attenuation=attenuation,
    )
