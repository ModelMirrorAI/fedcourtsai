"""Petition-document provisioning: selection, extraction, fetch, cell layout."""

from __future__ import annotations

import json
import logging
import threading
from datetime import date
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, supremecourt
from fedcourtsai.cert_backtest import redact_snapshot
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.documents import (
    _QP_END_RE,
    _QP_MIN_CHARS,
    KIND_BRIEF_IN_OPPOSITION,
    KIND_PETITION,
    KIND_QUESTIONS_PRESENTED,
    _qp_stored_is_fragment,
    backfill_questions_presented,
    document_fetch_losses,
    document_text_coverage,
    extract_pdf_text,
    extract_questions_presented,
    fetch_case_documents,
    questions_presented_extract,
    reset_document_fetch_losses,
    select_documents,
)
from fedcourtsai.supremecourt import SupremeCourtClient
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _pdf(text: str) -> bytes:
    """A minimal one-page PDF whose content stream draws ``text`` (no parens)."""
    return _pdf_pages([text])


def _pdf_pages(texts: list[str]) -> bytes:
    """A minimal PDF whose i-th page draws ``texts[i]`` (no parens).

    An empty string gives that page an empty content stream — a page pypdf
    extracts nothing from, which is what a scanned page looks like to the
    extractor and what the per-page OCR guard is exercised against.
    """
    font = 3 + 2 * len(texts)
    kids = " ".join(f"{3 + 2 * page} 0 R" for page in range(len(texts)))
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {len(texts)} >>".encode(),
    ]
    for page, text in enumerate(texts):
        stream = f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode() if text else b""
        # One object per append rather than a list of them: the page dict and its
        # content stream are appended separately, so no missing comma can merge
        # two PDF objects into one. The `+` inside the dict joins its two halves.
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


def _bio_url(entry_text: str, *, links: list[dict[str, str]] | None = None) -> str | None:
    """Run select_documents over a petition + one candidate entry; the BIO url or None."""
    payload = {
        "ProceedingsandOrder": [
            _PAYLOAD["ProceedingsandOrder"][0],  # the petition entry
            {
                "Date": "Jul 15 2026",
                "Text": entry_text,
                "Links": links
                or [{"Description": "Main Document", "DocumentUrl": "https://example/bio.pdf"}],
            },
        ]
    }
    refs = {r.kind: r.url for r in select_documents(payload)}
    return refs.get(KIND_BRIEF_IN_OPPOSITION)


@pytest.mark.parametrize(
    "entry_text",
    [
        # Real docket phrasings that the "filed ... in opposition" regex missed:
        "Brief of Scott Fuqua in opposition submitted.",  # 25-1108: submitted, not filed
        "Brief of respondent Washington filed.",  # 25-901: no "in opposition"
        "Brief of respondents Philip R. Taft Psy D and Associates, et al. filed.",  # 25-1128
        "Brief of respondents Bette Eakin, et al. in opposition filed.  VIDED.",  # 25-962
    ],
)
def test_select_documents_recognizes_respondent_and_submitted_bios(entry_text: str) -> None:
    assert _bio_url(entry_text) == "https://example/bio.pdf"


@pytest.mark.parametrize(
    "entry_text",
    [
        "Brief amicus curiae of the Cato Institute filed.",  # amicus, not a party BIO
        "Reply of petitioner Acme Corp. filed.",  # petitioner's reply
        "Supplemental brief of respondent Washington filed.",  # supplemental, not the BIO
        "Brief of respondent in support of the petition filed.",  # supports cert, not opposition
        "Waiver of right of respondent Berks County to respond filed.",  # a waiver, no brief
    ],
)
def test_select_documents_excludes_non_opposition_briefs(entry_text: str) -> None:
    assert _bio_url(entry_text) is None


def test_select_documents_returns_every_distinct_bio() -> None:
    # A multi-respondent petition draws a BIO from each respondent; all distinct
    # ones are returned (deduped by URL), in docket order — taking only the last
    # silently dropped the lead respondent's brief (issue #732, scotus/73281002).
    payload = {
        "ProceedingsandOrder": [
            {
                "Date": "May 29 2026",
                "Text": "Brief of respondent Luzerne County in opposition filed.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/lead.pdf"}
                ],
            },
            {
                "Date": "Jun 01 2026",
                "Text": "Brief of respondent Northampton County in opposition filed. VIDED.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/second.pdf"}
                ],
            },
            {  # a duplicate link (same URL) is not double-counted
                "Date": "Jun 01 2026",
                "Text": "Brief of respondent Northampton County in opposition filed. VIDED.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/second.pdf"}
                ],
            },
        ]
    }
    refs = select_documents(payload)
    assert [(r.kind, r.url) for r in refs] == [
        (KIND_BRIEF_IN_OPPOSITION, "https://example/lead.pdf"),
        (KIND_BRIEF_IN_OPPOSITION, "https://example/second.pdf"),
    ]


def test_fetch_case_documents_combines_multiple_bios() -> None:
    # Two respondents' opposition briefs combine into the one brief-in-opposition
    # document, each under its own header, so the cell reads all the opposition.
    payload = {
        "ProceedingsandOrder": [
            _PAYLOAD["ProceedingsandOrder"][0],  # petition
            {
                "Date": "Jun 01 2026",
                "Text": "Brief of respondents Bette Eakin, et al. in opposition filed.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/lead.pdf"}
                ],
            },
            {
                "Date": "Jun 01 2026",
                "Text": "Brief of respondent Northampton County in opposition filed.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/second.pdf"}
                ],
            },
        ]
    }
    served = {
        "https://example/petition.pdf": _pdf("QUESTION PRESENTED Whether X. PARTIES TO THE Acme."),
        "https://example/lead.pdf": _pdf("Lead respondents say deny."),
        "https://example/second.pdf": _pdf("Northampton also says deny."),
    }
    with _doc_client(served) as client:
        documents = fetch_case_documents(
            client,
            "scotus/9025000100",
            payload,
            stored_urls={},
            char_cap=10_000,
            today=date(2026, 7, 10),
        )
    bios = [d for d in documents if d.kind == KIND_BRIEF_IN_OPPOSITION]
    assert len(bios) == 1  # combined into one document
    assert "Lead respondents say deny." in bios[0].text
    assert "Northampton also says deny." in bios[0].text
    # Each block is headed by its docket entry text, so the respondents are named.
    assert "Bette Eakin" in bios[0].text and "Northampton County" in bios[0].text
    # Idempotency key is the canonical URL set, so an unchanged set is skipped.
    assert bios[0].url == "https://example/lead.pdf|https://example/second.pdf"
    stored = {KIND_BRIEF_IN_OPPOSITION: bios[0].url, KIND_PETITION: "https://example/petition.pdf"}
    with _doc_client(served) as client:
        again = fetch_case_documents(
            client,
            "scotus/9025000100",
            payload,
            stored_urls=stored,
            char_cap=10_000,
            today=date(2026, 7, 10),
        )
    assert [d.kind for d in again] == []  # nothing changed → nothing re-fetched


