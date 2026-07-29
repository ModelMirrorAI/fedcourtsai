"""Tests for the offered-vs-called tool rollup.

The load-bearing behaviours are the two that make the numbers mean anything:
normalizing engine-specific spellings of the same MCP tool, and keeping "never
called" distinct from "no denominator recorded".
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.mcp import manifest_tools
from fedcourtsai.registry import load_mcp_servers
from fedcourtsai.schemas import Engine, RetrievalCall, RetrievalLog, UsageRole
from fedcourtsai.serialize import write_json
from fedcourtsai.tool_usage import (
    build_tool_usage,
    is_web_tool,
    normalize_call,
    render_tool_usage_markdown,
)


def _log(
    root: Path,
    name: str,
    *,
    engine: Engine,
    actor: str,
    tools: list[str],
    offered: list[str] | None = None,
) -> None:
    write_json(
        root / name / "retrieval_log.json",
        RetrievalLog(
            case_id="scotus/1",
            run_id="r",
            role=UsageRole.predictor,
            actor_id=actor,
            engine=engine,
            mcp_servers=["courtlistener=pkg==1.1.0"],
            mcp_tools=offered or [],
            calls=[RetrievalCall(tool=t) for t in tools],
        ),
    )


# --- normalization -------------------------------------------------------------


def test_the_two_engine_spellings_are_one_tool() -> None:
    # Engines disagree on separator width. Un-normalized these split into two
    # rows and every per-tool rate is wrong.
    assert normalize_call("mcp__courtlistener__search") == "courtlistener.search"
    assert normalize_call("mcp_courtlistener_search") == "courtlistener.search"


def test_a_tool_name_containing_underscores_survives_normalization() -> None:
    # The tool half carries its own underscores; only the server separator is special.
    assert normalize_call("mcp__courtlistener__get_endpoint_schema") == (
        "courtlistener.get_endpoint_schema"
    )
    assert normalize_call("mcp_courtlistener_resume_citation_analysis") == (
        "courtlistener.resume_citation_analysis"
    )


def test_engine_builtins_are_not_mcp_tools() -> None:
    # Real tool use, but not what the manifest offers — mixing them into the
    # offered denominator would make every unused-tool rate meaningless.
    for builtin in ("Bash", "run_shell_command", "Read", "write_file", "WebSearch", "exec"):
        assert normalize_call(builtin) is None


# --- the rollup ----------------------------------------------------------------


def test_spellings_merge_into_one_row_with_both_engines(tmp_path: Path) -> None:
    _log(
        tmp_path, "a", engine=Engine.claude_code, actor="claude-baseline", tools=["mcp__cl__search"]
    )
    _log(tmp_path, "b", engine=Engine.gemini, actor="gemini-baseline", tools=["mcp_cl_search"])
    usage = build_tool_usage(tmp_path)
    (entry,) = [e for e in usage.entries if e.tool == "cl.search"]
    assert entry.calls == 2
    assert entry.called_cells == 2
    assert entry.engines == {"claude-code": 1, "gemini": 1}


def test_called_cells_counts_cells_not_calls(tmp_path: Path) -> None:
    # One cell hammering a tool is a different fact from many cells using it once.
    _log(
        tmp_path,
        "a",
        engine=Engine.claude_code,
        actor="claude-baseline",
        tools=["mcp__cl__search"] * 5,
    )
    usage = build_tool_usage(tmp_path)
    (entry,) = usage.entries
    assert (entry.calls, entry.called_cells) == (5, 1)


def test_the_current_manifest_supplies_the_never_called_rows(tmp_path: Path) -> None:
    # Without `offered_now` a ledger of pre-`mcp_tools` logs can only report what
    # was called, so a never-called tool is invisible rather than reported as a gap.
    _log(tmp_path, "a", engine=Engine.gemini, actor="gemini-baseline", tools=["mcp_cl_search"])
    bare = build_tool_usage(tmp_path)
    assert [e.tool for e in bare.entries] == ["cl.search"]

    usage = build_tool_usage(tmp_path, ["cl.search", "cl.read_document", "cl.get_counts"])
    never = [e.tool for e in usage.entries if e.calls == 0]
    assert never == ["cl.get_counts", "cl.read_document"]
    # Never-called rows lead: the actionable gaps come before the busy tools.
    assert [e.tool for e in usage.entries][-1] == "cl.search"


def test_a_missing_denominator_is_not_reported_as_zero_offered(tmp_path: Path) -> None:
    # A log predating the offered-tools record has an UNKNOWN denominator. Reading
    # that as "offered by nothing" would understate every tool's exposure.
    _log(tmp_path, "old", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"])
    _log(
        tmp_path,
        "new",
        engine=Engine.gemini,
        actor="g",
        tools=["mcp_cl_search"],
        offered=["cl.search", "cl.read_document"],
    )
    usage = build_tool_usage(tmp_path)
    assert usage.logs == 2
    assert usage.logs_without_offered_record == 1
    offered = {e.tool: e.offered_cells for e in usage.entries}
    assert offered["cl.search"] == 1  # only the log that recorded it
    assert offered["cl.read_document"] == 1


def test_offered_cells_accumulates_across_cells(tmp_path: Path) -> None:
    # The denominator the whole "unused in 3 cells is not unused in 400" caveat
    # rests on. It must count cells, not merely record presence.
    for name in ("a", "b", "c"):
        _log(
            tmp_path,
            name,
            engine=Engine.gemini,
            actor="g",
            tools=[],
            offered=["cl.search", "cl.get_counts"],
        )
    usage = build_tool_usage(tmp_path)
    assert {e.tool: e.offered_cells for e in usage.entries} == {"cl.search": 3, "cl.get_counts": 3}
    assert usage.logs_without_offered_record == 0


def test_actors_are_keyed_by_actor_not_engine(tmp_path: Path) -> None:
    # Two actors on the SAME engine must stay distinct, or the per-actor cut
    # silently becomes a duplicate of the per-engine one.
    _log(tmp_path, "a", engine=Engine.claude_code, actor="claude-baseline", tools=["mcp_cl_search"])
    _log(tmp_path, "b", engine=Engine.claude_code, actor="claude-judge", tools=["mcp_cl_search"])
    (entry,) = build_tool_usage(tmp_path).entries
    assert entry.actors == {"claude-baseline": 1, "claude-judge": 1}
    assert entry.engines == {"claude-code": 2}


def test_called_tools_are_ordered_by_descending_calls(tmp_path: Path) -> None:
    # A documented guarantee: after the never-called rows, the busiest lead.
    _log(
        tmp_path,
        "a",
        engine=Engine.gemini,
        actor="g",
        tools=["mcp_cl_search"] * 3 + ["mcp_cl_get_counts"] * 7 + ["mcp_cl_read_document"],
    )
    called = [e.tool for e in build_tool_usage(tmp_path).entries if e.calls]
    assert called == ["cl.get_counts", "cl.search", "cl.read_document"]


def test_builtins_are_counted_apart_from_manifest_tools(tmp_path: Path) -> None:
    _log(
        tmp_path,
        "a",
        engine=Engine.codex,
        actor="codex-baseline",
        tools=["exec", "exec", "mcp_cl_search"],
    )
    usage = build_tool_usage(tmp_path)
    assert usage.builtin_calls == {"exec": 2}
    assert [e.tool for e in usage.entries] == ["cl.search"]


def test_empty_ledger_renders_without_dividing_by_anything(tmp_path: Path) -> None:
    usage = build_tool_usage(tmp_path)
    assert usage.logs == 0 and usage.entries == []
    assert "No retrieval logs committed yet" in render_tool_usage_markdown(usage)


# --- the report's interpretive contract ----------------------------------------


def test_the_report_refuses_to_call_an_unused_tool_useless(tmp_path: Path) -> None:
    # The trap this report exists to avoid: a zero has three possible causes and
    # the data separates none of them, so the rendering must not imply the first.
    _log(tmp_path, "a", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"])
    md = render_tool_usage_markdown(build_tool_usage(tmp_path, ["cl.search", "cl.get_counts"]))
    assert "never called" in md
    assert "sandbox blocked it" in md
    assert "check the cause before retiring anything" in md


def test_an_unknown_denominator_renders_as_unknown_not_zero(tmp_path: Path) -> None:
    # Printing `0 offered` beside a headline calling the tool offered-but-never-
    # called reads as a contradiction; the column has to say "unknown".
    _log(tmp_path, "a", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"])
    md = render_tool_usage_markdown(build_tool_usage(tmp_path, ["cl.search", "cl.get_counts"]))
    assert "| cl.get_counts | — |" in md
    # And the pin skew is disclosed, since the offered set is today's manifest
    # while the calls came from whatever those cells actually ran.
    assert "courtlistener=pkg==1.1.0" in md


# --- the open-web substitution signal ------------------------------------------


def test_every_engines_web_tool_is_recognised() -> None:
    # Each engine names these itself; a miss here silently undercounts the signal.
    for tool in ("WebSearch", "WebFetch", "google_web_search", "web_fetch"):
        assert is_web_tool(tool)
    for tool in ("Bash", "run_shell_command", "Read", "exec", "ToolSearch", "glob"):
        assert not is_web_tool(tool)


def test_web_without_mcp_counts_only_cells_that_substituted(tmp_path: Path) -> None:
    # The signal is a cell that reached the web and called NO MCP tool. A cell
    # doing both used the web to supplement, not to substitute, and must not
    # inflate the number that gets read as an MCP gap.
    _log(tmp_path, "sub", engine=Engine.claude_code, actor="c", tools=["WebSearch"])
    _log(
        tmp_path,
        "both",
        engine=Engine.gemini,
        actor="g",
        tools=["google_web_search", "mcp_cl_search"],
    )
    _log(tmp_path, "mcp", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"])
    _log(tmp_path, "neither", engine=Engine.codex, actor="x", tools=["exec"])
    usage = build_tool_usage(tmp_path)
    assert usage.cells_with_mcp == 2
    assert usage.cells_with_web == 2
    assert usage.web_without_mcp_by_engine == {"claude-code": 1}
    assert usage.web_calls == {"WebSearch": 1, "google_web_search": 1}


def test_the_web_signal_is_reported_as_suggestive_not_as_failure(tmp_path: Path) -> None:
    # A forward cell is explicitly allowed to use public context, so web use is
    # sanctioned. Rendering it as a fault would send a reader hunting a bug that
    # the prompt licenses.
    _log(tmp_path, "sub", engine=Engine.claude_code, actor="c", tools=["WebSearch"])
    md = render_tool_usage_markdown(build_tool_usage(tmp_path))
    assert "without calling the MCP at all" in md
    assert "Suggestive, not proof" in md
    # And a zero is not read as a choice without checking the cell's surface.
    assert "not by itself evidence that a cell chose not to search" in md


# --- the shipped registries ----------------------------------------------------


def test_both_committed_registries_record_the_offered_tool_set() -> None:
    # `capture-retrieval` picks the registry by role, so a manifest missing
    # `tools` silently gives every cell of that role an empty offered set —
    # indistinguishable from "unrecorded", and permanently undiagnosable.
    for filename in ("predictors.yaml", "evaluators.yaml"):
        servers = load_mcp_servers(Path("config") / filename)
        assert servers, filename
        for server in servers:
            assert server.tools, f"{filename}: {server.id} records no advertised tools"


def test_the_two_registries_advertise_the_same_tools() -> None:
    # The manifests are kept in lockstep on the pin; the tool list is a property
    # of that pin, so a divergence means one of them was bumped alone.
    predictors, evaluators = (
        manifest_tools(load_mcp_servers(Path("config") / f))
        for f in ("predictors.yaml", "evaluators.yaml")
    )
    assert predictors == evaluators


def test_the_cli_reports_against_the_committed_manifest() -> None:
    # End to end over the real registries: the command must resolve a non-empty
    # offered set, which is what makes never-called tools visible at all.
    result = CliRunner().invoke(app, ["tool-usage"])
    assert result.exit_code == 0, result.output
    assert "The current manifest advertises" in result.output
    assert "never called" in result.output
