"""The bounded local-OCR recovery pass for scanned petitions.

No tesseract runs here. The pass takes its OCR call as an injected seam, so its
logic — the population predicate, the slice, the additive write, the marker, the
ledger — is exercised against a stub that says what a page "read"; the
subprocess wrapper that shells out to the real binaries is exercised separately,
against fake binaries laid on ``PATH``. Both halves are the point: an OCR test
that needed OCR installed would be a test the gate cannot run.
"""

from __future__ import annotations

import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, supremecourt
from fedcourtsai.cli import app
from fedcourtsai.pipeline.documents import (
    KIND_BRIEF_IN_OPPOSITION,
    KIND_PETITION,
    KIND_QUESTIONS_PRESENTED,
    OcrPage,
)
from fedcourtsai.pipeline.ocr_recovery import (
    MAX_DOCUMENT_BYTES,
    OcrPageFactory,
    OcrToolsMissing,
    ScannedPetition,
    fetchable_document_url,
    missing_ocr_binaries,
    ocr_page_for_pdf,
    recover_scanned_petitions,
    scanned_petitions,
)
from fedcourtsai.supremecourt import SupremeCourtClient

runner = CliRunner()

_TODAY = date(2026, 9, 1)

# What the stub OCR "reads" off a page image: a petition's front matter, so the
# recovered text also exercises the questions-presented re-derivation.
_OCR_TEXT = (
    "QUESTION PRESENTED\n"
    "Whether the court of appeals erred in holding that the statute reaches "
    "conduct wholly outside the United States.\n"
    "PARTIES TO THE PROCEEDING\nAcme Corp."
)


def _pdf_pages(texts: list[str]) -> bytes:
    """A minimal PDF whose i-th page draws ``texts[i]`` (no parens).

    An empty string leaves that page an empty content stream — what a scanned
    page looks like to the extractor, and the only kind the OCR guard fires on.
    """
    font = 3 + 2 * len(texts)
    kids = " ".join(f"{3 + 2 * page} 0 R" for page in range(len(texts)))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {len(texts)} >>".encode(),
    ]
    for page, text in enumerate(texts):
        stream = f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode() if text else b""
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {4 + 2 * page} 0 R ".encode()
            + f"/Resources << /Font << /F1 {font} 0 R >> >> >>".encode()
        )
        objects.append(
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"
        )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    start = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF".encode()
    )
    return bytes(out)


def _document(
    case_id: str,
    kind: str = KIND_PETITION,
    *,
    text: str = "",
    pages: int = 12,
    url: str | None = None,
) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=kind,
        url=url or f"https://www.supremecourt.gov/{case_id.rsplit('/', 1)[-1]}.pdf",
        entry_date="Jun 01 2026",
        fetched_at=date(2026, 6, 2),
        pages=pages,
        text=text,
    )


def _seed(corpus_root: Path, documents: list[corpus.CaseDocument]) -> Path:
    """A corpus holding ``documents``, every owning case in the live slice."""
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=case_id,
                    court="scotus",
                    docket_number=f"25-{index}",
                    # `last_live_polled` is live-slice membership, and documents
                    # reach the corpus on that channel only.
                    last_live_polled=date(2026, 6, 2),
                )
                for index, case_id in enumerate(sorted({d.case_id for d in documents}), start=1)
            ],
        )
        corpus.upsert_documents(conn, documents)
    return db


def _client(
    served: dict[str, bytes], *, status: dict[str, int] | None = None
) -> SupremeCourtClient:
    """The real client over a mock transport — same headers, same retry posture."""
    codes = status or {}

    def handler(request: httpx.Request) -> httpx.Response:
        key = str(request.url)
        if key in codes:
            return httpx.Response(codes[key], content=b"")
        if key in served:
            return httpx.Response(200, content=served[key])
        return httpx.Response(404)

    inner = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
    )
    return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _s: None)


def _stub_ocr(text: str = _OCR_TEXT) -> OcrPageFactory:
    """An OCR page factory that reads ``text`` off every image it is handed."""

    @contextmanager
    def factory(_data: bytes) -> Iterator[OcrPage]:
        yield lambda _index: text

    return factory


def _documents(db: Path, case_id: str) -> dict[str, corpus.CaseDocument]:
    with corpus.connect(db) as conn:
        return {d.kind: d for d in corpus.documents_for_case(conn, case_id)}


