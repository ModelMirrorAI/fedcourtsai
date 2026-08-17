"""Harness-side retrieval capture from the engines' own transcripts."""

from __future__ import annotations

import base64
import json
import random
import time
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.retrieval import (
    carries_redaction,
    parse_claude_retrieval,
    parse_codex_retrieval,
    parse_gemini_retrieval,
)
from fedcourtsai.schemas import RetrievalCall, RetrievalLog
from fedcourtsai.tool_usage import normalize_call
from tests.conftest import FixtureCorpus

runner = CliRunner()

# A synthetic stand-in for a Fernet token, never a real credential: the v1
# version+timestamp header then base64url ciphertext. Seeded from random bytes
# rather than a repeated pattern, because capture-time redaction confirms the
# run's entropy before rewriting it — a patterned blob is prose to the
# redactor, which is the whole point of the confirmation.
_FERNET = "gAAAAAB" + base64.urlsafe_b64encode(
    random.Random(20260804).randbytes(360)
).decode().rstrip("=")


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
    assert call.result_capture == "captured"


def test_claude_transcript_missing_or_garbage_is_empty(tmp_path: Path) -> None:
    assert parse_claude_retrieval(tmp_path / "absent.json") == []
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    assert parse_claude_retrieval(bad) == []


def test_claude_empty_result_is_captured_and_a_missing_one_is_not(tmp_path: Path) -> None:
    """The distinction the marker exists for, which the digests cannot make.

    Both rows end with a null ``result_digest``: one searched and got an empty
    payload back, the other's result never reached the transcript at all. A
    grader reading only the digest scores them identically and credits the
    second with having surfaced nothing.
    """
    transcript = [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "id": "toolu_1", "name": "search", "input": {"q": "a"}},
                    {"type": "tool_use", "id": "toolu_2", "name": "search", "input": {"q": "b"}},
                ]
            },
        },
        {
            "type": "user",
            # An answered call whose answer was empty — captured, digest null.
            "message": {"content": [{"type": "tool_result", "tool_use_id": "toolu_1"}]},
        },
    ]
    path = tmp_path / "execution.json"
    path.write_text(json.dumps(transcript))
    calls = parse_claude_retrieval(path)
    assert [call.result_capture for call in calls] == ["captured", "unobserved"]
    assert [call.result_digest for call in calls] == [None, None]


def test_claude_failed_result_is_captured_and_an_id_less_call_is_not(tmp_path: Path) -> None:
    # Both are capture-side facts about the pairing, not about what a tool
    # found: a call that errored was answered and is captured, while a call the
    # engine logged with no id has nothing an answer could pair against.
    transcript = [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "id": "toolu_1", "name": "search", "input": {"q": "a"}},
                    {"type": "tool_use", "name": "search", "input": {"q": "b"}},
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
                        "is_error": True,
                        "content": "upstream 502",
                    }
                ]
            },
        },
    ]
    path = tmp_path / "execution.json"
    path.write_text(json.dumps(transcript))
    calls = parse_claude_retrieval(path)
    assert [call.result_capture for call in calls] == ["captured", "unobserved"]


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
    assert calls[0].result_capture == "captured"


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
    # No call_id to pair an output against, and none is ever emitted: the row
    # says what was asked and cannot say what came back.
    assert calls[0].result_capture == "unobserved"


def test_codex_empty_output_is_captured_and_an_unanswered_call_is_not(tmp_path: Path) -> None:
    # Same pairing rule as the Claude transcript: the output *item*, not its
    # content, is what "captured" asserts. A call the rollout never answered
    # (the engine died mid-turn, say) is unobserved.
    rollout = tmp_path / "sessions" / "2026" / "07" / "10" / "rollout-2026-07-10T12-00-00.jsonl"
    rollout.parent.mkdir(parents=True)
    lines = [
        {
            "type": "response_item",
            "payload": {"type": "function_call", "name": "shell", "call_id": "c1", "input": "{}"},
        },
        {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "c1"}},
        {
            "type": "response_item",
            "payload": {"type": "function_call", "name": "shell", "call_id": "c2", "input": "{}"},
        },
    ]
    rollout.write_text("\n".join(json.dumps(line) for line in lines))
    calls = parse_codex_retrieval(tmp_path / "sessions")
    assert [call.result_capture for call in calls] == ["captured", "unobserved"]
    assert [call.result_digest for call in calls] == [None, None]


