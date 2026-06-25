"""Builds the GitHub Actions ``strategy.matrix`` for the agent fan-out.

``run-predict`` runs every enabled predictor against every open event; this is
the cartesian product the matrix needs. ``run-evaluate`` runs every enabled
evaluator against every resolved event (each evaluator scores all predictors for
that event internally, so predictors are not part of the matrix dimension).

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

from .registry import enabled_evaluators, enabled_predictors

_JSON_BLOCK = re.compile(r"```json\s*(.+?)\s*```", re.S)


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
                        "model": predictor.model or "",
                        "prompt": predictor.prompt,
                        "court": case.court,
                        "docket": case.docket,
                        "event_id": event_id,
                        "run_id": run_id,
                    }
                )
    return {"include": include}


def evaluate_matrix(
    evaluators_path: Path,
    cases: list[CaseRequest],
    run_id: str,
) -> dict[str, list[dict[str, Any]]]:
    include: list[dict[str, Any]] = []
    for evaluator in enabled_evaluators(evaluators_path):
        for case in cases:
            for event_id in case.events:
                include.append(
                    {
                        "evaluator_id": evaluator.id,
                        "engine": evaluator.engine,
                        "model": evaluator.model or "",
                        "prompt": evaluator.prompt,
                        "court": case.court,
                        "docket": case.docket,
                        "event_id": event_id,
                        "run_id": run_id,
                    }
                )
    return {"include": include}
