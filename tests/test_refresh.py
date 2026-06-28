import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.pipeline.refresh import (
    RefreshReport,
    full_refresh,
    reset_corpus_tracking,
    reset_seed_cursor,
)
from fedcourtsai.pipeline.seed import load_cursor, save_cursor
from fedcourtsai.schemas import CourtProgress, SeedProgress

runner = CliRunner()


def _seeded_cursor() -> SeedProgress:
    """A cursor that looks like a completed backfill of two courts."""
    return SeedProgress(
        snapshot="2026-03-31",
        courts={
            "ca1": CourtProgress(offset=5, total=5, complete=True),
            "ca9": CourtProgress(offset=3, total=3, complete=True),
        },
        completed=True,
    )


def _fetch(conn: sqlite3.Connection, case_id: str) -> corpus.CorpusRow:
    row = corpus.get_row(conn, case_id)
    assert row is not None
    return row


def _populate_corpus(db: Path) -> None:
    """A corpus with two pulled cases and a discovery watermark."""
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(case_id="ca1/1", court="ca1", last_pulled=date(2026, 6, 1)),
                corpus.CorpusRow(case_id="ca9/2", court="ca9", last_pulled=date(2026, 6, 2)),
            ],
        )
        corpus.set_discovery_watermark(conn, "ca1", date(2026, 3, 31))


# --- reset_seed_cursor ---------------------------------------------------------


def test_reset_seed_cursor_clears_progress_keeps_courts_and_snapshot() -> None:
    reset = reset_seed_cursor(_seeded_cursor())
    assert reset.snapshot == "2026-03-31"  # snapshot preserved so reconcile is a no-op
    assert reset.completed is False
    assert set(reset.courts) == {"ca1", "ca9"}  # known court set preserved
    for cp in reset.courts.values():
        assert cp == CourtProgress()  # offset 0, total None, not complete


def test_reset_seed_cursor_on_empty_cursor_is_a_noop() -> None:
    reset = reset_seed_cursor(SeedProgress())
    assert reset.courts == {}
    assert reset.completed is False


# --- reset_corpus_tracking -----------------------------------------------------


def test_reset_corpus_tracking_clears_pulled_and_arms_every_court(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    _populate_corpus(db)
    with corpus.connect(db) as conn:
        unpulled, watermarks = reset_corpus_tracking(
            conn, courts=["ca1", "ca9"], rediscover_since=date(2026, 3, 31)
        )
    assert (unpulled, watermarks) == (2, 2)
    with corpus.connect(db) as conn:
        # Rows themselves are preserved — only the forward cursors were reset.
        assert corpus.count(conn) == 2
        assert _fetch(conn, "ca1/1").last_pulled is None
        assert _fetch(conn, "ca9/2").last_pulled is None
        # Every tracked court is armed at the snapshot frontier so discovery
        # re-walks the post-snapshot range — including ca9, which had no watermark.
        assert corpus.get_discovery_watermark(conn, "ca1") == date(2026, 3, 31)
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 3, 31)


def test_reset_corpus_tracking_force_rewinds_an_advanced_watermark(tmp_path: Path) -> None:
    # The fix for the discovery race: set_discovery_watermark is forward-only, so a
    # pull that already advanced a court to today would otherwise pin it there. The
    # reset must force the frontier back so the post-snapshot range is re-walked.
    db = corpus.corpus_db_path(tmp_path)
    _populate_corpus(db)
    with corpus.connect(db) as conn:
        corpus.set_discovery_watermark(conn, "ca1", date(2026, 6, 30))  # pull advanced it
    with corpus.connect(db) as conn:
        reset_corpus_tracking(conn, courts=["ca1"], rediscover_since=date(2026, 3, 31))
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca1") == date(2026, 3, 31)


def test_reset_corpus_tracking_without_frontier_drops_watermarks(tmp_path: Path) -> None:
    # An undatable snapshot id yields no frontier, so there is nothing to re-walk
    # from — drop the watermarks (discovery falls back to its default), as before.
    db = corpus.corpus_db_path(tmp_path)
    _populate_corpus(db)
    with corpus.connect(db) as conn:
        unpulled, watermarks = reset_corpus_tracking(
            conn, courts=["ca1", "ca9"], rediscover_since=None
        )
    assert (unpulled, watermarks) == (2, 1)  # one existing watermark dropped
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca1") is None


def test_reset_corpus_tracking_is_state_idempotent(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path)
    _populate_corpus(db)
    with corpus.connect(db) as conn:
        reset_corpus_tracking(conn, courts=["ca1", "ca9"], rediscover_since=date(2026, 3, 31))
        again = reset_corpus_tracking(
            conn, courts=["ca1", "ca9"], rediscover_since=date(2026, 3, 31)
        )
    # last_pulled is already cleared (0); the watermarks re-arm to the same frontier
    # — the same end state, reported as the count of courts re-armed.
    assert again == (0, 2)
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca1") == date(2026, 3, 31)


