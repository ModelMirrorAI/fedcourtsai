"""The forward record over committed leaderboards, and the movement check."""

import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import ops
from fedcourtsai.cli import app
from fedcourtsai.performance_history import (
    AT_OR_BELOW_FLOOR,
    EVENTS_REMOVED,
    LEADERBOARD_PATH,
    NEGATIVE_SKILL,
    RANKED_STAGE,
    RESCORED,
    board_points,
    build_history,
    movements,
    previous_board,
)
from fedcourtsai.schemas import (
    Leaderboard,
    LeaderboardEntry,
    LeaderboardStage,
    LeaderboardStageEntry,
    LeaderboardStratum,
    PerformanceHistory,
    PerformancePoint,
)
from fedcourtsai.serialize import read_model, write_json


def _stratum(
    events: int, accuracy: float, *, floor: float | None = 0.9, skill: float | None = 0.3
) -> LeaderboardStratum:
    return LeaderboardStratum(
        events_scored=events,
        evaluations=events * 3,
        accuracy=accuracy,
        event_accuracy=accuracy,
        accuracy_events_scored=events,
        event_always_deny_accuracy=floor,
        mean_brier_score=0.05,
        population_brier_skill_score=skill,
    )


def _board(events: int = 20, accuracy: float = 0.95, **kw: float | None) -> Leaderboard:
    forward = _stratum(events, accuracy, **kw)
    return Leaderboard(
        predictors_ranked=1,
        evaluations_total=events * 3,
        events_scored=events,
        entries=[
            LeaderboardEntry(
                predictor_id="alpha", evaluators=3, events_scored=events, forward=forward
            )
        ],
        by_protocol=[
            LeaderboardEntry(
                predictor_id="alpha",
                process_window="proc-v8",
                evaluators=3,
                events_scored=events,
                forward=forward,
            )
        ],
        stages={
            "interim@arrival": LeaderboardStage(
                evaluations_total=12,
                events_scored=4,
                entries=[
                    LeaderboardStageEntry(
                        predictor_id="alpha",
                        evaluators=3,
                        events_scored=4,
                        forward=_stratum(4, 0.5),
                    )
                ],
            )
        },
    )


def _point(events: int, accuracy: float | None, **kw: float | None) -> PerformancePoint:
    fields: dict[str, float | None] = {
        "event_always_deny_accuracy": 0.9,
        "population_brier_skill_score": 0.3,
    }
    fields.update(kw)
    return PerformancePoint(
        predictor_id="alpha",
        stage=RANKED_STAGE,
        events=events,
        gradings=events,
        event_accuracy=accuracy,
        **fields,
    )


def test_a_board_yields_one_point_per_series_under_its_stage() -> None:
    points = board_points(_board())
    assert [(p.stage, p.process_window, p.events) for p in points] == [
        (RANKED_STAGE, None, 20),
        (RANKED_STAGE, "proc-v8", 20),
        ("interim@arrival", None, 4),
    ]
    assert points[0].gradings == 60
    assert points[0].event_accuracy == 0.95


def test_a_series_with_no_forward_stratum_is_left_out() -> None:
    board = Leaderboard(
        predictors_ranked=0,
        evaluations_total=0,
        entries=[LeaderboardEntry(predictor_id="idle", evaluators=0, events_scored=0)],
    )
    assert board_points(board) == []


def test_added_events_inside_the_bound_raise_no_flag() -> None:
    # 19 of 20, then two more events, one right: 20 of 22.
    (row,) = movements([_point(20, 0.95)], [_point(22, 20 / 22)])
    assert row.flags == []
    assert (row.events_before, row.events_after) == (20, 22)


def test_accuracy_moving_past_what_the_added_events_allow_is_rescored() -> None:
    # 19 of 20, then two more: at best 21 of 22, at worst 19 of 22.
    (row,) = movements([_point(20, 0.95)], [_point(22, 18 / 22)])
    assert row.flags == [AT_OR_BELOW_FLOOR, RESCORED]
    # No event was added, yet the figure moved.
    (same,) = movements([_point(20, 0.95)], [_point(20, 0.9)])
    assert RESCORED in same.flags


