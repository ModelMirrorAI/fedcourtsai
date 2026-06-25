"""``run-seed``: the deterministic, no-agent historical backfill.

Seed loads the historical mass from CourtListener's **public bulk-data** export
(not the rate-limited REST API), so it spends **no API budget** — see
``docs/data-pipeline.md`` and ``docs/seed-backfill.md``. One invocation processes
the **next chunk** for the tracked courts and returns; a daily schedule walks the
backlog until complete, then a quarterly pass reconciles against each new bulk
snapshot.

The pieces here:

- :class:`BulkSource` — the seam over a bulk snapshot. :func:`backfill` depends
  only on this protocol, so it is exercised with an in-memory fake; the live
  :class:`CourtListenerBulkSource` confines network access to one method.
- :func:`backfill` — the chunk driver: read the cursor, load the next chunk per
  court through the shared ingestion core into the corpus, advance the cursor,
  and return a :class:`SeedReport` for the tracking-issue comment.

The cursor (:class:`fedcourtsai.schemas.SeedProgress`, ``config/seed-progress.yaml``)
is git-tracked so the backfill is resumable and rebuildable after a fresh clone.
"""

from __future__ import annotations

import bz2
import csv
import gzip
import io
import json
import os
import re
import sqlite3
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import IO, Any, Protocol, runtime_checkable
from urllib.parse import urlsplit, urlunsplit

import httpx
import yaml
from pydantic import BaseModel

from .. import corpus, ids
from ..schemas import CourtProgress, SeedProgress
from ..serialize import write_yaml
from .events import AmbiguousEntry, extract_events
from .ingest import from_bulk_row, upsert_to_corpus


@dataclass(frozen=True)
class CourtChunk:
    """The next slice of one court's bulk stream, as returned by a bulk source.

    ``rows`` are the bulk records taken after the cursor's ``offset`` (at most the
    requested ``limit``). ``reached_end`` is ``True`` when the stream was exhausted
    — the signal to mark the court complete. ``total`` is the court's full row
    count when the source knows it cheaply (else ``None``; the driver fills it from
    the consumed offset once the stream ends).
    """

    rows: list[Mapping[str, Any]]
    reached_end: bool
    total: int | None = None


@runtime_checkable
class BulkSource(Protocol):
    """A bulk snapshot the backfill reads, one court chunk at a time."""

    @property
    def snapshot_id(self) -> str:
        """Stable id of the snapshot being loaded (drives reconciliation)."""

    def fetch_court_chunk(self, court: str, *, offset: int, limit: int) -> CourtChunk:
        """The next ``limit`` rows for ``court`` after ``offset`` in the snapshot."""


class CourtReport(BaseModel):
    """Per-court progress line in the run report."""

    court: str
    loaded: int
    total: int | None = None
    percent: float | None = None
    complete: bool


class SeedReport(BaseModel):
    """The ``--report`` payload, summarized for the tracking-issue comment."""

    snapshot: str | None = None
    complete: bool
    loaded_this_run: int
    courts: list[CourtReport]
    ambiguous: int = 0
    """Bulk entries the deterministic event classifier could not place; recorded
    (not guessed) for a later agent reconcile, mirroring forward discovery."""


# --- cursor IO -----------------------------------------------------------------


def load_cursor(path: Path) -> SeedProgress:
    """Read the committed cursor, or a fresh one if it does not exist yet."""
    if not path.exists():
        return SeedProgress()
    data = yaml.safe_load(path.read_text()) or {}
    return SeedProgress.model_validate(data)


def save_cursor(path: Path, progress: SeedProgress) -> None:
    """Write the bumped cursor deterministically (sorted, minimal diff)."""
    write_yaml(path, progress)


# --- the chunk driver ----------------------------------------------------------


def _reconcile(progress: SeedProgress, snapshot_id: str) -> SeedProgress:
    """Start a fresh reconciliation pass for a newly published snapshot.

    A new bulk snapshot supersedes the one the cursor was tracking, so the
    backfill re-loads it from the top — the upsert is idempotent, so unchanged
    cases overwrite in place and any corrections/additions land. Offsets reset;
    the known court set is preserved.
    """
    return SeedProgress(snapshot=snapshot_id, courts={c: CourtProgress() for c in progress.courts})


