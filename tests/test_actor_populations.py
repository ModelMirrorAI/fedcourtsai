"""An actor's population, and the routing of a docket's cells to its own.

A predictor or an evaluator forecasts or grades one prediction population's
dockets. The fan-out sends a slice's docket to the slice's actors and every
other docket to the Court's, so registering a slice's actors mints no cell on
the Court's docket and moves none of the Court's rosters.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from fedcourtsai.matrix import CaseRequest, evaluate_matrix, predict_matrix
from fedcourtsai.prediction_slices import (
    SCOTUS_POPULATION_KEY,
    SLICES,
    Population,
    routing_population,
)
from fedcourtsai.registry import (
    enabled_evaluators,
    enabled_predictors,
    evaluators_for,
    load_predictors,
    predictors_for,
)

PREDICTORS = Path("config/predictors.yaml")
EVALUATORS = Path("config/evaluators.yaml")
SLICE = {"ai-watchlist": Population(key="ai-watchlist", case_ids=frozenset({"cand/77"}))}


def _with_slice_actor(tmp_path: Path, source: Path, section: str) -> Path:
    """The committed registry plus one actor of the slice's population."""
    data = yaml.safe_load(source.read_text())
    extra = dict(data[section][0], id="slice-actor", population="ai-watchlist")
    data[section].append(extra)
    path = tmp_path / source.name
    path.write_text(yaml.safe_dump(data))
    return path


def test_an_actor_is_the_courts_unless_it_names_a_slice() -> None:
    assert {p.population for p in enabled_predictors(PREDICTORS)} == {SCOTUS_POPULATION_KEY}
    assert {e.population for e in enabled_evaluators(EVALUATORS)} == {SCOTUS_POPULATION_KEY}


def test_an_actor_of_an_undeclared_population_is_refused_at_load(tmp_path: Path) -> None:
    data = yaml.safe_load(PREDICTORS.read_text())
    data["predictors"][0]["population"] = "ai-watchlsit"
    data["predictors"][0]["enabled"] = False
    path = tmp_path / "predictors.yaml"
    path.write_text(yaml.safe_dump(data))

    assert "ai-watchlsit" not in SLICES
    with pytest.raises(ValueError, match="names population"):
        load_predictors(path)


def test_the_plans_candidate_count_follows_the_routing(tmp_path: Path) -> None:
    from fedcourtsai.cli import _predict_ledger_gate  # noqa: PLC0415 - the cli is heavy to import

    predictors = _with_slice_actor(tmp_path, PREDICTORS, "predictors")
    cases = [CaseRequest("cand", 77, ("evt-a",)), CaseRequest("scotus", 1, ("evt-b", "evt-c"))]

    gate = _predict_ledger_gate(cases, predictors, tmp_path / "data", SLICE)
    cells = predict_matrix(predictors, cases, "RID", data_root=tmp_path / "data", slices=SLICE)

    assert gate.candidates == len(cells["include"]) == 1 + 2 * len(enabled_predictors(PREDICTORS))


def test_a_docket_no_slice_admits_is_routed_to_the_courts_actors() -> None:
    assert routing_population("scotus/1", SLICE) == SCOTUS_POPULATION_KEY
    assert routing_population("ca9/123", SLICE) == SCOTUS_POPULATION_KEY
    assert routing_population("cand/77", None) == SCOTUS_POPULATION_KEY
    assert routing_population("cand/77", SLICE) == "ai-watchlist"


def test_the_rosters_split_by_population(tmp_path: Path) -> None:
    predictors = _with_slice_actor(tmp_path, PREDICTORS, "predictors")

    court = {p.id for p in predictors_for(predictors, SCOTUS_POPULATION_KEY)}

    assert court == {p.id for p in enabled_predictors(PREDICTORS)}
    assert [p.id for p in predictors_for(predictors, "ai-watchlist")] == ["slice-actor"]
    assert evaluators_for(EVALUATORS, "ai-watchlist") == []


def test_a_slice_docket_is_forecast_by_the_slices_predictors_alone(tmp_path: Path) -> None:
    predictors = _with_slice_actor(tmp_path, PREDICTORS, "predictors")
    cases = [CaseRequest("cand", 77, ("evt-a",)), CaseRequest("scotus", 1, ("evt-b",))]

    cells = predict_matrix(predictors, cases, "RID", slices=SLICE)["include"]

    by_court = {
        c: {r["predictor_id"] for r in cells if r["court"] == c} for c in ("cand", "scotus")
    }
    assert by_court["cand"] == {"slice-actor"}
    assert by_court["scotus"] == {p.id for p in enabled_predictors(PREDICTORS)}


def test_a_slice_with_no_predictor_mints_no_cell() -> None:
    cases = [CaseRequest("cand", 77, ("evt-a",))]

    assert predict_matrix(PREDICTORS, cases, "RID", slices=SLICE)["include"] == []


def test_a_request_may_not_narrow_a_docket_to_another_populations_predictor(
    tmp_path: Path,
) -> None:
    predictors = _with_slice_actor(tmp_path, PREDICTORS, "predictors")
    cases = [CaseRequest("scotus", 1, ("evt-b",), predictors=("slice-actor",))]

    with pytest.raises(ValueError, match="not enabled"):
        predict_matrix(predictors, cases, "RID", slices=SLICE)


def test_a_slice_docket_is_graded_by_the_slices_judges_alone(tmp_path: Path) -> None:
    evaluators = _with_slice_actor(tmp_path, EVALUATORS, "evaluators")
    cases = [CaseRequest("cand", 77, ("evt-a",)), CaseRequest("scotus", 1, ("evt-b",))]

    cells = evaluate_matrix(evaluators, cases, "RID", slices=SLICE)["include"]

    by_court = {
        c: {r["evaluator_id"] for r in cells if r["court"] == c} for c in ("cand", "scotus")
    }
    assert by_court["cand"] == {"slice-actor"}
    assert by_court["scotus"] == {e.id for e in enabled_evaluators(EVALUATORS)}
