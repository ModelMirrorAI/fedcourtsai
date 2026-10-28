"""The re-cut pass split at the credential boundary, as run-repair's ``recut`` runs it.

The re-cut (:mod:`fedcourtsai.pipeline.document_recut`) fetches filed PDFs from
supremecourt.gov and parses them, so it runs in three jobs, like the OCR
recovery (:mod:`fedcourtsai.pipeline.ocr_sweep`):

- **worklist** (:func:`recut_worklist`) — the read-only projection job walks the
  class in scope and writes the slice the parse reads: each candidate's case
  id, kind, stored Court URL and stored page count. All four are public facts
  about public filings: the Court serves each at that URL.
- **plan** (:func:`plan_recut_worklist`) — the parse job, holding no credential,
  re-fetches each item and re-cuts it through the fetching lanes' own
  extractor, and judges what the served PDF alone shows
  (:func:`~fedcourtsai.pipeline.document_recut.served_reading`): a fetch that
  failed, bytes that do not parse, a page count other than the stored one, an
  empty re-cut. The plan carries the re-cut text of every other item, and
  nothing from our stores, and ends its slice before its rows would outgrow
  the hand-off cap, as it does at its deadline. That text is the Court's public filing, which for a
  self-represented filer includes contact details, so it crosses under the
  carve-out ``docs/data-sources.md`` (*PII stance*) proposes for it.
- **read** (:func:`apply_recut_plan`) — the writer, or on a dry run the
  read-only reader, walks the class itself, checks the plan whole against the
  projection's own worklist, and judges each re-cut against the stored text
  (:func:`~fedcourtsai.pipeline.document_recut.stored_judgement`): another
  filing (``head-changed``), the same text (``unchanged``), or the re-cut, with
  a petition's re-derived questions-presented row. The two halves are the pass
  in one job's checks, in its order, so the ledger reads as that pass's did.

The stored text never crosses: the head and unchanged checks read it, so they
run on the side that holds the corpus, and the dry run has a reader job of its
own for that reason.

Both files are untrusted on the receiving side. Every identifier in them is
pattern-checked (a SCOTUS case id, a re-cut kind, a Court URL, an outcome line
of a closed shape), and a file that fails is refused with only the error type
and list positions named (:func:`fedcourtsai.handoff.read_handoff`).
"""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable, Sequence
from datetime import date
from typing import Annotated, Final, Literal, cast

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, Strict, StringConstraints

from .. import corpus
from ..handoff import MAX_HANDOFF_BYTES, HandoffRefused
from ..supremecourt import SupremeCourtClient
from .document_recut import (
    FETCH_FAILED,
    LEFT_THE_CLASS,
    RECUT_KINDS,
    SCOPE_ALL_LIVE,
    SCOPE_PREDICT_RELEVANT,
    DocumentRecutResult,
    RecutLedger,
    _CandidateOutcome,
    estimated_seconds_for_pages,
    outcome_of,
    recut_candidates,
    served_reading,
    stored_judgement,
)
from .documents import ExtractedText
from .ocr_recovery import fetchable_document_url

#: The most items one worklist or plan may carry: an unbounded dry run's
#: worklist is the whole class in scope, identifiers only, and the parse's
#: deadline bounds how many of them it reaches.
MAX_RECUT_ITEMS: Final = 20_000

#: The largest text one plan row may carry. Above any configured document cap;
#: the reader also checks each row against the cap it is configured with.
MAX_PLAN_TEXT_CHARS: Final = 1_000_000

#: The bytes the parse lets its plan's rows take: the hand-off cap less room
#: for the skip and unreached lines, which carry identifiers only. Every row is
#: a head-cut filing re-cut near the document cap, so the deadline alone would
#: let a fast slice write a plan both readers refuse whole.
PLAN_ROW_BYTE_BUDGET: Final = MAX_HANDOFF_BYTES - 8 * 1024 * 1024


def _row_byte_ceiling(char_cap: int) -> int:
    """The most bytes one plan row of a ``char_cap`` text can take as JSON.

    Six bytes a character covers the longest escape, beside room for the
    row's identifiers.
    """
    return 6 * char_cap + 4096


