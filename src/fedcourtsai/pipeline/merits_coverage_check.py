"""The merits coverage check: the census, set against the Court's own argument roll.

:mod:`fedcourtsai.pipeline.merits_coverage` gives every plenary grant *the
corpus knows* one status, so a grant the corpus missed is invisible to it. This
check adds a source the pipeline did not produce: the Court's Granted & Noted
list (:mod:`fedcourtsai.pipeline.granted_noted`), its roll of the cases set for
argument in a Term, with each case's grant date, argument date and decision
date. Every docket on the list must have a corpus row whose grant opens a
merits proceeding and a merits event, a forecast before its argument, a
forecast at the argued moment once argued, and a forecast before its decision.

It is monitoring, not a scored figure: every reading here is selected on what
has already happened to a case, so nothing it reports enters a board, a base
rate or a release figure. An **alarm** is a finding someone has to act on, and
the scheduled caller latches the alarms onto one issue; everything else is
reported beside them.

How long an alarm stands depends on whether it can still be closed. On a
pending case every finding (a missing row, a missing event, an argument
approaching with no forecast) alarms until it is closed. Once the case is
decided nothing can be repaired, so its findings alarm for
:data:`MISS_ALARM_DAYS` after the decision and are then carried as one standing
miss in the report: a permanent fact must not hold the alarm open forever.

A consolidated set is one argument and one opinion, so the argument and
decision checks are met by a forecast on any docket of the entry; the row and
event checks are per docket. An original-jurisdiction case and an application
set for argument are outside the merits stream's scope, and are listed apart.

Reads the corpus index and the committed predictions; writes nothing.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from datetime import date, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus, ids
from ..agent_feedback import GhRunner, _gh
from ..paths import CasePaths
from ..schemas import Moment, Stage
from . import granted_noted, moments
from .merits_coverage import (
    GAP_STATUSES,
    MeritsCoverage,
    MeritsCoverageStatus,
    MeritsCoverageTerm,
    classify_grant,
    merits_coverage,
)

#: How long after its grant a listed docket may lack a row, a merits grant or a
#: merits event before that is an alarm: the pull and the mint take a few days.
EVENT_GRACE_DAYS: Final = 7
#: A case this close to its argument (or past it) must hold a forecast.
ARGUMENT_WINDOW_DAYS: Final = 14
#: How long after argument the argued moment may go unforecast: the transcript
#: opens it, and a predict round has to reach it.
ARGUED_GRACE_DAYS: Final = 7
#: How long an unrepairable miss alarms before it becomes a standing miss.
MISS_ALARM_DAYS: Final = 28

#: The title of the one issue the scheduled check latches its alarms onto.
ISSUE_TITLE: Final = "Merits coverage failing"
#: That issue's label: a category, which starts nothing.
ISSUE_LABEL: Final = "merits-coverage"
ISSUE_LABEL_COLOR: Final = "b60205"
ISSUE_LABEL_DESCRIPTION: Final = "Long-lived merits coverage alarm (run-analytics escalation)"
#: The login the ambient workflow token writes as. Only an issue it opened is
#: the alarm: a green check closes what it matches, so matching on the label
#: alone would close anyone's issue filed under it.
ALARM_AUTHOR: Final = "github-actions[bot]"

_MERITS_EVENT_IDS: Final = frozenset(spec.event_id for spec in moments.moments_for(Stage.merits))
_ARGUED_EVENT_IDS: Final = frozenset(
    spec.event_id for spec in moments.moments_for(Stage.merits) if spec.moment == Moment.argued
)


class MeritsAlarm(StrEnum):
    """One reason a docket needs someone's attention."""

    no_corpus_row = "no_corpus_row"
    """On the Court's list, and the corpus holds no row for the docket."""
    no_merits_grant = "no_merits_grant"
    """The corpus row carries no grant that opens a merits proceeding."""
    no_merits_event = "no_merits_event"
    """A merits grant on the row, in scope, and no merits event was ever minted."""
    coverage_hole = "coverage_hole"
    """The census status is `no_event` or `not_forecastable`."""
    argument_unforecast = "argument_unforecast"
    """Argument is within the window or past, undecided, and no forecast exists."""
    argued_unforecast = "argued_unforecast"
    """Argued past the grace period, undecided, and no forecast at the argued moment."""
    decided_unforecast = "decided_unforecast"
    """Decided within the alarm window with no forecast before the decision date."""


