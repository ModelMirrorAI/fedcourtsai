"""Policy-area labels for analytics: what executive policy an emergency application is about.

Read-side only and deliberately not a prediction input: the labels are a
committed, hand-labeled reference (the package's ``policy_areas.json``),
keyed by application docket number, and the one consumer is the executive
success cut (:mod:`.executive_success`). No cell, outcome or score reads them,
so a relabel moves no frozen input.

**Why a separate vocabulary.** The questions-presented topics
(``docs/qp-topic.md``) label what a petition asks, and no application carries
one. An emergency application is read by the *policy* it challenges or
defends, whatever the legal theory or posture, so a removal dispute about the
head of a labor agency is ``personnel-removal`` and not labor.

**The vocabulary**, ``policy-area-v1``: the areas the published executive
success tally names, plus ``other``. One primary area per application.

- ``immigration``: immigration, citizenship and border policy, including
  removal and its procedures, parole and protected-status terminations, entry
  bans and birthright citizenship.
- ``federal-executions``: the method, schedule or lawfulness of a federal
  execution.
- ``foreign-affairs``: foreign relations, national security and foreign
  trade, including foreign aid, sanctions and emergency tariffs.
- ``elections-census``: elections and the census.
- ``personnel-removal``: presidential control over executive-branch officials
  and operations: removals, reinstatement orders, reductions in force,
  workforce orders, agency reorganization, and the military's personnel rules.
- ``education``: student loans, Title IX regulations, education grants, and
  restructuring of the Department of Education.
- ``health``: public health and health regulation, including vaccination
  requirements, the FDA, health-research grants and health-care policy.
- ``environment-energy``: environmental and energy regulation.
- ``firearms``: federal firearms regulation.
- ``other``: a general federal executive action in none of the above, and
  the label of one whose subject the raters could not determine (flagged
  ``uncertain``).

Where an action spans two areas it takes the area of its stated object: a
grant freeze for health research is ``health``, one for foreign aid
``foreign-affairs``.

**How the reference was labeled.** Two agent raters, each blind to the other
but not to the outcome, labeled every in-scope and unknown-scope application
of the ``exec-action-v1`` cut, and the federal-party rows it reads out of
scope, from its caption, court below and docket
entries, and from their own knowledge of a public case the docket names, so a
label is not reproducible from the record alone. The disagreements were
adjudicated row by row by the session that assembled the reference, which was
not blind. Each entry carries a short note
naming the policy and an ``uncertain`` flag where the subject is in doubt:
either rater was unsure of it, or, in the later round, the raters' areas
differed. The labels cover the applications the corpus held when they were
assigned, so a later application is ``unlabeled`` until it is added, and the
cut counts those beside its cells.

**Versioned like the scope rule.** ``policy-area-v1`` is this vocabulary and
these rules; a change to what an area covers is a new label beside it, while
adding or correcting an entry under the same rules is not.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from importlib.resources import files
from types import MappingProxyType
from typing import Any, Final, Literal, cast, get_args

#: The registered vocabulary's version.
POLICY_AREA_RULE_VERSION: Final[str] = "policy-area-v1"

#: The labels resource, at the package root.
POLICY_AREAS_RESOURCE: Final[str] = "policy_areas.json"

PolicyArea = Literal[
    "immigration",
    "federal-executions",
    "foreign-affairs",
    "elections-census",
    "personnel-removal",
    "education",
    "health",
    "environment-energy",
    "firearms",
    "other",
]

#: The vocabulary in reporting order, ``other`` last.
POLICY_AREAS: Final[tuple[PolicyArea, ...]] = get_args(PolicyArea)


@dataclass(frozen=True)
class PolicyLabel:
    """One application's policy-area label."""

    area: PolicyArea
    note: str
    uncertain: bool


def parse_policy_areas(text: str) -> Mapping[str, PolicyLabel]:
    """Parse a labels document, refusing an unknown version or area, a malformed
    entry, or a docket named twice under any spelling."""

    def refuse_repeats(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        seen: dict[str, Any] = {}
        for key, value in pairs:
            if key in seen:
                raise ValueError(f"policy-area labels name {key} twice")
            seen[key] = value
        return seen

    document = json.loads(text, object_pairs_hook=refuse_repeats)
    if document.get("rule_version") != POLICY_AREA_RULE_VERSION:
        raise ValueError(
            f"policy-area labels are {document.get('rule_version')!r}, "
            f"not {POLICY_AREA_RULE_VERSION!r}"
        )
    labels: dict[str, PolicyLabel] = {}
    for docket, entry in document["labels"].items():
        key = docket.strip().upper()
        if key in labels:
            raise ValueError(f"policy-area labels name {key} twice")
        if not isinstance(entry, dict) or set(entry) != {"area", "note", "uncertain"}:
            raise ValueError(f"{key}: an entry holds exactly area, note and uncertain")
        area, note, uncertain = entry["area"], entry["note"], entry["uncertain"]
        if area not in POLICY_AREAS:
            raise ValueError(f"{key}: unknown policy area {area!r}")
        if not isinstance(note, str) or not note.strip() or not isinstance(uncertain, bool):
            raise ValueError(f"{key}: note must be a non-empty string and uncertain a boolean")
        labels[key] = PolicyLabel(area=cast(PolicyArea, area), note=note, uncertain=uncertain)
    return MappingProxyType(labels)


@cache
def policy_areas() -> Mapping[str, PolicyLabel]:
    """The committed labels, keyed by normalized docket number."""
    resource = files("fedcourtsai").joinpath(POLICY_AREAS_RESOURCE)
    return parse_policy_areas(resource.read_text(encoding="utf-8"))


def policy_label(docket_number: str) -> PolicyLabel | None:
    """The label of one application, any spelling of its number; ``None`` if unlabeled."""
    return policy_areas().get(docket_number.strip().upper())
