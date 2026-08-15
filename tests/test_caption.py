"""Fixture-pinned tests for the petitioner-class rules (`pipeline.caption`).

The rules feed a census a selection constant may be frozen from, so the
fixtures ARE the specification: a change that moves any of these is a new
rule version needing a new census and a new statistical review, never a
quiet retune. Each registered rule carries its own fixtures, and the
`caption-v1` lists are frozen — the widened `caption-v2` reads them all the
same way, so every v1 fixture below is asserted under both rules and the v2
list pins exactly what the widening adds.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.analytics import _is_scored_segment_row
from fedcourtsai.pipeline.caption import (
    CAPTION_RULES,
    _scored_segment,
    caption_census,
    caption_rule,
    classify_petitioner,
    classify_petitioner_v2,
    petitioner_caption,
    petitioner_class,
    petitioner_class_v2,
)
from fedcourtsai.schemas import Disposition

FEDERAL = [
    "United States",
    "United States, Petitioner",
    "United States of America",
    "Merrick B. Garland, Attorney General",
    "Federal Communications Commission",
    "FCC",
    "National Labor Relations Board",
    "Securities and Exchange Commission",
    "Alejandro Mayorkas, Secretary of Homeland Security",
    "Xavier Becerra, Secretary of Health and Human Services",
    "Elizabeth Prelogar, Solicitor General",
    "Donald J. Trump, President of the United States",
    "Louis DeJoy, Postmaster General",
    "Environmental Protection Agency",
    "Internal Revenue Service",
    "Department of Justice",
    "Department of Homeland Security, et al.",
    "Commissioner of Internal Revenue",
    "Food and Drug Administration",
    "Consumer Financial Protection Bureau, et al.",
    "United States Postal Service",
    "Kilolo Kijakazi, Acting Commissioner of Social Security Administration",
]

STATE = [
    "Arizona",
    "Oklahoma, Petitioner",  # the event-vintage rendering: role label stripped
    "Anna Valentine, Warden",
    "Randy Smith, Sheriff, et al.",
    "Deanna Brookhart, Acting Warden",
    "State of Texas",
    "Commonwealth of Kentucky",
    "Texas, et al.",
    "Mark Brnovich, Attorney General of Arizona",
    "Christopher Paris, Commissioner, Pennsylvania State Police",
    "George Bivens, Acting Commissioner, Pennsylvania State Police",
    "Texas Department of Criminal Justice",
    "California Department of Corrections and Rehabilitation",
    "Superintendent, Massachusetts Correctional Institution",
    "Terence Clark, Director, Prince George's County Department of Corrections, Maryland",
]

PRIVATE = [
    "New York State Rifle & Pistol Association, Inc.",
    "United States ex rel. Polansky",  # qui tam: the relator petitions
    "United States, et al., ex rel. Smith",  # qui tam behind an et-al. — still the relator
    "U.S. Bank National Association",
    "United States Soccer Federation, Inc.",
    "United States Telecom Association",
    "USAA",
    "Maine Community Health Options",
    "Archdiocese of Washington",
    "Esther Virginia John",
    "Donald J. Trump",  # no office in the caption: the office is the class
    "John Doe",
    "Google LLC",
    "Americans for Prosperity Foundation",
    "Virginia Uranium, Inc.",
    "",
]


# The measured `caption-v1` federal recall gap, caption by caption: every
# distinct caption in the census frame that v1 reads as `private` and
# `caption-v2` reads as `federal`, verbatim as the corpus renders it. Five
# shapes, each a family rather than a one-off spelling — the "Office of the
# United States <office>" word order, an agency named without a "United
# States" / "Federal" lead (or spelled out where v1 lists only the initialism),
# the military departments in the officer convention, the deputy/under ranks of
# a federal office, and the sovereign behind an "In re" caption. Every entry is
# asserted `private` under v1 as well: the v1 spec is frozen, so the widening
# must show up as a v2-only change.
FEDERAL_V2_ONLY = [
    "Office of the United States Trustee",
    "United States Trustee Region 21",
    "William K. Harrington, United States Trustee, Region 2",
    "Robin Carnahan, Administrator of the General Services Administration",
    "Daren K. Margolin, Director of the Executive Office for Immigration Review",
    "Nuclear Regulatory Commission, et al.",
    "Agency for International Development, et al.",
    "Immigration and Customs Enforcement, et al.",
    "Tae D. Johnson, Acting Director of U.S. Immigration and Customs Enforcement, et al.",
    "Tony H. Pham, Senior Official Performing the Duties of the Director of U.S. "
    + "Immigration and Customs Enforcement, et al.",
    "Kevin Raycraft, Acting Director of the Detroit Field Office of U.S. Immigration "
    + "and Customs Enforcement, et al.",
    "Andrei Iancu, Under Secretary of Commerce for Intellectual Property and Director, "
    + "Patent and Trademark Office",
    "Laura Peter, Deputy Director, Patent and Trademark Office",
    "Frank Kendall, Secretary of the Air Force, et al.",
    "Department of the Air Force, et al.",
    "In Re United States, et al.",
]

# The same five shapes on captions the frame does not (yet) carry: the carve-in
# these rules feed selects at ARRIVAL, so the vocabulary is deliberately wider
# than history exercises, and these pin what a future caption of each shape
# reads as. They move no census cell — a pattern matching nothing counts
# nothing — so they are held apart from the measured list above rather than
# quoted beside it.
FEDERAL_V2_PROSPECTIVE = [
    "Office of the United States Attorney",
    "Nuclear Regulatory Commission",
    "Patent and Trademark Office",
    "Customs and Border Protection",
    "Federal Aviation Administration",
    "Surface Transportation Board",
    "Merit Systems Protection Board",
    "Equal Employment Opportunity Commission",
    "Carlos Del Toro, Secretary of the Navy",
    "Christine Wormuth, Secretary of the Army",
    "Department of the Navy",
    "In Re United States",
]


@pytest.mark.parametrize("title", FEDERAL)
def test_federal_captions(title: str) -> None:
    assert classify_petitioner(title) == "federal", title


@pytest.mark.parametrize("title", STATE)
def test_state_captions(title: str) -> None:
    assert classify_petitioner(title) == "state", title


@pytest.mark.parametrize("title", PRIVATE)
def test_private_captions(title: str) -> None:
    assert classify_petitioner(title) == "private", title


@pytest.mark.parametrize("title", [*FEDERAL_V2_ONLY, *FEDERAL_V2_PROSPECTIVE])
def test_caption_v2_reads_the_federal_shapes_v1_misses(title: str) -> None:
    """The widening, caption by caption — and v1 frozen underneath it.

    Both halves are the specification: v2 must read the measured misses as
    federal, and v1 must go on reading them as private, because the `sal-v2`
    carve-in is frozen on a census cut by v1 and a quiet retune of v1 would
    re-point that constant at a population it was never measured on."""
    assert classify_petitioner(title) == "private", title
    assert classify_petitioner_v2(title) == "federal", title


@pytest.mark.parametrize("title", [*FEDERAL, *STATE, *PRIVATE])
def test_caption_v2_keeps_every_caption_v1_fixture(title: str) -> None:
    """The widening is one-directional: it adds federal reads, it moves nothing.

    Every v1 fixture — federal, state, and private alike — classifies the same
    under v2, so the delta between the two censuses is drawn from the `private`
    cell only and the two are comparable cell by cell. Qui tam and the state
    block keep their precedence in particular: the relator still petitions, and
    a caption naming a state is still state."""
    assert classify_petitioner_v2(title) == classify_petitioner(title), title


@pytest.mark.parametrize(
    "title",
    [
        # The shape where the two rules' own patterns disagree in the losing
        # direction: v1 reads the officer tail as federal, while v2's widened
        # qui tam pattern — the "In re" prefix reaching the relator — would
        # fire first and read `private`. v1's answer wins, because v2 runs it
        # first and keeps any non-private read.
        "In re United States ex rel. Smith, Secretary",
        "In Re United States ex rel. Doe, Attorney General",
    ],
)
def test_a_v1_federal_read_survives_a_widened_pattern_that_would_undo_it(title: str) -> None:
    """One-directionality is a property of the rule, not of the fixture lists.

    The census delta is only interpretable as "the private cell lost rows to
    the federal cell" if no caption travels the other way, so the guarantee has
    to hold on captions nobody thought to write down — which is why v2 defers
    to v1's non-private answer rather than re-deriving one."""
    assert classify_petitioner(title) == "federal", title
    assert classify_petitioner_v2(title) == "federal", title


