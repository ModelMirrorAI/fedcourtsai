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
import yaml
from typer.testing import CliRunner

import fedcourtsai.cli as cli_module
from fedcourtsai import corpus, provision
from fedcourtsai.courtlistener import CourtListenerClient, RateLimiter, default_rate_limiter
from fedcourtsai.pipeline import decision_below
from fedcourtsai.pipeline.decision_below import (
    MAX_ENTRY_DOCKETS,
    MAX_ENTRY_PAGES,
    MAX_FILL_CASES,
    MAX_LOWER_NUMBERS,
    MAX_OPINIONS,
    MAX_REQUESTS_PER_CASE,
    MAX_SAMPLE,
    CaseInput,
    LowerCourtFacts,
    appellate_core,
    docket_document,
    facts_for_row,
    fill_candidates,
    fill_decision_below,
    lower_court_facts,
    match_case,
    match_cases,
    number_names,
    opinion_document,
    read_entry,
    read_rehearing,
    sample_rows,
    split_lower_numbers,
    unmapped_class,
)
from tests.workflow_argv import command_argv

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


def test_read_entry_ignores_a_motion_about_the_time_to_petition() -> None:
    extension = read_entry(
        "ORDER granting motion for extension of time to file petition for rehearing en banc."
    )
    assert not (extension.petition or extension.granted or extension.denied)
    extended = read_entry("Time to file petition for rehearing en banc extended to 05/01/2025.")
    assert not (extended.petition or extended.granted or extended.denied)


def test_read_entry_reads_a_disposition_stated_on_the_phrase() -> None:
    # A mandate entry recites the petition it follows; the denial still reads.
    mandate = read_entry("MANDATE ISSUED. Petition for rehearing en banc denied.")
    assert mandate.denied and not mandate.petition
    ordered = read_entry("Rehearing en banc is ordered.")
    assert ordered.granted and not ordered.denied


def _entries(*descriptions: str) -> list[tuple[int, Mapping[str, Any]]]:
    return [
        (11, {"entry_number": 40 + n, "date_filed": "2025-04-20", "description": d})
        for n, d in enumerate(descriptions)
    ]


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
    assert reading.complete is True
    assert reading.petition_filed is True
    assert reading.disposition == "denied"
    assert reading.dissent_noted is True
    assert [(c.entry_number, c.date_filed) for c in reading.cites] == [
        (41, date(2025, 4, 23)),
        (45, date(2025, 6, 2)),
    ]


def test_read_rehearing_says_no_only_after_a_complete_read() -> None:
    quiet = _entries("Letter filed.", "Bill of costs filed.")
    assert read_rehearing(quiet, complete=True).petition_filed is False
    partial = read_rehearing(quiet, complete=False)
    assert partial.petition_filed is None
    assert partial.complete is False
    # A positive reading stands either way; a missing dissent does not.
    denied = _entries("ORDER denying petition for rehearing en banc.")
    assert read_rehearing(denied, complete=False).petition_filed is True
    assert read_rehearing(denied, complete=False).dissent_noted is None
    assert read_rehearing(denied, complete=True).dissent_noted is False


def test_read_rehearing_with_no_entries_answers_unknown_not_no() -> None:
    reading = read_rehearing([], complete=True)
    assert reading.entries_read == 0
    assert reading.petition_filed is None
    assert reading.disposition is None


# --- the join --------------------------------------------------------------------


