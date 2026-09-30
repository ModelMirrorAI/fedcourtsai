"""Counsel-derived case annotations for analytics: is the Solicitor General's office counsel?

Read-side only and deliberately not a prediction input, like the party
annotations it sits beside (:mod:`.party`): every value is a pure function of
a corpus row's stored ``counsel`` entries, its own dates, and a committed roster,
so a cut re-derives from a corpus pointer with no stored column, no writer lane
and no model spend. The one consumer is the party rates cut
(:mod:`.party_rates`), and only when a caller asks for it.

**What the annotation reads.** The SCOTUS live channel stores one
:class:`~fedcourtsai.corpus.CounselEntry` per party/attorney pairing with the
side it appears for. This module reads the ``petitioner`` and ``respondent``
entries only. ``other`` (amici, invited briefs, intervenors) is never read: it
accrues overwhelmingly after a grant, so an ``other`` entry naming the
Solicitor General on a decided docket is a grant oracle, not a covariate.

**Why a dated roster, not a name list.** The index stores no firm or office
for an attorney, so "the Solicitor General's office" has to be read from who
the attorney *is*. A bare name list over-reads in both directions of time: a
former Solicitor General turns up as private counsel at a firm (petitioner side
especially), and a future one turns up before taking office — as a state
solicitor general, or as private counsel. So every roster member carries the
dated spans in which they held a post that signs the government's Supreme Court
filings (:data:`SG_OFFICE_ROSTER`), and a name counts as the office only on a
docket whose own life overlaps one of those spans. The spans are the office's,
not the person's career: a name on a docket filed after the member left is
private practice, however federal the party looks.

**The docket's life, from its own dates.** A docket is live from its filing
date to its resolution: ``date_decided`` or the cert denial date where the row
carries one. A granted petition's merits judgment is not stored on the row
(``date_decided`` is absent on every granted live-slice row the rule was
measured on), so a granted docket's life runs a fixed :data:`MERITS_SPAN` past
the grant. A pending docket runs to the cut's moment, or is open-ended without
one. A docket that cannot be dated at all answers ``unknown`` for any side a
roster name sits on, rather than a guess, and so does a resolved docket that
stores no closing date, unless the member was in office when it was filed.

**A successor signing after the resolution.** The stored counsel list is as of
the row's last write, and a later filing on a closed docket — a rehearing
response, a letter — puts the Solicitor General then in office on it. So a
roster member whose span starts *after* the docket's life ended still counts,
but only where the entry's party reads as the federal government
(:func:`_federal_party`): that is the one party a future Solicitor General can
never have represented in private practice. A span that ended *before* the
docket was filed never counts, because a successor, never a predecessor, is
what a late write adds.

**A cut rewinds the docket's life, not its counsel list.** Under a ``moment``
the life ends at the cut, but the list is still the one the row holds now, so a
successor the list gained after the cut is on it. That name takes the same
path as any late write — the office on a federal party, private practice
otherwise — rather than being read as a private appearance because the cut
predates the span: the list is post-cut either way, and a successor's name on
a federal party is the office.

**Versioned like the party rules, and for the same reason.** ``sg-office-v1``
is this roster together with this rule; :data:`COUNSEL_RULES` registers it
under that label, and a change to either one is a new label beside it, never an
edit to this one. The rule reads the party-v2 class predicate
(:func:`.party.classify_party_v2`) and changes nothing about it.

Honest limits, stated here and in the reading rule (``metrics/README.md``):
all but about a dozen resolved IFP rows carry no counsel in the index today,
so they read ``unknown``, not ``no``; counsel blocks accrue after docketing, so a pending
docket's ``no`` is provisional and a ``--through`` cut still reads the counsel
the row holds now; the roster names the office's leadership (Solicitors
General, acting Solicitors General, principal deputies) and one career deputy,
so an Assistant to the Solicitor General or another deputy signing as counsel
of record is missed without trace; and a name is matched on
its listed spellings only, so a spelling outside them is missed too.
"""

from __future__ import annotations

import html
import re
import unicodedata
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from types import MappingProxyType
from typing import Final, Literal

from .. import corpus
from .party import classify_party_v2

#: One side's reading: the office is counsel on it, is not, or the row cannot say.
CounselReading = Literal["yes", "no", "unknown"]

