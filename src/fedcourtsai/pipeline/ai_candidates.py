"""The AI-case candidate check: newly filed federal cases the watchlist may want.

The AI-case watchlist (``config/ai-watchlist.yaml``) is hand-curated, and
nothing else finds new filings. This module runs a reviewed set of saved
CourtListener searches (``config/ai-candidates.yaml``) over the dockets filed in
a recent window, drops what is already known, and renders what is left as one
comment for the long-lived ``ai-candidates`` issue, where the maintainer reads
each candidate against the watchlist's rule and adds it by a PR or leaves it.

**Candidates, not decisions.** Nothing here writes the watchlist, the corpus,
the ledger or ``data/``, and no model judges fit. A search names the watchlist
category it suggests, so each candidate carries a suggestion; the maintainer
assigns the category when a case is added.

**Known dockets drop out.** A result is dropped when the watchlist names its
docket (a listed case's own or a related row) or when an earlier run already
raised it. The raised set is read back from this check's own comments on the
issue (:func:`raised_docket_ids`), each of which carries the docket ids it
raised in a marker line, so a candidate is raised once whether it was added,
dismissed or left alone, and the issue is the record of what was raised.
Only comments the posting identity wrote are read, so a comment anyone else
writes cannot hide a candidate. That identity is the workflow's ambient
``GITHUB_TOKEN`` (:data:`POSTING_LOGINS`): a job that posted with any other
token would match no marker and raise its whole lookback again every run.

**What a comment republishes.** Court-record identifiers (court, docket
number, filing date), the names of the searches that matched, the suggested
category, and a link to the docket on CourtListener by id alone
(:func:`docket_url`). No caption, party, entry text or CourtListener value-add
field such as nature of suit is copied, not even as a link's slug: these are
dockets nobody has vetted, and a caption can name an individual party.

**Federal district courts and circuits only.** A district docket counts when
its number's case type is configured (civil and multidistrict); a circuit's
and the JPML's always count; every other court is counted and dropped.

**Bounded spend.** A search page is one request; a search stops at its page
cap and the run before the request that would pass its run cap. A wall (the
cap, the rate governor's budget, persistent throttling, a refused credential)
stops the run with the searches it did not reach reported deferred, and what
the finished searches found is still raised. The lookback window is longer
than the cadence, so a deferred search is caught up by the next run.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Final, Literal

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..agent_feedback import GhRunner, _gh, find_or_create_issue
from ..ai_watchlist import AiWatchlist
from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_throttled

#: Upstream's search filters a saved search may set. The search type, the
#: filing-date bound and the ordering come from the check, not the search.
SEARCH_PARAMS: Final = frozenset(
    {"q", "case_name", "description", "docket_number", "nature_of_suit", "cause", "party_name"}
)

#: A CourtListener district-court id: the state letters and a trailing ``d``.
DISTRICT_COURT: Final = re.compile(r"[a-z]{2,4}d")
#: The courts of appeals and the JPML, which count whatever their docket number.
APPELLATE_COURT: Final = re.compile(r"ca(?:[1-9]|1[01])|cadc|cafc|jpml")
#: The most candidates one comment raises, which keeps a comment far under
#: GitHub's 65,536-character limit; the rest wait for the next run.
MAX_ROWS: Final = 150
#: What a docket number may show in a comment: upstream text, so anything that
#: could open markup, a link or a mention is replaced.
_UNSAFE: Final = re.compile(r"[^A-Za-z0-9:._ /-]")
#: A district docket number's case type: ``3:26-cv-12826`` reads ``cv``.
_CASE_TYPE: Final = re.compile(r"^\d+:\d{2}-([a-z]+)-")

#: The marker line a rendered comment opens with; the docket ids it raised follow.
RAISED_MARKER: Final = "<!-- ai-candidates-raised:"
#: The leading lines of a posted comment the marker is looked for in: the
#: rendered first line, below the once-only key ``post-issue-comment`` prepends.
MARKER_LINES: Final = 2
#: The comment author whose markers count: the workflow's ambient token, as
#: ``gh`` names it (GraphQL drops the ``[bot]`` suffix the REST API keeps).
POSTING_LOGINS: Final = frozenset({"github-actions", "github-actions[bot]", "app/github-actions"})
#: The non-triggering label of the one long-lived issue the comments go to.
LABEL: Final = "ai-candidates"
LABEL_COLOR: Final = "5319e7"
LABEL_DESCRIPTION: Final = "Weekly AI-case watchlist candidates (fedcourts ai-candidates)"
ISSUE_TITLE: Final = "AI watchlist candidates"
ISSUE_BODY: Final = (
    "Long-lived issue for `fedcourts ai-candidates`: each run's newly filed "
    "federal cases that matched a saved search in `config/ai-candidates.yaml` "
    "and are not on the watchlist. Read each against the rule in "
    "`config/ai-watchlist.yaml`; add a case by a PR that cites the rule on a "
    "dated `added` line, or leave it. A candidate is raised once. Close this "
    "issue only to retire the check: a fresh one opens on the next run, and the "
    "raised set is read from every issue under this label."
)

SearchType = Literal["d", "r"]


class SavedSearch(BaseModel):
    """One saved search: upstream's filters, its type, and the category it suggests."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    type: SearchType
    params: dict[str, str]
    #: Require the config's ``ai_terms`` in the docket's documents (``q``).
    ai_terms: bool = False
    category: str | None = None

    @field_validator("params")
    @classmethod
    def _known(cls, value: dict[str, str]) -> dict[str, str]:
        unknown = sorted(set(value) - SEARCH_PARAMS)
        if unknown:
            raise ValueError(
                f"unknown search parameters {unknown}; allowed: {sorted(SEARCH_PARAMS)}"
            )
        if any(not text.strip() for text in value.values()):
            raise ValueError("a search parameter may not be empty")
        return value

    @model_validator(mode="after")
    def _searches_something(self) -> SavedSearch:
        if not self.params and not self.ai_terms:
            raise ValueError(f"search {self.name!r} needs a parameter or ai_terms")
        if self.ai_terms and self.type != "r":
            # A docket search reads no document text, so the phrases would
            # match only captions and docket fields.
            raise ValueError(f"search {self.name!r} reads ai_terms, so its type must be r")
        return self


