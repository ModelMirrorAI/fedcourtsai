"""Filesystem queries over the packed corpus and the derived-ledger tree.

Used by the orchestration layer (``run-pull`` / ``run-predict`` / ``run-evaluate``)
to enumerate what exists — which dockets the corpus tracks, which of their
predictable events are open or resolved — without an agent in the loop. Both the
case set and the event state are read from the packed corpus; the git tree under
``data/`` holds only the derived ledger (outcomes, predictions, evaluations).
"""

from __future__ import annotations

from pathlib import Path

from . import corpus, ids
from .schemas import AgentFlags, Evaluation, ModelUsage
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


def open_events(corpus_db_path: Path, court_id: str, docket_id: int) -> list[str]:
    """Event ids the corpus still tracks as unresolved (``resolved = 0``).

    The event-state seam reads from the packed corpus, where ``seed`` and ``pull``
    record predictable events as raw facts: a case enters the corpus with its
    event(s) open, and outcome detection flips each event's ``resolved`` flag when
    it records that event's ``outcome.json``. These are the events ``run-predict``
    should target. Empty (not created) if the corpus does not exist yet.
    """
    if not corpus_db_path.exists():
        return []
    case_id = ids.case_id(court_id, docket_id)
    with corpus.connect(corpus_db_path) as conn:
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


def iter_flags(data_root: Path) -> list[AgentFlags]:
    """Every committed ``flags.json`` in the derived ledger, in stable path order.

    A cell writes one only when it surfaced something to triage; predict flags live
    at ``predictions/<predictor>/<run>/flags.json`` and evaluate flags at
    ``evaluations/<evaluator>/<run>/flags.json``. Both are matched and validated so
    the run-ops dashboard rolls up only well-formed records. Returns nothing if the
    ledger does not exist yet (reading must not create it).
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return []
    patterns = (
        "*/*/events/*/predictions/*/*/flags.json",
        "*/*/events/*/evaluations/*/*/flags.json",
    )
    paths = sorted(path for pattern in patterns for path in cases_dir.glob(pattern))
    return [read_model(path, AgentFlags) for path in paths]
