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
  with a ``call_id`` their ``*_output`` items echo. An MCP item is the shape
  that breaks the echo: the Responses API settles it *on the call item*, with
  the answer in the item's own ``output`` (or ``error``) and no ``*_output``
  sibling to pair, so it is paired from the item itself. The hosted
  ``web_search_call`` is the other exception: it runs provider-side and carries
  a query but no ``call_id`` and no output item, so such a row records what was
  asked and never what came back.
- **Gemini**: the OpenTelemetry log's ``gemini_cli.tool_call`` events carry
  ``function_name`` / ``function_args`` attributes, and no result payload at
  all.

All parsers normalize to :class:`~fedcourtsai.schemas.RetrievalCall` rows.
Long parameters and results are digested (SHA-256, 16 hex chars), with a
truncated human-legible ``query`` slice kept where one is extractable — the
log is an audit trail, not a content mirror. Deliberately tolerant, exactly
like the usage parsers: an unreadable or unrecognized log yields ``[]``,
because capture is instrumentation that must never fail a real run.

Every row also states whether its result was seen at all: ``result_capture``
is ``captured`` where the transcript carried the result — as a paired result
item, or on the call item itself for an engine that settles it there — and
``unobserved`` where nothing came back to capture — every Gemini row, a hosted
Codex ``web_search_call``, or any call this pairing rule found no result item
for, which includes one the engine logged without a pairing id and one whose
result sits past a truncated transcript. The digests cannot say it, because a null
``result_digest`` or ``retrieved_doc_date`` is what a captured-empty result
and an uncaptured one both leave behind; without the marker a reader grades
"this call surfaced nothing" over calls whose results were never in the log.

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
            # Membership, not the value: a `tool_result` carrying empty content
            # was still captured, and that is exactly the case the marker
            # exists to separate from one whose result never reached the log.
            call_id = str(block.get("id", ""))
            captured = call_id in results
            result = results.get(call_id)
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
                    result_capture="captured" if captured else "unobserved",
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
# An MCP invocation answers to two type names — the rollout's `mcp_tool_call`
# and the Responses API's `mcp_call` — and under either it is the one call shape
# that carries its own result rather than echoing a `call_id` an output item
# answers.
_CODEX_MCP_CALL_TYPES = ("mcp_tool_call", "mcp_call")
_CODEX_CALL_TYPES = (
    "function_call",
    "custom_tool_call",
    "local_shell_call",
    *_CODEX_MCP_CALL_TYPES,
    "web_search_call",
)
_CODEX_OUTPUT_SUFFIX = "_output"
# Where an MCP call item carries its own settled result, most authoritative
# first: the Responses API's `output` / `error`, then the `result` the rollout's
# own record of the same call may use.
_CODEX_INLINE_RESULT_FIELDS = ("output", "error", "result")


def parse_codex_retrieval(sessions_dir: Path) -> list[RetrievalCall]:
    """Tool calls from the newest Codex rollout JSONL under ``sessions_dir``."""
    rollout = _newest_rollout(sessions_dir)
    if rollout is None:
        return []
    records = _codex_records(rollout)
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
        # Membership, not the value — an empty output item is still a captured
        # result. A hosted `web_search_call` carries no `call_id` at all, so it
        # can never match and lands as `unobserved`, which is the truth about it.
        call_id = str(payload.get("call_id", ""))
        captured = call_id in outputs
        result = outputs.get(call_id)
        # An MCP item settles on itself rather than in a sibling, so where the
        # sibling lookup produced no result, the item's own is the pairing. A
        # sibling that carried anything at all — an empty string included — wins;
        # only a null one, which digests to nothing either way, defers.
        if result is None:
            inline = _codex_inline_result(payload)
            if inline is not None:
                captured, result = True, inline
        calls.append(
            RetrievalCall(
                tool=_tool_name(_codex_tool(payload)),
                query=_query_slice(params),
                params_digest=_digest(params),
                timestamp=_text(record.get("timestamp")),
                result_digest=_digest(result),
                retrieved_doc_date=_doc_date(result) if result is not None else None,
                result_capture="captured" if captured else "unobserved",
            )
        )
    return calls[:RETRIEVAL_CALL_CAP]


