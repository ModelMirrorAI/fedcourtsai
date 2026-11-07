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
  for a quiet docket, so every docket refreshed before is read this way, right
  after the run's lead onboard; a long lead onboard may leave some of them to
  the next run, whose window starts from their own last refresh.
- **onboard**, a whole read of a docket the corpus holds no snapshot of. The
  listed dockets run from one page to over a hundred, so an onboard first asks
  upstream how many entries the docket holds (one request) and starts only
  when what is left of the run's share covers that many pages and the docket;
  one that starts short of that could be cut off by the share and leave
  nothing written for what it spent. Without a count it is sized at the page
  cap, and a docket the count puts past the cap fails on the count alone. One
  pending onboard leads each run, ahead of the incremental reads, rotating
  among them by day, so the list onboards a docket each run whose lead read
  succeeds, however long its dockets; the others follow the incremental reads,
  and each one the share left still covers lands the same run.
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
from .entry_reads import ENTRIES_PER_PAGE, full_read_due, merge_entries
from .ingest import from_api_docket, upsert_to_corpus

__all__ = [
    "COUNT_SLACK_PAGES",
    "ENTRIES_PER_PAGE",
    "OnboardDoesNotFit",
    "PlannedRefresh",
    "ReadMode",
    "Refreshed",
    "WatchlistRefreshReport",
    "full_read_due",
    "merge_entries",
    "plan_refresh",
    "refresh_docket",
    "refresh_watchlist",
    "refreshed_on",
]


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
    """Every listed docket's refresh: one onboard, the incremental reads, then the rest.

    One pending onboard leads, so each run onboards a docket while the whole
    share is still there to cover it; the pending onboards are all equally
    stale, so the lead rotates among them by ``today``; the incremental reads follow, then
    the other onboards and the full reads, so no other long whole read can
    crowd the incremental reads out of the run's share. Within each mode the
    stalest docket leads (never refreshed, then oldest ``last_pulled``). Reads
    only ``cases`` rows, never a snapshot, so a plan costs one row lookup a
    docket; whether a docket
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
    pending = [p for p in planned if p.mode is ReadMode.onboard]
    if pending:
        # Every pending onboard is equally stale (never refreshed), so the
        # lead rotates by day: a docket too long for what the incremental
        # reads leave of the share gets the whole share one day in
        # len(pending), and a docket whose lead read fails holds the lead
        # that day only.
        lead = pending[today.toordinal() % len(pending)]
        planned.remove(lead)
        planned.insert(0, lead)
    return planned


class OnboardDoesNotFit(RuntimeError):
    """What is left of the run's share cannot cover an onboard's read.

    Raised before the entries are read, so nothing is written; ``requests`` is
    what the refresh had already sent: the count, and the docket when a planned
    incremental read found no stored snapshot to merge into.
    """

    def __init__(self, message: str, *, requests: int) -> None:
        super().__init__(message)
        self.requests = requests


# Pages added to a counted onboard's size, for entries filed between the count
# and the read.
COUNT_SLACK_PAGES = 1


def _onboard_pages(
    client: CourtListenerClient, docket_id: int, max_entry_pages: int, count: Callable[[], None]
) -> int:
    """The pages an onboard is sized at: upstream's count, else the page cap.

    One request. A docket the count puts past the page cap raises
    :class:`EntryPageCapExceeded` here, before any of its pages are read.
    """
    count()
    found = client.count_docket_entries(docket_id)
    if found is None:
        return max_entry_pages
    pages = max(1, ceil(found / ENTRIES_PER_PAGE))
    if pages > max_entry_pages:
        raise EntryPageCapExceeded(
            f"docket {docket_id} counts {found} entries, over {max_entry_pages} pages"
        )
    return min(max_entry_pages, pages + COUNT_SLACK_PAGES)


def _fits(share_left: int | None, need: int) -> bool:
    return share_left is None or share_left >= need


@dataclass(frozen=True)
class Refreshed:
    case_id: str
    mode: ReadMode
    changed: bool
    entries: int
    # Requests this refresh sent: the entry count on an onboard, the docket
    # and each page of entries.
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
    on_request: Callable[[], None] | None = None,
) -> Refreshed:
    """Read one docket, store its snapshot if it changed, and stamp its row.

    ``share_left`` is what remains of the run's share: a full read the stored
    docket's length says it cannot cover is taken incrementally instead, and an
    onboard it cannot cover at upstream's count of its entries (at the page cap
    without a count) raises :class:`OnboardDoesNotFit` before its entries are
    read. Raises :class:`EntryPageCapExceeded` before writing anything when the
    count puts a docket past ``max_entry_pages`` or a read does not finish
    within it, so a truncated docket is never stored as if whole.
    """
    case_id = planned.case_id
    sent = 0

    def count() -> None:
        nonlocal sent
        sent += 1
        if on_request is not None:
            on_request()

    def left() -> int | None:
        return None if share_left is None else share_left - sent

    # The fewest pages a counted onboard is sized at.
    least = min(max_entry_pages, 1 + COUNT_SLACK_PAGES)
    if planned.mode is ReadMode.onboard:
        # The count, the docket and the fewest pages: nothing smaller is an
        # onboard, so a share under that is not spent on a count.
        if not _fits(left(), 2 + least):
            raise OnboardDoesNotFit(
                f"{case_id}: {share_left} of the share left, under the smallest onboard's "
                f"{2 + least}",
                requests=0,
            )
        pages = _onboard_pages(client, planned.docket_id, max_entry_pages, count)
        if not _fits(left(), 1 + pages):
            raise OnboardDoesNotFit(
                f"{case_id}: {left()} of the share left, under this onboard's {1 + pages}",
                requests=sent,
            )
    count()
    docket = client.get_docket(planned.docket_id)
    with corpus.connect(corpus_db_path) as conn:
        prior = corpus.latest_snapshot(conn, case_id)
    stored = prior[1].get("docket_entries") if prior is not None else None
    mode = planned.mode
    if not isinstance(stored, list) and planned.mode is not ReadMode.onboard:
        # Nothing stored to merge into: only a whole read will do.
        mode = ReadMode.onboard
        if not _fits(left(), 1 + least):
            raise OnboardDoesNotFit(
                f"{case_id}: no stored snapshot, and the share left cannot cover an onboard",
                requests=sent,
            )
        pages = _onboard_pages(client, planned.docket_id, max_entry_pages, count)
        if not _fits(left(), pages):
            raise OnboardDoesNotFit(
                f"{case_id}: no stored snapshot, and the share left cannot cover an onboard",
                requests=sent,
            )
    elif (
        mode is ReadMode.full
        and isinstance(stored, list)
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
    back to an incremental one rather than stopping the run, and an onboard it
    cannot cover is deferred while the run goes on. A docket that
    fails (an HTTP error, a malformed entry, or a read past ``max_entry_pages``)
    is recorded and skipped. The share running out, the ``deadline`` (a
    ``clock`` reading) passing, or ``max_consecutive_transient_failures``
    transient errors in a row stop the run, and the dockets not reached are
    deferred. None of these writes anything for the docket, which keeps its
    place in the next run's plan: a never-refreshed docket longer than the page
    cap therefore fails each run that reaches it, on its count alone, until the
    cap is raised, and the command exits non-zero on any failure so that is seen.

    ``on_refreshed`` is called with each docket as soon as its write lands, so
    a caller recording what a docket added keeps that record even if the run
    is killed before it returns.
    """
    report = WatchlistRefreshReport()
    # Every request a refresh sends, failed reads included, so the share left
    # stays exact after a read that fails part-way.
    spent = 0

    def count() -> None:
        nonlocal spent
        spent += 1

    transient_run = 0
    for index, planned in enumerate(plan):
        if deadline is not None and clock() >= deadline:
            report.stop_reason = "the run's wall-clock budget is spent"
            report.deferred.extend(p.case_id for p in plan[index:])
            break
        try:
            done = refresh_docket(
                client,
                corpus_db_path,
                planned,
                max_entry_pages=max_entry_pages,
                today=today,
                share_left=share - spent,
                on_request=count,
            )
        except RateBudgetExceeded as exc:
            report.stop_reason = str(exc)
            report.deferred.extend(p.case_id for p in plan[index:])
            break
        except OnboardDoesNotFit:
            # A shorter read further on may still fit, so the run goes on.
            report.deferred.append(planned.case_id)
            continue
        except (httpx.HTTPError, EntryPageCapExceeded, KeyError, ValueError) as exc:
            report.failed[planned.case_id] = f"{type(exc).__name__}: {exc}"
            transient_run = transient_run + 1 if is_transient(exc) else 0
            if transient_run >= max_consecutive_transient_failures:
                report.stop_reason = (
                    f"{transient_run} transient upstream failures in a row; upstream degraded"
                )
                report.deferred.extend(p.case_id for p in plan[index + 1 :])
                break
            continue
        transient_run = 0
        report.refreshed.append(done)
        if on_refreshed is not None:
            on_refreshed(done)
    return report
