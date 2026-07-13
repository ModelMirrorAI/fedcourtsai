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
from pathlib import Path
from typing import Protocol

from .corpus_ranged import (
    INDEX_KEY_PREFIX,
    POINTER_SUFFIX,
    IndexPointer,
    RemoteObject,
    parse_remote_url,
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


def digest_file(path: Path) -> tuple[str, int]:
    """``(sha256 hex digest, byte size)`` of ``path``, streamed in bounded memory."""
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as fh:
        while chunk := fh.read(_CHUNK_BYTES):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


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
    pointer_path: Path,
    remote_url: str,
    dest: Path,
    *,
    transport: WholeFileTransport | None = None,
) -> RemoteObject:
    """Fetch the blob the pointer names into ``dest``, sha256-verified.

    Downloads to a sibling ``.partial`` file, verifies digest + size, then
    renames into place — a failed or corrupted transfer never leaves a
    plausible-looking corpus file behind.
    """
    remote = resolve_pointer(pointer_path, remote_url)
    active = transport if transport is not None else S3FileTransport(remote.bucket)
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(dest.name + ".partial")
    try:
        active.download(remote.key, partial)
        digest, size = digest_file(partial)
        if size != remote.size or digest != remote.checksum:
            raise CorpusRemoteError(
                f"downloaded corpus index does not match the pointer {pointer_path}: "
                f"got sha256 {digest} ({size} bytes), "
                f"expected {remote.checksum} ({remote.size} bytes)"
            )
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    partial.replace(dest)
    return remote
