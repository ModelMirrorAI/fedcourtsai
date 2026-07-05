"""Offline DVC-metadata consistency checks (``fedcourtsai.dvc``)."""

from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai import corpus, dvc
from fedcourtsai.cli import app

runner = CliRunner()

POINTER = """\
outs:
- md5: 217457333eaa889e68f3dd9fff11ee74
  size: 2174976
  hash: md5
  path: corpus.db
"""

PIPELINE = """\
stages:
  leaderboard:
    cmd: uv run fedcourts leaderboard
    deps:
      - data/cases
    metrics:
      - metrics/leaderboard.json:
          cache: false
"""


def _repo(tmp_path: Path) -> Path:
    """A minimal repo layout: a corpus pointer plus a metrics pipeline output."""
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus" / "corpus.db.dvc").write_text(POINTER)
    (tmp_path / "metrics").mkdir()
    (tmp_path / "metrics" / "leaderboard.json").write_text("{}\n")
    (tmp_path / "dvc.yaml").write_text(PIPELINE)
    return tmp_path


def _collect_paths(repo: Path) -> dict[str, dvc.DvcOut]:
    outs, errors = dvc.collect_outs(repo)
    assert errors == []
    return {str(o.path): o for o in outs}


def test_collect_outs_resolves_pointer_and_pipeline_paths(tmp_path: Path) -> None:
    by_path = _collect_paths(_repo(tmp_path))
    # Pointer paths resolve relative to the pointer's own directory.
    assert by_path["corpus/corpus.db"].cached is True
    # cache: false metrics outputs are git-tracked, not remote blobs.
    assert by_path["metrics/leaderboard.json"].cached is False


def test_clean_repo_has_no_problems(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    errors = dvc.check_state(
        repo,
        is_tracked=lambda p: p == Path("metrics/leaderboard.json"),
        is_ignored=lambda p: p == Path("corpus/corpus.db"),
    )
    assert errors == []


def test_flags_blob_committed_to_git(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    errors = dvc.check_state(
        repo,
        is_tracked=lambda p: True,  # corpus.db is (wrongly) committed
        is_ignored=lambda p: True,
    )
    assert any("also committed to git" in e for e in errors)


def test_flags_blob_not_gitignored(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    errors = dvc.check_state(
        repo,
        is_tracked=lambda p: p == Path("metrics/leaderboard.json"),
        is_ignored=lambda p: False,  # corpus.db could be committed by accident
    )
    assert any("not gitignored" in e for e in errors)


def test_flags_missing_metrics_output(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "metrics" / "leaderboard.json").unlink()
    errors = dvc.check_state(
        repo,
        is_tracked=lambda p: True,
        is_ignored=lambda p: True,
    )
    assert any("is missing" in e for e in errors)


def test_flags_uncommitted_metrics_output(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    errors = dvc.check_state(
        repo,
        is_tracked=lambda p: False,  # metrics file present but never committed
        is_ignored=lambda p: True,
    )
    assert any("not committed to git" in e for e in errors)


def test_malformed_pointer_is_reported(tmp_path: Path) -> None:
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus" / "corpus.db.dvc").write_text("outs:\n- path: corpus.db\n")
    _outs, errors = dvc.collect_outs(tmp_path)
    assert any("no checksum" in e for e in errors)


def test_pointer_without_outs_is_reported(tmp_path: Path) -> None:
    (tmp_path / "broken.dvc").write_text("notouts: 1\n")
    _outs, errors = dvc.collect_outs(tmp_path)
    assert any("declares no outs" in e for e in errors)


def test_stage_without_cmd_is_reported(tmp_path: Path) -> None:
    (tmp_path / "dvc.yaml").write_text("stages:\n  s:\n    metrics:\n      - m.json\n")
    _outs, errors = dvc.collect_outs(tmp_path)
    assert any("has no cmd" in e for e in errors)


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


def test_cli_dvc_status_clean(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    result = runner.invoke(app, ["dvc-status", str(repo)])
    assert result.exit_code == 0, result.stdout
    assert "DVC metadata consistent" in result.stdout
    assert "corpus/corpus.db" in result.stdout


def test_cli_dvc_status_fails_when_blob_tracked(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    # Force the blob into git to simulate the classic mistake.
    (repo / "corpus" / "corpus.db").write_text("x")
    subprocess.run(["git", "-C", str(repo), "add", "-f", "corpus/corpus.db"], check=True)
    result = runner.invoke(app, ["dvc-status", str(repo)])
    assert result.exit_code == 1
    assert "also committed to git" in result.stderr


def test_cli_dvc_status_flags_wrong_layout_corpus(tmp_path: Path) -> None:
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
    result = runner.invoke(app, ["dvc-status", str(repo)])
    assert result.exit_code == 1
    assert "page size 4096" in result.stderr


def test_cli_dvc_status_ok_with_ranged_layout_corpus(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    # A blob written through the corpus writer path satisfies the contract.
    with corpus.connect(repo / "corpus" / "corpus.db"):
        pass
    result = runner.invoke(app, ["dvc-status", str(repo)])
    assert result.exit_code == 0, result.stdout
    assert "DVC metadata consistent" in result.stdout