def test_fetch_case_documents_retries_a_bio_that_failed_to_fetch() -> None:
    # A brief that 404s this poll (the rolling-window "missing document is
    # expected" case) must not be lost forever: the stored key records only the
    # briefs actually fetched, so the next poll re-fetches and self-heals.
    payload = {
        "ProceedingsandOrder": [
            {
                "Date": "Jun 01 2026",
                "Text": "Brief of respondents Bette Eakin, et al. in opposition filed.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/lead.pdf"}
                ],
            },
            {
                "Date": "Jun 02 2026",
                "Text": "Brief of respondent Northampton County in opposition filed.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/second.pdf"}
                ],
            },
        ]
    }
    # First poll: only the lead brief is fetchable.
    with _doc_client({"https://example/lead.pdf": _pdf("Lead says deny.")}) as client:
        first = fetch_case_documents(
            client,
            "scotus/9025000100",
            payload,
            stored_urls={},
            char_cap=10_000,
            today=date(2026, 7, 10),
        )
    bio1 = next(d for d in first if d.kind == KIND_BRIEF_IN_OPPOSITION)
    assert bio1.url == "https://example/lead.pdf"  # keyed on what was fetched
    assert "Northampton" not in bio1.text

    # Next poll: the second brief is now available. The partial stored key !=
    # the selected set, so the BIO re-fetches and picks up the missing brief.
    served = {
        "https://example/lead.pdf": _pdf("Lead says deny."),
        "https://example/second.pdf": _pdf("Northampton says deny too."),
    }
    with _doc_client(served) as client:
        second = fetch_case_documents(
            client,
            "scotus/9025000100",
            payload,
            stored_urls={KIND_BRIEF_IN_OPPOSITION: bio1.url},
            char_cap=10_000,
            today=date(2026, 7, 11),
        )
    bio2 = next(d for d in second if d.kind == KIND_BRIEF_IN_OPPOSITION)
    assert bio2.url == "https://example/lead.pdf|https://example/second.pdf"
    assert "Northampton says deny too." in bio2.text


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
    assert extracted.ocr_derived is False


def test_extract_pdf_text_is_never_ocr_derived_without_the_seam() -> None:
    """The fetching lanes pass no ``ocr_page``, so nothing they store claims OCR."""
    scanned = extract_pdf_text(_pdf_pages(["", ""]), char_cap=1000)
    assert scanned.text.strip() == "" and scanned.pages == 2
    assert scanned.ocr_derived is False


def test_extract_pdf_text_ocrs_only_the_pages_that_extracted_nothing() -> None:
    """The guard: an OCR reading never displaces a page's own extracted text."""
    ocred: list[int] = []

    def ocr(page: int) -> str:
        ocred.append(page)
        return f"OCR of page {page}"

    extracted = extract_pdf_text(
        _pdf_pages(["Digital first page", "", "Digital third page"]),
        char_cap=1000,
        ocr_page=ocr,
    )
    assert ocred == [1]  # only the page pypdf read nothing from
    assert "Digital first page" in extracted.text
    assert "OCR of page 1" in extracted.text
    assert "OCR of page 0" not in extracted.text
    assert extracted.pages == 3
    assert extracted.ocr_derived is True


def test_extract_pdf_text_ocr_failure_costs_its_own_page_only() -> None:
    """A raising renderer must not discard the pages that did extract.

    Unguarded it would exit through the whole-document handler, storing empty
    text with `pages=0` — which the recovery population reads as a PDF that
    would not open, ejecting the row from the class for good.
    """

    def ocr(page: int) -> str:
        raise ValueError(f"cannot render page {page}")

    extracted = extract_pdf_text(
        _pdf_pages(["Digital first page", ""]), char_cap=1000, ocr_page=ocr
    )
    assert "Digital first page" in extracted.text
    assert extracted.pages == 2  # not the could-not-open sentinel
    assert extracted.ocr_derived is False


def test_extract_pdf_text_ocr_that_reads_nothing_claims_no_derivation() -> None:
    """A page OCR also fails on stays the empty extraction it already was."""
    extracted = extract_pdf_text(_pdf_pages([""]), char_cap=1000, ocr_page=lambda _page: "")
    assert extracted.text.strip() == ""
    assert extracted.ocr_derived is False


def test_extract_pdf_text_ocr_obeys_the_same_cap_and_truncation_flag() -> None:
    """A recovered document is bounded exactly like a fetched one."""
    extracted = extract_pdf_text(
        _pdf_pages(["", ""]), char_cap=50, ocr_page=lambda _page: "y" * 200
    )
    assert len(extracted.text) == 50 and extracted.truncated is True
    assert extracted.ocr_derived is True


def test_extract_questions_presented_section() -> None:
    assert extract_questions_presented(_PETITION_TEXT) == (
        "Whether the agency exceeded its statutory authority."
    )
    assert extract_questions_presented("no heading here") is None
    unterminated = "QUESTIONS PRESENTED " + "w" * 10_000
    section = extract_questions_presented(unterminated)
    assert section is not None and len(section) <= 4_000


def test_extract_questions_presented_skips_table_of_contents_entry() -> None:
    # A petition whose table of contents lists the QP heading (leader dots to a
    # page number) before the real QP page. The extractor must skip the TOC
    # entry and return the prose question, not the dotted TOC lines (issue: the
    # QP extractor captured a table-of-contents fragment).
    petition = (
        "TABLE OF CONTENTS\n"
        "QUESTIONS PRESENTED ............................................. i\n"
        "TABLE OF AUTHORITIES .......................................... iii\n"
        "\n"
        "QUESTIONS PRESENTED\n"
        "Whether a reviewing court may affirm on a ground the agency never reached.\n"
        "PARTIES TO THE PROCEEDING Petitioner is Acme Corp."
    )
    assert extract_questions_presented(petition) == (
        "Whether a reviewing court may affirm on a ground the agency never reached."
    )


def test_extract_questions_presented_degraded_when_only_a_toc_entry() -> None:
    # If the only match is the TOC entry (no real QP body extracted), better to
    # derive nothing than to hand the agent dotted table-of-contents text. The
    # heading WAS there, so the result is the degraded empty extraction (stored
    # as an empty-text row and labeled `empty_text`), not `None`.
    toc_only = (
        "QUESTIONS PRESENTED ............................................. i\n"
        "TABLE OF AUTHORITIES .......................................... iii"
    )
    assert extract_questions_presented(toc_only) == ""


def test_extract_questions_presented_skips_a_space_aligned_toc_entry() -> None:
    # The same TOC entry aligned with blanks instead of leader dots: everything
    # after the heading text is alignment and the folio, which the dot rule alone
    # does not see, so the capture would read as the single character "i". The
    # real QP page later in the petition is the answer.
    petition = (
        "TABLE OF CONTENTS\n"
        "QUESTIONS PRESENTED                                           i\n"
        "PARTIES TO THE PROCEEDING                                    ii\n"
        "\n"
        "QUESTIONS PRESENTED\n"
        "Whether a reviewing court may affirm on a ground the agency never reached.\n"
        "CORPORATE DISCLOSURE STATEMENT Petitioner is Acme Corp."
    )
    assert extract_questions_presented(petition) == (
        "Whether a reviewing court may affirm on a ground the agency never reached."
    )


def test_extract_questions_presented_reads_past_prose_naming_the_opinion_below() -> None:
    # "the opinion below" is ordinary prose inside a question, and the
    # end-heading vocabulary also spells OPINIONS BELOW: on case alone the phrase
    # cuts the question short at itself. Only a match printed as a heading may
    # end the section.
    petition = (
        "QUESTIONS PRESENTED\n"
        "I. In the opinion below, the court of appeals held that the statute reaches "
        "conduct wholly outside the United States. The question presented is whether "
        "it does.\n"
        "OPINIONS BELOW\n"
        "The opinion of the court of appeals is reported at 1 F.4th 1."
    )
    section = extract_questions_presented(petition)
    assert section is not None
    assert section.startswith("I. In the opinion below,")
    assert section.endswith("The question presented is whether it does.")
    assert "reported at 1 F.4th 1" not in section  # the heading still terminates it


