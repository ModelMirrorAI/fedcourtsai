"""Seed a lean, real-slice **staging** corpus from the production stores.

The pipeline's orchestration and its read/write seams can only be exercised
end to end against a real corpus, and the production one is single-writer by
construction (see SECURITY.md): the corpus-write credentials exist only inside
the writer jobs, so there is nowhere to rehearse a write path without touching
the record. This module builds the missing surface — a **staging corpus**: a
handful of real cases copied into their own bucket/prefix pair, with the same
two-store shape the split-mode production system has, so an integration
scenario reads and writes something real for runner minutes.

**Two halves, copied differently, on purpose.**

* The **index blob** is *rebuilt*, not copied: a fresh database carrying only
  the slice's ``cases`` and ``events`` rows, written through the corpus's own
  upsert seams (so the slice is schema-current, whatever the source blob's
  vintage) and published to the destination remote through the same
  content-addressed :func:`fedcourtsai.corpus_remote.upload_index` the
  production push uses. It is **payload-free by construction** — the opinion
  body is dropped and no snapshot or document row is written — so the slice
  has split-on parity regardless of what mode the seeding process runs under.
* The **content store** half is a faithful **key-level copy**: every object
  under each case's prefix is read from the source store and written to the
  destination one, byte for byte. Copying rather than re-serializing is what
  makes the staging store a real specimen — every dated snapshot, every
  content-addressed document leaf, and the manifests that point at them arrive
  exactly as the writers produced them, not as this module would render them.
  The store's two kinds of object are copied on different rules, and the
  distinction is load-bearing: write-once keys already present are skipped,
  while the three **mutable** manifests are re-copied every time, because the
  writers overwrite those in place and a stale copy of one describes a case
  that no longer exists (see :func:`copy_case_objects`).

**The safety rails, and what actually guarantees the property.** What makes it
impossible to write production here is **IAM**: the seeding role's policy is
read-only on the production stores, so no input and no bug in this module
reaches the production write path. The rails are the second line, and they earn
their place by turning a misconfiguration into a local refusal before anything
is read rather than an ``AccessDenied`` part-way through. The source is a
**pinned parameter** (:class:`Source`), never the ambient environment — the
staging runbook repoints the environment's corpus variables at the staging
pair, and a source that followed them would read staging as its own source
while the rail protected the wrong stores. Three rails hang off that pin:
:func:`assert_destination_is_not_the_source` refuses a destination that is, or
is *inside*, either pinned source store — resolved through the same
parsers the transports use, so no spelling of a location slips past —
:func:`assert_no_pointer_override` refuses to read the source index through a
pointer override (the index half of the same self-seeding hazard), and
:func:`assert_stage_db_is_not_the_corpus` refuses a working file that would
overwrite the checkout's committed pointer. Everything else about the operation
is convergent rather than destructive — the remote is add-only and
content-addressed, and the store copy skips *write-once* keys already present
while re-copying the three mutable manifests — so a re-run converges on the
source's current state and a half-finished run is resumed by the next one.

**Ordering, at two levels, both the writers' blob-before-pointer rule.** On an
apply the content objects are copied *before* the blob is published, so a
reader that resolves the new pointer always finds the payloads its rows refer
to; a run interrupted between the two leaves a store ahead of its index, which
the next apply completes. Within a case the same rule again: the documents
manifest is the only object that points at other keys, so it lands **after**
the leaves it names.

Everything here takes its transports as parameters, so the whole module runs
offline in tests against in-memory stores — the same seam the casestore and
whole-file corpus transports already expose.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from . import casestore, corpus
from .casestore import (
    DEFAULT_PREFIX,
    CasestoreError,
    ObjectTransport,
    S3ObjectTransport,
    parse_s3_url,
)
from .config import Settings
from .corpus import CorpusEvent, CorpusRow, ReadConnection
from .corpus_ranged import IndexPointer, RangedBackendError, parse_remote_url
from .corpus_remote import WholeFileTransport, upload_index

# Generous by default: the point of the slice is a handful of real cases, and
# the cost of one is a few content-store objects, so the bound exists to stop a
# fat-fingered docket list from copying the corpus rather than to ration.
DEFAULT_MAX_CASES = 200

# The case-id grammar the corpus keys on (`<court>/<docket>`; see
# `fedcourtsai.ids.case_id`). Matched before anything reaches a key prefix, so
# a malformed entry is a refusal rather than an odd listing that reads as
# "this case has no content". Deliberately NARROWER than what `ids.case_id`
# can emit — `slugify` also passes `.` and `_`, which this rejects — because
# every id here becomes an S3 key prefix, and excluding `.` means no component
# can be a `..` path segment whatever a downstream consumer does with the key.
# A court id that needed those characters would widen this knowingly, not by
# inheriting the slug rule.
_CASE_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]*/[0-9]+")

# Where a case's content objects sit *within* its own prefix (the layout itself
# is `casestore`'s). Classification is anchored on the case-relative remainder,
# never a substring of the whole key: a court or docket id containing one of
# these words would otherwise miscount every object under it.
_SNAPSHOTS_SEGMENT = "snapshots/"
_DOCUMENTS_SEGMENT = "documents/"

# The three objects the writers **overwrite in place** — the small mutable
# manifests, as opposed to the write-once bulk (dated snapshots, and document
# text leaves whose keys carry their own content digest). The distinction is
# the whole of `copy_case_objects`' correctness: a destination copy of one of
# these is a *stale* copy the moment the source case is re-ingested, so it is
# re-copied on every apply, while an existing write-once key already holds
# identical bytes and is skipped.
_MUTABLE_KEYS = ("case.json", "events.json", "documents/documents.json")
# The manifest that *points at other keys*, so it must land after them.
_DOCUMENTS_MANIFEST = "documents/documents.json"


class SeedSliceError(RuntimeError):
    """A staging-seed configuration, safety-rail, or input problem.

    Deliberately loud: every message names what was expected, because the
    command's failure modes are all "the operator meant something else" — a
    malformed docket id, an unset store URL, a destination that is production.
    """


# --- the requested slice ------------------------------------------------------


def parse_case_ids(values: Sequence[str] = (), *, path: Path | None = None) -> list[str]:
    """The requested slice, from repeated options and/or a docket-list file.

    One ``<court>/<docket>`` case id per line or per option; ``#`` starts a
    comment and blank lines are ignored, so a docket list can carry its own
    provenance note. Order-preserving and de-duplicated (the slice is a set,
    but a reproducible one), and every entry is matched against the case-id
    grammar before it is used.
    """
    raw: list[str] = list(values)
    if path is not None:
        if not path.is_file():
            raise SeedSliceError(f"no docket list at {path}")
        # Explicit encoding: the workflow writes this file, but a maintainer's
        # own list should not read differently under a non-UTF-8 locale.
        raw.extend(path.read_text(encoding="utf-8").splitlines())
    case_ids: list[str] = []
    for line in raw:
        entry = line.split("#", 1)[0].strip()
        if not entry:
            continue
        if _CASE_ID_RE.fullmatch(entry) is None:
            raise SeedSliceError(f"{entry!r} is not a '<court>/<docket>' case id")
        if entry not in case_ids:
            case_ids.append(entry)
    if not case_ids:
        raise SeedSliceError("the slice names no case; pass --dockets or --dockets-file")
    return case_ids


def bound_cases(case_ids: Sequence[str], max_cases: int) -> tuple[list[str], int]:
    """``(kept, dropped)`` — the slice truncated to ``max_cases``, in order.

    A bound, not a filter: the dropped count is reported, so a truncated
    request is visible in the census rather than silently smaller than what was
    asked for.
    """
    if max_cases < 1:
        raise SeedSliceError(f"--max-cases must be at least 1, not {max_cases}")
    kept = list(case_ids[:max_cases])
    return kept, len(case_ids) - len(kept)


# --- the safety rail ----------------------------------------------------------


@dataclass(frozen=True)
class Destination:
    """Where a slice is seeded — one object because it is one concept.

    A staging corpus is a *pair* of stores, the safety rail compares both, and
    the two transports are test seams over that same pair rather than
    independent knobs; unset, each is built from its URL.

    **The rail sees only the URLs.** An injected transport is trusted to be the
    store its URL names, because nothing here can check that a caller-supplied
    client points where it claims. Only tests inject one, and a test that
    injected a transport disagreeing with its URL would be asserting about a
    configuration that cannot occur in the command.
    """

    remote_url: str
    casestore_url: str
    objects: ObjectTransport | None = None
    blob_transport: WholeFileTransport | None = None

    def __post_init__(self) -> None:
        # The same construction-time normalization and empty-slot refusal the
        # source gets: an unset workflow variable resolves to the empty
        # string, and all four store slots should fail closed in one voice —
        # a named refusal, never a parse error over the empty string.
        object.__setattr__(self, "remote_url", self.remote_url.strip())
        object.__setattr__(self, "casestore_url", self.casestore_url.strip())
        if not self.remote_url:
            raise SeedSliceError(
                "refusing to seed: the destination corpus remote URL is empty "
                "(--dest-remote) — an unset destination variable is a "
                "misconfiguration, not a default; see docs/security.md."
            )
        if not self.casestore_url:
            raise SeedSliceError(
                "refusing to seed: the destination content-store URL is empty "
                "(--dest-casestore) — an unset destination variable is a "
                "misconfiguration, not a default; see docs/security.md."
            )

    def object_transport(self) -> ObjectTransport:
        """The destination content-store transport, built from the URL if unset."""
        if self.objects is not None:
            return self.objects
        bucket, prefix = parse_s3_url(self.casestore_url)
        return S3ObjectTransport(bucket, prefix=prefix or DEFAULT_PREFIX)


@dataclass(frozen=True)
class Source:
    """Where a slice is read from — pinned by the caller, never ambient.

    The seeder's source doubles as the destination rail's comparison basis,
    so it is a parameter stated at the invocation rather than a value
    resolved from the environment: the staging runbook repoints the
    environment's corpus variables at the staging pair, and a source that
    followed them would have the seeder read staging as its own source while
    the rail protected the wrong stores. Construction fails closed — an
    empty URL in either slot is a refusal before anything is read, because
    half a comparison basis is no basis, and the content-store half is
    doubly required as the slice's payload source.

    **The rail sees only the URLs**, exactly as with :class:`Destination`:
    an injected transport is trusted to be the store its URL names, and only
    tests inject one. Reading *from* a pointer-overridden pair is
    deliberately unsupported — the source index is always the pinned
    remote's committed pointer (:func:`assert_no_pointer_override`); a
    source-pointer input would be its own feature, omitted knowingly.
    """

    remote_url: str
    casestore_url: str
    objects: ObjectTransport | None = None

    def __post_init__(self) -> None:
        # Normalized once at construction, so the rail's parsers and every
        # reader of these URLs see the same bytes — a padded variable value
        # must not pass the rail and then reach a URL-echoing parser
        # downstream (rail messages name slots, never URLs, and run logs are
        # public).
        object.__setattr__(self, "remote_url", self.remote_url.strip())
        object.__setattr__(self, "casestore_url", self.casestore_url.strip())
        if not self.remote_url:
            raise SeedSliceError(
                "refusing to seed: the source corpus remote URL is not pinned "
                "(--source-remote), so the rail cannot tell a staging "
                "destination from its source. Pin it to the production value "
                "(the workflow does) — see docs/security.md."
            )
        if not self.casestore_url:
            raise SeedSliceError(
                "refusing to seed: the source content-store URL is not pinned "
                "(--source-casestore). The rail cannot tell a staging "
                "destination from its source without it, and it is the "
                "slice's payload source — see docs/security.md."
            )

    def object_transport(self) -> ObjectTransport:
        """The source content-store transport, built from the URL if unset."""
        if self.objects is not None:
            return self.objects
        bucket, prefix = parse_s3_url(self.casestore_url)
        return S3ObjectTransport(bucket, prefix=prefix or DEFAULT_PREFIX)


# A store's identity for the rail: ``(bucket, prefix)`` case-folded. Comparing
# raw URL strings is not enough — the same location has many spellings
# (a bare bucket, a doubled slash, a trailing slash), and each one that the
# transports resolve identically but a string compare does not is a bypass.
_Location = tuple[str, str]


def _fold(location: _Location) -> _Location:
    return (location[0].casefold(), location[1].casefold())


def _remote_location(url: str, *, described_as: str) -> _Location:
    """The corpus remote's ``(bucket, prefix)``, through the transport's parser.

    Parser failures are re-raised naming only the slot: a rail message reaches
    run logs and a PR, and a store URL is supplied out of band and never
    published (see SECURITY.md).
    """
    try:
        return _fold(parse_remote_url(url.strip()))
    except RangedBackendError as exc:
        raise SeedSliceError(f"{described_as} is not an s3://<bucket>[/<prefix>] URL") from exc


def _store_location(url: str, *, described_as: str) -> _Location:
    """The content store's ``(bucket, prefix)``, with the transport's own default.

    ``prefix or DEFAULT_PREFIX`` mirrors :func:`casestore.transport_from_settings`
    exactly — without it a bare production bucket URL and the prefixed spelling
    of the same store compare unequal while resolving to the same objects.
    """
    try:
        bucket, prefix = parse_s3_url(url.strip())
    except CasestoreError as exc:
        raise SeedSliceError(f"{described_as} is not an s3://<bucket>[/<prefix>] URL") from exc
    return _fold((bucket, prefix or DEFAULT_PREFIX))


def _source_locations(source: Source) -> dict[str, _Location]:
    """Both pinned source stores as ``(bucket, prefix)``.

    The unset case cannot reach here — :class:`Source` refuses to construct
    with an empty slot — so this is pure resolution: the same parsers the
    transports use, over the two URLs the rail compares every destination
    against.
    """
    return {
        "corpus remote": _remote_location(source.remote_url, described_as="--source-remote"),
        "content store": _store_location(source.casestore_url, described_as="--source-casestore"),
    }


def assert_destination_is_not_the_source(destination: Destination, *, source: Source) -> None:
    """Refuse a destination that is, or is inside, either pinned source store.

    The invariant is that the seeder never writes what it reads. Its one
    production caller pins the source to the production pair, so there this
    is the production rail; pinned anywhere else it still refuses the
    self-seed that would read a pair as its own source — which is exactly
    what re-basing the comparison on the ambient environment would permit
    the moment that environment is repointed at the staging pair.

    The one rail that cannot be convergent: everything else this module does is
    add-only and idempotent, but a seed pointed at production would publish a
    handful-of-cases blob as the corpus index and rewrite the pointer to name
    it. So the comparison is deliberately coarse in the safe direction, on two
    levels:

    * **exact location** — the destination's ``(bucket, prefix)``, resolved
      through the *same parsers the transports use* (content store included,
      with its ``DEFAULT_PREFIX`` fallback), so every spelling of a location
      compares equal to every other: a bare bucket, a doubled slash, a trailing
      slash;
    * **bucket** — any destination sharing a bucket with either source
      store is refused whatever its prefix. That is the runbook's own
      invariant, that the staging pair is a separate bucket and not a prefix
      inside the source's, enforced rather than merely stated — and it is what
      makes the rail robust to prefix spellings nobody enumerated.

    Both checks run in **both** destination slots against **both** source
    stores: a staging content store that happens to name the source corpus
    remote is just as wrong. Every exact-location check runs **before** any
    bucket check, so a destination that is precisely a source store is
    diagnosed as that rather than as the vaguer "inside its bucket" — the two
    production stores share a bucket, so the coarse rule would otherwise
    shadow the precise one and the operator would get the less useful message.

    This is the second line, not the guarantee. The first is IAM: the staging
    read-write role's policy is read-only on the production stores, so a
    destination that got past this rail still could not be written. The rail
    catches the misconfiguration the policy would turn into a confusing
    ``AccessDenied`` — and, being local, it catches it before anything is read.
    """
    source_stores = _source_locations(source)
    slots = (
        ("--dest-remote", _remote_location(destination.remote_url, described_as="--dest-remote")),
        (
            "--dest-casestore",
            _store_location(destination.casestore_url, described_as="--dest-casestore"),
        ),
    )
    for flag, location in slots:
        for name, configured in source_stores.items():
            if location == configured:
                raise SeedSliceError(
                    f"refusing to seed: {flag} names the pinned source {name}. "
                    "The staging corpus is its own bucket/prefix pair — see the "
                    "staging corpus runbook in docs/security.md."
                )
    for flag, location in slots:
        for name, configured in source_stores.items():
            if location[0] == configured[0]:
                raise SeedSliceError(
                    f"refusing to seed: {flag} is a prefix inside the pinned source "
                    f"{name}'s bucket. The staging corpus is a SEPARATE bucket, not a "
                    "prefix inside its source's — see the staging corpus runbook in "
                    "docs/security.md."
                )


def assert_no_pointer_override(settings: Settings) -> None:
    """Refuse to seed while a corpus pointer override is set.

    The seeder's source index is the pinned remote's committed pointer; an
    override in the environment asks for another blob — a dev shell flipped
    to the staging pair may carry exactly that — which is the index-side
    twin of the store hazard the pin closes. Resolved against the pinned
    remote, a staging override is a missing key rather than a mis-read, so
    what this rail buys is the ``corpus-push`` posture stated as a named
    refusal: a command whose correctness depends on which blob it saw does
    not run under one, and the refusal says why where the missing key would
    not. Seeding *from* an overridden pair would need its own explicit
    source-pointer input — a deliberate omission (:class:`Source`).
    """
    if settings.corpus_pointer is not None:
        raise SeedSliceError(
            "refusing to seed: a corpus pointer override is set in the "
            "environment. The seeder reads the pinned source's committed "
            "pointer, never an override — unset the pointer variable (a dev "
            "shell flipped to the staging pair may carry one; see the staging "
            "corpus runbook in docs/security.md)."
        )


def assert_stage_db_is_not_the_corpus(stage_db: Path, *, settings: Settings) -> None:
    """Refuse a working file that would clobber the committed corpus pointer.

    The local half of the same rail. :func:`upload_index` writes the pointer
    **beside** the blob it publishes, so a ``stage_db`` resolving to the
    checkout's own ``corpus/corpus.db`` would overwrite ``corpus.db.ref`` with
    a pointer into the *staging* remote — and a writer lane that then committed
    it would repoint every consumer of production at a 200-case slice. Resolved
    before comparing, so ``./corpus/corpus.db`` and an absolute spelling of the
    same file are one path.
    """
    corpus_db = corpus.corpus_db_path(settings.corpus_root)
    # `strict=False`: neither file need exist yet, and a non-existent path
    # still resolves to the location it names.
    if stage_db.resolve(strict=False) == corpus_db.resolve(strict=False):
        raise SeedSliceError(
            f"refusing to seed: --stage-db is the corpus blob at {corpus_db}, whose "
            "committed pointer names production. Stage the slice somewhere else — the "
            "default is a gitignored path beside it."
        )


# --- the census ---------------------------------------------------------------


@dataclass(frozen=True)
class CaseCensus:
    """What one requested case contributes to the slice."""

    case_id: str
    present: bool  # a `cases` row exists in the source corpus
    events: int
    snapshots: int  # dated snapshot objects in the source content store
    documents: int  # content-addressed document text leaves
    objects: int  # every content-store object under the case's prefix


@dataclass(frozen=True)
class SliceCensus:
    """The whole slice's shape — what a dry run prints and an apply copies."""

    cases: tuple[CaseCensus, ...]
    requested: int
    dropped: int  # requested cases beyond --max-cases

    @property
    def missing(self) -> tuple[str, ...]:
        """Requested cases with no row in the source corpus."""
        return tuple(case.case_id for case in self.cases if not case.present)

    @property
    def rows(self) -> int:
        return sum(1 for case in self.cases if case.present)

    @property
    def events(self) -> int:
        return sum(case.events for case in self.cases)

    @property
    def objects(self) -> int:
        return sum(case.objects for case in self.cases)


