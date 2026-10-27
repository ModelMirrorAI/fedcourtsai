"""The adverse-order scan: candidate district orders against federal executive action.

The selection-adjusted analysis of the emergency docket needs a denominator the
corpus does not hold: every lower-court order adverse to a federal executive
action, whether or not anyone took it to the Supreme Court. Most such orders are
district-court preliminary injunctions, temporary restraining orders and
vacaturs, and CourtListener's bulk exports carry no docket entries, so the
order language that marks one can only be read through the REST API. This
module runs that read as a bounded **RECAP search**: each configured query asks
for district dockets whose entries match an order phrase, within one filing
window, and each result names the dockets and the entries that matched.

**A measurement, not a store.** Nothing here writes the corpus, the content
store or the ledger. The ``order-scan`` command prints one
:class:`OrderScanReport`, which a maintainer reads to hand-code the candidate
orders and to measure recall before any district docket is admitted anywhere.
The report carries identifiers only: court, docket id and number, the caption,
the filing date and nature of suit, and for each matched entry its number, date
and the order kinds its description reads as. The entry text itself is not
copied; a coder reads it on CourtListener. No request buys anything: RECAP
search reads only what CourtListener already holds, and RECAP Fetch is never
called.

**The queries are configuration.** ``config/order-scan.yaml`` names each query's
search filters verbatim (upstream's own parameter names, a closed set checked
here) and the filing windows each runs over, so the scan is retuned by a
reviewed config change rather than a code change. Every query runs once per
window, and each window is the same span for every query, so the per-window
counts compare across administrations.

**The order reading is text, and says so.** A matched entry's kinds come from a
pattern match over its description (the short description, then the search
snippet, where upstream returns no description): a TRO, a preliminary or
permanent injunction, a vacatur or set-aside, a stay under 5 U.S.C. 705. Its
polarity is ``granted``, ``denied``, ``mixed`` (both words) or ``unclear``.
These readings sort the candidates for hand review; they are not codes.

**District courts only.** A result from any other court (a circuit, a
bankruptcy court, the Supreme Court) is counted and dropped: the pool's unit is
the district order, and the circuit stay rulings it also needs are reached from
the district dockets.

**Recall is measured, not assumed.** The config lists a gold set: the district
dockets the corpus's immigration applications trace back to. The report says,
for each, whether any query found it, so a query set's recall is a figure in
the report rather than a hope.

**Bounded spend.** A search page is one request, a search stops at its page
cap, and the run stops before the request that would pass its run cap. A
transient fault the client retries costs up to three requests more, which the
client's rate governor counts and this cap does not. Reaching the cap, a 429 the
client's retries could not clear, the governor's own budget, or a 401 stops the
scan cleanly, with the searches it did not finish reported deferred.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Final, Literal

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_throttled

#: Upstream's RECAP search filters this scan may set. ``type`` is not among
#: them: the scan always asks for ``r`` (dockets with their matching entries),
#: and the filing window comes from the window, not the query.
SEARCH_PARAMS: Final = frozenset(
    {
        "q",
        "case_name",
        "description",
        "docket_number",
        "nature_of_suit",
        "cause",
        "court",
        "party_name",
        "entry_date_filed_after",
        "entry_date_filed_before",
        "order_by",
    }
)

#: A CourtListener district-court id: the state or territory letters and a
#: trailing ``d`` (``dcd``, ``mad``, ``nysd``, ``txwd``). Circuits (``ca9``,
#: ``cadc``), bankruptcy courts (``…b``) and ``scotus`` do not match.
DISTRICT_COURT: Final = re.compile(r"[a-z]{2,4}d")

OrderKind = Literal["tro", "preliminary-injunction", "permanent-injunction", "vacatur", "stay-705"]
Polarity = Literal["granted", "denied", "mixed", "unclear"]

_KINDS: Final[tuple[tuple[OrderKind, re.Pattern[str]], ...]] = (
    ("tro", re.compile(r"\btemporary restraining order\b|\bTRO\b")),
    ("preliminary-injunction", re.compile(r"\bpreliminar(?:y|ily) (?:injunction|enjoin)", re.I)),
    ("permanent-injunction", re.compile(r"\bpermanent(?:ly)? (?:injunction|enjoin)", re.I)),
    ("vacatur", re.compile(r"\bvacat(?:e|ed|es|ing|ur)\b|\bset(?:ting)? aside\b", re.I)),
    ("stay-705", re.compile(r"\b705\b|\bpostpone\w* the effective date", re.I)),
)
_GRANTED: Final = re.compile(r"\bgrant(?:s|ed|ing)?\b", re.I)
_DENIED: Final = re.compile(r"\bden(?:y|ies|ied|ying)\b", re.I)


class SearchWindow(BaseModel):
    """One filing window: dockets filed on or after ``filed_after`` and before ``filed_before``."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    filed_after: date
    filed_before: date

    @model_validator(mode="after")
    def _ordered(self) -> SearchWindow:
        if self.filed_before <= self.filed_after:
            raise ValueError(f"window {self.name!r} ends on or before it starts")
        return self


