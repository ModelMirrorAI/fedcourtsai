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
a cell, forward or replay, at the declared moment it forecasts instead of at the latest
snapshot, so a later moment is conditioned on the information set it declares;
:func:`place_at_moment` composes the anchor bound and the date rule into the
payload and documents a cell actually receives.

*What lands on disk.* :func:`write_cell_record` writes that placement to the
gitignored ``record/`` — the dated snapshot, the ``context.json`` conditioning
stamp, ``documents/`` with its manifest, and ``related/`` with the
``Vide``-linked dockets cut to the cell's moment and redacted
(:func:`place_related`), the snapshot and documents through the contact-detail
scrubs. One writer, because a cell's record is one thing: the
``provision-snapshot`` command and the local cascade both reach it here, so
neither can hand an agent a record shaped differently from the other's.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Literal

from . import casestore
from .corpus import CaseDocument, CorpusEvent, CorpusRow, normalize_docket_number
from .paths import CasePaths
from .pipeline import arrival_cut, cell_context, cert_signals, interim_signals, moments
from .pipeline.documents import (
    KIND_ARGUMENT_TRANSCRIPT,
    KIND_DESCRIPTIONS,
    OTHER_LIST,
    ScrubbedSnapshot,
    ScrubbedText,
    party_contact_values,
    scrub_contact_details,
    scrub_snapshot_contacts,
    unrepresented_sides,
)
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
class RelatedRead:
    """One ``Vide``-linked docket as the cell's read found it.

    ``case_id`` is ``None`` where no live corpus row carries the number, and
    ``latest`` where the row has no stored snapshot; ``unread`` says why
    nothing was looked up at all (no index to resolve through). Every link is
    still recorded in the manifest, so a cell can tell a docket the corpus does
    not hold from one the Court never linked.
    """

    docket_number: str
    case_id: str | None
    latest: tuple[date, dict[str, Any]] | None
    unread: str | None = None


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
    """Where a cell for ``event_id`` is placed, or ``None`` for no cut.

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


class TriggerAbsent(ProvisionError):
    """A placed cell whose snapshot does not carry the entry that opened its moment.

    Raised by :func:`place_at_moment` on a moment with a :data:`TRIGGER_READERS`
    reader, once neither the stored snapshot from before the cutoff nor the
    reconstruction from the latest payload carries the trigger entry. Not
    recoverable here, for the reason :class:`UnanchorableMoment` is not: a cell
    placed on a docket missing its own trigger is forecast from the moment
    *before* the one it is filed under, and an increment claim keyed on that
    trigger would then resolve on the very entry that defined the cell. Callers
    refuse the cell; a later round owes it again once the corpus holds a payload
    that carries the entry.
    """


TriggerReader = Callable[[Mapping[str, Any]], date | None]


def _cvsg_trigger(payload: Mapping[str, Any]) -> date | None:
    return cert_signals.entry_date(cert_signals.snapshot_cvsg_date(payload))


def _sg_brief_trigger(payload: Mapping[str, Any]) -> date | None:
    return cert_signals.sg_brief_date(payload)


def _call_for_response_trigger(payload: Mapping[str, Any]) -> date | None:
    return cert_signals.call_for_response_date(payload)


def _relist_trigger(payload: Mapping[str, Any]) -> date | None:
    return cert_signals.first_relist_date(payload)


def _response_requested_trigger(payload: Mapping[str, Any]) -> date | None:
    return interim_signals.response_requested_date(cert_signals.proceedings_entries(payload))


def _response_filed_trigger(payload: Mapping[str, Any]) -> date | None:
    return interim_signals.response_filed_date(cert_signals.proceedings_entries(payload))


#: The moments whose trigger is one docket entry, each read by the same parse
#: that dated the event's ``opened_at`` at ingest, so a payload the reader finds
#: nothing in is one the event could not have been dated from. A day can carry
#: more than one entry — an application docketed on the day the Court asks for a
#: response to it — so for these moments an entry from the trigger *day* is not
#: evidence of the trigger *entry*.
#:
#: Each reader takes the **first** dated matching entry, as ingest does, and
#: parses its date strictly (:func:`cert_signals.entry_date`). A trigger whose
#: date the strict parse cannot read is read as absent, which reconstructs or
#: refuses rather than placing a cell — the safe direction.
#:
#: Moments absent here keep the day rule in :func:`shows_the_moment`. The interim
#: arrival moment has the anchor bound instead (:mod:`.pipeline.arrival_cut`),
#: which already refuses a snapshot without its opening entry; the cert arrival
#: moment opens at docketing, which no entry dates; and the three merits moments
#: are dated by readers that do not take a bare payload — the grant off the
#: resolution, the briefed moment off a brief bounded by that grant, the
#: post-argument moment off the Court's transcript list — so reading them here
#: would be a second parse that can disagree with the first.
TRIGGER_READERS: Mapping[tuple[Stage, Moment], TriggerReader] = MappingProxyType(
    {
        (Stage.cert, Moment.cvsg): _cvsg_trigger,
        (Stage.cert, Moment.sg_brief): _sg_brief_trigger,
        (Stage.cert, Moment.response_requested): _call_for_response_trigger,
        (Stage.cert, Moment.relist): _relist_trigger,
        (Stage.interim, Moment.response_requested): _response_requested_trigger,
        (Stage.interim, Moment.response_filed): _response_filed_trigger,
    }
)


def trigger_reader(event_id: str) -> TriggerReader | None:
    """The reader for ``event_id``'s trigger entry, or ``None`` if its moment has none."""
    spec = moments.spec_for(event_id)
    if spec is None:
        return None
    return TRIGGER_READERS.get((spec.stage, spec.moment))


