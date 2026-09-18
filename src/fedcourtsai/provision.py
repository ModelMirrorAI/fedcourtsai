"""What a provisioned cell reads: the backend it comes from, and where it is cut.

The predict/evaluate cells materialize a read-only ``record/`` — the point-in-time
snapshot, the case's documents, and the predictable event — from the corpus. Three
questions this module answers for the provisioning callers, so ``cli`` stays a
thin caller and the local cascade is not a second implementation:

*Which store serves the read.* :class:`CasestoreSource` returns the **same
shapes** as the corpus read functions (``latest_snapshot`` / ``snapshot_at`` /
``documents_for_case`` / ``events_for_case``) out of the per-case content store
(:mod:`fedcourtsai.casestore`) rather than the SQLite corpus, behind
``--corpus-backend casestore``, so a cell's ``record/`` is **byte-identical**
whichever backend produced it — proven by ``tests/test_provision_casestore.py``.

*Where the read is cut.* :func:`moment_cutoff` and :func:`documents_before` place
a forward cell at the declared moment it forecasts instead of at the latest
snapshot, so a later moment is conditioned on the information set it declares;
:func:`place_at_moment` composes the two bounds into the payload and documents a
cell actually receives.

*What lands on disk.* :func:`write_cell_record` writes that placement to the
gitignored ``record/`` — the dated snapshot, the ``context.json`` conditioning
stamp, and ``documents/`` with its manifest. One writer, because a cell's record
is one thing: the provisioning command and the local cascade both reach it here,
so neither can hand an agent a record shaped differently from the other's.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Literal

from . import casestore
from .corpus import CaseDocument, CorpusEvent, CorpusRow
from .paths import CasePaths
from .pipeline import arrival_cut, cell_context, cert_signals, moments
from .schemas import Moment, Stage
from .serialize import write_raw_json, write_text


class ProvisionError(RuntimeError):
    """A provisioning-source configuration problem, surfaced with context."""


class UnanchorableMoment(ProvisionError):
    """An interim arrival cell whose opening entry cannot be located in the snapshot.

    Raised by :func:`place_at_moment`, and deliberately not recoverable: the
    anchor bound is the conditioning the date rule exists to replace, so a cell
    that fell back to the date rule would carry the defect together with a record
    saying it had been fixed. Callers refuse the cell.
    """


@dataclass(frozen=True)
class CellRead:
    """Everything one backend read hands a cell's provisioning.

    One object because it is one read. The reads ride a single connection so a
    ranged cell opens one and its egress counters are the whole story, and a
    caller that fetched these piecemeal would either reopen the connection or
    quietly give that up.

    ``row`` is present only where the terminal gate needs it, and ``cutoff`` /
    ``dated`` only where the cell's event declares a moment to be placed at —
    ``cutoff`` is where that moment falls, ``dated`` the stored snapshot from
    before it, if the corpus kept one.
    """

    latest: tuple[date, dict[str, Any]] | None
    documents: list[CaseDocument]
    events: list[CorpusEvent]
    row: CorpusRow | None
    cutoff: date | None
    dated: tuple[date, dict[str, Any]] | None


class CasestoreSource:
    """Read a case's snapshot / documents / events from the per-case content store.

    Mirrors the corpus read functions the provisioning commands use, so a
    casestore-sourced ``record/`` is byte-identical to a corpus-sourced one. Thin
    over the shared ``casestore.read_*`` helpers (the same implementation the
    process read source uses under the corpus-split mode), bound to an explicit
    transport so a test can point it at an in-memory store.
    """

    def __init__(self, transport: casestore.ObjectTransport) -> None:
        self._transport = transport

    def latest_snapshot(self, case_id: str) -> tuple[date, dict[str, Any]] | None:
        """The newest dated snapshot — ``(date, payload)`` — or ``None``."""
        return casestore.read_latest_snapshot(self._transport, case_id)

    def snapshot_at(self, case_id: str, *, before: date) -> tuple[date, dict[str, Any]] | None:
        """The newest dated snapshot strictly before ``before``, or ``None``.

        The exclusive bound of ``corpus.snapshot_at``, and for the same reason: a
        snapshot pulled *on* the cutoff day may already carry that day's entries.
        """
        return casestore.read_snapshot_at(self._transport, case_id, before=before)

    def documents_for_case(self, case_id: str) -> list[CaseDocument]:
        """The case's documents, kind-ordered, reconstructed from the manifest + leaves."""
        return casestore.read_documents(self._transport, case_id)

    def events_for_case(self, case_id: str) -> list[CorpusEvent]:
        """The case's predictable events, event_id-ordered (empty if none stored)."""
        return casestore.read_events(self._transport, case_id)


