"""``run-evaluate`` helpers.

Each evaluator scores each predictor's prediction against the realized
``outcome.json``. The qualitative judgment (reasoning quality) is produced by an
agent; the quantitative pieces (correctness, Brier score) are deterministic and
provided here so every evaluator computes them identically.
"""

from __future__ import annotations

from ..schemas import Outcome, Prediction


def is_correct(prediction: Prediction, outcome: Outcome) -> int:
    return int(prediction.predicted_disposition == outcome.actual_disposition)


def brier_score(prediction: Prediction, outcome: Outcome) -> float:
    """Brier score for the binary granted/denied forecast (lower is better)."""
    return (prediction.probability - outcome.actual_granted) ** 2


def vote_accuracy(prediction: Prediction, outcome: Outcome) -> float | None:
    """Fraction of predicted panel votes that matched, if votes were predicted."""
    if not prediction.votes or not outcome.votes:
        return None
    actual = {v.judge: v.vote for v in outcome.votes}
    scored = [v for v in prediction.votes if v.judge in actual]
    if not scored:
        return None
    hits = sum(1 for v in scored if actual[v.judge] == v.vote)
    return hits / len(scored)
