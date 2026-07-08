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
discovery. Both ``seed`` and ``pull`` drive this function.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from .. import corpus, ids
from ..config import PredictScope
from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_transient
from ..store import open_events
from .events import AmbiguousEntry, extract_events
from .ingest import from_api_docket, upsert_to_corpus
from .outcome import ReconcileRequest, resolve_case
from .recoverability import build_cluster_info, first_cluster_id

# The decision-time fields a docket record may carry; a record with none of them
# is dateless and a candidate for the linked-cluster enrichment below.
_DECISION_DATE_KEYS = ("date_terminated", "date_decided", "date_cert_granted", "date_cert_denied")


def _enrich_dateless_from_cluster(
    client: CourtListenerClient, docket: dict[str, Any]
) -> dict[str, Any]:
    """Fill a dateless docket's decision facts from its linked opinion cluster.

    The historical bulk-era slice carries no docket-level dates even on a fresh
    fetch — the decision date lives on the linked opinion cluster (its
    ``date_filed``), alongside the reporter citation and sometimes a disposition
    string. When the docket record has no decision-time date but links a
    cluster, spend one extra request on the cluster and gap-fill the record
    *upstream-shaped*, so the shared normalizer ingests it like any other source
    field:

    - cluster ``date_filed`` → ``date_decided`` — termination semantics in every
      case: for a denied petition the cluster is the denial order (petition-stage
      ≈ termination), while for a granted one it is the *merits opinion*, whose
      date is the termination, never the grant — so the cert-stage columns are
      deliberately not written here.
    - cluster disposition / citations → the same keys, only when the docket
      carries none.

    Returns the docket unchanged when it is dated, links no cluster, or the
    cluster fetch fails (enrichment must never fail the refresh). Pure gap-fill:
    a docket-level fact always wins over the cluster's.
    """
    if any(docket.get(key) for key in _DECISION_DATE_KEYS):
        return docket
    cluster_id = first_cluster_id(docket)
    if cluster_id is None:
        return docket
    try:
        info = build_cluster_info(client.get_opinion_cluster(cluster_id))
    except httpx.HTTPError:
        return docket
    enriched = dict(docket)
    if info.date_filed:
        enriched["date_decided"] = info.date_filed
    if info.raw_disposition and not any(
        docket.get(key) for key in ("disposition", "outcome", "nature_of_judgement")
    ):
        enriched["disposition"] = info.raw_disposition
    if info.citations and not docket.get("citations"):
        enriched["citations"] = info.citations
    return enriched


@dataclass
class PullResult:
    case_id: str
    changed: bool
    # Identifier of the snapshot stored in the corpus this refresh (its date).
    # Predictors record it as ``input_snapshot``; the corpus is the store.
    snapshot: str
    # Outcome detection (`pull`'s third job): events resolved deterministically
    # this refresh, and those that appear decided but need an agent to reconcile.
    resolved: list[str]
    reconcile: list[ReconcileRequest]
    # Docket entries that read like a request but match more than one event kind,
    # so extraction did not guess an event for them (mirrors discovery). Collected
    # for triage; not queued.
    ambiguous: list[AmbiguousEntry] = field(default_factory=list)


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

    # The normalized row (not the snapshot — that stays the raw docket) reads
    # through the cluster enrichment, so a dateless historical docket gains its
    # decision date from the linked opinion cluster on the same refresh.
    row = from_api_docket(_enrich_dateless_from_cluster(client, fresh))
    # Stamp the corpus tracking state so the budget governor can rotate this case
    # to the back of the oldest-`last_pulled`-first queue on the next run.
    upsert_to_corpus(corpus_db_path, [row], last_pulled=today)

    # Detect resolution of any open events: write outcome.json deterministically
    # when the disposition is machine-readable, else flag for agent reconcile.
    # Runs *before* re-extraction: `default_event` marks a decided case's baseline
    # resolved (from its disposition), so resolution must see the event still open
    # to record its outcome before extraction latches it closed.
    resolution = resolve_case(corpus_db_path, data_root, row, court_id, docket_id)

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
        reconcile=list(resolution.reconciles),
        ambiguous=list(extraction.ambiguous),
    )


@dataclass
class PullQueues:
    """The three downstream handoffs a ``pull-all`` run produces.

    Each entry is a JSON-serializable mapping shaped exactly as the ``run-pull``
    workflow consumes it (the ``jq`` fields in ``run-pull.yml``): ``predict`` and
    ``evaluate`` entries carry ``court`` / ``docket`` / ``events``; ``reconcile``
    adds the agent-facing ``reason``.
    """

    predict: list[dict[str, object]] = field(default_factory=list)
    evaluate: list[dict[str, object]] = field(default_factory=list)
    reconcile: list[dict[str, object]] = field(default_factory=list)
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
    """Whether a case is in predict scope: SCOTUS-eligible *and* not excluded.

    Reads the latched ``predict_eligible`` flag and applies the same exclusion
    reasoning the matrix backstop uses (``corpus.out_of_scope_reason_full`` — the
    row rules plus the snapshot-aware bare opinion-import rule). Checking it here,
    at queue time, means pull never opens a ``run-predict`` issue for a case the
    gate would only drop — so a batch of nothing-but-out-of-scope cases never
    files an empty run (the live evaluation also covers cases the seed reconcile
    has not yet latched ``predict_excluded``).
    """
    with corpus.connect(corpus_db_path) as conn:
        row = corpus.get_row(conn, case_id)
        return bool(
            row and row.predict_eligible and corpus.out_of_scope_reason_full(conn, row) is None
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
    """Refresh each due case and sort it into the predict / evaluate / reconcile queues.

    The per-case half of ``pull-all``: for every ``(court, docket)`` the rotation
    governor selected, refresh the docket (:func:`pull_case`, which also detects
    resolution), then route the result — a *changed* case with open events to
    ``predict``, a case that gained an ``outcome.json`` this run to ``evaluate``,
    and a case that appears decided but could not be recorded deterministically to
    ``reconcile``. Case selection (discovery + rotation) stays with the caller, so
    this seam composes the same way the CLI's ``pull-all`` does.

    The prediction-scope gate is the primary cost-saver: under
    ``scope == scotus_touched`` an out-of-scope case never reaches the ``predict``
    or ``evaluate`` queue, so it never opens a ``run-predict`` / ``run-evaluate``
    issue. ``reconcile`` stays ungated — it records ground truth for the corpus /
    back-testing, a different purpose from prediction spend. ``scope == all``
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
    gated = scope == PredictScope.scotus_touched
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
            queues.predict.append({"court": court, "docket": docket, "events": events})
        if in_scope and result.resolved:
            queues.evaluate.append({"court": court, "docket": docket, "events": result.resolved})
        if result.reconcile:
            queues.reconcile.append(
                {
                    "court": court,
                    "docket": docket,
                    "events": [r.event_id for r in result.reconcile],
                    "reason": result.reconcile[0].reason,
                }
            )
    return queues
