"""The merits-docket signal readers."""

from __future__ import annotations

from datetime import date

from fedcourtsai.pipeline.merits_signals import respondent_brief_date

GRANT = date(2025, 3, 4)


def _docket(*entries: tuple[str, str]) -> dict[str, object]:
    return {"ProceedingsandOrder": [{"Date": d, "Text": t} for d, t in entries]}


def test_the_respondents_merits_brief_is_read_from_its_entry() -> None:
    payload = _docket(
        ("Mar 4 2025", "Petition GRANTED."),
        ("Jun 2 2025", "Brief of respondent Penny Clarkston filed. (Distributed)"),
    )
    assert respondent_brief_date(payload, granted_on=GRANT) == date(2025, 6, 2)


def test_a_qualified_respondent_group_still_reads() -> None:
    # The Court writes "Brief of State respondents filed" where a case has
    # several respondent groups; requiring the bare noun would drop those.
    for text in ("Brief of State respondents filed.", "Brief of  NAACP respondents  filed."):
        assert respondent_brief_date(_docket(("Jun 2 2025", text)), granted_on=GRANT) == date(
            2025, 6, 2
        )


def test_the_cert_stage_brief_in_opposition_is_not_a_merits_brief() -> None:
    # Same shape, same words, different stage — and it is the single most
    # likely thing to be mistaken for this signal.
    before = _docket(("Feb 1 2025", "Brief of respondent Acme Corp. in opposition filed."))
    assert respondent_brief_date(before, granted_on=GRANT) is None
    # Even filed after the grant (a supplemental BIO, a rehearing opposition).
    after = _docket(("Jun 2 2025", "Brief of respondent Acme Corp. in opposition filed."))
    assert respondent_brief_date(after, granted_on=GRANT) is None


def test_an_amicus_supporting_the_respondent_is_not_the_respondent() -> None:
    payload = _docket(("Jun 2 2025", "Brief amicus curiae of Cato Institute filed."))
    assert respondent_brief_date(payload, granted_on=GRANT) is None


def test_a_respondent_supporting_the_petitioner_is_not_the_adversarial_brief() -> None:
    # A real merits brief, but not the moment being named: the opposing
    # argument is still to come, sometimes from a Court-appointed amicus.
    payload = _docket(
        ("Jun 2 2025", "Brief of respondent Steven Aiello in support of petitioner filed."),
        ("Jul 8 2025", "Brief of respondent Latrice Saxon filed."),
    )
    assert respondent_brief_date(payload, granted_on=GRANT) == date(2025, 7, 8)


def test_entries_at_or_before_the_grant_never_qualify() -> None:
    same_day = _docket(("Mar 4 2025", "Brief of respondent Acme Corp. filed."))
    assert respondent_brief_date(same_day, granted_on=GRANT) is None


def test_without_a_grant_date_there_is_no_merits_proceeding_to_brief() -> None:
    payload = _docket(("Jun 2 2025", "Brief of respondent Acme Corp. filed."))
    assert respondent_brief_date(payload, granted_on=None) is None


def test_an_undated_entry_is_skipped_rather_than_guessed() -> None:
    payload = {"ProceedingsandOrder": [{"Text": "Brief of respondent Acme Corp. filed."}]}
    assert respondent_brief_date(payload, granted_on=GRANT) is None


def test_the_first_qualifying_brief_wins() -> None:
    payload = _docket(
        ("Jun 2 2025", "Brief of respondent A filed."),
        ("Jul 8 2025", "Brief of respondent B filed."),
    )
    assert respondent_brief_date(payload, granted_on=GRANT) == date(2025, 6, 2)


def test_filings_that_merely_mention_a_respondent_do_not_match() -> None:
    # The start anchor is what separates the brief from the rest of the docket.
    for text in (
        "Blanket Consent filed by Respondent, Texas",
        "Motion for divided argument filed by respondents.",
        "Motion of respondent for leave to file the joint appendix under seal filed.",
        "Record received from the United States Court of Appeals for the Ninth Circuit.",
    ):
        assert respondent_brief_date(_docket(("Jun 2 2025", text)), granted_on=GRANT) is None
