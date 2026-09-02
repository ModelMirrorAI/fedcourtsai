"""The bounded local-OCR recovery pass for scanned petitions.

A SCOTUS petition that reached the corpus as a paper scan has no text layer, so
`pypdf` extracted nothing from it and every cell minted over that case reads an
empty petition — a degradation that persists for as long as the docket keeps
serving the same URL, since both the poller and the Term walker re-fetch a kind
only when its link changes. Nothing in the fetching lanes repairs it. This is
the pass that does, on the terms recorded in *Contract for the recovery pass*
(`docs/live-sources.md`):

- **Population.** Stored **petitions** whose text is empty or whitespace-only
  and whose `pages` is above zero. A zero-page row is a PDF the extractor could
  not open or a derived section, and neither is OCR's to repair; a case holding
  no petition row at all is a fetch gap, repaired in the fetch path or not at
  all. Both stay out.
- **Re-fetch.** By the row's own stored URL — for a petition the single link
  that was fetched, on supremecourt.gov — through the same polite client the
  fetching lanes use, so the pass spends none of the CourtListener budget.
- **OCR.** Page by page through :func:`~fedcourtsai.pipeline.documents.extract_pdf_text`'s
  injected ``ocr_page`` seam, which reads a page off its rendered image *only*
  where that page's own extraction yielded nothing. The extractor applies the
  same character cap and sets the same truncation flag it applies to a fetched
  document, so a recovered petition is bounded exactly like a fetched one.
- **Additive.** Text is written only where the stored row held none, so the
  pass cannot overwrite an extraction, and a write carries the ``ocr_derived``
  marker wherever OCR contributed any of its text: OCR output is derived text,
  lossy in a way a text layer is not, and must never read as a clean
  extraction. (A candidate whose re-fetch now serves a PDF with a text layer is
  recovered without the marker, which is the honest reading of it.)
- **What follows.** A recovered petition re-derives its ``questions-presented``
  row through the same deriver the ingest path uses, since such a row is written
  only where the petition has text; the derived row carries the petition's
  marker, because text cut out of an OCR reading is an OCR reading.

Two binaries, no new Python dependency: ``pdftoppm`` (poppler-utils) renders a
page to a PNG and ``tesseract`` reads it. They are installed by the `run-repair`
OCR step alone, so no scheduled lane grows the dependency — which is why the
seam is injected rather than imported, and why an apply **refuses** where they
are absent rather than silently recovering nothing.
"""

from __future__ import annotations

import logging
import shutil
import sqlite3
import subprocess
import tempfile
import time
from collections.abc import Callable, Iterator, Sequence
from contextlib import AbstractContextManager, contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..supremecourt import SupremeCourtClient
from .documents import (
    KIND_PETITION,
    KIND_QUESTIONS_PRESENTED,
    OcrPage,
    _derived_questions_document,
    extract_pdf_text,
    extract_questions_presented,
)
from .prefetch import prefetch_by_case

logger = logging.getLogger(__name__)

# The two binaries the pass shells out to. Names only — resolved on `PATH` by
# the step that installed them, never a path this repository hard-codes.
RENDER_BINARY = "pdftoppm"
OCR_BINARY = "tesseract"

# Render size, as the rendered page's long side in pixels rather than a
# resolution. On a letter page — what a Court filing is set on — 3300 px is
# exactly 300 dpi, tesseract's own documented floor for 10-12pt body text, and
# renders byte-identically to `-r 300`. Expressed this way because a resolution
# has no ceiling: a page whose MediaBox declares 200 inches rasterizes to a
# multi-gigapixel allocation at 300 dpi, and the renderer buffers it in this
# process. A pixel bound cannot be enlarged by the document.
RENDER_LONG_SIDE_PX = 3300

# Per-page wall-clock ceiling on each binary. A page is seconds of work, so a
# render or a recognition still running after this is a hang rather than a slow
# page, and the pass's whole cost is runner minutes: one wedged page must not
# hold the bound's worth of cases behind it. A timeout costs its own page (the
# extractor's `ocr_page` guard), never the document.
PAGE_TIMEOUT_SECONDS = 120.0

