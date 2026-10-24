"""The pilot's replay merits calibration cells: a kept tree read back, drawn, and laid out."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.merits_backtest import replay_merits_predictors
from fedcourtsai.merits_calibration import (
    calibration_documents,
    read_kept_run,
    write_calibration_overlay,
)
from fedcourtsai.reasoning_pilot import SAMPLE_FILE, write_sample
from fedcourtsai.schemas import Moment, Outcome, Stage
from tests.test_merits_backtest import _DECIDED_DOCKET, _case, _replayable

runner = CliRunner()
RUN = "20261024T000000Z"
EVENT = "cases/scotus/1/events/evt-brief-judgment"


def _kept(tmp_path: Path) -> Path:
    """A stub merits replay's kept tree over the one-case fixture corpus."""
    kept = tmp_path / "kept"
    with _replayable(tmp_path, _DECIDED_DOCKET) as conn:
        replay_merits_predictors(
            conn,
            [_case(conn)],
            config_root=Path("config"),
            work_root=tmp_path / "replay",
            run_id=RUN,
            engine_override="stub",
            keep_root=kept,
        )
    return kept


def test_a_stub_tree_reads_back_only_when_stub_lanes_are_allowed(tmp_path: Path) -> None:
    kept = _kept(tmp_path)
    with pytest.raises(ValueError, match="not an engine's"):
        read_kept_run(kept)

    run = read_kept_run(kept, allow_stub=True)

    assert run.run_id == RUN
    assert {(f.moment, f.case_id) for f in run.forecasts} == {
        (Moment.grant, "scotus/1"),
        (Moment.briefed, "scotus/1"),
    }
    assert all("prediction.json" in f.files for f in run.forecasts)


def _stray_forecast(kept: Path) -> None:
    stray = kept / f"stub/briefed/{EVENT}/predictions/p/{RUN}/copy.md"
    stray.parent.mkdir(parents=True)
    stray.write_text("a record copied under another name")


@pytest.mark.parametrize(
    ("plant", "match"),
    [
        (lambda k: (k / "stub/notes.txt").write_text("x"), "outside the kept layout"),
        (_stray_forecast, "not one of this run's forecast files"),
        (lambda k: (k / "stub/link").symlink_to(k / "run-id"), "not a regular file"),
        (lambda k: (k / "run-id").write_text("not-a-run\n"), "does not hold a run id"),
    ],
)
def test_a_tree_with_anything_out_of_place_is_refused_whole(
    tmp_path: Path, plant: Callable[[Path], object], match: str
) -> None:
    kept = _kept(tmp_path)
    plant(kept)

    with pytest.raises(ValueError, match=match):
        read_kept_run(kept, allow_stub=True)


def test_a_prediction_naming_another_case_is_refused(tmp_path: Path) -> None:
    kept = _kept(tmp_path)
    [path] = list(kept.glob(f"stub/briefed/{EVENT}/predictions/claude-baseline/*/prediction.json"))
    body = json.loads(path.read_text())
    path.write_text(json.dumps({**body, "case_id": "scotus/2"}))

    with pytest.raises(ValueError, match="prediction names"):
        read_kept_run(kept, allow_stub=True)


def test_the_overlay_lays_out_resolved_merits_events_an_evaluate_round_can_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kept = _kept(tmp_path)
    run = read_kept_run(kept, allow_stub=True)
    data_root = tmp_path / "data"
    with _replayable(tmp_path / "again", _DECIDED_DOCKET) as conn:
        case = _case(conn)
        documents = calibration_documents(run, [case])
        sample = write_calibration_overlay(conn, documents, [case], data_root)
        # A second overlay never sits beside the first.
        with pytest.raises(ValueError, match="already holds this event"):
            write_calibration_overlay(conn, documents, [case], data_root)

    assert {d.moment for d in documents} == {Moment.briefed}
    assert {d.stage for d in sample} == {Stage.merits}
    assert sorted(d.predictor_id for d in sample) == sorted(
        f.prediction.predictor_id for f in run.forecasts if f.moment is Moment.briefed
    )
    event = yaml.safe_load((data_root / EVENT / "event.yaml").read_text())
    assert (event["event_id"], event["resolved"]) == ("evt-brief-judgment", True)
    outcome = Outcome.model_validate_json((data_root / EVENT / "outcome.json").read_text())
    assert (outcome.judgment, outcome.actual_granted) == (case.judgment, 1)
    for document in sample:
        assert document.path.is_file()

    out = tmp_path / "sample"
    write_sample(sample, out)
    assert {e["stage"] for e in json.loads((out / SAMPLE_FILE).read_text())} == {"merits"}
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(data_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "again" / "corpus"))
    result = runner.invoke(
        app,
        [
            "evaluate-matrix",
            "--run-id",
            "20261025T000000Z",
            "--body-file",
            str(out / "body.md"),
            "--force",
            "--pilot-section",
            ".github/prompts/pilot/predicted-reasoning-quality.md",
            "--calibration",
        ],
    )
    assert result.exit_code == 0, result.output
    rows = json.loads(result.stdout.strip().splitlines()[-1])["include"]
    assert rows
    assert all(row["event_id"] == "evt-brief-judgment" and row["calibration"] for row in rows)


