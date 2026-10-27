import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import site_status
from fedcourtsai.cli import app
from fedcourtsai.ops import Vintaged
from fedcourtsai.schemas import (
    CertBacktest,
    CertBacktestEntry,
    LiveFrontier,
    PublicStatus,
    StatusLane,
)

runner = CliRunner()

WORKFLOWS = Path(".github/workflows")

_LANE = site_status.Lane("run-evaluate", "Evaluate", "Grades the forecasts.")
_DAILY = ["39 15 * * *"]
# 08:00 on Tuesday 27 October 2026: the run-ops tick the snapshot is taken on.
_AT = datetime(2026, 10, 27, 8, 0, tzinfo=UTC)


def _run(created: str, conclusion: str | None = "success", **extra: object) -> dict[str, object]:
    status = "completed" if conclusion is not None else "in_progress"
    return {
        "workflowName": "run-evaluate",
        "status": status,
        "conclusion": conclusion,
        "createdAt": created,
        "headBranch": "main",
        **extra,
    }


def _lane(runs: list[dict[str, object]]) -> StatusLane:
    return site_status.lane_status(_LANE, crons=_DAILY, runs=runs, generated_at=_AT)


# --- the cron reading ---------------------------------------------------------------


def test_parse_cron_reads_lists_ranges_steps_and_weekdays() -> None:
    cron = site_status.parse_cron("0,30 */6 * * 1-5")
    assert cron.minutes == frozenset({0, 30})
    assert cron.hours == frozenset({0, 6, 12, 18})
    assert cron.weekdays == frozenset({1, 2, 3, 4, 5})
    # 7 is Sunday as well as 0.
    assert site_status.parse_cron("0 0 * * 7").weekdays == frozenset({0})
    assert site_status.parse_cron("0 0 * * *").weekdays is None


@pytest.mark.parametrize("expression", ["0 0 1 * *", "0 0 * 6 *", "0 24 * * *", "0 0 * *"])
def test_parse_cron_refuses_what_it_does_not_model(expression: str) -> None:
    with pytest.raises(ValueError):
        site_status.parse_cron(expression)


def test_last_tick_is_the_newest_fire_at_or_before_the_instant() -> None:
    crons = [site_status.parse_cron("12 14 * * *"), site_status.parse_cron("32 17 * * *")]
    assert site_status.last_tick(crons, _AT) == datetime(2026, 10, 26, 17, 32, tzinfo=UTC)
    assert site_status.last_tick(crons, datetime(2026, 10, 27, 14, 12, tzinfo=UTC)) == datetime(
        2026, 10, 27, 14, 12, tzinfo=UTC
    )
    # A Monday-only cron, read on a Tuesday, reaches back to Monday.
    weekly = [site_status.parse_cron("30 8 * * 1")]
    assert site_status.last_tick(weekly, _AT) == datetime(2026, 10, 26, 8, 30, tzinfo=UTC)
    assert site_status.last_tick([], _AT) is None


def test_describe_schedule_lists_daily_times_and_groups_weekly_ones() -> None:
    assert site_status.describe_schedule(["39 15 * * *"]) == "daily at 15:39 UTC"
    assert site_status.describe_schedule(["12 14 * * *", "32 17 * * *"]) == (
        "daily at 14:12 and 17:32 UTC"
    )
    assert site_status.describe_schedule(["36 4 * * *", "41 5 * * 1", "59 12 * * 1"]) == (
        "daily at 04:36 UTC, plus Mondays at 05:41 and 12:59 UTC"
    )
    assert site_status.describe_schedule(["47 0,2,4,6,8,10 * * *"]) == "6 times a day"
    assert site_status.describe_schedule([]) == "no schedule"


def test_every_lane_names_a_workflow_that_declares_a_schedule() -> None:
    # A lane whose workflow lost its schedule would never read late, which is the
    # one thing the page exists to show.
    for lane in site_status.LANES:
        crons = site_status.workflow_crons(WORKFLOWS, lane.stem)
        assert crons, lane.stem
        for expression in crons:
            site_status.parse_cron(expression)


