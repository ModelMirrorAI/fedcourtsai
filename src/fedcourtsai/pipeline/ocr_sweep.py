"""The standing OCR sweep: the recovery pass on the walker's schedule.

The dispatched recovery (:mod:`fedcourtsai.pipeline.ocr_recovery`) repairs a
scanned filing whenever a maintainer spends a slice on it. A forward cell runs
once, usually within days of the filing it reads, so a scan stored between two
dispatches reaches its cell with no text. This sweep runs the same recovery
every walker window, capped, so a newly stored scan gets its text before the
cell that reads it.

It is split at the credential boundary, like the order-list vote sweep, because
it fetches and parses third-party PDFs:

- **worklist** (:func:`sweep_worklist`) — the read-only projection job walks the
  recovery class, puts it in sweep order and writes the window's slice: each
  candidate's case id, kind, stored Court URL and page count. All four are
  public facts about public filings: the Court serves each at that URL.
- **plan** (:func:`plan_worklist`) — the parse job, holding no credential, re-fetches
  each worklist item from supremecourt.gov and reads its pages through the same
  extractor and OCR seam the dispatched pass uses. The plan carries the text it
  read, and nothing from our stores. That text is the Court's public filing,
  which for a self-represented filer includes contact details, so it crosses
  under the carve-out ``docs/data-sources.md`` (*PII stance*) proposes for it.
- **apply** (:func:`apply_ocr_plan`) — the writer re-checks every plan row against
  the corpus it is about to write: the row must be an item of this window's
  worklist (read from the projection's own artifact, not the parse's), still in
  the recovery class at the same URL, and the plan no larger than the cap. Then
  it writes exactly what the dispatched pass would: the text, the
  ``ocr_derived`` marker, and a petition's re-derived questions-presented row.

The dispatched pass (run-repair's ``ocr-recovery``) runs on the same split
and the same two files, in class order rather than sweep order: its
projection takes the first ``--max-cases`` candidates of the class as the
apply's worklist (:func:`dispatched_worklist`), or a spread sample of it as
the dry run's probe list, and its writer checks the plan against that worklist
on the dispatched pass's own terms (``dispatched=True`` on :func:`check_plan`
and :func:`apply_ocr_plan`).

Both files are untrusted on the receiving side. Every identifier in them is
pattern-checked (a SCOTUS case id, a recoverable kind, a Court URL, a reason
from a closed set), and a file that fails is refused with only the error type
and list positions named (:func:`fedcourtsai.handoff.read_handoff`), never a
key, field name or value from the file. So nothing a forged file carries
reaches a step summary except a validated identifier or a count, and nothing
malformed survives the read to fail an apply halfway through.

**Sweep order** (:func:`order_sweep_class`, pure). A candidate a forward cell
will read is *forward*: its case carries an open event, its row is in predict
scope, and salience has not deferred it (an open merits event bypasses
salience, as at the predict seams). Forward candidates stored within
:data:`FRESH_DAYS` of the window come first, newest stored first, because the
cell for a new scan is closest. The older forward candidates follow, then the
backlog, each in class order rotated by the window. A candidate the sweep cannot
recover (an unreadable scan, a refused fetch, a recognition the document budget
cuts short) stays in the class, as on the dispatched pass, so without the
rotation an unreadable head would take the cap every window and starve the
rest. Only the fresh head is unrotated, and a candidate leaves it after
:data:`FRESH_DAYS`, so an unreadable fresh scan holds a slot for that long at
most. A long-open cert petition that never reads moves into the rotated forward
tier, where it takes its turn rather than a fixed slot.
"""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Annotated, Final, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StringConstraints,
)

from .. import corpus
from ..handoff import HandoffRefused
from ..schemas import Stage
from ..supremecourt import SupremeCourtClient
from .documents import KIND_QUESTIONS_PRESENTED
from .ocr_recovery import (
    RECOVERABLE_KINDS,
    OcrPageFactory,
    ScannedDocument,
    _rederived_questions,
    estimated_seconds_for_pages,
    exclusion_reason,
    fetchable_document_url,
    ocr_page_for_pdf,
    read_scanned_document,
    require_ocr_binaries,
    scanned_documents,
    spread_sample,
)

