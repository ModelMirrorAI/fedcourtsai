"""Offline stub cascade over a packed corpus: provision → predict → evaluate.

The production predict/evaluate cells run a coding agent inside Actions, so their
*mechanics* — provisioning a case's snapshot from the corpus, materializing its
predictable event into the git ledger, producing an artifact at the canonical
path, and having ``validate`` accept it — are only exercised in CI today. This
module drives those mechanics end-to-end with the offline :class:`StubRunner`
against a packed corpus (the fixture corpus in the gate's smoke), so a broken cell
fails fast in ``pytest`` instead of a labelled CI run.

It is the deterministic core a stub ``local-cascade`` would wrap: no model call,
no network, fully determined by the corpus and the run id. The corpus read seams
it exercises — :func:`fedcourtsai.corpus.latest_snapshot` (provision-snapshot) and
:func:`fedcourtsai.corpus.events_for_case` (materialize-event) — are the same ones
the live workflow calls after a ``dvc pull``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .. import corpus, ids
from ..paths import CasePaths
from ..schemas import Disposition, Outcome, PredictableEvent, UsageRole
from ..serialize import write_json, write_raw_json, write_yaml
from .outcome import granted_flag, is_machine_readable
from .runner import RunRequest, get_runner

# The prompt templates the live cells read; carried for parity with the workflow
# (the stub does not consult them) so a request is shaped like a real one.
PREDICT_PROMPT = Path(".github/prompts/predict.md")
EVALUATE_PROMPT = Path(".github/prompts/evaluate.md")


@dataclass(frozen=True)
class CascadeReport:
    """The artifacts one stub-cascade run produced for a case, for assertions/logging."""

    case_id: str
    predictions: tuple[Path, ...]
    outcomes: tuple[Path, ...]
    evaluations: tuple[Path, ...]


def run_stub_cascade(
    corpus_db_path: Path,
    data_root: Path,
    court_id: str,
    docket_id: int,
    run_id: str,
    *,
    predictor_id: str = "stub-baseline",
    evaluator_id: str = "stub-judge",
) -> CascadeReport:
    """Run provision → predict → (resolve →) evaluate for one case via the stub.

    Reads the case's events and latest snapshot from ``corpus_db_path``, provisions
    the snapshot and materializes each event into the ledger under ``data_root``,
    then runs a stub prediction for every event. For an event the corpus already
    marks resolved (its case carries a machine-readable disposition and a decision
    date), it also writes the ground-truth ``outcome.json`` rebuilt from the corpus
    row — the label ``pull`` would have recorded — and runs a stub evaluation that
    scores the prediction against it. Returns every artifact written, in the order
    produced. Raises ``KeyError`` if the corpus holds no row for the case.
    """
    case = ids.case_id(court_id, docket_id)
    runner = get_runner("stub")
    with corpus.connect(corpus_db_path) as conn:
        row = corpus.get_row(conn, case)
        events = corpus.events_for_case(conn, case)
        snapshot = corpus.latest_snapshot(conn, case)
    if row is None:
        raise KeyError(f"corpus has no row for {case}")

    case_paths = CasePaths(data_root, court_id, docket_id)
    # Provision the latest corpus snapshot where the cell would read it (record/).
    if snapshot is not None:
        snapshot_date, payload = snapshot
        write_raw_json(case_paths.snapshot(snapshot_date.isoformat()), payload)

    predictions: list[Path] = []
    outcomes: list[Path] = []
    evaluations: list[Path] = []
    disposition = row.disposition
    for event in events:
        event_paths = case_paths.event(event.event_id)
        # Materialize the corpus event into the git ledger, as the workflow does,
        # so the prediction committed beside it references an event `validate` sees.
        write_yaml(
            event_paths.event_file,
            PredictableEvent(
                event_id=event.event_id,
                case_id=event.case_id,
                kind=event.kind,
                title=event.title,
                description=event.description,
                docket_entry_id=event.docket_entry_id,
                opened_at=event.opened_at,
                decision_target=event.decision_target,
                resolved=event.resolved,
            ),
        )
        predictions.extend(
            runner.run(
                _request(
                    UsageRole.predictor,
                    data_root,
                    court_id,
                    docket_id,
                    event.event_id,
                    predictor_id,
                    run_id,
                    PREDICT_PROMPT,
                )
            )
        )

        # A resolved event has a recorded outcome the evaluator scores against;
        # rebuild it from the corpus row (the ground truth `pull` would have written)
        # and run the evaluate cell against the prediction just produced.
        if event.resolved and row.date_decided is not None and is_machine_readable(disposition):
            assert disposition is not None  # narrowed by is_machine_readable above
            outcome = Outcome(
                case_id=case,
                event_id=event.event_id,
                resolved_at=row.date_decided,
                actual_disposition=Disposition(disposition),
                actual_granted=granted_flag(Disposition(disposition)),
                source=row.citations[0] if row.citations else None,
            )
            write_json(event_paths.outcome, outcome)
            outcomes.append(event_paths.outcome)
            evaluations.extend(
                runner.run(
                    _request(
                        UsageRole.evaluator,
                        data_root,
                        court_id,
                        docket_id,
                        event.event_id,
                        evaluator_id,
                        run_id,
                        EVALUATE_PROMPT,
                    )
                )
            )

    return CascadeReport(
        case_id=case,
        predictions=tuple(predictions),
        outcomes=tuple(outcomes),
        evaluations=tuple(evaluations),
    )


def _request(
    role: UsageRole,
    data_root: Path,
    court_id: str,
    docket_id: int,
    event_id: str,
    actor_id: str,
    run_id: str,
    prompt: Path,
) -> RunRequest:
    """Build the cell's :class:`RunRequest` for ``role`` from the cell inputs."""
    return RunRequest(
        role=role,
        court_id=court_id,
        docket_id=docket_id,
        event_id=event_id,
        actor_id=actor_id,
        run_id=run_id,
        prompt=prompt,
        data_root=data_root,
    )
