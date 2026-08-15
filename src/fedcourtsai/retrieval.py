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
- **Codex**: the session rollout JSONL's response items carry ``function_call``
  / ``custom_tool_call`` / ``local_shell_call`` / ``mcp_tool_call`` payloads
  with a ``call_id`` their ``*_output`` items echo. The hosted
  ``web_search_call`` is the exception: it runs provider-side and carries a
  query but no ``call_id`` and no output item, so such a row records what was
  asked and never what came back — a null ``retrieved_doc_date`` there means
  the results were not captured, not that nothing was found.
- **Gemini**: the OpenTelemetry log's ``gemini_cli.tool_call`` events carry
  ``function_name`` / ``function_args`` attributes.

All parsers normalize to :class:`~fedcourtsai.schemas.RetrievalCall` rows.
Long parameters and results are digested (SHA-256, 16 hex chars), with a
truncated human-legible ``query`` slice kept where one is extractable — the
log is an audit trail, not a content mirror. Deliberately tolerant, exactly
like the usage parsers: an unreadable or unrecognized log yields ``[]``,
because capture is instrumentation that must never fail a real run.

A transcript is not trusted text: it records whatever a tool call carried,
including a credential the agent never chose to write. Every string harvested
here therefore passes through
:func:`~fedcourtsai.secretscan.redact_credentials` on its way into a row, and
does so *before* truncation, so a token cannot survive by sitting past the
cut. The log is a committed artifact; it must not be able to carry one.
"""

from __future__ import annotations

import hashlib
import json
import re
from contextlib import suppress
from pathlib import Path
from typing import Any

from .schemas import RetrievalCall
from .secretscan import REDACTION_MARKER_PREFIX, redact_credentials
from .usage import _gemini_attrs, _load_json, _load_json_objects, _newest_rollout

# The human-legible query slice kept (redacted; the rest is digested).
_QUERY_CAP = 500
# How much of a params payload is redacted before that slice is cut. A tool
# call's arguments are unbounded — a file write carries its whole body — and
# scanning all of it per call is work an agent chooses the size of, so the
# redactor sees a fixed window instead. Two orders of magnitude past the cap,
# which is what makes the cut safe: replacements only ever shorten the text,
# and no plausible payload shrinks 16 KiB below 500 chars, so nothing from
# beyond the window can slide into the kept slice.
_REDACT_WINDOW = 16 * 1024
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
RETRIEVAL_CALL_CAP = 500


def _digest(payload: Any) -> str | None:
    """A short stable digest of any JSON-serializable payload, or ``None`` for empty."""
    try:
        text = json.dumps(payload, sort_keys=True, default=str)
    except (TypeError, ValueError):
        text = str(payload)
    if not text or text in ('""', "null", "{}", "[]"):
        return None
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def carries_redaction(call: RetrievalCall) -> bool:
    """Whether capture rewrote credential-shaped text anywhere in this row.

    Reads the marker back out of the fields redaction covers, so the count a
    run reports needs no second channel. Advisory: an agent can type the marker
    into a tool call itself, which inflates the count but cannot suppress it.
    """
    return any(
        REDACTION_MARKER_PREFIX in field
        for field in (call.tool, call.query or "", call.timestamp or "")
    )


def _tool_name(value: Any) -> str:
    """A transcript-harvested tool name, bounded and redacted like any capture."""
    return redact_credentials(str(value)[:_REDACT_WINDOW])


def _text(value: Any) -> str | None:
    """A transcript-harvested scalar as a redacted string, or ``None`` for empty."""
    if not value:
        return None
    return redact_credentials(str(value)[:_REDACT_WINDOW])


def _query_slice(params: Any) -> str | None:
    """The human-legible query portion of a call's params: redacted, then truncated.

    Redaction runs ahead of the cut rather than over the kept slice, so a
    credential cannot survive by sitting past it.
    """
    candidate = _query_candidate(params)
    if not candidate:
        return None
    return redact_credentials(candidate[:_REDACT_WINDOW])[:_QUERY_CAP]


def _query_candidate(params: Any) -> str | None:
    """The untruncated, unredacted query portion of a call's params."""
    if isinstance(params, str):
        return params.strip() or None
    if isinstance(params, dict):
        for key in _QUERY_KEYS:
            value = params.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        try:
            return json.dumps(params, sort_keys=True, default=str)
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
                    tool=_tool_name(block["name"]),
                    query=_query_slice(params),
                    params_digest=_digest(params),
                    timestamp=_text(timestamp),
                    result_digest=_digest(result),
                    # A date the `\d{4}-\d{2}-\d{2}` capture produced; it has no
                    # room to carry anything else, so it needs no redaction.
                    retrieved_doc_date=_doc_date(result) if result is not None else None,
                )
            )
    return calls[:RETRIEVAL_CALL_CAP]


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
# `web_search_call` is the hosted search the engine runs provider-side: it is a
# retrieval channel like any other, so the leakage grading has to see it.
_CODEX_CALL_TYPES = (
    "function_call",
    "custom_tool_call",
    "local_shell_call",
    "mcp_tool_call",
    "web_search_call",
)
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
        # A hosted `web_search_call` carries neither `arguments` nor `input`,
        # and no `call_id` to pair an output against; its query sits under
        # `action`, which `_query_slice` reads through the shared `query` key.
        # `local_shell_call` also describes itself in `action`, so it records
        # its command here for the same reason a shell `function_call` does.
        params = _maybe_json(payload.get("arguments", payload.get("input", payload.get("action"))))
        result = outputs.get(str(payload.get("call_id", "")))
        calls.append(
            RetrievalCall(
                tool=_tool_name(payload.get("name") or payload.get("tool") or payload["type"]),
                query=_query_slice(params),
                params_digest=_digest(params),
                timestamp=_text(record.get("timestamp")),
                result_digest=_digest(result),
                retrieved_doc_date=_doc_date(result) if result is not None else None,
            )
        )
    return calls[:RETRIEVAL_CALL_CAP]


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

    Each ``gemini_cli.tool_call`` **log record** carries the invocation's
    ``function_name`` / ``function_args``; the local exporter logs no result
    payload, so result digests stay ``None`` for this engine.

    The CLI points its span, log, **and metric** exporters at the same
    ``outfile``, so the file interleaves log records with metric data points —
    and ``logToolCall`` records a tool-call *metric* whose attributes carry
    ``function_name`` but no args, no ``event.name``, and no timestamp. Those
    points are re-exported **cumulatively every 10s** for the whole session, so
    admitting them (this once accepted any node with a ``function_name`` and no
    event name) both drowned the log — ~90% of rows, one per distinct tool per
    flush — and, because a null timestamp sorts first, pushed real calls past
    ``RETRIEVAL_CALL_CAP``. Requiring the tool-call event name keeps only the log
    records; a real one always carries it.
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
        if name and event_name.endswith("tool_call"):
            params = _maybe_json(attrs.get("function_args") or node.get("function_args"))
            timestamp = attrs.get("event.timestamp") or node.get("event.timestamp")
            calls.append(
                RetrievalCall(
                    tool=_tool_name(name),
                    query=_query_slice(params),
                    params_digest=_digest(params),
                    timestamp=_text(timestamp),
                )
            )
            continue
        stack.extend(node.values())
    # The stack walk visits nested containers in reverse; restore log order by
    # timestamp where present (stable for ties/absent stamps).
    calls.sort(key=lambda call: call.timestamp or "")
    return calls[:RETRIEVAL_CALL_CAP]
