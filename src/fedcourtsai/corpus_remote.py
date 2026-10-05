"""Whole-file transport for the corpus index blob on the S3 corpus remote.

The corpus index (``corpus/corpus.db``) lives in a private S3 bucket; only the
small committed pointer (``corpus/corpus.db.ref``, JSON) names which exact
bytes a checkout reads. This module is the write/pull side of that contract —
the counterpart to :mod:`fedcourtsai.corpus_ranged`, which serves in-place
ranged reads from the same pointer:

* :func:`upload_index` publishes the blob at a **content-addressed** key
  (``<prefix>/index/sha256/<digest>``) and rewrites the pointer. Every
  published version is a new object, never an overwrite, so the remote is
  add-only (the read-write role grants no delete) and each version is
  immutable — the invariant the ranged reader's consistency-free design
  rests on.
* :func:`download_index` fetches the object the pointer names and verifies its
  sha256 + size before the file lands, failing loudly on any mismatch — a
  truncated or corrupted transfer can never masquerade as the corpus.
* :func:`local_blob_drift` and :func:`upstream_pointer` are the read-only
  checks behind a pulled blob's vintage: whether its bytes still match the
  pointer it came from (stat and hash only, settled from the pull sidecar's
  timestamp unless the blob was touched since), and whether the checkout's
  committed pointer differs from ``origin/main``'s (a ``git show`` against the
  local object store, no network).

Credentials and region come from the environment (the OIDC-assumed role in
workflows, the developer's profile locally), exactly like the ranged reader
and the casestore. The transport seam keeps boto3 out of unit tests; it is
deliberately whole-file (``upload_file``/``download_file``, streaming, no
in-memory bodies) rather than the casestore's small-object ``put``/``get``
protocol — the index blob is ~1 GB.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .corpus_ranged import (
    INDEX_KEY_PREFIX,
    POINTER_OVERRIDE_SOURCE,
    POINTER_SUFFIX,
    IndexPointer,
    RangedBackendError,
    RemoteObject,
    parse_index_pointer,
    parse_remote_url,
    read_index_pointer,
    resolve_pointer,
)

# Streaming digest/copy chunk size — bounded memory over a ~1 GB blob.
_CHUNK_BYTES = 8 * 1024 * 1024


class CorpusRemoteError(RuntimeError):
    """A corpus-remote transport or verification problem, surfaced with context."""


class WholeFileTransport(Protocol):
    """The whole-file transport seam: move one object between disk and the remote.

    Everything above this (content addressing, verification, the pointer) is
    agnostic to what stores the bytes — tests inject an in-memory fake, and an
    S3-compatible endpoint is a contained swap. Keys are bucket-absolute.
    """

    def upload(self, key: str, source: Path) -> None: ...

    def download(self, key: str, dest: Path) -> None: ...

    def exists(self, key: str) -> bool: ...


class S3FileTransport:
    """Streaming ``upload_file``/``download_file`` against S3.

    boto3's managed transfer handles multipart + retries for the ~1 GB blob;
    nothing is buffered in memory.
    """

    def __init__(self, bucket: str) -> None:
        # Deferred import: boto3 is heavyweight and only a transport that
        # actually goes to S3 should pay for it (matches S3RangeTransport).
        import boto3  # noqa: PLC0415
        from boto3.exceptions import Boto3Error  # noqa: PLC0415
        from botocore.exceptions import BotoCoreError, ClientError  # noqa: PLC0415

        self._bucket = bucket
        self._client = boto3.client("s3")
        self._ClientError = ClientError
        # Everything a failed transfer can raise (upload_file wraps its cause
        # in boto3's S3UploadFailedError, not ClientError), so callers see one
        # loud, contextual CorpusRemoteError instead of a raw traceback.
        self._transport_errors: tuple[type[Exception], ...] = (
            ClientError,
            BotoCoreError,
            Boto3Error,
        )

    def upload(self, key: str, source: Path) -> None:
        try:
            self._client.upload_file(str(source), self._bucket, key)
        except self._transport_errors as exc:
            raise CorpusRemoteError(f"upload of {key} failed: {exc}") from exc

    def download(self, key: str, dest: Path) -> None:
        try:
            self._client.download_file(self._bucket, key, str(dest))
        except self._transport_errors as exc:
            raise CorpusRemoteError(f"download of {key} failed: {exc}") from exc

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except self._ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code in {"NoSuchKey", "NotFound", "404"}:
                return False
            if code in {"AccessDenied", "403"}:
                # Without s3:ListBucket, HeadObject on an ABSENT key returns
                # 403, not 404. Treat it as "unknown": on an add-only,
                # content-addressed remote, put-if-absent safely degrades to
                # put-always (an existing digest key already holds identical
                # bytes), so uploading is always correct.
                return False
            raise CorpusRemoteError(f"existence check of {key} failed: {exc}") from exc
        except self._transport_errors as exc:
            raise CorpusRemoteError(f"existence check of {key} failed: {exc}") from exc
        return True


def pointer_path_for(db_path: Path) -> Path:
    """The committed JSON pointer's location beside the index blob."""
    return db_path.with_name(db_path.name + POINTER_SUFFIX)


