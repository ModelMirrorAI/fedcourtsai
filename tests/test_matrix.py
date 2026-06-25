from pathlib import Path

import pytest

from fedcourtsai.matrix import (
    CaseRequest,
    evaluate_matrix,
    parse_cases,
    predict_matrix,
)

PREDICTORS = Path("config/predictors.yaml")
EVALUATORS = Path("config/evaluators.yaml")


def test_predict_matrix_is_predictor_by_event_product() -> None:
    cases = [CaseRequest("ca9", 123, ("evt-a", "evt-b"))]
    m = predict_matrix(PREDICTORS, cases, "RID")
    inc = m["include"]
    # 2 enabled predictors x 1 case x 2 events
    assert len(inc) == 4
    engines = {row["engine"] for row in inc}
    assert engines == {"claude-code", "codex"}
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
    assert len(inc) == 2
    assert {row["evaluator_id"] for row in inc} == {"claude-judge", "codex-judge"}


def test_predict_matrix_fans_out_across_many_cases() -> None:
    cases = [
        CaseRequest("scotus", 1, ("evt-petition-a",)),
        CaseRequest("scotus", 2, ("evt-petition-b", "evt-petition-c")),
    ]
    m = predict_matrix(PREDICTORS, cases, "RID")
    inc = m["include"]
    # 2 predictors x (1 + 2) events across two cases
    assert len(inc) == 6
    cells = {(row["court"], row["docket"], row["event_id"]) for row in inc}
    assert cells == {
        ("scotus", 1, "evt-petition-a"),
        ("scotus", 2, "evt-petition-b"),
        ("scotus", 2, "evt-petition-c"),
    }


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
