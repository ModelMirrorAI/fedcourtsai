"""The clock and forward-claim rules every scoring surface shares."""

from datetime import UTC, date, datetime

from fedcourtsai.integrity import (
    FORWARD,
    FORWARD_CLAIM_POLICY,
    RETROSPECTIVE,
    cell_clock,
    classify_stratum,
    evaluation_clock,
    forward_claim_breach,
    forward_claim_record,
    latest_evaluations,
)
from fedcourtsai.schemas import (
    Disposition,
    Engine,
    Evaluation,
    Outcome,
    Prediction,
    PredictionContext,
    ProcessVersion,
)


def _prediction(
    *,
    created_at: datetime,
    stamped_at: datetime | None = None,
    mode: str | None = None,
) -> Prediction:
    context = (
        PredictionContext(
            mode=mode,
            snapshot_date=date(2026, 1, 5),
            signals_observable=True,
            distribution_count=1,
            band="baseline",
            salience_version="sal-v2",
            term=2025,
        )
        if mode is not None
        else None
    )
    return Prediction(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        predictor_id="alpha",
        engine=Engine.claude_code,
        run_id="20260101T000000Z",
        created_at=created_at,
        input_snapshot="record/snapshots/2026-01-01.json",
        granted=0,
        probability=0.1,
        predicted_disposition=Disposition.denied,
        process_version=(
            ProcessVersion(label="proc-v2", digest="sha256:x", stamped_at=stamped_at)
            if stamped_at is not None
            else None
        ),
        context=context,
    )


def _outcome(resolved_at: date) -> Outcome:
    return Outcome(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        resolved_at=resolved_at,
        actual_granted=0,
        actual_disposition=Disposition.denied,
    )


def test_cell_clock_prefers_the_harness_stamp() -> None:
    prediction = _prediction(
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        stamped_at=datetime(2026, 2, 2, tzinfo=UTC),
    )
    assert cell_clock(prediction) == datetime(2026, 2, 2, tzinfo=UTC)


def test_cell_clock_falls_back_to_created_at_on_an_unstamped_cell() -> None:
    prediction = _prediction(created_at=datetime(2026, 1, 1, tzinfo=UTC))
    assert cell_clock(prediction) == datetime(2026, 1, 1, tzinfo=UTC)


def test_cell_clock_normalizes_a_bare_timestamp_to_utc() -> None:
    # Agent-written created_at is not guaranteed an offset; clocks from
    # different writers must still compare.
    prediction = _prediction(created_at=datetime(2026, 1, 1))
    assert cell_clock(prediction) == datetime(2026, 1, 1, tzinfo=UTC)


def test_forward_claim_breach_needs_a_forward_context() -> None:
    # A null-context cell asserts nothing, and a replay cell runs after
    # resolution by design: neither can breach.
    resolved = _outcome(date(2026, 1, 1))
    late = datetime(2026, 6, 1, tzinfo=UTC)
    assert forward_claim_breach(_prediction(created_at=late), resolved) is None
    assert forward_claim_breach(_prediction(created_at=late, mode="replay"), resolved) is None
    assert forward_claim_breach(_prediction(created_at=late, mode="forward"), resolved)


def test_no_breach_when_the_event_resolved_after_the_clock() -> None:
    prediction = _prediction(created_at=datetime(2026, 1, 1, tzinfo=UTC), mode="forward")
    assert forward_claim_breach(prediction, _outcome(date(2026, 3, 1))) is None


def test_the_breach_keys_on_the_stamp_not_the_agent_clock() -> None:
    # The agent's created_at predates the resolution; the harness stamp does
    # not. The boundary must not rest on the clock the agent controls.
    prediction = _prediction(
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        stamped_at=datetime(2026, 6, 1, tzinfo=UTC),
        mode="forward",
    )
    assert forward_claim_breach(prediction, _outcome(date(2026, 3, 1)))


def test_forward_claim_record_carries_the_policy() -> None:
    record = forward_claim_record(2)
    assert record.policy == FORWARD_CLAIM_POLICY
    assert record.excluded == 2


def test_a_same_day_tie_is_not_a_breach() -> None:
    # An honest forward cell that lost a same-day race looks identical to a
    # mis-provisioned one, so the tie falls to the stratum boundary's own
    # conservative rule (retrospective), never to exclusion.
    prediction = _prediction(created_at=datetime(2026, 3, 1, 18, 0, tzinfo=UTC), mode="forward")
    assert forward_claim_breach(prediction, _outcome(date(2026, 3, 1))) is None


