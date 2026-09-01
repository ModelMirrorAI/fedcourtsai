"""The historical Term walker: build per-Term history through the live channel.

The historical half of the live-sources design (docs/live-sources.md): the
supremecourt.gov docket JSON serves every decided petition of the e-filing era
(OT2017+, per docs/live-sources.md), through the identical client,
mapping, identity, and ingest seams the forward poller uses — so the historical
set is built with the actual instrument, not a proxy. It accumulates resolved
outcomes reverse-chronologically by Term, primarily to give the statpack's
per-Term base rates real coverage, and secondarily to supply the cert back-test
set. Run by the ``run-seed`` workflow via ``fedcourts historical-terms``.

How it differs from :func:`~fedcourtsai.pipeline.live.discover_live`, the
forward frontier prober:

- **It walks whole Terms, not a frontier.** Each configured Term's two
  numbering streams (paid petitions from 1, IFP from 5001) are walked
  sequentially to their end — ``frontier_misses`` consecutive 404s — under
  per-invocation probe and wall-clock caps, resuming from a persisted cursor.
  The cursors live in the same ``live_discovery_cursors`` table as the forward
  poller's, under the distinct stream names ``historical-paid`` /
  ``historical-ifp``, so the two walkers can never collide on a (term, stream)
  key. The cursor advances over every *served* serial, so a resumed walk never
  re-reads one; a 404 never advances it, so a resumed run re-confirms the
  frontier cheaply. :func:`~fedcourtsai.corpus.clear_live_cursor` is the way back
  for a whole Term, when the pipeline has since learned to read more from it;
  :func:`refresh_dockets` is the targeted counterpart, re-serving an enumerated
  list of docket numbers through the same ingest seam and moving no cursor.
- **It ingests every decided petition.** Each served record's disposition is
  read from its proceedings text
  (:func:`~fedcourtsai.pipeline.cert_signals.match_disposition_signal`, the same
  patterns ingest-time resolution runs) and every decided one is kept. The walk
  probes each serial regardless, so declining to store a denial never saved a
  fetch — it only discarded a row already in hand, and cost every rate computed
  over the result a denominator it had to reconstruct from weights. Corpus
  breadth is cheap; the expensive stages are predict and evaluate, which select
  from the corpus rather than being bounded by it. Sampling belongs at that
  selection, where it is reversible. A record with no machine-readable
  disposition (a still-pending or held petition) is skipped entirely — pending
  matters are the forward poller's charter, and skipping them here keeps this
  walker's guarantee absolute: **it writes no predict/evaluate queues, and
  every row it ingests lands already RESOLVED**, so the pending rotation
  (``corpus.live_rotation``) never picks it up either — except the row whose
  ingest itself resolves a tracked open petition as *granted*: the shared
  resolution seam then mints the open merits event, exactly as the watchlist
  path would, and the rotation keeps that genuinely-live merits proceeding.
  The complement of that
  guarantee: a decided petition whose existing case carries an open,
  **predicted** event is left to the watchlist rather than ingested (see
  :meth:`_Walk.ingest`), so the resolution reaches the evaluate handoff this
  walker never files.
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
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from dataclasses import field as dataclasses_field
from datetime import date
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

from .. import corpus, ids
from ..config import HistoricalConfig
from ..matrix import event_has_predictions
from ..schemas import Disposition
from ..supremecourt import IFP_SERIAL_BASE, SupremeCourtClient, parse_scotus_docket_number
from .cert_signals import match_disposition_signal
from .ingest import UNSAMPLED_WEIGHT, backfill_live_signals
from .live import _resolve_identity, ingest_live_payload, provision_documents

# The walker's per-Term numbering streams. Same bases as the forward poller's,
# distinct cursor names so the two walkers never share a (term, stream) key in
# `live_discovery_cursors` (the forward frontier uses "paid" / "ifp").
HISTORICAL_STREAMS: tuple[tuple[str, int], ...] = (
    ("historical-paid", 1),
    ("historical-ifp", IFP_SERIAL_BASE),
)

# The walker previously persisted its cursors under these stream names; a
# corpus that still holds them is migrated in place at walk start (see
# `_migrate_legacy_cursors`). Droppable once no production corpus carries them.
_LEGACY_STREAM_RENAMES: Mapping[str, str] = {
    "seed-paid": "historical-paid",
    "seed-ifp": "historical-ifp",
}

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


class HistoricalReport(BaseModel):
    """The ``--report`` payload: this invocation's counts + overall walk state."""

    probed: int = 0
    """Docket-JSON fetches this invocation (the capped unit)."""
    served: int = 0
    ingested_granted: int = 0
    """Grants and GVRs — everything on the granted side is kept."""
    ingested_denied: int = 0
    """Denials — kept in full; a Term is overwhelmingly these."""
    ingested_other: int = 0
    """Other decided dispositions (dismissed etc.) — rare, all kept."""
    skipped_undecided: int = 0
    """Served records with no machine-readable disposition (left to the
    forward poller; never ingested here)."""
    left_to_watchlist: int = 0
    """Decided records whose existing case carries an open, predicted event —
    left to the watchlist so its resolution queues the evaluate handoff the
    walker never files."""
    documents: int = 0
    """Filed documents provisioned for OT``document_floor_term``+ ingests."""
    unrecorded_flagged: int = 0
    """Ingested petitions whose resolution left an unrecorded outcome — should
    be zero (the disposition matched before ingest); surfaced for triage."""
    failed: list[dict[str, object]] = Field(default_factory=list)
    """(term, stream, serial, reason) for streams stopped by upstream errors;
    their cursors are untouched, so the next invocation retries gap-free."""
    complete: bool = False
    """Every configured (term, stream) frontier was observed this invocation."""
    stopped: str = "complete"
    """Why the walk ended: complete | probe-cap | time-cap | stream-errors."""
    streams: list[StreamProgress] = Field(default_factory=list)


