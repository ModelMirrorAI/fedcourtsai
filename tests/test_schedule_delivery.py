import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import schedule_delivery as sd
from fedcourtsai import site_status
from fedcourtsai.cli import app
from fedcourtsai.schemas import OpsReport, PublicStatus
from fedcourtsai.site_status import parse_cron

runner = CliRunner()

NOW = datetime(2026, 11, 6, 13, 0, tzinfo=UTC)


def _at(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


def _run(
    path: str, created: str, *, event: str = "schedule", branch: str = "main"
) -> dict[str, str]:
    return {
        "path": f".github/workflows/{path}.yml",
        "created_at": created,
        "event": event,
        "head_branch": branch,
    }


def test_slots_between_lists_every_fire_in_the_half_open_span() -> None:
    crons = [parse_cron("17 1,7,13,19 * * *"), parse_cron("47 0,2 * * *")]
    slots = sd.slots_between(crons, _at("2026-11-06T00:47"), _at("2026-11-06T07:17"))
    assert slots == [_at("2026-11-06T01:17"), _at("2026-11-06T02:47"), _at("2026-11-06T07:17")]


def test_a_weekly_cron_fires_only_on_its_weekday() -> None:
    # 2026-11-02 is a Monday.
    slots = sd.slots_between(
        [parse_cron("57 12 * * 1")], _at("2026-10-31T00:00"), _at("2026-11-08T00:00")
    )
    assert slots == [_at("2026-11-02T12:57")]


def test_a_run_matches_the_newest_slot_at_or_before_it() -> None:
    slots = [_at("2026-11-06T01:17"), _at("2026-11-06T02:47"), _at("2026-11-06T04:47")]
    runs = [
        _at("2026-11-06T00:30"),  # before every slot: matches none
        _at("2026-11-06T01:40"),
        _at("2026-11-06T02:00"),  # a second run on the same slot keeps the first
        _at("2026-11-06T05:10"),  # 02:47's tick never came: read as dropped
    ]
    assert sd.match_slots(slots, runs) == {
        _at("2026-11-06T01:17"): _at("2026-11-06T01:40"),
        _at("2026-11-06T04:47"): _at("2026-11-06T05:10"),
    }


def test_schedule_runs_keeps_main_schedule_events_by_file_stem() -> None:
    pages = [
        {
            "workflow_runs": [
                _run("run-pull", "2026-11-06T01:20:00Z"),
                _run("run-pull", "2026-11-06T01:30:00Z", event="workflow_dispatch"),
                _run("run-pull", "2026-11-06T01:40:00Z", branch="staging"),
            ]
        },
        [{"workflow_runs": [_run("run-ops", "2026-11-06T08:05:00Z")]}],
    ]
    assert sd.schedule_runs(pages) == {
        "run-pull": [_at("2026-11-06T01:20")],
        "run-ops": [_at("2026-11-06T08:05")],
    }


def test_a_healthy_daily_workflow_is_not_flagged() -> None:
    runs = [_at("2026-11-06T08:04") - timedelta(days=d) for d in range(8)]
    record = sd.workflow_delivery("run-ops", crons=["0 8 * * *"], runs=sorted(runs), now=NOW)
    assert (record.day.slots, record.day.delivered, record.day.lateness_p50_min) == (1, 1, 4)
    assert (record.week.slots, record.week.delivered, record.week.dropped) == (7, 7, 0)
    assert record.flags == []


def test_a_slot_younger_than_the_settle_time_is_not_counted_yet() -> None:
    # 12:00's tick is an hour old at 13:00 and has not come: not dropped yet.
    runs = [_at("2026-11-06T11:01"), _at("2026-11-05T12:03")]
    record = sd.workflow_delivery("hourly", crons=["0 11,12 * * *"], runs=runs, now=NOW)
    assert record.day.slots == 2  # 2026-11-05 12:00 and 2026-11-06 11:00
    assert record.day.delivered == 2
    assert record.flags == []


def test_a_workflow_that_stopped_ticking_is_flagged() -> None:
    runs = [_at("2026-11-04T08:05")]
    record = sd.workflow_delivery("run-ops", crons=["0 8 * * *"], runs=runs, now=NOW)
    assert record.day.delivered == 0
    assert any("no scheduled run since 2026-11-04 08:05Z" in flag for flag in record.flags)
    assert any("0 of 1 slots" in flag for flag in record.flags)


def test_a_weekly_workflow_quiet_for_days_is_not_flagged_while_its_tick_came() -> None:
    runs = [_at("2026-11-02T13:00")]
    record = sd.workflow_delivery("weekly", crons=["57 12 * * 1"], runs=runs, now=NOW)
    assert record.flags == []
    assert record.week.delivered == 1


def test_a_lane_firing_under_half_its_slots_is_flagged() -> None:
    # Hourly at :26; only four of the day's slots delivered.
    runs = [_at(f"2026-11-06T{h:02d}:30") for h in (2, 5, 8, 10)]
    record = sd.workflow_delivery("promotion-prep", crons=["26 * * * *"], runs=runs, now=NOW)
    assert record.day.slots == 24
    assert record.day.delivered == 4
    assert "4 of 24 slots in the last 24 h delivered" in record.flags


def test_the_section_lists_flagged_workflows_first(tmp_path: Path) -> None:
    (tmp_path / "a.yml").write_text("on:\n  schedule:\n    - cron: '0 8 * * *'\n")
    (tmp_path / "b.yml").write_text("on:\n  schedule:\n    - cron: '0 9 * * *'\n")
    (tmp_path / "c.yml").write_text("on:\n  push:\n")
    rows = [{"workflow_runs": [_run("a", "2026-11-06T08:02:00Z")]}]
    delivery = sd.build_schedule_delivery(rows, workflows_root=tmp_path, now=NOW)
    assert [w.workflow for w in delivery.workflows] == ["a", "b"]
    text = sd.render_schedule_delivery(delivery)
    assert "**1 workflow(s) flagged:**" in text
    assert text.index("| b |") < text.index("| a |")


def test_ops_report_carries_delivery_into_the_report_and_the_status_lanes(
    tmp_path: Path,
) -> None:
    workflows = tmp_path / "workflows"
    workflows.mkdir()
    for lane in site_status.LANES:
        (workflows / f"{lane.stem}.yml").write_text(
            f"name: {lane.stem}\non:\n  schedule:\n    - cron: '0 6 * * *'\n"
        )
    scheduled = tmp_path / "schedule-runs.json"
    scheduled.write_text(
        json.dumps([[{"workflow_runs": [_run("run-pull", "2026-11-06T06:20:00Z")]}]])
    )
    config_root = tmp_path / "config"
    config_root.mkdir()
    status_out = tmp_path / "status.json"
    json_out = tmp_path / "ops.json"

    result = runner.invoke(
        app,
        [
            "ops-report",
            "--json",
            str(json_out),
            "--status-out",
            str(status_out),
            "--workflows-root",
            str(workflows),
            "--schedule-runs",
            str(scheduled),
            "--generated-at",
            NOW.isoformat(),
        ],
        env={
            "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
            "FEDCOURTS_CONFIG_ROOT": str(config_root),
            "FEDCOURTS_METRICS_ROOT": str(tmp_path / "metrics"),
        },
    )

    assert result.exit_code == 0, result.output
    assert "## Schedule delivery" in result.output
    report = OpsReport.model_validate_json(json_out.read_text())
    assert report.schedule_delivery is not None
    lanes = {
        lane.lane: lane for lane in PublicStatus.model_validate_json(status_out.read_text()).lanes
    }
    assert (lanes["run-pull"].slots_24h, lanes["run-pull"].delivered_24h) == (1, 1)
    assert lanes["run-pull"].lateness_p50_min == 20
    assert lanes["run-predict"].delivered_24h == 0


def test_an_unreadable_schedule_feed_drops_only_its_section(tmp_path: Path) -> None:
    scheduled = tmp_path / "schedule-runs.json"
    scheduled.write_text("{not json")
    config_root = tmp_path / "config"
    config_root.mkdir()
    json_out = tmp_path / "ops.json"
    result = runner.invoke(
        app,
        ["ops-report", "--json", str(json_out), "--schedule-runs", str(scheduled)],
        env={
            "FEDCOURTS_DATA_ROOT": str(tmp_path / "data"),
            "FEDCOURTS_CONFIG_ROOT": str(config_root),
            "FEDCOURTS_METRICS_ROOT": str(tmp_path / "metrics"),
        },
    )
    assert result.exit_code == 0, result.output
    assert "## Schedule delivery" not in result.output
    assert OpsReport.model_validate_json(json_out.read_text()).schedule_delivery is None
