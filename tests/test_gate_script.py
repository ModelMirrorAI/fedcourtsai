"""scripts/gate.sh names its stages on the command line: every name is checked
before any stage runs, so a typo — or a stage the script doesn't know — fails at
once, and no argument is ever silently ignored."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "gate.sh"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(GATE), *args], cwd=ROOT, capture_output=True, text=True, check=False
    )


def test_an_unknown_stage_is_refused_before_any_stage_runs() -> None:
    result = _run("lint", "no-such-stage")
    assert result.returncode == 2
    assert "unknown stage: no-such-stage" in result.stderr
    # lint never started: ruff's own output would name the formatted files.
    assert "already formatted" not in result.stdout + result.stderr


def test_a_lone_unknown_stage_is_refused_with_the_usage_line() -> None:
    result = _run("bogus")
    assert result.returncode == 2
    assert "usage: scripts/gate.sh" in result.stderr


def test_every_named_stage_runs_in_the_order_given() -> None:
    script = GATE.read_text()
    # The validation loop precedes the dispatch loop, and both iterate "$@".
    validate = script.index('for stage in "$@"; do')
    dispatch = script.index('for stage in "$@"; do', validate + 1)
    assert validate < dispatch
    assert "exit 2" in script[validate:dispatch]
