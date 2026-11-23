"""The AI-case watchlist: ``config/ai-watchlist.yaml``, read and checked.

The watchlist is a hand-curated list of lower-court cases in which an AI
developer, or an AI system's training, outputs or deployment, is central to a
claim or defense. The rule and the vocabulary of categories live in the file
itself, beside the cases they govern, so a change to either is reviewed in the
same PR as the cases it admits.

Every docket a listed case names, its own and each related one, is in the set
:func:`tagged_case_ids` returns, the dockets a case-level surface tags ``ai``,
so the tag follows a case to every court it reaches. The same set is what
``watchlist-refresh`` keeps current in the corpus, facts only: those dockets are
admitted by name, not their courts, and the pull rotation leaves them out. The
same set is the ``ai-watchlist`` prediction slice
(:mod:`fedcourtsai.prediction_slices`), which admits these dockets to
prediction scope only when ``predict.slices`` names it, as a population of its
own. None of this changes SCOTUS selection, which is why a ``scotus`` docket is
refused.

A state trial court's case is listed apart, under ``state_cases``, because
nothing above can reach it: CourtListener holds no docket for it, so it has no
corpus row, no tag and no refresh. Only a court ``state_courts`` names is
admitted, and its register of actions is read by hand: each entry of a state
case is a date and a kind the maintainer recorded from the court's own page,
which the AI-cases update reports beside a link to that page.
"""

from __future__ import annotations

import re
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from fedcourtsai import ids
from fedcourtsai.schemas import AiActivityKind, AiActivityMotion

#: The tag every watchlist docket carries on case-level surfaces.
AI_TAG = "ai"
#: The watchlist's file, under the config root.
AI_WATCHLIST_FILENAME = "ai-watchlist.yaml"

_CATEGORY = re.compile(r"^[a-z][a-z0-9-]*$")
#: A CourtListener court id, as the corpus stores it (``cand``, ``ca9``, ``jpml``).
_COURT = r"^[a-z][a-z0-9]*$"
#: A state trial court's id: the state's postal code, then hyphenated parts
#: (``ca-super-sf``). The hyphen keeps it apart from every CourtListener id.
#: The kinds whose entry can name a principal motion.
_MOTION_KINDS = frozenset({"motion", "ruling", "opinion"})
_STATE_COURT = re.compile(r"^[a-z]{2}(-[a-z0-9]+)+$")


class Relation(StrEnum):
    """How a related docket stands to the listed case."""

    #: A court of appeals docket reviewing the case.
    appeal = "appeal"
    #: A docket the case was transferred from, or refiled from in another court.
    transfer = "transfer"
    #: The Judicial Panel on Multidistrict Litigation's docket for the MDL.
    mdl = "mdl"
    #: A member case consolidated into the listed MDL or lead case.
    member = "member"
    #: A parallel docket on the same dispute (a second suit, a petition for review).
    companion = "companion"


class RelatedDocket(BaseModel):
    """One other docket of a listed case."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    court: str = Field(pattern=_COURT)
    docket_id: int = Field(gt=0)
    docket_number: str = Field(min_length=1)
    relation: Relation


class WatchlistCase(BaseModel):
    """One listed case: its primary docket, why the rule admits it, and its other dockets."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    court: str = Field(pattern=_COURT)
    docket_id: int = Field(gt=0)
    docket_number: str = Field(min_length=1)
    category: str
    why: str = Field(min_length=1)
    developers: list[str] = Field(min_length=1)
    added: date
    related: list[RelatedDocket] = Field(default_factory=list)

    @field_validator("developers")
    @classmethod
    def _named_developers(cls, value: list[str]) -> list[str]:
        if any(not name.strip() for name in value) or len(set(value)) != len(value):
            raise ValueError(f"developers must be distinct, non-empty names: {value}")
        return value

    def dockets(self) -> list[tuple[str, int]]:
        """Every ``(court, docket_id)`` the case names, its own first."""
        return [(self.court, self.docket_id)] + [(r.court, r.docket_id) for r in self.related]


class StateCourt(BaseModel):
    """One state trial court the rule admits, and where its public record is read."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    #: The court in the short form a reader knows (``S.F. Super. Ct.``).
    short: str = Field(min_length=1)
    #: The court's own page for looking a case up, which every item links to.
    case_information: str = Field(pattern=r"^https://[^\s()<>]+$")


class StateRegisterEntry(BaseModel):
    """One register-of-actions entry of a state case, recorded by hand: a date and a kind."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    date: date
    kind: AiActivityKind
    motion: AiActivityMotion | None = None

    @model_validator(mode="after")
    def _motion_on_a_kind_that_names_one(self) -> StateRegisterEntry:
        if self.motion is not None and self.kind not in _MOTION_KINDS:
            raise ValueError(
                f"a {self.kind} entry names no motion; only {sorted(_MOTION_KINDS)} may"
            )
        return self


