"""What an enabled prediction slice's dockets are owed, with no request naming them."""

from __future__ import annotations

import dataclasses
from datetime import date
from pathlib import Path

import pytest
import yaml

from fedcourtsai import corpus
from fedcourtsai.matrix import CaseRequest
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline import moments
from fedcourtsai.pipeline.slice_backlog import (
    derive_slice_evaluate_backlog,
    derive_slice_predict_backlog,
)
from fedcourtsai.prediction_slices import Population
from tests.conftest import seed_evaluation, seed_prediction

SLICE = {"ai-watchlist": Population(key="ai-watchlist", case_ids=frozenset({"cand/101"}))}
MOTION = "evt-motion-trial-dismissal-45"
BRIEF = "MOTION to Dismiss for Failure to State a Claim by Developer, Inc."
TODAY = date(2026, 6, 1)


@pytest.fixture
def switched_on(monkeypatch: pytest.MonkeyPatch) -> None:
    declared = moments.trial_spec
    monkeypatch.setattr(
        moments,
        "trial_spec",
        lambda m: dataclasses.replace(declared(m), forecastable=True, opens_from=date(2026, 1, 1)),
    )


def _registry(tmp_path: Path, name: str, section: str, ids: tuple[str, ...]) -> Path:
    """The committed registry plus slice actors ``ids``."""
    data = yaml.safe_load(Path("config", name).read_text())
    data[section] += [dict(data[section][0], id=i, population="ai-watchlist") for i in ids]
    path = tmp_path / name
    path.write_text(yaml.safe_dump(data))
    return path


def _corpus(
    tmp_path: Path,
    *,
    resolved: bool = False,
    excluded: bool = False,
    read_on: date | None = TODAY,
    ruling: str | None = None,
) -> Path:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="cand/101",
                    court="cand",
                    predict_excluded=excluded,
                    last_pulled=read_on,
                ),
                corpus.CorpusRow(case_id="cand/999", court="cand"),
            ],
        )
        corpus.upsert_events(
            conn,
            [
                corpus.CorpusEvent(
                    event_id=MOTION,
                    case_id=case_id,
                    court="cand",
                    kind="motion",
                    stage="trial",
                    moment="trial-dismissal",
                    resolved=resolved,
                )
                for case_id in ("cand/101", "cand/999")
            ]
            + [
                corpus.CorpusEvent(
                    event_id="evt-appeal-disposition",
                    case_id="cand/101",
                    court="cand",
                    kind="appeal",
                    resolved=resolved,
                )
            ],
        )
        if ruling is not None:
            entries = [
                {"id": 1, "entry_number": 45, "date_filed": "2026-01-05", "description": BRIEF},
                {"id": 2, "entry_number": 60, "date_filed": "2026-03-05", "description": ruling},
            ]
            corpus.upsert_snapshot(conn, "cand/101", TODAY, {"docket_entries": entries})
    return db


def _predict(
    tmp_path: Path, db: Path, ids: tuple[str, ...] = ("slice-a", "slice-b")
) -> list[CaseRequest]:
    with corpus.connect_readonly(db) as conn:
        return derive_slice_predict_backlog(
            conn,
            tmp_path / "data",
            _registry(tmp_path, "predictors.yaml", "predictors", ids),
            SLICE,
            max_attempts=2,
            today=TODAY,
        )


def _evaluate(
    tmp_path: Path, db: Path, ids: tuple[str, ...] = ("judge-a", "judge-b")
) -> list[CaseRequest]:
    with corpus.connect_readonly(db) as conn:
        return derive_slice_evaluate_backlog(
            conn,
            tmp_path / "data",
            _registry(tmp_path, "evaluators.yaml", "evaluators", ids),
            SLICE,
            max_attempts=2,
        )


def test_a_switched_off_slice_owes_no_forecast(tmp_path: Path) -> None:
    assert _predict(tmp_path, _corpus(tmp_path)) == []


def test_an_open_switched_on_motion_is_owed_on_the_slices_docket_alone(
    tmp_path: Path, switched_on: None
) -> None:
    # The stage-less baseline on the same docket, and the same motion on a
    # docket the slice does not list, are owed nothing.
    assert _predict(tmp_path, _corpus(tmp_path)) == [CaseRequest("cand", 101, (MOTION,))]


