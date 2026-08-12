"""The arrival-time petitioner class: federal / state / private, off the caption.

The one party signal fixed at filing (``docs/salience.md``, the ``sal-v2``
intent): ``parties``/``counsel`` accrue over a docket's life and are
contaminated with amici, so the petitioner's *caption* — preferably the
structured ``petitioner_title`` column, else the joined ``case_name``'s
pre-`` v. `` half — is the only honest arrival-time reading of who is asking.
The class is deliberately coarse (three values) because coarseness is what
survives caption re-rendering: measured over 12,851 event-vintage/current
pairs, ~97% of caption *strings* changed while the derived class survived in
99.98%, with the residual concentrated in officer-title renderings.

The rule's ordering is load-bearing and pinned by fixtures: **state markers
are tested before federal markers**, because SCOTUS captioning style renders a
state officer as ``"<name>, Attorney General of Arizona"`` and a federal
officer as ``"<name>, Attorney General"`` — an officer title *without* a
jurisdiction qualifier is the federal convention, so testing federal first
would misfile every qualified state officer. A bare state name appearing
somewhere inside a longer petitioner (``"New York State Rifle & Pistol
Association"``) is deliberately NOT a state marker — an entity named after a
state is private, and that false-positive family is grant-enriched, which is
exactly the direction a classifier must not lean.

This module is census-grade and selection-grade: the class feeds the salience
band (a reporting dimension) everywhere, and the ``federal`` class feeds the
``sal-v2`` arrival carve-in **only after** the census computed from this
committed rule passes statistical review — no constant is frozen off any
number this file did not produce (``docs/salience.md``).
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Final, Literal

from .. import corpus
from ..schemas import (
    GRANT_FAMILY_DISPOSITIONS,
    CaptionCensus,
    CaptionCensusClass,
    CaptionCensusTerm,
)
from ..supremecourt import IFP_SERIAL_BASE, parse_scotus_docket_number

PetitionerClass = Literal["federal", "state", "private"]

#: The committed rule's version, stamped on every census this module produces.
#: A change to the rule (any fixture moving) is a NEW version and a new census
#: — the constant a selection carve-in freezes names the census it came from.
CAPTION_RULE_VERSION = "caption-v1"

#: Class labels in reporting order (strongest measured grant rate first).
PETITIONER_CLASSES: Final[tuple[PetitionerClass, ...]] = ("federal", "state", "private")

#: The states, DC, and the territories, as caption words. Sorted longest-first
#: at pattern-build time so "West Virginia" wins over "Virginia".
_STATE_NAMES: Final[tuple[str, ...]] = (
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
    "District of Columbia",
    "Puerto Rico",
    "Guam",
    "American Samoa",
    "Northern Mariana Islands",
    "United States Virgin Islands",
)

_STATE_ALTERNATION: Final[str] = "|".join(
    re.escape(name) for name in sorted(_STATE_NAMES, key=len, reverse=True)
)

# The sovereign itself as petitioner: "Arizona", "State of Texas",
# "Commonwealth of Kentucky", "People of Michigan" — anchored to the caption's
# start so an entity merely *named after* a state never matches.
_STATE_SOVEREIGN_RE: Final = re.compile(
    rf"^(?:(?:State|Commonwealth|People|Territory)\s+of\s+)?(?:{_STATE_ALTERNATION})\b[,;]?\s*(?:et\s+al\.?)?$",
    re.IGNORECASE,
)

# A state officer or organ: an office/officer designation followed (in the
# same caption) by a jurisdiction qualifier — "Brnovich, Attorney General of
# Arizona", "Commissioner, Pennsylvania State Police", "Texas Department of
# Criminal Justice". The qualifier is what separates this from the federal
# convention below.
_OFFICE_WORDS: Final[str] = (
    "Attorney General|Governor|Lieutenant Governor|Secretary|Commissioner|"
    "Director|Superintendent|Warden|Sheriff|Treasurer|Auditor|Comptroller|"
    "Chairman|Chair|Administrator|Executive Director|District Attorney|"
    "Prosecuting Attorney|Board|Department|Division|Bureau|Commission|Agency|"
    "Authority|Office"
)
_STATE_OFFICER_RE: Final = re.compile(
    rf"(?:{_OFFICE_WORDS})[^,;]*?(?:of\s+(?:the\s+(?:State|Commonwealth)\s+of\s+)?|,\s*)?\s*(?:{_STATE_ALTERNATION})\b"
    rf"|(?:{_STATE_ALTERNATION})\s+(?:State\s+)?(?:{_OFFICE_WORDS})",
    re.IGNORECASE,
)

# The federal sovereign or its organs: the United States itself, a federal
# agency by name or initialism, or an officer styled in the federal
# convention — an office designation with no jurisdiction qualifier
# ("Garland, Attorney General"), or one qualified "of the United States".
_FEDERAL_SOVEREIGN_RE: Final = re.compile(
    r"^United States(?:\s+of\s+America)?\b|^U\.?S\.?\b(?!\w)", re.IGNORECASE
)
_FEDERAL_MARKER_RE: Final = re.compile(
    r"\bUnited States\b"
    r"|\bSolicitor General\b"
    r"|\bFederal\s+(?:Bureau|Communications|Election|Energy|Trade|Reserve|Deposit|Housing|Maritime|Mine|Labor)\b"
    r"|\b(?:NLRB|FCC|FDA|EPA|SEC|FTC|CFPB|FERC|ICE|DHS|IRS|SSA|USDA|HHS|HUD|DOT|DOJ|ATF|DEA|FBI|CIA|NSA|OPM|GSA|SBA|TSA|USCIS|VA)\b"
    r"|\bNational Labor Relations Board\b"
    r"|\bSecurities and Exchange Commission\b"
    r"|\bEnvironmental Protection Agency\b"
    r"|\bInternal Revenue Service\b"
    r"|\bSocial Security Administration\b"
    r"|\bPostmaster General\b"
    r"|\bComptroller of the Currency\b"
    r"|\bPresident of the United States\b",
    re.IGNORECASE,
)
# The federal officer convention: "<name>, <Office>" with nothing after the
# office naming a state — matched only when the caption's tail is an office
# designation, so "Esther Virginia John" (a name) never fires.
_FEDERAL_OFFICER_RE: Final = re.compile(
    rf",\s*(?:Acting\s+)?(?:{_OFFICE_WORDS})"
    r"(?:\s+of\s+(?:the\s+)?(?:United States|Treasury|State|Defense|Labor|Education"
    r"|Energy|Commerce|Transportation|Agriculture|the Interior|Homeland Security"
    r"|Health and Human Services|Housing and Urban Development|Veterans Affairs"
    r"|Justice))?"
    r"\s*(?:,\s*et\s+al\.?)?$",
    re.IGNORECASE,
)


def classify_petitioner(title: str) -> PetitionerClass:
    """The petitioner class of one caption string.

    State markers before federal markers, by the ordering argument in the
    module docstring; anything matching neither is ``private``. Pure and
    total — an empty or unparseable caption is ``private``, never an error,
    because the census must classify every row to keep its denominator whole.
    """
    text = title.strip()
    if not text:
        return "private"
    if _STATE_SOVEREIGN_RE.search(text) or _STATE_OFFICER_RE.search(text):
        return "state"
    if (
        _FEDERAL_SOVEREIGN_RE.search(text)
        or _FEDERAL_MARKER_RE.search(text)
        or _FEDERAL_OFFICER_RE.search(text)
    ):
        return "federal"
    return "private"


def petitioner_caption(row: corpus.CorpusRow) -> str:
    """The row's best petitioner caption: the structured column, else the split.

    The pre-`` v. `` half of ``case_name`` is the fallback for rows ingested
    before ``petitioner_title`` existed; the split inherits the join's
    rendering quirks, which is exactly why the column is preferred.
    """
    if row.petitioner_title:
        return row.petitioner_title
    head, _, _ = row.case_name.partition(" v. ")
    return head.strip()


def petitioner_class(row: corpus.CorpusRow) -> PetitionerClass:
    """The row's petitioner class, off its best available caption."""
    return classify_petitioner(petitioner_caption(row))


