"""The Solicitor General's posted briefs, for a docket whose filings are paper-only.

On a docket the Court has put under Rule 34.6 and Paragraph 9 of its electronic
filing guidelines (:mod:`.paper_only`), the Court posts nothing behind a party's
filing, so the document selector finds no link and a cell's ``documents/`` is
empty. Where the United States is a party, the Office of the Solicitor General
posts its own filing on its site, and this module fills the government's side
from there: the Office's petition as ``petition``, its *Petition Stage Response*
as ``brief-in-opposition`` and its *Petition Stage Reply Brief* as
``cert-reply``, the kinds a cert cell is already given.

**Dated by the docket, never by the Office.** A stored row is placed against a
cell's moment cutoff by its ``entry_date``, so each row carries the date of the
proceedings entry on the Court's own docket that records the filing — the
case-opening entry for a petition, the latest opposition entry for an
opposition, the first cert-stage reply entry for a reply — read by the
selector's own predicates (:mod:`.documents`). A brief the Office has posted
whose filing the stored docket does not yet show is not stored: the docket entry
is what tells a moment the filing exists, and storing ahead of it would hand a
cell a filing the docket it was placed on had not received. The latest
opposition entry rather than the first, because a docket with a second
respondent shows both, the entry text does not always say which is the
government's, and the later date can only place the row late, never early.

**One source, one host.** Every request goes to the Office's pages on
``www.justice.gov`` (:func:`is_osg_url`), redirects included, paced at the
site's ``robots.txt`` crawl delay. A docket is found by the briefs listing's own
text search (one GET, whose first page is the whole answer for one docket
number), and a brief is fetched from the PDF link that listing row carries. The
listing's paging and facet parameters are disallowed by ``robots.txt`` and never
built here.

**Superseded by the Court's copy.** Once the Court lifts the paper-only rule
(Rule 34.6 calls for electronic versions of all prior filings when it schedules
briefing and argument), the selector finds the Court's links for the same kinds
and the freshness pass replaces these rows by ``(case_id, kind)``, latest wins.
The OCR and re-cut passes re-fetch only the Court's own URLs, so an Office row
is never re-read by them.

The ``sg-posted-briefs`` harness boundary dates the cells that can read these
rows (``docs/freeze-record.md``). Terms of use: ``docs/data-sources.md``, *The
Solicitor General's posted briefs*.
"""

from __future__ import annotations

import hashlib
import html
import logging
import re
import sqlite3
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal
from urllib.parse import urlencode, urljoin, urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..supremecourt import BROWSER_USER_AGENT
from .cert_signals import cert_grant_date, match_disposition_signal
from .cert_signals import entry_date as parse_entry_date
from .document_backfill import is_predict_relevant
from .documents import (
    _CASE_OPENING_ENTRY_RE,
    KIND_BRIEF_IN_OPPOSITION,
    KIND_CERT_REPLY,
    KIND_PETITION,
    _derived_questions_document,
    _is_bio_entry,
    _is_cert_reply_entry,
    extract_filing_text,
    extract_questions_presented,
)
from .paper_only import paper_only_filings
from .prefetch import prefetch_by_case

logger = logging.getLogger(__name__)

#: The host the Office of the Solicitor General's pages are served from, and
#: the only one this module requests.
OSG_HOST = "www.justice.gov"
#: The path prefix every request stays under: the Office's own section.
OSG_PATH_PREFIX = "/osg/"
#: The Office's briefs listing, searched by docket number.
OSG_LISTING_URL = f"https://{OSG_HOST}/osg/supreme-court-briefs"
#: ``robots.txt`` on ``www.justice.gov`` sets ``Crawl-delay: 10`` for every
#: agent; every request after the first waits this long.
CRAWL_DELAY_SECONDS = 10.0
_RETRY_PAUSE_SECONDS = 10.0
_MAX_REDIRECTS = 5
#: A ceiling on one fetched brief. The Office's petitions run to a few hundred
#: pages with the appendix; a body past this is not a brief.
MAX_BRIEF_BYTES = 64 * 1024 * 1024

