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
    MAX_OPINION_CHARS,
    OpinionEnrichmentResult,
    citation_strings,
    cluster_names_docket,
    enrich_opinions,
    is_separate_writing,
    resource_id,
)
from fedcourtsai.supremecourt import live_docket_id

_BASE = "https://www.courtlistener.com/api/rest/v4/"
_BODY = "JUSTICE KAGAN delivered the opinion of the Court. The judgment is reversed."


def _link(resource: str, ident: int) -> str:
    return f"{_BASE}{resource}/{ident}/"


# --- the hyperlink guard -------------------------------------------------------


def test_resource_id_takes_a_well_formed_link() -> None:
    assert resource_id(_link("clusters", 4321), base_url=_BASE, resource="clusters") == 4321
    # A trailing slash is optional and surrounding whitespace is tolerated.
    assert resource_id(f"  {_BASE}opinions/9  ", base_url=_BASE, resource="opinions") == 9
    # Hostnames are case-insensitive; everything else about the authority is not.
    upper = "https://WWW.CourtListener.com/api/rest/v4/clusters/4321/"
    assert resource_id(upper, base_url=_BASE, resource="clusters") == 4321


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.test/api/rest/v4/clusters/1/",  # another host
        "http://www.courtlistener.com/api/rest/v4/clusters/1/",  # another scheme
        "https://www.courtlistener.com/api/rest/v3/clusters/1/",  # another API base
        "https://www.courtlistener.com/clusters/1/",  # outside the API path
        "https://www.courtlistener.com/api/rest/v4/opinions/1/",  # another resource
        "https://user:pw@www.courtlistener.com/api/rest/v4/clusters/1/",  # userinfo
        "https://www.courtlistener.com:8443/api/rest/v4/clusters/1/",  # another port
        "https://www.courtlistener.com.evil.test/api/rest/v4/clusters/1/",  # suffix host
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


def _cluster(
    cluster_id: int, *, docket_id: int, opinion_id: int, count: int = 12
) -> dict[str, Any]:
    return {
        "id": cluster_id,
        "docket": _link("dockets", docket_id),
        "citations": [{"volume": 602, "reporter": "U.S.", "page": 137}],
        "citation_count": count,
        "sub_opinions": [_link("opinions", opinion_id)],
    }