# --- population ------------------------------------------------------------


def test_the_population_is_empty_petitions_that_have_pages(tmp_path: Path) -> None:
    """Empty-with-pages is in; text, no pages, and other kinds are out.

    Each exclusion has its own reason and they are not interchangeable: a
    petition that extracted is not degraded, a zero-page row is a PDF that would
    not open (not OCR's to repair), and the combined opposition row is out
    structurally — text recovered there is discarded the next time a
    co-respondent's brief joins its idempotency key.
    """
    db = _seed(
        tmp_path / "corpus",
        [
            _document("scotus/1"),  # the class: empty, 12 pages
            _document("scotus/2", text="The petition argues X."),  # extracted
            _document("scotus/3", pages=0),  # would not open
            _document("scotus/4", kind=KIND_BRIEF_IN_OPPOSITION),  # not a petition
            _document("scotus/5", text="   \n\t "),  # whitespace-only is empty
            _document("scotus/6", kind=KIND_QUESTIONS_PRESENTED, pages=0),  # derived section
        ],
    )
    with corpus.connect(db) as conn:
        scan = scanned_petitions(conn)
    assert [c.petition.case_id for c in scan.candidates] == ["scotus/1", "scotus/5"]
    # The denominator counts every stored petition, in or out of the class: it
    # is what separates a converged corpus from one whose documents cannot be
    # read at all.
    # Four of the six cases hold a petition row at all (scotus/4 holds only an
    # opposition, scotus/6 only a derived section), and all four count toward
    # the denominator whether or not they are in the class.
    assert scan.petitions_seen == 4


def test_the_population_is_ordered_so_a_slice_advances(tmp_path: Path) -> None:
    """`case_id` order, which is what makes successive dispatches disjoint."""
    db = _seed(tmp_path / "corpus", [_document(f"scotus/{n}") for n in (3, 1, 2)])
    with corpus.connect(db) as conn:
        found = scanned_petitions(conn).candidates
    assert [c.petition.case_id for c in found] == ["scotus/1", "scotus/2", "scotus/3"]


# --- dry run ---------------------------------------------------------------


def test_the_dry_run_probes_the_fetch_path_and_writes_nothing(tmp_path: Path) -> None:
    """The dry run's second reading: what the writer's own fetch path gets back.

    Both planned writer-lane passes over supremecourt.gov assume the fetch
    succeeds, so the ledger a maintainer reads before approving a slice states
    the status of a sample re-fetched through the same client, headers and retry
    posture the fetching lanes use — every class reported rather than raised, or
    the question would be answered by one data point.
    """
    documents = [_document(f"scotus/{n}") for n in (1, 2, 3, 4)]
    db = _seed(tmp_path / "corpus", documents)
    served = {documents[0].url: _pdf_pages([""])}
    # The second 403s (the class that would kill an apply), the third is a 404.
    with _client(served, status={documents[1].url: 403}) as client, corpus.connect(db) as conn:
        result = recover_scanned_petitions(
            conn,
            client=client,
            apply=False,
            char_cap=10_000,
            today=_TODAY,
            ocr_page_factory=_stub_ocr(),
        )
    assert result.applied is False
    assert result.candidates == 4 and result.remaining == 4 and result.attempted == 0
    # min(3, population) — a sample, not the class.
    assert [(p.case_id, p.outcome, p.status) for p in result.probes] == [
        ("scotus/1", "served", 200),
        ("scotus/2", "http-error", 403),
        ("scotus/3", "not-served", 404),
    ]
    assert result.probes[0].bytes_fetched == len(served[documents[0].url])
    # Nothing OCR'd, nothing written: the stored rows are as they were.
    assert _documents(db, "scotus/1")[KIND_PETITION].text == ""
    assert result.recoveries == {} and result.failures == {}


def test_the_dry_run_probe_can_be_turned_off(tmp_path: Path) -> None:
    """`probe_sample=0` fetches nothing — the counting-only read an apply's
    witness needs, which must not re-fetch what was just fetched."""
    db = _seed(tmp_path / "corpus", [_document("scotus/1")])
    with _client({}) as client, corpus.connect(db) as conn:
        result = recover_scanned_petitions(
            conn, client=client, apply=False, char_cap=10_000, today=_TODAY, probe_sample=0
        )
    assert result.probes == [] and result.candidates == 1


