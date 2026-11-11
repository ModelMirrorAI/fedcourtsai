"""Follow-on dockets of the AI watchlist's cases, and listed dockets gone stale.

A listed case that is appealed, swept into a multidistrict proceeding or
brought to the Supreme Court gets a new docket, and nothing in the watchlist
(``config/ai-watchlist.yaml``) links it back until a maintainer adds a
``related`` row. Three readings here notice what the list does not yet name,
each against a source the watchlist did not produce:

- **Circuit and panel dockets** (:func:`check`), from CourtListener. One search
  per listed district docket asks the courts of appeals and the JPML for
  recently filed dockets that carry the listed docket's number. A new hit in a
  circuit that could hear the listed district's appeals is then read once, so
  its own originating-case fields say whether it reviews the listed case; a hit
  in any other regional circuit is another court's case with the same number.
  A hit is rendered as a candidate comment for the long-lived
  ``ai-candidates`` issue, marked with the listed case it is related to.
- **Supreme Court dockets** (:func:`scotus_follow_ons`), from the corpus. A
  SCOTUS row whose lower-court docket is a listed docket arises from a listed
  case. The watchlist never lists a SCOTUS docket, so the caller says which
  ones the ``ai`` relation already links; the rest are the alarm.
- **Stale listed dockets** (:func:`stale_dockets`), from the corpus. A listed
  docket ``watchlist-refresh`` has not stamped for :data:`STALE_AFTER_DAYS`
  days is one the feed has stopped following.

**Candidates, not decisions.** Nothing here writes the watchlist, the corpus,
the ledger or ``data/``. A follow-on joins the list by a maintainer's PR, like
any other docket. No reading here is a scored figure or changes selection.

**Raised once.** A circuit or panel candidate's comment opens with the same
marker line the candidate check's does
(:data:`~fedcourtsai.pipeline.ai_candidates.RAISED_MARKER`), so both checks
read one raised set and neither raises what the other already has.

**What a comment republishes.** Court-record identifiers only: court, docket
number, filing date, a link by docket id, and the listed case's name, which
the watchlist already publishes. No caption, party or entry text of the
follow-on docket is copied.

**What is not found.** A district-to-district transfer carries no
originating-case field upstream, so it is not detected. A Supreme Court docket
is matched through a listed docket's own number, so a petition from an appeal
the watchlist does not yet list is found only once that appeal is listed; the
circuit reading is what raises the appeal first.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from datetime import UTC, date, datetime, timedelta
from typing import Any, Final, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus, ids
from ..ai_watchlist import AiWatchlist, Relation
from ..courtlistener import CourtListenerClient, RateBudgetExceeded, is_throttled
from .ai_candidates import (
    _UNSAFE,
    APPELLATE_COURT,
    DISTRICT_COURT,
    MAX_ROWS,
    RAISED_MARKER,
    docket_url,
)
from .decision_below import split_lower_numbers
from .ingest import live_lower_court_id

#: The courts a follow-on search asks: every court of appeals and the JPML.
FOLLOW_ON_COURTS: Final = (
    "ca1 ca2 ca3 ca4 ca5 ca6 ca7 ca8 ca9 ca10 ca11 cadc cafc jpml"  # one upstream filter
)
#: How far back a run looks for newly filed follow-on dockets. Longer than a
#: weekly cadence several times over, so a missed run is caught up by the next.
LOOKBACK_DAYS: Final = 45
#: The most requests one run spends: the ``ai-candidates`` lane's share. The
#: lane reserves one run a day, so the caller must not run both checks on one day.
MAX_REQUESTS: Final = 40
#: Days without a successful refresh after which a listed docket is stale.
STALE_AFTER_DAYS: Final = 7
#: Days after which a stored check is too old to stand for today: the corpus
#: side that produces it runs several times a day, so an older one means the
#: check itself has stopped.
MAX_READING_AGE_DAYS: Final = 2

#: A district docket number: office, two-digit year, case type, sequence.
_DISTRICT_NUMBER: Final = re.compile(r"^(\d+):(\d{2})-([a-z]{2})-(\d+)", re.IGNORECASE)
#: The same number as another court may write it: the office is optional, the
#: sequence may be unpadded, and judge initials may trail it.
_LOOSE_DISTRICT: Final = re.compile(r"^(?:\d+:)?(\d{2})-([a-z]{2})-0*(\d+)", re.IGNORECASE)
#: A circuit docket number as SCOTUS and the circuits write it: ``25-2153``,
#: the Second Circuit's ``24-1234-cv``, the Federal Circuit's ``2024-1285``.
_CIRCUIT_NUMBER: Final = re.compile(r"^(?:20)?(\d{2})-0*(\d+)(?:-[a-z]{2})?$", re.IGNORECASE)
#: The JPML's own docket for an MDL, the only panel row worth raising: its
#: per-member rows repeat the member's district number.
_MDL_NUMBER: Final = re.compile(r"^MDL No\.? ?\d+", re.IGNORECASE)
_DATE: Final = re.compile(r"\d{4}-\d{2}-\d{2}")

Origin = Literal["confirmed", "unrecorded", "mention"]

#: The regional circuit that hears each state's or territory's district courts,
#: by the letters a CourtListener district id opens with (``cand`` reads ``ca``).
_STATE_CIRCUIT: Final[dict[str, str]] = {
    **dict.fromkeys(["me", "ma", "nh", "ri", "pr"], "ca1"),
    **dict.fromkeys(["ct", "ny", "vt"], "ca2"),
    **dict.fromkeys(["de", "nj", "pa", "vi"], "ca3"),
    **dict.fromkeys(["md", "nc", "sc", "va", "wv"], "ca4"),
    **dict.fromkeys(["la", "ms", "tx"], "ca5"),
    **dict.fromkeys(["ky", "mi", "oh", "tn"], "ca6"),
    **dict.fromkeys(["il", "in", "wi"], "ca7"),
    **dict.fromkeys(["ar", "ia", "mn", "mo", "ne", "nd", "sd"], "ca8"),
    **dict.fromkeys(["ak", "az", "ca", "hi", "id", "mt", "nv", "or", "wa", "gu"], "ca9"),
    **dict.fromkeys(["co", "ks", "nm", "ok", "ut", "wy"], "ca10"),
    **dict.fromkeys(["al", "fl", "ga"], "ca11"),
}
#: District ids whose opening letters would misread: the District of Columbia
#: and the Northern Mariana Islands (``nmid``, which opens like New Mexico).
_DISTRICT_CIRCUIT: Final[dict[str, str]] = {"dcd": "cadc", "nmid": "ca9"}


def regional_circuit(district: str) -> str | None:
    """The court of appeals that hears a district court's appeals; None when unknown."""
    return _DISTRICT_CIRCUIT.get(district) or _STATE_CIRCUIT.get(district[:2])


