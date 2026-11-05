"""State attorneys general and AI litigation: ``config/state-ags.yaml``, read and checked.

The registry is hand-curated, like the AI-case watchlist, because almost none of
what it records reaches the corpus: state AGs act against AI developers mostly
in state court, through investigations and settlements, and in multistate
letters and amicus briefs. It holds two lists. ``offices`` is the roster: each
of the 50 states and DC, how the office is filled, and its officeholders in
order, an elected or appointed successor included before they take office.
``actions`` are the AI actions: each names the states that took part, which one
led, its kind, and the AG office's own announcement as its source.

The method that reads the registry is ``ag-ai-ambition-v1``
(:data:`AMBITION_METHOD`), defined in ``docs/state-ags.md``: an office's tier is
the highest rung an action of a tier-raising kind reached for it in a trailing
window (:data:`AMBITION_WINDOW_DAYS`). The rung each kind reaches is
:func:`rung`; a kind on the ``defense`` or ``context`` track never raises a tier.
The coalition figures read only the actions two or more offices took part in;
:func:`build_board` computes them, and the tiers, into ``metrics/state-ags.json``.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date, timedelta
from enum import IntEnum, StrEnum
from itertools import combinations
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from fedcourtsai.ai_watchlist import UniqueKeyLoader
from fedcourtsai.schemas import (
    StateAgActionRow,
    StateAgCoalition,
    StateAgDataCenterRow,
    StateAgHolderRow,
    StateAgJoin,
    StateAgOfficeRow,
    StateAgPair,
    StateAgsBoard,
)

#: The registry's file, under the config root.
STATE_AGS_FILENAME = "state-ags.yaml"
#: The registered name of the ambition measure the registry feeds.
AMBITION_METHOD = "ag-ai-ambition-v1"
#: The trailing window, in days, an action counts toward an office's tier. It and
#: :func:`rung` define the method: a change to either is a new method version.
AMBITION_WINDOW_DAYS = 730

#: The jurisdictions the roster covers: the 50 states and the District of Columbia.
JURISDICTIONS: frozenset[str] = frozenset(
    [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "DC",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
)

_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class Selection(StrEnum):
    """How an attorney general comes to hold the office."""

    elected = "elected"
    #: Appointed by the governor.
    governor = "governor"
    #: Chosen by the legislature.
    legislature = "legislature"
    #: Chosen by the state supreme court.
    court = "court"


class HolderStatus(StrEnum):
    """Where an officeholder stands on the registry's own date."""

    #: Holds, or held, the office; ``start`` is the day they took it.
    serving = "serving"
    #: Elected or appointed and not yet in office; ``start`` is the day they take it.
    successor = "successor"
    #: The race is not called; ``name`` and ``party`` stay empty until it is.
    uncalled = "uncalled"


class Rung(IntEnum):
    """The ``ag-ai-ambition-v1`` tiers, lowest first."""

    none = 0
    signals = 1
    joins = 2
    investigates = 3
    sues = 4


class Track(StrEnum):
    """Which part of the method an action kind feeds."""

    #: The AG acting against an AI developer or system; raises the tier.
    enforcement = "enforcement"
    #: The AG defending a state AI law a developer challenges; recorded, never tiered.
    defense = "defense"
    #: Advocacy not aimed at a developer (a letter to Congress); recorded, never tiered.
    context = "context"


class Kind(StrEnum):
    """What kind of action a record is."""

    #: A signed letter or public comment aimed at AI companies.
    letter = "letter"
    #: An amicus brief in a case against an AI developer.
    amicus = "amicus"
    #: An announced investigation or civil investigative demand.
    investigation = "investigation"
    #: A settlement or assurance of voluntary compliance reached without suit.
    settlement = "settlement"
    #: A suit against an AI developer, in any court.
    suit = "suit"
    #: Defending a state AI law against a developer's challenge.
    defense = "defense"
    #: Advocacy to a legislature or agency, not aimed at a developer.
    advocacy = "advocacy"


_TRACK: dict[Kind, Track] = {
    Kind.letter: Track.enforcement,
    Kind.amicus: Track.enforcement,
    Kind.investigation: Track.enforcement,
    Kind.settlement: Track.enforcement,
    Kind.suit: Track.enforcement,
    Kind.defense: Track.defense,
    Kind.advocacy: Track.context,
}


#: Kinds that are filed in a court, so a record names the court and docket number.
_FILED: frozenset[Kind] = frozenset({Kind.amicus, Kind.suit, Kind.defense})
#: Kinds whose rung depends on who led, so a multistate record names its lead.
_LED: frozenset[Kind] = frozenset({Kind.investigation, Kind.settlement, Kind.suit})


def track(kind: Kind) -> Track:
    """The part of the method a kind feeds."""
    return _TRACK[kind]


