"""The opinion-cluster enrichment pass: cites and bodies for the merits track.

Every test is offline: the client's transport is an ``httpx.MockTransport``
routing on the request path, so the pass exercises the real client (its
governor, its retries, its path construction) with no network.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import pytest

from fedcourtsai import corpus
from fedcourtsai.courtlistener import (
    CourtListenerClient,
    RateBudgetExceeded,
    RateLimiter,
    default_rate_limiter,
)
from fedcourtsai.pipeline.opinion_enrichment import (
    OpinionEnrichmentResult,
    citation_strings,
    enrich_opinions,
    resource_id,
)

_BASE = "https://www.courtlistener.com/api/rest/v4/"
_BODY = "JUSTICE KAGAN delivered the opinion of the Court. The judgment is reversed."


def _link(resource: str, ident: int) -> str:
    return f"{_BASE}{resource}/{ident}/"


# --- the hyperlink guard -------------------------------------------------------


def test_resource_id_takes_a_well_formed_link() -> None:
    assert resource_id(_link("clusters", 4321), base_url=_BASE, resource="clusters") == 4321
    # A trailing slash is optional and surrounding whitespace is tolerated.
    assert resource_id(f"  {_BASE}opinions/9  ", base_url=_BASE, resource="opinions") == 9


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.test/api/rest/v4/clusters/1/",  # another host
        "http://www.courtlistener.com/api/rest/v4/clusters/1/",  # another scheme
        "https://www.courtlistener.com/api/rest/v3/clusters/1/",  # another API base
        "https://www.courtlistener.com/clusters/1/",  # outside the API path
        "https://www.courtlistener.com/api/rest/v4/opinions/1/",  # another resource
        "https://www.courtlistener.com/api/rest/v4/clusters/1/extra/",  # nested route
        "https://www.courtlistener.com/api/rest/v4/clusters/../dockets/1/",  # traversal
        "https://www.courtlistener.com/api/rest/v4/clusters/abc/",  # non-numeric id
        # A non-ASCII digit `int()` would happily parse.
        "https://www.courtlistener.com/api/rest/v4/clusters/\N{ARABIC-INDIC DIGIT ONE}/",
        "clusters/1/",  # relative
        "",
    ],
)
def test_resource_id_rejects_anything_off_the_api(url: str) -> None:
    assert resource_id(url, base_url=_BASE, resource="clusters") is None


def test_resource_id_rejects_a_non_string() -> None:
    assert resource_id({"id": 1}, base_url=_BASE, resource="clusters") is None
    assert resource_id(None, base_url=_BASE, resource="clusters") is None


def test_citation_strings_assembles_reporter_cites() -> None:
    payload = {
        "citations": [
            {"volume": 602, "reporter": "U.S.", "page": 137, "type": 1},
            {"volume": 144, "reporter": "S. Ct.", "page": 2244, "type": 2},
            {"volume": 602, "reporter": "U.S.", "page": 137, "type": 1},  # duplicate
            {"reporter": "", "volume": "", "page": ""},  # nothing to assemble
        ]
    }
    assert citation_strings(payload) == ["602 U.S. 137", "144 S. Ct. 2244"]


# --- the pass ------------------------------------------------------------------


class _Upstream:
    """Canned cluster/opinion/docket payloads, served by request path."""

    def __init__(
        self,
        *,
        clusters: Mapping[int, dict[str, Any]],
        opinions: Mapping[int, dict[str, Any]],
        dockets: Mapping[int, dict[str, Any]] | None = None,
    ) -> None:
        self.clusters = clusters
        self.opinions = opinions
        self.dockets = dockets or {}
        self.paths: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.paths.append(request.url.path)
        parts = request.url.path.strip("/").split("/")
        resource, ident = parts[-2], int(parts[-1])
        table: Mapping[int, dict[str, Any]] = {
            "clusters": self.clusters,
            "opinions": self.opinions,
            "dockets": self.dockets,
        }[resource]
        if ident not in table:
            return httpx.Response(404, json={"detail": "Not found."})
        return httpx.Response(200, json=table[ident])


def _client(
    handler: httpx.MockTransport, limiter: RateLimiter | None = None
) -> CourtListenerClient:
    """A client whose transport is mocked and whose limiter never throttles."""
    client = CourtListenerClient(
        rate_limiter=limiter or default_rate_limiter(10_000, 10_000, 10_000)
    )
    client._client = httpx.Client(base_url=_BASE, transport=handler)
    return client


@pytest.fixture(autouse=True)
def _no_backoff_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make tenacity's between-retry backoff instant so tests don't really sleep."""
    get: Any = CourtListenerClient._get
    monkeypatch.setattr(get.retry, "sleep", lambda _seconds: None)


def _row(case_id: str, **fields: object) -> corpus.CorpusRow:
    return corpus.CorpusRow.model_validate(
        {
            "case_id": case_id,
            "court": "scotus",
            "date_cert_granted": date(2024, 1, 8),
            **fields,
        }
    )


