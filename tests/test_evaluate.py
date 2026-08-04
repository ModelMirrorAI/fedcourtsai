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
    MERITS_BASE_RATE_MIN_PARSED,
    brier_skill_score,
    is_correct,
    judgment_correct,
    merits_base_rate,
    prediction_base_rate,
    segment_base_rate,
)
from fedcourtsai.pipeline.salience import salience_band
from fedcourtsai.schemas import (
    BaseRateBucket,
    Disposition,
    Engine,
    Judgment,
    JusticeVote,
    Outcome,
    Prediction,
    PredictionContext,
    StatPack,
    StatPackMerits,
    StatPackMeritsTerm,
    StatPackTerm,
    StatPackTermSegment,
    VoteValue,
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
    # An interim application docket is the same answer for a stage-level reason:
    # an `A`-form number carries no cert Term, so the cert band pool it would
    # have to be drawn from does not apply to it at all. The evaluate prompt's
    # interim rule (omit `segment_base_rate` and `brier_skill_score`) is the
    # agent-side half of this.
    assert segment_base_rate(_row("26A11"), _statpack(_term(2023, {"high": (0.4, 5)}))) is None


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


# --- merits_base_rate: the strictly-prior pooled disturbed rate ------------------


def _merits_term(year: int, *, disturbed: int, parsed: int) -> StatPackMeritsTerm:
    """One grant-Term row of the merits section — the counters the baseline pools."""
    return StatPackMeritsTerm(term=year, disturbed=disturbed, parsed=parsed)


def _merits_pack(*terms: StatPackMeritsTerm) -> StatPack:
    return StatPack(
        corpus_rows=1,
        merits=StatPackMerits(
            parsed=sum(t.parsed for t in terms),
            disturbed=sum(t.disturbed for t in terms),
            terms=list(terms),
        ),
    )


def test_merits_base_rate_pools_only_terms_before_the_cases() -> None:
    # OT24 case: OT24's own (and later) rows never contribute — the same
    # leakage guard as the segment baseline, on the grant-Term axis.
    pack = _merits_pack(
        _merits_term(2025, disturbed=40, parsed=40),
        _merits_term(2024, disturbed=36, parsed=40),
        _merits_term(2023, disturbed=24, parsed=40),
        _merits_term(2022, disturbed=32, parsed=40),
    )
    # Pooled aggregate over OT22+OT23: (24 + 32) / 80 = 0.70.
    assert merits_base_rate(2024, pack) == pytest.approx(0.70)


def test_merits_base_rate_lookback_bounds_the_pool_as_a_term_year_band() -> None:
    pack = _merits_pack(
        _merits_term(2023, disturbed=24, parsed=40),
        _merits_term(2021, disturbed=40, parsed=40),
    )
    # A 2-Term window before OT24 covers OT22+OT23 only; OT22 is absent from
    # the pack, which shortens the sample rather than pulling OT21 in.
    assert merits_base_rate(2024, pack, lookback_terms=2) == pytest.approx(0.60)


def test_merits_base_rate_none_without_a_section_or_prior_terms() -> None:
    assert merits_base_rate(2024, StatPack()) is None
    pack = _merits_pack(_merits_term(2024, disturbed=28, parsed=40))
    assert merits_base_rate(2024, pack) is None  # only the case's own Term


def test_merits_base_rate_refuses_a_sample_below_the_stated_floor() -> None:
    """A thin pool yields no baseline rather than a degenerate one.

    The section exists from its first parsed judgment, so without the floor one
    prior-Term row would hand out a 0.0/1.0 baseline — and `brier_skill` masks
    exactly the cells such a baseline got right, leaving a published mean taken
    only over the ones it got wrong.
    """
    thin = _merits_pack(_merits_term(2023, disturbed=1, parsed=1))
    assert merits_base_rate(2024, thin) is None
    just_under = _merits_pack(
        _merits_term(
            2023, disturbed=MERITS_BASE_RATE_MIN_PARSED - 1, parsed=MERITS_BASE_RATE_MIN_PARSED - 1
        )
    )
    assert merits_base_rate(2024, just_under) is None
    at_floor = _merits_pack(_merits_term(2023, disturbed=21, parsed=MERITS_BASE_RATE_MIN_PARSED))
    assert merits_base_rate(2024, at_floor) == pytest.approx(0.70)


def test_merits_base_rate_pools_aggregates_not_term_means() -> None:
    # Aggregate disturbed over aggregate parsed — a Term contributes at its
    # parsed count, so a thin Term cannot outvote a thick one.
    pack = _merits_pack(
        _merits_term(2023, disturbed=1, parsed=1),
        _merits_term(2022, disturbed=50, parsed=100),
    )
    assert merits_base_rate(2024, pack) == pytest.approx(51 / 101)


# --- judgment_correct: the merits exact-match diagnostic -------------------------


def _merits_prediction(judgment: Judgment) -> Prediction:
    return Prediction(
        case_id="scotus/1",
        event_id="evt-order-judgment",
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2025, 1, 1),
        input_snapshot="x",
        granted=0,
        probability=0.7,
        predicted_disposition=Disposition.other,
        judgment=judgment,
        votes=[JusticeVote(justice="roberts", vote=VoteValue.majority)],
    )


