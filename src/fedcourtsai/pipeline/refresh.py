"""``fedcourts full-refresh``: reset the pipeline's forward state for a clean rebuild.

A full refresh is the operator escape hatch for a *structural* change to how data
is produced — a new corpus column, a corrected normalization, a data-validity bug
whose easiest fix is to rebuild from source — where refreshing one case at a time
would never catch up. It resets the pipeline's **forward tracking state** so the
whole tracked set re-seeds and re-pulls fresh, while leaving every historical fact
in place:

- **Re-seed all bulk data.** The seed cursor (``config/seed-progress.yaml``) is reset
  so the next ``seed-backfill`` re-loads every court from the top — the same path
  seed's quarterly snapshot reconcile takes (:func:`fedcourtsai.pipeline.seed._reconcile`),
  triggered on demand rather than by a new snapshot. The ingestion upsert is
  idempotent, so unchanged cases overwrite in place and any newly-added column or
  corrected value is back-filled across the corpus.
- **Re-pull every tracked case.** The corpus forward cursors are cleared — each
  case's ``last_pulled`` and every per-court discovery watermark — so the budget
  governor treats the whole tracked set as stalest and re-fetches it, and forward
  discovery re-establishes each court's frontier from the next seed hand-off.

What it deliberately does **not** touch keeps the operation safe and reversible:

- **Corpus history is preserved.** Case rows, predictable-event rows, and dated
  snapshots are left intact; full refresh resets *tracking state*, never the facts,
  so the corpus stays append-only and its row count never drops. The prior corpus
  blob is retained by the DVC remote's S3 object versioning, so the pre-refresh
  state is recoverable.
- **The git ledger is preserved.** Outcomes, predictions, and evaluations under
  ``data/`` are versioned by git itself and stay where they are — kept as the
  historical record. "No current cases" follows because the agentic stages are
  driven by ``pull`` re-queuing changed cases with open events: after the reset
  ``pull`` re-pulls everyone and re-queues fresh, so new predictions accrue
  alongside the retained history rather than replacing it.

This module owns only the deterministic reset; it never spends API budget, runs an
agent, or writes under ``data/``. The run-seed workflow runs it (under the shared
``corpus-write`` lock) when a maintainer dispatches a full refresh, then loops the
ordinary backfill over the reset cursor.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from pydantic import BaseModel

from .. import corpus
from ..schemas import CourtProgress, SeedProgress
from .seed import load_cursor, save_cursor


class RefreshReport(BaseModel):
    """Summary of a full-refresh reset, for the run log / step summary."""

    snapshot: str | None = None
    courts_reset: int = 0
    """Known courts whose seed cursor was reset for a full re-load."""
    cases_unpulled: int = 0
    """Cases whose ``last_pulled`` stamp was cleared (re-pulled fresh)."""
    watermarks_cleared: int = 0
    """Per-court discovery watermarks dropped (re-discovered fresh)."""
    corpus_present: bool = False
    """Whether a corpus was found to reset (False = run before ``dvc pull``)."""
    dry_run: bool = False


def reset_seed_cursor(progress: SeedProgress) -> SeedProgress:
    """Return a cursor that forces a full re-seed of every known court.

    Mirrors seed's snapshot reconcile (:func:`fedcourtsai.pipeline.seed._reconcile`)
    but is triggered on demand rather than by a snapshot change: each known court's
    ``offset`` / ``total`` / ``complete`` are reset and the human ``completed``
    sign-off cleared, while the ``snapshot`` id and the known court set are
    preserved. The next ``seed-backfill`` then re-loads every court from the top.
    """
    return SeedProgress(
        snapshot=progress.snapshot,
        courts={court: CourtProgress() for court in progress.courts},
        completed=False,
    )


def reset_corpus_tracking(conn: sqlite3.Connection) -> tuple[int, int]:
    """Clear the corpus forward cursors; return ``(cases_unpulled, watermarks_cleared)``.

    Clears ``last_pulled`` on every case so the pull governor treats the whole
    tracked set as stalest and re-fetches it, and drops every per-court discovery
    watermark so forward discovery re-establishes each frontier from the next seed
    hand-off. Case rows, predictable-event rows, and dated snapshots are left intact
    — full refresh resets tracking state, not the historical facts.
    """
    with conn:
        unpulled = conn.execute(
            "UPDATE cases SET last_pulled = NULL WHERE last_pulled IS NOT NULL"
        ).rowcount
        watermarks = conn.execute("DELETE FROM discovery_watermarks").rowcount
    return unpulled, watermarks


def full_refresh(
    *, cursor_path: Path, corpus_db_path: Path, dry_run: bool = False
) -> RefreshReport:
    """Reset the seed cursor and corpus forward cursors for a clean pipeline rebuild.

    Resets the committed seed cursor (forcing a full re-seed) and, when a corpus is
    present, clears its forward tracking state (forcing a fresh re-pull + re-discover)
    — see the module docstring for what is preserved. With ``dry_run`` nothing is
    written; the report counts what *would* be reset so a maintainer can confirm the
    blast radius first. Idempotent: a second run over an already-reset state is a
    no-op that reports zero cleared cursors.
    """
    progress = load_cursor(cursor_path)
    reset = reset_seed_cursor(progress)
    if not dry_run:
        save_cursor(cursor_path, reset)

    corpus_present = corpus_db_path.exists()
    unpulled = watermarks = 0
    if corpus_present:
        with corpus.connect(corpus_db_path) as conn:
            if dry_run:
                unpulled = int(
                    conn.execute(
                        "SELECT COUNT(*) AS n FROM cases WHERE last_pulled IS NOT NULL"
                    ).fetchone()["n"]
                )
                watermarks = int(
                    conn.execute("SELECT COUNT(*) AS n FROM discovery_watermarks").fetchone()["n"]
                )
            else:
                unpulled, watermarks = reset_corpus_tracking(conn)

    return RefreshReport(
        snapshot=reset.snapshot,
        courts_reset=len(reset.courts),
        cases_unpulled=unpulled,
        watermarks_cleared=watermarks,
        corpus_present=corpus_present,
        dry_run=dry_run,
    )