class ResetReport(BaseModel):
    """Which (Term, stream) cursors a refresh reset, and which had none."""

    reset: list[str] = Field(default_factory=list)
    """``OT<term>/<stream>`` for each cursor actually removed."""
    absent: list[str] = Field(default_factory=list)
    """Configured pairs that carried no cursor — never walked, nothing to reset."""


class DocketRefreshReport(BaseModel):
    """One targeted re-snapshot pass over an enumerated list of docket numbers."""

    served: list[str] = Field(default_factory=list)
    """Numbers upstream served a record for, in the order given."""
    unserved: list[str] = Field(default_factory=list)
    """Numbers upstream has no record at; nothing was written for them."""
    undecided: list[str] = Field(default_factory=list)
    """The members of ``served`` carrying no machine-readable disposition, which
    the walk's own rule declines to ingest — pending matters are the forward
    poller's charter, and a named list may not write what a walk would not."""
    left_to_watchlist: list[str] = Field(default_factory=list)
    """The members of ``served`` whose case carries an open, predicted event, so
    the ingest seam left them for the watchlist. Named rather than counted: on a
    command whose whole premise is *these* dockets, the one a maintainer asked
    for and did not get is the one that must be nameable."""
    walk: HistoricalReport = Field(default_factory=HistoricalReport)
    """The ingest counters and per-number upstream failures, in the walker's own
    vocabulary: the same seam ran, so the same report describes what it did. Its
    walk-shaped fields do not apply — no stream was walked, and ``stopped`` reads
    ``targeted`` so the object cannot be mistaken for a walk's own report."""


