"""The label trigger is the pipeline's trust boundary (see SECURITY.md -> *Label
triggers*). Every `run:*` workflow must refuse a non-write actor *before* it does
any privileged work (mint a token, assume the S3 role, read the corpus, run an
agent). These tests lock that invariant in so a future edit cannot quietly drop a
guard; the action linters check syntax, but only this checks the security shape.
"""

from pathlib import Path
from typing import Any

import yaml

from tests.test_workflow_agent_bot import PIPELINE_BOT

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"

# Each privileged label trigger and the job that carries (or gates) its work.
# For the fan-out agents the entry point is the `plan` job, which the privileged
# matrix job `needs:`; for the rest the entry job is the privileged job itself.
RUN_LABELS = {
    "run-pull.yml": ("run:pull", "pull"),
    "run-predict.yml": ("run:predict", "plan"),
    "run-evaluate.yml": ("run:evaluate", "plan"),
    "run-backtest.yml": ("run:backtest", "backtest"),
}

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


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return job.get("steps", []) or []


def _is_authorize_step(step: dict[str, Any]) -> bool:
    """The fail-closed actor gate: the tested ``authorize-trigger`` command.

    Every gated workflow — the fan-outs (predict/evaluate/backtest) and the
    deterministic writer (pull) — delegates the decision to the one
    unit-tested command (``test_authz.py``), which also carries the bounded
    permission lookup. An inline collaborators-API check is deliberately NOT
    recognized: the decision logic must live in exactly one tested place, so a
    workflow that reintroduces an inline copy fails this test rather than
    quietly forking the gate. The security *shape* (a gate before any
    privileged step) is what this file locks in.
    """
    name = step.get("name", "")
    run = step.get("run", "")
    if "Authorize the trigger" not in name:
        return False
    return "fedcourts authorize-trigger" in run


def test_every_run_label_workflow_triggers_on_issue_label() -> None:
    for name in RUN_LABELS:
        wf = _load(name)
        # `on` parses to the truthy bool key in YAML; tolerate either spelling.
        on = wf.get("on") or wf.get(True)
        assert isinstance(on, dict), f"{name} has no `on:` block"
        assert "issues" in on, f"{name} must trigger on issues events"
        assert "labeled" in on["issues"]["types"], f"{name} must trigger on labeled"


def test_entry_job_authorizes_before_any_privileged_step() -> None:
    for name, (label, entry_job) in RUN_LABELS.items():
        wf = _load(name)
        job = wf["jobs"][entry_job]
        # The entry job is gated on the label name so it only runs for this trigger.
        assert label in str(job.get("if", "")), f"{name}:{entry_job} must gate on {label}"

        steps = _steps(job)
        assert steps, f"{name}:{entry_job} has no steps"
        # The gate must run before any privileged step, so refusal happens before a
        # token is minted, the S3 role assumed, or an agent run. The command-based
        # gate needs a checkout + Python env ahead of it, so the invariant is not
        # "the gate is first" — but what may precede it is an ALLOWLIST, not merely
        # "nothing matching PRIVILEGED_USES": a credential-free checkout and the
        # env sync, and nothing else. A pre-gate `run:` step, or a checkout that
        # drops `persist-credentials: false`, fails here rather than sliding past
        # a substring blocklist.
        authorize_idx = next((i for i, step in enumerate(steps) if _is_authorize_step(step)), None)
        assert authorize_idx is not None, f"{name}:{entry_job} has no fail-closed authorize step"
        for step in steps[:authorize_idx]:
            uses = step.get("uses", "")
            if uses.startswith("actions/checkout@"):
                assert step.get("with", {}).get("persist-credentials") is False, (
                    f"{name}:{entry_job} checks out with credentials before the gate"
                )
                continue
            assert uses == "./.github/actions/setup-python-env", (
                f"{name}:{entry_job} runs a non-allowlisted step before the authorize gate: "
                + (step.get("name") or uses or str(step)[:80])
            )


def test_every_gate_pins_the_bot_allowance_to_the_data_app() -> None:
    """The `Bot` fast-path is only safe pinned to the data App's own login.

    A second admin-installed App's label writes are `Bot` senders too
    (SECURITY.md -> *Label triggers*), so an unpinned gate extends the
    no-permission-lookup allowance to every installed App. Each gate passes
    ``--bot-actor`` naming the data App; this locks the flag in so a future
    edit cannot quietly widen the allowance back out.
    """
    for name, (_label, entry_job) in RUN_LABELS.items():
        wf = _load(name)
        job = wf["jobs"][entry_job]
        authorize = next((s for s in _steps(job) if _is_authorize_step(s)), None)
        assert authorize is not None, f"{name}:{entry_job} has no authorize step"
        # Whitespace-normalized so a cosmetic reflow of the run: block cannot
        # fail with a security-shaped message.
        run = " ".join(str(authorize.get("run", "")).split())
        assert f'--bot-actor "{PIPELINE_BOT}"' in run, (
            f"{name}:{entry_job} authorize step must pin --bot-actor to the data App"
        )


def _reachable_on_issue_label(job: dict[str, Any]) -> bool:
    """A job is on the label-trigger path unless its `if` pins the run to some other
    event (a job gated to `push` and so guarded by branch
    protection, not the label boundary)."""
    cond = str(job.get("if", ""))
    return not ("github.event_name ==" in cond and "'issues'" not in cond)


def test_privileged_job_is_gated_by_the_authorizing_entry_job() -> None:
    """On the issue-label path, the job that mints tokens / assumes the S3 role /
    runs the agent must be the authorizing entry job itself, or `needs:` it — never
    reachable around the gate.
    """
    for name, (_label, entry_job) in RUN_LABELS.items():
        wf = _load(name)
        for job_name, job in wf["jobs"].items():
            has_privileged = any(
                p in step.get("uses", "") for step in _steps(job) for p in PRIVILEGED_USES
            )
            if not has_privileged or not _reachable_on_issue_label(job):
                continue
            if job_name == entry_job:
                continue
            needs = job.get("needs", [])
            needs = [needs] if isinstance(needs, str) else needs
            assert entry_job in needs, (
                f"{name}:{job_name} does privileged work but does not need the "
                f"authorizing job '{entry_job}'"
            )
