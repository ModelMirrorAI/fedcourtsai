"""The bounded re-cut pass for filings stored under the plain head cut.

The `petition`, `application` and `appendix` kinds are cut at the document cap
the appendix-aware way (:func:`~fedcourtsai.pipeline.documents.extract_filing_text`):
the filing's own body is kept whole, each appendix item keeps its opening, and
every cut leaves a ``[pipeline note: …]`` line in the text. Fetching is
idempotent per kind and URL, so a row stored before that cut existed keeps the
plain head cut — the cap landing wherever it lands, usually inside the
appendix, with nothing in the text to say so — for as long as the docket keeps
serving the same link. This is the pass that re-cuts those rows, on the terms
recorded in *Contract for the re-cut pass* (`docs/live-sources.md`):

- **Population.** Stored rows of an appendix-bearing kind that are
  ``truncated``, not ``ocr_derived``, carry no ``[pipeline note:`` line, and
  whose stored URL is one Court link. An untruncated row was never cut, so the
  two cuts agree on it. An OCR-recovered row is head-cut by design
  (:func:`~fedcourtsai.pipeline.documents.extract_filing_text` says why) and
  re-reading it without OCR would empty it. A row whose text carries a note was
  cut the appendix-aware way already. A set-keyed or off-host URL is one this
  pass will not GET.
- **Scope.** The predict-relevant live-slice rows by default — queued for
  prediction or selected by the salience gate
  (:func:`~fedcourtsai.pipeline.document_backfill.is_predict_relevant`), the
  cases whose cells can still read the row — or the whole live slice.
- **Re-fetch.** By the row's own stored URL on supremecourt.gov, through the
  same polite client and the same guards the OCR recovery uses
  (:func:`~fedcourtsai.pipeline.ocr_recovery._refetch_document`).
- **Re-cut.** Through the fetching lanes' own extractor at the configured cap.
  A served PDF whose page count differs from the stored row's is another
  filing at the same link and is skipped as ``pages-changed``, as is one whose
  text does not open with the stored row's (``head-changed``); bytes that do
  not parse are ``unreadable``; a re-cut equal to the stored text is
  ``unchanged``; an empty re-cut is never written.
- **What follows.** A re-cut **petition** re-derives its
  ``questions-presented`` row through the ingest path's own deriver, from the
  stored text and from the re-cut, and writes it only where the two differ.
  The section sits in the front matter, which both cuts keep, so the two are
  expected to agree; a stored row the current deriver would read differently
  off either text is a questions-presented back-fill's to converge, not this
  pass's.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..supremecourt import SupremeCourtClient
from .document_backfill import is_predict_relevant
from .documents import (
    _CUT_NOTE_OPENER,
    APPENDIX_BEARING_KINDS,
    FETCHED_DOCUMENT_KINDS,
    KIND_PETITION,
    KIND_QUESTIONS_PRESENTED,
    ExtractedText,
    _derived_questions_document,
    extract_filing_text,
    extract_questions_presented,
)
from .ocr_recovery import DocumentRef, _refetch_document, fetchable_document_url
from .prefetch import prefetch_by_case

logger = logging.getLogger(__name__)

#: The kinds this pass re-cuts, in the fetched kinds' order so a case's
#: petition heads its candidates.
RECUT_KINDS: tuple[str, ...] = tuple(
    kind for kind in FETCHED_DOCUMENT_KINDS if kind in APPENDIX_BEARING_KINDS
)

#: The two scopes the population is walked over.
SCOPE_PREDICT_RELEVANT = "predict-relevant"
SCOPE_ALL_LIVE = "all-live"

# What one candidate is estimated to cost, which the slice deadline admits or
# declines it on: one throttled GET of a filing that runs to a few megabytes,
# a text-layer read of every page (the appendix-aware cut reads the whole
# filing, not the head the cap keeps), and the upsert. Five production
# petitions of 96 to 424 pages, 1,094 in all, took about 11 s together from a
# dev session, about 2 s a candidate. The estimate is set several times above
# that on purpose: declining a candidate costs nothing (it stays at the head of
# the class), while admitting one that does not fit costs the step its write
# tail. A GET that times out and takes the client's retry runs past it, which
# the caller's reserve carries.
ESTIMATED_CANDIDATE_OVERHEAD_SECONDS = 10.0
ESTIMATED_SECONDS_PER_PAGE = 0.05

#: The outcomes a reached candidate ends in, in ledger order.
RECUT = "recut"
UNCHANGED = "unchanged"
PAGES_CHANGED = "pages-changed"
HEAD_CHANGED = "head-changed"
UNREADABLE = "unreadable"
EMPTY_AFTER_RECUT = "empty-after-recut"
FETCH_FAILED = "fetch-failed"
UNREACHED = "unreached"
#: Only the split pass's writer reaches this one: the stored row it re-checks a
#: plan row against has left the class, or holds another filing, since the
#: projection read it.
LEFT_THE_CLASS = "left-the-class"
OUTCOMES: tuple[str, ...] = (
    RECUT,
    UNCHANGED,
    PAGES_CHANGED,
    HEAD_CHANGED,
    UNREADABLE,
    EMPTY_AFTER_RECUT,
    FETCH_FAILED,
    LEFT_THE_CLASS,
    UNREACHED,
)

# How much of the stored text a re-cut must open with to be the same filing.
# Both cuts keep the filing's own text from its first page, so a stored head
# cut and its re-cut agree there; a filing corrected and re-posted at the same
# link with the same page count does not.
HEAD_CHECK_CHARS = 2000

#: Why a stored row is out of the class. The first two are the ordinary shape
#: of a corpus that is mostly fine and are not tallied; the rest are rows a
#: reader might expect in the class and will not find there.
NOT_A_RECUT_KIND = "not-an-appendix-bearing-kind"
NOT_TRUNCATED = "not-truncated"
OCR_DERIVED = "ocr-derived"
HAS_CUT_NOTE = "has-cut-note"
UNFETCHABLE_URL = "unfetchable-url"
_TALLIED_EXCLUSIONS: tuple[str, ...] = (OCR_DERIVED, HAS_CUT_NOTE, UNFETCHABLE_URL)


def exclusion_reason(document: corpus.CaseDocument) -> str | None:
    """Why this row is out of the re-cut class, or ``None`` if it is in it.

    Stated as reasons rather than a conjunction, so the ledger's exclusion
    tallies cannot drift from the test that excluded the rows.
    """
    if document.kind not in APPENDIX_BEARING_KINDS:
        return NOT_A_RECUT_KIND
    if not document.truncated:
        return NOT_TRUNCATED
    if document.ocr_derived:
        return OCR_DERIVED
    if _CUT_NOTE_OPENER in document.text:
        return HAS_CUT_NOTE
    if not fetchable_document_url(document.url):
        return UNFETCHABLE_URL
    return None


@dataclass(frozen=True)
class RecutCandidate:
    """One stored row in the class, with its case's stored questions-presented text.

    ``stored_questions`` is read in the same walk that found the row and is
    carried on a petition alone, since no other kind has a derived section.
    """

    document: corpus.CaseDocument
    stored_questions: corpus.CaseDocument | None

    @property
    def key(self) -> str:
        """``<case_id> <kind>``: a case can hold a petition and an appendix at once."""
        return f"{self.document.case_id} {self.document.kind}"


def estimated_seconds_for_pages(pages: int) -> float:
    """The wall clock the slice deadline admits one candidate of ``pages`` stored pages on."""
    return ESTIMATED_CANDIDATE_OVERHEAD_SECONDS + max(pages, 0) * ESTIMATED_SECONDS_PER_PAGE


def estimated_candidate_seconds(candidate: RecutCandidate) -> float:
    """The wall clock the slice deadline admits one candidate on."""
    return estimated_seconds_for_pages(candidate.document.pages)


@dataclass(frozen=True)
class RecutScan:
    """What one walk of the corpus saw.

    ``documents_seen`` is the denominator — stored rows of an appendix-bearing
    kind in scope — and is what tells a converged class from a blob whose
    documents this process cannot read (a split-mode index with no content
    store configured serves every case an empty document list).
    """

    candidates: tuple[RecutCandidate, ...]
    cases_seen: int
    documents_seen: int
    excluded: dict[str, int]


def _scope_rows(conn: corpus.ReadConnection, scope: str) -> list[str]:
    if scope not in (SCOPE_PREDICT_RELEVANT, SCOPE_ALL_LIVE):
        raise ValueError(f"unknown re-cut scope {scope!r}")
    return [
        row.case_id
        for row in corpus.iter_rows(conn, court="scotus", live_slice=True)
        if scope == SCOPE_ALL_LIVE or is_predict_relevant(row)
    ]


def recut_candidates(
    conn: corpus.ReadConnection, *, scope: str = SCOPE_PREDICT_RELEVANT
) -> RecutScan:
    """Every stored row in the re-cut class, in ``case_id`` then kind order.

    Walked case by case through :func:`~fedcourtsai.corpus.documents_for_case`
    rather than queried, because under the corpus split the text lives in the
    per-case content store and the blob's ``documents`` table holds none of it.
    The order is what makes a bounded slice self-advancing: a re-cut row
    carries a cut note and leaves the class.
    """
    case_ids = _scope_rows(conn, scope)
    found: list[RecutCandidate] = []
    documents_seen = 0
    excluded: dict[str, int] = {}
    with prefetch_by_case(
        case_ids,
        lambda case_id: corpus.documents_for_case(conn, case_id),
        thread_name_prefix="document-recut",
    ) as fetched:
        for _case_id, documents in fetched:
            by_kind = {document.kind: document for document in documents}
            questions = by_kind.get(KIND_QUESTIONS_PRESENTED)
            for kind in RECUT_KINDS:
                document = by_kind.get(kind)
                if document is None:
                    continue
                documents_seen += 1
                reason = exclusion_reason(document)
                if reason is not None:
                    if reason in _TALLIED_EXCLUSIONS:
                        excluded[reason] = excluded.get(reason, 0) + 1
                    continue
                found.append(
                    RecutCandidate(
                        document=document,
                        stored_questions=questions if kind == KIND_PETITION else None,
                    )
                )
    return RecutScan(
        candidates=tuple(found),
        cases_seen=len(case_ids),
        documents_seen=documents_seen,
        excluded={reason: excluded[reason] for reason in _TALLIED_EXCLUSIONS if reason in excluded},
    )


class DocumentRecutResult(BaseModel):
    """What one re-cut pass found, and wrote (or would write, on a dry run)."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the rows or only reported them")
    scope: str = Field(
        description="`predict-relevant` (live-slice rows queued for prediction or "
        "selected by the salience gate) or `all-live` (the whole live slice)"
    )
    cases_seen: int = Field(ge=0, description="Live-slice SCOTUS rows in scope")
    documents_seen: int = Field(
        ge=0,
        description="Stored rows of an appendix-bearing kind in scope — the denominator "
        "under `candidates`. Zero means the documents could not be read rather than that "
        "the class is empty",
    )
    candidates: int = Field(
        ge=0,
        description="Stored petition, application and appendix rows that are truncated, "
        "not OCR-derived, carry no `[pipeline note:` line and have one fetchable Court "
        "URL — the whole re-cut class in scope",
    )
    candidates_by_kind: dict[str, int] = Field(
        default_factory=dict, description="The class cut by document kind"
    )
    excluded: dict[str, int] = Field(
        default_factory=dict,
        description="Truncated rows left out of the class, by reason: `ocr-derived` "
        "(head-cut by design), `has-cut-note` (already cut the appendix-aware way) and "
        "`unfetchable-url` (a set key or a URL off the Court's host)",
    )
    bound: int | None = Field(
        default=None,
        description="The slice size the run was bounded to; null on an unbounded dry run",
    )
    attempted: int = Field(
        ge=0,
        description="Candidates this run re-fetched — never more than `bound`, and short "
        "of it by the ones the slice deadline declined to start",
    )
    unreached: list[str] = Field(
        default_factory=list,
        description="Candidates inside the bound the slice deadline declined to start, as "
        "`<case_id> <kind>`, in class order: untouched, and at the head of the next slice",
    )
    outcomes_by_kind: dict[str, dict[str, int]] = Field(
        default_factory=dict,
        description="Kind -> outcome -> count over the slice: `recut` (an apply wrote "
        "it; a dry run would), `unchanged`, `pages-changed` (the link now serves a PDF "
        "of another page count — another filing), `head-changed` (same page count, but "
        "the text opens differently — another filing), `unreadable` (the served bytes "
        "did not parse as a PDF), `empty-after-recut`, `fetch-failed`, `left-the-class` "
        "(the split pass's writer found the stored row out of the class, or holding another "
        "filing, since the projection read it) and `unreached`",
    )
    recut: int = Field(ge=0, description="Rows re-cut (written on an apply)")
    unchanged: int = Field(ge=0, description="Rows whose re-cut equals the stored text")
    pages_changed: int = Field(
        ge=0, description="Rows skipped because the served PDF's page count differs"
    )
    head_changed: int = Field(
        ge=0,
        description="Rows skipped because the re-cut does not open with the stored text",
    )
    unreadable: int = Field(
        ge=0, description="Rows skipped because the served bytes did not parse as a PDF"
    )
    empty_after_recut: int = Field(
        ge=0, description="Rows whose re-cut read no text; never written over stored text"
    )
    fetch_failed: dict[str, int] = Field(
        default_factory=dict,
        description="Candidates the re-fetch did not return, reason class -> count",
    )
    remaining: int = Field(
        ge=0,
        description="Candidates an apply leaves in the class: every candidate less the "
        "re-cut rows it wrote that left it, which is what the step's walk-only re-read "
        "must find. On a dry run, the whole class",
    )
    questions_rederived: int = Field(
        ge=0,
        description="Questions-presented rows whose derivation the re-cut moved — derived "
        "from the re-cut petition differently than from the stored one (written on an "
        "apply)",
    )
    recuts: dict[str, str] = Field(
        default_factory=dict,
        description="`<case_id> <kind>` -> what the re-cut holds: the record of which "
        "stored rows an applied pass replaced",
    )
    skipped: dict[str, str] = Field(
        default_factory=dict,
        description="`<case_id> <kind>` -> why this candidate was reached and not re-cut",
    )


