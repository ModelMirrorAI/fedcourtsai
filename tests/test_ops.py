import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, ops
from fedcourtsai.cli import app
from fedcourtsai.leaderboard import Stratum
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    AgentToolingFeedback,
    BaseRateBucket,
    ConferenceBucket,
    CorpusCheck,
    CorpusValidation,
    DataHealth,
    DispositionShare,
    Engine,
    Evaluation,
    FlagCategory,
    FlagSeverity,
    GroupBy,
    LeakageAssessment,
    LedgerValidation,
    LiveFrontier,
    ModelUsage,
    OpsReport,
    StatPack,
    StatPackSection,
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
        _run("run-pull", "success", started="2026-06-24T00:00:00Z", ended="2026-06-24T00:30:00Z"),
        _run("run-pull", "failure", started="2026-06-25T00:00:00Z", ended="2026-06-25T00:10:00Z"),
        _run("run-pull", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:50:00Z"),
        # An in-progress run is not "completed": excluded from rate + durations.
        {
            "workflowName": "run-pull",
            "status": "in_progress",
            "conclusion": None,
            "createdAt": "2026-06-26T01:00:00Z",
        },
    ]
    (health,) = ops.summarize_health(runs)
    assert health.workflow == "run-pull"
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
        _run(
            "run-analytics", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:40:00Z"
        ),
    ]
    assert [h.workflow for h in ops.summarize_health(runs)] == ["run-analytics", "run-pull"]


def test_summarize_health_empty() -> None:
    assert ops.summarize_health([]) == []


def _usage(
    actor: str,
    cost: float,
    *,
    in_tok: int = 100,
    out_tok: int = 10,
    created_at: datetime | None = None,
) -> ModelUsage:
    return ModelUsage(
        case_id="ca9/1",
        event_id="evt-x",
        run_id="20260626T000000Z",
        role=UsageRole.predictor,
        actor_id=actor,
        engine=Engine.claude_code,
        model="claude-opus-4-8",
        created_at=created_at or datetime(2026, 6, 26),
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
    assert spend.window_days is None


def test_summarize_spend_window_spans_the_ledgers_own_stamps() -> None:
    spend = ops.summarize_spend(
        [
            _usage("a", 0.10, created_at=datetime(2026, 6, 24)),
            _usage("b", 0.30, created_at=datetime(2026, 6, 28)),
        ]
    )
    assert spend.window_days == 4.0


@pytest.mark.parametrize(
    ("stamps", "why"),
    [
        ([datetime(2026, 6, 24)], "one record spans nothing"),
        ([datetime(2026, 6, 24), datetime(2026, 6, 24)], "a same-instant batch spans nothing"),
    ],
)
def test_summarize_spend_leaves_an_unspanned_ledger_unrated(
    stamps: list[datetime], why: str
) -> None:
    spend = ops.summarize_spend([_usage("a", 0.10, created_at=s) for s in stamps])
    assert spend.window_days is None, why


def test_build_report_is_passed_the_clock_and_validates() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[
            _run(
                "run-pull", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:40:00Z"
            )
        ],
        usage=[_usage("a", 0.25)],
    )
    assert report.generated_at == "2026-06-26T12:00:00+00:00"
    # Round-trips through the strict schema (this is what `validate` would check).
    assert OpsReport.model_validate(report.model_dump()) == report


