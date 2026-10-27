"""Partial-identification bounds for a win rate seen only on the cases a litigant chose to bring.

Analytics only: nothing here reads the corpus or reaches a cell. The functions
are pure, take counts or plain records, and are the estimators the
selection-adjusted executive success analysis and its simulation study
(:mod:`.filing_simulation`) both call.

**The problem.** A side's win rate is observed only on the adverse orders it
brought to the Court and the Court decided. Which orders those are depends on
how strong the side thought each one was, so the observed rate is a selected
rate. With ``q`` the share of a side's pool of adverse orders that reached a
substantive decision and ``r`` its win rate among them, the quantities of
interest are partially identified, and every function here returns an
interval rather than a point.

``q`` counts only decided filings. A withdrawn, mooted or still-pending
application is a filing whose outcome was not observed, so for these bounds it
sits with the unfiled orders: an unobserved outcome is unobserved whatever
stopped it.

**Tier 1, no assumption (Manski).** The pool-level win rate ``P``, had every
adverse order been decided, lies in ``[r·q, r·q + (1 - q)]``: the unobserved
share could all have been losses or all wins.

**Tier 2, monotone selection.** If decided filings are at least as strong as
the rest, the unobserved share wins no more often than ``r``, and ``P`` lies in
``[r·q, r]``.

**Tier 3, Lee trimming.** For two sides a and b, the comparable-case gap ``Δ``
is the difference in win rates among the cases *both* would have brought (the
always-filers). Under A1 (the two pools have the same distribution of case
strength) and A2 (whatever the more selective side brings, the less selective
side brings too), the more selective side's decided filings are all
always-filers, and a share ``π = (q_high - q_low) / q_high`` of the other side's
are marginal. Trimming ``π`` of the less selective side's decided filings,
wins first or losses first, bounds its always-filer rate in
``[max(0, r - π) / (1 - π), min(1, r / (1 - π))]``, and subtracting the other
side's observed rate bounds ``Δ``.

**Strata.** A1 and A2 are more plausible within strata (issue, policy
direction, order type, salience band), so :func:`stratified_lee_gap` computes
the tier 3 bounds in each stratum and averages them with weights proportional
to the stratum's always-filer count, ``q_low x (combined pool)``. Those weights
make the average the always-filer gap over all strata rather than a pool-weighted
mix of stratum gaps. A stratum where either side has no pool, or no decided
filing, identifies nothing and is reported as skipped.

**Sensitivity to A1 (rho).** :func:`lee_gap` takes ``rho``: up to that share of
*each* side's decided filings may be cases outside the comparable set, beyond
the ``π`` A1 implies. The less selective side is trimmed by ``π + rho``, the
other by ``rho``, and the bounds widen monotonically in ``rho``.
:func:`breakdown_rho` finds the smallest ``rho`` at which the bounds on ``Δ``
include zero (the breakdown point, in Masten and Poirier's sense).

**Inference.** :func:`imbens_manski_interval` covers the partially identified
parameter at a nominal level from the interval's estimate and the standard
errors of its two ends, which :func:`cluster_bootstrap` estimates by
resampling whole controversies within each side, so repeated litigation over
one policy is one draw.

**Prediction trimming.** Where a score ranks cases by predicted strength,
:func:`prediction_trimmed_rate` drops the ``π`` lowest-scored decided filings
instead of trimming by outcome. Under a threshold filing rule the marginal
filings are the weakest, so this is close to a point estimate; it is valid
only as far as the score ranks strength correctly, and is reported beside the
outcome-trimmed bounds, never in place of them.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Sequence
from dataclasses import dataclass
from typing import Final

#: How close :func:`breakdown_rho` brackets the breakdown point.
_BREAKDOWN_TOLERANCE: Final[float] = 1e-6


@dataclass(frozen=True)
class Interval:
    """A closed interval ``[lower, upper]`` on a rate or a difference of rates."""

    lower: float
    upper: float

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError(f"an interval's lower end {self.lower} exceeds its upper {self.upper}")

    @property
    def width(self) -> float:
        """The interval's width."""
        return self.upper - self.lower

    def contains(self, value: float) -> bool:
        """Whether ``value`` lies in the closed interval."""
        return self.lower <= value <= self.upper


