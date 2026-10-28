"""The adverse-order scan: candidate district orders against federal executive action.

The selection-adjusted analysis of the emergency docket needs a denominator the
corpus does not hold: every lower-court order adverse to a federal executive
action, whether or not anyone took it to the Supreme Court. Most such orders are
district-court preliminary injunctions, temporary restraining orders and
vacaturs, and CourtListener's bulk exports carry no docket entries, so the
order language that marks one can only be read through the REST API. This
module runs that read as a bounded **RECAP search**: each configured query asks
for district dockets whose entries match an order phrase, within one window
of entry dates, and each result names the dockets and the entries
that matched.

**A measurement, not a store.** Nothing here writes the corpus, the content
store or the ledger. The ``order-scan`` command prints one
:class:`OrderScanReport`, which a maintainer reads to hand-code the candidate
orders and to measure recall before any district docket is admitted anywhere.
The report carries court-record identifiers and the scan's own readings: for
each docket its court, id, number, filing date and the searches that found it,
and for each matched entry its number, document id, date, the order kinds its
description reads as and their polarity. It copies no caption (a district
caption can name an individual party), no entry text and no CourtListener
value-add field such as nature of suit; a coder reads all three on
CourtListener. No request buys anything: RECAP
search reads only what CourtListener already holds, and RECAP Fetch is never
called.

**The queries are configuration.** ``config/order-scan.yaml`` names each query's
search filters verbatim (upstream's own parameter names, a closed set checked
here) and the windows each runs over, so the scan is retuned by a reviewed
config change rather than a code change. A window bounds the **entry** date
(when the order was entered), not the docket's filing date, since the pool's
unit is the order and an order's administration is the one in office when it
was entered: a suit filed in 2018 whose injunction issued in 2022 counts in
2022's window. Every query runs once per window, and each window is the same
span for every query, so the per-window counts compare across
administrations.

**The order reading is text, and says so.** A matched entry's kinds come from a
pattern match over its description (or, where upstream returns none, its
short description, then the search snippet): a TRO, a preliminary or
permanent injunction, a vacatur or set-aside, a stay under 5 U.S.C. 705. Its
polarity is ``granted``, ``denied``, ``mixed`` (both words) or ``unclear``.
These readings sort the candidates for hand review; they are not codes.

**District courts only.** A result from any other court (a circuit, a
bankruptcy court, the Supreme Court) is counted and dropped, and one naming no
docket id or court is counted apart as unparsed: the pool's unit is
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

**One scan, several runs.** A scan's searches outrun one run's cap, so a run
takes the previous run's report and carries it forward: finished searches are
kept unread, the search a wall stopped resumes at the page it could not read
(upstream's cursor link), a failed search restarts, and the hits accumulate.
The report therefore always describes the whole scan so far. A complete report,
or one made under another config digest, starts a fresh scan, so a retuned
query never resumes another query's pages.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Final, Literal

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_throttled

#: Upstream's RECAP search filters this scan may set. ``type`` is not among
#: them: the scan always asks for ``r`` (dockets with their matching entries),
#: and the entry-date bounds come from the window, not the query.
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
        "filed_after",
        "filed_before",
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
    ("tro", re.compile(r"(?i:\btemporary restraining order\b)|\bTRO\b")),
    ("preliminary-injunction", re.compile(r"\bpreliminar(?:y|ily) (?:injunction|enjoin)", re.I)),
    ("permanent-injunction", re.compile(r"\bpermanent(?:ly)? (?:injunction|enjoin)", re.I)),
    ("vacatur", re.compile(r"\bvacat(?:e|ed|es|ing|ur)\b|\bset(?:ting)? aside\b", re.I)),
    (
        "stay-705",
        re.compile(
            r"(?:\bsection|\bsec\.|§|U\.S\.C\.?)\s*705\b|\bpostpone\w* the effective date", re.I
        ),
    ),
)
_GRANTED: Final = re.compile(r"\bgrant(?:s|ed|ing)?\b", re.I)
_DENIED: Final = re.compile(r"\bden(?:y|ies|ied|ying)\b", re.I)


class SearchWindow(BaseModel):
    """One window: entries filed on or after ``start`` and before ``end``.

    Upstream's entry-date filters are inclusive at both ends, so the request
    carries ``end`` less a day, and two windows sharing a boundary date never
    both hold an entry filed on it.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    start: date
    end: date

    @model_validator(mode="after")
    def _ordered(self) -> SearchWindow:
        if self.end <= self.start:
            raise ValueError(f"window {self.name!r} ends on or before it starts")
        return self

    def params(self) -> dict[str, str]:
        """The window's entry-date filters, both inclusive as upstream reads them."""
        return {
            "entry_date_filed_after": self.start.isoformat(),
            "entry_date_filed_before": (self.end - timedelta(days=1)).isoformat(),
        }


