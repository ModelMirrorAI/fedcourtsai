"""Workflow finalize decisions: branch name, draft-vs-ready, PR title and body.

After a ``run-predict`` / ``run-evaluate`` / ``run-reconcile`` cell's agent writes
its files, the workflow hands the result to git: it names a branch, decides whether
the output is a ready PR or a draft a maintainer must finish, and writes the commit
message plus the PR title and body. That logic used to be inline workflow bash —
untestable, and the home of two production bugs (a branch name that omitted the
case and so collided when two cells fired in the same second, and the fiddly
push-auth dance). It lives here as small pure functions the ``finalize-branch`` /
``finalize-pr`` CLI commands wrap, so the YAML only runs git while every routing
decision is unit-tested.

The decision core is the same across the three workflows: a cell that wrote nothing
is *skipped*; a clean cell whose output fails schema validation is a hard *failure*;
otherwise a PR opens, as a *draft* when the agent did not finish (a turn/time limit)
or when a partial write left invalid output, and ready only when the agent finished
and the output validates. The per-role specifics — the branch shape, the commit
subject, and the PR prose — differ and are spelled out per builder.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from .paths import CasePaths

# The partial-output draft warning, appended to a draft PR's body so a maintainer
# knows the cell did not finish. Reconcile adds "before merging" because its merge
# is what fires the evaluate handoff.
_PARTIAL_PREDICT = (
    "⚠️ The agent did not finish (turn/time limit); this is partial output for a "
    "maintainer to review and complete."
)
_PARTIAL_RECONCILE = (
    "⚠️ The agent did not finish (turn/time limit); this is partial output for a "
    "maintainer to review and complete before merging."
)


class FinalizeRole(StrEnum):
    """Which workflow is finalizing; selects the branch/commit/PR shape."""

    predict = "predict"
    evaluate = "evaluate"
    reconcile = "reconcile"


# The judgment noun each predict/evaluate role writes, for human-facing text.
_JUDGMENT_NOUN = {FinalizeRole.predict: "prediction", FinalizeRole.evaluate: "evaluation"}

FinalizeAction = Literal["skip", "fail", "open"]


@dataclass(frozen=True)
class FinalizePlan:
    """The finalize decision for one cell, ready for the workflow to act on.

    ``action`` routes the workflow: ``skip`` (warn and stop — the cell wrote
    nothing), ``fail`` (error and exit non-zero — a clean run's output is invalid),
    or ``open`` (commit and open the PR). On ``skip``/``fail`` only ``message``
    carries the ``::warning::``/``::error::`` text; on ``open`` the ``draft`` flag
    plus ``commit_message`` / ``title`` / ``body`` carry the PR.
    """

    action: FinalizeAction
    draft: bool = False
    message: str = ""
    commit_message: str = ""
    title: str = ""
    body: str = ""


def branch_name(
    role: FinalizeRole,
    court: str,
    docket: int,
    run_id: str,
    *,
    event: str | None = None,
    actor: str | None = None,
) -> str:
    """The unique branch a cell's PR is pushed to.

    ``run_id`` is only second-granular and is shared by every matrix child of a
    plan job, so the case (``court``/``docket``) — and, for predict/evaluate, the
    event and actor — must ride in the branch or two concurrent cells collide on
    one ref and the loser is rejected. Reconcile fans out per case (it settles all
    of a case's events together), so its branch carries no event/actor.
    """
    if role is FinalizeRole.reconcile:
        return f"reconcile/{court}-{docket}-{run_id}"
    if event is None or actor is None:
        raise ValueError(f"{role.value} branch needs both event and actor")
    return f"{role.value}/{court}-{docket}-{event}-{actor}-{run_id}"


def _open_or_validation_failure(agent_ok: bool, validated: bool) -> tuple[FinalizeAction, bool]:
    """Route a cell that produced output, by whether it finished and validated.

    A clean run (``agent_ok``) must produce schema-valid output — invalid output
    is a hard failure that keeps the ledger honest. A run that hit a limit may have
    written a partial file; keep it for review as a draft rather than discarding the
    work. A finished, valid run is the only ready PR.
    """
    if not validated:
        return ("fail", False) if agent_ok else ("open", True)
    return ("open", not agent_ok)


def _partial_suffix(agent_ok: bool) -> str:
    return "" if agent_ok else " before the run hit its turn/time limit"


def _draft_body(body: str, draft: bool, warning: str) -> str:
    return f"{body}\n\n{warning}" if draft else body


def finalize_judgment(  # noqa: PLR0913 - inputs map 1:1 to the finalize state the workflow holds
    role: FinalizeRole,
    *,
    court: str,
    docket: int,
    event: str,
    actor: str,
    run_id: str,
    changed: bool,
    agent_ok: bool,
    validated: bool,
) -> FinalizePlan:
    """Finalize a predict or evaluate cell (one actor x one event).

    ``changed`` is whether the agent left any staged change; ``agent_ok`` whether
    its engine step finished cleanly; ``validated`` whether ``validate data``
    accepted the output (only meaningful when ``changed``).
    """
    if role not in (FinalizeRole.predict, FinalizeRole.evaluate):
        raise ValueError(f"finalize_judgment is for predict/evaluate, not {role.value}")
    noun = _JUDGMENT_NOUN[role]
    if not changed:
        return FinalizePlan(
            action="skip",
            message=f"{actor} produced no changes for {event}{_partial_suffix(agent_ok)}; "
            "skipping PR.",
        )
    action, draft = _open_or_validation_failure(agent_ok, validated)
    if action == "fail":
        return FinalizePlan(action="fail", message=f"{noun} for {event} failed schema validation")
    body = f"Automated {noun} by `{actor}` (run `{run_id}`) for event `{event}`."
    return FinalizePlan(
        action="open",
        draft=draft,
        commit_message=f"{role.value}({actor}): {court}/{docket} {event}",
        title=f"{role.value}({actor}): {court}/{docket} — {event}",
        body=_draft_body(body, draft, _PARTIAL_PREDICT),
    )


def finalize_reconcile(
    *,
    court: str,
    docket: int,
    run_id: str,
    settled: tuple[str, ...],
    agent_ok: bool,
    validated: bool,
    issue: int,
) -> FinalizePlan:
    """Finalize a reconcile cell (one case, the events the agent settled).

    ``settled`` is the event ids whose ``outcome.json`` the run added; an empty
    tuple means nothing was settled. ``issue`` is the triggering reconcile issue,
    closed by the PR.
    """
    if not settled:
        return FinalizePlan(
            action="skip",
            message=f"no outcome recorded for {court}/{docket}{_partial_suffix(agent_ok)}; "
            "nothing to reconcile.",
        )
    action, draft = _open_or_validation_failure(agent_ok, validated)
    if action == "fail":
        return FinalizePlan(
            action="fail",
            message=f"reconciled outcomes for {court}/{docket} failed schema validation",
        )
    events = ",".join(settled)
    body = (
        f"Reconciled ground truth for `{court}/{docket}` ({events}).\n\n"
        "When this merges, `run-reconcile` opens a `run:evaluate` issue for the "
        "settled events.\n\n"
        f"Closes #{issue}"
    )
    return FinalizePlan(
        action="open",
        draft=draft,
        commit_message=f"reconcile: {court}/{docket} — {events}",
        title=f"reconcile: {court}/{docket}",
        body=_draft_body(body, draft, _PARTIAL_RECONCILE),
    )


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
    ``evaluation.json`` for this evaluator and run (evaluate) — so the finalize step
    can skip opening a PR that carries no judgment, only the event scaffold. Reconcile
    has its own settled-events check and is not handled here.
    """
    events = CasePaths(data_root, court, docket).event(event)
    if role is FinalizeRole.predict:
        return events.prediction(actor, run_id).is_file()
    if role is FinalizeRole.evaluate:
        evaluator_root = events.base / "evaluations" / actor
        return any(evaluator_root.glob(f"*/{run_id}/evaluation.json"))
    raise ValueError(f"agent_produced_output is for predict/evaluate, not {role.value}")
