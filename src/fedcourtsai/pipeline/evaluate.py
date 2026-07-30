"""``run-evaluate`` helpers.

Each evaluator scores each predictor's prediction against the realized
``outcome.json``. The qualitative judgment (reasoning quality) is produced by an
agent; the quantitative pieces (correctness, Brier score, and the segment-baseline
skill score) are deterministic and provided here so every evaluator computes them
identically.

This module reads no config. Every tunable — the segment base rate's lookback
window, the claim floor's recent window — arrives as an argument, so the functions
stay pure and a test, a replay cell, and the cert back-test all get the same number
from the same inputs. Config resolves one level out, at the caller.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from enum import StrEnum

from ..corpus import CorpusRow, scotus_term_year
from ..schemas import Outcome, Prediction, ResolutionSignals, StatPack, StatPackTerm
from .salience import salience_band


def is_correct(prediction: Prediction, outcome: Outcome) -> int:
    return int(prediction.predicted_disposition == outcome.actual_disposition)


def brier_score(prediction: Prediction, outcome: Outcome) -> float:
    """Brier score for the binary granted/denied forecast (lower is better)."""
    return (prediction.probability - outcome.actual_granted) ** 2


def segment_base_rate(
    row: CorpusRow, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The leakage-safe salience-segment base rate for a case.

    The case's frozen ``sal-v1`` band's grant rate, pooled over statpack Terms
    **strictly before the case's own Term**. Leakage-safe by construction: only
    Terms preceding the case contribute, so the rate a replay cell anchors on never
    sees the case's own — or any later — Term. Pooled as a resolved-weighted mean of
    the per-Term band rates (each Term's ``est_grant_rate`` weighted by its
    ``weighted_resolved``), which equals the aggregate weighted grants over
    aggregate weighted resolved. ``None`` when the case has no Term, no band data
    precedes it, or nothing in the band resolved.

    ``lookback_terms`` bounds how far back the pool reaches;
    ``0`` (the default, and ``salience.base_rate_lookback_terms``'s shipped value)
    means unbounded — every prior Term, preserving the pre-registered behaviour
    exactly. The bound is a **Term-year band**, ``term - lookback_terms <= entry
    < term``, not a slice of the pack's rows: a Term absent from the statpack, or
    present as a zero-row cursor entry, shortens the sample rather than pulling an
    older Term in to refill the slot. That keeps the window a claim about the
    recency of the Court's behaviour, and keeps it from shifting — silently, and in
    every published skill number — as the walker's coverage changes.
    """
    term = scotus_term_year(row.docket_number)
    if term is None:
        return None
    # `band` and the statpack segments are both `sal-v1` today, so a plain name
    # match is safe. When sal-v2 lands, reconcile the band version with each Term's
    # `salience_version` here — a lagging statpack would otherwise miss silently. A
    # bounded `lookback_terms` limits, but does not fix, that exposure: it caps how
    # far back a stale version can reach, not whether the mismatch is noticed.
    band = salience_band(row)
    # A Term-YEAR floor, not a row count — see the docstring. `0` means no floor;
    # `term - 0` would exclude every Term, so the sentinel must short-circuit. A
    # negative window would read as unbounded-plus-a-Term; `ge=0` guards the config
    # path, and clamping here guards a direct caller.
    oldest = term - lookback_terms if lookback_terms > 0 else None
    weighted_grants = 0.0
    weighted_resolved = 0.0
    for entry in statpack.terms:
        if entry.term >= term:
            continue  # leakage guard: the case's own and later Terms never contribute
        if oldest is not None and entry.term < oldest:
            continue  # outside the configured lookback window
        for seg in entry.segments:
            if seg.band == band and seg.est_grant_rate is not None:
                weighted_grants += seg.est_grant_rate * seg.weighted_resolved
                weighted_resolved += seg.weighted_resolved
    if weighted_resolved == 0:
        return None
    return weighted_grants / weighted_resolved


