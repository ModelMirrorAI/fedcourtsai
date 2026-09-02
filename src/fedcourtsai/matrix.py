"""Builds the GitHub Actions ``strategy.matrix`` for the agent fan-out.

``run-predict`` runs every enabled predictor against every open event; this is
the cartesian product the matrix needs. ``run-evaluate`` runs every enabled
evaluator against every resolved event **that holds a committed prediction and
that the evaluator has not already graded** (each evaluator scores all predictors
for that event internally, so predictors are not part of the matrix dimension; a
predictionless event mints no cells, and neither does an already-graded one —
that second gate is what keeps a re-queue from spending tokens on gradings the
ledger already holds).

A named case list can carry **many** cases: the body holds either one
``{court, docket, events}`` object or a JSON array of them. ``parse_cases``
normalizes both forms into ``CaseRequest`` entries, and the matrix is the product
of the registry x every requested case x that case's events (narrowed per case
by an optional ``predictors`` filter — the engine-backfill path). The
``strategy.max-parallel`` cap in the workflow then throttles the whole fan-out,
and resolved events are still skipped because the caller resolves each case's
default event list (open case-baseline events for predict, resolved events for
evaluate).

Keeping this in the library (rather than inline YAML/JS) makes the routing
testable and keeps the registry the single source of truth for which agents
exist — the same place the future hypothesis-generation harness will add new
predictors.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .collect import parse_cell_artifact_name
from .finalize import FinalizeRole
from .ids import case_id, parse_run_id
from .paths import CasePaths
from .pricing import DEFAULT_MODELS
from .registry import enabled_evaluators, enabled_predictors

_JSON_BLOCK = re.compile(r"```json\s*(.+?)\s*```", re.S)


@dataclass(frozen=True)
class CaseRequest:
    """One case to fan out over: a court/docket and the events to target.

    ``events`` may be empty, meaning "resolve the case's default events" — open
    case-baseline events for predict, resolved events for evaluate. The CLI does that
    data-directory lookup; the matrix builders take fully-resolved entries.

    ``predictors`` narrows the predict fan-out to the named registry ids —
    the backfill path when one engine's cells failed (quota, outage) while the
    others delivered: it keeps a backfill body targeted at just the affected
    engines. The ledger-based per-predictor already-predicted skip in
    :func:`predict_matrix` (its ``data_root`` gate) independently drops any
    healthy engine that already landed, so this filter is the explicit form of
    the same intent, not the thing that prevents a double-commit. Empty means
    every enabled predictor; evaluate ignores it (an evaluator scores every
    committed prediction for its event).
    """

    court: str
    docket: int
    events: tuple[str, ...] = ()
    predictors: tuple[str, ...] = ()


def parse_cases(body: str) -> list[CaseRequest]:
    """Parse the ```json fenced block of a case-list body into case requests.

    Accepts either a single ``{court, docket, events}`` object (single-case,
    back-compat) or a JSON array of such objects (batch). ``events`` is optional
    per entry; an absent or empty list means "resolve this case's default
    events". ``predictors`` is optional per entry and narrows the predict
    fan-out to the named registry ids (see :class:`CaseRequest`). Raises
    ``ValueError`` if no block is present or an entry is missing
    ``court``/``docket``.
    """
    match = _JSON_BLOCK.search(body)
    if not match:
        raise ValueError("No ```json {court,docket,events} block found in the body.")
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
    data_root: Path | None = None,
    *,
    skip_predicted: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    """Build the predictor x case x event matrix, dropping cells already predicted.

    With ``data_root`` a deterministic per-predictor gate runs before any agent
    cell is minted, so it costs no model spend: a ``(predictor, event)`` cell
    whose predictor already committed a prediction for that event is skipped
    (:func:`event_has_predictions` with ``predictor_id``). This is the predict
    mirror of :func:`evaluate_matrix`'s already-evaluated gate — what makes a
    *sequential* re-queue idempotent at the cell grain: a run where two of three
    engines landed and one quota-failed re-mints only the missing engine, rather
    than the whole registry re-committing the healthy engines' predictions. It is
    a plan-time read of the checked-out ledger, not a lock — two runs planned
    before either's PR merges both see an unpredicted event and both mint.

    ``data_root=None`` skips the gate entirely (offline callers, and back-compat
    with a caller that assembles its own ledger). ``skip_predicted=False`` keeps
    the gate off for a deliberate re-predict — a prompt change where the point
    *is* to predict an already-predicted event again — so that never requires
    deleting committed artifacts to get a cell minted. The explicit
    ``CaseRequest.predictors`` narrowing is orthogonal: it names *which* engines a
    backfill body targets, while this gate independently drops any of them that
    already landed.
    """
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
                if (
                    data_root is not None
                    and skip_predicted
                    and event_has_predictions(
                        data_root, case.court, case.docket, event_id, predictor_id=predictor.id
                    )
                ):
                    continue
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

    * **Whole cases, never a split.** predict now *has* a per-predictor
      already-predicted skip (:func:`predict_matrix`'s ``data_root`` gate over
      :func:`event_has_predictions`), so a half-admitted case whose remaining
      engines re-queued next cycle would re-mint only the missing engines — not
      re-commit the ones that landed. Admitting cases whole is therefore a
      determinism / simplicity choice now, not a double-commit necessity: it
      keeps a deferred case a single clean re-queue unit rather than tracking
      partial admission per engine.
    * **Deterministic and salience-independent.** The trigger body carries only
      ``{court, docket, events}`` — no salience score, and its order is the live
      cycle's processing order, not a priority ranking. Ascending ``case_id`` is
      a stable order that yields the same kept subset for the same input however
      (or whether) selection ordered it — the point of a backstop that must hold
      when selection is exactly what failed. When a salience score reaches the
      trigger body it can key this order instead. ``case_id`` is
      ``court/docket`` and the sort is **lexical over that string** (docket is
      not zero-padded), so it is numeric-ascending only within a uniform docket
      digit width — fine and deterministic for one Term's SCOTUS dockets, but a
      future mixed-width caller must not read it as numeric order.

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


