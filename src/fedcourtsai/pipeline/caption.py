"""The arrival-time petitioner class: federal / state / private, off the caption.

The one party signal fixed at filing (``docs/salience.md``, the arrival-aware
scorers' intent): ``parties``/``counsel`` accrue over a docket's life and are
contaminated with amici, so the petitioner's *caption* — preferably the
structured ``petitioner_title`` column, else the joined ``case_name``'s
pre-`` v. `` half — is the only honest arrival-time reading of who is asking.
The class is deliberately coarse (three values) because coarseness is what
survives caption re-rendering, measured two ways: over 12,851
event-vintage/current pairs at the pre-re-render corpus vintage (the event
titles have since been re-rendered to current, so that cut no longer
reproduces), ~97% of caption strings changed while this rule's class flipped
once, zero among grant-family rows; and reproducibly today, across the 815
frame rows carrying a dated snapshot, the snapshot caption differs from the
current one in 98.8% of rows while the class agrees in 815/815 — a
cross-channel rendering invariance, not temporal drift, which stays a
declared gap. Role-suffix stripping below is what makes the rule
vintage-independent.

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

The rule is **versioned like a scorer**: each version is a separate predicate
registered in :data:`CAPTION_RULES`, never an in-place widening, because a
census a selection constant was frozen from must replay under the exact
predicate that produced it. ``caption-v1`` is the predicate the ``sal-v2``
carve-in is frozen on; ``caption-v2`` is the widened read — the same three
classes, reading the federal shapes v1's patterns measurably miss (the
``Office of the United States <office>`` word order, agencies and offices
named without a ``United States`` / ``Federal`` lead, the military departments
in the officer convention, and the sovereign behind an ``In re`` caption).
Widening is one-directional by construction, because v2 *runs v1 first and
keeps any non-``private`` answer*: no caption loses a ``federal`` or ``state``
read it had under v1, so the delta between the two censuses is drawn from the
``private`` cell only and the two are comparable cell by cell.

This module is census-grade and selection-grade: the class feeds the salience
band (a reporting dimension) everywhere, and the ``federal`` class feeds an
arrival carve-in **only after** the census computed from the carve-in's own
rule version passes statistical review — no constant is frozen off any number
this file did not produce (``docs/salience.md``).
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable, Mapping
from types import MappingProxyType
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

#: The baseline rule's version, and the census default. A change to a rule
#: (any fixture moving) is a NEW version and a new census — the constant a
#: selection carve-in freezes names the census it came from.
CAPTION_RULE_VERSION = "caption-v1"

#: The widened rule's version: v1's ordering and classes, more federal shapes.
CAPTION_RULE_VERSION_V2 = "caption-v2"

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

# The caption role label ("..., Petitioner(s)" / "..., Appellant"), stripped
# before classification: event-vintage captions carry it and the tail-anchored
# patterns below would otherwise read every labeled sovereign or officer as
# private. The live channel strips it at ingest; stripping here makes the
# rule vintage-independent, which is what the measured invariance rests on.
_ROLE_SUFFIX_RE: Final = re.compile(
    r",?\s*(?:Petitioners?|Respondents?|Appellants?|Appellees?)\s*$", re.IGNORECASE
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

# Sub-national officer tails with no jurisdiction in the caption: Wardens,
# Sheriffs, Superintendents, District/Prosecuting Attorneys petitioning at
# SCOTUS are state or local officers by office, so the unqualified tail is a
# state marker, never a federal one.
_SUBNATIONAL_OFFICER_RE: Final = re.compile(
    r",\s*(?:Acting\s+|Interim\s+)?(?:Warden|Sheriff|Superintendent|"
    r"District Attorney|Prosecuting Attorney)\b[^;]*$",
    re.IGNORECASE,
)

# The federal sovereign or its organs: the United States itself, a federal
# agency by name or initialism, or an officer styled in the federal
# convention — an office designation with no jurisdiction qualifier
# ("Garland, Attorney General"), or one qualified "of the United States".
# The sovereign must BE the petitioner, not merely lead its name: "U.S. Bank"
# and "United States Soccer Federation" are private, and a qui tam caption
# ("United States ex rel. <relator>") names a private relator as the party
# actually petitioning, so it is private too — measured at a 0.091 grant rate
# against the true federal cell's ~0.64.
_FEDERAL_SOVEREIGN_RE: Final = re.compile(
    r"^(?:United States(?:\s+of\s+America)?|U\.?S\.?A?\.?)\s*(?:$|[,;])", re.IGNORECASE
)
_QUI_TAM_RE: Final = re.compile(
    r"^United States,?(?:\s+et\s+al\.?,?)?\s+ex\.?\s*rel", re.IGNORECASE
)
_FEDERAL_MARKER_RE: Final = re.compile(
    r"\bSolicitor General\b"
    r"|\bFederal\s+(?:Bureau|Communications|Election|Energy|Trade|Reserve|Deposit|Housing|Maritime|Mine|Labor)\b"
    r"|\b(?:NLRB|FCC|FDA|EPA|SEC|FTC|CFPB|FERC|ICE|DHS|IRS|SSA|USDA|HHS|HUD|DOT|DOJ|ATF|DEA|FBI|CIA|NSA|OPM|GSA|SBA|TSA|USCIS|VA)\b"
    r"|\bNational Labor Relations Board\b"
    r"|\bSecurities and Exchange Commission\b"
    r"|\bEnvironmental Protection Agency\b"
    r"|\bInternal Revenue Service\b"
    r"|\bSocial Security Administration\b"
    r"|\bPostmaster General\b"
    r"|\bComptroller of the Currency\b"
    r"|\bCommissioner of Internal Revenue\b"
    r"|\bFood and Drug Administration\b"
    r"|\bConsumer Financial Protection Bureau\b"
    r"|\bUnited States\s+(?:Department|Postal Service|Forest Service|Patent|"
    r"Citizenship|Fish and Wildlife|Army Corps|Agency|Office|Court)\b"
    r"|^(?:United States\s+)?Department of\s+(?:Justice|State|Education|Defense|"
    r"Energy|Commerce|Labor|Transportation|Agriculture|the Interior|the Treasury|"
    r"Homeland Security|Health and Human Services|"
    r"Housing and Urban Development|Veterans Affairs)\b"
    r"|\bAttorney General of the United States\b"
    r"|\bPresident of the United States\b",
    re.IGNORECASE,
)
# The federal officer convention: "<name>, <Office>" with nothing after the
# office naming a state — matched only when the caption's tail is an office
# designation, so "Esther Virginia John" (a name) never fires. The office
# vocabulary here is the FEDERAL-plausible subset: a Warden, Sheriff,
# Superintendent, or District Attorney petitioning at SCOTUS is a state or
# local officer whatever the caption omits (measured: 29 unqualified such
# tails, grant rate 0.103 — the state profile, not the federal one), so
# those tails classify state below rather than federal here.
_FEDERAL_OFFICE_WORDS: Final[str] = (
    "Attorney General|Secretary|Commissioner|Director|Administrator|"
    "Chairman|Chair|Postmaster General|Solicitor General|Comptroller"
)
_FEDERAL_OFFICER_RE: Final = re.compile(
    rf",\s*(?:Acting\s+)?(?:{_FEDERAL_OFFICE_WORDS})"
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
    text = _ROLE_SUFFIX_RE.sub("", title.strip()).strip()
    if not text:
        return "private"
    if _QUI_TAM_RE.search(text):
        return "private"
    if (
        _STATE_SOVEREIGN_RE.search(text)
        or _STATE_OFFICER_RE.search(text)
        or _SUBNATIONAL_OFFICER_RE.search(text)
    ):
        return "state"
    if (
        _FEDERAL_SOVEREIGN_RE.search(text)
        or _FEDERAL_MARKER_RE.search(text)
        or _FEDERAL_OFFICER_RE.search(text)
    ):
        return "federal"
    return "private"


# --- caption-v2: the widened federal read -------------------------------------
#
# v1's constants above are frozen and untouched — every pattern here is
# additional, and v1's whole read runs first, so `caption-v1` replays byte for
# byte and the two rules can be censused side by side. Five shapes, each one a
# family the census frame measures v1 missing rather than a guess about what a
# caption might say:
#
# - the "Office of the United States <office>" word order (v1's federal marker
#   reads only the "United States Office" order), and the United States
#   Trustee, whom v1's list of "United States <organ>" names omits;
# - agencies and federal offices whose caption name leads with neither
#   "United States" nor "Federal";
# - the spelled-out form of an agency v1 carries only as an initialism;
# - the military departments as an officer's qualifier, and the deputy /
#   under / assistant ranks of the federal officer convention;
# - the sovereign behind an "In re" caption, which v1's start-anchored
#   sovereign pattern cannot see.
#
# The "In re" prefix is granted to the qui tam pattern in the same breath and
# not only to the sovereign: the relator, not the United States, is the party
# petitioning whatever prefix the caption carries, so qui tam keeps its
# precedence over the widened federal patterns below.
#
# Inside each shape the agency vocabulary is deliberately wider than the frame
# exercises — the carve-in these rules feed selects at ARRIVAL, where the
# caption that matters has not been filed yet, so a name of the same shape is
# listed whether or not a historical petition carries it. A pattern matching no
# frame row moves no census cell, so the widening the census measures is
# exactly the set of captions the fixtures record as measured.
_IN_RE_PREFIX: Final[str] = r"(?:In\s+re:?\s+)?"

_FEDERAL_SOVEREIGN_V2_RE: Final = re.compile(
    rf"^{_IN_RE_PREFIX}(?:United States(?:\s+of\s+America)?|U\.?S\.?A?\.?)\s*(?:$|[,;])",
    re.IGNORECASE,
)
_QUI_TAM_V2_RE: Final = re.compile(
    rf"^{_IN_RE_PREFIX}United States,?(?:\s+et\s+al\.?,?)?\s+ex\.?\s*rel", re.IGNORECASE
)
_FEDERAL_MARKER_V2_RE: Final = re.compile(
    r"\bOffice of the United States\b"
    r"|\bUnited States Trustee\b"
    r"|\bExecutive Office for Immigration Review\b"
    r"|\bGeneral Services Administration\b"
    r"|\bNuclear Regulatory Commission\b"
    r"|\bAgency for International Development\b"
    r"|\bImmigration and Customs Enforcement\b"
    r"|\bCustoms and Border Protection\b"
    r"|\bPatent and Trademark Office\b"
    r"|\bFederal Aviation Administration\b"
    r"|\bSurface Transportation Board\b"
    r"|\bMerit Systems Protection Board\b"
    r"|\bEqual Employment Opportunity Commission\b"
    r"|\bDepartment of the (?:Air Force|Army|Navy)\b"
    r"|\b(?:Secretary|Under Secretary|Deputy Secretary)\s+of\s+the\s+(?:Air Force|Army|Navy)\b",
    re.IGNORECASE,
)
# The officer tails v1's pattern misses: a military department as the
# qualifier, and the deputy / under / assistant ranks of the same offices. v1's
# own officer pattern still runs beside this one — it carries the civilian
# department qualifiers this supplement deliberately does not repeat.
_FEDERAL_OFFICER_V2_RE: Final = re.compile(
    rf",\s*(?:Acting\s+|Deputy\s+|Under\s+|Assistant\s+)*(?:{_FEDERAL_OFFICE_WORDS})"
    r"(?:\s+of\s+(?:the\s+)?(?:Air Force|Army|Navy))?"
    r"\s*(?:,\s*et\s+al\.?)?$",
    re.IGNORECASE,
)


def classify_petitioner_v2(title: str) -> PetitionerClass:
    """The ``caption-v2`` petitioner class of one caption string.

    v1's read runs first and is **final wherever it is not** ``private``, which
    is what makes the widening one-directional by construction rather than by
    inspection: no caption can lose a ``federal`` or ``state`` read it had
    under v1, so the delta between the two censuses is drawn from the
    ``private`` cell and nowhere else, and the two are comparable cell by cell.
    Only a v1 ``private`` caption reaches the widened patterns — where qui tam
    still runs before them, an ``In re``-prefixed relator caption included,
    because the prefix says nothing about who is petitioning. Pure and total,
    like v1: an empty or unparseable caption is ``private``, never an error.

    A v1 ``private`` caption cannot become ``state`` here, and does not need a
    second state pass to prove it: v2 adds no state pattern, so anything the
    state block would catch v1 already caught.
    """
    baseline = classify_petitioner(title)
    if baseline != "private":
        return baseline
    text = _ROLE_SUFFIX_RE.sub("", title.strip()).strip()
    if not text or _QUI_TAM_V2_RE.search(text):
        return "private"
    if (
        _FEDERAL_SOVEREIGN_V2_RE.search(text)
        or _FEDERAL_MARKER_V2_RE.search(text)
        or _FEDERAL_OFFICER_V2_RE.search(text)
    ):
        return "federal"
    return "private"


#: Every registered caption rule, keyed by version label. A rule is only ever
#: added here — never edited and never removed — because a frozen selection
#: constant names the census it came from, and that census replays only against
#: the predicate that produced it.
CAPTION_RULES: Final[Mapping[str, Callable[[str], PetitionerClass]]] = MappingProxyType(
    {
        CAPTION_RULE_VERSION: classify_petitioner,
        CAPTION_RULE_VERSION_V2: classify_petitioner_v2,
    }
)


def caption_rule(rule_version: str) -> Callable[[str], PetitionerClass]:
    """The registered predicate for ``rule_version``.

    Raises :class:`KeyError` for an unregistered label rather than falling back
    to the baseline rule: a caller asking for a rule this process cannot
    produce wants an error, not a census silently cut under a version it did
    not ask for.
    """
    return CAPTION_RULES[rule_version]


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
    """The row's ``caption-v1`` petitioner class, off its best available caption."""
    return classify_petitioner(petitioner_caption(row))


