"""The two combined cert-stage kinds: supplemental briefs and party letters.

Selection, combination and dating, the non-interference of their arms with
every existing kind, and provisioning's withholding of both from every cell.
"""

from __future__ import annotations

from datetime import date

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.documents import (
    COMBINED_KINDS,
    FETCHED_DOCUMENT_KINDS,
    KIND_BRIEF_IN_OPPOSITION,
    KIND_CERT_REPLY,
    KIND_DESCRIPTIONS,
    KIND_MERITS_BRIEF_PETITIONER,
    KIND_PARTY_LETTER,
    KIND_PETITION,
    KIND_SUPPLEMENTAL_BRIEF,
    combined_set_key,
    fetch_case_documents,
    select_documents,
    unheld_document_kinds,
)
from fedcourtsai.provision import (
    WITHHELD_KINDS,
    CellRead,
    documents_before,
    documents_for_moment,
    place_at_moment,
)
from tests.test_documents import _doc_client, _pdf

_HOST = "https://www.supremecourt.gov"
_PETITION = {
    "Date": "Jun 01 2026",
    "Text": "Petition for a writ of certiorari filed. (Response due July 2, 2026)",
    "Links": [{"Description": "Petition", "DocumentUrl": f"{_HOST}/petition.pdf"}],
}
_NEW_KINDS = (KIND_SUPPLEMENTAL_BRIEF, KIND_PARTY_LETTER)


def _entry(date_: str, text: str, url: str, label: str = "Main Document") -> dict[str, object]:
    return {"Date": date_, "Text": text, "Links": [{"Description": label, "DocumentUrl": url}]}


def _docket(*entries: dict[str, object]) -> dict[str, object]:
    return {"ProceedingsandOrder": [_PETITION, *entries]}


def _kind_of(text: str) -> str | None:
    """The kind one candidate entry after the petition is selected under, or None."""
    refs = select_documents(_docket(_entry("Jul 15 2026", text, f"{_HOST}/candidate.pdf")))
    kinds = [ref.kind for ref in refs if ref.url == f"{_HOST}/candidate.pdf"]
    assert len(kinds) <= 1
    return kinds[0] if kinds else None


# --- selection ----------------------------------------------------------------


@pytest.mark.parametrize(
    "entry_text",
    [
        # Real docket phrasings.
        "Supplemental brief of petitioner Graham Schiff filed. (Distributed)",
        "Supplemental brief of respondents City of New York, et al. filed. (Distributed)",
        "Supplemental brief of petitioner filed.",
        "Second supplemental brief of petitioner Kevin Byrd filed. (Distributed)",
        "Second supplemental brief of respondent Ray Lamb filed. (Distributed)",
        "Supplemental brief of appellants Robert A. Rucho, et al. filed. (Distributed)",
        "Supplemental letter brief of petitioner Rose Mary Knick filed. (Distributed)",
        "Supplemental reply letter brief of respondents Township of Scott, Pennsylvania, "
        + "et al. filed.",
        "Supplemental brief of respondent Benjamin Chui filed.  VIDED. (Distributed)",
        # A bare letter brief is the same paper under a shorter caption.
        "Letter brief of petitioner Acme Corp. filed.",
    ],
)
def test_a_partys_supplemental_brief_is_its_own_kind(entry_text: str) -> None:
    assert _kind_of(entry_text) == KIND_SUPPLEMENTAL_BRIEF


@pytest.mark.parametrize(
    "entry_text",
    [
        # An amicus's, the Solicitor General's as amicus among them.
        "Supplemental letter brief of United States as amicus curiae filed. (Distributed)",
        "Supplemental brief of amicus curiae Cato Institute filed.",
        # No party word: the entry alone cannot tell this filer from an amicus.
        "Supplemental brief of United States filed. VIDED. (Distributed)",
        "Supplemental Brief of Korean Claimants submitted.",
        # About a supplemental brief, or on rehearing, or refused.
        "Motion of respondent for leave to file a supplemental brief under seal filed.",
        "Supplemental brief of petitioner in support of petition for rehearing filed.",
        "Supplemental Brief of petitioner Henry L. Klein not accepted for filing.",
        # Other supplemental papers that are not a brief.
        "Supplemental appendix to the petition for rehearing filed.",
        "Joint appendix and 1 supplemental volume filed.",
    ],
)
def test_what_is_not_a_partys_supplemental_brief(entry_text: str) -> None:
    assert _kind_of(entry_text) is None


