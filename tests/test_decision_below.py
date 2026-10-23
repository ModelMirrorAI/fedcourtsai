"""The decision-below join: a SCOTUS petition's lower-court ruling on CourtListener.

Every test is offline: the client's transport is an ``httpx.MockTransport``
routing on the request path and query, so the join exercises the real client
(its governor, its retries, its path construction) with no network. The
payloads are trimmed to the fields CourtListener's v4 serializers carry.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

import fedcourtsai.cli as cli_module
from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.courtlistener import CourtListenerClient, RateLimiter, default_rate_limiter
from fedcourtsai.pipeline.decision_below import (
    CaseInput,
    LowerCourtFacts,
    appellate_core,
    facts_for_row,
    lower_court_facts,
    match_case,
    match_cases,
    number_names,
    read_entry,
    read_rehearing,
    sample_rows,
    split_lower_numbers,
    unmapped_class,
)

_BASE = "https://www.courtlistener.com/api/rest/v4/"
_JUDGMENT = date(2025, 4, 9)
_DOCKETED = date(2025, 7, 28)


def _link(resource: str, ident: int | str) -> str:
    return f"{_BASE}{resource}/{ident}/"


def _payload(**overrides: Any) -> dict[str, Any]:
    """A supremecourt.gov cert docket JSON, trimmed to the lower-court fields."""
    payload: dict[str, Any] = {
        "CaseNumber": "25-100 ",
        "DocketedDate": "July 28, 2025",
        "LowerCourt": "United States Court of Appeals for the Fifth Circuit",
        "LowerCourtCaseNumbers": "(24-50496)",
        "LowerCourtDecision": "April 9, 2025",
        "ProceedingsandOrder": [],
    }
    payload.update(overrides)
    return payload


def _facts(**overrides: Any) -> LowerCourtFacts:
    return lower_court_facts(_payload(**overrides))


# --- reading the SCOTUS docket ---------------------------------------------------


def test_lower_court_facts_reads_the_served_fields() -> None:
    facts = lower_court_facts(
        _payload(
            LowerCourtCaseNumbers="(24-812, 24-901, 24-2901)",
            LowerCourtRehearingDenied="September 2, 2025",
        )
    )
    assert facts.scotus_docket_number == "25-100"
    assert facts.scotus_docketed == _DOCKETED
    assert facts.court_id == "ca5"
    assert facts.docket_numbers == ["24-812", "24-901", "24-2901"]
    assert facts.judgment_date == _JUDGMENT
    assert facts.rehearing_denied == date(2025, 9, 2)


def test_lower_court_facts_tolerates_absent_and_unparseable_values() -> None:
    facts = lower_court_facts({"LowerCourt": "  ", "LowerCourtDecision": "sometime"})
    assert facts.court_name is None
    assert facts.court_id is None
    assert facts.docket_numbers == []
    assert facts.judgment_date is None


def test_split_lower_numbers_keeps_order_and_drops_duplicates() -> None:
    assert split_lower_numbers("(2025-1812, 2025-1813)") == ["2025-1812", "2025-1813"]
    assert split_lower_numbers("(21-1; 21-1; 21-2)") == ["21-1", "21-2"]
    assert split_lower_numbers(None) == []


@pytest.mark.parametrize(
    ("number", "core"),
    [
        ("24-50496", "24050496"),
        # A four-digit year folds to the two-digit core, as upstream's rule does.
        ("2025-1812", "25001812"),
        ("No. 24\N{EN DASH}50496", "24050496"),
        ("130596", None),
    ],
)
def test_appellate_core_mirrors_upstreams_rule(number: str, core: str | None) -> None:
    assert appellate_core(number) == core


def test_number_names_accepts_either_spelling_and_nothing_else() -> None:
    assert number_names("25-1812", "2025-1812")
    assert number_names("No. 24-50496", "24-50496")
    assert not number_names("24-50497", "24-50496")
    assert not number_names(None, "24-50496")


@pytest.mark.parametrize(
    ("name", "label"),
    [
        ("Supreme Court of Illinois", "state court"),
        ("District Court of Appeals of Florida, Sixth District", "state court"),
        ("Court of Appeals of Arizona, Division Two", "state court"),
        (
            "United States Court of Appeals for the Armed Forces",
            "military or specialized federal court",
        ),
        ("United States District Court for the District of Columbia", "federal district court"),
        ("Tribunal of Somewhere", "unrecognized tribunal"),
    ],
)
def test_unmapped_class_names_the_kind_of_court(name: str, label: str) -> None:
    assert unmapped_class(name) == label


# --- the rehearing reading -------------------------------------------------------


def test_read_entry_tells_a_petition_from_its_disposition() -> None:
    petition = read_entry("PETITION for rehearing en banc filed by Appellant Jane Doe.")
    assert petition.petition and not petition.denied
    denial = read_entry(
        "ORDER denying petition for rehearing en banc. Judge Ho dissents from the denial."
    )
    assert denial.denied and denial.dissent and not denial.petition
    granted = read_entry("ORDER granting rehearing en banc. The panel opinion is vacated.")
    assert granted.granted and not granted.denied
    panel_only = read_entry("ORDER denying petition for panel rehearing.")
    assert not (panel_only.petition or panel_only.denied or panel_only.granted)


def test_read_rehearing_cites_the_entries_that_set_it() -> None:
    entries = [
        (11, {"entry_number": 40, "date_filed": "2025-04-20", "description": "Letter filed."}),
        (
            11,
            {
                "entry_number": 41,
                "date_filed": "2025-04-23",
                "description": "PETITION for rehearing en banc filed.",
            },
        ),
        (
            11,
            {
                "entry_number": 45,
                "date_filed": "2025-06-02",
                "description": "",
                "recap_documents": [
                    {"description": "ORDER denying rehearing en banc; Judge Ho dissenting."}
                ],
            },
        ),
    ]
    reading = read_rehearing(entries)
    assert reading.entries_read == 3
    assert reading.petition_filed is True
    assert reading.disposition == "denied"
    assert reading.dissent_noted is True
    assert [(c.entry_number, c.date_filed) for c in reading.cites] == [
        (41, date(2025, 4, 23)),
        (45, date(2025, 6, 2)),
    ]


def test_read_rehearing_with_no_entries_answers_unknown_not_no() -> None:
    reading = read_rehearing([])
    assert reading.entries_read == 0
    assert reading.petition_filed is None
    assert reading.disposition is None


# --- the join --------------------------------------------------------------------


class _Upstream:
    """Canned CourtListener v4 payloads, served by path and query."""

    def __init__(
        self,
        *,
        dockets_by_number: Mapping[tuple[str, str], list[dict[str, Any]]] | None = None,
        dockets_by_core: Mapping[tuple[str, str], list[dict[str, Any]]] | None = None,
        clusters: Mapping[int, dict[str, Any]] | None = None,
        opinions: Mapping[int, dict[str, Any]] | None = None,
        entries: Mapping[int, list[dict[str, Any]]] | None = None,
        entries_status: int = 200,
    ) -> None:
        self.by_number = dockets_by_number or {}
        self.by_core = dockets_by_core or {}
        self.clusters = clusters or {}
        self.opinions = opinions or {}
        self.entries = entries or {}
        self.entries_status = entries_status
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        params = request.url.params
        parts = request.url.path.strip("/").split("/")
        if parts[-1] == "dockets":
            court = params.get("court", "")
            if "docket_number_core" in params:
                rows = self.by_core.get((court, params["docket_number_core"]), [])
            else:
                rows = self.by_number.get((court, params.get("docket_number", "")), [])
            return httpx.Response(200, json={"count": len(rows), "next": None, "results": rows})
        if parts[-1] == "docket-entries":
            if self.entries_status != 200:
                return httpx.Response(self.entries_status, json={"detail": "refused"})
            rows = self.entries.get(int(params["docket"]), [])
            return httpx.Response(200, json={"count": len(rows), "next": None, "results": rows})
        resource, ident = parts[-2], int(parts[-1])
        table = {"clusters": self.clusters, "opinions": self.opinions}[resource]
        if ident not in table:
            return httpx.Response(404, json={"detail": "Not found."})
        return httpx.Response(200, json=table[ident])


def _client(handler: _Upstream, limiter: RateLimiter | None = None) -> CourtListenerClient:
    client = CourtListenerClient(
        rate_limiter=limiter or default_rate_limiter(10_000, 10_000, 10_000)
    )
    client._client = httpx.Client(base_url=_BASE, transport=httpx.MockTransport(handler))
    return client


@pytest.fixture(autouse=True)
def _no_backoff_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make tenacity's between-retry backoff instant so tests don't really sleep."""
    get: Any = CourtListenerClient._get
    monkeypatch.setattr(get.retry, "sleep", lambda _seconds: None)


