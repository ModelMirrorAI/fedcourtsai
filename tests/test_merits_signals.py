"""The merits-docket signal readers."""

from __future__ import annotations

from datetime import date

import pytest

from fedcourtsai.pipeline.merits_signals import (
    is_petitioner_merits_brief,
    is_petitioner_merits_reply,
    is_respondent_merits_brief,
    is_respondent_merits_reply,
    respondent_brief_date,
)

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


@pytest.mark.parametrize(
    "text",
    [
        "Brief of petitioner Floyd Johnson filed.",
        "Brief of petitioners Department of Labor, et al. filed.",
        "Brief of petitioners Kousisis, et al. filed.",
        "Brief of the petitioner filed.  (Distributed)",
        "Brief of petitioners Federal Communications Commission, et al. filed. VIDED.",
    ],
)
def test_the_petitioners_merits_brief_reads_off_its_entry(text: str) -> None:
    assert is_petitioner_merits_brief(text)


@pytest.mark.parametrize(
    "text",
    [
        "Brief amicus curiae of Institute for Justice filed.",  # the anchor refuses it
        "Brief of amici curiae Kansas, et al. in support of petitioners filed.",
        "Brief of petitioner Acme Corp. in support of respondents filed.",
        "Brief of petitioner Acme Corp. in opposition filed.",
        "Reply of petitioner Acme Corp. filed.",  # the reply is its own entry family
        "Reply Brief of petitioner Acme Corp. filed. (Distributed)",
        "Motion of petitioner to dismiss the petition filed.",
        "Brief of respondent Acme Corp. filed.",  # the other side
    ],
)
def test_the_petitioner_predicate_refuses_everything_else(text: str) -> None:
    assert not is_petitioner_merits_brief(text)


def test_the_two_side_predicates_never_take_the_same_entry() -> None:
    # Whatever else they disagree about, no entry is both sides' brief — which is
    # what lets the document selector run them as two arms of one chain.
    for text in (
        "Brief of petitioner Floyd Johnson filed.",
        "Brief of respondent United States filed.",
        "Brief of respondents Mi Familia Vota, et al. in support of petitioners filed.",
        "Brief amicus curiae of Cato Institute filed.",
    ):
        assert not (is_petitioner_merits_brief(text) and is_respondent_merits_brief(text))


def test_filings_that_merely_mention_a_respondent_do_not_match() -> None:
    # The start anchor is what separates the brief from the rest of the docket.
    for text in (
        "Blanket Consent filed by Respondent, Texas",
        "Motion for divided argument filed by respondents.",
        "Motion of respondent for leave to file the joint appendix under seal filed.",
        "Record received from the United States Court of Appeals for the Ninth Circuit.",
    ):
        assert respondent_brief_date(_docket(("Jun 2 2025", text)), granted_on=GRANT) is None


# --- the reply on the merits -------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        # Real post-grant docket entries, each one the reply on a case carrying
        # committed merits cells.
        "Reply of petitioner Michael Salazar filed.",
        "Reply of petitioners Winston R. Anderson, et al. filed.",
        "Reply of petitioner Floyd Johnson filed.  (Distributed)",
        # The Clerk's other shapes: the collective caption, the unnamed party,
        # and the "Reply Brief" spelling.
        "Reply of Federal Petitioners filed.  VIDED. (Distributed)",
        "Reply of petitioner filed.  (Distributed)",
        "Reply Brief of petitioner Acme Corp. filed. (Distributed)",
    ],
)
def test_the_petitioners_reply_is_read_from_its_entry(text: str) -> None:
    assert is_petitioner_merits_reply(text)
    assert not is_respondent_merits_reply(text)


def test_the_respondents_reply_is_read_on_the_same_terms() -> None:
    # The rarer side — a cross-petition, or a judgment the Court appointed an
    # amicus to defend — read rather than left out, so neither side is reached
    # more loosely than the other.
    text = "Reply of respondent New Jersey Transit Corporation filed.  VIDED. (Distributed)"
    assert is_respondent_merits_reply(text)
    assert not is_petitioner_merits_reply(text)


@pytest.mark.parametrize(
    "text",
    [
        # A reply on a collateral motion is not merits advocacy. The unpartied
        # forms fall outside the anchor; the partied one satisfies it word for
        # word and is excluded explicitly, because each arm closes on its first
        # match and a motion reply would take the side's slot from its real one.
        "Reply on motion to intervene filed. (Distributed)",
        "Reply in support of motion of Missouri, et al. to intervene filed.",
        "Reply of petitioners in support of motion for divided argument filed.",
        "Reply of respondent in support of motion to expedite consideration filed.",
        "Reply of petitioner in support of application for a stay filed.",
        # Recorded under counsel's own name rather than a party's — unreachable by
        # any party-word anchor, and left unfetched rather than guessed at.
        "Reply of AT&T, Inc. and Verizon Communications Inc. filed (April 13, 2026).",
        "Reply letter (No. 21-1596) filed.",
        # A party replying in support of its opponent is real advocacy, but not
        # that side's own — excluded on the same reading its brief is.
        "Reply of respondent United States in support of petitioner filed.",
        # And the amicus, which the anchor refuses before any exclusion is read.
        "Reply brief amicus curiae of Cato Institute filed.",
    ],
)
def test_entries_that_are_not_a_sides_own_merits_reply(text: str) -> None:
    assert not is_petitioner_merits_reply(text)
    assert not is_respondent_merits_reply(text)


def test_the_opening_brief_and_the_reply_are_never_the_same_entry() -> None:
    # The four predicates are four arms of one chain in the document selector, so
    # no entry may satisfy two of them.
    for text in (
        "Brief of petitioner Floyd Johnson filed.",
        "Brief of respondent United States filed.",
        "Reply of petitioner Floyd Johnson filed.",
        "Reply of respondent New Jersey Transit Corporation filed.",
    ):
        matched = [
            is_petitioner_merits_brief(text),
            is_respondent_merits_brief(text),
            is_petitioner_merits_reply(text),
            is_respondent_merits_reply(text),
        ]
        assert sum(matched) == 1


def test_the_confession_of_error_reply_is_still_a_reply() -> None:
    # "in support of reversal" / "in support of vacatur" is a respondent agreeing
    # with the petitioner on the outcome — real merits advocacy, and not the
    # collateral-motion shape the exclusion above is aimed at.
    for text in (
        "Reply of respondents in support of reversal filed.",
        "Reply of respondent United States in support of vacatur filed.",
    ):
        assert is_respondent_merits_reply(text)


def test_a_reply_carries_no_merits_moment() -> None:
    # The milestone this module dates is the respondent's opening brief; a reply
    # is a document the selector fetches, never a moment.
    payload = _docket(
        ("Mar 4 2025", "Petition GRANTED."),
        ("Jun 2 2025", "Reply of respondent Penny Clarkston filed."),
    )
    assert respondent_brief_date(payload, granted_on=GRANT) is None