class _Upstream:
    """Canned CourtListener v4 payloads, served by path and query.

    ``cluster_pages`` answers the cluster list by ``(docket__court,
    docket__docket_number)``, applying its ``date_filed__lte`` filter unless
    ``ignore_date_filter`` says the filter was not applied upstream.
    """

    def __init__(  # noqa: PLR0913 - one canned answer per endpoint and fault
        self,
        *,
        dockets_by_number: Mapping[tuple[str, str], list[dict[str, Any]]] | None = None,
        dockets_by_core: Mapping[tuple[str, str], list[dict[str, Any]]] | None = None,
        cluster_pages: Mapping[tuple[str, str], list[dict[str, Any]]] | None = None,
        cluster_next: bool = False,
        ignore_date_filter: bool = False,
        opinions: Mapping[int, dict[str, Any]] | None = None,
        entries: Mapping[int, list[dict[str, Any]]] | None = None,
        entries_status: int = 200,
        entries_next: bool = False,
    ) -> None:
        self.by_number = dockets_by_number or {}
        self.by_core = dockets_by_core or {}
        self.cluster_pages = cluster_pages or {}
        self.cluster_next = cluster_next
        self.ignore_date_filter = ignore_date_filter
        self.opinions = opinions or {}
        self.entries = entries or {}
        self.entries_status = entries_status
        self.entries_next = entries_next
        self.requests: list[httpx.Request] = []

    @staticmethod
    def _page(rows: list[dict[str, Any]], more: bool) -> httpx.Response:
        nxt = "https://www.courtlistener.com/api/rest/v4/next/" if more else None
        return httpx.Response(200, json={"count": len(rows), "next": nxt, "results": rows})

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
            return self._page(rows, False)
        if parts[-1] == "clusters":
            key = (params.get("docket__court", ""), params.get("docket__docket_number", ""))
            rows = list(self.cluster_pages.get(key, []))
            bound = params.get("date_filed__lte")
            if bound and not self.ignore_date_filter:
                rows = [r for r in rows if r["date_filed"] <= bound]
            return self._page(rows, self.cluster_next)
        if parts[-1] == "docket-entries":
            if self.entries_status != 200:
                return httpx.Response(self.entries_status, json={"detail": "refused"})
            docket = int(params["docket"])
            rows = self.entries.get(docket, [])
            # Upstream pages entries by cursor: the next link re-asks for the
            # same docket with a cursor token.
            since = params.get("date_filed__gte")
            echo = f"&date_filed__gte={since}" if since else ""
            nxt = f"{_BASE}docket-entries/?cursor=c{len(self.requests)}&docket={docket}{echo}"
            return httpx.Response(
                200,
                json={
                    "count": len(rows),
                    "next": nxt if self.entries_next else None,
                    "results": rows,
                },
            )
        resource, ident = parts[-2], int(parts[-1])
        if resource != "opinions" or ident not in self.opinions:
            return httpx.Response(404, json={"detail": "Not found."})
        return httpx.Response(200, json=self.opinions[ident])


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


def _docket(ident: int, number: str = "24-50496", **extra: Any) -> dict[str, Any]:
    return {
        "id": ident,
        "court": _link("courts", "ca5"),
        "court_id": "ca5",
        "docket_number": number,
        "case_name": "Doe v. Roe",
        "panel_str": "",
        "clusters": [],
        **extra,
    }


