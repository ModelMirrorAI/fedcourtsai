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
import re
import sqlite3
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from .config import get_settings
from .corpus_ranged import RangedBackendError, connect_ranged
from .schemas import Disposition, EventKind

CORPUS_DB_FILENAME = "corpus.db"

# The corpus file's physical layout is a contract with ranged remote reads
# (read-only SQLite over HTTP range requests against the immutable blob on the
# DVC remote): 64 KB pages keep a B-tree descent to a handful of round trips
# (SQLite's maximum page size), and the file must not be in WAL mode at rest —
# a WAL reader needs the `-wal` sidecar, which never ships with the blob.
# `connect` creates databases with this layout, `ensure_ranged_layout` migrates
# a pre-existing file, and `check_ranged_layout` is the offline drift check
# `fedcourts dvc-status` enforces.
RANGED_PAGE_SIZE = 65536

# SQLite database header: the page size is the big-endian 16-bit word at offset
# 16, where the value 1 encodes 65536; the bytes at offsets 18/19 are the
# file-format write/read versions, 2 meaning WAL.
_HEADER_LEN = 20
_WAL_FORMAT_VERSION = 2


def corpus_db_path(corpus_root: Path) -> Path:
    """Location of the packed corpus database within ``corpus_root``."""
    return corpus_root / CORPUS_DB_FILENAME


def _file_layout(db_path: Path) -> tuple[int, bool] | None:
    """``(page_size, is_wal)`` from the SQLite file header, ``None`` if absent/empty."""
    if not db_path.is_file():
        return None
    with db_path.open("rb") as fh:
        header = fh.read(_HEADER_LEN)
    if len(header) < _HEADER_LEN:
        return None
    raw = int.from_bytes(header[16:18], "big")
    page_size = 65536 if raw == 1 else raw
    is_wal = _WAL_FORMAT_VERSION in (header[18], header[19])
    return page_size, is_wal


def check_ranged_layout(db_path: Path) -> list[str]:
    """Layout problems that would break ranged remote reads; empty when fine.

    Reads only the file header, so it is offline-safe and graceful before a
    ``dvc pull`` — an absent or empty file is not a problem, there is simply
    nothing to check yet.
    """
    layout = _file_layout(db_path)
    if layout is None:
        return []
    page_size, is_wal = layout
    problems: list[str] = []
    if page_size != RANGED_PAGE_SIZE:
        problems.append(
            f"{db_path}: page size {page_size} (ranged reads require {RANGED_PAGE_SIZE}; "
            "a corpus writer run migrates it)"
        )
    if is_wal:
        problems.append(
            f"{db_path}: WAL journal mode (the corpus must be non-WAL at rest; "
            "a corpus writer run migrates it)"
        )
    return problems


def ensure_ranged_layout(db_path: Path) -> bool:
    """Rebuild ``db_path`` to the ranged-read layout if it drifted; True if rebuilt.

    The migration for a file created under different settings: reset WAL to a
    rollback journal, set the 64 KB page size, and ``VACUUM`` so every page is
    rewritten at the new size. The corpus writers call this before their
    ``dvc add``, so a migration runs inside the job that already holds the
    ``corpus-write`` lock and the rebuilt file is what gets pushed. When the
    layout is already right this is a header read and a no-op.
    """
    if not check_ranged_layout(db_path):
        return False
    conn = sqlite3.connect(db_path)
    try:
        # Page-size changes need a VACUUM and cannot happen in WAL mode, so the
        # order matters: leave WAL first, set the size, then rebuild.
        conn.execute("PRAGMA journal_mode = DELETE")
        conn.execute(f"PRAGMA page_size = {RANGED_PAGE_SIZE}")
        conn.execute("VACUUM")
    finally:
        conn.close()
    return True


class PanelMember(BaseModel):
    """One judge on a decided case's panel, resolved against the people directory.

    The flat ``judges`` name list drives retrieval overlap; this carries the
    structured detail a name string cannot — the authoritative ``name`` and the
    judge's ``seniority`` (active / senior / chief / …) at decision time — for
    the sibling people-db bulk file the staged join resolves the cluster panel
    against. ``seniority`` is ``None`` when the directory does not record it.
    """

    model_config = ConfigDict(extra="forbid")

    name: str
    seniority: str | None = None


