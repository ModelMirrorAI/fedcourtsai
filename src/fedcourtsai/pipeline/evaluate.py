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
from ..schemas import Outcome, Prediction, StatPack
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
