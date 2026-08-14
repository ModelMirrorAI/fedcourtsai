"""Harness-side retrieval capture from the engines' own transcripts."""

from __future__ import annotations

import json
import time
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.retrieval import (
    carries_redaction,
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


def test_codex_rollout_captures_hosted_web_search(tmp_path: Path) -> None:
    # The hosted search runs provider-side, so it carries no name, no
    # arguments and no call_id — only an `action`. The leakage grading reads
    # this log, so a search that never lands here is a search nobody can see.
    rollout = tmp_path / "sessions" / "2026" / "07" / "10" / "rollout-2026-07-10T12-00-00.jsonl"
    rollout.parent.mkdir(parents=True)
    lines = [
        {
            "timestamp": "2026-07-10T12:00:05Z",
            "type": "response_item",
            "payload": {
                "id": "ws_1",
                "type": "web_search_call",
                "status": "completed",
                "action": {"type": "search", "query": "cert granted Smith v Jones"},
            },
        },
    ]
    rollout.write_text("\n".join(json.dumps(line) for line in lines))
    calls = parse_codex_retrieval(tmp_path / "sessions")
    assert len(calls) == 1
    assert calls[0].tool == "web_search_call"
    assert calls[0].query == "cert granted Smith v Jones"
    assert calls[0].timestamp == "2026-07-10T12:00:05Z"


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


def test_gemini_telemetry_ignores_tool_call_metric_points(tmp_path: Path) -> None:
    # The CLI aims its log AND metric exporters at one outfile, and the tool-call
    # metric's attributes carry `function_name` with no args, no event.name, and
    # no timestamp — re-exported cumulatively every ~10s. Only the real log
    # record counts; the metric points must not become phantom retrievals (they
    # once made up ~90% of a committed log and, sorting first on a null
    # timestamp, could push real calls past the cap).
    telemetry = tmp_path / "telemetry.log"
    real = {
        "attributes": [
            {"key": "event.name", "value": {"stringValue": "gemini_cli.tool_call"}},
            {"key": "event.timestamp", "value": {"stringValue": "2026-07-16T07:35:00Z"}},
            {"key": "function_name", "value": {"stringValue": "run_shell_command"}},
            {"key": "function_args", "value": {"stringValue": '{"command": "fedcourts query"}'}},
        ]
    }
    metric_point = {
        "attributes": [
            {"key": "function_name", "value": {"stringValue": "run_shell_command"}},
            {"key": "success", "value": {"boolValue": True}},
        ]
    }
    events = [real] + [metric_point] * 12  # 12 cumulative re-export flushes
    telemetry.write_text("\n".join(json.dumps(event) for event in events))
    calls = parse_gemini_retrieval(telemetry)
    assert len(calls) == 1  # not 13
    assert calls[0].tool == "run_shell_command"
    assert calls[0].query is not None and calls[0].timestamp == "2026-07-16T07:35:00Z"


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
    assert log["mcp_servers"] == ["courtlistener=courtlistener-api-client[mcp]==1.1.0"]
    assert log["calls"][0]["tool"] == "mcp__courtlistener__search"


def test_record_retrieval_empty_transcript_still_records(fixture_corpus: FixtureCorpus) -> None:
    # "Retrieved nothing" is evidence for the leakage grading, not a skip.
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


def test_codex_transcript_credential_is_redacted_at_capture(tmp_path: Path) -> None:
    # A transcript records whatever a tool call carried. `message` is not a
    # query key, so the whole params blob becomes the slice — which is how a
    # token riding in an engine payload reaches the log.
    fernet = "gAAAAAB" + "Xy7qL2m9Vt4Rz8Wc" * 30  # synthetic, never a real token
    rollout = tmp_path / "sessions" / "2026" / "07" / "10" / "rollout-2026-07-10T12-00-00.jsonl"
    rollout.parent.mkdir(parents=True)
    rollout.write_text(
        json.dumps(
            {
                "timestamp": "2026-07-10T12:00:02Z",
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "mcp__courtlistener__search",
                    "call_id": "c1",
                    "arguments": json.dumps({"message": fernet}),
                },
            }
        )
    )
    calls = parse_codex_retrieval(tmp_path / "sessions")
    assert len(calls) == 1
    query = calls[0].query
    assert query is not None
    assert fernet[:40] not in query
    assert "[redacted:fernet-token]" in query
    # The params digest still covers the unredacted payload, so the audit trail
    # keeps its identity even though the text is gone.
    assert calls[0].params_digest is not None


def test_capture_redacts_a_credential_sitting_past_the_query_cap(tmp_path: Path) -> None:
    # Redaction runs over the whole candidate, not the kept slice: a token
    # beyond the truncation point must not be a token the next payload
    # ordering promotes into the log.
    fernet = "gAAAAAB" + "Xy7qL2m9Vt4Rz8Wc" * 30
    transcript = [
        {
            "type": "assistant",
            "timestamp": "2026-07-10T12:00:01Z",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_1",
                        "name": "mcp__courtlistener__search",
                        "input": {"q": "cert petition " + "standing doctrine " * 40 + fernet},
                    }
                ]
            },
        }
    ]
    execution_file = tmp_path / "execution.json"
    execution_file.write_text(json.dumps(transcript))
    (call,) = parse_claude_retrieval(execution_file)
    assert call.query is not None
    assert len(call.query) <= 500
    assert "gAAAAA" not in call.query