def _cluster(
    ident: int, filed: str, *, docket: int = 11, opinions: Sequence[int] = ()
) -> dict[str, Any]:
    return {
        "id": ident,
        "docket": _link("dockets", docket),
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

_POST_JUDGMENT = [
    {
        "entry_number": 41,
        "date_filed": "2025-04-23",
        "description": "PETITION for rehearing en banc filed.",
    },
    {
        "entry_number": 45,
        "date_filed": "2025-06-02",
        "description": "ORDER denying petition for rehearing en banc. Judge Ho, " + "dissenting.",
    },
]


def _matched_upstream(**overrides: Any) -> _Upstream:
    kwargs: dict[str, Any] = {
        "dockets_by_number": {("ca5", "24-50496"): [_docket(11)]},
        "cluster_pages": {
            ("ca5", "24-50496"): [
                _cluster(500, "2025-04-09", opinions=[900]),
                # An earlier order on the same docket, dated before the judgment.
                _cluster(501, "2024-11-01"),
            ]
        },
        "opinions": {900: _OPINION},
        "entries": {11: _POST_JUDGMENT},
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
    assert on_date[0].docket_id == 11
    assert on_date[0].judges == "Smith, Ho, Oldham"
    assert on_date[0].panel_links == 3
    (opinion,) = on_date[0].opinions
    assert opinion.has_download_url and opinion.has_local_file and opinion.has_plain_text
    # The earlier cluster is reported but its opinions are not read.
    assert [c.opinions for c in found.clusters if not c.on_judgment_date] == [[]]
    assert found.clusters_truncated is False
    assert found.rehearing is not None
    assert found.rehearing.complete is True
    assert found.rehearing.disposition == "denied"
    assert found.rehearing.dissent_noted is True
    # docket list, cluster list, one opinion, one page of entries.
    assert found.requests == 4 == len(upstream.requests)
    clusters_request = upstream.requests[1]
    assert clusters_request.url.params["date_filed__lte"] == "2025-07-28"
    assert upstream.requests[-1].url.params["date_filed__gte"] == "2025-04-09"
    # The opinion text is not carried into the report.
    assert "Fifth Circuit ..." not in found.model_dump_json()


def test_match_case_falls_back_to_the_core_for_a_four_digit_year() -> None:
    row = {**_docket(21, "25-1812"), "court_id": "cafc", "court": _link("courts", 0)}
    upstream = _Upstream(
        dockets_by_core={("cafc", "25001812"): [row]},
        cluster_pages={("cafc", "25-1812"): [_cluster(700, "2025-04-09", docket=21)]},
    )
    facts = _facts(
        LowerCourt="United States Court of Appeals for the Federal Circuit",
        LowerCourtCaseNumbers="(2025-1812)",
    )
    with _client(upstream) as client:
        found = match_case(client, facts)
    assert [d.docket_id for d in found.dockets] == [21]
    assert found.status == "matched"
    asked = [dict(r.url.params) for r in upstream.requests if r.url.path.endswith("/dockets/")]
    assert asked == [
        {"court": "cafc", "docket_number": "2025-1812"},
        {"court": "cafc", "docket_number_core": "25001812"},
    ]
    # The cluster list asks by the number the checked row carries.
    (clusters,) = [r for r in upstream.requests if r.url.path.endswith("/clusters/")]
    assert clusters.url.params["docket__docket_number"] == "25-1812"


def test_match_case_drops_a_row_in_another_court_or_under_another_number() -> None:
    foreign_court = {**_docket(31), "court_id": "ca9", "court": _link("courts", 0)}
    foreign_number = _docket(32, "24-50497")
    upstream = _Upstream(dockets_by_number={("ca5", "24-50496"): [foreign_court, foreign_number]})
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.status == "no_docket"
    assert found.dockets == []


def test_match_case_ignores_a_cluster_dated_after_the_docketing() -> None:
    # Upstream ignoring the date filter must not let a later cluster in.
    upstream = _Upstream(
        dockets_by_number={("ca5", "24-50496"): [_docket(11)]},
        cluster_pages={
            ("ca5", "24-50496"): [_cluster(600, "2025-09-01"), _cluster(601, "2025-03-01")]
        },
        ignore_date_filter=True,
    )
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.status == "no_cluster_on_date"
    assert [c.cluster_id for c in found.clusters] == [601]


def test_match_case_drops_a_cluster_on_a_row_it_did_not_check() -> None:
    upstream = _matched_upstream(
        cluster_pages={("ca5", "24-50496"): [_cluster(500, "2025-04-09", docket=99)]}
    )
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.status == "no_cluster"
    assert found.clusters == []


def test_match_case_follows_no_link_off_the_api() -> None:
    cluster = _cluster(500, "2025-04-09")
    cluster["sub_opinions"] = ["https://evil.test/api/rest/v4/opinions/900/"]
    upstream = _matched_upstream(cluster_pages={("ca5", "24-50496"): [cluster]})
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.status == "matched"
    assert found.clusters[0].opinions == []
    assert all(r.url.host == "www.courtlistener.com" for r in upstream.requests)
    assert not any("/opinions/" in r.url.path for r in upstream.requests)


def test_match_case_flags_a_cluster_list_past_one_page() -> None:
    upstream = _matched_upstream(cluster_next=True)
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.clusters_truncated is True


@pytest.mark.parametrize("status", [403, 404, 500])
def test_a_fault_on_the_entries_leaves_the_match_and_says_why(status: int) -> None:
    upstream = _matched_upstream(entries_status=status)
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.status == "matched"
    assert found.rehearing is not None
    assert found.rehearing.entries_read == 0
    assert found.rehearing.petition_filed is None
    assert found.rehearing.unavailable is not None
    assert str(status) in found.rehearing.unavailable


def test_a_throttle_on_the_entries_still_stops_the_batch() -> None:
    upstream = _matched_upstream(entries_status=429)
    with _client(upstream) as client:
        report = match_cases(client, [CaseInput(label="a", facts=_facts())])
    assert report.matches == []
    assert report.deferred == ["a"]


def test_entries_past_the_page_cap_leave_the_negatives_unknown() -> None:
    quiet = [{"entry_number": 50, "date_filed": "2025-05-01", "description": "Letter filed."}]
    upstream = _matched_upstream(entries={11: quiet}, entries_next=True)
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.rehearing is not None
    assert found.rehearing.complete is False
    assert found.rehearing.petition_filed is None
    entry_pages = [r for r in upstream.requests if r.url.path.endswith("/docket-entries/")]
    assert len(entry_pages) == MAX_ENTRY_PAGES


def test_rows_past_the_row_cap_leave_the_negatives_unknown() -> None:
    rows = [_docket(11 + n) for n in range(MAX_ENTRY_DOCKETS + 1)]
    quiet = [{"entry_number": 50, "date_filed": "2025-05-01", "description": "Letter filed."}]
    upstream = _matched_upstream(
        dockets_by_number={("ca5", "24-50496"): rows},
        entries={row["id"]: quiet for row in rows},
    )
    with _client(upstream) as client:
        found = match_case(client, _facts())
    assert found.rehearing is not None
    assert found.rehearing.complete is False
    assert found.rehearing.petition_filed is None


def test_no_judgment_date_skips_the_entries_and_says_so() -> None:
    upstream = _matched_upstream()
    with _client(upstream) as client:
        found = match_case(client, _facts(LowerCourtDecision=None))
    assert found.rehearing is not None
    assert found.rehearing.unavailable is not None
    assert "judgment date" in found.rehearing.unavailable
    assert not any(r.url.path.endswith("/docket-entries/") for r in upstream.requests)


def test_a_case_never_exceeds_the_worst_case_request_count() -> None:
    numbers = ", ".join(f"24-5049{n}" for n in range(5))
    rows = {
        ("ca5", f"24-5049{n}"): [_docket(10 + n, f"24-5049{n}")] for n in range(MAX_LOWER_NUMBERS)
    }
    pages = {
        ("ca5", f"24-5049{n}"): [
            _cluster(500 + n, "2025-04-09", docket=10 + n, opinions=[900, 901])
        ]
        for n in range(MAX_LOWER_NUMBERS)
    }
    upstream = _Upstream(
        dockets_by_number=rows,
        cluster_pages=pages,
        opinions={900: _OPINION, 901: {**_OPINION, "id": 901}},
        entries_next=True,
    )
    with _client(upstream) as client:
        found = match_case(client, _facts(LowerCourtCaseNumbers=f"({numbers})"))
    assert found.requests == len(upstream.requests) <= MAX_REQUESTS_PER_CASE
    assert sum(len(c.opinions) for c in found.clusters) == MAX_OPINIONS


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


def _always(status: int) -> CourtListenerClient:
    def answer(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"detail": "no"})

    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client = httpx.Client(base_url=_BASE, transport=httpx.MockTransport(answer))
    return client


@pytest.mark.parametrize(("status", "words"), [(429, "throttling"), (401, "credential")])
def test_match_cases_stops_at_a_batch_wall_and_defers_the_rest(status: int, words: str) -> None:
    cases = [
        CaseInput(label="unmapped", facts=_facts(LowerCourt="Supreme Court of Ohio")),
        CaseInput(label="a", facts=_facts()),
        CaseInput(label="b", facts=_facts()),
    ]
    with _always(status) as client:
        report = match_cases(client, cases)
    assert [m.status for m in report.matches] == ["unmapped_court"]
    assert report.stopped is not None and words in report.stopped
    assert report.deferred == ["a", "b"]


def test_match_cases_records_a_one_case_failure_and_continues() -> None:
    cases = [CaseInput(label="a", facts=_facts()), CaseInput(label="b", facts=_facts())]
    with _always(500) as client:
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
    result = CliRunner().invoke(cli_module.app, ["decision-below", "--docket", "25-100"])
    assert result.exit_code == 2
    assert "token" in result.output


def test_command_refuses_an_empty_request() -> None:
    result = CliRunner().invoke(cli_module.app, ["decision-below"])
    assert result.exit_code == 2


def test_command_caps_the_sample() -> None:
    too_many = str(MAX_SAMPLE + 1)
    result = CliRunner().invoke(cli_module.app, ["decision-below", "--sample", too_many])
    assert result.exit_code == 2
    assert str(MAX_SAMPLE) in result.output


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
    result = CliRunner().invoke(cli_module.app, ["decision-below", "--docket", "25-100"])
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


# --- the fill ------------------------------------------------------------------

_TODAY = date(2026, 10, 30)


def test_an_entry_filed_after_the_docketing_is_not_read() -> None:
    # A petition on remand, filed after the SCOTUS docketing, would tell a cell
    # what came of the petition; the reading stops at the docketing.
    later = {
        "entry_number": 60,
        "date_filed": "2025-09-15",
        "description": "PETITION for rehearing en banc filed on remand.",
    }
    undated = {"entry_number": 61, "description": "ORDER granting rehearing en banc."}
    upstream = _matched_upstream(entries={11: [*_POST_JUDGMENT, later, undated]})
    with _client(upstream) as client:
        found = match_case(client, _facts(), case_id="scotus/1")
    assert found.rehearing is not None
    assert found.rehearing.entries_read == 2
    assert [c.entry_number for c in found.rehearing.cites] == [41, 45]
    assert found.rehearing.disposition == "denied"


def _matched() -> tuple[decision_below.DecisionBelowMatch, dict[int, str]]:
    upstream = _matched_upstream()
    with _client(upstream) as client:
        walk = decision_below._Walk(client)
        found = decision_below._match(walk, _facts(), case_id="scotus/1")
    return found, walk.texts


def test_the_opinion_row_carries_the_text_on_the_judgment_date() -> None:
    found, texts = _matched()
    document = opinion_document(found, texts, today=_TODAY, char_cap=10_000)
    assert document is not None
    assert document.kind == "decision-below"
    assert document.case_id == "scotus/1"
    assert document.entry_date == "2025-04-09"
    assert document.url == "https://www.courtlistener.com/opinion/500/"
    assert document.text == _OPINION["plain_text"]
    assert document.truncated is False
    cut = opinion_document(found, texts, today=_TODAY, char_cap=20)
    assert cut is not None and cut.truncated and len(cut.text) == 20
    # No text upstream, or no match: no row.
    assert opinion_document(found, {}, today=_TODAY, char_cap=10_000) is None
    unmatched = found.model_copy(update={"status": "no_cluster_on_date"})
    assert opinion_document(unmatched, texts, today=_TODAY, char_cap=10_000) is None


def test_the_docket_row_records_the_en_banc_reading_and_its_entries() -> None:
    found, _ = _matched()
    document = docket_document(found, today=_TODAY)
    assert document is not None
    assert document.kind == "lower-court-docket"
    assert document.url == "https://www.courtlistener.com/docket/11/"
    # Dated by the latest entry the reading cites.
    assert document.entry_date == "2025-06-02"
    text = document.text
    assert "Case number(s): 24-50496" in text
    assert "Judgment below (SCOTUS docket): 2025-04-09" in text
    assert "judges: Smith, Ho, Oldham" in text
    assert "petition filed: yes" in text
    assert "disposition: denied" in text
    assert "dissent noted: yes" in text
    assert "entry 45 on docket 11, filed 2025-06-02" in text
    # No docket row found: nothing to record.
    bare = found.model_copy(update={"status": "no_docket", "dockets": []})
    assert docket_document(bare, today=_TODAY) is None


def _seeded(db: Path) -> None:
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
                )
            ],
        )
        corpus.upsert_snapshot(conn, "scotus/1", date(2025, 8, 1), _payload())


