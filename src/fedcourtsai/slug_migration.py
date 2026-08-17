"""Converge committed entry-pinned event ids onto the current slug derivation.

An entry-pinned event's id is derived from the docket entry's own text
(:func:`fedcourtsai.pipeline.events.entry_event_id`), and extraction re-runs on
every refresh of the docket that defines it. :func:`fedcourtsai.corpus.upsert_events`
keys on ``(case_id, event_id)``, so a row minted under a superseded derivation
is not *updated* by that re-run: the re-ingest inserts a **second** row under
the id today's rule mints, and the case ends up carrying both. The stale one
keeps the ``resolved`` latch and the committed ledger directory; the new one
arrives open, and nothing closes it — a SCOTUS disposing order cites no docket
entry number, so the resolution latch never reaches it — leaving a permanent
open event that drags a decided case back into the forecast queue.

This sweep is the other half of any change to the derivation: it renames each
committed row whose stored id is not what today's rule derives from its own
stored entry text, in both stores — the corpus row through
:func:`fedcourtsai.corpus.rename_event` (atomic, ``resolved`` latch carried,
casestore events mirror included) and the ledger directory
``data/cases/<court>/<docket>/events/<event_id>/`` by moving it and restamping
the ``event_id`` inside ``event.yaml`` and ``outcome.json``. Deterministic,
offline, idempotent: a converged corpus renames nothing.

**The ledger half goes first.** The corpus row is this sweep's detection handle,
so an interrupted run that already moved the directory is re-found by the next
run and finished as a corpus-only rename, where flipping the row first would
strand the directory under an id nothing scans for again.

The within-case uniqueness suffix is not part of the derivation — it depends on
the docket's *other* entries — so a stored id that is the derived id plus a
numeric suffix is already converged and is left alone. Where the derived id is
already taken, by another row on the case or by a rename this same pass already
planned, the row is reported for triage instead: two stale rows now deriving one
id need the suffix re-assigned between them, which is a maintainer's call rather
than a rename's.

Three ledger shapes are likewise skipped and reported: a directory holding
anything beyond ``event.yaml`` / ``outcome.json`` — committed predict/evaluate
output names the event id inside its own files, which this sweep does not
rewrite — a case where the directories under *both* ids exist (merging them is a
judgement call), and a row whose stored entry text is missing, since the id
cannot be re-derived without it.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from . import corpus
from .paths import CasePaths, EventPaths
from .pipeline.events import entry_event_id
from .schemas import EventKind, Outcome, PredictableEvent
from .serialize import read_model, write_json, write_yaml

# The only files an event directory holds; cell output lives in subdirectories,
# so anything else here is a shape the rename must not carry blindly.
_EVENT_DOCUMENTS = frozenset({"event.yaml", "outcome.json"})

_NO_TEXT_REASON = (
    "the row stores no entry text, so the id today's rules derive for it is unknowable"
)
_TARGET_TAKEN_REASON = (
    "the derived id is already taken on this case, so the two rows need the "
    "within-case uniqueness suffix re-assigned between them"
)
_BOTH_DIRECTORIES_REASON = (
    "ledger directories exist under both the stored and the derived id; merging "
    "them is a judgement call this sweep does not make"
)


@dataclass
class SlugConvergenceResult:
    """What the slug convergence renamed (or would rename on a dry run)."""

    applied: bool = False
    renamed: list[tuple[str, str]] = field(default_factory=list)  # ("<case>/<old>", new event id)
    already_converged: int = 0  # entry-pinned rows already on the current derivation
    skipped: list[tuple[str, str]] = field(default_factory=list)  # (case_id/event_id, reason)


def converge_event_slugs(
    conn: sqlite3.Connection, data_root: Path, *, apply: bool
) -> SlugConvergenceResult:
    """Rename each entry-pinned event whose id the current derivation no longer mints.

    Dry run by default (finds the rows, writes nothing); ``apply`` moves the
    ledger directory and then renames the corpus row, in that order — see the
    module docstring for why the ledger half leads, and for every skip shape.
    ``data_root`` is the git ledger root.
    """
    result = SlugConvergenceResult(applied=apply)
    # The ids this pass has already spoken for, so a dry run reports the second
    # of two rows deriving one id as triage rather than as a rename it could not
    # perform (an `--apply` sees the first rename in the corpus itself).
    claimed: set[tuple[str, str]] = set()
    rows = conn.execute(
        "SELECT case_id, event_id, kind, description FROM events "
        "WHERE docket_entry_id IS NOT NULL ORDER BY case_id, event_id"
    ).fetchall()
    for row in rows:
        case_id, event_id = str(row["case_id"]), str(row["event_id"])
        ref = f"{case_id}/{event_id}"
        text = row["description"]
        if not text:
            result.skipped.append((ref, _NO_TEXT_REASON))
            continue
        derived = entry_event_id(str(text), EventKind(row["kind"]))
        if _is_converged(event_id, derived):
            result.already_converged += 1
            continue
        events = {event.event_id: event for event in corpus.events_for_case(conn, case_id)}
        if derived in events or (case_id, derived) in claimed:
            result.skipped.append((ref, _TARGET_TAKEN_REASON))
            continue
        old_paths = _ledger_event_paths(data_root, case_id, event_id)
        new_paths = _ledger_event_paths(data_root, case_id, derived)
        if old_paths is not None and new_paths is not None:
            reason = _ledger_blocker(old_paths, new_paths)
            if reason is not None:
                result.skipped.append((ref, reason))
                continue
        result.renamed.append((ref, derived))
        claimed.add((case_id, derived))
        if apply:
            if old_paths is not None and new_paths is not None and old_paths.base.is_dir():
                _move_ledger_event(old_paths, new_paths, derived)
            corpus.rename_event(
                conn,
                case_id,
                event_id,
                # Re-validated (not model_copy) so every carried field normalizes
                # and a future CorpusEvent field travels by construction.
                corpus.CorpusEvent.model_validate(
                    {**events[event_id].model_dump(), "event_id": derived}
                ),
            )
    return result


def _is_converged(event_id: str, derived: str) -> bool:
    """Whether ``event_id`` is what the current derivation mints, up to the collision suffix.

    ``extract_events`` appends the entry number to the *second* of two entries
    deriving one id, so ``<derived>-21`` is that id in converged form rather than
    a stale one — the suffix is a property of the docket, not of the derivation.
    """
    if event_id == derived:
        return True
    suffix = event_id.removeprefix(f"{derived}-")
    return suffix != event_id and suffix.isdigit()


def _ledger_blocker(old: EventPaths, new: EventPaths) -> str | None:
    """Why this event's ledger directory must not move, or ``None`` when it may.

    A missing source directory is not a blocker: a corpus row with no committed
    ledger side is renamed on its own, as is one whose directory an interrupted
    earlier run already moved to the target.
    """
    if not old.base.is_dir():
        return None
    if new.base.exists():
        return _BOTH_DIRECTORIES_REASON
    unexpected = sorted(
        child.name for child in old.base.iterdir() if child.name not in _EVENT_DOCUMENTS
    )
    if unexpected:
        return (
            f"the event directory holds more than its two documents ({', '.join(unexpected)}); "
            "committed cell output names this event id inside its own files"
        )
    return None


def _move_ledger_event(old: EventPaths, new: EventPaths, event_id: str) -> None:
    """Move the committed event directory and restamp the id inside its documents."""
    old.base.rename(new.base)
    if new.event_file.is_file():
        event = read_model(new.event_file, PredictableEvent)
        write_yaml(new.event_file, event.model_copy(update={"event_id": event_id}))
    if new.outcome.is_file():
        outcome = read_model(new.outcome, Outcome)
        write_json(new.outcome, outcome.model_copy(update={"event_id": event_id}))


def _ledger_event_paths(data_root: Path, case_id: str, event_id: str) -> EventPaths | None:
    """The committed event directory for ``(case_id, event_id)``, or ``None`` off the form."""
    court, _, docket = case_id.partition("/")
    if not docket.isdigit():
        return None
    return CasePaths(data_root, court, int(docket)).event(event_id)
