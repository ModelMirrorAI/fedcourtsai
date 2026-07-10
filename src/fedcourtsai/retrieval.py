"""Extract the cell's tool-call transcript from the engines' own run logs.

The retrieval-logging counterpart of :mod:`fedcourtsai.usage`, and the
load-bearing piece of the lean-agentic leakage approach: the log is harvested
from the engine's transcript — **never the agent's word** — so the
cross-evaluator's leakage grading can see what a replay cell actually
retrieved. The three engines
log tool calls in the same places their token usage lives:

- **Claude Code**: the ``execution_file`` transcript's assistant messages carry
  ``tool_use`` content blocks (name + input); the paired ``tool_result`` blocks
  arrive in subsequent user messages, matched by ``tool_use_id``.
- **Codex**: the session rollout JSONL's response items carry
  ``function_call`` / ``custom_tool_call`` / ``mcp_tool_call`` payloads with a
  ``call_id`` their ``*_output`` items echo.
- **Gemini**: the OpenTelemetry log's ``gemini_cli.tool_call`` events carry
  ``function_name`` / ``function_args`` attributes.

All parsers normalize to :class:`~fedcourtsai.schemas.RetrievalCall` rows.
Long parameters and results are digested (SHA-256, 16 hex chars), with a
truncated human-legible ``query`` slice kept where one is extractable — the
log is an audit trail, not a content mirror. Deliberately tolerant, exactly
like the usage parsers: an unreadable or unrecognized log yields ``[]``,
because capture is instrumentation that must never fail a real run.
"""

from __future__ import annotations

import hashlib
import json
import re
from contextlib import suppress
from pathlib import Path
from typing import Any

from .schemas import RetrievalCall
from .usage import _gemini_attrs, _load_json, _load_json_objects, _newest_rollout

# The human-legible query slice kept verbatim (the rest is digested).
_QUERY_CAP = 500
# Keys that carry the query-ish part of a tool's params, most specific first.
_QUERY_KEYS = ("q", "query", "search", "citation", "prompt", "command", "url", "endpoint")
# A document/decision date in a result payload — the leakage grading's timing signal. The
# quotes tolerate a backslash: a result often nests JSON inside a text block,
# so the serialized form the regex scans carries escaped quotes.
_DOC_DATE_RE = re.compile(
    r'\\?"(?:date_?[Ff]iled|date_?[Dd]ecided|decision_?date)\\?"\s*:\s*\\?"(\d{4}-\d{2}-\d{2})\\?"'
)
# Schema cap on calls per log; a longer transcript is truncated head-first
# (the earliest calls are the retrieval-shaped ones worth grading).
_MAX_CALLS = 500


def _digest(payload: Any) -> str | None:
    """A short stable digest of any JSON-serializable payload, or ``None`` for empty."""
    try:
        text = json.dumps(payload, sort_keys=True, default=str)
    except (TypeError, ValueError):
        text = str(payload)
    if not text or text in ('""', "null", "{}", "[]"):
        return None
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _query_slice(params: Any) -> str | None:
    """The human-legible query portion of a call's params, truncated."""
    if isinstance(params, str):
        text = params.strip()
        return text[:_QUERY_CAP] or None
    if isinstance(params, dict):
        for key in _QUERY_KEYS:
            value = params.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()[:_QUERY_CAP]
        try:
            return json.dumps(params, sort_keys=True, default=str)[:_QUERY_CAP]
        except (TypeError, ValueError):
            return None
    return None


def _doc_date(result: Any) -> str | None:
    """The first document/decision date legible in a result payload, if any."""
    try:
        text = json.dumps(result, default=str)
    except (TypeError, ValueError):
        text = str(result)
    match = _DOC_DATE_RE.search(text)
    return match.group(1) if match else None


def parse_claude_retrieval(execution_file: Path) -> list[RetrievalCall]:
    """Tool calls from a Claude Code ``execution_file`` JSON transcript."""
    doc = _load_json(execution_file)
    events = doc if isinstance(doc, list) else [doc] if isinstance(doc, dict) else []
    # First pass: index tool results by the tool_use id they answer.
    results: dict[str, Any] = {}
    for event in events:
        for block in _message_blocks(event):
            if block.get("type") == "tool_result" and block.get("tool_use_id"):
                results[str(block["tool_use_id"])] = block.get("content")
    calls: list[RetrievalCall] = []
    for event in events:
        timestamp = event.get("timestamp") if isinstance(event, dict) else None
        for block in _message_blocks(event):
            if block.get("type") != "tool_use" or not block.get("name"):
                continue
            params = block.get("input")
            result = results.get(str(block.get("id", "")))
            calls.append(
                RetrievalCall(
                    tool=str(block["name"]),
                    query=_query_slice(params),
                    params_digest=_digest(params),
                    timestamp=str(timestamp) if timestamp else None,
                    result_digest=_digest(result),
                    retrieved_doc_date=_doc_date(result) if result is not None else None,
                )
            )
    return calls[:_MAX_CALLS]