# --- apply -----------------------------------------------------------------


def test_the_apply_recovers_marks_and_rederives(tmp_path: Path) -> None:
    """The whole write, in one pass: text, marker, and the derived row beside it."""
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    with (
        _client({petition.url: _pdf_pages(["", ""])}) as client,
        corpus.connect(db) as conn,
    ):
        result = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr(),
        )
    assert result.applied and result.recovered == 1 and result.remaining == 0
    assert result.questions_rederived == 1
    assert "scotus/1" in result.recoveries and result.failures == {}

    stored = _documents(db, "scotus/1")
    recovered = stored[KIND_PETITION]
    assert _OCR_TEXT in recovered.text
    # The marker is the point: OCR output must never read as a clean extraction.
    assert recovered.ocr_derived is True
    assert recovered.truncated is False
    # A fetch and a re-read did happen, unlike the stored-text convergence
    # sweeps, so the row's fetch date moves.
    assert recovered.fetched_at == _TODAY
    assert recovered.url == petition.url  # the row keeps its identity

    questions = stored[KIND_QUESTIONS_PRESENTED]
    assert "wholly outside the United States" in questions.text
    # Text cut out of an OCR reading is an OCR reading.
    assert questions.ocr_derived is True


def test_the_apply_carries_the_truncation_flag_from_the_cap(tmp_path: Path) -> None:
    """The recovered document is bounded exactly like a fetched one.

    Same extractor, so the same character cap and the same flag: a maintainer
    reading a recovered petition is told it was cut, by the code that cut it.
    """
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    with (
        _client({petition.url: _pdf_pages(["", ""])}) as client,
        corpus.connect(db) as conn,
    ):
        result = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=50,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr("y" * 200),
        )
    assert result.recovered == 1
    recovered = _documents(db, "scotus/1")[KIND_PETITION]
    assert recovered.truncated is True and len(recovered.text) == 50


def test_the_apply_is_additive_and_never_overwrites_an_extraction(tmp_path: Path) -> None:
    """A petition that extracted is not in the class, so no OCR reaches it."""
    extracted = _document("scotus/2", text="The petition argues X.")
    db = _seed(tmp_path / "corpus", [_document("scotus/1"), extracted])
    with (
        _client({_document("scotus/1").url: _pdf_pages([""])}) as client,
        corpus.connect(db) as conn,
    ):
        recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr(),
        )
    kept = _documents(db, "scotus/2")[KIND_PETITION]
    assert kept.text == "The petition argues X." and kept.ocr_derived is False


def test_the_apply_only_ocrs_a_page_that_extracted_nothing(tmp_path: Path) -> None:
    """The per-page guard: a page with a text layer keeps its own reading.

    The population is documents that extracted to nothing at all, so this only
    bites on a mostly-scanned filing carrying one digital page — but that is
    exactly where a lossier reading must not win.
    """
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    with (
        _client({petition.url: _pdf_pages(["Digital page text", ""])}) as client,
        corpus.connect(db) as conn,
    ):
        recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr("OCR read this instead"),
        )
    text = _documents(db, "scotus/1")[KIND_PETITION].text
    assert "Digital page text" in text and "OCR read this instead" in text


def test_the_slice_bounds_the_run_and_reports_the_backlog(tmp_path: Path) -> None:
    """The bound is a slice size, not a refusal threshold.

    Each case costs a fetch and a page-by-page recognition and runner minutes
    are the whole cost, so a backlog clears across dispatches — and the slice is
    self-advancing, because a recovered petition leaves the class.
    """
    documents = [_document(f"scotus/{n}") for n in (1, 2, 3)]
    db = _seed(tmp_path / "corpus", documents)
    served = {d.url: _pdf_pages([""]) for d in documents}
    with _client(served) as client, corpus.connect(db) as conn:
        first = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=2,
            ocr_page_factory=_stub_ocr(),
        )
    assert first.attempted == 2 and first.recovered == 2 and first.remaining == 1
    assert sorted(first.recoveries) == ["scotus/1", "scotus/2"]
    with _client(served) as client, corpus.connect(db) as conn:
        second = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=2,
            ocr_page_factory=_stub_ocr(),
        )
    assert second.candidates == 1 and second.recovered == 1 and second.remaining == 0


