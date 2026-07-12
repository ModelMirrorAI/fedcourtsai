"""The unified raw-fact corpus.

All *raw facts* — dockets, dated snapshots, judges, case metadata and tracking
state, and event definitions — live in one packed, queryable store, written
**identically** by every ingestion channel (the CourtListener REST API and the
supremecourt.gov live + historical channels) through this one ingestion seam.
The packed store is a single **SQLite**
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

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

    Written identically whichever channel a row originates from; the ingestion
    core maps every source onto this shape.
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
    date_cert_granted: date | None = Field(
        default=None,
        description="Petition-stage date certiorari was granted — the petition "
        "event's true resolution moment. Distinct from `date_decided`, which keeps "
        "termination semantics: for a granted petition the docket terminates only "
        "at the merits judgment, months later.",
    )
    date_cert_denied: date | None = Field(
        default=None,
        description="Petition-stage date certiorari was denied — the petition "
        "event's resolution moment (for a denied petition, termination and the "
        "petition-stage decision usually coincide).",
    )
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
    last_live_polled: date | None = Field(
        default=None,
        description="Tracking state: date the SCOTUS live channel (supremecourt.gov "
        "docket JSON) last polled this case; None until first polled. Drives "
        "the live poller's rotation, kept separate from `last_pulled` so the two "
        "channels' rotations never disturb each other.",
    )
    distributed_for_conference: date | None = Field(
        default=None,
        description="The SCOTUS conference this petition is currently distributed for, "
        "parsed from the live proceedings ('DISTRIBUTED for Conference of …'; the "
        "latest entry wins, so a re-distribution updates it). The watchlist "
        "prioritizes and the conference-set report groups on it. Only the live "
        "channel supplies it; other writers preserve the stored value.",
    )
    distribution_count: int | None = Field(
        default=None,
        description="How many distinct conferences this petition has been distributed "
        "for, parsed from the live proceedings (relists = count - 1, floored at 0). "
        "None means the proceedings were never live-parsed — the parse-coverage "
        "sentinel for the whole live-signal family — while 0 asserts the petition "
        "was parsed and never distributed. Only the live channel supplies it; the "
        "upsert max-latches it (proceedings are append-only, so it only grows).",
    )
    cvsg_date: date | None = Field(
        default=None,
        description="Date the Court called for the views of the Solicitor General "
        "(the 'Solicitor General is invited to file' proceedings entry), parsed by "
        "the live channel. None asserts 'no CVSG observed' only where "
        "`distribution_count` is not None (the proceedings were parsed at all).",
    )
    originating_court_name: str | None = Field(
        default=None,
        description="The raw lower-court name the live docket JSON carries "
        "(`LowerCourt`), kept verbatim so unmapped tribunals — state courts, "
        "military courts — stay identifiable where `originating_court` (the "
        "tracked-court id linkage) is None. Only the live channel supplies it.",
    )
    sample_weight: int | None = Field(
        default=None,
        description="Inverse inclusion probability of this row under the corpus's "
        "construction: 1 for every row its channel includes with certainty, "
        "`denial_sample_every` for a denial the historical walker kept by its "
        "systematic serial sample — so a weighted aggregate can multiply by it "
        "and count sampled denials at full strength. None means no channel "
        "asserted a weight: permanent on rows the live channel never wrote, "
        "pre-capture within the live slice (backfilled by rule).",
    )
    predict_eligible: bool = Field(
        default=False,
        description="Derived convenience mirror of the prediction scope "
        "(court == 'scotus'). Every scope seam reads the court predicate "
        "directly; ingestion writes this column by the same rule and the scope "
        "reconcile normalizes stale values, so it is queryable but never the "
        "source of truth.",
    )
    predict_excluded: bool = Field(
        default=False,
        description="Out-of-scope latch: True when the seed reconcile has "
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
    has_opinion: bool = Field(
        default=False,
        description="Whether the case has a linked published opinion — the "
        "presence signal the scope classifiers key on (a merits disposition that "
        "lives only in the opinion text). Derived from `opinion_text` at "
        "construction, but stored as its own column so it survives the corpus "
        "split: under the split, the heavy `opinion_text` body moves to the "
        "content store and the corpus keeps only this bit.",
    )
    # embedding[] — a later upgrade for semantic retrieval; not stored yet.

    @model_validator(mode="after")
    def _derive_has_opinion(self) -> CorpusRow:
        # `has_opinion` reflects "an opinion body is present OR the stored flag
        # already says so." Monotonic OR, so it is consistent in every case: a
        # fresh ingest with `opinion_text` sets it True; a split-mode read (body
        # stripped to the store, flag column = 1) keeps it True; a plain read
        # round-trips unchanged. Never regresses a True to False.
        if self.opinion_text and not self.has_opinion:
            self.has_opinion = True
        return self


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


class CaseDocument(BaseModel):
    """One filed document's extracted text, stored as a raw fact.

    Fetched pipeline-side by the live poller (never agent-side) and keyed
    ``(case_id, kind)`` — the latest fetch of a kind wins, so a corrected or
    re-filed document supersedes. Text lives here in the DVC-backed corpus,
    never the git ledger (the access-gated, no-republication posture);
    provisioning materializes it into a cell's gitignored ``record/`` path.
    """

    model_config = ConfigDict(extra="forbid")

    case_id: str
    kind: str = Field(description="petition | brief-in-opposition | questions-presented | …")
    url: str = Field(description="The supremecourt.gov DocumentUrl fetched (or the source doc's)")
    entry_date: str | None = Field(
        default=None, description="The proceedings entry date the link rode on, verbatim"
    )
    fetched_at: date
    pages: int = Field(default=0, description="PDF page count (0 for a derived section)")
    truncated: bool = Field(
        default=False, description="Extracted text hit the storage cap and was cut"
    )
    text: str = Field(description="Extracted text (capped at ingest; may be empty for a scan)")


class DiscoveryWatermark(BaseModel):
    """Per-court forward-discovery cursor: the newest ``date_filed`` seen so far.

    Tracking state (not a docket fact): ``pull``
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
    originating_docket_number    TEXT,
    date_cert_granted   TEXT,
    date_cert_denied    TEXT,
    last_live_polled    TEXT,
    distributed_for_conference TEXT,
    distribution_count  INTEGER,
    cvsg_date           TEXT,
    originating_court_name TEXT,
    sample_weight       INTEGER,
    -- Presence bit for a linked published opinion (see CorpusRow.has_opinion):
    -- kept in the index so the scope classifiers still work when the corpus
    -- split moves the `opinion_text` body out to the content store.
    has_opinion         INTEGER NOT NULL DEFAULT 0
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

