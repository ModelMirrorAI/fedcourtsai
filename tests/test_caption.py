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
    names_captioned_petitioner,
    petitioner_caption,
    petitioner_class,
    petitioner_class_v2,
    petitioner_class_v3,
    petitioner_class_v4,
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
    assert caption_rule("caption-v1") is petitioner_class
    assert caption_rule("caption-v2") is petitioner_class_v2
    assert caption_rule("caption-v3") is petitioner_class_v3
    assert caption_rule("caption-v4") is petitioner_class_v4
    assert set(CAPTION_RULES) == {"caption-v1", "caption-v2", "caption-v3", "caption-v4"}
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
    """The census's local segment predicate equals `analytics`'s on every form —
    the two are held apart only to break an import cycle. The annotated docket
    number ("*** CAPITAL CASE ***") is pinned alongside the plain ones because
    it is the form the two most easily drift on: the gate reads it through
    normalization, and the statpack cut only agrees because its own parse strips
    the annotation first."""
    rows = [
        corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number="24-100"),
        corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="24-5001"),
        corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="24A100"),
        corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="801"),
        corpus.CorpusRow(case_id="ca9/5", court="ca9", docket_number="23-1234"),
        corpus.CorpusRow(case_id="scotus/6", court="scotus", docket_number=""),
        corpus.CorpusRow(case_id="scotus/7", court="scotus", docket_number="No. 01-7700"),
        corpus.CorpusRow(
            case_id="scotus/8", court="scotus", docket_number="25-100 *** CAPITAL CASE ***"
        ),
        corpus.CorpusRow(
            case_id="scotus/9", court="scotus", docket_number="25-5184 *** CAPITAL CASE ***"
        ),
    ]
    for row in rows:
        assert _scored_segment(row) == _is_scored_segment_row(row), row.case_id
    # Agreement alone would also hold if both readings dropped the annotated
    # rows, so the segment membership is pinned too: an annotated paid petition
    # is *in*, its IFP-serial twin excluded — both read off the serial that sits
    # behind the annotation.
    assert _is_scored_segment_row(rows[7]) is True
    assert _is_scored_segment_row(rows[8]) is False


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


# --- caption-v3: the Solicitor General's office as petitioner counsel ------------

_FILED_UNDER_PRELOGAR = date(2023, 3, 1)


def _counsel_row(
    title: str,
    *counsel: corpus.CounselEntry,
    case_id: str = "scotus/1",
    docket_number: str = "22-100",
    disposition: Disposition | None = None,
) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket_number,
        petitioner_title=title,
        date_filed=_FILED_UNDER_PRELOGAR,
        disposition=disposition,
        last_live_polled=date(2026, 8, 1),
        counsel=list(counsel),
    )


def _sg_for(role: corpus.CounselRole, party: str = "Bobby Lumpkin") -> corpus.CounselEntry:
    return corpus.CounselEntry(
        party=party, attorney="Elizabeth B. Prelogar", role=role, counsel_of_record=True
    )


def test_caption_v3_reads_an_sg_represented_warden_as_federal() -> None:
    """The Warden tail is v1's sub-national officer fallback: state wherever the
    caption omits the jurisdiction. Under caption-v3 the office's appearance for
    the petitioner runs first, so the same caption the Solicitor General files
    for reads federal — and without that appearance it is v2's state read."""
    title = "Michael Smith, Warden"
    assert classify_petitioner_v2(title) == "state"
    represented = _counsel_row(title, _sg_for(corpus.CounselRole.petitioner))
    assert petitioner_class_v2(represented) == "state"
    assert petitioner_class_v3(represented) == "federal"
    unrepresented = _counsel_row(
        title,
        corpus.CounselEntry(
            party="Michael Smith", attorney="Jane Roe", role=corpus.CounselRole.petitioner
        ),
    )
    assert petitioner_class_v3(unrepresented) == "state"