@dataclass(frozen=True)
class SideCounts:
    """One side's pool of adverse orders: its size, its decided filings and their wins."""

    pool: int
    decided: int
    wins: int

    def __post_init__(self) -> None:
        if not 0 <= self.wins <= self.decided <= self.pool:
            raise ValueError(
                f"counts need 0 <= wins <= decided <= pool; got wins={self.wins}, "
                f"decided={self.decided}, pool={self.pool}"
            )

    @property
    def filing_share(self) -> float | None:
        """``q``: the share of the pool that reached a substantive decision."""
        return self.decided / self.pool if self.pool else None

    @property
    def win_rate(self) -> float | None:
        """``r``: the win rate among decided filings."""
        return self.wins / self.decided if self.decided else None


@dataclass(frozen=True)
class OrderRecord:
    """One adverse order, as the stratified and bootstrapped estimators read it.

    ``side`` names the administration (or other group) the order belongs to;
    ``won`` is the side's result where the Court decided it and ``None``
    otherwise; ``score`` is an optional predicted strength.
    """

    side: str
    stratum: Hashable
    controversy: Hashable
    decided: bool
    won: bool | None = None
    score: float | None = None

    def __post_init__(self) -> None:
        if self.decided != (self.won is not None):
            raise ValueError("a decided order carries a result, and an undecided one does not")


@dataclass(frozen=True)
class LeeGap:
    """Tier 3 bounds on the comparable-case gap ``rate(a) - rate(b)``.

    ``less_selective`` names the side trimmed by ``π`` (``None`` when the two
    filing shares are equal and neither is trimmed beyond ``rho``).
    """

    gap: Interval
    trimming_share: float
    less_selective: str | None
    rho: float


@dataclass(frozen=True)
class StratumGap:
    """One stratum's tier 3 bounds and its weight in the average."""

    stratum: Hashable
    a: SideCounts
    b: SideCounts
    lee: LeeGap
    weight: float


@dataclass(frozen=True)
class StratifiedGap:
    """Tier 3 bounds averaged over strata, with the strata that identified nothing."""

    gap: Interval | None
    strata: tuple[StratumGap, ...]
    skipped: tuple[Hashable, ...]


def _check_share(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1]; got {value}")


def manski_bounds(win_rate: float, filing_share: float) -> Interval:
    """Tier 1: bounds on the pool-level win rate with no assumption on unfiled orders."""
    _check_share("win_rate", win_rate)
    _check_share("filing_share", filing_share)
    observed = win_rate * filing_share
    return Interval(observed, observed + (1.0 - filing_share))


def monotone_bounds(win_rate: float, filing_share: float) -> Interval:
    """Tier 2: bounds on the pool-level win rate when filed orders are at least as strong."""
    _check_share("win_rate", win_rate)
    _check_share("filing_share", filing_share)
    return Interval(win_rate * filing_share, win_rate)


def trimming_share(q_high: float, q_low: float) -> float:
    """``π``: the marginal share of the less selective side's decided filings under A1 and A2."""
    _check_share("q_high", q_high)
    _check_share("q_low", q_low)
    if q_low > q_high:
        raise ValueError(f"q_low {q_low} exceeds q_high {q_high}")
    if q_high == 0.0:
        raise ValueError("no decided filing on either side: nothing to trim")
    return (q_high - q_low) / q_high


def trimmed_rate_bounds(win_rate: float, share: float) -> Interval:
    """Bounds on the rate left after trimming ``share`` of decided filings, wins or losses first.

    A ``share`` of 1 or more leaves nothing, and the rate can be anything.
    """
    _check_share("win_rate", win_rate)
    if share < 0.0:
        raise ValueError(f"share must be non-negative; got {share}")
    if share >= 1.0:
        return Interval(0.0, 1.0)
    kept = 1.0 - share
    return Interval(max(0.0, win_rate - share) / kept, min(1.0, win_rate / kept))


