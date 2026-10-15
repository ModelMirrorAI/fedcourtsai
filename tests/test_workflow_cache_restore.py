"""Only a job holding nothing worth taking may restore the uv cache.

The cache is repository-wide: any job can save an entry under a key nothing has
claimed yet, and any later job restoring that key runs whatever it holds. A job
that parses third-party content — an order list, a filing PDF — runs code paths
nobody wrote the input for, so its own save is off (`save-cache: "false"`), but
that closes only the save its own action makes; a hostile parse holding the
job's runtime token can still write an entry directly. Only the restore side
closes the path, so every job turns the uv cache off (`restore-cache: "false"`
on `setup-python-env`) and installs from the index as the lockfile pins, unless
this file allows it to restore.

The allow-list is short and pinned, rather than the opt-out list, because a job
can be worth poisoning for reasons the YAML does not show: `ci.yml`'s jobs hold
no credential, but their verdicts are required checks — the path jail that
gates every data PR's auto-merge to `main` among them — and a poisoned cache
could forge a passing one. So a new job must opt out until someone adds it here
with the reason it is safe, and each allowed job is also checked to hold no
credential or secret: no App token with a `write` permission, no AWS role but a
read-only one, no `write` grant on its own token (its own `permissions:`, or
the workflow's when it sets none) beyond `id-token` for a role this file can
read, no secret but the runtime `GITHUB_TOKEN` (in its steps, its env or its
workflow's env, however spelled), no deployment environment (which can expose
secrets the YAML does not name), and no reusable-workflow call (whose jobs this
file cannot see).
"""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
SETUP = "./.github/actions/setup-python-env"

# The jobs allowed to restore the uv cache, each with why that is safe. A job
# here holds no credential and no secret (checked below), and its result is
# neither a required status check nor evidence a gate reads.
ALLOWED_TO_RESTORE: dict[tuple[str, str], str] = {
    ("run-repair.yml", "handoff-parse"): (
        "the parse of third-party documents itself: it holds no credential by "
        + "design, and its plan is re-validated by the writer it hands to"
    ),
    ("run-analytics.yml", "tool-usage"): (
        "a read-only report over committed retrieval logs, opening no PR and " + "feeding no check"
    ),
}

SECRET_NAME = re.compile(r"secrets\.([A-Za-z0-9_]+)")
# A secret reached any other way — by index or by dumping the whole context —
# cannot be told apart from a real one, so it always counts.
SECRET_OTHER = re.compile(r"secrets\s*\[|toJSON\(\s*secrets\b")


def _workflows() -> list[tuple[str, dict[Any, Any]]]:
    paths = sorted(WORKFLOWS.glob("*.y*ml"))
    return [(path.name, yaml.safe_load(path.read_text())) for path in paths]


def _jobs() -> list[tuple[str, str, dict[Any, Any], dict[Any, Any]]]:
    return [
        (name, job_name, job, wf)
        for name, wf in _workflows()
        for job_name, job in (wf.get("jobs") or {}).items()
    ]


def _steps(job: dict[Any, Any]) -> list[dict[Any, Any]]:
    return [step for step in job.get("steps") or [] if isinstance(step, dict)]


def _setup_steps(job: dict[Any, Any]) -> list[dict[Any, Any]]:
    return [step for step in _steps(job) if str(step.get("uses", "")) == SETUP]


def _credentialed(job: dict[Any, Any], workflow: dict[Any, Any] | None = None) -> list[str]:
    """Why ``job`` holds a credential or a secret; empty when it holds neither."""
    workflow = workflow or {}
    reasons = []
    if "uses" in job:
        reasons.append("reusable workflow call")
    if job.get("environment"):
        reasons.append(f"environment {job['environment']}")
    text = yaml.safe_dump(job) + yaml.safe_dump(workflow.get("env") or {})
    secrets = sorted({name for name in SECRET_NAME.findall(text) if name != "GITHUB_TOKEN"})
    if secrets:
        reasons.append(f"{len(secrets)} secret(s)")
    if SECRET_OTHER.search(text):
        reasons.append("secrets reached by index or toJSON")
    roles = []
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
        if role is not None:
            roles.append(str(role))
            if "READONLY" not in str(role):
                reasons.append(f"role {role}")
    # A job without its own `permissions:` inherits the workflow's.
    permissions = job["permissions"] if "permissions" in job else workflow.get("permissions")
    return reasons + _token_reasons(permissions, has_role=bool(roles))


