"""Fixture-pinned tests for the SG-office counsel annotation (`pipeline.counsel`).

The annotation's whole claim is that a dated roster separates the Solicitor
General's office from the same names in private practice, so the fixtures pin
the boundaries of that separation: the tenure edges, a former and a future
Solicitor General on the wrong side of them, a state solicitor general, the
amicus role the rule never reads, and the version stamp a cut carries.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.counsel import (
    COUNSEL_RULES,
    MERITS_SPAN,
    SG_OFFICE_ROSTER,
    SG_OFFICE_RULE_VERSION,
    counsel_rule,
    docket_life,
    normalize_attorney,
    sg_office_annotations,
)
from fedcourtsai.pipeline.party_rates import party_rates
from fedcourtsai.schemas import Disposition

runner = CliRunner()

# Sauer's one span opens on 2025-04-04; Francisco's Solicitor General span
# closes on 2020-07-03.
SAUER_START = date(2025, 4, 4)
FRANCISCO_END = date(2020, 7, 3)


def _counsel(attorney: str, party: str, role: str = "respondent") -> corpus.CounselEntry:
    return corpus.CounselEntry(
        party=party, attorney=attorney, role=corpus.CounselRole(role), counsel_of_record=True
    )


def _row(
    *counsel: corpus.CounselEntry,
    case_id: str = "scotus/1",
    docket_number: str = "24-100",
    case_name: str = "Jane Doe v. Acme Corp.",
    **kwargs: object,
) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        docket_number=docket_number,
        case_name=case_name,
        last_live_polled=date(2026, 9, 1),
        counsel=list(counsel),
        **kwargs,
    )


def test_the_roster_is_well_formed() -> None:
    """Aliases are normalized and unique; spans are ordered; OT2015 is covered."""
    aliases = [alias for member in SG_OFFICE_ROSTER for alias in member.aliases]
    assert len(aliases) == len(set(aliases))
    assert all(alias == normalize_attorney(alias) for alias in aliases)
    for member in SG_OFFICE_ROSTER:
        for span in member.spans:
            assert span.end is None or span.start <= span.end, member.name
            assert span.source
    ot2015 = date(2015, 10, 5)
    assert any(
        span.start <= ot2015 and (span.end is None or ot2015 <= span.end)
        for member in SG_OFFICE_ROSTER
        if member.name.startswith("Donald B. Verrilli")
        for span in member.spans
    )


def test_normalize_attorney_folds_the_spellings_the_index_carries() -> None:
    assert normalize_attorney("Noel J. Francisco") == "noel j francisco"
    assert normalize_attorney("Donald B. Verrilli Jr.") == "donald b verrilli"
    assert normalize_attorney("  D.  John   Sauer ") == "d john sauer"
    assert normalize_attorney("Jos&#xE9; O&#x27;Neil") == "jose o neil"
    assert normalize_attorney("") == ""


@pytest.mark.parametrize(
    ("decided", "expected"),
    [
        (date(2025, 4, 3), "no"),  # closed the day before the span opened
        (SAUER_START, "yes"),  # closed the day it opened: spans are inclusive
    ],
)
def test_the_span_start_is_inclusive(decided: date, expected: str) -> None:
    """A docket that closed before the member took office is not theirs (non-federal party)."""
    row = _row(
        _counsel("D. John Sauer", "Doe Holdings, LLC"),
        date_filed=date(2025, 1, 2),
        date_cert_denied=decided,
        disposition=Disposition.denied,
    )
    assert sg_office_annotations(row, None).respondent == expected


@pytest.mark.parametrize(
    ("filed", "expected"),
    [
        (FRANCISCO_END, "yes"),  # filed the day the span closed
        (date(2020, 7, 4), "no"),  # filed the day after: a former SG
    ],
)
def test_the_span_end_is_inclusive(filed: date, expected: str) -> None:
    row = _row(
        _counsel("Noel John Francisco", "United States", role="petitioner"),
        date_filed=filed,
        date_cert_denied=date(2020, 10, 5),
        disposition=Disposition.denied,
    )
    assert sg_office_annotations(row, None).petitioner == expected


def test_a_former_sg_in_private_practice_is_not_the_office() -> None:
    """Francisco at a firm, years after leaving: set aside, and counted as such."""
    row = _row(
        _counsel("Noel J. Francisco", "Bestwall LLC, et al.", role="petitioner"),
        _counsel("Jane Roe", "John Doe"),
        date_filed=date(2023, 12, 22),
        date_cert_denied=date(2024, 5, 13),
        disposition=Disposition.denied,
    )
    annotation = sg_office_annotations(row, None)
    assert (annotation.petitioner, annotation.respondent, annotation.side) == ("no", "no", "none")
    assert annotation.private_practice == 1


def test_a_former_sg_never_counts_even_on_a_federal_party() -> None:
    """A late write adds a successor, never a predecessor."""
    row = _row(
        _counsel("Noel John Francisco", "United States"),
        date_filed=date(2023, 1, 5),
        date_cert_denied=date(2023, 3, 1),
        disposition=Disposition.denied,
    )
    assert sg_office_annotations(row, None).respondent == "no"


def test_a_future_sg_as_a_state_solicitor_general_is_not_the_office() -> None:
    """Sauer signing for Missouri, before his federal span: a state SG, not the office."""
    row = _row(
        _counsel("D. John Sauer", "State of Missouri"),
        date_filed=date(2020, 2, 3),
        date_cert_denied=date(2020, 4, 20),
        disposition=Disposition.denied,
    )
    annotation = sg_office_annotations(row, None)
    assert annotation.respondent == "no"
    assert annotation.private_practice == 1


def test_a_state_solicitor_general_off_the_roster_is_not_the_office() -> None:
    """A state SG's bare "Solicitor General" title never reaches the index: no name match."""
    row = _row(
        _counsel("Barbara Dale Underwood", "New York"),
        date_filed=date(2024, 1, 5),
        date_cert_denied=date(2024, 3, 1),
        disposition=Disposition.denied,
    )
    annotation = sg_office_annotations(row, None)
    assert (annotation.respondent, annotation.private_practice) == ("no", 0)


