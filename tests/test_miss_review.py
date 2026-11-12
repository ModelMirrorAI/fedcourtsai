"""The forward miss review over a small fixture ledger."""

from datetime import UTC, date, datetime
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import ops
from fedcourtsai.cli import app
from fedcourtsai.integrity import FORWARD, RETROSPECTIVE, StratifiedCell
from fedcourtsai.miss_review import WRONG_SIDE_BRIER, build_miss_review, miss_review_summary
from fedcourtsai.process_version import FINER_INTERIM_READING_FROM
from fedcourtsai.schemas import (
    CountingWindow,
    Disposition,
    Engine,
    Evaluation,
    Judgment,
    MissReview,
    Moment,
    Outcome,
    Prediction,
    ProcessVersion,
    RetrievalLog,
    Stage,
    Stratum,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.store import evaluation_key

CASE = "scotus/123"
EVENT = "evt-petition-disposition"
RUN = "20260601T000000Z"


def _event_dir(data_root: Path, event_id: str = EVENT) -> Path:
    return data_root / "cases" / CASE / "events" / event_id


def _predict(
    data_root: Path,
    predictor_id: str,
    *,
    disposition: Disposition,
    probability: float,
    event_id: str = EVENT,
    fetches: int | None = None,
    run_id: str = RUN,
    **extra: object,
) -> None:
    run_dir = _event_dir(data_root, event_id) / "predictions" / predictor_id / run_id
    write_json(
        run_dir / "prediction.json",
        Prediction(
            case_id=CASE,
            event_id=event_id,
            predictor_id=predictor_id,
            engine=Engine.claude_code,
            run_id=run_id,
            created_at=datetime(2026, 6, 1, tzinfo=UTC),
            input_snapshot="record/snapshot.json",
            granted=int(probability >= 0.5),
            probability=probability,
            predicted_disposition=disposition,
            **extra,
        ),
    )
    if fetches is not None:
        write_json(
            run_dir / "retrieval_log.json",
            RetrievalLog(
                case_id=CASE,
                run_id=run_id,
                role="predictor",
                actor_id=predictor_id,
                engine=Engine.claude_code,
                self_provisioned_fetches=fetches,
            ),
        )


def _resolve(
    data_root: Path, disposition: Disposition, event_id: str = EVENT, **extra: object
) -> None:
    write_json(
        _event_dir(data_root, event_id) / "outcome.json",
        Outcome(
            case_id=CASE,
            event_id=event_id,
            resolved_at=date(2026, 6, 20),
            actual_disposition=disposition,
            actual_granted=int(disposition is not Disposition.denied),
            **extra,
        ),
    )


def _cell(
    predictor_id: str,
    evaluator_id: str = "eval-a",
    *,
    event_id: str = EVENT,
    stratum: Stratum = FORWARD,
    quality: float | None = 0.8,
    prediction_run_id: str = RUN,
    stage: Stage = Stage.cert,
    moment: Moment = Moment.distribution,
) -> StratifiedCell:
    evaluation = Evaluation(
        case_id=CASE,
        event_id=event_id,
        predictor_id=predictor_id,
        evaluator_id=evaluator_id,
        engine=Engine.claude_code,
        run_id="r1",
        prediction_run_id=prediction_run_id,
        created_at=datetime(2026, 6, 24, tzinfo=UTC),
        correct=1,
        reasoning_quality=quality,
    )
    return (evaluation, stratum, stage, moment)


def test_an_empty_ledger_reviews_nothing(tmp_path: Path) -> None:
    review = build_miss_review([], tmp_path)
    assert review.events.events == 0
    assert review.cells.cells == 0
    assert review.missed_events == []
    assert review.wrong_side_brier == WRONG_SIDE_BRIER


def test_a_miss_lists_every_forecast_of_the_event_and_marks_it_single(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.granted)
    _predict(tmp_path, "alpha", disposition=Disposition.denied, probability=0.1, fetches=0)
    _predict(tmp_path, "beta", disposition=Disposition.granted, probability=0.7, fetches=2)
    cells = [_cell("alpha"), _cell("alpha", "eval-b", quality=0.4), _cell("beta")]

    review = build_miss_review(cells, tmp_path)

    assert review.events.model_dump() == {"events": 1, "missed": 1, "shared": 0}
    assert review.cells.model_dump() == {"cells": 2, "missed": 1}
    (event,) = review.missed_events
    assert event.outcome == "granted"
    assert not event.shared
    alpha, beta = event.calls
    assert (alpha.wrong_call, alpha.wrong_side) == (True, True)
    assert alpha.prediction_run_id == RUN
    # Two gradings of one forecast are one cell, and its grade is their mean.
    assert alpha.gradings == 2
    assert alpha.mean_reasoning_quality == 0.6
    assert (beta.wrong_call, beta.wrong_side) == (False, False)
    assert review.by_predictor["alpha"].missed == 1
    assert review.by_predictor["beta"].missed == 0
    assert review.by_self_provisioning["none"].model_dump() == {"cells": 1, "missed": 1}
    assert review.by_self_provisioning["fetched"].model_dump() == {"cells": 1, "missed": 0}
    assert review.by_stage["cert@distribution"].missed == 1


def test_a_miss_every_predictor_shares_is_marked_shared(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.granted)
    _predict(tmp_path, "alpha", disposition=Disposition.denied, probability=0.1)
    _predict(tmp_path, "beta", disposition=Disposition.denied, probability=0.3)

    review = build_miss_review([_cell("alpha"), _cell("beta")], tmp_path)

    assert review.events.shared == 1
    assert review.missed_events[0].shared
    # No log was committed, so the depth cut says so instead of reading zero.
    assert review.by_self_provisioning["unlogged"].cells == 2


def test_a_lone_predictors_miss_is_not_shared(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.granted)
    _predict(tmp_path, "alpha", disposition=Disposition.denied, probability=0.1)

    review = build_miss_review([_cell("alpha")], tmp_path)

    assert review.events.missed == 1
    assert review.events.shared == 0


def test_a_wrong_label_on_the_right_side_of_one_half_is_a_wrong_call_only(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.gvr)
    _predict(tmp_path, "alpha", disposition=Disposition.granted, probability=0.8)

    review = build_miss_review([_cell("alpha")], tmp_path)

    (call,) = review.missed_events[0].calls
    assert call.wrong_call
    assert not call.wrong_side


def test_a_right_call_at_even_odds_is_on_the_wrong_side(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.denied)
    _predict(tmp_path, "alpha", disposition=Disposition.denied, probability=0.5)

    review = build_miss_review([_cell("alpha")], tmp_path)

    (call,) = review.missed_events[0].calls
    assert not call.wrong_call
    assert call.wrong_side


def test_an_event_nobody_missed_is_counted_and_not_listed(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.denied)
    _predict(tmp_path, "alpha", disposition=Disposition.denied, probability=0.05)

    review = build_miss_review([_cell("alpha")], tmp_path)

    assert review.events.model_dump() == {"events": 1, "missed": 0, "shared": 0}
    assert review.missed_events == []
    assert "0 of 1 forward event(s)" in miss_review_summary(review)


def test_only_the_forward_stratum_is_reviewed(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.granted)
    _predict(tmp_path, "alpha", disposition=Disposition.denied, probability=0.1)

    review = build_miss_review([_cell("alpha", stratum=RETROSPECTIVE)], tmp_path)

    assert review.events.events == 0


def test_a_cell_with_no_readable_prediction_is_left_out(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.granted)

    review = build_miss_review([_cell("alpha")], tmp_path)

    assert review.cells.cells == 0


def test_the_command_writes_a_byte_stable_artifact(tmp_path: Path) -> None:
    env = {"FEDCOURTS_DATA_ROOT": str(tmp_path / "data")}
    first, second = tmp_path / "a.json", tmp_path / "b.json"
    runner = CliRunner()
    for out in (first, second):
        result = runner.invoke(app, ["miss-review", "--out", str(out), "--all-versions"], env=env)
        assert result.exit_code == 0, result.output
    assert first.read_bytes() == second.read_bytes()
    assert read_model(first, MissReview).process_scope == "all"


def test_the_weekly_digest_prints_the_miss_counts_under_the_forward_block(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.granted)
    _predict(tmp_path, "alpha", disposition=Disposition.denied, probability=0.1)
    _predict(tmp_path, "beta", disposition=Disposition.denied, probability=0.3)
    review = build_miss_review([_cell("alpha"), _cell("beta")], tmp_path)

    lines = "\n".join(ops._miss_review_lines(ops.Vintaged(review, "2026-11-09")))

    assert "### Forward misses" in lines
    assert "`metrics/miss-review.json`, vintage 2026-11-09" in lines
    assert "**1** of **1** forward event(s) hold one, **1** of them missed by every" in lines
    # Per event, never per predictor.
    assert "alpha" not in lines
    assert "| cert@distribution | 1 | 1 | 1 |" in lines


def test_the_weekly_digest_says_when_the_review_has_never_landed() -> None:
    lines = ops._miss_review_lines(ops.Vintaged(None, None))
    assert "_`metrics/miss-review.json` has never landed._" in lines
    # A digest built without the review prints no block at all.
    assert ops._miss_review_lines(None) == []


FINER = ProcessVersion(
    label=FINER_INTERIM_READING_FROM, digest="sha256:x", stamped_at=datetime(2026, 6, 1, tzinfo=UTC)
)


def test_an_interim_cell_is_scored_on_the_finer_reading_its_grading_is(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.other, interim_reading="granted-in-part", interim_granted=1)
    _predict(
        tmp_path, "alpha", disposition=Disposition.granted, probability=0.8, process_version=FINER
    )
    cell = _cell("alpha", stage=Stage.interim, moment=Moment.arrival)

    review = build_miss_review([cell], tmp_path)

    # A partial grant called `granted` is right on the binary the cell is scored on.
    assert review.cells.model_dump() == {"cells": 1, "missed": 0}
    assert review.unscored_cells == 0


def test_an_interim_cell_the_finer_reading_leaves_unscored_is_counted_apart(
    tmp_path: Path,
) -> None:
    _resolve(tmp_path, Disposition.dismissed, interim_reading="dismissed-moot")
    _predict(
        tmp_path, "alpha", disposition=Disposition.granted, probability=0.8, process_version=FINER
    )
    cell = _cell("alpha", stage=Stage.interim, moment=Moment.arrival)

    review = build_miss_review([cell], tmp_path)

    assert review.unscored_cells == 1
    assert review.cells.cells == 0
    assert review.missed_events == []


def test_gradings_naming_two_runs_review_the_earlier_with_its_own_gradings(
    tmp_path: Path,
) -> None:
    _resolve(tmp_path, Disposition.granted)
    later = "20260602T000000Z"
    _predict(tmp_path, "alpha", disposition=Disposition.denied, probability=0.1)
    _predict(tmp_path, "alpha", disposition=Disposition.granted, probability=0.9, run_id=later)
    cells = [
        _cell("alpha", "eval-a", prediction_run_id=later, quality=0.2),
        _cell("alpha", "eval-b", quality=0.9),
    ]

    review = build_miss_review(cells, tmp_path)

    (call,) = review.missed_events[0].calls
    assert call.prediction_run_id == RUN
    assert call.gradings == 1
    assert call.mean_reasoning_quality == 0.9


def test_a_merits_event_is_read_on_the_judgment_axis(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.other, judgment=Judgment.reversed)
    _predict(tmp_path, "alpha", disposition=Disposition.other, probability=0.3)
    cell = _cell("alpha", stage=Stage.merits, moment=Moment.grant)

    review = build_miss_review([cell], tmp_path)

    (event,) = review.missed_events
    assert event.outcome == "reversed"
    # A prediction naming no judgment is wrong on that axis, never an `other == other` match.
    assert event.calls[0].call == "(none)"
    assert event.calls[0].wrong_call


def test_a_frozen_build_names_each_forecasts_window(tmp_path: Path) -> None:
    _resolve(tmp_path, Disposition.granted)
    _predict(tmp_path, "alpha", disposition=Disposition.denied, probability=0.1)
    cell = _cell("alpha")
    window = CountingWindow(
        label="proc-v8", digest="sha256:x", opens=datetime(2026, 5, 1, tzinfo=UTC)
    )

    review = build_miss_review([cell], tmp_path, cell_windows={evaluation_key(cell[0]): window})

    assert review.missed_events[0].calls[0].process_window == "proc-v8"
    assert review.by_band == {"(none)": review.cells}
    assert review.by_snapshot_provenance == {"(none)": review.cells}


def test_the_weekly_digest_says_when_nothing_is_reviewed(tmp_path: Path) -> None:
    lines = ops._miss_review_lines(ops.Vintaged(build_miss_review([], tmp_path), None))
    assert any("No forward cell is reviewed yet" in line for line in lines)
