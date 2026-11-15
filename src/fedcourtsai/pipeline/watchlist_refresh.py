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
  one that starts short of that would be cut off by the share. Without a
  count it is sized at the page cap, and a docket the count puts past the cap
  fails on the count alone. One pending onboard leads each run, ahead of the
  incremental reads, rotating
  among them by day, so the list onboards a docket each run whose lead read
  succeeds, however long its dockets; the others follow the incremental reads,
  and each one the share left still covers lands the same run. An onboard
  that stops part-way (a page that times out, a refusal, the share) keeps the
  pages it read in the content store, as the docket's ``onboard/partial.json``,
  and the docket's next onboard goes on from the page it stopped at: it is
  sized at the pages still owed, and closes with a read of the entries changed
  since the day the first attempt began, laid over the kept pages by id. Kept
  pages older than ``onboard_resume_max_age_days`` are ignored, and they are
  emptied when the docket's first snapshot is stored. They are never a
  snapshot: nothing reads them but the onboard that goes on from them. A run
  that may not write the content store keeps nothing and reads whole. Kept
  pages only help past a page that answers on a later day: a page that never
  answers stops every attempt at the same place until the kept pages age out.
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

The account's rate windows are shared with every other lane, and this
process's limiter counts only its own requests, so a read can be refused (429)
while its own count is in bounds. The command's client waits out a refusal
whose stated ``Retry-After`` is short (the per-minute window) and sends the
request again, since the read's later pages wait behind it; a longer
stated wait fails the docket at once. A failed docket's reason quotes what
upstream said, which names the limit that refused.