def _rederived_questions(
    previous: corpus.CaseDocument,
    recut: corpus.CaseDocument,
    stored: corpus.CaseDocument | None,
    *,
    today: date,
) -> list[corpus.CaseDocument]:
    """The questions-presented row a re-cut **petition** moves, if it moves one.

    The row is re-derived from the petition text twice, as stored and as re-cut,
    and written only where the two derivations differ: that is the change the
    re-cut makes. A stored row that differs from what the current deriver reads
    off the *stored* petition is a cutter change no back-fill has converged yet
    — `backfill-questions-presented`'s work, with its own classes and
    refusals — so this pass leaves it as it is. Then the ingest path's rule (no
    heading stores no row) and the recovery pass's guard (an empty derivation
    never replaces a stored question).
    """
    if recut.kind != KIND_PETITION:
        return []
    questions = extract_questions_presented(recut.text)
    before = extract_questions_presented(previous.text)
    if questions == before:
        return []
    if stored is not None and stored.text != (before or ""):
        # The stored row is not what the current deriver reads off the stored
        # petition: a cutter change still to converge, left to that back-fill.
        return []
    if questions is None:
        return []
    if not questions and stored is not None and stored.text.strip():
        return []
    return [_derived_questions_document(recut, questions, fetched_at=today)]