def _case_keys(objects: ObjectTransport | None, case_id: str) -> list[str]:
    """Every content-store key under one case's prefix, sorted (stable copies)."""
    if objects is None:
        return []
    return sorted(objects.list_keys(f"{casestore.case_prefix(case_id)}/"))


def _within_case(key: str, case_id: str) -> str:
    """A listed key's remainder *below* its case prefix (``snapshots/…``).

    Every classification below keys on this rather than on a substring of the
    whole key, so a court or docket id that happens to contain ``documents``
    cannot make one object read as another kind.
    """
    return key.removeprefix(f"{casestore.case_prefix(case_id)}/")


def census_slice(
    conn: ReadConnection,
    case_ids: Sequence[str],
    *,
    objects: ObjectTransport | None,
    requested: int | None = None,
    dropped: int = 0,
) -> SliceCensus:
    """Measure the slice against the source stores without writing anything.

    One row lookup, one event read, and one key listing per case — the whole
    dry run, and cheap enough over a bounded slice that the apply path takes
    the same census first and reports it alongside what it copied.
    """
    cases: list[CaseCensus] = []
    for case_id in case_ids:
        row = corpus.get_row(conn, case_id)
        events = corpus.events_for_case(conn, case_id) if row is not None else []
        keys = _case_keys(objects, case_id)
        within = [_within_case(key, case_id) for key in keys]
        cases.append(
            CaseCensus(
                case_id=case_id,
                present=row is not None,
                events=len(events),
                snapshots=sum(1 for rest in within if rest.startswith(_SNAPSHOTS_SEGMENT)),
                documents=sum(
                    1
                    for rest in within
                    if rest.startswith(_DOCUMENTS_SEGMENT) and rest != _DOCUMENTS_MANIFEST
                ),
                objects=len(keys),
            )
        )
    return SliceCensus(
        cases=tuple(cases),
        requested=len(case_ids) if requested is None else requested,
        dropped=dropped,
    )