#: Both sides composed into one cell key, in the party annotations' side
#: vocabulary plus ``unknown``: a row whose sides could not be read at all is
#: its own cell, never folded into ``none``.
CounselSide = Literal["both", "petitioner", "respondent", "none", "unknown"]

#: Reporting order for a :data:`CounselSide` value.
COUNSEL_SIDES: Final[tuple[CounselSide, ...]] = (
    "both",
    "petitioner",
    "respondent",
    "none",
    "unknown",
)

#: This annotation rule's version. The roster below is part of the rule: a
#: change to a span, an alias, or a member is a NEW label, never an edit.
SG_OFFICE_RULE_VERSION: Final[str] = "sg-office-v1"

#: How long a granted petition's life runs past its grant. The row carries no
#: merits-judgment date, and a grant is almost always decided within about a
#: year of it; a longer span would reach the next transition and read a future
#: Solicitor General's pre-office private appearance on a granted case as the
#: office. The cost is the tail of a case granted in the spring and decided
#: fifteen months later: a successor who signs only in that tail is caught by
#: the federal-party rule instead, or missed.
MERITS_SPAN: Final[timedelta] = timedelta(days=365)


@dataclass(frozen=True)
class OfficeSpan:
    """One span in which a roster member held a post that signs for the office.

    ``end`` is ``None`` while the member is in office. Both bounds are
    inclusive. ``source`` names where the dates come from, so a reader can
    check a boundary without reading the module history.
    """

    post: str
    start: date
    end: date | None
    source: str


@dataclass(frozen=True)
class RosterMember:
    """One person who signed for the Solicitor General's office, with their spellings."""

    name: str
    aliases: tuple[str, ...]
    spans: tuple[OfficeSpan, ...]