_CellKey = tuple[str, str, int, str]


def _cell_key(predictor_id: str, court: str, docket: int, event_id: str) -> _CellKey:
    """The one spelling of the guard's match key.

    Both sides of the match — the census's stranded cells and the matrix's
    entries — build it here. Spelled twice, the two would type-check while
    transposed, and a transposed key silently disarms the guard rather than
    failing anything.
    """
    return (predictor_id, court, docket, event_id)


@dataclass(frozen=True)
class StrandedCell:
    """One predict cell whose output sits in a run that was never collected.

    ``run_db_id`` is the GitHub run's database id — the handle
    ``gh run rerun <id> --failed`` takes, and the one the recovery note names.
    The cell's *pipeline* run id (the plan-time UTC stamp) is deliberately
    absent: the cell artifact name does not encode it
    (:func:`fedcourtsai.collect.cell_artifact_name`) and the runs API does not
    know it, so naming one would mean inventing it.
    """

    run_db_id: int
    predictor_id: str
    court: str
    docket: int
    event_id: str

    @property
    def key(self) -> _CellKey:
        """The (predictor, case, event) grain the matrix is deduped at."""
        return _cell_key(self.predictor_id, self.court, self.docket, self.event_id)


@dataclass(frozen=True)
class StrandedCensus:
    """The parsed stranded-artifact census, plus the records it could not read.

    ``unparsed`` holds each unreadable record — a malformed one, or a name that
    does not split into (predictor, court, docket, event) — and is never
    silently discarded: the caller reports them and moves on, because a guessed
    reading would withhold the wrong cell, a worse failure than the re-spend the
    guard exists to prevent.
    """

    cells: tuple[StrandedCell, ...]
    unparsed: tuple[str, ...]