def _docket(
    ident: int, number: str = "24-50496", *, clusters: Sequence[int] = (), **extra: Any
) -> dict[str, Any]:
    return {
        "id": ident,
        "court": _link("courts", "ca5"),
        "court_id": "ca5",
        "docket_number": number,
        "case_name": "Doe v. Roe",
        "panel_str": "",
        "clusters": [_link("clusters", c) for c in clusters],
        **extra,
    }


def _cluster(ident: int, filed: str, *, opinions: Sequence[int] = ()) -> dict[str, Any]:
    return {
        "id": ident,
        "date_filed": filed,
        "judges": "Smith, Ho, Oldham",
        "panel": [_link("people", 1), _link("people", 2), _link("people", 3)],
        "precedential_status": "Published",
        "sub_opinions": [_link("opinions", o) for o in opinions],
    }


_OPINION = {
    "id": 900,
    "type": "010combined",
    "author_str": "Ho",
    "per_curiam": False,
    "joined_by_str": "",
    "download_url": "https://www.ca5.uscourts.gov/opinions/pub/24/24-50496-CV0.pdf",
    "local_path": "pdf/2025/04/09/doe_v._roe.pdf",
    "plain_text": "United States Court of Appeals for the Fifth Circuit ...",
}


def _matched_upstream(**overrides: Any) -> _Upstream:
    kwargs: dict[str, Any] = {
        "dockets_by_number": {("ca5", "24-50496"): [_docket(11, clusters=[500, 501])]},
        "clusters": {
            500: _cluster(500, "2025-04-09", opinions=[900]),
            # An earlier order on the same docket, dated before the judgment.
            501: _cluster(501, "2024-11-01"),
        },
        "opinions": {900: _OPINION},
        "entries": {
            11: [
                {
                    "entry_number": 41,
                    "date_filed": "2025-04-23",
                    "description": "PETITION for rehearing en banc filed.",
                },
                {
                    "entry_number": 45,
                    "date_filed": "2025-06-02",
                    "description": "ORDER denying petition for rehearing en banc. Judge Ho, "
                    + "dissenting.",
                },
            ]
        },
    }
    kwargs.update(overrides)
    return _Upstream(**kwargs)


