"""The SCOTUS live channel's poller: discover and refresh pending petitions.

The live counterpart of :mod:`fedcourtsai.pipeline.pull`, fed by the
supremecourt.gov docket JSON (:class:`fedcourtsai.supremecourt.SupremeCourtClient`)
instead of the CourtListener REST API — minutes-to-hours fresh, budget-free.
Deterministic, no agent. Each cycle:

- **Discovery** probes the current Term's next unseen docket serials per
  numbering stream (paid petitions from 1, IFP from 5001) until the frontier —
  consecutive misses — and onboards each served petition, persisting a per-Term
  cursor (:func:`fedcourtsai.corpus.get_live_cursor`) so the next cycle resumes
  where this one stopped.
- **Refresh** re-polls the pending modern-cert watchlist
  (:func:`fedcourtsai.corpus.live_rotation` — recent Terms first, then stalest)
  and detects resolution: the disposition orders ride in the proceedings text,
  machine-matchable per the reachability probe, so a decided petition lands its
  ``outcome.json`` deterministically through the same
  :func:`~fedcourtsai.pipeline.outcome.resolve_case` seam pull uses.

Identity is reconciled before any row is minted: a petition already in the
corpus (by normalized Term-form docket number) is **enriched** under its
existing ``case_id``; only a genuinely unseen one mints the deterministic
reserved-range live id. Raw JSON is stored as the dated snapshot — the same
store, change detection, and provisioning surface as every other channel.

Queue handoffs reuse pull's shapes (:class:`~fedcourtsai.pipeline.pull.PullQueues`):
an in-scope petition queues ``predict`` on a **distribution transition** —
newly distributed for a conference, or relisted to a new one — the cert-calendar
analogue of ``predict_on_change_only``; a newly resolved case queues
``evaluate`` when the ledger holds a prediction to score (the live sweeps
resolve plenty of never-predicted petitions — nothing to score, no cells); an
ambiguous resolution lands on ``unrecorded`` for the run log.
"""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import httpx

from .. import corpus, ids
from ..config import LiveConfig, PredictScope, SalienceConfig
from ..matrix import event_has_predictions
from ..store import open_events
from ..supremecourt import (
    IFP_SERIAL_BASE,
    SupremeCourtClient,
    live_docket_id,
    parse_scotus_docket_number,
)
from .documents import fetch_case_documents
from .events import extract_events
from .ingest import from_live_record, map_live_docket, upsert_to_corpus
from .outcome import disposition_basis, resolve_case, termination_signal
from .pull import PullQueues, _in_predict_scope
from .salience import apply_salience_selection

# The two per-Term numbering streams discovery probes, each from its base.
STREAMS: tuple[tuple[str, int], ...] = (("paid", 1), ("ifp", IFP_SERIAL_BASE))


@dataclass
class LiveResult:
    """One case's live poll, mirroring the pull-side ``PullResult``."""

    case_id: str
    changed: bool
    resolved: list[str]
    unrecorded_events: list[str]
    unrecorded_reason: str | None = None
    # The conference this petition is distributed for after this poll.
    # The caller compares it against the pre-poll value: a transition (fresh
    # distribution or a relist's new date) is the predict trigger.
    distributed: date | None = None
    # A human-readable reason the fresh docket already reads as decided even
    # though resolution recorded no outcome (a SCOTUS terminal order the cert
    # resolver does not match — e.g. a Rule 39.8 dismissal), or None. Keeps such
    # a case out of the forward-predict queue; mirrors ``PullResult``.
    termination_signal: str | None = None


@dataclass
class LiveDiscovery:
    """What frontier probing found this cycle."""

    onboarded: list[LiveResult] = field(default_factory=list)
    # (stream, reason) for a stream stopped by an upstream error; its cursor is
    # untouched, so the next cycle retries the same serials gap-free.
    failed: list[dict[str, object]] = field(default_factory=list)

    @property
    def case_ids(self) -> list[str]:
        return [result.case_id for result in self.onboarded]


