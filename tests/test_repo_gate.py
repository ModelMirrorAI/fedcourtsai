"""Offline corpus + metrics bookkeeping checks (``fedcourtsai.repo_gate``)."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus, repo_gate
from fedcourtsai.cli import app

runner = CliRunner()

POINTER = json.dumps(
    {
        "key": "index/sha256/" + "a" * 64,
        "size": 2174976,
        "sha256": "a" * 64,
        "schema_version": "1.0",
    }
)


def _repo(tmp_path: Path) -> Path:
    """A minimal repo layout: the corpus pointer plus every metrics artifact."""
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus" / "corpus.db.ref").write_text(POINTER + "\n")
    (tmp_path / "metrics").mkdir()
    for artifact in repo_gate.METRICS_ARTIFACTS:
        (tmp_path / artifact).write_text("{}\n")
    return tmp_path


def _is_metrics(path: Path) -> bool:
    return path in set(repo_gate.METRICS_ARTIFACTS)


def test_clean_repo_has_no_problems(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    errors = repo_gate.check_state(
        repo,
        is_tracked=_is_metrics,
        is_ignored=lambda p: p == repo_gate.CORPUS_BLOB,
    )
    assert errors == []


def test_clean_repo_without_pointer_is_fine(tmp_path: Path) -> None:
    # A pre-corpus repo has no pointer yet; the gate must not demand one.
    repo = _repo(tmp_path)
    (repo / repo_gate.CORPUS_POINTER).unlink()
    errors = repo_gate.check_state(
        repo, is_tracked=_is_metrics, is_ignored=lambda p: p == repo_gate.CORPUS_BLOB
    )
    assert errors == []


def test_flags_blob_committed_to_git(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    errors = repo_gate.check_state(
        repo,
        is_tracked=lambda p: True,  # corpus.db is (wrongly) committed
        is_ignored=lambda p: True,
    )
    assert any("committed to git" in e and "corpus.db" in e for e in errors)


def test_flags_blob_not_gitignored(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    errors = repo_gate.check_state(
        repo,
        is_tracked=_is_metrics,
        is_ignored=lambda p: False,  # corpus.db could be committed by accident
    )
    assert any("not gitignored" in e for e in errors)


def test_flags_missing_metrics_artifact(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "metrics" / "leaderboard.json").unlink()
    errors = repo_gate.check_state(repo, is_tracked=lambda p: True, is_ignored=lambda p: True)
    assert any("leaderboard.json" in e and "is missing" in e for e in errors)


def test_flags_uncommitted_metrics_artifact(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    errors = repo_gate.check_state(
        repo,
        is_tracked=lambda p: False,  # metrics files present but never committed
        is_ignored=lambda p: True,
    )
    assert sum("not committed to git" in e for e in errors) == len(repo_gate.METRICS_ARTIFACTS)


def test_malformed_pointer_is_reported(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / repo_gate.CORPUS_POINTER).write_text('{"key": "index/sha256/x", "size": -1}\n')
    errors = repo_gate.check_state(
        repo, is_tracked=_is_metrics, is_ignored=lambda p: p == repo_gate.CORPUS_BLOB
    )
    assert any("sha256" in e for e in errors)


def _git_repo(tmp_path: Path) -> Path:
    repo = _repo(tmp_path)
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    (repo / "corpus" / ".gitignore").write_text("/corpus.db\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    # The blob itself is never added; only metadata + the gitignored layout.
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-q",
            "-m",
            "init",
        ],
        check=True,
    )
    return repo


def test_cli_corpus_status_clean(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    result = runner.invoke(app, ["corpus-status", str(repo)])
    assert result.exit_code == 0, result.stdout
    assert "corpus bookkeeping consistent" in result.stdout
    assert "pointer present" in result.stdout


def test_cli_corpus_status_fails_when_blob_tracked(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    # Force the blob into git to simulate the classic mistake.
    (repo / "corpus" / "corpus.db").write_text("x")
    subprocess.run(["git", "-C", str(repo), "add", "-f", "corpus/corpus.db"], check=True)
    result = runner.invoke(app, ["corpus-status", str(repo)])
    assert result.exit_code == 1
    assert "committed to git" in result.stderr


def test_cli_corpus_status_flags_wrong_layout_corpus(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    # A locally present blob whose physical layout breaks the ranged-read
    # contract (default 4 KB pages) must fail the offline gate.
    conn = sqlite3.connect(repo / "corpus" / "corpus.db")
    try:
        conn.execute("PRAGMA page_size = 4096")
        conn.execute("CREATE TABLE t (x TEXT)")
        conn.commit()
    finally:
        conn.close()
    result = runner.invoke(app, ["corpus-status", str(repo)])
    assert result.exit_code == 1
    assert "page size 4096" in result.stderr


def test_cli_corpus_status_ok_with_ranged_layout_corpus(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    # A blob written through the corpus writer path satisfies the contract.
    with corpus.connect(repo / "corpus" / "corpus.db"):
        pass
    result = runner.invoke(app, ["corpus-status", str(repo)])
    assert result.exit_code == 0, result.stdout
    assert "corpus bookkeeping consistent" in result.stdout
