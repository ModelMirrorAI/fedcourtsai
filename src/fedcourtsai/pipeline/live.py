"""The SCOTUS live channel's poller: discover and refresh pending petitions.

The live counterpart of :mod:`fedcourtsai.pipeline.pull`, fed by the
supremecourt.gov docket JSON (:class:`fedcourtsai.supremecourt.SupremeCourtClient`)
instead of the CourtListener REST API — minutes-to-hours fresh, budget-free.
Deterministic, no agent. Each cycle:

- **Discovery** probes the current docket Term's next unseen serials per
  numbering stream (paid petitions from 1, IFP from 5001) until the frontier —
  consecutive misses — and onboards each served petition, persisting a per-Term
  cursor (:func:`fedcourtsai.corpus.get_live_cursor`) so the next cycle resumes
  where this one stopped. For a bounded window after the July numbering roll it
  also probes the *outgoing* Term (``LiveConfig.outgoing_term_grace_days``), so a
  late filing onto the old prefix is caught before it is lost.
- **Refresh** re-polls the live modern-cert watchlist
  (:func:`fedcourtsai.corpus.live_rotation` — recent Terms first, then stalest;
  pending petitions plus the granted dockets whose merits proceeding is still
  open) and detects resolution: the disposition orders ride in the proceedings
  text,
  machine-matchable per the reachability probe, so a decided petition lands its
  ``outcome.json`` deterministically through the same
  :func:`~fedcourtsai.pipeline.outcome.resolve_case` seam pull uses — and a
  cert grant mints the open merits event that keeps its docket in this
  rotation until the judgment.
- **The application rotation** re-polls unresolved interim applications
  (:func:`fedcourtsai.corpus.application_rotation`) under its own small
  per-cycle cap, resolving them through the interim vocabulary and persisting
  the escalation signals. A changed, still-unresolved **substantive**
  application in predict scope queues predict (the interim predict path, quota'd
  by the salience reserve — see ``docs/salience.md``); everything else on the
  rotation stays ground-truth collection only.

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
ambiguous resolution lands on ``unrecorded`` for the pipeline-runs dashboard.
"""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Literal

import httpx

from .. import corpus, ids
from ..config import LiveConfig, PredictScope, SalienceConfig
from ..matrix import cell_failure_count, event_has_predictions, predicted_case_ids
from ..registry import enabled_predictors
from ..store import event_has_claimable_prediction, forecastable_events
from ..supremecourt import (
    IFP_SERIAL_BASE,
    SupremeCourtClient,
    current_docket_term,
    live_application_id,
    live_docket_id,
    parse_scotus_application_number,
    parse_scotus_docket_number,
    term_roll_date,
)
from .documents import fetch_case_documents
from .events import extract_events
from .ingest import from_live_record, map_live_docket, upsert_to_corpus
from .interim_signals import ApplicationKind
from .outcome import (
    disposition_basis,
    interim_disposal_signal,
    read_order_markers,
    resolve_case,
    termination_signal,
)
from .pull import PullQueues, _in_predict_scope
from .salience import apply_salience_selection

# The two per-Term numbering streams discovery probes, each from its base.
# The numbering sequences the frontier walk probes, as (name, first serial,
# docket form). The two cert streams share a form and differ only in where their
# serials start; the interim docket is a separate sequence addressed differently
# ("24A1099" rather than "24-1099") and identified in a disjoint id range, since
# `24A1` and `24-1` are different matters.
STREAMS: tuple[tuple[str, int, Literal["cert", "application"]], ...] = (
    ("paid", 1, "cert"),
    ("ifp", IFP_SERIAL_BASE, "cert"),
    ("application", 1, "application"),
)


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
    conn: sqlite3.Connection,
    payload: dict[str, object],
    term: int,
    serial: int,
    *,
    form: Literal["cert", "application"] = "cert",
) -> int:
    """The docket id this petition's row keys on: the matched row's, or a live mint.

    The reconciliation decision: join by normalized Term-form docket
    number onto any existing SCOTUS row and enrich it; only a genuinely unseen
    petition mints the deterministic reserved-range id. The minted id is
    permanent — see :func:`fedcourtsai.supremecourt.live_docket_id`.
    """
    separator = "A" if form == "application" else "-"
    raw_number = str(payload.get("CaseNumber") or f"{term:02d}{separator}{serial}")
    existing = corpus.scotus_case_id_by_docket_number(conn, raw_number)
    if existing is not None:
        return int(existing.rsplit("/", 1)[-1])
    if form == "application":
        return live_application_id(term, serial)
    return live_docket_id(term, serial)