def _seeded(tmp_path: Path) -> Path:
    """A corpus holding the five shapes the pass distinguishes.

    ``scotus/101`` is the ordinary case: granted, no opinion yet, and a stored
    REST-shaped snapshot linking its cluster. ``scotus/102`` is the same but
    unsnapshotted, so its cluster costs a docket fetch. ``scotus/103`` is
    already enriched (the idempotency key). ``scotus/104`` is an ungranted
    petition. The last is a granted live-first petition, whose reserved-range
    id addresses nothing upstream.
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
                _row(f"scotus/{live_docket_id(24, 900)}"),
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
            4321: _cluster(4321, docket_id=101, opinion_id=8765),
            5555: _cluster(5555, docket_id=102, opinion_id=9999, count=3),
        },
        opinions={
            8765: {"id": 8765, "type": "020lead", "plain_text": _BODY},
            9999: {"id": 9999, "type": "010combined", "plain_text": "The judgment is affirmed."},
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
    # Only the two granted, opinion-less, CourtListener-addressable rows are
    # eligible; the granted live-first petition is reported, never walked.
    assert result.eligible == 2 and result.considered == 2 and result.enriched == 2
    assert result.live_only == 1
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
        8765: {"id": 8765, "type": "020lead", "plain_text": "   "},
        9999: {"id": 9999, "type": "010combined", "plain_text": "The judgment is affirmed."},
    }
    result = _run(db, upstream, apply=True)
    assert result.no_body == 1 and result.enriched == 2
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/101")
    assert row is not None
    assert row.opinion_text is None and row.has_opinion is False
    assert row.citations == ["602 U.S. 137"]


def test_a_separate_writing_never_becomes_the_case_body(tmp_path: Path) -> None:
    """A dissent sitting first in `sub_opinions` yields no body, not the wrong one.

    `has_opinion` max-latches, so a body stored here is permanent — the row
    stops matching this pass's own predicate and no later run revisits it.
    """
    db = _seeded(tmp_path)
    upstream = _upstream()
    upstream.opinions = {
        8765: {"id": 8765, "type": "040dissent", "plain_text": "JUSTICE ALITO, dissenting."},
        9999: {"id": 9999, "type": "010combined", "plain_text": "The judgment is affirmed."},
    }
    result = _run(db, upstream, apply=True)
    assert result.no_body == 1
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/101")
    assert row is not None
    assert row.opinion_text is None and row.has_opinion is False
    assert row.citations == ["602 U.S. 137"]


@pytest.mark.parametrize(
    ("kind", "separate"),
    [
        ("010combined", False),
        ("020lead", False),
        ("025plurality", False),
        ("030concurrence", True),
        ("035concurrenceinpart", True),
        ("040dissent", True),
        ("050addendum", True),
        ("", False),
        (None, False),
    ],
)
def test_separate_writing_reads_the_type_vocabulary(kind: object, separate: bool) -> None:
    assert is_separate_writing({"type": kind}) is separate
    # An absent type is accepted rather than refused: an unknown shape must not
    # turn the whole population into a silent no-op.
    assert is_separate_writing({}) is False


def test_an_oversize_body_is_refused(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    upstream.opinions = {
        8765: {"id": 8765, "type": "020lead", "plain_text": "x" * (MAX_OPINION_CHARS + 1)},
        9999: {"id": 9999, "type": "010combined", "plain_text": "The judgment is affirmed."},
    }
    result = _run(db, upstream, apply=True)
    assert result.no_body == 1
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/101")
    assert row is not None and row.opinion_text is None


def test_several_clusters_are_refused_not_guessed_at(tmp_path: Path) -> None:
    """Nothing in a `clusters` list says which is the case's decision."""
    db = _seeded(tmp_path)
    upstream = _upstream()
    upstream.dockets = {
        102: {"id": 102, "clusters": [_link("clusters", 5555), _link("clusters", 4321)]}
    }
    result = _run(db, upstream, apply=True)
    assert result.ambiguous_cluster == 1 and result.enriched == 1
    # The ambiguity cost one docket fetch and no cluster fetch.
    assert not any(path.endswith("/clusters/5555/") for path in upstream.paths)
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/102")
    assert row is not None and row.has_opinion is False


def test_a_cluster_naming_another_docket_is_skipped(tmp_path: Path) -> None:
    """The link guard proves a cluster is on the API, not that it is this case's."""
    db = _seeded(tmp_path)
    upstream = _upstream()
    upstream.clusters = {
        4321: _cluster(4321, docket_id=999, opinion_id=8765),  # a different docket
        5555: _cluster(5555, docket_id=102, opinion_id=9999, count=3),
    }
    result = _run(db, upstream, apply=True)
    assert result.foreign_cluster == 1 and result.enriched == 1
    # The misjoined cluster's opinion was never fetched.
    assert not any(path.endswith("/opinions/8765/") for path in upstream.paths)
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/101")
    assert row is not None and row.citations == []


def test_a_cluster_naming_no_docket_is_accepted() -> None:
    # Fail-open on an absent field: refusing would make a served-shape change a
    # silent corpus-wide no-op, and the cluster came from this docket's own list.
    assert cluster_names_docket({}, base_url=_BASE, docket_id=101) is True
    assert cluster_names_docket({"docket": None}, base_url=_BASE, docket_id=101) is True
    assert (
        cluster_names_docket({"docket": _link("dockets", 101)}, base_url=_BASE, docket_id=101)
        is True
    )
    assert (
        cluster_names_docket({"docket": _link("dockets", 999)}, base_url=_BASE, docket_id=101)
        is False
    )


