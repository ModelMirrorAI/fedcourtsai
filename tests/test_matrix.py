from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pytest

from fedcourtsai.blinding import assign_aliases
from fedcourtsai.matrix import (
    CaseRequest,
    cap_predict_cells,
    cell_failure_count,
    evaluate_matrix,
    event_has_evaluations,
    event_has_predictions,
    fanout_order,
    last_predicted_dates,
    merits_event_case_ids,
    parse_cases,
    predict_matrix,
    predicted_case_ids,
)
from fedcourtsai.paths import CasePaths
from fedcourtsai.registry import enabled_evaluators, enabled_predictors
from fedcourtsai.schemas import CellFailure, Disposition, Prediction
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
        "claude-code": "claude-fable-5-1",
        "codex": "gpt-6-astra",
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


def _seed_event_definition(data_root: Path, court: str, docket: int, event_id: str) -> None:
    """Commit the bare fact that this event exists — its `event.yaml`.

    The ledger walk keys on the definition file's presence, never its contents,
    so the fixture writes a placeholder: a test that wrote a full record would
    be asserting something the function does not read.
    """
    event = CasePaths(data_root, court, docket).event(event_id)
    event.base.mkdir(parents=True)
    event.event_file.write_text("# placeholder\n", encoding="utf-8")


def test_merits_event_case_ids_takes_the_declared_merits_moments(tmp_path: Path) -> None:
    """The enrichment walk's priority read: the cases whose merits forecast is
    already committed, recognized through the moment table rather than a listed
    id — and anchored on the definition file, so a directory holding only cell
    output is not an event."""
    data_root = tmp_path / "data"
    assert merits_event_case_ids(data_root) == frozenset()  # no ledger prioritizes nothing

    _seed_event_definition(data_root, "scotus", 1, "evt-order-judgment")
    _seed_event_definition(data_root, "scotus", 2, "evt-brief-judgment")
    # Both merits moments on one case fold to the one case id.
    _seed_event_definition(data_root, "scotus", 1, "evt-brief-judgment")
    # A cert moment is not a merits one, however committed.
    _seed_event_definition(data_root, "scotus", 3, "evt-petition-disposition")
    # An interim moment is not either.
    _seed_event_definition(data_root, "scotus", 4, "evt-motion-disposition")
    # An event id the moment table does not declare at all.
    _seed_event_definition(data_root, "scotus", 5, "evt-order-something-else")
    # A directory with cell output but no definition is not an event.
    CasePaths(data_root, "scotus", 6).event("evt-order-judgment").predictions_dir.mkdir(
        parents=True
    )

    assert merits_event_case_ids(data_root) == frozenset({"scotus/1", "scotus/2"})


def test_predicted_case_ids_folds_every_committed_prediction_to_its_case(tmp_path: Path) -> None:
    """The sweep's candidate-admission read: one glob over the whole ledger,
    folded to `court/docket`, deduplicated across events, engines and runs — and
    depth-anchored on the filename, so the per-run siblings cannot fabricate a
    case."""
    data_root = tmp_path / "data"
    assert predicted_case_ids(data_root) == frozenset()  # no ledger admits nothing

    seed_prediction(data_root, "scotus", 1, "evt-a", predictor_id="claude-baseline")
    seed_prediction(data_root, "scotus", 1, "evt-a", predictor_id="codex-baseline")
    seed_prediction(data_root, "scotus", 1, "evt-b", predictor_id="claude-baseline")
    seed_prediction(data_root, "ca9", 7, "evt-a", predictor_id="claude-baseline")
    # A case with an event directory but no committed prediction: not a member.
    CasePaths(data_root, "scotus", 2).event("evt-a").predictions_dir.mkdir(parents=True)
    # A per-run sibling one level shallower must not count as a prediction.
    write_json(
        CasePaths(data_root, "scotus", 3).event("evt-a").prediction_attempt("codex-baseline", "R"),
        CellFailure(
            seam="predict",
            actor="codex-baseline",
            court="scotus",
            docket=3,
            event_id="evt-a",
            run_id="R",
            error_class="no_output",
        ),
    )

    assert predicted_case_ids(data_root) == frozenset({"scotus/1", "ca9/7"})


