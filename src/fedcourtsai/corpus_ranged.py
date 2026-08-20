"""Read-only ranged access to the corpus blob on the S3 corpus remote.

The corpus blob is content-addressed on the remote, therefore **immutable**:
the committed ``corpus/corpus.db.ref`` pointer names one exact byte sequence
(``index/sha256/<digest>``), and a corpus update publishes a *new* object
rather than rewriting the old one — the remote is add-only (see
:mod:`fedcourtsai.corpus_remote`, the whole-file transport that publishes those
objects). That immutability is what makes remote reads safe without any
consistency machinery — a read-only SQLite VFS can translate page reads into
HTTP range requests against the object and never observe a torn write. A
consumer gets live query access with per-query egress in KBs instead of a
full-blob transfer.

Three seams, each swappable on its own:

* **Transport** — one callable ``(object key, inclusive byte range) -> bytes``.
  :class:`S3RangeTransport` (boto3 ranged ``GetObject``) is today's
  implementation; an S3-compatible endpoint or another blob store is a
  contained swap, and tests substitute an in-memory transport here. It is also
  the one seam where a *transient* remote fault is absorbed
  (:data:`RETRY_BACKOFF_SECONDS`) — a permanent one still fails immediately.
* **Resolver** — :func:`resolve_index_pointer` is the **only** place that knows
  the remote key layout. It maps a validated pointer (key + checksum + size),
  from either carrier, to the object's coordinates and fails loudly when the
  coupling breaks.
* **VFS** — a private apsw VFS serving ``xRead`` from block-aligned ranged GETs
  (:data:`BLOCK_SIZE` bytes) through an in-process LRU cache, with the file
  size taken from the pointer (no HEAD request) and every write/lock/journal
  operation rejected or a no-op per the read-only contract.

Reference implementations (both MIT): michalc/sqlite-s3-query and
litements/s3sqlite. Implemented in-repo rather than depended on — both are
effectively unmaintained single-file packages, and in-repo code passes this
project's gate (mypy strict, tests, review). apsw provides the typed VFS API;
no ctypes VFS registration, no hand-rolled SigV4 signing.
"""

from __future__ import annotations

import json
import random
import re
import sys
import time
from collections import OrderedDict
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Any, Protocol, cast

import apsw

# Ranged GETs are block-aligned at this size: large enough that a B-tree
# descent over 64 KB pages usually lands in one or two blocks, small enough
# that a point lookup stays KB-scale egress.
BLOCK_SIZE = 256 * 1024
# LRU capacity in blocks (16 MiB with the default block size): bounds memory
# while letting a work session's hot pages (schema, index roots) stay resident.
CACHE_BLOCKS = 64

_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_S3_URL_RE = re.compile(r"s3://(?P<bucket>[^/]+)/?(?P<prefix>.*)")

# The committed corpus-index pointer's filename suffix (JSON, beside the blob).
POINTER_SUFFIX = ".ref"
# The pointer schema this reader understands; bumped on incompatible reshapes.
POINTER_SCHEMA_VERSION = "1.0"
# Remote-prefix-relative home of the published index versions; the digest in
# the key is the object's own sha256, so the layout is self-verifying — and
# parse_index_pointer — the chokepoint both pointer carriers pass through —
# ENFORCES that (key must equal index/sha256/<sha256>), so
# a pointer can never route readers to an object other than the one whose
# digest it carries.
INDEX_KEY_PREFIX = "index/sha256"

# Pauses *between* ranged-GET attempts, so the attempt budget is one more than
# the number of pauses. Every predict cell provisions its own snapshot over
# this transport, so a single transient remote fault would otherwise refuse one
# engine's cell while its siblings on the same event predict.
# Fixed rather than configurable: the schedule is short enough to cost nothing
# when unused and bounded enough that a genuinely down remote still fails fast.
# This budget layers on top of botocore's own request-level retries (the
# client is built with the default retry config): the marginal value here is
# the faults botocore does not re-attempt — mid-body stream failures during
# Body.read() — plus one place that names the flake before giving up.
RETRY_BACKOFF_SECONDS = (0.2, 0.6)
# Fraction of each pause added as jitter, so cells that flaked on the same
# object do not resynchronise onto the next attempt together.
RETRY_JITTER = 0.25

