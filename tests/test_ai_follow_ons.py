"""Follow-on dockets of listed AI cases: the search walk, the corpus readings, the renders.

Every test is offline: the client's transport is an ``httpx.MockTransport``
answering from canned pages, and the corpus is a temporary database.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

import httpx
import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.ai_watchlist import AiWatchlist
from fedcourtsai.cli import app
from fedcourtsai.corpus import CorpusRow
from fedcourtsai.courtlistener import CourtListenerClient, default_rate_limiter
from fedcourtsai.pipeline import ai_follow_ons
from fedcourtsai.pipeline.ai_candidates import raised_docket_ids
from fedcourtsai.pipeline.ai_follow_ons import (
    FOLLOW_ON_COURTS,
    ListedDocket,
    check,
    digest_line,
    failure,
    may_review,
    number_key,
    read_origin,
    regional_circuit,
    render_alarm,
    render_comment,
    scotus_follow_ons,
    searched_dockets,
    stale_dockets,
    watchlist_check,
)

_BASE = "https://www.courtlistener.com/api/rest/v4/"
_NOW = datetime(2026, 11, 11, 12, tzinfo=UTC)
_TODAY = _NOW.date()


@pytest.fixture(autouse=True)
def _no_backoff_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make tenacity's between-retry backoff instant so tests don't really sleep."""
    get: Any = CourtListenerClient._get
    monkeypatch.setattr(get.retry, "sleep", lambda _seconds: None)


def _watchlist() -> AiWatchlist:
    return AiWatchlist.model_validate(
        {
            "categories": {"copyright": "Training on works."},
            "cases": [
                {
                    "name": "Listed v. Developer",
                    "court": "cand",
                    "docket_id": 100,
                    "docket_number": "3:23-cv-00100",
                    "category": "copyright",
                    "why": "Training.",
                    "developers": ["Developer"],
                    "added": "2026-10-30",
                    "related": [
                        {
                            "court": "ca9",
                            "docket_id": 101,
                            "docket_number": "25-101",
                            "relation": "appeal",
                        },
                        {
                            "court": "jpml",
                            "docket_id": 102,
                            "docket_number": "MDL No. 3000",
                            "relation": "mdl",
                        },
                    ],
                },
                {
                    "name": "Second v. Developer",
                    "court": "nysd",
                    "docket_id": 200,
                    "docket_number": "1:24-cv-00200",
                    "category": "copyright",
                    "why": "Outputs.",
                    "developers": ["Developer"],
                    "added": "2026-11-09",
                },
            ],
        }
    )


def _hit(docket_id: int, court: str, number: str, filed: str = "2026-11-02") -> dict[str, Any]:
    return {
        "docket_id": docket_id,
        "court_id": court,
        "docketNumber": number,
        "caseName": "Someone v. Developer",
        "dateFiled": filed,
    }


def _docket(number: str = "", court: str | None = None) -> dict[str, Any]:
    return {
        "appeal_from": f"{_BASE}courts/{court}/" if court else None,
        "original_court_info": {"docket_number": number} if number is not None else None,
    }


class _Upstream:
    """Answers a search by its phrase and a docket read by its id; records every request."""

    def __init__(
        self,
        searches: dict[str, Any] | None = None,
        dockets: dict[int, Any] | None = None,
    ) -> None:
        self.searches = searches or {}
        self.dockets = dockets or {}
        self.search_requests: list[dict[str, str]] = []
        self.docket_reads: list[int] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/search/"):
            params = dict(parse_qsl(request.url.query.decode()))
            self.search_requests.append(params)
            answer = self.searches.get(params["q"].strip('"'), [])
            if isinstance(answer, httpx.Response):
                return answer
            if isinstance(answer, dict):
                return httpx.Response(200, json=answer)
            return httpx.Response(200, json={"count": len(answer), "next": None, "results": answer})
        docket_id = int(path.rstrip("/").rsplit("/", 1)[-1])
        self.docket_reads.append(docket_id)
        answer = self.dockets.get(docket_id, _docket())
        return answer if isinstance(answer, httpx.Response) else httpx.Response(200, json=answer)


