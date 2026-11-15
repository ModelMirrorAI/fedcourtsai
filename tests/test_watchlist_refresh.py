import json
from collections.abc import Callable
from contextlib import nullcontext
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus
from fedcourtsai.ai_activity import activity_path
from fedcourtsai.ai_watchlist import AI_WATCHLIST_FILENAME, load_ai_watchlist
from fedcourtsai.cli import app
from fedcourtsai.courtlistener import (
    CourtListenerClient,
    EntryPageCapExceeded,
    EntryPages,
    RateBudgetExceeded,
    default_rate_limiter,
)
from fedcourtsai.pipeline.ingest import from_api_docket, upsert_to_corpus
from fedcourtsai.pipeline.watchlist_refresh import (
    OnboardDoesNotFit,
    OnboardResume,
    PlannedRefresh,
    ReadMode,
    WatchlistRefreshReport,
    full_read_due,
    merge_entries,
    plan_refresh,
    refresh_docket,
    refresh_watchlist,
    refreshed_on,
)
from fedcourtsai.schemas import AiCaseActivity
from fedcourtsai.serialize import read_model

TODAY = date(2026, 11, 2)


def _docket(docket_id: int, court: str = "cand") -> dict[str, Any]:
    return {
        "id": docket_id,
        "court": f"https://www.courtlistener.com/api/rest/v4/courts/{court}/",
        "docket_number": "3:25-cv-08133",
        "case_name": "X.AI LLC v. OpenAI, Inc.",
        "date_filed": "2025-09-24",
        "nature_of_suit": "Other Statutory Actions",
    }


class FakeClient:
    """Canned docket facts; records which reads were asked for."""

    def __init__(
        self,
        entries: dict[int, list[dict[str, Any]]],
        *,
        changed: dict[int, list[dict[str, Any]]] | None = None,
        incomplete: frozenset[int] = frozenset(),
        over_budget: frozenset[int] = frozenset(),
        broken: frozenset[int] = frozenset(),
        pages: int = 1,
        counts: dict[int, int | None] | None = None,
    ) -> None:
        self.entries = entries
        self.changed = changed or {}
        self.incomplete = incomplete
        self.over_budget = over_budget
        self.broken = broken
        self.pages = pages
        # Upstream's count of a docket's entries; by default what it serves.
        self.counts = counts or {}
        self.counted: list[int] = []
        self.reads: list[tuple[int, str, date | None]] = []

    def count_docket_entries(self, docket_id: int) -> int | None:
        self.counted.append(docket_id)
        if docket_id in self.over_budget:
            raise RateBudgetExceeded("lane share spent")
        if docket_id in self.broken:
            raise httpx.ConnectError("upstream down")
        if docket_id in self.counts:
            return self.counts[docket_id]
        return len(self.entries.get(docket_id, []))

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        if docket_id in self.over_budget:
            raise RateBudgetExceeded("lane share spent")
        if docket_id in self.broken:
            raise httpx.ConnectError("upstream down")
        return _docket(docket_id)

    def docket_entries(
        self,
        docket_id: int,
        *,
        max_pages: int,
        date_modified_gte: date | None = None,
        on_request: Callable[[], None] | None = None,
    ) -> EntryPages:
        for _ in range(self.pages):
            if on_request is not None:
                on_request()
        if date_modified_gte is None:
            self.reads.append((docket_id, "whole", None))
            found = self.entries.get(docket_id, [])
        else:
            self.reads.append((docket_id, "since", date_modified_gte))
            found = self.changed.get(docket_id, [])
        return EntryPages(found, self.pages, docket_id not in self.incomplete)


_LISTED_COURTS = {
    docket_id: court
    for case in load_ai_watchlist(
        Path(__file__).resolve().parents[1] / "config" / AI_WATCHLIST_FILENAME
    ).cases
    for court, docket_id in case.dockets()
}


class ListedClient(FakeClient):
    """A fake that serves each listed docket under its own court."""

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        return _docket(docket_id, _LISTED_COURTS.get(docket_id, "cand"))


def _db(tmp_path: Path) -> Path:
    return corpus.corpus_db_path(tmp_path / "corpus")


def _client(fake: FakeClient) -> CourtListenerClient:
    return cast(CourtListenerClient, fake)


def _stamp(db: Path, docket_id: int, last_pulled: date) -> None:
    upsert_to_corpus(db, [from_api_docket(_docket(docket_id))], last_pulled=last_pulled)


def _planned(docket_id: int, mode: ReadMode, since: date | None = None) -> PlannedRefresh:
    last = since + timedelta(days=2) if since else None
    return PlannedRefresh("cand", docket_id, mode, last, since)


def test_full_read_days_spread_over_the_week() -> None:
    days = [TODAY + timedelta(days=n) for n in range(7)]
    assert sum(full_read_due(5, day, 7) for day in days) == 1
    picked = {next(n for n, day in enumerate(days) if full_read_due(d, day, 7)) for d in range(7)}
    assert picked == set(range(7))


def test_plan_puts_one_onboard_first_then_incremental_reads_then_the_rest(
    tmp_path: Path,
) -> None:
    db = _db(tmp_path)
    # Ids chosen so none falls on TODAY's full-read day.
    full_day = next(d for d in range(1, 20) if full_read_due(d, TODAY, 7))
    old, recent = [d for d in range(1, 20) if d != full_day][:2]
    _stamp(db, old, TODAY - timedelta(days=5))
    _stamp(db, recent, TODAY - timedelta(days=1))
    _stamp(db, full_day, TODAY - timedelta(days=1))
    with corpus.connect(db) as conn:
        plan = plan_refresh(
            conn,
            [("cand", recent), ("cand", old), ("cand", 99), ("cand", full_day), ("cand", old)],
            today=TODAY,
            overlap_days=2,
            full_read_every_days=7,
        )
    assert [(p.docket_id, p.mode) for p in plan] == [
        (99, ReadMode.onboard),
        (old, ReadMode.incremental),
        (recent, ReadMode.incremental),
        (full_day, ReadMode.full),
    ]
    by_id = {p.docket_id: p for p in plan}
    assert by_id[old].since == TODAY - timedelta(days=7)
    # A full read keeps its incremental date, for when the share cannot cover it.
    assert by_id[full_day].since == TODAY - timedelta(days=3)
    assert by_id[99].since is None