def test_an_applied_fill_stores_both_rows_and_stamps_the_case(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seeded(db)
    with corpus.connect(db) as conn, _client(_matched_upstream()) as client:
        row = corpus.get_row(conn, "scotus/1")
        assert row is not None
        dry = fill_decision_below(conn, client, [row], apply=False, today=_TODAY, char_cap=10_000)
        assert dry.stored == {"decision-below": 1, "lower-court-docket": 1}
        assert corpus.documents_for_case(conn, "scotus/1") == []
        stamped = corpus.get_row(conn, "scotus/1")
        assert stamped is not None and stamped.decision_below_attempted_at is None
    with corpus.connect(db) as conn, _client(_matched_upstream()) as client:
        row = corpus.get_row(conn, "scotus/1")
        assert row is not None
        applied = fill_decision_below(
            conn, client, [row], apply=True, today=_TODAY, char_cap=10_000
        )
        assert applied.counts == {"matched": 1}
        kinds = [d.kind for d in corpus.documents_for_case(conn, "scotus/1")]
        assert kinds == ["decision-below", "lower-court-docket"]
        stamped = corpus.get_row(conn, "scotus/1")
        assert stamped is not None and stamped.decision_below_attempted_at == _TODAY


def test_a_fill_stopped_at_a_wall_stamps_nothing(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    _seeded(db)
    with corpus.connect(db) as conn, _always(429) as client:
        row = corpus.get_row(conn, "scotus/1")
        assert row is not None
        report = fill_decision_below(conn, client, [row], apply=True, today=_TODAY, char_cap=10_000)
        assert report.stopped is not None and report.deferred == ["scotus/1"]
        again = corpus.get_row(conn, "scotus/1")
        assert again is not None and again.decision_below_attempted_at is None


def test_fill_candidates_order_and_exclusions(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    stale = date(2026, 9, 1)
    recent = date(2026, 10, 20)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/1", "25-10", originating_court="ca2"),
                _row("scotus/2", "25-20", originating_court="ca2"),
                _row("scotus/3", "25-5", originating_court="ca2", salience_selected=True),
                _row("scotus/4", "25-30", originating_court="ca2"),
                _row("scotus/5", "25-40", originating_court="ca2"),
                _row("scotus/6", "25-50", originating_court="ca2", date_cert_denied=recent),
                _row("scotus/7", "25-60", originating_court_name="Supreme Court of Ohio"),
                _row("scotus/8", "25-70", originating_court="ca2"),
                _row("scotus/9", "25-80", originating_court="ca2", merits_decided=recent),
            ],
        )
        corpus.stamp_decision_below_attempt(conn, "scotus/4", stale)
        corpus.stamp_decision_below_attempt(conn, "scotus/5", recent)
        corpus.stamp_decision_below_attempt(conn, "scotus/8", stale)
        corpus.upsert_documents(
            conn,
            [
                corpus.CaseDocument(
                    case_id="scotus/8",
                    kind="decision-below",
                    url="https://www.courtlistener.com/opinion/1/",
                    fetched_at=stale,
                    text="stored",
                )
            ],
        )
        picked = fill_candidates(
            conn, today=_TODAY, max_cases=MAX_FILL_CASES, priority=frozenset({"scotus/1"})
        )
        capped = fill_candidates(conn, today=_TODAY, max_cases=2)
    # Priority and salience first (newest first within), then never-attempted
    # newest first, then the stale re-attempt; a recent stamp, a denial, a merits
    # decision and a state court are not walked, and a stored opinion is settled.
    assert [r.case_id for r in picked.rows] == ["scotus/1", "scotus/3", "scotus/2", "scotus/4"]
    assert picked.settled == ["scotus/8"]
    assert [r.case_id for r in capped.rows] == ["scotus/3", "scotus/2"]
    assert capped.settled == []


def test_a_settled_case_is_re_stamped_with_no_request(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row("scotus/8", "25-70", originating_court="ca2")])
        corpus.stamp_decision_below_attempt(conn, "scotus/8", date(2026, 9, 1))
        upstream = _Upstream()
        with _client(upstream) as client:
            report = fill_decision_below(
                conn, client, [], apply=True, today=_TODAY, char_cap=10, settled=["scotus/8"]
            )
        row = corpus.get_row(conn, "scotus/8")
    assert report.requests == 0 and upstream.requests == []
    assert row is not None and row.decision_below_attempted_at == _TODAY


