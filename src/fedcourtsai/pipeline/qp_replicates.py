"""How far one topic labeler's agreement moves between runs on identical inputs.

A single labeling run's agreement with the reference block may carry a
run-level component the binomial error at the block's ``n`` does not capture
(``docs/qp-topic.md``).
The replicate mode measures that directly. Each replicate labels the frame's
reference rows alone and publishes nothing, and its run record carries which
reference rows it matched (:class:`~fedcourtsai.schemas.QpTopicReplicate`).
This module reads k such match vectors over the same items and separates the
spread of the run rates into its two sources:

- **item-level noise** — an item the labeler calls one way on some runs and the
  other way on others moves each run's rate by ``1/n`` independently of every
  other item. Were that the only source, the run rate's variance would be
  ``sum(p_i (1 - p_i)) / n^2``, with ``p_i`` item ``i``'s match probability,
  estimated without bias by ``k/(k-1) * p̂_i (1 - p̂_i)`` from the k runs;
- **a run-level component** — whatever moves every item of one run together
  (the session's reading of a rule, a drifting prompt, a model-side change). Its
  variance is the run rates' sample variance less the item-level term. Item
  main effects cancel from the run means because every run reads the same
  items, so this is the crossed items x runs analysis of variance estimator up
  to a factor ``(n-1)/n`` (the item term absorbs ``1/n`` of any run effect),
  which is negligible at the block sizes here.

Two assumptions bound what the split means. It is **linear on the probability
scale**: a run effect cannot move an item every run matches, so "run-level" is
a component of this block's agreement, not a property of the labeler on other
items. And it treats items as **independent within a run**: a labeler that
reads its rows in chunks or shared contexts puts any chunk effect in the
run-level bucket. Replicates pool only under one reference file and one
labeling prompt, since a revision of either would land there too.

Cochran's Q tests the null of no run effect (equal match probability across
runs) on the same table. With few replicates the run sd itself is imprecise —
its chi-square interval on ``k - 1`` degrees of freedom is printed beside it —
and the binomial error at ``n`` is a different estimand (item sampling: how far
this block's rate stands from a frame's), so it is printed apart, never as a
component of one total. All of it is descriptive input to a variance-aware
gate not yet pre-registered; nothing here chooses a floor.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from ..schemas import QpTopicRunSpend

#: Iteration cap and tolerance for the regularized incomplete gamma below.
_GAMMA_ITERATIONS = 500
_GAMMA_EPSILON = 1e-15
_TINY = 1e-300


class ReplicateError(ValueError):
    """The replicates cannot be pooled as given."""


@dataclass(frozen=True)
class Replicate:
    """One run's match vector over the reference, in reference ``case_id`` order.

    ``matches`` is the run record's string — ``1`` matched, ``0`` did not, ``-``
    not compared. ``kinds`` names each position's application input kind (empty
    on the petition frame). ``unclassifiable`` counts compared positions the run
    labeled ``unclassifiable``.
    """

    name: str
    matches: str
    unclassifiable: int
    kinds: tuple[str, ...] = ()
    #: The labeling prompt's sha256, where the run recorded one (saved labels do not).
    prompt_sha256: str | None = None


@dataclass(frozen=True)
class KindSpread:
    """The run rates on one application input kind."""

    kind: str
    n: int
    rates: tuple[float, ...]
    mean: float
    sd: float | None
    floor: float | None = None


@dataclass(frozen=True)
class ReplicateSpread:
    """The spread of k replicates' agreement over the items all of them compared."""

    names: tuple[str, ...]
    items: int
    rates: tuple[float, ...]
    mean: float
    run_sd: float
    item_noise_var: float
    run_component_var: float
    binomial_sd: float
    always: int
    never: int
    flip: int
    cochran_q: float | None
    p_value: float | None
    unclassifiable_shares: tuple[float, ...]
    per_kind: tuple[KindSpread, ...] = field(default_factory=tuple)
    #: The constant-labeler floor on the shared items: the largest reference
    #: class's share, which every rate here has to be read against.
    floor: float | None = None
    #: The run sd's 95% interval from the chi-square on ``k - 1`` df.
    run_sd_interval: tuple[float, float] | None = None

    @property
    def runs(self) -> int:
        """How many replicates were pooled."""
        return len(self.rates)

    @property
    def item_noise_sd(self) -> float:
        """The run rate's standard deviation were item-level noise its only source."""
        return math.sqrt(self.item_noise_var)

    @property
    def run_component_sd(self) -> float:
        """The run-level component's standard deviation, truncated at zero."""
        return math.sqrt(max(self.run_component_var, 0.0))

    @property
    def predictive_sd(self) -> float:
        """A next run's rate around ``mean``: ``run_sd * sqrt(1 + 1/k)``.

        The run rates' own sample spread with the uncertainty in ``mean`` added,
        on the same block of items; it is what a per-run floor would have to
        clear, and it says nothing about items the block does not hold.
        """
        return self.run_sd * math.sqrt(1 + 1 / self.runs)

    def as_json(self) -> dict[str, object]:
        """The spread as a JSON document, every derived figure included."""
        return {
            "runs": self.runs,
            "names": list(self.names),
            "items": self.items,
            "rates": list(self.rates),
            "mean": self.mean,
            "run_sd": self.run_sd,
            "predictive_sd": self.predictive_sd,
            "item_noise_sd": self.item_noise_sd,
            "run_component_var": self.run_component_var,
            "run_component_sd": self.run_component_sd,
            "binomial_sd": self.binomial_sd,
            "floor": self.floor,
            "run_sd_interval": list(self.run_sd_interval) if self.run_sd_interval else None,
            "always": self.always,
            "never": self.never,
            "flip": self.flip,
            "cochran_q": self.cochran_q,
            "cochran_df": self.runs - 1,
            "p_value": self.p_value,
            "unclassifiable_shares": list(self.unclassifiable_shares),
            "per_input_kind": [
                {
                    "input_kind": k.kind,
                    "n": k.n,
                    "rates": list(k.rates),
                    "mean": k.mean,
                    "sd": k.sd,
                    "floor": k.floor,
                }
                for k in self.per_kind
            ],
        }


