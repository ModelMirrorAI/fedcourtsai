"""Only the corpus writer jobs bind `corpus-write`, and every one of them does.

The production read-write role's OIDC trust names `environment:corpus-write`
alone (docs/security.md, *S3 / the private stores*). A job holding
`id-token: write` lets every step in it request a token for its environment,
and a job that runs an agent hands those steps to a model reading untrusted
docket text. So the environment the write role trusts must be bound by the
jobs that assume that role and by nothing else — above all by no agent job,
which then reaches, through `prod`, only the read-only role:

- every job that names the read-write role (`vars.AWS_ROLE_TO_ASSUME`, the
  read-only role's variable aside) binds the literal `corpus-write`;
- no other job binds it, or an expression that could resolve to it;
- no job that runs an agent binds it, by the detector
  `tests/test_workflow_token_holder.py` holds the App-credential rules with.

The environment's own controls — it exists, admits `main` alone, holds only
the names these jobs read — are the promotion gate's admin read
(`fedcourtsai.environment_checks.corpus_write_problems`); the last test here
binds that name list to what these jobs actually read.
"""

import re
from pathlib import Path
from typing import Any

import yaml

from fedcourtsai import environment_checks as ec
from tests.test_workflow_token_holder import _runs_agent, _steps

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"

ENVIRONMENT = ec.CORPUS_WRITE_ENVIRONMENT

# The read-write role's variable, dotted or indexed; `\b` keeps the read-only
# role's `AWS_ROLE_TO_ASSUME_READONLY` (and any other suffixed name) out.
READ_WRITE_ROLE = re.compile(
    r"vars\s*(\.\s*AWS_ROLE_TO_ASSUME\b|\[\s*['\"]AWS_ROLE_TO_ASSUME['\"]\s*\])"
)

# The writer jobs the detector must see. If a rename or a new spelling of the
# role hid one, the rules below would pass for want of a writer.
KNOWN_WRITER_JOBS = {
    ("run-pull.yml", "pull"),
    ("run-pull.yml", "live"),
    ("run-pull.yml", "enrich"),
    ("run-seed.yml", "seed"),
    ("run-seed.yml", "ocr-sweep"),
    ("run-repair.yml", "repair"),
    ("run-repair.yml", "applications"),
    ("run-repair.yml", "decision-record"),
    ("run-repair.yml", "opinion-record"),
}


def _load(path: Path) -> dict[Any, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict), path
    return data


def _jobs() -> list[tuple[str, str, dict[Any, Any], dict[Any, Any]]]:
    return [
        (path.name, job_name, job, workflow)
        for path in sorted(WORKFLOWS.glob("*.y*ml"))
        for workflow in [_load(path)]
        for job_name, job in (workflow.get("jobs") or {}).items()
        if isinstance(job, dict)
    ]


def _environment(job: dict[Any, Any]) -> str | None:
    environment = job.get("environment")
    if isinstance(environment, dict):
        environment = environment.get("name")
    return None if environment is None else str(environment)


def names_read_write_role(job: dict[Any, Any], workflow: dict[Any, Any]) -> bool:
    """Whether the job, or its workflow's env, which every job inherits, names the role."""
    surfaces = (job, workflow.get("env") or {})
    return any(READ_WRITE_ROLE.search(yaml.safe_dump(surface)) for surface in surfaces)


def binds_corpus_write(job: dict[Any, Any]) -> bool:
    """Whether the job's environment is, or as an expression could be, `corpus-write`."""
    environment = _environment(job)
    return environment is not None and ENVIRONMENT in environment


def violations(job: dict[Any, Any], workflow: dict[Any, Any]) -> list[str]:
    """Why ``job`` breaks the rules; empty when it keeps them."""
    found = []
    writer = names_read_write_role(job, workflow)
    if writer and _environment(job) != ENVIRONMENT:
        found.append(
            f"names the read-write role under environment {_environment(job)!r}, "
            + f"not the literal `{ENVIRONMENT}`"
        )
    if binds_corpus_write(job) and not writer:
        found.append(f"binds `{ENVIRONMENT}` without assuming the read-write role")
    if binds_corpus_write(job) and any(map(_runs_agent, _steps(job))):
        found.append(f"runs an agent under `{ENVIRONMENT}`")
    return found


