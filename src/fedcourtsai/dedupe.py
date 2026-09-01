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

A case-level baseline is not moved — its ledger half is owed at first touch or
at resolution rather than at the mint, so a missing one is no breakage — but a
baseline *directory* is not therefore free to ignore: committed cell output
anywhere under the dropped id names that id inside `prediction.json` /
`evaluation.json`, which no restamp here rewrites, so the row delete would
orphan it into a ``ledger_references_exist`` failure. A dropped case carrying
any such artifact refuses the whole pair.

Deterministic and conservative: a pair disagreeing on ``date_filed``,
``date_decided``, or ``disposition`` is reported and never dropped — the
dry-run output is the triage list — and only exact two-row groups with exactly
one live-minted id are candidates at all. Three ledger shapes likewise refuse a
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
from .ledger_events import EVENT_DOCUMENTS, move_event_directory
from .paths import CasePaths, EventPaths
from .pipeline import moments
from .pipeline.ingest import UNSAMPLED_WEIGHT
from .schemas import Outcome, PredictableEvent
from .serialize import read_model
from .supremecourt import is_live_docket_id


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


class LiveDedupeResult(BaseModel):
    """One dedupe run's outcome — what was (or would be) dropped, and what was not."""

    model_config = ConfigDict(extra="forbid")

    applied: bool
    pairs: int
    dropped: list[str]  # live-minted case_ids removed (or that a dry run would remove)
    skipped: list[SkippedPair]
    ledger_moves: list[LedgerMove]  # performed, or that a dry run would perform


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
_CELL_OUTPUT_REASON = (
    "the dropped id's {event_id} directory holds committed cell output ({extra}); "
    "a prediction or evaluation names its own case id inside its own files, which "
    "this merge does not rewrite, and the row delete would orphan it"
)
_UNREADABLE_REASON = (
    "the survivor's {event_id} document could not be read ({error}), so whether it "
    "still names the dropped case — the interrupted-move shape — is unknowable here"
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


def _candidates(conn: sqlite3.Connection) -> list[tuple[DuplicatePair, list[str]]]:
    """Every duplicate pair with its conflict list, in normalized-docket order.

    A candidate is an exact two-row group sharing one normalized docket number,
    of which exactly one id sits in the live-minted reserved range and the
    other below it. Any other group shape — three-plus rows, two upstream ids,
    two live ids, an unparseable id — is not this rule's pattern and is left
    untouched.
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
        if len(case_ids) != 2:
            continue
        docket_ids = [_docket_id(case_id) for case_id in case_ids]
        if any(docket_id is None for docket_id in docket_ids):
            continue
        live = [
            case_id
            for case_id, docket_id in zip(case_ids, docket_ids, strict=True)
            if docket_id is not None and is_live_docket_id(docket_id)
        ]
        if len(live) != 1:
            continue
        drop_id = live[0]
        keep_id = next(case_id for case_id in case_ids if case_id != drop_id)
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
    performs the writes. For each agreed pair: move the committed ledger
    directory of every minted moment the dropped id carries onto the survivor's
    path, restamping the case id inside its documents; fill the survivor in with
    every fact only the dropped row carries; stamp its ``sample_weight`` with the
    pair's minimum; move the dropped id's ``events`` / ``snapshots`` /
    ``documents`` rows under the surviving id; and delete the dropped ``case_id``
    from all four tables. A disagreeing pair, and one whose ledger half this
    merge cannot carry mechanically (see :func:`_ledger_moves`), is skipped and
    reported, never dropped. ``data_root`` is the git ledger root. Idempotent —
    once applied, a second run finds no pairs.
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
    return LiveDedupeResult(
        applied=apply,
        pairs=len(dropped) + len(skipped),
        dropped=dropped,
        skipped=skipped,
        ledger_moves=ledger_moves,
    )


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
    case id every event of the twin references — including the case-level
    baselines, which no move carries. Returns ``(event_id, entries)`` for the
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

    One entry per minted moment of the dropped twin whose committed directory
    belongs under the survivor — either still on the dropped case's path, or
    already at the survivor with documents naming the dropped case (an
    interrupted run's half, which the move helper's unconditional restamp
    finishes, and which reports as a restamp rather than a move). A case-level
    baseline is not moved: its ledger half is owed at first touch or resolution
    rather than at the mint, so a missing one is no breakage — but see below,
    because a baseline directory is not therefore free to ignore.

    Three shapes refuse the pair whole rather than merge it in part. Committed
    **cell output anywhere under the dropped case** — a prediction or evaluation
    names its own case id inside its own files, which no restamp here rewrites,
    so the row delete would orphan it into a ``ledger_references_exist``
    failure; this is the one check that looks past the minted moments, since the
    delete reaches every event of the twin. Directories under **both** ids for
    one moment, which is two committed definitions and a judgement call. And a
    survivor-side document that will not read, which leaves the interrupted-move
    question unanswerable: one unreadable file sends its pair to triage instead
    of aborting a pass that may already have written.
    """
    drop_paths = _case_paths(data_root, pair.drop)
    keep_paths = _case_paths(data_root, pair.keep)
    if drop_paths is None or keep_paths is None:  # pragma: no cover — both ids just parsed
        return [], None
    output = _committed_cell_output(drop_paths)
    if output is not None:
        event_id, entries = output
        return [], _CELL_OUTPUT_REASON.format(event_id=event_id, extra=", ".join(entries))
    minted = moments.minted_moment_ids()
    planned: list[LedgerMove] = []
    for event in corpus.events_for_case(conn, pair.drop):
        if event.event_id not in minted:
            continue
        old = drop_paths.event(event.event_id)
        new = keep_paths.event(event.event_id)
        if old.base.is_dir():
            if new.base.exists():
                return [], _LEDGER_COLLISION_REASON.format(event_id=event.event_id)
            planned.append(_planned_move(pair, event.event_id, restamp_only=False))
            continue
        try:
            interrupted = _still_names(new, pair.drop)
        except (OSError, ValueError, yaml.YAMLError) as error:
            return [], _UNREADABLE_REASON.format(event_id=event.event_id, error=error)
        if interrupted:
            planned.append(_planned_move(pair, event.event_id, restamp_only=True))
    return planned, None


def _planned_move(pair: DuplicatePair, event_id: str, *, restamp_only: bool) -> LedgerMove:
    return LedgerMove(
        event_id=event_id, from_case=pair.drop, to_case=pair.keep, restamp_only=restamp_only
    )


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
        drop_paths = _case_paths(data_root, move.from_case)
        keep_paths = _case_paths(data_root, move.to_case)
        if drop_paths is None or keep_paths is None:  # pragma: no cover — both ids just parsed
            continue
        move_event_directory(
            drop_paths.event(move.event_id),
            keep_paths.event(move.event_id),
            {"case_id": pair.keep},
        )

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