def lee_gap(
    a: SideCounts, b: SideCounts, *, rho: float = 0.0, a_name: str = "a", b_name: str = "b"
) -> LeeGap:
    """Tier 3 bounds on the comparable-case gap ``rate(a) - rate(b)``.

    ``rho`` relaxes A1: up to that share of each side's decided filings may lie
    outside the comparable set, beyond the ``π`` the filing shares imply.
    """
    if rho < 0.0:
        raise ValueError(f"rho must be non-negative; got {rho}")
    q_a, q_b, r_a, r_b = a.filing_share, b.filing_share, a.win_rate, b.win_rate
    if q_a is None or q_b is None or r_a is None or r_b is None:
        raise ValueError("each side needs a non-empty pool and at least one decided filing")
    if q_a > q_b:
        less: str | None = a_name
        pi = trimming_share(q_a, q_b)
        a_bounds = trimmed_rate_bounds(r_a, pi + rho)
        b_bounds = trimmed_rate_bounds(r_b, rho)
    elif q_b > q_a:
        less = b_name
        pi = trimming_share(q_b, q_a)
        a_bounds = trimmed_rate_bounds(r_a, rho)
        b_bounds = trimmed_rate_bounds(r_b, pi + rho)
    else:
        less = None
        pi = 0.0
        a_bounds = trimmed_rate_bounds(r_a, rho)
        b_bounds = trimmed_rate_bounds(r_b, rho)
    gap = Interval(a_bounds.lower - b_bounds.upper, a_bounds.upper - b_bounds.lower)
    return LeeGap(gap=gap, trimming_share=pi, less_selective=less, rho=rho)


def breakdown_rho(a: SideCounts, b: SideCounts) -> float:
    """The smallest ``rho`` at which the tier 3 bounds on ``rate(a) - rate(b)`` include zero.

    Zero when the A1 bounds already include it. The bounds widen
    monotonically in ``rho`` and reach ``[-1, 1]`` at ``rho = 1``, so a breakdown
    point always exists; it is bracketed by bisection.
    """
    if lee_gap(a, b).gap.contains(0.0):
        return 0.0
    low, high = 0.0, 1.0
    while high - low > _BREAKDOWN_TOLERANCE:
        mid = (low + high) / 2.0
        if lee_gap(a, b, rho=mid).gap.contains(0.0):
            high = mid
        else:
            low = mid
    return high


def side_counts(records: Iterable[OrderRecord]) -> SideCounts:
    """Pool, decided and win counts over one side's records."""
    pool = decided = wins = 0
    for record in records:
        pool += 1
        if record.decided:
            decided += 1
            wins += bool(record.won)
    return SideCounts(pool=pool, decided=decided, wins=wins)