def _client(upstream: _Upstream) -> CourtListenerClient:
    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client = httpx.Client(base_url=_BASE, transport=httpx.MockTransport(upstream))
    return client


# --- numbers and courts -------------------------------------------------------


def test_number_key_reads_one_docket_through_each_courts_spelling() -> None:
    assert number_key("1:20-cv-00613-SB") == number_key("20-cv-613") == ("20", "cv", "613")
    assert number_key("3:23-CV-03417") == number_key("23-cv-03417")
    assert number_key("25-02153") == number_key("25-2153") == ("25", "2153")
    assert number_key("1:20-cv-00613") != number_key("1:20-md-00613")
    assert number_key("24-1234-cv") == number_key("24-1234")
    assert number_key("2024-1285") == number_key("24-1285")
    assert number_key("MDL No. 3143") is None
    assert number_key("2025-G-0010") is None


def test_regional_circuit_reads_a_district_id() -> None:
    assert regional_circuit("cand") == "ca9"
    assert regional_circuit("nysd") == "ca2"
    assert regional_circuit("ded") == "ca3"
    assert regional_circuit("dcd") == "cadc"
    assert regional_circuit("nmd") == "ca10"
    assert regional_circuit("nmid") == "ca9"
    assert regional_circuit("vid") == "ca3"
    assert regional_circuit("vaed") == "ca4"
    assert regional_circuit("zzd") is None
    assert may_review("ca9", "cand") and may_review("cafc", "cand")
    assert not may_review("ca2", "cand")
    assert may_review("ca2", "zzd")


def test_only_listed_district_dockets_are_searched() -> None:
    assert [(d.court, d.docket_number) for d in searched_dockets(_watchlist())] == [
        ("cand", "3:23-cv-00100"),
        ("nysd", "1:24-cv-00200"),
    ]


def test_read_origin_compares_the_originating_number_and_court() -> None:
    listed = ListedDocket(
        case="Listed v. Developer",
        court="cand",
        docket_id=100,
        docket_number="3:23-cv-00100",
        added=date(2026, 10, 30),
    )
    assert read_origin(_docket("3:23-cv-00100-ABC", "cand"), listed) == "confirmed"
    assert read_origin(_docket("23-cv-100"), listed) == "confirmed"
    assert read_origin(_docket("3:23-cv-00999", "cand"), listed) is None
    assert read_origin(_docket("3:23-cv-00100", "cacd"), listed) is None
    # No originating court to compare: a different office is another district's case.
    assert read_origin(_docket("2:23-cv-00100"), listed) is None
    assert read_origin(_docket("2:23-cv-00100", "cand"), listed) == "confirmed"
    assert read_origin(_docket(""), listed) == "unrecorded"
    assert read_origin({"appeal_from": None, "original_court_info": None}, listed) == "unrecorded"


# --- the search walk ----------------------------------------------------------


def test_check_raises_confirmed_and_unrecorded_appeals_and_new_mdl_dockets() -> None:
    upstream = _Upstream(
        searches={
            "3:23-cv-00100": [
                _hit(101, "ca9", "25-101"),  # already listed
                _hit(301, "ca9", "26-301", "2026-11-03"),  # confirmed
                _hit(302, "ca9", "26-302", "2026-11-01"),  # origin not recorded yet
                _hit(303, "ca9", "26-303"),  # another case's appeal
                _hit(304, "ca2", "26-304"),  # a circuit that cannot hear cand
                _hit(305, "jpml", "MDL No. 3200", "2026-10-30"),  # a new MDL
                _hit(306, "jpml", "3:23-cv-00100"),  # a panel member row
                _hit(307, "scotus", "26-1"),  # not a court the check reads
                _hit(308, "ca9", "26-308"),  # raised before
            ],
        },
        dockets={
            301: _docket("3:23-cv-00100", "cand"),
            302: _docket(""),
            303: _docket("3:23-cv-00777", "cand"),
        },
    )
    with _client(upstream) as client:
        report = check(client, _watchlist(), raised=[308], now=_NOW)

    assert [(h.docket_id, h.relation.value, h.origin) for h in report.follow_ons] == [
        (301, "appeal", "confirmed"),
        (302, "appeal", "unrecorded"),
        (305, "mdl", "mention"),
    ]
    assert {h.related_to for h in report.follow_ons} == {"Listed v. Developer"}
    assert sorted(upstream.docket_reads) == [301, 302, 303]
    assert (report.searched, report.requests) == (2, 5)
    assert (report.hits, report.on_watchlist, report.already_raised) == (8, 1, 1)
    assert (report.other_origin, report.panel_member_rows) == (2, 1)
    assert failure(report) is None


