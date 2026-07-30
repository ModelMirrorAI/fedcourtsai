"""Tests for cert-stage claim scoring: the baseline, the score, the floor and lift.

The three properties that carry the doctrine, and so are pinned by mutation rather
than by prose: the baseline never reads the case's own Term, reporting the baseline
scores exactly zero either way, and the uninformed control's floor is *positive*
whenever its recent window disagrees with the baseline's — which is the whole
reason a claim total is published with a floor beside it.
"""

from __future__ import annotations

from datetime import date

import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.evaluate import (
    CERT_SIGNAL_CLAIMS,
    Claim,
    claim_base_rate,
    claim_floor,
    claim_floor_scores,
    claim_lift,
    claim_score,
    claim_scores,
    claim_total,
    resolve_claim,
)
from fedcourtsai.schemas import (
    BaseRateBucket,
    Disposition,
    Outcome,
    ResolutionSignals,
    StatPack,
    StatPackTerm,
)


def _term(
    year: int,
    *,
    relist: tuple[float | None, int] = (None, 0),
    cvsg: tuple[float | None, int] = (None, 0),
) -> StatPackTerm:
    return StatPackTerm(
        term=year,
        base_rates=BaseRateBucket(),
        est_relist_rate=relist[0],
        relist_weighted_resolved=relist[1],
        est_cvsg_rate=cvsg[0],
        cvsg_weighted_resolved=cvsg[1],
    )


def _statpack(*terms: StatPackTerm) -> StatPack:
    return StatPack(corpus_rows=1, terms=list(terms))


def _row(docket: str) -> corpus.CorpusRow:
    return corpus.CorpusRow(case_id=f"scotus/{docket}", court="scotus", docket_number=docket)


def _outcome(*, distributions: int = 1, cvsg: bool = False, signals: bool = True) -> Outcome:
    return Outcome(
        case_id="scotus/1",
        event_id="cert",
        resolved_at=date(2025, 6, 1),
        actual_disposition=Disposition.denied,
        actual_granted=0,
        signals=(
            ResolutionSignals(
                distribution_count=distributions,
                cvsg_date=date(2025, 2, 3) if cvsg else None,
            )
            if signals
            else None
        ),
    )


# --- resolve_claim: the outcome record, never the corpus column ------------------


def test_a_second_distribution_is_the_first_relist() -> None:
    # One distribution is a consideration, not a relist; relists are count - 1.
    assert resolve_claim(_outcome(distributions=1), Claim.relisted) == 0
    assert resolve_claim(_outcome(distributions=2), Claim.relisted) == 1
    assert resolve_claim(_outcome(distributions=7), Claim.relisted) == 1


def test_cvsg_resolves_on_the_frozen_date() -> None:
    assert resolve_claim(_outcome(cvsg=False), Claim.cvsg) == 0
    assert resolve_claim(_outcome(cvsg=True), Claim.cvsg) == 1


def test_an_outcome_without_signals_resolves_nothing() -> None:
    # Backward compatibility, and a doctrine: an absent signals block means the
    # proceedings were never live-parsed. Nothing was observed, which is not the
    # same as the signal not having happened — so the claim drops out of the set
    # rather than resolving false, and nothing crashes on the way.
    outcome = _outcome(signals=False)
    assert all(resolve_claim(outcome, claim) is None for claim in CERT_SIGNAL_CLAIMS)
    pack = _statpack(_term(2023, relist=(0.30, 100), cvsg=(0.02, 100)))
    row = _row("24-100")
    assert claim_scores({Claim.relisted: 0.9, Claim.cvsg: 0.9}, row, outcome, pack) == {}
    assert claim_total({Claim.relisted: 0.9}, row, outcome, pack) == 0.0
    assert claim_floor(row, outcome, pack) == 0.0


# --- claim_base_rate: the leakage guard --------------------------------------------


def test_claim_base_rate_never_reads_the_cases_own_term() -> None:
    # The mutation this pins: relaxing the guard from `>=` to `>` would admit OT24
    # itself. Its rate is set far from the prior Terms' so the two cannot coincide,
    # and the prior Terms are equal to each other so the expected value is exact.
    pack = _statpack(
        _term(2025, relist=(1.00, 100)),  # later than the case: excluded
        _term(2024, relist=(1.00, 100)),  # the case's OWN Term: excluded
        _term(2023, relist=(0.30, 100)),
        _term(2022, relist=(0.30, 100)),
    )
    assert claim_base_rate(_row("24-100"), pack, Claim.relisted) == pytest.approx(0.30)