def chi2_sf(statistic: float, df: int) -> float:
    """The chi-square survival function, ``P(X >= statistic)`` on ``df`` degrees of freedom.

    The regularized upper incomplete gamma ``Q(df/2, statistic/2)``: the series
    for the lower function below ``a + 1`` and Lentz's continued fraction above
    it, the standard pair that each converges fast on its own side.
    """
    if df < 1:
        raise ReplicateError("a chi-square needs at least one degree of freedom")
    if statistic <= 0:
        return 1.0
    a, x = df / 2, statistic / 2
    log_prefix = -x + a * math.log(x) - math.lgamma(a)
    if x < a + 1:
        term = total = 1 / a
        shifted = a
        for _ in range(_GAMMA_ITERATIONS):
            shifted += 1
            term *= x / shifted
            total += term
            if abs(term) < abs(total) * _GAMMA_EPSILON:
                break
        return max(0.0, 1 - total * math.exp(log_prefix))
    b = x + 1 - a
    c = 1 / _TINY
    d = 1 / b
    h = d
    for i in range(1, _GAMMA_ITERATIONS):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = _TINY if abs(d) < _TINY else d
        c = b + an / c
        c = _TINY if abs(c) < _TINY else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < _GAMMA_EPSILON:
            break
    return min(1.0, math.exp(log_prefix) * h)