def _codex_rollout(tmp_path: Path, *payloads: dict[str, object]) -> Path:
    """A one-session rollout of the given response items; returns its sessions dir."""
    rollout = tmp_path / "sessions" / "2026" / "07" / "10" / "rollout-2026-07-10T12-00-00.jsonl"
    rollout.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        {"timestamp": "2026-07-10T12:00:02Z", "type": "response_item", "payload": payload}
        for payload in payloads
    ]
    rollout.write_text("\n".join(json.dumps(line) for line in lines))
    return tmp_path / "sessions"


def test_codex_mcp_tool_call_pairs_a_separate_output(tmp_path: Path) -> None:
    # The rollout's own MCP spelling, answered by a sibling output item like any
    # other call. This path is unchanged by the inline pairing beside it.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_tool_call",
            "name": "search",
            "server_label": "courtlistener",
            "call_id": "m1",
            "arguments": json.dumps({"q": "qualified immunity"}),
        },
        {
            "type": "mcp_tool_call_output",
            "call_id": "m1",
            "output": '{"count": 2, "dateFiled": "2024-01-02"}',
        },
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.tool == "mcp__courtlistener__search"
    assert call.query == "qualified immunity"
    assert call.result_capture == "captured"
    assert call.result_digest is not None
    assert call.retrieved_doc_date == "2024-01-02"


def test_codex_mcp_call_pairs_the_result_carried_inline(tmp_path: Path) -> None:
    # The Responses API settles an MCP call on the call item — the answer under
    # its own `output`, no `*_output` sibling and no `call_id` to pair one by.
    # Read only by `call_id`, every such row would claim `unobserved` while the
    # transcript held the result.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_call",
            "id": "mcp_1",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"q": "chevron deference"}),
            "output": '{"count": 2, "dateFiled": "2024-01-02"}',
            "error": None,
        },
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.tool == "mcp__courtlistener__search"
    assert call.query == "chevron deference"
    assert call.result_capture == "captured"
    assert call.result_digest is not None
    assert call.retrieved_doc_date == "2024-01-02"


def test_codex_mcp_call_inline_error_is_captured(tmp_path: Path) -> None:
    # A failure that reached the transcript is a captured result: the record
    # says what came back, and what came back was an error.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_call",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"q": "chevron deference"}),
            "output": None,
            "error": "tool call failed: 429 rate limited",
        },
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.result_capture == "captured"
    assert call.result_digest is not None
    assert call.retrieved_doc_date is None


def test_codex_mcp_call_inline_empty_output_is_captured(tmp_path: Path) -> None:
    # The load-bearing half of "presence by value, not truthiness": an empty
    # answer that reached the transcript is captured, and only the marker can
    # say so — its digest is null exactly like an uncaptured call's.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_call",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"q": "chevron deference"}),
            "output": "",
        },
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.result_capture == "captured"
    assert call.result_digest is None


def test_codex_mcp_call_with_no_result_at_all_is_unobserved(tmp_path: Path) -> None:
    # Neither a sibling output nor an inline one: the item never settled, and
    # the row must not borrow the inline path's confidence. Both spellings of
    # "nothing settled" — the fields present and null, and the fields absent.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_call",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"q": "chevron deference"}),
            "output": None,
            "error": None,
        },
        {
            "type": "mcp_call",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"q": "major questions"}),
        },
    )
    calls = parse_codex_retrieval(sessions)
    assert [call.result_capture for call in calls] == ["unobserved", "unobserved"]
    assert [call.result_digest for call in calls] == [None, None]


