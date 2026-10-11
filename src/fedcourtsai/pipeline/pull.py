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
from enum import StrEnum
from pathlib import Path
from typing import Literal

import httpx

from .. import corpus, ids
from ..config import PredictScope
from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_transient
from ..matrix import (
    cell_failure_count,
    event_has_evaluations,
    event_has_predictions,
    predicted_case_ids,
)
from ..registry import enabled_evaluators, enabled_predictors
from ..schemas import Moment, Stage
from ..store import (
    event_has_claimable_prediction,
    forecastable_event_ids,
    forecastable_events,
    forward_refusal_reason_from_parts,
    predictor_holds_no_counted_prediction,
)
from .events import AmbiguousEntry, extract_events
from .ingest import from_api_docket, upsert_to_corpus
from .moments import spec_for
from .outcome import (
    UnrecordedOutcome,
    disposition_basis,
    forward_leakage,
    read_order_markers,
    resolve_case,
    termination_signal,
)


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
        order=read_order_markers(
            fresh, disposition=row.disposition, date_cert_granted=row.date_cert_granted
        ),
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
    """The three downstream queues a ``pull-all`` run produces.

    Each entry is a JSON-serializable mapping shaped exactly as the ``run-pull``
    workflow consumes it (the ``jq`` fields in ``run-pull.yml``): ``predict`` and
    ``evaluate`` entries carry ``court`` / ``docket`` / ``events``; ``unrecorded``
    adds the maintainer-facing ``reason`` the window's step summary surfaces.
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
    # Live-channel only: changed cases with open events that were NOT queued
    # forward because the case relisted inside the salience config's
    # `relist_requeue_cooldown_days` of its last prediction — administrative
    # churn, not a materially different posture, while capacity is enforced.
    # "Last prediction" spans both minting lanes (`live._last_predict_mint`):
    # this lane's `predict_queued_at` stamp, and the newest committed prediction
    # run in the ledger, which is all a stamp-free backlog derivation leaves.
    # Surfaced for triage, never silently dropped. The divert re-stamps
    # `predict_queued_at` to today (same as a decided-skip divert), which both
    # anchors the next cooldown check and keeps the same-cycle selection sweep
    # from immediately re-queuing what this cycle just suppressed.
    predict_skipped_relist_cooldown: list[dict[str, object]] = field(default_factory=list)
    evaluate: list[dict[str, object]] = field(default_factory=list)
    # Resolved events dropped from *this poll's* evaluate queue because the ledger
    # holds no prediction to score. Surfaced (never silently discarded), but not
    # lost either: a prediction that lands after the outcome (an in-flight predict
    # run racing a fast resolution) is picked up by `evaluate_backlog`, which
    # scans the same outcome-present / prediction-present / evaluation-absent
    # condition on a later cycle and re-queues it.
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
    # Live-channel only: the ledger-outcome convergence's counts for the run
    # log (recorded / unrecorded / failed / deferred), or ``{"error": <type>}``
    # when the pass itself raised and was skipped. Empty when it did not run.
    convergence: dict[str, object] = field(default_factory=dict)
    # Live-channel only: the document-freshness pass's ledger for the run log
    # (`live.refresh_stale_documents`) — candidates, checked, stale, refreshed
    # (cases attempted, failures included), documents written, unwritten,
    # failed, deferred by the cap or the deadline, unchecked, and the owed
    # kinds — or ``{"error": <type>}`` when the pass itself raised and was
    # skipped. Empty when the pass is disabled.
    document_freshness: dict[str, object] = field(default_factory=dict)


def _in_predict_scope(
    corpus_db_path: Path, case_id: str, *, cohort_completion: bool = False
) -> bool:
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

    ``cohort_completion`` is the caller's assertion that this queueing would
    only *finish an existing predictor cohort worth finishing* — an event of
    this case already carries a committed prediction, that cohort is one a
    claimable board will count once the event resolves and is graded, some
    enabled engine is missing from it, and the caller has already narrowed its
    queue to exactly those events.
    It bypasses the salience gate on the same reasoning :func:`evaluate_backlog`
    scopes itself by: the gate is a **funding** decision about which petitions
    earn a forecast, and a cohort that already exists was funded, so finishing
    it buys the missing engines on a case the project already paid to predict —
    the incremental spend is the gap, not a new case. The hard exclusions (court,
    ``predict_excluded``, the shared reason rules) are untouched.

    The analogy to :func:`evaluate_backlog` reaches the *funding* half only, and
    stops there. Grading scores a fixed artifact and opens no new information
    set, so refusing to strand a grading costs nothing; cohort completion mints
    a **new forecast at a new information set**, weeks after its siblings. So
    the caller owns two further bounds this flag cannot check for itself: it
    must queue only events that already hold a prediction — never a cell for an
    event nothing predicted — and only events whose cohort a claimable board
    counts (:func:`fedcourtsai.store.event_has_claimable_prediction`).
    """
    with corpus.connect(corpus_db_path) as conn:
        row = corpus.get_row(conn, case_id)
        return row is not None and _row_in_predict_scope(
            conn, row, cohort_completion=cohort_completion
        )


def _row_in_predict_scope(
    conn: corpus.ReadConnection, row: corpus.CorpusRow, *, cohort_completion: bool = False
) -> bool:
    """:func:`_in_predict_scope` over a row the caller already holds.

    The predicate itself, split from the connection handling so a read-only scan
    that has already fetched the row (:func:`derive_predict_backlog`) asks the
    same question without a second lookup — and so the two callers cannot drift
    into two subtly different scope gates.
    """
    return (
        row.court == "scotus"
        and corpus.out_of_scope_reason_full(conn, row) is None
        # The salience gate is a CERT-stage funding decision. A case whose
        # merits proceeding is open was selected by the Court itself, and
        # the question the gate answers — which of ~1,500 petitions is worth
        # a forecast — has no bearing on a population of ~65 grants a Term.
        and (
            not corpus.is_salience_deferred(row)
            or corpus.has_open_merits_event(conn, row.case_id)
            or cohort_completion
        )
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


def _cell_capped(
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    actor_id: str,
    max_attempts: int,
    seam: Literal["predict", "evaluate"] = "evaluate",
) -> bool:
    """Whether a cell has exhausted the per-cell attempt cap at ``seam``.

    Counts the committed ``attempt.json`` failure facts at that seam
    (:func:`fedcourtsai.matrix.cell_failure_count`), keyed on cell identity — the
    corpus-blind ``collect`` job records one per failed run, so a cell retried
    across runs counts against the same cap rather than resetting it.
    ``max_attempts <= 0`` disables the cap.

    ``actor_id`` is the evaluator at the evaluate seam and the predictor at the
    predict seam. Both backlog derivers here and the live channel's selection
    sweep consult it, so the seam is a parameter rather than one copy of these
    four lines per caller — three readings of one cap is three places for it to
    drift.
    """
    if max_attempts <= 0:
        return False
    return cell_failure_count(data_root, court, docket, event_id, actor_id, seam) >= max_attempts


@dataclass(frozen=True)
class BacklogEntry:
    """One case a backlog derivation owes cells on, and the events it owes them for.

    Shared by both derivers: the evaluate backlog's owed gradings and the
    predict backlog's owed forecasts have the same shape, because both name a
    case and the subset of its events some enabled actor has not covered.

    ``reopened`` is the predict deriver's alone and is a **subset of**
    ``events``: those admitted on the pre-freeze re-predict ground rather than
    because a predictor had never covered them (see
    :func:`derive_predict_backlog`). It travels separately because the fan-out's
    per-``(predictor, event)`` already-predicted skip would otherwise drop every
    one of them — the cell it re-owes is by definition one the ledger already
    holds. Empty for every evaluate entry and for an ordinary predict entry.
    """

    case_id: str
    court: str
    docket: int
    events: tuple[str, ...]
    reopened: tuple[str, ...] = ()

    def as_queue_entry(self) -> dict[str, object]:
        """The mapping shape a ``PullQueues`` list carries to the workflow.

        ``reopened`` is deliberately **not** carried: this shape is the pull
        lane's run-log queue, which no fan-out reads back, and a case list a
        maintainer replays by hand must re-derive its own re-predict grounds
        rather than inherit a stale claim that an event's cohort was de-counted.
        """
        return {"court": self.court, "docket": self.docket, "events": list(self.events)}


@dataclass(frozen=True)
class EvaluateBacklog:
    """What one backlog derivation found, before anything is queued.

    Separating the derivation from its consumption keeps the scan itself on
    the read seam regardless of who calls it: the pull seams queue what it
    finds into the run-log count, while the evaluate stage's own schedule
    fans out over it — and neither stamps. The schedule runs outside the
    writer jobs, so a stamp it wrote could never be pushed — it would mutate
    the runner's pulled copy and die with it — and it needs none (see
    :func:`derive_evaluate_backlog`).

    ``day`` is the date the derivation ran under, carried so the debounce
    comparison and any caller that does stamp (none standing) agree on the
    value.
    """

    entries: tuple[BacklogEntry, ...]
    day: date

    @property
    def case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries)