def backfill(
    source: BulkSource,
    *,
    cursor_path: Path,
    courts: Sequence[str],
    corpus_db_path: Path,
    max_cases: int,
) -> SeedReport:
    """Load the next chunk of the bulk snapshot into the corpus; return a report.

    Reads the cursor, reconciles against the live snapshot id if it changed, then
    walks the tracked courts in order, loading each court's next rows (skipping
    those already consumed) through the shared ingestion core into the packed
    corpus until the per-run ``max_cases`` budget is spent. Each ingested chunk
    then runs the deterministic event-definition stage
    (:mod:`fedcourtsai.pipeline.events`) so every seeded docket carries its
    predictable event(s) — at minimum the baseline disposition — exactly as
    forward discovery records them. Advances and writes the cursor. Idempotent:
    re-running after completion loads zero rows, and re-ingesting a docket
    re-upserts its events in place.
    """
    progress = load_cursor(cursor_path)
    if progress.snapshot != source.snapshot_id:
        progress = _reconcile(progress, source.snapshot_id)

    loaded_this_run = 0
    events: list[corpus.CorpusEvent] = []
    ambiguous: list[AmbiguousEntry] = []
    for court in courts:
        cp = progress.courts.setdefault(court, CourtProgress())
        if cp.complete:
            continue
        remaining = max_cases - loaded_this_run
        if remaining <= 0:
            break
        chunk = source.fetch_court_chunk(court, offset=cp.offset, limit=remaining)
        if chunk.rows:
            upsert_to_corpus(corpus_db_path, [from_bulk_row(r) for r in chunk.rows])
            for raw in chunk.rows:
                # Same event-definition stage discovery runs (discover.py), so a
                # seeded and a discovered docket yield identical event rows. Bulk
                # rows rarely carry entries, so most get the baseline event alone.
                extraction = extract_events(raw, normalize=from_bulk_row)
                events.extend(extraction.events)
                ambiguous.extend(extraction.ambiguous)
            cp.offset += len(chunk.rows)
            loaded_this_run += len(chunk.rows)
        if chunk.total is not None:
            cp.total = chunk.total
        if chunk.reached_end:
            cp.complete = True
            cp.total = chunk.total if chunk.total is not None else cp.offset

    frontier = snapshot_date(source.snapshot_id)
    completed = [c for c in courts if progress.courts.get(c, CourtProgress()).complete]
    if events or (frontier is not None and completed):
        with corpus.connect(corpus_db_path) as conn:
            if events:
                corpus.upsert_events(conn, events)
            # Hand the discovery frontier off to forward pull. A court whose
            # backfill is complete is "complete as of" the snapshot's date, so its
            # discovery watermark seeds to that date; the first forward `pull` then
            # discovers everything filed since the snapshot, not since today —
            # closing the snapshot→today gap. ``set_discovery_watermark`` only
            # moves forward, so a later forward watermark always wins and a re-run
            # (or a quarterly reconciliation against the same snapshot) never
            # rewinds it. A snapshot id that is not a quarter label yields no date,
            # so no frontier is handed off (the court keeps falling back to today).
            if frontier is not None:
                for court in completed:
                    corpus.set_discovery_watermark(conn, court, frontier)

    save_cursor(cursor_path, progress)
    return _report(progress, courts, loaded_this_run, ambiguous)


def _report(
    progress: SeedProgress,
    courts: Sequence[str],
    loaded_this_run: int,
    ambiguous: Sequence[AmbiguousEntry] = (),
) -> SeedReport:
    lines: list[CourtReport] = []
    for court in courts:
        cp = progress.courts.get(court, CourtProgress())
        if cp.total:
            percent: float | None = round(100.0 * cp.offset / cp.total, 1)
        elif cp.complete:
            percent = 100.0
        else:
            percent = None
        lines.append(
            CourtReport(
                court=court, loaded=cp.offset, total=cp.total, percent=percent, complete=cp.complete
            )
        )
    complete = bool(courts) and all(
        progress.courts.get(c, CourtProgress()).complete for c in courts
    )
    return SeedReport(
        snapshot=progress.snapshot,
        complete=complete,
        loaded_this_run=loaded_this_run,
        courts=lines,
        ambiguous=len(ambiguous),
    )


# --- the live CourtListener bulk source ----------------------------------------


