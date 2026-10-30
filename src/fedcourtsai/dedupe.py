"""Dedupe of live-minted duplicate SCOTUS rows in the corpus.

The two SCOTUS ingestion channels reconcile identity on the normalized
docket-number string (:func:`corpus.normalize_docket_number`) before minting a
row, and the normalization strips a bracketing ``*** … ***`` annotation exactly
so both channels spell one docket the same way. Pairs minted while that join
missed on the annotated spelling carry the same petition twice — under its
upstream CourtListener docket id and under the live channel's reserved-range id
(:data:`fedcourtsai.supremecourt.LIVE_DOCKET_ID_BASE`). This module removes
those pairs; the normalization closes the join, so the pair set cannot grow.

The keep/drop rule is the one the identity join itself applies when two rows
match (:func:`corpus.scotus_case_id_by_docket_number` — the lowest docket id
wins): the CourtListener-keyed row, the id the rest of the pipeline keys on,
survives. The merge then performs the write the missed join withheld, through
the same tested writers ingestion uses (so the content-store mirror stays in
step): every fact only the live twin carries fills in on the survivor
(keep-side precedence — a value both rows carry keeps the survivor's), the
twin's ``events`` / ``snapshots`` / ``documents`` rows move under the surviving
id (events through the event upsert, whose ``resolved`` latch never regresses;
snapshots and documents fill-in only, since a same-key row already on the
survivor is the fresher write), and the live-minted row is then deleted from
all four tables — no orphan survives. Content-store objects under a dropped id
are left in place: the store's posture is no-delete, and nothing resolves a
case id absent from the corpus index, so they are inert.

A **minted** forecast moment (:func:`fedcourtsai.pipeline.moments.minted_moment_ids`)
owes both halves at its mint, so re-keying its corpus row moves the committed
``data/cases/<court>/<docket>/events/<event_id>/`` directory with it: the row
would otherwise sit under the survivor while its ``event.yaml`` stayed on the
dropped case's path, which is exactly the half-landed shape
``validate-corpus``'s ``minted_moments_defined_in_ledger`` check fails on — and
most minted moments have no re-mint trigger, so nothing would heal it. The
ledger half goes first, before any corpus write: the twin's rows are this
merge's detection handle, so an interrupted pair is re-found and finished by the
next run, where flipping the corpus first would strand the directory under an id
the corpus no longer carries.

A case-level baseline (``evt-petition-disposition``, ``evt-motion-disposition``)
owes no ledger half at the mint — it arrives at first touch or at resolution, so
a *missing* one is no breakage — but a committed one under the dropped id is:
its ``outcome.json`` names the dropped case, and the row delete orphans it into a
``ledger_references_exist`` failure. So a baseline directory moves with its row
exactly as a minted moment's does, and where the survivor already commits its own
definition of the baseline the twin's copy is retired instead, provided the two
outcomes agree on the resolving facts (disposition, grant, resolution date); any
other field only the twin's outcome asserts fills in on the survivor's first, so
the retirement discards nothing. Two disagreeing definitions are a judgement call
and refuse the pair. Committed cell
output anywhere under the dropped id names that id inside `prediction.json` /
`evaluation.json`, which no restamp here rewrites, so a dropped case carrying any
such artifact refuses the whole pair.

The same ledger rule also runs without a pair, over **stranded** directories: a
committed directory under a live-range id the corpus no longer carries, whose
docket number (packed losslessly into the id) resolves to a surviving upstream
row. That is the shape a merge leaves when its corpus half lands and its ledger
half does not — the twin's rows, the pair's detection handle, are gone — so the
sweep re-finds it from the ledger side and finishes the move or the retirement.
Its documents are restamped in place before the rename, so an interrupted
stranded move stays under the live id and is re-found by the next run.

Deterministic and conservative: a pair disagreeing on ``date_filed``,
``date_decided``, or ``disposition`` is reported and never dropped — the
dry-run output is the triage list — and only two-row groups with exactly one
live-minted id are candidates at all, counted after setting aside any upstream
row that asserts none of the disposition, timing or live-poll facts (a
caption-only CourtListener twin, left in place, and only where its docket id is
above the survivor's). Three ledger shapes likewise refuse a
pair whole rather than merge it in part, because a half-merged twin is worse
than an unmerged one: committed cell output under the dropped id (above), a
survivor *already* holding a committed directory for a moment the twin also
committed (two definitions of one moment is a judgement call), and a
survivor-side document that will not read (the interrupted-move question is
then unanswerable, and one bad file must not abort a pass that may already have
written). Each merge step is its own transaction and every step is convergent,
so a run interrupted mid-pair leaves both rows present (the survivor merely
enriched) and a re-run completes it.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

from . import corpus
from .ids import case_id as make_case_id
from .ledger_events import (
    EVENT_DOCUMENTS,
    move_event_directory,
    remove_event_documents,
    restamp_event_documents,
)
from .paths import CasePaths, EventPaths, court_cases_dir
from .pipeline import moments
from .pipeline.ingest import UNSAMPLED_WEIGHT
from .schemas import Outcome, PredictableEvent
from .serialize import read_model, write_json
from .supremecourt import is_live_docket_id, reserved_docket_number


class DuplicatePair(BaseModel):
    """One duplicated SCOTUS docket: a CourtListener-keyed row and its live twin."""

    model_config = ConfigDict(extra="forbid")

    keep: str  # the CourtListener-keyed case_id (docket id below the live range)
    drop: str  # the live-minted case_id (docket id in the reserved range)
    agreed: bool  # date_filed, date_decided and disposition agree (None agrees)
    weight: int  # min of the pair's asserted sample_weights (a NULL asserts nothing)


class SkippedPair(BaseModel):
    """A pair reported for triage and never dropped, with what stopped the merge.

    Two families reach here: a pair whose facts disagree, and a pair whose
    ledger halves cannot be merged mechanically — colliding directories,
    committed cell output on the dropped id, or a document that will not read.
    ``conflicts`` reads as the triage note in every case.
    """

    model_config = ConfigDict(extra="forbid")

    pair: DuplicatePair
    conflicts: list[str]


class LedgerMove(BaseModel):
    """One committed event directory the merge carries onto the survivor."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    from_case: str  # the dropped id the directory sits under
    to_case: str  # the surviving id it belongs under
    # True when the directory is already at the survivor and only its documents
    # need the case id restamped — the half an interrupted run leaves behind.
    restamp_only: bool
    # True when the survivor already commits an agreeing definition of this
    # case-level baseline, so the twin's copy is deleted rather than moved.
    retire: bool = False


