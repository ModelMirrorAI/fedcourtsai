"""Filesystem queries over the packed corpus and the derived-ledger tree.

Used by the orchestration layer (``run-pull`` / ``run-predict`` / ``run-evaluate``)
to enumerate what exists — which dockets the corpus tracks, which of their
predictable events are open or resolved — without an agent in the loop. Both the
case set and the event state are read from the packed corpus; the git tree under
``data/`` holds only the derived ledger (outcomes, predictions, evaluations).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from . import corpus, ids
from .leaderboard import Stratum, classify_stratum
from .schemas import AgentFlags, AgentToolingFeedback, Evaluation, ModelUsage, Outcome, Prediction
from .serialize import read_model


def iter_tracked_cases(corpus_db_path: Path) -> list[tuple[str, int]]:
    """Return ``(court_id, docket_id)`` for every case in the packed corpus.

    The corpus is the set of tracked dockets — a case enters it the first time
    ``pull`` ingests its docket. Returns nothing if the corpus does not exist
    yet (rather than creating an empty one as a side effect of reading).
    """
    if not corpus_db_path.exists():
        return []
    found: list[tuple[str, int]] = []
    with corpus.connect(corpus_db_path) as conn:
        for row in corpus.iter_rows(conn):
            court_id, _, docket_raw = row.case_id.partition("/")
            if docket_raw.isdigit():
                found.append((court_id, int(docket_raw)))
    return found


def _case_pair(case_id: str) -> tuple[str, int] | None:
    """Split a ``<court_id>/<docket_id>`` case id into a ``(court, docket)`` pair."""
    court_id, _, docket_raw = case_id.partition("/")
    return (court_id, int(docket_raw)) if docket_raw.isdigit() else None


def cases_due_for_pull(
    corpus_db_path: Path, *, limit: int, skip_closed: bool = True, eligible_reserve: int = 0
) -> list[tuple[str, int]]:
    """The ``(court, docket)`` cases ``pull`` should refresh this run, stalest first.

    The budget governor: returns at most ``limit`` cases from the active set in
    oldest-``last_pulled``-first order (skipping closed/resolved cases by
    default), so a run provably touches no more than ``limit`` dockets and a
    large active set rotates over successive days. ``eligible_reserve`` reserves
    up to that many slots for the stalest ``predict_eligible`` cases so the pilot
    set rotates ahead of the general active set (see
    :func:`fedcourtsai.corpus.rotation_for_pull`). Empty if the corpus does not
    exist yet (reading must not create it).
    """
    if not corpus_db_path.exists():
        return []
    with corpus.connect(corpus_db_path) as conn:
        rows = corpus.rotation_for_pull(
            conn, limit=limit, skip_closed=skip_closed, eligible_reserve=eligible_reserve
        )
    return [pair for row in rows if (pair := _case_pair(row.case_id)) is not None]


def open_events(
    corpus_db_path: Path,
    court_id: str,
    docket_id: int,
    *,
    backend: corpus.CorpusBackend | None = None,
) -> list[str]:
    """Event ids the corpus still tracks as unresolved (``resolved = 0``).

    The event-state seam reads from the packed corpus, where the ingestion channels
    record predictable events as raw facts: a case enters the corpus with its
    event(s) open, and outcome detection flips each event's ``resolved`` flag when
    it records that event's ``outcome.json``. These are the events ``run-predict``
    should target. Empty (not created) if the local corpus does not exist yet;
    ``backend`` selects the read backend (see :func:`corpus.connect_readonly`).

    A case the scope reconcile has latched **out of scope** (``predict_excluded``)
    yields no predictable events here — so a stale/unresolvable or
    inconsistent case is dropped at the source, not just at the read-time matrix
    gate. The reconcile clears the latch if the case ever returns to scope.
    """
    choice = corpus.resolve_backend(backend)
    if choice == "local" and not corpus_db_path.exists():
        return []
    case_id = ids.case_id(court_id, docket_id)
    with corpus.connect_readonly(corpus_db_path, backend=choice) as conn:
        row = corpus.get_row(conn, case_id)
        if row is not None and row.predict_excluded:
            return []
        events = corpus.events_for_case(conn, case_id)
    return [event.event_id for event in events if not event.resolved]


def resolved_events(corpus_db_path: Path, court_id: str, docket_id: int) -> list[str]:
    """Event ids the corpus tracks as resolved (``resolved = 1``).

    The mirror of :func:`open_events`: an event whose ``outcome.json`` has been
    recorded is flipped resolved in the corpus, making it ready for
    ``run-evaluate``. Empty (not created) if the corpus does not exist yet.
    """
    if not corpus_db_path.exists():
        return []
    case_id = ids.case_id(court_id, docket_id)
    with corpus.connect(corpus_db_path) as conn:
        events = corpus.events_for_case(conn, case_id)
    return [event.event_id for event in events if event.resolved]


def iter_evaluations(data_root: Path) -> list[Evaluation]:
    """Every ``evaluation.json`` in the derived ledger, in stable path order.

    Walks ``data/cases/<court>/<docket>/events/<event>/evaluations/<evaluator>/
    <predictor>/<run>/evaluation.json`` and validates each against the schema, so
    the leaderboard aggregates only well-formed rows. Returns nothing if the
    ledger does not exist yet (reading must not create it).
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    pattern = "*/*/events/*/evaluations/*/*/*/evaluation.json"
    return [read_model(path, Evaluation) for path in sorted(cases_dir.glob(pattern))]


