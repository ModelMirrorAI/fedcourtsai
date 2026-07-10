"""The past-Term cert loader: build the back-test set through the live channel.

The back-test half of the live-sources design (docs/live-sources.md): the
supremecourt.gov docket JSON serves every decided petition of the e-filing era
(OT2017+, per docs/live-sources-probe.md), through the identical client,
mapping, identity, and ingest seams the forward poller uses — so the back-test
set is built with the actual instrument, not a proxy. Run by the ``run-seed``
workflow's ``live-terms`` mode via ``fedcourts seed-live-terms``.

How it differs from :func:`~fedcourtsai.pipeline.live.discover_live`, the
forward frontier prober:

- **It walks whole decided Terms, not a frontier.** Each configured Term's two
  numbering streams (paid petitions from 1, IFP from 5001) are walked
  sequentially to their end — ``frontier_misses`` consecutive 404s — under
  per-invocation probe and wall-clock caps, resuming from a persisted cursor.
  The cursors live in the same ``live_discovery_cursors`` table as the forward
  poller's, under the distinct stream names ``seed-paid`` / ``seed-ifp``, so
  the two walkers can never collide on a (term, stream) key. The cursor
  advances over every *served* serial — ingested or sampled out — so a skipped
  denial is never re-probed; a 404 never advances it, so a resumed run
  re-confirms the frontier cheaply.
- **It samples deliberately instead of ingesting the sequence.** A Term is
  overwhelmingly denials, so each served record's disposition is read from its
  proceedings text first (:func:`~fedcourtsai.pipeline.cert_signals.match_disposition_signal`,
  the same patterns ingest-time resolution runs): every decided petition is
  ingested **except denials, which are kept only when their serial is a
  multiple of ``denial_sample_every``** — a systematic sample over the docket
  sequence, deterministic per serial and therefore reproducible across resumed
  runs. The frame and ratio live in ``tracking.yaml``'s ``seed_live:`` section
  so the set's construction is documented. A record with no machine-readable
  disposition (a still-pending or held petition) is skipped entirely — pending
  matters are the forward poller's charter, and skipping them here keeps this
  loader's guarantee absolute: **it writes no predict/evaluate/reconcile
  queues, and every row it ingests lands already RESOLVED**, so the pending
  rotation (``corpus.live_rotation``) never picks it up either.
- **Documents follow the probe's floor.** An ingested petition from
  ``document_floor_term`` (~OT2021) onward gets its filed documents provisioned
  (:func:`~fedcourtsai.pipeline.live.provision_documents`) to feed
  document-rich replay cells; older Terms skip the fetch — the links are not
  served — and load as metadata+proceedings-only rows.

Ingestion itself is the shared live path
(:func:`~fedcourtsai.pipeline.live.ingest_live_payload`): identity reconciled
by docket number onto any existing SCOTUS row (else the deterministic
reserved-range live id), raw JSON stored as the dated snapshot, the normalized
resolved row upserted, ``outcome.json`` recorded, and events extracted — so a
loaded petition provisions replay cells exactly like a forward-tracked one.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from dataclasses import field as dataclasses_field
from datetime import date
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

from .. import corpus
from ..config import SeedLiveConfig
from ..schemas import Disposition
from ..supremecourt import IFP_SERIAL_BASE, SupremeCourtClient
from .cert_signals import match_disposition_signal
from .live import _resolve_identity, ingest_live_payload, provision_documents

# The loader's per-Term numbering streams. Same bases as the forward poller's,
# distinct cursor names so the two walkers never share a (term, stream) key in
# `live_discovery_cursors` (the forward frontier uses "paid" / "ifp").
SEED_STREAMS: tuple[tuple[str, int], ...] = (("seed-paid", 1), ("seed-ifp", IFP_SERIAL_BASE))

# The walk's cap probe: `None` keeps walking; a non-None reason stops it.
type OutOf = Callable[[], str | None]


class StreamProgress(BaseModel):
    """One (Term, stream) walk's state after this invocation."""

    term: int
    stream: str
    cursor: int | None
    """Highest serial confirmed served (persisted; ``None`` = never probed)."""
    frontier_reached: bool
    """Whether this invocation observed the stream's end (consecutive 404s)."""


