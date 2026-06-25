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

from .schemas import Disposition, EventKind

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
    last_pulled: date | None = Field(
        default=None,
        description="Tracking state: date `pull` last refreshed this case via REST; "
        "None until first pulled. Drives the budget governor's rotation.",
    )
    # embedding[] — a later upgrade for semantic retrieval; not stored yet.


class CorpusEvent(BaseModel):
    """A predictable event defined as a raw fact in the corpus.

    The corpus analogue of the git-ledger :class:`fedcourtsai.schemas.PredictableEvent`:
    when ``pull`` discovers a newly-filed docket it records the thing(s) the
    pipeline should predict about it — e.g. the disposition of the appeal — as
    corpus rows rather than per-case ``event.yaml`` files. Keyed by
    ``(case_id, event_id)`` so a case can carry more than one predictable event.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    event_id: str = Field(description="Stable `evt-<kind>-<slug>` id; unique within a case.")
    case_id: str
    court: str
    kind: EventKind
    title: str = ""
    description: str | None = None
    docket_entry_id: int | None = Field(
        default=None,
        description="CourtListener id of the docket entry this event is pinned to, "
        "when derived from a specific filing; None for case-level events.",
    )
    decision_target: str = "disposition"
    opened_at: date | None = Field(default=None, description="When the event became predictable.")
    resolved: bool = False


class DiscoveryWatermark(BaseModel):
    """Per-court forward-discovery cursor: the newest ``date_filed`` seen so far.

    Tracking state (not a docket fact), mirroring seed's bulk cursor: ``pull``
    discovers dockets filed on or after this date, then advances it, so each run
    resumes where the last left off without rescanning the whole court.
    """

    model_config = ConfigDict(extra="forbid")

    court: str
    last_filed: date


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
    summary       TEXT,
    last_pulled   TEXT
);
CREATE INDEX IF NOT EXISTS idx_cases_court ON cases(court);
CREATE INDEX IF NOT EXISTS idx_cases_disposition ON cases(disposition);
-- The governor rotates oldest-last_pulled-first over the unresolved set.
CREATE INDEX IF NOT EXISTS idx_cases_last_pulled ON cases(last_pulled);

-- Predictable event definitions: raw facts, one or more per case.
CREATE TABLE IF NOT EXISTS events (
    case_id         TEXT NOT NULL,
    event_id        TEXT NOT NULL,
    court           TEXT NOT NULL,
    kind            TEXT NOT NULL,
    title           TEXT NOT NULL DEFAULT '',
    description     TEXT,
    docket_entry_id INTEGER,
    decision_target TEXT NOT NULL DEFAULT 'disposition',
    opened_at       TEXT,
    resolved        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (case_id, event_id)
);
CREATE INDEX IF NOT EXISTS idx_events_case ON events(case_id);

-- Per-court forward-discovery watermark (the date_filed cursor for `pull`).
CREATE TABLE IF NOT EXISTS discovery_watermarks (
    court       TEXT PRIMARY KEY,
    last_filed  TEXT NOT NULL
);
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
    "last_pulled",
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
        "last_pulled": row.last_pulled.isoformat() if row.last_pulled else None,
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
        last_pulled=(date.fromisoformat(record["last_pulled"]) if record["last_pulled"] else None),
    )


def upsert_rows(conn: sqlite3.Connection, rows: list[CorpusRow]) -> int:
    """Insert or replace rows by ``case_id``; returns the number written.

    Idempotent: re-ingesting the same case overwrites its row, so ``seed`` and
    ``pull`` can both write a case without producing duplicates.
    """
    placeholders = ", ".join("?" for _ in _COLUMNS)
    # `last_pulled` only ever advances: a write that does not carry a fresh stamp
    # (e.g. a bulk seed re-ingest) must keep the timestamp a prior pull recorded,
    # so the governor does not see a refreshed case as never-pulled.
    updates = ", ".join(
        (f"{c}=COALESCE(excluded.{c}, cases.{c})" if c == "last_pulled" else f"{c}=excluded.{c}")
        for c in _COLUMNS
        if c != "case_id"
    )
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


DEFAULT_PRIOR_LIMIT = 20


class PriorQuery(BaseModel):
    """Structured filter for retrieving a handful of relevant priors.

    At prediction time a model wants a few *similar resolved* cases — precedent —
    not the bulk set in context. Each field narrows the candidate set: ``court``,
    ``topic`` and ``disposition`` are exact-match filters; ``judges`` and
    ``citations`` match on **overlap** (a row qualifies if it shares at least one
    value). Results come back ranked by relevance — total overlap across the
    multi-valued filters — so the closest priors lead. Semantic / embedding
    similarity is a later upgrade layered on this same seam.

    ``resolved_only`` defaults to ``True`` because a prior is only useful as
    precedent once its outcome is known; flip it off to retrieve open cases too.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    court: str | None = None
    topic: str | None = Field(default=None, description="Exact nature-of-suit / subject topic.")
    judges: list[str] = Field(
        default_factory=list, description="Match cases sharing any of these judges."
    )
    citations: list[str] = Field(
        default_factory=list, description="Match cases citing any of these authorities."
    )
    disposition: Disposition | None = Field(
        default=None, description="Restrict to one realized outcome label."
    )
    resolved_only: bool = Field(
        default=True, description="Keep only labeled (decided) cases — precedent."
    )


