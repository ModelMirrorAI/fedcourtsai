"""What counts as a job that runs an agent, for the workflow invariant tests.

"Runs an agent" means a step that hands control to an engine: the
claude-code and codex actions, the codex user setup that precedes a codex
cell, or the `engine-cli` composite, which installs the pinned engine CLI that
a shell step or the replay runner then invokes. A local composite counts as
the steps it runs, recursively. The composite is the one place an engine CLI
is installed from (`tests/test_workflow_engine_pins.py`), so the install step
marks every job that can run one.

Two invariants rest on this detector: no agent job reaches an App credential
(`tests/test_workflow_token_holder.py`), and no agent job binds the
environment the production read-write role trusts
(`tests/test_workflow_corpus_write.py`). It is maintainer-owned with them, so
a change that blinds it is reviewed as the change to both that it is.
"""

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
ACTIONS = ROOT / ".github" / "actions"

# A step whose `uses:` contains one of these hands control to a coding agent.
AGENT_USES = (
    "anthropics/claude-code-action",
    "openai/codex-action",
    "google-github-actions/run-gemini-cli",
    "./.github/actions/engine-cli",
    "./.github/actions/codex-user-setup",
)


def load(path: Path) -> dict[Any, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict), path
    return data


def steps(container: dict[Any, Any]) -> list[dict[Any, Any]]:
    return [step for step in container.get("steps") or [] if isinstance(step, dict)]


def composite_steps(uses: str) -> list[dict[Any, Any]]:
    """The steps a local composite runs, or none for any other `uses:`."""
    if not uses.startswith("./.github/actions/"):
        return []
    name = uses.removeprefix("./.github/actions/").rstrip("/")
    for filename in ("action.yml", "action.yaml"):
        path = ACTIONS / name / filename
        if path.exists():
            return steps(load(path).get("runs") or {})
    return []


def expanded(step: dict[Any, Any], seen: frozenset[str] = frozenset()) -> list[dict[Any, Any]]:
    """The step, then every step a local composite it calls runs, recursively."""
    uses = str(step.get("uses") or "")
    if uses in seen:
        return [step]
    inner = composite_steps(uses)
    return [step, *(s for i in inner for s in expanded(i, seen | {uses}))]


def runs_agent(step: dict[Any, Any]) -> bool:
    return any(marker in str(s.get("uses") or "") for s in expanded(step) for marker in AGENT_USES)