class SeedLiveReport(BaseModel):
    """The ``--report`` payload: this invocation's counts + overall walk state."""

    probed: int = 0
    """Docket-JSON fetches this invocation (the capped unit)."""
    served: int = 0
    ingested_granted: int = 0
    """Grants and GVRs — everything on the granted side is kept."""
    ingested_denied: int = 0
    """The systematic denial sample (serial % denial_sample_every == 0)."""
    ingested_other: int = 0
    """Other decided dispositions (dismissed etc.) — rare, all kept."""
    skipped_denials: int = 0
    skipped_undecided: int = 0
    """Served records with no machine-readable disposition (left to the
    forward poller; never ingested here)."""
    documents: int = 0
    """Filed documents provisioned for OT``document_floor_term``+ ingests."""
    reconcile_flagged: int = 0
    """Ingested petitions whose resolution needed a reconcile signal — should
    be zero (the disposition matched before ingest); surfaced for triage."""
    failed: list[dict[str, object]] = Field(default_factory=list)
    """(term, stream, serial, reason) for streams stopped by upstream errors;
    their cursors are untouched, so the next invocation retries gap-free."""
    complete: bool = False
    """Every configured (term, stream) frontier was observed this invocation."""
    stopped: str = "complete"
    """Why the walk ended: complete | probe-cap | time-cap | stream-errors."""
    streams: list[StreamProgress] = Field(default_factory=list)


def _payload_disposition(payload: Mapping[str, Any]) -> Disposition | None:
    """The cert disposition the record's proceedings text carries, or ``None``.

    First match in docket order over the same entry text ingest-time resolution
    reads, so the sampling decision always agrees with the label the ingested
    row will land with.
    """
    for entry in payload.get("ProceedingsandOrder") or []:
        if not isinstance(entry, Mapping):
            continue
        matched = match_disposition_signal(str(entry.get("Text") or ""))
        if matched is not None:
            return matched[0]
    return None


def _keep(disposition: Disposition | None, serial: int, sample_every: int) -> bool:
    """The sampling frame: all decided kept, except denials sampled by serial."""
    if disposition is None:
        return False
    if disposition == Disposition.denied:
        return serial % sample_every == 0
    return True