def _token_reasons(permissions: Any, *, has_role: bool) -> list[str]:
    """Why a job's own token grant counts; ``id-token`` counts only with no role to check."""
    if permissions == "write-all":
        return ["permissions: write-all"]
    if not isinstance(permissions, dict):
        return []
    reasons = []
    writes = sorted(
        key for key, value in permissions.items() if str(value) == "write" and key != "id-token"
    )
    if writes:
        reasons.append(f"job token with {', '.join(writes)}")
    if str(permissions.get("id-token")) == "write" and not has_role:
        reasons.append("id-token: write with no role this file can read")
    return reasons


SETUP_JOBS = [
    pytest.param(workflow, name, job, wf, id=f"{workflow}:{name}")
    for workflow, name, job, wf in _jobs()
    if _setup_steps(job)
]


@pytest.mark.parametrize(("workflow", "name", "job", "wf"), SETUP_JOBS)
def test_every_job_but_the_allowed_installs_without_the_uv_cache(
    workflow: str, name: str, job: dict[Any, Any], wf: dict[Any, Any]
) -> None:
    if (workflow, name) in ALLOWED_TO_RESTORE:
        return
    held = "; ".join(_credentialed(job, wf)) or "no credential, but it is not allowed to restore"
    for step in _setup_steps(job):
        with_ = step.get("with") or {}
        assert str(with_.get("restore-cache")) == "false", (
            f"{workflow}:{name} ({held}) restores the uv cache — "
            + 'pass `restore-cache: "false"` to setup-python-env, or allow it here with a reason'
        )


@pytest.mark.parametrize(("workflow", "name"), sorted(ALLOWED_TO_RESTORE))
def test_an_allowed_job_holds_nothing_and_still_restores(workflow: str, name: str) -> None:
    found = [(job, wf) for w, n, job, wf in _jobs() if (w, n) == (workflow, name)]
    assert found, f"{workflow}:{name} is allowed to restore but no longer exists"
    job, wf = found[0]
    assert _credentialed(job, wf) == [], f"{workflow}:{name} is allowed to restore but holds one"
    setups = _setup_steps(job)
    assert setups, f"{workflow}:{name} no longer runs setup-python-env"
    assert all(str((s.get("with") or {}).get("restore-cache", "true")) == "true" for s in setups), (
        f"{workflow}:{name} opted out — drop it from the allow-list"
    )