class SearchQuery(BaseModel):
    """One query: a name and upstream's search filters, verbatim."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    params: dict[str, str]

    @field_validator("params")
    @classmethod
    def _known(cls, value: dict[str, str]) -> dict[str, str]:
        unknown = sorted(set(value) - SEARCH_PARAMS)
        if unknown:
            raise ValueError(
                f"unknown search parameters {unknown}; allowed: {sorted(SEARCH_PARAMS)}"
            )
        if not value:
            raise ValueError("a query needs at least one search parameter")
        return value


class GoldDocket(BaseModel):
    """A district docket the scan should find, and the applications it traces to."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    docket_id: int
    court: str
    docket_number: str
    applications: list[str]


class OrderScanConfig(BaseModel):
    """``config/order-scan.yaml``: the run cap, the page cap, the windows, queries and gold set."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_requests_per_run: int = Field(gt=0)
    max_pages_per_search: int = Field(gt=0)
    windows: list[SearchWindow] = Field(min_length=1)
    queries: list[SearchQuery] = Field(min_length=1)
    gold: list[GoldDocket] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_names(self) -> OrderScanConfig:
        for label, names in (
            ("window", [w.name for w in self.windows]),
            ("query", [q.name for q in self.queries]),
        ):
            if len(set(names)) != len(names):
                raise ValueError(f"duplicate {label} names: {names}")
        return self

    def searches(self) -> list[tuple[SearchQuery, SearchWindow]]:
        """Every query in every window, query-major, in config order."""
        return [(query, window) for query in self.queries for window in self.windows]


def load_order_scan_config(path: Path) -> OrderScanConfig:
    """Read and validate the scan config; a missing file is an error, not a default."""
    data = yaml.safe_load(path.read_text())
    return OrderScanConfig.model_validate(data)


class MatchedEntry(BaseModel):
    """One docket entry the search matched, read for order kind and polarity."""

    model_config = ConfigDict(extra="forbid")

    entry_number: int | None = None
    entry_date_filed: str | None = None
    document_id: int | None = None
    kinds: list[OrderKind] = Field(default_factory=list)
    polarity: Polarity = "unclear"


class ScanHit(BaseModel):
    """One district docket at least one search returned."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    court: str
    docket_number: str = ""
    case_name: str = ""
    date_filed: str | None = None
    nature_of_suit: str = ""
    searches: list[str] = Field(default_factory=list)
    entries: list[MatchedEntry] = Field(default_factory=list)
    more_entries: bool = False


class SearchOutcome(BaseModel):
    """What one query in one window cost and returned."""

    model_config = ConfigDict(extra="forbid")

    search: str
    query: str
    window: str
    pages: int = 0
    count: int | None = None
    results: int = 0
    district: int = 0
    other_courts: int = 0
    truncated: bool = False
    error: str | None = None


class GoldOutcome(BaseModel):
    """Whether the scan found one gold docket, and which searches did."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    court: str
    docket_number: str
    applications: list[str]
    found: bool
    searches: list[str] = Field(default_factory=list)


class OrderScanReport(BaseModel):
    """The scan's result: per-search spend and counts, the hits, and gold recall."""

    model_config = ConfigDict(extra="forbid")

    generated_at: str
    max_requests: int
    requests: int = 0
    stopped: str | None = None
    deferred: list[str] = Field(default_factory=list)
    searches: list[SearchOutcome] = Field(default_factory=list)
    hits: list[ScanHit] = Field(default_factory=list)
    hits_by_window: dict[str, int] = Field(default_factory=dict)
    gold: list[GoldOutcome] = Field(default_factory=list)
    gold_found: int = 0


