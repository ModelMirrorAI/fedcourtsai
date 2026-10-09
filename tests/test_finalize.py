"""Shared finalize helpers (:mod:`fedcourtsai.finalize`).

The branch-name and draft-vs-ready PR routing moved to
:mod:`fedcourtsai.collect` (covered by ``test_collect.py``). What remains here is
``agent_produced_output`` — the check that a cell wrote its *own* judgment
artifact rather than only the materialized ``event.yaml`` scaffold.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.finalize import (
    FinalizeRole,
    OutputSnapshot,
    agent_produced_output,
    reset_output_root,
    snapshot_output_root,
)
from fedcourtsai.paths import CasePaths


def _produced(role: FinalizeRole, data_root: Path, actor: str) -> bool:
    return agent_produced_output(
        role, data_root=data_root, court="ca9", docket=1, event="evt-x", actor=actor, run_id="R"
    )


def test_predict_output_present_only_when_prediction_written(tmp_path: Path) -> None:
    events = CasePaths(tmp_path, "ca9", 1).event("evt-x")
    # Just the materialized event scaffold: the agent produced nothing.
    events.event_file.parent.mkdir(parents=True)
    events.event_file.write_text("event_id: evt-x\n")
    assert not _produced(FinalizeRole.predict, tmp_path, "claude-baseline")
    # Now the agent's own prediction lands → produced.
    prediction = events.prediction("claude-baseline", "R")
    prediction.parent.mkdir(parents=True)
    prediction.write_text("{}")
    assert _produced(FinalizeRole.predict, tmp_path, "claude-baseline")


def test_predict_output_is_scoped_to_the_actor_and_run(tmp_path: Path) -> None:
    events = CasePaths(tmp_path, "ca9", 1).event("evt-x")
    other = events.prediction("codex-baseline", "R")
    other.parent.mkdir(parents=True)
    other.write_text("{}")
    # A different predictor's prediction does not count for this actor.
    assert not _produced(FinalizeRole.predict, tmp_path, "claude-baseline")


def test_evaluate_output_present_only_when_evaluation_written(tmp_path: Path) -> None:
    events = CasePaths(tmp_path, "ca9", 1).event("evt-x")
    assert not _produced(FinalizeRole.evaluate, tmp_path, "claude-judge")
    evaluation = events.evaluation("claude-judge", "claude-baseline", "R")
    evaluation.parent.mkdir(parents=True)
    evaluation.write_text("{}")
    assert _produced(FinalizeRole.evaluate, tmp_path, "claude-judge")


# --- the clean slate between in-step engine attempts ---------------------------


def test_a_reset_removes_exactly_what_the_attempt_added(tmp_path: Path) -> None:
    root = tmp_path / "evaluations" / "gemini-judge"
    (root / "alias-a" / "EARLIER").mkdir(parents=True)
    (root / "alias-a" / "EARLIER" / "evaluation.json").write_text('{"kept": true}')
    (root / "empty-but-ours").mkdir()
    snapshot = snapshot_output_root(root)
    assert snapshot.existed
    # What a failed attempt leaves: a new run directory with a half draft, a
    # new file beside a kept one, and a link pointing outside the root.
    outside = tmp_path / "outside.txt"
    outside.write_text("not the cell's")
    (root / "alias-a" / "NOW" / "deep").mkdir(parents=True)
    (root / "alias-a" / "NOW" / "deep" / "evaluation.md").write_text("half")
    (root / "alias-a" / "EARLIER" / "stray.md").write_text("added")
    (root / "link").symlink_to(outside)
    (root / "dirlink").symlink_to(tmp_path, target_is_directory=True)
    removed = reset_output_root(snapshot)
    assert removed == ["alias-a/EARLIER/stray.md", "alias-a/NOW", "dirlink", "link"]
    # Everything the snapshot held is untouched, and nothing a link named was
    # followed.
    assert (root / "alias-a" / "EARLIER" / "evaluation.json").read_text() == '{"kept": true}'
    assert (root / "empty-but-ours").is_dir()
    assert outside.read_text() == "not the cell's"
    assert snapshot_output_root(root).entries == snapshot.entries


def test_a_root_that_did_not_exist_is_removed_whole(tmp_path: Path) -> None:
    root = tmp_path / "predictions" / "gemini-baseline" / "R"
    snapshot = snapshot_output_root(root)
    assert not snapshot.existed and snapshot.entries == frozenset()
    root.mkdir(parents=True)
    (root / "reasoning.md").write_text("half")
    assert reset_output_root(snapshot) == ["."]
    assert not root.exists()
    # Nothing to do when the attempt wrote nothing at all.
    assert reset_output_root(snapshot) == []


def test_a_root_reached_through_a_link_is_refused(tmp_path: Path) -> None:
    elsewhere = tmp_path / "elsewhere"
    (elsewhere / "R").mkdir(parents=True)
    (elsewhere / "R" / "precious.json").write_text("{}")
    root = tmp_path / "predictions" / "gemini-baseline" / "R"
    snapshot = snapshot_output_root(root)
    # The attempt turns an ancestor of the (not yet existing) root into a link.
    root.parent.parent.mkdir(parents=True)
    root.parent.symlink_to(elsewhere, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        reset_output_root(snapshot)
    assert (elsewhere / "R" / "precious.json").is_file()
    # A root that is itself a link the attempt created is unlinked, not followed.
    root.parent.unlink()
    root.parent.mkdir()
    root.symlink_to(elsewhere / "R", target_is_directory=True)
    assert reset_output_root(snapshot) == ["."]
    assert (elsewhere / "R" / "precious.json").is_file()


def test_an_output_snapshot_round_trips_and_refuses_a_malformed_file(tmp_path: Path) -> None:
    root = tmp_path / "root"
    (root / "a").mkdir(parents=True)
    snapshot = snapshot_output_root(root)
    assert OutputSnapshot.from_json(snapshot.to_json()) == snapshot
    for bad in ("[]", '{"root": "relative", "existed": true, "entries": []}', '{"root": "/x"}'):
        with pytest.raises(ValueError):
            OutputSnapshot.from_json(bad)


def test_the_snapshot_and_reset_commands_round_trip_a_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path))
    coords = [
        "--role",
        "predict",
        "--court",
        "ca9",
        "--docket",
        "1",
        "--event",
        "evt-x",
        "--actor",
        "g",
        "--run-id",
        "R",
    ]
    snapshot = tmp_path / "snapshot.json"
    runner = CliRunner()
    result = runner.invoke(app, ["cell-output-snapshot", *coords, "--out", str(snapshot)])
    assert result.exit_code == 0, result.output
    draft = CasePaths(tmp_path, "ca9", 1).event("evt-x").reasoning("g", "R")
    draft.parent.mkdir(parents=True)
    draft.write_text("half")
    result = runner.invoke(app, ["cell-output-reset", *coords, "--snapshot", str(snapshot)])
    assert result.exit_code == 0, result.output
    assert not draft.parent.exists()
    # An unreadable snapshot is a refusal the step reads as "do not retry".
    result = runner.invoke(
        app, ["cell-output-reset", *coords, "--snapshot", str(tmp_path / "nope")]
    )
    assert result.exit_code == 1


def test_a_snapshot_rewritten_to_name_another_root_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The snapshot sits where the agent can write it; the root is the cell's."""
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    precious = tmp_path / "workspace"
    (precious / "src").mkdir(parents=True)
    forged = tmp_path / "forged.json"
    forged.write_text(OutputSnapshot(root=precious, existed=False, entries=frozenset()).to_json())
    coords = ["--role", "predict", "--court", "ca9", "--docket", "1", "--event", "evt-x"]
    result = CliRunner().invoke(
        app,
        ["cell-output-reset", *coords, "--actor", "g", "--run-id", "R", "--snapshot", str(forged)],
    )
    assert result.exit_code == 1
    assert (precious / "src").is_dir()