def test_neither_fill_kind_reaches_a_cell_until_released() -> None:
    documents = [
        corpus.CaseDocument(
            case_id="scotus/1",
            kind=kind,
            url="https://www.courtlistener.com/opinion/1/",
            fetched_at=_TODAY,
            text="x",
        )
        for kind in ("decision-below", "lower-court-docket", "petition")
    ]
    kept = provision.documents_for_moment(documents, "evt-petition-disposition")
    assert [d.kind for d in kept] == ["petition"]


def test_the_fill_command_stores_a_named_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "corpus"
    root.mkdir()
    _seeded(corpus.corpus_db_path(root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_COURTLISTENER_API_TOKEN", "test-token")
    monkeypatch.setattr(cli_module, "_client", lambda: _client(_matched_upstream()))
    result = CliRunner().invoke(
        cli_module.app, ["enrich-decision-below", "--apply", "--case", "scotus/1"]
    )
    assert result.exit_code == 0, result.output
    assert "stored 1 decision-below, 1 lower-court-docket" in result.output
    assert "test-token" not in result.output
    with corpus.connect(corpus.corpus_db_path(root)) as conn:
        assert len(corpus.documents_for_case(conn, "scotus/1")) == 2


def test_the_fill_command_caps_the_walk() -> None:
    result = CliRunner().invoke(
        cli_module.app, ["enrich-decision-below", "--max-cases", str(MAX_FILL_CASES + 1)]
    )
    assert result.exit_code == 2


_WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"


def _step(workflow: str, job: str, predicate: Any) -> Mapping[str, Any]:
    wf = yaml.safe_load((_WORKFLOWS / workflow).read_text())
    return next(s for s in wf["jobs"][job]["steps"] if predicate(s))


@pytest.mark.parametrize(
    ("workflow", "job", "program", "expected"),
    [
        (
            "run-pull.yml",
            "live",
            (".venv/bin/fedcourts",),
            ["enrich-decision-below", "--apply", "--max-cases", "6"],
        ),
        (
            "run-analytics.yml",
            "decision-below",
            ("uv", "run", "fedcourts"),
            ["enrich-decision-below", "--max-cases", "25"],
        ),
    ],
)
def test_the_workflows_run_the_fill_with_flags_the_cli_accepts(
    workflow: str, job: str, program: tuple[str, ...], expected: list[str]
) -> None:
    """Both call sites are shell strings no Python check reaches, so a renamed
    flag would surface as a usage error in the job. Click validates every option
    before `--help` fires, so the parse is the check."""
    step = _step(workflow, job, lambda s: "enrich-decision-below" in str(s.get("run") or ""))
    calls = command_argv(step["run"], program)
    assert calls == [expected]
    result = CliRunner().invoke(cli_module.app, [*calls[0], "--help"])
    assert result.exit_code == 0, result.output


def test_the_live_fill_runs_on_the_opinion_steps_windows_and_tolerates_failure() -> None:
    """The fill spends CourtListener budget, so it runs on exactly the four full
    live windows the awaiting-grading step does, and like that step it can never
    fail the live pull whose facts the push and commit carry."""
    fill = _step("run-pull.yml", "live", lambda s: s.get("id") == "enrich-decision-below")
    opinion = _step("run-pull.yml", "live", lambda s: s.get("id") == "enrich-awaiting")
    assert fill["if"] == opinion["if"]
    assert fill["continue-on-error"] is True
    assert "FEDCOURTS_COURTLISTENER_API_TOKEN" in fill["env"]
