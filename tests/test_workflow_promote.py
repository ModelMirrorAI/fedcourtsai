"""The staging→main promotion gate lives in scripts/promotion-gate.sh, invoked
from two places: the `promote` dispatch workflow (the maintainer's pre-flight
driver) and ci.yml's `promotion-gate` job (the required check on the promotion
PR). These tests lock that shape: both call sites delegate to the one script,
the promote workflow stays credential-minimal (no environment, no secrets,
ambient token only), the CI job is unreachable from anything but the same-repo
staging→main PR, and the freshness matcher's run-title coupling with the
integration-test workflow holds at both ends. The `main-base` merge-routing
jail and dependabot's staging targeting live here too: routing to `main` is
policy these tests keep mechanical.
"""

from pathlib import Path
from typing import Any

import yaml

from fedcourtsai import metrics_refresh
from fedcourtsai.finalize import FinalizeRole

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
    # Strictly read-only: the sync push and the promotion PR are both the
    # maintainer's own writes. Any write scope here (or a bound environment,
    # which would put App keys and role ARNs in reach) is a posture change.
    assert job["permissions"] == {
        "contents": "read",
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
    # Freshness must see the PR *head* sha — no integration run ever carries
    # the synthetic merge-commit sha, so github.sha would be vacuously red.
    (gate_step,) = [s for s in job["steps"] if "promotion-gate" in str(s.get("run", ""))]
    assert gate_step["env"]["HEAD_SHA"] == "${{ github.event.pull_request.head.sha }}"


def test_freshness_title_coupling_holds_at_both_ends() -> None:
    # The gate greps integration-test run titles; the workflow's run-name is
    # what produces them. A drift on either side makes freshness pass or fail
    # vacuously, so both literals are pinned here.
    script = GATE_SCRIPT.read_text()
    assert 'prefix="integration-test: ${scenario} / ${engine} @"' in script
    assert 'prefix="integration-test: ${scenario} /"' in script
    # The suffix match is what pins the staging deployment environment.
    assert 'grep -F "@ staging"' in script
    run_name = _load(WORKFLOWS / "integration-test.yml")["run-name"]
    assert isinstance(run_name, str)
    assert run_name.startswith("integration-test: ${{ inputs.scenario }} / ${{ inputs.engine }} @")
    assert run_name.endswith("@ ${{ inputs.deploy-environment }}")


def _required_scenario_entries() -> list[str]:
    script = GATE_SCRIPT.read_text()
    (line,) = [ln for ln in script.splitlines() if ln.startswith("REQUIRED_SCENARIOS=")]
    return line.split(":-", 1)[1].rstrip('}"').split()


def test_required_scenarios_exist_on_the_integration_workflow() -> None:
    # Every scenario — and every engine variant — the gate demands must be
    # dispatchable, or a promotion could never satisfy freshness.
    entries = _required_scenario_entries()
    required = {entry.split("/")[0] for entry in entries}
    engines = {entry.split("/", 1)[1] for entry in entries if "/" in entry}
    inputs = _load(WORKFLOWS / "integration-test.yml")[True]["workflow_dispatch"]["inputs"]
    assert required <= set(inputs["scenario"]["options"])
    assert engines <= set(inputs["engine"]["options"])


def test_promote_help_text_lists_every_required_scenario() -> None:
    # On a freshness failure promote.yml prints the dispatch commands that
    # would satisfy the gate; if that help text drifts from the script's
    # required set, the maintainer is told to dispatch the wrong runs.
    # The names ride shell for-loops, so pin each name's presence in the step
    # text rather than a fully expanded command line.
    text = _steps_text(_load(WORKFLOWS / "promote.yml")["jobs"]["promote"])
    for entry in _required_scenario_entries():
        for name in entry.split("/", 1):
            assert name in text, f"promote.yml help text is missing {name!r}"


def test_main_base_jail_covers_every_legitimate_lane() -> None:
    # Merge routing to main rides this job's allowlist, which must track the
    # real bot lanes mechanically, or a renamed lane's PRs hit the jail.
    job = _load(WORKFLOWS / "ci.yml")["jobs"]["main-base"]
    condition = job["if"]
    assert "github.base_ref == 'main'" in condition
    assert "github.head_ref == 'staging'" in condition
    # The negation is the load-bearing structure: the job runs on everything
    # OUTSIDE the allowlist. Without the `!(` the jail inverts — it would fail
    # exactly the legitimate lanes and wave feature PRs through.
    assert "!(" in condition
    assert condition.index("!(") < condition.index("github.head_ref == 'staging'")
    # Fork heads must never match the allowlist, whatever their branch name —
    # the same-repo conjunct must sit INSIDE the negated group.
    same_repo = "github.event.pull_request.head.repo.full_name == github.repository"
    assert same_repo in condition
    assert condition.index("!(") < condition.index(same_repo)
    for role in FinalizeRole:
        assert f"startsWith(github.head_ref, '{role.value}/run-')" in condition
    # Pin the other end of the prefix coupling: the collect plan builder must
    # still construct branches under `<role>/run-`, or the jail's allowlist
    # silently stops matching what collect actually pushes.
    collect_src = (ROOT / "src" / "fedcourtsai" / "collect.py").read_text()
    assert 'f"{role.value}/run-{run_id}"' in collect_src
    assert "startsWith(github.head_ref, 'cleanup/')" in condition
    assert f"github.head_ref == '{metrics_refresh.REFRESH_BRANCH}'" in condition
    assert f"github.head_ref == '{metrics_refresh.BACKTEST_BRANCH}'" in condition
    assert job["permissions"] == {}
    # The job exists only to fail: when the `if` matches, the PR must not merge.
    assert "exit 1" in _steps_text(job)


def test_dependabot_targets_staging() -> None:
    # Dependency bumps are code/config; without an explicit target-branch
    # dependabot PRs go to main, where the main-base jail would strand them.
    config = _load(ROOT / ".github" / "dependabot.yml")
    for update in config["updates"]:
        assert update.get("target-branch") == "staging", update["package-ecosystem"]
