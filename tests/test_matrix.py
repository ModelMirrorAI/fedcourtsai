from pathlib import Path

import pytest

from fedcourtsai.matrix import (
    CaseRequest,
    evaluate_matrix,
    event_has_evaluations,
    parse_cases,
    predict_matrix,
)
from fedcourtsai.paths import CasePaths
from tests.conftest import seed_evaluation, seed_prediction

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
        "codex": "gpt-5.6-sol",
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


def test_parse_cases_reads_optional_predictors() -> None:
    body = """Backfill the failed engine.

```json
[
  {"court": "scotus", "docket": 1, "events": ["evt-a"], "predictors": ["codex-baseline"]},
  {"court": "scotus", "docket": 2, "events": ["evt-a"]}
]
```
"""
    assert parse_cases(body) == [
        CaseRequest("scotus", 1, ("evt-a",), ("codex-baseline",)),
        CaseRequest("scotus", 2, ("evt-a",)),
    ]


def test_predict_matrix_narrows_to_requested_predictors() -> None:
    cases = [
        CaseRequest("scotus", 1, ("evt-a",), predictors=("codex-baseline",)),
        CaseRequest("scotus", 2, ("evt-a",)),
    ]
    m = predict_matrix(PREDICTORS, cases, "RID")
    cells = {(row["docket"], row["predictor_id"]) for row in m["include"]}
    # Docket 1 mints only the requested engine's cell; docket 2 fans out fully.
    assert cells == {
        (1, "codex-baseline"),
        (2, "claude-baseline"),
        (2, "codex-baseline"),
        (2, "gemini-baseline"),
    }


def test_predict_matrix_rejects_unknown_predictor_ids() -> None:
    cases = [CaseRequest("scotus", 1, ("evt-a",), predictors=("codex-basline",))]
    with pytest.raises(ValueError, match="codex-basline"):
        predict_matrix(PREDICTORS, cases, "RID")


def test_parse_cases_requires_a_json_block() -> None:
    with pytest.raises(ValueError, match="No ```json"):
        parse_cases("No code block here.")


def test_parse_cases_rejects_entry_missing_keys() -> None:
    body = """```json
[{"court": "scotus"}]
```"""
    with pytest.raises(ValueError, match=r"court.*docket"):
        parse_cases(body)


def test_evaluate_matrix_drops_predictionless_events(tmp_path: Path) -> None:
    # The plan-time cost gate: an event with no committed prediction mints no
    # evaluator cells (nothing to score); one with a prediction fans out fully.
    seed_prediction(tmp_path / "data", "scotus", 1, "evt-petition-disposition")
    cases = [
        CaseRequest(court="scotus", docket=1, events=("evt-petition-disposition",)),
        CaseRequest(court="scotus", docket=2, events=("evt-petition-disposition",)),
    ]
    gated = evaluate_matrix(EVALUATORS, cases, "RID", data_root=tmp_path / "data")
    assert {(c["docket"]) for c in gated["include"]} == {1}
    # Without a ledger, the gate is off and both fan out (offline callers).
    ungated = evaluate_matrix(EVALUATORS, cases, "RID")
    assert {(c["docket"]) for c in ungated["include"]} == {1, 2}


def test_event_has_evaluations_ignores_the_shallow_per_run_siblings(tmp_path: Path) -> None:
    """An evaluate cell's usage/flags/tooling live one level *above* the
    per-predictor evaluation directories. A glob that matched them would report
    every cell as already-graded and silently mint nothing, ever."""
    data_root = tmp_path / "data"
    event = CasePaths(data_root, "scotus", 1).event("evt-petition-disposition")
    sibling = event.evaluation_usage("claude-judge", "20260101T000000Z")
    sibling.parent.mkdir(parents=True)
    sibling.write_text("{}")

    assert not event_has_evaluations(data_root, "scotus", 1, "evt-petition-disposition")
    seed_evaluation(data_root, "scotus", 1, "evt-petition-disposition")
    assert event_has_evaluations(data_root, "scotus", 1, "evt-petition-disposition")


def test_event_has_evaluations_can_ask_about_one_judge(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    seed_evaluation(data_root, "scotus", 1, "evt-x", evaluator_id="claude-judge")
    assert event_has_evaluations(data_root, "scotus", 1, "evt-x", evaluator_id="claude-judge")
    assert not event_has_evaluations(data_root, "scotus", 1, "evt-x", evaluator_id="codex-judge")
    # No evaluator named: any grading at all counts.
    assert event_has_evaluations(data_root, "scotus", 1, "evt-x")


def test_evaluate_matrix_mints_only_the_judges_that_have_not_graded(tmp_path: Path) -> None:
    """Cell granularity: a run where one judge landed and two did not should
    re-mint two cells, not three. This is what makes a re-queue safe."""
    data_root = tmp_path / "data"
    seed_prediction(data_root, "scotus", 1, "evt-petition-disposition")
    seed_evaluation(data_root, "scotus", 1, "evt-petition-disposition", evaluator_id="claude-judge")
    cases = [CaseRequest(court="scotus", docket=1, events=("evt-petition-disposition",))]

    gated = evaluate_matrix(EVALUATORS, cases, "RID", data_root=data_root)
    minted = {c["evaluator_id"] for c in gated["include"]}
    assert "claude-judge" not in minted, "an already-graded judge must not be re-minted"
    assert minted, "the judges that have not graded still fan out"


def test_a_fully_graded_event_mints_nothing_so_a_requeue_is_a_no_op(tmp_path: Path) -> None:
    """Without this, re-queueing double-counts: the leaderboard reads every
    committed evaluation.json into a per-(predictor, case, event) list with no
    run dedup, so a second grading silently reweights the standings."""
    data_root = tmp_path / "data"
    seed_prediction(data_root, "scotus", 1, "evt-x")
    for evaluator in ("claude-judge", "codex-judge", "gemini-judge"):
        seed_evaluation(data_root, "scotus", 1, "evt-x", evaluator_id=evaluator)
    cases = [CaseRequest(court="scotus", docket=1, events=("evt-x",))]

    assert evaluate_matrix(EVALUATORS, cases, "RID", data_root=data_root)["include"] == []
    # --force is the deliberate re-grade path, so a rubric change never requires
    # deleting committed artifacts to get a cell minted.
    forced = evaluate_matrix(EVALUATORS, cases, "RID", data_root=data_root, skip_evaluated=False)
    assert len(forced["include"]) == 3
