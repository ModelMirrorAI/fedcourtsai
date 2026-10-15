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


def test_the_post_run_poll_records_and_never_refuses() -> None:
    step = _step("post_poll")

    assert step["continue-on-error"] is True
    assert "poll-docket" in step["run"]
    # The docket number comes from the provisioning step's output, fixed before
    # the agent ran — never from the cell's record.
    assert step["env"]["PRE_MINT_POLL"] == "${{ steps.provision.outputs.pre_mint_poll }}"
    assert ".docket_number" in step["run"]
    assert "post_run_poll=" in step["run"]
    assert 'rm -f "$poll"' in step["run"]
    steps = _predict_steps()
    order = [s.get("id") or s.get("name") for s in steps]
    usage = next(i for i, s in enumerate(steps) if "record-usage" in str(s.get("run", "")))
    assert order.index("post_poll") < usage


def test_the_usage_step_records_the_post_run_poll() -> None:
    (usage,) = [s for s in _predict_steps() if "record-usage" in str(s.get("run", ""))]

    assert usage["env"]["POST_RUN_POLL"] == "${{ steps.post_poll.outputs.post_run_poll }}"
    assert "--post-run-poll-file" in usage["run"]


def test_a_poll_refused_cell_records_its_refusal_in_status_json() -> None:
    (status,) = [s for s in _predict_steps() if "> status.json" in str(s.get("run", ""))]

    assert status["env"]["PRE_MINT_POLL"] == "${{ steps.provision.outputs.pre_mint_poll }}"
    assert "pre_mint_refusal:$pre_mint_refusal" in status["run"]
    assert '.state == "decided"' in status["run"]