def casestore_source_from_settings() -> CasestoreSource:
    """Build a :class:`CasestoreSource` from the environment's store address.

    Raises :class:`ProvisionError` when the store is not configured — the casestore
    backend cannot serve reads without it.
    """
    transport = casestore.transport_from_settings()
    if transport is None:
        raise ProvisionError(
            "the casestore backend needs the content store addressed: set "
            "CORPUS_BASE_URL (one address per environment, both halves derived) "
            "or FEDCOURTS_CASESTORE_URL (s3://<bucket>[/<prefix>])"
        )
    return CasestoreSource(transport)


def moment_cutoff(event_id: str, events: Sequence[CorpusEvent]) -> date | None:
    """Where a forward cell for ``event_id`` is placed, or ``None`` for no cut.

    A stage's later moments exist *because* their information sets differ: a
    merits cell forecast at the grant is a different forecast from the same case
    once it is briefed. The declaration is what makes them different, so
    provisioning has to enforce it — a grant-moment cell handed the latest
    snapshot reads the merits briefs and the argument setting that only the
    briefed moment declares, and the two moments collapse into one.

    The cutoff is the day **after** the event opened, exclusive, so the trigger
    entry itself survives and everything filed after it does not — the same shape
    every reconstruction moment takes (:class:`fedcourtsai.pipeline.asof.CutoffPolicy`),
    and the shape that makes a forward cell and a replay of it comparable.

    ``None`` — no cut, the cell reads the latest snapshot — in three cases, each
    of which is an absent declaration rather than a permission:

    * ``event_id`` names no declared moment: an entry-pinned event the extractor
      minted has no declared information set to be placed at.
    * The moment declares that its ``opened_at`` is not its trigger
      (``opened_at_is_the_moment``), which is the cert petition baseline.
    * No event row, or a row whose ``opened_at`` was never recorded: the moment
      is declared but the date it happened is not, and a guessed cutoff would
      condition the cell on a fiction.
    """
    spec = moments.spec_for(event_id)
    if spec is None or not spec.opened_at_is_the_moment:
        return None
    row = next((event for event in events if event.event_id == event_id), None)
    if row is None or row.opened_at is None:
        return None
    return row.opened_at + timedelta(days=1)


def is_interim_arrival(event_id: str) -> bool:
    """Whether ``event_id`` names the interim stage's arrival moment.

    The one moment whose trigger is a docket entry the cell can be placed *at*
    rather than a day it can be placed *within*, and therefore the one that takes
    the anchor bound (:mod:`fedcourtsai.pipeline.arrival_cut`). An application is
    submitted, referred and sometimes disposed of inside a single day, so a
    date-valued cut hands the cell its own outcome; a cert or merits moment's
    trigger has no such intra-day tail to exclude.

    Read off the declared moment rather than the event id's spelling, so a moment
    added to the interim stage at the arrival position takes the bound without a
    second place having to be edited.
    """
    spec = moments.spec_for(event_id)
    return spec is not None and spec.stage is Stage.interim and spec.moment is Moment.arrival


