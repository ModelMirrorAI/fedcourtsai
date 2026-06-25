from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from fedcourtsai import corpus
from fedcourtsai.schemas import Disposition, EventKind


def _row(case_id: str = "ca9/123", **kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "ca9",
        "docket_number": "23-1234",
        "date_filed": date(2025, 1, 2),
        "date_decided": date(2026, 1, 2),
        "disposition": Disposition.granted,
        "judges": ["smith", "jones"],
        "topic": "civil rights",
        "citations": ["410 U.S. 113"],
        "opinion_text": "full text",
        "summary": "short",
    }
    base.update(kw)
    return corpus.CorpusRow.model_validate(base)


def test_db_path_under_corpus_root() -> None:
    assert corpus.corpus_db_path(Path("corpus")) == Path("corpus/corpus.db")


def test_extra_fields_forbidden() -> None:
    with pytest.raises(ValidationError):
        corpus.CorpusRow.model_validate({"case_id": "ca9/1", "court": "ca9", "surprise": "no"})


def test_roundtrip_preserves_all_fields(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    row = _row()
    with corpus.connect(db) as conn:
        assert corpus.upsert_rows(conn, [row]) == 1
        fetched = corpus.get_row(conn, "ca9/123")
    assert fetched == row


def test_connect_creates_parent_dir(tmp_path: Path) -> None:
    db = tmp_path / "nested" / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 0
    assert db.exists()


def test_upsert_is_idempotent_by_case_id(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(topic="old")])
        corpus.upsert_rows(conn, [_row(topic="new")])
        assert corpus.count(conn) == 1
        fetched = corpus.get_row(conn, "ca9/123")
        assert fetched is not None
        assert fetched.topic == "new"


