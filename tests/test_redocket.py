from datetime import date
from pathlib import Path

import pytest

from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.redocket import (
    EventIdentity,
    caption_sides,
    is_redocketed,
    ledger_identities,
    redocketed_events,
)
from fedcourtsai.schemas import EventKind, PredictableEvent, Stage
from fedcourtsai.serialize import write_yaml

_DOCKETED = date(2026, 8, 21)
_BEFORE = date(2026, 8, 20)


@pytest.mark.parametrize(
    ("event_caption", "current_caption"),
    [
        # Both sides replaced: the shape of a number re-entered for another petition.
        (
            "Jane Roe, Individually and on Behalf of Her Minor Child, et al. v. "
            + "Springfield Independent School District, et al.",
            "John Doe v. Kansas",
        ),
        # A common respondent survives the re-docketing; the petitioner does not.
        ("Richard Moe v. United States", "Samuel Poe v. United States"),
    ],
)
def test_another_petitioner_is_another_petition_whenever_the_event_opened(
    event_caption: str, current_caption: str
) -> None:
    for opened in (None, _BEFORE, _DOCKETED):
        assert is_redocketed(EventIdentity(event_caption, opened), current_caption, _DOCKETED)


def test_another_respondent_needs_the_docketed_date_to_have_moved_past_the_event() -> None:
    # A government petitioner survives the re-docketing; the respondent does
    # not, and the number's docketed date is now after the event opened.
    assert is_redocketed(
        EventIdentity("Kansas v. Richard Moe", _BEFORE), "Kansas v. Samuel Poe", _DOCKETED
    )
    # The first-named respondent left the case: same petition, same docketed date.
    assert not is_redocketed(
        EventIdentity("Ohio v. Richard Moe, et al.", _DOCKETED),
        "Ohio v. Second Avenue Foundation, et al.",
        _DOCKETED,
    )
    assert not is_redocketed(
        EventIdentity("Ohio v. Richard Moe", None), "Ohio v. Samuel Poe", _DOCKETED
    )


def test_an_interim_moment_is_read_on_the_petitioner_side_alone() -> None:
    # An application's baseline opens at its filing, before its docketing, so
    # an earlier opening corroborates nothing: a first-respondent change on the
    # same application is not a re-docketing.
    identity = EventIdentity("Doe v. Richard Roe, et al.", _BEFORE, "interim")
    assert not is_redocketed(identity, "Doe v. Second Ave Fdn, et al.", _DOCKETED)
    # The cert moment with the same identity is corroborated by the moved date.
    cert = EventIdentity("Doe v. Richard Roe, et al.", _BEFORE, "cert")
    assert is_redocketed(cert, "Doe v. Second Ave Fdn, et al.", _DOCKETED)
    # The petitioner arm still reads an interim moment.
    assert is_redocketed(EventIdentity("Moe v. Ohio", _BEFORE, "interim"), "Doe v. Ohio", _DOCKETED)


@pytest.mark.parametrize(
    ("event_caption", "current_caption"),
    [
        # A re-rendering of the same caption.
        ("DOE, JOHN v. KANSAS", "John Doe v. Kansas"),
        # An abbreviated rendering matches the full word by prefix.
        ("Doe v. Dep't of Corr.", "Doe v. Department of Corrections"),
        # A contraction matches the full word as an abbreviation.
        ("Doe v. Dep't", "Doe v. Department"),
        # Accents fold.
        ("José Núñez v. Kansas", "Jose Nunez v. Kansas"),
        # Role words beyond petitioner/respondent name no party.
        ("Doe, Applicant v. Kansas", "Doe v. Kansas"),
        ("Doe et vir v. Kansas", "Doe v. Kansas"),
        # A substituted officer keeps the office words.
        (
            "Doe v. Alan B. Carter, Attorney General",
            "Doe v. Beth Dunn, Attorney General",
        ),
        ("Doe v. Smith, Warden", "Doe v. Jones, Warden"),
        (
            "Carla Evans, Secretary of Homeland Security v. Doe",
            "Dale Foster, Secretary of Homeland Security v. Doe",
        ),
        # An `In re` caption has no respondent side to compare.
        ("In re John Doe", "John Doe v. United States"),
        # An upper-case `V.` is a middle initial, not the separator.
        ("John V. Doe v. Kansas", "John V. Doe v. Kansas"),
        # A caption with no party word compares nothing.
        ("M. W. v. Superior Court", "Jane Doe v. Superior Court"),
    ],
)
def test_the_same_petition_rendered_or_substituted_is_not_redocketed(
    event_caption: str, current_caption: str
) -> None:
    assert not is_redocketed(EventIdentity(event_caption, _BEFORE), current_caption, _DOCKETED)


def test_a_short_word_matches_only_itself() -> None:
    # Below four letters a prefix is not a match: Lee is not Leeds.
    assert is_redocketed(EventIdentity("Lee v. Ohio", _BEFORE), "Leeds v. Ohio", _DOCKETED)
    assert not is_redocketed(EventIdentity("Leed v. Ohio", _BEFORE), "Leeds v. Ohio", _DOCKETED)


def test_caption_sides_drop_role_words_and_short_words() -> None:
    petitioner, respondent = caption_sides("Jane Roe, et al., Petitioners v. Ohio")
    assert petitioner == {"jane", "roe"}
    assert respondent == {"ohio"}
    assert caption_sides("In re Jane Roe")[1] == frozenset()


def test_redocketed_events_reads_every_witness_and_skips_an_empty_caption() -> None:
    corpus_witness = {
        "evt-a": EventIdentity("Doe v. Kansas"),
        "evt-b": EventIdentity("Moe v. Ohio"),
    }
    committed = {"evt-a": EventIdentity("Moe v. Ohio")}
    assert redocketed_events("Doe v. Kansas", _DOCKETED, corpus_witness, committed) == {
        "evt-a",
        "evt-b",
    }
    assert redocketed_events("Doe v. Kansas", _DOCKETED, corpus_witness) == {"evt-b"}
    assert redocketed_events("", _DOCKETED, corpus_witness, committed) == frozenset()


def test_ledger_identities_reads_only_committed_definitions(tmp_path: Path) -> None:
    write_yaml(
        CasePaths(tmp_path, "scotus", 9026000221).event("evt-petition-disposition").event_file,
        PredictableEvent(
            event_id="evt-petition-disposition",
            case_id="scotus/9026000221",
            kind=EventKind.petition,
            stage=Stage.cert,
            title="Moe v. Ohio",
            opened_at=_BEFORE,
        ),
    )
    identities = ledger_identities(
        tmp_path, "scotus", 9026000221, ["evt-petition-disposition", "evt-uncommitted"]
    )
    assert identities == {"evt-petition-disposition": EventIdentity("Moe v. Ohio", _BEFORE, "cert")}


def test_an_unreadable_committed_definition_is_no_witness(tmp_path: Path) -> None:
    case = CasePaths(tmp_path, "scotus", 9026000221)
    broken = case.event("evt-petition-disposition").event_file
    broken.parent.mkdir(parents=True)
    broken.write_text("title: [unclosed\n", encoding="utf-8")
    undated = case.event("evt-petition-arrival-disposition").event_file
    undated.parent.mkdir(parents=True)
    undated.write_text("title: Moe v. Ohio\nopened_at: not-a-date\n", encoding="utf-8")
    identities = ledger_identities(
        tmp_path,
        "scotus",
        9026000221,
        ["evt-petition-disposition", "evt-petition-arrival-disposition"],
    )
    assert identities == {}
