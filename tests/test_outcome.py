from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.events import _SCOTUS_BASELINE_ONLY_KINDS
from fedcourtsai.pipeline.ingest import CorpusRow, from_api_docket
from fedcourtsai.pipeline.outcome import (
    CASE_BASELINE_ID_PREFIXES,
    MERITS_EVENT_ID,
    Resolution,
    appears_decided,
    detect_resolution,
    disposition_basis,
    granted_flag,
    interim_disposal_signal,
    is_machine_readable,
    merits_event_for,
    mint_merits_event,
    record_outcomes,
    resolution_signals,
    resolve_case,
    snapshot_shows_disposition,
    termination_signal,
)
from fedcourtsai.schemas import Disposition, EventKind, Outcome, PredictableEvent, Stage
from fedcourtsai.serialize import read_model
from fedcourtsai.store import _FORECASTABLE_KINDS

DECIDED_DOCKET = {
    "id": 64512345,
    "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
    "docket_number": "21-55555",
    "case_name": "Doe v. Roe",
    "date_filed": "2021-03-01",
    "date_terminated": "2022-06-15",
    "disposition": "Petition denied",
    "citations": ["12 F.4th 100"],
}


def _db(tmp_path: Path) -> Path:
    return corpus.corpus_db_path(tmp_path / "corpus")


def _open_event(
    tmp_path: Path,
    event_id: str = "evt-petition-review",
    kind: EventKind = EventKind.petition,
    stage: Stage | None = None,
) -> None:
    """Record an open predictable event in the corpus for the canned docket."""
    event = corpus.CorpusEvent(
        event_id=event_id,
        case_id="ca9/64512345",
        court="ca9",
        kind=kind,
        stage=stage,
        title="Petition for review",
    )
    with corpus.connect(_db(tmp_path)) as conn:
        corpus.upsert_events(conn, [event])


# --- pure helpers --------------------------------------------------------------


def test_granted_flag_maps_partial_grant_to_granted() -> None:
    assert granted_flag(Disposition.granted) == 1
    assert granted_flag(Disposition.granted_in_part) == 1
    assert granted_flag(Disposition.gvr) == 1  # a GVR grants the petition
    assert granted_flag(Disposition.denied) == 0
    assert granted_flag(Disposition.dismissed) == 0


def test_is_machine_readable_rejects_none_and_other() -> None:
    assert is_machine_readable(Disposition.denied) is True
    assert is_machine_readable(None) is False
    assert is_machine_readable(Disposition.other) is False


def test_appears_decided() -> None:
    assert appears_decided(from_api_docket(DECIDED_DOCKET)) is True
    pending = from_api_docket({"id": 1, "court_id": "ca9", "date_filed": "2024-01-01"})
    assert appears_decided(pending) is False
    # A SCOTUS docket whose only decided signal is the petition-stage cert date.
    cert_dated = from_api_docket({"id": 2, "court_id": "scotus", "date_cert_denied": "2023-01-09"})
    assert appears_decided(cert_dated) is True


# --- detection -----------------------------------------------------------------


def test_single_open_event_resolves_deterministically() -> None:
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert not resolution.unrecorded
    outcome = resolution.outcomes["evt-petition-review"]
    assert outcome.actual_disposition == Disposition.denied
    assert outcome.actual_granted == 0
    assert outcome.resolved_at == date(2022, 6, 15)
    assert outcome.source == "12 F.4th 100"


def test_cert_dated_petition_resolves_at_the_petition_stage() -> None:
    # A fresh SCOTUS docket typically carries the petition decision only as a
    # cert-stage date: no disposition string, and for a granted petition no
    # termination until the merits judgment. The derived disposition plus the
    # petition-stage resolution date make it deterministic, stamped at the grant.
    row = from_api_docket(
        {
            "id": 22451,
            "court_id": "scotus",
            "docket_number": "22-451",
            "date_cert_granted": "2022-10-03",
            "date_terminated": "2023-06-30",
        }
    )
    resolution = detect_resolution(row, "scotus", 22451, ["evt-petition-disposition"])
    assert not resolution.unrecorded
    outcome = resolution.outcomes["evt-petition-disposition"]
    assert outcome.actual_disposition == Disposition.granted
    assert outcome.actual_granted == 1
    assert outcome.resolved_at == date(2022, 10, 3)


def _application_docket(docket_number: str, disposition: str | None) -> CorpusRow:
    return from_api_docket(
        {
            "id": 9001,
            "court": "https://www.courtlistener.com/api/rest/v4/courts/scotus/",
            "docket_number": docket_number,
            "date_filed": "2024-08-01",
            "date_terminated": "2024-08-15",
            "disposition": disposition,
        }
    )


def test_decided_application_records_the_interim_outcome_on_the_interim_baseline() -> None:
    # The interim path: a granted stay whose open event is the interim-stage
    # motion baseline records the outcome from the row's interim-matched
    # disposition — dated by the disposing entry the ingest latched
    # (date_decided on an application docket), with no cert-only signals block.
    row = _application_docket("24A1099", "granted")
    resolution = detect_resolution(
        row,
        "scotus",
        9001,
        ["evt-motion-disposition"],
        stages={"evt-motion-disposition": Stage.interim},
    )
    assert not resolution.unrecorded
    outcome = resolution.outcomes["evt-motion-disposition"]
    assert outcome.actual_disposition == Disposition.granted
    assert outcome.actual_granted == 1
    assert outcome.resolved_at == date(2024, 8, 15)
    assert outcome.signals is None


def test_interim_routing_never_touches_a_cert_docket() -> None:
    # A cert docket with an interim-staged motion open beside its petition
    # still routes the case-level disposition to the cert event only — the
    # interim target rule is an application-docket branch, not a cert one.
    row = from_api_docket(
        {
            "id": 22451,
            "court_id": "scotus",
            "docket_number": "22-451",
            "date_cert_granted": "2022-10-03",
        }
    )
    resolution = detect_resolution(
        row,
        "scotus",
        22451,
        ["evt-motion-stay", "evt-petition-disposition"],
        stages={"evt-petition-disposition": Stage.cert, "evt-motion-stay": Stage.interim},
    )
    assert set(resolution.outcomes) == {"evt-petition-disposition"}
    assert resolution.outcomes["evt-petition-disposition"].actual_granted == 1


def test_decided_application_without_an_interim_staged_event_stays_unrecorded() -> None:
    # No stage-less fallback on an application docket: whatever shape the open
    # baseline carries — the cert-shaped petition id or the motion id — without
    # an explicit interim stage nothing is attributed, and the resolution
    # surfaces for triage instead of guessing.
    row = _application_docket("24A1099", "Petition denied")
    for baseline in ("evt-petition-disposition", "evt-motion-disposition"):
        resolution = detect_resolution(row, "scotus", 9001, [baseline])
        assert not resolution.outcomes
        (unrecorded,) = resolution.unrecorded
        assert unrecorded.event_id == baseline
        assert "interim baseline" in unrecorded.reason