def iter_stratified_evaluations(data_root: Path) -> list[tuple[Evaluation, Stratum]]:
    """Every evaluation joined to its pre-registration stratum, in stable path order.

    For each ``evaluation.json``, reads the scored predictor's prediction(s) for
    the same event and the event's ``outcome.json`` — all committed artifacts, so
    the split is deterministic and offline — and classifies the cell forward vs
    retrospective (:func:`fedcourtsai.leaderboard.classify_stratum`). An
    evaluation names the predictor but not a prediction run, so when the
    predictor ran the event more than once the **latest** prediction's
    ``created_at`` decides: the cell is forward only if even the newest
    prediction predates the resolution — the conservative reading, so a possibly
    post-resolution prediction is never presented as a forward forecast. An
    evaluation can only exist for a resolved event with a real prediction (the
    referential checks enforce both), so a missing sibling artifact raises
    rather than guessing a stratum.
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    cells: list[tuple[Evaluation, Stratum]] = []
    for path in sorted(cases_dir.glob("*/*/events/*/evaluations/*/*/*/evaluation.json")):
        evaluation = read_model(path, Evaluation)
        # event_dir/evaluations/<evaluator>/<predictor>/<run>/evaluation.json
        event_dir = path.parents[4]
        prediction_files = sorted(
            event_dir.glob(f"predictions/{evaluation.predictor_id}/*/prediction.json")
        )
        latest_created_at = max(read_model(p, Prediction).created_at for p in prediction_files)
        outcome = read_model(event_dir / "outcome.json", Outcome)
        cells.append((evaluation, classify_stratum(latest_created_at, outcome.resolved_at)))
    return cells


def ledger_cell_counts(data_root: Path) -> tuple[int, int, int]:
    """``(prediction cells, events predicted, predicted events resolved)``.

    The pipeline-funnel counts the ops substance section leads with, read
    straight off the committed ledger tree: every ``prediction.json`` is one
    cell; the distinct event directories those cells live under are the
    predicted events; a predicted event counts resolved once its
    ``outcome.json`` has landed beside them. Returns zeros when the ledger does
    not exist yet (reading must not create it).
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return (0, 0, 0)
    prediction_files = sorted(cases_dir.glob("*/*/events/*/predictions/*/*/prediction.json"))
    # prediction path: <event_dir>/predictions/<predictor>/<run>/prediction.json
    event_dirs = {path.parents[3] for path in prediction_files}
    resolved = sum(1 for event_dir in event_dirs if (event_dir / "outcome.json").exists())
    return (len(prediction_files), len(event_dirs), resolved)


def iter_usage(data_root: Path) -> list[ModelUsage]:
    """Every ``usage.json`` in the derived ledger, in stable path order.

    Predict usage lives at ``predictions/<predictor>/<run>/usage.json`` and
    evaluate usage at ``evaluations/<evaluator>/<run>/usage.json``; both are
    matched and validated so a cost roll-up sees only well-formed rows. Returns
    nothing if the ledger does not exist yet (reading must not create it).
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    patterns = (
        "*/*/events/*/predictions/*/*/usage.json",
        "*/*/events/*/evaluations/*/*/usage.json",
    )
    paths = sorted(path for pattern in patterns for path in cases_dir.glob(pattern))
    return [read_model(path, ModelUsage) for path in paths]


# The committed agent-artifact layout each stage writes, relative to data/cases:
# predict lives under a per-event prediction dir, evaluate under a per-event
# evaluator x run dir, and reconcile (per case) at the case root above the events.
_PREDICT_GLOB = "*/*/events/*/predictions/*/*/{name}"
_EVALUATE_GLOB = "*/*/events/*/evaluations/*/*/{name}"
_RECONCILE_GLOB = "*/*/reconcile/*/{name}"


def iter_flags(data_root: Path) -> list[AgentFlags]:
    """Every committed ``flags.json`` in the derived ledger, in stable path order.

    A cell writes one only when it surfaced something to triage; predict flags live
    at ``predictions/<predictor>/<run>/flags.json``, evaluate at
    ``evaluations/<evaluator>/<run>/flags.json``, and reconcile at
    ``reconcile/<run>/flags.json`` (per case). All are matched and validated so the
    run-ops dashboard rolls up only well-formed records. Returns nothing if the
    ledger does not exist yet (reading must not create it).
    """
    return _iter_agent_artifact(data_root, "flags.json", AgentFlags)


def iter_tooling(data_root: Path) -> list[AgentToolingFeedback]:
    """Every committed ``tooling.json`` self-report in the ledger, in stable path order.

    Mirrors :func:`iter_flags` across the three stages' layouts; the run-ops dashboard
    rolls these into the agent tooling-feedback digest. Returns nothing if the ledger
    does not exist yet (reading must not create it).
    """
    return _iter_agent_artifact(data_root, "tooling.json", AgentToolingFeedback)


def _iter_agent_artifact[T: BaseModel](data_root: Path, name: str, model: type[T]) -> list[T]:
    """Read every committed ``name`` agent artifact across all stages, validated."""
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    patterns = (
        _PREDICT_GLOB.format(name=name),
        _EVALUATE_GLOB.format(name=name),
        _RECONCILE_GLOB.format(name=name),
    )
    paths = sorted(path for pattern in patterns for path in cases_dir.glob(pattern))
    return [read_model(path, model) for path in paths]
