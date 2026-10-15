"""`record-usage --pre-mint-poll-file` / `--post-run-poll-file`: the bracket reaches usage.json."""

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


def _poll(polled_at: str, state: str) -> dict[str, str | None]:
    return {"polled_at": polled_at, "docket_number": "26A477", "state": state, "reason": None}


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
    poll.write_text(json.dumps(_poll("2026-10-14T15:50:00Z", "open")))

    result = runner.invoke(app, [*_record(None), "--pre-mint-poll-file", str(poll)])

    assert result.exit_code == 0, result.output
    recorded = _usage(_data_root).pre_mint_poll
    assert recorded is not None
    assert recorded.state == "open"
    assert recorded.docket_number == "26A477"
    assert recorded.polled_at.isoformat() == "2026-10-14T15:50:00+00:00"


def test_both_polls_bracket_the_run_on_the_usage_record(_data_root: Path, tmp_path: Path) -> None:
    pre, post = tmp_path / "pre.json", tmp_path / "post.json"
    pre.write_text(json.dumps(_poll("2026-10-14T15:50:00Z", "open")))
    post.write_text(json.dumps(_poll("2026-10-14T16:10:00Z", "open")))

    result = runner.invoke(
        app,
        [*_record(None), "--pre-mint-poll-file", str(pre), "--post-run-poll-file", str(post)],
    )

    assert result.exit_code == 0, result.output
    usage = _usage(_data_root)
    assert usage.pre_mint_poll is not None and usage.post_run_poll is not None
    assert usage.pre_mint_poll.polled_at < usage.post_run_poll.polled_at


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
    usage = _usage(_data_root)
    assert usage.pre_mint_poll is None
    assert usage.post_run_poll is None