class LiveDedupeResult(BaseModel):
    """One dedupe run's outcome — what was (or would be) dropped, and what was not."""

    model_config = ConfigDict(extra="forbid")

    applied: bool
    pairs: int
    dropped: list[str]  # live-minted case_ids removed (or that a dry run would remove)
    skipped: list[SkippedPair]
    ledger_moves: list[LedgerMove]  # performed, or that a dry run would perform
    # Stranded directories (a live-range id the corpus no longer carries) the
    # sweep could not carry, each with its reason; left in place.
    stranded_skipped: list[str] = []


# Columns the field-level merge does not fill generically: identity, the scope
# columns (the eligibility mirror derives from the court predicate, identical on
# both rows, and the exclusion latch is the scope reconcile's to re-decide from
# the merged facts), and the columns with their own merge semantics below — the
# weight (the pair minimum), the max-latched distribution count, the monotonic
# opinion and capital-case bits, the sticky salience selection, and the fill-in
# salience/queue stamps. A plain-bool column can NEVER ride the generic loop —
# `_lacks(False)` is false, so a drop-side True would be silently discarded —
# which is exactly the capital pair shape this merge exists for; the guard test
# in test_dedupe.py holds every plain-bool column to an explicit rule here.
_MERGE_SPECIAL = frozenset(
    {
        "case_id",
        "court",
        "predict_eligible",
        "predict_excluded",
        "sample_weight",
        "distribution_count",
        "has_opinion",
        "capital_case",
        "salience_score",
        "salience_version",
        "salience_selected",
        "predict_queued_at",
        "evaluate_queued_at",
    }
)


_LEDGER_COLLISION_REASON = (
    "committed ledger directories for {event_id} exist under both ids; merging two "
    "definitions of one minted moment is a judgement call this merge does not make"
)
_BASELINE_CONFLICT_REASON = (
    "committed ledger directories for the baseline {event_id} exist under both ids "
    "and do not agree ({detail}); choosing between two definitions is a judgement "
    "call this merge does not make"
)
_CELL_OUTPUT_REASON = (
    "the dropped id's {event_id} directory holds committed cell output ({extra}); "
    "a prediction or evaluation names its own case id inside its own files, which "
    "this merge does not rewrite, and the row delete would orphan it"
)
_UNREADABLE_REASON = (
    "a {event_id} document could not be read ({error}), so whether the survivor's "
    "directory is an interrupted move or an agreeing definition is unknowable here"
)


