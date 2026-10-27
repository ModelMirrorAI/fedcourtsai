"""The adverse-order scan: config checks, the RECAP search walk, its caps, and recall.

Every test is offline: the client's transport is an ``httpx.MockTransport``
answering from a table of canned search pages.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

import httpx
import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.courtlistener import CourtListenerClient, default_rate_limiter
from fedcourtsai.pipeline import order_scan
from fedcourtsai.pipeline.order_scan import (
    OrderScanConfig,
    SearchQuery,
    SearchWindow,
    load_order_scan_config,
    read_entry,
    scan,
)

_BASE = "https://www.courtlistener.com/api/rest/v4/"
_ROOT = Path(__file__).resolve().parent.parent

_Handler = Callable[[httpx.Request], httpx.Response]


@pytest.fixture(autouse=True)
def _no_backoff_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make tenacity's between-retry backoff instant so tests don't really sleep."""
    get: Any = CourtListenerClient._get
    monkeypatch.setattr(get.retry, "sleep", lambda _seconds: None)


def _client(handler: _Handler) -> CourtListenerClient:
    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client = httpx.Client(base_url=_BASE, transport=httpx.MockTransport(handler))
    return client


def _config(**overrides: Any) -> OrderScanConfig:
    data: dict[str, Any] = {
        "max_requests_per_run": 50,
        "max_pages_per_search": 5,
        "windows": [
            {"name": "w1", "filed_after": "2017-01-20", "filed_before": "2021-01-20"},
            {"name": "w2", "filed_after": "2021-01-20", "filed_before": "2025-01-20"},
        ],
        "queries": [
            {"name": "pi", "params": {"description": '"preliminary injunction"'}},
        ],
        "gold": [],
    }
    data.update(overrides)
    return OrderScanConfig.model_validate(data)


def _result(
    docket_id: int, court: str = "mad", *docs: dict[str, Any], **extra: Any
) -> dict[str, Any]:
    return {
        "docket_id": docket_id,
        "court_id": court,
        "docketNumber": f"1:25-cv-{docket_id:05d}",
        "caseName": f"State v. Agency {docket_id}",
        "dateFiled": "2025-03-01",
        "suitNature": "899 Other Statutes: Administrative Procedures Act",
        "recap_documents": list(docs),
        "more_docs": False,
        **extra,
    }


def _doc(entry: int, description: str, ident: int | None = None) -> dict[str, Any]:
    return {
        "id": ident if ident is not None else entry * 10,
        "entry_number": entry,
        "entry_date_filed": "2025-03-10",
        "description": description,
    }


def _page(results: list[dict[str, Any]], next_url: str | None = None) -> dict[str, Any]:
    return {"count": len(results), "next": next_url, "previous": None, "results": results}


