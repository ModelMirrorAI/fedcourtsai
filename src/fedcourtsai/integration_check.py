"""The fixed corpus read set the integration-test workflow dispatches.

Three reads cover the shapes the pipeline provisions with, each run through the
corpus read-backend seam (:func:`fedcourtsai.corpus.connect_readonly`) on its
own connection, so on the ranged backend the per-connection transfer counters
mirror per-read egress:

* a **point lookup** — the case's open (predictable) events, the shape
  ``open-events`` and the predict queueing read;
* a **priors retrieval** — a narrow indexed filter over the case's court, the
  shape ``query`` serves predictors;
* a **snapshot provisioning** — the case's latest dated snapshot, the shape
  ``provision-snapshot`` materializes for every agent cell.

Every read must come back non-empty and shape-plausible, and the whole set must
finish inside a generous wall-clock budget, so a pathology — a table scan where
a point lookup belongs, a block-cache regression — fails the check instead of
hiding in a run log. The decisions live here, typed and tested; the workflow
step is one ``fedcourts corpus-integration-check`` call.

:func:`resolve_integration_case` supplies that call its subject. Which case the
suite reads cannot be a static default: each deployment environment resolves its
own corpus pair, so a case named in one is simply absent from another, and any
one case drifts out of shape as its docket resolves. The resolver picks a
qualifying case out of the corpus the run actually holds.

:func:`run_mcp_check` is the same posture pointed at the other sidecar: a
minimal MCP client (initialize → tools/list over streamable HTTP) that proves
the tokenless CourtListener MCP sidecar completes the protocol handshake and
advertises tools — the surface every engine's cell config points at — without
spending a CourtListener call or needing the token at all.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

from . import corpus, corpus_service, ids, store
from .corpus_ranged import RangedConnection
from .schemas import Disposition
from .serialize import write_raw_json

# The hydration probe's survey width. The survey is a cheap index-only read
# (``full=False`` fetches no bodies) ranked newest-grant-first, so it must
# sweep wide enough to reach past the newest grants — whose opinions do not
# exist yet — into decided, enriched territory; on the production corpus 200
# granted rows span roughly two Terms.
HYDRATION_SURVEY_LIMIT = 200


# --- the run-time case resolver ------------------------------------------------

# How many candidates the resolver's bounded window admits. Wide enough that a
# run of scope- or gate-failing rows at the head does not exhaust it, narrow
# enough that the whole resolution stays a page or two of index over the ranged
# backend — and it caps the per-candidate snapshot reads too.
DEFAULT_CANDIDATE_SCAN = 25


class CaseResolutionError(RuntimeError):
    """No case in the scanned window is shaped for the integration suite."""


@dataclass(frozen=True)
class ResolvedCase:
    """The case the integration suite should run against, and the evidence for it."""

    court: str
    docket: int
    case_id: str
    last_live_polled: date | None
    snapshot_date: date
    open_event_ids: tuple[str, ...]
    scanned: int


def _docket_id(row: corpus.CorpusRow) -> int | None:
    """The numeric docket half of a row's ``case_id``, or ``None`` if it is not one.

    The inverse of :func:`fedcourtsai.ids.case_id`, kept defensive: the suite's
    ``--docket`` input is an integer, so a row whose id cannot round-trip through
    one is not a case the resolver can hand over, whatever else it qualifies on.
    """
    _, _, docket = row.case_id.partition("/")
    try:
        return int(docket)
    except ValueError:
        return None


def resolve_integration_case(
    *,
    corpus_db_path: Path,
    data_root: Path,
    court: str = "scotus",
    backend: corpus.CorpusBackend | None = None,
    scan_limit: int = DEFAULT_CANDIDATE_SCAN,
) -> ResolvedCase:
    """Pick a case the integration suite's read set and cells can actually run on.

    The suite needs a case that is **still predictable** (its event has not
    happened yet), **in predict scope**, and **snapshot-bearing** — the three
    properties a static default cannot keep, since each deployment environment
    resolves its own corpus pair and any one case drifts out of shape as its
    docket moves. Resolving at run time against the corpus the environment
    actually serves makes the same command correct on the production corpus and
    on the lean staging pair alike.

    Reads :func:`fedcourtsai.corpus.snapshot_bearing_open_cases`' bounded
    window — snapshotted, unresolved, unlatched, at least one open event,
    ordered **most recently live-polled first** — and returns the first
    candidate that also clears two further screens:

    * the full scope reason (:func:`fedcourtsai.corpus.out_of_scope_reason_full`,
      which adds the snapshot-aware rules the row-only latch cannot carry);
    * the **record gate the consumer itself applies** —
      :func:`fedcourtsai.store.forward_refusal_reason_from_parts` at the case
      baseline, the exact check ``provision-snapshot --refuse-terminal`` runs in
      the suite's cascade leg. Asking the real gate rather than approximating it
      is the point: the gate refuses on a latched *resolution date* as well as a
      disposition, so a cert-granted petition awaiting merits judgment reads as
      undisposed to a naive filter and is refused by the step that matters.

    Most-recently-live-polled-first is the ordering because the live channel
    stamps exactly the modern petitions the suite wants, and its newest stamp is
    the case whose row and stored snapshot best reflect the live docket.
    (Not ``last_pulled``: the pull governor rotates over the whole active set
    including the historical bulk import, so its freshest stamps are ancient
    dockets a repair sweep happened to touch.) Deterministic given a corpus, and
    bounded by ``scan_limit``.

    Two checks the suite's later steps own stay theirs: the textual terminal
    scan over the payload, and the snapshot staleness bound (which the
    integration harness deliberately leaves off, since a fixed case's snapshot
    ages on calendar time alone). Raises :class:`CaseResolutionError` — carrying
    the per-reason tally of what the window rejected — when nothing qualifies.
    """
    choice = corpus.resolve_backend(backend)
    rejected: Counter[str] = Counter()
    scanned = 0
    with corpus.connect_readonly(corpus_db_path, backend=choice) as conn:
        candidates = corpus.snapshot_bearing_open_cases(conn, court=court, limit=scan_limit)
        if not candidates and corpus.payload_reads_offloaded():
            # The window is keyed on the blob's `snapshots` table, which the
            # corpus split empties — so "no candidates" there means the index
            # cannot answer, not that no case qualifies. Say which it is rather
            # than reporting an unanswerable read as an absent case.
            raise CaseResolutionError(
                "cannot resolve a case under the corpus-split mode: the snapshot "
                "index the candidate window reads lives in the blob, and the "
                "split moves the payloads to the content store, so the window is "
                "empty by construction. Name the case explicitly, or resolve "
                "against a blob that carries its snapshot rows."
            )
        for row in candidates:
            scanned += 1
            docket = _docket_id(row)
            if docket is None:
                rejected["case id carries no integer docket"] += 1
                continue
            reason = corpus.out_of_scope_reason_full(conn, row)
            if reason is not None:
                rejected[reason] += 1
                continue
            events = corpus.events_for_case(conn, row.case_id)
            # The case baseline (no event id) is the shape the suite's cascade
            # leg provisions, so it is the shape the gate is asked about.
            refusal = store.forward_refusal_reason_from_parts(
                data_root, row.court, docket, "", events, row
            )
            if refusal is not None:
                rejected[refusal] += 1
                continue
            found = corpus.latest_snapshot(conn, row.case_id)
            if found is None:
                rejected["no stored snapshot"] += 1
                continue
            snapshot_date, payload = found
            if not payload:
                rejected["stored snapshot decodes to an empty object"] += 1
                continue
            open_ids = tuple(event.event_id for event in events if not event.resolved)
            if not open_ids:
                # The window's EXISTS said otherwise; treat a disagreeing read as
                # a rejection rather than handing over an eventless case.
                rejected["no open event"] += 1
                continue
            return ResolvedCase(
                court=row.court,
                docket=docket,
                case_id=row.case_id,
                last_live_polled=row.last_live_polled,
                snapshot_date=snapshot_date,
                open_event_ids=open_ids,
                scanned=scanned,
            )
    tally = (
        "; ".join(f"{reason} ({n})" for reason, n in sorted(rejected.items()))
        if rejected
        else "the blob stores no snapshot for any unresolved, unlatched case with an open event"
    )
    raise CaseResolutionError(
        f"no case in {court} is shaped for the integration suite: {scanned} "
        f"candidate(s) in a {scan_limit}-row window, none usable — {tally}. "
        f"Widen the scan limit, refresh the corpus, or name a case explicitly."
    )


class IntegrationStep(BaseModel):
    """One read of the fixed set: what it found and what it moved.

    ``gets`` / ``bytes_fetched`` are the read's ranged transfer counters —
    the egress evidence that a lookup moved KBs, not the blob — and ``None``
    wherever transfer is not a measured concept (the local backend, the MCP
    probe's steps).
    """

    name: str = Field(description="Which read shape this step exercises")
    ok: bool = Field(description="The read came back non-empty and shape-plausible")
    detail: str = Field(description="What was found, or why the step failed")
    gets: int | None = Field(default=None, ge=0, description="Ranged GETs; None when local")
    bytes_fetched: int | None = Field(
        default=None, ge=0, description="Ranged bytes fetched; None when local"
    )
    seconds: float = Field(ge=0.0, description="Wall clock this read took")


class IntegrationReport(BaseModel):
    """``fedcourts corpus-integration-check`` verdict, one per run.

    ``ok`` is the single pass/fail the workflow keys on: every step non-empty
    and the whole set inside the wall-clock budget. Machine JSON for the run
    log; :func:`render_markdown` is the human summary.
    """

    case_id: str = Field(description="The known case the point reads target")
    backend: str = Field(description="The corpus read backend the set ran on")
    steps: list[IntegrationStep] = Field(description="The fixed reads, in execution order")
    seconds: float = Field(ge=0.0, description="Wall clock for the whole set")
    budget_seconds: float = Field(ge=0.0, description="The budget the set must beat")
    within_budget: bool = Field(description="seconds <= budget_seconds")
    ok: bool = Field(description="Every step ok and the budget held")


def _run_step(
    name: str,
    corpus_db_path: Path,
    backend: corpus.CorpusBackend,
    read: Callable[[corpus.ReadConnection], tuple[bool, str]],
) -> IntegrationStep:
    """One read on its own connection, timed, with its transfer counters."""
    started = time.monotonic()
    with corpus.connect_readonly(corpus_db_path, backend=backend) as conn:
        ok, detail = read(conn)
        stats = conn.stats if isinstance(conn, RangedConnection) else None
    return IntegrationStep(
        name=name,
        ok=ok,
        detail=detail,
        gets=stats.gets if stats is not None else None,
        bytes_fetched=stats.bytes_fetched if stats is not None else None,
        seconds=time.monotonic() - started,
    )


def run_integration_check(
    *,
    corpus_db_path: Path,
    court: str,
    docket: int,
    limit: int = 5,
    budget_seconds: float = 300.0,
    backend: corpus.CorpusBackend | None = None,
    snapshot_out: Path | None = None,
) -> IntegrationReport:
    """Run the fixed read set against a known case and report every verdict.

    Runs all three reads even after a failure (each is independent evidence),
    records each one's result, transfer counters, and wall clock, and rolls
    them into one ``ok``. A backend that cannot serve at all (a misconfigured
    remote, a broken pointer) raises rather than reporting — that is a setup
    problem, not a read regression. ``snapshot_out`` materializes the
    provisioned snapshot like ``provision-snapshot`` does.
    """
    choice = corpus.resolve_backend(backend)
    case_id = ids.case_id(court, docket)

    def _open_events(conn: corpus.ReadConnection) -> tuple[bool, str]:
        row = corpus.get_row(conn, case_id)
        if row is None:
            return False, f"{case_id} is not in the corpus"
        if row.predict_excluded:
            return False, f"{case_id} is latched out of predict scope; pick another case"
        open_ids = [e.event_id for e in corpus.events_for_case(conn, case_id) if not e.resolved]
        if not open_ids:
            return False, f"{case_id} has no open events; pick another case"
        return True, ", ".join(open_ids)

    def _priors(conn: corpus.ReadConnection) -> tuple[bool, str]:
        query = corpus.PriorQuery(court=court)
        priors = corpus.retrieve_priors(conn, query, limit=limit)
        if not priors:
            return False, f"no resolved priors for court {court}"
        # Rows are CorpusRow-validated on read, so shape-plausible by construction.
        return True, f"{len(priors)} prior(s), first {priors[0].case_id}"

    def _snapshot(conn: corpus.ReadConnection) -> tuple[bool, str]:
        found = corpus.latest_snapshot(conn, case_id)
        if found is None:
            return False, f"no snapshot in the corpus for {case_id}"
        snapshot_date, payload = found
        if not payload:
            return False, f"snapshot {snapshot_date.isoformat()} decoded to an empty object"
        if snapshot_out is not None:
            write_raw_json(snapshot_out, payload)
        return True, f"snapshot {snapshot_date.isoformat()}, {len(payload)} top-level key(s)"

    started = time.monotonic()
    steps = [
        _run_step("open-events", corpus_db_path, choice, _open_events),
        _run_step(f"priors (court {court}, limit {limit})", corpus_db_path, choice, _priors),
        _run_step("provision-snapshot", corpus_db_path, choice, _snapshot),
    ]
    seconds = time.monotonic() - started
    within_budget = seconds <= budget_seconds
    return IntegrationReport(
        case_id=case_id,
        backend=choice,
        steps=steps,
        seconds=seconds,
        budget_seconds=budget_seconds,
        within_budget=within_budget,
        ok=within_budget and all(step.ok for step in steps),
    )


def run_service_check(
    *,
    service_url: str,
    court: str,
    docket: int,
    limit: int = 5,
    budget_seconds: float = 300.0,
) -> IntegrationReport:
    """The service-backend counterpart of the fixed read set.

    Probes the corpus query sidecar through the same client the CLI's
    ``service`` backend forwards with — the exact surface a cell retrieves
    from — so a green run proves the sidecar serves non-empty priors and open
    events for the known case. Three reads on the two endpoints the service
    exposes, ``query`` and ``open-events`` (snapshot provisioning is a
    deterministic workflow step's read, not a cell surface): the plain query,
    the open events, and the full-query hydration probe below. Per-read
    transfer counters come from the service's per-request deltas; a transport
    failure or refusal raises
    (:class:`~fedcourtsai.corpus_service.CorpusServiceError` — a setup
    problem, not a read regression), while an empty result reports as a
    failed step.

    The **hydration probe** guards the opinion-body path, which degrades to
    ``None`` at every layer rather than raising (so a dead content store
    cannot truncate a query stream — see :func:`fedcourtsai.corpus.prior_payload`),
    and would therefore pass every other read while returning bodiless rows to
    every cell. A cheap ``full=False`` survey of granted priors finds the
    first opinion-bearing row; the identical query re-asked with ``full=True``
    and a limit just past that row's rank must — ranking is deterministic —
    return the very row the survey found, and the probe fails if any returned
    row that claims an opinion hydrates an empty body, or if the targeted row
    is missing. Judging the rows the survey actually found is the point: a
    fixed-size window ranked newest-first would sample exactly the grants
    whose opinions do not exist yet and report their absence as health. Only
    a survey with **no** opinion-bearing row at all reports **ok with an
    UNVERIFIED note** rather than failing: before the first enrichment run
    there is nothing to certify, and nothing live reads bodies either.
    """
    case_id = ids.case_id(court, docket)
    started = time.monotonic()

    t0 = time.monotonic()
    query = corpus_service.client_query(
        service_url, corpus.PriorQuery(court=court), limit=limit, full=False
    )
    if query.rows:
        detail = f"{len(query.rows)} prior(s), first {query.rows[0].get('case_id')}"
    else:
        # The service's data-coverage notes explain a sparse-filter empty
        # result; surface them so the failed step reads as diagnosis.
        detail = "; ".join([f"no resolved priors for court {court}", *query.notes])
    steps = [
        IntegrationStep(
            name=f"service query (court {court}, limit {limit})",
            ok=bool(query.rows),
            detail=detail,
            gets=query.reads.gets if query.reads is not None else None,
            bytes_fetched=query.reads.bytes if query.reads is not None else None,
            seconds=time.monotonic() - t0,
        )
    ]

    t0 = time.monotonic()
    events = corpus_service.client_open_events(service_url, court, docket)
    steps.append(
        IntegrationStep(
            name="service open-events",
            ok=bool(events.event_ids),
            detail=", ".join(events.event_ids)
            if events.event_ids
            else f"{case_id} has no open events; pick another case",
            gets=events.reads.gets if events.reads is not None else None,
            bytes_fetched=events.reads.bytes if events.reads is not None else None,
            seconds=time.monotonic() - t0,
        )
    )

    t0 = time.monotonic()
    survey = corpus_service.client_query(
        service_url,
        corpus.PriorQuery(court=court, disposition=Disposition.granted),
        limit=HYDRATION_SURVEY_LIMIT,
        full=False,
    )
    first_bearing = next(
        (rank for rank, row in enumerate(survey.rows) if row.get("has_opinion")), None
    )
    if first_bearing is None:
        ok = True
        detail = (
            f"no opinion-bearing prior among {len(survey.rows)} granted row(s) surveyed — "
            "hydration UNVERIFIED until an enrichment pass has landed opinion bodies"
        )
        hydrated = None
    else:
        # The identical query, re-asked with bodies, cut just past the first
        # bearing row's rank: ranking is deterministic (relevance, recency,
        # case_id), so the response must contain that exact row — hydration is
        # judged on the rows the survey actually found, never on a window that
        # might miss them, and the row's absence is itself a failure. Bodies
        # are fetched only for opinion-bearing rows, so the wider limit costs
        # index bytes, not content-store GETs.
        target_id = str(survey.rows[first_bearing].get("case_id"))
        hydrated = corpus_service.client_query(
            service_url,
            corpus.PriorQuery(court=court, disposition=Disposition.granted),
            limit=first_bearing + 1,
            full=True,
        )
        claimed = [row for row in hydrated.rows if row.get("has_opinion")]
        empty = [
            str(row.get("case_id"))
            for row in claimed
            if not str(row.get("opinion_text") or "").strip()
        ]
        if not any(str(row.get("case_id")) == target_id for row in claimed):
            ok = False
            detail = (
                f"the hydration query did not return the opinion-bearing row it "
                f"targeted ({target_id}, survey rank {first_bearing + 1}) — "
                "ranking drifted between reads"
            )
        elif empty:
            ok = False
            detail = (
                f"{len(empty)} of {len(claimed)} opinion-bearing prior(s) hydrated no "
                f"body (content store unreachable or inconsistent): " + ", ".join(empty[:5])
            )
        else:
            ok = True
            detail = f"{len(claimed)} opinion-bearing prior(s), every body hydrated"
    # The hydration read's counters only: the step's egress evidence is the
    # content-store fetch, not the survey's index sweep.
    reads = hydrated.reads if hydrated is not None else None
    steps.append(
        IntegrationStep(
            name="service full-query hydration",
            ok=ok,
            detail=detail,
            gets=reads.gets if reads is not None else None,
            bytes_fetched=reads.bytes if reads is not None else None,
            seconds=time.monotonic() - t0,
        )
    )

    seconds = time.monotonic() - started
    within_budget = seconds <= budget_seconds
    return IntegrationReport(
        case_id=case_id,
        backend="service",
        steps=steps,
        seconds=seconds,
        budget_seconds=budget_seconds,
        within_budget=within_budget,
        ok=within_budget and all(step.ok for step in steps),
    )


class McpCheckReport(BaseModel):
    """``fedcourts mcp-integration-check`` verdict, one per run.

    The MCP-sidecar sibling of :class:`IntegrationReport`: same steps/budget
    shape (so the CLI renders and finishes both the same way), keyed on the
    probed endpoint URL instead of a corpus case and backend.
    """

    url: str = Field(description="The MCP endpoint the probe spoke to")
    steps: list[IntegrationStep] = Field(description="The protocol probes, in execution order")
    seconds: float = Field(ge=0.0, description="Wall clock for the whole probe")
    budget_seconds: float = Field(ge=0.0, description="The budget the probe must beat")
    within_budget: bool = Field(description="seconds <= budget_seconds")
    ok: bool = Field(description="Every step ok and the budget held")


class McpProbeError(RuntimeError):
    """The MCP sidecar cannot be probed at all — transport failure, a
    non-success HTTP status, a body that is not a JSON-RPC response, or a
    JSON-RPC *error* reply (a refusal to converse, e.g. rejecting the
    protocol version, is graded with the setup problems rather than the
    protocol disappointments). Mirrors how the corpus checks treat an
    unreachable backend."""


# The protocol revision the pinned CourtListener MCP release speaks; the server
# echoes the version it settles on, which the initialize step's detail records.
_MCP_PROTOCOL_VERSION = "2025-03-26"


def _mcp_post(
    client: httpx.Client, url: str, payload: dict[str, object], session_id: str | None
) -> httpx.Response:
    """One streamable-HTTP POST to the MCP endpoint; raises on transport failure."""
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if session_id is not None:
        headers["Mcp-Session-Id"] = session_id
    try:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise McpProbeError(f"MCP endpoint {url} unreachable or refusing: {exc}") from exc
    return response


def _mcp_result(response: httpx.Response) -> dict[str, object]:
    """The JSON-RPC result object from a JSON or SSE-framed response body."""
    content_type = response.headers.get("content-type", "")
    message: object = None
    if "text/event-stream" in content_type:
        # Streamable HTTP may frame the response as one-shot SSE; the reply is
        # the first data event carrying a JSON-RPC result or error.
        for line in response.text.splitlines():
            if not line.startswith("data:"):
                continue
            try:
                candidate = json.loads(line.removeprefix("data:").strip())
            except ValueError:
                # A ping payload or a multi-line data field split by this
                # line-by-line parse; keep scanning for the JSON-RPC reply.
                continue
            if isinstance(candidate, dict) and ("result" in candidate or "error" in candidate):
                message = candidate
                break
    else:
        message = response.json()
    if not isinstance(message, dict):
        raise McpProbeError(f"no JSON-RPC response in a {content_type or 'untyped'} body")
    if "error" in message:
        raise McpProbeError(f"JSON-RPC error: {message['error']}")
    result = message.get("result")
    if not isinstance(result, dict):
        raise McpProbeError("JSON-RPC response carried no result object")
    return result


def run_mcp_check(
    *, mcp_url: str, budget_seconds: float = 120.0, expected_tools: list[str] | None = None
) -> McpCheckReport:
    """Probe the MCP sidecar: complete the handshake, list the tools.

    Two steps, mirroring the corpus checks' shape: ``initialize`` must return
    a named server (the detail records name, version, and the negotiated
    protocol revision), and ``tools/list`` must advertise at least one tool
    (the detail names them). Token-free by design — no tool is *called*, so
    the probe exercises exactly what a cell's engine client needs before its
    first CourtListener call, and a sidecar launched without the token still
    checks green. Transport failures raise :class:`McpProbeError`; a
    protocol-level disappointment (no server name, an empty tool list)
    reports as a failed step.

    ``expected_tools`` adds a third step: the manifest's recorded ``tools`` for
    this pin, compared against what the server actually advertises. The
    manifest list is the offered denominator every retrieval log snapshots, and
    it is captured by hand at pin time — so without this check a version bump
    that adds or drops a tool leaves it silently wrong, and every later
    offered-vs-called rollup inherits the error. Drift fails the step and names
    both directions; an empty/omitted list skips it rather than asserting the
    server offers nothing.
    """
    started = time.monotonic()
    steps: list[IntegrationStep] = []
    with httpx.Client(timeout=30.0) as client:
        t0 = time.monotonic()
        response = _mcp_post(
            client,
            mcp_url,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": _MCP_PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "fedcourts-mcp-integration-check", "version": "0"},
                },
            },
            None,
        )
        session_id = response.headers.get("mcp-session-id")
        result = _mcp_result(response)
        server_info = result.get("serverInfo")
        if isinstance(server_info, dict) and server_info.get("name"):
            initialized = True
            detail = (
                f"{server_info.get('name')} {server_info.get('version', '?')} "
                f"(protocol {result.get('protocolVersion', '?')})"
            )
        else:
            initialized = False
            detail = "initialize returned no serverInfo.name"
        steps.append(
            IntegrationStep(
                name="initialize", ok=initialized, detail=detail, seconds=time.monotonic() - t0
            )
        )

        # The handshake's completion notification — required before further
        # requests; a notification, so there is no result to parse.
        _mcp_post(
            client, mcp_url, {"jsonrpc": "2.0", "method": "notifications/initialized"}, session_id
        )

        t0 = time.monotonic()
        response = _mcp_post(
            client, mcp_url, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, session_id
        )
        tools = _mcp_result(response).get("tools")
        names = (
            [str(t["name"]) for t in tools if isinstance(t, dict) and t.get("name")]
            if isinstance(tools, list)
            else []
        )
        steps.append(
            IntegrationStep(
                name="tools/list",
                ok=bool(names),
                detail=", ".join(names) if names else "the server advertises no tools",
                seconds=time.monotonic() - t0,
            )
        )
        if expected_tools:
            advertised, expected = set(names), set(expected_tools)
            missing = sorted(expected - advertised)
            added = sorted(advertised - expected)
            parts = []
            if missing:
                parts.append(f"recorded but not advertised: {', '.join(missing)}")
            if added:
                parts.append(f"advertised but not recorded: {', '.join(added)}")
            steps.append(
                IntegrationStep(
                    name="manifest tools",
                    ok=not parts,
                    detail=" · ".join(parts)
                    if parts
                    else f"manifest matches the server ({len(expected)} tool(s))",
                    seconds=0.0,
                )
            )

    seconds = time.monotonic() - started
    within_budget = seconds <= budget_seconds
    return McpCheckReport(
        url=mcp_url,
        steps=steps,
        seconds=seconds,
        budget_seconds=budget_seconds,
        within_budget=within_budget,
        ok=within_budget and all(step.ok for step in steps),
    )


def render_markdown(report: IntegrationReport | McpCheckReport) -> str:
    """The human summary of a report, for the Actions step summary."""
    if isinstance(report, McpCheckReport):
        title = f"## CourtListener MCP check — {report.url}"
    else:
        title = f"## Corpus integration check — {report.case_id} [{report.backend}]"
    lines = [
        title,
        "",
        "| read | result | detail | transfer | seconds |",
        "| --- | --- | --- | --- | --- |",
    ]
    for step in report.steps:
        transfer = (
            f"{step.gets} GET(s), {step.bytes_fetched} byte(s)"
            if step.gets is not None and step.bytes_fetched is not None
            else "n/a"
        )
        verdict = "ok" if step.ok else "**FAILED**"
        lines.append(
            f"| {step.name} | {verdict} | {step.detail} | {transfer} | {step.seconds:.2f} |"
        )
    budget = "within" if report.within_budget else "**OVER**"
    lines += [
        "",
        f"Wall clock: {report.seconds:.1f}s — {budget} the {report.budget_seconds:.0f}s budget.",
        "",
    ]
    return "\n".join(lines)
