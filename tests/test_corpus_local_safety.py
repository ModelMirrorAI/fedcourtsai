"""Corpus local safety: reads never change the pulled blob, and only the writer
jobs' writes to the configured corpus file ever reach the content store.

Two seams, one property — a local run (a dev checkout, a codespace, a bare
script, a dry run) leaves both the pulled blob and the remote store exactly as
it found them:

- :func:`fedcourtsai.corpus.connect_local_read` (behind ``connect_readonly``'s
  local backend and every read-only command) opens a current blob ``mode=ro``
  and reads a migrated temporary copy of an older one, so the file keeps the
  sha256 its pointer names.
- :func:`fedcourtsai.casestore.mirrors_connection` and the mirror transport
  gate every corpus write's mirror: an ambient store is written only inside a
  GitHub Actions job, and only from the configured corpus file.
"""

from __future__ import annotations

import hashlib
import logging
import re
import sqlite3
from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import casestore, corpus
from fedcourtsai.analytics import AnalyticsQuery, run_analytics
from fedcourtsai.cli import app
from fedcourtsai.pipeline.ingest import from_api_docket
from fedcourtsai.pipeline.outcome import detect_resolution, record_outcomes
from fedcourtsai.validate import run_corpus_validation

from .conftest import FixtureCorpus
from .test_outcome import DECIDED_DOCKET, _open_event

runner = CliRunner()

# Columns and a table this code's migrations add to an older blob — what a
# checkout newer than the published corpus finds missing.
_AGED_COLUMNS = ("merits_decision_method", "merits_argued")
_AGED_TABLE = "opinions"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _age_schema(db_path: Path) -> None:
    """Rewrite ``db_path`` as a blob packed before the newest migrations."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(f"DROP TABLE IF EXISTS {_AGED_TABLE}")
        for column in _AGED_COLUMNS:
            conn.execute(f"ALTER TABLE cases DROP COLUMN {column}")
        conn.commit()
        conn.execute("VACUUM")
    finally:
        conn.close()


def _columns(conn: corpus.ReadConnection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


@pytest.fixture(autouse=True)
def _fresh_read_copies() -> Iterator[None]:
    """Each test sees its own per-process migrated-copy cache."""
    corpus._discard_read_copies()
    yield
    corpus._discard_read_copies()


@pytest.fixture
def aged_corpus(fixture_corpus: FixtureCorpus) -> FixtureCorpus:
    _age_schema(fixture_corpus.db_path)
    with corpus.connect_local_unmigrated(fixture_corpus.db_path) as ro:
        assert not corpus.schema_is_current(ro)
    return fixture_corpus


# --- reads never change the pulled blob ----------------------------------------


def test_a_current_blob_is_read_in_place_without_a_copy(fixture_corpus: FixtureCorpus) -> None:
    db = fixture_corpus.db_path
    before = _sha256(db)
    with corpus.connect_readonly(db, backend="local") as conn:
        assert conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0] > 0
        # Strictly read-only: the connection itself refuses a write.
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            conn.execute("UPDATE cases SET topic = 'x'")
    assert _sha256(db) == before
    assert corpus._READ_COPIES == {}


def test_an_older_blob_is_read_through_a_migrated_copy_and_left_byte_identical(
    aged_corpus: FixtureCorpus, caplog: pytest.LogCaptureFixture
) -> None:
    db = aged_corpus.db_path
    before = _sha256(db)
    with caplog.at_level(logging.WARNING, logger="fedcourtsai.corpus"):
        with corpus.connect_readonly(db, backend="local") as conn:
            # The reader sees every column this code knows, as an in-place
            # migration would have given it ...
            assert set(_AGED_COLUMNS) <= _columns(conn, "cases")
            assert _columns(conn, _AGED_TABLE)
            rows = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        with corpus.connect_readonly(db, backend="local") as again:
            assert again.execute("SELECT COUNT(*) FROM cases").fetchone()[0] == rows
    # ... while the pulled file keeps the bytes its pointer names.
    assert _sha256(db) == before
    with corpus.connect_local_unmigrated(db) as ro:
        assert not set(_AGED_COLUMNS) & _columns(ro, "cases")
    # One copy per process, however many opens, and it says so once.
    assert len(corpus._READ_COPIES) == 1
    assert sum("predates this code's schema" in r.message for r in caplog.records) == 1
    (copy,) = corpus._READ_COPIES.values()
    corpus._discard_read_copies()
    assert not copy.exists()


def test_a_blob_changed_after_its_copy_is_re_examined(aged_corpus: FixtureCorpus) -> None:
    """A writer that migrates the blob in place ends the copy's tenure: the next
    read sees the file itself, so it also sees the writer's rows."""
    db = aged_corpus.db_path
    with corpus.connect_readonly(db, backend="local"):
        pass
    assert len(corpus._READ_COPIES) == 1
    with corpus.connect(db) as conn:
        conn.execute("UPDATE cases SET topic = 'migrated-then-written'")
        conn.commit()
    with corpus.connect_readonly(db, backend="local") as conn:
        topics = {row[0] for row in conn.execute("SELECT topic FROM cases").fetchall()}
    assert topics == {"migrated-then-written"}


