"""Off-ledger spend: the per-leg record, its sweep, and the separate report."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import off_ledger_spend, summaries
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from fedcourtsai.pricing import TokenCounts, estimate_cost_usd
from fedcourtsai.schemas import (
    CaseSummaryFrontMatter,
    CaseSummaryUsage,
    Engine,
    ModelUsage,
    OffLedgerSpend,
    UsageRole,
)
from fedcourtsai.serialize import read_model, write_json
from fedcourtsai.usage import parse_claude_transcripts_usage, parse_codex_usage_all

runner = CliRunner()

WHEN = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)


def _assistant(message_id: str, model: str, **usage: int) -> str:
    return json.dumps(
        {"type": "assistant", "message": {"id": message_id, "model": model, "usage": usage}}
    )


# --- engine logs ---------------------------------------------------------------


def test_claude_transcripts_count_each_response_once_by_model(tmp_path: Path) -> None:
    projects = tmp_path / "projects" / "-home-runner-work"
    projects.mkdir(parents=True)
    # One response written as two content-block lines repeating its usage, a
    # second response, a synthetic turn no model served, and a non-JSON line.
    (projects / "session-a.jsonl").write_text(
        "\n".join(
            [
                _assistant("msg_1", "claude-opus-5-5", input_tokens=100, output_tokens=10),
                _assistant("msg_1", "claude-opus-5-5", input_tokens=100, output_tokens=12),
                _assistant("msg_2", "claude-opus-5-5", input_tokens=5, cache_read_input_tokens=900),
                _assistant("msg_3", "<synthetic>", input_tokens=1, output_tokens=1),
                "not json",
                json.dumps({"type": "user", "message": {"content": "hi"}}),
            ]
        )
    )
    # A subagent's transcript on another model bills beside the main thread.
    sub = projects / "session-a" / "subagents"
    sub.mkdir(parents=True)
    (sub / "agent-1.jsonl").write_text(
        _assistant("msg_9", "claude-haiku-4-5", input_tokens=50, output_tokens=5)
    )

    found = parse_claude_transcripts_usage(tmp_path / "projects")

    assert found == {
        "claude-haiku-4-5": TokenCounts(input_tokens=50, output_tokens=5),
        "claude-opus-5-5": TokenCounts(
            input_tokens=105, output_tokens=12, cache_read_input_tokens=900
        ),
    }


def test_claude_transcripts_with_no_usage_read_as_none(tmp_path: Path) -> None:
    assert parse_claude_transcripts_usage(tmp_path / "missing") is None
    (tmp_path / "empty").mkdir()
    (tmp_path / "empty" / "s.jsonl").write_text(json.dumps({"type": "user"}))
    assert parse_claude_transcripts_usage(tmp_path / "empty") is None


def _rollout(path: Path, meta: dict[str, object], totals: list[tuple[int, int, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = [{"type": "session_meta", "payload": meta}]
    for total_input, cached, output in totals:
        records.append(
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "input_tokens": total_input,
                            "cached_input_tokens": cached,
                            "output_tokens": output,
                        }
                    },
                },
            }
        )
    path.write_text("\n".join(json.dumps(r) for r in records))


def test_codex_usage_all_sums_every_cell_and_skips_a_forks_inherited_totals(
    tmp_path: Path,
) -> None:
    day = tmp_path / "sessions" / "2026" / "11" / "01"
    _rollout(day / "rollout-1-a.jsonl", {"id": "a"}, [(100, 40, 10)])
    _rollout(day / "rollout-2-b.jsonl", {"id": "b"}, [(200, 0, 20)])
    # Sorted ahead of its parent's file, so only the ordering keeps the
    # inherited leading total from counting twice.
    _rollout(
        day / "rollout-0-c.jsonl",
        {"id": "c", "parent_thread_id": "a", "source": {"subagent": {}}},
        [(100, 40, 10), (130, 40, 15)],
    )

    counts = parse_codex_usage_all(tmp_path / "sessions")

    # a: 100 in (40 cached), 10 out; b: 200 in, 20 out; c adds 30 in, 5 out.
    assert counts == TokenCounts(input_tokens=290, output_tokens=35, cache_read_input_tokens=40)


# --- the recorder --------------------------------------------------------------


def _record_args(out: Path, *extra: str) -> list[str]:
    return [
        "off-ledger-spend",
        "--workflow",
        "integration-test",
        "--lane",
        "engine-actions-smoke",
        "--leg",
        "engine-actions-smoke-claude-code",
        "--selection",
        "gate",
        "--environment",
        "staging",
        "--ref",
        "promote/2026-11-02",
        "--run-id",
        "41200000001",
        "--run-attempt",
        "1",
        "--conclusion",
        "failure",
        "--out-dir",
        str(out),
        "--recorded-at",
        WHEN.isoformat(),
        *extra,
    ]


def test_record_prices_an_execution_file_and_writes_one_record(tmp_path: Path) -> None:
    execution = tmp_path / "execution.json"
    execution.write_text(
        json.dumps(
            [
                {"type": "assistant", "message": {"model": "claude-opus-5-5"}},
                {"type": "result", "usage": {"input_tokens": 1000, "output_tokens": 100}},
            ]
        )
    )
    out = tmp_path / "out"

    result = runner.invoke(app, _record_args(out, "--claude-execution-file", str(execution)))

    assert result.exit_code == 0, result.output
    record = read_model(out / "41200000001-1-engine-actions-smoke-claude-code.json", OffLedgerSpend)
    expected = estimate_cost_usd("claude-opus-5-5", TokenCounts(1000, 100))
    assert record.estimated_cost_usd == pytest.approx(expected)
    assert record.conclusion == "failure"
    assert record.selection == "gate"
    [line] = record.lines
    assert (line.source, line.engine, line.model, line.priced_as) == (
        "claude-execution-file",
        Engine.claude_code,
        "claude-opus-5-5",
        None,
    )


def test_record_prices_an_unknown_model_at_the_dearest_rate(tmp_path: Path) -> None:
    execution = tmp_path / "execution.json"
    execution.write_text(
        json.dumps({"type": "result", "usage": {"input_tokens": 1000, "output_tokens": 100}})
    )
    out = tmp_path / "out"

    result = runner.invoke(
        app,
        _record_args(
            out, "--claude-execution-file", str(execution), "--claude-model", "claude-new-9"
        ),
    )

    assert result.exit_code == 0, result.output
    [line] = read_model(next(out.glob("*.json")), OffLedgerSpend).lines
    assert line.model == "claude-new-9"
    assert line.priced_as is not None
    assert line.estimated_cost_usd == pytest.approx(
        estimate_cost_usd(line.priced_as, TokenCounts(1000, 100))
    )
    assert line.estimated_cost_usd >= estimate_cost_usd("claude-opus-5-5", TokenCounts(1000, 100))


def test_record_with_no_usage_exits_3_and_writes_nothing(tmp_path: Path) -> None:
    out = tmp_path / "out"
    result = runner.invoke(
        app, _record_args(out, "--claude-execution-file", str(tmp_path / "absent.json"))
    )
    assert result.exit_code == 3
    assert not out.exists()


def test_record_carries_cell_usage_and_summaries_at_their_own_cost(tmp_path: Path) -> None:
    cells = tmp_path / "round" / "data"
    for actor, cost in (("judge-a", 1.25), ("judge-b", 0.75)):
        write_json(
            cells / f"cases/scotus/1/events/evt-x/evaluations/{actor}/R1/usage.json",
            ModelUsage(
                case_id="scotus/1",
                event_id="evt-x",
                run_id="R1",
                role=UsageRole.evaluator,
                actor_id=actor,
                engine=Engine.claude_code,
                model="claude-opus-5-5",
                created_at=WHEN,
                input_tokens=10,
                output_tokens=1,
                estimated_cost_usd=cost,
            ),
        )
    written = tmp_path / "out-summaries" / "data"
    front = CaseSummaryFrontMatter(
        case_id="scotus/2",
        snapshot=date(2026, 10, 30),
        record_digest="sha256:" + "1" * 64,
        model="claude-sonnet-5",
        prompt_digest="sha256:" + "0" * 64,
        body_version=2,
        generated_at=WHEN,
        usage=CaseSummaryUsage(input_tokens=3000, output_tokens=400, estimated_cost_usd=0.5),
    )
    path = CasePaths(written, "scotus", 2).summary("2026-10-30")
    path.parent.mkdir(parents=True)
    path.write_text(summaries.render_summary(front, "body"))

    lines = off_ledger_spend.spend_lines(cell_usage_root=cells, case_summaries_root=written)

    assert [(str(line.source), line.records) for line in lines] == [
        ("cell-usage", 2),
        ("case-summaries", 1),
    ]
    assert [line.estimated_cost_usd for line in lines] == pytest.approx([2.0, 0.5])
    assert lines[1].engine is None


def test_a_record_whose_total_disagrees_with_its_lines_is_refused() -> None:
    doc = _record(cost=1.0).model_dump(mode="json")
    doc["estimated_cost_usd"] = 2.0
    with pytest.raises(ValueError, match="sum of the lines"):
        OffLedgerSpend.model_validate(doc)


# --- sweep ---------------------------------------------------------------------


def _record(  # noqa: PLR0913 - one keyword per field a test varies
    *,
    cost: float,
    run_id: str = "41200000001",
    attempt: int = 1,
    leg: str = "engine-smoke-codex",
    lane: str = "engine-smoke",
    workflow: str = "integration-test",
    selection: str | None = "gate",
    environment: str = "staging",
    ref: str = "promote/2026-11-02",
    when: datetime = WHEN,
) -> OffLedgerSpend:
    return OffLedgerSpend.model_validate(
        {
            "workflow": workflow,
            "lane": lane,
            "leg": leg,
            "selection": selection,
            "environment": environment,
            "ref": ref,
            "run_id": run_id,
            "run_attempt": attempt,
            "conclusion": "success",
            "recorded_at": when,
            "lines": [
                {
                    "source": "codex-sessions",
                    "engine": "codex",
                    "model": "gpt-6.1-sol",
                    "input_tokens": 1,
                    "output_tokens": 1,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                    "estimated_cost_usd": cost,
                }
            ],
            "estimated_cost_usd": cost,
        }
    )


def test_ingest_keeps_valid_records_of_its_own_run_only(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact"
    store = tmp_path / "store"
    write_json(artifact / "a.json", _record(cost=1.0))
    write_json(artifact / "b.json", _record(cost=1.0, run_id="999"))
    (artifact / "c.json").write_text("{}")
    write_json(artifact / "d.json", _record(cost=1.0, leg="other", ref="main"))
    write_json(artifact / "e.json", _record(cost=1.0, leg="another", workflow="summarize"))

    result = off_ledger_spend.ingest(
        artifact,
        run_id="41200000001",
        workflow="integration-test",
        ref="promote/2026-11-02",
        store=store,
    )

    assert result.stored == ["41200000001-1-engine-smoke-codex.json"]
    assert [name for name, _ in result.refused] == ["b.json", "c.json", "d.json", "e.json"]
    assert "names run 999" in result.refused[0][1]
    # A second sweep of the same artifact keeps nothing new, and a record that
    # differs from the kept copy never overwrites it.
    again = off_ledger_spend.ingest(
        artifact,
        run_id="41200000001",
        workflow="integration-test",
        ref="promote/2026-11-02",
        store=store,
    )
    assert again.stored == []
    assert again.unchanged == ["41200000001-1-engine-smoke-codex.json"]
    write_json(artifact / "a.json", _record(cost=0.01))
    changed = off_ledger_spend.ingest(
        artifact,
        run_id="41200000001",
        workflow="integration-test",
        ref="promote/2026-11-02",
        store=store,
    )
    assert ("41200000001-1-engine-smoke-codex.json", "differs from the record already kept") in (
        changed.refused
    )
    kept = read_model(store / "41200000001-1-engine-smoke-codex.json", OffLedgerSpend)
    assert kept.estimated_cost_usd == 1.0


def test_ingest_cli_warns_and_exits_zero_on_a_refusal(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact"
    write_json(artifact / "a.json", _record(cost=1.0, run_id="999"))
    result = runner.invoke(
        app,
        [
            "off-ledger-spend-ingest",
            "--from",
            str(artifact),
            "--run-id",
            "41200000001",
            "--workflow",
            "integration-test",
            "--ref",
            "promote/2026-11-02",
            "--store",
            str(tmp_path / "store"),
        ],
    )
    assert result.exit_code == 0
    assert "::warning::" in result.output
    assert "0 kept" in result.output


# --- report --------------------------------------------------------------------


def test_summary_windows_months_and_gate_runs() -> None:
    records = [
        # A gate run: two legs on attempt 1, one re-run leg on attempt 2.
        _record(cost=2.0, leg="engine-smoke-codex"),
        _record(cost=3.0, leg="engine-smoke-claude-code"),
        _record(cost=1.0, attempt=2, leg="engine-smoke-codex"),
        # A second, older gate run.
        _record(cost=4.0, run_id="41100000000", when=WHEN - timedelta(days=10)),
        # A canary on main with prod keys, inside the week.
        _record(
            cost=0.5,
            run_id="41200000002",
            lane="engine-actions-smoke",
            leg="engine-actions-smoke-gemini",
            selection=None,
            environment="prod",
            ref="main",
            when=WHEN - timedelta(days=1),
        ),
        # A staging labeling rehearsal last month, outside both windows.
        _record(
            cost=7.0,
            run_id="40000000000",
            workflow="run-analytics",
            lane="qp-topic-label",
            leg="qp-topic-label",
            selection="qp-topic-label",
            when=WHEN - timedelta(days=40),
        ),
        # Recorded after the report's instant: not yet known.
        _record(cost=100.0, run_id="41300000000", when=WHEN + timedelta(hours=1)),
    ]

    summary = off_ledger_spend.summarize(records, as_of=WHEN)

    week, month = summary.windows
    assert week.total_usd == pytest.approx(6.5)
    assert week.by_environment == {"prod": 0.5, "staging": 6.0}
    assert week.by_lane[("engine-smoke", "staging")] == (3, 6.0)
    assert month.total_usd == pytest.approx(10.5)
    assert summary.records == 6
    assert summary.months == [
        ("2026-09", {"staging": 7.0}),
        ("2026-10", {"prod": 0.5, "staging": 4.0}),
        ("2026-11", {"staging": 6.0}),
    ]
    assert [(c.run_id, c.attempts, c.legs, c.cost_usd) for c in summary.gate_candidates] == [
        ("41100000000", 1, 1, 4.0),
        ("41200000001", 2, 3, 6.0),
    ]

    text = off_ledger_spend.render_report(summary)
    assert "none of this counts toward the spend backstop" in text
    assert "median $5.00 a run" in text
    assert "| qp-topic-label |" not in text  # outside both windows
    assert "| 2026-09 | $0.00 | $7.00 | $7.00 |" in text
    assert json.loads(off_ledger_spend.summary_json(summary))["counted_in_backstop"] is False


def test_report_cli_over_an_empty_store(tmp_path: Path) -> None:
    out = tmp_path / "summary.json"
    result = runner.invoke(
        app,
        [
            "off-ledger-spend-report",
            "--store",
            str(tmp_path / "none"),
            "--as-of",
            WHEN.isoformat(),
            "--json",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "no gate run on record yet" in result.output
    assert json.loads(out.read_text())["records"] == 0


def test_codex_usage_all_over_two_cells_with_a_grandchild_filed_first(tmp_path: Path) -> None:
    day = tmp_path / "sessions" / "2026" / "11" / "01"
    _rollout(day / "rollout-5-p1.jsonl", {"id": "p1"}, [(100, 0, 10)])
    _rollout(day / "rollout-6-p2.jsonl", {"id": "p2"}, [(50, 0, 5)])
    child: dict[str, object] = {"subagent": {}}
    _rollout(
        day / "rollout-3-c1.jsonl",
        {"id": "c1", "parent_thread_id": "p1", "source": child},
        [(100, 0, 10), (120, 0, 12)],
    )
    _rollout(
        day / "rollout-1-g1.jsonl",
        {"id": "g1", "parent_thread_id": "c1", "source": child},
        [(100, 0, 10), (120, 0, 12), (125, 0, 13)],
    )
    _rollout(
        day / "rollout-4-c2.jsonl",
        {"id": "c2", "parent_thread_id": "p2", "source": child},
        [(50, 0, 5), (60, 0, 6)],
    )

    counts = parse_codex_usage_all(tmp_path / "sessions")

    # p1 100/10, c1 +20/+2, g1 +5/+1, p2 50/5, c2 +10/+1. The grandchild is
    # filed before its parent, so it is read first and counts 25/3 past p1's
    # total; c1 then repeats only totals already seen and counts nothing. The
    # sum is the same either way: nothing is counted twice.
    assert counts == TokenCounts(input_tokens=185, output_tokens=19)


def test_claude_transcripts_count_a_response_once_across_files(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    line = _assistant("msg_1", "claude-opus-5-5", input_tokens=10, output_tokens=2)
    (projects / "a.jsonl").write_text(line)
    (projects / "b.jsonl").write_text(line)
    assert parse_claude_transcripts_usage(projects) == {
        "claude-opus-5-5": TokenCounts(input_tokens=10, output_tokens=2)
    }


def test_a_dated_model_id_is_priced_at_its_alias(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    (projects / "a.jsonl").write_text(
        _assistant("m", "claude-haiku-4-5-20251001", input_tokens=1000, output_tokens=100)
    )
    [line] = off_ledger_spend.spend_lines(claude_transcripts_dir=projects)
    assert line.priced_as == "claude-haiku-4-5"
    assert line.estimated_cost_usd == pytest.approx(
        estimate_cost_usd("claude-haiku-4-5", TokenCounts(1000, 100))
    )


def test_an_explicit_codex_model_prices_the_sessions(tmp_path: Path) -> None:
    day = tmp_path / "sessions"
    _rollout(day / "rollout-1-a.jsonl", {"id": "a"}, [(1000, 0, 100)])
    [line] = off_ledger_spend.spend_lines(codex_sessions_dir=day, codex_model="gpt-6.1-sol")
    assert (line.model, line.priced_as) == ("gpt-6.1-sol", None)
