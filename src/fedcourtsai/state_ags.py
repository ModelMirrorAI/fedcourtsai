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
window (:data:`AMBITION_WINDOW_DAYS`), and the coalition figures read only the
actions two or more states took part in. The rung each kind reaches is
:func:`rung`; a kind on the ``defense`` or ``context`` track never raises a tier.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from enum import IntEnum, StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from fedcourtsai.ai_watchlist import _UniqueKeyLoader

#: The registry's file, under the config root.
STATE_AGS_FILENAME = "state-ags.yaml"
#: The registered name of the ambition measure the registry feeds.
AMBITION_METHOD = "ag-ai-ambition-v1"
#: The trailing window, in days, an action counts toward an office's tier.
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
    #: A multistate amicus brief in a case against an AI developer.
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

    def holder_on(self, day: date) -> Holder:
        """The holder in office on ``day``; a successor counts once their start has come."""
        current = self.holders[0]
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


class StateAgRegistry(BaseModel):
    """``config/state-ags.yaml``: the subject vocabulary, the roster, and the actions."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    categories: dict[str, str] = Field(min_length=1)
    offices: list[Office] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)

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
    data = yaml.load(path.read_text(), Loader=_UniqueKeyLoader)
    return StateAgRegistry.model_validate(data)
