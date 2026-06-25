from collections.abc import Callable
from datetime import date
from pathlib import Path

import httpx
import pytest

from fedcourtsai import corpus
from fedcourtsai.pipeline.ingest import from_bulk_row
from fedcourtsai.pipeline.seed import (
    BulkSource,
    CourtChunk,
    CourtListenerBulkSource,
    backfill,
    is_bulk_file_url,
    load_cursor,
    quarter_id,
    resolve_latest_dockets,
    save_cursor,
    sibling_bulk_url,
    snapshot_date,
)
from fedcourtsai.schemas import CourtProgress, Disposition, SeedProgress


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


def test_snapshot_date_maps_quarter_to_last_day() -> None:
    assert snapshot_date("2026-Q1") == date(2026, 3, 31)
    assert snapshot_date("2026-Q2") == date(2026, 6, 30)
    assert snapshot_date("2026-Q3") == date(2026, 9, 30)
    assert snapshot_date("2026-Q4") == date(2026, 12, 31)
    # A non-quarter, non-date id yields no frontier (seed hands nothing off).
    assert snapshot_date("not-a-quarter") is None


def test_snapshot_date_reads_iso_dated_snapshot_id() -> None:
    # An auto-resolved id is the dockets file's publication date verbatim, the
    # most accurate "complete as of" date for the discovery-frontier handoff.
    assert snapshot_date("2026-03-31") == date(2026, 3, 31)
    assert snapshot_date("2025-12-02") == date(2025, 12, 2)
    assert snapshot_date("2026-13-01") is None  # not a real calendar date


def test_backfill_hands_off_snapshot_date_as_watermark(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    # Complete both courts' backfill in one run.
    backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=100,
    )
    with corpus.connect(db) as conn:
        # Each completed court's discovery watermark is the snapshot's as-of date,
        # so the first forward pull searches from the snapshot, not from today.
        assert corpus.get_discovery_watermark(conn, "ca1") == date(2026, 6, 30)
        assert corpus.get_discovery_watermark(conn, "ca2") == date(2026, 6, 30)


def test_backfill_no_watermark_until_court_complete(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    # Budget stops mid-ca1 (4 of 5 rows), so neither court is complete this run.
    backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=4,
    )
    with corpus.connect(db) as conn:
        # No frontier handed off until a court's backfill is "complete as of" it.
        assert corpus.get_discovery_watermark(conn, "ca1") is None
        assert corpus.get_discovery_watermark(conn, "ca2") is None