def test_caption_v3_reads_the_office_on_a_private_caption_as_federal() -> None:
    represented = _counsel_row("John Doe", _sg_for(corpus.CounselRole.petitioner, "John Doe"))
    assert petitioner_class_v2(represented) == "private"
    assert petitioner_class_v3(represented) == "federal"


def test_caption_v3_never_reads_the_office_as_respondent_or_amicus_counsel() -> None:
    """The office opposing cert (respondent) is the commonest SG appearance and
    says nothing about who is asking, and `other` is the post-grant grant oracle —
    neither side moves the class."""
    for role in (corpus.CounselRole.respondent, corpus.CounselRole.other):
        row = _counsel_row("John Doe", _sg_for(role, "United States"))
        assert petitioner_class_v3(row) == "private", role


def test_caption_v3_reads_a_former_solicitor_general_in_private_practice_as_private() -> None:
    """The dated roster, not the name: Francisco's spans ended in 2020, so on a
    docket filed in 2023 his appearance for a private petitioner is private practice."""
    row = _counsel_row(
        "John Doe",
        corpus.CounselEntry(
            party="John Doe", attorney="Noel J. Francisco", role=corpus.CounselRole.petitioner
        ),
    )
    assert petitioner_class_v3(row) == "private"


@pytest.mark.parametrize("title", FEDERAL + STATE + PRIVATE)
def test_caption_v3_is_caption_v2_on_a_row_without_the_office(title: str) -> None:
    """With no counsel at all, v3 is v2 on every frozen fixture — the counsel
    check is the whole of the widening, so the two censuses differ only on rows
    the office appears on."""
    row = _counsel_row(title)
    assert petitioner_class_v3(row) == petitioner_class_v2(row)


def test_caption_v3_census_moves_only_the_rows_the_office_appears_on(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _counsel_row(
                    "Michael Smith, Warden",
                    _sg_for(corpus.CounselRole.petitioner),
                    case_id="scotus/1",
                    docket_number="24-100",
                    disposition=Disposition.granted,
                ),
                _counsel_row(
                    "John Doe",
                    _sg_for(corpus.CounselRole.respondent, "United States"),
                    case_id="scotus/2",
                    docket_number="24-101",
                    disposition=Disposition.denied,
                ),
            ],
        )
        v2 = caption_census(conn, rule_version="caption-v2")
        v3 = caption_census(conn, rule_version="caption-v3")
    v2_cells = {c.petitioner_class: c.n for c in v2.pooled}
    v3_cells = {c.petitioner_class: c.n for c in v3.pooled}
    assert v2_cells == {"federal": 0, "state": 1, "private": 1}
    assert v3_cells == {"federal": 1, "state": 0, "private": 1}
    assert v3.rule_version == "caption-v3"


# --- caption-v4: the office as counsel of record for the captioned petitioner ----

_FILED_UNDER_SAUER = date(2026, 7, 31)


def _v4_row(
    title: str | None,
    *counsel: corpus.CounselEntry,
    case_name: str = "",
    case_id: str = "scotus/9026000145",
    docket_number: str = "26-145",
    filed: date = _FILED_UNDER_SAUER,
    disposition: Disposition | None = None,
    denied: date | None = None,
) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket_number,
        case_name=case_name,
        petitioner_title=title,
        date_filed=filed,
        date_cert_denied=denied,
        disposition=disposition,
        last_live_polled=date(2026, 10, 29),
        counsel=list(counsel),
    )


def _counsel(
    party: str,
    attorney: str = "D. John Sauer",
    *,
    role: corpus.CounselRole = corpus.CounselRole.petitioner,
    of_record: bool = True,
) -> corpus.CounselEntry:
    return corpus.CounselEntry(
        party=party, attorney=attorney, role=role, counsel_of_record=of_record
    )


