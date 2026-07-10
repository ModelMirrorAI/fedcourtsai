from datetime import date
from pathlib import Path
from typing import Any, cast

import httpx

from fedcourtsai import corpus
from fedcourtsai.courtlistener import CourtListenerClient, RateBudgetExceeded
from fedcourtsai.pipeline.discover import discover_cases


def _docket(docket_id: int, court_url: str, date_filed: str, **kw: Any) -> dict[str, Any]:
    return {
        "id": docket_id,
        "court": f"https://www.courtlistener.com/api/rest/v4/courts/{court_url}/",
        "date_filed": date_filed,
        **kw,
    }


class FakeSearch:
    """Stand-in for the client's discovery API, recording how it was queried."""

    def __init__(self, by_court: dict[str, list[dict[str, Any]]]) -> None:
        self._by_court = by_court
        self.calls: list[tuple[str, date, int]] = []

    def iter_dockets(
        self, court: str, date_filed_gte: date, *, max_results: int
    ) -> list[dict[str, Any]]:
        self.calls.append((court, date_filed_gte, max_results))
        hits = [
            d
            for d in self._by_court.get(court, [])
            if date.fromisoformat(d["date_filed"]) >= date_filed_gte
        ]
        return hits[:max_results]


def _discover(client: FakeSearch, tmp_path: Path, **kw: Any) -> Any:
    return discover_cases(
        cast(CourtListenerClient, client),
        corpus.corpus_db_path(tmp_path / "corpus"),
        kw.pop("courts", ["ca9"]),
        max_new=kw.pop("max_new", 10),
        default_since=kw.pop("default_since", date(2026, 6, 1)),
    )


def test_discovery_onboards_docket_and_event(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": [_docket(101, "ca9", "2026-06-10", case_name="Doe v. Roe")]})
    result = _discover(client, tmp_path)

    assert result.total == 1
    assert result.case_ids == ["ca9/101"]
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "ca9/101")
        events = corpus.events_for_case(conn, "ca9/101")
    assert row is not None and row.court == "ca9"
    # The predictable event is recorded as a corpus row, not a git event.yaml.
    assert len(events) == 1
    assert events[0].event_id == "evt-appeal-disposition"
    assert events[0].title == "Doe v. Roe"
    assert events[0].opened_at == date(2026, 6, 10)


def test_scotus_event_is_a_petition(tmp_path: Path) -> None:
    client = FakeSearch({"scotus": [_docket(7, "scotus", "2026-06-05")]})
    _discover(client, tmp_path, courts=["scotus"])
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        events = corpus.events_for_case(conn, "scotus/7")
    assert events[0].event_id == "evt-petition-disposition"


def test_watermark_advances_to_newest_filed(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": [_docket(1, "ca9", "2026-06-03"), _docket(2, "ca9", "2026-06-09")]})
    result = _discover(client, tmp_path)
    assert result.courts[0].watermark == date(2026, 6, 9)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 9)