def _codex_records(rollout: Path) -> list[dict[str, Any]]:
    """Every JSON object in a rollout JSONL, tolerant of a line that is not one."""
    try:
        lines = rollout.read_text().splitlines()
    except OSError:
        return []
    records: list[dict[str, Any]] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def _codex_inline_result(payload: dict[str, Any]) -> Any:
    """An MCP call item's own settled result, or ``None`` where it holds none.

    The Responses API settles an MCP call **on the call item** — the answer in
    its ``output``, the failure in its ``error``, and no ``*_output`` sibling
    emitted either way — so a walk that only pairs by ``call_id`` reads every
    such row as ``unobserved`` while the transcript held the result. An inline
    ``error`` counts as captured for the same reason a Claude ``is_error``
    result does: the transcript recorded what came back, and what came back was
    a failure. ``result`` is read after both because the rollout's own record of
    an MCP call may name the answer that way, and the two spellings cost one
    lookup to cover jointly. Only MCP shapes are read this way; every other call
    type pairs against its output item.

    A sibling output item still wins: this is consulted only where the pairing
    found none, or found one carrying ``null`` — which digests to nothing, so
    reading the item's own result in its place can add a captured result but
    never overwrite one.

    Presence is by value, not by key: an unsettled item carries these fields as
    ``null`` (or omits them), while an empty string is a real, captured, empty
    answer.
    """
    if payload.get("type") not in _CODEX_MCP_CALL_TYPES:
        return None
    for field in _CODEX_INLINE_RESULT_FIELDS:
        value = payload.get(field)
        if value is not None:
            return value
    return None


def _codex_tool(payload: dict[str, Any]) -> Any:
    """A Codex call item's tool name, in the spelling the rollup normalizes.

    An MCP item names the server and the bare tool in two fields —
    ``server_label`` + ``name`` in the Responses spelling, ``server`` + ``tool``
    in the rollout's own — so the two are composed into the
    ``mcp__<server>__<tool>`` spelling the engines' MCP calls share.
    Uncomposed, ``search`` is indistinguishable from an engine builtin
    and :func:`~fedcourtsai.tool_usage.normalize_call` buckets it as one — the
    offered denominator loses the call and the MCP-gated result observability
    reads the engine as having no MCP calls at all.

    The server half flows into the name verbatim, which is what keeps the
    composition honest about an unknown server: a manifest's server ids are
    schema-constrained to lowercase, so anything else lands as the literal
    string the transcript carried rather than as a quietly normalized id.
    """
    name = payload.get("name") or payload.get("tool")
    server = payload.get("server_label") or payload.get("server")
    if name and server:
        return f"mcp__{server}__{name}"
    return name or payload["type"]


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


# --- Codex transcript shape distillation ---------------------------------
#
# The verification lever for the Codex parsing above. That parser reads the
# rollout against the Responses API's documented item shapes plus the
# rollout's own spellings, and a shape it does not recognize costs a whole
# engine's retrieval rows silently — the log records "no calls", which is
# indistinguishable from a cell that retrieved nothing. Distilling a real
# transcript's item shapes says which of the two a zero row-count is.
#
# Shape-only, by construction: a rollout carries retrieved documents and tool
# arguments verbatim, so the distillation must never be able to republish
# them. Every emitted string is either a JSON type name or an
# identifier-shaped token (:data:`_SHAPE_IDENTIFIER`) read from a *key* or a
# type discriminator; every *value* is replaced by its type name. The one
# residual is an object keyed by data rather than by schema — bounded by the
# identifier screen, the per-object key cap, and a walk that stops at the item
# envelope, where the keys are the CLI's own.
_SHAPE_DEPTH = 2
_SHAPE_KEY_CAP = 40
_SHAPE_VARIANT_CAP = 3
# What an emitted key or type discriminator may look like. Anything else is a
# free-text string wearing a key's position, and is reported as its shape
# rather than its content.
_SHAPE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:/-]{1,64}$")
_SHAPE_NON_IDENTIFIER = "<non-identifier>"