#: The ledger line the parse writes for an item it judged without the stored
#: text: the pass's own detail strings, and nothing else. A closed shape, so a
#: forged plan cannot put free text in one.
_SKIP_PATTERN: Final = (
    r"^(unreadable|empty-after-recut"
    r"|unreadable \([A-Za-z_][A-Za-z0-9_]{0,79}\)"
    r"|pages-changed \(stored [0-9]{1,6}, served [0-9]{1,6}\)"
    r"|fetch-failed \((unfetchable-url|transport-error|not-served|oversized|http-[0-9]{3})\))$"
)


def _recut_kind(kind: str) -> str:
    if kind not in RECUT_KINDS:
        raise ValueError(f"not a re-cut kind: {kind[:40]!r}")
    return kind


def _recut_key(key: str) -> str:
    _recut_kind(key.split(" ", 1)[1])
    return key


def _court_url(url: str) -> str:
    if not fetchable_document_url(url) or any(ord(ch) < 0x21 for ch in url):
        raise ValueError("not a single https link on the Court's own host")
    return url


_CaseId = Annotated[str, StringConstraints(pattern=r"^scotus/[0-9]{1,12}$")]
_Kind = Annotated[str, AfterValidator(_recut_kind)]
_Url = Annotated[str, StringConstraints(max_length=2048), AfterValidator(_court_url)]
_Key = Annotated[
    str,
    StringConstraints(pattern=r"^scotus/[0-9]{1,12} [a-z-]{1,40}$"),
    AfterValidator(_recut_key),
]
_Skip = Annotated[str, StringConstraints(pattern=_SKIP_PATTERN)]
_Pages = Annotated[int, Strict(), Field(ge=1, le=100_000)]
_Scope = Literal["predict-relevant", "all-live"]


class RecutWorkItem(BaseModel):
    """One candidate the parse should re-cut.

    Public: a ledger case id, a document kind, the Court's own URL for the
    filing, and the page count of the PDF served there. No text, snapshot or
    other row content.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: _CaseId
    kind: _Kind
    url: _Url
    pages: _Pages

    @property
    def key(self) -> str:
        return f"{self.case_id} {self.kind}"


class RecutWorklist(BaseModel):
    """The slice of the re-cut class the parse reads, in class order.

    ``bound`` is the dispatch's slice size, or null on an unbounded dry run,
    whose worklist is then the whole class in scope.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/recut-worklist"] = "fedcourts/recut-worklist"
    version: Literal[1] = 1
    scope: _Scope
    bound: int | None = Field(default=None, ge=1, le=MAX_RECUT_ITEMS)
    items: list[RecutWorkItem] = Field(max_length=MAX_RECUT_ITEMS)


class RecutPlanRow(BaseModel):
    """One filing the parse re-cut: the text the extractor cut, and how.

    The text is the Court's own public filing as served at ``url``. It can carry
    a self-represented filer's contact details, which is why it crosses under
    the proposed carve-out and is never printed. ``pages`` is the served PDF's
    count, which the parse has already found equal to the stored row's.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: _CaseId
    kind: _Kind
    url: _Url
    text: str = Field(min_length=1, max_length=MAX_PLAN_TEXT_CHARS)
    pages: _Pages
    truncated: bool

    @property
    def key(self) -> str:
        return f"{self.case_id} {self.kind}"


class RecutPlan(BaseModel):
    """What the credential-free parse read: the file the reader judges and the writer applies."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/recut-plan"] = "fedcourts/recut-plan"
    version: Literal[1] = 1
    rows: list[RecutPlanRow] = Field(max_length=MAX_RECUT_ITEMS)
    skips: dict[_Key, _Skip] = Field(
        default_factory=dict,
        max_length=MAX_RECUT_ITEMS,
        description="`<case_id> <kind>` -> the outcome the served PDF alone settled",
    )
    unreached: list[_Key] = Field(
        default_factory=list,
        max_length=MAX_RECUT_ITEMS,
        description="Worklist items the slice deadline declined to start, in class order",
    )


