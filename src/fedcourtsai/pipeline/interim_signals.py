"""Reading the interim docket: what an application asks for, and how it ended.

The Court's applications are a separate matter from its petitions — a stay, an
injunction, a vacatur pending certiorari — and they resolve on a different
standard, before a different bench. This module is the pair of readers both the
scope decision and the event model turn on: what an application *is*, and what
happened to it.

**Most of the interim docket is administrative.** Over the parsed application
dockets, roughly **80%** are requests to extend the time to
file, granted by a single Justice as a matter of course. They are not forecasts:
the answer is nearly always yes, one Justice gives it, and nothing about the case
predicts it. Including them would do to the interim population what including IFP
petitions would do to the cert one — swamp the slice worth predicting with a
near-deterministic majority, and hand any base rate built over it a number that
describes the Court's calendar rather than its judgment.

So the scope reader exists to *separate* those, not to reject them: an extension
is a real docket event, correctly recorded, and simply not the thing predicted.

A leaf module: it depends only on the shared schema, so no consumer can form an
import cycle around it.
"""

from __future__ import annotations

import re
from datetime import date
from enum import StrEnum

from ..schemas import Disposition
from .cert_signals import entry_date


class ApplicationKind(StrEnum):
    """What an application asks the Court for.

    ``extension`` is the administrative majority — more time to file a petition
    or a brief. ``substantive`` is the interim docket proper: a stay, an
    injunction, a vacatur. ``unknown`` is neither, and is deliberately
    not folded into either — an application whose ask cannot be read is a
    coverage gap, and treating it as administrative would quietly shrink the
    predicted population while treating it as substantive would pad it.
    """

    extension = "extension"
    substantive = "substantive"
    unknown = "unknown"


# An application states its own ask immediately after its number:
#   "Application (24A1) to extend the time to file a petition for a writ of
#    certiorari from July 15, 2024 to September 13, 2024, submitted to ..."
#   "Application (24A1099) for a stay, submitted to The Chief Justice."
# Reading the ask from that clause rather than from the whole docket is what
# keeps the two apart: an extension's text contains "for a writ of certiorari" —
# the thing whose deadline is being extended — which a relief-shaped pattern run
# over the joined proceedings reads as a substantive request. Every one of a
# sampled 26 classified substantive that way; anchoring on the ask fixed it.
_ASK_RE = re.compile(r"application\s*\(\s*\d{2}A\d+\s*\)\s*(?P<ask>[^,.]{0,160})", re.I)

_EXTENSION_ASK_RE = re.compile(r"extend\w*\s+the\s+time|extension\s+of\s+time", re.I)

# `writ` is deliberately absent: "a petition for a writ of certiorari" is what an
# extension application is about, not what it asks the Court to do.
_SUBSTANTIVE_ASK_RE = re.compile(
    r"\bfor\s+an?\s+(?:stay|injunction|vacatur)\b"
    r"|\bto\s+vacate\b"
    r"|\bfor\s+injunctive\s+relief\b"
    r"|\bstay\s+of\s+(?:execution|mandate|judgment)\b",
    re.I,
)


def application_kind(entry_texts: list[str]) -> ApplicationKind:
    """What the application asks for, read from the clause that states it.

    Read from the application's own ask — the phrase following its docket number
    — rather than from the joined proceedings, because a later entry can mention
    relief the application never sought and an extension's ask names the writ
    whose deadline it extends.

    The first ask wins. An application has one purpose; a docket that later
    carries a second `Application (...)` reference is reciting a companion
    matter, not changing its own.
    """
    for text in entry_texts:
        match = _ASK_RE.search(text)
        if match is None:
            continue
        ask = match.group("ask")
        if _EXTENSION_ASK_RE.search(ask):
            return ApplicationKind.extension
        if _SUBSTANTIVE_ASK_RE.search(ask):
            return ApplicationKind.substantive
    return ApplicationKind.unknown


class ReferralPosture(StrEnum):
    """Which bench decided an application.

    The interim docket's aggregation rule turns on this and nothing else: a
    Circuit Justice may act alone, or refer the application to the full Court,
    which then decides by majority. The referral is an ordinary docket entry, so
    the posture is observable rather than inferred — which is what makes the
    stage modelable and not merely describable.
    """

    circuit_justice = "circuit-justice"
    referred_to_court = "referred-to-court"


