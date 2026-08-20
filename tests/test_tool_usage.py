"""Tests for the offered-vs-called tool rollup.

The load-bearing behaviours are the ones that make the numbers mean anything:
normalizing engine-specific spellings of the same MCP tool, keeping "never
called" distinct from "no denominator recorded", keeping an uncaptured result
distinct from a call that came back empty, and refusing to publish a
correlation the ledger cannot support.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.mcp import manifest_tools
from fedcourtsai.registry import load_mcp_servers
from fedcourtsai.retrieval import RETRIEVAL_CALL_CAP
from fedcourtsai.schemas import (
    Disposition,
    Engine,
    Evaluation,
    LeakageAssessment,
    ModelUsage,
    Prediction,
    ProcessVersion,
    RetrievalCall,
    RetrievalLog,
    ToolUsefulness,
    UsageRole,
    normalize_call,
)
from fedcourtsai.serialize import write_json
from fedcourtsai.tool_usage import (
    TOOL_USAGE_CORRELATION_MIN_CELLS,
    build_tool_usage,
    is_web_tool,
    render_tool_usage_markdown,
)
from tests.conftest import bless_process


def _log(  # noqa: PLR0913 - a keyword-only fixture builder, one arg per log field a test varies
    root: Path,
    name: str,
    *,
    engine: Engine,
    actor: str,
    tools: list[str],
    offered: list[str] | None = None,
    calls: list[RetrievalCall] | None = None,
    mode: str | None = None,
    role: UsageRole = UsageRole.predictor,
    case_id: str = "scotus/1",
    run_id: str = "r",
) -> Path:
    path = root / name / "retrieval_log.json"
    write_json(
        path,
        RetrievalLog(
            case_id=case_id,
            run_id=run_id,
            role=role,
            actor_id=actor,
            engine=engine,
            mode=mode,
            mcp_servers=["courtlistener=pkg==1.1.0"],
            mcp_tools=offered or [],
            calls=calls if calls is not None else [RetrievalCall(tool=t) for t in tools],
        ),
    )
    return path


def _usage(cell_dir: Path, *, cost: float, engine: Engine = Engine.claude_code) -> None:
    write_json(
        cell_dir / "usage.json",
        ModelUsage(
            case_id="scotus/1",
            event_id="evt-petition-disposition",
            run_id="r",
            role=UsageRole.predictor,
            actor_id="claude-baseline",
            engine=engine,
            model="claude-fable-5",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_tokens=1,
            output_tokens=1,
            estimated_cost_usd=cost,
        ),
    )


def _stamp(digest: str = "sha256:blessed") -> ProcessVersion:
    return ProcessVersion(
        label="proc-v1", digest=digest, stamped_at=datetime(2026, 1, 1, tzinfo=UTC)
    )


def _cell(  # noqa: PLR0913 - one keyword per coordinate of the cell the join keys on
    root: Path,
    *,
    docket: str,
    predictor: str,
    engine: Engine,
    calls: int,
    brier: float | None,
    mode: str | None = "forward",
    judges: tuple[str, ...] = ("claude-judge",),
    run_id: str = "20260101T000000Z",
    event_id: str = "evt-petition-disposition",
    stamp: ProcessVersion | None = None,
) -> Path:
    """A predicted cell in the real ledger layout, with the panel that scored it.

    The usefulness join keys on the event directory the path names and on the
    evaluations nested beside the predictions, so the fixture has to be the
    committed shape rather than a flat directory of logs. ``stamp`` is what the
    frozen scope partitions on; ``None`` leaves it a shakedown cell.
    """
    event = root / "cases" / "scotus" / docket / "events" / event_id
    cell_dir = event / "predictions" / predictor / run_id
    _log(
        cell_dir.parent,
        run_id,
        engine=engine,
        actor=predictor,
        # One builtin beside the manifest calls, so the segment's MCP column is
        # not a copy of its call column.
        tools=["mcp__cl__search"] * calls + ["Bash"],
        case_id=f"scotus/{docket}",
        run_id=run_id,
        mode=mode,
    )
    write_json(
        cell_dir / "prediction.json",
        Prediction(
            case_id=f"scotus/{docket}",
            event_id=event_id,
            predictor_id=predictor,
            engine=engine,
            run_id=run_id,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="corpus",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
            process_version=stamp,
        ),
    )
    for judge in judges:
        write_json(
            event / "evaluations" / judge / predictor / run_id / "evaluation.json",
            Evaluation(
                case_id=f"scotus/{docket}",
                event_id=event_id,
                predictor_id=predictor,
                evaluator_id=judge,
                engine=Engine.claude_code,
                run_id=run_id,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
                correct=1,
                brier_score=brier,
                leakage=(
                    None
                    if mode is None
                    else LeakageAssessment(mode=mode, influenced_prediction="not_applicable")
                ),
            ),
        )
    return cell_dir


def _grading(
    root: Path,
    *,
    docket: str,
    judge: str,
    brier: float | None,
    mode: str = "forward",
    predictor: str = "claude-baseline",
    run_id: str = "20260101T000000Z",
    event_id: str = "evt-petition-disposition",
) -> None:
    """One more judge's grading of an existing cell, without a second prediction."""
    event = root / "cases" / "scotus" / docket / "events" / event_id
    write_json(
        event / "evaluations" / judge / predictor / run_id / "evaluation.json",
        Evaluation(
            case_id=f"scotus/{docket}",
            event_id=event_id,
            predictor_id=predictor,
            evaluator_id=judge,
            engine=Engine.codex,
            run_id=run_id,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            correct=1,
            brier_score=brier,
            leakage=LeakageAssessment(mode=mode, influenced_prediction="not_applicable"),
        ),
    )


