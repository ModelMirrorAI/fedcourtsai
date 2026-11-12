"""When the trial stage's motion events come into being, read from a district docket.

The trial stage (``docs/trial-stage.md``) forecasts the ruling on a motion once
its briefing is complete. This module reads a docket for the motions the stage
covers and for the day each would open, with no agent. Its counterpart,
:mod:`fedcourtsai.pipeline.trial_resolver`, reads how each one resolved.

Like the resolver, the rule is built to miss rather than misread. A motion it
cannot name, or briefing it cannot date, is reported with its reason and opens
nothing; it never opens an event on a guess.

- **The motion is its own entry's leading phrase.** A numbered entry that leads
  with a motion to dismiss, for class certification, for summary judgment or
  for a preliminary injunction is one event, named by that entry's number
  (:func:`~fedcourtsai.pipeline.trial_resolver.motion_moment`). An entry that
  leads with one of those motions and is not an event (a motion to dismiss that
  asks for other relief, a restraining order alone, an unnumbered entry) is
  reported as declined.
- **Briefing is a party's filing that leads with what it is and cites the
  motion.** An opposition leads with an opposition or an answering brief; a
  reply leads with a reply. Nothing but the reference may stand between that
  name and the motion's entry number, so briefing on a request, an objection
  or another motion about the motion is not the motion's briefing. A
  declaration, a notice, a joinder, a statement of non-opposition and a
  sur-reply are not briefing either.
- **A deadline is one the docket states.** Where the motion's own entry, or a
  later entry that sets or resets its deadlines, says when responses or
  replies are due, the latest such statement is the deadline. Where the docket
  states none, a caller may supply the district's local-rule periods. Either
  is trusted only while no entry after it speaks of an extension, a
  stipulation, a continuance or a schedule for a brief, whichever motion that
  entry cites: a clerk's default date outlives the schedule that replaced it.
- **A briefed motion opens** on the first reply filed on or after an
  opposition, or, with an opposition on the docket, on the day after a reply
  deadline that falls on or after the opposition, once that day has come. A
  motion nothing on the docket opposes stays unopened: the opposition may be
  a cross-motion this rule does not read as one.
- **A motion re-filed as a correction is one event**, the later entry's.
- **A preliminary-injunction motion opens** on the first opposition, or on
  the day after the response deadline once that day has come.
- **A motion the court ruled on first opens nothing.** The resolver's reading
  of the same docket says whether a ruling, a withdrawal or a closure came on
  or before the day the motion would have opened.

The input is the docket-entry shape ``watchlist-refresh`` stores. This module
reads only what it is given and fetches nothing.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

from .. import ids
from ..ai_watchlist import AiWatchlist, Relation
from . import trial_resolver as resolver
from .ai_candidates import DISTRICT_COURT
from .trial_resolver import Citation, MotionEvent, MotionResolution, TrialMoment, Unresolved

#: The label of the reading rule below. A changed rule is a new label.
OPENER_RULE: Final = "trial-opener-v1"


class Basis(StrEnum):
    """What an opening date was read from."""

    reply = "reply"
    opposition = "opposition"
    #: The day after a deadline the docket states.
    docket_deadline = "docket-deadline"
    #: The day after a deadline counted from the district's local rule.
    local_rule = "local-rule"


@dataclass(frozen=True)
class LocalRule:
    """A district's default briefing periods, in calendar days.

    ``opposition_days`` runs from the motion's filing; ``reply_days`` from the
    opposition's filing, and is ``None`` where the district allows no reply as
    of right.
    """

    opposition_days: int
    reply_days: int | None


@dataclass(frozen=True)
class Opening:
    """One motion the docket holds, and where its briefing stands.

    ``opens_on`` is the day the event opens, or ``None`` while it has not;
    ``waiting_on`` then says what it waits for. ``resolution`` is the
    resolver's reading of the same docket, and ``ruled_first`` is set when that
    reading is dated on or before the opening (or there is no opening): such a
    motion opens no event.
    """

    event: MotionEvent
    filed: Citation
    opposition: Citation | None
    reply: Citation | None
    opens_on: date | None
    basis: Basis | None
    waiting_on: str | None
    resolution: MotionResolution | Unresolved | None
    ruled_first: bool
    rule: str = OPENER_RULE

    @property
    def is_event(self) -> bool:
        """Whether this motion opens a forecast event."""
        return self.opens_on is not None and not self.ruled_first


@dataclass(frozen=True)
class Declined:
    """An entry that leads with a covered motion and is not an event."""

    cited: Citation
    reason: str
    rule: str = OPENER_RULE


# --- declined motions --------------------------------------------------------

# An entry that leads with a motion of a covered family, whether or not the
# resolver's kind rule takes it: the ones it does not take are reported.
_FAMILY = re.compile(
    resolver._MOTION_LEAD + r"(?:to\s+dismiss\b|for\s+(?:partial\s+)?summary\s+judgment\b|"
    r"to\s+certify\s+(?:a\s+|the\s+)?class\b|for\s+class\s+certification\b|"
    r"for\s+(?:an?\s+)?(?:preliminary\s+injunction|temporary\s+restraining\s+order)\b)",
    re.I,
)
_TRO_ONLY = re.compile(r"\btemporary\s+restraining\s+order\b", re.I)


def _declined_reason(text: str, number: int | None) -> str:
    if resolver.motion_moment(text) is None:
        if _TRO_ONLY.search(text[:160]):
            return "a temporary restraining order alone is not an event"
        return "the motion asks for other relief, or is not one the stage covers"
    if number is None:
        return "the motion's entry carries no number to name the event by"
    return "another entry already names an event by this number"


# --- briefing ----------------------------------------------------------------

# A clerk's bracketed or starred tag before the filing's name ("[SEALED]").
# Each piece is atomic and the run possessive, so a row of asterisks fails in
# linear time.
_TAG = r"(?>\[[^\]]{0,40}\]\s*|\*++[^*]{1,40}+\*++\s*)*+"
_QUALITY = r"(?:(?:amended|corrected|redacted|sealed|joint|consolidated|omnibus)\s+)*"
# What may stand between a brief's name and the motion it cites: nothing but
# the reference itself. A second motion, request or objection named before the
# number makes the filing briefing on that, not on the cited motion.
_CITES_MOTION = r"\s*\(?\s*re:?\s+\[?(\d+)\]?\s+(?:[\w.'\u2019]+\s+){0,3}?motion\b"
_OPPOSITION = re.compile(
    r"^\s*" + _TAG + _QUALITY + r"(?:opposition(?:/response)?|"
    r"(?:answering\s+brief|brief|memorandum(?:\s+of\s+law)?|response)\s+in\s+opposition)"
    + _CITES_MOTION,
    re.I,
)
_REPLY = re.compile(
    r"^\s*" + _TAG + _QUALITY + r"reply(?:\s+(?:brief|memorandum(?:\s+of\s+law)?))?"
    r"(?:\s+in\s+support)?(?:\s+to\s+response\s+to(?:\s+motion)?)?" + _CITES_MOTION,
    re.I,
)


def _briefing(text: str) -> tuple[str, int] | None:
    """``("opposition" | "reply", cited motion)`` for a party's brief, else ``None``."""
    for kind, pattern in (("reply", _REPLY), ("opposition", _OPPOSITION)):
        match = pattern.match(text)
        if match is not None:
            return kind, int(match.group(1))
    return None