def test_a_successor_signing_after_the_resolution_counts_on_a_federal_party_only() -> None:
    """A docket closed before the span opened: the office for the government, not for a firm."""
    federal = _row(
        _counsel("D. John Sauer", "Federal Respondents"),
        date_filed=date(2024, 12, 2),
        date_cert_denied=date(2025, 2, 24),
        disposition=Disposition.denied,
    )
    assert sg_office_annotations(federal, None).respondent == "yes"
    # ...but not at a cut taken before the successor took office.
    assert sg_office_annotations(federal, date(2025, 3, 1)).respondent == "no"


def test_amicus_entries_are_never_read() -> None:
    """The office as `other` (amicus, invited brief) leaves both sides untouched."""
    row = _row(
        _counsel("Jane Roe", "Acme Corp.", role="petitioner"),
        _counsel("D. John Sauer", "United States", role="other"),
        date_filed=date(2025, 6, 1),
        date_cert_granted=date(2025, 10, 1),
        disposition=Disposition.granted,
    )
    annotation = sg_office_annotations(row, None)
    assert (annotation.petitioner, annotation.respondent, annotation.side) == ("no", "no", "none")


def test_a_row_without_side_counsel_is_unknown_not_no() -> None:
    """The index gap (resolved IFP rows carry no counsel) reads unknown."""
    bare = _row(
        docket_number="24-5001",
        date_filed=date(2024, 6, 1),
        date_cert_denied=date(2024, 10, 7),
        disposition=Disposition.denied,
    )
    only_amicus = _row(
        _counsel("D. John Sauer", "United States", role="other"),
        date_filed=date(2025, 6, 1),
    )
    for row in (bare, only_amicus):
        annotation = sg_office_annotations(row, None)
        assert (annotation.petitioner, annotation.respondent, annotation.side) == (
            "unknown",
            "unknown",
            "unknown",
        )


def test_an_undated_roster_name_is_unknown() -> None:
    row = _row(
        _counsel("Jane Roe", "Doe", role="petitioner"),
        _counsel("D. John Sauer", "United States"),
    )
    annotation = sg_office_annotations(row, None)
    assert (annotation.petitioner, annotation.respondent, annotation.side) == (
        "no",
        "unknown",
        "unknown",
    )


def test_a_granted_docket_lives_a_merits_span_past_the_grant() -> None:
    row = _row(date_filed=date(2024, 1, 2), date_cert_granted=date(2024, 2, 28))
    assert docket_life(row, None).end == date(2024, 2, 28) + MERITS_SPAN
    assert docket_life(row, date(2024, 6, 1)).end == date(2024, 6, 1)
    pending = _row(date_filed=date(2026, 8, 1))
    assert docket_life(pending, None).end is None