def test_unreadable_application_resolution_stays_unrecorded() -> None:
    # A decided-looking application whose disposition the vocabularies could
    # not read is the unrecorded path with the machine-readability reason —
    # nothing is written on a guess, exactly as on a cert docket.
    row = _application_docket("24A1099", "vacated by consent")  # normalizes to `other`
    resolution = detect_resolution(
        row,
        "scotus",
        9001,
        ["evt-motion-disposition"],
        stages={"evt-motion-disposition": Stage.interim},
    )
    assert not resolution.outcomes
    (unrecorded,) = resolution.unrecorded
    assert "not machine-readable" in unrecorded.reason


def test_interim_disposal_signal_reads_relief_named_disposals() -> None:
    # The high-recall backstop must be wider than the resolving vocabulary: a
    # disposal naming the relief instead of the application ("Stay ... granted")
    # leaves the row unresolved while the outcome sits legible in the snapshot.
    relief_named = {
        "ProceedingsandOrder": [
            {"Text": "Stay of execution granted by The Chief Justice pending further order."}
        ]
    }
    assert interim_disposal_signal(relief_named) is not None
    # It also subsumes the resolving vocabulary's own shapes.
    vocabulary = {
        "ProceedingsandOrder": [{"Text": "Application (24A650) denied by Justice Kagan."}]
    }
    assert interim_disposal_signal(vocabulary) is not None
    # A live pending application's routine entries never match — a false
    # "decided" would park every pending stay.
    pending = {
        "ProceedingsandOrder": [
            {"Text": "Application (25A1) for a stay, submitted to The Chief Justice."},
            {"Text": "Response to application (25A1) requested by The Chief Justice."},
            {"Text": "Application (25A1) referred to the Court."},
            {"Text": "Brief amicus curiae of Amicus Org filed."},
        ]
    }
    assert interim_disposal_signal(pending) is None


def test_tolerant_application_spelling_is_also_guarded() -> None:
    # The guard keys on the tolerant recognizer, so a historical spelling the
    # strict `YYAnnn` parser rejects (and the relabel migration therefore
    # skips) still never receives a cert-rule outcome — its stage-less
    # petition-shaped baseline has no interim stage to attribute to.
    row = from_api_docket(
        {
            "id": 9002,
            "court": "https://www.courtlistener.com/api/rest/v4/courts/scotus/",
            "docket_number": "A-363",
            "date_filed": "1998-08-01",
            "date_terminated": "1998-08-15",
            "disposition": "Petition denied",
        }
    )
    resolution = detect_resolution(row, "scotus", 9002, ["evt-petition-disposition"])
    assert not resolution.outcomes
    (unrecorded,) = resolution.unrecorded
    assert "interim baseline" in unrecorded.reason


def test_undecided_docket_is_a_noop() -> None:
    row = from_api_docket({"id": 7, "court_id": "ca9", "date_filed": "2024-01-01"})
    resolution = detect_resolution(row, "ca9", 7, ["evt-petition-review"])
    assert not resolution.outcomes
    assert not resolution.unrecorded


def test_no_open_events_is_a_noop() -> None:
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, [])
    assert not resolution.outcomes
    assert not resolution.unrecorded


def test_unreadable_disposition_lands_unrecorded() -> None:
    # "affirmed" normalizes to the `other` catch-all — decided, but not how.
    row = from_api_docket({**DECIDED_DOCKET, "disposition": "affirmed"})
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert not resolution.outcomes
    (req,) = resolution.unrecorded
    assert req.event_id == "evt-petition-review"
    assert "not machine-readable" in req.reason


def test_decided_without_date_lands_unrecorded() -> None:
    row = from_api_docket({"id": 64512345, "court_id": "ca9", "disposition": "Petition denied"})
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert not resolution.outcomes
    (req,) = resolution.unrecorded
    assert "no decision date" in req.reason


def test_multiple_open_events_land_unrecorded() -> None:
    # One case-level disposition cannot be attributed across several open events.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-motion-a", "evt-motion-b"])
    assert not resolution.outcomes
    assert {r.event_id for r in resolution.unrecorded} == {"evt-motion-a", "evt-motion-b"}
    assert all("cannot be attributed" in r.reason for r in resolution.unrecorded)


def test_a_lone_non_baseline_event_never_inherits_the_case_disposition() -> None:
    # A decided docket whose only open event is a motion: the cert disposition
    # belongs to the case-baseline event, and the motion resolves on its own
    # filing's terms — attributing across would write the petition's outcome
    # onto a stay.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(
        row, "ca9", 64512345, ["evt-motion-construe-the-application-for-a-stay"]
    )
    assert not resolution.outcomes
    (req,) = resolution.unrecorded
    assert req.event_id == "evt-motion-construe-the-application-for-a-stay"
    assert "forecasts a different filing" in req.reason


def test_a_lone_baseline_event_still_resolves() -> None:
    # The guard narrows attribution, never the baseline path itself: petition-
    # and appeal-kind ids (any slug) keep resolving exactly as before.
    row = from_api_docket(DECIDED_DOCKET)
    for event_id in ("evt-petition-review", "evt-appeal-disposition"):
        resolution = detect_resolution(row, "ca9", 64512345, [event_id])
        assert not resolution.unrecorded
        assert list(resolution.outcomes) == [event_id]


def test_stage_routes_the_cert_disposition_past_an_open_motion() -> None:
    # A cert petition and an interim motion both open on a decided docket: the
    # stage identifies the target unambiguously, so the cert-stage event gets
    # the case-level disposition and the motion stays open — neither resolved
    # nor surfaced for triage (it resolves on its own filing's terms).
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(
        row,
        "ca9",
        64512345,
        ["evt-petition-disposition", "evt-motion-stay"],
        stages={"evt-petition-disposition": Stage.cert, "evt-motion-stay": Stage.interim},
    )
    assert list(resolution.outcomes) == ["evt-petition-disposition"]
    assert not resolution.unrecorded  # the motion is not an ambiguity — it stays open


def test_stage_routing_works_beside_a_stage_less_motion_too() -> None:
    # The disambiguation needs only the cert event's own stage: a stage-less
    # motion beside it (a pre-vocabulary row) changes nothing.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(
        row,
        "ca9",
        64512345,
        ["evt-petition-disposition", "evt-motion-stay"],
        stages={"evt-petition-disposition": Stage.cert, "evt-motion-stay": None},
    )
    assert list(resolution.outcomes) == ["evt-petition-disposition"]
    assert not resolution.unrecorded


