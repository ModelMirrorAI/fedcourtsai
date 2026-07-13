"""End-to-end local cascade: provision → predict → evaluate → validate, offline.

The repeatable, local form of the Phase-0 "one full cascade proven" milestone:
one command drives a single case through the whole derived-artifact pipeline over
the *fixture* corpus (or a real one — ``dvc pull``-ed locally, or queried in place
on the DVC remote via the ranged corpus backend) without GitHub Actions. It is the
iteration loop that otherwise only exists inside ``run-predict`` / ``run-evaluate``.

It reuses the production seams rather than reimplementing them: the engine-runner
seam (:mod:`fedcourtsai.pipeline.runner`) produces each predict/evaluate cell at
the canonical paths, the predictor/evaluator registries pick the actors, and the
packed corpus supplies the snapshot, the event definitions, and the ground truth.
With the default offline ``stub`` engine the whole cascade is deterministic and
network-free; the ``claude-code`` / ``codex`` engines drive the same cells through
the real headless agents against the identical contract, so a green local run
faithfully predicts a green CI run.

The steps mirror what ``run-predict`` / ``run-evaluate`` do around the agent call:

1. **Provision** the case's latest corpus snapshot to its gitignored ``record/``
   path (as ``provision-snapshot`` does), and materialize each target event's git
   ``event.yaml`` definition plus, for a resolved event, the ground-truth
   ``outcome.json`` the evaluator scores against.
2. **Predict** the event with every enabled predictor.
3. **Evaluate** every resolved target's predictions with every enabled evaluator.
4. **Validate** the produced ledger (schema + git-only referential checks), the
   same gate CI runs on the resulting PR.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .. import corpus, ids
from ..paths import CasePaths
from ..registry import enabled_evaluators, enabled_predictors
from ..schemas import Outcome, PredictableEvent, UsageRole
from ..serialize import write_json, write_raw_json, write_yaml
from ..validate import run_ledger_referential_checks, validate_ledger
from .outcome import disposition_basis, granted_flag, is_machine_readable
from .runner import RunRequest, get_runner


class CascadeError(RuntimeError):
    """The cascade cannot run as requested (missing corpus, case, or event)."""


@dataclass(frozen=True)
class CascadeReport:
    """What one ``local-cascade`` run produced, for the CLI to render.

    Not a schema artifact — a transient summary of the cell files written and the
    final ledger verdict, so a maintainer (or a test) can see the cascade ran end
    to end and produced a valid ledger.
    """

    case_id: str
    engine: str
    run_id: str
    snapshot: Path | None
    events: tuple[str, ...]
    predictions: tuple[Path, ...]
    outcomes: tuple[Path, ...]
    evaluations: tuple[Path, ...]
    valid: bool
    problems: tuple[str, ...]


def _select_events(events: list[corpus.CorpusEvent], event: str | None) -> list[corpus.CorpusEvent]:
    """The case's events to run: the one named, or all of them by default."""
    if event is not None:
        chosen = [e for e in events if e.event_id == event]
        if not chosen:
            available = ", ".join(e.event_id for e in events) or "none"
            raise CascadeError(f"event {event!r} is not defined for this case (have: {available})")
        return chosen
    if not events:
        raise CascadeError("the case has no predictable events in the corpus")
    return events


def _outcome_for_resolved(
    row: corpus.CorpusRow,
    event_id: str,
    basis: Literal["standard", "mootness"] = "standard",
) -> Outcome | None:
    """Ground-truth :class:`Outcome` for an already-resolved event, or ``None``.

    ``pull``'s :func:`fedcourtsai.pipeline.outcome.detect_resolution` records an
    outcome for an event transitioning open→resolved; the cascade instead replays
    an event the corpus already marks resolved, so it builds the same outcome from
    the stored row without that open-event gate. Returns ``None`` when the
    disposition is not machine-readable or there is no decision date (the unrecorded
    path), matching detection's rule so a guess is never recorded.
    """
    if not (is_machine_readable(row.disposition) and row.date_decided is not None):
        return None
    assert row.disposition is not None  # narrowed by is_machine_readable above
    return Outcome(
        case_id=row.case_id,
        event_id=event_id,
        resolved_at=row.date_decided,
        actual_disposition=row.disposition,
        actual_granted=granted_flag(row.disposition),
        source=row.citations[0] if row.citations else None,
        disposition_basis=basis,
    )