@dataclass(frozen=True)
class GuardedMatrix:
    """A predict matrix after the stranded-run guard, and what it withheld.

    ``withheld`` names the stranded cell behind each drop (its run included),
    so every withheld cell can be reported with its own recovery command.
    Empty when the census was empty or nothing matched, in which case
    ``include`` is the input list unchanged.
    """

    include: list[dict[str, Any]]
    withheld: tuple[StrandedCell, ...]


def read_stranded_census(path: Path) -> StrandedCensus:
    """Read the census of cell artifacts left behind by uncollected runs.

    The file is a JSON list of ``{"run_db_id": <int>, "artifact_name": <str>}``
    records, written by the plan job's census step from the runs and artifacts
    APIs. An absent or empty file is an empty census — the guard is simply off,
    which is what a degraded census step writes.

    Raises ``ValueError`` if the file is not a JSON list, leaving the caller to
    decide the direction: the CLI fails **open** there, because this guard
    prevents an expensive failure, not a dangerous one, and must never be the
    reason a legitimate run does not start.
    """
    if not path.exists():
        return StrandedCensus((), ())
    raw = path.read_text().strip()
    if not raw:
        return StrandedCensus((), ())
    records = json.loads(raw)
    if not isinstance(records, list):
        raise ValueError(f"{path}: expected a JSON list of census records, got {type(records)}.")
    cells: list[StrandedCell] = []
    unparsed: list[str] = []
    for record in records:
        name = record.get("artifact_name") if isinstance(record, dict) else None
        if not isinstance(name, str):
            unparsed.append(repr(record))
            continue
        parsed = parse_cell_artifact_name(FinalizeRole.predict, name)
        if parsed is None:
            unparsed.append(name)
            continue
        try:
            run_db_id = int(record["run_db_id"])
        except (KeyError, TypeError, ValueError):
            unparsed.append(name)
            continue
        cells.append(
            StrandedCell(
                run_db_id=run_db_id,
                predictor_id=parsed.actor,
                court=parsed.court,
                docket=parsed.docket,
                event_id=parsed.event_id,
            )
        )
    return StrandedCensus(tuple(cells), tuple(unparsed))


def drop_stranded_cells(
    matrix: dict[str, list[dict[str, Any]]], stranded: Sequence[StrandedCell]
) -> GuardedMatrix:
    """Withhold cells whose output already sits in an uncollected run.

    A predict cell spends its tokens *before* the run's single durability step,
    so a `collect` that fails after a full-width fan-out leaves every cell's
    output in an artifact and nothing in the ledger — and the ledger is what the
    already-predicted gate in :func:`predict_matrix` reads. The next live cycle
    therefore re-derives the same unpredicted events and re-spends the whole
    run. This guard closes that loop at the one place the spend can still be
    withheld: the plan.

    The grain is (predictor, case, event), matching the artifact name, so a cell
    the stranded run left no artifact for still runs — an engine whose cells
    died before upload while the others delivered is re-minted exactly as it is
    today.

    Two properties are deliberate:

    * **Existence, not success.** A cell uploads its artifact whether or not it
      produced a prediction, and the guard keys on the artifact alone. A cell
      that spent tokens and produced nothing is therefore withheld too, because
      collecting the run is how anyone learns which of the two it was; once
      collect lands, an event with no committed prediction re-queues normally.
    * **Uncollected runs only.** A run whose `collect` succeeded is not in the
      census, so an unmerged-but-collected run is outside this guard — that
      window is still the plan-time-read race :func:`predict_matrix` documents.
    """
    if not stranded:
        return GuardedMatrix(matrix["include"], ())
    # First wins, because the census is written newest run first: when one cell
    # is stranded in two uncollected runs, the note should name the newer, which
    # is the better recovery target (either recovers the cell).
    by_key: dict[_CellKey, StrandedCell] = {}
    for stranded_cell in stranded:
        by_key.setdefault(stranded_cell.key, stranded_cell)
    include: list[dict[str, Any]] = []
    withheld: list[StrandedCell] = []
    for cell in matrix["include"]:
        key = _cell_key(
            str(cell["predictor_id"]),
            str(cell["court"]),
            int(cell["docket"]),
            str(cell["event_id"]),
        )
        match = by_key.get(key)
        if match is None:
            include.append(cell)
        else:
            withheld.append(match)
    return GuardedMatrix(include, tuple(withheld))