def _recency_key(row: CorpusRow) -> tuple[int, int]:
    """Sort key putting decided cases first, newest decision first.

    Undated rows sort after dated ones; among dated rows the negated ordinal
    makes the most recent decision compare smallest (so it leads in an ascending
    sort).
    """
    if row.date_decided is not None:
        return (0, -row.date_decided.toordinal())
    return (1, 0)


def retrieve_priors(
    conn: sqlite3.Connection,
    query: PriorQuery,
    *,
    limit: int = DEFAULT_PRIOR_LIMIT,
) -> list[CorpusRow]:
    """Return up to ``limit`` priors matching ``query``, most relevant first.

    The exact-match filters (``court`` / ``topic`` / ``disposition`` and the
    ``resolved_only`` toggle) are pushed into SQL so only a narrowed candidate
    set is scanned; the overlap filters (``judges`` / ``citations``, stored as
    JSON arrays) are applied in Python, where each match also contributes to the
    relevance score. Ranking is relevance descending, then most-recent decision,
    then ``case_id`` so the result is deterministic.
    """
    if limit <= 0:
        return []
    clauses: list[str] = []
    params: list[object] = []
    if query.court is not None:
        clauses.append("court = ?")
        params.append(query.court)
    if query.topic is not None:
        clauses.append("topic = ?")
        params.append(query.topic)
    if query.disposition is not None:
        clauses.append("disposition = ?")
        params.append(Disposition(query.disposition).value)
    if query.resolved_only:
        clauses.append("disposition IS NOT NULL")
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""

    want_judges = set(query.judges)
    want_citations = set(query.citations)
    scored: list[tuple[int, tuple[int, int], str, CorpusRow]] = []
    for record in conn.execute(f"SELECT * FROM cases{where}", params):
        row = _from_record(record)
        judge_overlap = want_judges & set(row.judges)
        citation_overlap = want_citations & set(row.citations)
        # Overlap filters are required when given: skip a row that shares none.
        if want_judges and not judge_overlap:
            continue
        if want_citations and not citation_overlap:
            continue
        score = len(judge_overlap) + len(citation_overlap)
        scored.append((-score, _recency_key(row), row.case_id, row))
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    return [row for *_, row in scored[:limit]]


def rotation_for_pull(
    conn: sqlite3.Connection,
    *,
    limit: int,
    skip_closed: bool = True,
) -> list[CorpusRow]:
    """The next ``limit`` cases ``pull`` should refresh, stalest first.

    The CourtListener REST budget caps a run at a handful of dockets, so the
    governor refreshes the **oldest-``last_pulled``-first** slice of the active
    set and lets a large active set rotate over several days. Never-pulled cases
    (``last_pulled IS NULL``) are the stalest and sort ahead of any dated stamp;
    ``case_id`` breaks ties so the order is deterministic.

    With ``skip_closed`` (the default) a case that is **closed or resolved** —
    one carrying a realized ``disposition`` or a ``date_decided`` — is excluded,
    so no budget is spent re-fetching a docket whose outcome is already known.
    """
    if limit <= 0:
        return []
    where = " WHERE disposition IS NULL AND date_decided IS NULL" if skip_closed else ""
    cur = conn.execute(
        f"SELECT * FROM cases{where} "
        "ORDER BY last_pulled IS NOT NULL, last_pulled ASC, case_id ASC "
        "LIMIT ?",
        (limit,),
    )
    return [_from_record(record) for record in cur]