class CorpusRow(BaseModel):
    """One normalized, labeled raw-fact record in the corpus.

    Written identically whether a row originates from a bulk CSV (seed) or a
    REST docket (pull); the ingestion core maps both sources onto this shape.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    case_id: str = Field(description="Canonical `<court_id>/<docket_id>` id; primary key.")
    court: str
    docket_number: str = ""
    case_name: str = Field(
        default="",
        description="Case caption (e.g. `Doe v. Roe`), from the docket's case-name "
        "fields on both ingestion paths. The retrieval-judgment signal: a `query` "
        "prior without a caption cannot be assessed for comparability.",
    )
    date_filed: date | None = None
    date_decided: date | None = None
    disposition: Disposition | None = Field(
        default=None, description="Realized outcome label; None while unresolved."
    )
    judges: list[str] = Field(default_factory=list)
    panel: list[PanelMember] = Field(
        default_factory=list,
        description="Structured panel (name + seniority) resolved from the people directory; "
        "the joined detail behind the flat `judges` names.",
    )
    parties: list[str] = Field(
        default_factory=list, description="Party names on the docket (plaintiffs, appellants, …)."
    )
    attorneys: list[str] = Field(
        default_factory=list, description="Attorney names of record on the docket."
    )
    topic: str | None = Field(default=None, description="Nature of suit / subject-matter topic.")
    citations: list[str] = Field(default_factory=list)
    citation_count: int | None = Field(
        default=None, description="Times the decision has been cited (importance signal)."
    )
    precedential_status: str | None = Field(
        default=None, description="Published / Unpublished / Errata — the opinion's status."
    )
    opinion_text: str | None = None
    summary: str | None = None
    last_pulled: date | None = Field(
        default=None,
        description="Tracking state: date `pull` last refreshed this case via REST; "
        "None until first pulled. Drives the budget governor's rotation.",
    )
    predict_eligible: bool = Field(
        default=False,
        description="Prediction-scope latch: True once the case has interacted with "
        "SCOTUS, gating the agentic predict/evaluate stages. Set by the ingestion "
        "rule and never cleared by a later re-ingest; ingestion coverage is unaffected.",
    )
    predict_excluded: bool = Field(
        default=False,
        description="Out-of-scope latch (issue #343): True when the seed reconcile has "
        "marked this case excluded from predict scope (an out-of-scope predicate matched). "
        "Owned by the reconcile — not monotonic (cleared when a case returns to scope) and "
        "preserved across ingestion re-writes. Read by `open_events` so excluded cases yield "
        "no predictable events.",
    )
    originating_court: str | None = Field(
        default=None,
        description="Lower-court linkage: the court id this appellate / SCOTUS docket "
        "came from (CourtListener `appeal_from`), e.g. `ca9` for a SCOTUS petition. "
        "None when the source carries no lower-court link.",
    )
    originating_docket_number: str | None = Field(
        default=None,
        description="Lower-court linkage: the docket-number string in the originating "
        "court (CourtListener `originating_court_information.docket_number`). With "
        "`originating_court` this is the (court + number) join key onto the lower-court "
        "docket; only the REST path can populate it (bulk omits the table).",
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
    case_id             TEXT PRIMARY KEY,
    court               TEXT NOT NULL,
    docket_number       TEXT NOT NULL DEFAULT '',
    case_name           TEXT NOT NULL DEFAULT '',
    date_filed          TEXT,
    date_decided        TEXT,
    disposition         TEXT,
    judges              TEXT NOT NULL DEFAULT '[]',
    panel               TEXT NOT NULL DEFAULT '[]',
    parties             TEXT NOT NULL DEFAULT '[]',
    attorneys           TEXT NOT NULL DEFAULT '[]',
    topic               TEXT,
    citations           TEXT NOT NULL DEFAULT '[]',
    citation_count      INTEGER,
    precedential_status TEXT,
    opinion_text        TEXT,
    summary             TEXT,
    last_pulled         TEXT,
    predict_eligible    INTEGER NOT NULL DEFAULT 0,
    predict_excluded    INTEGER NOT NULL DEFAULT 0,
    originating_court            TEXT,
    originating_docket_number    TEXT
);
CREATE INDEX IF NOT EXISTS idx_cases_court ON cases(court);
CREATE INDEX IF NOT EXISTS idx_cases_disposition ON cases(disposition);
-- The governor rotates oldest-last_pulled-first over the unresolved set.
CREATE INDEX IF NOT EXISTS idx_cases_last_pulled ON cases(last_pulled);
-- retrieve_priors pushes its exact-match filters into SQL; each must be
-- index-served so a ranged remote read never scans the full cases table.
CREATE INDEX IF NOT EXISTS idx_cases_topic ON cases(topic);

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
-- The open-events census reads only unresolved rows; the partial index holds
-- exactly that (shrinking) subset in (case_id, event_id) order, so the census
-- is an ordered walk of a small index rather than a scan of every event —
-- which over ranged remote reads is the difference between KBs and the table.
CREATE INDEX IF NOT EXISTS idx_events_open ON events(case_id, event_id) WHERE resolved = 0;

-- Per-court forward-discovery watermark (the date_filed cursor for `pull`).
CREATE TABLE IF NOT EXISTS discovery_watermarks (
    court       TEXT PRIMARY KEY,
    last_filed  TEXT NOT NULL
);

-- Dated point-in-time docket snapshots: a raw fact, one per (case, pull date).
-- The full-docket JSON (docket + entries) a normalized `cases` row cannot fully
-- capture. Backs `pull`'s change detection and is the snapshot predictors and
-- evaluators are provisioned from at prediction time.
CREATE TABLE IF NOT EXISTS snapshots (
    case_id        TEXT NOT NULL,
    snapshot_date  TEXT NOT NULL,
    payload        TEXT NOT NULL,
    PRIMARY KEY (case_id, snapshot_date)
);
CREATE INDEX IF NOT EXISTS idx_snapshots_case ON snapshots(case_id);
"""

# Per-column DDL for the `cases` table, in storage order. Mirrors the `cases`
# definition in `_SCHEMA` and drives the additive migration below; a drift test
# keeps the two in lockstep. Every column beyond the original base set carries a
# constant DEFAULT so it can be back-filled with `ALTER TABLE ADD COLUMN` on a
# populated table.
_CASES_COLUMN_DDL: dict[str, str] = {
    "case_id": "TEXT PRIMARY KEY",
    "court": "TEXT NOT NULL",
    "docket_number": "TEXT NOT NULL DEFAULT ''",
    "case_name": "TEXT NOT NULL DEFAULT ''",
    "date_filed": "TEXT",
    "date_decided": "TEXT",
    "disposition": "TEXT",
    "judges": "TEXT NOT NULL DEFAULT '[]'",
    "panel": "TEXT NOT NULL DEFAULT '[]'",
    "parties": "TEXT NOT NULL DEFAULT '[]'",
    "attorneys": "TEXT NOT NULL DEFAULT '[]'",
    "topic": "TEXT",
    "citations": "TEXT NOT NULL DEFAULT '[]'",
    "citation_count": "INTEGER",
    "precedential_status": "TEXT",
    "opinion_text": "TEXT",
    "summary": "TEXT",
    "last_pulled": "TEXT",
    "predict_eligible": "INTEGER NOT NULL DEFAULT 0",
    "predict_excluded": "INTEGER NOT NULL DEFAULT 0",
    "originating_court": "TEXT",
    "originating_docket_number": "TEXT",
}

_COLUMNS = tuple(_CASES_COLUMN_DDL)


def _migrate_cases(conn: sqlite3.Connection) -> None:
    """Back-fill `cases` columns added after the table was first created.

    `CREATE TABLE IF NOT EXISTS` leaves an existing table untouched, so a corpus
    written by an older schema is missing any column introduced since. Add each
    missing column with its declared DDL; the constant DEFAULTs keep the ALTER
    valid on populated rows. Idempotent — a current-schema table adds nothing.
    """
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(cases)")}
    for column in _COLUMNS:
        if column not in existing:
            conn.execute(f"ALTER TABLE cases ADD COLUMN {column} {_CASES_COLUMN_DDL[column]}")


_DN_LABEL = re.compile(r"^NOS?\.?\s+")  # a leading "No." / "Nos." / "No " docket-number label
_DN_WHITESPACE = re.compile(r"\s+")
# Typographic dashes (en U+2013 / em U+2014) that stand in for a plain hyphen in a
# docket number, folded so a dash-variant reads as the modern Term-year form (#362).
_DN_DASHES = {0x2013: "-", 0x2014: "-"}


def normalize_docket_number(raw: str | None) -> str | None:
    """Canonicalize a docket-number string for the lower-court join, or ``None``.

    Upper-cases, drops a leading ``No.`` label, folds a typographic en/em dash to a
    plain hyphen, and removes all whitespace, so two spellings of the *same* number
    compare equal (``"No. 21-35466"`` == ``"21-35466"``, and a dash-variant Term
    docket reads like ``"01-7700"``). Deliberately a light, lossless normalization
    that yields no false matches: a consolidated / multi-number string
    (``"21-1, 21-2"``) keeps
    its punctuation and so will not match a single tracked docket — a miss, never a
    wrong link. Blank input (and a string that normalizes to empty) returns
    ``None``. Registered as the SQLite ``norm_dn`` function so the join can compare
    a stored ``docket_number`` against a normalized incoming value.
    """
    if raw is None:
        return None
    text = _DN_WHITESPACE.sub("", _DN_LABEL.sub("", raw.strip().upper().translate(_DN_DASHES)))
    return text or None