def read_entry(description: str) -> tuple[list[OrderKind], Polarity]:
    """The order kinds an entry description names, and whether it grants or denies."""
    kinds = [kind for kind, pattern in _KINDS if pattern.search(description)]
    granted = bool(_GRANTED.search(description))
    denied = bool(_DENIED.search(description))
    polarity: Polarity = (
        "mixed"
        if granted and denied
        else "granted"
        if granted
        else "denied"
        if denied
        else "unclear"
    )
    return kinds, polarity


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _entry(doc: Mapping[str, Any]) -> MatchedEntry:
    description = (
        _text(doc.get("description"))
        or _text(doc.get("short_description"))
        or _text(doc.get("snippet"))
    )
    kinds, polarity = read_entry(description)
    return MatchedEntry(
        entry_number=_int(doc.get("entry_number")),
        entry_date_filed=_text(doc.get("entry_date_filed")) or None,
        document_id=_int(doc.get("id")),
        kinds=kinds,
        polarity=polarity,
    )


class _RunCapReached(Exception):
    """The next request would pass the run's request cap."""


def _stop_reason(exc: Exception) -> str | None:
    if isinstance(exc, _RunCapReached):
        return str(exc)
    if isinstance(exc, RateBudgetExceeded):
        return f"API budget exhausted ({exc})"
    if is_throttled(exc):
        return f"CourtListener throttling persisted ({exc})"
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 401:
        return "CourtListener refused the credential (HTTP 401)"
    return None


def _merge(hits: dict[int, ScanHit], result: Mapping[str, Any], search: str) -> bool:
    """Fold one result into the hits; False when it is not a district docket."""
    docket_id = _int(result.get("docket_id"))
    court = _text(result.get("court_id"))
    if docket_id is None or not DISTRICT_COURT.fullmatch(court):
        return False
    hit = hits.get(docket_id)
    if hit is None:
        hit = hits[docket_id] = ScanHit(
            docket_id=docket_id,
            court=court,
            docket_number=_text(result.get("docketNumber")),
            case_name=_text(result.get("caseName")),
            date_filed=_text(result.get("dateFiled"))[:10] or None,
            nature_of_suit=_text(result.get("suitNature")),
        )
    if search not in hit.searches:
        hit.searches.append(search)
    seen = {(e.entry_number, e.document_id) for e in hit.entries}
    documents = result.get("recap_documents")
    for doc in documents if isinstance(documents, list) else []:
        if isinstance(doc, Mapping):
            entry = _entry(doc)
            if (entry.entry_number, entry.document_id) not in seen:
                seen.add((entry.entry_number, entry.document_id))
                hit.entries.append(entry)
    hit.more_entries = hit.more_entries or bool(result.get("more_docs"))
    return True


def _fetch(
    client: CourtListenerClient,
    report: OrderScanReport,
    outcome: SearchOutcome,
    params: Mapping[str, str],
    next_url: str | None,
) -> dict[str, Any]:
    """One search page, refused before the request that would pass the run cap."""
    if report.requests >= report.max_requests:
        raise _RunCapReached(f"run cap of {report.max_requests} requests reached")
    report.requests += 1
    page = client.search(params) if next_url is None else client.search_next(next_url)
    outcome.pages += 1
    return page


def _read_page(
    page: Mapping[str, Any], outcome: SearchOutcome, hits: dict[int, ScanHit]
) -> str | None:
    """Fold one page's results into the hits; the next page's link, if any."""
    if outcome.count is None:
        outcome.count = _int(page.get("count"))
    results = page.get("results")
    for result in results if isinstance(results, list) else []:
        if not isinstance(result, Mapping):
            continue
        outcome.results += 1
        if _merge(hits, result, outcome.search):
            outcome.district += 1
        else:
            outcome.other_courts += 1
    next_url = page.get("next")
    return next_url if isinstance(next_url, str) and next_url else None


