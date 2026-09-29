"""The SCOTUS syllabus lineup grammar and the lineup model it reads into.

Every fixture is a lineup paragraph as the syllabus prints it, written out as
text: the grammar reads text a fetching channel has already located, so no
test here touches an opinion PDF or the network.
"""

from __future__ import annotations

import pytest

from fedcourtsai.pipeline.lineup import (
    Join,
    Lineup,
    LineupGrammar,
    Writing,
    WritingKind,
    lineup_from_writings,
)
from fedcourtsai.pipeline.syllabus_lineup import (
    GRAMMAR_NAME,
    GRAMMAR_VERSION,
    SCOTUS_SYLLABUS,
    normalize_lineup_text,
    parse_syllabus_lineup,
)
from fedcourtsai.schemas import VoteValue

OT23 = (
    "Roberts",
    "Thomas",
    "Alito",
    "Sotomayor",
    "Kagan",
    "Gorsuch",
    "Kavanaugh",
    "Barrett",
    "Jackson",
)
OT21 = (
    "Roberts",
    "Thomas",
    "Breyer",
    "Alito",
    "Sotomayor",
    "Kagan",
    "Gorsuch",
    "Kavanaugh",
    "Barrett",
)
OT19 = (
    "Roberts",
    "Thomas",
    "Ginsburg",
    "Breyer",
    "Alito",
    "Sotomayor",
    "Kagan",
    "Gorsuch",
    "Kavanaugh",
)
OT17 = (
    "Roberts",
    "Kennedy",
    "Thomas",
    "Ginsburg",
    "Breyer",
    "Alito",
    "Sotomayor",
    "Kagan",
    "Gorsuch",
)

M = VoteValue.majority
D = VoteValue.dissent
CJ = VoteValue.concur_in_judgment
MIXED = VoteValue.concur_in_part
OUT = VoteValue.did_not_participate


def _votes(lineup: Lineup) -> dict[str, VoteValue]:
    return dict(lineup.votes)


def _writing(lineup: Lineup, author: str, kind: WritingKind) -> Writing:
    return next(w for w in lineup.writings if w.author == author and w.kind is kind)


def _assert_refused(lineup: Lineup) -> None:
    """An unreadable paragraph: incomplete, no votes, and a reason given."""
    assert not lineup.complete
    assert not lineup.writings_complete
    assert lineup.participating is None
    assert dict(lineup.votes) == {}
    assert lineup.problems


# --- unanimity -------------------------------------------------------------


def test_a_unanimous_court_accounts_for_every_justice() -> None:
    lineup = parse_syllabus_lineup(
        "SOTOMAYOR, J., delivered the opinion for a unanimous Court.", bench=OT23
    )
    assert lineup.complete and lineup.writings_complete
    assert lineup.problems == ()
    assert _votes(lineup) == dict.fromkeys(OT23, M)
    assert lineup.participating == 9
    lead = lineup.lead
    assert lead is not None
    assert lead.kind is WritingKind.opinion_of_the_court
    assert lead.author == "Sotomayor"
    assert lead.joiners == frozenset(OT23) - {"Sotomayor"}
    assert all(not join.partial for join in lead.joins)


def test_a_fully_listed_joiner_roll_with_a_concurrence_is_unanimous_on_the_vote() -> None:
    lineup = parse_syllabus_lineup(
        "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "THOMAS, ALITO, SOTOMAYOR, GORSUCH, KAVANAUGH, BARRETT, and JACKSON, JJ., "
        "joined. GORSUCH, J., filed a concurring opinion.",
        bench=OT23,
    )
    assert lineup.complete
    assert _votes(lineup) == dict.fromkeys(OT23, M)
    assert lineup.writing_roles["Gorsuch"] == (WritingKind.concurrence,)
    assert lineup.writing_roles["Kagan"] == (WritingKind.opinion_of_the_court,)
    # Writings are complete, so a Justice who wrote nothing is observed so.
    assert lineup.writing_roles["Alito"] == ()


