"""The document back-fill split at the credential boundary, as run-repair runs it.

The back-fill (:mod:`fedcourtsai.pipeline.document_backfill`) fetches docket
JSON and the filings it nominates from supremecourt.gov and parses them, so it
runs in three jobs, like the OCR recovery and the re-cut:

- **worklist** (:func:`backfill_worklist`) — the read-only projection job walks
  the class and writes the slice the parse reads: each candidate's case id,
  the kinds it is missing, the ``(term, serial, form)`` the upstream endpoint
  serves its docket at, its Term, and the stored ``(kind, url)`` pairs the fetch
  is idempotent against, beside the class's counts. All of it is public: a
  docket number and the Court's own links to its filings.
- **plan** (:func:`plan_backfill_worklist`) — the parse job, holding no
  credential, fetches each item's docket and reads it through
  :func:`~fedcourtsai.pipeline.document_backfill.read_candidate`, the pass's own
  upstream half. On a dry run that reading is the whole of the pass, so the
  parse prints the dry run's ledger itself and writes no plan
  (:func:`dry_run_ledger`). On an apply it fetches what selection nominated and
  writes the plan: each item's docket loss, floor, or fetched documents, with
  their text, and nothing from our stores. That text is the Court's public
  filing, which for a self-represented filer includes contact details, so it
  crosses under the carve-out ``docs/data-sources.md`` (*PII stance*) records
  for the document passes' plans. It ends its slice before its plan would
  outgrow the hand-off cap, as it does at its deadline.
- **write** (:func:`apply_backfill_plan`) — the writer walks the class itself,
  checks the plan whole against the projection's own worklist, and takes each
  reading through the pass's own ledger
  (:class:`~fedcourtsai.pipeline.document_backfill.BackfillLedger`): it stamps
  a floor and writes fetched documents exactly as the pass in one job does, so
  the ledger reads as that pass's did.

Both files are untrusted on the receiving side. Every identifier in them is
pattern-checked (a SCOTUS case id, a document kind, a Court URL), and a file
that fails is refused with only the error type and list positions named
(:func:`fedcourtsai.handoff.read_handoff`).
"""

from __future__ import annotations

import logging
import sqlite3
import time
from collections.abc import Callable, Sequence
from datetime import date
from typing import Annotated, Final, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, Strict, StringConstraints

from .. import corpus, supremecourt
from ..handoff import MAX_HANDOFF_BYTES, HandoffRefused
from .document_backfill import (
    MERITS_GAP_KINDS,
    MODERN_LINK_TERM,
    BackfillLedger,
    CandidateReading,
    DocumentBackfillResult,
    DocumentGap,
    DocumentGapScan,
    document_gaps,
    estimated_candidate_seconds,
    read_candidate,
)
from .documents import (
    BIO_URL_JOIN,
    KIND_APPLICATION,
    KIND_DESCRIPTIONS,
    KIND_PETITION,
    document_fetch_losses,
    reset_document_fetch_losses,
)

logger = logging.getLogger(__name__)

#: The most items one worklist or plan may carry: an unbounded dry run's
#: worklist is the whole class, identifiers only, and the parse's deadline
#: bounds how many of them it reaches.
MAX_BACKFILL_ITEMS: Final = 20_000

#: The largest text one planned document may carry. Above any configured
#: document cap; the writer also checks each against the cap it is configured
#: with.
MAX_PLAN_TEXT_CHARS: Final = 1_000_000

#: The bytes the parse lets its plan's readings take: the hand-off cap less room
#: for the unreached and loss lines, which carry identifiers and counts only.
#: One candidate's filings can run to several documents near the cap each, so
#: the deadline alone would let a fast slice write a plan its writer refuses
#: whole.
PLAN_BYTE_BUDGET: Final = MAX_HANDOFF_BYTES - 8 * 1024 * 1024

#: The kinds a candidate can be missing: either form's opening filing, and each
#: side's opening brief on the merits.
_GAP_KINDS: Final = frozenset({KIND_PETITION, KIND_APPLICATION, *MERITS_GAP_KINDS})


def _gap_kind(kind: str) -> str:
    if kind not in _GAP_KINDS:
        raise ValueError(f"not a gap kind: {kind[:40]!r}")
    return kind


def _document_kind(kind: str) -> str:
    if kind not in KIND_DESCRIPTIONS:
        raise ValueError(f"not a document kind: {kind[:40]!r}")
    return kind


