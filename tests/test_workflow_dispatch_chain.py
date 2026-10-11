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
    ("run-pull.yml", "chain-predict"): {"permission-actions": "write"},
    ("run-predict.yml", "chain"): {
        "permission-actions": "write",
        "permission-pull-requests": "read",
    },
}
# The one dispatch either job may send.
DISPATCH = re.compile(r"\bgh workflow run run-predict\.yml --repo \"\$REPO\" --ref main\s*$")


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
        assert job["permissions"] == {}
        # Gated on the repository-level switch, and never on a trigger or input.
        assert "vars.DISPATCH_CHAIN_ENABLED == 'true'" in job["if"]
        assert "inputs." not in job["if"]
        mints = [s for s in _steps(job) if "create-github-app-token" in s.get("uses", "")]
        assert len(mints) == 1
        grants = {k: v for k, v in mints[0]["with"].items() if k.startswith("permission-")}
        assert grants == ALLOWED_GRANTS[(workflow, job_name)]
        for step in _steps(job):
            assert "uses" in step or "run" in step
            if "uses" in step:
                assert "create-github-app-token" in step["uses"], (
                    f"{workflow}:{job_name} runs an action beside the token mint"
                )


def test_each_chain_job_dispatches_only_run_predict_on_main() -> None:
    for workflow, job_name in MINTERS:
        job = _load(WORKFLOWS / workflow)["jobs"][job_name]
        runs = "\n".join(str(s.get("run", "")) for s in _steps(job))
        dispatches = [line for line in runs.splitlines() if "gh workflow run" in line]
        assert dispatches, f"{workflow}:{job_name} dispatches nothing"
        for line in dispatches:
            assert DISPATCH.search(line), f"{workflow}:{job_name} dispatches {line.strip()!r}"
        assert "gh api -X" not in runs and "--method" not in runs, (
            f"{workflow}:{job_name} makes a writing API call beside the dispatch"
        )
