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
from collections.abc import Sequence
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
# stored snapshot 2026-07-13), 1,432 of the 3,028 entries matching this pattern
# carry the plural — a singular-only reading takes about half the amicus record,
# and takes least of it on the dockets that draw the most interest. Every stored
# payload is a cert docket, so those figures measure the reading rather than
# this column's own population: an application's proceedings are not snapshotted,
# and the size of the correction there is unmeasured. The vocabulary is one
# Clerk's across both forms, which is what carries the reading over.
#
# This is the **accepted** form: the Latin is what the Clerk writes once a brief
# is on the record. :data:`_AMICUS_SUBMITTED_RE` reads the other half.
_AMICUS_RE = re.compile(r"amic(?:us|i)\s+curiae", re.I)

# The **submission** form, which the Latin never reaches. A brief that has
# arrived and is waiting on the Clerk is docketed in English, with the filer
# named where the accepted form names it: "Amicus brief of X submitted."
# The docket is recording a brief it has been handed, and the stakes proxy the
# column serves is about how much interest a matter draws, not about how far
# through the Clerk's queue that interest has travelled — so the submission
# counts, and :func:`amicus_briefs` dedupes it against its own later acceptance.
#
# Anchored at the entry's start and requiring the bare verb, which is what keeps
# the neighbouring motion-for-leave shape out: a motion opens with the motion and
# not with the brief ("Motion for leave to file amicus brief filed by X."), and
# leave is permission to file rather than a brief handed over.
#
# The filer span is unbounded (`.+?`) rather than capped, unlike the bounded
# spans elsewhere in this module: one submission entry can name seven
# organizations in a row, and a cap tidy enough to look reasonable drops
# precisely the entries carrying the most interest.
# `re.S` so a filer list wrapped across lines still reaches the verb — which is
# the shape the unbounded span exists for in the first place.
_AMICUS_SUBMITTED_RE = re.compile(
    r"^\s*amic(?:us|i)\s+brief\s+of\s+(?P<filer>.+?)\s+submitted\b", re.I | re.S
)

# The Clerk's **refusal**, which shares the submission's opening clause and is
# not a brief the Court has: "Amicus brief of X not accepted for filing. (To be
# corrected and resubmitted - April 9, 2025)". The verb above already misses it
# — `\bsubmitted\b` does not match inside `resubmitted` — but only by accident of
# one word's spelling, and a refusal phrased with the bare verb would otherwise
# be counted with the filer clause running off into the parenthetical. Stated as
# its own rule so the exclusion is one a reader can check.
#
# It is read per entry, so a refusal never un-counts an earlier submission by the
# same filer: that would make the reading fall as the docket grows, which the
# max-latched column cannot follow. :func:`amicus_briefs` states the trade.
_AMICUS_REFUSED_RE = re.compile(r"\bnot\s+accepted\b", re.I)


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


# The Clerk's **renewal** form, which the submission anchor below would
# otherwise read as an arrival: an application denied by one Justice is refiled
# to another under the same number — "Application (26A118) refiled and submitted
# to Justice Alito." It carries the filing verb, and it is never the arrival:
# on every refiled docket read for this rule a disposition of the same
# application had already landed at or before it, so a payload whose head entry
# is missing would be stamped after its own first denial. It is the shape
# `\bsubmitted\b` alone does *not* exclude — `resubmitted` is not the Clerk's
# spelling, `refiled and submitted` is — and it is common: 14 of 70 substantive
# application dockets read for this rule carry one.
#
# Matched entries are skipped whole rather than excluded inside the anchor's
# span, so the exclusion is one rule a reader can check instead of a lookahead
# buried in a pattern. The cost is an arrival entry that describes *itself* as a
# refiling (an application first submitted here after being refiled from another
# docket), which falls back to the docketing date — merely late, the safe way to
# be wrong.
_APPLICATION_RENEWAL_RE = re.compile(r"\brefiled\b", re.I)