def test_search_asks_the_appellate_courts_for_the_number_inside_the_window() -> None:
    upstream = _Upstream()
    with _client(upstream) as client:
        report = check(client, _watchlist(), now=_NOW, lookback_days=30)

    first = upstream.search_requests[0]
    assert first["q"] == '"3:23-cv-00100"'
    assert first["type"] == "d"
    assert first["court"] == FOLLOW_ON_COURTS
    assert first["filed_after"] == (_TODAY - timedelta(days=30)).isoformat()
    assert report.filed_after == first["filed_after"]
    assert render_comment(report) == ""


def test_a_docket_found_under_two_listed_numbers_is_read_once() -> None:
    upstream = _Upstream(
        searches={
            "3:23-cv-00100": [_hit(301, "ca9", "26-301")],
            "1:24-cv-00200": [_hit(301, "ca9", "26-301")],
        },
        dockets={301: _docket("3:23-cv-00100", "cand")},
    )
    with _client(upstream) as client:
        report = check(client, _watchlist(), now=_NOW)

    assert [h.docket_id for h in report.follow_ons] == [301]
    assert upstream.docket_reads == [301]


def test_the_run_cap_leaves_new_hits_unread_and_keeps_what_it_confirmed() -> None:
    upstream = _Upstream(
        searches={
            "3:23-cv-00100": [
                _hit(301, "ca9", "26-301", "2026-11-05"),
                _hit(302, "ca9", "26-302", "2026-11-01"),
            ]
        },
        dockets={301: _docket("3:23-cv-00100", "cand")},
    )
    with _client(upstream) as client:
        report = check(client, _watchlist(), max_requests=3, now=_NOW)

    # Both searches ran first; the newest hit was read; the cap stopped the second read.
    assert (report.searched, report.requests, report.unread) == (2, 3, 1)
    assert report.stopped is not None and "run cap" in report.stopped
    assert report.deferred == []
    assert [h.docket_id for h in report.follow_ons] == [301]
    assert failure(report) is None
    assert "1 new hits were not read" in render_comment(report)


def test_the_run_cap_defers_the_searches_it_did_not_reach() -> None:
    with _client(_Upstream()) as client:
        report = check(client, _watchlist(), max_requests=1, now=_NOW)
    assert report.searched == 1
    assert report.deferred == ["nysd 1:24-cv-00200"]


def test_a_docket_is_attributed_to_the_listed_case_it_reviews_whatever_the_order() -> None:
    # A Second Circuit appeal from the nysd case that first surfaces under the
    # cand case's number, which the Second Circuit cannot review.
    upstream = _Upstream(
        searches={
            "3:23-cv-00100": [_hit(401, "ca2", "26-401")],
            "1:24-cv-00200": [_hit(401, "ca2", "26-401")],
        },
        dockets={401: _docket("1:24-cv-00200", "nysd")},
    )
    with _client(upstream) as client:
        report = check(client, _watchlist(), now=_NOW)

    assert [(h.docket_id, h.related_to, h.origin) for h in report.follow_ons] == [
        (401, "Second v. Developer", "confirmed")
    ]
    assert upstream.docket_reads == [401]