class CandidatesConfig(BaseModel):
    """``config/ai-candidates.yaml``: the caps, the window, the court rule and the searches."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    max_requests_per_run: int = Field(gt=0)
    max_pages_per_search: int = Field(gt=0)
    lookback_days: int = Field(gt=0)
    district_case_types: list[str] = Field(min_length=1)
    ai_terms: str = Field(min_length=1)
    searches: list[SavedSearch] = Field(min_length=1)

    @model_validator(mode="after")
    def _distinct(self) -> CandidatesConfig:
        names = [search.name for search in self.searches]
        if len(set(names)) != len(names):
            raise ValueError(f"search names must be distinct: {names}")
        return self

    def check_categories(self, watchlist: AiWatchlist) -> None:
        """Refuse a search suggesting a category the watchlist does not define."""
        for search in self.searches:
            if search.category is not None and search.category not in watchlist.categories:
                raise ValueError(
                    f"search {search.name!r}: category {search.category!r} is not one of "
                    f"{sorted(watchlist.categories)}"
                )

    def worst_case_requests(self) -> int:
        """Every search at its page cap."""
        return len(self.searches) * self.max_pages_per_search

    def params(self, search: SavedSearch, filed_after: date) -> dict[str, str]:
        """The request's filters: the search's own, its type, the window and the order."""
        params = dict(search.params)
        if search.ai_terms:
            own = params.get("q")
            params["q"] = f"({self.ai_terms}) AND ({own})" if own else self.ai_terms
        params["type"] = search.type
        params["filed_after"] = filed_after.isoformat()
        params["order_by"] = "dateFiled desc"
        return params


def load_candidates_config(path: Path, watchlist: AiWatchlist) -> CandidatesConfig:
    """Read and validate the config, its suggested categories against the watchlist's."""
    config = CandidatesConfig.model_validate(yaml.safe_load(path.read_text()))
    config.check_categories(watchlist)
    return config


class Candidate(BaseModel):
    """One docket a search found that the watchlist does not name and no run has raised."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    court: str
    docket_number: str
    date_filed: str | None = None
    url: str
    searches: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)


class SearchOutcome(BaseModel):
    """What one search read."""

    model_config = ConfigDict(extra="forbid")

    search: str
    count: int | None = None
    pages: int = 0
    results: int = 0
    kept: int = 0
    out_of_scope: int = 0
    unparsed: int = 0
    truncated: bool = False
    error: str | None = None


class CandidatesReport(BaseModel):
    """One run: its window and spend, each search's reading, and the new candidates."""

    model_config = ConfigDict(extra="forbid")

    generated_at: str
    filed_after: str
    max_requests: int
    requests: int = 0
    stopped: str | None = None
    deferred: list[str] = Field(default_factory=list)
    searches: list[SearchOutcome] = Field(default_factory=list)
    #: Dockets found in scope, before the known ones are dropped.
    found: int = 0
    on_watchlist: int = 0
    already_raised: int = 0
    candidates: list[Candidate] = Field(default_factory=list)


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