def recut_worklist(
    conn: corpus.ReadConnection, *, scope: str, bound: int | None
) -> tuple[RecutWorklist, DocumentRecutResult]:
    """The worklist for one dispatch, and the class ledger the projection prints.

    The slice is the class's first ``bound`` candidates, in class order, as the
    pass in one job takes it; ``bound=None`` (an unbounded dry run) is the whole
    class. The ledger is the walk-only reading: nothing reached, the whole class
    remaining.
    """
    if scope not in (SCOPE_PREDICT_RELEVANT, SCOPE_ALL_LIVE):
        raise ValueError(f"unknown re-cut scope {scope!r}")
    scan = recut_candidates(conn, scope=scope)
    picked = scan.candidates if bound is None else scan.candidates[:bound]
    if len(picked) > MAX_RECUT_ITEMS:
        raise HandoffRefused(
            f"the class in scope holds {len(picked)} candidates, above the "
            f"{MAX_RECUT_ITEMS} one worklist may carry; bound the dry run"
        )
    worklist = RecutWorklist(
        scope=cast(_Scope, scope),  # checked against the two scopes above
        bound=bound,
        items=[
            RecutWorkItem(
                case_id=c.document.case_id,
                kind=c.document.kind,
                url=c.document.url,
                pages=c.document.pages,
            )
            for c in picked
        ],
    )
    return worklist, RecutLedger(None, apply=False).result(scan, scope=scope, bound=bound, sliced=0)


def _check_unique(keys: Sequence[str], what: str) -> None:
    seen: set[str] = set()
    for key in keys:
        if key in seen:
            raise HandoffRefused(f"the {what} names {key} twice")
        seen.add(key)


def check_recut_worklist(worklist: RecutWorklist) -> None:
    """Refuse a worklist the projection could not have written."""
    if worklist.bound is not None and len(worklist.items) > worklist.bound:
        raise HandoffRefused(
            f"the worklist carries {len(worklist.items)} items, above its bound of {worklist.bound}"
        )
    _check_unique([item.key for item in worklist.items], "worklist")


def plan_recut_worklist(
    client: SupremeCourtClient,
    worklist: RecutWorklist,
    *,
    char_cap: int,
    deadline: float | None = None,
    monotonic: Callable[[], float] = time.monotonic,
    byte_budget: int = PLAN_ROW_BYTE_BUDGET,
) -> RecutPlan:
    """Re-fetch and re-cut each worklist item, with no corpus: the plan.

    The pass's own per-candidate work up to the stored text, through
    :func:`~fedcourtsai.pipeline.document_recut.served_reading`, under the
    pass's slice deadline: before each item its cost is estimated from the
    stored page count, and the first that will not fit ends the slice, it and
    the rest reported unreached. ``byte_budget`` ends it the same way, before
    an item whose largest possible row would take the plan's rows past it, so
    the plan stays under the hand-off cap its readers enforce.
    """
    check_recut_worklist(worklist)
    rows: list[RecutPlanRow] = []
    skips: dict[str, str] = {}
    unreached: list[str] = []
    spent = 0
    for index, item in enumerate(worklist.items):
        if spent + _row_byte_ceiling(char_cap) > byte_budget or (
            deadline is not None
            and estimated_seconds_for_pages(item.pages) > deadline - monotonic()
        ):
            unreached = [i.key for i in worklist.items[index:]]
            break
        extracted, detail, _reason = served_reading(
            client, item, stored_pages=item.pages, char_cap=char_cap
        )
        if extracted is None:
            skips[item.key] = detail
            continue
        row = RecutPlanRow(
            case_id=item.case_id,
            kind=item.kind,
            url=item.url,
            text=extracted.text,
            pages=extracted.pages,
            truncated=extracted.truncated,
        )
        spent += len(row.model_dump_json().encode())
        rows.append(row)
    return RecutPlan(rows=rows, skips=dict(sorted(skips.items())), unreached=unreached)