def test_an_absent_corpus_reads_empty_and_is_not_created(tmp_path: Path) -> None:
    db = corpus.corpus_db_path(tmp_path / "corpus")
    with corpus.connect_readonly(db, backend="local") as conn:
        assert conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0] == 0
        assert set(_AGED_COLUMNS) <= _columns(conn, "cases")
    assert not db.exists()
    assert not db.parent.exists()


def test_schema_is_current_tracks_every_migration(tmp_path: Path) -> None:
    db = tmp_path / "corpus.db"
    with corpus.connect(db):
        pass
    with corpus.connect_local_unmigrated(db) as ro:
        assert corpus.schema_is_current(ro)
    conn = sqlite3.connect(db)
    conn.execute("ALTER TABLE events DROP COLUMN opened_at")
    conn.commit()
    conn.close()
    with corpus.connect_local_unmigrated(db) as ro:
        assert not corpus.schema_is_current(ro)


def test_a_schema_that_does_not_replay_reads_as_not_current(tmp_path: Path) -> None:
    """An object whose DDL the replica cannot rebuild (here an index on a function
    only the writing connection had) degrades to the migrated copy, not a crash."""
    db = tmp_path / "corpus.db"
    with corpus.connect(db) as conn:
        conn.create_function("shout", 1, str.upper, deterministic=True)
        conn.execute("CREATE INDEX idx_cases_shout ON cases(shout(case_id))")
        conn.commit()
    before = _sha256(db)
    with corpus.connect_local_unmigrated(db) as ro:
        assert not corpus.schema_is_current(ro)
    with corpus.connect_local_read(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0] == 0
    assert _sha256(db) == before


def test_a_new_copy_replaces_the_one_for_the_files_earlier_state(
    aged_corpus: FixtureCorpus,
) -> None:
    db = aged_corpus.db_path
    with corpus.connect_local_read(db):
        pass
    (first,) = corpus._READ_COPIES.values()
    conn = sqlite3.connect(db)
    conn.execute("UPDATE cases SET topic = 'changed'")
    conn.commit()
    conn.close()
    with corpus.connect_local_read(db):
        pass
    assert len(corpus._READ_COPIES) == 1
    assert not first.exists()


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param(["corpus-info", "--corpus-backend", "local"], id="corpus-info"),
        pytest.param(["query", "--court", "scotus", "--limit", "3"], id="query"),
        pytest.param(["predict-plan", "--run-id", "RID"], id="predict-plan"),
        pytest.param(["evaluate-plan", "--run-id", "RID"], id="evaluate-plan"),
    ],
)
def test_read_only_commands_leave_an_older_blob_byte_identical(
    aged_corpus: FixtureCorpus, argv: list[str]
) -> None:
    """The executed check for the read commands: each runs to completion on a blob
    older than this code's schema, and the blob's sha256 does not move."""
    db = aged_corpus.db_path
    before = _sha256(db)
    result = runner.invoke(app, argv)
    assert result.exit_code == 0, result.output
    assert _sha256(db) == before


def test_corpus_validation_and_analytics_leave_an_older_blob_byte_identical(
    aged_corpus: FixtureCorpus,
) -> None:
    db = aged_corpus.db_path
    before = _sha256(db)
    verdict = run_corpus_validation(
        corpus_db_path=db, data_root=aged_corpus.data_root, today=date(2026, 10, 9)
    )
    assert not verdict.skipped
    report = run_analytics(corpus_db_path=db, query=AnalyticsQuery(group_by="court"))
    assert not report.skipped
    assert _sha256(db) == before


# --- remote mirroring: writer jobs only, configured corpus only ------------------


@pytest.fixture
def ambient_store(monkeypatch: pytest.MonkeyPatch) -> casestore.InMemoryObjectTransport:
    """A content store the *environment* names, as a writer job's base URL does.

    Built through the settings seam (not injected), so it is subject to every
    ambient-only gate — the state a dev shell or a writer job is in.
    """
    store = casestore.InMemoryObjectTransport()
    monkeypatch.setattr(casestore, "transport_from_settings", lambda: store)
    monkeypatch.setitem(
        casestore._MIRROR_WITHHELD, "outside_actions", False
    )  # each test sees its own one-time warning
    monkeypatch.setitem(casestore._MIRROR_WITHHELD, "not_corpus", False)
    return store


