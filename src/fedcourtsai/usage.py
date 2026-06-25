"""Extract token counts from the engines' own run logs.

Both agentic engines report token usage, but in different places and shapes:

- **Claude Code** (``anthropics/claude-code-action``) writes an ``execution_file``
  — a JSON transcript whose final ``result`` event carries cumulative ``usage``
  with ``input_tokens`` already excluding cached reads.
- **Codex** (``openai/codex-action``) writes a session *rollout* JSONL under
  ``$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl``; each ``token_count`` event
  carries cumulative ``total_token_usage`` whose ``input_tokens`` *includes* the
  cached portion.

Both parsers normalize to a :class:`~fedcourtsai.pricing.TokenCounts` so cost
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


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