def brier_skill(brier: float, actual_granted: int, base_rate: float | None) -> float | None:
    """Brier skill of a forecast's ``brier`` vs the naive ``base_rate`` baseline.

    ``1 - brier / baseline_brier``, where the baseline is the forecaster that
    always predicts ``base_rate``. ~0 when the forecast is no better than the base
    rate, positive (up to 1) when better, negative when worse. ``None`` when there
    is no base rate, or when the baseline is already perfect (its Brier is zero —
    ``base_rate`` matched the outcome exactly), where the ratio is undefined. The
    numeric core shared by the evaluate path and the cert back-test.
    """
    if base_rate is None:
        return None
    baseline_brier = (base_rate - actual_granted) ** 2
    if baseline_brier == 0:
        return None
    return 1.0 - brier / baseline_brier


def brier_skill_score(
    prediction: Prediction, outcome: Outcome, base_rate: float | None
) -> float | None:
    """Brier skill score of a prediction vs the segment base rate.

    Convenience wrapper over :func:`brier_skill` for schema objects: scores the
    prediction's Brier against the baseline that always predicts ``base_rate``, so
    parroting the segment's grant rate earns ~0 skill.
    """
    return brier_skill(brier_score(prediction, outcome), outcome.actual_granted, base_rate)


class Claim(StrEnum):
    """A cert-stage proposition that resolves against a committed outcome record.

    A claim carries a predictor's probability and is scored against a baseline the
    harness computes from strictly prior history. These two resolve against
    ``Outcome.signals`` — the docket-progress block frozen at resolution, rather than
    the corpus columns of the same name, which hold the *current* value and would
    make a score irreproducible.
    """

    relisted = "relisted"
    cvsg = "cvsg"


#: The claim set these functions score. Disposition is the third cert-stage claim,
#: but it already has a leakage-safe baseline in :func:`segment_base_rate` and is
#: scored through the headline Brier path, so it is not carried here — scoring it
#: twice would pay one belief twice over.
CERT_SIGNAL_CLAIMS: tuple[Claim, ...] = (Claim.relisted, Claim.cvsg)

#: How each claim reads its truth value off a resolution's frozen signals. A
#: distribution is a consideration, so relists are the count minus one and "relisted
#: at least once" is a count of two or more.
_CLAIM_RESOLVERS: dict[Claim, Callable[[ResolutionSignals], int]] = {
    Claim.relisted: lambda signals: int(signals.distribution_count >= 2),
    Claim.cvsg: lambda signals: int(signals.cvsg_date is not None),
}

#: How each claim reads its ``(rate, weighted denominator)`` off a statpack Term.
_CLAIM_TERM_RATES: dict[Claim, Callable[[StatPackTerm], tuple[float | None, int]]] = {
    Claim.relisted: lambda entry: (entry.est_relist_rate, entry.relist_weighted_resolved),
    Claim.cvsg: lambda entry: (entry.est_cvsg_rate, entry.cvsg_weighted_resolved),
}

#: The floor's recent window, in October Terms. Short enough to track the Court's
#: current practice — the rate a predictor with no case-specific information would
#: actually quote — and long enough that one Term's noise does not set it. It is a
#: different window from the baseline's on purpose: the gap between the two is the
#: free score an uninformed control collects, which is the whole reason a claim
#: total is reported with a floor beside it.
FLOOR_LOOKBACK_TERMS = 5


def resolve_claim(outcome: Outcome, claim: Claim) -> int | None:
    """A claim's realized truth value, or ``None`` when the outcome cannot resolve it.

    ``None`` where ``Outcome.signals`` is absent, which means the proceedings were
    never live-parsed — nothing was observed, as distinct from the signal not having
    happened. An unresolvable claim drops out of the claim set rather than resolving
    false, because a false value there would be a fabricated observation.
    """
    signals = outcome.signals
    if signals is None:
        return None
    return _CLAIM_RESOLVERS[claim](signals)