def _letters_and_digits(text: str) -> str:
    return "".join(c for c in text if c.isascii() and c.isalnum())


def _same_head(recut: str, stored: str) -> bool:
    """Whether the re-cut opens with the stored text, up to its first cut note.

    Compared on ASCII letters and digits alone: the PDF library's text layout
    moves line breaks between versions (a break inside a name, one joined onto
    the next line), and it reads a caption's decorative glyphs as different
    characters, some of them non-ASCII letters, neither of which is another
    filing. A re-cut head with no letter or digit opens no stored text that has one.
    """
    note = recut.find(_CUT_NOTE_OPENER)
    head = _letters_and_digits(recut[: min(HEAD_CHECK_CHARS, note if note >= 0 else len(recut))])
    opening = _letters_and_digits(stored[: HEAD_CHECK_CHARS * 2])
    if not head:
        return not opening
    length = min(len(head), len(opening))
    return head[:length] == opening[:length]


@dataclass(frozen=True)
class _CandidateOutcome:
    """What one reached candidate came to: its outcome, and the rows to write."""

    outcome: str
    detail: str
    recut: corpus.CaseDocument | None = None
    questions: tuple[corpus.CaseDocument, ...] = ()
    fetch_reason: str | None = None


def served_reading(
    client: SupremeCourtClient, document: DocumentRef, *, stored_pages: int, char_cap: int
) -> tuple[ExtractedText | None, str, str | None]:
    """Re-fetch and re-cut one filing, judged on what the served PDF alone shows.

    The half of a candidate's outcome that needs no stored text: the fetch, the
    parse, the page count against the stored row's, and an empty re-cut. Returns
    the extraction to judge against the stored text, or ``None`` with the
    outcome's ledger detail and, for a fetch that failed, its reason class. The
    split pass's parse runs exactly this, holding only the public page count.
    """
    data, refused = _refetch_document(client, document)
    if data is None:
        reason = refused or "not-served"
        return None, f"{FETCH_FAILED} ({reason})", reason
    try:
        extracted = extract_filing_text(data, kind=document.kind, char_cap=char_cap)
    except Exception as exc:  # one bad PDF must not cost the slice its ledger
        return None, f"{UNREADABLE} ({type(exc).__name__})", None
    if extracted.pages == 0:
        # The extractor's answer to bytes it could not parse: an error page or
        # a truncated body served as a PDF, not another filing.
        return None, UNREADABLE, None
    if extracted.pages != stored_pages:
        # The stored row's pages are the whole PDF's under either cut, so a
        # different count is a different filing at the same link — the fetching
        # lanes' business, not a re-cut.
        return None, f"{PAGES_CHANGED} (stored {stored_pages}, served {extracted.pages})", None
    if not extracted.text.strip():
        return None, EMPTY_AFTER_RECUT, None
    return extracted, RECUT, None