def _pooled(root: Path) -> ToolUsefulness:
    """The usefulness block over every process version — the fixtures' scope.

    Most of these tests are about the join's mechanics, not about the freeze, so
    they run unfrozen; the frozen filter has its own tests below.
    """
    useful = build_tool_usage(root, frozen_only=False).usefulness
    assert useful is not None
    return useful


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


# --- result observability ------------------------------------------------------


def test_a_captured_result_is_the_only_positive_evidence_of_observability(tmp_path: Path) -> None:
    # The rate counts digests, and a digest is the one thing that proves the
    # result side was recorded at all.
    _log(
        tmp_path,
        "a",
        engine=Engine.claude_code,
        actor="c",
        tools=[],
        calls=[
            RetrievalCall(tool="mcp__cl__search", result_digest="abc123"),
            RetrievalCall(tool="mcp__cl__search"),
        ],
    )
    (profile,) = build_tool_usage(tmp_path).engine_profiles
    assert (profile.calls, profile.calls_with_result) == (2, 1)
    assert profile.result_observability_rate == 0.5
    assert profile.captures_results is True


def test_an_engine_that_never_captures_a_result_is_not_read_as_all_dead_ends(
    tmp_path: Path,
) -> None:
    # The distinction the committed record cannot draw per call, taken at the
    # engine level instead: with no positive instance anywhere, a null means
    # "not captured", so quoting a 100% dead-end rate would blame the tool for
    # the transcript.
    _log(tmp_path, "g", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"] * 4)
    usage = build_tool_usage(tmp_path)
    (profile,) = usage.engine_profiles
    assert profile.calls_with_result == 0
    assert profile.result_observability_rate == 0.0
    assert profile.captures_results is False
    # And the per-tool dead-end row is withheld rather than reported as total.
    (entry,) = usage.entries
    assert entry.null_result_calls == {}


def test_dead_ends_are_counted_only_for_engines_that_capture_results(tmp_path: Path) -> None:
    # Two engines call the same tool. One records results and has a real dead
    # end; the other records none, so its calls must not enter the rate.
    _log(
        tmp_path,
        "claude",
        engine=Engine.claude_code,
        actor="c",
        tools=[],
        calls=[
            RetrievalCall(tool="mcp__cl__search", result_digest="abc123"),
            RetrievalCall(tool="mcp__cl__search"),
        ],
    )
    _log(tmp_path, "gemini", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"] * 3)
    (entry,) = build_tool_usage(tmp_path).entries
    assert entry.engines == {"claude-code": 2, "gemini": 3}
    assert entry.null_result_calls == {"claude-code": 1}


def test_the_observability_section_names_the_blind_engine_and_its_two_states(
    tmp_path: Path,
) -> None:
    # A reader who takes the column as a hit rate draws the wrong conclusion,
    # so the rendering has to say which two states a null covers.
    _log(tmp_path, "g", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"])
    md = render_tool_usage_markdown(build_tool_usage(tmp_path))
    assert "## Result observability" in md
    assert "Two states, not three" in md
    assert "not one **MCP** call in the whole ledger carried a result digest" in md
    # The flag rides in the table cell too: a row is what gets copied out.
    assert "(no MCP result capture)" in md


def test_builtin_results_alone_do_not_open_the_dead_end_gate(tmp_path: Path) -> None:
    # The real shape this gate exists for: an engine whose shell output pairs
    # cleanly while none of its MCP results reach the transcript would score well
    # on the overall rate and then print 100% dead ends for every manifest tool.
    _log(
        tmp_path,
        "a",
        engine=Engine.codex,
        actor="codex-baseline",
        tools=[],
        calls=[
            RetrievalCall(tool="exec", result_digest="shell01"),
            RetrievalCall(tool="exec", result_digest="shell02"),
            RetrievalCall(tool="mcp__cl__search"),
        ],
    )
    usage = build_tool_usage(tmp_path)
    (profile,) = usage.engine_profiles
    # Two of three calls carried a result, so the overall rate is healthy...
    assert (profile.calls_with_result, profile.result_observability_rate) == (2, 0.6667)
    # ...but not one of them was an MCP call, so the manifest tools stay unobserved.
    assert (profile.mcp_calls_with_result, profile.captures_results) == (0, False)
    (entry,) = usage.entries
    assert entry.null_result_calls == {}


# --- upstream throttling -------------------------------------------------------


def test_throttles_are_counted_over_the_mcp_calls_whose_condition_was_legible(
    tmp_path: Path,
) -> None:
    # The denominator is the legible conditions, not the calls: an unobserved
    # result could not have shown a throttle, and a builtin's result is not the
    # manifest tools being starved even when its text talks about rate limits.
    _log(
        tmp_path,
        "a",
        engine=Engine.claude_code,
        actor="c",
        tools=[],
        calls=[
            RetrievalCall(
                tool="mcp__cl__search",
                result_digest="d1",
                result_capture="captured",
                result_status="throttled",
            ),
            RetrievalCall(
                tool="mcp__cl__search",
                result_digest="d2",
                result_capture="captured",
                result_status="ok",
            ),
            RetrievalCall(
                tool="mcp__cl__search", result_capture="unobserved", result_status="unobserved"
            ),
            RetrievalCall(
                tool="WebFetch",
                result_digest="d3",
                result_capture="captured",
                result_status="throttled",
            ),
        ],
    )
    (profile,) = build_tool_usage(tmp_path).engine_profiles
    assert (profile.mcp_throttled_calls, profile.mcp_calls_with_status) == (1, 2)
    assert profile.mcp_throttle_rate == 0.5


def test_a_capture_blind_engine_gets_a_null_throttle_count_not_a_clean_one(
    tmp_path: Path,
) -> None:
    # The claim a 0 would make here is one the transcript is not entitled to:
    # Gemini logs no result at all, so it cannot be observed being starved. The
    # count goes null with the rate — a count of throttles in a transcript that
    # could not record one is no more a fact than the rate would be.
    _log(tmp_path, "g", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"] * 3)
    (profile,) = build_tool_usage(tmp_path).engine_profiles
    assert (profile.mcp_calls, profile.mcp_calls_with_status) == (3, 0)
    assert profile.mcp_throttled_calls is None
    assert profile.mcp_throttle_rate is None


def test_the_throttling_section_names_the_blind_engine_beside_the_number(
    tmp_path: Path,
) -> None:
    # The caveat has to sit where the number is read: an em dash in a line of
    # rates is exactly the shape a reader rounds to zero.
    _log(tmp_path, "g", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"])
    _log(
        tmp_path,
        "c",
        engine=Engine.claude_code,
        actor="c",
        tools=[],
        calls=[
            RetrievalCall(
                tool="mcp__cl__search",
                result_digest="d1",
                result_capture="captured",
                result_status="throttled",
            )
        ],
    )
    md = render_tool_usage_markdown(build_tool_usage(tmp_path))
    assert "## Upstream throttling" in md
    assert "`claude-code` 1/1 (100.0%)" in md
    # The reason rides in the figure itself, not in a note below it: a bare
    # `0/0 (—)` is exactly the shape a reader rounds to zero.
    assert "`gemini` — (capture-blind)" in md
    assert "0/0" not in md
    assert "capture-blind, not throttle-free" in md
    # Rendered on a clean ledger too: a reader needs to know the question was
    # asked, which a line that appears only on bad news cannot tell them.
    assert "floor" in md
    # And the number may not be read as an engine property.
    assert "per-engine cut is descriptive, not a comparison" in md
    assert "do not rank engines on it" in md


def test_the_throttling_section_reports_a_clean_ledger_rather_than_going_quiet(
    tmp_path: Path,
) -> None:
    _log(
        tmp_path,
        "c",
        engine=Engine.claude_code,
        actor="c",
        tools=[],
        calls=[
            RetrievalCall(
                tool="mcp__cl__search",
                result_digest="d1",
                result_capture="captured",
                result_status="ok",
            )
        ],
    )
    md = render_tool_usage_markdown(build_tool_usage(tmp_path))
    assert "`claude-code` 0/1 (0.0%)" in md
    assert "capture-blind, not throttle-free" not in md


def test_an_engine_that_called_no_mcp_tool_is_not_called_capture_blind(
    tmp_path: Path,
) -> None:
    # Two empty figures with different causes. An engine whose MCP results went
    # uncaptured is capture-blind; one that never called a manifest tool had
    # nothing to be throttled, and explaining its em dash as a capture gap would
    # be simply the wrong reason.
    _log(
        tmp_path,
        "c",
        engine=Engine.claude_code,
        actor="c",
        tools=[],
        calls=[
            RetrievalCall(
                tool="Read",
                result_digest="d1",
                result_capture="captured",
                result_status="ok",
            )
        ],
    )
    (profile,) = build_tool_usage(tmp_path).engine_profiles
    assert (profile.calls, profile.mcp_calls) == (1, 0)
    md = render_tool_usage_markdown(build_tool_usage(tmp_path))
    # Scoped to the ledger: the cell is what capture recorded, and an engine
    # whose manifest calls capture cannot see would read the same way.
    assert "`claude-code` — (no MCP calls in the ledger)" in md
    assert "capture-blind" not in md


# --- the mode, role, and actor cuts --------------------------------------------


def test_the_cuts_split_cells_by_mode_role_and_actor(tmp_path: Path) -> None:
    _log(
        tmp_path, "f", engine=Engine.claude_code, actor="c", tools=["mcp_cl_search"], mode="forward"
    )
    _log(
        tmp_path,
        "r",
        engine=Engine.claude_code,
        actor="c",
        tools=["mcp_cl_search", "Bash"],
        mode="replay",
    )
    _log(
        tmp_path,
        "e",
        engine=Engine.codex,
        actor="codex-judge",
        tools=["exec"],
        role=UsageRole.evaluator,
        mode="forward",
    )
    usage = build_tool_usage(tmp_path)
    assert [(c.key, c.cells, c.calls, c.mcp_calls) for c in usage.by_mode] == [
        ("forward", 2, 2, 1),
        ("replay", 1, 2, 1),
    ]
    assert [(c.key, c.cells) for c in usage.by_role] == [("evaluator", 1), ("predictor", 2)]
    assert [(c.key, c.calls) for c in usage.by_actor] == [("c", 3), ("codex-judge", 1)]


def test_an_unrecorded_mode_is_unknown_rather_than_folded_into_forward(tmp_path: Path) -> None:
    # A log predating the mode field says nothing about its mode. Defaulting it
    # to the mode that dominates today would make the cut agree with itself.
    _log(tmp_path, "old", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"])
    (cut,) = build_tool_usage(tmp_path).by_mode
    assert cut.key == "unknown"


def test_a_single_mode_ledger_says_the_comparison_is_empty(tmp_path: Path) -> None:
    _log(tmp_path, "f", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"], mode="forward")
    md = render_tool_usage_markdown(build_tool_usage(tmp_path))
    assert "so the mode cut compares nothing yet" in md


# --- the cost join --------------------------------------------------------------


def test_cost_joins_the_usage_record_beside_the_log(tmp_path: Path) -> None:
    _log(tmp_path, "a", engine=Engine.claude_code, actor="c", tools=["mcp_cl_search"] * 2)
    _usage(tmp_path / "a", cost=0.5)
    _log(tmp_path, "b", engine=Engine.claude_code, actor="c", tools=["mcp_cl_search"] * 4)
    _usage(tmp_path / "b", cost=1.5)
    (profile,) = build_tool_usage(tmp_path).engine_profiles
    assert (profile.cells_with_cost, profile.mean_cost_usd_per_cell) == (2, 1.0)
    assert profile.mean_calls_per_cell == 3.0
    assert profile.median_calls_per_cell == 3.0


def test_a_missing_usage_sibling_degrades_to_null_rather_than_to_free(tmp_path: Path) -> None:
    # The join must not crash on a cell that committed no usage record, and must
    # not average it in as $0 — that would drag every mean toward zero in
    # proportion to how much data is absent.
    _log(tmp_path, "costed", engine=Engine.claude_code, actor="c", tools=["mcp_cl_search"])
    _usage(tmp_path / "costed", cost=2.0)
    _log(tmp_path, "bare", engine=Engine.claude_code, actor="c", tools=["mcp_cl_search"])
    usage = build_tool_usage(tmp_path)
    (profile,) = usage.engine_profiles
    assert (profile.cells, profile.cells_with_cost) == (2, 1)
    assert profile.mean_cost_usd_per_cell == 2.0
    assert sorted(cell.cost_usd for cell in usage.cells if cell.cost_usd is not None) == [2.0]
    assert [cell.cost_usd for cell in usage.cells].count(None) == 1
    md = render_tool_usage_markdown(usage)
    assert "**1** cell(s) have a retrieval log and no `usage.json`" in md


def test_an_unreadable_usage_sibling_does_not_take_the_rollup_down(tmp_path: Path) -> None:
    # A reporting view over a ledger it does not own: one malformed record costs
    # that cell its cost, not the whole run.
    _log(tmp_path, "a", engine=Engine.claude_code, actor="c", tools=["mcp_cl_search"])
    (tmp_path / "a" / "usage.json").write_text("{not json")
    (cell,) = build_tool_usage(tmp_path).cells
    assert cell.cost_usd is None


# --- the under-powered usefulness verdict ---------------------------------------


def test_the_usefulness_join_reaches_the_gradings_of_a_predicted_cell(tmp_path: Path) -> None:
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=4,
        brier=0.16,
        judges=("claude-judge", "codex-judge"),
    )
    useful = _pooled(tmp_path)
    assert (useful.joined_cells, useful.joined_evaluations) == (1, 2)
    assert (useful.predicted_cells, useful.process_scope) == (1, "all")
    (segment,) = useful.segments
    assert (segment.engine, segment.mode, segment.stage, segment.moment) == (
        "claude-code",
        "forward",
        "cert",
        "distribution",
    )
    assert (segment.cells, segment.evaluations) == (1, 2)
    assert segment.mean_brier_score == 0.16
    # Total volume and the manifest-tool subset of it are separate columns: a
    # cell's shell work is tool use, but it is not retrieval.
    assert (segment.mean_calls, segment.mean_mcp_calls) == (5.0, 4.0)


def test_the_brier_denominator_is_the_gradings_that_scored_one(tmp_path: Path) -> None:
    # `evaluations` counts every judge; only some of them recorded a Brier. Reading
    # the mean against the evaluation total overstates what is behind it.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
        judges=("claude-judge",),
    )
    _grading(tmp_path, docket="1", judge="codex-judge", brier=None)
    useful = _pooled(tmp_path)
    assert (useful.joined_evaluations, useful.brier_gradings) == (2, 1)
    (segment,) = useful.segments
    assert (segment.evaluations, segment.brier_gradings) == (2, 1)


def test_a_cell_nobody_scored_does_not_join(tmp_path: Path) -> None:
    # A prediction with no Brier against it contributes no point; counting it
    # would put a cell into a denominator that has no score to pair with.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=3,
        brier=None,
    )
    useful = _pooled(tmp_path)
    assert (useful.predicted_cells, useful.joined_cells) == (1, 0)
    assert useful.segments == []


def test_cert_and_merits_briers_never_pool_into_one_population(tmp_path: Path) -> None:
    # Two moments score different questions against different base rates, so one
    # mean over both is a number about nothing. Both of these events carry the
    # SAME event-id kind slug (`order`) and different stages, which is exactly
    # what keying on the slug would have pooled.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
        event_id="evt-order-cvsg-disposition",
    )
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=6,
        brier=0.4,
        event_id="evt-order-judgment",
    )
    useful = _pooled(tmp_path)
    assert [(s.stage, s.moment, s.mean_brier_score) for s in useful.segments] == [
        ("cert", "cvsg", 0.2),
        ("merits", "grant", 0.4),
    ]
    assert [(c.mode, c.stage, c.moment) for c in useful.correlations] == [
        ("forward", "cert", "cvsg"),
        ("forward", "merits", "grant"),
    ]


def test_two_moments_of_one_stage_are_two_populations(tmp_path: Path) -> None:
    # Stage alone is too coarse: two moments of one stage answered from different
    # information sets are two populations, so the key carries both.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
    )
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=3,
        brier=0.3,
        event_id="evt-petition-arrival-disposition",
    )
    useful = _pooled(tmp_path)
    assert {s.stage for s in useful.segments} == {"cert"}
    assert sorted(s.moment for s in useful.segments) == ["arrival", "distribution"]


