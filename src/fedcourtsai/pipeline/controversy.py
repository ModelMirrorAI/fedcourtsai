"""Controversy grouping for analytics: which emergency applications are one dispute.

Read-side only and deliberately not a prediction input: every value is a pure
function of an application row, its latest live-shaped snapshot and the side
the scope rule (:mod:`.exec_action`) puts the government on. The one consumer
is the executive success cut (:mod:`.executive_success`).

**Why group.** One executive policy can reach the Court as several
applications: the same appeal renewed, companion applications from three
circuits decided in one order, a second application after the first was
withdrawn. Counted one by one, a policy litigated often weighs more than one
litigated once, so the published tallies report a controversy-level rate
beside the application-level one. The corpus stores one row per application
and no grouping key; this rule supplies one.

**What joins two applications**, under ``controversy-v2``. Any one link joins,
and the groups are the connected sets, so a link through a third application
joins too.

1. **The same case below.** Both applications name the same lower court and
   share a case number in the docket's ``LowerCourtCaseNumbers``. A
   consolidated appeal lists every member number, so its applications share
   one. The numbers read are a two-digit-year appellate number (``25-1234``)
   and a district number with its office prefix (``1:25-cv-01234``); another
   format links nothing.
2. **Decided together.** The order disposing of one application names the
   other's docket number ("Applications … (24A884, 24A885, and 24A886)
   granted"). It is read only for an application the cut counts as decided,
   so a cut at a past moment never joins on an order that moment had not
   reached.
3. **One order text on one day.** The Court often decides companion
   applications in separate entries that read the same: "Application (24A95)
   for stay presented to The Chief Justice and by him referred to the Court is
   denied", with the same statements after it, on every docket of one cluster,
   whatever the case below. Two decided applications join where their
   disposing texts are the same once markup and each one's own docket number
   are set aside, on the same decision date, from the same court below, with the same
   leading party on the government's side of the caption. The last two
   conditions keep a bare one-line order shared by unrelated applications on
   one day from joining them in most cases, though not all: two unrelated
   challenges to one officer from one circuit, denied the same day by the
   same bare order, still join, and each review row's ``controversy_id``
   shows it.
4. **The same government application against the same challenger, close in
   time.** Both are government-filed, their captions name the same leading
   party on each side once punctuation, case and ``et al.`` are set aside, and
   the later one was filed within :data:`CAPTION_LINK_DAYS` of the earlier
   one's decision (of its filing, where it has none). Where both carry a court
   below it must be the same. This catches a renewed application on a new
   appeal of the same order, and leaves apart two policies a caption names
   alike years apart (*Biden v. Missouri* on a vaccine rule and on a loan
   plan, *United States v. Texas* on SB8 and on enforcement priorities). It is
   not applied to challengers' applications, whose respondent is an agency
   that many unrelated challenges name.

Three things the rule does not do. It reads no text beyond the disposing
order, so two challenges to one policy brought by different parties in
different circuits, and decided separately, stay two controversies. An
officer's name changes on a transition, so a government caption that names
the officer rather than the agency does not join across one. And groups are
formed over the cut's rows whatever their dates, so a controversy can span a
transition; it takes its first dated application's administration.

**The controversy's outcome** is the executive's result in its last
substantively decided application, by the stored decision date (a decided
application with none sorts first), the later-docketed application winning a
tie. A controversy with no substantively decided application is indeterminate
and sits beside the rate. Its administration is that of its first-filed
application with a date under the cut's convention (under ``resolved``, a
pending first application passes it to the next), and its filer is
``government`` or ``challenger`` where every application in it was filed by
one side, else ``both``.

**Versioned like the scope rule.** ``controversy-v2`` is this set of links and
this outcome rule; a change to either is a new label. ``controversy-v1``
is links 1, 2 and 4, with link 4 bounded by neither time nor court; no code
computes it now, and the figures quoted under it are records of that rule.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Final

from .. import corpus
from .ingest import interim_disposing_text

#: This grouping rule's version.
CONTROVERSY_RULE_VERSION: Final[str] = "controversy-v2"

#: How soon after an application's decision a same-caption government
#: application still joins it: long enough for a renewed application on the
#: next appeal of one order, short of a new dispute under an old caption. Set
#: between the two: renewed applications in one dispute follow at 123 days
#: (24A1059 to 25A326) and 187 days (24A831 to 25A269), and the nearest new
#: dispute under an old caption at 263 days (21A85 to 22A17).
CAPTION_LINK_DAYS: Final[int] = 210

#: A lower-court case number: an appellate ``YY-NNNN`` or a district ``N:YY-cv-NNNN``.
_CASE_NUMBER_RE: Final = re.compile(r"\d+:\d{2}-[a-z]{2}-\d+|\b\d{2}-\d{1,5}\b", re.IGNORECASE)

#: An application docket number named in an order.
_APPLICATION_NUMBER_RE: Final = re.compile(r"\b\d{2}A\d+\b")

_ET_AL_RE: Final = re.compile(r"\bet\.?\s*al\.?", re.IGNORECASE)
_NON_WORD_RE: Final = re.compile(r"\W+")
_WORD_RE: Final = re.compile(r"\w+")
_MARKUP_RE: Final = re.compile(r"<[^>]*>")


@dataclass(frozen=True)
class ControversyLinks:
    """What one application can be joined on."""

    docket_number: str
    lower_cases: frozenset[tuple[str, str]]
    named: frozenset[str]
    caption: tuple[str, str] | None
    order: tuple[str, date, str, str] | None = None
    lower_court: str = ""
    filed: date | None = None
    ended: date | None = None


def _lead(half: str) -> str:
    """A caption half's leading party, normalized: up to its first comma, words only."""
    head = _ET_AL_RE.sub(" ", half.split(",", 1)[0])
    return _NON_WORD_RE.sub(" ", head).strip().casefold()