def test_qui_tam_keeps_its_precedence_behind_an_in_re_prefix() -> None:
    """v2 reads the sovereign behind an "In re" caption — and reads the
    relator behind one too, in the same breath. Granting the prefix to the
    sovereign pattern alone would have flipped a qui tam caption to federal on
    the strength of a prefix that says nothing about who is petitioning."""
    assert classify_petitioner_v2("In Re United States") == "federal"
    assert classify_petitioner_v2("In re United States, Petitioner") == "federal"
    assert classify_petitioner_v2("In Re United States ex rel. Smith") == "private"
    assert classify_petitioner_v2("In re United States, et al., ex rel. Smith") == "private"


def test_the_registry_serves_each_rule_and_raises_on_an_unregistered_one() -> None:
    """A census cut under a label this process cannot produce wants an error,
    not a silent fallback to the baseline rule."""
    assert caption_rule("caption-v1") is classify_petitioner
    assert caption_rule("caption-v2") is classify_petitioner_v2
    assert set(CAPTION_RULES) == {"caption-v1", "caption-v2"}
    with pytest.raises(KeyError):
        caption_rule("caption-v0")


def test_state_markers_outrank_federal_markers() -> None:
    """A qualified state officer never reads federal on the office word
    alone; the same office unqualified is the federal captioning convention
    — except the sub-national offices (Warden, Sheriff), which are state
    wherever the caption omits the jurisdiction."""
    assert classify_petitioner("Brnovich, Attorney General of Arizona") == "state"
    assert classify_petitioner("Garland, Attorney General") == "federal"