# --- deadlines ---------------------------------------------------------------

_DATE = r"(\d{1,2}/\d{1,2}/\d{2,4})"
_RESPONSES_DUE = re.compile(r"\bresponses?\s+due\s+by\s+" + _DATE, re.I)
_REPLIES_DUE = re.compile(r"\brepl(?:y|ies)\s+due\s+by\s+" + _DATE, re.I)
# An entry that sets a motion's deadlines names the motion right after its head.
_SETS = re.compile(r"^\s*(?:set/?)?(?:re)?set\s+deadlines?\s+as\s+to\s+\[?(\d+)\]?", re.I)
# A later entry that may have moved some briefing on the docket: it speaks of
# time or a schedule, and of a brief. It need not cite the motion, since an
# order on an extension motion cites that motion instead.
_MOVES = re.compile(
    r"\bexten(?:sion|d\w*)\b|\bbriefing\s+schedule\b|\bstipulat\w*|\bcontinu\w*|\breset\w*|"
    r"\benlarg\w*|\bdeadlines?\b|\bstay\w*",
    re.I,
)
_OF_BRIEFING = re.compile(r"\brepl(?:y|ies)\b|\brespon[ds]\w*|\bopposition\b|\bbrief\w*", re.I)


def _parse_day(text: str) -> date | None:
    for form in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(text, form).date()
        except ValueError:
            continue
    return None


