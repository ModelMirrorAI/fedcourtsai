"""Shared finalize helpers for the matrix workflows.

The matrix stages (``run-predict`` / ``run-evaluate``) used to
have the workflow name a branch and open a PR per cell from this module; that
routing now lives in :mod:`fedcourtsai.collect` (each cell uploads an artifact and
a ``collect`` job opens one PR per run). What remains here is the small piece every
cell still needs before it uploads: the role enum, and the check for whether the
agent actually wrote its own judgment artifact (so a cell that only has the
materialized ``event.yaml`` scaffold is reported as "produced nothing" rather than
committed). The ``finalize-produced`` CLI command wraps it.

Beside it sits the same question asked *forward* rather than backward:
:func:`required_outputs` names every file a finished cell of this role owes,
before the cell has written any of them. The engine watchdog's completion
sentinel (``scripts/engine-watchdog.sh``, armed by the cell workflows through
``fedcourts cell-outputs``) polls that list while the agent runs, so a cell whose
work is done but whose engine step will not conclude can have its step ended with
the output intact instead of destroyed at the job cap. The two are deliberately
different strengths: ``agent_produced_output`` is the one artifact that makes a
cell worth committing at all, while the sentinel's list is the *whole* contract —
it decides that an agent has finished, so anything short of complete has to read
as still working.
"""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from .paths import CasePaths, EventPaths


class FinalizeRole(StrEnum):
    """Which matrix workflow is running; selects role-specific behavior."""

    predict = "predict"
    evaluate = "evaluate"


def agent_produced_output(
    role: FinalizeRole,
    *,
    data_root: Path,
    court: str,
    docket: int,
    event: str,
    actor: str,
    run_id: str,
) -> bool:
    """Whether the agent wrote its own judgment artifact for this cell.

    The predict/evaluate workflows materialize the event's ``event.yaml`` *before*
    the agent runs, so "the working tree changed" is not "the agent produced a
    prediction": a failed agent leaves only that materialized event file. This
    checks for the agent's actual output — the ``prediction.json`` (predict) or any
    ``evaluation.json`` for this evaluator and run (evaluate) — so the cell can
    report whether it produced output rather than uploading only the event
    scaffold.
    """
    events = CasePaths(data_root, court, docket).event(event)
    if role is FinalizeRole.predict:
        return events.prediction(actor, run_id).is_file()
    if role is FinalizeRole.evaluate:
        return any(events.evaluator_dir(actor).glob(f"*/{run_id}/evaluation.json"))
    raise ValueError(f"agent_produced_output is for predict/evaluate, not {role.value}")


def cell_output_root(
    role: FinalizeRole,
    *,
    data_root: Path,
    court: str,
    docket: int,
    event: str,
    actor: str,
    run_id: str,
) -> Path:
    """The one directory a cell of this role writes its own output under.

    The sentinel watches this subtree for *write quiescence*, so it has to cover
    every path :func:`required_outputs` names and nothing an unrelated step
    writes. On evaluate that is the whole evaluator directory rather than the
    run-keyed one: a judge writes per-candidate directories beside its own
    run-keyed files, and the two sit at different depths under it.
    """
    events = CasePaths(data_root, court, docket).event(event)
    if role is FinalizeRole.predict:
        return events.prediction_dir(actor, run_id)
    if role is FinalizeRole.evaluate:
        return events.evaluator_dir(actor)
    raise ValueError(f"cell_output_root is for predict/evaluate, not {role.value}")


def blinded_candidates(*, data_root: Path, court: str, docket: int) -> list[str]:
    """The aliases staged for an evaluate cell to grade, as the agent sees them.

    Read from the staging directory rather than from the alias map, and for the
    reason the map lives outside the tree at all: the cell is told to enumerate
    ``record/blinded/`` and grade what it finds there, so the set the sentinel
    waits for is exactly the set the agent was asked to produce. Reading the map
    instead would make the sentinel disagree with the contract whenever staging
    dropped a candidate.
    """
    staged = CasePaths(data_root, court, docket).blinded_predictions
    if not staged.is_dir():
        return []
    return sorted(entry.name for entry in staged.iterdir() if entry.is_dir())


def required_outputs(
    role: FinalizeRole,
    *,
    data_root: Path,
    court: str,
    docket: int,
    event: str,
    actor: str,
    run_id: str,
    candidates: Sequence[str] = (),
) -> list[Path]:
    """Every file a finished cell of this role owes, whether or not it exists yet.

    The set is the prompt contract's, resolved through :mod:`fedcourtsai.paths` so
    no caller spells a filename:

    * **predict** — ``prediction.json`` (the artifact ``agent_produced_output``
      probes), the two prose documents it points at, and the per-run
      ``retrieval.md`` / ``tooling.json`` the contract asks for every run.
    * **evaluate** — one ``evaluation.json`` + ``evaluation.md`` per staged
      candidate (the per-candidate depth ``agent_produced_output`` globs), plus
      the judge-level ``retrieval.md`` / ``tooling.json`` keyed by evaluator and
      run. Candidates are named under their staging **aliases**, because the
      un-aliasing runs in the cell's tail and the sentinel runs while the agent
      still holds the tree.

    ``flags.json`` is deliberately absent from both: it is written only when a
    cell has something to flag, so requiring it would leave the sentinel unable
    to fire on the ordinary cell. So are ``usage.json`` and ``retrieval_log.json``
    — the harness writes those after the agent is done, which is after the step
    this sentinel exists to conclude.

    An evaluate role with no ``candidates`` raises rather than returning the
    judge-level pair alone. That set is two files a judge can write before it has
    graded anything, so returning it would have this function say "finished" of a
    cell that has done none of its work — the exact inversion the sentinel exists
    to avoid, and one a caller reaches by forgetting an argument.
    """
    events: EventPaths = CasePaths(data_root, court, docket).event(event)
    if role is FinalizeRole.predict:
        return [
            events.prediction(actor, run_id),
            events.reasoning(actor, run_id),
            events.predicted_reasoning(actor, run_id),
            events.prediction_retrieval(actor, run_id),
            events.prediction_tooling(actor, run_id),
        ]
    if role is FinalizeRole.evaluate:
        if not candidates:
            raise ValueError("an evaluate cell's completion set needs its staged candidates")
        paths = [
            events.evaluation_retrieval(actor, run_id),
            events.evaluation_tooling(actor, run_id),
        ]
        for candidate in candidates:
            paths.append(events.evaluation(actor, candidate, run_id))
            paths.append(events.evaluation_notes(actor, candidate, run_id))
        return paths
    raise ValueError(f"required_outputs is for predict/evaluate, not {role.value}")