@pytest.mark.parametrize(
    "entry_text",
    [
        # Real docket phrasings.
        "Letter of petitioner United States advising the Court of newly enacted "
        + "legislation filed.",
        "Letter from counsel for respondent filed.",
        "Letter of June 4, 2019 on behalf of respondents filed. (Distributed)",
        "Letter to Clerk from petitioner submitted.",
        "Letter of petitioner citing supplemental authority filed. (Distributed)",
        "Letter from counsel for petitioner calling the Court's attention to a recent "
        + "Fifth Circuit decision filed.",
        "Letter of respondents in response to petitioner's letter citing supplemental "
        + "authority filed.",
        "Letter in reply regarding supplemental authority filed by petitioner. (Distributed)",
        "Letter of September 17, 2019 from counsel for appellees League of Women Voters "
        + "of Michigan filed.",
        "Letter recieved from petitioners Daril Foose, et al.",
        "Letter from counsel for respondent California received.",
        # Substantive letters that only mention a procedural word.
        "Letter of petitioner advising the Court that the district court extended its "
        + "injunction filed.",
        "Letter of respondent advising the Court that the court of appeals granted a "
        + "motion to dismiss the appeal as moot filed.",
        "Letter of respondent noting the distribution of federal funds at issue ended filed.",
    ],
)
def test_a_partys_letter_is_its_own_kind(entry_text: str) -> None:
    assert _kind_of(entry_text) == KIND_PARTY_LETTER


@pytest.mark.parametrize(
    "entry_text",
    [
        # Procedural: when or how the case is handled, never what is decided.
        "Letter waiving the 14-day waiting period for the distribution of the petition "
        + "pursuant to Rule 15.5 filed.",
        "Letter of May 23, 2019 from counsel for petitioner waiving the 14-day waiting "
        + "period under Rule 15.5 filed.",
        "Letter from counsel for respondent requesting an extension of time filed.",
        "Letter from counsel for respondent requesting additional time filed.",
        "Letter from counsel for petitioner requesting that the petition be distributed "
        + "for the conference of January 9, 2026 filed.",
        "Letter of respondent in support of the motion to dismiss filed.",
        "Letter of petitioner withdrawing the motion for leave to file filed.",
        "Letter from counsel for petitioner regarding the distribution schedule filed.",
        "Letter from counsel for respondent granting blanket consent for the filing of "
        + "amicus curiae briefs received.",
        "Letter from counsel for petitioner submitted pursuant to Rule 12.6 filed.",
        "Letter from counsel for petitioner regarding Rule 29.6 disclosure filed.",
        "Supplemental letter from counsel for petitioners in response to motion filed.",
        # An amicus's letter, the Clerk's, a refused one, or a filer named without
        # a party word.
        "Letter of amicus curiae Commonwealth of Virginia notifying the Court filed.",
        "Letter from the Clerk to counsel for the petitioner filed.",
        "Letter of petitioner citing new authority not accepted for filing.",
        "Letter of Comcast Corporation, et al. submitted.",
        "Letter from the Solicitor General filed.",
        # Opens on something else.
        "Rule 35.3 letter regarding substitution of parties filed by respondents.",
        "Corporate Disclosure Letter filed with respect to brief in opposition of respondent X.",
        "Response to letter of petitioner filed by respondent.",
    ],
)
def test_what_is_not_a_partys_letter(entry_text: str) -> None:
    # Not None throughout: the disclosure letter's text satisfies the
    # opposition arm's reading, which these arms leave as it is.
    assert _kind_of(entry_text) not in _NEW_KINDS


