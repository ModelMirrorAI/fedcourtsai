"""The harness-boundary registry, its ancestry side test, and the pooled composition."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fedcourtsai import process_version
from fedcourtsai.process_version import (
    HARNESS_BOUNDARIES,
    BoundaryHistoryError,
    HarnessBoundary,
    boundary_side,
    composition,
    is_retired,
)
from fedcourtsai.schemas import CountingWindow
from tests.conftest import set_windows

T1 = datetime(2026, 1, 1, tzinfo=UTC)
T2 = datetime(2026, 4, 1, tzinfo=UTC)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, check=True, text=True
    ).stdout.strip()


def _commit(repo: Path, message: str) -> str:
    _git(repo, "commit", "--allow-empty", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def history(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """A three-commit line plus a side branch off the first commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@users.noreply.github.com")
    _git(repo, "config", "user.name", "test")
    shas = {"before": _commit(repo, "before"), "merge": _commit(repo, "merge")}
    shas["after"] = _commit(repo, "after")
    _git(repo, "switch", "-q", "-c", "side", shas["before"])
    shas["side"] = _commit(repo, "side")
    return repo, shas


def _boundary(merge: str) -> HarnessBoundary:
    return HarnessBoundary("test-boundary", merge, T1, None, "all")


def test_a_cell_is_after_a_boundary_its_sha_descends_from_or_equals(
    history: tuple[Path, dict[str, str]],
) -> None:
    repo, shas = history
    boundary = _boundary(shas["merge"])
    assert boundary_side(boundary, shas["after"], repo=repo) == "after"
    # A run started on the carrying commit itself is post-change.
    assert boundary_side(boundary, shas["merge"], repo=repo) == "after"
    assert boundary_side(boundary, shas["before"], repo=repo) == "before"
    # A branch that never merged the change is before it, whatever its clock.
    assert boundary_side(boundary, shas["side"], repo=repo) == "before"


def test_an_unstamped_cell_sits_on_neither_side(history: tuple[Path, dict[str, str]]) -> None:
    repo, shas = history
    assert boundary_side(_boundary(shas["merge"]), None, repo=repo) is None
    assert boundary_side(_boundary(shas["merge"]), "", repo=repo) is None


def test_an_unknown_commit_is_refused_never_guessed(
    history: tuple[Path, dict[str, str]],
) -> None:
    repo, shas = history
    with pytest.raises(BoundaryHistoryError, match="holds no commit"):
        boundary_side(_boundary(shas["merge"]), "f" * 40, repo=repo)


def test_a_shallow_clone_is_refused(history: tuple[Path, dict[str, str]], tmp_path: Path) -> None:
    repo, shas = history
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", f"file://{repo}", str(shallow)],
        check=True,
        capture_output=True,
    )
    with pytest.raises(BoundaryHistoryError, match="shallow"):
        boundary_side(_boundary(shas["merge"]), shas["after"], repo=shallow)


def test_the_registry_is_well_formed() -> None:
    names = [boundary.name for boundary in HARNESS_BOUNDARIES]
    assert len(names) == len(set(names)) == 11
    assert [b.at for b in HARNESS_BOUNDARIES] == sorted(b.at for b in HARNESS_BOUNDARIES)
    for boundary in HARNESS_BOUNDARIES:
        assert len(boundary.merge) == 40 and int(boundary.merge, 16) >= 0
        assert boundary.at.tzinfo is UTC
    # The proc-v9 three split only the carried-forward windows: the same merge
    # moved claude-baseline's digest.
    for boundary in HARNESS_BOUNDARIES[-3:]:
        assert boundary.predictors == frozenset({"codex-baseline", "gemini-baseline"})


def test_every_production_window_names_its_predictor() -> None:
    """The ranked set reads retirement off the registry, so no window is anonymous."""
    assert all(window.predictor_id for window in process_version.COUNTING_WINDOWS)
    assert not is_retired("claude-baseline")
    assert not is_retired("codex-baseline")


def test_retirement_needs_every_owned_window_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    closed = CountingWindow(
        label="proc-a", digest="sha256:" + "a" * 64, opens=T1, closes=T2, predictor_id="alpha"
    )
    successor = CountingWindow(
        label="proc-b", digest="sha256:" + "b" * 64, opens=T2, predictor_id="alpha"
    )
    set_windows(monkeypatch, closed)
    assert is_retired("alpha")
    set_windows(monkeypatch, closed, successor)
    assert not is_retired("alpha")
    # A predictor no window names is unknown, not retired.
    assert not is_retired("beta")


def test_composition_lists_every_window_in_opening_order() -> None:
    first = CountingWindow(label="proc-a", digest="sha256:" + "a" * 64, opens=T1, closes=T2)
    second = CountingWindow(label="proc-b", digest="sha256:" + "b" * 64, opens=T2)
    assert [(w.process_window, w.n) for w in composition({second: 1, first: 3})] == [
        ("proc-a", 3),
        ("proc-b", 1),
    ]
    # One window is still listed: the composition is part of every pooled figure.
    assert [(w.process_window, w.opens, w.n) for w in composition({first: 2})] == [
        ("proc-a", T1, 2)
    ]