def test_estimate_cost_actions_minutes_and_monthly_projection() -> None:
    runs = [
        _run("run-pull", "success", started="2026-06-24T00:00:00Z", ended="2026-06-24T00:30:00Z"),
        _run("run-pull", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:30:00Z"),
    ]
    cost = ops.estimate_cost(runs, ops.summarize_spend([]))
    assert cost.actions_minutes == 60.0  # two 30-minute runs
    # Public repo: standard runners are free, so minutes carry no dollar cost.
    assert cost.actions_cost_usd == 0.0
    assert ops._ACTIONS_USD_PER_MINUTE == 0.0
    assert cost.window_days == 2.0
    # $0 Actions over 2 days -> the projection reduces to the fixed infra.
    assert cost.actions_monthly_usd == 0.0
    assert cost.estimated_monthly_usd == ops._FIXED_MONTHLY_USD
    assert cost.fixed_monthly_usd == ops._FIXED_MONTHLY_USD


def test_estimate_cost_single_run_has_no_window_or_projection() -> None:
    runs = [
        _run("run-pull", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:30:00Z")
    ]
    cost = ops.estimate_cost(runs, ops.summarize_spend([]))
    assert cost.actions_minutes == 30.0
    assert cost.window_days is None  # need >1 run to span a window
    assert cost.actions_monthly_usd is None
    # Actions is free here, so an unrateable Actions window omits nothing: the
    # total still lands. Only a known-*nonzero* unrateable component blanks it.
    assert cost.estimated_monthly_usd == ops._FIXED_MONTHLY_USD


def test_estimate_cost_quiet_week_still_reports_the_model_rate() -> None:
    """A degraded Actions window must degrade its own cell, not the headline.

    Regression: the projection was suppressed whenever `actions_monthly` was None,
    so too few dated runs (a quiet week, or a degraded `gh run list`) erased a
    fully-rated model figure — blanking the number the dashboard exists to show.
    """
    one_run = [
        _run("run-pull", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:30:00Z")
    ]
    spend = ops.summarize_spend(
        [
            _usage("a", 20.0, created_at=datetime(2026, 6, 20)),
            _usage("b", 40.0, created_at=datetime(2026, 6, 26)),
        ]
    )
    cost = ops.estimate_cost(one_run, spend)

    assert cost.actions_monthly_usd is None  # the degraded component
    assert cost.model_monthly_usd == 300.0  # the rated one survives
    assert cost.estimated_monthly_usd == 300.0 + ops._FIXED_MONTHLY_USD


def _two_day_runs() -> list[dict[str, object]]:
    return [
        _run("run-pull", "success", started="2026-06-24T00:00:00Z", ended="2026-06-24T00:30:00Z"),
        _run("run-pull", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:30:00Z"),
    ]


def test_estimate_cost_projects_model_spend_into_the_run_rate() -> None:
    """The dominant variable cost must be rated, not just reported cumulatively.

    Regression: the projection was `actions + fixed`, so the headline run-rate was
    the infra alone ($55/mo) while the tournament was burning orders of magnitude
    more — the reading that missed a cap breach.
    """
    # $60 of model spend over a 6-day ledger span -> $10/day -> $300/mo.
    spend = ops.summarize_spend(
        [
            _usage("a", 20.0, created_at=datetime(2026, 6, 20)),
            _usage("b", 40.0, created_at=datetime(2026, 6, 26)),
        ]
    )
    assert spend.window_days == 6.0
    cost = ops.estimate_cost(_two_day_runs(), spend)

    assert cost.model_monthly_usd == 300.0
    assert cost.model_cost_usd == 60.0  # cumulative still reported alongside the rate
    # Actions is free here, so the all-in total is the model rate plus fixed infra.
    assert cost.estimated_monthly_usd == 300.0 + ops._FIXED_MONTHLY_USD
    assert cost.estimated_monthly_usd != ops._FIXED_MONTHLY_USD


def test_estimate_cost_withholds_a_total_it_cannot_honestly_compute() -> None:
    """Recorded spend with no span to rate -> no projection, rather than infra alone."""
    spend = ops.summarize_spend([_usage("a", 500.0, created_at=datetime(2026, 6, 26))])
    assert (spend.estimated_cost_usd, spend.window_days) == (500.0, None)

    cost = ops.estimate_cost(_two_day_runs(), spend)
    assert cost.model_monthly_usd is None
    assert cost.estimated_monthly_usd is None, "a total omitting $500 of spend would mislead"


def test_estimate_cost_still_totals_when_the_ledger_is_genuinely_empty() -> None:
    """No spend recorded is not unrated spend — the infra-only total is correct."""
    cost = ops.estimate_cost(_two_day_runs(), ops.summarize_spend([]))
    assert cost.model_monthly_usd is None
    assert cost.estimated_monthly_usd == ops._FIXED_MONTHLY_USD


def test_estimate_cost_rates_a_sub_day_span_at_full_precision() -> None:
    """The divisor is the raw span, so display rounding cannot move the rate.

    Regression: `window_days` was persisted as `round(span, 1)` and used as the
    divisor. A 70-minute ledger rounded to `0.0` — stored, not None, because it
    still passed `span > 0` — which unrated a real rate and rendered as `0d`.
    """
    spend = ops.summarize_spend(
        [
            _usage("a", 15.0, created_at=datetime(2026, 6, 26, 0, 0)),
            _usage("b", 15.0, created_at=datetime(2026, 6, 26, 1, 10)),
        ]
    )
    # 70 minutes, carried unrounded rather than collapsing to 0.0.
    assert spend.window_days == pytest.approx(70 / 1440)

    cost = ops.estimate_cost(_two_day_runs(), spend)
    # $30 over 70 min -> $30 * (1440/70) per day * 30 days.
    assert cost.model_monthly_usd == pytest.approx(30 * (1440 / 70) * 30, rel=1e-3)
    assert cost.estimated_monthly_usd is not None


def test_summarize_spend_tolerates_a_naive_ledger_stamp() -> None:
    """One malformed agent-written stamp must not crash the whole ops report."""
    spend = ops.summarize_spend(
        [
            _usage("a", 10.0, created_at=datetime(2026, 6, 20)),
            _usage("b", 10.0, created_at=datetime(2026, 6, 24, tzinfo=UTC)),
        ]
    )
    assert spend.window_days == pytest.approx(4.0)


def test_render_surfaces_the_model_rate_not_just_the_cumulative_total() -> None:
    """Both operator-facing surfaces must name the rate the fix exists to expose."""
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=_two_day_runs(),
        usage=[
            _usage("a", 20.0, created_at=datetime(2026, 6, 20)),
            _usage("b", 40.0, created_at=datetime(2026, 6, 26)),
        ],
    )
    assert report.cost.model_monthly_usd == 300.0

    all_in = f"{300.0 + ops._FIXED_MONTHLY_USD:,.0f}"
    body = ops.render_markdown(report)
    assert "model $300/mo" in body
    assert "$60.00 cumulative over 6.0d of ledger" in body
    assert f"Run-rate **~${all_in}/mo** projected" in body

    digest = ops.render_weekly_digest(report)
    assert "(~$300/mo while running)" in digest
    assert f"~${all_in}/mo projected all-in" in digest


def test_render_digest_says_unrated_rather_than_implying_zero_spend() -> None:
    """The None branch must read as 'not computed', never as a small number."""
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=_two_day_runs(),
        usage=[_usage("a", 500.0)],  # one record -> no span -> unrateable
    )
    assert report.cost.estimated_monthly_usd is None

    digest = ops.render_weekly_digest(report)
    assert "$500.00 model spend cumulative (unrated while running)" in digest
    assert "~— projected all-in" in digest


def test_render_markdown_smoke() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[
            _run(
                "run-pull", "failure", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:10:00Z"
            )
        ],
        usage=[_usage("a", 0.25)],
    )
    md = ops.render_markdown(report)
    assert "# Ops dashboard" in md
    assert "## Pipeline health" in md and "run-pull" in md
    # Spend and cost are one merged section, not two.
    assert "## Spend & cost" in md and "$0.25" in md
    assert "Run-rate" in md and "## Cost run-rate" not in md


def test_render_markdown_handles_empty_health() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[],
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


def test_render_data_health_healthy_has_no_failure_table() -> None:
    md = ops.render_data_health(_healthy())
    assert "## Data health" in md
    assert "✅ Healthy" in md
    assert "Ledger schema" in md and "12 artifact(s) valid" in md
    assert "Corpus integrity" in md and "1/1 check(s) over 500 row(s)" in md
    assert "| Check | Failures | Sample |" not in md


def test_render_data_health_surfaces_monitored_within_baseline() -> None:
    # A passed check with non-zero failures (e.g. case_dates_ordered within its
    # accepted baseline) is healthy overall but its count is still surfaced for the monitor.
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
        usage=[],
    )
    assert report.data_health is None
    assert "## Data health" not in ops.render_markdown(report)


