"""The trial slice's two prompt templates against the contract code declares."""

from __future__ import annotations

import re
from pathlib import Path
from typing import get_args

import pytest

from fedcourtsai.pipeline import claims, moments
from fedcourtsai.schemas import (
    Moment,
    TrialJudgmentLabel,
    TrialLeaveLabel,
    TrialRulingLabel,
)
from tests.test_cell_instructions import _PROMPT_PATH, _names_instruction_file

REPO_ROOT = Path(__file__).resolve().parents[1]
PREDICT = ".github/prompts/predict-trial.md"
EVALUATE = ".github/prompts/evaluate-trial.md"
TRIAL_MOMENTS = [m for m in Moment if m.value.startswith("trial-")]

pytestmark = pytest.mark.reads_docs


def _text(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


@pytest.mark.parametrize("prompt", [PREDICT, EVALUATE])
def test_a_trial_prompt_is_a_cells_whole_contract(prompt: str) -> None:
    text = _text(prompt)
    assert _names_instruction_file(text) == []
    assert sorted(set(_PROMPT_PATH.findall(text)) - {prompt}) == []
    assert "This prompt is your whole contract" in text


def test_the_trial_moments_are_the_five_the_prompts_name() -> None:
    assert len(TRIAL_MOMENTS) == 5
    for moment in TRIAL_MOMENTS:
        assert moments.trial_spec(moment) is not None
        for prompt in (PREDICT, EVALUATE):
            assert f"`{moment.value}`" in _text(prompt), (prompt, moment.value)


@pytest.mark.parametrize("labels", [TrialRulingLabel, TrialLeaveLabel, TrialJudgmentLabel], ids=str)
def test_both_prompts_name_every_outcome_label_as_written(labels: object) -> None:
    for label in get_args(labels):
        for prompt in (PREDICT, EVALUATE):
            assert f"`{label}`" in _text(prompt), (prompt, label)


def test_the_predict_prompt_names_every_declared_claim_and_no_other_trial_claim() -> None:
    text = _text(PREDICT)
    declared = {
        claims.CLAIM_TRIAL_RULING_GRANTED,
        claims.CLAIM_TRIAL_JUDGMENT_FOR_PLAINTIFF,
        claims.CLAIM_TRIAL_RULING,
        claims.CLAIM_TRIAL_LEAVE,
        claims.CLAIM_TRIAL_JUDGMENT,
    }
    # `trial-judgment` names a moment and its distribution claim alike.
    named = set(re.findall(r"`(trial-[a-z-]+)`", text))
    assert named == declared | {m.value for m in TRIAL_MOMENTS}
    owed: set[str] = set()
    for moment in TRIAL_MOMENTS:
        entry = 45 if moments.trial_spec(moment).per_motion else None
        event = moments.trial_event_id(moment, entry)
        declared_set = claims.declared_claim_set(event)
        assert declared_set is not None
        owed |= set(declared_set[1]) | set(claims.declared_distribution_claims(event))
    assert owed == declared


def test_the_predict_prompts_worked_example_is_a_consistent_block() -> None:
    text = _text(PREDICT)
    found = re.search(
        r"`granted` (0\.\d+), `granted-in-part` (0\.\d+), `denied` (0\.\d+), "
        r"`withdrawn` (0\.\d+),\s+`mooted` (0\.\d+); `probability` and "
        r"`trial-ruling-granted` are both (0\.\d+)",
        text,
    )
    assert found is not None
    granted, part, denied, withdrawn, mooted, headline = map(float, found.groups())
    assert granted + part + denied + withdrawn + mooted == pytest.approx(1.0)
    assert granted + part == pytest.approx(headline)


def test_the_evaluate_prompt_leaves_the_harness_its_fields() -> None:
    text = _text(EVALUATE)
    for field in ("segment_base_rate", "brier_skill_score", "base_rate_basis", "claim_scores"):
        assert f"`{field}`" in text
    assert "(probability - actual_granted)**2" in text