def test_an_undeclared_event_is_its_own_unknown_population(tmp_path: Path) -> None:
    # An entry-pinned event the moment registry does not declare has no population
    # to belong to, and guessing one from its id would invent a comparison.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
        event_id="evt-motion-stay-pending-appeal",
    )
    (segment,) = _pooled(tmp_path).segments
    assert (segment.stage, segment.moment) == ("unknown", "unknown")


def test_forward_and_replay_never_pool_into_one_population(tmp_path: Path) -> None:
    # A replay cell's grade is never claimable performance, so it cannot share a
    # population with a forward cell's.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
    )
    _cell(
        tmp_path,
        docket="2",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=3,
        brier=0.3,
        mode="replay",
    )
    useful = _pooled(tmp_path)
    assert [c.mode for c in useful.correlations] == ["forward", "replay"]
    assert all(c.cells == 1 for c in useful.correlations)


def test_the_mode_comes_from_the_harness_log_not_the_graders_leakage_block(
    tmp_path: Path,
) -> None:
    # The log is the record and the leakage block is a transcription of it. Keying
    # on the transcription would make the population a judgment.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
        judges=("claude-judge",),
    )
    # This judge transcribed the mode wrongly; the segment must not follow it.
    _grading(tmp_path, docket="1", judge="codex-judge", brier=0.3, mode="replay")
    (segment,) = _pooled(tmp_path).segments
    assert segment.mode == "forward"


