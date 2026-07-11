"""The trusted pipeline-App bot must reach the agent step.

`run-pull` files the `run:predict` / `run:evaluate` handoff
issues as the data App (`fedcourtsai-data[bot]`), and the plan job's
`authorize-trigger` gate approves that Bot sender. But claude-code-action and
codex-action each run their *own* actor check and refuse a bot by default, so the
automated handoff silently dies at the agent step unless the bot is allowlisted
there too. These tests lock that allowlist in — a regression here breaks the whole
automated pipeline while every other check stays green, so it needs its own guard.
"""

from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"

# The data App that files the handoff issues; the actor every automated run carries.
PIPELINE_BOT = "fedcourtsai-data[bot]"

# Each agent action and the `with:` input that allowlists a bot past its actor check.
AGENT_BOT_INPUT = {
    "anthropics/claude-code-action": "allowed_bots",
    "openai/codex-action": "allow-bot-users",
}

# The fan-out workflows whose agent steps run on the bot handoff.
AGENT_WORKFLOWS = ("run-predict.yml", "run-evaluate.yml")


def _load(name: str) -> dict[Any, Any]:
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    assert isinstance(data, dict)
    return data


def _agent_steps(wf: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Every step that invokes one of the known agent actions, with its action key."""
    found: list[tuple[str, dict[str, Any]]] = []
    for job in wf["jobs"].values():
        for step in job.get("steps", []) or []:
            uses = step.get("uses", "")
            for action, _input in AGENT_BOT_INPUT.items():
                if uses.startswith(action + "@"):
                    found.append((action, step))
    return found


def test_every_agent_step_allowlists_the_pipeline_bot() -> None:
    for name in AGENT_WORKFLOWS:
        steps = _agent_steps(_load(name))
        assert steps, f"{name} has no agent step to check"
        for action, step in steps:
            input_name = AGENT_BOT_INPUT[action]
            value = str(step.get("with", {}).get(input_name, ""))
            assert PIPELINE_BOT in value, (
                f"{name}: {action} step must set {input_name} to include "
                f"{PIPELINE_BOT!r} so the run-pull handoff reaches the agent "
                f"(got {value!r})"
            )


def test_agent_steps_do_not_allow_all_bots() -> None:
    """Allow the one trusted bot, never the `*` wildcard (a public-repo footgun)."""
    for name in AGENT_WORKFLOWS:
        for action, step in _agent_steps(_load(name)):
            value = str(step.get("with", {}).get(AGENT_BOT_INPUT[action], ""))
            assert "*" not in value, f"{name}: {action} must not allow all bots ('*')"