def test_a_letter_brief_is_the_supplemental_brief_never_the_letter() -> None:
    assert _kind_of("Supplemental letter brief of petitioner Rose Mary Knick filed.") == (
        KIND_SUPPLEMENTAL_BRIEF
    )


def test_both_arms_read_only_the_pending_petition() -> None:
    supplemental = "Supplemental brief of petitioner Acme Corp. filed."
    letter = "Letter of petitioner Acme Corp. filed."
    # After a denial (a rehearing-stage paper) nothing is taken.
    denied = _docket(
        {"Date": "Oct 06 2026", "Text": "Petition DENIED.", "Links": []},
        _entry("Oct 10 2026", supplemental, f"{_HOST}/supp.pdf"),
        _entry("Oct 11 2026", letter, f"{_HOST}/letter.pdf"),
    )
    assert {ref.kind for ref in select_documents(denied)} == {KIND_PETITION}
    # After a grant the merits stage begins, and neither arm reads it.
    granted = _docket(
        {"Date": "Oct 06 2026", "Text": "Petition GRANTED.", "Links": []},
        _entry("Nov 10 2026", supplemental, f"{_HOST}/supp.pdf"),
        _entry("Nov 11 2026", letter, f"{_HOST}/letter.pdf"),
    )
    assert {ref.kind for ref in select_documents(granted)} == {KIND_PETITION}


def test_each_arm_takes_its_main_document_alone() -> None:
    payload = _docket(
        _entry(
            "Jul 15 2026",
            "Supplemental brief of petitioner Acme Corp. filed.",
            f"{_HOST}/proof.pdf",
            label="Proof of Service",
        ),
    )
    assert {ref.kind for ref in select_documents(payload)} == {KIND_PETITION}


# --- non-interference -----------------------------------------------------------


_EXISTING = (
    _entry("Jul 01 2026", "Brief of respondent Washington in opposition filed.", f"{_HOST}/b.pdf"),
    _entry("Jul 09 2026", "Reply of petitioner Acme Corp. filed.", f"{_HOST}/reply.pdf"),
)
_NEW = (
    _entry("Jul 03 2026", "Supplemental brief of respondent Washington filed.", f"{_HOST}/s1.pdf"),
    _entry("Jul 05 2026", "Letter from counsel for respondent filed.", f"{_HOST}/l1.pdf"),
    _entry("Jul 20 2026", "Supplemental brief of petitioner Acme Corp. filed.", f"{_HOST}/s2.pdf"),
    _entry("Jul 21 2026", "Letter of petitioner Acme Corp. filed.", f"{_HOST}/l2.pdf"),
)


def test_the_new_arms_change_nothing_the_existing_arms_select() -> None:
    without = select_documents(_docket(*_EXISTING))
    with_new = select_documents(
        _docket(_EXISTING[0], _NEW[0], _NEW[1], _EXISTING[1], _NEW[2], _NEW[3])
    )
    assert [ref for ref in with_new if ref.kind not in _NEW_KINDS] == without
    by_kind: dict[str, list[str]] = {}
    for ref in with_new:
        by_kind.setdefault(ref.kind, []).append(ref.url)
    # The respondent's supplemental brief never lands in the opposition, and the
    # petitioner's never in the cert-stage reply.
    assert by_kind[KIND_BRIEF_IN_OPPOSITION] == [f"{_HOST}/b.pdf"]
    assert by_kind[KIND_CERT_REPLY] == [f"{_HOST}/reply.pdf"]
    assert by_kind[KIND_SUPPLEMENTAL_BRIEF] == [f"{_HOST}/s1.pdf", f"{_HOST}/s2.pdf"]
    assert by_kind[KIND_PARTY_LETTER] == [f"{_HOST}/l1.pdf", f"{_HOST}/l2.pdf"]


