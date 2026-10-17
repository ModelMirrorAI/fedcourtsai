"""No job that runs an agent can reach an App credential.

The dev App's installation token carries the App's bypass of `main`'s approval
rule: with contents write it can merge a green PR into `main` that no human
approved. A job that runs a coding agent cannot hold that token, or the key
that mints it, safely. The agent reads untrusted docket text, and a process it
leaves behind lives until the job ends, as the same user as every later step,
so it can read a later step's environment out of `/proc`: a token minted after
the agent finished, or the App's private key while a mint runs. Ordering the
steps does not help either: every secret a job names is delivered to its
runner when the job starts, whatever a step's `if:` says, and a Claude cell
runs as the runner user with sudo, so it can recover a key the job never
used. Only a separate job is a fence: a fresh runner that takes the agent's
output as an artifact (the `publish` job in run-backtest, `qp-topic-publish`
in run-analytics, the `collect` jobs of the cell lanes).

So every job in every workflow that runs an agent, a local composite counting
as the steps it runs, keeps three rules:

- it mints no App token, of any scope;
- it names no private key anywhere: no secret whose name holds `PRIVATE_KEY`,
  in its steps, its env, or its workflow's env;
- it never hands over the secrets context whole (`toJSON(secrets)`, an
  indexed `secrets[...]`, or `secrets: inherit`), which would carry every key
  without naming one.

And since a Claude step is handed the job's own token, every agent job spells
its own `permissions:` mapping, with no write but `id-token` (for the
read-only corpus role). That `id-token: write` is itself a residual, not a
control: it lets any process in the job request an OIDC token for the job's
environment (SECURITY.md states what that reaches).

"Runs an agent" means a step that hands control to an engine: the
claude-code and codex actions, the codex user setup that precedes a codex
cell, or the `engine-cli` composite, which installs the pinned engine CLI that
a shell step or the replay runner then invokes. The composite is the one
place an engine CLI is installed from (`tests/test_workflow_engine_pins.py`),
so the install step marks every job that can run one.
"""

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
ACTIONS = ROOT / ".github" / "actions"

MINT = "actions/create-github-app-token"

# A step whose `uses:` contains one of these hands control to a coding agent.
AGENT_USES = (
    "anthropics/claude-code-action",
    "openai/codex-action",
    "google-github-actions/run-gemini-cli",
    "./.github/actions/engine-cli",
    "./.github/actions/codex-user-setup",
)

# A private key named as a secret, however the App is called or the context
# spelled: dotted, or indexed with either quote.
PRIVATE_KEY = re.compile(r"secrets\s*(\.\s*\w*PRIVATE_KEY|\[\s*['\"]\w*PRIVATE_KEY)", re.I)
# The whole secrets context, or an index this file cannot read a name from.
WHOLE_SECRETS = re.compile(r"toJSON\(\s*secrets\s*\)|secrets\s*\[\s*[^'\"\s]", re.I)

# Jobs the agent detector must see. If a rename or a new way of launching an
# engine hid one of them, the rules above would pass for want of an agent job.
KNOWN_AGENT_JOBS = {
    ("run-backtest.yml", "backtest"),
    ("run-analytics.yml", "qp-topic-label"),
    ("run-predict.yml", "predict"),
    ("run-evaluate.yml", "evaluate"),
    ("integration-test.yml", "scenario"),
    ("integration-test.yml", "qp-labeler-smoke"),
}

# The token holders that open these lanes' PRs: each mints a contents-write App
# token, so each must stay agent-free.
KNOWN_TOKEN_HOLDERS = {
    ("run-backtest.yml", "publish"),
    ("run-analytics.yml", "qp-topic-publish"),
}


def _load(path: Path) -> dict[Any, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict), path
    return data


def _steps(container: dict[Any, Any]) -> list[dict[Any, Any]]:
    return [step for step in container.get("steps") or [] if isinstance(step, dict)]