def _docket_id(case_id: str) -> int | None:
    """The numeric docket id behind a ``<court>/<docket_id>`` case id, or ``None``."""
    tail = case_id.rsplit("/", 1)[-1]
    return int(tail) if tail.isdigit() else None


def _lacks(value: object) -> bool:
    """Whether a field value asserts nothing (``None``, empty string, empty list)."""
    return value is None or value in ("", [])


def _conflicts(keep: corpus.CorpusRow, drop: corpus.CorpusRow) -> list[str]:
    """The pair's disagreeing facts, empty when the pair agrees.

    ``date_filed``, ``date_decided`` and ``disposition`` must agree for a drop
    to be safe; ``None`` on one side counts as agreement toward the richer value
    (the side that carries a value), because a channel that never asserted the
    fact cannot contradict the one that did.
    """
    found: list[str] = []
    for field in ("date_filed", "date_decided", "disposition"):
        keep_val = getattr(keep, field)
        drop_val = getattr(drop, field)
        if keep_val is not None and drop_val is not None and keep_val != drop_val:
            found.append(f"{field}: {keep_val} != {drop_val}")
    return found


#: The docket facts an upstream row must assert at least one of to count as a
#: claim on its petition in :func:`_candidates`.
_STUB_FACTS = (
    "disposition",
    "date_filed",
    "date_decided",
    "date_cert_granted",
    "date_cert_denied",
    "last_live_polled",
)


def _is_stub(conn: sqlite3.Connection, case_id: str) -> bool:
    """Whether an upstream row asserts none of :data:`_STUB_FACTS`."""
    row = corpus.get_row(conn, case_id)
    return row is not None and all(_lacks(getattr(row, field)) for field in _STUB_FACTS)


def _candidates(conn: sqlite3.Connection) -> list[tuple[DuplicatePair, list[str]]]:
    """Every duplicate pair with its conflict list, in normalized-docket order.

    A candidate is a two-row group sharing one normalized docket number, of
    which exactly one id sits in the live-minted reserved range and the other
    below it. Upstream :func:`_is_stub` rows are set aside before the group is
    counted: CourtListener can carry one Supreme Court number under a second
    docket id that asserts none of the disposition, timing or live-poll facts,
    and such a row is no third claim on the petition, so it neither blocks the
    pair nor joins it, and the merge leaves it where it is. The survivor must
    still be the lowest upstream id in the group, the one the identity join
    resolves the number to, so a stub below it leaves the group untouched. Any
    other group shape — two upstream ids that each assert such a fact, two live
    ids, an unparseable id — is not this rule's pattern and is left untouched.
    """
    groups: dict[str, list[str]] = {}
    cur = conn.execute(
        "SELECT case_id, norm_dn(docket_number) AS dn FROM cases "
        "WHERE court = 'scotus' AND norm_dn(docket_number) IS NOT NULL"
    )
    for record in cur:
        groups.setdefault(str(record["dn"]), []).append(str(record["case_id"]))

    found: list[tuple[DuplicatePair, list[str]]] = []
    for dn in sorted(groups):
        case_ids = groups[dn]
        if len(case_ids) < 2:
            continue
        docket_ids = [_docket_id(case_id) for case_id in case_ids]
        if any(docket_id is None for docket_id in docket_ids):
            continue
        stub_ids: list[int] = []
        if len(case_ids) > 2:
            kept: list[tuple[str, int]] = []
            for case_id, docket_id in zip(case_ids, docket_ids, strict=True):
                assert docket_id is not None  # the group was skipped above otherwise
                if not is_live_docket_id(docket_id) and _is_stub(conn, case_id):
                    stub_ids.append(docket_id)
                else:
                    kept.append((case_id, docket_id))
            if len(kept) != 2:
                continue
            case_ids = [case_id for case_id, _ in kept]
            docket_ids = [docket_id for _, docket_id in kept]
        live = [
            case_id
            for case_id, docket_id in zip(case_ids, docket_ids, strict=True)
            if docket_id is not None and is_live_docket_id(docket_id)
        ]
        if len(live) != 1:
            continue
        drop_id = live[0]
        keep_id = next(case_id for case_id in case_ids if case_id != drop_id)
        # The identity join resolves a number to its lowest docket id, so a
        # survivor above a set-aside stub would leave the join pointing at the
        # stub, and the next write for the number would land there.
        keep_docket = _docket_id(keep_id)
        if stub_ids and (keep_docket is None or keep_docket > min(stub_ids)):
            continue
        keep_row = corpus.get_row(conn, keep_id)
        drop_row = corpus.get_row(conn, drop_id)
        if keep_row is None or drop_row is None:  # pragma: no cover — rows just listed
            continue
        conflicts = _conflicts(keep_row, drop_row)
        # The survivor's weight is the pair's minimum — exactly what the
        # ingestion upsert's min-latch lands when two channels weight one row,
        # applied here because the missed join kept that latch from firing. So
        # the petition's inclusion probability is the pair's best (lowest)
        # inverse weight.
        #
        # A NULL is **not** a weight of 1 in that minimum, and this is where the
        # difference bites: the CourtListener-keyed row is the survivor and
        # `pull` never writes the column at all, so reading its NULL as certainty
        # would let every merge strip the live twin's sampled weight — a silent
        # re-weighting of the legacy frame, performed by a de-duplication pass
        # that observed nothing about the block. A NULL asserts nothing and is
        # skipped; the fall-through applies only when neither row asserted.
        asserted = [
            weight
            for weight in (keep_row.sample_weight, drop_row.sample_weight)
            if weight is not None
        ]
        weight = min(asserted) if asserted else UNSAMPLED_WEIGHT
        found.append(
            (
                DuplicatePair(keep=keep_id, drop=drop_id, agreed=not conflicts, weight=weight),
                conflicts,
            )
        )
    return found