def controversy_links(
    row: corpus.CorpusRow,
    payload: Mapping[str, Any] | None,
    *,
    government_applicant: bool,
    decided: bool,
    filed: date | None = None,
    resolved: date | None = None,
) -> ControversyLinks:
    """The ``controversy-v2`` links of one application (module docstring for each).

    ``decided`` says whether the cut counts the application as decided; the
    disposing order is read only where it does. ``filed`` is the cut's filing
    date for the row and ``resolved`` its stored decision date; the order-text
    and caption links need them, and an application without them joins on
    neither.
    """
    lower_cases: frozenset[tuple[str, str]] = frozenset()
    named: frozenset[str] = frozenset()
    order: tuple[str, date, str, str] | None = None
    court = ""
    own = _normalized(row.docket_number)
    applicant, separator, respondent = row.case_name.partition(" v. ")
    government_lead = _lead(applicant if government_applicant else respondent) if separator else ""
    if payload is not None:
        court = str(payload.get("LowerCourt") or "").strip().casefold()
        numbers = str(payload.get("LowerCourtCaseNumbers") or "")
        if court:
            lower_cases = frozenset(
                (court, number.casefold()) for number in _CASE_NUMBER_RE.findall(numbers)
            )
        if decided:
            text = interim_disposing_text(payload) or ""
            named = frozenset(_APPLICATION_NUMBER_RE.findall(text.upper())) - {own}
            body = _order_body(text, own)
            if body and court and resolved is not None and government_lead:
                order = (court, resolved, body, government_lead)
    caption: tuple[str, str] | None = None
    if government_applicant and separator and _lead(applicant) and _lead(respondent):
        caption = (_lead(applicant), _lead(respondent))
    return ControversyLinks(
        row.docket_number,
        lower_cases,
        named,
        caption,
        order=order,
        lower_court=court,
        filed=filed,
        ended=resolved or filed,
    )


def _order_body(text: str, own: str) -> str:
    """A disposing text with markup and the application's own number set aside, normalized.

    The lead docket of a cluster carries the order's opinion as a link
    (``<a href='…/24a95_n7ip.pdf'>opinion</a>``) where its companions carry
    the bare word, so the markup is read as its text, and the texts are
    compared word by word, punctuation and spacing aside.
    """
    body = _MARKUP_RE.sub(" ", text).upper()
    body = re.sub(rf"\b{re.escape(own)}\b", " ", body)
    return " ".join(_WORD_RE.findall(body)).casefold()


def _caption_joins(first: ControversyLinks, second: ControversyLinks) -> bool:
    """Whether two same-caption government applications are close enough to join."""
    if first.lower_court and second.lower_court and first.lower_court != second.lower_court:
        return False
    if first.filed is None or second.filed is None:
        return False
    earlier, later = sorted((first, second), key=lambda item: item.filed or date.min)
    end = earlier.ended or earlier.filed
    return (
        end is not None
        and later.filed is not None
        and later.filed <= end + timedelta(days=CAPTION_LINK_DAYS)
    )


def _normalized(docket_number: str) -> str:
    return docket_number.strip().upper()


def group_controversies(links: Iterable[ControversyLinks]) -> dict[str, str]:
    """Each docket number's controversy id: the smallest docket number in its group.

    Keys and ids are the docket numbers as the rows spell them; they are
    compared case- and space-insensitively, and by Term and serial (``24A95``
    before ``24A105``), so an id names the group's first-docketed application.
    """
    items = list(links)
    spelled = {_normalized(item.docket_number): item.docket_number for item in items}
    parent = {key: key for key in spelled}

    def find(key: str) -> str:
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    def join(left: str, right: str) -> None:
        if right not in parent:
            return
        a, b = find(left), find(right)
        if a != b:
            first, second = sorted((a, b), key=docket_order)
            parent[second] = first

    by_key: dict[tuple[str, object], str] = {}
    by_caption: dict[tuple[str, str], list[ControversyLinks]] = {}
    for item in items:
        own = _normalized(item.docket_number)
        for other in item.named:
            join(own, other)
        keys: list[tuple[str, object]] = [("lower", case) for case in item.lower_cases]
        if item.order is not None:
            keys.append(("order", item.order))
        for key in keys:
            if key in by_key:
                join(by_key[key], own)
            else:
                by_key[key] = own
        if item.caption is not None:
            by_caption.setdefault(item.caption, []).append(item)
    for alike in by_caption.values():
        for index, first in enumerate(alike):
            for second in alike[index + 1 :]:
                if _caption_joins(first, second):
                    join(_normalized(first.docket_number), _normalized(second.docket_number))
    return {spelled[key]: spelled[find(key)] for key in spelled}


def docket_order(docket_number: str) -> tuple[int, int, str]:
    """Sort key for an application number, any spelling: Term, then serial."""
    docket_number = _normalized(docket_number)
    match = re.fullmatch(r"(\d{2})A(\d+)", docket_number)
    if match is None:
        return (99, 0, docket_number)
    return (int(match.group(1)), int(match.group(2)), docket_number)