def derive_evaluate_backlog(
    conn: corpus.ReadConnection,
    data_root: Path,
    evaluators_path: Path,
    *,
    cap: int,
    max_attempts: int,
    already_queued: set[str] | None = None,
    today: date | None = None,
) -> EvaluateBacklog:
    """Find the gradings the committed ledger still owes, reading only.

    This is what makes evaluate level-triggered. An event that is resolved, has
    a committed prediction, and is missing at least one enabled evaluator's
    evaluation is graded work still owed — a condition on committed state, so it
    survives a run that was dropped on the floor. The poll seams queue evaluate
    off *this cycle's* resolutions and resolution latches closed, so without
    this scan a failed or paused evaluate run loses those gradings with no
    automatic recovery.

    Purely local — the git ledger plus the corpus, no network — so unlike the
    predict selection sweep it takes no client, no deadline, and no politeness
    throttle. ``cap`` bounds model spend and PR volume, not request rate: each
    queued case fans out one cell per not-yet-graded evaluator. Candidates sort
    by ``evaluate_queued_at`` and a case already stamped with ``today`` is held
    back — the correct semantics for any caller that stamps, though no standing
    lane does: every production caller is stamp-free, so the column is a
    historical rotation record, the hold is vacuous in practice, and the same
    head of the queue re-derives each cycle until the ledger moves under it.
    (A pull-lane stamp here would starve the scheduled lane: a pull window
    precedes the evaluate slot daily, and the scheduled lane is the only actor
    that grades what this scan finds.)

    The connection is a :class:`~fedcourtsai.corpus.ReadConnection`, which keeps
    this scan on the read seam: every read here — ``iter_resolved_events``,
    ``get_row``, ``out_of_scope_reason_full`` — is typed to it, so a caller may
    pass a ranged connection and no writer-only API (``commit``,
    ``stamp_evaluate_queued``) is reachable through the parameter. It is a
    one-method protocol, not a proof: what actually keeps the corpus of record
    intact is that write credentials live only in the writer jobs.

    ``max_attempts`` is the poison-pill backstop the daily debounce lacks (counted
    from the committed ``attempt.json`` failure facts, see
    :func:`fedcourtsai.matrix.cell_failure_count`): an (evaluator, event)
    cell recorded failed that many times is not re-derived, so a cell that fails
    every attempt — a persistent quota wall, a malformed record — cannot re-queue
    forever. The count keys on cell identity, not process version, so a retry
    under a newer version still counts against the cap; ``max_attempts == 0``
    disables it (every ungraded cell re-queues). Because the cap is
    per (evaluator, event) it never lets one exhausted cell suppress a sibling
    evaluator still owed the same event.

    Scope is deliberately *not* ``_in_predict_scope``: that gate drops a
    salience-*deferred* case (``is_salience_deferred``), which is a predict
    *funding* decision. A petition predicted before it drifted below the funding
    line still has a prediction that must be graded, so scoping the backlog by
    predict funding would silently strand exactly those gradings. It uses the
    immutable scope only — SCOTUS and not out-of-scope by the row rules.

    ``already_queued`` is the case ids a caller's poll seams queued this cycle,
    so the deriver does not double-queue a case the fresh-resolution path just
    covered — case-granular, so a case queued this cycle for one event defers
    its *other* owed events to the next cycle. That is fine: the very next
    derivation re-presents them. For SCOTUS, where
    ``evt-petition-disposition`` is typically the sole event, the case rarely
    has other owed events at all.
    """
    day = today or date.today()
    if cap <= 0:
        return EvaluateBacklog(entries=(), day=day)
    seen = already_queued or set()
    evaluator_ids = [e.id for e in enabled_evaluators(evaluators_path)]

    # Drive from the resolved-event set and fetch each candidate's row, rather
    # than indexing the whole court and probing it. Only cases with a resolved
    # event can be owed a grading, and that set runs tens of thousands against a
    # SCOTUS slice of hundreds of thousands that only ever grows — so indexing
    # the court would make peak memory a function of the corpus rather than of
    # the work, for no gain. Both orders are `case_id`-ascending and the
    # candidates are re-sorted below, so the queue is unchanged either way.
    #
    # The cost is one scan plus a point query per candidate case, which a local
    # (pulled) corpus answers in seconds. That is why a scheduled caller pulls
    # rather than reading ranged: this access pattern is the wrong shape for a
    # backend that fetches by range.
    resolved_by_case: dict[str, list[str]] = {}
    for event in corpus.iter_resolved_events(conn, court="scotus"):
        resolved_by_case.setdefault(event.case_id, []).append(event.event_id)
    candidates: list[corpus.CorpusRow] = []
    for case_id in resolved_by_case:
        if case_id in seen:
            continue
        row = corpus.get_row(conn, case_id)
        if (
            row is not None
            and row.evaluate_queued_at != day
            and corpus.out_of_scope_reason_full(conn, row) is None
        ):
            candidates.append(row)

    # Stalest first, so the backlog drains fairly under the cap; a never-queued
    # case (evaluate_queued_at is None) sorts first.
    candidates.sort(key=lambda r: (r.evaluate_queued_at or date.min, r.case_id))

    entries: list[BacklogEntry] = []
    for row in candidates:
        if len(entries) >= cap:
            break
        court, docket_str = row.case_id.split("/", 1)
        docket = int(docket_str)
        # An (evaluator, event) cell is owed when it is ungraded AND has not hit
        # the per-cell attempt cap. Checking the cap per cell — not per case or
        # per event — is what keeps one poison-pill evaluator from suppressing a
        # sibling evaluator still owed the same event.
        owed = [
            event_id
            for event_id in resolved_by_case[row.case_id]
            if event_has_predictions(data_root, court, docket, event_id)
            and any(
                not event_has_evaluations(data_root, court, docket, event_id, evaluator_id=ev)
                and not _cell_capped(data_root, court, docket, event_id, ev, max_attempts)
                for ev in evaluator_ids
            )
        ]
        if not owed:
            continue
        entries.append(
            BacklogEntry(case_id=row.case_id, court=court, docket=docket, events=tuple(owed))
        )

    return EvaluateBacklog(entries=tuple(entries), day=day)


def evaluate_backlog(
    corpus_db_path: Path,
    data_root: Path,
    evaluators_path: Path,
    queues: PullQueues,
    *,
    cap: int,
    max_attempts: int,
    already_queued: set[str] | None = None,
    today: date | None = None,
) -> None:
    """Report the owed gradings a pull cycle found, without stamping them.

    The pull lane's consumption of :func:`derive_evaluate_backlog`: it appends
    to ``queues.evaluate`` (the same list the poll seams feed, so the workflow
    consumes one queue) and counts the additions in ``evaluate_from_backlog``.
    The queue is a run-log count, nothing more — nothing downstream reads it
    and no ``evaluate_queued_at`` stamp is written. Deliberately so: the scheduled
    evaluate lane holds off a case stamped *today*, and it is the only actor
    that grades, so a pull-lane stamp here would rotate owed gradings away
    from the one lane that can clear them (a pull window precedes the evaluate
    slot every day) while nothing acts on this queue in their place.
    """
    # Short-circuit a disabled deriver before opening anything: `corpus.connect`
    # creates the database and its schema, which a cap of 0 should not provoke.
    if cap <= 0:
        return
    with corpus.connect(corpus_db_path) as conn:
        derived = derive_evaluate_backlog(
            conn,
            data_root,
            evaluators_path,
            cap=cap,
            max_attempts=max_attempts,
            already_queued=already_queued,
            today=today,
        )

    for entry in derived.entries:
        queues.evaluate.append(entry.as_queue_entry())
        queues.evaluate_from_backlog += 1