@contextmanager
def connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    """Open the corpus database (creating its schema), yielding a connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # The lower-court join normalizes the stored docket_number with the same rule
    # the caller normalizes the incoming value, so both sides compare canonically.
    conn.create_function("norm_dn", 1, normalize_docket_number, deterministic=True)
    try:
        # Before any page exists: a fresh database is born with the ranged-read
        # page size (inert on an existing file, whose size is already fixed).
        conn.execute(f"PRAGMA page_size = {RANGED_PAGE_SIZE}")
        conn.executescript(_SCHEMA)
        _migrate_cases(conn)
        yield conn
    finally:
        conn.close()


CorpusBackend = Literal["local", "ranged"]


def resolve_backend(override: CorpusBackend | None = None) -> CorpusBackend:
    """The effective read backend: an explicit override, else the setting."""
    if override is not None:
        return override
    return get_settings().corpus_backend


class ReadConnection(Protocol):
    """The read seam the retrieval/provisioning helpers require of a connection.

    ``sqlite3.Connection`` satisfies it structurally (the local backend), as
    does :class:`fedcourtsai.corpus_ranged.RangedConnection` (the ranged
    backend) — rows only need name indexing, which both provide.
    """

    def execute(self, sql: str, parameters: Sequence[object] = (), /) -> Any: ...


class RecordRow(Protocol):
    """One name-indexable result row — ``sqlite3.Row`` or the ranged ``Row``."""

    def __getitem__(self, key: str) -> Any: ...


@contextmanager
def connect_readonly(
    db_path: Path, *, backend: CorpusBackend | None = None
) -> Iterator[ReadConnection]:
    """Open the corpus for reading via the selected backend.

    ``local`` (the default) opens the ``dvc pull``-ed file exactly like
    :func:`connect`; ``ranged`` queries the immutable blob in place on the DVC
    remote (see :mod:`fedcourtsai.corpus_ranged`), resolving the committed
    pointer next to ``db_path`` against the out-of-band remote URL. ``backend``
    overrides the ``FEDCOURTS_CORPUS_BACKEND`` setting. Writers never use this
    seam — they need the concrete local connection and always own the file.
    """
    if resolve_backend(backend) == "ranged":
        remote_url = get_settings().dvc_remote_url
        if remote_url is None:
            raise RangedBackendError(
                "the ranged corpus backend needs the DVC remote URL from the "
                "environment (the same out-of-band value the workflows use)"
            )
        pointer = db_path.with_name(db_path.name + ".dvc")
        with connect_ranged(pointer, remote_url) as ranged:
            yield ranged
    else:
        with connect(db_path) as conn:
            yield conn


def _to_record(row: CorpusRow) -> dict[str, object]:
    return {
        "case_id": row.case_id,
        "court": row.court,
        "docket_number": row.docket_number,
        "case_name": row.case_name,
        "date_filed": row.date_filed.isoformat() if row.date_filed else None,
        "date_decided": row.date_decided.isoformat() if row.date_decided else None,
        "disposition": row.disposition,
        "judges": json.dumps(row.judges, sort_keys=True),
        "panel": json.dumps([m.model_dump() for m in row.panel], sort_keys=True),
        "parties": json.dumps(row.parties, sort_keys=True),
        "attorneys": json.dumps(row.attorneys, sort_keys=True),
        "topic": row.topic,
        "citations": json.dumps(row.citations, sort_keys=True),
        "citation_count": row.citation_count,
        "precedential_status": row.precedential_status,
        "opinion_text": row.opinion_text,
        "summary": row.summary,
        "last_pulled": row.last_pulled.isoformat() if row.last_pulled else None,
        "predict_eligible": int(row.predict_eligible),
        "predict_excluded": int(row.predict_excluded),
        "originating_court": row.originating_court,
        "originating_docket_number": row.originating_docket_number,
    }


def _from_record(record: RecordRow) -> CorpusRow:
    return CorpusRow(
        case_id=record["case_id"],
        court=record["court"],
        docket_number=record["docket_number"],
        case_name=record["case_name"],
        date_filed=date.fromisoformat(record["date_filed"]) if record["date_filed"] else None,
        date_decided=(
            date.fromisoformat(record["date_decided"]) if record["date_decided"] else None
        ),
        disposition=record["disposition"],
        judges=json.loads(record["judges"]),
        panel=[PanelMember(**m) for m in json.loads(record["panel"])],
        parties=json.loads(record["parties"]),
        attorneys=json.loads(record["attorneys"]),
        topic=record["topic"],
        citations=json.loads(record["citations"]),
        citation_count=record["citation_count"],
        precedential_status=record["precedential_status"],
        opinion_text=record["opinion_text"],
        summary=record["summary"],
        last_pulled=(date.fromisoformat(record["last_pulled"]) if record["last_pulled"] else None),
        predict_eligible=bool(record["predict_eligible"]),
        predict_excluded=bool(record["predict_excluded"]),
        originating_court=record["originating_court"],
        originating_docket_number=record["originating_docket_number"],
    )


def _update_clause(column: str) -> str:
    """The ``ON CONFLICT`` assignment for one column, honoring its latch (if any).

    Most columns take the incoming value (``excluded``). Three are special:
    ``last_pulled`` only ever advances — a write without a fresh stamp (e.g. a
    bulk seed re-ingest) keeps the timestamp a prior pull recorded; ``predict_eligible``
    only ever latches on, so once a case is in prediction scope a later re-ingest
    (under a narrower rule) cannot drop it back out; and ``predict_excluded`` is owned
    by the seed reconcile (not an ingestion fact), so an upsert keeps the stored value
    rather than resetting it to the model default.
    """
    if column == "last_pulled":
        return f"{column}=COALESCE(excluded.{column}, cases.{column})"
    if column == "predict_eligible":
        return f"{column}=MAX(excluded.{column}, cases.{column})"
    if column == "predict_excluded":
        # The seed reconcile owns this flag (it is not an ingestion fact and is not
        # monotonic), so a re-ingest must never clobber it — keep the stored value.
        return f"{column}=cases.{column}"
    return f"{column}=excluded.{column}"


def upsert_rows(conn: sqlite3.Connection, rows: list[CorpusRow]) -> int:
    """Insert or replace rows by ``case_id``; returns the number written.

    Idempotent: re-ingesting the same case overwrites its row, so ``seed`` and
    ``pull`` can both write a case without producing duplicates.
    """
    placeholders = ", ".join("?" for _ in _COLUMNS)
    updates = ", ".join(_update_clause(c) for c in _COLUMNS if c != "case_id")
    sql = (
        f"INSERT INTO cases ({', '.join(_COLUMNS)}) VALUES ({placeholders}) "
        f"ON CONFLICT(case_id) DO UPDATE SET {updates}"
    )
    with conn:
        conn.executemany(sql, [tuple(_to_record(r)[c] for c in _COLUMNS) for r in rows])
    return len(rows)


def latch_originating_eligible(conn: sqlite3.Connection, rows: Iterable[CorpusRow]) -> int:
    """Latch ``predict_eligible`` on the tracked originating docket of each SCOTUS row.

    The second half of the prediction-scope rule: once a case interacts with the
    Supreme Court its originating court-of-appeals docket — where post-cert and
    remand activity lands — is also in scope (``docs/data-pipeline.md``). For every
    SCOTUS row in ``rows`` carrying a lower-court link (``originating_court`` +
    ``originating_docket_number``), set the latch on the corpus docket matching
    ``(court, normalized docket_number)``. Matching is grouped per originating court
    so at most one indexed scan per court runs, regardless of how many SCOTUS rows
    share it.

    Forward-only and idempotent, exactly like the ingestion latch: an unlinked
    SCOTUS row, or one whose originating docket is not tracked, is a no-op; an
    already-eligible docket is left alone (``predict_eligible = 0`` guards the
    write); and the flag is only ever set, never cleared. Returns the number of
    dockets newly latched this call.
    """
    by_court: dict[str, set[str]] = {}
    for row in rows:
        if row.court != "scotus":
            continue
        norm = normalize_docket_number(row.originating_docket_number)
        if row.originating_court and norm is not None:
            by_court.setdefault(row.originating_court, set()).add(norm)
    if not by_court:
        return 0
    latched = 0
    with conn:
        for court, norms in sorted(by_court.items()):
            placeholders = ", ".join("?" for _ in norms)
            cur = conn.execute(
                "UPDATE cases SET predict_eligible = 1 "
                f"WHERE court = ? AND predict_eligible = 0 AND norm_dn(docket_number) IN "
                f"({placeholders})",
                (court, *sorted(norms)),
            )
            latched += cur.rowcount
    return latched


# The Judiciary Act of 1925 (the "Judges' Bill") made the Supreme Court's
# jurisdiction largely discretionary; matters filed before it were appeals and
# writs of error heard *as of right* and decided on the merits. A pre-1925 docket
# number is a bare sequential integer ("801"); the modern discretionary-cert era
# carries a Term-year prefix ("01-7700", "22-451", "22A123").
_DISCRETIONARY_ERA_YEAR = 1925


def is_historical_mandatory(row: CorpusRow) -> bool:
    """Whether a SCOTUS row is a pre-1925 mandatory-jurisdiction matter (issue #309).

    The ``evt-petition-disposition`` event model targets the *modern discretionary
    cert* regime (a ~1% grant base rate, "granted" = the Court takes the case up).
    Pre-1925 appeals heard as of right do not fit it — for them the meaningful
    disposition is the merits outcome (affirmed / reversed), a different label — so
    the predict/evaluate scope excludes them rather than overloading one event kind
    across two regimes. Detected by the one signal their unusually sparse snapshots
    reliably carry: a **bare sequential docket number** with no Term-year prefix
    (e.g. ``801`` vs a modern ``01-7700``); a ``date_filed`` before the Judiciary
    Act of 1925 corroborates it on the rare row that carries one (these snapshots
    typically have every activity date null).

    Non-SCOTUS rows are never historical-mandatory here — the regime is a Supreme
    Court concept, and the gate only ever sees a case once it is SCOTUS-eligible.

    The bare-number test is applied to the *normalized* docket (issue #343): a great
    many historical SCOTUS dockets carry a ``No.`` label (``"No. 123"``), which a raw
    ``isdigit`` misses; :func:`normalize_docket_number` strips that, so they read as
    the bare sequential numbers they are.
    """
    if row.court != "scotus":
        return False
    docket_number = normalize_docket_number(row.docket_number) or ""
    bare_sequential = docket_number.isdigit()
    pre_discretionary = row.date_filed is not None and row.date_filed.year < _DISCRETIONARY_ERA_YEAR
    return bare_sequential or pre_discretionary


# SCOTUS docket numbers lead with a two-digit October-Term year ("01-7700" ->
# OT2001, "93-7515" -> OT1993). The century pivot is 30: a 30-99 prefix is 19xx
# and 00-29 is 20xx. The corpus demonstrably holds mid-century year-prefixed
# dockets (e.g. "68-..." petitions from OT1968), while a Term decades in the
# future cannot exist — so every prefix >= 30 must be 19xx. Good through OT2029;
# revisit the pivot before the 2030 Term.
_SCOTUS_TERM_RE = re.compile(r"^(\d{2})-\d+")

# Provisional staleness cutoff (issue #343 refines it against the corpus). A SCOTUS
# Term before this is long past any pending-petition horizon; far enough back that a
# genuinely open modern cert petition is never caught.
_STALE_TERM_CUTOFF_YEAR = 2015


def scotus_term_year(docket_number: str) -> int | None:
    """Parse the October-Term year from a modern SCOTUS docket number, or ``None``.

    ``"01-7700"`` -> ``2001``, ``"93-7515"`` -> ``1993``, ``"68-123"`` -> ``1968``,
    and (after normalization) ``"No. 01-7700"`` -> ``2001`` — the ``No.`` label
    dominates the historical SCOTUS dockets the raw parser used to miss. Returns
    ``None`` for anything that is not the ``YY-NNNN`` form — bare sequential
    numbers (``"801"``), application/original dockets (``"22A123"``, ``"22O141"``),
    or blank — so callers fall through rather than guess a year. Public so the
    scope audit can bucket the open events the predicate does *not* catch.
    """
    match = _SCOTUS_TERM_RE.match(normalize_docket_number(docket_number) or "")
    if match is None:
        return None
    two_digit = int(match.group(1))
    return 1900 + two_digit if two_digit >= 30 else 2000 + two_digit


def is_modern_cert(row: CorpusRow) -> bool:
    """Whether a SCOTUS docket is a modern discretionary-cert petition, by form.

    The Term-prefixed ``YY-NNNN`` docket number is the post-1925 discretionary-cert
    form — the population the ``evt-petition-disposition`` model actually predicts.
    Bare sequential (pre-1925), application (``22A123``), original (``22O141``),
    and unparseable numbers all fall outside it, as does every non-SCOTUS row.
    The cert-stage base-rate cut keys on this, so the calibration anchor the
    prompts point at reflects modern grant/deny petitions rather than blending in
    historical merits-era labels.
    """
    return row.court == "scotus" and scotus_term_year(row.docket_number) is not None


def case_year(row: CorpusRow) -> int | None:
    """The year a case is anchored to, from its best temporal signal, or ``None``.

    A SCOTUS row's parsed October-Term year, then ``date_filed``, then
    ``date_decided``. Most corpus rows carry no full dates, so this year is the
    finest timing signal that generalizes: it is the key behind
    :func:`case_era` and the ``decided_before`` retrieval cutoff. ``None`` when
    the row carries no signal at all (the bare bulk-import shells).
    """
    if row.court == "scotus":
        year = scotus_term_year(row.docket_number)
        if year is not None:
            return year
    if row.date_filed is not None:
        return row.date_filed.year
    if row.date_decided is not None:
        return row.date_decided.year
    return None


def case_era(row: CorpusRow) -> str | None:
    """The decade bucket a case belongs to (``"1890s"``, ``"2020s"``), or ``None``.

    :func:`case_year`'s decade; ``None`` when the row carries no temporal signal,
    so consumers show a visible no-era bucket rather than guessing. Historical
    cases can thereby be base-rated against their own period even where
    ``--term`` cannot parse.
    """
    year = case_year(row)
    if year is None:
        return None
    return f"{year - year % 10}s"


def is_stale_unresolvable(row: CorpusRow) -> bool:
    """Whether a SCOTUS row is an old petition the corpus can never resolve (issue #333).

    Modern-format SCOTUS petitions from old Terms (e.g. ``93-7515`` -> OT1993,
    ``01-7700`` -> OT2001) whose snapshots are bare stubs — empty docket entries,
    null cert dates — sit perpetually open because deterministic outcome detection
    has nothing to resolve them from, so they are re-predicted every run decades
    after they actually resolved (the bulk of the noise on the #333 feedback issue).
    Distinct from :func:`is_historical_mandatory`: those are *pre-1925* mandatory-
    jurisdiction matters with bare sequential numbers; these are post-1925
    discretionary-cert dockets that are simply too old to still be pending.

    **Provisional and deliberately conservative — issue #343 refines it.** Caught
    only when: SCOTUS; no realized ``disposition`` and no ``date_decided`` (still
    open in the corpus); and a docket-number Term year older than
    ``_STALE_TERM_CUTOFF_YEAR``. Rows whose Term year cannot be parsed from the
    docket number are left in scope, so the rule may under-catch (a stub still
    flags) but never drops a live modern petition.
    """
    if row.court != "scotus":
        return False
    if row.disposition is not None or row.date_decided is not None:
        return False
    term_year = scotus_term_year(row.docket_number)
    return term_year is not None and term_year < _STALE_TERM_CUTOFF_YEAR


def is_published_opinion_unresolvable(row: CorpusRow) -> bool:
    """Whether a still-open SCOTUS row's disposition lives only in an opinion (issue #363).

    The recoverability probe (`run-analytics`, recoverability mode) found these historical
    ``evt-petition-disposition`` cases carry a **linked published opinion** (a reporter
    citation / non-zero ``citation_count`` / ``opinion_text``) but **no machine-readable
    disposition** on either the docket or the cluster and no docket entries. The outcome
    exists only in the opinion *text* — recoverable by parsing it, not by a structured
    re-ingest — and for a cert event it is a **merits** label (affirmed / reversed), not
    a cert grant/deny, so the modern discretionary-cert model cannot score it. Predict
    scope therefore excludes it.

    Complements the two siblings for the cases their docket-number tests cannot parse
    (issue #362): :func:`is_stale_unresolvable` needs a parseable ``YY-NNNN`` Term year,
    and :func:`is_historical_mandatory` needs a bare sequential number or a pre-1925
    ``date_filed`` (null on these rows) — so an old, oddly-formatted docket with a
    published opinion falls through both and lands here instead.

    Safe against a live petition **by construction**: a pending cert petition has no
    published opinion yet (no citation, no ``opinion_text``), so it can never match.
    SCOTUS-only, and only while still open (no ``disposition`` and no ``date_decided``);
    a case that later gains a real disposition is released by the two-directional scope
    reconcile. The published-opinion signal mirrors ``validate._recoverable_signal``.
    """
    if row.court != "scotus":
        return False
    if row.disposition is not None or row.date_decided is not None:
        return False
    return bool(row.citations or row.citation_count or row.opinion_text)


# SCOTUS application ("22A123", older "A-9999"), original-jurisdiction ("22O141"),
# and miscellaneous/motions ("22M75", "03M77") docket numbers — the term letter
# (A / O / M) marks a form that is not the modern discretionary-cert petition. A
# trailing period on the historical spelling ("22A99.") is tolerated; the letter
# is what a cert docket's ``YY-NNNN`` never carries.
_SCOTUS_APPLICATION_RE = re.compile(r"^(?:\d{2}A\d+|A-?\d+)\.?$")
_SCOTUS_ORIGINAL_RE = re.compile(r"^\d{2}O\d+\.?$")
_SCOTUS_MISCELLANEOUS_RE = re.compile(r"^\d{2}M\d+\.?$")
# The spelled-out original-jurisdiction ("No. 155, Orig." / "155, Original.") and
# miscellaneous ("No. 33, Misc." — the pre-1971 separate docket, merged into the
# unified numbering at OT1970) markers — the text-form counterparts of the numeric
# letter forms, tells a cert docket's `YY-NNNN` never carries.
_SCOTUS_ORIGINAL_TEXT_RE = re.compile(r"ORIG")
_SCOTUS_MISC_TEXT_RE = re.compile(r"MISC")


def is_non_cert_scotus_form(row: CorpusRow) -> bool:
    """Whether a SCOTUS docket is an application or original-jurisdiction matter (issue #362).

    A stay / emergency **application** (``22A123``, older ``A-9999``), an
    **original-jurisdiction** case (``22O141`` numeric, or its spelled-out
    ``No. 155, Orig.`` / ``Original`` form — e.g. a State-v-State dispute), and a
    **miscellaneous** docket (``22M75`` / ``03M77`` — the modern motions docket,
    e.g. leave to file out of time — or the pre-1971 ``No. 33, Misc.`` separate
    docket, merged into the unified numbering at OT1970) are not the
    discretionary-cert form the ``evt-petition-disposition`` model targets: an
    application's disposition is a stay grant/deny, an original case's a merits
    judgment, and a motions docket's a procedural leave — none the cert
    grant/deny the model calibrates on — while the pre-1971 miscellaneous docket
    is decades-stale by construction. So predict scope excludes them (as it does
    the pre-1925 mandatory-jurisdiction regime, #309), keyed on the term letter
    (``A`` / ``O`` / ``M``) or the ``Orig`` / ``Misc`` marker that a cert
    docket's ``YY-NNNN`` never carries. SCOTUS-only.

    Conservative — it matches on format alone, so it never catches a modern cert
    petition (which carries a hyphen, no letter and no ``Orig``/``Misc`` marker).
    If application *stays* are later modeled as their own motion events (issue
    #372), refine this to spare those rather than the whole case; today an
    application docket carries only the mis-fit cert baseline, so excluding the
    case loses nothing.
    """
    if row.court != "scotus":
        return False
    dn = normalize_docket_number(row.docket_number) or ""
    return bool(
        _SCOTUS_APPLICATION_RE.match(dn)
        or _SCOTUS_ORIGINAL_RE.match(dn)
        or _SCOTUS_MISCELLANEOUS_RE.match(dn)
        or _SCOTUS_ORIGINAL_TEXT_RE.search(dn)
        or _SCOTUS_MISC_TEXT_RE.search(dn)
    )


# Separators a consolidated multi-docket string joins its members with:
# "No. 155; No. 156", "Nos. 522, 523, 524", "Nos. 155 and 156", "155 & 156".
_CONSOLIDATED_SEPARATORS = re.compile(r";|,|&|\band\b", re.IGNORECASE)


def consolidated_docket_members(raw: str) -> list[str] | None:
    """The member docket numbers of a consolidated multi-docket string, or ``None``.

    Splits the **raw** string on the separators and normalizes each member
    individually (so a per-member ``No.`` / ``Nos.`` label is stripped), keeping
    the non-empty results. ``None`` when the string is not consolidated — no
    separator, or fewer than two members survive — so the single-docket
    predicates own it. Deliberately a *scope* reader, not a join key:
    :func:`normalize_docket_number` keeps refusing multi-number strings for the
    lower-court join (a miss, never a wrong link), while the scope predicates may
    classify the members it refuses to match.
    """
    if not raw or not _CONSOLIDATED_SEPARATORS.search(raw):
        return None
    members = [normalize_docket_number(part) for part in _CONSOLIDATED_SEPARATORS.split(raw)]
    found = [member for member in members if member]
    return found if len(found) >= 2 else None


def is_consolidated_out_of_scope(row: CorpusRow) -> bool:
    """Whether a consolidated SCOTUS docket's members all classify out of scope (issue #449).

    A consolidated row carries several docket numbers in one string, so no
    single-number predicate can read it. This rule splits the members
    (:func:`consolidated_docket_members`) and runs **each member through the
    existing single-docket predicates** on a copy of the row: the row leaves
    predict scope only when *every* member agrees — all bare-sequential numbers
    (the pre-1925 mandatory-jurisdiction regime, #309) or all stale Term years
    on a still-open row (#333). Any disagreement, or any member the predicates
    cannot read, keeps the row in scope and visible in the audit's unclassified
    bucket — conservative like every sibling: it can under-catch, never drop a
    live consolidated petition (whose members parse to recent Terms and match
    neither branch). SCOTUS-only.
    """
    if row.court != "scotus":
        return False
    members = consolidated_docket_members(row.docket_number)
    if members is None:
        return False
    member_rows = [row.model_copy(update={"docket_number": member}) for member in members]
    return all(is_historical_mandatory(member) for member in member_rows) or all(
        is_stale_unresolvable(member) for member in member_rows
    )


def is_date_inconsistent(row: CorpusRow) -> bool:
    """Whether a case's filing/decision dates are internally inconsistent (issue #171).

    ``date_decided`` before ``date_filed`` — a case that looks decided before it was
    filed. A faithful but nonsensical CourtListener ordering the validation monitor
    (#171) tracks *without* rewriting; such a case cannot yield a meaningful
    prediction, so the predict scope excludes it. Court-agnostic (the malformation is
    not SCOTUS-specific). This does **not** weaken the monitor — the validation check
    still counts these rows; only prediction skips them.
    """
    return (
        row.date_filed is not None
        and row.date_decided is not None
        and row.date_decided < row.date_filed
    )


def is_bare_import_profile(row: CorpusRow) -> bool:
    """Whether a SCOTUS row carries none of the fields the sibling predicates key on.

    The bulk import leaves a class of historical opinion-import dockets with an
    **empty docket number, null dates, no disposition, and no citation/opinion
    fields** — exactly the row fields every other exclusion predicate tests — so
    they fall through all of them. This profile is one half of
    :func:`is_bare_opinion_import` (issue #438); alone it is *not* an exclusion
    signal, because a row this empty could also be a malformed but genuinely live
    case. The other half — the latest snapshot linking a published opinion
    cluster — is what marks it as a decided historical matter.
    """
    if row.court != "scotus":
        return False
    if normalize_docket_number(row.docket_number):
        return False
    if row.date_filed is not None or row.date_decided is not None or row.disposition is not None:
        return False
    return not (row.citations or row.citation_count or row.opinion_text)


def snapshot_links_opinion_cluster(payload: Mapping[str, Any]) -> bool:
    """Whether a docket snapshot links at least one opinion cluster.

    CourtListener dockets carry a ``clusters`` list of opinion-cluster URLs; a
    non-empty list means a published opinion exists for the docket — the decided
    signal a bare bulk-import row itself does not carry.
    """
    return bool(payload.get("clusters"))


def is_bare_opinion_import(row: CorpusRow, snapshot: Mapping[str, Any] | None) -> bool:
    """Whether a row is a bare bulk-import docket whose snapshot links an opinion (issue #438).

    The profile of a historical opinion-import docket: every row field the sibling
    exclusion predicates key on is empty (:func:`is_bare_import_profile`), while
    the latest snapshot **links an opinion cluster** — the decision is published,
    so the matter resolved long ago, but the petition-stage facts a cert
    prediction needs were never imported. Predicting such a case only ever emits
    the raw base rate, so predict scope excludes it.

    Safe against a live petition by construction, like the sibling
    :func:`is_published_opinion_unresolvable`: a pending case has no published
    opinion cluster to link. Two-directional like every latched exclusion — a
    later re-ingest that fills in real petition-stage facts (a docket number, a
    filing date) breaks the bare profile and the scope reconcile releases the
    latch. Needs the snapshot, so it cannot join the row-only
    ``OUT_OF_SCOPE_RULES``; :func:`out_of_scope_reason_full` applies it wherever
    the corpus is at hand, and row-only seams see it through ``predict_excluded``.
    """
    return (
        is_bare_import_profile(row)
        and snapshot is not None
        and (snapshot_links_opinion_cluster(snapshot))
    )


BARE_OPINION_IMPORT_REASON = (
    "bare bulk-import row whose snapshot links a published opinion cluster (#438)"
)


# Each (predicate, reason) the predict-scope gate excludes a case on from the row
# alone — shared by every enforcement seam via :func:`out_of_scope_reason` /
# :func:`out_of_scope_reason_full`, so an exclusion that lands here is enforced at
# every point. Snapshot-aware exclusions (the bare opinion-import rule) cannot live
# in this row-only list; they are applied by :func:`out_of_scope_reason_full`.
OUT_OF_SCOPE_RULES: list[tuple[Callable[[CorpusRow], bool], str]] = [
    (is_historical_mandatory, "pre-1925 mandatory-jurisdiction matter (#309)"),
    (is_stale_unresolvable, "stale unresolvable old SCOTUS petition (#333)"),
    (
        is_published_opinion_unresolvable,
        "published opinion but no machine-readable cert disposition (#363)",
    ),
    (
        is_non_cert_scotus_form,
        "SCOTUS application / original-jurisdiction docket — not discretionary cert (#362)",
    ),
    (
        is_consolidated_out_of_scope,
        "consolidated docket whose members all classify out of scope (#449)",
    ),
    (is_date_inconsistent, "internally inconsistent dates — decided before filed (#171)"),
]


def out_of_scope_reason(row: CorpusRow) -> str | None:
    """The first exclusion reason matching ``row``, or ``None`` if it is in predict scope.

    Row-only: applies just the predicates a :class:`CorpusRow` can answer.
    Callers holding a corpus connection should prefer
    :func:`out_of_scope_reason_full`, which adds the snapshot-aware rules; a seam
    without the corpus sees those through the ``predict_excluded`` latch instead.
    """
    for predicate, reason in OUT_OF_SCOPE_RULES:
        if predicate(row):
            return reason
    return None


def out_of_scope_reason_full(conn: ReadConnection, row: CorpusRow) -> str | None:
    """Every exclusion reason a corpus connection can evaluate, or ``None`` if in scope.

    The row rules (:func:`out_of_scope_reason`) plus the snapshot-aware bare
    opinion-import rule (:func:`is_bare_opinion_import`), which needs the case's
    latest snapshot. The one reason evaluator for every seam that holds the
    corpus — the scope reconcile, the scope audit, the cleanup sweep, the pull
    queue gate, and the matrix backstop. The snapshot is fetched only for rows
    matching the bare profile, so the common case costs nothing extra.
    """
    reason = out_of_scope_reason(row)
    if reason is not None:
        return reason
    if is_bare_import_profile(row):
        snap = latest_snapshot(conn, row.case_id)
        if snap is not None and snapshot_links_opinion_cluster(snap[1]):
            return BARE_OPINION_IMPORT_REASON
    return None


def get_row(conn: ReadConnection, case_id: str) -> CorpusRow | None:
    """Fetch a single case row, or ``None`` if it is not in the corpus."""
    cur = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    record = cur.fetchone()
    return _from_record(record) if record is not None else None


def count(conn: ReadConnection) -> int:
    """Number of rows currently in the corpus."""
    cur = conn.execute("SELECT COUNT(*) AS n FROM cases")
    return int(cur.fetchone()["n"])


def iter_rows(
    conn: sqlite3.Connection,
    *,
    court: str | None = None,
    disposition: Disposition | None = None,
    resolved: bool | None = None,
    predict_eligible: bool | None = None,
) -> Iterator[CorpusRow]:
    """Yield rows in ``case_id`` order, optionally filtered by court / disposition.

    The filters cover the common retrieval and back-test selections; richer
    querying (by judge, topic, citation, or semantic similarity) is layered on
    top of this same store. ``resolved`` keeps only rows carrying (``True``) or
    lacking (``False``) a realized disposition — pushed into SQL so a consumer of
    the small resolved slice never pays a full-corpus scan. ``predict_eligible``
    scopes to the prediction universe (the scope reconcile only weighs cases that
    could actually be predicted).
    """
    clauses: list[str] = []
    params: list[object] = []
    if court is not None:
        clauses.append("court = ?")
        params.append(court)
    if disposition is not None:
        clauses.append("disposition = ?")
        params.append(Disposition(disposition).value)
    if resolved is not None:
        clauses.append("disposition IS NOT NULL" if resolved else "disposition IS NULL")
    if predict_eligible is not None:
        clauses.append("predict_eligible = ?")
        params.append(int(predict_eligible))
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    cur = conn.execute(f"SELECT * FROM cases{where} ORDER BY case_id", params)
    for record in cur:
        yield _from_record(record)


def set_predict_excluded(conn: sqlite3.Connection, case_id: str, excluded: bool) -> None:
    """Set a case's out-of-scope latch (issue #343). The seed reconcile's sole writer.

    Owned here rather than through ``upsert_rows`` so ingestion never disturbs it
    (the upsert keeps the stored value — see :func:`_update_clause`) and so the
    reconcile can both set and clear it as a case leaves or re-enters scope.
    """
    with conn:
        conn.execute(
            "UPDATE cases SET predict_excluded = ? WHERE case_id = ?", (int(excluded), case_id)
        )


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
    era: str | None = Field(
        default=None,
        description="Restrict to one decade era, e.g. `1890s` (see `case_era`) — "
        "so historical cases retrieve priors from their own period.",
    )
    decided_before: int | None = Field(
        default=None,
        description="Exclusive year cutoff: keep only priors whose best-known year "
        "(`case_year`) strictly precedes it. Rows with no derivable year are "
        "excluded — a prior qualifies only when it provably came first. This is "
        "the back-test replay clock; live (forward) retrieval omits it because "
        "every resolved prior genuinely precedes an open case.",
    )
    resolved_only: bool = Field(
        default=True, description="Keep only labeled (decided) cases — precedent."
    )


def recency_key(row: CorpusRow) -> tuple[int, int]:
    """Sort key putting decided cases first, newest decision first.

    Undated rows sort after dated ones; among dated rows the negated ordinal
    makes the most recent decision compare smallest (so it leads in an ascending
    sort).
    """
    if row.date_decided is not None:
        return (0, -row.date_decided.toordinal())
    return (1, 0)


def retrieve_priors(
    conn: ReadConnection,
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
        # Era and year are derived (Term year or filing/decision dates), not
        # stored columns, so they filter here rather than in SQL.
        if query.era is not None and case_era(row) != query.era:
            continue
        if query.decided_before is not None:
            year = case_year(row)
            if year is None or year >= query.decided_before:
                continue
        judge_overlap = want_judges & set(row.judges)
        citation_overlap = want_citations & set(row.citations)
        # Overlap filters are required when given: skip a row that shares none.
        if want_judges and not judge_overlap:
            continue
        if want_citations and not citation_overlap:
            continue
        score = len(judge_overlap) + len(citation_overlap)
        scored.append((-score, recency_key(row), row.case_id, row))
    scored.sort(key=lambda item: (item[0], item[1], item[2]))
    return [row for *_, row in scored[:limit]]


def _rotation_rows(
    conn: sqlite3.Connection,
    *,
    limit: int,
    skip_closed: bool,
    only_eligible: bool = False,
) -> list[CorpusRow]:
    """Stalest-first active cases: never-pulled first, then oldest ``last_pulled``.

    The shared query behind :func:`rotation_for_pull`. ``skip_closed`` drops cases
    carrying a realized ``disposition`` / ``date_decided`` (their outcome is known);
    ``only_eligible`` further restricts to ``predict_eligible`` cases. ``case_id``
    breaks ties so the order is deterministic.
    """
    if limit <= 0:
        return []
    clauses: list[str] = []
    if skip_closed:
        clauses.append("disposition IS NULL AND date_decided IS NULL")
    if only_eligible:
        clauses.append("predict_eligible = 1")
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    cur = conn.execute(
        f"SELECT * FROM cases{where} "
        "ORDER BY last_pulled IS NOT NULL, last_pulled ASC, case_id ASC "
        "LIMIT ?",
        (limit,),
    )
    return [_from_record(record) for record in cur]


def rotation_for_pull(
    conn: sqlite3.Connection,
    *,
    limit: int,
    skip_closed: bool = True,
    eligible_reserve: int = 0,
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

    ``eligible_reserve`` reserves up to that many of the ``limit`` slots for the
    stalest **``predict_eligible``** cases (the SCOTUS-touched pilot set), filled
    first; the remainder fall to the normal stalest-first rotation over the whole
    active set. This keeps the small predict-eligible pool rotating fast enough to
    catch new docket activity before a case resolves, instead of waiting its turn
    behind the much larger active set. Reserve slots the eligible pool cannot fill
    fall through to the general rotation, so the reserve never wastes budget; a
    case picked by the reserve is not picked again by the general fill.
    """
    if limit <= 0:
        return []
    reserve = min(eligible_reserve, limit)
    picked: list[CorpusRow] = []
    seen: set[str] = set()
    if reserve > 0:
        for row in _rotation_rows(conn, limit=reserve, skip_closed=skip_closed, only_eligible=True):
            picked.append(row)
            seen.add(row.case_id)
    remaining = limit - len(picked)
    if remaining > 0:
        # Over-fetch by the reserved count so dropping cases already taken by the
        # eligible reserve still leaves ``remaining`` distinct general cases.
        for row in _rotation_rows(conn, limit=remaining + len(seen), skip_closed=skip_closed):
            if row.case_id in seen:
                continue
            picked.append(row)
            seen.add(row.case_id)
            if len(picked) >= limit:
                break
    return picked


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


def _event_from_record(record: RecordRow) -> CorpusEvent:
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


def _event_update_clause(column: str) -> str:
    """The ``ON CONFLICT`` assignment for one event column, honoring its latch.

    ``resolved`` only ever latches **on**: a re-ingest carries freshly-extracted
    events with ``resolved = 0`` (extraction never observes resolution — outcome
    detection does, via :func:`set_event_resolved`), so a re-discovery or a
    quarterly seed reconcile must not reopen an event a prior outcome already
    closed. Every other column takes the incoming value. Mirrors the ``cases``
    upsert's :func:`_update_clause` for ``predict_eligible``.
    """
    if column == "resolved":
        return f"{column}=MAX(excluded.{column}, events.{column})"
    return f"{column}=excluded.{column}"


def upsert_events(conn: sqlite3.Connection, events: list[CorpusEvent]) -> int:
    """Insert or replace predictable-event definitions by ``(case_id, event_id)``.

    Idempotent, so re-discovering a docket overwrites its event rows rather than
    duplicating them — like the ``cases`` upsert, this keeps ``seed`` and ``pull``
    able to rewrite the same fact without proliferating rows. ``resolved`` is the
    one column a re-ingest cannot regress (see :func:`_event_update_clause`), so a
    re-discovery or reconcile never reopens an already-closed event.
    """
    placeholders = ", ".join("?" for _ in _EVENT_COLUMNS)
    updates = ", ".join(
        _event_update_clause(c) for c in _EVENT_COLUMNS if c not in ("case_id", "event_id")
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


def events_for_case(conn: ReadConnection, case_id: str) -> list[CorpusEvent]:
    """Predictable events defined for one case, in ``event_id`` order."""
    cur = conn.execute("SELECT * FROM events WHERE case_id = ? ORDER BY event_id", (case_id,))
    return [_event_from_record(record) for record in cur]


def iter_open_events(conn: ReadConnection, *, court: str | None = None) -> Iterator[CorpusEvent]:
    """Yield unresolved (``resolved = 0``) events in ``(case_id, event_id)`` order.

    Optionally filtered to one ``court``. The corpus-wide complement of
    :func:`events_for_case`, for read-only censuses (e.g. the predict-scope audit)
    that must scan every still-open event rather than one case's.
    """
    clauses = ["resolved = 0"]
    params: list[object] = []
    if court is not None:
        clauses.append("court = ?")
        params.append(court)
    where = " AND ".join(clauses)
    cur = conn.execute(f"SELECT * FROM events WHERE {where} ORDER BY case_id, event_id", params)
    for record in cur:
        yield _event_from_record(record)


def set_event_resolved(
    conn: sqlite3.Connection, case_id: str, event_id: str, *, resolved: bool = True
) -> None:
    """Flip a predictable event's ``resolved`` flag in the corpus.

    The corpus event row is the source of truth for whether an event is still
    open: outcome detection calls this to close an event the moment it records
    that event's ``outcome.json``, so the next ``open_events`` read no longer
    queues it for prediction. A no-op if ``(case_id, event_id)`` is not a known
    event.
    """
    with conn:
        conn.execute(
            "UPDATE events SET resolved = ? WHERE case_id = ? AND event_id = ?",
            (int(resolved), case_id, event_id),
        )


def event_count(conn: ReadConnection) -> int:
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


# --- dated point-in-time snapshots (raw facts) ---------------------------------


def upsert_snapshot(
    conn: sqlite3.Connection, case_id: str, snapshot_date: date, payload: Mapping[str, Any]
) -> None:
    """Store one pull's full-docket snapshot, keyed by ``(case_id, snapshot_date)``.

    The snapshot is the raw point-in-time docket JSON (docket + entries) that a
    normalized ``cases`` row does not fully capture — it is what ``pull`` diffs to
    detect change and what predictors/evaluators are provisioned from. Serialized
    with sorted keys so a re-store of the same facts is byte-identical. Idempotent:
    a second pull on the same day overwrites that day's snapshot rather than
    duplicating it.
    """
    with conn:
        conn.execute(
            "INSERT INTO snapshots (case_id, snapshot_date, payload) VALUES (?, ?, ?) "
            "ON CONFLICT(case_id, snapshot_date) DO UPDATE SET payload = excluded.payload",
            (case_id, snapshot_date.isoformat(), json.dumps(payload, sort_keys=True)),
        )


def latest_snapshot(conn: ReadConnection, case_id: str) -> tuple[date, dict[str, Any]] | None:
    """The most recent dated snapshot for a case — ``(date, payload)`` — or ``None``.

    Ordered by ``snapshot_date`` so the newest pull wins; ``None`` means the case
    has never been snapshotted (the onboarding signal for ``pull``).
    """
    cur = conn.execute(
        "SELECT snapshot_date, payload FROM snapshots WHERE case_id = ? "
        "ORDER BY snapshot_date DESC LIMIT 1",
        (case_id,),
    )
    record = cur.fetchone()
    if record is None:
        return None
    payload: dict[str, Any] = json.loads(record["payload"])
    return date.fromisoformat(record["snapshot_date"]), payload


def snapshot_count(conn: ReadConnection) -> int:
    """Total number of dated snapshot rows in the corpus."""
    cur = conn.execute("SELECT COUNT(*) AS n FROM snapshots")
    return int(cur.fetchone()["n"])