def quarter_id(d: date) -> str:
    """Quarter label, e.g. ``2026-Q2``, used as a default snapshot id."""
    return f"{d.year}-Q{(d.month - 1) // 3 + 1}"


# --- snapshot discovery (resolve the latest bulk snapshot from the bucket) ------

# Public bulk-data naming convention: ``<table>-YYYY-MM-DD.csv.(bz2|gz)``.
_SNAPSHOT_RE = re.compile(r"-(\d{4}-\d{2}-\d{2})\.csv\.(?:bz2|gz)$")
# A partial-generation run leaves tiny placeholder objects (an empty bz2 is ~14
# bytes); require a real payload so discovery never picks a stub snapshot.
_MIN_SNAPSHOT_BYTES = 1024
# S3 ListObjectsV2 XML uses a default namespace; ``{*}`` matches it either way.
_S3_NS = "{*}"


def _iter_bucket(client: httpx.Client, origin: str, prefix: str) -> Iterator[tuple[str, int]]:
    """Yield ``(key, size)`` for every object under ``prefix``, paging as needed."""
    token: str | None = None
    while True:
        params = {"list-type": "2", "prefix": prefix}
        if token is not None:
            params["continuation-token"] = token
        resp = client.get(origin, params=params)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        for contents in root.findall(f"{_S3_NS}Contents"):
            key = contents.findtext(f"{_S3_NS}Key")
            size = contents.findtext(f"{_S3_NS}Size")
            if key is not None and size is not None:
                yield key, int(size)
        if root.findtext(f"{_S3_NS}IsTruncated") == "true":
            token = root.findtext(f"{_S3_NS}NextContinuationToken")
        else:
            return


def discover_latest_snapshot(
    base_url: str,
    *,
    tables: Sequence[str] = ("dockets",),
    client: httpx.Client | None = None,
    timeout: float = 30.0,
    min_bytes: int = _MIN_SNAPSHOT_BYTES,
) -> str:
    """Return the most recent snapshot date published for *every* table.

    Lists the public bulk-data bucket under ``base_url`` and returns the latest
    ``YYYY-MM-DD`` carrying a non-placeholder file for each table in ``tables``
    (their intersection), so a multi-table run never references a table that lagged
    during the quarterly regeneration. Raises :class:`ValueError` if no snapshot is
    published for all of them.
    """
    split = urlsplit(base_url)
    origin = urlunsplit((split.scheme, split.netloc, "", "", ""))
    prefix = split.path.lstrip("/")
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    owned = client is None
    client = client or httpx.Client(timeout=timeout, follow_redirects=True)
    try:
        per_table: list[set[str]] = []
        for table in tables:
            dates: set[str] = set()
            for key, size in _iter_bucket(client, origin, f"{prefix}{table}-"):
                if size < min_bytes:
                    continue
                m = _SNAPSHOT_RE.search(key)
                if m is not None:
                    dates.add(m.group(1))
            per_table.append(dates)
    finally:
        if owned:
            client.close()
    common = set.intersection(*per_table) if per_table else set()
    if not common:
        raise ValueError(f"No bulk snapshot published for all of {list(tables)} under {base_url}")
    return max(common)  # ISO dates sort lexicographically == chronologically


def bulk_file_url(base_url: str, table: str, snapshot: str, *, ext: str = "csv.bz2") -> str:
    """Build the bulk file URL for ``table`` at ``snapshot`` under ``base_url``."""
    return f"{base_url.rstrip('/')}/{table}-{snapshot}.{ext}"


def resolve_dockets_source(
    bulk_url: str,
    *,
    snapshot: str | None = None,
    timeout: float = 30.0,
    client: httpx.Client | None = None,
) -> tuple[str, str]:
    """Resolve ``(snapshot_id, dockets_url)`` from the configured bulk URL.

    ``bulk_url`` is normally the bulk-data **base** directory: the latest snapshot
    is auto-discovered (unless ``snapshot`` pins one for a reproducible run) and the
    dockets file URL is built from it. An explicit ``.csv`` file URL is honored
    as-is — a manual pin — with its snapshot taken from the filename (or
    ``snapshot`` when given).
    """
    if bulk_url.rstrip("/").endswith((".csv.bz2", ".csv.gz", ".csv")):
        m = _SNAPSHOT_RE.search(bulk_url)
        snap = snapshot or (m.group(1) if m else quarter_id(date.today()))
        return snap, bulk_url
    snap = snapshot or discover_latest_snapshot(bulk_url, timeout=timeout, client=client)
    return snap, bulk_file_url(bulk_url, "dockets", snap)