def test_all_other_members_with_a_recusal_in_the_lead_sentence() -> None:
    lineup = parse_syllabus_lineup(
        "KAVANAUGH, J., delivered the opinion of the Court, in which all other Members "
        "joined, except JACKSON, J., who took no part in the consideration or decision "
        "of the case.",
        bench=OT23,
    )
    assert lineup.complete
    assert _votes(lineup) == {**dict.fromkeys(OT23, M), "Jackson": OUT}
    assert lineup.participating == 8
    assert "Jackson" not in lineup.writing_roles


# --- divided Courts --------------------------------------------------------


def test_five_four_with_several_concurrences_and_dissents() -> None:
    lineup = parse_syllabus_lineup(
        "GORSUCH, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "THOMAS, ALITO, and KAVANAUGH, JJ., joined. THOMAS, J., filed a concurring "
        "opinion. KAVANAUGH, J., filed a concurring opinion, in which ALITO, J., "
        "joined. KAGAN, J., filed a dissenting opinion, in which SOTOMAYOR and "
        "JACKSON, JJ., joined. BARRETT, J., filed a dissenting opinion.",
        bench=OT23,
    )
    assert lineup.complete
    assert _votes(lineup) == {
        "Roberts": M,
        "Thomas": M,
        "Alito": M,
        "Sotomayor": D,
        "Kagan": D,
        "Gorsuch": M,
        "Kavanaugh": M,
        "Barrett": D,
        "Jackson": D,
    }
    kavanaugh = _writing(lineup, "Kavanaugh", WritingKind.concurrence)
    assert kavanaugh.joins == (Join("Alito"),)
    dissent = _writing(lineup, "Kagan", WritingKind.dissent)
    assert dissent.joiners == {"Sotomayor", "Jackson"}
    assert lineup.writing_roles["Barrett"] == (WritingKind.dissent,)
    assert lineup.writing_roles["Roberts"] == ()


def test_a_joint_dissent_and_a_concurrence_in_the_judgment() -> None:
    """A six-three judgment on a five-Justice opinion, with one jointly written dissent."""
    lineup = parse_syllabus_lineup(
        "ALITO, J., delivered the opinion of the Court, in which THOMAS, GORSUCH, "
        "KAVANAUGH, and BARRETT, JJ., joined. THOMAS, J., and KAVANAUGH, J., filed "
        "concurring opinions. ROBERTS, C. J., filed an opinion concurring in the "
        "judgment. BREYER, SOTOMAYOR, and KAGAN, JJ., filed a dissenting opinion.",
        bench=OT21,
    )
    assert lineup.complete
    assert _votes(lineup) == {
        "Roberts": CJ,
        "Thomas": M,
        "Breyer": D,
        "Alito": M,
        "Sotomayor": D,
        "Kagan": D,
        "Gorsuch": M,
        "Kavanaugh": M,
        "Barrett": M,
    }
    joint = _writing(lineup, "Breyer", WritingKind.dissent)
    assert joint.authors == ("Breyer", "Sotomayor", "Kagan")
    assert joint.joins == ()
    # Each co-author wrote the dissent; none of them merely joined it.
    for justice in ("Breyer", "Sotomayor", "Kagan"):
        assert lineup.writing_roles[justice] == (WritingKind.dissent,)
    # The plural sentence is two writings, one each.
    assert lineup.writing_roles["Thomas"] == (WritingKind.concurrence,)
    assert lineup.writing_roles["Kavanaugh"] == (WritingKind.concurrence,)


def test_joins_of_a_separate_opinion_in_part() -> None:
    lineup = parse_syllabus_lineup(
        "ALITO, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "THOMAS, GORSUCH, KAVANAUGH, and BARRETT, JJ., joined. BARRETT, J., filed a "
        "concurring opinion, in which THOMAS and GORSUCH, JJ., joined as to Part II\u2013B. "
        "SOTOMAYOR, J., filed a dissenting opinion, in which KAGAN and JACKSON, JJ., "
        "joined.",
        bench=OT23,
    )
    assert lineup.complete
    concurrence = _writing(lineup, "Barrett", WritingKind.concurrence)
    assert concurrence.joins == (
        Join("Thomas", "as to Part II\u2013B"),
        Join("Gorsuch", "as to Part II\u2013B"),
    )
    assert all(join.partial for join in concurrence.joins)
    # Joining part of a concurrence does not move a Justice off the majority.
    assert lineup.votes["Thomas"] is M


