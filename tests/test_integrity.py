"""The clock and forward-claim rules every scoring surface shares."""

from datetime import UTC, date, datetime

from fedcourtsai.integrity import (
    FORWARD,
    FORWARD_CLAIM_POLICY,
    RETROSPECTIVE,
    cell_clock,
    classify_stratum,
    forward_claim_breach,
    forward_claim_record,
)
from fedcourtsai.schemas import (
    Disposition,
    Engine,
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
    assert cell_clock(prediction).tzinfo is not None


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