def dated_from_trigger(payload: Mapping[str, Any], cutoff: date, reader: TriggerReader) -> bool:
    """Whether ``payload``'s trigger is the entry the event was dated from.

    Exact: the trigger ``reader`` finds must fall on the day the event opened,
    ``cutoff`` being exclusive and one day after it. This is the test a stored
    snapshot from before the cutoff has to pass to be taken as ``dated``. Being
    before the cutoff is not enough, because nothing bounds a stored snapshot from
    below: one carrying an older matching entry and nothing from the trigger day
    may predate the moment by weeks, and is not the docket as it stood then.
    """
    return reader(payload) == cutoff - timedelta(days=1)


def carries_trigger(payload: Mapping[str, Any], cutoff: date, reader: TriggerReader) -> bool:
    """Whether ``payload`` carries a trigger entry ``reader`` finds before ``cutoff``.

    The test the *placed* payload has to pass, whichever branch built it. Looser
    than :func:`dated_from_trigger` on purpose: a reconstruction is the latest
    payload cut at the cutoff, so it has no lower-bound problem — every entry the
    docket held before the cutoff is on it. A trigger dated earlier than the event
    (an entry backdated after the pull that dated the event) is still the moment
    having happened by the cutoff, and the cell is placed with it rather than
    refused on a disagreement no later pull could resolve.
    """
    found = reader(payload)
    return found is not None and found < cutoff