#: How stale a case's corpus row may be and still be minted from by
#: :func:`derive_predict_backlog`.
#:
#: The live channel's selection sweep re-polls every case *before* it queues
#: one, and acts on what comes back: a docket that now looks decided is
#: diverted to ``predict_skipped_decided`` instead of queued. That re-poll is
#: the backstop against forecasting a case whose answer is already public, and
#: a scan over committed state has no equivalent — it can only mint from what
#: the record last saw. So the record's own age becomes the bound. An open
#: event on a row nobody has polled in a fortnight is exactly as likely to be
#: resolved-but-unrecorded as still pending, and a forward cell on that case is
#: a mislabeled backtest.
#:
#: Seven days: the live windows poll four times a day on a stalest-first
#: rotation, so a case this lane cares about is normally seen within a day or
#: two (median 1 on the shipped corpus) and a week is several rotations of
#: slack rather than a tight bound. The hold is never terminal — it clears the
#: moment the rotation reaches the case — so the cost of it being slightly too
#: tight is a cycle's delay, while the cost of it being too loose is a cell
#: minted on a stale record.
BACKLOG_MAX_POLL_AGE_DAYS = 7


def _last_observed(row: corpus.CorpusRow) -> date | None:
    """When either ingestion channel last saw this case, or ``None`` if neither has.

    The freshest of the two rotation stamps. They are written by different
    channels and neither is complete: ``last_live_polled`` is the
    supremecourt.gov poller's and covers essentially every case the predict
    backlog considers, while ``last_pulled`` is the CourtListener rotation's and
    covers a small overlap. Taking the maximum asks the question that actually
    matters — *how old is this record* — rather than privileging one channel's
    coverage.
    """
    seen = [stamp for stamp in (row.last_live_polled, row.last_pulled) if stamp is not None]
    return max(seen) if seen else None


#: The declared ``(stage, moment)`` pairs a **re-predict** may target — the
#: moment half of the pre-freeze re-predict rule (see
#: :func:`derive_predict_backlog`). Narrower than the fan-out's own
#: forecastability gate, and deliberately a table rather than a chain of
#: conditions, so the cohort can be narrowed or widened here without reading
#: the deriver.
#:
#: A moment earns a place by two questions: *is the moment still open* (a
#: forecast made after its information set has moved on is a different forecast
#: from the one the cohort holds), and *does the re-predicted cell reach a
#: board while it still matters*.
#:
#: * **cert / distribution** — the petition baseline. Open for as long as the
#:   petition is undistributed-past: the conference it is currently distributed
#:   for decides it, so the rule additionally refuses one whose conference has
#:   already passed (:func:`_reopenable_moment`). This is the cohort the rule
#:   exists for.
#: * **cert / cvsg** — forecast after the Court called for the Solicitor
#:   General's views, an information set that does not expire on a date.
#: * **interim / arrival, response_requested, response_filed** — the
#:   application lane's three moments, each keyed on a docket transition that
#:   has already happened rather than on a date ahead.
#:
#: Two families are excluded, and each for its own reason:
#:
#: * **cert / arrival** — its whole contract is "forecast at docketing, before
#:   any distribution or docket-acquired signal exists"
#:   (:mod:`fedcourtsai.pipeline.moments`). Every such petition has since been
#:   distributed or is about to be, so a cell minted now is not a late forecast
#:   of that moment but a forecast of a different one. The moment is gone; only
#:   the original cell ever observed it.
#: * **merits / grant, briefed** — the moment stays genuinely open (these
#:   resolve months out), so the rule *would* apply. They are held out because a
#:   merits re-predict is spend now for a board population that arrives a Term
#:   later, which is a funding decision rather than a correctness one. Adding
#:   either pair here is the whole change needed to take them.
REPREDICT_MOMENTS: frozenset[tuple[Stage, Moment]] = frozenset(
    {
        (Stage.cert, Moment.distribution),
        (Stage.cert, Moment.cvsg),
        (Stage.interim, Moment.arrival),
        (Stage.interim, Moment.response_requested),
        (Stage.interim, Moment.response_filed),
    }
)


def _reopenable_moment(event_id: str, row: corpus.CorpusRow, *, day: date) -> bool:
    """Whether ``event_id``'s declared moment is one a re-predict may still target.

    :data:`REPREDICT_MOMENTS` plus the one bound that is a date rather than a
    table row: a **distribution** cell forecasts the conference the petition is
    currently distributed for, so once that conference is past the moment the
    cohort was forecast at is over — the order list has been issued or the
    petition relisted, and either way a cell minted now answers a different
    question from the one the de-counted cells answered. A petition with no
    conference at all is refused for the same reason the fan-out's own
    information-set precondition refuses it
    (:func:`fedcourtsai.store._premature_distribution_cell`): the distribution
    moment has not happened.

    An **undeclared** event — an entry-pinned motion, a legacy baseline id —
    has no moment to check and is refused. The rule adds cells to a backlog
    that is otherwise version-blind, so an event the register cannot place is
    left alone rather than guessed into a cohort.
    """
    spec = spec_for(event_id)
    if spec is None or (spec.stage, spec.moment) not in REPREDICT_MOMENTS:
        return False
    if spec.moment is Moment.distribution:
        conference = row.distributed_for_conference
        return conference is not None and conference >= day
    return True


class CaseDisposition(StrEnum):
    """The one bucket a predict-backlog derivation files a case under.

    The admission walk records one of these at every point it decides a case,
    so :class:`CaseReconciliation` can check that each case of the independently
    computed universe landed in exactly one bucket. A bucket names *why*: a case
    in the universe that the walk dropped with no disposition is exactly the
    silent loss the reconciliation exists to surface.
    """

    derived = "derived"
    held_stale = "held_stale"
    held_unswept = "held_unswept"
    held_decided = "held_decided"
    dropped_already_queued = "dropped_already_queued"
    dropped_excluded = "dropped_excluded"
    dropped_not_funded = "dropped_not_funded"
    dropped_owed_nothing = "dropped_owed_nothing"
    dropped_cap_reached = "dropped_cap_reached"


#: The dispositions that put a case on the lane's books: minted, or owed and
#: waiting on a hold. A case the walk files under one of these must be in the
#: universe; one outside it is the walk admitting work the universe says is not
#: there, which the reconciliation names as well.
_ADMITTED_DISPOSITIONS = frozenset(
    {
        CaseDisposition.derived,
        CaseDisposition.held_stale,
        CaseDisposition.held_unswept,
        CaseDisposition.held_decided,
    }
)


class _DispositionLog:
    """The admission walk's record of what it decided per case, bounded by the universe.

    The walk decides over every SCOTUS case with an open event — very nearly the
    whole court — so recording every decision would make memory a function of
    the corpus. Only what the reconciliation reads is kept: dispositions of
    universe cases, and admitting dispositions of any case. The universe filters
    what is *kept*, never what the walk *decides*, so the two stay independent.
    """

    def __init__(self, universe: frozenset[str]) -> None:
        self.universe = universe
        self.by_case: dict[str, list[CaseDisposition]] = {}

    def record(self, case_id: str, disposition: CaseDisposition) -> None:
        if case_id in self.universe or disposition in _ADMITTED_DISPOSITIONS:
            self.by_case.setdefault(case_id, []).append(disposition)

    def count(self, disposition: CaseDisposition) -> int:
        """How many cases' final disposition is ``disposition``."""
        return sum(1 for filed in self.by_case.values() if filed and filed[-1] is disposition)

    def reclassify(self, case_id: str, disposition: CaseDisposition) -> None:
        """Replace a case's last disposition — the cap displacing an admitted case."""
        kept = self.by_case.get(case_id)
        if kept:
            kept[-1] = disposition
        else:
            self.record(case_id, disposition)


