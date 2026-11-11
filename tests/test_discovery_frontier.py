"""The discovery frontier check: the probes it stores and the thresholds it reads back."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, supremecourt
from fedcourtsai.cli import app
from fedcourtsai.config import FrontierCheckConfig, LiveConfig
from fedcourtsai.pipeline import discovery_frontier as df
from fedcourtsai.pipeline import live, order_lineups
from fedcourtsai.schemas import LiveFrontier
from fedcourtsai.serialize import read_model
from fedcourtsai.supremecourt import SupremeCourtClient

TODAY = date(2026, 11, 11)  # a Wednesday
CONFIG = FrontierCheckConfig(enabled=True, lookahead=6, hole_reprobes_per_stream=2)

ORDER_TEXT = (
    "(ORDER LIST:  610 U.S.) \n"
    + "THURSDAY, NOVEMBER 5, 2026 \n"
    + "CERTIORARI DENIED \n"
    + "26-5007 DOE, JANE V. ROE, WARDEN, ET AL. \n"
    + "(26A9) \n"
    + "The application for stay presented to Justice Thomas and by him \n"
    + "referred to the Court is denied.  The petition for a writ of \n"
    + "certiorari is denied. "
)


def _client(served: set[str], *, failing: set[str] | None = None) -> SupremeCourtClient:
    """A Court client that serves the named docket JSONs and 404s every other one."""

    def handler(request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        if failing and name in failing:
            return httpx.Response(500)
        if name in served:
            return httpx.Response(200, json={"CaseNumber": name})
        return httpx.Response(404)

    inner = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
    )
    return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _seconds: None)


def _seed(db: Path, numbers: Mapping[str, str | None], cursors: Mapping[str, int]) -> None:
    """Corpus rows by docket number (with a filing date) and the Term-26 cursors."""
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=f"scotus/{9_000_000 + index}",
                    court="scotus",
                    docket_number=number,
                    date_filed=date.fromisoformat(filed) if filed else None,
                )
                for index, (number, filed) in enumerate(numbers.items())
            ],
        )
        for stream, serial in cursors.items():
            corpus.set_live_cursor(conn, 26, stream, serial)
            corpus.set_live_frontier(conn, 26, stream, serial)


@pytest.fixture
def no_lists(monkeypatch: pytest.MonkeyPatch) -> df.OutsideFrontier:
    """Replace the Court's lists with an outside frontier the test fills in."""
    outside = df.OutsideFrontier()
    monkeypatch.setattr(df, "read_outside_frontier", lambda *_args, **_kwargs: outside)
    return outside


# --- pure pieces ------------------------------------------------------------------


def test_the_streams_are_the_ones_discovery_walks() -> None:
    assert df.STREAMS == live.STREAMS


def test_stream_serial_sorts_a_number_into_its_stream() -> None:
    assert df.stream_serial("26-618") == (26, "paid", 618)
    assert df.stream_serial("No. 26-6135") == (26, "ifp", 6135)
    assert df.stream_serial("26-5001") == (26, "ifp", 5001)
    assert df.stream_serial("26a669 ") == (26, "application", 669)
    assert df.stream_serial("26M30") is None
    assert df.stream_serial("159, Orig.") is None


def test_holes_are_the_unheld_serials_up_to_the_cursor() -> None:
    assert df.stream_holes([1, 2, 4, 9], 1, 6) == [3, 5, 6]
    assert df.stream_holes([5001, 5003], 5001, 5003) == [5002]
    assert df.stream_holes([1, 2], 1, None) == []


def test_the_hole_sample_rotates_through_every_hole() -> None:
    holes = list(range(100, 107))
    seen: set[int] = set()
    for offset in range(4):
        sample = df.hole_sample(holes, 3, date(2026, 11, 11 + offset))
        assert len(sample) == 3
        seen.update(sample)
    assert seen == set(holes)
    assert df.hole_sample(holes, 10, TODAY) == holes
    assert df.hole_sample(holes, 0, TODAY) == []


def test_a_served_number_is_unreachable_only_past_the_unserved_run() -> None:
    probed = list(range(11, 21))
    # 11 serves: ordinary new intake the next cycle onboards, and the walk goes on.
    assert df.unreachable_hits(10, probed, [11], 2) == []
    # One unserved number is inside the tolerance; 13 is reached.
    assert df.unreachable_hits(10, probed, [11, 13], 2) == []
    # Two unserved numbers stop the walk, so everything served after them is pinned.
    assert df.unreachable_hits(10, probed, [13, 14], 2) == [13, 14]
    assert df.unreachable_hits(10, probed, [11, 14, 18], 2) == [14, 18]
    assert df.unreachable_hits(10, probed, [], 2) == []


