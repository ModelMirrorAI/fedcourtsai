"""The United States' amicus brief on the merits: selected, stored, and handed to no cell."""

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
    KIND_MERITS_BRIEF_PETITIONER,
    KIND_MERITS_BRIEF_RESPONDENT,
    KIND_MERITS_REPLY_PETITIONER,
    KIND_SG_INVITED_BRIEF,
    DocumentRef,
    select_documents,
)
from fedcourtsai.provision import WITHHELD_KINDS, CellRead, documents_for_moment, place_at_moment
from tests.test_documents import (
    _GRANT_ENTRY,
    _LEAD_BRIEFS,
    _MERITS_PETITION_ENTRY,
    _entry,
    _granted_payload,
    _lead_payload,
    _member_payload,
)

_US_URL = "https://www.supremecourt.gov/DocketPDF/25/25-700/us-amicus.pdf"
_US_WORDS = "Brief for the United States as amicus curiae supporting petitioners filed."
_INVITATION = {
    "Date": "Jan 20 2026",
    "Text": "The Solicitor General is invited to file a brief in this case expressing the "
    + "views of the United States.",
    "Links": [],
}


def _kinds(payload: Mapping[str, Any], **kw: Any) -> dict[str, str]:
    return {ref.kind: ref.url for ref in select_documents(payload, **kw)}


@pytest.mark.parametrize(
    "words",
    [
        _US_WORDS,
        "Brief of the United States as amicus curiae supporting respondents filed.",
        "Brief of the United States as Amicus Curiae in support of neither party filed.",
        "Brief amicus curiae of United States filed.",
        "Brief for the United States as amicus curiae supporting vacatur filed. (Distributed)",
    ],
)
def test_the_united_states_merits_amicus_brief_is_selected_after_the_grant(words: str) -> None:
    payload = _granted_payload(_entry("Jun 12 2026", words, url=_US_URL))
    assert _kinds(payload)[KIND_MERITS_AMICUS_UNITED_STATES] == _US_URL


@pytest.mark.parametrize(
    "words",
    [
        # Amici whose names open with the same words.
        "Brief amicus curiae of United States Conference of Catholic Bishops filed.",
        "Brief of United States Senators as amici curiae filed.",
        # Any other amicus brief stays unselected.
        "Brief amicus curiae of Cato Institute filed.",
        "Brief amici curiae of States of Ohio, et al. filed.",
        # The United States as a party is a party's brief, not an amicus's.
        "Brief for the United States filed.",
        "Brief for the federal respondents filed.",
        # Papers about the brief open on their own word.
        "Motion of the United States for leave to participate in oral argument as amicus "
        + "curiae and for divided argument filed.",
        "Supplemental brief of the United States as amicus curiae filed.",
    ],
)
def test_other_merits_stage_filings_are_not_the_united_states_amicus_brief(words: str) -> None:
    payload = _granted_payload(_entry("Jun 12 2026", words, url=_US_URL))
    assert KIND_MERITS_AMICUS_UNITED_STATES not in _kinds(payload)


def test_a_cert_stage_united_states_amicus_brief_is_not_the_merits_one() -> None:
    # Before the grant, and on the grant day itself, the brief is cert stage.
    for filed in ("Mar 02 2026", "Apr 06 2026"):
        payload = {
            "ProceedingsandOrder": [
                _MERITS_PETITION_ENTRY,
                _entry(filed, _US_WORDS, url=_US_URL),
                _GRANT_ENTRY,
            ]
        }
        assert KIND_MERITS_AMICUS_UNITED_STATES not in _kinds(payload)
    # An ungranted docket has no merits stage to place it in.
    ungranted = {"ProceedingsandOrder": [_entry("Jun 12 2026", _US_WORDS, url=_US_URL)]}
    assert KIND_MERITS_AMICUS_UNITED_STATES not in _kinds(ungranted)