def test_an_apply_without_its_bound_is_refused(tmp_path: Path) -> None:
    """An unbounded apply is a refusal, not a full-population job."""
    db = _seed(tmp_path / "corpus", [_document("scotus/1")])
    with (
        _client({}) as client,
        corpus.connect(db) as conn,
        pytest.raises(ValueError, match="slice bound"),
    ):
        recover_scanned_petitions(conn, client=client, apply=True, char_cap=10_000, today=_TODAY)


def test_a_fetch_failure_writes_nothing_and_is_named(tmp_path: Path) -> None:
    """Every candidate the re-fetch did not return is counted and named.

    The stored row keeps the empty text it had and stays in the class, which is
    what makes a 403'd upstream read as a backlog rather than a converged one.
    """
    documents = [_document(f"scotus/{n}") for n in (1, 2)]
    db = _seed(tmp_path / "corpus", documents)
    with (
        _client({}, status={documents[0].url: 403}) as client,
        corpus.connect(db) as conn,
    ):
        result = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr(),
        )
    assert result.recovered == 0 and result.remaining == 2
    assert result.failures == {"scotus/1": "http-403", "scotus/2": "not-served"}
    assert result.unfetched == {"http-403": 1, "not-served": 1}
    assert _documents(db, "scotus/1")[KIND_PETITION].text == ""


def test_a_scan_ocr_cannot_read_stays_in_the_class(tmp_path: Path) -> None:
    """Re-fetched and read, and the images yielded nothing — the one
    non-advancing case, named apart so a cleared slice that did not shrink the
    class says so."""
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    with (
        _client({petition.url: _pdf_pages([""])}) as client,
        corpus.connect(db) as conn,
    ):
        result = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr("   "),
        )
    assert result.empty_after_ocr == 1 and result.recovered == 0 and result.remaining == 1
    assert result.failures == {"scotus/1": "empty-after-ocr"}
    assert _documents(db, "scotus/1")[KIND_PETITION].ocr_derived is False