A failed docket's reason also says where its read stopped: the last request it
asked for (the entry count, the docket, or a numbered page of the entries,
with that page's cursor where the failure came from it), how long ago that
request was asked for, and how long the docket's read had run. The first time
covers this process's own rate-limit waits and the client's resends as well as
upstream's answer. Two failures of one long docket are compared by those: the
same page each time is one slow page upstream, a different one each time is
the read's length. Where the read kept its pages for the next run, or dropped
kept pages whose cursor upstream refused, the reason says that too.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import StrEnum
from math import ceil
from pathlib import Path
from typing import Any

import httpx

from .. import casestore, corpus, ids
from ..ai_activity import became_available
from ..courtlistener import (
    CourtListenerClient,
    EntryPageCapExceeded,
    RateBudgetExceeded,
    failed_cursor,
    is_transient,
    refusal_detail,
)
from .entry_reads import ENTRIES_PER_PAGE, full_read_due, merge_entries
from .ingest import from_api_docket, upsert_to_corpus

logger = logging.getLogger(__name__)

__all__ = [
    "COUNT_SLACK_PAGES",
    "ENTRIES_PER_PAGE",
    "OnboardDoesNotFit",
    "OnboardResume",
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
class OnboardResume:
    """How an onboard that stops part-way is kept and taken up again.

    ``overlap_days`` is how far before the day the read began its closing read
    reaches back, as an incremental read's does before the last refresh;
    ``max_age_days`` is how long after that day kept pages are still used.
    """

    overlap_days: int
    max_age_days: int


_PARTIAL_KIND = "onboard-partial"
_PARTIAL_VERSION = 1


@dataclass(frozen=True)
class _KeptPages:
    """What an earlier run's onboard of a docket fetched before it stopped."""

    # The day the read began: the closing read asks for what changed since.
    started: date
    pages: int
    # The page the read goes on from; None once every page is held and only
    # the closing read is owed.
    cursor: str | None
    entries: list[dict[str, Any]]


class _OnboardKeeper:
    """One docket's onboard, kept across runs in the content store.

    A whole read that stops part-way leaves the pages it fetched, and the
    cursor of the page it stopped on, in the docket's ``onboard/partial.json``;
    the next run's onboard goes on from that cursor. This rests on upstream's
    own ordering, which the client does not choose: it serves a docket's
    entries newest id first and its cursor names a position in that order (an
    entry id), so the pages after it are the same entries whenever they are
    read; what a later
    day cannot see from there is an entry added or changed since the read
    began, so a read taken up again closes with an incremental read back to
    that day, laid over the kept pages by id. An entry deleted upstream in
    between is left to the docket's next whole re-read, as it is for every
    incremental read.

    The object is never a snapshot: it is kept beside ``snapshots/`` and its
    body is this module's own shape. Writing it is best-effort, since a run
    that cannot keep its pages is no worse off than one that never could.
    """

    def __init__(
        self,
        transport: casestore.ObjectTransport,
        planned: PlannedRefresh,
        today: date,
        resume: OnboardResume,
    ) -> None:
        self._transport = transport
        self._case_id = planned.case_id
        self._docket_id = planned.docket_id
        self._today = today
        self._resume = resume
        # Whether the object holds pages at all, usable or not: pages this
        # docket's onboard will never go on from are emptied when it finishes.
        self._holds_pages = False
        self.kept = self._load()

    def _load(self) -> _KeptPages | None:
        """The usable pages an earlier run kept; None when there are none to go on from."""
        try:
            body = casestore.read_onboard_partial(self._transport, self._case_id)
        except Exception as exc:  # broad by design: an unreadable store means a whole read
            logger.warning("watchlist-refresh: kept pages of %s unreadable: %s", self._case_id, exc)
            return None
        self._holds_pages = body is not None and "entries" in body
        if (
            body is None
            or body.get("kind") != _PARTIAL_KIND
            or body.get("version") != _PARTIAL_VERSION
            or body.get("docket_id") != self._docket_id
        ):
            return None
        pages, cursor, entries = body.get("pages"), body.get("cursor"), body.get("entries")
        try:
            started = date.fromisoformat(str(body.get("started")))
        except ValueError:
            return None
        if not (
            isinstance(pages, int)
            and not isinstance(pages, bool)
            and pages >= 1
            and (cursor is None or (isinstance(cursor, str) and cursor))
            and isinstance(entries, list)
            and all(isinstance(e, dict) and _has_id(e) for e in entries)
            and 0 <= (self._today - started).days <= self._resume.max_age_days
        ):
            return None
        return _KeptPages(started=started, pages=pages, cursor=cursor, entries=entries)

    def pages_owed(self, counted: int) -> int:
        """Requests the entries still cost, of a docket upstream counts at ``counted`` pages."""
        if self.kept is None:
            return counted
        # The pages not yet held (none once the whole read is done), and one
        # page of the closing read. A closing read that runs longer is not
        # sized here: the client's limiter holds the run to its share, and a
        # read it stops keeps its pages like any other.
        rest = 0 if self.kept.cursor is None else max(1, counted - self.kept.pages)
        return rest + 1

    def _write(self, body: dict[str, Any]) -> bool:
        try:
            casestore.write_onboard_partial(
                self._transport,
                self._case_id,
                {"kind": _PARTIAL_KIND, "version": _PARTIAL_VERSION, **body},
            )
        except Exception as exc:  # broad by design: keeping pages never fails the run
            logger.warning("watchlist-refresh: pages of %s not kept: %s", self._case_id, exc)
            return False
        return True

    def _keep(self, exc: BaseException, held: _KeptPages) -> None:
        """Store ``held`` for the next run, and say so on the failure being raised."""
        kept = self._write(
            {
                "docket_id": self._docket_id,
                "started": held.started.isoformat(),
                "updated": self._today.isoformat(),
                "pages": held.pages,
                "cursor": held.cursor,
                "entries": held.entries,
            }
        )
        if kept:
            exc.add_note(
                f"kept {held.pages} page(s) of entries, read since {held.started}, "
                "for this docket's next onboard"
            )

    def _drop(self) -> None:
        """Empty the object: the next onboard of this docket starts from its first page."""
        self._write({"docket_id": self._docket_id, "cleared": self._today.isoformat()})

    def read(
        self, client: CourtListenerClient, asked: _Requests, max_entry_pages: int
    ) -> list[dict[str, Any]]:
        """Every entry of the docket: the kept pages, the pages after them, the closing read.

        Raises what the read raised, having kept the pages it held by then.
        """
        kept = self.kept
        started = kept.started if kept is not None else self._today
        entries = list(kept.entries) if kept is not None else []
        before = kept.pages if kept is not None else 0
        pages, cursor = before, (kept.cursor if kept is not None else None)
        if kept is None or kept.cursor is not None:
            if before >= max_entry_pages:
                raise EntryPageCapExceeded(
                    f"docket {self._docket_id} has more than {max_entry_pages} pages of entries "
                    "in all"
                )

            def on_page(found: list[dict[str, Any]], following: str | None) -> None:
                nonlocal pages, cursor
                for entry in found:
                    int(entry["id"])  # a malformed entry fails the read; it is never kept
                entries.extend(found)
                pages, cursor = pages + 1, following

            asked.whole_read_starts_after(before)
            try:
                read = client.docket_entries(
                    self._docket_id,
                    max_pages=max_entry_pages - before,
                    cursor=cursor,
                    on_request=lambda: asked.page(None),
                    on_page=on_page,
                )
            except Exception as exc:
                if pages > before and cursor is not None:
                    self._keep(exc, _KeptPages(started, pages, cursor, entries))
                elif kept is not None and pages == before and _refuses_cursor(exc):
                    self._drop()
                    exc.add_note("the kept pages' cursor was refused; they are dropped")
                raise
            if not read.complete:
                raise EntryPageCapExceeded(
                    f"docket {self._docket_id} has more than {max_entry_pages} pages of entries "
                    "in all"
                )
        if kept is None:
            return entries
        since = started - timedelta(days=self._resume.overlap_days)
        try:
            closing = client.docket_entries(
                self._docket_id,
                max_pages=max_entry_pages,
                date_modified_gte=since,
                on_request=lambda: asked.page(since),
            )
        except Exception as exc:
            if kept.cursor is not None:
                self._keep(exc, _KeptPages(started, pages, None, entries))
            raise
        if not closing.complete:
            raise EntryPageCapExceeded(
                f"docket {self._docket_id} has more than {max_entry_pages} pages of entries "
                f"changed since {since}"
            )
        return merge_entries(entries, closing.entries)

    def finish(self) -> None:
        """The docket's snapshot is stored: whatever pages the object held are emptied."""
        if self._holds_pages:
            self._drop()


def _has_id(entry: Mapping[str, Any]) -> bool:
    try:
        int(entry["id"])
    except (KeyError, TypeError, ValueError):
        return False
    return True


def _refuses_cursor(exc: BaseException) -> bool:
    """Whether upstream refused the request as asked (400) or found nothing at it (404).

    Not a 401 or 403, which refuse the caller whatever it asks: kept pages are
    not dropped over a credential.
    """
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code in (
        httpx.codes.BAD_REQUEST,
        httpx.codes.NOT_FOUND,
    )


def _onboard_keeper(
    corpus_db_path: Path, planned: PlannedRefresh, today: date, resume: OnboardResume | None
) -> _OnboardKeeper | None:
    """The keeper of this docket's onboard, where the run may write the content store.

    None without ``resume``, and wherever a corpus write on this database would
    not reach the store (a dev checkout, a scratch database): pages that cannot
    be emptied again are not read either, so such a run reads whole.
    """
    if resume is None:
        return None
    with corpus.connect(corpus_db_path) as conn:
        transport = casestore.write_transport(conn)
    return None if transport is None else _OnboardKeeper(transport, planned, today, resume)


class _Requests:
    """One refresh's requests: counted, and each named to the caller before it is sent."""

    def __init__(
        self, on_request: Callable[[], None] | None, on_step: Callable[[str], None] | None
    ) -> None:
        self.sent = 0
        # Pages asked for so far, by the date each read is narrowed to (None: whole).
        self._pages: dict[date | None, int] = {}
        self._on_request = on_request
        self._on_step = on_step

    def send(self, step: str) -> None:
        self.sent += 1
        if self._on_request is not None:
            self._on_request()
        if self._on_step is not None:
            self._on_step(step)

    def size(self) -> None:
        self.send("the entry count")

    def page(self, since: date | None) -> None:
        """The next page of the entries, of those changed since ``since`` when narrowed."""
        number = self._pages[since] = self._pages.get(since, 0) + 1
        self.send(f"page {number} of the entries" + (f" changed since {since}" if since else ""))

    def whole_read_starts_after(self, pages: int) -> None:
        """Number the whole read's pages from after ``pages`` an earlier run kept."""
        self._pages[None] = pages


@dataclass(frozen=True)
class Refreshed:
    case_id: str
    mode: ReadMode
    changed: bool
    entries: int
    # Requests this refresh sent: the entry count on an onboard, the docket
    # and each page of entries.
    requests: int
    # Pages of entries an onboard took from an earlier run's kept pages
    # rather than asking for again; 0 for a read made whole in this run.
    resumed_pages: int = 0
    # The docket's own fields, without its entries.
    docket: Mapping[str, Any] = field(default_factory=dict, compare=False)
    # Entries the stored docket lacked; empty on an onboard, which has no
    # stored docket to be new against.
    added: tuple[Mapping[str, Any], ...] = field(default=(), compare=False)
    # Entries the stored docket held whose documents became readable, each with
    # the ids of those documents; empty on an onboard.
    gained: tuple[tuple[Mapping[str, Any], frozenset[int]], ...] = field(default=(), compare=False)
    # Every entry the docket holds after this refresh, where a new entry's
    # placeholder or numbered twin is looked for.
    listed: tuple[Mapping[str, Any], ...] = field(default=(), compare=False)


def _read_entries(
    client: CourtListenerClient,
    docket_id: int,
    asked: _Requests,
    since: date | None,
    stored: object,
    max_entry_pages: int,
) -> list[dict[str, Any]]:
    """One read made in this run alone: whole, or what changed since ``since`` over ``stored``."""
    read = client.docket_entries(
        docket_id,
        max_pages=max_entry_pages,
        date_modified_gte=since,
        on_request=lambda: asked.page(since),
    )
    if not read.complete:
        what = f"changed since {since}" if since else "in all"
        raise EntryPageCapExceeded(
            f"docket {docket_id} has more than {max_entry_pages} pages of entries {what}"
        )
    return merge_entries(stored if since and isinstance(stored, list) else [], read.entries)


def refresh_docket(  # noqa: PLR0913 - each option bounds or observes the one refresh
    client: CourtListenerClient,
    corpus_db_path: Path,
    planned: PlannedRefresh,
    *,
    max_entry_pages: int,
    today: date,
    share_left: int | None = None,
    on_request: Callable[[], None] | None = None,
    on_step: Callable[[str], None] | None = None,
    resume: OnboardResume | None = None,
) -> Refreshed:
    """Read one docket, store its snapshot if it changed, and stamp its row.

    ``share_left`` is what remains of the run's share: a full read the stored
    docket's length says it cannot cover is taken incrementally instead, and an
    onboard it cannot cover at upstream's count of its entries (at the page cap
    without a count) raises :class:`OnboardDoesNotFit` before its entries are
    read. Raises :class:`EntryPageCapExceeded` before writing anything when the
    count puts a docket past ``max_entry_pages`` or a read does not finish
    within it, so a truncated docket is never stored as if whole.

    ``on_request`` is called before each request is sent, and ``on_step`` with
    what that request asks for (the entry count, the docket, or a numbered page
    of the entries), so a caller can say where a read that raised had got to.

    With ``resume``, where the run may write the content store, an onboard that
    raises part-way keeps the pages it fetched (the exception carries a note
    saying so), and an onboard of a docket with kept pages goes on from them:
    it is sized at the pages still owed, and closes with a read of what changed
    since the day the first attempt began.
    """
    case_id = planned.case_id
    asked = _Requests(on_request, on_step)
    # Kept pages are looked for only where the read is an onboard.
    keeper = (
        _onboard_keeper(corpus_db_path, planned, today, resume)
        if planned.mode is ReadMode.onboard
        else None
    )

    def owed(counted: int) -> int:
        return counted if keeper is None else keeper.pages_owed(counted)

    def left() -> int | None:
        return None if share_left is None else share_left - asked.sent

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
        pages = owed(_onboard_pages(client, planned.docket_id, max_entry_pages, asked.size))
        if not _fits(left(), 1 + pages):
            raise OnboardDoesNotFit(
                f"{case_id}: {left()} of the share left, under this onboard's {1 + pages}",
                requests=asked.sent,
            )
    asked.send("the docket")
    docket = client.get_docket(planned.docket_id)
    with corpus.connect(corpus_db_path) as conn:
        prior = corpus.latest_snapshot(conn, case_id)
    stored = prior[1].get("docket_entries") if prior is not None else None
    mode = planned.mode
    if not isinstance(stored, list) and planned.mode is not ReadMode.onboard:
        # Nothing stored to merge into: only a whole read will do.
        mode = ReadMode.onboard
        keeper = _onboard_keeper(corpus_db_path, planned, today, resume)
        if not _fits(left(), 1 + least):
            raise OnboardDoesNotFit(
                f"{case_id}: no stored snapshot, and the share left cannot cover an onboard",
                requests=asked.sent,
            )
        pages = owed(_onboard_pages(client, planned.docket_id, max_entry_pages, asked.size))
        if not _fits(left(), pages):
            raise OnboardDoesNotFit(
                f"{case_id}: no stored snapshot, and the share left cannot cover an onboard",
                requests=asked.sent,
            )
    elif (
        mode is ReadMode.full
        and isinstance(stored, list)
        and share_left is not None
        and 1 + max(1, ceil(len(stored) / ENTRIES_PER_PAGE)) > share_left
    ):
        mode = ReadMode.incremental
    since = planned.since if mode is ReadMode.incremental else None
    if keeper is not None:
        entries = merge_entries([], keeper.read(client, asked, max_entry_pages))
    else:
        entries = _read_entries(client, planned.docket_id, asked, since, stored, max_entry_pages)
    fresh = {**docket, "docket_entries": entries}
    changed = prior is None or prior[1] != fresh
    if changed:
        with corpus.connect(corpus_db_path) as conn:
            corpus.upsert_snapshot(conn, case_id, today, fresh)
    upsert_to_corpus(corpus_db_path, [from_api_docket(fresh)], last_pulled=today)
    resumed = keeper.kept.pages if keeper is not None and keeper.kept is not None else 0
    if keeper is not None:
        keeper.finish()
    known = {e.get("id") for e in stored} if isinstance(stored, list) else None
    added = () if known is None else tuple(e for e in entries if e.get("id") not in known)
    gained = () if not isinstance(stored, list) else tuple(became_available(stored, entries))
    return Refreshed(
        case_id=case_id,
        mode=mode,
        changed=changed,
        entries=len(entries),
        requests=asked.sent,
        resumed_pages=resumed,
        docket=docket,
        added=added,
        gained=gained,
        listed=tuple(e for e in entries if isinstance(e, Mapping)),
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
            # case id -> pages an onboard took from an earlier run's kept pages.
            "resumed": {r.case_id: r.resumed_pages for r in self.refreshed if r.resumed_pages},
            "failed": dict(sorted(self.failed.items())),
            "deferred": list(self.deferred),
            "stop_reason": self.stop_reason,
        }


class _ReadProgress:
    """Where one docket's read has got to, and since when, for a failure's reason."""

    def __init__(self, clock: Callable[[], float]) -> None:
        self._clock = clock
        self._began = clock()
        self._step: str | None = None
        self._step_at = self._began

    def at(self, step: str) -> None:
        self._step, self._step_at = step, self._clock()

    def where(self, exc: BaseException) -> str:
        """The last request the read asked for before ``exc``, and the time it had taken.

        The first time is from when that request was asked for, so it covers
        the limiter's wait before it was sent and every resend the client made
        of it; the second is the docket's whole read. A failure raised after
        that request answered (a malformed entry, a read past the page cap) is
        placed by it all the same. ``""`` for a read that raised before asking
        for anything.
        """
        if self._step is None:
            return ""
        now = self._clock()
        cursor = failed_cursor(exc)
        return (
            f"last request: {self._step}"
            + (f", cursor {cursor}" if cursor else "")
            + f"; {now - self._step_at:.0f}s since it was asked for, waits and resends included, "
            + f"{now - self._began:.0f}s into this docket's read"
        )


def _notes(exc: BaseException) -> list[str]:
    """What the refresh itself noted on a failure it let through: pages kept, or dropped."""
    return [str(note) for note in getattr(exc, "__notes__", ())]


def _bracketed(notes: Iterable[str]) -> str:
    return "".join(f" [{note}]" for note in notes if note)


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
    resume: OnboardResume | None = None,
) -> WatchlistRefreshReport:
    """Refresh the planned dockets in order until the plan, the share or the time runs out.

    ``share`` is the lane's per-run request cap, which the client also enforces;
    it is passed here so a full read the rest of the share cannot cover falls
    back to an incremental one rather than stopping the run, and an onboard it
    cannot cover is deferred while the run goes on. A docket that
    fails (an HTTP error, a malformed entry, or a read past ``max_entry_pages``)
    is recorded, with the last request its read asked for and the time since,
    and skipped. The share running out, the ``deadline`` (a
    ``clock`` reading) passing, or ``max_consecutive_transient_failures``
    transient errors in a row stop the run, and the dockets not reached are
    deferred. None of these writes a snapshot or a row for the docket, which
    keeps its place in the next run's plan; with ``resume``, an onboard stopped
    part-way keeps the pages it fetched for that run to go on from, and its
    reason (or the run's stop reason) says so. A never-refreshed docket longer
    than the page cap fails each run that reaches it, on its count alone, until
    the cap is raised, and the command exits non-zero on any failure so that is
    seen.

    ``on_refreshed`` is called with each docket as soon as its write lands, so
    a caller recording what a docket added keeps that record even if the run
    is killed before it returns.
    """
    report = WatchlistRefreshReport()
    # Every request a refresh asks for, failed reads included, so the share
    # left holds after a read that fails part-way. A request the client sends
    # again (a retry, or after waiting out a refusal) is counted once here and
    # each time by the client's limiter, which is what enforces the share: a
    # run with resends reaches the limiter's cap a few requests early and
    # stops there.
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
        progress = _ReadProgress(clock)
        try:
            done = refresh_docket(
                client,
                corpus_db_path,
                planned,
                max_entry_pages=max_entry_pages,
                today=today,
                share_left=share - spent,
                on_request=count,
                on_step=progress.at,
                resume=resume,
            )
        except RateBudgetExceeded as exc:
            report.stop_reason = str(exc) + _bracketed(_notes(exc))
            report.deferred.extend(p.case_id for p in plan[index:])
            break
        except OnboardDoesNotFit:
            # A shorter read further on may still fit, so the run goes on.
            report.deferred.append(planned.case_id)
            continue
        except (httpx.HTTPError, EntryPageCapExceeded, KeyError, ValueError) as exc:
            # What upstream said about a refusal rides the reason: for a 429,
            # the limit that refused and the wait it asked for. So does where
            # the read stopped, and whether its pages were kept for the next run.
            notes = [refusal_detail(exc), progress.where(exc), *_notes(exc)]
            report.failed[planned.case_id] = f"{type(exc).__name__}: {exc}" + _bracketed(notes)
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