def claim_base_rate(
    row: CorpusRow, statpack: StatPack, claim: Claim, *, lookback_terms: int = 0
) -> float | None:
    """The leakage-safe baseline probability for one claim on one case.

    The claim's rate over the scored segment, pooled over statpack Terms **strictly
    before the case's own Term** — the same guard, doctrine, and pooling
    :func:`segment_base_rate` uses, so the two baselines cannot disagree about what a
    cell was allowed to know. Pooled as a resolved-weighted mean of the per-Term
    rates (each Term's rate weighted by its own denominator), which equals the
    aggregate weighted positives over aggregate weighted observations. ``None`` when
    the case has no Term, when no Term precedes it, or when nothing resolved.

    ``lookback_terms`` bounds how far back the pool reaches; ``0`` (the default, and
    ``salience.base_rate_lookback_terms``'s shipped value) means unbounded. The bound
    is a **Term-year band**, ``term - lookback_terms <= entry < term``, not a slice of
    the pack's rows: a Term absent from the statpack, or present as a zero-row cursor
    entry, shortens the sample rather than pulling an older Term in to refill the
    slot. That keeps the window a claim about the recency of the Court's behaviour
    instead of one about the walker's coverage, which moves.

    ``b`` is the harness's, never the predictor's: a predictor that supplied its own
    would maximize by declaring one far from the outcome.
    """
    term = scotus_term_year(row.docket_number)
    if term is None:
        return None
    read = _CLAIM_TERM_RATES[claim]
    # A Term-YEAR floor, not a row count — see the docstring. `0` means no floor;
    # `term - 0` would exclude every Term, so the sentinel must short-circuit, and a
    # negative window would read as unbounded-plus-a-Term.
    oldest = term - lookback_terms if lookback_terms > 0 else None
    positives = 0.0
    observed = 0.0
    for entry in statpack.terms:
        if entry.term >= term:
            continue  # leakage guard: the case's own and later Terms never contribute
        if oldest is not None and entry.term < oldest:
            continue  # outside the configured lookback window
        rate, denominator = read(entry)
        if rate is None:
            continue
        positives += rate * denominator
        observed += denominator
    if observed == 0:
        return None
    return positives / observed


def claim_score(p: float, y: int, b: float) -> float:
    """One claim's score: the baseline's Brier minus the forecast's.

    ``(b - y)**2 - (p - y)**2``, for predicted probability ``p``, realized outcome
    ``y`` in {0, 1}, and harness-computed baseline ``b``. Positive when the forecast
    landed closer to the outcome than the baseline did, negative when a bold call
    missed.

    **Proper.** For a fixed ``b`` the score differs from ``-(p - y)**2`` by a term
    that depends on ``b`` and ``y`` but not on ``p``, so nothing done to ``p`` can
    move it; expected score is therefore maximized by reporting the probability
    actually held. (Not an affine transform in the usual sense — the added term
    varies with ``y`` — but the ``p``-independence is what propriety needs, and it is
    exact.)

    **Restating the baseline is worth nothing.** At ``p == b`` the score is
    identically 0 for *either* outcome, realized and not merely in expectation.

    The difference form rather than :func:`brier_skill`'s ratio, because per-claim
    scores are summed and a ratio does not compose — and because the ratio explodes
    near the endpoints where these baselines live.
    """
    return (b - y) ** 2 - (p - y) ** 2


def _scoreable(
    row: CorpusRow,
    outcome: Outcome,
    statpack: StatPack,
    claims: Iterable[Claim],
    lookback_terms: int,
) -> list[tuple[Claim, int, float]]:
    """``(claim, y, b)`` for each claim that both resolves and has a baseline.

    One definition of the scored set, shared by the total and the floor: a floor
    computed over a different set of claims is not a floor for that total.
    """
    scoreable = []
    for claim in claims:
        y = resolve_claim(outcome, claim)
        if y is None:
            continue
        b = claim_base_rate(row, statpack, claim, lookback_terms=lookback_terms)
        if b is None:
            continue
        scoreable.append((claim, y, b))
    return scoreable


def claim_scores(
    probabilities: Mapping[Claim, float],
    row: CorpusRow,
    outcome: Outcome,
    statpack: StatPack,
    *,
    lookback_terms: int = 0,
) -> dict[Claim, float]:
    """Per-claim scores for a set of predicted probabilities.

    Claims the outcome cannot resolve, or that have no prior-Term baseline, are
    absent from the result rather than scored as zero. Pass the returned mapping's
    keys to :func:`claim_floor` so the floor covers exactly the same claims.
    """
    return {
        claim: claim_score(probabilities[claim], y, b)
        for claim, y, b in _scoreable(row, outcome, statpack, probabilities, lookback_terms)
    }


