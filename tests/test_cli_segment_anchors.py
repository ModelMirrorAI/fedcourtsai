"""``fedcourts segment-anchors``: the pooled per-band anchors a cert cell is scored against."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.pipeline.base_rates import _pooled_band_rate
from fedcourtsai.pipeline.salience import SALIENCE_VERSION
from fedcourtsai.schemas import (
    BaseRateBucket,
    StatPack,
    StatPackTerm,
    StatPackTermSegment,
    StatPackTermVersionSegments,
)

runner = CliRunner()


def _segment(
    band: str, risk: tuple[float, int], terminal: tuple[float, int]
) -> StatPackTermSegment:
    return StatPackTermSegment(
        band=band,
        prefix_est_grant_rate=risk[0],
        prefix_weighted_resolved=risk[1],
        est_grant_rate=terminal[0],
        weighted_resolved=terminal[1],
    )


def _term(year: int, segments: list[StatPackTermSegment], *, version: str) -> StatPackTerm:
    return StatPackTerm(
        term=year, base_rates=BaseRateBucket(), salience_version=version, segments=segments
    )


@pytest.fixture
def _roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config = tmp_path / "config"
    config.mkdir()
    (config / "tracking.yaml").write_text("salience:\n  base_rate_lookback_terms: 2\n")
    metrics = tmp_path / "metrics"
    metrics.mkdir()
    (metrics / "statpack.json").write_text(_pack().model_dump_json())
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config))
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(metrics))
    return tmp_path


def _pack() -> StatPack:
    other = "sal-other"
    return StatPack(
        corpus_rows=1,
        terms=[
            # Carries the pinned version but nothing resolved: never listed as pooled.
            _term(
                2026,
                [
                    StatPackTermSegment(
                        band="elevated",
                        prefix_est_grant_rate=None,
                        prefix_weighted_resolved=0,
                        est_grant_rate=None,
                        weighted_resolved=0,
                    )
                ],
                version=SALIENCE_VERSION,
            ),
            # The case's own Term: never pooled for a 2025 docket.
            _term(2025, [_segment("elevated", (0.9, 100), (0.9, 50))], version=SALIENCE_VERSION),
            _term(
                2024,
                [
                    _segment("elevated", (0.2, 100), (0.1, 60)),
                    # A rate-less slice contributes to neither the rate nor its n.
                    StatPackTermSegment(
                        band="baseline",
                        prefix_est_grant_rate=None,
                        prefix_weighted_resolved=77,
                        est_grant_rate=None,
                        weighted_resolved=55,
                    ),
                ],
                version=SALIENCE_VERSION,
            ),
            # Carries the pinned version only as an alt block.
            StatPackTerm(
                term=2023,
                base_rates=BaseRateBucket(),
                salience_version=other,
                segments=[_segment("elevated", (0.7, 999), (0.7, 999))],
                alt_segments=[
                    StatPackTermVersionSegments(
                        salience_version=SALIENCE_VERSION,
                        segments=[_segment("elevated", (0.1, 300), (0.05, 140))],
                    )
                ],
            ),
            # Inside the window but carrying neither the pinned version nor an alt
            # block of it: never pooled, never listed.
            _term(2023, [_segment("elevated", (0.6, 500), (0.6, 500))], version="sal-none"),
            # Outside the two-Term window for a 2025 docket.
            _term(2022, [_segment("elevated", (0.5, 100), (0.5, 100))], version=SALIENCE_VERSION),
        ],
    )


@pytest.mark.usefixtures("_roots")
def test_pools_strictly_prior_terms_in_the_window_under_the_pinned_version() -> None:
    result = runner.invoke(app, ["segment-anchors", "--term", "2025", "--term", "2026"])
    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert report["base_rate_lookback_terms"] == 2
    by_term = {a["docket_term"]: a for a in report["anchors"]}

    ot25 = by_term[2025]
    assert ot25["pooled_terms"] == [2023, 2024]
    elevated = ot25["bands"]["elevated"]
    assert elevated["risk_set"] == pytest.approx((0.2 * 100 + 0.1 * 300) / 400)
    assert elevated["risk_set_weighted_resolved"] == 400
    assert elevated["terminal"] == pytest.approx((0.1 * 60 + 0.05 * 140) / 200)
    assert elevated["terminal_weighted_resolved"] == 200
    baseline = ot25["bands"]["baseline"]
    assert baseline == {
        "risk_set": None,
        "terminal": None,
        "risk_set_weighted_resolved": 0,
        "terminal_weighted_resolved": 0,
    }

    # Every printed rate is the scorer's own pooler on the same pack.
    pack = _pack()
    for anchor in report["anchors"]:
        for band, figures in anchor["bands"].items():
            for basis in ("risk_set", "terminal"):
                assert figures[basis] == _pooled_band_rate(
                    band,
                    SALIENCE_VERSION,
                    anchor["docket_term"],
                    pack,
                    lookback_terms=2,
                    risk_set=basis == "risk_set",
                )

    # A Term later, the window slides: 2025 joins and 2023 falls out.
    ot26 = by_term[2026]
    assert ot26["pooled_terms"] == [2024, 2025]
    assert ot26["bands"]["elevated"]["risk_set"] == pytest.approx((0.2 * 100 + 0.9 * 100) / 200)


def test_an_unreadable_statpack_exits_1(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["segment-anchors", "--term", "2025", "--statpack", str(tmp_path / "missing.json")]
    )
    assert result.exit_code == 1


@pytest.mark.usefixtures("_roots")
def test_a_term_that_contributed_nothing_is_not_listed_as_pooled() -> None:
    result = runner.invoke(app, ["segment-anchors", "--term", "2027"])
    assert result.exit_code == 0, result.output
    (anchor,) = json.loads(result.stdout)["anchors"]
    assert anchor["pooled_terms"] == [2025]
    assert anchor["bands"]["elevated"]["risk_set"] == pytest.approx(0.9)