def check_recut_plan(plan: RecutPlan, worklist: RecutWorklist, *, char_cap: int) -> None:
    """Refuse a plan the parse could not have written for this worklist, whole.

    The read already refused any malformed identifier, URL or outcome line.
    Beyond that: a key named twice across rows, skips and unreached; a plan that
    does not account for every worklist item exactly once (the ledger is built
    on it, and an item it dropped would vanish from it); a key that is not an
    item of ``worklist`` (the projection's own file, which the parse cannot
    replace); a row at another URL than its item's, or of another page count
    (the parse skips that as ``pages-changed``); unreached items that are not
    the worklist's tail in its order (the parse ends its slice, it never skips
    ahead); a ``pages-changed`` skip that does not name its item's stored page
    count beside a different served one; and a text longer than the configured
    document cap, or whitespace only. A row's text is checked against the
    stored filing only by the head check the pass already makes: the reader
    holds no PDF to re-cut, so text after a matching opening is the parse's.
    """
    check_recut_worklist(worklist)
    keys = [row.key for row in plan.rows] + [*plan.skips, *plan.unreached]
    _check_unique(keys, "plan")
    items = {item.key: item for item in worklist.items}
    for key in keys:
        if key not in items:
            raise HandoffRefused(f"the plan reports {key}, which is not on this worklist")
    if len(keys) != len(worklist.items):
        raise HandoffRefused(
            f"the plan accounts for {len(keys)} of the worklist's {len(worklist.items)} items"
        )
    order = [item.key for item in worklist.items]
    if plan.unreached != order[len(order) - len(plan.unreached) :]:
        raise HandoffRefused("the plan's unreached items are not the worklist's tail, in order")
    for key, detail in plan.skips.items():
        if detail.startswith("pages-changed") and (
            not detail.startswith(f"pages-changed (stored {items[key].pages}, ")
            or detail == f"pages-changed (stored {items[key].pages}, served {items[key].pages})"
        ):
            raise HandoffRefused(
                f"the plan's skip for {key} does not name its stored page count beside another"
            )
    for row in plan.rows:
        item = items[row.key]
        if row.url != item.url or row.pages != item.pages:
            raise HandoffRefused(
                f"the plan's row {row.key} is not this worklist's item at its URL and page count"
            )
        if len(row.text) > char_cap:
            raise HandoffRefused(
                f"the plan's text for {row.key} is {len(row.text)} characters, "
                f"above the {char_cap}-character document cap"
            )
        if not row.text.strip():
            raise HandoffRefused(f"the plan's text for {row.key} is empty")


def apply_recut_plan(
    conn: sqlite3.Connection,
    plan: RecutPlan,
    worklist: RecutWorklist,
    *,
    char_cap: int,
    today: date,
    apply: bool,
) -> DocumentRecutResult:
    """Judge each plan row against the stored text, and write the re-cuts on an apply.

    The class is walked here, before anything is written, over the worklist's
    own scope, so ``remaining`` is that class less the re-cuts that left it —
    the number the workflow's re-read must then find. A plan row whose stored
    row is no longer in the class at the worklist's URL and page count is
    ``left-the-class``: the corpus moved since the projection, which is not a
    forged plan. Without ``apply`` it reports what an apply would write and
    writes nothing, which is the dry run's reading.
    """
    check_recut_plan(plan, worklist, char_cap=char_cap)
    scan = recut_candidates(conn, scope=worklist.scope)
    in_class = {candidate.key: candidate for candidate in scan.candidates}
    rows = {row.key: row for row in plan.rows}
    unreached = set(plan.unreached)
    ledger = RecutLedger(conn, apply=apply)
    for item in worklist.items:
        key = item.key
        if key in unreached:
            ledger.unreach(key, item.kind)
            continue
        if key in plan.skips:
            detail = plan.skips[key]
            outcome = outcome_of(detail)
            # A fetch failure's reason class is the parenthesis the pattern pinned.
            fetch_reason = detail[len(FETCH_FAILED) + 2 : -1] if outcome == FETCH_FAILED else None
            ledger.reach(
                key, item.kind, _CandidateOutcome(outcome, detail, fetch_reason=fetch_reason)
            )
            continue
        row = rows[key]
        candidate = in_class.get(key)
        if (
            candidate is None
            or candidate.document.url != item.url
            or candidate.document.pages != item.pages
        ):
            ledger.reach(key, item.kind, _CandidateOutcome(LEFT_THE_CLASS, LEFT_THE_CLASS))
            continue
        extracted = ExtractedText(text=row.text, pages=row.pages, truncated=row.truncated)
        ledger.reach(key, item.kind, stored_judgement(candidate, extracted, today=today))
    return ledger.result(
        scan, scope=worklist.scope, bound=worklist.bound, sliced=len(worklist.items)
    )