def _stated(pattern: re.Pattern[str], text: str) -> date | None:
    match = pattern.search(text)
    return _parse_day(match.group(1)) if match is not None else None


@dataclass
class _Deadline:
    """One deadline the docket states, and whether the schedule has moved since."""

    day: date | None = None
    moved: bool = False

    def state(self, day: date | None) -> None:
        if day is not None:
            self.day, self.moved = day, False

    def trusted(self) -> date | None:
        return None if self.moved else self.day


# --- one motion --------------------------------------------------------------


def _resolved_on(resolution: MotionResolution | Unresolved | None) -> date | None:
    if isinstance(resolution, MotionResolution):
        return resolution.cited.date_filed
    if isinstance(resolution, Unresolved) and resolution.candidates:
        return resolution.candidates[0].date_filed
    return None


def _open_one(  # noqa: PLR0912, PLR0915 - one branch per way briefing completes
    own: Mapping[str, Any],
    event: MotionEvent,
    entries: Sequence[Mapping[str, Any]],
    *,
    today: date,
    local_rule: LocalRule | None,
) -> Opening:
    number = event.entry_number
    later = resolver._after(entries, number)
    filed = resolver.cite(own)
    own_text = str(own.get("description") or "")
    responses = _Deadline(_stated(_RESPONSES_DUE, own_text))
    replies = _Deadline(_stated(_REPLIES_DUE, own_text))
    local_moved = False
    opposition: Citation | None = None
    reply: Citation | None = None
    for entry in later:
        text = resolver._entry_text(entry)
        brief = _briefing(text)
        if brief is not None:
            kind, cited_number = brief
            cited = resolver.cite(entry)
            if cited_number != number or cited.date_filed is None:
                continue
            if kind == "opposition" and opposition is None:
                opposition = cited
            elif kind == "reply" and reply is None and opposition is not None:
                reply = cited
            continue
        sets = _SETS.match(text)
        if sets is not None and int(sets.group(1)) == number:
            # A fresh statement of a deadline is the schedule for that deadline.
            full = str(entry.get("description") or "")
            responses.state(_stated(_RESPONSES_DUE, full))
            replies.state(_stated(_REPLIES_DUE, full))
            continue
        if _MOVES.search(text) and _OF_BRIEFING.search(text):
            # Some briefing on the docket moved, and the rule cannot say whose.
            responses.moved = replies.moved = local_moved = True
    injunction = event.moment is TrialMoment.preliminary_injunction

    opens_on: date | None = None
    basis: Basis | None = None
    waiting_on: str | None = None

    def after(deadline: date | None, how: Basis, *, not_before: date | None = None) -> bool:
        nonlocal opens_on, basis
        if deadline is None or today <= deadline:
            return False
        if not_before is not None and deadline < not_before:
            return False
        opens_on, basis = deadline + timedelta(days=1), how
        return True

    def local(start: date | None, days: int | None) -> date | None:
        if local_rule is None or local_moved or start is None or days is None:
            return None
        return start + timedelta(days=days)

    if injunction:
        if opposition is not None:
            opens_on, basis = opposition.date_filed, Basis.opposition
        elif not after(responses.trusted(), Basis.docket_deadline):
            rule_day = local(filed.date_filed, local_rule.opposition_days if local_rule else None)
            if responses.day is not None or not after(rule_day, Basis.local_rule):
                waiting_on = "the opposition, or its deadline"
    elif reply is not None:
        opens_on, basis = reply.date_filed, Basis.reply
    elif opposition is None:
        waiting_on = "an opposition the rule can read"
    elif not after(replies.trusted(), Basis.docket_deadline, not_before=opposition.date_filed):
        rule_day = local(opposition.date_filed, local_rule.reply_days if local_rule else None)
        if replies.day is not None or not after(rule_day, Basis.local_rule):
            waiting_on = "the reply, or its deadline"

    resolution = resolver.resolve_motion(event, entries)
    resolved_on = _resolved_on(resolution)
    ruled_first = resolution is not None and (
        opens_on is None or resolved_on is None or resolved_on <= opens_on
    )
    return Opening(
        event=event,
        filed=filed,
        opposition=opposition,
        reply=reply,
        opens_on=opens_on,
        basis=basis,
        waiting_on=None if ruled_first else waiting_on,
        resolution=resolution,
        ruled_first=ruled_first,
    )