def shows_the_moment(payload: Mapping[str, Any], cutoff: date) -> bool:
    """Whether ``payload`` is late enough to show the moment ``cutoff`` was taken from.

    A stored snapshot from before the cutoff is the better evidence *only if it
    reaches the trigger*. Nothing bounds it from below: the newest one the corpus
    kept may predate the moment by weeks, and an event opened by a backfill —
    a merits moment stamped at the row's latched grant date long after the fact —
    can have no stored snapshot anywhere near it. Handing that to a cell would
    place it before its own moment (a merits cell reading a still-pending
    petition) while the artifact recorded ``dated`` at the moment's cutoff, and
    two cells of one cohort would carry materially different information sets
    with nothing to tell them apart.

    So the payload has to carry an entry from the trigger day itself — the day
    the cutoff was taken from, ``cutoff`` being exclusive and one day after it.
    False where it does not, and where the payload discloses no dated
    proceedings at all: neither can be shown to reach the moment, and
    reconstructing from the later payload is what does.
    """
    trigger = cutoff - timedelta(days=1)
    return any(
        (filed := cert_signals.entry_date(raw)) is not None and filed >= trigger
        for _, raw in cert_signals.proceedings_entries(payload)
    )


#: Top-level payload fields carrying a date of the docket's own, so the rule
#: that cuts the proceedings cuts these too. ``date_filed`` is deliberately
#: absent: the docket's arrival precedes every moment by construction, and
#: subjecting it to a fail-closed parse would drop the one field that identifies
#: what the cell is looking at.
_DATE_KEYED_FIELDS: tuple[str, ...] = (
    "date_argued",
    "date_reargued",
    "date_terminated",
    "date_decided",
    "date_cert_granted",
    "date_cert_denied",
    "date_rehearing_denied",
)

#: The payload's own generation stamp — a fact about the *pull*, not the docket.
_GENERATION_STAMPS: tuple[str, ...] = ("sJsonCreationDate",)


def cut_dated_fields(payload: Mapping[str, Any], cutoff: date) -> dict[str, Any]:
    """``payload`` with its post-cutoff top-level dates removed.

    The truncation's own principle, applied to the fields it does not reach.
    Cutting the proceedings but leaving ``date_argued`` set removes the argument
    *entry* from a grant-moment cell while handing it the argument *date* — the
    docket says the case was argued either way, and the cut would be a claim the
    payload contradicts. Content offers no rule here, but a date does: a value
    falling on or after the cutoff records something the cell's moment had not
    reached.

    **Fails closed on an unparseable value**, exactly as the entry rule does: a
    date that cannot be read cannot be shown to predate the moment. A genuinely
    pre-cutoff date is kept, because it was true at the moment and is part of
    what the cell should see.

    The generation stamp goes unconditionally. It dates the *pull* the payload
    was reconstructed from, so on a re-dated snapshot it is months ahead of every
    other date in the file — and re-stamping it with the cutoff would assert a
    pull that never happened. Absence is the honest record of a reconstruction.

    This is for the reconstructed branch only. A ``dated`` payload is what the
    docket really served, and its fields were true when it served them.
    """
    out = dict(payload)
    for key in _DATE_KEYED_FIELDS:
        if key not in out:
            continue
        value = cert_signals.entry_date(str(out[key]) if out[key] is not None else None)
        if value is None or value >= cutoff:
            del out[key]
    for key in _GENERATION_STAMPS:
        out.pop(key, None)
    return out


