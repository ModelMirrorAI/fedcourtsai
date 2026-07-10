from datetime import date
from typing import Any

from fedcourtsai.pipeline.events import extract_events
from fedcourtsai.pipeline.ingest import from_bulk_row
from fedcourtsai.schemas import EventKind


def _docket(entries: list[dict[str, Any]], **kw: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": 555,
        "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
        "case_name": "Doe v. Roe",
        "date_filed": "2026-06-01",
        "docket_entries": entries,
    }
    base.update(kw)
    return base


def _entry(
    entry_id: int, description: str, *, number: int | None = None, date_filed: str = "2026-06-02"
) -> dict[str, Any]:
    entry: dict[str, Any] = {"id": entry_id, "description": description, "date_filed": date_filed}
    if number is not None:
        entry["entry_number"] = number
    return entry


def _by_kind(events: list[Any]) -> dict[EventKind, list[Any]]:
    out: dict[EventKind, list[Any]] = {}
    for e in events:
        out.setdefault(EventKind(e.kind), []).append(e)
    return out


def test_baseline_event_always_present_even_without_entries() -> None:
    result = extract_events(_docket([]))
    assert [e.event_id for e in result.events] == ["evt-appeal-disposition"]
    assert result.ambiguous == []


def test_scotus_baseline_is_a_petition() -> None:
    docket = _docket([], court="https://www.courtlistener.com/api/rest/v4/courts/scotus/")
    result = extract_events(docket)
    assert result.events[0].event_id == "evt-petition-disposition"


def test_scotus_administrative_motions_extract_no_event() -> None:
    # Extensions of time (and IFP/amicus leave) are filed on nearly every
    # petition and granted as a matter of course — an open event for each would
    # drag decided cases into the predict queue forever (#472). Substantive
    # applications still extract.
    docket = _docket(
        [
            _entry(1, "Motion to extend the time to file a response filed.", number=1),
            _entry(2, "Motion for leave to proceed in forma pauperis filed.", number=2),
        ],
        court="https://www.courtlistener.com/api/rest/v4/courts/scotus/",
    )
    result = extract_events(docket)
    assert [e.event_id for e in result.events] == ["evt-petition-disposition"]


def test_scotus_petition_entry_collapses_into_the_baseline() -> None:
    # At SCOTUS the petition *is* the case: the cert-petition filing entry must
    # not mint a second open petition event beside evt-petition-disposition, or
    # every deterministic resolution turns two-events-ambiguous (#472). A stay
    # motion on the same docket still extracts as its own event.
    docket = _docket(
        [
            _entry(1, "Petition for a writ of certiorari filed.", number=1),
            _entry(2, "MOTION for stay pending disposition filed by Applicant", number=2),
        ],
        court="https://www.courtlistener.com/api/rest/v4/courts/scotus/",
    )
    result = extract_events(docket)
    assert [e.event_id for e in result.events] == [
        "evt-petition-disposition",
        "evt-motion-stay-pending-disposition",
    ]
    assert result.ambiguous == []


def test_motion_entry_becomes_predictable_event() -> None:
    result = extract_events(
        _docket([_entry(10, "MOTION for stay pending appeal filed by Appellant", number=10)])
    )
    motions = _by_kind(result.events)[EventKind.motion]
    assert len(motions) == 1
    event = motions[0]
    assert event.event_id == "evt-motion-stay-pending-appeal"
    assert event.docket_entry_id == 10
    assert event.opened_at == date(2026, 6, 2)
    assert event.description.startswith("MOTION for stay")
    assert event.resolved is False  # no disposing order references it


def test_disposing_order_referencing_entry_number_resolves_it() -> None:
    result = extract_events(
        _docket(
            [
                _entry(10, "MOTION for stay pending appeal", number=10),
                _entry(11, "ORDER granting motion, Dkt. 10", number=11),
            ]
        )
    )
    motion = _by_kind(result.events)[EventKind.motion][0]
    assert motion.resolved is True
    # The disposing order is not itself emitted as a predictable event.
    assert EventKind.order not in _by_kind(result.events)


