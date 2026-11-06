import json
from datetime import UTC, datetime
from pathlib import Path

import yaml
from typer.testing import CliRunner

from fedcourtsai import catch_up as cu
from fedcourtsai.cli import app

runner = CliRunner()

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"


def _at(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


def _run(
    run_id: int,
    workflow: str,
    created: str,
    *,
    title: str | None = None,
    status: str = "completed",
    conclusion: str | None = "success",
    branch: str = "main",
) -> dict[str, object]:
    return {
        "id": run_id,
        "path": f".github/workflows/{workflow}.yml",
        "display_title": title if title is not None else workflow,
        "created_at": created,
        "status": status,
        "conclusion": conclusion,
        "head_branch": branch,
    }


def _pages(*runs: dict[str, object]) -> list[object]:
    return [[{"workflow_runs": list(runs)}]]


# Served predict slots, so the pull cases read the pull lane alone.
PREDICT_OK = _run(900, "run-predict", "2026-11-06T14:15:00Z")


def test_an_unserved_pull_slot_is_made_up() -> None:
    rows = _pages(
        _run(1, "run-pull", "2026-11-06T12:50:00Z", title="run-pull live"),
        _run(2, "run-pull", "2026-11-06T14:50:00Z", title="run-pull live", status="in_progress"),
        PREDICT_OK,
    )
    answer = cu.catch_up(rows, workflows_root=WORKFLOWS, now=_at("2026-11-06T15:10"), run_id=2)
    assert answer.pull.action == "dispatch"
    assert answer.pull.slot == _at("2026-11-06T13:17")
    assert answer.predict.action == "none"


def test_a_pull_slot_within_its_grace_is_left_to_its_tick() -> None:
    # 13:50 is 33 minutes after 13:17, so the newest slot due is still 07:17,
    # which a pull window served.
    rows = _pages(
        _run(0, "run-pull", "2026-11-06T07:30:00Z", title="run-pull pull"),
        _run(1, "run-pull", "2026-11-06T12:50:00Z", title="run-pull live"),
        PREDICT_OK,
    )
    answer = cu.catch_up(rows, workflows_root=WORKFLOWS, now=_at("2026-11-06T13:50"), run_id=1)
    assert answer.pull.action == "none"
    assert answer.pull.slot == _at("2026-11-06T07:17")


def test_a_pull_run_since_the_slot_serves_it_whatever_started_it() -> None:
    for title in ("run-pull pull", "run-pull"):  # a plain title predates run-name
        rows = _pages(_run(1, "run-pull", "2026-11-06T13:40:00Z", title=title), PREDICT_OK)
        answer = cu.catch_up(rows, workflows_root=WORKFLOWS, now=_at("2026-11-06T15:00"), run_id=9)
        assert answer.pull.action == "none", title
        assert "served by run 1" in answer.pull.reason


def test_a_cancelled_or_live_run_does_not_serve_a_pull_slot() -> None:
    rows = _pages(
        _run(1, "run-pull", "2026-11-06T13:20:00Z", title="run-pull pull", conclusion="cancelled"),
        _run(2, "run-pull", "2026-11-06T14:50:00Z", title="run-pull live"),
        _run(3, "run-pull", "2026-11-06T14:00:00Z", title="run-pull pull", branch="staging"),
        PREDICT_OK,
    )
    answer = cu.catch_up(rows, workflows_root=WORKFLOWS, now=_at("2026-11-06T15:10"), run_id=2)
    assert answer.pull.action == "dispatch"


def test_a_waiting_corpus_writer_holds_the_make_up() -> None:
    rows = _pages(
        _run(2, "run-pull", "2026-11-06T14:50:00Z", title="run-pull live", status="in_progress"),
        _run(3, "run-seed", "2026-11-06T14:40:00Z", status="pending", conclusion=None),
        PREDICT_OK,
    )
    answer = cu.catch_up(rows, workflows_root=WORKFLOWS, now=_at("2026-11-06T15:10"), run_id=2)
    assert answer.pull.action == "none"
    assert "run 3 (run-seed) waits for the corpus lock" in answer.pull.reason


def test_an_unserved_predict_slot_is_made_up_and_any_predict_run_serves_it() -> None:
    lone = _pages(_run(2, "run-pull", "2026-11-06T15:00:00Z", title="run-pull pull"))
    answer = cu.catch_up(lone, workflows_root=WORKFLOWS, now=_at("2026-11-06T15:20"), run_id=2)
    assert answer.predict.action == "dispatch"
    assert answer.predict.slot == _at("2026-11-06T14:12")
    dispatched = _pages(
        _run(2, "run-pull", "2026-11-06T15:00:00Z", title="run-pull pull"),
        _run(5, "run-predict", "2026-11-06T14:30:00Z", status="queued", conclusion=None),
    )
    answer = cu.catch_up(
        dispatched, workflows_root=WORKFLOWS, now=_at("2026-11-06T15:20"), run_id=2
    )
    assert answer.predict.action == "none"


def test_a_late_tick_skips_the_pull_a_made_up_window_already_ran() -> None:
    rows = _pages(
        _run(7, "run-pull", "2026-11-06T14:00:00Z", title="run-pull pull"),
        _run(8, "run-pull", "2026-11-06T14:30:00Z", title="run-pull pull", status="in_progress"),
    )
    verdict = cu.slot_served(
        rows, schedule="17 1,7,13,19 * * *", run_id=8, created_at=_at("2026-11-06T14:30")
    )
    assert verdict.served
    assert "run 7 already served" in verdict.reason


def test_a_tick_with_no_earlier_window_runs_its_pull() -> None:
    rows = _pages(
        _run(6, "run-pull", "2026-11-06T12:00:00Z", title="run-pull pull"),  # the slot before
        _run(7, "run-pull", "2026-11-06T13:30:00Z", title="run-pull live"),
        _run(8, "run-pull", "2026-11-06T13:40:00Z", title="run-pull pull"),
    )
    verdict = cu.slot_served(
        rows, schedule="17 1,7,13,19 * * *", run_id=8, created_at=_at("2026-11-06T13:40")
    )
    assert not verdict.served


def test_the_commands_print_their_answers(tmp_path: Path) -> None:
    runs = tmp_path / "runs.json"
    runs.write_text(
        json.dumps(_pages(_run(2, "run-pull", "2026-11-06T14:50:00Z", title="run-pull live")))
    )
    result = runner.invoke(
        app,
        [
            "catch-up",
            "--runs-file",
            str(runs),
            "--run-id",
            "2",
            "--now",
            "2026-11-06T15:20:00+00:00",
            "--workflows-root",
            str(WORKFLOWS),
        ],
    )
    assert result.exit_code == 0, result.output
    answer = json.loads(result.output)
    assert answer["pull"]["action"] == "dispatch"
    assert answer["predict"]["action"] == "dispatch"
    result = runner.invoke(
        app,
        [
            "slot-served",
            "--runs-file",
            str(runs),
            "--schedule",
            "17 1,7,13,19 * * *",
            "--run-id",
            "3",
            "--created-at",
            "2026-11-06T15:00:00Z",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["served"] is False


def test_an_unreadable_runs_file_is_refused(tmp_path: Path) -> None:
    runs = tmp_path / "runs.json"
    runs.write_text("{not json")
    result = runner.invoke(app, ["catch-up", "--runs-file", str(runs), "--run-id", "1"])
    assert result.exit_code != 0


def test_run_pull_titles_each_run_with_its_mode() -> None:
    workflow = yaml.safe_load((WORKFLOWS / "run-pull.yml").read_text())
    title = workflow["run-name"]
    assert "format('run-pull {0}'" in title
    assert f"startsWith(github.event.schedule, '{cu.PULL_CRON_PREFIX}')" in title
    assert cu.pull_crons(WORKFLOWS) == ["17 1,7,13,19 * * *"]
