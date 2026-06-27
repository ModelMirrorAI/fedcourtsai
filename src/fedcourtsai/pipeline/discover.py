"""``run-pull`` forward discovery: pick up cases filed after the seed backfill.

The forward-frontier counterpart to ``pull_case`` (which *refreshes* known
dockets). For each tracked court it asks the CourtListener REST API for dockets
filed since that court's discovery watermark, routes each new docket through the
shared ingestion core (:mod:`fedcourtsai.pipeline.ingest`) into the unified
corpus, runs the deterministic event-definition stage
(:mod:`fedcourtsai.pipeline.events`) to record its predictable event
definition(s) as corpus rows, and advances the watermark — all *raw facts*, none
of it per-case git files. Entries the extractor cannot confidently classify are
collected on the result so the caller can open an agent reconcile issue.

Two budget guards keep a run inside the CourtListener API ceiling: a hard cap on
new dockets per run (``max_new``), and ascending ``date_filed`` ordering so a run
that hits the cap still advances the watermark monotonically and the next run
resumes from where it stopped, gap-free. Derived judgments (outcomes,
predictions, evaluations) are never written here — they belong to the git ledger.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Protocol

import httpx

from .. import corpus
from ..courtlistener import CourtListenerClient
from .events import AmbiguousEntry, extract_events
from .ingest import from_api_docket, to_corpus_row


class _DocketSearch(Protocol):
    """The slice of :class:`CourtListenerClient` discovery needs (eases testing)."""

    def iter_dockets(
        self, court: str, date_filed_gte: date, *, max_results: int
    ) -> list[dict[str, object]]: ...


@dataclass
class CourtDiscovery:
    """What discovery found for one court this run."""

    court: str
    onboarded: int
    watermark: date


@dataclass
class DiscoverResult:
    """Aggregate outcome of a discovery pass across the tracked courts."""

    courts: list[CourtDiscovery] = field(default_factory=list)
    case_ids: list[str] = field(default_factory=list)
    ambiguous: list[AmbiguousEntry] = field(default_factory=list)
    # Courts whose discovery hit an unrecoverable REST error this run (e.g. a
    # timeout, or retries exhausted). Recorded so one slow court degrades the run
    # gracefully instead of aborting the whole refresh; carries ``court`` /
    # ``reason`` for a maintainer to triage. The failed court's watermark is left
    # untouched, so the next run retries its range gap-free.
    failed: list[dict[str, object]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.case_ids)


def discover_cases(
    client: CourtListenerClient | _DocketSearch,
    corpus_db_path: Path,
    courts: list[str],
    *,
    max_new: int,
    default_since: date,
) -> DiscoverResult:
    """Discover and onboard newly-filed dockets across ``courts``, within budget.

    Walks the courts in order, onboarding at most ``max_new`` dockets in total
    (the budget governor's discovery cap). For each new docket it upserts the
    normalized corpus row, records its default predictable event, and advances
    the court's watermark to the newest ``date_filed`` it onboarded. A court with
    no watermark yet starts from ``default_since`` — normally the snapshot date
    seed handed off, or ``--since`` for a never-seeded court (``today`` is only the
    last resort). A court that finds nothing still records the date it searched
    from, so it resumes there rather than resetting to ``default_since`` next run.
    """
    result = DiscoverResult()
    if max_new <= 0:
        return result

    with corpus.connect(corpus_db_path) as conn:
        for court in courts:
            remaining = max_new - result.total
            if remaining <= 0:
                break

            since = corpus.get_discovery_watermark(conn, court) or default_since
            try:
                dockets = client.iter_dockets(court, since, max_results=remaining)
            except httpx.HTTPError as exc:
                # One court's REST failure must not abort discovery (which itself
                # runs before the per-case refresh): the courts already onboarded
                # this run keep their corpus writes, and refresh still proceeds.
                # ``iter_dockets`` is the first touch for this court and raises
                # before any write, so no partial corpus state is left behind.
                # Leave the watermark untouched so the next run retries this exact
                # range gap-free, rather than skipping forward past unseen filings.
                result.failed.append({"court": court, "reason": f"{type(exc).__name__}: {exc}"})
                continue
            if not dockets:
                # No new filings — but still record the frontier we searched from,
                # so the next run resumes from ``since`` instead of resetting to
                # ``default_since`` (a court that keeps finding nothing would
                # otherwise restart from "today" every run — a steady-state hole,
                # not a one-time miss). ``since`` is a date already searched
                # (``date_filed >= since``), so re-searching from it next run
                # cannot skip a real filing; the watermark only ever moves forward.
                corpus.set_discovery_watermark(conn, court, since)
                continue
            rows = [from_api_docket(d) for d in dockets]

            store_rows = [to_corpus_row(r) for r in rows]
            corpus.upsert_rows(conn, store_rows)
            # A discovered SCOTUS docket latches its originating tracked CoA docket
            # eligible (the second half of the prediction-scope rule).
            corpus.latch_originating_eligible(conn, store_rows)
            for docket in dockets:
                extraction = extract_events(docket)
                corpus.upsert_events(conn, extraction.events)
                result.ambiguous.extend(extraction.ambiguous)

            watermark = max((r.date_filed for r in rows if r.date_filed is not None), default=since)
            corpus.set_discovery_watermark(conn, court, watermark)

            result.courts.append(CourtDiscovery(court, len(rows), watermark))
            result.case_ids.extend(r.case_id for r in rows)

    return result