def _composite_steps(uses: str) -> list[dict[Any, Any]]:
    """The steps a local composite runs, or none for any other `uses:`."""
    if not uses.startswith("./.github/actions/"):
        return []
    name = uses.removeprefix("./.github/actions/").rstrip("/")
    for filename in ("action.yml", "action.yaml"):
        path = ACTIONS / name / filename
        if path.exists():
            return _steps(_load(path).get("runs") or {})
    return []


def _expanded(step: dict[Any, Any], seen: frozenset[str] = frozenset()) -> list[dict[Any, Any]]:
    """The step, then every step a local composite it calls runs, recursively."""
    uses = str(step.get("uses") or "")
    if uses in seen:
        return [step]
    inner = _composite_steps(uses)
    return [step, *(s for i in inner for s in _expanded(i, seen | {uses}))]


def _runs_agent(step: dict[Any, Any]) -> bool:
    return any(marker in str(s.get("uses") or "") for s in _expanded(step) for marker in AGENT_USES)


def _mints(step: dict[Any, Any]) -> bool:
    return any(MINT in str(s.get("uses") or "") for s in _expanded(step))


def _mints_write_token(step: dict[Any, Any]) -> bool:
    for s in _expanded(step):
        if MINT not in str(s.get("uses") or ""):
            continue
        inputs = s.get("with") or {}
        scoped = {k: str(v).strip() for k, v in inputs.items() if str(k).startswith("permission-")}
        contents = scoped.get("permission-contents")
        # Unscoped is the installation's full grant, and an expression is
        # whatever it evaluates to: both count as contents write.
        if not scoped or contents == "write" or (contents is not None and "${{" in contents):
            return True
    return False


def violations(job: dict[Any, Any], workflow: dict[Any, Any] | None = None) -> list[str]:
    """Why ``job`` breaks the rules; empty when it runs no agent or keeps them."""
    steps = _steps(job)
    if not any(map(_runs_agent, steps)):
        return []
    found = []
    for step in steps:
        if _mints(step):
            found.append(f"mints an App token in step {step.get('name')!r}")
    surfaces: list[tuple[str, object]] = [
        (f"step {s.get('name')!r}", s) for step in steps for s in _expanded(step)
    ]
    surfaces.append(("its job definition", {k: v for k, v in job.items() if k != "steps"}))
    if workflow is not None:
        surfaces.append(("its workflow's env", workflow.get("env") or {}))
    for where, node in surfaces:
        text = yaml.safe_dump(node)
        if PRIVATE_KEY.search(text):
            found.append(f"names a private-key secret in {where}")
        if WHOLE_SECRETS.search(text):
            found.append(f"hands over the whole secrets context in {where}")
    if str(job.get("secrets") or "").strip() == "inherit":
        found.append("inherits every secret (`secrets: inherit`)")
    return found


def _workflows() -> list[tuple[str, dict[Any, Any]]]:
    return [(path.name, _load(path)) for path in sorted(WORKFLOWS.glob("*.y*ml"))]


def _jobs() -> list[tuple[str, str, dict[Any, Any], dict[Any, Any]]]:
    return [
        (name, job_name, job, wf)
        for name, wf in _workflows()
        for job_name, job in (wf.get("jobs") or {}).items()
        if isinstance(job, dict)
    ]


def _agent_jobs() -> set[tuple[str, str]]:
    return {(wf, name) for wf, name, job, _ in _jobs() if any(map(_runs_agent, _steps(job)))}


def test_no_job_that_runs_an_agent_can_reach_an_app_credential() -> None:
    broken = {
        f"{name}:{job_name}": found
        for name, job_name, job, wf in _jobs()
        if (found := violations(job, wf))
    }
    assert not broken, (
        "a job that runs an agent can reach an App credential; give the agent the "
        + "job's own token and open any PR from a separate job that takes the "
        + f"agent's output as an artifact: {broken}"
    )