# S3 error codes naming a transient server-side condition. Listed by name
# because S3 returns some of them (``RequestTimeout``) with a 4xx status; the
# rest of the 5xx family is caught by status instead.
_TRANSIENT_ERROR_CODES = frozenset(
    {"InternalError", "RequestTimeout", "ServiceUnavailable", "SlowDown"}
)

# Test seam: the pause between attempts, bound here so an offline test can
# replace it without touching the global clock.
_sleep = time.sleep

# Each connection registers its own uniquely-named VFS (state lives in the VFS
# instance); the counter keeps concurrent connections from colliding.
_vfs_names = count()


def _is_transient(exc: Any) -> bool:
    """Whether a failed ranged GET is worth another attempt.

    Deliberately an allowlist. A permanent fault — 403 from a role that cannot
    read the corpus remote, 404 from a drifted pointer, a redirect from the
    wrong region — is a misconfiguration, and smearing it over a retry budget
    turns a one-line diagnosis into a slow mystery. Only server-side
    transients and connection-level faults are retried. ``exc`` is untyped
    because botocore ships no type information, so its exception classes and
    their ``response`` payload are only known at runtime.
    """
    from botocore.exceptions import (  # noqa: PLC0415
        ClientError,
        HTTPClientError,
        IncompleteReadError,
    )
    from botocore.exceptions import (  # noqa: PLC0415
        ConnectionError as BotoConnectionError,
    )

    # The connection never got a usable HTTP response: timeouts, dropped and
    # closed connections, endpoint failures, truncated bodies.
    if isinstance(exc, BotoConnectionError | HTTPClientError | IncompleteReadError):
        return True
    if isinstance(exc, ClientError):
        response = exc.response
        if response.get("Error", {}).get("Code") in _TRANSIENT_ERROR_CODES:
            return True
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        return isinstance(status, int) and status >= 500
    return False


def _fault_summary(exc: Any) -> str:
    """A one-token account of a failed attempt, safe to print.

    Never the exception's message: connection-family messages embed the full
    endpoint URL (bucket included), and the remote's name must not reach a log
    or an error type that callers render. The class name — plus the S3 error
    code where one exists — is enough to count and classify flakes.
    """
    from botocore.exceptions import ClientError  # noqa: PLC0415

    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code")
        if isinstance(code, str) and code:
            return f"{type(exc).__name__}: {code}"
    return type(exc).__name__


class RangedBackendError(RuntimeError):
    """The ranged backend cannot serve — misconfigured remote, broken pointer,
    or a transient fault that survived the whole retry budget.

    Deliberately loud: every failure names what was expected so a drifted
    remote layout or missing out-of-band configuration is a diagnosis, not a
    mystery. A permanent per-request fault (403, 404) is *not* wrapped: callers
    that catch this type deliberately degrade, and a misconfigured remote must
    crash the caller instead of degrading into the unprovisioned path.
    """


class RangeTransport(Protocol):
    """The transport seam: fetch one inclusive byte range of one object.

    Everything above this seam (VFS, cache, resolver) is agnostic to what
    serves the bytes — swap the callable to change storage backends or to run
    offline tests.
    """

    def __call__(self, key: str, start: int, end: int) -> bytes: ...