@dataclass
class _Walk:
    """One invocation's walk state: the shared handles and its running report."""

    client: SupremeCourtClient
    corpus_db_path: Path
    data_root: Path
    config: SeedLiveConfig
    today: date
    report: SeedLiveReport = dataclasses_field(default_factory=SeedLiveReport)

    def walk_stream(self, term: int, stream: str, base: int, out_of: OutOf) -> None:
        """Walk one (Term, stream) from its cursor to frontier, cap, or error."""
        report = self.report
        with corpus.connect(self.corpus_db_path) as conn:
            cursor = corpus.get_live_cursor(conn, term, stream)
        serial = (cursor + 1) if cursor is not None else base
        misses = 0
        while misses < self.config.frontier_misses and out_of() is None:
            try:
                payload = self.client.get_docket(term, serial)
            except httpx.HTTPError as exc:
                # Stream stops (cursor untouched -> gap-free retry next
                # invocation); the walk moves on to the next stream/Term.
                report.failed.append(
                    {
                        "term": term,
                        "stream": stream,
                        "serial": serial,
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                )
                break
            report.probed += 1
            if payload is None:
                misses += 1
                serial += 1
                continue
            misses = 0
            report.served += 1
            disposition = _payload_disposition(payload)
            if disposition is None:
                report.skipped_undecided += 1
            elif _keep(disposition, serial, self.config.denial_sample_every):
                self.ingest(payload, term, serial, disposition)
            else:
                report.skipped_denials += 1
            # The cursor covers every served serial — sampled out or not — so
            # a resumed walk never re-reads a skipped denial. (404s do not
            # advance it: the frontier is re-confirmed, cheaply.)
            with corpus.connect(self.corpus_db_path) as conn:
                corpus.set_live_cursor(conn, term, stream, serial)
            serial += 1
        with corpus.connect(self.corpus_db_path) as conn:
            stored = corpus.get_live_cursor(conn, term, stream)
        report.streams.append(
            StreamProgress(
                term=term,
                stream=stream,
                cursor=stored,
                frontier_reached=misses >= self.config.frontier_misses,
            )
        )

    def ingest(self, payload: dict[str, Any], term: int, serial: int, label: Disposition) -> None:
        """Land one sampled decided petition through the shared live-ingest path."""
        report = self.report
        with corpus.connect(self.corpus_db_path) as conn:
            docket_id = _resolve_identity(conn, payload, term, serial)
        result = ingest_live_payload(
            self.corpus_db_path, self.data_root, payload, docket_id, today=self.today
        )
        if label == Disposition.granted:
            report.ingested_granted += 1
        elif label == Disposition.denied:
            report.ingested_denied += 1
        else:
            report.ingested_other += 1
        report.reconcile_flagged += len(result.reconcile_events)
        if term >= self.config.document_floor_term:
            try:
                report.documents += provision_documents(
                    self.client,
                    self.corpus_db_path,
                    result.case_id,
                    payload,
                    char_cap=self.config.document_text_cap,
                    today=self.today,
                )
            except httpx.HTTPError as exc:
                # The row is already landed; a document fetch that degrades
                # past the client's retry costs the documents, never the petition.
                report.failed.append(
                    {
                        "term": term,
                        "stream": "documents",
                        "serial": serial,
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                )


def load_terms(
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    config: SeedLiveConfig,
    *,
    today: date,
    clock: Callable[[], float] = time.monotonic,
) -> SeedLiveReport:
    """One capped invocation of the past-Term walk; resumes from the cursors.

    Walks ``config.terms`` in order, each Term's ``seed-paid`` then ``seed-ifp``
    stream, until every stream's frontier is observed or a per-invocation cap
    (``max_probes_per_run`` docket fetches; ``max_run_minutes`` wall clock,
    checked between serials) stops the walk. An upstream error stops only its
    stream — cursor untouched, next invocation retries the same serial — and
    never aborts the invocation. Returns the report the run-seed loop reads for
    its stop conditions and progress comment.
    """
    walk = _Walk(client, corpus_db_path, data_root, config, today)
    deadline = clock() + config.max_run_minutes * 60

    def out_of() -> str | None:
        if walk.report.probed >= config.max_probes_per_run:
            return "probe-cap"
        if clock() >= deadline:
            return "time-cap"
        return None

    for term in config.terms:
        for stream, base in SEED_STREAMS:
            walk.walk_stream(term, stream, base, out_of)
            capped = out_of()
            if capped is not None:
                walk.report.stopped = capped
                return walk.report
    walk.report.complete = all(s.frontier_reached for s in walk.report.streams)
    walk.report.stopped = "complete" if walk.report.complete else "stream-errors"
    return walk.report


def fold_totals(totals: SeedLiveReport | None, latest: SeedLiveReport) -> SeedLiveReport:
    """Fold one invocation's report into a run's cumulative totals.

    The run-seed loop invokes ``seed-live-terms`` many times per job (each
    invocation is one checkpoint chunk); the totals file is what the run's
    single progress comment renders. Counters and failures accumulate; the walk
    state — per-(Term, stream) progress, ``complete``, ``stopped`` — is the
    latest invocation's view (its cursors already encode all prior progress).
    """
    if totals is None:
        return latest.model_copy(deep=True)
    merged = {(s.term, s.stream): s for s in totals.streams}
    merged.update({(s.term, s.stream): s for s in latest.streams})
    return SeedLiveReport(
        probed=totals.probed + latest.probed,
        served=totals.served + latest.served,
        ingested_granted=totals.ingested_granted + latest.ingested_granted,
        ingested_denied=totals.ingested_denied + latest.ingested_denied,
        ingested_other=totals.ingested_other + latest.ingested_other,
        skipped_denials=totals.skipped_denials + latest.skipped_denials,
        skipped_undecided=totals.skipped_undecided + latest.skipped_undecided,
        documents=totals.documents + latest.documents,
        reconcile_flagged=totals.reconcile_flagged + latest.reconcile_flagged,
        failed=[*totals.failed, *latest.failed],
        complete=latest.complete,
        stopped=latest.stopped,
        streams=[merged[key] for key in sorted(merged, reverse=True)],
    )


def render_markdown(report: SeedLiveReport) -> str:
    """The report as the run-seed progress comment / step-summary body."""
    ingested = report.ingested_granted + report.ingested_denied + report.ingested_other
    lines = [
        "### Past-Term cert loader progress" + (" — walk complete ✅" if report.complete else ""),
        "",
        f"Probed **{report.probed}** serial(s) ({report.served} served); ingested "
        f"**{ingested}** decided petition(s) — {report.ingested_granted} granted/GVR, "
        f"{report.ingested_denied} sampled denial(s), {report.ingested_other} other — "
        f"skipped {report.skipped_denials} denial(s) and {report.skipped_undecided} "
        f"undecided; provisioned {report.documents} document(s).",
        "",
        "| OT | Stream | Serial reached | Frontier |",
        "|----|--------|---------------:|:--------:|",
    ]
    for s in report.streams:
        lines.append(
            f"| {s.term} | {s.stream} | {s.cursor if s.cursor is not None else '—'} "
            f"| {'✅' if s.frontier_reached else ''} |"
        )
    if report.failed:
        lines += ["", f"⚠️ {len(report.failed)} stream error(s); those cursors will retry."]
    if report.reconcile_flagged:
        lines += ["", f"⚠️ {report.reconcile_flagged} ingested petition(s) flagged reconcile."]
    return "\n".join(lines)