def test_extract_questions_presented_skips_a_space_aligned_toc_the_floor_cannot_catch() -> None:
    # The space-aligned rule earns its keep where the floor cannot help: a TOC
    # whose following entries are outside the end-heading vocabulary, so the
    # capture runs on well past 40 characters and reads as a long "question".
    petition = (
        "QUESTIONS PRESENTED                                           i\n"
        "STATEMENT OF JURISDICTION                                     4\n"
        "STATUTES AND REGULATIONS INVOLVED                             5\n"
        "SUMMARY OF ARGUMENT                                           9\n"
        "\n"
        "QUESTIONS PRESENTED\n"
        "Whether a reviewing court may affirm on a ground the agency never reached.\n"
        "PARTIES TO THE PROCEEDING Petitioner is Acme Corp."
    )
    assert extract_questions_presented(petition) == (
        "Whether a reviewing court may affirm on a ground the agency never reached."
    )


def test_extract_questions_presented_ends_at_a_title_case_heading() -> None:
    # Petitions set the same front matter in title case as often as in caps, and
    # pypdf recovers a small-caps heading that way: the section must still end
    # there rather than running on into the parties list.
    petition = (
        "QUESTIONS PRESENTED\n"
        "Whether a reviewing court may affirm on a ground the agency never reached.\n"
        "Parties to the Proceeding\n"
        "Petitioner is Acme Corp. Respondents are the agency and its administrator."
    )
    assert extract_questions_presented(petition) == (
        "Whether a reviewing court may affirm on a ground the agency never reached."
    )


def test_extract_questions_presented_reads_a_tab_delimited_petition() -> None:
    # A petition that sets its front matter in a table extracts with tabs as the
    # only separator: no line break after the heading, the question running on
    # the heading's own line, and the next heading tab-separated too. A
    # terminator matching a literal space finds no end at all, so the capture
    # runs on into the table of contents and the leader-dot rule discards it —
    # heading found, nothing derived.
    petition = (
        "i\t\t\n\t\n"
        "QUESTION\tPRESENTED\tWhether\t a\tclaim\t for\t wrongful\t death\t under"
        "\tMassachusetts\tlaw\tis\tpreempted\tby\tERISA.\t\t \t\n"
        "ii\t\t\n\t\n"
        "RELATED\tPROCEEDINGS\t\tUnited\tStates\tDistrict\tCourt\t(D.\tMass)\t"
        "Judgment\tentered\tAugust\t22,\t2024.\t\t\n"
        "iii\t\t\n\t\n"
        "TABLE\tOF\tCONTENTS\t\tQuestion presented "
        ".................................................................. i\n"
    )
    section = extract_questions_presented(petition)
    # Exact equality: this text is the labeler's entire evidentiary input, so
    # the fixture pins the artifact, trailing page-folio crumb included — the
    # crumb is pre-existing extractor residue on every layout, not this shape's.
    assert section == (
        "Whether\t a\tclaim\t for\t wrongful\t death\t under"
        + "\tMassachusetts\tlaw\tis\tpreempted\tby\tERISA.\t\t \t\nii"
    )


def test_the_terminator_vocabulary_never_binds_on_a_literal_space() -> None:
    """The construction, not just the outcome: a phrase added to the vocabulary
    with a literal space would silently reintroduce the tab blind spot for that
    phrase alone, and every outcome test would keep passing."""
    assert " " not in _QP_END_RE.pattern
    # Representative separated spellings of vocabulary entries still terminate.
    for separated in (
        "PARTIES\tTO\tTHE\tPROCEEDING",
        "RELATED\nCASES",
        "TABLE\tOF\nAUTHORITIES",
        "LIST\tOF\tALL\tPARTIES",
    ):
        assert _QP_END_RE.search(separated), separated


def test_extract_questions_presented_reads_a_body_after_a_tab_run() -> None:
    # The blank-run folio rule fires only where alignment and a folio are ALL
    # that follows the heading on the line: a question opening after the same
    # run of tabs is a question, not a contents entry.
    petition = (
        "QUESTION\tPRESENTED\t\t\t\t"
        "Whether a reviewing court may affirm on a ground the agency never reached.\n"
        "PARTIES\tTO\tTHE\tPROCEEDING\tPetitioner is Acme Corp."
    )
    assert extract_questions_presented(petition) == (
        "Whether a reviewing court may affirm on a ground the agency never reached."
    )


def test_extract_questions_presented_skips_a_tab_aligned_toc_entry() -> None:
    # A table of contents aligns its folios with tab runs as readily as with
    # blanks, and the blank-run rule reads either: the entry stays a contents
    # capture — including where the following entries are outside the
    # end-heading vocabulary, so the floor cannot help — and the real QP page
    # later in the petition is the answer.
    petition = (
        "TABLE\tOF\tCONTENTS\n"
        "QUESTIONS\tPRESENTED\t\t\t\ti\n"
        "STATEMENT\tOF\tJURISDICTION\t\t\t4\n"
        "SUMMARY\tOF\tARGUMENT\t\t\t9\n"
        "\n"
        "QUESTIONS PRESENTED\n"
        "Whether a reviewing court may affirm on a ground the agency never reached.\n"
        "PARTIES TO THE PROCEEDING Petitioner is Acme Corp."
    )
    assert extract_questions_presented(petition) == (
        "Whether a reviewing court may affirm on a ground the agency never reached."
    )


def test_extract_questions_presented_ends_at_a_double_spaced_heading() -> None:
    # A justified caps heading extracts with the blanks the typesetting left
    # between its words; the parties list must not ride along on the question
    # because of them.
    petition = (
        "QUESTIONS PRESENTED\n"
        "Whether a reviewing court may affirm on a ground the agency never reached.\n"
        "PARTIES  TO  THE  PROCEEDING\n"
        "Petitioners were the defendants-appellants below."
    )
    assert extract_questions_presented(petition) == (
        "Whether a reviewing court may affirm on a ground the agency never reached."
    )


def test_extract_questions_presented_ends_at_a_heading_wrapped_mid_phrase() -> None:
    # The extraction puts a line break where the printed heading wrapped, in the
    # middle of the phrase. A caps heading is a heading wherever its words fall.
    petition = (
        "QUESTIONS PRESENTED\n"
        "Whether a reviewing court may affirm on a ground the agency never reached.\n"
        "RELATED\nCASES\n"
        "State v. Moehle, No. 2021-CF-4832 (Fla. 1st Cir. Ct.). Judgment entered 2021."
    )
    assert extract_questions_presented(petition) == (
        "Whether a reviewing court may affirm on a ground the agency never reached."
    )


def test_extract_questions_presented_keeps_a_quotation_that_elides() -> None:
    # A legal quotation elides with a four-dot ellipsis, which is dots in a run:
    # the leader-dot rule must be long enough that a question quoting a statute
    # is not read as a contents page.
    petition = (
        "QUESTIONS PRESENTED\n"
        'Whether 18 U.S.C. 924(c), which reaches "any person who . . . uses a firearm '
        '. . . ." during a crime of violence, requires proof that the defendant knew '
        "the weapon was operable.\n"
        "PARTIES TO THE PROCEEDING Petitioner is Acme Corp."
    )
    section = extract_questions_presented(petition)
    assert section is not None
    assert section.startswith("Whether 18 U.S.C. 924(c)")
    assert section.endswith("the weapon was operable.")


