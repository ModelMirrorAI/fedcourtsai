"""The unified raw-fact corpus.

All *raw facts* — dockets, dated snapshots, judges, case metadata and tracking
state, and event definitions — live in one packed, queryable store, written
**identically** by ``seed`` (CourtListener bulk data) and ``pull`` (the REST
API) through this one ingestion seam. The packed store is a single **SQLite**
database (``corpus/corpus.db``) versioned with DVC: the data blob lives in the
DVC remote and only the small ``*.dvc`` pointer is committed to git.

SQLite was chosen over Parquet shards because the corpus is a single artifact
(one DVC pointer, not a sharded tree), it is queryable with plain SQL for
retrieval (filter by court / judges / topic / citation), and it needs no extra
runtime dependency. The *format* is internal; the stable contract the ledger
relies on is this row schema — its identifiers and ``Disposition`` vocabulary,
shared with :mod:`fedcourtsai.schemas`.

Each row is a normalized, **labeled** record: it carries the realized
``disposition`` so the corpus doubles as a back-testing set (replay a predictor
against resolved events, score against the known label) and a retrieval source
(pull a handful of relevant priors at prediction time).
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .schemas import Disposition

CORPUS_DB_FILENAME = "corpus.db"


def corpus_db_path(corpus_root: Path) -> Path:
    """Location of the packed corpus database within ``corpus_root``."""
    return corpus_root / CORPUS_DB_FILENAME


class CorpusRow(BaseModel):
    """One normalized, labeled raw-fact record in the corpus.

    Written identically whether a row originates from a bulk CSV (seed) or a
    REST docket (pull); the ingestion core maps both sources onto this shape.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    case_id: str = Field(description="Canonical `<court_id>/<docket_id>` id; primary key.")
    court: str
    docket_number: str = ""
    date_filed: date | None = None
    date_decided: date | None = None
    disposition: Disposition | None = Field(
        default=None, description="Realized outcome label; None while unresolved."
    )
    judges: list[str] = Field(default_factory=list)
    topic: str | None = Field(default=None, description="Nature of suit / subject-matter topic.")
    citations: list[str] = Field(default_factory=list)
    opinion_text: str | None = None
    summary: str | None = None
    # embedding[] — a later upgrade for semantic retrieval; not stored yet.


_SCHEMA = """
CREATE TABLE IF NOT EXISTS cases (
    case_id       TEXT PRIMARY KEY,
    court         TEXT NOT NULL,
    docket_number TEXT NOT NULL DEFAULT '',
    date_filed    TEXT,
    date_decided  TEXT,
    disposition   TEXT,
    judges        TEXT NOT NULL DEFAULT '[]',
    topic         TEXT,
    citations     TEXT NOT NULL DEFAULT '[]',
    opinion_text  TEXT,
    summary       TEXT
);
CREATE INDEX IF NOT EXISTS idx_cases_court ON cases(court);
CREATE INDEX IF NOT EXISTS idx_cases_disposition ON cases(disposition);
"""

_COLUMNS = (
    "case_id",
    "court",
    "docket_number",
    "date_filed",
    "date_decided",
    "disposition",
    "judges",
    "topic",
    "citations",
    "opinion_text",
    "summary",
)


@contextmanager
def connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Open the corpus database (creating its schema), yielding a connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(_SCHEMA)
        yield conn
    finally:
        conn.close()


def _to_record(row: CorpusRow) -> dict[str, object]:
    return {
        "case_id": row.case_id,
        "court": row.court,
        "docket_number": row.docket_number,
        "date_filed": row.date_filed.isoformat() if row.date_filed else None,
        "date_decided": row.date_decided.isoformat() if row.date_decided else None,
        "disposition": row.disposition,
        "judges": json.dumps(row.judges, sort_keys=True),
        "topic": row.topic,
        "citations": json.dumps(row.citations, sort_keys=True),
        "opinion_text": row.opinion_text,
        "summary": row.summary,
    }


def _from_record(record: sqlite3.Row) -> CorpusRow:
    return CorpusRow(
        case_id=record["case_id"],
        court=record["court"],
        docket_number=record["docket_number"],
        date_filed=date.fromisoformat(record["date_filed"]) if record["date_filed"] else None,
        date_decided=(
            date.fromisoformat(record["date_decided"]) if record["date_decided"] else None
        ),
        disposition=record["disposition"],
        judges=json.loads(record["judges"]),
        topic=record["topic"],
        citations=json.loads(record["citations"]),
        opinion_text=record["opinion_text"],
        summary=record["summary"],
    )


def upsert_rows(conn: sqlite3.Connection, rows: list[CorpusRow]) -> int:
    """Insert or replace rows by ``case_id``; returns the number written.

    Idempotent: re-ingesting the same case overwrites its row, so ``seed`` and
    ``pull`` can both write a case without producing duplicates.
    """
    placeholders = ", ".join("?" for _ in _COLUMNS)
    updates = ", ".join(f"{c}=excluded.{c}" for c in _COLUMNS if c != "case_id")
    sql = (
        f"INSERT INTO cases ({', '.join(_COLUMNS)}) VALUES ({placeholders}) "
        f"ON CONFLICT(case_id) DO UPDATE SET {updates}"
    )
    with conn:
        conn.executemany(sql, [tuple(_to_record(r)[c] for c in _COLUMNS) for r in rows])
    return len(rows)


def get_row(conn: sqlite3.Connection, case_id: str) -> CorpusRow | None:
    """Fetch a single case row, or ``None`` if it is not in the corpus."""
    cur = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    record = cur.fetchone()
    return _from_record(record) if record is not None else None


def count(conn: sqlite3.Connection) -> int:
    """Number of rows currently in the corpus."""
    cur = conn.execute("SELECT COUNT(*) AS n FROM cases")
    return int(cur.fetchone()["n"])


def iter_rows(
    conn: sqlite3.Connection,
    *,
    court: str | None = None,
    disposition: Disposition | None = None,
) -> Iterator[CorpusRow]:
    """Yield rows in ``case_id`` order, optionally filtered by court / disposition.

    The filters cover the common retrieval and back-test selections; richer
    querying (by judge, topic, citation, or semantic similarity) is layered on
    top of this same store.
    """
    clauses: list[str] = []
    params: list[object] = []
    if court is not None:
        clauses.append("court = ?")
        params.append(court)
    if disposition is not None:
        clauses.append("disposition = ?")
        params.append(Disposition(disposition).value)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    cur = conn.execute(f"SELECT * FROM cases{where} ORDER BY case_id", params)
    for record in cur:
        yield _from_record(record)
