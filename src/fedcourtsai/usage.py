"""Extract token counts from the engines' own run logs.

The three agentic engines report token usage in different places and shapes:

- **Claude Code** (``anthropics/claude-code-action``) writes an ``execution_file``
  — a JSON transcript whose final ``result`` event carries cumulative ``usage``
  with ``input_tokens`` already excluding cached reads.
- **Codex** (``openai/codex-action``) writes a session *rollout* JSONL under
  ``$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl``; each ``token_count`` event
  carries cumulative ``total_token_usage`` whose ``input_tokens`` *includes* the
  cached portion.
- **Gemini** (``google-github-actions/run-gemini-cli``) writes an OpenTelemetry
  ``telemetry.log``; each ``gemini_cli.api_response`` event carries the *per-call*
  ``input_token_count`` / ``output_token_count`` / ``cached_content_token_count`` /
  ``thoughts_token_count``, so the counts are **summed across all events** for the
  run (not read from a single cumulative record like the other two).

All parsers normalize to a :class:`~fedcourtsai.pricing.TokenCounts` so cost
estimation downstream is engine-agnostic. They are deliberately tolerant: an
unreadable or unrecognized log yields ``None`` rather than raising, because usage
capture is best-effort instrumentation that must never fail a real run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .pricing import TokenCounts


def _as_int(value: Any) -> int:
    """Coerce a reported token field to a non-negative int (missing/garbage -> 0)."""
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def parse_claude_usage(execution_file: Path) -> TokenCounts | None:
    """Token counts from a Claude Code ``execution_file`` JSON transcript.

    Prefers the final ``result`` event's cumulative ``usage``; falls back to any
    object in the document that carries a ``usage`` block. Returns ``None`` when
    the file is absent, unparseable, or carries no usage.
    """
    usage = _find_claude_usage(_load_json(execution_file))
    if usage is None:
        return None
    return TokenCounts(
        input_tokens=_as_int(usage.get("input_tokens")),
        output_tokens=_as_int(usage.get("output_tokens")),
        cache_read_input_tokens=_as_int(usage.get("cache_read_input_tokens")),
        cache_creation_input_tokens=_as_int(usage.get("cache_creation_input_tokens")),
    )


def _find_claude_usage(doc: Any) -> dict[str, Any] | None:
    """Locate the most authoritative ``usage`` block in a Claude transcript."""
    events = doc if isinstance(doc, list) else [doc]
    # The terminal ``result`` event reports cumulative usage for the whole run.
    for event in reversed(events):
        if isinstance(event, dict) and event.get("type") == "result":
            usage = event.get("usage")
            if isinstance(usage, dict):
                return usage
    # Fallback: a bare result object, or the last event that carries usage.
    for event in reversed(events):
        if isinstance(event, dict):
            usage = event.get("usage")
            if isinstance(usage, dict):
                return usage
    return None


def parse_codex_usage(sessions_dir: Path) -> TokenCounts | None:
    """Token counts from the newest Codex rollout JSONL under ``sessions_dir``.

    Reads the last ``token_count`` event's cumulative ``total_token_usage`` and
    normalizes it to the Claude convention: Codex's ``input_tokens`` counts the
    cached portion, so the cached tokens are split out into
    ``cache_read_input_tokens`` and subtracted from fresh input. Returns ``None``
    when no rollout file or usage event is found.
    """
    rollout = _newest_rollout(sessions_dir)
    if rollout is None:
        return None
    usage = _last_codex_token_usage(rollout)
    if usage is None:
        return None
    cached = _as_int(usage.get("cached_input_tokens"))
    total_input = _as_int(usage.get("input_tokens"))
    return TokenCounts(
        input_tokens=max(0, total_input - cached),
        output_tokens=_as_int(usage.get("output_tokens")),
        cache_read_input_tokens=cached,
        cache_creation_input_tokens=0,
    )


def _newest_rollout(sessions_dir: Path) -> Path | None:
    """The lexically-latest ``rollout-*.jsonl`` under ``sessions_dir``.

    Codex names rollout files with a leading UTC timestamp, so lexical order is
    chronological — no clock or ``mtime`` read needed for a deterministic pick.
    """
    if not sessions_dir.is_dir():
        return None
    rollouts = sorted(sessions_dir.rglob("rollout-*.jsonl"))
    return rollouts[-1] if rollouts else None


def _last_codex_token_usage(rollout: Path) -> dict[str, Any] | None:
    """The cumulative ``total_token_usage`` from the last ``token_count`` event."""
    found: dict[str, Any] | None = None
    for raw in rollout.read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = _extract_total_token_usage(record)
        if usage is not None:
            found = usage
    return found


def _extract_total_token_usage(record: Any) -> dict[str, Any] | None:
    """Find a ``total_token_usage`` dict in a rollout record, regardless of nesting.

    Codex has moved this block between ``payload`` and ``payload.info`` across
    versions, so search the record rather than hard-coding one path.
    """
    if not isinstance(record, dict):
        return None
    stack: list[Any] = [record]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            block = node.get("total_token_usage")
            if isinstance(block, dict):
                return block
            stack.extend(node.values())
    return None


# Per-call token attributes on a Gemini ``gemini_cli.api_response`` event.
_GEMINI_TOKEN_FIELDS: tuple[str, ...] = (
    "input_token_count",
    "output_token_count",
    "cached_content_token_count",
    "thoughts_token_count",
)


def parse_gemini_usage(telemetry_file: Path) -> TokenCounts | None:
    """Token counts from a Gemini CLI OpenTelemetry ``telemetry.log``.

    Each ``gemini_cli.api_response`` event reports one model call's tokens, so the
    per-call counts are summed across the whole run. Normalizes to the Claude
    convention: Gemini's ``input_token_count`` includes the cached portion, so the
    cached tokens are split out into ``cache_read_input_tokens`` and subtracted
    from fresh input; thinking tokens (``thoughts_token_count``) bill as output.
    Returns ``None`` when the log is absent, unparseable, or carries no token
    events.
    """
    events = _find_gemini_token_events(_load_json_objects(telemetry_file))
    if not events:
        return None
    input_total = sum(_as_int(e.get("input_token_count")) for e in events)
    output_total = sum(_as_int(e.get("output_token_count")) for e in events)
    cached_total = sum(_as_int(e.get("cached_content_token_count")) for e in events)
    thoughts_total = sum(_as_int(e.get("thoughts_token_count")) for e in events)
    return TokenCounts(
        input_tokens=max(0, input_total - cached_total),
        output_tokens=output_total + thoughts_total,
        cache_read_input_tokens=cached_total,
        cache_creation_input_tokens=0,
    )


def _find_gemini_token_events(doc: Any) -> list[dict[str, Any]]:
    """Every token-bearing ``api_response`` event anywhere in the telemetry doc.

    Walks the decoded structure and returns each node's normalized attribute dict
    that carries at least one token field. A matched event is not descended into,
    so each model call is counted exactly once regardless of how the local OTEL
    exporter nests its records.
    """
    events: list[dict[str, Any]] = []
    stack: list[Any] = [doc]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            attrs = _gemini_attrs(node)
            if any(field in attrs for field in _GEMINI_TOKEN_FIELDS):
                events.append(attrs)
                continue
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return events


def _gemini_attrs(node: dict[str, Any]) -> dict[str, Any]:
    """Normalize a record's token attributes, tolerating OTEL nesting.

    Token counts may sit directly on the record or under an ``attributes`` block
    that is either a plain dict or an OTLP ``[{key, value}, ...]`` list whose
    values are wrapped (``{"intValue": "12"}``). All three shapes flatten here.
    """
    attrs: dict[str, Any] = {}
    raw = node.get("attributes")
    if isinstance(raw, dict):
        attrs.update(raw)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict) and "key" in item:
                attrs[item["key"]] = _otel_value(item.get("value"))
    for field in _GEMINI_TOKEN_FIELDS:
        if field in node:
            attrs.setdefault(field, node[field])
    return attrs


def _otel_value(value: Any) -> Any:
    """Unwrap an OTLP typed attribute value (``{"intValue": "12"}`` -> ``"12"``)."""
    if isinstance(value, dict):
        for key in ("intValue", "doubleValue", "stringValue", "value"):
            if key in value:
                return value[key]
    return value


def _load_json_objects(path: Path) -> list[Any]:
    """Decode the telemetry file into a list of top-level JSON values.

    The Gemini CLI local exporter concatenates pretty-printed JSON records rather
    than emitting one-per-line, so a plain ``json.loads``/JSONL read does not
    cover it. Try the whole file as one value first (a single object or array),
    then fall back to decoding consecutive objects. Tolerant: returns ``[]`` on an
    unreadable or unparseable file.
    """
    try:
        text = path.read_text().strip()
    except OSError:
        return []
    if not text:
        return []
    try:
        return [json.loads(text)]
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    objects: list[Any] = []
    idx, length = 0, len(text)
    while idx < length:
        while idx < length and text[idx] in " \t\r\n,":
            idx += 1
        if idx >= length:
            break
        try:
            obj, idx = decoder.raw_decode(text, idx)
        except json.JSONDecodeError:
            break
        objects.append(obj)
    return objects


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