def test_officer_title_is_the_class_boundary() -> None:
    """The same person with and without the office: the class keys on the
    office as captioned — dropping the title drops the class, which is why
    the structured column matters."""
    with_office = "Donald J. Trump, President of the United States"
    without = "Donald J. Trump"
    assert classify_petitioner(with_office) == "federal"
    assert classify_petitioner(without) == "private"


def test_row_reading_prefers_the_structured_column() -> None:
    row = corpus.CorpusRow(
        case_id="scotus/1",
        court="scotus",
        case_name="Brnovich v. Democratic National Committee",  # short join: private
        petitioner_title="Mark Brnovich, Attorney General of Arizona",
    )
    assert petitioner_caption(row) == row.petitioner_title
    assert petitioner_class(row) == "state"


def test_row_reading_falls_back_to_the_caption_split() -> None:
    row = corpus.CorpusRow(
        case_id="scotus/2",
        court="scotus",
        case_name="United States v. Sineneng-Smith",
    )
    assert petitioner_caption(row) == "United States"
    assert petitioner_class(row) == "federal"


def test_caption_census_counts_the_scored_segment(tmp_path: Path) -> None:
    """The census frame is the gate's scored segment: live-slice paid
    modern-cert resolved rows, cut by class with n and grant-family per Term —
    IFP, unresolved, and off-form rows never enter the denominator, and a
    Term with any unresolved frame row reports per Term but never pools."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-100",
                    petitioner_title="United States",
                    disposition=Disposition.granted,
                    last_live_polled=date(2026, 8, 1),
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="24-101",
                    case_name="John Doe v. Roe",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 8, 1),
                ),
                corpus.CorpusRow(  # unresolved: outside the census denominator
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="24-102",
                    last_live_polled=date(2026, 8, 1),
                ),
                corpus.CorpusRow(  # IFP: not the scored segment
                    case_id="scotus/4",
                    court="scotus",
                    docket_number="24-5001",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 8, 1),
                ),
            ],
        )
        census = caption_census(conn)
    assert census.rule_version == "caption-v1"
    assert [t.term for t in census.terms] == [2024]
    cells = {c.petitioner_class: c for c in census.terms[0].classes}
    assert (cells["federal"].n, cells["federal"].grant_family) == (1, 1)
    assert cells["federal"].rate == 1.0
    assert (cells["private"].n, cells["private"].grant_family) == (1, 0)
    assert cells["state"].n == 0 and cells["state"].rate is None
    # Term 2024 carries an unresolved frame row, so it is right-censored:
    # reported per Term — with the caveat travelling in the row — never pooled.
    assert census.terms[0].censored is True
    assert census.terms[0].unresolved == 1
    assert all(c.n == 0 for c in census.pooled)


def test_the_census_cuts_the_same_frame_under_either_rule(tmp_path: Path) -> None:
    """One frame, two rules, two censuses — each stamped with the rule that cut
    it. The frame is identical (same rows, same denominator per Term), so the
    delta is a class migration out of `private` and nothing else; a census
    asked for an unregistered rule raises rather than falling back."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    docket_number="24-100",
                    petitioner_title="United States",  # federal under both rules
                    disposition=Disposition.granted,
                    last_live_polled=date(2026, 8, 1),
                ),
                corpus.CorpusRow(
                    case_id="scotus/2",
                    court="scotus",
                    docket_number="24-101",
                    petitioner_title="Office of the United States Trustee",  # v2 only
                    disposition=Disposition.granted,
                    last_live_polled=date(2026, 8, 1),
                ),
                corpus.CorpusRow(
                    case_id="scotus/3",
                    court="scotus",
                    docket_number="24-102",
                    case_name="John Doe v. Roe",
                    disposition=Disposition.denied,
                    last_live_polled=date(2026, 8, 1),
                ),
            ],
        )
        v1 = caption_census(conn, rule_version="caption-v1")
        v2 = caption_census(conn, rule_version="caption-v2")
        with pytest.raises(KeyError):
            caption_census(conn, rule_version="caption-v0")
    assert (v1.rule_version, v2.rule_version) == ("caption-v1", "caption-v2")
    v1_cells = {c.petitioner_class: c for c in v1.pooled}
    v2_cells = {c.petitioner_class: c for c in v2.pooled}
    assert (v1_cells["federal"].n, v1_cells["private"].n) == (1, 2)
    assert (v2_cells["federal"].n, v2_cells["private"].n) == (2, 1)
    # Same frame both times: the classes repartition, the denominator does not move.
    assert sum(c.n for c in v1.pooled) == sum(c.n for c in v2.pooled) == 3
    assert sum(c.grant_family for c in v1.pooled) == sum(c.grant_family for c in v2.pooled) == 2