def find_live_duplicates(conn: sqlite3.Connection) -> list[DuplicatePair]:
    """Every SCOTUS pair sharing a normalized docket number across the id ranges."""
    return [pair for pair, _ in _candidates(conn)]


def dedupe_live_rows(conn: sqlite3.Connection, data_root: Path, *, apply: bool) -> LiveDedupeResult:
    """Merge each agreed duplicate pair onto its survivor and drop the live twin.

    Dry run by default (reports what would change, writes nothing); ``apply``
    performs the writes. For each agreed pair: move every committed ledger
    directory the dropped id carries onto the survivor's path, restamping the
    case id inside its documents (or retire a baseline copy the survivor already
    defines in agreement); fill the survivor in with
    every fact only the dropped row carries; stamp its ``sample_weight`` with the
    pair's minimum; move the dropped id's ``events`` / ``snapshots`` /
    ``documents`` rows under the surviving id; and delete the dropped ``case_id``
    from all four tables. A disagreeing pair, and one whose ledger half this
    merge cannot carry mechanically (see :func:`_ledger_moves`), is skipped and
    reported, never dropped. Then sweep the **stranded** directories — ledger
    halves a landed corpus merge left under a live-range id the corpus no longer
    carries (:func:`_stranded_moves`) — onto their survivors by the same rule.
    ``data_root`` is the git ledger root. Idempotent — once applied, a second
    run finds no pairs and nothing stranded.
    """
    dropped: list[str] = []
    skipped: list[SkippedPair] = []
    ledger_moves: list[LedgerMove] = []
    for pair, conflicts in _candidates(conn):
        if not pair.agreed:
            skipped.append(SkippedPair(pair=pair, conflicts=conflicts))
            continue
        planned, blocker = _ledger_moves(conn, data_root, pair)
        if blocker is not None:
            skipped.append(SkippedPair(pair=pair, conflicts=[blocker]))
            continue
        dropped.append(pair.drop)
        ledger_moves.extend(planned)
        if apply:
            _apply_pair(conn, pair, data_root, planned)
    stranded, stranded_skipped = _stranded_moves(conn, data_root)
    ledger_moves.extend(stranded)
    if apply:
        for move in stranded:
            _apply_ledger_move(data_root, move, restamp_first=True)
    return LiveDedupeResult(
        applied=apply,
        pairs=len(dropped) + len(skipped),
        dropped=dropped,
        skipped=skipped,
        ledger_moves=ledger_moves,
        stranded_skipped=stranded_skipped,
    )