def outcome_of(detail: str) -> str:
    """The ledger outcome a skip's detail line names: its first word."""
    return detail.split(" ", 1)[0]


def stored_judgement(
    candidate: RecutCandidate, extracted: ExtractedText, *, today: date
) -> _CandidateOutcome:
    """The half of a candidate's outcome that reads the stored text: what to write.

    A re-cut that does not open with the stored text is another filing
    (``head-changed``); one equal to it, truncation flag included, is
    ``unchanged``; anything else is the re-cut, with a petition's re-derived
    questions-presented row where the re-cut moves it.
    """
    document = candidate.document
    if not _same_head(extracted.text, document.text):
        return _CandidateOutcome(HEAD_CHANGED, HEAD_CHANGED)
    if extracted.text == document.text and extracted.truncated == document.truncated:
        return _CandidateOutcome(UNCHANGED, UNCHANGED)
    recut = document.model_copy(
        update={
            "text": extracted.text,
            "pages": extracted.pages,
            "truncated": extracted.truncated,
            "fetched_at": today,
        }
    )
    questions = tuple(
        _rederived_questions(document, recut, candidate.stored_questions, today=today)
    )
    detail = (
        f"pages={extracted.pages} chars={len(document.text)}->{len(extracted.text)} "
        f"notes={extracted.text.count(_CUT_NOTE_OPENER)} "
        f"truncated={str(extracted.truncated).lower()}"
        + (" questions-presented=rederived" if questions else "")
    )
    return _CandidateOutcome(RECUT, detail, recut=recut, questions=questions)


