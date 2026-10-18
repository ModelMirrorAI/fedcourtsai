"""The dispatch App: who may mint it, what it may hold, and what it may start.

Its token can start any workflow on any ref, so the security argument for it
(docs/security.md, *The GitHub Apps*) rests on the code that mints it rather than
on the token's scope: exactly three jobs mint it, each binds `prod` (so only
`main`'s promoted code reaches the key), holds nothing else, and starts exactly
one thing — the two drain-chain jobs an input-less `run-predict` on `main`, the
promotion train's `dispatch-gate` the integration `gate` suite at a validated
`promote/<date>` candidate. A new minter, a wider grant or a different dispatch
reopens that argument, so each is a failure here.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"

DISPATCH_KEY = "secrets.DISPATCH_APP_PRIVATE_KEY"
CHAIN_JOBS = {("run-pull.yml", "chain-predict"), ("run-predict.yml", "chain")}
TRAIN_JOB = ("promotion-prep.yml", "dispatch-gate")
MINTERS = CHAIN_JOBS | {TRAIN_JOB}
ALLOWED_GRANTS = {
    TRAIN_JOB: {"permission-actions": "write"},
    ("run-pull.yml", "chain-predict"): {
        "permission-actions": "write",
        "permission-pull-requests": "read",
    },
    ("run-predict.yml", "chain"): {
        "permission-actions": "write",
        "permission-pull-requests": "read",
    },
}
# The one dispatch each job may send.
DISPATCH = re.compile(r"\bgh workflow run run-predict\.yml --repo \"\$REPO\" --ref main\s*$")
TRAIN_DISPATCH = re.compile(
    r"\bgh workflow run integration-test\.yml --repo \"\$REPO\" "
    + r"--ref \"\$REF\" -f scenario=\"\$SCENARIO\"\s*$"
)
DISPATCHES = {**{job: DISPATCH for job in CHAIN_JOBS}, TRAIN_JOB: TRAIN_DISPATCH}
# The actions a chain job may run: the checkout and env setup its tested
# `fedcourts chain-step` needs, then the token mint, in that order.
CHECKOUT = "actions/checkout@"
SETUP = "./.github/actions/setup-python-env"
MINT = "create-github-app-token"
# `gh api` flags that make a call write: an explicit method, or a field or
# input body (which turns the call into a POST without naming the method).
# One `gh api` command: from the call to the next shell operator or
# redirection, so a later command's own flags (`rm -f`) are not read as its.
GH_API_CALL = re.compile(r"\bgh api\b[^|;&>]*")
WRITING_FLAGS = re.compile(r"(?:^|\s)(?:-X|--method|-f|-F|--field|--raw-field|--input)(?:\s|=|$)")


def _load(path: Path) -> dict[Any, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    return data


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return list(job.get("steps", []) or [])


def test_only_the_three_minters_reference_the_dispatch_key() -> None:
    found = set()
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for job_name, job in (_load(path).get("jobs") or {}).items():
            if DISPATCH_KEY in yaml.safe_dump(job):
                found.add((path.name, job_name))
    assert found == MINTERS


def test_each_chain_job_binds_prod_and_holds_nothing_else() -> None:
    for workflow, job_name in CHAIN_JOBS:
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


def test_each_minter_dispatches_only_its_one_workflow() -> None:
    for workflow, job_name in MINTERS:
        job = _load(WORKFLOWS / workflow)["jobs"][job_name]
        # A backslash-continued command is one logical line: join it first, or a
        # flag on a continuation line escapes the per-line scans below.
        runs = re.sub(r"\\\n\s*", " ", "\n".join(str(s.get("run", "")) for s in _steps(job)))
        dispatches = [line for line in runs.splitlines() if "gh workflow run" in line]
        assert dispatches, f"{workflow}:{job_name} dispatches nothing"
        for line in dispatches:
            assert DISPATCHES[(workflow, job_name)].search(line), (
                f"{workflow}:{job_name} dispatches {line.strip()!r}"
            )
        for line in runs.splitlines():
            for call in GH_API_CALL.findall(line):
                assert not WRITING_FLAGS.search(call), (
                    f"{workflow}:{job_name} makes a writing API call: {call.strip()!r}"
                )


def test_each_chain_job_decides_through_the_tested_command() -> None:
    expected = {("run-pull.yml", "chain-predict"): "pull", ("run-predict.yml", "chain"): "drain"}
    for (workflow, job_name), mode in expected.items():
        job = _load(WORKFLOWS / workflow)["jobs"][job_name]
        runs = "\n".join(str(s.get("run", "")) for s in _steps(job))
        assert "uv run fedcourts chain-step" in runs
        assert f"--mode {mode}" in runs
        assert "--promotion-prs-file" in runs
        # A candidate counts only once approved, from its whole review list.
        assert "--promotion-reviews-file promotion-reviews.json" in runs
        assert 'gh api --paginate --slurp "repos/${REPO}/pulls/${n}/reviews?per_page=100"' in runs
        assert 'gh api --paginate --slurp "repos/${REPO}/pulls?state=open&base=main' in runs


def test_the_train_dispatch_job_holds_the_token_alone_and_checks_the_head_first() -> None:
    """The promotion train's dispatcher binds `prod`, sits behind the same
    repository switch as the chain jobs, runs no project code, and mints the
    token only after the candidate's tip is confirmed at the planned head, with
    the ambient token; the dispatch step re-reads the runs at the head, so one
    head gets one paid gate suite."""
    workflow, job_name = TRAIN_JOB
    job = _load(WORKFLOWS / workflow)["jobs"][job_name]
    assert job["environment"] == "prod"
    assert job["permissions"] == {"contents": "read"}
    assert "vars.DISPATCH_CHAIN_ENABLED == 'true'" in job["if"]
    assert "needs.plan.outputs.action == 'dispatch_gate'" in job["if"]
    steps = _steps(job)
    uses = [step["uses"] for step in steps if "uses" in step]
    assert len(uses) == 1 and MINT in uses[0], "no checkout, no project code, one mint"
    mint = next(i for i, step in enumerate(steps) if MINT in step.get("uses", ""))
    check = steps[0]
    assert mint == 1
    assert check["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert "git/ref/heads/${REF}" in check["run"]
    assert '"$tip" != "$SHA"' in check["run"]
    assert "^promote/[0-9]{4}-[0-9]{2}-[0-9]{2}" in check["run"]
    dispatch = steps[2]
    assert dispatch["env"]["GH_TOKEN"] == "${{ steps.app-token.outputs.token }}"
    run = dispatch["run"]
    assert run.index("integration-test.yml/runs?head_sha=${SHA}") < run.index("gh workflow run")
    assert '[ "$existing" != 0 ]' in run
    # Title-independent: any dispatched run at the head and ref stops it, and
    # so does a run list longer than the page read.
    assert "display_title" not in run
    assert '.event == \\"workflow_dispatch\\"' in run
    assert "if .total_count > (.workflow_runs | length) then 1" in run
    # The suite is one of the two gate suites, validated before the mint.
    assert "gate | offline-gate) ;;" in check["run"]


def test_no_workflow_hands_a_job_every_secret() -> None:
    """A job that can read every secret can read the dispatch key: refuse both
    spellings anywhere, not only in the chain jobs."""
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text()
        assert "toJSON(secrets)" not in text.replace(" ", ""), path.name
        assert not re.search(r"secrets:\s*inherit", text), path.name
