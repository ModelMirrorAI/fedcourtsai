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
``evaluate``; an ambiguous resolution queues ``reconcile``.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import httpx

from .. import corpus, ids
from ..config import LiveConfig, PredictScope
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
from .outcome import resolve_case
from .pull import PullQueues, _in_predict_scope

# The two per-Term numbering streams discovery probes, each from its base.
STREAMS: tuple[tuple[str, int], ...] = (("paid", 1), ("ifp", IFP_SERIAL_BASE))


@dataclass
class LiveResult:
    """One case's live poll, mirroring the pull-side ``PullResult``."""

    case_id: str
    changed: bool
    resolved: list[str]
    reconcile_events: list[str]
    reconcile_reason: str | None = None
    # The conference this petition is distributed for after this poll.
    # The caller compares it against the pre-poll value: a transition (fresh
    # distribution or a relist's new date) is the predict trigger.
    distributed: date | None = None


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
) -> LiveResult:
    """Land one fetched docket JSON in the corpus; detect change and resolution.

    The live analogue of ``pull_case`` after its fetch: snapshot the raw JSON
    (change detection against the latest stored snapshot), upsert the normalized
    row (stamping ``last_live_polled``), run resolution over the still-open
    events, then re-extract predictable events from the mapped record so a
    filing that appeared since onboarding becomes trackable.
    """
    case_id = ids.case_id("scotus", docket_id)
    with corpus.connect(corpus_db_path) as conn:
        prior = corpus.latest_snapshot(conn, case_id)
        changed = prior is None or prior[1] != payload
        corpus.upsert_snapshot(conn, case_id, today, payload)

    record = map_live_docket(payload, docket_id)
    row = from_live_record(record)
    upsert_to_corpus(corpus_db_path, [row], last_live_polled=today)

    # Resolution before re-extraction, exactly as in pull_case: `default_event`
    # marks a decided case's baseline resolved, so resolution must see the event
    # still open to record its outcome before extraction latches it closed.
    resolution = resolve_case(corpus_db_path, data_root, row, "scotus", docket_id)

    extraction = extract_events(record, normalize=from_live_record)
    with corpus.connect(corpus_db_path) as conn:
        corpus.upsert_events(conn, extraction.events)

    return LiveResult(
        case_id=case_id,
        changed=changed,
        resolved=sorted(resolution.outcomes),
        reconcile_events=[r.event_id for r in resolution.reconciles],
        reconcile_reason=resolution.reconciles[0].reason if resolution.reconciles else None,
        distributed=row.distributed_for_conference,
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


def discover_live(
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    term: int,
    *,
    max_new: int,
    frontier_misses: int = 2,
    document_text_cap: int = 150_000,
    today: date,
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
        if len(result.onboarded) >= max_new:
            break
        with corpus.connect(corpus_db_path) as conn:
            cursor = corpus.get_live_cursor(conn, term, stream)
        serial = (cursor + 1) if cursor is not None else base
        misses = 0
        while misses < frontier_misses and len(result.onboarded) < max_new:
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
            if ingested.distributed is not None:
                # Frontier catch-up on an already-distributed petition: it will
                # queue predict this cycle, so provision its documents now.
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
    return result


def poll_live_cases(
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    due: list[corpus.CorpusRow],
    *,
    scope: PredictScope = PredictScope.all,
    document_text_cap: int = 150_000,
    today: date,
) -> PullQueues:
    """Refresh each due pending petition and sort it into the handoff queues.

    The predict handoff fires on a **distribution transition** — the petition is
    newly distributed for a conference, or a relist moved its date — the live
    analogue of ``pull.predict_on_change_only`` tuned to the cert calendar:
    distribution is the signal that resolution is imminent and the
    record is complete enough to predict. Outcomes (``evaluate``) and ambiguous
    resolutions (``reconcile``) route unconditionally — ground truth, not
    prediction spend. A petition whose docket JSON has vanished (404 on a
    previously served number) is recorded on ``failed`` and its
    ``last_live_polled`` still advances via the row upsert path — it must not
    pin the rotation's front.
    """
    queues = PullQueues()
    gated = scope == PredictScope.scotus_touched
    for row in due:
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
        if transitioned:
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
        _route_result(queues, corpus_db_path, result, gated=gated, queue_predict=transitioned)
    return queues


def _route_result(
    queues: PullQueues,
    corpus_db_path: Path,
    result: LiveResult,
    *,
    gated: bool,
    queue_predict: bool,
) -> None:
    """Sort one poll result into the handoff queues (pull's routing, verbatim).

    ``queue_predict`` is the caller's distribution-transition verdict —
    it gates only the predict handoff; outcomes and reconcile signals are
    ground truth and always route.
    """
    docket_id = int(result.case_id.rsplit("/", 1)[-1])
    in_scope = not gated or _in_predict_scope(corpus_db_path, result.case_id)
    events = open_events(corpus_db_path, "scotus", docket_id)
    if queue_predict and in_scope and result.changed and events:
        queues.predict.append({"court": "scotus", "docket": docket_id, "events": events})
    if in_scope and result.resolved:
        queues.evaluate.append({"court": "scotus", "docket": docket_id, "events": result.resolved})
    if result.reconcile_events:
        queues.reconcile.append(
            {
                "court": "scotus",
                "docket": docket_id,
                "events": result.reconcile_events,
                "reason": result.reconcile_reason,
            }
        )


def live_poll_all(
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    *,
    term: int,
    config: LiveConfig,
    scope: PredictScope = PredictScope.all,
    today: date,
) -> tuple[PullQueues, LiveDiscovery]:
    """One live cycle: frontier discovery, then the pending-petition refresh.

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
    """
    discovery = discover_live(
        client,
        corpus_db_path,
        data_root,
        term,
        max_new=config.max_new_cases_per_run,
        frontier_misses=config.frontier_misses,
        document_text_cap=config.document_text_cap,
        today=today,
    )
    queues = PullQueues()
    gated = scope == PredictScope.scotus_touched
    for onboarded in discovery.onboarded:
        # A brand-new row has no prior membership, so "distributed at all" is
        # the transition test for the discovery path.
        _route_result(
            queues,
            corpus_db_path,
            onboarded,
            gated=gated,
            queue_predict=onboarded.distributed is not None,
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
    )
    queues.predict.extend(refreshed.predict)
    queues.evaluate.extend(refreshed.evaluate)
    queues.reconcile.extend(refreshed.reconcile)
    queues.failed.extend(refreshed.failed)
    return queues, discovery
