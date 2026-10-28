"""A combined row of several filings is cut filing by filing, every argument before any appendix."""

from __future__ import annotations

from datetime import date

import pytest

from fedcourtsai.pipeline.documents import (
    KIND_BRIEF_IN_OPPOSITION,
    CombinedFiling,
    bio_block_texts,
    cut_combined_text,
    fetch_case_documents,
)
from tests.test_documents import _PAYLOAD, _doc_client, _pdf_pages

_NOTE = "[pipeline note:"


def _body(name: str, pages: int, width: int) -> list[str]:
    """``pages`` argument pages for ``name``, the last ending on its conclusion."""
    texts = [f"{name} argument page {n} " + "x" * width for n in range(pages)]
    texts[-1] += f"\nCONCLUSION OF {name}"
    return texts


def _appendix(pages: int, width: int) -> list[str]:
    return [
        "APPENDIX\nOpinion of the court of appeals " + "y" * width,
        *[f"App. page {n} " + "y" * width for n in range(1, pages)],
    ]


def _filing(name: str, pages: list[str], total: int | None = None) -> CombinedFiling:
    return (f"=== Brief of respondent {name} in opposition filed. ===", pages, total or len(pages))


def test_under_the_cap_the_row_is_every_page_joined_under_its_header() -> None:
    first = _filing("Washington", ["one", "two"])
    second = _filing("Detainees", ["three"])
    text, cut = cut_combined_text([first, second], char_cap=10_000)
    assert not cut
    assert text == f"{first[0]}\none\ntwo\n\n{second[0]}\nthree"


def test_the_first_appendix_never_crowds_out_the_second_argument() -> None:
    # The shape of the flagged case: a first brief with a long bound appendix,
    # then a second brief whose argument a docket-order cut never reached.
    first = _filing("Washington", _body("WASHINGTON", 5, 900) + _appendix(30, 900))
    second = _filing("Detainees", _body("DETAINEES", 5, 900))
    cap = 15_000
    text, cut = cut_combined_text([first, second], char_cap=cap)
    assert cut
    assert len(text) <= cap
    assert "CONCLUSION OF WASHINGTON" in text
    assert "CONCLUSION OF DETAINEES" in text
    # The appendix opens, is cut, and the cut is stated inside the first block.
    blocks = bio_block_texts(text)
    assert len(blocks) == 2
    assert "Opinion of the court of appeals" in blocks[0]
    assert "of this filing's appendix omitted here" in blocks[0]
    assert _NOTE not in blocks[1]


def test_where_the_arguments_overflow_every_appendix_goes_and_the_cap_is_shared() -> None:
    first = _filing("Washington", _body("WASHINGTON", 20, 900) + _appendix(10, 900))
    second = _filing("Detainees", _body("DETAINEES", 4, 900))
    cap = 12_000
    text, cut = cut_combined_text([first, second], char_cap=cap)
    assert cut
    assert len(text) <= cap
    first_block, second_block = bio_block_texts(text)
    # The shorter brief is under its even share, so it is kept whole.
    assert "CONCLUSION OF DETAINEES" in second_block
    assert _NOTE not in second_block
    # The longer one takes the rest and says where it was cut.
    assert "WASHINGTON argument page 0" in first_block
    assert "CONCLUSION OF WASHINGTON" not in first_block
    assert "of this filing omitted here" in first_block
    # Its appendix is left out whole, and the note says which pages.
    assert "Opinion of the court of appeals" not in first_block
    assert "this filing's appendix, PDF pages 21 to 30" in first_block


def test_two_long_arguments_share_the_cap_evenly() -> None:
    first = _filing("Washington", _body("WASHINGTON", 20, 900))
    second = _filing("Detainees", _body("DETAINEES", 20, 900))
    text, cut = cut_combined_text([first, second], char_cap=12_000)
    assert cut
    first_block, second_block = bio_block_texts(text)
    assert abs(len(first_block) - len(second_block)) < 1_500


def test_pages_never_read_are_stated_in_their_filing() -> None:
    first = _filing("Washington", _body("WASHINGTON", 5, 900), total=40)
    second = _filing("Detainees", _body("DETAINEES", 5, 900))
    text, cut = cut_combined_text([first, second], char_cap=8_000)
    assert cut
    first_block, _ = bio_block_texts(text)
    assert "PDF pages 6 to 40 of this filing were not read" in first_block


def test_a_cap_too_small_to_share_falls_back_to_the_plain_cut_and_says_so() -> None:
    filings = [_filing(name, _body(name, 3, 900)) for name in ("A", "B", "C")]
    text, cut = cut_combined_text(filings, char_cap=3_000)
    whole = "\n\n".join(f"{header}\n" + "\n".join(pages) for header, pages, _ in filings)
    assert cut
    assert len(text) <= 3_000
    head, note = text.rsplit("\n", 1)
    assert whole.startswith(head)
    assert note.startswith(_NOTE) and note.endswith("-character text cap]")


def _notes_close(text: str) -> bool:
    """Every note the cut wrote is whole: on its own line and closed."""
    lines = [line for line in text.splitlines() if _NOTE in line]
    return bool(lines) and all(line.startswith(_NOTE) and line.endswith("]") for line in lines)


