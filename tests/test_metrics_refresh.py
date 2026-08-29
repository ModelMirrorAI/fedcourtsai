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
    ClaimJudgeAgreement,
    ClaimScoreBoard,
    DocketPack,
    DocketPackTerm,
    GroupBy,
    Leaderboard,
    LeaderboardEntry,
    LeaderboardStage,
    LeaderboardStageEntry,
    LeaderboardStratum,
    ScopeManifest,
    StatPack,
    StatPackCoverage,
    StatPackSection,
)
from fedcourtsai.serialize import read_model, write_json, write_text

runner = CliRunner()


def _metrics_dir(tmp_path: Path) -> Path:
    """A metrics directory holding every regenerated artifact.

    Returns the metrics directory itself; `render_refresh_pr` takes the repo root
    (its parent), because the refresh now also carries `data/scope/scope.json`.
    """
    metrics = tmp_path / "metrics"
    write_json(
        metrics / "leaderboard.json",
        Leaderboard(
            predictors_ranked=2,
            evaluations_total=12,
            events_scored=6,
            forward_evaluations=4,
            retrospective_evaluations=8,
            entries=[
                LeaderboardEntry(
                    predictor_id="claude-baseline",
                    rank=1,
                    evaluators=2,
                    events_scored=6,
                    forward=LeaderboardStratum(events_scored=2, evaluations=2, accuracy=0.8),
                    retrospective=LeaderboardStratum(events_scored=4, evaluations=4, accuracy=0.9),
                ),
                LeaderboardEntry(
                    predictor_id="codex-baseline",
                    rank=2,
                    evaluators=2,
                    events_scored=6,
                    forward=LeaderboardStratum(events_scored=2, evaluations=2, accuracy=0.7),
                    retrospective=LeaderboardStratum(events_scored=4, evaluations=4, accuracy=0.8),
                ),
            ],
        ),
    )
    write_json(
        metrics / "claim-scores.json",
        ClaimScoreBoard(
            evaluations_total=9,
            cells_with_claims=0,
            forward_agreement=ClaimJudgeAgreement(
                pairs=0,
                pair_events=0,
                suppressed=True,
                missing_claim_block=9,
                masked_claim_total=0,
                missing_reasoning_quality=0,
            ),
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
                    always_denied_accuracy=0.9,
                    lift_over_always_denied=0.0,
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
    write_json(
        metrics / "docket.json",
        DocketPack(
            corpus_rows=80998,
            resolved=60000,
            open=20998,
            coverage=StatPackCoverage(live_slice_rows=9924, live_slice_resolved=9327),
            sections=[StatPackSection(title="Cases by court", group_by=GroupBy.court)],
            terms=[DocketPackTerm(term=2025), DocketPackTerm(term=2024)],
        ),
    )
    write_text(metrics / "docket.md", "# Docket pack\n")
    return metrics


def test_no_changes_means_no_pr(tmp_path: Path) -> None:
    assert render_refresh_pr([], _metrics_dir(tmp_path).parent, "RID") is None


def test_pr_names_the_artifacts_and_reads_headlines(tmp_path: Path) -> None:
    metrics = _metrics_dir(tmp_path)
    changed = [
        "metrics/statpack.md",
        "metrics/leaderboard.json",
        "metrics/statpack.json",
        "metrics/backtest.json",
    ]
    pr = render_refresh_pr(changed, metrics.parent, "RID")
    assert pr is not None
    # Fixed branch: the next refresh force-pushes it, so an unmerged PR updates in
    # place instead of stacking one PR per schedule tick.
    assert pr.branch == REFRESH_BRANCH
    # statpack.json/.md collapse to one name in the title, in display order.
    assert pr.title == "metrics: refresh leaderboard, backtest, statpack"
    assert pr.commit_message == pr.title
    # Headlines come from the regenerated artifacts themselves.
    assert (
        "[frozen] 2 predictor(s) ranked from 12 cert-stage evaluation(s) "
        "(4 forward / 8 retrospective / 0 procedural)" in pr.body
    )
    assert "2 predictor(s) over 1500 resolved event(s) (retrospective by construction)" in pr.body
    assert "80998 corpus case(s): 60000 resolved / 20998 open" in pr.body
    assert "RID" in pr.body
    # Both entries cover the whole scored set and nothing was re-graded, so the
    # audit clauses stay off the line rather than reporting a computed nothing.
    assert "superseded" not in pr.body
    assert "unequal scored-set coverage" not in pr.body


def test_the_leaderboard_headline_flags_a_regrade_and_uneven_coverage(tmp_path: Path) -> None:
    """The refresh PR body is the surface a maintainer reads.

    A supersession means a standing may have moved on a re-grade, and unequal
    coverage means two entries were compared over different event sets. Neither
    is recoverable from the counts on the line, and the build-time warning lands
    in the run log rather than in the PR.
    """
    metrics = _metrics_dir(tmp_path)
    board = read_model(metrics / "leaderboard.json", Leaderboard)
    board.superseded_gradings = 2
    board.entries[1].events_scored = 4
    write_json(metrics / "leaderboard.json", board)

    pr = render_refresh_pr(["metrics/leaderboard.json"], metrics.parent, "RID")

    assert pr is not None
    assert "2 superseded grading(s) collapsed away" in pr.body
    # The magnitude travels with the flag: this is the line most likely to be
    # quoted out of the body, and a flag without an `n` cannot be read.
    assert "unequal scored-set coverage (codex-baseline 4/6)" in pr.body


def test_the_leaderboard_headline_names_a_wholly_absent_predictor(tmp_path: Path) -> None:
    """The shortfall scan iterates entries, so a predictor an engine-wide outage
    kept out of a block entirely leaves no entry to scan — the roster check is
    what names it. Without a roster the check stays off rather than reading an
    empty roster as universal absence."""
    metrics = _metrics_dir(tmp_path)
    roster = ["claude-baseline", "codex-baseline", "gemini-baseline"]

    pr = render_refresh_pr(
        ["metrics/leaderboard.json"], metrics.parent, "RID", predictor_roster=roster
    )
    assert pr is not None
    # The block is named beside the predictor: which population lost the engine
    # decides the comparability consequence.
    assert "absent from a populated block: gemini-baseline from `cert board`" in pr.body
    assert "not a cross-engine comparison" in pr.body

    without_roster = render_refresh_pr(["metrics/leaderboard.json"], metrics.parent, "RID")
    assert without_roster is not None
    assert "absent from a populated block" not in without_roster.body

    # Absence is judged per populated block, not against the union of all
    # entries: a predictor on the cert board but missing from a populated stage
    # block is named with that block's key.
    board = read_model(metrics / "leaderboard.json", Leaderboard)
    board.stages = {
        "interim@application-arrival": LeaderboardStage(
            evaluations_total=3,
            events_scored=1,
            entries=[
                LeaderboardStageEntry(predictor_id="claude-baseline", evaluators=3, events_scored=1)
            ],
        )
    }
    write_json(metrics / "leaderboard.json", board)
    per_block = render_refresh_pr(
        ["metrics/leaderboard.json"],
        metrics.parent,
        "RID",
        predictor_roster=["claude-baseline", "codex-baseline"],
    )
    assert per_block is not None
    assert "codex-baseline from `interim@application-arrival`" in per_block.body
    assert "codex-baseline from `cert board`" not in per_block.body


def test_the_leaderboard_headline_appends_the_unranked_stage_totals(tmp_path: Path) -> None:
    """A file whose ranked board is the frozen empty state can still hold
    populated stage blocks; the line says so rather than reading as an empty
    artifact."""
    metrics = _metrics_dir(tmp_path)
    board = read_model(metrics / "leaderboard.json", Leaderboard)
    board.stages = {
        "interim@application-arrival": LeaderboardStage(
            evaluations_total=6,
            events_scored=2,
            forward_evaluations=6,
            entries=[
                LeaderboardStageEntry(predictor_id="claude-baseline", evaluators=3, events_scored=2)
            ],
        )
    }
    write_json(metrics / "leaderboard.json", board)

    pr = render_refresh_pr(["metrics/leaderboard.json"], metrics.parent, "RID")
    assert pr is not None
    # The event denominator travels with the volume count, so the evaluations
    # cannot be read as a scored population.
    assert "6 evaluation(s) over 2 scored event(s) in 1 unranked stage block(s)" in pr.body


def test_pr_carries_the_claim_score_surface_with_a_sensible_suppressed_headline(
    tmp_path: Path,
) -> None:
    # The suppressed state is the shipping state (no committed evaluation
    # carries a block yet), so the headline must read as honest counts plus a
    # withheld coefficient — never as a broken artifact.
    pr = render_refresh_pr(["metrics/claim-scores.json"], _metrics_dir(tmp_path).parent, "RID")
    assert pr is not None
    assert pr.title == "metrics: refresh claim-scores"
    assert (
        "[frozen] 0 of 9 evaluation(s) carry claim scores; "
        "forward judge agreement: suppressed (n=0 < 10)" in pr.body
    )


def test_pr_carries_the_docket_pack(tmp_path: Path) -> None:
    # An artifact missing from the display order is silently absent from the
    # refresh PR, so the court-facing pack has to be listed with its own headline.
    pr = render_refresh_pr(
        ["metrics/docket.md", "metrics/docket.json"], _metrics_dir(tmp_path).parent, "RID"
    )
    assert pr is not None
    assert pr.title == "metrics: refresh docket"
    assert "9924 live-slice case(s) (9327 resolved) over 2 Term(s)" in pr.body
    assert "human-readable docket-pack companion" in pr.body


def test_partial_refresh_lists_only_the_changed_artifacts(tmp_path: Path) -> None:
    metrics = _metrics_dir(tmp_path)
    pr = render_refresh_pr(["metrics/leaderboard.json"], metrics.parent, "RID")
    assert pr is not None
    assert pr.title == "metrics: refresh leaderboard"
    assert "backtest" not in pr.body
    assert "statpack" not in pr.body


def test_unrecognized_paths_alone_yield_no_pr(tmp_path: Path) -> None:
    # Only the known artifacts drive a refresh PR; a stray path is not a refresh.
    assert render_refresh_pr(["metrics/other.json"], _metrics_dir(tmp_path).parent, "RID") is None


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


def test_the_refresh_carries_the_scope_manifest(tmp_path: Path) -> None:
    """`data/scope/scope.json` is the one refreshed artifact outside `metrics/`.

    It is deterministic and git-tracked like the rest, and it is the only surface
    that publishes the salience decision — so drift in it falsifies a claim
    `README.md` makes rather than merely aging a number. It has to be named in the
    display order to appear in a refresh PR at all.
    """
    _metrics_dir(tmp_path)
    write_json(
        tmp_path / "data" / "scope" / "scope.json",
        ScopeManifest(cases=3102, eligible=2900, excluded=202),
    )
    pr = render_refresh_pr(["data/scope/scope.json"], tmp_path, "RID")
    assert pr is not None
    assert "`data/scope/scope.json`" in pr.body
    assert "3102 public case(s)" in pr.body
    assert "2900 eligible" in pr.body


def test_a_skipped_scope_manifest_says_so_rather_than_reporting_zero(tmp_path: Path) -> None:
    """The command writes an empty `skipped` manifest when the corpus is absent.
    A refresh PR that reported that as "0 public cases" would read as the public
    set collapsing rather than as the corpus not being on disk."""
    _metrics_dir(tmp_path)
    write_json(tmp_path / "data" / "scope" / "scope.json", ScopeManifest(skipped=True))
    pr = render_refresh_pr(["data/scope/scope.json"], tmp_path, "RID")
    assert pr is not None
    assert "skipped (no corpus" in pr.body


def test_artifacts_are_matched_on_path_not_basename(tmp_path: Path) -> None:
    """The display order carries directories now, so a same-named file elsewhere
    cannot be mistaken for a refreshed artifact."""
    _metrics_dir(tmp_path)
    assert render_refresh_pr(["somewhere/else/leaderboard.json"], tmp_path, "RID") is None
