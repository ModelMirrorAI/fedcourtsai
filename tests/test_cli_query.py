import json
import threading
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus, corpus_service, fixture
from fedcourtsai.cli import app
from fedcourtsai.schemas import Disposition
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


def test_query_screens_non_cert_applications(fixture_corpus: FixtureCorpus) -> None:
    # A time-extension application beside the fixture's substantive stay: the
    # cert surface is the default, so only the stay (and the petitions) come
    # back; --include-applications returns the extension too.
    with corpus.connect(fixture_corpus.db_path) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="scotus/350",
                    court="scotus",
                    docket_number="26A40",
                    case_name="Ellison v. Marbury Power Cooperative",
                    application_kind="extension",
                    disposition=Disposition.granted,
                    date_filed=date(2026, 7, 20),
                    date_decided=date(2026, 7, 22),
                )
            ],
        )
    default = runner.invoke(app, ["query", "--court", "scotus"])
    opted_in = runner.invoke(app, ["query", "--court", "scotus", "--include-applications"])
    assert default.exit_code == 0, default.output
    assert opted_in.exit_code == 0, opted_in.output
    screened = {r["case_id"] for r in _rows(default.stdout)}
    included = {r["case_id"] for r in _rows(opted_in.stdout)}
    assert "scotus/350" not in screened
    assert "scotus/306" in screened  # the substantive stay: interim predict scope
    assert included == screened | {"scotus/350"}


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


def test_corpus_info_reports_freshness(fixture_corpus: FixtureCorpus) -> None:
    # The blob on disk is otherwise undated (the committed pointer is a content
    # digest), so this line is the whole freshness surface a corpus-dependent
    # claim can cite. The fixture carries snapshots but no pull stamp.
    newest = max(case.snapshot_date for case in fixture.FIXTURE_CASES)
    result = runner.invoke(app, ["corpus-info"])
    assert result.exit_code == 0, result.output
    assert f"freshness: never pulled, latest snapshot {newest.isoformat()}" in result.stdout

    with corpus.connect(fixture_corpus.db_path) as conn:
        row = corpus.get_row(conn, "ca9/101")
        assert row is not None
        corpus.upsert_rows(conn, [row.model_copy(update={"last_pulled": date(2026, 8, 16)})])
    pulled = runner.invoke(app, ["corpus-info"])
    assert pulled.exit_code == 0, pulled.output
    assert "freshness: latest pull 2026-08-16" in pulled.stdout


def test_corpus_info_freshness_falls_back_on_an_empty_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The payload-free index shape in miniature: a blob with no snapshot rows
    # and no pull stamp must degrade to words rather than crash on the NULLs.
    corpus_root = tmp_path / "corpus"
    with corpus.connect(corpus.corpus_db_path(corpus_root)):
        pass
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(corpus_root))
    result = runner.invoke(app, ["corpus-info"])
    assert result.exit_code == 0, result.output
    assert "freshness: never pulled, no snapshots" in result.stdout


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


def test_query_empty_sparse_filter_prints_coverage_note_on_stderr(
    fixture_corpus: FixtureCorpus,
) -> None:
    # A zero-row result through a sparse filter must explain itself on stderr,
    # never stdout — cells parse stdout as one JSON row per line.
    result = runner.invoke(app, ["query", "--court", "ca9", "--citation", "999 U.S. 999"])
    assert result.exit_code == 0
    assert _rows(result.stdout) == []
    assert "note: citations filter" in result.stderr
    # A zero limit scans nothing, so there is no coverage story to tell.
    capped = runner.invoke(
        app, ["query", "--court", "ca9", "--citation", "999 U.S. 999", "--limit", "0"]
    )
    assert "note:" not in capped.stderr