def test_a_dissent_joined_in_full_by_some_and_in_part_by_another() -> None:
    lineup = parse_syllabus_lineup(
        "KAVANAUGH, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "THOMAS, ALITO, and BARRETT, JJ., joined. GORSUCH, J., filed a dissenting "
        "opinion, in which SOTOMAYOR, J., joined as to Parts I and II. KAGAN, J., filed "
        "a dissenting opinion, in which SOTOMAYOR and JACKSON, JJ., joined, and in "
        "which GORSUCH, J., joined as to Part I.",
        bench=OT23,
    )
    assert lineup.complete
    kagan = _writing(lineup, "Kagan", WritingKind.dissent)
    assert kagan.joins == (
        Join("Sotomayor"),
        Join("Jackson"),
        Join("Gorsuch", "as to Part I"),
    )
    assert {j: lineup.votes[j] for j in ("Gorsuch", "Sotomayor", "Kagan", "Jackson")} == (
        dict.fromkeys(("Gorsuch", "Sotomayor", "Kagan", "Jackson"), D)
    )


# --- split and scoped lead opinions ----------------------------------------


def test_the_opinion_of_the_court_except_as_to_a_part() -> None:
    lineup = parse_syllabus_lineup(
        "GORSUCH, J., delivered the opinion of the Court, except as to Part III\u2013B. "
        "ROBERTS, C. J., and THOMAS, ALITO, and KAVANAUGH, JJ., joined that opinion in "
        "full, and BARRETT, J., joined except as to Part III\u2013B. KAGAN, J., filed a "
        "dissenting opinion, in which SOTOMAYOR and JACKSON, JJ., joined.",
        bench=OT23,
    )
    assert lineup.complete
    lead = lineup.lead
    assert lead is not None and lead.author == "Gorsuch"
    assert lead.scope == "the opinion of the Court except as to Part III\u2013B"
    assert lead.joins == (
        Join("Roberts"),
        Join("Thomas"),
        Join("Alito"),
        Join("Kavanaugh"),
        Join("Barrett", "except as to Part III\u2013B"),
    )
    assert lineup.votes["Barrett"] is M
    assert [lineup.votes[j] for j in ("Sotomayor", "Kagan", "Jackson")] == [D, D, D]


def test_split_form_joiners_separated_by_a_semicolon() -> None:
    lineup = parse_syllabus_lineup(
        "BREYER, J., delivered the opinion of the Court, except as to Part II\u2013C. "
        "ROBERTS, C. J., and GINSBURG, SOTOMAYOR, and KAGAN, JJ., joined that opinion "
        "in full; KAVANAUGH, J., joined except as to Part II\u2013C. THOMAS, J., filed a "
        "dissenting opinion, in which ALITO and GORSUCH, JJ., joined.",
        bench=OT19,
    )
    assert lineup.complete
    lead = lineup.lead
    assert lead is not None
    assert Join("Kavanaugh", "except as to Part II\u2013C") in lead.joins
    assert lineup.votes["Kavanaugh"] is M
    assert lineup.votes["Gorsuch"] is D


def test_a_scoped_lead_with_a_plurality_part_and_a_partial_concurrence() -> None:
    lineup = parse_syllabus_lineup(
        "ROBERTS, C. J., delivered the opinion of the Court with respect to Parts I, "
        "II, and III\u2013A, in which THOMAS, ALITO, GORSUCH, and KAVANAUGH, JJ., joined, "
        "and an opinion with respect to Part III\u2013B, in which THOMAS and KAVANAUGH, "
        "JJ., joined. BARRETT, J., filed an opinion concurring in part and concurring "
        "in the judgment. SOTOMAYOR, J., filed a dissenting opinion, in which KAGAN "
        "and JACKSON, JJ., joined.",
        bench=OT23,
    )
    assert lineup.complete
    lead = lineup.lead
    assert lead is not None
    assert lead.kind is WritingKind.opinion_of_the_court
    joins = {join.justice: join.qualifier for join in lead.joins}
    # Joined every clause: in full. Joined only the Court's parts: qualified.
    assert joins["Thomas"] is None
    assert joins["Kavanaugh"] is None
    assert joins["Alito"] == "with respect to Parts I, II, and III\u2013A"
    assert joins["Gorsuch"] == "with respect to Parts I, II, and III\u2013A"
    # Concurring in part and in the judgment is a vote with the majority.
    assert lineup.votes["Barrett"] is M
    assert lineup.writing_roles["Barrett"] == (WritingKind.concurrence_in_part,)
    assert [lineup.votes[j] for j in ("Sotomayor", "Kagan", "Jackson")] == [D, D, D]


