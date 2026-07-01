import json
from datetime import datetime
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import ops
from fedcourtsai.cli import app
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    AgentToolingFeedback,
    CorpusCheck,
    CorpusScopeAudit,
    CorpusValidation,
    CourtProgress,
    DataHealth,
    Engine,
    FlagCategory,
    FlagSeverity,
    LedgerValidation,
    ModelUsage,
    OpsReport,
    ScopeDocketShape,
    ScopeExclusion,
    ScopeUnclassified,
    SeedProgress,
    UsageRole,
)


def _run(
    workflow: str, conclusion: str, *, status: str = "completed", started: str, ended: str
) -> dict[str, object]:
    return {
        "workflowName": workflow,
        "status": status,
        "conclusion": conclusion,
        "createdAt": started,
        "startedAt": started,
        "updatedAt": ended,
    }


def test_summarize_health_rates_durations_and_recency() -> None:
    runs: list[dict[str, object]] = [
        _run("run-seed", "success", started="2026-06-24T00:00:00Z", ended="2026-06-24T00:30:00Z"),
        _run("run-seed", "failure", started="2026-06-25T00:00:00Z", ended="2026-06-25T00:10:00Z"),
        _run("run-seed", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:50:00Z"),
        # An in-progress run is not "completed": excluded from rate + durations.
        {
            "workflowName": "run-seed",
            "status": "in_progress",
            "conclusion": None,
            "createdAt": "2026-06-26T01:00:00Z",
        },
    ]
    (health,) = ops.summarize_health(runs)
    assert health.workflow == "run-seed"
    assert health.runs_considered == 4
    assert (health.successes, health.failures) == (2, 1)
    assert health.success_rate == 2 / 3
    # Most recent run is the in-progress one (latest createdAt) -> conclusion None.
    assert health.last_conclusion is None
    assert health.last_run_at == "2026-06-26T01:00:00Z"
    # Durations of the three completed runs: 1800, 600, 3000 -> median 1800.
    assert health.median_seconds == 1800
    assert health.p95_seconds == 3000


def test_summarize_health_groups_and_sorts_by_workflow() -> None:
    runs = [
        _run("run-pull", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:05:00Z"),
        _run("run-seed", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:40:00Z"),
    ]
    assert [h.workflow for h in ops.summarize_health(runs)] == ["run-pull", "run-seed"]


def test_summarize_health_empty() -> None:
    assert ops.summarize_health([]) == []


def test_summarize_backfill_per_court_and_overall() -> None:
    progress = SeedProgress(
        snapshot="2026-03-31",
        courts={
            "scotus": CourtProgress(offset=4000, total=8000),
            "ca1": CourtProgress(offset=2000, total=2000, complete=True),
        },
    )
    bf = ops.summarize_backfill(progress, ["scotus", "ca1"])
    assert bf.snapshot == "2026-03-31"
    assert (bf.courts_total, bf.courts_complete) == (2, 1)
    assert bf.cases_loaded == 6000
    assert bf.cases_total == 10000  # every total known -> overall available
    assert bf.percent == 60.0
    by_court = {c.court: c for c in bf.entries}
    assert by_court["scotus"].percent == 50.0
    assert by_court["ca1"].percent == 100.0 and by_court["ca1"].complete


def test_summarize_backfill_hides_overall_when_a_total_is_unknown() -> None:
    progress = SeedProgress(
        snapshot="2026-03-31",
        courts={"scotus": CourtProgress(offset=4000, total=8000)},
    )
    # ca1 has no cursor entry yet (total unknown, not complete).
    bf = ops.summarize_backfill(progress, ["scotus", "ca1"])
    assert bf.cases_loaded == 4000
    assert bf.cases_total is None
    assert bf.percent is None
    assert {c.court: c.percent for c in bf.entries} == {"scotus": 50.0, "ca1": None}


def _usage(actor: str, cost: float, *, in_tok: int = 100, out_tok: int = 10) -> ModelUsage:
    return ModelUsage(
        case_id="ca9/1",
        event_id="evt-x",
        run_id="20260626T000000Z",
        role=UsageRole.predictor,
        actor_id=actor,
        engine=Engine.claude_code,
        model="claude-opus-4-8",
        created_at=datetime(2026, 6, 26),
        input_tokens=in_tok,
        output_tokens=out_tok,
        cache_read_input_tokens=5,
        cache_creation_input_tokens=0,
        estimated_cost_usd=cost,
    )


def test_summarize_spend_totals_and_mean() -> None:
    spend = ops.summarize_spend([_usage("a", 0.10), _usage("b", 0.30)])
    assert spend.runs == 2
    assert spend.total_tokens == 2 * (100 + 10 + 5)
    assert spend.estimated_cost_usd == 0.4
    assert spend.mean_cost_usd_per_run == 0.2


def test_summarize_spend_empty_has_zero_mean() -> None:
    spend = ops.summarize_spend([])
    assert (spend.runs, spend.total_tokens, spend.estimated_cost_usd) == (0, 0, 0.0)
    assert spend.mean_cost_usd_per_run == 0.0


def test_build_report_is_passed_the_clock_and_validates() -> None:
    progress = SeedProgress(snapshot="2026-03-31", courts={"scotus": CourtProgress(offset=10)})
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[
            _run(
                "run-seed", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:40:00Z"
            )
        ],
        progress=progress,
        courts=["scotus"],
        usage=[_usage("a", 0.25)],
    )
    assert report.generated_at == "2026-06-26T12:00:00+00:00"
    # Round-trips through the strict schema (this is what `validate` would check).
    assert OpsReport.model_validate(report.model_dump()) == report


def test_project_backfill_computes_rate_and_eta() -> None:
    prev = ops.build_ops_report(
        generated_at="2026-06-24T00:00:00+00:00",
        runs=[],
        progress=SeedProgress(courts={"scotus": CourtProgress(offset=2000, total=10000)}),
        courts=["scotus"],
        usage=[],
    )
    now = ops.build_ops_report(
        generated_at="2026-06-26T00:00:00+00:00",  # 2 days later
        runs=[],
        progress=SeedProgress(courts={"scotus": CourtProgress(offset=8000, total=10000)}),
        courts=["scotus"],
        usage=[],
        previous=prev,
    )
    # 6000 cases over 2 days = 3000/day; 2000 remaining -> ~0.67 days -> 2026-06-26.
    assert now.backfill.cases_per_day == 3000.0
    assert now.backfill.eta_date == "2026-06-26"


def test_project_backfill_no_previous_leaves_rate_unset() -> None:
    bf = ops.summarize_backfill(
        SeedProgress(courts={"scotus": CourtProgress(offset=10, total=100)}), ["scotus"]
    )
    same = ops.project_backfill(bf, None, "2026-06-26T00:00:00+00:00")
    assert same.cases_per_day is None and same.eta_date is None


def test_project_backfill_no_progress_reports_zero_rate_no_eta() -> None:
    prev = ops.build_ops_report(
        generated_at="2026-06-24T00:00:00+00:00",
        runs=[],
        progress=SeedProgress(courts={"scotus": CourtProgress(offset=5000, total=10000)}),
        courts=["scotus"],
        usage=[],
    )
    now = ops.build_ops_report(
        generated_at="2026-06-25T00:00:00+00:00",
        runs=[],
        progress=SeedProgress(courts={"scotus": CourtProgress(offset=5000, total=10000)}),
        courts=["scotus"],
        usage=[],
        previous=prev,
    )
    assert now.backfill.cases_per_day == 0.0
    assert now.backfill.eta_date is None  # stalled -> no projection


def test_estimate_cost_actions_minutes_and_monthly_projection() -> None:
    runs = [
        _run("run-seed", "success", started="2026-06-24T00:00:00Z", ended="2026-06-24T00:30:00Z"),
        _run("run-seed", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:30:00Z"),
    ]
    cost = ops.estimate_cost(runs, ops.summarize_spend([]))
    assert cost.actions_minutes == 60.0  # two 30-minute runs
    assert cost.actions_cost_usd == round(60 * ops._ACTIONS_USD_PER_MINUTE, 4)  # 0.36
    assert cost.window_days == 2.0
    # $0.36 over 2 days -> $5.40/mo Actions + $55 fixed = $60.40 -> rounded $60.
    assert cost.actions_monthly_usd == 5.4
    assert cost.estimated_monthly_usd == 60.4
    assert cost.fixed_monthly_usd == ops._FIXED_MONTHLY_USD


def test_estimate_cost_single_run_has_no_window_or_projection() -> None:
    runs = [
        _run("run-seed", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:30:00Z")
    ]
    cost = ops.estimate_cost(runs, ops.summarize_spend([]))
    assert cost.actions_minutes == 30.0
    assert cost.window_days is None  # need >1 run to span a window
    assert cost.actions_monthly_usd is None
    assert cost.estimated_monthly_usd is None


def test_render_markdown_smoke() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[
            _run(
                "run-seed", "failure", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:10:00Z"
            )
        ],
        progress=SeedProgress(
            snapshot="2026-03-31", courts={"scotus": CourtProgress(offset=4000, total=8000)}
        ),
        courts=["scotus"],
        usage=[_usage("a", 0.25)],
    )
    md = ops.render_markdown(report)
    assert "# Ops dashboard" in md
    assert "## Pipeline health" in md and "run-seed" in md
    assert "## Backfill progress" in md and "scotus" in md
    assert "## Spend (model usage)" in md and "$0.25" in md


def test_render_markdown_handles_empty_health() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[],
        progress=SeedProgress(),
        courts=[],
        usage=[],
    )
    md = ops.render_markdown(report)
    assert "_No runs in the window._" in md


# --- data health --------------------------------------------------------------


def _healthy() -> DataHealth:
    return DataHealth(
        ok=True,
        ledger=LedgerValidation(ok=True, checked=12, invalid=0),
        corpus=CorpusValidation(
            ok=True, corpus_rows=500, checks=[CorpusCheck(name="corpus_opens", passed=True)]
        ),
    )


def _failing() -> DataHealth:
    return DataHealth(
        ok=False,
        ledger=LedgerValidation(ok=True, checked=12, invalid=0),
        corpus=CorpusValidation(
            ok=False,
            corpus_rows=500,
            checks=[
                CorpusCheck(name="corpus_opens", passed=True),
                CorpusCheck(
                    name="row_count_monotonic",
                    passed=False,
                    failures=1,
                    problems=["row count 10 dropped below baseline 20"],
                ),
            ],
        ),
    )


def test_render_scope_audit_tabulates_exclusions_and_recoverable() -> None:
    audit = CorpusScopeAudit(
        skipped=False,
        corpus_rows=1000,
        scotus_open_events=50,
        exclusions=[
            ScopeExclusion(
                reason="stale unresolvable old SCOTUS petition (#333)",
                cases=32,
                open_events=32,
                recoverable=12,
            ),
            ScopeExclusion(
                reason="pre-1925 mandatory-jurisdiction matter (#309)",
                cases=15,
                open_events=15,
                recoverable=0,
            ),
        ],
        unclassified=[
            ScopeUnclassified(
                reason="docket Term not parseable (a format the predicate skips)", open_events=3
            )
        ],
        unparseable_docket_shapes=[ScopeDocketShape(shape="99A999", count=3)],
    )
    md = ops.render_scope_audit(audit)
    assert "## Out-of-scope open events" in md
    assert "**47** of 50 open SCOTUS event(s) are out of scope" in md
    assert "**12** carry a disposition signal" in md
    assert "| stale unresolvable old SCOTUS petition (#333) | 32 | 32 | 12 |" in md
    # The #343 refinement breakdown renders too.
    assert "the #343 refinement signal" in md
    assert "| docket Term not parseable (a format the predicate skips) | 3 |" in md
    # …and the docket-shape histogram that targets the parser broadening.
    assert "| `99A999` | 3 |" in md


def test_render_scope_audit_clean_and_skipped() -> None:
    clean = ops.render_scope_audit(CorpusScopeAudit(scotus_open_events=12))
    assert "all 12 open SCOTUS event(s) are in scope" in clean
    skipped = ops.render_scope_audit(CorpusScopeAudit(skipped=True))
    assert "skipped (no corpus pulled)" in skipped


def test_render_markdown_includes_scope_audit_when_present() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-30T00:00:00+00:00",
        runs=[],
        progress=SeedProgress(courts={}),
        courts=[],
        usage=[],
        scope_audit=CorpusScopeAudit(
            scotus_open_events=10,
            exclusions=[
                ScopeExclusion(
                    reason="stale unresolvable old SCOTUS petition (#333)",
                    cases=3,
                    open_events=3,
                    recoverable=1,
                )
            ],
        ),
    )
    assert report.scope_audit is not None
    assert "## Out-of-scope open events" in ops.render_markdown(report)


def test_render_data_health_healthy_has_no_failure_table() -> None:
    md = ops.render_data_health(_healthy())
    assert "## Data health" in md
    assert "✅ Healthy" in md
    assert "Ledger schema" in md and "12 artifact(s) valid" in md
    assert "Corpus integrity" in md and "1/1 check(s) over 500 row(s)" in md
    assert "| Check | Failures | Sample |" not in md


def test_render_data_health_surfaces_monitored_within_baseline() -> None:
    # A passed check with non-zero failures (e.g. case_dates_ordered within the #171
    # baseline) is healthy overall but its count is still surfaced for the monitor.
    health = DataHealth(
        ok=True,
        ledger=LedgerValidation(ok=True, checked=12, invalid=0),
        corpus=CorpusValidation(
            ok=True,
            corpus_rows=500,
            checks=[
                CorpusCheck(name="corpus_opens", passed=True),
                CorpusCheck(
                    name="case_dates_ordered",
                    passed=True,
                    failures=20,
                    detail="0 future-dated, 20 decided-before-filed vs accepted baseline 50",
                ),
            ],
        ),
    )
    md = ops.render_data_health(health)
    assert "✅ Healthy" in md
    assert "| Check | Failures | Sample |" not in md  # not a failure
    assert "Monitored (within accepted baselines)" in md
    assert "case_dates_ordered: 0 future-dated, 20 decided-before-filed" in md


def test_render_data_health_failing_lists_each_failed_check() -> None:
    md = ops.render_data_health(_failing())
    assert "❌ Failing" in md
    assert "| Check | Failures | Sample |" in md
    assert "row_count_monotonic" in md
    assert "dropped below baseline" in md
    # A passing check never appears in the failure table.
    assert "| corpus_opens |" not in md


def test_render_data_health_skipped_corpus_reads_as_not_run() -> None:
    md = ops.render_data_health(
        DataHealth(ok=True, ledger=LedgerValidation(ok=True, checked=3), corpus=None)
    )
    assert "_no verdict yet_" in md


def test_render_markdown_includes_data_health_when_present() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[],
        progress=SeedProgress(),
        courts=[],
        usage=[],
        data_health=_failing(),
    )
    md = ops.render_markdown(report)
    assert "## Data health" in md and "row_count_monotonic" in md
    # Round-trips through the strict schema.
    assert OpsReport.model_validate(report.model_dump()) == report