def test_the_writers_are_seen_and_opted_out() -> None:
    # The derivation must keep seeing the jobs it exists for; an empty
    # parametrization would pass vacuously.
    names = {f"{p.values[0]}:{p.values[1]}" for p in SETUP_JOBS}
    assert {
        "run-seed.yml:seed",
        "run-pull.yml:pull",
        "run-repair.yml:votes",
        "ci.yml:paths",
        "integration-test.yml:scenario",
    } <= names


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
    ("job", "workflow", "expected"),
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
            {},
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
            {},
            "role ${{ vars.RW }}",
        ),
        (
            {"permissions": {"contents": "read", "issues": "write"}, "steps": []},
            {},
            "job token with issues",
        ),
        ({"permissions": "write-all", "steps": []}, {}, "permissions: write-all"),
        (
            {"steps": []},
            {"permissions": {"contents": "write"}},
            "job token with contents",
        ),
        (
            {"steps": [{"run": "x", "env": {"KEY": "${{ secrets.MODEL_KEY }}"}}]},
            {},
            "1 secret(s)",
        ),
        ({"env": {"KEY": "${{ secrets.MODEL_KEY }}"}, "steps": []}, {}, "1 secret(s)"),
        ({"steps": []}, {"env": {"KEY": "${{ secrets.MODEL_KEY }}"}}, "1 secret(s)"),
        (
            {"steps": [{"run": "x", "env": {"K": "${{ secrets[format('K{0}', 1)] }}"}}]},
            {},
            "secrets reached by index or toJSON",
        ),
        (
            {"steps": [{"run": "x", "env": {"ALL": "${{ toJSON(secrets) }}"}}]},
            {},
            "secrets reached by index or toJSON",
        ),
        ({"environment": "prod", "steps": []}, {}, "environment prod"),
        ({"uses": "./.github/workflows/other.yml"}, {}, "reusable workflow call"),
        (
            {"permissions": {"id-token": "write"}, "steps": []},
            {},
            "id-token: write with no role this file can read",
        ),
    ],
)
def test_each_credential_kind_is_seen(
    job: dict[Any, Any], workflow: dict[Any, Any], expected: str
) -> None:
    assert _credentialed(job, workflow) == [expected]


def test_a_job_with_its_own_permissions_does_not_inherit_the_workflows() -> None:
    job = {"permissions": {"contents": "read"}, "steps": []}
    assert _credentialed(job, {"permissions": {"contents": "write"}}) == []


def test_the_opt_out_turns_the_cache_off_and_fails_closed() -> None:
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
        # Only an explicit "true" turns either half on; any other value — a
        # typo, an empty string — leaves the cache off.
        assert with_["enable-cache"] == "${{ inputs.restore-cache == 'true' }}"
        assert with_["restore-cache"] == "${{ inputs.restore-cache == 'true' }}"
        assert with_["save-cache"] == (
            "${{ inputs.restore-cache == 'true' && inputs.save-cache == 'true' }}"
        )
        assert str(with_.get("cache-python", "false")) == "false"


# The other ways a job could restore a cache entry. `setup-python-env` is the
# one sanctioned path, and the tests above decide which jobs may turn it on;
# anything else would restore beside a credential without passing through them.
ACTIONS = ROOT / ".github" / "actions"
SETUP_UV = "astral-sh/setup-uv"
# Actions whose cache is on unless a step turns it off: `setup-go` caches by
# default, `setup-node` caches the package manager a `packageManager` field
# names, and `setup-uv` enables its cache on hosted runners. A step using one
# must name the input and set it false — `setup-uv` everywhere but inside
# `setup-python-env`, whose cache inputs follow its `restore-cache` input.
CACHE_ON_BY_DEFAULT = {
    "actions/setup-go": "cache",
    "actions/setup-node": "package-manager-cache",
    SETUP_UV: "enable-cache",
}
_FALSE = {"false", ""}


def _surfaces() -> list[tuple[str, list[dict[Any, Any]]]]:
    """Every step list in the workflows and the composites, named for the report."""
    surfaces: list[tuple[str, list[dict[Any, Any]]]] = []
    for name, wf in _workflows():
        for job_name, job in (wf.get("jobs") or {}).items():
            surfaces.append((f"{name}:{job_name}", _steps(job)))
    for path in sorted(ACTIONS.glob("*/action.y*ml")):
        action = yaml.safe_load(path.read_text())
        steps = (action.get("runs") or {}).get("steps") or []
        surfaces.append(
            (f"{path.parent.name}/action.yml", [s for s in steps if isinstance(s, dict)])
        )
    return surfaces