def event_has_predictions(
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    *,
    predictor_id: str | None = None,
) -> bool:
    """Whether the git ledger holds a prediction for this event.

    The evaluate cost gate: an evaluator cell scores predictions against the
    outcome, so an event with none — typical for a petition the pipeline
    resolved without ever predicting (a frontier catch-up, a rotation sweep of
    a decided historical case) — has nothing for an agent to do, and every
    cell minted for it is pure model spend. Predictions are committed files,
    so the check is offline and exact at plan time.

    With ``predictor_id`` it asks about one engine, the mirror of
    :func:`event_has_evaluations`'s ``evaluator_id`` — the actionable grain for
    the predict re-queue: a predict run where two of three engines landed and one
    quota-failed should re-mint only the third. Committed predictions live at
    ``predictions/<predictor>/<run>/prediction.json``, so the glob is
    depth-anchored by that filename and cannot match the shallower per-run
    siblings (``predictions/<predictor>/<run>/usage.json`` and friends), the same
    shape :func:`event_has_evaluations` relies on. ``None`` (the default) keeps
    the original any-predictor semantics for existing callers.
    """
    predictions_root = CasePaths(data_root, court, docket).event(event_id).predictions_dir
    return any(predictions_root.glob(f"{predictor_id or '*'}/*/prediction.json"))


def predicted_case_ids(data_root: Path) -> frozenset[str]:
    """Every case id the git ledger holds at least one committed prediction for.

    The **candidate-admission** read for the live predict sweep's
    cohort-completion carve-out: a salience-deferred case whose event already
    carries a partial predictor cohort is admitted back into the sweep so the
    missing engines can be minted. Answering that at the case grain is what
    makes it one glob for the whole ledger rather than a per-row probe of every
    SCOTUS case in the corpus.

    Membership says only that a cohort exists *somewhere* on the case — never
    that any particular cell is owed, and never that a specific event may be
    queued. The sweep re-checks both: the per-``(predictor, event)`` owed test
    decides what is missing, and
    :func:`fedcourtsai.store.event_has_claimable_prediction` narrows a
    carve-out case to the events whose cohort a board would count. Membership
    here is deliberately the weaker, cheaper question — one glob against a
    per-row probe of every SCOTUS case in the corpus — so it must never be read
    as the bound.

    Committed predictions live at
    ``cases/<court>/<docket>/events/<event>/predictions/<predictor>/<run>/prediction.json``,
    so the glob is depth-anchored by that filename exactly as
    :func:`event_has_predictions` is, and cannot match the shallower per-run
    siblings (``usage.json`` and friends). An absent ``data_root`` — a fresh
    checkout, an offline caller — yields the empty set, which admits nothing.
    """
    cases_root = data_root / "cases"
    return frozenset(
        # `<court>/<docket>/events/<event>/predictions/<predictor>/<run>/prediction.json`
        # counted back from the file: parents[5] is the docket, parents[6] the court.
        case_id(path.parents[6].name, int(path.parents[5].name))
        for path in cases_root.glob("*/*/events/*/predictions/*/*/prediction.json")
    )