def test_render_markdown_omits_data_health_when_absent() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[],
        progress=SeedProgress(),
        courts=[],
        usage=[],
    )
    assert report.data_health is None
    assert "## Data health" not in ops.render_markdown(report)


# --- agent-flags digest -------------------------------------------------------


def _flags(run_id: str, *flags: AgentFlag, case: str = "ca9/1", actor: str = "p") -> AgentFlags:
    return AgentFlags(
        case_id=case, run_id=run_id, role=UsageRole.predictor, actor_id=actor, flags=list(flags)
    )


def test_summarize_flags_counts_every_flag_and_caps_recent_newest_first() -> None:
    older = _flags(
        "20260101T000000Z",
        AgentFlag(category=FlagCategory.scope, severity=FlagSeverity.info, message="old"),
    )
    newer = _flags(
        "20260201T000000Z",
        AgentFlag(category=FlagCategory.blocked, severity=FlagSeverity.blocker, message="stuck"),
        AgentFlag(category=FlagCategory.data_quality, severity=FlagSeverity.warning, message="odd"),
    )
    digest = ops.summarize_flags([older, newer], limit=1)
    # Counts cover every committed flag, not just the capped recent window.
    assert (digest.total, digest.cells) == (3, 2)
    assert (digest.blockers, digest.warnings, digest.infos) == (1, 1, 1)
    # Newest run first, and the cap keeps only the most recent cell.
    assert [fs.run_id for fs in digest.recent] == ["20260201T000000Z"]