def _event_definition(event: corpus.CorpusEvent) -> PredictableEvent:
    """The git ``event.yaml`` for a corpus event (the git-ledger analogue)."""
    return PredictableEvent(
        event_id=event.event_id,
        case_id=event.case_id,
        kind=event.kind,
        title=event.title or event.case_id,
        description=event.description,
        docket_entry_id=event.docket_entry_id,
        opened_at=event.opened_at,
        decision_target=event.decision_target,
        resolved=event.resolved,
    )


def run_cascade(
    *,
    corpus_db_path: Path,
    data_root: Path,
    config_root: Path,
    court: str,
    docket: int,
    event: str | None = None,
    engine: str = "stub",
    run_id: str,
) -> CascadeReport:
    """Run the full predict → evaluate → validate cascade for one case.

    Reads the case and its events from the packed corpus via the read-backend
    seam (:func:`fedcourtsai.corpus.connect_readonly`) — the local file by
    default, or the immutable blob in place on the DVC remote when the
    corpus-backend setting says ``ranged``, so a ranged-configured environment
    runs the cascade with no local pull. Provisions the snapshot and
    materializes the git event/outcome definitions the agents read, fans the
    selected engine out over the enabled predictors then evaluators, and
    validates the resulting ledger. Returns a :class:`CascadeReport`. Raises
    :class:`CascadeError` for a missing corpus/case/event and
    :class:`fedcourtsai.pipeline.runner.EngineUnavailable` /
    ``EngineFailed`` for a real-engine problem.
    """
    runner = get_runner(engine)
    case_id = ids.case_id(court, docket)
    case_paths = CasePaths(data_root, court, docket)

    backend = corpus.resolve_backend()
    if backend == "local" and not corpus_db_path.exists():
        raise CascadeError(
            f"no corpus at {corpus_db_path}; run `fedcourts make-fixture-corpus` first"
        )

    with corpus.connect_readonly(corpus_db_path, backend=backend) as conn:
        row = corpus.get_row(conn, case_id)
        if row is None:
            raise CascadeError(f"case {case_id} is not in the corpus at {corpus_db_path}")
        all_events = corpus.events_for_case(conn, case_id)
        found = corpus.latest_snapshot(conn, case_id)

    targets = _select_events(all_events, event)

    snapshot: Path | None = None
    # The provisioned snapshot also supplies the outcome's basis marker, so a
    # cascade over a resolved mootness case grades like the live channel would.
    basis: Literal["standard", "mootness"] = "standard"
    if found is not None:
        snapshot_date, payload = found
        snapshot = case_paths.snapshot(snapshot_date.isoformat())
        write_raw_json(snapshot, payload)
        basis = disposition_basis(payload)

    # Materialize the git event definitions, and the ground truth for any resolved
    # target, that the agents read — the workflow's provisioning step.
    outcomes: list[Path] = []
    for ev in targets:
        events = case_paths.event(ev.event_id)
        write_yaml(events.event_file, _event_definition(ev))
        if ev.resolved:
            outcome = _outcome_for_resolved(row, ev.event_id, basis)
            if outcome is not None:
                write_json(events.outcome, outcome)
                outcomes.append(events.outcome)

    def _request(role: UsageRole, actor: str, prompt: str, event_id: str) -> RunRequest:
        return RunRequest(
            role=role,
            court_id=court,
            docket_id=docket,
            event_id=event_id,
            actor_id=actor,
            run_id=run_id,
            prompt=Path(prompt),
            data_root=data_root,
        )

    predictions: list[Path] = []
    for ev in targets:
        for predictor in enabled_predictors(config_root / "predictors.yaml"):
            request = _request(UsageRole.predictor, predictor.id, predictor.prompt, ev.event_id)
            predictions.extend(runner.run(request))

    evaluations: list[Path] = []
    for ev in targets:
        if not case_paths.event(ev.event_id).outcome.is_file():
            continue  # nothing to score until the event resolves
        for evaluator in enabled_evaluators(config_root / "evaluators.yaml"):
            request = _request(UsageRole.evaluator, evaluator.id, evaluator.prompt, ev.event_id)
            evaluations.extend(runner.run(request))

    ledger = validate_ledger(data_root)
    references = run_ledger_referential_checks(data_root)
    problems = [*ledger.problems]
    for check in references:
        problems.extend(check.problems)

    return CascadeReport(
        case_id=case_id,
        engine=engine,
        run_id=run_id,
        snapshot=snapshot,
        events=tuple(ev.event_id for ev in targets),
        predictions=tuple(predictions),
        outcomes=tuple(outcomes),
        evaluations=tuple(evaluations),
        valid=ledger.ok and all(c.passed for c in references),
        problems=tuple(problems),
    )