#: The census statuses that are a documented refusal: no forecast is owed.
_REFUSALS: Final = frozenset({MeritsCoverageStatus.out_of_scope, MeritsCoverageStatus.terminated})


class CheckedDocket(BaseModel):
    """One docket the check read, with what the Court's list and the corpus say."""

    model_config = ConfigDict(extra="forbid")

    docket_number: str
    list_term: int | None = Field(
        description="October Term of the Granted & Noted list naming the docket; "
        "None for a corpus grant on no list read"
    )
    lead: str | None = Field(
        default=None,
        description="The first docket of its consolidated entry, where this is another member",
    )
    code: str | None = Field(default=None, description="The list's three-letter case code")
    granted: date | None = Field(
        default=None, description="Grant date: the list's, or the corpus's where no list has it"
    )
    argument: date | None = Field(
        default=None, description="The list's latest argument date for the entry"
    )
    decided: date | None = Field(
        default=None, description="Decision date: the corpus's, or the list's where it has none"
    )
    case_id: str | None = None
    status: MeritsCoverageStatus | None = Field(
        default=None, description="The census status; None without a merits grant on the row"
    )
    detail: str | None = None
    terminated: str | None = Field(
        default=None,
        description="How the proceeding ended with no disposition (`merits_terminated`); "
        "set whatever the status, since a forecast made before a dismissal still reads `forecast`",
    )
    merits_events: int = Field(default=0, ge=0, description="Merits events the corpus holds")
    first_forecast: date | None = Field(
        default=None, description="UTC day of the earliest committed merits prediction"
    )
    argued_forecast: bool = Field(
        default=False, description="A committed prediction at the argued moment"
    )
    alarms: list[MeritsAlarm] = Field(default_factory=list)
    standing_miss: bool = Field(
        default=False,
        description="Decided past the alarm window with a finding that can no longer be "
        "repaired: no forecast before the decision, or no row, grant or event",
    )


class ListReading(BaseModel):
    """One Term's Granted & Noted list as the check read it."""

    model_config = ConfigDict(extra="forbid")

    term: int
    read: bool = Field(description="False where the list was not published or not readable")
    entries: int = Field(default=0, ge=0)
    dockets: int = Field(default=0, ge=0, description="Term-form dockets the check reconciles")
    with_merits_event: int = Field(default=0, ge=0)
    without_merits_event: int = Field(default=0, ge=0)
    original: list[str] = Field(
        default_factory=list, description="Original-jurisdiction cases, outside prediction scope"
    )
    applications: list[str] = Field(
        default_factory=list,
        description="Applications set for argument, outside the merits stream",
    )
    problems: list[str] = Field(
        default_factory=list, description="Dockets whose entry printed no readable grant date"
    )


class MeritsCoverageCheck(BaseModel):
    """The scheduled merits coverage check's whole result."""

    model_config = ConfigDict(extra="forbid")

    as_of: date
    term: int = Field(description="The October Term the check ran for")
    census: MeritsCoverage
    lists: list[ListReading]
    dockets: list[CheckedDocket] = Field(
        description="Every listed docket, then every census grant without a prediction "
        "that no list read names"
    )
    alarms: int = Field(ge=0, description="Dockets carrying at least one alarm")
    ok: bool = Field(description="No alarm, and the Term's own list was read")


def _forecasts(data_root: Path, case_id: str, event_ids: Iterable[str]) -> dict[str, date | None]:
    """Each merits event id with a committed prediction, and its earliest run's UTC day.

    A run directory whose name is not a run-id stamp still counts as a
    prediction, with no day.
    """
    court, docket = case_id.split("/", 1)
    found: dict[str, date | None] = {}
    for event_id in sorted(set(event_ids)):
        root = CasePaths(data_root, court, int(docket)).event(event_id).predictions_dir
        days: list[date] = []
        seen = False
        for path in root.glob("*/*/prediction.json"):
            seen = True
            try:
                days.append(ids.parse_run_id(path.parent.name).date())
            except ValueError:
                continue
        if seen:
            found[event_id] = min(days, default=None)
    return found


def _first(days: Iterable[date | None]) -> date | None:
    return min((d for d in days if d is not None), default=None)


class _Facts(BaseModel):
    """What the ledger holds for one consolidated entry, pooled over its dockets."""

    model_config = ConfigDict(extra="forbid")

    any_forecast: bool = False
    first_forecast: date | None = None
    argued_forecast: bool = False


