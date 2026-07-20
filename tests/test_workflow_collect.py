"""`collect` is the single writer for a run's agent output, and it used to exist
as 250 lines duplicated verbatim in run-predict.yml and run-evaluate.yml — so a
durability fix had to land twice, and one copy could silently drift from the
other. It now lives in the `collect-run` composite action.

These tests lock that shape in. The action linters check syntax; only this checks
that both workflows still delegate, that the security posture stayed in the
caller where it is reviewable next to the trigger, and that the two call sites
differ by nothing but their role.
"""

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
COLLECT_ACTION = ROOT / ".github" / "actions" / "collect-run" / "action.yml"

# Each fan-out workflow and the matrix job its collect job waits on.
FAN_OUTS = {"run-predict.yml": "predict", "run-evaluate.yml": "evaluate"}

# Work that must NOT reappear inline in a workflow: whoever re-adds it has
# forked the collect contract again.
COLLECT_INTERNALS = ("download-artifact", "gh pr create", "collect-plan")


def _load(path: Path) -> dict[Any, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    return data


def _collect_job(workflow: str) -> dict[str, Any]:
    job = _load(WORKFLOWS / workflow)["jobs"]["collect"]
    assert isinstance(job, dict)
    return job


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return list(job.get("steps", []))


def test_both_workflows_delegate_collect_to_the_shared_action() -> None:
    for workflow, role in FAN_OUTS.items():
        steps = _steps(_collect_job(workflow))
        delegations = [s for s in steps if s.get("uses") == "./.github/actions/collect-run"]
        assert len(delegations) == 1, f"{workflow} must delegate collect exactly once"
        assert delegations[0]["with"]["role"] == role


def test_no_workflow_reimplements_collect_inline() -> None:
    """The regression guard: re-inlining any of this forks the contract again."""
    for workflow in FAN_OUTS:
        body = (WORKFLOWS / workflow).read_text()
        collect_start = body.index("\n  collect:")
        collect_body = body[collect_start:]
        for marker in COLLECT_INTERNALS:
            assert marker not in collect_body, (
                f"{workflow}'s collect job contains {marker!r} inline; "
                "it belongs in .github/actions/collect-run"
            )


def test_the_two_call_sites_differ_only_by_role() -> None:
    """Anything else that diverges is drift the composite was meant to end."""
    predict, evaluate = (_collect_job(w) for w in FAN_OUTS)

    # The matrix job each waits on is legitimately per-workflow.
    assert predict.pop("needs") == ["plan", "predict"]
    assert evaluate.pop("needs") == ["plan", "evaluate"]

    # The delegating step differs only in `role`; normalize it out, then the two
    # jobs must be byte-equal — setup steps, permissions, timeout, everything.
    def _normalized(job: dict[str, Any]) -> dict[str, Any]:
        call = next(s for s in _steps(job) if s.get("uses", "").endswith("collect-run"))
        call["with"] = {k: v for k, v in call["with"].items() if k != "role"}
        return job

    assert _normalized(predict) == _normalized(evaluate), (
        "the two collect jobs diverge by more than their role — that drift is "
        "exactly what the composite extraction was meant to end"
    )


def test_the_caller_keeps_the_security_posture_visible() -> None:
    """`permissions`/`environment` must stay in the workflow, not move behind a
    `uses:` — they are the trust boundary and belong next to the trigger."""
    for workflow in FAN_OUTS:
        job = _collect_job(workflow)
        assert job["environment"] == "runner"
        assert job["permissions"] == {
            "contents": "write",
            "pull-requests": "write",
            "issues": "write",
        }


def test_the_composite_derives_every_role_dependent_string() -> None:
    """A hardcoded role in the shared body would make one workflow silently wrong."""
    body = COLLECT_ACTION.read_text()
    _, run_block = body.split("runs:", 1)
    for stray in ("--role predict", "--role evaluate", "pattern: predict-", "pattern: evaluate-"):
        assert stray not in run_block, f"{stray!r} is hardcoded; derive it from `role`"
    # Both nouns are reachable, and an unknown role fails loudly rather than
    # rendering an empty warning.
    assert "predict) noun=prediction" in run_block
    assert "evaluate) noun=evaluation" in run_block
    assert "::error::unknown role" in run_block


def test_the_issue_comments_use_the_ambient_token_not_the_app_token() -> None:
    """Least privilege: commenting triggers nothing, so issue-write stays off the
    contents-write App token. Preserved verbatim through the extraction."""
    action = _load(COLLECT_ACTION)
    commenting = [
        s
        for s in action["runs"]["steps"]
        if "gh issue comment" in s.get("run", "") or "post-agent-feedback" in s.get("run", "")
    ]
    assert len(commenting) == 3, "expected the stall, secret-scan, and feedback-latch steps"
    for step in commenting:
        assert step["env"]["GH_TOKEN"] == "${{ inputs.github-token }}"