def test_a_court_clause_without_its_own_joiners_was_joined_by_the_rest() -> None:
    """The Court lists joiners only where fewer than all joined."""
    lineup = parse_syllabus_lineup(
        "BARRETT, J., delivered the opinion of the Court with respect to Parts I, II, "
        "and III, and an opinion with respect to Part IV, in which ROBERTS, C. J., and "
        "KAVANAUGH, J., joined. THOMAS, J., filed an opinion concurring in part and "
        "concurring in the judgment. JACKSON, J., filed a dissenting opinion.",
        bench=OT23,
    )
    assert lineup.complete
    lead = lineup.lead
    assert lead is not None
    joins = {join.justice: join.qualifier for join in lead.joins}
    assert joins["Roberts"] is None and joins["Kavanaugh"] is None
    for justice in ("Alito", "Sotomayor", "Kagan", "Gorsuch"):
        assert joins[justice] == "with respect to Parts I, II, and III"
    # The partial concurrer and the dissenter are not credited to the lead.
    assert "Thomas" not in joins and "Jackson" not in joins
    assert lineup.votes["Thomas"] is M
    assert lineup.votes["Jackson"] is D


def test_a_plurality_with_a_concurrence_in_the_judgment() -> None:
    lineup = parse_syllabus_lineup(
        "BREYER, J., announced the judgment of the Court and delivered an opinion, in "
        "which GINSBURG, SOTOMAYOR, and KAGAN, JJ., joined. ROBERTS, C. J., filed an "
        "opinion concurring in the judgment. THOMAS, J., filed a dissenting opinion. "
        "ALITO, J., filed a dissenting opinion, in which GORSUCH, J., joined, and in "
        "which THOMAS and KAVANAUGH, JJ., joined as to Parts I, II, III, and IV\u2013F. "
        "GORSUCH, J., filed a dissenting opinion. KAVANAUGH, J., filed a dissenting "
        "opinion.",
        bench=OT19,
    )
    assert lineup.complete
    lead = lineup.lead
    assert lead is not None and lead.kind is WritingKind.plurality
    assert lead.joiners == {"Ginsburg", "Sotomayor", "Kagan"}
    assert _votes(lineup) == {
        "Roberts": CJ,
        "Thomas": D,
        "Ginsburg": M,
        "Breyer": M,
        "Alito": D,
        "Sotomayor": M,
        "Kagan": M,
        "Gorsuch": D,
        "Kavanaugh": D,
    }
    alito = _writing(lineup, "Alito", WritingKind.dissent)
    assert Join("Kavanaugh", "as to Parts I, II, III, and IV\u2013F") in alito.joins


# --- separate-writing kinds ------------------------------------------------


def test_concurring_in_part_and_dissenting_in_part() -> None:
    lineup = parse_syllabus_lineup(
        "KENNEDY, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "THOMAS, ALITO, and GORSUCH, JJ., joined. BREYER, J., filed an opinion "
        "concurring in part and dissenting in part, in which GINSBURG, SOTOMAYOR, and "
        "KAGAN, JJ., joined.",
        bench=OT17,
    )
    assert lineup.complete
    for justice in ("Breyer", "Ginsburg", "Sotomayor", "Kagan"):
        assert lineup.votes[justice] is MIXED
    assert lineup.writing_roles["Breyer"] == (WritingKind.concurrence_in_part_dissent_in_part,)