# Per-document wall-clock ceiling on the whole recognition. The page timeout
# alone is not a document bound: a scan whose pages OCR to nothing accumulates
# no characters, so the extractor's cap never fires and a long one can run for
# the length of the step, discarding the slice's other petitions with it. At the
# ~5 s a rendered page costs, this admits a filing well past the longest
# petition and cuts off anything that is no longer reading pages but grinding on
# them. What it has read by then is a partial reading, so it is discarded rather
# than stored, and the candidate stays in the class.
DOCUMENT_BUDGET_SECONDS = 600.0

# The hosts a stored document URL may be re-fetched from. The ingest path takes
# `DocumentUrl` verbatim out of the upstream docket JSON, so a stored URL is
# upstream-controlled text, and this pass is the only thing that GETs one back:
# an unconstrained re-fetch would make the ledger a readable probe of whatever
# the writer job can reach. The Court's own host is the only place a filing
# lives, so the constraint costs nothing real.
DOCUMENT_HOST_SUFFIX = "supremecourt.gov"

# A ceiling on one re-fetched filing. `get_document` reads the whole body into
# memory with no size bound, and this pass then spills it to disk and rasterizes
# it; the largest stored petition is a few megabytes, so anything past this is
# not a filing. Refused as its own reported reason rather than truncated: half a
# PDF is not a document.
MAX_DOCUMENT_BYTES = 64 * 1024 * 1024

# How many of the population's PDFs a dry run re-fetches, to report what the
# writer's own fetch path gets back before an apply spends a slice on it.
DEFAULT_PROBE_SAMPLE = 3


class OcrToolsMissing(RuntimeError):
    """The OCR binaries are not on ``PATH``.

    Raised rather than degraded: neither binary is a Python dependency, so their
    absence is the ordinary state of every environment except the `run-repair`
    OCR step, and a pass that quietly recovered nothing there would report a
    converged population that was never read.
    """


def missing_ocr_binaries() -> list[str]:
    """Which of the two binaries ``PATH`` does not resolve, in fixed order."""
    return [name for name in (RENDER_BINARY, OCR_BINARY) if shutil.which(name) is None]


def require_ocr_binaries() -> None:
    """Refuse unless both binaries are present (see :class:`OcrToolsMissing`)."""
    missing = missing_ocr_binaries()
    if missing:
        raise OcrToolsMissing(
            f"OCR requires {' and '.join(missing)} on PATH; the run-repair OCR step "
            "installs them, and nothing else does"
        )


def _run(argv: list[str], *, stdin: bytes | None, timeout: float) -> bytes | None:
    """One binary invocation; its stdout, or ``None`` on any failure.

    A fixed argument vector and no shell: the only caller-varying value is a
    page number rendered from an ``int``, so nothing here can be made to
    interpolate. Failures are owned rather than raised — the seam's contract is
    that a page costs itself and no more — but they are warned, because a run
    that OCR'd nothing and a run whose renderer was broken read the same in a
    ledger otherwise.
    """
    try:
        # A fixed argument vector and `shell=False` (the default): nothing here
        # reaches a shell, and the binaries are resolved on `PATH` by the step
        # that installed them.
        completed = subprocess.run(
            argv, input=stdin, capture_output=True, timeout=timeout, check=False
        )
    except (OSError, subprocess.SubprocessError) as exc:
        logger.warning("ocr: %s failed: %s", argv[0], exc)
        return None
    if completed.returncode != 0:
        logger.warning(
            "ocr: %s exited %d: %s",
            argv[0],
            completed.returncode,
            completed.stderr.decode("utf-8", "replace").strip()[:200],
        )
        return None
    return completed.stdout


def _render_page(pdf_path: Path, index: int, *, long_side: int, timeout: float) -> bytes | None:
    """Render one page of a PDF to a PNG on stdout, or ``None``.

    ``index`` is the extractor's 0-based page index; ``pdftoppm`` numbers pages
    from 1. The argv **ends at the input path**, with no output root after it:
    that omission is what makes the renderer write the image to stdout instead
    of to a file beside the input, and a ``-`` in that position is taken as a
    filename prefix rather than as stdout — an image written to a file named
    ``-`` and an empty read here.
    """
    page = str(index + 1)
    return _run(
        [
            RENDER_BINARY,
            "-f",
            page,
            "-l",
            page,
            "-scale-to",
            str(long_side),
            "-png",
            "-singlefile",
            str(pdf_path),
        ],
        stdin=None,
        timeout=timeout,
    )


