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

:func:`run_mcp_check` is the same posture pointed at the other sidecar: a
minimal MCP client (initialize → tools/list over streamable HTTP) that proves
the tokenless CourtListener MCP sidecar completes the protocol handshake and
advertises tools — the surface every engine's cell config points at — without
spending a CourtListener call or needing the token at all.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

from . import corpus, corpus_service, ids
from .corpus_ranged import RangedConnection
from .serialize import write_raw_json


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
    events for the known case. Two reads: the service exposes ``query`` and
    ``open-events`` only (snapshot provisioning is a deterministic workflow
    step's read, not a cell surface). Per-read transfer counters come from the
    service's per-request deltas; a transport failure or refusal raises
    (:class:`~fedcourtsai.corpus_service.CorpusServiceError` — a setup
    problem, not a read regression), while an empty result reports as a
    failed step.
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


def run_mcp_check(*, mcp_url: str, budget_seconds: float = 120.0) -> McpCheckReport:
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
