from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from fedcourtsai.pipeline.evaluate import brier_score, is_correct, vote_accuracy
from fedcourtsai.schemas import (
    Disposition,
    Engine,
    JudgeVote,
    Outcome,
    Prediction,
    TrackedCase,
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