def test_codex_mcp_call_reads_the_rollout_s_own_field_spellings(tmp_path: Path) -> None:
    # The rollout's record of an MCP call may name the same three things
    # `server` / `tool` / `result` rather than `server_label` / `name` /
    # `output`. Both spellings compose and settle the same way; which one codex
    # actually writes is what a real transcript will say.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_tool_call",
            "tool": "search",
            "server": "courtlistener",
            "arguments": json.dumps({"q": "chevron deference"}),
            "result": '{"count": 2, "dateFiled": "2024-01-02"}',
        },
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.tool == "mcp__courtlistener__search"
    assert normalize_call(call.tool) == "courtlistener.search"
    assert call.result_capture == "captured"
    assert call.result_digest is not None
    assert call.retrieved_doc_date == "2024-01-02"


def test_codex_mcp_sibling_output_outranks_the_inline_field(tmp_path: Path) -> None:
    # The sibling is the pairing wherever it carried anything — an empty string
    # included, which is a captured empty answer and not an absent one.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_tool_call",
            "name": "search",
            "server_label": "courtlistener",
            "call_id": "m1",
            "output": '{"dateFiled": "2024-01-02"}',
        },
        {"type": "mcp_tool_call_output", "call_id": "m1", "output": ""},
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.result_capture == "captured"
    assert call.result_digest is None  # the sibling's empty output, not the inline one
    assert call.retrieved_doc_date is None


def test_codex_mcp_null_sibling_output_defers_to_the_inline_field(tmp_path: Path) -> None:
    # A sibling carrying `null` digests to nothing either way, so reading the
    # item's own result in its place can add a captured result and never
    # overwrite one; the marker is `captured` under both readings.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_tool_call",
            "name": "search",
            "server_label": "courtlistener",
            "call_id": "m1",
            "output": '{"dateFiled": "2024-01-02"}',
        },
        {"type": "mcp_tool_call_output", "call_id": "m1"},
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.result_capture == "captured"
    assert call.result_digest is not None
    assert call.retrieved_doc_date == "2024-01-02"


def test_codex_mcp_name_composes_into_the_rollup_s_mcp_spelling(tmp_path: Path) -> None:
    # The bare `name` an MCP item carries is `search` — indistinguishable from
    # an engine builtin once it is a row. Asserted through the rollup's own
    # normalizer rather than against the string, because what the composition
    # buys is the MCP classification, not the spelling.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_call",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"q": "chevron deference"}),
            "output": "{}",
        },
    )
    (call,) = parse_codex_retrieval(sessions)
    assert normalize_call(call.tool) == "courtlistener.search"
    assert normalize_call("search") is None


def test_codex_custom_tool_call_pairs_its_output(tmp_path: Path) -> None:
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "custom_tool_call",
            "name": "apply_patch",
            "call_id": "t1",
            "input": "*** Begin Patch",
        },
        {"type": "custom_tool_call_output", "call_id": "t1", "output": "patched"},
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.tool == "apply_patch"
    assert call.result_capture == "captured"
    assert call.result_digest is not None


def test_codex_local_shell_call_records_its_command(tmp_path: Path) -> None:
    # No `name` and no `arguments`: the invocation describes itself in `action`,
    # so the row is named by payload type and queried from the command.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "local_shell_call",
            "call_id": "s1",
            "action": {"type": "exec", "command": ["fedcourts", "query", "--court", "scotus"]},
        },
        {"type": "local_shell_call_output", "call_id": "s1", "output": "3 rows"},
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.tool == "local_shell_call"
    assert call.query is not None and "fedcourts" in call.query
    assert call.result_capture == "captured"


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
    # The local exporter logs no result payload, so the whole engine is
    # unobserved — never "returned nothing".
    assert calls[0].result_capture == "unobserved"


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
    # The transcript carries the call and no result block for it, so the
    # written artifact says so rather than leaving a reader to infer it from a
    # null digest.
    assert log["calls"][0]["result_capture"] == "unobserved"
    assert log["result_capture_coverage"] == 0.0


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
    written = json.loads(destination.read_text())
    assert written["calls"] == []
    # No call carries a marker, so there is no rate to report: zero-of-zero is
    # not 0.0, which would claim every call went uncaptured.
    assert written["result_capture_coverage"] is None


