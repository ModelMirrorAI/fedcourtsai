from pathlib import Path

import pytest

from fedcourtsai.matrix import (
    CaseRequest,
    evaluate_matrix,
    parse_cases,
    predict_matrix,
    reconcile_matrix,
)

PREDICTORS = Path("config/predictors.yaml")
EVALUATORS = Path("config/evaluators.yaml")


def test_predict_matrix_is_predictor_by_event_product() -> None:
    cases = [CaseRequest("ca9", 123, ("evt-a", "evt-b"))]
    m = predict_matrix(PREDICTORS, cases, "RID")
    inc = m["include"]
    # 3 enabled predictors x 1 case x 2 events
    assert len(inc) == 6
    engines = {row["engine"] for row in inc}
    assert engines == {"claude-code", "codex", "gemini"}
    # Registry `model: null` resolves to the engine's predict/evaluate default —
    # never empty, so the workflow passes it straight to the engine step and the
    # recorded model is what actually ran.
    assert {row["engine"]: row["model"] for row in inc} == {
        "claude-code": "claude-fable-5",
        "codex": "gpt-5.5",
        "gemini": "gemini-3.1-pro-preview",
    }
    row = inc[0]
    assert row["court"] == "ca9"
    assert row["docket"] == 123
    assert row["run_id"] == "RID"
    assert set(row) == {
        "predictor_id",
        "engine",
        "model",
        "prompt",
        "court",
        "docket",
        "event_id",
        "run_id",
    }


def test_evaluate_matrix_is_evaluator_by_event_product() -> None:
    cases = [CaseRequest("ca9", 123, ("evt-a",))]
    m = evaluate_matrix(EVALUATORS, cases, "RID")
    inc = m["include"]
    assert len(inc) == 3
    assert {row["evaluator_id"] for row in inc} == {
        "claude-judge",
        "codex-judge",
        "gemini-judge",
    }
    assert all(row["model"] for row in inc)  # resolved, never empty


def test_predict_matrix_fans_out_across_many_cases() -> None:
    cases = [
        CaseRequest("scotus", 1, ("evt-petition-a",)),
        CaseRequest("scotus", 2, ("evt-petition-b", "evt-petition-c")),
    ]
    m = predict_matrix(PREDICTORS, cases, "RID")
    inc = m["include"]
    # 3 predictors x (1 + 2) events across two cases
    assert len(inc) == 9
    cells = {(row["court"], row["docket"], row["event_id"]) for row in inc}
    assert cells == {
        ("scotus", 1, "evt-petition-a"),
        ("scotus", 2, "evt-petition-b"),
        ("scotus", 2, "evt-petition-c"),
    }


def test_reconcile_matrix_is_one_cell_per_case() -> None:
    cases = [
        CaseRequest("ca9", 123, ("evt-a", "evt-b")),
        CaseRequest("scotus", 1, ("evt-petition",)),
    ]
    m = reconcile_matrix(cases, "RID")
    inc = m["include"]
    # One cell per case (not per event); both events ride in one space-joined field.
    assert len(inc) == 2
    first = inc[0]
    assert first == {
        "engine": "claude-code",
        "prompt": ".github/prompts/reconcile.md",
        "court": "ca9",
        "docket": 123,
        "events": "evt-a evt-b",
        "run_id": "RID",
    }
    assert inc[1]["court"] == "scotus"
    assert inc[1]["events"] == "evt-petition"


def test_reconcile_matrix_skips_cases_with_no_open_events() -> None:
    cases = [
        CaseRequest("ca9", 123, ()),
        CaseRequest("ca9", 456, ("evt-a",)),
    ]
    m = reconcile_matrix(cases, "RID")
    inc = m["include"]
    assert len(inc) == 1
    assert inc[0]["docket"] == 456


def test_parse_cases_accepts_single_object() -> None:
    body = """Predict this.

```json
{"court": "ca9", "docket": 64512345, "events": ["evt-motion-stay"]}
```
"""
    assert parse_cases(body) == [CaseRequest("ca9", 64512345, ("evt-motion-stay",))]


def test_parse_cases_accepts_list_of_objects() -> None:
    body = """Predict the long conference.

```json
[
  {"court": "scotus", "docket": 1, "events": ["evt-petition-a"]},
  {"court": "scotus", "docket": 2, "events": []},
  {"court": "scotus", "docket": 3}
]
```
"""
    assert parse_cases(body) == [
        CaseRequest("scotus", 1, ("evt-petition-a",)),
        CaseRequest("scotus", 2, ()),
        CaseRequest("scotus", 3, ()),
    ]


def test_parse_cases_requires_a_json_block() -> None:
    with pytest.raises(ValueError, match="No ```json"):
        parse_cases("No code block here.")


def test_parse_cases_rejects_entry_missing_keys() -> None:
    body = """```json
[{"court": "scotus"}]
```"""
    with pytest.raises(ValueError, match=r"court.*docket"):
        parse_cases(body)