def in_scope(court: str, docket_number: str, case_types: Iterable[str]) -> bool:
    """Whether a docket is one the watchlist's rule can admit.

    A district docket whose number carries no readable case type is kept: an
    unfamiliar number format is a reason to look, not to drop.
    """
    if APPELLATE_COURT.fullmatch(court):
        return True
    if not DISTRICT_COURT.fullmatch(court):
        return False
    match = _CASE_TYPE.match(docket_number)
    return match is None or match.group(1) in set(case_types)


def docket_url(docket_id: int) -> str:
    """The docket's CourtListener page by id alone.

    Upstream's own path ends in a slug of the caption, which can name an
    individual party in a docket nobody has vetted; the bare id path redirects
    to the same page without putting that slug in a public comment.
    """
    return f"https://www.courtlistener.com/docket/{docket_id}/"


_DATE: Final = re.compile(r"\d{4}-\d{2}-\d{2}")


def _fold(
    found: dict[int, Candidate],
    result: Mapping[str, Any],
    search: SavedSearch,
    case_types: Sequence[str],
) -> Literal["kept", "out-of-scope", "unparsed"]:
    docket_id = _int(result.get("docket_id"))
    court = _text(result.get("court_id"))
    if docket_id is None or not court:
        return "unparsed"
    number = _text(result.get("docketNumber"))
    if not in_scope(court, number, case_types):
        return "out-of-scope"
    hit = found.get(docket_id)
    if hit is None:
        hit = found[docket_id] = Candidate(
            docket_id=docket_id,
            court=court,
            docket_number=number,
            date_filed=filed
            if _DATE.fullmatch(filed := _text(result.get("dateFiled"))[:10])
            else None,
            url=docket_url(docket_id),
        )
    if search.name not in hit.searches:
        hit.searches.append(search.name)
    if search.category is not None and search.category not in hit.categories:
        hit.categories.append(search.category)
    return "kept"


def _run_search(
    client: CourtListenerClient,
    report: CandidatesReport,
    config: CandidatesConfig,
    search: SavedSearch,
    params: Mapping[str, str],
    found: dict[int, Candidate],
) -> tuple[SearchOutcome, str | None]:
    """Read one search to its page cap; its outcome and the run's stop reason, if any."""
    outcome = SearchOutcome(search=search.name)
    link: str | None = None
    try:
        while True:
            request = client.search_link_params(link) if link is not None else params
            if report.requests >= report.max_requests:
                raise _RunCapReached(f"run cap of {report.max_requests} requests reached")
            report.requests += 1
            page = client.search(request)
            outcome.pages += 1
            if outcome.count is None:
                outcome.count = _int(page.get("count"))
            results = page.get("results")
            if not isinstance(results, list):
                raise ValueError("search page carries no results list")
            for result in results:
                outcome.results += 1
                kind = (
                    _fold(found, result, search, config.district_case_types)
                    if isinstance(result, Mapping)
                    else "unparsed"
                )
                if kind == "kept":
                    outcome.kept += 1
                elif kind == "out-of-scope":
                    outcome.out_of_scope += 1
                else:
                    outcome.unparsed += 1
            next_url = page.get("next")
            if not isinstance(next_url, str) or not next_url:
                return outcome, None
            if outcome.pages >= config.max_pages_per_search:
                outcome.truncated = True
                return outcome, None
            link = next_url
    except (_RunCapReached, RateBudgetExceeded, httpx.HTTPError, ValueError) as exc:
        stop = _stop_reason(exc)
        if stop is None:
            outcome.error = f"{type(exc).__name__}: {exc}"
            outcome.truncated = outcome.pages > 0
        return outcome, stop


