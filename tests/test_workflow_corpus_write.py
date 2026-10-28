"""Only the corpus writer jobs bind `corpus-write`, and every one of them does.

The production read-write role's OIDC trust is to name
`environment:corpus-write` alone, a maintainer IAM step (docs/security.md,
*S3 / the private stores*). A job holding
`id-token: write` lets every step in it request a token for its environment,
and a job that runs an agent hands those steps to a model reading untrusted
docket text. So the environment the write role trusts must be bound by the
jobs that assume that role and by nothing else — above all by no agent job,
which then reaches, through `prod`, only the read-only role:

- every job that names the read-write role (`vars.AWS_ROLE_TO_ASSUME`, the
  read-only role's variable aside) binds the literal `corpus-write`;
- no other job binds it, or an expression that names it; and an expression
  whose last alternative is the bare dispatching ref's name — which resolves
  to `corpus-write` on a branch of that name — appears only on the three
  branch-resolving workflows that need it (`REF_RESOLVED_WORKFLOWS`). That
  fall-through is not refused here because the environment's own
  `main`-only branch policy refuses a deployment from any other ref, a
  branch named `corpus-write` included, before a step runs, and the promotion
  gate checks that policy;
- no job that runs an agent binds it, by the detector
  `tests/agent_detector.py`, which the App-credential rules
  (`tests/test_workflow_token_holder.py`) share.

A job's steps are read together with the steps of every local composite
they call, so a composite that named the role would mark its caller.

The environment's own controls — it exists, admits `main` alone, holds the
names these jobs read and nothing else — are the promotion gate's admin read
(`fedcourtsai.environment_checks.corpus_write_problems`); the last test here
binds that name list to what these jobs actually read.
"""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from fedcourtsai import environment_checks as ec
from tests import agent_detector
from tests.agent_detector import expanded as _expanded
from tests.agent_detector import runs_agent as _runs_agent
from tests.agent_detector import steps as _steps

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"

ENVIRONMENT = ec.CORPUS_WRITE_ENVIRONMENT

# The read-write role's variable, dotted or indexed; `\b` keeps the read-only
# role's `AWS_ROLE_TO_ASSUME_READONLY` (and any other suffixed name) out.
READ_WRITE_ROLE = re.compile(
    r"vars\s*(\.\s*AWS_ROLE_TO_ASSUME\b|\[\s*['\"]AWS_ROLE_TO_ASSUME['\"]\s*\])"
)

# A secret or variable named in an expression, dotted or indexed.
NAMED = re.compile(r"\b(secrets|vars)\s*(?:\.\s*([A-Z0-9_]+)|\[\s*['\"]([A-Z0-9_]+)['\"]\s*\])")

# An environment expression whose last alternative is the bare ref name: a
# dispatch from a branch named `corpus-write` would resolve to that
# environment.
REF_NAME_FALLTHROUGH = re.compile(r"github\.ref_name\s*\)*\s*\}\}\s*$")

# The workflows whose environments resolve from the dispatching branch, so
# their staging dispatches are rehearsals (docs/pipeline.md). Their forms are
# pinned by text in tests/test_workflow_auth_gate.py; the fall-through to the
# ref's own name is what keeps an off-list ref fail-closed, and the
# `corpus-write` environment's branch policy is what refuses the one ref
# name that would reach it.
REF_RESOLVED_WORKFLOWS = frozenset({"integration-test.yml", "run-analytics.yml", "summarize.yml"})

# The writer jobs the detector must see. If a rename or a new spelling of the
# role hid one, the rules below would pass for want of a writer.
KNOWN_WRITER_JOBS = {
    ("run-pull.yml", "pull"),
    ("run-pull.yml", "live"),
    ("run-pull.yml", "enrich"),
    ("run-seed.yml", "seed"),
    ("run-seed.yml", "ocr-sweep"),
    ("run-seed.yml", "opinion-record"),
    ("run-repair.yml", "repair"),
    ("run-repair.yml", "applications"),
    ("run-repair.yml", "decision-record"),
    ("run-repair.yml", "opinion-record"),
}