#: The largest slice a worklist or plan may carry. Above any configured cap
#: (``historical.sweep_caps.ocr`` is bounded below it), so a file past it is
#: refused as malformed rather than read.
MAX_SWEEP_ITEMS = 200

#: The largest text one plan row may carry. Above any configured document cap;
#: the writer also checks each row against the cap it is configured with.
MAX_PLAN_TEXT_CHARS = 1_000_000

#: How long a forward candidate stays in the unrotated head of the slice, in
#: days from when it was stored. A forward cell for an application usually runs
#: within days of the filing; past this a candidate takes its turn in rotation.
FRESH_DAYS: Final = 7

#: Windows a day, for the rotation key: run-seed's four.
WINDOWS_PER_DAY: Final = 4

#: Why the parse read no text for an item: the dispatched pass's reasons, and
#: nothing else. A closed set, so a forged plan cannot put free text in one.
_REASON_PATTERN: Final = (
    r"^(unfetchable-url|transport-error|not-served|oversized|"
    r"budget-exhausted|empty-after-ocr|http-[0-9]{3})$"
)


def _recoverable_kind(kind: str) -> str:
    if kind not in RECOVERABLE_KINDS:
        raise ValueError(f"not a recoverable kind: {kind[:40]!r}")
    return kind


def _recoverable_key(key: str) -> str:
    _recoverable_kind(key.split(" ", 1)[1])
    return key


def _court_url(url: str) -> str:
    if not fetchable_document_url(url) or any(ord(ch) < 0x21 for ch in url):
        raise ValueError("not a single https link on the Court's own host")
    return url


_CaseId = Annotated[str, StringConstraints(pattern=r"^scotus/[0-9]{1,12}$")]
_Kind = Annotated[str, AfterValidator(_recoverable_kind)]
_Url = Annotated[str, StringConstraints(max_length=2048), AfterValidator(_court_url)]
_Key = Annotated[
    str,
    StringConstraints(pattern=r"^scotus/[0-9]{1,12} [a-z-]{1,40}$"),
    AfterValidator(_recoverable_key),
]
_Reason = Annotated[str, StringConstraints(pattern=_REASON_PATTERN)]


@dataclass(frozen=True)
class SweepCandidate:
    """One recovery-class row, and whether a forward cell will read it."""

    scanned: ScannedDocument
    forward: bool

    @property
    def key(self) -> str:
        """``<case_id> <kind>``, the ledger key the dispatched pass uses."""
        return self.scanned.key


def forward_case_ids(conn: corpus.ReadConnection) -> frozenset[str]:
    """SCOTUS cases a forward predict cell can still read.

    An open event on a row that is in predict scope (``predict_excluded = 0``),
    and that salience has not deferred: unscored, selected, or carrying an open
    merits event, which bypasses the gate (:func:`~fedcourtsai.corpus.is_salience_deferred`,
    :func:`~fedcourtsai.corpus.has_open_merits_event`). One query, answered in the
    join, so it reads only the open in-scope slice.
    """
    cur = conn.execute(
        "SELECT DISTINCT e.case_id FROM events e JOIN cases c ON c.case_id = e.case_id "
        "WHERE e.resolved = 0 AND e.court = 'scotus' AND c.predict_excluded = 0 "
        "AND (c.salience_version IS NULL OR c.salience_selected = 1 OR e.stage = ?)",
        (Stage.merits.value,),
    )
    return frozenset(str(record["case_id"]) for record in cur)


