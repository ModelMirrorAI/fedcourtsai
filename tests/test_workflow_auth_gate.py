"""The trigger surface is the pipeline's trust boundary (see SECURITY.md ->
*Trigger surface*). Every workflow that does privileged work — mint an App
token, assume the S3 role, hand control to a coding agent — enters through a
trigger the platform itself gates: a `schedule`, which fires only from the
default branch and so runs only what a maintainer-merged promotion put on
`main`, or a `workflow_dispatch`, which GitHub refuses to anyone without
repository write. Nothing an outside actor can file — an issue, a label, a
comment — starts any of it.

The one outside-reachable trigger in the directory is `pull_request`, on CI, the
workflow linters and CodeQL. It stays because those jobs are the other half of
the same invariant: they bind no environment, name no secret, and mint no token
or role, so privilege and outside reachability are disjoint here rather than
merely rare together. Both halves are pinned below.

These tests lock that shape in so a future edit cannot quietly reopen a path
around it. The action linters check syntax; only this checks the security shape.
"""

from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"

# The privileged lanes: each spends real money or writes the corpus, and each
# derives what it does from committed state rather than from anything a
# requester supplies. They are named here so a new trigger on one of them is a
# test failure, not a silent widening.
PRIVILEGED_LANES = (
    "run-predict.yml",
    "run-evaluate.yml",
    "run-pull.yml",
    "run-backtest.yml",
)

# The agent fan-outs, whose cells spend model tokens behind the `review` hold.
AGENT_FAN_OUTS = ("run-predict.yml", "run-evaluate.yml")

# Trigger classes an actor outside the write-access boundary can fire. `issues`
# leads because an issue *form* applies its declared labels on creation
# regardless of the submitter's permissions; the rest are the same hole wearing
# a different event name, and a ban written against one alone would miss them.
# `workflow_run` is on the list for the opposite reason: it is not fired from
# outside directly, but it *runs in the privileged context of the default
# branch* and can be chained off a fork's `pull_request` run, which is the
# classic way an unprivileged event reaches secrets.
OUTSIDE_REACHABLE_TRIGGERS = frozenset(
    {
        "issues",
        "issue_comment",
        "pull_request_target",
        "pull_request_review",
        "pull_request_review_comment",
        "repository_dispatch",
        "workflow_run",
        "discussion",
        "discussion_comment",
        "gollum",
        "fork",
        "watch",
        "public",
    }
)

# `pull_request` is deliberately NOT on that list, and the omission is the whole
# reason the list can stay a denylist. CI, the workflow linters and CodeQL take
# it — any fork contributor fires those — and GitHub runs a fork's PR under a
# read-only token with no access to secrets or environments. What keeps that
# safe is not the trigger but the jobs behind it, so those files are held to a
# stricter shape instead: no environment, no secret, no token mint, no role.
UNPRIVILEGED_PULL_REQUEST_WORKFLOWS = ("ci.yml", "codeql.yml", "lint-actions.yml")

# The environments whose deployment-branch policy pins the ref a job may run
# from: `prod` to `main`, `staging` to the staging branch (docs/security.md).
# Binding *some* environment is not the property — GitHub auto-creates a
# referenced environment unprotected, so `environment: dev` would gate nothing —
# which is why the sweep below is a membership test rather than a truthiness one.
BRANCH_POLICIED_ENVIRONMENTS = frozenset({"prod", "staging"})

# The one privileged job whose environment is an expression rather than a
# literal: integration-test resolves it from its `deploy-environment` input,
# falling back to the ref's own name. Pinned by its exact text so a change to it
# has to come back through this file; the AWS role trust policies pin the OIDC
# `sub` to the named environments, so a run under an auto-created one can assume
# nothing (docs/security.md carries that carve-out).
COMPUTED_ENVIRONMENT = (
    "${{ inputs.deploy-environment != 'auto' && inputs.deploy-environment "
    "|| (github.ref_name == 'main' && 'prod' || github.ref_name) }}"
)

# Step markers that mean "privileged work has started": minting an App token,
# assuming the S3 role, or handing control to a coding agent.
PRIVILEGED_USES = (
    "create-github-app-token",
    "configure-aws-credentials",
    "claude-code-action",
    "codex-action",
)


def _load(name: str) -> dict[Any, Any]:
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    assert isinstance(data, dict)
    return data


def _triggers(wf: dict[Any, Any]) -> dict[str, Any]:
    # `on` parses to the truthy bool key in YAML; tolerate either spelling.
    on = wf.get("on") or wf.get(True)
    assert isinstance(on, dict), "workflow has no `on:` block"
    return on


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return job.get("steps", []) or []


def _jobs(wf: dict[Any, Any]) -> dict[str, dict[str, Any]]:
    jobs = wf.get("jobs") or {}
    assert isinstance(jobs, dict)
    return jobs


def _is_privileged(job: dict[str, Any]) -> bool:
    return any(marker in step.get("uses", "") for step in _steps(job) for marker in PRIVILEGED_USES)