def test_summarize_flags_empty_is_all_zero() -> None:
    digest = ops.summarize_flags([])
    assert (digest.total, digest.cells, digest.recent) == (0, 0, [])


def test_render_flags_digest_lists_recent_and_notes_truncation() -> None:
    sets = [
        _flags(
            f"202602{n:02d}T000000Z",
            AgentFlag(category=FlagCategory.other, severity=FlagSeverity.info, message=f"n{n}"),
            actor=f"p{n}",
        )
        for n in range(1, 4)
    ]
    md = ops.render_flags_digest(ops.summarize_flags(sets, limit=2))
    assert "## Agent flags" in md
    assert "**3** flag(s) across **3** cell(s)" in md
    assert "showing the 2 most recent" in md
    # The shared collect table renders the triage columns.
    assert "| severity | category | actor | case | event | note |" in md
    # Only the two most recent cells appear in the table.
    assert "`p3`" in md and "`p2`" in md and "`p1`" not in md


def test_render_flags_digest_clean_ledger_reads_as_none() -> None:
    assert "_No agent flags on record._" in ops.render_flags_digest(ops.summarize_flags([]))


def _tooling(
    run_id: str,
    *,
    used: bool = True,
    helpful: list[str] | None = None,
    gaps: list[str] | None = None,
    actor: str = "p",
    base_rates: bool = False,
) -> AgentToolingFeedback:
    return AgentToolingFeedback(
        case_id="ca9/1",
        run_id=run_id,
        role=UsageRole.predictor,
        actor_id=actor,
        used_corpus_query=used,
        used_base_rates=base_rates,
        helpful=helpful or [],
        gaps=gaps or [],
    )