-- Per-Term live-discovery cursor for the SCOTUS live channel: the highest
-- docket serial confirmed served, per numbering stream. Tracking state,
-- mirroring the watermarks above: a sequential prober resumes from the cursor
-- and a 404 past it marks the Term's frontier. Two walkers share the table
-- under disjoint stream names: the forward poller's frontier discovery uses
-- "paid" / "ifp" (paid petitions from 1, IFP from 5001), and the historical
-- Term walker (pipeline.historical) uses "historical-paid" / "historical-ifp"
-- over the same serial spaces — so the walker can walk a Term the poller is
-- also tracking without either rewinding the other.
CREATE TABLE IF NOT EXISTS live_discovery_cursors (
    term         INTEGER NOT NULL,
    stream       TEXT NOT NULL,
    last_serial  INTEGER NOT NULL,
    -- The serial the stream's frontier (consecutive 404s) was last observed at,
    -- or NULL if no walk has reached it. `frontier_serial = last_serial` means
    -- the walk is complete *at the current cursor*: a cursor that later
    -- advances past the stamp degrades the stream to partial until a fresh
    -- miss-exit re-confirms the end. The per-Term walk-complete signal for
    -- downstream census readers — no clock involved.
    frontier_serial INTEGER,
    PRIMARY KEY (term, stream)
);