def shows_the_moment(payload: Mapping[str, Any], cutoff: date, event_id: str) -> bool:
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

    Where the moment has a trigger reader (:data:`TRIGGER_READERS`), the payload
    has to carry the trigger entry itself, dated on the day the event opened
    (:func:`dated_from_trigger`). A pull taken earlier on the trigger day carries
    that day's other entries and not the trigger, so the day alone would take it
    as ``dated``. Every other moment falls back to the day rule:
    the payload carries an entry from the trigger day — the day the cutoff was
    taken from, ``cutoff`` being exclusive and one day after it.

    False where neither holds, and where the payload discloses no dated
    proceedings at all: none of these can be shown to reach the moment, and
    reconstructing from the later payload is what does.
    """
    reader = trigger_reader(event_id)
    if reader is not None:
        return dated_from_trigger(payload, cutoff, reader)
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
GENERATION_STAMPS: tuple[str, ...] = ("sJsonCreationDate",)


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
    for key in GENERATION_STAMPS:
        out.pop(key, None)
    return out


# Snapshot fields that reveal the outcome — because they exist only once the
# matter was decided (or record the decision), or because they accrue with the
# proceedings and so, on a decided docket, betray it — stripped before an
# agentic replay sees the docket. This blocklist is key-name-based, so every
# channel's outcome-bearing keys must be listed.
#
# The proceedings entries are NOT here: they are truncated by date instead
# (`truncate_snapshot`). Content offers no rule that separates a disposing order
# from a pre-decision entry, but a date does — an entry filed before the cutoff
# cannot record a decision that came after it. Dropping them wholesale left a
# replay cell reading a docket with no history at all, which is not the docket
# any forward cell ever saw, and left it unable to observe its own salience band.
# Truncation is applied on top of this list, never instead of it.
SNAPSHOT_OUTCOME_FIELDS: tuple[str, ...] = (
    "disposition",
    "date_terminated",
    "date_decided",
    "date_cert_granted",
    "date_cert_denied",
    "date_argued",
    "date_reargued",
    "date_rehearing_denied",
    "clusters",
    "citations",
    "citation_count",
    "opinion_text",
    "precedential_status",
    "summary",
    # Regenerated on docket activity, so on a decided live docket it postdates
    # (and thereby leaks the existence of) the decision.
    "sJsonCreationDate",
    # The /qp/ page is generated when certiorari is GRANTED and opens with the
    # grant order — the key's very presence leaks the outcome (verified live).
    # The questions presented reach cells from the petition text instead.
    "QPLink",
    # The party and counsel blocks accrue after arrival: every third-party
    # filing appends its counsel of record, and amici pile onto granted
    # petitions (mean "Other" entries: 10.37 granted vs 0.45 denied), so on a
    # decided docket the blocks' sheer size is a grant oracle — and
    # "AttorneyHeaderOther" is emitted only when the "Other" block is
    # non-empty, so its very presence is the boolean form of the same oracle
    # (verified live). "PetitionerTitle" and "RespondentTitle" are NOT here:
    # they are the arrival-time captions a forward cell sees (pipeline ingest
    # reads them for the case name).
    "Petitioner",
    "Respondent",
    "Other",
    "AttorneyHeaderPetitioner",
    "AttorneyHeaderRespondent",
    "AttorneyHeaderOther",
)


def redact_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    """Drop the top-level fields that reveal that (or how) the matter was decided.

    :data:`SNAPSHOT_OUTCOME_FIELDS` only. The proceedings entries survive this
    and are handled by :func:`truncate_snapshot`, which is the other half — a
    caller wanting the pre-decision view wants both.

    Deliberately uniform across provenances: the counsel blocks are stripped
    from genuinely pre-decision (``dated``) snapshots too, where they are
    legitimate arrival-time signal, because the blocks are undated — date
    truncation cannot apply — and a uniform replay information set beats a
    dated/truncated mixture the scoring would then have to carry. The cost is
    stated, not hidden: every replay cell is blind to counsel identity, which
    a forward cell sees, so replay figures understate the same predictor's
    forward information set. Do not "fix" this on dated snapshots — that
    reopens the seam on every decided one.
    """
    return {key: value for key, value in payload.items() if key not in SNAPSHOT_OUTCOME_FIELDS}


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


def documents_for_moment(documents: Iterable[CaseDocument], event_id: str) -> list[CaseDocument]:
    """The documents a cell for ``event_id`` may be handed at all, before any date cut.

    The argument transcript belongs to the post-argument moment alone. The date
    rule already keeps it from a grant or briefed cell, which are cut before the
    argument; this keeps it from the cells no date rule reaches — an uncut cell
    (:func:`moment_cutoff` returning ``None``) reads every stored document — so
    a document kind added for one moment changes no other moment's information
    set.
    """
    spec = moments.spec_for(event_id)
    argued = spec is not None and spec.stage == Stage.merits and spec.moment == Moment.argued
    return [
        document for document in documents if argued or document.kind != KIND_ARGUMENT_TRANSCRIPT
    ]


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

    ``cutoff is None`` is the no-cut case and passes everything through as read,
    except the documents that belong to another moment (:func:`documents_for_moment`),
    which no cell outside that moment receives under either branch.
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

    Raises :class:`TriggerAbsent` where the moment has a trigger reader
    (:data:`TRIGGER_READERS`) and the placed payload does not carry that entry,
    whichever branch built it.
    """
    provenance: Literal["as-stored", "dated", "truncated"] = "as-stored"
    admitted = documents_for_moment(documents, event)
    withheld = len(documents) - len(admitted)
    documents = admitted
    if cutoff is None:
        return Placement(snapshot_date, payload, documents, provenance, None, 0, withheld)
    # Nothing is removed from a `dated` payload by the DATE rule: it is what the
    # docket served. The anchor bound below can still remove from it.
    dropped_entries = 0
    reconstruct = read.dated is None or not shows_the_moment(read.dated[1], cutoff, event)
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
    reader = trigger_reader(event)
    if reader is not None and not carries_trigger(payload, cutoff, reader):
        # Reached only on the reconstructed branch: a `dated` payload was taken
        # because it carries the trigger. So even the latest payload, cut to the
        # moment, does not — the corpus has not yet stored a pull that shows the
        # entry the event was dated from. There is no snapshot to fall back to
        # that would be honest about the moment, so the cell is refused.
        raise TriggerAbsent(
            f"refusing to provision {case} {event}: no stored snapshot carries the "
            "docket entry that opened the moment, so the cell would be placed before "
            "its own trigger"
        )
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
        withheld + len(documents) - len(kept),
    )