@pytest.mark.parametrize("cap", [5_000, 8_000, 15_000, 40_000])
def test_every_note_fits_whole_under_the_cap(cap: int) -> None:
    # The final slice never has to bite: every filing writes all three notes it
    # can (a body cut, an appendix cut, unread pages) and each closes.
    filings = [
        _filing(name, _body(name, 12, 900) + _appendix(12, 900), total=60)
        for name in ("Washington", "Detainees", "Intervenors")
    ]
    text, cut = cut_combined_text(filings, char_cap=cap)
    assert cut
    assert len(text) <= cap
    assert _notes_close(text)


def test_an_unreadable_filing_costs_nothing_and_the_others_share_the_cap() -> None:
    # A PDF that will not open reads as no pages (`read_filing_pages`).
    empty = _filing("Unreadable", [], total=0)
    second = _filing("Detainees", _body("DETAINEES", 20, 900))
    text, cut = cut_combined_text([empty, second], char_cap=10_000)
    assert cut
    first_block, second_block = bio_block_texts(text)
    assert first_block.strip() == ""
    assert "DETAINEES argument page 0" in second_block
    assert _notes_close(text)


def test_the_fetched_row_carries_every_brief_through_its_conclusion() -> None:
    payload = {
        "ProceedingsandOrder": [
            _PAYLOAD["ProceedingsandOrder"][0],  # petition
            {
                "Date": "Jun 01 2026",
                "Text": "Brief of respondent Washington in opposition filed.",
                "Links": [
                    {
                        "Description": "Main Document",
                        "DocumentUrl": "https://www.supremecourt.gov/lead.pdf",
                    }
                ],
            },
            {
                "Date": "Jun 02 2026",
                "Text": "Brief of respondents Detainees in opposition filed.",
                "Links": [
                    {
                        "Description": "Main Document",
                        "DocumentUrl": "https://www.supremecourt.gov/second.pdf",
                    }
                ],
            },
        ]
    }
    lead_pages = [f"Washington argues page {n} " + "w" * 400 for n in range(5)]
    lead_pages += ["APPENDIX"] + [f"Appendix opinion page {n} " + "a" * 400 for n in range(20)]
    second_pages = [f"Detainees argue page {n} " + "d" * 400 for n in range(4)]
    second_pages.append("Detainees conclusion deny the petition")
    served = {
        "https://www.supremecourt.gov/petition.pdf": _pdf_pages(["QUESTION PRESENTED Whether X."]),
        "https://www.supremecourt.gov/lead.pdf": _pdf_pages(lead_pages),
        "https://www.supremecourt.gov/second.pdf": _pdf_pages(second_pages),
    }
    cap = 6_000
    with _doc_client(served) as client:
        documents = fetch_case_documents(
            client,
            "scotus/9025000100",
            payload,
            stored_urls={},
            char_cap=cap,
            today=date(2026, 7, 10),
        )
    (bio,) = [d for d in documents if d.kind == KIND_BRIEF_IN_OPPOSITION]
    assert bio.truncated
    assert len(bio.text) <= cap
    assert bio.pages == len(lead_pages) + len(second_pages)
    first_block, second_block = bio_block_texts(bio.text)
    assert "Washington argues page 4" in first_block
    assert "of this filing's appendix omitted here" in first_block
    assert "Detainees conclusion deny the petition" in second_block


def test_a_group_of_two_with_one_fetched_is_cut_as_one_filing_under_its_header() -> None:
    payload = {
        "ProceedingsandOrder": [
            _PAYLOAD["ProceedingsandOrder"][0],  # petition
            {
                "Date": "Jun 01 2026",
                "Text": "Brief of respondent Washington in opposition filed.",
                "Links": [
                    {
                        "Description": "Main Document",
                        "DocumentUrl": "https://www.supremecourt.gov/lead.pdf",
                    }
                ],
            },
            {
                "Date": "Jun 02 2026",
                "Text": "Brief of respondents Detainees in opposition filed.",
                "Links": [
                    {
                        "Description": "Main Document",
                        "DocumentUrl": "https://www.supremecourt.gov/missing.pdf",
                    }
                ],
            },
        ]
    }
    lead_pages = [f"Washington argues page {n} " + "w" * 400 for n in range(5)]
    lead_pages += ["APPENDIX"] + [f"Appendix opinion page {n} " + "a" * 400 for n in range(20)]
    served = {
        "https://www.supremecourt.gov/petition.pdf": _pdf_pages(["QUESTION PRESENTED Whether X."]),
        "https://www.supremecourt.gov/lead.pdf": _pdf_pages(lead_pages),
    }
    with _doc_client(served) as client:
        documents = fetch_case_documents(
            client,
            "scotus/9025000100",
            payload,
            stored_urls={},
            char_cap=6_000,
            today=date(2026, 7, 10),
        )
    (bio,) = [d for d in documents if d.kind == KIND_BRIEF_IN_OPPOSITION]
    assert bio.truncated
    assert bio.url == "https://www.supremecourt.gov/lead.pdf"
    (block,) = bio_block_texts(bio.text)
    assert bio.text.startswith("=== Brief of respondent Washington")
    assert "Washington argues page 4" in block
    assert "of this filing's appendix omitted here" in block
    assert _notes_close(bio.text)