# --- predictable event definitions (raw facts) ---------------------------------

_EVENT_COLUMNS = (
    "case_id",
    "event_id",
    "court",
    "kind",
    "title",
    "description",
    "docket_entry_id",
    "decision_target",
    "opened_at",
    "resolved",
)


def _event_to_record(event: CorpusEvent) -> dict[str, object]:
    return {
        "case_id": event.case_id,
        "event_id": event.event_id,
        "court": event.court,
        "kind": event.kind,
        "title": event.title,
        "description": event.description,
        "docket_entry_id": event.docket_entry_id,
        "decision_target": event.decision_target,
        "opened_at": event.opened_at.isoformat() if event.opened_at else None,
        "resolved": int(event.resolved),
    }


def _event_from_record(record: sqlite3.Row) -> CorpusEvent:
    return CorpusEvent(
        case_id=record["case_id"],
        event_id=record["event_id"],
        court=record["court"],
        kind=record["kind"],
        title=record["title"],
        description=record["description"],
        docket_entry_id=record["docket_entry_id"],
        decision_target=record["decision_target"],
        opened_at=date.fromisoformat(record["opened_at"]) if record["opened_at"] else None,
        resolved=bool(record["resolved"]),
    )


def upsert_events(conn: sqlite3.Connection, events: list[CorpusEvent]) -> int:
    """Insert or replace predictable-event definitions by ``(case_id, event_id)``.

    Idempotent, so re-discovering a docket overwrites its event rows rather than
    duplicating them — like the ``cases`` upsert, this keeps ``seed`` and ``pull``
    able to rewrite the same fact without proliferating rows.
    """
    placeholders = ", ".join("?" for _ in _EVENT_COLUMNS)
    updates = ", ".join(
        f"{c}=excluded.{c}" for c in _EVENT_COLUMNS if c not in ("case_id", "event_id")
    )
    sql = (
        f"INSERT INTO events ({', '.join(_EVENT_COLUMNS)}) VALUES ({placeholders}) "
        f"ON CONFLICT(case_id, event_id) DO UPDATE SET {updates}"
    )
    with conn:
        conn.executemany(
            sql, [tuple(_event_to_record(e)[c] for c in _EVENT_COLUMNS) for e in events]
        )
    return len(events)


def events_for_case(conn: sqlite3.Connection, case_id: str) -> list[CorpusEvent]:
    """Predictable events defined for one case, in ``event_id`` order."""
    cur = conn.execute("SELECT * FROM events WHERE case_id = ? ORDER BY event_id", (case_id,))
    return [_event_from_record(record) for record in cur]


def event_count(conn: sqlite3.Connection) -> int:
    """Total number of predictable-event rows in the corpus."""
    cur = conn.execute("SELECT COUNT(*) AS n FROM events")
    return int(cur.fetchone()["n"])


# --- per-court discovery watermark (tracking state) ----------------------------


def get_discovery_watermark(conn: sqlite3.Connection, court: str) -> date | None:
    """The newest ``date_filed`` ``pull`` has discovered for ``court``, or ``None``.

    ``None`` means the court has never been discovered; the caller supplies the
    starting date for that first pass.
    """
    cur = conn.execute("SELECT last_filed FROM discovery_watermarks WHERE court = ?", (court,))
    record = cur.fetchone()
    return date.fromisoformat(record["last_filed"]) if record is not None else None


def set_discovery_watermark(conn: sqlite3.Connection, court: str, last_filed: date) -> None:
    """Advance (or initialize) ``court``'s forward-discovery watermark.

    The watermark only moves forward: a write older than the stored value is
    ignored, so a re-run that discovers nothing new cannot rewind the cursor.
    """
    with conn:
        conn.execute(
            "INSERT INTO discovery_watermarks (court, last_filed) VALUES (?, ?) "
            "ON CONFLICT(court) DO UPDATE SET last_filed = excluded.last_filed "
            "WHERE excluded.last_filed > discovery_watermarks.last_filed",
            (court, last_filed.isoformat()),
        )
