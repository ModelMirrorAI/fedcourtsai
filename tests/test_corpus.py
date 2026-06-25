from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from fedcourtsai import corpus
from fedcourtsai.schemas import Disposition


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