_QUARTER_LAST_DAY = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}


def sibling_bulk_url(dockets_url: str, table: str) -> str | None:
    """The URL of a sibling bulk file (e.g. ``opinion-clusters``) next to dockets.

    CourtListener names each table's bulk file ``<table>-<snapshot>.csv.bz2`` in
    one directory, so a sibling table's URL is the dockets URL with its leading
    ``dockets`` filename token swapped for ``table``. Returns ``None`` when the
    dockets URL does not follow that naming (a manually pinned, non-standard URL),
    in which case the join simply has no sibling to read and those fields stay
    blank — the backfill still loads the docket spine.
    """
    head, sep, name = dockets_url.rpartition("/")
    if not name.startswith("dockets"):
        return None
    return f"{head}{sep}{table}{name[len('dockets') :]}"


def snapshot_date(snapshot_id: str) -> date | None:
    """The bulk snapshot's as-of date — the discovery frontier seed hands to pull.

    Two id shapes carry a date:

    - ``YYYY-MM-DD`` — an auto-discovered snapshot id *is* the bulk file's
      publication date (see :func:`discover_latest_snapshot`), which is the most
      accurate "complete as of" date available and the default in CI.
    - ``YYYY-Qn`` — a manually pinned quarter label maps to that quarter's final
      calendar day, since CourtListener regenerates the export on the last day of
      March/June/September/December.

    The date is what each completed court's discovery watermark seeds to, so the
    first forward ``pull`` searches from the snapshot rather than from today,
    closing the snapshot→today gap. Returns ``None`` for any other id (e.g. a
    one-off nightly label); seed then cannot establish a frontier and the court
    falls back to discovery's last-resort default.
    """
    iso = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", snapshot_id)
    if iso is not None:
        try:
            return date(int(iso[1]), int(iso[2]), int(iso[3]))
        except ValueError:
            return None
    m = re.fullmatch(r"(\d{4})-Q([1-4])", snapshot_id)
    if m is None:
        return None
    month, day = _QUARTER_LAST_DAY[int(m.group(2))]
    return date(int(m.group(1)), month, day)


# Rows inserted per executemany batch while staging the GB-scale bulk files.
_STAGE_BATCH = 5000

