"""Moving a committed event directory to the identity its corpus row carries.

``data/cases/<court>/<docket>/events/<event_id>/`` is the ledger half of an
event, and both halves name the same identity: the directory's own path spells
the case and the event id, and ``event.yaml`` / ``outcome.json`` restate them
inside. A sweep that re-keys the corpus half — a re-derived event id, a case id
merged onto a surviving twin — therefore owes the same move here, or the two
stores disagree about which event the committed definition defines.

The move and the restamp are one operation with a deliberate order and a
deliberate asymmetry: the rename is conditional on the source directory still
being there, the restamp is unconditional on the target's documents. A run
interrupted between the two steps leaves the directory already at the target
with its documents still naming the old identity, and a rewrite hung off the
*source* directory's existence would never revisit that shape — so the restamp
runs whenever the target exists, and the next pass converges it.
"""

from __future__ import annotations

from collections.abc import Mapping

from .paths import EventPaths
from .schemas import Outcome, PredictableEvent
from .serialize import read_model, write_json, write_yaml

# The only files an event directory holds; cell output lives in subdirectories,
# so anything else there is a shape a move must not carry blindly — the
# artifacts under it name their own case and event id inside their own files,
# which no restamp here rewrites.
EVENT_DOCUMENTS = frozenset({"event.yaml", "outcome.json"})


def move_event_directory(old: EventPaths, new: EventPaths, restamp: Mapping[str, str]) -> None:
    """Move ``old`` onto ``new`` and restamp ``restamp``'s fields in both documents.

    ``restamp`` carries the identity fields the move changes (``event_id`` for a
    rename within a case, ``case_id`` for a move between them). Idempotent: see
    the module docstring for why the restamp is unconditional on the target. The
    documents are re-validated rather than ``model_copy``-ed, so every carried
    field normalizes and a future field travels by construction.
    """
    if old.base.is_dir():
        # A rename within one case lands in an `events/` directory that already
        # holds the source; a move *between* cases may be the first thing the
        # target case commits, so its parent has to be made.
        new.base.parent.mkdir(parents=True, exist_ok=True)
        old.base.rename(new.base)
    if new.event_file.is_file():
        event = read_model(new.event_file, PredictableEvent)
        write_yaml(
            new.event_file, PredictableEvent.model_validate({**event.model_dump(), **restamp})
        )
    if new.outcome.is_file():
        outcome = read_model(new.outcome, Outcome)
        write_json(new.outcome, Outcome.model_validate({**outcome.model_dump(), **restamp}))
