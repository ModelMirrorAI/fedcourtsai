"""The corpus query service (:mod:`fedcourtsai.corpus_service`).

These lock the properties that make the sidecar a pure transport change: rows
byte-identical to the direct read path, the per-request ranged read-stats
delta, and the clean failure contract (unreachable service, unknown path,
malformed body).
"""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import httpx
import pytest

from fedcourtsai import corpus, corpus_ranged, corpus_service
from fedcourtsai.fixture import build_fixture_corpus
from tests.conftest import FixtureCorpus

REMOTE_URL = "s3://test-bucket/store"


@contextmanager
def _running_server(db_path: Path) -> Iterator[str]:
    server = corpus_service.create_server(db_path, backend="local")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_query_round_trip_matches_direct_read(fixture_corpus: FixtureCorpus) -> None:
    q = corpus.PriorQuery(court="ca9", judges=["smith"])
    with _running_server(fixture_corpus.db_path) as url:
        response = corpus_service.client_query(url, q, limit=20, full=False)
    with corpus.connect_readonly(fixture_corpus.db_path, backend="local") as conn:
        direct = [corpus.prior_payload(row) for row in corpus.retrieve_priors(conn, q, limit=20)]
    assert direct  # the fixture genuinely matches something
    served = [json.dumps(r, sort_keys=True) for r in response.rows]
    assert served == [json.dumps(r, sort_keys=True) for r in direct]
    assert response.reads is None  # local backend: nothing was transferred


def test_query_full_toggles_opinion_text(fixture_corpus: FixtureCorpus) -> None:
    q = corpus.PriorQuery(court="ca1")
    with _running_server(fixture_corpus.db_path) as url:
        bare = corpus_service.client_query(url, q, limit=5, full=False)
        full = corpus_service.client_query(url, q, limit=5, full=True)
    assert "opinion_text" not in bare.rows[0]
    assert "dismissed for lack of jurisdiction" in str(full.rows[0]["opinion_text"])


def test_open_events_round_trip(fixture_corpus: FixtureCorpus) -> None:
    with _running_server(fixture_corpus.db_path) as url:
        response = corpus_service.client_open_events(url, "ca9", 103)
    assert response.event_ids  # ca9/103 is the fixture's open case
    assert all(isinstance(eid, str) for eid in response.event_ids)


def test_health_unknown_path_and_malformed_body(fixture_corpus: FixtureCorpus) -> None:
    with _running_server(fixture_corpus.db_path) as url:
        health = httpx.get(f"{url}/healthz", timeout=5)
        assert health.status_code == 200
        assert health.json()["status"] == "ok"
        assert health.json()["backend"] == "local"
        assert httpx.get(f"{url}/nope", timeout=5).status_code == 404
        assert httpx.post(f"{url}/v1/nope", content=b"{}", timeout=5).status_code == 404
        bad = httpx.post(f"{url}/v1/query", content=b'{"schema_version":"1.0"}', timeout=5)
        assert bad.status_code == 400
        assert "error" in bad.json()


def test_client_wraps_unreachable_and_non_200() -> None:
    q = corpus.PriorQuery()
    with pytest.raises(corpus_service.CorpusServiceError, match="is the sidecar running"):
        corpus_service.client_query("http://127.0.0.1:9", q, limit=1, full=False)


def test_client_wraps_rejection(fixture_corpus: FixtureCorpus) -> None:
    # A base URL whose paths all 404 on the real server: the client must wrap
    # the non-200 in CorpusServiceError, naming the path and status.
    q = corpus.PriorQuery()
    with (
        _running_server(fixture_corpus.db_path) as url,
        pytest.raises(corpus_service.CorpusServiceError, match="rejected /v1/query \\(404\\)"),
    ):
        corpus_service.client_query(f"{url}/wrong-prefix", q, limit=1, full=False)


# --- the ranged read-stats delta, in-process over an offline transport ---