def test_last_predicted_dates_takes_the_newest_run_per_case(tmp_path: Path) -> None:
    """The date half of the same read: per case, the newest run that landed one.

    The relist cooldown and the text-coverage denominator both need *when* a
    case was last minted, not merely whether it ever was — only the pull/live
    lane stamps `predict_queued_at`, so for a schedule-derived mint the run
    directory is the only record of the date.
    """
    data_root = tmp_path / "data"
    assert last_predicted_dates(data_root) == {}  # no ledger dates nothing

    seed_prediction(data_root, "scotus", 1, "evt-a", run_id="20260101T000000Z")
    # A later run on another event of the same case wins the fold.
    seed_prediction(
        data_root, "scotus", 1, "evt-b", predictor_id="codex-baseline", run_id="20260615T120000Z"
    )
    seed_prediction(data_root, "ca9", 7, "evt-a", run_id="20260302T090000Z")
    # A run directory that is not a run id is a stray, not a crash: the callers
    # compare dates and must not be taken down by one.
    write_json(
        CasePaths(data_root, "scotus", 9).event("evt-a").prediction("claude-baseline", "not-a-run"),
        Prediction(
            case_id="scotus/9",
            event_id="evt-a",
            predictor_id="claude-baseline",
            engine="claude-code",
            model="claude-fable-5",
            run_id="not-a-run",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=0.05,
            predicted_disposition=Disposition.denied,
        ),
    )

    assert last_predicted_dates(data_root) == {
        "scotus/1": date(2026, 6, 15),
        "ca9/7": date(2026, 3, 2),
    }
    # Membership and dates come off the same glob, so the stray is absent from
    # the dates while still being a member.
    assert "scotus/9" in predicted_case_ids(data_root)


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
    """Without this, re-queueing pays a full evaluate cell per judge for
    gradings the ledger already holds — the boards collapse the re-runs, so the
    duplicate spend buys nothing the standings would show."""
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


# --- fan-out order -------------------------------------------------------------
#
# GitHub starts a matrix's `include` entries in list order under max-parallel, so
# list position is start time. These pin that no engine is systematically early
# or late, and that order is the only thing the layout decides. Every input is
# fixed, so none of these can flake: the SE-based tolerances bound how badly a
# biased key could still pass, not run-to-run noise — never widen them for that.

_BALANCE_CASES = 600
_MatrixBuilder = Callable[[Path, list[CaseRequest], str], dict[str, list[dict[str, Any]]]]


def _synthetic_cases(n: int) -> list[CaseRequest]:
    return [CaseRequest("scotus", 25_000 + d, ("evt-petition-cert",)) for d in range(n)]


def _positions(include: list[dict[str, Any]], actor_key: str) -> dict[str, list[int]]:
    """Each actor's 0-based position within its (case, event) group of cells."""
    groups: dict[tuple[str, int, str], list[str]] = {}
    for cell in include:
        group = (cell["court"], cell["docket"], cell["event_id"])
        groups.setdefault(group, []).append(cell[actor_key])
    positions: dict[str, list[int]] = {}
    for actors in groups.values():
        for i, actor in enumerate(actors):
            positions.setdefault(actor, []).append(i)
    return positions


@pytest.mark.parametrize(
    ("builder", "registry", "actor_key"),
    [
        (predict_matrix, PREDICTORS, "predictor_id"),
        (evaluate_matrix, EVALUATORS, "evaluator_id"),
    ],
)
def test_fanout_balances_every_engines_position(
    builder: _MatrixBuilder, registry: Path, actor_key: str
) -> None:
    # Over many cases each engine's mean slot within its case sits at the centre
    # (1.0 for three engines; per-cell sd ~0.82, so the SE over 600 cases is
    # ~0.03 and 0.1 is >3 SE), and none takes the first or the last slot in much
    # more than its 1/n share (SE ~0.02, so +0.06 is ~3 SE).
    include = builder(registry, _synthetic_cases(_BALANCE_CASES), "20261006T120000Z")["include"]
    positions = _positions(include, actor_key)
    n = len(positions)
    assert n == 3
    centre = (n - 1) / 2
    for actor, slots in positions.items():
        assert len(slots) == _BALANCE_CASES
        assert abs(sum(slots) / len(slots) - centre) < 0.1, actor
        first_share = sum(1 for s in slots if s == 0) / len(slots)
        assert first_share < 1 / n + 0.06, actor
        last_share = sum(1 for s in slots if s == n - 1) / len(slots)
        assert last_share < 1 / n + 0.06, actor


@pytest.mark.parametrize(
    ("builder", "registry", "actor_key"),
    [
        (predict_matrix, PREDICTORS, "predictor_id"),
        (evaluate_matrix, EVALUATORS, "evaluator_id"),
    ],
)
def test_fanout_balances_pairwise_precedence(
    builder: _MatrixBuilder, registry: Path, actor_key: str
) -> None:
    # A plain rotation of the registry order would still put claude ahead of
    # codex in two cases of three; the keyed shuffle balances every pair
    # (SE ~0.02 over 600 cases, so 0.07 is >3 SE).
    include = builder(registry, _synthetic_cases(_BALANCE_CASES), "RID")["include"]
    pos = _positions(include, actor_key)
    actors = sorted(pos)
    for i, a in enumerate(actors):
        for b in actors[i + 1 :]:
            ahead = sum(1 for x, y in zip(pos[a], pos[b], strict=True) if x < y)
            assert abs(ahead / _BALANCE_CASES - 0.5) < 0.07, (a, b)