def test_codex_transcript_credential_is_redacted_at_capture(tmp_path: Path) -> None:
    # A transcript records whatever a tool call carried. `message` is not a
    # query key, so the whole params blob becomes the slice — which is how a
    # token riding in an engine payload reaches the log.
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
                    "arguments": json.dumps({"message": _FERNET}),
                },
            }
        )
    )
    calls = parse_codex_retrieval(tmp_path / "sessions")
    assert len(calls) == 1
    query = calls[0].query
    assert query is not None
    assert _FERNET[:40] not in query
    assert "[redacted:fernet-token]" in query
    # The params digest still covers the unredacted payload, so the audit trail
    # keeps its identity even though the text is gone.
    assert calls[0].params_digest is not None


def test_codex_inline_mcp_result_is_redacted_at_capture(tmp_path: Path) -> None:
    # The mirror of the separate-output case for the inline path: an MCP item
    # that both asks and answers on one record must give the row no route a
    # credential can ride. The params reach the log as text and are redacted;
    # the result reaches it only as a digest and a date capture, exactly as a
    # sibling output does — the pairing changed, the treatment did not.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_call",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"message": _FERNET}),
            "output": json.dumps({"token": _FERNET, "dateFiled": "2024-01-02"}),
        },
    )
    (call,) = parse_codex_retrieval(sessions)
    assert call.result_capture == "captured"
    assert call.query is not None
    assert _FERNET[:40] not in call.query
    assert "[redacted:fernet-token]" in call.query
    assert carries_redaction(call)
    # Nothing of the inline result survives as text anywhere in the row.
    assert _FERNET[:40] not in call.model_dump_json()
    assert call.result_digest is not None and call.retrieved_doc_date == "2024-01-02"