def application_arrival_date(
    docket_number: str, entries: list[tuple[str, str | None]]
) -> date | None:
    """When the application itself reached the docket, or ``None``.

    The interim stage's arrival moment, read where the docket itself records
    it: the entry in which the application is *submitted*. The docketing date
    is the alternative, and it is the worse reading in both directions. It is
    not always there to take — on a row carrying none the baseline would
    declare an arrival moment whose date the corpus never held, and
    provisioning cannot place a cell at a moment it cannot date. And where it
    is there it runs **late**: over 60 substantive application dockets the
    submission entry precedes docketing on 34, by a median 5 days and up to 64,
    and follows it on none. Late is the enlarging direction — a cut taken a day
    after docketing admits filings the arrival moment never saw.

    Anchored on the **submission clause** of the docket's *own* application
    number ("Application (26A11) for a stay, submitted to ..."), in the
    :data:`_RESPONSE_FILED_RE` idiom: the number in its parentheses, then the
    filing verb within a bounded span. Both halves carry weight, and the verb
    carries the sharper one. The number alone would match every later entry
    reciting it, and on 50 of 60 sampled dockets the next entry naming the
    number **is the disposition** — so an application whose head entry is
    missing from a degraded payload would be stamped at the day it was decided,
    and the cell provisioned under a well-formed ``truncated`` cutoff that
    admits its own outcome. Requiring the verb refuses that: the clause matched
    the head entry of all 150 live application dockets read for this rule and
    matched no disposition entry on any of them.

    The verb is necessary but not sufficient, which is what
    :data:`_APPLICATION_RENEWAL_RE` is for — read it before trusting the
    paragraph above, because the renewal form carries the verb too.

    The span is ``.{0,200}?`` rather than ``[^.]{0,200}?`` as **headroom**, not
    as an observed need: no matched entry on those 150 dockets required it
    (``[^.]`` matches every one, the longest span being 139 characters against
    the 200 bound). :data:`_RESPONSE_FILED_RE` documents the form that would —
    text between the number and the verb naming courts and parties that carry
    periods — and the permissive span costs nothing here.

    The consolidated form :func:`match_interim_disposition` reads
    ("applications for stays (23A349, 23A350) …") does not match, though the
    verb rather than the number is what excludes it: that shape is a *disposing*
    order. A docket whose application was submitted under a consolidated caption
    falls back to docketing rather than borrowing a companion's date.

    The **earliest** dated match wins, where :func:`_first_dated` takes the
    first in docket order. The two rules differ because the readings do: a
    response entry names a distinct filing whose first occurrence is the
    moment, while every match here is the same application being submitted, so
    the earliest is the arrival and no ordering assumption is needed to get it.
    It is also the second half of the renewal defence — on a docket carrying
    both a head entry and a refiling, ``min`` keeps the head even before the
    renewal exclusion is reached.

    ``None`` where the number is unusable or no submission entry carries a
    readable date. Undated entries are skipped rather than guessed at, the same
    discipline :func:`_first_dated` applies and for the same reason: this date
    opens an event and fixes the moment a forecast is taken from.
    """
    number = docket_number.strip()
    if not number:
        return None
    anchor = re.compile(
        r"application\s*\(\s*" + re.escape(number) + r"\s*\).{0,200}?\bsubmitted\b", re.I
    )
    filed: list[date] = []
    for text, raw in entries:
        if _APPLICATION_RENEWAL_RE.search(text):
            continue
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


# The accepted entry's own filer clause — the name between "amic(us|i) curiae
# of" and the filing verb, which is where "Brief amici curiae of X, et al. filed.
# VIDED. (Distributed)" says who filed. Reading the clause rather than the whole
# entry is what makes the filer comparison below mean anything: matched against
# the entry entire, a name would keep finding itself inside the boilerplate the
# Clerk wraps every acceptance in.
#
# An accepted-form entry that names no filer this way contributes none, and that
# is right rather than lossy: those entries are the recitals — a motion to
# participate in argument as amicus curiae, an argument transcript's counsel
# line, an invitation to a court-appointed amicus — and none of them is the
# acceptance of a submitted brief.
_ACCEPTED_FILER_RE = re.compile(r"amic(?:us|i)\s+curiae\s+of\s+(?P<filer>.+?)\s+filed\b", re.I)


def _lead_filer(name: str) -> str:
    """A filer name reduced to the form two entries can be matched on.

    Case, surrounding whitespace, internal run-length and trailing punctuation
    are all things the Clerk varies between the submission entry and the
    acceptance entry for the same brief, so all four are normalized away. The
    name is then cut at its first comma, leaving the **lead** amicus: a brief
    filed by several is docketed under its first filer and an "et al." whose
    presence and spelling differ between the two entries, and the lead name is
    the part that does not move.
    """
    lead = name.split(",", maxsplit=1)[0]
    return re.sub(r"\s+", " ", lead).strip().strip(".,;:").casefold()


def _submitted_filer(text: str) -> str | None:
    """The lead filer a submission entry names, or ``None`` if it is not one."""
    if _AMICUS_REFUSED_RE.search(text):
        return None
    match = _AMICUS_SUBMITTED_RE.match(text)
    if match is None:
        return None
    return _lead_filer(match.group("filer")) or None


