"""The ranged corpus backend (``fedcourtsai.corpus_ranged``), fully offline.

Everything below the transport seam is exercised with an in-memory transport
serving a local file; the boto3 transport itself (and the env-driven
``connect_readonly`` path) runs against moto's S3 stand-in. No test touches
the network.
"""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import apsw
import boto3
import pytest
from moto import mock_aws

from fedcourtsai import corpus, corpus_ranged, store
from fedcourtsai.fixture import FIXTURE_CASES, build_fixture_corpus
from fedcourtsai.pipeline.cascade import run_cascade
from fedcourtsai.schemas import Disposition

REMOTE_URL = "s3://test-bucket/store"


class FileTransport:
    """Serve byte ranges of an in-memory blob, recording every fetch."""

    def __init__(self, blob: bytes) -> None:
        self.blob = blob
        self.calls: list[tuple[int, int]] = []

    def __call__(self, key: str, start: int, end: int) -> bytes:
        self.calls.append((start, end))
        return self.blob[start : end + 1]


def _write_pointer(db_path: Path) -> tuple[Path, str]:
    """A DVC pointer for ``db_path`` in the committed pointer's exact shape."""
    blob = db_path.read_bytes()
    md5 = hashlib.md5(blob).hexdigest()
    pointer = db_path.with_name(db_path.name + ".dvc")
    pointer.write_text(
        f"outs:\n- md5: {md5}\n  size: {len(blob)}\n  hash: md5\n  path: {db_path.name}\n"
    )
    return pointer, md5


def _fixture_remote(tmp_path: Path) -> tuple[Path, FileTransport]:
    """The fixture corpus staged behind an offline transport."""
    db = build_fixture_corpus(tmp_path / "corpus.db")
    pointer, _ = _write_pointer(db)
    return pointer, FileTransport(db.read_bytes())


# --- resolver -------------------------------------------------------------------


def test_resolver_maps_pointer_to_remote_key(tmp_path: Path) -> None:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    pointer, md5 = _write_pointer(db)
    remote = corpus_ranged.resolve_pointer(pointer, REMOTE_URL)
    assert remote.bucket == "test-bucket"
    assert remote.key == f"store/files/md5/{md5[:2]}/{md5[2:]}"
    assert remote.size == db.stat().st_size
    assert remote.md5 == md5


def test_resolver_handles_prefixless_bucket(tmp_path: Path) -> None:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    pointer, md5 = _write_pointer(db)
    remote = corpus_ranged.resolve_pointer(pointer, "s3://bare-bucket")
    assert remote.key == f"files/md5/{md5[:2]}/{md5[2:]}"


@pytest.mark.parametrize(
    ("pointer_text", "expected"),
    [
        ("outs: []\n", "exactly one out"),
        ("outs:\n- md5: nope\n  size: 5\n  path: corpus.db\n", "no valid md5"),
        (f"outs:\n- md5: {'a' * 32}\n  size: 0\n  path: corpus.db\n", "no positive size"),
        ("notouts: 1\n", "exactly one out"),
        ("{", "not valid YAML"),
    ],
)
def test_resolver_fails_loudly_on_broken_pointer(
    tmp_path: Path, pointer_text: str, expected: str
) -> None:
    pointer = tmp_path / "corpus.db.dvc"
    pointer.write_text(pointer_text)
    with pytest.raises(corpus_ranged.RangedBackendError, match=expected):
        corpus_ranged.resolve_pointer(pointer, REMOTE_URL)


def test_resolver_fails_loudly_on_missing_pointer_and_bad_url(tmp_path: Path) -> None:
    with pytest.raises(corpus_ranged.RangedBackendError, match="no DVC pointer"):
        corpus_ranged.resolve_pointer(tmp_path / "corpus.db.dvc", REMOTE_URL)
    pointer = tmp_path / "corpus.db.dvc"
    pointer.write_text(f"outs:\n- md5: {'a' * 32}\n  size: 5\n  path: corpus.db\n")
    with pytest.raises(corpus_ranged.RangedBackendError, match="not an s3://"):
        corpus_ranged.resolve_pointer(pointer, "gs://elsewhere/prefix")


