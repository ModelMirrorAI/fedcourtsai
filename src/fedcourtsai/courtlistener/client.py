"""Thin, typed client for the CourtListener REST API v4.

Reads dockets and their entries (the ``pull`` channel), plus the opinion
cluster and opinion records a decided docket links (the opinion-enrichment
channel — :mod:`fedcourtsai.pipeline.opinion_enrichment`). Every endpoint goes
through one throttled, retried :meth:`CourtListenerClient._get`, so each shares
the same rate governor, retry policy, and error classification.

Used by the deterministic ``run-pull`` scripts. Agents that need
richer, exploratory access use the official CourtListener MCP server instead
(see ``.mcp.json``); this client exists so the routine docket fetching is
reproducible and does not require an agent in the loop.

Auth: pass a CourtListener API token (every CourtListener account gets one).
Docs: https://www.courtlistener.com/help/api/rest/
"""

from __future__ import annotations

from datetime import date
from types import TracebackType
from typing import Any, Literal

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


def is_throttled(exc: BaseException) -> bool:
    """Whether a failed request is upstream throttling (HTTP 429) specifically.

    The narrow slice of :func:`is_transient` a caller reads as "the shared
    quota wall, not this request's fault": a 429 that survives the client's
    own retry cycle tells a batch consumer to stop rather than press every
    remaining item into the same wall. Kept here beside ``is_transient`` so
    the status-code taxonomy lives in one place.
    """
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429


# The failure-queue error-class taxonomy — deliberately the *same* transient /
# permanent split as `is_transient`, not a parallel one, so a retry (part of the
# client) and the durable failure queue agree on what "worth retrying" means.
ErrorClass = Literal["transient", "permanent"]


def classify_error(exc: BaseException) -> ErrorClass:
    """The error class the durable failure queue records for a failed cell.

    A thin label over :func:`is_transient`: a transient fault (timeout, 5xx, 429)
    is worth another attempt; anything else (a 404, a quota/permission wall, a
    deterministic client error) is permanent. Kept here beside ``is_transient``
    so the two never diverge.
    """
    return "transient" if is_transient(exc) else "permanent"


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
        # Redirects are not followed, stated rather than inherited: the
        # Authorization header rides every request, so a 3xx off the API origin
        # would be a credential leak and a request this client did not address.
        # A 3xx therefore reaches `raise_for_status` and surfaces as a permanent
        # error the caller records, not as a silent hop to another origin.
        self._client = httpx.Client(
            base_url=base_url, headers=headers, timeout=timeout, follow_redirects=False
        )
        # Throttle to CourtListener's per-token budget unless a limiter is supplied.
        self._rate_limiter = rate_limiter if rate_limiter is not None else default_rate_limiter()

    @property
    def base_url(self) -> str:
        """The REST base every request is built against.

        Exposed so a caller holding an upstream *hyperlink* (a snapshot
        payload's ``clusters`` entry, say) can check it resolves under this
        client's own API base before trusting the id inside it — the client
        itself only ever takes ids and builds its own paths.
        """
        return str(self._client.base_url)

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

    def get_cluster(self, cluster_id: int) -> JsonDict:
        """Fetch a single opinion cluster by CourtListener cluster id.

        A cluster is the decision a docket produced: its reporter ``citations``,
        the ``citation_count`` of how often it has been cited since, and the
        ``sub_opinions`` (majority, concurrences, dissents) whose bodies carry
        the text.
        """
        return self._get(f"clusters/{cluster_id}/")

    def get_opinion(self, opinion_id: int) -> JsonDict:
        """Fetch a single opinion by CourtListener opinion id.

        One sub-opinion of a cluster; ``plain_text`` carries the extracted body
        where upstream holds one.
        """
        return self._get(f"opinions/{opinion_id}/")

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