class S3RangeTransport:
    """Ranged ``GetObject`` against S3 — today's transport implementation.

    Credentials and region come from the environment (the OIDC-assumed role in
    workflows, the developer's profile locally), exactly like the whole-file
    corpus transport and the casestore.

    A transient fault is retried on the :data:`RETRY_BACKOFF_SECONDS` schedule
    and each retry is announced on stderr, so the flake rate is countable from
    a run log; a permanent one propagates on the first attempt, and an
    exhausted budget becomes a :class:`RangedBackendError` naming the object,
    the range, and how many attempts were spent.
    """

    def __init__(self, bucket: str) -> None:
        # Deferred import: boto3 is heavyweight (hundreds of ms) and only a
        # connection that actually goes to S3 should pay it.
        import boto3  # noqa: PLC0415

        self._bucket = bucket
        self._client = boto3.client("s3")

    def __call__(self, key: str, start: int, end: int) -> bytes:
        byte_range = f"bytes={start}-{end}"
        attempts = len(RETRY_BACKOFF_SECONDS) + 1
        for attempt in range(1, attempts + 1):
            try:
                response = self._client.get_object(Bucket=self._bucket, Key=key, Range=byte_range)
                return bytes(response["Body"].read())
            except Exception as exc:
                if not _is_transient(exc):
                    raise
                if attempt == attempts:
                    raise RangedBackendError(
                        f"ranged read of {key} ({byte_range}) failed after "
                        f"{attempts} attempts: {_fault_summary(exc)}"
                    ) from exc
                pause = RETRY_BACKOFF_SECONDS[attempt - 1]
                pause += random.uniform(0.0, pause * RETRY_JITTER)
                # Printed rather than logged: only a line that *starts* with
                # the marker is annotated by the workflow runner, and the
                # ranged reader runs under callers with different (or no)
                # logging configuration. The exception is summarised, never
                # interpolated: connection-family messages embed the endpoint
                # URL, bucket included, and the remote's name is supplied out
                # of band and never committed or rendered — the key and range
                # are what identify the failed read.
                print(
                    f"::warning::ranged read of {key} ({byte_range}) attempt "
                    f"{attempt}/{attempts} failed ({_fault_summary(exc)}); "
                    f"retrying in {pause:.2f}s",
                    file=sys.stderr,
                    flush=True,
                )
                _sleep(pause)
        raise AssertionError("unreachable")  # pragma: no cover


@dataclass(frozen=True)
class RemoteObject:
    """The corpus blob resolved to its remote coordinates.

    ``checksum`` carries the pointer's sha256 so a whole-file download can
    verify what it fetched (see
    :func:`fedcourtsai.corpus_remote.download_index`).
    """

    bucket: str
    key: str
    size: int
    checksum: str  # the pointer's sha256, hex


@dataclass(frozen=True)
class IndexPointer:
    """A validated corpus index pointer's contents, whichever carrier held it.

    Parsed from the committed ``corpus/corpus.db.ref`` file or from the
    out-of-band override; ``key`` is remote-prefix-relative and content-addressed
    (``index/sha256/<digest>``), so every published version is immutable and
    the remote stays add-only; ``size`` rides along because the ranged reader
    serves ``xFileSize`` from the pointer, never a HEAD request.
    """

    key: str
    size: int
    sha256: str
    schema_version: str = POINTER_SCHEMA_VERSION

    def __post_init__(self) -> None:
        # The key<->digest binding is the type's own invariant, not only the
        # parser's: whatever constructs one of these — a parsed carrier, a
        # publish, a test — cannot hand the digest-blind ranged reader a key
        # its checksum does not vouch for.
        if _SHA256_RE.fullmatch(self.sha256) is None:
            raise RangedBackendError(f"index pointer carries no valid sha256: {self.sha256!r}")
        if self.key != f"{INDEX_KEY_PREFIX}/{self.sha256}":
            raise RangedBackendError(
                f"index pointer key {self.key!r} does not match its own sha256 "
                f"(expected {INDEX_KEY_PREFIX}/{self.sha256})"
            )
        if self.size <= 0:
            raise RangedBackendError(f"index pointer carries no positive size: {self.size!r}")


def parse_remote_url(remote_url: str) -> tuple[str, str]:
    """Split the corpus remote's ``s3://<bucket>[/<prefix>]`` URL, loudly."""
    url_match = _S3_URL_RE.fullmatch(remote_url)
    if url_match is None:
        raise RangedBackendError(
            f"corpus remote URL {remote_url!r} is not an s3://<bucket>[/<prefix>] URL"
        )
    return url_match["bucket"], url_match["prefix"].strip("/")


def find_pointer(db_path: Path) -> Path:
    """The committed ``.ref`` pointer beside ``db_path``, failing loudly when absent."""
    pointer = db_path.with_name(db_path.name + POINTER_SUFFIX)
    if pointer.is_file():
        return pointer
    raise RangedBackendError(f"no corpus pointer at {pointer} (is the repo checked out?)")