def petitioner_class_v2(row: corpus.CorpusRow) -> PetitionerClass:
    """The row's ``caption-v2`` petitioner class, off its best available caption."""
    return classify_petitioner_v2(petitioner_caption(row))


def _scored_segment(row: corpus.CorpusRow) -> bool:
    """The salience gate's scored segment: paid modern-cert petitions.

    Mirrors ``analytics._is_scored_segment_row`` deliberately without
    importing it — ``analytics`` imports ``pipeline.salience``, which the
    ``sal-v2`` scorer's caption bands make an importer of this module, so an
    ``analytics`` import here would close a cycle. A test pins the two
    predicates equal on every plain form; the one pinned divergence is an
    annotated docket number ("*** CAPITAL CASE ***"), which parses here
    through normalization — the gate's own reading — where the statpack
    cut's raw parse drops the row.
    """
    if not corpus.is_modern_cert(row):
        return False
    parsed = parse_scotus_docket_number(corpus.normalize_docket_number(row.docket_number) or "")
    return parsed is not None and parsed[1] < IFP_SERIAL_BASE


def caption_census(
    conn: corpus.ReadConnection,
    *,
    corpus_sha256: str = "",
    rule_version: str = CAPTION_RULE_VERSION,
) -> CaptionCensus:
    """The per-Term, per-class grant-family census the carve-in freezes from.

    ``rule_version`` names which registered predicate (:data:`CAPTION_RULES`)
    cuts the frame, and is stamped on the result: two rule versions census the
    same frame independently, so a widening is reviewable as a per-class,
    per-Term delta rather than as an unlabelled re-run.

    The population frame is the statpack's predictor-facing cut — live-slice,
    paid, modern-cert petitions, resolved (disposition-labeled) rows, Term
    parseable — the population whose per-band base rates anchor cells, so a
    class rate conditions on what any arrival selection would operate over.
    (The gate itself screens on the Tier-0 rules rather than this cut; the
    difference is rows the census counts that the gate would exclude, never
    the reverse.) ``pooled`` spans only the Terms whose frame carries no
    unresolved row — an in-progress Term is right-censored and its
    resolved-so-far rate is outcome-correlated, so it reports per-Term but
    never pools. Every row's ``sample_weight`` must be 1: the census counts
    raw, and a subsampled frame (a future re-walk vintage) must fail loud
    here rather than overstate the grant family. Deterministic and
    read-only: two runs over one corpus pointer agree byte for byte, which
    is what lets a statistical review of this artifact license a frozen
    constant (``docs/salience.md``).
    """
    classify = caption_rule(rule_version)
    counts: dict[int, dict[str, list[int]]] = defaultdict(
        lambda: {c: [0, 0] for c in PETITIONER_CLASSES}
    )
    unresolved: dict[int, int] = defaultdict(int)
    for row in corpus.iter_rows(conn, court="scotus"):
        if not corpus.is_live_slice(row) or not _scored_segment(row):
            continue
        term = corpus.scotus_term_year(row.docket_number)
        if term is None:
            continue
        if row.disposition is None:
            unresolved[term] += 1
            continue
        if (row.sample_weight or 1) != 1:
            raise ValueError(
                f"{row.case_id}: sample_weight {row.sample_weight} — the census "
                "counts raw and must not run over a subsampled frame"
            )
        cell = counts[term][classify(petitioner_caption(row))]
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
        if not unresolved[term]:
            for name in PETITIONER_CLASSES:
                pooled[name][0] += counts[term][name][0]
                pooled[name][1] += counts[term][name][1]
        terms.append(
            CaptionCensusTerm(
                term=term,
                classes=_classes(counts[term]),
                censored=bool(unresolved[term]),
                unresolved=unresolved[term],
            )
        )
    return CaptionCensus(
        rule_version=rule_version,
        corpus_sha256=corpus_sha256,
        terms=terms,
        pooled=_classes(pooled),
    )