def truncate_snapshot(
    payload: Mapping[str, Any], cutoff: date | None
) -> tuple[dict[str, Any], int]:
    """The docket as it stood strictly before ``cutoff``, and how many entries went.

    ``cutoff=None`` removes the proceedings **key**, not just its contents: when
    no forward moment could be identified the docket's posture is unknown, and an
    empty list would instead assert that it was empty. A real cutoff leaves the
    list even when nothing survives, because that genuinely is an observation.

    **Fails closed on an undated entry.** An entry whose date is missing or
    unparseable is dropped, because it could be the disposing order and nothing
    about it says otherwise. That costs a little pre-decision context and cannot
    leak an outcome, which is the right way round.

    A surviving entry is reduced to the fields a consumer reads (see
    :data:`_ENTRY_FIELDS`), because the outcome blocklist matches top-level keys
    only and nothing else screens what an entry nests.

    Entry ids are positional and assigned on read, so truncating the *tail*
    renumbers nothing. Dropping an undated entry from the *middle* does shift
    everything after it — accepted, because the alternative is keeping an entry
    that could be the disposing order, and nothing downstream pins an id across a
    truncation.
    """
    out = dict(payload)
    dropped = 0
    for key in cert_signals.PROCEEDINGS_KEYS:
        entries = out.get(key)
        if not isinstance(entries, list):
            continue
        if cutoff is None:
            # No cutoff means no moment could be identified, so the key is removed
            # outright rather than emptied. An empty list is an observation — "the
            # docket had no entries then" — and this is the opposite of one. Left
            # as `[]`, a cell would read zero distributions and claim the weakest
            # band about a petition whose posture is entirely unknown.
            dropped += len(entries)
            del out[key]
            continue
        kept: list[Any] = []
        for entry in entries:
            filed = (
                cert_signals.entry_date(_entry_raw_date(entry))
                if isinstance(entry, Mapping)
                else None
            )
            if filed is not None and filed < cutoff:
                kept.append(_entry_fields(entry))
            else:
                dropped += 1
        # A real cutoff with nothing surviving IS an observation: as at that date
        # the docket carried no entries, and `[]` says so.
        out[key] = kept
    return out, dropped


#: What a surviving entry keeps. The outcome blocklist matches **top-level** keys,
#: so nothing screens the structures nested inside an entry — a live entry's
#: `Links` (document pointers; a replay cell is provisioned no documents, so this
#: would be its only path to one) or a REST entry's `recap_documents`, which
#: carries document text and its own upload date. Rather than extend a blocklist
#: to a shape upstream can change under us, keep only the two fields every
#: consumer actually reads and drop the rest.
_ENTRY_FIELDS: tuple[str, ...] = ("Date", "Text", "date_filed", "description")


def _entry_fields(entry: Mapping[str, Any]) -> dict[str, Any]:
    """A surviving entry reduced to the fields a consumer reads."""
    return {key: entry[key] for key in _ENTRY_FIELDS if key in entry}


def _entry_raw_date(entry: Mapping[str, Any]) -> str | None:
    """An entry's own date string, over either payload shape."""
    raw = entry.get("Date") if "Date" in entry else entry.get("date_filed")
    return str(raw) if raw else None


def documents_before(documents: Iterable[CaseDocument], cutoff: date) -> list[CaseDocument]:
    """The documents on the docket strictly before ``cutoff``.

    The snapshot's cut is only half a cell's information set: the merits briefs a
    grant-moment cell must not read arrive as *documents*, and a filtered snapshot
    beside an unfiltered ``record/documents/`` would hand them over anyway.

    A document is placed by ``entry_date`` — the proceedings entry its link rode
    on, which is when it reached the docket. That date is stored verbatim and
    parsed strictly (:func:`fedcourtsai.pipeline.cert_signals.entry_date`), so a
    missing or partial string yields nothing to compare; those fall back to
    ``fetched_at``, which is safe in exactly one direction — the pipeline cannot
    fetch a document before it is filed, so a fetch before the cutoff means a
    filing before the cutoff. The reverse does not hold (a backfill fetches an old
    document late), so the fallback drops documents a cell could have read rather
    than keeping ones it could not.

    Two residuals the date cannot reach, both from a row holding more text than
    its one date describes.

    The first is **combination**. A multi-respondent case's opposition briefs are
    stored as one ``brief-in-opposition`` row dated by the earliest of them
    (:mod:`fedcourtsai.pipeline.documents`), and a row is kept or dropped whole —
    so a cutoff falling between two constituents admits the later one's text as
    though it had been filed at the earlier date. Dating the row at its *last*
    brief would close that at a price this cut is not willing to pay: the whole
    opposition, lead respondent included, dropped from every cell placed between
    the two. Nothing here can cut inside a stored row, so what bounds this
    residual is how narrow the selector's arm for the kind is, not this function.

    The second is **supersession**. Documents are keyed ``(case_id, kind)``
    and the latest fetch of a kind wins, so a *corrected* filing supersedes the
    original under the entry date of whichever fetch is stored. A pre-cutoff
    ``entry_date`` therefore admits the text as later amended, not necessarily
    the text as it read at the moment. The corpus keeps no per-kind history to
    place the earlier version against, and the alternative — dropping every
    document whose kind was ever re-fetched — would cost a cell its petition.
    """
    kept: list[CaseDocument] = []
    for document in documents:
        filed = cert_signals.entry_date(document.entry_date)
        placed = filed if filed is not None else document.fetched_at
        if placed < cutoff:
            kept.append(document)
    return kept