#: The relation the Court's docket JSON writes on a linked docket in its
#: ``RelatedCaseNumber`` list: a cross-petition, a companion case, or the
#: petition this one is held for, linked on both sides.
VIDE_RELATION: Final = "Vide"

#: At most this many linked dockets are staged, in the order the Court lists
#: them. Each costs a snapshot read, and a docket linked to more than a handful
#: is a group whose lead the cell's own snapshot already names.
MAX_RELATED_DOCKETS: Final = 4

# A SCOTUS docket number as `normalize_docket_number` leaves it: a two-digit
# Term, the form letter (`-` for a petition, `A` for an application, `O` for an
# original action) and the sequence. The number becomes a file name under
# `record/related/`, so anything else upstream serves is refused, as a document
# kind is (`_checked_kind`).
_RELATED_NUMBER_RE = re.compile(r"^\d{2}[-AO]\d{1,5}$")


def vide_docket_numbers(payload: Mapping[str, Any]) -> tuple[str, ...]:
    """The docket numbers ``payload`` links as ``Vide``, normalized, in served order.

    Read off ``RelatedCaseNumber``, the list the Court's JSON carries on both
    sides of the link (``{"DisplayCaseNumber": "25-1323", "RelatedType":
    "Vide"}``). Any other relation type is skipped, as are the docket's own
    number, a repeat and a number not shaped as a SCOTUS docket number, and the
    list stops at :data:`MAX_RELATED_DOCKETS`. A caller passes the payload the
    cell is placed on, so a link the Court added after the cell's moment is not
    read off a ``dated`` snapshot; a ``truncated`` one keeps the latest list,
    since the field is undated.
    """
    linked = payload.get("RelatedCaseNumber")
    if not isinstance(linked, list):
        return ()
    own = normalize_docket_number(str(payload.get("CaseNumber") or ""))
    numbers: list[str] = []
    for item in linked:
        if not isinstance(item, Mapping):
            continue
        if str(item.get("RelatedType") or "").strip().lower() != VIDE_RELATION.lower():
            continue
        number = normalize_docket_number(str(item.get("DisplayCaseNumber") or ""))
        if number is None or not _RELATED_NUMBER_RE.match(number):
            continue
        if number == own or number in numbers:
            continue
        numbers.append(number)
    return tuple(numbers[:MAX_RELATED_DOCKETS])


