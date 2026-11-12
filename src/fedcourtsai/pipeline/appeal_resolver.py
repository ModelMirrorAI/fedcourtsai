"""The appeal stage's opener and resolver for `appeal-disposition`.

The appeal stage (`docs/appeal-stage.md`) forecasts a court of appeals'
disposition of a listed appeal. This module reads one appellate docket and
says two things about it: when its briefing closed, which is when the event
opens, and how the panel disposed of the appeal. It is deterministic, runs no
agent and is court-agnostic: it reads the forms the courts of appeals' dockets
share and declines the rest.

It is built to miss rather than misread, on the trial resolver's terms
(`pipeline/trial_resolver.py`). A disposition is read only from an entry that
is the court's judgment or opinion by its leading words, and only from the
decretal forms below; a judgment entry the rule cannot read is an
:class:`Unresolved` for the maintainer's triage, never a guess. An entry that
decides a petition for review, whose outcomes the stage does not name, is
triage as well.

**What it reads as a disposition**

- a judgment entry that leads with its result (`JUDGMENT, Affirmed.`) and
  speaks of no other;
- an opinion, memorandum or summary-order entry whose text states the result
  in the court's capitals (`we VACATE … and REMAND`, `AFFIRMED.`);
- a judgment "that the judgment of the District Court be affirmed", and an
  opinion or order "affirming the judgment of the district court";
- an order whose own words dismiss the whole appeal, split by who ended it:
  the parties (a voluntary or stipulated dismissal, a settlement, Rule 42(b))
  or the court (for want of jurisdiction, as moot, as untimely). A dismissal
  that states neither, both, or another reason is triage, and so is one that
  reaches less than the whole appeal.

An entry whose result words sit beside a dissent, a cross-appeal, a stay, a
certified question or a fee ruling is triage: the rule cannot say the words
are the panel's disposition of the whole appeal. A document received from
another court, a party's filing and an entry the clerk has voided are not
read at all.

**When the event opens.** On the appellant's reply brief as filed. A deadline
that passes with no reply opens nothing under this rule: the forms in which
the courts state a reply deadline differ too much to read safely, so such an
appeal waits. A docket that speaks of a cross-appeal opens nothing either,
because the last brief there is not the appellant's reply.

Nothing registers, schedules or writes an event from this module;
`fedcourts appeal-events` reads it as a dry run.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from .. import ids
from ..ai_watchlist import AiWatchlist, Relation
from . import trial_resolver as resolver
from .trial_resolver import Citation

APPEAL_RULE = "appeal-resolver-v1"

MOMENT = "appeal-disposition"


class AppealOutcome(StrEnum):
    affirmed = "affirmed"
    reversed = "reversed"
    vacated = "vacated"
    mixed = "mixed"
    #: The court's own dismissal, for want of jurisdiction or as moot.
    dismissed = "dismissed"
    #: The parties ended the appeal.
    no_merits_decision = "no-merits-decision"


@dataclass(frozen=True)
class Disposition:
    outcome: AppealOutcome
    cited: Citation
    moment: str = MOMENT
    rule: str = APPEAL_RULE


@dataclass(frozen=True)
class Unresolved:
    """The court has acted in a form the rule cannot read: maintainer triage."""

    reason: str
    candidates: tuple[Citation, ...]
    moment: str = MOMENT
    rule: str = APPEAL_RULE


@dataclass(frozen=True)
class Opening:
    """What one appellate docket says about its `appeal-disposition` event."""

    reply: Citation | None
    opens_on: date | None
    waiting_on: str | None
    resolution: Disposition | Unresolved | None
    #: A disposition the rule read came with no reply brief read before it.
    ruled_first: bool

    @property
    def is_event(self) -> bool:
        return self.opens_on is not None and not self.ruled_first


# --- the entry ---------------------------------------------------------------

# A clerk's marker in front of the text: a document number, a note that the
# entry was vacated or entered in error. The match is possessive, so a long
# bracketed prefix costs linear time.
_TAG = r"(?>\[[^\]]{0,80}\]\s*(?:--\s*)?)*+"
# An entry the clerk has voided, wherever the marker sits.
_VOID = re.compile(
    r"\[[^\]]{0,80}\b(?:vacated|stricken|withdrawn|entered\s+in\s+error)\b[^\]]{0,80}\]"
    r"|^\s*(?:opinion|memorandum|judgment)\s+(?:withdrawn|vacated)\b",
    re.I,
)
# Not the court of appeals' own act: a document received from another court,
# a party's filing, the Supreme Court's judgment.
_NOT_THIS_COURT = re.compile(
    r"\breceived\b|\bfiled\s+by\s+(?:appell|petitioner|respondent|amic|plaintiff|defendant)"
    r"|\bin\s+(?:support|opposition)\b|\bsupreme\s+court\s+of\s+the\s+united\s+states\b"
    r"|\bdistrict\s+judge\b|\b(?:order|opinion)\s+of\s+the\s+district\s+court\s*,",
    re.I,
)

# The court's own disposition entry, by its leading words.
_JUDGMENT_LEAD = re.compile(
    r"^\s*" + _TAG + r"(?:filed\s+)?(?:per\s+curiam\s+|summary\s+)?"
    r"(?:judgment|order\s+and\s+judgment)\b",
    re.I,
)
_OPINION_LEAD = re.compile(
    r"^\s*" + _TAG + r"(?:filed\s+)?(?:sealed\s+|redacted\s+|amended\s+|per\s+curiam\s+)*"
    r"(?:(?:non-?|not\s+)?precedential\s+|unpublished\s+|published\s+)?"
    r"(?:opinion|memorandum(?:\s+disposition)?|summary\s+order)\b",
    re.I,
)
_ORDER_LEAD = re.compile(
    r"^\s*" + _TAG + r"(?:filed\s+)?(?:(?:per\s+curiam|clerk'?s?|text)\s+)?order\b", re.I
)

_PETITION_FOR_REVIEW = re.compile(r"\bpetitions?\s+for\s+review\b", re.I)
# Words that mean the entry's result words may belong to something other than
# the panel's disposition of the whole appeal: a separate writing, a second
# appeal, a stay, a certified question, a collateral ruling.
_OTHER_SUBJECT = re.compile(
    r"\bdissent\w*|\bconcurr?\w*|\bwould\b|\bcross-?\s?appeal\w*|\ben\s+banc\b"
    r"|\bpending\s+appeal\b|\bcertif\w+|\bfees?\b|\bsanctions?\b|\bas\s+to\b"
    r"|\bappeals?\s+in\b|\bmotion\s+to\s+(?:dismiss|vacate)\b",
    re.I,
)

# The result in the court's capitals. Case matters here: lower-case prose in an
# opinion's summary speaks of what a court below vacated or dismissed.
_CAPS = re.compile(r"\b(AFFIRM|REVERS|VACAT|DISMISS)(?:ED|E|ES|S|ING)?\b(\s+IN\s+PART\b)?")
# A judgment entry that leads with its result, in any case.
_LEADING_RESULT = re.compile(
    r"^\s*" + _TAG + r"(?:per\s+curiam\s+)?judgment\s*[,:.-]\s*"
    r"((?:(?:affirmed|reversed|vacated|dismissed|remanded)(?:\s+in\s+part)?"
    r"(?:\s*(?:,|;|and)\s*)*)+)",
    re.I,
)
_WORD = re.compile(r"\b(affirm|revers|vacat|dismiss)\w*(\s+in\s+part\b)?", re.I)
# "that the judgment of the District Court be affirmed"; "affirming the
# judgment of the district court". The clause runs to its full stop.
_BE_RESULT = re.compile(
    r"\bthat\s+the\s+(?:judgment|orders?|decision)\s+of\s+the\s+district\s+court\b[^.;]{0,80}?"
    r"\bbe\s+((?:affirmed|reversed|vacated)\b[^.;]{0,120})",
    re.I,
)
_ING_RESULT = re.compile(
    r"\b((?:affirming|reversing|vacating)(?:\s+in\s+part)?(?:\s+and\s+"
    r"(?:affirming|reversing|vacating)(?:\s+in\s+part)?)?)\s+(?:the\s+)?"
    r"(?:judgment|orders?|decision)\s+of\s+the\s+district\s+court\b",
    re.I,
)

# An order's own words dismissing the appeal.
_DISMISSES_APPEAL = re.compile(
    r"\bappeal\s+(?:is\s+)?(?:hereby\s+)?(?:voluntarily\s+)?dismissed\b"
    r"|\bdismissing\s+(?:the\s+|this\s+)?appeal\b",
    re.I,
)
# The order speaks of a dismissal it does not make.
_NO_DISMISSAL = re.compile(
    r"\bshow\s+cause\b|\bshould\b|\bwhether\b|\bunless\b|\breferred\b|\bdeferred\b|\bshall\b", re.I
)
# The order dismisses less than the whole appeal.
_PARTIAL = re.compile(
    r"\bin\s+part\b|\bas\s+to\b|\bremain\w*|\bproceeds?\b|\bcross-?\s?appeal\w*|['\u2019]s\s+appeal\b"
    r"|\b(?:his|her|their)\s+appeal\b|\bappeals?\s+in\b|\bappeal\s+no\b",
    re.I,
)
_BY_PARTIES = re.compile(
    r"\bvoluntar\w+\s+dismiss\w*|\bvoluntarily\s+dismiss\w*|\bstipulat\w+\s+(?:\w+\s+){0,3}?dismiss\w*"
    r"|\bsettle\w*|\b42\s*\(\s*b\s*\)",
    re.I,
)
_BY_COURT = re.compile(
    r"\bdismiss\w*\b[^.;]{0,40}?\b(?:for\s+(?:lack|want)\s+of\s+(?:appellate\s+)?jurisdiction"
    r"|as\s+moot|as\s+untimely)\b",
    re.I,
)
_OTHER_REASON = re.compile(r"\bfailure\s+to\s+(?:prosecute|pay|comply|file)\b|\b42-1\b", re.I)

_STEMS = {
    "affirm": AppealOutcome.affirmed,
    "revers": AppealOutcome.reversed,
    "vacat": AppealOutcome.vacated,
    "dismiss": AppealOutcome.dismissed,
}


def _results(text: str) -> list[tuple[str, bool]]:
    return [(m.group(1).lower(), bool(m.group(2))) for m in _WORD.finditer(text)]


def _combine(found: Sequence[tuple[str, bool]]) -> AppealOutcome | str | None:
    """One outcome from the result words read, or the reason there is none."""
    stems = {stem.lower() for stem, _ in found}
    if not stems:
        return None
    partial = any(part for _, part in found)
    if len(stems) == 1 and not partial:
        (stem,) = stems
        return _STEMS[stem]
    if len(stems) > 1 and partial and "dismiss" not in stems:
        return AppealOutcome.mixed
    if partial:
        return "the entry states a result in part that the rule cannot pair with another"
    return "the entry states more than one result and does not say which part each reaches"


def _dismissal(text: str) -> AppealOutcome | str:
    parties = bool(_BY_PARTIES.search(text))
    court = bool(_BY_COURT.search(text))
    if _OTHER_REASON.search(text) or parties == court:
        return "a dismissal that does not say whether the parties or the court ended the appeal"
    return AppealOutcome.no_merits_decision if parties else AppealOutcome.dismissed


def _read_judgment(text: str) -> AppealOutcome | str | None:
    if _PETITION_FOR_REVIEW.search(text):
        return "the entry decides a petition for review, whose outcomes the stage does not name"
    found: list[tuple[str, bool]] = []
    leading = _LEADING_RESULT.match(text)
    if leading is not None:
        found = _results(leading.group(1))
        if found and _WORD.search(text, leading.end()):
            return "the judgment states a result and then speaks of another"
    if not found:
        for match in (*_BE_RESULT.finditer(text), *_ING_RESULT.finditer(text)):
            found.extend(_results(match.group(1)))
    if not found:
        found = [(m.group(1).lower(), bool(m.group(2))) for m in _CAPS.finditer(text)]
    if not found:
        # A bare judgment, or an opinion entry that states no result: the
        # result is in an entry beside it.
        return None
    if _OTHER_SUBJECT.search(text):
        return "the entry's result may not be the panel's disposition of the whole appeal"
    result = _combine(found)
    return _dismissal(text) if result is AppealOutcome.dismissed else result


def read_disposition(text: str) -> AppealOutcome | str | None:
    """What one entry's text says of the appeal's disposition.

    An outcome where the entry is the court's disposition in a form the rule
    reads, a reason (a string) where it is the court's disposition in a form
    the rule will not settle, and ``None`` where the entry disposes of
    nothing.
    """
    if _VOID.search(text) or _NOT_THIS_COURT.search(text):
        return None
    if _JUDGMENT_LEAD.match(text) or _OPINION_LEAD.match(text):
        return _read_judgment(text)
    if _ORDER_LEAD.match(text) and _DISMISSES_APPEAL.search(text):
        if _NO_DISMISSAL.search(text):
            return None
        if _PARTIAL.search(text):
            return "an order that dismisses less than the whole appeal"
        return _dismissal(text)
    return None


# --- briefing ----------------------------------------------------------------

# The appellant's reply brief as filed: the entry leads with the brief and
# says at once who filed it. A deadline, an extension, a deficiency notice, a
# paper copy received, a supplemental reply, a reply on a motion and another
# party's reply are not it.
_REPLY_BRIEF = re.compile(
    r"^\s*" + _TAG + r"(?:ecf\s+filer:\s*)?"
    r"(?P<lead>(?:(?:redacted|sealed|electronic|proof|final|corrected|amended|appellants?'?s?|"
    r"petitioners?'?s?)\s+)*)reply\s+brief\s*,?\s*(?:\[\d+\]\s*)?"
    r"(?:on\s+behalf\s+of|submitted\s+for\s+filing\s+by|filed\s+by)\s+(?P<who>\w+)",
    re.I,
)
_REPLY_SUBMITTED = re.compile(
    r"^\s*" + _TAG + r"submitted\s+\(ecf\)\s+reply\s+brief\s+for\s+review\.\s+submitted\s+by\s+"
    r"(?P<who>\w+)",
    re.I,
)
_APPELLANT = re.compile(r"^(?:appellant|petitioner)", re.I)
_OTHER_PARTY = re.compile(r"^(?:appellee|respondent|amic|intervenor|cross)", re.I)
_NOT_THE_REPLY = re.compile(
    r"\bstricken\b|\bdeficien\w*|\bdefective\b|\bmotion\b|\bsupplemental\b|\bcross-", re.I
)
_CROSS_APPEAL = re.compile(r"\bcross-?\s?appe(?:al|llant|llee)", re.I)


def is_reply_brief(text: str) -> bool:
    """Whether ``text`` is the appellant's reply brief as filed."""
    if _VOID.search(text) or _NOT_THE_REPLY.search(text):
        return False
    match = _REPLY_BRIEF.match(text)
    if match is not None:
        who = match.group("who")
        if _OTHER_PARTY.match(who):
            return False
        return bool(_APPELLANT.match(who) or _APPELLANT.search(match.group("lead").strip()))
    submitted = _REPLY_SUBMITTED.match(text)
    return submitted is not None and bool(_APPELLANT.match(submitted.group("who")))


