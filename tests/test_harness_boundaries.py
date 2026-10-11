"""The harness-boundary registry, its ancestry side test, and the pooled composition."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai import leaderboard, process_version
from fedcourtsai.cli import app
from fedcourtsai.leaderboard import boundary_sides, skill_components
from fedcourtsai.process_version import (
    HARNESS_BOUNDARIES,
    BoundaryHistoryError,
    HarnessBoundary,
    boundary_side,
    composition,
    is_retired,
)
from fedcourtsai.release_sensitivity import project, rebuild
from fedcourtsai.schemas import CountingWindow, Leaderboard, ProcessVersion
from fedcourtsai.serialize import read_model
from fedcourtsai.store import stratify
from tests.conftest import set_windows
from tests.test_dataset_export import _event, _grade, _outcome, _prediction

T1 = datetime(2026, 1, 1, tzinfo=UTC)
T2 = datetime(2026, 4, 1, tzinfo=UTC)
#: When every fixture cell is stamped: a test boundary dated here falls inside
#: their span, which a listed boundary must.
STAMPED = datetime(2026, 2, 1, tzinfo=UTC)


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
    # The two that reached the corpus by back-fill are marked gradual.
    assert {b.name for b in HARNESS_BOUNDARIES if b.gradual} == {
        "merits-brief-spellings-consolidated-lead",
        "widened-document-kinds-freshness",
    }


def test_a_stamped_value_that_is_not_a_sha_never_reaches_git(
    history: tuple[Path, dict[str, str]],
) -> None:
    repo, shas = history
    for bad in ("fill", "--upload-pack=x", "HEAD", shas["after"].upper()):
        with pytest.raises(BoundaryHistoryError, match="not a commit sha"):
            boundary_side(_boundary(shas["merge"]), bad, repo=repo)


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


def test_the_board_reads_each_cells_side_off_its_pipeline_sha(
    history: tuple[Path, dict[str, str]], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End to end over a real history: a cell built before the carrying commit,
    one built on it, and one with no `pipeline_sha`, through `boundary_sides`."""
    repo, shas = history
    digest = "sha256:" + "a" * 64
    set_windows(monkeypatch, CountingWindow(label="proc-a", digest=digest, opens=T1))
    boundary = HarnessBoundary("test-boundary", shas["merge"], STAMPED, None, "all")
    monkeypatch.setattr(leaderboard, "HARNESS_BOUNDARIES", (boundary,))
    data = tmp_path / "data"
    for n, sha in ((1, shas["before"]), (2, shas["merge"]), (3, None)):
        case = f"scotus/{n}"
        _event(data, case)
        _outcome(data, case, resolved_at=datetime(2026, 3, 1, tzinfo=UTC).date())
        stamp = ProcessVersion(
            label="proc-a", digest=digest, stamped_at=datetime(2026, 2, 1, tzinfo=UTC)
        )
        _prediction(
            data, case, stamp=stamp.model_copy(update={"pipeline_sha": sha}), mode="forward"
        )
        _grade(data, case, "e1", prediction_run_id="p1", stamped=datetime(2026, 3, 2, tzinfo=UTC))
    run = stratify(data)
    sides = boundary_sides(run.cells, data, repo=repo)
    assert sorted(
        (
            ev.case_id,
            sides[(ev.case_id, ev.event_id, ev.predictor_id, ev.evaluator_id, ev.run_id)].sides,
        )
        for ev, *_ in run.cells
    ) == [
        ("scotus/1", {"test-boundary": "before"}),
        ("scotus/2", {"test-boundary": "after"}),
        ("scotus/3", {"test-boundary": None}),
    ]
    board = leaderboard.build_leaderboard(
        run.cells, cell_windows=run.cell_windows, boundaries=sides
    )
    (entry,) = board.entries
    assert [(b.boundary, b.before, b.after, b.unstamped, b.scope) for b in entry.boundaries] == [
        ("test-boundary", 1, 1, 1, "all")
    ]


def _stamped_ledger(data: Path, digest: str, shas: list[str | None]) -> None:
    """One forward cell per case, its scored prediction stamped at each sha."""
    for n, sha in enumerate(shas, start=1):
        case = f"scotus/{n}"
        _event(data, case)
        _outcome(data, case, resolved_at=datetime(2026, 3, 1, tzinfo=UTC).date())
        stamp = ProcessVersion(
            label="proc-a",
            digest=digest,
            stamped_at=datetime(2026, 2, 1, tzinfo=UTC),
            pipeline_sha=sha,
        )
        _prediction(data, case, stamp=stamp, mode="forward")
        _grade(data, case, "e1", prediction_run_id="p1", stamped=datetime(2026, 3, 2, tzinfo=UTC))


def test_the_leaderboard_command_lists_a_boundary_read_in_its_checkout(
    history: tuple[Path, dict[str, str]], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The command reads each cell's side in the checkout it runs from, and the
    listing leaves the release-sensitivity projection of the board unchanged."""
    repo, shas = history
    digest = "sha256:" + "a" * 64
    set_windows(monkeypatch, CountingWindow(label="proc-a", digest=digest, opens=T1))
    boundary = HarnessBoundary("test-boundary", shas["merge"], STAMPED, None, "all", gradual=True)
    monkeypatch.setattr(leaderboard, "HARNESS_BOUNDARIES", (boundary,))
    data = tmp_path / "data"
    _stamped_ledger(data, digest, [shas["before"], shas["after"]])
    monkeypatch.chdir(repo)
    out = tmp_path / "leaderboard.json"
    env = {"FEDCOURTS_DATA_ROOT": str(data), "FEDCOURTS_METRICS_ROOT": str(tmp_path / "m")}
    result = CliRunner().invoke(app, ["leaderboard", "--out", str(out)], env=env)
    assert result.exit_code == 0, result.output
    board = read_model(out, Leaderboard)
    (entry,) = board.entries
    assert [(b.boundary, b.before, b.after, b.gradual) for b in entry.boundaries] == [
        ("test-boundary", 1, 1, True)
    ]
    # release-sensitivity rebuilds with the pass's windows, without boundaries,
    # and still matches: its projection carries the composition and the cut.
    run = stratify(data)
    assert project(board) == project(
        rebuild(run.cells, data, skill_components(run.cells, data, None), run.cell_windows)
    )


def test_a_cell_the_checkout_cannot_place_is_named_in_the_refusal(
    history: tuple[Path, dict[str, str]], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, shas = history
    digest = "sha256:" + "a" * 64
    set_windows(monkeypatch, CountingWindow(label="proc-a", digest=digest, opens=T1))
    monkeypatch.setattr(leaderboard, "HARNESS_BOUNDARIES", (_boundary(shas["merge"]),))
    data = tmp_path / "data"
    _stamped_ledger(data, digest, ["f" * 40])
    with pytest.raises(
        BoundaryHistoryError, match=r"scotus/1 .* alpha .*pipeline_sha f{40}.*fetch"
    ):
        boundary_sides(stratify(data).cells, data, repo=repo)
