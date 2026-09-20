import json
import re
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


def _unwrapped(text: str) -> str:
    """Error output as one whitespace-free-ish line, past any box drawing.

    Typer renders a usage error inside a Rich panel whose width follows the
    terminal, so the sentences below arrive wrapped and column-padded at a
    width no test can pin — and Rich emits ANSI style codes wherever it
    detects a capable sink (GitHub Actions included), so the codes must go
    the same way as the borders. Stripping both and collapsing the runs of
    whitespace leaves the content, which is what the assertions are about.
    """
    plain = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    return " ".join(plain.replace("│", " ").replace("|", " ").split())


def test_a_free_text_search_argument_is_refused_with_the_interface(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The failure this closes is behavioural: a cell guesses a search engine,
    # gets one terse line, and abandons the corpus for the rest of its run
    # rather than re-issuing the same question as structured filters.
    result = runner.invoke(app, ["query", "--court", "scotus", "Anderson-Burdick mail voting"])
    assert result.exit_code == 2
    out = _unwrapped(result.output)
    assert "unexpected extra argument" in out
    assert "takes no free-text search argument" in out
    # The rule, and the one invocation that shows what to do instead.
    assert "none of them positional" in out
    assert "fedcourts query --court scotus --disposition granted --limit 5" in out
    assert "fedcourts query --help" in out


def test_a_bad_flag_value_is_refused_with_the_interface(fixture_corpus: FixtureCorpus) -> None:
    # `--full` is a boolean, so a case name after it parses as a positional —
    # the wrong mental model this screen exists to correct.
    result = runner.invoke(app, ["query", "--court", "scotus", "--full", "Jennings v. Rodriguez"])
    assert result.exit_code == 2
    out = _unwrapped(result.output)
    assert "takes no free-text search argument" in out
    assert "bare four-digit October-Term year (2025)" in out


def test_the_replay_clock_takes_a_date_or_a_term_year(fixture_corpus: FixtureCorpus) -> None:
    # Both ca9 priors are filed in 2022 (their best-known year) and decided in
    # 2023 — ca9/101 on 09-18, ca9/102 on 11-30. A bare year screens on the
    # best-known year; a date screens on the resolution date alone.
    def ids(clock: str) -> list[object]:
        result = runner.invoke(app, ["query", "--court", "ca9", "--decided-before", clock])
        assert result.exit_code == 0, result.output
        return [r["case_id"] for r in _rows(result.stdout)]

    # Neither prior had been decided by mid-2023, so a date there empties the
    # set — as the bare year 2022 does, for the unrelated reason that neither
    # row's best-known year precedes 2022.
    assert ids("2023-06-30") == ids("2022") == []
    # The bare year 2023 admits both: it can only ask about the year. The date
    # asks about the day, and drops the one not yet decided on 2023-10-02.
    assert ids("2023") == ["ca9/102", "ca9/101"]
    assert ids("2023-10-02") == ["ca9/101"]


def test_query_reads_the_replay_cutoff_from_the_environment(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The cell contract: the prompt spells only `--decided-before "$DECIDED_BEFORE"`
    # (its October Term), and the cutoff day reaches the mask through the
    # environment. ca9/101 was decided 2023-09-18 and ca9/102 2023-11-30, both
    # filed in 2022, so the Term bar 2023 admits both and a cutoff of 2023-10-02
    # removes the one that had not been decided yet.
    def ids(*, cutoff: str | None) -> tuple[list[object], str]:
        monkeypatch.delenv("REPLAY_CUTOFF", raising=False)
        if cutoff is not None:
            monkeypatch.setenv("REPLAY_CUTOFF", cutoff)
        result = runner.invoke(app, ["query", "--court", "ca9", "--decided-before", "2023"])
        assert result.exit_code == 0, result.output
        return [r["case_id"] for r in _rows(result.stdout)], _unwrapped(result.stderr)

    plain, plain_err = ids(cutoff=None)
    clocked, clocked_err = ids(cutoff="2023-10-02")
    assert plain == ["ca9/102", "ca9/101"]
    assert clocked == ["ca9/101"]
    # And it says so, before the rows: a cell that did not pass the flag would
    # otherwise read the narrower result as a thin corpus.
    assert "replay cutoff" not in plain_err
    assert "replay cutoff 2023-10-02 (from REPLAY_CUTOFF)" in clocked_err
    # The interface screen names the variable too, so a caller reading the help
    # learns where a day bar it never typed came from.
    teach = _unwrapped(runner.invoke(app, ["query", "--court", "ca9", "nope"]).output)
    assert "REPLAY_CUTOFF in its environment" in teach


def test_an_unparseable_replay_cutoff_is_refused_not_ignored(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Falling through to "no day" would widen a replay cell's retrieval while
    # looking masked — the same failure the argument's refusal exists to prevent.
    monkeypatch.setenv("REPLAY_CUTOFF", "last June")
    result = runner.invoke(app, ["query", "--court", "ca9", "--decided-before", "2023"])
    assert result.exit_code == 2
    out = _unwrapped(result.output)
    assert "REPLAY_CUTOFF" in out and "ISO date" in out


def test_an_unreadable_replay_clock_is_refused_with_the_interface(
    fixture_corpus: FixtureCorpus,
) -> None:
    # Refused rather than dropped: a clock that fell through to "no cutoff"
    # would unmask a replay cell's retrieval while looking masked.
    for clock in ("2026-13-01", "last year", "20260630", "25", "202", "1789-09-30"):
        result = runner.invoke(app, ["query", "--court", "ca9", "--decided-before", clock])
        assert result.exit_code == 2, clock
        out = _unwrapped(result.output)
        assert any(m in out for m in ("replay clock", "calendar date", "federal judiciary")), clock
        assert "bare four-digit October-Term year" in out, clock


def test_an_invented_era_is_refused_and_the_vocabulary_printed(
    fixture_corpus: FixtureCorpus,
) -> None:
    # An era is a decade token. A court-name era would otherwise filter every
    # row away and read back as a corpus holding no priors at all.
    result = runner.invoke(app, ["query", "--court", "scotus", "--era", "Roberts Court"])
    assert result.exit_code == 2
    out = _unwrapped(result.output)
    assert "Unknown era 'Roberts Court'" in out
    assert "1890s" in out and "2020s" in out
    assert "fedcourts query --court scotus --disposition granted --limit 5" in out


def test_a_valid_query_is_untouched_by_the_teaching_error_path(
    fixture_corpus: FixtureCorpus,
) -> None:
    # The change is error reporting only: the rows, the read-stats line and the
    # exit code of a well-formed invocation are exactly what they were.
    result = runner.invoke(app, ["query", "--court", "ca9", "--judge", "smith", "--limit", "5"])
    assert result.exit_code == 0, result.output
    assert [r["case_id"] for r in _rows(result.stdout)] == ["ca9/102", "ca9/101"]
    assert "takes no free-text search argument" not in result.output
    assert "1790s" not in result.output


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
    # "in this blob", not "no snapshots": under the corpus split the content
    # store holds them, and AGENTS.md points agents at this line as evidence.
    assert "freshness: never pulled, no snapshots in this blob" in result.stdout


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
    # Both spellings, because the date carries a second field over the wire and a
    # day that failed to serialize would unmask the sidecar's retrieval alone.
    server, url = _serve(fixture_corpus.db_path)
    monkeypatch.setenv("FEDCOURTS_CORPUS_SERVICE_URL", url)
    try:
        for clock in ("2023", "2023-10-02"):
            args = [
                "query",
                "--court",
                "ca9",
                "--judge",
                "smith",
                "--decided-before",
                clock,
                "--limit",
                "3",
            ]
            local = runner.invoke(app, args)
            served = runner.invoke(app, [*args, "--corpus-backend", "service"])
            assert served.exit_code == 0, served.output
            assert served.stdout == local.stdout, clock
    finally:
        server.shutdown()
        server.server_close()
    # And the date really did narrow, or the parity above proves nothing: the
    # last invocation was the dated one.
    year_only = runner.invoke(
        app,
        ["query", "--court", "ca9", "--judge", "smith", "--decided-before", "2023", "--limit", "3"],
    )
    assert _rows(local.stdout) != _rows(year_only.stdout)


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


# --- the citation-coverage sentinel -------------------------------------------


def _flat(text: str) -> str:
    """stderr flattened for matching: no colour codes, no wrapping artefacts."""
    return " ".join(re.sub(r"\x1b\[[0-9;]*m", "", text).split())


def _citation_less_court(db_path: Path) -> None:
    """A 200-row court scope whose `citations` column is populated for none of it."""
    with corpus.connect(db_path) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id=f"ca5/{i}",
                    court="ca5",
                    docket_number=f"23-{i}",
                    case_name="Doe v. Roe",
                    disposition=Disposition.denied,
                    date_decided=date(2025, 1, 2),
                )
                for i in range(200)
            ],
        )


