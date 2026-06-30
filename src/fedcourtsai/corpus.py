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
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .schemas import Disposition, EventKind

CORPUS_DB_FILENAME = "corpus.db"


def corpus_db_path(corpus_root: Path) -> Path:
    """Location of the packed corpus database within ``corpus_root``."""
    return corpus_root / CORPUS_DB_FILENAME


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
    originating_court            TEXT,
    originating_docket_number    TEXT
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


_DN_LABEL = re.compile(r"^NO\.?\s+")  # a leading "No." / "No " docket-number label
_DN_WHITESPACE = re.compile(r"\s+")


def normalize_docket_number(raw: str | None) -> str | None:
    """Canonicalize a docket-number string for the lower-court join, or ``None``.

    Upper-cases, drops a leading ``No.`` label, and removes all whitespace, so two
    spellings of the *same* number compare equal (``"No. 21-35466"`` ==
    ``"21-35466"``). Deliberately a light, lossless normalization that yields no
    false matches: a consolidated / multi-number string (``"21-1, 21-2"``) keeps
    its punctuation and so will not match a single tracked docket — a miss, never a
    wrong link. Blank input (and a string that normalizes to empty) returns
    ``None``. Registered as the SQLite ``norm_dn`` function so the join can compare
    a stored ``docket_number`` against a normalized incoming value.
    """
    if raw is None:
        return None
    text = _DN_WHITESPACE.sub("", _DN_LABEL.sub("", raw.strip().upper()))
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
        conn.executescript(_SCHEMA)
        _migrate_cases(conn)
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
        "originating_court": row.originating_court,
        "originating_docket_number": row.originating_docket_number,
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
        originating_court=record["originating_court"],
        originating_docket_number=record["originating_docket_number"],
    )


def _update_clause(column: str) -> str:
    """The ``ON CONFLICT`` assignment for one column, honoring its latch (if any).

    Most columns take the incoming value (``excluded``). Two never regress:
    ``last_pulled`` only ever advances — a write without a fresh stamp (e.g. a
    bulk seed re-ingest) keeps the timestamp a prior pull recorded — and
    ``predict_eligible`` only ever latches on, so once a case is in prediction
    scope a later re-ingest (under a narrower rule) cannot drop it back out.
    """
    if column == "last_pulled":
        return f"{column}=COALESCE(excluded.{column}, cases.{column})"
    if column == "predict_eligible":
        return f"{column}=MAX(excluded.{column}, cases.{column})"
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
    """
    if row.court != "scotus":
        return False
    docket_number = row.docket_number.strip()
    bare_sequential = bool(docket_number) and docket_number.isdigit()
    pre_discretionary = row.date_filed is not None and row.date_filed.year < _DISCRETIONARY_ERA_YEAR
    return bare_sequential or pre_discretionary


# Modern SCOTUS docket numbers lead with a two-digit October-Term year ("01-7700"
# -> OT2001, "93-7515" -> OT1993). Term-style numbering began OT1971, so a 70-99
# prefix is 19xx and 00-69 is 20xx — a pivot good through OT2069.
_SCOTUS_TERM_RE = re.compile(r"^(\d{2})-\d+")

# Provisional staleness cutoff (issue #343 refines it against the corpus). A SCOTUS
# Term before this is long past any pending-petition horizon; far enough back that a
# genuinely open modern cert petition is never caught.
_STALE_TERM_CUTOFF_YEAR = 2015


def scotus_term_year(docket_number: str) -> int | None:
    """Parse the October-Term year from a modern SCOTUS docket number, or ``None``.

    ``"01-7700"`` -> ``2001``, ``"93-7515"`` -> ``1993``. Returns ``None`` for
    anything that is not the modern ``YY-NNNN`` form — bare sequential historical
    numbers (``"801"``), application/original dockets (``"22A123"``, ``"22O141"``),
    or blank — so callers fall through rather than guess a year. Public so the scope
    audit can bucket the open events the predicate does *not* catch (#343).
    """
    match = _SCOTUS_TERM_RE.match(docket_number.strip())
    if match is None:
        return None
    two_digit = int(match.group(1))
    return 1900 + two_digit if two_digit >= 70 else 2000 + two_digit


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


# Each (predicate, reason) the predict-scope gate excludes a case on — the single
# source of truth shared by the matrix backstop (``cli._scope_filtered``), the
# run-cleanup sweep (``cleanup``), and the scope audit (``validate.run_scope_audit``),
# so an exclusion that lands here is enforced at every point.
OUT_OF_SCOPE_RULES: list[tuple[Callable[[CorpusRow], bool], str]] = [
    (is_historical_mandatory, "pre-1925 mandatory-jurisdiction matter (#309)"),
    (is_stale_unresolvable, "stale unresolvable old SCOTUS petition (#333)"),
    (is_date_inconsistent, "internally inconsistent dates — decided before filed (#171)"),
]


def out_of_scope_reason(row: CorpusRow) -> str | None:
    """The first exclusion reason matching ``row``, or ``None`` if it is in predict scope."""
    for predicate, reason in OUT_OF_SCOPE_RULES:
        if predicate(row):
            return reason
    return None


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


def events_for_case(conn: sqlite3.Connection, case_id: str) -> list[CorpusEvent]:
    """Predictable events defined for one case, in ``event_id`` order."""
    cur = conn.execute("SELECT * FROM events WHERE case_id = ? ORDER BY event_id", (case_id,))
    return [_event_from_record(record) for record in cur]


def iter_open_events(
    conn: sqlite3.Connection, *, court: str | None = None
) -> Iterator[CorpusEvent]:
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


def latest_snapshot(conn: sqlite3.Connection, case_id: str) -> tuple[date, dict[str, Any]] | None:
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


def snapshot_count(conn: sqlite3.Connection) -> int:
    """Total number of dated snapshot rows in the corpus."""
    cur = conn.execute("SELECT COUNT(*) AS n FROM snapshots")
    return int(cur.fetchone()["n"])
