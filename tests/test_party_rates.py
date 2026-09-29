"""Fixture-pinned tests for the party rates cut (`pipeline.party_rates`).

The cut publishes shares, so the fixtures pin the parts of a share a reader
cannot see from the number: which rows are in the denominator (substantive asks
only, one row per docket, pending and unreadable rows outside), how the sampled
denial block is restored to full strength, and what `--through` does to an
outcome dated after the cut.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.party_rates import DEFAULT_RATES_RULE, party_rates
from fedcourtsai.schemas import Disposition, PartyRateCell, PartyRates

runner = CliRunner()


def _row(case_id: str, case_name: str, **kwargs: object) -> corpus.CorpusRow:
    """One live-slice SCOTUS row: `last_live_polled` is what puts it in the slice."""
    return corpus.CorpusRow(
        case_id=case_id,
        court="scotus",
        case_name=case_name,
        last_live_polled=date(2026, 9, 1),
        **kwargs,
    )


def _rates_corpus(db: Path) -> None:
    """Three federal-applicant applications, a duplicate, the exclusions, cert rows."""
    rows = [
        _row(  # granted substantive ask, the DHS caption shape party-v1 misses
            "scotus/1",
            "Kristi Noem, Secretary, Department of Homeland Security, et al. v. Jane Doe",
            docket_number="24A100",
            date_filed=date(2025, 3, 1),
            date_decided=date(2025, 4, 1),
            disposition=Disposition.granted,
            application_kind="substantive",
        ),
        _row(  # the same docket under a second case id: counted once
            "scotus/9",
            "Kristi Noem, Secretary, Department of Homeland Security, et al. v. Jane Doe",
            docket_number="24A100",
            date_filed=date(2025, 3, 1),
            date_decided=date(2025, 4, 1),
            disposition=Disposition.granted,
            application_kind="substantive",
        ),
        _row(  # denied substantive ask
            "scotus/2",
            "United States v. Acme Corp.",
            docket_number="24A200",
            date_filed=date(2025, 5, 1),
            date_decided=date(2025, 5, 20),
            disposition=Disposition.denied,
            application_kind="substantive",
        ),
        _row(  # decided after the replication moment below
            "scotus/3",
            "United States v. Roe",
            docket_number="25A300",
            date_filed=date(2025, 9, 1),
            date_decided=date(2025, 11, 1),
            disposition=Disposition.granted,
            application_kind="substantive",
        ),
        _row(  # an extension: beside the cell, never in its rate
            "scotus/4",
            "United States v. Poe",
            docket_number="25A400",
            date_filed=date(2025, 6, 1),
            date_decided=date(2025, 6, 2),
            disposition=Disposition.granted,
            application_kind="extension",
        ),
        _row(  # a never-parsed application
            "scotus/5",
            "United States v. Moe",
            docket_number="25A500",
            date_filed=date(2025, 6, 1),
        ),
        _row(  # paid cert, SG petitioner, a GVR — the granted side of the binary
            "scotus/6",
            "United States v. Jane Doe",
            docket_number="18-100",
            date_filed=date(2019, 6, 1),
            date_cert_granted=date(2019, 10, 1),
            disposition=Disposition.gvr,
        ),
        _row(  # IFP cert against the government, one frame grant
            "scotus/7",
            "John Roe v. United States",
            docket_number="18-5001",
            date_filed=date(2019, 6, 1),
            date_cert_granted=date(2019, 10, 1),
            disposition=Disposition.granted,
        ),
        _row(  # ...and one sampled denial standing for ten
            "scotus/8",
            "John Poe v. United States",
            docket_number="18-5010",
            date_filed=date(2019, 6, 1),
            date_cert_denied=date(2019, 10, 1),
            disposition=Disposition.denied,
            sample_weight=10,
        ),
        _row(  # decided, label unreadable: outside the rate, not a denial
            "scotus/10",
            "Jane Doe v. United States",
            docket_number="18-200",
            date_filed=date(2019, 6, 1),
            date_cert_denied=date(2019, 10, 1),
            disposition=Disposition.other,
        ),
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)


def _cells(rates: PartyRates) -> dict[tuple[str | None, str, str], PartyRateCell]:
    return {(c.administration, c.stratum, c.federal_party): c for c in rates.cells}


def test_every_rate_carries_its_numerator_and_denominator(tmp_path: Path) -> None:
    """The application cell: substantive asks only, one row per docket."""
    db = tmp_path / "corpus.db"
    _rates_corpus(db)
    with corpus.connect(db) as conn:
        rates = party_rates(conn, as_of_field="filed")
    assert rates.rule_version == DEFAULT_RATES_RULE == "party-v2"
    assert rates.duplicate_rows == 1
    cell = _cells(rates)[("trump-47", "application", "petitioner")]
    assert (cell.rows, cell.resolved, cell.granted) == (3, 3, 2)
    assert cell.grant_rate == pytest.approx(2 / 3)
    assert cell.dispositions == {"denied": 1, "granted": 2}
    assert (cell.excluded_extension, cell.excluded_unknown_ask, cell.excluded_unparsed) == (
        1,
        0,
        1,
    )


def test_the_sampled_block_counts_at_its_weight(tmp_path: Path) -> None:
    """A sampled denial is ten denials in the rate, one row in the raw pair."""
    db = tmp_path / "corpus.db"
    _rates_corpus(db)
    with corpus.connect(db) as conn:
        rates = party_rates(conn, as_of_field="filed")
    cells = _cells(rates)
    ifp = cells[("trump-45", "ifp-cert", "respondent")]
    assert (ifp.rows, ifp.sampled_rows, ifp.resolved, ifp.granted) == (2, 1, 2, 1)
    assert (ifp.weighted_resolved, ifp.weighted_granted) == (11, 1)
    assert ifp.grant_rate == pytest.approx(1 / 11)
    paid = cells[("trump-45", "paid-cert", "petitioner")]
    assert (paid.granted, paid.resolved, paid.grant_rate) == (1, 1, 1.0)
    unreadable = cells[("trump-45", "paid-cert", "respondent")]
    assert (unreadable.unreadable, unreadable.resolved, unreadable.grant_rate) == (1, 0, None)
    assert "gvr" in rates.granted_labels


def test_through_places_the_cut_at_a_past_moment(tmp_path: Path) -> None:
    """Rows filed later leave; an outcome dated later reads as pending."""
    db = tmp_path / "corpus.db"
    _rates_corpus(db)
    with corpus.connect(db) as conn:
        at_october = party_rates(conn, as_of_field="filed", through=date(2025, 10, 1))
        at_april = party_rates(conn, as_of_field="filed", through=date(2025, 4, 15))
    cell = _cells(at_october)[("trump-47", "application", "petitioner")]
    assert (cell.rows, cell.pending, cell.resolved, cell.granted) == (3, 1, 2, 1)
    early = _cells(at_april)[("trump-47", "application", "petitioner")]
    assert (early.rows, early.resolved, early.granted) == (1, 1, 1)
    # Filed after the April cut: the denied ask, the Roe ask, the extension and
    # the never-parsed one.
    assert at_april.filed_after_through == 4


def test_since_bounds_the_cut_from_below(tmp_path: Path) -> None:
    """Rows filed before `since` leave, so a coverage start can bound both cells."""
    db = tmp_path / "corpus.db"
    _rates_corpus(db)
    with corpus.connect(db) as conn:
        rates = party_rates(conn, as_of_field="filed", since=date(2025, 4, 18))
    cell = _cells(rates)[("trump-47", "application", "petitioner")]
    # The March DHS ask leaves; the May and September asks stay.
    assert (cell.rows, cell.resolved, cell.granted) == (2, 2, 1)
    assert rates.since == date(2025, 4, 18)
    # Before the bound: the March ask (its duplicate is dropped first) and the
    # four 2019 cert rows.
    assert rates.filed_before_since == 5


def test_a_sampled_row_decided_after_the_cut_is_pending(tmp_path: Path) -> None:
    """Under `through` a sampled denial dated later drops out of both pairs."""
    db = tmp_path / "corpus.db"
    _rates_corpus(db)
    with corpus.connect(db) as conn:
        rates = party_rates(conn, as_of_field="filed", through=date(2019, 9, 1))
    ifp = _cells(rates)[("trump-45", "ifp-cert", "respondent")]
    assert (ifp.rows, ifp.sampled_rows, ifp.pending) == (2, 1, 2)
    assert (ifp.weighted_resolved, ifp.grant_rate) == (0, None)


def test_the_resolved_convention_moves_pending_rows_to_unattributed(tmp_path: Path) -> None:
    """Under `resolved` a row with no outcome at the cut has no date to attribute."""
    db = tmp_path / "corpus.db"
    _rates_corpus(db)
    with corpus.connect(db) as conn:
        rates = party_rates(conn, as_of_field="resolved", through=date(2025, 10, 1))
        with pytest.raises(ValueError, match="unknown as-of field"):
            party_rates(conn, as_of_field="argued")
        with pytest.raises(KeyError):
            party_rates(conn, as_of_field="filed", rule_version="party-v9")
    cells = _cells(rates)
    assert cells[(None, "application", "petitioner")].pending == 1
    assert cells[("trump-47", "application", "petitioner")].resolved == 2


def test_party_v1_reads_the_dhs_caption_as_non_federal(tmp_path: Path) -> None:
    """The reason the cut defaults to party-v2, pinned: v1 drops the DHS application."""
    db = tmp_path / "corpus.db"
    _rates_corpus(db)
    with corpus.connect(db) as conn:
        v1 = party_rates(conn, as_of_field="filed", rule_version="party-v1")
    cells = _cells(v1)
    assert cells[("trump-47", "application", "petitioner")].rows == 2
    assert cells[("trump-47", "application", "none")].rows == 1


def test_the_command_prints_the_rates_with_its_vintage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """JSON on stdout; the human cut, each share with its pair, and the vintage on stderr."""
    corpus_root = tmp_path / "corpus"
    _rates_corpus(corpus.corpus_db_path(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = runner.invoke(app, ["party-rates", "--as-of", "filed", "--through", "2025-10-01"])
    assert result.exit_code == 0, result.output
    assert "party rates (party-v2 over caption-v2, as-of filed, through 2025-10-01)" in (
        result.stderr
    )
    assert "corpus latest pull never pulled" in result.stderr
    assert "trump-47 application federal-petitioner: granted 1/2 = 50.0%" in result.stderr
    assert "granted 1/11 = 9.1% (raw 1/2, 1 sampled row(s) counted at their weight)" in (
        result.stderr
    )
    payload = json.loads(result.stdout)
    assert payload["through"] == "2025-10-01"
    assert payload["as_of_field"] == "filed"


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--as-of", "argued"], "unknown --as-of"),
        (["--as-of", "filed", "--rule-version", "party-v9"], "unregistered party rule"),
        (["--as-of", "filed", "--through", "October"], "unreadable --through"),
        (["--as-of", "filed", "--since", "April"], "unreadable --since"),
    ],
)
def test_the_command_refuses_what_it_cannot_cut(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, args: list[str], message: str
) -> None:
    corpus_root = tmp_path / "corpus"
    _rates_corpus(corpus.corpus_db_path(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = runner.invoke(app, ["party-rates", *args])
    assert result.exit_code == 2
    assert message in result.stderr


def test_the_command_fails_loud_without_a_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "empty"))
    result = runner.invoke(app, ["party-rates", "--as-of", "filed"])
    assert result.exit_code == 1
    assert "the corpus database is missing" in result.stderr
