"""Converge declared-moment events onto the moment their id declares.

An event id that the declared-moments table registers
(:mod:`fedcourtsai.pipeline.moments`) names exactly one forecast moment: the
id is the key, and the table is the authority on what it declares. The stored
``moment`` column, in the corpus row and in the ledger ``event.yaml`` written
from it, is a copy of that answer. A copy goes stale when a row moves to a new
identity and its moment travels with it instead of being re-derived. The
population this pass exists for is that shape: application baselines renamed
from the cert petition id (:mod:`fedcourtsai.application_migration`) with the
cert stage's ``distribution`` moment carried onto ``evt-motion-disposition``,
whose declared moment is ``arrival``.

Nothing re-derives the column on its own for these rows. The upsert writes the
incoming moment on every re-ingest, but a decided application has left the live
rotation and is not re-read. This pass is the convergence: every corpus row
whose id is a declared moment, which is un-pinned, whose stage is the declared
moment's stage, and whose **non-null** moment differs from the declared one is
re-stamped to the declared moment. The same holds for every ledger
``event.yaml`` of that shape, scanned on its own so a ledger file whose corpus
row already converged is still found. A null moment is not this pass's
population. It already reads downstream as the stage's first moment, and the
``backfill-event-moments`` sweep materializes that reading.

Moving a moment moves the event between moment strata, so a scored event would
change the population a published figure was taken over. Any event whose ledger
directory holds committed predictions or evaluations is therefore skipped in
both stores and reported, for the maintainer to decide on with its scores in
view. An entry-pinned row, or a row whose stage is not its declared moment's
stage, is also skipped and reported, because either shape means the id is being
used for something the table does not describe.

Deterministic, offline and idempotent: a converged row no longer matches the
predicate. Dry run by default. ``apply`` refuses above ``max_rewrites``, which
counts corpus rows and ledger files together.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from . import corpus
from .paths import CasePaths
from .pipeline import moments
from .schemas import Moment, PredictableEvent
from .serialize import read_model, write_yaml


@dataclass(frozen=True)
class MomentRewrite:
    """One stored moment converging on the moment its event id declares."""

    case_id: str
    event_id: str
    was: str
    now: Moment
    #: The ledger ``event.yaml`` this rewrite targets; ``None`` for a corpus row.
    path: Path | None = None


@dataclass
class MomentConvergenceResult:
    """What the moment convergence rewrote (or would rewrite on a dry run)."""

    applied: bool = False
    corpus_rows: list[MomentRewrite] = field(default_factory=list)
    ledger_files: list[MomentRewrite] = field(default_factory=list)
    #: ``(case_id/event_id, reason)`` for every held-back shape, for triage.
    skipped: list[tuple[str, str]] = field(default_factory=list)
    #: True when ``apply`` was asked for but the blast-radius bound refused it.
    #: Nothing is written in that case, and the plan is reported.
    refused: bool = False

    @property
    def total(self) -> int:
        """Corpus rows and ledger files together, which is what the bound counts."""
        return len(self.corpus_rows) + len(self.ledger_files)


_SCORED_REASON = (
    "committed predictions or evaluations under this event; moving its moment "
    "moves scored cells between moment strata"
)
_PINNED_REASON = "entry-pinned row under a declared-moment id; not the declared moment"


def _event_dir(data_root: Path, case_id: str, event_id: str) -> Path | None:
    """The ledger directory for ``(case_id, event_id)``, or ``None`` for an unaddressable id."""
    court, _, docket = case_id.partition("/")
    if not docket.isdigit():
        return None
    return CasePaths(data_root, court, int(docket)).event(event_id).base


def _hold_back(
    spec: moments.MomentSpec, *, pinned: bool, stage: object, event_dir: Path | None
) -> str | None:
    """Why this stale event is reported rather than re-stamped, or ``None`` to re-stamp it.

    ``stage`` is compared by equality, never identity: the corpus hands in the
    stored string, and a validated ledger model hands in its own form of it.
    """
    if pinned:
        return _PINNED_REASON
    if stage != spec.stage:
        return f"stage {stage!s} is not the declared moment's stage {spec.stage.value}"
    if event_dir is not None and any(
        (event_dir / name).is_dir() for name in ("predictions", "evaluations")
    ):
        return _SCORED_REASON
    return None


def _scan_corpus(
    conn: sqlite3.Connection, data_root: Path, spec: moments.MomentSpec
) -> tuple[list[MomentRewrite], list[tuple[str, str]]]:
    """The corpus rows under ``spec``'s id carrying a different non-null moment."""
    rewrites: list[MomentRewrite] = []
    skipped: list[tuple[str, str]] = []
    rows = conn.execute(
        "SELECT case_id, stage, moment, docket_entry_id FROM events "
        "WHERE event_id = ? AND moment IS NOT NULL AND moment != ? ORDER BY case_id",
        (spec.event_id, spec.moment.value),
    ).fetchall()
    for row in rows:
        case_id = str(row["case_id"])
        reason = _hold_back(
            spec,
            pinned=row["docket_entry_id"] is not None,
            stage=row["stage"],
            event_dir=_event_dir(data_root, case_id, spec.event_id),
        )
        if reason is not None:
            skipped.append((f"{case_id}/{spec.event_id}", reason))
            continue
        rewrites.append(MomentRewrite(case_id, spec.event_id, str(row["moment"]), spec.moment))
    return rewrites, skipped