def test_a_docket_stamped_today_means_the_day_has_run() -> None:
    plan = [
        _planned(1, ReadMode.onboard),
        _planned(2, ReadMode.incremental, TODAY - timedelta(days=3)),
    ]
    assert not refreshed_on(plan, TODAY)
    assert refreshed_on(plan, TODAY - timedelta(days=1))


def test_merge_lays_changed_entries_over_stored_newest_id_first() -> None:
    stored = [{"id": 3, "d": "old"}, {"id": 1, "d": "a"}]
    changed = [{"id": 3, "d": "new"}, {"id": 4, "d": "b"}]
    assert merge_entries(stored, changed) == [
        {"id": 4, "d": "b"},
        {"id": 3, "d": "new"},
        {"id": 1, "d": "a"},
    ]


def test_onboard_stores_snapshot_and_row_and_nothing_else(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient(
        {7: [{"id": 1, "description": "Complaint"}, {"id": 2, "description": "Order"}]}
    )
    done = refresh_docket(
        _client(fake), db, _planned(7, ReadMode.onboard), max_entry_pages=150, today=TODAY
    )
    assert done.changed and done.entries == 2
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "cand/7")
        snap = corpus.latest_snapshot(conn, "cand/7")
        events = corpus.events_for_case(conn, "cand/7")
    assert row is not None and row.court == "cand" and row.last_pulled == TODAY
    assert snap is not None and snap[0] == TODAY
    assert [e["id"] for e in snap[1]["docket_entries"]] == [2, 1]
    # Facts only: a stay motion or an order is never extracted as an event.
    assert events == []


def test_incremental_read_merges_into_the_stored_docket(tmp_path: Path) -> None:
    db = _db(tmp_path)
    first = FakeClient({7: [{"id": 1, "description": "Complaint"}]})
    refresh_docket(
        _client(first), db, _planned(7, ReadMode.onboard), max_entry_pages=150, today=TODAY
    )
    since = TODAY - timedelta(days=2)
    later = TODAY + timedelta(days=1)
    second = FakeClient({}, changed={7: [{"id": 5, "description": "Motion to dismiss"}]})
    done = refresh_docket(
        _client(second),
        db,
        _planned(7, ReadMode.incremental, since),
        max_entry_pages=150,
        today=later,
    )
    assert second.reads == [(7, "since", since)]
    assert done.changed and done.mode is ReadMode.incremental
    with corpus.connect(db) as conn:
        snap = corpus.latest_snapshot(conn, "cand/7")
    assert snap is not None and snap[0] == later
    assert [e["id"] for e in snap[1]["docket_entries"]] == [5, 1]
    assert [e["id"] for e in done.added] == [5]
    assert [e["id"] for e in done.listed] == [5, 1]


def test_an_entry_whose_document_became_readable_is_reported(tmp_path: Path) -> None:
    db = _db(tmp_path)
    sealed = {"id": 70, "attachment_number": None, "is_available": False}
    first = FakeClient({7: [{"id": 1, "description": "Order", "recap_documents": [sealed]}]})
    refresh_docket(
        _client(first), db, _planned(7, ReadMode.onboard), max_entry_pages=150, today=TODAY
    )
    since = TODAY - timedelta(days=2)
    readable = {**sealed, "is_available": True}
    second = FakeClient(
        {}, changed={7: [{"id": 1, "description": "Order", "recap_documents": [readable]}]}
    )
    done = refresh_docket(
        _client(second),
        db,
        _planned(7, ReadMode.incremental, since),
        max_entry_pages=150,
        today=TODAY + timedelta(days=1),
    )
    assert done.added == ()
    assert [(e["id"], ids) for e, ids in done.gained] == [(1, frozenset({70}))]


def test_an_unchanged_docket_stores_no_new_snapshot(tmp_path: Path) -> None:
    db = _db(tmp_path)
    entries = {7: [{"id": 1, "description": "Complaint"}]}
    refresh_docket(
        _client(FakeClient(entries)),
        db,
        _planned(7, ReadMode.onboard),
        max_entry_pages=150,
        today=TODAY,
    )
    later = TODAY + timedelta(days=1)
    done = refresh_docket(
        _client(FakeClient(entries)),
        db,
        _planned(7, ReadMode.full),
        max_entry_pages=150,
        today=later,
    )
    assert not done.changed
    with corpus.connect(db) as conn:
        snap = corpus.latest_snapshot(conn, "cand/7")
        row = corpus.get_row(conn, "cand/7")
    assert snap is not None and snap[0] == TODAY
    assert row is not None and row.last_pulled == later


def test_an_incremental_plan_with_no_stored_snapshot_reads_the_whole_docket(
    tmp_path: Path,
) -> None:
    db = _db(tmp_path)
    _stamp(db, 7, TODAY - timedelta(days=1))
    fake = FakeClient({7: [{"id": 1}]})
    done = refresh_docket(
        _client(fake),
        db,
        _planned(7, ReadMode.incremental, TODAY - timedelta(days=3)),
        max_entry_pages=150,
        today=TODAY,
    )
    assert fake.reads == [(7, "whole", None)]
    assert done.mode is ReadMode.onboard


@pytest.mark.parametrize("mode", [ReadMode.onboard, ReadMode.incremental])
def test_a_read_past_the_page_cap_writes_nothing(tmp_path: Path, mode: ReadMode) -> None:
    db = _db(tmp_path)
    if mode is ReadMode.incremental:
        refresh_docket(
            _client(FakeClient({7: [{"id": 1}]})),
            db,
            _planned(7, ReadMode.onboard),
            max_entry_pages=150,
            today=TODAY - timedelta(days=1),
        )
    fake = FakeClient({7: [{"id": 1}]}, incomplete=frozenset({7}))
    with pytest.raises(EntryPageCapExceeded):
        refresh_docket(
            _client(fake),
            db,
            _planned(7, mode, TODAY - timedelta(days=3)),
            max_entry_pages=150,
            today=TODAY,
        )
    with corpus.connect(db) as conn:
        snap = corpus.latest_snapshot(conn, "cand/7")
        row = corpus.get_row(conn, "cand/7")
    if mode is ReadMode.onboard:
        assert snap is None and row is None
    else:
        assert snap is not None and snap[0] == TODAY - timedelta(days=1)
        assert row is not None and row.last_pulled == TODAY - timedelta(days=1)


