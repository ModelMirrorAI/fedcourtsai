"""The declared forecast moments: which events exist, and what each one is.

A stage asks one question. A case passes several points at which that question
can honestly be forecast, each with a different information set — a petition at
its first distribution and the same petition after a CVSG; an application on
arrival and again once a response is in; a granted case at the grant and again
once it is briefed. Each of those is a separate **event**, so each freezes its
own context, resolves against the same ground truth, and is scored on its own.

This module is the single register of which moments exist. Everything that used
to ask "is this *the* merits event?" by comparing an id, or "what claims does
this event declare?" by parsing a kind out of a slug, asks this table instead.

**The table is closed and code-owned.** Only the mint seams write these ids;
no extractor can produce one. That property is what lets outcome attribution
widen from "exactly one open event per stage" to "every open event of this
stage, provided they are all declared moments" without losing its refusal of a
*spurious* duplicate — the shape that would otherwise attribute one case-level
disposition to an event that has no claim on it.

Nothing reads a moment out of an event id. Ids are ``evt-<kind>-<label>``
(:mod:`fedcourtsai.ids`), the kind segment is a single token, and the label tail
already carries a collision suffix from the entry-pinned extractor — so there is
no third segment to spare. The id is a key into this table and nothing more.

The trial stage keeps a table of its own below (:data:`DECLARED_TRIAL_MOMENTS`):
its moments are different questions rather than one question asked again, and
a motion moment names one event per motion. Its ids sit on a reserved label, a
motion's id ends in the number of the entry that filed it, and
:func:`trial_spec_for` is the only reader of that shape; the record, not the
id, still carries the stage and the moment.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Final

from .. import ids
from ..schemas import EventKind, Moment, Stage

#: The declared claim-set versions, named here and resolved to claim ids by
#: :mod:`fedcourtsai.pipeline.claims`. Strings rather than an import, so this
#: module stays a leaf and the claims module can read this table.
CLAIM_SET_CERT_V2 = "cert-v2"
CLAIM_SET_INTERIM_V1 = "interim-v1"
CLAIM_SET_MERITS_V1 = "merits-v1"
#: The authorship versions: each carries its predecessor's binary claims and
#: adds the stage's distribution claims (``pipeline.claims``).
CLAIM_SET_CERT_V3 = "cert-v3"
CLAIM_SET_INTERIM_V2 = "interim-v2"
CLAIM_SET_MERITS_V2 = "merits-v2"
#: The interim authorship set re-resolved on the finer interim reading: the same
#: claims as ``interim-v2``, its ``interim-disposition`` claim resolving on
#: ``Outcome.interim_granted`` (``pipeline.claims``).
CLAIM_SET_INTERIM_V3 = "interim-v3"
#: The trial stage's sets. The stage asks different questions at its moments,
#: so it declares a set per question: a ruling on a motion, a ruling on a
#: motion to dismiss (which adds leave to amend), and the final disposition.
CLAIM_SET_TRIAL_MOTION_V1 = "trial-motion-v1"
CLAIM_SET_TRIAL_DISMISSAL_V1 = "trial-dismissal-v1"
CLAIM_SET_TRIAL_JUDGMENT_V1 = "trial-judgment-v1"


@dataclass(frozen=True)
class MomentSpec:
    """One declared forecast moment: its event, its stage, and what it declares.

    ``ordinal`` orders the *registry* within a stage — 0 is the first, the one
    the ranked board reports and the one a null ``moment`` reads as. It is a
    sort key inside this table, never an identity: a moment is named because a
    reader has to know which information set produced a number, and ``merits/2``
    does not say that.

    ``claim_set_version`` names the declared claim set by version string rather
    than carrying its claim ids, so this module stays a leaf: the ids and their
    resolvers live in :mod:`fedcourtsai.pipeline.claims`, which reads this table.
    Every moment of a stage declares the **same** set — the claims do not change
    because the forecast was taken later, only the information set does.

    ``forecastable`` gates whether the fan-out ever mints a cell for the moment.
    A moment can be declared, parsed, and latched while still being switched
    off — the honest state for one whose horizon has not been shown to clear
    the pipeline's own commit latency.

    ``opened_at_is_the_moment`` says whether the corpus event's ``opened_at``
    date *is* the transition this moment is declared at, which is what lets
    provisioning cut a forward cell's snapshot to the moment's information set.
    True for every moment a mint seam opens at its own trigger — the CVSG
    invitation, the Solicitor General's invited brief, the cert call for a
    response, the first relist, the cert grant, the argument transcript, the interim
    response request, the arrival of a
    petition or an application. False for
    the cert petition baseline, whose ``opened_at`` is docketing: the moment
    it declares is the **distribution**, so a cut at docketing would delete
    the distribution and relist history the declared information set is made
    of.
    """

    event_id: str
    kind: EventKind
    stage: Stage
    moment: Moment
    ordinal: int
    decision_target: str
    description: str
    claim_set_version: str | None
    forecastable: bool = True
    opened_at_is_the_moment: bool = True


#: Every declared moment, stage-major then ordinal. Add a row to add a moment;
#: nothing else keys on the shape of an id.
DECLARED_MOMENTS: tuple[MomentSpec, ...] = (
    MomentSpec(
        event_id=ids.event_id(EventKind.petition.value, "disposition"),
        kind=EventKind.petition,
        stage=Stage.cert,
        moment=Moment.distribution,
        ordinal=0,
        decision_target="disposition",
        description="Disposition of the petition for a writ of certiorari.",
        claim_set_version=CLAIM_SET_CERT_V3,
        # The one moment whose `opened_at` is not its trigger: the ingest
        # projection derives this baseline from the docket merely existing, so
        # the date is docketing. The moment is the distribution, and the
        # distribution/relist history is the signal the cell is conditioned on.
        opened_at_is_the_moment=False,
    ),
    MomentSpec(
        event_id=ids.event_id(EventKind.order.value, "cvsg-disposition"),
        kind=EventKind.order,
        stage=Stage.cert,
        moment=Moment.cvsg,
        ordinal=1,
        decision_target="disposition",
        description=(
            "Disposition of the petition, forecast after the Court called for "
            "the Solicitor General's views."
        ),
        claim_set_version=CLAIM_SET_CERT_V3,
    ),
    MomentSpec(
        # Chronologically the EARLIEST cert moment (docketing precedes every
        # distribution), carried at a later ordinal deliberately: ordinal
        # orders the registry, and the stage's first-position spec is the
        # petition baseline the open-first-moment guard and the resolution
        # sweep key on — renumbering it would move both. The sal-v2 arrival
        # cohort's moment: minted at selection (the deterministic draw or the
        # arrival carve-in), forecast from the docketing-time information set.
        event_id=ids.event_id(EventKind.petition.value, "arrival-disposition"),
        kind=EventKind.petition,
        stage=Stage.cert,
        moment=Moment.arrival,
        ordinal=2,
        decision_target="disposition",
        description=(
            "Disposition of the petition, forecast at docketing — before any "
            "distribution or docket-acquired signal exists."
        ),
        claim_set_version=CLAIM_SET_CERT_V3,
    ),
    MomentSpec(
        # Chronologically after the CVSG moment it follows: the invitation opens
        # that one, and the brief it asked for opens this one, typically months
        # later.
        event_id=ids.event_id(EventKind.brief.value, "sg-disposition"),
        kind=EventKind.brief,
        stage=Stage.cert,
        moment=Moment.sg_brief,
        ordinal=3,
        decision_target="disposition",
        description=(
            "Disposition of the petition, forecast once the Solicitor General has "
            "filed the brief the Court invited."
        ),
        claim_set_version=CLAIM_SET_CERT_V3,
    ),
    MomentSpec(
        # The cert stage's call for a response, typically after the respondent
        # waived: the Court's first sign that a petition has a reader. It shares
        # the interim moment's name, as `arrival` does, because the moment is the
        # same act at a different stage; aggregation keys on the pair.
        event_id=ids.event_id(EventKind.order.value, "call-for-response-disposition"),
        kind=EventKind.order,
        stage=Stage.cert,
        moment=Moment.response_requested,
        ordinal=4,
        decision_target="disposition",
        description=(
            "Disposition of the petition, forecast after the Court called for a response to it."
        ),
        claim_set_version=CLAIM_SET_CERT_V3,
    ),
    MomentSpec(
        # The cert stage's first relist: a conference considered the petition and
        # the Court listed it again rather than deciding it. Only the first relist
        # opens it; a later one repeats the same signal.
        event_id=ids.event_id(EventKind.order.value, "relist-disposition"),
        kind=EventKind.order,
        stage=Stage.cert,
        moment=Moment.relist,
        ordinal=5,
        decision_target="disposition",
        description=(
            "Disposition of the petition, forecast after the Court first relisted it "
            "for another conference."
        ),
        claim_set_version=CLAIM_SET_CERT_V3,
    ),
    MomentSpec(
        event_id=ids.event_id(EventKind.motion.value, "disposition"),
        kind=EventKind.motion,
        stage=Stage.interim,
        moment=Moment.arrival,
        ordinal=0,
        decision_target="disposition",
        description="Disposition of the application for interim relief.",
        claim_set_version=CLAIM_SET_INTERIM_V3,
    ),
    MomentSpec(
        event_id=ids.event_id(EventKind.order.value, "response-requested-disposition"),
        kind=EventKind.order,
        stage=Stage.interim,
        moment=Moment.response_requested,
        ordinal=1,
        decision_target="disposition",
        description=(
            "Disposition of the application, forecast after the Court called for a response."
        ),
        claim_set_version=CLAIM_SET_INTERIM_V3,
    ),
    MomentSpec(
        event_id=ids.event_id(EventKind.brief.value, "response-disposition"),
        kind=EventKind.brief,
        stage=Stage.interim,
        moment=Moment.response_filed,
        ordinal=2,
        decision_target="disposition",
        description=("Disposition of the application, forecast once a response has been filed."),
        claim_set_version=CLAIM_SET_INTERIM_V3,
    ),
    MomentSpec(
        event_id=ids.event_id(EventKind.order.value, "judgment"),
        kind=EventKind.order,
        stage=Stage.merits,
        moment=Moment.grant,
        ordinal=0,
        decision_target="judgment",
        description="Disposition of the judgment below, following the cert grant.",
        claim_set_version=CLAIM_SET_MERITS_V2,
    ),
    MomentSpec(
        event_id=ids.event_id(EventKind.brief.value, "judgment"),
        kind=EventKind.brief,
        stage=Stage.merits,
        moment=Moment.briefed,
        ordinal=1,
        decision_target="judgment",
        description=(
            "Disposition of the judgment below, forecast once both sides' merits "
            "briefs are on the record."
        ),
        claim_set_version=CLAIM_SET_MERITS_V2,
    ),
    MomentSpec(
        # Opened by the argument transcript rather than by a docket entry: the
        # Court posts it the day the case is argued, on a per-Term list the
        # docket does not link.
        event_id=ids.event_id(EventKind.argument.value, "judgment"),
        kind=EventKind.argument,
        stage=Stage.merits,
        moment=Moment.argued,
        ordinal=2,
        decision_target="judgment",
        description=(
            "Disposition of the judgment below, forecast once the transcript of the "
            "oral argument is posted."
        ),
        claim_set_version=CLAIM_SET_MERITS_V2,
    ),
)

_BY_EVENT_ID: Mapping[str, MomentSpec] = MappingProxyType(
    {spec.event_id: spec for spec in DECLARED_MOMENTS}
)


def spec_for(event_id: str) -> MomentSpec | None:
    """The declared moment ``event_id`` names, or ``None`` if it declares none.

    ``None`` covers every entry-pinned event the extractor mints and every
    legacy id written before this table existed. A caller that needs a
    stage-level answer for those falls back to its own rule — the table adds a
    vocabulary, it does not take one away.
    """
    return _BY_EVENT_ID.get(event_id)


def event_stage(stage: Stage | str | None, event_id: str) -> Stage | None:
    """An event's stage: its own where it records one, else the one its id declares.

    A committed ``event.yaml`` may carry no stage — the cert petition baselines
    are written without one — and this table is the authority on a declared
    id's stage. ``None`` for a stage-less event whose id declares nothing.
    """
    if stage is not None:
        return Stage(stage)
    spec = spec_for(event_id)
    return spec.stage if spec is not None else None


def minted_moment_ids() -> frozenset[str]:
    """The declared moments whose ledger ``event.yaml`` is owed **at the mint**.

    Every moment in this table except the two **case-level baselines** — the
    cert petition's ``evt-petition-disposition`` and the interim application's
    ``evt-motion-disposition``. Not to be read as "the stage's first position",
    which is what :func:`moments_for` calls a baseline and a different set:
    merits' first position, ``evt-order-judgment``, is minted like the rest.
    A case-level baseline is a fact about a docket merely
    existing: the ingest projection derives it from the row's own shape, so a
    corpus row carries one long before anything writes its definition, and its
    ledger half arrives later — at first touch (``materialize-event`` in a
    predict cell) or at resolution. Every other moment here exists only because
    a mint seam decided it does, and that seam writes both halves in one step
    (:func:`fedcourtsai.pipeline.outcome.persist_moment_events`), so for these
    ids a corpus row without its ledger file is a half-landed mint — the shape
    ``validate-corpus``'s corpus→ledger check fails on.

    A case-level baseline is recognized by its id rather than listed: it is
    the bare ``disposition`` id of its kind (``evt-<kind>-disposition``),
    which is what the ingest projection synthesizes, while every later moment
    carries a qualifying label (``arrival-``, ``cvsg-``, ``sg-``, ``call-``,
    ``relist-``, ``response-``) or a different decision target (``judgment``). Registering
    a moment therefore needs no edit here; what would is a new stage whose
    baseline is *not* the bare
    ``evt-<kind>-disposition`` shape — the merits precedent, whose first
    position is a minted moment rather than a first-touch baseline.
    """
    return frozenset(
        spec.event_id
        for spec in DECLARED_MOMENTS
        if spec.event_id != ids.event_id(spec.kind.value, "disposition")
    )


def declares(event_id: str, stage: Stage) -> bool:
    """Whether ``event_id`` is a declared moment **of** ``stage``.

    The predicate outcome attribution widens on. Both halves matter: an
    undeclared id is not a moment, and a declared moment of a *different* stage
    has no claim on this stage's disposition.

    Stage comparisons here and below are equality, never identity: callers
    hand in real :class:`Stage` members from the corpus *and* the plain
    strings a validated artifact carries (``use_enum_values``), and a
    ``StrEnum`` is equal to its value where an ``is`` check silently fails —
    turning every lookup total-miss for exactly the deserialized records the
    normalization exists to serve.
    """
    spec = _BY_EVENT_ID.get(event_id)
    return spec is not None and spec.stage == stage


def scores_votes(event_id: str) -> bool:
    """Whether a per-Justice vote forecast for ``event_id`` may be scored at all.

    True only where this table declares ``event_id`` a **merits** moment. Every
    stage that declares a vote block elicits one; exactly one scores it. An
    individual *cert* vote is never scored, however visible it happens to be: a
    cert vote becomes public only when a Justice chooses to note it, so
    observation is very nearly a deterministic function of the value being
    scored and the deny-and-silent stratum has zero probability of observation —
    no reweighting identifies it (`docs/decision-model.md`). The rule is
    therefore structural, not a property of what a particular outcome record
    contains, and it lives here because this table is the authority on an
    event's stage.

    Denial is the **default**, rather than the cert stage being named and the
    rest allowed: an id the table does not declare — an entry-pinned event, a
    record written before the table existed — has no stage this module can
    state, so it cannot be shown not to be cert. The permissive fallback
    :func:`spec_for` documents is the wrong one for a prohibition; a caller
    reading a vocabulary loses nothing by falling back, while a guard that
    falls back scores exactly the ids it cannot vouch for.

    Expressed through :func:`declares` rather than re-reading the table, so the
    equality-not-identity rule that function documents holds here by
    construction instead of by inspection.
    """
    return declares(event_id, Stage.merits)


def first_moment(stage: Stage) -> Moment | None:
    """``stage``'s ordinal-0 moment — what a null ``moment`` reads as.

    ``None`` for a stage with no declared moment, which cannot happen for the
    Court's three stages but keeps the lookup total rather than raising at a
    seam that is only normalizing a legacy record.
    """
    ordered = sorted(
        (spec for spec in DECLARED_MOMENTS if spec.stage == stage), key=lambda s: s.ordinal
    )
    return ordered[0].moment if ordered else None


def moments_for(stage: Stage) -> tuple[MomentSpec, ...]:
    """``stage``'s declared moments in registry order (ordinal ascending).

    Registry order, not chronology: the first position is the stage's
    baseline — the spec the open-first-moment guards and the resolution fan
    key on — and a later registration may be chronologically earlier (the
    cert arrival moment precedes every distribution while carrying a later
    ordinal). A caller wanting time order reads each spec's description.
    """
    return tuple(
        sorted((spec for spec in DECLARED_MOMENTS if spec.stage == stage), key=lambda s: s.ordinal)
    )


# --- the trial stage ----------------------------------------------------------

#: The label every trial-stage event id begins with. Reserved: only the trial
#: mint seam writes an id on it, and the entry-pinned extractor's subject slug
#: steps off it (:mod:`fedcourtsai.pipeline.events`).
TRIAL_LABEL_PREFIX: Final = "trial-"


@dataclass(frozen=True)
class TrialMomentSpec:
    """One declared moment of the trial stage (``docs/trial-stage.md``).

    Kept apart from :data:`DECLARED_MOMENTS` because the two tables answer
    different questions. A Court stage asks one question at several moments, so
    its rows are ordered and a null moment reads as the first. The trial
    stage's moments are five different questions, none of them first, and a
    motion moment names a **family** of events, one per motion a docket files,
    where a Court moment names exactly one. So nothing that walks the Court's
    table (the first-moment reading, the resolution fan, the mint sweep) meets
    a trial row, and a reader of a trial event asks :func:`trial_spec_for`.

    ``word`` is what the id carries after :data:`TRIAL_LABEL_PREFIX`. On a
    motion moment (``per_motion``) the number of the docket entry that filed
    the motion follows it; the judgment moment is one event per case and its
    id ends at the word.

    ``claim_set_version`` names the moment's declared claim set by version
    string, as :class:`MomentSpec` does, resolved in
    :mod:`fedcourtsai.pipeline.claims`.

    ``forecastable`` is the same switch :class:`MomentSpec` carries: a moment
    declared here mints no cell until it is switched on. ``opens_from`` is the
    day it was switched on, set with the switch and never without it: the
    watchlist pass writes no event of a moment that has none, and an event it
    does write opens no earlier than that day, since a motion briefed before
    the registration is forecast from the registration
    (:mod:`fedcourtsai.pipeline.trial_events`).
    """

    moment: Moment
    kind: EventKind
    word: str
    per_motion: bool
    decision_target: str
    description: str
    claim_set_version: str
    forecastable: bool = False
    opens_from: date | None = None

    def __post_init__(self) -> None:
        if self.forecastable != (self.opens_from is not None):
            raise ValueError(
                f"{self.moment.value}: `forecastable` and `opens_from` are set together"
            )

    @property
    def stage(self) -> Stage:
        return Stage.trial


#: Every declared trial moment. A motion event is opened by the motion's
#: filing, so its kind is ``motion``; the final disposition is the court's act.
DECLARED_TRIAL_MOMENTS: tuple[TrialMomentSpec, ...] = (
    TrialMomentSpec(
        moment=Moment.trial_dismissal,
        kind=EventKind.motion,
        word="dismissal",
        per_motion=True,
        decision_target="ruling",
        description="The district court's ruling on a motion to dismiss.",
        claim_set_version=CLAIM_SET_TRIAL_DISMISSAL_V1,
    ),
    TrialMomentSpec(
        moment=Moment.trial_class,
        kind=EventKind.motion,
        word="class",
        per_motion=True,
        decision_target="ruling",
        description="The district court's ruling on a motion for class certification.",
        claim_set_version=CLAIM_SET_TRIAL_MOTION_V1,
    ),
    TrialMomentSpec(
        moment=Moment.trial_summary_judgment,
        kind=EventKind.motion,
        word="summary-judgment",
        per_motion=True,
        decision_target="ruling",
        description="The district court's ruling on one party's motion for summary judgment.",
        claim_set_version=CLAIM_SET_TRIAL_MOTION_V1,
    ),
    TrialMomentSpec(
        moment=Moment.trial_preliminary_injunction,
        kind=EventKind.motion,
        word="preliminary-injunction",
        per_motion=True,
        decision_target="ruling",
        description="The district court's ruling on a motion for a preliminary injunction.",
        claim_set_version=CLAIM_SET_TRIAL_MOTION_V1,
    ),
    TrialMomentSpec(
        moment=Moment.trial_judgment,
        kind=EventKind.order,
        word="judgment",
        per_motion=False,
        decision_target="judgment",
        description="The district court's final disposition of the case.",
        claim_set_version=CLAIM_SET_TRIAL_JUDGMENT_V1,
    ),
)

_TRIAL_BY_MOMENT: Mapping[Moment, TrialMomentSpec] = MappingProxyType(
    {spec.moment: spec for spec in DECLARED_TRIAL_MOMENTS}
)
_TRIAL_BY_KIND_AND_WORD: Mapping[tuple[str, str], TrialMomentSpec] = MappingProxyType(
    {(spec.kind.value, spec.word): spec for spec in DECLARED_TRIAL_MOMENTS}
)
# The entry number is a positive integer with no leading zero, so one motion has
# one id.
_TRIAL_ID_RE: Final = re.compile(
    rf"^evt-(?P<kind>[a-z0-9._]+)-{re.escape(TRIAL_LABEL_PREFIX)}"
    r"(?P<word>[a-z]+(?:-[a-z]+)*?)(?:-(?P<entry>[1-9][0-9]*))?$"
)


def trial_event_id(moment: Moment, entry_number: int | None = None) -> str:
    """The id of ``moment``'s event: the one writer of an id on the trial label.

    A motion moment takes the number of the docket entry that filed the motion
    and the judgment moment takes none; either mismatch is refused, as is a
    moment the trial stage does not declare.
    """
    spec = _TRIAL_BY_MOMENT.get(Moment(moment))
    if spec is None:
        raise ValueError(f"{moment!r} is not a declared trial moment")
    if not spec.per_motion:
        if entry_number is not None:
            raise ValueError(f"{spec.moment.value} is one event per case and takes no entry")
        return ids.event_id(spec.kind.value, f"{TRIAL_LABEL_PREFIX}{spec.word}")
    if entry_number is None or entry_number < 1:
        raise ValueError(f"{spec.moment.value} is named by the entry that filed the motion")
    return ids.event_id(spec.kind.value, f"{TRIAL_LABEL_PREFIX}{spec.word}-{entry_number}")


def trial_spec_for(event_id: str) -> TrialMomentSpec | None:
    """The declared trial moment ``event_id`` belongs to, or ``None``.

    ``None`` for every id off the trial label, and for an id on it that no
    declared moment writes: a wrong kind, an unknown word, a motion id without
    its entry number or a judgment id with one.
    """
    match = _TRIAL_ID_RE.fullmatch(event_id)
    if match is None:
        return None
    spec = _TRIAL_BY_KIND_AND_WORD.get((match["kind"], match["word"]))
    if spec is None or spec.per_motion != (match["entry"] is not None):
        return None
    return spec


def trial_entry_number(event_id: str) -> int | None:
    """The docket entry that filed the motion ``event_id`` names.

    ``None`` for the judgment event and for any id :func:`trial_spec_for` does
    not recognize.
    """
    match = _TRIAL_ID_RE.fullmatch(event_id)
    if match is None or match["entry"] is None or trial_spec_for(event_id) is None:
        return None
    return int(match["entry"])


def trial_spec(moment: Moment | str) -> TrialMomentSpec:
    """The declared trial moment ``moment`` names; refused for any other."""
    spec = _TRIAL_BY_MOMENT.get(Moment(moment))
    if spec is None:
        raise ValueError(f"{moment!r} is not a declared trial moment")
    return spec


def trial_moment(moment: Moment | str) -> bool:
    """Whether ``moment`` is one the trial stage declares."""
    return any(spec.moment == moment for spec in DECLARED_TRIAL_MOMENTS)


def on_trial_label(event_id: str) -> bool:
    """Whether ``event_id``'s label begins with the reserved trial prefix."""
    kind = ids.parse_event_kind(event_id)
    return kind is not None and event_id.startswith(f"evt-{kind}-{TRIAL_LABEL_PREFIX}")
