"""Back-fill committed ``event.yaml`` definitions from the corpus event row.

A committed ``event.yaml`` is never rewritten by a cell: ``materialize-event``
leaves an existing file standing and warns, field by field, where the corpus
projection has moved away from it. The outcome writer rewrites the definition
from the corpus at resolution, so an event resolved through it converges on its
own. Two populations do not:

* **Definitions written before the moment axis existed.** They carry no
  ``stage`` and no ``moment``, and many of them were resolved by a lane that
  never rewrote the definition, so nothing ever will. The corpus row carries
  both.
* **Interim arrival definitions dated by docketing.** The interim arrival
  moment is dated from the docket's own submission entry (the 2026-09-02
  freeze-record entry), and the corpus row carries that date, while a
  definition committed before the rule still says the docketing date.

This pass carries the corpus row's ``stage``, ``moment`` and ``opened_at`` onto
the committed file, under rules that keep it from moving anything already
scored or anything a cell is cut on:

* **``stage`` and ``moment`` are fill-only.** A null is filled from the corpus;
  a recorded value that differs is a conflict, reported and never overwritten,
  because which side is right is then a question rather than a back-fill.
* **A fill that re-keys a scored cell is held back.** The scored joins read an
  unrecorded stage and moment through
  :func:`fedcourtsai.store.normalized_stage` and
  :func:`fedcourtsai.store.normalized_moment`, so a fill that agrees with that
  reading (a petition baseline's ``cert`` / ``distribution``) moves no figure.
  One that does not agree, on a case carrying a committed evaluation, would move
  a graded cell between board blocks, so it is reported instead.
* **``opened_at`` is rewritten on resolved events only, and only where no event
  of the case carries a committed evaluation.** On an open event the
  definition is what the next cell reads, and the outcome writer rewrites it
  from the corpus at resolution anyway; the cut itself is computed from the
  corpus row (:func:`fedcourtsai.provision.moment_cutoff`), never from this
  file, so leaving it moves no cut. On a scored case the committed date is read
  by the claim set-aside (the response-requested moment's ``opened_at`` dates
  an increment claim's signal), so a rewrite there could move a graded figure.
  The corpus side is the right one where the two differ: it is the registered
  rule.
* **A corpus row that records nothing for a field leaves the committed value
  standing.** A back-fill never erases.

Dry-run by default. ``apply=True`` requires ``max_rewrites``, the number of
files the dry run said it would rewrite, and refuses above it with nothing
written: the population is finite and does not grow (the outcome writer and
the cell projection write every new definition with all three fields), so a
larger count means the predicate widened. Every model is built and validated
before the first write. The corpus is only read.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Literal

import yaml

from . import corpus
from .schemas import Moment, PredictableEvent, Stage
from .serialize import read_model, write_yaml
from .store import normalized_moment, normalized_stage

#: The definition fields this pass carries from the corpus row, in ledger order.
BACKFILLED_FIELDS: tuple[str, ...] = ("stage", "moment", "opened_at")

HoldReason = Literal["conflict", "corpus-null", "re-keys-scored", "open-event", "scored-case"]

#: What each hold reason means, printed beside the counts so the ledger reads alone.
HOLD_REASONS: dict[HoldReason, str] = {
    "conflict": "the committed value is recorded and differs from the corpus; "
    "stage and moment are fill-only",
    "corpus-null": "the corpus row records nothing for the field; a back-fill never erases",
    "re-keys-scored": "the fill moves the event's normalized stage/moment and the case "
    "carries a committed evaluation, so a graded cell would change board block",
    "open-event": "the event is open; the outcome writer rewrites its definition from "
    "the corpus at resolution, and the cut is computed from the corpus row",
    "scored-case": "an event of the case carries a committed evaluation, and the "
    "committed opened_at is read by the claim set-aside",
}

FieldValue = Stage | Moment | date | None


def _text(value: FieldValue) -> str:
    """One field value as the ledger prints it."""
    if value is None:
        return "null"
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


@dataclass(frozen=True)
class FieldChange:
    """One field of one committed definition, as found and as the corpus has it."""

    name: str
    was: FieldValue
    now: FieldValue

    def render(self) -> str:
        return f"{self.name} {_text(self.was)} -> {_text(self.now)}"


@dataclass(frozen=True)
class DefinitionRewrite:
    """One committed ``event.yaml`` the pass rewrites, and the fields it moves."""

    path: Path
    case_id: str
    event_id: str
    kind: str
    resolved: bool
    changes: tuple[FieldChange, ...]

    @property
    def ref(self) -> str:
        return f"{self.case_id} {self.event_id}"

    @property
    def fields(self) -> tuple[str, ...]:
        return tuple(change.name for change in self.changes)


@dataclass(frozen=True)
class HeldChange:
    """One field the pass found drifted and leaves as committed, and why."""

    case_id: str
    event_id: str
    change: FieldChange
    reason: HoldReason

    @property
    def ref(self) -> str:
        return f"{self.case_id} {self.event_id}"


@dataclass
class EventDefinitionBackfillResult:
    """The ledger of one run: what was found, what moves, what is held back."""

    committed: int = 0
    no_corpus_row: list[str] = field(default_factory=list)
    unreadable: list[str] = field(default_factory=list)
    rewrites: list[DefinitionRewrite] = field(default_factory=list)
    held: list[HeldChange] = field(default_factory=list)
    refused: bool = False
    applied: bool = False

    def field_counts(self) -> Counter[str]:
        """How many rewrites move each field."""
        return Counter(name for rewrite in self.rewrites for name in rewrite.fields)

    def held_counts(self) -> Counter[HoldReason]:
        """How many held fields fall under each reason."""
        return Counter(held.reason for held in self.held)

    def fill_populations(self) -> Counter[tuple[str, str, str, str]]:
        """Stage/moment rewrites grouped by ``(kind, stage, moment, open|resolved)``.

        The bulk of the class is one shape, the pre-moment petition baseline, so
        the ledger states the shapes and their counts and lists the files in
        the log rather than putting thousands of identical lines in a summary.
        """
        populations: Counter[tuple[str, str, str, str]] = Counter()
        for rewrite in self.rewrites:
            moved = {c.name: c.now for c in rewrite.changes if c.name in ("stage", "moment")}
            if moved:
                populations[
                    (
                        rewrite.kind,
                        _text(moved.get("stage")) if "stage" in moved else "(kept)",
                        _text(moved.get("moment")) if "moment" in moved else "(kept)",
                        "resolved" if rewrite.resolved else "open",
                    )
                ] += 1
        return populations


def _case_carries_evaluations(case_dir: Path) -> bool:
    """Whether any event of the case holds a committed evaluation directory."""
    events_dir = case_dir / "events"
    return events_dir.is_dir() and any(path.is_dir() for path in events_dir.glob("*/evaluations"))


def _normalized(event: PredictableEvent) -> tuple[Stage | None, Moment | None]:
    """The (stage, moment) the scored joins read this definition as."""
    stage = normalized_stage(event.kind, event.stage)
    return stage, normalized_moment(stage, event.moment)


Assessment = tuple[list[FieldChange], list[tuple[FieldChange, HoldReason]]]


def _assess_stage_moment(
    committed: PredictableEvent, target: PredictableEvent, *, scored_case: bool
) -> Assessment:
    """The fill-only rule on ``stage`` and ``moment``, with the scored-cell hold."""
    held: list[tuple[FieldChange, HoldReason]] = []
    fills: list[FieldChange] = []
    for name in ("stage", "moment"):
        was, now = getattr(committed, name), getattr(target, name)
        if was == now:
            continue
        change = FieldChange(name, was, now)
        if now is None:
            held.append((change, "corpus-null"))
        elif was is not None:
            held.append((change, "conflict"))
        else:
            fills.append(change)
    if not fills:
        return [], held
    filled = committed.model_copy(update={c.name: c.now for c in fills})
    if scored_case and _normalized(filled) != _normalized(committed):
        return [], held + [(change, "re-keys-scored") for change in fills]
    return fills, held


def _assess_opened_at(
    committed: PredictableEvent,
    target: PredictableEvent,
    *,
    row_resolved: bool,
    scored_case: bool,
) -> Assessment:
    """``opened_at`` on resolved events of unscored cases only."""
    if committed.opened_at == target.opened_at:
        return [], []
    change = FieldChange("opened_at", committed.opened_at, target.opened_at)
    reason: HoldReason | None = None
    if target.opened_at is None:
        reason = "corpus-null"
    elif not (committed.resolved and row_resolved):
        reason = "open-event"
    elif scored_case:
        reason = "scored-case"
    return ([], [(change, reason)]) if reason is not None else ([change], [])


def _assess(
    committed: PredictableEvent, row: corpus.CorpusEvent, *, scored_case: bool
) -> Assessment:
    """The field changes one definition takes, and the drifted fields it keeps."""
    # Validate the corpus values through the ledger model, so the comparison is
    # between like types (the corpus row carries plain strings for its enums).
    target = PredictableEvent.model_validate(
        {
            **committed.model_dump(),
            "stage": row.stage,
            "moment": row.moment,
            "opened_at": row.opened_at,
        }
    )
    moves, held = _assess_stage_moment(committed, target, scored_case=scored_case)
    date_moves, date_held = _assess_opened_at(
        committed, target, row_resolved=row.resolved, scored_case=scored_case
    )
    return moves + date_moves, held + date_held


def _read_committed(
    data_root: Path, result: EventDefinitionBackfillResult
) -> dict[tuple[str, str], tuple[Path, PredictableEvent]]:
    """Every readable committed definition by ``(case_id, event_id)``; counts into ``result``."""
    committed: dict[tuple[str, str], tuple[Path, PredictableEvent]] = {}
    for path in sorted((data_root / "cases").glob("*/*/events/*/event.yaml")):
        result.committed += 1
        try:
            event = read_model(path, PredictableEvent)
        except (OSError, ValueError, yaml.YAMLError):
            result.unreadable.append(path.relative_to(data_root).as_posix())
            continue
        committed[(event.case_id, event.event_id)] = (path, event)
    return committed


def _corpus_rows(
    conn: corpus.ReadConnection, keys: Iterable[tuple[str, str]]
) -> dict[tuple[str, str], corpus.CorpusEvent]:
    """The corpus event row of each key that has one, one table scan per court."""
    wanted = set(keys)
    rows: dict[tuple[str, str], corpus.CorpusEvent] = {}
    for court in sorted({case_id.partition("/")[0] for case_id, _ in wanted}):
        for row in corpus.iter_court_events(conn, court=court):
            key = (row.case_id, row.event_id)
            if key in wanted:
                rows[key] = row
    return rows


def backfill_event_definitions(
    conn: corpus.ReadConnection,
    data_root: Path,
    *,
    apply: bool = False,
    max_rewrites: int | None = None,
) -> EventDefinitionBackfillResult:
    """Compare every committed ``event.yaml`` with its corpus row; on apply, rewrite.

    ``apply`` without ``max_rewrites`` raises: the bound is the count the
    maintainer read off the dry run. Above it the result comes back
    ``refused`` and nothing is written.
    """
    if apply and max_rewrites is None:
        raise ValueError("apply requires max_rewrites, the count read off the dry run")
    result = EventDefinitionBackfillResult()
    committed = _read_committed(data_root, result)
    rows = _corpus_rows(conn, committed)
    scored: dict[Path, bool] = {}
    planned: list[tuple[Path, PredictableEvent]] = []
    for key in sorted(committed):
        path, event = committed[key]
        row = rows.get(key)
        if row is None:
            result.no_corpus_row.append(f"{key[0]} {key[1]}")
            continue
        case_dir = path.parent.parent.parent
        if case_dir not in scored:
            scored[case_dir] = _case_carries_evaluations(case_dir)
        moves, held = _assess(event, row, scored_case=scored[case_dir])
        result.held.extend(
            HeldChange(event.case_id, event.event_id, change, reason) for change, reason in held
        )
        if not moves:
            continue
        rewritten = PredictableEvent.model_validate(
            {**event.model_dump(), **{change.name: change.now for change in moves}}
        )
        result.rewrites.append(
            DefinitionRewrite(
                path=path,
                case_id=event.case_id,
                event_id=event.event_id,
                kind=str(event.kind),
                resolved=event.resolved,
                changes=tuple(sorted(moves, key=lambda c: BACKFILLED_FIELDS.index(c.name))),
            )
        )
        planned.append((path, rewritten))
    if not apply:
        return result
    assert max_rewrites is not None
    if len(planned) > max_rewrites:
        result.refused = True
        return result
    for path, rewritten in planned:
        write_yaml(path, rewritten)
    result.applied = True
    return result