def parse_index_pointer(data: object, *, source: str) -> IndexPointer:
    """Validate decoded pointer content from any carrier, failing loudly.

    ``source`` names where the JSON came from — a committed ``.ref`` file or
    the out-of-band override — so every defect message stays a diagnosis
    rather than a confusing download failure later. Both carriers get exactly
    this validation, key↔digest binding included: no pointer, however
    supplied, can route the digest-blind ranged reader to an object its
    checksum does not vouch for.
    """
    if not isinstance(data, dict):
        raise RangedBackendError(f"corpus pointer {source} must be a JSON object")
    key = data.get("key")
    size = data.get("size")
    sha256 = data.get("sha256")
    schema_version = data.get("schema_version")
    if not isinstance(key, str) or not key:
        raise RangedBackendError(f"corpus pointer {source} carries no remote key")
    if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
        raise RangedBackendError(f"corpus pointer {source} carries no valid sha256 checksum")
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise RangedBackendError(f"corpus pointer {source} carries no positive size")
    if schema_version != POINTER_SCHEMA_VERSION:
        raise RangedBackendError(
            f"corpus pointer {source} has schema_version {schema_version!r}; "
            f"this reader understands {POINTER_SCHEMA_VERSION!r}"
        )
    # The key must be derived from the carried digest: a pointer whose key and
    # sha256 diverge could route the (digest-blind) ranged reader to a
    # different object than the one the checksum vouches for.
    if key != f"{INDEX_KEY_PREFIX}/{sha256}":
        raise RangedBackendError(
            f"corpus pointer {source} key {key!r} does not match its own "
            f"sha256 (expected {INDEX_KEY_PREFIX}/{sha256})"
        )
    return IndexPointer(key=key, size=size, sha256=sha256, schema_version=schema_version)