@dataclass(frozen=True)
class Placement:
    """A cell's inputs after the moment cut, and the boundary its context records.

    ``dropped_entries`` / ``dropped_documents`` are the auditable size of what the
    placement excluded. They are deliberately **not** carried into
    ``context.json``: the cell reads that file, and how much a cut removed
    separates a grant from a denial about as cleanly as the disposing order does.
    They belong in the harness's own log, which is why they ride out here instead.
    """

    snapshot_date: date
    payload: dict[str, Any]
    documents: list[CaseDocument]
    provenance: Literal["as-stored", "dated", "truncated"]
    boundary: arrival_cut.CutBoundary | None
    dropped_entries: int
    dropped_documents: int


def place_at_moment(
    case: str,
    event: str,
    cutoff: date | None,
    read: CellRead,
    *,
    payload: dict[str, Any],
    snapshot_date: date,
    documents: list[CaseDocument],
) -> Placement:
    """Cut a cell's snapshot and documents to the moment its event declares.

    ``cutoff is None`` is the no-cut case and passes everything through as read.
    Otherwise two bounds compose, in this order and no other. The **anchor bound**
    (:mod:`fedcourtsai.pipeline.arrival_cut`, on the interim arrival moment only)
    runs on the payload as the corpus served it, so the anchor index it records is
    a position in that list rather than in one the date rule has already thinned.
    Then the **date rule** reconstructs, where no stored snapshot from before the
    cutoff reaches the moment.

    Raises :class:`UnanchorableMoment` where an interim arrival's opening entry
    cannot be anchored. There is deliberately no fall back to the date rule alone:
    that rule is the conditioning the anchor bound replaces, and a cell taking it
    while its context recorded the tighter one would carry the defect together
    with a record saying it had been fixed. ``arrival-cut-ledger`` counts those
    refusals.
    """
    provenance: Literal["as-stored", "dated", "truncated"] = "as-stored"
    if cutoff is None:
        return Placement(snapshot_date, payload, documents, provenance, None, 0, 0)
    # Nothing is removed from a `dated` payload by the DATE rule: it is what the
    # docket served. The anchor bound below can still remove from it.
    dropped_entries = 0
    reconstruct = read.dated is None or not shows_the_moment(read.dated[1], cutoff)
    if not reconstruct and read.dated is not None:
        # What the docket really served at the moment, which also knows what had
        # not yet been filed — strictly better than reconstructing it, so it is
        # preferred and recorded apart. Only where it reaches the trigger, though:
        # a stored snapshot from well before the moment would place the cell
        # earlier than the cohort it is filed under.
        snapshot_date, payload = read.dated
        provenance = "dated"
    boundary = arrival_cut.CutBoundary(kind="date")
    if is_interim_arrival(event):
        # The anchor bound, before the date rule and on BOTH provenances. A
        # `dated` payload is exempt from the date rule because the docket really
        # served it — but it can have been served on the opening day itself, after
        # that day's referral or disposition was docketed, so the one branch that
        # reads a payload unmodified is the branch this bound is most needed on.
        anchored = arrival_cut.cut_at_arrival(
            payload,
            docket_number=arrival_cut.payload_docket_number(payload),
            opened_at=cutoff - timedelta(days=1),
        )
        if anchored is None:
            raise UnanchorableMoment(
                f"refusing to provision {case} {event}: the opening entry could not "
                "be anchored in the snapshot, so the arrival moment's information "
                "set cannot be located"
            )
        payload = anchored.payload
        boundary = arrival_cut.CutBoundary(
            kind="arrival-position", anchor_index=anchored.anchor_index
        )
        dropped_entries += anchored.dropped_same_day
    if reconstruct:
        # Reconstructed from a later payload: post-cutoff entries removed, and an
        # entry whose date is missing or unparseable removed with them
        # (`truncate_snapshot` fails closed — an undated entry could be the one
        # that decides the case). Never `blind`: this path always holds a cutoff to
        # keep entries against, so it never removes the proceedings key outright,
        # which is what that provenance records.
        payload, date_dropped = truncate_snapshot(payload, cutoff)
        dropped_entries += date_dropped
        # The same date rule over the top-level fields truncation does not reach,
        # so the cut docket does not carry an argument date whose entry it just
        # removed.
        payload = cut_dated_fields(payload, cutoff)
        # The docket as at the cutoff is dated by the cutoff, not by the pull whose
        # bytes it was reconstructed from — otherwise the one file the cell's
        # information set is judged against carries a later date than anything in
        # it.
        snapshot_date = cutoff
        provenance = "truncated"
    # Documents take the DATE rule under either cut kind, and that residual is
    # stated rather than closed: a document is placed by the entry date its link
    # rode on, which cannot say where inside the opening day it sat, and the one
    # document an arrival cell most needs — the application itself — is filed on
    # that day. Tightening to the day before would cost the cell its own
    # application to remove a tail the corpus cannot locate.
    kept = documents_before(documents, cutoff)
    return Placement(
        snapshot_date,
        payload,
        kept,
        provenance,
        boundary,
        dropped_entries,
        len(documents) - len(kept),
    )


