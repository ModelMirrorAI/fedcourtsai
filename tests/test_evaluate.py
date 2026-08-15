"""Tests for the deterministic evaluate helpers and the baselines they score against.

Two modules, tested together because they are one path: `pipeline.evaluate`
holds the scorers and `segment_base_rate`, while `pipeline.base_rates` holds
the pooled baselines those scorers are measured against. The baselines live in
a leaf so the leaderboard can read them without importing the corpus-bound
half; neither half means much without the other, so one file pins both.
`is_correct` / `brier_score` are exercised through the runner and leaderboard
suites; here we pin the baseline helpers, whose whole point is a *leakage-safe*
skill score keyed on the salience band — and `vote_accuracy`'s stage gate, which
belongs beside them for the same reason: it is a leakage-shaped rule about which
quantities may be scored at all, not a detail of the arithmetic.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.base_rates import (
    INTERIM_BASE_RATE_MIN_RESOLVED,
    MERITS_BASE_RATE_MIN_PARSED,
    REALIZED_BAND_RATE_MIN_RESOLVED,
    interim_base_rate,
    merits_base_rate,
    prediction_base_rate,
    realized_band_rate,
)
from fedcourtsai.pipeline.evaluate import (
    brier_skill,
    brier_skill_score,
    is_correct,
    judgment_correct,
    segment_base_rate,
    vote_accuracy,
)
from fedcourtsai.pipeline.moments import moments_for, scores_votes
from fedcourtsai.pipeline.salience import salience_band
from fedcourtsai.schemas import (
    GRANT_FAMILY_DISPOSITIONS,
    GRANTED_DISPOSITIONS,
    BaseRateBucket,
    Disposition,
    Engine,
    Judgment,
    JusticeVote,
    Outcome,
    Prediction,
    PredictionContext,
    Stage,
    StatPack,
    StatPackInterim,
    StatPackInterimTerm,
    StatPackMerits,
    StatPackMeritsTerm,
    StatPackTerm,
    StatPackTermSegment,
    StatPackTermVersionSegments,
    VoteValue,
)


def _segments(band_rates: dict[str, tuple[float, int]]) -> list[StatPackTermSegment]:
    return [
        StatPackTermSegment(
            band=band,
            weighted_resolved=n,
            est_grant_rate=rate,
            prefix_weighted_resolved=n,
            prefix_est_grant_rate=rate,
        )
        for band, (rate, n) in band_rates.items()
    ]


def _term(
    year: int,
    band_rates: dict[str, tuple[float, int]],
    *,
    version: str = "sal-v3",
    alt: dict[str, dict[str, tuple[float, int]]] | None = None,
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
        segments=_segments(band_rates),
        alt_segments=[
            StatPackTermVersionSegments(salience_version=v, segments=_segments(rates))
            for v, rates in (alt or {}).items()
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
    # And None for a docket with no derivable Term year on either axis.
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
        salience_version="sal-v3",
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
            salience_version="sal-v3",
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
        salience_version = "sal-v3" if band else None
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
        salience_version="sal-v3",
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
    """A sal-v1 `high` and a sal-v3 `high` are different populations sharing a
    label. A sal-v3 band must pool only the sal-v3 Terms — never a blend no
    version ever defined."""
    pack = _statpack(
        _term(2023, {"high": (0.30, 100)}),
        _term(2022, {"high": (0.60, 100)}, version="sal-v1"),
    )
    # Row-derived band: the live scorer is sal-v3, so only the sal-v3 Term pools.
    assert segment_base_rate(_row("24-100"), pack) == pytest.approx(0.30)
    # Frozen band: pinned to the version the cell actually froze.
    assert prediction_base_rate(_context("high", term=2024), pack) == pytest.approx(0.30)
    v1 = _context("high", term=2024, salience_version="sal-v1")
    assert prediction_base_rate(v1, pack) == pytest.approx(0.60)


def test_a_non_active_version_pools_from_its_alt_segments_block() -> None:
    """One Term publishes every registered version's bands, not only the live one.

    A prediction keeps the version that banded it for life, so when the live pass
    moves to a new scorer the older one still needs a baseline. `alt_segments`
    carries it on the same Term, and the pin has to look there — otherwise every
    cell frozen at the previous version silently loses its skill score the day
    the scorer changes."""
    pack = _statpack(_term(2023, {"high": (0.30, 100)}, alt={"sal-v0": {"high": (0.60, 100)}}))
    # The active version reads the Term's own `segments`.
    assert prediction_base_rate(_context("high", term=2024), pack) == pytest.approx(0.30)
    # The retired version reads its own block on the same Term — no blend.
    retired = _context("high", term=2024, salience_version="sal-v0")
    assert prediction_base_rate(retired, pack) == pytest.approx(0.60)
    # A version in neither place still gets the contracted no-baseline answer.
    assert (
        prediction_base_rate(_context("high", term=2024, salience_version="sal-v9"), pack) is None
    )


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


# --- realized_band_rate: the case's OWN Term, leave-one-out ----------------------


def _own_term(
    year: int,
    *,
    terminal: tuple[int, int],
    risk_set: tuple[int, int] | None = None,
    version: str = "sal-v1",
    band: str = "high",
    observed: int | None = None,
) -> StatPackTerm:
    """A Term whose ``band`` carries ``(weighted grants, weighted resolved)``.

    The pack publishes rates rather than counts, so the fixture divides exactly
    as the statpack builder does and leaves `realized_band_rate` to round the
    numerator back out. ``risk_set`` defaults to the terminal pair, so a fixture
    encodes a prefix-versus-terminal gap only when the test is about one.
    ``observed`` is the raw row count behind the weighted estimate, defaulting
    to a Term walked at weight 1 — set it lower for a reweighted Term.
    """
    grants, resolved = terminal
    prefix_grants, prefix_resolved = risk_set if risk_set is not None else terminal
    return StatPackTerm(
        term=year,
        base_rates=BaseRateBucket(),
        salience_version=version,
        segments=[
            StatPackTermSegment(
                band=band,
                resolved=observed if observed is not None else resolved,
                weighted_resolved=resolved,
                est_grant_rate=grants / resolved,
                prefix_resolved=observed if observed is not None else prefix_resolved,
                prefix_weighted_resolved=prefix_resolved,
                prefix_est_grant_rate=prefix_grants / prefix_resolved,
            )
        ],
    )


def _realized(
    pack: StatPack, own_grant_family: int, *, term: int = 2025, risk_set: bool = False, **kw: int
) -> float | None:
    return realized_band_rate(
        "high", "sal-v1", term, pack, risk_set=risk_set, own_grant_family=own_grant_family, **kw
    )


def test_realized_band_rate_leaves_the_scored_case_out() -> None:
    """The case sits inside its own Term's rate, and in a thin band that bites.

    OT2025's `high` band as published: 32 weighted grants over 72 resolved. A
    granted case must be scored against the other 71 (31/71), a denied one
    against 32/71 — never the 32/72 that contains it.
    """
    pack = _statpack(_own_term(2025, terminal=(32, 72)))
    assert _realized(pack, 1) == pytest.approx(31 / 71)
    assert _realized(pack, 0) == pytest.approx(32 / 71)
    # The uncorrected rate is neither, and sits between them — which is exactly
    # the direction the correction has to move in.
    assert 31 / 71 < 32 / 72 < 32 / 71


def test_realized_band_rate_needs_the_band_to_survive_the_omission() -> None:
    """One resolved row and leaving it out leaves no band at all.

    The floor would catch this too, so the test dials it away to pin the
    degenerate guard itself: n=0 is `None`, never a division.
    """
    pack = _statpack(_own_term(2025, terminal=(1, 1)))
    assert _realized(pack, 1, min_resolved=0) is None
    assert _realized(pack, 0, min_resolved=0) is None


def test_realized_band_rate_omits_a_band_under_the_minimum() -> None:
    """The floor is measured on the leave-one-out denominator that scores the case.

    30 resolved leaves 29 after the omission and publishes nothing; 31 leaves
    exactly the stated minimum and publishes. A thin band is omitted, visibly,
    rather than scored on a handful of cases.
    """
    assert REALIZED_BAND_RATE_MIN_RESOLVED == 30
    assert _realized(_statpack(_own_term(2025, terminal=(10, 30))), 0) is None
    assert _realized(_statpack(_own_term(2025, terminal=(10, 31))), 0) == pytest.approx(10 / 30)


def test_the_minimum_binds_on_observed_rows_not_only_weighted_ones() -> None:
    """A denial-reweighted Term can carry a weighted 31 over a dozen real
    petitions, and the rate's standard error follows the rows. So the floor
    binds twice — on the leave-one-out weighted denominator *and* on the
    observed count behind it — and a Term that clears only the first publishes
    nothing."""
    thin = _statpack(_own_term(2025, terminal=(10, 31), observed=14))
    assert _realized(thin, 0) is None
    assert _realized(_statpack(_own_term(2025, terminal=(10, 31), observed=31)), 0) is not None


def test_realized_band_rate_subtracts_on_the_packs_own_grant_definition() -> None:
    """`own_grant_family` is the numerator's membership test, not `actual_granted`.

    `granted-in-part` is a granted binary outcome that keeps its own statpack
    bucket, so it is absent from the published rate's numerator; subtracting it
    would remove a grant that was never counted and hand the cell a baseline one
    grant too low.
    """
    pack = _statpack(_own_term(2025, terminal=(32, 72)))
    assert Disposition.granted_in_part in GRANTED_DISPOSITIONS
    assert Disposition.granted_in_part not in GRANT_FAMILY_DISPOSITIONS
    assert _realized(pack, 0) == pytest.approx(32 / 71)  # the granted-in-part case
    assert _realized(pack, 1) == pytest.approx(31 / 71)  # a plain grant


def test_a_case_outside_the_packs_counts_gets_no_baseline_rather_than_a_clamp() -> None:
    """The subtraction landing out of range proves the case is not in this
    vintage — a pack built before it resolved. Clamping would hand the cell a
    certainty baseline and, with it, a large fabricated skill; the honest answer
    is the same `None` every other gap returns."""
    grantless = _statpack(_own_term(2025, terminal=(0, 72)))
    assert _realized(grantless, 0) == pytest.approx(0.0)  # in range: a real all-denied band
    assert _realized(grantless, 1) is None
    saturated = _statpack(_own_term(2025, terminal=(72, 72)))
    assert _realized(saturated, 1) == pytest.approx(1.0)
    assert _realized(saturated, 0) is None


def test_realized_band_rate_is_version_pinned_like_the_prior_term_pool() -> None:
    """A band name means something only under the scorer that assigned it.

    A sal-v1 `high` and a sal-v2 `high` are different populations sharing a
    label, so a pack carrying only the other version has no rate to offer —
    `None`, never a blend no version ever defined.
    """
    pack = _statpack(_own_term(2025, terminal=(32, 72), version="sal-v2"))
    assert _realized(pack, 1) is None
    assert realized_band_rate(
        "high", "sal-v2", 2025, pack, risk_set=False, own_grant_family=1
    ) == pytest.approx(31 / 71)


def test_realized_band_rate_keeps_the_risk_set_terminal_pairing() -> None:
    """The same pairing the prior-Term baseline uses, and here it is what makes
    the omission well defined: a case frozen at a band ends at that band or a
    stronger one, so it is counted in the band's risk set — and a case banded
    off the row now is counted in the band's terminal population. Read the wrong
    rate and the case is subtracted from a population it was never in."""
    pack = _statpack(_own_term(2025, terminal=(14, 901), risk_set=(90, 1301)))
    assert _realized(pack, 1, risk_set=False) == pytest.approx(13 / 900)
    assert _realized(pack, 1, risk_set=True) == pytest.approx(89 / 1300)


def test_realized_band_rate_reads_only_the_cases_own_term() -> None:
    """The one difference from the strictly-prior pooler, and it cuts both ways:
    neither an earlier Term nor a later one contributes anything."""
    pack = _statpack(
        _own_term(2026, terminal=(70, 72)),
        _own_term(2025, terminal=(32, 72)),
        _own_term(2024, terminal=(2, 72)),
    )
    assert _realized(pack, 1) == pytest.approx(31 / 71)
    assert _realized(pack, 1, term=2023) is None  # a Term the pack does not carry


def test_the_leave_one_out_null_is_exactly_the_self_inclusion_price() -> None:
    """Jackknifing moves the baseline away from the case's own outcome by a fixed
    factor, so the metric's null is stated rather than assumed. A forecaster
    reporting the case-excluded level scores exactly 0; one reporting the band's
    *published* rate — which contains its own case — scores `(2n - 1) / n**2`,
    the price of that self-inclusion and nothing else. The docs quote the bound;
    this pins it."""
    n = 72
    pack = _statpack(_own_term(2025, terminal=(32, n)))
    loo = _realized(pack, 1)
    assert loo is not None
    assert brier_skill((loo - 1) ** 2, 1, loo) == pytest.approx(0.0)
    published = 32 / n
    assert brier_skill((published - 1) ** 2, 1, loo) == pytest.approx((2 * n - 1) / n**2)


def test_prior_term_and_realized_term_skill_can_disagree_in_sign() -> None:
    """The decomposition's whole point, on a Term that ran hot.

    History put the `high` band at 40%; OT2025 realized 60% (61 of 101, or 60 of
    100 once the scored case is left out). A predictor at 0.50 on a case that
    was granted **beat history** — positive prior-Term skill — and **lost to the
    Term** — negative realized-Term skill. Holding the level at what actually
    obtained is what turns the sign: the first number credits the level call,
    the second asks only whether the predictor could tell this case from its
    band-mates.
    """
    pack = _statpack(
        _term(2024, {"high": (0.40, 100)}),
        _own_term(2025, terminal=(61, 101)),
    )
    prediction, outcome = _prediction(0.5), _outcome(1)
    prior = prediction_base_rate(_context("high", term=2025), pack)
    realized = _realized(pack, 1, risk_set=True)
    assert prior == pytest.approx(0.40)
    assert realized == pytest.approx(0.60)
    prior_skill = brier_skill_score(prediction, outcome, prior)
    realized_skill = brier_skill_score(prediction, outcome, realized)
    assert prior_skill is not None and realized_skill is not None
    # brier 0.25 against baseline briers 0.36 and 0.16.
    assert prior_skill == pytest.approx(1 - 0.25 / 0.36)
    assert realized_skill == pytest.approx(1 - 0.25 / 0.16)
    assert prior_skill > 0 > realized_skill


# --- interim_base_rate: the strictly-prior pooled substantive grant rate ---------


def _interim_term(year: int, *, granted: int, resolved: int) -> StatPackInterimTerm:
    """One application-Term row of the interim section — the counters it pools."""
    return StatPackInterimTerm(
        term=year,
        applications=resolved,
        substantive=resolved,
        substantive_resolved=resolved,
        substantive_granted=granted,
    )


def _interim_pack(*terms: StatPackInterimTerm) -> StatPack:
    return StatPack(
        corpus_rows=1,
        interim=StatPackInterim(
            substantive_resolved=sum(t.substantive_resolved for t in terms),
            substantive_granted=sum(t.substantive_granted for t in terms),
            terms=list(terms),
        ),
    )


def _application_row(docket: str) -> corpus.CorpusRow:
    return corpus.CorpusRow(case_id=f"scotus/{docket}", court="scotus", docket_number=docket)


def test_interim_base_rate_pools_only_terms_before_the_applications() -> None:
    # OT2026 application: its own Term never contributes, on the application-Term
    # axis — the same leakage guard the two sibling baselines apply.
    pack = _interim_pack(
        _interim_term(2026, granted=60, resolved=60),
        _interim_term(2025, granted=4, resolved=40),
        _interim_term(2024, granted=2, resolved=40),
    )
    assert interim_base_rate(2026, pack) == pytest.approx(6 / 80)


def test_interim_base_rate_lookback_bounds_the_pool_as_a_term_year_band() -> None:
    pack = _interim_pack(
        _interim_term(2025, granted=6, resolved=60),
        _interim_term(2022, granted=60, resolved=60),  # outside a 2-Term window
    )
    assert interim_base_rate(2026, pack, lookback_terms=2) == pytest.approx(0.10)


def test_interim_base_rate_none_without_a_section_or_prior_terms() -> None:
    assert interim_base_rate(2026, StatPack()) is None
    pack = _interim_pack(_interim_term(2026, granted=6, resolved=60))
    assert interim_base_rate(2026, pack) is None  # only the application's own Term


def test_the_interim_floor_binds_on_the_pooled_count_not_the_per_term_one() -> None:
    # Two thin Terms that each fall short still clear the floor together: the
    # floor is a statement about the pooled sample, so it clears by
    # accumulation exactly as the merits one does.
    halves = _interim_pack(
        _interim_term(2025, granted=3, resolved=25),
        _interim_term(2024, granted=2, resolved=25),
    )
    assert interim_base_rate(2026, halves) == pytest.approx(5 / 50)
    # One short of the floor is no baseline, never a degenerate rate.
    short = _interim_pack(
        _interim_term(2025, granted=3, resolved=25),
        _interim_term(2024, granted=2, resolved=24),
    )
    assert interim_base_rate(2026, short) is None
    assert INTERIM_BASE_RATE_MIN_RESOLVED == 50


def test_segment_base_rate_takes_the_interim_arm_on_an_application_docket() -> None:
    """An `A`-form docket is scored against the interim pool, not the cert bands.

    The cert band table is a different population resolving on a different
    standard, so the arm is chosen by the docket form rather than fallen through
    to: a pack carrying only cert Terms yields nothing for an application.
    """
    cert_only = _statpack(_term(2025, {"high": (0.4, 100)}))
    assert segment_base_rate(_application_row("26A11"), cert_only) is None

    cleared = _interim_pack(
        _interim_term(2025, granted=6, resolved=60),
        _interim_term(2026, granted=60, resolved=60),  # own Term: never pooled
    )
    assert segment_base_rate(_application_row("26A11"), cleared) == pytest.approx(0.10)

    # One resolution short of the floor: no baseline, and no fallback to the
    # pack-level rate or to the cert band table.
    thin = _interim_pack(_interim_term(2025, granted=6, resolved=49))
    assert segment_base_rate(_application_row("26A11"), thin) is None


# --- merits_base_rate: the strictly-prior pooled disturbed rate ------------------


def _merits_term(year: int, *, disturbed: int, parsed: int) -> StatPackMeritsTerm:
    """One grant-Term row of the merits section — the counters the baseline pools.

    Built as a guard-run row (`cert_order_excluded=0`): a null there marks a
    build the cert-order pool guard never ran on, which the baseline refuses —
    the null-guard test constructs its row explicitly.
    """
    return StatPackMeritsTerm(term=year, disturbed=disturbed, parsed=parsed, cert_order_excluded=0)


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


def test_merits_base_rate_refuses_a_null_guard_pool() -> None:
    """A pooled Term whose `cert_order_excluded` is null yields no baseline.

    Null marks a build the cert-order pool guard never ran on, so that Term's
    parsed counts may include the cert-order class the rate must exclude —
    `metrics/README.md` rules such a section unquotable, and this makes the
    rule structural rather than conventional.
    """
    # Distinguishable numbers on purpose: pooling the null Term would yield
    # 0.75 and silently dropping it 0.60, so a wrong-branch edit is legible
    # from the failure, not only from the missing None.
    null_guard = StatPackMeritsTerm(term=2022, disturbed=36, parsed=40)
    contaminated = _merits_pack(_merits_term(2023, disturbed=24, parsed=40), null_guard)
    assert merits_base_rate(2024, contaminated) is None
    # A null-guard row outside the pooled window never poisons the pool: the
    # case's own (or later) Term is skipped by the leakage guard, and a Term
    # behind the lookback window is skipped by the band.
    future_null = _merits_pack(
        StatPackMeritsTerm(term=2024, disturbed=40, parsed=40),
        _merits_term(2023, disturbed=28, parsed=40),
    )
    assert merits_base_rate(2024, future_null) == pytest.approx(0.70)
    behind_window = _merits_pack(
        _merits_term(2023, disturbed=28, parsed=40),
        StatPackMeritsTerm(term=2020, disturbed=40, parsed=40),
    )
    assert merits_base_rate(2024, behind_window, lookback_terms=2) == pytest.approx(0.70)
    # Deliberate scoping, pinned: the pack-level roll-up is never consulted —
    # the pool reads Terms, so refusal is a property of the counts the number
    # rests on. (The builder fills both levels together; a divergence between
    # them is a hand-edited pack, which section-level refusal would not defend
    # against either.) `_merits_pack` leaves the pack-level count at its null
    # default, so every healthy pool above already exercises this; this states
    # it as a choice rather than leaving it as drift.
    pack_level_null = _merits_pack(_merits_term(2023, disturbed=28, parsed=40))
    assert pack_level_null.merits is not None
    assert pack_level_null.merits.cert_order_excluded is None
    assert merits_base_rate(2024, pack_level_null) == pytest.approx(0.70)


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


# --- vote_accuracy: the stage gate on the one quantity that has one --------------

#: One vote list, reused on both sides of every gate case below, so the only
#: thing that varies between a scored 1.0 and a null is the event's stage.
_VOTES = [JusticeVote(justice="roberts", vote=VoteValue.majority)]


def _voting_pair(event_id: str) -> tuple[Prediction, Outcome]:
    """A prediction and an outcome on ``event_id``, both naming the same vote.

    Deliberately identical apart from the event: handed to `vote_accuracy` these
    would score a perfect 1.0 on their intersection, so a null can only come
    from the gate.
    """
    prediction = _merits_prediction(Judgment.reversed).model_copy(
        update={"event_id": event_id, "votes": _VOTES}
    )
    outcome = _merits_outcome(Judgment.reversed).model_copy(
        update={"event_id": event_id, "votes": _VOTES}
    )
    return prediction, outcome


def test_vote_accuracy_scores_the_declared_merits_moments() -> None:
    for spec in moments_for(Stage.merits):
        prediction, outcome = _voting_pair(spec.event_id)
        assert vote_accuracy(prediction, outcome) == 1.0, spec.event_id


def test_vote_accuracy_is_never_scored_at_the_cert_stage() -> None:
    """The pre-registered prohibition, made structural.

    A cert vote becomes public only when a Justice chooses to note it, so
    observation is very nearly a deterministic function of the value being
    scored and the deny-and-silent stratum can never be reweighted into view
    (`docs/decision-model.md`). The rule is therefore *never score*, whatever a
    record happens to contain — so a cert-moment pair that names the very same
    vote on both sides scores nothing at all. Remove the gate in
    `pipeline.moments.scores_votes` and every assertion here reads 1.0.
    """
    for spec in moments_for(Stage.cert):
        prediction, outcome = _voting_pair(spec.event_id)
        assert prediction.votes and outcome.votes, spec.event_id
        assert vote_accuracy(prediction, outcome) is None, spec.event_id


def test_vote_accuracy_is_denied_by_default_off_the_register() -> None:
    """An id the moments table cannot place scores no votes either.

    Denial is the default rather than the cert stage being named: the register
    is the only authority on an event's stage, so an id it does not declare —
    an entry-pinned event, a record older than the table — is one that cannot be
    shown *not* to be cert. Interim moments are declared and unscored for the
    plainer reason that the stage forecasts no votes.
    """
    assert not scores_votes("evt-appeal-disposition")
    prediction, outcome = _voting_pair("evt-appeal-disposition")
    assert vote_accuracy(prediction, outcome) is None
    for spec in moments_for(Stage.interim):
        interim_prediction, interim_outcome = _voting_pair(spec.event_id)
        assert vote_accuracy(interim_prediction, interim_outcome) is None, spec.event_id


def test_realized_band_rate_reads_a_retired_versions_alt_segments_block() -> None:
    """The realized-Term rate resolves its version exactly as the pooler does.

    An asymmetry here would be invisible and expensive: on the day a new scorer
    activates, every cell frozen at the old one would keep its prior-Term skill
    and silently lose its realized-Term skill, so the board would print two
    skill columns over two different populations — split on a version label
    rather than on the resolved-count floor, which is this field's only stated
    reason to be absent.
    """
    own = _own_term(2025, terminal=(32, 72))
    retired = _own_term(2025, terminal=(40, 80), version="sal-v0")
    pack = _statpack(
        own.model_copy(
            update={
                "alt_segments": [
                    StatPackTermVersionSegments(
                        salience_version="sal-v0", segments=retired.segments
                    )
                ]
            }
        )
    )
    # The active version reads the Term's own segments (32 grants of 72, less the case).
    assert _realized(pack, 1) == pytest.approx(31 / 71)
    # The retired version reads its own block on the same Term — no blend, no None.
    assert realized_band_rate(
        "high", "sal-v0", 2025, pack, risk_set=False, own_grant_family=1
    ) == pytest.approx(39 / 79)
    # A version in neither place still gets the contracted no-baseline answer.
    assert (
        realized_band_rate("high", "sal-v9", 2025, pack, risk_set=False, own_grant_family=1) is None
    )