# --- the two halves -----------------------------------------------------------


@contextmanager
def _mirror_disabled() -> Iterator[None]:
    """Silence the casestore dual-write for the duration of a slice build.

    ``upsert_rows`` / ``upsert_events`` mirror through the **process-wide**
    casestore transport, which in a seeding run is built from settings — i.e.
    the *production* content store. The staging store's half is a faithful
    key-level copy instead, so the mirror is switched off outright rather than
    repointed: nothing in this module may write to production, and a sink that
    is off cannot. :func:`casestore.transport_override` puts back exactly what
    was there, so the block borrows the seam without disturbing its caller.
    """
    with casestore.transport_override(None):
        yield


def build_slice_blob(
    source_conn: ReadConnection, case_ids: Sequence[str], dest_db: Path
) -> tuple[int, int]:
    """Write a payload-free index blob carrying only the slice's rows + events.

    Returns ``(rows, events)``. The destination file is rebuilt from scratch on
    every call — the slice is a pure function of the source and the docket
    list, so re-running converges rather than accumulating — and the rows are
    written through :func:`fedcourtsai.corpus.upsert_rows`, so the blob carries
    the current schema and the current migrations whatever the source's
    vintage.

    Payload-free by construction, not by mode: the opinion body is dropped from
    every row before it is written and no ``snapshots`` / ``documents`` row is
    written at all, so the slice has split-on parity even when the seeding
    process runs with the split mode off. The retained ``has_opinion`` bit
    still says a body exists — it rides the row and dropping the body does not
    re-derive it — so the scope classifiers read the slice the way they read
    production.

    **Two tables are deliberately left empty**: ``discovery_watermarks`` and
    ``live_discovery_cursors``. Both are *ingestion* state — where the pull
    governor and the Term walkers resume from — and the staging corpus exists
    for the read and orchestration seams, which never consult them. Copying
    them would be worse than useless: a slice carrying production's cursors
    reads as a corpus already walked to a frontier it does not contain, so
    anything that did consult them would draw a false conclusion instead of an
    obviously empty one. An ingestion path exercised against the staging corpus
    would need them seeded deliberately, which is a different feature from
    this one.
    """
    rows: list[CorpusRow] = []
    events: list[CorpusEvent] = []
    for case_id in case_ids:
        row = corpus.get_row(source_conn, case_id)
        if row is None:
            continue
        rows.append(row.model_copy(update={"opinion_text": None}))
        events.extend(corpus.events_for_case(source_conn, case_id))
    dest_db.parent.mkdir(parents=True, exist_ok=True)
    dest_db.unlink(missing_ok=True)
    with _mirror_disabled(), corpus.connect(dest_db) as conn:
        if rows:
            corpus.upsert_rows(conn, rows)
        if events:
            corpus.upsert_events(conn, events)
    # The same layout contract every writer command honors before a push: 64 KB
    # pages, non-WAL at rest, or the ranged reader cannot serve the blob.
    corpus.ensure_ranged_layout(dest_db)
    return len(rows), len(events)


