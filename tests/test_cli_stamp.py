"""End-to-end coverage of `fedcourts stamp-cell` and `process-digest`.

The stamp is harness-owned: the agent writes an unstamped prediction/evaluation,
then this step reads it, injects the process version derived from the registry,
and rewrites it. These exercise the real command against seeded ledger cells.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from fedcourtsai.cli import app
from fedcourtsai.paths import CasePaths
from tests.conftest import seed_evaluation, seed_prediction

runner = CliRunner()


@pytest.fixture(autouse=True)
def _data_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("FEDCOURTS_DATA_ROOT", str(tmp_path / "data"))
    return tmp_path / "data"


def _stamp(role: str, actor: str, docket: int, event: str, run_id: str) -> Result:
    return runner.invoke(
        app,
        [
            "stamp-cell",
            "--court",
            "scotus",
            "--docket",
            str(docket),
            "--event",
            event,
            "--run-id",
            run_id,
            "--role",
            role,
            "--actor",
            actor,
            "--stamped-at",
            "2026-01-01T00:00:00Z",
            "--pipeline-sha",
            "sha-abc",
        ],
    )


def test_stamp_injects_the_process_version_into_the_agents_prediction(_data_root: Path) -> None:
    seed_prediction(_data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    path = (
        CasePaths(_data_root, "scotus", 1)
        .event("evt-x")
        .prediction("claude-baseline", "20260101T000000Z")
    )
    assert json.loads(path.read_text())["process_version"] is None, "agent writes it unstamped"

    result = _stamp("predictor", "claude-baseline", 1, "evt-x", "20260101T000000Z")
    assert result.exit_code == 0, result.output

    pv = json.loads(path.read_text())["process_version"]
    assert pv["label"] == "proc-v1"
    assert pv["digest"].startswith("sha256:")
    assert pv["pipeline_sha"] == "sha-abc"


def test_stamp_is_byte_stable_under_a_fixed_clock(_data_root: Path) -> None:
    """Everything but `stamped_at` is deterministic: re-stamping with the same
    clock is byte-identical. In production `stamped_at` defaults to now, so a
    rerun's bytes differ there — but the partition-relevant `digest` is stable
    (proven in test_process_version), and a rerun regenerates the cell from the
    agent anyway, so the wall-clock field never moves a metric."""
    seed_prediction(_data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    path = (
        CasePaths(_data_root, "scotus", 1)
        .event("evt-x")
        .prediction("claude-baseline", "20260101T000000Z")
    )
    _stamp("predictor", "claude-baseline", 1, "evt-x", "20260101T000000Z")
    first = path.read_bytes()
    _stamp("predictor", "claude-baseline", 1, "evt-x", "20260101T000000Z")
    assert path.read_bytes() == first


def test_stamp_evaluator_covers_every_predictors_evaluation(_data_root: Path) -> None:
    """One evaluate cell scores every predictor, so the stamp must reach all of
    its evaluation.json — a single-file assumption would leave most unstamped."""
    for predictor in ("claude-baseline", "codex-baseline", "gemini-baseline"):
        seed_evaluation(
            _data_root,
            "scotus",
            2,
            "evt-y",
            evaluator_id="claude-judge",
            predictor_id=predictor,
            run_id="RID",
        )
    result = _stamp("evaluator", "claude-judge", 2, "evt-y", "RID")
    assert result.exit_code == 0, result.output
    assert "3 file(s)" in result.output

    for predictor in ("claude-baseline", "codex-baseline", "gemini-baseline"):
        path = (
            CasePaths(_data_root, "scotus", 2)
            .event("evt-y")
            .evaluation("claude-judge", predictor, "RID")
        )
        assert json.loads(path.read_text())["process_version"]["label"] == "proc-v1"


def test_a_missing_artifact_is_a_clean_no_op(_data_root: Path) -> None:
    """A no-output cell has nothing to stamp; it must not fail the cell."""
    result = _stamp("predictor", "claude-baseline", 999, "evt-x", "RID")
    assert result.exit_code == 0
    assert "no predictor artifact" in result.output


def test_an_unknown_actor_fails_the_cell(_data_root: Path) -> None:
    """A registry typo must fail loudly, not ship an unstamped-but-frozen-looking
    cell — the artifact exists but the config to derive its digest does not."""
    seed_prediction(_data_root, "scotus", 1, "evt-x", predictor_id="claude-baseline")
    result = _stamp("predictor", "no-such-predictor", 1, "evt-x", "20260101T000000Z")
    assert result.exit_code != 0


def test_process_digest_all_lists_every_enabled_actor() -> None:
    result = runner.invoke(app, ["process-digest", "--all"])
    assert result.exit_code == 0, result.output
    lines = [line for line in result.output.splitlines() if line.strip()]
    # Three predictors + three evaluators in the shipped registry.
    assert len(lines) == 6
    assert all("sha256:" in line and "proc-v1" in line for line in lines)