def reset_walk(
    corpus_db_path: Path, terms: Sequence[int], streams: Sequence[str] | None = None
) -> ResetReport:
    """Clear the historical cursors for ``terms`` so the next walk re-covers them.

    The re-walk half of a full refresh: this moves no data and fetches nothing. It
    drops the resume points, and the next ``historical-terms`` invocations do the
    work — which is what makes it safe to run and cheap to undo by simply not
    walking.

    Re-walking **adds**. Every re-served docket upserts onto its existing row
    through the corpus latches, so a refreshed row keeps what the first pass
    captured and gains what the pipeline has since learned to read — a new column,
    a corrected parser, a disposition the old patterns missed. Nothing is deleted
    and ``case_id`` never moves, so re-running is idempotent rather than
    destructive.

    ``streams`` narrows which numbering sequences re-open; ``None`` means both.
    The two cost very differently — a Term's IFP sequence is roughly three times
    its paid one — and only the paid stream feeds the scored segment, so a refresh
    aimed at the predicted population should not have to pay for the rest of the
    docket first.
    """
    wanted = tuple(
        HISTORICAL_STREAMS
        if streams is None
        else [(name, base) for name, base in HISTORICAL_STREAMS if name in set(streams)]
    )
    report = ResetReport()
    _migrate_legacy_cursors(corpus_db_path)
    with corpus.connect(corpus_db_path) as conn:
        for term in sorted(set(terms)):
            for stream, _base in wanted:
                label = f"OT{2000 + term}/{stream}"
                if corpus.clear_live_cursor(conn, term, stream):
                    report.reset.append(label)
                else:
                    report.absent.append(label)
    return report


def _payload_disposition(payload: Mapping[str, Any]) -> Disposition | None:
    """The cert disposition the record's proceedings text carries, or ``None``.

    First match in docket order over the same entry text ingest-time resolution
    reads, so the keep/skip decision always agrees with the label the ingested
    row will land with.
    """
    for entry in payload.get("ProceedingsandOrder") or []:
        if not isinstance(entry, Mapping):
            continue
        matched = match_disposition_signal(str(entry.get("Text") or ""))
        if matched is not None:
            return matched[0]
    return None


def _migrate_legacy_cursors(corpus_db_path: Path) -> None:
    """Rename any legacy-named walk cursors in place; idempotent, no-op when clean.

    Runs at walk start (not as a one-shot script) so the rename stays correct
    even if the corpus blob is ever rolled back to a pointer that still carries
    the legacy names.
    """
    with corpus.connect(corpus_db_path) as conn:
        corpus.rename_live_streams(conn, _LEGACY_STREAM_RENAMES)


