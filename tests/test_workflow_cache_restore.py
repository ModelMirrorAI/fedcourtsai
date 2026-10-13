"""A job holding a credential or a secret never restores the uv cache.

The cache is repository-wide: any job can save an entry under a key nothing has
claimed yet, and any later job restoring that key runs whatever it holds. A job
that parses third-party content — an order list, a filing PDF — runs code paths
nobody wrote the input for, so its own save is off (`save-cache: "false"`), but
that closes only the save its own action makes; a hostile parse holding the
job's runtime token can still write an entry directly. Only the restore side
closes the path, so every job carrying a credential that can change the
repository, the corpus or another run — or a secret a poisoned entry could
exfiltrate — installs from the index under the lockfile's hashes with the cache
off entirely (`restore-cache: "false"` on `setup-python-env`).

The set is derived from the YAML rather than listed, so a new job of either kind
fails here until it opts out. A job counts if it mints an App token with any
`write` permission, assumes an AWS role that is not a read-only one, grants its
own token any `write` scope other than `id-token` (which only exchanges for a
role, and that role is checked itself), references any secret other than the
runtime `GITHUB_TOKEN` (in its own steps or env, or its workflow's env), or binds
a deployment environment — an environment can expose secrets the YAML does not
name, so any binding counts.
"""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
SETUP = "./.github/actions/setup-python-env"


SECRET = re.compile(r"secrets\.([A-Za-z0-9_]+)")


def _jobs() -> list[tuple[str, str, dict[Any, Any], dict[Any, Any]]]:
    """Every job with its workflow-level ``env``, which every job inherits."""
    jobs = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        data = yaml.safe_load(path.read_text())
        for name, job in (data.get("jobs") or {}).items():
            jobs.append((path.name, name, job, data.get("env") or {}))
    return jobs


def _steps(job: dict[Any, Any]) -> list[dict[Any, Any]]:
    return [step for step in job.get("steps") or [] if isinstance(step, dict)]


def _credentialed(job: dict[Any, Any], workflow_env: dict[Any, Any] | None = None) -> list[str]:
    """Why ``job`` holds a credential or a secret; empty when it holds neither."""
    reasons = []
    if job.get("environment"):
        reasons.append(f"environment {job['environment']}")
    secrets = sorted(
        {
            name
            for name in SECRET.findall(yaml.safe_dump(job) + yaml.safe_dump(workflow_env or {}))
            if name != "GITHUB_TOKEN"
        }
    )
    if secrets:
        reasons.append(f"{len(secrets)} secret(s)")
    for step in _steps(job):
        uses = str(step.get("uses", ""))
        with_ = step.get("with") or {}
        if "create-github-app-token" in uses:
            writes = sorted(
                key
                for key, value in with_.items()
                if key.startswith("permission-") and str(value) == "write"
            )
            if writes:
                reasons.append(f"App token with {', '.join(writes)}")
        role = with_.get("role-to-assume")
        if role is not None and "READONLY" not in str(role):
            reasons.append(f"role {role}")
    permissions = job.get("permissions")
    if permissions == "write-all":
        reasons.append("permissions: write-all")
    elif isinstance(permissions, dict):
        writes = sorted(
            key for key, value in permissions.items() if str(value) == "write" and key != "id-token"
        )
        if writes:
            reasons.append(f"job token with {', '.join(writes)}")
    return reasons


def _setup_steps(job: dict[Any, Any]) -> list[dict[Any, Any]]:
    return [step for step in _steps(job) if str(step.get("uses", "")) == SETUP]


CREDENTIALED = [
    pytest.param(workflow, name, job, env, id=f"{workflow}:{name}")
    for workflow, name, job, env in _jobs()
    if _credentialed(job, env) and _setup_steps(job)
]


