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
    AMICUS_LINE_RULE,
    AmicusLineForecast,
    arm_of,
    build_fit,
    fit_digest,
    fit_rows,
    forecast,
    freeze,
    pools,
    verify,
)
from fedcourtsai.cli import app
from fedcourtsai.pipeline.salience import registered_versions, scorer
from fedcourtsai.schemas import (
    AmicusLineCell,
    AmicusLineFit,
    CertAnchor,
    Disposition,
    PredictionContext,
)
from tests.conftest import FixtureCorpus

runner = CliRunner()

# The active version, read through the scorer rather than imported by value.
SALIENCE_VERSION = scorer().version
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
    # The same fit's band rate, both arms pooled: 7 grants over 110 read rows.
    assert weakest["none"].unsplit_rate == pytest.approx(7 / 110)
    assert weakest["some"].unsplit_rate == weakest["none"].unsplit_rate
    assert weakest["none"].unread_resolved == 0


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
    assert payload["rule"] == AMICUS_LINE_RULE
    assert payload["min_resolved"] == AMICUS_LINE_MIN_RESOLVED
    assert {cell["salience_version"] for cell in payload["cells"]} == {SALIENCE_VERSION}
    weakest = next(cell for cell in payload["cells"] if cell["band"] == _WEAKEST)
    assert (weakest["none_resolved"], weakest["some_resolved"]) == (1, 1)
    assert len(payload["pools"]) == 2 * len(scorer(SALIENCE_VERSION).bands)
    assert json.loads(runner.invoke(app, ["amicus-line-fit"]).stdout)["pools"] == []


def test_the_forecast_ignores_another_band_and_another_version() -> None:
    other_band = _fit(2025, none=(500, 400), some=(500, 400)).model_copy(update={"band": "x"})
    other_version = _fit(2025, none=(500, 400), some=(500, 400)).model_copy(
        update={"salience_version": "sal-x"}
    )
    read = _forecast(
        [other_band, other_version, _fit(2025, none=(100, 2), some=(0, 0))], term=2026, amicus=0
    )
    assert (read.basis, read.arm_resolved) == ("arm", 100)
    assert read.rate == pytest.approx(0.02)


def _committed_fit(*cells: AmicusLineCell) -> AmicusLineFit:
    return AmicusLineFit(
        rule=AMICUS_LINE_RULE, min_resolved=AMICUS_LINE_MIN_RESOLVED, cells=list(cells)
    )


def _context(count: int | None = 0, *, term: int | None = 2026) -> PredictionContext:
    return PredictionContext(
        mode="forward",
        snapshot_date=date(2026, 10, 1),
        signals_observable=True,
        distribution_count=1,
        band=_WEAKEST,
        salience_version=SALIENCE_VERSION,
        term=term,
        cert_amicus_briefs=count,
    )


_ANCHOR = CertAnchor(rate=0.05, statpack_digest="sha256:pack", lookback_terms=10)


def test_the_committed_fit_is_the_rows_fit_under_the_rule() -> None:
    rows = [_row(1, amicus=0), _row(2, amicus=2, disposition=Disposition.granted)]
    fit = build_fit(rows)
    assert (fit.rule, fit.min_resolved) == (AMICUS_LINE_RULE, AMICUS_LINE_MIN_RESOLVED)
    assert fit.cells == fit_rows(rows)
    # The digest names the counts, not the serialisation.
    assert fit_digest(fit) == fit_digest(AmicusLineFit.model_validate_json(fit.model_dump_json()))
    assert fit_digest(fit) != fit_digest(build_fit(rows[:1]))


def test_freezing_pools_the_cells_arm_under_the_anchors_window() -> None:
    fit = _committed_fit(
        _fit(2025, none=(40, 2), some=(40, 10)),
        _fit(2026, none=(40, 40), some=(40, 40)),  # the cell's own Term: never pooled
        _fit(2010, none=(40, 40), some=(40, 40)),  # outside the anchor's ten Terms
    )
    none = freeze(_context(0), fit, _ANCHOR)
    some = freeze(_context(3), fit, _ANCHOR)
    assert none is not None and some is not None
    assert (none.arm, none.basis, none.rate, none.arm_resolved) == ("none", "arm", 0.05, 40)
    assert (some.arm, some.basis, some.rate) == ("some", "arm", 0.25)
    assert none.rule == AMICUS_LINE_RULE
    assert none.fit_digest == fit_digest(fit)


def test_freezing_falls_back_to_the_anchors_rate_and_says_so() -> None:
    fit = _committed_fit(_fit(2025, none=(40, 2), some=(5, 5)))
    thin = freeze(_context(1), fit, _ANCHOR)
    assert thin is not None
    assert (thin.basis, thin.rate, thin.arm_resolved) == ("band-fallback", 0.05, 5)
    # An anchor whose own pool was empty leaves the fallback without a rate.
    empty = freeze(_context(1), fit, _ANCHOR.model_copy(update={"rate": None}))
    assert empty is not None and empty.rate is None and empty.basis == "band-fallback"


def test_nothing_is_frozen_without_a_count_an_anchor_or_the_rules_own_fit() -> None:
    fit = _committed_fit(_fit(2025, none=(40, 2), some=(40, 10)))
    assert freeze(_context(None), fit, _ANCHOR) is None
    assert freeze(_context(0), fit, None) is None
    assert freeze(_context(0, term=None), fit, _ANCHOR) is None
    assert freeze(_context(0), fit.model_copy(update={"rule": "amicus-line-v1"}), _ANCHOR) is None
    assert freeze(_context(0), fit.model_copy(update={"min_resolved": 1}), _ANCHOR) is None


def test_a_frozen_line_verifies_only_against_the_committed_fit_it_names() -> None:
    fit = _committed_fit(_fit(2025, none=(40, 2), some=(40, 10)))
    later = _committed_fit(_fit(2025, none=(40, 4), some=(40, 10)))
    context = _context(0)
    line = freeze(context, fit, _ANCHOR)
    assert line is not None
    committed = [later.model_dump_json(), fit.model_dump_json()]
    assert verify(line, context, _ANCHOR, committed) is None
    # No committed build, or none carrying the digest the record names.
    assert "no committed" in (verify(line, context, _ANCHOR, []) or "")
    assert "not a fit build in force" in (
        verify(line, context, _ANCHOR, [later.model_dump_json(), "not json"]) or ""
    )
    # A record naming a real build but a rate, arm or basis that build does not yield.
    for edit in ({"rate": 0.9}, {"arm": "some"}, {"basis": "band-fallback"}, {"arm_resolved": 7}):
        edited = line.model_copy(update=edit)
        assert "does not re-pool" in (verify(edited, context, _ANCHOR, committed) or "")
    # A count edited after freezing puts the cell in the other arm: refused.
    assert "does not re-pool" in (verify(line, _context(2), _ANCHOR, committed) or "")
