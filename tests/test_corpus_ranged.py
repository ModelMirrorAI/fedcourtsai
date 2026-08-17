"""The ranged corpus backend (``fedcourtsai.corpus_ranged``), fully offline.

Everything below the transport seam is exercised with an in-memory transport
serving a local file; the boto3 transport itself (and the env-driven
``connect_readonly`` path) runs against moto's S3 stand-in. No test touches
the network.
"""

from __future__ import annotations

import hashlib
import io
import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

import apsw
import boto3
import pytest
from botocore.exceptions import (
    ClientError,
    ConnectionClosedError,
    EndpointConnectionError,
    IncompleteReadError,
)
from moto import mock_aws
from typer.testing import CliRunner

from fedcourtsai import cli, corpus, corpus_ranged, store
from fedcourtsai.fixture import FIXTURE_CASES, build_fixture_corpus
from fedcourtsai.paths import CasePaths
from fedcourtsai.pipeline.cascade import run_cascade
from fedcourtsai.schemas import Disposition

REMOTE_URL = "s3://test-bucket/store"
_SHA = "a" * 64


class FileTransport:
    """Serve byte ranges of an in-memory blob, recording every fetch."""

    def __init__(self, blob: bytes) -> None:
        self.blob = blob
        self.calls: list[tuple[int, int]] = []

    def __call__(self, key: str, start: int, end: int) -> bytes:
        self.calls.append((start, end))
        return self.blob[start : end + 1]


def _write_pointer(db_path: Path) -> tuple[Path, str]:
    """A JSON ``.ref`` pointer for ``db_path`` in the committed pointer's exact shape."""
    blob = db_path.read_bytes()
    sha256 = hashlib.sha256(blob).hexdigest()
    pointer = db_path.with_name(db_path.name + ".ref")
    pointer.write_text(
        json.dumps(
            {
                "key": f"index/sha256/{sha256}",
                "size": len(blob),
                "sha256": sha256,
                "schema_version": "1.0",
            }
        )
        + "\n"
    )
    return pointer, sha256


def _fixture_remote(tmp_path: Path) -> tuple[Path, FileTransport]:
    """The fixture corpus staged behind an offline transport."""
    db = build_fixture_corpus(tmp_path / "corpus.db")
    pointer, _ = _write_pointer(db)
    return pointer, FileTransport(db.read_bytes())


# --- resolver -------------------------------------------------------------------


def test_resolver_maps_pointer_to_remote_key(tmp_path: Path) -> None:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    pointer, sha256 = _write_pointer(db)
    remote = corpus_ranged.resolve_pointer(pointer, REMOTE_URL)
    assert remote.bucket == "test-bucket"
    assert remote.key == f"store/index/sha256/{sha256}"
    assert remote.size == db.stat().st_size
    assert remote.checksum == sha256


def test_resolver_handles_prefixless_bucket(tmp_path: Path) -> None:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    pointer, sha256 = _write_pointer(db)
    remote = corpus_ranged.resolve_pointer(pointer, "s3://bare-bucket")
    assert remote.key == f"index/sha256/{sha256}"


def test_find_pointer_returns_ref_and_fails_when_absent(tmp_path: Path) -> None:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    ref, _ = _write_pointer(db)
    assert corpus_ranged.find_pointer(db) == ref
    ref.unlink()
    with pytest.raises(corpus_ranged.RangedBackendError, match="no corpus pointer"):
        corpus_ranged.find_pointer(db)


