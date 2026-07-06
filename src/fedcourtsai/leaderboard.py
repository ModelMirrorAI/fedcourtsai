"""Aggregate the evaluations ledger into a ranked per-predictor leaderboard.

Deterministic and offline: a pure function of the committed artifacts under
``data/`` — no network, no clock, no randomness — so the same ledger always
yields byte-identical output. ``fedcourts leaderboard`` writes the result to
``metrics/leaderboard.json``.

Every scored cell is stratified by the **pre-registration standard** before any
aggregation: a prediction committed while its event was still open is a true
*forward* forecast; a prediction over an event that had already resolved is
*retrospective* by construction — the outcome is public knowledge inside every
modern model's training data, so such a cell measures recall plus calibration,
never ex-ante forecasting skill. The two strata are aggregated separately and
never blended into one headline number. :func:`classify_stratum` is the single
definition of the split, derivable offline from committed artifacts (the
prediction's ``created_at`` vs the outcome's ``resolved_at``).
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import date, datetime
from typing import Literal

from .schemas import Evaluation, Leaderboard, LeaderboardEntry, LeaderboardStratum

Stratum = Literal["forward", "retrospective"]

FORWARD: Stratum = "forward"
RETROSPECTIVE: Stratum = "retrospective"

# Brier scores are bounded in [0, 1]; predictors that never reported one sort
# after every predictor that did, without colliding with a real worst score.
_NO_BRIER: float = 2.0
# Accuracies are bounded in [0, 1]; a predictor with no cells in a stratum sorts
# after every predictor that has any, without colliding with a real worst score.
_NO_ACCURACY: float = -1.0


def classify_stratum(prediction_created_at: datetime, resolved_at: date) -> Stratum:
    """Which pre-registration stratum a scored cell belongs to.

    Retrospective when the event's resolution predates the prediction's commit.
    A same-day tie also counts as retrospective — the conservative reading, so a
    cell whose ordering within the day is unknowable is never presented as a
    forward forecast.
    """
    return RETROSPECTIVE if resolved_at <= prediction_created_at.date() else FORWARD


def _mean(values: Sequence[float]) -> float | None:
    """Mean of the present values, or ``None`` when none were reported."""
    return sum(values) / len(values) if values else None


def _aggregate(evals: Sequence[Evaluation]) -> LeaderboardStratum | None:
    """One stratum's aggregates, or ``None`` when the stratum has no evaluations."""
    if not evals:
        return None
    return LeaderboardStratum(
        events_scored=len({(ev.case_id, ev.event_id) for ev in evals}),
        evaluations=len(evals),
        accuracy=sum(ev.correct for ev in evals) / len(evals),
        mean_brier_score=_mean([ev.brier_score for ev in evals if ev.brier_score is not None]),
        mean_vote_accuracy=_mean(
            [ev.vote_accuracy for ev in evals if ev.vote_accuracy is not None]
        ),
        mean_reasoning_quality=_mean(
            [ev.reasoning_quality for ev in evals if ev.reasoning_quality is not None]
        ),
    )


def _rank_key(entry: LeaderboardEntry) -> tuple[float, float, float, float, str]:
    """Total order: forward stratum first, retrospective as tie-break, then id.

    Forward accuracy (desc) then forward Brier (asc, missing last) lead because
    only the forward stratum measures forecasting skill; the retrospective pair
    orders predictors that have no forward cells yet. ``predictor_id`` makes the
    ranking deterministic under full ties.
    """

    def acc(stratum: LeaderboardStratum | None) -> float:
        return stratum.accuracy if stratum is not None else _NO_ACCURACY

    def brier(stratum: LeaderboardStratum | None) -> float:
        if stratum is None or stratum.mean_brier_score is None:
            return _NO_BRIER
        return stratum.mean_brier_score

    return (
        -acc(entry.forward),
        brier(entry.forward),
        -acc(entry.retrospective),
        brier(entry.retrospective),
        entry.predictor_id,
    )


def build_leaderboard(cells: Iterable[tuple[Evaluation, Stratum]]) -> Leaderboard:
    """Roll stratified evaluations up into a best-first leaderboard.

    One entry per predictor, each carrying its **forward** and **retrospective**
    aggregates separately (a stratum with no cells is null, never zero-filled
    into a blend). Entries rank by forward accuracy (desc), forward Brier (asc,
    missing last), the retrospective pair as tie-break, then ``predictor_id`` —
    a total order, so the ranking is deterministic even under ties.
    """
    by_predictor: dict[str, dict[Stratum, list[Evaluation]]] = defaultdict(
        lambda: {FORWARD: [], RETROSPECTIVE: []}
    )
    for ev, stratum in cells:
        by_predictor[ev.predictor_id][stratum].append(ev)

    entries: list[LeaderboardEntry] = []
    for predictor_id, strata in by_predictor.items():
        evals = strata[FORWARD] + strata[RETROSPECTIVE]
        entries.append(
            LeaderboardEntry(
                predictor_id=predictor_id,
                rank=1,  # provisional; assigned after sorting
                evaluators=len({ev.evaluator_id for ev in evals}),
                forward=_aggregate(strata[FORWARD]),
                retrospective=_aggregate(strata[RETROSPECTIVE]),
            )
        )

    entries.sort(key=_rank_key)
    for position, entry in enumerate(entries, start=1):
        entry.rank = position

    def _stratum_total(stratum: Stratum) -> int:
        return sum(len(strata[stratum]) for strata in by_predictor.values())

    return Leaderboard(
        predictors_ranked=len(entries),
        evaluations_total=_stratum_total(FORWARD) + _stratum_total(RETROSPECTIVE),
        forward_evaluations=_stratum_total(FORWARD),
        retrospective_evaluations=_stratum_total(RETROSPECTIVE),
        entries=entries,
    )
