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

Where a result *was* captured, ``result_status`` says what came back in it —
``throttled`` when the payload carries the shape the pinned CourtListener MCP
server renders an upstream HTTP 429 as, ``error`` on the engine's own failure
marker, ``ok`` otherwise. The throttle state is the one that changes how a cell
should be read: a call the shared daily quota turned away retrieved nothing, so
a starved run's coverage is not comparable with a well-fed one's, and the 429
evidence exists nowhere else — the payload it sits in is digested away one line
later. It is a floor by construction, and only on the engines whose results
reach a transcript at all; every Gemini row is ``unobserved``.

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

from .schemas import RetrievalCall, RetrievalResultStatus
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
# The shape a captured result takes when the shared upstream quota turned the
# call away rather than answering it. Read off the pinned CourtListener MCP
# release (:mod:`fedcourtsai.mcp` names it): its tool-handler middleware turns an
# upstream HTTP 429 into the tool error `Rate limit exceeded: HTTP 429: <detail>.
# For higher rate limits, …`, and its citation tools append `Rate limited by the
# upstream API (retry in ~Ns, …)` to a result the throttle cut short. Both carry
# one of these phrases; `Too Many Requests` covers a transport-level rendering of
# the same status.
#
# Phrase-anchored on purpose, unlike the bare `\b429\b` in
# :mod:`fedcourtsai.pipeline.runner`'s transient-failure regex — that one scans an
# agent's stderr, this one scans *retrieved legal content*, where 429 is an
# everyday U.S. Reports volume ("429 U.S. 274") and a docket number besides. The
# asymmetry is deliberate: a false positive invents starvation in a run that had
# none and taints every comparison drawn from it, while a false negative only
# leaves a throttled call reading as `ok` — where every call sat before the marker
# existed. So the predicate is cheap to miss with and expensive to fire wrongly,
# and every count derived from it is a floor.
_THROTTLE_RE = re.compile(
    r"""
      rate[\s_-]*limit[\s_-]*exceeded   # the MCP tool handler's own 429 rendering
    | rate[\s_-]*limited                # the citation tools' partial-result note
    | \bhttp[\s_-]*429\b                # the API client's `HTTP 429: <detail>` str
    | too[\s_-]*many[\s_-]*requests     # the status' reason phrase
    """,
    re.IGNORECASE | re.VERBOSE,
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


def _result_text(result: Any) -> str:
    """A captured result payload as the one searchable string both readers scan.

    Serialized once per call and handed to the date and condition reads
    together: a result payload is unbounded, and re-serializing it per question
    costs the walk in proportion to how much the agent retrieved.
    """
    try:
        return json.dumps(result, default=str)
    except (TypeError, ValueError):
        return str(result)


def _doc_date(text: str) -> str | None:
    """The first document/decision date legible in a serialized result, if any."""
    match = _DOC_DATE_RE.search(text)
    return match.group(1) if match else None


def _result_status(
    text: str, *, captured: bool, engine_error: bool = False
) -> RetrievalResultStatus:
    """The condition of a call's result, from what capture actually holds.

    ``unobserved`` wherever no result reached the log, so this field and
    ``result_capture`` never disagree about capture (the schema rejects a row
    where they do). Otherwise the throttle predicate decides first — a 429
    arrives *as* an error, and which error it is, is the whole point — then the
    engine's own error marker, then ``ok`` as the residual.

    ``engine_error`` is a structural flag the engine set (a Claude
    ``tool_result``'s ``is_error``, a Codex MCP item's inline ``error``), never
    a guess from the text: no marker robust enough to sniff a generic failure
    out of arbitrary result prose exists, and inventing one would put a
    text-shaped judgment in a field whose whole value is that it is mechanical.
    Where an engine sets no such flag, its failures land in ``ok`` — which is
    why ``ok`` claims only "captured, unmarked, unthrottled".
    """
    if not captured:
        return "unobserved"
    if _THROTTLE_RE.search(text):
        return "throttled"
    return "error" if engine_error else "ok"


def parse_claude_retrieval(execution_file: Path) -> list[RetrievalCall]:
    """Tool calls from a Claude Code ``execution_file`` JSON transcript."""
    doc = _load_json(execution_file)
    events = doc if isinstance(doc, list) else [doc] if isinstance(doc, dict) else []
    # First pass: index tool-result *blocks* by the tool_use id they answer. The
    # whole block, not just its content: `is_error` rides beside the payload and
    # is the engine's own word on whether the call came back a failure.
    results: dict[str, dict[str, Any]] = {}
    for event in events:
        for block in _message_blocks(event):
            if block.get("type") == "tool_result" and block.get("tool_use_id"):
                results[str(block["tool_use_id"])] = block
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
            answer = results.get(call_id)
            captured = call_id in results
            result = answer.get("content") if answer is not None else None
            text = _result_text(result) if result is not None else ""
            calls.append(
                RetrievalCall(
                    tool=_tool_name(block["name"]),
                    query=_query_slice(params),
                    params_digest=_digest(params),
                    timestamp=_text(timestamp),
                    result_digest=_digest(result),
                    # A date the `\d{4}-\d{2}-\d{2}` capture produced; it has no
                    # room to carry anything else, so it needs no redaction.
                    retrieved_doc_date=_doc_date(text) if result is not None else None,
                    result_capture="captured" if captured else "unobserved",
                    result_status=_result_status(
                        text,
                        captured=captured,
                        engine_error=bool(answer.get("is_error")) if answer is not None else False,
                    ),
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
        # A sibling `*_output` item carries no failure flag of its own, so a call
        # paired that way has only its text to be read by: the throttle predicate
        # can still classify it, but a generic failure lands as `ok`.
        engine_error = False
        # An MCP item settles on itself rather than in a sibling, so where the
        # sibling lookup produced no result, the item's own is the pairing. A
        # sibling that carried anything at all — an empty string included — wins;
        # only a null one, which digests to nothing either way, defers.
        if result is None:
            inline = _codex_inline_result(payload)
            if inline is not None:
                field, result = inline
                captured, engine_error = True, field == "error"
        text = _result_text(result) if result is not None else ""
        calls.append(
            RetrievalCall(
                tool=_tool_name(_codex_tool(payload)),
                query=_query_slice(params),
                params_digest=_digest(params),
                timestamp=_text(record.get("timestamp")),
                result_digest=_digest(result),
                retrieved_doc_date=_doc_date(text) if result is not None else None,
                result_capture="captured" if captured else "unobserved",
                result_status=_result_status(text, captured=captured, engine_error=engine_error),
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


def _codex_inline_result(payload: dict[str, Any]) -> tuple[str, Any] | None:
    """An MCP call item's own settled result as ``(field, value)``, else ``None``.

    The field name rides back with the value because ``error`` is the engine's
    own word that this call came back a failure — the Codex counterpart of a
    Claude ``tool_result``'s ``is_error`` — and the per-call condition marker
    reads it rather than guessing a failure out of the payload's prose.

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
            return field, value
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
                    # construction — a whole engine's capture rate is 0.0, and
                    # its result condition is unreadable rather than fine: this
                    # engine cannot be seen being throttled at all.
                    result_capture="unobserved",
                    result_status="unobserved",
                )
            )
            continue
        stack.extend(node.values())
    # The stack walk visits nested containers in reverse; restore log order by
    # timestamp where present (stable for ties/absent stamps).
    calls.sort(key=lambda call: call.timestamp or "")
    return calls[:RETRIEVAL_CALL_CAP]
