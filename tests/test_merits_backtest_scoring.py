from datetime import date, timedelta

import pytest

from fedcourtsai.backtest import BacktestPrediction
from fedcourtsai.merits_backtest import (
    MERITS_REPLAY_BASELINE_MIN,
    MeritsBacktestPopulation,
    MeritsBacktestTerm,
    MeritsReplayCase,
    MeritsReplayCell,
    MeritsReplayCutoff,
    MeritsReplayFenced,
    MeritsReplayOutcome,
    MeritsReplaySweep,
    as_of_base_rate,
    baseline_pool_terms,
    score_merits_backtest,
)
from fedcourtsai.schemas import Disposition, Judgment, MeritsBacktest, Moment


def _case(n: int, *, term: int = 2024, decided: date, disturbed: bool = True) -> MeritsReplayCase:
    granted = date(term, 1, 10)
    return MeritsReplayCase(
        case_id=f"scotus/{n}",
        docket_number=f"{term % 100}-{n}",
        case_name=None,
        term=term,
        ifp=False,
        argued=date(term, 12, 1),
        decided=decided,
        judgment=Judgment.reversed if disturbed else Judgment.affirmed,
        disturbed=disturbed,
        method=None,
        cutoffs=[
            MeritsReplayCutoff(
                moment=Moment.grant,
                event_id="evt-order-judgment",
                opened_at=granted,
                cutoff=granted + timedelta(days=1),
            ),
            MeritsReplayCutoff(
                moment=Moment.briefed,
                event_id="evt-brief-judgment",
                opened_at=date(term, 9, 1),
                cutoff=date(term, 9, 2),
            ),
        ],
    )


def _cell(case: MeritsReplayCase, moment: Moment) -> MeritsReplayCell:
    [cut] = [c for c in case.cutoffs if c.moment is moment]
    return MeritsReplayCell(
        case_id=case.case_id,
        event_id=cut.event_id,
        moment=moment,
        cutoff=cut.cutoff,
        snapshot_date=cut.cutoff,
        provenance="truncated",
        dropped_entries=0,
        dropped_documents=0,
        documents=["petition"],
    )


def _said(p: float) -> BacktestPrediction:
    return BacktestPrediction(Disposition.granted if p >= 0.5 else Disposition.denied, p)


def _population(cases: list[MeritsReplayCase]) -> MeritsBacktestPopulation:
    return MeritsBacktestPopulation(
        pulled_through=date(2026, 10, 24),
        terms=[
            MeritsBacktestTerm(
                term=2024,
                assigned=len(cases),
                order_riding=0,
                argued_unjudged=1,
                plenary_decided=len(cases),
                cases=len(cases),
                excluded={"no-briefed-date": 1},
            )
        ],
        cases=cases,
        excluded=[],
    )


def test_the_as_of_base_rate_admits_only_judgments_decided_before_the_cutoff() -> None:
    cutoff = date(2024, 6, 1)
    known = [_case(n, term=2023, decided=date(2024, 3, 1), disturbed=n % 3 != 0) for n in range(30)]
    later = [_case(100 + n, term=2023, decided=date(2024, 6, 1)) for n in range(10)]
    stale = [_case(200 + n, term=2019, decided=date(2020, 5, 1)) for n in range(10)]

    rate = as_of_base_rate([*known, *later, *stale], cutoff, 2024)

    assert rate == pytest.approx(sum(c.disturbed for c in known) / len(known))


def test_the_as_of_base_rate_is_null_below_its_floor() -> None:
    thin = [
        _case(n, term=2023, decided=date(2024, 3, 1)) for n in range(MERITS_REPLAY_BASELINE_MIN - 1)
    ]

    assert as_of_base_rate(thin, date(2024, 6, 1), 2024) is None


def test_the_pool_reaches_back_the_lookback_from_the_oldest_term() -> None:
    assert baseline_pool_terms([2025, 2024]) == [2021, 2022, 2023, 2024, 2025]
    assert baseline_pool_terms([]) == []