def test_unresolved_row_has_null_disposition(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca1/9", disposition=None)])
        fetched = corpus.get_row(conn, "ca1/9")
    assert fetched is not None
    assert fetched.disposition is None


def test_iter_rows_filters_by_court_and_disposition(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/1", court="ca9", disposition=Disposition.granted),
        _row(case_id="ca9/2", court="ca9", disposition=Disposition.denied),
        _row(case_id="ca1/3", court="ca1", disposition=Disposition.granted),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        by_court = [r.case_id for r in corpus.iter_rows(conn, court="ca9")]
        granted = [r.case_id for r in corpus.iter_rows(conn, disposition=Disposition.granted)]
        both = [
            r.case_id for r in corpus.iter_rows(conn, court="ca9", disposition=Disposition.granted)
        ]
    assert by_court == ["ca9/1", "ca9/2"]
    assert granted == ["ca1/3", "ca9/1"]
    assert both == ["ca9/1"]


def test_get_row_missing_returns_none(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "nope/0") is None


def test_last_pulled_roundtrips(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/7", last_pulled=date(2026, 6, 20))])
        fetched = corpus.get_row(conn, "ca9/7")
    assert fetched is not None
    assert fetched.last_pulled == date(2026, 6, 20)


def test_last_pulled_defaults_to_none(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/8")])
        fetched = corpus.get_row(conn, "ca9/8")
    assert fetched is not None
    assert fetched.last_pulled is None


def test_upsert_without_stamp_preserves_prior_last_pulled(tmp_path: Path) -> None:
    # A bulk re-ingest (no stamp) must not reset a timestamp a prior pull recorded,
    # else the governor would treat a freshly-refreshed case as never-pulled.
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row(case_id="ca9/9", last_pulled=date(2026, 6, 1))])
        corpus.upsert_rows(conn, [_row(case_id="ca9/9", topic="refreshed", last_pulled=None)])
        fetched = corpus.get_row(conn, "ca9/9")
    assert fetched is not None
    assert fetched.topic == "refreshed"  # other columns still overwrite
    assert fetched.last_pulled == date(2026, 6, 1)  # but the stamp is preserved


def test_retrieve_priors_defaults_to_resolved_only(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/decided", disposition=Disposition.granted),
        _row(case_id="ca9/open", disposition=None, date_decided=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery())
    assert [r.case_id for r in priors] == ["ca9/decided"]


def test_retrieve_priors_include_open(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/decided", disposition=Disposition.granted),
        _row(case_id="ca9/open", disposition=None, date_decided=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(resolved_only=False))
    assert {r.case_id for r in priors} == {"ca9/decided", "ca9/open"}


def test_retrieve_priors_exact_filters(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/1", court="ca9", topic="civil rights", disposition=Disposition.granted),
        _row(case_id="ca9/2", court="ca9", topic="contracts", disposition=Disposition.granted),
        _row(case_id="ca1/3", court="ca1", topic="civil rights", disposition=Disposition.denied),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        by_court = corpus.retrieve_priors(conn, corpus.PriorQuery(court="ca9"))
        by_topic = corpus.retrieve_priors(conn, corpus.PriorQuery(topic="civil rights"))
        by_disp = corpus.retrieve_priors(conn, corpus.PriorQuery(disposition=Disposition.denied))
    assert {r.case_id for r in by_court} == {"ca9/1", "ca9/2"}
    assert {r.case_id for r in by_topic} == {"ca9/1", "ca1/3"}
    assert [r.case_id for r in by_disp] == ["ca1/3"]


def test_retrieve_priors_judge_overlap_required_and_ranked(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/both", judges=["smith", "jones"], date_decided=date(2025, 1, 1)),
        _row(case_id="ca9/one", judges=["smith", "lee"], date_decided=date(2025, 1, 1)),
        _row(case_id="ca9/none", judges=["doe"], date_decided=date(2025, 1, 1)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(judges=["smith", "jones"]))
    # Only cases sharing a judge survive; sharing more ranks higher.
    assert [r.case_id for r in priors] == ["ca9/both", "ca9/one"]


def test_retrieve_priors_citation_overlap_required(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/cited", citations=["410 U.S. 113"]),
        _row(case_id="ca9/other", citations=["347 U.S. 483"]),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(citations=["410 U.S. 113"]))
    assert [r.case_id for r in priors] == ["ca9/cited"]


def test_retrieve_priors_ranks_by_total_overlap(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/more", judges=["smith", "jones"], citations=["410 U.S. 113"]),
        _row(case_id="ca9/less", judges=["smith"], citations=["410 U.S. 113"]),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(
            conn, corpus.PriorQuery(judges=["smith", "jones"], citations=["410 U.S. 113"])
        )
    # Both satisfy every filter; the one sharing more judges has higher overlap.
    assert [r.case_id for r in priors] == ["ca9/more", "ca9/less"]


def test_retrieve_priors_requires_all_given_filters(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    # Shares the judge but cites a different authority — excluded, since each
    # given list filter must overlap (the filters AND together).
    rows = [
        _row(case_id="ca9/judge-only", judges=["smith"], citations=["999 U.S. 1"]),
        _row(case_id="ca9/both", judges=["smith"], citations=["410 U.S. 113"]),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(
            conn, corpus.PriorQuery(judges=["smith"], citations=["410 U.S. 113"])
        )
    assert [r.case_id for r in priors] == ["ca9/both"]


def test_retrieve_priors_ties_break_by_recency_then_case_id(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _row(case_id="ca9/old", judges=["smith"], date_decided=date(2020, 1, 1)),
        _row(case_id="ca9/new", judges=["smith"], date_decided=date(2025, 1, 1)),
        _row(case_id="ca9/undated", judges=["smith"], date_decided=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(judges=["smith"]))
    # Equal overlap: newest decision first, undated last.
    assert [r.case_id for r in priors] == ["ca9/new", "ca9/old", "ca9/undated"]


def test_retrieve_priors_respects_limit(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [_row(case_id=f"ca9/{i}", disposition=Disposition.granted) for i in range(5)]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        priors = corpus.retrieve_priors(conn, corpus.PriorQuery(), limit=2)
    assert len(priors) == 2


def test_retrieve_priors_zero_limit_is_empty(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row()])
        assert corpus.retrieve_priors(conn, corpus.PriorQuery(), limit=0) == []


def test_prior_query_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        corpus.PriorQuery.model_validate({"surprise": "no"})


def _active(case_id: str, **kw: object) -> corpus.CorpusRow:
    """An unresolved (open) corpus row, eligible for rotation."""
    return _row(case_id=case_id, disposition=None, date_decided=None, **kw)


def test_rotation_orders_never_pulled_first_then_oldest(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _active("ca9/1", last_pulled=date(2026, 6, 20)),
        _active("ca9/2", last_pulled=None),  # never pulled — stalest
        _active("ca9/3", last_pulled=date(2026, 6, 10)),  # oldest dated
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        order = [r.case_id for r in corpus.rotation_for_pull(conn, limit=10)]
    assert order == ["ca9/2", "ca9/3", "ca9/1"]


def test_rotation_respects_limit(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [_active(f"ca9/{i}", last_pulled=None) for i in range(5)]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        picked = corpus.rotation_for_pull(conn, limit=2)
    assert len(picked) == 2


def test_rotation_zero_limit_is_empty(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_active("ca9/1")])
        assert corpus.rotation_for_pull(conn, limit=0) == []


def test_rotation_skips_closed_and_resolved(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _active("ca9/open"),
        _row(case_id="ca9/resolved", disposition=Disposition.granted, date_decided=None),
        _row(case_id="ca9/closed", disposition=None, date_decided=date(2026, 1, 1)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        kept = [r.case_id for r in corpus.rotation_for_pull(conn, limit=10)]
    assert kept == ["ca9/open"]


def test_rotation_without_skip_closed_includes_all(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    rows = [
        _active("ca9/open", last_pulled=None),
        _row(case_id="ca9/resolved", disposition=Disposition.granted, last_pulled=None),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
        kept = {r.case_id for r in corpus.rotation_for_pull(conn, limit=10, skip_closed=False)}
    assert kept == {"ca9/open", "ca9/resolved"}


def _event(
    case_id: str = "ca9/123", event_id: str = "evt-appeal-disposition", **kw: object
) -> corpus.CorpusEvent:
    base: dict[str, object] = {
        "case_id": case_id,
        "event_id": event_id,
        "court": "ca9",
        "kind": EventKind.appeal,
        "title": "Doe v. Roe",
        "opened_at": date(2026, 6, 1),
    }
    base.update(kw)
    return corpus.CorpusEvent.model_validate(base)


def test_event_roundtrips(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    event = _event(description="appeal outcome", resolved=True)
    with corpus.connect(db) as conn:
        assert corpus.upsert_events(conn, [event]) == 1
        fetched = corpus.events_for_case(conn, "ca9/123")
    assert fetched == [event]


def test_event_docket_entry_id_roundtrips(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    event = _event(event_id="evt-motion-stay", kind=EventKind.motion, docket_entry_id=987)
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [event])
        fetched = corpus.events_for_case(conn, "ca9/123")
    assert fetched[0].docket_entry_id == 987


def test_event_docket_entry_id_defaults_to_none(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event()])
        fetched = corpus.events_for_case(conn, "ca9/123")
    assert fetched[0].docket_entry_id is None


def test_events_upsert_is_idempotent_by_case_and_event(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(conn, [_event(title="old")])
        corpus.upsert_events(conn, [_event(title="new")])
        fetched = corpus.events_for_case(conn, "ca9/123")
        assert corpus.event_count(conn) == 1
    assert fetched[0].title == "new"


def test_multiple_events_per_case(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [_event(event_id="evt-appeal-disposition"), _event(event_id="evt-motion-stay")],
        )
        ids = [e.event_id for e in corpus.events_for_case(conn, "ca9/123")]
    assert ids == ["evt-appeal-disposition", "evt-motion-stay"]


def test_events_for_missing_case_is_empty(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.events_for_case(conn, "nope/0") == []


def test_watermark_set_and_get(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") is None
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 10))
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 10)


def test_watermark_only_moves_forward(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 10))
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 1))  # older — ignored
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 10)
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 20))  # newer — applied
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 20)


def test_watermark_is_per_court(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.set_discovery_watermark(conn, "ca9", date(2026, 6, 10))
        corpus.set_discovery_watermark(conn, "ca1", date(2026, 5, 1))
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 10)
        assert corpus.get_discovery_watermark(conn, "ca1") == date(2026, 5, 1)