@dataclass(frozen=True)
class CaseReconciliation:
    """Case-grain accounting of one predict-backlog derivation.

    The **universe** is every SCOTUS case with an open forecastable event that
    is in predict scope and funded, computed by :func:`_predict_universe`
    without reference to the admission walk. The walk files each case it
    decides under a :class:`CaseDisposition`; a sound derivation files every
    universe case exactly once. Three failures are named:

    - ``unaccounted`` — a universe case the walk filed nowhere: it fell out of
      the derivation without a reason, which is how owed work goes silently
      unforecast.
    - ``multiply_accounted`` — a universe case filed more than once, so the
      bucket counts no longer partition the universe.
    - ``admitted_outside_universe`` — a case the walk derived or held that the
      universe does not contain: the two predicates disagree in the other
      direction.

    ``dropped_owed_nothing`` covers a case every enabled predictor already
    covered or attempt-capped, and also a cohort-only case whose narrowing left
    no event a claimable board counts.

    ``buckets`` counts universe cases by their single disposition (a multiply
    accounted case is counted under none of them). ``dropped_cap_reached`` is the
    censoring bucket, and says so explicitly: when the walk stops at the cycle
    cap, every candidate it never reached is filed there rather than under the
    disposition a full walk would have given it, and a case the walk reaches
    only after the re-predict budget filled, owed no never-predicted cell, is
    filed there too because its re-owed events were never evaluated.
    """

    universe: int
    buckets: dict[str, int]
    unaccounted: tuple[str, ...] = ()
    multiply_accounted: tuple[str, ...] = ()
    admitted_outside_universe: tuple[str, ...] = ()
    cap_reached: bool = False

    @property
    def sound(self) -> bool:
        return not (self.unaccounted or self.multiply_accounted or self.admitted_outside_universe)

    def counts_json(self) -> dict[str, int | bool]:
        """The plan's ``counts.case_reconciliation`` block: case counts, plus the censoring flag.

        ``cap_reached`` travels inside the block so a bucket count read out of it
        cannot be mistaken for a total when the walk stopped at the cap.
        """
        return {
            "cap_reached": self.cap_reached,
            "universe_cases": self.universe,
            **{f"{bucket}_cases": self.buckets.get(bucket, 0) for bucket in CaseDisposition},
            "unaccounted_cases": len(self.unaccounted),
            "multiply_accounted_cases": len(self.multiply_accounted),
            "admitted_outside_universe_cases": len(self.admitted_outside_universe),
        }

    def detail_json(self) -> dict[str, list[str]]:
        """The named discrepancies, for the plan's top-level ``case_reconciliation``."""
        return {
            "unaccounted": list(self.unaccounted),
            "multiply_accounted": list(self.multiply_accounted),
            "admitted_outside_universe": list(self.admitted_outside_universe),
        }


def _predict_universe(
    conn: corpus.ReadConnection,
    *,
    predicted: frozenset[str],
    merits_open: set[str],
    day: date,
) -> frozenset[str]:
    """Every case the predict backlog must account for, computed apart from the walk.

    A SCOTUS case with an open event, a row, funding (the salience latch, an
    open merits event, or a committed prediction somewhere on the case), predict
    scope (:func:`_row_in_predict_scope`, with ``cohort_completion`` exactly when
    the prediction is its only funding) and at least one forecastable open event
    (:func:`fedcourtsai.store.forecastable_event_ids`).

    It shares the **leaf** predicates with :func:`derive_predict_backlog` and
    deliberately nothing else: not :func:`_predict_backlog_candidates`, not its
    ordering, not the loop. A filter added to the walk — a debounce, a skip —
    that drops a case without filing it therefore leaves that case here and
    unaccounted, instead of shrinking both sides of the comparison at once. No
    ledger read beyond the bulk ``predicted`` set: whether a case is still
    *owed* is the walk's answer to give (``dropped_owed_nothing``), so the
    universe costs corpus reads only — and it starts from
    :func:`fedcourtsai.corpus.open_unexcluded_case_ids`, which answers the
    ``predict_excluded`` latch in SQL, so rows are hydrated only for the few
    thousand unexcluded cases rather than for the whole open-event set.
    """
    universe: set[str] = set()
    for case_id in corpus.open_unexcluded_case_ids(conn, court="scotus"):
        row = corpus.get_row(conn, case_id)
        if row is None or row.predict_excluded:
            continue
        funded_by_selection = row.salience_selected or row.case_id in merits_open
        if not funded_by_selection and row.case_id not in predicted:
            continue
        if not _row_in_predict_scope(conn, row, cohort_completion=not funded_by_selection):
            continue
        court, docket_str = row.case_id.split("/", 1)
        if forecastable_event_ids(conn, court, int(docket_str), today=day):
            universe.add(row.case_id)
    return frozenset(universe)


def _reconcile(
    universe: frozenset[str], log: _DispositionLog, *, cap_reached: bool
) -> CaseReconciliation:
    """Check the walk's dispositions against the universe, case by case."""
    buckets: dict[str, int] = {}
    unaccounted: list[str] = []
    multiply: list[str] = []
    for case_id in sorted(universe):
        filed = log.by_case.get(case_id, [])
        if not filed:
            unaccounted.append(case_id)
        elif len(filed) > 1:
            multiply.append(case_id)
        else:
            buckets[filed[0].value] = buckets.get(filed[0].value, 0) + 1
    outside = sorted(
        case_id
        for case_id, filed in log.by_case.items()
        if case_id not in universe and any(d in _ADMITTED_DISPOSITIONS for d in filed)
    )
    return CaseReconciliation(
        universe=len(universe),
        buckets=buckets,
        unaccounted=tuple(unaccounted),
        multiply_accounted=tuple(multiply),
        admitted_outside_universe=tuple(outside),
        cap_reached=cap_reached,
    )


@dataclass(frozen=True)
class PredictBacklog:
    """What one predict-backlog derivation found, having written nothing.

    The predict mirror of :class:`EvaluateBacklog`, with one asymmetry that is
    the whole point of the class: it has no queueing/stamping consumer beside
    it. The live channel's selection sweep still owns the pull lane's predict
    queue and its ``predict_queued_at`` stamp, because the sweep re-polls each
    candidate before queueing it and the stamp is a corpus write. This scan is
    for the caller with no corpus-write credentials at all — the predict
    stage's own schedule, which reads the committed record and derives its fan-out
    from it.

    The three **hold** counts are the derivation's other output, and they are
    counted over the *owed* population alone — a candidate is only counted as
    held if, but for the hold, it would have produced an entry. That is what
    makes them mean something: "work this lane owes and cannot mint yet",
    rather than "candidates that fell out somewhere", which the ordinary
    admission rules already drop by the hundred. Every hold clears on its own
    as another lane advances or the docket moves, which is why they are
    reported at all — an empty
    backlog otherwise reads the same whether the queue is drained or every owed
    case is waiting on a lane this one cannot drive.

    - ``held_stale`` — the case's corpus row is older than
      :data:`BACKLOG_MAX_POLL_AGE_DAYS`. Clears at the case's next live poll.
    - ``held_unswept`` — the pull lane has never queued the case *and* it has
      no stored documents, so provisioning has not been attempted for it.
      Clears when run-pull sweeps it.
    - ``held_decided`` — the case's latest stored snapshot already discloses
      the outcome of every event it is owed
      (:func:`~fedcourtsai.pipeline.outcome.forward_leakage`), so provisioning
      would refuse each of its forward cells. Clears when the events resolve,
      or when a newer snapshot stops disclosing them — which, for a scan false
      positive, is not until the docket itself moves. ``decided_events`` names
      every dropped ``(case_id, event_id, reason)``, including events dropped
      from a case that is still derived, so each drop is traceable to its
      docket and the entry that tripped the scan.

    The classes are first-match, in that order, so a case in several counts
    once, under the first; the sum is the true held total.

    ``cap_reached`` says the scan hit ``cap`` rather than exhausting the
    candidates, so every hold count is **censored** and a reader quoting a hold
    count without it would be quoting a lower bound as a total. It covers two
    stopping shapes, since the re-predict rule gave the cap two effects: the
    walk breaking outright (the cap full of never-predicted work, so nothing
    past it is examined at all), and the milder one where the walk continues but
    stops evaluating re-predict grounds — candidates past that point are still
    examined for never-predicted cells, and a re-owed-only case among them is
    skipped silently rather than counted as held.

    ``day`` is the date the derivation ran under, carried so a reader can say
    which staleness horizon it filtered on.

    ``reowed_events`` counts the entries' ``reopened`` events across the whole
    derivation — the pre-freeze re-predict rule's own contribution, reported
    apart from the total because it is spend on events the ledger already
    covers and a reader deciding whether to let a cycle run needs the two
    numbers separately. Censored by ``cap_reached`` exactly as the holds are.

    ``reconciliation`` is the case-grain check that nothing fell out of the
    derivation unrecorded (:class:`CaseReconciliation`); ``None`` only when the
    derivation was disabled (``cap <= 0``) and examined nothing.
    """

    entries: tuple[BacklogEntry, ...]
    day: date
    held_stale: int = 0
    held_unswept: int = 0
    held_decided: int = 0
    decided_events: tuple[tuple[str, str, str], ...] = ()
    cap_reached: bool = False
    reconciliation: CaseReconciliation | None = None

    @property
    def case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries)

    @property
    def reowed_events(self) -> int:
        return sum(len(entry.reopened) for entry in self.entries)


