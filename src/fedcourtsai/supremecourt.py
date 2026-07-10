"""The SCOTUS live channel's client: supremecourt.gov per-docket JSON (#472).

The Court's own site serves a structured JSON docket per case at
``supremecourt.gov/rss/cases/JSON/<term>-<number>.json`` — the authoritative
record, minutes-to-hours fresh, with **no API budget**. This is deliberately
*not* the CourtListener client: no token, no request governor, none of the
budget machinery. The three access facts from docs/live-sources.md (verified by
the #523 probe, docs/live-sources-probe.md) shape it instead: a browser
user-agent (the default programmatic UA is refused with a 403), a polite ~1
request/second throttle, and backoff on errors.

Identity for the live channel lives here too: :func:`live_docket_id` mints the
deterministic reserved-range docket id a live-first petition keeps forever
(``9_000_000_000 + term * 1_000_000 + serial``) — collision-proof against
CourtListener ids (~1e8), decodable back to the Term-form number, and stable
across re-discovery, so identity needs no allocation state and never merges.
When CourtListener later ingests the same docket, its facts enrich the existing
row via the normalized docket-number join (see ``corpus.scotus_case_id_by_docket_number``
and the symmetric guard in ``pipeline.discover``).
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from datetime import date
from typing import Any

import httpx

DOCKET_JSON_URL = "https://www.supremecourt.gov/rss/cases/JSON/{term:02d}-{serial}.json"

# Any ordinary browser UA is accepted; the default programmatic UA gets a 403.
# Pinned so runs are comparable (shared with the #523 probe's posture).
BROWSER_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0"

# The reserved identity range for live-first petitions. CourtListener docket ids
# are orders of magnitude below this base, so the two id spaces can never
# collide; term/serial pack losslessly because a Term's serials stay far under
# the 1_000_000 stride (paid ~1..2000, IFP 5001..~8000).
LIVE_DOCKET_ID_BASE = 9_000_000_000
_LIVE_TERM_STRIDE = 1_000_000

# IFP petitions are numbered from 5001 within a Term; paid petitions from 1.
IFP_SERIAL_BASE = 5001

# Backoff pause before the single retry on a transient upstream response.
_RETRY_PAUSE_SECONDS = 5.0


def live_docket_id(term: int, serial: int) -> int:
    """The deterministic reserved-range docket id for a live-first petition.

    Permanent — the row never migrates to a CourtListener id (case_id
    immutability; the ledger and snapshots key on it). Idempotent by
    construction, so re-discovery of the same petition mints the same id.
    """
    if not 0 <= term < 100:
        raise ValueError(f"term out of range: {term}")
    if not 0 < serial < _LIVE_TERM_STRIDE:
        raise ValueError(f"serial out of range: {serial}")
    return LIVE_DOCKET_ID_BASE + term * _LIVE_TERM_STRIDE + serial


def is_live_docket_id(docket_id: int) -> bool:
    """Whether a docket id sits in the live channel's reserved range."""
    return docket_id >= LIVE_DOCKET_ID_BASE


def parse_scotus_docket_number(raw: str | None) -> tuple[int, int] | None:
    """Parse a modern Term-form docket number to ``(term, serial)``, or ``None``.

    Accepts the JSON's ``CaseNumber`` verbatim (it carries a trailing space) and
    ordinary spellings like ``"22-451"``. Applications (``22A123``), original
    docket (``22O141``), and pre-1925 bare numbers do not parse — the live
    channel tracks cert petitions.
    """
    if raw is None:
        return None
    text = raw.strip()
    head, sep, tail = text.partition("-")
    if not sep or not head.isdigit() or len(head) != 2 or not tail.isdigit():
        return None
    return int(head), int(tail)


def current_october_term(today: date) -> int:
    """The two-digit October Term ``today`` falls in (new Term opens in October)."""
    year = today.year if today.month >= 10 else today.year - 1
    return year % 100


class SupremeCourtClient:
    """Polite fetcher for the per-docket JSON. Read-only; no token, no governor.

    ``get_docket`` returns the parsed JSON object, or ``None`` when the docket
    does not exist (a 404 or a non-JSON body — the site serves HTML error pages
    under some failure modes, and "no docket here" must never crash a poll).
    Throttles before every request after the first and retries once, after a
    pause, on 403/429/5xx or a transport error; a second failure raises, so a
    degraded upstream degrades the run instead of being hammered.
    """

    def __init__(
        self,
        *,
        throttle_seconds: float = 1.0,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._throttle = throttle_seconds
        self._sleep = sleep
        self._own_client = client is None
        self._client = client or httpx.Client(
            headers={"User-Agent": BROWSER_USER_AGENT},
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )
        self._first_request = True

    def __enter__(self) -> SupremeCourtClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def _pace(self) -> None:
        if self._first_request:
            self._first_request = False
            return
        self._sleep(self._throttle)

    def get_docket(self, term: int, serial: int) -> dict[str, Any] | None:
        """Fetch one docket's JSON, or ``None`` when no docket is served there."""
        url = DOCKET_JSON_URL.format(term=term, serial=serial)
        for attempt in (1, 2):
            self._pace()
            try:
                response = self._client.get(url)
            except httpx.HTTPError:
                if attempt == 1:
                    self._sleep(_RETRY_PAUSE_SECONDS)
                    continue
                raise
            if response.status_code == 404:
                return None
            if response.status_code in (403, 429) or response.status_code >= 500:
                if attempt == 1:
                    self._sleep(_RETRY_PAUSE_SECONDS)
                    continue
                response.raise_for_status()
            try:
                payload = response.json()
            except json.JSONDecodeError:
                return None
            return payload if isinstance(payload, dict) else None
        raise AssertionError("unreachable")  # pragma: no cover