_REFERRED_RE = re.compile(r"referred\s+to\s+the\s+court", re.I)

# The disposing language, anchored on the application itself so a recital of some
# other filing's fate cannot match. Both postures are covered:
#   "Application (24A650) denied by Justice Kagan."
#   "... presented to The Chief Justice and by him referred to the Court is denied."
#   "Application (24A1) granted by Justice Alito extending the time to file ..."
#   "Applications for stays (23A349, 23A350, 23A351, and 23A384) granted by the
#    Court." — one order disposing of four consolidated applications, so the
#    plural is not a stylistic variant but the shape a consolidated interim
#    matter always takes.
_INTERIM_SIGNALS: tuple[tuple[re.Pattern[str], Disposition, str], ...] = (
    (re.compile(r"applications?\b[^.]{0,200}?\bis\s+denied", re.I), Disposition.denied, "denied"),
    (re.compile(r"applications?\b[^.]{0,200}?\bdenied\b", re.I), Disposition.denied, "denied"),
    (
        re.compile(r"applications?\b[^.]{0,200}?\bis\s+granted", re.I),
        Disposition.granted,
        "granted",
    ),
    (re.compile(r"applications?\b[^.]{0,200}?\bgranted\b", re.I), Disposition.granted, "granted"),
    (
        re.compile(r"applications?\b[^.]{0,200}?\bwithdrawn\b", re.I),
        Disposition.withdrawn,
        "withdrawn",
    ),
    (
        re.compile(r"applications?\b[^.]{0,200}?\bdismissed\b", re.I),
        Disposition.dismissed,
        "dismissed",
    ),
)


def match_interim_disposition(text: str) -> tuple[Disposition, str] | None:
    """The disposition an entry records for its application, or ``None``.

    Denials are tested before grants, because the full-Court form states both
    words in one sentence — "presented to The Chief Justice and by him referred
    to the Court **is denied**" — and a grant-first scan would read the referral
    clause and stop.

    ``None`` is the ordinary case: most entries are filings, responses and
    letters, and none of them disposes of anything. It is also the right answer
    for an application the Court has *deferred* — "referred to the Court is
    deferred pending oral argument" decides nothing, and the disposition arrives
    in a later entry, sometimes months later and after argument.
    """
    for pattern, disposition, label in _INTERIM_SIGNALS:
        if pattern.search(text):
            return disposition, label
    return None


def referral_posture(entry_texts: list[str]) -> ReferralPosture:
    """Whether the full Court decided the application, or a Justice alone.

    Defaults to the single-Justice posture, which is the unmarked case: a
    referral leaves an entry, acting alone does not. So absence of evidence is
    the right reading here, unusually — the Court records the exception.
    """
    if any(_REFERRED_RE.search(text) for text in entry_texts):
        return ReferralPosture.referred_to_court
    return ReferralPosture.circuit_justice


def is_predictable_application(kind: ApplicationKind) -> bool:
    """Whether an application belongs in the predicted interim population.

    Only the substantive ones. An extension is excluded for the same reason IFP
    petitions are excluded from the cert tournament and for a stronger version of
    it: the answer is nearly always yes, one Justice gives it without the Court
    sitting, and no fact about the case moves it. A base rate over a population
    that is ~80% extensions would describe the Court's calendar, and a predictor
    scored against it would be rewarded for saying "granted" every time.

    ``unknown`` is excluded too, and that is the conservative direction: an
    application whose ask cannot be read is a parser gap, and admitting it would
    put a matter of unknown character into a scored population. Excluding it
    shrinks coverage visibly instead, which is the failure that gets noticed.
    """
    return kind is ApplicationKind.substantive


# The Court asking for a response is the interim docket's strongest cheap signal,
# and it is not the same event as a response arriving: a respondent may answer
# uninvited, but only the Court (or a Circuit Justice) requests one. That makes
# it the analogue of a CVSG rather than of a relist — an affirmative act of
# attention rather than a rescheduling.
_RESPONSE_REQUESTED_RE = re.compile(r"response\s+to\s+application[^.]{0,80}?requested", re.I)

