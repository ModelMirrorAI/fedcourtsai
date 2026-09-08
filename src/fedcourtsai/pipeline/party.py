"""Party-derived case annotations for analytics: which sovereign is on which side.

Read-side only, and deliberately not a prediction input: every value here is a
pure function of a corpus row's caption plus a date the *caller* supplies, so a
cut re-derives from a corpus pointer with no stored column, no writer lane, and
no model spend. The petitioner-class rules in :mod:`.caption` are the building
block; this module adds the three things a party cut needs that they do not
give: the respondent side, the two sides composed into one annotation, and the
administration a federal party belonged to.

**Versioned like a caption rule, and for the same reason.** ``party-v1``
composes :func:`.caption.classify_petitioner_v2` over *both* caption halves;
:data:`PARTY_RULES` registers it under that label and a change to what any
annotation means is a new label beside it, never an edit to this one. The
selection-grade predicates are called and never touched: ``caption-v1`` is the
``sal-v2`` carve-in's frozen predicate and ``caption-v2`` is the predicate
``sal-v3`` and the active ``sal-v4`` carve in on, so a widening of either would
move selection. The respondent half is a call site :mod:`.salience` has no
analogue for — it reads the petitioner caption only — which is exactly why the
composition lives here under its own label rather than inside a caption rule.

**The administration comes from dates, never from the caption's names.** A
federal officer is captioned in official capacity ("Noem, Secretary of Homeland
Security"), and that caption *auto-substitutes* on a transition: the same
docket reads one officer's name before January 20 and the successor's after,
with no docket event to mark it. Our stored ``case_name`` is as-of-last-pull, so
the officer a caption names is evidence about when the row was last refreshed,
not about whose administration litigated it. Dates carry no such hazard, so
:func:`administration_for` reads a date against :data:`ADMINISTRATIONS` and the
caption's names are used for one narrow, separately-labeled purpose:
:attr:`PartyAnnotations.named_president`, a surname match on a party's name.

The label says who held office on that date; it does not assert that the
administration was the litigant. The ``federal`` class is the federal
government broadly — the United States, its agencies, and officers in the
caption's officer convention, and a caption naming a United States *court* —
so a case captioned between two federal appellate judges attributes an
administration the executive had no part in. That is the honest reading of a
date-attributed label, and a cut that needs the executive specifically has to
narrow the class rather than the date.

**Which date is the caller's to choose.** A petition filed under one
administration is routinely resolved under the next, so "the administration"
is not a property of a case at all — it is a property of a case *at a moment*.
:func:`party_annotations` therefore takes ``as_of`` as a required argument and
attributes that instant only; there is no default, because a default is a
convention silently inherited by every cut that forgets to state one. Each
analytics cut declares its own — arrival questions ("who held office when this
arrived") read the filing date, outcome questions ("who held office when the
Court acted") read the resolution date — and stamps the choice on its output
(:attr:`PartyCensus.as_of_field`), so two cuts are comparable only when their
stamps agree. Neither gloss says the government *brought* the case: federal
parties are respondents far more often than petitioners, which the side fields
report and the date fields never do. ``as_of`` may be ``None`` (an undated
row), which answers ``administration=None`` rather than guessing.

Honest limits, of which the census counts the first and states the rest: the
respondent side exists only where the joined caption carries a `` v. ``
separator, so an ``In re`` or ``Ex parte`` caption annotates from its single
party (:attr:`PartyCensus.single_party`); ``petitioner_title`` (the structured,
rendering-independent petitioner column) backs under half the frame — 9,625 of
20,145 rows on the blob pulled 2026-09-08, newest stored snapshot 2026-07-13 —
and the rest split ``case_name``, which no structured respondent column backs
on either path; and an anonymized or initialized IFP caption carries no
classifiable party name at all, so it lands in the ``none`` cell without a
counter of its own. Those rows are ``private``/``none`` by the same
total-function rule the caption classifiers use — never an error, and never a
fabricated class, but ``none`` reads as "no sovereign this caption names",
never as "no sovereign".
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Final, Literal, get_args

from .. import corpus
from ..schemas import (
    PartyAdministrationCell,
    PartyCensus,
    PartyFrameCell,
    PartyPresidentCell,
    PartySideCell,
)
from .caption import (
    CAPTION_RULE_VERSION_V2,
    PetitionerClass,
    classify_petitioner_v2,
    petitioner_caption,
)

#: Which side(s) of the caption a sovereign class occupies.
PartySide = Literal["none", "petitioner", "respondent", "both"]

#: Reporting order for a side value: the cells a reader compares, weakest last.
PARTY_SIDES: Final[tuple[PartySide, ...]] = ("both", "petitioner", "respondent", "none")

#: This annotation rule's version. A change to what any field means is a NEW
#: label registered beside this one in :data:`PARTY_RULES` — the census names
#: the rule it was cut under, so a number keeps replaying under the rule that
#: produced it.
PARTY_RULE_VERSION = "party-v1"

#: The caption rule ``party-v1`` composes over both halves. Stamped on the
#: census beside the party rule so the artifact is self-describing: a party
#: label names which caption predicate produced its classes, rather than leaving
#: a reader to recover the pairing from the source at the commit that ran it.
PARTY_CAPTION_RULE_VERSION: Final[str] = CAPTION_RULE_VERSION_V2


@dataclass(frozen=True)
class Administration:
    """One presidential administration, as a date window with an unambiguous label.

    ``label`` carries the presidency's ordinal because a surname does not
    identify an administration: Trump's two non-consecutive terms are separate
    administrations that litigated different cases, and ``bush-41`` /
    ``bush-43`` are different people. ``start`` is the inauguration date.
    """

    label: str
    president: str
    start: date


#: The administration calendar: inauguration dates, ascending, no gaps.
#:
#: Attribution is by date, so the calendar is the whole mechanism and its reach
#: is the honest bound on what can be attributed. It begins at 1981-01-20
#: because the corpus's earliest filing date is 1982-10-05 (blob pulled
#: 2026-09-08, newest stored snapshot 2026-07-13) — a full term of margin below
#: anything a row's *filing* can carry, and a floor that only a historical
#: backfill could move. A date before the first entry attributes ``None`` rather
#: than the first administration, which matters for the one field that does
#: reach further back: a historical SCOTUS row's decision date can predate the
#: calendar by a century, and "unknown" is the only true answer there. The live
#: slice, which is what the census cuts, begins far later — its filing dates run
#: from 2017-06-27 on the same blob — so five of these entries are exercised by
#: no census row at all and exist for callers annotating rows outside it.
#:
#: A transfer of power happens at noon Eastern on inauguration day. We hold
#: dates, not times, so the boundary rule is ``start <= as_of``: inauguration
#: day itself attributes to the *incoming* administration. The half-day this
#: misattributes is the honest cost of date granularity, and it is stated here
#: rather than discovered in a cell that looks one case short.
ADMINISTRATIONS: Final[tuple[Administration, ...]] = (
    Administration(label="reagan-40", president="Reagan", start=date(1981, 1, 20)),
    Administration(label="bush-41", president="Bush", start=date(1989, 1, 20)),
    Administration(label="clinton-42", president="Clinton", start=date(1993, 1, 20)),
    Administration(label="bush-43", president="Bush", start=date(2001, 1, 20)),
    Administration(label="obama-44", president="Obama", start=date(2009, 1, 20)),
    Administration(label="trump-45", president="Trump", start=date(2017, 1, 20)),
    Administration(label="biden-46", president="Biden", start=date(2021, 1, 20)),
    Administration(label="trump-47", president="Trump", start=date(2025, 1, 20)),
)

#: Every president surname the calendar knows, longest-first so a surname that
#: contains another never loses the longer match. Ties break alphabetically
#: rather than on set order, which is hash-randomized per process: the module
#: promises two runs over one pointer agree byte for byte, and a pattern built
#: in a different order is a different artifact even where it matches the same.
_PRESIDENT_SURNAMES: Final[tuple[str, ...]] = tuple(
    sorted({admin.president for admin in ADMINISTRATIONS}, key=lambda name: (-len(name), name))
)

# A president's surname as the last word of a party's *name* segment — the
# segment before the first comma, which is where a caption puts the party and
# after which it puts the office ("Trump, President of the United States") or
# the et-al tail. Requiring the surname to END the name segment is what keeps
# an entity merely containing the word out: "Bush Brothers & Co." and "Clinton
# County Board" end in "Co." and "Board". It cannot keep out a private litigant
# who happens to be named Bush or Clinton, and nothing about a caption can — the
# flag is a NAME match, not an identification of the person, which is why it
# travels as its own field beside a class rather than inside one. It fires on
# BOTH capacities: an official-capacity caption ("Trump, President of the United
# States") matches the same way a personal-capacity one does, so the flag alone
# is not the personal-capacity family — that family is the flag together with
# `federal_party == "none"`, an office in the caption being what separates them.
_PRESIDENT_NAME_RE: Final = re.compile(
    r"^[^,;]*?\b(" + "|".join(re.escape(name) for name in _PRESIDENT_SURNAMES) + r")\s*(?:$|[,;])",
    re.IGNORECASE,
)

#: The caption separator SCOTUS captions join on. Only the FIRST occurrence
#: splits: a consolidated caption can carry more, and everything after the first
#: separator is the respondent side as the caption renders it. The frame carries
#: no such caption today (measured: zero live-slice rows hold two separators), so
#: nothing bleeds; were a consolidated-caption source to land, the respondent
#: half would carry a second case's petitioner and the unanchored markers would
#: read it. The exact spelling is load-bearing in the other direction too: a
#: caption whose separator is malformed ("Pennsylvania, Petitioner v.Landis")
#: does not split at all and annotates as a single party, which is one row of the
#: frame and the same shape the frozen caption rules already miss.
_CAPTION_SEPARATOR: Final[str] = " v. "

#: Which date field a cut reads for ``as_of``, by name. ``filed`` is the arrival
#: moment (who held office when the petition arrived); ``resolved`` is the
#: petition-stage resolution moment (who held office when the Court acted) — the
#: cert grant or denial date, falling back to ``date_decided`` where a row
#: carries only the termination date. Under ``resolved`` a pending petition has
#: no date at all, so the newest administration's window is **right-censored**
#: and its count is a floor; :attr:`PartyCensus.pending` is the size of that
#: censoring.
PARTY_AS_OF_FIELDS: Final[tuple[str, ...]] = ("filed", "resolved")

#: One docket stratum. Typed rather than free text because every administration
#: cell is keyed on it, so a typo would silently mint a cell nobody counted.
DocketStratum = Literal["paid-cert", "ifp-cert", "application", "other"]

#: The docket strata the frame mixes, in reporting order. The census keys every
#: administration cell on one, because the strata are not present in equal
#: proportion across the windows — the live channel's coverage of the IFP and
#: application streams grew over the slice's span, and the excluded sampled block
#: is entirely IFP — and the class rates differ sharply between them. A count
#: compared across administrations without holding the stratum fixed compares
#: that mix, not litigation; holding it fixed is what makes the comparison mean
#: anything. ``other`` is the residue the three named forms do not cover:
#: original-jurisdiction, miscellaneous, and unparseable docket numbers.
PARTY_STRATA: Final[tuple[DocketStratum, ...]] = get_args(DocketStratum)


@dataclass(frozen=True)
class PartyAnnotations:
    """One row's party annotation at one instant, under one rule version.

    Frozen and self-describing: ``rule_version`` and ``as_of`` travel with the
    values, because neither a side class nor an administration means anything
    without them.
    """

    rule_version: str
    petitioner_class: PetitionerClass
    respondent_class: PetitionerClass | None
    federal_party: PartySide
    state_party: PartySide
    named_president: str | None
    named_president_side: Literal["petitioner", "respondent"] | None
    as_of: date | None
    administration: str | None

    @property
    def named_president_in_caption(self) -> bool:
        """Whether a calendar president's surname names a party in this caption.

        A surname match in either capacity, so it is true of an
        official-capacity caption as readily as a personal-capacity one; the
        personal-capacity reading is this together with ``federal_party ==
        "none"``, an office in the caption being what tells the two apart.
        """
        return self.named_president is not None


def administration_for(as_of: date | None) -> str | None:
    """The administration in office on ``as_of``, or ``None`` where unknowable.

    ``None`` for an undated row and for any date before the calendar's first
    inauguration — the two cases where the honest answer is that we cannot say,
    and where returning the earliest administration would manufacture a cell.
    Inauguration day attributes to the incoming administration
    (:data:`ADMINISTRATIONS`).
    """
    if as_of is None:
        return None
    match: str | None = None
    for admin in ADMINISTRATIONS:
        if admin.start <= as_of:
            match = admin.label
        else:
            break
    return match


def respondent_caption(row: corpus.CorpusRow) -> str | None:
    """The row's respondent caption, or ``None`` where the caption has one party.

    Unlike the petitioner side, no structured respondent column exists on
    either ingestion path — the SCOTUS live channel's ``RespondentTitle`` is
    consumed into the joined ``case_name`` and not stored on its own — so this
    is always the split, and it inherits the join's rendering quirks. An ``In
    re`` / ``Ex parte`` caption has no respondent half and answers ``None``,
    which is a different fact from "a respondent nobody could classify" and is
    kept distinct all the way to the census.
    """
    _, separator, tail = row.case_name.partition(_CAPTION_SEPARATOR)
    if not separator:
        return None
    return tail.strip() or None


def _side(petitioner_hit: bool, respondent_hit: bool) -> PartySide:
    """Compose two side hits into a :data:`PartySide` value."""
    if petitioner_hit and respondent_hit:
        return "both"
    if petitioner_hit:
        return "petitioner"
    if respondent_hit:
        return "respondent"
    return "none"


def _named_president(text: str) -> str | None:
    """The calendar president whose surname ends this caption half's name segment.

    Only the *leading* segment is tested — the party the caption puts first —
    so a president named second among several parties on a side does not match;
    and the caller stops at the petitioner side, so a caption naming presidents
    on both sides reports the petitioner's. Both are undercounts by
    construction, stated here and in :class:`.PartyPresidentCell` because the
    field's whole use is as a screen whose recall a reader must know.
    """
    match = _PRESIDENT_NAME_RE.match(text.strip())
    if match is None:
        return None
    matched = match.group(1).casefold()
    return next(name for name in _PRESIDENT_SURNAMES if name.casefold() == matched)


def party_annotations(row: corpus.CorpusRow, as_of: date | None) -> PartyAnnotations:
    """The ``party-v1`` annotation of ``row`` as of ``as_of``.

    Both caption halves go through ``caption-v2``'s class predicate unchanged
    (:func:`.caption.classify_petitioner_v2`) — the petitioner half preferring
    the structured ``petitioner_title`` column, the respondent half from the
    caption split, ``None`` where there is no `` v. `` to split on. A
    single-party caption therefore reports the petitioner's class alone; it
    never reports the missing side as ``private``.

    ``as_of`` is required and may be ``None``. It decides one field —
    :attr:`PartyAnnotations.administration` — and it is the caller's convention
    to choose: the module docstring says why there is no default. The
    administration is attributed **only** where a federal party is present:
    with no federal litigant there is no administration to speak of, and
    stamping the date's president on a private-versus-state case would invite
    exactly the cross-tab that means nothing.

    Pure and total, like the caption classifiers: no lookup, no I/O, and no
    caption shape raises.
    """
    petitioner_text = petitioner_caption(row)
    respondent_text = respondent_caption(row)
    petitioner_cls = classify_petitioner_v2(petitioner_text)
    respondent_cls = classify_petitioner_v2(respondent_text) if respondent_text else None
    federal = _side(petitioner_cls == "federal", respondent_cls == "federal")
    state = _side(petitioner_cls == "state", respondent_cls == "state")
    president = _named_president(petitioner_text)
    president_side: Literal["petitioner", "respondent"] | None = None
    if president is not None:
        president_side = "petitioner"
    elif respondent_text is not None:
        president = _named_president(respondent_text)
        if president is not None:
            president_side = "respondent"
    return PartyAnnotations(
        rule_version=PARTY_RULE_VERSION,
        petitioner_class=petitioner_cls,
        respondent_class=respondent_cls,
        federal_party=federal,
        state_party=state,
        named_president=president,
        named_president_side=president_side,
        as_of=as_of,
        administration=administration_for(as_of) if federal != "none" else None,
    )


#: Every registered annotation rule, keyed by version label. Added to, never
#: edited: a cut names the rule it ran under, and that number replays only
#: against the rule that produced it.
PARTY_RULES: Final[Mapping[str, Callable[[corpus.CorpusRow, date | None], PartyAnnotations]]] = (
    MappingProxyType({PARTY_RULE_VERSION: party_annotations})
)


def party_rule(rule_version: str) -> Callable[[corpus.CorpusRow, date | None], PartyAnnotations]:
    """The registered annotator for ``rule_version``.

    Raises :class:`KeyError` for an unregistered label rather than falling back
    to the current rule: a caller asking for a rule this process cannot produce
    wants an error, not a cut silently taken under a version it did not ask for.
    """
    return PARTY_RULES[rule_version]


def docket_stratum(row: corpus.CorpusRow) -> DocketStratum:
    """The row's docket stratum (:data:`PARTY_STRATA`), off its docket number alone.

    Read through the shared recognizers rather than a private parse: the
    tolerant application form first (an application number is a separate
    numbering sequence, not a spelling of the cert one), then the modern-cert
    form split by the fee serial, and everything else — original, miscellaneous,
    pre-modern, unparseable — as ``other``. Total, like the annotations: every
    frame row lands in exactly one stratum, so the strata partition the
    denominator.
    """
    if corpus.is_scotus_application_form(row.docket_number):
        return "application"
    if corpus.is_modern_cert(row):
        return "ifp-cert" if corpus.is_ifp_petition(row) else "paid-cert"
    return "other"


def as_of_date(row: corpus.CorpusRow, as_of_field: str) -> date | None:
    """The row's ``as_of`` date under the named convention (:data:`PARTY_AS_OF_FIELDS`).

    ``resolved`` prefers the petition-stage resolution moment — the cert grant
    or denial date, which is when the Court acted on this petition — and falls
    back to ``date_decided`` only where neither is stored, because
    ``date_decided`` carries termination semantics and for a granted petition
    that is the merits judgment months later. ``None`` where the row carries no
    such date; the caller reports that mass rather than substituting another
    field's date for it.
    """
    if as_of_field == "filed":
        return row.date_filed
    if as_of_field == "resolved":
        return row.date_cert_granted or row.date_cert_denied or row.date_decided
    raise ValueError(f"unknown as-of field {as_of_field!r}; known: {', '.join(PARTY_AS_OF_FIELDS)}")


def party_census(
    conn: corpus.ReadConnection,
    *,
    as_of_field: str,
    corpus_sha256: str = "",
    rule_version: str = PARTY_RULE_VERSION,
) -> PartyCensus:
    """The live-slice party census: who the sovereign parties are, by administration.

    Counts only. Grant rates by government-party status belong to the analytics
    cuts that carry scope strings and denial-reweighting, and a rate published
    from here would be one nobody reviewed; what this artifact answers is the
    prior question — how much of the frame each annotation cell holds, and how
    much of it the caption cannot classify at all.

    The frame is the live slice's **unweighted** rows (SCOTUS rows the live
    channel has polled, carrying ``sample_weight`` 1), not the salience gate's
    scored segment: the annotation is a property of a caption, so the honest
    denominator is every row that has one, IFP and interim-docket rows
    included. The one exclusion is the live slice's legacy systematic denial
    sample — a block the earlier historical walker kept one row in ten, still
    stored weighted — counted whole in :attr:`PartyCensus.sampled_excluded`
    and annotated nowhere. Mixing it in would understate that stratum tenfold
    in exactly the cells it is concentrated in (IFP prisoner petitions against
    wardens and the United States), and inflating it by its weight would report
    a count of rows nobody holds; a raw count over the rows that stand for
    themselves, beside the size of the block that does not, is the reading the
    later reweighted rate cuts can build on rather than one they would have to
    contradict. The other coverage counters
    (:attr:`PartyCensus.single_party`, :attr:`PartyCensus.undated`,
    :attr:`PartyCensus.pending`) likewise name the rows a cell could not be
    built from rather than dropping them silently.

    **Every administration cell is keyed on a docket stratum**
    (:data:`PARTY_STRATA`), and :attr:`PartyCensus.frame_by_administration` is
    the matching denominator. Without the stratum a cross-window comparison is
    a mix comparison: the windows hold wildly different proportions of paid
    cert, IFP cert and applications, the excluded sampled block is entirely
    IFP, and the class rates differ between the strata — enough that the raw
    federal-respondent share rises across the windows while the within-stratum
    share is flat. Window size alone does not fix that, which is why the
    denominator is cut the same way the numerator is.

    ``as_of_field`` names which date drives the administration attribution and
    is stamped on the result: the same corpus cut under ``filed`` and under
    ``resolved`` gives different — both correct — administration counts, and
    the stamp is what keeps two cuts from being compared as if they agreed.
    Under ``resolved`` the newest window is right-censored, since a pending
    petition has no resolution date, and :attr:`PartyCensus.pending` is the
    size of the censoring.

    Deterministic and read-only: two runs over one corpus pointer agree byte
    for byte, and ``corpus_sha256`` plus the freshness stamps say which pointer.
    """
    annotate = party_rule(rule_version)
    if as_of_field not in PARTY_AS_OF_FIELDS:
        raise ValueError(
            f"unknown as-of field {as_of_field!r}; known: {', '.join(PARTY_AS_OF_FIELDS)}"
        )
    rows = 0
    single_party = 0
    undated = 0
    pending = 0
    sampled_excluded = 0
    federal_counts: dict[PartySide, int] = dict.fromkeys(PARTY_SIDES, 0)
    state_counts: dict[PartySide, int] = dict.fromkeys(PARTY_SIDES, 0)
    administration_counts: dict[tuple[PartySide, str | None, DocketStratum], int] = defaultdict(int)
    president_counts: dict[tuple[str, Literal["petitioner", "respondent"]], int] = defaultdict(int)
    frame_counts: dict[tuple[str | None, DocketStratum], int] = defaultdict(int)
    excluded_counts: dict[tuple[str | None, DocketStratum], int] = defaultdict(int)
    for row in corpus.iter_rows(conn, court="scotus", live_slice=True):
        stratum = docket_stratum(row)
        if (row.sample_weight or 1) != 1:
            sampled_excluded += 1
            # The excluded block is dated and stratified exactly as the frame
            # is: the coverage gap is only legible in the same cells the
            # federal counts are read in.
            excluded_counts[(administration_for(as_of_date(row, as_of_field)), stratum)] += 1
            continue
        as_of = as_of_date(row, as_of_field)
        annotation = annotate(row, as_of)
        rows += 1
        # The denominator is built for EVERY frame row, federal party or not,
        # and cut the same way the numerator is: a federal count without its
        # window-and-stratum cell's own size is a numerator alone.
        frame_counts[(administration_for(as_of), stratum)] += 1
        if annotation.respondent_class is None:
            single_party += 1
        if as_of is None:
            undated += 1
        if row.disposition is None:
            pending += 1
        federal_counts[annotation.federal_party] += 1
        state_counts[annotation.state_party] += 1
        if annotation.federal_party != "none":
            administration_counts[
                (annotation.federal_party, annotation.administration, stratum)
            ] += 1
        if annotation.named_president is not None and annotation.named_president_side is not None:
            president_counts[(annotation.named_president, annotation.named_president_side)] += 1
    windows: list[str | None] = [*(admin.label for admin in ADMINISTRATIONS), None]
    return PartyCensus(
        rule_version=rule_version,
        caption_rule_version=PARTY_CAPTION_RULE_VERSION,
        as_of_field=as_of_field,
        corpus_sha256=corpus_sha256,
        latest_pull=corpus.latest_pull_date(conn),
        latest_snapshot=corpus.latest_snapshot_date(conn),
        rows=rows,
        single_party=single_party,
        undated=undated,
        pending=pending,
        sampled_excluded=sampled_excluded,
        frame_by_administration=[
            PartyFrameCell(
                administration=administration,
                stratum=stratum,
                rows=frame_counts[(administration, stratum)],
                sampled_excluded=excluded_counts[(administration, stratum)],
            )
            for administration in windows
            for stratum in PARTY_STRATA
            if frame_counts[(administration, stratum)] or excluded_counts[(administration, stratum)]
        ],
        federal_party=[PartySideCell(side=side, n=federal_counts[side]) for side in PARTY_SIDES],
        state_party=[PartySideCell(side=side, n=state_counts[side]) for side in PARTY_SIDES],
        federal_by_administration=[
            PartyAdministrationCell(
                federal_party=side,
                administration=administration,
                stratum=stratum,
                n=administration_counts[(side, administration, stratum)],
            )
            for side in PARTY_SIDES
            if side != "none"
            for administration in windows
            for stratum in PARTY_STRATA
            if administration_counts[(side, administration, stratum)]
        ],
        named_president=[
            PartyPresidentCell(president=president, side=side, n=n)
            for (president, side), n in sorted(president_counts.items())
        ],
    )