# --- a docket ----------------------------------------------------------------


def read_docket(
    entries: Iterable[Mapping[str, Any]],
    *,
    today: date,
    local_rule: LocalRule | None = None,
) -> tuple[list[Opening], list[Declined]]:
    """Every covered motion on a docket, and every motion entry declined.

    ``entries`` are the docket's entries, in any order. ``today`` is the day
    the docket is read on: a deadline opens a motion only once that day has
    passed. ``local_rule`` is the district's default briefing periods, used
    only where the docket states no deadline.
    """
    ordered = [
        entry
        for entry in resolver._ordered(entries)
        if (resolver.cite(entry).date_filed or date.min) <= today
    ]
    openings: list[Opening] = []
    declined: list[Declined] = []
    named: set[int] = set()
    corrected = _corrected(ordered)
    for entry in ordered:
        text = resolver._entry_text(entry)
        if not _FAMILY.search(text):
            continue
        moment = resolver.motion_moment(text)
        number = resolver._number(entry)
        if moment is None or number is None or number in named:
            declined.append(Declined(resolver.cite(entry), _declined_reason(text, number)))
            continue
        if number in corrected:
            declined.append(
                Declined(resolver.cite(entry), f"re-filed as entry {corrected[number]}")
            )
            continue
        named.add(number)
        openings.append(
            _open_one(
                entry, MotionEvent(moment, number), ordered, today=today, local_rule=local_rule
            )
        )
    return openings, declined


_CORRECTS = re.compile(
    r"\bcorrect(?:ion|ed|s|ing)\s+(?:of\s+|to\s+|version\s+of\s+)?"
    r"(?:(?:docket|dkt\.?|doc\.?|entry|ecf|filing)\s*)?(?:nos?\.?\s*)?#?\s*\[?(\d+)\]?",
    re.I,
)


def _corrected(ordered: Sequence[Mapping[str, Any]]) -> dict[int, int]:
    """Motion entries a later motion entry says it corrects: ``{earlier: later}``."""
    found: dict[int, int] = {}
    kinds = {
        number: resolver.motion_moment(resolver._entry_text(entry))
        for entry in ordered
        if (number := resolver._number(entry)) is not None
    }
    for entry in ordered:
        text = resolver._entry_text(entry)
        number = resolver._number(entry)
        moment = resolver.motion_moment(text)
        if number is None or moment is None:
            continue
        for match in _CORRECTS.finditer(text):
            earlier = int(match.group(1))
            if earlier < number and kinds.get(earlier) is moment:
                found[earlier] = number
    return found


# --- one motion on two dockets -----------------------------------------------

_NUMBERS = re.compile(r"\d+")
_SPACE = re.compile(r"\s+")


def _same_motion_key(entry: Mapping[str, Any]) -> tuple[str, str]:
    """A motion entry's filing day and its text with every number struck."""
    text = resolver._entry_text(entry)[:200]
    return str(entry.get("date_filed") or ""), _SPACE.sub(" ", _NUMBERS.sub("#", text)).lower()


