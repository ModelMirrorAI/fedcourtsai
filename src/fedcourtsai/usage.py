"""Extract token counts from the engines' own run logs, plus run provenance.

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
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .pricing import TokenCounts


def resolve_pipeline_sha(explicit: str = "") -> str | None:
    """The git commit of the pipeline checkout that ran this cell, if resolvable.

    Provenance for ``usage.json``: the sha pins the prompt templates, harness,
    and registry in force at run time. An explicit value wins; otherwise
    ``GITHUB_SHA`` (set by Actions on every workflow step) covers CI, and the
    local ``git rev-parse HEAD`` covers the local harness. Best-effort: a
    non-repo cwd or missing git resolves to ``None`` rather than failing the
    capture.
    """
    if explicit:
        return explicit
    from_env = os.environ.get("GITHUB_SHA", "")
    if from_env:
        return from_env
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


_ENGINE_VERSION = re.compile(r"(?<![\d.])(\d+\.\d+\.\d+)(?![\d.])")


def engine_version_from_output(output: str) -> str | None:
    """The first dotted ``X.Y.Z`` version in an engine binary's ``--version`` output.

    Provenance for ``usage.json``: each CLI prints its version in its own shape
    (``2.1.289 (Claude Code)``, ``codex-cli 0.144.1``, a bare ``0.49.0``), so
    the first standalone three-part version is what the record keeps. Output
    naming none resolves to ``None`` rather than failing the capture, and a
    version run into a longer dotted string (an IP address, a four-part build
    number) is not mistaken for one.
    """
    match = _ENGINE_VERSION.search(output)
    return match.group(1) if match else None


def resolve_engine_version(
    at_install: str, after_run: str, pin: str
) -> tuple[str | None, str | None]:
    """The engine version a cell records, and any disagreement around it.

    ``at_install`` is the binary's ``--version`` read when the harness
    installed it, before any agent ran — present for the CLIs the harness
    installs. ``after_run`` is the same read once the cell finished — the only
    read for a CLI its action installs (codex). The recorded version is the
    install-time read where there is one, since nothing the agent did can have
    shaped it, else the after-run read. A disagreement — the after-run read
    differing from the install-time one, or the recorded version differing from
    the ``pin`` the workflow installed from — is returned as a sentence the
    record keeps, never resolved by picking a side.
    """
    before = engine_version_from_output(at_install)
    after = engine_version_from_output(after_run)
    recorded = before or after
    problems: list[str] = []
    if before is not None and after is not None and after != before:
        problems.append(f"the binary reported {after} after the run but {before} at install")
    if pin and recorded is not None and recorded != pin:
        problems.append(f"the binary reported {recorded} but the pin is {pin}")
    return recorded, "; ".join(problems) or None


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


_CLAUDE_USAGE_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)


def parse_claude_transcripts_usage(projects_dir: Path) -> dict[str, TokenCounts] | None:
    """Token counts by model from the Claude Code CLI's own session transcripts.

    The headless ``claude -p`` the pipeline runner launches (a cascade cell, a
    back-test cell) writes no ``execution_file``; the CLI keeps its session
    transcripts as JSONL under ``~/.claude/projects/``, one ``assistant`` line
    per content block of each API response, every line repeating that
    response's ``usage``. So each response is counted once, by its message
    ``id``, at the largest figure any of its lines reports, and subagent
    transcripts under the same tree are counted beside the main thread's, as a
    subagent bills beside its parent. Grouped by the model each response names
    (Claude Code's ``<synthetic>`` placeholder, which no model served, is
    left out). Returns ``None`` when the tree holds no usage at all.
    """
    if not projects_dir.is_dir():
        return None
    by_message: dict[str, tuple[str, dict[str, int]]] = {}
    for transcript in sorted(projects_dir.rglob("*.jsonl")):
        for record in _jsonl_records(transcript):
            if record.get("type") != "assistant":
                continue
            message = record.get("message")
            if not isinstance(message, dict):
                continue
            model = message.get("model")
            usage = message.get("usage")
            if not isinstance(model, str) or model == _CLAUDE_SYNTHETIC_MODEL:
                continue
            if not isinstance(usage, dict):
                continue
            key = str(message.get("id") or record.get("requestId") or "")
            if not key:
                continue
            counts = {field: _as_int(usage.get(field)) for field in _CLAUDE_USAGE_FIELDS}
            if key in by_message:
                _, known = by_message[key]
                counts = {field: max(counts[field], known[field]) for field in counts}
            by_message[key] = (model, counts)
    totals: dict[str, dict[str, int]] = {}
    for model, counts in by_message.values():
        bucket = totals.setdefault(model, dict.fromkeys(_CLAUDE_USAGE_FIELDS, 0))
        for field, value in counts.items():
            bucket[field] += value
    result = {
        model: TokenCounts(**bucket)
        for model, bucket in sorted(totals.items())
        if sum(bucket.values()) > 0
    }
    return result or None


def parse_codex_usage(sessions_dir: Path) -> TokenCounts | None:
    """Token counts from the cell's Codex rollouts under ``sessions_dir``.

    Reads each of the cell's sessions (:func:`codex_cell_rollouts`: the parent
    and every subagent session it spawned) for its last ``token_count`` event's
    cumulative ``total_token_usage`` and sums them, since a subagent bills
    beside its parent rather than inside it. A subagent forked with its
    parent's history copies the parent's ``token_count`` events into its own
    rollout and continues the parent's running total, so its leading totals
    that repeat an earlier session's are inherited, and only what it adds
    past the last of them is its own. Normalizes to the Claude
    convention: Codex's ``input_tokens`` counts the cached portion, so the
    cached tokens are split out into ``cache_read_input_tokens`` and subtracted
    from fresh input. Returns ``None`` when no rollout or usage event is found.
    """
    return _sum_codex_rollouts(codex_cell_rollouts(sessions_dir))


def parse_codex_usage_all(sessions_dir: Path) -> TokenCounts | None:
    """Token counts from **every** Codex session under ``sessions_dir``, summed.

    For a sessions tree that several cells shared — a back-test's or a
    cascade's runner-chosen ``CODEX_HOME`` — where :func:`parse_codex_usage`
    would read one cell. Top-level sessions are read before subagent sessions,
    so a forked subagent's inherited leading totals are already seen when its
    own rollout is read and only what it added is counted, exactly as for one
    cell. Returns ``None`` when no rollout or usage event is found.
    """
    if not sessions_dir.is_dir():
        return None
    rollouts = sorted(sessions_dir.rglob("rollout-*.jsonl"))
    metas = {rollout: _codex_session_meta(rollout) for rollout in rollouts}

    def is_child(rollout: Path) -> bool:
        meta = metas[rollout]
        return meta is not None and (_codex_parent_id(meta) is not None or _codex_is_subagent(meta))

    ordered = [r for r in rollouts if not is_child(r)] + [r for r in rollouts if is_child(r)]
    return _sum_codex_rollouts(ordered)


def _sum_codex_rollouts(rollouts: list[Path]) -> TokenCounts | None:
    """Sum the rollouts' own cumulative usage, leaving out inherited leading totals."""
    seen: set[str] = set()
    found = False
    total_input = cached = output = 0
    for rollout in rollouts:
        history = _codex_token_usages(rollout)
        if not history:
            continue
        found = True
        keys = [json.dumps(usage, sort_keys=True, default=str) for usage in history]
        inherited: dict[str, Any] = {}
        for key, usage in zip(keys, history, strict=True):
            if key not in seen:
                break
            inherited = usage
        last = history[-1]

        def own(field: str, last: dict[str, Any] = last, base: dict[str, Any] = inherited) -> int:
            return max(0, _as_int(last.get(field)) - _as_int(base.get(field)))

        total_input += own("input_tokens")
        cached += own("cached_input_tokens")
        output += own("output_tokens")
        seen.update(keys)
    if not found:
        return None
    return TokenCounts(
        input_tokens=max(0, total_input - cached),
        output_tokens=output,
        cache_read_input_tokens=cached,
        cache_creation_input_tokens=0,
    )


