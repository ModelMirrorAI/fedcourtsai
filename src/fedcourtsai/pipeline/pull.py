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
from ..store import event_has_claimable_prediction, forecastable_event_ids, forecastable_events
from .events import AmbiguousEntry, extract_events
from .ingest import from_api_docket, upsert_to_corpus
from .outcome import (
    UnrecordedOutcome,
    disposition_basis,
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
    """The three downstream handoffs a ``pull-all`` run produces.

    Each entry is a JSON-serializable mapping shaped exactly as the ``run-pull``
    workflow consumes it (the ``jq`` fields in ``run-pull.yml``): ``predict`` and
    ``evaluate`` entries carry ``court`` / ``docket`` / ``events``; ``unrecorded``
    adds the maintainer-facing ``reason`` the pipeline-runs dashboard surfaces.
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
    # `relist_requeue_cooldown_days` of its last predict queue — administrative
    # churn, not a materially different posture, while capacity is enforced.
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
    """

    case_id: str
    court: str
    docket: int
    events: tuple[str, ...]

    def as_queue_entry(self) -> dict[str, object]:
        """The mapping shape a ``PullQueues`` list carries to the workflow."""
        return {"court": self.court, "docket": self.docket, "events": list(self.events)}


@dataclass(frozen=True)
class EvaluateBacklog:
    """What one backlog derivation found, before anything is queued or stamped.

    Separating the derivation from its consumption is what lets the same scan
    serve two callers with different authority over the corpus of record: the
    pull seams queue *and* stamp, while the evaluate stage's own schedule only
    reads. That schedule runs outside the writer jobs, so a stamp it wrote
    could never be pushed — it would mutate the runner's pulled copy and die
    with it — and it needs none (see :func:`derive_evaluate_backlog`).

    ``day`` is the date the derivation ran under, carried so a caller that does
    stamp writes the same value the debounce filtered on.
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
    back, so a caller that stamps drains its backlog stalest-first and skips
    what it queued this cycle. The debounce runs one way only: it holds a
    scheduled derivation back from a case the pull lane stamped this morning,
    while a stamp-free caller leaves nothing for the pull lane to skip on, and
    orders on a key it never advances — the same head of the queue re-derives
    each cycle until the ledger moves under it.

    The connection is a :class:`~fedcourtsai.corpus.ReadConnection`, which keeps
    this scan on the read seam: every read here — ``iter_resolved_events``,
    ``get_row``, ``out_of_scope_reason_full`` — is typed to it, so a caller may
    pass a ranged connection and no writer-only API (``commit``,
    ``stamp_evaluate_queued``) is reachable through the parameter. It is a
    one-method protocol, not a proof: what actually keeps the corpus of record
    intact is that write credentials live only in the writer jobs. Stamping is
    the caller's, on its own concrete connection (:func:`evaluate_backlog`).

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
    its *other* owed events to the next cycle. That is fine: they are debounced
    anyway, and re-derived stalest-first later. For SCOTUS, where
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
    """Queue the owed gradings a pull cycle found, and stamp what it queued.

    The pull lane's consumption of :func:`derive_evaluate_backlog`: it appends
    to ``queues.evaluate`` (the same list the poll seams feed, so the workflow
    consumes one queue), counts the additions in ``evaluate_from_backlog``, and
    stamps ``evaluate_queued_at`` on the queued cases so the next cycle's
    stalest-first ordering rotates past work already handed off. The stamp is a
    corpus write, which is why it lives here rather than in the deriver: this
    runs inside the pull writer job, the one place that holds corpus-write
    credentials.
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

    if derived.case_ids:
        with corpus.connect(corpus_db_path) as conn:
            corpus.stamp_evaluate_queued(conn, derived.case_ids, derived.day)


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

    ``day`` is the date the derivation ran under, carried so a reader can say
    which day's debounce stamps it filtered on.

    The two **hold** counts are the derivation's other output, and they are
    counted over the *owed* population alone — a candidate is only counted as
    held if, but for the hold, it would have produced an entry. That is what
    makes them mean something: "work this lane owes and cannot mint yet",
    rather than "candidates that fell out somewhere", which the ordinary
    admission rules already drop by the hundred. Both holds clear on their own
    as another lane advances, which is why they are reported at all — an empty
    backlog otherwise reads the same whether the queue is drained or every owed
    case is waiting on a lane this one cannot drive.

    - ``held_stale`` — the case's corpus row is older than
      :data:`BACKLOG_MAX_POLL_AGE_DAYS`. Clears at the case's next live poll.
    - ``held_unswept`` — the pull lane has never queued the case *and* it has
      no stored documents, so provisioning has not been attempted for it.
      Clears when run-pull sweeps it.

    ``cap_reached`` says the scan stopped on ``cap`` rather than exhausting the
    candidates, so both counts are **censored**: candidates past the break were
    never examined and are in neither figure. A reader quoting a hold count
    without it would be quoting a lower bound as a total.

    ``day`` is the date the derivation ran under, carried so a reader can say
    which day's debounce stamps and which staleness horizon it filtered on.
    """

    entries: tuple[BacklogEntry, ...]
    day: date
    held_stale: int = 0
    held_unswept: int = 0
    cap_reached: bool = False

    @property
    def case_ids(self) -> tuple[str, ...]:
        return tuple(entry.case_id for entry in self.entries)


def _predict_backlog_candidates(
    conn: corpus.ReadConnection,
    *,
    seen: set[str],
    predicted: frozenset[str],
    merits_open: set[str],
    day: date,
) -> list[tuple[corpus.CorpusRow, bool]]:
    """The rows :func:`derive_predict_backlog` may spend a cap slot on, stalest first.

    Steps 1 through 6 of that function's admission list — everything decidable
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
            continue
        row = corpus.get_row(conn, case_id)
        if row is None or row.predict_queued_at == day or row.predict_excluded:
            continue
        # The sweep's candidate filter, verbatim, so admission and narrowing
        # cannot disagree: a row neither selection nor the merits bypass admits
        # is here on the cohort ground alone, and only such a row is narrowed.
        cohort_only = not row.salience_selected and case_id not in merits_open
        if cohort_only and case_id not in predicted:
            continue
        if not _row_in_predict_scope(conn, row, cohort_completion=cohort_only):
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
    run dropped on the floor, a paused lane, or a handoff that never fired. Two
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
    3. ``row.predict_queued_at != day`` — the one-way debounce. This lane writes
       no stamp, so it honours the one the pull/live lane wrote (a case handed
       off this morning is not re-derived tonight) and leaves none of its own.
    4. ``not row.predict_excluded`` — the cheap row-level scope latch, the
       sweep's own pre-filter.
    5. Funding: selected by salience, **or** carrying an open merits event (the
       Court's own selection outranks the cert-stage funding question), **or**
       already holding a committed prediction somewhere (cohort completion,
       admission only — see the narrowing below).
    6. :func:`_row_in_predict_scope` — the full scope gate the pull and live
       lanes apply at queue time, with ``cohort_completion`` set exactly when
       (5) admitted the row on the cohort ground alone.
    7. **Owed** — some ``(predictor, event)`` cell of the case is both
       unpredicted and under the per-cell attempt cap, over the event list the
       cohort narrowing below leaves.

    Then two **timing holds**, which run only on a case step 7 found owed, so
    every held case is one this lane genuinely owes and cannot mint yet:

    8. **Record freshness** — the case was observed by either ingestion channel
       within :data:`BACKLOG_MAX_POLL_AGE_DAYS` (:func:`_last_observed`).
       Counted on ``held_stale``. The sweep re-polls before it queues and can
       divert a now-decided docket; this scan cannot, so the record's age is
       the only guard it has against a forward cell on a case whose answer is
       already public.
    9. **Provisioning attempted** — the case has stored documents *or* carries
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

    Steps 1 through 6 filter, then candidates sort **stalest first** (see
    :func:`_predict_backlog_candidates`) and steps 7 through 9 run inside the
    ``cap`` — a held case costs no cap slot, but the loop still stops at the
    cap, so both hold counts are censored by it and ``cap_reached`` says
    whether they were. Ordering the owed check ahead of the holds is also what
    keeps the document probe cheap under the corpus split: step 9 reads the
    store only for an owed, fresh, never-queued case, which is a small fraction
    of the candidate set rather than all of it. ``cap`` bounds model spend and
    PR volume: each queued case fans out one cell per predictor still owed the
    event.

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

    A **cohort-only** candidate is narrowed further,
    to the events whose cohort a claimable board will count
    (:func:`fedcourtsai.store.event_has_claimable_prediction`) — the sweep's
    two bounds, unchanged: a case the funding gate declined earns its missing
    engines on an event already paid for, never new cells on its other events,
    and never a one-engine comparison on an event whose whole cohort sits
    outside the frozen process scope.

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
    candidates = _predict_backlog_candidates(
        conn, seen=seen, predicted=predicted, merits_open=merits_open, day=day
    )

    entries: list[BacklogEntry] = []
    held_stale = 0
    held_unswept = 0
    cap_reached = False
    for row, cohort_only in candidates:
        if len(entries) >= cap:
            cap_reached = True
            break
        court, docket_str = row.case_id.split("/", 1)
        docket = int(docket_str)
        events = forecastable_event_ids(conn, court, docket, today=day)
        if cohort_only:
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
        if not owed:
            continue
        observed = _last_observed(row)
        if observed is None or (day - observed).days > BACKLOG_MAX_POLL_AGE_DAYS:
            # Too stale to mint a forward cell from: the sweep would have
            # re-polled and could have diverted this case as decided, and this
            # scan cannot. Clears at the case's next poll.
            held_stale += 1
            continue
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
            held_unswept += 1
            continue
        entries.append(
            BacklogEntry(case_id=row.case_id, court=court, docket=docket, events=tuple(owed))
        )

    return PredictBacklog(
        entries=tuple(entries),
        day=day,
        held_stale=held_stale,
        held_unswept=held_unswept,
        cap_reached=cap_reached,
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