@pytest.mark.parametrize(
    ("pointer_text", "expected"),
    [
        ("{", "not valid JSON"),
        ("[1, 2]\n", "must be a JSON object"),
        (
            json.dumps({"size": 5, "sha256": _SHA, "schema_version": "1.0"}),
            "no remote key",
        ),
        (
            json.dumps(
                {"key": "index/sha256/nope", "size": 5, "sha256": "nope", "schema_version": "1.0"}
            ),
            "no valid sha256",
        ),
        (
            json.dumps(
                {"key": f"index/sha256/{_SHA}", "size": 0, "sha256": _SHA, "schema_version": "1.0"}
            ),
            "no positive size",
        ),
        (
            json.dumps(
                {"key": f"index/sha256/{_SHA}", "size": 5, "sha256": _SHA, "schema_version": "9.9"}
            ),
            "schema_version",
        ),
        (
            # A key/digest divergence could route the digest-blind ranged
            # reader to a different object than the checksum vouches for.
            json.dumps(
                {
                    "key": f"index/sha256/{'b' * 64}",
                    "size": 5,
                    "sha256": _SHA,
                    "schema_version": "1.0",
                }
            ),
            "does not match its own",
        ),
    ],
)
def test_resolver_fails_loudly_on_broken_pointer(
    tmp_path: Path, pointer_text: str, expected: str
) -> None:
    pointer = tmp_path / "corpus.db.ref"
    pointer.write_text(pointer_text)
    with pytest.raises(corpus_ranged.RangedBackendError, match=expected):
        corpus_ranged.resolve_pointer(pointer, REMOTE_URL)


def test_resolver_fails_loudly_on_missing_pointer_and_bad_url(tmp_path: Path) -> None:
    with pytest.raises(corpus_ranged.RangedBackendError, match="no corpus pointer"):
        corpus_ranged.resolve_pointer(tmp_path / "corpus.db.ref", REMOTE_URL)
    pointer = tmp_path / "corpus.db.ref"
    pointer.write_text(
        json.dumps(
            {"key": f"index/sha256/{_SHA}", "size": 5, "sha256": _SHA, "schema_version": "1.0"}
        )
    )
    with pytest.raises(corpus_ranged.RangedBackendError, match="not an s3://"):
        corpus_ranged.resolve_pointer(pointer, "gs://elsewhere/prefix")


# --- equivalence: ranged results == local results --------------------------------


def test_ranged_backend_matches_local(tmp_path: Path) -> None:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    with corpus.connect(db) as conn:
        stamped = corpus.get_row(conn, FIXTURE_CASES[0].case_id)
        assert stamped is not None
        # A pull stamp, so the freshness aggregate below compares real dates.
        corpus.upsert_rows(conn, [stamped.model_copy(update={"last_pulled": date(2026, 8, 16)})])
    pointer, _ = _write_pointer(db)
    transport = FileTransport(db.read_bytes())
    prior_query = corpus.PriorQuery(court="ca9", resolved_only=False)

    with corpus.connect(db) as conn:
        local = {
            "count": corpus.count(conn),
            "snapshots": corpus.snapshot_count(conn),
            "latest_snapshot_date": corpus.latest_snapshot_date(conn),
            "latest_pull": corpus.latest_pull_date(conn),
            "row": corpus.get_row(conn, FIXTURE_CASES[0].case_id),
            "priors": corpus.retrieve_priors(conn, prior_query),
            "events": corpus.events_for_case(conn, FIXTURE_CASES[0].case_id),
            "open": list(corpus.iter_open_events(conn)),
            "snapshot": corpus.latest_snapshot(conn, FIXTURE_CASES[0].case_id),
        }

    with corpus_ranged.connect_ranged(pointer, REMOTE_URL, transport=transport) as ranged:
        assert corpus.count(ranged) == local["count"]
        assert corpus.snapshot_count(ranged) == local["snapshots"]
        # The freshness aggregates `corpus-info` prints: MAX over an apsw cursor
        # reads the same as over sqlite3, so `--corpus-backend ranged` is dated too.
        assert corpus.latest_snapshot_date(ranged) == local["latest_snapshot_date"]
        assert corpus.latest_pull_date(ranged) == local["latest_pull"]
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
    # The legacy env alias must keep working until the repo variable is renamed;
    # clear the preferred names so an ambient value cannot shadow the check.
    monkeypatch.delenv("FEDCOURTS_CORPUS_REMOTE_URL", raising=False)
    monkeypatch.delenv("CORPUS_REMOTE_URL", raising=False)
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

    The end-to-end provisioning shape the integration-test workflow's
    stub-cascade scenario exercises against the real remote: with the backend set to
    ``ranged`` in the environment, ``run_cascade`` provisions the snapshot,
    predicts with the offline stub engine, and validates the ledger without a
    pulled corpus file on disk.
    """
    db = corpus.corpus_db_path(tmp_path / "corpus")
    build_fixture_corpus(db)
    pointer, _ = _write_pointer(db)
    _stage_moto_bucket(pointer, db.read_bytes())
    db.unlink()  # ranged access must not need (or recreate) the local blob
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "ranged")
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", REMOTE_URL)
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
    for name in (
        "FEDCOURTS_CORPUS_REMOTE_URL",
        "CORPUS_REMOTE_URL",
        "FEDCOURTS_DVC_REMOTE_URL",
        "DVC_REMOTE_URL",
    ):
        monkeypatch.delenv(name, raising=False)
    with (
        pytest.raises(corpus_ranged.RangedBackendError, match="remote URL"),
        corpus.connect_readonly(tmp_path / "corpus.db"),
    ):
        pass


@mock_aws
def test_cli_materialize_event_reads_via_ranged_backend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A ranged predict cell can materialize its event.yaml with no local corpus.

    The cell-side command reads the events table through the same backend seam as
    its sibling reads; a local-only open here would silently create an empty
    corpus and report the event missing, failing every ranged matrix cell.
    """
    corpus_root = tmp_path / "corpus"
    db = corpus.corpus_db_path(corpus_root)
    build_fixture_corpus(db)
    pointer, _ = _write_pointer(db)
    _stage_moto_bucket(pointer, db.read_bytes())
    db.unlink()  # ranged access must not need (or recreate) the local blob
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "ranged")
    monkeypatch.setenv("FEDCOURTS_CORPUS_REMOTE_URL", REMOTE_URL)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    result = CliRunner().invoke(
        cli.app,
        [
            "materialize-event",
            "--court",
            "scotus",
            "--docket",
            "305",
            "--event",
            "evt-petition-disposition",
        ],
    )
    assert result.exit_code == 0, result.output
    dest = CasePaths(tmp_path / "data", "scotus", 305).event("evt-petition-disposition").event_file
    assert dest.is_file()
    assert "ranged corpus reads" in result.stderr  # the per-query egress evidence
    assert not db.exists(), "the ranged read must not create a local corpus file"