# --- equivalence: ranged results == local results --------------------------------


def test_ranged_backend_matches_local(tmp_path: Path) -> None:
    pointer, transport = _fixture_remote(tmp_path)
    db = tmp_path / "corpus.db"
    prior_query = corpus.PriorQuery(court="ca9", resolved_only=False)

    with corpus.connect(db) as conn:
        local = {
            "count": corpus.count(conn),
            "snapshots": corpus.snapshot_count(conn),
            "row": corpus.get_row(conn, FIXTURE_CASES[0].case_id),
            "priors": corpus.retrieve_priors(conn, prior_query),
            "events": corpus.events_for_case(conn, FIXTURE_CASES[0].case_id),
            "open": list(corpus.iter_open_events(conn)),
            "snapshot": corpus.latest_snapshot(conn, FIXTURE_CASES[0].case_id),
        }

    with corpus_ranged.connect_ranged(pointer, REMOTE_URL, transport=transport) as ranged:
        assert corpus.count(ranged) == local["count"]
        assert corpus.snapshot_count(ranged) == local["snapshots"]
        assert corpus.get_row(ranged, FIXTURE_CASES[0].case_id) == local["row"]
        assert corpus.retrieve_priors(ranged, prior_query) == local["priors"]
        assert corpus.events_for_case(ranged, FIXTURE_CASES[0].case_id) == local["events"]
        assert list(corpus.iter_open_events(ranged)) == local["open"]
        assert corpus.latest_snapshot(ranged, FIXTURE_CASES[0].case_id) == local["snapshot"]


# --- efficiency: point lookups are bounded, not scans ----------------------------


def _many_page_corpus(tmp_path: Path) -> Path:
    """A corpus whose cases table spans many 64 KB pages."""
    db = tmp_path / "corpus.db"
    rows = [
        corpus.CorpusRow(
            case_id=f"ca9/{i}",
            court="ca9",
            docket_number=f"23-{i}",
            disposition=Disposition.granted,
            opinion_text="x" * 4096,  # pad each row so ~16 rows fill a 64 KB page
        )
        for i in range(1000)
    ]
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, rows)
    return db


def test_point_lookup_request_count_is_bounded(tmp_path: Path) -> None:
    db = _many_page_corpus(tmp_path)
    pointer, _ = _write_pointer(db)
    transport = FileTransport(db.read_bytes())
    # One block == one page: the GET count mirrors the page-read count, so an
    # accidental table scan would blow the bound by an order of magnitude.
    block = corpus.RANGED_PAGE_SIZE
    total_blocks = -(-db.stat().st_size // block)
    assert total_blocks > 20, "fixture must span many blocks for the bound to mean anything"
    with corpus_ranged.connect_ranged(
        pointer, REMOTE_URL, transport=transport, block_size=block
    ) as ranged:
        assert corpus.get_row(ranged, "ca9/500") is not None
        stats = ranged.stats
        assert stats.gets <= 8, f"indexed point lookup took {stats.gets} GETs"
        assert stats.bytes_fetched <= 8 * block


def test_repeated_lookup_is_served_from_cache(tmp_path: Path) -> None:
    pointer, transport = _fixture_remote(tmp_path)
    with corpus_ranged.connect_ranged(pointer, REMOTE_URL, transport=transport) as ranged:
        first = corpus.get_row(ranged, FIXTURE_CASES[0].case_id)
        gets_after_first = ranged.stats.gets
        assert corpus.get_row(ranged, FIXTURE_CASES[0].case_id) == first
        assert ranged.stats.gets == gets_after_first, "second lookup must hit the block cache"


# --- read-only enforcement --------------------------------------------------------


def test_write_attempt_fails_cleanly(tmp_path: Path) -> None:
    pointer, transport = _fixture_remote(tmp_path)
    with corpus_ranged.connect_ranged(pointer, REMOTE_URL, transport=transport) as ranged:
        with pytest.raises(apsw.ReadOnlyError):
            ranged.execute(
                "INSERT INTO events (case_id, event_id, court, kind) "
                "VALUES ('x/1', 'evt-x', 'x', 'motion')"
            )
        # The connection still serves reads after the rejected write.
        assert corpus.count(ranged) == len(FIXTURE_CASES)


# --- the boto3 transport and the env-driven seam (moto) --------------------------


def _stage_moto_bucket(pointer: Path, blob: bytes) -> None:
    remote = corpus_ranged.resolve_pointer(pointer, REMOTE_URL)
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket=remote.bucket)
    client.put_object(Bucket=remote.bucket, Key=remote.key, Body=blob)


