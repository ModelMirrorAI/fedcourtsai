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
    restamp_event_documents(new, restamp)


def restamp_event_documents(paths: EventPaths, restamp: Mapping[str, str]) -> None:
    """Rewrite ``restamp``'s fields into the directory's ``event.yaml`` and ``outcome.json``.

    Either document may be absent; an absent one is left absent. Re-validated
    rather than ``model_copy``-ed, so every carried field normalizes.
    """
    if paths.event_file.is_file():
        event = read_model(paths.event_file, PredictableEvent)
        write_yaml(
            paths.event_file, PredictableEvent.model_validate({**event.model_dump(), **restamp})
        )
    if paths.outcome.is_file():
        outcome = read_model(paths.outcome, Outcome)
        write_json(paths.outcome, Outcome.model_validate({**outcome.model_dump(), **restamp}))


def remove_event_documents(paths: EventPaths) -> None:
    """Delete an event directory that holds only :data:`EVENT_DOCUMENTS`.

    Refuses (``ValueError``) a directory holding anything else, since cell
    output under it is a judgment no caller here may discard. The emptied
    ``events/`` and case directories go too, so no bare shell is left behind.
    """
    if not paths.base.is_dir():
        return
    extra = sorted(
        child.name for child in paths.base.iterdir() if child.name not in EVENT_DOCUMENTS
    )
    if extra:
        raise ValueError(f"{paths.base} holds more than its documents: {', '.join(extra)}")
    for name in sorted(EVENT_DOCUMENTS):
        (paths.base / name).unlink(missing_ok=True)
    paths.base.rmdir()
    for parent in (paths.base.parent, paths.base.parent.parent):
        if parent.is_dir() and not any(parent.iterdir()):
            parent.rmdir()