def test_match_case_finds_the_cluster_on_the_judgment_date() -> None:
    upstream = _matched_upstream()
    with _client(upstream) as client:
        found = match_case(client, _facts(), case_id="scotus/1")
    assert found.status == "matched"
    assert [d.docket_id for d in found.dockets] == [11]
    on_date = [c for c in found.clusters if c.on_judgment_date]
    assert [c.cluster_id for c in on_date] == [500]
    assert on_date[0].judges == "Smith, Ho, Oldham"
    assert on_date[0].panel_links == 3
    (opinion,) = on_date[0].opinions
    assert opinion.has_download_url and opinion.has_local_file and opinion.has_plain_text
    # The earlier cluster is reported but its opinions are not read.
    assert [c.opinions for c in found.clusters if not c.on_judgment_date] == [[]]
    assert found.rehearing is not None
    assert found.rehearing.disposition == "denied"
    assert found.rehearing.dissent_noted is True
    # docket list, two clusters, one opinion, one page of entries.
    assert found.requests == 5 == len(upstream.requests)
    entries_request = upstream.requests[-1]
    assert entries_request.url.params["date_filed__gte"] == "2025-04-09"
    # The opinion text is not carried into the report.
    assert "Fifth Circuit ..." not in found.model_dump_json()


def test_match_case_falls_back_to_the_core_for_a_four_digit_year() -> None:
    upstream = _Upstream(
        dockets_by_core={
            ("cafc", "25001812"): [
                {**_docket(21, "25-1812"), "court_id": "cafc", "court": _link("courts", 0)}
            ]
        }
    )
    facts = _facts(
        LowerCourt="United States Court of Appeals for the Federal Circuit",
        LowerCourtCaseNumbers="(2025-1812)",
    )
    with _client(upstream) as client:
        found = match_case(client, facts)
    assert [d.docket_id for d in found.dockets] == [21]
    assert found.status == "no_cluster"
    asked = [dict(r.url.params) for r in upstream.requests if r.url.path.endswith("/dockets/")]
    assert asked == [
        {"court": "cafc", "docket_number": "2025-1812"},
        {"court": "cafc", "docket_number_core": "25001812"},
    ]