def _accepted_filer(text: str) -> str | None:
    """The lead filer an accepted entry names, or ``None`` if it names none."""
    match = _ACCEPTED_FILER_RE.search(text)
    if match is None:
        return None
    return _lead_filer(match.group("filer")) or None


def amicus_briefs(entry_texts: list[str]) -> int:
    """How many amicus briefs the docket records.

    A count rather than a flag: on the interim docket amicus interest is a
    proxy for stakes, and one brief is a different signal from a dozen.

    The docket writes a brief twice, in two vocabularies. An accepted filing
    takes the Latin — "Brief amic(us|i) curiae of X filed." — and a brief handed
    in but not yet on the record takes English — "Amicus brief of X submitted."
    Both are briefs the docket records, so both count; what must not happen is
    that one brief counts twice as it moves from the second form to the first,
    because the Clerk appends the acceptance as its own later entry rather than
    rewriting the earlier one. So the count is:

    - every entry in the accepted form, one per entry; plus
    - every **distinct lead filer** in the submitted form that no accepted entry
      names.

    Both halves of that dedup are doing work. It is keyed on the *filer* rather
    than on the entry, so a docket carrying the same submission twice still
    contributes one; and it is keyed on the **lead** filer — the name before the
    first comma, :func:`_lead_filer` — because a brief filed by several amici is
    docketed under its first one, and the "et al." that follows is spelled and
    punctuated differently between the submission entry and the acceptance entry
    for the same brief. Matching on the lead name is what lets the two entries
    recognize each other. Where it over-matches — two genuinely different amici
    whose names agree up to their first comma — the count is one short, which is
    the direction that cannot manufacture salience.

    Two pre-acceptance shapes stay out, and neither is a brief the docket has
    been handed. A **motion for leave** asks permission to file; the brief may
    never follow, and the docket says so in its own later entry when leave is
    denied. A **refusal** — "Amicus brief of X not accepted for filing. (To be
    corrected and resubmitted - April 9, 2025)" — is a brief the Clerk turned
    away; over the stored payloads (cert dockets, newest stored snapshot
    2026-07-13), 74 of the 86 such entries are followed by a later `filed` entry
    naming the same lead amicus, which is where that brief is counted. The
    refusal rule reaches the English form only: an entry that refuses a brief
    while reciting the Latin ("Brief amicus curiae of X not accepted for
    filing.") is counted by the accepted arm, as it was before this reading, and
    is left counting for the same reason the recitals below are.

    **Every rule here only ever adds to the accepted-entry count**, and that is a
    constraint rather than an observation. The corpus column max-latches, so a
    reading that could return *less* than a previously stored one would leave the
    column and a fresh read of the same docket permanently disagreeing, with no
    way to bring the column down. The submitted arm is therefore expressed as an
    addition over a disjoint set of entries — an entry already in the accepted
    form is never re-read as a submission — and never as a re-interpretation of
    entries the accepted form already counts.

    The same constraint fixes what happens when a submission is later *refused*:
    it stays counted, an overcount of one on that docket. Un-counting it would
    make this function non-monotone over an append-only docket, which the
    max-latch cannot follow; and the 74/86 figure above says the usual sequel to
    a refusal is a corrected refiling that the accepted arm counts anyway.
    Accepting the overcount is the cheaper of the two errors.

    An *entry* that recites the Latin without being a brief still counts, and is
    left counting: 153 of the 3,028 accepted-form entries are not `Brief
    amic(us|i) curiae …` — motions for leave to participate in oral argument as
    amicus curiae, the argument transcript's own line naming counsel for an
    amicus, an invitation to a court-appointed amicus. Narrowing there would move
    the count down, which the paragraph above rules out.

    Reads every entry it is given. :func:`amicus_briefs_through` is the bounded
    form, and it is what the corpus column is derived through.
    """
    on_record = [text for text in entry_texts if _AMICUS_RE.search(text)]
    accepted = {filer for text in on_record if (filer := _accepted_filer(text)) is not None}
    pending: set[str] = set()
    for text in entry_texts:
        # Disjoint by construction: an entry the accepted form already counts is
        # never re-read as a submission, which is what makes the second term
        # purely additive and so latch-compatible.
        if _AMICUS_RE.search(text):
            continue
        filer = _submitted_filer(text)
        if filer is not None and filer not in accepted:
            pending.add(filer)
    return len(on_record) + len(pending)


