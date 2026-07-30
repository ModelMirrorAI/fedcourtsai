"""The per-claim scoring rule.

Pre-registered in ``docs/outcome-decomposition.md``. Only the rule itself is
built: the claim *set* it was to be applied to turned out not to be forecastable,
so nothing calls this yet. The rule survives that because it is independent of
which claims are eventually declared — and its properties are what the
decomposition rests on, so they are pinned here rather than left in prose.
"""

from __future__ import annotations

from fedcourtsai.pipeline.evaluate import claim_score


def test_reporting_the_baseline_scores_exactly_zero_either_way() -> None:
    # Realized, not merely in expectation: `p == b` is worth precisely nothing
    # whichever way the claim resolves. Exact equality, not approx — the two Brier
    # terms are the same expression, so any drift here is a changed rule.
    for b in (0.0, 0.02, 0.3, 0.5, 0.87, 1.0):
        assert claim_score(b, 0, b) == 0.0
        assert claim_score(b, 1, b) == 0.0


def test_a_forecast_closer_than_the_baseline_scores_positive() -> None:
    # And a bold miss is paid for, which is what stops volume being free.
    assert claim_score(0.9, 1, 0.3) > 0
    assert claim_score(0.1, 0, 0.3) > 0
    assert claim_score(0.9, 0, 0.3) < 0


def test_the_score_is_proper_because_the_added_term_is_p_independent() -> None:
    """Propriety, as a property rather than an assertion.

    For a fixed baseline the score differs from the negated Brier score by a term
    that does not involve ``p``, so the gap between any two forecasts is the same
    whatever the baseline is — which is exactly why moving ``b`` cannot make a
    dishonest ``p`` pay.
    """
    for b in (0.05, 0.4, 0.95):
        for y in (0, 1):
            gap = claim_score(0.7, y, b) - claim_score(0.2, y, b)
            reference = -((0.7 - y) ** 2) + (0.2 - y) ** 2
            assert abs(gap - reference) < 1e-12


def test_expected_score_is_maximized_by_the_honest_probability() -> None:
    # The operational form of propriety: sweep p, and the argmax of expected score
    # sits at the probability actually held, wherever the baseline is.
    for truth in (0.1, 0.35, 0.8):
        for b in (0.05, 0.5, 0.9):
            best = max(
                (
                    truth * claim_score(p / 500, 1, b) + (1 - truth) * claim_score(p / 500, 0, b),
                    p / 500,
                )
                for p in range(501)
            )[1]
            assert abs(best - truth) < 0.005