def order_sweep_class(
    candidates: Sequence[SweepCandidate], *, rotation: int, today: date
) -> list[SweepCandidate]:
    """The recovery class in sweep order: the fresh forward head, then two rotated tiers.

    ``candidates`` arrive in class order (``case_id``, then kind). Forward
    candidates stored on or after ``today`` less :data:`FRESH_DAYS` come first,
    newest stored first (ties keep class order). The older forward candidates
    follow, then the backlog; each of those two tiers starts at ``rotation``
    modulo its length. Pure: the same class, rotation and day give the same order.
    """
    fresh_from = today - timedelta(days=FRESH_DAYS)
    fresh = [c for c in candidates if c.forward and c.scanned.document.fetched_at >= fresh_from]
    stale = [c for c in candidates if c.forward and c.scanned.document.fetched_at < fresh_from]
    backlog = [c for c in candidates if not c.forward]
    # Newest stored first. Python's sort is stable, so equal dates keep class order.
    fresh.sort(key=lambda c: c.scanned.document.fetched_at, reverse=True)
    return fresh + _rotated(stale, rotation) + _rotated(backlog, rotation)


def _rotated(tier: list[SweepCandidate], rotation: int) -> list[SweepCandidate]:
    if not tier:
        return tier
    start = rotation % len(tier)
    return tier[start:] + tier[:start]


def window_rotation(now: datetime, cap: int) -> int:
    """The rotated tiers' starting offset for the window running at ``now``.

    One cap's width further on each of run-seed's windows (six hours apart), so
    consecutive windows tile a rotated tier rather than retrying the same head.
    """
    window = now.date().toordinal() * WINDOWS_PER_DAY + now.hour * WINDOWS_PER_DAY // 24
    return window * cap


class OcrWorkItem(BaseModel):
    """One candidate the parse should re-read.

    Public: a ledger case id, a document kind, the Court's own URL for the filing,
    and the page count of the PDF served there. ``forward`` says the case has an
    open event in predict scope, which the committed event files and predictions
    under ``data/`` already show for every case a forward cell has run on. No
    text, snapshot or other row content.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: _CaseId
    kind: _Kind
    url: _Url
    pages: StrictInt = Field(ge=1, le=100_000)
    forward: bool

    @property
    def key(self) -> str:
        return f"{self.case_id} {self.kind}"


class OcrWorklist(BaseModel):
    """The window's slice of the recovery class, in sweep order: what the parse reads.

    The class totals ride with it so the parse job's summary can state the
    whole ledger line without a corpus.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/ocr-worklist"] = "fedcourts/ocr-worklist"
    version: Literal[1] = 1
    class_size: int = Field(ge=0)
    forward_size: int = Field(ge=0)
    cap: int = Field(ge=1, le=MAX_SWEEP_ITEMS)
    items: list[OcrWorkItem] = Field(max_length=MAX_SWEEP_ITEMS)


class OcrPlanRow(BaseModel):
    """One filing the parse recovered: the text it read and how it read it.

    The text is the Court's own public filing as served at ``url``, read through
    the extractor with the OCR seam supplied. It can carry a self-represented
    filer's contact details, which is why it crosses under the proposed
    carve-out and is never printed. ``pages``, ``truncated`` and ``ocr_derived``
    are the extractor's own readings, stored on the row as the dispatched pass
    stores them.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: _CaseId
    kind: _Kind
    url: _Url
    text: str = Field(min_length=1, max_length=MAX_PLAN_TEXT_CHARS)
    pages: StrictInt = Field(ge=1, le=100_000)
    truncated: bool
    ocr_derived: bool

    @property
    def key(self) -> str:
        return f"{self.case_id} {self.kind}"


class OcrPlan(BaseModel):
    """What the credential-free parse read: the file the writer applies."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/ocr-plan"] = "fedcourts/ocr-plan"
    version: Literal[1] = 1
    rows: list[OcrPlanRow] = Field(max_length=MAX_SWEEP_ITEMS)
    failures: dict[_Key, _Reason] = Field(
        default_factory=dict,
        max_length=MAX_SWEEP_ITEMS,
        description="`<case_id> <kind>` -> why the parse read no text for it",
    )
    unreached: list[_Key] = Field(
        default_factory=list,
        max_length=MAX_SWEEP_ITEMS,
        description="Worklist items the slice deadline declined to start, in sweep order",
    )


@dataclass(frozen=True)
class SweepSelection:
    """One window's selection: the class, its forward share, and the slice."""

    class_size: int
    forward_size: int
    class_by_kind: dict[str, int]
    documents_seen: int
    slice: tuple[SweepCandidate, ...]