def _cache_mechanisms(where: str, steps: list[dict[Any, Any]]) -> list[str]:
    """Each cache a step list restores or saves outside `setup-python-env`."""
    found = []
    for step in steps:
        uses = str(step.get("uses", ""))
        action = uses.split("@", 1)[0]
        with_ = step.get("with") or {}
        if action.startswith("actions/cache"):
            found.append(f"{where} uses {action}")
            continue
        if action == "./.github/actions/setup-python-env" or (
            action == SETUP_UV and where == "setup-python-env/action.yml"
        ):
            continue
        default_on = CACHE_ON_BY_DEFAULT.get(action)
        if default_on is not None and str(with_.get(default_on, "true")).lower() not in _FALSE:
            found.append(f"{where} leaves {action}'s default-on `{default_on}` on")
        for key, value in with_.items():
            # `cach`, not `cache`: `dependency-caching` and its kin count too.
            if "cach" in str(key).lower() and str(value).lower() not in _FALSE:
                found.append(f"{where} sets {action}'s `{key}: {value}`")
    return found


def test_no_job_or_composite_restores_a_cache_outside_setup_python_env() -> None:
    """No credential-holding job restores a cache, so no other path may exist.

    The tests above hold `setup-python-env` to the allow-list; this holds every
    other cache mechanism at zero, so the property cannot erode through a
    second door: `actions/cache` in any form, any action input naming a cache
    left on, or an action whose cache is on by default — `setup-uv` among
    them, which may leave its cache to an input only inside
    `setup-python-env`, where the opt-out test pins it to `restore-cache`. It
    is what lets the corpus-check lane run PR-head code with a credential:
    entries that code saves are restored by no job that holds anything.
    """
    found = [hit for where, steps in _surfaces() for hit in _cache_mechanisms(where, steps)]
    assert not found, "a cache restored outside setup-python-env:\n" + "\n".join(found)


@pytest.mark.parametrize(
    ("step", "expected"),
    [
        ({"uses": "actions/cache@x"}, "uses actions/cache"),
        ({"uses": "actions/cache/restore@x"}, "uses actions/cache/restore"),
        ({"uses": "astral-sh/setup-uv@x"}, "default-on `enable-cache`"),
        (
            {"uses": "astral-sh/setup-uv@x", "with": {"enable-cache": "auto"}},
            "default-on `enable-cache`",
        ),
        ({"uses": "actions/setup-python@x", "with": {"cache": "pip"}}, "`cache: pip`"),
        ({"uses": "actions/setup-go@x"}, "default-on `cache`"),
        ({"uses": "actions/setup-node@x"}, "default-on `package-manager-cache`"),
        ({"uses": "ruby/setup-ruby@x", "with": {"bundler-cache": True}}, "`bundler-cache: True`"),
        (
            {"uses": "some/setup-java@x", "with": {"dependency-caching": "true"}},
            "`dependency-caching: true`",
        ),
    ],
)
def test_each_cache_mechanism_is_seen(step: dict[Any, Any], expected: str) -> None:
    found = _cache_mechanisms("w.yml:j", [step])
    assert found
    assert expected in found[0]


@pytest.mark.parametrize(
    "step",
    [
        {"uses": "actions/setup-go@x", "with": {"cache": False}},
        {"uses": "actions/setup-node@x", "with": {"package-manager-cache": "false"}},
        {"uses": "astral-sh/setup-uv@x", "with": {"enable-cache": False}},
        {"uses": "actions/setup-python@x", "with": {"python-version": "3.12"}},
        {"uses": "./.github/actions/setup-python-env", "with": {"restore-cache": "true"}},
    ],
)
def test_a_cache_turned_off_or_absent_is_not_counted(step: dict[Any, Any]) -> None:
    assert _cache_mechanisms("w.yml:j", [step]) == []


def test_no_root_package_json_lets_setup_node_cache_by_default() -> None:
    """`setup-node` turns its package-manager cache on when the repository root
    carries a `package.json` naming a `packageManager`, and a remote action that
    calls `setup-node` inside itself is out of reach of every input the sweep
    above reads. No root manifest, no automatic cache: the engine CLI pins live
    under `.github/engines/`, not at the root."""
    assert not (ROOT / "package.json").exists(), (
        "a root package.json would let a setup-node inside a remote action restore a cache"
    )
