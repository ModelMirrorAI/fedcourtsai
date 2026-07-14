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
never ex-ante forecasting skill. A cell whose outcome was mootness practice
(the outcome's ``disposition_basis``) is *procedural* regardless of timing —
its label tracks the Court's vacatur wording, not cert-worthiness. The strata
are aggregated separately and never blended into one headline number, and only
forward/retrospective enter the ranking. :func:`classify_stratum` is the single
definition of the timing split, derivable offline from committed artifacts (the
prediction's ``created_at`` vs the outcome's ``resolved_at``); the procedural
override lives with the join in ``store.iter_stratified_evaluations``.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Literal

from .schemas import (
    BigCaseLeaderboard,
    Evaluation,
    Leaderboard,
    LeaderboardEntry,
    LeaderboardStratum,
    Prediction,
)
from .serialize import read_model

Stratum = Literal["forward", "retrospective", "procedural"]

FORWARD: Stratum = "forward"
RETROSPECTIVE: Stratum = "retrospective"
# Cells whose outcome was mootness practice (the outcome's disposition_basis):
# the ground-truth label tracks the Court's vacatur wording rather than
# cert-worthiness, so these aggregate separately and never enter the ranking.
PROCEDURAL: Stratum = "procedural"

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
        mean_brier_skill_score=_mean(
            [ev.brier_skill_score for ev in evals if ev.brier_skill_score is not None]
        ),
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
    orders predictors that have no forward cells yet. The procedural stratum
    never contributes — vacatur-practice calls buy no rank. ``predictor_id`` makes the
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


def _kendall_tau_b(points: Sequence[tuple[float, float]]) -> float | None:
    """Kendall's tau-b rank correlation of the (x, y) points, or ``None``.

    Tau-b handles ties (big-case scores can repeat): the denominator excludes
    pairs tied on each axis, so a perfectly monotone relationship reads +1 even
    with ties. Returns ``None`` with fewer than two points or when every pair
    ties on one axis (the correlation is undefined). O(n^2), which is ample for a
    cohort-sized set.
    """
    n = len(points)
    if n < 2:
        return None
    n0 = n * (n - 1) // 2
    concordant = discordant = tie_x = tie_y = 0
    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            dx = xi - points[j][0]
            dy = yi - points[j][1]
            if dx == 0:
                tie_x += 1
            if dy == 0:
                tie_y += 1
            if dx != 0 and dy != 0:
                if (dx > 0) == (dy > 0):
                    concordant += 1
                else:
                    discordant += 1
    denominator = math.sqrt((n0 - tie_x) * (n0 - tie_y))
    if denominator == 0:
        return None
    return (concordant - discordant) / denominator


def big_case_agreement(data_root: Path) -> dict[str, BigCaseLeaderboard]:
    """Each predictor's big-case rank-agreement with the evaluator panel.

    Deterministic and offline over the committed ledger. For every
    ``(predictor, case, event)`` an evaluator gave a big-case read on, pairs the
    predictor's latest ``big_case_score`` with the **mean** of the panel's
    independent reads for that event, then correlates the predictor's ordering
    against the panel's with Kendall's tau-b (:func:`_kendall_tau_b`) across the
    scored events (one per case in the current single-event model). Predictors
    with no comparable event are absent from the map (their ``big_case`` stays
    null).
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return {}
    reads: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for path in sorted(cases_dir.glob("*/*/events/*/evaluations/*/*/*/evaluation.json")):
        evaluation = read_model(path, Evaluation)
        if evaluation.big_case is not None:
            key = (evaluation.predictor_id, evaluation.case_id, evaluation.event_id)
            reads[key].append(evaluation.big_case.evaluator_score)

    points: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for (predictor_id, case_id, event_id), evaluator_scores in reads.items():
        prediction_files = sorted(
            (cases_dir / case_id / "events" / event_id).glob(
                f"predictions/{predictor_id}/*/prediction.json"
            )
        )
        predictions = [read_model(p, Prediction) for p in prediction_files]
        if not predictions:
            continue
        latest = max(predictions, key=lambda pr: pr.created_at)
        if latest.big_case_score is None:
            continue
        panel_mean = sum(evaluator_scores) / len(evaluator_scores)
        points[predictor_id].append((latest.big_case_score, panel_mean))

    return {
        predictor_id: BigCaseLeaderboard(rank_agreement=_kendall_tau_b(pairs), cases=len(pairs))
        for predictor_id, pairs in points.items()
    }


def build_leaderboard(
    cells: Iterable[tuple[Evaluation, Stratum]],
    big_case: Mapping[str, BigCaseLeaderboard] | None = None,
) -> Leaderboard:
    """Roll stratified evaluations up into a best-first leaderboard.

    One entry per predictor, each carrying its **forward** and **retrospective**
    aggregates separately (a stratum with no cells is null, never zero-filled
    into a blend). Entries rank by forward accuracy (desc), forward Brier (asc,
    missing last), the retrospective pair as tie-break, then ``predictor_id`` —
    a total order, so the ranking is deterministic even under ties. ``big_case``
    (from :func:`big_case_agreement`) attaches each predictor's big-case
    rank-agreement as a second, orthogonal dimension that never affects the rank;
    absent from the map (or unsupplied) leaves the entry's ``big_case`` null.
    """
    by_predictor: dict[str, dict[Stratum, list[Evaluation]]] = defaultdict(
        lambda: {FORWARD: [], RETROSPECTIVE: [], PROCEDURAL: []}
    )
    for ev, stratum in cells:
        by_predictor[ev.predictor_id][stratum].append(ev)

    entries: list[LeaderboardEntry] = []
    for predictor_id, strata in by_predictor.items():
        evals = strata[FORWARD] + strata[RETROSPECTIVE] + strata[PROCEDURAL]
        entries.append(
            LeaderboardEntry(
                predictor_id=predictor_id,
                rank=1,  # provisional; assigned after sorting
                evaluators=len({ev.evaluator_id for ev in evals}),
                forward=_aggregate(strata[FORWARD]),
                retrospective=_aggregate(strata[RETROSPECTIVE]),
                procedural=_aggregate(strata[PROCEDURAL]),
                big_case=(big_case or {}).get(predictor_id),
            )
        )

    entries.sort(key=_rank_key)
    for position, entry in enumerate(entries, start=1):
        entry.rank = position

    def _stratum_total(stratum: Stratum) -> int:
        return sum(len(strata[stratum]) for strata in by_predictor.values())

    return Leaderboard(
        predictors_ranked=len(entries),
        evaluations_total=(
            _stratum_total(FORWARD) + _stratum_total(RETROSPECTIVE) + _stratum_total(PROCEDURAL)
        ),
        forward_evaluations=_stratum_total(FORWARD),
        retrospective_evaluations=_stratum_total(RETROSPECTIVE),
        procedural_evaluations=_stratum_total(PROCEDURAL),
        entries=entries,
    )
