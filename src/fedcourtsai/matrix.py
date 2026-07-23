"""Builds the GitHub Actions ``strategy.matrix`` for the agent fan-out.

``run-predict`` runs every enabled predictor against every open event; this is
the cartesian product the matrix needs. ``run-evaluate`` runs every enabled
evaluator against every resolved event **that holds a committed prediction and
that the evaluator has not already graded** (each evaluator scores all predictors
for that event internally, so predictors are not part of the matrix dimension; a
predictionless event mints no cells, and neither does an already-graded one —
that second gate is what keeps a re-queue from double-counting).

A single trigger can carry **many** cases: the issue body holds either one
``{court, docket, events}`` object or a JSON array of them. ``parse_cases``
normalizes both forms into ``CaseRequest`` entries, and the matrix is the product
of the registry x every requested case x that case's events (narrowed per case
by an optional ``predictors`` filter — the engine-backfill path). The
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

from .ids import case_id
from .paths import CasePaths
from .pricing import DEFAULT_MODELS
from .registry import enabled_evaluators, enabled_predictors

_JSON_BLOCK = re.compile(r"```json\s*(.+?)\s*```", re.S)


@dataclass(frozen=True)
class CaseRequest:
    """One case to fan out over: a court/docket and the events to target.

    ``events`` may be empty, meaning "resolve the case's default events" — open
    events for predict, resolved events for evaluate. The CLI does that
    data-directory lookup; the matrix builders take fully-resolved entries.

    ``predictors`` narrows the predict fan-out to the named registry ids —
    the backfill path when one engine's cells failed (quota, outage) while the
    others delivered: re-running the full registry would duplicate the healthy
    engines' committed predictions, since predict has no already-predicted
    skip. Empty means every enabled predictor; evaluate ignores it (an
    evaluator scores every committed prediction for its event).
    """

    court: str
    docket: int
    events: tuple[str, ...] = ()
    predictors: tuple[str, ...] = ()


def parse_cases(issue_body: str) -> list[CaseRequest]:
    """Parse the ```json fenced block of an issue body into case requests.

    Accepts either a single ``{court, docket, events}`` object (single-case,
    back-compat) or a JSON array of such objects (batch). ``events`` is optional
    per entry; an absent or empty list means "resolve this case's default
    events". ``predictors`` is optional per entry and narrows the predict
    fan-out to the named registry ids (see :class:`CaseRequest`). Raises
    ``ValueError`` if no block is present or an entry is missing
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
                predictors=tuple(str(p) for p in entry.get("predictors") or ()),
            )
        )
    return cases


def predict_matrix(
    predictors_path: Path,
    cases: list[CaseRequest],
    run_id: str,
) -> dict[str, list[dict[str, Any]]]:
    predictors = enabled_predictors(predictors_path)
    enabled_ids = {p.id for p in predictors}
    for case in cases:
        # Fail loud: a typo'd or disabled id silently skipping cells would make
        # a backfill run look complete while delivering nothing for that engine.
        unknown = [pid for pid in case.predictors if pid not in enabled_ids]
        if unknown:
            raise ValueError(
                f"{case.court}/{case.docket}: predictors {unknown} are not enabled "
                f"registry ids (enabled: {sorted(enabled_ids)})."
            )
    include: list[dict[str, Any]] = []
    for predictor in predictors:
        for case in cases:
            if case.predictors and predictor.id not in case.predictors:
                continue
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


@dataclass(frozen=True)
class CappedMatrix:
    """A predict matrix after the salience-independent volume cap, and what it deferred.

    ``include`` is the kept fan-out (never more than the cap). ``dropped_cells``
    and ``dropped_cases`` name the overflow the cap held back — those cases stay
    in the corpus predict queue and re-queue on a later cycle, so the numbers
    report a **deferral, never a deletion**. Both are ``0`` / empty when the
    matrix fit under the cap and passed through unchanged.
    """

    include: list[dict[str, Any]]
    dropped_cells: int
    dropped_cases: tuple[str, ...]


def cap_predict_cells(matrix: dict[str, list[dict[str, Any]]], max_cells: int) -> CappedMatrix:
    """Hold the predict fan-out under ``max_cells`` by deferring whole overflow cases.

    The salience-INDEPENDENT volume backstop (see
    :class:`fedcourtsai.config.PredictConfig`). It runs on the fully-built,
    scope-filtered matrix, so it holds even when selection queued far more than a
    fundable run — the failure mode a past cost breach hit — bounding both
    GitHub's 256-job matrix ceiling (a wider matrix is rejected outright, losing
    the whole run) and the run's worst-case model spend. Cases are admitted
    **whole** (every predictor x event cell for a case, or none) in ascending
    ``case_id`` order, keeping the prefix that fits; the rest are deferred.

    Two properties drive the shape:

    * **Whole cases, never a split.** predict has no already-predicted skip (see
      :class:`CaseRequest`), so a half-admitted case whose remaining engines
      re-queued next cycle would re-commit the engines that already landed.
      Admitting cases whole keeps a deferred case cleanly re-queueable.
    * **Deterministic and salience-independent.** The trigger body carries only
      ``{court, docket, events}`` — no salience score, and its order is the live
      cycle's processing order, not a priority ranking. Ascending ``case_id`` is
      a stable order that yields the same kept subset for the same input however
      (or whether) selection ordered it — the point of a backstop that must hold
      when selection is exactly what failed. When a salience score reaches the
      trigger body it can key this order instead.

    Under the cap the matrix passes through unchanged (original cell order, no
    reordering). Over it, the kept cells keep their original order — only the
    deferred cases' cells are removed. A single case whose own cells exceed the
    whole cap is deferred like any other (it would overflow the matrix ceiling on
    its own); this is unreachable for cert petitions, which carry one or two open
    events, i.e. three or six cells.
    """
    include = matrix["include"]
    if len(include) <= max_cells:
        return CappedMatrix(include, 0, ())
    # Cells for one case are scattered across the predictor-major list, so first
    # tally each case's cell count, then admit whole cases in a stable order.
    per_case: dict[str, int] = {}
    for cell in include:
        cid = case_id(str(cell["court"]), int(cell["docket"]))
        per_case[cid] = per_case.get(cid, 0) + 1
    kept_cases: set[str] = set()
    running = 0
    for cid in sorted(per_case):
        # Prefix semantics: stop at the first case that would cross the cap
        # rather than skipping ahead to pack a smaller later one, so the kept set
        # is the ascending-case_id prefix that fits (with the uniform per-case
        # cell counts of a cert fan-out, prefix and best-pack coincide anyway).
        if running + per_case[cid] > max_cells:
            break
        running += per_case[cid]
        kept_cases.add(cid)
    kept = [
        cell for cell in include if case_id(str(cell["court"]), int(cell["docket"])) in kept_cases
    ]
    dropped_cases = tuple(cid for cid in sorted(per_case) if cid not in kept_cases)
    return CappedMatrix(kept, len(include) - len(kept), dropped_cases)


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


def event_has_evaluations(
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    *,
    evaluator_id: str | None = None,
) -> bool:
    """Whether the git ledger already holds an evaluation for this event.

    The idempotency gate, and the mirror of :func:`event_has_predictions`. With
    ``evaluator_id`` it asks about one judge, which is the actionable grain: an
    evaluate cell scores *every* predictor for its event in one run, so a run
    where two of three judges landed should re-mint only the third.

    Committed evaluations live at
    ``evaluations/<evaluator>/<predictor>/<run>/evaluation.json``. The glob is
    depth-anchored by that filename, so it cannot match the per-run siblings one
    level shallower (``evaluations/<evaluator>/<run>/usage.json`` and friends) —
    the same shape :func:`fedcourtsai.finalize.agent_produced_output` relies on.

    **Accepted limitation: this asks "has this judge graded this event", not
    "has it graded every prediction for this event".** The ledger is keyed by
    (evaluator, predictor, event) but a cell is only (evaluator, event) — the
    prompt has it score *every* predictor in one pass, with no partial mode. So
    a prediction that lands *after* a judge graded the event (the engine-backfill
    path in :class:`CaseRequest`) is never scored by that judge.

    Gating per predictor instead would be worse, not better: re-minting the cell
    to pick up the late prediction re-grades the ones already scored, and the
    leaderboard has no run dedup, so that double-counts. Between a visible
    coverage gap (a prediction with no evaluation, findable by a ledger scan) and
    a silent miscount (standings reweighted with no trace), the gap is the safer
    failure. The real fix is dedup at the leaderboard, which would make
    re-grading safe and let this gate move to the per-predictor grain.
    """
    root = CasePaths(data_root, court, docket).event(event_id).base / "evaluations"
    return any(root.glob(f"{evaluator_id or '*'}/*/*/evaluation.json"))


def evaluate_matrix(
    evaluators_path: Path,
    cases: list[CaseRequest],
    run_id: str,
    data_root: Path | None = None,
    *,
    skip_evaluated: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Build the evaluator x case x event matrix, dropping cells with nothing to do.

    With ``data_root``, two deterministic gates run before any agent cell is
    minted, so neither costs model spend:

    * **predictionless** — an event with no committed prediction has nothing to
      score (:func:`event_has_predictions`).
    * **already evaluated** — a judge that has already graded this event is not
      re-minted (:func:`event_has_evaluations`, per evaluator). This is what
      makes a *sequential* re-queue idempotent: a later run, or a manual
      single-issue recovery, mints only the missing judges. It is a plan-time
      read of the checked-out ledger, not a lock — two runs planned before
      either's PR merges both see an ungraded event and both mint, and
      ``gh run rerun --failed`` reuses the cached matrix without re-planning at
      all, so neither is protected by this.
      Without it a re-queue would double-count, because the leaderboard reads
      every committed ``evaluation.json`` into a per-(predictor, case, event)
      list with no run dedup — a second grading of the same cell silently
      reweights the standings. See :func:`event_has_evaluations` for the grain
      this gate works at, and the coverage gap that follows from it.

    ``data_root=None`` skips both (callers that assemble their own ledger).
    ``skip_evaluated=False`` keeps the second gate off for a deliberate
    re-grade — a prompt or rubric change, where the point *is* to score an
    already-graded event again — so that never requires deleting committed
    artifacts to get a cell minted.
    """
    include: list[dict[str, Any]] = []
    for evaluator in enabled_evaluators(evaluators_path):
        for case in cases:
            for event_id in case.events:
                if data_root is not None and not event_has_predictions(
                    data_root, case.court, case.docket, event_id
                ):
                    continue
                if (
                    data_root is not None
                    and skip_evaluated
                    and event_has_evaluations(
                        data_root,
                        case.court,
                        case.docket,
                        event_id,
                        evaluator_id=evaluator.id,
                    )
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