def ingest_live_payload(
    corpus_db_path: Path,
    data_root: Path,
    payload: dict[str, object],
    docket_id: int,
    *,
    today: date,
    sample_weight: int = 1,
    form: Literal["cert", "application"] = "cert",
) -> LiveResult:
    """Land one fetched docket JSON in the corpus; detect change and resolution.

    The live analogue of ``pull_case`` after its fetch: snapshot the raw JSON
    (change detection against the latest stored snapshot), upsert the normalized
    row (stamping ``last_live_polled``), run resolution over the still-open
    events, then re-extract predictable events from the mapped record so a
    filing that appeared since onboarding becomes trackable.

    ``sample_weight`` records how the calling channel came to include this row.
    The poller's paths include every row they touch — the default 1 — while the
    historical walker passed the legacy sampling interval for a denial its serial
    sample kept. The upsert min-latches it, so a weight-1 row never regresses.
    """
    case_id = ids.case_id("scotus", docket_id)
    with corpus.connect(corpus_db_path) as conn:
        prior = corpus.latest_snapshot(conn, case_id)
        changed = prior is None or prior[1] != payload
        corpus.upsert_snapshot(conn, case_id, today, payload)

    record = map_live_docket(payload, docket_id, form=form)
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
        # The two order-text markers read the RAW payload rather than the mapped
        # record: `_live_entries` synthesizes a list even for a payload carrying
        # no proceedings key at all, which would report "assessed, nothing
        # found" where nothing was disclosed — and the raw payload is what the
        # snapshot stores, so a later cascade over the same case marks the
        # outcome identically.
        order=read_order_markers(
            payload, disposition=row.disposition, date_cert_granted=row.date_cert_granted
        ),
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
        # Form-keyed decided-guard: the cert scan on a cert docket, the
        # high-recall interim disposal scan on an application — the interim
        # resolver's vocabulary is exact-match, so a disposal it misses must
        # still divert the forward queue rather than mint a cell whose
        # snapshot shows the outcome.
        termination_signal=(
            interim_disposal_signal(record) if form == "application" else termination_signal(record)
        ),
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


def _within_term_roll_grace(today: date, grace_days: int) -> bool:
    """Whether ``today`` sits inside the outgoing-Term grace window after a roll.

    The window opens at the July docket-number roll (:func:`term_roll_date`) and
    runs through ``grace_days`` *inclusive* — the roll day itself is day 0 — so
    the outgoing Term is probed alongside the current one only while a late tail
    filing onto it is still plausible. ``term_roll_date`` returns a July 1 at or
    before ``today``, so the lower bound never trips; it is stated for the reader.
    """
    return 0 <= (today - term_roll_date(today)).days <= grace_days


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
    for stream, base, form in STREAMS:
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
                payload = client.get_docket(term, serial, form=form)
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
                docket_id = _resolve_identity(conn, payload, term, serial, form=form)
            ingested = ingest_live_payload(
                corpus_db_path, data_root, payload, docket_id, today=today, form=form
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
    salience_config: SalienceConfig | None = None,
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

    ``salience_config`` (when the scope is gated) additionally suppresses a
    **relist** transition — as opposed to a petition's first distribution —
    inside ``relist_requeue_cooldown_days`` of the case's last predict queue:
    administrative churn, not a materially different posture, while capacity
    is enforced. ``None`` (or an ungated scope) leaves every relist queueing
    unconditionally.
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
        # A relist is a transition where `row` (the pre-poll state) already
        # carried a distribution — as opposed to a petition's first ever
        # distribution — so the cooldown never touches a case's first
        # prediction, only a repeat. `row.predict_queued_at` is the pre-poll
        # stamp: the elapsed days since the case's last predict queue.
        relisted = transitioned and row.distributed_for_conference is not None
        relist_suppressed = (
            queue_predict
            and relisted
            and gated
            and salience_config is not None
            and row.predict_queued_at is not None
            and (today - row.predict_queued_at).days < salience_config.relist_requeue_cooldown_days
        )
        if queue_predict and not relist_suppressed:
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
            relist_suppressed=relist_suppressed,
        )
    return queues


