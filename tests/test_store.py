from datetime import date
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.schemas import Disposition, EventKind
from fedcourtsai.store import (
    cases_due_for_pull,
    iter_tracked_cases,
    open_events,
    resolved_events,
)


def _event(event_id: str, *, resolved: bool) -> corpus.CorpusEvent:
    return corpus.CorpusEvent(
        event_id=event_id,
        case_id="ca9/7",
        court="ca9",
        kind=EventKind.appeal,
        resolved=resolved,
    )


def test_iter_tracked_cases_reads_from_corpus(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        corpus.CorpusRow(case_id="ca9/2", court="ca9"),
        corpus.CorpusRow(case_id="ca1/10", court="ca1"),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    # Sorted by case_id, parsed back into (court, docket) pairs.
    assert iter_tracked_cases(db) == [("ca1", 10), ("ca9", 2)]


def test_iter_tracked_cases_missing_corpus_is_empty(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    assert iter_tracked_cases(db) == []
    assert not db.exists()  # reading must not create the corpus as a side effect


def test_cases_due_for_pull_rotates_stalest_first_and_caps(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        corpus.CorpusRow(case_id="ca9/1", court="ca9", last_pulled=date(2026, 6, 20)),
        corpus.CorpusRow(case_id="ca9/2", court="ca9", last_pulled=None),  # stalest
        corpus.CorpusRow(case_id="ca1/3", court="ca1", last_pulled=date(2026, 6, 10)),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    # Never-pulled first, then oldest stamp; capped at the per-run limit.
    assert cases_due_for_pull(db, limit=2) == [("ca9", 2), ("ca1", 3)]


def test_cases_due_for_pull_skips_closed(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    rows = [
        corpus.CorpusRow(case_id="ca9/1", court="ca9"),
        corpus.CorpusRow(case_id="ca9/2", court="ca9", disposition=Disposition.denied),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    assert cases_due_for_pull(db, limit=10) == [("ca9", 1)]


def test_cases_due_for_pull_missing_corpus_is_empty(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    assert cases_due_for_pull(db, limit=10) == []
    assert not db.exists()  # reading must not create the corpus as a side effect


def test_open_and_resolved_events_partition_corpus_events(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    with corpus.connect(db) as conn:
        corpus.upsert_events(
            conn,
            [
                _event("evt-appeal-disposition", resolved=False),
                _event("evt-motion-stay", resolved=True),
            ],
        )
    # The corpus resolved flag is the single source of truth for event state.
    assert open_events(db, "ca9", 7) == ["evt-appeal-disposition"]
    assert resolved_events(db, "ca9", 7) == ["evt-motion-stay"]


def test_event_queries_missing_corpus_is_empty(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    assert open_events(db, "ca9", 7) == []
    assert resolved_events(db, "ca9", 7) == []
    assert not db.exists()  # reading must not create the corpus as a side effect