def rung(kind: Kind, *, led: bool, multistate: bool) -> Rung:
    """The tier an action of ``kind`` reaches for one participating office.

    A letter signals and an amicus brief joins, whoever drafted it. An
    investigation, settlement or suit is the office's own when it acted alone or
    led the coalition, and a join when another state led. Leading a multistate
    suit is suing. Kinds off the enforcement track reach nothing.
    """
    if track(kind) is not Track.enforcement:
        return Rung.none
    if kind is Kind.letter:
        return Rung.signals
    if kind is Kind.amicus:
        return Rung.joins
    if multistate and not led:
        return Rung.joins
    return Rung.sues if kind is Kind.suit else Rung.investigates


class Holder(BaseModel):
    """One attorney general of an office, past, present or next."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str | None = None
    party: str | None = None
    status: HolderStatus
    start: date
    sources: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _named_unless_uncalled(self) -> Holder:
        named = self.name is not None and self.name.strip() != ""
        if self.status is HolderStatus.uncalled and (named or self.party is not None):
            raise ValueError("an uncalled race names no winner and no party")
        if self.status is not HolderStatus.uncalled and not named:
            raise ValueError(f"a {self.status.value} holder needs a name")
        return self


class Office(BaseModel):
    """One state's attorney general's office and its holders, in the order they serve."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    state: str
    selection: Selection
    holders: list[Holder] = Field(min_length=1)

    @field_validator("state")
    @classmethod
    def _known_state(cls, value: str) -> str:
        if value not in JURISDICTIONS:
            raise ValueError(f"{value!r} is not a state postal code or DC")
        return value

    @model_validator(mode="after")
    def _ordered_holders(self) -> Office:
        starts = [holder.start for holder in self.holders]
        if starts != sorted(starts) or len(set(starts)) != len(starts):
            raise ValueError(f"{self.state}: holders must start on distinct days, in order")
        statuses = [holder.status for holder in self.holders]
        if statuses[0] is not HolderStatus.serving:
            raise ValueError(f"{self.state}: the first holder must be one who served")
        pending = [s for s in statuses if s is not HolderStatus.serving]
        if len(pending) > 1 or (pending and statuses[-1] is HolderStatus.serving):
            raise ValueError(f"{self.state}: at most one pending holder, and only last")
        return self

    def holder_on(self, day: date) -> Holder | None:
        """The holder in office on ``day``; a successor counts once their start has come.

        A day before the first recorded holder's start has no holder on record.
        """
        current: Holder | None = None
        for holder in self.holders:
            if holder.start <= day:
                current = holder
        return current

    def transition(self) -> Holder | None:
        """The pending successor (or uncalled race), if the office is changing hands."""
        last = self.holders[-1]
        return None if last.status is HolderStatus.serving else last


class Action(BaseModel):
    """One AI action by one or more AG offices."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    title: str = Field(min_length=1)
    announced: date
    kind: Kind
    category: str
    states: list[str] = Field(min_length=1)
    lead: str | None = None
    developers: list[str] = Field(min_length=1)
    #: The court and docket number, for a suit, amicus or defense that was filed.
    court: str | None = None
    docket_number: str | None = None
    #: The watchlist case's name, when the action is in a case the watchlist follows.
    watchlist_case: str | None = None
    why: str = Field(min_length=1)
    sources: list[str] = Field(min_length=1)
    added: date

    @field_validator("id")
    @classmethod
    def _slug(cls, value: str) -> str:
        if not _SLUG.match(value):
            raise ValueError(f"action id {value!r} must be lower-case kebab-case")
        return value

    @model_validator(mode="after")
    def _consistent(self) -> Action:
        unknown = sorted(set(self.states) - JURISDICTIONS)
        if unknown:
            raise ValueError(f"{self.id}: unknown states {unknown}")
        if len(set(self.states)) != len(self.states):
            raise ValueError(f"{self.id}: a state is listed twice")
        if self.lead is not None and self.lead not in self.states:
            raise ValueError(f"{self.id}: lead {self.lead!r} is not among the states")
        if len(self.states) == 1 and self.lead not in (None, self.states[0]):
            raise ValueError(f"{self.id}: a single-state action is led by that state")
        if (self.court is None) != (self.docket_number is None):
            raise ValueError(f"{self.id}: court and docket_number come together")
        if self.kind in _FILED and self.court is None:
            raise ValueError(f"{self.id}: a {self.kind.value} names its court and docket number")
        if self.multistate and self.kind in _LED and self.lead is None:
            raise ValueError(f"{self.id}: a multistate {self.kind.value} names its lead state")
        if self.added < self.announced:
            raise ValueError(f"{self.id}: added before the action's own date")
        return self

    @property
    def multistate(self) -> bool:
        """Whether two or more offices took part, so the coalition figures read it."""
        return len(self.states) > 1

    def rung_for(self, state: str) -> Rung:
        """The tier this action reaches for one participating office."""
        if state not in self.states:
            return Rung.none
        led = not self.multistate or self.lead == state
        return rung(self.kind, led=led, multistate=self.multistate)


#: The smallest project, in megawatts, the data-center layer lists.
DATA_CENTER_THRESHOLD_MW = 1000


class DataCenterStatus(StrEnum):
    """Where a data center project stands."""

    announced = "announced"
    under_construction = "under-construction"
    operating = "operating"
    #: Kept on record, never marked on the map.
    cancelled = "cancelled"


class DataCenter(BaseModel):
    """One large AI data center project: context beside the tier, never part of it."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    name: str = Field(min_length=1)
    state: str
    locality: str = Field(min_length=1)
    developers: list[str] = Field(min_length=1)
    capacity_mw: int = Field(ge=DATA_CENTER_THRESHOLD_MW)
    status: DataCenterStatus
    announced: date
    sources: list[str] = Field(min_length=1)
    added: date

    @field_validator("id")
    @classmethod
    def _slug(cls, value: str) -> str:
        if not _SLUG.match(value):
            raise ValueError(f"data center id {value!r} must be lower-case kebab-case")
        return value

    @model_validator(mode="after")
    def _consistent(self) -> DataCenter:
        if self.state not in JURISDICTIONS:
            raise ValueError(f"{self.id}: {self.state!r} is not a state postal code or DC")
        if self.added < self.announced:
            raise ValueError(f"{self.id}: added before the project's own date")
        return self

    @property
    def marked(self) -> bool:
        """Whether the project marks its state on the map: every status but cancelled."""
        return self.status is not DataCenterStatus.cancelled


