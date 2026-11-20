"""The stamp's skill record on a trial-stage evaluation: a Brier, and no base rate."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    Disposition,
    Evaluation,
    EventKind,
    Moment,
    Outcome,
    PredictableEvent,
    Prediction,
    Stage,
)
from fedcourtsai.serialize import write_json, write_yaml

runner = CliRunner()
EVENT = "evt-motion-trial-dismissal-45"


@pytest.fixture(autouse=True)
def _data_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    # No statpack anywhere: the trial record must not need one.
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(tmp_path / "metrics"))
    return tmp_path / "data"


def test_the_stamp_writes_a_trial_brier_and_clears_the_rate_and_skill(_data_root: Path) -> None:
    event_paths = CasePaths(_data_root, "cand", 100).event(EVENT)
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id=EVENT,
            case_id="cand/100",
            kind=EventKind.motion,
            stage=Stage.trial,
            moment=Moment.trial_dismissal,
            title="Motion to dismiss (entry 45)",
            opened_at=date(2026, 2, 1),
            decision_target="ruling",
        ),
    )
    write_json(
        event_paths.prediction("claude-baseline", "RID"),
        Prediction(
            case_id="cand/100",
            event_id=EVENT,
            predictor_id="claude-baseline",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 2, 2, tzinfo=UTC),
            input_snapshot="2026-02-01.json",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.other,
        ),
    )
    write_json(
        event_paths.outcome,
        Outcome(
            case_id="cand/100",
            event_id=EVENT,
            resolved_at=date(2026, 7, 20),
            actual_disposition=Disposition.other,
            actual_granted=0,
            trial_ruling="denied",
        ),
    )
    graded = event_paths.evaluation("claude-judge", "claude-baseline", "RID")
    write_json(
        graded,
        Evaluation(
            case_id="cand/100",
            event_id=EVENT,
            predictor_id="claude-baseline",
            evaluator_id="claude-judge",
            engine="claude-code",
            run_id="RID",
            created_at=datetime(2026, 8, 1, tzinfo=UTC),
            # A judge's own arithmetic, wrong on all four.
            correct=1,
            brier_score=0.09,
            segment_base_rate=0.46,
            brier_skill_score=0.5,
            base_rate_basis="terminal",
        ),
    )

    result = runner.invoke(
        app,
        [
            "stamp-cell",
            "--court",
            "cand",
            "--docket",
            "100",
            "--event",
            EVENT,
            "--run-id",
            "RID",
            "--role",
            "evaluator",
            "--actor",
            "claude-judge",
            "--stamped-at",
            "2026-08-01T00:00:00Z",
            "--pipeline-sha",
            "sha-abc",
        ],
    )

    assert result.exit_code == 0, result.output
    stamped = json.loads(graded.read_text())
    # granted=1 against a denial, and (0.7 - 0)**2 from the committed pair.
    assert stamped["correct"] == 0
    assert stamped["brier_score"] == pytest.approx(0.49)
    assert stamped["segment_base_rate"] is None
    assert stamped["brier_skill_score"] is None
    assert stamped["base_rate_basis"] is None
    assert "brier_score 0.09" in result.output
    # The stage registers no rate, so the stamp looks for no statpack.
    assert "statpack" not in result.output
