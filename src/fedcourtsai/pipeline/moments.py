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
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from .. import ids
from ..schemas import EventKind, Moment, Stage

#: The declared claim-set versions, named here and resolved to claim ids by
#: :mod:`fedcourtsai.pipeline.claims`. Strings rather than an import, so this
#: module stays a leaf and the claims module can read this table.
CLAIM_SET_CERT_V1 = "cert-v1"
CLAIM_SET_MERITS_V1 = "merits-v1"


@dataclass(frozen=True)
class MomentSpec:
    """One declared forecast moment: its event, its stage, and what it declares.

    ``ordinal`` orders the moments *within* a stage — 0 is the first, the one
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
        claim_set_version=CLAIM_SET_CERT_V1,
    ),
    MomentSpec(
        event_id=ids.event_id(EventKind.motion.value, "disposition"),
        kind=EventKind.motion,
        stage=Stage.interim,
        moment=Moment.arrival,
        ordinal=0,
        decision_target="disposition",
        description="Disposition of the application for interim relief.",
        claim_set_version=None,
    ),
    MomentSpec(
        event_id=ids.event_id(EventKind.order.value, "judgment"),
        kind=EventKind.order,
        stage=Stage.merits,
        moment=Moment.grant,
        ordinal=0,
        decision_target="judgment",
        description="Disposition of the judgment below, following the cert grant.",
        claim_set_version=CLAIM_SET_MERITS_V1,
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


def declares(event_id: str, stage: Stage) -> bool:
    """Whether ``event_id`` is a declared moment **of** ``stage``.

    The predicate outcome attribution widens on. Both halves matter: an
    undeclared id is not a moment, and a declared moment of a *different* stage
    has no claim on this stage's disposition.
    """
    spec = _BY_EVENT_ID.get(event_id)
    return spec is not None and spec.stage is stage


def first_moment(stage: Stage) -> Moment | None:
    """``stage``'s ordinal-0 moment — what a null ``moment`` reads as.

    ``None`` for a stage with no declared moment, which cannot happen for the
    three real stages but keeps the lookup total rather than raising at a seam
    that is only normalizing a legacy record.
    """
    ordered = sorted(
        (spec for spec in DECLARED_MOMENTS if spec.stage is stage), key=lambda s: s.ordinal
    )
    return ordered[0].moment if ordered else None


def moments_for(stage: Stage) -> tuple[MomentSpec, ...]:
    """``stage``'s declared moments, earliest first."""
    return tuple(
        sorted((spec for spec in DECLARED_MOMENTS if spec.stage is stage), key=lambda s: s.ordinal)
    )