def read_appeal(entries: Iterable[Mapping[str, Any]], *, today: date) -> Opening:
    """Read one appellate docket as of ``today``.

    Entries with no date or dated after ``today`` are not read, so a reading
    as of a past day sees what the docket showed then. The first entry that
    reads as a disposition is the resolution; entries the rule could not
    settle are triage candidates only where none reads.
    """
    ordered = [
        entry
        for entry in resolver._ordered(entries)
        if (resolver.cite(entry).date_filed or date.max) <= today
    ]
    reply: Citation | None = None
    crossed = False
    resolution: Disposition | Unresolved | None = None
    unread: list[tuple[Citation, str]] = []
    for entry in ordered:
        text = resolver._entry_text(entry)
        if not text:
            continue
        cited = resolver.cite(entry)
        if _CROSS_APPEAL.search(text):
            crossed = True
        if reply is None and is_reply_brief(text):
            reply = cited
        if resolution is not None:
            continue
        read = read_disposition(text)
        if isinstance(read, AppealOutcome):
            resolution = Disposition(read, cited)
        elif isinstance(read, str):
            unread.append((cited, read))
    if resolution is None and unread:
        resolution = Unresolved(unread[0][1], tuple(cited for cited, _ in unread))

    opens_on: date | None = None
    waiting_on: str | None = None
    if crossed:
        waiting_on = "a cross-appeal's briefing, which the rule does not read"
    elif reply is not None:
        opens_on = reply.date_filed
    else:
        waiting_on = "the appellant's reply brief"

    # Only a disposition the rule read closes an appeal that never opened: an
    # entry it could not settle may not be the disposition at all.
    ruled_first = False
    if isinstance(resolution, Disposition):
        resolved_on = resolution.cited.date_filed
        ruled_first = opens_on is None or resolved_on is None or resolved_on <= opens_on
    return Opening(
        reply=reply,
        opens_on=opens_on,
        waiting_on=None if ruled_first else waiting_on,
        resolution=resolution,
        ruled_first=ruled_first,
    )