@mock_aws
def test_s3_transport_serves_exact_ranges(tmp_path: Path) -> None:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    pointer, _ = _write_pointer(db)
    blob = db.read_bytes()
    _stage_moto_bucket(pointer, blob)
    remote = corpus_ranged.resolve_pointer(pointer, REMOTE_URL)
    transport = corpus_ranged.S3RangeTransport(remote.bucket)
    assert transport(remote.key, 0, 15) == blob[:16]
    assert transport(remote.key, 100, 299) == blob[100:300]


@mock_aws
def test_connect_readonly_ranged_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    pointer, _ = _write_pointer(db)
    _stage_moto_bucket(pointer, db.read_bytes())
    db.unlink()  # ranged access must not need (or recreate) the local blob
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "ranged")
    monkeypatch.setenv("FEDCOURTS_DVC_REMOTE_URL", REMOTE_URL)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    with corpus.connect_readonly(db) as conn:
        assert corpus.count(conn) == len(FIXTURE_CASES)
        assert corpus.latest_snapshot(conn, FIXTURE_CASES[0].case_id) == (
            date.fromisoformat(str(FIXTURE_CASES[0].snapshot_date)),
            FIXTURE_CASES[0].snapshot_payload(),
        )
    assert not db.exists(), "the ranged backend must not create a local file"

    # The provisioning read path (store.open_events) rides the same seam;
    # ca9/103 is the fixture's open-event appeals case.
    events = store.open_events(db, "ca9", 103)
    assert events == ["evt-appeal-disposition"]


@mock_aws
def test_stub_cascade_reads_via_ranged_backend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The local cascade's corpus reads ride the ranged seam — no local blob needed.

    The end-to-end provisioning shape the integration-corpus workflow's optional
    cascade cell exercises against the real remote: with the backend set to
    ``ranged`` in the environment, ``run_cascade`` provisions the snapshot,
    predicts with the offline stub engine, and validates the ledger without a
    ``dvc pull``-ed corpus file on disk.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    build_fixture_corpus(db)
    pointer, _ = _write_pointer(db)
    _stage_moto_bucket(pointer, db.read_bytes())
    db.unlink()  # ranged access must not need (or recreate) the local blob
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "ranged")
    monkeypatch.setenv("FEDCOURTS_DVC_REMOTE_URL", REMOTE_URL)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    # ca9/103 is the fixture's open-event appeals case: predict only, nothing
    # to evaluate — the same shape as a real open case.
    report = run_cascade(
        corpus_db_path=db,
        data_root=tmp_path / "data",
        config_root=Path("config"),
        court="ca9",
        docket=103,
        run_id="20260628T120000Z",
    )

    assert report.valid, report.problems
    assert report.snapshot is not None and report.snapshot.is_file()
    assert report.predictions and not report.evaluations
    assert not db.exists(), "the ranged cascade must not create a local corpus file"


def test_connect_readonly_ranged_without_remote_url_fails_loudly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "ranged")
    monkeypatch.delenv("FEDCOURTS_DVC_REMOTE_URL", raising=False)
    monkeypatch.delenv("DVC_REMOTE_URL", raising=False)
    with (
        pytest.raises(corpus_ranged.RangedBackendError, match="remote URL"),
        corpus.connect_readonly(tmp_path / "corpus.db"),
    ):
        pass
