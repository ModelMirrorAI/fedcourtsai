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
ACTIONS = WORKFLOWS.parent / "actions"

# The privileged lanes: each spends real money or writes the corpus, and each
# derives what it does from committed state rather than from anything a
# requester supplies. They are named here so a new trigger on one of them is a
# test failure, not a silent widening.
PRIVILEGED_LANES = (
    "run-predict.yml",
    "run-evaluate.yml",
    "run-pull.yml",
    "run-backtest.yml",
    "summarize.yml",
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

# The two admitted expression forms for a privileged job's environment, each
# pinned by its exact text so a change has to come back through this file; the
# AWS role trust policies pin the OIDC `sub` to the named environments, so a
# run under an auto-created one can assume nothing (docs/security.md carries
# that carve-out). This one is integration-test's: resolved from its
# `deploy-environment` input, falling back to the ref's own name.
COMPUTED_ENVIRONMENT = (
    "${{ inputs.deploy-environment != 'auto' && inputs.deploy-environment "
    "|| (github.ref_name == 'main' && 'prod' || github.ref_name) }}"
)

# The other computed form, run-analytics's: pure branch resolution with no
# input override — strictly narrower than the one above, since the dispatching
# ref alone decides and the dispatcher chooses nothing. Same fail-closed tail:
# a ref that is neither `main` nor `staging` resolves its own name, which
# names no configured environment and binds nothing.
BRANCH_RESOLVED_ENVIRONMENT = "${{ github.ref_name == 'main' && 'prod' || github.ref_name }}"

# Which workflow may carry which computed form — per-workflow, never global: a
# production lane's prod job quietly becoming branch-resolvable (its corpus
# role assumable from a staging ref) must fail this sweep, not pass under a
# form admitted for the rehearsable lanes.
COMPUTED_ENVIRONMENTS = {
    "integration-test.yml": COMPUTED_ENVIRONMENT,
    "run-analytics.yml": BRANCH_RESOLVED_ENVIRONMENT,
    "summarize.yml": BRANCH_RESOLVED_ENVIRONMENT,
}

# One environment bound by one workflow alone, each for a risk class of its
# own. `corpus-check` holds the read-only role for the lane that runs PR-head
# code after the maintainer approves it (docs/corpus-check.md): its required
# reviewer is the gate, its branch policy admits `main` alone, and the
# read-only role is the only role whose trust names it. Pinned per workflow, so
# another lane binding it — and so reaching a role behind an approval meant for
# a different question — fails the sweep below.
LANE_ENVIRONMENTS = {"corpus-check.yml": "corpus-check"}

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


def _privileged_composites() -> tuple[str, ...]:
    """The local composites that do privileged work inside the calling job.

    A composite runs in its caller's job with the job's grants, so one that
    assumes the role (`corpus-readonly`, `corpus-sidecar`, `corpus-ranged`)
    makes its caller privileged exactly as the AWS action would. Derived from
    the composites themselves, so a new one is seen without an edit here.
    """
    found = []
    for path in sorted(ACTIONS.glob("*/action.y*ml")):
        action = yaml.safe_load(path.read_text())
        steps = (action.get("runs") or {}).get("steps") or []
        if any(marker in str(step.get("uses", "")) for step in steps for marker in PRIVILEGED_USES):
            found.append(f"./.github/actions/{path.parent.name}")
    return tuple(found)


PRIVILEGED_COMPOSITES = _privileged_composites()


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
    return any(
        marker in step.get("uses", "") for step in _steps(job) for marker in PRIVILEGED_USES
    ) or any(step.get("uses", "") in PRIVILEGED_COMPOSITES for step in _steps(job))


def test_the_sweep_sees_the_composites_that_assume_the_role() -> None:
    # The derivation must keep seeing the composites it exists for; an empty
    # tuple would let every caller of them pass the sweep below vacuously.
    assert {
        "./.github/actions/corpus-readonly",
        "./.github/actions/corpus-sidecar",
        "./.github/actions/corpus-ranged",
    } <= set(PRIVILEGED_COMPOSITES)
    assert _is_privileged({"steps": [{"uses": "./.github/actions/corpus-readonly"}]})


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
    same reason as the trigger sweep above. A job is privileged when it uses a
    marker action directly or through a local composite that does, so the
    read-only corpus composites' callers are swept too. The one lane
    environment, `corpus-check`, is admitted for its own workflow only: its
    branch policy admits `main` alone, and its required reviewer is what
    stands between a planned check and the read-only role.
    """
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        for job_name, job in _jobs(_load(path.name)).items():
            if not _is_privileged(job):
                continue
            environment = job.get("environment")
            assert (
                environment in BRANCH_POLICIED_ENVIRONMENTS
                or environment == COMPUTED_ENVIRONMENTS.get(path.name)
                or environment == LANE_ENVIRONMENTS.get(path.name)
            ), (
                f"{path.name}:{job_name} mints a token, assumes the S3 role or runs an "
                f"agent under environment {environment!r} — not one whose branch policy "
                "pins which ref a dispatch may run it from"
            )


def test_a_lane_environment_is_bound_by_its_own_workflow_alone() -> None:
    """`corpus-check`'s reviewer approves one question — run this SHA's check —
    and the read-only role trusts it for that. A job elsewhere binding it would
    reach the role behind an approval given for something else."""
    bound: dict[str, set[str]] = {env: set() for env in LANE_ENVIRONMENTS.values()}
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        for job in _jobs(_load(path.name)).values():
            environment = job.get("environment")
            name = environment.get("name") if isinstance(environment, dict) else environment
            if name in bound:
                bound[str(name)].add(path.name)
    for workflow, environment in LANE_ENVIRONMENTS.items():
        assert bound[environment] == {workflow}, (
            f"`{environment}` is bound by {sorted(bound[environment])}, not {workflow} alone"
        )


# The hold's one routed form: a round whose own plan auto-released it binds the
# reviewer-less `review-auto`, every other round binds `review`.
AUTO_RELEASED_HOLD = {
    "run-predict.yml": (
        "${{ needs.plan.outputs.auto_release == 'true' && 'review-auto' || 'review' }}"
    ),
}


def test_the_agent_cells_sit_behind_the_review_hold() -> None:
    """The spend gate, which sits behind the trigger rather than in it.

    No trigger decides whether a round spends; the `review` environment's
    required reviewers do. Every job that hands control to a coding agent must
    therefore wait on the `approval` hold job, or a round would spend the moment
    its cron fired.

    The one exception is spelled exactly: a predict round its own plan job
    auto-released (`hold-decision`, within `review_hold`'s caps) binds the
    reviewer-less `review-auto` instead. Any other expression — one keyed on a
    trigger, an input, or anything but the plan's decision — fails here.
    """
    for name in AGENT_FAN_OUTS:
        wf = _load(name)
        allowed = {"review", AUTO_RELEASED_HOLD.get(name, "review")}
        assert wf["jobs"]["approval"]["environment"] in allowed, (
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


def test_the_auto_release_output_comes_only_from_the_hold_decision() -> None:
    """The routed hold above trusts `needs.plan.outputs.auto_release`, so pin
    where that value is made: the plan job's `hold` step, which runs the tested
    `fedcourts hold-decision` and writes nothing else to that output. A later
    edit that fed the output from an input, a variable or another step would
    route a round past the reviewers without the caps' say-so."""
    plan = _load("run-predict.yml")["jobs"]["plan"]
    assert plan["outputs"]["auto_release"] == "${{ steps.hold.outputs.auto_release }}"
    holds = [step for step in _steps(plan) if step.get("id") == "hold"]
    assert len(holds) == 1
    run = str(holds[0].get("run", ""))
    assert "uv run fedcourts hold-decision" in run
    assert run.count("auto_release=") == 1
    assert "auto_release=$(jq -r '.auto_release' <<<\"$decision\")" in run
    # No other step in the job writes that output.
    for step in _steps(plan):
        if step.get("id") != "hold":
            assert "auto_release=" not in str(step.get("run", ""))


def test_the_scheduled_back_test_spends_only_behind_the_review_hold() -> None:
    """The same spend gate, on the lane the sweep above cannot see.

    `run-backtest` reaches its engines through the CLI runner seam rather than
    through an action, so no `uses:` marker identifies its replay job. Its cron
    would otherwise be a schedule that spends on its own — the one thing the
    workflow's header, `metrics/README.md` and the `CertBacktest` schema all
    register it does not do. The schedule asks; the hold spends.
    """
    wf = _load("run-backtest.yml")
    jobs = _jobs(wf)
    assert jobs["approval"]["environment"] == "review", (
        "run-backtest's hold must bind the `review` environment"
    )
    # No token, no code, no grant: the job exists for the environment alone.
    assert jobs["approval"]["permissions"] == {}
    assert not any("uses" in step for step in _steps(jobs["approval"]))

    replay = jobs["backtest"]
    needs = replay.get("needs", [])
    needs = [needs] if isinstance(needs, str) else needs
    assert {"cadence", "plan", "approval"} <= set(needs), (
        "the replay job must wait on the cadence guard, the plan and the hold"
    )
    condition = " ".join(str(replay["if"]).split())
    # The dispatch path is unchanged — a dispatcher's own parameter choice is
    # the deliberate decision — and the cron path reaches the replay only
    # through a released hold.
    assert "github.event_name != 'schedule'" in condition
    assert "needs.cadence.outputs.proceed == 'true'" in condition
    assert "needs.approval.result == 'success'" in condition

    # The two environments answer different questions and neither replaces the
    # other: `prod` pins which ref may run this at all, `review` whether this
    # run may spend. Dropping `prod` would leave the job reachable from any ref.
    assert replay["environment"] == "prod"
    assert jobs["plan"]["environment"] == "prod"

    # A hold that never released still has to leave a record, or a fortnight
    # that declined to spend is indistinguishable from one that never fired.
    # Named `rejected` like the other lanes' reporters, so the class the
    # security docs describe keeps covering it.
    rejected = " ".join(str(jobs["rejected"]["if"]).split())
    assert "needs.approval.result != 'success'" in rejected
    assert jobs["rejected"]["permissions"] == {}
    assert "environment" not in jobs["rejected"]