def write_cell_record(
    paths: CasePaths,
    case_id: str,
    placement: Placement,
    *,
    mode: str,
    cutoff: date | None,
    snapshot_dest: Path | None = None,
) -> Path:
    """Materialize one cell's whole ``record/``, and return the snapshot's path.

    Three files, written together because they describe one information set: the
    dated snapshot, the ``context.json`` the prompt contract reads its mode and
    conditioning from, and ``documents/`` with the manifest naming what is there.
    A caller that wrote only the first would hand an agent a snapshot with no
    frozen mode, band or cutoff beside it — the cell would then have to guess its
    own posture, which is the one thing provisioning exists to settle.

    Every document kind is screened **before the first write**, so a record is
    either whole or absent: a refusal after the snapshot and the context had
    landed would leave a half-provisioned record that ``assert-cell-record``
    reads as complete.

    Every record subtree this write owns is then **cleared**, so what is on disk
    is exactly what this placement put there. Ephemeral runners never reach the
    state the clearing guards; a tree that provisions twice — the local cascade,
    moving from one event's moment to the next — does, and a document the tighter
    cut dropped would otherwise still be sitting in ``documents/`` for the next
    cell to read.

    The opinion slot goes with them, and it is the one that matters most: a
    majority opinion postdates every predict moment by construction, so a body
    :func:`fedcourtsai.cli.provision_opinion` staged earlier in the same tree
    would reach a predict cell whose ``context.json`` says it was placed at its
    moment. Clearing here is safe because the evaluate lane stages the opinion
    *after* this write, never before.

    ``snapshot_dest`` sends the payload somewhere else entirely, which is a
    caller asking for a copy rather than for a cell's record; the clearing is
    skipped there, since emptying the record to write outside it would destroy a
    provisioned cell on behalf of a command that provisioned none.
    """
    kinds = [_checked_kind(doc.kind) for doc in placement.documents]
    if snapshot_dest is None:
        _clear_dir(paths.snapshots_dir)
        _clear_dir(paths.documents_dir)
        clear_opinion_slot(paths)
    dest = snapshot_dest or paths.snapshot(placement.snapshot_date.isoformat())
    write_raw_json(dest, placement.payload)
    # The cell's context: its mode, and the conditioning state it is about to run
    # against. Both are stated at provisioning — the mode so the prompt contract
    # keys replay etiquette on it rather than inferring from env vars, and the
    # rest because the salience band only ever strengthens, so a band re-derived
    # later is the band the petition *ended* at. Derived from the payload rather
    # than the corpus row: the row holds current values, the payload is what this
    # cell can read, and a baseline has to be conditioned on the latter. The
    # cutoff rides along as the cohort marker: a forward cell whose `cutoff` is
    # non-null was placed at its moment, and a figure that pools it with one
    # provisioned from the latest snapshot pools two information sets.
    write_raw_json(
        paths.cell_context,
        cell_context.build(
            case_id,
            placement.snapshot_date,
            placement.payload,
            mode,
            provenance=placement.provenance,
            cutoff=cutoff,
            boundary=placement.boundary,
        ).model_dump(mode="json"),
    )
    for kind, doc in zip(kinds, placement.documents, strict=True):
        write_text(paths.document(kind), doc.text)
    if placement.documents:
        write_raw_json(paths.documents_manifest, document_manifest(placement.documents))
    return dest