def scan(
    client: CourtListenerClient,
    config: OrderScanConfig,
    *,
    max_requests: int,
    now: datetime | None = None,
) -> OrderScanReport:
    """Run every search in turn, stopping cleanly at a run-level wall."""
    report = OrderScanReport(
        generated_at=(now or datetime.now(UTC)).isoformat(timespec="seconds"),
        max_requests=max_requests,
    )
    hits: dict[int, ScanHit] = {}
    searches = config.searches()
    for index, (query, window) in enumerate(searches):
        name = f"{query.name}/{window.name}"
        outcome = SearchOutcome(search=name, query=query.name, window=window.name)
        params = {
            **query.params,
            "type": "r",
            "filed_after": window.filed_after.isoformat(),
            "filed_before": window.filed_before.isoformat(),
        }
        stop: str | None = None
        try:
            page = _fetch(client, report, outcome, params, None)
            while True:
                next_url = _read_page(page, outcome, hits)
                if next_url is None:
                    break
                if outcome.pages >= config.max_pages_per_search:
                    outcome.truncated = True
                    break
                page = _fetch(client, report, outcome, params, next_url)
        except (_RunCapReached, RateBudgetExceeded, httpx.HTTPError, ValueError) as exc:
            stop = _stop_reason(exc)
            if stop is None:
                outcome.error = f"{type(exc).__name__}: {exc}"
        if stop is not None:
            # The search that hit the wall is deferred with the rest, though the
            # pages it already read stay counted and merged.
            report.stopped = stop
            report.deferred = [f"{q.name}/{w.name}" for q, w in searches[index:]]
            if outcome.pages:
                outcome.truncated = True
                report.searches.append(outcome)
            break
        report.searches.append(outcome)
    report.hits = sorted(hits.values(), key=lambda hit: hit.docket_id)
    report.hits_by_window = {
        window.name: sum(
            any(search.endswith(f"/{window.name}") for search in hit.searches)
            for hit in report.hits
        )
        for window in config.windows
    }
    report.gold = [_gold(item, hits) for item in config.gold]
    report.gold_found = sum(item.found for item in report.gold)
    return report


def _gold(item: GoldDocket, hits: Mapping[int, ScanHit]) -> GoldOutcome:
    hit = hits.get(item.docket_id)
    return GoldOutcome(
        docket_id=item.docket_id,
        court=item.court,
        docket_number=item.docket_number,
        applications=item.applications,
        found=hit is not None,
        searches=list(hit.searches) if hit is not None else [],
    )


def plan_lines(config: OrderScanConfig, *, max_requests: int) -> list[str]:
    """The searches a run would make and its worst-case spend, with no request sent."""
    searches = config.searches()
    worst = len(searches) * config.max_pages_per_search
    lines = [
        f"order-scan plan: {len(searches)} searches "
        + f"({len(config.queries)} queries x {len(config.windows)} windows), "
        + f"up to {config.max_pages_per_search} pages each; worst case {worst} requests, "
        + f"run cap {max_requests}",
    ]
    for query, window in searches:
        filters = ", ".join(f"{key}={value!r}" for key, value in sorted(query.params.items()))
        lines.append(
            f"  {query.name}/{window.name}: filed {window.filed_after} to {window.filed_before}; "
            + filters
        )
    if config.gold:
        lines.append(f"gold set: {len(config.gold)} dockets")
    return lines


def summary_lines(report: OrderScanReport) -> list[str]:
    """A short plain-text reading of a report, for the run log and summary."""
    lines = [
        f"order-scan: {len(report.hits)} district dockets from {len(report.searches)} searches, "
        + f"{report.requests} of {report.max_requests} requests",
    ]
    if report.stopped:
        lines.append(f"stopped: {report.stopped}; {len(report.deferred)} searches deferred")
    for outcome in report.searches:
        flag = " (truncated)" if outcome.truncated else ""
        error = f" error: {outcome.error}" if outcome.error else ""
        lines.append(
            f"  {outcome.search}: count {outcome.count}, {outcome.pages} pages, "
            + f"{outcome.district} district / {outcome.other_courts} other{flag}{error}"
        )
    for window, count in sorted(report.hits_by_window.items()):
        lines.append(f"  window {window}: {count} dockets")
    if report.gold:
        lines.append(f"gold recall: {report.gold_found} of {len(report.gold)}")
        missed = [f"{g.court} {g.docket_number}" for g in report.gold if not g.found]
        if missed:
            lines.append("  missed: " + "; ".join(missed))
    return lines
