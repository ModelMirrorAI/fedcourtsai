"""The AI-case candidate check: config, the search walk, the known-docket diff, the comment.

Every test is offline: the client's transport is an ``httpx.MockTransport``
answering from canned search pages, and the issue side runs through the
``gh`` runner seam.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl

import httpx
import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from fedcourtsai.ai_watchlist import AiWatchlist, load_ai_watchlist
from fedcourtsai.cli import app
from fedcourtsai.config import load_courtlistener_budget
from fedcourtsai.courtlistener import CourtListenerClient, default_rate_limiter
from fedcourtsai.pipeline import ai_candidates
from fedcourtsai.pipeline.ai_candidates import (
    RAISED_MARKER,
    CandidatesConfig,
    CandidatesReport,
    SavedSearch,
    check,
    docket_url,
    in_scope,
    load_candidates_config,
    raised_docket_ids,
    render_comment,
)

_BASE = "https://www.courtlistener.com/api/rest/v4/"
_ROOT = Path(__file__).resolve().parent.parent
_NOW = datetime(2026, 11, 8, 12, tzinfo=UTC)

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


def _watchlist() -> AiWatchlist:
    return AiWatchlist.model_validate(
        {
            "categories": {"copyright": "Training on works.", "privacy": "Personal data."},
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
                        }
                    ],
                }
            ],
        }
    )


def _config(**overrides: Any) -> CandidatesConfig:
    data: dict[str, Any] = {
        "max_requests_per_run": 20,
        "max_pages_per_search": 2,
        "lookback_days": 21,
        "district_case_types": ["cv", "md"],
        "ai_terms": '"large language model"',
        "searches": [
            {"name": "dev", "type": "d", "params": {"party_name": '"Developer"'}},
            {
                "name": "claims",
                "type": "r",
                "ai_terms": True,
                "category": "copyright",
                "params": {"q": "suitNature:Copyright"},
            },
        ],
    }
    data.update(overrides)
    return CandidatesConfig.model_validate(data)


def _result(docket_id: int, court: str = "cand", number: str | None = None) -> dict[str, Any]:
    return {
        "docket_id": docket_id,
        "court_id": court,
        "docketNumber": number if number is not None else f"3:26-cv-{docket_id:05d}",
        "caseName": f"Someone v. Developer {docket_id}",
        "dateFiled": f"2026-11-{docket_id % 28 + 1:02d}",
        "docket_absolute_url": f"/docket/{docket_id}/someone-v-developer/",
    }


def _page(results: list[dict[str, Any]], next_url: str | None = None) -> dict[str, Any]:
    return {"count": len(results), "next": next_url, "previous": None, "results": results}


class _Upstream:
    """Answers each search by its type and cursor, and records every request."""

    def __init__(self, pages: dict[tuple[str, str], Any]) -> None:
        self.pages = pages
        self.requests: list[dict[str, str]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        params = dict(parse_qsl(request.url.query.decode()))
        self.requests.append(params)
        answer = self.pages.get((params.get("type", ""), params.get("cursor", "")))
        if isinstance(answer, httpx.Response):
            return answer
        return httpx.Response(200, json=answer if answer is not None else _page([]))


# --- config -------------------------------------------------------------------


def test_committed_config_loads_and_fits_its_lane_share() -> None:
    watchlist = load_ai_watchlist(_ROOT / "config" / "ai-watchlist.yaml")
    config = load_candidates_config(_ROOT / "config" / "ai-candidates.yaml", watchlist)
    lane = load_courtlistener_budget(_ROOT / "config").lane("ai-candidates")

    assert config.max_requests_per_run == lane.per_run
    assert config.worst_case_requests() <= config.max_requests_per_run


def test_config_refuses_unknown_parameters_and_doc_terms_on_a_docket_search() -> None:
    with pytest.raises(ValidationError, match="unknown search parameters"):
        SavedSearch(name="x", type="d", params={"type": "o"})
    with pytest.raises(ValidationError, match="type must be r"):
        SavedSearch(name="x", type="d", ai_terms=True, params={})
    with pytest.raises(ValidationError, match="needs a parameter"):
        SavedSearch(name="x", type="r", params={})
    with pytest.raises(ValidationError, match="distinct"):
        _config(
            searches=[
                {"name": "a", "type": "d", "params": {"q": "x"}},
                {"name": "a", "type": "d", "params": {"q": "y"}},
            ]
        )


def test_config_refuses_a_category_the_watchlist_does_not_define() -> None:
    config = _config(
        searches=[{"name": "a", "type": "d", "category": "nope", "params": {"q": "x"}}]
    )
    with pytest.raises(ValueError, match="'nope' is not one of"):
        config.check_categories(_watchlist())


def test_params_join_the_ai_terms_and_bound_the_filing_date() -> None:
    config = _config()
    claims = config.searches[1]
    params = config.params(claims, _NOW.date())

    assert params["q"] == '("large language model") AND (suitNature:Copyright)'
    assert params["type"] == "r"
    assert params["filed_after"] == "2026-11-08"
    assert params["order_by"] == "dateFiled desc"
    assert "q" not in config.params(config.searches[0], _NOW.date())


# --- scope and links ----------------------------------------------------------


def test_scope_keeps_civil_district_circuit_and_panel_dockets_only() -> None:
    types = ["cv", "md"]
    assert in_scope("cand", "3:26-cv-12826", types)
    assert in_scope("nysd", "1:25-md-03143", types)
    assert not in_scope("moed", "4:26-cr-00504", types)
    assert not in_scope("ncwd", "1:26-mj-00045", types)
    assert in_scope("ca9", "26-7228", types)
    assert in_scope("cadc", "26-5001", types)
    assert in_scope("jpml", "MDL No. 3143", types)
    assert not in_scope("uscfc", "1:26-cv-01636", types)
    assert not in_scope("canb", "26-10001", types)
    assert not in_scope("scotus", "26-100", types)
    # An unfamiliar district number format is kept for a look.
    assert in_scope("dcd", "26-1234", types)


def test_docket_url_is_the_bare_id_path() -> None:
    assert docket_url(7) == "https://www.courtlistener.com/docket/7/"


# --- the walk -----------------------------------------------------------------


def test_check_drops_watchlist_and_raised_dockets_and_merges_searches() -> None:
    upstream = _Upstream(
        {
            ("d", ""): _page([_result(1), _result(100), _result(5, "moed", "4:26-cr-00005")]),
            ("r", ""): _page([_result(1), _result(101, "ca9", "25-101"), _result(2), _result(3)]),
        }
    )
    report = check(
        _client(upstream), _config(), _watchlist(), raised={3}, max_requests=20, now=_NOW
    )

    assert report.filed_after == "2026-10-18"
    assert upstream.requests[0]["filed_after"] == "2026-10-18"
    assert report.requests == 2
    assert report.found == 5
    assert report.on_watchlist == 2
    assert report.already_raised == 1
    assert sorted(hit.docket_id for hit in report.candidates) == [1, 2]
    first = next(hit for hit in report.candidates if hit.docket_id == 1)
    assert first.searches == ["dev", "claims"]
    assert first.categories == ["copyright"]
    assert report.searches[0].out_of_scope == 1


def test_check_follows_next_links_to_the_page_cap_and_marks_truncation() -> None:
    page_two = f"{_BASE}search/?type=d&cursor=two"
    page_three = f"{_BASE}search/?type=d&cursor=three"
    upstream = _Upstream(
        {
            ("d", ""): _page([_result(1)], page_two),
            ("d", "two"): _page([_result(2)], page_three),
            ("d", "three"): _page([_result(3)]),
        }
    )
    report = check(_client(upstream), _config(), _watchlist(), max_requests=20, now=_NOW)

    dev = report.searches[0]
    assert dev.pages == 2
    assert dev.truncated
    assert sorted(hit.docket_id for hit in report.candidates) == [1, 2]
    assert not any(request.get("cursor") == "three" for request in upstream.requests)


def test_check_stops_at_the_run_cap_and_defers_the_rest() -> None:
    upstream = _Upstream({("d", ""): _page([_result(1)])})
    report = check(_client(upstream), _config(), _watchlist(), max_requests=1, now=_NOW)

    assert report.requests == 1
    assert report.stopped is not None and "run cap" in report.stopped
    assert report.deferred == ["claims"]
    assert [hit.docket_id for hit in report.candidates] == [1]
    assert ai_candidates.failure(report) is None


def test_a_refused_credential_fails_the_run() -> None:
    upstream = _Upstream({("d", ""): httpx.Response(401, json={"detail": "no"})})
    report = check(_client(upstream), _config(), _watchlist(), max_requests=20, now=_NOW)

    assert report.deferred == ["dev", "claims"]
    assert ai_candidates.failure(report) == "CourtListener refused the credential (HTTP 401)"


def test_every_search_failing_fails_the_run_but_one_failure_does_not() -> None:
    bad = httpx.Response(200, json={"count": 0})
    report = check(
        _client(_Upstream({("d", ""): bad, ("r", ""): bad})),
        _config(),
        _watchlist(),
        max_requests=20,
        now=_NOW,
    )
    assert all(outcome.error for outcome in report.searches)
    assert ai_candidates.failure(report) == "every search failed"

    report = check(
        _client(_Upstream({("d", ""): bad})), _config(), _watchlist(), max_requests=20, now=_NOW
    )
    assert ai_candidates.failure(report) is None


# --- the raised set and the comment -------------------------------------------


def _report_with(*docket_ids: int) -> CandidatesReport:
    upstream = _Upstream({("d", ""): _page([_result(i) for i in docket_ids])})
    return check(_client(upstream), _config(), _watchlist(), max_requests=20, now=_NOW)


def test_comment_round_trips_its_raised_ids_and_is_empty_when_quiet() -> None:
    body = render_comment(_report_with(7, 8))
    assert body.splitlines()[0] == f"{RAISED_MARKER} 8 7 -->"
    # Below a once-only key, as post-issue-comment posts it, it still counts.
    keyed = "<!-- run: 1 -->\n" + body
    assert raised_docket_ids([{"author": {"login": "github-actions"}, "body": keyed}]) == {7, 8}
    assert "https://www.courtlistener.com/docket/7/)" in body
    # Neither the caption nor upstream's slug of it is copied.
    assert "Someone v. Developer" not in body
    assert "someone-v-developer" not in body
    assert raised_docket_ids([{"author": {"login": "github-actions"}, "body": body}]) == {7, 8}
    assert render_comment(_report_with()) == ""


def test_raised_set_reads_only_the_posting_identitys_first_line() -> None:
    marker = f"{RAISED_MARKER} 1 2 -->"
    comments: list[dict[str, Any]] = [
        {"author": {"login": "github-actions"}, "body": marker + "\ntable"},
        {"author": {"login": "someone"}, "body": f"{RAISED_MARKER} 3 -->"},
        {"author": {"login": "github-actions[bot]"}, "body": f"a\nb\n{RAISED_MARKER} 4 -->"},
        {"author": {"login": "fedcourtsai-data[bot]"}, "body": f"{RAISED_MARKER} 7 -->"},
        {"author": {"login": "app/github-actions"}, "body": f"{RAISED_MARKER} 5 x 6 -->"},
        {"author": None, "body": f"{RAISED_MARKER} 9 -->"},
    ]
    assert raised_docket_ids(comments) == {1, 2, 5, 6}


class _Gh:
    """Answers the ``gh`` calls the issue side makes, and records them."""

    def __init__(self, issues: list[int], comments: dict[int, list[dict[str, Any]]]) -> None:
        self.issues = issues
        self.comments = comments
        self.calls: list[list[str]] = []

    def __call__(self, argv: Sequence[str]) -> str:
        self.calls.append(list(argv))
        if argv[1:3] == ["issue", "list"]:
            state = argv[argv.index("--state") + 1]
            numbers = self.issues if state == "all" else self.issues[:1]
            return json.dumps([{"number": n} for n in numbers])
        if argv[1:3] == ["issue", "view"]:
            return json.dumps({"comments": self.comments.get(int(argv[3]), [])})
        return ""


def test_issue_side_reads_every_labelled_issue(tmp_path: Path) -> None:
    gh = _Gh(
        [12, 4],
        {
            12: [{"author": {"login": "github-actions"}, "body": f"{RAISED_MARKER} 7 -->"}],
            4: [{"author": {"login": "github-actions"}, "body": f"{RAISED_MARKER} 8 -->"}],
        },
    )
    assert ai_candidates.candidates_issue("o/r", runner=gh) == 12
    assert raised_docket_ids(ai_candidates.issue_comments("o/r", runner=gh)) == {7, 8}
    assert any(call[1:3] == ["label", "create"] and "ai-candidates" in call for call in gh.calls)


def test_upstream_text_cannot_inject_markup_into_the_comment() -> None:
    hostile = _result(9, "ca9", "26-1 [x](https://e.example) @someone\n<!--")
    hostile["dateFiled"] = "not a date at all"
    upstream = _Upstream({("d", ""): _page([hostile])})
    report = check(_client(upstream), _config(), _watchlist(), max_requests=20, now=_NOW)
    body = render_comment(report)

    row = next(line for line in body.splitlines() if line.startswith("| ca9"))
    assert "@" not in row and "[x]" not in row and "<!--" not in row
    assert "| ? |" in row


def test_a_large_week_raises_at_most_the_row_cap() -> None:
    upstream = _Upstream(
        {("d", ""): _page([_result(i) for i in range(1000, 1000 + ai_candidates.MAX_ROWS + 10)])}
    )
    config = _config(max_pages_per_search=1)
    report = check(_client(upstream), config, _watchlist(), max_requests=20, now=_NOW)
    body = render_comment(report)

    raised = raised_docket_ids([{"author": {"login": "github-actions"}, "body": body}])
    assert len(raised) == ai_candidates.MAX_ROWS
    assert "10 older candidates are held for the next run." in body
    assert len(body) < 65_536


def test_a_run_stopped_before_its_first_request_fails() -> None:
    upstream = _Upstream({})
    report = check(_client(upstream), _config(), _watchlist(), max_requests=0, now=_NOW)
    assert report.requests == 0
    assert ai_candidates.failure(report) is not None


# --- the command --------------------------------------------------------------


def test_plan_needs_no_token_and_sends_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FEDCOURTS_COURTLISTENER_API_TOKEN", raising=False)
    result = CliRunner().invoke(app, ["ai-candidates", "--plan"])

    assert result.exit_code == 0, result.output
    assert "ai-candidates plan: 12 searches" in result.output
    assert "worst case 24 requests, run cap 40" in result.output


def test_command_refuses_a_raised_cap_bad_raised_file_and_malformed_repo(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FEDCOURTS_COURTLISTENER_API_TOKEN", "dummy")
    result = CliRunner().invoke(app, ["ai-candidates", "--max-requests", "41"])
    assert result.exit_code == 2
    assert "between 1 and the config's 40" in result.output
    bad = tmp_path / "raised.json"
    bad.write_text('["x"]')
    result = CliRunner().invoke(app, ["ai-candidates", "--raised", str(bad)])
    assert result.exit_code == 2
    assert "cannot read --raised" in result.output
    result = CliRunner().invoke(
        app,
        ["ai-candidates-issue", "--repo", "not a repo", "--issue-out", "a", "--raised-out", "b"],
    )
    assert result.exit_code == 2
    assert "owner/name" in result.output


def test_issue_command_writes_the_number_and_raised_ids(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = f"{RAISED_MARKER} 5 2 -->"
    gh = _Gh([3], {3: [{"author": {"login": "github-actions"}, "body": body}]})
    find, read = ai_candidates.candidates_issue, ai_candidates.issue_comments
    monkeypatch.setattr(ai_candidates, "candidates_issue", lambda repo: find(repo, runner=gh))
    monkeypatch.setattr(ai_candidates, "issue_comments", lambda repo: read(repo, runner=gh))
    issue_out, raised_out = tmp_path / "issue.txt", tmp_path / "raised.json"
    result = CliRunner().invoke(
        app,
        [
            "ai-candidates-issue",
            "--repo",
            "o/r",
            "--issue-out",
            str(issue_out),
            "--raised-out",
            str(raised_out),
        ],
    )

    assert result.exit_code == 0, result.output
    assert issue_out.read_text() == "3\n"
    assert json.loads(raised_out.read_text()) == [2, 5]
