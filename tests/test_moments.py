"""The declared forecast-moment register and its normalization at the join."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.cli import _forward_leakage
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.claims import (
    CLAIM_AMICUS_INCREMENT,
    CLAIM_INTERIM_DISPOSITION,
    CLAIM_REFERRAL_INCREMENT,
    CLAIM_RESPONSE_REQUESTED_INCREMENT,
    CLAIM_SET_INTERIM_V1,
    declared_claim_set,
)
from fedcourtsai.pipeline.ingest import CorpusRow, default_event
from fedcourtsai.pipeline.outcome import (
    MERITS_EVENT_ID,
    arrival_event_for,
    briefed_merits_event_for,
    cvsg_event_for,
    interim_response_events_for,
)
from fedcourtsai.schemas import Disposition, EventKind, Moment, Stage
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
    # A validated artifact hands back the plain string (`use_enum_values`),
    # and the register must normalize it identically — the lookups compare by
    # equality, because an identity check silently misses every deserialized
    # record and drops the cell to a bare-stage block.
    assert normalized_moment("cert", None) == Moment.distribution  # type: ignore[arg-type]
    assert moments.declares("evt-order-cvsg-disposition", "cert") is True  # type: ignore[arg-type]


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


def test_the_briefed_moment_mints_only_while_the_grant_moment_is_open() -> None:
    """The open-first-moment guard, which is what makes a forever-true trigger safe.

    The respondent's brief stays on the docket permanently, so this trigger
    re-fires on every poll — harmless, because the upsert is idempotent. What
    would not be harmless is minting on a docket whose judgment has already
    landed: that creates a permanently open event nothing can ever resolve,
    which would keep the case in the rotation and owed a cell forever.
    """
    briefed = date(2025, 6, 1)
    row = CorpusRow(
        case_id="scotus/1",
        court="scotus",
        docket_id=1,
        source="live",
        docket_number="24-100",
        disposition=Disposition.granted,
        date_cert_granted=date(2025, 3, 4),
        merits_brief_filed=briefed,
    )
    minted = briefed_merits_event_for(row, [MERITS_EVENT_ID])
    assert minted is not None
    assert (minted.event_id, minted.stage, minted.moment) == (
        "evt-brief-judgment",
        Stage.merits,
        Moment.briefed,
    )
    assert minted.opened_at == briefed  # the moment, not the grant date
    # The grant moment already closed: the case is decided, nothing to forecast.
    assert briefed_merits_event_for(row, []) is None
    # A judgment already latched: same answer, checked on the row rather than
    # the event set, since the two can disagree for a poll.
    decided = row.model_copy(update={"merits_judgment": "reversed"})
    assert briefed_merits_event_for(decided, [MERITS_EVENT_ID]) is None
    # No brief parsed yet.
    unbriefed = row.model_copy(update={"merits_brief_filed": None})
    assert briefed_merits_event_for(unbriefed, [MERITS_EVENT_ID]) is None


def test_a_granted_application_mints_no_briefed_moment_either() -> None:
    """The same `opens_merits_proceeding` guard the grant moment takes."""
    application = CorpusRow(
        case_id="scotus/2",
        court="scotus",
        docket_id=2,
        source="live",
        docket_number="24A100",
        disposition=Disposition.granted,
        date_cert_granted=None,
        merits_brief_filed=date(2025, 6, 1),
    )
    assert briefed_merits_event_for(application, [MERITS_EVENT_ID]) is None


def test_the_cvsg_moment_mints_only_while_the_petition_is_open() -> None:
    """Same forever-true trigger, same open-first-moment guard.

    The CVSG date stays latched on the row for the life of the case, so this
    re-fires on every poll. What makes that safe is that the cert baseline must
    still be open: a CVSG on an already-decided petition would mint an event
    with nothing left to forecast and no way to resolve it.
    """
    called = date(2025, 5, 12)
    row = CorpusRow(
        case_id="scotus/3",
        court="scotus",
        docket_id=3,
        source="live",
        docket_number="24-200",
        cvsg_date=called,
    )
    baseline = moments.moments_for(Stage.cert)[0].event_id
    minted = cvsg_event_for(row, [baseline])
    assert minted is not None
    assert (minted.event_id, minted.stage, minted.moment) == (
        "evt-order-cvsg-disposition",
        Stage.cert,
        Moment.cvsg,
    )
    assert minted.opened_at == called  # the moment, not the filing date
    assert minted.decision_target == "disposition"  # the same question as moment one
    # The petition already resolved: nothing left to forecast.
    assert cvsg_event_for(row, []) is None
    # No CVSG on the docket.
    assert cvsg_event_for(row.model_copy(update={"cvsg_date": None}), [baseline]) is None
    # A circuit docket carries no cert stage at all.
    circuit = row.model_copy(update={"court": "ca9", "case_id": "ca9/3"})
    assert cvsg_event_for(circuit, [baseline]) is None


def test_every_cert_moment_declares_the_same_claim_set() -> None:
    """The claims do not change because the forecast was taken earlier or later.

    Only the information set moves, and that lives on the aggregation key. A
    per-moment set version would fragment every claim aggregate for nothing.
    """
    sets = [declared_claim_set(s.event_id) for s in moments.moments_for(Stage.cert)]
    assert len(sets) >= 3  # baseline, CVSG, arrival
    assert all(cs == sets[0] for cs in sets)
    assert sets[0] is not None


def test_the_interim_response_moments_are_distinct_events() -> None:
    """A request and a filing are different events, kept apart deliberately.

    A respondent may answer uninvited, and a requested response may never
    arrive — so one "the record filled" signal would conflate two things with
    very different horizons (median 17 days against median 2).
    """
    row = CorpusRow(
        case_id="scotus/4",
        court="scotus",
        docket_id=4,
        source="live",
        docket_number="24A200",
        response_requested_at=date(2025, 4, 1),
        response_filed_at=date(2025, 4, 5),
    )
    baseline = moments.moments_for(Stage.interim)[0].event_id
    minted = interim_response_events_for(row, [baseline])
    assert [(e.moment, e.opened_at) for e in minted] == [
        (Moment.response_requested, date(2025, 4, 1)),
        (Moment.response_filed, date(2025, 4, 5)),
    ]
    # Each mints on its own signal, not as a pair.
    only_filed = row.model_copy(update={"response_requested_at": None})
    assert [e.moment for e in interim_response_events_for(only_filed, [baseline])] == [
        Moment.response_filed
    ]
    # And the same open-first-moment guard: a decided application mints nothing.
    assert interim_response_events_for(row, []) == []


def test_every_interim_moment_declares_the_same_interim_set() -> None:
    """All three interim moments declare `interim-v1`, with the same four ids.

    The claims do not change because the forecast was taken later — only the
    information set does, and that lives on the aggregation key — so the three
    moments must agree exactly, order included.
    """
    expected = (
        CLAIM_SET_INTERIM_V1,
        (
            CLAIM_INTERIM_DISPOSITION,
            CLAIM_RESPONSE_REQUESTED_INCREMENT,
            CLAIM_REFERRAL_INCREMENT,
            CLAIM_AMICUS_INCREMENT,
        ),
    )
    declared = [declared_claim_set(spec.event_id) for spec in moments.moments_for(Stage.interim)]
    assert len(declared) == 3
    assert declared == [expected, expected, expected]


def test_a_granted_case_reaches_the_predict_queue_without_being_salience_selected(
    tmp_path: Path,
) -> None:
    """The merits bypass, at the seam that matters.

    A granted docket has no further distribution transition, so the selection
    sweep is the ONLY path to a merits cell — and the sweep gates on
    `salience_selected`, which a below-cap petition never gets and, because the
    selection pass never cohorts a resolved row, never will. Without the bypass
    every grant the gate missed is unforecastable at the merits stage forever.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    row = corpus.CorpusRow(
        case_id="scotus/5",
        court="scotus",
        docket_number="24-300",
        disposition=Disposition.granted,
        date_cert_granted=date(2025, 3, 4),
        salience_version="sal-v1",
        salience_selected=False,  # scored, below the cap
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        # Not yet granted-with-an-open-merits-event: the gate still refuses.
        assert corpus.is_salience_deferred(row) is True
        assert corpus.has_open_merits_event(conn, row.case_id) is False
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=MERITS_EVENT_ID,
                    case_id=row.case_id,
                    court="scotus",
                    kind=EventKind.order,
                    stage=Stage.merits,
                    moment=Moment.grant,
                )
            ],
        )
        assert corpus.has_open_merits_event(conn, row.case_id) is True
        assert corpus.merits_open_case_ids(conn) == {row.case_id}


