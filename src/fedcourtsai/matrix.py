"""Builds the GitHub Actions ``strategy.matrix`` for the agent fan-out.

``run-predict`` runs every enabled predictor against every open event; this is
the cartesian product the matrix needs. ``run-evaluate`` runs every enabled
evaluator against every resolved event **that holds a committed prediction**
(each evaluator scores all predictors for that event internally, so predictors
are not part of the matrix dimension; a predictionless event mints no cells).
``run-reconcile`` runs a single agent against each case ``run-pull`` flagged as
decided-but-not-machine-readable, so it fans out **per case** (not per event):
the agent must weigh all of a case's open events together to attribute the
case-level disposition, so they are kept in one cell.

A single trigger can carry **many** cases: the issue body holds either one
``{court, docket, events}`` object or a JSON array of them. ``parse_cases``
normalizes both forms into ``CaseRequest`` entries, and the matrix is the product
of the registry x every requested case x that case's events. The
``strategy.max-parallel`` cap in the workflow then throttles the whole fan-out,
and resolved events are still skipped because the caller resolves each case's
default event list (open events for predict, resolved events for evaluate).

Keeping this in the library (rather than inline YAML/JS) makes the routing
testable and keeps the registry the single source of truth for which agents
exist — the same place the future hypothesis-generation harness will add new
predictors.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import CasePaths
from .pricing import DEFAULT_MODELS
from .registry import enabled_evaluators, enabled_predictors

_JSON_BLOCK = re.compile(r"```json\s*(.+?)\s*```", re.S)

# The single reconcile agent and its prompt. Reconcile has no registry — there is
# one agent that confirms ground truth from the docket — so engine and prompt are
# fixed here rather than read from a config file.
_RECONCILE_ENGINE = "claude-code"
_RECONCILE_PROMPT = ".github/prompts/reconcile.md"


@dataclass(frozen=True)
class CaseRequest:
    """One case to fan out over: a court/docket and the events to target.

    ``events`` may be empty, meaning "resolve the case's default events" — open
    events for predict, resolved events for evaluate. The CLI does that
    data-directory lookup; the matrix builders take fully-resolved entries.
    """

    court: str
    docket: int
    events: tuple[str, ...] = ()


def parse_cases(issue_body: str) -> list[CaseRequest]:
    """Parse the ```json fenced block of an issue body into case requests.

    Accepts either a single ``{court, docket, events}`` object (single-case,
    back-compat) or a JSON array of such objects (batch). ``events`` is optional
    per entry; an absent or empty list means "resolve this case's default
    events". Raises ``ValueError`` if no block is present or an entry is missing
    ``court``/``docket``.
    """
    match = _JSON_BLOCK.search(issue_body)
    if not match:
        raise ValueError("No ```json {court,docket,events} block found in the issue body.")
    data = json.loads(match.group(1))
    entries = data if isinstance(data, list) else [data]
    cases: list[CaseRequest] = []
    for entry in entries:
        if not isinstance(entry, dict) or "court" not in entry or "docket" not in entry:
            raise ValueError(f"Each case needs 'court' and 'docket'; got {entry!r}.")
        cases.append(
            CaseRequest(
                court=str(entry["court"]),
                docket=int(entry["docket"]),
                events=tuple(entry.get("events") or ()),
            )
        )
    return cases


def predict_matrix(
    predictors_path: Path,
    cases: list[CaseRequest],
    run_id: str,
) -> dict[str, list[dict[str, Any]]]:
    include: list[dict[str, Any]] = []
    for predictor in enabled_predictors(predictors_path):
        for case in cases:
            for event_id in case.events:
                include.append(
                    {
                        "predictor_id": predictor.id,
                        "engine": predictor.engine,
                        # Resolved, never empty: the registry override wins, else the
                        # engine's predict/evaluate default. The workflow passes this
                        # to the engine step, so the recorded model is what ran.
                        "model": predictor.model or DEFAULT_MODELS[predictor.engine],
                        "prompt": predictor.prompt,
                        "court": case.court,
                        "docket": case.docket,
                        "event_id": event_id,
                        "run_id": run_id,
                    }
                )
    return {"include": include}


def event_has_predictions(data_root: Path, court: str, docket: int, event_id: str) -> bool:
    """Whether the git ledger holds at least one prediction for this event.

    The evaluate cost gate: an evaluator cell scores predictions against the
    outcome, so an event with none — typical for a petition the pipeline
    resolved without ever predicting (a frontier catch-up, a rotation sweep of
    a decided historical case) — has nothing for an agent to do, and every
    cell minted for it is pure model spend. Predictions are committed files,
    so the check is offline and exact at plan time.
    """
    predictions_root = CasePaths(data_root, court, docket).event(event_id).predictions_dir
    return any(predictions_root.glob("*/*/prediction.json"))


def evaluate_matrix(
    evaluators_path: Path,
    cases: list[CaseRequest],
    run_id: str,
    data_root: Path | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Build the evaluator x case x event matrix, dropping predictionless events.

    With ``data_root``, an event with no committed prediction is dropped before
    any agent cell is minted (:func:`event_has_predictions`) — the plan job's
    deterministic cost gate. ``None`` skips the gate (callers that assemble
    their own ledger).
    """
    include: list[dict[str, Any]] = []
    for evaluator in enabled_evaluators(evaluators_path):
        for case in cases:
            for event_id in case.events:
                if data_root is not None and not event_has_predictions(
                    data_root, case.court, case.docket, event_id
                ):
                    continue
                include.append(
                    {
                        "evaluator_id": evaluator.id,
                        "engine": evaluator.engine,
                        # Resolved, never empty — see predict_matrix.
                        "model": evaluator.model or DEFAULT_MODELS[evaluator.engine],
                        "prompt": evaluator.prompt,
                        "court": case.court,
                        "docket": case.docket,
                        "event_id": event_id,
                        "run_id": run_id,
                    }
                )
    return {"include": include}


def reconcile_matrix(
    cases: list[CaseRequest],
    run_id: str,
) -> dict[str, list[dict[str, Any]]]:
    """Build the per-case ``run-reconcile`` matrix.

    One cell per case (not per event): the reconcile agent confirms the docket's
    disposition and attributes it across the case's open events together, so every
    open event id rides in a single space-joined ``events`` field. A case with no
    open events contributes nothing (there is nothing to reconcile). Mirrors the
    shape the workflow consumes — ``court`` / ``docket`` / ``events`` plus the
    fixed reconcile ``engine`` / ``prompt`` and the shared ``run_id``.
    """
    include: list[dict[str, Any]] = []
    for case in cases:
        if not case.events:
            continue
        include.append(
            {
                "engine": _RECONCILE_ENGINE,
                "prompt": _RECONCILE_PROMPT,
                "court": case.court,
                "docket": case.docket,
                "events": " ".join(case.events),
                "run_id": run_id,
            }
        )
    return {"include": include}
