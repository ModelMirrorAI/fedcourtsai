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
import os
import re
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

from .. import ids
from ..schemas import CourtProgress, SeedProgress
from ..serialize import write_yaml
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
    corpus until the per-run ``max_cases`` budget is spent. Advances and writes
    the cursor. Idempotent: re-running after completion loads zero rows.
    """
    progress = load_cursor(cursor_path)
    if progress.snapshot != source.snapshot_id:
        progress = _reconcile(progress, source.snapshot_id)

    loaded_this_run = 0
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
            cp.offset += len(chunk.rows)
            loaded_this_run += len(chunk.rows)
        if chunk.total is not None:
            cp.total = chunk.total
        if chunk.reached_end:
            cp.complete = True
            cp.total = chunk.total if chunk.total is not None else cp.offset

    save_cursor(cursor_path, progress)
    return _report(progress, courts, loaded_this_run)


def _report(progress: SeedProgress, courts: Sequence[str], loaded_this_run: int) -> SeedReport:
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


@dataclass
class CourtListenerBulkSource:
    """Streams a CourtListener public bulk-data CSV, filtered to one court.

    A bulk snapshot is a single combined CSV per table (one file for *all*
    courts), so a court's "stream" is the subsequence of rows whose court id
    matches. The file is fetched once per run to a local cache, then scanned
    locally per court — a multi-court run does not re-download it. Network access
    is confined to :meth:`_ensure_local`; the parse/filter logic is pure.

    The exact bulk file ``url`` (and its ``snapshot_id``) are supplied by the
    caller from the runner env, since CourtListener names snapshots by date; the
    layout assumed here (CSV with a court-id column, optional ``.bz2``/``.gz``
    compression inferred from the url) may need tuning when wired to live data.
    """

    snapshot_id: str
    url: str
    court_field: str = "court_id"
    timeout: float = 30.0
    client: httpx.Client | None = None
    cache_path: Path | None = None
    _owned_cache: bool = field(default=False, init=False)

    def _ensure_local(self) -> Path:
        if self.cache_path is not None and self.cache_path.exists():
            return self.cache_path
        fd, name = tempfile.mkstemp(suffix=".bulk")
        os.close(fd)
        path = Path(name)
        client = self.client or httpx.Client(timeout=self.timeout, follow_redirects=True)
        try:
            with client.stream("GET", self.url) as resp:
                resp.raise_for_status()
                with path.open("wb") as fh:
                    for block in resp.iter_bytes():
                        fh.write(block)
        finally:
            if self.client is None:
                client.close()
        self.cache_path = path
        self._owned_cache = True
        return path

    def _open_text(self, path: Path) -> IO[str]:
        if self.url.endswith(".bz2"):
            return io.TextIOWrapper(bz2.open(path, "rb"), encoding="utf-8", newline="")
        if self.url.endswith(".gz"):
            return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8", newline="")
        return open(path, encoding="utf-8", newline="")

    def _iter_court_rows(self, fh: IO[str], court: str) -> Iterator[Mapping[str, Any]]:
        target = ids.slugify(court)
        for row in csv.DictReader(fh):
            raw = (row.get(self.court_field) or "").strip()
            if raw and ids.slugify(raw) == target:
                yield row

    def fetch_court_chunk(self, court: str, *, offset: int, limit: int) -> CourtChunk:
        path = self._ensure_local()
        rows: list[Mapping[str, Any]] = []
        reached_end = True
        with self._open_text(path) as fh:
            for i, row in enumerate(self._iter_court_rows(fh, court)):
                if i < offset:
                    continue
                if len(rows) >= limit:
                    reached_end = False
                    break
                rows.append(row)
        return CourtChunk(rows=rows, reached_end=reached_end)

    def cleanup(self) -> None:
        """Remove the downloaded cache file (only one this source created)."""
        if self._owned_cache and self.cache_path is not None:
            self.cache_path.unlink(missing_ok=True)
            self._owned_cache = False