def _cluster(cluster_id: int, *, opinion_id: int, count: int = 12) -> dict[str, Any]:
    return {
        "id": cluster_id,
        "citations": [{"volume": 602, "reporter": "U.S.", "page": 137}],
        "citation_count": count,
        "sub_opinions": [_link("opinions", opinion_id)],
    }


def _seeded(tmp_path: Path) -> Path:
    """A corpus holding the four shapes the pass distinguishes.

    ``scotus/101`` is the ordinary case: granted, no opinion yet, and a stored
    snapshot linking its cluster. ``scotus/102`` is the same but unsnapshotted,
    so its cluster costs a docket fetch. ``scotus/103`` is already enriched
    (the idempotency key). ``scotus/104`` is an ungranted petition — outside the
    merits track entirely.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row("scotus/101"),
                _row("scotus/102"),
                _row("scotus/103", opinion_text="Already stored."),
                _row("scotus/104", date_cert_granted=None),
            ],
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/101",
            date(2024, 6, 1),
            {"id": 101, "clusters": [_link("clusters", 4321)]},
        )
    return db


def _upstream() -> _Upstream:
    return _Upstream(
        clusters={
            4321: _cluster(4321, opinion_id=8765),
            5555: _cluster(5555, opinion_id=9999, count=3),
        },
        opinions={
            8765: {"id": 8765, "plain_text": _BODY},
            9999: {"id": 9999, "plain_text": "The judgment is affirmed."},
        },
        dockets={102: {"id": 102, "clusters": [_link("clusters", 5555)]}},
    )


def _run(db: Path, upstream: _Upstream, **kwargs: Any) -> OpinionEnrichmentResult:
    with corpus.connect(db) as conn, _client(httpx.MockTransport(upstream)) as client:
        return enrich_opinions(conn, client, **kwargs)


def test_dry_run_reports_coverage_and_writes_nothing(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    result = _run(db, upstream, apply=False)

    assert result.applied is False
    # Only the two granted, opinion-less rows are eligible.
    assert result.eligible == 2 and result.considered == 2 and result.enriched == 2
    # The snapshotted case costs cluster+opinion; the unsnapshotted one also
    # pays a docket fetch to find its cluster.
    assert result.requests == 5
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/101")
    assert row is not None
    assert row.opinion_text is None and row.has_opinion is False and row.citations == []


def test_apply_lands_cites_body_and_the_presence_bit(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    result = _run(db, upstream, apply=True)

    assert result.applied is True and result.enriched == 2
    with corpus.connect(db) as conn:
        snapshotted = corpus.get_row(conn, "scotus/101")
        fetched = corpus.get_row(conn, "scotus/102")
        untouched = corpus.get_row(conn, "scotus/104")
    assert snapshotted is not None
    assert snapshotted.opinion_text == _BODY
    assert snapshotted.has_opinion is True
    assert snapshotted.citations == ["602 U.S. 137"]
    assert snapshotted.citation_count == 12
    assert fetched is not None and fetched.citation_count == 3
    assert untouched is not None and untouched.has_opinion is False


def test_snapshot_link_spares_the_docket_fetch(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    _run(db, upstream, apply=False)
    # The snapshotted case never hits `dockets/`; the unsnapshotted one must.
    assert upstream.paths == [
        "/api/rest/v4/clusters/4321/",
        "/api/rest/v4/opinions/8765/",
        "/api/rest/v4/dockets/102/",
        "/api/rest/v4/clusters/5555/",
        "/api/rest/v4/opinions/9999/",
    ]


def test_apply_is_idempotent(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    _run(db, _upstream(), apply=True)
    again = _run(db, _upstream(), apply=True)
    # Both rows now carry the presence bit, so nothing matches and nothing is spent.
    assert again.eligible == 0 and again.enriched == 0 and again.requests == 0


def test_max_cases_bounds_one_run(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    result = _run(db, upstream, apply=True, max_cases=1)
    assert result.eligible == 2 and result.considered == 1 and result.enriched == 1
    assert result.requests == 2
    with corpus.connect(db) as conn:
        deferred = corpus.get_row(conn, "scotus/102")
    assert deferred is not None and deferred.has_opinion is False


def test_a_docket_linking_no_cluster_is_counted_not_written(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    upstream.dockets = {102: {"id": 102, "clusters": []}}
    result = _run(db, upstream, apply=True)
    assert result.no_cluster == 1 and result.enriched == 1
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/102")
    assert row is not None and row.has_opinion is False


def test_a_link_off_the_api_is_not_followed(tmp_path: Path) -> None:
    """A snapshot naming another host falls back to the docket, never fetches it."""
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row("scotus/102")])
        corpus.upsert_snapshot(
            conn,
            "scotus/102",
            date(2024, 6, 1),
            {"id": 102, "clusters": ["https://evil.test/api/rest/v4/clusters/4321/"]},
        )
    upstream = _upstream()
    result = _run(db, upstream, apply=True)
    assert result.enriched == 1
    # The rejected link never became a request; the docket supplied the cluster.
    assert upstream.paths[0] == "/api/rest/v4/dockets/102/"
    assert not any(path.endswith("/clusters/4321/") for path in upstream.paths)


def test_a_body_less_opinion_still_lands_its_citations(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    upstream.opinions = {
        8765: {"id": 8765, "plain_text": "   "},
        9999: {"id": 9999, "plain_text": "The judgment is affirmed."},
    }
    result = _run(db, upstream, apply=True)
    assert result.no_body == 1 and result.enriched == 2
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/101")
    assert row is not None
    assert row.opinion_text is None and row.has_opinion is False
    assert row.citations == ["602 U.S. 137"]


def test_one_bad_docket_does_not_cost_the_run(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    upstream.clusters = {5555: _cluster(5555, opinion_id=9999, count=3)}  # 4321 now 404s
    result = _run(db, upstream, apply=True)
    assert result.enriched == 1
    assert [case_id for case_id, _ in result.failed] == ["scotus/101"]
    assert "404" in result.failed[0][1]
    with corpus.connect(db) as conn:
        survivor = corpus.get_row(conn, "scotus/102")
    assert survivor is not None and survivor.has_opinion is True


class _BudgetLimiter(RateLimiter):
    """Admits ``allow`` requests, then reports the window's budget spent."""

    def __init__(self, allow: int) -> None:
        super().__init__([(10_000, 60.0)], sleep_fn=lambda _: None)
        self.allow = allow
        self.calls = 0

    def acquire(self) -> None:
        self.calls += 1
        if self.calls > self.allow:
            raise RateBudgetExceeded("next request must wait 3000s, over the 300s bound")
        super().acquire()


