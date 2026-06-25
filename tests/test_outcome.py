from datetime import date
from pathlib import Path

from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.ingest import from_api_docket
from fedcourtsai.pipeline.outcome import (
    appears_decided,
    detect_resolution,
    granted_flag,
    is_machine_readable,
    record_outcomes,
    resolve_case,
)
from fedcourtsai.schemas import Disposition, EventKind, Outcome, PredictableEvent
from fedcourtsai.serialize import read_model, write_yaml

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


def _open_event(tmp_path: Path, event_id: str = "evt-petition-review") -> None:
    """Write an open event.yaml for the canned docket's case."""
    event = PredictableEvent(
        event_id=event_id,
        case_id="ca9/64512345",
        kind=EventKind.petition,
        title="Petition for review",
    )
    path = CasePaths(tmp_path, "ca9", 64512345).event(event_id).event_file
    write_yaml(path, event)


# --- pure helpers --------------------------------------------------------------


def test_granted_flag_maps_partial_grant_to_granted() -> None:
    assert granted_flag(Disposition.granted) == 1
    assert granted_flag(Disposition.granted_in_part) == 1
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


# --- detection -----------------------------------------------------------------


def test_single_open_event_resolves_deterministically() -> None:
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert not resolution.reconciles
    outcome = resolution.outcomes["evt-petition-review"]
    assert outcome.actual_disposition == Disposition.denied
    assert outcome.actual_granted == 0
    assert outcome.resolved_at == date(2022, 6, 15)
    assert outcome.source == "12 F.4th 100"


def test_undecided_docket_is_a_noop() -> None:
    row = from_api_docket({"id": 7, "court_id": "ca9", "date_filed": "2024-01-01"})
    resolution = detect_resolution(row, "ca9", 7, ["evt-petition-review"])
    assert not resolution.outcomes
    assert not resolution.reconciles


def test_no_open_events_is_a_noop() -> None:
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, [])
    assert not resolution.outcomes
    assert not resolution.reconciles


def test_unreadable_disposition_routes_to_reconcile() -> None:
    # "affirmed" normalizes to the `other` catch-all — decided, but not how.
    row = from_api_docket({**DECIDED_DOCKET, "disposition": "affirmed"})
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert not resolution.outcomes
    (req,) = resolution.reconciles
    assert req.event_id == "evt-petition-review"
    assert "not machine-readable" in req.reason


def test_decided_without_date_routes_to_reconcile() -> None:
    row = from_api_docket({"id": 64512345, "court_id": "ca9", "disposition": "Petition denied"})
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    assert not resolution.outcomes
    (req,) = resolution.reconciles
    assert "no decision date" in req.reason


def test_multiple_open_events_route_to_reconcile() -> None:
    # One case-level disposition cannot be attributed across several open events.
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-motion-a", "evt-motion-b"])
    assert not resolution.outcomes
    assert {r.event_id for r in resolution.reconciles} == {"evt-motion-a", "evt-motion-b"}
    assert all("cannot be attributed" in r.reason for r in resolution.reconciles)


# --- ledger write --------------------------------------------------------------


def test_record_outcomes_writes_outcome_and_marks_resolved(tmp_path: Path) -> None:
    _open_event(tmp_path)
    row = from_api_docket(DECIDED_DOCKET)
    resolution = detect_resolution(row, "ca9", 64512345, ["evt-petition-review"])
    written = record_outcomes(tmp_path, "ca9", 64512345, resolution)
    assert written == ["evt-petition-review"]

    event_paths = CasePaths(tmp_path, "ca9", 64512345).event("evt-petition-review")
    written_outcome = read_model(event_paths.outcome, Outcome)
    assert written_outcome.actual_disposition == Disposition.denied
    # The event record is flipped resolved so it stays consistent with its outcome.
    assert read_model(event_paths.event_file, PredictableEvent).resolved is True


def test_resolve_case_end_to_end(tmp_path: Path) -> None:
    _open_event(tmp_path)
    row = from_api_docket(DECIDED_DOCKET)
    resolution = resolve_case(tmp_path, row, "ca9", 64512345)
    assert "evt-petition-review" in resolution.outcomes
    assert CasePaths(tmp_path, "ca9", 64512345).event("evt-petition-review").outcome.exists()


def test_resolve_case_is_idempotent(tmp_path: Path) -> None:
    # A second refresh sees the event closed (outcome.json exists) and does nothing.
    _open_event(tmp_path)
    row = from_api_docket(DECIDED_DOCKET)
    resolve_case(tmp_path, row, "ca9", 64512345)
    again = resolve_case(tmp_path, row, "ca9", 64512345)
    assert not again.outcomes
    assert not again.reconciles