def test_the_invited_brief_keeps_its_own_kind_beside_the_merits_brief() -> None:
    sg_url = "https://www.supremecourt.gov/sg.pdf"
    invited = _entry(
        "Mar 02 2026", "Brief for the United States as amicus curiae filed.", url=sg_url
    )
    payload = {
        "ProceedingsandOrder": [
            _MERITS_PETITION_ENTRY,
            _INVITATION,
            invited,
            _GRANT_ENTRY,
            _entry("Jun 12 2026", _US_WORDS, url=_US_URL),
        ]
    }
    kinds = _kinds(payload)
    assert kinds[KIND_SG_INVITED_BRIEF] == sg_url
    assert kinds[KIND_MERITS_AMICUS_UNITED_STATES] == _US_URL


def test_the_brief_is_taken_from_its_main_document_and_the_first_one_wins() -> None:
    linkless: dict[str, object] = {"Date": "Jun 12 2026", "Text": _US_WORDS, "Links": []}
    word_count = _entry(
        "Jun 12 2026", _US_WORDS, url="https://x.gov/wc.pdf", label="Certificate of Word Count"
    )
    later = _entry("Jul 01 2026", _US_WORDS, url="https://x.gov/second.pdf")
    assert KIND_MERITS_AMICUS_UNITED_STATES not in _kinds(_granted_payload(word_count))
    # The merits arms' degradation: a first entry posting no main document is
    # passed over for the next that does.
    assert _kinds(_granted_payload(linkless, later))[KIND_MERITS_AMICUS_UNITED_STATES] == (
        "https://x.gov/second.pdf"
    )
    first = _entry("Jun 12 2026", _US_WORDS, url=_US_URL)
    assert _kinds(_granted_payload(first, later))[KIND_MERITS_AMICUS_UNITED_STATES] == _US_URL


_PARTY_FILINGS = (
    _entry("May 01 2026", "Brief of petitioner Acme Corp. filed.", url="https://x.gov/p.pdf"),
    _entry("Jun 01 2026", "Brief of respondent Roe filed.", url="https://x.gov/r.pdf"),
    _entry("Jul 01 2026", "Reply of petitioner Acme Corp. filed.", url="https://x.gov/pr.pdf"),
    _entry("Jul 02 2026", "Reply of respondent Roe filed.", url="https://x.gov/rr.pdf"),
)


def _without(refs: list[DocumentRef], kind: str) -> list[DocumentRef]:
    return [ref for ref in refs if ref.kind != kind]


@pytest.mark.parametrize("position", range(len(_PARTY_FILINGS) + 1))
def test_the_new_arm_moves_no_other_kind(position: int) -> None:
    """Whatever the United States' brief sits beside, every other row is unchanged."""
    us = [
        _entry("Jun 12 2026", _US_WORDS, url=_US_URL),
        _entry("Jun 13 2026", "Brief amicus curiae of United States filed.", url="https://x/2"),
    ]
    entries = list(_PARTY_FILINGS)
    baseline = select_documents(_granted_payload(*entries))
    entries[position:position] = us
    with_brief = select_documents(_granted_payload(*entries))
    assert _without(with_brief, KIND_MERITS_AMICUS_UNITED_STATES) == baseline
    assert [r.kind for r in with_brief][-1] == KIND_MERITS_AMICUS_UNITED_STATES


def test_the_kind_is_a_fetched_kind_that_describes_itself() -> None:
    assert FETCHED_DOCUMENT_KINDS[-1] == KIND_MERITS_AMICUS_UNITED_STATES
    assert KIND_MERITS_AMICUS_UNITED_STATES in KIND_DESCRIPTIONS


# --- consolidation -----------------------------------------------------------------


def test_a_consolidated_member_borrows_the_groups_brief_off_the_lead() -> None:
    lead = _lead_payload(*_LEAD_BRIEFS, _entry("Jul 20 2026", _US_WORDS, url=_US_URL))
    refs = select_documents(_member_payload(), lead=lead)
    kinds = {ref.kind: ref for ref in refs}
    assert kinds[KIND_MERITS_AMICUS_UNITED_STATES].url == _US_URL
    assert kinds[KIND_MERITS_AMICUS_UNITED_STATES].entry_date == "Jul 20 2026"
    # The party filings borrow as before, and the amicus brief sits after them.
    without = _without(refs, KIND_MERITS_AMICUS_UNITED_STATES)
    assert without == select_documents(_member_payload(), lead=_lead_payload(*_LEAD_BRIEFS))
    assert [r.kind for r in refs][-1] == KIND_MERITS_AMICUS_UNITED_STATES


