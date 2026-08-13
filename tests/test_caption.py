"""Fixture-pinned tests for the petitioner-class rule (`pipeline.caption`).

The rule feeds a census a selection constant may be frozen from, so the
fixtures ARE the specification: a change that moves any of these is a new
rule version needing a new census and a new statistical review, never a
quiet retune.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from fedcourtsai import corpus
from fedcourtsai.analytics import _is_scored_segment_row
from fedcourtsai.pipeline.caption import (
    _scored_segment,
    caption_census,
    classify_petitioner,
    petitioner_caption,
    petitioner_class,
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


@pytest.mark.parametrize("title", FEDERAL)
def test_federal_captions(title: str) -> None:
    assert classify_petitioner(title) == "federal", title


@pytest.mark.parametrize("title", STATE)
def test_state_captions(title: str) -> None:
    assert classify_petitioner(title) == "state", title


@pytest.mark.parametrize("title", PRIVATE)
def test_private_captions(title: str) -> None:
    assert classify_petitioner(title) == "private", title


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
