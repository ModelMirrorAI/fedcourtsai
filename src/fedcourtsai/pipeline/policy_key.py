"""Policy keys for analytics: which emergency applications challenge one policy.

Read-side only and deliberately not a prediction input: the keys are a
committed, hand-labeled reference (the package's ``policy_keys.json``), and the
one consumer is the executive success cut (:mod:`.executive_success`). No cell,
outcome or score reads them, so a relabel moves no frozen input.

**Why a key beside the rule.** ``controversy-v2`` (:mod:`.controversy`) joins
only what the record links: a shared case below, one order, one order text on
one day, or a renewed government application under one caption. One policy
challenged by different litigants in different courts, and decided apart,
stays several controversies under it: the travel ban, the census question,
the military's transgender-service rule. A published per-policy tally counts
each such policy once. The record cannot say which suits share a policy, so a
key names them, and the cut counts the controversies a second time with the
keys' joins added to the rule's. The rule's own cells stay as they are, and
the keyed cells sit beside them.

**The reference**, ``policy-key-v1``: each key names one federal policy, or one
suit across courts, and lists the applications that challenge or defend it.
An application sits under at most one key. A key joins its applications to
each other and, through the rule's links, to whatever the rule joins them to.
A key need not list an application the rule already joins, and listing one
changes nothing.

**How the keys were labeled.** By one grouper, the session that assembled the
emergency-docket replication, with no second rater: it grouped the rows the
policy-area rounds labeled (OT2016 from 2017-01-20 through OT2024) into
policies, reading the raters' notes and its own knowledge of a public case the
docket names, not blind to the outcome and with the published per-policy tally
in view. A key is not reproducible from the record alone. The keys cover the
applications those rounds read, so a later application joins only by the rule
until a key lists it. Two keys name one suit across courts rather than one
policy (the EMTALA suit, the *Juliana* climate suit).

**Versioned like the policy areas.** ``policy-key-v1`` is this reference and
these rules; a change to what a key means is a new label beside it, while
adding an application to a key under the same rules is not.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from importlib.resources import files
from types import MappingProxyType
from typing import Any, Final

#: The reference's version.
POLICY_KEY_RULE_VERSION: Final[str] = "policy-key-v1"

#: The reference resource, at the package root.
POLICY_KEYS_RESOURCE: Final[str] = "policy_keys.json"


@dataclass(frozen=True)
class PolicyKey:
    """One policy and the applications that challenge or defend it."""

    key: str
    note: str
    dockets: tuple[str, ...]


def parse_policy_keys(text: str) -> Mapping[str, PolicyKey]:
    """Parse a keys document, keyed by normalized docket number.

    Refuses an unknown version, a malformed key, a key named twice, a key with
    fewer than two applications, and an application under two keys or twice
    under one, in any spelling.
    """

    def refuse_repeats(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        seen: dict[str, Any] = {}
        for key, value in pairs:
            if key in seen:
                raise ValueError(f"policy keys name {key} twice")
            seen[key] = value
        return seen

    document = json.loads(text, object_pairs_hook=refuse_repeats)
    if not isinstance(document, dict) or not isinstance(document.get("keys"), dict):
        raise ValueError("policy keys are an object with a keys object")
    if document.get("rule_version") != POLICY_KEY_RULE_VERSION:
        raise ValueError(
            f"policy keys are {document.get('rule_version')!r}, not {POLICY_KEY_RULE_VERSION!r}"
        )
    by_docket: dict[str, PolicyKey] = {}
    for name, entry in document["keys"].items():
        if not name.strip():
            raise ValueError("a key needs a name")
        if not isinstance(entry, dict) or set(entry) != {"note", "dockets"}:
            raise ValueError(f"{name}: a key holds exactly note and dockets")
        note, dockets = entry["note"], entry["dockets"]
        if not isinstance(note, str) or not note.strip():
            raise ValueError(f"{name}: note must be a non-empty string")
        if not isinstance(dockets, list) or not all(isinstance(d, str) for d in dockets):
            raise ValueError(f"{name}: dockets must be a list of docket numbers")
        spelled = tuple(docket.strip().upper() for docket in dockets)
        if len(set(spelled)) < 2:
            raise ValueError(f"{name}: a key joins at least two applications")
        if len(set(spelled)) != len(spelled):
            raise ValueError(f"{name}: names an application twice")
        policy = PolicyKey(key=name, note=note, dockets=spelled)
        for docket in spelled:
            if docket in by_docket:
                raise ValueError(f"{docket} sits under {by_docket[docket].key} and {name}")
            by_docket[docket] = policy
    return MappingProxyType(by_docket)


@cache
def policy_keys() -> Mapping[str, PolicyKey]:
    """The committed keys, keyed by normalized docket number."""
    resource = files("fedcourtsai").joinpath(POLICY_KEYS_RESOURCE)
    return parse_policy_keys(resource.read_text(encoding="utf-8"))


def policy_key(docket_number: str) -> PolicyKey | None:
    """The key one application sits under, any spelling of its number; ``None`` if none."""
    return policy_keys().get(docket_number.strip().upper())
