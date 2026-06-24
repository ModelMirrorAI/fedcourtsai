"""Unit tests for the shared ingestion core.

The contract under test: an API docket JSON and a bulk CSV row carrying the same
facts normalize to the same :class:`NormalizedDocket`, and that intermediate
projects cleanly to both the active tier (``TrackedCase`` / ``docket.json``) and
the historical tier (``CorpusRow``).
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml

from fedcourtsai.pipeline.ingest import (
    NormalizedDocket,
    parse_disposition,
    select_untracked,
    write_active_case,
)
from fedcourtsai.schemas import CaseStatus, Disposition, TrackedCase

API_DOCKET = {
    "id": 64512345,
    "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
    "docket_number": "23-12345",
    "case_name": "Doe v. Roe",
    "date_filed": "2026-01-15",
    "date_terminated": "2026-05-20",
    "assigned_to_str": "Jane Smith",
    "referred_to_str": "John Doe",
    "nature_of_suit": "Civil Rights",
    "absolute_url": "/docket/64512345/doe-v-roe/",
    "disposition": "Motion Granted in Part",
    "docket_entries": [{"entry_number": 1, "description": "Complaint filed"}],
}

# Same facts, as a flat bulk-data CSV row.
BULK_ROW = {
    "id": "64512345",
    "court_id": "ca9",
    "docket_number": "23-12345",
    "case_name": "Doe v. Roe",
    "date_filed": "2026-01-15",
    "date_terminated": "2026-05-20",
    "assigned_to_str": "Jane Smith; John Doe",
    "nature_of_suit": "Civil Rights",
    "absolute_url": "/docket/64512345/doe-v-roe/",
    "disposition": "granted in part",
    "citations": "5 F.4th 100 | 6 F.4th 200",
}


def test_api_and_bulk_agree_on_core_fields() -> None:
    api = NormalizedDocket.from_api_docket(API_DOCKET)
    bulk = NormalizedDocket.from_bulk_row(BULK_ROW)

    for field_name in (
        "court_id",
        "docket_id",
        "docket_number",
        "case_name",
        "date_filed",
        "date_decided",
        "disposition",
        "judges",
        "nature_of_suit",
        "source_url",
    ):
        assert getattr(api, field_name) == getattr(bulk, field_name), field_name

    assert api.court_id == "ca9"
    assert api.docket_id == 64512345
    assert api.case_id == "ca9/64512345"
    assert api.disposition is Disposition.granted_in_part
    assert api.judges == ("Jane Smith", "John Doe")
    assert api.date_decided == date(2026, 5, 20)


def test_api_preserves_entries_bulk_has_none() -> None:
    api = NormalizedDocket.from_api_docket(API_DOCKET)
    bulk = NormalizedDocket.from_bulk_row(BULK_ROW)
    assert api.entries and api.entries[0]["entry_number"] == 1
    assert bulk.entries == ()
    # Bulk surfaces citations the API docket lacks.
    assert bulk.citations == ("5 F.4th 100", "6 F.4th 200")


def test_court_id_and_docket_id_overrides() -> None:
    payload = {k: v for k, v in API_DOCKET.items() if k not in {"court", "court_id"}}
    nd = NormalizedDocket.from_api_docket(payload, court_id="scotus", docket_id=999)
    assert nd.court_id == "scotus"
    assert nd.docket_id == 999


def test_api_docket_missing_ids_raise() -> None:
    with pytest.raises(ValueError):
        NormalizedDocket.from_api_docket({"id": 1})  # no court
    with pytest.raises(ValueError):
        NormalizedDocket.from_api_docket({"court": ".../courts/ca9/"})  # no id


def test_bulk_row_missing_ids_raise() -> None:
    with pytest.raises(ValueError):
        NormalizedDocket.from_bulk_row({"court_id": "ca9"})


def test_sparse_bulk_row_degrades_to_defaults() -> None:
    nd = NormalizedDocket.from_bulk_row({"id": "7", "court_id": "ca1", "date_filed": ""})
    assert nd.docket_number == ""
    assert nd.case_name == ""
    assert nd.date_filed is None
    assert nd.disposition is None
    assert nd.judges == ()
    # Still a valid, labelable corpus row.
    row = nd.to_corpus_row()
    assert row.case_id == "ca1/7"
    assert row.disposition is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Motion Granted", Disposition.granted),
        ("GRANTED IN PART", Disposition.granted_in_part),
        ("denied", Disposition.denied),
        ("Case Dismissed", Disposition.dismissed),
        ("Withdrawn by movant", Disposition.withdrawn),
        ("affirmed", Disposition.other),
        ("", None),
        (None, None),
    ],
)
def test_parse_disposition(text: object, expected: Disposition | None) -> None:
    assert parse_disposition(text) == expected


def test_to_corpus_row_carries_label_and_columns() -> None:
    row = NormalizedDocket.from_bulk_row(BULK_ROW).to_corpus_row()
    assert row.court_id == "ca9"
    # `_Strict` models serialize enums to their value (use_enum_values=True).
    assert row.disposition == Disposition.granted_in_part
    assert row.citations == ["5 F.4th 100", "6 F.4th 200"]
    assert row.date_decided == date(2026, 5, 20)
    # Round-trips through its own schema.
    assert row.model_validate(row.model_dump()) == row


def test_to_tracked_case_projection() -> None:
    nd = NormalizedDocket.from_api_docket(API_DOCKET)
    case = nd.to_tracked_case(
        tracked_since=date(2026, 6, 24),
        last_pulled=datetime(2026, 6, 24, tzinfo=UTC),
    )
    assert isinstance(case, TrackedCase)
    assert case.case_id == "ca9/64512345"
    assert case.courtlistener_url == "/docket/64512345/doe-v-roe/"
    assert case.status == CaseStatus.active
    assert case.tracked_since == date(2026, 6, 24)


def test_to_record_identical_across_sources() -> None:
    api_record = NormalizedDocket.from_api_docket(API_DOCKET).to_record()
    bulk_record = NormalizedDocket.from_bulk_row(BULK_ROW).to_record()
    # The shared normalized columns match; only source-specific extras differ.
    shared = set(api_record) & set(bulk_record) - {"citations"}
    for key in shared:
        assert api_record[key] == bulk_record[key], key
    assert "docket_entries" in api_record
    assert "docket_entries" not in bulk_record


def test_write_active_case_materializes_artifacts(tmp_path: Path) -> None:
    nd = NormalizedDocket.from_api_docket(API_DOCKET)
    case = write_active_case(
        tmp_path,
        nd,
        tracked_since=date(2026, 6, 24),
        last_pulled=datetime(2026, 6, 24, tzinfo=UTC),
        snapshot_date=date(2026, 6, 24),
    )
    base = tmp_path / "cases" / "ca9" / "64512345"
    case_yaml = base / "case.yaml"
    docket_json = base / "record" / "docket.json"
    snapshot = base / "record" / "snapshots" / "2026-06-24.json"

    assert case_yaml.exists() and docket_json.exists() and snapshot.exists()
    # Newline-terminated, deterministic writes (serialize contract).
    assert docket_json.read_text().endswith("\n")
    assert json.loads(docket_json.read_text()) == json.loads(snapshot.read_text())

    persisted = TrackedCase.model_validate(yaml.safe_load(case_yaml.read_text()))
    assert persisted == case
    assert persisted.case_id == "ca9/64512345"


def test_select_untracked_skips_known_cases(tmp_path: Path) -> None:
    existing = NormalizedDocket.from_api_docket(API_DOCKET)
    write_active_case(tmp_path, existing, snapshot_date=date(2026, 6, 24))

    fresh = NormalizedDocket.from_bulk_row({"id": "111", "court_id": "ca1"})
    again = NormalizedDocket.from_bulk_row(BULK_ROW)  # same id as `existing`

    untracked = select_untracked(tmp_path, [existing, fresh, again])
    assert [d.docket_id for d in untracked] == [111]
