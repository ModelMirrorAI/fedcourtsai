"""Aggregate the evaluations ledger into a ranked per-predictor leaderboard.

Deterministic and offline: a pure function of the committed ``evaluation.json``
rows under ``data/`` — no network, no clock, no randomness — so the same ledger
always yields byte-identical output. ``fedcourts leaderboard`` writes the result
to ``metrics/leaderboard.json``.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence

from .schemas import Evaluation, Leaderboard, LeaderboardEntry

# Brier scores are bounded in [0, 1]; predictors that never reported one sort
# after every predictor that did, without colliding with a real worst score.
_NO_BRIER: float = 2.0


def _mean(values: Sequence[float]) -> float | None:
    """Mean of the present values, or ``None`` when none were reported."""
    return sum(values) / len(values) if values else None


def build_leaderboard(evaluations: Iterable[Evaluation]) -> Leaderboard:
    """Roll the evaluations ledger up into a best-first leaderboard.

    One entry per predictor: mean correctness (accuracy), mean Brier score, mean
    vote accuracy, a mean reasoning-quality summary, and counts of events scored,
    evaluations, and distinct evaluators. Optional metrics average only over the
    evaluations that reported them. Entries rank by accuracy (desc), then mean
    Brier score (asc, missing last), then ``predictor_id`` — a total order, so the
    ranking is deterministic even under ties.
    """
    by_predictor: dict[str, list[Evaluation]] = defaultdict(list)
    for ev in evaluations:
        by_predictor[ev.predictor_id].append(ev)

    entries: list[LeaderboardEntry] = []
    for predictor_id, evals in by_predictor.items():
        accuracy = sum(ev.correct for ev in evals) / len(evals)
        entries.append(
            LeaderboardEntry(
                predictor_id=predictor_id,
                rank=1,  # provisional; assigned after sorting
                events_scored=len({(ev.case_id, ev.event_id) for ev in evals}),
                evaluations=len(evals),
                evaluators=len({ev.evaluator_id for ev in evals}),
                accuracy=accuracy,
                mean_brier_score=_mean(
                    [ev.brier_score for ev in evals if ev.brier_score is not None]
                ),
                mean_vote_accuracy=_mean(
                    [ev.vote_accuracy for ev in evals if ev.vote_accuracy is not None]
                ),
                mean_reasoning_quality=_mean(
                    [ev.reasoning_quality for ev in evals if ev.reasoning_quality is not None]
                ),
            )
        )

    entries.sort(
        key=lambda e: (
            -e.accuracy,
            e.mean_brier_score if e.mean_brier_score is not None else _NO_BRIER,
            e.predictor_id,
        )
    )
    for position, entry in enumerate(entries, start=1):
        entry.rank = position

    return Leaderboard(
        predictors_ranked=len(entries),
        evaluations_total=sum(e.evaluations for e in entries),
        entries=entries,
    )