def codex_cell_rollouts(sessions_dir: Path) -> list[Path]:
    """The cell's own Codex sessions: its parent rollout, then each subagent's.

    A Codex session that spawns a subagent writes the subagent's session to a
    rollout of its own, and a subagent started after the parent's last write
    is the **newest** file — so "the newest rollout" can be a subagent's,
    leaving the parent's calls and tokens out of the cell's record. Each
    rollout opens with a ``session_meta`` record naming its thread ``id`` and,
    for a subagent, its ``parent_thread_id`` and a ``source`` of
    ``{"subagent": …}``, which is what this reads.

    The **parent** is the newest rollout whose ``session_meta`` names no
    parent and no subagent source. Its subagents are every rollout whose
    parent chain reaches it, and every subagent rollout naming no parent at
    all (the sessions directory is the cell's own, so an orphaned subagent is
    still this cell's work). A subagent's calls are the cell's: what a cell
    retrieved through a helper it spawned is what it retrieved, for leakage
    grading as for spend. Parent first, then subagents in file order.

    A tree with no top-level ``session_meta`` — a rollout written before Codex
    logged one, or a directory holding only subagent sessions — falls back to
    the newest rollout alone; an empty or missing directory yields no rollouts.
    """
    if not sessions_dir.is_dir():
        return []
    rollouts = sorted(sessions_dir.rglob("rollout-*.jsonl"))
    metas = {rollout: _codex_session_meta(rollout) for rollout in rollouts}
    parents = [
        rollout
        for rollout, meta in metas.items()
        if meta is not None and _codex_parent_id(meta) is None and not _codex_is_subagent(meta)
    ]
    if not parents:
        return rollouts[-1:]
    parent = parents[-1]
    included = {str((metas[parent] or {}).get("id") or "")}
    children: list[Path] = []
    pending = [rollout for rollout in rollouts if rollout not in parents]
    progressed = True
    while progressed:
        progressed = False
        for rollout in list(pending):
            meta = metas[rollout]
            if meta is None:
                continue
            parent_id = _codex_parent_id(meta)
            orphan = parent_id is None and _codex_is_subagent(meta)
            if orphan or (parent_id is not None and parent_id in included):
                children.append(rollout)
                included.add(str(meta.get("id") or ""))
                pending.remove(rollout)
                progressed = True
    return [parent, *sorted(children)]