def test_render_markdown_healthy_data_health_is_one_line() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[],
        usage=[],
        data_health=_healthy(),
    )
    md = ops.render_markdown(report)
    # A green verdict collapses to a single line — no full section, no detail table.
    assert "**Data health:** ✅ Healthy." in md
    assert "## Data health" not in md and "Ledger schema" not in md


def test_render_markdown_hides_dormant_workflows() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[
            _run(
                "run-pull", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:05:00Z"
            ),
            # Dormant: only skipped runs, so it counts no successes or failures.
            _run(
                "run-seed", "skipped", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:00:01Z"
            ),
        ],
        usage=[],
    )
    md = ops.render_markdown(report)
    assert "| run-pull |" in md
    assert "| run-seed |" not in md
    assert "1 dormant workflow(s) with no runs in the window hidden" in md


# --- agent-flags digest -------------------------------------------------------


def _flags(run_id: str, *flags: AgentFlag, case: str = "ca9/1", actor: str = "p") -> AgentFlags:
    return AgentFlags(
        case_id=case, run_id=run_id, role=UsageRole.predictor, actor_id=actor, flags=list(flags)
    )


def test_summarize_flags_counts_in_window_and_caps_recent_newest_first() -> None:
    older = _flags(
        "20260101T000000Z",
        AgentFlag(category=FlagCategory.scope, severity=FlagSeverity.info, message="old"),
    )
    newer = _flags(
        "20260201T000000Z",
        AgentFlag(category=FlagCategory.blocked, severity=FlagSeverity.blocker, message="stuck"),
        AgentFlag(category=FlagCategory.data_quality, severity=FlagSeverity.warning, message="odd"),
    )
    # A window wide enough to hold both cells: counts cover every in-window flag.
    digest = ops.summarize_flags(
        [older, newer], generated_at="2026-02-05T00:00:00+00:00", window_days=60, limit=1
    )
    assert (digest.total, digest.cells) == (3, 2)
    assert (digest.blockers, digest.warnings, digest.infos) == (1, 1, 1)
    assert digest.archived == 0
    # Newest run first, and the cap keeps only the most recent cell.
    assert [fs.run_id for fs in digest.recent] == ["20260201T000000Z"]


def test_summarize_flags_windows_out_old_flags_but_keeps_them_archived() -> None:
    older = _flags(
        "20260101T000000Z",
        AgentFlag(category=FlagCategory.scope, severity=FlagSeverity.info, message="old"),
    )
    newer = _flags(
        "20260201T000000Z",
        AgentFlag(category=FlagCategory.data_quality, severity=FlagSeverity.warning, message="odd"),
    )
    # The default 14-day window from just after `newer` excludes the month-old cell,
    # which is counted as archived (it stays in the ledger, out of the summary).
    digest = ops.summarize_flags([older, newer], generated_at="2026-02-05T00:00:00+00:00")
    assert (digest.total, digest.cells) == (1, 1)
    assert digest.window_days == ops._AGENT_DIGEST_WINDOW_DAYS
    assert digest.archived == 1
    assert [fs.run_id for fs in digest.recent] == ["20260201T000000Z"]


def test_summarize_flags_tolerates_naive_generated_at_and_unparseable_run_id() -> None:
    older = _flags(
        "20260101T000000Z",
        AgentFlag(category=FlagCategory.scope, severity=FlagSeverity.info, message="old"),
    )
    newer = _flags(
        "20260201T000000Z",
        AgentFlag(category=FlagCategory.data_quality, severity=FlagSeverity.warning, message="odd"),
    )
    # An unparseable run id counts as in-window (surfaced, not silently dropped).
    weird = _flags(
        "not-a-timestamp",
        AgentFlag(category=FlagCategory.other, severity=FlagSeverity.info, message="?"),
    )
    # A hand-passed *naive* generated_at (no offset) must not crash; treated as UTC.
    digest = ops.summarize_flags([older, newer, weird], generated_at="2026-02-05T00:00:00")
    # `newer` (4d) and the unparseable cell are in the 14-day window; `older` (35d) is not.
    assert (digest.total, digest.cells) == (2, 2)
    assert digest.archived == 1
    assert {fs.run_id for fs in digest.recent} == {"20260201T000000Z", "not-a-timestamp"}


def test_render_flags_digest_empty_in_window_notes_archived_older() -> None:
    old = _flags(
        "20260101T000000Z",
        AgentFlag(category=FlagCategory.scope, severity=FlagSeverity.info, message="old"),
    )
    # Generated months later: nothing is in-window, but the old flag is counted archived.
    md = ops.render_flags_digest(
        ops.summarize_flags([old], generated_at="2026-06-01T00:00:00+00:00")
    )
    assert "_No flags in the last 14d._" in md
    assert "1 older flag(s) archived in the ledger." in md


def test_summarize_flags_empty_is_all_zero() -> None:
    digest = ops.summarize_flags([], generated_at="2026-02-05T00:00:00+00:00")
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
    md = ops.render_flags_digest(
        ops.summarize_flags(sets, generated_at="2026-02-03T12:00:00+00:00", limit=2)
    )
    assert "### Flags" in md
    assert "**3** flag(s) across **3** cell(s)" in md and "last 14d" in md
    assert "showing the 2 most recent" in md
    # The shared collect table renders the triage columns.
    assert "| severity | category | actor | case | event | note |" in md
    # Only the two most recent cells appear in the table.
    assert "`p3`" in md and "`p2`" in md and "`p1`" not in md


