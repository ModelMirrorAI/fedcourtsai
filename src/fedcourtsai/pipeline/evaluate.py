"""``run-evaluate`` helpers.

Each evaluator scores each predictor's prediction against the realized
``outcome.json``. The qualitative judgment (reasoning quality) is produced by an
agent; the quantitative pieces (correctness, Brier score, and the segment-baseline
skill score) are deterministic and provided here so every evaluator computes them
identically.

This module reads no config. Every tunable — today, the segment base rate's
lookback window — arrives as an argument, so the functions stay pure and a test,
a replay cell, and the cert back-test all get the same number from the same
inputs. Config resolves one level out, at the caller.
"""

from __future__ import annotations

from ..corpus import CorpusRow, scotus_term_year
from ..schemas import Outcome, Prediction, PredictionContext, StatPack
from .salience import salience_band


def is_correct(prediction: Prediction, outcome: Outcome) -> int:
    return int(prediction.predicted_disposition == outcome.actual_disposition)


def brier_score(prediction: Prediction, outcome: Outcome) -> float:
    """Brier score for the binary granted/denied forecast (lower is better)."""
    return (prediction.probability - outcome.actual_granted) ** 2


def _pooled_band_rate(
    band: str,
    term: int,
    statpack: StatPack,
    *,
    lookback_terms: int,
    risk_set: bool,
) -> float | None:
    """One band's grant rate pooled over Terms strictly before ``term``.

    ``risk_set`` picks which of the two published rates is pooled, and the choice
    has to match how ``band`` was obtained — see the two callers. Pooled as a
    resolved-weighted mean of the per-Term rates, which equals aggregate weighted
    grants over aggregate weighted resolved, so a Term contributes at the weight
    belonging to the rate being pooled.
    """
    # `band` and the statpack segments are both `sal-v1` today, so a plain name
    # match is safe. When sal-v2 lands, reconcile the band version with each Term's
    # `salience_version` here — a lagging statpack would otherwise miss silently. A
    # bounded `lookback_terms` limits, but does not fix, that exposure: it caps how
    # far back a stale version can reach, not whether the mismatch is noticed.
    #
    # A Term-YEAR floor, not a row count — see the callers' docstrings. `0` means no
    # floor; `term - 0` would exclude every Term, so the sentinel must short-circuit.
    # A negative window would read as unbounded-plus-a-Term; `ge=0` guards the config
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
            if seg.band != band:
                continue
            rate = seg.prefix_est_grant_rate if risk_set else seg.est_grant_rate
            denominator = seg.prefix_weighted_resolved if risk_set else seg.weighted_resolved
            if rate is not None:
                weighted_grants += rate * denominator
                weighted_resolved += denominator
    if weighted_resolved == 0:
        return None
    return weighted_grants / weighted_resolved


def segment_base_rate(
    row: CorpusRow, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The band rate for a case whose band is read from the row **now**.

    For a resolved case that is its *terminal* band, so this pools
    ``est_grant_rate`` — the rate over rows that ended in the band. Baseline and
    grouping match, which is what makes the number meaningful.

    This is the fallback, not the preferred path. Prefer
    :func:`prediction_base_rate` wherever the cell froze its own conditioning;
    use this only where it did not, which today means the cert back-test (whose
    replay snapshot has its proceedings stripped, so the cell could not observe
    its band at all) and any prediction written before the frozen block existed.

    Leakage-safe by construction: only Terms preceding the case contribute, so
    the rate never sees the case's own — or any later — Term. ``None`` when the
    case has no Term, no band data precedes it, or nothing in the band resolved.

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
    return _pooled_band_rate(
        salience_band(row),
        term,
        statpack,
        lookback_terms=lookback_terms,
        risk_set=False,
    )


def prediction_base_rate(
    context: PredictionContext | None, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The band rate a cell actually faced, from its frozen conditioning.

    Pools ``prefix_est_grant_rate`` — the **risk-set** rate over every petition
    that ever *reached* the band, not only those that ended in it. That is the
    right rate precisely because ``context.band`` is the band as at prediction: a
    band only ever strengthens, so a cell sitting at ``baseline`` may still relist,
    and the population it belongs to is everyone who has reached ``baseline``.

    The pairing is the whole point. Reading the risk-set rate against a *terminal*
    band would overstate the baseline for exactly the petitions whose band moved,
    and reading the terminal rate against a frozen band would understate it
    several-fold in the weak bands. Neither half is correct alone.

    ``None`` when there is no frozen context, when the snapshot disclosed no
    proceedings so no band could be derived, or when no prior Term carries the
    band — the caller then falls back to :func:`segment_base_rate`, which is
    honest rather than invented.
    """
    if context is None or context.band is None or context.term is None:
        return None
    return _pooled_band_rate(
        context.band,
        context.term,
        statpack,
        lookback_terms=lookback_terms,
        risk_set=True,
    )


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


def vote_accuracy(prediction: Prediction, outcome: Outcome) -> float | None:
    """Fraction of predicted votes that matched, over the Justices both name.

    Scored only where the outcome actually records a vote, so a Justice whose vote
    was never observed costs a predictor nothing — the denominator is what the
    record discloses, never what the predictor attempted. ``Outcome.vote_provenance``
    is what says whether a short list means "only these are public" or "nobody
    looked"; this function needs only the intersection either way.
    """
    if not prediction.votes or not outcome.votes:
        return None
    actual = {v.justice: v.vote for v in outcome.votes}
    scored = [v for v in prediction.votes if v.justice in actual]
    if not scored:
        return None
    hits = sum(1 for v in scored if actual[v.justice] == v.vote)
    return hits / len(scored)
