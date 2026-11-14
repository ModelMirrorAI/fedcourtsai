"""The interim per-moment reference line and the interim constant-forecast floor.

What the registration owes and these pin:

- **The statpack counts each later moment's pool** on the finer reading: a
  resolved application whose response request, or response, is dated strictly
  before its decision. A moment dated on the decision day, a moot dismissal and
  a row with no decision date join no pool, and the widened slice has twins.
- **The per-moment rate pools exactly the registered finer pool's Terms**: the
  caller's lookback before `INTERIM_WINDOW_FROM_TERM` and the three-Term window
  over the widened counts from it, under the same floor and refusals. The
  arrival moment has no pool.
- **The board scores a second line beside the registered one**, over a subset
  of its cells, only for a cell on the finer reading whose caller passed a
  window.
- **An interim block carries the constant-`denied` floor** under the rule that
  stamped `correct`, and leaves it null beside a grading whose `correct` no
  longer reproduces.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pytest

from fedcourtsai import corpus, leaderboard
from fedcourtsai.analytics import _InterimAcc
from fedcourtsai.integrity import FORWARD
from fedcourtsai.leaderboard import CellSkill, _evaluation_key, _floor_fields
from fedcourtsai.pipeline import alignment_board
from fedcourtsai.pipeline.base_rates import (
    INTERIM_BASE_RATE_MIN_RESOLVED,
    INTERIM_WINDOW_FROM_TERM,
    interim_base_rate,
    interim_moment_base_rate,
)
from fedcourtsai.process_version import FINER_INTERIM_READING_FROM
from fedcourtsai.schemas import (
    Disposition,
    Engine,
    Evaluation,
    InterimResolutionSignals,
    Moment,
    Outcome,
    Prediction,
    PredictionContext,
    ProcessVersion,
    Stage,
    StatPack,
    StatPackInterim,
    StatPackInterimTerm,
)

_EVENT = "evt-order-response-requested-disposition"
_DECIDED = date(2025, 3, 10)


def _row(n: int, **kwargs: Any) -> corpus.CorpusRow:
    fields: dict[str, Any] = {
        "case_id": f"scotus/{n}",
        "court": "scotus",
        "docket_number": f"24A{n}",
        "case_name": "x",
        "disposition": "denied",
        "application_kind": "substantive",
        "application_kind_wide": "substantive",
        "interim_reading": "denied",
        "date_decided": _DECIDED,
    }
    fields.update(kwargs)
    return corpus.CorpusRow.model_validate(fields)


def _moment_counts(acc: _InterimAcc, prefix: str = "") -> tuple[int, int, int, int]:
    return (
        getattr(acc, f"{prefix}moment_request_granted"),
        getattr(acc, f"{prefix}moment_request_resolved"),
        getattr(acc, f"{prefix}moment_response_filed_granted"),
        getattr(acc, f"{prefix}moment_response_filed_resolved"),
    )


def test_the_statpack_counts_a_moment_dated_strictly_before_the_decision() -> None:
    before = date(2025, 3, 3)
    acc = _InterimAcc()
    for row in (
        # Requested and answered before a grant: both pools, both granted.
        _row(
            1,
            disposition="granted",
            interim_reading="granted",
            response_requested_at=before,
            response_filed_at=before,
        ),
        # An unrequested response before a denial: the response pool alone.
        _row(2, response_filed_at=before),
        # A request dated on the decision day opens no scored cell.
        _row(3, response_requested_at=_DECIDED, response_filed_at=_DECIDED),
        # A moot dismissal leaves the finer pool, and every moment pool with it.
        _row(4, interim_reading="dismissed-moot", response_requested_at=before),
        # No decision date: the as-of order cannot be read.
        _row(5, date_decided=None, response_requested_at=before),
        # Reached neither moment.
        _row(6),
    ):
        acc.add(row)
    assert (acc.finer_granted, acc.finer_resolved) == (1, 5)
    assert _moment_counts(acc) == (1, 1, 1, 2)
    assert _moment_counts(acc, "wide_") == (1, 1, 1, 2)
    # The row with no decision date is the one no pool can place.
    assert (acc.moment_undated, acc.wide_moment_undated) == (1, 1)


def test_a_request_flagged_with_no_date_is_counted_undated() -> None:
    acc = _InterimAcc()
    acc.add(_row(1, response_requested=True))
    acc.add(_row(2, response_requested=True, response_requested_at=date(2025, 3, 1)))
    assert _moment_counts(acc) == (0, 1, 0, 0)
    assert acc.moment_undated == 1


def test_the_widened_twins_count_the_widened_slice() -> None:
    acc = _InterimAcc()
    # Substantive only on the widened ask: the registered pools do not see it.
    acc.add(_row(1, application_kind="unknown", response_requested_at=date(2025, 3, 1)))
    assert _moment_counts(acc) == (0, 0, 0, 0)
    assert _moment_counts(acc, "wide_") == (0, 1, 0, 0)
    total = _InterimAcc()
    total.merge(acc)
    total.merge(acc)
    assert _moment_counts(total, "wide_") == (0, 2, 0, 0)


def _term(
    year: int, *, moments: bool = True, unread: int = 0, undated: int = 0, scale: int = 1
) -> Any:
    counts: dict[str, int] = {}
    if moments:
        counts = {
            "moment_request_granted": 20 * scale,
            "moment_request_resolved": 60 * scale,
            "moment_response_filed_granted": 24 * scale,
            "moment_response_filed_resolved": 80 * scale,
            "wide_moment_request_granted": 21 * scale,
            "wide_moment_request_resolved": 70 * scale,
            "wide_moment_response_filed_granted": 27 * scale,
            "wide_moment_response_filed_resolved": 90 * scale,
            "moment_undated": undated,
            "wide_moment_undated": undated,
        }
    return StatPackInterimTerm(
        term=year,
        substantive_resolved=200,
        substantive_granted=20,
        finer_resolved=200,
        finer_granted=20,
        finer_moot=0,
        finer_unread=unread,
        wide_resolved=220,
        wide_granted=22,
        wide_finer_resolved=220,
        wide_finer_granted=22,
        wide_finer_unread=0,
        wide_unread=0,
        **counts,
    )


def _pack(*terms: Any) -> StatPack:
    return StatPack(
        interim=StatPackInterim(terms=list(terms), substantive_resolved=0, substantive_granted=0)
    )


def test_the_moment_rate_pools_strictly_prior_terms_inside_the_lookback() -> None:
    pack = _pack(_term(2026, scale=3), _term(2025), _term(2024), _term(2014, scale=5))
    rate = interim_moment_base_rate(2026, Moment.response_requested, pack, lookback_terms=10)
    assert rate == pytest.approx(40 / 120)
    filed = interim_moment_base_rate(2026, Moment.response_filed, pack, lookback_terms=10)
    assert filed == pytest.approx(48 / 160)
    # The registered finer pool reads the same two Terms.
    assert interim_base_rate(2026, pack, lookback_terms=10, reading="finer") == pytest.approx(0.1)


def test_the_arrival_moment_has_no_pool() -> None:
    pack = _pack(_term(2025), _term(2024))
    assert interim_moment_base_rate(2026, Moment.arrival, pack, lookback_terms=10) is None
    assert interim_moment_base_rate(2026, None, pack, lookback_terms=10) is None


@pytest.mark.parametrize("gap", [{"moments": False}, {"unread": 1}, {"undated": 1}])
def test_the_moment_rate_refuses_a_term_it_does_not_cover(gap: dict[str, Any]) -> None:
    pack = _pack(_term(2025), _term(2024, **gap))
    assert interim_moment_base_rate(2026, Moment.response_requested, pack) is None


def test_the_moment_rate_takes_the_registered_floor() -> None:
    assert INTERIM_BASE_RATE_MIN_RESOLVED > 30
    thin = _term(2025).model_copy(
        update={"moment_request_resolved": 30, "moment_request_granted": 10}
    )
    assert interim_moment_base_rate(2026, Moment.response_requested, _pack(thin)) is None
    assert interim_moment_base_rate(2026, Moment.response_filed, _pack(thin)) == pytest.approx(0.3)


def test_from_the_window_term_the_moment_rate_reads_the_widened_window() -> None:
    term = INTERIM_WINDOW_FROM_TERM
    pack = _pack(*(_term(term - back) for back in range(1, 6)))
    rate = interim_moment_base_rate(term, Moment.response_requested, pack, lookback_terms=10)
    # Three Terms whatever the caller passes, over the widened counts.
    assert rate == pytest.approx(63 / 210)


def _prediction(label: str, *, disposition: Disposition = Disposition.denied) -> Prediction:
    return Prediction(
        case_id="scotus/2",
        event_id=_EVENT,
        predictor_id="p",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2026, 11, 10),
        input_snapshot="x",
        granted=0,
        probability=0.3,
        predicted_disposition=disposition,
        context=PredictionContext(
            mode="forward",
            snapshot_date=date(2026, 11, 10),
            signals_observable=True,
            response_requested=True,
            referred_to_court=False,
            amicus_briefs=0,
            term=2026,
        ),
        process_version=ProcessVersion(
            label=label,
            digest="sha256:" + "0" * 64,
            stamped_at=datetime(2026, 11, 10, tzinfo=UTC),
        ),
    )


def _outcome(finer: str) -> Outcome:
    granted = int(finer in ("granted", "granted-in-part"))
    return Outcome(
        case_id="scotus/2",
        event_id=_EVENT,
        resolved_at=date(2026, 12, 1),
        actual_disposition=Disposition.granted if finer == "granted" else Disposition.denied,
        actual_granted=int(finer == "granted"),
        interim_signals=InterimResolutionSignals(
            response_requested=True, referred_to_court=False, amicus_briefs=0
        ),
        interim_reading=finer,
        interim_granted=granted,
    )


def _interim_cell(
    monkeypatch: pytest.MonkeyPatch,
    prediction: Prediction,
    outcome: Outcome,
    *,
    moment: Moment | None = Moment.response_requested,
    lookback_terms: int | None = 10,
    stage: Stage = Stage.interim,
) -> Any:
    monkeypatch.setattr(leaderboard, "_scored_prediction", lambda _dir, _ev: prediction)
    target = outcome.interim_granted
    assert target is not None
    return leaderboard._interim_cell(
        Path("."),
        object(),  # type: ignore[arg-type]
        stage,
        moment,
        outcome,
        _pack(_term(2025), _term(2024)),
        target,
        lookback_terms,
    )


def test_a_finer_cell_at_a_later_moment_gets_the_moment_baseline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cell = _interim_cell(monkeypatch, _prediction(FINER_INTERIM_READING_FROM), _outcome("denied"))
    assert cell.moment_baseline == pytest.approx((40 / 120) ** 2)
    assert (cell.deny, cell.recomputed) == (1, 1)


def test_the_floor_follows_the_finer_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    # A partial grant is a miss for a constant `denied` call on the finer
    # reading, and a predicted `granted` is correct against it.
    prediction = _prediction(FINER_INTERIM_READING_FROM, disposition=Disposition.granted)
    cell = _interim_cell(monkeypatch, prediction, _outcome("granted-in-part"))
    assert (cell.deny, cell.recomputed) == (0, 1)
    assert cell.moment_baseline == pytest.approx((1 - 40 / 120) ** 2)


@pytest.mark.parametrize(
    "kwargs",
    [{"moment": Moment.arrival}, {"lookback_terms": None}],
)
def test_no_moment_baseline_without_a_pool_or_a_window(
    monkeypatch: pytest.MonkeyPatch, kwargs: dict[str, Any]
) -> None:
    cell = _interim_cell(
        monkeypatch, _prediction(FINER_INTERIM_READING_FROM), _outcome("denied"), **kwargs
    )
    assert cell.moment_baseline is None
    assert cell.deny == 1  # the floor needs neither


def test_a_registered_reading_cell_has_no_moment_line(monkeypatch: pytest.MonkeyPatch) -> None:
    cell = _interim_cell(monkeypatch, _prediction("proc-v16"), _outcome("denied"))
    assert cell.moment_baseline is None
    assert cell.deny == 1


def test_a_cell_off_the_interim_stage_carries_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    cell = _interim_cell(
        monkeypatch, _prediction(FINER_INTERIM_READING_FROM), _outcome("denied"), stage=Stage.cert
    )
    assert (cell.moment_baseline, cell.deny, cell.recomputed) == (None, None, None)


def _evaluation(n: int, correct: int, *, event: int = 0) -> Evaluation:
    return Evaluation(
        case_id=f"scotus/{event}",
        event_id=_EVENT,
        predictor_id="p",
        evaluator_id=f"judge-{n}",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2026, 12, 2),
        correct=correct,
        brier_score=0.09,
    )


def _skills(*pairs: tuple[Evaluation, CellSkill]) -> dict[Any, CellSkill]:
    return {_evaluation_key(ev): skill for ev, skill in pairs}


def test_an_interim_block_carries_the_constant_denied_floor() -> None:
    # Two events, two judges each: the forecast is right on both, a constant
    # `denied` on one.
    evals = [_evaluation(n, 1, event=event) for event in (0, 1) for n in (0, 1)]
    deny = {0: 1, 1: 0}
    skills = _skills(
        *(
            (ev, CellSkill(brier=0.09, deny_correct=deny[i // 2], recomputed_correct=1))
            for i, ev in enumerate(evals)
        )
    )
    fields = _floor_fields(evals, skills, None)
    assert fields["always_deny_accuracy"] == 0.5
    assert fields["accuracy_lift"] == 0.5
    assert fields["event_always_deny_accuracy"] == 0.5
    assert fields["event_accuracy_lift"] == 0.5
    assert "grants_realized" not in fields


def test_the_floor_stays_null_beside_a_grading_that_no_longer_reproduces() -> None:
    evals = [_evaluation(0, 1)]
    stale = _skills((evals[0], CellSkill(brier=0.09, deny_correct=1, recomputed_correct=0)))
    assert "always_deny_accuracy" not in _floor_fields(evals, stale, None)
    uncovered = _skills((evals[0], CellSkill(brier=0.09)))
    assert "always_deny_accuracy" not in _floor_fields(evals, uncovered, None)
    assert "always_deny_accuracy" not in _floor_fields(evals, {}, None)


def test_the_moment_line_aggregates_beside_the_registered_one() -> None:
    # Ten events with the line and one more the registered column alone scores.
    evals = [_evaluation(0, 1, event=event) for event in range(11)]
    with_line = CellSkill(brier=0.09, prior_term_baseline=0.01, moment_baseline=0.12)
    skills = _skills(
        *((ev, with_line) for ev in evals[:10]),
        (evals[10], CellSkill(brier=0.09, prior_term_baseline=0.01)),
    )
    stratum = leaderboard._aggregate(evals, skills)
    assert stratum is not None
    assert stratum.population_brier_skill_score == pytest.approx(1 - 0.09 / 0.01)
    assert stratum.skill_scored == 11
    assert stratum.population_moment_skill_score == pytest.approx(1 - 0.09 / 0.12)
    assert (stratum.moment_skill_scored, stratum.moment_skill_events_scored) == (10, 10)
    bare = leaderboard._aggregate(evals, {})
    assert bare is not None
    assert (bare.population_moment_skill_score, bare.moment_skill_scored) == (None, None)


def test_below_the_event_floor_the_block_carries_counts_and_no_figure() -> None:
    # Nine events graded by three judges each: 27 gradings, still nine events.
    assert leaderboard.MIN_EVENTS_FOR_MOMENT_LINE == 10
    evals = [_evaluation(n, 1, event=event) for event in range(9) for n in range(3)]
    cell = CellSkill(brier=0.09, prior_term_baseline=0.01, moment_baseline=0.12)
    stratum = leaderboard._aggregate(evals, _skills(*((ev, cell) for ev in evals)))
    assert stratum is not None
    assert stratum.population_moment_skill_score is None
    assert (stratum.moment_skill_scored, stratum.moment_skill_events_scored) == (27, 9)
    payload = stratum.model_dump(mode="json")
    assert "population_moment_skill_score" not in payload
    assert payload["moment_skill_events_scored"] == 9


def _components(
    monkeypatch: pytest.MonkeyPatch,
    evaluation: Evaluation,
    moment: Moment,
    *,
    lookback_terms: int | None = 10,
) -> dict[Any, CellSkill]:
    """`skill_components` over one interim cell, its artifacts supplied in memory."""
    prediction = _prediction(FINER_INTERIM_READING_FROM)
    outcome = _outcome("denied")
    monkeypatch.setattr(leaderboard, "_scored_prediction", lambda _dir, _ev: prediction)
    monkeypatch.setattr(leaderboard, "_read_outcome", lambda _dir, _ev, _cache: outcome)
    monkeypatch.setattr(alignment_board, "load_inputs", lambda _root: None)
    return leaderboard.skill_components(
        [(evaluation, FORWARD, Stage.interim, moment)],
        Path("."),
        _pack(_term(2025), _term(2024)),
        interim_lookback_terms=lookback_terms,
    )


def test_the_moment_line_rides_only_on_a_cell_the_registered_column_scores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    base = _evaluation(0, 1)
    # Brier 0.09 against a 0.1 pool on a denial: skill 1 - 0.09 / 0.01.
    scored = base.model_copy(update={"segment_base_rate": 0.1, "brier_skill_score": -8.0})
    (cell,) = _components(monkeypatch, scored, Moment.response_requested).values()
    assert cell.prior_term_baseline == pytest.approx(0.01)
    assert cell.moment_baseline == pytest.approx((40 / 120) ** 2)
    assert (cell.deny_correct, cell.recomputed_correct) == (1, 1)
    # No recorded skill: the cell stays in the map for its floor, with no line.
    (floor_only,) = _components(monkeypatch, base, Moment.response_requested).values()
    assert floor_only.prior_term_baseline is None
    assert floor_only.moment_baseline is None
    assert floor_only.deny_correct == 1
    # No window from the caller: the floor, and no line.
    (unwindowed,) = _components(
        monkeypatch, scored, Moment.response_requested, lookback_terms=None
    ).values()
    assert unwindowed.moment_baseline is None
    # A grading with no Brier carries nothing, which leaves its block's floor null.
    unscored = base.model_copy(update={"brier_score": None})
    assert _components(monkeypatch, unscored, Moment.response_requested) == {}


def test_a_block_with_no_moment_line_serializes_without_its_fields() -> None:
    evals = [_evaluation(0, 1)]
    stratum = leaderboard._aggregate(evals, _skills((evals[0], CellSkill(brier=0.09))))
    assert stratum is not None
    payload = stratum.model_dump(mode="json")
    assert "population_moment_skill_score" not in payload
    assert "moment_skill_scored" not in payload
    assert "moment_skill_events_scored" not in payload
