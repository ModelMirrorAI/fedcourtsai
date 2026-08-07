"""The declared forecast-moment register and its normalization at the join."""

from __future__ import annotations

import pytest

from fedcourtsai import corpus
from fedcourtsai.cli import _forward_leakage
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.claims import declared_claim_set
from fedcourtsai.pipeline.ingest import CorpusRow, default_event
from fedcourtsai.schemas import EventKind, Moment, Stage
from fedcourtsai.store import normalized_moment


def _row(court: str = "scotus", docket_number: str = "25-100") -> CorpusRow:
    return CorpusRow(
        case_id=f"{court}/1", court=court, docket_id=1, source="live", docket_number=docket_number
    )


def test_every_declared_moment_is_internally_consistent() -> None:
    """The table is the vocabulary, so it has to be self-describing.

    A duplicate id would make `spec_for` lossy, and two moments sharing an
    ordinal within a stage would make "which is first" — the thing a null
    moment normalizes to — depend on declaration order.
    """
    ids = [spec.event_id for spec in moments.DECLARED_MOMENTS]
    assert len(set(ids)) == len(ids), "a declared event id appears twice"
    for stage in Stage:
        ordinals = [spec.ordinal for spec in moments.moments_for(stage)]
        assert len(set(ordinals)) == len(ordinals), f"{stage} declares a duplicate ordinal"
        if ordinals:
            assert min(ordinals) == 0, f"{stage} declares no first moment"


def test_each_real_stage_declares_a_first_moment() -> None:
    for stage in (Stage.cert, Stage.interim, Stage.merits):
        assert moments.first_moment(stage) is not None


def test_spec_for_is_none_on_an_entry_pinned_or_legacy_id() -> None:
    """The table adds a vocabulary; it does not take one away.

    Every entry-pinned event the extractor mints carries an id the register has
    never heard of, and it must read as "declares no moment" rather than as an
    error — the caller then falls back to its own stage rule.
    """
    assert moments.spec_for("evt-motion-construe-the-application-for-a-stay") is None
    assert moments.spec_for("evt-appeal-disposition") is None
    assert moments.spec_for("") is None


def test_declares_requires_both_the_id_and_the_stage() -> None:
    """The predicate attribution widens on — both halves are load-bearing.

    An undeclared id is not a moment, and a declared moment of a *different*
    stage has no claim on this stage's disposition.
    """
    assert moments.declares("evt-petition-disposition", Stage.cert) is True
    assert moments.declares("evt-petition-disposition", Stage.merits) is False
    assert moments.declares("evt-motion-construe-a-stay", Stage.interim) is False


def test_the_mint_stamps_the_moment_rather_than_leaving_it_derivable() -> None:
    """The events upsert takes the incoming value for every column but `resolved`.

    So a moment left off at the mint is not merely absent — it is nulled again
    by the next re-ingest, which would make the column decay to empty on the
    exact rows the rotations touch most.
    """
    cert = default_event(_row())
    assert cert.stage == Stage.cert and cert.moment == Moment.distribution
    application = default_event(_row(docket_number="25A100"))
    assert application.stage == Stage.interim and application.moment == Moment.arrival
    circuit = default_event(_row(court="ca9", docket_number="22-15044"))
    assert circuit.stage is None and circuit.moment is None


def test_a_null_moment_reads_as_the_stages_first() -> None:
    """A record written before the axis existed had no second moment to be.

    Normalizing at the join rather than back-filling the artifact follows the
    stage rule beside it: the join decides what a legacy record reads as, and
    the record keeps saying only what its writer knew.
    """
    assert normalized_moment(Stage.cert, None) == Moment.distribution
    assert normalized_moment(Stage.merits, None) == Moment.grant
    # An explicit moment is never overridden.
    assert normalized_moment(Stage.cert, Moment.cvsg) == Moment.cvsg
    # No stage means no moment to normalize to.
    assert normalized_moment(None, None) is None


def test_the_moment_round_trips_through_the_corpus() -> None:
    """The column is additive, so an old blob reads as unset rather than failing."""
    event = corpus.CorpusEvent(
        event_id="evt-order-judgment",
        case_id="scotus/1",
        court="scotus",
        kind=EventKind.order,
        stage=Stage.merits,
        moment=Moment.grant,
    )
    record = corpus._event_to_record(event)
    assert record["moment"] == Moment.grant
    assert corpus._event_from_record(record).moment == Moment.grant
    # A record from before the column existed.
    del record["moment"]
    assert corpus._event_from_record(record).moment is None


def test_a_later_merits_moment_declares_the_merits_claim_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keyed on the declaration, not on one event id.

    The old rule compared against the single minted merits id, so a second
    merits moment fell through to the kind lookup, found no `order` entry, and
    declared **no claims** — while the stage-keyed validate check still demanded
    a `judgment` on it. A silent, contradictory pair.
    """
    briefed = moments.MomentSpec(
        event_id="evt-brief-judgment",
        kind=EventKind.brief,
        stage=Stage.merits,
        moment=Moment.briefed,
        ordinal=1,
        decision_target="judgment",
        description="test",
        claim_set_version=moments.CLAIM_SET_MERITS_V1,
    )
    _register(monkeypatch, briefed)
    assert declared_claim_set("evt-order-judgment") == declared_claim_set("evt-brief-judgment")
    # And an undeclared order-kind event still declares nothing.
    assert declared_claim_set("evt-order-something-else") is None


def test_a_later_merits_moment_takes_the_judgment_leakage_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keyed on the declared stage, not on one event id.

    A merits moment sent down the cert branch meets the grant order that opened
    its own proceeding, reads it as a disclosed outcome, and refuses the cell —
    permanently, on every attempt, with an exit code rather than a message.
    """
    briefed = moments.MomentSpec(
        event_id="evt-brief-judgment",
        kind=EventKind.brief,
        stage=Stage.merits,
        moment=Moment.briefed,
        ordinal=1,
        decision_target="judgment",
        description="test",
        claim_set_version=moments.CLAIM_SET_MERITS_V1,
    )
    _register(monkeypatch, briefed)
    granted = {
        "docket_number": "24-100",
        "ProceedingsandOrder": [{"Date": "Mar 4 2025", "Text": "Petition GRANTED."}],
    }
    # The cert moment must refuse: its own outcome is on the docket.
    assert _forward_leakage(granted, "scotus", "evt-petition-disposition") is not None
    # Both merits moments must be admitted: the grant is their legitimate record.
    assert _forward_leakage(granted, "scotus", "evt-order-judgment") is None
    assert _forward_leakage(granted, "scotus", "evt-brief-judgment") is None


def _register(monkeypatch: pytest.MonkeyPatch, *extra: moments.MomentSpec) -> None:
    """Register additional moments for the duration of a test."""
    declared = (*moments.DECLARED_MOMENTS, *extra)
    monkeypatch.setattr(moments, "DECLARED_MOMENTS", declared)
    monkeypatch.setattr(moments, "_BY_EVENT_ID", {s.event_id: s for s in declared})
