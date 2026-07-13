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
  contained swap, and tests substitute an in-memory transport here.
* **Resolver** — :func:`resolve_pointer` is the **only** place that knows the
  remote key layout. It maps the committed pointer (key + checksum + size) to
  the object's coordinates and fails loudly when the coupling breaks. For one
  transition cycle it also resolves the legacy DVC pointer
  (``corpus/corpus.db.dvc``, md5 cache layout) so a checkout that predates the
  ``.ref`` pointer still reads; the legacy branch goes away with the shim.
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
import re
from collections import OrderedDict
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Any, Protocol, cast

import apsw
import yaml

# Ranged GETs are block-aligned at this size: large enough that a B-tree
# descent over 64 KB pages usually lands in one or two blocks, small enough
# that a point lookup stays KB-scale egress.
BLOCK_SIZE = 256 * 1024
# LRU capacity in blocks (16 MiB with the default block size): bounds memory
# while letting a work session's hot pages (schema, index roots) stay resident.
CACHE_BLOCKS = 64

_MD5_RE = re.compile(r"[0-9a-f]{32}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_S3_URL_RE = re.compile(r"s3://(?P<bucket>[^/]+)/?(?P<prefix>.*)")

# The committed corpus-index pointer's filename suffixes: the JSON pointer is
# primary; the DVC-era YAML pointer is honored for one transition cycle (the
# shim) so a checkout that predates the `.ref` pointer still resolves.
POINTER_SUFFIX = ".ref"
LEGACY_POINTER_SUFFIX = ".dvc"
# The pointer schema this reader understands; bumped on incompatible reshapes.
POINTER_SCHEMA_VERSION = "1.0"
# Remote-prefix-relative home of the published index versions; the digest in
# the key is the object's own sha256, so the layout is self-verifying — and
# read_index_pointer ENFORCES that (key must equal index/sha256/<sha256>), so
# a pointer can never route readers to an object other than the one whose
# digest it carries.
INDEX_KEY_PREFIX = "index/sha256"

# Each connection registers its own uniquely-named VFS (state lives in the VFS
# instance); the counter keeps concurrent connections from colliding.
_vfs_names = count()


class RangedBackendError(RuntimeError):
    """The ranged backend cannot serve — misconfigured remote or broken pointer.

    Deliberately loud: every failure names what was expected so a drifted
    remote layout or missing out-of-band configuration is a diagnosis, not a
    mystery.
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
    """

    def __init__(self, bucket: str) -> None:
        # Deferred import: boto3 is heavyweight (hundreds of ms) and only a
        # connection that actually goes to S3 should pay it.
        import boto3  # noqa: PLC0415

        self._bucket = bucket
        self._client = boto3.client("s3")

    def __call__(self, key: str, start: int, end: int) -> bytes:
        response = self._client.get_object(
            Bucket=self._bucket, Key=key, Range=f"bytes={start}-{end}"
        )
        return bytes(response["Body"].read())


@dataclass(frozen=True)
class RemoteObject:
    """The corpus blob resolved to its remote coordinates.

    ``checksum``/``checksum_algorithm`` carry the pointer's content identity —
    sha256 from the ``.ref`` pointer, md5 from the legacy shim — so a
    whole-file download can verify what it fetched (see
    :func:`fedcourtsai.corpus_remote.download_index`).
    """

    bucket: str
    key: str
    size: int
    checksum: str
    checksum_algorithm: str  # "sha256" (.ref pointer) or "md5" (legacy shim)


@dataclass(frozen=True)
class IndexPointer:
    """The committed ``corpus/corpus.db.ref`` pointer's contents.

    ``key`` is remote-prefix-relative and content-addressed
    (``index/sha256/<digest>``), so every published version is immutable and
    the remote stays add-only; ``size`` rides along because the ranged reader
    serves ``xFileSize`` from the pointer, never a HEAD request.
    """

    key: str
    size: int
    sha256: str
    schema_version: str = POINTER_SCHEMA_VERSION


def parse_remote_url(remote_url: str) -> tuple[str, str]:
    """Split the corpus remote's ``s3://<bucket>[/<prefix>]`` URL, loudly."""
    url_match = _S3_URL_RE.fullmatch(remote_url)
    if url_match is None:
        raise RangedBackendError(
            f"corpus remote URL {remote_url!r} is not an s3://<bucket>[/<prefix>] URL"
        )
    return url_match["bucket"], url_match["prefix"].strip("/")


def find_pointer(db_path: Path) -> Path:
    """The committed pointer beside ``db_path``: ``.ref``, else the legacy ``.dvc``.

    The legacy fallback exists for one transition cycle only, so a checkout
    that predates the ``.ref`` pointer (or a writer's very first run after the
    cutover) still resolves; it is deleted together with the shim.
    """
    pointer = db_path.with_name(db_path.name + POINTER_SUFFIX)
    if pointer.is_file():
        return pointer
    legacy = db_path.with_name(db_path.name + LEGACY_POINTER_SUFFIX)
    if legacy.is_file():
        return legacy
    raise RangedBackendError(
        f"no corpus pointer at {pointer} (nor legacy {legacy}); is the repo checked out?"
    )


def read_index_pointer(pointer_path: Path) -> IndexPointer:
    """Parse and validate the committed JSON pointer, failing loudly.

    Every defect names what was expected (the offline gate reuses this for its
    pointer well-formedness check), so a hand-edited or truncated pointer is a
    diagnosis, not a confusing download failure later.
    """
    if not pointer_path.is_file():
        raise RangedBackendError(f"no corpus pointer at {pointer_path} (is the repo checked out?)")
    try:
        pointer = json.loads(pointer_path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise RangedBackendError(f"corpus pointer {pointer_path} is not valid JSON: {exc}") from exc
    if not isinstance(pointer, dict):
        raise RangedBackendError(f"corpus pointer {pointer_path} must be a JSON object")
    key = pointer.get("key")
    size = pointer.get("size")
    sha256 = pointer.get("sha256")
    schema_version = pointer.get("schema_version")
    if not isinstance(key, str) or not key:
        raise RangedBackendError(f"corpus pointer {pointer_path} carries no remote key")
    if not isinstance(sha256, str) or _SHA256_RE.fullmatch(sha256) is None:
        raise RangedBackendError(f"corpus pointer {pointer_path} carries no valid sha256 checksum")
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise RangedBackendError(f"corpus pointer {pointer_path} carries no positive size")
    if schema_version != POINTER_SCHEMA_VERSION:
        raise RangedBackendError(
            f"corpus pointer {pointer_path} has schema_version {schema_version!r}; "
            f"this reader understands {POINTER_SCHEMA_VERSION!r}"
        )
    # The key must be derived from the carried digest: a pointer whose key and
    # sha256 diverge could route the (digest-blind) ranged reader to a
    # different object than the one the checksum vouches for.
    if key != f"{INDEX_KEY_PREFIX}/{sha256}":
        raise RangedBackendError(
            f"corpus pointer {pointer_path} key {key!r} does not match its own "
            f"sha256 (expected {INDEX_KEY_PREFIX}/{sha256})"
        )
    return IndexPointer(key=key, size=size, sha256=sha256, schema_version=schema_version)


def resolve_pointer(pointer_path: Path, remote_url: str) -> RemoteObject:
    """Map the committed pointer to the blob's bucket/key/size/checksum.

    The single place that knows the remote key layout. The primary format is
    the JSON ``.ref`` pointer, whose content-addressed ``key`` joins directly
    under the remote prefix; a ``.dvc`` pointer takes the legacy branch for
    one transition cycle. Raises :class:`RangedBackendError` with a specific
    message on any mismatch, so a layout change or a malformed pointer
    surfaces immediately.
    """
    bucket, prefix = parse_remote_url(remote_url)
    if pointer_path.name.endswith(LEGACY_POINTER_SUFFIX):
        return _resolve_legacy_pointer(pointer_path, bucket, prefix)
    pointer = read_index_pointer(pointer_path)
    key = "/".join(part for part in (prefix, pointer.key) if part)
    return RemoteObject(
        bucket=bucket,
        key=key,
        size=pointer.size,
        checksum=pointer.sha256,
        checksum_algorithm="sha256",
    )


def _resolve_legacy_pointer(pointer_path: Path, bucket: str, prefix: str) -> RemoteObject:
    """Resolve the DVC-era YAML pointer against DVC's md5 cache layout.

    Transition shim, kept for one cycle: it maps the legacy pointer's md5 +
    size to ``<prefix>/files/md5/<first two md5 hex chars>/<rest>`` so a
    checkout that predates ``corpus.db.ref`` still reads. Deleted together
    with the committed ``.dvc`` file once every consumer is on the JSON
    pointer.
    """
    if not pointer_path.is_file():
        raise RangedBackendError(f"no corpus pointer at {pointer_path} (is the repo checked out?)")
    try:
        pointer = yaml.safe_load(pointer_path.read_text())
    except yaml.YAMLError as exc:
        raise RangedBackendError(
            f"legacy DVC pointer {pointer_path} is not valid YAML: {exc}"
        ) from exc
    outs = pointer.get("outs") if isinstance(pointer, dict) else None
    if not isinstance(outs, list) or len(outs) != 1 or not isinstance(outs[0], dict):
        raise RangedBackendError(
            f"legacy DVC pointer {pointer_path} must declare exactly one out; "
            "cannot resolve the blob"
        )
    md5 = outs[0].get("md5")
    size = outs[0].get("size")
    if not isinstance(md5, str) or _MD5_RE.fullmatch(md5) is None:
        raise RangedBackendError(f"legacy DVC pointer {pointer_path} carries no valid md5 checksum")
    if not isinstance(size, int) or size <= 0:
        raise RangedBackendError(f"legacy DVC pointer {pointer_path} carries no positive size")
    parts = [prefix, "files", "md5", md5[:2], md5[2:]]
    key = "/".join(part for part in parts if part)
    return RemoteObject(bucket=bucket, key=key, size=size, checksum=md5, checksum_algorithm="md5")


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
    pointer_path: Path,
    remote_url: str,
    *,
    transport: RangeTransport | None = None,
    block_size: int = BLOCK_SIZE,
) -> Iterator[RangedConnection]:
    """Open the corpus blob the pointer names for read-only remote queries.

    Resolves ``pointer_path`` against ``remote_url`` (see
    :func:`resolve_pointer`), registers a connection-private VFS, and yields a
    :class:`RangedConnection`. ``transport`` defaults to
    :class:`S3RangeTransport` against the resolved bucket; tests pass an
    offline stand-in (and may shrink ``block_size`` so request-count
    assertions stay meaningful on a small fixture).
    """
    remote = resolve_pointer(pointer_path, remote_url)
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
    db_name = pointer_path.name
    for suffix in (POINTER_SUFFIX, LEGACY_POINTER_SUFFIX):
        db_name = db_name.removesuffix(suffix)
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