# --- transport retry: transients absorbed, permanent faults loud -----------------

_KEY = "index/sha256/" + _SHA


class StubS3Client:
    """A ``get_object`` stand-in replaying a scripted sequence of outcomes.

    An ``Exception`` outcome is raised, a ``bytes`` outcome is served as a
    body; the last outcome repeats, so a script can outlast the attempt budget
    and let the budget itself be what the assertion measures.
    """

    def __init__(self, outcomes: Sequence[Exception | bytes]) -> None:
        self._outcomes = list(outcomes)
        self.calls: list[dict[str, str]] = []

    def get_object(self, **kwargs: str) -> dict[str, Any]:
        self.calls.append(kwargs)
        outcome = self._outcomes[min(len(self.calls), len(self._outcomes)) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return {"Body": io.BytesIO(outcome)}


def _client_error(code: str, status: int) -> ClientError:
    """A botocore ``ClientError`` in the exact shape boto3 raises from S3."""
    return ClientError(
        {
            "Error": {"Code": code, "Message": f"stub {code}"},
            "ResponseMetadata": {"HTTPStatusCode": status},
        },
        "GetObject",
    )


def _stub_transport(
    monkeypatch: pytest.MonkeyPatch,
    outcomes: Sequence[Exception | bytes],
    *,
    sleeps: list[float] | None = None,
) -> corpus_ranged.S3RangeTransport:
    """The real transport with its S3 client and its pause replaced.

    boto3.client is patched out before construction so the test never builds a
    real client: an ambient AWS profile (the maintainer's SSO flow) must not
    be read, and the ~seconds of first-construction cost must not be paid.
    """
    import boto3  # noqa: PLC0415

    recorded: list[float] = [] if sleeps is None else sleeps
    monkeypatch.setattr(corpus_ranged, "_sleep", recorded.append)
    stub = StubS3Client(outcomes)
    monkeypatch.setattr(boto3, "client", lambda *a, **k: stub)
    return corpus_ranged.S3RangeTransport("test-bucket")


def _stub_calls(transport: corpus_ranged.S3RangeTransport) -> list[dict[str, str]]:
    client = transport._client
    assert isinstance(client, StubS3Client)
    return client.calls


def _warnings(captured: str) -> list[str]:
    return [line for line in captured.splitlines() if line.startswith("::warning::")]


@pytest.mark.parametrize(
    "fault",
    [
        _client_error("SlowDown", 503),
        _client_error("InternalError", 500),
        _client_error("ServiceUnavailable", 503),
        # S3 answers a stalled upload/read with a 4xx status but a transient
        # meaning, so the code — not the status — is what classifies it.
        _client_error("RequestTimeout", 400),
        # An unnamed 5xx still counts: the status carries the transience.
        _client_error("SomeNewServerFault", 502),
        # The endpoint URL embeds the bucket, exactly as botocore renders it —
        # the leak-check below is only load-bearing because of that.
        EndpointConnectionError(endpoint_url="https://test-bucket.s3.us-east-1.amazonaws.com/x"),
        ConnectionClosedError(endpoint_url="https://test-bucket.s3.us-east-1.amazonaws.com/x"),
        IncompleteReadError(actual_bytes=3, expected_bytes=7),
    ],
)
def test_transient_fault_is_retried_until_it_succeeds(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], fault: Exception
) -> None:
    transport = _stub_transport(monkeypatch, [fault, fault, b"payload"])
    assert transport(_KEY, 0, 6) == b"payload"
    assert len(_stub_calls(transport)) == 3, "both transient faults must have been retried"

    warnings = _warnings(capsys.readouterr().err)
    assert len(warnings) == 2, warnings
    assert "attempt 1/3" in warnings[0]
    assert "attempt 2/3" in warnings[1]
    for line in warnings:
        # The key and range make the flake attributable to one object read.
        assert _KEY in line
        assert "bytes=0-6" in line
        assert "test-bucket" not in line, "the warning names the read, not the remote"


