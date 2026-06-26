from datetime import date
from typing import Any

import httpx
import pytest

from fedcourtsai.courtlistener import CourtListenerClient, RateLimiter, default_rate_limiter


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
