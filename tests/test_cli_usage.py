"""End-to-end coverage of `fedcourts record-usage` and `usage-summary`."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import ModelUsage
from fedcourtsai.serialize import read_model
from fedcourtsai.store import iter_usage

runner = CliRunner()


@pytest.fixture(autouse=True)
def _data_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    return tmp_path / "data"


def test_record_predict_usage_from_explicit_tokens(
    _data_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_SHA", "ci-checkout-sha")
    result = runner.invoke(
        app,
        [
            "record-usage",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-motion-stay",
            "--run-id",
            "20260624T103000Z",
            "--engine",
            "claude-code",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
            "--input-tokens",
            "150000",
            "--output-tokens",
            "8000",
        ],
    )
    assert result.exit_code == 0, result.output
    path = (
        CasePaths(_data_root, "ca9", 123)
        .event("evt-motion-stay")
        .prediction_usage("claude-baseline", "20260624T103000Z")
    )
    usage = read_model(path, ModelUsage)
    assert usage.model == "claude-fable-5"  # engine default applied
    assert usage.input_tokens == 150_000
    # 150K fresh input + 8K output at claude-fable-5's $10/$50 = $1.90.
    assert usage.estimated_cost_usd == pytest.approx(1.90)
    # created_at was derived from the run id timestamp.
    assert usage.created_at.isoformat() == "2026-06-24T10:30:00+00:00"
    # Provenance resolved ambiently from the Actions checkout env.
    assert usage.pipeline_sha == "ci-checkout-sha"


def test_record_usage_stamps_the_explicit_pipeline_sha(_data_root: Path) -> None:
    result = runner.invoke(
        app,
        [
            "record-usage",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-motion-stay",
            "--run-id",
            "20260624T103000Z",
            "--engine",
            "claude-code",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
            "--input-tokens",
            "1000",
            "--output-tokens",
            "10",
            "--pipeline-sha",
            "feedc0ffee",
        ],
    )
    assert result.exit_code == 0, result.output
    path = (
        CasePaths(_data_root, "ca9", 123)
        .event("evt-motion-stay")
        .prediction_usage("claude-baseline", "20260624T103000Z")
    )
    assert read_model(path, ModelUsage).pipeline_sha == "feedc0ffee"


def test_record_evaluate_usage_uses_evaluator_path(_data_root: Path) -> None:
    result = runner.invoke(
        app,
        [
            "record-usage",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-motion-stay",
            "--run-id",
            "20260624T110000Z",
            "--engine",
            "codex",
            "--role",
            "evaluator",
            "--actor",
            "codex-judge",
            "--input-tokens",
            "100000",
            "--output-tokens",
            "5000",
        ],
    )
    assert result.exit_code == 0, result.output
    path = (
        CasePaths(_data_root, "ca9", 123)
        .event("evt-motion-stay")
        .evaluation_usage("codex-judge", "20260624T110000Z")
    )
    usage = read_model(path, ModelUsage)
    assert usage.model == "gpt-5.6-sol"
    assert usage.actor_id == "codex-judge"


def test_record_usage_reads_claude_execution_file(_data_root: Path, tmp_path: Path) -> None:
    log = tmp_path / "execution.json"
    log.write_text(
        json.dumps(
            [
                {
                    "type": "result",
                    "usage": {
                        "input_tokens": 120_000,
                        "output_tokens": 6_000,
                        "cache_read_input_tokens": 30_000,
                    },
                }
            ]
        )
    )
    result = runner.invoke(
        app,
        [
            "record-usage",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-motion-stay",
            "--run-id",
            "20260624T103000Z",
            "--engine",
            "claude-code",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
            "--claude-execution-file",
            str(log),
        ],
    )
    assert result.exit_code == 0, result.output
    usage = iter_usage(_data_root)[0]
    assert usage.input_tokens == 120_000
    assert usage.cache_read_input_tokens == 30_000


def test_record_usage_reads_gemini_telemetry_file(_data_root: Path, tmp_path: Path) -> None:
    log = tmp_path / "telemetry.log"
    log.write_text(
        json.dumps(
            {
                "name": "gemini_cli.api_response",
                "model": "gemini-3.5-flash",
                "input_token_count": 90_000,
                "cached_content_token_count": 20_000,
                "output_token_count": 4_000,
                "thoughts_token_count": 1_000,
            }
        )
    )
    result = runner.invoke(
        app,
        [
            "record-usage",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-motion-stay",
            "--run-id",
            "20260624T103000Z",
            "--engine",
            "gemini",
            "--role",
            "predictor",
            "--actor",
            "gemini-baseline",
            "--gemini-telemetry-file",
            str(log),
        ],
    )
    assert result.exit_code == 0, result.output
    usage = iter_usage(_data_root)[0]
    assert usage.engine == "gemini"
    assert usage.model == "gemini-3.5-flash"  # engine default applied
    assert usage.input_tokens == 70_000  # 90k - 20k cached
    assert usage.cache_read_input_tokens == 20_000
    assert usage.output_tokens == 5_000  # 4k + 1k thoughts


def test_record_usage_no_tokens_is_non_fatal_and_writes_nothing(_data_root: Path) -> None:
    result = runner.invoke(
        app,
        [
            "record-usage",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-motion-stay",
            "--run-id",
            "20260624T103000Z",
            "--engine",
            "claude-code",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
        ],
    )
    assert result.exit_code == 3
    assert iter_usage(_data_root) == []


def test_recorded_usage_validates(_data_root: Path) -> None:
    runner.invoke(
        app,
        [
            "record-usage",
            "--court",
            "ca9",
            "--docket",
            "123",
            "--event",
            "evt-motion-stay",
            "--run-id",
            "20260624T103000Z",
            "--engine",
            "claude-code",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
            "--input-tokens",
            "1000",
            "--output-tokens",
            "100",
        ],
    )
    result = runner.invoke(app, ["validate", str(_data_root)])
    assert result.exit_code == 0, result.output


def test_usage_summary_aggregates(_data_root: Path) -> None:
    for run_id, out in (("20260624T100000Z", "8000"), ("20260624T110000Z", "4000")):
        runner.invoke(
            app,
            [
                "record-usage",
                "--court",
                "ca9",
                "--docket",
                "123",
                "--event",
                "evt-motion-stay",
                "--run-id",
                run_id,
                "--engine",
                "claude-code",
                "--role",
                "predictor",
                "--actor",
                "claude-baseline",
                "--input-tokens",
                "100000",
                "--output-tokens",
                out,
            ],
        )
    result = runner.invoke(app, ["usage-summary"])
    assert result.exit_code == 0, result.output
    summary = json.loads(result.output)
    assert summary["overall"]["runs"] == 2
    actor = summary["by_actor"]["claude-baseline"]
    assert actor["runs"] == 2
    assert actor["role"] == "predictor"
    assert actor["mean_cost_usd_per_run"] == pytest.approx(actor["estimated_cost_usd"] / 2)