def test_two_stage_less_events_still_refuse() -> None:
    # No stage disambiguates, so the multi-open refusal holds verbatim.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(
        row,
        "ca9",
        64512345,
        ["evt-motion-a", "evt-motion-b"],
        stages={"evt-motion-a": None, "evt-motion-b": None},
    )
    assert not resolution.outcomes
    assert all("cannot be attributed" in r.reason for r in resolution.unrecorded)


def test_two_events_sharing_the_cert_stage_refuse() -> None:
    # The stage must identify the target *unambiguously*: two cert-staged
    # events (a data defect worth a human look) refuse rather than guess.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(
        row,
        "ca9",
        64512345,
        ["evt-petition-a", "evt-petition-b"],
        stages={"evt-petition-a": Stage.cert, "evt-petition-b": Stage.cert},
    )
    assert not resolution.outcomes
    assert {r.event_id for r in resolution.unrecorded} == {"evt-petition-a", "evt-petition-b"}
    assert all("cannot be attributed" in r.reason for r in resolution.unrecorded)


def test_an_unreadable_disposition_still_surfaces_every_open_event() -> None:
    # Stage routing narrows attribution, not triage: with nothing recordable
    # (the disposition normalizes to `other`), whole-docket triage is the
    # conservative call, so even a cert-staged event's interim sibling is
    # surfaced rather than silently left behind an unrecordable decision.
    row = from_api_docket({**DECIDED_DOCKET, "disposition": "affirmed"})
    resolution = detect_resolution(
        row,
        "ca9",
        64512345,
        ["evt-petition-disposition", "evt-motion-stay"],
        stages={"evt-petition-disposition": Stage.cert, "evt-motion-stay": Stage.interim},
    )
    assert not resolution.outcomes
    assert {r.event_id for r in resolution.unrecorded} == {
        "evt-petition-disposition",
        "evt-motion-stay",
    }
    assert all("not machine-readable" in r.reason for r in resolution.unrecorded)


def test_a_lone_interim_staged_event_never_inherits_the_cert_disposition() -> None:
    # An explicit non-cert stage opts the event out of the stage-less prefix
    # fallback: the cert disposition is not its outcome, whatever its id.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(
        row,
        "ca9",
        64512345,
        ["evt-motion-stay"],
        stages={"evt-motion-stay": Stage.interim},
    )
    assert not resolution.outcomes
    (req,) = resolution.unrecorded
    assert "forecasts a different filing" in req.reason


def test_attribution_prefixes_and_forecastable_kinds_agree() -> None:
    # Two encodings of "case-baseline" — the attribution guard keys on the id
    # prefix, the queue filter on the corpus kind column — must name the same
    # kinds, or targeting and attribution drift apart silently.
    assert set(CASE_BASELINE_ID_PREFIXES) == {f"evt-{kind}-" for kind in _FORECASTABLE_KINDS}


def test_scotus_baseline_only_kinds_match_the_attribution_prefixes() -> None:
    # A third encoding of the same set — the kinds a SCOTUS entry never mints an
    # event for. It must stay equal to the prefixes the case-level disposition
    # routes on: a kind in the router but not the mint guard re-opens the
    # two-baseline ambiguity, and one in the guard but not the router would have
    # the unmintable-event sweep delete events the guard still produces.
    assert {f"evt-{kind.value}-" for kind in _SCOTUS_BASELINE_ONLY_KINDS} == set(
        CASE_BASELINE_ID_PREFIXES
    )


# --- ledger write --------------------------------------------------------------


def test_record_outcomes_writes_outcome_and_marks_resolved(tmp_path: Path) -> None:
    _open_event(tmp_path)
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    written = record_outcomes(_db(tmp_path), tmp_path, "ca9", 64512345, resolution)
    assert written == ["evt-petition-review"]

    event_paths = CasePaths(tmp_path, "ca9", 64512345).event("evt-petition-review")
    written_outcome = read_model(event_paths.outcome, Outcome)
    assert written_outcome.actual_disposition == Disposition.denied
    # The event.yaml is materialized beside the outcome (resolved), so the
    # deterministic writers' straight-to-main commits never leave a referential
    # orphan for the offline validate gate to reject.
    materialized = read_model(event_paths.event_file, PredictableEvent)
    assert materialized.event_id == "evt-petition-review"
    assert materialized.resolved is True
    # The corpus event is flipped resolved so it stays consistent with its outcome.
    with corpus.connect(_db(tmp_path)) as conn:
        (event,) = corpus.events_for_case(conn, "ca9/64512345")
    assert event.resolved is True


def test_resolve_case_end_to_end(tmp_path: Path) -> None:
    _open_event(tmp_path)
    row = from_api_docket(DECIDED_DOCKET)
    resolution = resolve_case(_db(tmp_path), tmp_path, row, "ca9", 64512345)
    assert "evt-petition-review" in resolution.outcomes
    assert CasePaths(tmp_path, "ca9", 64512345).event("evt-petition-review").outcome.exists()


def test_resolve_case_routes_by_the_corpus_stage_and_leaves_the_motion_open(
    tmp_path: Path,
) -> None:
    # End-to-end stage plumb-through: the corpus holds a cert-staged petition
    # and an interim motion, both open. The refresh resolves the petition and
    # leaves the motion open in the corpus — no refusal, no motion outcome.
    _open_event(tmp_path, "evt-petition-disposition", stage=Stage.cert)
    _open_event(tmp_path, "evt-motion-stay", kind=EventKind.motion, stage=Stage.interim)
    row = from_api_docket(DECIDED_DOCKET)
    resolution = resolve_case(_db(tmp_path), tmp_path, row, "ca9", 64512345)
    assert list(resolution.outcomes) == ["evt-petition-disposition"]
    assert not resolution.unrecorded
    with corpus.connect(_db(tmp_path)) as conn:
        state = {e.event_id: e.resolved for e in corpus.events_for_case(conn, "ca9/64512345")}
    assert state == {"evt-petition-disposition": True, "evt-motion-stay": False}


def test_resolve_case_is_idempotent(tmp_path: Path) -> None:
    # A second refresh sees the event closed (corpus resolved flag) and does nothing.
    _open_event(tmp_path)
    row = from_api_docket(DECIDED_DOCKET)
    resolve_case(_db(tmp_path), tmp_path, row, "ca9", 64512345)
    again = resolve_case(_db(tmp_path), tmp_path, row, "ca9", 64512345)
    assert not again.outcomes
    assert not again.unrecorded


# --- merits event minting ------------------------------------------------------

GRANTED_SCOTUS_DOCKET = {
    "id": 22451,
    "court_id": "scotus",
    "docket_number": "22-451",
    "case_name": "Doe v. Roe",
    "date_cert_granted": "2022-10-03",
}


