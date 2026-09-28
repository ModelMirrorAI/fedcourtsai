"""Who is asking, and what each action does for them (:mod:`fedcourtsai.asking_party`).

Every caption below is a real `event.yaml` title from the committed ledger,
except the contradicting-label cases, which move a real caption's label to the
wrong side. Docket numbers are the committed ones where committed data carries
one, and illustrative where a test needs a form it lacks. A decline pinned here
is a claim that the rule refuses that caption, not a failure to reach it.
"""

import pytest

from fedcourtsai.asking_party import (
    AskingSides,
    asking_sides,
    caption_heads,
    outcome_lines,
)
from fedcourtsai.schemas import Stage
from fedcourtsai.short_caption import AGENCY_ACRONYMS


def _sides(
    caption: str,
    *,
    docket_number: str | None = None,
    stage: Stage | None = Stage.cert,
    mirrored: bool = False,
    court_id: str = "scotus",
) -> AskingSides | str:
    return asking_sides(
        caption,
        court_id=court_id,
        docket_number=docket_number,
        stage=stage,
        mirrored=mirrored,
    )


@pytest.mark.parametrize(
    ("caption", "asking", "other"),
    [
        ("United States v. E. Jean Carroll, et al.", "United States", "Carroll"),
        (
            "Donald J. Trump, President of the United States, et al. v. California, et al.",
            "Trump",
            "California",
        ),
        ("Apple Inc. v. Epic Games, Inc.", "Apple", "Epic Games"),
        ("Raymond Poore v. United States", "Poore", "United States"),
        (
            "Federal Trade Commission, et al. v. National Horsemen's Benevolent and "
            + "Protective Association, et al.",
            "FTC",
            "National Horsemen's Benevolent and Protective Association",
        ),
        # A label the caption still carries is read, and agrees with the order.
        (
            "National Republican Congressional Committee, et al. Applicants v. "
            + "Sherrod Brown, et al.",
            "National Republican Congressional Committee",
            "Brown",
        ),
        (
            "Mark Crawford, et al., Petitioners v. Department of the Treasury, et al.",
            "Crawford",
            "Department of the Treasury",
        ),
        (
            "Benancio Garcia, III, Appellant v. Steven Hobbs, Secretary of State of "
            + "Washington, et al.",
            "Garcia",
            "Hobbs",
        ),
    ],
)
def test_the_first_named_side_is_the_one_asking(caption: str, asking: str, other: str) -> None:
    assert _sides(caption) == AskingSides(asking=asking, other=other)


@pytest.mark.parametrize(
    ("caption", "kwargs", "declined"),
    [
        # Mandamus or prohibition: one side only.
        ("In Re Richard Devillier, et al.", {}, "in_re"),
        ("In Re Curt Gilgenbach, et ux., Petitioners", {}, "in_re"),
        # The short-caption rule cannot name a side.
        (
            "Markwayne Mullin, Secretary of Homeland Security, et al. v. Refugee and "
            + "Immigrant Center for Education and Legal Services, et al.",
            {},
            "short_form",
        ),
        (
            "Katherine L. Hobbins Forester, et al. v. Adam Gerol, et al.",
            {"stage": Stage.interim},
            "short_form",
        ),
        # Two sides with one short name: a line could not tell them apart.
        ("Ronald Dittmer, et ux. v. Katie Dittmer", {}, "short_form"),
        # A sovereign against a sovereign with no docket number: the ACA
        # cross-petitions, which decline here before the mirror is consulted.
        ("Texas, et al., Petitioners v. California, et al.", {}, "original_jurisdiction"),
        # An original docket number declines whatever the caption says.
        (
            "Texas, et al., Petitioners v. California, et al.",
            {"docket_number": "22O153"},
            "original_jurisdiction",
        ),
        (
            "Apple Inc. v. Epic Games, Inc.",
            {"docket_number": "158, Orig."},
            "original_jurisdiction",
        ),
        # The Epic Games / Apple cross-petitions, each mirrored by the other.
        ("Epic Games, Inc., Petitioner v. Apple Inc.", {"mirrored": True}, "cross_petition"),
        ("Apple Inc., Petitioner v. Epic Games, Inc.", {"mirrored": True}, "cross_petition"),
        # Labels that contradict the order, or a cross-petitioner label.
        ("Apple Inc., Respondent v. Epic Games, Inc., Petitioner", {}, "docket_labels"),
        ("Apple Inc., Cross-Petitioner v. Epic Games, Inc.", {}, "docket_labels"),
        # A moment with no registered stage.
        ("Apple Inc. v. Epic Games, Inc.", {"stage": None}, "stage"),
        ("", {}, "no_caption"),
        ("Apple Inc. v. Epic Games, Inc.", {"court_id": "ca9"}, "not_scotus"),
        ("Apple Inc. v. Epic Games, Inc. v. Google LLC", {}, "not_two_sided"),
    ],
)
def test_the_rule_declines_where_the_caption_cannot_carry_the_answer(
    caption: str, kwargs: dict[str, object], declined: str
) -> None:
    assert _sides(caption, **kwargs) == declined  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("caption", "docket_number", "stage", "asking", "other"),
    [
        # A petition number is never original, whoever the parties are.
        ("Texas v. United States", "22-58", Stage.cert, "Texas", "United States"),
        # Nor is an application number: the Alabama v. California stay application,
        # and a United States v. State application.
        (
            "Alabama, et al. v. California, et al.",
            "26A139",
            Stage.interim,
            "Alabama",
            "California",
        ),
        (
            "United States, Petitioner v. Texas, et al.",
            "23A607",
            Stage.interim,
            "United States",
            "Texas",
        ),
    ],
)
def test_a_sovereign_pair_on_a_petition_or_application_number_is_read_as_any_other(
    caption: str, docket_number: str, stage: Stage, asking: str, other: str
) -> None:
    assert _sides(caption, docket_number=docket_number, stage=stage) == AskingSides(
        asking=asking, other=other
    )