def _merits_outcome(judgment: Judgment) -> Outcome:
    return Outcome(
        case_id="scotus/1",
        event_id="evt-order-judgment",
        resolved_at=date(2025, 6, 1),
        actual_disposition=Disposition.other,
        actual_granted=int(judgment in {Judgment.reversed, Judgment.vacated}),
        judgment=judgment,
    )


def test_judgment_correct_is_exact_on_the_full_vocabulary() -> None:
    assert (
        judgment_correct(_merits_prediction(Judgment.reversed), _merits_outcome(Judgment.reversed))
        == 1
    )
    # A reversal call against a vacatur is wrong on this axis, even though both
    # disturb the judgment below — exact match, not the binary projection.
    assert (
        judgment_correct(_merits_prediction(Judgment.reversed), _merits_outcome(Judgment.vacated))
        == 0
    )


def test_judgment_correct_none_off_the_merits_axis() -> None:
    cert_prediction = _prediction(0.4)
    cert_outcome = _outcome(1)
    assert judgment_correct(cert_prediction, cert_outcome) is None
    assert judgment_correct(cert_prediction, _merits_outcome(Judgment.reversed)) is None
    assert judgment_correct(_merits_prediction(Judgment.reversed), cert_outcome) is None


def test_correct_is_the_judgment_axis_on_a_merits_cell() -> None:
    """`correct` compares the stage's own outcome label.

    A merits outcome's `actual_disposition` is always the off-vocabulary
    `other`, so a disposition comparison there would score every merits cell
    against a constant the merits contract never defines — and the leaderboard's
    merits accuracy column would be that constant, settable by the predictor.
    Where both sides carry a judgment, `correct` is the judgment match.
    """
    outcome = _merits_outcome(Judgment.reversed)
    assert is_correct(_merits_prediction(Judgment.reversed), outcome) == 1
    assert is_correct(_merits_prediction(Judgment.vacated), outcome) == 0
    # …and it does not care what the prediction wrote in predicted_disposition,
    # which on a merits cell is exactly the ungoverned field.
    wrong_judgment = _merits_prediction(Judgment.affirmed).model_copy(
        update={"predicted_disposition": Disposition.other}
    )
    assert is_correct(wrong_judgment, outcome) == 0


def test_a_judgment_less_prediction_earns_no_free_merits_match() -> None:
    """The routing is on the outcome, so `other == other` is never a match.

    A merits outcome's `actual_disposition` is `other`; a prediction that
    carries no judgment but writes `other` there would collect a costless 1 if
    `correct` needed a judgment on both sides. `validate` refuses such a
    prediction, but `correct` is computed before validate runs, so the axis has
    to hold on its own.
    """
    outcome = _merits_outcome(Judgment.reversed)
    judgment_less = _prediction(0.6).model_copy(update={"predicted_disposition": Disposition.other})
    assert judgment_less.judgment is None
    assert is_correct(judgment_less, outcome) == 0


def test_correct_stays_the_disposition_axis_off_the_merits_stage() -> None:
    # A cert cell carries no judgment on either side, so the disposition
    # comparison is unchanged — the path every committed evaluation took.
    assert is_correct(_prediction(0.9), _outcome(1)) == 1
    assert is_correct(_prediction(0.1), _outcome(1)) == 0
