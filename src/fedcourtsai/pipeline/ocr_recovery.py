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
  pass cannot overwrite an extraction, and every write carries the
  ``ocr_derived`` marker: OCR output is derived text, lossy in a way a text
  layer is not, and must never read as a clean extraction.
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
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import date
from pathlib import Path

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..supremecourt import SupremeCourtClient
from .documents import (
    KIND_PETITION,
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

# Render resolution. 300 dpi is tesseract's own documented floor for body text
# at 10-12pt, which is what a printed brief is set in; below it the recognition
# rate falls off a cliff, and above it the render cost climbs for nothing.
RENDER_DPI = 300

# Per-page wall-clock ceiling on each binary. A page is seconds of work, so a
# render or a recognition still running after this is a hang rather than a slow
# page, and the pass's whole cost is runner minutes: one wedged page must not
# hold the bound's worth of cases behind it. A timeout costs its own page (the
# extractor's `ocr_page` guard), never the document.
PAGE_TIMEOUT_SECONDS = 120.0

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


def _render_page(pdf_path: Path, index: int, *, dpi: int, timeout: float) -> bytes | None:
    """Render one page of a PDF to a PNG on stdout, or ``None``.

    ``index`` is the extractor's 0-based page index; ``pdftoppm`` numbers pages
    from 1, and ``-singlefile`` with ``-`` as the output prefix is what makes it
    write the image to stdout rather than to a numbered file beside the input.
    """
    page = str(index + 1)
    return _run(
        [
            RENDER_BINARY,
            "-f",
            page,
            "-l",
            page,
            "-r",
            str(dpi),
            "-png",
            "-singlefile",
            str(pdf_path),
            "-",
        ],
        stdin=None,
        timeout=timeout,
    )


def _ocr_png(png: bytes, *, timeout: float) -> str:
    """The text tesseract reads off one rendered page, or ``""``."""
    out = _run([OCR_BINARY, "stdin", "stdout"], stdin=png, timeout=timeout)
    return "" if out is None else out.decode("utf-8", "replace")


@contextmanager
def ocr_page_for_pdf(
    data: bytes, *, dpi: int = RENDER_DPI, timeout: float = PAGE_TIMEOUT_SECONDS
) -> Iterator[OcrPage]:
    """An :data:`~fedcourtsai.pipeline.documents.OcrPage` over one PDF's bytes.

    The bytes are spilled to a temporary file once per document rather than per
    page, because the renderer takes a path and a petition runs to hundreds of
    pages; the directory and everything in it are removed on exit whether or not
    the extraction completed.

    The binary requirement is owned here, by the one implementation that has it:
    a caller supplying its own seam has no use for them, and the pass's
    pre-flight refusal is a fail-fast copy of this rather than the only guard.
    """
    require_ocr_binaries()
    with tempfile.TemporaryDirectory(prefix="ocr-recovery-") as tmp:
        pdf_path = Path(tmp) / "document.pdf"
        pdf_path.write_bytes(data)

        def ocr_page(index: int) -> str:
            png = _render_page(pdf_path, index, dpi=dpi, timeout=timeout)
            if png is None:
                return ""
            return _ocr_png(png, timeout=timeout)

        yield ocr_page


# The factory the pass calls per document. Injected so the pass's own logic is
# testable with no binaries present — the tests supply a stub — while the one
# effectful implementation stays :func:`ocr_page_for_pdf`.
OcrPageFactory = Callable[[bytes], AbstractContextManager[OcrPage]]


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
        "`http-error` (a status the client's retry did not clear), or "
        "`transport-error` (no response at all)"
    )
    status: int | None = Field(
        default=None, description="The HTTP status where one was returned, else null"
    )
    bytes_fetched: int = Field(default=0, ge=0, description="Length of the served body")