def _row(case_id: str = "scotus/9026000001") -> corpus.CorpusRow:
    return corpus.CorpusRow(case_id=case_id, court="scotus", docket_number="26-1")


def _event(case_id: str = "scotus/9026000001") -> corpus.CorpusEvent:
    return corpus.CorpusEvent(
        event_id="evt-petition-cert",
        case_id=case_id,
        court="scotus",
        kind="petition",
        title="Petition",
    )


def _configure_corpus_root(monkeypatch: pytest.MonkeyPatch, root: Path) -> Path:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(root))
    return corpus.corpus_db_path(root)


def test_a_writer_job_write_to_the_configured_corpus_mirrors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambient_store: casestore.InMemoryObjectTransport,
) -> None:
    """The writer-job path, unchanged: inside an Actions job, the configured
    corpus file's writes mirror every object they did before."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    db = _configure_corpus_root(monkeypatch, tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row()])
        corpus.upsert_events(conn, [_event()])
        corpus.upsert_snapshot(conn, "scotus/9026000001", date(2026, 10, 1), {"k": 1})
        corpus.set_event_resolved(conn, "scotus/9026000001", "evt-petition-cert")
    assert set(ambient_store.objects) == {
        casestore.case_key("scotus/9026000001"),
        casestore.events_key("scotus/9026000001"),
        casestore.snapshot_key("scotus/9026000001", date(2026, 10, 1)),
    }


def test_a_writer_job_mirrors_through_a_relative_corpus_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambient_store: casestore.InMemoryObjectTransport,
) -> None:
    """The workflows name the corpus root relative to the checkout; the file
    SQLite reports is absolute. Both spellings are the same corpus."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", "corpus")
    with corpus.connect(corpus.corpus_db_path(Path("corpus"))) as conn:
        corpus.upsert_rows(conn, [_row()])
    assert ambient_store.puts == 1