def test_extract_questions_presented_floors_a_fragment() -> None:
    # A capture under the length floor is a front-matter crumb, not a question:
    # the degraded empty extraction, never text that reads as the QP.
    fragment = "QUESTIONS PRESENTED\ni\nPARTIES TO THE PROCEEDING Petitioner is Acme Corp."
    assert extract_questions_presented(fragment) == ""
    # Absent heading and degraded capture stay distinguishable.
    assert extract_questions_presented("no heading here") is None


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
            "QUESTION PRESENTED Whether the agency exceeded its statutory authority. "
            "PARTIES TO THE PROCEEDING Acme."
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
    assert "Whether the agency exceeded" in by_kind[KIND_PETITION].text
    assert by_kind[KIND_QUESTIONS_PRESENTED].text == (
        "Whether the agency exceeded its statutory authority."
    )
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


def _failing_doc_client(*, unserved: set[str], raising: set[str]) -> SupremeCourtClient:
    """A client whose documents 404 or fail transport, per URL.

    The two silent-loss branches of the fetch path, produced apart: an unserved
    URL is the rolling-window miss (``get_document`` returns ``None``), a
    raising one a transport failure the client's own retry does not clear.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        key = str(request.url)
        if key in raising:
            raise httpx.ConnectError("upstream unreachable", request=request)
        if key in unserved:
            return httpx.Response(404)
        return httpx.Response(200, content=_pdf("Served."))

    inner = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
    )
    return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _s: None)


def test_fetch_case_documents_records_every_dropped_document(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # The provisioning gap has to be diagnosable rather than silent: each skip
    # is counted by reason and warned into the run log, so a case that reaches
    # prediction with no petition carries the route it took instead of only the
    # fact that it has none.
    payload = {
        "ProceedingsandOrder": [
            _PAYLOAD["ProceedingsandOrder"][0],  # petition
            {
                "Date": "Jun 01 2026",
                "Text": "Brief of respondents Bette Eakin, et al. in opposition filed.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/lead.pdf"}
                ],
            },
            {
                "Date": "Jun 02 2026",
                "Text": "Brief of respondent Northampton County in opposition filed.",
                "Links": [
                    {"Description": "Main Document", "DocumentUrl": "https://example/second.pdf"}
                ],
            },
        ]
    }
    reset_document_fetch_losses()
    client = _failing_doc_client(
        unserved={"https://example/petition.pdf", "https://example/second.pdf"},
        raising={"https://example/lead.pdf"},
    )
    with client, caplog.at_level(logging.WARNING, logger="fedcourtsai.pipeline.documents"):
        documents = fetch_case_documents(
            client,
            "scotus/9025000100",
            payload,
            stored_urls={},
            char_cap=10_000,
            today=date(2026, 7, 10),
        )
    assert documents == []  # unchanged: recording is not a control-flow change
    losses = document_fetch_losses()
    assert losses.unavailable == 2  # the petition and the second brief
    assert losses.http_error == 1  # the lead brief's transport failure
    # A case count, not a third per-brief one: every selected brief failed, so
    # the docket lists an opposition the corpus will not hold.
    assert losses.bio_empty == 1
    assert losses.records == 4
    # And the run log carries it, which is the half that survives an ephemeral
    # runner — nothing there reads a counter.
    logged = "\n".join(record.getMessage() for record in caplog.records)
    assert "https://example/petition.pdf" in logged
    assert "unavailable" in logged and "http-error" in logged
    assert "2 selected brief(s), none fetched" in logged
    assert logged.count("scotus/9025000100") == 4

    # The counter is a record of one pass, not a running total across them.
    reset_document_fetch_losses()
    assert document_fetch_losses().records == 0


def test_fetch_case_documents_records_nothing_on_a_clean_fetch() -> None:
    # The counter must stay a signal: a pass that lost nothing records nothing,
    # including the idempotency skips, which are not losses.
    reset_document_fetch_losses()
    served = {
        "https://example/petition.pdf": _pdf("QUESTION PRESENTED Whether X. PARTIES TO THE Acme."),
        "https://example/bio.pdf": _pdf("The petition should be denied."),
    }
    with _doc_client(served) as client:
        fetch_case_documents(
            client,
            "scotus/9025000100",
            _PAYLOAD,
            stored_urls={},
            char_cap=10_000,
            today=date(2026, 7, 10),
        )
    assert document_fetch_losses().records == 0


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


def test_the_document_existence_probe_agrees_with_the_full_read(tmp_path: Path) -> None:
    """`has_documents_for_case` answers the same question `documents_for_case`
    answers by truth of an empty list, without materializing the text. Pinned as
    agreement rather than in isolation, because a probe that drifted from the read
    would silently change what the predict backlog treats as provisioned."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        assert corpus.has_documents_for_case(conn, "scotus/1") is False
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/1",
                    kind=KIND_BRIEF_IN_OPPOSITION,
                    url="https://example/bio.pdf",
                    fetched_at=date(2026, 7, 9),
                    text="stored",
                )
            ],
        )
        for case_id in ("scotus/1", "scotus/2"):
            assert corpus.has_documents_for_case(conn, case_id) == bool(
                corpus.documents_for_case(conn, case_id)
            )
        assert corpus.has_documents_for_case(conn, "scotus/1") is True