#: The dated roster ``sg-office-v1`` reads, retrieved 2026-09-30.
#:
#: The primary source is the Department of Justice's Office of the Solicitor
#: General pages (``justice.gov/osg``): the historical list of Solicitors
#: General and each Solicitor General's biography. Those pages give an exact day
#: for three boundaries — Verrilli sworn in 2011-06-09, Francisco sworn in
#: 2017-09-19, Sauer in office from 2025-04-04 — and years for the rest
#: (Prelogar 2021 to 2025, having served as acting Solicitor General and principal
#: deputy for nearly seven months before her confirmation; Francisco
#: 2017 to 2020; Verrilli 2011 to 2016). A span that ends or begins at a change of
#: administration takes the inauguration day from the administration calendar
#: (:data:`.party.ADMINISTRATIONS`), since these are political posts that turn
#: over with it. The remaining days (the acting-Solicitor-General handovers of
#: 2016, 2017 and 2020, and the deputies' spans) are the public record of those
#: handovers, which the OSG pages do not state; each span's ``source`` says
#: which kind of date it holds. ``docs/data-sources.md`` records the same.
#:
#: Coverage: every Solicitor General and acting Solicitor General from OT2015
#: (Verrilli, in office at its opening on 2015-10-05) to the retrieval date,
#: the principal deputies seen signing as counsel of record, and one career
#: deputy (Kneedler). The live slice's earliest filing is 2017-06-27, so the
#: pre-2017 spans exist to exclude, not to include: a Verrilli or Gershengorn
#: entry on a live-slice docket is always private practice.
#:
#: Aliases are the attorney strings the index carries for each person,
#: normalized by :func:`normalize_attorney`, plus their full-middle-name form.
#: A bare first-and-last form is listed only where no namesake is in the index:
#: "Sarah Harris" and "John Sauer" are left out for that reason.
SG_OFFICE_ROSTER: Final[tuple[RosterMember, ...]] = (
    RosterMember(
        name="Donald B. Verrilli, Jr.",
        aliases=("donald b verrilli", "donald beaton verrilli", "donald verrilli"),
        spans=(
            OfficeSpan(
                post="Solicitor General",
                start=date(2011, 6, 9),
                end=date(2016, 6, 24),
                source="start: OSG biography (sworn in); end: OSG list gives 2016, "
                "day from the public record of the handover",
            ),
        ),
    ),
    RosterMember(
        name="Ian Heath Gershengorn",
        aliases=("ian heath gershengorn", "ian h gershengorn", "ian gershengorn"),
        spans=(
            OfficeSpan(
                post="Acting Solicitor General",
                start=date(2016, 6, 24),
                end=date(2017, 1, 20),
                source="start: public record of the handover; end: inauguration",
            ),
        ),
    ),
    RosterMember(
        name="Noel J. Francisco",
        aliases=("noel john francisco", "noel j francisco", "noel francisco"),
        spans=(
            OfficeSpan(
                post="Acting Solicitor General",
                start=date(2017, 1, 20),
                end=date(2017, 3, 10),
                source="start: inauguration; end: public record of the handover",
            ),
            OfficeSpan(
                post="Solicitor General",
                start=date(2017, 9, 19),
                end=date(2020, 7, 3),
                source="start: OSG biography (sworn in); end: OSG list gives 2020, "
                "day from the public record of the handover",
            ),
        ),
    ),
    RosterMember(
        name="Jeffrey B. Wall",
        aliases=("jeffrey b wall", "jeffrey bryan wall", "jeffrey wall"),
        spans=(
            OfficeSpan(
                post="Acting Solicitor General, Principal Deputy Solicitor General",
                start=date(2017, 3, 10),
                end=date(2021, 1, 20),
                source="start: public record of the handover; end: inauguration",
            ),
        ),
    ),
    RosterMember(
        name="Elizabeth B. Prelogar",
        aliases=("elizabeth b prelogar", "elizabeth barchas prelogar", "elizabeth prelogar"),
        spans=(
            OfficeSpan(
                post="Acting Solicitor General, Principal Deputy Solicitor General, "
                "Solicitor General",
                start=date(2021, 1, 20),
                end=date(2025, 1, 20),
                source="OSG biography (2021 - 2025; acting and principal deputy for "
                "nearly seven months before confirmation); days: inaugurations",
            ),
        ),
    ),
    RosterMember(
        name="Brian H. Fletcher",
        aliases=("brian h fletcher", "brian halligan fletcher", "brian fletcher"),
        spans=(
            OfficeSpan(
                post="Principal Deputy Solicitor General, Acting Solicitor General",
                start=date(2021, 1, 20),
                end=date(2025, 1, 20),
                source="inaugurations; not on an OSG page",
            ),
        ),
    ),
    RosterMember(
        name="Sarah M. Harris",
        aliases=("sarah m harris", "sarah michelle harris"),
        spans=(
            OfficeSpan(
                post="Acting Solicitor General, Principal Deputy Solicitor General",
                start=date(2025, 1, 20),
                end=None,
                source="start: inauguration; not on an OSG page",
            ),
        ),
    ),
    RosterMember(
        name="D. John Sauer",
        aliases=("d john sauer", "dean john sauer"),
        spans=(
            OfficeSpan(
                post="Solicitor General",
                start=date(2025, 4, 4),
                end=None,
                source="OSG staff profile (became Solicitor General on April 4, 2025)",
            ),
        ),
    ),
    RosterMember(
        name="Hashim M. Mooppan",
        aliases=("hashim m mooppan", "hashim mooppan"),
        spans=(
            OfficeSpan(
                post="Principal Deputy Solicitor General",
                start=date(2025, 4, 4),
                end=None,
                source="start: the Solicitor General's arrival, public record; not on an OSG page",
            ),
        ),
    ),
    RosterMember(
        name="Edwin S. Kneedler",
        aliases=("edwin s kneedler", "edwin smiley kneedler", "edwin kneedler"),
        spans=(
            OfficeSpan(
                post="Deputy Solicitor General (career)",
                start=date(2015, 10, 5),
                end=None,
                source="career deputy throughout the roster's coverage; start is "
                "the coverage floor (OT2015's opening), not an appointment",
            ),
        ),
    ),
)

# The suffixes a normalized attorney name drops: a "Jr." or "III" is part of
# how a name is written, not of who it names.
_NAME_SUFFIXES: Final[frozenset[str]] = frozenset({"jr", "sr", "ii", "iii", "iv", "esq", "esquire"})