def select_sweep(
    candidates: Sequence[SweepCandidate], *, cap: int, rotation: int, today: date
) -> tuple[SweepCandidate, ...]:
    """The first ``cap`` candidates in sweep order (:func:`order_sweep_class`)."""
    if cap < 1:
        raise ValueError("the sweep cap must be at least 1")
    return tuple(order_sweep_class(candidates, rotation=rotation, today=today)[:cap])


def sweep_selection(conn: corpus.ReadConnection, *, cap: int, now: datetime) -> SweepSelection:
    """Walk the recovery class and take the window's slice."""
    scan = scanned_documents(conn)
    forward_ids = forward_case_ids(conn)
    candidates = [
        SweepCandidate(scanned=s, forward=s.document.case_id in forward_ids)
        for s in scan.candidates
    ]
    by_kind: dict[str, int] = {}
    for candidate in candidates:
        kind = candidate.scanned.document.kind
        by_kind[kind] = by_kind.get(kind, 0) + 1
    return SweepSelection(
        class_size=len(candidates),
        forward_size=sum(1 for c in candidates if c.forward),
        class_by_kind={k: by_kind[k] for k in RECOVERABLE_KINDS if by_kind.get(k)},
        documents_seen=scan.documents_seen,
        slice=select_sweep(
            candidates, cap=cap, rotation=window_rotation(now, cap), today=now.date()
        ),
    )


def sweep_worklist(selection: SweepSelection, *, cap: int) -> OcrWorklist:
    """The selection as the public worklist the parse job reads."""
    return OcrWorklist(
        class_size=selection.class_size,
        forward_size=selection.forward_size,
        cap=cap,
        items=[
            OcrWorkItem(
                case_id=c.scanned.document.case_id,
                kind=c.scanned.document.kind,
                url=c.scanned.document.url,
                pages=c.scanned.document.pages,
                forward=c.forward,
            )
            for c in selection.slice
        ],
    )


def dispatched_worklist(
    conn: corpus.ReadConnection,
    candidates: Sequence[ScannedDocument],
    *,
    max_cases: int | None,
    probe: int,
) -> OcrWorklist:
    """The dispatched pass's worklist over one walk of the class.

    An apply's is its slice: the first ``max_cases`` candidates in class order,
    the order the dispatched pass has always taken them in, so a recovered row
    leaving the class still advances the next dispatch. A dry run's is the
    spread sample its probe re-fetches (``probe`` of them,
    :func:`~fedcourtsai.pipeline.ocr_recovery.spread_sample`), since the dry
    run reads statuses and OCRs nothing. ``cap`` is the bound itself on an
    apply, so the writer can hold the plan to the number the dispatch carried.
    """
    if max_cases is not None:
        picked = list(candidates[:max_cases])
        cap = max_cases
    else:
        picked = spread_sample(candidates, probe)
        cap = max(probe, 1)
    forward_ids = forward_case_ids(conn)
    return OcrWorklist(
        class_size=len(candidates),
        forward_size=sum(1 for c in candidates if c.document.case_id in forward_ids),
        cap=cap,
        items=[
            OcrWorkItem(
                case_id=c.document.case_id,
                kind=c.document.kind,
                url=c.document.url,
                pages=c.document.pages,
                forward=c.document.case_id in forward_ids,
            )
            for c in picked
        ],
    )


def _check_unique(keys: Sequence[str], what: str) -> None:
    seen: set[str] = set()
    for key in keys:
        if key in seen:
            raise HandoffRefused(f"the {what} names {key} twice")
        seen.add(key)


def check_worklist(worklist: OcrWorklist) -> None:
    """Refuse a worklist the projection could not have written."""
    if len(worklist.items) > worklist.cap:
        raise HandoffRefused(
            f"the worklist carries {len(worklist.items)} items, above its cap of {worklist.cap}"
        )
    _check_unique([item.key for item in worklist.items], "worklist")