def test_the_document_existence_probe_reads_a_documentless_blob_as_empty(tmp_path: Path) -> None:
    """A remote blob packed before the documents table existed reads as "no
    documents" rather than failing — the same degradation `documents_for_case`
    gives, which a ranged cell depends on."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        conn.execute("DROP TABLE documents")
        conn.commit()
        assert corpus.has_documents_for_case(conn, "scotus/1") is False
        assert corpus.documents_for_case(conn, "scotus/1") == []


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
    assert manifest[0]["empty_text"] is False  # real extracted text is present


def test_provision_snapshot_flags_a_blank_extraction(fixture_corpus: FixtureCorpus) -> None:
    # A scanned filing with no text layer extracts to whitespace: pages/truncated
    # alone would read as usable, so the manifest must carry empty_text=true so the
    # cell tells "document present but unextractable" apart from "document absent".
    db = corpus.corpus_db_path(fixture_corpus.corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/305",
                    kind=KIND_PETITION,
                    url="https://example/scanned.pdf",
                    fetched_at=date(2026, 7, 10),
                    pages=10,
                    text="   \n  \n",  # scanned, no text layer -> whitespace only
                )
            ],
        )
    result = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])
    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    entry = next(
        e for e in json.loads(paths.documents_manifest.read_text()) if e["kind"] == KIND_PETITION
    )
    assert entry["empty_text"] is True and entry["pages"] == 10


def test_provision_snapshot_carries_the_ocr_derivation_marker(
    fixture_corpus: FixtureCorpus,
) -> None:
    # Text a recovery pass read off the page images is a lossy derivation of the
    # filing, not the filed words; a manifest that dropped the marker would
    # present it to the cell as a clean extraction.
    db = corpus.corpus_db_path(fixture_corpus.corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/305",
                    kind=KIND_PETITION,
                    url="https://example/scanned.pdf",
                    fetched_at=date(2026, 7, 10),
                    pages=10,
                    ocr_derived=True,
                    text="QUESTIONS PRESENTED\nWhether the scan was readable.",
                ),
                corpus.CaseDocument(
                    case_id="scotus/305",
                    kind=KIND_BRIEF_IN_OPPOSITION,
                    url="https://example/bio.pdf",
                    fetched_at=date(2026, 7, 10),
                    pages=8,
                    text="The petition should be denied.",
                ),
            ],
        )
    result = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])
    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    manifest = json.loads(paths.documents_manifest.read_text())
    marked = {entry["kind"]: entry["ocr_derived"] for entry in manifest}
    assert marked[KIND_PETITION] is True
    # Per document, not per cell: the untouched brief still reads as extracted.
    assert marked[KIND_BRIEF_IN_OPPOSITION] is False


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


# --- backfill: re-deriving stored questions presented --------------------------------

_HONEST_QP = "Whether a reviewing court may affirm on a ground the agency never reached."
# What a pre-guard extraction stored: the petition's own contents entry.
_STALE_TOC_QP = (
    "QUESTIONS PRESENTED ............................................. i\n"
    "TABLE OF AUTHORITIES .......................................... iii"
)
_HONEST_PETITION = (
    "QUESTIONS PRESENTED ............................................. i\n"
    "QUESTIONS PRESENTED\n" + _HONEST_QP + "\nPARTIES TO THE PROCEEDING Acme Corp."
)


def _petition_document(case_id: str, text: str, *, pages: int = 40) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=KIND_PETITION,
        url=f"https://example/{case_id.rsplit('/', 1)[-1]}.pdf",
        entry_date="Jun 01 2026",
        fetched_at=date(2026, 6, 2),
        pages=pages,
        text=text,
    )


def _bio_document(case_id: str, text: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=KIND_BRIEF_IN_OPPOSITION,
        url=f"https://example/{case_id.rsplit('/', 1)[-1]}-bio.pdf",
        entry_date="Jul 01 2026",
        fetched_at=date(2026, 7, 2),
        pages=20,
        text=text,
    )


def _stored_qp(case_id: str, text: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id=case_id,
        kind=KIND_QUESTIONS_PRESENTED,
        url=f"https://example/{case_id.rsplit('/', 1)[-1]}.pdf",
        entry_date="Jun 01 2026",
        fetched_at=date(2026, 6, 2),
        text=text,
    )


def _seed_qp_backfill_corpus(corpus_root: Path) -> Path:
    """Four petitions covering every class the backfill separates.

    - scotus/1: a stale dot-leader TOC capture stored over a derivable QP.
    - scotus/2: the same petition, stored honestly -> unchanged.
    - scotus/3: a body truncated at the prose phrase "the opinion below".
    - scotus/4: petition text but no stored QP row at all -> derived anew.
    """
    db = corpus.corpus_db_path(corpus_root)
    prose = (
        "QUESTIONS PRESENTED\n"
        "I. In the opinion below, the court of appeals held that the statute reaches "
        "conduct wholly outside the United States.\n"
        "OPINIONS BELOW\nThe opinion is reported at 1 F.4th 1."
    )
    truncated = "I. In the"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                # `last_live_polled` puts the row in the live slice — the channel
                # that stores documents, and the backfill's population.
                corpus.CorpusRow(
                    case_id=f"scotus/{n}",
                    court="scotus",
                    docket_number=f"25-{n}",
                    last_live_polled=date(2026, 6, 2),
                )
                for n in (1, 2, 3, 4)
            ],
        )
        corpus.upsert_documents(
            conn,
            [
                _petition_document("scotus/1", _HONEST_PETITION),
                _stored_qp("scotus/1", _STALE_TOC_QP),
                _petition_document("scotus/2", _HONEST_PETITION),
                _stored_qp("scotus/2", _HONEST_QP),
                _petition_document("scotus/3", prose),
                _stored_qp("scotus/3", truncated),
                _petition_document("scotus/4", _HONEST_PETITION),
            ],
        )
    return db


def _stored_qp_text(db: Path, case_id: str) -> str | None:
    with corpus.connect(db) as conn:
        found = {d.kind: d for d in corpus.documents_for_case(conn, case_id)}
    document = found.get(KIND_QUESTIONS_PRESENTED)
    return None if document is None else document.text


def test_backfill_questions_presented_classifies_every_change(tmp_path: Path) -> None:
    db = _seed_qp_backfill_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        result = backfill_questions_presented(conn, apply=False)
    assert result.petitions == 4
    assert result.unchanged == 1  # scotus/2, already what the extractor derives
    assert result.updated == 3
    assert result.changes == {
        "scotus/1": "stale-toc-fragment",
        "scotus/3": "prose-terminator-fragment",
        "scotus/4": "derived-anew",
    }
    assert result.reasons == {
        "derived-anew": 1,
        "prose-terminator-fragment": 1,
        "stale-toc-fragment": 1,
    }
    # A dry run writes nothing at all.
    assert _stored_qp_text(db, "scotus/1") == _STALE_TOC_QP
    assert _stored_qp_text(db, "scotus/4") is None


class _DictReadSource:
    """A payload read source over a dict — just enough of the Protocol to
    serve document reads, the one method the backfill exercises. Records the
    thread each read ran on, so a test can pin the fetch schedule (the serial
    warm-up read, then the pool) and that no case is fetched twice."""

    def __init__(self, documents: dict[str, list[corpus.CaseDocument]]) -> None:
        self._documents = documents
        self.read_threads: dict[str, list[int]] = {}
        self._lock = threading.Lock()

    def latest_snapshot(self, case_id: str) -> tuple[date, dict[str, object]] | None:
        return None

    def snapshot_at(self, case_id: str, *, before: date) -> tuple[date, dict[str, object]] | None:
        return None

    def latest_live_snapshot(self, case_id: str) -> tuple[date, dict[str, object]] | None:
        return None

    def documents_for_case(self, case_id: str) -> list[corpus.CaseDocument]:
        with self._lock:
            self.read_threads.setdefault(case_id, []).append(threading.get_ident())
        return self._documents.get(case_id, [])

    def has_documents(self, case_id: str) -> bool:
        return bool(self._documents.get(case_id))

    def opinion_text(self, case_id: str) -> str | None:
        return None


def test_backfill_marks_a_qp_derived_from_recovered_petition_text(tmp_path: Path) -> None:
    """A QP row cut out of an OCR reading is an OCR reading.

    The follow-on a text recovery owes: the petition carries the derivation
    marker, so the row derived from it must too — on the derived-anew branch (no
    stored QP, the shape a recovered petition leaves, since a QP row is written
    only where the petition had text) and on the re-derive branch alike.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    recovered = [
        _petition_document(f"scotus/{n}", _HONEST_PETITION).model_copy(update={"ocr_derived": True})
        for n in (1, 2)
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=f"scotus/{n}",
                    court="scotus",
                    docket_number=f"25-{n}",
                    last_live_polled=date(2026, 6, 2),
                )
                for n in (1, 2)
            ],
        )
        # scotus/1 holds no QP row; scotus/2 holds a stale one to re-derive over.
        corpus.upsert_documents(conn, [*recovered, _stored_qp("scotus/2", "a stale capture")])
        result = backfill_questions_presented(conn, apply=True)
    assert result.updated == 2
    with corpus.connect(db) as conn:
        for case_id in ("scotus/1", "scotus/2"):
            derived = {d.kind: d for d in corpus.documents_for_case(conn, case_id)}[
                KIND_QUESTIONS_PRESENTED
            ]
            assert derived.text  # something was derived at all
            assert derived.ocr_derived is True


