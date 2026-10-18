"""When a promotion owes the gate's admin-read `contexts` stage."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.contexts_due import (
    CONTEXTS_SENSITIVE,
    batch_paths,
    contexts_due,
    split_due,
    verdict_line,
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize(
    "path",
    [
        ".github/workflows/ci.yml",
        ".github/workflows/nested/anything.yml",
        "scripts/promotion-gate.sh",
        "src/fedcourtsai/ruleset_checks.py",
        "src/fedcourtsai/environment_checks.py",
        "src/fedcourtsai/required_checks.py",
        "config/corpus-check.yaml",
        "src/fedcourtsai/corpus_check.py",
    ],
)
def test_a_path_the_stage_judges_against_makes_it_due(path: str) -> None:
    assert contexts_due([path]) == [path]


@pytest.mark.parametrize(
    "path",
    [
        "data/cases/scotus/1/events/evt-x/outcome.json",
        "docs/security.md",
        ".github/actions/setup-python-env/action.yml",
        ".github/workflows",  # the directory's name alone is no file in it
        "scripts/promotion-gate.sh.orig",
        "src/fedcourtsai/ruleset_checks_extra.py",
        "config/review-hold.yaml",  # nothing the stage runs reads it
        "",
    ],
)
def test_anything_else_does_not(path: str) -> None:
    assert contexts_due([path]) == []


def test_the_due_paths_come_back_sorted_and_once() -> None:
    paths = ["config/corpus-check.yaml\n", ".github/workflows/b.yml", ".github/workflows/b.yml"]
    assert contexts_due(paths) == [".github/workflows/b.yml", "config/corpus-check.yaml"]


def test_every_listed_file_exists() -> None:
    """A rename that leaves the list naming a missing file would read as never due."""
    for entry in CONTEXTS_SENSITIVE:
        target = ROOT / entry
        assert target.is_dir() if entry.endswith("/") else target.is_file(), entry


@pytest.mark.parametrize(
    ("due", "before", "after"),
    [
        (["scripts/promotion-gate.sh"], True, False),
        ([".github/workflows/ci.yml"], False, True),
        ([".github/workflows/ci.yml", "src/fedcourtsai/corpus_check.py"], True, True),
    ],
)
def test_the_verdict_says_when_to_run_the_stage(due: list[str], before: bool, after: bool) -> None:
    """The stage reads main's workflows, so a workflow change is checked after the merge."""
    assert split_due(due) == (
        [p for p in due if not p.startswith(".github/")],
        [p for p in due if p.startswith(".github/")],
    )
    line = verdict_line(due)
    assert ("before merging" in line) is before
    assert ("after merging for the workflow changes" in line) is after


def test_the_verdict_names_what_makes_it_due_and_counts_the_rest() -> None:
    assert verdict_line([]).startswith("contexts: not due")
    line = verdict_line([f".github/workflows/w{i}.yml" for i in range(7)])
    assert line.startswith("contexts: due — the batch changes .github/workflows/w0.yml")
    assert "(+2 more)" in line
    assert "scripts/promotion-gate.sh contexts" in line


def _repo(tmp_path: Path) -> tuple[Path, str]:
    """A main that gains a workflow change after a data-only batch branched off it."""
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
        ).stdout.strip()

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.invalid")
    git("config", "user.name", "t")
    (repo / "README").write_text("base\n")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    git("switch", "-q", "-c", "batch")
    (repo / "data").mkdir()
    (repo / "data" / "row.json").write_text("{}\n")
    git("add", "-A")
    git("commit", "-q", "-m", "data only")
    batch = git("rev-parse", "HEAD")
    git("switch", "-q", "main")
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text("on: push\n")
    git("add", "-A")
    git("commit", "-q", "-m", "main moves on")
    return repo, batch


def test_what_main_gained_after_the_batch_branched_is_not_the_batchs(tmp_path: Path) -> None:
    repo, batch = _repo(tmp_path)
    assert batch_paths(repo, batch, "main") == ["data/row.json"]
    assert contexts_due(batch_paths(repo, batch, "main")) == []


def test_the_cli_prints_the_verdict_or_the_list_and_never_fails_on_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, batch = _repo(tmp_path)
    monkeypatch.chdir(repo)
    runner = CliRunner()
    plain = runner.invoke(app, ["contexts-due", "--at", batch, "--main-ref", "main"])
    assert plain.exit_code == 0
    assert plain.output.startswith("contexts: not due")
    # The reverse diff (main's workflow change as the batch) is due, and still exits 0.
    due = runner.invoke(app, ["contexts-due", "--at", "main", "--main-ref", batch, "--json"])
    assert due.exit_code == 0
    assert json.loads(due.output) == [".github/workflows/ci.yml"]


def test_the_cli_exits_1_when_git_cannot_read_the_diff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, batch = _repo(tmp_path)
    monkeypatch.chdir(repo)
    result = CliRunner().invoke(app, ["contexts-due", "--at", batch, "--main-ref", "no-such"])
    assert result.exit_code == 1


def test_the_gate_stage_reports_and_never_fails() -> None:
    script = (ROOT / "scripts" / "promotion-gate.sh").read_text()
    stage = script.split("contexts_due() {", 1)[1].split("\n}\n", 1)[0]
    assert not re.search(r"\bfail\b", stage)
    all_stage = script.split("  all)", 1)[1].split(";;", 1)[0]
    assert all_stage.index("registry ") < all_stage.index("contexts_due ")


def test_the_gate_stage_warns_without_main_fetched(tmp_path: Path) -> None:
    repo, batch = _repo(tmp_path)
    subprocess.run(["git", "-C", str(repo), "branch", "-q", "-m", "main", "trunk"], check=True)
    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "promotion-gate.sh"), "contexts-due", batch],
        capture_output=True,
        text=True,
        check=False,
        cwd=repo,
        env={"PATH": os.environ["PATH"], "GITHUB_REPOSITORY": "owner/repo"},
    )
    assert result.returncode == 0
    assert "origin/main is not fetched" in result.stdout
