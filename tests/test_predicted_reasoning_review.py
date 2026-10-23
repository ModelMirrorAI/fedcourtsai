"""The evaluator-authored grade of ``predicted_reasoning.md`` and the review behind it.

``Evaluation.predicted_reasoning_quality`` grades the forecast document alone
(``docs/outcome-decomposition.md``, *Grading the forecast document, design*).
The schema holds the grade to its audit trail: a grade stands on the central
claims it rests on, and a null grade beside a review states the record's
ground for it.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    CentralClaim,
    Engine,
    Evaluation,
    PredictedReasoningReview,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.validate import (
    CHECK_PREDICTED_REASONING_HELD,
    check_predicted_reasoning_grade_held,
)

_CLAIMS = [
    CentralClaim(claim="The petition is denied.", status="borne-out", basis="Order list"),
    CentralClaim(claim="No CVSG issues.", status="borne-out"),
    CentralClaim(claim="Justice Thomas dissents from denial.", status="not-borne-out"),
]


def _evaluation(**fields: Any) -> Evaluation:
    return Evaluation(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        predictor_id="p",
        evaluator_id="e",
        engine=Engine.claude_code,
        run_id="r",
        created_at=datetime(2026, 10, 23),
        correct=True,
        **fields,
    )


def test_an_evaluation_that_was_not_asked_for_the_grade_carries_neither_field() -> None:
    evaluation = _evaluation()
    assert evaluation.predicted_reasoning_quality is None
    assert evaluation.predicted_reasoning_review is None


def test_a_grade_with_its_central_claims_validates_and_round_trips(tmp_path: Path) -> None:
    evaluation = _evaluation(
        predicted_reasoning_quality=0.75,
        predicted_reasoning_review=PredictedReasoningReview(central_claims=_CLAIMS),
    )
    path = tmp_path / "evaluation.json"
    write_json(path, evaluation)
    assert read_model(path, Evaluation) == evaluation
    assert json.loads(path.read_text())["predicted_reasoning_review"]["central_claims"][2][
        "status"
    ] == ("not-borne-out")


def test_a_grade_without_a_review_is_refused() -> None:
    with pytest.raises(ValidationError, match="central claims"):
        _evaluation(predicted_reasoning_quality=0.5)


def test_a_grade_whose_review_lists_no_claims_is_refused() -> None:
    with pytest.raises(ValidationError, match="central claims"):
        _evaluation(
            predicted_reasoning_quality=0.5,
            predicted_reasoning_review=PredictedReasoningReview(),
        )


def test_a_not_gradeable_ground_cannot_stand_beside_a_grade() -> None:
    with pytest.raises(ValidationError, match="cannot stand beside a grade"):
        _evaluation(
            predicted_reasoning_quality=0.5,
            predicted_reasoning_review=PredictedReasoningReview(
                central_claims=_CLAIMS, not_gradeable="record silent"
            ),
        )


def test_a_null_grade_beside_a_review_must_state_the_records_ground() -> None:
    with pytest.raises(ValidationError, match="not_gradeable"):
        _evaluation(predicted_reasoning_review=PredictedReasoningReview(central_claims=_CLAIMS))
    evaluation = _evaluation(
        predicted_reasoning_review=PredictedReasoningReview(
            not_gradeable="The staged record carries no order for the event."
        )
    )
    assert evaluation.predicted_reasoning_quality is None


@pytest.mark.parametrize("grade", [-0.1, 1.1])
def test_the_grade_is_bounded_to_the_unit_interval(grade: float) -> None:
    with pytest.raises(ValidationError):
        _evaluation(
            predicted_reasoning_quality=grade,
            predicted_reasoning_review=PredictedReasoningReview(central_claims=_CLAIMS),
        )


def test_at_most_five_central_claims() -> None:
    with pytest.raises(ValidationError):
        PredictedReasoningReview(central_claims=_CLAIMS * 2)


def test_a_central_claims_status_is_closed() -> None:
    with pytest.raises(ValidationError):
        CentralClaim.model_validate({"claim": "x", "status": "partly"})


def test_a_null_grade_may_list_the_claims_the_record_could_not_settle() -> None:
    evaluation = _evaluation(
        predicted_reasoning_review=PredictedReasoningReview(
            central_claims=[CentralClaim(claim="The Court grants.", status="unresolved")],
            not_gradeable="The staged record carries no order for the event.",
        )
    )
    assert evaluation.predicted_reasoning_quality is None


def test_no_committed_evaluation_carries_the_grade_before_registration(tmp_path: Path) -> None:
    """The pilot grades off the ledger; a committed grade is one no protocol covers yet."""
    data_root = tmp_path / "data"
    ep = CasePaths(data_root, "scotus", 1).event("evt-petition-disposition")
    path = ep.evaluation("e", "p", "r")
    write_json(path, _evaluation())
    check = check_predicted_reasoning_grade_held(data_root)
    assert check.name == CHECK_PREDICTED_REASONING_HELD
    assert check.passed and check.checked == 1

    write_json(
        path,
        _evaluation(
            predicted_reasoning_quality=0.5,
            predicted_reasoning_review=PredictedReasoningReview(central_claims=_CLAIMS),
        ),
    )
    check = check_predicted_reasoning_grade_held(data_root)
    assert not check.passed
    assert any("no registered protocol" in p for p in check.problems)
    assert check_predicted_reasoning_grade_held(data_root, registered=True).passed