def test_fanout_order_is_keyed_per_event_not_only_per_case() -> None:
    # The key carries the event, so a two-event case does not hand the same
    # engine the first slot on both events: the two orders agree only at the
    # 1-in-3! chance rate (SE ~0.015 over 600 cases, so +0.06 is ~4 SE).
    two_events = ("evt-petition-a", "evt-petition-b")
    cases = [CaseRequest("scotus", 26_000 + d, two_events) for d in range(_BALANCE_CASES)]
    include = predict_matrix(PREDICTORS, cases, "RID")["include"]
    orders: dict[tuple[int, str], list[str]] = {}
    for cell in include:
        orders.setdefault((cell["docket"], cell["event_id"]), []).append(cell["predictor_id"])
    same = sum(
        1
        for d in range(_BALANCE_CASES)
        if orders[(26_000 + d, two_events[0])] == orders[(26_000 + d, two_events[1])]
    )
    assert same / _BALANCE_CASES < 1 / 6 + 0.06


def test_fanout_is_case_major_in_request_order() -> None:
    # A case's cells sit together, cases in the order requested, so a large run
    # interleaves engines across its whole start window.
    cases = [
        CaseRequest("scotus", 30, ("evt-petition-a",)),
        CaseRequest("scotus", 10, ("evt-petition-b", "evt-petition-c")),
        CaseRequest("scotus", 20, ("evt-petition-d",)),
    ]
    include = predict_matrix(PREDICTORS, cases, "RID")["include"]
    groups = [(30, "evt-petition-a"), (10, "evt-petition-b"), (10, "evt-petition-c")]
    groups.append((20, "evt-petition-d"))
    assert [(c["docket"], c["event_id"]) for c in include] == [g for g in groups for _ in range(3)]


def test_fanout_order_is_deterministic_and_keyed_on_the_run() -> None:
    cases = _synthetic_cases(50)
    first = predict_matrix(PREDICTORS, cases, "20261006T120000Z")["include"]
    # A re-plan under the same run id reproduces the order exactly.
    assert predict_matrix(PREDICTORS, cases, "20261006T120000Z")["include"] == first
    other = predict_matrix(PREDICTORS, cases, "20261007T120000Z")["include"]
    assert [c["predictor_id"] for c in first] != [c["predictor_id"] for c in other]
    # The run id moves order, never membership.
    assert sorted(map(_cell_identity, first)) == sorted(map(_cell_identity, other))


def _cell_identity(cell: dict[str, Any]) -> tuple[str, str, int, str]:
    return (cell["predictor_id"], cell["court"], cell["docket"], cell["event_id"])


def test_fanout_order_does_not_track_the_blinding_shuffle() -> None:
    # The fan-out key is domain-separated from `assign_aliases`, which hashes the
    # same (run, case, event) joined with each predictor id: without the prefix,
    # the predict fan-out order under a run would equal the alias order those
    # predictors get under the same run, case and event in every trial.
    predictors = enabled_predictors(PREDICTORS)
    ids = [p.id for p in predictors]
    trials = 300
    agree = 0
    for d in range(trials):
        aliases = assign_aliases(ids, case_id=f"scotus/{d}", event_id="evt-x", run_id="RID")
        fan = fanout_order(predictors, run_id="RID", case=f"scotus/{d}", event_id="evt-x")
        agree += list(aliases.values()) == [p.id for p in fan]
    # Independent streams agree on 1 permutation in 3! = 6 (SE ~6.5 over 300).
    assert agree < trials / 6 + 25


def _registry_major(include: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The same cells laid out predictor-major, a layout the cap must not care about."""
    rank = {p.id: i for i, p in enumerate(enabled_predictors(PREDICTORS))}
    first_seen: dict[int, int] = {}
    for i, cell in enumerate(include):
        first_seen.setdefault(cell["docket"], i)
    return sorted(include, key=lambda c: (rank[c["predictor_id"]], first_seen[c["docket"]]))


@pytest.mark.parametrize("max_cells", [1, 3, 7, 10, 20, 31, 45, 200])
def test_cap_admits_the_same_cases_whatever_the_fanout_order(max_cells: int) -> None:
    # Uneven per-case cell counts (two-event cases, a narrowed backfill case), so
    # whole-case admission is exercised at boundaries that are not multiples of 3.
    events = ("evt-petition-a", "evt-petition-b")
    cases = [CaseRequest("scotus", 24_000 + d, events[: 1 + d % 2]) for d in range(12)]
    cases.append(CaseRequest("scotus", 23_999, events[:1], predictors=("codex-baseline",)))
    matrix = predict_matrix(PREDICTORS, cases, "RID")
    reordered = {"include": _registry_major(matrix["include"])}
    assert reordered["include"] != matrix["include"]
    new = cap_predict_cells(matrix, max_cells)
    old = cap_predict_cells(reordered, max_cells)
    assert sorted(new.include, key=_cell_identity) == sorted(old.include, key=_cell_identity)
    assert new.dropped_cases == old.dropped_cases
    assert new.dropped_cells == old.dropped_cells