def test_no_workflow_takes_a_trigger_an_outside_actor_can_reach() -> None:
    """The repository-wide invariant, swept rather than enumerated.

    A workflow added later inherits it: this reads every file in the directory,
    so a new one carrying an `issues` (or `issue_comment`, or
    `pull_request_target`) trigger fails here even though nothing else in this
    file names it. Keeping the boundary at the trigger is what lets the lanes
    below carry no actor gate of their own.
    """
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        on = _triggers(_load(path.name))
        reachable = sorted(OUTSIDE_REACHABLE_TRIGGERS & set(on))
        assert not reachable, (
            f"{path.name} declares {reachable} — a trigger an actor without repository "
            "write can fire. Every privileged lane relies on the platform gating its "
            "trigger; a workflow that needs one of these needs a fail-closed actor "
            "gate before any privileged step, and this file needs to say so"
        )


def test_the_pull_request_workflows_stay_unprivileged() -> None:
    """The other half of the denylist above: `pull_request` is allowed, so the
    jobs behind it carry the burden instead.

    A fork's PR run gets a read-only token and no environment secrets, but that
    is GitHub's guarantee about the *token*, not about what the file asks for.
    Pin the shape that makes the guarantee redundant — nothing here to leak even
    if the platform's rules moved — so a secret or an environment added to CI
    fails here rather than in a fork's run.
    """
    for name in UNPRIVILEGED_PULL_REQUEST_WORKFLOWS:
        wf = _load(name)
        assert "pull_request" in _triggers(wf), f"{name} is listed here but takes no PR trigger"
        assert wf.get("permissions") == {}, f"{name} must open with a zero top-level grant"
        for job_name, job in _jobs(wf).items():
            assert not _is_privileged(job), (
                f"{name}:{job_name} mints a token, assumes a role or runs an agent on a "
                "fork-reachable trigger"
            )
        assert "secrets." not in (WORKFLOWS / name).read_text(), (
            f"{name} names a secret on a fork-reachable trigger"
        )


def test_the_privileged_lanes_keep_only_platform_gated_triggers() -> None:
    """A subset test, not a ban on one event name.

    The lanes above spend or write, and nothing about them is judged per-actor:
    a round derives its work from committed state. So the only triggers they may
    carry are the two GitHub gates on its own — the default-branch-only cron and
    the write-gated dispatch — and `workflow_dispatch` must stay, because it is
    the manual twin that drains a backlog when a scheduled slot is missed.
    """
    for name in PRIVILEGED_LANES:
        on = _triggers(_load(name))
        assert set(on) <= {"schedule", "workflow_dispatch"}, (
            f"{name} gained a trigger beyond the platform-gated two: {sorted(on)}"
        )
        assert "workflow_dispatch" in on, (
            f"{name} must keep the on-demand dispatch its recovery path depends on"
        )


def test_every_privileged_job_binds_a_deployment_environment() -> None:
    """With no actor gate in the workflow, the environment is the ref gate.

    A `workflow_dispatch` is write-gated but not branch-gated: repository write
    lets someone dispatch from any ref, including a branch whose workflow file
    they just rewrote. What refuses that is the bound environment's deployment
    branch rule, so a privileged job that binds none would be reachable from an
    arbitrary ref by anyone with write. Swept across every workflow, for the
    same reason as the trigger sweep above.
    """
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        for job_name, job in _jobs(_load(path.name)).items():
            if not _is_privileged(job):
                continue
            environment = job.get("environment")
            assert (
                environment in BRANCH_POLICIED_ENVIRONMENTS or environment == COMPUTED_ENVIRONMENT
            ), (
                f"{path.name}:{job_name} mints a token, assumes the S3 role or runs an "
                f"agent under environment {environment!r} — not one whose branch policy "
                "pins which ref a dispatch may run it from"
            )


def test_the_agent_cells_sit_behind_the_review_hold() -> None:
    """The spend gate, which sits behind the trigger rather than in it.

    No trigger decides whether a round spends; the `review` environment's
    required reviewers do. Every job that hands control to a coding agent must
    therefore wait on the `approval` hold job, or a round would spend the moment
    its cron fired.
    """
    for name in AGENT_FAN_OUTS:
        wf = _load(name)
        assert wf["jobs"]["approval"]["environment"] == "review", (
            f"{name}'s hold must bind the `review` environment"
        )
        agent_jobs = [
            job_name
            for job_name, job in _jobs(wf).items()
            if any(
                "claude-code-action" in step.get("uses", "")
                or "codex-action" in step.get("uses", "")
                for step in _steps(job)
            )
        ]
        assert agent_jobs, f"{name} has no agent job to check"
        for job_name in agent_jobs:
            needs = wf["jobs"][job_name].get("needs", [])
            needs = [needs] if isinstance(needs, str) else needs
            assert "approval" in needs, (
                f"{name}:{job_name} runs an agent without waiting on the review hold"
            )