def plan_worklist(
    client: SupremeCourtClient,
    worklist: OcrWorklist,
    *,
    char_cap: int,
    ocr_page_factory: OcrPageFactory = ocr_page_for_pdf,
    deadline: float | None = None,
    monotonic: Callable[[], float] = time.monotonic,
) -> OcrPlan:
    """Re-fetch and read each worklist item, with no corpus: the plan.

    The same per-candidate work the dispatched pass's apply does, through
    :func:`~fedcourtsai.pipeline.ocr_recovery.read_scanned_document`, and the
    same slice deadline: before each item its cost is estimated from the page
    count, and the first that will not fit ends the slice, it and the rest
    reported unreached.
    """
    check_worklist(worklist)
    if worklist.items and ocr_page_factory is ocr_page_for_pdf:
        require_ocr_binaries()
    rows: list[OcrPlanRow] = []
    failures: dict[str, str] = {}
    unreached: list[str] = []
    for index, item in enumerate(worklist.items):
        if deadline is not None:
            estimate = estimated_seconds_for_pages(item.pages)
            if estimate > deadline - monotonic():
                unreached = [i.key for i in worklist.items[index:]]
                break
        extracted, reason = read_scanned_document(
            client, item, char_cap=char_cap, ocr_page_factory=ocr_page_factory
        )
        if extracted is None:
            failures[item.key] = reason or "not-served"
            continue
        rows.append(
            OcrPlanRow(
                case_id=item.case_id,
                kind=item.kind,
                url=item.url,
                text=extracted.text,
                pages=extracted.pages,
                truncated=extracted.truncated,
                ocr_derived=extracted.ocr_derived,
            )
        )
    return OcrPlan(rows=rows, failures=dict(sorted(failures.items())), unreached=unreached)


class OcrSweepApplyResult(BaseModel):
    """What the writer did with one plan."""

    model_config = ConfigDict(extra="forbid")

    applied: bool
    planned: int = Field(ge=0, description="Rows the plan carried")
    written: dict[str, str] = Field(
        default_factory=dict,
        description="`<case_id> <kind>` -> what was stored: pages, characters, flags",
    )
    skipped: dict[str, str] = Field(
        default_factory=dict,
        description="`<case_id> <kind>` -> why a plan row was not written: the stored "
        "row left the class, or its URL moved, since the projection read it",
    )
    questions_rederived: int = Field(ge=0, default=0)


def check_plan(
    plan: OcrPlan, worklist: OcrWorklist, *, cap: int, char_cap: int, dispatched: bool = False
) -> None:
    """Refuse a plan the parse could not have written for this window, whole.

    The read already refused any malformed identifier, URL or reason. Beyond
    that: more rows than the window's cap; a key named twice; a row, failure or
    unreached key that is not an item of ``worklist`` (the projection's own
    file, which the parse cannot replace), or a row at a URL other than its
    item's; a row not marked ``ocr_derived`` (every class member is a scan whose
    stored extraction read empty, so a reading of it that OCR did not contribute
    to is not one this sweep produces); a text longer than the configured
    document cap; or a text that is whitespace only.

    ``dispatched`` holds the plan to the dispatched pass's terms instead. It
    must account for every worklist item exactly once — read, not recovered or
    unreached — because the writer's ledger is built from the plan's own count
    and an item the plan dropped would vanish from it. And a row need not be
    marked ``ocr_derived``: the dispatched pass stores whatever the re-served
    filing reads as, a text layer included, with the extractor's own flag.
    """
    check_worklist(worklist)
    if len(plan.rows) > cap:
        raise HandoffRefused(f"the plan carries {len(plan.rows)} rows, above the cap of {cap}")
    _check_unique([row.key for row in plan.rows], "plan")
    urls = {item.key: item.url for item in worklist.items}
    for key in [*plan.failures, *plan.unreached]:
        if key not in urls:
            raise HandoffRefused(f"the plan reports {key}, which is not on this window's worklist")
    if dispatched:
        _check_unique([row.key for row in plan.rows] + [*plan.failures, *plan.unreached], "plan")
        accounted = len(plan.rows) + len(plan.failures) + len(plan.unreached)
        if accounted != len(worklist.items):
            raise HandoffRefused(
                f"the plan accounts for {accounted} of the worklist's {len(worklist.items)} items"
            )
    for row in plan.rows:
        if urls.get(row.key) != row.url:
            raise HandoffRefused(
                f"the plan's row {row.key} is not an item of this window's worklist at its URL"
            )
        if not row.ocr_derived and not dispatched:
            raise HandoffRefused(f"the plan's row {row.key} is not marked ocr_derived")
        if len(row.text) > char_cap:
            raise HandoffRefused(
                f"the plan's text for {row.key} is {len(row.text)} characters, "
                f"above the {char_cap}-character document cap"
            )
        if not row.text.strip():
            raise HandoffRefused(f"the plan's text for {row.key} is empty")


