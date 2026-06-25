from datetime import date
from pathlib import Path

from fedcourtsai import corpus
from fedcourtsai.pipeline.seed import (
    BulkSource,
    CourtChunk,
    CourtListenerBulkSource,
    backfill,
    load_cursor,
    quarter_id,
    save_cursor,
)
from fedcourtsai.schemas import CourtProgress, SeedProgress


def _row(court: str, docket: int) -> dict[str, str]:
    """A minimal bulk CSV row the shared ingestion core accepts."""
    return {"id": str(docket), "court_id": court, "docket_number": f"{docket}-x"}


class FakeBulkSource:
    """In-memory :class:`BulkSource` — per-court row lists, no network."""

    def __init__(
        self,
        snapshot_id: str,
        data: dict[str, list[dict[str, str]]],
        *,
        provide_total: bool = False,
    ) -> None:
        self.snapshot_id = snapshot_id
        self._data = data
        self._provide_total = provide_total

    def fetch_court_chunk(self, court: str, *, offset: int, limit: int) -> CourtChunk:
        rows = self._data.get(court, [])
        taken = rows[offset : offset + limit]
        reached_end = offset + len(taken) >= len(rows)
        total = len(rows) if self._provide_total else None
        return CourtChunk(rows=list(taken), reached_end=reached_end, total=total)


def _data() -> dict[str, list[dict[str, str]]]:
    return {
        "ca1": [_row("ca1", i) for i in range(5)],
        "ca2": [_row("ca2", i) for i in range(3)],
    }


def test_fake_source_is_a_bulk_source() -> None:
    assert isinstance(FakeBulkSource("s", {}), BulkSource)


def test_first_run_loads_one_chunk_up_to_budget(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    report = backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=4,
    )
    assert report.loaded_this_run == 4
    assert report.snapshot == "2026-Q2"
    assert report.complete is False
    # Budget spent on ca1; ca2 untouched this run.
    progress = load_cursor(cursor)
    assert progress.courts["ca1"].offset == 4
    assert progress.courts["ca1"].complete is False
    assert progress.courts["ca2"].offset == 0
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 4