#: The federal petitions caption-v2 misses: each caption, the counsel block's own
#: party string for the office's entry (the corpus's renderings: the block
#: abbreviates the caption's officer title and drops a given name), and the
#: caption's v2 read.
SG_FILED = [
    ("U.S. DOGE Service, et al.", "U.S. Doge Service, et al.", "private"),
    (
        "Warden, Moshannon Valley Correctional Center, et al.",
        "Warden, Moshannon Valley Correctional Center, et al.",
        "private",
    ),
    ("Juan Baltazar, Warden, et al.", "Baltazar, Warden, et al.", "state"),
    (
        "Markwayne Mullin, Secretary, Department of Homeland Security, et al.",
        "Markwayne Mullin, et al.",
        "private",
    ),
    (
        "Kenneth Genalo, Director of the New York Field Office of U.S. Immigration and "
        + "Customs Enforcement, et al.",
        "Kenneth Genalo, et al.",
        "state",
    ),
    ("Vivek H. Murthy, Surgeon General, et al.", "Vivek H. Murthy , et al.", "private"),
    ("Pension Benefit Guaranty Corporation", "Pension Benefit Guaranty Corporation", "private"),
]


@pytest.mark.parametrize(("title", "party", "v2"), SG_FILED)
def test_caption_v4_reads_the_office_for_the_captioned_petitioner_as_federal(
    title: str, party: str, v2: str
) -> None:
    """The office as counsel of record for the party the caption names reads
    federal, ahead of the Warden fallback and the qualified state markers alike;
    without that entry each caption keeps its v2 read."""
    row = _v4_row(title, _counsel(party))
    assert petitioner_class_v2(row) == v2
    assert petitioner_class_v4(row) == "federal"
    assert petitioner_class_v3(row) == "federal"
    assert petitioner_class_v4(_v4_row(title)) == v2


def test_caption_v4_reads_the_joined_case_name_where_no_structured_caption_is_stored() -> None:
    row = _v4_row(
        None,
        _counsel("Pension Benefit Guaranty Corporation"),
        case_name="Pension Benefit Guaranty Corporation v. Smith",
    )
    assert petitioner_class_v4(row) == "federal"


@pytest.mark.parametrize(
    ("title", "v2"),
    [
        ("International Partners for Ethical Care, Inc., et al.", "private"),
        ("Mark Brnovich, Attorney General of Arizona, et al.", "state"),
        ("Atlantic Coast Pipeline, LLC", "private"),
        ("Miriam Fuld, et al.", "private"),
    ],
)
def test_caption_v4_never_reads_a_supporting_amicus_or_a_consolidation(title: str, v2: str) -> None:
    """The two post-outcome shapes caption-v3 admits: the office listed under the
    petitioner for "United States" (a supporting amicus, or a government petition
    consolidated at the grant) beside the captioned petitioner's own counsel.
    v3 reads them federal; v4 reads each as v2."""
    row = _v4_row(
        title,
        _counsel(title, "Jane Roe"),
        _counsel("United States"),
        _counsel("united states", "Noel John Francisco"),
        filed=date(2019, 6, 27),
        disposition=Disposition.granted,
    )
    assert petitioner_class_v3(row) == "federal"
    assert petitioner_class_v4(row) == v2


def test_caption_v4_keeps_a_state_petitioner_and_a_state_solicitor_general_state() -> None:
    """A state's own counsel is no roster name, and a future Solicitor General
    appearing as a state's solicitor general before taking office reads as
    private practice under the dated roster: both state petitions stay state."""
    texas = _v4_row("Texas", _counsel("Texas", "Aaron L. Nielson"))
    assert petitioner_class_v4(texas) == "state"
    missouri = _v4_row(
        "Eric S. Schmitt, Attorney General of Missouri, et al.",
        _counsel("Eric S. Schmitt, Attorney General of Missouri, et al."),
        case_id="scotus/2",
        docket_number="19-500",
        filed=date(2019, 10, 1),
        disposition=Disposition.denied,
        denied=date(2020, 1, 13),
    )
    assert petitioner_class_v2(missouri) == "state"
    assert petitioner_class_v4(missouri) == "state"