def apply_ocr_plan(  # noqa: PLR0913
    conn: sqlite3.Connection,
    plan: OcrPlan,
    worklist: OcrWorklist,
    *,
    cap: int,
    char_cap: int,
    today: date,
    apply: bool,
    dispatched: bool = False,
    within: Collection[str] | None = None,
) -> OcrSweepApplyResult:
    """Write each plan row whose stored row is still the scan the projection saw.

    The plan is checked whole first, against this window's worklist
    (:func:`check_plan`). Then, per row, the
    stored document of that case and kind must still be in the recovery class
    (:func:`~fedcourtsai.pipeline.ocr_recovery.exclusion_reason`) at the plan's URL. A
    row that has since gained text, or whose link moved, is skipped and named:
    the corpus moved on since the projection, which is not a forged plan.
    Additive, like the dispatched pass: text lands only where the stored row
    held none, with the extractor's ``ocr_derived`` reading, and a recovered
    petition re-derives its questions-presented row against the question
    stored now. Without ``apply`` it reports what it would write and writes nothing.

    ``dispatched`` is the dispatched pass's writer (:func:`check_plan`). It
    writes a row whose link now serves a filing of another length, as that pass
    always has, storing the page count the parse read: it reads the filing
    whole, so the reading is of the filing served now. ``within`` is the
    recovery class the writer walked before the write: a row outside it (its
    case left the live slice since the projection) is skipped as
    ``left-the-class``, so what is written is always counted out of that class.
    """
    check_plan(plan, worklist, cap=cap, char_cap=char_cap, dispatched=dispatched)
    written: dict[str, str] = {}
    skipped: dict[str, str] = {}
    rederived = 0
    for row in plan.rows:
        if within is not None and row.key not in within:
            skipped[row.key] = "left-the-class"
            continue
        stored: Mapping[str, corpus.CaseDocument] = {
            d.kind: d for d in corpus.documents_for_case(conn, row.case_id)
        }
        document = stored.get(row.kind)
        if document is None:
            skipped[row.key] = "no-stored-row"
            continue
        excluded = exclusion_reason(document)
        if excluded is not None:
            skipped[row.key] = excluded
            continue
        if document.url != row.url:
            skipped[row.key] = "url-changed"
            continue
        if document.pages != row.pages and not dispatched:
            # The link now serves a filing of another length than the one the
            # projection counted: a different document, which the dispatched
            # pass, reading it whole, is the route for.
            skipped[row.key] = "pages-changed"
            continue
        recovered = document.model_copy(
            update={
                "text": row.text,
                "pages": row.pages,
                "truncated": row.truncated,
                "ocr_derived": row.ocr_derived,
                "fetched_at": today,
            }
        )
        questions = stored.get(KIND_QUESTIONS_PRESENTED)
        follow_on = _rederived_questions(
            recovered, None if questions is None else questions.text, today=today
        )
        if apply:
            corpus.upsert_documents(conn, [recovered, *follow_on])
        rederived += len(follow_on)
        written[row.key] = (
            f"pages={row.pages} chars={len(row.text)} "
            f"truncated={str(row.truncated).lower()} "
            f"ocr_derived={str(row.ocr_derived).lower()}"
        )
    return OcrSweepApplyResult(
        applied=apply,
        planned=len(plan.rows),
        written=dict(sorted(written.items())),
        skipped=dict(sorted(skipped.items())),
        questions_rederived=rederived,
    )
