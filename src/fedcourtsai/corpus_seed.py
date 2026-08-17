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

**The safety rails, and what actually guarantees the property.** What makes it
impossible to write production here is **IAM**: the seeding role's policy is
read-only on the production stores, so no input and no bug in this module
reaches the production write path. The rails are the second line, and they earn
their place by turning a misconfiguration into a local refusal before anything
is read rather than an ``AccessDenied`` part-way through:
:func:`assert_destination_is_not_production` refuses a destination that is, or
is *inside*, either configured production store — resolved through the same
parsers the transports use, so no spelling of a location slips past — and
:func:`assert_stage_db_is_not_the_corpus` refuses a working file that would
overwrite the checkout's committed pointer. Everything else about the operation
is convergent rather than destructive — the remote is add-only and
content-addressed, the store copy skips keys already present — so a re-run
converges and a half-finished run is resumed by the next one.

**Ordering.** On an apply the content objects are copied *before* the blob is
published, mirroring the writers' blob-before-pointer rule one level up: a
reader that resolves the new pointer always finds the payloads its rows refer
to. A run interrupted between the two leaves a store ahead of its index, which
the next apply completes.

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
# "this case has no content".
_CASE_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]*/[0-9]+")

# Where a case's content objects live under its own prefix, used to classify a
# listed key for the census (the layout itself is `casestore`'s).
_SNAPSHOTS_SEGMENT = "/snapshots/"
_DOCUMENTS_SEGMENT = "/documents/"
_DOCUMENTS_MANIFEST = "/documents/documents.json"


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
        raw.extend(path.read_text().splitlines())
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

    def object_transport(self) -> ObjectTransport:
        """The destination content-store transport, built from the URL if unset."""
        if self.objects is not None:
            return self.objects
        bucket, prefix = parse_s3_url(self.casestore_url.strip())
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


def _production_locations(settings: Settings) -> dict[str, _Location]:
    """Both production stores as ``(bucket, prefix)``, failing closed if unset.

    An unset production URL is refused rather than skipped: without it the rail
    cannot tell a staging destination from production at all, and a rail that
    silently checks one half is worse than one that stops. The content-store
    URL is doubly required — it is also the slice's payload source, so a seed
    without it would publish rows with nothing to provision from.
    """
    locations: dict[str, _Location] = {}
    remote = settings.corpus_remote_url
    if remote is None or not remote.strip():
        raise SeedSliceError(
            "refusing to seed: the production corpus remote URL is not configured, so "
            "the rail cannot tell a staging destination from production. Set it to the "
            "production value (the workflow does) — see docs/security.md."
        )
    locations["corpus remote"] = _remote_location(
        remote, described_as="the production corpus remote URL"
    )
    store = settings.casestore_url
    if store is None or not store.strip():
        raise SeedSliceError(
            "refusing to seed: the production content-store URL is not configured. The "
            "rail cannot tell a staging destination from production without it, and it "
            "is the slice's payload source — see docs/security.md."
        )
    locations["content store"] = _store_location(
        store, described_as="the production content-store URL"
    )
    return locations