# A writer job whose switch is not the literal "true", and the one value it may
# carry instead.
REMOTE_WRITES_VALUES = {
    ("run-repair.yml", "repair"): "${{ inputs.repair_mode == 'apply' && 'true' || '' }}",
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


def _surfaces(job: dict[Any, Any], workflow: dict[Any, Any]) -> list[object]:
    """The job, every step of a local composite it calls, and its workflow's env."""
    composites = [s for step in _steps(job) for s in _expanded(step)[1:]]
    return [job, *composites, workflow.get("env") or {}]


def names_read_write_role(job: dict[Any, Any], workflow: dict[Any, Any]) -> bool:
    """Whether the job, a composite it calls, or its workflow's env names the role."""
    return any(READ_WRITE_ROLE.search(yaml.safe_dump(s)) for s in _surfaces(job, workflow))


def falls_through_to_the_ref_name(job: dict[Any, Any]) -> bool:
    """Whether the job's environment is an expression ending in the bare ref name."""
    environment = _environment(job)
    return environment is not None and bool(REF_NAME_FALLTHROUGH.search(environment))


def binds_corpus_write(job: dict[Any, Any]) -> bool:
    """Whether the job's environment is, or as an expression could be, `corpus-write`."""
    environment = _environment(job)
    return environment is not None and ENVIRONMENT in environment


def violations(
    job: dict[Any, Any], workflow: dict[Any, Any], workflow_name: str | None = None
) -> list[str]:
    """Why ``job`` breaks the rules; empty when it keeps them."""
    found = []
    if falls_through_to_the_ref_name(job) and workflow_name not in REF_RESOLVED_WORKFLOWS:
        found.append(
            "resolves its environment to the dispatching ref's own name, which a "
            + f"branch named `{ENVIRONMENT}` would turn into that environment"
        )
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
        if (found := violations(job, workflow, name))
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


# The switch that lets a job write the remote corpus estate at all
# (`Settings.remote_writes`): the content-store mirror and `corpus-push`.
REMOTE_WRITES = "FEDCOURTS_REMOTE_WRITES"


def sets_remote_writes(job: dict[Any, Any]) -> bool:
    """Whether the job's own ``env:`` names the remote-writes switch."""
    return REMOTE_WRITES in (job.get("env") or {})


def test_exactly_the_writer_jobs_enable_remote_writes() -> None:
    """The switch is what a non-writer job's corpus writes meet before its
    role does, so it is set where permissions are reviewed: on each writer
    job's own ``env:``, by every job that assumes the read-write role and by no
    other. A job-level setting keeps it off every other job. Its value is the
    literal ``"true"``, except on run-repair's corpus job, whose dry run holds
    the read-only role and keeps its local dedupe on the runner: there it is
    one admitted expression whose only on-value is an apply."""
    enabled = {(name, job_name) for name, job_name, job, _ in _jobs() if sets_remote_writes(job)}
    assert enabled == KNOWN_WRITER_JOBS, (
        f"`{REMOTE_WRITES}` must be set by exactly the corpus writer jobs: "
        + f"{sorted(enabled ^ KNOWN_WRITER_JOBS)}"
    )
    not_literal = {
        f"{name}:{job_name}": job["env"][REMOTE_WRITES]
        for name, job_name, job, _ in _jobs()
        if sets_remote_writes(job)
        and job["env"][REMOTE_WRITES] != REMOTE_WRITES_VALUES.get((name, job_name), "true")
    }
    assert not not_literal, (
        f'`{REMOTE_WRITES}` must be the literal "true" (or the one value '
        + f"REMOTE_WRITES_VALUES admits for that job): {not_literal}"
    )


def _repair_job() -> dict[Any, Any]:
    job = _load(WORKFLOWS / "run-repair.yml")["jobs"]["repair"]
    assert isinstance(job, dict)
    return job


def _repair_step(name: str) -> dict[Any, Any]:
    (step,) = [step for step in _steps(_repair_job()) if step.get("name") == name]
    return step


def test_a_repair_dry_run_holds_the_read_only_role_and_no_write_credential() -> None:
    """A dry run is read before an apply is decided, so it holds what a read
    needs and nothing more: the read-only role, no App token, no git identity,
    and not the `corpus-write` lock a scheduled writer window queues on; nor
    does it publish a verdict over a blob nobody committed. Each read-only
    grant's condition is its read-write twin's with the mode test negated, so
    exactly one role is assumed."""
    apply = "inputs.repair_mode == 'apply'"
    for name in (
        "Mint app token",
        "Configure git identity",
        "Configure AWS credentials (corpus S3 remote, read-write)",
        "Produce + publish the corpus validation verdict",
    ):
        assert apply in _repair_step(name)["if"], name
    write = _repair_step("Configure AWS credentials (corpus S3 remote, read-write)")
    step = _repair_step("Configure AWS credentials (corpus S3 remote, read-only)")
    assert step["if"] == write["if"].replace(apply, "inputs.repair_mode != 'apply'")
    assert step["with"]["role-to-assume"] == "${{ vars.AWS_ROLE_TO_ASSUME_READONLY }}"
    group = _repair_job()["concurrency"]["group"]
    assert f"&& {apply} && 'corpus-write' ||" in group


APPLY_ONLY = 'if [ "${REPAIR_MODE}" = "apply" ]; then'


def _block_end(run: str, start: int) -> int:
    """The offset of the ``fi`` closing the shell ``if`` that opens at ``start``."""
    match = re.compile(r"^\s*fi\s*$", re.MULTILINE).search(run, start)
    assert match is not None
    return match.start()


def test_a_repair_dry_run_pushes_nothing() -> None:
    """Every step that pushes reaches its push only on an apply: the two
    prerequisites that apply locally on a dry run exit before `corpus-push`,
    and no step authenticates git until it knows the run is an apply — a dry
    run has no token to authenticate with."""
    for step in _steps(_repair_job()):
        run = str(step.get("run") or "")
        if "push_with_retry.sh" not in run and "corpus-push" not in run:
            continue
        name = step["name"]
        assert step["env"].get("REPAIR_MODE") == "${{ inputs.repair_mode }}", name
        guard = run.find('if [ "${REPAIR_MODE}" != "apply" ]')
        assert guard != -1, name
        end = _block_end(run, guard)
        assert re.search(r"^\s*exit 0\s*$", run[guard:end], re.MULTILINE), name
        assert end < run.find("uv run fedcourts corpus-push"), name
        for setup in re.finditer("gh auth setup-git", run):
            preceding = run[: setup.start()].rstrip().splitlines()[-1].strip()
            assert setup.start() > end or preceding == APPLY_ONLY, name


def test_the_switch_is_named_nowhere_but_a_writer_jobs_own_env() -> None:
    """Not in a workflow-wide ``env:``, which every job in it inherits, not in
    a container's, a service's or a step's, and not in a composite action,
    which any job could call."""
    stray = [
        f"{name}:{job_name}"
        for name, job_name, job, workflow in _jobs()
        if REMOTE_WRITES in yaml.safe_dump(workflow.get("env") or {})
        or REMOTE_WRITES in yaml.safe_dump(job.get("container") or {})
        or REMOTE_WRITES in yaml.safe_dump(job.get("services") or {})
        or any(REMOTE_WRITES in yaml.safe_dump(step) for step in _steps(job))
    ]
    stray += [
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / ".github" / "actions").rglob("*.y*ml"))
        if REMOTE_WRITES in path.read_text()
    ]
    assert not stray, f"`{REMOTE_WRITES}` named outside a writer job's own env: {stray}"


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
    # The fall-through to the ref's name, admitted only where it is pinned.
    resolved = "${{ github.ref_name == 'main' && 'prod' || github.ref_name }}"
    assert violations({"environment": resolved, "steps": [readonly]}, {})
    assert violations({"environment": resolved, "steps": [readonly]}, {}, "run-pull.yml")
    assert violations({"environment": resolved, "steps": [readonly]}, {}, "summarize.yml") == []


def test_a_composite_that_names_the_role_marks_its_caller(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:

    composite = tmp_path / "write-role"
    composite.mkdir()
    (composite / "action.yml").write_text(
        "runs:\n  using: composite\n  steps:\n"
        + "    - run: echo\n      env:\n        ROLE: ${{ vars.AWS_ROLE_TO_ASSUME }}\n"
    )
    monkeypatch.setattr(agent_detector, "ACTIONS", tmp_path)
    job = {"environment": "prod", "steps": [{"uses": "./.github/actions/write-role"}]}
    assert names_read_write_role(job, {})
    assert violations(job, {})


def test_the_ref_resolved_workflows_are_the_ones_that_fall_through() -> None:
    falling = {name for name, _, job, _ in _jobs() if falls_through_to_the_ref_name(job)}
    assert falling == REF_RESOLVED_WORKFLOWS


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
        for surface in _surfaces(job, workflow):
            for kind, dotted, indexed in NAMED.findall(yaml.safe_dump(surface)):
                (secrets if kind == "secrets" else variables).add(dotted or indexed)
    assert secrets == set(ec.CORPUS_WRITE_SECRETS)
    assert variables == set(ec.CORPUS_WRITE_VARIABLES)
