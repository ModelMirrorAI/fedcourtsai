"""``watchlist-refresh``: keep the AI watchlist's dockets current, facts only.

The dockets ``config/ai-watchlist.yaml`` names are lower-court cases outside
prediction scope, so they are refreshed by this pass rather than by the pull
rotation (which leaves them out by name). Each refresh stores the docket the
way ``pull`` does, a dated full-docket snapshot plus the normalized ``cases``
row stamped ``last_pulled``, and does nothing else: no event extraction, no
outcome detection, no predict or evaluate queue. No moment is registered for a
lower-court docket, so there is nothing to forecast yet.

A docket is read three ways:

- **incremental**, the entries upstream added or changed since the last
  refresh (less an overlap), merged by id into the stored entries. Two requests
  for a quiet docket, so every docket refreshed before is read this way first.
- **onboard**, a whole read of a docket the corpus holds no snapshot of. The
  listed dockets run to over a hundred pages, so onboarding the list spreads
  over several runs: each docket is read whole or not at all, and the run stops
  at its lane's share, leaving the rest first in line for the next.
- **full**, a whole re-read on a day the docket's id picks, once every
  ``full_read_every_days``, so the reads spread across the period. It catches
  what the incremental read cannot see: an entry deleted upstream, or a
  document attached without moving its entry's modification time. A full read
  is taken only when what is left of the run's share covers the docket's stored
  length; a docket longer than that is read incrementally instead, and its
  full read waits for its next day.

A snapshot is stored only when the docket differs from the stored one, since a
daily copy of an unchanged multi-megabyte MDL docket would hold nothing new.
Entries are kept newest id first, upstream's own order, whichever way they
were read.

A degraded upstream degrades the run rather than hanging it: the run stops at
a wall-clock deadline or after consecutive transient failures, as ``pull-all``
does, and defers the dockets it did not reach.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import StrEnum
from math import ceil
from pathlib import Path
from typing import Any

import httpx

from .. import corpus, ids
from ..courtlistener import (
    CourtListenerClient,
    EntryPageCapExceeded,
    RateBudgetExceeded,
    is_transient,
)
from .ingest import from_api_docket, upsert_to_corpus

#: Entries upstream serves on one page of ``docket-entries/``.
ENTRIES_PER_PAGE = 20


class ReadMode(StrEnum):
    """How one refresh reads a docket's entries."""

    incremental = "incremental"
    onboard = "onboard"
    full = "full"


@dataclass(frozen=True)
class PlannedRefresh:
    """One docket's refresh, as the plan orders it."""

    court: str
    docket_id: int
    mode: ReadMode
    # The last refresh's date, or None for a docket never refreshed.
    last_pulled: date | None
    # ``date_modified__gte`` for an incremental read, and the fallback a full
    # read takes when the share cannot cover it; None for a docket never refreshed.
    since: date | None

    @property
    def case_id(self) -> str:
        return ids.case_id(self.court, self.docket_id)


def full_read_due(docket_id: int, today: date, every_days: int) -> bool:
    """Whether ``today`` is the docket's day for a whole re-read.

    The docket id picks the day, so the period's full reads spread across its
    days rather than all falling on one.
    """
    return (docket_id + today.toordinal()) % every_days == 0


def refreshed_on(plan: Iterable[PlannedRefresh], day: date) -> bool:
    """Whether any planned docket was already refreshed on ``day``.

    The once-a-day test: a run stamps every docket it refreshes, so a docket
    stamped ``day`` means a run already took ``day``'s share.
    """
    return any(p.last_pulled == day for p in plan)


_MODE_ORDER = {ReadMode.incremental: 0, ReadMode.onboard: 1, ReadMode.full: 2}


