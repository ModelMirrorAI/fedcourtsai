"""Fixture-pinned tests for the petitioner-class rule (`pipeline.caption`).

Every caption here is either a real one from the corpus or a shape the stats
review of the rule's precursor named as a failure mode. The rule feeds a
census a selection constant may be frozen from, so the fixtures ARE the
specification: a change that moves any of these is a new rule needing a new
census and a new review, never a quiet retune.
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
    "United States ex rel. Polansky",
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
    "Kilolo Kijakazi, Acting Commissioner of Social Security Administration",
]

STATE = [
    "Arizona",
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
    """The ordering the review flagged: a qualified state officer must never
    read federal on the office word alone, while the same office unqualified
    is the federal captioning convention."""
    assert classify_petitioner("Brnovich, Attorney General of Arizona") == "state"
    assert classify_petitioner("Garland, Attorney General") == "federal"


def test_officer_title_is_the_class_boundary() -> None:
    """The one observed class-flip family: the same person with and without
    the office. The class keys on the office as captioned — dropping the
    title drops the class, which is why the structured column matters."""
    with_office = "Donald J. Trump, President of the United States"
    without = "Donald J. Trump"
    assert classify_petitioner(with_office) == "federal"
    assert classify_petitioner(without) == "private"


def test_row_reading_prefers_the_structured_column() -> None:
    row = corpus.CorpusRow(
        case_id="scotus/1",
        court="scotus",
        case_name="Clark v. Sweeney",  # the short join that misfiles as private
        petitioner_title="Terence Clark, Director, Prince George's County "
        "Department of Corrections, Maryland",
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
    IFP, unresolved, and off-form rows never enter the denominator."""
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
    cells = {c.petitioner_class: c for c in census.pooled}
    assert (cells["federal"].n, cells["federal"].grant_family) == (1, 1)
    assert cells["federal"].rate == 1.0
    assert (cells["private"].n, cells["private"].grant_family) == (1, 0)
    assert cells["state"].n == 0 and cells["state"].rate is None


def test_scored_segment_predicate_matches_analytics() -> None:
    """The census's local segment predicate must equal `analytics`'s — held
    apart only to break an import cycle, never to diverge."""
    rows = [
        corpus.CorpusRow(case_id="scotus/1", court="scotus", docket_number="24-100"),
        corpus.CorpusRow(case_id="scotus/2", court="scotus", docket_number="24-5001"),
        corpus.CorpusRow(case_id="scotus/3", court="scotus", docket_number="24A100"),
        corpus.CorpusRow(case_id="scotus/4", court="scotus", docket_number="801"),
        corpus.CorpusRow(case_id="ca9/5", court="ca9", docket_number="23-1234"),
        corpus.CorpusRow(case_id="scotus/6", court="scotus", docket_number=""),
    ]
    for row in rows:
        assert _scored_segment(row) == _is_scored_segment_row(row), row.case_id