def test_the_correlation_is_withheld_below_the_declared_floor(tmp_path: Path) -> None:
    # The refusal this block exists for: a handful of cells cannot support a
    # coefficient, and publishing one anyway invites the naive read.
    for docket in range(3):
        _cell(
            tmp_path,
            docket=str(docket),
            predictor="claude-baseline",
            engine=Engine.claude_code,
            calls=docket + 1,
            brier=0.1 * (docket + 1),
        )
    useful = _pooled(tmp_path)
    assert useful.joined_cells == 3 < TOOL_USAGE_CORRELATION_MIN_CELLS
    (correlation,) = useful.correlations
    assert correlation.published is False
    # Withheld, not merely unreported: no downstream reader can quote a number.
    assert correlation.calls_brier_tau is None
    assert correlation.withheld_reason is not None
    assert "below the pre-declared floor" in correlation.withheld_reason


def test_the_correlation_is_published_once_the_floor_is_met(tmp_path: Path) -> None:
    # The other side of the floor: it is a threshold, not a permanent refusal.
    for docket in range(TOOL_USAGE_CORRELATION_MIN_CELLS):
        _cell(
            tmp_path,
            docket=str(docket),
            predictor="claude-baseline",
            engine=Engine.claude_code,
            calls=docket + 1,
            brier=round(0.9 - docket * 0.02, 4),
        )
    useful = _pooled(tmp_path)
    assert useful.joined_cells == TOOL_USAGE_CORRELATION_MIN_CELLS
    (correlation,) = useful.correlations
    assert correlation.published is True
    # Calls rise as Brier falls in this fixture, so the rank correlation is -1.
    assert correlation.calls_brier_tau == -1.0
    assert correlation.withheld_reason is None
    md = render_tool_usage_markdown(build_tool_usage(tmp_path, frozen_only=False))
    # Brier is a loss, so the rendering must say which sign is the good one.
    assert "a NEGATIVE tau is the one that would mean more calls beside better forecasts" in md
    assert "Descriptive, never causal" in md


