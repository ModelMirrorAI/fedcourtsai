"""The appeal reader's sample: the draw, the civil screen, the reading, the walls.

Every test is offline: the client's transport is an ``httpx.MockTransport``
answering from canned pages.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.config import load_courtlistener_budget
from fedcourtsai.courtlistener import CourtListenerClient, default_rate_limiter
from fedcourtsai.pipeline import appeal_sample
from fedcourtsai.pipeline.appeal_sample import failure, is_civil, sample, summary_lines

_BASE = "https://www.courtlistener.com/api/rest/v4/"
_ROOT = Path(__file__).resolve().parents[1]
_NOW = datetime(2026, 11, 12, 12, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _no_backoff_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make tenacity's between-retry backoff instant so tests don't really sleep."""
    get: Any = CourtListenerClient._get
    monkeypatch.setattr(get.retry, "sleep", lambda _seconds: None)


def _entry(number: int, filed: str, text: str) -> dict[str, Any]:
    return {"id": number, "entry_number": number, "date_filed": filed, "description": text}


_REPLY = _entry(20, "2025-03-01", "REPLY BRIEF FILED by Appellant Jane Roe.")
_AFFIRMED = _entry(30, "2025-06-01", "JUDGMENT, Affirmed. Mandate to issue.")
_PARTIAL = _entry(
    31, "2025-06-01", "ORDER filed: the appeal is DISMISSED as to appellant John Doe only."
)


class _Upstream:
    """Canned search pages, dockets and entry pages, with every request recorded."""

    def __init__(
        self,
        pages: list[list[int]],
        dockets: dict[int, dict[str, Any]],
        entries: dict[int, list[list[dict[str, Any]]]],
    ) -> None:
        self.pages = pages
        self.dockets = dockets
        self.entries = entries
        self.requests: list[httpx.Request] = []
        self.fail: dict[str, int] = {}

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        path = request.url.path.removeprefix("/api/rest/v4/")
        for marker, status in self.fail.items():
            if marker in str(request.url):
                return httpx.Response(status, json={"detail": "refused"})
        if path == "search/":
            index = int(request.url.params.get("cursor", "0"))
            following = (
                f"{_BASE}search/?cursor={index + 1}" if index + 1 < len(self.pages) else None
            )
            results = [{"docket_id": docket_id} for docket_id in self.pages[index]]
            return httpx.Response(200, json={"count": 99, "next": following, "results": results})
        if path == "docket-entries/":
            docket_id = int(request.url.params["docket"])
            index = int(request.url.params.get("cursor", "0"))
            pages = self.entries.get(docket_id, [[]])
            following = (
                f"{_BASE}docket-entries/?docket={docket_id}&cursor={index + 1}"
                if index + 1 < len(pages)
                else None
            )
            return httpx.Response(200, json={"next": following, "results": pages[index]})
        docket_id = int(path.removeprefix("dockets/").strip("/"))
        return httpx.Response(200, json=self.dockets[docket_id])


def _docket(number: str, kind: str, *, terminated: str | None = None) -> dict[str, Any]:
    return {
        "docket_number": number,
        "appellate_case_type_information": kind,
        "date_terminated": terminated,
    }


def _client(upstream: _Upstream) -> CourtListenerClient:
    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client = httpx.Client(base_url=_BASE, transport=httpx.MockTransport(upstream))
    return client


def _upstream() -> _Upstream:
    return _Upstream(
        pages=[[1, 2, 3, 1], [4, 5, 6]],
        dockets={
            1: _docket("24-100", "Civil, Private", terminated="2025-06-01"),
            2: _docket("24-101", "Criminal, Direct Criminal"),
            3: _docket("24-102", ""),
            4: _docket("24-103", "civil, United States as party", terminated="2025-07-01"),
            5: _docket("24-104", "Civil US, United States", terminated="2025-08-01"),
            6: _docket("24-105", "Civil, Private"),
        },
        entries={
            1: [[_REPLY], [_AFFIRMED]],
            4: [[_PARTIAL]],
            5: [[_entry(1, "2024-09-01", "Notice of appeal docketed.")]],
            6: [[_REPLY]],
        },
    )


def test_is_civil_reads_the_case_type_each_circuit_writes() -> None:
    assert is_civil("Civil, Private") is True
    assert is_civil("civil, private, Diversity") is True
    assert is_civil("Civil US, United States") is True
    assert is_civil("Criminal, Direct Criminal") is False
    assert is_civil("agency, petition review, Immigration") is False
    assert is_civil("Bankruptcy, District Court") is False
    assert is_civil("Orig. Proceeding Victim Rights, Mandamus") is False
    assert is_civil("") is None
    assert is_civil(None) is None