def test_budget_exhaustion_stops_the_walk_and_keeps_what_landed(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    with (
        corpus.connect(db) as conn,
        _client(httpx.MockTransport(upstream), _BudgetLimiter(2)) as client,
    ):
        result = enrich_opinions(conn, client, apply=True)

    assert result.stopped is not None and "budget exhausted" in result.stopped
    assert result.deferred == ["scotus/102"]
    # The case completed before the wall is still written.
    assert result.enriched == 1
    with corpus.connect(db) as conn:
        landed = corpus.get_row(conn, "scotus/101")
        deferred = corpus.get_row(conn, "scotus/102")
    assert landed is not None and landed.opinion_text == _BODY
    assert deferred is not None and deferred.has_opinion is False


class _SpySink:
    """A mirror sink recording the rows an ``upsert_rows`` write re-mirrors."""

    def __init__(self) -> None:
        self.mirrored: list[str] = []

    def mirror_cases(self, rows: Sequence[corpus.CorpusRow]) -> None:
        self.mirrored.extend(row.case_id for row in rows)

    def mirror_snapshot(
        self, case_id: str, snapshot_date: date, payload: Mapping[str, Any]
    ) -> None: ...

    def mirror_documents_for_cases(
        self, conn: corpus.ReadConnection, case_ids: Iterable[str]
    ) -> None: ...

    def mirror_documents(self, documents: Sequence[corpus.CaseDocument]) -> None: ...

    def mirror_events_for_cases(
        self, conn: corpus.ReadConnection, case_ids: Iterable[str]
    ) -> None: ...


def test_the_write_re_mirrors_the_case(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The freshness invariant `casestore.read_opinion_text` rests on.

    Every opinion write must flow through `upsert_rows`, which re-mirrors the
    case's stored `case.json` — a direct `UPDATE` would leave the content store
    holding a body the index no longer matches.
    """
    db = _seeded(tmp_path)
    spy = _SpySink()
    monkeypatch.setitem(corpus._MIRROR, "sink", spy)
    _run(db, _upstream(), apply=True)
    assert sorted(spy.mirrored) == ["scotus/101", "scotus/102"]


def test_a_dry_run_never_mirrors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = _seeded(tmp_path)
    spy = _SpySink()
    monkeypatch.setitem(corpus._MIRROR, "sink", spy)
    _run(db, _upstream(), apply=False)
    assert spy.mirrored == []


def test_enrichment_survives_a_reingest_of_the_snapshot(tmp_path: Path) -> None:
    """A re-served docket cannot regress the presence bit.

    The body and cites take the incoming value on upsert, so a channel that
    carries neither clears them; the `has_opinion` max-latch is what keeps the
    case's coverage legible to the readers that OR on the bit.
    """
    db = _seeded(tmp_path)
    _run(db, _upstream(), apply=True)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row("scotus/101")])
        row = corpus.get_row(conn, "scotus/101")
    assert row is not None and row.has_opinion is True