def _resolve_identity(
    conn: sqlite3.Connection, payload: dict[str, object], term: int, serial: int
) -> int:
    """The docket id this petition's row keys on: the matched row's, or a live mint.

    The reconciliation decision: join by normalized Term-form docket
    number onto any existing SCOTUS row and enrich it; only a genuinely unseen
    petition mints the deterministic reserved-range id. The minted id is
    permanent — see :func:`fedcourtsai.supremecourt.live_docket_id`.
    """
    raw_number = str(payload.get("CaseNumber") or f"{term:02d}-{serial}")
    existing = corpus.scotus_case_id_by_docket_number(conn, raw_number)
    if existing is not None:
        return int(existing.rsplit("/", 1)[-1])
    return live_docket_id(term, serial)


def ingest_live_payload(
    corpus_db_path: Path,
    data_root: Path,
    payload: dict[str, object],
    docket_id: int,
    *,
    today: date,
    sample_weight: int = 1,
) -> LiveResult:
    """Land one fetched docket JSON in the corpus; detect change and resolution.

    The live analogue of ``pull_case`` after its fetch: snapshot the raw JSON
    (change detection against the latest stored snapshot), upsert the normalized
    row (stamping ``last_live_polled``), run resolution over the still-open
    events, then re-extract predictable events from the mapped record so a
    filing that appeared since onboarding becomes trackable.

    ``sample_weight`` records how the calling channel came to include this row.
    The poller's paths include every row they touch — the default 1 — while the
    historical walker passes ``denial_sample_every`` for a denial its serial
    sample kept. The upsert min-latches it, so a weight-1 row never regresses.
    """
    case_id = ids.case_id("scotus", docket_id)
    with corpus.connect(corpus_db_path) as conn:
        prior = corpus.latest_snapshot(conn, case_id)
        changed = prior is None or prior[1] != payload
        corpus.upsert_snapshot(conn, case_id, today, payload)

    record = map_live_docket(payload, docket_id)
    row = from_live_record(record)
    upsert_to_corpus(corpus_db_path, [row], last_live_polled=today, sample_weight=sample_weight)

    # Resolution before re-extraction, exactly as in pull_case: `default_event`
    # marks a decided case's baseline resolved, so resolution must see the event
    # still open to record its outcome before extraction latches it closed.
    resolution = resolve_case(
        corpus_db_path,
        data_root,
        row,
        "scotus",
        docket_id,
        disposition_basis=disposition_basis(record),
    )

    extraction = extract_events(record, normalize=from_live_record)
    with corpus.connect(corpus_db_path) as conn:
        corpus.upsert_events(conn, extraction.events)

    return LiveResult(
        case_id=case_id,
        changed=changed,
        resolved=sorted(resolution.outcomes),
        unrecorded_events=[r.event_id for r in resolution.unrecorded],
        unrecorded_reason=resolution.unrecorded[0].reason if resolution.unrecorded else None,
        distributed=row.distributed_for_conference,
        termination_signal=termination_signal(record),
    )


def provision_documents(
    client: SupremeCourtClient,
    corpus_db_path: Path,
    case_id: str,
    payload: dict[str, object],
    *,
    char_cap: int,
    today: date,
) -> int:
    """Fetch this petition's predict-input documents into the corpus.

    Called on the same **distribution transition** that queues prediction — the
    moment the record is complete enough to predict is the moment its content
    is provisioned, and the fetch happens near filing time (document links are
    a rolling window upstream). Idempotent per (kind, url); returns the number
    of documents written.
    """
    with corpus.connect(corpus_db_path) as conn:
        stored = {d.kind: d.url for d in corpus.documents_for_case(conn, case_id)}
    documents = fetch_case_documents(
        client, case_id, payload, stored_urls=stored, char_cap=char_cap, today=today
    )
    if not documents:
        return 0
    with corpus.connect(corpus_db_path) as conn:
        return corpus.upsert_documents(conn, documents)