def _read_docket(
    conn: corpus.ReadConnection, data_root: Path, docket: CheckedDocket, *, today: date
) -> corpus.CorpusRow | None:
    """Fill ``docket`` from its corpus row and the ledger; the row, or None if absent."""
    if docket.case_id is None:
        return None
    row = corpus.get_row(conn, docket.case_id)
    if row is None:
        docket.case_id = None
        return None
    if docket.granted is None:
        docket.granted = row.date_cert_granted
    if row.merits_decided is not None:
        docket.decided = row.merits_decided
    if row.merits_terminated is not None:
        docket.terminated = str(row.merits_terminated)
    events = [
        e
        for e in corpus.events_for_case(conn, row.case_id)
        if e.stage == Stage.merits or e.event_id in _MERITS_EVENT_IDS
    ]
    docket.merits_events = len(events)
    forecasts = _forecasts(data_root, row.case_id, _MERITS_EVENT_IDS | {e.event_id for e in events})
    docket.first_forecast = _first(forecasts.values())
    docket.argued_forecast = any(eid in _ARGUED_EVENT_IDS for eid in forecasts)
    if corpus.opens_merits_proceeding(row):
        docket.status, docket.detail = classify_grant(conn, data_root, row, today=today)
    return row


def _alarm_entry(members: Sequence[CheckedDocket], *, today: date) -> None:
    """Set the alarms on one consolidated entry's dockets (a single docket is an entry)."""
    facts = _Facts(
        any_forecast=any(m.status == MeritsCoverageStatus.forecast for m in members),
        first_forecast=_first(m.first_forecast for m in members),
        argued_forecast=any(m.argued_forecast for m in members),
    )
    for docket in members:
        alarms: list[MeritsAlarm] = []
        granted = docket.granted
        overdue = granted is None or today - granted >= timedelta(days=EVENT_GRACE_DAYS)
        refused = docket.status in _REFUSALS or docket.terminated is not None
        if docket.list_term is not None and overdue:
            if docket.case_id is None:
                alarms.append(MeritsAlarm.no_corpus_row)
            elif docket.status is None:
                alarms.append(MeritsAlarm.no_merits_grant)
            elif docket.merits_events == 0 and not refused:
                alarms.append(MeritsAlarm.no_merits_event)
        if docket.status in GAP_STATUSES:
            alarms.append(MeritsAlarm.coverage_hole)
        if docket.status is not None and not refused:
            alarms.extend(_moment_alarms(docket, facts, today=today))
        # Once the case is decided nothing above can be repaired, so past the
        # window every finding on it is one standing miss rather than an alarm.
        if docket.decided is not None and not _in_miss_window(docket, today):
            docket.standing_miss = bool(alarms) or (not refused and _missed(docket, facts))
            alarms = []
        docket.alarms = alarms


def _missed(docket: CheckedDocket, facts: _Facts) -> bool:
    """Whether the entry was decided with no forecast before the decision date.

    A forecast dated on the decision day does not count: the run id carries no
    order against the opinion's release, so the strict reading is the safe one.
    """
    if docket.decided is None:
        return False
    return facts.first_forecast is None or facts.first_forecast >= docket.decided


def _in_miss_window(docket: CheckedDocket, today: date) -> bool:
    return docket.decided is not None and today - docket.decided <= timedelta(days=MISS_ALARM_DAYS)


def _moment_alarms(docket: CheckedDocket, facts: _Facts, *, today: date) -> list[MeritsAlarm]:
    if docket.decided is not None:
        if _missed(docket, facts) and _in_miss_window(docket, today):
            return [MeritsAlarm.decided_unforecast]
        return []
    argument = docket.argument
    if argument is None:
        return []
    found: list[MeritsAlarm] = []
    if not facts.any_forecast and argument - today <= timedelta(days=ARGUMENT_WINDOW_DAYS):
        found.append(MeritsAlarm.argument_unforecast)
    if not facts.argued_forecast and today - argument >= timedelta(days=ARGUED_GRACE_DAYS):
        found.append(MeritsAlarm.argued_unforecast)
    return found