def test_seed_does_not_lower_a_later_forward_watermark(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    # A forward pull has already advanced ca1 past the snapshot date.
    with corpus.connect(db) as conn:
        corpus.set_discovery_watermark(conn, "ca1", date(2026, 8, 1))
    backfill(
        FakeBulkSource("2026-Q2", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=100,
    )
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca1") == date(2026, 8, 1)  # not rewound
        assert corpus.get_discovery_watermark(conn, "ca2") == date(2026, 6, 30)  # newly seeded


def test_non_quarter_snapshot_hands_off_no_watermark(tmp_path: Path) -> None:
    cursor = tmp_path / "seed-progress.yaml"
    db = corpus.corpus_db_path(tmp_path)
    backfill(
        FakeBulkSource("nightly-2026-06-25", _data()),
        cursor_path=cursor,
        courts=["ca1", "ca2"],
        corpus_db_path=db,
        max_cases=100,
    )
    with corpus.connect(db) as conn:
        assert corpus.get_discovery_watermark(conn, "ca1") is None
        assert corpus.get_discovery_watermark(conn, "ca2") is None


def test_bulk_source_stages_and_serves_court_chunks(tmp_path: Path) -> None:
    dockets = tmp_path / "dockets.csv"
    dockets.write_text(
        "id,court_id,docket_number\n"
        "1,ca9,9-1\n"
        "2,ca1,1-1\n"  # untracked court — filtered out of staging
        "3,ca9,9-2\n"
        "4,ca9,9-3\n"
    )
    source = CourtListenerBulkSource(
        "2026-Q2", dockets_url="dockets.csv", courts=["ca9"], dockets_cache=dockets
    )
    try:
        first = source.fetch_court_chunk("ca9", offset=0, limit=2)
        assert [r["id"] for r in first.rows] == ["1", "3"]  # ca1 row skipped
        assert first.reached_end is False
        assert first.total == 3  # staging knows the per-court count cheaply

        rest = source.fetch_court_chunk("ca9", offset=2, limit=2)
        assert [r["id"] for r in rest.rows] == ["4"]
        assert rest.reached_end is True
        assert rest.total == 3
    finally:
        source.cleanup()


def test_bulk_source_joins_opinion_cluster_fields(tmp_path: Path) -> None:
    dockets = tmp_path / "dockets.csv"
    dockets.write_text("id,court_id,docket_number\n1,ca9,9-1\n2,ca9,9-2\n")
    clusters = tmp_path / "opinion-clusters.csv"
    clusters.write_text(
        "id,docket_id,disposition,summary,judges\n"
        "10,1,Affirmed; motion granted,The panel affirmed.,Smith; Lee\n"
        "999,9999,Reversed,unrelated,Doe\n"  # docket not tracked — ignored
    )
    source = CourtListenerBulkSource(
        "2026-Q2",
        dockets_url="dockets.csv",
        courts=["ca9"],
        clusters_url="opinion-clusters.csv",
        dockets_cache=dockets,
        clusters_cache=clusters,
    )
    try:
        chunk = source.fetch_court_chunk("ca9", offset=0, limit=10)
    finally:
        source.cleanup()

    by_id = {r["id"]: r for r in chunk.rows}
    assert by_id["1"]["disposition"] == "Affirmed; motion granted"
    assert by_id["1"]["summary"] == "The panel affirmed."
    assert by_id["1"]["judges"] == "Smith; Lee"
    # No cluster for docket 2 → the joined fields stay blank (as today).
    assert by_id["2"].get("disposition") is None

    # The served row flows through the shared normalizer to fill the corpus fields.
    row = from_bulk_row(by_id["1"])
    assert row.disposition == Disposition.granted
    assert row.summary == "The panel affirmed."
    assert row.judges == ["Lee", "Smith"]  # split on ';', deduped, sorted


def test_bulk_source_keeps_latest_cluster_per_docket(tmp_path: Path) -> None:
    dockets = tmp_path / "dockets.csv"
    dockets.write_text("id,court_id\n1,ca9\n")
    clusters = tmp_path / "opinion-clusters.csv"
    clusters.write_text(
        "id,docket_id,disposition,summary,judges\n"
        "5,1,Denied,old summary,A\n"
        "8,1,Granted,new summary,B\n"  # higher cluster id — the later disposition wins
    )
    source = CourtListenerBulkSource(
        "2026-Q2",
        dockets_url="dockets.csv",
        courts=["ca9"],
        clusters_url="opinion-clusters.csv",
        dockets_cache=dockets,
        clusters_cache=clusters,
    )
    try:
        chunk = source.fetch_court_chunk("ca9", offset=0, limit=10)
    finally:
        source.cleanup()
    assert chunk.rows[0]["disposition"] == "Granted"
    assert chunk.rows[0]["summary"] == "new summary"


def test_bulk_source_without_clusters_loads_spine_blank(tmp_path: Path) -> None:
    dockets = tmp_path / "dockets.csv"
    dockets.write_text("id,court_id,docket_number\n1,ca9,9-1\n")
    source = CourtListenerBulkSource(
        "2026-Q2", dockets_url="dockets.csv", courts=["ca9"], dockets_cache=dockets
    )
    try:
        chunk = source.fetch_court_chunk("ca9", offset=0, limit=10)
    finally:
        source.cleanup()
    assert chunk.rows[0].get("disposition") is None  # no sibling to join


def test_staging_is_reused_across_sources_for_same_snapshot(tmp_path: Path) -> None:
    staging = tmp_path / "stage.db"
    full = tmp_path / "full.csv"
    full.write_text("id,court_id\n1,ca9\n2,ca9\n")
    src1 = CourtListenerBulkSource(
        "2026-Q2", dockets_url="full.csv", courts=["ca9"], staging_path=staging, dockets_cache=full
    )
    src1.fetch_court_chunk("ca9", offset=0, limit=10)
    src1.cleanup()  # a caller-owned staging_path survives cleanup
    assert staging.exists()

    # A second source on the SAME snapshot reuses the staged DB and never reads the
    # (now empty) source file it is pointed at.
    empty = tmp_path / "empty.csv"
    empty.write_text("id,court_id\n")
    src2 = CourtListenerBulkSource(
        "2026-Q2",
        dockets_url="empty.csv",
        courts=["ca9"],
        staging_path=staging,
        dockets_cache=empty,
    )
    try:
        chunk = src2.fetch_court_chunk("ca9", offset=0, limit=10)
    finally:
        src2.cleanup()
    assert chunk.total == 2  # served from the reused staging, not the empty file


def test_staging_rebuilds_on_snapshot_change(tmp_path: Path) -> None:
    staging = tmp_path / "stage.db"
    full = tmp_path / "full.csv"
    full.write_text("id,court_id\n1,ca9\n2,ca9\n")
    src1 = CourtListenerBulkSource(
        "2026-Q2", dockets_url="full.csv", courts=["ca9"], staging_path=staging, dockets_cache=full
    )
    src1.fetch_court_chunk("ca9", offset=0, limit=10)
    src1.cleanup()

    # A newer snapshot supersedes the staged DB: it is rebuilt from the new file.
    empty = tmp_path / "empty.csv"
    empty.write_text("id,court_id\n")
    src2 = CourtListenerBulkSource(
        "2026-Q3",
        dockets_url="empty.csv",
        courts=["ca9"],
        staging_path=staging,
        dockets_cache=empty,
    )
    try:
        chunk = src2.fetch_court_chunk("ca9", offset=0, limit=10)
    finally:
        src2.cleanup()
    assert chunk.total == 0  # rebuilt empty for the new snapshot


def test_bulk_source_cleanup_preserves_injected_files(tmp_path: Path) -> None:
    dockets = tmp_path / "dockets.csv"
    dockets.write_text("id,court_id\n1,ca9\n")
    source = CourtListenerBulkSource(
        "2026-Q2", dockets_url="dockets.csv", courts=["ca9"], dockets_cache=dockets
    )
    source.fetch_court_chunk("ca9", offset=0, limit=1)
    source.cleanup()  # injected (not downloaded), so it must survive
    assert dockets.exists()


def test_sibling_bulk_url_derives_or_declines() -> None:
    assert (
        sibling_bulk_url("https://x/y/dockets-2026-03-31.csv.bz2", "opinion-clusters")
        == "https://x/y/opinion-clusters-2026-03-31.csv.bz2"
    )
    assert (
        sibling_bulk_url("https://x/dockets.csv.gz", "opinion-clusters")
        == "https://x/opinion-clusters.csv.gz"
    )
    # A non-standard pinned URL has no derivable sibling.
    assert sibling_bulk_url("https://x/custom-export.csv", "opinion-clusters") is None


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


# --- resolving the latest bulk file from a bucket prefix -----------------------

_BUCKET = "https://com-courtlistener-storage.s3.us-west-2.amazonaws.com"


def _s3_listing(keys: list[str], *, next_token: str | None = None) -> str:
    """A minimal S3 ListObjectsV2 XML body for the given keys."""
    contents = "".join(f"<Contents><Key>{k}</Key></Contents>" for k in keys)
    truncated = "true" if next_token else "false"
    token = f"<NextContinuationToken>{next_token}</NextContinuationToken>" if next_token else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
        f"<IsTruncated>{truncated}</IsTruncated>{token}{contents}</ListBucketResult>"
    )


def _mock_client(handle: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handle), follow_redirects=True)