def test_row_reading_under_the_wider_rule() -> None:
    """The row-level v2 predicate reads the same caption source as v1's — the
    structured column first, the caption split behind it."""
    row = corpus.CorpusRow(
        case_id="scotus/1",
        court="scotus",
        case_name="Office of the United States Trustee v. John Q. Hammons Fall 2006, LLC",
    )
    assert petitioner_caption(row) == "Office of the United States Trustee"
    assert petitioner_class(row) == "private"
    assert petitioner_class_v2(row) == "federal"


def test_scored_segment_predicate_matches_analytics() -> None:
    """The census's local segment predicate equals `analytics`'s on every
    plain form — held apart to break an import cycle — with one deliberate
    divergence pinned below: an annotated docket number ("*** CAPITAL CASE
    ***") parses here through normalization, matching the gate's own reading,
    where `analytics`'s raw parse drops the row from the statpack cut."""
    rows = [
        corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number="24-100"),
        corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="24-5001"),
        corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="24A100"),
        corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="801"),
        corpus.CorpusRow(case_id="ca9/5", court="ca9", docket_number="23-1234"),
        corpus.CorpusRow(case_id="scotus/6", court="scotus", docket_number=""),
        corpus.CorpusRow(case_id="scotus/7", court="scotus", docket_number="No. 01-7700"),
    ]
    for row in rows:
        assert _scored_segment(row) == _is_scored_segment_row(row), row.case_id
    annotated = corpus.CorpusRow(
        case_id="scotus/8", court="scotus", docket_number="25-100 *** CAPITAL CASE ***"
    )
    assert _scored_segment(annotated) is True  # the gate's reading
    assert _is_scored_segment_row(annotated) is False  # the statpack cut's raw parse


def test_petitioner_title_survives_a_channel_without_it(tmp_path: Path) -> None:
    """The fill-in latch: a REST/bulk enrich carries no PetitionerTitle, and
    must keep — never wipe — what the live channel stamped."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/1",
                    court="scotus",
                    petitioner_title="United States",
                    last_live_polled=date(2026, 8, 1),
                )
            ],
        )
        corpus.upsert_rows(  # the enriching channel: no title in its record
            conn,
            [corpus.CorpusRow(case_id="scotus/1", court="scotus", topic="refreshed")],
        )
        row = corpus.get_row(conn, "scotus/1")
    assert row is not None
    assert row.petitioner_title == "United States"
    assert row.topic == "refreshed"