class SearchQuery(BaseModel):
    """One query: a name and upstream's search filters, verbatim."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    params: dict[str, str]
    #: A control: read for its upstream ``count`` alone, one page a window,
    #: with its results neither kept as hits nor counted toward recall.
    count_only: bool = False

    def page_cap(self, default: int) -> int:
        """The pages one search of this query may read."""
        return 1 if self.count_only else default

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

    def digest(self) -> str:
        """The searches' identity: the windows, queries and page cap, not the run cap or gold set.

        A resumed scan carries a prior report forward only under the same
        digest, so a retuned query never resumes another query's pages.
        """
        payload = self.model_dump_json(include={"windows", "queries", "max_pages_per_search"})
        return hashlib.sha256(payload.encode()).hexdigest()

    def worst_case_requests(self) -> int:
        """Every search at its page cap: the most a run of this config can ask for."""
        return sum(query.page_cap(self.max_pages_per_search) for query, _window in self.searches())

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
    date_filed: str | None = None
    searches: list[str] = Field(default_factory=list)
    entries: list[MatchedEntry] = Field(default_factory=list)
    more_entries: bool = False


class SearchOutcome(BaseModel):
    """What one query in one window cost and returned."""

    model_config = ConfigDict(extra="forbid")

    search: str
    query: str
    window: str
    count_only: bool = False
    pages: int = 0
    count: int | None = None
    results: int = 0
    district: int = 0
    other_courts: int = 0
    unparsed: int = 0
    truncated: bool = False
    error: str | None = None
    #: Read to its end, or to its page cap; a later run skips it.
    done: bool = False
    #: The next page's link when a run stopped mid-search, so the next run
    #: resumes there rather than from the first page.
    resume_link: str | None = None
    #: The runs this search failed in. It restarts once; a second failure
    #: settles it as done with its error, so one bad search cannot hold the
    #: scan open.
    failures: int = 0


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
    #: The config's search digest (:meth:`OrderScanConfig.digest`).
    config_digest: str = ""
    requests: int = 0
    #: Which run of a resumed scan this is (1 for a fresh scan), and the
    #: requests every run of it has spent.
    run: int = 1
    requests_total: int = 0
    #: Every configured search is done: the next run starts a fresh scan.
    complete: bool = False
    #: The searches this run sent a request for.
    attempted: list[str] = Field(default_factory=list)
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


def _merge(
    hits: dict[int, ScanHit], result: Mapping[str, Any], search: str
) -> Literal["district", "other", "unparsed"]:
    """Fold one result into the hits, saying whether it was a district docket.

    A result naming no docket id or no court is ``unparsed``, counted apart from
    the other courts so that a renamed upstream field reads as a fault rather
    than as a search that found only circuit dockets.
    """
    docket_id = _int(result.get("docket_id"))
    court = _text(result.get("court_id"))
    if docket_id is None or not court:
        return "unparsed"
    if not DISTRICT_COURT.fullmatch(court):
        return "other"
    hit = hits.get(docket_id)
    if hit is None:
        hit = hits[docket_id] = ScanHit(
            docket_id=docket_id,
            court=court,
            docket_number=_text(result.get("docketNumber")),
            date_filed=_text(result.get("dateFiled"))[:10] or None,
        )
    if search not in hit.searches:
        hit.searches.append(search)
    seen = {(e.entry_number, e.document_id) for e in hit.entries}
    documents = result.get("recap_documents")
    for doc in documents if isinstance(documents, list) else []:
        if isinstance(doc, Mapping):
            entry = _entry(doc)
            key = (entry.entry_number, entry.document_id)
            # An entry with neither id is kept as it comes: there is nothing to
            # tell two of them apart by.
            if key == (None, None) or key not in seen:
                seen.add(key)
                hit.entries.append(entry)
    hit.more_entries = hit.more_entries or bool(result.get("more_docs"))
    return "district"


def _fetch(
    client: CourtListenerClient,
    report: OrderScanReport,
    outcome: SearchOutcome,
    params: Mapping[str, str],
    next_url: str | None,
) -> dict[str, Any]:
    """One search page, refused before the request that would pass the run cap."""
    if next_url is not None:
        # Checked before the cap and the count: a refused link sends nothing.
        params = client.search_link_params(next_url)
    if report.requests >= report.max_requests:
        raise _RunCapReached(f"run cap of {report.max_requests} requests reached")
    report.requests += 1
    page = client.search(params)
    outcome.pages += 1
    return page


def _read_page(
    page: Mapping[str, Any], outcome: SearchOutcome, hits: dict[int, ScanHit]
) -> str | None:
    """Fold one page's results into the hits; the next page's link, if any."""
    if outcome.count is None:
        outcome.count = _int(page.get("count"))
    results = page.get("results")
    if not isinstance(results, list):
        raise ValueError("search page carries no results list")
    for result in results:
        outcome.results += 1
        kind = _merge(hits, result, outcome.search) if isinstance(result, Mapping) else "unparsed"
        if kind == "district":
            outcome.district += 1
        elif kind == "other":
            outcome.other_courts += 1
        else:
            outcome.unparsed += 1
    next_url = page.get("next")
    return next_url if isinstance(next_url, str) and next_url else None


#: The runs a search may fail in before it is settled as done with its error.
MAX_SEARCH_FAILURES = 2


def _run_search(
    client: CourtListenerClient,
    report: OrderScanReport,
    outcome: SearchOutcome,
    params: Mapping[str, str],
    page_cap: int,
    kept: dict[int, ScanHit],
) -> str | None:
    """Read one search from its resume link (or first page); the stop reason, if any."""
    link = outcome.resume_link
    outcome.resume_link = None
    try:
        page = _fetch(client, report, outcome, params, link)
        while True:
            next_url = _read_page(page, outcome, kept)
            if next_url is None:
                outcome.done = True
                return None
            if outcome.pages >= page_cap:
                outcome.truncated = not outcome.count_only
                outcome.done = True
                return None
            link = next_url
            page = _fetch(client, report, outcome, params, link)
    except (_RunCapReached, RateBudgetExceeded, httpx.HTTPError, ValueError) as exc:
        stop = _stop_reason(exc)
        if stop is None:
            # A failed search restarts from its first page on the next run,
            # once; the pages read before the fault stay merged.
            outcome.error = f"{type(exc).__name__}: {exc}"
            outcome.truncated = outcome.pages > 0
            outcome.failures += 1
            outcome.done = outcome.failures >= MAX_SEARCH_FAILURES
            return None
        # A wall: the next run resumes at the page this one could not read.
        outcome.resume_link = link
        return stop


def scan(
    client: CourtListenerClient,
    config: OrderScanConfig,
    *,
    max_requests: int,
    prior: OrderScanReport | None = None,
    now: datetime | None = None,
) -> OrderScanReport:
    """Run every search not yet done, stopping cleanly at a run-level wall.

    ``prior`` is the previous run's report. Its finished searches are carried
    over unread, a search it stopped in resumes at the page it could not read,
    a failed one restarts (once: a second failure settles it), and its hits
    are kept and added to. A complete prior report (every search done) starts a
    fresh scan, as no prior does, and so does one made under another config
    digest.
    """
    digest = config.digest()
    if prior is not None and (prior.complete or prior.config_digest != digest):
        prior = None
    report = OrderScanReport(
        generated_at=(now or datetime.now(UTC)).isoformat(timespec="seconds"),
        max_requests=max_requests,
        config_digest=digest,
        run=prior.run + 1 if prior is not None else 1,
    )
    before = {o.search: o for o in prior.searches} if prior is not None else {}
    hits = {hit.docket_id: hit.model_copy(deep=True) for hit in (prior.hits if prior else [])}
    for query, window in config.searches():
        name = f"{query.name}/{window.name}"
        carried = before.get(name)
        if carried is not None and (carried.done or report.stopped is not None):
            report.searches.append(carried.model_copy(deep=True))
            continue
        if report.stopped is not None:
            continue
        if carried is not None and carried.error is None and carried.resume_link:
            outcome = carried.model_copy(deep=True)
        else:
            outcome = SearchOutcome(
                search=name,
                query=query.name,
                window=window.name,
                count_only=query.count_only,
                failures=carried.failures if carried is not None else 0,
            )
        params = {**query.params, "type": "r", **window.params()}
        sent = report.requests
        # A control's results are read for the counts and then dropped.
        kept: dict[int, ScanHit] = {} if query.count_only else hits
        stop = _run_search(
            client, report, outcome, params, query.page_cap(config.max_pages_per_search), kept
        )
        if report.requests > sent:
            report.attempted.append(name)
        report.searches.append(outcome)
        report.stopped = stop
    done = {o.search for o in report.searches if o.done}
    names = [f"{q.name}/{w.name}" for q, w in config.searches()]
    report.deferred = [name for name in names if name not in done]
    report.complete = not report.deferred
    report.requests_total = (prior.requests_total if prior is not None else 0) + report.requests
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
    lines = [
        f"order-scan plan: {len(searches)} searches "
        + f"({len(config.queries)} queries x {len(config.windows)} windows), "
        + f"up to {config.max_pages_per_search} pages each (one for a count-only control); "
        + f"worst case {config.worst_case_requests()} requests, run cap {max_requests} "
        + f"(at most {-(-config.worst_case_requests() // max_requests)} runs)",
    ]
    for query, window in searches:
        filters = ", ".join(f"{key}={value!r}" for key, value in sorted(query.params.items()))
        pages = query.page_cap(config.max_pages_per_search)
        lines.append(
            f"  {query.name}/{window.name}: entries {window.start} to {window.end} (exclusive), "
            + f"up to {pages} page{'s' if pages != 1 else ''}; {filters}"
        )
    if config.gold:
        lines.append(f"gold set: {len(config.gold)} dockets")
    return lines


def _printable(text: str, limit: int = 160) -> str:
    """An error string fit for a fenced summary: one line, no backticks, bounded."""
    flat = " ".join(text.replace("`", "'").split())
    return flat if len(flat) <= limit else flat[: limit - 3] + "..."


def failure(report: OrderScanReport) -> str | None:
    """Why the run should fail its job, though the report stands; None when it should not.

    A refused credential, or a run in which every search it sent a request
    for failed, yields a report with nothing new that would otherwise read as
    a quiet result.
    """
    if report.stopped is not None and "HTTP 401" in report.stopped:
        return report.stopped
    ran = [o for o in report.searches if o.search in report.attempted]
    if ran and all(outcome.error for outcome in ran):
        return "every search failed"
    return None


def summary_lines(report: OrderScanReport) -> list[str]:
    """A short plain-text reading of a report, for the run log and summary."""
    finished = sum(o.done for o in report.searches)
    total = finished + len(report.deferred)
    state = "complete" if report.complete else f"{len(report.deferred)} searches to go"
    lines = [
        f"order-scan run {report.run}: {len(report.hits)} district dockets, "
        + f"{finished} of {total} searches done ({state}); "
        + f"{report.requests} of {report.max_requests} requests this run, "
        + f"{report.requests_total} over the scan",
    ]
    if report.stopped:
        lines.append(f"stopped: {_printable(report.stopped)}")
    for outcome in report.searches:
        flag = (
            " (truncated)" if outcome.truncated else " (count only)" if outcome.count_only else ""
        )
        progress = "" if outcome.done else " (resumes next run)"
        here = " *" if outcome.search in report.attempted else ""
        error = f" error: {_printable(outcome.error)}" if outcome.error else ""
        lines.append(
            f"  {outcome.search}{here}: count {outcome.count}, {outcome.pages} pages, "
            + f"{outcome.district} district / {outcome.other_courts} other / "
            + f"{outcome.unparsed} unparsed{flag}{progress}{error}"
        )
    if report.attempted:
        lines.append("  (* read this run)")
    for window, count in sorted(report.hits_by_window.items()):
        lines.append(f"  window {window}: {count} dockets")
    if report.gold:
        lines.append(f"gold recall: {report.gold_found} of {len(report.gold)}")
        missed = [f"{g.court} {g.docket_number}" for g in report.gold if not g.found]
        if missed:
            lines.append("  missed: " + "; ".join(missed))
    return lines
