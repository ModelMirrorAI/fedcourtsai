"""The amicus-adjusted cert reference line: its fit, its pooling and its fallback."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import analytics, corpus
from fedcourtsai.amicus_line import (
    AMICUS_LINE_MIN_RESOLVED,
    AmicusLineCell,
    AmicusLineForecast,
    arm_of,
    fit_rows,
    forecast,
    pools,
)
from fedcourtsai.cli import app
from fedcourtsai.pipeline.salience import SALIENCE_VERSION, registered_versions, scorer
from fedcourtsai.schemas import Disposition
from tests.conftest import FixtureCorpus

runner = CliRunner()

_WEAKEST = scorer(SALIENCE_VERSION).bands[-1]


def _row(
    serial: int,
    *,
    term: int = 24,
    disposition: Disposition | None = Disposition.denied,
    amicus: int | None = 0,
    live: bool = True,
    weight: int | None = None,
) -> corpus.CorpusRow:
    return corpus.CorpusRow(
        case_id=f"scotus/{term}{serial:05d}",
        court="scotus",
        docket_number=f"{term}-{serial}",
        case_name="Doe v. Roe",
        disposition=disposition,
        cert_amicus_briefs=amicus,
        distribution_count=1,
        last_live_polled=date(2026, 1, 1) if live else None,
        sample_weight=weight,
    )


def _cell(cells: list[AmicusLineCell], term: int, band: str = _WEAKEST) -> AmicusLineCell:
    (found,) = (
        c
        for c in cells
        if c.term == term and c.band == band and c.salience_version == SALIENCE_VERSION
    )
    return found


def test_the_arms_are_none_against_one_or_more() -> None:
    assert [arm_of(n) for n in (0, 1, 2, 9)] == ["none", "some", "some", "some"]


def test_the_fit_cuts_a_risk_set_on_the_stored_count() -> None:
    rows = [
        _row(1, amicus=0),
        _row(2, amicus=0, disposition=Disposition.granted),
        _row(3, amicus=1, disposition=Disposition.granted),
        _row(4, amicus=3),
        _row(5, amicus=None),  # never read since the column existed: neither arm
        _row(6, disposition=None),  # pending: in no rate
        _row(7, live=False),  # outside the live slice the band rates pool
        _row(5001, amicus=2),  # an IFP serial: outside the scored segment
    ]
    cell = _cell(fit_rows(rows), 2024)
    assert (cell.none_resolved, cell.none_weighted_resolved, cell.none_weighted_grants) == (2, 2, 1)
    assert (cell.some_resolved, cell.some_weighted_resolved, cell.some_weighted_grants) == (2, 2, 1)
    assert cell.unread_resolved == 1


def test_the_fit_weights_as_the_band_rates_do() -> None:
    rows = [_row(1, weight=5), _row(2, weight=None, disposition=Disposition.granted)]
    cell = _cell(fit_rows(rows), 2024)
    assert (cell.none_resolved, cell.none_weighted_resolved, cell.none_weighted_grants) == (2, 6, 1)


def test_the_fit_sums_to_the_statpacks_risk_sets(fixture_corpus: FixtureCorpus) -> None:
    """Same population, same walk: the arms and the unread rows are the segment's risk set."""
    with corpus.connect_local_read(fixture_corpus.db_path) as conn:
        cells = fit_rows(corpus.iter_rows(conn))
    pack = analytics.build_statpack(corpus_db_path=fixture_corpus.db_path)
    published = {}
    for entry in pack.terms:
        blocks = [(entry.salience_version, entry.segments)]
        blocks += [(block.salience_version, block.segments) for block in entry.alt_segments]
        for version, segments in blocks:
            for seg in segments:
                if seg.prefix_resolved:
                    published[(entry.term, version, seg.band)] = seg.prefix_resolved
    assert published, "the fixture corpus resolves no scored-segment petition"
    assert {
        (c.term, c.salience_version, c.band): c.none_resolved + c.some_resolved + c.unread_resolved
        for c in cells
    } == published
    assert {c.salience_version for c in cells} <= set(registered_versions())


def _fit(term: int, *, none: tuple[int, int], some: tuple[int, int]) -> AmicusLineCell:
    return AmicusLineCell(
        term=term,
        salience_version=SALIENCE_VERSION,
        band=_WEAKEST,
        none_resolved=none[0],
        none_weighted_resolved=none[0],
        none_weighted_grants=none[1],
        some_resolved=some[0],
        some_weighted_resolved=some[0],
        some_weighted_grants=some[1],
        unread_resolved=0,
    )


