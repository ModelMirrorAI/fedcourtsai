"""Thin, typed client for the CourtListener REST API v4.

Used by the deterministic ``run-seed`` / ``run-pull`` scripts. Agents that need
richer, exploratory access use the official CourtListener MCP server instead
(see ``.mcp.json``); this client exists so the routine docket fetching is
reproducible and does not require an agent in the loop.

Auth: pass a CourtListener API token (every CourtListener account gets one).
Docs: https://www.courtlistener.com/help/api/rest/
"""

from __future__ import annotations

from datetime import date
from types import TracebackType
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from .ratelimit import RateLimiter, default_rate_limiter

JsonDict = dict[str, Any]


def is_transient(exc: BaseException) -> bool:
    """Whether a failed request is worth retrying.

    Network/timeout faults (:class:`httpx.RequestError`) and server-side errors
    (HTTP 5xx) or throttling (429) are transient — a retry may succeed. A
    deterministic client error such as a 404 (missing docket) is not: retrying it
    only burns the API budget without changing the outcome, so it propagates to
    the caller on the first attempt. Callers use the same split to tell a
    degraded upstream (worth backing off from) from a per-docket condition.
    """
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        return status == 429 or status >= 500
    return isinstance(exc, httpx.RequestError)


class CourtListenerClient:
    def __init__(
        self,
        base_url: str = "https://www.courtlistener.com/api/rest/v4/",
        api_token: str | None = None,
        timeout: float = 30.0,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        headers = {"Accept": "application/json"}
        if api_token:
            headers["Authorization"] = f"Token {api_token}"
        self._client = httpx.Client(base_url=base_url, headers=headers, timeout=timeout)
        # Throttle to CourtListener's per-token budget unless a limiter is supplied.
        self._rate_limiter = rate_limiter if rate_limiter is not None else default_rate_limiter()

    def __enter__(self) -> CourtListenerClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(min=1, max=20),
        retry=retry_if_exception(is_transient),
        reraise=True,
    )
    def _get(self, path: str, params: JsonDict | None = None) -> JsonDict:
        # Block here so retries (this method re-runs on retry) also count against
        # the budget — every outbound request passes through this throttle.
        self._rate_limiter.acquire()
        resp = self._client.get(path, params=params)
        resp.raise_for_status()
        data: JsonDict = resp.json()
        return data

    def get_docket(self, docket_id: int) -> JsonDict:
        """Fetch a single docket by CourtListener docket id."""
        return self._get(f"dockets/{docket_id}/")

    def get_opinion_cluster(self, cluster_id: int) -> JsonDict:
        """Fetch a single opinion cluster by CourtListener cluster id.

        A docket's ``clusters`` field lists opinion-cluster URLs; the trailing id
        is what this resolves. Read-only, like every method here — used by the
        recoverability probe to follow a docket's linked cluster for its
        ``disposition`` / ``precedential_status`` / citations.
        """
        return self._get(f"clusters/{cluster_id}/")

    def list_docket_entries(self, docket_id: int, page: int = 1) -> JsonDict:
        """List docket entries (the timeline of filings/orders) for a docket."""
        return self._get("docket-entries/", {"docket": docket_id, "page": page})

    def iter_docket_entries(self, docket_id: int) -> list[JsonDict]:
        """Page through and collect all docket entries for a docket."""
        results: list[JsonDict] = []
        page = 1
        while True:
            payload = self.list_docket_entries(docket_id, page=page)
            results.extend(payload.get("results", []))
            if not payload.get("next"):
                break
            page += 1
        return results

    def list_dockets(
        self,
        court: str,
        date_filed_gte: date,
        page: int = 1,
        order_by: str = "date_filed",
    ) -> JsonDict:
        """List a court's dockets filed on or after ``date_filed_gte`` (one page).

        Forward discovery: the REST analogue of scanning the bulk export for
        new filings. Ascending ``date_filed`` order is the default so a caller
        consuming results under a budget advances a watermark monotonically.
        """
        return self._get(
            "dockets/",
            {
                "court": court,
                "date_filed__gte": date_filed_gte.isoformat(),
                "order_by": order_by,
                "page": page,
            },
        )

    def iter_dockets(
        self,
        court: str,
        date_filed_gte: date,
        *,
        max_results: int,
        order_by: str = "date_filed",
    ) -> list[JsonDict]:
        """Page through new filings for a court, stopping once ``max_results`` is hit.

        ``max_results`` is a hard cap so discovery stays inside the API budget:
        no more pages are fetched than needed to fill it.
        """
        results: list[JsonDict] = []
        page = 1
        while len(results) < max_results:
            payload = self.list_dockets(court, date_filed_gte, page=page, order_by=order_by)
            results.extend(payload.get("results", []))
            if not payload.get("next"):
                break
            page += 1
        return results[:max_results]
