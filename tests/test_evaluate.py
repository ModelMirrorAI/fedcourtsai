"""Tests for the deterministic evaluate helpers, focused on the segment baseline.

`is_correct` / `brier_score` / `vote_accuracy` are exercised through the runner
and leaderboard suites; here we pin the two segment-baseline helpers, whose whole
point is a *leakage-safe* skill score keyed on the salience band.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.evaluate import (
    brier_skill_score,
    prediction_base_rate,
    segment_base_rate,
)
from fedcourtsai.pipeline.salience import salience_band
from fedcourtsai.schemas import (
    BaseRateBucket,
    Disposition,
    Engine,
    Outcome,
    Prediction,
    PredictionContext,
    StatPack,
    StatPackTerm,
    StatPackTermSegment,
)


def _term(
    year: int, band_rates: dict[str, tuple[float, int]], *, version: str = "sal-v1"
) -> StatPackTerm:
    """A Term whose bands carry ``(rate, weighted_resolved)``.

    The rate is written to **both** the terminal and the risk-set field, so these
    fixtures exercise the pooling arithmetic without also encoding a
    prefix-versus-terminal gap. `test_the_baseline_reads_the_risk_set_rate` is
    where the two are deliberately set apart.
    """
    return StatPackTerm(
        term=year,
        base_rates=BaseRateBucket(),
        salience_version=version,
        segments=[
            StatPackTermSegment(
                band=band,
                weighted_resolved=n,
                est_grant_rate=rate,
                prefix_weighted_resolved=n,
                prefix_est_grant_rate=rate,
            )
            for band, (rate, n) in band_rates.items()
        ],
    )


def _statpack(*terms: StatPackTerm) -> StatPack:
    return StatPack(corpus_rows=1, terms=list(terms))


def _row(docket: str, *, distribution_count: int = 3, cvsg: bool = False) -> corpus.CorpusRow:
    # distribution_count=3 -> 2 relists -> the `high` band by default.
    return corpus.CorpusRow(
        case_id=f"scotus/{docket}",
        court="scotus",
        docket_number=docket,
        distribution_count=distribution_count,
        cvsg_date=date(2025, 1, 2) if cvsg else None,
    )


def _prediction(probability: float) -> Prediction:
    return Prediction(
        case_id="scotus/1",
        event_id="cert",
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2025, 1, 1),
        input_snapshot="x",
        granted=probability >= 0.5,
        probability=probability,
        predicted_disposition=Disposition.granted if probability >= 0.5 else Disposition.denied,
    )


def _outcome(granted: int) -> Outcome:
    return Outcome(
        case_id="scotus/1",
        event_id="cert",
        resolved_at=date(2025, 6, 1),
        actual_disposition=Disposition.granted if granted else Disposition.denied,
        actual_granted=granted,
    )


# --- segment_base_rate: the leakage-safe prior-Term band rate --------------------


def test_segment_base_rate_uses_only_terms_before_the_case_term() -> None:
    # A high-band OT24 case anchors on the pooled high-band rate over OT22+OT23,
    # never OT24's own (or a later Term's) rate — the leakage guard.
    pack = _statpack(
        _term(2024, {"high": (0.90, 100)}),  # the case's own Term: excluded
        _term(2023, {"high": (0.40, 100)}),
        _term(2022, {"high": (0.20, 100)}),
    )
    # Pooled weighted mean over OT22+OT23: (0.40*100 + 0.20*100)/200 = 0.30.
    assert segment_base_rate(_row("24-100"), pack) == pytest.approx(0.30)


def test_segment_base_rate_keys_on_the_cases_own_band() -> None:
    pack = _statpack(_term(2023, {"high": (0.40, 100), "baseline": (0.01, 100)}))
    high = segment_base_rate(_row("24-100", distribution_count=3), pack)  # 2 relists -> high
    baseline = segment_base_rate(
        _row("24-101", distribution_count=1), pack
    )  # 0 relists -> baseline
    assert high == pytest.approx(0.40)
    assert baseline == pytest.approx(0.01)


def test_segment_base_rate_none_when_no_prior_term_data() -> None:
    # Only the case's own Term is present -> nothing precedes it -> no base rate.
    pack = _statpack(_term(2024, {"high": (0.90, 100)}))
    assert segment_base_rate(_row("24-100"), pack) is None
    # And None for a docket with no derivable Term year.
    assert (
        segment_base_rate(_row("bare-docket"), _statpack(_term(2023, {"high": (0.4, 5)}))) is None
    )


def test_segment_base_rate_skips_bands_with_nothing_resolved() -> None:
    # A prior Term whose band resolved nothing (est_grant_rate None) contributes
    # no weight; the rate is still None when every prior Term is empty.
    pack = _statpack(_term(2023, {"high": (None, 0)}))  # type: ignore[dict-item]
    assert segment_base_rate(_row("24-100"), pack) is None


# --- the lookback window: `salience.base_rate_lookback_terms` --------------------


def test_the_default_lookback_pools_every_prior_term() -> None:
    # The shipped default is unbounded, and it must stay that way silently: this
    # pins that the bare call and an explicit 0 agree, and that both reach the
    # oldest Term in the pack.
    pack = _statpack(
        _term(2024, {"high": (0.40, 100)}),
        _term(2023, {"high": (0.20, 100)}),
        _term(2018, {"high": (0.60, 100)}),  # six Terms back — still pooled
    )
    unbounded = segment_base_rate(_row("25-100"), pack)
    assert unbounded == pytest.approx(0.40)  # (0.40 + 0.20 + 0.60) * 100 / 300
    assert segment_base_rate(_row("25-100"), pack, lookback_terms=0) == unbounded


def test_the_lookback_window_bounds_the_pool() -> None:
    pack = _statpack(
        _term(2024, {"high": (0.40, 100)}),
        _term(2023, {"high": (0.20, 100)}),
        _term(2022, {"high": (0.90, 100)}),  # outside a 2-Term window
    )
    # OT25 case, lookback 2 -> OT24 + OT23 only: (0.40 + 0.20) * 100 / 200 = 0.30.
    assert segment_base_rate(_row("25-100"), pack, lookback_terms=2) == pytest.approx(0.30)


def test_the_lookback_is_a_term_year_band_not_a_rank_slice() -> None:
    # OT2023 is absent from the pack. A rank slice would take the two most recent
    # prior *rows* (OT24 + OT22) and quietly reach outside the stated window; the
    # year band takes OT24 alone and shrinks the sample honestly. Published skill
    # numbers must not move because the walker's coverage changed.
    pack = _statpack(
        _term(2024, {"high": (0.40, 100)}),
        _term(2022, {"high": (0.90, 100)}),
        _term(2021, {"high": (0.90, 100)}),
    )
    assert segment_base_rate(_row("25-100"), pack, lookback_terms=2) == pytest.approx(0.40)


def test_a_zero_row_cursor_term_inside_the_window_does_not_extend_it() -> None:
    # Cursor-only Terms appear in the pack for every band with no resolved rows.
    # One inside the window contributes no weight and must not push the floor back
    # to admit an older Term — the failure mode a rank slice would have.
    pack = _statpack(
        _term(2024, {"high": (0.40, 100)}),
        _term(2023, {"high": (None, 0)}),  # type: ignore[dict-item]
        _term(2022, {"high": (0.90, 100)}),
    )
    assert segment_base_rate(_row("25-100"), pack, lookback_terms=2) == pytest.approx(0.40)


def test_the_window_never_reaches_the_cases_own_term() -> None:
    # The leakage guard is not a lookback bound and cannot be widened past it.
    pack = _statpack(
        _term(2026, {"high": (0.99, 100)}),  # later than the case: excluded
        _term(2025, {"high": (0.99, 100)}),  # the case's own Term: excluded
        _term(2024, {"high": (0.40, 100)}),
    )
    assert segment_base_rate(_row("25-100"), pack, lookback_terms=50) == pytest.approx(0.40)


# --- brier_skill_score: lift over the naive base-rate forecaster -----------------


def test_parroting_the_base_rate_scores_zero_skill() -> None:
    # probability == base_rate -> pred Brier == baseline Brier -> skill 0.
    skill = brier_skill_score(_prediction(0.30), _outcome(1), base_rate=0.30)
    assert skill == pytest.approx(0.0)


def test_beating_the_base_rate_scores_positive_skill() -> None:
    # A confident correct grant call beats the 0.30 baseline on a granted outcome.
    skill = brier_skill_score(_prediction(0.90), _outcome(1), base_rate=0.30)
    assert skill is not None and skill > 0
    # 1 - (0.9-1)^2 / (0.3-1)^2 = 1 - 0.01/0.49.
    assert skill == pytest.approx(1 - 0.01 / 0.49)


def test_worse_than_the_base_rate_scores_negative_skill() -> None:
    skill = brier_skill_score(_prediction(0.10), _outcome(1), base_rate=0.30)
    assert skill is not None and skill < 0


def test_brier_skill_none_without_a_base_rate_or_on_a_perfect_baseline() -> None:
    assert brier_skill_score(_prediction(0.9), _outcome(1), base_rate=None) is None
    # A base rate that already resolved the outcome exactly (1.0 on a grant) makes
    # the baseline Brier zero -> skill undefined -> None (no divide-by-zero).
    assert brier_skill_score(_prediction(0.9), _outcome(1), base_rate=1.0) is None


def test_the_baseline_matches_the_band_it_is_grouped_by() -> None:
    """Baseline and grouping have to agree, and today both are terminal.

    `segment_base_rate` derives the band from the row as it stands now — for a
    resolved case, its terminal band — so it must read the rate over rows that
    *ended* in that band. The risk-set rate is published beside it and is several
    times higher in the weak bands, but reading it against a terminal band would
    overstate the baseline for exactly the petitions whose band moved. Switching
    the read requires pinning the band as at prediction; the two go together.
    """
    term = StatPackTerm(
        term=2024,
        base_rates=BaseRateBucket(),
        salience_version="sal-v1",
        segments=[
            StatPackTermSegment(
                band="baseline",
                weighted_resolved=900,
                est_grant_rate=0.015,  # ended at baseline
                prefix_weighted_resolved=1300,
                prefix_est_grant_rate=0.069,  # ever reached baseline
            )
        ],
    )
    row = _row("25-100", distribution_count=1)  # OT2025, so OT2024 is prior
    assert salience_band(row) == "baseline"
    assert segment_base_rate(row, _statpack(term)) == pytest.approx(0.015)


def test_pooling_weights_by_the_denominator_of_the_rate_it_pools() -> None:
    """A Term contributes at the weight belonging to the rate being pooled. Mixing
    a terminal rate with a risk-set denominator (or the reverse) drifts the pooled
    figure without failing anything."""
    terms = [
        StatPackTerm(
            term=year,
            base_rates=BaseRateBucket(),
            salience_version="sal-v1",
            segments=[
                StatPackTermSegment(
                    band="baseline",
                    weighted_resolved=n,
                    est_grant_rate=rate,
                    prefix_weighted_resolved=1,  # decoy: wrong denominator if read
                    prefix_est_grant_rate=0.99,
                )
            ],
        )
        for year, rate, n in ((2022, 0.04, 100), (2023, 0.08, 300))
    ]
    # (0.04*100 + 0.08*300) / 400 = 0.07
    row = _row("25-100", distribution_count=1)
    assert segment_base_rate(row, _statpack(*terms)) == pytest.approx(0.07)


_DERIVE_FROM_BAND = object()


def _context(
    band: str | None,
    term: int | None = 2025,
    *,
    signals_observable: bool = True,
    salience_version: str | object | None = _DERIVE_FROM_BAND,
) -> PredictionContext:
    # The harness stamps `salience_version` whenever it derives a band
    # (cell_context.build), so the fixture mirrors that pairing by default.
    if salience_version is _DERIVE_FROM_BAND:
        salience_version = "sal-v1" if band else None
    assert salience_version is None or isinstance(salience_version, str)
    return PredictionContext(
        mode="forward",
        snapshot_date=date(2025, 3, 1),
        signals_observable=signals_observable,
        band=band,
        salience_version=salience_version,
        term=term,
    )


def _split_term(year: int, *, terminal: float, risk_set: float) -> StatPackTerm:
    """A Term whose two published rates disagree, so reading the wrong one fails."""
    return StatPackTerm(
        term=year,
        base_rates=BaseRateBucket(),
        salience_version="sal-v1",
        segments=[
            StatPackTermSegment(
                band="baseline",
                weighted_resolved=900,
                est_grant_rate=terminal,
                prefix_weighted_resolved=1300,
                prefix_est_grant_rate=risk_set,
            )
        ],
    )


def test_a_frozen_band_reads_the_risk_set_rate() -> None:
    """The pairing this change exists for: band as at prediction, rate over the
    population that had reached it. A cell at `baseline` may still relist, so the
    petitions it belongs with are everyone who reached `baseline`."""
    pack = _statpack(_split_term(2024, terminal=0.015, risk_set=0.069))
    assert prediction_base_rate(_context("baseline"), pack) == pytest.approx(0.069)


def test_a_row_derived_band_keeps_the_terminal_rate() -> None:
    """The other half of the pairing. `segment_base_rate` reads the band off the
    row, which for a resolved case is terminal — so it must pool the terminal
    rate. Mixing the two is what would overstate the baseline for exactly the
    petitions whose band moved."""
    pack = _statpack(_split_term(2024, terminal=0.015, risk_set=0.069))
    row = _row("25-100", distribution_count=1)
    assert segment_base_rate(row, pack) == pytest.approx(0.015)


def test_an_unobservable_band_yields_no_frozen_rate() -> None:
    """A replay snapshot with its proceedings stripped discloses no band. Falling
    back is honest; guessing `baseline` from the absence would invent a posture."""
    pack = _statpack(_split_term(2024, terminal=0.015, risk_set=0.069))
    assert prediction_base_rate(_context(None, signals_observable=False), pack) is None
    assert prediction_base_rate(None, pack) is None


def test_the_frozen_path_keeps_the_prior_term_guard() -> None:
    """Freezing the band must not loosen the leakage control: a cell's own Term
    and every later one still contribute nothing."""
    pack = _statpack(
        _split_term(2026, terminal=0.99, risk_set=0.99),  # later than the cell
        _split_term(2025, terminal=0.99, risk_set=0.99),  # the cell's own Term
        _split_term(2024, terminal=0.015, risk_set=0.069),
    )
    assert prediction_base_rate(_context("baseline", term=2025), pack) == pytest.approx(0.069)


# --- version-pinned pooling: a band name only means something under its scorer ----


def test_pooling_is_version_pinned_to_the_bands_scorer() -> None:
    """A sal-v2 `high` and a sal-v1 `high` are different populations sharing a
    label. A sal-v1 band must pool only the sal-v1 Terms — never a blend no
    version ever defined."""
    pack = _statpack(
        _term(2023, {"high": (0.30, 100)}),
        _term(2022, {"high": (0.60, 100)}, version="sal-v2"),
    )
    # Row-derived band: the live scorer is sal-v1, so only the sal-v1 Term pools.
    assert segment_base_rate(_row("24-100"), pack) == pytest.approx(0.30)
    # Frozen band: pinned to the version the cell actually froze.
    assert prediction_base_rate(_context("high", term=2024), pack) == pytest.approx(0.30)
    v2 = _context("high", term=2024, salience_version="sal-v2")
    assert prediction_base_rate(v2, pack) == pytest.approx(0.60)


def test_a_fully_mismatched_pack_yields_none_not_a_blend() -> None:
    """A statpack lagging the band's version has no honest baseline: the answer
    is the contracted `None`, not a silently pooled number."""
    pack = _statpack(_term(2023, {"high": (0.30, 100)}, version="sal-v0"))
    assert segment_base_rate(_row("24-100"), pack) is None
    assert prediction_base_rate(_context("high", term=2024), pack) is None


def test_a_versionless_frozen_band_yields_no_baseline() -> None:
    """The harness stamps `salience_version` whenever it derives a band, so a
    band without a version never arrives from a cell — but a hand-built context
    without one gets `None` rather than a guessed pool."""
    pack = _statpack(_term(2023, {"high": (0.30, 100)}))
    ctx = _context("high", term=2024, salience_version=None)
    assert prediction_base_rate(ctx, pack) is None
