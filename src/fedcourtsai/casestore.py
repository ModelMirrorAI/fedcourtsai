"""Write-once, browsable per-case content object store (corpus split, phase 1).

The corpus is a single ~1 GB SQLite blob that commingles two things with very
different lifetimes: tiny, mutated-every-run metadata (the scannable ``cases``
columns, scope, cursors) and huge, write-once bulk payloads (dated snapshots and
extracted document text). Because the index transport content-addresses the
*whole* file and a writer re-pushes it every run, the remote accumulates a
fresh ~1 GB object per run regardless of how few cases changed.

This module is the first step of splitting that blob: it stages each case's bulk
payloads as **browsable per-case objects** in S3, mirroring the git ledger's
``data/cases/<court>/<docket>/`` shape (see :mod:`fedcourtsai.paths`) so a human
can ``aws s3 ls`` a case and read its story. Only *changed* cases upload, so
storage scales with real case churn rather than run count.

Layout (under the configured ``s3://<bucket>/<prefix>``)::

    <court>/<docket_id>/
        case.json                              # the CorpusRow (facts + our tracking)
        events.json                            # the case's CorpusEvent list
        snapshots/<YYYY-MM-DD>.json            # dated point-in-time docket payload
        documents/documents.json               # manifest: kind -> current text leaf
        documents/<kind>/<YYYY-MM-DD>-<digest>.txt   # extracted text (content-addressed leaf)

**Write-once discipline.** Bulk content objects are never overwritten in place, so
"what did a cell see?" stays reproducible: document text leaves are
content-addressed (a superseding brief lands at a *new* key), and dated snapshots
are naturally immutable per day. ``case.json`` / ``events.json`` /
``documents.json`` are small mutable manifests overwritten as the case evolves —
S3 object versioning retains their history, and a consumer pins the exact content
it read via the recorded object key + digest (:class:`ObjectRef`). The store is
therefore append-friendly: it fits the read-write role's no-delete posture (see
SECURITY.md) — a mutable manifest is a new *version*, never a delete.

**Ours/theirs boundary is unchanged.** Everything staged here is CourtListener /
supremecourt.gov-derived raw fact, so it lives only in the access-gated bucket,
never public git — exactly as the SQLite corpus does today (see
docs/data-sources.md).

Phase 1 dual-writes: the four corpus write seams (:func:`fedcourtsai.corpus`
``upsert_rows`` / ``upsert_snapshot`` / ``upsert_documents`` / ``upsert_events``)
mirror here through the best-effort ``mirror_*`` helpers, reached via a single
process transport (:func:`active_transport`) so activation is purely the env flag
with no writer signature threading. It stays **gated on ``FEDCOURTS_CASESTORE_URL``**
(unset → :func:`active_transport` is ``None`` → every mirror call is a pure no-op,
the default and the state in every test that does not opt in) — so with the flag
off the pipeline is byte-for-byte unchanged, and a mirror failure with the flag on
only logs (it never breaks the SQLite write that is the phase-1 system of record).
``set_event_resolved`` also re-mirrors, so a resolved event's ``events.json`` stays
current. **Known gap:** the direct-``UPDATE`` writers on ``cases`` columns — scope
reconcile (``set_predict_excluded`` / ``normalize_predict_eligible``) and
``backfill_live_signals`` — are *not* mirrored, so ``case.json`` can lag the corpus
until the case is next re-ingested. Provisioning does not read ``case.json`` (only
snapshot/documents/events), so this does not affect the phase-3 casestore
provisioning parity; a later phase that builds the index from the store will close
it.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Protocol

from .config import get_settings
from .corpus import (
    CaseDocument,
    CorpusEvent,
    CorpusRow,
    ReadConnection,
    documents_for_case,
    events_for_case,
    set_mirror_sink,
    set_payload_read_source,
)

logger = logging.getLogger(__name__)

# Bucket-relative default prefix; ``v1`` namespaces the layout so a later
# incompatible reshape can land beside it rather than migrate in place.
DEFAULT_PREFIX = "casestore/v1"

_S3_URL_RE = re.compile(r"s3://(?P<bucket>[^/]+)(?:/(?P<prefix>.+?))?/*$")
# The short content digest that makes a document text leaf's key unique per
# distinct content (a superseding filing lands at a new key, never overwriting).
_LEAF_DIGEST_CHARS = 12


class CasestoreError(RuntimeError):
    """A casestore configuration or transport problem, surfaced with context."""


# --- transport seam -----------------------------------------------------------


class ObjectTransport(Protocol):
    """The whole-object transport seam, mirroring corpus_ranged's range seam.

    Everything above this (key layout, serialization, mirroring) is agnostic to
    what stores the bytes — swap the implementation for S3, or the in-memory one
    to run offline tests.
    """

    def put(self, key: str, body: bytes, *, if_absent: bool = False) -> None:
        """Store ``body`` at ``key``. When ``if_absent`` and the key already
        holds an object, skip the write (the leaf is content-addressed, so an
        existing key already holds identical bytes)."""

    def get(self, key: str) -> bytes | None:
        """The object at ``key``, or ``None`` if it does not exist."""

    def exists(self, key: str) -> bool:
        """Whether an object exists at ``key``."""

    def list_keys(self, prefix: str) -> list[str]:
        """Every stored key beginning with ``prefix`` (used to find the latest
        dated snapshot under a case's ``snapshots/`` — needs ``s3:ListBucket``)."""
        ...


class InMemoryObjectTransport:
    """A dict-backed transport for tests (no network, no boto3)."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.puts = 0

    def put(self, key: str, body: bytes, *, if_absent: bool = False) -> None:
        if if_absent and key in self.objects:
            return
        self.objects[key] = body
        self.puts += 1

    def get(self, key: str) -> bytes | None:
        return self.objects.get(key)

    def exists(self, key: str) -> bool:
        return key in self.objects

    def list_keys(self, prefix: str) -> list[str]:
        return [key for key in self.objects if key.startswith(prefix)]


class S3ObjectTransport:
    """Whole-object ``PutObject`` / ``GetObject`` against S3.

    Credentials and region come from the environment (the OIDC-assumed role in
    workflows, the developer's profile locally), exactly like the ranged reader
    and the whole-file corpus transport.
    """

    def __init__(self, bucket: str, *, prefix: str = "") -> None:
        # Deferred import: boto3 is heavyweight and only a transport that
        # actually goes to S3 should pay for it (matches S3RangeTransport).
        import boto3  # noqa: PLC0415
        from botocore.exceptions import ClientError  # noqa: PLC0415

        self._bucket = bucket
        self._prefix = prefix.strip("/")
        self._client = boto3.client("s3")
        self._ClientError = ClientError

    def _full_key(self, key: str) -> str:
        return f"{self._prefix}/{key}" if self._prefix else key

    def put(self, key: str, body: bytes, *, if_absent: bool = False) -> None:
        if if_absent and self.exists(key):
            return
        self._client.put_object(Bucket=self._bucket, Key=self._full_key(key), Body=body)

    def get(self, key: str) -> bytes | None:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=self._full_key(key))
        except self._ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "404"}:
                return None
            raise
        return bytes(response["Body"].read())

    def exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=self._full_key(key))
        except self._ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"NoSuchKey", "NotFound", "404"}:
                return False
            raise
        return True

    def list_keys(self, prefix: str) -> list[str]:
        full_prefix = self._full_key(prefix)
        strip = f"{self._prefix}/" if self._prefix else ""
        keys: list[str] = []
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix=full_prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"].removeprefix(strip))  # back to a logical key
        return keys


def parse_s3_url(url: str) -> tuple[str, str]:
    """Split ``s3://<bucket>[/<prefix>]`` into ``(bucket, prefix)``.

    Raises :class:`CasestoreError` on anything that is not such a URL.
    """
    match = _S3_URL_RE.fullmatch(url)
    if match is None:
        raise CasestoreError(f"casestore URL {url!r} is not an s3://<bucket>[/<prefix>] URL")
    return match["bucket"], (match["prefix"] or "").strip("/")


def transport_from_settings() -> ObjectTransport | None:
    """Build the configured casestore transport, or ``None`` when dual-write is off.

    Reads ``FEDCOURTS_CASESTORE_URL``; unset (or empty — the workflow passes an
    unset repo variable through as ``""``) means the case store is disabled and
    writers mirror nothing (the default, fully-reversible state). A bare bucket
    URL falls back to :data:`DEFAULT_PREFIX` so both env forms serve the layout.
    """
    url = get_settings().casestore_url
    if url is None or not url.strip():
        return None
    bucket, prefix = parse_s3_url(url.strip())
    return S3ObjectTransport(bucket, prefix=prefix or DEFAULT_PREFIX)


# --- process transport + best-effort mirroring --------------------------------
#
# The dual-write hooks in `fedcourtsai.corpus` reach the store through a single
# process-wide transport, so activation is purely the env flag — no writer
# signature threading. It is built lazily from settings once and cached; unset
# flag → None → every mirror call is a pure no-op (the default, and the state in
# every test that does not opt in).

# A one-slot container (not a rebindable module global) holds the cached
# transport, so the accessors need no `global` statement.
_ACTIVE: dict[str, ObjectTransport | None] = {}


def active_transport() -> ObjectTransport | None:
    """The process-wide casestore transport (lazily built from settings, cached).

    A build failure (a malformed ``FEDCOURTS_CASESTORE_URL``, a boto3/region
    problem) disables the store — it logs and caches ``None`` rather than raising,
    so a fat-fingered flag can never crash an ingestion write.
    """
    if "transport" not in _ACTIVE:
        try:
            _ACTIVE["transport"] = transport_from_settings()
        except Exception as exc:  # broad by design: a bad flag disables, never crashes
            logger.warning("casestore: disabled — could not build transport: %s", exc)
            _ACTIVE["transport"] = None
    return _ACTIVE["transport"]


def set_active_transport(transport: ObjectTransport | None) -> None:
    """Override the process transport (tests / explicit wiring)."""
    _ACTIVE["transport"] = transport


def reset_active_transport() -> None:
    """Clear the cache so the next access rebuilds from settings (tests)."""
    _ACTIVE.clear()


def _best_effort(description: str, write: Callable[[ObjectTransport], object]) -> None:
    """Run one mirror write against the active transport, swallowing any failure.

    Dual-write is secondary to the SQLite blob (the phase-1 system of record), so a
    store hiccup logs and is swallowed — it must never fail an ingestion write.
    A no-op when the store is disabled (transport ``None``).
    """
    transport = active_transport()
    if transport is None:
        return
    try:
        write(transport)
    except Exception as exc:  # broad by design: no mirror error may break ingestion
        logger.warning("casestore: mirror failed (%s): %s", description, exc)


def mirror_cases(rows: Sequence[CorpusRow]) -> None:
    """Best-effort mirror of each row's ``case.json``; never raises."""
    transport = active_transport()
    if transport is None:
        return
    for row in rows:
        try:
            write_case(transport, row)
        except Exception as exc:  # broad by design: no mirror error may break ingestion
            logger.warning("casestore: mirror of case %s failed: %s", row.case_id, exc)


def mirror_snapshot(case_id: str, snapshot_date: date, payload: Mapping[str, Any]) -> None:
    """Best-effort mirror of one dated snapshot object; never raises."""
    _best_effort(
        f"snapshot {case_id}", lambda t: write_snapshot(t, case_id, snapshot_date, payload)
    )


def mirror_documents_for_cases(conn: ReadConnection, case_ids: Iterable[str]) -> None:
    """Best-effort mirror of each case's FULL document set + manifest; never raises.

    Guards on the transport *first*, so with the store off nothing is read back —
    the flag-off path stays a pure no-op. Reading the committed set back per case
    makes the mirrored manifest reflect every stored kind, not just the batch that
    triggered the write.
    """
    transport = active_transport()
    if transport is None:
        return
    for case_id in dict.fromkeys(case_ids):
        try:
            write_documents(transport, case_id, documents_for_case(conn, case_id))
        except Exception as exc:  # broad by design: no mirror error may break ingestion
            logger.warning("casestore: mirror of documents %s failed: %s", case_id, exc)


def mirror_documents(documents: Sequence[CaseDocument]) -> None:
    """Best-effort mirror of a document *batch*, merged per case; never raises.

    The split-mode entry point: the blob keeps no documents, so the batch is
    merged onto each case's existing store manifest (:func:`merge_documents`)
    rather than read back from the corpus. Transport-guarded (store off → no-op).
    """
    transport = active_transport()
    if transport is None:
        return
    by_case: dict[str, list[CaseDocument]] = {}
    for doc in documents:
        by_case.setdefault(doc.case_id, []).append(doc)
    for case_id, docs in by_case.items():
        try:
            merge_documents(transport, case_id, docs)
        except Exception as exc:  # broad by design: no mirror error may break ingestion
            logger.warning("casestore: mirror of documents %s failed: %s", case_id, exc)


def mirror_events_for_cases(conn: ReadConnection, case_ids: Iterable[str]) -> None:
    """Best-effort mirror of each case's FULL event list; never raises.

    Transport-guarded before any read-back (flag off → pure no-op); the committed
    set is read back per case so ``events.json`` is the complete list.
    """
    transport = active_transport()
    if transport is None:
        return
    for case_id in dict.fromkeys(case_ids):
        try:
            write_events(transport, case_id, events_for_case(conn, case_id))
        except Exception as exc:  # broad by design: no mirror error may break ingestion
            logger.warning("casestore: mirror of events %s failed: %s", case_id, exc)


# --- serialization + digests --------------------------------------------------


def _canonical_json(payload: Any) -> bytes:
    """Deterministic, newline-terminated JSON bytes (matches serialize.write_raw_json)."""
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def digest_bytes(body: bytes) -> str:
    """The sha256 hex digest of ``body`` — the content identity a consumer pins."""
    return hashlib.sha256(body).hexdigest()


@dataclass(frozen=True)
class ObjectRef:
    """A written object's coordinates: its key, content digest, and byte size.

    Recorded so a consumer can pin the exact content it was provisioned from,
    independent of a mutable manifest that may later point elsewhere.
    """

    key: str
    digest: str
    size: int


@dataclass(frozen=True)
class CaseMirror:
    """What :func:`mirror_case` wrote for one case (for logging / later pointering)."""

    case: ObjectRef
    events: ObjectRef | None = None
    snapshot: ObjectRef | None = None
    documents: list[ObjectRef] = field(default_factory=list)


# --- key layout (mirrors fedcourtsai.paths.CasePaths) -------------------------


def _split_case_id(case_id: str) -> tuple[str, str]:
    court, _, docket = case_id.partition("/")
    if not court or not docket:
        raise CasestoreError(f"case_id {case_id!r} is not '<court>/<docket>'")
    return court, docket


def case_prefix(case_id: str) -> str:
    """The per-case key prefix, e.g. ``ca9/64512345``."""
    court, docket = _split_case_id(case_id)
    return f"{court}/{docket}"


def case_key(case_id: str) -> str:
    return f"{case_prefix(case_id)}/case.json"


def events_key(case_id: str) -> str:
    return f"{case_prefix(case_id)}/events.json"


def snapshot_key(case_id: str, snapshot_date: date) -> str:
    return f"{case_prefix(case_id)}/snapshots/{snapshot_date.isoformat()}.json"


def documents_manifest_key(case_id: str) -> str:
    return f"{case_prefix(case_id)}/documents/documents.json"


def document_leaf_key(case_id: str, kind: str, fetched_at: date, digest: str) -> str:
    """A content-addressed, browsable text leaf: ``documents/<kind>/<date>-<digest>.txt``.

    The digest suffix makes the key unique per distinct content, so a superseding
    filing lands at a new key and the store is genuinely write-once.
    """
    return (
        f"{case_prefix(case_id)}/documents/{kind}/"
        f"{fetched_at.isoformat()}-{digest[:_LEAF_DIGEST_CHARS]}.txt"
    )


# --- writers ------------------------------------------------------------------


def write_case(transport: ObjectTransport, row: CorpusRow) -> ObjectRef:
    """Write the case's ``case.json`` (the CorpusRow); overwrite (a mutable manifest)."""
    body = _canonical_json(row.model_dump(mode="json"))
    key = case_key(row.case_id)
    transport.put(key, body)
    return ObjectRef(key=key, digest=digest_bytes(body), size=len(body))


def write_events(
    transport: ObjectTransport, case_id: str, events: Sequence[CorpusEvent]
) -> ObjectRef:
    """Write ``events.json`` (the case's predictable-event list, sorted by id)."""
    payload = [e.model_dump(mode="json") for e in sorted(events, key=lambda e: e.event_id)]
    body = _canonical_json(payload)
    key = events_key(case_id)
    transport.put(key, body)
    return ObjectRef(key=key, digest=digest_bytes(body), size=len(body))


def write_snapshot(
    transport: ObjectTransport,
    case_id: str,
    snapshot_date: date,
    payload: Mapping[str, Any],
) -> ObjectRef:
    """Write one dated point-in-time snapshot object (immutable per day)."""
    body = _canonical_json(dict(payload))
    key = snapshot_key(case_id, snapshot_date)
    transport.put(key, body)
    return ObjectRef(key=key, digest=digest_bytes(body), size=len(body))


def _put_document_leaf(
    transport: ObjectTransport, case_id: str, doc: CaseDocument
) -> tuple[dict[str, Any], ObjectRef]:
    """Write one document's content-addressed text leaf; return its manifest entry + ref."""
    text_bytes = doc.text.encode("utf-8")
    digest = digest_bytes(text_bytes)
    leaf = document_leaf_key(case_id, doc.kind, doc.fetched_at, digest)
    transport.put(leaf, text_bytes, if_absent=True)
    entry = {
        "kind": doc.kind,
        "url": doc.url,
        "entry_date": doc.entry_date,
        "fetched_at": doc.fetched_at.isoformat(),
        "pages": doc.pages,
        "truncated": doc.truncated,
        "text_key": leaf,
        "digest": digest,
        "bytes": len(text_bytes),
    }
    return entry, ObjectRef(key=leaf, digest=digest, size=len(text_bytes))


def write_documents(
    transport: ObjectTransport, case_id: str, documents: Sequence[CaseDocument]
) -> list[ObjectRef]:
    """Write each document's text as a content-addressed leaf + a current manifest.

    Text leaves are written ``if_absent`` (content-addressed keys already hold
    identical bytes, so a re-mirror uploads nothing). The manifest records the
    current leaf per kind with its digest, so provisioning can resolve and pin
    the exact text without reading the leaf. The manifest is *replaced* with
    exactly these kinds — the caller passes the full set (a corpus read-back);
    see :func:`merge_documents` for the split-mode batch merge.
    """
    refs: list[ObjectRef] = []
    manifest_entries: list[dict[str, Any]] = []
    # One current leaf per kind: CaseDocument is keyed (case_id, kind) with
    # latest-wins, so a batch carrying two of a kind keeps only the last — the
    # manifest is "kind -> current leaf", not an append log.
    by_kind = {doc.kind: doc for doc in documents}
    for doc in sorted(by_kind.values(), key=lambda d: d.kind):
        entry, ref = _put_document_leaf(transport, case_id, doc)
        manifest_entries.append(entry)
        refs.append(ref)
    manifest_body = _canonical_json({"documents": manifest_entries})
    transport.put(documents_manifest_key(case_id), manifest_body)
    return refs


def merge_documents(
    transport: ObjectTransport, case_id: str, documents: Sequence[CaseDocument]
) -> list[ObjectRef]:
    """Overlay a *batch* of documents onto the case's existing manifest.

    The split-mode counterpart to :func:`write_documents`: under the corpus split
    the blob holds no documents to read the full set back from, so the store is the
    accumulator. Each batch's kinds are written (content-addressed leaves) and
    merged into the existing ``documents.json`` — other kinds already recorded are
    preserved — so a later brief-in-opposition fetch never drops the petition from
    the manifest. Kind-sorted, matching :func:`write_documents`.
    """
    entries: dict[str, dict[str, Any]] = {}
    existing = transport.get(documents_manifest_key(case_id))
    if existing is not None:
        for entry in json.loads(existing).get("documents", []):
            entries[entry["kind"]] = entry
    refs: list[ObjectRef] = []
    for doc in {doc.kind: doc for doc in documents}.values():
        entry, ref = _put_document_leaf(transport, case_id, doc)
        entries[doc.kind] = entry
        refs.append(ref)
    manifest_body = _canonical_json({"documents": [entries[k] for k in sorted(entries)]})
    transport.put(documents_manifest_key(case_id), manifest_body)
    return refs


def mirror_case(
    transport: ObjectTransport,
    *,
    row: CorpusRow,
    events: Sequence[CorpusEvent] | None = None,
    snapshot: tuple[date, Mapping[str, Any]] | None = None,
    documents: Sequence[CaseDocument] | None = None,
) -> CaseMirror:
    """Mirror one case's mutated content to the store; the dual-write entry point.

    Writes ``case.json`` always; ``events.json`` / a dated snapshot / document
    leaves only when the caller supplies them (each writer channel has a
    different subset of a case's content in hand). ``events=None`` skips the
    events object; ``events=[]`` writes an explicit empty list.
    """
    case_ref = write_case(transport, row)
    events_ref = None if events is None else write_events(transport, row.case_id, events)
    snapshot_ref = (
        write_snapshot(transport, row.case_id, snapshot[0], snapshot[1])
        if snapshot is not None
        else None
    )
    document_refs = (
        write_documents(transport, row.case_id, documents) if documents is not None else []
    )
    return CaseMirror(
        case=case_ref, events=events_ref, snapshot=snapshot_ref, documents=document_refs
    )


# --- reads (the payload read source, symmetric to the mirror) -----------------
#
# Under the corpus split these serve the payloads the blob no longer holds. They
# take an explicit transport so provision.CasestoreSource (its own transport, for
# tests) and the process read source (the active transport) share one implementation.


def _snapshot_dates(transport: ObjectTransport, case_id: str) -> list[date]:
    """Every dated snapshot's date for a case, parsed from its ``snapshots/`` keys."""
    prefix = f"{case_prefix(case_id)}/snapshots/"
    dates: list[date] = []
    for key in transport.list_keys(prefix):
        stem = key[len(prefix) :]
        if stem.endswith(".json"):
            try:
                dates.append(date.fromisoformat(stem[: -len(".json")]))
            except ValueError:
                continue
    return dates


def read_latest_snapshot(
    transport: ObjectTransport, case_id: str
) -> tuple[date, dict[str, Any]] | None:
    """The newest dated snapshot — ``(date, payload)`` — or ``None`` (mirrors the
    corpus ``ORDER BY snapshot_date DESC LIMIT 1``)."""
    dates = _snapshot_dates(transport, case_id)
    if not dates:
        return None
    latest = max(dates)
    body = transport.get(snapshot_key(case_id, latest))
    if body is None:
        return None
    return latest, json.loads(body)


def read_latest_live_snapshot(
    transport: ObjectTransport, case_id: str
) -> tuple[date, dict[str, Any]] | None:
    """The newest **live-shaped** snapshot (carrying ``ProceedingsandOrder``), or
    ``None`` — mirrors ``corpus.latest_live_snapshot``, skipping newer REST rows."""
    for snapshot_date in sorted(_snapshot_dates(transport, case_id), reverse=True):
        body = transport.get(snapshot_key(case_id, snapshot_date))
        if body is None:
            continue
        payload = json.loads(body)
        if "ProceedingsandOrder" in payload:
            return snapshot_date, payload
    return None


def read_documents(transport: ObjectTransport, case_id: str) -> list[CaseDocument]:
    """The case's documents, kind-ordered, reconstructed from the manifest + leaves."""
    body = transport.get(documents_manifest_key(case_id))
    if body is None:
        return []
    documents: list[CaseDocument] = []
    for entry in json.loads(body).get("documents", []):  # manifest is kind-sorted
        leaf = transport.get(entry["text_key"])
        documents.append(
            CaseDocument(
                case_id=case_id,
                kind=entry["kind"],
                url=entry["url"],
                entry_date=entry["entry_date"],
                fetched_at=date.fromisoformat(entry["fetched_at"]),
                pages=entry["pages"],
                truncated=entry["truncated"],
                text=leaf.decode("utf-8") if leaf is not None else "",
            )
        )
    return documents


def read_events(transport: ObjectTransport, case_id: str) -> list[CorpusEvent]:
    """The case's predictable events, event_id-ordered (empty if none stored)."""
    body = transport.get(events_key(case_id))
    if body is None:
        return []
    return [CorpusEvent.model_validate(entry) for entry in json.loads(body)]


class _CasestoreReadSource:
    """``corpus.PayloadReadSource`` over the process (active) transport.

    Consulted only under the corpus-split mode (the gate lives in
    ``corpus._payload_read_source``). With the store unbuilt (transport ``None``)
    it reads as empty — the same "no prior / no documents" the corpus would.
    """

    def latest_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        transport = active_transport()
        return None if transport is None else read_latest_snapshot(transport, case_id)

    def latest_live_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        transport = active_transport()
        return None if transport is None else read_latest_live_snapshot(transport, case_id)

    def documents_for_case(self, case_id: str) -> list[CaseDocument]:
        transport = active_transport()
        return [] if transport is None else read_documents(transport, case_id)


# --- dual-write sink registration ---------------------------------------------


class _CorpusMirrorSink:
    """Adapts this module's ``mirror_*`` functions to :class:`fedcourtsai.corpus.MirrorSink`.

    Registered with the corpus write seams so they mirror here *without* importing
    this module — the dependency is inverted (casestore → corpus only), which keeps
    the storage layer free of the S3 mirror and free of an import cycle.
    """

    mirror_cases = staticmethod(mirror_cases)
    mirror_snapshot = staticmethod(mirror_snapshot)
    mirror_documents_for_cases = staticmethod(mirror_documents_for_cases)
    mirror_documents = staticmethod(mirror_documents)
    mirror_events_for_cases = staticmethod(mirror_events_for_cases)


# Runs on import; fedcourtsai/__init__ imports this module so the sink is always
# registered. The sink's mirror_* helpers are themselves gated on the flag
# (active_transport() is None → no-op), so registration alone changes nothing.
set_mirror_sink(_CorpusMirrorSink())

# The read counterpart, registered the same way. corpus consults it only under the
# corpus-split mode (corpus._payload_read_source gates on the flag), so with the
# mode off the corpus reads never leave SQLite and registration alone changes nothing.
set_payload_read_source(_CasestoreReadSource())
