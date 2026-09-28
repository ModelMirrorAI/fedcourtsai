"""The conventional short form of a SCOTUS caption, or ``None`` where it is not certain.

Display-only: the big-case board publishes it beside the full caption so a row
can be scanned on a phone (``metrics/README.md``). Nothing predicts, evaluates,
or scores on it, and nothing reads it back.

The rule is deterministic and deliberately conservative, because the two ways it
can fail are not equally bad. A ``None`` costs the reader nothing — the site
falls back to the full caption — while a wrong short form ("Petersen v. Vota"
for a party that is an organisation) publishes an error under the Court's own
case name. So every branch below that is not sure returns ``None``, and where
a party could be read either as a person or as an organisation the rule reads
it as an organisation, whose short form is its name rather than one word of it.

The rule, applied to each side of the single `` v. `` (an ``In re`` caption has
one side and renders ``In re <party>``):

1. **The first-named party.** The text before the side's first comma, keeping a
   following bare corporate-form segment (``, Inc.``, ``, LLC``) as evidence the
   party is an organisation. Everything after — ``et al.``, office titles,
   ``Individually and as …`` — is description, not the name.
2. **The sovereign.** ``United States`` and a state or territory name are
   already their short form.
3. **An organisation** — a corporate form, an institutional noun (``County``,
   ``Department``, ``Association`` …), a ``dba`` alias, or any name that is not
   person-shaped — renders as its name, with a leading ``The``, a parenthetical
   and trailing corporate forms dropped; a federal agency with an acronym the
   Court's own case names use renders as that acronym. A name still longer than
   :data:`MAX_ORGANISATION_WORDS` has no short form this rule can find — the
   conventional one is an acronym or a noun phrase only a reader knows — so it
   is ``None``.
4. **A person** — two to five capitalised words or initials — renders as the
   surname, the last word (``St.`` joins it). A name of initials only
   (``N. R.``, a minor) renders whole. A surname particle (``da``, ``van`` …)
   or a name longer than :data:`MAX_PERSON_WORDS` makes the surname's extent
   unknowable from the caption, so it is ``None``.

Either side ``None`` makes the whole short caption ``None``.
"""

from __future__ import annotations

import re
from typing import Final

from .pipeline.caption import STATE_NAMES

#: Organisation names longer than this have no short form the rule can derive.
MAX_ORGANISATION_WORDS: Final = 6

#: A person's name longer than this may end in a two-word surname ("Montoya
#: Palacios") or a maiden name kept as a middle one, and the caption cannot say
#: which, so it has no short form.
MAX_PERSON_WORDS: Final = 3

#: Federal agencies whose acronym the Court's own case names use. A general
#: vocabulary, not a per-case answer: it names agencies, never a litigant's
#: particular short form.
AGENCY_ACRONYMS: Final[dict[str, str]] = {
    "Consumer Financial Protection Bureau": "CFPB",
    "Environmental Protection Agency": "EPA",
    "Equal Employment Opportunity Commission": "EEOC",
    "Federal Bureau of Investigation": "FBI",
    "Federal Communications Commission": "FCC",
    "Federal Election Commission": "FEC",
    "Federal Energy Regulatory Commission": "FERC",
    "Federal Trade Commission": "FTC",
    "Food and Drug Administration": "FDA",
    "National Labor Relations Board": "NLRB",
    "Securities and Exchange Commission": "SEC",
}

#: Corporate forms: a segment or trailing word that marks a business name and is
#: dropped from its short form.
_CORPORATE_FORMS: Final = frozenset(
    {
        "Co.",
        "Company",
        "Corp.",
        "Corporation",
        "GmbH",
        "Inc",
        "Inc.",
        "Incorporated",
        "L.L.C.",
        "L.P.",
        "LLC",
        "LLP",
        "LP",
        "Ltd",
        "Ltd.",
        "N.A.",
        "P.L.L.C.",
        "PLC",
        "PLLC",
        "S.A.",
    }
)

#: Words that make a name an institution rather than a person. Erring towards an
#: organisation is the safe direction: its short form is the whole name.
_INSTITUTION_WORDS: Final = frozenset(
    {
        "Administration",
        "Agency",
        "Alliance",
        "Association",
        "Associates",
        "Bank",
        "Bar",
        "Board",
        "Bureau",
        "Center",
        "Chapel",
        "Church",
        "City",
        "Coalition",
        "College",
        "Colony",
        "Commission",
        "Committee",
        "Congress",
        "Council",
        "County",
        "Court",
        "Department",
        "District",
        "Foundation",
        "Fund",
        "Group",
        "Health",
        "Hospital",
        "Industries",
        "Institute",
        "Insurance",
        "Markets",
        "Ministries",
        "Nation",
        "Office",
        "Parish",
        "Partners",
        "Railroad",
        "Railway",
        "Regents",
        "School",
        "Schools",
        "Service",
        "Services",
        "Society",
        "Technologies",
        "Technology",
        "Trust",
        "Tribe",
        "Tribes",
        "Union",
        "University",
        "Village",
    }
    | _CORPORATE_FORMS
)

