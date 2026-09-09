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
  carries. A new appointment adds one row here and nowhere else.
- **Which surnames span more than one token.** Every modern-span surname is a
  single space-free token (a test pins this), but the parser must stay correct
  over the full historical span a vote source can cover, and the Court's one
  compound surname is Van Devanter's — so :data:`COMPOUND_SURNAMES` names it,
  and the recital parser resolves a multi-token capture against this set
  rather than truncating to the final token.
"""

from __future__ import annotations

from collections.abc import Mapping
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


def normalize_scdb_justice(justice_name: str) -> str | None:
    """The entry-printed surname for one SCDB ``justiceName`` value.

    ``None`` for a spelling the map does not carry — an import refuses or flags
    an unknown name rather than guessing, because a guessed surname would be
    indistinguishable from a normalized one everywhere downstream.
    """
    return SCDB_JUSTICE_SURNAMES.get(justice_name)