def test_a_temporary_database_never_mirrors_even_in_a_writer_job(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambient_store: casestore.InMemoryObjectTransport,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    _configure_corpus_root(monkeypatch, tmp_path / "corpus")
    scratch = tmp_path / "scratch" / "seeded.db"
    with caplog.at_level(logging.WARNING, logger="fedcourtsai.casestore"):
        with corpus.connect(scratch) as conn:
            corpus.upsert_rows(conn, [_row()])
            corpus.upsert_events(conn, [_event()])
            corpus.upsert_snapshot(conn, "scotus/9026000001", date(2026, 10, 1), {"k": 1})
        with sqlite3.connect(":memory:") as memory:
            memory.row_factory = sqlite3.Row
            assert not casestore.mirrors_connection(memory)
    assert ambient_store.puts == 0
    assert sum("not the configured corpus file" in r.message for r in caplog.records) == 1


def test_a_local_run_never_attempts_a_content_store_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambient_store: casestore.InMemoryObjectTransport,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Outside an Actions job the configured corpus file itself stays local: a
    dev checkout holding any credential cannot turn a writer into a remote
    write. The store is still the read seam."""
    db = _configure_corpus_root(monkeypatch, tmp_path / "corpus")
    with (
        caplog.at_level(logging.WARNING, logger="fedcourtsai.casestore"),
        corpus.connect(db) as conn,
    ):
        corpus.upsert_rows(conn, [_row()])
        corpus.upsert_events(conn, [_event()])
        corpus.set_event_resolved(conn, "scotus/9026000001", "evt-petition-cert")
    assert ambient_store.puts == 0
    assert casestore.active_transport() is ambient_store
    assert sum("only inside a GitHub Actions job" in r.message for r in caplog.records) == 1


@pytest.mark.parametrize(("in_actions", "attempts"), [(False, False), (True, True)])
def test_record_outcomes_attempts_a_store_write_only_in_a_writer_job(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambient_store: casestore.InMemoryObjectTransport,
    in_actions: bool,
    attempts: bool,
) -> None:
    """The run that found the gap: the outcome sweep's corpus close, dry-run on a
    local copy of the corpus with the environment naming the production store.

    Every ``put`` is recorded rather than refused, because a mirror failure is
    swallowed by design — a refusing transport would pass this test while the
    write was still attempted. The writer-job case is the control that the
    recording sees the attempts it is there to catch.
    """
    attempted: list[str] = []
    monkeypatch.setattr(ambient_store, "put", lambda key, body, **_: attempted.append(key))
    if in_actions:
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
    db = _configure_corpus_root(monkeypatch, tmp_path / "corpus")
    _open_event(tmp_path)
    resolution = detect_resolution(
        from_api_docket(DECIDED_DOCKET), "ca9", 64512345, ["evt-petition-review"]
    )
    assert record_outcomes(db, tmp_path, "ca9", 64512345, resolution) == ["evt-petition-review"]
    with corpus.connect(db) as conn:
        assert all(e.resolved for e in corpus.events_for_case(conn, "ca9/64512345"))
    assert bool(attempted) is attempts


def test_the_pointer_override_still_withholds_in_a_writer_job(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambient_store: casestore.InMemoryObjectTransport,
) -> None:
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setitem(casestore._MIRROR_WITHHELD, "warned", False)
    monkeypatch.setattr(
        casestore, "_mirror_blocked", lambda: True
    )  # the override's own gate, covered in test_casestore
    db = _configure_corpus_root(monkeypatch, tmp_path / "corpus")
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row()])
    assert ambient_store.puts == 0


def test_an_injected_transport_mirrors_any_connection(tmp_path: Path) -> None:
    """Explicit wiring is the code's own choice of store, not the environment's,
    so the ambient-only gates do not bind it."""
    store = casestore.InMemoryObjectTransport()
    casestore.set_active_transport(store)
    with corpus.connect(tmp_path / "anywhere.db") as conn:
        corpus.upsert_rows(conn, [_row()])
    assert store.puts == 1


def test_transport_override_restores_the_ambient_provenance(
    monkeypatch: pytest.MonkeyPatch,
    ambient_store: casestore.InMemoryObjectTransport,
    tmp_path: Path,
) -> None:
    db = _configure_corpus_root(monkeypatch, tmp_path / "corpus")
    assert casestore.active_transport() is ambient_store
    with casestore.transport_override(casestore.InMemoryObjectTransport()):
        pass
    # Back to the ambient store, and so back under the ambient gates.
    with corpus.connect(db) as conn:
        corpus.upsert_rows(conn, [_row()])
    assert ambient_store.puts == 0


@pytest.mark.parametrize(
    ("in_actions", "out", "mirrored"),
    [
        pytest.param(True, None, True, id="writer-job-configured-corpus"),
        pytest.param(True, "scratch.db", False, id="writer-job-scratch-out"),
        pytest.param(False, None, False, id="local-configured-corpus"),
    ],
)
def test_a_corpus_writing_command_mirrors_only_as_a_writer_job_on_the_corpus(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambient_store: casestore.InMemoryObjectTransport,
    in_actions: bool,
    out: str | None,
    mirrored: bool,
) -> None:
    """End to end through the CLI: a command that writes the corpus through the
    write seams (the fixture builder, the one corpus writer that runs offline)."""
    if in_actions:
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
    _configure_corpus_root(monkeypatch, tmp_path / "corpus")
    argv = ["make-fixture-corpus"]
    if out is not None:
        argv += ["--out", str(tmp_path / out)]
    result = runner.invoke(app, argv)
    assert result.exit_code == 0, result.output
    assert (ambient_store.puts > 0) is mirrored
    if mirrored:
        with corpus.connect_local_read(corpus.corpus_db_path(tmp_path / "corpus")) as conn:
            cases = corpus.count(conn)
        assert len([k for k in ambient_store.objects if k.endswith("/case.json")]) == cases


def test_a_withheld_write_in_a_split_writer_job_is_an_error_every_time(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    ambient_store: casestore.InMemoryObjectTransport,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Under the split the blob keeps no payloads, so a writer-job write to any
    other database stores them nowhere: said at error level, on every write."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("FEDCOURTS_CORPUS_SPLIT", "true")
    _configure_corpus_root(monkeypatch, tmp_path / "corpus")
    with (
        caplog.at_level(logging.WARNING, logger="fedcourtsai.casestore"),
        corpus.connect(tmp_path / "staged.db") as conn,
    ):
        corpus.upsert_rows(conn, [_row()])
        corpus.upsert_events(conn, [_event()])
    errors = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert len(errors) == 2
    assert all("stored nowhere" in r.getMessage() for r in errors)
    assert ambient_store.puts == 0


_SRC = Path(__file__).resolve().parents[1] / "src" / "fedcourtsai"


def test_production_code_never_injects_a_live_transport() -> None:
    """The injected-transport exemption from the ambient gates is for tests and
    for switching the mirror off: no production call site injects a store."""
    call = re.compile(r"(?<!def )(?:set_active_transport|transport_override)\(([^)]*)\)")
    injected = [
        (path.name, match.group(1))
        for path in sorted(_SRC.rglob("*.py"))
        for match in call.finditer(path.read_text())
        # `transport_override` hands its own argument to `set_active_transport`;
        # an empty argument list is a prose mention, not a call that injects.
        if match.group(1).strip() not in {"", "None", "transport"}
    ]
    assert injected == []