#: Lower-case surname particles: a surname's extent is unknowable past one.
_PARTICLES: Final = frozenset(
    {"da", "de", "del", "della", "der", "di", "dos", "du", "la", "le", "van", "von", "y"}
)

#: State names that are also given names, so a person may start with one.
_GIVEN_NAME_STATES: Final = frozenset({"Georgia", "Virginia"})

#: Federal courts named with their seat: the court's name is the head, before ``for``.
_FEDERAL_COURT_HEADS: Final = ("United States District Court", "United States Court of Appeals")

#: Person-name suffixes, which arrive as their own comma segment.
_NAME_SUFFIXES: Final = frozenset({"Jr.", "Sr.", "II", "III", "IV"})

_INITIALS_RE: Final = re.compile(r"^(?:[A-Z]\.)+$")
# An apostrophe may be typed or typographic (U+2019).
_NAME_WORD_RE: Final = re.compile("^[A-Z][A-Za-z'\u2019\\-]*[a-z][A-Za-z'\u2019\\-]*$")
_IN_RE_RE: Final = re.compile(r"^In\s+re:?\s+", re.IGNORECASE)
_PARENTHETICAL_RE: Final = re.compile(r"\s*\([^)]*\)")
_SINGLE_WORD_STATES: Final = frozenset(name for name in STATE_NAMES if " " not in name)


def short_caption(caption: str | None) -> str | None:
    """The conventional short form of ``caption``, or ``None`` where the rule is not sure.

    >>> short_caption("Donald J. Trump, President of the United States, et al. v. California")
    'Trump v. California'
    """
    text = " ".join((caption or "").split())
    in_re = _IN_RE_RE.match(text)
    if in_re is not None:
        return _short_in_re(text[in_re.end() :])
    sides = text.split(" v. ")
    if len(sides) != 2:
        return None
    left, right = (_short_party(side) for side in sides)
    if left is None or right is None:
        return None
    return f"{left} v. {right}"


def _short_in_re(rest: str) -> str | None:
    """``In re <party>`` for a one-sided caption, or ``None``."""
    party = _short_party(rest) if rest and " v. " not in rest else None
    return f"In re {party}" if party is not None else None


def _short_party(side: str) -> str | None:
    """The short form of one side's first-named party, or ``None``."""
    segments = [segment.strip() for segment in side.split(",")]
    name = _PARENTHETICAL_RE.sub("", segments[0]).strip()
    corporate = False
    for segment in segments[1:]:
        words = segment.split()
        if not words or segment in _NAME_SUFFIXES:
            continue
        if words[0] in _CORPORATE_FORMS:
            corporate = True
            continue
        # Past the corporate-form segments the side describes the party rather
        # than naming it; only a `dba` alias still says what kind of party it is.
        corporate = corporate or words[0] == "dba"
        break
    if name.startswith("The "):
        name = name[len("The ") :]
    if not name:
        return None
    if name in ("United States", "United States of America"):
        return "United States"
    if name in STATE_NAMES:
        return name
    words = name.split()
    if corporate or any(word in _INSTITUTION_WORDS for word in words) or not _person_shaped(words):
        return _short_organisation(name)
    return _surname(words)


def _person_shaped(words: list[str]) -> bool:
    """Whether ``words`` can be a person's name: two to five names or initials."""
    if not 2 <= len(words) <= 5:
        return False
    first, last = words[0], words[-1]
    if not _INITIALS_RE.match(first) and len(first) < 3:
        return False
    if first in _SINGLE_WORD_STATES and first not in _GIVEN_NAME_STATES:
        return False
    if last in _SINGLE_WORD_STATES:
        return False
    return all(
        _INITIALS_RE.match(word) or _NAME_WORD_RE.match(word) or word in _PARTICLES or word == "St."
        for word in words
    )


def _surname(words: list[str]) -> str | None:
    """A person's surname, or their initials where the name is initials only."""
    if all(_INITIALS_RE.match(word) for word in words):
        return " ".join(words)
    if len(words) > MAX_PERSON_WORDS:
        return None
    last = words[-1]
    if _INITIALS_RE.match(last) or last == "St.":
        return None
    previous = words[-2]
    if previous in _PARTICLES:
        return None
    if previous == "St.":
        return f"St. {last}"
    return last


def _short_organisation(name: str) -> str | None:
    """An organisation's short form: its acronym, or its name trimmed of form words."""
    for head in _FEDERAL_COURT_HEADS:
        if name.startswith(f"{head} "):
            return head
    if name in AGENCY_ACRONYMS:
        return AGENCY_ACRONYMS[name]
    words = name.split()
    while len(words) > 1 and words[-1] in _CORPORATE_FORMS:
        words.pop()
    if sum(1 for word in words if word not in ("&", "-")) > MAX_ORGANISATION_WORDS:
        return None
    return " ".join(words)