def test_capture_redacts_a_credential_sitting_past_the_query_cap(tmp_path: Path) -> None:
    # Redaction runs over the whole candidate, not the kept slice: a token
    # beyond the truncation point must not be a token the next payload
    # ordering promotes into the log.
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
                        "input": {"q": "cert petition " + "standing doctrine " * 40 + _FERNET},
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
    transcript = [
        {
            "type": "assistant",
            "timestamp": f"2026-07-10T12:00:01Z {_FERNET}",
            "message": {
                "content": [
                    {"type": "tool_use", "id": "toolu_1", "name": f"tool-{_FERNET}", "input": {}}
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
    transcript = [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "t1",
                        "name": "mcp__courtlistener__search",
                        "input": {"message": _FERNET},
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


def test_record_retrieval_refuses_an_out_of_vocabulary_context_mode(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The context file sits in the agent's workspace, so its mode is trusted
    # only inside the declared vocabulary: anything else falls back to the
    # caller's word instead of reaching the grader.
    provisioned = runner.invoke(app, ["provision-snapshot", "--court", "scotus", "--docket", "305"])
    assert provisioned.exit_code == 0, provisioned.output
    context_path = CasePaths(fixture_corpus.data_root, "scotus", 305).cell_context
    tampered = json.loads(context_path.read_text())
    tampered["mode"] = "definitely-not-a-mode"
    context_path.write_text(json.dumps(tampered))

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
            "--mode",
            "forward",
            "--mode-from-context",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "unknown mode" in result.output
    destination = (
        CasePaths(fixture_corpus.data_root, "scotus", 305)
        .event("evt-petition-disposition")
        .prediction_retrieval_log("gemini-baseline", "20260710T120000Z")
    )
    assert json.loads(destination.read_text())["mode"] == "forward"


def _log(calls: list[RetrievalCall]) -> RetrievalLog:
    """A retrieval log carrying nothing but the calls under test."""
    return RetrievalLog(
        case_id="scotus/305",
        run_id="20260710T120000Z",
        role="predictor",
        actor_id="claude-baseline",
        engine="claude-code",
        calls=calls,
    )


def _captured(count: int) -> list[RetrievalCall]:
    return [RetrievalCall(tool="search", result_capture="captured") for _ in range(count)]


def _unobserved(count: int) -> list[RetrievalCall]:
    return [RetrievalCall(tool="search", result_capture="unobserved") for _ in range(count)]


def test_capture_coverage_is_the_share_of_calls_whose_result_was_seen() -> None:
    assert _log(_captured(1) + _unobserved(3)).result_capture_coverage == 0.25
    assert _log(_captured(2)).result_capture_coverage == 1.0
    # A whole log of provider-side calls: a real rate, and a different fact
    # from "no rate", which is why the null below is not spelled 0.0.
    assert _log(_unobserved(3)).result_capture_coverage == 0.0


def test_capture_coverage_is_null_where_no_call_carries_the_marker() -> None:
    """The committed ledger's shape: rows written before the field existed.

    Recomputing over such a log has to reproduce exactly what the record
    already holds — a null — or reading the ledger would restate it.
    """
    assert _log([]).result_capture_coverage is None
    legacy = _log([RetrievalCall(tool="search"), RetrievalCall(tool="read_file")])
    assert legacy.result_capture_coverage is None
    # Mixed: only marker-carrying rows can be the denominator, because a legacy
    # row is capture-unknown rather than a capture failure.
    mixed = _log([*_captured(1), RetrievalCall(tool="read_file")])
    assert mixed.result_capture_coverage == 1.0


def test_capture_coverage_follows_the_calls_rather_than_a_writers_claim() -> None:
    # Derived, so the rate and the rows cannot disagree in a committed artifact.
    asserted = RetrievalLog(
        case_id="scotus/305",
        run_id="20260710T120000Z",
        role="predictor",
        actor_id="claude-baseline",
        engine="claude-code",
        calls=_unobserved(1),
        result_capture_coverage=1.0,
    )
    assert asserted.result_capture_coverage == 0.0


def test_capture_marker_round_trips_through_the_schema() -> None:
    original = _log(_captured(1) + _unobserved(1))
    payload = json.loads(original.model_dump_json())
    assert payload["calls"][0]["result_capture"] == "captured"
    assert payload["calls"][1]["result_capture"] == "unobserved"
    assert payload["result_capture_coverage"] == 0.5
    assert RetrievalLog.model_validate(payload) == original
    # A record written before the field existed still validates, and reads as
    # capture-unknown rather than as a call whose result went uncaptured.
    legacy = {key: value for key, value in payload.items() if key != "result_capture_coverage"}
    legacy["calls"] = [{"tool": "search"}]
    restored = RetrievalLog.model_validate(legacy)
    assert restored.calls[0].result_capture is None
    assert restored.result_capture_coverage is None


# --- the per-call result condition ---------------------------------------------


def _claude_result_transcript(payload: object, *, is_error: bool = False) -> list[object]:
    """A one-call Claude transcript whose ``tool_result`` carries ``payload``."""
    result: dict[str, object] = {
        "type": "tool_result",
        "tool_use_id": "toolu_1",
        "content": payload,
    }
    if is_error:
        result["is_error"] = True
    return [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_1",
                        "name": "mcp__courtlistener__search",
                        "input": {"q": "chevron deference"},
                    }
                ]
            },
        },
        {"type": "user", "message": {"content": [result]}},
    ]


def _claude_status(tmp_path: Path, payload: object, *, is_error: bool = False) -> RetrievalCall:
    path = tmp_path / "execution.json"
    path.write_text(json.dumps(_claude_result_transcript(payload, is_error=is_error)))
    (call,) = parse_claude_retrieval(path)
    return call


def test_a_throttled_claude_result_is_marked_and_still_digested(tmp_path: Path) -> None:
    # The shape the pinned CourtListener MCP server renders an upstream 429 as.
    # That evidence lives only in the payload, which the row digests away one
    # line later, so the marker is the last place a starved run stays legible —
    # and the digest is untouched, because this reads the result, not replaces it.
    call = _claude_status(
        tmp_path,
        [
            {
                "type": "text",
                "text": (
                    "Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled.'}. "
                    "For higher rate limits, you can upgrade your membership at "
                    "https://donate.free.law/forms/membership"
                ),
            }
        ],
        is_error=True,
    )
    # Throttled outranks the engine's own error flag: a 429 arrives *as* an
    # error, and which error it is, is the whole point of the field.
    assert call.result_status == "throttled"
    assert call.result_capture == "captured"
    assert call.result_digest is not None


def test_the_citation_tools_partial_throttle_note_is_marked_too(tmp_path: Path) -> None:
    # A result the quota cut short rather than refused outright: the call came
    # back with rows, and the cell still did not get what it asked for.
    call = _claude_status(
        tmp_path,
        "Rate limited by the upstream API (retry in ~41s). Call `resume_citation_analysis`.",
    )
    assert call.result_status == "throttled"


def test_an_ordinary_result_is_ok_and_a_us_reports_429_is_not_a_throttle(
    tmp_path: Path,
) -> None:
    # The predicate is phrase-anchored precisely because what it scans is
    # retrieved legal content, where 429 is an everyday reporter volume. A bare
    # number must never invent starvation in a run that had none.
    call = _claude_status(
        tmp_path,
        [{"type": "text", "text": '{"citation": "429 U.S. 274", "dateFiled": "1977-01-11"}'}],
    )
    assert call.result_status == "ok"
    assert call.retrieved_doc_date == "1977-01-11"


def test_an_engine_marked_failure_is_an_error_not_an_ok(tmp_path: Path) -> None:
    # `ok` claims only "captured, unmarked, unthrottled", so a failure the
    # engine itself flagged must not land there.
    assert _claude_status(tmp_path, "upstream 502", is_error=True).result_status == "error"


def test_an_unanswered_claude_call_has_no_condition_to_read(tmp_path: Path) -> None:
    transcript = [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "id": "toolu_1", "name": "search", "input": {"q": "a"}}
                ]
            },
        }
    ]
    path = tmp_path / "execution.json"
    path.write_text(json.dumps(transcript))
    (call,) = parse_claude_retrieval(path)
    assert (call.result_capture, call.result_status) == ("unobserved", "unobserved")