def _codex_session_meta(rollout: Path) -> dict[str, Any] | None:
    """The payload of a rollout's first ``session_meta`` record, if it has one."""
    try:
        with rollout.open() as handle:
            for raw in handle:
                line = raw.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict) and record.get("type") == "session_meta":
                    payload = record.get("payload")
                    return payload if isinstance(payload, dict) else None
    except OSError:
        return None
    return None


def _codex_subagent_source(meta: dict[str, Any]) -> Any:
    """The ``subagent`` half of a session's ``source``, or ``None`` for a top-level one."""
    source = meta.get("source")
    return source.get("subagent") if isinstance(source, dict) else None


def _codex_is_subagent(meta: dict[str, Any]) -> bool:
    return _codex_subagent_source(meta) is not None


def _codex_parent_id(meta: dict[str, Any]) -> str | None:
    """The thread a session was spawned from, wherever its release records it."""
    parent = meta.get("parent_thread_id")
    if not parent:
        subagent = _codex_subagent_source(meta)
        spawn = subagent.get("thread_spawn") if isinstance(subagent, dict) else None
        parent = spawn.get("parent_thread_id") if isinstance(spawn, dict) else None
    return str(parent) if parent else None


# --- Served model ------------------------------------------------------------
#
# The model each engine's own log names for the cell's main-agent calls, kept
# beside the requested ``model`` a cell is priced at. Each engine logs it at a
# different distance from the provider, and the distance is the reading:
#
# - **Claude Code**: each main-thread ``assistant`` event's ``message.model`` is
#   the model the API response named, so a provider-side substitution shows.
# - **Gemini**: each ``gemini_cli.api_response`` record's ``model`` is the
#   response's own ``modelVersion`` where the API sent one, else the model the
#   CLI requested — so it shows a provider substitution and the CLI's own
#   fallback alike, in the provider's spelling of the version.
# - **Codex**: each ``turn_context`` record's ``model`` is the model the CLI
#   addressed for that turn. A server-side reroute Codex reports only as a
#   transient event its rollout does not persist, so on this engine the value
#   shows a client-side switch and never a provider substitution.