def document_manifest(documents: Sequence[CaseDocument]) -> list[dict[str, Any]]:
    """The ``documents.json`` rows describing a cell's provisioned documents.

    Every stored field but the text itself, so the row's own ``ocr_derived``
    marker reaches the cell: text a recovery pass read off a page image is a lossy
    derivation of the filing, and a manifest that dropped the marker would present
    it as a clean extraction.
    """
    return [
        {
            **doc.model_dump(mode="json", exclude={"text"}),
            # A present document whose extracted text is blank/whitespace (a
            # scanned PDF with no text layer) would read as usable from
            # pages/truncated alone; flag it so the cell distinguishes
            # "no document" / "document present but no text layer" / "text
            # present". Derived here, not stored on the row.
            "empty_text": not doc.text.strip(),
        }
        for doc in documents
    ]


def clear_opinion_slot(paths: CasePaths) -> None:
    """Remove a previously staged opinion, so "no slot" always means "no body".

    The slot's whole contract is that its **absence** tells a grader there is
    nothing to grade against, and — because an opinion postdates every predict
    moment — that a predict cell was never handed one. A run that stages nothing
    and leaves an older body in place would break both on the one tree where it
    can happen, a re-provision over a dirty checkout, and the grader would read a
    stale opinion as this cell's. Ephemeral runners never reach the state; the
    invariant is stated unconditionally, so it holds unconditionally.
    """
    paths.opinion_text.unlink(missing_ok=True)
    paths.opinion_manifest.unlink(missing_ok=True)
    if paths.opinion_dir.is_dir() and not any(paths.opinion_dir.iterdir()):
        paths.opinion_dir.rmdir()


#: A document kind, as it is allowed to appear in a `record/documents/` filename.
#: Every stored kind is a module constant (:mod:`fedcourtsai.pipeline.documents`),
#: never docket text — but this is the one seam that turns a corpus-supplied
#: string into a path, and the screen costs a regex.
_DOCUMENT_KIND = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _checked_kind(kind: str) -> str:
    """``kind`` if it is a bare filename stem, else a refusal naming it."""
    if not _DOCUMENT_KIND.match(kind):
        raise ProvisionError(
            f"refusing to provision a document of kind {kind!r}: a kind names a "
            "file inside the cell's record and must be a bare lowercase stem"
        )
    return kind


def _clear_dir(directory: Path) -> None:
    """Remove a record subdirectory's files, so "absent" always means "not placed".

    Files only, and that is the whole reach: every writer of these two directories
    goes through :func:`write_cell_record`, which lays down flat files named by
    :func:`_checked_kind` and by a date, so a nested path under one of them is a
    tree nothing here made and nothing here should silently delete.
    """
    if not directory.is_dir():
        return
    for entry in directory.iterdir():
        if entry.is_file():
            entry.unlink()