def test_second_run_resumes_from_watermark(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": [_docket(1, "ca9", "2026-06-03"), _docket(2, "ca9", "2026-06-09")]})
    _discover(client, tmp_path)
    # Add a newer filing and re-run: the query must start at the stored watermark.
    client._by_court["ca9"].append(_docket(3, "ca9", "2026-06-12"))
    result = _discover(client, tmp_path)
    # Second call queried from the stored watermark, not default_since.
    assert client.calls[-1][1] == date(2026, 6, 9)
    assert "ca9/3" in result.case_ids


def test_budget_cap_limits_total_across_courts(tmp_path: Path) -> None:
    client = FakeSearch(
        {
            "ca9": [_docket(1, "ca9", "2026-06-02"), _docket(2, "ca9", "2026-06-03")],
            "ca1": [_docket(3, "ca1", "2026-06-04")],
        }
    )
    result = _discover(client, tmp_path, courts=["ca9", "ca1"], max_new=2)
    assert result.total == 2  # ca9 fills the budget; ca1 is not reached
    assert [c.court for c in result.courts] == ["ca9"]


def test_zero_budget_is_noop(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": [_docket(1, "ca9", "2026-06-02")]})
    result = _discover(client, tmp_path, max_new=0)
    assert result.total == 0
    assert client.calls == []


def test_court_with_no_new_filings_records_searched_frontier(tmp_path: Path) -> None:
    client = FakeSearch({"ca9": []})
    result = _discover(client, tmp_path)
    assert result.total == 0
    assert result.courts == []  # nothing onboarded, so no per-court line
    # A court that finds nothing still records the date it searched from, so the
    # next run resumes there instead of resetting to default_since.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 1)


class FlakySearch(FakeSearch):
    """A FakeSearch that raises a transient REST error for chosen courts."""

    def __init__(self, by_court: dict[str, list[dict[str, Any]]], fail: set[str]) -> None:
        super().__init__(by_court)
        self._fail = fail

    def iter_dockets(
        self, court: str, date_filed_gte: date, *, max_results: int
    ) -> list[dict[str, Any]]:
        if court in self._fail:
            self.calls.append((court, date_filed_gte, max_results))
            raise httpx.ReadTimeout("The read operation timed out")
        return super().iter_dockets(court, date_filed_gte, max_results=max_results)


def test_one_court_rest_failure_does_not_abort_discovery(tmp_path: Path) -> None:
    # ca9 times out; ca1 must still be discovered (a slow court can't nuke the run).
    client = FlakySearch(
        {
            "ca9": [_docket(1, "ca9", "2026-06-03")],
            "ca1": [_docket(2, "ca1", "2026-06-04")],
        },
        fail={"ca9"},
    )
    result = _discover(client, tmp_path, courts=["ca9", "ca1"])

    assert result.case_ids == ["ca1/2"]
    assert [f["court"] for f in result.failed] == ["ca9"]
    assert "ReadTimeout" in str(result.failed[0]["reason"])
    # The failed court's watermark is left untouched so the next run retries its
    # range gap-free, rather than recording a frontier it never actually searched.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") is None
        assert corpus.get_discovery_watermark(conn, "ca1") == date(2026, 6, 4)


def test_empty_run_does_not_reset_watermark_to_default(tmp_path: Path) -> None:
    # First run onboards a docket (watermark -> 2026-06-09).
    client = FakeSearch({"ca9": [_docket(1, "ca9", "2026-06-09")]})
    _discover(client, tmp_path)
    # Second run finds nothing, even with an *earlier* default_since: it must
    # resume from the stored watermark, never rewind to default_since.
    client._by_court["ca9"] = []
    _discover(client, tmp_path, default_since=date(2026, 6, 1))
    assert client.calls[-1][1] == date(2026, 6, 9)
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 9)


def test_discovery_stops_at_the_deadline_between_courts(tmp_path: Path) -> None:
    # Past the deadline the court walk stops; unvisited courts keep their
    # watermarks so the next run resumes gap-free.
    client = FakeSearch(
        {
            "ca9": [_docket(1, "ca9", "2026-06-03")],
            "ca1": [_docket(2, "ca1", "2026-06-04")],
        }
    )
    clock = iter([0.0, 100.0])  # ca9 starts pre-deadline; ca1 is past it
    result = discover_cases(
        cast(CourtListenerClient, client),
        corpus.corpus_db_path(tmp_path / "corpus"),
        ["ca9", "ca1"],
        max_new=10,
        default_since=date(2026, 6, 1),
        deadline=50.0,
        time_fn=lambda: next(clock),
    )

    assert result.case_ids == ["ca9/1"]
    assert result.stopped == "run deadline reached"
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 6, 3)
        assert corpus.get_discovery_watermark(conn, "ca1") is None


def test_discovery_stops_when_the_api_budget_is_exhausted(tmp_path: Path) -> None:
    # RateBudgetExceeded means every later court would hit the same wall this
    # window: stop the walk at once, leaving watermarks for a gap-free retry.
    class BudgetSearch:
        def iter_dockets(
            self, court: str, date_filed_gte: date, *, max_results: int
        ) -> list[dict[str, Any]]:
            raise RateBudgetExceeded("next request must wait 3000s, over the 300s bound")

    result = discover_cases(
        cast(CourtListenerClient, BudgetSearch()),
        corpus.corpus_db_path(tmp_path / "corpus"),
        ["ca9", "ca1"],
        max_new=10,
        default_since=date(2026, 6, 1),
    )

    assert result.total == 0
    assert result.stopped is not None
    assert result.stopped.startswith("API budget exhausted")
    assert result.failed == []


def test_scotus_discovery_enriches_a_live_first_row(tmp_path: Path) -> None:
    # The CourtListener half of the live channel's identity scheme (#472): a
    # petition the live poller saw first keys on its reserved-range live id
    # forever. CL discovery of the same docket number must enrich that row —
    # and define its events under it — not mint a duplicate under the CL id.
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [corpus.CorpusRow(case_id="scotus/9025000007", court="scotus", docket_number="25-7")],
        )
    client = FakeSearch(
        {
            "scotus": [
                _docket(
                    74112233,
                    "scotus",
                    "2026-06-10",
                    docket_number="25-7",
                    case_name="Doe v. Roe",
                )
            ]
        }
    )
    result = _discover(client, tmp_path, courts=["scotus"])
    assert result.case_ids == ["scotus/9025000007"]
    with corpus.connect(db) as conn:
        assert corpus.get_row(conn, "scotus/74112233") is None
        enriched = corpus.get_row(conn, "scotus/9025000007")
        events = corpus.events_for_case(conn, "scotus/9025000007")
    assert enriched is not None and enriched.case_name == "Doe v. Roe"
    assert [e.event_id for e in events] == ["evt-petition-disposition"]