def read_related(
    numbers: Sequence[str],
    *,
    own_case: str,
    resolve: Callable[[Sequence[str]], Mapping[str, str] | None],
    snapshot: Callable[[str], tuple[date, dict[str, Any]] | None],
) -> tuple[RelatedRead, ...]:
    """Each linked docket's row and latest stored snapshot.

    ``resolve`` maps the numbers to live case ids in one read, or answers
    ``None`` where it has no index to read
    (:func:`corpus.live_scotus_case_ids_by_docket_numbers`); ``snapshot`` reads
    one case's latest stored snapshot from whichever store serves the cell. A
    number resolving to the cell's own case is dropped, which covers a payload
    that serves no ``CaseNumber``.
    """
    if not numbers:
        return ()
    found = resolve(numbers)
    if found is None:
        return tuple(
            RelatedRead(number, None, None, unread="no corpus index to resolve it through")
            for number in numbers
        )
    reads: list[RelatedRead] = []
    for number in numbers:
        linked = found.get(number)
        if linked == own_case:
            continue
        reads.append(RelatedRead(number, linked, snapshot(linked) if linked else None))
    return tuple(reads)


@dataclass(frozen=True)
class RelatedPlacement:
    """One linked docket as a cell receives it, or the reason it receives none.

    ``payload`` is ``None`` exactly when ``reason`` is set. Every staged one is
    reconstructed by the date rule, so ``snapshot_date`` is the bound it was cut
    to, or its own pull date where that is earlier.
    """

    docket_number: str
    case_id: str | None
    snapshot_date: date | None
    payload: dict[str, Any] | None
    reason: str | None


def place_related(
    related: RelatedRead, cutoff: date | None, *, event: str, mode: str, vintage: date
) -> RelatedPlacement:
    """Cut one linked docket to what the cell's own docket could show.

    Bounded strictly before the cell's ``cutoff`` where it has one, so a
    companion is read as it stood when the cell's moment opened. On the
    interim arrival moment, whose own docket is cut at the opening entry
    because an application can be submitted and decided inside one day, the
    companion is bounded strictly before the opening day instead: it carries no
    anchor to cut at. Without a cutoff, a forward cell's companion is bounded
    strictly before ``vintage``, the date of the cell's own snapshot: the
    companion's stored pull can be newer, and an order disposing of both
    dockets entered in between would reach the cell through the companion
    after the cell's own terminal gate read a docket without it. A replay cell
    with no cutoff gets none: nothing bounds it by its event date.

    The cut is the date rule (:func:`truncate_snapshot` and
    :func:`cut_dated_fields`), which fails closed on an undated entry, and then
    the back-test's outcome redaction (:func:`redact_snapshot`),
    because a companion is always rebuilt from a later payload and its undated
    top-level fields outlive the cut: ``QPLink`` exists only once certiorari is
    granted, and the party and counsel blocks grow with a grant's amici. The
    redaction takes the contact-bearing blocks with it, so a staged companion
    carries no counsel contact details to scrub.
    """

    def withheld(reason: str) -> RelatedPlacement:
        return RelatedPlacement(related.docket_number, related.case_id, None, None, reason)

    if related.unread is not None:
        return withheld(related.unread)
    if related.case_id is None:
        return withheld("not in the corpus")
    if related.latest is None:
        return withheld("no stored snapshot")
    if cutoff is None and mode == "replay":
        return withheld("a replay cell with no cutoff")
    if cutoff is None:
        bound = vintage
    elif is_interim_arrival(event):
        bound = cutoff - timedelta(days=1)
    else:
        bound = cutoff
    stored_on, payload = related.latest
    cut, _ = truncate_snapshot(payload, bound)
    return RelatedPlacement(
        related.docket_number,
        related.case_id,
        min(stored_on, bound),
        redact_snapshot(cut_dated_fields(cut, bound)),
        None,
    )