_STAGING_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (snapshot_id TEXT NOT NULL);
-- One row per tracked docket; the raw CSV record is kept verbatim as JSON so the
-- normalizer sees every column and a new upstream column needs no migration here.
CREATE TABLE IF NOT EXISTS dockets (
    id       INTEGER PRIMARY KEY,
    court_id TEXT NOT NULL,
    row      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dockets_court ON dockets(court_id, id);
-- One (latest) opinion cluster per docket, carrying just the fields the corpus
-- lifts. Keyed on the docket foreign key so Phase B is a one-to-one LEFT JOIN.
CREATE TABLE IF NOT EXISTS clusters (
    docket_id   INTEGER PRIMARY KEY,
    cluster_id  INTEGER NOT NULL,
    disposition TEXT,
    summary     TEXT,
    judges      TEXT
);
"""

# opinion-cluster columns lifted into the served docket row, under the names the
# normalizer (`ingest._normalize`) already reads.
_CLUSTER_FIELDS = ("disposition", "summary", "judges")


@dataclass
class CourtListenerBulkSource:
    """A staged, multi-table join over CourtListener public bulk-data CSVs.

    A bulk snapshot is one combined CSV *per table* (dockets, opinion-clusters, …),
    each sorted by its own primary key rather than the join key — so a row's full
    fact set is spread across files that cannot be co-iterated. This source resolves
    that with a two-phase staged join behind the :class:`BulkSource` seam:

    - **Phase A — stage once** (:meth:`_ensure_staged`, heavy, on the first fetch):
      stream ``dockets`` filtered to the tracked ``courts`` into a local SQLite,
      then stream ``opinion-clusters`` keeping only rows whose ``docket_id`` is in
      that set (the latest cluster per docket wins), into a table keyed on the join
      key. The staging DB is tagged with ``snapshot_id``; pointing ``staging_path``
      at a path the workflow caches lets daily runs *reuse* it instead of
      re-streaming, and a snapshot change rebuilds it.
    - **Phase B — serve chunks** (:meth:`fetch_court_chunk`, cheap, per run): a
      single indexed SQL ``LEFT JOIN`` aliasing the cluster columns to the names the
      normalizer reads, ordered by docket id with ``LIMIT``/``OFFSET``.

    URLs (and ``snapshot_id``) come from the caller (the runner env names snapshots
    by date). ``clusters_url`` is optional: without it the docket spine still loads
    and the joined fields stay blank. ``*_cache`` inject local files in place of a
    download (tests, or a pre-fetched file); network access is confined to
    :meth:`_ensure_local`.
    """

    snapshot_id: str
    dockets_url: str
    courts: Sequence[str]
    clusters_url: str | None = None
    court_field: str = "court_id"
    timeout: float = 30.0
    client: httpx.Client | None = None
    staging_path: Path | None = None
    dockets_cache: Path | None = None
    clusters_cache: Path | None = None
    _conn: sqlite3.Connection | None = field(default=None, init=False)
    _db_path: Path | None = field(default=None, init=False)
    _owned_db: bool = field(default=False, init=False)
    _owned_files: list[Path] = field(default_factory=list, init=False)

    # --- Phase B: serve chunks (cheap, per run) --------------------------------

    def fetch_court_chunk(self, court: str, *, offset: int, limit: int) -> CourtChunk:
        conn = self._ensure_staged()
        target = ids.slugify(court)
        (total,) = conn.execute(
            "SELECT COUNT(*) FROM dockets WHERE court_id = ?", (target,)
        ).fetchone()
        cur = conn.execute(
            "SELECT d.row AS row, c.disposition AS disposition, c.summary AS summary, "
            "c.judges AS judges "
            "FROM dockets d LEFT JOIN clusters c ON c.docket_id = d.id "
            "WHERE d.court_id = ? ORDER BY d.id LIMIT ? OFFSET ?",
            (target, limit, offset),
        )
        rows = [self._merge(r) for r in cur.fetchall()]
        reached_end = offset + len(rows) >= total
        return CourtChunk(rows=rows, reached_end=reached_end, total=total)

    @staticmethod
    def _merge(row: sqlite3.Row) -> Mapping[str, Any]:
        """Overlay the joined cluster fields onto the raw docket record."""
        record = dict(json.loads(row["row"]))
        for field_name in _CLUSTER_FIELDS:
            value = row[field_name]
            if value is not None:
                record[field_name] = value
        return record

    # --- Phase A: stage once (heavy, on snapshot change) -----------------------

    def _ensure_staged(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        path = self.staging_path
        if path is None:
            fd, name = tempfile.mkstemp(suffix=".staging.db")
            os.close(fd)
            path = Path(name)
            self._owned_db = True
        self._db_path = path
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.executescript(_STAGING_SCHEMA)
        if not self._snapshot_matches(conn):
            self._build_staging(conn)
        self._conn = conn
        return conn

    def _snapshot_matches(self, conn: sqlite3.Connection) -> bool:
        meta = conn.execute("SELECT snapshot_id FROM meta LIMIT 1").fetchone()
        return meta is not None and meta[0] == self.snapshot_id

    def _build_staging(self, conn: sqlite3.Connection) -> None:
        conn.execute("DELETE FROM dockets")
        conn.execute("DELETE FROM clusters")
        conn.execute("DELETE FROM meta")
        docket_ids = self._stage_dockets(conn)
        if self.clusters_url is not None:
            self._stage_clusters(conn, docket_ids)
        conn.execute("INSERT INTO meta(snapshot_id) VALUES (?)", (self.snapshot_id,))
        conn.commit()

    def _stage_dockets(self, conn: sqlite3.Connection) -> set[int]:
        targets = {ids.slugify(c) for c in self.courts}
        path = self._ensure_local(self.dockets_url, self.dockets_cache)
        docket_ids: set[int] = set()
        batch: list[tuple[int, str, str]] = []
        with self._open_text(path, self.dockets_url) as fh:
            for row in csv.DictReader(fh):
                raw = (row.get(self.court_field) or "").strip()
                if not raw:
                    continue
                court = ids.slugify(raw)
                if court not in targets:
                    continue
                docket_id = _as_int(row.get("id"))
                if docket_id is None:
                    continue
                docket_ids.add(docket_id)
                batch.append((docket_id, court, json.dumps(row, sort_keys=True)))
                if len(batch) >= _STAGE_BATCH:
                    self._insert_dockets(conn, batch)
                    batch.clear()
        self._insert_dockets(conn, batch)
        return docket_ids

    @staticmethod
    def _insert_dockets(conn: sqlite3.Connection, batch: Sequence[tuple[int, str, str]]) -> None:
        if batch:
            conn.executemany(
                "INSERT OR REPLACE INTO dockets(id, court_id, row) VALUES (?, ?, ?)", batch
            )

    def _stage_clusters(self, conn: sqlite3.Connection, docket_ids: set[int]) -> None:
        assert self.clusters_url is not None
        path = self._ensure_local(self.clusters_url, self.clusters_cache)
        batch: list[tuple[int, int, str | None, str | None, str | None]] = []
        with self._open_text(path, self.clusters_url) as fh:
            for row in csv.DictReader(fh):
                docket_id = _as_int(row.get("docket_id"))
                if docket_id is None or docket_id not in docket_ids:
                    continue
                batch.append(
                    (
                        docket_id,
                        _as_int(row.get("id")) or 0,
                        _clean_cell(row.get("disposition")),
                        _clean_cell(row.get("summary")),
                        _clean_cell(row.get("judges")),
                    )
                )
                if len(batch) >= _STAGE_BATCH:
                    self._upsert_clusters(conn, batch)
                    batch.clear()
        self._upsert_clusters(conn, batch)

    @staticmethod
    def _upsert_clusters(
        conn: sqlite3.Connection,
        batch: Sequence[tuple[int, int, str | None, str | None, str | None]],
    ) -> None:
        # One cluster per docket: a later, higher-id cluster (the most recent
        # disposition) wins; an earlier one never clobbers it.
        if batch:
            conn.executemany(
                "INSERT INTO clusters(docket_id, cluster_id, disposition, summary, judges) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(docket_id) DO UPDATE SET "
                "cluster_id = excluded.cluster_id, disposition = excluded.disposition, "
                "summary = excluded.summary, judges = excluded.judges "
                "WHERE excluded.cluster_id > clusters.cluster_id",
                batch,
            )

    # --- IO (network confined here) --------------------------------------------

    def _ensure_local(self, url: str, cache: Path | None) -> Path:
        if cache is not None and cache.exists():
            return cache
        fd, name = tempfile.mkstemp(suffix=".bulk")
        os.close(fd)
        path = Path(name)
        client = self.client or httpx.Client(timeout=self.timeout, follow_redirects=True)
        try:
            with client.stream("GET", url) as resp:
                resp.raise_for_status()
                with path.open("wb") as fh:
                    for block in resp.iter_bytes():
                        fh.write(block)
        finally:
            if self.client is None:
                client.close()
        self._owned_files.append(path)
        return path

    @staticmethod
    def _open_text(path: Path, url: str) -> IO[str]:
        if url.endswith(".bz2"):
            return io.TextIOWrapper(bz2.open(path, "rb"), encoding="utf-8", newline="")
        if url.endswith(".gz"):
            return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8", newline="")
        return open(path, encoding="utf-8", newline="")

    def cleanup(self) -> None:
        """Drop everything this source created; leave injected/cached files alone.

        Closes the staging connection and removes the downloaded source files and a
        *temporary* staging DB. A caller-supplied ``staging_path`` is preserved so a
        later run can reuse it; injected ``*_cache`` files are never touched.
        """
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        for path in self._owned_files:
            path.unlink(missing_ok=True)
        self._owned_files.clear()
        if self._owned_db and self._db_path is not None:
            self._db_path.unlink(missing_ok=True)
            self._owned_db = False


def _as_int(value: Any) -> int | None:
    """Parse a CSV cell to ``int``, or ``None`` if blank or non-numeric."""
    text = value.strip() if isinstance(value, str) else value
    if text in (None, ""):
        return None
    try:
        return int(text)
    except (TypeError, ValueError):
        return None


def _clean_cell(value: Any) -> str | None:
    """Trim a CSV cell to a non-empty string, or ``None`` for a blank."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None