def _stranded_moves(
    conn: sqlite3.Connection, data_root: Path
) -> tuple[list[LedgerMove], list[str]]:
    """Ledger work for directories a landed merge left under a dropped live id.

    A stranded case is a committed SCOTUS case directory whose docket id sits in
    a live-channel reserved range, whose case id the corpus no longer carries,
    and whose docket number — decoded from the id itself — resolves through the
    identity join to a surviving upstream row. Any other absent case is not this
    rule's shape and is left untouched. Each stranded case is planned by
    :func:`_plan_ledger`; a refusal is reported and leaves the case in place.
    """
    court_dir = court_cases_dir(data_root, "scotus")
    if not court_dir.is_dir():
        return [], []
    planned: list[LedgerMove] = []
    refused: list[str] = []
    for case_dir in sorted(court_dir.iterdir()):
        if not case_dir.is_dir() or not case_dir.name.isdigit():
            continue
        docket_id = int(case_dir.name)
        if not is_live_docket_id(docket_id):
            continue
        drop = make_case_id("scotus", docket_id)
        if corpus.get_row(conn, drop) is not None:
            continue
        keep = corpus.scotus_case_id_by_docket_number(conn, reserved_docket_number(docket_id))
        keep_docket = None if keep is None else _docket_id(keep)
        if keep is None or keep_docket is None or is_live_docket_id(keep_docket):
            continue
        drop_paths = _case_paths(data_root, drop)
        if drop_paths is None:  # pragma: no cover — the id just parsed
            continue
        moves, blocker = _plan_ledger(
            data_root, drop, keep, sorted(_committed_event_ids(drop_paths))
        )
        if blocker is not None:
            refused.append(f"stranded {drop} (survivor {keep}): {blocker}")
            continue
        planned.extend(moves)
    return planned, refused


def _apply_ledger_move(data_root: Path, move: LedgerMove, *, restamp_first: bool = False) -> None:
    """Perform one planned ledger move, restamp or retirement.

    ``restamp_first`` rewrites the documents in place before the rename, for a
    caller with no other handle on an interrupted move: the directory then stays
    under the dropped id until it is fully carried, where that caller re-finds it.
    """
    drop_paths = _case_paths(data_root, move.from_case)
    keep_paths = _case_paths(data_root, move.to_case)
    if drop_paths is None or keep_paths is None:  # pragma: no cover — both ids just parsed
        return
    old = drop_paths.event(move.event_id)
    new = keep_paths.event(move.event_id)
    if move.retire:
        # The survivor takes the twin's extra facts before the twin's copy goes,
        # so a run cut off between the two re-plans the same retirement, whose
        # fill-in then adds nothing.
        _, old_outcome = _read_documents(old)
        _, new_outcome = _read_documents(new)
        if old_outcome is not None and new_outcome is not None:
            filled = _filled_outcome(new_outcome, old_outcome)
            if filled != new_outcome:
                write_json(new.outcome, Outcome.model_validate(filled.model_dump()))
        remove_event_documents(old)
        return
    restamp = {"case_id": move.to_case}
    if restamp_first:
        restamp_event_documents(old, restamp)
    move_event_directory(old, new, restamp)


def _case_paths(data_root: Path, case_id: str) -> CasePaths | None:
    """The committed case directory for ``case_id``, or ``None`` off the id form."""
    court, _, docket = case_id.partition("/")
    if not docket.isdigit():
        return None
    return CasePaths(data_root, court, int(docket))


def _still_names(paths: EventPaths, case_id: str) -> bool:
    """Whether a directory already at the survivor still names the dropped case.

    The interrupted-run shape: a pass that moved the directory and stopped before
    the restamp leaves documents naming a case the corpus is about to stop
    carrying. Nothing else puts the dropped id inside a survivor-side document,
    so this is the whole re-detection rule. Raises whatever the read raises — an
    unreadable document is a triage skip for its pair, decided by the caller,
    never a crash that abandons a pass which has already written.
    """
    named_by_event = (
        paths.event_file.is_file()
        and read_model(paths.event_file, PredictableEvent).case_id == case_id
    )
    return named_by_event or (
        paths.outcome.is_file() and read_model(paths.outcome, Outcome).case_id == case_id
    )


def _committed_cell_output(case_paths: CasePaths) -> tuple[str, list[str]] | None:
    """The first event directory under this case holding committed cell output.

    Scoped to the whole case, not to the moments this merge would move: the row
    delete is what orphans a prediction or an evaluation, and it deletes the
    case id every event of the twin references, and a move carries only the
    event documents, never what sits beside them. Returns ``(event_id, entries)`` for the
    first such directory, or ``None`` when the case carries none.
    """
    if not case_paths.events_dir.is_dir():
        return None
    for event_dir in sorted(case_paths.events_dir.iterdir()):
        if not event_dir.is_dir():
            continue
        extra = sorted(
            child.name for child in event_dir.iterdir() if child.name not in EVENT_DOCUMENTS
        )
        if extra:
            return event_dir.name, extra
    return None