def test_sample_screens_reads_and_counts_each_reading() -> None:
    upstream = _upstream()
    with _client(upstream) as client:
        report = sample(client, "ca9", now=_NOW)

    first = dict(upstream.requests[0].url.params)
    assert first == {
        "type": "d",
        "court": "ca9",
        "filed_after": "2024-07-01",
        "filed_before": "2025-06-30",
        "order_by": f"random_{appeal_sample.SEED} desc",
    }
    assert (report.candidates, report.not_civil, report.no_case_type) == (6, 1, 1)
    assert report.exhausted and report.stopped is None
    assert report.requests == len(upstream.requests) == 13
    by_id = {row.docket_id: row for row in report.rows}
    assert sorted(by_id) == [1, 4, 5, 6]
    assert (by_id[1].reading, by_id[1].outcome, by_id[1].entry_numbers) == (
        "resolved",
        "affirmed",
        [30],
    )
    assert by_id[1].reply_read and by_id[1].entries == 2
    assert (by_id[4].reading, by_id[4].entry_numbers) == ("triage", [31])
    assert by_id[4].reason == "an order that dismisses less than the whole appeal"
    assert (by_id[5].reading, by_id[5].terminated) == ("open", True)
    assert (by_id[6].reading, by_id[6].terminated) == ("open", False)
    assert report.counts() == {
        "sampled": 4,
        "resolved": 1,
        "triage": 1,
        "open": 2,
        "open_terminated": 1,
        "too_long": 0,
    }
    lines = "\n".join(summary_lines(report))
    assert "4 of 25 civil appeals read" in lines
    assert "disposition read: 1 (affirmed 1)" in lines
    assert "triage: 1 of the 2 appeals with a disposition entry (0.50)" in lines
    assert "nothing read: 2, of which 1 upstream marks terminated" in lines
    assert failure(report) is None


def test_the_report_carries_no_entry_text() -> None:
    with _client(_upstream()) as client:
        report = sample(client, "ca9", now=_NOW)
    dumped = report.model_dump_json()
    assert "Jane Roe" not in dumped and "John Doe" not in dumped and "Private" not in dumped


def test_sample_stops_at_take_and_asks_no_more() -> None:
    upstream = _upstream()
    with _client(upstream) as client:
        report = sample(client, "ca9", take=1, now=_NOW)
    assert [row.docket_id for row in report.rows] == [1]
    assert not report.exhausted and report.stopped is None
    assert len(upstream.requests) == 4


def test_a_docket_longer_than_the_page_cap_is_not_read() -> None:
    upstream = _upstream()
    upstream.entries[1] = [[_AFFIRMED]] + [[] for _ in range(appeal_sample.MAX_ENTRY_PAGES)]
    with _client(upstream) as client:
        report = sample(client, "ca9", take=1, now=_NOW)
    (row,) = report.rows
    assert (row.reading, row.outcome) == ("too-long", None)
    assert report.counts()["too_long"] == 1


def test_the_run_cap_stops_the_run_and_drops_the_docket_in_hand() -> None:
    upstream = _upstream()
    with _client(upstream) as client:
        report = sample(client, "ca9", max_requests=3, now=_NOW)
    assert report.stopped == "run cap of 3 requests reached"
    assert report.rows == [] and report.requests == len(upstream.requests) == 3
    assert failure(report) == report.stopped

    upstream = _upstream()
    with _client(upstream) as client:
        kept = sample(client, "ca9", max_requests=6, now=_NOW)
    assert [row.docket_id for row in kept.rows] == [1]
    assert kept.stopped is not None and failure(kept) is None


def test_a_refused_credential_fails_the_run() -> None:
    upstream = _upstream()
    upstream.fail["search/"] = 401
    with _client(upstream) as client:
        report = sample(client, "ca9", now=_NOW)
    assert report.stopped == "CourtListener refused the credential (HTTP 401)"
    assert failure(report) == report.stopped


def test_one_dockets_failed_read_is_recorded_and_passed_over() -> None:
    upstream = _upstream()
    upstream.fail["dockets/4/"] = 404
    with _client(upstream) as client:
        report = sample(client, "ca9", now=_NOW)
    assert sorted(row.docket_id for row in report.rows) == [1, 5, 6]
    assert len(report.errors) == 1 and report.errors[0].startswith("docket 4: ")


def test_a_court_outside_the_sample_is_refused() -> None:
    with _client(_upstream()) as client, pytest.raises(ValueError):
        sample(client, "ca5", now=_NOW)


def test_plan_prints_the_search_and_needs_no_token() -> None:
    result = CliRunner().invoke(app, ["appeal-sample", "--court", "ca2", "--plan"])
    assert result.exit_code == 0, result.output
    assert "appeal-sample ca2: the first 25 civil appeals" in result.output
    assert f"at most {appeal_sample.MAX_REQUESTS} requests" in result.output


def test_command_refuses_another_court_and_a_cap_above_the_lane_share() -> None:
    assert CliRunner().invoke(app, ["appeal-sample", "--court", "ca5", "--plan"]).exit_code == 2
    over = str(appeal_sample.MAX_REQUESTS + 1)
    result = CliRunner().invoke(
        app, ["appeal-sample", "--court", "ca2", "--plan", "--max-requests", over]
    )
    assert result.exit_code == 2


def test_command_prints_the_report_and_the_reading(monkeypatch: pytest.MonkeyPatch) -> None:
    upstream = _upstream()
    monkeypatch.setenv("FEDCOURTS_COURTLISTENER_API_TOKEN", "test-token")
    monkeypatch.setattr("fedcourtsai.cli._client", lambda _lane: _client(upstream))
    result = CliRunner().invoke(app, ["appeal-sample", "--court", "ca3"])
    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert report["court"] == "ca3" and report["counts"]["sampled"] == 4
    assert "appeal-sample ca3: 4 of 25 civil appeals read" in result.stderr


def test_the_lane_share_is_the_run_cap() -> None:
    lane = load_courtlistener_budget(_ROOT / "config").lane("appeal-sample")
    assert (lane.per_run, lane.dispatched) == (appeal_sample.MAX_REQUESTS, True)