def poll_applications(
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    due: list[corpus.CorpusRow],
    *,
    document_text_cap: int = 150_000,
    today: date,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> PullQueues:
    """Refresh each due unresolved application; queue the predictable slice forward.

    The interim counterpart of :func:`poll_live_cases`. Each poll catches the
    entries filed since the last one — a response request, a referral, an
    amicus brief, the disposition itself — and lands them as the latched corpus
    signals; a machine-matched resolution records the interim ``outcome.json``
    on the motion/interim baseline (:mod:`fedcourtsai.pipeline.outcome`'s
    stage-keyed interim target).

    An application has no distribution calendar, so there is no transition to
    key the predict handoff on. The interim trigger is instead **any observed
    docket change while the application is still unresolved**, on a
    **substantive** application in predict scope — every filing on a live stay
    application moves its posture, so change is the honest analogue of the cert
    side's distribution transition — debounced to daily by the shared
    ``predict_queued_at`` stamp (the same stamp the routing writes and the
    selection sweep's retry compares), so a busy docket queues at most once a
    day. The scope check is the shared :func:`_in_predict_scope` (row scope —
    which spares only substantive applications — plus the salience latch,
    fail-open until the reserve has scored the row); an extension, an
    unknown-ask application, or a reserve-deferred one never queues. Routing
    stays **ungated** by the cycle's predict scope: the per-row predicate above
    already protects predict spend, while gating would hide out-of-scope
    resolutions from the run log, leaving the stream's accumulation invisible.
    A non-machine-matchable resolution surfaces on ``unrecorded`` while its
    baseline is still open *and* its row is not ``predict_excluded``; once the
    scope reconcile latches an out-of-scope row, ``open_events`` yields nothing
    and the resolution lands silently as the row's latched disposition columns.
    The same politeness applies (the client paces every fetch) and the same
    soft budget: on expiry the polls done so far are committed and the rotation
    resumes next cycle. A vanished docket (404 on a previously served number)
    is stamped so it cannot pin the rotation's front, exactly as in the cert
    refresh.
    """
    queues = PullQueues()
    for row in due:
        if deadline is not None and time_fn() >= deadline:
            break
        parsed = parse_scotus_application_number(row.docket_number)
        docket_id = int(row.case_id.rsplit("/", 1)[-1])
        if parsed is None:
            # application_rotation verified the addressable form, so this is
            # unreachable in practice; skip defensively rather than probe a
            # malformed URL.
            continue
        term, serial = parsed
        try:
            payload = client.get_docket(term, serial, form="application")
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
            with corpus.connect(corpus_db_path) as conn:
                stamped = row.model_copy(update={"last_live_polled": today})
                corpus.upsert_rows(conn, [stamped])
            queues.failed.append(
                {"court": "scotus", "docket": docket_id, "reason": "docket JSON no longer served"}
            )
            continue
        result = ingest_live_payload(
            corpus_db_path, data_root, payload, docket_id, today=today, form="application"
        )
        # The interim predict trigger, on the post-poll row (the poll may have
        # just latched the substantive ask — or the resolution, which closes
        # the seam: a resolved application must never mint a forward cell its
        # snapshot already answers). `row` is the pre-poll state, so its
        # `predict_queued_at` carries the debounce.
        with corpus.connect(corpus_db_path) as conn:
            fresh = corpus.get_row(conn, result.case_id)
        # Pending is the two-clause test the reserve uses (no disposition AND
        # no resolution date): a dated resolution whose disposition text the
        # vocabulary could not read is still resolved, never a forward cell.
        queue_predict = (
            result.changed
            and fresh is not None
            and fresh.disposition is None
            and corpus.resolution_date(fresh) is None
            and fresh.application_kind == ApplicationKind.substantive
            and row.predict_queued_at != today
            and _in_predict_scope(corpus_db_path, result.case_id)
        )
        if queue_predict:
            # Predict is about to be queued — provision the application's
            # documents on the same trigger, exactly as the cert refresh does.
            # Idempotent per (kind, url), so a re-queue with unchanged filings
            # costs nothing.
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
            gated=False,
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
    relist_suppressed: bool = False,
) -> None:
    """Sort one poll result into the handoff queues (pull's routing, verbatim).

    ``queue_predict`` is the caller's distribution-transition verdict — it
    gates only the predict handoff. The evaluate handoff requires a committed
    prediction (an unscoreable resolution lands on ``evaluate_skipped``);
    unrecorded outcomes always route. A predict queue entry stamps
    ``predict_queued_at`` (the selection sweep's daily-retry debounce).
    ``relist_suppressed`` diverts an otherwise-queueable relist to
    ``predict_skipped_relist_cooldown`` instead (checked after the decided
    guard, since a decided docket is never queued regardless of relist timing).
    """
    docket_id = int(result.case_id.rsplit("/", 1)[-1])
    in_scope = not gated or _in_predict_scope(corpus_db_path, result.case_id)
    events = forecastable_events(corpus_db_path, "scotus", docket_id, today=today)
    if queue_predict and in_scope and result.changed and events:
        # A decided-looking docket never queues forward (pull's rule, verbatim).
        decided_reason = _decided_reason(result)
        if decided_reason:
            queues.predict_skipped_decided.append(
                {"court": "scotus", "docket": docket_id, "events": events, "reason": decided_reason}
            )
        elif relist_suppressed:
            queues.predict_skipped_relist_cooldown.append(
                {
                    "court": "scotus",
                    "docket": docket_id,
                    "events": events,
                    "reason": "relisted inside the requeue cooldown of its last predict queue",
                }
            )
        else:
            queues.predict.append({"court": "scotus", "docket": docket_id, "events": events})
        # Queue entry and both diverts stamp: the sweep's daily debounce must
        # cover a diverted selected case too, or a later window's sweep
        # re-fetches it and appends a duplicate divert entry the same day.
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


