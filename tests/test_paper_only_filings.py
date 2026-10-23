"""A Rule 34.6 paper-only docket is read off its payload and frozen on the cell's context."""

from __future__ import annotations

from datetime import date
from typing import Any

from fedcourtsai.pipeline import cell_context
from fedcourtsai.pipeline.documents import paper_only_filings, select_documents

_PAPER_ONLY = (
    "Pursuant to Rule 34.6 and Paragraph 9 of the Guidelines for the Submission of "
    + "Documents to the Supreme Court's Electronic Filing System, filings in this case "
    + "should be submitted in paper form only, and should not be submitted through the "
    + "Court's electronic filing system."
)
_LIFTED = (
    "As Rule 34.6 provides, “If the Court schedules briefing and oral argument in a "
    + "case that was governed by Federal Rule of Civil Procedure 5.2(c) or Federal Rule "
    + "of Criminal Procedure 49.1(c), the parties shall submit electronic versions of all "
    + "prior and subsequent filings with this Court in the case.”"
)


def _entry(day: str, text: str) -> dict[str, Any]:
    return {"Date": day, "Text": text, "Links": []}


def _payload(*entries: dict[str, Any]) -> dict[str, Any]:
    return {"CaseNumber": "26-55 ", "ProceedingsandOrder": list(entries)}


_PETITION = _entry("Jul 01 2026", "Petition for a writ of certiorari filed.")


def test_the_paper_only_entry_marks_the_docket() -> None:
    payload = _payload(_PETITION, _entry("Jul 07 2026", _PAPER_ONLY))
    assert paper_only_filings(payload) is True
    # The reason it matters: the selector finds nothing to fetch on such a docket.
    assert select_documents(payload) == []


def test_a_later_call_for_electronic_versions_lifts_it() -> None:
    payload = _payload(
        _PETITION,
        _entry("Jul 07 2026", _PAPER_ONLY),
        _entry("Jan 12 2027", "Petition GRANTED."),
        _entry("Jan 12 2027", _LIFTED),
    )
    assert paper_only_filings(payload) is False


def test_an_ordinary_docket_reads_false_and_a_rest_payload_none() -> None:
    assert paper_only_filings(_payload(_PETITION)) is False
    assert paper_only_filings(_payload()) is False
    assert paper_only_filings({"id": 305, "docket_number": "24-12"}) is None


def test_the_rule_quoted_mid_entry_does_not_mark_the_docket() -> None:
    quoted = _entry("Jul 09 2026", "Letter noting that, pursuant to Rule 34.6 and Paragraph 9, ...")
    assert paper_only_filings(_payload(_PETITION, quoted)) is False


def test_the_context_freezes_the_flag() -> None:
    marked = _payload(_PETITION, _entry("Jul 07 2026", _PAPER_ONLY))
    built = cell_context.build("scotus/9026000055", date(2026, 7, 20), marked, "forward")
    assert built.paper_only_filings is True
    plain = cell_context.build(
        "scotus/9026000055", date(2026, 7, 20), _payload(_PETITION), "forward"
    )
    assert plain.paper_only_filings is False
    rest = {"id": 305, "docket_number": "24-12", "docket_entries": []}
    assert (
        cell_context.build("scotus/305", date(2026, 7, 20), rest, "forward").paper_only_filings
        is None
    )