# --- the dry run -------------------------------------------------------------


class SurveyRow(BaseModel):
    case: str
    docket: str
    stored: bool
    opens_on: date | None = None
    reply_entry: int | None = None
    waiting_on: str | None = None
    ruled_first: bool = False
    outcome: str | None = None
    triage: str | None = None
    resolved_on: date | None = None
    resolved_entry: int | None = None


class Survey(BaseModel):
    rule: str = APPEAL_RULE
    read_on: date
    appeals: list[SurveyRow]

    def counts(self) -> dict[str, int]:
        stored = [row for row in self.appeals if row.stored]
        events = [row for row in stored if row.opens_on is not None and not row.ruled_first]
        return {
            "listed": len(self.appeals),
            "stored": len(stored),
            "events": len(events),
            "ruled_first": sum(row.ruled_first for row in stored),
            "waiting": sum(row.waiting_on is not None for row in stored),
            "events_resolved": sum(row.outcome is not None for row in events),
            "events_triage": sum(row.triage is not None for row in events),
            "events_open": sum(row.outcome is None and row.triage is None for row in events),
        }


def survey(
    watchlist: AiWatchlist,
    entries_of: Callable[[str], Sequence[Mapping[str, Any]] | None],
    *,
    today: date,
) -> Survey:
    """Read every listed ``relation: appeal`` docket; ``entries_of`` maps a case id to entries."""
    rows: list[SurveyRow] = []
    seen: set[str] = set()
    for case in watchlist.cases:
        lead = ids.case_id(case.court, case.docket_id)
        for docket in case.related:
            docket_id = ids.case_id(docket.court, docket.docket_id)
            if docket.relation is not Relation.appeal or docket_id in seen:
                continue
            seen.add(docket_id)
            entries = entries_of(docket_id)
            if entries is None:
                rows.append(SurveyRow(case=lead, docket=docket_id, stored=False))
                continue
            opening = read_appeal(entries, today=today)
            resolution = opening.resolution
            cited = (
                resolution.cited
                if isinstance(resolution, Disposition)
                else resolution.candidates[0]
                if isinstance(resolution, Unresolved)
                else None
            )
            rows.append(
                SurveyRow(
                    case=lead,
                    docket=docket_id,
                    stored=True,
                    opens_on=opening.opens_on,
                    reply_entry=opening.reply.entry_number if opening.reply else None,
                    waiting_on=opening.waiting_on,
                    ruled_first=opening.ruled_first,
                    outcome=resolution.outcome if isinstance(resolution, Disposition) else None,
                    triage=resolution.reason if isinstance(resolution, Unresolved) else None,
                    resolved_on=cited.date_filed if cited else None,
                    resolved_entry=cited.entry_number if cited else None,
                )
            )
    return Survey(read_on=today, appeals=rows)


def summary_lines(result: Survey) -> list[str]:
    counts = result.counts()
    return [
        f"appeal-events ({result.rule}), read {result.read_on}: "
        + f"{counts['stored']} of {counts['listed']} listed appeal(s) stored",
        f"  {counts['events']} open an event, {counts['ruled_first']} disposed of with no reply "
        + f"brief read before it, {counts['waiting']} waiting",
        f"  of the {counts['events']} event(s): {counts['events_resolved']} resolved, "
        + f"{counts['events_triage']} to triage, {counts['events_open']} read as open",
    ]
