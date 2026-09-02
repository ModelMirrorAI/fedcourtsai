import json
import re
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import cli, corpus, ops
from fedcourtsai.agent_feedback import open_issue_once
from fedcourtsai.cli import app
from fedcourtsai.integrity import forward_claim_record, leakage_record
from fedcourtsai.paths import CasePaths
from fedcourtsai.schemas import (
    AgentFlag,
    AgentFlags,
    AgentToolingFeedback,
    Backtest,
    BacktestCourtScore,
    BacktestEntry,
    BaseRateBucket,
    CertBacktest,
    ClaimProbability,
    ClaimScoreBoard,
    ConferenceBucket,
    CorpusCheck,
    CorpusValidation,
    DataHealth,
    Disposition,
    DispositionShare,
    Engine,
    Evaluation,
    EventKind,
    FlagCategory,
    FlagSeverity,
    FrozenProcessRecord,
    GroupBy,
    Leaderboard,
    LeaderboardEntry,
    LeakageAssessment,
    LedgerValidation,
    LiveFrontier,
    ModelUsage,
    Moment,
    OpsReport,
    Outcome,
    PredictableEvent,
    Prediction,
    SalienceReplay,
    Stage,
    StatPack,
    StatPackSection,
    Stratum,
    UsageRole,
)
from fedcourtsai.serialize import write_json, write_text, write_yaml
from fedcourtsai.spend import SpendVerdict
from fedcourtsai.store import (
    CellCensusRow,
    PredictedEventRef,
    RecentCells,
    iter_predicted_events,
    load_predicted_event,
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
    the fixed infra alone while the tournament was burning orders of magnitude
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


def test_render_markdown_footnotes_a_level_triggered_gate_workflow() -> None:
    """`promote` fails by design until its gates are satisfied, so its rate must not
    read as breakage — the row stays (a broken gate must be visible) and is annotated."""
    report = ops.build_ops_report(
        generated_at="2026-07-27T20:00:00+00:00",
        runs=[
            _run(
                "promote",
                "failure",
                started="2026-07-26T22:04:00Z",
                ended="2026-07-26T22:05:00Z",
            ),
            _run(
                "run-pull",
                "success",
                started="2026-07-27T01:17:00Z",
                ended="2026-07-27T01:20:00Z",
            ),
        ],
        usage=[],
    )
    md = ops.render_markdown(report)
    assert "| promote | failure |" in md  # still shown, never hidden
    assert "promote is level-triggered" in md
    assert "not incidents" in md


def test_render_markdown_omits_the_gate_footnote_when_no_gate_workflow_ran() -> None:
    """The note is scoped to what actually ran, so an ordinary day carries no aside."""
    report = ops.build_ops_report(
        generated_at="2026-07-27T20:00:00+00:00",
        runs=[
            _run(
                "run-pull",
                "success",
                started="2026-07-27T01:17:00Z",
                ended="2026-07-27T01:20:00Z",
            )
        ],
        usage=[],
    )
    assert "level-triggered" not in ops.render_markdown(report)


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
    assert "Monitored (a known condition, not a defect)" in md
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


def test_render_markdown_green_verdict_still_carries_the_monitored_counts() -> None:
    """A monitored count never reddens a verdict, so a green dashboard is the
    only state it ever occurs in — gating it behind the failing branch would
    hide it permanently. The one-line collapse still holds otherwise."""
    health = _healthy().model_copy(
        update={
            "corpus": CorpusValidation(
                ok=True,
                corpus_rows=500,
                checks=[
                    CorpusCheck(name="corpus_opens", passed=True),
                    CorpusCheck(
                        name="docket_numbers_carry_no_capital_marking",
                        passed=True,
                        failures=462,
                        detail="advisory: 462 of 590570 SCOTUS row(s) still carry the marking",
                    ),
                ],
            )
        }
    )
    report = ops.build_ops_report(
        generated_at="2026-06-26T12:00:00+00:00",
        runs=[],
        usage=[],
        data_health=health,
    )
    md = ops.render_markdown(report)
    assert "**Data health:** ✅ Healthy." in md
    assert "Monitored (a known condition, not a defect)" in md
    assert "docket_numbers_carry_no_capital_marking: advisory: 462 of" in md
    # Still collapsed: the monitored lines ride the green line, not a full section.
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
    correct: int | None = 1,
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


def test_substance_accuracy_skips_the_cells_reporting_no_correct() -> None:
    """A null `correct` is a missing figure here too, not a wrong call.

    The stamp clears it where the committed prediction or outcome was
    unreadable, so both the calibration block's replay accuracy and the
    per-predictor row average over the cells that report one — and a predictor
    with none reports no accuracy rather than a zero. `sample` still counts the
    cells, as it does for the Brier beside it.
    """
    stratified: list[tuple[Evaluation, Stratum]] = [
        (_evaluation("scored", correct=1, brier=0.05), "retrospective"),
        (_evaluation("scored", correct=None, brier=None), "retrospective"),
        (_evaluation("unscored", correct=None, brier=None), "retrospective"),
    ]
    digest = ops.summarize_substance(cell_counts=(3, 3, 3), stratified_evaluations=stratified)
    assert digest.calibration.sample == 3
    assert digest.calibration.accuracy == 1.0  # 1/1, not 1/3
    assert digest.calibration.accuracy_scored == 1
    by_id = {row.predictor_id: row for row in digest.predictor_scores}
    assert by_id["scored"].accuracy == 1.0
    assert by_id["scored"].evaluations == 2
    assert by_id["scored"].accuracy_scored == 1
    assert by_id["unscored"].accuracy is None
    assert by_id["unscored"].accuracy_scored == 0
    # The rendered line prints accuracy's own base against the cell count, so a
    # percentage over one cell cannot read as a percentage over three.
    md = ops.render_substance(digest)
    assert "(n=1 of 3)" in md
    assert "| unscored | 1 | — | 0 |" in md


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
    assert md.startswith("<!-- weekly-digest: 2026-W28 -->")
    assert "# Weekly performance digest" in md
    assert "## Health questions" in md
    assert "Replay calibration on 1 scored cell(s)" in md and "do you believe it?" in md
    assert "Forward cells scored (frozen): 1 total, no prior snapshot to diff" in md
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


def test_weekly_digest_reframes_the_shakedown_state_honestly() -> None:
    """The frozen-empty shakedown must not read as a stalled machine: the digest's
    'what is blocking?' / 'is the frontier producing?' questions would mislead when
    the answer is just 'nothing frozen yet'."""
    report = ops.build_ops_report(
        generated_at="2026-07-11T00:00:00+00:00",
        runs=[],
        usage=[],
        # Predictions committed (version-blind census), zero frozen evaluations.
        substance=ops.summarize_substance(
            cell_counts=(410, 137, 5), stratified_evaluations=[], process_scope="frozen"
        ),
    )
    md = ops.render_weekly_digest(report)
    assert "No frozen-process cells yet" in md
    assert "what is blocking the first batch" not in md
    assert "still shakedown, none frozen yet" in md
    assert "is the live frontier producing?" not in md


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
    assert body.startswith("<!-- weekly-digest: ")
    assert "# Weekly performance digest" in body
    assert "3 petition(s) distributed for **2026-09-29**" in body


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


def test_substance_labels_the_frozen_scope_and_the_honest_empty_state() -> None:
    """The frozen headline shows the prediction census (version-blind) with zero
    scored cells and says why — not a broken funnel, the shakedown state."""
    digest = ops.summarize_substance(
        cell_counts=(410, 137, 5),  # many predictions committed...
        stratified_evaluations=[],  # ...but none from a frozen process yet
        process_scope="frozen",
    )
    assert digest.process_scope == "frozen"
    md = ops.render_substance(digest)
    # The census still shows the predictions (never version-filtered).
    assert "**410**" in md and "**137**" in md
    # And the scored line names the scope + the honest empty note.
    assert "frozen process only" in md
    assert "No frozen-process evaluations yet" in md


def test_substance_all_versions_scope_has_no_frozen_note() -> None:
    digest = ops.summarize_substance(
        cell_counts=(410, 137, 5),
        stratified_evaluations=[
            (_evaluation("claude-baseline", correct=1, quality=0.9), "retrospective")
        ],
        process_scope="all",
    )
    md = ops.render_substance(digest)
    assert "frozen process only" not in md
    assert "No frozen-process evaluations yet" not in md


def test_leakage_digest_stays_all_versions_while_substance_is_frozen(tmp_path: Path) -> None:
    """Leakage is a diagnostic — shakedown contamination is exactly what it must
    surface — so it must not ride the frozen stream. A shakedown (unstamped) cell
    with a likely-leakage block still counts in the leakage digest even though the
    frozen substance headline is empty."""
    data_root = tmp_path / "data"
    ev = _evaluation("claude-baseline", correct=1)
    ev = ev.model_copy(
        update={
            "case_id": "scotus/1",
            "event_id": "evt-x",
            "leakage": LeakageAssessment(
                mode="forward",
                retrieved_outcome_material=True,
                influenced_prediction="likely",
                notes="read the disposition",
            ),
        }
    )
    event = CasePaths(data_root, "scotus", 1).event("evt-x")
    write_json(event.evaluation(ev.evaluator_id, ev.predictor_id, ev.run_id), ev)
    write_json(
        event.prediction("claude-baseline", "p1"),
        Prediction(
            case_id="scotus/1",
            event_id="evt-x",
            predictor_id="claude-baseline",
            engine=Engine.claude_code,
            run_id="p1",
            created_at=datetime(2026, 6, 20, tzinfo=UTC),
            input_snapshot="corpus",
            granted=1,
            probability=0.7,
            predicted_disposition=Disposition.granted,
            process_version=None,  # shakedown: unstamped
        ),
    )
    write_json(
        event.outcome,
        Outcome.model_validate(
            dict(
                case_id="scotus/1",
                event_id="evt-x",
                resolved_at=date(2026, 6, 23),
                actual_disposition=Disposition.granted,
                actual_granted=1,
                disposition_basis="standard",
            )
        ),
    )

    json_out = tmp_path / "ops.json"
    result = runner.invoke(
        app,
        ["ops-report", "--json", str(json_out), "--generated-at", "2026-06-24T00:00:00+00:00"],
        env=_ops_env(tmp_path),
    )
    assert result.exit_code == 0, result.output
    report = json.loads(json_out.read_text())
    # Frozen substance is empty (the cell is unstamped)...
    assert report["substance"]["process_scope"] == "frozen"
    assert report["substance"]["cells"]["evaluations_forward"] == 0
    # ...but the leakage diagnostic still sees the shakedown contamination.
    assert report["leakage"]["assessed"] >= 1
    assert report["leakage"]["likely"] >= 1


def test_render_substance_names_the_forward_claim_exclusions() -> None:
    # The rendered line appears exactly when the record carries a non-zero
    # count, so an exclusion is legible on the dashboard, not only on the
    # boards.
    quiet = ops.summarize_substance(
        cell_counts=(0, 0, 0),
        stratified_evaluations=[],
        forward_claim=forward_claim_record(0),
    )
    loud = ops.summarize_substance(
        cell_counts=(0, 0, 0),
        stratified_evaluations=[],
        forward_claim=forward_claim_record(2),
    )

    assert "Forward-claim integrity" not in ops.render_substance(quiet)
    assert "Forward-claim integrity: **2** cell(s)" in ops.render_substance(loud)


# --- the daily prediction-reading digest -----------------------------------------


def _seed_digest_cell(  # noqa: PLR0913 - a full cell is this many independent parts
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    *,
    predictor_id: str,
    run_id: str,
    stage: Stage = Stage.cert,
    probability: float = 0.4,
    reasoning: str = "Because the anchor says so.",
    predicted_reasoning: str | None = "The Court will deny.",
    flags: AgentFlags | None = None,
) -> None:
    """Commit one full predict cell — event.yaml, prediction, both documents.

    Richer than ``conftest.seed_prediction``, which writes the record alone: the
    digest's whole subject is the prose beside the number, so its fixtures have
    to carry the documents the prediction names.
    """
    event = CasePaths(data_root, court, docket).event(event_id)
    write_yaml(
        event.event_file,
        PredictableEvent(
            event_id=event_id,
            case_id=f"{court}/{docket}",
            kind=EventKind.petition,
            stage=stage,
            moment=Moment.distribution,
            title=f"Case {docket}",
        ),
    )
    write_json(
        event.prediction(predictor_id, run_id),
        Prediction(
            case_id=f"{court}/{docket}",
            event_id=event_id,
            predictor_id=predictor_id,
            engine="claude-code",
            model="claude-fable-5",
            run_id=run_id,
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            input_snapshot="record/snapshots/2026-01-01.json",
            granted=0,
            probability=probability,
            predicted_disposition=Disposition.denied,
            claims=[ClaimProbability(claim_id="disposition", probability=probability)],
            predicted_reasoning_doc=(
                "predicted_reasoning.md" if predicted_reasoning is not None else None
            ),
        ),
    )
    write_text(event.reasoning(predictor_id, run_id), reasoning)
    if predicted_reasoning is not None:
        write_text(event.predicted_reasoning(predictor_id, run_id), predicted_reasoning)
    if flags is not None:
        write_json(event.prediction_flags(predictor_id, run_id), flags)


def _digest_refs(*specs: tuple[str, str, str]) -> list[PredictedEventRef]:
    """Selection-index rows from ``(case, event, latest run)`` triples, newest first."""
    refs = [
        PredictedEventRef(case_id=case, event_id=event, latest_run_id=run)
        for case, event, run in specs
    ]
    refs.sort(key=lambda ref: (ref.latest_run_id, ref.case_id, ref.event_id), reverse=True)
    return refs


def _digest_body(ref: PredictedEventRef) -> str:
    """A stand-in prior digest body: the marker is all the selector reads."""
    return f"{ops.daily_digest_marker(ref.case_id, ref.event_id)}\n# read me\n"


def test_the_digest_features_the_newest_event_nothing_has_featured() -> None:
    # The point of the habit is to read what just landed, so recency wins over
    # every other ordering the index could offer.
    refs = _digest_refs(
        ("scotus/1", "evt-petition-disposition", "20260101T000000Z"),
        ("scotus/2", "evt-petition-disposition", "20260301T000000Z"),
        ("scotus/3", "evt-petition-disposition", "20260201T000000Z"),
    )

    chosen = ops.select_daily_digest_event(refs, [])

    assert chosen is not None
    assert chosen.case_id == "scotus/2"


def test_two_consecutive_digests_feature_two_different_events() -> None:
    # The whole idempotency contract: yesterday's body is the only state, and
    # reading it back must move the digest on rather than repeat it.
    refs = _digest_refs(
        ("scotus/1", "evt-petition-disposition", "20260101T000000Z"),
        ("scotus/2", "evt-petition-disposition", "20260301T000000Z"),
        ("scotus/3", "evt-petition-disposition", "20260201T000000Z"),
    )

    first = ops.select_daily_digest_event(refs, [])
    assert first is not None
    second = ops.select_daily_digest_event(refs, [_digest_body(first)])

    assert second is not None
    assert (second.case_id, second.event_id) != (first.case_id, first.event_id)
    assert second.case_id == "scotus/3"


def test_the_digest_rotates_rather_than_duplicating_when_nothing_is_new() -> None:
    # Once the ledger stops growing daily every candidate is featured. Repeating
    # the newest reading would make the digest worthless; re-reading the oldest
    # keeps it producing something without inventing a backlog.
    refs = _digest_refs(
        ("scotus/1", "evt-petition-disposition", "20260101T000000Z"),
        ("scotus/2", "evt-petition-disposition", "20260301T000000Z"),
        ("scotus/3", "evt-petition-disposition", "20260201T000000Z"),
    )
    by_case = {ref.case_id: ref for ref in refs}
    # Newest issue first, gh's own order: scotus/1 was featured longest ago.
    prior = [_digest_body(by_case[case]) for case in ("scotus/3", "scotus/2", "scotus/1")]

    chosen = ops.select_daily_digest_event(refs, prior)

    assert chosen is not None
    assert chosen.case_id == "scotus/1"


def test_an_empty_ledger_features_nothing() -> None:
    assert ops.select_daily_digest_event([], []) is None


def test_the_digest_renders_a_header_and_a_section_per_predictor(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    for predictor in ("claude-baseline", "codex-baseline", "gemini-baseline"):
        _seed_digest_cell(
            data_root,
            "scotus",
            9,
            "evt-petition-disposition",
            predictor_id=predictor,
            run_id="20260301T000000Z",
            reasoning=f"{predictor} rationale.",
            predicted_reasoning=f"{predictor} forecast of the Court.",
        )
    event = load_predicted_event(data_root, "scotus/9", "evt-petition-disposition")
    assert event is not None

    body = ops.render_daily_digest(
        event, generated_at="2026-03-02T08:00:00Z", repo="owner/name", ref="main"
    )

    assert body.startswith("<!-- daily-digest-event: scotus/9/evt-petition-disposition -->")
    for predictor in ("claude-baseline", "codex-baseline", "gemini-baseline"):
        assert ops.daily_digest_cell_heading(predictor, "20260301T000000Z") in body
        assert f"{predictor} rationale." in body
        assert f"{predictor} forecast of the Court." in body
    # Header facts a reader needs before the prose means anything.
    assert "kind `petition`, stage `cert`, moment `distribution`" in body
    assert "https://github.com/owner/name/blob/main/" in body


def test_the_digest_labels_the_probability_by_stage_not_by_disposition(tmp_path: Path) -> None:
    # `probability` is P(granted) on cert and interim, P(disturbed) on merits —
    # never P(the predicted disposition). Captioning it with the disposition
    # would render a confident deny as "P(denied) = 0.05", the number inverted
    # by its own caption.
    data_root = tmp_path / "data"
    _seed_digest_cell(
        data_root,
        "scotus",
        1,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
        probability=0.05,
    )
    _seed_digest_cell(
        data_root,
        "scotus",
        2,
        "evt-brief-judgment",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
        stage=Stage.merits,
        probability=0.05,
    )
    cert = load_predicted_event(data_root, "scotus/1", "evt-petition-disposition")
    merits = load_predicted_event(data_root, "scotus/2", "evt-brief-judgment")
    assert cert is not None
    assert merits is not None

    cert_body = ops.render_daily_digest(cert, generated_at="2026-03-02T08:00:00Z")
    merits_body = ops.render_daily_digest(merits, generated_at="2026-03-02T08:00:00Z")

    assert "**P(granted) = 0.05** · predicted disposition `denied`" in cert_body
    assert "**P(disturbed) = 0.05** · predicted disposition `denied`" in merits_body


def test_the_digest_truncates_a_long_document_and_links_the_file(tmp_path: Path) -> None:
    # A cut-off argument must never read as the whole of one, so a truncated
    # document says so and carries the link to the committed text.
    data_root = tmp_path / "data"
    _seed_digest_cell(
        data_root,
        "scotus",
        1,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
        reasoning="x" * 40_000,
    )
    event = load_predicted_event(data_root, "scotus/1", "evt-petition-disposition")
    assert event is not None

    body = ops.render_daily_digest(
        event, generated_at="2026-03-02T08:00:00Z", repo="owner/name", ref="main"
    )

    assert "truncated at 6,000 characters" in body
    assert "the full `reasoning.md` is in" in body
    assert len(body) < 20_000


def test_the_digest_body_is_clamped_under_the_issue_size_limit(tmp_path: Path) -> None:
    # GitHub refuses an over-long body with a 422 rather than truncating it, so a
    # digest of an event that accumulated many predictors must lose its tail
    # rather than lose the whole reading surface.
    data_root = tmp_path / "data"
    for index in range(40):
        _seed_digest_cell(
            data_root,
            "scotus",
            1,
            "evt-petition-disposition",
            predictor_id=f"p{index:02d}-baseline",
            run_id="20260301T000000Z",
            reasoning="y" * 5_000,
            predicted_reasoning="z" * 5_000,
        )
    event = load_predicted_event(data_root, "scotus/1", "evt-petition-disposition")
    assert event is not None

    body = ops.render_daily_digest(event, generated_at="2026-03-02T08:00:00Z")

    assert len(body) <= 60_000
    assert body.endswith("the committed artifacts carry the rest._\n")
    # The marker survives the clamp: it is the first line, so a clamped digest is
    # still recognized as having featured its event.
    assert body.startswith("<!-- daily-digest-event: scotus/1/evt-petition-disposition -->")


def test_daily_digest_cli_writes_a_bounded_body_and_a_title(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    for predictor in ("claude-baseline", "codex-baseline"):
        _seed_digest_cell(
            data_root,
            "scotus",
            7,
            "evt-petition-disposition",
            predictor_id=predictor,
            run_id="20260301T000000Z",
        )
    out = tmp_path / "digest.md"
    title_out = tmp_path / "title.txt"

    result = runner.invoke(
        app,
        [
            "daily-digest",
            "--repo",
            "owner/name",
            "--out",
            str(out),
            "--title-out",
            str(title_out),
            "--generated-at",
            "2026-03-02T08:00:00Z",
        ],
        env=_ops_env(tmp_path),
    )

    assert result.exit_code == 0, result.output
    body = out.read_text()
    assert body.startswith("<!-- daily-digest-event: scotus/7/evt-petition-disposition -->")
    for predictor in ("claude-baseline", "codex-baseline"):
        assert ops.daily_digest_cell_heading(predictor, "20260301T000000Z") in body
    assert len(body) <= 60_000
    assert title_out.read_text().startswith("Daily digest: Case 7 (scotus/7 ")


def test_daily_digest_cli_reads_prior_bodies_and_moves_on(tmp_path: Path) -> None:
    # The workflow-facing contract in file form: yesterday's issue body in,
    # today's different event out — no state store between the two runs.
    data_root = tmp_path / "data"
    for docket, run in ((1, "20260101T000000Z"), (2, "20260301T000000Z")):
        _seed_digest_cell(
            data_root,
            "scotus",
            docket,
            "evt-petition-disposition",
            predictor_id="claude-baseline",
            run_id=run,
        )
    first = tmp_path / "day1.md"
    args = ["daily-digest", "--out", str(first), "--generated-at", "2026-03-02T08:00:00Z"]
    assert runner.invoke(app, args, env=_ops_env(tmp_path)).exit_code == 0
    prior = tmp_path / "prior.json"
    prior.write_text(json.dumps([{"body": first.read_text()}]))
    second = tmp_path / "day2.md"

    result = runner.invoke(
        app,
        [
            "daily-digest",
            "--prior-issues",
            str(prior),
            "--out",
            str(second),
            "--generated-at",
            "2026-03-03T08:00:00Z",
        ],
        env=_ops_env(tmp_path),
    )

    assert result.exit_code == 0, result.output
    assert "scotus/2/evt-petition-disposition" in first.read_text().splitlines()[0]
    assert "scotus/1/evt-petition-disposition" in second.read_text().splitlines()[0]


def test_daily_digest_cli_says_so_when_there_is_nothing_to_feature(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["daily-digest", "--out", str(tmp_path / "digest.md")], env=_ops_env(tmp_path)
    )

    assert result.exit_code == 0, result.output
    assert "nothing to feature" in result.output
    assert not (tmp_path / "digest.md").exists()


def test_daily_digest_over_the_committed_ledger_is_bounded_and_complete() -> None:
    # The acceptance dry-run, against the repo's own `data/`: a real event, one
    # section per committed predictor cell, inside the body limit. Asserted
    # structurally rather than against a fixed case, because which event is
    # newest moves with every data run.
    ledger = Path("data")
    if not (ledger / "cases").exists():  # pragma: no cover - the ledger is committed
        pytest.skip("no committed ledger in this checkout")
    refs = iter_predicted_events(ledger)
    chosen = ops.select_daily_digest_event(refs, [])
    assert chosen is not None
    event = load_predicted_event(ledger, chosen.case_id, chosen.event_id)
    assert event is not None

    body = ops.render_daily_digest(
        event, generated_at="2026-03-02T08:00:00Z", repo="ModelMirrorAI/fedcourtsai"
    )

    assert body.startswith(ops.daily_digest_marker(chosen.case_id, chosen.event_id))
    # Counting `## ` headings would identify nothing: the prose a section
    # carries is agent-written and routinely spells its own headings, so the
    # assertion asks for each cell's own heading instead.
    for cell in event.cells:
        heading = ops.daily_digest_cell_heading(
            cell.prediction.predictor_id, cell.prediction.run_id
        )
        assert heading in body
    assert len(event.cells) >= 1
    assert 1_000 < len(body) <= 60_000


class _FakeDigestGh:
    """A :data:`GhRunner` whose ``issue list --json body`` returns canned bodies.

    Local to the digest tests because what they exercise is the *composition* of
    selection and posting — the seam's own contract is asserted in
    ``tests/test_agent_feedback.py``.
    """

    def __init__(self, *, bodies: list[str], create_url: str = "") -> None:
        self._bodies = bodies
        self._create_url = create_url
        self.calls: list[list[str]] = []

    def __call__(self, argv: Sequence[str]) -> str:
        self.calls.append(list(argv))
        verb = tuple(argv[1:3])
        if verb == ("issue", "list"):
            return json.dumps([{"body": body} for body in self._bodies])
        if verb == ("issue", "create"):
            return self._create_url + "\n"
        return ""  # label create

    def created_issue(self) -> bool:
        return any(tuple(c[1:3]) == ("issue", "create") for c in self.calls)


def _prior_digest(case: str, day: str) -> str:
    """A prior digest body: both markers, then prose."""
    return (
        f"{ops.daily_digest_marker(case, 'evt-petition-disposition')}\n"
        f"{ops.daily_digest_day_marker(day)}\n# read me\n"
    )


def test_the_digest_body_carries_both_markers_in_its_leading_lines(tmp_path: Path) -> None:
    # The two markers answer different questions — which event was featured, and
    # which day this issue is — and both have to be where the readers look.
    data_root = tmp_path / "data"
    _seed_digest_cell(
        data_root,
        "scotus",
        1,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
    )
    event = load_predicted_event(data_root, "scotus/1", "evt-petition-disposition")
    assert event is not None

    body = ops.render_daily_digest(event, generated_at="2026-03-02T08:00:00Z")

    lines = body.splitlines()
    assert lines[0] == ops.daily_digest_marker("scotus/1", "evt-petition-disposition")
    assert lines[1] == ops.daily_digest_day_marker("2026-03-02T08:00:00Z")
    assert ops.daily_digest_day_marker("2026-03-02T08:00:00Z") == (
        "<!-- daily-digest-day: 2026-03-02 -->"
    )


def test_a_marker_quoted_in_agent_prose_cannot_retire_an_event(tmp_path: Path) -> None:
    # The prose a digest inlines is written by agents that read docket text and,
    # on a forward cell, the open web. A whole-body marker test would let one of
    # them quote another event's marker and take that event out of the reading
    # queue for good, silently.
    data_root = tmp_path / "data"
    victim = ops.daily_digest_marker("scotus/2", "evt-petition-disposition")
    _seed_digest_cell(
        data_root,
        "scotus",
        1,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
        reasoning=f"The docket says {victim} which is not a marker.",
    )
    event = load_predicted_event(data_root, "scotus/1", "evt-petition-disposition")
    assert event is not None
    body = ops.render_daily_digest(event, generated_at="2026-03-02T08:00:00Z")
    refs = _digest_refs(
        ("scotus/1", "evt-petition-disposition", "20260301T000000Z"),
        ("scotus/2", "evt-petition-disposition", "20260201T000000Z"),
    )

    chosen = ops.select_daily_digest_event(refs, [body])

    # scotus/2 is still unfeatured, so it is what tomorrow reads.
    assert chosen is not None
    assert chosen.case_id == "scotus/2"
    # And the quoted marker is shown as written rather than acting as one.
    assert "&lt;!-- daily-digest-event: scotus/2/evt-petition-disposition -->" in body


def test_a_rotated_re_read_actually_opens_an_issue() -> None:
    # The two halves composed, because separately they were both right and
    # together they were not: guarded on the event marker the create would find
    # the rotated event's own past issue and post nothing, so the rotation would
    # be dead on the one path it exists for.
    refs = _digest_refs(
        ("scotus/1", "evt-petition-disposition", "20260101T000000Z"),
        ("scotus/2", "evt-petition-disposition", "20260201T000000Z"),
    )
    prior = [_prior_digest("scotus/2", "2026-03-02"), _prior_digest("scotus/1", "2026-03-01")]
    chosen = ops.select_daily_digest_event(refs, prior)
    assert chosen is not None
    assert chosen.case_id == "scotus/1"  # the rotation branch

    gh = _FakeDigestGh(bodies=prior, create_url="https://github.com/o/r/issues/9")
    status = open_issue_once(
        repo="o/r",
        label=ops.DAILY_DIGEST_LABEL,
        label_color="1d76db",
        label_description="d",
        title="Daily digest",
        body="body",
        marker=ops.daily_digest_day_marker("2026-03-03T08:00:00Z"),
        runner=gh,
    )

    assert status == "opened https://github.com/o/r/issues/9"
    assert gh.created_issue()


def test_a_second_run_on_a_day_already_digested_posts_nothing() -> None:
    # The other half of the same guard: the create is idempotent per day, so a
    # re-dispatch of the schedule adds no second issue.
    gh = _FakeDigestGh(bodies=[_prior_digest("scotus/1", "2026-03-03")])

    status = open_issue_once(
        repo="o/r",
        label=ops.DAILY_DIGEST_LABEL,
        label_color="1d76db",
        label_description="d",
        title="Daily digest",
        body="body",
        marker=ops.daily_digest_day_marker("2026-03-03T20:00:00Z"),
        runner=gh,
    )

    assert status.startswith("digest already posted")
    assert not gh.created_issue()


def test_daily_digest_cli_post_opens_one_issue_with_the_day_marker(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The CLI's own wiring: --post reaches the opener with the day marker and the
    # rendered title, and reads the prior bodies through the gh seam.
    data_root = tmp_path / "data"
    _seed_digest_cell(
        data_root,
        "scotus",
        3,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
    )
    seen: dict[str, object] = {}

    def fake_open(**kwargs: object) -> str:
        seen.update(kwargs)
        return "opened https://github.com/o/r/issues/1"

    monkeypatch.setattr(cli, "issue_bodies", lambda *args, **kwargs: [])
    monkeypatch.setattr(cli, "open_issue_once", fake_open)

    result = runner.invoke(
        app,
        [
            "daily-digest",
            "--repo",
            "o/r",
            "--post",
            "--out",
            str(tmp_path / "digest.md"),
            "--generated-at",
            "2026-03-02T08:00:00Z",
        ],
        env=_ops_env(tmp_path),
    )

    assert result.exit_code == 0, result.output
    assert seen["marker"] == "<!-- daily-digest-day: 2026-03-02 -->"
    assert seen["label"] == ops.DAILY_DIGEST_LABEL
    assert str(seen["title"]).startswith("Daily digest: Case 3")
    assert str(seen["body"]).startswith("<!-- daily-digest-event: scotus/3/")


def test_daily_digest_cli_post_needs_a_repo(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    _seed_digest_cell(
        data_root,
        "scotus",
        3,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
    )

    result = runner.invoke(app, ["daily-digest", "--post"], env=_ops_env(tmp_path))

    assert result.exit_code == 2
    assert "--post needs --repo" in result.output


def test_the_digest_reads_a_null_stage_petition_as_cert(tmp_path: Path) -> None:
    # Most committed petition events record no stage at all. Declining to
    # normalize would caption the digest's headline number — the one figure it
    # exists to make readable — as an unnamed binary on the bulk of the ledger.
    data_root = tmp_path / "data"
    event_paths = CasePaths(data_root, "scotus", 5).event("evt-petition-disposition")
    _seed_digest_cell(
        data_root,
        "scotus",
        5,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
        probability=0.12,
    )
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id="evt-petition-disposition",
            case_id="scotus/5",
            kind=EventKind.petition,
            stage=None,
            title="Case 5",
        ),
    )
    event = load_predicted_event(data_root, "scotus/5", "evt-petition-disposition")
    assert event is not None

    body = ops.render_daily_digest(event, generated_at="2026-03-02T08:00:00Z")

    assert "**P(granted) = 0.12**" in body
    assert "no stage recorded" not in body


def test_the_digest_defuses_every_field_it_did_not_write(tmp_path: Path) -> None:
    # The defusing runs once over everything below the marker block, so a field
    # nobody thought of — a claim id, the corpus's own case caption — cannot
    # carry a marker into the body and suppress a later digest.
    data_root = tmp_path / "data"
    forged = ops.daily_digest_day_marker("2026-03-03")
    event_paths = CasePaths(data_root, "scotus", 6).event("evt-petition-disposition")
    _seed_digest_cell(
        data_root,
        "scotus",
        6,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
    )
    write_yaml(
        event_paths.event_file,
        PredictableEvent(
            event_id="evt-petition-disposition",
            case_id="scotus/6",
            kind=EventKind.petition,
            stage=Stage.cert,
            title=f"A case captioned {forged}",
        ),
    )
    event = load_predicted_event(data_root, "scotus/6", "evt-petition-disposition")
    assert event is not None

    body = ops.render_daily_digest(event, generated_at="2026-03-02T08:00:00Z")

    assert forged not in body
    assert forged.replace("<!--", "&lt;!--") in body
    assert forged not in ops.daily_digest_title(event)


def test_a_marker_below_the_block_does_not_block_the_next_create() -> None:
    # The create guard reads the same leading block the selection does, so even
    # an un-defused marker deeper in a body cannot suppress tomorrow's digest.
    body = _prior_digest("scotus/1", "2026-03-02")
    body += f"\nThe filing quotes {ops.daily_digest_day_marker('2026-03-03')} verbatim.\n"
    gh = _FakeDigestGh(bodies=[body], create_url="https://github.com/o/r/issues/4")

    status = open_issue_once(
        repo="o/r",
        label=ops.DAILY_DIGEST_LABEL,
        label_color="1d76db",
        label_description="d",
        title="t",
        body="b",
        marker=ops.daily_digest_day_marker("2026-03-03T08:00:00Z"),
        marker_lines=ops.DAILY_DIGEST_MARKER_LINES,
        runner=gh,
    )

    assert status == "opened https://github.com/o/r/issues/4"
    assert gh.created_issue()


def test_daily_digest_cli_writes_no_body_when_the_day_is_already_digested(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Selection runs before the day guard, so a second run of an already-digested
    # day renders the *next* event. Writing that body would put an unpublished
    # digest into the caller's step summary as if it had been featured.
    data_root = tmp_path / "data"
    _seed_digest_cell(
        data_root,
        "scotus",
        8,
        "evt-petition-disposition",
        predictor_id="claude-baseline",
        run_id="20260301T000000Z",
    )
    monkeypatch.setattr(cli, "issue_bodies", lambda *args, **kwargs: [])
    monkeypatch.setattr(cli, "open_issue_once", lambda **kwargs: "digest already posted under `x`")
    out = tmp_path / "digest.md"

    result = runner.invoke(
        app,
        ["daily-digest", "--repo", "o/r", "--post", "--out", str(out)],
        env=_ops_env(tmp_path),
    )

    assert result.exit_code == 0, result.output
    assert not out.exists()


def test_daily_digest_cli_refuses_an_unreadable_prior_issues_file(tmp_path: Path) -> None:
    # Falling back to "nothing featured" would silently re-feature the newest
    # event, which is the one failure the stateless design cannot notice.
    bad = tmp_path / "prior.json"
    bad.write_text("{not json")

    result = runner.invoke(
        app, ["daily-digest", "--prior-issues", str(bad)], env=_ops_env(tmp_path)
    )

    assert result.exit_code == 2
    # Under FORCE_COLOR the usage error renders in a wrapped rich panel, so the
    # flag name can be split across styled lines: strip the escapes and the
    # panel frame, collapse whitespace, then look for it.
    plain = re.sub(r"\x1b\[[0-9;]*m|[│╭╰─╮╯]|\s+", "", result.output)
    assert "--prior-issues" in plain


# --- the weekly performance digest's three substantive sections -------------------


def _empty_report(generated_at: str = "2026-09-02T08:30:00+00:00") -> OpsReport:
    return ops.build_ops_report(generated_at=generated_at, runs=[], usage=[])


def _analytics(
    *,
    leaderboard: Leaderboard | None = None,
    claim_scores: ClaimScoreBoard | None = None,
    statpack: StatPack | None = None,
    backtest: Backtest | None = None,
    salience_replay: SalienceReplay | None = None,
    cert_backtest: CertBacktest | None = None,
    vintage: str | None = "2026-08-29",
    in_force: str = "sal-v4",
) -> ops.WeeklyAnalytics:
    """A `WeeklyAnalytics` whose every artifact carries the same stated vintage."""
    return ops.WeeklyAnalytics(
        leaderboard=ops.Vintaged(leaderboard, vintage),
        claim_scores=ops.Vintaged(claim_scores, vintage),
        statpack=ops.Vintaged(statpack, vintage),
        backtest=ops.Vintaged(backtest, vintage),
        salience_replay=ops.Vintaged(salience_replay, vintage),
        cert_backtest=ops.Vintaged(cert_backtest, vintage),
        salience_version_in_force=in_force,
    )


def _production(
    rows: list[CellCensusRow] | None = None,
    *,
    cells: int = 29,
    events: int = 10,
    spend: float = 60.69,
    backstop: SpendVerdict | None = None,
) -> ops.WeeklyProduction:
    return ops.WeeklyProduction(
        census=RecentCells(
            rows=rows if rows is not None else [CellCensusRow("predictor", "cert", 29)],
            cells=cells,
            events=events,
            window_days=7,
        ),
        spend_usd=spend,
        backstop=backstop,
    )


def test_the_weekly_digest_explains_an_empty_leaderboard_rather_than_showing_a_zero() -> None:
    # An empty frozen board is the registered shakedown state, not a regression.
    # A bare "0 predictors ranked" reads as the latter, which is exactly the
    # misreading metrics/README.md warns about.
    board = Leaderboard(
        process_scope="frozen",
        predictors_ranked=0,
        evaluations_total=0,
        events_scored=0,
        frozen_process=FrozenProcessRecord(
            since=datetime(2026, 8, 1, tzinfo=UTC), digests=["sha256:abc"]
        ),
    )

    md = ops.render_weekly_digest(_empty_report(), analytics=_analytics(leaderboard=board))

    assert "**no predictor ranked**" in md
    assert "no stamped grading has reached the ranked population" in md
    assert "the frozen counting window opened 2026-08-01" in md
    assert "`--all-versions` is where the shakedown pool shows" in md
    assert "`metrics/leaderboard.json`, vintage 2026-08-29" in md


def test_the_weekly_digest_distinguishes_an_absent_board_from_an_empty_one() -> None:
    # "Never landed" and "landed and empty" are different facts about the
    # pipeline, and only one of them is a reason to look at the refresh.
    md = ops.render_weekly_digest(_empty_report(), analytics=_analytics())

    assert "**Leaderboard**: `metrics/leaderboard.json` has never landed." in md
    assert "**no predictor ranked**" not in md
    # An artifact that never landed carries no vintage: there is no commit to
    # date, and printing "vintage unknown" beside it would suggest there is.
    assert "leaderboard.json`, vintage" not in md


def test_the_weekly_digest_carries_a_vintage_beside_every_metrics_figure() -> None:
    # A board is byte-stable and a statpack moves only when the corpus does, so a
    # figure without its vintage silently claims to be this week's.
    md = ops.render_weekly_digest(
        _empty_report(),
        analytics=_analytics(
            leaderboard=Leaderboard(
                process_scope="frozen", predictors_ranked=0, evaluations_total=0, events_scored=0
            ),
            claim_scores=ClaimScoreBoard(
                process_scope="frozen", evaluations_total=0, cells_with_claims=0
            ),
            statpack=_statpack_with_cert_section(denied=95, granted=5),
            backtest=Backtest(predictors_evaluated=0, events_scored=0),
            salience_replay=SalienceReplay(salience_version="sal-v4", cells_evaluated=0),
        ),
    )

    for artifact in (
        "leaderboard.json",
        "claim-scores.json",
        "statpack.json",
        "backtest.json",
        "salience-replay.json",
    ):
        assert f"`metrics/{artifact}`, vintage 2026-08-29" in md


def test_the_weekly_digest_says_when_a_vintage_is_unknown() -> None:
    # Omitting it would leave the number reading as current; saying "unknown"
    # tells the reader its age is unestablished.
    md = ops.render_weekly_digest(
        _empty_report(),
        analytics=_analytics(
            statpack=_statpack_with_cert_section(denied=95, granted=5), vintage=None
        ),
    )

    assert "`metrics/statpack.json`, vintage unknown" in md


def test_the_weekly_digest_reports_the_missing_cert_backtest_honestly() -> None:
    # `metrics/cert-backtest.json` has never landed and is off the scheduled
    # refresh, so the line has to say so — never a stale number as current, and
    # never a silently absent section either.
    md = ops.render_weekly_digest(_empty_report(), analytics=_analytics())

    assert "**Cert back-test**: **no report has landed yet.**" in md
    assert "there is no number here to be stale" in md


def test_the_weekly_digest_names_the_scorer_a_replay_was_produced_under() -> None:
    # A per-band figure means something only under the function that assigned the
    # band, so a replay from an older scorer is history, not a current reading.
    replay = SalienceReplay(
        salience_version="sal-v1",
        salience_versions=["sal-v1"],
        terms=[2022, 2023],
        policies=["arrival"],
        cells_evaluated=6,
    )

    stale = ops.render_weekly_digest(
        _empty_report(), analytics=_analytics(salience_replay=replay, in_force="sal-v4")
    )
    current = ops.render_weekly_digest(
        _empty_report(), analytics=_analytics(salience_replay=replay, in_force="sal-v1")
    )

    assert "produced under `sal-v1` while **`sal-v4`** is the scorer in force" in stale
    assert "not a current reading of the gate" in stale
    assert "is the scorer in force" not in current


def test_the_weekly_digest_reports_the_backtest_floor_beside_its_accuracy() -> None:
    # Raw accuracy is close to meaningless alone under cert's denial skew: a
    # constant predictor scores its slice's base rate exactly.
    board = Backtest(
        predictors_evaluated=1,
        events_scored=28_409,
        entries=[
            BacktestEntry(
                rank=1,
                predictor_id="prior-vote",
                events_scored=28_409,
                accuracy=0.6382,
                granted_accuracy=0.8897,
                mean_brier_score=0.0985,
                always_denied_accuracy=0.6374,
                lift_over_always_denied=0.0008,
            )
        ],
    )

    md = ops.render_weekly_digest(_empty_report(), analytics=_analytics(backtest=board))

    assert "| prior-vote | _all courts pooled_ | 28,409 | 63.8% | 63.7% | +0.08% | 0.0985 |" in md
    assert "Read a lift only against its own court's floor" in md


def test_the_weekly_digest_counts_the_weeks_cells_by_role_and_stage() -> None:
    rows = [
        CellCensusRow("evaluator", "interim", 2),
        CellCensusRow("predictor", "cert", 6),
        CellCensusRow("predictor", "merits", 3),
    ]

    md = ops.render_weekly_digest(
        _empty_report(), production=_production(rows, cells=11, events=4, spend=12.5)
    )

    assert "## Produced this week (last 7d)" in md
    assert "**11** cell(s) over **4** event(s)" in md
    assert "**$12.50** of measured model spend" in md
    assert "| evaluator | interim | 2 |" in md
    assert "| predictor | merits | 3 |" in md
    # The ledger lag is part of the figure's meaning, not a footnote to omit.
    assert "floor on what was spent" in md


def test_the_weekly_digest_places_the_spend_backstop_window() -> None:
    md = ops.render_weekly_digest(
        _empty_report(),
        production=_production(backstop=SpendVerdict(688.12, 2500.0, 30, 300, enforced=True)),
    )

    assert "**$688.12** of **$2,500.00** over the trailing 30d window" in md
    assert "**28%** consumed" in md
    assert "$1,811.88 left" in md
    assert "clear" in md


def test_the_weekly_digest_invents_no_budget_when_none_is_configured() -> None:
    # An unenforced ceiling has no fraction; printing one would report a budget
    # that does not exist.
    md = ops.render_weekly_digest(
        _empty_report(),
        production=_production(backstop=SpendVerdict(0.0, 0.0, 30, 0, enforced=False)),
    )

    assert "**no ceiling configured**" in md
    assert "consumed" not in md


def test_the_weekly_digest_degrades_to_its_questions_without_the_feeds() -> None:
    md = ops.render_weekly_digest(_empty_report())

    assert "## Health questions" in md
    assert "## Analytics state" not in md
    assert "## Produced this week" not in md
    assert "## Backtest results" not in md


def test_the_weekly_digest_marker_is_one_per_iso_week() -> None:
    # Monday and the following Sunday are the same week and so the same digest;
    # the Monday after is a new one.
    assert ops.weekly_digest_marker("2026-09-02T08:30:00Z") == "<!-- weekly-digest: 2026-W36 -->"
    assert ops.weekly_digest_marker("2026-09-06T23:00:00Z") == "<!-- weekly-digest: 2026-W36 -->"
    assert ops.weekly_digest_marker("2026-09-07T08:30:00Z") == "<!-- weekly-digest: 2026-W37 -->"
    assert ops.weekly_digest_title("2026-09-02T08:30:00Z") == (
        "Weekly performance digest — 2026-W36"
    )


def test_ops_report_renders_every_weekly_section_over_the_committed_tree(tmp_path: Path) -> None:
    # The acceptance dry-run, against the repo's own `metrics/` and `data/`: all
    # three sections, the honest-empty leaderboard state, the missing
    # cert-backtest line, and a vintage beside every metrics-derived figure.
    if not Path("metrics/leaderboard.json").exists():  # pragma: no cover - it is committed
        pytest.skip("no committed metrics in this checkout")
    out = tmp_path / "digest.md"

    result = runner.invoke(
        app,
        ["ops-report", "--digest-out", str(out), "--generated-at", "2026-09-02T08:30:00+00:00"],
    )

    assert result.exit_code == 0, result.output
    md = out.read_text()
    assert md.startswith("<!-- weekly-digest: 2026-W36 -->")
    for heading in (
        "## Health questions",
        "## Analytics state",
        "## Produced this week",
        "## Backtest results",
    ):
        assert heading in md
    # Structural only. Asserting the *current* contents of `metrics/` — the empty
    # leaderboard, the absent cert back-test — would turn each of those milestones
    # into a red required check on `main` the day it is reached; the honest-empty
    # and missing-report branches are pinned synthetically above instead.
    for artifact in ("leaderboard.json", "claim-scores.json", "statpack.json", "backtest.json"):
        assert f"`metrics/{artifact}`, " in md
    assert len(md) <= 60_000


def test_post_weekly_digest_takes_its_key_and_title_from_the_body(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The body's own marker is both the once-a-week idempotency key and the
    # source of the title, so a re-dispatch adds no second issue and the title
    # can never disagree with what the issue says.
    seen: dict[str, object] = {}

    def fake_open(**kwargs: object) -> str:
        seen.update(kwargs)
        return "opened https://github.com/o/r/issues/2"

    monkeypatch.setattr(cli, "open_issue_once", fake_open)
    body = tmp_path / "digest.md"
    body.write_text("<!-- weekly-digest: 2026-W36 -->\n# Weekly performance digest\n")

    result = runner.invoke(app, ["post-weekly-digest", "--repo", "o/r", "--body-file", str(body)])

    assert result.exit_code == 0, result.output
    assert seen["marker"] == "<!-- weekly-digest: 2026-W36 -->"
    assert seen["label"] == ops.WEEKLY_DIGEST_LABEL
    assert seen["title"] == "Weekly performance digest — 2026-W36"
    assert seen["marker_lines"] == ops.WEEKLY_DIGEST_MARKER_LINES


def test_post_weekly_digest_refuses_a_body_that_is_not_a_digest(tmp_path: Path) -> None:
    # Opening it anyway would title the issue from a guess and key its
    # idempotency on a line that means nothing.
    body = tmp_path / "digest.md"
    body.write_text("# Some other document\n")

    result = runner.invoke(app, ["post-weekly-digest", "--repo", "o/r", "--body-file", str(body)])

    assert result.exit_code == 2
    assert "does not open with a weekly-digest marker" in result.output


def test_post_weekly_digest_posts_nothing_for_an_empty_body(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["post-weekly-digest", "--repo", "o/r", "--body-file", str(tmp_path / "absent.md")]
    )

    assert result.exit_code == 0, result.output
    assert "nothing to post" in result.output


def test_the_weekly_digest_marker_round_trips_to_its_week() -> None:
    marker = ops.weekly_digest_marker("2026-09-02T08:30:00Z")
    assert ops.weekly_digest_week(marker) == "2026-W36"
    assert ops.weekly_digest_title_for_week("2026-W36") == "Weekly performance digest — 2026-W36"
    # Anything that is not a marker reads as one, so a poster can refuse it.
    assert ops.weekly_digest_week("# Weekly performance digest") is None
    assert ops.weekly_digest_week("<!-- daily-digest-day: 2026-09-02 -->") is None


def test_artifact_vintage_refuses_a_shallow_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A depth-1 clone must yield no vintage, not the tip's date.

    In a shallow clone the single fetched commit is grafted parentless, so a
    pathspec'd ``git log`` matches it for every tracked path and answers with the
    tip's date — stamping a months-old board as today's. That is the exact
    misreading the vintage exists to prevent, and worse than no vintage at all,
    so shallowness is checked before the history is read.
    """
    artifact = tmp_path / "leaderboard.json"
    artifact.write_text("{}")
    calls: list[tuple[str, ...]] = []

    def fake_git(*args: str) -> str | None:
        calls.append(args)
        if args[:2] == ("rev-parse", "--is-shallow-repository"):
            return "true"
        return "2026-09-02"

    monkeypatch.setattr(cli, "_git", fake_git)

    assert cli._artifact_vintage(artifact) is None
    # And the history was never read, so no wrong date could leak out.
    assert all(args[0] != "log" for args in calls)


def test_artifact_vintage_reads_the_commit_date_on_a_full_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact = tmp_path / "leaderboard.json"
    artifact.write_text("{}")

    def fake_git(*args: str) -> str | None:
        return "false" if args[0] == "rev-parse" else "2026-08-29"

    monkeypatch.setattr(cli, "_git", fake_git)

    assert cli._artifact_vintage(artifact) == "2026-08-29"


def test_artifact_vintage_of_an_absent_file_is_unknown(tmp_path: Path) -> None:
    assert cli._artifact_vintage(tmp_path / "never-landed.json") is None


def test_the_weekly_digest_says_the_frozen_window_has_not_opened_yet() -> None:
    # An empty board has two causes and only one of them is about production. A
    # freeze instant in the future means the counting window has not opened, so
    # no grading could have reached it however well the pipeline ran; reporting
    # that as "nothing has been graded" is the bare-zero misreading again.
    board = Leaderboard(
        process_scope="frozen",
        predictors_ranked=0,
        evaluations_total=0,
        events_scored=0,
        frozen_process=FrozenProcessRecord(
            since=datetime(2026, 9, 5, tzinfo=UTC), digests=["sha256:abc"]
        ),
    )
    before = ops.render_weekly_digest(
        _empty_report("2026-09-02T08:30:00+00:00"), analytics=_analytics(leaderboard=board)
    )
    after = ops.render_weekly_digest(
        _empty_report("2026-09-12T08:30:00+00:00"), analytics=_analytics(leaderboard=board)
    )

    assert "the frozen counting window opens **2026-09-05**" in before
    assert "empty by construction" in before
    assert "the frozen counting window opened 2026-09-05 and no stamped grading" in after


def test_the_weekly_digest_refuses_to_anchor_a_score_on_a_pooled_base_rate() -> None:
    # docs/salience.md registers the pooled band rate as a fit diagnostic for the
    # ranking constant, not a scoring baseline: quoting one as a forecast anchor
    # would breach the leakage guard registered there.
    md = ops.render_weekly_digest(
        _empty_report(),
        analytics=_analytics(statpack=_statpack_with_cert_section(denied=95, granted=5)),
    )

    assert "Neither figure anchors a scored cell" in md
    assert "strictly-prior-Term risk-set rate" in md
    assert "orientation" in md
    assert "anchors every score" not in md


def test_the_weekly_digest_publishes_the_predicted_courts_row_not_only_the_pooled_one() -> None:
    # A pooled lift can be bought entirely on a docket this pipeline never
    # predicts: the SCOTUS floor is ~82% and the appellate floors near zero, so
    # the pooled row is the one that misleads and it is the one that gets quoted.
    board = Backtest(
        predictors_evaluated=1,
        events_scored=28_409,
        entries=[
            BacktestEntry(
                rank=1,
                predictor_id="prior-vote",
                events_scored=28_409,
                accuracy=0.6382,
                granted_accuracy=0.8897,
                mean_brier_score=0.0985,
                always_denied_accuracy=0.6374,
                lift_over_always_denied=0.0008,
                courts=[
                    BacktestCourtScore(
                        court="scotus",
                        events_scored=21_511,
                        accuracy=0.8219,
                        granted_accuracy=0.9,
                        mean_brier_score=0.1,
                        always_denied_accuracy=0.8219,
                        lift_over_always_denied=0.0,
                    ),
                    BacktestCourtScore(
                        court="ca4",
                        events_scored=5_736,
                        accuracy=0.0154,
                        granted_accuracy=0.9,
                        mean_brier_score=0.1,
                        always_denied_accuracy=0.011,
                        lift_over_always_denied=0.0044,
                    ),
                ],
            )
        ],
    )

    md = ops.render_weekly_digest(_empty_report(), analytics=_analytics(backtest=board))

    assert "| prior-vote | scotus | 21,511 | 82.2% | 82.2% | +0.00% | 0.1000 |" in md
    assert "| prior-vote | _all courts pooled_ | 28,409 |" in md
    assert "Read a lift only against its own court's floor" in md
    assert "iteration instrument" in md


def test_the_weekly_digest_prints_an_uncomputed_backtest_figure_as_unknown() -> None:
    # The floor, the lift and the Brier are all nullable on the schema. Formatting
    # a None raises, which would take the whole ops report down — dashboard
    # included — over a figure that simply was not computed.
    board = Backtest(
        predictors_evaluated=1,
        events_scored=10,
        entries=[
            BacktestEntry(
                rank=1,
                predictor_id="p",
                events_scored=10,
                accuracy=0.5,
                granted_accuracy=0.5,
                mean_brier_score=None,
                always_denied_accuracy=None,
                lift_over_always_denied=None,
            )
        ],
    )

    md = ops.render_weekly_digest(_empty_report(), analytics=_analytics(backtest=board))

    assert "| p | _all courts pooled_ | 10 | 50.0% | — | — | — |" in md


def test_the_weekly_digest_dates_the_window_it_counted() -> None:
    # "last 7d" alone is not recoverable: the Monday tick titles its issue for the
    # week that starts that morning while the census covers the seven days before
    # it, so without bounds the section describes the previous week under this
    # week's heading.
    production = ops.WeeklyProduction(
        census=RecentCells(rows=[], cells=0, events=0, window_days=7),
        spend_usd=0.0,
        backstop=None,
        window_start=date(2026, 8, 26),
        window_end=date(2026, 9, 2),
    )

    md = ops.render_weekly_digest(_empty_report(), production=production)

    assert "## Produced this week (2026-08-26 to 2026-09-02, the 7d before this digest)" in md


def test_the_weekly_digest_body_is_clamped_under_the_issue_size_limit() -> None:
    # Bounded by construction, but the boards it renders grow with the roster, so
    # the clamp is what makes the bound a guarantee — and the marker has to
    # survive it or the week's idempotency key is gone.
    board = Leaderboard(
        process_scope="all",
        predictors_ranked=4_000,
        evaluations_total=4_000,
        events_scored=1,
        entries=[
            LeaderboardEntry(
                predictor_id=f"predictor-{index:05d}",
                rank=index + 1,
                evaluators=1,
                events_scored=1,
            )
            for index in range(4_000)
        ],
    )

    md = ops.render_weekly_digest(_empty_report(), analytics=_analytics(leaderboard=board))

    assert len(md) <= 60_000
    assert md.startswith("<!-- weekly-digest: 2026-W36 -->")
    assert md.endswith("the committed artifacts carry the rest._\n")


def test_the_weekly_digest_defuses_a_marker_quoted_by_the_ledger() -> None:
    # Predictor ids are free-form strings off the ledger; the same one-pass
    # defusing the daily digest applies keeps one from forging a marker.
    board = Leaderboard(
        process_scope="all",
        predictors_ranked=1,
        evaluations_total=1,
        events_scored=1,
        entries=[
            LeaderboardEntry(
                predictor_id="<!-- weekly-digest: 2026-W40 -->",
                rank=1,
                evaluators=1,
                events_scored=1,
            ),
        ],
    )

    md = ops.render_weekly_digest(_empty_report(), analytics=_analytics(leaderboard=board))

    assert "<!-- weekly-digest: 2026-W40 -->" not in md
    assert "&lt;!-- weekly-digest: 2026-W40 -->" in md
    assert md.splitlines()[0] == "<!-- weekly-digest: 2026-W36 -->"


def test_ops_report_refuses_an_unparseable_generated_at(tmp_path: Path) -> None:
    # Two parsers with two failure postures would anchor the census window on the
    # clock while the marker still carried the raw string — one report pairing a
    # clock-anchored week with a marker naming no week.
    result = runner.invoke(
        app,
        ["ops-report", "--digest-out", str(tmp_path / "d.md"), "--generated-at", "last tuesday"],
        env=_ops_env(tmp_path),
    )

    assert result.exit_code == 2
    # Under FORCE_COLOR the usage error renders in a wrapped rich panel, so the
    # flag name can be split across styled lines: strip the escapes and the
    # panel frame, collapse whitespace, then look for it.
    plain = re.sub(r"\x1b\[[0-9;]*m|[│╭╰─╮╯]|\s+", "", result.output)
    assert "--generated-at" in plain


def test_render_substance_names_the_leakage_exclusions() -> None:
    # Its own line, on the same terms as the forward-claim one above, with the
    # assessed denominator beside the count.
    quiet = ops.summarize_substance(
        cell_counts=(0, 0, 0),
        stratified_evaluations=[],
        leakage_exclusion=leakage_record(0, 4),
    )
    loud = ops.summarize_substance(
        cell_counts=(0, 0, 0),
        stratified_evaluations=[],
        leakage_exclusion=leakage_record(3, 9),
    )

    assert "Leakage exclusion" not in ops.render_substance(quiet)
    assert "Leakage exclusion: **3** of 9 assessed cell(s)" in ops.render_substance(loud)


def test_a_headline_emptied_by_leakage_is_not_the_shakedown_state() -> None:
    # The shakedown placeholder must not swallow an exclusion-emptied board:
    # the cells existed and were dropped, which the line above says.
    emptied = ops.summarize_substance(
        cell_counts=(2, 1, 1),
        stratified_evaluations=[],
        leakage_exclusion=leakage_record(2, 2),
    )
    rendered = ops.render_substance(emptied)

    assert "No frozen-process evaluations yet" not in rendered
    assert "Leakage exclusion: **2** of 2 assessed cell(s)" in rendered
