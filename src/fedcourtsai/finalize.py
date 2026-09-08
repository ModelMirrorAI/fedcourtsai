"""Shared finalize helpers for the matrix workflows.

The matrix stages (``run-predict`` / ``run-evaluate``) used to
have the workflow name a branch and open a PR per cell from this module; that
routing now lives in :mod:`fedcourtsai.collect` (each cell uploads an artifact and
a ``collect`` job opens one PR per run). What remains here is the small piece every
cell still needs before it uploads: the role enum, and the check for whether the
agent actually wrote its own judgment artifact (so a cell that only has the
materialized ``event.yaml`` scaffold is reported as "produced nothing" rather than
committed). The ``finalize-produced`` CLI command wraps it.

Beside it sits the same question asked *forward* rather than backward:
:func:`required_outputs` names every file a finished cell of this role owes,
before the cell has written any of them. The engine watchdog's completion
sentinel (``scripts/engine-watchdog.sh``, armed by the cell workflows through
``fedcourts cell-outputs``) polls that list while the agent runs, so a cell whose
work is done but whose engine step will not conclude can have its step ended with
the output intact instead of destroyed at the job cap. The two are deliberately
different strengths: ``agent_produced_output`` is the one artifact that makes a
cell worth committing at all, while the sentinel's list is the *whole* contract —
it decides that an agent has finished, so anything short of complete has to read
as still working.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path

from .paths import CasePaths, EventPaths


class FinalizeRole(StrEnum):
    """Which matrix workflow is running; selects role-specific behavior."""

    predict = "predict"
    evaluate = "evaluate"


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
    scaffold.
    """
    events = CasePaths(data_root, court, docket).event(event)
    if role is FinalizeRole.predict:
        return events.prediction(actor, run_id).is_file()
    if role is FinalizeRole.evaluate:
        return any(events.evaluator_dir(actor).glob(f"*/{run_id}/evaluation.json"))
    raise ValueError(f"agent_produced_output is for predict/evaluate, not {role.value}")


def cell_output_root(
    role: FinalizeRole,
    *,
    data_root: Path,
    court: str,
    docket: int,
    event: str,
    actor: str,
    run_id: str,
) -> Path:
    """The one directory a cell of this role writes its own output under.

    The sentinel watches this subtree for *write quiescence*, so it has to cover
    every path :func:`required_outputs` names and nothing an unrelated step
    writes. On evaluate that is the whole evaluator directory rather than the
    run-keyed one: a judge writes per-candidate directories beside its own
    run-keyed files, and the two sit at different depths under it.
    """
    events = CasePaths(data_root, court, docket).event(event)
    if role is FinalizeRole.predict:
        return events.prediction_dir(actor, run_id)
    if role is FinalizeRole.evaluate:
        return events.evaluator_dir(actor)
    raise ValueError(f"cell_output_root is for predict/evaluate, not {role.value}")


def blinded_candidates(*, data_root: Path, court: str, docket: int) -> list[str]:
    """The aliases staged for an evaluate cell to grade, as the agent sees them.

    Read from the staging directory rather than from the alias map, and for the
    reason the map lives outside the tree at all: the cell is told to enumerate
    ``record/blinded/`` and grade what it finds there, so the set the sentinel
    waits for is exactly the set the agent was asked to produce. Reading the map
    instead would make the sentinel disagree with the contract whenever staging
    dropped a candidate.
    """
    staged = CasePaths(data_root, court, docket).blinded_predictions
    if not staged.is_dir():
        return []
    return sorted(entry.name for entry in staged.iterdir() if entry.is_dir())


def required_outputs(
    role: FinalizeRole,
    *,
    data_root: Path,
    court: str,
    docket: int,
    event: str,
    actor: str,
    run_id: str,
    candidates: Sequence[str] = (),
) -> list[Path]:
    """Every file a finished cell of this role owes, whether or not it exists yet.

    The set is the prompt contract's, resolved through :mod:`fedcourtsai.paths` so
    no caller spells a filename:

    * **predict** — ``prediction.json`` (the artifact ``agent_produced_output``
      probes), the two prose documents it points at, and the per-run
      ``retrieval.md`` / ``tooling.json`` the contract asks for every run.
    * **evaluate** — one ``evaluation.json`` + ``evaluation.md`` per staged
      candidate (the per-candidate depth ``agent_produced_output`` globs), plus
      the judge-level ``retrieval.md`` / ``tooling.json`` keyed by evaluator and
      run. Candidates are named under their staging **aliases**, because the
      un-aliasing runs in the cell's tail and the sentinel runs while the agent
      still holds the tree.

    ``flags.json`` is deliberately absent from both: it is written only when a
    cell has something to flag, so requiring it would leave the sentinel unable
    to fire on the ordinary cell. So are ``usage.json`` and ``retrieval_log.json``
    — the harness writes those after the agent is done, which is after the step
    this sentinel exists to conclude.

    An evaluate role with no ``candidates`` raises rather than returning the
    judge-level pair alone. That set is two files a judge can write before it has
    graded anything, so returning it would have this function say "finished" of a
    cell that has done none of its work — the exact inversion the sentinel exists
    to avoid, and one a caller reaches by forgetting an argument.
    """
    events: EventPaths = CasePaths(data_root, court, docket).event(event)
    if role is FinalizeRole.predict:
        return [
            events.prediction(actor, run_id),
            events.reasoning(actor, run_id),
            events.predicted_reasoning(actor, run_id),
            events.prediction_retrieval(actor, run_id),
            events.prediction_tooling(actor, run_id),
        ]
    if role is FinalizeRole.evaluate:
        if not candidates:
            raise ValueError("an evaluate cell's completion set needs its staged candidates")
        paths = [
            events.evaluation_retrieval(actor, run_id),
            events.evaluation_tooling(actor, run_id),
        ]
        for candidate in candidates:
            paths.append(events.evaluation(actor, candidate, run_id))
            paths.append(events.evaluation_notes(actor, candidate, run_id))
        return paths
    raise ValueError(f"required_outputs is for predict/evaluate, not {role.value}")
