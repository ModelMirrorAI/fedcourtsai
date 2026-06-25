from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.ingest import (
    CorpusSource,
    default_event,
    from_api_docket,
    from_bulk_row,
    merge_rows,
    normalize_disposition,
    to_corpus_row,
    upsert_to_corpus,
)
from fedcourtsai.schemas import Disposition, EventKind

# Equivalent facts about one docket, shaped the way each upstream source delivers
# them: the API as a JSON object (court as a hyperlink, panel as nested judges),
# the bulk export as a flat CSV row (strings, pipe-delimited lists).
API_DOCKET = {
    "id": 64512345,
    "court": "https://www.courtlistener.com/api/rest/v4/courts/ca9/",
    "docket_number": "21-55555",
    "case_name": "Doe v. Roe",
    "date_filed": "2021-03-01",
    "date_terminated": "2022-06-15",
    "nature_of_suit": "Civil Rights",
    "panel": [{"name_full": "Jane Smith"}, {"name_full": "Alan Lee"}],
    "disposition": "Motion granted in part and denied in part",
    "citations": ["12 F.4th 100"],
}

BULK_ROW = {
    "id": "64512345",
    "court_id": "ca9",
    "docket_number": "21-55555",
    "case_name": "Doe v. Roe",
    "date_filed": "2021-03-01",
    "date_terminated": "2022-06-15",
    "nature_of_suit": "Civil Rights",
    "judges": "Alan Lee|Jane Smith",
    "disposition": "Motion granted in part and denied in part",
    "citations": "12 F.4th 100",
}


def test_api_and_bulk_normalize_to_same_row() -> None:
    api = from_api_docket(API_DOCKET)
    bulk = from_bulk_row(BULK_ROW)
    # The whole point of the shared core: identical apart from the source tag.
    assert api.model_dump(exclude={"source"}) == bulk.model_dump(exclude={"source"})
    assert api.source == CorpusSource.api
    assert bulk.source == CorpusSource.bulk


def test_normalized_fields() -> None:
    row = from_api_docket(API_DOCKET)
    assert row.case_id == "ca9/64512345"
    assert row.court == "ca9"
    assert row.docket_id == 64512345
    assert row.date_filed == date(2021, 3, 1)
    assert row.date_decided == date(2022, 6, 15)
    assert row.disposition == Disposition.granted_in_part
    assert row.nature_of_suit == "Civil Rights"
    assert row.judges == ["Alan Lee", "Jane Smith"]  # sorted, deduplicated
    assert row.citations == ["12 F.4th 100"]


def test_court_id_from_url_and_field_agree() -> None:
    assert from_api_docket(API_DOCKET).court == from_bulk_row(BULK_ROW).court == "ca9"


def test_missing_court_is_rejected() -> None:
    with pytest.raises(ValueError, match="court"):
        from_api_docket({"id": 1})


def test_blank_optionals_become_none() -> None:
    row = from_bulk_row({"id": "7", "court_id": "ca1", "date_filed": "", "nature_of_suit": ""})
    assert row.date_filed is None
    assert row.date_decided is None
    assert row.disposition is None
    assert row.nature_of_suit is None
    assert row.judges == []
    assert row.citations == []
    assert row.docket_number == ""


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Granted", Disposition.granted),
        ("DENIED", Disposition.denied),
        ("granted in part", Disposition.granted_in_part),
        ("Petition dismissed", Disposition.dismissed),
        ("Withdrawn by appellant", Disposition.withdrawn),
        ("affirmed", Disposition.other),
        ("", None),
        (None, None),
    ],
)
def test_normalize_disposition(raw: str | None, expected: Disposition | None) -> None:
    assert normalize_disposition(raw) == expected


def test_merge_rows_last_wins() -> None:
    stale = from_bulk_row({**BULK_ROW, "nature_of_suit": "old"})
    fresh = from_api_docket(API_DOCKET)
    merged = merge_rows([stale, fresh])
    assert len(merged) == 1
    assert merged[0].nature_of_suit == "Civil Rights"
    assert merged[0].source == CorpusSource.api


def test_to_corpus_row_projects_onto_store_schema() -> None:
    store_row = to_corpus_row(from_api_docket(API_DOCKET))
    assert isinstance(store_row, corpus.CorpusRow)
    assert store_row.case_id == "ca9/64512345"
    assert store_row.topic == "Civil Rights"  # nature_of_suit -> topic
    assert store_row.judges == ["Alan Lee", "Jane Smith"]
    assert store_row.disposition == Disposition.granted_in_part


def test_upsert_to_corpus_persists_rows(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [from_api_docket(API_DOCKET), from_bulk_row({"id": "9", "court_id": "ca1"})]
    assert upsert_to_corpus(db, rows) == 2
    with corpus.connect(db) as conn:
        assert {r.case_id for r in corpus.iter_rows(conn)} == {"ca9/64512345", "ca1/9"}


def test_default_event_for_appeal() -> None:
    event = default_event(from_api_docket(API_DOCKET))
    assert event.case_id == "ca9/64512345"
    assert event.court == "ca9"
    assert event.kind == EventKind.appeal
    assert event.event_id == "evt-appeal-disposition"
    assert event.title == "Doe v. Roe"
    assert event.opened_at == date(2021, 3, 1)
    # API_DOCKET carries a disposition, so the event is already resolved.
    assert event.resolved is True


def test_default_event_for_scotus_is_a_petition() -> None:
    event = default_event(from_bulk_row({"id": "5", "court_id": "scotus"}))
    assert event.kind == EventKind.petition
    assert event.event_id == "evt-petition-disposition"
    assert event.resolved is False  # no disposition yet
    assert event.title == "scotus/5"  # falls back to case_id when unnamed


def test_upsert_to_corpus_is_idempotent_by_case(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    upsert_to_corpus(db, [from_bulk_row({**BULK_ROW, "nature_of_suit": "old"})])
    upsert_to_corpus(db, [from_api_docket(API_DOCKET)])  # same case_id, fresher facts
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 1
        fetched = corpus.get_row(conn, "ca9/64512345")
    assert fetched is not None
    assert fetched.topic == "Civil Rights"
