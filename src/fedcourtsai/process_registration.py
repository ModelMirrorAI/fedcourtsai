"""Pending registrations: the edits a PR makes to the registry when it moves the process.

A label is named by hand in the PR that moves a digest, and registered here as
**pending** rows: the label's counting instant, each newly blessed digest's
bless moment, each window the label opens and each window it closes, all with
``at`` and ``merge`` null. The merge that carries the PR to ``main`` stamps
them with its own SHA and committer time
(:mod:`fedcourtsai.promotion_record`). A harness boundary is registered the
same way, in the PR that makes the change.

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
_LABEL = re.compile(r"proc-v(\d+)")
_BOUNDARY_REACH = ("self-represented dockets", "granted dockets", "all", "replay cells")


class RegistrationError(ValueError):
    """A registration the registry cannot take."""


@dataclass(frozen=True)
class LiveActor:
    """One enabled actor and the digest its process computes on this tree."""

    role: str
    actor_id: str
    digest: str


def _pending_instant() -> dict[str, Any]:
    return {"at": None, "merge": None, "source": "merge"}


def _ordinal(label: str) -> int:
    match = _LABEL.fullmatch(label)
    if match is None:
        raise RegistrationError(f"a process label is proc-vN, not {label!r}")
    return int(match.group(1))


def register_process(
    registry: Mapping[str, Any], label: str, actors: Sequence[LiveActor]
) -> dict[str, Any]:
    """``registry`` with ``label`` registered, pending, over the live fleet's digests.

    - ``blessings`` becomes the live fleet: a digest already blessed is carried
      forward with its bless moment and first label; a new one is pending
      under ``label``;
    - where the **predictor** digests moved (one changed, appeared or left),
      the label gets a pending counting instant as the last label row; each
      predictor digest newly blessed opens a pending window, and each open
      window whose digest no live predictor computes closes pending;
    - where only **evaluator** digests moved, the label holds its
      predecessor's counting instant (its ``since`` is a copy of the last
      label's) and opens and closes no window, since an evaluator digest
      records and never partitions;
    - each live evaluator digest gains ``label`` in ``evaluate_blessing_labels``.

    Refuses a registry whose freeze record has not declared merge-stamped
    instants (``merge_stamping_declared``), a label that does not follow the
    last one, a label registration already waiting for its merge, and a fleet
    whose digests have not moved.
    """
    document: dict[str, Any] = copy.deepcopy(dict(registry))
    if document.get("merge_stamping_declared") is None:
        raise RegistrationError(
            "no freeze-record entry declares merge-stamped instants "
            "(merge_stamping_declared is unset); register the label by hand"
        )
    _refuse_label(document, label)
    carried = {blessing["digest"]: blessing for blessing in document["blessings"]}
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
        _move_windows(document, label, moved, live_predictors)
        since = _pending_instant()
    else:
        since = dict(document["labels"][-1]["since"])
    for actor in actors:
        if actor.role == "evaluator":
            named = document["evaluate_blessing_labels"].setdefault(actor.digest, [])
            if label not in named:
                named.append(label)
    document["labels"].append({"label": label, "since": since})
    document["blessings"] = blessings
    return document


def _refuse_label(document: Mapping[str, Any], label: str) -> None:
    """Refuse a label already registered, not after the last, or behind a pending one.

    Only a pending label, blessing or window blocks a new label; a pending
    harness boundary is independent of labels and rides along.
    """
    labels = document["labels"]
    ordinal = _ordinal(label)
    if any(entry["label"] == label for entry in labels):
        raise RegistrationError(f"{label} is already registered")
    if labels and ordinal <= _ordinal(labels[-1]["label"]):
        raise RegistrationError(f"{label} does not follow {labels[-1]['label']}")
    if any(stamp.kind != "boundary" for stamp in pending_registrations(document)):
        raise RegistrationError("a label registration is already waiting for its merge")


def _move_windows(
    document: dict[str, Any],
    label: str,
    moved: Sequence[Mapping[str, Any]],
    live_predictors: set[str],
) -> None:
    """Close, pending, each open window no live predictor computes; open one per new digest."""
    for window in document["windows"]:
        if (
            window["closes"] is None
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
    """``registry`` with a pending harness boundary appended; refuses a reused name."""
    document: dict[str, Any] = copy.deepcopy(dict(registry))
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