def test_an_apply_with_work_refuses_where_the_binaries_are_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Neither binary is a Python dependency, so their absence is a refusal.

    Checked only where there is work — a converged population owes nothing — and
    ahead of every fetch and every write, so the refusal costs no request.
    """
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    db = _seed(tmp_path / "corpus", [_document("scotus/1")])
    with (
        _client({}) as client,
        corpus.connect(db) as conn,
        pytest.raises(OcrToolsMissing, match="pdftoppm and tesseract"),
    ):
        recover_scanned_petitions(
            conn, client=client, apply=True, char_cap=10_000, today=_TODAY, max_cases=5
        )


def test_a_converged_population_needs_no_binaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    db = _seed(tmp_path / "corpus", [_document("scotus/1", text="extracted")])
    with _client({}) as client, corpus.connect(db) as conn:
        result = recover_scanned_petitions(
            conn, client=client, apply=True, char_cap=10_000, today=_TODAY, max_cases=5
        )
    assert result.candidates == 0 and result.recovered == 0


def test_a_stored_url_off_the_courts_host_is_refused_before_the_request(tmp_path: Path) -> None:
    """A stored URL is upstream text, and this pass is the only thing that GETs one.

    The ingest path takes `DocumentUrl` verbatim out of the docket JSON, so an
    unconstrained re-fetch would make the ledger a readable probe of whatever the
    writer job can reach — and a relative or `file:` URL would reach the client
    as something other than an HTTP request. Refused before the request, under
    its own reason, so it reads as a URL problem rather than an upstream one.
    """
    for url in (
        "http://www.supremecourt.gov/x.pdf",  # not HTTPS
        "https://evil.example/x.pdf",
        "https://supremecourt.gov.evil.example/x.pdf",  # a suffix, not the host
        "file:///etc/passwd",
        "/DocketPDF/x.pdf",  # relative: not a request at all
    ):
        assert fetchable_document_url(url) is False, url
    for url in (
        "https://www.supremecourt.gov/DocketPDF/23/23-790/1/x.pdf",
        "https://supremecourt.gov/x.pdf",
    ):
        assert fetchable_document_url(url) is True, url

    petition = _document("scotus/1", url="https://evil.example/x.pdf")
    db = _seed(tmp_path / "corpus", [petition])
    requested: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        return httpx.Response(200, content=_pdf_pages([""]))

    inner = httpx.Client(transport=httpx.MockTransport(handler))
    with (
        SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _s: None) as client,
        corpus.connect(db) as conn,
    ):
        dry = recover_scanned_petitions(
            conn, client=client, apply=False, char_cap=10_000, today=_TODAY
        )
        applied = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr(),
        )
    assert requested == []  # neither mode asked for it
    assert [entry.outcome for entry in dry.probes] == ["unfetchable-url"]
    assert applied.failures == {"scotus/1": "unfetchable-url"}
    assert _documents(db, "scotus/1")[KIND_PETITION].text == ""


def test_an_oversized_body_is_refused_rather_than_rasterized(tmp_path: Path) -> None:
    """A body past the ceiling is not a filing.

    `get_document` reads a whole response into memory with no size bound, and
    this pass then spills it to disk and rasterizes it, so the ceiling is where
    an anomalous body stops costing anything but its own candidate.
    """
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    oversize = b"%PDF-1.4" + b"0" * (MAX_DOCUMENT_BYTES + 1)
    with _client({petition.url: oversize}) as client, corpus.connect(db) as conn:
        result = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr(),
        )
    assert result.failures == {"scotus/1": "oversized"} and result.recovered == 0


def test_a_transport_failure_costs_its_candidate_in_both_modes(tmp_path: Path) -> None:
    """No response at all — the class the status-code branches cannot report."""
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route", request=request)

    inner = httpx.Client(transport=httpx.MockTransport(handler))
    with (
        SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _s: None) as client,
        corpus.connect(db) as conn,
    ):
        dry = recover_scanned_petitions(
            conn, client=client, apply=False, char_cap=10_000, today=_TODAY
        )
        applied = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr(),
        )
    assert [(entry.outcome, entry.status) for entry in dry.probes] == [("transport-error", None)]
    assert applied.failures == {"scotus/1": "transport-error"}


def test_a_stored_question_is_never_emptied_by_a_recovery(tmp_path: Path) -> None:
    """The convergence sweep's refusal, kept here.

    A recovered petition whose OCR text carries a heading with nothing usable
    under it derives the empty string, and a full-length question stored beside
    a scanned petition came from a superseded filing — emptying it is as likely
    to be this pass misjudging as a bad row. A case with no stored question
    still gets the honest empty row, which is the ingest path's own rule.
    """
    heading_only = "QUESTIONS PRESENTED\nOPINIONS BELOW\nThe opinion is reported at 1 F.4th 1."
    documents = [
        _document("scotus/1"),
        _document("scotus/1", kind=KIND_QUESTIONS_PRESENTED, pages=0, text="A real question."),
        _document("scotus/2"),
    ]
    db = _seed(tmp_path / "corpus", documents)
    served = {d.url: _pdf_pages([""]) for d in documents}
    with _client(served) as client, corpus.connect(db) as conn:
        result = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr(heading_only),
        )
    assert result.recovered == 2
    assert _documents(db, "scotus/1")[KIND_QUESTIONS_PRESENTED].text == "A real question."
    assert _documents(db, "scotus/2")[KIND_QUESTIONS_PRESENTED].text == ""
    assert result.questions_rederived == 1


def test_ocr_text_with_no_heading_stores_no_questions_row(tmp_path: Path) -> None:
    """No QUESTION(S) PRESENTED heading anywhere means nothing to derive."""
    petition = _document("scotus/1")
    db = _seed(tmp_path / "corpus", [petition])
    with _client({petition.url: _pdf_pages([""])}) as client, corpus.connect(db) as conn:
        result = recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            ocr_page_factory=_stub_ocr("Nothing here names a question."),
        )
    assert result.recovered == 1 and result.questions_rederived == 0
    assert KIND_QUESTIONS_PRESENTED not in _documents(db, "scotus/1")


def test_each_recovery_is_written_as_it_is_made(tmp_path: Path) -> None:
    """A batched write would turn the step's wall-clock cap into a slice that
    recovered a dozen filings and stored none, so each case is banked as it
    lands."""
    documents = [_document(f"scotus/{n}") for n in (1, 2)]
    db = _seed(tmp_path / "corpus", documents)
    served = {d.url: _pdf_pages([""]) for d in documents}
    seen: list[str] = []

    @contextmanager
    def factory(_data: bytes) -> Iterator[OcrPage]:
        # Abandon the run mid-slice, once the first case has been written.
        if seen:
            raise KeyboardInterrupt("the step's cap, near enough")
        seen.append("first")
        yield lambda _index: _OCR_TEXT

    with (
        _client(served) as client,
        corpus.connect(db) as conn,
        pytest.raises(KeyboardInterrupt),
    ):
        recover_scanned_petitions(
            conn,
            client=client,
            apply=True,
            char_cap=10_000,
            today=_TODAY,
            max_cases=2,
            ocr_page_factory=factory,
        )
    assert _OCR_TEXT in _documents(db, "scotus/1")[KIND_PETITION].text
    assert _documents(db, "scotus/2")[KIND_PETITION].text == ""


def _class_of(db: Path) -> tuple[ScannedPetition, ...]:
    with corpus.connect(db) as conn:
        return scanned_petitions(conn).candidates


def test_the_probe_sample_is_spread_across_the_class(tmp_path: Path) -> None:
    """The head is the same three cases every dispatch; a spread sample reports
    on the class rather than on its first three rows."""
    documents = [_document(f"scotus/{n}") for n in range(10, 40)]
    db = _seed(tmp_path / "corpus", documents)
    with _client({d.url: b"%PDF" for d in documents}) as client, corpus.connect(db) as conn:
        result = recover_scanned_petitions(
            conn, client=client, apply=False, char_cap=10_000, today=_TODAY
        )
    sampled = [entry.case_id for entry in result.probes]
    assert len(sampled) == 3 and len(set(sampled)) == 3
    ordered = [candidate.petition.case_id for candidate in _class_of(db)]
    assert [ordered.index(case_id) for case_id in sampled] == [0, 10, 20]


def test_a_dry_run_reports_no_bound_even_when_handed_one(tmp_path: Path) -> None:
    """A dry run writes nothing, so a bound it did not spend would read as a
    slice that attempted none of it."""
    db = _seed(tmp_path / "corpus", [_document("scotus/1")])
    with _client({}) as client, corpus.connect(db) as conn:
        result = recover_scanned_petitions(
            conn,
            client=client,
            apply=False,
            char_cap=10_000,
            today=_TODAY,
            max_cases=5,
            probe_sample=0,
        )
    assert result.bound is None and result.attempted == 0


# --- the subprocess wrapper ------------------------------------------------


def _fake_binary(directory: Path, name: str, script: str) -> None:
    path = directory / name
    path.write_text(f"#!/bin/sh\n{script}\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def test_the_ocr_seam_shells_out_to_the_binaries_on_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Render then recognize, each a fixed argv with no shell.

    Exercised against fakes rather than the real binaries, which the gate does
    not install: what is under test is the wiring — the page number the renderer
    is given, the image piped to the recognizer, and the text handed back.
    """
    binaries = tmp_path / "bin"
    binaries.mkdir()
    # The renderer echoes the page range it was asked for; the recognizer reads
    # the "image" off stdin and reports it, so the seam's plumbing is visible.
    _fake_binary(binaries, "pdftoppm", 'echo "PAGE $2-$4"')
    _fake_binary(binaries, "tesseract", "cat -")
    monkeypatch.setenv("PATH", f"{binaries}{os.pathsep}{os.environ['PATH']}")

    with ocr_page_for_pdf(b"%PDF-1.4 not really a pdf") as ocr_page:
        # 0-based for the extractor, 1-based for the renderer.
        assert ocr_page(0).strip() == "PAGE 1-1"
        assert ocr_page(41).strip() == "PAGE 42-42"