def read_index_pointer(pointer_path: Path) -> IndexPointer:
    """Parse and validate the committed JSON pointer file, failing loudly.

    Every defect names what was expected (the offline gate reuses this for its
    pointer well-formedness check), so a hand-edited or truncated pointer is a
    diagnosis, not a confusing download failure later.
    """
    if not pointer_path.is_file():
        raise RangedBackendError(f"no corpus pointer at {pointer_path} (is the repo checked out?)")
    try:
        data = json.loads(pointer_path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise RangedBackendError(f"corpus pointer {pointer_path} is not valid JSON: {exc}") from exc
    return parse_index_pointer(data, source=str(pointer_path))


# How error messages name the out-of-band pointer's origin (the env-supplied
# JSON, see ``Settings.corpus_pointer``) in place of a file path.
POINTER_OVERRIDE_SOURCE = "from the environment override"


def parse_pointer_override(value: str) -> IndexPointer:
    """Parse and validate the out-of-band pointer JSON, failing loudly.

    The env-supplied twin of :func:`read_index_pointer`: same schema, same
    validation, no file. It serves a corpus pair whose pointer is not
    committed (the staging pair — see *Developer access* in
    ``docs/data-pipeline.md``); read paths prefer it over the committed file
    when it is set.
    """
    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        raise RangedBackendError(
            f"corpus pointer {POINTER_OVERRIDE_SOURCE} is not valid JSON: {exc}"
        ) from exc
    return parse_index_pointer(data, source=POINTER_OVERRIDE_SOURCE)


def resolve_index_pointer(pointer: IndexPointer, remote_url: str) -> RemoteObject:
    """Map a validated pointer to the blob's bucket/key/size/checksum.

    The single place that knows the remote key layout: the pointer's
    content-addressed ``key`` joins directly under the remote prefix. Raises
    :class:`RangedBackendError` with a specific message on a malformed URL,
    so a layout change surfaces immediately.
    """
    bucket, prefix = parse_remote_url(remote_url)
    key = "/".join(part for part in (prefix, pointer.key) if part)
    return RemoteObject(bucket=bucket, key=key, size=pointer.size, checksum=pointer.sha256)


def resolve_pointer(pointer: Path | IndexPointer, remote_url: str) -> RemoteObject:
    """Resolve either pointer carrier against the remote.

    A committed ``.ref`` path is read and validated first; an
    :class:`IndexPointer` goes straight to :func:`resolve_index_pointer`.
    """
    if isinstance(pointer, Path):
        pointer = read_index_pointer(pointer)
    return resolve_index_pointer(pointer, remote_url)


@dataclass
class ReadStats:
    """Per-connection ranged-read counters, surfaced to callers via ``stats``."""

    gets: int = 0
    bytes_fetched: int = 0


class _BlockCache:
    """A small in-process LRU of fetched blocks, keyed by block index."""

    def __init__(self, capacity: int) -> None:
        self._capacity = capacity
        self._blocks: OrderedDict[int, bytes] = OrderedDict()

    def get(self, index: int) -> bytes | None:
        block = self._blocks.get(index)
        if block is not None:
            self._blocks.move_to_end(index)
        return block

    def put(self, index: int, block: bytes) -> None:
        self._blocks[index] = block
        self._blocks.move_to_end(index)
        while len(self._blocks) > self._capacity:
            self._blocks.popitem(last=False)


class _BlockReader:
    """Serve arbitrary reads of the remote object from block-aligned fetches."""

    def __init__(
        self,
        transport: RangeTransport,
        key: str,
        size: int,
        *,
        block_size: int,
        cache: _BlockCache,
        stats: ReadStats,
    ) -> None:
        self._transport = transport
        self._key = key
        self.size = size
        self._block_size = block_size
        self._cache = cache
        self.stats = stats

    def _block(self, index: int) -> bytes:
        cached = self._cache.get(index)
        if cached is not None:
            return cached
        start = index * self._block_size
        end = min(start + self._block_size, self.size) - 1
        block = self._transport(self._key, start, end)
        self.stats.gets += 1
        self.stats.bytes_fetched += len(block)
        self._cache.put(index, block)
        return block

    def read(self, amount: int, offset: int) -> bytes:
        if offset >= self.size or amount <= 0:
            return b""
        end = min(offset + amount, self.size)
        first, last = offset // self._block_size, (end - 1) // self._block_size
        parts: list[bytes] = []
        for index in range(first, last + 1):
            block = self._block(index)
            lo = offset - index * self._block_size if index == first else 0
            hi = end - index * self._block_size if index == last else len(block)
            parts.append(block[lo:hi])
        return b"".join(parts)


class _RangedFile:
    """The read-only file object the VFS hands SQLite for the main database.

    Locking is a no-op and ``xDeviceCharacteristics`` reports ``IMMUTABLE`` —
    the pointer names one content-addressed byte sequence, so there is no
    writer to coordinate with and no change to detect. Reads past EOF are
    zero-filled per SQLite's short-read semantics.
    """

    def __init__(self, reader: _BlockReader) -> None:
        self._reader = reader

    def xRead(self, amount: int, offset: int) -> bytes:
        data = self._reader.read(amount, offset)
        return data if len(data) == amount else data.ljust(amount, b"\0")

    def xFileSize(self) -> int:
        # From the committed pointer — the object is never HEADed.
        return self._reader.size

    def xLock(self, level: int) -> None:
        pass

    def xUnlock(self, level: int) -> None:
        pass

    def xCheckReservedLock(self) -> bool:
        return False

    def xFileControl(self, op: int, ptr: int) -> bool:
        return False

    def xSectorSize(self) -> int:
        return 4096

    def xDeviceCharacteristics(self) -> int:
        return apsw.SQLITE_IOCAP_IMMUTABLE

    def xSync(self, flags: int) -> None:
        pass

    def xWrite(self, data: bytes, offset: int) -> None:
        raise apsw.ReadOnlyError("the ranged corpus is read-only")

    def xTruncate(self, size: int) -> None:
        raise apsw.ReadOnlyError("the ranged corpus is read-only")

    def xClose(self) -> None:
        pass


class _RangedVFS(apsw.VFS):
    """A VFS serving exactly one immutable remote object as the main database."""

    def __init__(self, name: str, reader: _BlockReader) -> None:
        self._reader = reader
        # base="" inherits the default VFS for the ambient methods SQLite needs
        # (randomness, time, sleep); everything file-shaped is overridden below.
        super().__init__(name, base="")

    def xOpen(self, name: object, flags: list[int]) -> apsw.VFSFile:
        if not flags[0] & apsw.SQLITE_OPEN_MAIN_DB:
            # Journals/WAL never exist for an immutable read-only object.
            raise apsw.CantOpenError("the ranged VFS serves only the main database")
        flags[1] = flags[0]
        # apsw accepts any object with the file methods; the stubs insist on
        # the VFSFile class, whose __init__ would open a real OS file.
        return cast(apsw.VFSFile, _RangedFile(self._reader))

    def xAccess(self, pathname: str, flags: int) -> bool:
        return False

    def xFullPathname(self, name: str) -> str:
        return name

    def xDelete(self, name: str, syncdir: bool) -> None:
        raise apsw.ReadOnlyError("the ranged corpus is read-only")


class Row:
    """A ``sqlite3.Row``-alike: index by column name or position.

    The corpus deserializers index records by column name; apsw yields plain
    tuples, so the connection installs a row trace that wraps each row in this.
    """

    __slots__ = ("_names", "_values")

    def __init__(self, names: dict[str, int], values: tuple[Any, ...]) -> None:
        self._names = names
        self._values = values

    def __getitem__(self, key: str | int) -> Any:
        return self._values[self._names[key] if isinstance(key, str) else key]

    def keys(self) -> list[str]:
        return list(self._names)

    def __len__(self) -> int:
        return len(self._values)


class RangedConnection:
    """The read-only connection the ranged backend yields.

    Satisfies the corpus read seam (``execute`` returning name-indexable rows)
    so the retrieval and provisioning helpers run unchanged; ``stats`` carries
    the per-connection GET count and bytes fetched for retrieval logging.
    """

    def __init__(self, connection: apsw.Connection, stats: ReadStats) -> None:
        self._connection = connection
        self.stats = stats

    def execute(self, sql: str, parameters: Sequence[Any] = (), /) -> apsw.Cursor:
        cursor = self._connection.cursor()

        def _trace(cursor: apsw.Cursor, values: tuple[Any, ...]) -> Row:
            names = {description[0]: i for i, description in enumerate(cursor.description)}
            return Row(names, values)

        cursor.row_trace = _trace
        return cursor.execute(sql, tuple(parameters))

    def close(self) -> None:
        self._connection.close()


@contextmanager
def connect_ranged(
    pointer: Path | IndexPointer,
    remote_url: str,
    *,
    transport: RangeTransport | None = None,
    block_size: int = BLOCK_SIZE,
) -> Iterator[RangedConnection]:
    """Open the corpus blob the pointer names for read-only remote queries.

    Resolves ``pointer`` — a committed ``.ref`` path, or an
    :class:`IndexPointer` already validated from the out-of-band override —
    against ``remote_url`` (see :func:`resolve_pointer`), registers a
    connection-private VFS, and yields a :class:`RangedConnection`.
    ``transport`` defaults to :class:`S3RangeTransport` against the resolved
    bucket; tests pass an offline stand-in (and may shrink ``block_size`` so
    request-count assertions stay meaningful on a small fixture).
    """
    remote = resolve_pointer(pointer, remote_url)
    reader = _BlockReader(
        transport if transport is not None else S3RangeTransport(remote.bucket),
        remote.key,
        remote.size,
        block_size=block_size,
        cache=_BlockCache(CACHE_BLOCKS),
        stats=ReadStats(),
    )
    vfs_name = f"fedcourts-ranged-{next(_vfs_names)}"
    vfs = _RangedVFS(vfs_name, reader)
    # The SQLite connection needs a db *name*; a file-borne pointer supplies
    # it, an env-borne one has no filename so the canonical name stands in.
    if isinstance(pointer, Path):
        db_name = pointer.name.removesuffix(POINTER_SUFFIX)
    else:
        db_name = "corpus.db"
    try:
        connection = apsw.Connection(
            db_name,
            flags=apsw.SQLITE_OPEN_READONLY,
            vfs=vfs_name,
        )
        try:
            yield RangedConnection(connection, reader.stats)
        finally:
            connection.close()
    finally:
        vfs.unregister()