def _ledger_moves(
    conn: sqlite3.Connection, data_root: Path, pair: DuplicatePair
) -> tuple[list[LedgerMove], str | None]:
    """The pair's owed ledger moves, or the reason the whole pair must not merge.

    Covers every event the dropped twin carries in the corpus and every
    directory committed under its path (see :func:`_plan_ledger`).
    """
    drop_paths = _case_paths(data_root, pair.drop)
    if drop_paths is None:  # pragma: no cover — the id just parsed
        return [], None
    event_ids = {event.event_id for event in corpus.events_for_case(conn, pair.drop)}
    event_ids |= _committed_event_ids(drop_paths)
    return _plan_ledger(data_root, pair.drop, pair.keep, sorted(event_ids))


def _committed_event_ids(case_paths: CasePaths) -> set[str]:
    """The event ids with a committed directory under this case."""
    if not case_paths.events_dir.is_dir():
        return set()
    return {child.name for child in case_paths.events_dir.iterdir() if child.is_dir()}


def _plan_ledger(
    data_root: Path, drop: str, keep: str, event_ids: list[str]
) -> tuple[list[LedgerMove], str | None]:
    """The ledger work carrying ``drop``'s committed directories onto ``keep``.

    One entry per event whose committed directory belongs under the survivor:
    a **move** when it is still on the dropped case's path and the survivor has
    none; a **restamp** when it is already at the survivor with documents naming
    the dropped case (an interrupted run's half, which the move helper's
    unconditional restamp finishes); and a **retirement** when both ids commit a
    case-level baseline whose outcomes agree, so the survivor's definition
    stands and the twin's copy goes.

    Four shapes refuse the pair whole rather than merge it in part. Committed
    **cell output anywhere under the dropped case** — a prediction or evaluation
    names its own case id inside its own files, which no restamp here rewrites,
    so the row delete would orphan it into a ``ledger_references_exist``
    failure. Directories under **both** ids for one minted moment, which is two
    committed definitions and a judgement call; and the same for a baseline
    whose two definitions disagree (:func:`_baseline_disagreement`). And a
    survivor-side document that will not read, which leaves the interrupted-move
    question unanswerable: one unreadable file sends its pair to triage instead
    of aborting a pass that may already have written.
    """
    drop_paths = _case_paths(data_root, drop)
    keep_paths = _case_paths(data_root, keep)
    if drop_paths is None or keep_paths is None:  # pragma: no cover — both ids just parsed
        return [], None
    output = _committed_cell_output(drop_paths)
    if output is not None:
        event_id, entries = output
        return [], _CELL_OUTPUT_REASON.format(event_id=event_id, extra=", ".join(entries))
    minted = moments.minted_moment_ids()
    planned: list[LedgerMove] = []
    for event_id in event_ids:
        move = LedgerMove(event_id=event_id, from_case=drop, to_case=keep, restamp_only=False)
        try:
            step, blocker = _plan_event(
                drop_paths.event(event_id), keep_paths.event(event_id), move, event_id in minted
            )
        except (OSError, ValueError, yaml.YAMLError) as error:
            return [], _UNREADABLE_REASON.format(event_id=event_id, error=error)
        if blocker is not None:
            return [], blocker
        if step is not None:
            planned.append(step)
    return planned, None


def _plan_event(
    old: EventPaths, new: EventPaths, move: LedgerMove, minted: bool
) -> tuple[LedgerMove | None, str | None]:
    """One event's step for :func:`_plan_ledger`: ``(step, None)`` or ``(None, reason)``.

    ``(None, None)`` when the event owes nothing. Raises whatever a document
    read raises, for the caller to report.
    """
    if old.base.is_dir():
        if not new.base.exists():
            _read_documents(old)  # an unreadable twin document is triage, not a crash mid-apply
            return move, None
        if minted:
            return None, _LEDGER_COLLISION_REASON.format(event_id=move.event_id)
        detail = _baseline_disagreement(old, new)
        if detail is not None:
            return None, _BASELINE_CONFLICT_REASON.format(event_id=move.event_id, detail=detail)
        return move.model_copy(update={"retire": True}), None
    if _still_names(new, move.from_case):
        return move.model_copy(update={"restamp_only": True}), None
    return None, None


