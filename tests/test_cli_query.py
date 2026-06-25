import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import corpus
from fedcourtsai.cli import app
from fedcourtsai.schemas import Disposition

runner = CliRunner()


def _seed_corpus(corpus_root: Path) -> None:
    db = corpus.corpus_db_path(corpus_root)
    with corpus.connect(db) as conn:
        corpus.upsert_rows(
            conn,
            [
                corpus.CorpusRow(
                    case_id="ca9/1",
                    court="ca9",
                    topic="civil rights",
                    judges=["smith", "jones"],
                    citations=["410 U.S. 113"],
                    disposition=Disposition.granted,
                    date_decided=date(2025, 1, 1),
                    opinion_text="long opinion body",
                ),
                corpus.CorpusRow(
                    case_id="ca9/2",
                    court="ca9",
                    topic="contracts",
                    judges=["smith"],
                    disposition=Disposition.denied,
                    date_decided=date(2024, 1, 1),
                ),
                corpus.CorpusRow(
                    case_id="ca9/open",
                    court="ca9",
                    judges=["smith"],
                    disposition=None,
                    date_decided=None,
                ),
            ],
        )


def _rows(output: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in output.splitlines() if line.strip()]


def test_query_ranks_and_omits_opinion_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path))
    _seed_corpus(tmp_path)
    result = runner.invoke(app, ["query", "--court", "ca9", "--judge", "smith", "--judge", "jones"])
    assert result.exit_code == 0
    rows = _rows(result.stdout)
    # ca9/1 shares both judges (higher overlap) so it ranks first; ca9/open is
    # excluded by the resolved-only default.
    assert [r["case_id"] for r in rows] == ["ca9/1", "ca9/2"]
    assert "opinion_text" not in rows[0]


def test_query_full_includes_opinion_text(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path))
    _seed_corpus(tmp_path)
    result = runner.invoke(app, ["query", "--court", "ca9", "--full", "--limit", "1"])
    assert result.exit_code == 0
    rows = _rows(result.stdout)
    assert rows[0]["opinion_text"] == "long opinion body"


def test_query_include_open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path))
    _seed_corpus(tmp_path)
    result = runner.invoke(app, ["query", "--judge", "smith", "--include-open"])
    assert result.exit_code == 0
    assert {r["case_id"] for r in _rows(result.stdout)} == {"ca9/1", "ca9/2", "ca9/open"}


def test_query_unknown_disposition_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path))
    _seed_corpus(tmp_path)
    result = runner.invoke(app, ["query", "--disposition", "nope"])
    assert result.exit_code == 2
    assert "Unknown disposition" in result.stderr


def test_query_missing_corpus_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEDCOURTS_CORPUS_ROOT", str(tmp_path / "absent"))
    result = runner.invoke(app, ["query"])
    assert result.exit_code == 1
    assert "No corpus" in result.stderr
