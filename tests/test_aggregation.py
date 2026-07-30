"""The vote thresholds each stage decides by, and the identities a forecast owes.

These lock the two parameters that separate cert, interim, and merits — the
aggregation rule here, the observation mask in ``docs/decision-model.md`` — plus
the arithmetic that turns a margin distribution into a disposition probability.
The thresholds are load-bearing for a scored quantity, so a silent change to one
would rescale every derived probability rather than fail anything.
"""

from __future__ import annotations

import pytest

from fedcourtsai.pipeline.aggregation import (
    AGGREGATION,
    disposition_probability,
    expected_votes,
    rule_for,
)
from fedcourtsai.schemas import Stage


def test_every_stage_declares_a_rule() -> None:
    """The lookup must be total over the vocabulary, or a stage lands on a
    KeyError at scoring time rather than at import."""
    assert set(AGGREGATION) == set(Stage)


def test_cert_takes_four_and_does_not_move_with_recusals() -> None:
    """The custom is stated as four Justices, not as a fraction of the bench, so
    a recusal leaves it at four — unlike the majority rules below."""
    rule = AGGREGATION[Stage.cert]
    assert rule.threshold(9) == 4
    assert rule.threshold(8) == 4


def test_below_quorum_is_rejected_rather_than_clamped() -> None:
    """With five sitting the Court cannot act at all (28 U.S.C. section 1), so
    there is no threshold to return. Clamping would answer an invalid question
    confidently — and pre-register that answer."""
    for stage in Stage:
        with pytest.raises(ValueError, match="quorum"):
            AGGREGATION[stage].threshold(5)
    # At quorum the rules resume: four is still four, a majority of six is four.
    assert AGGREGATION[Stage.cert].threshold(6) == 4
    assert AGGREGATION[Stage.merits].threshold(6) == 4


def test_a_majority_moves_with_the_bench() -> None:
    """This is the substantive difference from cert: an eight-Justice merits
    Court still needs five, which is what makes a 4-4 split an affirmance by an
    equally divided Court rather than a judgment."""
    merits = AGGREGATION[Stage.merits]
    assert merits.threshold(9) == 5
    assert merits.threshold(8) == 5
    assert merits.threshold(6) == 4
    assert AGGREGATION[Stage.interim].threshold(9) == 5


def test_no_rule_claims_statutory_authority_for_its_vote_count() -> None:
    """The finding these citations record: every threshold is Court practice. The
    Rules state no certiorari vote count and no statute states the merits
    majority, so a source implying otherwise would misrepresent what backs the
    number."""
    for stage, rule in AGGREGATION.items():
        assert "Court practice" in rule.source, stage


def test_every_rule_names_a_source() -> None:
    for stage, rule in AGGREGATION.items():
        assert rule.source.strip(), stage


def test_an_undeclared_stage_yields_no_rule_rather_than_a_guess() -> None:
    """A circuit motion has no Supreme Court decision standard. Returning None
    lets the caller drop to disposition-level scoring; inventing a threshold
    would produce a number that means nothing."""
    assert rule_for(None) is None
    assert rule_for(Stage.cert) is AGGREGATION[Stage.cert]


def test_a_malformed_margin_is_rejected_rather_than_scored() -> None:
    """This feeds a scored quantity, so a number that cannot be a probability
    must not reach a caller that will trust it."""
    with pytest.raises(ValueError, match="sums to"):
        disposition_probability([1.0] * 10, Stage.cert)
    with pytest.raises(ValueError, match="negative"):
        disposition_probability([-1.0, 1.0] + [0.5] * 8, Stage.cert)
    with pytest.raises(ValueError, match="bins"):
        disposition_probability([0.0] * 9 + [1.0], Stage.merits, participating=8)


def test_disposition_probability_sums_the_mass_at_or_above_the_threshold() -> None:
    # 0..9 votes; 0.1 at each of 4..9 is 0.6 of the mass at or above four.
    margin = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    assert disposition_probability(margin, Stage.cert) == pytest.approx(0.6)
    # A majority needs five, so the same distribution gives one bin less.
    assert disposition_probability(margin, Stage.merits) == pytest.approx(0.5)


def test_the_stage_is_what_separates_the_two_probabilities() -> None:
    """The whole model claim in one assertion: same votes, different stage,
    different disposition — because only the threshold changed."""
    margin = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # exactly 4 votes
    assert disposition_probability(margin, Stage.cert) == pytest.approx(1.0)
    assert disposition_probability(margin, Stage.merits) == pytest.approx(0.0)


def test_expected_votes_is_the_coherence_identity_right_hand_side() -> None:
    """By linearity of expectation the per-justice probabilities must sum to
    this, whatever the dependence between votes — which is why the check is free
    and needs no independence assumption."""
    margin = [0.0, 0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    assert expected_votes(margin) == pytest.approx(2.0)


def test_a_degenerate_margin_carries_no_probability() -> None:
    assert disposition_probability([1.0] + [0.0] * 9, Stage.cert) == pytest.approx(0.0)
    assert expected_votes([1.0] + [0.0] * 9) == pytest.approx(0.0)