def test_the_bypass_does_not_reopen_the_cert_gate(tmp_path: Path) -> None:
    """`salience_selected` keeps meaning "spent tournament budget at cert".

    Latching it on granted rows would have been the easy way to get the bypass,
    and it would corrupt the one reading the column is documented to carry —
    leaking into the scope manifest and the salience board. The bypass is
    conditioned on the event's stage instead, so the row is untouched.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    row = corpus.CorpusRow(
        case_id="scotus/6",
        court="scotus",
        docket_number="24-301",
        disposition=Disposition.granted,
        date_cert_granted=date(2025, 3, 4),
        salience_version="sal-v1",
        salience_selected=False,
    )
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [row])
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=MERITS_EVENT_ID,
                    case_id=row.case_id,
                    court="scotus",
                    kind=EventKind.order,
                    stage=Stage.merits,
                    moment=Moment.grant,
                )
            ],
        )
        stored = corpus.get_row(conn, row.case_id)
    assert stored is not None and stored.salience_selected is False


def test_the_arrival_moment_mints_on_selection_while_the_petition_is_open() -> None:
    """The caller owns the selection predicate; the helper owns the guards.

    The sal-v2 arrival event is minted by selection, not by a docket signal,
    so the mint helper enforces only what makes the event coherent: a SCOTUS
    cert-form docket with a docketing date, and the petition baseline still
    open — the same open-first-moment guard as the CVSG mint.
    """
    filed = date(2026, 7, 15)
    row = corpus.CorpusRow(
        case_id="scotus/26000042",
        court="scotus",
        docket_number="26-42",
        date_filed=filed,
    )
    baseline = moments.moments_for(Stage.cert)[0].event_id
    minted = arrival_event_for(row, [baseline])
    assert minted is not None
    assert (minted.event_id, minted.stage, minted.moment) == (
        "evt-petition-arrival-disposition",
        Stage.cert,
        Moment.arrival,
    )
    assert minted.opened_at == filed  # the docketing-time information set
    assert minted.decision_target == "disposition"  # the same question as moment one
    # The petition already resolved: nothing left to forecast.
    assert arrival_event_for(row, []) is None
    # No docketing date: the moment's information set is undefined.
    assert arrival_event_for(row.model_copy(update={"date_filed": None}), [baseline]) is None
    # A distribution on the docket: the docketing-time information set is
    # gone, and the arrival label would be false — minted never, however
    # forever-true the selection predicate is.
    distributed = row.model_copy(update={"distributed_for_conference": date(2026, 9, 28)})
    assert arrival_event_for(distributed, [baseline]) is None
    scanned = row.model_copy(update={"distribution_count": 1})
    assert arrival_event_for(scanned, [baseline]) is None
    # An application docket carries no cert arrival.
    application = row.model_copy(update={"docket_number": "26A42"})
    assert arrival_event_for(application, [baseline]) is None
    # A circuit docket carries no cert stage at all.
    circuit = row.model_copy(update={"court": "ca9", "case_id": "ca9/42"})
    assert arrival_event_for(circuit, [baseline]) is None