def test_resumes_and_completes_across_runs(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    src = FakeBulkSource("2026-Q2", _data())
    backfill(src, cursor_path=cursor, courts=["ca1", "ca2"], corpus_db_path=db, max_cases=4)
    # run 1 loaded ca1 0->4; run 2 finishes ca1 (4->5) then ca2 (0->3).
    report = backfill(
        src, cursor_path=cursor, courts=["ca1", "ca2"], corpus_db_path=db, max_cases=4
    )

    assert report.loaded_this_run == 4
    assert report.complete is True
    progress = load_cursor(cursor)
    assert progress.courts["ca1"].complete is True
    assert progress.courts["ca1"].total == 5  # filled from offset on completion
    assert progress.courts["ca2"].complete is True
    with corpus.connect(db) as conn:
        assert corpus.count(conn) == 8


def test_idempotent_after_completion(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    src = FakeBulkSource("2026-Q2", _data())
    backfill(src, cursor_path=cursor, courts=["ca1", "ca2"], corpus_db_path=db, max_cases=100)
    report = backfill(
        src, cursor_path=cursor, courts=["ca1", "ca2"], corpus_db_path=db, max_cases=100
    )
    assert report.loaded_this_run == 0
    assert report.complete is True


def test_new_snapshot_triggers_reconciliation(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    backfill(
        FakeBulkSource("2026-Q1", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=100,
    )
    assert load_cursor(cursor).courts["ca1"].complete is True

    # A newer snapshot supersedes the cursor: offsets reset and it reloads.
    report = backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=2,
    )
    assert report.snapshot == "2026-Q2"
    assert report.loaded_this_run == 2
    progress = load_cursor(cursor)
    assert progress.snapshot == "2026-Q2"
    assert progress.courts["ca1"].offset == 2
    assert progress.courts["ca1"].complete is False


def test_report_percent_when_total_known(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    report = backfill(
        FakeBulkSource("2026-Q2", {"ca1": [_row("ca1", i) for i in range(10)]}, provide_total=True),
        cursor_path=cursor,
        courts=["ca1"],
        corpus_db_path=db,
        max_cases=4,
    )
    line = report.courts[0]
    assert (line.loaded, line.total, line.percent, line.complete) == (4, 10, 40.0, False)


def test_empty_courts_loads_nothing(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    report = backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=[],
        corpus_db_path=corpus.corpus_db_path(tmp_path),
        max_cases=100,
    )
    assert report.loaded_this_run == 0
    assert report.courts == []


def test_cursor_roundtrips(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    progress = SeedProgress(
        snapshot="2026-Q2", courts={"ca9": CourtProgress(offset=12000, total=45000)}
    )
    save_cursor(cursor, progress)
    assert load_cursor(cursor) == progress


def test_completed_is_the_human_gate_not_machine_state(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    # Even once every court's stream is exhausted, the backfill leaves `completed`
    # false: it is the maintainer's sign-off (flipped by the run-seed completion
    # PR), never set automatically — see SeedProgress.completed.
    report = backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=100,
    )
    assert report.complete is True
    assert load_cursor(cursor).completed is False

    # A maintainer acknowledges by merging the PR; a fresh snapshot supersedes the
    # cursor, so the acknowledgement must reset — the new backfill is not done.
    acknowledged = load_cursor(cursor)
    acknowledged.completed = True
    save_cursor(cursor, acknowledged)
    backfill(
        FakeBulkSource("2026-Q3", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=2,
    )
    assert load_cursor(cursor).completed is False


def test_load_cursor_missing_is_fresh(tmp_path: Path) -> None:
    assert load_cursor(tmp_path / "absent.yaml") == SeedProgress()


def test_quarter_id() -> None:
    assert quarter_id(date(2026, 6, 25)) == "2026-Q2"
    assert quarter_id(date(2026, 1, 1)) == "2026-Q1"
    assert quarter_id(date(2026, 12, 31)) == "2026-Q4"


def test_courtlistener_bulk_source_filters_skips_and_ends(tmp_path: Path) -> None:
    csv_path = tmp_path / "dockets.csv"
    csv_path.write_text(
        "id,court_id,docket_number\n"
        "1,ca9,9-1\n"
        "2,ca1,1-1\n"  # different court — filtered out
        "3,ca9,9-2\n"
        "4,ca9,9-3\n"
    )
    source = CourtListenerBulkSource("2026-Q2", url="dockets.csv", cache_path=csv_path)

    first = source.fetch_court_chunk("ca9", offset=0, limit=2)
    assert [r["id"] for r in first.rows] == ["1", "3"]  # ca1 row skipped
    assert first.reached_end is False

    rest = source.fetch_court_chunk("ca9", offset=2, limit=2)
    assert [r["id"] for r in rest.rows] == ["4"]
    assert rest.reached_end is True


def test_courtlistener_bulk_source_cleanup_only_owned(tmp_path: Path) -> None:
    csv_path = tmp_path / "dockets.csv"
    csv_path.write_text("id,court_id\n1,ca9\n")
    source = CourtListenerBulkSource("2026-Q2", url="dockets.csv", cache_path=csv_path)
    source.fetch_court_chunk("ca9", offset=0, limit=1)
    source.cleanup()  # did not download this cache, so it must survive
    assert csv_path.exists()


def test_backfill_defines_baseline_events(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    report = backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=100,
    )
    # No bulk entries, so each docket gets exactly its baseline event and none is
    # ambiguous — the historical backfill is now visible to prediction.
    assert report.ambiguous == 0
    with corpus.connect(db) as conn:
        assert corpus.event_count(conn) == 8  # one per seeded docket (5 + 3)
        events = corpus.events_for_case(conn, "ca1/0")
        assert [(e.event_id, e.kind, e.resolved) for e in events] == [
            ("evt-appeal-disposition", "appeal", False)
        ]


def test_backfill_event_definition_is_idempotent(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    backfill(
        FakeBulkSource("2026-Q1", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=100,
    )
    # A newer snapshot reloads every row from the top; events re-upsert in place
    # rather than duplicating (the (case_id, event_id) primary key absorbs them).
    backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=100,
    )
    with corpus.connect(db) as conn:
        assert corpus.event_count(conn) == 8


def test_max_cases_zero_is_a_noop(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    report = backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=corpus.corpus_db_path(tmp_path),
        max_cases=0,
    )
    assert report.loaded_this_run == 0
    assert report.complete is False