def _scotus_event(
    tmp_path: Path,
    event_id: str = "evt-petition-disposition",
    kind: EventKind = EventKind.petition,
    stage: Stage | None = Stage.cert,
    resolved: bool = False,
) -> None:
    event = corpus.CorpusEvent(
        event_id=event_id,
        case_id="scotus/22451",
        court="scotus",
        kind=kind,
        stage=stage,
        title="Doe v. Roe",
        resolved=resolved,
    )
    with corpus.connect(_db(tmp_path)) as conn:
        corpus.upsert_events(conn, [event])


def test_cert_grant_mints_the_open_merits_event(tmp_path: Path) -> None:
    """A recorded grant opens `evt-order-judgment`, after the attribution pass.

    The same pass that resolves the petition never sees the merits event among
    the open set — the outcomes carry the petition only, nothing lands
    unrecorded — and the minted event reaches both stores: an open corpus row
    (kind order, stage merits, opened at the grant) and its ledger event.yaml.
    """
    _scotus_event(tmp_path)
    row = from_api_docket(GRANTED_SCOTUS_DOCKET)
    resolution = resolve_case(_db(tmp_path), tmp_path, row, "scotus", 22451)
    assert list(resolution.outcomes) == ["evt-petition-disposition"]
    assert not resolution.unrecorded
    with corpus.connect(_db(tmp_path)) as conn:
        events = {e.event_id: e for e in corpus.events_for_case(conn, "scotus/22451")}
    merits = events[MERITS_EVENT_ID]
    assert merits.resolved is False
    assert merits.kind == EventKind.order
    assert merits.stage == Stage.merits
    assert merits.decision_target == "judgment"
    assert merits.opened_at == date(2022, 10, 3)  # the grant date
    assert merits.title == "Doe v. Roe"
    assert events["evt-petition-disposition"].resolved is True
    ledger = read_model(
        CasePaths(tmp_path, "scotus", 22451).event(MERITS_EVENT_ID).event_file,
        PredictableEvent,
    )
    assert ledger.resolved is False
    assert ledger.stage == Stage.merits.value
    assert ledger.decision_target == "judgment"


def test_gvr_and_summary_reversal_mint_no_merits_event() -> None:
    # Both terminate the case at the cert order itself — a GVR vacates and
    # remands in the grant order, a summary reversal decides the merits there —
    # so no merits proceeding follows and nothing is minted.
    row = from_api_docket(GRANTED_SCOTUS_DOCKET)

    def resolution_with(disposition: Disposition) -> Resolution:
        return Resolution(
            outcomes={
                "evt-petition-disposition": Outcome(
                    case_id="scotus/22451",
                    event_id="evt-petition-disposition",
                    resolved_at=date(2022, 10, 3),
                    actual_disposition=disposition,
                    actual_granted=granted_flag(disposition),
                )
            }
        )

    assert merits_event_for(row, resolution_with(Disposition.gvr)) is None
    assert merits_event_for(row, resolution_with(Disposition.summary_reversal)) is None
    assert merits_event_for(row, resolution_with(Disposition.denied)) is None
    minted = merits_event_for(row, resolution_with(Disposition.granted))
    assert minted is not None and minted.event_id == MERITS_EVENT_ID
    partial = merits_event_for(row, resolution_with(Disposition.granted_in_part))
    assert partial is not None


def test_minting_never_reopens_a_resolved_merits_event(tmp_path: Path) -> None:
    # Re-detection after the judgment has closed the merits event must not
    # reopen it: the events upsert MAX-latches `resolved`, and the ledger
    # event.yaml is written from the post-upsert state so it honours the same
    # latch rather than regressing the committed definition to open.
    _scotus_event(tmp_path)
    row = from_api_docket(GRANTED_SCOTUS_DOCKET)
    resolution = resolve_case(_db(tmp_path), tmp_path, row, "scotus", 22451)
    with corpus.connect(_db(tmp_path)) as conn:
        corpus.set_event_resolved(conn, "scotus/22451", MERITS_EVENT_ID)
    mint_merits_event(_db(tmp_path), tmp_path, "scotus", 22451, row, resolution)
    with corpus.connect(_db(tmp_path)) as conn:
        events = {e.event_id: e for e in corpus.events_for_case(conn, "scotus/22451")}
    assert events[MERITS_EVENT_ID].resolved is True
    ledger = read_model(
        CasePaths(tmp_path, "scotus", 22451).event(MERITS_EVENT_ID).event_file,
        PredictableEvent,
    )
    assert ledger.resolved is True


def test_minting_is_scotus_only() -> None:
    # The shared resolution seam also records granted dispositions on circuit
    # dockets; those open no merits proceeding before the Court, so no
    # cert-vocabulary merits event may be minted for them.
    row = from_api_docket(
        {
            "id": 64512345,
            "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
            "docket_number": "21-55555",
            "case_name": "Doe v. Roe",
            "date_terminated": "2022-06-15",
            "disposition": "Petition granted",
        }
    )
    resolution = Resolution(
        outcomes={
            "evt-petition-review": Outcome(
                case_id="ca9/64512345",
                event_id="evt-petition-review",
                resolved_at=date(2022, 6, 15),
                actual_disposition=Disposition.granted,
                actual_granted=1,
            )
        }
    )
    assert merits_event_for(row, resolution) is None


def test_granted_docket_repoll_is_a_clean_noop(tmp_path: Path) -> None:
    """The re-poll shape a retained granted docket presents, end to end.

    The petition event is resolved, the merits event open with stage merits,
    and the row still carries the granted disposition and cert date. Nothing is
    recorded (the cert disposition already has its resolved home), nothing is
    surfaced for triage, and the merits event neither resolves nor duplicates.
    """
    _scotus_event(tmp_path)
    row = from_api_docket(GRANTED_SCOTUS_DOCKET)
    resolve_case(_db(tmp_path), tmp_path, row, "scotus", 22451)
    again = resolve_case(_db(tmp_path), tmp_path, row, "scotus", 22451)
    assert not again.outcomes
    assert not again.unrecorded
    with corpus.connect(_db(tmp_path)) as conn:
        events = corpus.events_for_case(conn, "scotus/22451")
    assert {e.event_id: e.resolved for e in events} == {
        "evt-petition-disposition": True,
        MERITS_EVENT_ID: False,
    }


