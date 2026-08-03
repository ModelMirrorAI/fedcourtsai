"""The vote vocabulary, and the distinctions it exists to keep.

A vote is not a disposition, a merits judgment is not a cert grant, and an
unobserved vote is not an absent one. Each of those was collapsed before, and
each collapse is the kind that no later import can undo — so they are pinned
here rather than left to the schema's shape.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from fedcourtsai.analytics import _GRANT_LABELS
from fedcourtsai.pipeline.outcome import granted_flag
from fedcourtsai.schemas import (
    GRANTED_DISPOSITIONS,
    Disposition,
    Judgment,
    JusticeVote,
    Outcome,
    VoteProvenance,
    VoteValue,
    WritingRole,
)


def test_a_vote_cannot_be_a_disposition() -> None:
    """The defect this replaces: `vote` was typed as what the *Court* did, a
    vocabulary with no member for joining a majority or dissenting."""
    with pytest.raises(ValidationError):
        JusticeVote(justice="jackson", vote=Disposition.granted)
    assert JusticeVote(justice="jackson", vote=VoteValue.majority).vote == VoteValue.majority


def test_the_vote_vocabulary_spans_every_stage() -> None:
    """One model, two parameters: the same object at cert and at merits, so one
    vocabulary has to carry both."""
    assert {VoteValue.grant, VoteValue.deny} <= set(VoteValue)
    assert {VoteValue.majority, VoteValue.dissent} <= set(VoteValue)
    # Non-participation is recorded, because a threshold counts participating
    # Justices and a recusal moves the denominator.
    assert {VoteValue.recused, VoteValue.did_not_participate} <= set(VoteValue)


def test_silence_about_writing_is_not_an_observation_that_none_occurred() -> None:
    """`none` is an affirmative claim — this Justice wrote nothing — which is what
    a final order list discloses about every participating Justice. Defaulting to
    it would turn every record that simply does not address writing into that
    claim, which is the collapse the vocabulary exists to prevent."""
    assert JusticeVote(justice="kagan", vote=VoteValue.deny).writing is None
    stated = JusticeVote(justice="kagan", vote=VoteValue.deny, writing=WritingRole.none)
    assert stated.writing == WritingRole.none  # _Strict stores enum values


def test_a_summary_reversal_is_a_grant_on_the_binary_axis() -> None:
    """The Court granting review and deciding the merits in one order. Keeping it
    off the granted side would break comparability with every rate computed before
    the label existed."""
    assert granted_flag(Disposition.summary_reversal) == 1
    assert granted_flag(Disposition.denied) == 0


def test_the_merits_judgment_is_not_a_cert_disposition() -> None:
    """A DIG has no coherent value on the grant binary — certiorari *was* granted
    and the merits event resolved to nothing — so the axes stay apart."""
    assert "dismissed-as-improvidently-granted" not in {d.value for d in Disposition}
    assert Judgment.dig.value == "dismissed-as-improvidently-granted"
    assert Judgment.equally_divided.value == "affirmed-by-an-equally-divided-court"


def test_provenance_distinguishes_unobserved_from_absent() -> None:
    """The distinction no later import can restore: two votes with `complete=false`
    means seven are unobserved, which is the ordinary state at the cert stage."""
    partial = VoteProvenance(source="order-list:2025-03-10", participating=9, complete=False)
    assert partial.complete is False
    # The bounds are the Court's own: nine seats, and a quorum of six below which
    # it cannot act at all (28 U.S.C. section 1). A denominator outside them is
    # not a denominator.
    for bad in (10, 5, 0):
        with pytest.raises(ValidationError):
            VoteProvenance(source="x", participating=bad, complete=True)


def test_provenance_requires_a_source() -> None:
    """A vote record whose origin is unstated cannot be audited, and this field is
    the only thing that says which of several possible sources produced it."""
    with pytest.raises(ValidationError):
        VoteProvenance(participating=9, complete=True)  # type: ignore[call-arg]


def test_the_grant_family_has_one_definition() -> None:
    """A grant COUNT and a grant RATE are printed in adjacent columns of the docket
    pack, so two enumerations of "what counts as a grant" would diverge somewhere
    visible. The scoring target and the analytics family must agree member for
    member."""
    assert {d.value for d in GRANTED_DISPOSITIONS if d is not Disposition.granted_in_part} == set(
        _GRANT_LABELS
    )
    assert Disposition.summary_reversal.value in _GRANT_LABELS


def test_the_vote_and_disposition_vocabularies_stay_disjoint() -> None:
    """They answer different questions — what a Justice did, and what the Court
    did — so a value in both would let one be silently read as the other. Stated
    as disjointness rather than as a spelling, so it keeps holding as either
    vocabulary grows."""
    assert not ({d.value for d in Disposition} & {v.value for v in VoteValue})
    assert not ({d.value for d in Disposition} & {j.value for j in Judgment})


def test_an_outcome_written_before_this_vocabulary_still_validates() -> None:
    """2971 committed outcomes carry `votes: []` and no provenance or judgment.
    Every field added here is optional precisely so none of them breaks."""
    legacy = Outcome.model_validate(
        {
            "schema_version": "1.0",
            "case_id": "scotus/1",
            "event_id": "evt-petition-disposition",
            "resolved_at": "2025-06-01",
            "actual_disposition": "denied",
            "actual_granted": 0,
            "votes": [],
        }
    )
    assert legacy.vote_provenance is None  # nobody looked, not "nine unanimous"
    assert legacy.judgment is None