def _message_blocks(event: Any) -> list[dict[str, Any]]:
    """The content blocks of a transcript event's message, tolerant of shape."""
    if not isinstance(event, dict):
        return []
    message = event.get("message")
    content = message.get("content") if isinstance(message, dict) else event.get("content")
    if not isinstance(content, list):
        return []
    return [block for block in content if isinstance(block, dict)]


# Codex payload types that represent a tool invocation / its output.
_CODEX_CALL_TYPES = ("function_call", "custom_tool_call", "local_shell_call", "mcp_tool_call")
_CODEX_OUTPUT_SUFFIX = "_output"


def parse_codex_retrieval(sessions_dir: Path) -> list[RetrievalCall]:
    """Tool calls from the newest Codex rollout JSONL under ``sessions_dir``."""
    rollout = _newest_rollout(sessions_dir)
    if rollout is None:
        return []
    records: list[dict[str, Any]] = []
    try:
        for raw in rollout.read_text().splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
    except OSError:
        return []
    outputs: dict[str, Any] = {}
    for record in records:
        payload = _codex_payload(record)
        if payload is None:
            continue
        if str(payload.get("type", "")).endswith(_CODEX_OUTPUT_SUFFIX) and payload.get("call_id"):
            outputs[str(payload["call_id"])] = payload.get("output")
    calls: list[RetrievalCall] = []
    for record in records:
        payload = _codex_payload(record)
        if payload is None or payload.get("type") not in _CODEX_CALL_TYPES:
            continue
        params = _maybe_json(payload.get("arguments", payload.get("input")))
        result = outputs.get(str(payload.get("call_id", "")))
        calls.append(
            RetrievalCall(
                tool=str(payload.get("name") or payload.get("tool") or payload["type"]),
                query=_query_slice(params),
                params_digest=_digest(params),
                timestamp=str(record.get("timestamp")) if record.get("timestamp") else None,
                result_digest=_digest(result),
                retrieved_doc_date=_doc_date(result) if result is not None else None,
            )
        )
    return calls[:_MAX_CALLS]


def _maybe_json(params: Any) -> Any:
    """Decode a JSON-string params payload where the engine serialized it."""
    if isinstance(params, str):
        with suppress(json.JSONDecodeError):
            return json.loads(params)
    return params


def _codex_payload(record: dict[str, Any]) -> dict[str, Any] | None:
    """The response-item payload of a rollout record, wherever Codex nests it."""
    payload = record.get("payload")
    if isinstance(payload, dict):
        inner = payload.get("payload")
        return inner if isinstance(inner, dict) else payload
    return record if "type" in record else None


def parse_gemini_retrieval(telemetry_file: Path) -> list[RetrievalCall]:
    """Tool calls from a Gemini CLI OpenTelemetry ``telemetry.log``.

    Each ``gemini_cli.tool_call`` event carries the invocation's
    ``function_name`` / ``function_args``; the local exporter logs no result
    payload, so result digests stay ``None`` for this engine.
    """
    calls: list[RetrievalCall] = []
    stack: list[Any] = [_load_json_objects(telemetry_file)]
    while stack:
        node = stack.pop()
        if isinstance(node, list):
            stack.extend(node)
            continue
        if not isinstance(node, dict):
            continue
        attrs = _gemini_attrs(node)
        name = attrs.get("function_name") or node.get("function_name")
        event_name = str(attrs.get("event.name") or node.get("event.name") or "")
        if name and (not event_name or event_name.endswith("tool_call")):
            params = _maybe_json(attrs.get("function_args") or node.get("function_args"))
            timestamp = attrs.get("event.timestamp") or node.get("event.timestamp")
            calls.append(
                RetrievalCall(
                    tool=str(name),
                    query=_query_slice(params),
                    params_digest=_digest(params),
                    timestamp=str(timestamp) if timestamp else None,
                )
            )
            continue
        stack.extend(node.values())
    # The stack walk visits nested containers in reverse; restore log order by
    # timestamp where present (stable for ties/absent stamps).
    calls.sort(key=lambda call: call.timestamp or "")
    return calls[:_MAX_CALLS]