def _printable(url: str) -> str:
    if any(ord(ch) < 0x21 or ord(ch) == 0x7F for ch in url):
        raise ValueError("a URL with a control character or a space")
    return url


def _court_link_or_set(url: str) -> str:
    """A single https link on the Court's own host, or a set key joining them.

    A fetched document's URL is the link the client requested, which it refuses
    off the Court's host; a combined opposition's is the canonical join of
    every brief fetched into it.
    """
    if not all(supremecourt.is_court_url(part) for part in url.split(BIO_URL_JOIN)):
        raise ValueError("not a Court link or a set of them")
    return _printable(url)


_CaseId = Annotated[str, StringConstraints(pattern=r"^scotus/[0-9]{1,12}$")]
_GapKind = Annotated[str, AfterValidator(_gap_kind)]
_DocumentKind = Annotated[str, AfterValidator(_document_kind)]
_StoredUrl = Annotated[str, StringConstraints(min_length=1, max_length=16_384)]
_PlanUrl = Annotated[
    str, StringConstraints(min_length=1, max_length=16_384), AfterValidator(_court_link_or_set)
]
_Count = Annotated[int, Strict(), Field(ge=0)]


class BackfillWorkItem(BaseModel):
    """One candidate the parse should fetch for.

    Public: a ledger case id, the kinds the row is missing, the upstream address
    its docket number parses to, its Term, and the links the Court served for
    the documents the case already holds. No text, snapshot or other row
    content.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: _CaseId
    kinds: list[_GapKind] = Field(min_length=1, max_length=len(_GAP_KINDS))
    term: int = Field(strict=True, ge=0, le=9999)
    serial: int = Field(strict=True, ge=1, le=99_999_999)
    form: Literal["cert", "application"]
    term_year: int | None = Field(default=None, strict=True, ge=1789, le=9999)
    stored_urls: dict[_DocumentKind, _StoredUrl] = Field(
        default_factory=dict, max_length=len(KIND_DESCRIPTIONS)
    )

    def gap(self) -> DocumentGap:
        """The candidate as the pass reads it."""
        return DocumentGap(
            case_id=self.case_id,
            kinds=tuple(self.kinds),
            address=(self.term, self.serial, self.form),
            term_year=self.term_year,
            stored_urls=tuple(sorted(self.stored_urls.items())),
        )


class BackfillWorklist(BaseModel):
    """The slice of the back-fill class the parse reads, in class order, with the class's counts.

    ``bound`` is the dispatch's slice size, or null on an unbounded dry run,
    whose worklist is then the whole class. The counts are what the dry run's
    ledger reports beside the parse's readings, since the parse opens no
    corpus to count them.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/document-backfill-worklist"] = "fedcourts/document-backfill-worklist"
    version: Literal[1] = 1
    bound: int | None = Field(default=None, ge=1, le=MAX_BACKFILL_ITEMS)
    cases_seen: _Count
    cases_with_documents: _Count
    unaddressable: _Count
    candidates: _Count
    standing_floors: _Count
    merits_candidates: _Count
    items: list[BackfillWorkItem] = Field(max_length=MAX_BACKFILL_ITEMS)


class PlanDocument(BaseModel):
    """One document the parse fetched, as the fetch made it.

    The text is the Court's own public filing as served at ``url``, or a section
    derived from it. It can carry a self-represented filer's contact details,
    which is why it crosses under the carve-out and is never printed. Empty
    where the extractor read nothing, as the fetching lanes store it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: _CaseId
    kind: _DocumentKind
    url: _PlanUrl
    entry_date: str | None = Field(default=None, max_length=64)
    fetched_at: date
    pages: int = Field(default=0, strict=True, ge=0, le=100_000)
    truncated: bool = False
    ocr_derived: bool = False
    text: str = Field(max_length=MAX_PLAN_TEXT_CHARS)

    def stored(self) -> corpus.CaseDocument:
        return corpus.CaseDocument.model_validate(self.model_dump())


class BackfillReading(BaseModel):
    """What the parse read for one item: a docket loss, a floor, or what it fetched.

    ``documents`` empty, with no loss and no floor, is a candidate whose every
    selected filing was lost fetch-side, which ``fetch_losses`` on the plan
    attributes.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: _CaseId
    loss: Literal["docket-unserved", "docket-error"] | None = None
    floor: Literal["no-link", "no-entry"] | None = None
    alarmed: bool = False
    documents: list[PlanDocument] = Field(default_factory=list, max_length=64)

    def reading(self) -> CandidateReading:
        return CandidateReading(
            loss=self.loss,
            floor=self.floor,
            alarmed=self.alarmed,
            documents=tuple(document.stored() for document in self.documents),
        )


