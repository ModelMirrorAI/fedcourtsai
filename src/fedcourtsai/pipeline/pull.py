"""``run-pull``: the single-docket REST helper — onboard or refresh one docket.

Deterministic — no agent required. Fetches a docket from the CourtListener REST
API, normalizes it through the shared ingestion core, and upserts the resulting
row into the unified corpus (:mod:`fedcourtsai.corpus`). It reports whether the
docket changed since the last pull — the signal that downstream ``run-predict``
should be triggered for this case.

The first pull of a docket onboards it (no prior snapshot → ``changed``);
later pulls refresh it. Both the normalized row and the dated full-docket
snapshot (the point-in-time JSON a normalized row cannot fully capture) land in
the corpus, never in per-case git files: the snapshot backs change detection and
is what predictors/evaluators are provisioned from. Each refresh also re-extracts
the docket's predictable events, so a filing that appears after onboarding (a
stay / emergency motion) becomes trackable, not just the events present at
discovery. ``pull`` drives this function for onboarding and refresh alike.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import httpx

from .. import corpus, ids
from ..config import PredictScope
from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_transient
from ..matrix import event_has_evaluations, event_has_predictions
from ..registry import enabled_evaluators
from ..store import open_events
from .events import AmbiguousEntry, extract_events
from .ingest import from_api_docket, upsert_to_corpus
from .outcome import UnrecordedOutcome, disposition_basis, resolve_case, termination_signal


@dataclass
class PullResult:
    case_id: str
    changed: bool
    # Identifier of the snapshot stored in the corpus this refresh (its date).
    # Predictors record it as ``input_snapshot``; the corpus is the store.
    snapshot: str
    # Outcome detection (`pull`'s third job): events resolved deterministically
    # this refresh, and those that appear decided but could not be recorded.
    resolved: list[str]
    unrecorded: list[UnrecordedOutcome]
    # Docket entries that read like a request but match more than one event kind,
    # so extraction did not guess an event for them (mirrors discovery). Collected
    # for triage; not queued.
    ambiguous: list[AmbiguousEntry] = field(default_factory=list)
    # Why the fresh docket looks already decided despite its open events (a
    # terminal docket entry or a linked opinion cluster), or None when it reads
    # as genuinely pending. Keeps decided-looking cases out of the forward
    # prediction queue.
    termination_signal: str | None = None


def pull_case(
    client: CourtListenerClient,
    corpus_db_path: Path,
    data_root: Path,
    court_id: str,
    docket_id: int,
) -> PullResult:
    case_id = ids.case_id(court_id, docket_id)

    docket = client.get_docket(docket_id)
    entries = client.iter_docket_entries(docket_id)
    fresh = {**docket, "docket_entries": entries}

    today = date.today()
    # Change detection and snapshot storage both live in the corpus now: compare
    # the fresh full docket against the latest snapshot the corpus holds, then
    # store today's. A docket with no prior snapshot is an onboard (`changed`).
    with corpus.connect(corpus_db_path) as conn:
        prior = corpus.latest_snapshot(conn, case_id)
        changed = prior is None or prior[1] != fresh
        corpus.upsert_snapshot(conn, case_id, today, fresh)

    row = from_api_docket(fresh)
    # Stamp the corpus tracking state so the budget governor can rotate this case
    # to the back of the oldest-`last_pulled`-first queue on the next run.
    upsert_to_corpus(corpus_db_path, [row], last_pulled=today)

    # Detect resolution of any open events: write outcome.json deterministically
    # when the disposition is machine-readable, else surface it unrecorded.
    # Runs *before* re-extraction: `default_event` marks a decided case's baseline
    # resolved (from its disposition), so resolution must see the event still open
    # to record its outcome before extraction latches it closed.
    resolution = resolve_case(
        corpus_db_path,
        data_root,
        row,
        court_id,
        docket_id,
        disposition_basis=disposition_basis(fresh),
    )

    # Re-extract predictable events from the refreshed docket, not just at
    # discovery: a filing that appears *after* onboarding — most importantly a
    # SCOTUS stay / emergency motion — becomes trackable this way (detection picks
    # it up on the next refresh). Idempotent and resolved-latching (`upsert_events`
    # never reopens a closed event); `extract_events` marks an entry-pinned event
    # resolved when a later disposing order cites its number.
    extraction = extract_events(fresh)
    with corpus.connect(corpus_db_path) as conn:
        corpus.upsert_events(conn, extraction.events)

    return PullResult(
        case_id=case_id,
        changed=changed,
        snapshot=today.isoformat(),
        resolved=sorted(resolution.outcomes),
        unrecorded=list(resolution.unrecorded),
        ambiguous=list(extraction.ambiguous),
        termination_signal=termination_signal(fresh),
    )


@dataclass
class PullQueues:
    """The three downstream handoffs a ``pull-all`` run produces.

    Each entry is a JSON-serializable mapping shaped exactly as the ``run-pull``
    workflow consumes it (the ``jq`` fields in ``run-pull.yml``): ``predict`` and
    ``evaluate`` entries carry ``court`` / ``docket`` / ``events``; ``unrecorded``
    adds the maintainer-facing ``reason`` the run log surfaces.
    """

    predict: list[dict[str, object]] = field(default_factory=list)
    # Changed cases with open events that were NOT queued forward because the
    # refreshed docket already looks decided (its latest entry reads terminal,
    # or its outcome could not be recorded deterministically). A forward cell on a
    # decided case is a mislabeled back-test — its "unrestricted retrieval"
    # would let any predictor read the outcome — so these are surfaced in the
    # run log for maintainer triage instead of silently mispredicted. A
    # terminal-entry case with no recordable outcome keeps its events open and
    # will re-skip on later refreshes until a maintainer records its outcome
    # or retires it.
    predict_skipped_decided: list[dict[str, object]] = field(default_factory=list)
    evaluate: list[dict[str, object]] = field(default_factory=list)
    # Resolved events dropped from the evaluate queue because the ledger holds
    # no prediction to score. Surfaced (never silently discarded): resolution
    # latches closed, so this poll's edge-triggered queue is once-only. What was
    # once an unrecoverable drop — a prediction landing *after* the outcome, an
    # in-flight predict run racing a fast resolution — is now re-derived by
    # `evaluate_backlog` on a later cycle: the ledger scan (outcome + prediction
    # present, evaluation absent) that this comment used to name as the manual
    # recovery is exactly what the deriver runs.
    evaluate_skipped: list[dict[str, object]] = field(default_factory=list)
    # Of the `evaluate` entries above, how many the backlog deriver contributed
    # (as opposed to this poll's fresh resolutions). Count, not a parallel list,
    # so a caller cannot write it to a second file and double-queue.
    evaluate_from_backlog: int = 0
    unrecorded: list[dict[str, object]] = field(default_factory=list)
    # Cases whose refresh hit an unrecoverable REST error this run (e.g. a 404,
    # or retries exhausted). Recorded so a single bad docket degrades the run
    # gracefully instead of aborting the rotation; carries ``court`` / ``docket``
    # / ``reason`` for a maintainer to triage.
    failed: list[dict[str, object]] = field(default_factory=list)
    # Why the rotation stopped before exhausting ``due`` (deadline, breaker, or
    # API budget), or None when it ran to completion. The cases it never reached
    # land in ``deferred``: their ``last_pulled`` is untouched, so they stay at
    # the stalest-first front of the next window's rotation.
    stopped: str | None = None
    deferred: list[dict[str, object]] = field(default_factory=list)


def _in_predict_scope(corpus_db_path: Path, case_id: str) -> bool:
    """Whether a case is in predict scope: a SCOTUS docket, not excluded, and selected.

    The scope predicate is the immutable row property ``court == "scotus"``,
    with the same exclusion reasoning the matrix backstop layers on
    (``corpus.out_of_scope_reason_full`` — the row rules plus the snapshot-aware
    bare opinion-import rule), plus the salience gate: a scored petition not
    selected into the fundable slice (``corpus.is_salience_deferred``) is deferred,
    not queued. Checking it here,
    at queue time, means pull never opens a ``run-predict`` issue for a case the
    gate would only drop — so a batch of nothing-but-out-of-scope cases never
    files an empty run (the live evaluation also covers cases the scope reconcile
    has not yet latched ``predict_excluded``). The salience check is fail-open: an
    unscored row is treated as selected, so the queue is unaffected until the
    selection pass has run.
    """
    with corpus.connect(corpus_db_path) as conn:
        row = corpus.get_row(conn, case_id)
        return bool(
            row
            and row.court == "scotus"
            and corpus.out_of_scope_reason_full(conn, row) is None
            and not corpus.is_salience_deferred(row)
        )


def _queue_predict(
    queues: PullQueues,
    corpus_db_path: Path,
    result: PullResult,
    court: str,
    docket: int,
    events: list[str],
) -> None:
    """Queue one changed case with open events forward — or divert it.

    A decided-looking docket never queues forward: either the fresh payload
    carries a termination signal, or resolution left an unrecorded outcome
    (appears decided, not deterministically recordable). Both land on
    ``predict_skipped_decided`` with the reason, so the skip is triageable
    rather than silent. Either way the case's ``predict_queued_at`` is stamped,
    so the live channel's selection sweep never re-queues on the same day a
    pull-side queue entry (or divert) already covered.
    """
    decided_reason = result.termination_signal or (
        "docket appears decided; its outcome could not be recorded deterministically"
        if result.unrecorded
        else None
    )
    if decided_reason:
        queues.predict_skipped_decided.append(
            {"court": court, "docket": docket, "events": events, "reason": decided_reason}
        )
    else:
        queues.predict.append({"court": court, "docket": docket, "events": events})
    with corpus.connect(corpus_db_path) as conn:
        corpus.stamp_predict_queued(conn, [result.case_id], date.today())


def evaluate_backlog(
    corpus_db_path: Path,
    data_root: Path,
    evaluators_path: Path,
    queues: PullQueues,
    *,
    cap: int,
    already_queued: set[str] | None = None,
    today: date | None = None,
) -> None:
    """Re-derive the evaluate queue from committed ledger state.

    This is what makes ``run:evaluate`` level-triggered. The poll seams
    (``pull_cases`` / ``live`` routing) queue evaluate off *this cycle's*
    resolutions, and resolution latches closed, so a failed or paused evaluate
    run drops those gradings with no automatic recovery. This scan finds them
    again: an event that is resolved, has a committed prediction, and is missing
    at least one enabled evaluator's evaluation is graded work still owed.

    Purely local — the git ledger plus the corpus, no network — so unlike the
    predict selection sweep it takes no client, no deadline, and no politeness
    throttle. ``cap`` bounds model spend and PR volume, not request rate: each
    queued case fans out one cell per not-yet-graded evaluator. Candidates drain
    stalest-first by ``evaluate_queued_at`` across cycles, debounced to daily by
    the same stamp (a case queued today waits for tomorrow's cycle rather than
    re-queuing while its run PR is in flight or failed).

    Scope is deliberately *not* ``_in_predict_scope``: that gate drops a
    salience-*deferred* case (``is_salience_deferred``), which is a predict
    *funding* decision. A petition predicted before it drifted below the funding
    line still has a prediction that must be graded, so scoping the backlog by
    predict funding would silently strand exactly those gradings. It uses the
    immutable scope only — SCOTUS and not out-of-scope by the row rules.

    Appends to ``queues.evaluate`` (the same list the poll seams feed, so the
    workflow consumes one queue) and counts the additions in
    ``evaluate_from_backlog``. ``already_queued`` is the case ids this cycle's
    poll seams already queued, so the deriver does not double-queue a case the
    fresh-resolution path just covered.
    """
    if cap <= 0:
        return
    day = today or date.today()
    seen = already_queued or set()
    evaluator_ids = [e.id for e in enabled_evaluators(evaluators_path)]

    # A plain (writable) connection, matching the selection sweep: `iter_rows`
    # and `out_of_scope_reason_full` are typed to it, and the deriver only reads
    # here — the single write is the stamp below, on its own connection.
    with corpus.connect(corpus_db_path) as conn:
        rows_by_case = {row.case_id: row for row in corpus.iter_rows(conn, court="scotus")}
        resolved_by_case: dict[str, list[str]] = {}
        for event in corpus.iter_resolved_events(conn, court="scotus"):
            resolved_by_case.setdefault(event.case_id, []).append(event.event_id)
        candidates = [
            row
            for case_id, row in rows_by_case.items()
            if case_id in resolved_by_case
            and case_id not in seen
            and row.evaluate_queued_at != day
            and corpus.out_of_scope_reason_full(conn, row) is None
        ]

    # Stalest first, so the backlog drains fairly under the cap; a never-queued
    # case (evaluate_queued_at is None) sorts first.
    candidates.sort(key=lambda r: (r.evaluate_queued_at or date.min, r.case_id))

    queued_case_ids: list[str] = []
    for row in candidates:
        if len(queued_case_ids) >= cap:
            break
        court, docket_str = row.case_id.split("/", 1)
        docket = int(docket_str)
        owed = [
            event_id
            for event_id in resolved_by_case[row.case_id]
            if event_has_predictions(data_root, court, docket, event_id)
            and any(
                not event_has_evaluations(data_root, court, docket, event_id, evaluator_id=ev)
                for ev in evaluator_ids
            )
        ]
        if not owed:
            continue
        queues.evaluate.append({"court": court, "docket": docket, "events": owed})
        queues.evaluate_from_backlog += 1
        queued_case_ids.append(row.case_id)

    if queued_case_ids:
        with corpus.connect(corpus_db_path) as conn:
            corpus.stamp_evaluate_queued(conn, queued_case_ids, day)


def pull_cases(
    client: CourtListenerClient,
    corpus_db_path: Path,
    data_root: Path,
    due: Iterable[tuple[str, int]],
    *,
    scope: PredictScope = PredictScope.all,
    deadline: float | None = None,
    max_consecutive_transient_failures: int | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> PullQueues:
    """Refresh each due case and sort it into the predict / evaluate / unrecorded queues.

    The per-case half of ``pull-all``: for every ``(court, docket)`` the rotation
    governor selected, refresh the docket (:func:`pull_case`, which also detects
    resolution), then route the result — a *changed* case with open events to
    ``predict`` unless the refreshed docket already looks decided (a termination
    signal, or an unrecorded outcome for its open events), in which case it lands on
    ``predict_skipped_decided`` for triage instead of a mislabeled forward cell;
    a case that gained an ``outcome.json`` this run to ``evaluate``
    **when the ledger holds a prediction to score** (ground-truth recording is
    ungated; only the evaluator fan-out is), and a case that appears decided but
    could not be recorded deterministically to ``unrecorded``. Case selection
    (discovery + rotation) stays with the caller, so this seam composes the
    same way the CLI's ``pull-all`` does.

    The prediction-scope gate is the primary cost-saver: under
    ``scope == scotus_docket`` an out-of-scope case never reaches the ``predict``
    or ``evaluate`` queue, so it never opens a ``run-predict`` / ``run-evaluate``
    issue. ``unrecorded`` stays ungated — it surfaces ground-truth gaps for the
    corpus / back-testing, a different purpose from prediction spend. ``scope == all``
    (the default) enqueues exactly as before.

    Three guards stop the rotation early — recording why on ``stopped`` and the
    unreached cases on ``deferred`` — so a degraded upstream degrades the run
    instead of hanging it into the CI job timeout (which would discard even the
    completed refreshes): a wall-clock ``deadline`` (monotonic, checked between
    cases), a circuit breaker after ``max_consecutive_transient_failures``
    timeouts/5xx/429s in a row (each doomed case burns a full retry cycle of
    budget and minutes; deterministic errors like a 404 never trip it), and
    :class:`RateBudgetExceeded` from the client when the API budget is spent.
    """
    queues = PullQueues()
    gated = scope == PredictScope.scotus_docket
    due_list = list(due)
    consecutive_transient = 0

    def _stop(reason: str, remaining: list[tuple[str, int]]) -> None:
        queues.stopped = reason
        queues.deferred = [{"court": c, "docket": d} for c, d in remaining]

    for index, (court, docket) in enumerate(due_list):
        if deadline is not None and time_fn() >= deadline:
            _stop("run deadline reached", due_list[index:])
            break
        try:
            result = pull_case(client, corpus_db_path, data_root, court, docket)
        except RateBudgetExceeded as exc:
            # The next request cannot fit the API budget this window; every
            # later case would hit the same wall, so defer them all now.
            _stop(f"API budget exhausted ({exc})", due_list[index:])
            break
        except httpx.HTTPError as exc:
            # One docket's REST failure must not abort the rotation: the cases
            # already refreshed this run keep their corpus writes and queue
            # entries. Record the casualty and move on. ``pull_case`` fetches
            # before it writes, so a failure here leaves no partial corpus state.
            queues.failed.append(
                {"court": court, "docket": docket, "reason": f"{type(exc).__name__}: {exc}"}
            )
            if is_transient(exc):
                consecutive_transient += 1
                if (
                    max_consecutive_transient_failures is not None
                    and consecutive_transient >= max_consecutive_transient_failures
                ):
                    _stop(
                        f"{consecutive_transient} consecutive transient REST failures",
                        due_list[index + 1 :],
                    )
                    break
            else:
                consecutive_transient = 0
            continue
        consecutive_transient = 0
        in_scope = not gated or _in_predict_scope(corpus_db_path, result.case_id)
        events = open_events(corpus_db_path, court, docket)
        if in_scope and result.changed and events:
            _queue_predict(queues, corpus_db_path, result, court, docket, events)
        if in_scope and result.resolved:
            # Only events something actually predicted reach evaluation: an
            # outcome recorded for a never-predicted event has nothing to score,
            # and each queued case fans out one agent cell per evaluator.
            scoreable = [
                event_id
                for event_id in result.resolved
                if event_has_predictions(data_root, court, docket, event_id)
            ]
            if scoreable:
                queues.evaluate.append({"court": court, "docket": docket, "events": scoreable})
            unscoreable = [e for e in result.resolved if e not in scoreable]
            if unscoreable:
                queues.evaluate_skipped.append(
                    {"court": court, "docket": docket, "events": unscoreable}
                )
        if result.unrecorded:
            queues.unrecorded.append(
                {
                    "court": court,
                    "docket": docket,
                    "events": [r.event_id for r in result.unrecorded],
                    "reason": result.unrecorded[0].reason,
                }
            )
    return queues