# --- a clean slate between in-step engine attempts ------------------------------
#
# The cell workflows' gemini step retries a transient fault in place
# (`scripts/gemini-cell.sh`), and a retried attempt must start from the state the
# first one did: a half-written `reasoning.md` the failed attempt left behind
# would otherwise be read — by the retry, by the completion sentinel, and by the
# tail — as the cell's own output. So the step records what the output root held
# before the first attempt, and resets it to exactly that before each retry.


@dataclass(frozen=True)
class OutputSnapshot:
    """What a cell's output root held before its first engine attempt.

    ``entries`` are root-relative POSIX paths of every file, directory and
    symlink under the root; ``existed`` says whether the root itself was there
    (a predict cell's run-keyed directory is not; an evaluate cell's evaluator
    directory may be, holding earlier runs' committed work).
    """

    root: Path
    existed: bool
    entries: frozenset[str]

    def to_json(self) -> str:
        return json.dumps(
            {"root": str(self.root), "existed": self.existed, "entries": sorted(self.entries)},
            indent=2,
        )

    @classmethod
    def from_json(cls, text: str) -> OutputSnapshot:
        raw = json.loads(text)
        if not isinstance(raw, dict):
            raise ValueError("an output snapshot is a JSON object")
        root, existed, entries = raw.get("root"), raw.get("existed"), raw.get("entries")
        if not isinstance(root, str) or not os.path.isabs(root):
            raise ValueError("an output snapshot names its root as an absolute path")
        if not isinstance(existed, bool):
            raise ValueError("an output snapshot says whether its root existed")
        if not isinstance(entries, list) or not all(isinstance(e, str) for e in entries):
            raise ValueError("an output snapshot lists its entries as strings")
        return cls(root=Path(root), existed=existed, entries=frozenset(entries))


def _walk_entries(root: Path) -> set[str]:
    """Every entry under ``root``, root-relative, never following a symlink."""
    found: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(dirpath)
        for name in [*dirnames, *filenames]:
            found.add((base / name).relative_to(root).as_posix())
    return found


def _refuse_a_linked_root(root: Path) -> None:
    """Refuse a root reached through a symlink anywhere along its path.

    The reset deletes what it did not record, so it must act on the directory
    the cell's path names and on nothing a link could redirect it to.
    """
    if root.resolve() != root:
        raise ValueError(f"{root} is reached through a symlink; refusing to act on it")


def snapshot_output_root(root: Path) -> OutputSnapshot:
    """Record what ``root`` holds now, before an engine attempt writes to it."""
    absolute = Path(os.path.abspath(root))
    if absolute.is_symlink() or (absolute.exists() and not absolute.is_dir()):
        raise ValueError(f"{root} exists and is not a plain directory")
    if not absolute.exists():
        return OutputSnapshot(root=absolute, existed=False, entries=frozenset())
    _refuse_a_linked_root(absolute)
    return OutputSnapshot(root=absolute, existed=True, entries=frozenset(_walk_entries(absolute)))


def reset_output_root(snapshot: OutputSnapshot) -> list[str]:
    """Remove every entry under the snapshot's root that the snapshot did not hold.

    Returns the removed paths, root-relative and sorted (``.`` for the root
    itself). A file or symlink is unlinked, never followed; a directory the
    snapshot did not hold is removed whole, since nothing under it can be an
    entry the snapshot did. An entry the snapshot held is left as it is, even if
    an attempt rewrote it — restoring content is not this function's to do, and
    the collect job's add-only path jail already refuses a cell that edited an
    existing file. A root the snapshot says did not exist is removed entirely.
    """
    root = snapshot.root
    if root.is_symlink():
        if snapshot.existed:
            raise ValueError(f"{root} became a symlink; refusing to reset it")
        root.unlink()
        return ["."]
    if not root.exists():
        return []
    _refuse_a_linked_root(root)
    if not snapshot.existed:
        shutil.rmtree(root)
        return ["."]
    removed: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        base = Path(dirpath)
        kept: list[str] = []
        for name in dirnames:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if relative in snapshot.entries:
                kept.append(name)
                continue
            if path.is_symlink():
                path.unlink()
            else:
                shutil.rmtree(path)
            removed.append(relative)
        # Pruned in place, so the walk never descends into what was just removed.
        dirnames[:] = kept
        for name in filenames:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if relative not in snapshot.entries:
                path.unlink()
                removed.append(relative)
    return sorted(removed)
