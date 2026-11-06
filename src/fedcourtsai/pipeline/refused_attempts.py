"""Removal of predict failure facts that record a forward refusal on a resolved event.

The corpus record gate refuses to provision a forward cell whose event the
corpus already records as resolved (``provision-snapshot --refuse-terminal``).
That refusal is designed behaviour, so ``collect`` counts it as a skip rather
than a failure. A fact written for such a refusal anyway is a wrong
``attempt.json``: it is counted against the cell's attempt cap and read by
``successor-disclosures`` as a failed earlier-window attempt, which puts the
cell in the wrong bucket.

The pass removes exactly the facts a maintainer names, one cell per
``court/docket/event/run_id/actor`` id, after reading each one's run log. The
log is the evidence and the list is the decision, so the pass infers nothing
and widens nothing. What it does check is that each named fact *could* be that
shape, and it refuses the whole list if any one could not:

- the cell's run directory holds ``attempt.json`` and nothing else, so no
  prediction, usage record or transcript is deleted with it;
- the fact is a ``predict`` seam ``no_output`` record whose own fields name the
  same cell, because the record gate refuses forward predict cells only, and a
  refused cell ran nothing;
- the event carries a committed ``outcome.json`` resolved on or before the
  run's UTC date, because the gate refuses only an event the corpus already
  records as resolved, and a run that predates the resolution cannot have
  been refused for it.

A staleness-bound refusal (the forward bound) passes all three checks and is a
failure by design, which is why the run log decides what is named and these
checks only rule out what cannot be a refusal on a resolved event.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from .. import ids
from ..paths import CasePaths
from ..schemas import CellFailure, Outcome
from ..serialize import read_model

#: One named cell, court/docket/event/run_id/actor. The grammar is run-repair's
#: cell grammar (`repair_passes.REGRADE_CELL`), which excludes `.` so no field
#: can be a `..` path segment.
CELL = re.compile(r"([a-z0-9-]+)/([0-9]+)/(evt-[a-z0-9-]+)/([0-9]{8}T[0-9]{6}Z)/([a-z0-9-]+)")

ATTEMPT = "attempt.json"


@dataclass(frozen=True)
class AttemptCell:
    """One named predict cell whose failure fact is to be removed."""

    court: str
    docket: int
    event_id: str
    run_id: str
    actor: str

    @property
    def ref(self) -> str:
        return f"{self.court}/{self.docket}/{self.event_id}/{self.run_id}/{self.actor}"


def parse_cell(text: str) -> AttemptCell:
    """The cell a ``court/docket/event/run_id/actor`` id names.

    Raises ``ValueError`` on an id outside the grammar.
    """
    match = CELL.fullmatch(text)
    if match is None:
        raise ValueError(
            f"malformed cell {text!r} (want court/docket/event/run_id/actor, e.g. "
            "scotus/9526000634/evt-brief-response-disposition/20261105T203825Z/claude-baseline)"
        )
    court, docket, event_id, run_id, actor = match.groups()
    return AttemptCell(court, int(docket), event_id, run_id, actor)


@dataclass
class RemovalResult:
    """What the pass removed (or would), and why it refused any named cell."""

    removed: list[Path] = field(default_factory=list)
    refused: list[tuple[str, str]] = field(default_factory=list)


def _fact_refusal(run_dir: Path, cell: AttemptCell) -> str:
    """Why the run directory's fact is not a lone predict no_output record of ``cell``, or ''."""
    if not run_dir.is_dir():
        return "no committed run directory for the cell"
    entries = sorted(p.name for p in run_dir.iterdir())
    if entries != [ATTEMPT]:
        return f"the run directory holds more than {ATTEMPT}: {', '.join(entries)}"
    try:
        fact = read_model(run_dir / ATTEMPT, CellFailure)
    except (ValueError, ValidationError) as exc:
        return f"{ATTEMPT} does not validate: {exc}"
    if fact.seam != "predict" or fact.error_class != "no_output":
        return f"the fact is a {fact.seam} {fact.error_class} record, not a predict no_output one"
    named = (fact.court, fact.docket, fact.event_id, fact.run_id, fact.actor)
    if named != (cell.court, cell.docket, cell.event_id, cell.run_id, cell.actor):
        return f"the fact names a different cell: {'/'.join(str(f) for f in named)}"
    return ""


def _outcome_refusal(outcome_path: Path, run_id: str) -> str:
    """Why the event was not resolved by the run's date, or ''."""
    if not outcome_path.is_file():
        return "the event has no committed outcome, so it was not resolved"
    try:
        outcome = read_model(outcome_path, Outcome)
    except (ValueError, ValidationError) as exc:
        return f"outcome.json does not validate: {exc}"
    run_day = ids.parse_run_id(run_id).date()
    if outcome.resolved_at > run_day:
        return (
            f"the event resolved {outcome.resolved_at.isoformat()}, after the run "
            f"({run_day.isoformat()}), so the run cannot have been refused for it"
        )
    return ""


def _refusal(data_root: Path, cell: AttemptCell) -> str:
    """Why ``cell``'s fact cannot be a refusal on a resolved event, or ''."""
    event = CasePaths(data_root, cell.court, cell.docket).event(cell.event_id)
    return _fact_refusal(event.prediction_dir(cell.actor, cell.run_id), cell) or (
        _outcome_refusal(event.outcome, cell.run_id)
    )


def remove_refused_attempts(
    data_root: Path, cells: list[AttemptCell], *, apply: bool
) -> RemovalResult:
    """Remove each named cell's failure fact, or refuse the whole list.

    All or nothing: if any named cell fails a check, nothing is removed and
    every refusal is reported, so a list is applied whole or corrected whole.
    A cell named twice is removed once. On apply, the emptied run directory
    and any parent emptied with it up to the event directory are
    removed too, so the ledger carries no empty directories.
    """
    result = RemovalResult()
    seen: set[str] = set()
    for cell in cells:
        if cell.ref in seen:
            continue
        seen.add(cell.ref)
        reason = _refusal(data_root, cell)
        if reason:
            result.refused.append((cell.ref, reason))
            continue
        event = CasePaths(data_root, cell.court, cell.docket).event(cell.event_id)
        result.removed.append(event.prediction_attempt(cell.actor, cell.run_id))
    if result.refused or not apply:
        return result
    for path in result.removed:
        path.unlink()
        stop = path.parents[3]  # the event directory, above predictions/<actor>/<run>/
        directory = path.parent
        while directory != stop and not any(directory.iterdir()):
            directory.rmdir()
            directory = directory.parent
    return result