#: The outcome fields two definitions of one baseline must agree on for the
#: twin's copy to be retired in favour of the survivor's.
_RESOLVING_FACTS = ("actual_disposition", "actual_granted", "resolved_at")

#: Identity fields the survivor's outcome never takes from the twin's.
_OUTCOME_IDENTITY = frozenset({"schema_version", "case_id", "event_id"})


def _read_documents(paths: EventPaths) -> tuple[PredictableEvent | None, Outcome | None]:
    """The directory's parsed ``event.yaml`` and ``outcome.json``, either ``None`` if absent."""
    event = read_model(paths.event_file, PredictableEvent) if paths.event_file.is_file() else None
    outcome = read_model(paths.outcome, Outcome) if paths.outcome.is_file() else None
    return event, outcome


def _baseline_disagreement(old: EventPaths, new: EventPaths) -> str | None:
    """Why the twin's baseline copy cannot be retired, or ``None`` when it can.

    The survivor's definition stands when it records the same resolution as the
    twin's (:data:`_RESOLVING_FACTS`), or when the twin records none; any other
    field only the twin's outcome asserts fills in on the survivor's at the
    retirement (:func:`_filled_outcome`), so nothing the twin alone carries is
    discarded. A twin outcome the survivor lacks altogether is likewise not
    discarded: that pair refuses. Raises whatever the read raises.
    """
    _, old_outcome = _read_documents(old)
    _, new_outcome = _read_documents(new)
    if old_outcome is None:
        return None
    if new_outcome is None:
        return "only the dropped id's directory records an outcome"
    differing = [
        field
        for field in _RESOLVING_FACTS
        if getattr(old_outcome, field) != getattr(new_outcome, field)
    ]
    return f"outcomes differ on {', '.join(differing)}" if differing else None


def _filled_outcome(keep: Outcome, drop: Outcome) -> Outcome:
    """The survivor's outcome with every field only the twin's asserts filled in.

    Keep-side precedence, the rule the corpus merge applies to the rows: a field
    the survivor asserts keeps its value, one it lacks takes the twin's. A nested
    block both carry (``signals``, say) fills field by field only when no field
    both assert disagrees — a stamp like a parse label describes its block's
    values, so it is never grafted onto values it did not produce.
    """
    updates: dict[str, Any] = {}
    for name in Outcome.model_fields:
        if name in _OUTCOME_IDENTITY:
            continue
        keep_val = getattr(keep, name)
        drop_val = getattr(drop, name)
        if _lacks(drop_val):
            continue
        if _lacks(keep_val):
            updates[name] = drop_val
        elif isinstance(keep_val, BaseModel) and type(keep_val) is type(drop_val):
            nested = _filled_block(keep_val, drop_val)
            if nested is not None:
                updates[name] = nested
    return keep.model_copy(update=updates) if updates else keep


def _filled_block(keep: BaseModel, drop: BaseModel) -> BaseModel | None:
    """``keep`` with ``drop``'s fields filled in, or ``None`` if they disagree or add nothing."""
    updates: dict[str, Any] = {}
    for name in type(keep).model_fields:
        keep_val = getattr(keep, name)
        drop_val = getattr(drop, name)
        if _lacks(drop_val):
            continue
        if _lacks(keep_val):
            updates[name] = drop_val
        elif keep_val != drop_val:
            return None
    return keep.model_copy(update=updates) if updates else None