def related_manifest(placed: Sequence[RelatedPlacement]) -> list[dict[str, Any]]:
    """The ``related.json`` rows: every link, staged or not, and why not."""
    return [
        {
            "docket_number": item.docket_number,
            "relation": VIDE_RELATION,
            "case_id": item.case_id,
            "staged": item.payload is not None,
            "file": f"{item.docket_number}.json" if item.payload is not None else None,
            "snapshot_date": item.snapshot_date.isoformat() if item.snapshot_date else None,
            "reason": item.reason,
        }
        for item in placed
    ]


def staged_scrub(text: str, values: tuple[str, ...], sides: tuple[str, ...]) -> ScrubbedText | None:
    """One staged document's contact scrub on a docket read as self-represented on ``sides``.

    None where the docket is not scrubbed. A docket read so on a party side runs
    both passes. One read so on its `Other` list alone runs the value pass only:
    no amicus's own brief is staged — the one amicus filing selected is the
    Solicitor General's invited brief, which counsel for the United States
    files — so what is staged there is counsel's filings (the staged filers
    there are represented), and the shape pass would cost their text its
    misreads of legal prose. The premise is about amici: a self-represented
    non-amicus `Other` filer whose own opposition is staged gets the value pass
    alone as well. Where no amicus
    value clears its floor nothing runs, and the document is staged as filed and
    recorded as unscrubbed (None).
    """
    if not sides:
        return None
    done = scrub_contact_details(text, values, shape=any(side != OTHER_LIST for side in sides))
    return done if done.passes else None


@dataclass(frozen=True)
class RecordWrite:
    """What :func:`write_cell_record` put on disk, for the caller to report.

    ``unrepresented`` is the docket-level reading both contact scrubs keyed on;
    ``snapshot_scrub`` the staged snapshot's scrub where that reading fired, and
    ``staged`` each provisioned document beside its scrub result (None where
    the scrub did not run over it). Counts are what a caller may echo from
    these — never a withheld value.
    """

    snapshot: Path
    unrepresented: tuple[str, ...]
    snapshot_scrub: ScrubbedSnapshot | None
    staged: tuple[tuple[CaseDocument, ScrubbedText | None], ...]
    related: tuple[RelatedPlacement, ...] = ()


