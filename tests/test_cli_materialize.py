from datetime import datetime
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import Disposition, Engine, PredictableEvent, Prediction
from fedcourtsai.serialize import read_model, write_json
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _write_prediction(data_root: Path, court: str, docket: int, event: str) -> None:
    ep = CasePaths(data_root, court, docket).event(event)
    write_json(
        ep.prediction("claude-baseline", "2026-06-28T00-00-00Z"),
        Prediction(
            case_id=f"{court}/{docket}",
            event_id=event,
            predictor_id="claude-baseline",
            engine=Engine.claude_code,
            run_id="2026-06-28T00-00-00Z",
            created_at=datetime(2026, 6, 28),
            input_snapshot="record/snapshots/2026-06-28.json",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
        ),
    )


def test_materialize_event_writes_event_yaml_from_corpus(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(
        app,
        [
            "materialize-event",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-petition-disposition",
        ],
    )

    assert result.exit_code == 0, result.output
    dest = (
        CasePaths(fixture_corpus.data_root, "scotus", 305)
        .event("evt-petition-disposition")
        .event_file
    )
    assert dest.is_file()
    event = read_model(dest, PredictableEvent)
    assert event.event_id == "evt-petition-disposition"
    assert event.case_id == "scotus/305"
    assert event.kind == "petition"
    assert event.resolved is False


def test_materialize_event_honors_explicit_out(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    out = tmp_path / "scratch" / "event.yaml"
    result = runner.invoke(
        app,
        [
            "materialize-event",
            "--court",
            "ca9",
            "--docket",
            "101",
            "--event",
            "evt-appeal-disposition",
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0, result.output
    assert read_model(out, PredictableEvent).event_id == "evt-appeal-disposition"


def test_materialize_event_missing_event_exits_nonzero(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(
        app,
        [
            "materialize-event",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-does-not-exist",
        ],
    )

    assert result.exit_code == 1
    assert "No event" in result.output


def test_materialized_event_lets_a_prediction_pass_validate(fixture_corpus: FixtureCorpus) -> None:
    # Regression: a corpus-discovered event has no event.yaml, so a prediction
    # committed beside it is an orphan the offline `validate` gate rejects (the
    # failure that skipped every predict PR). Materializing the event first makes
    # the same ledger validate clean.
    data_root = fixture_corpus.data_root
    _write_prediction(data_root, "scotus", 305, "evt-petition-disposition")

    orphaned = runner.invoke(app, ["validate", str(data_root)])
    assert orphaned.exit_code == 1
    assert "ORPHAN" in orphaned.output

    materialized = runner.invoke(
        app,
        [
            "materialize-event",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-petition-disposition",
        ],
    )
    assert materialized.exit_code == 0, materialized.output

    fixed = runner.invoke(app, ["validate", str(data_root)])
    assert fixed.exit_code == 0, fixed.output
