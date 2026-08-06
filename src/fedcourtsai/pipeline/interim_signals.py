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
from enum import StrEnum

from ..schemas import Disposition


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
_AMICUS_RE = re.compile(r"amicus\s+curiae", re.I)


def response_requested(entry_texts: list[str]) -> bool:
    """Whether the Court or a Circuit Justice asked for a response."""
    return any(_RESPONSE_REQUESTED_RE.search(text) for text in entry_texts)


def amicus_briefs(entry_texts: list[str]) -> int:
    """How many amicus briefs the docket records.

    A count rather than a flag: on the interim docket amicus interest is a
    proxy for stakes, and one brief is a different signal from a dozen. Counted
    over entries, so a single entry naming several filers counts once — an
    undercount, and the direction that cannot manufacture salience.
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
