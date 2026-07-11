"""The metrics-refresh review-PR plan (run-analytics's metrics-refresh job)."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.metrics_refresh import REFRESH_BRANCH, render_backtest_pr, render_refresh_pr
from fedcourtsai.schemas import (
    Backtest,
    BacktestEntry,
    BaseRateBucket,
    CertBacktest,
    CertBacktestEntry,
    Leaderboard,
    LeaderboardEntry,
    LeaderboardStratum,
    StatPack,
)
from fedcourtsai.serialize import write_json, write_text

runner = CliRunner()


def _metrics_dir(tmp_path: Path) -> Path:
    """A metrics directory holding all four regenerated artifacts."""
    metrics = tmp_path / "metrics"
    write_json(
        metrics / "leaderboard.json",
        Leaderboard(
            predictors_ranked=2,
            evaluations_total=12,
            forward_evaluations=4,
            retrospective_evaluations=8,
            entries=[
                LeaderboardEntry(
                    predictor_id="claude-baseline",
                    rank=1,
                    evaluators=2,
                    forward=LeaderboardStratum(events_scored=2, evaluations=2, accuracy=0.8),
                    retrospective=LeaderboardStratum(events_scored=4, evaluations=4, accuracy=0.9),
                ),
                LeaderboardEntry(
                    predictor_id="codex-baseline",
                    rank=2,
                    evaluators=2,
                    forward=LeaderboardStratum(events_scored=2, evaluations=2, accuracy=0.7),
                    retrospective=LeaderboardStratum(events_scored=4, evaluations=4, accuracy=0.8),
                ),
            ],
        ),
    )
    write_json(
        metrics / "backtest.json",
        Backtest(
            predictors_evaluated=2,
            events_scored=1500,
            entries=[
                BacktestEntry(
                    predictor_id="constant-denied",
                    rank=1,
                    events_scored=1500,
                    accuracy=0.9,
                    granted_accuracy=0.9,
                )
            ],
        ),
    )
    write_json(
        metrics / "statpack.json",
        StatPack(
            corpus_rows=80998,
            resolved=60000,
            open=20998,
            overall=BaseRateBucket(cases=80998, resolved=60000, open=20998),
        ),
    )
    write_text(metrics / "statpack.md", "# Statpack\n")
    return metrics


def test_no_changes_means_no_pr(tmp_path: Path) -> None:
    assert render_refresh_pr([], _metrics_dir(tmp_path), "RID") is None


def test_pr_names_the_artifacts_and_reads_headlines(tmp_path: Path) -> None:
    metrics = _metrics_dir(tmp_path)
    changed = [
        "metrics/statpack.md",
        "metrics/leaderboard.json",
        "metrics/statpack.json",
        "metrics/backtest.json",
    ]
    pr = render_refresh_pr(changed, metrics, "RID")
    assert pr is not None
    # Fixed branch: the next refresh force-pushes it, so an unmerged PR updates in
    # place instead of stacking one PR per schedule tick.
    assert pr.branch == REFRESH_BRANCH
    # statpack.json/.md collapse to one name in the title, in display order.
    assert pr.title == "metrics: refresh leaderboard, backtest, statpack"
    assert pr.commit_message == pr.title
    # Headlines come from the regenerated artifacts themselves.
    assert "2 predictor(s) ranked from 12 evaluation(s) (4 forward / 8 retrospective)" in pr.body
    assert "2 predictor(s) over 1500 resolved event(s) (retrospective by construction)" in pr.body
    assert "80998 corpus case(s): 60000 resolved / 20998 open" in pr.body
    assert "RID" in pr.body


def test_partial_refresh_lists_only_the_changed_artifacts(tmp_path: Path) -> None:
    metrics = _metrics_dir(tmp_path)
    pr = render_refresh_pr(["metrics/leaderboard.json"], metrics, "RID")
    assert pr is not None
    assert pr.title == "metrics: refresh leaderboard"
    assert "backtest" not in pr.body
    assert "statpack" not in pr.body


def test_unrecognized_paths_alone_yield_no_pr(tmp_path: Path) -> None:
    # Only the known artifacts drive a refresh PR; a stray path is not a refresh.
    assert render_refresh_pr(["metrics/other.json"], _metrics_dir(tmp_path), "RID") is None


def test_cli_plan_round_trips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    metrics = _metrics_dir(tmp_path)
    monkeypatch.setenv("FEDCOURTS_METRICS_ROOT", str(metrics))
    changed_file = tmp_path / "changed.txt"
    changed_file.write_text("metrics/leaderboard.json\nmetrics/statpack.json\n")
    result = runner.invoke(
        app,
        ["metrics-refresh-plan", "--changed-file", str(changed_file), "--run-id", "RID"],
    )
    assert result.exit_code == 0, result.output
    plan = json.loads(result.output)
    assert plan["changed"] == ["metrics/leaderboard.json", "metrics/statpack.json"]
    assert plan["pr"]["branch"] == REFRESH_BRANCH
    assert plan["pr"]["title"] == "metrics: refresh leaderboard, statpack"


def test_cli_plan_is_null_when_nothing_changed(tmp_path: Path) -> None:
    changed_file = tmp_path / "changed.txt"
    changed_file.write_text("")
    result = runner.invoke(
        app, ["metrics-refresh-plan", "--changed-file", str(changed_file), "--run-id", "RID"]
    )
    assert result.exit_code == 0, result.output
    plan = json.loads(result.output)
    assert plan == {"changed": [], "pr": None}


def test_render_backtest_pr_reads_the_report_headline(tmp_path: Path) -> None:
    report = CertBacktest(
        events_scored=25,
        predictors_evaluated=3,
        always_denied_accuracy=0.92,
        entries=[
            CertBacktestEntry(
                predictor_id="claude-baseline",
                rank=1,
                events_scored=25,
                accuracy=0.96,
                granted_accuracy=0.96,
                mean_brier_score=0.05,
                lift_over_always_denied=0.04,
            )
        ],
    )
    (tmp_path / "cert-backtest.json").write_text(report.model_dump_json())
    pr = render_backtest_pr(tmp_path, "RID", limit=25, engine="auto")
    assert pr is not None
    assert pr.branch == "metrics/cert-backtest"
    assert "cert back-test over 25 petition(s)" in pr.title
    assert "`claude-baseline`" in pr.body and "+4.0%" in pr.body
    assert "always-deny floor: **92%**" in pr.body
    assert "--limit 25 --engine auto" in pr.body
    assert "not** auto-merged" in pr.body


def test_render_backtest_pr_none_without_a_report(tmp_path: Path) -> None:
    assert render_backtest_pr(tmp_path, "RID", limit=25, engine="stub") is None


def test_render_backtest_pr_empty_set_still_renders(tmp_path: Path) -> None:
    empty = CertBacktest(events_scored=0, predictors_evaluated=0)
    (tmp_path / "cert-backtest.json").write_text(empty.model_dump_json())
    pr = render_backtest_pr(tmp_path, "RID", limit=25, engine="stub")
    assert pr is not None and "no predictors scored" in pr.body