def claim_total(
    probabilities: Mapping[Claim, float],
    row: CorpusRow,
    outcome: Outcome,
    statpack: StatPack,
    *,
    lookback_terms: int = 0,
) -> float:
    """The sum of :func:`claim_scores` — a claim set's total.

    A sum rather than a mean because a mean over *attempted* claims would reward
    declining; over a mandatory set the two differ only by a constant factor anyway.
    The total is descriptive on its own and carries a claim about skill only as
    :func:`claim_lift` over :func:`claim_floor`.
    """
    return sum(
        claim_scores(probabilities, row, outcome, statpack, lookback_terms=lookback_terms).values()
    )


def claim_floor_scores(
    row: CorpusRow,
    outcome: Outcome,
    statpack: StatPack,
    *,
    claims: Iterable[Claim] = CERT_SIGNAL_CLAIMS,
    lookback_terms: int = 0,
    floor_lookback_terms: int = FLOOR_LOOKBACK_TERMS,
) -> dict[Claim, float]:
    """Per-claim scores an uninformed control earns on this case.

    The control knows nothing about the case and reports, for every claim, that
    claim's unconditional rate over a **recent window** (``floor_lookback_terms``),
    while the baseline ``b`` it is scored against uses the configured lookback
    (``lookback_terms``, unbounded as shipped). Where the two windows disagree the
    control earns score for free, and that gap is exactly why a claim total is
    unreadable without this figure beside it — a positive total is not evidence of
    case-level skill.

    The control is held to the same leakage guard as the baseline: its window is
    still strictly-prior Terms, so the floor is a total a real predictor could have
    earned. Where the recent window is too thin to yield a rate the control falls
    back to the baseline itself and scores exactly 0 for that claim, which is what a
    control with nothing more recent to say is worth. A ``floor_lookback_terms`` of
    ``0`` means unbounded, making the control identical to the baseline and the floor
    identically zero — the degenerate case, and the reason the default is a real
    window.

    ``claims`` must be the same claim set the total was computed over; pass
    :func:`claim_scores`' keys.
    """
    floor = {}
    for claim, y, b in _scoreable(row, outcome, statpack, claims, lookback_terms):
        control = claim_base_rate(row, statpack, claim, lookback_terms=floor_lookback_terms)
        floor[claim] = claim_score(control if control is not None else b, y, b)
    return floor


def claim_floor(
    row: CorpusRow,
    outcome: Outcome,
    statpack: StatPack,
    *,
    claims: Iterable[Claim] = CERT_SIGNAL_CLAIMS,
    lookback_terms: int = 0,
    floor_lookback_terms: int = FLOOR_LOOKBACK_TERMS,
) -> float:
    """The sum of :func:`claim_floor_scores` — the uninformed control's total."""
    return sum(
        claim_floor_scores(
            row,
            outcome,
            statpack,
            claims=claims,
            lookback_terms=lookback_terms,
            floor_lookback_terms=floor_lookback_terms,
        ).values()
    )


def claim_lift(total: float, floor: float) -> float:
    """A claim total's lift over its floor — the figure that carries a skill claim.

    The raw total is descriptive: information-free volume pays under this rule, so a
    predictor reporting only long-run rates collects a positive total forever. The
    lift subtracts what that control earns. It is only a comparison when both sides
    cover the same claims and the same window, so report the floor's window with it.
    """
    return total - floor


def vote_accuracy(prediction: Prediction, outcome: Outcome) -> float | None:
    """Fraction of predicted panel votes that matched, if votes were predicted."""
    if not prediction.votes or not outcome.votes:
        return None
    actual = {v.judge: v.vote for v in outcome.votes}
    scored = [v for v in prediction.votes if v.judge in actual]
    if not scored:
        return None
    hits = sum(1 for v in scored if actual[v.judge] == v.vote)
    return hits / len(scored)