def test_claim_base_rate_pools_prior_terms_by_their_denominators() -> None:
    # A resolved-weighted mean, not a mean of rates: the thin Term counts less.
    pack = _statpack(
        _term(2023, relist=(0.40, 300)),
        _term(2022, relist=(0.20, 100)),
    )
    # (0.40*300 + 0.20*100) / 400 = 0.35.
    assert claim_base_rate(_row("24-100"), pack, Claim.relisted) == pytest.approx(0.35)


def test_claim_base_rate_is_none_without_a_term_a_predecessor_or_a_rate() -> None:
    pack = _statpack(_term(2023, relist=(0.30, 100)))
    # No derivable October Term from the docket number.
    assert claim_base_rate(_row("bare-docket"), pack, Claim.relisted) is None
    # Nothing precedes the case's own Term.
    assert claim_base_rate(_row("23-100"), pack, Claim.relisted) is None
    # The Term precedes it but resolved nothing for this claim.
    assert claim_base_rate(_row("24-100"), pack, Claim.cvsg) is None


def test_the_lookback_is_a_term_year_band_not_a_rank_slice() -> None:
    # OT2023 is absent. A rank slice would take the two most recent prior *rows*
    # (OT24 + OT22) and quietly reach outside the stated window; the year band takes
    # OT24 alone and shrinks the sample honestly, so a published claim score does
    # not move because the walker's coverage changed. Same semantics, and same
    # rationale, as `segment_base_rate`'s window.
    pack = _statpack(
        _term(2024, relist=(0.40, 100)),
        _term(2022, relist=(0.90, 100)),
        _term(2021, relist=(0.90, 100)),
    )
    assert claim_base_rate(_row("25-100"), pack, Claim.relisted, lookback_terms=2) == pytest.approx(
        0.40
    )


def test_the_default_lookback_is_unbounded() -> None:
    pack = _statpack(
        _term(2024, relist=(0.40, 100)),
        _term(2018, relist=(0.20, 100)),  # six Terms back — still pooled
    )
    row = _row("25-100")
    assert claim_base_rate(row, pack, Claim.relisted) == pytest.approx(0.30)
    assert claim_base_rate(row, pack, Claim.relisted, lookback_terms=0) == pytest.approx(0.30)


# --- claim_score: proper, and worth nothing for restating the baseline -------------


def test_reporting_the_baseline_scores_exactly_zero_either_way() -> None:
    # Realized, not merely in expectation: `p == b` is worth precisely nothing
    # whichever way the claim resolves. Exact equality, not approx — the two Brier
    # terms are the same expression, so any drift here is a changed rule.
    for b in (0.0, 0.02, 0.3, 0.5, 0.97, 1.0):
        assert claim_score(b, 0, b) == 0.0
        assert claim_score(b, 1, b) == 0.0


def test_a_forecast_closer_than_the_baseline_scores_positive() -> None:
    assert claim_score(0.9, 1, 0.3) == pytest.approx((0.3 - 1) ** 2 - (0.9 - 1) ** 2)
    assert claim_score(0.9, 1, 0.3) > 0


def test_a_confident_miss_costs() -> None:
    assert claim_score(0.9, 0, 0.3) == pytest.approx(0.3**2 - 0.9**2)
    assert claim_score(0.9, 0, 0.3) < 0


def test_the_score_is_proper_because_the_added_term_is_p_independent() -> None:
    # For a fixed b and y the score is -(p - y)^2 plus a constant, so the p that
    # maximizes it is p = y in the realized case and p = pi in expectation. Pinned
    # as a property: the gap between any two forecasts must not depend on b.
    for b in (0.05, 0.4, 0.8):
        gap = claim_score(0.7, 1, b) - claim_score(0.2, 1, b)
        assert gap == pytest.approx((0.2 - 1) ** 2 - (0.7 - 1) ** 2)


# --- the floor: what an uninformed control collects for free ----------------------


def _windowed_pack() -> StatPack:
    """A pack whose recent Terms disagree with the pooled history.

    OT2020-21 sat at 10%, OT2022-24 at 40%, and equal denominators make the pooled
    (unbounded) rate 28% against a 3-Term recent rate of 40%. That gap is the free
    score, and it is the shape of the real corpus: this repo ships an unbounded
    baseline lookback while the per-Term rates move Term to Term.
    """
    return _statpack(
        _term(2024, relist=(0.40, 100), cvsg=(0.40, 100)),
        _term(2023, relist=(0.40, 100), cvsg=(0.40, 100)),
        _term(2022, relist=(0.40, 100), cvsg=(0.40, 100)),
        _term(2021, relist=(0.10, 100), cvsg=(0.10, 100)),
        _term(2020, relist=(0.10, 100), cvsg=(0.10, 100)),
    )


