"""run-predict polls the live docket before minting, and the poll reaches usage.json.

The poll's result must travel as a step output, fixed before any agent runs: a
file left on the runner would sit where the agent, running as the same user,
could rewrite it before the usage step reads it.
"""

from pathlib import Path
from typing import Any

import yaml

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "run-predict.yml"


def _predict_steps() -> list[dict[str, Any]]:
    data = yaml.safe_load(WORKFLOW.read_text())
    steps: list[dict[str, Any]] = data["jobs"]["predict"]["steps"]
    return steps


def _step(step_id: str) -> dict[str, Any]:
    (step,) = [s for s in _predict_steps() if s.get("id") == step_id]
    return step


def test_the_forward_provision_polls_the_live_docket() -> None:
    run = _step("provision")["run"]

    assert "--refuse-terminal" in run
    assert "--pre-mint-poll " in run
    assert "--pre-mint-poll-out" in run


def test_the_poll_leaves_the_runner_as_a_step_output_before_the_agent_runs() -> None:
    run = _step("provision")["run"]

    assert "pre_mint_poll=" in run
    assert '>> "$GITHUB_OUTPUT"' in run
    # The file is removed in the same step, so nothing the agent can reach holds it.
    assert 'rm -f "$poll"' in run


def test_the_usage_step_records_the_poll_from_the_step_output() -> None:
    (usage,) = [s for s in _predict_steps() if "record-usage" in str(s.get("run", ""))]

    assert usage["env"]["PRE_MINT_POLL"] == "${{ steps.provision.outputs.pre_mint_poll }}"
    assert "--pre-mint-poll-file" in usage["run"]
