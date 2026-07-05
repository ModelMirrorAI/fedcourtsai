"""The fixed corpus read set the integration-corpus workflow dispatches.

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
"""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, Field

from . import corpus, ids
from .corpus_ranged import RangedConnection
from .serialize import write_raw_json


class IntegrationStep(BaseModel):
    """One read of the fixed set: what it found and what it moved.

    ``gets`` / ``bytes_fetched`` are the read's ranged transfer counters —
    the egress evidence that a lookup moved KBs, not the blob — and ``None``
    on the local backend, where nothing is transferred.
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


def render_markdown(report: IntegrationReport) -> str:
    """The human summary of a report, for the Actions step summary."""
    lines = [
        f"## Corpus integration check — {report.case_id} [{report.backend}]",
        "",
        "| read | result | detail | transfer | seconds |",
        "| --- | --- | --- | --- | --- |",
    ]
    for step in report.steps:
        transfer = (
            f"{step.gets} GET(s), {step.bytes_fetched} byte(s)"
            if step.gets is not None and step.bytes_fetched is not None
            else "n/a (local)"
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