def _ocr_png(png: bytes, *, timeout: float) -> str:
    """The text tesseract reads off one rendered page, or ``""``."""
    out = _run([OCR_BINARY, "stdin", "stdout"], stdin=png, timeout=timeout)
    return "" if out is None else out.decode("utf-8", "replace")


@dataclass
class OcrRun:
    """One document's recognition: the page seam, and whether it ran out of time.

    Two values rather than a bare callable, because the extractor cannot tell
    the caller apart a page OCR read as blank from a page it never reached: both
    reach it as ``""``. ``budget_spent`` is that distinction, and the pass needs
    it — a document whose recognition was cut short has a *partial* reading, and
    storing one as the petition's text would replace a filing that reads as
    empty with a filing that reads as complete and is not. So it is discarded,
    and the case stays in the class.
    """

    page: OcrPage
    budget_spent: bool = False


@contextmanager
def ocr_page_for_pdf(
    data: bytes,
    *,
    long_side: int = RENDER_LONG_SIDE_PX,
    timeout: float = PAGE_TIMEOUT_SECONDS,
    budget: float = DOCUMENT_BUDGET_SECONDS,
    monotonic: Callable[[], float] = time.monotonic,
) -> Iterator[OcrRun]:
    """An :class:`OcrRun` over one PDF's bytes.

    The bytes are spilled to a temporary file once per document rather than per
    page, because the renderer takes a path and a petition runs to hundreds of
    pages; the directory and everything in it are removed on exit whether or not
    the extraction completed.

    ``budget`` is the document's whole share of the run, spent from the first
    page: once it is gone every remaining page reads as nothing and the run says
    so. Cutting one document off is the cheap failure — it stays in the class and
    re-enters a later slice — where letting it run on costs the slice's other
    petitions their writes.

    The binary requirement is owned here, by the one implementation that has it:
    a caller supplying its own seam has no use for them, and the pass's
    pre-flight refusal is a fail-fast copy of this rather than the only guard.
    """
    require_ocr_binaries()
    with tempfile.TemporaryDirectory(prefix="ocr-recovery-") as tmp:
        pdf_path = Path(tmp) / "document.pdf"
        pdf_path.write_bytes(data)
        deadline = monotonic() + budget
        run = OcrRun(page=lambda _index: "")

        def ocr_page(index: int) -> str:
            if monotonic() >= deadline:
                logger.warning("ocr: document budget spent; stopping at page %d", index + 1)
                run.budget_spent = True
                return ""
            png = _render_page(pdf_path, index, long_side=long_side, timeout=timeout)
            if png is None:
                return ""
            return _ocr_png(png, timeout=timeout)

        run.page = ocr_page
        yield run


# The factory the pass calls per document. Injected so the pass's own logic is
# testable with no binaries present — the tests supply a stub — while the one
# effectful implementation stays :func:`ocr_page_for_pdf`.
OcrPageFactory = Callable[[bytes], AbstractContextManager[OcrRun]]


class OcrFetchProbe(BaseModel):
    """What the writer's fetch path got back for one sampled petition URL.

    The dry run's second job. Both planned writer-lane passes over
    supremecourt.gov assume the fetch succeeds, and cell-side reports of 403s
    from that host put the assumption in question; a probe through
    :meth:`~fedcourtsai.supremecourt.SupremeCourtClient.get_document` — the same
    client, headers and retry posture the fetching lanes use — answers it for
    the writer path before an apply spends a slice finding out.
    """

    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(description="The case whose stored petition URL was sampled")
    url: str = Field(description="The stored URL the probe fetched")
    outcome: str = Field(
        description="`served` (bytes came back), `not-served` (upstream 404), "
        "`http-error` (a status the client's retry did not clear), "
        "`transport-error` (no response at all), or `unfetchable-url` (a stored "
        "URL this pass refuses to request — not HTTPS on the Court's own host)"
    )
    status: int | None = Field(
        default=None, description="The HTTP status where one was returned, else null"
    )
    bytes_fetched: int = Field(default=0, ge=0, description="Length of the served body")