# --- full_refresh --------------------------------------------------------------


def test_full_refresh_resets_cursor_and_corpus(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    save_cursor(cursor, _seeded_cursor())
    db = corpus.corpus_db_path(tmp_path)
    _populate_corpus(db)

    report = full_refresh(cursor_path=cursor, corpus_db_path=db)

    assert report == RefreshReport(
        snapshot="2026-03-31",
        courts_reset=2,
        cases_unpulled=2,
        watermarks_reset=2,
        rediscover_since="2026-03-31",
        corpus_present=True,
        dry_run=False,
    )
    # Cursor was rewritten for a full re-seed.
    persisted = load_cursor(cursor)
    assert persisted.completed is False
    assert all(cp == CourtProgress() for cp in persisted.courts.values())
    # Corpus forward cursors were reset, rows kept, every court armed to re-discover.
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 2
        assert _fetch(conn, "ca1/1").last_pulled is None
        assert corpus.get_discovery_watermark(conn, "ca9") == date(2026, 3, 31)


def test_full_refresh_dry_run_writes_nothing(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    save_cursor(cursor, _seeded_cursor())
    db = corpus.corpus_db_path(tmp_path)
    _populate_corpus(db)

    report = full_refresh(cursor_path=cursor, corpus_db_path=db, dry_run=True)

    assert report.dry_run is True
    # Counts reflect what *would* be reset (one watermark per tracked court).
    assert (report.courts_reset, report.cases_unpulled, report.watermarks_reset) == (2, 2, 2)
    assert report.rediscover_since == "2026-03-31"
    # Nothing was actually changed.
    assert load_cursor(cursor).completed is True
    with corpus.connect(db) as conn:
        assert _fetch(conn, "ca1/1").last_pulled == date(2026, 6, 1)
        assert corpus.get_discovery_watermark(conn, "ca1") == date(2026, 3, 31)  # unchanged
        assert corpus.get_discovery_watermark(conn, "ca9") is None  # not created


def test_full_refresh_without_corpus_resets_cursor_only(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    save_cursor(cursor, _seeded_cursor())
    db = corpus.corpus_db_path(tmp_path)  # never created

    report = full_refresh(cursor_path=cursor, corpus_db_path=db)

    assert report.corpus_present is False
    assert (report.cases_unpulled, report.watermarks_reset) == (0, 0)
    assert report.courts_reset == 2
    assert load_cursor(cursor).completed is False
    # The reset must not have created an empty corpus as a side effect.
    assert not db.exists()


def test_full_refresh_missing_cursor_starts_fresh(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"  # never written
    db = corpus.corpus_db_path(tmp_path)

    report = full_refresh(cursor_path=cursor, corpus_db_path=db)

    assert report.courts_reset == 0
    assert load_cursor(cursor).completed is False


# --- the CLI command -----------------------------------------------------------


def _cli_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the CLI's config + corpus roots at ``tmp_path``; return the cursor path.

    A ``tracking.yaml`` aims the seed cursor inside ``tmp_path`` so the command never
    touches the real ``config/seed-progress.yaml``.
    """
    config_root = tmp_path / "config"
    config_root.mkdir()
    cursor = tmp_path / "seed-progress.yaml"
    (config_root / "tracking.yaml").write_text(f"seed:\n  cursor: {cursor}\n")
    monkeypatch.setenv("FEDCOURTS_CONFIG_ROOT", str(config_root))
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path))
    return cursor


def test_cli_full_refresh_resets_and_reports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cursor = _cli_env(tmp_path, monkeypatch)
    save_cursor(cursor, _seeded_cursor())
    _populate_corpus(corpus.corpus_db_path(tmp_path))

    report_path = tmp_path / "refresh.json"
    result = runner.invoke(app, ["full-refresh", "--report", str(report_path)])

    assert result.exit_code == 0, result.stdout
    assert "reset 2 court(s)" in result.stdout
    assert load_cursor(cursor).completed is False
    payload = json.loads(report_path.read_text())
    assert payload["cases_unpulled"] == 2
    assert payload["watermarks_reset"] == 2
    assert payload["rediscover_since"] == "2026-03-31"


def test_cli_full_refresh_dry_run_changes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cursor = _cli_env(tmp_path, monkeypatch)
    save_cursor(cursor, _seeded_cursor())
    _populate_corpus(corpus.corpus_db_path(tmp_path))

    result = runner.invoke(app, ["full-refresh", "--dry-run"])

    assert result.exit_code == 0, result.stdout
    assert "would reset" in result.stdout
    assert load_cursor(cursor).completed is True  # untouched


def test_cli_full_refresh_without_corpus_notes_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cursor = _cli_env(tmp_path, monkeypatch)
    save_cursor(cursor, _seeded_cursor())

    result = runner.invoke(app, ["full-refresh"])

    assert result.exit_code == 0, result.stdout
    assert "no corpus present" in result.stdout