def test_quiet_business_days_skip_weekends_and_today() -> None:
    assert df.quiet_business_days(date(2026, 11, 10), TODAY) == 0
    assert df.quiet_business_days(date(2026, 11, 6), TODAY) == 2  # Mon 9th, Tue 10th
    assert df.quiet_business_days(date(2026, 11, 5), TODAY) == 3
    assert df.quiet_business_days(TODAY, TODAY) == 0


def test_the_stall_threshold_relaxes_for_ifp_and_in_the_recess() -> None:
    config = FrontierCheckConfig()
    assert df.stall_threshold("paid", TODAY, config) == 3
    assert df.stall_threshold("application", TODAY, config) == 3
    assert df.stall_threshold("ifp", TODAY, config) == 7
    assert df.stall_threshold("paid", date(2026, 8, 3), config) == 10
    assert df.stall_threshold("ifp", date(2026, 9, 30), config) == 10


# --- the network half -------------------------------------------------------------


def test_the_check_is_off_by_default_and_spends_nothing(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(db, {"26-1": "2026-11-10"}, {"paid": 1})
    assert LiveConfig().frontier_check.enabled is False
    with _client(set()) as client:
        ledger = df.run_frontier_check(
            client, db, 26, FrontierCheckConfig(), frontier_misses=2, today=TODAY
        )
    assert ledger == {}
    with corpus.connect(db) as conn:
        assert corpus.live_frontier_checks(conn, 26) == {}


def test_a_reading_stores_the_pinned_hit_the_serving_hole_and_the_outside_number(
    tmp_path: Path, no_lists: df.OutsideFrontier
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    # Paid holds 1, 2, 4, 6: holes 3 and 5. No IFP or application cursor.
    _seed(db, dict.fromkeys(["26-1", "26-2", "26-4", "26-6"], "2026-11-10"), {"paid": 6})
    no_lists.highest["paid"] = (9, "order-list 2026-11-09")
    no_lists.highest["application"] = (40, "miscellaneous-order 2026-11-05")
    # 26-3 now serves (a hole filled in); 26-10 serves past the unserved 26-7..26-9.
    with _client({"26-3", "26-10"}) as client:
        ledger = df.run_frontier_check(client, db, 26, CONFIG, frontier_misses=2, today=TODAY)
    assert ledger == {
        "due": 1,
        "checked": 1,
        "outside_ahead": 1,
        "lookahead_hits": 1,
        "holes_serving": 1,
        "deferred": 0,
        "unread": 0,
    }
    with corpus.connect(db) as conn:
        stored = corpus.live_frontier_checks(conn, 26)
    assert stored == {
        "paid": corpus.FrontierCheck(
            term=26,
            stream="paid",
            checked_on=TODAY,
            cursor_serial=6,
            outside_serial=9,
            outside_source="order-list 2026-11-09",
            lookahead_probed=6,
            lookahead_hits=(10,),
            holes_reprobed=2,
            holes_serving=(3,),
        )
    }


def test_a_reading_is_taken_once_a_day_and_carries_serving_holes_forward(
    tmp_path: Path, no_lists: df.OutsideFrontier
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(db, dict.fromkeys(["26-1", "26-4"], "2026-11-10"), {"paid": 4})
    config = CONFIG.model_copy(update={"hole_reprobes_per_stream": 1, "lookahead": 0})
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        name = request.url.path.rsplit("/", 1)[-1].removesuffix(".json")
        requests.append(name)
        return httpx.Response(200, json={"CaseNumber": name})

    def client() -> SupremeCourtClient:
        return SupremeCourtClient(
            throttle_seconds=1.0,
            client=httpx.Client(transport=httpx.MockTransport(handler)),
            sleep=lambda _seconds: None,
        )

    with client() as first:
        df.run_frontier_check(first, db, 26, config, frontier_misses=2, today=TODAY)
    assert len(requests) == 1
    # The same day again: nothing is due and nothing is requested.
    with client() as again:
        ledger = df.run_frontier_check(again, db, 26, config, frontier_misses=2, today=TODAY)
    assert ledger == {"due": 0}
    assert len(requests) == 1
    # The next day re-probes the other hole and keeps the first one's finding.
    with client() as later:
        df.run_frontier_check(later, db, 26, config, frontier_misses=2, today=date(2026, 11, 12))
    assert sorted(requests) == ["26-2", "26-3"]
    with corpus.connect(db) as conn:
        assert corpus.live_frontier_checks(conn, 26)["paid"].holes_serving == (2, 3)


def test_a_hole_that_stops_serving_is_dropped_and_a_cut_off_stream_stores_nothing(
    tmp_path: Path, no_lists: df.OutsideFrontier
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(db, dict.fromkeys(["26-1", "26-4"], "2026-11-10"), {"paid": 4})
    with corpus.connect(db) as conn:
        corpus.set_live_frontier_check(
            conn,
            corpus.FrontierCheck(
                term=26,
                stream="paid",
                checked_on=date(2026, 11, 10),
                cursor_serial=4,
                holes_serving=(2, 3),
            ),
        )
    config = CONFIG.model_copy(update={"lookahead": 0})
    # Today's re-probe of both holes finds only 26-3 serving.
    with _client({"26-3"}) as client:
        df.run_frontier_check(client, db, 26, config, frontier_misses=2, today=TODAY)
    with corpus.connect(db) as conn:
        assert corpus.live_frontier_checks(conn, 26)["paid"].holes_serving == (3,)

    # A client whose request deadline is spent raises through, and the day's
    # reading is not replaced by a partial one.
    inner = httpx.Client(transport=httpx.MockTransport(lambda _request: httpx.Response(404)))
    spent = SupremeCourtClient(
        throttle_seconds=1.0, client=inner, sleep=lambda _s: None, deadline_seconds=0.0
    )
    with spent, pytest.raises(supremecourt.DeadlineExceeded):
        df.run_frontier_check(spent, db, 26, config, frontier_misses=2, today=date(2026, 11, 12))
    with corpus.connect(db) as conn:
        assert corpus.live_frontier_checks(conn, 26)["paid"].checked_on == TODAY


def test_an_expired_budget_defers_the_reading_to_the_next_cycle(
    tmp_path: Path, no_lists: df.OutsideFrontier
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(db, {"26-1": "2026-11-10"}, {"paid": 1})
    with _client(set()) as client:
        ledger = df.run_frontier_check(
            client,
            db,
            26,
            CONFIG,
            frontier_misses=2,
            today=TODAY,
            deadline=0.0,
            time_fn=lambda: 5.0,
        )
    assert ledger == {"due": 1, "checked": 0, "deferred": 1}
    with corpus.connect(db) as conn:
        assert corpus.live_frontier_checks(conn, 26) == {}


def test_an_upstream_error_is_recorded_and_the_reading_still_lands(
    tmp_path: Path, no_lists: df.OutsideFrontier
) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(db, {"26-1": "2026-11-10"}, {"paid": 1})
    no_lists.problems.append("OT26 order listing not read: HTTPStatusError")
    with _client(set(), failing={"26-3"}) as client:
        df.run_frontier_check(client, db, 26, CONFIG, frontier_misses=2, today=TODAY)
    with corpus.connect(db) as conn:
        check = corpus.live_frontier_checks(conn, 26)["paid"]
    assert check.lookahead_probed == 1
    assert check.problems == (
        "OT26 order listing not read: HTTPStatusError",
        "look-ahead stopped at 26-3: HTTPStatusError",
    )


LISTING = (
    "<span>11/05/26</span> <span><a href='/orders/courtorders/110526zr1_test.pdf'>"
    + "Miscellaneous Order</a></span>"
)


class _FakeOrderFetcher:
    """An order fetcher whose every document reads as ``ORDER_TEXT``."""

    text: str | None = ORDER_TEXT

    def __init__(self, _client: SupremeCourtClient) -> None:
        pass

    def document(
        self, url: str, ref: order_lineups.OrderDocumentRef | None = None
    ) -> order_lineups.FetchedDocument:
        reason = None if self.text else "fetch failed: 403 for url 'https://x'\nsee @someone"
        return order_lineups.FetchedDocument(url, ref, self.text, reason=reason)


class _NoGrantedList:
    def __init__(self, _client: SupremeCourtClient) -> None:
        pass

    def opinion(self, _url: str) -> bytes | None:
        return None


def _listing_client(terms: set[int]) -> SupremeCourtClient:
    """A Court client serving the order listing for ``terms`` and nothing else."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path in {f"/orders/ordersofthecourt/{term}" for term in terms}:
            return httpx.Response(200, text=LISTING)
        return httpx.Response(404)

    inner = httpx.Client(
        transport=httpx.MockTransport(handler),
        headers={"User-Agent": supremecourt.BROWSER_USER_AGENT},
    )
    return SupremeCourtClient(throttle_seconds=1.0, client=inner, sleep=lambda _seconds: None)


@pytest.fixture
def fake_lists(monkeypatch: pytest.MonkeyPatch) -> type[_FakeOrderFetcher]:
    monkeypatch.setattr(_FakeOrderFetcher, "text", ORDER_TEXT)
    monkeypatch.setattr(order_lineups, "OrderFetcher", _FakeOrderFetcher)
    monkeypatch.setattr(df, "OpinionFetcher", _NoGrantedList)
    return _FakeOrderFetcher


def test_the_outside_frontier_is_the_highest_number_the_lists_name(
    fake_lists: type[_FakeOrderFetcher],
) -> None:
    with _listing_client({26}) as client:
        outside = df.read_outside_frontier(client, 26, today=TODAY, documents=5)
        unread = df.read_outside_frontier(client, 26, today=TODAY, documents=0)
    assert outside.highest == {
        "ifp": (5007, "miscellaneous-order 2026-11-05"),
        "application": (9, "miscellaneous-order 2026-11-05"),
    }
    assert outside.problems == []
    assert unread.highest == {}


def test_an_unread_listing_is_a_problem_not_a_frontier(
    fake_lists: type[_FakeOrderFetcher],
) -> None:
    with _listing_client({26}) as client:
        # In October the outgoing Term's listing is read too, and it is not served.
        outside = df.read_outside_frontier(client, 26, today=date(2026, 10, 6), documents=5)
    assert outside.problems == ["OT25 order listing not read: not served"]
    assert outside.highest["ifp"][0] == 5007


def test_an_unread_or_unparsed_document_is_recorded_without_upstream_text(
    fake_lists: type[_FakeOrderFetcher], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A problem line is published, so it carries the reason's head and a type name only."""
    monkeypatch.setattr(fake_lists, "text", None)
    with _listing_client({26}) as client:
        unread = df.read_outside_frontier(client, 26, today=TODAY, documents=5)
    assert unread.problems == ["miscellaneous-order 2026-11-05 not read: fetch failed"]

    def _raise(*_args: Any, **_kwargs: Any) -> Any:
        raise ValueError("a caption the grammar does not know\n@someone")

    monkeypatch.setattr(fake_lists, "text", ORDER_TEXT)
    monkeypatch.setattr(order_lineups, "read_documents", _raise)
    with _listing_client({26}) as client:
        unparsed = df.read_outside_frontier(client, 26, today=TODAY, documents=5)
    assert unparsed.problems == ["miscellaneous-order 2026-11-05 not parsed: ValueError"]
    assert unparsed.highest == {}


# --- the read-only half -----------------------------------------------------------


def _read(db: Path, *, today: date = TODAY, config: FrontierCheckConfig = CONFIG) -> Any:
    with corpus.connect(db) as conn:
        return df.read_discovery_frontier(conn, 26, today=today, config=config)


def _stream(discovery: Any, name: str) -> Any:
    return next(row for row in discovery.streams if row.stream == name)


def test_a_clean_corpus_reads_at_the_frontier(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(
        db,
        {"26-1": "2026-11-09", "26-2": "2026-11-10", "26-5001": "2026-11-10", "26A1": None},
        {"paid": 2, "ifp": 5001, "application": 1},
    )
    discovery = _read(db)
    assert discovery.ok is True
    paid = _stream(discovery, "paid")
    assert (paid.cursor, paid.frontier, paid.holes) == (2, 2, 0)
    assert (paid.newest_filed, paid.quiet_business_days) == (date(2026, 11, 10), 0)
    assert paid.checked_on is None
    # A stream whose newest rows carry no filing date has no movement reading.
    assert _stream(discovery, "application").quiet_business_days is None
    assert "never probed" in df.stream_line(26, paid)
    assert df.render_lines(discovery)[0] == "**Discovery frontier** (OT26): not yet probed"
    with corpus.connect(db) as conn:
        for stream, cursor in (("paid", 2), ("ifp", 5001), ("application", 1)):
            corpus.set_live_frontier_check(
                conn,
                corpus.FrontierCheck(
                    term=26, stream=stream, checked_on=TODAY, cursor_serial=cursor
                ),
            )
    assert df.render_lines(_read(db))[0] == "**Discovery frontier** (OT26): no alarm"


def test_each_threshold_raises_its_own_alarm(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    held = {f"26-{serial}": "2026-11-05" for serial in (1, 9, 10)}
    _seed(db, held, {"paid": 10})
    with corpus.connect(db) as conn:
        corpus.set_live_frontier_check(
            conn,
            corpus.FrontierCheck(
                term=26,
                stream="paid",
                checked_on=date(2026, 11, 7),
                cursor_serial=10,
                outside_serial=14,
                outside_source="order-list 2026-11-09",
                lookahead_probed=6,
                lookahead_hits=(13,),
                holes_reprobed=7,
                holes_serving=(2, 3, 4, 5, 6, 7),
            ),
        )
    discovery = _read(db)
    assert discovery.ok is False
    alarms = _stream(discovery, "paid").alarms
    assert alarms == [
        "order-list 2026-11-09 names 26-14, above the cursor at 26-10",
        "no docket newer than 2026-11-05 for 3 business day(s) (alarm at 3)",
        "26-13 served past an unserved run the sequential probe stops at",
        "6 skipped number(s) now serve and are not in the corpus (alarm over 5): "
        + "26-2, 26-3, 26-4, 26-5, 26-6, 26-7",
        "the frontier reading is from 2026-11-07, more than 3 day(s) old",
    ]
    body = df.render_alarm(discovery)
    assert "**Discovery frontier** (OT26): **behind**" in body
    assert all(alarm in body for alarm in alarms)


def test_an_alarm_clears_when_the_corpus_catches_up(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    _seed(db, {"26-1": "2026-11-10", "26-3": "2026-11-10"}, {"paid": 3})
    with corpus.connect(db) as conn:
        corpus.set_live_frontier_check(
            conn,
            corpus.FrontierCheck(
                term=26,
                stream="paid",
                checked_on=TODAY,
                cursor_serial=3,
                outside_serial=8,
                outside_source="order-list 2026-11-09",
                lookahead_hits=(6,),
                holes_serving=(2,),
            ),
        )
    config = CONFIG.model_copy(update={"hole_alarm_over": 0})
    assert len(_stream(_read(db, config=config), "paid").alarms) == 3
    # The cursor passes the outside number and the hit, and a row now holds 26-2.
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=f"scotus/{9_100_000 + serial}",
                    court="scotus",
                    docket_number=f"26-{serial}",
                    date_filed=date(2026, 11, 10),
                )
                for serial in (2, 4, 5, 6, 7, 8)
            ],
        )
        corpus.set_live_cursor(conn, 26, "paid", 8)
    discovery = _read(db, config=config)
    paid = _stream(discovery, "paid")
    assert discovery.ok is True
    assert (paid.lookahead_hits, paid.holes_serving, paid.alarms) == ([], [], [])


# --- the commands -----------------------------------------------------------------


def test_live_frontier_carries_the_verdict_only_when_the_check_is_on(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus_root = tmp_path / "corpus"
    _seed(corpus.corpus_db_path(corpus_root), {"26-1": "2026-11-10"}, {"paid": 1})
    config_root = tmp_path / "config"
    config_root.mkdir()
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config_root))
    out = tmp_path / "live-frontier.json"

    (config_root / "tracking.yaml").write_text("live: {}\n")
    result = CliRunner().invoke(app, ["live-frontier", "--out", str(out), "--today", "2026-11-11"])
    assert result.exit_code == 0, result.output
    assert read_model(out, LiveFrontier).discovery is None

    (config_root / "tracking.yaml").write_text("live:\n  frontier_check:\n    enabled: true\n")
    result = CliRunner().invoke(app, ["live-frontier", "--out", str(out), "--today", "2026-11-11"])
    assert result.exit_code == 0, result.output
    discovery = read_model(out, LiveFrontier).discovery
    assert discovery is not None
    assert (discovery.term, discovery.ok) == (26, True)
    assert "**Discovery frontier** (OT26): not yet probed" in result.output

    # A verdict that cannot be read costs only its own field, never the snapshot.
    def _raise(*_args: Any, **_kwargs: Any) -> Any:
        raise ValueError("bad stored\nreading")

    monkeypatch.setattr(df, "read_discovery_frontier", _raise)
    result = CliRunner().invoke(app, ["live-frontier", "--out", str(out), "--today", "2026-11-11"])
    assert result.exit_code == 0, result.output
    assert "::warning::discovery frontier: not read (ValueError: bad stored reading)" in (
        result.output
    )
    assert read_model(out, LiveFrontier).discovery is None