def may_review(circuit: str, district: str) -> bool:
    """Whether a circuit could hear an appeal from a district.

    The district's regional circuit and the Federal Circuit can; a district
    whose circuit is not known rules nothing out.
    """
    regional = regional_circuit(district)
    return regional is None or circuit in {regional, "cafc"}


def number_key(number: str) -> tuple[str, ...] | None:
    """A docket number reduced to what identifies it across courts' spellings.

    ``1:20-cv-00613-SB`` and ``20-cv-613`` share a key, as do ``25-02153`` and
    ``25-2153``. The district office is dropped, since a court of appeals often
    omits it; the caller compares the court as well. ``None`` for a number in
    neither form, which then matches nothing.
    """
    text = number.strip()
    match = _LOOSE_DISTRICT.match(text)
    if match is not None:
        return (match.group(1), match.group(2).lower(), match.group(3))
    match = _CIRCUIT_NUMBER.match(text)
    if match is not None:
        return (match.group(1), match.group(2))
    return None


class ListedDocket(BaseModel):
    """One docket the watchlist names, with the listed case it belongs to."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case: str
    court: str
    docket_id: int
    docket_number: str
    added: date


def listed_dockets(watchlist: AiWatchlist) -> list[ListedDocket]:
    """Every docket the watchlist names, a case's own first, in file order."""
    listed: list[ListedDocket] = []
    for case in watchlist.cases:
        rows = [(case.court, case.docket_id, case.docket_number)] + [
            (r.court, r.docket_id, r.docket_number) for r in case.related
        ]
        listed += [
            ListedDocket(
                case=case.name,
                court=court,
                docket_id=docket_id,
                docket_number=number,
                added=case.added,
            )
            for court, docket_id, number in rows
        ]
    return listed