class StateAgRegistry(BaseModel):
    """``config/state-ags.yaml``: the subject vocabulary, the roster, and the actions."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    categories: dict[str, str] = Field(min_length=1)
    offices: list[Office] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)
    data_centers: list[DataCenter] = Field(default_factory=list)

    @model_validator(mode="after")
    def _consistent(self) -> StateAgRegistry:
        for name, description in self.categories.items():
            if not _SLUG.match(name) or not description.strip():
                raise ValueError(f"category {name!r} must be kebab-case with a description")
        states = [office.state for office in self.offices]
        if len(set(states)) != len(states):
            raise ValueError("an office is listed twice")
        if self.offices and set(states) != JURISDICTIONS:
            missing = sorted(JURISDICTIONS - set(states))
            raise ValueError(f"the roster covers every state and DC or none; missing {missing}")
        ids = [action.id for action in self.actions]
        if len(set(ids)) != len(ids):
            raise ValueError("an action id is used twice")
        centers = [center.id for center in self.data_centers]
        if len(set(centers)) != len(centers):
            raise ValueError("a data center id is used twice")
        for action in self.actions:
            if action.category not in self.categories:
                raise ValueError(
                    f"{action.id}: category {action.category!r} is not one of "
                    f"{sorted(self.categories)}"
                )
        return self

    def office(self, state: str) -> Office:
        """The office for one state; a missing one is an error."""
        for office in self.offices:
            if office.state == state:
                return office
        raise KeyError(state)

    def tier(self, state: str, as_of: date) -> Rung:
        """The office's ``ag-ai-ambition-v1`` tier on ``as_of``: the highest rung in the window."""
        since = as_of - timedelta(days=AMBITION_WINDOW_DAYS)
        reached = [
            action.rung_for(state) for action in self.actions if since < action.announced <= as_of
        ]
        return max(reached, default=Rung.none)


def load_state_ags(path: Path) -> StateAgRegistry:
    """Read and validate the registry; a missing or empty file is an error, not a default."""
    data = yaml.load(path.read_text(), Loader=UniqueKeyLoader)
    return StateAgRegistry.model_validate(data)


#: The label each tier is published under.
TIER_LABELS: dict[Rung, str] = {
    Rung.none: "None recorded",
    Rung.signals: "Signals",
    Rung.joins: "Joins",
    Rung.investigates: "Investigates",
    Rung.sues: "Sues",
}


def _holder_name(holder: Holder | None) -> str | None:
    return None if holder is None else holder.name


def _holder_row(holder: Holder) -> StateAgHolderRow:
    return StateAgHolderRow(
        name=holder.name,
        party=holder.party,
        status=holder.status.value,
        start=holder.start,
        sources=list(holder.sources),
    )


