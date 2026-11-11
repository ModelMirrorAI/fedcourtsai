"""The forward record over time, read from the committed leaderboards.

``metrics/leaderboard.json`` is overwritten by each refresh, so how a
predictor's figures moved is in its git history and nowhere else. This module
reads that history instead of keeping a second copy: every first-parent
landing of the board on a ref is one revision, and each revision's forward
figures are copied out per **series** — a (predictor, counting window, stage)
triple, with the predictor's pooled record as a series of its own. Nothing is
recomputed, so a point can never disagree with the board it came from.

First-parent, because a refresh lands through a merge: the merge is when the
board reached the ref, and the branch commit beneath it was never in force.
A board written under an older schema may not parse; its commit is listed as
unreadable and its figures are absent. One that parses without a field the
current schema added has that figure null, never zero.

:func:`movements` compares two boards series by series and flags what an
operator should look at: a series of at least
:data:`MIN_EVENTS_FOR_LEVEL_FLAGS` events at or below its always-deny floor or
under zero prior-Term skill (the gate counts the accuracy column's events,
which is not the skill column's own denominator), a series that lost events,
and a series whose accuracy moved
by more than its added events can explain. The last is arithmetic: ``k`` of
``n`` events correct, then ``a`` more events, bounds the new accuracy between
``k / (n + a)`` and ``(k + a) / (n + a)``; outside that, earlier cells were
re-scored, re-windowed or left the population. These are alarms about the
artifact, not findings about a predictor (``metrics/README.md``).
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from . import statpack_history
from .leaderboard import stage_moment_key
from .pipeline.moments import first_moment
from .schemas import (
    Leaderboard,
    LeaderboardEntry,
    LeaderboardStageEntry,
    PerformanceHistory,
    PerformanceMovement,
    PerformancePoint,
    PerformanceRevision,
    Stage,
)

DEFAULT_REF = "origin/main"
LEADERBOARD_PATH = "metrics/leaderboard.json"

#: The stage key of the board's top-level entries: the ranked cert board.
RANKED_STAGE = stage_moment_key(Stage.cert, first_moment(Stage.cert))

AT_OR_BELOW_FLOOR = "at-or-below-floor"
NEGATIVE_SKILL = "negative-skill"
EVENTS_REMOVED = "events-removed"
RESCORED = "rescored"

#: The fewest events a series holds before its level is flagged. Below it a
#: series at its floor or under zero skill is one or two calls, not a state.
MIN_EVENTS_FOR_LEVEL_FLAGS = 10

#: Slack on the re-scoring bound, for accuracies the board rounds.
_BOUND_TOLERANCE = 1e-6


def _point(entry: LeaderboardEntry | LeaderboardStageEntry, stage: str) -> PerformancePoint | None:
    forward = entry.forward
    if forward is None:
        return None
    return PerformancePoint(
        predictor_id=entry.predictor_id,
        process_window=entry.process_window,
        stage=stage,
        events=(
            forward.accuracy_events_scored
            if "accuracy_events_scored" in forward.model_fields_set
            else None
        ),
        gradings=forward.evaluations,
        event_accuracy=forward.event_accuracy,
        event_always_deny_accuracy=forward.event_always_deny_accuracy,
        mean_brier_score=forward.mean_brier_score,
        population_brier_skill_score=forward.population_brier_skill_score,
        population_realized_term_skill_score=forward.population_realized_term_skill_score,
    )


def _key(point: PerformancePoint) -> tuple[str, str, str]:
    return (point.stage, point.predictor_id, point.process_window or "")


def board_points(board: Leaderboard) -> list[PerformancePoint]:
    """Every forward series one board carries, in (stage, predictor, window) order.

    The ranked board's entries and its per-window cut file under
    :data:`RANKED_STAGE`; each ``stages`` block files under its own key. A
    series with no forward stratum is left out.
    """
    blocks: list[tuple[str, Sequence[LeaderboardEntry | LeaderboardStageEntry]]] = [
        (RANKED_STAGE, [*board.entries, *board.by_protocol])
    ]
    for stage, block in board.stages.items():
        blocks.append((stage, [*block.entries, *block.by_protocol]))
    points = [
        point
        for stage, entries in blocks
        for entry in entries
        if (point := _point(entry, stage)) is not None
    ]
    return sorted(points, key=_key)


def _rescored(before: PerformancePoint, after: PerformancePoint) -> bool:
    """Whether accuracy moved by more than the events added can explain."""
    if (
        before.event_accuracy is None
        or after.event_accuracy is None
        or before.events is None
        or not after.events
    ):
        return False
    added = after.events - before.events
    if added < 0:
        return False
    correct_before = before.event_accuracy * before.events
    low = correct_before / after.events
    high = (correct_before + added) / after.events
    return not low - _BOUND_TOLERANCE <= after.event_accuracy <= high + _BOUND_TOLERANCE


def _flags(before: PerformancePoint | None, after: PerformancePoint) -> list[str]:
    flags: list[str] = []
    readable = after.events is not None and after.events >= MIN_EVENTS_FOR_LEVEL_FLAGS
    if (
        readable
        and after.event_accuracy is not None
        and after.event_always_deny_accuracy is not None
        and after.event_accuracy <= after.event_always_deny_accuracy
    ):
        flags.append(AT_OR_BELOW_FLOOR)
    skill = after.population_brier_skill_score
    if readable and skill is not None and skill < 0:
        flags.append(NEGATIVE_SKILL)
    if before is not None and before.events is not None and after.events is not None:
        if after.events < before.events:
            flags.append(EVENTS_REMOVED)
        elif _rescored(before, after):
            flags.append(RESCORED)
    return flags


def movements(
    before: Sequence[PerformancePoint], after: Sequence[PerformancePoint]
) -> list[PerformanceMovement]:
    """Each series the newer board carries, against the same series before it."""
    earlier = {_key(point): point for point in before}
    rows: list[PerformanceMovement] = []
    for point in sorted(after, key=_key):
        prior = earlier.get(_key(point))
        rows.append(
            PerformanceMovement(
                predictor_id=point.predictor_id,
                process_window=point.process_window,
                stage=point.stage,
                events_before=prior.events if prior is not None else None,
                events_after=point.events,
                event_accuracy_before=prior.event_accuracy if prior is not None else None,
                event_accuracy_after=point.event_accuracy,
                floor_after=point.event_always_deny_accuracy,
                mean_brier_before=prior.mean_brier_score if prior is not None else None,
                mean_brier_after=point.mean_brier_score,
                skill_before=prior.population_brier_skill_score if prior is not None else None,
                skill_after=point.population_brier_skill_score,
                flags=_flags(prior, point),
            )
        )
    return rows


def landings(repo: Path, ref: str) -> list[tuple[str, datetime]] | None:
    """The board's first-parent landings on ``ref``, oldest first.

    ``None`` where the history cannot be read at all — git missing, no such
    ref, or a shallow clone, whose history would read as a shorter record
    rather than as an unknown one.
    """
    if (
        statpack_history.git_read(repo, "rev-parse", "--is-shallow-repository") or ""
    ).strip() != "false":
        return None
    log = statpack_history.git_read(
        repo,
        "log",
        "--first-parent",
        "--format=%H %ct",
        "--end-of-options",
        ref,
        "--",
        LEADERBOARD_PATH,
    )
    if log is None:
        return None
    rows = [line.split() for line in log.splitlines() if line.strip()]
    return [(sha, datetime.fromtimestamp(int(stamp), UTC)) for sha, stamp in reversed(rows)]


def board_at(repo: Path, sha: str) -> Leaderboard | None:
    """The board one commit carries, or ``None`` where it does not parse."""
    text = statpack_history.git_read(repo, "cat-file", "blob", f"{sha}:{LEADERBOARD_PATH}")
    if text is None:
        return None
    try:
        return Leaderboard.model_validate_json(text)
    except ValidationError:
        return None


def build_history(repo: Path, ref: str = DEFAULT_REF) -> PerformanceHistory | None:
    """The record over ``ref``'s landings, or ``None`` where no history is readable."""
    found = landings(repo, ref)
    if found is None:
        return None
    revisions: list[PerformanceRevision] = []
    unreadable: list[str] = []
    for sha, landed in found:
        board = board_at(repo, sha)
        if board is None:
            unreadable.append(sha)
            continue
        revisions.append(
            PerformanceRevision(commit=sha, landed=landed.date(), points=board_points(board))
        )
    moved = movements(revisions[-2].points, revisions[-1].points) if len(revisions) > 1 else []
    return PerformanceHistory(ref=ref, revisions=revisions, unreadable=unreadable, movements=moved)


def previous_board(repo: Path, ref: str = DEFAULT_REF) -> tuple[Leaderboard, str] | None:
    """The newest readable board before ``ref``'s current one, with its landing date."""
    found = landings(repo, ref)
    if not found:
        return None
    for sha, landed in reversed(found[:-1]):
        board = board_at(repo, sha)
        if board is not None:
            return board, landed.date().isoformat()
    return None