def test_a_supplemental_brief_never_takes_a_merits_slot() -> None:
    payload = _docket(
        {"Date": "Oct 06 2026", "Text": "Petition GRANTED.", "Links": []},
        _entry(
            "Nov 01 2026", "Supplemental brief of petitioner Acme Corp. filed.", f"{_HOST}/s.pdf"
        ),
        _entry("Nov 20 2026", "Brief of petitioner Acme Corp. filed.", f"{_HOST}/merits.pdf"),
    )
    refs = {ref.kind: ref.url for ref in select_documents(payload)}
    assert refs[KIND_MERITS_BRIEF_PETITIONER] == f"{_HOST}/merits.pdf"
    assert KIND_SUPPLEMENTAL_BRIEF not in refs


def test_the_new_kinds_are_fetched_combined_and_described() -> None:
    assert FETCHED_DOCUMENT_KINDS[-2:] == _NEW_KINDS
    assert set(_NEW_KINDS) <= set(COMBINED_KINDS)
    assert all(KIND_DESCRIPTIONS[kind] for kind in _NEW_KINDS)


# --- combination and dating -----------------------------------------------------


def _fetch(
    payload: dict[str, object], stored: dict[str, str] | None = None
) -> list[corpus.CaseDocument]:
    served = {
        f"{_HOST}/petition.pdf": _pdf("QUESTION PRESENTED Whether X. PARTIES TO THE Acme."),
        f"{_HOST}/b.pdf": _pdf("Washington says deny."),
        f"{_HOST}/reply.pdf": _pdf("Acme replies."),
        f"{_HOST}/s1.pdf": _pdf("Washington supplements."),
        f"{_HOST}/s2.pdf": _pdf("Acme supplements."),
        f"{_HOST}/l1.pdf": _pdf("Respondent writes."),
        f"{_HOST}/l2.pdf": _pdf("Petitioner writes of mootness."),
    }
    with _doc_client(served) as client:
        return fetch_case_documents(
            client,
            "scotus/9026000100",
            payload,
            stored_urls=stored or {},
            char_cap=10_000,
            today=date(2026, 7, 25),
        )


def test_each_new_kind_is_one_combined_row_dated_by_its_latest_filing() -> None:
    payload = _docket(*_EXISTING, *_NEW)
    rows = {doc.kind: doc for doc in _fetch(payload)}
    supplemental = rows[KIND_SUPPLEMENTAL_BRIEF]
    assert "Washington supplements." in supplemental.text
    assert "Acme supplements." in supplemental.text
    assert "=== Supplemental brief of respondent Washington filed. (Jul 03 2026) ===" in (
        supplemental.text
    )
    assert supplemental.url == f"{_HOST}/s1.pdf|{_HOST}/s2.pdf"
    assert supplemental.entry_date == "Jul 20 2026"
    letters = rows[KIND_PARTY_LETTER]
    assert "Petitioner writes of mootness." in letters.text
    assert letters.entry_date == "Jul 21 2026"
    # The opposition keeps its own dating, by its earliest brief.
    assert rows[KIND_BRIEF_IN_OPPOSITION].entry_date == "Jul 01 2026"
    # A lone filing is stored raw, as a lone opposition is.
    lone = {doc.kind: doc for doc in _fetch(_docket(_NEW[1]))}
    assert lone[KIND_PARTY_LETTER].text.strip() == "Respondent writes."
    assert lone[KIND_PARTY_LETTER].url == f"{_HOST}/l1.pdf"


def test_a_cell_placed_between_two_letters_reads_neither() -> None:
    rows = _fetch(_docket(*_NEW))
    between = {doc.kind for doc in documents_before(rows, date(2026, 7, 10))}
    after = {doc.kind for doc in documents_before(rows, date(2026, 7, 22))}
    assert not between & set(_NEW_KINDS)
    assert set(_NEW_KINDS) <= after


def test_an_undatable_constituent_dates_the_row_by_its_fetch() -> None:
    payload = _docket(
        _entry("Jul 03 2026", "Letter from counsel for respondent filed.", f"{_HOST}/l1.pdf"),
        _entry("July 2026", "Letter of petitioner Acme Corp. filed.", f"{_HOST}/l2.pdf"),
    )
    rows = {doc.kind: doc for doc in _fetch(payload)}
    assert rows[KIND_PARTY_LETTER].entry_date is None
    assert rows[KIND_PARTY_LETTER].fetched_at == date(2026, 7, 25)


