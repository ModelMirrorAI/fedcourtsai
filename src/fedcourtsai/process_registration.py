"""Pending registrations: the edits a PR makes to the registry when it moves the process.

A label is named by hand in the PR that moves a digest, and registered here as
**pending** rows: the label's counting instant, each newly blessed digest's
bless moment, each window the label opens and each window it closes, all with
``at`` and ``merge`` null. The merge that carries the PR to ``main`` stamps
them with its own SHA and committer time
(:mod:`fedcourtsai.promotion_record`). A harness boundary is registered the
same way, in the PR that makes the change.

A label belongs to one prediction population, the SCOTUS docket or one slice,
and a registration reads and writes that population's rows alone: its actors'
digests, its blessings, its windows, its counting instant. Registering a
slice's label therefore leaves every SCOTUS row as it was, and the reverse.

These functions edit the registry document and nothing else; the commands in
:mod:`fedcourtsai.cli` read the live digests and write the files.
"""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from .promotion_record import pending_registrations

#: The line in ``process_version.py`` that names the label cells stamp.
LABEL_LINE = re.compile(r'^CURRENT_PROCESS_LABEL = "([^"]+)"$', re.MULTILINE)
#: The SCOTUS docket's population key (``prediction_slices.SCOTUS_POPULATION_KEY``).
SCOTUS = "scotus"
_BOUNDARY_REACH = ("self-represented dockets", "granted dockets", "all", "replay cells")


class RegistrationError(ValueError):
    """A registration the registry cannot take."""


@dataclass(frozen=True)
class LiveActor:
    """One enabled actor and the digest its process computes on this tree."""

    role: str
    actor_id: str
    digest: str
    population: str = SCOTUS


def _pending_instant() -> dict[str, Any]:
    return {"at": None, "merge": None, "source": "merge"}


def _ordinal(label: str, population: str) -> int:
    prefix = "proc" if population == SCOTUS else population
    match = re.fullmatch(re.escape(prefix) + r"-v(\d+)", label)
    if match is None:
        raise RegistrationError(
            f"a process label of population {population!r} is {prefix}-vN, not {label!r}"
        )
    return int(match.group(1))


def _population_of(row: Mapping[str, Any]) -> str:
    return str(row.get("population", SCOTUS))


def register_process(
    registry: Mapping[str, Any],
    label: str,
    actors: Sequence[LiveActor],
    population: str = SCOTUS,
) -> dict[str, Any]:
    """``registry`` with ``label`` registered, pending, over ``population``'s live fleet.

    ``actors`` is every enabled actor; the registration reads those of
    ``population`` and, of the registry, the rows under that population's
    labels. Every other population's rows pass through untouched.

    - the population's ``blessings`` become its live fleet: a digest already
      blessed is carried forward with its bless moment and first label; a new
      one is pending under ``label``;
    - where the **predictor** digests moved (one changed, appeared or left),
      the label gets a pending counting instant as the last label row; each
      predictor digest newly blessed opens a pending window, and each open
      window whose digest no live predictor computes closes pending;
    - where only **evaluator** digests moved, the label holds its
      predecessor's counting instant (its ``since`` is a copy of the
      population's last label's) and opens and closes no window, since an
      evaluator digest records and never partitions;
    - each of the population's live evaluator digests gains ``label`` in
      ``evaluate_blessing_labels``.

    Refuses a registry whose freeze record has not declared merge-stamped
    instants (``merge_stamping_declared``), a label that is not named for the
    population or does not follow its last one, a label registration already
    waiting for its merge, a fleet whose digests have not moved, a digest
    another population's label already blesses, and a population's first label
    with no enabled predictor, since nothing would open its counting window.
    """
    document: dict[str, Any] = copy.deepcopy(dict(registry))
    _refuse_undeclared(document, "label")
    own_labels = [row for row in document["labels"] if _population_of(row) == population]
    _refuse_label(document, label, population, own_labels)
    named = {row["label"] for row in own_labels}
    actors = [actor for actor in actors if actor.population == population]
    others = [blessing for blessing in document["blessings"] if blessing["label"] not in named]
    _refuse_shared_digest(actors, others)
    carried = {
        blessing["digest"]: blessing
        for blessing in document["blessings"]
        if blessing["label"] in named
    }
    blessings: list[dict[str, Any]] = []
    for actor in actors:
        if actor.digest in carried:
            blessings.append(carried[actor.digest])
        else:
            blessings.append(
                {
                    "digest": actor.digest,
                    "role": actor.role,
                    "actor_id": actor.actor_id,
                    "label": label,
                    "blessed": _pending_instant(),
                }
            )
    moved = [blessing for blessing in blessings if blessing["label"] == label]
    if not moved and {b["digest"] for b in blessings} == set(carried):
        raise RegistrationError("no digest moved: a label registers a moved process")
    live_predictors = {actor.digest for actor in actors if actor.role == "predictor"}
    blessed_predictors = {
        blessing["digest"] for blessing in carried.values() if blessing["role"] == "predictor"
    }
    if live_predictors != blessed_predictors:
        _move_windows(document, label, moved, live_predictors, named)
        since = _pending_instant()
    elif own_labels:
        since = dict(own_labels[-1]["since"])
    else:
        raise RegistrationError(
            f"population {population!r} has no enabled predictor: its first label opens "
            "a counting window"
        )
    for actor in actors:
        if actor.role == "evaluator":
            blessed_by = document["evaluate_blessing_labels"].setdefault(actor.digest, [])
            if label not in blessed_by:
                blessed_by.append(label)
    row: dict[str, Any] = {"label": label, "since": since}
    if population != SCOTUS:
        row["population"] = population
    document["labels"].append(row)
    scotus_first = population == SCOTUS
    document["blessings"] = blessings + others if scotus_first else others + blessings
    return document


