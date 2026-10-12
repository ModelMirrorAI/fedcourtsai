"""The dispatch App: who may mint it, what it may hold, and what it may start.

Its token can start any workflow on any ref, so the security argument for it
(docs/security.md, *The GitHub Apps*) rests on the code that mints it rather than
on the token's scope: exactly two jobs mint it, each binds `prod` (so only
`main`'s promoted code reaches the key), holds nothing else, and starts exactly
one thing — an input-less `run-predict` on `main`. A new minter, a wider grant
or a different dispatch reopens that argument, so each is a failure here.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"

DISPATCH_KEY = "secrets.DISPATCH_APP_PRIVATE_KEY"
MINTERS = {("run-pull.yml", "chain-predict"), ("run-predict.yml", "chain")}
ALLOWED_GRANTS = {
    ("run-pull.yml", "chain-predict"): {
        "permission-actions": "write",
        "permission-pull-requests": "read",
    },
    ("run-predict.yml", "chain"): {
        "permission-actions": "write",
        "permission-pull-requests": "read",
    },
}
# The one dispatch either job may send.
DISPATCH = re.compile(r"\bgh workflow run run-predict\.yml --repo \"\$REPO\" --ref main\s*$")
# The actions a chain job may run: the checkout and env setup its tested
# `fedcourts chain-step` needs, then the token mint, in that order.
CHECKOUT = "actions/checkout@"
SETUP = "./.github/actions/setup-python-env"
MINT = "create-github-app-token"
# `gh api` flags that make a call write: an explicit method, or a field or
# input body (which turns the call into a POST without naming the method).
WRITING_FLAGS = re.compile(r"(?:^|\s)(?:-X|--method|-f|-F|--field|--raw-field|--input)(?:\s|=|$)")


def _load(path: Path) -> dict[Any, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    return data


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return list(job.get("steps", []) or [])


def test_only_the_two_chain_jobs_reference_the_dispatch_key() -> None:
    found = set()
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for job_name, job in (_load(path).get("jobs") or {}).items():
            if DISPATCH_KEY in yaml.safe_dump(job):
                found.add((path.name, job_name))
    assert found == MINTERS


def test_each_chain_job_binds_prod_and_holds_nothing_else() -> None:
    for workflow, job_name in MINTERS:
        job = _load(WORKFLOWS / workflow)["jobs"][job_name]
        assert job["environment"] == "prod"
        # The checkout's read and nothing more: everything else rides the token.
        assert job["permissions"] == {"contents": "read"}
        # Gated on the repository-level switch, and never on a trigger or input.
        assert "vars.DISPATCH_CHAIN_ENABLED == 'true'" in job["if"]
        assert "inputs." not in job["if"]
        mints = [s for s in _steps(job) if MINT in s.get("uses", "")]
        assert len(mints) == 1
        grants = {k: v for k, v in mints[0]["with"].items() if k.startswith("permission-")}
        assert grants == ALLOWED_GRANTS[(workflow, job_name)]
        uses = [step["uses"] for step in _steps(job) if "uses" in step]
        # Checkout, env setup, then the mint: the token exists only after the
        # environment is built, and no other action runs in a job that holds it.
        assert len(uses) == 3
        assert uses[0].startswith(CHECKOUT)
        assert uses[1] == SETUP
        assert MINT in uses[2]
        checkout = next(s for s in _steps(job) if s.get("uses", "").startswith(CHECKOUT))
        assert checkout["with"]["persist-credentials"] is False
        assert "ref" not in checkout["with"], "a chain job checks out the run's own ref"
        for step in _steps(job):
            assert "uses" in step or "run" in step


def test_each_chain_job_dispatches_only_run_predict_on_main() -> None:
    for workflow, job_name in MINTERS:
        job = _load(WORKFLOWS / workflow)["jobs"][job_name]
        runs = "\n".join(str(s.get("run", "")) for s in _steps(job))
        dispatches = [line for line in runs.splitlines() if "gh workflow run" in line]
        assert dispatches, f"{workflow}:{job_name} dispatches nothing"
        for line in dispatches:
            assert DISPATCH.search(line), f"{workflow}:{job_name} dispatches {line.strip()!r}"
        for line in runs.splitlines():
            if "gh api" in line:
                assert not WRITING_FLAGS.search(line), (
                    f"{workflow}:{job_name} makes a writing API call: {line.strip()!r}"
                )


def test_each_chain_job_decides_through_the_tested_command() -> None:
    expected = {("run-pull.yml", "chain-predict"): "pull", ("run-predict.yml", "chain"): "drain"}
    for (workflow, job_name), mode in expected.items():
        job = _load(WORKFLOWS / workflow)["jobs"][job_name]
        runs = "\n".join(str(s.get("run", "")) for s in _steps(job))
        assert "uv run fedcourts chain-step" in runs
        assert f"--mode {mode}" in runs
        assert "--promotion-prs-file" in runs


def test_no_workflow_hands_a_job_every_secret() -> None:
    """A job that can read every secret can read the dispatch key: refuse both
    spellings anywhere, not only in the chain jobs."""
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text()
        assert "toJSON(secrets)" not in text.replace(" ", ""), path.name
        assert not re.search(r"secrets:\s*inherit", text), path.name
