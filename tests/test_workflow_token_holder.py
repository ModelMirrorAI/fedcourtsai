"""No job that runs an agent holds an App token that can write the repository.

The dev App's installation token carries the App's bypass of `main`'s approval
rule: with contents write it can merge a green PR into `main` that no human
approved. A job that runs a coding agent cannot hold that token safely, however
late it mints it. The agent reads untrusted docket text, and a process it
leaves behind lives until the job ends, as the same user as every later step.
So it can read a later step's environment out of `/proc`: the minted token, or
the App's private key while the mint step runs. Minting after the agent
finishes is therefore no fence. Only a separate job is, on a fresh runner that
takes the agent's output as an artifact (the `publish` job in run-backtest,
`qp-topic-publish` in run-analytics, the `collect` jobs of the cell lanes).

Two rules hold for every job in every workflow, a local composite counting as
the steps it runs:

- a job that runs an agent mints no App token that can write contents, at any
  point in the job. A mint with no `permission-*` input takes every permission
  the installation holds, so it counts as a write mint.
- such a job names no App private key at or after its first agent step, nor
  in its job-level env, so no later mint, of any scope, runs beside a process
  the agent left.

"Runs an agent" means a step that hands control to an engine: the
claude-code and codex actions, the codex user setup that precedes a codex
cell, or the `engine-cli` composite, which installs the pinned engine CLI that
a shell step or the replay runner then invokes. The composite is the one
place an engine CLI is installed from (`tests/test_workflow_engine_pins.py`),
so the install step marks every job that can run one.
"""

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

# The private key every App mint is fed, however the App is named.
PRIVATE_KEY_MARKER = "_APP_PRIVATE_KEY"

# Jobs the agent detector must see. If a rename or a new way of launching an
# engine hid one of them, the rules above would pass for want of an agent job.
KNOWN_AGENT_JOBS = {
    ("run-backtest.yml", "backtest"),
    ("run-analytics.yml", "qp-topic-label"),
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


def _runs_agent(step: dict[Any, Any], seen: frozenset[str] = frozenset()) -> bool:
    uses = str(step.get("uses") or "")
    if any(marker in uses for marker in AGENT_USES):
        return True
    if uses in seen:
        return False
    return any(_runs_agent(inner, seen | {uses}) for inner in _composite_steps(uses))


def _mints_write_token(step: dict[Any, Any], seen: frozenset[str] = frozenset()) -> bool:
    uses = str(step.get("uses") or "")
    if MINT in uses:
        inputs = step.get("with") or {}
        scoped = {k: str(v).strip() for k, v in inputs.items() if str(k).startswith("permission-")}
        # Unscoped is the installation's full grant, contents write included.
        return not scoped or scoped.get("permission-contents") == "write"
    if uses in seen:
        return False
    return any(_mints_write_token(inner, seen | {uses}) for inner in _composite_steps(uses))


def _names_private_key(node: object) -> bool:
    return PRIVATE_KEY_MARKER in yaml.safe_dump(node)


def violations(job: dict[Any, Any]) -> list[str]:
    """Why ``job`` breaks the token-holder rules; empty when it keeps them."""
    steps = _steps(job)
    agent_at = [i for i, step in enumerate(steps) if _runs_agent(step)]
    if not agent_at:
        return []
    found = []
    for step in steps:
        if _mints_write_token(step):
            found.append(f"mints a contents-write App token in step {step.get('name')!r}")
    for step in steps[agent_at[0] :]:
        if _names_private_key(step):
            found.append(
                f"names an App private key in step {step.get('name')!r}, at or after the "
                + "first agent step"
            )
    if _names_private_key(job.get("env") or {}):
        found.append("names an App private key in its job-level env")
    return found


def _jobs() -> list[tuple[str, str, dict[Any, Any]]]:
    return [
        (path.name, job_name, job)
        for path in sorted(WORKFLOWS.glob("*.y*ml"))
        for job_name, job in (_load(path).get("jobs") or {}).items()
        if isinstance(job, dict)
    ]


def _agent_jobs() -> set[tuple[str, str]]:
    return {(wf, name) for wf, name, job in _jobs() if any(map(_runs_agent, _steps(job)))}


def test_no_job_that_runs_an_agent_holds_a_write_app_token() -> None:
    broken = {f"{wf}:{name}": found for wf, name, job in _jobs() if (found := violations(job))}
    assert not broken, (
        "a job that runs an agent can reach an App token that writes the repository; "
        + "open the PR from a separate job that takes the agent's output as an "
        + f"artifact: {broken}"
    )


def test_the_detector_sees_the_agent_jobs() -> None:
    missing = KNOWN_AGENT_JOBS - _agent_jobs()
    assert not missing, f"no agent step detected in {sorted(missing)}"


def test_the_token_holders_mint_write_tokens_and_run_no_agent() -> None:
    jobs = {(wf, name): job for wf, name, job in _jobs()}
    for key in sorted(KNOWN_TOKEN_HOLDERS):
        job = jobs.get(key)
        assert job is not None, f"{key} is gone; the lane's PR has no token holder"
        steps = _steps(job)
        assert any(map(_mints_write_token, steps)), f"{key} no longer mints the PR token"
        assert not any(map(_runs_agent, steps)), f"{key} runs an agent beside its token"
        # The agent's output arrives as data, never as a job output that a
        # later `run:` could interpolate.
        assert any("download-artifact" in str(s.get("uses") or "") for s in steps), key


def test_the_rules_refuse_a_mint_beside_an_agent() -> None:
    """The shape the rules exist for, on a synthetic job, so a change to the
    detector that stopped seeing it fails here rather than passing everywhere."""
    agent = {"name": "Install", "uses": "./.github/actions/engine-cli"}
    credentials = {
        "client-id": "${{ vars.DEV_APP_CLIENT_ID }}",
        "private-key": "${{ secrets.DEV_APP_PRIVATE_KEY }}",
    }

    def mint(**permissions: str) -> dict[str, Any]:
        return {
            "name": "Mint app token",
            "uses": f"{MINT}@0000000000000000000000000000000000000000",
            "with": {**credentials, **permissions},
        }

    late_mint = mint(**{"permission-contents": "write", "permission-pull-requests": "write"})
    assert violations({"steps": [agent, late_mint]})

    # Read-scoped and minted before the agent, as the claude cells' comment
    # token is, it is allowed.
    early_read = mint(**{"permission-contents": "read", "permission-pull-requests": "write"})
    assert violations({"steps": [early_read, agent]}) == []
    # The same read-scoped mint after the agent puts the private key beside it.
    assert violations({"steps": [agent, early_read]})
    # Unscoped is the installation's full grant.
    assert violations({"steps": [mint(), agent]})
    # A job that runs no agent may hold the token.
    assert violations({"steps": [late_mint]}) == []