class OcrRecoveryResult(BaseModel):
    """What one recovery pass found, and wrote."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the rows or only counted them")
    candidates: int = Field(
        ge=0,
        description="Stored petitions whose text is empty or whitespace-only and "
        "whose page count is above zero — the whole recoverable class on this corpus",
    )
    bound: int | None = Field(
        default=None,
        description="The per-dispatch slice size the run was bounded to, or null "
        "where the run took none (dry runs are unbounded: they write nothing)",
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


def scanned_petitions(conn: corpus.ReadConnection) -> list[corpus.CaseDocument]:
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
    found: list[corpus.CaseDocument] = []
    with prefetch_by_case(
        case_ids,
        lambda case_id: corpus.documents_for_case(conn, case_id),
        thread_name_prefix="ocr-recovery",
    ) as fetched:
        for _case_id, documents in fetched:
            found.extend(document for document in documents if _is_scanned_petition(document))
    return found


def probe_document_fetch(
    client: SupremeCourtClient, documents: list[corpus.CaseDocument], *, sample: int
) -> list[OcrFetchProbe]:
    """Re-fetch the first ``sample`` candidates and report what came back.

    Reads nothing out of the bodies and writes nothing anywhere: the point is the
    status, not the PDF. Every failure class is *reported* rather than raised —
    a probe that aborted the dry run on the first 403 would answer the question
    with one data point.
    """
    probes: list[OcrFetchProbe] = []
    for document in documents[: max(sample, 0)]:
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

    Additive in both directions. A candidate whose re-fetch fails, or whose
    pages OCR to nothing, is *counted and named* and nothing is written for it:
    the stored row keeps the empty text it had, stays in the class, and re-enters
    the next slice — which is also the pass's one non-advancing case, and why the
    ledger reports ``empty_after_ocr`` apart from the candidates the slice never
    reached.
    """
    if apply and max_cases is None:
        raise ValueError("an apply must carry its slice bound")
    candidates = scanned_petitions(conn)
    if not apply:
        probes = probe_document_fetch(client, candidates, sample=probe_sample)
        return OcrRecoveryResult(
            applied=False,
            candidates=len(candidates),
            bound=max_cases,
            attempted=0,
            recovered=0,
            empty_after_ocr=0,
            remaining=len(candidates),
            questions_rederived=0,
            probes=probes,
        )

    assert max_cases is not None  # narrowed by the refusal above
    slice_ = candidates[:max_cases]
    if slice_ and ocr_page_factory is ocr_page_for_pdf:
        # Fail fast, and only where all three conditions hold: there is work to
        # do (a converged population owes no dependency), and the seam actually
        # in use is the one that shells out (an injected seam has no binaries to
        # want). Ahead of every fetch and every write, so the refusal costs no
        # request — the factory itself refuses too, one document later.
        require_ocr_binaries()
    updates: list[corpus.CaseDocument] = []
    recoveries: dict[str, str] = {}
    failures: dict[str, str] = {}
    unfetched: dict[str, int] = {}
    empty_after_ocr = 0
    questions_rederived = 0

    def lose(case_id: str, reason: str) -> None:
        failures[case_id] = reason
        unfetched[reason] = unfetched.get(reason, 0) + 1

    for document in slice_:
        try:
            data = client.get_document(document.url)
        except httpx.HTTPStatusError as exc:
            lose(document.case_id, f"http-{exc.response.status_code}")
            continue
        except httpx.HTTPError as exc:
            logger.warning("ocr: fetch failed for %s: %s", document.case_id, exc)
            lose(document.case_id, "transport-error")
            continue
        if data is None:
            lose(document.case_id, "not-served")
            continue
        with ocr_page_factory(data) as ocr_page:
            extracted = extract_pdf_text(data, char_cap=char_cap, ocr_page=ocr_page)
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
                # A fetch and a re-read did happen here, unlike the stored-text
                # convergence sweeps, so the row's fetch date is today's.
                "fetched_at": today,
            }
        )
        updates.append(petition)
        recoveries[document.case_id] = (
            f"pages={extracted.pages} chars={len(extracted.text)} "
            f"truncated={str(extracted.truncated).lower()} "
            f"ocr_derived={str(extracted.ocr_derived).lower()}"
        )
        questions = extract_questions_presented(petition.text)
        if questions is not None:
            # The ingest path's own rule: a heading with nothing usable under it
            # stores the honest empty row, and no heading at all stores none.
            updates.append(_derived_questions_document(petition, questions, fetched_at=today))
            questions_rederived += 1
    if updates:
        corpus.upsert_documents(conn, updates)
    return OcrRecoveryResult(
        applied=True,
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