def test_summarize_tooling_counts_corpus_use_and_ranks_items() -> None:
    reports = [
        _tooling(
            "20260101T000000Z",
            used=True,
            base_rates=True,
            helpful=["query"],
            gaps=["a citation tool"],
        ),
        _tooling("20260102T000000Z", used=True, helpful=["query"], gaps=["docket diff"]),
        _tooling("20260103T000000Z", used=False, helpful=["MCP"], gaps=["a citation tool"]),
    ]
    digest = ops.summarize_tooling(reports, recent_limit=2)
    assert digest.reports == 3
    assert digest.corpus_query_uses == 2
    assert digest.base_rate_uses == 1
    # Most-mentioned first: "query" (2) ahead of "MCP" (1); gaps the same way.
    assert [(c.label, c.count) for c in digest.helpful] == [("query", 2), ("MCP", 1)]
    assert digest.gaps[0].label == "a citation tool" and digest.gaps[0].count == 2
    # recent is newest-first and capped.
    assert [r.run_id for r in digest.recent] == ["20260103T000000Z", "20260102T000000Z"]


def test_summarize_tooling_empty_is_zero() -> None:
    digest = ops.summarize_tooling([])
    assert (digest.reports, digest.corpus_query_uses, digest.helpful, digest.gaps) == (0, 0, [], [])