def test_a_non_json_response_costs_one_case(tmp_path: Path) -> None:
    """An HTML interstitial raises a ValueError the walk must not unwind on."""
    db = _seeded(tmp_path)

    def handle(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/clusters/4321/"):
            return httpx.Response(200, text="<html>maintenance</html>")
        return _upstream()(request)

    with corpus.connect(db) as conn, _client(httpx.MockTransport(handle)) as client:
        result = enrich_opinions(conn, client, apply=True)

    assert [entry["case_id"] for entry in result.failed] == ["scotus/101"]
    # The sibling case still converged, and its write survived the failure.
    assert result.enriched == 1
    with corpus.connect(db) as conn:
        row = corpus.get_row(conn, "scotus/102")
    assert row is not None and row.has_opinion is True


def test_enrichment_does_not_move_predict_scope(tmp_path: Path) -> None:
    """A raw-facts channel must not silently change what is predictable.

    `citations`, `citation_count`, and `has_opinion` are the three fields
    `is_published_opinion_unresolvable` keys on, so a well-formed in-scope
    granted docket is the case that proves the write is scope-neutral.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                _row(
                    "scotus/101",
                    docket_number="23-719",
                    case_name="Roe v. Doe",
                    date_filed=date(2023, 9, 1),
                    disposition="granted",
                )
            ],
        )
        corpus.upsert_snapshot(
            conn,
            "scotus/101",
            date(2024, 6, 1),
            {"id": 101, "clusters": [_link("clusters", 4321)]},
        )
        before = corpus.get_row(conn, "scotus/101")
        assert before is not None
        assert corpus.out_of_scope_reason_full(conn, before) is None
    _run(db, _upstream(), apply=True)
    with corpus.connect(db) as conn:
        after = corpus.get_row(conn, "scotus/101")
        assert after is not None
        assert after.has_opinion is True
        assert corpus.out_of_scope_reason_full(conn, after) is None


def test_one_bad_docket_does_not_cost_the_run(tmp_path: Path) -> None:
    db = _seeded(tmp_path)
    upstream = _upstream()
    # 4321 is gone from upstream, so the first case's cluster fetch 404s.
    upstream.clusters = {5555: _cluster(5555, docket_id=102, opinion_id=9999, count=3)}
    result = _run(db, upstream, apply=True)
    assert result.enriched == 1
    assert [entry["case_id"] for entry in result.failed] == ["scotus/101"]
    assert "404" in result.failed[0]["reason"]
    # The failed request is counted: an inspection of spend must include it.
    assert result.requests == 4
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


def test_persistent_throttling_stops_the_walk_and_defers_the_rest(tmp_path: Path) -> None:
    """A 429 the client's retries could not clear ends the pass, deferring, not failing.

    A throttle the retry cycle cannot clear is a quota wall (whichever window
    imposed it), so pressing on would burn every remaining case's retry cycle
    into the same wall. The case that hit it defers with the rest — nothing
    about it failed, and nothing latches — while what landed before is kept.
    """
    db = _seeded(tmp_path)
    upstream = _upstream()
    throttled_attempts = 0

    def throttled(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/dockets/102/"):
            nonlocal throttled_attempts
            throttled_attempts += 1
            return httpx.Response(429, json={"detail": "Request was throttled."})
        return upstream(request)

    with corpus.connect(db) as conn, _client(httpx.MockTransport(throttled)) as client:
        result = enrich_opinions(conn, client, apply=True)

    assert result.stopped is not None and "throttling" in result.stopped
    # The stop is post-retry, not first-sight: the client spent its full retry
    # cycle against the wall before the walk gave up.
    assert throttled_attempts == 4
    assert result.deferred == ["scotus/102"]
    assert result.failed == []
    assert result.enriched == 1
    # The doomed docket fetch is still counted: spend inspection includes it.
    assert result.requests == 3
    with corpus.connect(db) as conn:
        landed = corpus.get_row(conn, "scotus/101")
        deferred = corpus.get_row(conn, "scotus/102")
    assert landed is not None and landed.opinion_text == _BODY
    assert deferred is not None and deferred.has_opinion is False


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