def _predict_backlog_candidates(
    conn: corpus.ReadConnection,
    *,
    seen: set[str],
    predicted: frozenset[str],
    merits_open: set[str],
    log: _DispositionLog,
) -> list[tuple[corpus.CorpusRow, bool]]:
    """The rows :func:`derive_predict_backlog` may spend a cap slot on, stalest first.

    Steps 1 through 5 of that function's admission list — everything decidable
    from the row and the two bulk reads, before any per-case ledger or document
    work. Each row is paired with the ``cohort_only`` flag saying it was admitted
    on the cohort-completion ground alone, which is what narrows its events.

    Driven from the open-event set, which on a SCOTUS corpus is very nearly
    every case: this is a whole-court walk, and calling it anything else would
    overstate it. What it avoids is **hydrating a row per case** — the walk
    materializes case *ids* and then fetches only the rows that survive the
    cheap set membership tests, so peak memory is a list of ids rather than a
    list of :class:`~fedcourtsai.corpus.CorpusRow` models. The bound the drive
    does give is a real one, just narrower than "only the work": a case with no
    open event cannot be owed a forecast and never becomes a candidate.

    Ordering is the live sweep's own rotation key with the queue stamp in
    front: stalest ``predict_queued_at`` first (never-queued sorts first), then
    least-recently-observed, then ``case_id``. The middle key matters because
    the first is ``None`` for most of the set — without it a never-queued
    candidate would be ordered by the lexical accident of its docket number.

    Every row it turns away is filed on ``log`` with the reason, so the case
    reconciliation can tell a reasoned drop from a silent one.
    """
    open_case_ids: list[str] = []
    for event in corpus.iter_open_events(conn, court="scotus"):
        if not open_case_ids or open_case_ids[-1] != event.case_id:
            # The iterator is `(case_id, event_id)`-ordered, so a case's events
            # arrive contiguously and the last id seen is the whole dedupe.
            open_case_ids.append(event.case_id)

    candidates: list[tuple[corpus.CorpusRow, bool]] = []
    for case_id in open_case_ids:
        if case_id in seen:
            log.record(case_id, CaseDisposition.dropped_already_queued)
            continue
        row = corpus.get_row(conn, case_id)
        if row is None or row.predict_excluded:
            log.record(case_id, CaseDisposition.dropped_excluded)
            continue
        # The sweep's candidate filter, verbatim, so admission and narrowing
        # cannot disagree: a row neither selection nor the merits bypass admits
        # is here on the cohort ground alone, and only such a row is narrowed.
        cohort_only = not row.salience_selected and case_id not in merits_open
        if cohort_only and case_id not in predicted:
            log.record(case_id, CaseDisposition.dropped_not_funded)
            continue
        if not _row_in_predict_scope(conn, row, cohort_completion=cohort_only):
            log.record(case_id, CaseDisposition.dropped_excluded)
            continue
        candidates.append((row, cohort_only))

    # Stalest first, so the backlog drains fairly under the cap; a never-queued
    # case (predict_queued_at is None) sorts first, and among those the
    # least-recently-observed leads — the same rotation order the live sweep
    # drains in, so the two lanes never disagree about which case is next.
    candidates.sort(
        key=lambda pair: (
            pair[0].predict_queued_at or date.min,
            _last_observed(pair[0]) or date.min,
            pair[0].case_id,
        )
    )
    return candidates


def _reowed_pre_freeze_events(
    conn: corpus.ReadConnection,
    data_root: Path,
    row: corpus.CorpusRow,
    *,
    events: list[str],
    predictor_ids: list[str],
    max_attempts: int,
    day: date,
) -> list[str]:
    """Which of ``events`` are owed a cell again because their cohort is de-counted.

    The pre-freeze re-predict rule. Applied to the case's **whole** admitted
    event list, deliberately overlapping the never-predicted arm rather than
    taking what it left: an event can carry both a predictor that never
    forecast it and predictors whose only cells are de-counted, and that is
    precisely the state a run leaves when one engine quota-fails before a
    revocation. Handing this only the leftovers would mint the missing engine,
    stamp it blessed, and leave its rivals de-counted — a **one-engine frozen
    cohort**, the exact shape
    :func:`fedcourtsai.store.event_has_claimable_prediction` exists to refuse
    and the inverse of the completeness this rule is justified by. So the arms
    overlap at the event grain and stay disjoint at the cell grain, which is
    where it matters: a predictor with no cell is the never-predicted arm's,
    one whose cells are all de-counted is this one's, and no predictor is both.

    Three gates, each answering a different question, and an event must pass
    all three:

    1. **Genuinely forward.** :func:`fedcourtsai.store.forward_refusal_reason_from_parts`
       — the record-side forward gate the fan-out itself applies, reused rather
       than restated: the ledger holds no ``outcome.json``, the corpus does not
       flag the event resolved, and the row's own columns *for this event's
       stage* carry no disposition, resolution date, latched merits judgment or
       merits termination. The last limb is the one a version-blind reading
       would miss: a docket the live channel has polled as decided but whose
       outcome it has not yet written is decided in the corpus and open in the
       ledger, and a "forward" cell minted on it is a replay in forward
       clothing.
    2. **The moment is still open.** :func:`_reopenable_moment` —
       :data:`REPREDICT_MOMENTS`, plus the refusal of a distribution event that
       carries no conference still ahead.
    3. **Every existing cell is de-counted, for at least one predictor.**
       :func:`fedcourtsai.store.predictor_holds_no_counted_prediction`, under
       the same per-cell attempt cap the never-predicted arm takes. A predictor
       already holding a counted cell on the event — a closed window's
       included — is not re-owed one, so an event whose cohort is partly
       counted re-owes only the engines that are not.

    The caller passes the case's whole forecastable set, and for a cohort-only
    candidate this runs **before** the cohort narrowing rather than after it —
    which is the whole of the funding gate's widening: the narrowing governs the
    never-predicted arm, and this rule is asked over the unnarrowed list, so a
    salience-declined case's wholly de-counted events are re-owed alongside a
    funded case's. What the rule never reaches is an event no predictor has
    forecast at all — gate 3 is false with no runs — so it re-opens the
    pre-freeze cohort and opens no *event* the funding gate declined. (At the
    **cell** grain a re-owed event does complete: the fan-out's
    already-predicted skip never drops an engine holding nothing, so an engine
    with no cell on such an event is minted its first one. That is the
    completeness the rule is justified by, not a second widening.)

    The cost of running unnarrowed is small but real and worth naming: a
    cohort-only candidate whose events pass the cheap moment filter now pays one
    `events_for_case` query, a `forward_refusal_reason_from_parts` per surviving
    event and up to one ledger glob per predictor, on events the narrowing would
    previously have dropped for free. The moment filter still runs first and
    alone, so a candidate whose events are all merits, cert/arrival or
    entry-pinned — the common case — pays nothing.
    """
    # The moment filter runs first and alone, because it needs only the row and
    # the register while both gates after it read a store: without this every
    # candidate would pay a `events_for_case` query to have all its events
    # refused for being merits, cert/arrival, or entry-pinned — which is the
    # common case, not the rare one.
    reopenable = [event_id for event_id in events if _reopenable_moment(event_id, row, day=day)]
    if not reopenable:
        return []
    case_events = corpus.events_for_case(conn, row.case_id)
    court, docket_str = row.case_id.split("/", 1)
    docket = int(docket_str)
    reowed: list[str] = []
    for event_id in reopenable:
        refusal = forward_refusal_reason_from_parts(
            data_root, court, docket, event_id, case_events, row
        )
        if refusal is not None:
            continue
        if any(
            predictor_holds_no_counted_prediction(data_root, court, docket, event_id, pid)
            and not _cell_capped(data_root, court, docket, event_id, pid, max_attempts, "predict")
            for pid in predictor_ids
        ):
            reowed.append(event_id)
    return reowed