@dataclass
class _Walk:
    """One invocation's walk state: the shared handles and its running report."""

    client: SupremeCourtClient
    corpus_db_path: Path
    data_root: Path
    config: HistoricalConfig
    today: date
    report: HistoricalReport = dataclasses_field(default_factory=HistoricalReport)

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
            # Every decided petition is kept. The payload is already paid for by
            # the time its disposition can be read, so declining one saves nothing
            # and costs a row the corpus can only recover by re-walking the Term.
            if disposition is None:
                report.skipped_undecided += 1
            else:
                self.ingest(payload, term, serial, disposition)
            # The cursor covers every served serial, so a resumed walk never
            # re-reads one. (404s do not advance it: the frontier is re-confirmed,
            # cheaply.)
            with corpus.connect(self.corpus_db_path) as conn:
                corpus.set_live_cursor(conn, term, stream, serial)
            serial += 1
        frontier_reached = misses >= self.config.frontier_misses
        with corpus.connect(self.corpus_db_path) as conn:
            stored = corpus.get_live_cursor(conn, term, stream)
            if frontier_reached and stored is not None:
                # Persist where the end was observed (previously only this
                # invocation's report knew): `frontier_serial = last_serial`
                # is the statpack's per-Term "walk complete" signal.
                corpus.set_live_frontier(conn, term, stream, stored)
        report.streams.append(
            StreamProgress(
                term=term,
                stream=stream,
                cursor=stored,
                frontier_reached=frontier_reached,
            )
        )

    def ingest(self, payload: dict[str, Any], term: int, serial: int, label: Disposition) -> None:
        """Land one decided petition through the shared live-ingest path.

        One guard first: a serial that resolves to an existing case with an
        **open, predicted** event is left to the watchlist instead of ingested.
        The walker files no evaluate handoffs by charter, so ingesting such a
        case here would land its outcome without ever queuing the committed
        prediction for scoring — and the resolved row would leave the live
        rotation, so the forward poller would never see the transition either.
        The watchlist re-poll detects the resolution and queues evaluate; the
        cursor still advances (the serial is served), so the walker never
        re-probes it.
        """
        report = self.report
        with corpus.connect(self.corpus_db_path) as conn:
            docket_id = _resolve_identity(conn, payload, term, serial)
            open_event_ids = [
                event.event_id
                for event in corpus.events_for_case(conn, ids.case_id("scotus", docket_id))
                if not event.resolved
            ]
        if any(
            event_has_predictions(self.data_root, "scotus", docket_id, event_id)
            for event_id in open_event_ids
        ):
            report.left_to_watchlist += 1
            return
        result = ingest_live_payload(
            self.corpus_db_path,
            self.data_root,
            payload,
            docket_id,
            today=self.today,
            # The walk keeps every decided petition, so it includes every row it
            # writes with certainty. What lands is `ingest_live_payload`'s reading
            # rather than this assertion — but on *this* path the two always
            # agree, and for a reason worth stating: the stream sets its cursor
            # after each serial is served, so at ingest the stored cursor is
            # `serial - 1` and the weight rule's cursor conjunct short-circuits
            # before the density guard is consulted. A forward walk therefore
            # writes 1 unconditionally, which is what lets a re-walk regress the
            # legacy frame at all. The guard bites on the below-cursor re-serves
            # instead — `refresh_dockets`, which touches no cursor, and the
            # poller's rotations and sweep — where re-serving one kept serial
            # observes nothing about the nine petitions behind it. The column
            # stays because the corpus holds denials the earlier sampled walk kept
            # at a higher weight, which a weighted estimate must keep honouring.
            sample_weight=UNSAMPLED_WEIGHT,
        )
        if label in (Disposition.granted, Disposition.gvr):
            report.ingested_granted += 1
        elif label == Disposition.denied:
            report.ingested_denied += 1
        else:
            report.ingested_other += 1
        report.unrecorded_flagged += len(result.unrecorded_events)
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
    config: HistoricalConfig,
    *,
    today: date,
    clock: Callable[[], float] = time.monotonic,
) -> HistoricalReport:
    """One capped invocation of the Term walk; resumes from the cursors.

    Walks ``config.terms`` in order, each Term's ``historical-paid`` then
    ``historical-ifp`` stream, until every stream's frontier is observed or a
    per-invocation cap (``max_probes_per_run`` docket fetches;
    ``max_run_minutes`` wall clock, checked between serials) stops the walk. An
    upstream error stops only its stream — cursor untouched, next invocation
    retries the same serial — and never aborts the invocation. Returns the
    report the run-seed walk loop reads for its stop conditions and
    step summary.
    """
    _migrate_legacy_cursors(corpus_db_path)
    # Pre-capture live rows get their parsed signals and sample weights filled
    # here — the daily corpus-writer entrypoint — so the statpack's live-slice
    # aggregates never see a NULL a rule could have resolved. (The forward
    # poller needs no such hook: its active rows self-heal on the next re-poll
    # through the ordinary ingest path.)
    backfill_live_signals(corpus_db_path)
    walk = _Walk(client, corpus_db_path, data_root, config, today)
    deadline = clock() + config.max_run_minutes * 60

    def out_of() -> str | None:
        if walk.report.probed >= config.max_probes_per_run:
            return "probe-cap"
        if clock() >= deadline:
            return "time-cap"
        return None

    for term in config.terms:
        for stream, base in HISTORICAL_STREAMS:
            walk.walk_stream(term, stream, base, out_of)
            capped = out_of()
            if capped is not None:
                walk.report.stopped = capped
                return walk.report
    walk.report.complete = all(s.frontier_reached for s in walk.report.streams)
    walk.report.stopped = "complete" if walk.report.complete else "stream-errors"
    return walk.report