def test_calibration_rows_are_pilot_rows() -> None:
    result = runner.invoke(
        app, ["evaluate-matrix", "--run-id", "20261025T000000Z", "--calibration"]
    )

    assert result.exit_code == 1
    assert "needs --pilot-section" in result.output


def test_the_sample_command_refuses_a_stub_tree_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kept = _kept(tmp_path)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    args = [
        "reasoning-pilot-merits-sample",
        str(kept),
        str(tmp_path / "sample"),
        "--data-root",
        str(tmp_path / "data"),
        "--terms",
        "2024",
        "--corpus-backend",
        "local",
    ]

    refused = runner.invoke(app, args)
    taken = runner.invoke(app, [*args, "--allow-stub"])

    assert refused.exit_code == 1 and "refusing the kept tree" in refused.output
    assert taken.exit_code == 0, taken.output
    assert (tmp_path / "data" / EVENT / "outcome.json").is_file()
    assert (tmp_path / "sample" / "body.md").is_file()


def test_an_event_under_another_moment_is_refused(tmp_path: Path) -> None:
    kept = _kept(tmp_path)
    (kept / "stub/briefed/cases/scotus/1/events").rename(tmp_path / "moved")
    (kept / "stub/grant/cases/scotus/1/events/evt-order-judgment").rename(
        kept / "stub/grant/cases/scotus/1/events/evt-brief-judgment"
    )

    with pytest.raises(ValueError, match="merits moment's event"):
        read_kept_run(kept, allow_stub=True)


def _claude_lane(kept: Path) -> None:
    """The stub tree recast as a real engine's lane holding the one predictor it ran."""
    (kept / "stub").rename(kept / "claude-code")
    for path in list((kept / "claude-code").rglob("predictions/*")):
        if path.name != "claude-baseline":
            shutil.rmtree(path)


def test_an_engine_lane_holds_only_predictors_configured_on_that_engine(
    tmp_path: Path,
) -> None:
    kept = _kept(tmp_path)
    _claude_lane(kept)

    run = read_kept_run(kept, predictors={"claude-baseline": "claude-code"})
    with pytest.raises(ValueError, match="not a configured predictor"):
        read_kept_run(kept, predictors={"claude-baseline": "codex"})

    assert {(f.lane, f.prediction.predictor_id) for f in run.forecasts} == {
        ("claude-code", "claude-baseline")
    }


def test_one_predictor_kept_in_two_lanes_is_refused(tmp_path: Path) -> None:
    kept = _kept(tmp_path)
    shutil.copytree(kept / "stub", tmp_path / "stub")
    _claude_lane(kept)
    shutil.copytree(tmp_path / "stub", kept / "stub")

    with pytest.raises(ValueError, match="more than one lane"):
        read_kept_run(kept, allow_stub=True)


def test_a_kept_event_that_opened_on_another_day_is_left_out(tmp_path: Path) -> None:
    kept = _kept(tmp_path)
    event_file = kept / "stub/briefed" / EVENT / "event.yaml"
    event = yaml.safe_load(event_file.read_text())
    event_file.write_text(yaml.safe_dump({**event, "opened_at": "2001-01-01"}))
    run = read_kept_run(kept, allow_stub=True)
    with _replayable(tmp_path / "again", _DECIDED_DOCKET) as conn:
        case = _case(conn)

    assert calibration_documents(run, [case]) == []
    assert calibration_documents(run, [case], moment=Moment.grant)


def test_the_sample_command_never_writes_the_committed_ledger(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "reasoning-pilot-merits-sample",
            str(tmp_path / "kept"),
            str(tmp_path / "sample"),
            "--data-root",
            "data/cases",
        ],
    )

    assert result.exit_code == 2
    assert "committed ledger" in result.output