def searched_dockets(watchlist: AiWatchlist) -> list[ListedDocket]:
    """The listed district dockets a follow-on search is run for.

    A circuit or panel docket is itself a follow-on, and what follows it is a
    Supreme Court docket, which the corpus reading covers.
    """
    return [
        docket
        for docket in listed_dockets(watchlist)
        if DISTRICT_COURT.fullmatch(docket.court) and _DISTRICT_NUMBER.match(docket.docket_number)
    ]


class FollowOn(BaseModel):
    """One circuit or panel docket that follows a listed case and is not yet listed."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    court: str
    docket_number: str
    date_filed: str | None = None
    url: str
    #: The listed case, and the listed docket whose number the hit carries.
    related_to: str
    from_court: str
    from_docket_number: str
    #: The ``related`` relation a maintainer would most likely give it.
    relation: Relation
    #: ``confirmed``: the docket's originating case is the listed docket.
    #: ``unrecorded``: upstream holds no originating case for it yet.
    #: ``mention``: a panel docket, which records no originating case at all.
    origin: Origin


class FollowOnReport(BaseModel):
    """One run: its window and spend, and the follow-on dockets nobody knows yet."""

    model_config = ConfigDict(extra="forbid")

    generated_at: str
    filed_after: str
    max_requests: int
    requests: int = 0
    searched: int = 0
    stopped: str | None = None
    #: Listed dockets whose search the run did not reach or could not finish.
    deferred: list[str] = Field(default_factory=list)
    #: Listed dockets whose search filled its page: more hits may exist.
    truncated: list[str] = Field(default_factory=list)
    #: Searches that failed without stopping the run.
    errors: list[str] = Field(default_factory=list)
    #: Docket reads that failed; the hit is read again by the next run.
    read_errors: list[str] = Field(default_factory=list)
    #: New hits the run stopped before reading; the next run reads them.
    unread: int = 0
    hits: int = 0
    on_watchlist: int = 0
    already_raised: int = 0
    #: Circuit hits from another case: a circuit that cannot hear the listed
    #: district's appeals, or a docket whose originating case is another docket.
    other_origin: int = 0
    #: Panel rows that are not an MDL's own docket.
    panel_member_rows: int = 0
    follow_ons: list[FollowOn] = Field(default_factory=list)


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


def search_params(docket: ListedDocket, filed_after: date) -> dict[str, str]:
    """The search for dockets above a listed district docket: its number, as a phrase."""
    match = _DISTRICT_NUMBER.match(docket.docket_number)
    number = match.group(0) if match is not None else docket.docket_number
    return {
        "type": "d",
        "q": f'"{number}"',
        "court": FOLLOW_ON_COURTS,
        "filed_after": filed_after.isoformat(),
        "order_by": "dateFiled desc",
    }


def _office(number: str) -> str | None:
    match = _DISTRICT_NUMBER.match(number.strip())
    return match.group(1) if match is not None else None


def read_origin(payload: Mapping[str, Any], listed: ListedDocket) -> Origin | None:
    """What a circuit docket's own fields say about the listed docket.

    ``confirmed`` when its originating case number is the listed docket's and
    its originating court, where upstream names one, is the listed court;
    ``None`` when either names a different case; ``unrecorded`` when upstream
    holds no originating number to compare.
    """
    court_url = _text(payload.get("appeal_from")).rstrip("/")
    from_court = court_url.rsplit("/", 1)[-1] if court_url else ""
    if from_court and from_court != listed.court:
        return None
    info = payload.get("original_court_info")
    origin_number = _text(info.get("docket_number")) if isinstance(info, Mapping) else ""
    if not origin_number.strip():
        return "unrecorded"
    key = number_key(origin_number)
    if key is None or key != number_key(listed.docket_number):
        return None
    offices = {_office(origin_number), _office(listed.docket_number)}
    if not from_court and None not in offices and len(offices) > 1:
        # No originating court to compare, and the two numbers name different
        # offices: another district's case with the same sequence.
        return None
    return "confirmed"


def _spend(report: FollowOnReport) -> None:
    if report.requests >= report.max_requests:
        raise _RunCapReached(f"run cap of {report.max_requests} requests reached")
    report.requests += 1


class _Hit(BaseModel):
    """One docket a search surfaced, with every listed docket whose number it carries."""

    model_config = ConfigDict(extra="forbid")

    docket_id: int
    court: str
    docket_number: str
    date_filed: str | None
    under: list[ListedDocket] = Field(default_factory=list)


def _collect(found: dict[int, _Hit], result: Mapping[str, Any], listed: ListedDocket) -> None:
    docket_id = _int(result.get("docket_id"))
    court = _text(result.get("court_id"))
    if docket_id is None or not APPELLATE_COURT.fullmatch(court):
        return
    hit = found.get(docket_id)
    if hit is None:
        filed = _text(result.get("dateFiled"))[:10]
        hit = found[docket_id] = _Hit(
            docket_id=docket_id,
            court=court,
            docket_number=_text(result.get("docketNumber")),
            date_filed=filed if _DATE.fullmatch(filed) else None,
        )
    hit.under.append(listed)


def _follow_on(hit: _Hit, listed: ListedDocket, relation: Relation, origin: Origin) -> FollowOn:
    return FollowOn(
        docket_id=hit.docket_id,
        court=hit.court,
        docket_number=hit.docket_number,
        date_filed=hit.date_filed,
        url=docket_url(hit.docket_id),
        related_to=listed.case,
        from_court=listed.court,
        from_docket_number=listed.docket_number,
        relation=relation,
        origin=origin,
    )


def _judge(client: CourtListenerClient, report: FollowOnReport, hit: _Hit) -> FollowOn | None:
    """One new hit's verdict: a panel docket by its number, a circuit docket by one read.

    The docket is compared with every listed docket it surfaced under, so one
    that carries two listed numbers is attributed to the case it reviews.
    """
    if hit.court == "jpml":
        if not _MDL_NUMBER.match(hit.docket_number):
            report.panel_member_rows += 1
            return None
        return _follow_on(hit, hit.under[0], Relation.mdl, "mention")
    reviewable = [listed for listed in hit.under if may_review(hit.court, listed.court)]
    if not reviewable:
        report.other_origin += 1
        return None
    _spend(report)
    payload = client.get_docket(hit.docket_id)
    verdicts = [(read_origin(payload, listed), listed) for listed in reviewable]
    for wanted in ("confirmed", "unrecorded"):
        for origin, listed in verdicts:
            if origin == wanted:
                return _follow_on(hit, listed, Relation.appeal, origin)
    report.other_origin += 1
    return None


def _search_all(
    client: CourtListenerClient, report: FollowOnReport, watchlist: AiWatchlist, filed_after: date
) -> dict[int, _Hit]:
    found: dict[int, _Hit] = {}
    for listed in searched_dockets(watchlist):
        label = f"{listed.court} {listed.docket_number}"
        if report.stopped is not None:
            report.deferred.append(label)
            continue
        try:
            _spend(report)
            page = client.search(search_params(listed, filed_after))
            results = page.get("results")
            if not isinstance(results, list):
                raise ValueError("search page carries no results list")
            report.searched += 1
            if isinstance(page.get("next"), str) and page.get("next"):
                report.truncated.append(label)
            for result in results:
                if isinstance(result, Mapping):
                    _collect(found, result, listed)
        except (_RunCapReached, RateBudgetExceeded, httpx.HTTPError, ValueError) as exc:
            stop = _stop_reason(exc)
            if stop is not None:
                report.stopped = stop
                report.deferred.append(label)
            else:
                report.errors.append(f"{label}: {type(exc).__name__}: {exc}")
    return found


def check(
    client: CourtListenerClient,
    watchlist: AiWatchlist,
    *,
    raised: Iterable[int] = (),
    max_requests: int = MAX_REQUESTS,
    lookback_days: int = LOOKBACK_DAYS,
    now: datetime | None = None,
) -> FollowOnReport:
    """Search above every listed district docket and keep the follow-ons nobody knows yet.

    ``raised`` is the docket ids earlier comments raised
    (:func:`~fedcourtsai.pipeline.ai_candidates.raised_docket_ids`). Every
    search runs before any docket is read, and the new hits are then read
    newest first. A wall (the run cap, the rate budget, persistent throttling,
    a refused credential) stops the run with the searches it did not finish
    reported deferred and the hits it did not read counted unread; what was
    found before it is kept, and the rest is still inside the next run's window.
    """
    moment = now or datetime.now(UTC)
    filed_after = moment.date() - timedelta(days=lookback_days)
    report = FollowOnReport(
        generated_at=moment.isoformat(timespec="seconds"),
        filed_after=filed_after.isoformat(),
        max_requests=max_requests,
    )
    known = {docket.docket_id for docket in listed_dockets(watchlist)}
    raised_ids = set(raised)
    hits = _search_all(client, report, watchlist, filed_after)
    report.hits = len(hits)
    report.on_watchlist = sum(docket_id in known for docket_id in hits)
    report.already_raised = sum(d in raised_ids and d not in known for d in hits)
    fresh = sorted(
        (hit for d, hit in hits.items() if d not in known and d not in raised_ids),
        key=lambda hit: (hit.date_filed or "", hit.court, hit.docket_number),
        reverse=True,
    )
    for index, hit in enumerate(fresh):
        if report.stopped is not None:
            report.unread = len(fresh) - index
            break
        try:
            follow_on = _judge(client, report, hit)
        except (_RunCapReached, RateBudgetExceeded, httpx.HTTPError) as exc:
            stop = _stop_reason(exc)
            if stop is not None:
                report.stopped = stop
                report.unread = len(fresh) - index
                break
            report.read_errors.append(
                f"{hit.court} docket {hit.docket_id}: {type(exc).__name__}: {exc}"
            )
            continue
        if follow_on is not None:
            report.follow_ons.append(follow_on)
    return report


def failure(report: FollowOnReport) -> str | None:
    """Why the run should fail its job though its report stands; None when it should not.

    A refused credential, a run stopped before any search answered, or a run
    in which no search answered at all, would otherwise read as a quiet week.
    """
    if report.stopped is not None and "HTTP 401" in report.stopped:
        return report.stopped
    if report.stopped is not None and report.searched == 0:
        return report.stopped
    if report.errors and report.searched == 0:
        return "every search failed"
    return None


_ORIGIN_NOTE: Final[dict[str, str]] = {
    "confirmed": "originating case is the listed docket",
    "unrecorded": "carries the listed number; no originating case recorded yet",
    "mention": "panel docket that carries the listed number",
}


def render_comment(report: FollowOnReport) -> str:
    """The issue comment raising a run's follow-ons; empty when there are none."""
    shown = report.follow_ons[:MAX_ROWS]
    if not shown:
        return ""
    count = len(shown)
    lines = [
        f"{RAISED_MARKER} {' '.join(str(hit.docket_id) for hit in shown)} -->",
        f"### {count} follow-on docket{'s' if count != 1 else ''} of listed cases "
        + f"({report.generated_at[:10]})",
        "",
        f"Circuit and JPML dockets filed since {report.filed_after} that carry a listed "
        + "docket's number and are not on the watchlist or raised before. Add one as a "
        + "`related` row of its case in `config/ai-watchlist.yaml` by a PR, or leave it. "
        + "Each is raised once.",
        "",
        "| Court | Docket | Filed | Related to | From | Suggested relation | Basis |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for hit in shown:
        number = _UNSAFE.sub("-", hit.docket_number) or str(hit.docket_id)
        lines.append(
            f"| {hit.court} | [{number}]({hit.url}) | {hit.date_filed or '?'} | "
            + f"{hit.related_to} | {hit.from_court} {hit.from_docket_number} | "
            + f"{hit.relation.value} | {_ORIGIN_NOTE[hit.origin]} |"
        )
    held = len(report.follow_ons) - count
    if held:
        lines += ["", f"{held} older follow-ons are held for the next run."]
    lines += ["", *_footer(report)]
    return "\n".join(lines) + "\n"


def _footer(report: FollowOnReport) -> list[str]:
    lines = [
        f"Requests: {report.requests} of {report.max_requests}. {report.searched} listed "
        + f"district dockets searched; {report.hits} dockets carried a listed number, "
        + f"{report.on_watchlist} already on the watchlist, {report.already_raised} raised "
        + f"before, {report.other_origin} from another case."
    ]
    if report.truncated:
        lines.append("More hits than one page: " + ", ".join(report.truncated) + ".")
    if report.errors or report.read_errors:
        lines.append(
            f"Failed: {len(report.errors)} searches, {len(report.read_errors)} docket reads "
            + "(see the run log)."
        )
    if report.unread:
        lines.append(f"{report.unread} new hits were not read this run; the next run reads them.")
    if report.deferred:
        lines.append(
            "Not reached this run, caught up by the next: " + ", ".join(report.deferred) + "."
        )
    return lines


def _printable(text: str, limit: int = 160) -> str:
    flat = " ".join(text.replace("`", "'").split())
    return flat if len(flat) <= limit else flat[: limit - 3] + "..."


def summary_lines(report: FollowOnReport) -> list[str]:
    """A short plain-text reading of a run, for the log and the step summary."""
    lines = [
        f"ai-follow-ons: {len(report.follow_ons)} new follow-on dockets filed since "
        + f"{report.filed_after}; {report.searched} listed dockets searched, {report.hits} "
        + f"hits, {report.on_watchlist} on the watchlist, {report.already_raised} raised "
        + f"before, {report.other_origin} from another case, {report.panel_member_rows} "
        + f"panel member rows; {report.requests} of {report.max_requests} requests",
    ]
    if report.stopped:
        lines.append(f"stopped: {_printable(report.stopped)}")
    lines += [f"  error: {_printable(error)}" for error in report.errors + report.read_errors]
    if report.unread:
        lines.append(f"  unread: {report.unread} new hits")
    if report.truncated:
        lines.append("  truncated: " + ", ".join(report.truncated))
    if report.deferred:
        lines.append("  deferred: " + ", ".join(report.deferred))
    for hit in report.follow_ons:
        lines.append(
            f"  new: {hit.court} {_printable(hit.docket_number, 40)} filed {hit.date_filed} "
            + f"[{hit.relation.value}, {hit.origin}] from {hit.from_court} "
            + f"{hit.from_docket_number}"
        )
    return lines


def plan_lines(
    watchlist: AiWatchlist, *, max_requests: int, lookback_days: int, today: date
) -> list[str]:
    """The searches a run would make, with no request sent."""
    searched = searched_dockets(watchlist)
    filed_after = today - timedelta(days=lookback_days)
    lines = [
        f"ai-follow-ons plan: {len(searched)} searches (one per listed district docket) over "
        + f"circuit and JPML dockets filed since {filed_after}, plus one read per new circuit "
        + f"hit; run cap {max_requests}",
    ]
    lines += [f"  {d.court} {d.docket_number}: {d.case}" for d in searched]
    return lines


# --- The corpus readings: Supreme Court follow-ons and stale listed dockets ---


class ScotusFollowOn(BaseModel):
    """One Supreme Court docket whose lower-court docket is a listed docket."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    docket_number: str
    date_filed: str | None = None
    related_to: str
    from_court: str
    from_docket_number: str
    #: Whether the ``ai`` relation already links it to the watchlist.
    linked: bool


class StaleDocket(BaseModel):
    """One listed docket with no successful refresh inside the window."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    case: str
    docket_number: str
    #: The last refresh's date; None for a docket never refreshed.
    last_pulled: str | None = None
    days: int


class WatchlistCheck(BaseModel):
    """The corpus readings of one day: what arose at the Court, and what went stale."""

    model_config = ConfigDict(extra="forbid")

    generated_at: str
    listed: int
    stale_after_days: int
    scotus: list[ScotusFollowOn] = Field(default_factory=list)
    stale: list[StaleDocket] = Field(default_factory=list)
    #: Set when a stored check is read back: how many days old it is.
    reading_age_days: int | None = None

    @property
    def unlinked(self) -> list[ScotusFollowOn]:
        return [row for row in self.scotus if not row.linked]

    @property
    def outdated(self) -> bool:
        """A stored check too old to stand for today."""
        return self.reading_age_days is not None and (self.reading_age_days > MAX_READING_AGE_DAYS)

    @property
    def ok(self) -> bool:
        """Nothing to alarm on: a current reading with no unlinked Supreme Court
        docket and no stale listed docket."""
        return not self.unlinked and not self.stale and not self.outdated


def read_back(text: str, *, now: datetime | None = None) -> WatchlistCheck:
    """A stored check (the command's JSON) read back where no corpus is at hand.

    The reading's age is stamped on it, so a check that stopped being produced
    alarms instead of repeating its last clean answer. Raises ``ValueError``
    on anything that is not a stored check.
    """
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("a stored watchlist check is a JSON object")
    data.pop("ok", None)
    data.pop("reading_age_days", None)
    check_ = WatchlistCheck.model_validate(data)
    made = datetime.fromisoformat(check_.generated_at)
    if made.tzinfo is None:
        made = made.replace(tzinfo=UTC)
    moment = now or datetime.now(UTC)
    check_.reading_age_days = max((moment.date() - made.astimezone(UTC).date()).days, 0)
    return check_


def scotus_follow_ons(
    conn: corpus.ReadConnection,
    watchlist: AiWatchlist,
    *,
    linked: Iterable[str] = (),
) -> list[ScotusFollowOn]:
    """Every Supreme Court docket in the corpus that arises from a listed docket.

    A row matches when its lower court is a listed docket's court and one of
    its lower-court numbers is that docket's number. ``linked`` is the SCOTUS
    case ids the ``ai`` relation already ties to the watchlist; a match outside
    it is unlinked. Newest first.
    """
    wanted: dict[tuple[str, tuple[str, ...]], ListedDocket] = {}
    for docket in listed_dockets(watchlist):
        key = number_key(docket.docket_number)
        if key is not None:
            wanted.setdefault((docket.court, key), docket)
    linked_ids = set(linked)
    cursor = conn.execute(
        "SELECT case_id, docket_number, date_filed, originating_court, "
        "originating_court_name, originating_docket_number FROM cases "
        "WHERE court = 'scotus' AND originating_docket_number IS NOT NULL"
    )
    found: list[ScotusFollowOn] = []
    for row in cursor.fetchall():
        court = row["originating_court"] or live_lower_court_id(row["originating_court_name"])
        if court is None:
            continue
        for number in split_lower_numbers(row["originating_docket_number"]):
            key = number_key(number)
            listed = wanted.get((court, key)) if key is not None else None
            if listed is None:
                continue
            filed = _text(row["date_filed"])[:10]
            found.append(
                ScotusFollowOn(
                    case_id=row["case_id"],
                    docket_number=_text(row["docket_number"]),
                    date_filed=filed if _DATE.fullmatch(filed) else None,
                    related_to=listed.case,
                    from_court=listed.court,
                    from_docket_number=listed.docket_number,
                    linked=row["case_id"] in linked_ids,
                )
            )
            break
    return sorted(found, key=lambda hit: (hit.date_filed or "", hit.case_id), reverse=True)


def stale_dockets(
    conn: corpus.ReadConnection,
    watchlist: AiWatchlist,
    *,
    today: date,
    stale_after_days: int = STALE_AFTER_DAYS,
) -> list[StaleDocket]:
    """Listed dockets not refreshed for ``stale_after_days``, stalest first.

    A docket never refreshed counts from the day its case was listed, so a
    newly added case has the same window to onboard before it alarms. A
    ``related`` row carries no date of its own, so one added later to an older
    case is stale until its first refresh.
    """
    stale: list[StaleDocket] = []
    for docket in listed_dockets(watchlist):
        case_id = ids.case_id(docket.court, docket.docket_id)
        row = corpus.get_row(conn, case_id)
        last = row.last_pulled if row is not None else None
        days = (today - (last or docket.added)).days
        if days >= stale_after_days:
            stale.append(
                StaleDocket(
                    case_id=case_id,
                    case=docket.case,
                    docket_number=docket.docket_number,
                    last_pulled=last.isoformat() if last is not None else None,
                    days=days,
                )
            )
    return sorted(stale, key=lambda d: (-d.days, d.case_id))


def watchlist_check(
    conn: corpus.ReadConnection,
    watchlist: AiWatchlist,
    *,
    linked: Iterable[str] = (),
    now: datetime | None = None,
    stale_after_days: int = STALE_AFTER_DAYS,
) -> WatchlistCheck:
    """Both corpus readings for one day."""
    moment = now or datetime.now(UTC)
    return WatchlistCheck(
        generated_at=moment.isoformat(timespec="seconds"),
        listed=len(listed_dockets(watchlist)),
        stale_after_days=stale_after_days,
        scotus=scotus_follow_ons(conn, watchlist, linked=linked),
        stale=stale_dockets(
            conn, watchlist, today=moment.date(), stale_after_days=stale_after_days
        ),
    )


def digest_line(check_: WatchlistCheck) -> str:
    """The check as one line, for a digest."""
    if check_.ok:
        return (
            f"AI watchlist: {check_.listed} listed dockets current; "
            + "no unlinked Supreme Court docket."
        )
    parts = []
    if check_.outdated:
        parts.append(
            f"the last check is {check_.reading_age_days} days old "
            + f"({check_.generated_at[:10]})"
        )
    if check_.unlinked:
        parts.append(f"{len(check_.unlinked)} unlinked Supreme Court docket(s) from a listed case")
    if check_.stale:
        parts.append(
            f"{len(check_.stale)} of {check_.listed} listed dockets not refreshed in "
            + f"{check_.stale_after_days} days"
        )
    return "AI watchlist: " + "; ".join(parts) + "."


def _tick(text: str) -> str:
    """Corpus text made safe inside a code span of a table cell."""
    return _UNSAFE.sub("-", text)


def render_alarm(check_: WatchlistCheck) -> str:
    """An alarm issue's body for the check; empty when there is nothing to alarm on."""
    if check_.ok:
        return ""
    lines = [f"`fedcourts ai-watchlist-check`, {check_.generated_at[:10]}.", ""]
    if check_.outdated:
        lines += [
            f"### The check has not run for {check_.reading_age_days} days",
            "",
            "No newer reading has been published, so what follows may be out of date.",
            "",
        ]
    if check_.unlinked:
        lines += [
            "### Supreme Court dockets from a listed case that the watchlist does not link",
            "",
            "| Docket | Filed | Listed case | Lower-court docket |",
            "| --- | --- | --- | --- |",
        ]
        lines += [
            f"| `{_tick(row.docket_number)}` (`{_tick(row.case_id)}`) | "
            + f"{row.date_filed or '?'} | {row.related_to} | "
            + f"{row.from_court} {row.from_docket_number} |"
            for row in check_.unlinked
        ]
        lines.append("")
    if check_.stale:
        lines += [
            f"### Listed dockets not refreshed in {check_.stale_after_days} days",
            "",
            "| Docket | Listed case | Last refreshed | Days |",
            "| --- | --- | --- | --- |",
        ]
        lines += [
            f"| `{_tick(row.case_id)}` {row.docket_number} | {row.case} | "
            + f"{row.last_pulled or 'never'} | {row.days} |"
            for row in check_.stale
        ]
        lines.append("")
    return "\n".join(lines)