def test_a_series_that_shrank_is_flagged_as_such() -> None:
    (row,) = movements([_point(20, 0.95)], [_point(18, 0.95)])
    assert row.flags == [EVENTS_REMOVED]


def test_level_flags_wait_for_ten_events() -> None:
    at_floor = {"event_always_deny_accuracy": 0.95, "population_brier_skill_score": -0.1}
    (small,) = movements([], [_point(9, 0.95, **at_floor)])
    assert small.flags == []
    assert small.events_before is None
    (readable,) = movements([], [_point(10, 0.95, **at_floor)])
    assert readable.flags == [AT_OR_BELOW_FLOOR, NEGATIVE_SKILL]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@users.noreply.github.com",
            *args,
        ],
        check=True,
        capture_output=True,
    )


def _land(repo: Path, content: str | Leaderboard) -> None:
    path = repo / LEADERBOARD_PATH
    if isinstance(content, str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    else:
        write_json(path, content)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "board")


def _repo(tmp_path: Path, *boards: str | Leaderboard) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    for board in boards:
        _land(repo, board)
    return repo


def test_the_history_reads_every_landing_oldest_first_and_names_the_unreadable(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path, '{"not": "a board"}', _board(20, 0.95), _board(22, 20 / 22))

    history = build_history(repo, "main")

    assert history is not None
    assert len(history.unreadable) == 1
    assert [rev.points[0].events for rev in history.revisions] == [20, 22]
    pooled = [row for row in history.movements if row.stage == RANKED_STAGE]
    assert pooled[0].events_before == 20
    assert pooled[0].flags == []


def test_the_previous_board_skips_an_unreadable_landing(tmp_path: Path) -> None:
    repo = _repo(tmp_path, _board(20, 0.95), '{"not": "a board"}', _board(22, 20 / 22))

    found = previous_board(repo, "main")

    assert found is not None
    assert found[0].entries[0].forward is not None
    assert found[0].entries[0].forward.accuracy_events_scored == 20


def test_a_single_landing_has_no_previous_board_and_no_movement(tmp_path: Path) -> None:
    repo = _repo(tmp_path, _board())
    assert previous_board(repo, "main") is None
    history = build_history(repo, "main")
    assert history is not None
    assert history.movements == []


def test_an_unknown_ref_is_no_history(tmp_path: Path) -> None:
    repo = _repo(tmp_path, _board())
    assert build_history(repo, "no-such-ref") is None


def test_the_command_writes_the_history_and_refuses_an_unknown_ref(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, _board(20, 0.95), _board(22, 20 / 22))
    monkeypatch.chdir(repo)
    out = tmp_path / "history.json"
    runner = CliRunner()

    result = runner.invoke(app, ["performance-history", "--ref", "main", "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert len(read_model(out, PerformanceHistory).revisions) == 2

    refused = runner.invoke(app, ["performance-history", "--ref", "no-such-ref"])
    assert refused.exit_code == 2


def test_the_digest_prints_only_pooled_series_that_moved_or_trip_a_flag() -> None:
    lines = "\n".join(
        ops._movement_lines(
            ops.Vintaged(_board(22, 18 / 22), "2026-11-09"),
            ops.Vintaged(_board(20, 0.95), "2026-11-07"),
        )
    )
    assert "### Movement since the previous board" in lines
    assert "the board landed 2026-11-07" in lines
    assert "| cert@distribution | alpha | 20 → 22 | 95.0% → 81.8% |" in lines
    assert "`rescored`" in lines
    # The per-window row and the unmoved interim series are not printed.
    assert "interim@arrival" not in lines
    assert lines.count("| alpha |") == 1


def test_the_digest_says_when_nothing_moved_and_is_silent_without_a_previous_board() -> None:
    board = ops.Vintaged(_board(), "2026-11-09")
    quiet = ops._movement_lines(board, ops.Vintaged(_board(), "2026-11-07"))
    assert any("No pooled forward series moved" in line for line in quiet)
    assert ops._movement_lines(board, None) == []