def test_decided_row_beside_a_resolved_cert_event_is_a_noop() -> None:
    # The pure form of the re-poll guard: the case-level disposition belongs to
    # the already-resolved cert event, so the open merits event is not triaged.
    row = from_api_docket(GRANTED_SCOTUS_DOCKET)
    stages: dict[str, Stage | None] = {
        "evt-petition-disposition": Stage.cert,
        MERITS_EVENT_ID: Stage.merits,
    }
    resolution = detect_resolution(
        row,
        "scotus",
        22451,
        [MERITS_EVENT_ID],
        stages=stages,
        resolved_event_ids=["evt-petition-disposition"],
    )
    assert not resolution.outcomes
    assert not resolution.unrecorded
    # A stage-less resolved baseline event carries the disposition just the same.
    resolution = detect_resolution(
        row,
        "scotus",
        22451,
        [MERITS_EVENT_ID],
        stages={MERITS_EVENT_ID: Stage.merits, "evt-petition-disposition": None},
        resolved_event_ids=["evt-petition-disposition"],
    )
    assert not resolution.outcomes and not resolution.unrecorded
    # Without a resolved home for the disposition the conservative surface stays.
    resolution = detect_resolution(
        row, "scotus", 22451, [MERITS_EVENT_ID], stages={MERITS_EVENT_ID: Stage.merits}
    )
    assert resolution.unrecorded


def test_the_noop_guard_yields_to_news_the_row_carries() -> None:
    """A docket-level decision date or a mutated disposition re-opens triage.

    The no-op covers exactly the retained-granted re-poll shape. When
    `date_decided` latches without a judgment-shaped entry to parse (an
    upstream termination the merits branch cannot read) or the disposition
    stops telling the recorded grant's story (a DIG relabeled `dismissed`),
    the poll is news, and the conservative surface must carry it to the
    maintainer.
    """
    stages: dict[str, Stage | None] = {
        "evt-petition-disposition": Stage.cert,
        MERITS_EVENT_ID: Stage.merits,
    }
    decided = from_api_docket(GRANTED_SCOTUS_DOCKET | {"date_terminated": "2023-06-30"})
    resolution = detect_resolution(
        decided,
        "scotus",
        22451,
        [MERITS_EVENT_ID],
        stages=stages,
        resolved_event_ids=["evt-petition-disposition"],
    )
    assert resolution.unrecorded
    mutated = from_api_docket(GRANTED_SCOTUS_DOCKET | {"disposition": "Petition dismissed"})
    resolution = detect_resolution(
        mutated,
        "scotus",
        22451,
        [MERITS_EVENT_ID],
        stages=stages,
        resolved_event_ids=["evt-petition-disposition"],
    )
    assert resolution.unrecorded


def test_record_outcomes_refuses_an_orphaned_outcome(tmp_path: Path) -> None:
    # A resolution for an event the corpus does not hold is an internal
    # inconsistency: fail before writing, never commit an outcome the offline
    # validate gate would reject as a referential orphan.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    with pytest.raises(RuntimeError, match="orphaned outcome"):
        record_outcomes(_db(tmp_path), tmp_path, "ca9", 64512345, resolution)
    assert not CasePaths(tmp_path, "ca9", 64512345).event("evt-petition-review").outcome.exists()


def test_termination_signal_reads_the_clerks_termination_entry() -> None:
    # A stale CA docket often carries no date_terminated/disposition, yet its
    # latest entry states the matter is over — the signal appears_decided
    # cannot see.
    docket = {
        "id": 1,
        "docket_entries": [
            {"id": 10, "description": "Briefing complete"},
            {"id": 11, "description": "Case termination for order and judgment"},
        ],
    }
    signal = termination_signal(docket)
    assert signal is not None and "Case termination" in signal


def test_termination_signal_reads_the_opinion_issued_entry() -> None:
    docket = {"id": 1, "docket_entries": [{"id": 10, "short_description": "Opinion Issued."}]}
    signal = termination_signal(docket)
    assert signal is not None and "Opinion Issued" in signal


def test_termination_signal_only_reads_the_latest_entry() -> None:
    # Pendency is event-level: a filing *after* a terminal entry (a
    # stay-the-mandate motion, a rehearing petition) reopens the docket, so
    # the earlier terminal entry must not starve the later event.
    docket = {
        "id": 1,
        "docket_entries": [
            {"id": 10, "description": "Opinion Issued."},
            {"id": 11, "description": "Motion to stay the mandate"},
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_ignores_a_cluster_link_alone() -> None:
    # A linked opinion cluster alone is deliberately not a signal: a
    # motions-panel opinion can publish on a still-pending appeal.
    docket = {
        "id": 1,
        "docket_entries": [{"id": 10, "description": "Filed"}],
        "clusters": ["https://www.courtlistener.com/api/rest/v4/clusters/10122744/"],
    }
    assert termination_signal(docket) is None


def test_termination_signal_none_for_a_pending_docket() -> None:
    # Routine entries — including ones that merely *mention* an opinion — read
    # as pending; only the anchored terminal phrasings match.
    docket = {
        "id": 1,
        "docket_entries": [
            {"id": 10, "description": "Motion to stay pending appeal"},
            {"id": 11, "description": "Citing the opinion issued in a related case"},
        ],
        "clusters": [],
    }
    assert termination_signal(docket) is None


def test_termination_signal_reads_a_rule_398_ifp_dismissal() -> None:
    # A Rule 39.8 IFP-denial/dismissal the cert-disposition resolver does not
    # match (the noun and verb are many words apart); the routing backstop does.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion for leave to proceed in forma pauperis DENIED and petition "
                    "for a writ of habeas corpus DISMISSED. See Rule 39.8."
                ),
            }
        ],
    }
    signal = termination_signal(docket)
    assert signal is not None and "39.8" in signal


def test_termination_signal_reads_a_bare_rule_398_filing_bar() -> None:
    # An abusive-filer Rule 39.8 bar with no "petition ... dismissed" verb: only
    # the rule-39.8 alternation can catch it, so this pins that branch specifically.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion for leave to proceed in forma pauperis DENIED. See Rule 39.8."
                ),
            }
        ],
    }
    assert termination_signal(docket) is not None


def test_termination_signal_reads_a_fee_default_closure() -> None:
    docket = {"id": 1, "docket_entries": [{"id": 10, "description": "Case considered closed."}]}
    assert termination_signal(docket) is not None


def test_termination_signal_ignores_an_ifp_denial_with_a_fee_deadline() -> None:
    # The initial IFP denial that only sets a payment deadline is NOT terminal:
    # the petition may still proceed on payment, so it must stay predictable —
    # the later closure/dismissal entry, not this denial, is the terminal signal.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion for leave to proceed in forma pauperis is denied. Petitioner "
                    "allowed until Nov 12 2025, to pay the docketing fee. Rule 33.1."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_reads_a_gvr_vacate_and_remand_order() -> None:
    # The GVR shape the cert-disposition resolver's grant-anchored patterns
    # miss: a bare vacate-and-remand order carries no "grant" word and no
    # literal "GVR" token, yet the matter is decided. This is the exact entry
    # that leaked already-decided SCOTUS dockets into forward cells.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Judgment VACATED and case REMANDED for further consideration "
                    "in light of Louisiana v. Callais."
                ),
            }
        ],
    }
    signal = termination_signal(docket)
    assert signal is not None and "VACATED" in signal