def test_a_codex_inline_mcp_error_reads_its_condition_from_the_field(tmp_path: Path) -> None:
    # The Codex counterpart of `is_error`: the item's own `error` field is the
    # engine's word that this came back a failure, so no text sniffing is needed
    # to tell it from an `output` that merely reads badly.
    sessions = _codex_rollout(
        tmp_path,
        {
            "type": "mcp_call",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"q": "chevron deference"}),
            "error": "tool call failed: upstream timeout",
        },
        {
            "type": "mcp_call",
            "call_id": "call_2",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"q": "major questions"}),
            "error": "Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled.'}",
        },
        {
            "type": "mcp_call",
            "call_id": "call_3",
            "name": "search",
            "server_label": "courtlistener",
            "arguments": json.dumps({"q": "standing"}),
            "output": '{"results": [], "count": 0}',
        },
    )
    assert [call.result_status for call in parse_codex_retrieval(sessions)] == [
        "error",
        "throttled",
        "ok",
    ]


def test_every_gemini_call_is_condition_blind(tmp_path: Path) -> None:
    # Not "no throttle" — no observation. The local exporter logs the
    # invocation and nothing of what came back, so this engine can never be
    # seen being starved.
    telemetry = tmp_path / "telemetry.log"
    telemetry.write_text(
        json.dumps(
            {
                "attributes": {
                    "event.name": "gemini_cli.tool_call",
                    "function_name": "mcp_cl_search",
                    "function_args": {"q": "chevron"},
                    "event.timestamp": "2026-07-10T12:00:01Z",
                }
            }
        )
    )
    (call,) = parse_gemini_retrieval(telemetry)
    assert (call.result_capture, call.result_status) == ("unobserved", "unobserved")