def check(
    client: CourtListenerClient,
    config: CandidatesConfig,
    watchlist: AiWatchlist,
    *,
    raised: Iterable[int] = (),
    max_requests: int,
    now: datetime | None = None,
) -> CandidatesReport:
    """Run every saved search over the window and keep the dockets nobody knows yet.

    ``raised`` is the docket ids earlier runs raised (:func:`raised_docket_ids`).
    A search the run could not reach is reported deferred; what the finished
    searches found is kept either way.
    """
    moment = now or datetime.now(UTC)
    filed_after = moment.date() - timedelta(days=config.lookback_days)
    report = CandidatesReport(
        generated_at=moment.isoformat(timespec="seconds"),
        filed_after=filed_after.isoformat(),
        max_requests=max_requests,
    )
    found: dict[int, Candidate] = {}
    for search in config.searches:
        if report.stopped is not None:
            report.deferred.append(search.name)
            continue
        outcome, stop = _run_search(
            client, report, config, search, config.params(search, filed_after), found
        )
        report.searches.append(outcome)
        if stop is not None:
            report.stopped = stop
            report.deferred.append(search.name)
    listed = {docket_id for case in watchlist.cases for _court, docket_id in case.dockets()}
    seen = set(raised)
    known = listed | seen
    report.found = len(found)
    report.on_watchlist = sum(docket_id in listed for docket_id in found)
    report.already_raised = sum(
        docket_id in seen and docket_id not in listed for docket_id in found
    )
    report.candidates = sorted(
        (hit for docket_id, hit in found.items() if docket_id not in known),
        key=lambda hit: (hit.date_filed or "", hit.court, hit.docket_number),
        reverse=True,
    )
    return report


def raised_docket_ids(comments: Iterable[Mapping[str, Any]]) -> set[int]:
    """The docket ids this check's earlier comments raised.

    ``comments`` are issue comments as ``gh issue view --json comments`` lists
    them (``author.login`` and ``body``). Only a comment by the posting identity
    counts, and only its leading :data:`MARKER_LINES` lines are read (the post
    puts its own once-only key above the marker), so a quoted marker further
    down a body, or a comment anyone else writes, decides nothing.
    """
    raised: set[int] = set()
    for comment in comments:
        author = comment.get("author")
        login = author.get("login") if isinstance(author, Mapping) else None
        if login not in POSTING_LOGINS:
            continue
        for raw in _text(comment.get("body")).splitlines()[:MARKER_LINES]:
            line = raw.strip()
            if line.startswith(RAISED_MARKER) and line.endswith("-->"):
                inner = line[len(RAISED_MARKER) : -len("-->")]
                raised.update(int(token) for token in inner.split() if token.isdigit())
    return raised


def candidates_issue(repo: str, *, runner: GhRunner = _gh) -> int:
    """The long-lived ``ai-candidates`` issue's number, opened (with its label) if absent."""
    return find_or_create_issue(
        repo=repo,
        label=LABEL,
        label_color=LABEL_COLOR,
        label_description=LABEL_DESCRIPTION,
        title=ISSUE_TITLE,
        body=ISSUE_BODY,
        runner=runner,
    )


def issue_comments(repo: str, *, runner: GhRunner = _gh) -> list[dict[str, Any]]:
    """Every comment on every issue under :data:`LABEL`, open or closed.

    Closed issues are read too, so retiring an issue and opening a fresh one
    does not forget what was raised on the old one.
    """
    issues = json.loads(
        runner(
            [
                "gh",
                "issue",
                "list",
                "--repo",
                repo,
                "--label",
                LABEL,
                "--state",
                "all",
                "--limit",
                "100",
                "--json",
                "number",
            ]
        )
        or "[]"
    )
    comments: list[dict[str, Any]] = []
    for issue in issues if isinstance(issues, list) else []:
        number = issue.get("number") if isinstance(issue, dict) else None
        if not isinstance(number, int):
            continue
        view = json.loads(
            runner(["gh", "issue", "view", str(number), "--repo", repo, "--json", "comments"])
            or "{}"
        )
        listed = view.get("comments") if isinstance(view, dict) else None
        comments.extend(c for c in listed or [] if isinstance(c, dict))
    return comments