def test_only_the_writer_jobs_bind_corpus_write() -> None:
    broken = {
        f"{name}:{job_name}": found
        for name, job_name, job, workflow in _jobs()
        if (found := violations(job, workflow))
    }
    assert not broken, (
        f"the `{ENVIRONMENT}` environment, which the production read-write role's "
        + "trust names, must be bound by exactly the jobs that assume that role, "
        + f"and by no agent job: {broken}"
    )


def test_the_detector_sees_the_writer_jobs() -> None:
    writers = {
        (name, job_name)
        for name, job_name, job, workflow in _jobs()
        if names_read_write_role(job, workflow)
    }
    assert writers == KNOWN_WRITER_JOBS, (
        "the jobs naming the read-write role changed; a new writer binds "
        + f"`{ENVIRONMENT}` and is added here: {sorted(writers ^ KNOWN_WRITER_JOBS)}"
    )


def test_the_rules_refuse_every_way_the_environment_leaks() -> None:
    """The shapes the rules exist for, on synthetic jobs, so a change to the
    detector that stopped seeing one fails here rather than passing everywhere."""
    role = {
        "name": "Configure AWS credentials",
        "uses": "aws-actions/configure-aws-credentials@0000000000000000000000000000000000000000",
        "with": {"role-to-assume": "${{ vars.AWS_ROLE_TO_ASSUME }}"},
    }
    readonly = {
        "uses": "./.github/actions/corpus-readonly",
        "with": {"role-to-assume": "${{ vars.AWS_ROLE_TO_ASSUME_READONLY }}"},
    }
    agent = {"name": "Install", "uses": "./.github/actions/engine-cli"}

    assert violations({"environment": ENVIRONMENT, "steps": [role]}, {}) == []
    assert violations({"environment": {"name": ENVIRONMENT}, "steps": [role]}, {}) == []
    assert violations({"environment": "prod", "steps": [readonly]}, {}) == []
    # A writer under any other environment, or a computed one.
    assert violations({"environment": "prod", "steps": [role]}, {})
    assert violations({"steps": [role]}, {})
    computed = "${{ inputs.apply && 'corpus-write' || 'prod' }}"
    assert violations({"environment": computed, "steps": [role]}, {})
    # The indexed spelling, and the role named once in the workflow's env.
    indexed = {"run": "x", "env": {"ROLE": "${{ vars['AWS_ROLE_TO_ASSUME'] }}"}}
    assert violations({"environment": "prod", "steps": [indexed]}, {})
    workflow = {"env": {"ROLE": "${{ vars.AWS_ROLE_TO_ASSUME }}"}}
    assert violations({"environment": "prod", "steps": []}, workflow)
    # A reader under `corpus-write`, directly or by expression.
    assert violations({"environment": ENVIRONMENT, "steps": [readonly]}, {})
    assert violations({"environment": computed, "steps": [readonly]}, {})
    # An agent under `corpus-write`, even beside the role.
    found = violations({"environment": ENVIRONMENT, "steps": [role, agent]}, {})
    assert found == [f"runs an agent under `{ENVIRONMENT}`"]


def test_the_gate_admits_exactly_the_names_the_writer_jobs_read() -> None:
    """The gate refuses any secret or variable in the environment outside
    `CORPUS_WRITE_SECRETS` / `CORPUS_WRITE_VARIABLES`; those are exactly what
    the jobs binding it read, so a rename in one cannot leave the other
    admitting a name nothing uses, or refusing one a writer needs."""
    secrets: set[str] = set()
    variables: set[str] = set()
    for _, _, job, workflow in _jobs():
        if not binds_corpus_write(job):
            continue
        text = yaml.safe_dump(job) + yaml.safe_dump(workflow.get("env") or {})
        secrets |= set(re.findall(r"secrets\.([A-Z0-9_]+)", text))
        variables |= set(re.findall(r"vars\.([A-Z0-9_]+)", text))
    assert secrets == set(ec.CORPUS_WRITE_SECRETS)
    assert variables == set(ec.CORPUS_WRITE_VARIABLES)
