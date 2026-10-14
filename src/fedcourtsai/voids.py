"""The event void: which single events are de-counted, and the predicate every reader asks.

An event is voided when its committed outcome records a different petition than
the one the event was opened on — the Court re-docketed its number, or the ingest
attached another docket's disposition. The rule, its admissibility criteria and
what a void owes are in ``docs/process-version.md`` (*Voiding an event*); each
void is a row in ``voided_events.json`` beside a dated ``docs/freeze-record.md``
entry. This module is small and code-owned on purpose: it holds the one predicate
(:func:`is_voided`) that every scored surface, the evaluate backlog and the export
route through, so a change to what a void reaches is a reviewed change here.
"""

from __future__ import annotations

from collections.abc import Mapping
from importlib.resources import files
from types import MappingProxyType
from typing import Final

from .schemas import Evaluation, VoidedEvent, VoidedEventsRegistry

#: The voided-events registry: a code-owned data file, so a void is a reviewed,
#: maintainer-merged edit to one file; append-only, since a removed row would
#: re-count gradings a dated entry withdrew.
VOIDED_EVENTS_RESOURCE = "voided_events.json"


def load_voided_events(text: str | None = None) -> Mapping[tuple[str, str], VoidedEvent]:
    """The voided events keyed ``(case_id, event_id)``; ``text`` overrides the packaged file.

    Refuses an event registered twice: one key, one dated void.
    """
    raw = (
        text
        if text is not None
        else files("fedcourtsai").joinpath(VOIDED_EVENTS_RESOURCE).read_text(encoding="utf-8")
    )
    registry = VoidedEventsRegistry.model_validate_json(raw)
    voided: dict[tuple[str, str], VoidedEvent] = {}
    for event in registry.events:
        key = (event.case_id, event.event_id)
        if key in voided:
            raise ValueError(f"voided_events.json registers {key[0]} {key[1]} twice")
        voided[key] = event
    return MappingProxyType(voided)


#: The registry as loaded at import; :func:`is_voided` reads it.
VOIDED_EVENTS: Final[Mapping[tuple[str, str], VoidedEvent]] = load_voided_events()

#: The reason prefix recorded against a cell a voided event drops; the event's
#: own stated defect follows it.
VOIDED_EXCLUSION_REASON = "the event is voided — its outcome describes another petition"


def is_voided(case_id: str, event_id: str) -> bool:
    """Whether this event is voided — the one predicate every void-aware reader asks."""
    return (case_id, event_id) in VOIDED_EVENTS


def voided_reason(evaluation: Evaluation) -> str | None:
    """Why this grading's event is voided, or ``None`` where it is not.

    A voided event's gradings leave every scored figure — every stratum, rank
    key, claim score, composition count and export row — because the outcome
    they were scored against is not the forecast subject's. Like the leakage
    rule it changes membership and never a value: no score on any record is
    touched, and the boards publish how many gradings it dropped.
    """
    if not is_voided(evaluation.case_id, evaluation.event_id):
        return None
    entry = VOIDED_EVENTS[(evaluation.case_id, evaluation.event_id)]
    return f"{VOIDED_EXCLUSION_REASON} ({entry.defect}; freeze record {entry.declared.isoformat()})"
