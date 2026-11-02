"""Prediction slices: the registry, the committed off state, and the population guard."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from fedcourtsai import prediction_slices
from fedcourtsai.ai_watchlist import load_ai_watchlist, tagged_case_ids
from fedcourtsai.config import PredictConfig, load_predict_config
from fedcourtsai.prediction_slices import (
    SCOTUS_POPULATION,
    SLICES,
    Population,
    SliceOverlapError,
    SliceSource,
    check_slice_ids,
    load_slices,
    population_of,
)
from fedcourtsai.store import (
    in_population,
    iter_evaluations,
    iter_predicted_events,
    iter_predictions,
    stratify,
)
from tests.conftest import seed_evaluation, seed_prediction

_CONFIG = Path(__file__).resolve().parent.parent / "config"


def test_the_committed_config_switches_no_slice_on() -> None:
    # Groundwork: the mechanism exists, and the committed scope is still the
    # SCOTUS docket alone.
    assert load_predict_config(_CONFIG).slices == []


def test_every_registered_slice_reads_a_committed_list_and_no_two_overlap() -> None:
    populations = load_slices(_CONFIG, SLICES)

    assert set(populations) == set(SLICES)
    watchlist = tagged_case_ids(load_ai_watchlist(_CONFIG / "ai-watchlist.yaml"))
    assert populations["ai-watchlist"].case_ids == watchlist
    assert all(not SCOTUS_POPULATION.admits_case(case_id) for case_id in watchlist)


def test_the_predict_config_refuses_an_unknown_or_repeated_slice() -> None:
    assert PredictConfig().slices == []
    assert PredictConfig.model_validate({"slices": ["ai-watchlist"]}).slices == ["ai-watchlist"]
    with pytest.raises(ValidationError, match="unknown prediction slice"):
        PredictConfig.model_validate({"slices": ["cadc-argued"]})
    with pytest.raises(ValidationError, match="distinct"):
        PredictConfig.model_validate({"slices": ["ai-watchlist", "ai-watchlist"]})
    with pytest.raises(ValueError, match="unknown prediction slice"):
        check_slice_ids(["all-cadc"])


def test_a_population_names_a_court_or_a_list() -> None:
    listed = Population(key="s", case_ids=frozenset({"cand/101"}))

    assert SCOTUS_POPULATION.admits("scotus", 1)
    assert not SCOTUS_POPULATION.admits("cand", 101)
    assert listed.admits("cand", 101)
    assert not listed.admits("cand", 102)
    assert not listed.admits_case("cand/not-a-docket")
    with pytest.raises(ValueError, match="not both"):
        Population(key="bad")
    with pytest.raises(ValueError, match="not both"):
        Population(key="bad", court="scotus", case_ids=frozenset())


def test_population_of_keys_scotus_a_slice_or_nothing() -> None:
    slices = {"ai-watchlist": Population(key="ai-watchlist", case_ids=frozenset({"cand/101"}))}

    assert population_of("scotus/24001", slices) == "scotus"
    assert population_of("cand/101", slices) == "ai-watchlist"
    assert population_of("cand/102", slices) is None
    assert population_of("cand/101", {}) is None


def _two_slices(monkeypatch: pytest.MonkeyPatch, first: str, second: str) -> None:
    monkeypatch.setattr(
        prediction_slices,
        "SLICES",
        {
            "one": SliceSource("one.yaml", lambda _: frozenset({first}), "first"),
            "two": SliceSource("two.yaml", lambda _: frozenset({second}), "second"),
        },
    )


def test_load_slices_refuses_a_docket_two_slices_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "one.yaml").write_text("")
    (tmp_path / "two.yaml").write_text("")
    _two_slices(monkeypatch, "cadc/7", "cadc/7")

    with pytest.raises(SliceOverlapError, match="cadc/7"):
        load_slices(tmp_path, ["one", "two"])
    # Each alone is fine: the overlap is between enabled slices.
    assert load_slices(tmp_path, ["one"])["one"].case_ids == frozenset({"cadc/7"})


def test_load_slices_refuses_a_scotus_docket_and_a_missing_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "one.yaml").write_text("")
    _two_slices(monkeypatch, "scotus/1", "cadc/7")

    with pytest.raises(ValueError, match="SCOTUS docket"):
        load_slices(tmp_path, ["one"])
    with pytest.raises(FileNotFoundError, match=r"two\.yaml"):
        load_slices(tmp_path, ["two"])


def test_in_population_reads_the_event_dirs_court_and_docket(tmp_path: Path) -> None:
    event_dir = tmp_path / "cases" / "cand" / "101" / "events" / "evt-x"

    assert not in_population(event_dir, SCOTUS_POPULATION)
    assert in_population(event_dir, Population(key="s", case_ids=frozenset({"cand/101"})))
    assert in_population(tmp_path / "cases" / "scotus" / "5" / "events" / "e", SCOTUS_POPULATION)


def test_scotus_readers_leave_a_slices_events_out(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    seed_prediction(data_root, "scotus", 24001, "evt-petition-cert")
    seed_prediction(data_root, "cand", 101, "evt-petition-cert")
    seed_evaluation(data_root, "scotus", 24001, "evt-petition-cert")
    seed_evaluation(data_root, "cand", 101, "evt-petition-cert")
    listed = Population(key="ai-watchlist", case_ids=frozenset({"cand/101"}))

    assert [row.case_id for row in iter_predictions(data_root)] == ["scotus/24001"]
    assert [row.case_id for row in iter_predictions(data_root, population=listed)] == ["cand/101"]
    assert [ref.case_id for ref in iter_predicted_events(data_root)] == ["scotus/24001"]
    assert [ev.case_id for ev in iter_evaluations(data_root)] == ["scotus/24001"]
    assert [ev.case_id for ev in iter_evaluations(data_root, population=listed)] == ["cand/101"]
    # The ops report's all-populations reading.
    assert [ev.case_id for ev in iter_evaluations(data_root, population=None)] == [
        "cand/101",
        "scotus/24001",
    ]


def test_stratify_never_reads_a_cell_outside_its_population(tmp_path: Path) -> None:
    # A slice grading with no outcome beside it is a ledger the SCOTUS join
    # would refuse if it read it; the guard means the SCOTUS pass never does,
    # and the slice's own pass does.
    data_root = tmp_path / "data"
    seed_prediction(data_root, "cand", 101, "evt-petition-cert")
    seed_evaluation(data_root, "cand", 101, "evt-petition-cert")
    listed = Population(key="ai-watchlist", case_ids=frozenset({"cand/101"}))

    run = stratify(data_root, frozen_only=False)
    assert run.cells == []
    assert run.excluded == []
    with pytest.raises(FileNotFoundError):
        stratify(data_root, frozen_only=False, population=listed)
