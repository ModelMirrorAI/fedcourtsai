from datetime import date

import httpx

from fedcourtsai.courtlistener import CourtListenerClient, default_rate_limiter


def _client(handler: httpx.MockTransport) -> CourtListenerClient:
    """A client whose transport is mocked and whose limiter never throttles."""
    client = CourtListenerClient(rate_limiter=default_rate_limiter(10_000, 10_000, 10_000))
    client._client = httpx.Client(
        base_url="https://www.courtlistener.com/api/rest/v4/", transport=handler
    )
    return client


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