def test_a_run_records_failures_and_defers_what_the_share_does_not_reach(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient(
        {1: [{"id": 1}], 2: [{"id": 2}], 3: [{"id": 3}], 4: [{"id": 4}]},
        incomplete=frozenset({2}),
        broken=frozenset({1}),
        over_budget=frozenset({3}),
    )
    plan = [_planned(n, ReadMode.onboard) for n in (1, 2, 4, 3, 5)]
    report = refresh_watchlist(_client(fake), db, plan, max_entry_pages=150, today=TODAY, share=160)
    assert [r.case_id for r in report.refreshed] == ["cand/4"]
    assert set(report.failed) == {"cand/1", "cand/2"}
    assert report.deferred == ["cand/3", "cand/5"]
    assert report.stop_reason == "lane share spent"
    assert report.as_json()["refreshed"] == [
        {"case_id": "cand/4", "mode": "onboard", "changed": True, "entries": 1, "requests": 3}
    ]


def _onboarded(db: Path, docket_id: int, entries: int) -> None:
    fake = FakeClient({docket_id: [{"id": n} for n in range(1, entries + 1)]})
    refresh_docket(
        _client(fake),
        db,
        _planned(docket_id, ReadMode.onboard),
        max_entry_pages=150,
        today=TODAY - timedelta(days=1),
    )


def test_a_full_read_the_share_left_cannot_cover_is_taken_incrementally(
    tmp_path: Path,
) -> None:
    db = _db(tmp_path)
    _onboarded(db, 7, 60)  # three pages stored: a full read costs four requests
    since = TODAY - timedelta(days=3)
    short = FakeClient({}, changed={7: [{"id": 61}]})
    done = refresh_docket(
        _client(short),
        db,
        _planned(7, ReadMode.full, since),
        max_entry_pages=150,
        today=TODAY,
        share_left=3,
    )
    assert short.reads == [(7, "since", since)]
    assert done.mode is ReadMode.incremental and done.entries == 61

    roomy = FakeClient({7: [{"id": n} for n in range(2, 62)]})
    done = refresh_docket(
        _client(roomy),
        db,
        _planned(7, ReadMode.full, since),
        max_entry_pages=150,
        today=TODAY + timedelta(days=1),
        share_left=5,  # 61 entries stored now: four pages and the docket
    )
    # The whole read drops the entry deleted upstream, which no merge would.
    assert roomy.reads == [(7, "whole", None)]
    assert done.mode is ReadMode.full and done.entries == 60


def test_the_share_left_shrinks_by_what_each_refresh_spent(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _onboarded(db, 7, 60)
    _onboarded(db, 8, 60)
    fake = FakeClient({7: [{"id": n} for n in range(1, 61)], 8: [{"id": n} for n in range(1, 61)]})
    plan = [_planned(n, ReadMode.full, TODAY - timedelta(days=3)) for n in (7, 8)]
    report = refresh_watchlist(_client(fake), db, plan, max_entry_pages=150, today=TODAY, share=5)
    # Docket 7's full read costs two here (one page), leaving three: under docket
    # 8's stored four, so 8 is read incrementally.
    assert [r.mode for r in report.refreshed] == [ReadMode.full, ReadMode.incremental]


def test_a_run_stops_at_its_deadline_and_defers_the_rest(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient({n: [{"id": n}] for n in (1, 2, 3)})
    plan = [_planned(n, ReadMode.onboard) for n in (1, 2, 3)]
    report = refresh_watchlist(
        _client(fake),
        db,
        plan,
        max_entry_pages=150,
        today=TODAY,
        share=160,
        deadline=10.0,
        # Six seconds a docket read: the third would start past the deadline.
        clock=lambda: 6.0 * len(fake.counted),
    )
    assert [r.case_id for r in report.refreshed] == ["cand/1", "cand/2"]
    assert report.deferred == ["cand/3"]
    assert report.stop_reason == "the run's wall-clock budget is spent"


def test_a_run_of_transient_failures_stops_the_run(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient({4: [{"id": 4}]}, broken=frozenset({1, 2, 3}))
    plan = [_planned(n, ReadMode.onboard) for n in (1, 2, 3, 4)]
    report = refresh_watchlist(
        _client(fake),
        db,
        plan,
        max_entry_pages=150,
        today=TODAY,
        share=160,
        max_consecutive_transient_failures=3,
    )
    assert report.refreshed == []
    assert set(report.failed) == {"cand/1", "cand/2", "cand/3"}
    assert report.deferred == ["cand/4"]
    assert report.stop_reason is not None and "transient" in report.stop_reason


class ThrottledClient(FakeClient):
    """A fake whose named dockets are refused with upstream's 429."""

    def __init__(self, entries: dict[int, list[dict[str, Any]]], throttled: frozenset[int]) -> None:
        super().__init__(entries)
        self.throttled = throttled

    def get_docket(self, docket_id: int) -> dict[str, Any]:
        if docket_id in self.throttled:
            request = httpx.Request("GET", f"{_API}dockets/{docket_id}/")
            response = httpx.Response(
                429,
                json={"detail": "Request was throttled. Rate limit exceeded: 300/hour."},
                headers={"Retry-After": "1800"},
                request=request,
            )
            raise httpx.HTTPStatusError("429 Too Many Requests", request=request, response=response)
        return super().get_docket(docket_id)


_API = "https://www.courtlistener.com/api/rest/v4/"


def test_a_refused_docket_s_reason_names_the_limit_that_refused(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = ThrottledClient({1: [{"id": 1}], 2: [{"id": 2}]}, throttled=frozenset({1}))
    plan = [_planned(n, ReadMode.onboard) for n in (1, 2)]
    report = refresh_watchlist(_client(fake), db, plan, max_entry_pages=150, today=TODAY, share=160)
    assert report.failed["cand/1"] == (
        "HTTPStatusError: 429 Too Many Requests "
        + "[Retry-After 1800s; upstream said: Request was throttled. "
        + "Rate limit exceeded: 300/hour.] "
        + "[last request: the docket; 0s since it was asked for, waits and resends included, "
        + "0s into this docket's read]"
    )
    assert [r.case_id for r in report.refreshed] == ["cand/2"]


def test_a_long_onboard_refused_mid_read_waits_and_lands_whole(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The real client under the refresh: a 429 partway through the pages costs a wait.

    Upstream refuses the third page of a five-page docket, stating a 51-second
    wait, until a request arrives after that wait. A client that holds for it
    stores every entry; one that never holds retries seconds apart, is refused
    each time, and loses the read.
    """
    get: Any = CourtListenerClient._get  # tenacity attaches the Retrying as `.retry`
    monkeypatch.setattr(get.retry, "sleep", lambda _seconds: None)
    pages = 5

    def run(
        db: Path, *, max_throttle_wait: float = 0.0, throttle_wait_budget: float = 0.0
    ) -> tuple[WatchlistRefreshReport, list[float]]:
        slept: list[float] = []

        def handle(request: httpx.Request) -> httpx.Response:
            params = dict(request.url.params)
            if request.url.path.endswith("/dockets/7/"):
                return httpx.Response(200, json=_docket(7))
            if params.get("count") == "on":
                return httpx.Response(200, json={"count": pages * 20})
            page = int(params.get("cursor", "1"))
            if page == 3 and sum(slept) < 51:
                return httpx.Response(
                    429,
                    json={"detail": "Request was throttled. Rate limit exceeded: 25/min."},
                    headers={"Retry-After": "51"},
                )
            entries = [{"id": page * 100 + n} for n in range(20)]
            following = (
                f"{_API}docket-entries/?cursor={page + 1}&docket=7" if page < pages else None
            )
            return httpx.Response(200, json={"results": entries, "next": following})

        client = CourtListenerClient(
            rate_limiter=default_rate_limiter(10_000, 10_000, 10_000),
            sleep_fn=slept.append,
            max_throttle_wait=max_throttle_wait,
            throttle_wait_budget=throttle_wait_budget,
        )
        client._client = httpx.Client(base_url=_API, transport=httpx.MockTransport(handle))
        with client:
            report = refresh_watchlist(
                client,
                db,
                [_planned(7, ReadMode.onboard)],
                max_entry_pages=150,
                today=TODAY,
                share=160,
            )
        return report, slept

    held, slept = run(_db(tmp_path / "held"), max_throttle_wait=65.0, throttle_wait_budget=180.0)
    assert held.failed == {}
    assert [(r.case_id, r.entries) for r in held.refreshed] == [("cand/7", pages * 20)]
    assert slept == [52.0]
    # The count, the docket and the five pages: the refresh counts a page
    # once, however many times the client sent it.
    assert held.refreshed[0].requests == 2 + pages

    unheld, slept = run(_db(tmp_path / "unheld"))
    assert unheld.refreshed == [] and slept == []
    assert "Rate limit exceeded: 25/min" in unheld.failed["cand/7"]
    assert "Retry-After 51s" in unheld.failed["cand/7"]


def test_a_read_that_times_out_says_which_page_and_how_long_it_took(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The real client under the refresh: one page of a long onboard never answers.

    Upstream serves the count, the docket and two pages in a second each, then
    times out on the third page however often the client sends it. The reason
    names that page and its cursor, the time since it was first sent (every
    resend's timeout) and the time the whole read had run.
    """
    get: Any = CourtListenerClient._get  # tenacity attaches the Retrying as `.retry`
    monkeypatch.setattr(get.retry, "sleep", lambda _seconds: None)
    now = 0.0
    timed_out = 0

    def handle(request: httpx.Request) -> httpx.Response:
        nonlocal now, timed_out
        params = dict(request.url.params)
        if request.url.path.endswith("/dockets/7/"):
            now += 1
            return httpx.Response(200, json=_docket(7))
        if params.get("count") == "on":
            now += 1
            return httpx.Response(200, json={"count": 100})
        page = int(params.get("cursor", "1"))
        if page == 3:
            now += 30
            timed_out += 1
            raise httpx.ReadTimeout("The read operation timed out")
        now += 1
        entries = [{"id": page * 100 + n} for n in range(20)]
        return httpx.Response(
            200,
            json={"results": entries, "next": f"{_API}docket-entries/?cursor={page + 1}&docket=7"},
        )

    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client = httpx.Client(base_url=_API, transport=httpx.MockTransport(handle))
    db = _db(tmp_path)
    with client:
        report = refresh_watchlist(
            client,
            db,
            [_planned(7, ReadMode.onboard)],
            max_entry_pages=150,
            today=TODAY,
            share=160,
            clock=lambda: now,
        )
    assert timed_out == 4
    assert report.failed == {
        "cand/7": "ReadTimeout: The read operation timed out "
        + "[last request: page 3 of the entries, cursor 3; 120s since it was asked for, "
        + "waits and resends included, 124s into this docket's read]"
    }
    with corpus.connect(db) as conn:
        assert corpus.latest_snapshot(conn, "cand/7") is None


class PagedUpstream:
    """A mock upstream for one docket of ``pages`` pages, entries newest id first.

    ``slow`` names pages that time out however often they are asked for;
    ``added`` is entries the date-narrowed read serves; ``refuse_cursor`` makes
    upstream answer any cursor with a 404. Every request is recorded.
    """

    def __init__(self, docket_id: int, pages: int) -> None:
        self.docket_id = docket_id
        self.pages = pages
        self.slow: set[int] = set()
        self.added: list[dict[str, Any]] = []
        self.refuse_cursor = False
        self.asked: list[str] = []

    def entries(self, page: int) -> list[dict[str, Any]]:
        top = (self.pages - page + 1) * 100
        return [{"id": top - n, "description": f"entry {top - n}"} for n in range(20)]

    def handle(self, request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        if request.url.path.endswith(f"/dockets/{self.docket_id}/"):
            self.asked.append("docket")
            return httpx.Response(200, json=_docket(self.docket_id))
        if params.get("count") == "on":
            self.asked.append("count")
            return httpx.Response(200, json={"count": self.pages * 20})
        if "date_modified__gte" in params:
            self.asked.append(f"since {params['date_modified__gte']}")
            return httpx.Response(200, json={"results": self.added, "next": None})
        if "cursor" in params and self.refuse_cursor:
            self.asked.append("refused")
            return httpx.Response(404, json={"detail": "Invalid cursor"})
        page = int(params.get("cursor", "1"))
        self.asked.append(f"page {page}")
        if page in self.slow:
            raise httpx.ReadTimeout("The read operation timed out")
        following = (
            f"{_API}docket-entries/?cursor={page + 1}&docket={self.docket_id}"
            if page < self.pages
            else None
        )
        return httpx.Response(200, json={"results": self.entries(page), "next": following})

    def client(self) -> CourtListenerClient:
        client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
        client._client = httpx.Client(base_url=_API, transport=httpx.MockTransport(self.handle))
        return client


_RESUME = OnboardResume(overlap_days=2, max_age_days=14)
_PARTIAL_KEY = "cand/7/onboard/partial.json"


def _onboard(upstream: PagedUpstream, db: Path, today: date) -> WatchlistRefreshReport:
    with upstream.client() as client:
        return refresh_watchlist(
            client,
            db,
            [_planned(upstream.docket_id, ReadMode.onboard)],
            max_entry_pages=150,
            today=today,
            share=160,
            resume=_RESUME,
        )


@pytest.fixture
def store(monkeypatch: pytest.MonkeyPatch) -> casestore.InMemoryObjectTransport:
    """An injected content store, and no backoff sleeps in the client's retries."""
    get: Any = CourtListenerClient._get  # tenacity attaches the Retrying as `.retry`
    monkeypatch.setattr(get.retry, "sleep", lambda _seconds: None)
    transport = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(transport)
    return transport


def test_an_onboard_stopped_part_way_goes_on_from_its_kept_pages(
    tmp_path: Path, store: casestore.InMemoryObjectTransport
) -> None:
    """A five-page docket whose fourth page times out one day and answers the next."""
    db = _db(tmp_path)
    upstream = PagedUpstream(7, pages=5)
    upstream.slow = {4}
    first = _onboard(upstream, db, TODAY)
    assert first.refreshed == []
    assert first.failed["cand/7"].endswith(
        f"[kept 3 page(s) of entries, read since {TODAY}, for this docket's next onboard]"
    )
    assert "[last request: page 4 of the entries, cursor 4;" in first.failed["cand/7"]
    kept = json.loads(store.objects[_PARTIAL_KEY])
    assert (kept["kind"], kept["docket_id"], kept["pages"], kept["cursor"]) == (
        "onboard-partial",
        7,
        3,
        "4",
    )
    assert len(kept["entries"]) == 60
    # The kept pages are not a snapshot, to the store's readers or the corpus's.
    assert casestore.read_latest_snapshot(store, "cand/7") is None
    with corpus.connect(db) as conn:
        assert corpus.latest_snapshot(conn, "cand/7") is None
        assert corpus.get_row(conn, "cand/7") is None

    # The next day: one entry was filed since, and one kept entry was amended.
    upstream.slow = set()
    upstream.added = [
        {"id": 900, "description": "filed since"},
        {"id": 500, "description": "amended"},
    ]
    upstream.asked.clear()
    following_day = TODAY + timedelta(days=1)
    second = _onboard(upstream, db, following_day)
    assert second.failed == {}
    assert upstream.asked == [
        "count",
        "docket",
        "page 4",
        "page 5",
        f"since {TODAY - timedelta(2)}",
    ]
    done = second.refreshed[0]
    assert (done.entries, done.requests, done.resumed_pages) == (101, 5, 3)
    assert second.as_json()["resumed"] == {"cand/7": 3}
    with corpus.connect(db) as conn:
        found = corpus.latest_snapshot(conn, "cand/7")
    assert found is not None and found[0] == following_day
    stored = found[1]["docket_entries"]
    ids_stored = [e["id"] for e in stored]
    assert ids_stored == sorted(ids_stored, reverse=True) and len(set(ids_stored)) == 101
    assert ids_stored[0] == 900
    assert next(e for e in stored if e["id"] == 500)["description"] == "amended"
    # Every entry a whole read made in one go would hold is there.
    assert {e["id"] for page in range(1, 6) for e in upstream.entries(page)} <= set(ids_stored)
    # The kept pages are emptied, and an emptied object is nothing to go on from.
    emptied = json.loads(store.objects[_PARTIAL_KEY])
    assert "entries" not in emptied and emptied["cleared"] == following_day.isoformat()


def test_a_resumed_onboard_that_stops_again_keeps_every_page_so_far(
    tmp_path: Path, store: casestore.InMemoryObjectTransport
) -> None:
    db = _db(tmp_path)
    upstream = PagedUpstream(7, pages=6)
    upstream.slow = {3}
    _onboard(upstream, db, TODAY)
    upstream.slow = {5}
    again = _onboard(upstream, db, TODAY + timedelta(days=1))
    kept = json.loads(store.objects[_PARTIAL_KEY])
    # Still dated from the first attempt: the closing read reaches back to it.
    assert (kept["pages"], kept["cursor"], kept["started"]) == (4, "5", TODAY.isoformat())
    assert f"[kept 4 page(s) of entries, read since {TODAY}," in again.failed["cand/7"]
    assert "[last request: page 5 of the entries, cursor 5;" in again.failed["cand/7"]
    upstream.slow = set()
    last = _onboard(upstream, db, TODAY + timedelta(days=2))
    assert [(r.entries, r.resumed_pages) for r in last.refreshed] == [(120, 4)]


def test_a_resumed_onboard_is_sized_at_the_pages_still_owed(
    tmp_path: Path, store: casestore.InMemoryObjectTransport
) -> None:
    db = _db(tmp_path)
    upstream = PagedUpstream(7, pages=6)
    upstream.slow = {5}
    _onboard(upstream, db, TODAY)
    upstream.slow = set()
    planned = _planned(7, ReadMode.onboard)
    # Six pages counted and four kept: two owed, the count's slack page, the
    # closing read and the docket. A share one short of that does not start.
    with upstream.client() as client, pytest.raises(OnboardDoesNotFit):
        refresh_docket(
            client, db, planned, max_entry_pages=150, today=TODAY, share_left=5, resume=_RESUME
        )
    with upstream.client() as client:
        done = refresh_docket(
            client, db, planned, max_entry_pages=150, today=TODAY, share_left=6, resume=_RESUME
        )
    assert (done.entries, done.requests) == (120, 5)


def test_kept_pages_past_their_age_or_for_another_docket_are_not_used(
    tmp_path: Path, store: casestore.InMemoryObjectTransport
) -> None:
    db = _db(tmp_path)
    upstream = PagedUpstream(7, pages=3)
    upstream.slow = {3}
    _onboard(upstream, db, TODAY)
    upstream.slow = set()
    upstream.asked.clear()
    late = _onboard(upstream, db, TODAY + timedelta(days=15))
    assert upstream.asked == ["count", "docket", "page 1", "page 2", "page 3"]
    assert [(r.entries, r.resumed_pages) for r in late.refreshed] == [(60, 0)]

    for unusable in (
        {"kind": "onboard-partial", "version": 1, "docket_id": 8, "pages": 1, "cursor": "2"},
        {"kind": "onboard-partial", "version": 2, "docket_id": 7, "pages": 1, "cursor": "2"},
        {"kind": "onboard-partial", "version": 1, "docket_id": 7, "pages": 0, "cursor": "2"},
        {"kind": "onboard-partial", "version": 1, "docket_id": 7, "pages": 1, "cursor": ""},
        {"id": 7, "docket_entries": []},
    ):
        other = tmp_path / str(len(str(unusable)))
        casestore.write_onboard_partial(
            store, "cand/7", {"started": TODAY.isoformat(), "entries": [], **unusable}
        )
        upstream.asked.clear()
        whole = _onboard(upstream, _db(other), TODAY)
        assert upstream.asked == ["count", "docket", "page 1", "page 2", "page 3"], unusable
        assert whole.refreshed[0].resumed_pages == 0
    store.objects[_PARTIAL_KEY] = b"not json"
    assert _onboard(upstream, _db(tmp_path / "raw"), TODAY).refreshed[0].entries == 60


def test_kept_pages_whose_cursor_upstream_refuses_are_dropped(
    tmp_path: Path, store: casestore.InMemoryObjectTransport
) -> None:
    db = _db(tmp_path)
    upstream = PagedUpstream(7, pages=3)
    upstream.slow = {3}
    _onboard(upstream, db, TODAY)
    upstream.slow, upstream.refuse_cursor = set(), True
    refused = _onboard(upstream, db, TODAY + timedelta(days=1))
    assert refused.refreshed == []
    assert refused.failed["cand/7"].endswith(
        "[the kept pages' cursor was refused; they are dropped]"
    )
    assert "entries" not in json.loads(store.objects[_PARTIAL_KEY])
    upstream.refuse_cursor = False
    upstream.asked.clear()
    whole = _onboard(upstream, db, TODAY + timedelta(days=2))
    assert upstream.asked == ["count", "docket", "page 1", "page 2", "page 3"]
    assert whole.refreshed[0].entries == 60


def test_a_closing_read_that_fails_keeps_the_whole_read_and_owes_only_itself(
    tmp_path: Path, store: casestore.InMemoryObjectTransport, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = _db(tmp_path)
    upstream = PagedUpstream(7, pages=3)
    upstream.slow = {2}
    _onboard(upstream, db, TODAY)
    upstream.slow = set()
    served = upstream.handle

    def closing_read_down(request: httpx.Request) -> httpx.Response:
        if "date_modified__gte" in dict(request.url.params):
            return httpx.Response(502)
        return served(request)

    monkeypatch.setattr(upstream, "handle", closing_read_down)
    failed = _onboard(upstream, db, TODAY + timedelta(days=1))
    assert failed.refreshed == []
    kept = json.loads(store.objects[_PARTIAL_KEY])
    assert (kept["pages"], kept["cursor"], len(kept["entries"])) == (3, None, 60)
    monkeypatch.setattr(upstream, "handle", served)
    upstream.asked.clear()
    done = _onboard(upstream, db, TODAY + timedelta(days=2))
    assert upstream.asked == ["count", "docket", f"since {TODAY - timedelta(2)}"]
    assert [(r.entries, r.resumed_pages) for r in done.refreshed] == [(60, 3)]


def test_a_malformed_entry_is_never_kept(
    tmp_path: Path, store: casestore.InMemoryObjectTransport, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = _db(tmp_path)
    upstream = PagedUpstream(7, pages=3)
    monkeypatch.setattr(
        upstream,
        "entries",
        lambda page: [{"description": "no id"}] if page == 2 else [{"id": page}],
    )
    report = _onboard(upstream, db, TODAY)
    assert report.failed["cand/7"].startswith("KeyError")
    kept = json.loads(store.objects[_PARTIAL_KEY])
    assert (kept["pages"], kept["cursor"], kept["entries"]) == (1, "2", [{"id": 1}])


def test_a_run_that_may_not_write_the_store_keeps_nothing_and_reads_whole(tmp_path: Path) -> None:
    """No content store: the read fails as it did, and leaves nothing behind."""
    db = _db(tmp_path)
    upstream = PagedUpstream(7, pages=3)
    upstream.slow = {3}
    get: Any = CourtListenerClient._get
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(get.retry, "sleep", lambda _seconds: None)
        report = _onboard(upstream, db, TODAY)
    assert "kept" not in report.failed["cand/7"]
    assert casestore.active_transport() is None


def test_a_refresh_names_each_request_it_sends(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient({1: [{"id": 1}]}, changed={1: []}, pages=2)
    steps: list[str] = []
    refresh_docket(
        _client(fake),
        db,
        _planned(1, ReadMode.onboard),
        max_entry_pages=150,
        today=TODAY,
        on_step=steps.append,
    )
    assert steps == [
        "the entry count",
        "the docket",
        "page 1 of the entries",
        "page 2 of the entries",
    ]
    steps.clear()
    since = TODAY - timedelta(days=3)
    refresh_docket(
        _client(fake),
        db,
        PlannedRefresh("cand", 1, ReadMode.incremental, TODAY, since),
        max_entry_pages=150,
        today=TODAY,
        on_step=steps.append,
    )
    assert steps == [
        "the docket",
        f"page 1 of the entries changed since {since}",
        f"page 2 of the entries changed since {since}",
    ]


def test_a_malformed_entry_fails_its_docket_only(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient({1: [{"description": "no id"}], 2: [{"id": 2}]})
    plan = [_planned(n, ReadMode.onboard) for n in (1, 2)]
    report = refresh_watchlist(_client(fake), db, plan, max_entry_pages=150, today=TODAY, share=160)
    assert list(report.failed) == ["cand/1"] and report.failed["cand/1"].startswith("KeyError")
    # Raised after the page answered: the reason places it by the last request, no cursor.
    assert "[last request: page 1 of the entries; 0s since" in report.failed["cand/1"]
    assert [r.case_id for r in report.refreshed] == ["cand/2"]


def test_dry_run_plans_every_listed_docket_and_reads_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_client(_lane: str, **_waits: float) -> None:
        raise AssertionError("a dry run must not build a CourtListener client")

    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setattr("fedcourtsai.cli._client", no_client)
    with corpus.connect(_db(tmp_path)):
        pass

    result = CliRunner().invoke(app, ["watchlist-refresh", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "cand/71450167\tonboard" in result.output
    assert "nothing read" in result.output


def test_the_command_records_a_day_of_significant_new_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    today = datetime.now(UTC).date()
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    first = ListedClient(
        {71450167: [{"id": 1, "date_filed": "2025-09-24", "description": "COMPLAINT"}]}
    )
    monkeypatch.setattr("fedcourtsai.cli._client", lambda _lane, **_waits: nullcontext(first))
    # An onboard starts only when the share left covers the page cap, so the
    # listed dockets onboard over several runs.
    for _ in range(len(_LISTED_COURTS)):
        onboard = CliRunner().invoke(app, ["watchlist-refresh"])
        assert onboard.exit_code == 0, onboard.output
        if any(docket_id == 71450167 for docket_id, _, _ in first.reads):
            break
    else:
        pytest.fail("the docket never onboarded")
    # Onboarding records nothing: a whole docket is history, not news.
    assert not activity_path(tmp_path / "data", today).exists()

    judgment = {
        "id": 9,
        "entry_number": 40,
        "date_filed": today.isoformat(),
        "description": "JUDGMENT.",
    }
    second = ListedClient(
        {71450167: [judgment, *first.entries[71450167]]}, changed={71450167: [judgment]}
    )
    monkeypatch.setattr("fedcourtsai.cli._client", lambda _lane, **_waits: nullcontext(second))
    refreshed = CliRunner().invoke(app, ["watchlist-refresh"])
    assert refreshed.exit_code == 0, refreshed.output
    record = read_model(activity_path(tmp_path / "data", today), AiCaseActivity)
    assert [(e.case, e.category, e.entry_id, e.kind) for e in record.entries] == [
        ("X.AI v. OpenAI", "competitor", 9, "judgment")
    ]


def test_one_onboard_leads_the_plan_rotating_by_day(tmp_path: Path) -> None:
    db = _db(tmp_path)
    inc = next(d for d in range(1, 20) if not full_read_due(d, TODAY, 7))
    _stamp(db, inc, TODAY - timedelta(days=1))
    with corpus.connect(db) as conn:
        plan = plan_refresh(
            conn,
            [("cand", 98), ("cand", inc), ("cand", 97)],
            today=TODAY,
            overlap_days=2,
            full_read_every_days=7,
        )
    # The two pending onboards take the lead on alternate days.
    lead = (97, 98)[TODAY.toordinal() % 2]
    other = 98 if lead == 97 else 97
    assert [(p.docket_id, p.mode) for p in plan] == [
        (lead, ReadMode.onboard),
        (inc, ReadMode.incremental),
        (other, ReadMode.onboard),
    ]
    with corpus.connect(db) as conn:
        tomorrow = plan_refresh(
            conn,
            [("cand", 98), ("cand", inc), ("cand", 97)],
            today=TODAY + timedelta(days=1),
            overlap_days=2,
            full_read_every_days=7,
        )
    assert tomorrow[0].docket_id != lead


def test_an_onboard_the_share_left_cannot_cover_is_deferred_unread(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient({1: [{"id": n} for n in range(1, 42)]})  # 41 entries: three pages
    with pytest.raises(OnboardDoesNotFit) as caught:
        refresh_docket(
            _client(fake),
            db,
            _planned(1, ReadMode.onboard),
            max_entry_pages=150,
            today=TODAY,
            share_left=5,  # the count, then one short of the docket and four pages
        )
    assert caught.value.requests == 1  # the count; no docket, no entries
    assert fake.reads == []
    done = refresh_docket(
        _client(fake),
        db,
        _planned(1, ReadMode.onboard),
        max_entry_pages=150,
        today=TODAY,
        share_left=6,
    )
    assert done.mode is ReadMode.onboard


def test_an_onboard_too_short_for_any_read_is_deferred_without_a_count(tmp_path: Path) -> None:
    fake = FakeClient({1: [{"id": 1}]})
    with pytest.raises(OnboardDoesNotFit) as caught:
        refresh_docket(
            _client(fake),
            _db(tmp_path),
            _planned(1, ReadMode.onboard),
            max_entry_pages=150,
            today=TODAY,
            share_left=3,  # the count and the docket, then one short of two pages
        )
    assert caught.value.requests == 0
    assert fake.counted == []


def test_an_onboard_without_a_count_is_sized_at_the_page_cap(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient({1: [{"id": 1}]}, counts={1: None})
    with pytest.raises(OnboardDoesNotFit) as caught:
        refresh_docket(
            _client(fake),
            db,
            _planned(1, ReadMode.onboard),
            max_entry_pages=150,
            today=TODAY,
            share_left=151,  # the count, then one short of the docket and 150 pages
        )
    assert caught.value.requests == 1
    assert fake.reads == []
    done = refresh_docket(
        _client(fake),
        db,
        _planned(1, ReadMode.onboard),
        max_entry_pages=150,
        today=TODAY,
        share_left=152,
    )
    assert done.mode is ReadMode.onboard


def test_an_onboard_counted_past_the_page_cap_fails_on_the_count(tmp_path: Path) -> None:
    fake = FakeClient({1: [{"id": 1}]}, counts={1: 3001})  # 151 pages of twenty
    with pytest.raises(EntryPageCapExceeded, match="counts 3001 entries"):
        refresh_docket(
            _client(fake),
            _db(tmp_path),
            _planned(1, ReadMode.onboard),
            max_entry_pages=150,
            today=TODAY,
            share_left=160,
        )
    assert fake.counted == [1]
    assert fake.reads == []


def test_an_incremental_plan_without_a_snapshot_is_deferred_when_short(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _stamp(db, 3, TODAY - timedelta(days=1))  # a row, but no snapshot
    fake = FakeClient({3: [{"id": n} for n in range(1, 42)]})  # three pages
    with pytest.raises(OnboardDoesNotFit) as caught:
        refresh_docket(
            _client(fake),
            db,
            _planned(3, ReadMode.incremental, TODAY - timedelta(days=3)),
            max_entry_pages=150,
            today=TODAY,
            share_left=5,  # the docket and the count, then one short of four pages
        )
    assert caught.value.requests == 2  # the docket and its count; no entries
    assert fake.reads == []
    done = refresh_docket(
        _client(fake),
        db,
        _planned(3, ReadMode.incremental, TODAY - timedelta(days=3)),
        max_entry_pages=150,
        today=TODAY,
        share_left=6,
    )
    assert done.mode is ReadMode.onboard
    assert fake.reads == [(3, "whole", None)]


def test_a_run_defers_an_onboard_that_does_not_fit_and_goes_on(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _onboarded(db, 7, 1)
    fake = FakeClient(
        {1: [{"id": 1}], 2: [{"id": 2}], 3: [{"id": 3}]},
        changed={7: [{"id": 2}]},
        counts={2: 2000},  # a hundred pages
    )
    plan = [
        _planned(1, ReadMode.onboard),
        _planned(7, ReadMode.incremental, TODAY - timedelta(days=3)),
        _planned(2, ReadMode.onboard),
        _planned(3, ReadMode.onboard),
    ]
    report = refresh_watchlist(_client(fake), db, plan, max_entry_pages=150, today=TODAY, share=60)
    # The first onboard spends three and the incremental read two, leaving 55:
    # docket 2's count puts it at 102 and it waits for a later run, after which
    # docket 3's one page still fits and lands the same run.
    assert [r.case_id for r in report.refreshed] == ["cand/1", "cand/7", "cand/3"]
    assert report.deferred == ["cand/2"]
    assert report.stop_reason is None
    assert (7, "since", TODAY - timedelta(days=3)) in fake.reads
    assert (2, "whole", None) not in fake.reads


def test_a_failed_read_still_counts_against_the_share(tmp_path: Path) -> None:
    db = _db(tmp_path)
    _onboarded(db, 7, 60)  # four requests for a full read
    fake = FakeClient(
        {1: [{"id": 1}], 7: [{"id": n} for n in range(1, 61)]},
        incomplete=frozenset({1}),
    )
    plan = [
        _planned(1, ReadMode.onboard),
        _planned(7, ReadMode.full, TODAY - timedelta(days=3)),
    ]
    report = refresh_watchlist(_client(fake), db, plan, max_entry_pages=1, today=TODAY, share=5)
    # The failed onboard sent three requests (its count, the docket and a
    # page), leaving two: under docket 7's four, so its full read falls back
    # to an incremental one.
    assert set(report.failed) == {"cand/1"}
    assert [r.mode for r in report.refreshed] == [ReadMode.incremental]


def test_a_stop_keeps_the_onboards_deferred_before_it(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient({1: [{"id": 1}]}, over_budget=frozenset({3}))
    plan = [
        _planned(1, ReadMode.onboard),
        _planned(2, ReadMode.onboard),
        _planned(3, ReadMode.incremental, TODAY - timedelta(days=3)),
    ]
    report = refresh_watchlist(_client(fake), db, plan, max_entry_pages=1, today=TODAY, share=3)
    # Docket 1 spends three, so 2 cannot fit; 3 then finds the share spent, and
    # the stop adds it to the deferral rather than replacing the list.
    assert [r.case_id for r in report.refreshed] == ["cand/1"]
    assert report.deferred == ["cand/2", "cand/3"]


@pytest.mark.parametrize(("share_left", "fits"), [(151, False), (152, True)])
def test_an_onboard_counted_at_the_page_cap_is_sized_at_the_cap(
    tmp_path: Path, share_left: int, fits: bool
) -> None:
    fake = FakeClient({1: [{"id": 1}]}, counts={1: 3000})  # exactly 150 pages
    planned = _planned(1, ReadMode.onboard)
    if fits:
        done = refresh_docket(
            _client(fake),
            _db(tmp_path),
            planned,
            max_entry_pages=150,
            today=TODAY,
            share_left=share_left,
        )
        assert done.mode is ReadMode.onboard
    else:
        with pytest.raises(OnboardDoesNotFit):
            refresh_docket(
                _client(fake),
                _db(tmp_path),
                planned,
                max_entry_pages=150,
                today=TODAY,
                share_left=share_left,
            )
        assert fake.reads == []


def test_a_share_spent_on_the_count_stops_the_run(tmp_path: Path) -> None:
    fake = FakeClient({1: [{"id": 1}], 2: [{"id": 2}]}, over_budget=frozenset({1}))
    plan = [_planned(1, ReadMode.onboard), _planned(2, ReadMode.onboard)]
    report = refresh_watchlist(
        _client(fake), _db(tmp_path), plan, max_entry_pages=150, today=TODAY, share=160
    )
    assert report.refreshed == []
    assert report.deferred == ["cand/1", "cand/2"]
    assert report.stop_reason == "lane share spent"
    assert fake.reads == []