class BackfillPlan(BaseModel):
    """What the credential-free parse read on an apply: the file the writer lands."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/document-backfill-plan"] = "fedcourts/document-backfill-plan"
    version: Literal[1] = 1
    readings: list[BackfillReading] = Field(max_length=MAX_BACKFILL_ITEMS)
    unreached: list[_CaseId] = Field(
        default_factory=list,
        max_length=MAX_BACKFILL_ITEMS,
        description="Worklist items the slice declined to start, in class order",
    )
    fetch_losses: dict[Annotated[str, StringConstraints(max_length=40)], _Count] = Field(
        description="The document-fetch losses the parse recorded, by reason, zero-filled",
        max_length=16,
    )


def _scan_and_candidates(
    conn: corpus.ReadConnection,
) -> tuple[DocumentGapScan, list[DocumentGap], int]:
    scan = document_gaps(conn)
    unaddressable = [gap for gap in scan.gaps if gap.address is None]
    for gap in unaddressable:
        logger.warning(
            "document-backfill: %s holds no %s and no addressable docket number",
            gap.case_id,
            ", ".join(gap.kinds),
        )
    return scan, [gap for gap in scan.gaps if gap.address is not None], len(unaddressable)


def backfill_worklist(
    conn: corpus.ReadConnection, *, bound: int | None
) -> tuple[BackfillWorklist, DocumentBackfillResult]:
    """The worklist for one dispatch, and the class ledger the projection prints.

    The slice is the class's first ``bound`` candidates, in class order, as the
    pass in one job takes it; ``bound=None`` (an unbounded dry run) is the whole
    class. The ledger is the walk-only reading: nothing reached, the whole class
    remaining.
    """
    scan, candidates, unaddressable = _scan_and_candidates(conn)
    picked = candidates if bound is None else candidates[:bound]
    if len(picked) > MAX_BACKFILL_ITEMS:
        raise HandoffRefused(
            f"the class holds {len(picked)} candidates, above the "
            f"{MAX_BACKFILL_ITEMS} one worklist may carry; bound the dry run"
        )
    items: list[BackfillWorkItem] = []
    for gap in picked:
        assert gap.address is not None  # unaddressable gaps never enter a slice
        term, serial, form = gap.address
        items.append(
            BackfillWorkItem(
                case_id=gap.case_id,
                kinds=list(gap.kinds),
                term=term,
                serial=serial,
                form=form,
                term_year=gap.term_year,
                stored_urls=dict(gap.stored_urls),
            )
        )
    merits = sum(1 for gap in candidates if gap.merits)
    worklist = BackfillWorklist(
        bound=bound,
        cases_seen=scan.cases_seen,
        cases_with_documents=scan.cases_with_documents,
        unaddressable=unaddressable,
        candidates=len(candidates),
        standing_floors=scan.standing_floors,
        merits_candidates=merits,
        items=items,
    )
    reset_document_fetch_losses()
    reading = BackfillLedger(None, apply=False, today=date.min).result(
        scan,
        unaddressable=unaddressable,
        candidates=len(candidates),
        merits_candidates=merits,
        bound=0,
        sliced=0,
        unreached=[],
        fetch_losses=document_fetch_losses().by_reason,
    )
    return worklist, reading


def _check_unique(keys: Sequence[str], what: str) -> None:
    seen: set[str] = set()
    for key in keys:
        if key in seen:
            raise HandoffRefused(f"the {what} names {key} twice")
        seen.add(key)


def check_backfill_worklist(worklist: BackfillWorklist) -> None:
    """Refuse a worklist the projection could not have written."""
    if worklist.bound is not None and len(worklist.items) > worklist.bound:
        raise HandoffRefused(
            f"the worklist carries {len(worklist.items)} items, above its bound of {worklist.bound}"
        )
    if len(worklist.items) > worklist.candidates:
        raise HandoffRefused("the worklist carries more items than its class holds candidates")
    _check_unique([item.case_id for item in worklist.items], "worklist")
    for item in worklist.items:
        _check_unique(item.kinds, f"worklist item {item.case_id}")


def _class_scan(worklist: BackfillWorklist) -> DocumentGapScan:
    return DocumentGapScan(
        gaps=(),
        cases_seen=worklist.cases_seen,
        cases_with_documents=worklist.cases_with_documents,
        standing_floors=worklist.standing_floors,
    )


def dry_run_ledger(
    client: supremecourt.SupremeCourtClient,
    worklist: BackfillWorklist,
    *,
    char_cap: int,
    today: date,
    deadline: float | None = None,
    monotonic: Callable[[], float] = time.monotonic,
) -> DocumentBackfillResult:
    """The dry run, read whole in the parse: each item's docket fetched and selected.

    The pass's dry run writes nothing and reads nothing of the corpus past the
    class it walked, which the worklist carries, so the parse makes the whole
    reading itself, under the pass's own slice deadline.
    """
    check_backfill_worklist(worklist)
    reset_document_fetch_losses()
    ledger = BackfillLedger(None, apply=False, today=today)
    unreached: list[str] = []
    for index, item in enumerate(worklist.items):
        if _declined(deadline, monotonic, apply=False):
            unreached = [i.case_id for i in worklist.items[index:]]
            break
        gap = item.gap()
        ledger.take(gap, read_candidate(client, gap, apply=False, char_cap=char_cap, today=today))
    return ledger.result(
        _class_scan(worklist),
        unaddressable=worklist.unaddressable,
        candidates=worklist.candidates,
        merits_candidates=worklist.merits_candidates,
        bound=worklist.bound,
        sliced=len(worklist.items),
        unreached=unreached,
        fetch_losses=document_fetch_losses().by_reason,
    )


def _declined(deadline: float | None, monotonic: Callable[[], float], *, apply: bool) -> bool:
    if deadline is None:
        return False
    estimate = estimated_candidate_seconds(apply=apply)
    left = deadline - monotonic()
    if estimate > left:
        logger.warning(
            "document-backfill: slice deadline reached with %.0fs left (~%.0fs a candidate)",
            left,
            estimate,
        )
        return True
    return False


def plan_backfill_worklist(
    client: supremecourt.SupremeCourtClient,
    worklist: BackfillWorklist,
    *,
    char_cap: int,
    today: date,
    deadline: float | None = None,
    monotonic: Callable[[], float] = time.monotonic,
    byte_budget: int = PLAN_BYTE_BUDGET,
) -> BackfillPlan:
    """Fetch each worklist item's docket and the filings it nominates, with no corpus: the plan.

    The pass's own per-candidate work up to the write, through
    :func:`~fedcourtsai.pipeline.document_backfill.read_candidate`, under the
    pass's slice deadline: the first item the deadline will not hold ends the
    slice, it and the rest reported unreached. ``byte_budget`` ends it the same
    way at the first item whose reading would take the plan past it, that
    reading discarded with its losses, so the plan stays under the hand-off cap
    its writer enforces and the item heads the next slice.
    """
    check_backfill_worklist(worklist)
    reset_document_fetch_losses()
    readings: list[BackfillReading] = []
    unreached: list[str] = []
    spent = 0
    losses = document_fetch_losses().by_reason
    for index, item in enumerate(worklist.items):
        if _declined(deadline, monotonic, apply=True):
            unreached = [i.case_id for i in worklist.items[index:]]
            break
        read = read_candidate(client, item.gap(), apply=True, char_cap=char_cap, today=today)
        reading = BackfillReading(
            case_id=item.case_id,
            loss=read.loss,
            floor=read.floor,
            alarmed=read.alarmed,
            documents=[
                PlanDocument.model_validate(document.model_dump()) for document in read.documents
            ],
        )
        size = len(reading.model_dump_json().encode())
        if spent + size > byte_budget:
            logger.warning(
                "document-backfill: the plan's byte budget ends the slice at %s", item.case_id
            )
            unreached = [i.case_id for i in worklist.items[index:]]
            break
        spent += size
        readings.append(reading)
        losses = document_fetch_losses().by_reason
    return BackfillPlan(readings=readings, unreached=unreached, fetch_losses=losses)


def _loss_reasons() -> list[str]:
    """The fetch's own loss reasons, in the ledger's order."""
    reset_document_fetch_losses()
    return list(document_fetch_losses().by_reason)


def check_backfill_plan(plan: BackfillPlan, worklist: BackfillWorklist, *, char_cap: int) -> None:
    """Refuse a plan the parse could not have written for this worklist, whole.

    The read already refused any malformed identifier, kind, URL or count.
    Beyond that: a case named twice across readings and unreached; a plan that
    does not account for every worklist item exactly once (the ledger is built
    on it, and an item it dropped would vanish from it); a case that is not an
    item of ``worklist`` (the projection's own file, which the parse cannot
    replace); unreached items that are not the worklist's tail in its order (the
    parse ends its slice, it never skips ahead); a reading of more than one
    shape, or an alarm on no floor or on a docket older than the alarm's Term; a
    document of another case, two of one kind, or a text longer than the
    configured document cap; and loss counts under any reason but the fetch's
    own.

    What the writer cannot check is that a reading is what the Court served:
    it holds no docket and no PDF, so a document's text, and a floor's reading,
    are the parse's.
    """
    check_backfill_worklist(worklist)
    keys = [reading.case_id for reading in plan.readings] + list(plan.unreached)
    _check_unique(keys, "plan")
    items = {item.case_id: item for item in worklist.items}
    for key in keys:
        if key not in items:
            raise HandoffRefused(f"the plan reports {key}, which is not on this worklist")
    if len(keys) != len(worklist.items):
        raise HandoffRefused(
            f"the plan accounts for {len(keys)} of the worklist's {len(worklist.items)} items"
        )
    order = [item.case_id for item in worklist.items]
    if plan.unreached != order[len(order) - len(plan.unreached) :]:
        raise HandoffRefused("the plan's unreached items are not the worklist's tail, in order")
    if set(plan.fetch_losses) != set(_loss_reasons()):
        raise HandoffRefused("the plan's fetch losses are not the fetch's own reasons")
    for reading in plan.readings:
        _check_reading(reading, items[reading.case_id], char_cap=char_cap)


def _check_reading(reading: BackfillReading, item: BackfillWorkItem, *, char_cap: int) -> None:
    shapes = (reading.loss is not None) + (reading.floor is not None) + bool(reading.documents)
    if shapes > 1:
        raise HandoffRefused(f"the plan's reading of {reading.case_id} has more than one shape")
    if reading.alarmed and (
        reading.floor is None or item.term_year is None or item.term_year < MODERN_LINK_TERM
    ):
        raise HandoffRefused(f"the plan raises an alarm on {reading.case_id} no floor can carry")
    _check_unique([document.kind for document in reading.documents], f"reading {reading.case_id}")
    for document in reading.documents:
        if document.case_id != reading.case_id:
            raise HandoffRefused(
                f"the plan files a document of another case under {reading.case_id}"
            )
        if len(document.text) > char_cap:
            raise HandoffRefused(
                f"the plan's {document.kind} text for {reading.case_id} is {len(document.text)} "
                f"characters, above the {char_cap}-character document cap"
            )


def apply_backfill_plan(
    conn: sqlite3.Connection,
    plan: BackfillPlan,
    worklist: BackfillWorklist,
    *,
    char_cap: int,
    today: date,
) -> DocumentBackfillResult:
    """Land each reading of the plan as the pass in one job's apply does.

    The class is walked here, before anything is written, so ``remaining`` is
    that class less what this write took out of it — the number the workflow's
    re-read must then find. A reading whose candidate is no longer in the class
    (recovered, stamped or no longer predict-relevant since the projection) is
    counted as read and written nowhere: ``left_class``, as is one whose missing
    kinds or stored links have changed since. There is no dry run
    here: the pass's dry run is read whole in the parse (:func:`dry_run_ledger`).
    """
    check_backfill_plan(plan, worklist, char_cap=char_cap)
    scan, candidates, unaddressable = _scan_and_candidates(conn)
    in_class = {gap.case_id: gap for gap in candidates}
    readings = {reading.case_id: reading for reading in plan.readings}
    ledger = BackfillLedger(conn, apply=True, today=today)
    for item in worklist.items:
        planned = readings.get(item.case_id)
        if planned is None:
            continue
        # A candidate still in the class but no longer as the parse read it (a
        # kind since stored, or a link since changed) is left alone as well: the
        # plan's documents answer the gap the projection saw, not this one.
        current = in_class.get(item.case_id)
        ledger.take(current or item.gap(), planned.reading(), in_class=current == item.gap())
    return ledger.result(
        scan,
        unaddressable=unaddressable,
        candidates=len(candidates),
        merits_candidates=sum(1 for gap in candidates if gap.merits),
        bound=worklist.bound,
        sliced=len(worklist.items),
        unreached=list(plan.unreached),
        fetch_losses={reason: plan.fetch_losses[reason] for reason in _loss_reasons()},
    )
