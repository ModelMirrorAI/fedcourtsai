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
    load_evaluators,
    load_predictors,
    predictors_for,
)

PREDICTORS = Path("config/predictors.yaml")
EVALUATORS = Path("config/evaluators.yaml")
SLICE = {"ai-watchlist": Population(key="ai-watchlist", case_ids=frozenset({"cand/77"}))}


#: The committed registries' slice actors, in registry order.
SLICE_PREDICTORS = ["claude-trial", "codex-trial", "gemini-trial"]
SLICE_JUDGES = ["claude-trial-judge", "codex-trial-judge", "gemini-trial-judge"]


def _courts_actors_only(tmp_path: Path, source: Path, section: str) -> Path:
    """The committed registry narrowed to the Court's actors: a slice with no actor."""
    data = yaml.safe_load(source.read_text())
    data[section] = [
        actor
        for actor in data[section]
        if actor.get("population", SCOTUS_POPULATION_KEY) == SCOTUS_POPULATION_KEY
    ]
    path = tmp_path / source.name
    path.write_text(yaml.safe_dump(data))
    return path


def _with_slice_actor(tmp_path: Path, source: Path, section: str) -> Path:
    """The Court's committed actors plus exactly one actor of the slice's population."""
    path = _courts_actors_only(tmp_path, source, section)
    data = yaml.safe_load(path.read_text())
    extra = dict(data[section][0], id="slice-actor", population="ai-watchlist")
    data[section].append(extra)
    path.write_text(yaml.safe_dump(data))
    return path


def test_an_actor_is_the_courts_unless_it_names_a_slice() -> None:
    predictors = load_predictors(PREDICTORS)
    evaluators = load_evaluators(EVALUATORS)

    assert [p.id for p in predictors if p.population == "ai-watchlist"] == SLICE_PREDICTORS
    assert [e.id for e in evaluators if e.population == "ai-watchlist"] == SLICE_JUDGES
    assert {p.population for p in predictors if p.id not in SLICE_PREDICTORS} == {
        SCOTUS_POPULATION_KEY
    }
    assert {e.population for e in evaluators if e.id not in SLICE_JUDGES} == {SCOTUS_POPULATION_KEY}
    assert {p.population for p in enabled_predictors(PREDICTORS)} == {
        SCOTUS_POPULATION_KEY,
        "ai-watchlist",
    }
    assert {e.population for e in enabled_evaluators(EVALUATORS)} == {
        SCOTUS_POPULATION_KEY,
        "ai-watchlist",
    }


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

    court = predictors_for(PREDICTORS, SCOTUS_POPULATION_KEY)
    assert court
    assert gate.candidates == len(cells["include"]) == 1 + 2 * len(court)


def test_a_docket_no_slice_admits_is_routed_to_the_courts_actors() -> None:
    assert routing_population("scotus/1", SLICE) == SCOTUS_POPULATION_KEY
    assert routing_population("ca9/123", SLICE) == SCOTUS_POPULATION_KEY
    assert routing_population("cand/77", None) == SCOTUS_POPULATION_KEY
    assert routing_population("cand/77", SLICE) == "ai-watchlist"


def test_the_rosters_split_by_population(tmp_path: Path) -> None:
    predictors = _with_slice_actor(tmp_path, PREDICTORS, "predictors")

    court = {p.id for p in predictors_for(predictors, SCOTUS_POPULATION_KEY)}

    assert court == {p.id for p in predictors_for(PREDICTORS, SCOTUS_POPULATION_KEY)}
    assert court.isdisjoint(SLICE_PREDICTORS)
    assert [p.id for p in predictors_for(predictors, "ai-watchlist")] == ["slice-actor"]
    assert [p.id for p in predictors_for(PREDICTORS, "ai-watchlist")] == SLICE_PREDICTORS
    assert [e.id for e in evaluators_for(EVALUATORS, "ai-watchlist")] == SLICE_JUDGES
    assert {p.id for p in enabled_predictors(PREDICTORS)} == court | set(SLICE_PREDICTORS)


def test_a_slice_docket_is_forecast_by_the_slices_predictors_alone(tmp_path: Path) -> None:
    predictors = _with_slice_actor(tmp_path, PREDICTORS, "predictors")
    cases = [CaseRequest("cand", 77, ("evt-a",)), CaseRequest("scotus", 1, ("evt-b",))]

    cells = predict_matrix(predictors, cases, "RID", slices=SLICE)["include"]

    by_court = {
        c: {r["predictor_id"] for r in cells if r["court"] == c} for c in ("cand", "scotus")
    }
    assert by_court["cand"] == {"slice-actor"}
    assert by_court["scotus"] == {p.id for p in predictors_for(PREDICTORS, SCOTUS_POPULATION_KEY)}
    assert by_court["scotus"]


def test_a_slice_with_no_predictor_mints_no_cell(tmp_path: Path) -> None:
    predictors = _courts_actors_only(tmp_path, PREDICTORS, "predictors")
    cases = [CaseRequest("cand", 77, ("evt-a",))]

    assert predictors_for(predictors, SCOTUS_POPULATION_KEY)
    assert predict_matrix(predictors, cases, "RID", slices=SLICE)["include"] == []


def test_the_committed_slice_predictors_forecast_a_slice_docket() -> None:
    cases = [CaseRequest("cand", 77, ("evt-a",)), CaseRequest("scotus", 1, ("evt-b",))]

    cells = predict_matrix(PREDICTORS, cases, "RID", slices=SLICE)["include"]

    assert {r["predictor_id"] for r in cells if r["court"] == "cand"} == set(SLICE_PREDICTORS)
    assert {r["predictor_id"] for r in cells if r["court"] == "scotus"}.isdisjoint(SLICE_PREDICTORS)


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
    assert by_court["scotus"] == {e.id for e in evaluators_for(EVALUATORS, SCOTUS_POPULATION_KEY)}
    assert by_court["scotus"]