def normalize_attorney(name: str) -> str:
    """An attorney string folded to the form the roster's aliases are written in.

    HTML entities decoded, accents folded to ASCII, lower-cased, punctuation
    to spaces, whitespace collapsed, and a trailing generational or ``Esq.``
    suffix dropped. Total: an empty string normalizes to an empty string.
    """
    folded = unicodedata.normalize("NFKD", html.unescape(name))
    ascii_only = folded.encode("ascii", "ignore").decode().lower()
    tokens = re.sub(r"[^a-z0-9 ]", " ", ascii_only).split()
    return " ".join(token for token in tokens if token not in _NAME_SUFFIXES)


def _alias_index(roster: Iterable[RosterMember]) -> Mapping[str, RosterMember]:
    """Alias → member, refusing an alias two members share (it would name neither)."""
    index: dict[str, RosterMember] = {}
    for member in roster:
        for alias in member.aliases:
            if alias != normalize_attorney(alias):
                raise ValueError(f"roster alias {alias!r} is not in normalized form")
            if alias in index:
                raise ValueError(f"roster alias {alias!r} names two members")
            index[alias] = member
    return MappingProxyType(index)


_ROSTER_BY_ALIAS: Final[Mapping[str, RosterMember]] = _alias_index(SG_OFFICE_ROSTER)

# The generic federal party strings the counsel blocks carry and no caption
# rule reads: "Federal Respondents", "Federal Parties", "federal petitioner".
_GENERIC_FEDERAL_RE: Final = re.compile(
    r"^\s*federal\s+(?:respondents?|petitioners?|part(?:y|ies))\b", re.IGNORECASE
)
_UNITED_STATES_RE: Final = re.compile(
    r"^\s*(?:the\s+)?united\s+states(?:\s+of\s+america)?\s*[.,]?\s*(?:$|,?\s*et\s+al)",
    re.IGNORECASE,
)


def _federal_party(party: str) -> bool:
    """Whether a counsel entry's party string reads as the federal government.

    party-v2's class predicate (:func:`.party.classify_party_v2`), plus the two
    shapes a counsel block carries that a caption half does not: the bare
    "United States" with an ``et al.`` tail, and the generic "Federal
    Respondents". HTML entities are decoded first, as the blocks carry them.
    """
    text = html.unescape(party)
    return (
        classify_party_v2(text) == "federal"
        or bool(_UNITED_STATES_RE.search(text))
        or bool(_GENERIC_FEDERAL_RE.search(text))
    )


@dataclass(frozen=True)
class DocketLife:
    """The span a docket was live, from its own dates.

    ``end`` is ``None`` for a docket still live (open-ended) and for a resolved
    docket that stores no closing date; ``closed`` tells the two apart, since
    the first overlaps every later span and the second cannot be placed.
    """

    start: date | None
    end: date | None
    closed: bool = False


def docket_life(row: corpus.CorpusRow, moment: date | None) -> DocketLife:
    """The row's life: filing to resolution, capped at the cut's ``moment``.

    ``start`` is the filing date, or the earliest stored resolution date where
    the row carries none. ``end`` is ``date_decided`` or the cert denial date,
    whichever is later; a granted row with neither runs :data:`MERITS_SPAN` past
    its grant; a pending row is open-ended. A resolved row that stores none of
    those dates has an unknown end (``closed`` with ``end`` ``None``), which no
    ``moment`` stands in for. A ``moment`` otherwise caps ``end`` (a span
    starting after the cut had not started at it).
    """
    resolutions = [d for d in (row.date_cert_granted, row.date_cert_denied, row.date_decided) if d]
    start = row.date_filed or (min(resolutions) if resolutions else None)
    closing = [d for d in (row.date_decided, row.date_cert_denied) if d]
    end: date | None
    if closing:
        end = max(closing)
    elif row.date_cert_granted is not None:
        end = row.date_cert_granted + MERITS_SPAN
    elif row.disposition is not None:
        return DocketLife(start=start, end=None, closed=True)
    else:
        end = None
    if moment is not None and (end is None or end > moment):
        end = moment
    return DocketLife(start=start, end=end)


#: How one roster name on one docket reads under the dated spans.
EntryReading = Literal["office", "private", "undated"]

#: The counsel roles the annotation reads. ``other`` is left out on purpose
#: (module docstring): it is a grant oracle on a decided docket.
_READ_ROLES: Final[frozenset[corpus.CounselRole]] = frozenset(
    {corpus.CounselRole.petitioner, corpus.CounselRole.respondent}
)