def test_the_floor_applies_per_population_not_to_the_pooled_total(tmp_path: Path) -> None:
    # Two populations of 20 are not one of 40. Pooling them to clear the floor is
    # exactly the blend the floor exists to prevent.
    half = TOOL_USAGE_CORRELATION_MIN_CELLS - 10
    for docket in range(half * 2):
        _cell(
            tmp_path,
            docket=str(docket),
            predictor="claude-baseline",
            engine=Engine.claude_code,
            calls=docket + 1,
            brier=round(0.9 - docket * 0.01, 4),
            mode="forward" if docket < half else "replay",
        )
    useful = _pooled(tmp_path)
    assert useful.joined_cells == half * 2 > TOOL_USAGE_CORRELATION_MIN_CELLS
    assert [c.published for c in useful.correlations] == [False, False]
    assert all(c.calls_brier_tau is None for c in useful.correlations)


def test_several_judges_of_one_cell_are_one_point_not_several(tmp_path: Path) -> None:
    # Pseudo-replication is the failure mode a cross-evaluated panel invites:
    # three gradings of one prediction are three readings of one observation.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
        judges=("claude-judge", "codex-judge", "gemini-judge"),
    )
    useful = _pooled(tmp_path)
    assert (useful.joined_cells, useful.joined_evaluations) == (1, 3)


