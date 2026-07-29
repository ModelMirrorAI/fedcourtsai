"""Offered-vs-called tool rollup over the committed retrieval logs.

Read-only and offline: it reads ``data/`` and nothing else — no corpus, no
network — so it runs in the gate and answers, from cells that already ran, which
configured tools are actually being used.

Three questions, and one trap.

**Which offered tools were never called?** A cell's log records what it *called*;
the offered set comes from ``mcp_tools``, snapshotted from the pinned manifest at
capture time. ``mcp_servers`` cannot supply it — it names servers, and a server
advertises many tools — so a log written before ``mcp_tools`` existed has an
unknown denominator, reported as such rather than as zero offered.

**Which are called by some engines and not others?** Usually a prompt or sandbox
problem rather than a tool problem, so per-engine counts sit beside every total.

**How often is each called, and by whom?** Per engine and per actor.

The trap is interpretive, and the report is shaped to avoid setting it: a tool
can be unused because it is useless, because the prompt never mentions it, or
because a sandbox blocked it. Only the first would justify retiring it, and this
data cannot distinguish them. So a zero is reported as *never called*, always
beside the number of cells that offered it — a tool offered in 3 cells and never
called reads very differently from one offered in 400 — and the cause is left to
a human.

Engines do not agree on tool names. The same MCP tool arrives as
``mcp__courtlistener__search`` from one and ``mcp_courtlistener_search`` from
another, so calls are normalized to ``<server>.<tool>`` before counting;
un-normalized, one tool splits into two rows and every rate is wrong.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

from .schemas import RetrievalLog, ToolUsage, ToolUsageEntry
from .serialize import read_model

# An MCP tool call as the engines spell it: `mcp` then the server and tool,
# separated by either one or two underscores depending on the engine. The tool
# half may itself contain single underscores (`get_endpoint_schema`), so the
# separator is matched greedily-left and the remainder taken whole.
_MCP_CALL = re.compile(r"^mcp_{1,2}(?P<server>[a-z0-9]+)_{1,2}(?P<tool>.+)$")

# The engines' open-web tools, by their own names: claude-code's `WebSearch` /
# `WebFetch`, gemini's `google_web_search` / `web_fetch`, and codex's hosted
# `web_search_call`, which the rollout names by payload type rather than by a
# tool name. A codex cell can also reach the web through a spawned `curl`,
# which lands here as a shell call rather than a web one.
_WEB_TOOLS = frozenset(
    {"WebSearch", "WebFetch", "google_web_search", "web_fetch", "web_search_call"}
)


def is_web_tool(tool: str) -> bool:
    """Whether a call is to the open web rather than the corpus or the MCP."""
    return tool in _WEB_TOOLS


def normalize_call(tool: str) -> str | None:
    """An MCP call name as ``<server>.<tool>``, or ``None`` if it is not one.

    Engine built-ins (``Bash``, ``run_shell_command``, ``Read``, ``write_file``)
    return ``None``: they are real tool use but they are not what the manifest
    offers, so they are counted separately rather than mixed into the offered
    denominator.
    """
    match = _MCP_CALL.match(tool)
    if match is None:
        return None
    return f"{match['server']}.{match['tool']}"


def build_tool_usage(data_root: Path, offered_now: list[str] | None = None) -> ToolUsage:
    """Roll every committed ``retrieval_log.json`` into one offered-vs-called view.

    ``offered_now`` is the tool set the *current* manifest advertises. It exists
    because the per-cell ``mcp_tools`` snapshot only reaches logs written after
    that field landed: without it, a ledger of older logs reports "0 offered but
    never called" — true and useless, since a tool no cell recorded as offered is
    indistinguishable from one that does not exist. Passing the current manifest
    makes the never-called list visible immediately, at the cost of comparing
    today's advertised set against calls made under whatever was pinned then. A
    tool listed here with no calls is genuinely never-called; one absent here but
    called historically ran under an older pin.

    Deterministic: entries sort offered-then-never-called first (the actionable
    rows), then by descending calls, then by name — so a reader meets the gaps
    before the busy tools, and a rerun over an unchanged ledger reproduces the
    file byte for byte.
    """
    calls_by_tool: Counter[str] = Counter()
    cells_by_tool: Counter[str] = Counter()
    engines_by_tool: defaultdict[str, Counter[str]] = defaultdict(Counter)
    actors_by_tool: defaultdict[str, Counter[str]] = defaultdict(Counter)
    offered_cells: Counter[str] = Counter()
    builtin_calls: Counter[str] = Counter()

    logs = 0
    logs_without_offered = 0
    pins: Counter[str] = Counter()
    web_calls: Counter[str] = Counter()
    cells_with_mcp = 0
    cells_with_web = 0
    web_without_mcp: Counter[str] = Counter()
    for path in sorted(data_root.rglob("retrieval_log.json")):
        log = read_model(path, RetrievalLog)
        logs += 1
        for pin in log.mcp_servers:
            pins[pin] += 1
        if log.mcp_tools:
            for offered in log.mcp_tools:
                offered_cells[offered] += 1
        else:
            logs_without_offered += 1
        seen_here: set[str] = set()
        used_web = False
        for call in log.calls:
            normalized = normalize_call(call.tool)
            if normalized is None:
                builtin_calls[call.tool] += 1
                if is_web_tool(call.tool):
                    web_calls[call.tool] += 1
                    used_web = True
                continue
            calls_by_tool[normalized] += 1
            # `str()`, not `.value`: the models use `use_enum_values`, so at run
            # time this field is already the plain string the type says is an
            # Engine — a mismatch mypy cannot see and `.value` fails on.
            engines_by_tool[normalized][str(log.engine)] += 1
            actors_by_tool[normalized][log.actor_id] += 1
            seen_here.add(normalized)
        for normalized in seen_here:
            cells_by_tool[normalized] += 1
        cells_with_mcp += bool(seen_here)
        cells_with_web += used_web
        if used_web and not seen_here:
            web_without_mcp[str(log.engine)] += 1

    entries = [
        ToolUsageEntry(
            tool=tool,
            offered_cells=offered_cells.get(tool, 0),
            called_cells=cells_by_tool.get(tool, 0),
            calls=calls_by_tool.get(tool, 0),
            engines=dict(sorted(engines_by_tool[tool].items())),
            actors=dict(sorted(actors_by_tool[tool].items())),
        )
        for tool in sorted(set(offered_cells) | set(calls_by_tool) | set(offered_now or ()))
    ]
    entries.sort(key=lambda e: (e.calls > 0, -e.calls, e.tool))

    return ToolUsage(
        logs=logs,
        logs_without_offered_record=logs_without_offered,
        offered_now=sorted(offered_now or ()),
        pins=dict(sorted(pins.items())),
        web_calls=dict(sorted(web_calls.items(), key=lambda kv: (-kv[1], kv[0]))),
        cells_with_mcp=cells_with_mcp,
        cells_with_web=cells_with_web,
        web_without_mcp_by_engine=dict(sorted(web_without_mcp.items())),
        entries=entries,
        builtin_calls=dict(sorted(builtin_calls.items(), key=lambda kv: (-kv[1], kv[0]))),
    )


def render_tool_usage_markdown(usage: ToolUsage) -> str:
    """A short human-readable rollup — the shape the run summary carries."""
    lines = ["# Tool usage — offered vs called", ""]
    if usage.logs == 0:
        lines.append("_No retrieval logs committed yet._")
        return "\n".join(lines) + "\n"

    never = [e for e in usage.entries if e.calls == 0]
    lines += [
        f"**{usage.logs}** cell log(s). **{len(usage.entries)}** MCP tool(s) seen "
        f"offered or called; **{len(never)}** never called.",
        "",
    ]
    by_tool = {e.tool: e.calls for e in usage.entries}
    if usage.offered_now:
        called_now = sum(1 for t in usage.offered_now if by_tool.get(t))
        lines += [
            f"_The current manifest advertises **{len(usage.offered_now)}** tool(s); "
            f"**{called_now}** of them have ever been called._",
            "",
        ]
    if usage.logs_without_offered_record:
        pins = ", ".join(f"`{pin}` ({n})" for pin, n in usage.pins.items()) or "an unnamed pin"
        lines += [
            f"_{usage.logs_without_offered_record} log(s) predate the offered-tools "
            "record, so their own denominator is unknown — the `offered in` column reads "
            "`—` for them. Those cells ran under " + pins + ", while the offered set above "
            "is what the manifest pins **now**: a tool listed with no calls is genuinely "
            "never-called, and one called but not listed ran under an older pin._",
            "",
        ]
    lines += [
        "| tool | offered in | called in | calls | engines |",
        "| --- | --: | --: | --: | --- |",
    ]
    for entry in usage.entries:
        engines = ", ".join(f"{k} {v}" for k, v in entry.engines.items()) or "—"
        # `—`, not `0`: no cell recorded this tool as offered, which on a ledger
        # of pre-`mcp_tools` logs means unknown. Printing 0 beside a headline
        # that counts it as offered-but-never-called reads as a contradiction.
        offered = str(entry.offered_cells) if entry.offered_cells else "—"
        lines.append(
            f"| {entry.tool} | {offered} | {entry.called_cells} | {entry.calls} | {engines} |"
        )
    lines += [
        "",
        "_A zero means **never called**, not useless: a tool can go unused because "
        "the prompt never mentions it or a sandbox blocked it, and this data cannot "
        "tell those apart. Read the offered count beside it — unused in 3 cells is "
        "not unused in 400 — and check the cause before retiring anything._",
    ]
    if usage.cells_with_web or usage.cells_with_mcp:
        web = ", ".join(f"`{name}` {count}" for name, count in usage.web_calls.items()) or "none"
        lines += [
            "",
            "## Open web vs the MCP",
            "",
            f"**{usage.cells_with_mcp}** cell(s) called an MCP tool; "
            f"**{usage.cells_with_web}** reached the open web ({web}).",
        ]
        if usage.web_without_mcp_by_engine:
            per_engine = ", ".join(
                f"{engine} {count}" for engine, count in usage.web_without_mcp_by_engine.items()
            )
            total = sum(usage.web_without_mcp_by_engine.values())
            lines += [
                "",
                f"**{total}** cell(s) searched the web without calling the MCP at all "
                f"({per_engine}) — the substitution signal, and the place to look for a "
                "gap or a failure in the MCP surface.",
            ]
        lines += [
            "",
            "_Suggestive, not proof. A forward cell is explicitly allowed to use public "
            "context the corpus does not carry, so web use is sanctioned rather than a "
            "fault; what it flags is a cell that needed something and did not get it from "
            "the configured tools. All three engines carry a web tool, so a zero here is "
            "a cell's own restraint rather than a gap in what it was handed._",
        ]
    if usage.builtin_calls:
        shown = list(usage.builtin_calls.items())[:10]
        rows = ", ".join(f"`{name}` {count}" for name, count in shown)
        lines += [
            "",
            f"**Engine built-ins** (not manifest tools, counted separately): {rows}.",
        ]
    return "\n".join(lines) + "\n"