def _scored_segment(row: corpus.CorpusRow) -> bool:
    """The salience gate's scored segment: paid modern-cert petitions.

    Mirrors ``analytics._is_scored_segment_row`` deliberately without
    importing it — ``analytics`` imports ``pipeline.salience``, which the
    ``sal-v2`` scorer's caption bands make an importer of this module, so an
    ``analytics`` import here would close a cycle. A test pins the two
    predicates equal so they cannot drift apart silently.
    """
    if not corpus.is_modern_cert(row):
        return False
    parsed = parse_scotus_docket_number(row.docket_number)
    return parsed is not None and parsed[1] < IFP_SERIAL_BASE


def caption_census(conn: corpus.ReadConnection) -> CaptionCensus:
    """The per-Term, per-class grant-family census the carve-in freezes from.

    The population frame is exactly the salience gate's scored segment — the
    live-slice, paid, modern-cert petitions (``corpus.is_live_slice`` +
    paid ``is_modern_cert``), resolved rows only, Term parseable — so a class
    rate here conditions on the same population any arrival selection would
    operate on. Deterministic and read-only: two census runs over one corpus
    pointer agree byte for byte, which is what lets a statistical review of
    this artifact license a frozen constant (``docs/salience.md``).
    """
    counts: dict[int, dict[str, list[int]]] = defaultdict(
        lambda: {c: [0, 0] for c in PETITIONER_CLASSES}
    )
    for row in corpus.iter_rows(conn, court="scotus"):
        if not corpus.is_live_slice(row) or not _scored_segment(row):
            continue
        if row.disposition is None:
            continue
        term = corpus.scotus_term_year(row.docket_number)
        if term is None:
            continue
        cell = counts[term][petitioner_class(row)]
        cell[0] += 1
        if row.disposition in GRANT_FAMILY_DISPOSITIONS:
            cell[1] += 1

    def _classes(source: dict[str, list[int]]) -> list[CaptionCensusClass]:
        return [
            CaptionCensusClass(
                petitioner_class=name,
                n=source[name][0],
                grant_family=source[name][1],
                rate=(source[name][1] / source[name][0]) if source[name][0] else None,
            )
            for name in PETITIONER_CLASSES
        ]

    pooled: dict[str, list[int]] = {c: [0, 0] for c in PETITIONER_CLASSES}
    terms: list[CaptionCensusTerm] = []
    for term in sorted(counts):
        for name in PETITIONER_CLASSES:
            pooled[name][0] += counts[term][name][0]
            pooled[name][1] += counts[term][name][1]
        terms.append(CaptionCensusTerm(term=term, classes=_classes(counts[term])))
    return CaptionCensus(
        rule_version=CAPTION_RULE_VERSION,
        terms=terms,
        pooled=_classes(pooled),
    )