def test_backfill_reads_the_content_store_concurrently_and_identically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The offloaded branch serves document reads from the registered source —
    the first case on the calling thread (the warm-up that constructs a lazy
    client before the pool exists), the rest on worker threads, one read per
    case — and its result is identical to the serial SQLite pass: same counts,
    same ledger, same ordering. The rows stay in SQLite either way (the
    candidate walk is metadata); only the payload reads move."""
    db = _seed_qp_backfill_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        serial = backfill_questions_presented(conn, apply=False)
        stored = {
            f"scotus/{n}": corpus.documents_for_case(conn, f"scotus/{n}") for n in (1, 2, 3, 4)
        }
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    source = _DictReadSource(stored)
    # Save/restore the registered source around the swap; the read of the
    # private registry is the only way to put back the casestore singleton it
    # registers at import (there is no public getter).
    previous = corpus._READ_SOURCE.get("source")
    corpus.set_payload_read_source(source)
    try:
        assert corpus.payload_reads_offloaded()
        with corpus.connect(db) as conn:
            offloaded = backfill_questions_presented(conn, apply=False)
    finally:
        corpus.set_payload_read_source(previous)
    assert offloaded == serial
    assert offloaded.updated == 3
    # One read per case — the pool never duplicates a fetch.
    assert sorted(source.read_threads) == sorted(stored)
    assert all(len(idents) == 1 for idents in source.read_threads.values())
    # The warm-up read runs on the calling thread; the tail runs off it.
    first_case = next(iter(source.read_threads))
    assert source.read_threads[first_case] == [threading.get_ident()]
    tail_idents = {
        idents[0] for case_id, idents in source.read_threads.items() if case_id != first_case
    }
    assert threading.get_ident() not in tail_idents


def test_labeling_extract_reads_the_content_store_under_the_split(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The split writer leaves the blob's `documents` table empty and the store
    # is the system of record for it, so the labeling extract has to serve its
    # texts through the registered read source. A pass that ran SQL of its own
    # over `documents` would report an empty extract against a split blob —
    # which is the failure this shape exists to prevent, so the test empties the
    # table rather than trusting the source to shadow it.
    db = _seed_qp_backfill_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        stored = {
            f"scotus/{n}": corpus.documents_for_case(conn, f"scotus/{n}") for n in (1, 2, 3, 4)
        }
        with conn:
            conn.execute("DELETE FROM documents")
        assert questions_presented_extract(conn).rows == []

    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    source = _DictReadSource(stored)
    previous = corpus._READ_SOURCE.get("source")
    corpus.set_payload_read_source(source)
    try:
        with corpus.connect(db) as conn:
            extract = questions_presented_extract(conn)
    finally:
        corpus.set_payload_read_source(previous)

    # scotus/4 has a petition but no stored questions-presented row, so it is
    # outside the QP-bearing population rather than a skip.
    assert [row.case_id for row in extract.rows] == ["scotus/1", "scotus/2", "scotus/3"]
    assert extract.skipped == 0
    assert extract.rows[1].text == _HONEST_QP
    # One read per scoped case, the store's own — never the emptied blob.
    assert sorted(source.read_threads) == sorted(stored)


def test_backfill_questions_presented_floors_a_stored_fragment(tmp_path: Path) -> None:
    # A stored row the current extractor would no longer produce, and cannot
    # replace either: the rewrite is the honest empty text, not the fragment.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    toc_only = "QUESTIONS PRESENTED                                          i\nTABLE OF CONTENTS"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/9", court="scotus", last_live_polled=date(2026, 6, 2)
                )
            ],
        )
        corpus.upsert_documents(
            conn,
            [_petition_document("scotus/9", toc_only), _stored_qp("scotus/9", "i")],
        )
        result = backfill_questions_presented(conn, apply=True)
    assert result.changes == {"scotus/9": "below-floor"}
    assert _stored_qp_text(db, "scotus/9") == ""


def test_backfill_questions_presented_refuses_to_empty_a_full_length_question(
    tmp_path: Path,
) -> None:
    # The stored row is a whole question; this pass derives nothing from the
    # petition text it can see. That is as likely a misjudged extraction as a bad
    # row, so it is reported and left alone — the write a sweep does not make.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/11", court="scotus", last_live_polled=date(2026, 6, 2)
                )
            ],
        )
        corpus.upsert_documents(
            conn,
            [
                # Petition text with no QP heading at all -> nothing to derive.
                _petition_document("scotus/11", "PARTIES TO THE PROCEEDING Acme Corp."),
                _stored_qp("scotus/11", _HONEST_QP),
            ],
        )
        result = backfill_questions_presented(conn, apply=True)
    assert result.refused == ["scotus/11"]
    assert result.changes == {} and result.updated == 0
    assert _stored_qp_text(db, "scotus/11") == _HONEST_QP


def test_qp_stored_fragment_table() -> None:
    # The helper's whole truth table, so a strip-rule change cannot silently
    # move the refusal boundary: junk-throughout shapes read as fragments
    # (heal), anything question-sized after stripping does not (refuse).
    question = "Whether a claim for wrongful death under state law is preempted by ERISA."
    assert len(question) >= _QP_MIN_CHARS
    fragment_shapes = [
        "." * 42 + "i",  # pure dot leader
        "." * 42 + "i\n" + "." * 50 + "ii",  # a leader block
        "QUESTION PRESENTED\n      i\nTABLE OF AUTHORITIES\n      iii",  # folio on its own line
    ]
    protected_shapes = [
        question + "\nRELATED PROCEEDINGS      ii\n",  # question + trailing TOC residue
        # A single-line question quoting a statute through a long elision:
        # prose around dots, never a leader — the run strips, the line stays.
        'Whether the phrase "any person . . . . . . . . who violates" the statute '
        "reaches an authorized user who misuses access.",
        # No TOC shape at all: trailing padding is not stripping, so the
        # entry condition never fires and the refusal holds.
        question + "\n\n\n",
    ]
    for shape in fragment_shapes:
        assert _qp_stored_is_fragment(shape), shape[:60]
    for shape in protected_shapes:
        assert not _qp_stored_is_fragment(shape), shape[:60]


def test_backfill_heals_a_toc_fragment_however_long_over_the_floor(tmp_path: Path) -> None:
    # A stored dot-leader run clears the character floor by counting the dots
    # — 43 characters of leader and a folio is not a question, and the refusal
    # must not freeze it. The fragment test (not the change classifier — they
    # ask different questions) lifts the refusal, and the heal that empties a
    # full-length value carries its own reason class so the dry-run ledger
    # shows the emptied subset apart.
    long_leader = "." * 42 + "i"
    assert len(long_leader) >= _QP_MIN_CHARS  # over the floor: the refusal's trigger shape
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/12", court="scotus", last_live_polled=date(2026, 6, 2)
                )
            ],
        )
        corpus.upsert_documents(
            conn,
            [
                # No QP heading in the visible text -> the extractor derives
                # nothing; the stored fragment must heal, not survive refused.
                _petition_document("scotus/12", "PARTIES TO THE PROCEEDING Acme Corp."),
                _stored_qp("scotus/12", long_leader),
            ],
        )
        result = backfill_questions_presented(conn, apply=True)
    assert result.refused == []
    assert result.changes == {"scotus/12": "toc-junk-emptied"}
    assert _stored_qp_text(db, "scotus/12") == ""


def test_backfill_keeps_refusing_a_question_with_trailing_toc_residue(tmp_path: Path) -> None:
    # The mixed shape the fragment test must not swallow: a genuine stored
    # question whose old extraction also captured a trailing contents line.
    # Line-wise it classifies as a stale fragment, but stripping the
    # TOC-shaped lines leaves a question-sized text — so the refusal holds
    # and the question survives.
    mixed = (
        "Whether a claim for wrongful death under state law is preempted by "
        "ERISA where the plan is self-funded.\n"
        "RELATED PROCEEDINGS      ii\n"
    )
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/13", court="scotus", last_live_polled=date(2026, 6, 2)
                )
            ],
        )
        corpus.upsert_documents(
            conn,
            [
                _petition_document("scotus/13", "PARTIES TO THE PROCEEDING Acme Corp."),
                _stored_qp("scotus/13", mixed),
            ],
        )
        result = backfill_questions_presented(conn, apply=True)
    assert result.refused == ["scotus/13"]
    assert result.changes == {} and result.updated == 0
    assert _stored_qp_text(db, "scotus/13") == mixed


def test_degraded_extraction_provisions_as_an_empty_text_document(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The seam the tri-state exists for: a petition whose QP heading yields
    # nothing usable stores an empty-text row, and provisioning labels it
    # `empty_text` — "we derived nothing", never a fragment reading as the
    # question.
    served = {
        "https://example/petition.pdf": _pdf(
            "QUESTIONS PRESENTED i TABLE OF CONTENTS Petitioner is Acme Corp."
        )
    }
    with _doc_client(served) as client:
        documents = fetch_case_documents(
            client,
            "scotus/305",
            {"ProceedingsandOrder": [_PAYLOAD["ProceedingsandOrder"][0]]},
            stored_urls={},
            char_cap=10_000,
            today=date(2026, 7, 10),
        )
    by_kind = {d.kind: d for d in documents}
    assert by_kind[KIND_QUESTIONS_PRESENTED].text == ""
    db = corpus.corpus_db_path(fixture_corpus.corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_documents(conn, documents)
    result = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])
    assert result.exit_code == 0, result.output
    paths = CasePaths(fixture_corpus.data_root, "scotus", 305)
    entry = next(
        e
        for e in json.loads(paths.documents_manifest.read_text())
        if e["kind"] == KIND_QUESTIONS_PRESENTED
    )
    assert entry["empty_text"] is True


def test_backfill_questions_presented_cli_dry_run_then_apply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = _seed_qp_backfill_corpus(tmp_path / "corpus")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    dry = runner.invoke(app, ["backfill-questions-presented"])
    assert dry.exit_code == 0, dry.output
    assert "dry-run" in dry.output and "would rewrite 3" in dry.output
    assert "scotus/1: stale-toc-fragment" in dry.output
    stale = _stored_qp_text(db, "scotus/1")
    assert stale is not None and stale.startswith("QUESTIONS PRESENTED ...")

    applied = runner.invoke(app, ["backfill-questions-presented", "--apply"])
    assert applied.exit_code == 0, applied.output
    assert "applied" in applied.output and "rewrote 3" in applied.output
    assert _stored_qp_text(db, "scotus/1") == _HONEST_QP
    assert _stored_qp_text(db, "scotus/2") == _HONEST_QP  # the honest row is untouched
    prose = _stored_qp_text(db, "scotus/3")
    assert prose is not None and prose.startswith("I. In the opinion below,")
    assert _stored_qp_text(db, "scotus/4") == _HONEST_QP

    again = runner.invoke(app, ["backfill-questions-presented"])
    assert again.exit_code == 0, again.output
    assert "would rewrite 0" in again.output  # idempotent


def test_backfill_questions_presented_cli_fails_loud(tmp_path: Path) -> None:
    absent = runner.invoke(
        app,
        ["backfill-questions-presented"],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path / "absent")},
    )
    assert absent.exit_code == 1

    # A corpus holding no petition text at all is the wrong blob, not a converged one.
    empty_root = tmp_path / "empty"
    with corpus.connect(corpus.corpus_db_path(empty_root)):
        pass  # schema only, no rows
    empty = runner.invoke(
        app, ["backfill-questions-presented"], env={"FEDCOURTS_CORPUS_ROOT": str(empty_root)}
    )
    assert empty.exit_code == 1
    assert "wrong blob" in empty.output


def _seed_text_coverage_corpus(corpus_root: Path) -> Path:
    """Seven SCOTUS rows spanning every cut and every caveat the measure reports.

    - scotus/10: paid modern-cert, a scanned filing — the petition and the
      questions-presented row derived from it both read back empty.
    - scotus/11: paid modern-cert, every document carrying text.
    - scotus/12: an IFP serial, so outside the scored segment, with an empty
      brief in opposition — the second fetched kind, counted apart.
    - scotus/13: documents but no `last_live_polled`, so outside the live slice
      the walk frames on — present precisely to prove it is not counted.
    - scotus/14: distributed but holding no documents at all — the other
      failure mode, which no extraction fix reaches.
    - scotus/15: an empty petition stored with zero pages, which is the
      could-not-open branch rather than a scan.
    - scotus/16: an interim application docket, distributed and queued and
      holding nothing — structurally petitionless, so the queued count must
      hold it out rather than report it as a provisioning gap.
    """
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=f"scotus/{n}",
                    court="scotus",
                    docket_number=docket,
                    last_live_polled=polled,
                    # The two denominators the missing-document count reports
                    # over: distribution is the wide stock (a case can have been
                    # distributed long before anything fetched for it), the
                    # queue stamp the narrow, decision-relevant one.
                    distribution_count=distributions,
                    predict_queued_at=queued,
                )
                for n, docket, polled, distributions, queued in (
                    (10, "25-10", date(2026, 6, 2), 1, date(2026, 6, 3)),
                    (11, "25-11", date(2026, 6, 2), 1, None),
                    # At/above IFP_SERIAL_BASE: modern-cert in form, in forma pauperis.
                    (12, "25-9001", date(2026, 6, 2), 2, None),
                    (13, "25-13", None, 1, None),
                    # Distributed and queued, but holding nothing to read.
                    (14, "25-14", date(2026, 6, 2), 1, date(2026, 6, 3)),
                    (15, "25-15", date(2026, 6, 2), 1, None),
                    # An application, not a cert petition: no petition is ever
                    # selected for it, so its absence is the docket form.
                    (16, "26A245", date(2026, 6, 2), 1, date(2026, 6, 3)),
                )
            ],
        )
        corpus.upsert_documents(
            conn,
            [
                # Whitespace-only, not absent: a legible scan with no text layer
                # extracts to exactly this, which is what the measurement counts.
                _petition_document("scotus/10", "   \n\n"),
                _stored_qp("scotus/10", ""),
                _petition_document("scotus/11", _HONEST_PETITION),
                _stored_qp("scotus/11", _HONEST_QP),
                _bio_document("scotus/11", "The petition should be denied."),
                _petition_document("scotus/12", _HONEST_PETITION),
                _bio_document("scotus/12", ""),
                _petition_document("scotus/13", ""),
                _petition_document("scotus/15", "", pages=0),
            ],
        )
    return db


def test_document_text_coverage_counts_empty_text_by_kind_and_segment(tmp_path: Path) -> None:
    db = _seed_text_coverage_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        coverage = document_text_coverage(conn)

    # scotus/13 carries an empty petition but no live-slice stamp: documents
    # reach the corpus on that channel only, so counting it would import a row
    # the pipeline can never provision a cell from.
    assert coverage.cases == 6
    assert coverage.cases_read == 4  # scotus/14 and scotus/16 served nothing
    assert coverage.offloaded is False
    # The petition cut, which is the one a scanning decision reads.
    assert coverage.kind_totals(KIND_PETITION) == (4, 2)
    assert coverage.kind_totals(KIND_BRIEF_IN_OPPOSITION) == (2, 1)
    assert coverage.kind_totals(KIND_QUESTIONS_PRESENTED) == (2, 1)

    cuts = {(cut.segment, cut.kind): (cut.documents, cut.empty) for cut in coverage.cuts}
    assert cuts[("scored", KIND_PETITION)] == (3, 2)
    assert cuts[("scored", KIND_QUESTIONS_PRESENTED)] == (2, 1)
    assert cuts[("rest", KIND_PETITION)] == (1, 0)
    # Zero-filled: a cut nothing was read for is reported, never omitted.
    assert cuts[("rest", KIND_QUESTIONS_PRESENTED)] == (0, 0)
    assert cuts[("scored", KIND_BRIEF_IN_OPPOSITION)] == (1, 0)
    assert cuts[("rest", KIND_BRIEF_IN_OPPOSITION)] == (1, 1)

    # The two counts that keep the empty share from being read as the whole
    # problem: a distributed case with nothing stored, and an empty petition
    # that is a failed open rather than a scan.
    # The wide count is the unfiltered stock, so the application docket is in it.
    assert coverage.distributed == 6
    assert coverage.distributed_without_petition == 2
    # The narrow denominator: scotus/10, scotus/14 and scotus/16 are queued, two
    # of them hold no petition, and only scotus/14 is a gap — scotus/16 is an
    # application docket, which no petition was ever selected for.
    assert coverage.queued == 3
    assert coverage.queued_without_petition == 1
    assert coverage.queued_application_forms == 1
    assert coverage.unopened_petitions == 1

    # The triage list an extraction fix would work from: case_ids in walk order,
    # kinds in read order.
    assert coverage.empty_documents == {
        "scotus/10": [KIND_PETITION, KIND_QUESTIONS_PRESENTED],
        "scotus/12": [KIND_BRIEF_IN_OPPOSITION],
        "scotus/15": [KIND_PETITION],
    }
    # And the second ledger, for the mode no extraction fix reaches: the gap
    # named, the structural floor held out of it.
    assert coverage.queued_without_petition_cases == ["scotus/14"]


def test_document_text_coverage_reach_counts_only_the_counted_kinds(tmp_path: Path) -> None:
    # `cases_read` is the population the cuts are computed over, so a case
    # serving only an uncounted kind must not inflate it — otherwise the reach
    # line silently stops describing the table the moment a new kind is stored.
    db = _seed_text_coverage_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/14",
                    kind="reply",
                    url="https://example/14-reply.pdf",
                    entry_date="Jul 01 2026",
                    fetched_at=date(2026, 7, 2),
                    pages=8,
                    text="Reply text.",
                )
            ],
        )
        coverage = document_text_coverage(conn)
    assert coverage.cases_read == 4
    # And it is still counted as a distributed case holding no petition.
    assert coverage.distributed_without_petition == 2


def test_document_text_coverage_share_is_none_over_an_unread_cut(tmp_path: Path) -> None:
    db = _seed_text_coverage_corpus(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        coverage = document_text_coverage(conn)
    by_cut = {(cut.segment, cut.kind): cut for cut in coverage.cuts}
    # None, not 0.0: a cut nothing was read for must never report as one
    # measured at zero — the same reason every printed line carries its own
    # denominator.
    assert by_cut[("rest", KIND_QUESTIONS_PRESENTED)].share is None
    assert by_cut[("scored", KIND_QUESTIONS_PRESENTED)].share == 0.5


def test_corpus_info_text_coverage_is_opt_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _seed_text_coverage_corpus(tmp_path / "corpus")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))

    plain = runner.invoke(app, ["corpus-info"])
    assert plain.exit_code == 0, plain.output
    # The default stays the cheap vintage report: no per-case document read.
    assert "text coverage" not in plain.stdout

    measured = runner.invoke(app, ["corpus-info", "--text-coverage"])
    assert measured.exit_code == 0, measured.output
    # The petition leads, never a pooled total over kinds that fail differently.
    assert "text coverage: 2 of 4 stored petition(s) carry no text (50.00%)" in measured.stdout
    assert "1 with pages but no text layer, 1 a PDF the extractor could not open" in measured.stdout
    # The other failure mode, printed beside the first rather than left to a
    # reader to notice it is missing.
    assert "missing documents: 2 of 6 distributed case(s) hold no petition row" in measured.stdout
    assert "and 1 of 3 queued for prediction" in measured.stdout
    # The queued count's exclusion is printed, not left to a reader to infer
    # from the docket forms — and it says which side of the ratio it left, since
    # a filtered numerator over an unfiltered denominator is otherwise a share
    # of nothing in particular.
    assert "1 further queued case(s) hold no petition because they are interim" in measured.stdout
    assert "out of the count above but still inside its denominator" in measured.stdout
    # A reach count, said to be one.
    assert (
        "text frame: the pass read documents for 4 of the 6 live-slice case(s)" in measured.stdout
    )
    assert "a reach count, not a failure rate" in measured.stdout
    assert "scored petition            n=3 empty=2 (66.67%)" in measured.stdout
    assert "rest   brief-in-opposition n=1 empty=1 (100.00%)" in measured.stdout
    assert "rest   questions-presented n=0 empty=0 (-)" in measured.stdout
    # The questions-presented zero is structural, and the report says so.
    assert "structurally unable to carry a scan" in measured.stdout
    assert "empty text (3 case(s)):" in measured.stdout
    assert "scotus/10: petition, questions-presented" in measured.stdout
    assert "scotus/12: brief-in-opposition" in measured.stdout
    assert "scotus/15: petition" in measured.stdout
    # The second ledger: the queued gap enumerated, so a store-configured run
    # names the cases a provisioning repair would be designed against — and the
    # application docket is not among them.
    assert "no petition, queued (1 case(s)):" in measured.stdout
    queued_ledger = measured.stdout.split("no petition, queued (1 case(s)):")[1]
    assert queued_ledger.splitlines()[1].strip() == "scotus/14"
    assert "scotus/16" not in queued_ledger


def test_corpus_info_text_coverage_caveats_a_blob_only_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The dev-checkout shape: no content store configured, so the payload reads
    # come off the blob. Under the corpus split that is an undercount, and the
    # report has to say so rather than let the number read as the system's.
    _seed_text_coverage_corpus(tmp_path / "corpus")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    result = runner.invoke(app, ["corpus-info", "--text-coverage"])
    assert result.exit_code == 0, result.output
    assert "text source: this blob's own tables" in result.stdout
    assert "every count below is the blob's own and undercounts the system" in result.stdout
    # And the caveat comes first: the lines under it assert absence, which must
    # not be read before the line saying whether presence was visible at all.
    lines = [line for line in result.stdout.splitlines() if line.startswith(("text ", "missing "))]
    assert lines[0].startswith("text source:")


def test_corpus_info_text_coverage_self_limits_when_the_store_serves_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Corpus-split on with no store transport built: every payload read comes
    # back empty. The counts are then honest zeros over a population the pass
    # never saw, which only the served fraction distinguishes from a corpus
    # whose petitions all carry text.
    _seed_text_coverage_corpus(tmp_path / "corpus")
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "1")
    monkeypatch.delenv("FEDCOURTS_CASESTORE_URL", raising=False)
    monkeypatch.delenv("CASESTORE_URL", raising=False)
    result = runner.invoke(app, ["corpus-info", "--text-coverage"])
    assert result.exit_code == 0, result.output
    assert "text coverage: 0 of 0 stored petition(s) carry no text (-)" in result.stdout
    assert "text frame: the pass read documents for 0 of the 6 live-slice case(s)" in result.stdout
    # Every distributed case reads as holding no petition, which is the loudest
    # form the self-limit takes: nothing was readable, and the report says it in
    # the count a reader is most likely to act on. The application docket still
    # comes out of the queued count — that exclusion is read off the docket
    # number, so it holds whether or not a document was served.
    assert "missing documents: 6 of 6 distributed case(s)" in result.stdout
    assert "and 2 of 3 queued for prediction" in result.stdout
    assert "1 further queued case(s) hold no petition because they are interim" in result.stdout
    assert "text source: the per-case content store" in result.stdout