def render_comment(report: CandidatesReport) -> str:
    """The issue comment for a run's candidates; empty when there are none to raise.

    At most :data:`MAX_ROWS` candidates, newest first, are raised; the rest are
    left out of the marker, so the next run raises them while its lookback
    still reaches them.
    """
    shown = report.candidates[:MAX_ROWS]
    if not shown:
        return ""
    ids = " ".join(str(hit.docket_id) for hit in shown)
    count = len(shown)
    lines = [
        f"{RAISED_MARKER} {ids} -->",
        f"### {count} new AI-case candidate{'s' if count != 1 else ''} "
        + f"({report.generated_at[:10]})",
        "",
        f"Federal dockets filed since {report.filed_after} that matched a saved search in "
        + "`config/ai-candidates.yaml` and are not on the watchlist or raised before. "
        + "Read each against the rule in `config/ai-watchlist.yaml`: add a case by a PR "
        + "that cites the rule on a dated `added` line, or leave it. "
        + "Each is raised once.",
        "",
        "| Court | Docket | Filed | Matched | Suggested category |",
        "| --- | --- | --- | --- | --- |",
    ]
    for hit in shown:
        number = _UNSAFE.sub("-", hit.docket_number) or str(hit.docket_id)
        lines.append(
            f"| {hit.court} | [{number}]({hit.url}) | {hit.date_filed or '?'} | "
            + f"{', '.join(hit.searches)} | {', '.join(hit.categories) or '—'} |"
        )
    held = len(report.candidates) - count
    if held:
        lines += ["", f"{held} older candidates are held for the next run."]
    lines += ["", *_footer(report)]
    return "\n".join(lines) + "\n"


def _footer(report: CandidatesReport) -> list[str]:
    lines = [
        f"Requests: {report.requests} of {report.max_requests}. "
        + f"Found {report.found} dockets in scope; {report.on_watchlist} already on the "
        + f"watchlist, {report.already_raised} raised before."
    ]
    truncated = [o.search for o in report.searches if o.truncated]
    if truncated:
        lines.append("Truncated at the page cap (narrow the search): " + ", ".join(truncated) + ".")
    failed = [o.search for o in report.searches if o.error]
    if failed:
        lines.append("Failed: " + ", ".join(failed) + " (see the run log).")
    if report.deferred:
        lines.append(
            "Not reached this run, caught up by the next: " + ", ".join(report.deferred) + "."
        )
    return lines


def _printable(text: str, limit: int = 160) -> str:
    flat = " ".join(text.replace("`", "'").split())
    return flat if len(flat) <= limit else flat[: limit - 3] + "..."


def failure(report: CandidatesReport) -> str | None:
    """Why the run should fail its job though its report stands; None when it should not.

    A refused credential, a run stopped before its first request, or a run in
    which every search it reached failed, would otherwise read as a quiet week.
    """
    if report.stopped is not None and "HTTP 401" in report.stopped:
        return report.stopped
    if report.stopped is not None and report.requests == 0:
        # Stopped before its first request (a spent budget): nothing was read,
        # which a quiet week must not be mistaken for.
        return report.stopped
    if report.searches and all(outcome.error for outcome in report.searches):
        return "every search failed"
    return None


def summary_lines(report: CandidatesReport) -> list[str]:
    """A short plain-text reading of a run, for the log and the step summary."""
    lines = [
        f"ai-candidates: {len(report.candidates)} new candidates from dockets filed since "
        + f"{report.filed_after}; {report.found} in scope, {report.on_watchlist} on the "
        + f"watchlist, {report.already_raised} raised before; "
        + f"{report.requests} of {report.max_requests} requests",
    ]
    if report.stopped:
        lines.append(f"stopped: {_printable(report.stopped)}")
    for outcome in report.searches:
        flag = " (truncated)" if outcome.truncated else ""
        error = f" error: {_printable(outcome.error)}" if outcome.error else ""
        lines.append(
            f"  {outcome.search}: count {outcome.count}, {outcome.pages} pages, "
            + f"{outcome.kept} kept / {outcome.out_of_scope} out of scope / "
            + f"{outcome.unparsed} unparsed{flag}{error}"
        )
    if report.deferred:
        lines.append("  deferred: " + ", ".join(report.deferred))
    for hit in report.candidates:
        lines.append(
            f"  new: {hit.court} {_printable(hit.docket_number, 40)} filed {hit.date_filed} "
            + f"[{', '.join(hit.searches)}]"
        )
    return lines


def plan_lines(config: CandidatesConfig, *, max_requests: int, today: date) -> list[str]:
    """The searches a run would make and its worst-case spend, with no request sent."""
    filed_after = today - timedelta(days=config.lookback_days)
    lines = [
        f"ai-candidates plan: {len(config.searches)} searches over dockets filed since "
        + f"{filed_after}, up to {config.max_pages_per_search} pages each; worst case "
        + f"{config.worst_case_requests()} requests, run cap {max_requests}",
    ]
    for search in config.searches:
        filters = ", ".join(
            f"{key}={value!r}"
            for key, value in sorted(config.params(search, filed_after).items())
            if key not in {"filed_after", "order_by"}
        )
        category = f" [{search.category}]" if search.category else ""
        lines.append(f"  {search.name}{category}: {filters}")
    return lines