def last_predicted_dates(data_root: Path) -> dict[str, date]:
    """Per case, the UTC date of the newest run that committed a prediction for it.

    The **ledger's own answer to "when was this case last minted for
    prediction"**, for the callers that cannot get it from
    ``predict_queued_at``. That column is a corpus write, so only the writer
    jobs set it; a case minted by a schedule-driven backlog derivation carries
    no stamp however many predictions it lands, and anything keyed on the stamp
    alone reads such a case as never predicted. The committed run directory is
    the fact that survives both lanes: it exists exactly when a prediction was
    landed, whoever derived the cell.

    The date comes from the run-id directory name, which is a UTC timestamp
    (:func:`fedcourtsai.ids.run_id`), so a run whose id is not in that form is
    skipped rather than crashing the read — an unparseable directory is a
    stray, and a caller comparing dates must not be taken down by one.

    Same glob and same anchoring as :func:`predicted_case_ids`, one ledger walk
    for the whole tree, so a caller wanting both the membership and the date
    should take this and read its keys. An absent ``data_root`` yields an empty
    mapping, which dates nothing. A malformed *docket* segment is still fatal
    in both functions, deliberately: that layout is written only through
    :class:`~fedcourtsai.paths.CasePaths`, so a non-numeric docket directory is
    a corrupted ledger rather than a stray, and the two must fail together.
    """
    latest: dict[str, date] = {}
    cases_root = data_root / "cases"
    for path in cases_root.glob("*/*/events/*/predictions/*/*/prediction.json"):
        try:
            minted = parse_run_id(path.parents[0].name).date()
        except ValueError:
            continue
        case = case_id(path.parents[6].name, int(path.parents[5].name))
        current = latest.get(case)
        if current is None or minted > current:
            latest[case] = minted
    return latest


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

    Gating per predictor instead would re-mint the cell to pick up the late
    prediction, re-grading every prediction the judge already scored. That
    costs tokens rather than accuracy: the scoring surfaces count one grading
    per (case, event, predictor, evaluator), newest by harness clock
    (:func:`fedcourtsai.integrity.latest_evaluation_runs`), so a re-grade
    supersedes rather than double-counts. What the coarse grain buys is the
    spend, and what it costs is a coverage gap that falls *differentially* — an
    engine whose cells backfill late accumulates fewer scored events than one
    that ran on time. The leaderboard publishes the relative half of that gap
    (each entry's ``events_scored`` against its population's union, warned on
    at build time), leaving the absolute half — a prediction with no evaluation
    at all — to a ledger scan. So moving to the per-predictor grain is a
    decision about run cost, taken on its own.
    """
    root = CasePaths(data_root, court, docket).event(event_id).base / "evaluations"
    return any(root.glob(f"{evaluator_id or '*'}/*/*/evaluation.json"))


def cell_failure_count(
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    actor: str,
    seam: str,
) -> int:
    """How many committed failure facts this ``(actor, event, seam)`` cell holds.

    The activation of the per-cell attempt cap. The corpus-blind ``collect`` job
    writes one run-scoped ``attempt.json`` per failed cell
    (:class:`fedcourtsai.schemas.CellFailure`); this counts them at the seam's
    directory grain — ``predictions/<predictor>/*/attempt.json`` for predict,
    ``evaluations/<evaluator>/*/attempt.json`` for evaluate — the same shape the
    ``event_has_*`` gates use, one level shallower because the failure fact is keyed
    by (actor, run) rather than (actor, predictor, run). The count is the poison
    pill the derivers read against ``max_attempts``: a cell recorded failed that
    many times is no longer owed. Inherently idempotent — a run-scoped path means a
    rerun overwrites rather than accumulating, so counting committed facts can
    never double-count. ``seam`` is ``predict`` / ``evaluate``, matching the
    ledger subtree the facts live under.
    """
    event = CasePaths(data_root, court, docket).event(event_id)
    root = event.predictions_dir if seam == "predict" else event.base / "evaluations"
    return sum(1 for _ in root.glob(f"{actor}/*/attempt.json"))


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
      What it saves is model spend, not accuracy: the boards count one grading
      per (case, event, predictor, evaluator)
      (:func:`fedcourtsai.integrity.latest_evaluation_runs`), so a second
      grading supersedes rather than reweighting the standings. See
      :func:`event_has_evaluations` for the grain this gate works at, and the
      coverage gap that follows from it.

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