def test_the_combined_rows_are_idempotent_on_their_set_and_owed_when_it_grows() -> None:
    first = _docket(_NEW[0], _NEW[1])
    rows = _fetch(first)
    stored = {doc.kind: doc.url for doc in rows}
    assert _fetch(first, stored) == []
    assert unheld_document_kinds(select_documents(first), stored) == []
    grown = _docket(*_NEW)
    refs = select_documents(grown)
    assert unheld_document_kinds(refs, stored) == [KIND_SUPPLEMENTAL_BRIEF, KIND_PARTY_LETTER]
    assert stored[KIND_PARTY_LETTER] != combined_set_key(
        [ref for ref in refs if ref.kind == KIND_PARTY_LETTER]
    )


# --- provisioning withholds both ------------------------------------------------


def _document(kind: str) -> corpus.CaseDocument:
    return corpus.CaseDocument(
        case_id="scotus/9026000100",
        kind=kind,
        url=f"{_HOST}/{kind}.pdf",
        entry_date="Jul 01 2026",
        fetched_at=date(2026, 7, 2),
        pages=1,
        truncated=False,
        text="text",
    )


def test_the_new_kinds_are_withheld() -> None:
    assert set(_NEW_KINDS) <= WITHHELD_KINDS


@pytest.mark.parametrize(
    "event_id",
    [
        *(spec.event_id for spec in moments.DECLARED_MOMENTS),
        # An event that declares no moment, which no date rule reaches.
        "evt-petition-cert",
    ],
)
def test_no_cell_at_any_moment_is_handed_a_withheld_kind(event_id: str) -> None:
    documents = [_document(KIND_PETITION), *(_document(kind) for kind in sorted(WITHHELD_KINDS))]
    kept = documents_for_moment(documents, event_id)
    assert {doc.kind for doc in kept} == {KIND_PETITION}
    # And through the placement every provisioning caller uses, uncut and cut.
    read = CellRead(
        latest=(date(2026, 7, 2), {}),
        documents=documents,
        events=[],
        row=None,
        cutoff=None,
        dated=None,
    )
    placement = place_at_moment(
        "scotus/9026000100",
        event_id,
        None,
        read,
        payload={},
        snapshot_date=date(2026, 7, 2),
        documents=documents,
    )
    assert {doc.kind for doc in placement.documents} == {KIND_PETITION}
    assert placement.dropped_documents == len(WITHHELD_KINDS)


def test_a_cut_cell_is_not_handed_a_withheld_kind_dated_before_its_cutoff() -> None:
    # The cut branch: a real cutoff, and every document dated well before it, so
    # only the withholding can keep the two kinds out.
    documents = [_document(KIND_PETITION), *(_document(kind) for kind in sorted(WITHHELD_KINDS))]
    payload = {
        "ProceedingsandOrder": [
            {"Date": "Jun 01 2026", "Text": "Petition for a writ of certiorari filed."},
            {"Date": "Jul 01 2026", "Text": "Letter from counsel for respondent filed."},
            {"Date": "Jul 05 2026", "Text": "DISTRIBUTED for Conference of 9/29/2026."},
            {"Date": "Oct 06 2026", "Text": "Petition DENIED."},
        ]
    }
    cutoff = date(2026, 9, 30)
    assert {doc.kind for doc in documents_before(documents, cutoff)} == {
        KIND_PETITION,
        *WITHHELD_KINDS,
    }
    read = CellRead(
        latest=(date(2026, 10, 7), payload),
        documents=documents,
        events=[],
        row=None,
        cutoff=cutoff,
        dated=None,
    )
    placement = place_at_moment(
        "scotus/9026000100",
        "evt-order-judgment",
        cutoff,
        read,
        payload=payload,
        snapshot_date=date(2026, 10, 7),
        documents=documents,
    )
    assert placement.provenance == "truncated"
    assert {doc.kind for doc in placement.documents} == {KIND_PETITION}
    assert placement.dropped_documents == len(WITHHELD_KINDS)