def test_an_excluded_cell_could_never_have_classified_forward() -> None:
    # The argument that defeats "you dropped the cells that made you look
    # bad": the breach predicate (strictly before the clock day) implies the
    # retrospective predicate (on or before), so exclusion can only ever touch
    # cells outside the claimable stratum. Pinned at the boundary so a flip of
    # either operator fails here.
    clock = datetime(2026, 3, 2, tzinfo=UTC)
    for resolved in (date(2026, 3, 1), date(2026, 3, 2), date(2026, 3, 3)):
        prediction = _prediction(created_at=clock, mode="forward")
        breach = forward_claim_breach(prediction, _outcome(resolved))
        stratum = classify_stratum(clock, resolved)
        if breach is not None:
            assert stratum is RETROSPECTIVE
    assert classify_stratum(clock, date(2026, 3, 3)) is FORWARD
    assert (
        forward_claim_breach(
            _prediction(created_at=clock, mode="forward"), _outcome(date(2026, 3, 3))
        )
        is None
    )


def test_forward_claim_record_splits_by_predictor_and_carries_the_denominator() -> None:
    record = forward_claim_record(
        [("beta", "reason"), ("alpha", "reason"), ("beta", "reason")], claimed_forward=5
    )
    assert record.excluded == 3
    assert record.claimed_forward == 5
    assert record.by_predictor == {"alpha": 1, "beta": 2}


def _evaluation(
    *,
    created_at: datetime,
    stamped_at: datetime | None = None,
    run_id: str = "20260101T000000Z",
    evaluator_id: str = "eval-a",
) -> Evaluation:
    return Evaluation(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        predictor_id="alpha",
        evaluator_id=evaluator_id,
        engine=Engine.claude_code,
        run_id=run_id,
        created_at=created_at,
        correct=1,
        process_version=(
            ProcessVersion(label="proc-v2", digest="sha256:x", stamped_at=stamped_at)
            if stamped_at is not None
            else None
        ),
    )


def test_evaluation_clock_prefers_the_harness_stamp() -> None:
    evaluation = _evaluation(
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        stamped_at=datetime(2026, 2, 2, tzinfo=UTC),
    )
    assert evaluation_clock(evaluation) == datetime(2026, 2, 2, tzinfo=UTC)


def test_evaluation_clock_falls_back_to_created_at_on_an_unstamped_cell() -> None:
    evaluation = _evaluation(created_at=datetime(2026, 1, 1, tzinfo=UTC))
    assert evaluation_clock(evaluation) == datetime(2026, 1, 1, tzinfo=UTC)


def test_evaluation_clock_normalizes_a_bare_timestamp_to_utc() -> None:
    # Same rule as the prediction clock: a naive created_at reads as UTC so
    # clocks from different writers always compare.
    evaluation = _evaluation(created_at=datetime(2026, 1, 1))
    assert evaluation_clock(evaluation) == datetime(2026, 1, 1, tzinfo=UTC)


def test_a_clock_tie_between_two_gradings_breaks_on_the_run_id() -> None:
    # Two runs of one grader can share a clock — two unstamped runs written the
    # same second, or two stamps from one `stamp-cell` invocation. The survivor
    # must be a property of the records, not of dict insertion, or a board
    # rebuild could pick a different grading from an unchanged ledger.
    same_clock = datetime(2026, 2, 2, tzinfo=UTC)
    lower = _evaluation(created_at=same_clock, run_id="20260101T000000Z")
    higher = _evaluation(created_at=same_clock, run_id="20260202T000000Z")

    assert [ev.run_id for ev in latest_evaluations([lower, higher])] == ["20260202T000000Z"]
    # ...and the input order does not decide it.
    assert [ev.run_id for ev in latest_evaluations([higher, lower])] == ["20260202T000000Z"]


def test_survivors_come_back_in_input_order() -> None:
    # The ledger reads hand this function `sorted(glob(...))` path order and the
    # boards serialize deterministically off it, so the collapse must preserve
    # the surviving records' relative order rather than emit them in key order.
    first = _evaluation(created_at=datetime(2026, 1, 1, tzinfo=UTC), evaluator_id="eval-a")
    superseded = _evaluation(
        created_at=datetime(2026, 1, 1, tzinfo=UTC), evaluator_id="eval-b", run_id="r1"
    )
    winner = _evaluation(
        created_at=datetime(2026, 3, 3, tzinfo=UTC), evaluator_id="eval-b", run_id="r2"
    )
    last = _evaluation(created_at=datetime(2026, 1, 1, tzinfo=UTC), evaluator_id="eval-c")

    kept = latest_evaluations([first, superseded, winner, last])

    assert [ev.evaluator_id for ev in kept] == ["eval-a", "eval-b", "eval-c"]
    assert [ev.run_id for ev in kept] == ["20260101T000000Z", "r2", "20260101T000000Z"]