def _drop_disclosed(
    conn: corpus.ReadConnection,
    case_id: str,
    court: str,
    owed: list[str],
    reowed: list[str],
    dropped: list[tuple[str, str, str]],
) -> tuple[list[str], list[str]]:
    """``owed`` and ``reowed`` less each event the case's latest snapshot answers.

    One snapshot read per case, scanned per event with
    :func:`~fedcourtsai.pipeline.outcome.forward_leakage` — the refusal
    provisioning applies to a forward cell — so the backlog never derives a
    cell provisioning would refuse. Each dropped event is appended to
    ``dropped`` as ``(case_id, event_id, reason)``. A case with no stored
    snapshot keeps its events: provisioning refuses that shape too, but loudly
    and by name (exit 1, no snapshot in the corpus), which a count here would
    turn silent.
    """
    snapshot = corpus.latest_snapshot(conn, case_id)
    if snapshot is None:
        return owed, reowed
    payload = snapshot[1]
    disclosed: dict[str, str] = {}
    for event_id in dict.fromkeys([*owed, *reowed]):
        reason = forward_leakage(payload, court, event_id)
        if reason is not None:
            disclosed[event_id] = reason
    dropped.extend((case_id, event_id, reason) for event_id, reason in disclosed.items())
    return (
        [event_id for event_id in owed if event_id not in disclosed],
        [event_id for event_id in reowed if event_id not in disclosed],
    )


def _timing_hold(
    conn: corpus.ReadConnection, row: corpus.CorpusRow, *, day: date
) -> CaseDisposition | None:
    """The first of the two timing holds an owed case is under, or ``None``.

    Steps 7 and 8 of :func:`derive_predict_backlog`, asked only of a case that
    step 6 found owed.
    """
    observed = _last_observed(row)
    if observed is None or (day - observed).days > BACKLOG_MAX_POLL_AGE_DAYS:
        # Too stale to mint a forward cell from: the sweep would have
        # re-polled and could have diverted this case as decided, and this
        # scan cannot. Clears at the case's next poll.
        return CaseDisposition.held_stale
    provisioning_attempted = row.predict_queued_at is not None or (
        corpus.has_documents_for_case(conn, row.case_id)
    )
    if not provisioning_attempted:
        # Provisioning has never been *attempted* for this case: the pull
        # lane has never queued it (its stamp is the lane's own record that
        # it ran) and nothing is stored. That is the one genuinely
        # timing-only state — the sweep reaches, provisions and stamps such
        # a case — so it is held rather than minted with an empty record/.
        # A queued case is admitted on the lane's word even where its store
        # came up empty: provisioning ran and found nothing, which is a
        # coverage fact for the queued-without-petition metric, not a
        # reason to strand the case forever. Reading it as an exclusion
        # would permanently bar every structurally unprovisionable docket —
        # an application form has no document route at all.
        return CaseDisposition.held_unswept
    return None


