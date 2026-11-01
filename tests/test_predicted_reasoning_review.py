"""The evaluator-authored grade of ``predicted_reasoning.md`` and the review behind it.

``Evaluation.predicted_reasoning_quality`` grades the forecast document alone
(``docs/outcome-decomposition.md``, *Grading the forecast document, design*).
The schema holds the grade to its audit trail: a grade stands on the central
claims it rests on, and a null grade beside a review states the record's
ground for it.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from fedcourtsai.paths import CasePaths
from fedcourtsai.process_version import EVALUATE_BLESSING_LABELS
from fedcourtsai.schemas import (
    CentralClaim,
    CorpusCheck,
    Engine,
    Evaluation,
    PredictedReasoningReview,
    ProcessVersion,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.validate import (
    CHECK_PREDICTED_REASONING_REGISTERED,
    PREDICTED_REASONING_GRADE_FROM,
    asks_predicted_reasoning_grade,
    check_predicted_reasoning_grade_registered,
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


_OLD_JUDGE = "sha256:" + "a" * 64
_NEW_JUDGE = "sha256:" + "b" * 64
_LABELS = {_OLD_JUDGE: ("proc-v14", "proc-v15"), _NEW_JUDGE: ("proc-v16",)}


def _stamp(digest: str) -> ProcessVersion:
    return ProcessVersion(
        label="proc-v16", digest=digest, stamped_at=datetime(2026, 11, 1, tzinfo=UTC)
    )


def _graded(**fields: Any) -> Evaluation:
    return _evaluation(
        predicted_reasoning_quality=0.5,
        predicted_reasoning_review=PredictedReasoningReview(central_claims=_CLAIMS),
        **fields,
    )


def _check_one(tmp_path: Path, evaluation: Evaluation) -> CorpusCheck:
    data_root = tmp_path / "data"
    path = (
        CasePaths(data_root, "scotus", 1)
        .event("evt-petition-disposition")
        .evaluation("e", "p", "r")
    )
    write_json(path, evaluation)
    return check_predicted_reasoning_grade_registered(data_root, blessing_labels=_LABELS)


def test_the_registering_label_is_proc_v16() -> None:
    assert PREDICTED_REASONING_GRADE_FROM == "proc-v16"


def test_a_grade_under_a_digest_blessed_at_the_registering_label_passes(tmp_path: Path) -> None:
    check = _check_one(tmp_path, _graded(process_version=_stamp(_NEW_JUDGE)))
    assert check.name == CHECK_PREDICTED_REASONING_REGISTERED
    assert check.passed and check.checked == 1


def test_a_grade_under_an_earlier_digest_is_refused(tmp_path: Path) -> None:
    """A proc-v15 judge's prompt never asked for the grade, so no protocol covers it."""
    check = _check_one(tmp_path, _graded(process_version=_stamp(_OLD_JUDGE)))
    assert not check.passed
    assert any("not blessed at proc-v16" in p for p in check.problems)


def test_a_grade_under_an_unregistered_digest_is_refused(tmp_path: Path) -> None:
    check = _check_one(tmp_path, _graded(process_version=_stamp("sha256:" + "c" * 64)))
    assert not check.passed


def test_an_unstamped_grade_is_refused(tmp_path: Path) -> None:
    """No stamp shows which prompt ran, so the conservative reading refuses it."""
    check = _check_one(tmp_path, _graded())
    assert not check.passed
    assert any("no process stamp" in p for p in check.problems)


def test_an_ungraded_evaluation_passes_under_any_stamp(tmp_path: Path) -> None:
    assert _check_one(tmp_path, _evaluation(process_version=_stamp(_OLD_JUDGE))).passed
    assert _check_one(tmp_path, _evaluation()).passed


def test_a_later_label_asks_too_and_the_live_registry_asks_at_proc_v16() -> None:
    assert asks_predicted_reasoning_grade(
        _OLD_JUDGE, blessing_labels={_OLD_JUDGE: ("proc-v15", "proc-v17")}
    )
    assert not asks_predicted_reasoning_grade(None, blessing_labels=_LABELS)
    live = [d for d, labels in EVALUATE_BLESSING_LABELS.items() if "proc-v16" in labels]
    assert len(live) == 3
    assert all(asks_predicted_reasoning_grade(d) for d in live)


def test_the_evaluate_prompt_asks_for_the_grade_and_the_pilot_note_does_not() -> None:
    """The rubric lives in the registered prompt once; the pilot note repeats none of it."""
    root = Path(__file__).resolve().parent.parent / ".github" / "prompts"
    prompt = (root / "evaluate.md").read_text()
    assert "**Grading the forecast document — every stage" in prompt
    for field in ("`predicted_reasoning_quality`", "`predicted_reasoning_review`"):
        assert field in prompt
    assert "Do not score the forecast document" not in prompt
    note = (root / "pilot" / "predicted-reasoning-quality.md").read_text()
    assert "| Grade | Anchor |" not in note
    assert "central_claims" not in note