# --- the lane judgement -------------------------------------------------------------


def test_a_lane_that_ran_after_its_last_tick_and_succeeded_is_up() -> None:
    lane = _lane([_run("2026-10-26T15:50:00Z")])
    assert lane.state == "up"
    assert lane.expected_since == datetime(2026, 10, 26, 15, 39, tzinfo=UTC)
    assert (lane.runs_7d, lane.successes_7d) == (1, 1)


def test_a_lane_that_has_not_started_since_its_last_tick_is_late() -> None:
    # The run before the 26th's tick succeeded; nothing has started since.
    lane = _lane([_run("2026-10-25T15:45:00Z")])
    assert lane.state == "late"
    assert lane.last_conclusion == "success"


def test_the_grace_period_keeps_a_tick_that_has_only_just_passed_from_reading_late() -> None:
    lane = site_status.lane_status(
        _LANE,
        crons=["30 7 * * *"],
        runs=[_run("2026-10-26T07:35:00Z")],
        generated_at=_AT,
    )
    # 07:30 today is inside the two-hour grace, so yesterday's tick is the one owed.
    assert lane.expected_since == datetime(2026, 10, 26, 7, 30, tzinfo=UTC)
    assert lane.state == "up"


def test_a_lane_whose_newest_conclusive_run_failed_is_failing() -> None:
    lane = _lane([_run("2026-10-26T15:50:00Z", "failure"), _run("2026-10-25T15:45:00Z")])
    assert lane.state == "failing"
    assert lane.last_conclusion == "failure"
    assert (lane.runs_7d, lane.successes_7d) == (2, 1)


def test_cancelled_and_skipped_runs_start_a_lane_but_conclude_nothing() -> None:
    # A superseded corpus writer ends cancelled with nothing wrong: the lane
    # started on time, and its last conclusive run is the success before.
    lane = _lane(
        [
            _run("2026-10-26T15:50:00Z", "cancelled"),
            _run("2026-10-26T15:45:00Z", "skipped"),
            _run("2026-10-25T15:45:00Z", "failure"),
            _run("2026-10-24T15:45:00Z"),
        ]
    )
    assert lane.state == "failing"
    assert lane.last_started_at == datetime(2026, 10, 26, 15, 50, tzinfo=UTC)
    assert lane.last_concluded_at == datetime(2026, 10, 25, 15, 45, tzinfo=UTC)


def test_an_in_progress_run_counts_as_started() -> None:
    lane = _lane([_run("2026-10-26T15:50:00Z", None), _run("2026-10-25T15:45:00Z")])
    assert lane.state == "up"
    assert lane.last_started_at == datetime(2026, 10, 26, 15, 50, tzinfo=UTC)


def test_a_staging_rehearsal_is_not_a_production_run() -> None:
    lane = _lane([_run("2026-10-26T16:00:00Z", headBranch="staging"), _run("2026-10-25T15:45:00Z")])
    assert lane.state == "late"


def test_runs_of_other_workflows_and_after_the_snapshot_are_ignored() -> None:
    assert _lane([]).state == "no-runs"
    assert _lane([_run("2026-10-26T15:50:00Z", workflowName="run-predict")]).state == "no-runs"
    assert _lane([_run("2026-10-27T09:00:00Z")]).state == "no-runs"


# --- the back-test headlines ---------------------------------------------------------


def _cert_entry(predictor_id: str, *, granted_lift: float | None) -> CertBacktestEntry:
    return CertBacktestEntry(
        predictor_id=predictor_id,
        rank=1,
        events_scored=10,
        accuracy=0.8,
        granted_accuracy=0.9,
        mean_brier_score=0.05,
        granted_lift_over_always_denied=granted_lift,
        lift_over_always_denied=-0.1,
        engine="claude-code",
    )


