"""What a provisioned cell reads: the backend it comes from, and where it is cut.

The predict/evaluate cells materialize a read-only ``record/`` — the point-in-time
snapshot, the case's documents, and the predictable event — from the corpus. Two
questions this module answers for the provisioning commands, both leaf-pure so
``cli`` stays a thin caller:

*Which store serves the read.* :class:`CasestoreSource` returns the **same
shapes** as the corpus read functions (``latest_snapshot`` / ``snapshot_at`` /
``documents_for_case`` / ``events_for_case``) out of the per-case content store
(:mod:`fedcourtsai.casestore`) rather than the SQLite corpus, behind
``--corpus-backend casestore``, so a cell's ``record/`` is **byte-identical**
whichever backend produced it — proven by ``tests/test_provision_casestore.py``.

*Where the read is cut.* :func:`moment_cutoff` and :func:`documents_before` place
a forward cell at the declared moment it forecasts instead of at the latest
snapshot, so a later moment is conditioned on the information set it declares.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from . import casestore
from .corpus import CaseDocument, CorpusEvent, CorpusRow
from .pipeline import cert_signals, moments


class ProvisionError(RuntimeError):
    """A provisioning-source configuration problem, surfaced with context."""


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
    """Build a :class:`CasestoreSource` from ``FEDCOURTS_CASESTORE_URL``.

    Raises :class:`ProvisionError` when the store is not configured — the casestore
    backend cannot serve reads without it.
    """
    transport = casestore.transport_from_settings()
    if transport is None:
        raise ProvisionError(
            "the casestore backend needs FEDCOURTS_CASESTORE_URL (s3://<bucket>[/<prefix>])"
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

    One residual the date cannot reach: documents are keyed ``(case_id, kind)``
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