def _merged_row(keep: corpus.CorpusRow, drop: corpus.CorpusRow, weight: int) -> corpus.CorpusRow:
    """The survivor with every fact only the dropped twin carries filled in.

    Keep-side precedence: a field the survivor already asserts keeps its value
    (the agreement check guarantees the checked facts match anyway), and a field
    it lacks takes the twin's — so the live channel's signals (the conference
    stamps, the lower-court name, the cert dates) survive the drop. The columns
    with their own semantics merge by them: ``distribution_count`` takes the max
    (proceedings only grow), ``has_opinion`` and ``capital_case`` OR
    (monotonic — the live twin is the only row that could have seen the
    capital marking), ``salience_selected`` stays sticky, the salience score/version and the queue
    stamps fill in, and ``sample_weight`` takes the pair minimum computed by the
    caller.
    """
    updates: dict[str, Any] = {}
    for name in corpus.CorpusRow.model_fields:
        if name in _MERGE_SPECIAL:
            continue
        keep_val = getattr(keep, name)
        drop_val = getattr(drop, name)
        if _lacks(keep_val) and not _lacks(drop_val):
            updates[name] = drop_val
    counts = [c for c in (keep.distribution_count, drop.distribution_count) if c is not None]
    if counts:
        updates["distribution_count"] = max(counts)
    updates["has_opinion"] = keep.has_opinion or drop.has_opinion
    updates["capital_case"] = keep.capital_case or drop.capital_case
    updates["sample_weight"] = weight
    if keep.salience_version is None and drop.salience_version is not None:
        updates["salience_version"] = drop.salience_version
        updates["salience_score"] = drop.salience_score
    if drop.salience_selected and not keep.salience_selected:
        updates["salience_selected"] = True
    for name in ("predict_queued_at", "evaluate_queued_at"):
        if getattr(keep, name) is None and getattr(drop, name) is not None:
            updates[name] = getattr(drop, name)
    return keep.model_copy(update=updates)


def _apply_pair(
    conn: sqlite3.Connection,
    pair: DuplicatePair,
    data_root: Path,
    ledger_moves: list[LedgerMove],
) -> None:
    """Merge one agreed pair onto the survivor, then delete the live twin."""
    keep_row = corpus.get_row(conn, pair.keep)
    drop_row = corpus.get_row(conn, pair.drop)
    if keep_row is None or drop_row is None:  # pragma: no cover — rows just listed
        return
    merged = _merged_row(keep_row, drop_row, pair.weight)

    # The ledger half leads: the twin's corpus rows are this merge's detection
    # handle, so a run interrupted here is re-found and finished by the next one,
    # where a corpus flip first would strand the directory under a dropped id.
    for move in ledger_moves:
        _apply_ledger_move(data_root, move)

    # The salience and queue columns bypass the ingestion upsert (it keeps the
    # stored value — they belong to the salience pass and the queue routing), so
    # converge them directly first; the upsert below then holds them, and the
    # mirrored model matches the database column-for-column.
    with conn:
        conn.execute(
            "UPDATE cases SET salience_score = ?, salience_version = ?, "
            "salience_selected = ?, predict_queued_at = ?, evaluate_queued_at = ? "
            "WHERE case_id = ?",
            (
                merged.salience_score,
                merged.salience_version,
                int(merged.salience_selected),
                merged.predict_queued_at.isoformat() if merged.predict_queued_at else None,
                merged.evaluate_queued_at.isoformat() if merged.evaluate_queued_at else None,
                pair.keep,
            ),
        )
    # The survivor's facts land through the ingestion upsert, so the per-column
    # latches apply (the min-latch lands the pair-minimum weight) and the
    # content-store mirror receives the merged survivor.
    corpus.upsert_rows(conn, [merged])

    drop_events = corpus.events_for_case(conn, pair.drop)
    if drop_events:
        corpus.upsert_events(
            conn, [event.model_copy(update={"case_id": pair.keep}) for event in drop_events]
        )
    keep_dates = {
        str(record["snapshot_date"])
        for record in conn.execute(
            "SELECT snapshot_date FROM snapshots WHERE case_id = ?", (pair.keep,)
        )
    }
    for record in conn.execute(
        "SELECT snapshot_date, payload FROM snapshots WHERE case_id = ?", (pair.drop,)
    ).fetchall():
        snapshot_date = str(record["snapshot_date"])
        if snapshot_date not in keep_dates:
            corpus.upsert_snapshot(
                conn,
                pair.keep,
                date.fromisoformat(snapshot_date),
                json.loads(str(record["payload"])),
            )
    keep_kinds = {document.kind for document in corpus.documents_for_case(conn, pair.keep)}
    moved_documents = [
        document.model_copy(update={"case_id": pair.keep})
        for document in corpus.documents_for_case(conn, pair.drop)
        if document.kind not in keep_kinds
    ]
    if moved_documents:
        corpus.upsert_documents(conn, moved_documents)

    with conn:
        conn.execute("DELETE FROM events WHERE case_id = ?", (pair.drop,))
        conn.execute("DELETE FROM snapshots WHERE case_id = ?", (pair.drop,))
        conn.execute("DELETE FROM documents WHERE case_id = ?", (pair.drop,))
        conn.execute("DELETE FROM cases WHERE case_id = ?", (pair.drop,))