def test_disposing_order_without_reference_leaves_request_predictable() -> None:
    result = extract_events(
        _docket(
            [
                _entry(10, "MOTION for stay pending appeal", number=10),
                _entry(11, "ORDER granting the motion", number=11),
            ]
        )
    )
    motion = _by_kind(result.events)[EventKind.motion][0]
    # No docket-entry citation ⇒ we do not guess which request it closed.
    assert motion.resolved is False


def test_ambiguous_entry_is_flagged_not_guessed() -> None:
    result = extract_events(
        _docket([_entry(12, "MOTION for leave to file petition for rehearing en banc", number=12)])
    )
    # Matches both motion and petition — surfaced for an agent, not classified.
    assert all(e.kind != EventKind.motion or e.docket_entry_id != 12 for e in result.events)
    assert len(result.ambiguous) == 1
    amb = result.ambiguous[0]
    assert amb.case_id == "ca9/555"
    assert amb.entry_id == 12
    assert "motion" in amb.reason and "petition" in amb.reason


def test_routine_entries_produce_no_event() -> None:
    result = extract_events(
        _docket(
            [
                _entry(1, "Notice of appearance filed by counsel"),
                _entry(2, "ORDER setting briefing schedule"),  # order, no disposition verb
                _entry(3, "Transcript filed"),
            ]
        )
    )
    # Only the case-level baseline survives.
    assert [e.event_id for e in result.events] == ["evt-appeal-disposition"]
    assert result.ambiguous == []


def test_two_like_motions_get_distinct_event_ids() -> None:
    result = extract_events(
        _docket(
            [
                _entry(20, "MOTION for extension of time", number=20),
                _entry(21, "MOTION for extension of time", number=21),
            ]
        )
    )
    ids = sorted(e.event_id for e in _by_kind(result.events)[EventKind.motion])
    assert ids == ["evt-motion-extension-of-time", "evt-motion-extension-of-time-21"]


def test_petition_entry_classified_as_petition() -> None:
    result = extract_events(_docket([_entry(30, "PETITION for writ of certiorari", number=30)]))
    petitions = _by_kind(result.events)[EventKind.petition]
    assert any(e.event_id == "evt-petition-writ-of-certiorari" for e in petitions)


def test_recap_document_description_is_classified() -> None:
    entry = {
        "id": 40,
        "entry_number": 40,
        "date_filed": "2026-06-03",
        "description": "",
        "recap_documents": [{"short_description": "Motion to dismiss for lack of jurisdiction"}],
    }
    result = extract_events(_docket([entry]))
    motions = _by_kind(result.events)[EventKind.motion]
    assert any(e.docket_entry_id == 40 for e in motions)


def test_entry_without_id_is_skipped() -> None:
    result = extract_events(_docket([{"description": "MOTION for stay", "entry_number": 1}]))
    assert [e.event_id for e in result.events] == ["evt-appeal-disposition"]


def test_bulk_normalize_seam_yields_same_events_as_api() -> None:
    # The seed seam (`normalize=from_bulk_row`) over a bulk CSV row with no
    # entries gives the same baseline event a discovered docket would — one
    # extractor, two sources.
    bulk_row = {"id": "555", "court_id": "ca9", "case_name": "Doe v. Roe"}
    seeded = extract_events(bulk_row, normalize=from_bulk_row)
    assert [e.event_id for e in seeded.events] == ["evt-appeal-disposition"]
    assert seeded.events[0].case_id == "ca9/555"
    assert seeded.ambiguous == []


def test_bulk_normalize_seam_classifies_entries_when_present() -> None:
    # When a bulk source *does* carry docket entries, the same seam produces the
    # entry-pinned events too — the bulk row shape only changes normalization.
    bulk_row = {
        "id": "555",
        "court_id": "ca9",
        "case_name": "Doe v. Roe",
        "docket_entries": [_entry(7, "MOTION to dismiss for lack of jurisdiction", number=7)],
    }
    result = extract_events(bulk_row, normalize=from_bulk_row)
    motions = _by_kind(result.events)[EventKind.motion]
    assert any(e.docket_entry_id == 7 for e in motions)
