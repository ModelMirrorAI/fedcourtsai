"""Builds the GitHub Actions ``strategy.matrix`` for the agent fan-out.

``run-predict`` runs every enabled predictor against every open event; this is
the cartesian product the matrix needs. ``run-evaluate`` runs every enabled
evaluator against every resolved event (each evaluator scores all predictors for
that event internally, so predictors are not part of the matrix dimension).

Keeping this in the library (rather than inline YAML/JS) makes the routing
testable and keeps the registry the single source of truth for which agents
exist — the same place the future hypothesis-generation harness will add new
predictors.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .registry import enabled_evaluators, enabled_predictors


def predict_matrix(
    predictors_path: Path,
    court_id: str,
    docket_id: int,
    event_ids: list[str],
    run_id: str,
) -> dict[str, list[dict[str, Any]]]:
    include: list[dict[str, Any]] = []
    for predictor in enabled_predictors(predictors_path):
        for event_id in event_ids:
            include.append(
                {
                    "predictor_id": predictor.id,
                    "engine": predictor.engine,
                    "model": predictor.model or "",
                    "prompt": predictor.prompt,
                    "court": court_id,
                    "docket": docket_id,
                    "event_id": event_id,
                    "run_id": run_id,
                }
            )
    return {"include": include}


def evaluate_matrix(
    evaluators_path: Path,
    court_id: str,
    docket_id: int,
    event_ids: list[str],
    run_id: str,
) -> dict[str, list[dict[str, Any]]]:
    include: list[dict[str, Any]] = []
    for evaluator in enabled_evaluators(evaluators_path):
        for event_id in event_ids:
            include.append(
                {
                    "evaluator_id": evaluator.id,
                    "engine": evaluator.engine,
                    "model": evaluator.model or "",
                    "prompt": evaluator.prompt,
                    "court": court_id,
                    "docket": docket_id,
                    "event_id": event_id,
                    "run_id": run_id,
                }
            )
    return {"include": include}
