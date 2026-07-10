"""Petition-document provisioning (#474): selection, extraction, fetch, cell layout."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx
from typer.testing import CliRunner

from fedcourtsai import corpus, supremecourt
from fedcourtsai.cert_backtest import redact_snapshot
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.documents import (
    KIND_BRIEF_IN_OPPOSITION,
    KIND_PETITION,
    KIND_QUESTIONS_PRESENTED,
    extract_pdf_text,
    extract_questions_presented,
    fetch_case_documents,
    select_documents,
)
from fedcourtsai.supremecourt import SupremeCourtClient
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _pdf(text: str) -> bytes:
    """A minimal one-page PDF whose content stream draws ``text`` (no parens)."""
    stream = f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF".encode()
    )
    return bytes(out)


_PETITION_TEXT = (
    "QUESTION PRESENTED Whether the agency exceeded its statutory authority. "
    "PARTIES TO THE PROCEEDING Petitioner is Acme Corp."
)

_PAYLOAD = {
    "CaseNumber": "25-100 ",
    "QPLink": "../qp/25-00100qp.pdf",  # outcome artifact: must never be selected
    "ProceedingsandOrder": [
        {
            "Date": "Jun 01 2026",
            "Text": "Petition for a writ of certiorari filed. (Response due July 2, 2026)",
            "Links": [
                {"Description": "Petition", "DocumentUrl": "https://example/petition.pdf"},
                {"Description": "Appendix", "DocumentUrl": "https://example/appendix.pdf"},
            ],
        },
        {
            "Date": "Jul 01 2026",
            "Text": "Brief of respondents in opposition filed.",
            "Links": [{"Description": "Main Document", "DocumentUrl": "https://example/bio.pdf"}],
        },
        {"Date": "Jul 08 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."},
    ],
}


# --- selection --------------------------------------------------------------------


def test_select_documents_petition_and_bio_never_qplink() -> None:
    refs = select_documents(_PAYLOAD)
    assert [(r.kind, r.url) for r in refs] == [
        (KIND_PETITION, "https://example/petition.pdf"),
        (KIND_BRIEF_IN_OPPOSITION, "https://example/bio.pdf"),
    ]
    assert all("qp" not in r.url for r in refs)  # QPLink leaks the outcome


def test_select_documents_latest_bio_supersedes() -> None:
    payload = {
        "ProceedingsandOrder": [
            _PAYLOAD["ProceedingsandOrder"][1],
            {
                "Date": "Jul 05 2026",
                "Text": "Brief of respondents in opposition filed. (Corrected)",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/bio2.pdf"}
                ],
            },
        ]
    }
    refs = select_documents(payload)
    assert [(r.kind, r.url) for r in refs] == [
        (KIND_BRIEF_IN_OPPOSITION, "https://example/bio2.pdf")
    ]


# --- extraction -------------------------------------------------------------------


def test_extract_pdf_text_reads_and_caps() -> None:
    extracted = extract_pdf_text(_pdf("Hello petition world"), char_cap=1000)
    assert "Hello petition world" in extracted.text
    assert extracted.pages == 1 and extracted.truncated is False

    capped = extract_pdf_text(_pdf("x" * 200), char_cap=50)
    assert len(capped.text) == 50 and capped.truncated is True


def test_extract_pdf_text_garbage_degrades_to_empty() -> None:
    extracted = extract_pdf_text(b"not a pdf at all", char_cap=1000)
    assert extracted.text == "" and extracted.pages == 0


def test_extract_questions_presented_section() -> None:
    assert extract_questions_presented(_PETITION_TEXT) == (
        "Whether the agency exceeded its statutory authority."
    )
    assert extract_questions_presented("no heading here") is None
    unterminated = "QUESTIONS PRESENTED " + "w" * 10_000
    section = extract_questions_presented(unterminated)
    assert section is not None and len(section) <= 4_000


# --- fetch orchestration ----------------------------------------------------------


def _doc_client(served: dict[str, bytes]) -> SupremeCourtClient:
    def handler(request: httpx.Request) -> httpx.Response:
        key = str(request.url)
        if key in served:
            return httpx.Response(200, content=served[key])
        return httpx.Response(404)

    inner = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
    )
    return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _s: None)


def test_fetch_case_documents_fetches_extracts_and_derives_qp() -> None:
    served = {
        "https://example/petition.pdf": _pdf(
            "QUESTION PRESENTED Whether X. PARTIES TO THE PROCEEDING Acme."
        ),
        "https://example/bio.pdf": _pdf("The petition should be denied because Y."),
    }
    with _doc_client(served) as client:
        documents = fetch_case_documents(
            client,
            "scotus/9025000100",
            _PAYLOAD,
            stored_urls={},
            char_cap=10_000,
            today=date(2026, 7, 10),
        )
    by_kind = {d.kind: d for d in documents}
    assert set(by_kind) == {KIND_PETITION, KIND_BRIEF_IN_OPPOSITION, KIND_QUESTIONS_PRESENTED}
    assert "Whether X." in by_kind[KIND_PETITION].text
    assert by_kind[KIND_QUESTIONS_PRESENTED].text == "Whether X."
    assert by_kind[KIND_QUESTIONS_PRESENTED].pages == 0  # derived, not fetched
    assert "denied because Y" in by_kind[KIND_BRIEF_IN_OPPOSITION].text


def test_fetch_case_documents_skips_stored_urls_and_missing() -> None:
    served = {"https://example/bio.pdf": _pdf("BIO text.")}
    with _doc_client(served) as client:
        documents = fetch_case_documents(
            client,
            "scotus/9025000100",
            _PAYLOAD,
            # Petition already stored at the same URL -> not re-fetched (and no
            # QP re-derivation); the BIO is new.
            stored_urls={KIND_PETITION: "https://example/petition.pdf"},
            char_cap=10_000,
            today=date(2026, 7, 10),
        )
    assert [d.kind for d in documents] == [KIND_BRIEF_IN_OPPOSITION]


# --- corpus storage + cell provisioning --------------------------------------------


def test_documents_roundtrip_latest_wins(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    first = corpus.CaseDocument(
        case_id="scotus/1",
        kind=KIND_BRIEF_IN_OPPOSITION,
        url="https://example/bio.pdf",
        fetched_at=date(2026, 7, 9),
        text="old",
    )
    replacement = first.model_copy(update={"url": "https://example/bio2.pdf", "text": "new"})
    with corpus.connect(db) as conn:
        corpus.upsert_documents(conn, [first])
        corpus.upsert_documents(conn, [replacement])
        stored = corpus.documents_for_case(conn, "scotus/1")
        assert corpus.documents_for_case(conn, "scotus/2") == []
    assert len(stored) == 1
    assert stored[0].text == "new" and stored[0].url == "https://example/bio2.pdf"


def test_provision_snapshot_materializes_documents(fixture_corpus: FixtureCorpus) -> None:
    db = corpus.corpus_db_path(fixture_corpus.corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/305",
                    kind=KIND_QUESTIONS_PRESENTED,
                    url="https://example/petition.pdf",
                    fetched_at=date(2026, 7, 10),
                    text="Whether X.",
                )
            ],
        )
    result = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])
    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    assert paths.document(KIND_QUESTIONS_PRESENTED).read_text() == "Whether X.\n"
    manifest = json.loads(paths.documents_manifest.read_text())
    assert manifest[0]["kind"] == KIND_QUESTIONS_PRESENTED
    assert "text" not in manifest[0]  # metadata only; the text lives in its own file


def test_redact_snapshot_strips_qplink() -> None:
    # The /qp/ page is generated at grant time; the key's presence leaks the outcome.
    assert "QPLink" not in redact_snapshot({"QPLink": "../qp/x.pdf", "CaseNumber": "25-1 "})


def test_select_documents_real_bio_caption_and_amicus_excluded() -> None:
    # The real entry names every respondent (62 chars between "Brief" and
    # "in opposition" on Loper Bright); an amicus "in opposition" never selects.
    payload = {
        "ProceedingsandOrder": [
            {
                "Date": "Jan 20 2023",
                "Text": "Brief amici curiae of States in opposition filed.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/amicus.pdf"}
                ],
            },
            {
                "Date": "Feb 15 2023",
                "Text": "Brief of respondents Gina Raimondo, Secretary of Commerce, "
                "et al. in opposition filed.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/bio.pdf"},
                    {
                        "Description": "Certificate of Word Count",
                        "DocumentUrl": "https://example/cert.pdf",
                    },
                ],
            },
        ]
    }
    refs = select_documents(payload)
    assert [(r.kind, r.url) for r in refs] == [
        (KIND_BRIEF_IN_OPPOSITION, "https://example/bio.pdf")
    ]