def _recut_one(
    client: SupremeCourtClient, candidate: RecutCandidate, *, char_cap: int, today: date
) -> _CandidateOutcome:
    """Re-fetch and re-cut one candidate; what to write, or why nothing."""
    document = candidate.document
    extracted, detail, fetch_reason = served_reading(
        client, document, stored_pages=document.pages, char_cap=char_cap
    )
    if extracted is None:
        return _CandidateOutcome(outcome_of(detail), detail, fetch_reason=fetch_reason)
    return stored_judgement(candidate, extracted, today=today)


def recut_documents(  # noqa: PLR0913 - keyword-only; slice deadline + injected clock over the pass's args
    conn: sqlite3.Connection,
    *,
    client: SupremeCourtClient,
    apply: bool,
    char_cap: int,
    today: date,
    max_cases: int | None = None,
    scope: str = SCOPE_PREDICT_RELEVANT,
    deadline: float | None = None,
    monotonic: Callable[[], float] = time.monotonic,
) -> DocumentRecutResult:
    """Re-fetch and re-cut the head-cut filings; write the re-cut rows on an apply.

    Both modes re-fetch and re-cut, because the outcome — a re-cut, an unchanged
    text, a link now serving another filing — is only known from the served PDF,
    and that is what a maintainer reads before approving an apply. The **dry
    run** writes nothing and takes ``max_cases`` when given (unbounded
    otherwise, which the caller's deadline then bounds); the **apply** requires
    it. ``max_cases=0`` is the walk-only reading: it fetches nothing.

    ``deadline`` is a :func:`time.monotonic` reading past which no new
    candidate is started. Before each candidate its estimate
    (:func:`estimated_candidate_seconds`) is checked against what is left, and
    the first that does not fit ends the slice: it and every candidate behind it
    are reported ``unreached``. A started candidate is finished.

    Each re-cut is written as it is made, so a step cut short by its cap has
    banked what it wrote. The written row keeps the stored ``entry_date``,
    ``url`` and kind and takes the re-cut's text, page count and truncation flag;
    its ``fetched_at`` moves to ``today``, because a fetch did happen. The
    replaced text stays recoverable: the content store's text leaves are
    content-addressed, so a re-cut writes a new leaf beside the old one.
    """
    if apply and max_cases is None:
        raise ValueError("an apply must carry its slice bound")
    scan = recut_candidates(conn, scope=scope)
    candidates = scan.candidates
    slice_ = candidates if max_cases is None else candidates[:max_cases]
    ledger = RecutLedger(conn, apply=apply)
    for index, candidate in enumerate(slice_):
        if deadline is not None:
            estimate = estimated_candidate_seconds(candidate)
            left = deadline - monotonic()
            if estimate > left:
                tail = slice_[index:]
                for c in tail:
                    ledger.unreach(c.key, c.document.kind)
                logger.warning(
                    "recut: slice deadline reached with %.0fs left; %d candidate(s) not "
                    "started, first %s (%d pages, ~%.0fs)",
                    left,
                    len(tail),
                    candidate.key,
                    candidate.document.pages,
                    estimate,
                )
                break
        ledger.reach(
            candidate.key,
            candidate.document.kind,
            _recut_one(client, candidate, char_cap=char_cap, today=today),
        )
    return ledger.result(scan, scope=scope, bound=max_cases, sliced=len(slice_))