def test_render_flags_digest_clean_ledger_reads_as_none() -> None:
    md = ops.render_flags_digest(ops.summarize_flags([], generated_at="2026-02-03T12:00:00+00:00"))
    assert "_No flags in the last 14d._" in md


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
    digest = ops.summarize_tooling(
        reports, generated_at="2026-01-03T12:00:00+00:00", recent_limit=2
    )
    assert digest.reports == 3
    assert digest.corpus_query_uses == 2
    assert digest.base_rate_uses == 1
    # Most-mentioned first: "query" (2) ahead of "MCP" (1); gaps the same way.
    assert [(c.label, c.count) for c in digest.helpful] == [("query", 2), ("MCP", 1)]
    assert digest.gaps[0].label == "a citation tool" and digest.gaps[0].count == 2
    # recent is newest-first and capped.
    assert [r.run_id for r in digest.recent] == ["20260103T000000Z", "20260102T000000Z"]


def test_summarize_tooling_empty_is_zero() -> None:
    digest = ops.summarize_tooling([], generated_at="2026-01-03T12:00:00+00:00")
    assert (digest.reports, digest.corpus_query_uses, digest.helpful, digest.gaps) == (0, 0, [], [])


def test_render_tooling_digest_shows_share_and_items() -> None:
    md = ops.render_tooling_digest(
        ops.summarize_tooling(
            [
                _tooling("r1", used=True, base_rates=True, helpful=["query"]),
                _tooling("r2", used=False, gaps=["x"]),
            ],
            generated_at="2026-01-03T12:00:00+00:00",
        )
    )
    assert "### Tooling feedback" in md
    assert "used by **1/2**" in md
    assert "base-rate `stats` by **1/2**" in md
    assert "Most helpful" in md and "query" in md
    assert "Wished-for / missing" in md and "x" in md


def test_render_tooling_digest_empty_reads_as_none() -> None:
    md = ops.render_tooling_digest(
        ops.summarize_tooling([], generated_at="2026-01-03T12:00:00+00:00")
    )
    assert "_No tooling reports in the last 14d._" in md


def test_ops_report_rolls_up_committed_tooling(tmp_path: Path) -> None:
    report = _tooling("20260615T000000Z", used=True, helpful=["fedcourts query"], actor="codex")
    path = (
        tmp_path
        / "data/cases/ca9/1/events/evt-motion-x/predictions/codex/20260615T000000Z/tooling.json"
    )
    path.parent.mkdir(parents=True)
    path.write_text(report.model_dump_json())

    json_out = tmp_path / "ops.json"
    result = runner.invoke(
        app,
        ["ops-report", "--json", str(json_out), "--generated-at", "2026-06-20T00:00:00+00:00"],
        env=_ops_env(tmp_path),
    )
    assert result.exit_code == 0, result.output
    assert "## Agent signals" in result.output and "### Tooling feedback" in result.output
    assert "fedcourts query" in result.output

    parsed = json.loads(json_out.read_text())
    assert parsed["tooling"]["reports"] == 1 and parsed["tooling"]["corpus_query_uses"] == 1
    assert parsed["tooling"]["helpful"][0]["label"] == "fedcourts query"


def test_render_markdown_includes_agent_flags_section() -> None:
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[],
        usage=[],
        flags=[
            _flags(
                "20260620T000000Z",
                AgentFlag(
                    category=FlagCategory.scope, severity=FlagSeverity.warning, message="check"
                ),
            )
        ],
    )
    md = ops.render_markdown(report)
    assert "## Agent signals (last 14d)" in md
    assert "### Flags" in md and "1 warning" in md
    # The digest round-trips through the strict schema.
    assert OpsReport.model_validate(report.model_dump()) == report


# --- open trigger issues (stalled fan-outs) -------------------------------------


def test_summarize_trigger_issues_filters_and_orders_oldest_first() -> None:
    raw = [
        {
            "number": 387,
            "title": "predict: 4 case(s)",
            "labels": [{"name": "run:predict"}],
            "createdAt": "2026-07-02T08:29:52Z",
        },
        # Not a trigger label: dropped (dashboards and trackers are long-lived).
        {
            "number": 117,
            "title": "Ops dashboard",
            "labels": [{"name": "ops-dashboard"}],
            "createdAt": "2026-06-01T00:00:00Z",
        },
        # An older trigger must lead — the longest-stalled first.
        {
            "number": 377,
            "title": "evaluate: 1 case(s)",
            "labels": [{"name": "run:evaluate"}],
            "createdAt": "2026-07-01T14:22:42Z",
        },
    ]
    issues = ops.summarize_trigger_issues(raw)
    assert [(i.number, i.label) for i in issues] == [
        (377, "run:evaluate"),
        (387, "run:predict"),
    ]


def test_render_open_triggers_lists_age_and_labels() -> None:
    issues = ops.summarize_trigger_issues(
        [
            {
                "number": 5,
                "title": "predict: 2 case(s)",
                "labels": [{"name": "run:predict"}],
                "createdAt": "2026-07-01T12:00:00Z",
            }
        ]
    )
    md = ops.render_open_triggers(issues, "2026-07-02T12:00:00Z")
    assert "## Open trigger issues" in md
    assert "| #5 | `run:predict` | 1d |" in md
    assert "re-applying the label" in md


def test_render_open_triggers_empty_is_all_clear() -> None:
    md = ops.render_open_triggers([], "2026-07-02T12:00:00Z")
    assert "None — every fan-out landed or closed" in md