def test_termination_signal_reads_the_judgment_issued_entry() -> None:
    # "Judgment Issued" is the SCOTUS mandate analog — it follows the
    # disposition order, so it is often the *latest* entry and the only
    # terminal-shaped text the latest-entry rule can see.
    docket = {"id": 1, "docket_entries": [{"id": 10, "description": "Judgment Issued."}]}
    assert termination_signal(docket) is not None


def test_termination_signal_ignores_a_vacatur_without_a_remand() -> None:
    # An interim vacatur (a stay vacated, an order vacated on rehearing) does
    # not end the matter; only the vacate-and-remand pair reads terminal.
    docket = {
        "id": 1,
        "docket_entries": [{"id": 10, "description": "Order vacating the stay entered."}],
    }
    assert termination_signal(docket) is None


def test_termination_signal_ignores_a_vacate_and_remand_motion() -> None:
    # The SG's confession-of-error *motion* asks for a vacate-and-remand but
    # decides nothing — the verb precedes "judgment", which the disposition
    # noun-verb shape ("judgment ... vacated ... remand") does not match.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion of respondent to vacate the judgment and remand the case "
                    "for further proceedings filed."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_ignores_an_en_banc_panel_opinion_vacatur() -> None:
    # Rehearing en banc vacates the *panel opinion* and remands to the panel —
    # the appeal is very much alive, and no "judgment" anchors the pair.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Rehearing en banc GRANTED. The panel opinion is VACATED and "
                    "the case is REMANDED to the panel."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_ignores_a_judgment_issued_recital() -> None:
    # A docketing recital that merely *mentions* an issued judgment ("NOTICE OF
    # APPEAL filed from the judgment issued on ...") opens a matter rather than
    # closing one; only the start-anchored bare "Judgment Issued" entry counts.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "NOTICE OF APPEAL filed from the judgment issued on 03/04/2026 "
                    "by the district court."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_reads_a_cert_before_judgment_denial() -> None:
    # The CBJ denial is a deliberate resolver miss (its multi-word noun-verb
    # gap would also admit the expedite-motion recital), so routing is its
    # only net — the denied-CBJ docket goes quiet with this as its latest entry.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": "Petition for a writ of certiorari before judgment denied.",
            }
        ],
    }
    assert termination_signal(docket) is not None
    # The consolidated-docket plural form terminates the same way.
    plural = {
        "id": 2,
        "docket_entries": [
            {
                "id": 10,
                "description": "Petitions for writs of certiorari before judgment denied.",
            }
        ],
    }
    assert termination_signal(plural) is not None


def test_termination_signal_ignores_a_cbj_expedite_motion_order() -> None:
    # The order on an expedite motion recites the same noun phrase but opens
    # with "Motion ..." — a pending CBJ docket must never be parked out of the
    # forward queue by its own scheduling order.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Motion of petitioners to expedite consideration of the "
                    "petition for a writ of certiorari before judgment denied."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_reads_a_cert_before_judgment_grant() -> None:
    # The grant half of the CBJ disposition, symmetric with the denial: once
    # cert-before-judgment is granted the petition-disposition event is decided,
    # so the docket must route out of the forward queue with the grant latest.
    # The resolver now reads this grant at ingest too; this routing backstop
    # stays as defense in depth (a pre-resolution or replay snapshot).
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": "Petition for a writ of certiorari before judgment GRANTED",
            }
        ],
    }
    assert termination_signal(docket) is not None
    # The common order-list phrasing opens with "The petition ..."; the backstop
    # (and the leakage-guard whole-snapshot scan it shares) must catch that form
    # too, matching the shapes the resolver now records.
    the_form = {
        "id": 2,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "The petition for a writ of certiorari before judgment is granted."
                ),
            }
        ],
    }
    assert termination_signal(the_form) is not None
    # The grant is caught on the raw live payload shape too — the window before
    # argument where the grant is the latest entry, which would otherwise leak.
    live = {
        "CaseNumber": "24-1000 ",
        "ProceedingsandOrder": [
            {
                "Date": "Oct 24 2025",
                "Text": "Petition for a writ of certiorari before judgment filed.",
            },
            {
                "Date": "Dec 05 2025",
                "Text": "Petition for a writ of certiorari before judgment GRANTED",
            },
        ],
    }
    assert termination_signal(live) is not None


def test_termination_signal_reads_a_scotus_merits_judgment() -> None:
    # The Court has entered judgment, so nothing about the petition is pending.
    # Both the "Adjudged to be ..." order-list form and the bare "Judgment
    # ..." form read terminal.
    adjudged = {"id": 1, "docket_entries": [{"id": 10, "description": "Adjudged to be AFFIRMED."}]}
    assert termination_signal(adjudged) is not None
    reversed_ = {"id": 2, "docket_entries": [{"id": 10, "description": "Judgment REVERSED."}]}
    assert termination_signal(reversed_) is not None


def test_termination_signal_ignores_a_merits_disposition_recital() -> None:
    # A history recital that merely *names* a below judgment being affirmed
    # opens the matter ("Notice of appeal ..."), so it must not read terminal —
    # only the start-anchored disposition entry counts.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "Notice of appeal filed from the judgment affirmed by the "
                    "Court of Appeals on 02/01/2026."
                ),
            }
        ],
    }
    assert termination_signal(docket) is None


def test_termination_signal_reads_a_decided_cbj_docket_on_the_live_shape() -> None:
    # Regression for the leak three engines flagged: a cert-before-judgment
    # docket that was granted, argued, and decided on the merits reached a
    # forward predict cell with the outcome in view. Its latest entry is the
    # merits judgment, which no branch read before; the raw live payload shape
    # is exactly what the live channel stores and provisions.
    docket = {
        "CaseNumber": "24-1000 ",
        "ProceedingsandOrder": [
            {
                "Date": "Oct 24 2025",
                "Text": "Petition for a writ of certiorari before judgment filed.",
            },
            {
                "Date": "Dec 05 2025",
                "Text": "Petition for a writ of certiorari before judgment GRANTED",
            },
            {"Date": "Apr 01 2026", "Text": "Argued. For petitioner: ... For respondent: ..."},
            {"Date": "Jun 30 2026", "Text": "Adjudged to be AFFIRMED."},
        ],
    }
    assert termination_signal(docket) is not None


def test_termination_signal_reads_a_circuit_vacate_and_remand_disposition() -> None:
    # The CA disposition shape carries the same judgment-vacated-remand
    # noun-verb order as the SCOTUS GVR, so the one pattern covers both.
    docket = {
        "id": 1,
        "docket_entries": [
            {
                "id": 10,
                "description": (
                    "OPINION filed. The judgment of the district court is VACATED "
                    "and the case is REMANDED for further proceedings."
                ),
            }
        ],
    }
    assert termination_signal(docket) is not None