# Claude Code's placeholder for a message it composed itself (an API error
# rendered as a turn), which no model served.
_CLAUDE_SYNTHETIC_MODEL = "<synthetic>"
# Gemini's main-agent role; its utility calls (routing, loop detection,
# compression, summaries) carry roles of their own and run on helper models by
# design, so they are not the cell's model. A record with no role predates the
# attribute and is read as the main agent's.
_GEMINI_MAIN_ROLES = frozenset({"", "main"})


def _first_seen(models: list[str]) -> list[str] | None:
    """Distinct non-empty model ids in first-seen order; ``None`` when there are none."""
    distinct = list(dict.fromkeys(model for model in models if model))
    return distinct or None


def parse_claude_served_models(execution_file: Path) -> list[str] | None:
    """The models a Claude Code transcript's main-thread responses name.

    Main thread only: a subagent the session spawned (``parent_tool_use_id``
    set) runs on whatever model its definition names, by design.
    """
    doc = _load_json(execution_file)
    events = doc if isinstance(doc, list) else [doc]
    models: list[str] = []
    for event in events:
        if not isinstance(event, dict) or event.get("type") != "assistant":
            continue
        if event.get("parent_tool_use_id"):
            continue
        message = event.get("message")
        model = message.get("model") if isinstance(message, dict) else None
        if isinstance(model, str) and model != _CLAUDE_SYNTHETIC_MODEL:
            models.append(model)
    return _first_seen(models)


def parse_codex_served_models(sessions_dir: Path) -> list[str] | None:
    """The models the cell's parent Codex session addressed, one per turn context."""
    rollouts = codex_cell_rollouts(sessions_dir)
    if not rollouts:
        return None
    models: list[str] = []
    try:
        lines = rollouts[0].read_text().splitlines()
    except OSError:
        return None
    for raw in lines:
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict) or record.get("type") != "turn_context":
            continue
        payload = record.get("payload")
        model = payload.get("model") if isinstance(payload, dict) else None
        if isinstance(model, str):
            models.append(model)
    return _first_seen(models)


def parse_gemini_served_models(telemetry_file: Path) -> list[str] | None:
    """The models a Gemini CLI telemetry log's main-agent responses name."""
    models: list[str] = []
    # The token walk pops its stack from the end, so it visits a run of
    # top-level records last-first; reversing restores log order, and the
    # timestamp (where the record carries one) settles the rest.
    events = sorted(
        reversed(_find_gemini_token_events(_load_json_objects(telemetry_file))),
        key=lambda attrs: str(attrs.get("event.timestamp") or ""),
    )
    for attrs in events:
        # Token counts are what usage reads a response by, so a record naming
        # no event is still one; a record naming another event is not.
        name = str(attrs.get("event.name") or "")
        if name and not name.endswith("api_response"):
            continue
        if str(attrs.get("role") or "") not in _GEMINI_MAIN_ROLES:
            continue
        model = attrs.get("model")
        if isinstance(model, str):
            models.append(model)
    return _first_seen(models)


def _last_codex_token_usage(rollout: Path) -> dict[str, Any] | None:
    """The cumulative ``total_token_usage`` from the last ``token_count`` event."""
    history = _codex_token_usages(rollout)
    return history[-1] if history else None


def _codex_token_usages(rollout: Path) -> list[dict[str, Any]]:
    """Every ``token_count`` event's cumulative ``total_token_usage``, in file order."""
    found: list[dict[str, Any]] = []
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
            found.append(usage)
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


# The response attributes the served-model read keys on, flattened from the
# record itself where an exporter left them there rather than under
# ``attributes``, exactly as the token counts are.
_GEMINI_RESPONSE_FIELDS: tuple[str, ...] = ("model", "role")


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
    for field in (*_GEMINI_TOKEN_FIELDS, *_GEMINI_RESPONSE_FIELDS):
        if field in node:
            attrs.setdefault(field, node[field])
    return attrs


def _otel_value(value: Any) -> Any:
    """Unwrap an OTLP typed attribute value (``{"intValue": "12"}`` -> ``"12"``)."""
    if isinstance(value, dict):
        for key in ("intValue", "doubleValue", "boolValue", "stringValue", "value"):
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


def _jsonl_records(path: Path) -> list[dict[str, Any]]:
    """The JSON objects of a JSONL file, one per line; an unreadable line is skipped."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []
    records: list[dict[str, Any]] = []
    for raw in lines:
        try:
            record = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