@dataclass(frozen=True)
class CopyCounts:
    """What one object copy moved, skipped, and could not read."""

    copied: int  # written at the destination (new bulk + every mutable manifest)
    skipped: int  # write-once keys the destination already held
    unreadable: int  # listed at the source but gone by the time it was read


def _copy_order(keys: Sequence[str], case_id: str) -> list[str]:
    """A case's keys with the documents manifest **last**.

    The module's blob-before-pointer rule, one level down: the manifest is the
    only object that *points at other keys*, so a copy interrupted part-way
    must never leave one naming leaves the destination does not hold. Land the
    leaves first and an interrupted case is merely incomplete — readable, and
    completed by the next apply — instead of internally inconsistent.
    """
    return sorted(keys, key=lambda key: _within_case(key, case_id) == _DOCUMENTS_MANIFEST)


def copy_case_objects(
    source: ObjectTransport, dest: ObjectTransport, case_ids: Sequence[str]
) -> CopyCounts:
    """Copy every content object under each case's prefix.

    A key-level copy, so the destination holds the writers' own bytes rather
    than a re-serialization: dated snapshots, content-addressed document
    leaves, and the manifests that point at them all arrive unchanged.

    **Two classes of key, copied on different rules**, because the store has
    two kinds of object (see :mod:`fedcourtsai.casestore`):

    * **write-once** — dated snapshots and content-addressed text leaves.
      Skipped when the destination already holds the key, since that key can
      only hold identical bytes. This is what makes a re-seed converge to no
      work.
    * **mutable** (:data:`_MUTABLE_KEYS`: ``case.json``, ``events.json``,
      ``documents/documents.json``) — **always re-copied**. The writers
      overwrite these in place, so an existing destination copy is evidence of
      nothing: skip them and a re-seed leaves a manifest naming a superseded
      petition while the new leaf sits unreachable beside it, and a
      ``case.json`` still saying the case is undecided while the blob half —
      rebuilt from scratch every apply — says denied. Re-copying is what keeps
      the two halves of the staging corpus describing the same case.

    A key that lists but no longer reads is counted and skipped rather than
    fatal: the listing is a moment older than the read, and a slice missing one
    leaf is worth more than a refused seed.
    """
    copied = skipped = unreadable = 0
    for case_id in case_ids:
        for key in _copy_order(_case_keys(source, case_id), case_id):
            mutable = _within_case(key, case_id) in _MUTABLE_KEYS
            if not mutable and dest.exists(key):
                skipped += 1
                continue
            body = source.get(key)
            if body is None:
                unreadable += 1
                continue
            dest.put(key, body)
            copied += 1
    return CopyCounts(copied=copied, skipped=skipped, unreadable=unreadable)