def test_a_failed_docket_read_costs_only_that_hit() -> None:
    upstream = _Upstream(
        searches={
            "3:23-cv-00100": [
                _hit(301, "ca9", "26-301", "2026-11-05"),
                _hit(302, "ca9", "26-302", "2026-11-01"),
            ]
        },
        dockets={
            301: httpx.Response(404, json={}),
            302: _docket("3:23-cv-00100", "cand"),
        },
    )
    with _client(upstream) as client:
        report = check(client, _watchlist(), now=_NOW)

    assert [h.docket_id for h in report.follow_ons] == [302]
    assert len(report.read_errors) == 1 and report.errors == []
    assert failure(report) is None


def test_a_refused_credential_and_an_all_failed_run_fail_the_job() -> None:
    refused = _Upstream(searches={"3:23-cv-00100": httpx.Response(401, json={})})
    with _client(refused) as client:
        report = check(client, _watchlist(), now=_NOW)
    assert "HTTP 401" in (failure(report) or "")
    assert report.deferred == ["cand 3:23-cv-00100", "nysd 1:24-cv-00200"]

    for answer in ({"count": 0}, httpx.Response(404, json={})):
        broken = _Upstream(searches={"3:23-cv-00100": answer, "1:24-cv-00200": answer})
        with _client(broken) as client:
            report = check(client, _watchlist(), now=_NOW)
        assert (len(report.errors), report.searched) == (2, 0)
        assert failure(report) == "every search failed"

    half = _Upstream(searches={"3:23-cv-00100": httpx.Response(404, json={})})
    with _client(half) as client:
        report = check(client, _watchlist(), now=_NOW)
    assert (len(report.errors), report.searched) == (1, 1)
    assert failure(report) is None


def test_a_full_page_is_reported_truncated() -> None:
    upstream = _Upstream(
        searches={
            "3:23-cv-00100": {
                "count": 40,
                "next": f"{_BASE}search/?cursor=abc",
                "results": [],
            }
        }
    )
    with _client(upstream) as client:
        report = check(client, _watchlist(), now=_NOW)
    assert report.truncated == ["cand 3:23-cv-00100"]


def test_comment_carries_the_shared_raised_marker_and_no_caption() -> None:
    upstream = _Upstream(
        searches={"3:23-cv-00100": [_hit(301, "ca9", "26-301|[x](y)")]},
        dockets={301: _docket("3:23-cv-00100", "cand")},
    )
    with _client(upstream) as client:
        report = check(client, _watchlist(), now=_NOW)
    comment = render_comment(report)

    posted = {"author": {"login": "github-actions"}, "body": "<!-- key -->\n" + comment}
    assert raised_docket_ids([posted]) == {301}
    assert "Someone v. Developer" not in comment
    assert "26-301--x--y-" in comment
    assert "https://www.courtlistener.com/docket/301/" in comment
    assert "| Listed v. Developer | cand 3:23-cv-00100 | appeal |" in comment


# --- the corpus readings ------------------------------------------------------


def _db(tmp_path: Path, rows: list[CorpusRow]) -> Path:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    return db


def _scotus(docket_id: int, number: str, **fields: Any) -> CorpusRow:
    return CorpusRow(case_id=f"scotus/{docket_id}", court="scotus", docket_number=number, **fields)


def test_scotus_rows_match_a_listed_docket_by_court_and_number(tmp_path: Path) -> None:
    db = _db(
        tmp_path,
        [
            _scotus(
                1,
                "26-500",
                originating_court="ca9",
                originating_docket_number="24-900, 25-101",
                date_filed=date(2026, 11, 2),
            ),
            # The live channel's row: a court name and no court id.
            _scotus(
                2,
                "26A77",
                originating_court_name="United States Court of Appeals for the Ninth Circuit",
                originating_docket_number="25-00101",
                date_filed=date(2026, 11, 5),
            ),
            # The same number in another circuit, and another number in the same one.
            _scotus(3, "26-501", originating_court="ca2", originating_docket_number="25-101"),
            _scotus(4, "26-502", originating_court="ca9", originating_docket_number="25-1010"),
            _scotus(5, "26-503", originating_court_name="Supreme Court of Ohio"),
        ],
    )
    with corpus.connect_readonly(db) as conn:
        found = scotus_follow_ons(conn, _watchlist(), linked=["scotus/1"])

    assert [(f.case_id, f.docket_number, f.linked) for f in found] == [
        ("scotus/2", "26A77", False),
        ("scotus/1", "26-500", True),
    ]
    assert {(f.from_court, f.from_docket_number) for f in found} == {("ca9", "25-101")}