def stratified_lee_gap(
    records: Iterable[OrderRecord], a: str, b: str, *, rho: float = 0.0
) -> StratifiedGap:
    """Tier 3 bounds on ``rate(a) - rate(b)`` within strata, averaged by always-filer weight."""
    by_stratum: dict[Hashable, dict[str, list[OrderRecord]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for record in records:
        if record.side in (a, b):
            by_stratum[record.stratum][record.side].append(record)
    strata: list[StratumGap] = []
    skipped: list[Hashable] = []
    for stratum in sorted(by_stratum, key=repr):
        a_counts = side_counts(by_stratum[stratum][a])
        b_counts = side_counts(by_stratum[stratum][b])
        if not (a_counts.decided and b_counts.decided):
            skipped.append(stratum)
            continue
        lee = lee_gap(a_counts, b_counts, rho=rho, a_name=a, b_name=b)
        q_low = min(a_counts.decided / a_counts.pool, b_counts.decided / b_counts.pool)
        weight = q_low * (a_counts.pool + b_counts.pool)
        strata.append(StratumGap(stratum=stratum, a=a_counts, b=b_counts, lee=lee, weight=weight))
    total = sum(item.weight for item in strata)
    gap = (
        Interval(
            sum(item.weight * item.lee.gap.lower for item in strata) / total,
            sum(item.weight * item.lee.gap.upper for item in strata) / total,
        )
        if total > 0.0
        else None
    )
    return StratifiedGap(gap=gap, strata=tuple(strata), skipped=tuple(skipped))


def prediction_trimmed_rate(records: Sequence[OrderRecord], share: float) -> float | None:
    """The win rate after dropping the ``share`` lowest-scored decided filings.

    The number dropped is ``share x decided``, rounded to the nearest whole
    filing; ties in score keep the input order. ``None`` when nothing decided
    is left. Every decided record must carry a score.
    """
    if not 0.0 <= share <= 1.0:
        raise ValueError(f"share must lie in [0, 1]; got {share}")
    decided = [record for record in records if record.decided]
    if any(record.score is None for record in decided):
        raise ValueError("prediction trimming needs a score on every decided filing")
    ranked = sorted(decided, key=lambda record: record.score or 0.0)
    kept = ranked[round(share * len(ranked)) :]
    if not kept:
        return None
    return sum(bool(record.won) for record in kept) / len(kept)


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def imbens_manski_critical_value(width: float, sigma: float, level: float = 0.95) -> float:
    """``C``, solving ``Φ(C + width / sigma) - Φ(-C) = level``.

    It runs from the one-sided quantile when the interval is wide relative to
    its noise to the two-sided one when it collapses to a point.
    """
    if not 0.0 < level < 1.0:
        raise ValueError(f"level must lie in (0, 1); got {level}")
    if sigma <= 0.0:
        raise ValueError(f"sigma must be positive; got {sigma}")
    ratio = width / sigma
    low, high = 0.0, 10.0
    for _ in range(200):
        mid = (low + high) / 2.0
        if _normal_cdf(mid + ratio) - _normal_cdf(-mid) < level:
            low = mid
        else:
            high = mid
    return high


def imbens_manski_interval(
    estimate: Interval, se_lower: float, se_upper: float, level: float = 0.95
) -> Interval:
    """A confidence interval covering the partially identified parameter at ``level``.

    With both standard errors zero there is no sampling noise to cover, and the
    estimate is returned.
    """
    if se_lower < 0.0 or se_upper < 0.0:
        raise ValueError("standard errors must be non-negative")
    sigma = max(se_lower, se_upper)
    if sigma == 0.0:
        return estimate
    critical = imbens_manski_critical_value(estimate.width, sigma, level)
    return Interval(estimate.lower - critical * se_lower, estimate.upper + critical * se_upper)


def _sd(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def cluster_bootstrap(
    records: Sequence[OrderRecord],
    statistic: Callable[[list[OrderRecord]], Interval | None],
    *,
    draws: int,
    rng: random.Random,
) -> tuple[float, float, int]:
    """Standard errors of an interval statistic's two ends, resampling controversies.

    Controversies are drawn with replacement within each side, so each side
    keeps its number of controversies and a controversy's orders travel
    together. A draw on which the statistic is undefined is dropped. Returns
    ``(se_lower, se_upper, usable_draws)``.
    """
    if draws < 0:
        raise ValueError(f"draws must be non-negative; got {draws}")
    clusters: dict[str, dict[Hashable, list[OrderRecord]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        clusters[record.side][record.controversy].append(record)
    groups = [list(by_controversy.values()) for _, by_controversy in sorted(clusters.items())]
    lowers: list[float] = []
    uppers: list[float] = []
    for _ in range(draws):
        sample: list[OrderRecord] = []
        for group in groups:
            for _ in range(len(group)):
                sample.extend(group[rng.randrange(len(group))])
        result = statistic(sample)
        if result is not None:
            lowers.append(result.lower)
            uppers.append(result.upper)
    return _sd(lowers), _sd(uppers), len(lowers)