def test_joining_the_court_and_a_dissent_in_part_is_both_sides() -> None:
    lineup = parse_syllabus_lineup(
        "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "SOTOMAYOR, KAVANAUGH, BARRETT, and JACKSON, JJ., joined, and in which ALITO, "
        "J., joined as to Parts I and II. ALITO, J., filed an opinion concurring in "
        "part and dissenting in part. THOMAS, J., filed a dissenting opinion, in "
        "which GORSUCH, J., joined.",
        bench=OT23,
    )
    assert lineup.complete
    assert lineup.votes["Alito"] is MIXED
    assert lineup.votes["Thomas"] is D and lineup.votes["Gorsuch"] is D


def test_concurring_in_the_judgment_alone() -> None:
    lineup = parse_syllabus_lineup(
        "THOMAS, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "ALITO, SOTOMAYOR, KAGAN, KAVANAUGH, BARRETT, and JACKSON, JJ., joined. "
        "GORSUCH, J., filed an opinion concurring in the judgment.",
        bench=OT23,
    )
    assert lineup.complete
    assert lineup.votes["Gorsuch"] is CJ
    assert lineup.writing_roles["Gorsuch"] == (WritingKind.concurrence_in_judgment,)


# --- per curiam and non-participation --------------------------------------


def test_a_per_curiam_speaks_for_everyone_not_writing_separately_against_it() -> None:
    lineup = parse_syllabus_lineup(
        "PER CURIAM. THOMAS, J., filed an opinion concurring in the judgment. "
        "SOTOMAYOR, J., filed a dissenting opinion, in which KAGAN and JACKSON, JJ., "
        "joined.",
        bench=OT23,
    )
    assert lineup.complete
    lead = lineup.lead
    assert lead is not None
    assert lead.kind is WritingKind.per_curiam
    assert lead.author is None
    assert lead.joiners == {"Roberts", "Alito", "Gorsuch", "Kavanaugh", "Barrett"}
    assert lineup.votes["Thomas"] is CJ
    assert [lineup.votes[j] for j in ("Sotomayor", "Kagan", "Jackson")] == [D, D, D]
    assert lineup.votes["Roberts"] is M
    # Nobody authors a per curiam, so it is no Justice's writing role.
    assert lineup.writing_roles["Roberts"] == ()


def test_a_recusal_sentence_leaves_an_eight_member_court_complete() -> None:
    lineup = parse_syllabus_lineup(
        "SOTOMAYOR, J., delivered the opinion of the Court, in which ROBERTS, C. J., "
        "and THOMAS, ALITO, GORSUCH, KAVANAUGH, BARRETT, and JACKSON, JJ., joined. "
        "KAGAN, J., took no part in the consideration or decision of the case.",
        bench=OT23,
    )
    assert lineup.complete
    assert lineup.votes["Kagan"] is OUT
    assert lineup.participating == 8
    assert "Kagan" not in lineup.writing_roles


def test_non_participation_in_an_eight_member_term_with_an_unseated_justice() -> None:
    """A Justice seated after argument is the syllabus's to exclude, or the bench's."""
    lineup = parse_syllabus_lineup(
        "GINSBURG, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "KENNEDY, BREYER, SOTOMAYOR, and KAGAN, JJ., joined. THOMAS, J., filed a "
        "dissenting opinion, in which ALITO, J., joined. GORSUCH, J., took no part in "
        "the consideration or decision of the case.",
        bench=OT17,
    )
    assert lineup.complete
    assert lineup.participating == 8
    assert lineup.votes["Gorsuch"] is OUT


# --- names -----------------------------------------------------------------


def test_compound_and_full_names_resolve_to_the_roster_surname() -> None:
    full = parse_syllabus_lineup(
        "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "THOMAS, ALITO, SOTOMAYOR, GORSUCH, KAVANAUGH, and BARRETT, JJ., joined. "
        "KETANJI BROWN JACKSON, J., filed a dissenting opinion.",
        bench=OT23,
    )
    short = parse_syllabus_lineup(
        "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "THOMAS, ALITO, SOTOMAYOR, GORSUCH, KAVANAUGH, and BARRETT, JJ., joined. "
        "JACKSON, J., filed a dissenting opinion.",
        bench=OT23,
    )
    assert full.complete and short.complete
    assert full.votes == short.votes
    assert full.writing_roles["Jackson"] == (WritingKind.dissent,)