def test_the_floor_is_positive_when_the_windows_disagree() -> None:
    # The justification for reporting a floor at all, pinned as a number. The
    # control knows nothing about the case; it reports the recent rate (0.40)
    # against a baseline pooled over every prior Term (0.28), and banks the
    # difference on both claims.
    pack = _windowed_pack()
    row = _row("25-100")
    outcome = _outcome(distributions=2, cvsg=True)  # both claims resolve true
    per_claim = claim_floor_scores(row, outcome, pack, floor_lookback_terms=3)
    expected = (0.28 - 1) ** 2 - (0.40 - 1) ** 2  # ~0.158 per claim
    assert per_claim == {
        Claim.relisted: pytest.approx(expected),
        Claim.cvsg: pytest.approx(expected),
    }
    total = claim_floor(row, outcome, pack, floor_lookback_terms=3)
    assert total > 0
    assert total == pytest.approx(2 * expected)


def test_the_floor_is_zero_when_the_windows_agree() -> None:
    # Same window on both sides -> the control *is* the baseline -> it earns nothing,
    # which is what `p == b` is worth. `floor_lookback_terms=0` is the degenerate
    # unbounded case that makes the two coincide.
    pack = _windowed_pack()
    row = _row("25-100")
    outcome = _outcome(distributions=2, cvsg=True)
    assert claim_floor(row, outcome, pack, floor_lookback_terms=0) == 0.0
    assert claim_floor(row, outcome, pack, lookback_terms=3, floor_lookback_terms=3) == 0.0


def test_a_recent_window_too_thin_to_price_falls_back_to_the_baseline() -> None:
    # No Term inside the control's window -> it has nothing more recent to say ->
    # it reports the baseline and scores 0, rather than dropping the claim and
    # leaving the floor covering fewer claims than the total it is subtracted from.
    pack = _statpack(_term(2019, relist=(0.40, 100)))
    floor = claim_floor_scores(
        _row("25-100"), _outcome(distributions=2), pack, claims=(Claim.relisted,)
    )
    assert floor == {Claim.relisted: 0.0}


def test_a_claim_with_no_baseline_leaves_the_set_on_both_sides() -> None:
    # CVSG resolves here but no prior Term priced it, so there is nothing to score
    # against. It has to drop out of the total AND the floor — a floor covering
    # fewer claims than the total it is subtracted from would inflate the lift.
    pack = _statpack(_term(2023, relist=(0.30, 100)))  # no cvsg rate anywhere
    row = _row("24-100")
    outcome = _outcome(distributions=2, cvsg=True)
    scores = claim_scores({Claim.relisted: 0.9, Claim.cvsg: 0.9}, row, outcome, pack)
    assert set(scores) == {Claim.relisted}
    assert set(claim_floor_scores(row, outcome, pack)) == {Claim.relisted}


def test_the_lift_is_the_total_over_the_control() -> None:
    pack = _windowed_pack()
    row = _row("25-100")
    outcome = _outcome(distributions=2, cvsg=True)
    scores = claim_scores({Claim.relisted: 0.9, Claim.cvsg: 0.9}, row, outcome, pack)
    total = claim_total({Claim.relisted: 0.9, Claim.cvsg: 0.9}, row, outcome, pack)
    assert total == pytest.approx(sum(scores.values()))
    # The floor is taken over exactly the claims the total covered.
    floor = claim_floor(row, outcome, pack, claims=scores.keys(), floor_lookback_terms=3)
    assert claim_lift(total, floor) == pytest.approx(total - floor)
    # A forecaster that only restates the recent rate lifts nothing over the control.
    parrot = claim_total({Claim.relisted: 0.40, Claim.cvsg: 0.40}, row, outcome, pack)
    assert claim_lift(parrot, floor) == pytest.approx(0.0)


def test_the_floor_obeys_the_same_leakage_guard_as_the_baseline() -> None:
    # The control has to be a total a real predictor could have earned, so its
    # recent window is still strictly-prior Terms. OT25's rate is 1.0 here; if the
    # control could see its own Term the floor would price off it.
    pack = _statpack(
        _term(2025, relist=(1.00, 100)),
        _term(2024, relist=(0.40, 100)),
        _term(2020, relist=(0.10, 100)),
    )
    row = _row("25-100")
    outcome = _outcome(distributions=2)
    floor = claim_floor_scores(row, outcome, pack, claims=(Claim.relisted,), floor_lookback_terms=1)
    # Baseline pools OT24 + OT20 = 0.25; the control's 1-Term window is OT24 = 0.40.
    assert floor == {Claim.relisted: pytest.approx((0.25 - 1) ** 2 - (0.40 - 1) ** 2)}
