import json
import threading
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus_service
from fedcourtsai.cli import app
from tests.conftest import FixtureCorpus

runner = CliRunner()


def _rows(output: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in output.splitlines() if line.strip()]


def test_query_ranks_and_omits_opinion_text(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--court", "ca9", "--judge", "smith"])
    assert result.exit_code == 0, result.output
    rows = _rows(result.stdout)
    # ca9/101 and ca9/102 both share judge smith; ca9/102 (decided later) ranks
    # first on recency, and the open ca9/103 is excluded by the resolved-only default.
    assert [r["case_id"] for r in rows] == ["ca9/102", "ca9/101"]
    assert "opinion_text" not in rows[0]


def test_query_full_includes_opinion_text(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--court", "ca1", "--full"])
    assert result.exit_code == 0, result.output
    rows = _rows(result.stdout)
    assert rows[0]["case_id"] == "ca1/201"
    assert "dismissed for lack of jurisdiction" in str(rows[0]["opinion_text"])


def test_query_rows_carry_caption_and_derived_era(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--court", "ca9", "--judge", "smith"])
    assert result.exit_code == 0, result.output
    row = _rows(result.stdout)[0]
    # The retrieval-judgment fields: caption stored on the row, era derived.
    assert row["case_name"] == "Cohen v. Pacific Mutual"
    assert row["era"] == "2020s"
    assert row["date_filed"] == "2022-06-02"


def test_query_era_filter(fixture_corpus: FixtureCorpus) -> None:
    kept = runner.invoke(app, ["query", "--court", "ca9", "--era", "2020s"])
    none = runner.invoke(app, ["query", "--court", "ca9", "--era", "1890s"])
    assert kept.exit_code == 0 and none.exit_code == 0
    assert _rows(kept.stdout) and not _rows(none.stdout)


def test_query_include_open(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--court", "ca9", "--judge", "berzon", "--include-open"])
    assert result.exit_code == 0, result.output
    # berzon sits on ca9/101 (resolved) and ca9/103 (open); --include-open keeps both.
    assert {r["case_id"] for r in _rows(result.stdout)} == {"ca9/101", "ca9/103"}


def test_query_unknown_disposition_errors(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["query", "--disposition", "nope"])
    assert result.exit_code == 2
    assert "Unknown disposition" in result.stderr


def test_query_missing_corpus_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    result = runner.invoke(app, ["query"])
    assert result.exit_code == 1
    assert "No corpus" in result.stderr


# --- the service backend: same command, forwarded to a corpus-serve sidecar ---


def _serve(db_path: Path) -> tuple[corpus_service._CorpusHTTPServer, str]:
    server = corpus_service.create_server(db_path, backend="local")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def test_query_service_backend_output_matches_local(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    local = runner.invoke(app, ["query", "--court", "ca9", "--judge", "smith"])
    server, url = _serve(fixture_corpus.db_path)
    try:
        monkeypatch.setenv("FEDCOURTS_CORPUS_SERVICE_URL", url)
        served = runner.invoke(
            app, ["query", "--court", "ca9", "--judge", "smith", "--corpus-backend", "service"]
        )
    finally:
        server.shutdown()
        server.server_close()
    assert served.exit_code == 0, served.output
    # The service is a transport change, not a different surface: same bytes.
    assert served.stdout == local.stdout


def test_open_events_service_backend_matches_local(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    local = runner.invoke(app, ["open-events", "--court", "ca9", "--docket", "103"])
    server, url = _serve(fixture_corpus.db_path)
    try:
        monkeypatch.setenv("FEDCOURTS_CORPUS_SERVICE_URL", url)
        served = runner.invoke(
            app,
            ["open-events", "--court", "ca9", "--docket", "103", "--corpus-backend", "service"],
        )
    finally:
        server.shutdown()
        server.server_close()
    assert served.exit_code == 0, served.output
    assert served.stdout == local.stdout
    assert local.stdout.strip()  # the fixture's open case genuinely has events


def test_query_service_backend_prints_relayed_read_stats(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_query(
        base_url: str, query: object, *, limit: int, full: bool
    ) -> corpus_service.QueryResponse:
        return corpus_service.QueryResponse(
            schema_version="1.0",
            rows=[{"case_id": "scotus/1"}],
            reads=corpus_service.ReadCounters(gets=3, bytes=1024),
        )

    monkeypatch.setenv("FEDCOURTS_CORPUS_SERVICE_URL", "http://127.0.0.1:1")
    monkeypatch.setattr(corpus_service, "client_query", fake_query)
    result = runner.invoke(app, ["query", "--corpus-backend", "service"])
    assert result.exit_code == 0, result.output
    # The sidecar's per-request delta feeds the exact stderr evidence line the
    # prompts tell agents to record.
    assert "ranged corpus reads: 3 GET(s), 1024 byte(s)" in result.stderr


def test_query_service_backend_unreachable_exits_one(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_SERVICE_URL", "http://127.0.0.1:9")
    result = runner.invoke(app, ["query", "--corpus-backend", "service"])
    assert result.exit_code == 1
    assert "is the sidecar running" in result.stderr


def test_query_service_backend_needs_url(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("FEDCOURTS_CORPUS_SERVICE_URL", raising=False)
    result = runner.invoke(app, ["query", "--corpus-backend", "service"])
    assert result.exit_code == 2
    assert "FEDCOURTS_CORPUS_SERVICE_URL" in result.stderr


def test_corpus_info_rejects_service_backend(fixture_corpus: FixtureCorpus) -> None:
    result = runner.invoke(app, ["corpus-info", "--corpus-backend", "service"])
    assert result.exit_code == 2
    assert "choose local, ranged" in result.stderr


def test_corpus_serve_rejects_non_connection_backends(fixture_corpus: FixtureCorpus) -> None:
    for backend in ("service", "casestore"):
        result = runner.invoke(app, ["corpus-serve", "--corpus-backend", backend])
        assert result.exit_code == 2, result.output


def test_query_service_backend_parity_with_replay_clock(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The replay clock and the overlap filters ride the forwarded PriorQuery
    # untouched: a flag-heavy invocation matches the local backend byte for byte.
    args = [
        "query",
        "--court",
        "ca9",
        "--judge",
        "smith",
        "--decided-before",
        "2023",
        "--limit",
        "3",
    ]
    local = runner.invoke(app, args)
    server, url = _serve(fixture_corpus.db_path)
    try:
        monkeypatch.setenv("FEDCOURTS_CORPUS_SERVICE_URL", url)
        served = runner.invoke(app, [*args, "--corpus-backend", "service"])
    finally:
        server.shutdown()
        server.server_close()
    assert served.exit_code == 0, served.output
    assert served.stdout == local.stdout


def test_corpus_serve_rejects_env_inherited_service_backend(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The setting (not the flag) can also name a non-connection backend; the
    # in-command guard must catch that path too.
    monkeypatch.setenv("FEDCOURTS_CORPUS_BACKEND", "service")
    result = runner.invoke(app, ["corpus-serve"])
    assert result.exit_code == 2
    assert "corpus-serve serves the local or ranged backend" in result.stderr