def test_query_says_how_thin_the_citation_column_is_before_it_scans(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The failure this prevents: a cell reading zero rows as "no such case".

    Said on stderr, never stdout — cells parse stdout as one JSON row per line —
    and said once, not twice: the empty-result coverage note is the same
    reading, so the caller that already said it does not repeat it.
    """
    _citation_less_court(fixture_corpus.db_path)
    result = runner.invoke(app, ["query", "--court", "ca5", "--citation", "597 U.S. 1"])
    assert result.exit_code == 0, result.output
    assert _rows(result.stdout) == []
    err = _flat(result.stderr)
    assert "only 0 row(s) in scope (ca5) carry any reporter citation" in err
    assert "a column that was never filled than a case that does not exist" in err
    assert err.count("citations filter:") == 1


def test_query_still_serves_a_citation_filter_the_column_can_answer(
    fixture_corpus: FixtureCorpus,
) -> None:
    """The other branch: a matching cite returns its row, sentinel or not."""
    result = runner.invoke(app, ["query", "--court", "ca9", "--citation", "410 U.S. 113"])
    assert result.exit_code == 0, result.output
    assert _rows(result.stdout), result.output


def test_query_service_backend_relays_the_citation_sentinel(
    fixture_corpus: FixtureCorpus, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The sidecar is a transport: same reading, same one line.

    It is also where the reading matters most — the sidecar holds the ranged
    connection, so it is the process whose transfer the narrowed scan saves.
    """
    _citation_less_court(fixture_corpus.db_path)
    server, url = _serve(fixture_corpus.db_path)
    try:
        monkeypatch.setenv("FEDCOURTS_CORPUS_SERVICE_URL", url)
        result = runner.invoke(
            app,
            [
                "query",
                "--court",
                "ca5",
                "--citation",
                "597 U.S. 1",
                "--corpus-backend",
                "service",
            ],
        )
    finally:
        server.shutdown()
        server.server_close()
    assert result.exit_code == 0, result.output
    err = _flat(result.stderr)
    assert "only 0 row(s) in scope (ca5) carry any reporter citation" in err
    assert err.count("citations filter:") == 1