def _refuse_shared_digest(actors: Sequence[LiveActor], others: Sequence[Mapping[str, Any]]) -> None:
    """Refuse a live digest that another population's label already blesses."""
    foreign = {blessing["digest"]: blessing["label"] for blessing in others}
    for actor in actors:
        if actor.digest in foreign:
            raise RegistrationError(
                f"{actor.role} {actor.actor_id} computes {actor.digest}, which "
                f"{foreign[actor.digest]} blesses for another population: two populations "
                "never share a process"
            )


def _refuse_undeclared(document: Mapping[str, Any], what: str) -> None:
    """Refuse a pending registration before merge-stamped instants are declared."""
    if document.get("merge_stamping_declared") is None:
        raise RegistrationError(
            "no freeze-record entry declares merge-stamped instants "
            f"(merge_stamping_declared is unset); the {what} can be registered only "
            "once main holds that declaration"
        )


def _refuse_label(
    document: Mapping[str, Any],
    label: str,
    population: str,
    own_labels: Sequence[Mapping[str, Any]],
) -> None:
    """Refuse a label already registered, not after its population's last, or behind a pending one.

    Only a pending label, blessing or window blocks a new label, whichever
    population's it is: one label per promotion. A pending harness boundary is
    independent of labels and rides along.
    """
    ordinal = _ordinal(label, population)
    if any(entry["label"] == label for entry in document["labels"]):
        raise RegistrationError(f"{label} is already registered")
    if own_labels and ordinal <= _ordinal(own_labels[-1]["label"], population):
        raise RegistrationError(f"{label} does not follow {own_labels[-1]['label']}")
    if any(stamp.kind != "boundary" for stamp in pending_registrations(document)):
        raise RegistrationError("a label registration is already waiting for its merge")


def _move_windows(
    document: dict[str, Any],
    label: str,
    moved: Sequence[Mapping[str, Any]],
    live_predictors: set[str],
    own_labels: set[str],
) -> None:
    """Close, pending, each of the population's open windows no live predictor computes.

    Then open one per newly blessed digest. ``own_labels`` names the
    population's labels, so another population's window is never closed.
    """
    for window in document["windows"]:
        if (
            window["label"] in own_labels
            and window["closes"] is None
            and window["revoked_at"] is None
            and window["digest"] not in live_predictors
        ):
            window["closes"] = _pending_instant()
    for blessing in moved:
        if blessing["role"] == "predictor":
            document["windows"].append(
                {
                    "label": label,
                    "digest": blessing["digest"],
                    "predictor_id": blessing["actor_id"],
                    "opens": _pending_instant(),
                    "closes": None,
                    "revoked_at": None,
                }
            )


def register_boundary(
    registry: Mapping[str, Any],
    name: str,
    *,
    predictors: Sequence[str] | None,
    reach: str,
    gradual: bool,
) -> dict[str, Any]:
    """``registry`` with a pending harness boundary appended; refuses a reused name.

    Refuses, like :func:`register_process`, a registry whose freeze record has
    not declared merge-stamped instants: nothing would stamp the boundary, so
    no cell would ever have a side of it.
    """
    document: dict[str, Any] = copy.deepcopy(dict(registry))
    _refuse_undeclared(document, "boundary")
    if any(boundary["name"] == name for boundary in document["harness_boundaries"]):
        raise RegistrationError(f"a boundary named {name!r} is already registered")
    if reach not in _BOUNDARY_REACH:
        raise RegistrationError(f"reach is one of {', '.join(_BOUNDARY_REACH)}, not {reach!r}")
    document["harness_boundaries"].append(
        {
            "name": name,
            "merge": None,
            "at": None,
            "predictors": list(predictors) if predictors is not None else None,
            "reach": reach,
            "gradual": gradual,
        }
    )
    return document


def set_current_label(source: str, label: str) -> str:
    """``process_version.py``'s source with ``CURRENT_PROCESS_LABEL`` set to ``label``."""
    if len(LABEL_LINE.findall(source)) != 1:
        raise RegistrationError("process_version.py names CURRENT_PROCESS_LABEL other than once")
    return LABEL_LINE.sub(f'CURRENT_PROCESS_LABEL = "{label}"', source)
