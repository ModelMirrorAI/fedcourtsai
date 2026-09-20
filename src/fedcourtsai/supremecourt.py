"""The SCOTUS live channel's client: supremecourt.gov per-docket JSON.

The Court's own site serves a structured JSON docket per case at
``supremecourt.gov/rss/cases/JSON/<term>-<number>.json`` — the authoritative
record, minutes-to-hours fresh, with **no API budget**. This is deliberately
*not* the CourtListener client: no token, no request governor, none of the
budget machinery. The three access facts from docs/live-sources.md (verified by
the reachability probe, docs/live-sources.md) shape it instead: a browser
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
from typing import Any, Literal
from urllib.parse import urlsplit

import httpx

DOCKET_JSON_URL = "https://www.supremecourt.gov/rss/cases/JSON/{docket}.json"

# Any ordinary browser UA is accepted; the default programmatic UA gets a 403.
# Pinned so runs are comparable (shared with the reachability probe's posture).
BROWSER_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0"

# The reserved identity range for live-first petitions. CourtListener docket ids
# are orders of magnitude below this base, so the two id spaces can never
# collide; term/serial pack losslessly because a Term's serials stay far under
# the 1_000_000 stride (paid ~1..2000, IFP 5001..~8000).
LIVE_DOCKET_ID_BASE = 9_000_000_000
_LIVE_TERM_STRIDE = 1_000_000

# The same scheme for the interim docket. Applications are numbered in their own
# per-Term sequence ("24A1099"), so `24A1` and `24-1` are different matters and
# must never share an id — hence a disjoint base rather than a shared one. Serials
# run to roughly 1200 a Term, far under the stride.
LIVE_APPLICATION_ID_BASE = 9_500_000_000

# IFP petitions are numbered from 5001 within a Term; paid petitions from 1.
IFP_SERIAL_BASE = 5001

# Backoff pause before the single retry on a transient upstream response.
_RETRY_PAUSE_SECONDS = 5.0

# The host this channel is scoped to. Every URL it requests is a supremecourt.gov
# path — the docket JSON this module builds, and the filed documents whose links
# come verbatim out of that JSON — because the Court's own site is the only place
# those records live (docs/data-sources.md, docs/live-sources.md). Anywhere else
# is not a channel the pipeline has: it would let another origin supply bytes
# that are stored as a filed document and read by a cell as evidence, while the
# politeness pacing and the 403 retry posture stay keyed to the intended host.
# The rule binds the URL a fetch starts at as well as every hop it is sent to,
# because a `DocumentUrl` is upstream-controlled text and a `Location` header is
# upstream-controlled text — the same input by two routes. Matched as a suffix
# so the Court's subdomains are in and a lookalike like `supremecourt.gov.example`
# is out.
DOCUMENT_HOST_SUFFIX = "supremecourt.gov"

# How many same-host hops one fetch may walk before the chain is treated as a
# loop. Tighter than httpx's own default, because this channel's redirects are
# an upstream housekeeping detail rather than a routing layer.
_MAX_REDIRECTS = 5


def is_court_url(url: str) -> bool:
    """Whether ``url`` is HTTPS on the Court's own host.

    The predicate both the redirect guard below and the OCR pass's
    ``fetchable_document_url`` are written against, so "the host this channel is
    scoped to" has one spelling rather than two that can drift apart. Scheme is
    part of it: a plaintext hop to the right host is still not this channel, and
    a `file:` or relative URL would reach the client as something other than an
    HTTP request. Userinfo is refused for a reason of its own — it dials the
    right host, but it lets an upstream string decide what credentials the
    request carries — and a non-default port is refused because the Court serves
    its records on 443. So is any URL carrying a character that is not
    printable: ``urlsplit`` drops tabs and newlines before parsing, so a control
    character inside an otherwise-plausible link would pass this and then reach
    the transport as a different string from the one checked.
    """
    if any(not char.isprintable() for char in url):
        return False
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return False
    if parts.scheme != "https" or not parts.hostname:
        return False
    if parts.username or parts.password or port not in (None, 443):
        return False
    host = parts.hostname.lower()
    return host == DOCUMENT_HOST_SUFFIX or host.endswith(f".{DOCUMENT_HOST_SUFFIX}")


class OffHostFetch(httpx.HTTPError):
    """A request that would have left the Court's host, refused unmade.

    Raised for the two routes a fetch can leave the host: the URL it starts at
    — which for a document is a ``DocumentUrl`` lifted verbatim from docket
    JSON, the case this exists for, though the docket-JSON URL this module
    builds is checked by the same rule — and a ``Location`` header it is
    redirected to. ``redirected_from`` is what tells them apart in the log line.

    An ``httpx.HTTPError`` so that a caller which does not know the condition
    degrades the way it degrades every other failed fetch — skipping the
    document rather than crashing the run — while a caller that wants it apart
    catches this class first and counts it under its own reason. The distinction
    is worth keeping: a transport failure is routine and self-healing, an
    off-host fetch is a document the channel would have taken from a host it is
    not scoped to, and one occurrence is worth a maintainer's reading.
    """

    def __init__(self, target: str, *, redirected_from: str | None = None) -> None:
        where = target if redirected_from is None else f"{redirected_from} -> {target}"
        super().__init__(f"refused a fetch off the Court's host: {where}")
        self.target = target
        self.redirected_from = redirected_from


def live_docket_id(term: int, serial: int) -> int:
    """The deterministic reserved-range docket id for a live-first petition.

    Permanent — the row never migrates to a CourtListener id (case_id
    immutability; the ledger and snapshots key on it). Idempotent by
    construction, so re-discovery of the same petition mints the same id.
    """
    return _reserved_id(LIVE_DOCKET_ID_BASE, term, serial)


def live_application_id(term: int, serial: int) -> int:
    """The deterministic reserved-range docket id for a live-first application.

    A disjoint range from :func:`live_docket_id`, because the two numbering
    sequences overlap: ``24A1`` and ``24-1`` are different matters that would
    otherwise collide on ``(term, serial)``. Same permanence and idempotence.
    """
    return _reserved_id(LIVE_APPLICATION_ID_BASE, term, serial)


def _reserved_id(base: int, term: int, serial: int) -> int:
    if not 0 <= term < 100:
        raise ValueError(f"term out of range: {term}")
    if not 0 < serial < _LIVE_TERM_STRIDE:
        raise ValueError(f"serial out of range: {serial}")
    return base + term * _LIVE_TERM_STRIDE + serial


def is_live_docket_id(docket_id: int) -> bool:
    """Whether a docket id sits in either live-channel reserved range."""
    return docket_id >= LIVE_DOCKET_ID_BASE


def is_application_docket_id(docket_id: int) -> bool:
    """Whether a docket id was minted for an interim-docket application."""
    return docket_id >= LIVE_APPLICATION_ID_BASE


def parse_scotus_docket_number(raw: str | None) -> tuple[int, int] | None:
    """Parse a modern Term-form docket number to ``(term, serial)``, or ``None``.

    Accepts the JSON's ``CaseNumber`` verbatim (it carries a trailing space) and
    ordinary spellings like ``"22-451"``. Applications (``22A123``) parse through
    :func:`parse_scotus_application_number` instead, because they are a separate
    numbering sequence rather than a spelling of the same one. Original docket
    (``22O141``) and pre-1925 bare numbers do not parse at all.
    """
    if raw is None:
        return None
    text = raw.strip()
    head, sep, tail = text.partition("-")
    if not sep or not head.isdigit() or len(head) != 2 or not tail.isdigit():
        return None
    return int(head), int(tail)


def parse_scotus_application_number(raw: str | None) -> tuple[int, int] | None:
    """Parse an interim-docket application number to ``(term, serial)``, or ``None``.

    ``"24A1099"`` -> ``(24, 1099)``. Accepts the JSON's ``CaseNumber`` verbatim,
    trailing space and all.

    Deliberately strict where the scope rule is tolerant: that rule has to
    *recognize* every spelling an application might carry so none reaches cert
    scope, while this has to *address* one on the upstream JSON endpoint, which
    serves exactly the ``YYAnnn`` form. A number this rejects is still an
    application; it is simply not one the live channel can fetch.
    """
    if raw is None:
        return None
    head, sep, tail = raw.strip().upper().partition("A")
    if not sep or not head.isdigit() or len(head) != 2 or not tail.isdigit():
        return None
    return int(head), int(tail)


def scotus_docket_slug(
    term: int, serial: int, *, form: Literal["cert", "application"] = "cert"
) -> str:
    """The upstream path segment for a docket: ``"24-1099"`` or ``"24A1099"``."""
    separator = "A" if form == "application" else "-"
    return f"{term:02d}{separator}{serial}"


def october_term_year(day: date) -> int:
    """The October Term ``day`` falls in — the tree's one date→Term rule.

    A Term opens in October and runs until the next one does, so the pivot is
    the calendar month: ``2026-06-30`` is OT2025, ``2026-10-05`` is OT2026.
    Deliberate at the seam — a late-September long-conference order, issued for
    the *incoming* Term, lands in the **outgoing** Term's row — and stated here
    once rather than per caller, so the merits cohort's Term axis (keyed on the
    cert-grant date), the statpack's per-Term rows, and the back-test replay
    clock all cut on the same boundary. Do not re-derive it anywhere.
    """
    return day.year if day.month >= 10 else day.year - 1


def current_docket_term(today: date) -> int:
    """The two-digit Term prefix the Clerk assigns new filings ``today``.

    Not the October Term ``today`` falls in: the Clerk starts a Term's docket
    numbering the **July** before it opens (26-1 was docketed July 1, 2026,
    three months ahead of OT26's October start, while 25-numbered filings end
    in late June), so the filing prefix rolls in July. Probing discovery by an
    October roll would leave the entire summer intake — the long-conference
    cohort — invisible until the Term opened. The other date→Term pivot in the
    tree, :func:`october_term_year` above, rolls in **October** on purpose: it
    names the October Term a date belongs to, a different concept — do not
    unify them.
    """
    year = today.year if today.month >= 7 else today.year - 1
    return year % 100


def term_roll_date(today: date) -> date:
    """The July 1 on which the filing-Term prefix ``today`` uses last rolled.

    The docket-number roll is July 1 (see :func:`current_docket_term`), so this
    is that boundary for the Term in force ``today``: July 1 of the same year in
    the second half, of the prior year in the first half. ``(today - this).days``
    is how far past the roll ``today`` sits — the axis the outgoing-Term grace
    window is measured on.
    """
    year = today.year if today.month >= 7 else today.year - 1
    return date(year, 7, 1)


class SupremeCourtClient:
    """Polite fetcher for the per-docket JSON. Read-only; no token, no governor.

    ``get_docket`` returns the parsed JSON object, or ``None`` when the docket
    does not exist (a 404 or a non-JSON body — the site serves HTML error pages
    under some failure modes, and "no docket here" must never crash a poll).
    Throttles before every request after the first and retries once, after a
    pause, on 403/429/5xx or a transport error; a second failure raises, so a
    degraded upstream degrades the run instead of being hammered. Redirects are
    walked here rather than left to httpx, so that a hop off the Court's host is
    refused (:class:`OffHostFetch`) before the request is made rather than
    discovered after the bytes are in hand.
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

    def get_docket(
        self, term: int, serial: int, *, form: Literal["cert", "application"] = "cert"
    ) -> dict[str, Any] | None:
        """Fetch one docket's JSON, or ``None`` when no docket is served there.

        ``form`` selects the numbering sequence: a cert petition is ``YY-NNNN``
        and an interim application ``YYAnnn``. Upstream serves both at the same
        endpoint with the same payload shape — proceedings included — so nothing
        below this call has to know which it fetched.
        """
        url = DOCKET_JSON_URL.format(docket=scotus_docket_slug(term, serial, form=form))
        response = self._fetch(url)
        if response is None:
            return None
        try:
            payload = response.json()
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None

    def get_document(self, url: str) -> bytes | None:
        """Fetch one linked document (a filed PDF), or ``None`` when not served.

        Same politeness as the docket fetch. Document links may vanish — the
        reachability probe found coverage is a rolling ~5-Term window — so a
        missing document is an expected condition, never an error. A link that
        is not on the Court's host, or that redirects off it, raises
        :class:`OffHostFetch` instead of returning bytes: the link comes
        verbatim out of upstream JSON and what comes back is filed as evidence,
        so the bytes have to have come from the host the channel is scoped to.
        """
        response = self._fetch(url)
        return response.content if response is not None else None

    def _fetch(self, url: str) -> httpx.Response | None:
        """One paced GET with a single-retry backoff; ``None`` on a 404."""
        for attempt in (1, 2):
            self._pace()
            try:
                response = self._walk(url)
            except (OffHostFetch, httpx.TooManyRedirects):
                # Neither is retried: asking again returns the same refusal or
                # walks the same loop, at the cost of a pause and a second walk.
                raise
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
            return response
        raise AssertionError("unreachable")  # pragma: no cover

    def _walk(self, url: str) -> httpx.Response:
        """One GET on the Court's host, following only hops that stay on it.

        Both ends of the chain are checked, because both are upstream text: the
        starting URL is a ``DocumentUrl`` copied verbatim out of docket JSON,
        and each hop is a ``Location`` header. Following is done here rather
        than by the client, because checking the final origin after httpx has
        followed the chain would mean the off-host request was already made and
        its body already read — the bytes become a stored document, and the
        pacing and the 403 retry posture are keyed to the intended host. Every
        hop is paced like the request it is, and a same-host chain resolves to
        its final response. The per-request ``follow_redirects=False`` also
        binds an injected client, so a caller's client cannot follow the chain
        out from under this.
        """
        if not is_court_url(url):
            raise OffHostFetch(url)
        current = url
        response = self._get(current)
        hops = 0
        while response.is_redirect and response.next_request is not None:
            if hops == _MAX_REDIRECTS:
                # The cap counts hops taken, so the response after the last one
                # is still read: a chain that ends exactly at the cap resolves
                # rather than spending a request whose body is then discarded.
                response.close()
                raise httpx.TooManyRedirects(
                    f"too many redirects fetching {url}", request=response.request
                )
            target = str(response.next_request.url)
            if not is_court_url(target):
                response.close()
                raise OffHostFetch(target, redirected_from=current)
            hops += 1
            self._pace()
            current = target
            response = self._get(current)
        return response

    def _get(self, url: str) -> httpx.Response:
        """One unfollowed GET, with a malformed upstream URL kept in-protocol.

        A ``Location`` naming a non-ASCII host reaches httpx as an encoding
        error rather than an HTTP one — raised while the redirect request is
        built, so it surfaces on the request that *received* the header — and
        neither ``UnicodeEncodeError`` (a ``ValueError``) nor ``httpx.InvalidURL``
        is an ``httpx.HTTPError``, so either escaping here would end the whole
        pass over one bad header. It is an upstream that cannot be spoken to,
        which is what ``RemoteProtocolError`` says.
        """
        try:
            return self._client.get(url, follow_redirects=False)
        except (ValueError, httpx.InvalidURL) as exc:
            raise httpx.RemoteProtocolError(f"unusable URL from upstream at {url}") from exc