def test_a_multi_token_surname_stays_whole() -> None:
    bench = (
        "Hughes",
        "Van Devanter",
        "McReynolds",
        "Brandeis",
        "Sutherland",
        "Butler",
        "Stone",
        "Roberts",
        "Cardozo",
    )
    with pytest.raises(ValueError, match="roster"):
        # The roster carries the modern span plus the one compound surname,
        # so the rest of this bench is unknown; the bench is an input, and an
        # unknown name in it is refused outright.
        parse_syllabus_lineup("PER CURIAM.", bench=bench)
    lineup = parse_syllabus_lineup(
        "ROBERTS, C. J., delivered the opinion of the Court, in which THOMAS, ALITO, "
        "SOTOMAYOR, KAGAN, GORSUCH, KAVANAUGH, and BARRETT, JJ., joined. VAN DEVANTER, "
        "J., filed a dissenting opinion.",
        bench=(*OT23[:-1], "Van Devanter"),
    )
    assert lineup.complete
    assert lineup.votes["Van Devanter"] is D


def test_an_apostrophe_in_either_form_resolves() -> None:
    bench = (
        "Rehnquist",
        "Stevens",
        "O'Connor",
        "Scalia",
        "Kennedy",
        "Souter",
        "Thomas",
        "Ginsburg",
        "Breyer",
    )
    lineup = parse_syllabus_lineup(
        "O\u2019CONNOR, J., delivered the opinion of the Court, in which REHNQUIST, "
        "C. J., and STEVENS, SCALIA, KENNEDY, SOUTER, THOMAS, GINSBURG, and BREYER, "
        "JJ., joined.",
        bench=bench,
    )
    assert lineup.complete
    assert lineup.lead is not None and lineup.lead.author == "O'Connor"


def test_the_bench_is_validated_as_an_input() -> None:
    with pytest.raises(ValueError, match="twice"):
        parse_syllabus_lineup("PER CURIAM.", bench=("Kagan", "kagan"))


# --- the bound-volume text layer --------------------------------------------


def test_mixed_case_volume_text_with_ligature_loss_hyphenation_and_page_cites() -> None:
    lineup = parse_syllabus_lineup(
        "Thomas, J., delivered the opinion of the Court, in which Roberts, C. J., and "
        "Kennedy, Alito, and Gor-\nsuch, JJ., joined. Ginsburg, J., fled a dissenting "
        "opinion, in which Breyer, Sotomayor, and Kagan, JJ., joined, post, p. 128. "
        "Breyer, J., fled a dissenting opin-\nion, post, p. 140.",
        bench=OT17,
    )
    assert lineup.complete
    assert _votes(lineup) == {
        "Roberts": M,
        "Kennedy": M,
        "Thomas": M,
        "Ginsburg": D,
        "Breyer": D,
        "Alito": M,
        "Sotomayor": D,
        "Kagan": D,
        "Gorsuch": M,
    }


def test_normalization_collapses_titles_and_drops_page_cites() -> None:
    text = normalize_lineup_text("Alito, J., fled a con- curring opinion, ante, p. 12.")
    assert text == "Alito § fled a concurring opinion."