def test_render_tooling_digest_shows_share_and_items() -> None:
    md = ops.render_tooling_digest(
        ops.summarize_tooling(
            [
                _tooling("r1", used=True, base_rates=True, helpful=["query"]),
                _tooling("r2", used=False, gaps=["x"]),
            ]
        )
    )
    assert "## Agent tooling feedback" in md
    assert "used by **1/2**" in md
    assert "base-rate `stats` by **1/2**" in md
    assert "Most helpful" in md and "query" in md
    assert "Wished-for / missing" in md and "x" in md


def test_render_tooling_digest_empty_reads_as_none() -> None:
    assert "_No tooling reports on record._" in ops.render_tooling_digest(ops.summarize_tooling([]))


def test_ops_report_rolls_up_committed_tooling(tmp_path: Path) -> None:
    report = _tooling("20260615T000000Z", used=True, helpful=["fedcourts query"], actor="codex")
    path = (
        tmp_path
        / "data/cases/ca9/1/events/evt-motion-x/predictions/codex/20260615T000000Z/tooling.json"
    )
    path.parent.mkdir(parents=True)
    path.write_text(report.model_dump_json())

    json_out = tmp_path / "ops.json"
    result = runner.invoke(app, ["ops-report", "--json", str(json_out)], env=_ops_env(tmp_path))
    assert result.exit_code == 0, result.output
    assert "## Agent tooling feedback" in result.output and "fedcourts query" in result.output

    parsed = json.loads(json_out.read_text())
    assert parsed["tooling"]["reports"] == 1 and parsed["tooling"]["corpus_query_uses"] == 1
    assert parsed["tooling"]["helpful"][0]["label"] == "fedcourts query"