def _coalition(registry: StateAgRegistry, states: Sequence[str], as_of: date) -> StateAgCoalition:
    """Affinity, participation and join rankings over the multistate actions to ``as_of``."""
    multistate = [
        frozenset(a.states) for a in registry.actions if a.multistate and a.announced <= as_of
    ]
    total = len(multistate)
    joined = {s: sum(1 for group in multistate if s in group) for s in states}
    participation = {s: (joined[s] / total if total else 0.0) for s in states}
    affinity: dict[tuple[str, str], StateAgPair] = {}
    pairs: list[StateAgPair] = []
    for a, b in combinations(states, 2):
        joint = sum(1 for group in multistate if a in group and b in group)
        if not joint:
            continue
        either = sum(1 for group in multistate if a in group or b in group)
        pair = StateAgPair(a=a, b=b, joint=joint, either=either, affinity=joint / either)
        affinity[(a, b)] = affinity[(b, a)] = pair
        pairs.append(pair)
    pairs.sort(key=lambda p: (-p.affinity, -p.joint, p.a, p.b))
    rankings: dict[str, list[StateAgJoin]] = {}
    for lead in states:
        if not joined[lead]:
            continue
        joins = [
            StateAgJoin(
                state=other,
                affinity=affinity[(lead, other)].affinity,
                joint=affinity[(lead, other)].joint,
                either=affinity[(lead, other)].either,
                participation=participation[other],
                score=affinity[(lead, other)].affinity * participation[other],
            )
            for other in states
            if (lead, other) in affinity
        ]
        joins.sort(key=lambda j: (-j.score, j.state))
        rankings[lead] = joins
    return StateAgCoalition(
        multistate_actions=total,
        participation=participation,
        pairs=pairs,
        join_rankings=rankings,
    )


def build_board(
    registry: StateAgRegistry, as_of: date, watchlist_cases: frozenset[str]
) -> StateAgsBoard:
    """The ``metrics/state-ags.json`` board for ``as_of``, computed from the registry.

    ``watchlist_cases`` is the set of case names the AI watchlist lists; an
    action naming any other is refused, so a link the site renders always
    resolves. An empty roster yields no office rows, never a guessed one.
    """
    for action in registry.actions:
        if action.watchlist_case is not None and action.watchlist_case not in watchlist_cases:
            raise ValueError(
                f"{action.id}: watchlist_case {action.watchlist_case!r} is not on the watchlist"
            )
    since = as_of - timedelta(days=AMBITION_WINDOW_DAYS)
    newest = sorted(registry.actions, key=lambda a: (a.announced, a.id), reverse=True)
    offices = {office.state: office for office in registry.offices}
    centers = sorted(registry.data_centers, key=lambda c: (c.state, -c.capacity_mw, c.id))
    rows: list[StateAgOfficeRow] = []
    for state in sorted(offices):
        office = offices[state]
        mine = [a for a in newest if state in a.states]
        window = [a for a in mine if since < a.announced <= as_of]
        pending = office.transition()
        current = office.holder_on(as_of)
        tier = registry.tier(state, as_of)
        rows.append(
            StateAgOfficeRow(
                state=state,
                selection=office.selection.value,
                holder=_holder_row(current) if current is not None else None,
                transition=None if pending is None else _holder_row(pending),
                transition_overdue=pending is not None and pending.start <= as_of,
                data_center_ids=[c.id for c in centers if c.state == state and c.marked],
                tier=int(tier),
                tier_label=TIER_LABELS[tier],
                window_counts={k.value: sum(1 for a in window if a.kind is k) for k in Kind},
                action_ids=[a.id for a in mine],
            )
        )
    actions = [
        StateAgActionRow(
            id=a.id,
            title=a.title,
            announced=a.announced,
            kind=a.kind.value,
            track=track(a.kind).value,
            category=a.category,
            states=list(a.states),
            lead=a.lead,
            holders={
                s: _holder_name(offices[s].holder_on(a.announced)) if s in offices else None
                for s in a.states
            },
            rungs={s: int(a.rung_for(s)) for s in a.states},
            in_window=since < a.announced <= as_of,
            developers=list(a.developers),
            court=a.court,
            docket_number=a.docket_number,
            watchlist_case=a.watchlist_case,
            why=a.why,
            sources=list(a.sources),
        )
        for a in newest
    ]
    return StateAgsBoard(
        method=AMBITION_METHOD,
        as_of=as_of,
        window_days=AMBITION_WINDOW_DAYS,
        offices=rows,
        actions=actions,
        data_center_threshold_mw=DATA_CENTER_THRESHOLD_MW,
        data_centers=[
            StateAgDataCenterRow(
                id=c.id,
                name=c.name,
                state=c.state,
                locality=c.locality,
                developers=list(c.developers),
                capacity_mw=c.capacity_mw,
                status=c.status.value,
                announced=c.announced,
                sources=list(c.sources),
            )
            for c in centers
        ],
        defense_and_context=sum(1 for a in newest if track(a.kind) is not Track.enforcement),
        coalition=_coalition(registry, sorted(JURISDICTIONS), as_of),
    )