def test_the_two_result_markers_may_not_disagree_about_capture() -> None:
    # One fact read twice: a condition is legible exactly when a result was
    # captured, so a row claiming otherwise means the parser is broken.
    with pytest.raises(ValidationError, match="disagree about whether"):
        RetrievalCall(tool="search", result_capture="unobserved", result_status="ok")
    with pytest.raises(ValidationError, match="disagree about whether"):
        RetrievalCall(tool="search", result_capture="captured", result_status="unobserved")
    # A null in either field is the legacy record's capture-unknown, which
    # constrains nothing.
    assert RetrievalCall(tool="search", result_status="ok").result_capture is None


def _throttled(count: int) -> list[RetrievalCall]:
    return [
        RetrievalCall(tool="search", result_capture="captured", result_status="throttled")
        for _ in range(count)
    ]


def _ok(count: int) -> list[RetrievalCall]:
    return [
        RetrievalCall(tool="search", result_capture="captured", result_status="ok")
        for _ in range(count)
    ]


def test_the_log_counts_throttles_over_the_calls_it_could_read() -> None:
    assert _log(_throttled(2) + _ok(3)).throttled_calls == 2
    # A real zero, and the stronger claim: results were legible, none was a throttle.
    assert _log(_ok(3)).throttled_calls == 0


def test_a_condition_blind_log_reports_no_throttle_count_at_all() -> None:
    # The distinction the whole field turns on. A Gemini cell's every result is
    # unobserved, so a 0 here would assert a clean run out of a blind one.
    blind = _log(
        [
            RetrievalCall(tool="search", result_capture="unobserved", result_status="unobserved")
            for _ in range(4)
        ]
    )
    assert blind.throttled_calls is None
    assert blind.result_capture_coverage == 0.0
    # As are an empty log and one written before the field existed.
    assert _log([]).throttled_calls is None
    assert _log([RetrievalCall(tool="search")]).throttled_calls is None


def test_the_throttle_count_follows_the_calls_rather_than_a_writers_claim() -> None:
    asserted = RetrievalLog(
        case_id="scotus/305",
        run_id="20260710T120000Z",
        role="predictor",
        actor_id="claude-baseline",
        engine="claude-code",
        calls=_ok(2),
        throttled_calls=7,
    )
    assert asserted.throttled_calls == 0


def test_the_condition_marker_round_trips_through_the_schema() -> None:
    original = _log(_throttled(1) + _ok(1))
    payload = json.loads(original.model_dump_json())
    assert [call["result_status"] for call in payload["calls"]] == ["throttled", "ok"]
    assert payload["throttled_calls"] == 1
    assert RetrievalLog.model_validate(payload) == original
    # A record written before the field existed still validates and reads as
    # condition-unknown rather than as a cell nothing ever turned away.
    legacy = {key: value for key, value in payload.items() if key != "throttled_calls"}
    legacy["calls"] = [{"tool": "search", "result_capture": "captured"}]
    restored = RetrievalLog.model_validate(legacy)
    assert restored.calls[0].result_status is None
    assert restored.throttled_calls is None
