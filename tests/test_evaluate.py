"""Tests for the deterministic evaluate helpers, focused on the segment baseline.

`is_correct` / `brier_score` / `vote_accuracy` are exercised through the runner
and leaderboard suites; here we pin the two segment-baseline helpers, whose whole
point is a *leakage-safe* skill score keyed on the salience band.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.evaluate import brier_skill_score, segment_base_rate
from fedcourtsai.schemas import (
    BaseRateBucket,
    Disposition,
    Engine,
    Outcome,
    Prediction,
    StatPack,
    StatPackTerm,
    StatPackTermSegment,
)


def _term(year: int, band_rates: dict[str, tuple[float, int]]) -> StatPackTerm:
    return StatPackTerm(
        term=year,
        base_rates=BaseRateBucket(),
        salience_version="sal-v1",
        segments=[
            StatPackTermSegment(band=band, weighted_resolved=n, est_grant_rate=rate)
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