def assert_destination_is_not_production(destination: Destination, *, settings: Settings) -> None:
    """Refuse a destination that is, or is inside, either production store.

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
    * **bucket** — any destination sharing a bucket with either production
      store is refused whatever its prefix. That is the runbook's own
      invariant, that the staging pair is a separate bucket and not a prefix
      inside production's, enforced rather than merely stated — and it is what
      makes the rail robust to prefix spellings nobody enumerated.

    Both checks run in **both** destination slots against **both** production
    stores: a staging content store that happens to name the production corpus
    remote is just as wrong.

    This is the second line, not the guarantee. The first is IAM: the staging
    read-write role's policy is read-only on the production stores, so a
    destination that got past this rail still could not be written. The rail
    catches the misconfiguration the policy would turn into a confusing
    ``AccessDenied`` — and, being local, it catches it before anything is read.
    """
    production = _production_locations(settings)
    slots = (
        ("--dest-remote", _remote_location(destination.remote_url, described_as="--dest-remote")),
        (
            "--dest-casestore",
            _store_location(destination.casestore_url, described_as="--dest-casestore"),
        ),
    )
    for flag, location in slots:
        for name, configured in production.items():
            if location == configured:
                raise SeedSliceError(
                    f"refusing to seed: {flag} names the configured production {name}. "
                    "The staging corpus is its own bucket/prefix pair — see the "
                    "staging-corpus runbook in docs/security.md."
                )
            if location[0] == configured[0]:
                raise SeedSliceError(
                    f"refusing to seed: {flag} is a prefix inside the production "
                    f"{name}'s bucket. The staging corpus is a SEPARATE bucket, not a "
                    "prefix inside production's — see the staging-corpus runbook in "
                    "docs/security.md."
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
        cases.append(
            CaseCensus(
                case_id=case_id,
                present=row is not None,
                events=len(events),
                snapshots=sum(1 for key in keys if _SNAPSHOTS_SEGMENT in key),
                documents=sum(
                    1
                    for key in keys
                    if _DOCUMENTS_SEGMENT in key and not key.endswith(_DOCUMENTS_MANIFEST)
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


def copy_case_objects(
    source: ObjectTransport, dest: ObjectTransport, case_ids: Sequence[str]
) -> tuple[int, int]:
    """Copy every content object under each case's prefix; ``(copied, present)``.

    A key-level copy, so the destination holds the writers' own bytes rather
    than a re-serialization: dated snapshots, content-addressed document
    leaves, and the mutable manifests that point at them all arrive unchanged.
    Keys the destination already holds are skipped, which is what makes a
    re-run converge to no work — safe because the bulk objects are write-once
    and content-addressed, and because a manifest only ever gains entries. A
    key that lists but no longer reads is skipped rather than fatal: the
    listing is a moment older than the read, and a slice missing one leaf is
    worth more than a refused seed.
    """
    copied = present = 0
    for case_id in case_ids:
        for key in _case_keys(source, case_id):
            if dest.exists(key):
                present += 1
                continue
            body = source.get(key)
            if body is None:
                continue
            dest.put(key, body)
            copied += 1
    return copied, present


# --- the operation ------------------------------------------------------------


@dataclass(frozen=True)
class SeedResult:
    """What one ``corpus-seed-slice`` invocation measured and (maybe) wrote."""

    census: SliceCensus
    applied: bool
    rows: int
    events: int
    objects_copied: int
    objects_present: int
    blob_bytes: int
    pointer: IndexPointer | None

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
        if self.census.missing:
            missing = ", ".join(f"`{case_id}`" for case_id in self.census.missing)
            lines.append(f"- no row in the source corpus for: {missing}")
        if not self.applied:
            lines.append("- nothing written — re-dispatch with `apply` to seed.")
            return "\n".join(lines) + "\n"
        lines += [
            f"- copied **{self.objects_copied}** object(s) "
            + f"({self.objects_present} already present)",
            f"- published a {self.blob_bytes}-byte index blob",
        ]
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


def seed_slice(
    *,
    source_conn: ReadConnection,
    case_ids: Sequence[str],
    destination: Destination,
    settings: Settings,
    stage_db: Path,
    source_objects: ObjectTransport | None = None,
    apply: bool = False,
    max_cases: int = DEFAULT_MAX_CASES,
) -> SeedResult:
    """Measure — and on ``apply``, seed — the staging corpus slice.

    The safety rail runs first, before a single read: a destination naming
    either production store is refused outright. Then the slice is bounded, the
    census taken, and on an apply the content objects are copied before the
    rebuilt index blob is published, so a reader resolving the new pointer
    always finds the payloads its rows refer to.

    ``stage_db`` is the runner-local working file the blob is built at; the
    published pointer is written beside it (:func:`upload_index`'s contract),
    which is where the caller reads the value a staging consumer must resolve.
    The destination's transports default to S3 built from its URLs; tests
    inject in-memory ones through the same seams the corpus transports already
    expose.
    """
    assert_destination_is_not_production(destination, settings=settings)
    assert_stage_db_is_not_the_corpus(stage_db, settings=settings)
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
            objects_copied=0,
            objects_present=0,
            blob_bytes=0,
            pointer=None,
        )
    copied = present = 0
    if source_objects is not None:
        copied, present = copy_case_objects(source_objects, destination.object_transport(), kept)
    rows, events = build_slice_blob(source_conn, kept, stage_db)
    pointer = upload_index(
        stage_db, destination.remote_url.strip(), transport=destination.blob_transport
    )
    return SeedResult(
        census=census,
        applied=True,
        rows=rows,
        events=events,
        objects_copied=copied,
        objects_present=present,
        blob_bytes=stage_db.stat().st_size,
        pointer=pointer,
    )