def test_caption_v4_keeps_a_warden_with_state_counsel_state() -> None:
    row = _v4_row("Michael Smith, Warden", _counsel("Michael Smith, Warden", "Jane Roe"))
    assert petitioner_class_v4(row) == "state"


@pytest.mark.parametrize("attorney", ["Noel J. Francisco", "Elizabeth B. Prelogar"])
def test_caption_v4_reads_a_former_solicitor_general_in_private_practice_as_private(
    attorney: str,
) -> None:
    """The dated roster, not the name: a former Solicitor General as counsel of
    record for a private petitioner, on a docket filed after the span ended, is
    private practice, though the party match holds."""
    row = _v4_row("Acme Corp., et al.", _counsel("Acme Corp., et al.", attorney))
    assert petitioner_class_v4(row) == "private"


def test_caption_v4_reads_only_counsel_of_record_on_the_petitioner_side() -> None:
    """The office opposing cert, listed as `other`, or listed for the petitioner
    but not as counsel of record moves nothing."""
    title = "Warden, Moshannon Valley Correctional Center, et al."
    for entry in (
        _counsel(title, role=corpus.CounselRole.respondent),
        _counsel(title, role=corpus.CounselRole.other),
        _counsel(title, of_record=False),
    ):
        assert petitioner_class_v4(_v4_row(title, entry)) == "private", entry


@pytest.mark.parametrize("title", FEDERAL + STATE + PRIVATE)
def test_caption_v4_is_caption_v2_on_a_row_without_the_office(title: str) -> None:
    row = _v4_row(title)
    assert petitioner_class_v4(row) == petitioner_class_v2(row)


@pytest.mark.parametrize(
    ("party", "caption_text", "expected"),
    [
        ("Baltazar, Warden, et al.", "Juan Baltazar, Warden, et al.", True),
        ("U.S. Doge Service, et al.", "U.S. DOGE Service, et al.", True),
        ("Vivek H. Murthy , et al.", "Vivek H. Murthy, Surgeon General, et al.", True),
        ("Kenneth Genalo, et al.", "Kenneth Genalo, in His Official Capacity as Director", True),
        ("United States", "International Partners for Ethical Care, Inc., et al.", False),
        ("United States", "Mark Brnovich, Attorney General of Arizona, et al.", False),
        ("Smith", "Michael Smithson, Warden", False),
        ("United States", "Chamber of Commerce of the United States", False),
        ("United States", "United States, et al.", True),
        ("", "John Doe", False),
        ("John Doe", "", False),
    ],
)
def test_the_party_match_is_lead_against_lead(
    party: str, caption_text: str, expected: bool
) -> None:
    assert names_captioned_petitioner(party, caption_text) is expected


def test_caption_v4_census_moves_only_the_office_filed_rows(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    warden = "Juan Baltazar, Warden, et al."
    amicus = "International Partners for Ethical Care, Inc., et al."
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _v4_row(
                    warden,
                    _counsel("Baltazar, Warden, et al."),
                    case_id="scotus/1",
                    docket_number="24-100",
                    disposition=Disposition.granted,
                ),
                _v4_row(
                    amicus,
                    _counsel(amicus, "Jane Roe"),
                    _counsel("United States"),
                    case_id="scotus/2",
                    docket_number="24-101",
                    disposition=Disposition.granted,
                ),
            ],
        )
        censuses = [
            caption_census(conn, rule_version=version)
            for version in ("caption-v2", "caption-v3", "caption-v4")
        ]
    cells = {
        census.rule_version: {c.petitioner_class: c.n for c in census.pooled} for census in censuses
    }
    assert cells["caption-v2"] == {"federal": 0, "state": 1, "private": 1}
    assert cells["caption-v3"] == {"federal": 2, "state": 0, "private": 0}
    assert cells["caption-v4"] == {"federal": 1, "state": 0, "private": 1}