def test_termination_signal_reads_the_raw_live_payload_shape() -> None:
    # The live channel stores the supremecourt.gov JSON verbatim as the
    # point-in-time snapshot: proceedings ride under ProceedingsandOrder/Text,
    # not docket_entries/description. The signal must read both shapes.
    docket = {
        "CaseNumber": "25-274 ",
        "ProceedingsandOrder": [
            {"Date": "Jun 01 2026", "Text": "Petition for a writ of certiorari filed."},
            {"Date": "May 11 2026", "Text": "Judgment Issued."},
        ],
    }
    assert termination_signal(docket) is not None


def test_termination_signal_latest_entry_rule_holds_on_the_live_shape() -> None:
    # Same pendency semantics on the raw shape: an administrative notation
    # after the terminal entry is the latest described entry, so the
    # latest-entry rule reads the docket as active — provisioning's
    # whole-snapshot disposition scan, not this signal, covers that tail.
    docket = {
        "CaseNumber": "25-274 ",
        "ProceedingsandOrder": [
            {"Date": "May 11 2026", "Text": "Judgment Issued."},
            {"Date": "May 11 2026", "Text": "Application (25A1231) denied as moot."},
        ],
    }
    assert termination_signal(docket) is None


def test_snapshot_shows_disposition_catches_a_cbj_grant_masked_by_trailing_cleanup() -> None:
    # The leak shape (scotus/25-243): a cert-before-judgment GRANT is decided,
    # but the docket tail carries post-disposition cleanup ("Judgment Issued", a
    # stay application denied as moot). termination_signal (latest entry) misses
    # it; the whole-snapshot scan the provisioning leakage guard uses catches it.
    docket = {
        "CaseNumber": "25-243 ",
        "ProceedingsandOrder": [
            {"Date": "May 11 2026", "Text": "Motion to expedite GRANTED."},
            {
                "Date": "May 11 2026",
                "Text": "Petition for writ of certiorari before judgment GRANTED.",
            },
            {"Date": "May 11 2026", "Text": "Judgment Issued."},
            {
                "Date": "May 11 2026",
                "Text": "Application (25A1229) denied as moot by Justice Thomas.",
            },
        ],
    }
    assert termination_signal(docket) is None  # latest-entry rule still misses it
    signal = snapshot_shows_disposition(docket)
    assert signal is not None and "certiorari before judgment GRANTED" in signal


def test_snapshot_shows_disposition_none_for_a_pending_snapshot() -> None:
    # No disposition-shaped entry anywhere — a live, pending petition.
    docket = {
        "CaseNumber": "25-900 ",
        "ProceedingsandOrder": [
            {"Date": "Jun 01 2026", "Text": "Petition for a writ of certiorari filed."},
            {"Date": "Jul 01 2026", "Text": "Brief of respondents in opposition filed."},
            {"Date": "Jul 08 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."},
        ],
    }
    assert snapshot_shows_disposition(docket) is None


def test_disposition_basis_reads_the_payload_and_threads_into_the_outcome() -> None:
    munsingwear = {
        "CaseNumber": "25-100 ",
        "ProceedingsandOrder": [
            {"Date": "Jun 01 2026", "Text": "Petition for a writ of certiorari filed."},
            {
                "Date": "May 11 2026",
                "Text": (
                    "Judgment VACATED and case REMANDED with instructions to "
                    "dismiss the case as moot."
                ),
            },
        ],
    }
    assert disposition_basis(munsingwear) == "mootness"
    plain = {
        "id": 1,
        "docket_entries": [{"id": 10, "description": "Petition DENIED."}],
    }
    assert disposition_basis(plain) == "standard"
    assert disposition_basis({"id": 2, "docket_entries": []}) == "standard"

    # The basis lands on the written ground truth.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(
        row, "ca9", 64512345, ["evt-petition-review"], disposition_basis="mootness"
    )
    assert resolution.outcomes["evt-petition-review"].disposition_basis == "mootness"
    # And defaults to standard when the channel passes nothing.
    default = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert default.outcomes["evt-petition-review"].disposition_basis == "standard"


def test_resolution_signals_are_frozen_onto_the_outcome() -> None:
    """The signals a cert-stage forecast resolves against are copied out of the
    mutable corpus columns and into the immutable record, so re-scoring the same
    cell later reads what was true at resolution rather than what is true now."""
    signals = resolution_signals(3, date(2026, 2, 1))
    assert signals is not None
    assert signals.distribution_count == 3  # two relists
    assert signals.cvsg_date == date(2026, 2, 1)


def test_unparsed_proceedings_record_no_signals_at_all() -> None:
    """`distribution_count` is the corpus's coverage sentinel for the whole
    live-signal family, so where it is absent nothing was observed — and the block
    must be absent rather than present-with-nulls, or a reader cannot tell 'no
    CVSG' from 'never looked'."""
    assert resolution_signals(None, None) is None
    assert resolution_signals(None, date(2026, 2, 1)) is None


def test_a_parsed_petition_with_no_cvsg_says_so_unambiguously() -> None:
    # The distinction the block exists to make: inside it, a null CVSG date is a
    # statement that none was called for, not a gap in the record.
    signals = resolution_signals(1, None)
    assert signals is not None
    assert signals.distribution_count == 1  # distributed once, never relisted
    assert signals.cvsg_date is None


def test_an_outcome_written_before_the_block_existed_still_parses() -> None:
    """Every committed outcome predates the field, so its payload has no `signals`
    key at all — not a null one. Reading the absent shape is what proves the
    2971 records on disk keep validating."""
    payload = {
        "schema_version": "1.0",
        "case_id": "ca9/1",
        "event_id": "evt-petition-review",
        "resolved_at": "2026-01-01",
        "actual_disposition": "denied",
        "actual_granted": 0,
    }
    assert "signals" not in payload
    outcome = Outcome.model_validate(payload)
    assert outcome.signals is None


# --- merits detection: a parsed judgment resolves the merits event ---------------

_MERITS_STAGES: dict[str, Stage | None] = {
    "evt-petition-disposition": Stage.cert,
    MERITS_EVENT_ID: Stage.merits,
}


def _judged_row(judgment: str = "reversed", decided: str | None = "2023-06-27") -> CorpusRow:
    """The retained granted docket's re-poll row once the judgment latched.

    Built over the API-shaped grant and stamped with the merits pair the live
    channel's ingest parse latches (`map_live_docket`); the parse path itself
    is pinned in test_ingest.
    """
    row = from_api_docket(GRANTED_SCOTUS_DOCKET)
    return row.model_copy(
        update={
            "merits_judgment": judgment,
            "merits_decided": date.fromisoformat(decided) if decided else None,
        }
    )