class OcrRecoveryResult(BaseModel):
    """What one recovery pass found, and wrote."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the rows or only counted them")
    petitions_seen: int = Field(
        ge=0,
        description="Stored petitions the walk read at all — the denominator "
        "under `candidates`. Zero means the documents could not be read rather "
        "than that the class is empty: a split-mode index with no content store "
        "configured serves every case an empty document list",
    )
    candidates: int = Field(
        ge=0,
        description="Stored petitions whose text is empty or whitespace-only and "
        "whose page count is above zero — the whole recoverable class on this corpus",
    )
    bound: int | None = Field(
        default=None,
        description="The per-dispatch slice size an applied run was bounded to; "
        "null on a dry run, which is unbounded because it writes nothing",
    )
    attempted: int = Field(
        ge=0, description="Candidates this run re-fetched — the slice, never more than `bound`"
    )
    recovered: int = Field(
        ge=0, description="Petitions that came back with text (apply writes these)"
    )
    empty_after_ocr: int = Field(
        ge=0,
        description="Petitions re-fetched and OCR'd that still read empty — an "
        "image OCR could not read; they stay in the class and re-enter the next slice",
    )
    unfetched: dict[str, int] = Field(
        default_factory=dict,
        description="Candidates the re-fetch did not return, reason class -> count",
    )
    remaining: int = Field(
        ge=0,
        description="Candidates the run did not reach, plus those it reached and "
        "could not recover — the backlog the next slice would face",
    )
    questions_rederived: int = Field(
        ge=0,
        description="Questions-presented rows re-derived from a recovered petition "
        "and written beside it",
    )
    recoveries: dict[str, str] = Field(
        default_factory=dict,
        description="case_id -> what was recovered, untruncated: the record of which "
        "stored petitions an applied pass replaced",
    )
    failures: dict[str, str] = Field(
        default_factory=dict, description="case_id -> why this candidate produced no text"
    )
    probes: list[OcrFetchProbe] = Field(
        default_factory=list,
        description="The dry run's fetch sample through the writer's own fetch path",
    )


def _is_scanned_petition(document: corpus.CaseDocument) -> bool:
    """The population predicate, in one place: an empty petition that has pages.

    Whitespace-only counts as empty (it is what the coverage report counts, and
    what provisioning stamps as ``empty_text``); ``pages > 0`` is what separates
    a scan from a PDF the extractor could not open, which is not OCR's to repair.
    """
    return document.kind == KIND_PETITION and not document.text.strip() and document.pages > 0


def fetchable_document_url(url: str) -> bool:
    """Whether a stored URL is one this pass may re-fetch.

    A stored ``CaseDocument.url`` is not a value this repository wrote: the
    ingest path takes ``DocumentUrl`` verbatim out of the upstream docket JSON,
    checking only that it is non-empty. This pass is the only thing that GETs one
    back, from inside the writer job, and reports the status per URL — so an
    unconstrained re-fetch would make the dry-run ledger a readable probe of
    whatever that job can reach, and a `file:` or relative URL would reach the
    client as something other than an HTTP request. HTTPS on the Court's own host
    is where a filing lives; everything else is refused before the request, and
    counted under its own reason so a refused URL reads as a URL problem rather
    than an upstream one.
    """
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    if parts.scheme != "https" or not parts.hostname:
        return False
    host = parts.hostname.lower()
    return host == DOCUMENT_HOST_SUFFIX or host.endswith(f".{DOCUMENT_HOST_SUFFIX}")


@dataclass(frozen=True)
class ScannedPetition:
    """One candidate, with what the pass has to know about its case.

    ``stored_questions`` is the case's stored questions-presented text, read in
    the same walk that found the petition rather than by a second read: the
    re-derivation decides against it, and a decision that needed another
    content-store round trip per case would be paid for in the slice's budget.
    """

    petition: corpus.CaseDocument
    stored_questions: str | None


@dataclass(frozen=True)
class ScannedPetitionScan:
    """What one walk of the corpus saw.

    ``petitions_seen`` is the denominator, and it is here because zero
    candidates has two very different causes: a converged corpus, and a blob
    whose documents this process cannot read at all — a split-mode index with no
    content store configured serves every case an empty document list, which
    would otherwise report as a class of nothing and a clean run. The caller
    refuses on the denominator, not on the class.
    """

    candidates: tuple[ScannedPetition, ...]
    petitions_seen: int


def scanned_petitions(conn: corpus.ReadConnection) -> ScannedPetitionScan:
    """Every stored petition in the recovery class, in ``case_id`` order.

    The population is walked case by case rather than queried, because under the
    corpus-split mode the document text lives in the per-case content store and
    the blob's ``documents`` table holds none of it — a SQL predicate over that
    table would report an empty population against the corpus production reads.
    :func:`~fedcourtsai.corpus.documents_for_case` is the read that routes to
    whichever holds them, and the walk is bounded to the live/historical slice
    for the same reason the questions-presented sweep is: documents reach the
    corpus on that channel only.

    Ordering is the row order (``case_id``), which is what makes a bounded slice
    self-advancing: a recovered petition leaves the class, so the next dispatch's
    slice starts where this one's population ran out.
    """
    case_ids = [row.case_id for row in corpus.iter_rows(conn, court="scotus", live_slice=True)]
    found: list[ScannedPetition] = []
    petitions_seen = 0
    with prefetch_by_case(
        case_ids,
        lambda case_id: corpus.documents_for_case(conn, case_id),
        thread_name_prefix="ocr-recovery",
    ) as fetched:
        for _case_id, documents in fetched:
            by_kind = {document.kind: document for document in documents}
            petition = by_kind.get(KIND_PETITION)
            if petition is None:
                continue
            petitions_seen += 1
            if not _is_scanned_petition(petition):
                continue
            questions = by_kind.get(KIND_QUESTIONS_PRESENTED)
            found.append(
                ScannedPetition(
                    petition=petition,
                    stored_questions=None if questions is None else questions.text,
                )
            )
    return ScannedPetitionScan(candidates=tuple(found), petitions_seen=petitions_seen)


def _probe_sample(candidates: Sequence[ScannedPetition], size: int) -> list[ScannedPetition]:
    """``size`` candidates spread evenly across the class, in class order.

    Spread rather than the head, because the head is the same three cases every
    dispatch: a sample that never moves reports on three fixed URLs however many
    dry runs are read, and the question the probe answers is about the class.
    """
    if size <= 0 or not candidates:
        return []
    if size >= len(candidates):
        return list(candidates)
    stride = len(candidates) / size
    return [candidates[int(index * stride)] for index in range(size)]


def probe_document_fetch(
    client: SupremeCourtClient, candidates: Sequence[ScannedPetition], *, sample: int
) -> list[OcrFetchProbe]:
    """Re-fetch a spread sample of the class and report what came back.

    Reads nothing out of the bodies and writes nothing anywhere: the point is the
    status, not the PDF. Every failure class is *reported* rather than raised —
    a probe that aborted the dry run on the first 403 would answer the question
    with one data point.
    """
    probes: list[OcrFetchProbe] = []
    for candidate in _probe_sample(candidates, sample):
        document = candidate.petition
        if not fetchable_document_url(document.url):
            probes.append(
                OcrFetchProbe(case_id=document.case_id, url=document.url, outcome="unfetchable-url")
            )
            continue
        try:
            data = client.get_document(document.url)
        except httpx.HTTPStatusError as exc:
            probes.append(
                OcrFetchProbe(
                    case_id=document.case_id,
                    url=document.url,
                    outcome="http-error",
                    status=exc.response.status_code,
                )
            )
            continue
        except httpx.HTTPError as exc:
            logger.warning("ocr: probe transport failure for %s: %s", document.case_id, exc)
            probes.append(
                OcrFetchProbe(case_id=document.case_id, url=document.url, outcome="transport-error")
            )
            continue
        if data is None:
            probes.append(
                OcrFetchProbe(
                    case_id=document.case_id, url=document.url, outcome="not-served", status=404
                )
            )
            continue
        probes.append(
            OcrFetchProbe(
                case_id=document.case_id,
                url=document.url,
                outcome="served",
                status=200,
                bytes_fetched=len(data),
            )
        )
    return probes


def _refetch_document(
    client: SupremeCourtClient, document: corpus.CaseDocument
) -> tuple[bytes | None, str | None]:
    """Re-fetch one stored document; its bytes, or ``None`` and why not.

    Every way this can fail to produce a usable body is a *reported reason*
    rather than a raise, because a slice must cost the maintainer one candidate
    when a filing is unreachable, not the whole dispatch. The refusals that
    precede the request are as much a reason as the ones the network gives:
    a stored URL this pass will not GET (:func:`fetchable_document_url`), and a
    body past the document ceiling, which is not a filing.
    """
    if not fetchable_document_url(document.url):
        logger.warning("ocr: refusing to fetch %s for %s", document.url, document.case_id)
        return None, "unfetchable-url"
    try:
        data = client.get_document(document.url)
    except httpx.HTTPStatusError as exc:
        return None, f"http-{exc.response.status_code}"
    except httpx.HTTPError as exc:
        logger.warning("ocr: fetch failed for %s: %s", document.case_id, exc)
        return None, "transport-error"
    if data is None:
        return None, "not-served"
    if len(data) > MAX_DOCUMENT_BYTES:
        logger.warning(
            "ocr: %s served %d bytes, past the %d-byte document ceiling",
            document.case_id,
            len(data),
            MAX_DOCUMENT_BYTES,
        )
        return None, "oversized"
    return data, None


def recover_scanned_petitions(
    conn: sqlite3.Connection,
    *,
    client: SupremeCourtClient,
    apply: bool,
    char_cap: int,
    today: date,
    max_cases: int | None = None,
    probe_sample: int = DEFAULT_PROBE_SAMPLE,
    ocr_page_factory: OcrPageFactory = ocr_page_for_pdf,
) -> OcrRecoveryResult:
    """Re-read the scanned petitions off their page images; write what comes back.

    Dry run unless ``apply``, and the two runs do deliberately different work.
    The **dry run** enumerates the class, OCRs nothing and writes nothing, and
    re-fetches a ``probe_sample`` of the population through the writer's own
    fetch path so the ledger a maintainer reads before approving a slice states
    what that path actually gets back from supremecourt.gov
    (:class:`OcrFetchProbe`). The **apply** takes the first ``max_cases``
    candidates — required, and the slice size rather than a refusal threshold,
    because each case costs a fetch and a page-by-page recognition and the whole
    cost is runner minutes — re-fetches each by its stored URL, walks its pages
    through the extractor with the OCR seam supplied, and upserts the petitions
    that came back with text, each carrying ``ocr_derived``, together with the
    questions-presented row re-derived from the recovered text.

    Written per case rather than in one batch at the end, because the step that
    runs this has a wall-clock cap: a batched write turns a cap hit into a slice
    that recovered a dozen filings and stored none of them. That banks the work
    under the corpus split, where the per-case content-store write is itself the
    durable one; against a self-contained blob the durable step is the pointer
    push the workflow makes after the pass, and a cap hit loses the slice however
    it was written.

    Additive on the petition. A candidate whose re-fetch fails, or whose pages
    OCR to nothing, is *counted and named* and nothing is written for it: the
    stored row keeps the empty text it had, stays in the class, and re-enters the
    next slice — which is also the pass's one non-advancing case, and why the
    ledger reports ``empty_after_ocr`` apart from the candidates the slice never
    reached — as does every candidate the re-fetch did not return, and every one
    whose recognition ran out of time, which is why "self-advancing" means the
    recovered ones leave rather than that the next dispatch starts further on:
    what failed sits at the head of the class and is retried first.
    The derived questions-presented row is additive under one more
    guard: the deriver stores the empty row where a heading has nothing usable
    under it, and a *stored* non-empty row is never replaced by that reading —
    the convergence sweep's refusal in a stricter form, at any length rather than
    that sweep's character floor. A question stored beside a scanned petition
    came from a superseded filing, and emptying it is as likely to be this pass
    misjudging as a bad row; the sweep's whole subject is the derived row, while
    this pass is here for the petition and has no business deciding that one.

    The recovered row's ``fetched_at`` moves to ``today``, unlike the stored-text
    convergence sweeps, because a fetch and a re-read did happen. That is
    visible downstream in one place: provisioning places a document by its entry
    date and falls back to ``fetched_at`` where the entry date is missing, so
    such a petition can fall outside a replay cell's as-of window it previously
    sat inside. The direction is the conservative one — a cell sees less, never
    more — which is why the honest date is kept.
    """
    if apply and max_cases is None:
        raise ValueError("an apply must carry its slice bound")
    scan = scanned_petitions(conn)
    candidates = scan.candidates
    if not apply:
        return OcrRecoveryResult(
            applied=False,
            petitions_seen=scan.petitions_seen,
            candidates=len(candidates),
            # A dry run is unbounded whatever it was handed: it writes nothing,
            # and reporting a bound it did not spend would read as a slice that
            # attempted none of it.
            bound=None,
            attempted=0,
            recovered=0,
            empty_after_ocr=0,
            remaining=len(candidates),
            questions_rederived=0,
            probes=probe_document_fetch(client, candidates, sample=probe_sample),
        )

    assert max_cases is not None  # narrowed by the refusal above
    slice_ = candidates[:max_cases]
    if slice_ and ocr_page_factory is ocr_page_for_pdf:
        # Fail fast, and only where both conditions hold: there is work to do (a
        # converged population owes no dependency), and the seam actually in use
        # is the one that shells out (an injected seam has no binaries to want).
        # Ahead of every fetch and every write, so the refusal costs no request —
        # the factory itself refuses too, one document later.
        require_ocr_binaries()
    recoveries: dict[str, str] = {}
    failures: dict[str, str] = {}
    unfetched: dict[str, int] = {}
    empty_after_ocr = 0
    questions_rederived = 0

    def lose(case_id: str, reason: str) -> None:
        failures[case_id] = reason
        unfetched[reason] = unfetched.get(reason, 0) + 1

    for candidate in slice_:
        document = candidate.petition
        data, refused = _refetch_document(client, document)
        if data is None:
            lose(document.case_id, refused or "not-served")
            continue
        with ocr_page_factory(data) as run:
            extracted = extract_pdf_text(data, char_cap=char_cap, ocr_page=run.page)
        if run.budget_spent:
            # A partial reading, and nothing downstream would say so: `truncated`
            # is the character cap's flag, not this one's, so a filing cut off
            # at page 90 would read as the whole petition. The candidate keeps
            # its empty text and stays in the class.
            lose(document.case_id, "budget-exhausted")
            continue
        if not extracted.text.strip():
            # Re-fetched and read, and the images yielded nothing: an unreadable
            # scan, not a fetch gap. Named apart so a slice that cleared its
            # bound without advancing the class says so.
            empty_after_ocr += 1
            failures[document.case_id] = "empty-after-ocr"
            continue
        petition = document.model_copy(
            update={
                "text": extracted.text,
                "pages": extracted.pages,
                "truncated": extracted.truncated,
                "ocr_derived": extracted.ocr_derived,
                "fetched_at": today,
            }
        )
        updates = [petition]
        questions = extract_questions_presented(petition.text)
        if questions is not None and (questions or not (candidate.stored_questions or "").strip()):
            # The ingest path's rule — no heading stores no row, a heading with
            # nothing usable under it stores the honest empty row — with the
            # convergence sweep's refusal on top: an empty derivation never
            # replaces a stored question.
            updates.append(_derived_questions_document(petition, questions, fetched_at=today))
            questions_rederived += 1
        corpus.upsert_documents(conn, updates)
        recoveries[document.case_id] = (
            f"pages={extracted.pages} chars={len(extracted.text)} "
            f"truncated={str(extracted.truncated).lower()} "
            f"ocr_derived={str(extracted.ocr_derived).lower()}"
        )
    return OcrRecoveryResult(
        applied=True,
        petitions_seen=scan.petitions_seen,
        candidates=len(candidates),
        bound=max_cases,
        attempted=len(slice_),
        recovered=len(recoveries),
        empty_after_ocr=empty_after_ocr,
        unfetched=dict(sorted(unfetched.items())),
        remaining=len(candidates) - len(recoveries),
        questions_rederived=questions_rederived,
        recoveries=dict(sorted(recoveries.items())),
        failures=dict(sorted(failures.items())),
    )
