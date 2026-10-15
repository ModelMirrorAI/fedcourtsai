"""`record-usage --pre-mint-poll-file`: the poll provisioning took reaches usage.json."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import ModelUsage
from fedcourtsai.serialize import read_model
from tests.test_cli_usage import _record

runner = CliRunner()


@pytest.fixture(autouse=True)
def _data_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    return tmp_path / "data"


def _usage(data_root: Path) -> ModelUsage:
    path = (
        CasePaths(data_root, "ca9", 123)
        .event("evt-motion-stay")
        .prediction_usage("claude-baseline", "20260624T103000Z")
    )
    return read_model(path, ModelUsage)


def test_the_pre_mint_poll_is_recorded_on_the_usage_record(
    _data_root: Path, tmp_path: Path
) -> None:
    poll = tmp_path / "poll.json"
    poll.write_text(
        json.dumps({"polled_at": "2026-10-14T15:50:00Z", "state": "open", "reason": None})
    )

    result = runner.invoke(app, [*_record(None), "--pre-mint-poll-file", str(poll)])

    assert result.exit_code == 0, result.output
    recorded = _usage(_data_root).pre_mint_poll
    assert recorded is not None
    assert recorded.state == "open"
    assert recorded.polled_at.isoformat() == "2026-10-14T15:50:00+00:00"


def test_an_unreadable_poll_record_warns_and_records_nothing(
    _data_root: Path, tmp_path: Path
) -> None:
    poll = tmp_path / "poll.json"
    poll.write_text("{not json")

    result = runner.invoke(app, [*_record(None), "--pre-mint-poll-file", str(poll)])

    assert result.exit_code == 0, result.output
    assert "pre-mint poll record unreadable" in result.output
    assert _usage(_data_root).pre_mint_poll is None


def test_a_usage_record_without_a_poll_still_validates(_data_root: Path) -> None:
    result = runner.invoke(app, _record(None))

    assert result.exit_code == 0, result.output
    assert _usage(_data_root).pre_mint_poll is None