def test_is_bulk_file_url_distinguishes_file_from_prefix() -> None:
    assert is_bulk_file_url(f"{_BUCKET}/bulk-data/dockets-2026-03-31.csv.bz2")
    assert is_bulk_file_url("https://x/y/dockets.csv.gz")
    assert is_bulk_file_url("https://x/y/export.csv")
    assert not is_bulk_file_url(f"{_BUCKET}/bulk-data/")
    assert not is_bulk_file_url(f"{_BUCKET}/bulk-data")


def test_resolve_latest_dockets_picks_newest_by_date() -> None:
    seen: dict[str, str] = {}

    def handle(request: httpx.Request) -> httpx.Response:
        seen.update(dict(request.url.params))
        body = _s3_listing(
            [
                "bulk-data/dockets-2025-12-31.csv.bz2",
                "bulk-data/dockets-2026-03-31.csv.bz2",  # newest
                "bulk-data/dockets-2025-09-04.csv.bz2",
                "bulk-data/opinion-clusters-2026-03-31.csv.bz2",  # not a dockets file
            ]
        )
        return httpx.Response(200, text=body)

    with _mock_client(handle) as client:
        url, snapshot_id = resolve_latest_dockets(f"{_BUCKET}/bulk-data/", client=client)

    assert url == f"{_BUCKET}/bulk-data/dockets-2026-03-31.csv.bz2"
    assert snapshot_id == "2026-03-31"
    # Listing is scoped to the dockets prefix so unrelated tables aren't paged in.
    assert seen["prefix"] == "bulk-data/dockets-"
    assert seen["list-type"] == "2"


def test_resolve_latest_dockets_follows_pagination() -> None:
    pages = {
        None: _s3_listing(["bulk-data/dockets-2025-12-31.csv.bz2"], next_token="page2"),
        "page2": _s3_listing(["bulk-data/dockets-2026-03-31.csv.bz2"]),
    }

    def handle(request: httpx.Request) -> httpx.Response:
        token = request.url.params.get("continuation-token")
        return httpx.Response(200, text=pages[token])

    with _mock_client(handle) as client:
        url, snapshot_id = resolve_latest_dockets(f"{_BUCKET}/bulk-data/", client=client)

    # The newest key lives on the second page, so pagination must be followed.
    assert snapshot_id == "2026-03-31"
    assert url.endswith("dockets-2026-03-31.csv.bz2")


def test_resolve_latest_dockets_raises_when_no_dockets_file() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=_s3_listing([]))

    with _mock_client(handle) as client, pytest.raises(ValueError, match=r"No dockets-.*file"):
        resolve_latest_dockets(f"{_BUCKET}/bulk-data/", client=client)