# --- refusal ---------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("", id="empty"),
        pytest.param("The judgment of the Court of Appeals is reversed.", id="no-lineup"),
        pytest.param(
            "Held: The statute does not apply. Pp. 4\u201312. 45 F. 4th 678, reversed.",
            id="holding-not-lineup",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
            + "THOMAS, ALITO, SOTOMAYOR, GORSUCH, KAVANAUGH, and BARRETT, JJ., joined. "
            + "JACKSON, J., filed a dissenting opinion, in which nobody else joined "
            + "willingly.",
            id="garbled-join",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
            + "THOMAS, ALITO, SOTOMAYOR, GORSUCH, KAVANAUGH, and BARRETT, JJ., joined. "
            + "SMITH, J., filed a dissenting opinion.",
            id="unknown-name",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court. The Court also noted a "
            + "dissent without saying whose.",
            id="trailing-unreadable-sentence",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., "
            + "joined. ALITO, J., delivered the opinion of the Court.",
            id="two-leads",
        ),
        pytest.param(
            "JACKSON, J., filed an opinion concurring with the spirit of the Court.",
            id="unknown-writing-kind-and-no-lead",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court, in which all other Members "
            + "joined. KAGAN, J., took no part in the consideration or decision of the case.",
            id="author-took-no-part",
        ),
        pytest.param(
            "THOMAS and ALITO, JJ., delivered the opinion of the Court.",
            id="two-lead-authors",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion for a unanimous Court. THOMAS, J., filed a "
            + "dissenting opinion.",
            id="unanimous-and-a-dissent",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court, in which all other Members "
            + "joined. THOMAS, J., filed a dissenting opinion.",
            id="all-others-and-a-dissent",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
            + "THOMAS, ALITO, SOTOMAYOR, GORSUCH, KAVANAUGH, BARRETT, and JACKSON, JJ., "
            + "joined. THOMAS, J., filed a dissenting opinion.",
            id="full-joiner-and-a-dissent",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court, in which all other Members "
            + "joined, and in which THOMAS, J., joined as to Part I. THOMAS, J., filed a "
            + "dissenting opinion.",
            id="joined-twice-and-a-dissent",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court. KAGAN, J., filed a dissenting "
            + "opinion.",
            id="author-dissents-from-own-opinion",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court. THOMAS, J., filed an opinion "
            + "concurring in part.",
            id="bare-concurring-in-part",
        ),
        pytest.param(
            "GORSUCH, J., delivered the opinion of the Court, except as to Part II. "
            + "ROBERTS, C. J., and THOMAS, ALITO, SOTOMAYOR, KAGAN, KAVANAUGH, BARRETT, "
            + "and JACKSON, JJ., joined that opinion in full, and GORSUCH, J., joined "
            + "except as to Part II.",
            id="author-as-follower-joiner",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
            + "THOMAS, THOMAS, ALITO, SOTOMAYOR, GORSUCH, KAVANAUGH, BARRETT, and JACKSON, "
            + "JJ., joined.",
            id="duplicate-lead-joiner",
        ),
        pytest.param(
            "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
            + "ALITO, SOTOMAYOR, GORSUCH, KAVANAUGH, BARRETT, and JACKSON, JJ., joined. "
            + "THOMAS, J., filed a dissenting opinion, in which THOMAS, J., joined.",
            id="self-join-of-a-dissent",
        ),
    ],
)
def test_an_unreadable_paragraph_is_refused_never_guessed(text: str) -> None:
    _assert_refused(parse_syllabus_lineup(text, bench=OT23))


def test_a_bare_lead_reads_as_every_participant_joining() -> None:
    """The Court's convention, and why the caller must deliver the whole paragraph."""
    lineup = parse_syllabus_lineup("KAGAN, J., delivered the opinion of the Court.", bench=OT23)
    assert lineup.complete
    assert _votes(lineup) == dict.fromkeys(OT23, M)


def test_dissenting_in_part_alone_is_both_sides() -> None:
    lineup = parse_syllabus_lineup(
        "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "SOTOMAYOR, GORSUCH, KAVANAUGH, BARRETT, and JACKSON, JJ., joined, and in which "
        "THOMAS and ALITO, JJ., joined as to Part I. THOMAS, J., filed an opinion "
        "dissenting in part, in which ALITO, J., joined.",
        bench=OT23,
    )
    assert lineup.complete
    assert lineup.votes["Thomas"] is MIXED and lineup.votes["Alito"] is MIXED


def test_a_justice_the_explicit_joins_never_place_keeps_the_lineup_incomplete() -> None:
    """Every sentence reads, but one Justice is named nowhere: no inference fills them."""
    lineup = parse_syllabus_lineup(
        "KAGAN, J., delivered the opinion of the Court, in which ROBERTS, C. J., and "
        "THOMAS, ALITO, SOTOMAYOR, GORSUCH, and KAVANAUGH, JJ., joined. JACKSON, J., "
        "filed a dissenting opinion.",
        bench=OT23,
    )
    assert not lineup.complete
    assert lineup.participating is None
    assert "Barrett" not in lineup.votes
    assert lineup.votes["Jackson"] is D
    assert any("Barrett" in problem for problem in lineup.problems)
    # Writing roles stay author-only when they are not known to be complete.
    assert "Barrett" not in lineup.writing_roles
    assert lineup.writing_roles["Jackson"] == (WritingKind.dissent,)