def plan_refresh(
    conn: corpus.ReadConnection,
    dockets: Iterable[tuple[str, int]],
    *,
    today: date,
    overlap_days: int,
    full_read_every_days: int,
) -> list[PlannedRefresh]:
    """Every listed docket's refresh: the cheap incremental reads, then the whole ones.

    Incremental reads come first so a long whole read can never crowd them out
    of the run's share; within each mode the stalest docket leads (never
    refreshed, then oldest ``last_pulled``). Reads only ``cases`` rows, never a
    snapshot, so a plan costs one row lookup a docket; whether a docket
    actually holds a snapshot to merge into is settled when it is read
    (:func:`refresh_docket` reads it whole when it does not).
    """
    planned: list[PlannedRefresh] = []
    for court, docket_id in dict.fromkeys(dockets):
        row = corpus.get_row(conn, ids.case_id(court, docket_id))
        last = row.last_pulled if row is not None else None
        if last is None:
            planned.append(PlannedRefresh(court, docket_id, ReadMode.onboard, None, None))
            continue
        since = last - timedelta(days=overlap_days)
        mode = (
            ReadMode.full
            if full_read_due(docket_id, today, full_read_every_days)
            else ReadMode.incremental
        )
        planned.append(PlannedRefresh(court, docket_id, mode, last, since))
    planned.sort(
        key=lambda p: (
            _MODE_ORDER[p.mode],
            p.last_pulled is not None,
            p.last_pulled or today,
            p.case_id,
        )
    )
    return planned