def test_a_slice_with_no_predictor_owes_nothing(tmp_path: Path, switched_on: None) -> None:
    assert _predict(tmp_path, _corpus(tmp_path), ids=()) == []


def test_a_motion_is_owed_until_every_slice_predictor_holds_a_forecast(
    tmp_path: Path, switched_on: None
) -> None:
    db = _corpus(tmp_path)
    seed_prediction(tmp_path / "data", "cand", 101, MOTION, predictor_id="slice-a")
    assert _predict(tmp_path, db) == [CaseRequest("cand", 101, (MOTION,))]

    seed_prediction(tmp_path / "data", "cand", 101, MOTION, predictor_id="slice-b")
    assert _predict(tmp_path, db) == []


def test_a_court_predictors_forecast_does_not_cover_the_slice(
    tmp_path: Path, switched_on: None
) -> None:
    db = _corpus(tmp_path)
    seed_prediction(tmp_path / "data", "cand", 101, MOTION, predictor_id="claude-baseline")

    assert _predict(tmp_path, db) == [CaseRequest("cand", 101, (MOTION,))]


def test_a_docket_latched_out_of_scope_or_resolved_owes_no_forecast(
    tmp_path: Path, switched_on: None
) -> None:
    assert _predict(tmp_path, _corpus(tmp_path, excluded=True)) == []
    assert _predict(tmp_path / "b", _corpus(tmp_path / "b", resolved=True)) == []


def test_a_docket_not_read_inside_the_bound_is_held(tmp_path: Path, switched_on: None) -> None:
    assert _predict(tmp_path, _corpus(tmp_path, read_on=None)) == []
    assert _predict(tmp_path / "b", _corpus(tmp_path / "b", read_on=date(2026, 5, 1))) == []


def test_an_event_the_stored_docket_may_already_decide_is_not_owed(
    tmp_path: Path, switched_on: None
) -> None:
    # Provisioning refuses this cell by design and records nothing, so a
    # backlog that owed it would mint it again every round.
    hearing = "Minute Entry: Motion Hearing held. The Court granted 45 motion to dismiss."
    quiet = "ORDER setting hearing on 45 Motion to Dismiss for 7/1/2026."

    assert _predict(tmp_path, _corpus(tmp_path, ruling=hearing)) == []
    assert _predict(tmp_path / "b", _corpus(tmp_path / "b", ruling=quiet)) == [
        CaseRequest("cand", 101, (MOTION,))
    ]


def test_a_cell_at_the_attempt_cap_is_not_owed_again(tmp_path: Path, switched_on: None) -> None:
    db = _corpus(tmp_path)
    event = CasePaths(tmp_path / "data", "cand", 101).event(MOTION)
    for predictor in ("slice-a", "slice-b"):
        for run in ("20260501T000000Z", "20260502T000000Z"):
            attempt = event.predictions_dir / predictor / run / "attempt.json"
            attempt.parent.mkdir(parents=True)
            attempt.write_text("{}")

    assert _predict(tmp_path, db) == []


def test_a_resolved_predicted_motion_is_owed_until_every_slice_judge_grades_it(
    tmp_path: Path,
) -> None:
    db = _corpus(tmp_path, resolved=True)
    assert _evaluate(tmp_path, db) == []  # nothing predicted, nothing to grade

    seed_prediction(tmp_path / "data", "cand", 101, MOTION, predictor_id="slice-a")
    # The trial event alone: the resolved stage-less baseline is not the slice's.
    assert _evaluate(tmp_path, db) == [CaseRequest("cand", 101, (MOTION,))]

    for judge in ("judge-a", "judge-b"):
        seed_evaluation(tmp_path / "data", "cand", 101, MOTION, evaluator_id=judge)
    assert _evaluate(tmp_path, db) == []


def test_an_open_motion_and_a_slice_with_no_judge_owe_no_grading(tmp_path: Path) -> None:
    seed_prediction(tmp_path / "data", "cand", 101, MOTION, predictor_id="slice-a")

    assert _evaluate(tmp_path, _corpus(tmp_path)) == []
    assert _evaluate(tmp_path / "b", _corpus(tmp_path / "b", resolved=True), ids=()) == []