def test_the_ocr_seam_owns_its_failures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A failing binary costs its own page and returns "", never raises.

    The extractor guards this too, but the seam must not lean on that: a raising
    renderer that escaped would discard every digital page beside it and store
    `pages=0`, which the population predicate reads as a PDF that would not open
    — ejecting the row from the class permanently.
    """
    binaries = tmp_path / "bin"
    binaries.mkdir()
    _fake_binary(binaries, "pdftoppm", "exit 3")
    _fake_binary(binaries, "tesseract", "cat -")
    monkeypatch.setenv("PATH", f"{binaries}{os.pathsep}{os.environ['PATH']}")
    with ocr_page_for_pdf(b"%PDF-1.4") as ocr_page:
        assert ocr_page(0) == ""


def test_a_wedged_binary_costs_its_page_and_is_killed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The timeout is what the module's central claim rests on.

    A renderer that never returns must not hold the slice: `subprocess.run`'s
    own timeout kills the child and raises, and that arm returns "" like every
    other failure — the page costs itself.
    """
    binaries = tmp_path / "bin"
    binaries.mkdir()
    _fake_binary(binaries, "pdftoppm", "sleep 30")
    _fake_binary(binaries, "tesseract", "cat -")
    monkeypatch.setenv("PATH", f"{binaries}{os.pathsep}{os.environ['PATH']}")
    with ocr_page_for_pdf(b"%PDF-1.4", timeout=0.5) as ocr_page:
        assert ocr_page(0) == ""


