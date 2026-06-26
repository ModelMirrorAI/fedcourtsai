from datetime import datetime

from fedcourtsai import ops
from fedcourtsai.schemas import (
    CourtProgress,
    Engine,
    ModelUsage,
    OpsReport,
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