def test_ops_report_carries_open_triggers_into_markdown() -> None:
    report = ops.build_ops_report(
        generated_at="2026-07-02T12:00:00+00:00",
        runs=[],
        usage=[],
        open_triggers=ops.summarize_trigger_issues(
            [
                {
                    "number": 9,
                    "title": "evaluate: 1 case(s)",
                    "labels": [{"name": "run:evaluate"}],
                    "createdAt": "2026-07-02T09:00:00Z",
                }
            ]
        ),
    )
    md = ops.render_markdown(report)
    assert "## Open trigger issues" in md and "| #9 | `run:evaluate` | 3h |" in md
    assert OpsReport.model_validate(report.model_dump()) == report


# --- ops-report CLI: data-health wiring ---------------------------------------

runner = CliRunner()


def _ops_env(tmp_path: Path) -> dict[str, str]:
    """An isolated CLI env: empty data/, config, and metrics roots.

    The metrics root matters: without it the statpack read falls back to the
    repo's real committed ``metrics/statpack.json`` (the path is CWD-relative),
    and these tests' output would change under a future metrics refresh.
    """
    config_root = tmp_path / "config"
    config_root.mkdir(exist_ok=True)
    return {
        "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
        "FEDCOURTS_CONFIG_ROOT": str(config_root),
        "FEDCOURTS_METRICS_ROOT": str(tmp_path / "metrics"),
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
    result = runner.invoke(
        app,
        ["ops-report", "--json", str(json_out), "--generated-at", "2026-06-20T00:00:00+00:00"],
        env=_ops_env(tmp_path),
    )
    assert result.exit_code == 0, result.output
    assert "## Agent signals" in result.output and "### Flags" in result.output
    assert "ambiguous" in result.output

    report = json.loads(json_out.read_text())
    assert report["flags"]["total"] == 1 and report["flags"]["warnings"] == 1
    assert report["flags"]["recent"][0]["actor_id"] == "claude-baseline"


def _leaky_evaluation(
    verdict: str, *, run_id: str = "20260710T120000Z", predictor: str = "claude-baseline"
) -> Evaluation:
    return Evaluation(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        predictor_id=predictor,
        evaluator_id="codex-judge",
        engine="codex",
        run_id=run_id,
        created_at=datetime(2026, 7, 10, 12, tzinfo=UTC),
        correct=1,
        leakage_suspected=verdict in ("possible", "likely"),
        leakage=LeakageAssessment(
            mode="replay" if verdict != "not_applicable" else "forward",
            retrieved_outcome_material=verdict in ("possible", "likely"),
            influenced_prediction=verdict,
        ),
    )


def test_summarize_leakage_buckets_and_names_likely_offenders() -> None:
    evaluations = [
        _leaky_evaluation("not_applicable"),
        _leaky_evaluation("none"),
        _leaky_evaluation("possible"),
        _leaky_evaluation("likely", run_id="20260710T130000Z", predictor="gemini-baseline"),
        # An old-schema record with no leakage block is skipped, not counted.
        _leaky_evaluation("none").model_copy(update={"leakage": None}),
    ]
    digest = ops.summarize_leakage(evaluations, generated_at="2026-07-12T00:00:00+00:00")
    assert (digest.assessed, digest.not_applicable, digest.none) == (4, 1, 1)
    assert (digest.possible, digest.likely) == (1, 1)
    assert digest.flagged == ["scotus/1 evt-petition-disposition gemini-baseline (by codex-judge)"]


def test_summarize_leakage_empty_is_all_zero() -> None:
    digest = ops.summarize_leakage([], generated_at="2026-07-12T00:00:00+00:00")
    assert digest.assessed == 0 and digest.flagged == []


# --- substance: scored cells, calibration, predictor scores, live frontier ------


def _evaluation(
    predictor: str,
    *,
    correct: int = 1,
    brier: float | None = 0.1,
    quality: float | None = 0.8,
    brier_skill: float | None = None,
    run_id: str = "20260701T000000Z",
) -> Evaluation:
    return Evaluation(
        case_id="scotus/1",
        event_id="evt-petition-disposition",
        predictor_id=predictor,
        evaluator_id="codex-judge",
        engine=Engine.codex,
        run_id=run_id,
        created_at=datetime(2026, 7, 1, tzinfo=UTC),
        correct=correct,
        brier_score=brier,
        reasoning_quality=quality,
        brier_skill_score=brier_skill,
    )


def _statpack_with_cert_section(denied: int, granted: int) -> StatPack:
    resolved = denied + granted
    return StatPack(
        sections=[
            StatPackSection(
                title="Modern discretionary-cert petitions by disposition",
                court="scotus",
                cert_stage=True,
                group_by=GroupBy.disposition,
                buckets=[
                    BaseRateBucket(key="denied", cases=denied, resolved=denied),
                    BaseRateBucket(key="granted", cases=granted, resolved=granted),
                ],
            )
        ],
        resolved=resolved,
    )


def _statpack_with_salience_section(band_grants: dict[str, tuple[int, int]]) -> StatPack:
    """A statpack carrying only the pack-wide salience-band section.

    ``band_grants`` maps a band to ``(granted, denied)`` weighted counts.
    """
    return StatPack(
        sections=[
            StatPackSection(
                title="Cert petitions by salience band",
                court="scotus",
                cert_stage=True,
                live_slice=True,
                weighted=True,
                group_by=GroupBy.salience_band,
                buckets=[
                    BaseRateBucket(
                        key=band,
                        cases=granted + denied,
                        resolved=granted + denied,
                        dispositions=[
                            DispositionShare(
                                disposition="granted",
                                count=granted,
                                share=granted / (granted + denied),
                            ),
                            DispositionShare(
                                disposition="denied",
                                count=denied,
                                share=denied / (granted + denied),
                            ),
                        ],
                    )
                    for band, (granted, denied) in band_grants.items()
                ],
            )
        ],
        resolved=sum(g + d for g, d in band_grants.values()),
    )


def test_summarize_substance_segment_base_rate_and_skill() -> None:
    # The segment base rate pools the grant family across bands; the replay skill
    # averages the reported brier_skill_score cells (a forward cell is ignored).
    stratified: list[tuple[Evaluation, Stratum]] = [
        (_evaluation("alpha", brier_skill=0.5, run_id="20260701T000000Z"), "retrospective"),
        (_evaluation("alpha", brier_skill=-0.1, run_id="20260702T000000Z"), "retrospective"),
        (_evaluation("alpha", brier_skill=0.9, run_id="20260703T000000Z"), "forward"),
    ]
    digest = ops.summarize_substance(
        cell_counts=(3, 1, 3),
        stratified_evaluations=stratified,
        # high band 40/60, baseline 2/198 -> pooled grants 42 / 300 resolved = 0.14.
        statpack=_statpack_with_salience_section({"high": (40, 60), "baseline": (2, 198)}),
    )
    cal = digest.calibration
    assert cal.segment_grant_rate == 0.14
    assert cal.segment_base_rate_cases == 300
    assert cal.mean_brier_skill == 0.2  # (0.5 - 0.1) / 2, forward cell excluded


def test_summarize_substance_without_salience_section_leaves_segment_null() -> None:
    digest = ops.summarize_substance(
        cell_counts=(1, 1, 1),
        stratified_evaluations=[(_evaluation("p", brier_skill=None), "retrospective")],
        statpack=StatPack(),  # no salience-band section
    )
    assert digest.calibration.segment_grant_rate is None
    assert digest.calibration.segment_base_rate_cases is None
    assert digest.calibration.mean_brier_skill is None


def test_render_substance_shows_the_segment_base_rate_line() -> None:
    digest = ops.summarize_substance(
        cell_counts=(2, 1, 2),
        stratified_evaluations=[(_evaluation("p", correct=1, brier_skill=0.25), "retrospective")],
        statpack=_statpack_with_salience_section({"high": (30, 70)}),
    )
    md = ops.render_substance(digest)
    assert "Salience-scored segment base grant rate **30%**" in md
    assert "resolved paid-segment petitions" in md
    assert "replay Brier skill vs baseline **+0.250**" in md


def test_summarize_substance_counts_calibration_and_scores() -> None:
    stratified: list[tuple[Evaluation, Stratum]] = [
        (_evaluation("claude-baseline", correct=1, brier=0.05, quality=0.9), "retrospective"),
        (_evaluation("claude-baseline", correct=0, brier=0.4, quality=0.5), "retrospective"),
        (_evaluation("gemini-baseline", correct=1, brier=None, quality=None), "forward"),
    ]
    digest = ops.summarize_substance(
        cell_counts=(6, 4, 3),
        stratified_evaluations=stratified,
        statpack=_statpack_with_cert_section(denied=90, granted=10),
    )
    cells = digest.cells
    assert (cells.predictions, cells.events_predicted, cells.predicted_resolved) == (6, 4, 3)
    assert (cells.evaluations_forward, cells.evaluations_retrospective) == (1, 2)
    assert cells.predictions_delta is None  # no prior snapshot supplied

    cal = digest.calibration
    assert cal.sample == 2  # replay stratum only
    assert cal.mean_brier == 0.225
    assert cal.accuracy == 0.5
    assert cal.deny_base_rate == 0.9 and cal.base_rate_cases == 100
    assert cal.lift_over_always_deny == -0.4

    by_id = {row.predictor_id: row for row in digest.predictor_scores}
    assert by_id["claude-baseline"].evaluations == 2
    assert by_id["claude-baseline"].median == 0.5 or by_id["claude-baseline"].median == 0.9
    assert by_id["gemini-baseline"].median is None  # no quality grades reported


def test_quantiles_are_deterministic_on_an_odd_sample() -> None:
    stratified: list[tuple[Evaluation, Stratum]] = [
        (_evaluation("p", quality=q, run_id=f"2026070{n}T000000Z"), "retrospective")
        for n, q in enumerate((0.2, 0.5, 0.9), start=1)
    ]
    (row,) = ops.summarize_substance(
        cell_counts=(3, 3, 3), stratified_evaluations=stratified
    ).predictor_scores
    assert (row.p25, row.median, row.p75) == (0.2, 0.5, 0.9)


def test_summarize_substance_deltas_come_from_the_previous_snapshot() -> None:
    prior = ops.build_ops_report(
        generated_at="2026-07-04T00:00:00+00:00",
        runs=[],
        usage=[],
        substance=ops.summarize_substance(cell_counts=(4, 3, 1), stratified_evaluations=[]),
    )
    digest = ops.summarize_substance(
        cell_counts=(6, 4, 3),
        stratified_evaluations=[(_evaluation("p"), "retrospective")],
        previous=prior,
    )
    assert digest.cells.predictions_delta == 2
    assert digest.cells.predicted_resolved_delta == 2
    assert digest.cells.evaluations_retrospective_delta == 1
    assert digest.cells.evaluations_forward_delta == 0


def test_summarize_substance_without_base_rate_leaves_lift_null() -> None:
    digest = ops.summarize_substance(
        cell_counts=(1, 1, 1),
        stratified_evaluations=[(_evaluation("p"), "retrospective")],
        statpack=StatPack(),  # no cert-stage section
    )
    assert digest.calibration.accuracy == 1.0
    assert digest.calibration.deny_base_rate is None
    assert digest.calibration.lift_over_always_deny is None


def test_render_substance_suppresses_empty_subsections() -> None:
    digest = ops.summarize_substance(cell_counts=(0, 0, 0), stratified_evaluations=[])
    md = ops.render_substance(digest)
    assert "## Substance (is it producing?)" in md
    assert "Prediction cells committed: **0**" in md
    # An idle instrument shows only the headline line — no empty sub-blocks or
    # "not producing yet" placeholders.
    assert "**Calibration" not in md
    assert "**Evaluation scores by predictor**" not in md
    assert "**Live frontier**" not in md
    assert "yet._" not in md


def test_render_substance_shows_frontier_and_lift() -> None:
    digest = ops.summarize_substance(
        cell_counts=(6, 4, 3),
        stratified_evaluations=[(_evaluation("p", correct=1), "retrospective")],
        statpack=_statpack_with_cert_section(denied=95, granted=5),
        live_frontier=LiveFrontier(
            generated_on=date(2026, 7, 11),
            watchlist=40,
            next_conference=date(2026, 9, 29),
            next_conference_petitions=35,
            conferences=[ConferenceBucket(conference=date(2026, 9, 29), petitions=35)],
            documents_provisioned=28,
        ),
    )
    md = ops.render_substance(digest)
    assert "lift **+5.0%**" in md
    assert "(n=1)" in md
    assert "Watchlist **40** petition(s)" in md
    assert "next conference **2026-09-29** (35 petition(s))" in md
    assert "documents provisioned on **28/40**" in md


def test_render_markdown_includes_substance_when_present() -> None:
    report = ops.build_ops_report(
        generated_at="2026-07-11T00:00:00+00:00",
        runs=[],
        usage=[],
        substance=ops.summarize_substance(cell_counts=(0, 0, 0), stratified_evaluations=[]),
    )
    md = ops.render_markdown(report)
    assert "## Substance (is it producing?)" in md
    assert OpsReport.model_validate(report.model_dump()) == report


# --- the weekly digest ----------------------------------------------------------


def test_render_weekly_digest_asks_the_fixed_questions() -> None:
    report = ops.build_ops_report(
        generated_at="2026-07-11T00:00:00+00:00",
        runs=[],
        usage=[_usage("a", 1.5)],
        substance=ops.summarize_substance(
            cell_counts=(6, 4, 3),
            stratified_evaluations=[
                (_evaluation("p", correct=1), "retrospective"),
                (_evaluation("p", correct=1, run_id="20260702T000000Z"), "forward"),
            ],
            statpack=_statpack_with_cert_section(denied=95, granted=5),
            live_frontier=LiveFrontier(
                generated_on=date(2026, 7, 11),
                watchlist=40,
                next_conference=date(2026, 9, 29),
                next_conference_petitions=35,
                documents_provisioned=28,
            ),
        ),
        open_triggers=ops.summarize_trigger_issues(
            [
                {
                    "number": 9,
                    "title": "evaluate: 1 case(s)",
                    "labels": [{"name": "run:evaluate"}],
                    "createdAt": "2026-07-08T09:00:00Z",
                }
            ]
        ),
    )
    md = ops.render_weekly_digest(report)
    assert "### Weekly digest" in md
    assert "Replay calibration on 1 scored cell(s)" in md and "do you believe it?" in md
    assert "Forward cells scored: 1 total, no prior snapshot to diff" in md
    assert "35 petition(s) distributed for **2026-09-29**" in md and "28/40" in md
    assert "Oldest stalled trigger: `run:evaluate` (2d old)" in md
    assert "Spend vs budget: $1.50" in md


def test_weekly_digest_reports_the_segment_brier_skill_when_present() -> None:
    report = ops.build_ops_report(
        generated_at="2026-07-11T00:00:00+00:00",
        runs=[],
        usage=[],
        substance=ops.summarize_substance(
            cell_counts=(2, 1, 2),
            stratified_evaluations=[
                (_evaluation("p", correct=1, brier_skill=0.3), "retrospective")
            ],
            statpack=_statpack_with_salience_section({"high": (30, 70)}),
        ),
    )
    md = ops.render_weekly_digest(report)
    assert "Brier skill **+0.300** vs the segment base rate" in md


def test_render_weekly_digest_all_absent_still_asks() -> None:
    report = ops.build_ops_report(generated_at="2026-07-11T00:00:00+00:00", runs=[], usage=[])
    md = ops.render_weekly_digest(report)
    assert "No scored replay cells yet" in md
    assert "Stalled triggers: none" in md
    assert "within plan?" in md


# --- lenient prior snapshots ------------------------------------------------------


def test_ops_report_drops_deltas_on_an_incompatible_prior_snapshot(tmp_path: Path) -> None:
    """A prior snapshot carrying since-removed fields (the strict schema rejects
    them) must silently drop the deltas — never fail the daily report."""
    stale = {
        "schema_version": "1.0",
        "generated_at": "2026-07-01T00:00:00+00:00",
        "spend": {
            "runs": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "mean_cost_usd_per_run": 0.0,
        },
        "cost": {
            "actions_minutes": 0.0,
            "actions_cost_usd": 0.0,
            "model_cost_usd": 0.0,
            "fixed_monthly_usd": 55.0,
        },
        "backfill": {"courts_total": 14, "courts_complete": 0, "cases_loaded": 0},
        "scope_audit": {"skipped": True},
    }
    prev = tmp_path / "prev-ops.json"
    prev.write_text(json.dumps(stale))
    json_out = tmp_path / "ops.json"
    result = runner.invoke(
        app,
        ["ops-report", "--previous", str(prev), "--json", str(json_out)],
        env=_ops_env(tmp_path),
    )
    assert result.exit_code == 0, result.output
    parsed = json.loads(json_out.read_text())
    assert parsed["substance"]["cells"]["predictions_delta"] is None


def test_ops_report_writes_the_digest_and_reads_the_frontier(tmp_path: Path) -> None:
    frontier = LiveFrontier(
        generated_on=date(2026, 7, 11),
        watchlist=3,
        next_conference=date(2026, 9, 29),
        next_conference_petitions=3,
        documents_provisioned=2,
    )
    frontier_path = tmp_path / "live-frontier.json"
    frontier_path.write_text(frontier.model_dump_json())
    digest_out = tmp_path / "digest.md"
    result = runner.invoke(
        app,
        [
            "ops-report",
            "--live-frontier",
            str(frontier_path),
            "--digest-out",
            str(digest_out),
            "--generated-at",
            "2026-07-11T00:00:00+00:00",
        ],
        env=_ops_env(tmp_path),
    )
    assert result.exit_code == 0, result.output
    assert "documents provisioned on **2/3**" in result.output
    body = digest_out.read_text()
    assert "### Weekly digest" in body and "3 petition(s) distributed for **2026-09-29**" in body


# --- the live-frontier snapshot CLI ------------------------------------------------


def _watchlist_row(docket: int, number: str, conference: date) -> "corpus.CorpusRow":
    return corpus.CorpusRow(
        case_id=f"scotus/{docket}",
        court="scotus",
        docket_number=number,
        distributed_for_conference=conference,
    )


def test_live_frontier_snapshots_watchlist_and_documents(tmp_path: Path) -> None:
    corpus_root = tmp_path / "corpus"
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _watchlist_row(1, "25-101", date(2026, 9, 29)),
                _watchlist_row(2, "25-102", date(2026, 9, 29)),
                _watchlist_row(3, "25-103", date(2026, 10, 10)),
            ],
        )
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/1",
                    kind="petition",
                    url="https://example/1.pdf",
                    fetched_at=date(2026, 7, 10),
                    text="QUESTION PRESENTED",
                )
            ],
        )
    out = tmp_path / "live-frontier.json"
    result = runner.invoke(
        app,
        ["live-frontier", "--out", str(out), "--today", "2026-07-11"],
        env={"FEDCOURTS_CORPUS_ROOT": str(corpus_root)},
    )
    assert result.exit_code == 0, result.output
    frontier = LiveFrontier.model_validate_json(out.read_text())
    assert frontier.watchlist == 3
    assert frontier.next_conference == date(2026, 9, 29)
    assert frontier.next_conference_petitions == 2
    assert [c.petitions for c in frontier.conferences] == [2, 1]
    assert frontier.documents_provisioned == 1
    assert frontier.skipped is False