def test_caption_heads_strip_labels_and_keep_whole_names() -> None:
    assert caption_heads("Epic Games, Inc., Petitioner v. Apple Inc.") == (
        "epic games",
        "apple inc.",
    )
    assert caption_heads("Apple Inc. v. Epic Games, Inc.") == ("apple inc.", "epic games")
    # Two different people who share a surname are two different heads.
    assert caption_heads("Martin Mizrahi v. United States") != caption_heads(
        "Sara Mizrahi v. United States"
    )
    assert caption_heads("In Re Joan Farr") is None


def _lines(stage: Stage, asking: str, other: str) -> dict[str, tuple[str, str]]:
    return {
        action: (side, line)
        for action, side, line in outcome_lines(stage, AskingSides(asking=asking, other=other))
    }


def test_petition_lines_say_a_grant_decides_nothing_and_a_denial_is_no_ruling() -> None:
    assert _lines(Stage.cert, "United States", "Carroll") == {
        "granted": (
            "granted",
            "The Court takes up the United States' case; "
            "a grant alone decides nothing yet about who is right.",
        ),
        "denied": (
            "not-granted",
            "The United States' petition ends and the lower court's decision stands; "
            "that is not a ruling that the lower court was right.",
        ),
    }


def test_application_lines_are_temporary_relief() -> None:
    assert _lines(Stage.interim, "Trump", "California") == {
        "granted": (
            "granted",
            "Trump gets the relief requested, for now; the case continues in the lower courts.",
        ),
        "denied": (
            "not-granted",
            "Trump does not get the relief requested, for now; things stay as the lower "
            "courts left them while the case continues.",
        ),
    }


def test_merits_lines_pair_by_side_not_one_to_one() -> None:
    lines = _lines(Stage.merits, "Department of Labor", "Sun Valley Orchards")
    assert list(lines) == ["reversed", "affirmed", "vacated"]
    # Reversal and vacatur both sit on the disturbed side of P(disturbed).
    assert {action: side for action, (side, _) in lines.items()} == {
        "reversed": "disturbed",
        "affirmed": "undisturbed",
        "vacated": "disturbed",
    }
    assert lines["reversed"][1] == (
        "The Department of Labor wins in the Court; the lower court's decision is "
        "overturned, and any remaining issues go back to it."
    )
    assert lines["affirmed"][1] == (
        "Sun Valley Orchards wins in the Court; the lower court's decision is upheld."
    )
    assert lines["vacated"][1] == (
        "The lower court's decision is set aside and the case goes back to it, "
        "without the Court deciding it for either side."
    )


@pytest.mark.parametrize("stage", list(Stage))
def test_every_stage_has_lines_and_none_speaks_of_likelihood(stage: Stage) -> None:
    lines = outcome_lines(stage, AskingSides(asking="Apple", other="Epic Games"))
    assert lines
    for _, _, line in lines:
        lowered = line.lower()
        assert not any(word in lowered for word in ("likely", "probab", "chance", "expect"))


@pytest.mark.parametrize(
    ("party", "expected"),
    [
        ("Republican National Committee", "The Republican National Committee wins"),
        ("City of Cleveland", "The City of Cleveland wins"),
        ("National Association for Gun Rights", "The National Association for Gun Rights wins"),
        ("National Veterans Legal Services Program", "The National Veterans Legal Services"),
        ("Cook County", "Cook County wins"),
        ("Walmart", "Walmart wins"),
        ("Texas", "Texas wins"),
        ("Humphreys", "Humphreys wins"),
        # A company whose name carries an "of" phrase is still a company.
        ("Unum Life Insurance Company of America", "Unum Life Insurance Company of America wins"),
    ],
)
def test_an_institution_takes_an_article_and_a_person_or_company_does_not(
    party: str, expected: str
) -> None:
    assert _lines(Stage.merits, party, "Other")["reversed"][1].startswith(expected)


@pytest.mark.parametrize("acronym", sorted(AGENCY_ACRONYMS.values()))
def test_an_agency_acronym_takes_an_article(acronym: str) -> None:
    lines = _lines(Stage.cert, acronym, "Other")
    assert lines["granted"][1].startswith(f"The Court takes up the {acronym}'s case")
    assert lines["denied"][1].startswith(f"The {acronym}'s petition ends")