class RecutLedger:
    """The pass's ledger, kept candidate by candidate, writing each re-cut as it is made.

    One accumulator for the pass in one job and for the split pass's writer, so
    the two ledgers cannot drift: the writer reaches a candidate with the
    outcome its plan row and the stored text come to, the in-job pass with the
    one its own fetch does.
    """

    def __init__(self, conn: sqlite3.Connection | None, *, apply: bool) -> None:
        if apply and conn is None:
            raise ValueError("an applying ledger writes through a connection")
        self._conn = conn
        self._apply = apply
        self._outcomes: dict[str, dict[str, int]] = {}
        self._counts = dict.fromkeys(OUTCOMES, 0)
        self._recuts: dict[str, str] = {}
        self._skipped: dict[str, str] = {}
        self._fetch_failed: dict[str, int] = {}
        self._unreached: list[str] = []
        self._questions_rederived = 0
        self._left_class = 0

    def _record(self, kind: str, outcome: str) -> None:
        by_kind = self._outcomes.setdefault(kind, {})
        by_kind[outcome] = by_kind.get(outcome, 0) + 1
        self._counts[outcome] += 1

    def unreach(self, key: str, kind: str) -> None:
        """A candidate inside the bound the slice deadline declined to start."""
        self._unreached.append(key)
        self._record(kind, UNREACHED)

    def reach(self, key: str, kind: str, outcome: _CandidateOutcome) -> None:
        """A started candidate's outcome, written on an apply where it is a re-cut."""
        self._record(kind, outcome.outcome)
        if outcome.fetch_reason is not None:
            reason = outcome.fetch_reason
            self._fetch_failed[reason] = self._fetch_failed.get(reason, 0) + 1
        if outcome.recut is None:
            self._skipped[key] = outcome.detail
            return
        self._questions_rederived += len(outcome.questions)
        if self._apply:
            assert self._conn is not None  # refused at construction otherwise
            corpus.upsert_documents(self._conn, [outcome.recut, *outcome.questions])
            # Counted off the written row rather than assumed: a re-cut leaves
            # the class by carrying a cut note or fitting under the cap, and
            # the step's witness compares `remaining` with a re-walk exactly.
            self._left_class += exclusion_reason(outcome.recut) is not None
        self._recuts[key] = outcome.detail

    def result(
        self, scan: RecutScan, *, scope: str, bound: int | None, sliced: int
    ) -> DocumentRecutResult:
        """The ledger over ``scan``'s class, for a slice of ``sliced`` candidates."""
        counts = self._counts
        return DocumentRecutResult(
            applied=self._apply,
            scope=scope,
            cases_seen=scan.cases_seen,
            documents_seen=scan.documents_seen,
            candidates=len(scan.candidates),
            candidates_by_kind=_count_by_kind(scan.candidates),
            excluded=scan.excluded,
            bound=bound,
            attempted=sliced - len(self._unreached),
            unreached=list(self._unreached),
            outcomes_by_kind=_in_kind_order_nested(self._outcomes),
            recut=counts[RECUT],
            unchanged=counts[UNCHANGED],
            pages_changed=counts[PAGES_CHANGED],
            head_changed=counts[HEAD_CHANGED],
            unreadable=counts[UNREADABLE],
            empty_after_recut=counts[EMPTY_AFTER_RECUT],
            fetch_failed=dict(sorted(self._fetch_failed.items())),
            remaining=len(scan.candidates) - self._left_class,
            questions_rederived=self._questions_rederived,
            recuts=dict(sorted(self._recuts.items())),
            skipped=dict(sorted(self._skipped.items())),
        )


def _count_by_kind(candidates: Sequence[RecutCandidate]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for candidate in candidates:
        kind = candidate.document.kind
        counts[kind] = counts.get(kind, 0) + 1
    return {kind: counts[kind] for kind in RECUT_KINDS if kind in counts}


def _in_kind_order_nested(
    outcomes: Mapping[str, Mapping[str, int]],
) -> dict[str, dict[str, int]]:
    """Kinds in :data:`RECUT_KINDS` order, outcomes in :data:`OUTCOMES` order."""
    return {
        kind: {
            outcome: outcomes[kind][outcome] for outcome in OUTCOMES if outcomes[kind].get(outcome)
        }
        for kind in RECUT_KINDS
        if kind in outcomes
    }