#: The Office's brief types this fill stores, mapped onto the kinds a cert cell
#: is given. Matched case-insensitively on the listing's *Brief Type* cell.
#: Every other type (merits briefs, amicus briefs, the invited brief) is left
#: alone: by the time a docket is at those stages the Court has lifted the
#: paper-only rule and posts its own copies, which the selector takes.
OSG_BRIEF_KINDS: Mapping[str, str] = {
    "petition for writ of certiorari": KIND_PETITION,
    "petition stage response": KIND_BRIEF_IN_OPPOSITION,
    "petition stage reply brief": KIND_CERT_REPLY,
}
#: The kinds this fill can store, in the order a case's owed kinds are listed.
SG_BRIEF_KINDS: tuple[str, ...] = (KIND_PETITION, KIND_BRIEF_IN_OPPOSITION, KIND_CERT_REPLY)

DEFAULT_FILL_CASES = 6
MAX_FILL_CASES = 20

SgStatus = Literal["stored", "nothing-posted", "failed"]


def is_osg_url(url: str) -> bool:
    """Whether ``url`` is HTTPS on the Office's section of ``www.justice.gov``.

    The same posture as :func:`fedcourtsai.supremecourt.is_court_url`: a link
    out of a listing row is upstream text and what it returns is stored as a
    filed document, so the scheme, the exact host, the default port and the
    path prefix are all checked, userinfo is refused, and so is any character
    that is not printable (``urlsplit`` drops tabs and newlines before parsing).
    """
    if any(not char.isprintable() for char in url):
        return False
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return False
    if parts.scheme != "https" or (parts.hostname or "").lower() != OSG_HOST:
        return False
    if parts.username or parts.password or port not in (None, 443):
        return False
    return parts.path.startswith(OSG_PATH_PREFIX)


def listing_search_url(docket_number: str) -> str:
    """The briefs listing searched for one docket number, every Term and type."""
    query = urlencode({"text": docket_number, "sc_term": "All", "type": "All", "subject": "All"})
    return f"{OSG_LISTING_URL}?{query}"


@dataclass(frozen=True)
class OsgListing:
    """One row of the Office's briefs listing."""

    term: str
    docket_numbers: tuple[str, ...]
    caption: str
    brief_url: str | None
    pdf_url: str | None
    brief_type: str
    filed: date | None

    @property
    def kind(self) -> str | None:
        """The stored kind this row's type maps onto, or ``None`` for a type left alone."""
        return OSG_BRIEF_KINDS.get(self.brief_type.strip().lower())


_ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
_CELL_RE = re.compile(
    r"<td\b[^>]*\bheaders=\"([^\"]+)\"[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL
)
_HREF_RE = re.compile(r"<a\b[^>]*\bhref=\"([^\"]+)\"", re.IGNORECASE)
_DATETIME_RE = re.compile(r"<time\b[^>]*\bdatetime=\"(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_DOCKET_TOKEN_RE = re.compile(r"\b\d{2}-\d{1,5}\b|\b\d{2}A\d{1,5}\b", re.IGNORECASE)


def _cell_text(fragment: str) -> str:
    return " ".join(html.unescape(_TAG_RE.sub(" ", fragment)).split())


def _column(header: str) -> str:
    """A listing cell's column, from its ``headers`` id (``view-field-number-table-column``)."""
    name = header.strip().lower()
    for column in ("sc-term", "number", "title", "brief-attachments", "brief-type", "date"):
        if f"-{column}-table-column" in name:
            return column
    return ""


def parse_listing(page: str, *, page_url: str) -> list[OsgListing]:
    """The rows of one listing page, links resolved against ``page_url``.

    Cells are read by their ``headers`` attribute rather than their position,
    so a column the Office adds or reorders does not shift a reading. A row
    with no docket number or no type is left out. A link that does not resolve
    onto the Office's section (:func:`is_osg_url`) is kept as ``None``, so the
    row is still counted but nothing is fetched from it.
    """
    found: list[OsgListing] = []
    for row in _ROW_RE.findall(page):
        cells: dict[str, str] = {}
        for header, body in _CELL_RE.findall(row):
            column = _column(header)
            if column:
                cells[column] = body
        numbers = tuple(
            token.upper() for token in _DOCKET_TOKEN_RE.findall(_cell_text(cells.get("number", "")))
        )
        brief_type = _cell_text(cells.get("brief-type", ""))
        if not numbers or not brief_type:
            continue
        found.append(
            OsgListing(
                term=_cell_text(cells.get("sc-term", "")),
                docket_numbers=numbers,
                caption=_cell_text(cells.get("title", "")),
                brief_url=_osg_link(cells.get("title", ""), page_url),
                pdf_url=_osg_link(cells.get("brief-attachments", ""), page_url),
                brief_type=brief_type,
                filed=_listing_date(cells.get("date", "")),
            )
        )
    return found


def _osg_link(fragment: str, page_url: str) -> str | None:
    match = _HREF_RE.search(fragment)
    if match is None:
        return None
    url = urljoin(page_url, html.unescape(match.group(1)).strip())
    return url if is_osg_url(url) else None


def _listing_date(fragment: str) -> date | None:
    match = _DATETIME_RE.search(fragment)
    if match is None:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


class OffSectionFetch(httpx.HTTPError):
    """A request or redirect hop that would leave the Office's section."""

    def __init__(self, target: str) -> None:
        super().__init__(f"refused a fetch off {OSG_HOST}{OSG_PATH_PREFIX}: {target}")


class OversizedBrief(httpx.HTTPError):
    """A fetched body larger than :data:`MAX_BRIEF_BYTES`."""


class OsgClient:
    """A paced, single-host fetcher for the Office's listing and brief PDFs.

    Waits :data:`CRAWL_DELAY_SECONDS` before every request after the first,
    retries once after a pause on a transport error, a 403, a 429 or a 5xx,
    and raises on the second failure. Redirects are walked here, each hop
    checked against :func:`is_osg_url` before it is requested. ``requests``
    counts every GET made, hops and retries included.
    """

    def __init__(
        self,
        *,
        delay_seconds: float = CRAWL_DELAY_SECONDS,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._delay = delay_seconds
        self._sleep = sleep
        self._own_client = client is None
        self._client = client or httpx.Client(
            headers={"User-Agent": BROWSER_USER_AGENT}, timeout=httpx.Timeout(60.0)
        )
        self._first_request = True
        self.requests = 0

    def __enter__(self) -> OsgClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        if self._own_client:
            self._client.close()

    def search(self, docket_number: str) -> tuple[str, str] | None:
        """The listing page searched for ``docket_number`` and the URL it was served at."""
        response = self._fetch(listing_search_url(docket_number))
        if response is None:
            return None
        return response.text, str(response.url)

    def get_pdf(self, url: str) -> bytes | None:
        """One brief's bytes, ``None`` on a 404 or a body that is not a PDF."""
        response = self._fetch(url)
        if response is None:
            return None
        if len(response.content) > MAX_BRIEF_BYTES:
            raise OversizedBrief(f"{url}: {len(response.content)} bytes")
        if not response.content.startswith(b"%PDF"):
            return None
        return response.content

    def _pace(self) -> None:
        if self._first_request:
            self._first_request = False
            return
        self._sleep(self._delay)

    def _fetch(self, url: str) -> httpx.Response | None:
        for attempt in (1, 2):
            try:
                response = self._walk(url)
            except (OffSectionFetch, httpx.TooManyRedirects):
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
        if not is_osg_url(url):
            raise OffSectionFetch(url)
        response = self._get(url)
        hops = 0
        while response.is_redirect and response.next_request is not None:
            target = str(response.next_request.url)
            response.close()
            if hops == _MAX_REDIRECTS:
                raise httpx.TooManyRedirects(f"too many redirects fetching {url}")
            if not is_osg_url(target):
                raise OffSectionFetch(target)
            hops += 1
            response = self._get(target)
        return response

    def _get(self, url: str) -> httpx.Response:
        self._pace()
        self.requests += 1
        try:
            return self._client.get(url, follow_redirects=False)
        except (ValueError, httpx.InvalidURL) as exc:
            raise httpx.RemoteProtocolError(f"unusable URL at {url}") from exc


def paper_entry_dates(payload: Mapping[str, Any]) -> dict[str, str]:
    """The docket entry date each fillable kind's filing carries, kind → date.

    Read with the selector's own predicates over the docket's entries in
    order, without asking for a link: the case-opening entry for
    ``petition``; the **latest** cert-stage opposition entry for
    ``brief-in-opposition`` (see the module docstring); the first cert-stage
    reply entry before any disposition for ``cert-reply``. The date is the
    entry's own, verbatim. A kind whose entry the docket does not show is
    absent.
    """
    granted_on = cert_grant_date(payload)
    found: dict[str, str] = {}
    disposed = False
    for entry in payload.get("ProceedingsandOrder") or []:
        if not isinstance(entry, Mapping):
            continue
        text = str(entry.get("Text") or "")
        entry_date = str(entry.get("Date") or "").strip()
        filed = parse_entry_date(entry_date or None)
        if entry_date:
            if KIND_PETITION not in found and _CASE_OPENING_ENTRY_RE.search(text):
                found[KIND_PETITION] = entry_date
            elif _is_bio_entry(text, filed=filed, granted_on=granted_on):
                found[KIND_BRIEF_IN_OPPOSITION] = entry_date
            elif (
                KIND_CERT_REPLY not in found
                and not disposed
                and _is_cert_reply_entry(text, filed=filed, granted_on=granted_on)
            ):
                found[KIND_CERT_REPLY] = entry_date
        disposed = disposed or match_disposition_signal(text) is not None
    return found


@dataclass(frozen=True)
class FillCandidate:
    """One paper-only docket the fill walks, and the kinds it owes."""

    row: corpus.CorpusRow
    docket_number: str
    entry_dates: Mapping[str, str]
    owed: tuple[str, ...]


def _rotation_key(case_id: str, today: date) -> str:
    """A per-day order, so a docket the Office never posts for cannot hold the cap."""
    return hashlib.sha256(f"{today.isoformat()}:{case_id}".encode()).hexdigest()


def fill_candidates(
    conn: corpus.ReadConnection,
    *,
    today: date,
    max_cases: int,
    priority: frozenset[str] = frozenset(),
) -> list[FillCandidate]:
    """The paper-only dockets the next fill walks, at most ``max_cases``.

    An undecided SCOTUS docket a cell can still be placed on
    (:func:`~fedcourtsai.pipeline.document_backfill.is_predict_relevant`),
    with no disposition, petition not denied and no merits decision (a
    selected docket the Court granted, vacated and remanded years ago is
    still selected, and no cell is placed on it), whose latest live snapshot
    is paper-only
    (:func:`~fedcourtsai.pipeline.paper_only.paper_only_filings`) and shows
    the filing of a fillable kind the stored set does not hold. The ledger's
    forecast cases (``priority``) go first, then the rest in a per-day order
    (:func:`_rotation_key`). A docket leaves the class by holding a row of
    every kind its entries show, or by the Court lifting the paper-only rule;
    one the Office never posts for stays, and costs one listing search each
    time the rotation reaches it.
    """
    # The walk is materialized before any snapshot read, so the prefetch's
    # workers never share the row cursor on `conn`.
    rows = {
        row.case_id: row
        for row in corpus.iter_rows(conn, court="scotus", live_slice=True)
        if row.disposition is None
        and row.date_cert_denied is None
        and row.merits_decided is None
        and is_predict_relevant(row)
    }
    picked: list[tuple[tuple[int, str], FillCandidate]] = []
    with prefetch_by_case(
        list(rows),
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="sg-briefs",
    ) as fetched:
        for case_id, snapshot in fetched:
            if snapshot is None or paper_only_filings(snapshot[1]) is not True:
                continue
            dates = paper_entry_dates(snapshot[1])
            if not dates:
                continue
            held = corpus.document_urls_for_case(conn, case_id)
            owed = tuple(kind for kind in SG_BRIEF_KINDS if kind in dates and kind not in held)
            if not owed:
                continue
            row = rows[case_id]
            number = corpus.strip_docket_annotation(row.docket_number).strip().upper()
            candidate = FillCandidate(row=row, docket_number=number, entry_dates=dates, owed=owed)
            first = 0 if case_id in priority else 1
            picked.append(((first, _rotation_key(case_id, today)), candidate))
    picked.sort(key=lambda pair: pair[0])
    return [candidate for _, candidate in picked[:max_cases]]


class SgBriefCase(BaseModel):
    """What the fill found for one docket."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    docket_number: str
    status: SgStatus = Field(
        description="stored (at least one row stored, or would be under a dry run) | "
        "nothing-posted (the Office's listing has no brief of an owed kind for this "
        "docket number) | failed (a request failed; the docket is retried next time)"
    )
    owed: list[str] = Field(description="The kinds the docket's entries show and the store lacks")
    stored: list[str] = Field(default_factory=list, description="The kinds stored")
    listed_types: list[str] = Field(
        default_factory=list,
        description="Every brief type the Office lists for this docket number, stored or not",
    )
    detail: str | None = None


class SgBriefReport(BaseModel):
    """One fill pass: the dockets walked and what was stored."""

    model_config = ConfigDict(extra="forbid")

    applied: bool
    cases: list[SgBriefCase] = Field(default_factory=list)
    stored: dict[str, int] = Field(default_factory=dict, description="Kind -> rows stored")
    requests: int = Field(default=0, description="GETs made on www.justice.gov")

    @property
    def counts(self) -> dict[str, int]:
        tally: dict[str, int] = {}
        for case in self.cases:
            tally[case.status] = tally.get(case.status, 0) + 1
        return dict(sorted(tally.items()))


def _pick(listings: Sequence[OsgListing], docket_number: str, kind: str) -> OsgListing | None:
    """The listing row of ``kind`` for this docket, the latest filed where several."""
    matching = [
        listing
        for listing in listings
        if listing.kind == kind
        and docket_number in listing.docket_numbers
        and listing.pdf_url is not None
    ]
    if not matching:
        return None
    return max(matching, key=lambda listing: listing.filed or date.min)


def brief_documents(
    client: OsgClient,
    candidate: FillCandidate,
    listings: Sequence[OsgListing],
    *,
    today: date,
    char_cap: int,
) -> list[corpus.CaseDocument]:
    """The rows one docket's posted briefs make, fetched and extracted.

    One row for each owed kind the listing carries, under the kind's own cut
    (:func:`~fedcourtsai.pipeline.documents.extract_filing_text`), dated by the
    docket entry (:func:`paper_entry_dates`), its ``url`` the Office's PDF
    link. A stored petition also yields its derived ``questions-presented``
    row, as the selector's fetch does. A PDF the Office no longer serves is
    skipped.
    """
    documents: list[corpus.CaseDocument] = []
    for kind in candidate.owed:
        listing = _pick(listings, candidate.docket_number, kind)
        if listing is None or listing.pdf_url is None:
            continue
        data = client.get_pdf(listing.pdf_url)
        if data is None:
            logger.warning(
                "sg-briefs: %s %s: the Office's PDF is not served (%s)",
                candidate.row.case_id,
                kind,
                listing.pdf_url,
            )
            continue
        extracted = extract_filing_text(data, kind=kind, char_cap=char_cap)
        document = corpus.CaseDocument(
            case_id=candidate.row.case_id,
            kind=kind,
            url=listing.pdf_url,
            entry_date=candidate.entry_dates[kind],
            fetched_at=today,
            pages=extracted.pages,
            truncated=extracted.truncated,
            ocr_derived=extracted.ocr_derived,
            text=extracted.text,
        )
        documents.append(document)
        if kind == KIND_PETITION and document.text:
            questions = extract_questions_presented(document.text)
            if questions is not None:
                documents.append(_derived_questions_document(document, questions, fetched_at=today))
    return documents


def fill_sg_briefs(
    conn: sqlite3.Connection,
    client: OsgClient,
    candidates: Sequence[FillCandidate],
    *,
    apply: bool,
    today: date,
    char_cap: int,
) -> SgBriefReport:
    """Search the Office's listing for each candidate and store what it posts.

    One listing search a docket, and one PDF GET for each owed kind the
    listing carries. Rows are written only under ``apply``; a dry run fetches
    and counts the same rows. A docket whose search or fetch fails is
    reported ``failed`` and the pass moves on; nothing marks it, so the next
    pass that reaches it asks again.
    """
    report = SgBriefReport(applied=apply)
    for candidate in candidates:
        case = SgBriefCase(
            case_id=candidate.row.case_id,
            docket_number=candidate.docket_number,
            status="nothing-posted",
            owed=list(candidate.owed),
        )
        report.cases.append(case)
        try:
            served = client.search(candidate.docket_number)
            listings = parse_listing(served[0], page_url=served[1]) if served else []
            case.listed_types = sorted(
                {
                    listing.brief_type
                    for listing in listings
                    if candidate.docket_number in listing.docket_numbers
                }
            )
            documents = brief_documents(client, candidate, listings, today=today, char_cap=char_cap)
        except httpx.HTTPError as exc:
            case.status = "failed"
            case.detail = f"{type(exc).__name__}: {exc}"
            logger.warning("sg-briefs: %s: %s", candidate.row.case_id, case.detail)
            continue
        if not documents:
            continue
        case.status = "stored"
        case.stored = [document.kind for document in documents]
        for document in documents:
            report.stored[document.kind] = report.stored.get(document.kind, 0) + 1
        if apply:
            corpus.upsert_documents(conn, documents)
    report.stored = dict(sorted(report.stored.items()))
    report.requests = client.requests
    return report