def _scan_ledger(
    data_root: Path, spec: moments.MomentSpec
) -> tuple[list[MomentRewrite], list[tuple[str, str]]]:
    """The ledger ``event.yaml`` files under ``spec``'s id carrying a different non-null moment."""
    rewrites: list[MomentRewrite] = []
    skipped: list[tuple[str, str]] = []
    for path in sorted((data_root / "cases").glob(f"*/*/events/{spec.event_id}/event.yaml")):
        definition = read_model(path, PredictableEvent)
        if definition.moment is None or definition.moment == spec.moment:
            continue
        reason = _hold_back(
            spec,
            pinned=definition.docket_entry_id is not None,
            stage=definition.stage,
            event_dir=path.parent,
        )
        if reason is not None:
            skipped.append((f"{definition.case_id}/{spec.event_id} (ledger)", reason))
            continue
        rewrites.append(
            MomentRewrite(
                definition.case_id, spec.event_id, str(definition.moment), spec.moment, path
            )
        )
    return rewrites, skipped


def converge_event_moments(
    conn: sqlite3.Connection,
    data_root: Path,
    *,
    apply: bool,
    max_rewrites: int | None = None,
) -> MomentConvergenceResult:
    """Re-stamp each declared-moment event whose stored moment disagrees with its id.

    Reads the corpus events table and the ledger under ``data_root``. With
    ``apply`` it writes both: each ledger ``event.yaml`` with only its
    ``moment`` changed, then the corpus through
    :func:`fedcourtsai.corpus.stamp_event_moments`, which includes the casestore
    mirror. ``max_rewrites`` is the blast-radius bound. Over it, nothing is
    written and ``refused`` is set.
    """
    result = MomentConvergenceResult(applied=apply)
    for spec in moments.DECLARED_MOMENTS:
        rows, row_skips = _scan_corpus(conn, data_root, spec)
        files, file_skips = _scan_ledger(data_root, spec)
        result.corpus_rows.extend(rows)
        result.ledger_files.extend(files)
        result.skipped.extend(row_skips + file_skips)

    if apply and max_rewrites is not None and result.total > max_rewrites:
        result.refused = True
        result.applied = False
        return result
    if not apply:
        return result

    for rewrite in result.ledger_files:
        if rewrite.path is not None:
            definition = read_model(rewrite.path, PredictableEvent)
            write_yaml(rewrite.path, definition.model_copy(update={"moment": rewrite.now}))
    corpus.stamp_event_moments(conn, [(r.case_id, r.event_id, r.now) for r in result.corpus_rows])
    return result
