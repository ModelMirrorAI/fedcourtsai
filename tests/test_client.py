from datetime import date
from typing import Any

import httpx
import pytest

from fedcourtsai.courtlistener import (
    CourtListenerClient,
    EntryPageCapExceeded,
    RateLimiter,
    classify_error,
    default_rate_limiter,
    is_transient,
)


class _CountingLimiter(RateLimiter):
    """A non-throttling limiter that counts how many requests it admits.

    Every attempt — including each retry — must pass through ``acquire`` so a
    retried request still counts against the API budget; the counter lets a test
    assert exactly that.
    """

    def __init__(self) -> None:
        super().__init__([(10_000, 60.0)], sleep_fn=lambda _: None)
        self.calls = 0

    def acquire(self) -> None:
        self.calls += 1
        super().acquire()


def _client(
    handler: httpx.MockTransport, rate_limiter: RateLimiter | None = None
) -> CourtListenerClient:
    """A client whose transport is mocked and whose limiter never throttles."""
    client = CourtListenerClient(
        rate_limiter=rate_limiter or default_rate_limiter(10_000, 10_000, 10_000)
    )
    client._client = httpx.Client(
        base_url="https://www.courtlistener.com/api/rest/v4/", transport=handler
    )
    return client


@pytest.fixture(autouse=True)
def _no_backoff_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make tenacity's between-retry backoff instant so tests don't really sleep."""
    get: Any = CourtListenerClient._get  # tenacity attaches the Retrying as `.retry`
    monkeypatch.setattr(get.retry, "sleep", lambda _seconds: None)


def test_list_dockets_builds_filter_query() -> None:
    seen: dict[str, str] = {}

    def handle(request: httpx.Request) -> httpx.Response:
        seen.update(dict(request.url.params))
        return httpx.Response(200, json={"results": [], "next": None})

    client = _client(httpx.MockTransport(handle))
    client.list_dockets("ca9", date(2026, 6, 1))
    client.close()

    assert seen["court"] == "ca9"
    assert seen["date_filed__gte"] == "2026-06-01"
    assert seen["order_by"] == "date_filed"
    assert seen["page"] == "1"


def test_iter_dockets_pages_until_max_results() -> None:
    pages = {
        "1": {"results": [{"id": 1}, {"id": 2}], "next": "page2"},
        "2": {"results": [{"id": 3}, {"id": 4}], "next": "page3"},
        "3": {"results": [{"id": 5}], "next": None},
    }
    requested: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        page = request.url.params.get("page", "1")
        requested.append(page)
        return httpx.Response(200, json=pages[page])

    client = _client(httpx.MockTransport(handle))
    got = client.iter_dockets("ca9", date(2026, 6, 1), max_results=3)
    client.close()

    assert [d["id"] for d in got] == [1, 2, 3]
    # Stopped after page 2 satisfied the cap; page 3 was never fetched.
    assert requested == ["1", "2"]


def test_iter_dockets_stops_when_no_next_page() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": [{"id": 1}], "next": None})

    client = _client(httpx.MockTransport(handle))
    got = client.iter_dockets("ca1", date(2026, 1, 1), max_results=50)
    client.close()

    assert [d["id"] for d in got] == [1]


def test_cluster_and_opinion_paths_are_built_from_ids() -> None:
    # The enrichment endpoints take ids, never caller-supplied URLs, so the
    # request path is always the client's own construction.
    paths: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        return httpx.Response(200, json={"id": 7})

    client = _client(httpx.MockTransport(handle))
    assert client.get_cluster(4321) == {"id": 7}
    assert client.get_opinion(8765) == {"id": 7}
    client.close()

    assert paths == [
        "/api/rest/v4/clusters/4321/",
        "/api/rest/v4/opinions/8765/",
    ]


def test_cluster_fetch_shares_the_rate_governor_and_retries() -> None:
    # The enrichment endpoints inherit `_get`'s policy rather than a parallel
    # one: a persistent 5xx is retried to the same cap, every attempt throttled.
    limiter = _CountingLimiter()

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, json={"detail": "bad gateway"})

    client = _client(httpx.MockTransport(handle), rate_limiter=limiter)
    with pytest.raises(httpx.HTTPStatusError):
        client.get_cluster(4321)
    client.close()

    assert limiter.calls == 4


def test_redirects_are_not_followed(monkeypatch: pytest.MonkeyPatch) -> None:
    # The Authorization header rides every request, so a 3xx must surface to the
    # caller rather than carry the credential to whatever origin it names.
    # httpx mounts a proxy transport from the environment at construction, and
    # a mounted proxy would take the request before the swapped transport sees
    # it, so the test runs with no proxy configured wherever it runs.
    for name in (
        "HTTPS_PROXY",
        "https_proxy",
        "HTTP_PROXY",
        "http_proxy",
        "ALL_PROXY",
        "all_proxy",
    ):
        monkeypatch.delenv(name, raising=False)
    hosts: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        return httpx.Response(
            302, headers={"Location": "https://evil.test/api/rest/v4/clusters/1/"}
        )

    # Only the transport is swapped here, not the whole `httpx.Client`, so the
    # redirect policy under test is the one the constructor sets.
    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client._transport = httpx.MockTransport(handle)
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        client.get_cluster(1)
    client.close()

    # The redirect raises rather than being followed, it is classified permanent
    # (so no retry spends budget on it), and the named host was never contacted.
    assert excinfo.value.response.status_code == 302
    assert classify_error(excinfo.value) == "permanent"
    assert hosts == ["www.courtlistener.com"]


def test_base_url_is_exposed_for_link_checking() -> None:
    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    assert client.base_url == "https://www.courtlistener.com/api/rest/v4/"
    client.close()


def test_retries_transient_failure_then_succeeds() -> None:
    # Two connection errors, then a good response: the call succeeds on attempt 3,
    # and every attempt — retries included — passed through the rate limiter.
    attempts: list[int] = []
    limiter = _CountingLimiter()

    def handle(request: httpx.Request) -> httpx.Response:
        attempts.append(1)
        if len(attempts) < 3:
            raise httpx.ConnectError("connection reset", request=request)
        return httpx.Response(200, json={"id": 64512345})

    client = _client(httpx.MockTransport(handle), rate_limiter=limiter)
    docket = client.get_docket(64512345)
    client.close()

    assert docket == {"id": 64512345}
    assert len(attempts) == 3
    assert limiter.calls == 3  # retries are throttled too — they count against budget


def test_exhausted_retries_raise_clean_typed_error() -> None:
    # A persistent 5xx is retried up to the cap, then the typed httpx error is
    # re-raised (reraise=True) rather than tenacity's RetryError wrapper.
    limiter = _CountingLimiter()

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"detail": "service unavailable"})

    client = _client(httpx.MockTransport(handle), rate_limiter=limiter)
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        client.get_docket(64512345)
    client.close()

    assert excinfo.value.response.status_code == 503
    assert limiter.calls == 4  # stop_after_attempt(4): the request + three retries


def test_request_timeout_is_retried_then_raised() -> None:
    # A timeout is a transient transport fault: retried to the cap, then the typed
    # TimeoutException surfaces to the caller.
    limiter = _CountingLimiter()

    def handle(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    client = _client(httpx.MockTransport(handle), rate_limiter=limiter)
    with pytest.raises(httpx.TimeoutException):
        client.get_docket(64512345)
    client.close()

    assert limiter.calls == 4


def test_missing_docket_404_is_not_retried() -> None:
    # A 404 is deterministic — retrying only burns budget — so it raises on the
    # first attempt without consuming the retry allowance.
    limiter = _CountingLimiter()

    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"detail": "Not found."})

    client = _client(httpx.MockTransport(handle), rate_limiter=limiter)
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        client.get_docket(99999999)
    client.close()

    assert excinfo.value.response.status_code == 404
    assert limiter.calls == 1  # no retries spent on a guaranteed-to-fail request


def _status_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://example.test")
    return httpx.HTTPStatusError(
        f"{status}", request=request, response=httpx.Response(status, request=request)
    )


def test_classify_error_agrees_with_is_transient() -> None:
    """The failure-queue error class is the same transient/permanent split the
    client retries on — one taxonomy, not two."""
    transient: list[BaseException] = [
        _status_error(429),  # throttled
        _status_error(503),  # server-side
        httpx.ReadTimeout("timed out", request=httpx.Request("GET", "https://example.test")),
    ]
    permanent: list[BaseException] = [
        _status_error(404),  # missing docket
        _status_error(403),  # a quota / permission wall
        ValueError("not an httpx error at all"),
    ]
    for exc in transient:
        assert is_transient(exc) is True
        assert classify_error(exc) == "transient"
    for exc in permanent:
        assert is_transient(exc) is False
        assert classify_error(exc) == "permanent"


_ENTRIES = "https://www.courtlistener.com/api/rest/v4/docket-entries/"


def _cursor_entries(
    pages: int, *, docket: int = 7
) -> tuple[httpx.MockTransport, list[dict[str, str]]]:
    """A docket-entries endpoint that pages only by cursor, ignoring ``page``, as upstream does."""
    seen: list[dict[str, str]] = []

    def handle(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        seen.append(params)
        index = int(params.get("cursor", "0"))
        nxt = f"{_ENTRIES}?cursor={index + 1}&docket={docket}" if index + 1 < pages else None
        return httpx.Response(200, json={"next": nxt, "results": [{"id": index}]})

    return httpx.MockTransport(handle), seen


def test_docket_entries_follow_the_cursor_not_a_page_number() -> None:
    transport, seen = _cursor_entries(3)
    client = _client(transport)

    entries = client.iter_docket_entries(7)

    assert [e["id"] for e in entries] == [0, 1, 2]
    assert seen[0] == {"docket": "7"}
    assert [p.get("cursor") for p in seen[1:]] == ["1", "2"]
    assert all("page" not in p for p in seen)


def test_docket_entries_past_the_page_cap_are_refused_whole() -> None:
    transport, seen = _cursor_entries(10)
    client = _client(transport)

    with pytest.raises(EntryPageCapExceeded, match="more than 4 pages"):
        client.iter_docket_entries(7, max_pages=4)
    assert len(seen) == 4

    read = client.docket_entries(7, max_pages=4)
    assert (read.pages, read.complete, len(read.entries)) == (4, False, 4)


def test_docket_entries_date_filter_rides_the_first_page() -> None:
    transport, seen = _cursor_entries(1)
    client = _client(transport)

    read = client.docket_entries(7, max_pages=2, date_filed_gte=date(2026, 1, 2))

    assert read.complete and read.pages == 1
    assert seen == [{"docket": "7", "date_filed__gte": "2026-01-02"}]


def test_docket_entries_modified_filter_rides_every_page() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        seen.append(params)
        if "cursor" in params:
            return httpx.Response(200, json={"next": None, "results": [{"id": 1}]})
        nxt = f"{_ENTRIES}?cursor=1&date_modified__gte=2026-10-29&docket=7"
        return httpx.Response(200, json={"next": nxt, "results": [{"id": 2}]})

    seen: list[dict[str, str]] = []
    client = _client(httpx.MockTransport(handle))

    read = client.docket_entries(7, max_pages=3, date_modified_gte=date(2026, 10, 29))

    assert read.complete and [e["id"] for e in read.entries] == [2, 1]
    assert seen[0] == {"docket": "7", "date_modified__gte": "2026-10-29"}
    assert seen[1]["date_modified__gte"] == "2026-10-29"


@pytest.mark.parametrize(
    ("next_url", "message"),
    [
        ("https://evil.example/api/rest/v4/docket-entries/?cursor=1&docket=7", "off the"),
        ("https://www.courtlistener.com/api/rest/v4/search/?cursor=1&docket=7", "off the"),
        (f"{_ENTRIES}?cursor=1&docket=8", "another question"),
        (f"{_ENTRIES}?cursor=1", "another question"),
        (f"{_ENTRIES}?cursor=1&docket=7&docket=7", "repeats a parameter"),
    ],
)
def test_docket_entries_refuse_a_next_link_this_client_did_not_build(
    next_url: str, message: str
) -> None:
    calls: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json={"next": next_url, "results": []})

    client = _client(httpx.MockTransport(handle))
    with pytest.raises(ValueError, match=message):
        client.docket_entries(7, max_pages=3)
    assert len(calls) == 1


def test_docket_entries_refuse_a_next_link_that_drops_the_date_filter() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"next": f"{_ENTRIES}?cursor=1&docket=7", "results": []})

    client = _client(httpx.MockTransport(handle))
    with pytest.raises(ValueError, match="another question"):
        client.docket_entries(7, max_pages=3, date_filed_gte=date(2026, 1, 2))


def test_docket_entries_count_each_page_before_it_is_sent() -> None:
    sent = 0

    def handle(request: httpx.Request) -> httpx.Response:
        nonlocal sent
        sent += 1
        if sent == 2:
            return httpx.Response(404, json={"detail": "gone"})
        return httpx.Response(200, json={"next": f"{_ENTRIES}?cursor=1&docket=7", "results": []})

    counted: list[None] = []
    client = _client(httpx.MockTransport(handle))
    with pytest.raises(httpx.HTTPStatusError):
        client.docket_entries(7, max_pages=3, on_request=lambda: counted.append(None))
    assert len(counted) == sent == 2