def test_a_court_below_quorum_is_incomplete() -> None:
    lineup = parse_syllabus_lineup(
        "KAGAN, J., delivered the opinion of the Court, in which all other Members "
        "joined. THOMAS, J., took no part in the consideration or decision of the "
        "case. ALITO, J., took no part in the consideration or decision of the case. "
        "GORSUCH, J., took no part in the consideration or decision of the case. "
        "BARRETT, J., took no part in the consideration or decision of the case.",
        bench=OT23,
    )
    assert not lineup.complete
    assert any("quorum" in problem for problem in lineup.problems)


# --- grammar stamp and the model beyond the syllabus -----------------------


def test_every_lineup_carries_the_grammar_stamp() -> None:
    lineup = SCOTUS_SYLLABUS.parse(
        "SOTOMAYOR, J., delivered the opinion for a unanimous Court.", bench=OT23
    )
    assert (lineup.court, lineup.grammar, lineup.grammar_version) == (
        "scotus",
        GRAMMAR_NAME,
        GRAMMAR_VERSION,
    )
    refused = parse_syllabus_lineup("nonsense", bench=OT23)
    assert (refused.grammar, refused.grammar_version) == (GRAMMAR_NAME, GRAMMAR_VERSION)
    grammar: LineupGrammar = SCOTUS_SYLLABUS
    assert (grammar.court, grammar.name, grammar.version) == (
        "scotus",
        GRAMMAR_NAME,
        GRAMMAR_VERSION,
    )


def test_the_model_holds_a_partial_vote_list_beside_complete_writing_roles() -> None:
    """The shape an order-list reading takes: a few noted votes, every writer known.

    Built directly, because no order-list grammar exists yet; this pins that the
    model can say "two votes observed, the rest unobserved" and "every
    participating Justice's writing role observed" at the same time.
    """
    lineup = Lineup(
        court="scotus",
        grammar="test-order-list",
        grammar_version=1,
        bench=OT23,
        writings=(
            Writing(WritingKind.dissent, "Alito", (Join("Gorsuch"),)),
            Writing(WritingKind.statement, "Sotomayor"),
        ),
        votes={"Alito": VoteValue.grant, "Gorsuch": VoteValue.grant, "Barrett": OUT},
        complete=False,
        writings_complete=True,
    )
    assert lineup.participating is None
    assert lineup.writing_roles["Alito"] == (WritingKind.dissent,)
    assert lineup.writing_roles["Sotomayor"] == (WritingKind.statement,)
    assert lineup.writing_roles["Kagan"] == ()
    assert "Barrett" not in lineup.writing_roles
    assert lineup.lead is None


def test_derivation_refuses_a_lineup_without_exactly_one_lead() -> None:
    lineup = lineup_from_writings(
        court="scotus",
        grammar="test",
        grammar_version=1,
        bench=OT23,
        writings=[Writing(WritingKind.dissent, "Jackson")],
        quorum=6,
    )
    _assert_refused(lineup)


def test_derivation_refuses_a_signatory_off_the_bench() -> None:
    lineup = lineup_from_writings(
        court="scotus",
        grammar="test",
        grammar_version=1,
        bench=OT23,
        writings=[Writing(WritingKind.opinion_of_the_court, "Breyer")],
        quorum=6,
    )
    _assert_refused(lineup)
    assert any("Breyer" in problem for problem in lineup.problems)


def test_a_plain_concurrence_without_a_lead_join_places_nobody() -> None:
    """A concurrence alone does not say its author supported the judgment."""
    lineup = lineup_from_writings(
        court="scotus",
        grammar="test",
        grammar_version=1,
        bench=OT23,
        writings=[
            Writing(
                WritingKind.opinion_of_the_court,
                "Kagan",
                tuple(Join(j) for j in OT23 if j not in {"Kagan", "Thomas"}),
            ),
            Writing(WritingKind.concurrence, "Thomas"),
        ],
        quorum=6,
    )
    assert not lineup.complete
    assert "Thomas" not in lineup.votes