def _predict_cell_capped(
    data_root: Path,
    court: str,
    docket: int,
    event_id: str,
    predictor_id: str,
    max_attempts: int,
) -> bool:
    """Whether a predict cell has exhausted the per-cell attempt cap.

    The predict-seam mirror of :func:`fedcourtsai.pipeline.pull._cell_capped`:
    counts the committed ``attempt.json`` failure facts at the ``predict`` seam
    (:func:`fedcourtsai.matrix.cell_failure_count`), keyed on cell identity — the
    corpus-blind ``collect`` job records one per failed run, so a cell retried
    across runs counts against the same cap rather than resetting it.
    ``max_attempts <= 0`` disables the cap.
    """
    if max_attempts <= 0:
        return False
    return cell_failure_count(data_root, court, docket, event_id, predictor_id, "predict") >= (
        max_attempts
    )


def salience_sweep(  # noqa: PLR0913,PLR0912,PLR0915 - cycle args (deadline/clock) + the per-cell owed fallback branch + the dual-form addressing + the cohort narrowing's two arms
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    queues: PullQueues,
    *,
    cap: int,
    already_queued: set[int],
    predictors_path: Path | None = None,
    max_attempts: int = 0,
    document_text_cap: int = 150_000,
    today: date,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> None:
    """Queue the petitions the distribution trigger alone would miss.

    The transition trigger only fires when a poll observes a membership change,
    and the queue-time latch read predates the cycle's selection pass — so four
    real gaps remain: a petition whose first transition and first selection land
    in the same cycle (deferred at queue time), a petition latched when its
    transitions all predate the first applied pass (the catch-up backlog), and a
    selected petition whose queued run left a ``(predictor, event)`` cell without
    a committed prediction (the retry), and a petition **deferred since** its
    run fired, whose event keeps a partial cohort no later transition can finish
    (cohort completion, below). The sweep closes all four: every candidate case
    with an open event still *owed* a prediction is re-polled,
    provisioned, and queued, up to ``cap`` fetches per cycle, stalest first.
    A reserve-selected **application** is swept on identical terms (addressed
    through the application form of the docket JSON): the interim analogue of
    the same-cycle gap is structural there — an application has no distribution
    transition at all — so the sweep is the path that queues one whose
    selection postdates its last docket change.

    **Owed is per ``(predictor, event)`` cell**, mirroring
    :func:`fedcourtsai.pipeline.pull.evaluate_backlog`: with ``predictors_path``
    the sweep re-queues a case while ANY enabled predictor lacks a prediction for
    ANY open event, so a case where two of three engines landed and one
    quota-failed is still swept for the missing engine — the old case-level gate
    treated any single landed prediction as "done" and never retried it. The
    per-cell attempt cap (``max_attempts``, the durable failure queue's poison-pill
    backstop; ``0`` disables it) keeps one cell that fails every attempt from
    re-queuing forever, and checking it per cell means a poison-pill engine never
    suppresses a sibling still owed the same event. Without ``predictors_path``
    (an offline / registry-free caller) the sweep falls back to the case-level
    gate — any committed prediction suppresses — the same ``data_root=None``
    convention :func:`fedcourtsai.matrix.predict_matrix` uses to keep its skip off.

    **Cohort completion re-admits a salience-deferred case, for its predicted
    events only.** Selection decides which petitions earn a forecast, so a case
    scored below the capacity slice is not a sweep candidate — but a case that
    *was* selected when its run fired, and drifted below the line since, can be
    left with an event carrying two of three engines and no path back: the
    distribution transition already fired, and the funding gate refuses it. So a
    case with any committed prediction (:func:`fedcourtsai.matrix.predicted_case_ids`)
    is admitted as a candidate on that ground, and on that ground the queued
    event list is narrowed to the events whose cohort a claimable board will
    count once the event resolves and is graded
    (:func:`fedcourtsai.store.event_has_claimable_prediction`).

    That narrowing carries **two** bounds, and both are load-bearing. The spend
    bound: a deferred case with a partial event and a second, untouched open
    event would otherwise queue both and mint brand-new cells on a case the
    funding gate declined. The comparability bound: an event whose whole
    existing cohort is outside the frozen process scope is not completed by a
    freshly-stamped cell — the new cell lands in the scope, its rivals do not,
    and the board gains an event scored on one engine alone. Completing a cohort
    the board does not count is not the gap this exists to close; it is a new
    one. The per-cell owed check and the attempt cap apply unchanged, so a
    deferred case whose cohort is complete — or whose only gap is poison-pilled
    — is still not swept, and a deferred case with no prediction at all is never
    a candidate.

    The narrowing predicate is ``not row.salience_selected and case_id not in
    merits_open`` — the candidate filter's own arms negated, so admission and
    narrowing cannot disagree — which is **narrower** than
    :func:`fedcourtsai.corpus.is_salience_deferred`: an *unscored* row (no
    ``salience_version``) is fail-open *selected* to that predicate but
    unselected to this one, so a cohort-bearing unscored row is narrowed to its
    predicted events rather than queued whole. Deliberate, and the conservative
    direction: the selection pass runs earlier in the same cycle, so an unscored
    row here is a row selection has not yet had an opinion about, and the sweep
    spends nothing new on it until it does. Reading
    ``is_salience_deferred`` instead would widen spend, not narrow it.

    The ``predict_queued_at`` stamp debounces the retry to daily: a case queued
    today — by this cycle's routing or an earlier window — waits for tomorrow's
    sweep, so an open-but-unmerged run PR is not re-queued every cycle while a
    genuinely failed run still retries the next day. Each sweep re-polls the
    docket, so the decided-looking guard and outcome recording run against
    fresh facts, exactly as a rotation poll would.
    """
    if cap <= 0:
        return
    # Resolve the enabled predictor ids once for the per-cell owed check. None
    # (no registry handle) selects the case-level fallback gate below.
    predictor_ids = (
        [p.id for p in enabled_predictors(predictors_path)] if predictors_path is not None else None
    )
    # One ledger glob per cycle, mirroring the `merits_open` read below: the
    # candidate filter consults it per row, and a per-row probe would walk the
    # predictions tree once for every SCOTUS case in the corpus.
    predicted = predicted_case_ids(data_root)
    with corpus.connect(corpus_db_path) as conn:
        # Read once, not per row: this comprehension walks every SCOTUS row, and
        # the set is a small ordered slice of the partial open-events index.
        merits_open = corpus.merits_open_case_ids(conn)
        candidates = sorted(
            (
                row
                for row in corpus.iter_rows(conn, court="scotus")
                # `predict_excluded` is the cheap row-level pre-filter: a selected
                # petition later latched out of scope must not spend a fetch slot
                # every cycle only to be rejected post-fetch (the full exclusion
                # reasoning still re-runs on the fresh row before queueing).
                #
                # The merits bypass rides beside it, not through it: a granted
                # docket has no further distribution transition, so this sweep is
                # the ONLY path to a merits cell — and the cert-stage funding
                # question does not apply to a case the Court has already agreed
                # to hear. `predict_excluded` still refuses, so the hard-scope
                # rules are untouched.
                #
                # Cohort completion rides beside both, and is admission ONLY: a
                # case with a committed prediction somewhere may re-enter the
                # sweep, which never says a cell is owed — the per-cell owed
                # check below decides that, and the in-loop narrowing confines
                # the queue to the events holding a *claimable* cohort.
                if (row.salience_selected or row.case_id in merits_open or row.case_id in predicted)
                and not row.predict_excluded
            ),
            # Stalest first, so the catch-up backlog drains fairly under the
            # cap. A same-cycle first-selection was polled today and therefore
            # sorts last — behind the backlog during a drain — but it is never
            # dropped (sticky candidate, unstamped), only deferred to a later
            # cycle while the backlog clears.
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
        events = forecastable_events(corpus_db_path, "scotus", docket_id, today=today)
        # Which ground admitted this row. The expressions are the candidate
        # filter's, verbatim, so admission and narrowing cannot disagree: only a
        # row that neither selection nor the merits bypass admitted is here on
        # the cohort ground, and only such a row is narrowed.
        cohort_only = not row.salience_selected and row.case_id not in merits_open
        if cohort_only:
            events = [
                event_id
                for event_id in events
                if event_has_claimable_prediction(data_root, "scotus", docket_id, event_id)
            ]
        # The owed check runs BEFORE the fetch — a fully-predicted case costs no
        # docket fetch — exactly where the old any-prediction case gate sat.
        if not events:
            continue
        if predictor_ids is None:
            # Registry-free fallback: the case-level gate (any committed
            # prediction suppresses the whole case). A
            # cohort-only candidate always falls here, because every event left
            # after the narrowing holds a prediction by construction — without
            # the registry there is no engine grain to be owed at.
            if any(
                event_has_predictions(data_root, "scotus", docket_id, event_id)
                for event_id in events
            ):
                continue
        elif not any(
            # Per (predictor, event): the case is owed while some enabled predictor
            # lacks a prediction for some open event and that cell is not
            # attempt-capped. This re-queues a case where some engines landed and
            # one quota-failed — the whole point of the per-cell grain.
            not event_has_predictions(data_root, "scotus", docket_id, event_id, predictor_id=pid)
            and not _predict_cell_capped(
                data_root, "scotus", docket_id, event_id, pid, max_attempts
            )
            for event_id in events
            for pid in predictor_ids
        ):
            continue
        # The sweep addresses both docket forms: a reserve-selected application
        # is only ever reachable here (it has no distribution transition, and
        # its selection may postdate its last docket change), so the cert-only
        # parse would strand exactly the cases the reserve funds.
        form: Literal["cert", "application"] = "cert"
        parsed = parse_scotus_docket_number(row.docket_number)
        if parsed is None:
            parsed = parse_scotus_application_number(row.docket_number)
            form = "application"
        if parsed is None:
            continue
        term, serial = parsed
        fetches += 1
        try:
            payload = client.get_docket(term, serial, form=form)
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
        result = ingest_live_payload(
            corpus_db_path, data_root, payload, docket_id, today=today, form=form
        )
        # Ground-truth routing first: the re-poll may have caught a resolution,
        # in which case there is nothing left to predict.
        _route_result(
            queues, corpus_db_path, data_root, result, gated=True, queue_predict=False, today=today
        )
        open_now = forecastable_events(corpus_db_path, "scotus", docket_id, today=today)
        if cohort_only:
            # Re-narrow after the re-poll, not just before it: the fresh ingest
            # may have minted a NEW open event on this case, and a new event has
            # no cohort to complete — queueing it would be exactly the new spend
            # the funding gate declined.
            open_now = [
                event_id
                for event_id in open_now
                if event_has_claimable_prediction(data_root, "scotus", docket_id, event_id)
            ]
        if not open_now or not _in_predict_scope(
            corpus_db_path, result.case_id, cohort_completion=cohort_only
        ):
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
    predictors_path: Path | None = None,
    predict_max_attempts: int = 0,
    today: date,
    deadline: float | None = None,
    time_fn: Callable[[], float] = time.monotonic,
) -> tuple[PullQueues, LiveDiscovery]:
    """One live cycle: discovery, the pending refresh, the application rotation,
    then the salience pass.

    Discovery runs the current filing Term and — for
    ``config.outgoing_term_grace_days`` after the July numbering roll — the
    outgoing Term too, from its own cursor, so its late tail is onboarded rather
    than lost; the grace probe shares the cycle's new-case budget behind the
    primary one and routes its onboards through the identical queue logic.

    ``config`` (the ``live:`` section of ``tracking.yaml``) carries the cycle's
    caps and politeness knobs. Discovery runs first so a petition docketed since
    the last cycle is onboarded this same cycle; a case discovery just ingested
    is excluded from the refresh rotation (its poll is seconds old; re-fetching
    it would only spend cadence), and its result is routed through the identical
    queue logic instead. After the cert polls, up to
    ``config.max_applications_per_run`` unresolved interim applications are
    re-polled (:func:`poll_applications`): a changed, unresolved substantive
    application in predict scope queues forward under the change-trigger
    debounce; everything else on the rotation is ground-truth collection.

    Predict timing is the distribution trigger everywhere: a freshly
    onboarded petition queues predict only if it is already distributed for a
    conference (frontier catch-up); an undistributed one simply enters the
    watchlist, and the refresh queues it when its distribution lands.

    ``salience_config`` wires the salience gate into the cycle: it also
    suppresses a near-immediate relist's re-queue during the refresh (see
    :func:`poll_live_cases`), and after the polls have ingested the day's
    transitions, the selection pass scores and latches against the fresh
    cohorts (:func:`apply_salience_selection` — before the caller's corpus
    push, so the committed pointer carries the post-pass latch: every sweep
    pick is either selected at the pointer the predict matrix gate reads or a
    cohort-completion pick that gate keeps narrowed rather than admits whole, and a
    fail-open queue entry the same pass scores-and-defers is dropped by that
    read-time gate, non-destructively), and under the gated scope the
    selection sweep queues what the transition trigger missed. ``None`` skips
    all three, leaving the queue-time deferral check fail-open.

    ``predictors_path`` and ``predict_max_attempts`` feed the sweep's per-cell
    owed check (see :func:`salience_sweep`): with the registry handle the sweep
    re-queues a case while any enabled predictor still owes an open event — a
    case where some engines landed and one quota-failed — instead of treating any
    single landed prediction as done, honoring the predict-side per-cell attempt
    cap. ``None`` leaves the sweep on its case-level fallback gate.
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
    # The outgoing-Term grace probe. Discovery probes exactly one Term, but the
    # Clerk's docket numbering rolls in July (``supremecourt.current_docket_term``)
    # three months before the Term opens, so at the roll the previous Term's
    # streams stop advancing while late filings may still land on them. The
    # historical walker does not recover them: it advances its cursor over every
    # served serial whether or not the record is decided, so a serial it passes
    # while still pending is never re-read — the tail is lost, not merely
    # delayed. For a bounded window after the roll, probe `term - 1` too,
    # from its own cursor, so a late tail filing is caught at the source and its
    # frontier re-stamped. The window (not a per-stream frontier test) is the
    # retirement: a drained stream would be skipped by the frontier test, which
    # is exactly the post-roll tail this probe exists to catch, so the probe
    # must run past a stale frontier while the window is open. Shares the
    # cycle's new-case budget behind the primary probe. Keyed on `term` being
    # the true current filing Term, so a manual `--term` override addresses one
    # Term only and never drags an unrelated `term - 1` probe with it.
    remaining = config.max_new_cases_per_run - len(discovery.onboarded)
    if (
        config.outgoing_term_grace_days > 0
        and term == current_docket_term(today)
        and _within_term_roll_grace(today, config.outgoing_term_grace_days)
        and remaining > 0
        and (deadline is None or time_fn() < deadline)
    ):
        grace = discover_live(
            client,
            corpus_db_path,
            data_root,
            term - 1,
            max_new=remaining,
            frontier_misses=config.frontier_misses,
            document_text_cap=config.document_text_cap,
            gated=gated,
            today=today,
            deadline=deadline,
            time_fn=time_fn,
        )
        discovery.onboarded.extend(grace.onboarded)
        discovery.failed.extend(grace.failed)
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
        salience_config=salience_config,
        document_text_cap=config.document_text_cap,
        today=today,
        deadline=deadline,
        time_fn=time_fn,
    )
    queues.predict.extend(refreshed.predict)
    queues.predict_skipped_decided.extend(refreshed.predict_skipped_decided)
    queues.predict_skipped_relist_cooldown.extend(refreshed.predict_skipped_relist_cooldown)
    queues.evaluate.extend(refreshed.evaluate)
    queues.evaluate_skipped.extend(refreshed.evaluate_skipped)
    queues.unrecorded.extend(refreshed.unrecorded)
    queues.failed.extend(refreshed.failed)

    # The application rotation, after the cert polls: unresolved interim
    # applications under their own cap. A changed, unresolved substantive
    # application in scope queues predict (poll_applications' per-row
    # predicate); the rest is ground-truth collection. A case discovery's
    # application stream just onboarded is excluded exactly as the cert
    # refresh excludes fresh petitions — its poll is seconds old.
    max_applications = config.max_applications_per_run
    with corpus.connect(corpus_db_path) as conn:
        applications_due = [
            row
            for row in corpus.application_rotation(
                conn,
                limit=max_applications + len(fresh),
                term_floor_year=config.term_floor_year,
            )
            if row.case_id not in fresh
        ][:max_applications]
    application_results = poll_applications(
        client,
        corpus_db_path,
        data_root,
        applications_due,
        document_text_cap=config.document_text_cap,
        today=today,
        deadline=deadline,
        time_fn=time_fn,
    )
    queues.predict.extend(application_results.predict)
    queues.predict_skipped_decided.extend(application_results.predict_skipped_decided)
    queues.evaluate.extend(application_results.evaluate)
    queues.evaluate_skipped.extend(application_results.evaluate_skipped)
    queues.unrecorded.extend(application_results.unrecorded)
    queues.failed.extend(application_results.failed)

    if salience_config is not None:
        with corpus.connect(corpus_db_path) as conn:
            apply_salience_selection(conn, data_root, salience_config)
        if gated:
            already_queued = {
                int(str(entry["docket"]))
                for entry in (
                    *queues.predict,
                    *queues.predict_skipped_decided,
                    *queues.predict_skipped_relist_cooldown,
                    *queues.unrecorded,
                    *queues.failed,
                )
            }
            salience_sweep(
                client,
                corpus_db_path,
                data_root,
                queues,
                cap=salience_config.sweep_cases_per_cycle,
                already_queued=already_queued,
                predictors_path=predictors_path,
                max_attempts=predict_max_attempts,
                document_text_cap=config.document_text_cap,
                today=today,
                deadline=deadline,
                time_fn=time_fn,
            )
    return queues, discovery