def derive_predict_backlog(
    conn: corpus.ReadConnection,
    data_root: Path,
    predictors_path: Path,
    *,
    cap: int,
    max_attempts: int,
    already_queued: set[str] | None = None,
    today: date | None = None,
) -> PredictBacklog:
    """Find the forecasts the committed record still owes, reading only.

    What makes predict level-triggered, the way :func:`derive_evaluate_backlog`
    does for grading. A case is owed a forecast when it is in predict scope,
    funded, and some enabled predictor is missing a prediction for some open
    forecastable event of it — a condition on committed state, so it survives a
    run dropped on the floor, a paused lane, or a round that never ran. Two
    further conditions gate *minting* rather than owing, and the difference is
    load-bearing: a case can be owed and still held.

    This is **not** an extraction of :func:`fedcourtsai.pipeline.live.salience_sweep`
    and must not become one. The sweep's body interleaves network fetches,
    ingest writes, document provisioning, and the queue stamp — every one of
    which this scan is defined by *not* doing — so what the two share is the
    predicate set, applied here read-only over an already-open connection.

    **The admission predicates, in the order they run:**

    1. ``already_queued`` — case ids a caller has already covered this cycle.
    2. The case has a row (an open event whose case row is absent cannot be
       scope-checked, so it is skipped rather than crashed).
    3. ``not row.predict_excluded`` — the cheap row-level scope latch, the
       sweep's own pre-filter.
    4. Funding: selected by salience, **or** carrying an open merits event (the
       Court's own selection outranks the cert-stage funding question), **or**
       already holding a committed prediction somewhere (cohort completion or a
       pre-freeze re-predict, admission only — see the narrowing below).
    5. :func:`_row_in_predict_scope` — the full scope gate the pull and live
       lanes apply at queue time, with ``cohort_completion`` set exactly when
       (4) admitted the row on the cohort ground alone.
    6. **Owed** — some ``(predictor, event)`` cell of the case is either
       unpredicted, or **re-owed under the pre-freeze rule**, and under the
       per-cell attempt cap, over the event list the cohort narrowing below
       leaves.

    Then three **holds**, which run only on a case step 6 found owed, so every
    held case is one this lane genuinely owes and cannot mint yet:

    7. **Record freshness** — the case was observed by either ingestion channel
       within :data:`BACKLOG_MAX_POLL_AGE_DAYS` (:func:`_last_observed`).
       Counted on ``held_stale``. The sweep re-polls before it queues and can
       divert a now-decided docket; this scan cannot, so the record's age is
       the only guard it has against a forward cell on a case whose answer is
       already public.
    8. **Provisioning attempted** — the case has stored documents *or* carries
       a ``predict_queued_at`` stamp. Counted on ``held_unswept``. The stamp is
       the pull lane's own record that it queued the case, and the sweep
       provisions at queue time, so a stamp is proof provisioning **ran** —
       whatever it found. Only the never-queued-and-unstored class is held, and
       that class is genuinely timing-only: the sweep reaches it, provisions
       it, and stamps it. Reading document presence as the predicate instead
       would conflate "not yet provisioned" with "provisioned, found nothing"
       and permanently bar every docket with no document route at all, the
       application form among them — the interim lane would never be admitted.
       An admitted case whose store is empty mints a cell with a thin
       ``record/``; that is the queued-without-petition coverage metric's
       problem to report, not this predicate's to exclude.
    9. **Outcome not disclosed** — per event, the case's latest stored snapshot
       does not already show that event's outcome
       (:func:`~fedcourtsai.pipeline.outcome.forward_leakage`, the scan
       provisioning refuses a forward cell on). An event it flags is dropped;
       a case left with none is counted on ``held_decided``. This is the plan
       seam's copy of the live routing's decided-docket diversion, which keeps
       such a docket off the queue but records nothing the backlog can read.

    **Case-grain reconciliation.** Every step above that turns a case away files
    it under a :class:`CaseDisposition`, and so does every step that derives or
    holds one. Beside the walk, :func:`_predict_universe` computes the cases the
    derivation must account for — open forecastable event, predict scope,
    funded — from the leaf predicates alone, and ``reconciliation`` checks that
    each universe case landed in exactly one bucket. A predicate added to the
    walk that drops an owed case without filing it shows up there as
    **unaccounted**, by name, instead of as a quietly shorter backlog. The
    universe costs one query over the open events of unexcluded rows plus the
    corpus reads of the funded ones; it reads no ledger beyond the bulk
    prediction set.

    Steps 1 through 5 filter, then candidates sort **stalest first** (see
    :func:`_predict_backlog_candidates`) and steps 6 through 9 run inside the
    ``cap`` — a held case costs no cap slot, but the loop still stops at the
    cap, so every hold count is censored by it and ``cap_reached`` says
    whether it was. Ordering the owed check ahead of the holds is also what
    keeps the store reads cheap under the corpus split: step 8 reads the store
    only for an owed, fresh, never-queued case, and step 9 reads one snapshot
    per owed case that passed the other holds — a small fraction of the
    candidate set rather than all of it. ``cap`` bounds model spend and PR
    volume: each queued case fans out one cell per predictor still owed the
    event.

    The stalest-first order keys on the pull/live lane's stamp, which that lane
    refreshes on an active docket every day, so when more cases are owed than
    ``cap`` the dockets moving fastest are derived last. Under the cap nothing
    is lost; above it, they wait for the older owed cases to drain.

    **A ``predict_queued_at`` stamp holds nothing off.** The pull and live
    lanes write it and mint nothing, so this derivation is the only lane that
    turns a queued case into cells. A debounce on today's stamp would hold off
    exactly the cases the live channel is watching most closely: it re-stamps a
    case on each day's first poll that sees docket activity, and its morning
    windows precede both scheduled rounds, so an active application or petition
    would be skipped at every round for as long as its docket kept moving. What
    makes a repeated derivation safe is the fan-out's per-``(predictor, event)``
    already-predicted skip — the ledger-side idempotency
    :func:`derive_evaluate_backlog` rests on too — with the stranded-run guard
    covering a round whose collect has not merged.

    run-pull stays the sole provisioner, and the property that gives is a
    **throughput bound, not a latency one**: this backlog can never outrun
    run-pull's provisioning rate — the sweep's per-window cap plus the other
    provisioning paths' own bounds — so a held set larger than that rate clears
    over as many windows as it takes rather than by the next one.

    The queued event list is per-event, not per-case, and it drops an event on
    **two** grounds: every enabled predictor has already predicted it, or every
    predictor still missing it has hit ``max_attempts``. The two are not
    equally settled. The already-predicted arm changes nothing — the predict
    matrix's per-``(predictor, event)`` skip would drop those cells anyway, so
    narrowing here only spares the fan-out a case that would arrive empty. The
    attempt-capped arm is **stricter than the live sweep**, deliberately: the
    sweep's owed check is per case, so a case whose only gap is poison-pilled
    is still queued and the matrix still mints those cells. Here the cap
    decides admission, which is what ``predict.max_attempts_per_cell`` exists
    to do — an unattended lane that re-derives a cell failing every attempt
    would spend on it every cycle forever, and no stamp holds it back. The cost
    of the stricter reading is that raising the ceiling, not a re-queue, is what
    reopens such a cell.

    **The pre-freeze re-predict rule.** The owed check above is otherwise
    version-blind — a committed prediction is a committed prediction — and that
    is a hole a de-count opens: a cell stamped before its digest's counting
    window opened, under a label whose digests stay de-counted (every label
    before ``proc-v8``), or inside a revoked window counts nowhere, so an event
    whose whole cohort is such cells holds forecasts no claimable board will
    ever count while the deriver reports it covered. A supersession opens no
    such hole: it closes windows, whose cells keep counting, so it re-owes
    nothing. When the event then resolves,
    the evaluate lane grades it, :func:`fedcourtsai.store.stratify` drops every
    result as out of frozen scope, and the event is consumed for nothing. So an
    event is owed a cell **again** when it is genuinely forward, its declared
    moment is still open, and some predictor's every committed cell on it is
    de-counted — :func:`_reowed_pre_freeze_events`, which spells
    the three gates out. It is a rule over committed state like every other
    predicate here: no flag, no dispatch input, nothing to remember to set.

    A re-predict **replaces** rather than adds. The older cell stays under its
    own run id and nothing edits it; provisioning stages the newest resolvable
    run per predictor
    (:func:`fedcourtsai.blinding.latest_prediction_dirs`) and the evaluation
    names the ``prediction_run_id`` it graded, so the new cell is the one the
    board reads and the old one is history. Re-owed cells are ordered after
    never-predicted ones at both grains — within an entry's event list, and
    between entries — so the rule can never starve the ordinary backlog under
    the cap.

    A **cohort-only** candidate — one the salience round declined, here only
    because it already holds a prediction somewhere — is narrowed to the events
    whose cohort a claimable board will count
    (:func:`fedcourtsai.store.event_has_claimable_prediction`), so the case
    earns its missing engines on work already paid for and never a one-engine
    comparison on a cohort outside the frozen process scope. That narrowing
    governs the **never-predicted arm only**, and that is the funding gate's one
    widening: the re-predict rule is asked over the candidate's whole
    forecastable set, so a declined case's wholly de-counted events are
    re-owed like a funded case's. The ground is the narrowing's own argument
    rather than a waiver of it — what it refuses is a *partial* completion, and
    a wholly de-counted cohort is re-minted for every engine at once. Without this the
    forward cohort would be re-predicted only on its funded half, and the rest
    graded on resolution and dropped from the frozen board.

    The widening is bounded by the rule: an event no predictor has forecast is
    not re-owed, so no *event* the funding gate declined is opened, and the
    salience selection itself does not move. At the **cell** grain a re-owed
    event does complete — an engine holding nothing on it is minted its first
    cell, because the fan-out's already-predicted skip never drops such an
    engine — which is the completeness the rule is justified by. Such a case
    still sorts with the re-owed work, not with the never-predicted lead group:
    what classifies it is ``owed``, which the narrowing governs.

    Like the evaluate deriver, the scan is driven from the **open-event set**
    (``corpus.iter_open_events``) with a point query per candidate case. On a
    SCOTUS corpus that set covers very nearly every row, so this is a
    whole-court walk and the bound it gives is narrower than "only the work":
    what it avoids is hydrating a :class:`~fedcourtsai.corpus.CorpusRow` per
    case. The walk materializes case **ids**, and only the ids surviving the
    cheap membership tests are ever read as rows — so peak memory scales with
    the id list, not with the model-shaped corpus, on a SCOTUS slice of
    hundreds of thousands of rows that only grows. Either way the access
    pattern is the wrong shape for a fetch-by-range backend, which is why a
    scheduled caller pulls the corpus and reads it locally.

    The connection is a :class:`~fedcourtsai.corpus.ReadConnection`: every read
    here is typed to it, so no writer-only API (``commit``,
    ``stamp_predict_queued``) is reachable through the parameter. That is a
    one-method protocol, not a proof — what keeps the corpus of record intact
    is that write credentials live only in the writer jobs.

    ``max_attempts`` is the poison-pill backstop, counted from the committed
    ``attempt.json`` failure facts at the predict seam: a ``(predictor, event)``
    cell recorded failed that many times is not re-derived, so a cell that fails
    every attempt cannot re-derive forever. Because the cap is per cell it never
    lets one exhausted engine suppress a sibling predictor still owed the same
    event; ``max_attempts == 0`` disables it.
    """
    day = today or date.today()
    if cap <= 0:
        return PredictBacklog(entries=(), day=day)
    seen = already_queued or set()
    predictor_ids = [p.id for p in enabled_predictors(predictors_path)]
    # Two bulk reads rather than a probe per row, exactly as the sweep takes
    # them: one ledger glob for the cohort-completion admission ground, and one
    # small ordered slice of the partial open-events index for the merits bypass.
    predicted = predicted_case_ids(data_root)
    merits_open = corpus.merits_open_case_ids(conn)
    # The universe first, and from its own reads, so the walk below cannot
    # shape it; the log keeps only what the reconciliation needs.
    universe = _predict_universe(conn, predicted=predicted, merits_open=merits_open, day=day)
    log = _DispositionLog(universe)
    candidates = _predict_backlog_candidates(
        conn, seen=seen, predicted=predicted, merits_open=merits_open, log=log
    )

    entries: list[BacklogEntry] = []
    reowed_only: list[BacklogEntry] = []
    decided: list[tuple[str, str, str]] = []
    cap_reached = False
    for position, (row, cohort_only) in enumerate(candidates):
        # Two different budgets, and the difference is what stops the re-predict
        # rule starving the ordinary backlog. The **walk** stops only when the
        # cap is full of never-predicted work, because until then a later
        # candidate may still carry some and must be reached. What the filled
        # budget stops is the re-predict evaluation: past it a candidate is
        # examined for never-predicted cells alone, which is the work this loop
        # already did per candidate. The cost is real and worth naming: once the
        # budget fills with re-owed work the walk runs to the end of the
        # candidate list rather than stopping, paying one `forecastable_event_ids`
        # query and the per-cell ledger globs on each remaining candidate. That
        # is the price of not starving the ordinary backlog, and it is bounded
        # by the candidate set, which the funding and cohort filters already cut
        # to a few hundred rows.
        budget_full = len(entries) + len(reowed_only) >= cap
        if budget_full and len(entries) >= cap:
            cap_reached = True
            # Censored, and filed as such: every candidate from here on was
            # never examined, so none of them may read as unaccounted.
            for unexamined, _ in candidates[position:]:
                log.record(unexamined.case_id, CaseDisposition.dropped_cap_reached)
            break
        cap_reached = cap_reached or budget_full
        court, docket_str = row.case_id.split("/", 1)
        docket = int(docket_str)
        events = forecastable_event_ids(conn, court, docket, today=day)
        # The re-predict rule runs **before** the cohort narrowing below,
        # because it is one of that narrowing's two admission grounds: an event
        # is kept when a claimable board already counts its cohort, or when the
        # rule re-owes it. So it is asked over the case's whole forecastable
        # set, not over what the narrowing left. The whole admitted list is also
        # what it takes on a funded case, and for a second reason: an event can
        # be owed a never-predicted cell for one engine and a re-predict for
        # another, and minting only the first would build a one-engine frozen
        # cohort. See `_reowed_pre_freeze_events` — the arms overlap per event
        # and stay disjoint per cell.
        reowed = (
            []
            if budget_full
            else _reowed_pre_freeze_events(
                conn,
                data_root,
                row,
                events=events,
                predictor_ids=predictor_ids,
                max_attempts=max_attempts,
                day=day,
            )
        )
        if cohort_only:
            # The cohort-completion narrowing, unchanged, and it governs the
            # **never-predicted** arm alone: a salience-deferred case reaches
            # this scan only because it already holds a prediction somewhere,
            # and this keeps only the events a claimable board already counts,
            # so the case earns its missing engines on work already paid for
            # and never new cells on its untouched events.
            #
            # The re-predict rule is deliberately **not** narrowed by it — that
            # is the funding gate's one widening, and it is carried by the call
            # above taking the case's whole forecastable set rather than by a
            # second ground here. Adding a ground here would be worse than
            # redundant: a re-owed event reaches `entry.events` and
            # `entry.reopened` regardless (they are built from `owed + reowed`),
            # so the only thing it would change is letting a re-owed event's
            # *never-predicted* engine into `owed` — which would promote a
            # salience-declined case into the never-predicted lead group and
            # break the priority this loop's two lists exist to keep. That
            # engine's first cell is minted either way: the fan-out's
            # already-predicted skip never drops an engine holding nothing, so
            # the cohort still completes.
            events = [
                event_id
                for event_id in events
                if event_has_claimable_prediction(data_root, court, docket, event_id)
            ]
        owed = [
            event_id
            for event_id in events
            if any(
                not event_has_predictions(data_root, court, docket, event_id, predictor_id=pid)
                and not _cell_capped(
                    data_root, court, docket, event_id, pid, max_attempts, "predict"
                )
                for pid in predictor_ids
            )
        ]
        # The owed check runs FIRST, and the two timing holds after it, so a
        # hold is only counted where it is the sole thing between the case and
        # an entry. Counted the other way round the figures would be dominated
        # by cases the owed check drops anyway, and "held, still owed a
        # forecast" would be false of almost every one of them.
        if not owed and not reowed:
            # Past a full re-predict budget the re-owed arm was never asked, so
            # "owed nothing" is unproven there and the case is filed as censored.
            log.record(
                row.case_id,
                CaseDisposition.dropped_cap_reached
                if budget_full
                else CaseDisposition.dropped_owed_nothing,
            )
            continue
        hold = _timing_hold(conn, row, day=day)
        if hold is not None:
            log.record(row.case_id, hold)
            continue
        # The same textual disclosure scan provisioning runs on the same newest
        # snapshot, asked here so an owed event whose docket already shows its
        # outcome is never derived: provisioning would refuse the cell, but only
        # after the round spent a runner on it, and the event stays owed — and
        # re-derived — at every round until its outcome is recorded. Keyed per
        # event, because one docket discloses different events' outcomes: the
        # grant that answers a cert event opens the merits event beside it.
        owed, reowed = _drop_disclosed(conn, row.case_id, court, owed, reowed, decided)
        if not owed and not reowed:
            log.record(row.case_id, CaseDisposition.held_decided)
            continue
        # Never-predicted events lead the list, events re-owed and nothing else
        # follow, so a downstream reader that truncates an event list keeps the
        # ordinary backlog first — the same priority the two entry lists give at
        # the case grain. An event in both arms is already in `owed` and is not
        # repeated; `reopened` still names it, since the licence it carries is
        # read per cell and its de-counted engines need it.
        entry = BacklogEntry(
            case_id=row.case_id,
            court=court,
            docket=docket,
            events=tuple(owed) + tuple(e for e in reowed if e not in owed),
            reopened=tuple(reowed),
        )
        if owed:
            entries.append(entry)
            if len(entries) + len(reowed_only) > cap:
                # A never-predicted case displaces the stalest-last re-owed one,
                # which is the priority stated below made to hold under the cap
                # rather than only in the returned order.
                displaced = reowed_only.pop()
                log.reclassify(displaced.case_id, CaseDisposition.dropped_cap_reached)
        else:
            reowed_only.append(entry)
        log.record(row.case_id, CaseDisposition.derived)

    ordered = entries + reowed_only
    for overflow in ordered[cap:]:
        log.reclassify(overflow.case_id, CaseDisposition.dropped_cap_reached)

    return PredictBacklog(
        # Cases owed a never-predicted cell come first, and a case owed only
        # re-predicts follows every one of them, each group keeping the
        # stalest-first order it was walked in. Under the cap the re-owed end is
        # what gives way, at both ends of the loop: a filled budget stops new
        # re-owed cases being admitted, and a never-predicted case found
        # afterwards displaces the stalest-last re-owed one. So the rule cannot
        # starve the ordinary backlog. The slice is defence, not logic: the loop
        # invariant already holds the two lists to `cap` between them.
        entries=tuple(ordered[:cap]),
        day=day,
        # The hold counts are read off the disposition log, which keeps every
        # held case whatever the universe says (holding is an admission), so
        # the counts and the reconciliation cannot disagree about a hold.
        held_stale=log.count(CaseDisposition.held_stale),
        held_unswept=log.count(CaseDisposition.held_unswept),
        held_decided=log.count(CaseDisposition.held_decided),
        decided_events=tuple(decided),
        cap_reached=cap_reached,
        reconciliation=_reconcile(universe, log, cap_reached=cap_reached),
    )


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
        events = forecastable_events(corpus_db_path, court, docket)
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