def test_a_parsed_judgment_resolves_the_open_merits_event() -> None:
    resolution = detect_resolution(
        _judged_row(),
        "scotus",
        22451,
        [MERITS_EVENT_ID],
        stages=_MERITS_STAGES,
        resolved_event_ids=["evt-petition-disposition"],
    )
    assert not resolution.unrecorded
    outcome = resolution.outcomes[MERITS_EVENT_ID]
    # The merits mapping: the judgment axis carries the result, the cert
    # vocabulary's catch-all records that no cert label applies, and the
    # declared binary is the disturbed projection.
    assert outcome.judgment == "reversed"
    assert outcome.actual_disposition == Disposition.other
    assert outcome.actual_granted == 1
    assert outcome.resolved_at == date(2023, 6, 27)
    # No vote record: the entry text cannot honestly yield a provenance block.
    assert outcome.votes == [] and outcome.vote_provenance is None


def test_the_two_procedural_exits_resolve_undisturbed() -> None:
    for judgment in ("dismissed-as-improvidently-granted", "affirmed-by-an-equally-divided-court"):
        resolution = detect_resolution(
            _judged_row(judgment),
            "scotus",
            22451,
            [MERITS_EVENT_ID],
            stages=_MERITS_STAGES,
            resolved_event_ids=["evt-petition-disposition"],
        )
        outcome = resolution.outcomes[MERITS_EVENT_ID]
        assert outcome.judgment == judgment
        assert outcome.actual_granted == 0  # the judgment below stands


def test_an_undated_judgment_parse_surfaces_the_merits_event() -> None:
    # A judgment with no fully specified entry date has no resolved_at to
    # stamp; the conservative surface carries it to the maintainer.
    resolution = detect_resolution(
        _judged_row(decided=None),
        "scotus",
        22451,
        [MERITS_EVENT_ID],
        stages=_MERITS_STAGES,
        resolved_event_ids=["evt-petition-disposition"],
    )
    assert not resolution.outcomes
    [unrecorded] = resolution.unrecorded
    assert unrecorded.event_id == MERITS_EVENT_ID
    assert "undated" in unrecorded.reason


def test_an_out_of_vocabulary_judgment_surfaces_rather_than_raising() -> None:
    # `merits_judgment` is blob-tolerant TEXT whose readers re-validate against
    # the vocabulary rather than failing the row — the same contract the
    # cascade's replay keeps. A corrupt value must reach the maintainer through
    # the conservative surface, never as an exception out of the live poll.
    resolution = detect_resolution(
        _judged_row("remanded-with-prejudice"),
        "scotus",
        22451,
        [MERITS_EVENT_ID],
        stages=_MERITS_STAGES,
        resolved_event_ids=["evt-petition-disposition"],
    )
    assert not resolution.outcomes
    [unrecorded] = resolution.unrecorded
    assert unrecorded.event_id == MERITS_EVENT_ID
    assert "out of vocabulary" in unrecorded.reason


def test_the_merits_branch_leaves_other_open_events_alone() -> None:
    # An entry-pinned motion open beside the merits event resolves on its own
    # filing's terms: the judgment closes the merits event only.
    resolution = detect_resolution(
        _judged_row(),
        "scotus",
        22451,
        [MERITS_EVENT_ID, "evt-motion-stay"],
        stages=_MERITS_STAGES | {"evt-motion-stay": None},
        resolved_event_ids=["evt-petition-disposition"],
    )
    assert list(resolution.outcomes) == [MERITS_EVENT_ID]
    assert not resolution.unrecorded


def test_the_judged_repoll_resolves_end_to_end(tmp_path: Path) -> None:
    """Grant → mint → judged re-poll → the merits outcome lands and the event closes."""
    _scotus_event(tmp_path)
    grant_row = from_api_docket(GRANTED_SCOTUS_DOCKET)
    resolve_case(_db(tmp_path), tmp_path, grant_row, "scotus", 22451)
    resolution = resolve_case(_db(tmp_path), tmp_path, _judged_row(), "scotus", 22451)
    assert list(resolution.outcomes) == [MERITS_EVENT_ID]
    assert not resolution.unrecorded
    with corpus.connect(_db(tmp_path)) as conn:
        events = {e.event_id: e.resolved for e in corpus.events_for_case(conn, "scotus/22451")}
    assert events == {"evt-petition-disposition": True, MERITS_EVENT_ID: True}
    written = read_model(
        CasePaths(tmp_path, "scotus", 22451).event(MERITS_EVENT_ID).outcome, Outcome
    )
    assert written.judgment == "reversed" and written.actual_granted == 1
    # And a further re-poll of the fully-decided docket is a clean no-op: no
    # open events remain, so detection has nothing to do.
    again = resolve_case(_db(tmp_path), tmp_path, _judged_row(), "scotus", 22451)
    assert not again.outcomes and not again.unrecorded


def test_a_granted_application_mints_no_merits_event() -> None:
    """A granted stay is a SCOTUS grant that opens no merits proceeding.

    The interim and cert vocabularies share the `granted` label, so the mint
    cannot key on the disposition alone: an application that the Court grants
    is finished at that order and will never enter a merits proceeding, but it
    reaches the same resolution seam a cert grant does. Minting there would put
    a judgment forecast on a docket with no judgment to forecast — inert only
    while interim events carry no stage, and a live bug the moment they do.
    """
    application = CorpusRow(
        case_id="scotus/900001",
        court="scotus",
        docket_id=900001,
        source="live",
        docket_number="24A100",
        case_name="Doe v. Roe",
        application_kind="substantive",
        disposition=Disposition.granted,
        # The application ingest branch nulls the cert-stage dates by design;
        # that is exactly what `opens_merits_proceeding` keys on.
        date_cert_granted=None,
    )
    resolution = Resolution(
        outcomes={
            "evt-motion-disposition": Outcome(
                case_id="scotus/900001",
                event_id="evt-motion-disposition",
                resolved_at=date(2025, 3, 4),
                actual_disposition=Disposition.granted,
                actual_granted=1,
            )
        }
    )
    assert merits_event_for(application, resolution) is None


def test_a_circuit_grant_mints_no_merits_event() -> None:
    """The other non-cert grant that reaches this seam: pull refreshes every court."""
    circuit = CorpusRow(
        case_id="ca9/123",
        court="ca9",
        docket_id=123,
        source="api",
        docket_number="22-15044",
        disposition=Disposition.granted,
        date_cert_granted=date(2025, 1, 2),  # meaningless off SCOTUS; still refused
    )
    resolution = Resolution(
        outcomes={
            "evt-appeal-disposition": Outcome(
                case_id="ca9/123",
                event_id="evt-appeal-disposition",
                resolved_at=date(2025, 3, 4),
                actual_disposition=Disposition.granted,
                actual_granted=1,
            )
        }
    )
    assert merits_event_for(circuit, resolution) is None