def test_a_member_never_borrows_a_brief_marked_for_other_dockets() -> None:
    marked = _entry(
        "Jul 20 2026",
        "Brief for the United States as amicus curiae supporting petitioners filed "
        + "(as to 25-500).",
        url=_US_URL,
    )
    assert KIND_MERITS_AMICUS_UNITED_STATES not in _kinds(
        _member_payload(), lead=_lead_payload(*_LEAD_BRIEFS, marked)
    )
    ours = _entry(
        "Jul 21 2026",
        "Brief for the United States as amicus curiae supporting petitioners filed "
        + "(as to 25-501).",
        url="https://x.gov/ours.pdf",
    )
    assert _kinds(_member_payload(), lead=_lead_payload(*_LEAD_BRIEFS, marked, ours))[
        KIND_MERITS_AMICUS_UNITED_STATES
    ] == ("https://x.gov/ours.pdf")


def test_a_lead_never_takes_a_members_marked_brief_as_its_own() -> None:
    marked = _entry(
        "Jul 20 2026",
        "Brief for the United States as amicus curiae filed (as to 25-501).",
        url="https://x.gov/member.pdf",
    )
    unmarked = _entry("Jul 22 2026", _US_WORDS, url=_US_URL)
    lead = _lead_payload(*_LEAD_BRIEFS, marked)
    assert KIND_MERITS_AMICUS_UNITED_STATES not in _kinds(lead)
    assert _kinds(_lead_payload(*_LEAD_BRIEFS, marked, unmarked))[
        KIND_MERITS_AMICUS_UNITED_STATES
    ] == (_US_URL)
    # The lead's party filings are selected as before.
    assert {
        kind: url
        for kind, url in _kinds(_lead_payload(*_LEAD_BRIEFS, marked, unmarked)).items()
        if kind in (KIND_MERITS_BRIEF_PETITIONER, KIND_MERITS_BRIEF_RESPONDENT)
    } == {
        kind: url
        for kind, url in _kinds(_lead_payload(*_LEAD_BRIEFS)).items()
        if kind in (KIND_MERITS_BRIEF_PETITIONER, KIND_MERITS_BRIEF_RESPONDENT)
    }
    assert KIND_MERITS_REPLY_PETITIONER in _kinds(lead)


# --- withheld from every cell --------------------------------------------------------


def _document(kind: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id="scotus/70",
        kind=kind,
        url=f"https://x.gov/{kind}.pdf",
        entry_date="2026-06-12",
        fetched_at=date(2026, 6, 13),
        pages=1,
        truncated=False,
        text="text",
    )


def test_no_cell_of_any_moment_is_handed_the_kind() -> None:
    assert KIND_MERITS_AMICUS_UNITED_STATES in WITHHELD_KINDS
    documents = [
        _document(KIND_MERITS_BRIEF_PETITIONER),
        _document(KIND_MERITS_AMICUS_UNITED_STATES),
    ]
    events = [spec.event_id for spec in moments.DECLARED_MOMENTS] + ["evt-unregistered-moment"]
    for event in events:
        kinds = {d.kind for d in documents_for_moment(documents, event)}
        assert KIND_MERITS_AMICUS_UNITED_STATES not in kinds, event
        assert KIND_MERITS_BRIEF_PETITIONER in kinds, event


def test_an_uncut_cell_is_not_handed_the_kind_either() -> None:
    documents = [
        _document(KIND_MERITS_BRIEF_PETITIONER),
        _document(KIND_MERITS_AMICUS_UNITED_STATES),
    ]
    read = CellRead(
        latest=(date(2026, 7, 1), {}),
        documents=documents,
        events=[],
        row=None,
        cutoff=None,
        dated=None,
    )
    for spec in moments.DECLARED_MOMENTS:
        placement = place_at_moment(
            "scotus/70",
            spec.event_id,
            None,
            read,
            payload={},
            snapshot_date=date(2026, 7, 1),
            documents=documents,
        )
        assert [d.kind for d in placement.documents] == [KIND_MERITS_BRIEF_PETITIONER]
        assert placement.dropped_documents == 1