def test_render_markdown_includes_agent_flags_section() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[],
        progress=SeedProgress(),
        courts=[],
        usage=[],
        flags=[
            _flags(
                "20260601T000000Z",
                AgentFlag(
                    category=FlagCategory.scope, severity=FlagSeverity.warning, message="check"
                ),
            )
        ],
    )
    md = ops.render_markdown(report)
    assert "## Agent flags" in md and "1 warning" in md
    # The digest round-trips through the strict schema.
    assert OpsReport.model_validate(report.model_dump()) == report


# --- ops-report CLI: data-health wiring ---------------------------------------

runner = CliRunner()


def _ops_env(tmp_path: Path) -> dict[str, str]:
    """An isolated CLI env: empty data/ + a tracking.yaml whose cursor is a fresh path."""
    config_root = tmp_path / "config"
    config_root.mkdir(exist_ok=True)
    (config_root / "tracking.yaml").write_text(
        f"seed:\n  cursor: {tmp_path / 'seed-progress.yaml'}\n"
    )
    return {
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
    }


def test_ops_report_folds_in_corpus_verdict_and_writes_data_health(tmp_path: Path) -> None:
    verdict = CorpusValidation(
        ok=False,
        corpus_rows=42,
        checks=[
            CorpusCheck(name="corpus_opens", passed=True),
            CorpusCheck(
                name="ledger_references_exist",
                passed=False,
                failures=2,
                problems=["outcome X: case is not in the corpus"],
            ),
        ],
    )
    verdict_path = tmp_path / "corpus-validation.json"
    verdict_path.write_text(verdict.model_dump_json())
    json_out = tmp_path / "ops.json"
    dh_out = tmp_path / "data-health.md"

    result = runner.invoke(
        app,
        [
            "ops-report",
            "--corpus-validation",
            str(verdict_path),
            "--json",
            str(json_out),
            "--data-health-out",
            str(dh_out),
            "--generated-at",
            "2026-06-27T00:00:00+00:00",
        ],
        env=_ops_env(tmp_path),
    )
    assert result.exit_code == 0, result.output
    assert "## Data health" in result.output and "❌ Failing" in result.output

    report = json.loads(json_out.read_text())
    assert report["data_health"]["ok"] is False
    assert report["data_health"]["corpus"]["corpus_rows"] == 42
    # The git-only ledger check ran too (empty tree -> a pass).
    assert report["data_health"]["ledger"]["ok"] is True

    body = dh_out.read_text()
    assert "ledger_references_exist" in body


def test_ops_report_without_corpus_verdict_still_has_ledger_health(tmp_path: Path) -> None:
    json_out = tmp_path / "ops.json"
    result = runner.invoke(app, ["ops-report", "--json", str(json_out)], env=_ops_env(tmp_path))
    assert result.exit_code == 0, result.output
    report = json.loads(json_out.read_text())
    # Corpus half absent, ledger half present -> overall ok from the ledger alone.
    assert report["data_health"]["corpus"] is None
    assert report["data_health"]["ledger"]["ok"] is True
    assert report["data_health"]["ok"] is True


def test_ops_report_rolls_up_committed_flags(tmp_path: Path) -> None:
    flags = _flags(
        "20260615T000000Z",
        AgentFlag(category=FlagCategory.scope, severity=FlagSeverity.warning, message="ambiguous"),
        case="ca9/123",
        actor="claude-baseline",
    )
    flags_path = (
        tmp_path
        / "data/cases/ca9/123/events/evt-motion-x/predictions/claude-baseline/20260615T000000Z"
        / "flags.json"
    )
    flags_path.parent.mkdir(parents=True)
    flags_path.write_text(flags.model_dump_json())

    json_out = tmp_path / "ops.json"
    result = runner.invoke(app, ["ops-report", "--json", str(json_out)], env=_ops_env(tmp_path))
    assert result.exit_code == 0, result.output
    assert "## Agent flags" in result.output and "ambiguous" in result.output

    report = json.loads(json_out.read_text())
    assert report["flags"]["total"] == 1 and report["flags"]["warnings"] == 1
    assert report["flags"]["recent"][0]["actor_id"] == "claude-baseline"