# --- the process scope the Brier column carries ---------------------------------


def test_the_default_scope_keeps_only_blessed_process_cells(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A Brier is a grade, so the block that prints one is scoped like the boards.
    # A shakedown cell's Brier is comparable to nothing and must not sit in it.
    bless_process(monkeypatch, "sha256:blessed")
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
    )
    _cell(
        tmp_path,
        docket="2",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=3,
        brier=0.3,
        stamp=_stamp(),
    )
    frozen = build_tool_usage(tmp_path).usefulness
    assert frozen is not None
    assert (frozen.process_scope, frozen.predicted_cells, frozen.joined_cells) == ("frozen", 2, 1)
    (segment,) = frozen.segments
    assert segment.mean_brier_score == 0.3
    # And the unfrozen scope says so in its own field rather than looking alike.
    assert _pooled(tmp_path).joined_cells == 2


def test_the_scope_is_stamped_on_the_artifact_and_rendered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A grade with no process scope beside it is not readable, so the scope has to
    # survive into the published surface, not merely into the builder's arguments.
    bless_process(monkeypatch, "sha256:blessed")
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
        stamp=_stamp(),
    )
    md = render_tool_usage_markdown(build_tool_usage(tmp_path))
    assert "Process scope: **frozen**" in md
    pooled = render_tool_usage_markdown(build_tool_usage(tmp_path, frozen_only=False))
    assert "every process version, shakedown cells included" in pooled