def test_a_document_that_outlives_its_budget_is_abandoned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The page timeout is not a document bound.

    A scan whose pages OCR to nothing accumulates no characters, so the
    extractor's cap never fires; without a document budget one filing can run
    for the length of the step and take the slice's other petitions' writes with
    it. Past the budget every remaining page reads as nothing, which is exactly
    how the extractor treats a page OCR could not read.
    """
    binaries = tmp_path / "bin"
    binaries.mkdir()
    _fake_binary(binaries, "pdftoppm", 'printf "IMAGE"')
    _fake_binary(binaries, "tesseract", 'printf "read"')
    monkeypatch.setenv("PATH", f"{binaries}{os.pathsep}{os.environ['PATH']}")
    clock = iter([0.0, 1.0, 99.0, 99.0])
    with ocr_page_for_pdf(b"%PDF-1.4", budget=10.0, monotonic=lambda: next(clock)) as ocr_page:
        assert ocr_page(0) == "read"  # inside the budget
        assert ocr_page(1) == ""  # past it: abandoned, not recognized


def test_missing_binaries_are_named_in_a_fixed_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    binaries = tmp_path / "bin"
    binaries.mkdir()
    _fake_binary(binaries, "tesseract", "true")
    monkeypatch.setenv("PATH", str(binaries))
    assert missing_ocr_binaries() == ["pdftoppm"]
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    assert missing_ocr_binaries() == ["pdftoppm", "tesseract"]


# --- the CLI ---------------------------------------------------------------


def test_the_cli_dry_run_reports_the_class_and_the_probe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    petition = _document("scotus/1")
    _seed(tmp_path / "corpus", [petition])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    paced: list[float] = []

    class _Recorder(SupremeCourtClient):
        def __init__(self, **kwargs: object) -> None:
            # The politeness seam the contract names: the pass fetches through
            # the same throttled client the fetching lanes use, at the pacing
            # its config sets, not at whatever an OCR loop can manage.
            paced.append(float(kwargs["throttle_seconds"]))  # type: ignore[arg-type]
            super().__init__(
                throttle_seconds=1.0,
                client=httpx.Client(
                    transport=httpx.MockTransport(lambda _r: httpx.Response(403, content=b"")),
                    headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
                ),
                sleep=lambda _s: None,
            )

    monkeypatch.setattr("fedcourtsai.cli.SupremeCourtClient", _Recorder)
    result = runner.invoke(app, ["ocr-recover-petitions"])
    assert result.exit_code == 0, result.output
    assert "dry-run" in result.output and "1 scanned petition(s) in the class" in result.output
    assert "probe scotus/1: http-error (status 403" in result.output
    assert paced == [1.0]


def test_the_cli_refuses_an_apply_without_its_slice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(tmp_path / "corpus", [_document("scotus/1")])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["ocr-recover-petitions", "--apply"])
    assert result.exit_code == 2
    assert "requires an explicit --max-cases" in result.output


def test_the_cli_fails_loud_without_a_corpus(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["ocr-recover-petitions"],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path / "absent")},
    )
    assert result.exit_code == 1
    assert "corpus database is missing" in result.output


def test_the_cli_reports_missing_binaries_as_a_refusal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed(tmp_path / "corpus", [_document("scotus/1")])
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    result = runner.invoke(app, ["ocr-recover-petitions", "--apply", "--max-cases", "5"])
    assert result.exit_code == 1
    assert "the run-repair OCR step" in result.output