def chi2_quantile(probability: float, df: int) -> float:
    """The chi-square quantile: ``x`` with ``P(X <= x) = probability``, by bisection on
    :func:`chi2_sf`, which is monotone, to well below any printed precision."""
    if not 0 < probability < 1:
        raise ReplicateError("a quantile's probability lies strictly between 0 and 1")
    low, high = 0.0, max(1.0, float(df))
    while 1 - chi2_sf(high, df) < probability:
        high *= 2
    for _ in range(200):
        middle = (low + high) / 2
        if 1 - chi2_sf(middle, df) < probability:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def _floor(labels: Sequence[str]) -> float | None:
    if not labels:
        return None
    counts: dict[str, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    return max(counts.values()) / len(labels)


def _sample_sd(values: Sequence[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


def spread(
    replicates: Sequence[Replicate], reference_labels: Sequence[str] = ()
) -> ReplicateSpread:
    """Pool k replicates over the reference items every one of them compared.

    ``reference_labels`` is the reference's label per position, in the same
    order; given, the constant-labeler floor is reported on the shared items
    (and per kind). Refuses fewer than two replicates, vectors of different
    lengths (they index different reference files), replicates recorded under
    different labeling prompts, and a pool with no item compared by all.
    """
    if len(replicates) < 2:
        raise ReplicateError("a spread needs at least two replicates")
    length = len(replicates[0].matches)
    if any(len(r.matches) != length for r in replicates):
        raise ReplicateError("the replicates index reference files of different lengths")
    prompts = {r.prompt_sha256 for r in replicates if r.prompt_sha256 is not None}
    if len(prompts) > 1:
        raise ReplicateError("the replicates were recorded under different labeling prompts")
    if reference_labels and len(reference_labels) != length:
        raise ReplicateError("the reference labels do not index the replicates' items")
    kinds = replicates[0].kinds
    if any(r.kinds != kinds for r in replicates):
        raise ReplicateError("the replicates name different input kinds for the same items")
    shared = [i for i in range(length) if all(r.matches[i] != "-" for r in replicates)]
    if not shared:
        raise ReplicateError("no reference item was compared by every replicate")
    k, n = len(replicates), len(shared)
    columns = [sum(r.matches[i] == "1" for i in shared) for r in replicates]
    rows = [sum(r.matches[i] == "1" for r in replicates) for i in shared]
    rates = tuple(c / n for c in columns)
    mean = sum(rates) / k
    run_var = sum((r - mean) ** 2 for r in rates) / (k - 1)
    item_noise_var = sum(k / (k - 1) * (t / k) * (1 - t / k) for t in rows) / n**2
    total = sum(rows)
    denominator = k * total - sum(t * t for t in rows)
    cochran_q: float | None = None
    p_value: float | None = None
    if denominator > 0:
        cochran_q = (k - 1) * (k * sum(c * c for c in columns) - total**2) / denominator
        p_value = chi2_sf(cochran_q, k - 1)
    per_kind: list[KindSpread] = []
    if kinds:
        for kind in sorted(set(kinds)):
            positions = [i for i in shared if kinds[i] == kind]
            if not positions:
                continue
            kind_rates = tuple(
                sum(r.matches[i] == "1" for i in positions) / len(positions) for r in replicates
            )
            per_kind.append(
                KindSpread(
                    kind=kind,
                    n=len(positions),
                    rates=kind_rates,
                    mean=sum(kind_rates) / k,
                    sd=_sample_sd(kind_rates),
                    floor=_floor([reference_labels[i] for i in positions])
                    if reference_labels
                    else None,
                )
            )
    run_sd = math.sqrt(run_var)
    interval = (
        run_sd * math.sqrt((k - 1) / chi2_quantile(0.975, k - 1)),
        run_sd * math.sqrt((k - 1) / chi2_quantile(0.025, k - 1)),
    )
    return ReplicateSpread(
        names=tuple(r.name for r in replicates),
        items=n,
        rates=rates,
        mean=mean,
        run_sd=run_sd,
        item_noise_var=item_noise_var,
        run_component_var=run_var - item_noise_var,
        binomial_sd=math.sqrt(mean * (1 - mean) / n),
        always=sum(1 for t in rows if t == k),
        never=sum(1 for t in rows if t == 0),
        flip=sum(1 for t in rows if 0 < t < k),
        cochran_q=cochran_q,
        p_value=p_value,
        unclassifiable_shares=tuple(
            r.unclassifiable / (length - r.matches.count("-")) for r in replicates
        ),
        per_kind=tuple(per_kind),
        floor=_floor([reference_labels[i] for i in shared]) if reference_labels else None,
        run_sd_interval=interval,
    )


def replicates_from_records(
    runs: Sequence[QpTopicRunSpend],
    *,
    frame: str,
    model: str,
    reference_sha256: str,
    kinds: Sequence[str] = (),
    prompt_sha256: str | None = None,
) -> tuple[list[Replicate], list[tuple[QpTopicRunSpend, str]]]:
    """The frame's replicate records for ``model`` against this reference, and the rest.

    Returns the replicates to pool and the frame's replicate records left out,
    each with why — another model's, one measured against a different reference
    file (its match string indexes other items or another standard), or one
    under another labeling prompt than ``prompt_sha256``. With no
    ``prompt_sha256`` every prompt is kept, and :func:`spread` refuses a pool
    that mixes them. Ordered by run id and attempt so a report lists them the
    same way every time.
    """
    pooled: list[Replicate] = []
    skipped: list[tuple[QpTopicRunSpend, str]] = []
    for run in sorted(runs, key=lambda r: (int(r.run_id), r.run_attempt)):
        if run.frame != frame or run.outcome != "replicate" or run.replicate is None:
            continue
        if run.model != model:
            skipped.append((run, f"labeled by {run.model}"))
            continue
        if run.replicate.reference_sha256 != reference_sha256:
            skipped.append((run, "measured against another reference file"))
            continue
        if prompt_sha256 is not None and run.replicate.prompt_sha256 != prompt_sha256:
            skipped.append((run, "labeled under another prompt"))
            continue
        pooled.append(
            Replicate(
                name=f"run {run.run_id}-{run.run_attempt}",
                matches=run.replicate.matches,
                unclassifiable=run.replicate.unclassifiable,
                kinds=tuple(kinds),
                prompt_sha256=run.replicate.prompt_sha256,
            )
        )
    return pooled, skipped


def replicate_from_labels(
    name: str,
    labels: Mapping[str, str],
    reference: Sequence[tuple[str, str, str]],
) -> Replicate:
    """A replicate read off any labeling run's labels, over the reference rows it holds.

    ``reference`` is ``(case_id, label, input_kind)`` in ``case_id`` order
    (``input_kind`` empty on the petition frame). A batch's labels carry rows
    beyond the reference; only reference rows are read, so a past labeling run's
    saved labels pool with replicates on the same items. The caller is
    responsible for the labels having been read from the same reference rows'
    inputs; a reference relabeled after the run scores it against the new
    standard, which is what the report says.
    """
    matches = "".join(
        "-" if case_id not in labels else "1" if labels[case_id] == label else "0"
        for case_id, label, _ in reference
    )
    kinds = tuple(kind for _, _, kind in reference) if any(k for _, _, k in reference) else ()
    return Replicate(
        name=name,
        matches=matches,
        unclassifiable=sum(
            1 for case_id, _, _ in reference if labels.get(case_id) == "unclassifiable"
        ),
        kinds=kinds,
    )


def render_spread(spread_: ReplicateSpread, *, against: str) -> str:
    """The spread report: every figure beside its ``n`` and the sources it separates."""
    lines = [
        f"qp-topic replicates: {spread_.runs} run(s) over {spread_.items} reference item(s) "
        f"compared by all, against {against} — agreement, not accuracy",
    ]
    width = max(len(name) for name in spread_.names)
    for name, rate, share in zip(
        spread_.names, spread_.rates, spread_.unclassifiable_shares, strict=True
    ):
        lines.append(f"  {name:{width}s}  {rate:.1%}  (unclassifiable {share:.1%} of compared)")
    lines += [
        f"  mean:            {spread_.mean:.1%}",
        "  floor:           "
        + ("n/a" if spread_.floor is None else f"{spread_.floor:.1%}")
        + " (a constant labeler on the same items; every rate reads against it)",
        f"  run sd:          {spread_.run_sd:.2%} (sample sd of the run rates, "
        f"{spread_.runs - 1} df"
        + (
            ""
            if spread_.run_sd_interval is None
            else f"; 95% interval {spread_.run_sd_interval[0]:.2%} to "
            f"{spread_.run_sd_interval[1]:.2%}"
        )
        + ")",
        f"  predictive sd:   {spread_.predictive_sd:.2%} (a next run on these items)",
        f"  item-level sd:   {spread_.item_noise_sd:.2%} (the run sd were flipping items "
        "the only source)",
        f"  run-level var:   {spread_.run_component_var:+.6f} "
        f"(sd {spread_.run_component_sd:.2%} truncated at 0; run var less item-level var)",
        f"  binomial sd:     {spread_.binomial_sd:.2%} (sqrt(p(1-p)/n): item-sampling error, "
        "how far this block's rate may stand from a frame's — a different estimand, not a "
        "component of the run sd)",
        f"  items:           {spread_.always} always matched, {spread_.never} never, "
        f"{spread_.flip} flipped between runs",
    ]
    if spread_.cochran_q is None or spread_.p_value is None:
        lines.append("  Cochran's Q:     undefined (no item flipped)")
    else:
        lines.append(
            f"  Cochran's Q:     {spread_.cochran_q:.2f} on {spread_.runs - 1} df, "
            f"p = {spread_.p_value:.4f} (null: no run effect)"
        )
    for kind in spread_.per_kind:
        rates = ", ".join(f"{rate:.1%}" for rate in kind.rates)
        sd = "n/a" if kind.sd is None else f"{kind.sd:.2%}"
        floor = "n/a" if kind.floor is None else f"{kind.floor:.1%}"
        lines.append(
            f"  {kind.kind:17s} n={kind.n}: {rates} (mean {kind.mean:.1%}, sd {sd}, floor {floor})"
        )
    return "\n".join(lines)