def test_live_frontier_skips_gracefully_without_a_corpus(tmp_path: Path) -> None:
    out = tmp_path / "live-frontier.json"
    result = runner.invoke(
        app,
        ["live-frontier", "--out", str(out), "--today", "2026-07-11"],
        env={"FEDCOURTS_CORPUS_ROOT": str(tmp_path / "absent")},
    )
    assert result.exit_code == 0, result.output
    frontier = LiveFrontier.model_validate_json(out.read_text())
    assert frontier.skipped is True and frontier.watchlist == 0


def test_estimate_cost_projection_arithmetic_with_a_nonzero_rate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The public repo prices Actions at zero, which would mask a regression in
    # the projection math — prove the arithmetic with the dormant nonzero path.
    monkeypatch.setattr(ops, "_ACTIONS_USD_PER_MINUTE", 0.006)
    runs = [
        _run("run-pull", "success", started="2026-06-24T00:00:00Z", ended="2026-06-24T00:30:00Z"),
        _run("run-pull", "success", started="2026-06-26T00:00:00Z", ended="2026-06-26T00:30:00Z"),
    ]
    cost = ops.estimate_cost(runs, ops.summarize_spend([]))
    # $0.36 over a 2-day window -> $5.40/mo Actions, plus the fixed infra.
    assert cost.actions_cost_usd == 0.36
    assert cost.actions_monthly_usd == 5.4
    assert cost.estimated_monthly_usd == 5.4 + ops._FIXED_MONTHLY_USD


