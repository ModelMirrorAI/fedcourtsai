"""Shared finalize helpers (:mod:`fedcourtsai.finalize`).

The branch-name and draft-vs-ready PR routing moved to
:mod:`fedcourtsai.collect` (covered by ``test_collect.py``). What remains here is
``agent_produced_output`` — the check that a cell wrote its *own* judgment
artifact rather than only the materialized ``event.yaml`` scaffold.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from fedcourtsai.finalize import FinalizeRole, agent_produced_output
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


def test_agent_produced_output_rejects_reconcile(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        _produced(FinalizeRole.reconcile, tmp_path, "x")