class _FileTransport:
    """Serve byte ranges of an in-memory blob (the test_corpus_ranged pattern)."""

    def __init__(self, blob: bytes) -> None:
        self.blob = blob
        self.calls: list[tuple[int, int]] = []

    def __call__(self, key: str, start: int, end: int) -> bytes:
        self.calls.append((start, end))
        return self.blob[start : end + 1]


def _ranged_conn(tmp_path: Path) -> tuple[Path, _FileTransport]:
    db = build_fixture_corpus(tmp_path / "corpus.db")
    blob = db.read_bytes()
    sha256 = hashlib.sha256(blob).hexdigest()
    pointer = db.with_name(db.name + ".ref")
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
    return pointer, _FileTransport(blob)


def test_ranged_reads_delta_per_request(tmp_path: Path) -> None:
    pointer, transport = _ranged_conn(tmp_path)
    request = corpus_service.QueryRequest(
        schema_version="1.0", query=corpus.PriorQuery(court="ca9"), limit=5, full=False
    )
    service = corpus_service.CorpusService(
        lambda: corpus_ranged.connect_ranged(pointer, REMOTE_URL, transport=transport),
        backend="ranged",
    )
    try:
        first = service.query(request)
        second = service.query(request)
    finally:
        service.close()
    # The request that triggers the lazy open is charged the open's transfer
    # (the true cold cost lands on a real evidence line); the repeat reads the
    # warm block cache and honestly reports zero rather than the connection's
    # cumulative totals.
    assert transport.calls  # the open genuinely transferred bytes
    assert first.reads is not None and first.reads.gets > 0
    assert second.reads == corpus_service.ReadCounters(gets=0, bytes=0)
    assert first.rows and first.rows == second.rows


def test_backend_failure_returns_redacted_500(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A ranged sidecar with no remote URL configured fails on first use; the
    # wire body names the exception type only (backend errors can embed the
    # remote URL, and the client echoes this body into workflow logs).
    monkeypatch.delenv("FEDCOURTS_CORPUS_REMOTE_URL", raising=False)
    monkeypatch.delenv("CORPUS_REMOTE_URL", raising=False)
    server = corpus_service.create_server(tmp_path / "corpus.db", backend="ranged")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_address[1]}"
    q = corpus.PriorQuery()
    try:
        with pytest.raises(
            corpus_service.CorpusServiceError, match="rejected /v1/query \\(500\\)"
        ) as exc_info:
            corpus_service.client_query(url, q, limit=1, full=False)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    message = str(exc_info.value)
    assert "see the sidecar log" in message
    assert "s3://" not in message  # no backend detail rides the wire


def test_oversized_request_is_rejected(fixture_corpus: FixtureCorpus) -> None:
    with _running_server(fixture_corpus.db_path) as url:
        response = httpx.post(f"{url}/v1/query", content=b"x" * 2_000_000, timeout=10)
    assert response.status_code == 413


def test_client_rejects_limit_past_service_ceiling(fixture_corpus: FixtureCorpus) -> None:
    q = corpus.PriorQuery()
    with pytest.raises(corpus_service.CorpusServiceError, match="invalid corpus service request"):
        corpus_service.client_query(
            "http://127.0.0.1:1", q, limit=corpus_service.MAX_QUERY_LIMIT + 1, full=False
        )


def test_query_empty_result_carries_coverage_notes(fixture_corpus: FixtureCorpus) -> None:
    # A zero-row result through a sparse filter names the data gap so a cell
    # can tell "no data" from "no match"; a non-empty result carries no notes.
    with _running_server(fixture_corpus.db_path) as url:
        empty = corpus_service.client_query(
            url,
            corpus.PriorQuery(court="ca9", citations=["999 U.S. 999"]),
            limit=5,
            full=False,
        )
        matched = corpus_service.client_query(
            url, corpus.PriorQuery(court="ca9", judges=["smith"]), limit=5, full=False
        )
    assert empty.rows == []
    assert len(empty.notes) == 1 and "citations filter" in empty.notes[0]
    assert matched.rows and matched.notes == []
