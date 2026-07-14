from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from fedcourtsai.pipeline.evaluate import brier_score, is_correct, vote_accuracy
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    Disposition,
    Engine,
    Evaluation,
    FlagCategory,
    FlagSeverity,
    JudgeVote,
    ModelUsage,
    Outcome,
    Prediction,
    TrackedCase,
    UsageRole,
)


def _prediction(**kw: object) -> Prediction:
    base = dict(
        case_id="ca9/123",
        event_id="evt-motion-stay",
        predictor_id="claude-baseline",
        engine=Engine.claude_code,
        run_id="r1",
        created_at=datetime(2026, 6, 24, tzinfo=UTC),
        input_snapshot="record/snapshots/2026-06-24.json",
        granted=1,
        probability=0.8,
        predicted_disposition=Disposition.granted,
    )
    base.update(kw)
    return Prediction.model_validate(base)


def test_probability_bounds_enforced() -> None:
    with pytest.raises(ValidationError):
        _prediction(probability=1.5)


def test_extra_fields_forbidden() -> None:
    with pytest.raises(ValidationError):
        TrackedCase.model_validate(
            {
                "case_id": "ca9/1",
                "court_id": "ca9",
                "docket_id": 1,
                "tracked_since": date(2026, 1, 1),
                "surprise": "nope",
            }
        )


def _usage(**kw: object) -> ModelUsage:
    base: dict[str, object] = dict(
        case_id="ca9/123",
        event_id="evt-motion-stay",
        run_id="20260624T103000Z",
        role=UsageRole.predictor,
        actor_id="claude-baseline",
        engine=Engine.claude_code,
        model="claude-opus-4-8",
        created_at=datetime(2026, 6, 24, tzinfo=UTC),
        input_tokens=150_000,
        output_tokens=8_000,
        estimated_cost_usd=0.95,
    )
    base.update(kw)
    return ModelUsage.model_validate(base)


def test_model_usage_roundtrips() -> None:
    usage = _usage(cache_read_input_tokens=50_000)
    assert usage.role == UsageRole.predictor
    assert usage.cache_creation_input_tokens == 0


def test_model_usage_rejects_negative_tokens() -> None:
    with pytest.raises(ValidationError):
        _usage(input_tokens=-1)


def test_model_usage_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        _usage(surprise="nope")


def _evaluation(**kw: object) -> Evaluation:
    base: dict[str, object] = dict(
        case_id="ca9/123",
        event_id="evt-motion-stay",
        predictor_id="claude-baseline",
        evaluator_id="gemini-judge",
        engine=Engine.gemini,
        run_id="r1",
        created_at=datetime(2026, 6, 24, tzinfo=UTC),
        correct=1,
    )
    base.update(kw)
    return Evaluation.model_validate(base)


def test_engine_includes_gemini() -> None:
    assert Engine("gemini") is Engine.gemini


def test_evaluation_tracks_provider_engine() -> None:
    assert _evaluation().engine == Engine.gemini


def test_evaluation_records_model_when_given() -> None:
    # `model` records which model produced the evaluation (all three providers);
    # optional so records written before the field existed still validate.
    assert _evaluation(model="gemini-3.1-pro-preview").model == "gemini-3.1-pro-preview"
    assert _evaluation().model is None


def test_prediction_records_model_when_given() -> None:
    assert _prediction(model="claude-fable-5").model == "claude-fable-5"


def test_prediction_big_case_score_is_optional_and_range_checked() -> None:
    # Optional (defaults None) so a record written before the field existed still
    # validates — the backward-compat contract for the new big-case dimension.
    plain = _prediction()
    assert plain.big_case_score is None and plain.big_case_rationale is None
    scored = _prediction(big_case_score=0.8, big_case_rationale="major separation-of-powers case")
    assert scored.big_case_score == 0.8
    for bad in (-0.1, 1.5):
        with pytest.raises(ValidationError):
            _prediction(big_case_score=bad)
    with pytest.raises(ValidationError):  # rationale is length-bounded
        _prediction(big_case_rationale="x" * 501)


def test_evaluation_requires_engine() -> None:
    bad = {
        "case_id": "ca9/123",
        "event_id": "evt-motion-stay",
        "predictor_id": "claude-baseline",
        "evaluator_id": "gemini-judge",
        "run_id": "r1",
        "created_at": datetime(2026, 6, 24, tzinfo=UTC),
        "correct": 1,
    }
    with pytest.raises(ValidationError):
        Evaluation.model_validate(bad)


def _flags(**kw: object) -> AgentFlags:
    base: dict[str, object] = dict(
        case_id="ca9/123",
        run_id="r1",
        role=UsageRole.predictor,
        actor_id="claude-baseline",
        flags=[AgentFlag(category=FlagCategory.data_quality, message="snapshot is empty")],
    )
    base.update(kw)
    return AgentFlags.model_validate(base)


def test_agent_flags_round_trip() -> None:
    flags = _flags(
        flags=[
            AgentFlag(
                category=FlagCategory.blocked,
                severity=FlagSeverity.blocker,
                message="no snapshot provisioned",
                event_id="evt-motion-stay",
            )
        ]
    )
    assert flags.flags[0].severity == FlagSeverity.blocker
    assert flags.flags[0].event_id == "evt-motion-stay"
    # use_enum_values makes the enum fields serialize as their wire strings.
    assert flags.model_dump()["flags"][0]["category"] == "blocked"


def test_agent_flags_requires_at_least_one_flag() -> None:
    # The file is written only when there is something to say; an empty list is invalid.
    with pytest.raises(ValidationError):
        _flags(flags=[])


def test_agent_flag_message_must_be_non_empty() -> None:
    with pytest.raises(ValidationError):
        AgentFlag(category=FlagCategory.other, message="")


def test_agent_flags_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        _flags(surprise="nope")


def test_scoring() -> None:
    pred = _prediction(
        probability=0.75,
        votes=[JudgeVote(judge="smith", vote=Disposition.granted)],
    )
    outcome = Outcome(
        case_id="ca9/123",
        event_id="evt-motion-stay",
        resolved_at=date(2026, 7, 1),
        actual_disposition=Disposition.granted,
        actual_granted=1,
        votes=[JudgeVote(judge="smith", vote=Disposition.granted)],
    )
    assert is_correct(pred, outcome) == 1
    assert brier_score(pred, outcome) == pytest.approx(0.0625)
    assert vote_accuracy(pred, outcome) == 1.0


def test_is_correct_treats_gvr_as_a_distinct_label_but_a_grant_for_brier() -> None:
    # gvr is its own label: a `granted` prediction is not `correct` on a gvr
    # outcome, but the Brier score is unchanged because gvr counts as a grant
    # (actual_granted == 1), so a confident grant forecast still scores well.
    gvr_outcome = Outcome(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        resolved_at=date(2026, 7, 1),
        actual_disposition=Disposition.gvr,
        actual_granted=1,
    )
    said_granted = _prediction(predicted_disposition=Disposition.granted, probability=0.9)
    said_gvr = _prediction(predicted_disposition=Disposition.gvr, probability=0.9)
    assert is_correct(said_granted, gvr_outcome) == 0  # label differs
    assert is_correct(said_gvr, gvr_outcome) == 1
    assert brier_score(said_granted, gvr_outcome) == pytest.approx(0.01)  # grant on the binary axis