def merge_entries(
    stored: Iterable[Mapping[str, Any]], changed: Iterable[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    """The stored entries with the changed ones laid over them by id, newest id first."""
    by_id: dict[int, dict[str, Any]] = {int(e["id"]): dict(e) for e in stored}
    by_id.update({int(e["id"]): dict(e) for e in changed})
    return [by_id[key] for key in sorted(by_id, reverse=True)]


@dataclass(frozen=True)
class Refreshed:
    case_id: str
    mode: ReadMode
    changed: bool
    entries: int
    # Requests this refresh sent: the docket and each page of entries.
    requests: int
    # The docket's own fields, without its entries.
    docket: Mapping[str, Any] = field(default_factory=dict, compare=False)
    # Entries the stored docket lacked; empty on an onboard, which has no
    # stored docket to be new against.
    added: tuple[Mapping[str, Any], ...] = field(default=(), compare=False)


def refresh_docket(
    client: CourtListenerClient,
    corpus_db_path: Path,
    planned: PlannedRefresh,
    *,
    max_entry_pages: int,
    today: date,
    share_left: int | None = None,
) -> Refreshed:
    """Read one docket, store its snapshot if it changed, and stamp its row.

    ``share_left`` is what remains of the run's share: a full read the stored
    docket's length says it cannot cover is taken incrementally instead. Raises
    :class:`EntryPageCapExceeded` before writing anything when a read does not
    finish within ``max_entry_pages``, so a truncated docket is never stored as
    if whole.
    """
    case_id = planned.case_id
    sent = 0

    def count() -> None:
        nonlocal sent
        sent += 1

    count()
    docket = client.get_docket(planned.docket_id)
    with corpus.connect(corpus_db_path) as conn:
        prior = corpus.latest_snapshot(conn, case_id)
    stored = prior[1].get("docket_entries") if prior is not None else None
    mode = planned.mode
    if not isinstance(stored, list):
        # Nothing stored to merge into: only a whole read will do.
        mode = ReadMode.onboard
    elif (
        mode is ReadMode.full
        and share_left is not None
        and 1 + max(1, ceil(len(stored) / ENTRIES_PER_PAGE)) > share_left
    ):
        mode = ReadMode.incremental
    since = planned.since if mode is ReadMode.incremental else None
    read = client.docket_entries(
        planned.docket_id,
        max_pages=max_entry_pages,
        date_modified_gte=since,
        on_request=count,
    )
    if not read.complete:
        what = f"changed since {since}" if since else "in all"
        raise EntryPageCapExceeded(
            f"docket {planned.docket_id} has more than {max_entry_pages} pages of entries {what}"
        )
    entries = merge_entries(stored if since and stored else [], read.entries)
    fresh = {**docket, "docket_entries": entries}
    changed = prior is None or prior[1] != fresh
    if changed:
        with corpus.connect(corpus_db_path) as conn:
            corpus.upsert_snapshot(conn, case_id, today, fresh)
    upsert_to_corpus(corpus_db_path, [from_api_docket(fresh)], last_pulled=today)
    known = {e.get("id") for e in stored} if isinstance(stored, list) else None
    added = () if known is None else tuple(e for e in entries if e.get("id") not in known)
    return Refreshed(
        case_id=case_id,
        mode=mode,
        changed=changed,
        entries=len(entries),
        requests=sent,
        docket=docket,
        added=added,
    )


@dataclass
class WatchlistRefreshReport:
    refreshed: list[Refreshed] = field(default_factory=list)
    # case id -> why the read failed; nothing was written for it.
    failed: dict[str, str] = field(default_factory=dict)
    # Planned but not reached: the share, the deadline or the upstream ran out first.
    deferred: list[str] = field(default_factory=list)
    stop_reason: str | None = None

    def as_json(self) -> dict[str, Any]:
        return {
            "refreshed": [
                {
                    "case_id": r.case_id,
                    "mode": r.mode.value,
                    "changed": r.changed,
                    "entries": r.entries,
                    "requests": r.requests,
                }
                for r in self.refreshed
            ],
            "failed": dict(sorted(self.failed.items())),
            "deferred": list(self.deferred),
            "stop_reason": self.stop_reason,
        }


def refresh_watchlist(  # noqa: PLR0913 - each bound is a caller-tuned guard
    client: CourtListenerClient,
    corpus_db_path: Path,
    plan: list[PlannedRefresh],
    *,
    max_entry_pages: int,
    today: date,
    share: int,
    deadline: float | None = None,
    max_consecutive_transient_failures: int = 3,
    clock: Callable[[], float] = time.monotonic,
    on_refreshed: Callable[[Refreshed], None] | None = None,
) -> WatchlistRefreshReport:
    """Refresh the planned dockets in order until the plan, the share or the time runs out.

    ``share`` is the lane's per-run request cap, which the client also enforces;
    it is passed here so a full read the rest of the share cannot cover falls
    back to an incremental one rather than stopping the run. A docket that
    fails (an HTTP error, a malformed entry, or a read past ``max_entry_pages``)
    is recorded and skipped. The share running out, the ``deadline`` (a
    ``clock`` reading) passing, or ``max_consecutive_transient_failures``
    transient errors in a row stop the run, and the dockets not reached are
    deferred. None of these writes anything for the docket, which keeps its
    place in the next run's plan: a never-refreshed docket longer than the page
    cap therefore fails every run, ahead of the onboards behind it, until the
    cap is raised, and the command exits non-zero on any failure so that is seen.

    ``on_refreshed`` is called with each docket as soon as its write lands, so
    a caller recording what a docket added keeps that record even if the run
    is killed before it returns.
    """
    report = WatchlistRefreshReport()
    spent = 0
    transient_run = 0
    for index, planned in enumerate(plan):
        if deadline is not None and clock() >= deadline:
            report.stop_reason = "the run's wall-clock budget is spent"
            report.deferred = [p.case_id for p in plan[index:]]
            break
        try:
            done = refresh_docket(
                client,
                corpus_db_path,
                planned,
                max_entry_pages=max_entry_pages,
                today=today,
                share_left=share - spent,
            )
        except RateBudgetExceeded as exc:
            report.stop_reason = str(exc)
            report.deferred = [p.case_id for p in plan[index:]]
            break
        except (httpx.HTTPError, EntryPageCapExceeded, KeyError, ValueError) as exc:
            report.failed[planned.case_id] = f"{type(exc).__name__}: {exc}"
            transient_run = transient_run + 1 if is_transient(exc) else 0
            if transient_run >= max_consecutive_transient_failures:
                report.stop_reason = (
                    f"{transient_run} transient upstream failures in a row; upstream degraded"
                )
                report.deferred = [p.case_id for p in plan[index + 1 :]]
                break
            continue
        transient_run = 0
        spent += done.requests
        report.refreshed.append(done)
        if on_refreshed is not None:
            on_refreshed(done)
    return report
