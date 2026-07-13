"""The corpus file's ranged-read contract (``fedcourtsai.corpus``).

Ranged remote reads — read-only SQLite over HTTP range requests against the
immutable corpus blob — are governed by two properties this suite pins down:
the file's physical layout (64 KB pages, non-WAL at rest) and every agent /
provisioning read path resolving through an index rather than a table scan.
"""

from __future__ import annotations

import re
import sqlite3
from collections.abc import Callable
from datetime import date
from functools import partial
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.fixture import build_fixture_corpus
from fedcourtsai.schemas import Disposition, EventKind

# --- physical layout ------------------------------------------------------------


def _legacy_db(db_path: Path, *, page_size: int = 4096, wal: bool = False) -> None:
    """A populated database with a pre-contract physical layout."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(f"PRAGMA page_size = {page_size}")
        if wal:
            conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("CREATE TABLE t (k TEXT PRIMARY KEY, v TEXT)")
        conn.execute("INSERT INTO t VALUES ('a', 'b')")
        conn.commit()
    finally:
        conn.close()


def test_connect_creates_ranged_layout(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        assert conn.execute("PRAGMA page_size").fetchone()[0] == corpus.RANGED_PAGE_SIZE
    assert corpus.check_ranged_layout(db) == []


def test_check_ranged_layout_graceful_before_pull(tmp_path: Path) -> None:
    # Absent and empty files are the pre-pull states, not problems.
    assert corpus.check_ranged_layout(tmp_path / "corpus.db") == []
    empty = tmp_path / "empty.db"
    empty.touch()
    assert corpus.check_ranged_layout(empty) == []


def test_check_ranged_layout_flags_small_pages(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _legacy_db(db, page_size=4096)
    problems = corpus.check_ranged_layout(db)
    assert len(problems) == 1
    assert "page size 4096" in problems[0]


def test_check_ranged_layout_flags_wal(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _legacy_db(db, page_size=corpus.RANGED_PAGE_SIZE, wal=True)
    problems = corpus.check_ranged_layout(db)
    assert len(problems) == 1
    assert "WAL" in problems[0]


def test_ensure_ranged_layout_migrates_and_preserves(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _legacy_db(db, page_size=4096, wal=True)
    assert corpus.ensure_ranged_layout(db) is True
    assert corpus.check_ranged_layout(db) == []
    conn = sqlite3.connect(db)
    try:
        assert conn.execute("SELECT v FROM t WHERE k = 'a'").fetchone()[0] == "b"
    finally:
        conn.close()
    # Already in shape: the second call is a header-read no-op.
    assert corpus.ensure_ranged_layout(db) is False


def test_ensure_ranged_layout_no_file_is_noop(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    assert corpus.ensure_ranged_layout(db) is False
    assert not db.exists()


def test_fixture_corpus_has_ranged_layout(tmp_path: Path) -> None:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    assert corpus.check_ranged_layout(db) == []


# --- index-served read paths ----------------------------------------------------

# A full table scan plans as exactly "SCAN <table>"; an index-served walk says
# "... USING [COVERING] INDEX ...". Only the former is a regression.
_FULL_SCAN = re.compile(r"SCAN (cases|events|snapshots)\b(?! USING)")


def _select_plans(conn: sqlite3.Connection, read: Callable[[], object]) -> list[tuple[str, str]]:
    """``(statement, plan)`` for each SELECT the callable executes.

    The statements are captured via the trace hook and re-planned with
    ``EXPLAIN QUERY PLAN``, so the audit covers the exact SQL the read path
    runs — a query change cannot silently drift away from the test.
    """
    statements: list[str] = []
    conn.set_trace_callback(statements.append)
    try:
        read()
    finally:
        conn.set_trace_callback(None)
    plans: list[tuple[str, str]] = []
    for stmt in statements:
        if not stmt.lstrip().upper().startswith("SELECT"):
            continue
        params = ("x",) * stmt.count("?")
        detail = " | ".join(
            str(record["detail"]) for record in conn.execute(f"EXPLAIN QUERY PLAN {stmt}", params)
        )
        plans.append((stmt, detail))
    return plans


def _assert_index_served(plans: list[tuple[str, str]], *, expect: str | None = None) -> None:
    assert plans, "expected the read path to execute at least one SELECT"
    for stmt, detail in plans:
        assert not _FULL_SCAN.search(detail), f"full table scan: {stmt} => {detail}"
        if expect is not None:
            assert expect in detail, f"expected {expect}: {stmt} => {detail}"


def _row(case_id: str, **kw: object) -> corpus.CorpusRow:
    base: dict[str, object] = {
        "case_id": case_id,
        "court": "ca9",
        "docket_number": "23-1234",
        "disposition": Disposition.granted,
        "topic": "civil rights",
    }
    base.update(kw)
    return corpus.CorpusRow.model_validate(base)


def _event(case_id: str, **kw: object) -> corpus.CorpusEvent:
    base: dict[str, object] = {
        "case_id": case_id,
        "event_id": "evt-appeal-disposition",
        "court": "ca9",
        "kind": EventKind.appeal,
        "title": "Doe v. Roe",
    }
    base.update(kw)
    return corpus.CorpusEvent.model_validate(base)


def _populated(db_path: Path) -> None:
    rows = [_row(f"ca9/{i}") for i in range(20)]
    events = [_event(f"ca9/{i}", resolved=i % 3 == 0) for i in range(20)]
    with corpus.connect(db_path) as conn:
        corpus.upsert_rows(conn, rows)
        corpus.upsert_events(conn, events)
        for i in range(20):
            corpus.upsert_snapshot(conn, f"ca9/{i}", date(2026, 6, 1), {"n": i})
            corpus.upsert_snapshot(conn, f"ca9/{i}", date(2026, 6, 2), {"n": i})


def test_get_row_is_index_served(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _populated(db)
    with corpus.connect(db) as conn:
        plans = _select_plans(conn, lambda: corpus.get_row(conn, "ca9/1"))
    _assert_index_served(plans)


def test_retrieve_priors_filters_are_index_served(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _populated(db)
    queries = {
        "idx_cases_court": corpus.PriorQuery(court="ca9"),
        "idx_cases_topic": corpus.PriorQuery(topic="civil rights", resolved_only=False),
        "idx_cases_disposition": corpus.PriorQuery(disposition=Disposition.granted),
    }
    with corpus.connect(db) as conn:
        for index_name, query in queries.items():
            plans = _select_plans(conn, partial(corpus.retrieve_priors, conn, query))
            _assert_index_served(plans, expect=index_name)


def test_events_for_case_is_index_served(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _populated(db)
    with corpus.connect(db) as conn:
        plans = _select_plans(conn, lambda: corpus.events_for_case(conn, "ca9/1"))
    _assert_index_served(plans)


def _open_events_list(conn: sqlite3.Connection, court: str | None) -> list[corpus.CorpusEvent]:
    return list(corpus.iter_open_events(conn, court=court))


def test_open_events_census_uses_partial_index(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _populated(db)
    with corpus.connect(db) as conn:
        for court in (None, "ca9"):
            plans = _select_plans(conn, partial(_open_events_list, conn, court))
            _assert_index_served(plans, expect="idx_events_open")


def test_latest_snapshot_is_index_served(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _populated(db)
    with corpus.connect(db) as conn:
        assert corpus.latest_snapshot(conn, "ca9/1") is not None
        plans = _select_plans(conn, lambda: corpus.latest_snapshot(conn, "ca9/1"))
    _assert_index_served(plans)