def _forecast(
    fit: list[AmicusLineCell], *, term: int, amicus: int, lookback: int = 10
) -> AmicusLineForecast:
    return forecast(
        fit,
        band=_WEAKEST,
        salience_version=SALIENCE_VERSION,
        term=term,
        cert_amicus_briefs=amicus,
        band_rate=0.04,
        lookback_terms=lookback,
    )


def test_the_forecast_pools_strictly_prior_terms_inside_the_window() -> None:
    fit = [
        _fit(2026, none=(1000, 1000), some=(1000, 1000)),  # the cell's own Term: never read
        _fit(2025, none=(100, 2), some=(40, 8)),
        _fit(2024, none=(100, 4), some=(40, 12)),
        _fit(2010, none=(1000, 1000), some=(1000, 1000)),  # older than the window
    ]
    none = _forecast(fit, term=2026, amicus=0)
    some = _forecast(fit, term=2026, amicus=4)
    assert (none.basis, none.arm, none.arm_resolved) == ("arm", "none", 200)
    assert none.rate == pytest.approx(6 / 200)
    assert (some.basis, some.arm, some.arm_resolved) == ("arm", "some", 80)
    assert some.rate == pytest.approx(20 / 80)
    # No window: the old Term joins the pool.
    unbounded = _forecast(fit, term=2026, amicus=0, lookback=0)
    assert unbounded.arm_resolved == 1200


def test_a_thin_arm_falls_back_to_the_band_rate() -> None:
    fit = [_fit(2025, none=(500, 10), some=(AMICUS_LINE_MIN_RESOLVED - 1, 20))]
    thin = _forecast(fit, term=2026, amicus=1)
    assert (thin.basis, thin.rate, thin.arm_resolved) == (
        "band-fallback",
        0.04,
        AMICUS_LINE_MIN_RESOLVED - 1,
    )
    # The other arm is judged on its own count.
    full = _forecast(fit, term=2026, amicus=0)
    assert full.basis == "arm"
    # At the minimum exactly, the arm's rate is used.
    at = _forecast(
        [_fit(2025, none=(500, 10), some=(AMICUS_LINE_MIN_RESOLVED, 15))], term=2026, amicus=1
    )
    assert at.basis == "arm"
    assert at.rate == pytest.approx(15 / AMICUS_LINE_MIN_RESOLVED)


def test_an_empty_pool_falls_back() -> None:
    empty = _forecast([], term=2026, amicus=0)
    assert (empty.basis, empty.rate, empty.arm_resolved) == ("band-fallback", 0.04, 0)


def test_the_pools_table_lists_both_arms_of_every_band() -> None:
    table = pools(
        [_fit(2025, none=(100, 2), some=(10, 5))],
        salience_version=SALIENCE_VERSION,
        term=2026,
        lookback_terms=10,
    )
    assert [(p.band, p.arm) for p in table] == [
        (band, arm) for band in scorer(SALIENCE_VERSION).bands for arm in ("none", "some")
    ]
    weakest = {p.arm: p for p in table if p.band == _WEAKEST}
    assert weakest["none"].rate == pytest.approx(0.02)
    assert weakest["none"].meets_minimum is True
    # A thin arm's rate is printed, and marked as one the line would not use.
    assert weakest["some"].rate == pytest.approx(0.5)
    assert weakest["some"].meets_minimum is False
    assert weakest["some"].terms == [2025]


def test_the_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    assert runner.invoke(app, ["amicus-line-fit"]).exit_code == 1  # no corpus yet
    (tmp_path / "corpus").mkdir()
    with corpus.connect(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
        corpus.upsert_rows(conn, [_row(1, amicus=0), _row(2, amicus=2)])
    assert runner.invoke(app, ["amicus-line-fit", "--salience-version", "nope"]).exit_code == 2
    result = runner.invoke(app, ["amicus-line-fit", "--before-term", "2026"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["rule"] == "amicus-line-v1"
    assert payload["min_resolved"] == AMICUS_LINE_MIN_RESOLVED
    assert {cell["salience_version"] for cell in payload["cells"]} == {SALIENCE_VERSION}
    weakest = next(cell for cell in payload["cells"] if cell["band"] == _WEAKEST)
    assert (weakest["none_resolved"], weakest["some_resolved"]) == (1, 1)
    assert len(payload["pools"]) == 2 * len(scorer(SALIENCE_VERSION).bands)
    assert runner.invoke(app, ["amicus-line-fit"]).stdout.count('"pools": []') == 1
