"""The staging→main promotion gate lives in scripts/promotion-gate.sh, invoked
from two places: the `promote` dispatch workflow (the maintainer's pre-flight
driver) and ci.yml's `promotion-gate` job (the required check on the promotion
PR). These tests lock that shape: both call sites delegate to the one script,
the promote workflow stays credential-minimal (no environment, no secrets,
ambient token only), the CI job is unreachable from anything but the same-repo
staging→main PR, and the freshness matcher's run-title coupling with the
integration-test workflow holds at both ends.
"""

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
GATE_SCRIPT = ROOT / "scripts" / "promotion-gate.sh"


def _load(path: Path) -> dict[Any, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    return data


def _steps_text(job: dict[str, Any]) -> str:
    return "\n".join(str(step.get("run", "")) for step in job.get("steps", []))


def test_promote_is_dispatch_only_and_credential_minimal() -> None:
    wf = _load(WORKFLOWS / "promote.yml")
    # yaml parses the `on:` key as boolean True
    assert list(wf[True].keys()) == ["workflow_dispatch"]
    assert wf["permissions"] == {}
    job = wf["jobs"]["promote"]
    # The sync push is the only write this workflow performs; widening this
    # block (or binding an environment, which would put App keys and role
    # ARNs in reach of a branch-mutating job) is a posture change.
    assert job["permissions"] == {
        "contents": "write",
        "actions": "read",
        "issues": "read",
    }
    assert "environment" not in job
    assert "secrets." not in (WORKFLOWS / "promote.yml").read_text()


def test_promote_delegates_both_gates_to_the_script() -> None:
    job = _load(WORKFLOWS / "promote.yml")["jobs"]["promote"]
    text = _steps_text(job)
    assert "scripts/promotion-gate.sh quiesce" in text
    assert "scripts/promotion-gate.sh freshness" in text


def test_ci_promotion_gate_runs_only_on_the_same_repo_promotion_pr() -> None:
    job = _load(WORKFLOWS / "ci.yml")["jobs"]["promotion-gate"]
    condition = job["if"]
    assert "github.base_ref == 'main'" in condition
    assert "github.head_ref == 'staging'" in condition
    # A fork branch named `staging` must get the skip, never the gate.
    assert "github.event.pull_request.head.repo.full_name == github.repository" in condition
    assert "scripts/promotion-gate.sh all" in _steps_text(job)
    assert "environment" not in job


def test_freshness_title_coupling_holds_at_both_ends() -> None:
    # The gate greps integration-test run titles; the workflow's run-name is
    # what produces them. A drift on either side makes freshness pass or fail
    # vacuously, so both literals are pinned here.
    script = GATE_SCRIPT.read_text()
    assert 'pattern="integration-test: ${scenario} / ${engine} @"' in script
    assert 'pattern="integration-test: ${scenario} /"' in script
    run_name = _load(WORKFLOWS / "integration-test.yml")["run-name"]
    assert isinstance(run_name, str)
    assert run_name.startswith("integration-test: ${{ inputs.scenario }} / ${{ inputs.engine }} @")


def test_required_scenarios_exist_on_the_integration_workflow() -> None:
    # Every scenario the gate demands must be dispatchable, or a promotion
    # could never satisfy freshness.
    script = GATE_SCRIPT.read_text()
    (line,) = [ln for ln in script.splitlines() if ln.startswith("REQUIRED_SCENARIOS=")]
    default = line.split(":-", 1)[1].rstrip('}"')
    required = {entry.split("/")[0] for entry in default.split()}
    wf = _load(WORKFLOWS / "integration-test.yml")
    dispatchable = set(wf[True]["workflow_dispatch"]["inputs"]["scenario"]["options"])
    assert required <= dispatchable