def owned_by_lead(
    lead_entries: Iterable[Mapping[str, Any]], member_entries: Iterable[Mapping[str, Any]]
) -> frozenset[int]:
    """The member docket's motion entry numbers that the lead docket also holds.

    One motion docketed on a multidistrict proceeding's lead docket and again
    on a member docket is the lead docket's event. Two entries are the same
    motion when they were filed on one day and their texts agree once every
    number is struck (the entry numbers they cite differ by docket).
    """
    lead = {
        _same_motion_key(entry)
        for entry in lead_entries
        if resolver.motion_moment(resolver._entry_text(entry)) is not None
    }
    owned: set[int] = set()
    for entry in member_entries:
        number = resolver._number(entry)
        text = resolver._entry_text(entry)
        if number is None or resolver.motion_moment(text) is None:
            continue
        if entry.get("date_filed") and _same_motion_key(entry) in lead:
            owned.add(number)
    return frozenset(owned)


# --- the watchlist's dockets -------------------------------------------------


class SurveyRow(BaseModel):
    """One motion the survey read: identifiers and dates only, no docket text."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    moment: str
    entry_number: int
    filed: date | None
    opposition_entry: int | None
    reply_entry: int | None
    opens_on: date | None
    basis: str | None
    #: ``event`` (it opens a forecast event), ``ruled-first`` (the court ruled
    #: before it would have opened), ``pending`` (briefing is not complete),
    #: or ``lead-docket`` (the lead docket holds the same motion).
    status: str
    waiting_on: str | None
    #: The resolver's ruling, ``triage``, or ``None`` while it reads none.
    resolved: str | None
    resolved_entry: int | None
    resolved_on: date | None
    triage_reason: str | None


class SurveyDeclined(BaseModel):
    """A motion entry the survey declined, and why."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    entry_number: int | None
    filed: date | None
    reason: str


class Survey(BaseModel):
    """What the opener and the resolver read on the watchlist's district dockets."""

    model_config = ConfigDict(extra="forbid")

    opener_rule: str = OPENER_RULE
    resolver_rule: str = resolver.RESOLVER_RULE
    read_on: date
    dockets_read: list[str] = Field(default_factory=list)
    #: Listed district dockets the corpus holds no stored entries for.
    dockets_missing: list[str] = Field(default_factory=list)
    motions: list[SurveyRow] = Field(default_factory=list)
    declined: list[SurveyDeclined] = Field(default_factory=list)

    def counts(self) -> dict[str, int]:
        """The survey's totals: motions by status, and events by how they resolved."""
        events = [row for row in self.motions if row.status == "event"]
        return {
            "motions": len(self.motions),
            "events": len(events),
            "ruled_first": sum(row.status == "ruled-first" for row in self.motions),
            "pending": sum(row.status == "pending" for row in self.motions),
            "lead_docket": sum(row.status == "lead-docket" for row in self.motions),
            "declined": len(self.declined),
            "events_resolved": sum(row.resolved not in (None, "triage") for row in events),
            "events_triage": sum(row.resolved == "triage" for row in events),
            "events_open": sum(row.resolved is None for row in events),
        }


#: The relations whose dockets hold motions of their own. A transferred-from
#: docket repeats the receiving docket's entries, an appeal is the appeal
#: stage's, and the panel's docket holds no merits motion.
_OWN_MOTIONS: Final = frozenset({Relation.member, Relation.companion})


def survey_dockets(watchlist: AiWatchlist) -> list[tuple[str, str | None]]:
    """The district dockets the trial stage reads: ``(case id, lead case id or None)``.

    A listed case's own docket and its member and companion dockets, district
    courts only. A member docket names its lead, so a motion both hold is the
    lead's event.
    """
    found: list[tuple[str, str | None]] = []
    for case in watchlist.cases:
        lead = ids.case_id(case.court, case.docket_id)
        if DISTRICT_COURT.fullmatch(case.court):
            found.append((lead, None))
        for related in case.related:
            if related.relation in _OWN_MOTIONS and DISTRICT_COURT.fullmatch(related.court):
                found.append(
                    (
                        ids.case_id(related.court, related.docket_id),
                        lead if related.relation is Relation.member else None,
                    )
                )
    return found