def _listed(term: int, text: str) -> tuple[ListReading, list[list[CheckedDocket]]]:
    """One list's reading and its entries' dockets, unread against the corpus."""
    reading = ListReading(term=term, read=True, original=granted_noted.original_dockets(text))
    groups: list[list[CheckedDocket]] = []
    seen: set[str] = set()
    for entry in granted_noted.parse_granted_noted(text):
        reading.entries += 1
        codes = dict(entry.codes)
        members: list[CheckedDocket] = []
        for number in entry.dockets:
            if number in seen:
                continue
            seen.add(number)
            if corpus.scotus_term_year(number) is None:
                reading.applications.append(number)
                continue
            if entry.granted is None:
                reading.problems.append(number)
            members.append(
                CheckedDocket(
                    docket_number=number,
                    list_term=term,
                    code=codes.get(number),
                    granted=entry.granted,
                    argument=entry.argument,
                    decided=entry.decided,
                )
            )
        for member in members[1:]:
            member.lead = members[0].docket_number
        if members:
            groups.append(members)
    return reading, groups


def merits_coverage_check(
    conn: corpus.ReadConnection,
    data_root: Path,
    *,
    term: int,
    lists: Mapping[int, str | None],
    today: date,
) -> MeritsCoverageCheck:
    """Run the check for October Term ``term`` against the lists' extracted text.

    ``lists`` maps a four-digit October Term to its Granted & Noted list's
    text, or to ``None`` where the list could not be read. The census covers
    grants made in ``term - 1`` and ``term``: a Term's argument docket is filled
    from the grants of the second half of the Term before it. The check is not
    ``ok`` unless ``term``'s own list was read; any other list is read where it
    exists, since the Court opens the next Term's list while this one runs.
    """
    census = merits_coverage(conn, data_root, first_term=term - 1, last_term=term, today=today)
    readings: list[ListReading] = []
    groups: list[list[CheckedDocket]] = []
    for list_term in sorted(lists):
        text = lists[list_term]
        if text is None:
            readings.append(ListReading(term=list_term, read=False))
            continue
        reading, listed = _listed(list_term, text)
        readings.append(reading)
        groups.extend(listed)
    numbers = [d.docket_number for group in groups for d in group]
    case_ids = corpus.scotus_case_ids_by_docket_numbers(conn, numbers)
    on_a_list: set[str] = set()
    by_term = {r.term: r for r in readings}
    for group in groups:
        for docket in group:
            norm = corpus.normalize_docket_number(docket.docket_number)
            docket.case_id = case_ids.get(norm) if norm is not None else None
            _read_docket(conn, data_root, docket, today=today)
            if docket.case_id is not None:
                on_a_list.add(docket.case_id)
            if docket.list_term is not None:
                listing = by_term[docket.list_term]
                listing.dockets += 1
                if docket.merits_events:
                    listing.with_merits_event += 1
                else:
                    listing.without_merits_event += 1
        _alarm_entry(group, today=today)
    for entry in census.uncovered:
        if entry.case_id in on_a_list:
            continue
        docket = CheckedDocket(
            docket_number=entry.docket_number, list_term=None, case_id=entry.case_id
        )
        _read_docket(conn, data_root, docket, today=today)
        _alarm_entry([docket], today=today)
        groups.append([docket])
    dockets = [d for group in groups for d in group]
    alarms = sum(bool(d.alarms) for d in dockets)
    own = by_term.get(term)
    return MeritsCoverageCheck(
        as_of=today,
        term=term,
        census=census,
        lists=readings,
        dockets=dockets,
        alarms=alarms,
        ok=alarms == 0 and own is not None and own.read,
    )


_ALARM_TEXT: Final[Mapping[MeritsAlarm, str]] = {
    MeritsAlarm.no_corpus_row: "no corpus row",
    MeritsAlarm.no_merits_grant: "the corpus row holds no grant opening a merits proceeding",
    MeritsAlarm.no_merits_event: "no merits event",
    MeritsAlarm.coverage_hole: "census hole",
    MeritsAlarm.argument_unforecast: f"argument within {ARGUMENT_WINDOW_DAYS} days or past, "
    + "no forecast",
    MeritsAlarm.argued_unforecast: f"argued {ARGUED_GRACE_DAYS} or more days ago, "
    + "no forecast at the argued moment",
    MeritsAlarm.decided_unforecast: "decided with no forecast before the decision",
}


def _day(value: date | None) -> str:
    return value.isoformat() if value is not None else "-"


def _status_cells(term: MeritsCoverageTerm) -> str:
    cells = [term.statuses.get(status.value, 0) for status in MeritsCoverageStatus]
    return " | ".join(str(cell) for cell in cells)


