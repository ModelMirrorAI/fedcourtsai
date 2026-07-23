from pathlib import Path

import pytest

from fedcourtsai.matrix import (
    CaseRequest,
    cap_predict_cells,
    cell_failure_count,
    evaluate_matrix,
    event_has_evaluations,
    event_has_predictions,
    parse_cases,
    predict_matrix,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.registry import enabled_evaluators, enabled_predictors
from fedcourtsai.schemas import CellFailure
from fedcourtsai.serialize import write_json
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


def _oversized_matrix(n_cases: int) -> dict[str, list[dict[str, object]]]:
    """A predict matrix over ``n_cases`` single-event SCOTUS dockets (3 cells each)."""
    cases = [CaseRequest("scotus", d, ("evt-petition-cert",)) for d in range(1, n_cases + 1)]
    return predict_matrix(PREDICTORS, cases, "RID")


def test_cap_predict_cells_under_the_cap_passes_through_unchanged() -> None:
    # The common path: a normal run is well under the backstop, so the matrix is
    # returned byte-for-byte with nothing deferred.
    matrix = _oversized_matrix(5)  # 15 cells
    capped = cap_predict_cells(matrix, 240)
    assert capped.include == matrix["include"]
    assert capped.dropped_cells == 0
    assert capped.dropped_cases == ()


def test_cap_predict_cells_keeps_a_matrix_that_exactly_equals_the_cap() -> None:
    # The `<=` boundary: 5 cases x 3 engines = 15 cells against a 15-cell cap is
    # kept in full — the cap defers only what is strictly over it.
    matrix = _oversized_matrix(5)
    assert len(matrix["include"]) == 15
    capped = cap_predict_cells(matrix, 15)
    assert capped.include == matrix["include"]
    assert capped.dropped_cells == 0
    assert capped.dropped_cases == ()


def test_cap_predict_cells_defers_whole_overflow_cases() -> None:
    # 5 cases x 3 engines = 15 cells; a 9-cell cap keeps exactly the three
    # lowest-case_id cases whole and defers the rest.
    matrix = _oversized_matrix(5)
    capped = cap_predict_cells(matrix, 9)
    assert len(capped.include) == 9
    kept_cases = {(c["court"], c["docket"]) for c in capped.include}
    assert kept_cases == {("scotus", 1), ("scotus", 2), ("scotus", 3)}
    # Every kept case is present WHOLE — all three of its engines, none split off.
    assert all(sum(1 for c in capped.include if c["docket"] == d) == 3 for d in (1, 2, 3))
    assert capped.dropped_cells == 6
    assert capped.dropped_cases == ("scotus/4", "scotus/5")


def test_cap_predict_cells_rounds_down_to_the_case_boundary() -> None:
    # A cap that falls mid-case (10, between the 9th and 12th cell) must not slice
    # a case to hit it exactly: predict has no already-predicted skip, so a
    # half-admitted case would double-commit its landed engines on re-queue. It
    # keeps the whole-case prefix (9) instead.
    capped = cap_predict_cells(_oversized_matrix(5), 10)
    assert len(capped.include) == 9
    assert capped.dropped_cells == 6


def test_cap_predict_cells_defers_without_destroying_or_mutating() -> None:
    # Non-destructive: the deferred cases are exactly the ones not kept — none
    # invented, none lost — and the input matrix is left untouched, so the
    # overflow is queueable on a later cycle rather than deleted.
    matrix = _oversized_matrix(5)
    original = [dict(c) for c in matrix["include"]]
    capped = cap_predict_cells(matrix, 9)
    kept_cases = {f"scotus/{c['docket']}" for c in capped.include}
    all_cases = {f"scotus/{d}" for d in range(1, 6)}
    assert kept_cases | set(capped.dropped_cases) == all_cases
    assert kept_cases.isdisjoint(capped.dropped_cases)
    assert matrix["include"] == original  # the cap read the matrix, it did not edit it


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


def test_event_has_predictions_can_ask_about_one_predictor(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    seed_prediction(data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    assert event_has_predictions(data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    assert not event_has_predictions(data_root, "scotus", 1, "evt-x", predictor_id="codex-baseline")
    # No predictor named: any prediction at all counts (the original semantics).
    assert event_has_predictions(data_root, "scotus", 1, "evt-x")


def test_predict_matrix_mints_only_the_engines_that_have_not_predicted(tmp_path: Path) -> None:
    """Cell granularity: a run where two of three engines landed and one
    quota-failed should re-mint only the third. This is what makes a partial
    predict re-queue idempotent, the mirror of the evaluate already-graded gate."""
    data_root = tmp_path / "data"
    seed_prediction(
        data_root, "scotus", 1, "evt-petition-disposition", predictor_id="claude-baseline"
    )
    seed_prediction(
        data_root, "scotus", 1, "evt-petition-disposition", predictor_id="codex-baseline"
    )
    cases = [CaseRequest(court="scotus", docket=1, events=("evt-petition-disposition",))]

    gated = predict_matrix(PREDICTORS, cases, "RID", data_root=data_root)
    minted = {c["predictor_id"] for c in gated["include"]}
    unpredicted = {p.id for p in enabled_predictors(PREDICTORS)} - {
        "claude-baseline",
        "codex-baseline",
    }
    assert minted == unpredicted, "exactly the engines that have not predicted, and no others"
    # Without a ledger the gate is off and every enabled engine fans out (offline
    # callers, back-compat with a caller that assembles its own ledger).
    ungated = predict_matrix(PREDICTORS, cases, "RID")
    assert {c["predictor_id"] for c in ungated["include"]} == {
        p.id for p in enabled_predictors(PREDICTORS)
    }
    # skip_predicted=False is the deliberate re-predict path (a prompt change),
    # so it never requires deleting committed artifacts to get a cell minted.
    forced = predict_matrix(PREDICTORS, cases, "RID", data_root=data_root, skip_predicted=False)
    assert {c["predictor_id"] for c in forced["include"]} == {
        p.id for p in enabled_predictors(PREDICTORS)
    }


def test_a_fully_predicted_event_mints_nothing(tmp_path: Path) -> None:
    # Every enabled engine has predicted: a re-queue mints nothing (the whole-case
    # volume cap can then treat the empty case as cleanly deferred).
    data_root = tmp_path / "data"
    predictors = enabled_predictors(PREDICTORS)
    for predictor in predictors:
        seed_prediction(data_root, "scotus", 1, "evt-x", predictor_id=predictor.id)
    cases = [CaseRequest(court="scotus", docket=1, events=("evt-x",))]
    assert predict_matrix(PREDICTORS, cases, "RID", data_root=data_root)["include"] == []


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
    ungraded = {e.id for e in enabled_evaluators(EVALUATORS)} - {"claude-judge"}
    assert minted == ungraded, "exactly the judges that have not graded, and no others"


def test_a_fully_graded_event_mints_nothing_so_a_requeue_is_a_no_op(tmp_path: Path) -> None:
    """Without this, re-queueing double-counts: the leaderboard reads every
    committed evaluation.json into a per-(predictor, case, event) list with no
    run dedup, so a second grading silently reweights the standings."""
    data_root = tmp_path / "data"
    evaluators = enabled_evaluators(EVALUATORS)
    seed_prediction(data_root, "scotus", 1, "evt-x")
    for evaluator in evaluators:
        seed_evaluation(data_root, "scotus", 1, "evt-x", evaluator_id=evaluator.id)
    cases = [CaseRequest(court="scotus", docket=1, events=("evt-x",))]

    assert evaluate_matrix(EVALUATORS, cases, "RID", data_root=data_root)["include"] == []
    # --force is the deliberate re-grade path, so a rubric change never requires
    # deleting committed artifacts to get a cell minted.
    forced = evaluate_matrix(EVALUATORS, cases, "RID", data_root=data_root, skip_evaluated=False)
    assert len(forced["include"]) == len(evaluators)


def _write_failure(
    data_root: Path, court: str, docket: int, event_id: str, actor: str, seam: str, run_id: str
) -> None:
    events = CasePaths(data_root, court, docket).event(event_id)
    dest = (
        events.prediction_attempt(actor, run_id)
        if seam == "predict"
        else events.evaluation_attempt(actor, run_id)
    )
    write_json(
        dest,
        CellFailure(
            seam=seam,
            actor=actor,
            court=court,
            docket=docket,
            event_id=event_id,
            run_id=run_id,
            error_class="no_output",
        ),
    )


def test_cell_failure_count_counts_distinct_run_facts(tmp_path: Path) -> None:
    """Two distinct-run failure facts for one cell count as 2; a rerun writing the
    same run id overwrites rather than double-counting (run-scoped path)."""
    data_root = tmp_path / "data"
    event = "evt-petition-disposition"
    assert cell_failure_count(data_root, "scotus", 1, event, "gemini-baseline", "predict") == 0
    _write_failure(data_root, "scotus", 1, event, "gemini-baseline", "predict", "R1")
    _write_failure(data_root, "scotus", 1, event, "gemini-baseline", "predict", "R2")
    assert cell_failure_count(data_root, "scotus", 1, event, "gemini-baseline", "predict") == 2
    # A rerun of R1 overwrites its own fact — counting committed files can't dupe.
    _write_failure(data_root, "scotus", 1, event, "gemini-baseline", "predict", "R1")
    assert cell_failure_count(data_root, "scotus", 1, event, "gemini-baseline", "predict") == 2


def test_cell_failure_count_is_per_actor_event_and_seam(tmp_path: Path) -> None:
    """The count is keyed on (actor, event, seam): a fact for a sibling actor, a
    different event, or the other seam does not leak into a cell's tally."""
    data_root = tmp_path / "data"
    event = "evt-petition-disposition"
    _write_failure(data_root, "scotus", 1, event, "claude-judge", "evaluate", "R1")
    # Same event/run, other actor and the predict seam — must not be counted for
    # claude-judge's evaluate cell.
    _write_failure(data_root, "scotus", 1, event, "codex-judge", "evaluate", "R1")
    _write_failure(data_root, "scotus", 1, event, "claude-judge", "predict", "R1")
    _write_failure(data_root, "scotus", 1, "evt-other", "claude-judge", "evaluate", "R1")
    assert cell_failure_count(data_root, "scotus", 1, event, "claude-judge", "evaluate") == 1