def test_match_case_drops_a_row_in_another_court_or_under_another_number() -> None:
    foreign_court = {**_docket(31), "court_id": "ca9", "court": _link("courts", 0)}
    foreign_number = _docket(32, "24-50497")
    upstream = _Upstream(dockets_by_number={("ca5", "24-50496"): [foreign_court, foreign_number]})
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.status == "no_docket"
    assert found.dockets == []


def test_match_case_ignores_a_cluster_dated_after_the_docketing() -> None:
    upstream = _Upstream(
        dockets_by_number={("ca5", "24-50496"): [_docket(11, clusters=[600, 601])]},
        clusters={600: _cluster(600, "2025-09-01"), 601: _cluster(601, "2025-03-01")},
    )
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.status == "no_cluster_on_date"
    assert [c.cluster_id for c in found.clusters] == [601]


def test_match_case_follows_no_link_off_the_api() -> None:
    row = _docket(11)
    row["clusters"] = ["https://evil.test/api/rest/v4/clusters/500/"]
    upstream = _Upstream(dockets_by_number={("ca5", "24-50496"): [row]})
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.status == "no_cluster"
    assert all(r.url.host == "www.courtlistener.com" for r in upstream.requests)
    assert not any("/clusters/" in r.url.path for r in upstream.requests)


def test_refused_entries_leave_the_match_and_say_why() -> None:
    upstream = _matched_upstream(entries_status=403)
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.status == "matched"
    assert found.rehearing is not None
    assert found.rehearing.entries_read == 0
    assert found.rehearing.unavailable is not None
    assert "403" in found.rehearing.unavailable


def test_an_unmapped_court_spends_nothing() -> None:
    upstream = _Upstream()
    with _client(upstream) as client:
        found = match_case(client, _facts(LowerCourt="Supreme Court of Illinois"))
    assert found.status == "unmapped_court"
    assert found.reason.startswith("state court")
    assert upstream.requests == []


def test_a_docket_with_no_lower_court_spends_nothing() -> None:
    upstream = _Upstream()
    with _client(upstream) as client:
        found = match_case(client, _facts(LowerCourt=None, LowerCourtCaseNumbers=None))
    assert found.status == "no_lower_court"
    assert upstream.requests == []


def test_match_cases_stops_at_a_throttle_wall_and_defers_the_rest() -> None:
    def throttled(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"detail": "slow down"})

    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client = httpx.Client(base_url=_BASE, transport=httpx.MockTransport(throttled))
    cases = [
        CaseInput(label="unmapped", facts=_facts(LowerCourt="Supreme Court of Ohio")),
        CaseInput(label="a", facts=_facts()),
        CaseInput(label="b", facts=_facts()),
    ]
    with client:
        report = match_cases(client, cases)
    assert [m.status for m in report.matches] == ["unmapped_court"]
    assert report.stopped is not None and "throttling" in report.stopped
    assert report.deferred == ["a", "b"]