def write_cell_record(
    paths: CasePaths,
    case_id: str,
    placement: Placement,
    *,
    mode: str,
    cutoff: date | None,
    snapshot_dest: Path | None = None,
    related: Sequence[RelatedPlacement] = (),
) -> RecordWrite:
    """Materialize one cell's whole ``record/`` from its placement.

    Three things, written together because they describe one information set: the
    dated snapshot, the ``context.json`` the prompt contract reads its mode and
    conditioning from, and ``documents/`` with the manifest naming what is there
    — both staged copies through the contact-detail scrubs — and, where
    ``related`` holds any, ``related/`` with each linked docket
    :func:`place_related` placed and its ``related.json``. A caller that wrote
    only the first would hand an agent a snapshot with no frozen mode, band or
    cutoff beside it — the cell would then have to guess its own posture, which
    is the one thing provisioning exists to settle.

    Every document kind is screened **before the first write**, so a refusal
    cannot leave a half-provisioned record that ``assert-cell-record`` reads as
    complete.

    Every record subtree this write owns is then **cleared**, so what is on disk
    is exactly what this placement put there. Ephemeral runners never reach the
    state the clearing guards; a tree that provisions twice — the local cascade,
    moving from one event's moment to the next — does, and a document the tighter
    cut dropped would otherwise still be sitting in ``documents/`` for the next
    cell to read. The opinion slot goes with them, and it is the one that matters
    most: a majority opinion postdates every predict moment by construction, so a
    body ``provision-opinion`` staged earlier in the same tree would reach a
    predict cell whose ``context.json`` says it was placed at its moment.
    Clearing here is safe because the evaluate lane stages the opinion *after*
    this write, never before.

    ``snapshot_dest`` sends the payload somewhere else entirely, which is a
    caller asking for a copy rather than for a cell's record; the clearing is
    skipped there, since emptying the record to write outside it would destroy a
    provisioned cell on behalf of a command that provisioned none.
    """
    kinds = screen_document_kinds(placement.documents)
    if snapshot_dest is None:
        _clear_dir(paths.snapshots_dir)
        _clear_dir(paths.documents_dir)
        _clear_dir(paths.related_dir)
        clear_opinion_slot(paths)
    payload = placement.payload
    dest = snapshot_dest or paths.snapshot(placement.snapshot_date.isoformat())
    # The staged snapshot is the payload with a self-represented filer's own
    # contact keys withheld, on either party side or the `Other` list of amici
    # (`scrub_snapshot_contacts`): the copy a cell can quote from, on the same
    # docket-level reading the document scrub below keys on. A separate object,
    # so everything else here — the cell context, the scrub trigger, the
    # document scrub — reads the payload as served.
    unrepresented = unrepresented_sides(payload)
    snapshot_scrub = scrub_snapshot_contacts(payload) if unrepresented else None
    write_raw_json(dest, payload if snapshot_scrub is None else snapshot_scrub.payload)
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
            payload,
            mode,
            provenance=placement.provenance,
            cutoff=cutoff,
            boundary=placement.boundary,
        ).model_dump(mode="json"),
    )
    staged: list[tuple[CaseDocument, ScrubbedText | None]] = []
    if placement.documents:
        # The contact-detail scrub, keyed on the docket-level reading that
        # separates a filing signed by counsel from one signed in person:
        # whether the snapshot names anyone but the filer to write to, on
        # either party side or on an amicus block — or, on the Court's own
        # docket, withholds the petitioner's block outright.
        # Where it does not, every document staged for this cell has its
        # contact details withheld (shapes and served values; served values
        # alone where only an amicus reads so, see `staged_scrub`) — the whole
        # docket rather than the petition alone, since deciding per document
        # who signed it would be a second reading with its own failure mode,
        # and a filing by the other side's counsel loses only professional
        # details the cell has no use for. The corpus row and the source PDF are
        # untouched: the scrub is on the copy staged under `record/`, which is
        # the copy a cell can quote into the public ledger.
        # The filer's own contact values, off every served block on the sides
        # the trigger read as self-represented (on the `Other` list, off the
        # qualifying blocks alone), key the scrub's value pass: it finds them
        # however a scan fragmented them, which no shape pattern can promise.
        # Read off `payload` — the payload as served — and never off the staged
        # snapshot copy, whose contact keys hold the placeholder: keyed on that,
        # the pass would look for the placeholder and miss the values.
        contact_values = party_contact_values(payload, unrepresented)
        staged = [
            (doc, staged_scrub(doc.text, contact_values, unrepresented))
            for doc in placement.documents
        ]
        for kind, (doc, scrubbed) in zip(kinds, staged, strict=True):
            write_text(paths.document(kind), doc.text if scrubbed is None else scrubbed.text)
        write_raw_json(paths.documents_manifest, document_manifest(staged))
    if related and snapshot_dest is None:
        # Each linked docket as `place_related` cut and redacted it: the
        # redaction already removed the party and counsel blocks a contact
        # scrub would read.
        for item in related:
            if item.payload is not None:
                write_raw_json(paths.related_snapshot(item.docket_number), item.payload)
        write_raw_json(paths.related_manifest, related_manifest(related))
    return RecordWrite(
        snapshot=dest,
        unrepresented=unrepresented,
        snapshot_scrub=snapshot_scrub,
        staged=tuple(staged),
        related=tuple(related) if snapshot_dest is None else (),
    )


