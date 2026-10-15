"""The corpus-check lane's shape (`.github/workflows/corpus-check.yml`).

The one workflow that runs PR-head code with a corpus credential
(docs/corpus-check.md). What bounds it is structural — which job holds what,
what code each job checks out, where the command comes from — so the structure
is pinned here; the decisions the jobs route on are tested in
``test_corpus_check``. ``test_workflow_auth_gate`` pins the environment to this
workflow alone and ``test_workflow_cache_restore`` keeps every cache off.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from tests.workflow_gate import AUTHORIZE_JOB, SENTINEL_JOB, own_condition

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
NAME = "corpus-check.yml"
CHECKOUT = "actions/checkout@"
SETUP = "./.github/actions/setup-python-env"
READONLY = "./.github/actions/corpus-readonly"
PLANNED_SHA = "${{ needs.plan.outputs.sha }}"


def _load(name: str = NAME) -> dict[Any, Any]:
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    assert isinstance(data, dict)
    return data


def _triggers(wf: dict[Any, Any]) -> dict[str, Any]:
    on = wf.get("on")
    if on is None:
        on = wf.get(True)
    assert isinstance(on, dict)
    return on


def _job(name: str) -> dict[str, Any]:
    job = _load()["jobs"][name]
    assert isinstance(job, dict)
    return job


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return [step for step in job.get("steps") or [] if isinstance(step, dict)]


def _uses(step: dict[str, Any]) -> str:
    return str(step.get("uses", ""))


def _index(steps: list[dict[str, Any]], predicate: Any) -> int:
    hits = [i for i, step in enumerate(steps) if predicate(step)]
    assert len(hits) == 1, f"expected one matching step, found {len(hits)}"
    return hits[0]


def test_it_starts_only_on_the_schedule_or_an_input_less_dispatch() -> None:
    on = _triggers(_load())
    assert set(on) == {"schedule", "workflow_dispatch"}
    # No inputs: nothing a dispatcher types reaches the plan.
    assert not (on["workflow_dispatch"] or {}).get("inputs")


def test_it_polls_every_thirty_minutes_on_minutes_of_its_own() -> None:
    crons = [str(entry["cron"]) for entry in _triggers(_load())["schedule"]]
    assert len(crons) == 1
    minutes, *rest = crons[0].split()
    assert rest == ["*", "*", "*", "*"]
    first, second = (int(m) for m in minutes.split(","))
    assert second - first == 30
    taken: set[int] = set()
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        if path.name == NAME:
            continue
        for entry in _triggers(_load(path.name)).get("schedule") or []:
            taken.update(int(m) for m in str(entry["cron"]).split()[0].split(","))
    assert taken, "no other schedules to compare against"
    assert not {first, second} & taken, "a corpus-check poll shares a minute with another cron"


def test_a_zero_grant_and_one_check_at_a_time() -> None:
    wf = _load()
    assert wf["permissions"] == {}
    assert wf["concurrency"] == {"group": "corpus-check", "cancel-in-progress": False}
    # The run gate opens and closes the workflow (test_workflow_auth_gate).
    assert list(wf["jobs"]) == [AUTHORIZE_JOB, "plan", "run", "post", SENTINEL_JOB]


def test_every_job_installs_with_the_cache_off() -> None:
    for name in ("plan", "run", "post"):
        setups = [step for step in _steps(_job(name)) if _uses(step) == SETUP]
        assert len(setups) == 1, name
        assert setups[0]["with"] == {"restore-cache": "false", "save-cache": "false"}, name


def test_every_checkout_drops_its_credentials() -> None:
    for name in ("plan", "run", "post"):
        for step in _steps(_job(name)):
            if _uses(step).startswith(CHECKOUT):
                assert (step.get("with") or {}).get("persist-credentials") is False, name


def test_the_plan_holds_no_credential_and_runs_only_on_main() -> None:
    plan = _job("plan")
    assert plan["permissions"] == {
        "contents": "read",
        "pull-requests": "read",
        "actions": "read",
    }
    assert "environment" not in plan
    assert own_condition(plan) == "github.ref == 'refs/heads/main'"
    assert plan["needs"] == [AUTHORIZE_JOB]
    # Its own checkout of the run's ref, where config/corpus-check.yaml is read.
    for step in _steps(plan):
        if _uses(step).startswith(CHECKOUT):
            assert set(step["with"]) == {"persist-credentials"}
    run = "\n".join(str(step.get("run", "")) for step in _steps(plan))
    assert "fedcourts corpus-check-candidates" in run
    assert "fedcourts corpus-check-plan" in run
    assert run.count("--paginate --slurp") == 2
    # The environment's protection is read and handed to the plan, which plans
    # nothing without it.
    assert 'gh api "repos/${REPO}/environments/corpus-check"' in run
    assert "/deployment-branch-policies" in run
    assert '--environment-file "${work}/environment.json"' in run
    assert '--branch-policies-file "${work}/branch-policies.json"' in run
    assert 'gh api "repos/${REPO}/commits/${sha}"' in run


def test_an_empty_poll_stops_before_the_install() -> None:
    steps = _steps(_job("plan"))
    peek = _index(steps, lambda step: step.get("id") == "peek")
    setup = _index(steps, lambda step: _uses(step) == SETUP)
    pick = _index(steps, lambda step: step.get("id") == "plan")
    assert peek < setup < pick
    gate = "${{ steps.peek.outputs.any == 'true' }}"
    assert steps[setup]["if"] == gate
    assert steps[pick]["if"] == gate
    # A superset of the CLI's block test: any body naming the info string.
    assert 'contains("corpus-check")' in str(steps[peek]["run"])
    # The plan's outputs come from the picking step alone.
    plan = _job("plan")
    assert set(plan["outputs"]) == {"found", "pr", "sha", "command", "refusal"}
    for key, value in plan["outputs"].items():
        assert value == f"${{{{ steps.plan.outputs.{key} }}}}"


def test_the_run_job_holds_the_environment_and_the_read_only_role_alone() -> None:
    run = _job("run")
    assert run["environment"] == "corpus-check"
    assert run["permissions"] == {"contents": "read", "id-token": "write"}
    assert run["needs"] == [AUTHORIZE_JOB, "plan"]
    condition = own_condition(run)
    assert "needs.plan.outputs.found == 'true'" in condition
    assert "needs.plan.outputs.refusal == ''" in condition
    readonly = [step for step in _steps(run) if _uses(step) == READONLY]
    assert len(readonly) == 1
    # Production through `main`'s committed pointer: no staging selector.
    assert readonly[0]["with"] == {
        "role-to-assume": "${{ vars.AWS_ROLE_TO_ASSUME_READONLY }}",
        "aws-region": "${{ vars.AWS_REGION }}",
        "corpus-base-url": "${{ vars.CORPUS_BASE_URL }}",
    }


def test_only_the_run_job_reads_variables_and_no_job_reads_a_secret() -> None:
    text = (WORKFLOWS / NAME).read_text()
    assert "secrets." not in text
    assert "secrets[" not in text
    allowed = {"AWS_ROLE_TO_ASSUME_READONLY", "AWS_REGION", "CORPUS_BASE_URL"}
    for name in ("plan", "post"):
        assert "vars." not in yaml.safe_dump(_job(name)), name
    assert set(re.findall(r"vars\.([A-Za-z0-9_]+)", yaml.safe_dump(_job("run")))) == allowed


def test_reviewed_code_runs_first_and_the_planned_head_beside_it() -> None:
    """The composites, the pull and the vintage come from the run's own ref.

    A local composite resolves from the workspace root, so the root must hold
    the run's own checkout and the PR head must land beside it; and the
    vintage the comment quotes is read before any PR code runs.
    """
    steps = _steps(_job("run"))
    checkouts = [i for i, step in enumerate(steps) if _uses(step).startswith(CHECKOUT)]
    assert len(checkouts) == 2
    own, head = (steps[i] for i in checkouts)
    assert set(own["with"]) == {"persist-credentials"}
    assert head["with"] == {"ref": PLANNED_SHA, "path": "check", "persist-credentials": False}
    assert checkouts[0] == 0
    vintage = _index(steps, lambda step: step.get("id") == "vintage")
    local = [i for i, step in enumerate(steps) if _uses(step).startswith("./")]
    assert all(i < checkouts[1] for i in local)
    assert vintage < checkouts[1]
    # Nothing after the head's checkout is a local composite: from there on
    # the PR's code is in the workspace.
    assert "fedcourts corpus-info" in str(steps[vintage]["run"])


ACCOUNT = "corpuscheck"


def test_the_head_never_runs_as_the_runners_account() -> None:
    """No step runs the head's code as the runner: the install and the check
    both go through the wrapper, which hops to the unprivileged account."""
    steps = _steps(_job("run"))
    head = _index(steps, lambda step: _uses(step).startswith(CHECKOUT) and "path" in step["with"])
    after = steps[head + 1 :]
    assert all("working-directory" not in step for step in after)
    bodies = [str(step.get("run", "")) for step in after]
    assert not any("uv sync" in body for body in bodies)
    assert sum("fedcourts corpus-check-exec" in body for body in bodies) == 1


def test_the_account_is_provisioned_without_sudo_and_proven_separate() -> None:
    steps = _steps(_job("run"))
    provision = steps[_index(steps, lambda step: "useradd" in str(step.get("run", "")))]
    check = steps[_index(steps, lambda step: step.get("id") == "check")]
    assert provision["env"]["CHECK_USER"] == ACCOUNT
    assert check["env"]["CHECK_USER"] == ACCOUNT
    body = str(provision["run"])
    # Its own copies, owned by it, under its own closed home.
    assert 'sudo chmod 700 "$home"' in body
    assert 'sudo chown -R "${CHECK_USER}:${CHECK_USER}" "${home}/check" "${home}/corpus"' in body
    assert 'sudo chmod o-rwx "$HOME" "$RUNNER_TEMP"' in body
    # Each separation is asserted as the account, not assumed.
    for refused in (
        "refuse sudo -n true",
        "refuse sudo -n -l",
        'refuse /usr/bin/cat -- "/proc/$$/environ"',
        'refuse /usr/bin/cat -- "/proc/${worker}/environ"',
        'refuse /usr/bin/ls -- "$RUNNER_TEMP"',
        'refuse /usr/bin/ls -- "$HOME"',
        'refuse /usr/bin/ls -- "$GITHUB_WORKSPACE"',
        'refuse /usr/bin/ls -- "$runner_root"',
        'refuse /usr/bin/cat -- "$GITHUB_ENV"',
        "refuse /usr/bin/test -w /var/run/docker.sock",
        "refuse crontab /dev/null",
        "refuse at -l",
    ):
        assert refused in body
    assert 'id -nG "$CHECK_USER"' in body
    # The runner's install root is derived from the worker, or the step fails.
    assert "pgrep -o -f 'Runner.Worker'" in body
    assert "cannot derive the runner's install root" in body
    # No scheduling, before any PR code runs.
    assert "sudo tee -a /etc/cron.deny /etc/at.deny" in body
    # Less kernel surface: the AppArmor switch must take; the older one where present.
    assert "sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=1" in body
    assert "sudo sysctl -w kernel.unprivileged_userns_clone=0" in body
    # No route to either metadata endpoint, proven by a refused connection.
    for endpoint in ("169.254.169.254", "168.63.129.16"):
        assert endpoint in body
    assert '-m owner --uid-owner "$CHECK_USER"' in body
    assert "except ConnectionRefusedError" in body
    assert "require /usr/bin/python3 -I -c" in body


def test_the_command_reaches_the_check_only_through_the_tested_wrapper() -> None:
    steps = _steps(_job("run"))
    check = steps[_index(steps, lambda step: step.get("id") == "check")]
    assert check["env"]["CHECK_COMMAND"] == "${{ needs.plan.outputs.command }}"
    body = str(check["run"])
    assert "uv run fedcourts corpus-check-exec" in body
    assert '--command "$CHECK_COMMAND"' in body
    assert '--user "$CHECK_USER"' in body
    assert '--workdir "/home/${CHECK_USER}/check"' in body
    assert '--corpus-root "/home/${CHECK_USER}/corpus"' in body
    # Guard < step < job, with the install's own bound inside the step too.
    check_s = int(re.search(r"--timeout-seconds (\d+)", body).group(1))  # type: ignore[union-attr]
    install_s = int(
        re.search(r"--install-timeout-seconds (\d+)", body).group(1)  # type: ignore[union-attr]
    )
    assert check_s + install_s < check["timeout-minutes"] * 60
    assert check["timeout-minutes"] < _job("run")["timeout-minutes"]


def test_no_run_block_interpolates_an_expression() -> None:
    """Every value reaches a script through `env:`, never `${{ }}` in `run:`."""
    for name in ("plan", "run", "post"):
        for step in _steps(_job(name)):
            assert "${{" not in str(step.get("run", "")), f"{name}: {step.get('name')}"


def test_the_post_job_checks_out_no_pr_code_and_holds_no_role() -> None:
    post = _job("post")
    assert post["permissions"] == {"contents": "read", "pull-requests": "write"}
    assert "environment" not in post
    assert post["needs"] == [AUTHORIZE_JOB, "plan", "run"]
    condition = own_condition(post)
    assert condition.startswith("always() &&")
    assert "needs.plan.result == 'success'" in condition
    assert "needs.plan.outputs.found == 'true'" in condition
    for step in _steps(post):
        if _uses(step).startswith(CHECKOUT):
            assert set(step["with"]) == {"persist-credentials"}
        assert _uses(step) != READONLY
    body = "\n".join(str(step.get("run", "")) for step in _steps(post))
    assert "uv run fedcourts corpus-check-comment" in body
    assert "repos/${REPO}/issues/${PR}/comments" in body
    # The digest a reader matches the comment against.
    assert 'sha256sum "$body"' in body
    assert "Posted comment sha256" in body
    # The job's own condition holds no `||`: the run gate's guard is a
    # top-level conjunct after it (test_workflow_auth_gate pins the guard).
    assert "||" not in condition


def test_the_post_job_takes_the_sha_and_command_from_the_plan() -> None:
    env = _steps(_job("post"))[-1]["env"]
    assert env["CHECK_SHA"] == PLANNED_SHA
    assert env["CHECK_COMMAND"] == "${{ needs.plan.outputs.command }}"
    assert env["RUN_RESULT"] == "${{ needs.run.result }}"
    assert env["CHECK_PHASE"] == "${{ needs.run.outputs.phase }}"
    assert env["GH_TOKEN"] == "${{ github.token }}"


def test_the_requester_list_and_the_lane_are_maintainer_owned() -> None:
    owners = (ROOT / ".github" / "CODEOWNERS").read_text().splitlines()
    owned = {line.split()[0] for line in owners if line.strip() and not line.startswith("#")}
    assert {
        "/config/corpus-check.yaml",
        "/src/fedcourtsai/corpus_check.py",
        "/tests/test_corpus_check.py",
        "/tests/test_workflow_corpus_check.py",
        "/.github/workflows/",
    } <= owned