# In order: ``bool`` precedes ``int`` because it is a subclass of one.
_JSON_TYPE_NAMES: tuple[tuple[type | tuple[type, ...], str], ...] = (
    (bool, "bool"),
    ((int, float), "number"),
    (str, "string"),
    (dict, "object"),
    (list, "array"),
)


def _json_type_name(value: Any) -> str:
    """The JSON type name of ``value`` — the only thing a value contributes."""
    if value is None:
        return "null"
    for kinds, name in _JSON_TYPE_NAMES:
        if isinstance(value, kinds):
            return name
    return "unknown"


def _shape_token(value: Any) -> str:
    """A key name or type discriminator, screened to identifier shape."""
    text = value if isinstance(value, str) else str(value)
    return text if _SHAPE_IDENTIFIER.match(text) else _SHAPE_NON_IDENTIFIER


def _shape(value: Any, depth: int) -> Any:
    """``value`` with every leaf replaced by its JSON type name.

    Recurses ``depth`` levels into objects, keeping their keys (screened and
    capped); below that, and for every scalar, only the type name survives. An
    array spends no level of its own — it is a container, not a nesting step,
    and the shape that matters is its elements' — so its distinct element
    shapes (capped) are read at the array's own depth.
    """
    if depth <= 0:
        return _json_type_name(value)
    if isinstance(value, dict):
        keys = sorted(_shape_token(key) for key in value)[:_SHAPE_KEY_CAP]
        by_token = {_shape_token(key): item for key, item in value.items()}
        return {key: _shape(by_token[key], depth - 1) for key in keys}
    if isinstance(value, list):
        variants: list[Any] = []
        for item in value:
            shape = _shape(item, depth)
            if shape not in variants:
                variants.append(shape)
            if len(variants) >= _SHAPE_VARIANT_CAP:
                break
        return variants
    return _json_type_name(value)


def distill_codex_shapes(sessions_dir: Path) -> dict[str, Any]:
    """Distinct item shapes across every Codex rollout under ``sessions_dir``.

    Every rollout in the tree, not the newest alone
    (:func:`parse_codex_retrieval`'s input): the question a distillation
    answers is which shapes an engine emits at all, and a session that logged
    the interesting item is as good evidence as the last one written.

    Returns a JSON-ready mapping: the file and record totals, then one entry
    per distinct shape — the record envelope's type and keys, the payload's
    own type, and the payload's :func:`_shape` — with the number of records
    that carried it, most frequent first. Tolerant like the parsers: a missing
    directory or an unreadable rollout yields an empty distillation, never an
    exception, because this is instrumentation.
    """
    rollouts = sorted(sessions_dir.rglob("*.jsonl")) if sessions_dir.is_dir() else []
    counts: dict[str, int] = {}
    entries: dict[str, dict[str, Any]] = {}
    records = 0
    for rollout in rollouts:
        for record in _codex_records(rollout):
            records += 1
            payload = _codex_payload(record)
            entry = {
                "record_type": _shape_token(record["type"]) if "type" in record else None,
                "record_keys": sorted(_shape_token(key) for key in record)[:_SHAPE_KEY_CAP],
                "payload_type": (
                    _shape_token(payload["type"])
                    if payload is not None and "type" in payload
                    else None
                ),
                "payload_shape": None if payload is None else _shape(payload, _SHAPE_DEPTH),
            }
            key = json.dumps(entry, sort_keys=True)
            entries.setdefault(key, entry)
            counts[key] = counts.get(key, 0) + 1
    ordered = sorted(counts, key=lambda key: (-counts[key], key))
    return {
        "files": len(rollouts),
        "records": records,
        "shapes": [{"count": counts[key], **entries[key]} for key in ordered],
    }


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
                    # The local exporter logs the invocation and nothing of what
                    # came back, so every Gemini row is unobserved by
                    # construction — a whole engine's capture rate is 0.0.
                    result_capture="unobserved",
                )
            )
            continue
        stack.extend(node.values())
    # The stack walk visits nested containers in reverse; restore log order by
    # timestamp where present (stable for ties/absent stamps).
    calls.sort(key=lambda call: call.timestamp or "")
    return calls[:RETRIEVAL_CALL_CAP]