-- Per-case filed-document text: a raw fact fetched pipeline-side by the
-- live poller on the distribution transition. Keyed (case_id, kind) — the
-- latest fetch of a kind wins. Text stays in the DVC-backed corpus
-- (access-gated), never the git ledger; provisioning materializes it per cell.
CREATE TABLE IF NOT EXISTS documents (
    case_id     TEXT NOT NULL,
    kind        TEXT NOT NULL,
    url         TEXT NOT NULL,
    entry_date  TEXT,
    fetched_at  TEXT NOT NULL,
    pages       INTEGER NOT NULL DEFAULT 0,
    truncated   INTEGER NOT NULL DEFAULT 0,
    text        TEXT NOT NULL,
    PRIMARY KEY (case_id, kind)
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
    "date_cert_granted": "TEXT",
    "date_cert_denied": "TEXT",
    "last_live_polled": "TEXT",
    "distributed_for_conference": "TEXT",
    "distribution_count": "INTEGER",
    "cvsg_date": "TEXT",
    "originating_court_name": "TEXT",
    "sample_weight": "INTEGER",
    "has_opinion": "INTEGER NOT NULL DEFAULT 0",
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


def _migrate_live_cursors(conn: sqlite3.Connection) -> None:
    """Back-fill `live_discovery_cursors` columns added after table creation.

    The cursors table's counterpart of :func:`_migrate_cases` — before
    ``frontier_serial`` the table needed no migration path. Nullable, no
    DEFAULT needed; idempotent on a current-schema table.
    """
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(live_discovery_cursors)")}
    if "frontier_serial" not in existing:
        conn.execute("ALTER TABLE live_discovery_cursors ADD COLUMN frontier_serial INTEGER")


_DN_LABEL = re.compile(r"^NOS?\.?\s+")  # a leading "No." / "Nos." / "No " docket-number label
_DN_WHITESPACE = re.compile(r"\s+")
# Typographic dashes (en U+2013 / em U+2014) that stand in for a plain hyphen in a
# docket number, folded so a dash-variant reads as the modern Term-year form.
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
        _migrate_live_cursors(conn)
        yield conn
    finally:
        conn.close()


CorpusBackend = Literal["local", "ranged", "casestore"]


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

    The ``casestore`` backend has no query surface (it serves per-case
    *provisioning* reads from content objects, not SQL), so it is rejected here — a
    command that only reads via this seam cannot serve it and must not silently fall
    back to ``local``.
    """
    effective = resolve_backend(backend)
    if effective == "casestore":
        raise ValueError(
            "the casestore backend has no queryable connection; it serves only "
            "per-case provisioning reads (see fedcourtsai.provision)"
        )
    if effective == "ranged":
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
        "date_cert_granted": (row.date_cert_granted.isoformat() if row.date_cert_granted else None),
        "date_cert_denied": row.date_cert_denied.isoformat() if row.date_cert_denied else None,
        "last_live_polled": row.last_live_polled.isoformat() if row.last_live_polled else None,
        "distributed_for_conference": (
            row.distributed_for_conference.isoformat() if row.distributed_for_conference else None
        ),
        "distribution_count": row.distribution_count,
        "cvsg_date": row.cvsg_date.isoformat() if row.cvsg_date else None,
        "originating_court_name": row.originating_court_name,
        "sample_weight": row.sample_weight,
        "has_opinion": int(row.has_opinion),
    }


def _optional_date(record: RecordRow, column: str) -> date | None:
    """Read a date column that a remote blob packed under an older schema lacks.

    Local reads always see every column (``connect`` migrates on open), but the
    ranged backend serves the remote blob as-is, and its ``Row`` raises for a
    column the blob predates — treat that as unset rather than failing the row.
    """
    try:
        raw = record[column]
    except (KeyError, IndexError):
        return None
    return date.fromisoformat(raw) if raw else None


def _optional_int(record: RecordRow, column: str) -> int | None:
    """Read an integer column an older remote blob lacks (see ``_optional_date``)."""
    try:
        raw = record[column]
    except (KeyError, IndexError):
        return None
    return int(raw) if raw is not None else None


def _optional_str(record: RecordRow, column: str) -> str | None:
    """Read a text column an older remote blob lacks (see ``_optional_date``)."""
    try:
        raw = record[column]
    except (KeyError, IndexError):
        return None
    return raw if raw else None


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
        date_cert_granted=_optional_date(record, "date_cert_granted"),
        date_cert_denied=_optional_date(record, "date_cert_denied"),
        last_live_polled=_optional_date(record, "last_live_polled"),
        distributed_for_conference=_optional_date(record, "distributed_for_conference"),
        distribution_count=_optional_int(record, "distribution_count"),
        cvsg_date=_optional_date(record, "cvsg_date"),
        originating_court_name=_optional_str(record, "originating_court_name"),
        sample_weight=_optional_int(record, "sample_weight"),
        has_opinion=bool(_optional_int(record, "has_opinion")),
    )


def _update_clause(column: str) -> str:
    """The ``ON CONFLICT`` assignment for one column, honoring its latch (if any).

    Most columns take the incoming value (``excluded``). Four latch families are
    special: channel-supplied facts (``last_pulled``, the live-parsed signals)
    only ever fill in, so a writer that does not carry the fact keeps what
    another channel stamped; ``distribution_count`` is a max-latch (proceedings
    are append-only, so the count only ever grows); ``sample_weight`` is a
    min-latch (an inclusion probability is only ever learned upward, toward
    weight 1); and ``predict_excluded`` is owned by the scope reconcile (not an
    ingestion fact), so an upsert keeps the stored value rather than resetting
    it to the model default. ``predict_eligible`` deliberately takes the
    incoming value: it is a derived mirror of the court predicate, so a
    re-ingest self-heals a stale value rather than latching it.
    """
    if column in (
        "last_pulled",
        "last_live_polled",
        "distributed_for_conference",
        "cvsg_date",
        "originating_court_name",
    ):
        # Channel-supplied values only ever fill in: a writer that does not carry
        # the fact (a CourtListener enrichment without the live channel's
        # conference parse) must not wipe what another channel stamped. Safe for
        # exactly the columns whose degraded parse yields NULL.
        return f"{column}=COALESCE(excluded.{column}, cases.{column})"
    if column == "distribution_count":
        # A fill-in latch is not enough here: a degraded live parse (a payload
        # served with its proceedings missing) yields a confident 0 — not NULL —
        # and 0 asserts "parsed, never distributed", so COALESCE would let it
        # wipe a stored count. Proceedings are append-only upstream: the count
        # only ever legitimately grows, so the max-latch takes every real
        # advance and rejects the regression.
        return (
            f"{column}=MAX("
            f"COALESCE(excluded.{column}, cases.{column}), "
            f"COALESCE(cases.{column}, excluded.{column}))"
        )
    if column == "sample_weight":
        # An inclusion probability can only be learned upward (toward certainty):
        # once any channel knows the row is included with P=1 (weight 1), a later
        # walker re-serve of its sampled serial must not regress it to N — and a
        # writer with no weight to assert (NULL) preserves the stored value.
        return (
            f"{column}=MIN("
            f"COALESCE(excluded.{column}, cases.{column}), "
            f"COALESCE(cases.{column}, excluded.{column}))"
        )
    if column == "predict_excluded":
        # The scope reconcile owns this flag (it is not an ingestion fact and is not
        # monotonic), so a re-ingest must never clobber it — keep the stored value.
        return f"{column}=cases.{column}"
    return f"{column}=excluded.{column}"


# --- dual-write sink (dependency-inverted) ------------------------------------
#
# The per-case content store (fedcourtsai.casestore) mirrors each mutated case for
# the corpus split. To keep this storage module free of the S3 mirror — and free of
# an import cycle — corpus does NOT import casestore; instead casestore registers a
# sink here when it is imported (wired in fedcourtsai/__init__). No sink registered
# → dual-write off (the default) → every hook below is a pure no-op.


class MirrorSink(Protocol):
    """The dual-write callbacks casestore registers via :func:`set_mirror_sink`."""

    def mirror_cases(self, rows: Sequence[CorpusRow]) -> None: ...

    def mirror_snapshot(
        self, case_id: str, snapshot_date: date, payload: Mapping[str, Any]
    ) -> None: ...

    def mirror_documents_for_cases(self, conn: ReadConnection, case_ids: Iterable[str]) -> None: ...

    def mirror_documents(self, documents: Sequence[CaseDocument]) -> None: ...

    def mirror_events_for_cases(self, conn: ReadConnection, case_ids: Iterable[str]) -> None: ...


_MIRROR: dict[str, MirrorSink] = {}


def set_mirror_sink(sink: MirrorSink | None) -> None:
    """Register (``None`` clears) the dual-write sink; called by casestore on import."""
    if sink is None:
        _MIRROR.pop("sink", None)
    else:
        _MIRROR["sink"] = sink


def _mirror_sink() -> MirrorSink | None:
    return _MIRROR.get("sink")


# --- payload read source (dependency-inverted, symmetric to the mirror sink) --
#
# Under the corpus split the bulk payloads (snapshots, documents) live only in the
# content store, not the blob — so the payload *reads* must come from the store
# too: change detection and document dedup in the writer, and provisioning /
# back-test replay in the readers. casestore registers a read source here with the
# same inversion as the mirror sink (corpus never imports casestore). The snapshot
# / document read functions consult it ONLY when `corpus_split` is on, so with the
# mode off every read is the byte-for-byte SQLite path it is today.


class PayloadReadSource(Protocol):
    """Casestore-backed payload reads, consulted under the corpus-split mode."""

    def latest_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None: ...

    def latest_live_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None: ...

    def documents_for_case(self, case_id: str) -> list[CaseDocument]: ...


_READ_SOURCE: dict[str, PayloadReadSource] = {}


def set_payload_read_source(source: PayloadReadSource | None) -> None:
    """Register (``None`` clears) the casestore payload read source (called by casestore)."""
    if source is None:
        _READ_SOURCE.pop("source", None)
    else:
        _READ_SOURCE["source"] = source


def _payload_read_source() -> PayloadReadSource | None:
    """The read source, or ``None`` unless the corpus-split mode is on AND one is
    registered — so the default path never leaves SQLite."""
    if not get_settings().corpus_split:
        return None
    return _READ_SOURCE.get("source")


def _split_mode() -> bool:
    """Whether the corpus-split write mode is on: the payload columns/tables are
    left empty (the content store is the system of record for them) so the blob
    stays a small metadata index. Off by default — the writer is unchanged."""
    return get_settings().corpus_split


def upsert_rows(conn: sqlite3.Connection, rows: list[CorpusRow]) -> int:
    """Insert or replace rows by ``case_id``; returns the number written.

    Idempotent: re-ingesting the same case overwrites its row, so every
    channel can write a case without producing duplicates.
    """
    placeholders = ", ".join("?" for _ in _COLUMNS)
    updates = ", ".join(_update_clause(c) for c in _COLUMNS if c != "case_id")
    sql = (
        f"INSERT INTO cases ({', '.join(_COLUMNS)}) VALUES ({placeholders}) "
        f"ON CONFLICT(case_id) DO UPDATE SET {updates}"
    )
    split = _split_mode()

    def _stored(row: CorpusRow) -> dict[str, object]:
        record = _to_record(row)
        if split:
            # The opinion body moves to the content store (still mirrored below via
            # the full `rows`); the index keeps only the `has_opinion` bit.
            record["opinion_text"] = None
        return record

    with conn:
        conn.executemany(sql, [tuple(_stored(r)[c] for c in _COLUMNS) for r in rows])
    if (sink := _mirror_sink()) is not None:
        sink.mirror_cases(rows)
    return len(rows)


def normalize_predict_eligible(conn: sqlite3.Connection) -> int:
    """Converge the derived scope columns to the scope predicate.

    ``predict_eligible`` is a convenience mirror of ``court == 'scotus'`` (the
    prediction scope); every scope seam reads the court predicate directly, so
    correctness never depends on this. A non-SCOTUS row also sheds any stale
    ``predict_excluded`` latch — outside the reconcile's universe nothing would
    ever release it, and under ``scope=all`` a stale latch silently empties the
    case's open events. Run by the scope reconcile so rows written under an
    earlier, broader rule read consistently. Idempotent; returns rows changed.
    """
    with conn:
        changed = conn.execute(
            "UPDATE cases SET predict_eligible = (court = 'scotus') "
            "WHERE predict_eligible != (court = 'scotus')"
        ).rowcount
        changed += conn.execute(
            "UPDATE cases SET predict_excluded = 0 WHERE court != 'scotus' AND predict_excluded = 1"
        ).rowcount
        return changed


def scotus_case_id_by_docket_number(conn: sqlite3.Connection, raw: str | None) -> str | None:
    """The existing SCOTUS row matching a Term-form docket number, or ``None``.

    The identity-reconciliation join for the live channel: the corpus
    keys on docket ids, which a supremecourt.gov record does not carry, so both
    channels reconcile on the normalized docket-number string (the same
    ``norm_dn`` rule the lower-court link join uses) before minting a row — a live
    poll enriches the CourtListener-keyed row when one exists, and CourtListener
    discovery enriches the live-keyed row when the live channel saw the petition
    first. Should two rows ever match (a pre-guard historical duplicate), the
    lowest docket id — the CourtListener-keyed row — wins deterministically.
    """
    norm = normalize_docket_number(raw)
    if norm is None:
        return None
    cur = conn.execute(
        "SELECT case_id FROM cases WHERE court = 'scotus' AND norm_dn(docket_number) = ?",
        (norm,),
    )
    case_ids: list[str] = [str(record["case_id"]) for record in cur]
    if not case_ids:
        return None
    return min(case_ids, key=lambda cid: int(cid.rsplit("/", 1)[-1]))


# The Judiciary Act of 1925 (the "Judges' Bill") made the Supreme Court's
# jurisdiction largely discretionary; matters filed before it were appeals and
# writs of error heard *as of right* and decided on the merits. A pre-1925 docket
# number is a bare sequential integer ("801"); the modern discretionary-cert era
# carries a Term-year prefix ("01-7700", "22-451", "22A123").
_DISCRETIONARY_ERA_YEAR = 1925


def is_historical_mandatory(row: CorpusRow) -> bool:
    """Whether a SCOTUS row is a pre-1925 mandatory-jurisdiction matter.

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
    Court concept, and the scope gate only ever weighs SCOTUS dockets.

    The bare-number test is applied to the *normalized* docket: a great
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

# Provisional staleness cutoff (the scope reconcile refines it against the corpus). A SCOTUS
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


def is_live_slice(row: CorpusRow) -> bool:
    """Whether a row belongs to the live/historical provenance slice.

    The slice the statpack's predictor-facing base rates aggregate over: rows
    the supremecourt.gov channel (forward poller or historical Term walker) has
    written, whose dispositions and dates come from parsed proceedings text
    rather than the frozen bulk import. ``last_live_polled`` is the marker —
    every live-channel write stamps it and the upsert COALESCE-latch means a
    later REST enrichment can never wipe it — so membership is monotonic.
    SQL pushdown uses :data:`LIVE_SLICE_SQL`.
    """
    return row.last_live_polled is not None


# The SQL form of `is_live_slice`, for pushed-down filtering.
LIVE_SLICE_SQL = "last_live_polled IS NOT NULL"


class ResolutionDatedRow(Protocol):
    """The fields resolution timing reads — satisfied by both the storage row
    (:class:`CorpusRow`) and the ingestion row, which carry the same date facts."""

    @property
    def court(self) -> str: ...
    @property
    def date_decided(self) -> date | None: ...
    @property
    def date_cert_granted(self) -> date | None: ...
    @property
    def date_cert_denied(self) -> date | None: ...


def resolution_date(row: ResolutionDatedRow) -> date | None:
    """When the matter this row predicts actually resolved, or ``None``.

    For a SCOTUS docket the predicted event is the cert petition, whose true
    resolution moment is the petition-stage decision: the cert grant/denial date
    when the row carries one, falling back to ``date_decided``. (For a granted
    petition ``date_decided`` is the *termination* of the whole case — the merits
    judgment, months after the grant — so the cert date must win.) Everywhere
    else the docket-level decision date is the resolution.
    """
    if row.court == "scotus":
        return row.date_cert_granted or row.date_cert_denied or row.date_decided
    return row.date_decided


def case_year(row: CorpusRow) -> int | None:
    """The year a case is anchored to, from its best temporal signal, or ``None``.

    A SCOTUS row's parsed October-Term year, then ``date_filed``, then the
    :func:`resolution_date` (petition-stage cert date before the docket's
    ``date_decided``). Most corpus rows carry no full dates, so this year is the
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
    resolved = resolution_date(row)
    if resolved is not None:
        return resolved.year
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
    """Whether a SCOTUS row is an old petition the corpus can never resolve.

    Modern-format SCOTUS petitions from old Terms (e.g. ``93-7515`` -> OT1993,
    ``01-7700`` -> OT2001) whose snapshots are bare stubs — empty docket entries,
    null cert dates — sit perpetually open because deterministic outcome detection
    has nothing to resolve them from, so they are re-predicted every run decades
    after they actually resolved (the bulk of the feedback-issue noise).
    Distinct from :func:`is_historical_mandatory`: those are *pre-1925* mandatory-
    jurisdiction matters with bare sequential numbers; these are post-1925
    discretionary-cert dockets that are simply too old to still be pending.

    **Provisional and deliberately conservative — the scope reconcile refines it.** Caught
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
    """Whether a still-open SCOTUS row's disposition lives only in an opinion.

    Some historical ``evt-petition-disposition`` cases (observed on the
    bulk-era import) carry a **linked published opinion** (a reporter
    citation / non-zero ``citation_count`` / ``opinion_text``) but **no machine-readable
    disposition** on either the docket or the cluster and no docket entries. The outcome
    exists only in the opinion *text* — recoverable by parsing it, not by a structured
    re-ingest — and for a cert event it is a **merits** label (affirmed / reversed), not
    a cert grant/deny, so the modern discretionary-cert model cannot score it. Predict
    scope therefore excludes it.

    Complements the two siblings for the cases their docket-number tests cannot
    parse: :func:`is_stale_unresolvable` needs a parseable ``YY-NNNN`` Term year,
    and :func:`is_historical_mandatory` needs a bare sequential number or a pre-1925
    ``date_filed`` (null on these rows) — so an old, oddly-formatted docket with a
    published opinion falls through both and lands here instead.

    Safe against a live petition **by construction**: a pending cert petition has no
    published opinion yet (no citation, no ``has_opinion``), so it can never match.
    SCOTUS-only, and only while still open (no ``disposition`` and no ``date_decided``);
    a case that later gains a real disposition is released by the two-directional scope
    reconcile. The published-opinion signal mirrors ``validate._recoverable_signal``.

    Reads the ``has_opinion`` presence bit rather than ``opinion_text`` so it holds
    under the corpus split, where the opinion body moves to the content store.
    """
    if row.court != "scotus":
        return False
    if row.disposition is not None or row.date_decided is not None:
        return False
    return bool(row.citations or row.citation_count or row.has_opinion)


# SCOTUS application ("22A123", older "A-9999"), original-jurisdiction ("22O141"),
# and miscellaneous/motions ("22M75", "03M77", hyphenated "M-62") docket numbers —
# the term letter (A / O / M) marks a form that is not the modern
# discretionary-cert petition. Each form also carries a **trailing-letter**
# historical spelling — a bare number followed by the letter ("515 M", "133M",
# "979 A") — the pre-unification way the separate dockets were written. Each form
# tolerates a trailing period on the historical spelling ("22A99.") and a single
# trailing parenthetical companion — a related docket ("A-706 (98-1368)") or a
# Term annotation ("A-241 (O. T. 1995)") — which would otherwise defeat the end
# anchor; the letter is what a cert docket's ``YY-NNNN`` never carries (and the
# trailing-letter alternative requires no hyphen, so a hyphenated cert number
# can never reach it). Typographic dashes are already folded to a hyphen by
# :func:`normalize_docket_number` before these regexes see the string.
_SCOTUS_FORM_SUFFIX = r"(?:\([^()]+\))?\.?$"
_SCOTUS_APPLICATION_RE = re.compile(r"^(?:\d{2}A\d+|A-?\d+|\d+A)" + _SCOTUS_FORM_SUFFIX)
_SCOTUS_ORIGINAL_RE = re.compile(r"^(?:\d{2}O\d+|\d+O)" + _SCOTUS_FORM_SUFFIX)
_SCOTUS_MISCELLANEOUS_RE = re.compile(r"^(?:\d{2}M\d+|M-?\d+|\d+M)" + _SCOTUS_FORM_SUFFIX)
# SCOTUS disbarment ("D-2464", Term-prefixed "16D2924" / "16D02977") — the
# attorney-discipline docket, same tolerances as the sibling letter forms.
_SCOTUS_DISBARMENT_RE = re.compile(r"^(?:\d{2}D\d+|D-?\d+|\d+D)" + _SCOTUS_FORM_SUFFIX)
# The spelled-out original-jurisdiction ("No. 155, Orig." / "155, Original.") and
# miscellaneous ("No. 33, Misc." — the pre-1971 separate docket, merged into the
# unified numbering at OT1970) markers — the text-form counterparts of the numeric
# letter forms, tells a cert docket's `YY-NNNN` never carries.
_SCOTUS_ORIGINAL_TEXT_RE = re.compile(r"ORIG")
_SCOTUS_MISC_TEXT_RE = re.compile(r"MISC")


def is_non_cert_scotus_form(row: CorpusRow) -> bool:
    """Whether a SCOTUS docket is an application or original-jurisdiction matter.

    A stay / emergency **application** (``22A123``, older ``A-9999``, with or
    without a parenthetical companion like ``A-706 (98-1368)``), an
    **original-jurisdiction** case (``22O141`` numeric, or its spelled-out
    ``No. 155, Orig.`` / ``Original`` form — e.g. a State-v-State dispute), and a
    **miscellaneous** docket (``22M75`` / ``03M77``, hyphenated ``M-62``,
    trailing-letter ``515 M`` — the motions docket, e.g. leave to file out of
    time — or the pre-1971 ``No. 33, Misc.`` separate docket, merged into the
    unified numbering at OT1970) are not the
    discretionary-cert form the ``evt-petition-disposition`` model targets: an
    application's disposition is a stay grant/deny, an original case's a merits
    judgment, and a motions docket's a procedural leave — none the cert
    grant/deny the model calibrates on — while the pre-1971 miscellaneous docket
    is decades-stale by construction. So predict scope excludes them (as it does
    the pre-1925 mandatory-jurisdiction regime), keyed on the term letter
    (``A`` / ``O`` / ``M``) or the ``Orig`` / ``Misc`` marker that a cert
    docket's ``YY-NNNN`` never carries. SCOTUS-only.

    Conservative — it matches on format alone, so it never catches a modern cert
    petition (which carries a hyphen, no letter and no ``Orig``/``Misc`` marker).
    If application *stays* are later modeled as their own motion events,
    refine this to spare those rather than the whole case; today an
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


def is_disbarment_docket(row: CorpusRow) -> bool:
    """Whether a still-open SCOTUS docket is a disbarment (attorney-discipline) matter.

    The Court's disbarment docket — ``No. D-2464``, or the Term-prefixed spelling
    ``16D2924`` / ``16D02977`` (October-Term year + the same ``D`` sequence, whose
    numbers continue the plain ``D-####`` series) — disciplines members of the
    Court's bar, typically reciprocally after state-court discipline. Its
    disposition is a disbarment order, not the cert grant/deny the
    ``evt-petition-disposition`` model calibrates on, so predict scope excludes
    it, keyed on the ``D`` form letter a cert docket's ``YY-NNNN`` never carries
    (same period / parenthetical / dash tolerances as the sibling letter forms).

    Same guards as the siblings: SCOTUS-only, and only while the row is still
    open (no ``disposition`` and no ``date_decided``) — a resolved row carries
    ground truth and is never this rule's business, and the two-directional
    scope reconcile releases a latched row that later resolves. Format-only
    otherwise, so it can never catch a live cert petition.
    """
    if row.court != "scotus":
        return False
    if row.disposition is not None or row.date_decided is not None:
        return False
    dn = normalize_docket_number(row.docket_number) or ""
    return bool(_SCOTUS_DISBARMENT_RE.match(dn))


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
    """Whether a consolidated SCOTUS docket's members all classify out of scope.

    A consolidated row carries several docket numbers in one string, so no
    single-number predicate can read it. This rule splits the members
    (:func:`consolidated_docket_members`) and runs **each member through the
    existing single-docket predicates** on a copy of the row: the row leaves
    predict scope only when *every* member agrees — all bare-sequential numbers
    (the pre-1925 mandatory-jurisdiction regime), all stale Term years
    on a still-open row, or all non-cert letter forms
    (:func:`is_non_cert_scotus_form` — e.g. the consolidated miscellaneous
    pair ``No. 99M81; No. 99M82`` or application pair ``A-363; A-366``). Any
    disagreement, or any member the predicates cannot read, keeps the row in
    scope and visible in the audit's unclassified bucket — conservative like
    every sibling: it can under-catch, never drop a live consolidated petition
    (whose members parse to recent Terms and match no branch). SCOTUS-only.
    """
    if row.court != "scotus":
        return False
    members = consolidated_docket_members(row.docket_number)
    if members is None:
        return False
    member_rows = [row.model_copy(update={"docket_number": member}) for member in members]
    return (
        all(is_historical_mandatory(member) for member in member_rows)
        or all(is_stale_unresolvable(member) for member in member_rows)
        or all(is_non_cert_scotus_form(member) for member in member_rows)
    )


def is_date_inconsistent(row: CorpusRow) -> bool:
    """Whether a case's filing/decision dates are internally inconsistent.

    ``date_decided`` before ``date_filed`` — a case that looks decided before it was
    filed. A faithful but nonsensical CourtListener ordering the validation monitor
    tracks *without* rewriting; such a case cannot yield a meaningful
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
    :func:`is_bare_opinion_import`; alone it is *not* an exclusion
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
    return not (row.citations or row.citation_count or row.has_opinion)


def snapshot_links_opinion_cluster(payload: Mapping[str, Any]) -> bool:
    """Whether a docket snapshot links at least one opinion cluster.

    CourtListener dockets carry a ``clusters`` list of opinion-cluster URLs; a
    non-empty list means a published opinion exists for the docket — the decided
    signal a bare bulk-import row itself does not carry.
    """
    return bool(payload.get("clusters"))


def is_bare_opinion_import(row: CorpusRow, snapshot: Mapping[str, Any] | None) -> bool:
    """Whether a row is a bare bulk-import docket whose snapshot links an opinion.

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


BARE_OPINION_IMPORT_REASON = "bare bulk-import row whose snapshot links a published opinion cluster"


# Each (predicate, reason) the predict-scope gate excludes a case on from the row
# alone — shared by every enforcement seam via :func:`out_of_scope_reason` /
# :func:`out_of_scope_reason_full`, so an exclusion that lands here is enforced at
# every point. Snapshot-aware exclusions (the bare opinion-import rule) cannot live
# in this row-only list; they are applied by :func:`out_of_scope_reason_full`.
OUT_OF_SCOPE_RULES: list[tuple[Callable[[CorpusRow], bool], str]] = [
    (is_historical_mandatory, "pre-1925 mandatory-jurisdiction matter"),
    (
        is_stale_unresolvable,
        "stale unresolvable old SCOTUS petition (pre-2015 Term, still open)",
    ),
    (
        is_published_opinion_unresolvable,
        "published opinion but no machine-readable cert disposition",
    ),
    (
        is_non_cert_scotus_form,
        "SCOTUS application / original-jurisdiction docket — not discretionary cert",
    ),
    (
        is_disbarment_docket,
        "SCOTUS disbarment docket — attorney discipline, not discretionary cert",
    ),
    (
        is_consolidated_out_of_scope,
        "consolidated docket whose members all classify out of scope",
    ),
    (is_date_inconsistent, "internally inconsistent dates — decided before filed"),
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
) -> Iterator[CorpusRow]:
    """Yield rows in ``case_id`` order, optionally filtered by court / disposition.

    The filters cover the common retrieval and back-test selections; richer
    querying (by judge, topic, citation, or semantic similarity) is layered on
    top of this same store. ``resolved`` keeps only rows carrying (``True``) or
    lacking (``False``) a realized disposition — pushed into SQL so a consumer of
    the small resolved slice never pays a full-corpus scan.
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
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    cur = conn.execute(f"SELECT * FROM cases{where} ORDER BY case_id", params)
    for record in cur:
        yield _from_record(record)


def set_predict_excluded(conn: sqlite3.Connection, case_id: str, excluded: bool) -> None:
    """Set a case's out-of-scope latch. The scope reconcile's sole writer.

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

    Keys on :func:`resolution_date` — the petition-stage cert date on SCOTUS
    dockets, the docket decision date elsewhere — so a granted petition ranks by
    when cert was granted, not by the merits termination months later. Undated
    rows sort after dated ones; among dated rows the negated ordinal makes the
    most recent decision compare smallest (so it leads in an ascending sort).
    """
    resolved = resolution_date(row)
    if resolved is not None:
        return (0, -resolved.toordinal())
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
    only_scotus: bool = False,
) -> list[CorpusRow]:
    """Stalest-first active cases: never-pulled first, then oldest ``last_pulled``.

    The shared query behind :func:`rotation_for_pull`. ``skip_closed`` drops cases
    carrying a realized ``disposition`` / ``date_decided`` (their outcome is known);
    ``only_scotus`` further restricts to SCOTUS dockets (the prediction scope).
    ``case_id`` breaks ties so the order is deterministic.
    """
    if limit <= 0:
        return []
    clauses: list[str] = []
    if skip_closed:
        clauses.append("disposition IS NULL AND date_decided IS NULL")
    if only_scotus:
        clauses.append("court = 'scotus'")
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
    stalest **SCOTUS dockets** (the prediction scope), filled
    first; the remainder fall to the normal stalest-first rotation over the whole
    active set. This keeps the in-scope pool rotating fast enough to
    catch new docket activity before a case resolves, instead of waiting its turn
    behind the much larger active set. Reserve slots the SCOTUS pool cannot fill
    fall through to the general rotation, so the reserve never wastes budget; a
    case picked by the reserve is not picked again by the general fill.
    """
    if limit <= 0:
        return []
    reserve = min(eligible_reserve, limit)
    picked: list[CorpusRow] = []
    seen: set[str] = set()
    if reserve > 0:
        for row in _rotation_rows(conn, limit=reserve, skip_closed=skip_closed, only_scotus=True):
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


# SQL October-Term-year expression over the modern Term-prefixed docket form,
# with the same century pivot as `scotus_term_year` (>= 30 -> 19xx). Requires
# the GLOB prefilter so the leading two characters are digits; candidates are
# re-verified in Python with `is_modern_cert`.
_TERM_YEAR_SQL = (
    "CASE WHEN CAST(substr(docket_number, 1, 2) AS INTEGER) >= 30 "
    "THEN 1900 + CAST(substr(docket_number, 1, 2) AS INTEGER) "
    "ELSE 2000 + CAST(substr(docket_number, 1, 2) AS INTEGER) END"
)


def live_rotation(
    conn: sqlite3.Connection, *, limit: int, term_floor_year: int = 2017
) -> list[CorpusRow]:
    """The next ``limit`` pending petitions the live poller should refresh.

    The SCOTUS live channel's counterpart of :func:`rotation_for_pull`: pending
    modern-cert petitions (no disposition, no termination, an open event) from
    ``term_floor_year`` forward — the floor the reachability probe established
    (docs/live-sources-probe.md). **Distributed petitions lead** (nearest
    conference first — they are days from resolution, the opposite of
    stalest-first; a past conference date sorts first of all, since that
    petition is overdue for its order-list result), then recent Terms
    first, then never-polled before stale, then ``case_id`` for determinism.
    Rotates on ``last_live_polled``, never ``last_pulled``, so the CourtListener
    enrichment rotation is undisturbed.
    """
    if limit <= 0:
        return []
    sql = (
        "SELECT * FROM cases WHERE court = 'scotus' "
        "AND disposition IS NULL AND date_decided IS NULL "
        "AND docket_number GLOB '[0-9][0-9]-*' "
        f"AND {_TERM_YEAR_SQL} >= ? "
        "AND EXISTS (SELECT 1 FROM events "
        "            WHERE events.case_id = cases.case_id AND events.resolved = 0) "
        "ORDER BY distributed_for_conference IS NULL, distributed_for_conference ASC, "
        f"{_TERM_YEAR_SQL} DESC, last_live_polled IS NOT NULL, "
        "last_live_polled ASC, case_id ASC LIMIT ?"
    )
    # Over-fetch to cover candidates the Python re-verification drops (labeled
    # docket-number spellings the raw GLOB admits but `is_modern_cert` rejects).
    cur = conn.execute(sql, (term_floor_year, limit * 2))
    picked = [row for record in cur if is_modern_cert(row := _from_record(record))]
    return picked[:limit]


def conference_watchlist(conn: ReadConnection, *, term_floor_year: int = 2017) -> list[CorpusRow]:
    """Every pending petition distributed for a conference, nearest date first.

    The live cert watchlist read: pending modern-cert petitions whose
    proceedings carry a parsed ``distributed_for_conference``, ordered by that
    date then ``case_id``. The pending-before-conference set — the September
    framing's long-conference set is a date-slice of it — exposed via the
    ``conference-set`` CLI so the set is visible before a live run fires.
    """
    sql = (
        "SELECT * FROM cases WHERE court = 'scotus' "
        "AND disposition IS NULL AND date_decided IS NULL "
        "AND distributed_for_conference IS NOT NULL "
        "AND docket_number GLOB '[0-9][0-9]-*' "
        f"AND {_TERM_YEAR_SQL} >= ? "
        "ORDER BY distributed_for_conference ASC, case_id ASC"
    )
    return [
        row
        for record in conn.execute(sql, (term_floor_year,))
        if is_modern_cert(row := _from_record(record))
    ]


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
    historical re-walk must not reopen an event a prior outcome already
    closed. Every other column takes the incoming value. Mirrors the ``cases``
    upsert's :func:`_update_clause` for ``predict_eligible``.
    """
    if column == "resolved":
        return f"{column}=MAX(excluded.{column}, events.{column})"
    return f"{column}=excluded.{column}"


def upsert_events(conn: sqlite3.Connection, events: list[CorpusEvent]) -> int:
    """Insert or replace predictable-event definitions by ``(case_id, event_id)``.

    Idempotent, so re-discovering a docket overwrites its event rows rather than
    duplicating them — like the ``cases`` upsert, this keeps every channel
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
    # The mirror reads the full committed set back per case (guarded on the flag,
    # so this is a pure no-op when the store is off).
    if (sink := _mirror_sink()) is not None:
        sink.mirror_events_for_cases(conn, [e.case_id for e in events])
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
    # Resolving is a direct UPDATE the upsert_events hook never sees, so re-mirror
    # the case's events here too — otherwise the casestore events.json keeps the
    # stale resolved=0 until the next re-ingest, and a casestore-provisioned
    # event.yaml would carry a stale flag for a replay cell's resolved target.
    if (sink := _mirror_sink()) is not None:
        sink.mirror_events_for_cases(conn, [case_id])


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


# --- per-Term live-discovery cursors (tracking state) ---------------------


def get_live_cursor(conn: sqlite3.Connection, term: int, stream: str) -> int | None:
    """The highest docket serial the live prober has confirmed served, or ``None``.

    ``None`` means the (Term, stream) pair has never been probed; the caller
    starts from the stream's numbering base (paid petitions from 1, IFP from
    5001).
    """
    cur = conn.execute(
        "SELECT last_serial FROM live_discovery_cursors WHERE term = ? AND stream = ?",
        (term, stream),
    )
    record = cur.fetchone()
    return int(record["last_serial"]) if record is not None else None


def set_live_cursor(conn: sqlite3.Connection, term: int, stream: str, last_serial: int) -> None:
    """Advance (or initialize) a (Term, stream) live-discovery cursor.

    Forward-only, mirroring :func:`set_discovery_watermark`: a write below the
    stored serial is ignored, so a degraded run cannot rewind the frontier and
    re-onboard the whole Term.
    """
    with conn:
        conn.execute(
            "INSERT INTO live_discovery_cursors (term, stream, last_serial) VALUES (?, ?, ?) "
            "ON CONFLICT(term, stream) DO UPDATE SET last_serial = excluded.last_serial "
            "WHERE excluded.last_serial > live_discovery_cursors.last_serial",
            (term, stream, last_serial),
        )


def get_live_frontier(conn: sqlite3.Connection, term: int, stream: str) -> int | None:
    """The serial the stream's frontier was last observed at, or ``None``.

    ``None`` means either the (Term, stream) was never probed or its walk has
    never reached the end. A value equal to :func:`get_live_cursor`'s means the
    stream is complete at the current cursor (see the table DDL).
    """
    cur = conn.execute(
        "SELECT frontier_serial FROM live_discovery_cursors WHERE term = ? AND stream = ?",
        (term, stream),
    )
    record = cur.fetchone()
    if record is None or record["frontier_serial"] is None:
        return None
    return int(record["frontier_serial"])


def set_live_frontier(conn: sqlite3.Connection, term: int, stream: str, serial: int) -> None:
    """Stamp where a walk observed the (Term, stream) frontier.

    Called on a miss-exit (consecutive 404s) with the cursor at that moment.
    Overwrites — the frontier of a live Term legitimately moves forward as new
    petitions are docketed — but only onto an existing cursor row: a stream
    with no cursor has served nothing, so it has no frontier worth recording.
    """
    with conn:
        conn.execute(
            "UPDATE live_discovery_cursors SET frontier_serial = ? WHERE term = ? AND stream = ?",
            (serial, term, stream),
        )


def live_cursor_rows(conn: sqlite3.Connection) -> list[tuple[int, str, int, int | None]]:
    """Every live-discovery cursor as ``(term, stream, last_serial, frontier_serial)``.

    The statpack's census/completeness read: one query over the whole (small)
    table, deterministically ordered. Local opens migrate the schema, so both
    columns always exist here.
    """
    cur = conn.execute(
        "SELECT term, stream, last_serial, frontier_serial FROM live_discovery_cursors "
        "ORDER BY term, stream"
    )
    return [
        (
            int(row["term"]),
            str(row["stream"]),
            int(row["last_serial"]),
            int(row["frontier_serial"]) if row["frontier_serial"] is not None else None,
        )
        for row in cur
    ]


def rename_live_streams(conn: sqlite3.Connection, renames: Mapping[str, str]) -> int:
    """Rename live-discovery cursor streams in place; idempotent migration helper.

    Each old-named row folds into its new name with the same forward-only rule
    as :func:`set_live_cursor` (the further-along serial wins on a collision),
    then the old row is dropped. A corpus with no old-named rows is a no-op, so
    a walker can run this unconditionally at start. Returns rows migrated.
    """
    migrated = 0
    with conn:
        for old, new in renames.items():
            rows = conn.execute(
                "SELECT term, last_serial, frontier_serial FROM live_discovery_cursors "
                "WHERE stream = ?",
                (old,),
            ).fetchall()
            for record in rows:
                # The frontier stamp travels with the serial it was observed at:
                # on a collision it follows the further-along cursor (the same
                # forward-only rule), so a stale stamp never overwrites a live one.
                conn.execute(
                    "INSERT INTO live_discovery_cursors (term, stream, last_serial, "
                    "frontier_serial) VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(term, stream) DO UPDATE SET "
                    "last_serial = excluded.last_serial, "
                    "frontier_serial = excluded.frontier_serial "
                    "WHERE excluded.last_serial > live_discovery_cursors.last_serial",
                    (
                        int(record["term"]),
                        new,
                        int(record["last_serial"]),
                        record["frontier_serial"],
                    ),
                )
                conn.execute(
                    "DELETE FROM live_discovery_cursors WHERE term = ? AND stream = ?",
                    (int(record["term"]), old),
                )
                migrated += 1
    return migrated


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
    # Under the split mode the snapshot lives only in the content store (mirrored
    # below); the blob keeps no snapshots table content, so change detection reads
    # the store via the read source instead.
    if not _split_mode():
        with conn:
            conn.execute(
                "INSERT INTO snapshots (case_id, snapshot_date, payload) VALUES (?, ?, ?) "
                "ON CONFLICT(case_id, snapshot_date) DO UPDATE SET payload = excluded.payload",
                (case_id, snapshot_date.isoformat(), json.dumps(payload, sort_keys=True)),
            )
    if (sink := _mirror_sink()) is not None:
        sink.mirror_snapshot(case_id, snapshot_date, payload)


def latest_snapshot(conn: ReadConnection, case_id: str) -> tuple[date, dict[str, Any]] | None:
    """The most recent dated snapshot for a case — ``(date, payload)`` — or ``None``.

    Ordered by ``snapshot_date`` so the newest pull wins; ``None`` means the case
    has never been snapshotted (the onboarding signal for ``pull``). Under the
    corpus-split mode the snapshots live in the content store, so the read is
    served from there (``conn`` is unused) — see :func:`_payload_read_source`.
    """
    if (source := _payload_read_source()) is not None:
        return source.latest_snapshot(case_id)
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


def latest_live_snapshot(conn: ReadConnection, case_id: str) -> tuple[date, dict[str, Any]] | None:
    """The most recent **live-shaped** snapshot for a case, or ``None``.

    The `snapshots` table holds both channels' payloads under one key space —
    a supremecourt.gov docket JSON (carrying ``ProceedingsandOrder``) and a
    CourtListener REST docket look nothing alike — so a consumer of the live
    proceedings (the signal backfill) must skip past any newer REST snapshot a
    later ``pull`` stored, not just take the newest row. Under the corpus-split
    mode the snapshots live in the content store, so it is served from there.
    """
    if (source := _payload_read_source()) is not None:
        return source.latest_live_snapshot(case_id)
    cur = conn.execute(
        "SELECT snapshot_date, payload FROM snapshots WHERE case_id = ? "
        "ORDER BY snapshot_date DESC",
        (case_id,),
    )
    for record in cur:
        payload: dict[str, Any] = json.loads(record["payload"])
        if "ProceedingsandOrder" in payload:
            return date.fromisoformat(record["snapshot_date"]), payload
    return None


def snapshot_count(conn: ReadConnection) -> int:
    """Total number of dated snapshot rows in the corpus."""
    cur = conn.execute("SELECT COUNT(*) AS n FROM snapshots")
    return int(cur.fetchone()["n"])


# --- per-case filed-document text (raw facts) ------------------------------


def upsert_documents(conn: sqlite3.Connection, documents: list[CaseDocument]) -> int:
    """Insert or replace documents by ``(case_id, kind)``; returns rows written.

    Latest-wins by design: a corrected or re-filed document (a new BIO after a
    bounced one) simply supersedes the stored text for its kind.
    """
    split = _split_mode()
    if not split:
        with conn:
            conn.executemany(
                "INSERT INTO documents (case_id, kind, url, entry_date, fetched_at, pages, "
                "truncated, text) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(case_id, kind) DO UPDATE SET url = excluded.url, "
                "entry_date = excluded.entry_date, fetched_at = excluded.fetched_at, "
                "pages = excluded.pages, truncated = excluded.truncated, text = excluded.text",
                [
                    (
                        d.case_id,
                        d.kind,
                        d.url,
                        d.entry_date,
                        d.fetched_at.isoformat(),
                        d.pages,
                        int(d.truncated),
                        d.text,
                    )
                    for d in documents
                ],
            )
    if (sink := _mirror_sink()) is not None:
        if split:
            # The blob holds no documents to read back; the store is the system of
            # record, so mirror the in-hand batch and let it merge with the case's
            # existing manifest (the writer already deduped against the store).
            sink.mirror_documents(documents)
        else:
            # The mirror reads the full committed set back per case (guarded on the
            # flag, so this is a pure no-op when the store is off).
            sink.mirror_documents_for_cases(conn, [d.case_id for d in documents])
    return len(documents)


def documents_for_case(conn: ReadConnection, case_id: str) -> list[CaseDocument]:
    """Every stored document for a case, ordered by kind (deterministic).

    Provisioning materializes these into the cell's gitignored ``record/``
    path; empty when the live poller has not fetched for this case (a
    pre-OT2021 petition whose links the site no longer serves, or a case the
    distribution trigger has not yet reached). Like :func:`_optional_date` for
    columns, a remote blob packed before the table existed reads as "no
    documents" rather than failing the ranged cell. Under the corpus-split mode the
    documents live in the content store, so the set is served from there.
    """
    if (source := _payload_read_source()) is not None:
        return source.documents_for_case(case_id)
    try:
        cur = conn.execute(
            "SELECT case_id, kind, url, entry_date, fetched_at, pages, truncated, text "
            "FROM documents WHERE case_id = ? ORDER BY kind",
            (case_id,),
        )
    except Exception as exc:
        if "no such table" in str(exc).lower():
            return []
        raise
    return [
        CaseDocument(
            case_id=record["case_id"],
            kind=record["kind"],
            url=record["url"],
            entry_date=record["entry_date"],
            fetched_at=date.fromisoformat(record["fetched_at"]),
            pages=int(record["pages"]),
            truncated=bool(record["truncated"]),
            text=record["text"],
        )
        for record in cur
    ]