def grant_problems(job: dict[Any, Any]) -> list[str]:
    """Why an agent job's own token could write; empty when it cannot.

    The Claude step is handed the job's own token, so the job's grant is the
    token's. It must be spelled on the job itself, as a mapping: a job with no
    `permissions:` inherits the workflow's, and `write-all` / `read-all` are
    blanket grants this file cannot read scope by scope. `id-token: write` is
    the one write admitted, for the read-only corpus role.
    """
    grant = job.get("permissions")
    if not isinstance(grant, dict):
        return [f"no job-level permissions mapping (found {grant!r})"]
    return [
        f"grants {scope}: {level}"
        for scope, level in grant.items()
        if str(level).strip() not in ("read", "none") and scope != "id-token"
    ]


def test_every_agent_job_spells_a_grant_with_no_write_but_id_token() -> None:
    broken = {
        f"{name}:{job_name}": found
        for name, job_name, job, _ in _jobs()
        if any(map(_runs_agent, _steps(job))) and (found := grant_problems(job))
    }
    assert not broken, f"an agent job's own token could write: {broken}"


def test_the_grant_rule_refuses_every_widening() -> None:
    assert grant_problems({"permissions": {"contents": "read", "id-token": "write"}}) == []
    assert grant_problems({"permissions": {}}) == []
    assert grant_problems({"permissions": {"contents": "write"}})
    assert grant_problems({"permissions": {"contents": "read", "pull-requests": "write"}})
    assert grant_problems({"permissions": "write-all"})
    assert grant_problems({})


def test_the_detector_sees_the_agent_jobs() -> None:
    missing = KNOWN_AGENT_JOBS - _agent_jobs()
    assert not missing, f"no agent step detected in {sorted(missing)}"


def test_the_token_holders_mint_write_tokens_and_run_no_agent() -> None:
    jobs = {(name, job_name): job for name, job_name, job, _ in _jobs()}
    for key in sorted(KNOWN_TOKEN_HOLDERS):
        job = jobs.get(key)
        assert job is not None, f"{key} is gone; the lane's PR has no token holder"
        steps = _steps(job)
        assert any(map(_mints_write_token, steps)), f"{key} no longer mints the PR token"
        assert not any(map(_runs_agent, steps)), f"{key} runs an agent beside its token"
        # The agent's output arrives as data, never as a job output that a
        # later `run:` could interpolate.
        assert any("download-artifact" in str(s.get("uses") or "") for s in steps), key


def test_the_rules_refuse_every_way_an_agent_job_reaches_a_key() -> None:
    """The shapes the rules exist for, on synthetic jobs, so a change to the
    detector that stopped seeing one fails here rather than passing everywhere."""
    agent = {"name": "Install", "uses": "./.github/actions/engine-cli"}

    def mint(**permissions: str) -> dict[str, Any]:
        return {
            "name": "Mint app token",
            "uses": f"{MINT}@0000000000000000000000000000000000000000",
            "with": {
                "client-id": "${{ vars.DEV_APP_CLIENT_ID }}",
                "private-key": "${{ secrets.DEV_APP_PRIVATE_KEY }}",
                **permissions,
            },
        }

    # A mint of any scope, before or after the agent: the key is delivered to
    # the runner at job start either way.
    assert violations({"steps": [agent, mint(**{"permission-contents": "write"})]})
    assert violations({"steps": [mint(**{"permission-contents": "read"}), agent]})
    # A key named anywhere else in the job, or in the workflow's env.
    key_in_env = {"env": {"KEY": "${{ secrets['DATA_APP_PRIVATE_KEY'] }}"}, "steps": [agent]}
    assert violations(key_in_env)
    workflow = {"env": {"KEY": "${{ secrets.SOME_PRIVATE_KEY }}"}}
    assert violations({"steps": [agent]}, workflow)
    # The whole secrets context.
    dump = {"name": "Dump", "run": "echo", "env": {"ALL": "${{ toJSON(secrets) }}"}}
    assert violations({"steps": [agent, dump]})
    # A job that runs no agent may hold the token.
    assert violations({"steps": [mint(**{"permission-contents": "write"})]}) == []

    # A token holder's write mint is recognized however the scope is spelled.
    assert _mints_write_token(mint())
    assert _mints_write_token(mint(**{"permission-contents": "${{ inputs.scope }}"}))
    assert not _mints_write_token(mint(**{"permission-contents": "read"}))