def test_capture_leaves_ordinary_query_text_intact(tmp_path: Path) -> None:
    transcript = [
        {
            "type": "assistant",
            "timestamp": "2026-07-10T12:00:01Z",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_1",
                        "name": "mcp__courtlistener__search",
                        "input": {
                            "q": "https://www.courtlistener.com/api/rest/v4/search/"
                            "?q=cited_by%3A12345&type=o&court=scotus"
                        },
                    }
                ]
            },
        }
    ]
    execution_file = tmp_path / "execution.json"
    execution_file.write_text(json.dumps(transcript))
    (call,) = parse_claude_retrieval(execution_file)
    assert call.query == (
        "https://www.courtlistener.com/api/rest/v4/search/?q=cited_by%3A12345&type=o&court=scotus"
    )
    assert call.tool == "mcp__courtlistener__search"


def test_capture_redacts_the_tool_name_and_timestamp(tmp_path: Path) -> None:
    # Every string harvested from a transcript is redacted, not just the query
    # slice: nothing about a transcript guarantees which field a payload lands
    # in, and the log is committed whole.
    blob = "gAAAAAB" + "Xy7qL2m9Vt4Rz8Wc" * 30
    transcript = [
        {
            "type": "assistant",
            "timestamp": f"2026-07-10T12:00:01Z {blob}",
            "message": {
                "content": [
                    {"type": "tool_use", "id": "toolu_1", "name": f"tool-{blob}", "input": {}}
                ]
            },
        }
    ]
    execution_file = tmp_path / "execution.json"
    execution_file.write_text(json.dumps(transcript))
    (call,) = parse_claude_retrieval(execution_file)
    assert call.tool == "tool-[redacted:fernet-token]"
    assert call.timestamp == "2026-07-10T12:00:01Z [redacted:fernet-token]"
    assert carries_redaction(call)


def test_capture_bounds_the_work_a_payload_can_ask_for(tmp_path: Path) -> None:
    # A tool call's arguments are unbounded and agent-influenced (a file write
    # carries its whole body), so redaction reads a fixed window rather than
    # however much the payload offers.
    transcript = [
        {
            "type": "assistant",
            "timestamp": "2026-07-10T12:00:01Z",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_1",
                        "name": "Write",
                        "input": {"content": "-eyJ" * 200_000},
                    }
                ]
            },
        }
    ]
    execution_file = tmp_path / "execution.json"
    execution_file.write_text(json.dumps(transcript))
    started = time.monotonic()
    (call,) = parse_claude_retrieval(execution_file)
    assert time.monotonic() - started < 10
    assert call.query is not None
    assert len(call.query) <= 500


def test_record_retrieval_reports_the_redaction_count(
    fixture_corpus: FixtureCorpus, tmp_path: Path
) -> None:
    blob = "gAAAAAB" + "Xy7qL2m9Vt4Rz8Wc" * 30
    transcript = [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "t1",
                        "name": "mcp__courtlistener__search",
                        "input": {"message": blob},
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
            "--claude-execution-file",
            str(execution),
        ],
    )
    assert result.exit_code == 0, result.output
    # Redaction lets through a run the collect scan would have withheld, so the
    # fact that it fired has to surface somewhere.
    assert "1 redacted" in result.output
    assert "::warning::" in result.output


def test_record_retrieval_takes_its_mode_from_the_cell_context(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The harness-written record, not a workflow constant: provisioning wrote
    # the cell's mode into record/context.json, and --mode-from-context reads
    # it back so the retrieval log cannot assert a mode the cell never had.
    provisioned = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])
    assert provisioned.exit_code == 0, provisioned.output

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
            "--mode-from-context",
        ],
    )

    assert result.exit_code == 0, result.output
    destination = (
        CasePaths(fixture_corpus.data_root, "scotus", 305)
        .event("evt-petition-disposition")
        .prediction_retrieval_log("gemini-baseline", "20260710T120000Z")
    )
    assert json.loads(destination.read_text())["mode"] == "forward"


def test_record_retrieval_records_unknown_mode_when_no_context_was_provisioned(
    fixture_corpus: FixtureCorpus,
) -> None:
    # A refused provisioning leaves no context.json; the log must say the mode
    # is unknown rather than assert forward on a cell that was never one.
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
            "--mode-from-context",
        ],
    )

    assert result.exit_code == 0, result.output
    destination = (
        CasePaths(fixture_corpus.data_root, "scotus", 305)
        .event("evt-petition-disposition")
        .prediction_retrieval_log("gemini-baseline", "20260710T120000Z")
    )
    assert json.loads(destination.read_text())["mode"] is None