def test_summarize_health_excludes_label_filter_skips() -> None:
    # The label-triggered workflows complete a skipped run for every unrelated
    # `issues: labeled` event — skips are not executions, so they must not
    # dilute the rate, drag the duration percentiles toward the ~1s skip
    # overhead, or masquerade as the "last" run.
    runs: list[dict[str, object]] = [
        _run(
            "run-predict", "success", started="2026-07-13T10:00:00Z", ended="2026-07-13T10:30:00Z"
        ),
        _run(
            "run-predict", "failure", started="2026-07-13T11:00:00Z", ended="2026-07-13T11:10:00Z"
        ),
        _run(
            "run-predict", "skipped", started="2026-07-13T12:00:00Z", ended="2026-07-13T12:00:01Z"
        ),
        _run(
            "run-predict", "skipped", started="2026-07-13T12:30:00Z", ended="2026-07-13T12:30:01Z"
        ),
    ]
    (health,) = ops.summarize_health(runs)
    assert (health.successes, health.failures) == (1, 1)
    # Rate over conclusive runs only — matching the rendered "(x/y)" fraction.
    assert health.success_rate == 1 / 2
    # Durations exclude the ~1s skips.
    assert health.median_seconds == 600
    # The most recent *execution* is the failure, not the later skips.
    assert health.last_conclusion == "failure"
    assert health.last_run_at == "2026-07-13T11:00:00Z"


def test_summarize_substance_excludes_procedural_cells_from_both_strata() -> None:
    # A mootness-basis (procedural) cell counts in neither timing stratum —
    # the funnel mirrors the leaderboard's segmentation, so no headline
    # metric ever mixes it in.
    stratified: list[tuple[Evaluation, Stratum]] = [
        (_evaluation("claude-baseline", correct=1, brier=0.1, quality=0.8), "forward"),
        (_evaluation("claude-baseline", correct=1, brier=0.0, quality=0.9), "procedural"),
    ]
    digest = ops.summarize_substance(
        cell_counts=(2, 2, 2),
        stratified_evaluations=stratified,
        statpack=None,
    )
    assert (digest.cells.evaluations_forward, digest.cells.evaluations_retrospective) == (1, 0)