class StateCase(BaseModel):
    """One listed state trial court case, known by the court's own case number."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    court: str
    case_number: str = Field(min_length=1)
    category: str
    why: str = Field(min_length=1)
    developers: list[str] = Field(min_length=1)
    added: date
    entries: list[StateRegisterEntry] = Field(default_factory=list)

    @field_validator("developers")
    @classmethod
    def _named_developers(cls, value: list[str]) -> list[str]:
        if any(not name.strip() for name in value) or len(set(value)) != len(value):
            raise ValueError(f"developers must be distinct, non-empty names: {value}")
        return value

    @field_validator("entries")
    @classmethod
    def _entries_in_order(cls, value: list[StateRegisterEntry]) -> list[StateRegisterEntry]:
        if [entry.date for entry in value] != sorted(entry.date for entry in value):
            raise ValueError("entries must be in date order, oldest first")
        return value


class AiWatchlist(BaseModel):
    """``config/ai-watchlist.yaml``: the category vocabulary and the listed cases."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    categories: dict[str, str] = Field(min_length=1)
    cases: list[WatchlistCase] = Field(min_length=1)
    state_courts: dict[str, StateCourt] = Field(default_factory=dict)
    state_cases: list[StateCase] = Field(default_factory=list)

    @field_validator("state_courts")
    @classmethod
    def _state_court_ids(cls, value: dict[str, StateCourt]) -> dict[str, StateCourt]:
        for court in value:
            if not _STATE_COURT.match(court):
                raise ValueError(
                    f"state court id {court!r} must be a postal code and hyphenated parts"
                )
        return value

    @field_validator("categories")
    @classmethod
    def _category_names(cls, value: dict[str, str]) -> dict[str, str]:
        for name, description in value.items():
            if not _CATEGORY.match(name):
                raise ValueError(f"category {name!r} must be lower-case kebab-case")
            if not description.strip():
                raise ValueError(f"category {name!r} needs a description")
        return value

    @model_validator(mode="after")
    def _consistent(self) -> AiWatchlist:
        names = [case.name for case in self.cases] + [case.name for case in self.state_cases]
        if len(set(names)) != len(names):
            raise ValueError(f"case names must be distinct: {names}")
        state_numbers: dict[tuple[str, str], str] = {}
        for listed in self.state_cases:
            if listed.court not in self.state_courts:
                raise ValueError(
                    f"{listed.name}: court {listed.court!r} is not one of the admitted "
                    f"state courts {sorted(self.state_courts)}"
                )
            if listed.category not in self.categories:
                raise ValueError(
                    f"{listed.name}: category {listed.category!r} is not one of "
                    f"{sorted(self.categories)}"
                )
            key = (listed.court, listed.case_number)
            if key in state_numbers:
                raise ValueError(
                    f"{listed.court} case number {listed.case_number} is named twice "
                    f"({state_numbers[key]}; {listed.name})"
                )
            state_numbers[key] = listed.name
        seen: dict[tuple[str, int], str] = {}
        numbers: dict[tuple[str, str], str] = {}
        for case in self.cases:
            if case.category not in self.categories:
                raise ValueError(
                    f"{case.name}: category {case.category!r} is not one of "
                    f"{sorted(self.categories)}"
                )
            for court, docket_id in case.dockets():
                if court == "scotus":
                    raise ValueError(
                        f"{case.name}: a SCOTUS docket is never listed; it enters the "
                        "SCOTUS pipeline on its own salience terms"
                    )
                if (court, docket_id) in seen:
                    raise ValueError(
                        f"{court} docket {docket_id} is named twice "
                        f"({seen[(court, docket_id)]}; {case.name})"
                    )
                seen[(court, docket_id)] = case.name
            for court, number in [(case.court, case.docket_number)] + [
                (r.court, r.docket_number) for r in case.related
            ]:
                if (court, number) in numbers:
                    raise ValueError(
                        f"{court} docket number {number} is named twice "
                        f"({numbers[(court, number)]}; {case.name})"
                    )
                numbers[(court, number)] = case.name
        return self

    def by_category(self) -> dict[str, list[WatchlistCase]]:
        """The listed cases under each category, every category present, in file order."""
        grouped: dict[str, list[WatchlistCase]] = {name: [] for name in self.categories}
        for case in self.cases:
            grouped[case.category].append(case)
        return grouped


class UniqueKeyLoader(yaml.SafeLoader):
    """A safe loader that refuses a repeated mapping key, which plain YAML keeps the last of."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
        keys = [self.construct_object(key, deep=deep) for key, _ in node.value]
        duplicated = sorted({str(key) for key in keys if keys.count(key) > 1})
        if duplicated:
            raise ValueError(f"duplicate key(s) {duplicated}: a later entry would hide one")
        return super().construct_mapping(node, deep=deep)


def load_ai_watchlist(path: Path) -> AiWatchlist:
    """Read and validate the watchlist; a missing or empty file is an error, not a default."""
    data = yaml.load(path.read_text(), Loader=UniqueKeyLoader)
    return AiWatchlist.model_validate(data)


def tagged_case_ids(watchlist: AiWatchlist) -> frozenset[str]:
    """The case ids (``<court>/<docket_id>``) of every docket that carries :data:`AI_TAG`."""
    return frozenset(
        ids.case_id(court, docket_id)
        for case in watchlist.cases
        for court, docket_id in case.dockets()
    )
