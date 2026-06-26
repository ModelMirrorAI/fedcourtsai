import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths

runner = CliRunner()


def _store_snapshot(corpus_root: Path, payload: dict[str, object]) -> None:
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_snapshot(conn, "ca9/123", date(2026, 6, 10), payload)


def test_provision_snapshot_writes_latest_from_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    payload = {"id": 123, "docket_entries": [{"id": 1, "description": "Filed"}]}
    _store_snapshot(tmp_path / "corpus", payload)

    result = runner.invoke(app, ["provision-snapshot", "--court", "ca9", "--docket", "123"])

    assert result.exit_code == 0
    dest = CasePaths(tmp_path / "data", "ca9", 123).snapshot("2026-06-10")
    assert json.loads(dest.read_text()) == payload


def test_provision_snapshot_honors_explicit_out(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    payload = {"id": 123, "docket_entries": []}
    _store_snapshot(tmp_path / "corpus", payload)
    out = tmp_path / "scratch" / "snap.json"

    result = runner.invoke(
        app, ["provision-snapshot", "--court", "ca9", "--docket", "123", "--out", str(out)]
    )

    assert result.exit_code == 0
    assert json.loads(out.read_text()) == payload


def test_provision_snapshot_missing_corpus_snapshot_exits_nonzero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "corpus"))
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))

    result = runner.invoke(app, ["provision-snapshot", "--court", "ca9", "--docket", "999"])

    assert result.exit_code == 1
    assert "No snapshot" in result.output