def refresh_dockets(
    client: SupremeCourtClient,
    corpus_db_path: Path,
    data_root: Path,
    config: HistoricalConfig,
    numbers: Sequence[str],
    *,
    today: date,
) -> DocketRefreshReport:
    """Re-serve an enumerated list of docket numbers through the walk's ingest seam.

    The targeted half of a refresh. :func:`reset_walk` re-opens whole Terms,
    which is the right instrument when the pipeline learns to read something new
    across a population; it is the wrong one when a known, enumerated set of
    dockets needs its stored row rebuilt, because re-covering a Term pays for its
    entire serial range at ~1 req/s to reach a handful of rows.

    **No cursor is touched.** A targeted re-snapshot is not a rewind: the walk
    resumes exactly where it left off, and re-reading a serial the cursor has
    already passed is the point here rather than state to record. That is also
    what makes this safe beside a walk of the same Term — both write the same
    rows through the same latches, and neither can move the other's resume point.

    Additive on exactly the terms a re-walk is: each re-served docket upserts
    onto its existing row through the corpus latches, so no row is deleted and
    ``case_id`` never moves, while an *unlatched* column takes the fresh parse —
    which is what lets a tightened pattern retract a stale reading as well as
    supply a missed one. A number upstream no longer serves, or now serves with
    no machine-readable disposition, is reported and never ingested: the walk's
    rule unchanged, because a named list must not be able to write what a walk
    would not.

    **Corpus-side, on the case this exists for.** The write is the shared ingest
    seam's, so ``outcome.json`` is recorded only where the event is still open —
    :func:`~fedcourtsai.pipeline.outcome.record_outcomes` reads open events alone
    and never overwrites a committed outcome. A docket a walk already landed has
    its cert event latched resolved, so a re-serve converges the corpus row and
    leaves the ledger label where it is; moving *that* is
    ``converge-disposition-labels``' remit, not this path's. A number the corpus
    has never held is onboarded outright, ledger included, exactly as the walk
    would have onboarded it.

    ``numbers`` are Term-form docket numbers (``"22-451"``); repeats collapse,
    order preserved, since probing the same serial twice buys nothing and would
    double-count the report. The whole list is parsed before the first fetch and
    a malformed member raises :class:`ValueError`, so a typo costs no upstream
    traffic and no half-applied list. The count is bounded by
    ``config.max_probes_per_run`` — the same per-invocation probe bound the walk
    runs under, and it lives here rather than in the caller so a code caller is
    bounded on the same terms as the command.
    """
    parsed: list[tuple[str, int, int]] = []
    malformed: list[str] = []
    for number in dict.fromkeys(numbers):
        pair = parse_scotus_docket_number(number)
        if pair is None:
            malformed.append(number)
        else:
            parsed.append((number, pair[0], pair[1]))
    if malformed:
        raise ValueError(
            "not Term-form SCOTUS docket number(s) (want e.g. 22-451): " + ", ".join(malformed)
        )
    if len(parsed) > config.max_probes_per_run:
        raise ValueError(
            f"{len(parsed)} docket(s) named, past the {config.max_probes_per_run}-probe "
            "bound one invocation runs under; split the list across dispatches."
        )
    walk = _Walk(client, corpus_db_path, data_root, config, today)
    # `stopped` names the shape of the pass, so the report can never read as a
    # walk that ended incomplete: no stream was walked, and none was left short.
    walk.report.stopped = "targeted"
    report = DocketRefreshReport(walk=walk.report)
    for number, term, serial in parsed:
        try:
            payload = client.get_docket(term, serial)
        except httpx.HTTPError as exc:
            # One number's upstream failure costs that number, never the list:
            # unlike a stream, the members are independent, so there is no
            # gap-free-resume property to protect by stopping early.
            walk.report.failed.append(
                {
                    "term": term,
                    "stream": "targeted",
                    "serial": serial,
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        walk.report.probed += 1
        if payload is None:
            report.unserved.append(number)
            continue
        walk.report.served += 1
        report.served.append(number)
        disposition = _payload_disposition(payload)
        if disposition is None:
            walk.report.skipped_undecided += 1
            report.undecided.append(number)
            continue
        deferred = walk.report.left_to_watchlist
        walk.ingest(payload, term, serial, disposition)
        if walk.report.left_to_watchlist > deferred:
            report.left_to_watchlist.append(number)
    return report


def fold_totals(totals: HistoricalReport | None, latest: HistoricalReport) -> HistoricalReport:
    """Fold one invocation's report into a run's cumulative totals.

    The run-seed walk loop invokes ``historical-terms`` many times per job
    (each invocation is one checkpoint chunk); the totals file is what the run's
    single step summary renders. Counters and failures accumulate; the walk
    state — per-(Term, stream) progress, ``complete``, ``stopped`` — is the
    latest invocation's view (its cursors already encode all prior progress).
    """
    if totals is None:
        return latest.model_copy(deep=True)
    merged = {(s.term, s.stream): s for s in totals.streams}
    merged.update({(s.term, s.stream): s for s in latest.streams})
    return HistoricalReport(
        probed=totals.probed + latest.probed,
        served=totals.served + latest.served,
        ingested_granted=totals.ingested_granted + latest.ingested_granted,
        ingested_denied=totals.ingested_denied + latest.ingested_denied,
        ingested_other=totals.ingested_other + latest.ingested_other,
        skipped_undecided=totals.skipped_undecided + latest.skipped_undecided,
        left_to_watchlist=totals.left_to_watchlist + latest.left_to_watchlist,
        documents=totals.documents + latest.documents,
        unrecorded_flagged=totals.unrecorded_flagged + latest.unrecorded_flagged,
        failed=[*totals.failed, *latest.failed],
        complete=latest.complete,
        stopped=latest.stopped,
        streams=[merged[key] for key in sorted(merged, reverse=True)],
    )


def render_markdown(report: HistoricalReport) -> str:
    """The report as the run-seed walk's step-summary body."""
    ingested = report.ingested_granted + report.ingested_denied + report.ingested_other
    lines = [
        "### Historical Term walker progress" + (" — walk complete ✅" if report.complete else ""),
        "",
        f"Probed **{report.probed}** serial(s) ({report.served} served); ingested "
        f"**{ingested}** decided petition(s) — {report.ingested_granted} granted/GVR, "
        f"{report.ingested_denied} denial(s), {report.ingested_other} other — "
        f"skipped {report.skipped_undecided} undecided; provisioned "
        f"{report.documents} document(s).",
        "",
        "| OT | Stream | Serial reached | Frontier |",
        "|----|--------|---------------:|:--------:|",
    ]
    for s in report.streams:
        lines.append(
            f"| {s.term} | {s.stream} | {s.cursor if s.cursor is not None else '—'} "
            f"| {'✅' if s.frontier_reached else ''} |"
        )
    if report.left_to_watchlist:
        lines += [
            "",
            f"{report.left_to_watchlist} decided petition(s) with an open predicted "
            "event left to the watchlist (its re-poll queues the evaluate handoff).",
        ]
    if report.failed:
        lines += ["", f"⚠️ {len(report.failed)} stream error(s); those cursors will retry."]
    if report.unrecorded_flagged:
        lines += [
            "",
            f"⚠️ {report.unrecorded_flagged} ingested petition(s) landed with an "
            "unrecorded outcome.",
        ]
    return "\n".join(lines)