def test_stale_dockets_count_from_the_last_refresh_or_the_listing(tmp_path: Path) -> None:
    db = _db(
        tmp_path,
        [
            CorpusRow(case_id="cand/100", court="cand", last_pulled=_TODAY - timedelta(days=1)),
            CorpusRow(case_id="ca9/101", court="ca9", last_pulled=_TODAY - timedelta(days=7)),
            # jpml/102 was never refreshed: its case was listed 12 days ago.
            # nysd/200 was never refreshed either, but was listed 2 days ago.
        ],
    )
    with corpus.connect_readonly(db) as conn:
        stale = stale_dockets(conn, _watchlist(), today=_TODAY)

    assert [(s.case_id, s.last_pulled, s.days) for s in stale] == [
        ("jpml/102", None, 12),
        ("ca9/101", (_TODAY - timedelta(days=7)).isoformat(), 7),
    ]


def test_watchlist_check_alarms_on_unlinked_scotus_dockets_and_stale_dockets(
    tmp_path: Path,
) -> None:
    fresh = [
        CorpusRow(case_id=case_id, court=case_id.split("/")[0], last_pulled=_TODAY)
        for case_id in ("cand/100", "ca9/101", "jpml/102", "nysd/200")
    ]
    petition = _scotus(1, "26-500", originating_court="ca9", originating_docket_number="25-101")
    db = _db(tmp_path, [*fresh, petition])

    with corpus.connect_readonly(db) as conn:
        linked = watchlist_check(conn, _watchlist(), linked=["scotus/1"], now=_NOW)
        unlinked = watchlist_check(conn, _watchlist(), now=_NOW)

    assert linked.ok and render_alarm(linked) == ""
    assert digest_line(linked) == (
        "AI watchlist: 4 listed dockets current; no unlinked Supreme Court docket."
    )
    assert not unlinked.ok
    assert "1 unlinked Supreme Court docket(s)" in digest_line(unlinked)
    alarm = render_alarm(unlinked)
    assert "| `26-500` (`scotus/1`) | ? | Listed v. Developer | ca9 25-101 |" in alarm
    assert "not refreshed" not in alarm


# --- the commands -------------------------------------------------------------


def test_plan_prints_the_searches_and_needs_no_token() -> None:
    result = CliRunner().invoke(app, ["ai-follow-ons", "--plan"])
    assert result.exit_code == 0, result.output
    assert "ai-follow-ons plan:" in result.output
    assert f"run cap {ai_follow_ons.MAX_REQUESTS}" in result.output


def test_follow_ons_command_refuses_a_cap_above_the_lane_share() -> None:
    result = CliRunner().invoke(
        app, ["ai-follow-ons", "--plan", "--max-requests", str(ai_follow_ons.MAX_REQUESTS + 1)]
    )
    assert result.exit_code == 2


def test_check_command_writes_the_report_the_alarm_and_the_digest_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "config"
    config.mkdir()
    (config / "ai-watchlist.yaml").write_text(
        json.dumps(_watchlist().model_dump(mode="json")), encoding="utf-8"
    )
    corpus_root = tmp_path / "corpus"
    corpus_root.mkdir()
    with corpus.connect(corpus.corpus_db_path(corpus_root)) as conn:
        corpus.upsert_rows(
            conn,
            [_scotus(1, "26-500", originating_court="ca9", originating_docket_number="25-101")],
        )
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "local")

    alarm, digest = tmp_path / "alarm.md", tmp_path / "digest.txt"
    result = CliRunner().invoke(
        app, ["ai-watchlist-check", "--alarm-out", str(alarm), "--digest-out", str(digest)]
    )

    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert [row["case_id"] for row in report["scotus"]] == ["scotus/1"]
    assert "scotus/1" in alarm.read_text(encoding="utf-8")
    assert digest.read_text(encoding="utf-8").startswith("AI watchlist: 1 unlinked")