# Both numbers of the Latin, because the plural is not a stylistic variant: a
# brief filed by several amici is docketed "Brief amici curiae of X, et al.
# filed." and one filed by a single amicus "Brief amicus curiae of X filed."
# Across the 2,459 SCOTUS dockets whose proceedings the corpus stores (newest
# stored snapshot 2026-07-13), 1,432 of the 3,028 entries this counts carry the
# plural — a singular-only reading takes about half the amicus record, and takes
# least of it on the dockets that draw the most interest. Every stored
# payload is a cert docket, so those figures measure the reading rather than
# this column's own population: an application's proceedings are not snapshotted,
# and the size of the correction there is unmeasured. The vocabulary is one
# Clerk's across both forms, which is what carries the reading over.
_AMICUS_RE = re.compile(r"amic(?:us|i)\s+curiae", re.I)


def response_requested(entry_texts: list[str]) -> bool:
    """Whether the Court or a Circuit Justice asked for a response."""
    return any(_RESPONSE_REQUESTED_RE.search(text) for text in entry_texts)


# The respondent's answer arriving, which is a different event from the Court
# asking for one: a respondent may answer uninvited, and a requested response
# may never be filed. Anchored on the entry's own opening clause, and requiring
# the filing verb, because the *request* shares the same opening — "Response to
# application (25A97) requested by Justice Alito, due by 4pm" — and an
# anchor-only pattern reads a third of the requests as filings.
#
# `.{0,200}?` rather than `[^.]{0,200}?`: respondent names carry periods ("et
# al.", "Dep't"), and stopping at the first one drops a third of the real
# filings.
_RESPONSE_FILED_RE = re.compile(
    r"^\s*response\s+to\s+(?:the\s+)?(?:application|request)\b.{0,200}?\bfiled\b", re.I
)


def response_requested_date(entries: list[tuple[str, str | None]]) -> date | None:
    """When the Court asked for a response, or ``None``.

    The dated sibling of :func:`response_requested`, which the escalation ladder
    reads as a flag. The two disagree in exactly one place and deliberately: an
    undated request sets the flag and yields no date, because a date here opens
    an event and fixes the moment a forecast is taken from.
    """
    return _first_dated(entries, _RESPONSE_REQUESTED_RE)


def response_filed_date(entries: list[tuple[str, str | None]]) -> date | None:
    """When a response to the application was filed, or ``None``.

    The **first** one wins: an application drawing several responses is
    answered once the first arrives, which is the moment being named.
    """
    return _first_dated(entries, _RESPONSE_FILED_RE)


def application_arrival_date(
    docket_number: str, entries: list[tuple[str, str | None]]
) -> date | None:
    """When the application itself reached the docket, or ``None``.

    The interim stage's arrival moment, read where the docket itself records
    it. The application form's docketing date is not always there to take, and
    on a row that carries none the submission entry is the only record of when
    the application arrived — without it the baseline declares an arrival
    moment whose date the corpus never held, and provisioning cannot place a
    cell at a moment it cannot date. It is also the better reading even where
    both exist: the cut a declared moment takes must keep the entry that states
    the application, and only this date is that entry's own.

    Anchored on the docket's **own** number in the parenthesized form the Clerk
    writes it in ("Application (26A11) for a stay, submitted to ..."), so a
    recital of a companion matter's application cannot supply the date. The
    anchor is the number **alone** in its parentheses, which means the
    consolidated form :func:`match_interim_disposition` reads ("applications
    for stays (23A349, 23A350) …") is not matched here: a docket whose only
    naming entries are consolidated yields ``None`` and keeps its docketing
    date, which is the safe direction — an arrival read off a companion's
    filing would place the cell at a moment this docket never had.

    The **earliest** dated match wins, where :func:`_first_dated` takes the
    first match in docket order. The two rules differ because the readings do:
    a response entry names a distinct filing whose first occurrence is the
    moment, while every match here is the *same* application, so the earliest
    is simply the one fact being read and no ordering assumption is needed to
    get it.

    ``None`` where the number is unusable or no entry naming it carries a
    readable date. Undated entries are skipped rather than guessed at, the same
    discipline :func:`_first_dated` applies and for the same reason: this date
    opens an event and fixes the moment a forecast is taken from.
    """
    number = docket_number.strip()
    if not number:
        return None
    anchor = re.compile(r"\(\s*" + re.escape(number) + r"\s*\)", re.I)
    filed: list[date] = []
    for text, raw in entries:
        if anchor.search(text) and (when := entry_date(raw)) is not None:
            filed.append(when)
    return min(filed) if filed else None