def summary_lines(check: MeritsCoverageCheck) -> list[str]:
    """The check in a few log lines: each list's counts, the census, the verdict."""
    lines: list[str] = []
    for reading in check.lists:
        if not reading.read:
            lines.append(f"OT{reading.term} Granted & Noted list: not published or not readable")
            continue
        lines.append(
            f"OT{reading.term} Granted & Noted list: {reading.entries} entries, "
            f"{reading.dockets} dockets; {reading.with_merits_event} with a merits event, "
            f"{reading.without_merits_event} without; {len(reading.original)} original, "
            f"{len(reading.applications)} application(s) set for argument"
        )
    for term in check.census.terms:
        statuses = ", ".join(f"{k} {v}" for k, v in term.statuses.items()) or "-"
        lines.append(
            f"OT{term.term} grants: plenary {term.plenary_grants}, "
            f"order-riding {term.order_riding}; {statuses}"
        )
    standing = sum(d.standing_miss for d in check.dockets)
    lines.append(
        f"alarms on {check.alarms} docket(s); {standing} standing miss(es); "
        f"{'ok' if check.ok else 'FAILING'}"
    )
    return lines


def digest_line(check: MeritsCoverageCheck) -> str:
    """The one-line count a digest carries for the Term."""
    forecast = sum(d.status == MeritsCoverageStatus.forecast for d in check.dockets if d.list_term)
    listed = sum(1 for d in check.dockets if d.list_term)
    return (
        f"Merits coverage, OT{check.term}: {forecast} of {listed} listed dockets forecast, "
        f"{check.alarms} with an alarm (as of {check.as_of.isoformat()})"
    )


def render_report(check: MeritsCoverageCheck, *, vintage: str | None = None) -> str:
    """The check as Markdown: the alarms first, then everything reported beside them.

    ``vintage`` is the corpus vintage line to quote beside the figures.
    """
    out: list[str] = [f"## Merits coverage, OT{check.term}, as of {check.as_of.isoformat()}", ""]
    out.append(digest_line(check) + ".")
    if vintage:
        out.append(f"Corpus vintage: {vintage}.")
    out.append("")
    alarmed = [d for d in check.dockets if d.alarms]
    unread = [r for r in check.lists if not r.read and r.term == check.term]
    if alarmed or unread:
        out.append("### Alarms")
        out.append("")
        out.extend(
            f"- The OT{r.term} Granted & Noted list could not be read, so nothing was "
            + "reconciled against it."
            for r in unread
        )
        for d in alarmed:
            reasons = "; ".join(_ALARM_TEXT[a] for a in d.alarms)
            status = f", census status `{d.status.value}`" if d.status is not None else ""
            case = f" (`{d.case_id}`)" if d.case_id else ""
            out.append(
                f"- **{d.docket_number}**{case}: {reasons}{status}. Granted {_day(d.granted)}, "
                f"argument {_day(d.argument)}, decided {_day(d.decided)}."
            )
        out.append("")
    else:
        out.extend(["No alarm.", ""])
    out.extend(_render_lists(check))
    out.extend(_render_census(check))
    out.extend(_render_reported(check))
    return "\n".join(out).rstrip() + "\n"


def _render_lists(check: MeritsCoverageCheck) -> list[str]:
    out = ["### The Court's Granted & Noted lists", ""]
    out.append("| List | Entries | Dockets | With a merits event | Without |")
    out.append("|---|---|---|---|---|")
    for r in check.lists:
        if r.read:
            out.append(
                f"| OT{r.term} | {r.entries} | {r.dockets} | {r.with_merits_event} "
                f"| {r.without_merits_event} |"
            )
        else:
            out.append(f"| OT{r.term} | not published or not readable | | | |")
    out.append("")
    return out


def _render_census(check: MeritsCoverageCheck) -> list[str]:
    names = " | ".join(f"`{status.value}`" for status in MeritsCoverageStatus)
    out = ["### Census by grant Term", ""]
    out.append(f"| Grant Term | Plenary grants | Order-riding | {names} |")
    out.append("|---|---|---|" + "---|" * len(MeritsCoverageStatus))
    out.extend(
        f"| OT{t.term} | {t.plenary_grants} | {t.order_riding} | {_status_cells(t)} |"
        for t in check.census.terms
    )
    out.append("")
    return out


def _refusal(docket: CheckedDocket) -> str:
    status = docket.status.value if docket.status is not None else "-"
    return f"`{status}`" + (f" ({docket.detail})" if docket.detail else "")