def test_the_tool_counts_stay_all_versions_while_the_brier_is_scoped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A count of what a cell called is a fact about the pipeline, not a grade, and
    # scoping it would hide most of what there is to inspect.
    bless_process(monkeypatch, "sha256:blessed")
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=2,
        brier=0.2,
    )
    usage = build_tool_usage(tmp_path)
    assert usage.logs == 1
    assert usage.usefulness is not None and usage.usefulness.joined_cells == 0


def test_a_cell_at_the_call_cap_is_disclosed_as_right_censored(tmp_path: Path) -> None:
    # The x axis is truncated at the cap, so a coefficient over capped cells
    # understates the spread it was taken over.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        # One short of the cap, since the fixture adds a builtin call of its own.
        calls=RETRIEVAL_CALL_CAP - 1,
        brier=0.2,
    )
    useful = _pooled(tmp_path)
    assert useful.cells_at_call_cap == 1
    md = render_tool_usage_markdown(build_tool_usage(tmp_path, frozen_only=False))
    assert "right-censored" in md


def test_the_verdict_renders_the_refusal_beside_the_denominators(tmp_path: Path) -> None:
    # The line that has to survive into the run summary: the table is a set of
    # denominators, and no relationship may be read out of it.
    _cell(
        tmp_path,
        docket="1",
        predictor="claude-baseline",
        engine=Engine.claude_code,
        calls=5,
        brier=0.25,
    )
    md = render_tool_usage_markdown(build_tool_usage(tmp_path, frozen_only=False))
    assert "## Does retrieval buy accuracy?" in md
    assert "**Under-powered — no correlation published.**" in md
    assert f"TOOL_USAGE_CORRELATION_MIN_CELLS = {TOOL_USAGE_CORRELATION_MIN_CELLS}" in md
    assert "| cells (n) |" in md
    assert "read no relationship between calls and Brier out of it" in md
    # And it never claims to be the board.
    assert "An ops view, not a scored board" in md


def test_a_ledger_with_no_scored_cell_says_so_rather_than_printing_an_empty_table(
    tmp_path: Path,
) -> None:
    _log(tmp_path, "a", engine=Engine.gemini, actor="g", tools=["mcp_cl_search"])
    md = render_tool_usage_markdown(build_tool_usage(tmp_path))
    assert "Nothing joins in this scope" in md


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