def test_the_cert_headline_reads_the_granted_axis_when_the_report_carries_it() -> None:
    report = CertBacktest(
        events_scored=10,
        predictors_evaluated=1,
        salience_version="sal-v4",
        always_denied_accuracy=0.9,
        always_not_granted_accuracy=0.9,
        entries=[_cert_entry("claude-baseline", granted_lift=0.0)],
    )
    built = site_status._cert(Vintaged(value=report, vintage="2026-10-17"))
    assert built is not None
    assert built.vintage == date(2026, 10, 17)
    assert built.table is not None
    assert built.table.columns[3] == "Granted-or-not accuracy"
    assert built.table.rows == [["claude-baseline", "model", "10", "90.0%", "+0.00%", "0.0500"]]
    assert "iteration instrument" in built.reading


def test_an_older_cert_report_is_read_on_exact_disposition_rather_than_shown_blank() -> None:
    report = CertBacktest(
        events_scored=10,
        predictors_evaluated=1,
        salience_version="sal-v4",
        always_denied_accuracy=0.9,
        entries=[_cert_entry("claude-baseline", granted_lift=None)],
    )
    built = site_status._cert(Vintaged(value=report, vintage=None))
    assert built is not None
    assert built.table is not None
    assert built.table.columns[3] == "Exact-disposition accuracy"
    assert built.table.rows[0][3:5] == ["80.0%", "-10.00%"]
    assert "exact disposition" in built.summary


def test_a_backtest_that_never_landed_is_left_out() -> None:
    assert site_status._cert(Vintaged(value=None, vintage=None)) is None


# --- the command --------------------------------------------------------------------


def test_ops_report_writes_a_status_snapshot_without_spend(tmp_path: Path) -> None:
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    for lane in site_status.LANES:
        (workflows / f"{lane.stem}.yml").write_text(
            f"name: {lane.stem}\non:\n  schedule:\n    - cron: '0 6 * * *'\n"
        )
    frontier = tmp_path / "live-frontier.json"
    frontier.write_text(
        LiveFrontier(
            generated_on=date(2026, 10, 27),
            watchlist=479,
            documents_provisioned=134,
            next_conference=date(2026, 11, 6),
            next_conference_petitions=270,
        ).model_dump_json()
    )
    runs = tmp_path / "runs.json"
    runs.write_text(
        json.dumps(
            [
                {
                    "workflowName": "run-pull",
                    "status": "completed",
                    "conclusion": "success",
                    "createdAt": "2026-10-27T06:05:00Z",
                    "headBranch": "main",
                }
            ]
        )
    )
    config_root = tmp_path / "config"
    config_root.mkdir()
    out = tmp_path / "status.json"

    result = runner.invoke(
        app,
        [
            "ops-report",
            "--runs",
            str(runs),
            "--live-frontier",
            str(frontier),
            "--status-out",
            str(out),
            "--workflows-root",
            str(workflows),
            "--generated-at",
            "2026-10-27T09:00:00+00:00",
        ],
        env={
            "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
            "FEDCOURTS_CONFIG_ROOT": str(config_root),
            "FEDCOURTS_METRICS_ROOT": str(tmp_path / "metrics"),
        },
    )

    assert result.exit_code == 0, result.output
    status = PublicStatus.model_validate_json(out.read_text())
    states = {lane.lane: lane.state for lane in status.lanes}
    assert states["run-pull"] == "up"
    assert states["run-predict"] == "no-runs"
    assert [p.window for p in status.production] == ["7d", "30d", "term"]
    assert status.production[2].term == 2026
    assert status.production[2].start == date(2026, 10, 1)
    assert status.coverage.watchlist == 479
    assert status.coverage.documents_provisioned == 134
    assert status.backtests == []
    # The page is public: nothing in the snapshot is a dollar figure.
    assert "usd" not in out.read_text().lower()
    assert "spend" not in out.read_text().lower()