def _render_reported(check: MeritsCoverageCheck) -> list[str]:
    out: list[str] = []
    members = [d for d in check.dockets if d.lead is not None]
    if members:
        out.extend(["### Consolidated members", ""])
        out.extend(
            f"- {d.docket_number} with lead {d.lead}: "
            + (f"`{d.status.value}`" if d.status is not None else "no merits grant on the row")
            for d in members
        )
        out.append("")
    refused = [
        d
        for d in check.dockets
        if d.list_term is not None and (d.status in _REFUSALS or d.terminated is not None)
    ]
    if refused:
        out.extend(["### Listed, no further forecast owed", ""])
        out.extend(
            f"- {d.docket_number}: "
            + (f"terminated ({d.terminated})" if d.terminated is not None else _refusal(d))
            for d in refused
        )
        out.append("")
    standing = [d for d in check.dockets if d.standing_miss]
    if standing:
        out.extend(["### Standing misses", ""])
        out.append(
            f"Decided more than {MISS_ALARM_DAYS} days ago with no forecast before the "
            + "decision, or with no row, merits grant or merits event:"
        )
        out.append("")
        out.append(", ".join(f"{d.docket_number} ({_day(d.decided)})" for d in standing) + ".")
        out.append("")
    for r in check.lists:
        apart = [*r.original, *r.applications]
        if apart:
            out.extend([f"### Outside the merits stream, OT{r.term} list", ""])
            out.append(
                "Original-jurisdiction cases and applications set for argument, not alarmed: "
                + ", ".join(apart)
                + "."
            )
            out.append("")
        if r.problems:
            out.append(
                f"The OT{r.term} list printed no readable grant date for: "
                + ", ".join(r.problems)
                + "."
            )
            out.append("")
    return out


def _alarm_issue(repo: str, runner: GhRunner) -> int | None:
    """The open alarm issue's number: this check's title, opened by the workflow token."""
    listing = json.loads(
        runner(["gh", "api", f"repos/{repo}/issues?labels={ISSUE_LABEL}&state=open&per_page=100"])
        or "[]"
    )
    for issue in listing if isinstance(listing, list) else []:
        if not isinstance(issue, dict) or "pull_request" in issue:
            continue
        user = issue.get("user")
        login = user.get("login") if isinstance(user, dict) else None
        number = issue.get("number")
        if issue.get("title") == ISSUE_TITLE and login == ALARM_AUTHOR and isinstance(number, int):
            return number
    return None


def latch(
    repo: str, check: MeritsCoverageCheck, report_path: Path, *, runner: GhRunner = _gh
) -> str:
    """Open, refresh or close the one alarm issue to match ``check``; what was done.

    A failing check opens the issue, or rewrites the open one's body in place
    with the latest report, so a recurring failure stays on one thread. A
    passing check closes it with a comment. A passing check with no open issue
    writes nothing. Refuses a check that never read its own Term's list:
    nothing was reconciled, so it can neither raise nor clear the alarm.
    """
    own = next((r for r in check.lists if r.term == check.term), None)
    if own is None or not own.read:
        raise ValueError(f"the check never read the OT{check.term} Granted & Noted list")
    runner(
        [
            "gh",
            "label",
            "create",
            ISSUE_LABEL,
            "--repo",
            repo,
            "--force",
            "--color",
            ISSUE_LABEL_COLOR,
            "--description",
            ISSUE_LABEL_DESCRIPTION,
        ]
    )
    number = _alarm_issue(repo, runner)
    if check.alarms:
        if number is None:
            url = runner(
                [
                    "gh",
                    "issue",
                    "create",
                    "--repo",
                    repo,
                    "--title",
                    ISSUE_TITLE,
                    "--label",
                    ISSUE_LABEL,
                    "--body-file",
                    str(report_path),
                ]
            )
            return f"opened {url.strip()}"
        runner(
            ["gh", "issue", "edit", str(number), "--repo", repo, "--body-file", str(report_path)]
        )
        return f"refreshed #{number}"
    if number is None:
        return "no alarm, and no open issue"
    runner(
        [
            "gh",
            "issue",
            "comment",
            str(number),
            "--repo",
            repo,
            "--body",
            f"Merits coverage has no alarm as of {check.as_of.isoformat()}: closing.",
        ]
    )
    runner(["gh", "issue", "close", str(number), "--repo", repo, "--reason", "completed"])
    return f"closed #{number}"