@pytest.mark.parametrize(
    ("code", "status"),
    [("AccessDenied", 403), ("NoSuchKey", 404), ("PermanentRedirect", 301), ("InvalidRange", 416)],
)
def test_permanent_fault_fails_immediately_without_retry(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], code: str, status: int
) -> None:
    """A misconfigured remote is a diagnosis, not a flake — no budget is spent on it."""
    fault = _client_error(code, status)
    transport = _stub_transport(monkeypatch, [fault, b"unreachable"])
    with pytest.raises(ClientError) as raised:
        transport(_KEY, 0, 6)
    assert raised.value is fault, "the original fault must propagate unwrapped"
    assert len(_stub_calls(transport)) == 1
    assert _warnings(capsys.readouterr().err) == []


def test_exhausted_budget_raises_ranged_backend_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    sleeps: list[float] = []
    fault = _client_error("ServiceUnavailable", 503)
    transport = _stub_transport(monkeypatch, [fault], sleeps=sleeps)
    attempts = len(corpus_ranged.RETRY_BACKOFF_SECONDS) + 1
    with pytest.raises(corpus_ranged.RangedBackendError) as raised:
        transport(_KEY, 0, 6)

    message = str(raised.value)
    assert f"failed after {attempts} attempts" in message
    assert _KEY in message and "bytes=0-6" in message
    assert raised.value.__cause__ is fault
    assert len(_stub_calls(transport)) == attempts, "the budget must be spent exactly once over"
    assert len(_warnings(capsys.readouterr().err)) == attempts - 1

    # Each pause sits on its scheduled base, extended by at most the jitter.
    assert len(sleeps) == len(corpus_ranged.RETRY_BACKOFF_SECONDS)
    for pause, base in zip(sleeps, corpus_ranged.RETRY_BACKOFF_SECONDS, strict=True):
        assert base <= pause <= base * (1 + corpus_ranged.RETRY_JITTER)


def test_successful_read_neither_sleeps_nor_warns(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    sleeps: list[float] = []
    transport = _stub_transport(monkeypatch, [b"payload"], sleeps=sleeps)
    assert transport(_KEY, 0, 6) == b"payload"
    assert _stub_calls(transport) == [{"Bucket": "test-bucket", "Key": _KEY, "Range": "bytes=0-6"}]
    assert sleeps == []
    assert capsys.readouterr().err == ""
