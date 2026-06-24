"""Thin, typed client for the CourtListener REST API v4.

Used by the deterministic ``run-seed`` / ``run-pull`` scripts. Agents that need
richer, exploratory access use the official CourtListener MCP server instead
(see ``.mcp.json``); this client exists so the routine docket fetching is
reproducible and does not require an agent in the loop.

Auth: pass a CourtListener API token (every CourtListener account gets one).
Docs: https://www.courtlistener.com/help/api/rest/
"""

from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .ratelimit import RateLimiter, default_rate_limiter

JsonDict = dict[str, Any]


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
        retry=retry_if_exception_type(httpx.HTTPError),
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