def discover_live(  # noqa: PLR0913 - soft-budget deadline + injected clock over the cycle args
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    term: int,
    *,
    max_new: int,
    frontier_misses: int = 2,
    document_text_cap: int = 150_000,
    gated: bool = False,
    today: date,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> LiveDiscovery:
    """Probe the Term's frontier serials and onboard each served petition.

    Sequential probing per stream from the persisted cursor: a served record is
    onboarded (identity-reconciled, snapshotted, events defined) and advances
    the cursor; ``frontier_misses`` consecutive 404s mark the stream's current
    frontier (numbers are assigned sequentially, so the tolerance only bridges
    the occasional withheld number). An upstream error stops the stream —
    cursor untouched, next cycle retries gap-free — and never aborts the cycle.
    """
    result = LiveDiscovery()
    if max_new <= 0:
        return result
    for stream, base in STREAMS:
        if len(result.onboarded) >= max_new or (deadline is not None and time_fn() >= deadline):
            break
        with corpus.connect(corpus_db_path) as conn:
            cursor = corpus.get_live_cursor(conn, term, stream)
        serial = (cursor + 1) if cursor is not None else base
        misses = 0
        while (
            misses < frontier_misses
            and len(result.onboarded) < max_new
            and (deadline is None or time_fn() < deadline)
        ):
            try:
                payload = client.get_docket(term, serial)
            except httpx.HTTPError as exc:
                result.failed.append(
                    {"stream": stream, "serial": serial, "reason": f"{type(exc).__name__}: {exc}"}
                )
                break
            if payload is None:
                misses += 1
                serial += 1
                continue
            misses = 0
            with corpus.connect(corpus_db_path) as conn:
                docket_id = _resolve_identity(conn, payload, term, serial)
            ingested = ingest_live_payload(
                corpus_db_path, data_root, payload, docket_id, today=today
            )
            if ingested.distributed is not None and (
                not gated or _in_predict_scope(corpus_db_path, ingested.case_id)
            ):
                # Frontier catch-up on an already-distributed petition that the
                # gate would queue: provision its documents now. A deferred
                # petition just enters the watchlist — the selection sweep
                # provisions it if it is ever latched.
                provision_documents(
                    client,
                    corpus_db_path,
                    ingested.case_id,
                    payload,
                    char_cap=document_text_cap,
                    today=today,
                )
            with corpus.connect(corpus_db_path) as conn:
                corpus.set_live_cursor(conn, term, stream, serial)
            result.onboarded.append(ingested)
            serial += 1
        if misses >= frontier_misses:
            # This probe observed the stream's current end — stamp it at the
            # cursor so downstream census readers can tell "walked to the
            # frontier" from "stopped at a cap". A cap/error exit leaves any
            # prior stamp alone. No cursor row means nothing was ever served
            # (a Term not yet opened): nothing to stamp.
            with corpus.connect(corpus_db_path) as conn:
                stored = corpus.get_live_cursor(conn, term, stream)
                if stored is not None:
                    corpus.set_live_frontier(conn, term, stream, stored)
    return result


def poll_live_cases(  # noqa: PLR0913 - soft-budget deadline + injected clock over the cycle args
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    due: list[corpus.CorpusRow],
    *,
    scope: PredictScope = PredictScope.all,
    document_text_cap: int = 150_000,
    today: date,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> PullQueues:
    """Refresh each due pending petition and sort it into the handoff queues.

    The predict handoff fires on a **distribution transition** — the petition is
    newly distributed for a conference, or a relist moved its date — the live
    analogue of ``pull.predict_on_change_only`` tuned to the cert calendar:
    distribution is the signal that resolution is imminent and the
    record is complete enough to predict. Ground-truth *recording* is ungated;
    the ``evaluate`` queue requires a committed prediction to score (drops are
    surfaced on ``evaluate_skipped``), and ambiguous resolutions route to
    ``unrecorded`` unconditionally. A petition whose docket JSON has vanished (404 on a
    previously served number) is recorded on ``failed`` and its
    ``last_live_polled`` still advances via the row upsert path — it must not
    pin the rotation's front.
    """
    queues = PullQueues()
    gated = scope == PredictScope.scotus_docket
    for row in due:
        if deadline is not None and time_fn() >= deadline:
            # Soft wall-clock budget reached: stop cleanly with the polls done so
            # far committed (each poll advances last_live_polled), so the caller
            # pushes real progress and the next cycle resumes the rotation where
            # it left off (nearest-conference-first, staleness breaking ties)
            # rather than re-doing this cycle wholesale.
            break
        parsed = parse_scotus_docket_number(row.docket_number)
        docket_id = int(row.case_id.rsplit("/", 1)[-1])
        if parsed is None:
            # live_rotation verified the modern-cert form, so this is unreachable
            # in practice; skip defensively rather than probe a malformed URL.
            continue
        term, serial = parsed
        try:
            payload = client.get_docket(term, serial)
        except httpx.HTTPError as exc:
            queues.failed.append(
                {
                    "court": "scotus",
                    "docket": docket_id,
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        if payload is None:
            # Previously served, now 404 — upstream withdrew the record. Stamp
            # the poll (so the rotation moves on) and note the casualty.
            with corpus.connect(corpus_db_path) as conn:
                stamped = row.model_copy(update={"last_live_polled": today})
                corpus.upsert_rows(conn, [stamped])
            queues.failed.append(
                {"court": "scotus", "docket": docket_id, "reason": "docket JSON no longer served"}
            )
            continue
        result = ingest_live_payload(corpus_db_path, data_root, payload, docket_id, today=today)
        # The transition test: `row` is the pre-poll corpus row, so a fresh
        # distribution (None -> date) and a relist (date -> new date) both
        # trigger; an unchanged membership does not, however else the docket moved.
        transitioned = (
            result.distributed is not None and result.distributed != row.distributed_for_conference
        )
        # The queue decision is made here so provisioning follows it: a
        # transition on a petition the salience latch defers spends neither
        # document fetches nor corpus blob. The latch read is the pre-pass
        # state — the cycle-end selection sweep rescues a petition whose first
        # transition and first selection land in the same cycle.
        queue_predict = transitioned and (
            not gated or _in_predict_scope(corpus_db_path, result.case_id)
        )
        if queue_predict:
            # Predict is about to be queued for this petition — provision its
            # documents (petition / QP / BIO) on the same trigger. Idempotent
            # per (kind, url), so a relist with unchanged filings costs nothing.
            provision_documents(
                client,
                corpus_db_path,
                result.case_id,
                payload,
                char_cap=document_text_cap,
                today=today,
            )
        _route_result(
            queues,
            corpus_db_path,
            data_root,
            result,
            gated=gated,
            queue_predict=queue_predict,
            today=today,
        )
    return queues


def _decided_reason(result: LiveResult) -> str | None:
    """The forward-queue guard: why a decided-looking docket must not queue predict.

    A terminal order the cert resolver missed, or an outcome that appears
    decided but was not deterministically recorded, diverts to
    ``predict_skipped_decided`` so the skip is triageable — not a mislabeled
    forward cell whose unrestricted retrieval could read the outcome.
    """
    return result.termination_signal or (
        "docket appears decided; its outcome could not be recorded deterministically"
        if result.unrecorded_events
        else None
    )


def _route_result(
    queues: PullQueues,
    corpus_db_path: Path,
    data_root: Path,
    result: LiveResult,
    *,
    gated: bool,
    queue_predict: bool,
    today: date,
) -> None:
    """Sort one poll result into the handoff queues (pull's routing, verbatim).

    ``queue_predict`` is the caller's distribution-transition verdict — it
    gates only the predict handoff. The evaluate handoff requires a committed
    prediction (an unscoreable resolution lands on ``evaluate_skipped``);
    unrecorded outcomes always route. A predict queue entry stamps
    ``predict_queued_at`` (the selection sweep's daily-retry debounce).
    """
    docket_id = int(result.case_id.rsplit("/", 1)[-1])
    in_scope = not gated or _in_predict_scope(corpus_db_path, result.case_id)
    events = open_events(corpus_db_path, "scotus", docket_id)
    if queue_predict and in_scope and result.changed and events:
        # A decided-looking docket never queues forward (pull's rule, verbatim).
        decided_reason = _decided_reason(result)
        if decided_reason:
            queues.predict_skipped_decided.append(
                {"court": "scotus", "docket": docket_id, "events": events, "reason": decided_reason}
            )
        else:
            queues.predict.append({"court": "scotus", "docket": docket_id, "events": events})
            with corpus.connect(corpus_db_path) as conn:
                corpus.stamp_predict_queued(conn, [result.case_id], today)
    if in_scope and result.resolved:
        # Only events something actually predicted reach evaluation: the live
        # sweeps resolve plenty of never-predicted petitions (frontier catch-up,
        # historical rotation), and each queued case fans out one agent cell per
        # evaluator — pure spend with nothing to score.
        scoreable = [
            event_id
            for event_id in result.resolved
            if event_has_predictions(data_root, "scotus", docket_id, event_id)
        ]
        if scoreable:
            queues.evaluate.append({"court": "scotus", "docket": docket_id, "events": scoreable})
        unscoreable = [e for e in result.resolved if e not in scoreable]
        if unscoreable:
            queues.evaluate_skipped.append(
                {"court": "scotus", "docket": docket_id, "events": unscoreable}
            )
    if result.unrecorded_events:
        queues.unrecorded.append(
            {
                "court": "scotus",
                "docket": docket_id,
                "events": result.unrecorded_events,
                "reason": result.unrecorded_reason,
            }
        )


def salience_sweep(  # noqa: PLR0913 - soft-budget deadline + injected clock over the cycle args
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    queues: PullQueues,
    *,
    cap: int,
    already_queued: set[int],
    document_text_cap: int = 150_000,
    today: date,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> None:
    """Queue selected petitions the distribution trigger alone would miss.

    The transition trigger only fires when a poll observes a membership change,
    and the queue-time latch read predates the cycle's selection pass — so three
    real gaps remain: a petition whose first transition and first selection land
    in the same cycle (deferred at queue time), a petition latched when its
    transitions all predate the first applied pass (the catch-up backlog), and a
    selected petition whose queued run produced no committed prediction (the
    retry). The sweep closes all three: every latched petition with open,
    never-predicted events is re-polled, provisioned, and queued, up to ``cap``
    fetches per cycle, stalest first.

    The ``predict_queued_at`` stamp debounces the retry to daily: a case queued
    today — by this cycle's routing or an earlier window — waits for tomorrow's
    sweep, so an open-but-unmerged run PR is not re-queued every cycle while a
    genuinely failed run still retries the next day. Each sweep re-polls the
    docket, so the decided-looking guard and outcome recording run against
    fresh facts, exactly as a rotation poll would.
    """
    if cap <= 0:
        return
    with corpus.connect(corpus_db_path) as conn:
        candidates = sorted(
            (
                row
                for row in corpus.iter_rows(conn, court="scotus")
                # `predict_excluded` is the cheap row-level pre-filter: a selected
                # petition later latched out of scope must not spend a fetch slot
                # every cycle only to be rejected post-fetch (the full exclusion
                # reasoning still re-runs on the fresh row before queueing).
                if row.salience_selected and not row.predict_excluded
            ),
            key=lambda row: (row.last_live_polled or date.min, row.case_id),
        )
    fetches = 0
    for row in candidates:
        if fetches >= cap or (deadline is not None and time_fn() >= deadline):
            break
        docket_id = int(row.case_id.rsplit("/", 1)[-1])
        if docket_id in already_queued:
            continue
        if row.predict_queued_at == today:
            continue
        events = open_events(corpus_db_path, "scotus", docket_id)
        if not events or any(
            event_has_predictions(data_root, "scotus", docket_id, event_id) for event_id in events
        ):
            continue
        parsed = parse_scotus_docket_number(row.docket_number)
        if parsed is None:
            continue
        term, serial = parsed
        fetches += 1
        try:
            payload = client.get_docket(term, serial)
        except httpx.HTTPError as exc:
            queues.failed.append(
                {"court": "scotus", "docket": docket_id, "reason": f"{type(exc).__name__}: {exc}"}
            )
            continue
        if payload is None:
            queues.failed.append(
                {"court": "scotus", "docket": docket_id, "reason": "docket JSON no longer served"}
            )
            continue
        result = ingest_live_payload(corpus_db_path, data_root, payload, docket_id, today=today)
        # Ground-truth routing first: the re-poll may have caught a resolution,
        # in which case there is nothing left to predict.
        _route_result(
            queues, corpus_db_path, data_root, result, gated=True, queue_predict=False, today=today
        )
        open_now = open_events(corpus_db_path, "scotus", docket_id)
        if not open_now or not _in_predict_scope(corpus_db_path, result.case_id):
            continue
        reason = _decided_reason(result)
        if reason:
            queues.predict_skipped_decided.append(
                {"court": "scotus", "docket": docket_id, "events": open_now, "reason": reason}
            )
            # Stamp the divert too: a decided-looking docket whose outcome stays
            # unrecordable keeps open events, and without the stamp it would
            # re-fetch and re-append every window instead of daily.
            with corpus.connect(corpus_db_path) as conn:
                corpus.stamp_predict_queued(conn, [result.case_id], today)
            continue
        provision_documents(
            client, corpus_db_path, result.case_id, payload, char_cap=document_text_cap, today=today
        )
        queues.predict.append({"court": "scotus", "docket": docket_id, "events": open_now})
        with corpus.connect(corpus_db_path) as conn:
            corpus.stamp_predict_queued(conn, [result.case_id], today)


def live_poll_all(  # noqa: PLR0913 - soft-budget deadline + injected clock over the cycle args
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    *,
    term: int,
    config: LiveConfig,
    scope: PredictScope = PredictScope.all,
    salience_config: SalienceConfig | None = None,
    today: date,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> tuple[PullQueues, LiveDiscovery]:
    """One live cycle: discovery, the pending refresh, then the salience pass.

    ``config`` (the ``live:`` section of ``tracking.yaml``) carries the cycle's
    caps and politeness knobs. Discovery runs first so a petition docketed since
    the last cycle is onboarded this same cycle; a case discovery just ingested
    is excluded from the refresh rotation (its poll is seconds old; re-fetching
    it would only spend cadence), and its result is routed through the identical
    queue logic instead.

    Predict timing is the distribution trigger everywhere: a freshly
    onboarded petition queues predict only if it is already distributed for a
    conference (frontier catch-up); an undistributed one simply enters the
    watchlist, and the refresh queues it when its distribution lands.

    ``salience_config`` wires the salience gate into the cycle: after the polls
    have ingested the day's transitions, the selection pass scores and latches
    against the fresh cohorts (:func:`apply_salience_selection` — before the
    caller's corpus push, so the committed pointer carries the post-pass latch:
    every sweep pick is selected at the pointer the predict matrix gate reads,
    and a fail-open queue entry the same pass scores-and-defers is dropped by
    that read-time gate, non-destructively), and under the gated scope the
    selection sweep queues what the transition trigger missed. ``None`` skips
    both, leaving the queue-time deferral check fail-open.
    """
    gated = scope == PredictScope.scotus_docket
    discovery = discover_live(
        client,
        corpus_db_path,
        data_root,
        term,
        max_new=config.max_new_cases_per_run,
        frontier_misses=config.frontier_misses,
        document_text_cap=config.document_text_cap,
        gated=gated,
        today=today,
        deadline=deadline,
        time_fn=time_fn,
    )
    queues = PullQueues()
    for onboarded in discovery.onboarded:
        # A brand-new row has no prior membership, so "distributed at all" is
        # the transition test for the discovery path.
        _route_result(
            queues,
            corpus_db_path,
            data_root,
            onboarded,
            gated=gated,
            queue_predict=onboarded.distributed is not None,
            today=today,
        )

    fresh = set(discovery.case_ids)
    max_cases = config.max_cases_per_run
    with corpus.connect(corpus_db_path) as conn:
        due = [
            row
            for row in corpus.live_rotation(
                conn, limit=max_cases + len(fresh), term_floor_year=config.term_floor_year
            )
            if row.case_id not in fresh
        ][:max_cases]
    refreshed = poll_live_cases(
        client,
        corpus_db_path,
        data_root,
        due,
        scope=scope,
        document_text_cap=config.document_text_cap,
        today=today,
        deadline=deadline,
        time_fn=time_fn,
    )
    queues.predict.extend(refreshed.predict)
    queues.predict_skipped_decided.extend(refreshed.predict_skipped_decided)
    queues.evaluate.extend(refreshed.evaluate)
    queues.evaluate_skipped.extend(refreshed.evaluate_skipped)
    queues.unrecorded.extend(refreshed.unrecorded)
    queues.failed.extend(refreshed.failed)

    if salience_config is not None:
        with corpus.connect(corpus_db_path) as conn:
            apply_salience_selection(conn, salience_config)
        if gated:
            already_queued = {
                int(str(entry["docket"]))
                for entry in (
                    *queues.predict,
                    *queues.predict_skipped_decided,
                    *queues.unrecorded,
                )
            }
            salience_sweep(
                client,
                corpus_db_path,
                data_root,
                queues,
                cap=salience_config.sweep_cases_per_cycle,
                already_queued=already_queued,
                document_text_cap=config.document_text_cap,
                today=today,
                deadline=deadline,
                time_fn=time_fn,
            )
    return queues, discovery