def pulled_pointer_path_for(db_path: Path) -> Path:
    """The pull-provenance sidecar's location beside the index blob.

    Gitignored, written by every ``corpus-pull``: which pointer the blob on
    disk actually came from. The override is process-scoped but the file it
    pulls is durable, so without this record a blob pulled through the
    override would read as the committed pointer's in every later shell.
    """
    return db_path.with_name(db_path.name + ".pulled" + POINTER_SUFFIX)


def digest_file(path: Path) -> tuple[str, int]:
    """``(sha256 hex digest, byte size)`` of ``path``, streamed in bounded memory."""
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as fh:
        while chunk := fh.read(_CHUNK_BYTES):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


@dataclass(frozen=True)
class BlobDrift:
    """A local blob whose bytes no longer match the pointer it was pulled from.

    ``pointer_source`` names the record the expected digest came from — the
    pull-provenance sidecar, or the committed ``.ref`` when no pull recorded
    one — so the report says which claim the bytes broke.
    """

    pointer_sha256: str
    pointer_source: Path
    on_disk_sha256: str


def local_blob_drift(db_path: Path) -> BlobDrift | None:
    """The drift between the blob on disk and its pointer, or ``None`` when it matches.

    A pull lands a sha256-verified blob, but a default local read migrates the
    file in place (``corpus.connect``), after which its bytes are no longer the
    ones any pointer names and a vintage quoted from it describes a blob that
    exists nowhere else. The expected digest is the pull-provenance sidecar's
    — the pointer the blob actually came from — else the committed ``.ref``.
    A blob matching the committed ref is not drift either: ``corpus-push``
    publishes the blob on disk and rewrites the ref, leaving the sidecar behind.

    Hashing a ~1 GB blob costs seconds, so the sidecar's timestamp stands in
    for the digest where it can: the pull writes the sidecar only after the
    verified blob is in place, so a blob of the pointer's size last modified
    strictly *before* its sidecar is still the verified pull. Anything else —
    a blob modified at or after the pull, a size that differs, no sidecar to
    time against — is settled by the digest. ``None`` too when there is no blob
    or no readable pointer to compare against: nothing can be claimed then.
    """
    if not db_path.is_file():
        return None
    pulled_path = pulled_pointer_path_for(db_path)
    committed_path = pointer_path_for(db_path)
    committed: IndexPointer | None = None
    try:
        if committed_path.is_file():
            committed = read_index_pointer(committed_path)
        expected = read_index_pointer(pulled_path) if pulled_path.is_file() else committed
    except RangedBackendError:
        return None
    if expected is None:
        return None
    record = pulled_path if pulled_path.is_file() else committed_path
    blob = db_path.stat()
    if (
        record == pulled_path
        and blob.st_size == expected.size
        and blob.st_mtime_ns < pulled_path.stat().st_mtime_ns
    ):
        return None
    sha256, _ = digest_file(db_path)
    if sha256 == expected.sha256 or (committed is not None and sha256 == committed.sha256):
        return None
    return BlobDrift(pointer_sha256=expected.sha256, pointer_source=record, on_disk_sha256=sha256)