def document_manifest(
    staged: Sequence[tuple[CaseDocument, ScrubbedText | None]],
) -> list[dict[str, Any]]:
    """The ``documents.json`` rows describing a cell's provisioned documents."""
    return [
        {
            # Every stored field but the text itself, so the row's own
            # `ocr_derived` marker reaches the cell: text a recovery pass read
            # off a page image is a lossy derivation of the filing, and a
            # manifest that dropped the marker would present it as a clean
            # extraction.
            **doc.model_dump(mode="json", exclude={"text"}),
            # What the file is, in a sentence, so a kind the cell's instructions
            # do not name still describes itself — and how it was cut, where
            # the cut leaves notes in the text. Null for a kind with none.
            "kind_description": KIND_DESCRIPTIONS.get(doc.kind),
            # A present document whose extracted text is blank/whitespace (a
            # scanned PDF with no text layer) would read as usable from
            # pages/truncated alone; flag it so the cell distinguishes "no
            # document" / "document present but no text layer" / "text
            # present". Derived here, not stored on the row. Read off the stored
            # text, so the flag keeps naming what the extraction produced — a
            # scrub replaces a contact detail with a placeholder and can never
            # empty text that had any.
            "empty_text": not doc.text.strip(),
            # Whether the scrub ran over this document's staged text **and** its
            # residual check came back clean, and how many details it withheld.
            # The two are separate facts: a scrubbed document with nothing to
            # withhold reads `true, 0`, which is a different statement from a
            # document the scrub never saw, and a cell that meets the
            # placeholder in the text can tell from here that the pipeline put
            # it there. A scrub that ran but left something contact-shaped on
            # the document's opening or closing reads `false` with a non-zero
            # `contact_residuals`; `contact_scrub_passes` still names what ran.
            # `true` is a claim about those two stretches where the shape pass
            # ran: the middle is not read, and a value-only scrub reads `true`
            # with no residual check run.
            "contact_scrubbed": scrubbed is not None and scrubbed.clean,
            "contact_replacements": 0 if scrubbed is None else scrubbed.replacements,
            "contact_residuals": 0 if scrubbed is None else scrubbed.residuals,
            # Which passes ran: `shape` wherever the scrub ran on a docket read
            # as self-represented on a party side, `value` only where the docket
            # served a contact value specific enough to key on — and `value`
            # alone on a docket read so on its `Other` list alone. A shape-only
            # scrub is the weaker of the two — it misses a detail a scan split
            # mid-word or across a line — so the manifest says which one the
            # text went through rather than letting `contact_scrubbed` read as
            # complete.
            "contact_scrub_passes": [] if scrubbed is None else list(scrubbed.passes),
        }
        for doc, scrubbed in staged
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


def screen_document_kinds(documents: Sequence[CaseDocument]) -> list[str]:
    """Each document's kind, once every one has passed :func:`_checked_kind`.

    Public so a caller that provisions several cells in turn can refuse a bad
    kind before its first cell runs, rather than at the write that would have
    placed it.
    """
    return [_checked_kind(doc.kind) for doc in documents]


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

    Files only, and that is the whole reach: :func:`write_cell_record` lays down
    flat files here, named by :func:`_checked_kind` and by a date, so a nested
    path under one of these directories is a tree this writer never made and
    should not silently delete.
    """
    if not directory.is_dir():
        return
    for entry in directory.iterdir():
        if entry.is_file():
            entry.unlink()
