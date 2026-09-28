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
        # A sovereign against a sovereign on an application number.
        (
            "Alabama, et al. v. California, et al.",
            {"docket_number": "26A139", "stage": Stage.interim},
            "original_jurisdiction",
        ),
        # The same shape with no docket number: the ACA cross-petitions, which
        # decline here before the mirror is consulted.
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


def test_a_sovereign_pair_on_a_term_form_petition_number_is_a_cert_case() -> None:
    assert _sides("Texas v. United States", docket_number="22-58") == AskingSides(
        asking="Texas", other="United States"
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


def _lines(stage: Stage, asking: str, other: str) -> dict[str, str]:
    return dict(outcome_lines(stage, AskingSides(asking=asking, other=other)))


def test_petition_lines_name_both_sides_and_say_a_grant_decides_nothing() -> None:
    assert _lines(Stage.cert, "United States", "Carroll") == {
        "granted": "The Court agrees to hear the United States' case; "
        "that decides nothing yet about who is right.",
        "denied": "Carroll's win in the lower court stands; "
        "that is not a ruling that the lower court was right.",
    }


def test_application_lines_are_temporary_relief() -> None:
    assert _lines(Stage.interim, "Trump", "California") == {
        "granted": "Trump gets the relief requested, for now; the case continues in the "
        "lower courts.",
        "denied": "Trump does not get the relief requested; the lower court's order stays in "
        "effect while the case continues.",
    }


def test_merits_lines_cover_reversal_affirmance_and_vacatur() -> None:
    lines = _lines(Stage.merits, "Department of Labor", "Sun Valley Orchards")
    assert list(lines) == ["reversed", "affirmed", "vacated"]
    assert lines["reversed"] == (
        "The Department of Labor wins in the Court; the lower court's decision is overturned."
    )
    assert lines["affirmed"] == (
        "Sun Valley Orchards wins in the Court; the lower court's decision is upheld."
    )
    assert "without either side winning yet" in lines["vacated"]


@pytest.mark.parametrize("stage", list(Stage))
def test_every_stage_has_lines_and_none_speaks_of_likelihood(stage: Stage) -> None:
    lines = outcome_lines(stage, AskingSides(asking="Apple", other="Epic Games"))
    assert lines
    for _, line in lines:
        lowered = line.lower()
        assert not any(word in lowered for word in ("likely", "probab", "chance", "expect"))


@pytest.mark.parametrize(
    ("party", "expected"),
    [
        ("Republican National Committee", "The Republican National Committee wins"),
        ("City of Cleveland", "The City of Cleveland wins"),
        ("Cook County", "Cook County wins"),
        ("Walmart", "Walmart wins"),
        ("Texas", "Texas wins"),
        ("Humphreys", "Humphreys wins"),
    ],
)
def test_an_institution_takes_an_article_and_a_person_or_company_does_not(
    party: str, expected: str
) -> None:
    lines = _lines(Stage.merits, party, "Other")
    assert lines["reversed"].startswith(expected)
