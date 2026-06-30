"""Shared finalize helpers for the matrix workflows.

The matrix stages (``run-predict`` / ``run-evaluate`` / ``run-reconcile``) used to
have the workflow name a branch and open a PR per cell from this module; that
routing now lives in :mod:`fedcourtsai.collect` (each cell uploads an artifact and
a ``collect`` job opens one PR per run). What remains here is the small piece every
cell still needs before it uploads: the role enum, and the check for whether the
agent actually wrote its own judgment artifact (so a cell that only has the
materialized ``event.yaml`` scaffold is reported as "produced nothing" rather than
committed). The ``finalize-produced`` CLI command wraps it.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from .paths import CasePaths


class FinalizeRole(StrEnum):
    """Which matrix workflow is running; selects role-specific behavior."""

    predict = "predict"
    evaluate = "evaluate"
    reconcile = "reconcile"


def agent_produced_output(
    role: FinalizeRole,
    *,
    data_root: Path,
    court: str,
    docket: int,
    event: str,
    actor: str,
    run_id: str,
) -> bool:
    """Whether the agent wrote its own judgment artifact for this cell.

    The predict/evaluate workflows materialize the event's ``event.yaml`` *before*
    the agent runs, so "the working tree changed" is not "the agent produced a
    prediction": a failed agent leaves only that materialized event file. This
    checks for the agent's actual output — the ``prediction.json`` (predict) or any
    ``evaluation.json`` for this evaluator and run (evaluate) — so the cell can
    report whether it produced output rather than uploading only the event
    scaffold. Reconcile has its own settled-events check and is not handled here.
    """
    events = CasePaths(data_root, court, docket).event(event)
    if role is FinalizeRole.predict:
        return events.prediction(actor, run_id).is_file()
    if role is FinalizeRole.evaluate:
        evaluator_root = events.base / "evaluations" / actor
        return any(evaluator_root.glob(f"*/{run_id}/evaluation.json"))
    raise ValueError(f"agent_produced_output is for predict/evaluate, not {role.value}")