def test_a_report_scores_each_moment_and_compares_them_only_on_the_paired_cases() -> None:
    reversed_case = _case(1, decided=date(2025, 6, 1), disturbed=True)
    affirmed_case = _case(2, decided=date(2025, 6, 2), disturbed=False)
    population = _population([reversed_case, affirmed_case])
    # Thirty pooled judgments decided before both cutoffs, two thirds disturbed.
    pool = [
        _case(10 + n, term=2023, decided=date(2023, 12, 1), disturbed=n % 3 != 0) for n in range(30)
    ]
    sweep = MeritsReplaySweep(
        cells=[
            _cell(reversed_case, Moment.grant),
            _cell(affirmed_case, Moment.grant),
            _cell(reversed_case, Moment.briefed),
        ],
        fenced=[
            MeritsReplayFenced(
                case_id=affirmed_case.case_id,
                event_id="evt-brief-judgment",
                moment=Moment.briefed,
                reason="briefs-not-staged",
                detail="",
                judgment=affirmed_case.judgment,
                disturbed=False,
            )
        ],
    )
    predictions = {
        "claude-baseline": {
            Moment.grant: {"scotus/1": _said(0.6), "scotus/2": _said(0.4)},
            # A prediction for the fenced cell is not scored.
            Moment.briefed: {"scotus/1": _said(0.9), "scotus/2": _said(0.9)},
        },
        "codex-baseline": {Moment.grant: {"scotus/1": _said(0.2)}},
    }

    outcome = MeritsReplayOutcome(
        sweep=sweep,
        predictions=predictions,
        ran_on={"claude-baseline": ("claude", "model-x")},
        unavailable=[],
        lost_cells=[],
    )

    report = score_merits_backtest(population, pool, outcome, run_id="20261024T000000Z")

    MeritsBacktest.model_validate_json(report.model_dump_json())
    assert (report.cells, report.paired_cases) == ({"grant": 2, "briefed": 1}, 1)
    assert report.fenced == {"grant": {}, "briefed": {"briefs-not-staged": 1}}
    assert report.terms[0].argued_unjudged == 1
    claude, codex = report.entries
    grant, briefed = claude.moments
    assert (grant.events_scored, grant.lost, grant.accuracy) == (2, 0, 1.0)
    assert grant.mean_brier_score == pytest.approx((0.4**2 + 0.4**2) / 2)
    assert (grant.disturbed_share, grant.majority_accuracy) == (0.5, 0.5)
    assert grant.baselined_brier_score == pytest.approx(0.4**2)
    base = 2 / 3
    assert grant.baselined == 2
    assert grant.brier_skill == pytest.approx(1 - (0.4**2 + 0.4**2) / ((base - 1) ** 2 + base**2))
    assert (briefed.events_scored, briefed.lost) == (1, 0)
    assert (claude.paired.cases, claude.paired.disturbed) == (1, 1)
    assert claude.paired.brier_change == pytest.approx(0.1**2 - 0.4**2)
    assert (claude.engine, claude.model) == ("claude", "model-x")
    codex_grant, codex_briefed = codex.moments
    assert (codex_grant.events_scored, codex_grant.lost) == (1, 1)
    assert (codex_briefed.events_scored, codex_briefed.lost, codex_briefed.accuracy) == (0, 1, None)
    assert codex.paired.cases == 0 and codex.paired.brier_change is None


def test_a_cell_with_no_baseline_is_scored_but_not_counted_toward_skill() -> None:
    case = _case(1, decided=date(2025, 6, 1))
    sweep = MeritsReplaySweep(cells=[_cell(case, Moment.grant)], fenced=[])
    predictions = {"claude-baseline": {Moment.grant: {"scotus/1": _said(0.7)}}}

    outcome = MeritsReplayOutcome(
        sweep=sweep, predictions=predictions, ran_on={}, unavailable=[], lost_cells=[]
    )

    report = score_merits_backtest(_population([case]), [], outcome)

    [grant, _] = report.entries[0].moments
    assert (grant.events_scored, grant.baselined, grant.brier_skill) == (1, 0, None)
