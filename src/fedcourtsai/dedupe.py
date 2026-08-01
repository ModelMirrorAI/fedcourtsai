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

Deterministic and conservative: a pair disagreeing on ``date_filed``,
``date_decided``, or ``disposition`` is reported and never dropped — the
dry-run output is the triage list — and only exact two-row groups with exactly
one live-minted id are candidates at all. Each merge step is its own
transaction and every step is convergent, so a run interrupted mid-pair leaves
both rows present (the survivor merely enriched) and a re-run completes it.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict

from . import corpus
from .supremecourt import is_live_docket_id


class DuplicatePair(BaseModel):
    """One duplicated SCOTUS docket: a CourtListener-keyed row and its live twin."""

    model_config = ConfigDict(extra="forbid")

    keep: str  # the CourtListener-keyed case_id (docket id below the live range)
    drop: str  # the live-minted case_id (docket id in the reserved range)
    agreed: bool  # date_filed, date_decided and disposition agree (None agrees)
    weight: int  # min of the pair's sample_weights (None reads as 1)


class SkippedPair(BaseModel):
    """A disagreeing pair, reported with its conflicting facts and never dropped."""

    model_config = ConfigDict(extra="forbid")

    pair: DuplicatePair
    conflicts: list[str]


class LiveDedupeResult(BaseModel):
    """One dedupe run's outcome — what was (or would be) dropped, and what was not."""

    model_config = ConfigDict(extra="forbid")

    applied: bool
    pairs: int
    dropped: list[str]  # live-minted case_ids removed (or that a dry run would remove)
    skipped: list[SkippedPair]


# Columns the field-level merge does not fill generically: identity, the scope
# columns (the eligibility mirror derives from the court predicate, identical on
# both rows, and the exclusion latch is the scope reconcile's to re-decide from
# the merged facts), and the columns with their own merge semantics below — the
# weight (the pair minimum), the max-latched distribution count, the monotonic
# opinion bit, the sticky salience selection, and the fill-in salience/queue
# stamps.
_MERGE_SPECIAL = frozenset(
    {
        "case_id",
        "court",
        "predict_eligible",
        "predict_excluded",
        "sample_weight",
        "distribution_count",
        "has_opinion",
        "salience_score",
        "salience_version",
        "salience_selected",
        "predict_queued_at",
        "evaluate_queued_at",
    }
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
        # applied here because the missed join kept that latch from firing. The
        # live channel demonstrably included this petition (it minted a row for
        # it) and asserts a weight on every row it writes — the poller and the
        # keep-every-decided-petition walk include with certainty, weight 1 —
        # so the petition's inclusion probability is the pair's best (lowest)
        # inverse weight. None reads as 1, the weight backfill's own
        # fall-through for a spelling its serial parser cannot read.
        weight = min(keep_row.sample_weight or 1, drop_row.sample_weight or 1)
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


def dedupe_live_rows(conn: sqlite3.Connection, *, apply: bool) -> LiveDedupeResult:
    """Merge each agreed duplicate pair onto its survivor and drop the live twin.

    Dry run by default (reports what would change, writes nothing); ``apply``
    performs the writes. For each agreed pair: fill the survivor in with every
    fact only the dropped row carries, stamp its ``sample_weight`` with the
    pair's minimum, move the dropped id's ``events`` / ``snapshots`` /
    ``documents`` rows under the surviving id, and delete the dropped
    ``case_id`` from all four tables. A disagreeing pair is skipped and reported
    with its conflicts, never dropped. Idempotent — once applied, a second run
    finds no pairs.
    """
    dropped: list[str] = []
    skipped: list[SkippedPair] = []
    for pair, conflicts in _candidates(conn):
        if not pair.agreed:
            skipped.append(SkippedPair(pair=pair, conflicts=conflicts))
            continue
        dropped.append(pair.drop)
        if apply:
            _apply_pair(conn, pair)
    return LiveDedupeResult(
        applied=apply, pairs=len(dropped) + len(skipped), dropped=dropped, skipped=skipped
    )


def _merged_row(keep: corpus.CorpusRow, drop: corpus.CorpusRow, weight: int) -> corpus.CorpusRow:
    """The survivor with every fact only the dropped twin carries filled in.

    Keep-side precedence: a field the survivor already asserts keeps its value
    (the agreement check guarantees the checked facts match anyway), and a field
    it lacks takes the twin's — so the live channel's signals (the conference
    stamps, the lower-court name, the cert dates) survive the drop. The columns
    with their own semantics merge by them: ``distribution_count`` takes the max
    (proceedings only grow), ``has_opinion`` ORs (monotonic),
    ``salience_selected`` stays sticky, the salience score/version and the queue
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


def _apply_pair(conn: sqlite3.Connection, pair: DuplicatePair) -> None:
    """Merge one agreed pair onto the survivor, then delete the live twin."""
    keep_row = corpus.get_row(conn, pair.keep)
    drop_row = corpus.get_row(conn, pair.drop)
    if keep_row is None or drop_row is None:  # pragma: no cover — rows just listed
        return
    merged = _merged_row(keep_row, drop_row, pair.weight)

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