def test_match_cases_records_a_one_case_failure_and_continues() -> None:
    def broken(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "upstream fault"})

    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client = httpx.Client(base_url=_BASE, transport=httpx.MockTransport(broken))
    cases = [CaseInput(label="a", facts=_facts()), CaseInput(label="b", facts=_facts())]
    with client:
        report = match_cases(client, cases)
    assert report.counts == {"failed": 2}
    assert report.stopped is None
    assert all(m.requests >= 1 for m in report.matches)


# --- the inputs ------------------------------------------------------------------


def _row(case_id: str, number: str, **extra: Any) -> corpus.CorpusRow:
    return corpus.CorpusRow(case_id=case_id, court="scotus", docket_number=number, **extra)


def test_facts_for_row_prefers_the_live_snapshot(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    "scotus/1",
                    "25-100",
                    originating_court="ca5",
                    originating_docket_number="24-50496",
                    date_filed=_DOCKETED,
                ),
                _row(
                    "scotus/2",
                    "25-101",
                    originating_court_name="United States Court of Appeals for the Ninth Circuit",
                    originating_docket_number="23-55501",
                ),
            ],
        )
        corpus.upsert_snapshot(conn, "scotus/1", date(2025, 8, 1), _payload())
        first, second = corpus.get_row(conn, "scotus/1"), corpus.get_row(conn, "scotus/2")
        assert first is not None and second is not None
        with_snapshot = facts_for_row(conn, first)
        without = facts_for_row(conn, second)
    assert with_snapshot.judgment_date == _JUDGMENT
    assert with_snapshot.court_id == "ca5"
    # The row's own linkage carries the court and number but no judgment date.
    assert without.court_id == "ca9"
    assert without.docket_numbers == ["23-55501"]
    assert without.judgment_date is None


def test_sample_rows_takes_the_newest_circuit_petitions(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/10", "24-900", originating_court="ca2"),
                _row("scotus/11", "25-5", originating_court="ca3"),
                _row("scotus/12", "25-40", originating_court_name="Supreme Court of Ohio"),
                _row("scotus/13", "25A12", originating_court="ca4"),
                _row(
                    "scotus/14",
                    "25-30",
                    originating_court_name="United States Court of Appeals for the Tenth Circuit",
                ),
            ],
        )
        picked = sample_rows(conn, 2)
    assert [r.case_id for r in picked] == ["scotus/14", "scotus/11"]


# --- the command -----------------------------------------------------------------


def test_command_refuses_to_run_without_a_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FEDCOURTS_COURTLISTENER_API_TOKEN", raising=False)
    result = CliRunner().invoke(app, ["decision-below", "--docket", "25-100"])
    assert result.exit_code == 2
    assert "token" in result.output


def test_command_refuses_an_empty_request() -> None:
    result = CliRunner().invoke(app, ["decision-below"])
    assert result.exit_code == 2


def test_command_matches_a_named_scotus_number(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Court:
        def __init__(self, **_: Any) -> None:
            pass

        def __enter__(self) -> _Court:
            return self

        def __exit__(self, *exc: object) -> None:
            return None

        def get_docket(self, term: int, serial: int) -> dict[str, Any] | None:
            assert (term, serial) == (25, 100)
            return _payload()

    upstream = _matched_upstream()
    monkeypatch.setenv("FEDCOURTS_COURTLISTENER_API_TOKEN", "test-token")
    monkeypatch.setattr(cli_module, "SupremeCourtClient", _Court)
    monkeypatch.setattr(cli_module, "_client", lambda: _client(upstream))
    result = CliRunner().invoke(app, ["decision-below", "--docket", "25-100"])
    assert result.exit_code == 0, result.output
    assert "1 of 1 matched" in result.output
    assert '"status": "matched"' in result.output
    # The token reaches the client through settings, never the report.
    assert "test-token" not in result.output


def test_a_body_that_is_not_an_object_fails_its_case_only() -> None:
    def listy(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=["not", "an", "object"])

    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client = httpx.Client(base_url=_BASE, transport=httpx.MockTransport(listy))
    cases = [CaseInput(label="a", facts=_facts()), CaseInput(label="b", facts=_facts())]
    with client:
        report = match_cases(client, cases)
    assert report.counts == {"failed": 2}
    assert all("not an object" in m.reason for m in report.matches)