#: The ref whose committed pointer a checkout's own is compared against: the
#: production pointer, which the deterministic writers advance on ``main``.
UPSTREAM_POINTER_REF = "origin/main"


def upstream_pointer(db_path: Path, ref: str = UPSTREAM_POINTER_REF) -> IndexPointer | None:
    """The pointer ``ref`` commits beside ``db_path``, read from the local object store.

    ``git show <ref>:./<pointer>`` reads only what the last fetch brought in —
    no network — so it answers "has this checkout's pointer fallen behind the
    production one, as far as this clone knows". ``None`` whenever it cannot
    answer: no git, not a repository, ``ref`` never fetched, or a pointer the
    ref does not carry or that does not parse.
    """
    pointer_name = pointer_path_for(db_path).name
    try:
        proc = subprocess.run(
            ["git", "-C", str(db_path.parent), "show", f"{ref}:./{pointer_name}"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        return parse_index_pointer(json.loads(proc.stdout), source=f"{ref}:{pointer_name}")
    except (json.JSONDecodeError, RangedBackendError):
        return None


def write_pointer(pointer_path: Path, pointer: IndexPointer) -> None:
    """Write the committed pointer as deterministic JSON (minimal diffs)."""
    payload = {
        "key": pointer.key,
        "size": pointer.size,
        "sha256": pointer.sha256,
        "schema_version": pointer.schema_version,
    }
    pointer_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def upload_index(
    db_path: Path, remote_url: str, *, transport: WholeFileTransport | None = None
) -> IndexPointer:
    """Publish ``db_path`` to its content-addressed key and rewrite the pointer.

    Put-if-absent: the key embeds the blob's own sha256, so an existing object
    already holds identical bytes and a re-push uploads nothing. The blob goes
    up **before** the pointer file is (re)written, mirroring the workflows'
    push-blob-before-commit-pointer ordering — a committed pointer must always
    resolve against the remote. Returns the pointer that was written.
    """
    if not db_path.is_file():
        raise CorpusRemoteError(f"no corpus index at {db_path}; nothing to push")
    bucket, prefix = parse_remote_url(remote_url)
    sha256, size = digest_file(db_path)
    relative_key = f"{INDEX_KEY_PREFIX}/{sha256}"
    key = "/".join(part for part in (prefix, relative_key) if part)
    active = transport if transport is not None else S3FileTransport(bucket)
    if not active.exists(key):
        active.upload(key, db_path)
    pointer = IndexPointer(key=relative_key, size=size, sha256=sha256)
    write_pointer(pointer_path_for(db_path), pointer)
    return pointer


def download_index(
    pointer: Path | IndexPointer,
    remote_url: str,
    dest: Path,
    *,
    transport: WholeFileTransport | None = None,
) -> RemoteObject:
    """Fetch the blob the pointer names into ``dest``, sha256-verified.

    ``pointer`` is a committed ``.ref`` path or an :class:`IndexPointer`
    already validated from the out-of-band override. Downloads to a sibling
    ``.partial`` file, verifies digest + size, then renames into place — a
    failed or corrupted transfer never leaves a plausible-looking corpus file
    behind.
    """
    remote = resolve_pointer(pointer, remote_url)
    active = transport if transport is not None else S3FileTransport(remote.bucket)
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + ".partial")
    try:
        active.download(remote.key, partial)
        digest, size = digest_file(partial)
        if size != remote.size or digest != remote.checksum:
            source = pointer if isinstance(pointer, Path) else POINTER_OVERRIDE_SOURCE
            raise CorpusRemoteError(
                f"downloaded corpus index does not match the pointer {source}: "
                f"got sha256 {digest} ({size} bytes), "
                f"expected {remote.checksum} ({remote.size} bytes)"
            )
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    partial.replace(dest)
    return remote