def interim_disposition_date(entries: Sequence[tuple[str, str | None]]) -> date | None:
    """The day the application was disposed of, read strictly, or ``None``.

    The cut date :func:`amicus_briefs_through` takes, and it is read here rather
    than borrowed from the stored ``date_terminated`` because the two need
    different strictness. A stored date merely records; this one decides which
    entries are retained in a **max-latched** column, so a date that is partly a
    function of the day the parser ran would drop genuinely-dated entries and
    the latch would make the drop permanent. :func:`~..cert_signals.entry_date`
    refuses a partial string, and an unreadable disposition date yields ``None``
    — no cut at all, which is the conservative direction.

    The **last** disposing entry wins, the rule the interim resolver applies and
    for the same reason: an application can be deferred pending argument and
    decided months later, and a consolidated order can dispose of several at
    once. In both the earlier entry is a step rather than the outcome.
    """
    decided: date | None = None
    for text, raw in entries:
        if match_interim_disposition(text) is None:
            continue
        when = entry_date(raw)
        if when is not None:
            decided = when
    return decided


def amicus_briefs_through(entries: Sequence[tuple[str, str | None]], through: date | None) -> int:
    """How many amicus briefs the docket records **through the end of** ``through``.

    The resolution-side cut, and the semantics it fixes are **end of day**: an
    entry dated on ``through`` counts, and an entry dated after it does not. That
    is the reading an application's disposition takes — the corpus column is
    frozen onto the outcome as the state at resolution, and the resolution value
    is a statement about the docket the Court decided rather than an information
    set anyone forecast from. The alternative is to stop at the disposing entry
    itself, as the *prediction* side stops at the entry that opened the event, and
    it is declined rather than unavailable: within-day docket order is observable
    (a submission can and does appear after the denial that decided the matter),
    but ordering the resolution end by it would have that end answer a question
    about a forecaster nobody asked about.

    Without the bound the count is limited by nothing but the poll: the derivation
    runs over whatever entries the payload carries, so an entry filed *after* the
    disposition day that happens to land in a poll before resolution is detected
    is counted into a column labelled "as at resolution".

    ``through`` is ``None`` on an open application, which has no day to be cut at
    — and also, deliberately but less happily, on a **resolved** one whose
    disposing entry carries no readable date, since the caller reads the date off
    that entry. Such a row keeps the unbounded reading, which is the leak this
    function exists to close, on a path that raises nothing. The bound is
    date-conditioned and the size of that arm is unmeasured; `docs/salience.md`
    and `docs/freeze-record.md` say so where a reader of the column will look.

    **Undated entries always count.** Dropping them would make the bounded count
    fall below the unbounded one for a reason that has nothing to do with the
    cut, and the entry may well predate the disposition. That is the opposite
    discipline to :func:`_first_dated`, which skips undated entries, and the
    readings differ because the stakes do: there a guessed date opens an event,
    here a dropped entry silently lowers a latched column.

    **The residual, stated plainly.** The corpus column max-latches, so this
    bound can only govern derivations that run while it applies. A row polled
    before its disposition date was readable — the ordinary case for a live
    application, whose column is written on every poll — latched whatever the
    unbounded reading gave at the time, and a later bounded derivation cannot
    bring it back down. So the cut governs the *derivation*, not the stored
    value: it removes the after-the-fact entries a resolution-detecting poll
    would otherwise add, and leaves untouched any count that had already latched
    high. Bringing those rows down is a corpus re-derivation, which only a writer
    job can do.
    """
    if through is None:
        return amicus_briefs([text for text, _ in entries])
    kept = [text for text, raw in entries if (when := entry_date(raw)) is None or when <= through]
    return amicus_briefs(kept)


def escalation_signals(
    entries: Sequence[tuple[str, str | None]], *, through: date | None = None
) -> tuple[bool, bool, int]:
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

    Takes dated entries rather than bare texts because ``through`` bounds the
    amicus count at the end of that day (:func:`amicus_briefs_through`) — the
    resolution-side cut, passed as the disposition date by the ingest derivation
    and left ``None`` by every reader whose entries are already cut at its own
    moment. Monotonicity is a statement about a *fixed* cut: the count only grows
    as entries accumulate before ``through``.

    **The bound reaches the count and not the two flags**, and the returned tuple
    is therefore mixed-cut when ``through`` is given. That is scope, not a claim
    that the flags cannot move late: an end-of-day bound would apply to them
    unchanged, and a response request or referral entered after the disposition
    is the same leak. It is left out because each flag resolves its own
    registered claim, so bounding them is its own change with its own
    registration, and the size of the arm it would move is unmeasured.
    """
    texts = [text for text, _ in entries]
    return (
        response_requested(texts),
        referral_posture(texts) is ReferralPosture.referred_to_court,
        amicus_briefs_through(entries, through),
    )
