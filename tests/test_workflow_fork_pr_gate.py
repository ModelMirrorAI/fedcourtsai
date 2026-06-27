"""Fork `pull_request` runs must get **no** `runner` secrets (see SECURITY.md and
docs/security.md -> *Going public*). The `runner` environment's deployment branches
are restricted to `main`, so a workflow running from a fork PR (a non-`main` ref)
executes without the App keys, agent tokens, CourtListener token, or S3 role. These
tests lock the *code-side* shape of that control in place so a future edit cannot
quietly route a secret-bearing job onto the fork-PR path; the live end-to-end check
from a real fork remains a maintainer step (docs/security.md -> *Going public*).
"""

from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"


def _load(name: str) -> dict[Any, Any]:
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    assert isinstance(data, dict)
    return data


def _all_workflows() -> list[str]:
    names = sorted(p.name for p in WORKFLOWS.glob("*.yml"))
    assert names, "no workflow files found"
    return names


def _on(wf: dict[Any, Any]) -> dict[str, Any]:
    # `on` parses to the truthy bool key in YAML; tolerate either spelling.
    on = wf.get("on")
    if on is None:
        on = wf.get(True)
    assert isinstance(on, dict), "workflow has no `on:` block"
    return on


def _reachable_on_pull_request(wf: dict[Any, Any]) -> bool:
    return "pull_request" in _on(wf)


def _env_name(job: dict[Any, Any]) -> str | None:
    env = job.get("environment")
    if isinstance(env, dict):
        name = env.get("name")
        return name if isinstance(name, str) else None
    return env if isinstance(env, str) else None


def _steps(job: dict[Any, Any]) -> list[dict[str, Any]]:
    return job.get("steps", []) or []


def test_no_pull_request_target_anywhere() -> None:
    """`pull_request_target` runs with the *base* repo's secrets on the fork's head
    ref — the canonical way to leak secrets to a fork PR. It must appear in no
    workflow; the fork path is `pull_request` (secret-free) only.
    """
    for name in _all_workflows():
        assert "pull_request_target" not in _on(_load(name)), (
            f"{name} uses pull_request_target, which would expose base secrets to fork PRs"
        )


def test_runner_environment_jobs_are_unreachable_on_pull_request() -> None:
    """Any job that declares `environment: runner` can read the runner secrets only
    from a `main` ref (deployment-branch policy). Such a workflow must therefore not
    be reachable on `pull_request`, where the ref is a fork/PR ref."""
    for name in _all_workflows():
        wf = _load(name)
        runner_jobs = [j for j, job in wf["jobs"].items() if _env_name(job) == "runner"]
        if runner_jobs:
            assert not _reachable_on_pull_request(wf), (
                f"{name} triggers on pull_request yet has runner-environment job(s) "
                f"{runner_jobs}; a fork PR could reach a secret-bearing job"
            )


def test_pull_request_workflows_carry_no_secrets() -> None:
    """A workflow reachable on `pull_request` (so runnable from a fork) must not
    declare any deployment environment, reference the `secrets.` context, or leave
    the checkout's `GITHUB_TOKEN` persisted for pushes."""
    for name in _all_workflows():
        wf = _load(name)
        if not _reachable_on_pull_request(wf):
            continue

        for job_name, job in wf["jobs"].items():
            assert _env_name(job) is None, (
                f"{name}:{job_name} is on the pull_request path but declares an environment"
            )

        # The `secrets.` context yields nothing useful on a fork PR, but referencing
        # it at all means a job is shaped to consume a secret — keep the fork path clear.
        text = (WORKFLOWS / name).read_text()
        assert "secrets." not in text, (
            f"{name} is on the pull_request path but references the secrets context"
        )

        # Every checkout must opt out of persisted credentials so the default
        # GITHUB_TOKEN is not left usable for pushes from a fork-PR run.
        for job_name, job in wf["jobs"].items():
            for step in _steps(job):
                if "actions/checkout" in step.get("uses", ""):
                    persist = step.get("with", {}).get("persist-credentials")
                    assert persist is False, (
                        f"{name}:{job_name} checkout must set persist-credentials: false "
                        f"on the pull_request path (got {persist!r})"
                    )
