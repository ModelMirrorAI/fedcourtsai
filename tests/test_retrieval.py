"""Harness-side retrieval capture from the engines' own transcripts (#525)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.retrieval import (
    parse_claude_retrieval,
    parse_codex_retrieval,
    parse_gemini_retrieval,
)
from tests.conftest import FixtureCorpus

runner = CliRunner()


def test_claude_transcript_tool_calls_with_results(tmp_path: Path) -> None:
    transcript = [
        {
            "type": "assistant",
            "timestamp": "2026-07-10T12:00:01Z",
            "message": {
                "content": [
                    {"type": "text", "text": "Searching."},
                    {
                        "type": "tool_use",
                        "id": "toolu_1",
                        "name": "mcp__courtlistener__search",
                        "input": {"q": "chevron deference cert petition", "court": "scotus"},
                    },
                ]
            },
        },
        {
            "type": "user",
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_1",
                        "content": [{"type": "text", "text": '{"dateFiled": "2023-05-01"}'}],
                    }
                ]
            },
        },
        {"type": "result", "usage": {"input_tokens": 10, "output_tokens": 5}},
    ]
    path = tmp_path / "execution.json"
    path.write_text(json.dumps(transcript))
    calls = parse_claude_retrieval(path)
    assert len(calls) == 1
    call = calls[0]
    assert call.tool == "mcp__courtlistener__search"
    assert call.query == "chevron deference cert petition"
    assert call.params_digest and call.result_digest
    assert call.retrieved_doc_date == "2023-05-01"
    assert call.timestamp == "2026-07-10T12:00:01Z"


def test_claude_transcript_missing_or_garbage_is_empty(tmp_path: Path) -> None:
    assert parse_claude_retrieval(tmp_path / "absent.json") == []
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    assert parse_claude_retrieval(bad) == []


def test_codex_rollout_function_calls(tmp_path: Path) -> None:
    rollout = tmp_path / "sessions" / "2026" / "07" / "10" / "rollout-2026-07-10T12-00-00.jsonl"
    rollout.parent.mkdir(parents=True)
    lines = [
        {
            "timestamp": "2026-07-10T12:00:02Z",
            "type": "response_item",
            "payload": {
                "type": "function_call",
                "name": "shell",
                "call_id": "c1",
                "arguments": json.dumps({"command": ["fedcourts", "query", "--court", "scotus"]}),
            },
        },
        {
            "type": "response_item",
            "payload": {"type": "function_call_output", "call_id": "c1", "output": "3 rows"},
        },
        {
            "type": "response_item",
            "payload": {"type": "token_count", "info": {"total_token_usage": {}}},
        },
    ]
    rollout.write_text("\n".join(json.dumps(line) for line in lines))
    calls = parse_codex_retrieval(tmp_path / "sessions")
    assert len(calls) == 1
    assert calls[0].tool == "shell"
    assert calls[0].result_digest is not None
    assert calls[0].timestamp == "2026-07-10T12:00:02Z"


def test_gemini_telemetry_tool_calls(tmp_path: Path) -> None:
    telemetry = tmp_path / "telemetry.log"
    events = [
        {
            "attributes": [
                {"key": "event.name", "value": {"stringValue": "gemini_cli.tool_call"}},
                {"key": "event.timestamp", "value": {"stringValue": "2026-07-10T12:00:03Z"}},
                {"key": "function_name", "value": {"stringValue": "search"}},
                {"key": "function_args", "value": {"stringValue": '{"q": "qualified immunity"}'}},
            ]
        },
        {"attributes": [{"key": "input_token_count", "value": {"intValue": "10"}}]},
    ]
    telemetry.write_text("\n".join(json.dumps(event) for event in events))
    calls = parse_gemini_retrieval(telemetry)
    assert len(calls) == 1
    assert calls[0].tool == "search"
    assert calls[0].query == "qualified immunity"


def test_record_retrieval_writes_log_with_manifest(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    transcript = [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "t1",
                        "name": "mcp__courtlistener__search",
                        "input": {"q": "x"},
                    }
                ]
            },
        }
    ]
    execution = tmp_path / "execution.json"
    execution.write_text(json.dumps(transcript))
    result = runner.invoke(
        app,
        [
            "record-retrieval",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-petition-disposition",
            "--run-id",
            "20260710T120000Z",
            "--engine",
            "claude-code",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
            "--mode",
            "forward",
            "--claude-execution-file",
            str(execution),
        ],
    )
    assert result.exit_code == 0, result.output
    destination = (
        CasePaths(fixture_corpus.data_root, "scotus", 305)
        .event("evt-petition-disposition")
        .prediction_retrieval_log("claude-baseline", "20260710T120000Z")
    )
    log = json.loads(destination.read_text())
    assert log["mode"] == "forward"
    assert log["mcp_servers"] == ["courtlistener=courtlistener-api-client[mcp]==1.0.0"]
    assert log["calls"][0]["tool"] == "mcp__courtlistener__search"


def test_record_retrieval_empty_transcript_still_records(fixture_corpus: FixtureCorpus) -> None:
    # "Retrieved nothing" is evidence for the #526 evaluator, not a skip.
    result = runner.invoke(
        app,
        [
            "record-retrieval",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-petition-disposition",
            "--run-id",
            "20260710T120000Z",
            "--engine",
            "gemini",
            "--role",
            "predictor",
            "--actor",
            "gemini-baseline",
        ],
    )
    assert result.exit_code == 0, result.output
    destination = (
        CasePaths(fixture_corpus.data_root, "scotus", 305)
        .event("evt-petition-disposition")
        .prediction_retrieval_log("gemini-baseline", "20260710T120000Z")
    )
    assert json.loads(destination.read_text())["calls"] == []
