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

**What joins two applications**, under ``controversy-v1``. Any one link joins,
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
3. **The same government application against the same challenger.** Both are
   government-filed and their captions name the same leading party on each
   side, once punctuation, case and ``et al.`` are set aside. This catches a
   renewed application on a new appeal of the same order. It is not applied
   to challengers' applications, whose respondent is an agency that many
   unrelated challenges name.

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

**Versioned like the scope rule.** ``controversy-v1`` is this set of links and
this outcome rule; a change to either is a new label.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Final

from .. import corpus
from .ingest import interim_disposing_text

#: This grouping rule's version.
CONTROVERSY_RULE_VERSION: Final[str] = "controversy-v1"

#: A lower-court case number: an appellate ``YY-NNNN`` or a district ``N:YY-cv-NNNN``.
_CASE_NUMBER_RE: Final = re.compile(r"\d+:\d{2}-[a-z]{2}-\d+|\b\d{2}-\d{1,5}\b", re.IGNORECASE)

#: An application docket number named in an order.
_APPLICATION_NUMBER_RE: Final = re.compile(r"\b\d{2}A\d+\b")

_ET_AL_RE: Final = re.compile(r"\bet\.?\s*al\.?", re.IGNORECASE)
_NON_WORD_RE: Final = re.compile(r"\W+")


@dataclass(frozen=True)
class ControversyLinks:
    """What one application can be joined on."""

    docket_number: str
    lower_cases: frozenset[tuple[str, str]]
    named: frozenset[str]
    caption: tuple[str, str] | None


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
) -> ControversyLinks:
    """The ``controversy-v1`` links of one application (module docstring for each).

    ``decided`` says whether the cut counts the application as decided; the
    disposing order is read only where it does.
    """
    lower_cases: frozenset[tuple[str, str]] = frozenset()
    named: frozenset[str] = frozenset()
    own = _normalized(row.docket_number)
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
    caption: tuple[str, str] | None = None
    applicant, separator, respondent = row.case_name.partition(" v. ")
    if government_applicant and separator and _lead(applicant) and _lead(respondent):
        caption = (_lead(applicant), _lead(respondent))
    return ControversyLinks(row.docket_number, lower_cases, named, caption)


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
    for item in items:
        own = _normalized(item.docket_number)
        for other in item.named:
            join(own, other)
        keys: list[tuple[str, object]] = [("lower", case) for case in item.lower_cases]
        if item.caption is not None:
            keys.append(("caption", item.caption))
        for key in keys:
            if key in by_key:
                join(by_key[key], own)
            else:
                by_key[key] = own
    return {spelled[key]: spelled[find(key)] for key in spelled}


def docket_order(docket_number: str) -> tuple[int, int, str]:
    """Sort key for an application number, any spelling: Term, then serial."""
    docket_number = _normalized(docket_number)
    match = re.fullmatch(r"(\d{2})A(\d+)", docket_number)
    if match is None:
        return (99, 0, docket_number)
    return (int(match.group(1)), int(match.group(2)), docket_number)
