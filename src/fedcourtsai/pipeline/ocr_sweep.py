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
  under the carve-out ``docs/data-sources.md`` (*PII stance*) records for it.
- **apply** (:func:`apply_ocr_plan`) — the writer re-checks every plan row against
  the corpus it is about to write: the row must still be in the recovery class,
  at the same URL, and the plan no larger than the cap. Then it writes exactly
  what the dispatched pass would: the text, the ``ocr_derived`` marker, and a
  petition's re-derived questions-presented row.

**Sweep order** (:func:`order_sweep_class`, pure). A candidate a forward cell
will read comes first: its case carries an open event, its row is in predict
scope, and salience has not deferred it (an open merits event bypasses
salience, as at the predict seams). These are ordered newest stored first,
because the cell for a new scan is closest. The backlog follows in class order,
rotated by the window's date. A candidate the sweep cannot recover (an
unreadable scan, a refused fetch) stays in the class, as on the dispatched pass,
so without the rotation an unreadable head would take the cap every window and
starve the rest. The forward tier is not rotated. A case leaves it when it is
decided, so an unreadable forward scan holds the cap for days at most, not
indefinitely.
"""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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
    ocr_page_for_pdf,
    read_scanned_document,
    require_ocr_binaries,
    scanned_documents,
)

#: The largest slice a worklist or plan may carry. Above any configured cap
#: (``historical.sweep_caps.ocr`` is bounded below it), so a file past it is
#: refused as malformed rather than read.
MAX_SWEEP_ITEMS = 200

#: The largest text one plan row may carry. Above any configured document cap;
#: the writer also checks each row against the cap it is configured with.
MAX_PLAN_TEXT_CHARS = 1_000_000


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
    candidates: Sequence[SweepCandidate], *, rotation: int
) -> list[SweepCandidate]:
    """The recovery class in sweep order: forward newest-stored first, then the rotated backlog.

    ``candidates`` arrive in class order (``case_id``, then kind), which is the
    order ties keep within the forward tier and the order the backlog rotates
    from. ``rotation`` is any integer; the backlog starts at ``rotation`` modulo
    its length. Pure: the same class and rotation give the same order.
    """
    forward = [c for c in candidates if c.forward]
    backlog = [c for c in candidates if not c.forward]
    # Newest stored first. Python's sort is stable, so equal dates keep class order.
    forward.sort(key=lambda c: c.scanned.document.fetched_at, reverse=True)
    if backlog:
        start = rotation % len(backlog)
        backlog = backlog[start:] + backlog[:start]
    return forward + backlog


def backlog_rotation(today: date, cap: int) -> int:
    """The backlog's starting offset for a window on ``today``.

    One cap's width further on each day, so that over consecutive days the slices
    tile the backlog rather than retrying the same head. Windows on the same day
    share the offset; between them the class only shrinks by what they recovered.
    """
    return today.toordinal() * cap


class OcrWorkItem(BaseModel):
    """One candidate the parse should re-read.

    Public: a ledger case id, a document kind, the Court's own URL for the filing,
    and the page count of the PDF served there. ``forward`` says that a forward
    cell will read it, which the committed predictions under ``data/`` already
    show. No text, snapshot or other row content.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str = Field(min_length=1, max_length=64)
    kind: str = Field(min_length=1, max_length=64)
    url: str = Field(min_length=1, max_length=2048)
    pages: int = Field(ge=1, le=100_000)
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
    filer's contact details, which is why it crosses under the recorded carve-out
    and is never printed. ``pages``, ``truncated`` and ``ocr_derived`` are the
    extractor's own readings, stored on the row exactly as the dispatched pass
    stores them.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str = Field(min_length=1, max_length=64)
    kind: str = Field(min_length=1, max_length=64)
    url: str = Field(min_length=1, max_length=2048)
    text: str = Field(min_length=1, max_length=MAX_PLAN_TEXT_CHARS)
    pages: int = Field(ge=1, le=100_000)
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
    failures: dict[str, str] = Field(
        default_factory=dict,
        description="`<case_id> <kind>` -> why the parse read no text for it",
    )
    unreached: list[str] = Field(
        default_factory=list,
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
    candidates: Sequence[SweepCandidate], *, cap: int, rotation: int
) -> tuple[SweepCandidate, ...]:
    """The first ``cap`` candidates in sweep order (:func:`order_sweep_class`)."""
    if cap < 1:
        raise ValueError("the sweep cap must be at least 1")
    return tuple(order_sweep_class(candidates, rotation=rotation)[:cap])


def sweep_selection(conn: corpus.ReadConnection, *, cap: int, today: date) -> SweepSelection:
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
        slice=select_sweep(candidates, cap=cap, rotation=backlog_rotation(today, cap)),
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
    for item in worklist.items:
        if item.kind not in RECOVERABLE_KINDS:
            raise HandoffRefused(f"the worklist names {item.key}, not a recoverable kind")


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


def check_plan(plan: OcrPlan, *, cap: int, char_cap: int) -> None:
    """Refuse a plan the parse could not have written for this window, whole.

    More rows than the window's cap, a key named twice, a kind outside the
    recovery class, a text longer than the configured document cap, or a text
    that is whitespace only.
    """
    if len(plan.rows) > cap:
        raise HandoffRefused(f"the plan carries {len(plan.rows)} rows, above the cap of {cap}")
    _check_unique([row.key for row in plan.rows], "plan")
    for row in plan.rows:
        if row.kind not in RECOVERABLE_KINDS:
            raise HandoffRefused(f"the plan names {row.key}, not a recoverable kind")
        if len(row.text) > char_cap:
            raise HandoffRefused(
                f"the plan's text for {row.key} is {len(row.text)} characters, "
                f"above the {char_cap}-character document cap"
            )
        if not row.text.strip():
            raise HandoffRefused(f"the plan's text for {row.key} is empty")


def apply_ocr_plan(
    conn: sqlite3.Connection,
    plan: OcrPlan,
    *,
    cap: int,
    char_cap: int,
    today: date,
    apply: bool,
) -> OcrSweepApplyResult:
    """Write each plan row whose stored row is still the scan the projection saw.

    The plan is checked whole first (:func:`check_plan`). Then, per row, the
    stored document of that case and kind must still be in the recovery class
    (:func:`~fedcourtsai.pipeline.ocr_recovery.exclusion_reason`) at the plan's URL. A
    row that has since gained text, or whose link moved, is skipped and named:
    the corpus moved on since the projection, which is not a forged plan.
    Additive, like the dispatched pass: text lands only where the stored row
    held none, with the extractor's ``ocr_derived`` reading, and a recovered
    petition re-derives its questions-presented row against the question
    stored now. Without ``apply`` it reports what it would write and writes nothing.
    """
    check_plan(plan, cap=cap, char_cap=char_cap)
    written: dict[str, str] = {}
    skipped: dict[str, str] = {}
    rederived = 0
    for row in plan.rows:
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
