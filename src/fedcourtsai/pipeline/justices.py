"""The Court's roster: one surname spelling shared by every vote surface.

The normalization contract the SCDB entry in ``docs/data-sources.md`` decides:
justice names normalize to the **entry-printed surnames** the docket recital
parser (:func:`fedcourtsai.pipeline.judgment.opinion_author`) returns, never to
a source's own naming variables — so a single spelling serves the docket-derived
authorship recital and any imported vote list, and a consumer never has to know
which surface a name came from.

Two facts this module is the single home for:

- **The SCDB spelling map.** :data:`SCDB_JUSTICE_SURNAMES` carries every
  ``justiceName`` value in the database's modern (1946-) span — the Vinson-court
  bench onward, holdover appointees included — onto its entry-printed surname,
  spellings as the SCDB online codebook's *Justice Name* page gives them. The
  map is deliberately **many-to-one** (``RHJackson`` and ``KBJackson`` both
  print as "Jackson"): the surname is the published spelling and the *Term*
  disambiguates, which the import's docket-number-plus-Term join already
  carries — and no two same-surname Justices sit in one Term anywhere in this
  span (the Jacksons are separated by seven decades), so the join can never
  face a surname it cannot settle. A new appointment adds one row here and
  nowhere else.
- **Which surnames span more than one token.** Every modern-span surname is a
  single space-free token (a test pins this); the Court's one compound surname
  in its whole history is Van Devanter's, so :data:`COMPOUND_SURNAMES` carries
  it defensively — no current source reaches past the modern span, and the
  recital parser resolving against this set is what keeps it total if one ever
  does — and the parser resolves a multi-token capture against the roster
  rather than truncating to the final token.
- **Who sat when.** :data:`SERVICE` carries each Justice's judicial oath and
  end of service, as the Court's own *Members of the Supreme Court* page prints
  them, for every Justice who served on or after :data:`SERVICE_FLOOR`. A vote
  source that credits a Justice by silence — the syllabus lineup grammar does,
  under the Court's list-only-where-fewer-than-all convention — needs the bench
  a decision was actually made by, and :func:`bench_on` and
  :func:`seated_after` are that bench.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Final

#: SCDB ``justiceName`` -> entry-printed surname, over the modern (1946-) span.
SCDB_JUSTICE_SURNAMES: Final[Mapping[str, str]] = MappingProxyType(
    {
        # The Vinson court's holdover appointees.
        "HLBlack": "Black",
        "SFReed": "Reed",
        "FFrankfurter": "Frankfurter",
        "WODouglas": "Douglas",
        "FMurphy": "Murphy",
        "RHJackson": "Jackson",
        "WBRutledge": "Rutledge",
        "HHBurton": "Burton",
        # Vinson through the present bench, in appointment order.
        "FMVinson": "Vinson",
        "TCClark": "Clark",
        "SMinton": "Minton",
        "EWarren": "Warren",
        "JHarlan2": "Harlan",
        "WJBrennan": "Brennan",
        "CEWhittaker": "Whittaker",
        "PStewart": "Stewart",
        "BRWhite": "White",
        "AJGoldberg": "Goldberg",
        "AFortas": "Fortas",
        "TMarshall": "Marshall",
        "WEBurger": "Burger",
        "HABlackmun": "Blackmun",
        "LFPowell": "Powell",
        "WHRehnquist": "Rehnquist",
        "JPStevens": "Stevens",
        "SDOConnor": "O'Connor",
        "AScalia": "Scalia",
        "AMKennedy": "Kennedy",
        "DHSouter": "Souter",
        "CThomas": "Thomas",
        "RBGinsburg": "Ginsburg",
        "SGBreyer": "Breyer",
        "JGRoberts": "Roberts",
        "SAAlito": "Alito",
        "SSotomayor": "Sotomayor",
        "EKagan": "Kagan",
        "NMGorsuch": "Gorsuch",
        "BMKavanaugh": "Kavanaugh",
        "ACBarrett": "Barrett",
        "KBJackson": "Jackson",
    }
)

#: Every entry-printed surname the modern span can produce. A membership set,
#: not a reverse map: two Justices may print the same surname, so the reverse
#: direction needs the Term and belongs to the import's join, not to a lookup.
ENTRY_SURNAMES: Final[frozenset[str]] = frozenset(SCDB_JUSTICE_SURNAMES.values())

#: The surnames that span more than one token, over the Court's whole history —
#: what keeps the recital parser total where a vote source reaches past the
#: modern span. Exactly one exists.
COMPOUND_SURNAMES: Final[frozenset[str]] = frozenset({"Van Devanter"})

#: Everything the recital parser may resolve a capture against.
KNOWN_SURNAMES: Final[frozenset[str]] = ENTRY_SURNAMES | COMPOUND_SURNAMES

# Casefolded index for the recital parser: docket entries print surnames in
# whatever case the order list used (all-caps included), so membership is
# case-blind while the resolved value is always the roster's own spelling —
# without this, an all-caps compound surname would split and an all-caps
# ordinary one would pass through un-normalized.
_SURNAMES_BY_FOLD: Final[Mapping[str, str]] = MappingProxyType(
    {surname.casefold(): surname for surname in KNOWN_SURNAMES}
)


def resolve_surname(candidate: str) -> str | None:
    """The roster's spelling for a printed surname, however the entry cased it.

    ``None`` for a name the roster does not carry — the caller decides its own
    fallback, because "unknown surname" means different things to a best-effort
    recital parse (keep the token) and to an import (refuse the row).
    """
    return _SURNAMES_BY_FOLD.get(candidate.casefold())


def normalize_scdb_justice(justice_name: str) -> str | None:
    """The entry-printed surname for one SCDB ``justiceName`` value.

    ``None`` for a spelling the map does not carry — an import refuses or flags
    an unknown name rather than guessing, because a guessed surname would be
    indistinguishable from a normalized one everywhere downstream.
    """
    return SCDB_JUSTICE_SURNAMES.get(justice_name)


@dataclass(frozen=True)
class Service:
    """One Justice's time on the Court: oath through last day of service.

    ``joined`` is the date the judicial oath was taken; ``left`` the date
    service terminated (death, retirement, resignation), inclusive, and
    ``None`` for a sitting Justice. Dates as the Court's *Members of the
    Supreme Court* page prints them.
    """

    justice: str
    joined: date
    left: date | None = None


#: The earliest decision date :func:`bench_on` answers for. The vote channel's
#: scope is merits decisions from October Term 2016 on, and :data:`SERVICE`
#: carries every Justice who served on or after this date — no earlier.
SERVICE_FLOOR: Final = date(2016, 10, 1)

#: Every Justice who served on or after :data:`SERVICE_FLOOR`, by seniority of
#: oath. A new appointment adds one row, and a departure fills one ``left``.
SERVICE: Final[tuple[Service, ...]] = (
    Service("Kennedy", date(1988, 2, 18), date(2018, 7, 31)),
    Service("Thomas", date(1991, 10, 23)),
    Service("Ginsburg", date(1993, 8, 10), date(2020, 9, 18)),
    Service("Breyer", date(1994, 8, 3), date(2022, 6, 30)),
    Service("Roberts", date(2005, 9, 29)),
    Service("Alito", date(2006, 1, 31)),
    Service("Sotomayor", date(2009, 8, 8)),
    Service("Kagan", date(2010, 8, 7)),
    Service("Gorsuch", date(2017, 4, 10)),
    Service("Kavanaugh", date(2018, 10, 6)),
    Service("Barrett", date(2020, 10, 27)),
    Service("Jackson", date(2022, 6, 30)),
)


def bench_on(day: date) -> tuple[str, ...]:
    """The Justices who could have decided a case on ``day``, oldest oath first.

    A Justice is on the bench from the day **after** the oath through the last
    day of service, inclusive. The oath day is excluded because the Court's
    one same-day handover in the span is exactly that shape: on 2022-06-30
    Justice Breyer's retirement took effect at noon and Justice Jackson took
    the oath after the day's opinions had been announced, so both of them are
    in service that day and only Breyer decided anything. Counting the oath day
    would seat ten.

    Raises ``ValueError`` before :data:`SERVICE_FLOOR`, where the roster is not
    carried, so an earlier decision is refused rather than read against a
    bench missing its departed members.
    """
    if day < SERVICE_FLOOR:
        raise ValueError(f"no bench roster before {SERVICE_FLOOR.isoformat()}: {day.isoformat()}")
    return tuple(s.justice for s in SERVICE if s.joined < day and (s.left is None or day <= s.left))


def seated_after(argued: date, bench: tuple[str, ...]) -> tuple[str, ...]:
    """The Justices of ``bench`` who took the oath after ``argued``.

    A Justice not yet seated when a case was argued did not hear it, and in
    practice takes no part; whether the source says so is the reading's
    question, not this roster's (``pipeline.syllabus_lineup``).
    """
    joined = {s.justice: s.joined for s in SERVICE}
    return tuple(name for name in bench if joined[name] > argued)