def _row(case_id: str, opening: Opening, *, lead_owned: bool) -> SurveyRow:
    resolution = opening.resolution
    resolved: str | None = None
    reason: str | None = None
    cited: Citation | None = None
    if isinstance(resolution, MotionResolution):
        resolved, cited = resolution.ruling.value, resolution.cited
    elif isinstance(resolution, Unresolved):
        resolved, reason = "triage", resolution.reason
        cited = resolution.candidates[0] if resolution.candidates else None
    if lead_owned:
        status = "lead-docket"
    elif opening.ruled_first:
        status = "ruled-first"
    elif opening.opens_on is not None:
        status = "event"
    else:
        status = "pending"
    return SurveyRow(
        case_id=case_id,
        moment=opening.event.moment.value,
        entry_number=opening.event.entry_number,
        filed=opening.filed.date_filed,
        opposition_entry=opening.opposition.entry_number if opening.opposition else None,
        reply_entry=opening.reply.entry_number if opening.reply else None,
        opens_on=opening.opens_on,
        basis=opening.basis.value if opening.basis else None,
        status=status,
        waiting_on=opening.waiting_on,
        resolved=resolved,
        resolved_entry=cited.entry_number if cited else None,
        resolved_on=cited.date_filed if cited else None,
        triage_reason=reason,
    )


def survey(
    watchlist: AiWatchlist,
    entries_of: Callable[[str], Sequence[Mapping[str, Any]] | None],
    *,
    today: date,
) -> Survey:
    """Read every district docket the watchlist lists for its motions.

    ``entries_of`` returns a docket's stored entries by case id, or ``None``
    where none are stored. The result carries identifiers and dates only.
    """
    result = Survey(read_on=today)
    stored: dict[str, Sequence[Mapping[str, Any]] | None] = {}
    seen: set[str] = set()
    for case_id, lead in survey_dockets(watchlist):
        if case_id in seen:
            continue
        seen.add(case_id)
        if case_id not in stored:
            stored[case_id] = entries_of(case_id)
        entries = stored[case_id]
        if not entries:
            result.dockets_missing.append(case_id)
            continue
        result.dockets_read.append(case_id)
        owned: frozenset[int] = frozenset()
        if lead is not None:
            if lead not in stored:
                stored[lead] = entries_of(lead)
            owned = owned_by_lead(stored[lead] or (), entries)
        openings, declined = read_docket(entries, today=today)
        result.motions.extend(
            _row(case_id, opening, lead_owned=opening.event.entry_number in owned)
            for opening in openings
        )
        result.declined.extend(
            SurveyDeclined(
                case_id=case_id,
                entry_number=item.cited.entry_number,
                filed=item.cited.date_filed,
                reason=item.reason,
            )
            for item in declined
        )
    return result


def summary_lines(result: Survey) -> list[str]:
    """The survey's one-screen reading, for stderr."""
    counts = result.counts()
    decided = counts["events_resolved"] + counts["events_triage"]
    return [
        f"trial-events ({result.opener_rule}, {result.resolver_rule}), read {result.read_on}: "
        f"{len(result.dockets_read)} docket(s) read, {len(result.dockets_missing)} not stored",
        f"  {counts['motions']} motion(s): {counts['events']} open an event, "
        f"{counts['ruled_first']} ruled before opening, {counts['pending']} not fully briefed, "
        f"{counts['lead_docket']} the lead docket's, {counts['declined']} declined",
        f"  of the {counts['events']} event(s): {counts['events_resolved']} resolved, "
        f"{counts['events_triage']} to triage, {counts['events_open']} read as open"
        + (f"; triage {counts['events_triage']} of {decided} read" if decided else ""),
    ]
