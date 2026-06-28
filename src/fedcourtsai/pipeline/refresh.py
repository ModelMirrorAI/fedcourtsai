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
- **Re-pull and re-discover every tracked case.** The corpus forward cursors are
  reset — each case's ``last_pulled`` is cleared so the budget governor treats the
  active set as stalest and re-pulls it, and each tracked court's discovery
  watermark is reset to the snapshot frontier so forward discovery re-walks the
  whole post-snapshot range. Re-discovery re-ingests every case filed since the
  snapshot **whether open or closed** — closing the gap that ``pull``'s rotation,
  which skips closed cases to save budget, would otherwise leave for cases that
  resolved after the snapshot. Together with the re-seed (everything up to the
  snapshot), that reaches every tracked case. (Closed cases are re-ingested at the
  docket level via discovery and re-seed, not via a per-docket re-pull, which
  ``skip_closed`` still elides.) Re-ingestion never reopens an already-resolved
  event — ``upsert_events`` latches ``resolved`` — so prior outcomes hold.

What it deliberately does **not** touch keeps the operation safe and reversible:

- **Corpus history is preserved.** Case rows, predictable-event rows, and dated
  snapshots are left intact; full refresh resets *tracking state*, never the facts,
  so the corpus stays append-only and its row count never drops. Because DVC
  content-addresses the corpus blob, a refreshed corpus pushes under a new key
  while the pre-refresh blob stays in the remote (the read-write IAM role grants no
  delete) and the previous ``.dvc`` pointer is preserved in git history — so the
  prior state is recoverable.
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
from datetime import date
from pathlib import Path

from pydantic import BaseModel

from .. import corpus
from ..schemas import CourtProgress, SeedProgress
from .seed import load_cursor, save_cursor, snapshot_date


class RefreshReport(BaseModel):
    """Summary of a full-refresh reset, for the run log / step summary."""

    snapshot: str | None = None
    courts_reset: int = 0
    """Courts whose seed progress was actually cleared (0 if already at the start)."""
    cases_unpulled: int = 0
    """Cases whose ``last_pulled`` stamp was cleared (re-pulled fresh)."""
    watermarks_reset: int = 0
    """Per-court discovery watermarks reset to ``rediscover_since`` (or dropped)."""
    rediscover_since: str | None = None
    """ISO date discovery re-walks from (the snapshot frontier), or None if undatable."""
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


def reset_corpus_tracking(
    conn: sqlite3.Connection, *, courts: list[str], rediscover_since: date | None
) -> tuple[int, int]:
    """Reset the corpus forward cursors; return ``(cases_unpulled, watermarks_reset)``.

    Clears ``last_pulled`` on every case so the pull governor treats the whole
    tracked set as stalest and re-fetches it. For discovery, every tracked court's
    watermark is **reset to ``rediscover_since``** (the snapshot frontier) rather
    than dropped, so forward discovery deterministically re-walks the whole
    post-snapshot range — re-ingesting every case filed since the snapshot, closed
    or open, through the current normalization. This is a *force* write (unlike
    :func:`fedcourtsai.corpus.set_discovery_watermark`, which only moves forward),
    so it cannot be defeated by an interleaved ``pull`` that already advanced a
    watermark to today. When ``rediscover_since`` is None (a snapshot id with no
    derivable date) there is no frontier to seed, so watermarks are dropped and
    discovery falls back to its default — matching seed's own behavior.

    Case rows, predictable-event rows, and dated snapshots are left intact — full
    refresh resets tracking state, not the historical facts; re-ingestion never
    reopens an already-resolved event (``upsert_events`` latches ``resolved``).
    """
    with conn:
        unpulled = conn.execute(
            "UPDATE cases SET last_pulled = NULL WHERE last_pulled IS NOT NULL"
        ).rowcount
        if rediscover_since is not None and courts:
            conn.executemany(
                "INSERT INTO discovery_watermarks (court, last_filed) VALUES (?, ?) "
                "ON CONFLICT(court) DO UPDATE SET last_filed = excluded.last_filed",
                [(court, rediscover_since.isoformat()) for court in courts],
            )
            watermarks = len(courts)
        else:
            watermarks = conn.execute("DELETE FROM discovery_watermarks").rowcount
    return unpulled, watermarks


def full_refresh(
    *, cursor_path: Path, corpus_db_path: Path, dry_run: bool = False
) -> RefreshReport:
    """Reset the seed cursor and corpus forward cursors for a clean pipeline rebuild.

    Resets the committed seed cursor (forcing a full re-seed) and, when a corpus is
    present, resets its forward tracking state — clearing every ``last_pulled`` and
    resetting each tracked court's discovery watermark to the snapshot frontier
    (``rediscover_since``) — so pull re-pulls the active set and discovery re-walks
    the post-snapshot range. See the module docstring for what is preserved. With
    ``dry_run`` nothing is written; the report counts what *would* be reset so a
    maintainer can confirm the blast radius first. State-idempotent: a second run
    lands the same end state (it reports zero further ``last_pulled`` cleared, the
    watermarks already at the frontier).
    """
    progress = load_cursor(cursor_path)
    reset = reset_seed_cursor(progress)
    if not dry_run:
        save_cursor(cursor_path, reset)

    rediscover_since = snapshot_date(reset.snapshot) if reset.snapshot else None
    courts = list(reset.courts)
    # Count only courts that actually carried progress to clear, so an idempotent
    # re-run over an already-reset cursor reports 0 rather than the full court count.
    courts_reset = sum(1 for cp in progress.courts.values() if cp != CourtProgress())

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
                # The real run resets one watermark per tracked court when there is
                # a frontier to seed; otherwise it drops whatever watermarks exist.
                watermarks = (
                    len(courts)
                    if rediscover_since is not None and courts
                    else int(
                        conn.execute("SELECT COUNT(*) AS n FROM discovery_watermarks").fetchone()[
                            "n"
                        ]
                    )
                )
            else:
                unpulled, watermarks = reset_corpus_tracking(
                    conn, courts=courts, rediscover_since=rediscover_since
                )

    return RefreshReport(
        snapshot=reset.snapshot,
        courts_reset=courts_reset,
        cases_unpulled=unpulled,
        watermarks_reset=watermarks,
        rediscover_since=rediscover_since.isoformat() if rediscover_since else None,
        corpus_present=corpus_present,
        dry_run=dry_run,
    )
