from pathlib import Path

from fedcourtsai.matrix import evaluate_matrix, predict_matrix

PREDICTORS = Path("config/predictors.yaml")
EVALUATORS = Path("config/evaluators.yaml")


def test_predict_matrix_is_predictor_by_event_product() -> None:
    m = predict_matrix(PREDICTORS, "ca9", 123, ["evt-a", "evt-b"], "RID")
    inc = m["include"]
    # 2 enabled predictors x 2 events
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
    m = evaluate_matrix(EVALUATORS, "ca9", 123, ["evt-a"], "RID")
    inc = m["include"]
    assert len(inc) == 2
    assert {row["evaluator_id"] for row in inc} == {"claude-judge", "codex-judge"}