def test_the_version_stamp_and_the_registry() -> None:
    row = _row(
        _counsel("Elizabeth B. Prelogar", "United States", role="petitioner"),
        _counsel("Elizabeth B. Prelogar", "Garland, Att&#x27;y Gen."),
        date_filed=date(2022, 1, 5),
        date_cert_granted=date(2022, 3, 1),
        disposition=Disposition.granted,
    )
    annotation = counsel_rule(SG_OFFICE_RULE_VERSION)(row, None)
    assert annotation.rule_version == SG_OFFICE_RULE_VERSION == "sg-office-v1"
    assert annotation.side == "both"
    assert list(COUNSEL_RULES) == ["sg-office-v1"]
    with pytest.raises(KeyError):
        counsel_rule("sg-office-v9")


def _rates_corpus(db: Path) -> None:
    rows = [
        _row(  # caption names no federal party; the office answers for a court
            _counsel("Elizabeth B. Prelogar", "United States Court of Appeals"),
            case_id="scotus/1",
            docket_number="22-100",
            case_name="In re John Doe",
            date_filed=date(2022, 1, 5),
            date_cert_denied=date(2022, 3, 1),
            disposition=Disposition.denied,
        ),
        _row(  # a former SG for a private petitioner
            _counsel("Noel J. Francisco", "Acme Corp.", role="petitioner"),
            _counsel("Jane Roe", "John Doe"),
            case_id="scotus/2",
            docket_number="22-200",
            case_name="Acme Corp. v. John Doe",
            date_filed=date(2022, 2, 5),
            date_cert_granted=date(2022, 5, 1),
            disposition=Disposition.granted,
        ),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)


def test_party_rates_keys_cells_on_the_counsel_side_only_when_asked(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _rates_corpus(db)
    with corpus.connect(db) as conn:
        plain = party_rates(conn, as_of_field="filed")
        keyed = party_rates(conn, as_of_field="filed", counsel_rule_version="sg-office-v1")
        with pytest.raises(KeyError):
            party_rates(conn, as_of_field="filed", counsel_rule_version="sg-office-v9")
    assert plain.counsel_rule_version is None
    assert {cell.sg_counsel for cell in plain.cells} == {None}
    assert keyed.counsel_rule_version == "sg-office-v1"
    assert keyed.counsel_private_practice == 1
    cells = {(c.federal_party, c.sg_counsel): c for c in keyed.cells}
    assert cells[("none", "respondent")].rows == 1
    assert cells[("none", "none")].granted == 1


def test_the_command_prints_the_counsel_side(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus_root = tmp_path / "corpus"
    _rates_corpus(corpus.corpus_db_path(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = runner.invoke(
        app, ["party-rates", "--as-of", "filed", "--counsel-rule", "sg-office-v1"]
    )
    assert result.exit_code == 0, result.output
    assert "counsel rule sg-office-v1: 1 rated row(s)" in result.stderr
    assert "biden-46 paid-cert federal-none sg-counsel-respondent: granted 0/1" in result.stderr
    assert json.loads(result.stdout)["counsel_rule_version"] == "sg-office-v1"
    refused = runner.invoke(
        app, ["party-rates", "--as-of", "filed", "--counsel-rule", "sg-office-v9"]
    )
    assert refused.exit_code == 2
    assert "unregistered counsel rule" in refused.stderr


def test_a_resolved_row_without_a_closing_date_is_not_open_ended() -> None:
    """Decided, no date: a span opening after the filing cannot be placed on it."""
    future = _row(
        _counsel("D. John Sauer", "State of Missouri"),
        date_filed=date(2019, 2, 3),
        disposition=Disposition.denied,
    )
    annotation = sg_office_annotations(future, None)
    assert (annotation.respondent, annotation.side, annotation.private_practice) == (
        "unknown",
        "unknown",
        0,
    )
    in_office = _row(
        _counsel("Noel John Francisco", "United States"),
        date_filed=date(2018, 2, 3),
        disposition=Disposition.denied,
    )
    assert sg_office_annotations(in_office, None).respondent == "yes"


def test_party_rates_reads_counsel_at_the_cut(tmp_path: Path) -> None:
    """A cut before the successor took office: the late write is not the office yet."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    _counsel("D. John Sauer", "Federal Respondents"),
                    docket_number="24-593",
                    case_name="Jane Doe v. Acme Corp.",
                    date_filed=date(2024, 12, 2),
                    date_cert_denied=date(2025, 2, 24),
                    disposition=Disposition.denied,
                )
            ],
        )
        early = party_rates(
            conn,
            as_of_field="filed",
            through=date(2025, 3, 1),
            counsel_rule_version="sg-office-v1",
        )
        late = party_rates(conn, as_of_field="filed", counsel_rule_version="sg-office-v1")
    assert [(c.sg_counsel, c.resolved) for c in early.cells] == [("none", 1)]
    assert early.counsel_private_practice == 1
    assert [(c.sg_counsel, c.resolved) for c in late.cells] == [("respondent", 1)]