# --- the operation ------------------------------------------------------------


@dataclass(frozen=True)
class SeedResult:
    """What one ``corpus-seed-slice`` invocation measured and (maybe) wrote."""

    census: SliceCensus
    applied: bool
    rows: int
    events: int
    objects: CopyCounts
    blob_bytes: int
    pointer: IndexPointer | None
    # The source index blob the census was taken over, where the caller
    # resolved one (the ranged read does; a local file has no pointer of its
    # own). Rendered so a stale source pin is visible in the census a
    # maintainer reads before an apply — a pin naming a bucket that still
    # resolves to an outdated blob is green and wrong everywhere else.
    source_pointer: IndexPointer | None = None

    def render_markdown(self) -> str:
        """The step-summary rendering: the census table, then the verdict.

        An applied run also renders the published pointer, because that value
        is the only thing a staging *consumer* needs and the runner it was
        computed on is thrown away.
        """
        mode = "applied" if self.applied else "dry run"
        lines = [
            f"### Staging corpus slice ({mode})",
            "",
            "| case | row | events | snapshots | documents | objects |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for case in self.census.cases:
            row = "yes" if case.present else "**missing**"
            lines.append(
                f"| `{case.case_id}` | {row} | {case.events} | "
                f"{case.snapshots} | {case.documents} | {case.objects} |"
            )
        lines += [
            "",
            f"- **{len(self.census.cases)} case(s)** in the slice "
            + f"({self.census.requested} requested, {self.census.dropped} over the bound)",
            f"- **{self.census.rows} row(s)**, {self.census.events} event(s), "
            + f"{self.census.objects} content-store object(s)",
        ]
        if self.source_pointer is not None:
            # The pin's resolved value: which source blob this census
            # measured. A stale pin still resolves somewhere — this line is
            # where a maintainer sees *what* it resolved to.
            lines.append(
                f"- source index blob `{self.source_pointer.key}` "
                + f"({self.source_pointer.size} bytes)"
            )
        if self.census.missing:
            missing = ", ".join(f"`{case_id}`" for case_id in self.census.missing)
            lines.append(f"- no row in the source corpus for: {missing}")
        if not self.applied:
            lines.append("- nothing written — re-dispatch with `apply` to seed.")
            return "\n".join(lines) + "\n"
        lines += [
            f"- copied **{self.objects.copied}** object(s) — every mutable manifest "
            + f"plus any new write-once key; {self.objects.skipped} write-once key(s) "
            + "the destination already held were skipped",
            f"- published a {self.blob_bytes}-byte index blob",
        ]
        if self.objects.unreadable:
            # Never silent: a listed key that would not read means the slice is
            # missing content the census counted, which the next apply fixes.
            lines.append(
                f"- {self.objects.unreadable} listed object(s) could not be read and "
                + "were left out — re-apply to pick them up"
            )
        if self.pointer is not None:
            lines += [
                "",
                "The staging index pointer this run published — the value a staging",
                "consumer resolves against the staging corpus remote:",
                "",
                "```json",
                "{",
                f'  "key": "{self.pointer.key}",',
                f'  "schema_version": "{self.pointer.schema_version}",',
                f'  "sha256": "{self.pointer.sha256}",',
                f'  "size": {self.pointer.size}',
                "}",
                "```",
            ]
        return "\n".join(lines) + "\n"


def seed_slice(  # noqa: PLR0913 - keyword-only; one invocation's full coordinates
    *,
    source_conn: ReadConnection,
    source: Source,
    case_ids: Sequence[str],
    destination: Destination,
    settings: Settings,
    stage_db: Path,
    apply: bool = False,
    max_cases: int = DEFAULT_MAX_CASES,
    source_pointer: IndexPointer | None = None,
) -> SeedResult:
    """Measure — and on ``apply``, seed — the staging corpus slice.

    All three rails run first, before a single read: a pointer override in
    the environment is refused, then a destination that is or is inside
    either pinned source store, then a working file that would clobber the
    committed pointer. Then the slice is bounded, the census taken,
    and on an apply the content objects are copied **before** the rebuilt index
    blob is published — so a reader resolving the new pointer always finds the
    payloads its rows refer to. The reverse order would publish an index
    describing content that is not there yet, which is exactly the window a
    failed or interrupted run leaves open.

    ``source`` is the **pin**: where the slice is read from and what the
    destination rail compares against, stated by the caller rather than
    resolved from the environment — so a repointed environment cannot move
    either. Its content store is required at construction: that store is
    where a split-mode corpus keeps every payload, so a seed without one
    would publish rows with nothing to provision from — a hollow staging
    corpus that looks seeded. (:func:`census_slice` keeps its transport
    optional, because measuring a blob-only source is a coherent thing to
    want.) ``source_pointer`` is the source blob's resolved identity where
    the caller has one — rendered into the census so a stale pin is visible
    in the reading a maintainer does before an apply.

    ``stage_db`` is the runner-local working file the blob is built at; the
    published pointer is written beside it (:func:`upload_index`'s contract),
    which is where the caller reads the value a staging consumer must resolve.
    The transports default to S3 built from the pinned URLs; tests
    inject in-memory ones through the same seams the corpus transports already
    expose.
    """
    assert_no_pointer_override(settings)
    assert_destination_is_not_the_source(destination, source=source)
    assert_stage_db_is_not_the_corpus(stage_db, settings=settings)
    source_objects = source.object_transport()
    kept, dropped = bound_cases(case_ids, max_cases)
    census = census_slice(
        source_conn, kept, objects=source_objects, requested=len(case_ids), dropped=dropped
    )
    if not apply:
        return SeedResult(
            census=census,
            applied=False,
            rows=0,
            events=0,
            objects=CopyCounts(copied=0, skipped=0, unreadable=0),
            blob_bytes=0,
            pointer=None,
            source_pointer=source_pointer,
        )
    objects = copy_case_objects(source_objects, destination.object_transport(), kept)
    rows, events = build_slice_blob(source_conn, kept, stage_db)
    pointer = upload_index(
        stage_db, destination.remote_url.strip(), transport=destination.blob_transport
    )
    return SeedResult(
        census=census,
        applied=True,
        rows=rows,
        events=events,
        objects=objects,
        blob_bytes=stage_db.stat().st_size,
        pointer=pointer,
        source_pointer=source_pointer,
    )
