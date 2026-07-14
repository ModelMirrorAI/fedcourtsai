"""``run-evaluate`` helpers.

Each evaluator scores each predictor's prediction against the realized
``outcome.json``. The qualitative judgment (reasoning quality) is produced by an
agent; the quantitative pieces (correctness, Brier score, and the segment-baseline
skill score) are deterministic and provided here so every evaluator computes them
identically.
"""

from __future__ import annotations

from ..corpus import CorpusRow, scotus_term_year
from ..schemas import Outcome, Prediction, StatPack
from .salience import salience_band


def is_correct(prediction: Prediction, outcome: Outcome) -> int:
    return int(prediction.predicted_disposition == outcome.actual_disposition)


def brier_score(prediction: Prediction, outcome: Outcome) -> float:
    """Brier score for the binary granted/denied forecast (lower is better)."""
    return (prediction.probability - outcome.actual_granted) ** 2


def segment_base_rate(row: CorpusRow, statpack: StatPack) -> float | None:
    """The leakage-safe salience-segment base rate for a case.

    The case's frozen ``sal-v1`` band's grant rate, pooled over statpack Terms
    **strictly before the case's own Term**. Leakage-safe by construction: only
    Terms preceding the case contribute, so the rate a replay cell anchors on never
    sees the case's own — or any later — Term. Pooled as a resolved-weighted mean of
    the per-Term band rates (each Term's ``est_grant_rate`` weighted by its
    ``weighted_resolved``), which equals the aggregate weighted grants over
    aggregate weighted resolved. ``None`` when the case has no Term, no band data
    precedes it, or nothing in the band resolved.
    """
    term = scotus_term_year(row.docket_number)
    if term is None:
        return None
    # `band` and the statpack segments are both `sal-v1` today, so a plain name
    # match is safe. When sal-v2 lands, reconcile the band version with each Term's
    # `salience_version` here — a lagging statpack would otherwise miss silently.
    band = salience_band(row)
    weighted_grants = 0.0
    weighted_resolved = 0.0
    for entry in statpack.terms:
        if entry.term >= term:
            continue  # leakage guard: the case's own and later Terms never contribute
        for seg in entry.segments:
            if seg.band == band and seg.est_grant_rate is not None:
                weighted_grants += seg.est_grant_rate * seg.weighted_resolved
                weighted_resolved += seg.weighted_resolved
    if weighted_resolved == 0:
        return None
    return weighted_grants / weighted_resolved


def brier_skill_score(
    prediction: Prediction, outcome: Outcome, base_rate: float | None
) -> float | None:
    """Brier skill score of the forecast vs the segment base rate.

    ``1 - brier(prediction) / brier(baseline)``, where the baseline is the naive
    forecaster that always predicts ``base_rate``. A prediction no better than the
    base rate scores ~0, a better one positive (up to 1), a worse one negative — so
    parroting the segment's grant rate earns no skill. ``None`` when there is no
    base rate, or when the baseline is already perfect (``base_rate`` matched the
    outcome exactly), where the skill ratio is undefined.
    """
    if base_rate is None:
        return None
    baseline_brier = (base_rate - outcome.actual_granted) ** 2
    if baseline_brier == 0:
        return None
    return 1.0 - brier_score(prediction, outcome) / baseline_brier


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