def _first_dated(entries: list[tuple[str, str | None]], pattern: re.Pattern[str]) -> date | None:
    """The earliest fully-dated entry matching ``pattern``, in docket order.

    Undated entries are skipped rather than guessed at — the same discipline
    every dated read in the pipeline applies, and it matters more here because
    these dates open events.
    """
    for text, raw in entries:
        if pattern.search(text):
            filed = entry_date(raw)
            if filed is not None:
                return filed
    return None


def amicus_briefs(entry_texts: list[str]) -> int:
    """How many amicus briefs the docket records.

    A count rather than a flag: on the interim docket amicus interest is a
    proxy for stakes, and one brief is a different signal from a dozen. Counted
    over entries, so a single entry naming several filers counts once — an
    undercount, and the direction that cannot manufacture salience.

    The Latin is what separates a brief on the record from an attempt at one,
    and the docket draws that line itself: an accepted filing is "Brief
    amic(us|i) curiae of X filed.", while the pre-acceptance shapes name their
    filer in English — "Motion for leave to file amicus brief …", "Amicus brief
    of X submitted.", "Amicus brief of X not accepted for filing." None of the
    three is a brief the Court has, and each is also a state a real brief passes
    *through*: the docket appends the acceptance as its own later entry rather
    than rewriting the earlier one, so counting the earlier entry counts one
    brief twice. Across the stored payloads (cert dockets, newest stored snapshot
    2026-07-13), 74 of the 86 `Amic(us|i) brief of X not accepted` entries are
    followed by a later `filed` entry naming the same lead amicus; none of the 7
    `submitted` entries has such a twin yet, six of them being three days old at
    their snapshot's date and the seventh sitting on a docket that reached
    argument and judgment without the brief ever being filed. So a pre-acceptance
    entry is either a brief the docket will count again in its own words, or one
    that never arrives — the two arms of one exclusion, and either alone would
    carry it. The corpus column max-latches, so an overcount is permanent while
    an undercount corrects itself on the next poll.

    That correction runs only while the application is open, because the
    rotation re-polls no resolved row and the outcome freezes the column as it
    stands — so a brief still awaiting the Clerk when the application resolves is
    missed for good. It is the deliberate side of the trade: a few days of lag on
    a handful of dockets, and a rare miss at the boundary, taken over an
    overcount that no later poll can undo.

    An *entry* that recites the phrase without being a brief still counts, and is
    left counting: 153 of the 3,028 counted entries are not `Brief amic(us|i)
    curiae …` — motions for leave to participate in oral argument as amicus
    curiae, the argument transcript's own line naming counsel for an amicus, an
    invitation to a court-appointed amicus. Narrowing there would move the count
    down, which a max-latched column cannot represent, so the column and a fresh
    reading of the same docket would stop agreeing.
    """
    return sum(1 for text in entry_texts if _AMICUS_RE.search(text))


def escalation_signals(entry_texts: list[str]) -> tuple[bool, bool, int]:
    """The three cheap signals an interim forecast can condition on.

    ``(response_requested, referred_to_court, amicus_briefs)``.

    All three are **monotone over an application's life** — the Court does not
    un-request a response, un-refer an application, or un-file an amicus brief —
    which is the same property the cert docket's distribution count has, and it
    carries the same two traps with it. A band derived from them at resolution is
    the band the application *ended* at, not the one a cell faced; and a rate
    conditioned on the ending band understates the rate a live application
    actually faces. `docs/salience.md` records how the cert program answers both,
    and the answers transfer unchanged.
    """
    return (
        response_requested(entry_texts),
        referral_posture(entry_texts) is ReferralPosture.referred_to_court,
        amicus_briefs(entry_texts),
    )
