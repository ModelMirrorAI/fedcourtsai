"""The AI-case watchlist: ``config/ai-watchlist.yaml``, read and checked.

The watchlist is a hand-curated list of lower-court cases in which an AI
developer, or an AI system's training, outputs or deployment, is central to a
claim or defense. The rule and the vocabulary of categories live in the file
itself, beside the cases they govern, so a change to either is reviewed in the
same PR as the cases it admits.

Every docket a listed case names, its own and each related one, is in the set
:func:`tagged_case_ids` returns, the dockets a case-level surface tags ``ai``,
so the tag follows a case to every court it reaches. The tag is a label for
display surfaces only: nothing here widens the corpus's court allowlist,
admits a case to prediction scope, or changes SCOTUS selection, which is why
a ``scotus`` docket is refused.
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

#: The tag every watchlist docket carries on case-level surfaces.
AI_TAG = "ai"

_CATEGORY = re.compile(r"^[a-z][a-z0-9-]*$")
#: A CourtListener court id, as the corpus stores it (``cand``, ``ca9``, ``jpml``).
_COURT = r"^[a-z][a-z0-9]*$"


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


class AiWatchlist(BaseModel):
    """``config/ai-watchlist.yaml``: the category vocabulary and the listed cases."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    categories: dict[str, str] = Field(min_length=1)
    cases: list[WatchlistCase] = Field(min_length=1)

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
        names = [case.name for case in self.cases]
        if len(set(names)) != len(names):
            raise ValueError(f"case names must be distinct: {names}")
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


class _UniqueKeyLoader(yaml.SafeLoader):
    """A safe loader that refuses a repeated mapping key, which plain YAML keeps the last of."""

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
        keys = [self.construct_object(key, deep=deep) for key, _ in node.value]
        duplicated = sorted({str(key) for key in keys if keys.count(key) > 1})
        if duplicated:
            raise ValueError(f"duplicate key(s) {duplicated}: a later entry would hide one")
        return super().construct_mapping(node, deep=deep)


def load_ai_watchlist(path: Path) -> AiWatchlist:
    """Read and validate the watchlist; a missing or empty file is an error, not a default."""
    data = yaml.load(path.read_text(), Loader=_UniqueKeyLoader)
    return AiWatchlist.model_validate(data)


def tagged_case_ids(watchlist: AiWatchlist) -> frozenset[str]:
    """The case ids (``<court>/<docket_id>``) of every docket that carries :data:`AI_TAG`."""
    return frozenset(
        ids.case_id(court, docket_id)
        for case in watchlist.cases
        for court, docket_id in case.dockets()
    )
