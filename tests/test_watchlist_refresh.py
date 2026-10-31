from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path
from typing import Any, cast

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.courtlistener import (
    CourtListenerClient,
    EntryPageCapExceeded,
    EntryPages,
    RateBudgetExceeded,
)
from fedcourtsai.pipeline.ingest import from_api_docket, upsert_to_corpus
from fedcourtsai.pipeline.watchlist_refresh import (
    PlannedRefresh,
    ReadMode,
    full_read_due,
    merge_entries,
    plan_refresh,
    refresh_docket,
    refresh_watchlist,
    refreshed_on,
)

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
    ) -> None:
        self.entries = entries
        self.changed = changed or {}
        self.incomplete = incomplete
        self.over_budget = over_budget
        self.broken = broken
        self.pages = pages
        self.reads: list[tuple[int, str, date | None]] = []

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


def test_plan_puts_incremental_reads_first_then_onboards_then_full_reads(
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
        (old, ReadMode.incremental),
        (recent, ReadMode.incremental),
        (99, ReadMode.onboard),
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
        {"case_id": "cand/4", "mode": "onboard", "changed": True, "entries": 1, "requests": 2}
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
    ticks = iter([0.0, 5.0, 11.0])
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
        clock=lambda: next(ticks),
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


def test_a_malformed_entry_fails_its_docket_only(tmp_path: Path) -> None:
    db = _db(tmp_path)
    fake = FakeClient({1: [{"description": "no id"}], 2: [{"id": 2}]})
    plan = [_planned(n, ReadMode.onboard) for n in (1, 2)]
    report = refresh_watchlist(_client(fake), db, plan, max_entry_pages=150, today=TODAY, share=160)
    assert list(report.failed) == ["cand/1"] and report.failed["cand/1"].startswith("KeyError")
    assert [r.case_id for r in report.refreshed] == ["cand/2"]


def test_dry_run_plans_every_listed_docket_and_reads_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_client(_lane: str) -> None:
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