def test_the_credentialed_set_is_not_empty() -> None:
    # The derivation must keep seeing the writers it exists for; an empty set
    # would pass every parametrized case below vacuously.
    names = {f"{p.values[0]}:{p.values[1]}" for p in CREDENTIALED}
    assert {
        "run-seed.yml:seed",
        "run-pull.yml:pull",
        "run-repair.yml:votes",
        "integration-test.yml:scenario",
        "summarize.yml:generate",
    } <= names


@pytest.mark.parametrize(("workflow", "name", "job", "workflow_env"), CREDENTIALED)
def test_a_credentialed_job_installs_without_the_uv_cache(
    workflow: str, name: str, job: dict[Any, Any], workflow_env: dict[Any, Any]
) -> None:
    for step in _setup_steps(job):
        with_ = step.get("with") or {}
        assert str(with_.get("restore-cache")) == "false", (
            f"{workflow}:{name} holds {'; '.join(_credentialed(job, workflow_env))} "
            + 'and restores the uv cache — pass `restore-cache: "false"` to setup-python-env'
        )


def test_a_read_only_role_and_the_runtime_token_never_count() -> None:
    job = {
        "permissions": {"contents": "read", "id-token": "write"},
        "steps": [
            {
                "uses": "aws-actions/configure-aws-credentials@x",
                "with": {"role-to-assume": "${{ vars.AWS_ROLE_TO_ASSUME_READONLY }}"},
            },
            {"run": "gh pr list", "env": {"GH_TOKEN": "${{ secrets.GITHUB_TOKEN }}"}},
        ],
    }
    assert _credentialed(job) == []


@pytest.mark.parametrize(
    ("job", "expected"),
    [
        (
            {
                "steps": [
                    {
                        "uses": "actions/create-github-app-token@x",
                        "with": {"permission-contents": "write"},
                    }
                ]
            },
            "App token with permission-contents",
        ),
        (
            {
                "steps": [
                    {
                        "uses": "./.github/actions/corpus-sidecar",
                        "with": {"role-to-assume": "${{ vars.RW }}"},
                    }
                ]
            },
            "role ${{ vars.RW }}",
        ),
        (
            {"permissions": {"contents": "read", "issues": "write"}, "steps": []},
            "job token with issues",
        ),
        ({"permissions": "write-all", "steps": []}, "permissions: write-all"),
        (
            {"steps": [{"run": "x", "env": {"KEY": "${{ secrets.MODEL_KEY }}"}}]},
            "1 secret(s)",
        ),
        ({"env": {"KEY": "${{ secrets.MODEL_KEY }}"}, "steps": []}, "1 secret(s)"),
        ({"environment": "prod", "steps": []}, "environment prod"),
    ],
)
def test_each_credential_kind_is_seen(job: dict[Any, Any], expected: str) -> None:
    assert _credentialed(job) == [expected]


def test_a_secret_in_the_workflow_env_counts_for_every_job() -> None:
    assert _credentialed({"steps": []}, {"KEY": "${{ secrets.MODEL_KEY }}"}) == ["1 secret(s)"]


def test_the_opt_out_turns_the_cache_off_entirely() -> None:
    action = yaml.safe_load(
        (ROOT / ".github" / "actions" / "setup-python-env" / "action.yml").read_text()
    )
    assert action["inputs"]["restore-cache"]["default"] == "true"
    installs = [
        step
        for step in action["runs"]["steps"]
        if "astral-sh/setup-uv" in str(step.get("uses", ""))
    ]
    assert installs, "setup-python-env no longer installs uv through setup-uv"
    for step in installs:
        with_ = step["with"]
        # Off means neither half runs: no restore of any key, and no save a
        # later job could restore.
        assert with_["enable-cache"] == "${{ inputs.restore-cache != 'false' }}"
        assert with_["restore-cache"] == "${{ inputs.restore-cache }}"
        assert "inputs.restore-cache != 'false'" in str(with_["save-cache"])
        assert str(with_.get("cache-python", "false")) == "false"
