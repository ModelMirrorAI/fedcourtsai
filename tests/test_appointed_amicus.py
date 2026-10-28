"""A Court-appointed amicus's merits brief: selected, stored, and handed to no cell yet."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Any

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.documents import (
    FETCHED_DOCUMENT_KINDS,
    KIND_DESCRIPTIONS,
    KIND_MERITS_AMICUS_UNITED_STATES,
    KIND_MERITS_BRIEF_APPOINTED_AMICUS,
    KIND_MERITS_BRIEF_PETITIONER,
    DocumentRef,
    select_documents,
)
from fedcourtsai.pipeline.merits_signals import respondent_brief_date
from fedcourtsai.provision import WITHHELD_KINDS, documents_for_moment
from tests.test_documents import (
    _GRANT_ENTRY,
    _LEAD_BRIEFS,
    _MERITS_PETITION_ENTRY,
    _entry,
    _granted_payload,
    _lead_payload,
    _member_payload,
)

_AMICUS_URL = "https://www.supremecourt.gov/DocketPDF/25/25-700/appointed-amicus.pdf"
_AMICUS_WORDS = "Brief of Court-appointed amicus curiae in support of the judgment below filed."


def _kinds(payload: Mapping[str, Any], **kw: Any) -> dict[str, str]:
    return {ref.kind: ref.url for ref in select_documents(payload, **kw)}


@pytest.mark.parametrize(
    "words",
    [
        _AMICUS_WORDS,
        # The two spellings the Clerk uses, with the docket's own suffix.
        "Brief of Court-appointed amicus curiae filed.  (Distributed)",
        "Brief amicus curiae of Court-appointed amicus curiae in support of the judgment "
        + "below filed.",
        "Brief of the Court appointed amicus curiae filed.",
    ],
)
def test_the_appointed_amicus_brief_is_selected_after_the_grant(words: str) -> None:
    payload = _granted_payload(_entry("Aug 25 2026", words, url=_AMICUS_URL))
    assert _kinds(payload)[KIND_MERITS_BRIEF_APPOINTED_AMICUS] == _AMICUS_URL


def test_the_stored_brief_is_the_entry_that_dates_the_briefed_moment() -> None:
    entry = _entry("Aug 25 2026", _AMICUS_WORDS, url=_AMICUS_URL)
    payload = _granted_payload(entry)
    ref = {r.kind: r for r in select_documents(payload)}[KIND_MERITS_BRIEF_APPOINTED_AMICUS]
    assert ref.entry_date == "Aug 25 2026"
    assert respondent_brief_date(payload, granted_on=date(2026, 4, 6)) == date(2026, 8, 25)


@pytest.mark.parametrize(
    "words",
    [
        # An appointed amicus on the petitioner's side leaves the defense unfiled.
        "Brief of Court-appointed amicus curiae in support of petitioner filed.",
        # Any other amicus brief stays unselected.
        "Brief amicus curiae of Cato Institute filed.",
        "Brief of amici curiae Former Judges in support of the judgment below filed.",
        # The appointment itself and papers about the brief are not the brief.
        "Jane Roe, Esquire, of Washington, D. C., is invited to brief and argue this case, "
        + "as amicus curiae, in support of the judgment below.",
        "Motion of Court-appointed amicus curiae for an extension of time filed.",
    ],
)
def test_other_merits_stage_filings_are_not_the_appointed_amicus_brief(words: str) -> None:
    payload = _granted_payload(_entry("Aug 25 2026", words, url=_AMICUS_URL))
    assert KIND_MERITS_BRIEF_APPOINTED_AMICUS not in _kinds(payload)


def test_a_brief_before_the_grant_or_on_an_ungranted_docket_is_not_selected() -> None:
    for filed in ("Mar 02 2026", "Apr 06 2026"):
        payload = {
            "ProceedingsandOrder": [
                _MERITS_PETITION_ENTRY,
                _entry(filed, _AMICUS_WORDS, url=_AMICUS_URL),
                _GRANT_ENTRY,
            ]
        }
        assert KIND_MERITS_BRIEF_APPOINTED_AMICUS not in _kinds(payload)
    ungranted = {"ProceedingsandOrder": [_entry("Aug 25 2026", _AMICUS_WORDS, url=_AMICUS_URL)]}
    assert KIND_MERITS_BRIEF_APPOINTED_AMICUS not in _kinds(ungranted)


def test_the_brief_is_taken_from_its_main_document_and_the_first_one_wins() -> None:
    word_count = _entry(
        "Aug 25 2026", _AMICUS_WORDS, url="https://x.gov/wc.pdf", label="Certificate of Word Count"
    )
    later = _entry("Sep 01 2026", _AMICUS_WORDS, url="https://x.gov/second.pdf")
    assert KIND_MERITS_BRIEF_APPOINTED_AMICUS not in _kinds(_granted_payload(word_count))
    assert _kinds(_granted_payload(word_count, later))[KIND_MERITS_BRIEF_APPOINTED_AMICUS] == (
        "https://x.gov/second.pdf"
    )
    first = _entry("Aug 25 2026", _AMICUS_WORDS, url=_AMICUS_URL)
    assert _kinds(_granted_payload(first, later))[KIND_MERITS_BRIEF_APPOINTED_AMICUS] == (
        _AMICUS_URL
    )


_OTHER_FILINGS = (
    _entry("May 01 2026", "Brief of petitioner Acme Corp. filed.", url="https://x.gov/p.pdf"),
    _entry(
        "Jun 01 2026",
        "Brief of respondent United States supporting vacatur filed.",
        url="https://x.gov/r.pdf",
    ),
    _entry(
        "Jun 12 2026",
        "Brief for the United States as amicus curiae supporting petitioners filed.",
        url="https://x.gov/us.pdf",
    ),
    _entry("Sep 20 2026", "Reply of petitioner Acme Corp. filed.", url="https://x.gov/pr.pdf"),
)


def _without(refs: list[DocumentRef], kind: str) -> list[DocumentRef]:
    return [ref for ref in refs if ref.kind != kind]


@pytest.mark.parametrize("position", range(len(_OTHER_FILINGS) + 1))
def test_the_new_arm_moves_no_other_kind(position: int) -> None:
    entries = list(_OTHER_FILINGS)
    baseline = select_documents(_granted_payload(*entries))
    entries.insert(position, _entry("Aug 25 2026", _AMICUS_WORDS, url=_AMICUS_URL))
    with_brief = select_documents(_granted_payload(*entries))
    assert _without(with_brief, KIND_MERITS_BRIEF_APPOINTED_AMICUS) == baseline
    assert KIND_MERITS_BRIEF_APPOINTED_AMICUS in {ref.kind for ref in with_brief}


def test_the_kind_is_a_fetched_kind_that_describes_itself() -> None:
    assert KIND_MERITS_BRIEF_APPOINTED_AMICUS in FETCHED_DOCUMENT_KINDS
    assert KIND_MERITS_BRIEF_APPOINTED_AMICUS in KIND_DESCRIPTIONS


# --- consolidation -----------------------------------------------------------------


def test_a_consolidated_member_borrows_the_groups_brief_off_the_lead() -> None:
    lead = _lead_payload(*_LEAD_BRIEFS, _entry("Aug 25 2026", _AMICUS_WORDS, url=_AMICUS_URL))
    refs = {ref.kind: ref for ref in select_documents(_member_payload(), lead=lead)}
    assert refs[KIND_MERITS_BRIEF_APPOINTED_AMICUS].url == _AMICUS_URL
    assert refs[KIND_MERITS_BRIEF_APPOINTED_AMICUS].entry_date == "Aug 25 2026"


def test_a_member_never_borrows_a_brief_marked_for_other_dockets() -> None:
    marked = _entry(
        "Aug 25 2026",
        "Brief of Court-appointed amicus curiae in support of the judgment below filed "
        + "(as to 25-500).",
        url=_AMICUS_URL,
    )
    assert KIND_MERITS_BRIEF_APPOINTED_AMICUS not in _kinds(
        _member_payload(), lead=_lead_payload(*_LEAD_BRIEFS, marked)
    )
    ours = _entry(
        "Aug 26 2026",
        "Brief of Court-appointed amicus curiae in support of the judgment below filed "
        + "(as to 25-501).",
        url="https://x.gov/ours.pdf",
    )
    assert _kinds(_member_payload(), lead=_lead_payload(*_LEAD_BRIEFS, marked, ours))[
        KIND_MERITS_BRIEF_APPOINTED_AMICUS
    ] == ("https://x.gov/ours.pdf")


def test_a_lead_never_takes_a_members_marked_brief_as_its_own() -> None:
    marked = _entry(
        "Aug 25 2026",
        "Brief of Court-appointed amicus curiae filed (as to 25-501).",
        url="https://x.gov/member.pdf",
    )
    assert KIND_MERITS_BRIEF_APPOINTED_AMICUS not in _kinds(_lead_payload(*_LEAD_BRIEFS, marked))


# --- withheld from every cell --------------------------------------------------------


def _document(kind: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id="scotus/70",
        kind=kind,
        url=f"https://x.gov/{kind}.pdf",
        entry_date="2026-08-25",
        fetched_at=date(2026, 8, 26),
        pages=1,
        truncated=False,
        text="text",
    )


def test_no_moment_is_handed_the_kind_until_a_re_bless() -> None:
    assert KIND_MERITS_BRIEF_APPOINTED_AMICUS in WITHHELD_KINDS
    # The United States' merits brief is staged; this one is not.
    assert KIND_MERITS_AMICUS_UNITED_STATES not in WITHHELD_KINDS
    documents = [
        _document(KIND_MERITS_BRIEF_PETITIONER),
        _document(KIND_MERITS_BRIEF_APPOINTED_AMICUS),
    ]
    events = [spec.event_id for spec in moments.DECLARED_MOMENTS] + ["evt-unregistered-moment"]
    for event in events:
        kinds = {d.kind for d in documents_for_moment(documents, event)}
        assert kinds == {KIND_MERITS_BRIEF_PETITIONER}, event