def _read_entry(member: RosterMember, party: str, life: DocketLife) -> EntryReading:
    """One roster name on one docket: the office, private practice, or undatable.

    The office where one of the member's spans overlaps the docket's life; the
    office too where a span began after the life ended — a successor's late
    write, or, under a cut, a name the list gained after it — but only on a
    federal party; private practice otherwise, including every span that ended
    before the docket was filed. A resolved docket with no closing date is
    placed only where a span covers its filing; a span opening after the
    filing cannot be told apart from a future appearance there, so it reads
    undated.
    """
    if life.start is None:
        return "undated"
    successor = False
    unplaced = False
    for span in member.spans:
        if span.end is not None and span.end < life.start:
            continue  # left office before the docket was filed: never the office
        if span.start <= life.start:
            return "office"  # in office at the filing
        if life.closed and life.end is None:
            unplaced = True  # opened after the filing; the docket's end is unknown
            continue
        if life.end is None or span.start <= life.end:
            return "office"
        successor = True  # took office after the life ended (or after the cut)
    if unplaced:
        return "undated"
    return "office" if successor and _federal_party(party) else "private"


@dataclass(frozen=True)
class CounselAnnotations:
    """One row's counsel annotation under one rule version, self-describing.

    ``petitioner`` and ``respondent`` are the per-side readings; ``side`` is
    the two composed into one cell key. ``private_practice`` counts the roster
    names the dated spans set aside on the two sides — the entries an undated
    roster would have read as the office.
    """

    rule_version: str
    petitioner: CounselReading
    respondent: CounselReading
    side: CounselSide
    private_practice: int


def _compose(petitioner: CounselReading, respondent: CounselReading) -> CounselSide:
    """Compose two side readings into one :data:`CounselSide`."""
    if petitioner == "yes" and respondent == "yes":
        return "both"
    if petitioner == "yes":
        return "petitioner"
    if respondent == "yes":
        return "respondent"
    if "unknown" in (petitioner, respondent):
        return "unknown"
    return "none"


def sg_office_annotations(row: corpus.CorpusRow, moment: date | None) -> CounselAnnotations:
    """The ``sg-office-v1`` annotation of ``row``, read as of the cut's ``moment``.

    A side reads ``yes`` where one of its entries names a roster member the
    dated spans place in the office on this docket (module docstring for the
    rule), ``unknown`` where the row carries no petitioner or respondent counsel
    at all — the index gap, not an absence of counsel — or where a roster name
    on it cannot be dated, and ``no`` otherwise. ``other`` entries are never
    read. ``moment`` is the cut's ``through`` date, or ``None`` for the whole
    blob. Pure and total: no I/O, and no entry shape raises.
    """
    life = docket_life(row, moment)
    readings: dict[str, CounselReading] = {"petitioner": "no", "respondent": "no"}
    sided = [entry for entry in row.counsel if entry.role in _READ_ROLES]
    private = 0
    for entry in sided:
        member = _ROSTER_BY_ALIAS.get(normalize_attorney(entry.attorney or ""))
        if member is None:
            continue
        role = entry.role.value
        reading = _read_entry(member, entry.party, life)
        if reading == "office":
            readings[role] = "yes"
        elif reading == "undated" and readings[role] == "no":
            readings[role] = "unknown"
        elif reading == "private":
            private += 1
    if not sided:
        readings = {"petitioner": "unknown", "respondent": "unknown"}
    petitioner, respondent = readings["petitioner"], readings["respondent"]
    return CounselAnnotations(
        rule_version=SG_OFFICE_RULE_VERSION,
        petitioner=petitioner,
        respondent=respondent,
        side=_compose(petitioner, respondent),
        private_practice=private,
    )


#: Every registered counsel annotation rule, keyed by version label. Added to,
#: never edited: a cut names the rule it ran under.
COUNSEL_RULES: Final[
    Mapping[str, Callable[[corpus.CorpusRow, date | None], CounselAnnotations]]
] = MappingProxyType({SG_OFFICE_RULE_VERSION: sg_office_annotations})


def counsel_rule(
    rule_version: str,
) -> Callable[[corpus.CorpusRow, date | None], CounselAnnotations]:
    """The registered counsel annotator for ``rule_version``; :class:`KeyError` if none."""
    return COUNSEL_RULES[rule_version]