class _Upstream:
    """Answers each search by its window and cursor, and records every request."""

    def __init__(self, pages: dict[tuple[str, str], dict[str, Any]]) -> None:
        self.pages = pages
        self.requests: list[dict[str, str]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        params = dict(parse_qsl(request.url.query.decode()))
        self.requests.append(params)
        key = (params.get("filed_after", ""), params.get("cursor", ""))
        if key not in self.pages:
            return httpx.Response(200, json=_page([]))
        return httpx.Response(200, json=self.pages[key])


def test_read_entry_names_kinds_and_polarity() -> None:
    assert read_entry("ORDER granting 12 Motion for Preliminary Injunction") == (
        ["preliminary-injunction"],
        "granted",
    )
    assert read_entry("ORDER denying motion for temporary restraining order") == (
        ["tro"],
        "denied",
    )
    assert read_entry("MEMORANDUM granting in part and denying in part; rule vacated") == (
        ["vacatur"],
        "mixed",
    )
    assert read_entry("Order postponing the effective date under section 705") == (
        ["stay-705"],
        "unclear",
    )
    assert read_entry("NOTICE of appearance") == ([], "unclear")


def test_config_refuses_an_unknown_search_parameter() -> None:
    with pytest.raises(ValidationError, match="unknown search parameters"):
        SearchQuery(name="x", params={"type": "o"})


def test_config_refuses_a_backwards_window() -> None:
    with pytest.raises(ValidationError, match="ends on or before"):
        SearchWindow(name="w", filed_after=date(2021, 1, 1), filed_before=date(2020, 1, 1))


def test_config_refuses_duplicate_and_slashed_names() -> None:
    with pytest.raises(ValidationError, match="duplicate query names"):
        _config(queries=[{"name": "a", "params": {"q": "x"}}, {"name": "a", "params": {"q": "y"}}])
    with pytest.raises(ValidationError):
        _config(queries=[{"name": "a/b", "params": {"q": "x"}}])


def test_scan_pages_merges_and_keeps_district_dockets_only() -> None:
    next_url = f"{_BASE}search/?type=r&filed_after=2017-01-20&cursor=abc"
    upstream = _Upstream(
        {
            ("2017-01-20", ""): _page(
                [
                    _result(1, "mad", _doc(5, "ORDER granting preliminary injunction")),
                    _result(2, "ca1", _doc(3, "ORDER granting stay")),
                ],
                next_url,
            ),
            ("2017-01-20", "abc"): _page([_result(3, "nysd", _doc(7, "TRO denied"))]),
            ("2021-01-20", ""): _page(
                [
                    _result(
                        1,
                        "mad",
                        _doc(5, "ORDER granting preliminary injunction"),
                        _doc(9, "ORDER vacating the rule"),
                        more_docs=True,
                    )
                ]
            ),
        }
    )
    config = _config(
        gold=[
            {"docket_id": 3, "court": "nysd", "docket_number": "x", "applications": ["19A1"]},
            {"docket_id": 99, "court": "dcd", "docket_number": "y", "applications": ["25A1"]},
        ]
    )
    report = scan(
        _client(upstream), config, max_requests=50, now=datetime(2026, 10, 27, tzinfo=UTC)
    )

    assert upstream.requests[0]["type"] == "r"
    assert upstream.requests[0]["filed_before"] == "2021-01-20"
    assert upstream.requests[1]["cursor"] == "abc"
    assert report.requests == 3
    assert [hit.docket_id for hit in report.hits] == [1, 3]
    first = report.hits[0]
    assert first.searches == ["pi/w1", "pi/w2"]
    assert [entry.entry_number for entry in first.entries] == [5, 9]
    assert first.entries[1].kinds == ["vacatur"]
    assert first.more_entries
    assert report.searches[0].other_courts == 1 and report.searches[0].district == 2
    assert report.hits_by_window == {"w1": 2, "w2": 1}
    assert report.gold_found == 1
    assert [g.found for g in report.gold] == [True, False]
    assert report.stopped is None and report.deferred == []


def test_scan_stops_a_search_at_its_page_cap() -> None:
    def endless(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_page([_result(1)], f"{_BASE}search/?type=r&cursor=more"))

    report = scan(_client(endless), _config(max_pages_per_search=2), max_requests=50)
    assert [s.pages for s in report.searches] == [2, 2]
    assert all(s.truncated for s in report.searches)
    assert report.requests == 4


def test_scan_stops_before_the_request_past_the_run_cap() -> None:
    upstream = _Upstream({})
    report = scan(_client(upstream), _config(), max_requests=1)
    assert len(upstream.requests) == 1
    assert report.requests == 1
    assert report.stopped == "run cap of 1 requests reached"
    assert report.deferred == ["pi/w2"]
    assert [s.search for s in report.searches] == ["pi/w1"]


def test_a_refused_credential_stops_the_scan() -> None:
    report = scan(_client(lambda request: httpx.Response(401)), _config(), max_requests=50)
    assert report.stopped is not None and "401" in report.stopped
    assert report.deferred == ["pi/w1", "pi/w2"]
    assert report.searches == []


def test_a_failed_search_is_recorded_and_the_scan_goes_on() -> None:
    def answer(request: httpx.Request) -> httpx.Response:
        if "2017-01-20" in str(request.url):
            return httpx.Response(400, json={"detail": "bad query"})
        return httpx.Response(200, json=_page([_result(4)]))

    report = scan(_client(answer), _config(), max_requests=50)
    assert report.searches[0].error is not None and "400" in report.searches[0].error
    assert report.searches[1].district == 1
    assert report.stopped is None


def test_search_next_refuses_a_link_off_the_search_endpoint() -> None:
    upstream = _Upstream({})
    client = _client(upstream)
    with pytest.raises(ValueError, match="off the search endpoint"):
        client.search_next("https://example.com/api/rest/v4/search/?cursor=x")
    with pytest.raises(ValueError, match="off the search endpoint"):
        client.search_next(f"{_BASE}dockets/?cursor=x")
    with pytest.raises(ValueError, match="repeats a parameter"):
        client.search_next(f"{_BASE}search/?court=a&court=b")
    assert upstream.requests == []


def test_an_off_endpoint_next_link_fails_only_its_search() -> None:
    def answer(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_page([_result(1)], "https://example.com/next"))

    report = scan(_client(answer), _config(), max_requests=50)
    assert all(s.error is not None for s in report.searches)
    assert [h.docket_id for h in report.hits] == [1]


def test_the_committed_config_loads_and_fits_its_cap() -> None:
    config = load_order_scan_config(_ROOT / "config" / "order-scan.yaml")
    worst = len(config.searches()) * config.max_pages_per_search
    assert worst <= config.max_requests_per_run
    assert len({g.docket_id for g in config.gold}) == len(config.gold)
    assert config.max_requests_per_run <= 150


def test_cli_plan_needs_no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FEDCOURTS_COURTLISTENER_API_TOKEN", raising=False)
    result = CliRunner().invoke(app, ["order-scan", "--plan", "--max-requests", "10"])
    assert result.exit_code == 0, result.output
    assert "run cap 10" in result.output


def test_cli_refuses_without_a_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FEDCOURTS_COURTLISTENER_API_TOKEN", raising=False)
    result = CliRunner().invoke(app, ["order-scan"])
    assert result.exit_code == 2
    assert "no CourtListener API token" in result.output


def test_cli_refuses_a_cap_above_the_config(monkeypatch: pytest.MonkeyPatch) -> None:
    result = CliRunner().invoke(app, ["order-scan", "--plan", "--max-requests", "100000"])
    assert result.exit_code == 2


def test_summary_names_missed_gold() -> None:
    report = order_scan.OrderScanReport(
        generated_at="2026-10-27T00:00:00+00:00",
        max_requests=10,
        gold=[
            order_scan.GoldOutcome(
                docket_id=1, court="dcd", docket_number="1:25-cv-1", applications=[], found=False
            )
        ],
    )
    lines = order_scan.summary_lines(report)
    assert "gold recall: 0 of 1" in lines
    assert any("dcd 1:25-cv-1" in line for line in lines)
