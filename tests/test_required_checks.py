"""Required status checks against the jobs that can actually report them.

The failure this guards is quiet and expensive: a context added to a branch's
required-checks rule before its producing job exists on that branch leaves every
PR into it pending forever, and the auto-merging collect PRs hang first — data
production stops on a change that reads like a tightening. These lock both
directions, since the ordering only works if you can tell which step you are on.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.required_checks import (
    produced_contexts,
    ready_to_require,
    unproduced_contexts,
)

runner = CliRunner()


def _workflow(directory: Path, name: str, body: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(body)


def test_a_job_reports_under_its_id_by_default(tmp_path: Path) -> None:
    _workflow(tmp_path, "ci.yml", "on: [pull_request]\njobs:\n  gate: {runs-on: ubuntu-latest}\n")
    assert produced_contexts(tmp_path) == {"gate"}


def test_a_named_job_reports_under_its_name(tmp_path: Path) -> None:
    """GitHub keys the check context on `name` when a job sets one, so the id is
    the wrong thing to match against — requiring the id would hang."""
    _workflow(tmp_path, "ci.yml", "on: [pull_request]\njobs:\n  gate:\n    name: Full gate\n")
    assert produced_contexts(tmp_path) == {"Full gate"}
    assert unproduced_contexts(["gate"], tmp_path) == ["gate"]


def test_an_expression_name_vouches_for_nothing(tmp_path: Path) -> None:
    """A name resolved at run time reports as `smoke <rendered>`, never `smoke`.
    Falling back to the job id would bless a context GitHub never reports —
    the one error that hangs a branch, so the job contributes nothing."""
    _workflow(
        tmp_path,
        "pr.yml",
        'on: [pull_request]\njobs:\n  smoke:\n    name: "smoke ${{ inputs.x }}"\n',
    )
    assert produced_contexts(tmp_path) == set()
    assert ready_to_require(["smoke"], tmp_path) == []


def test_a_matrix_job_vouches_for_nothing(tmp_path: Path) -> None:
    """A matrix reports one context per combination (`predict (a)`, `predict
    (b)`) and never the bare name, so no spelling of it can be vouched for.
    `run-predict.yml`'s `predict` is the live case."""
    _workflow(
        tmp_path,
        "pr.yml",
        "on: [pull_request]\njobs:\n"
        "  predict:\n"
        "    strategy:\n      matrix:\n        case: [a, b]\n"
        "  gate: {runs-on: ubuntu-latest}\n",
    )
    assert produced_contexts(tmp_path) == {"gate"}
    assert ready_to_require(["predict"], tmp_path) == []


def test_a_workflow_that_no_pull_request_triggers_is_not_a_producer(tmp_path: Path) -> None:
    """A job skipped by `if:` still reports `skipped`, which satisfies a
    requirement — that is how `promotion-gate` passes on an ordinary PR. A
    workflow the trigger filters out reports nothing at all, and nothing hangs."""
    _workflow(tmp_path, "issues.yml", "on: [issues]\njobs:\n  collect: {runs-on: ubuntu-latest}\n")
    assert produced_contexts(tmp_path) == set()


def test_a_path_filtered_workflow_is_not_a_producer(tmp_path: Path) -> None:
    """`zizmor` is the live case: `lint-actions.yml` is filtered to
    `.github/**`, so requiring it would hang any PR that touches no workflow —
    which `docs/security.md` states in as many words."""
    _workflow(
        tmp_path,
        "lint.yml",
        "on:\n  pull_request:\n    paths: ['.github/**']\njobs:\n  zizmor: {}\n",
    )
    assert produced_contexts(tmp_path) == set()


def test_a_branch_filter_is_honoured_when_a_base_branch_is_given(tmp_path: Path) -> None:
    _workflow(
        tmp_path,
        "pr.yml",
        "on:\n  pull_request:\n    branches: [staging]\njobs:\n  only-staging: {}\n",
    )
    assert produced_contexts(tmp_path, "main") == set()
    assert produced_contexts(tmp_path, "staging") == {"only-staging"}
    # Without a base branch the filter cannot be evaluated, so it is not applied.
    assert produced_contexts(tmp_path) == {"only-staging"}


def test_contexts_are_gathered_across_every_workflow(tmp_path: Path) -> None:
    """A required context may be produced by any workflow on the branch, not
    only ci.yml — scoping the search to one file would report false hangs."""
    _workflow(tmp_path, "ci.yml", "on: [pull_request]\njobs:\n  gate: {runs-on: ubuntu-latest}\n")
    _workflow(
        tmp_path,
        "lint-actions.yml",
        "on: [pull_request]\njobs:\n  lint: {runs-on: ubuntu-latest}\n",
    )
    assert produced_contexts(tmp_path) == {"gate", "lint"}
    assert unproduced_contexts(["gate", "lint"], tmp_path) == []


def test_an_unreadable_workflow_contributes_nothing_rather_than_raising(tmp_path: Path) -> None:
    """Tolerant, but conservative with it: a file this cannot parse is one whose
    jobs it cannot vouch for, so the contexts go unclaimed and the check asks
    for a second look instead of blessing a rule it did not verify."""
    _workflow(tmp_path, "broken.yml", "jobs: [this is not a mapping\n")
    _workflow(tmp_path, "ci.yml", "on: [pull_request]\njobs:\n  gate: {runs-on: ubuntu-latest}\n")
    assert produced_contexts(tmp_path) == {"gate"}


def test_a_missing_directory_produces_nothing(tmp_path: Path) -> None:
    assert produced_contexts(tmp_path / "absent") == set()
    assert unproduced_contexts(["gate"], tmp_path / "absent") == ["gate"]


def test_ready_to_require_is_the_other_half_of_the_ordering(tmp_path: Path) -> None:
    """`main-base` is the live case: its definition must reach the branch before
    its name may join that branch's required contexts."""
    _workflow(tmp_path, "ci.yml", "on: [pull_request]\njobs:\n  gate: {runs-on: ubuntu-latest}\n")
    assert ready_to_require(["main-base"], tmp_path) == []
    _workflow(
        tmp_path,
        "ci.yml",
        "on: [pull_request]\njobs:\n"
        "  gate: {runs-on: ubuntu-latest}\n"
        "  main-base: {runs-on: ubuntu-latest}\n",
    )
    assert ready_to_require(["main-base"], tmp_path) == ["main-base"]


def test_the_cli_fails_naming_every_context_that_would_hang(tmp_path: Path) -> None:
    _workflow(tmp_path, "ci.yml", "on: [pull_request]\njobs:\n  gate: {runs-on: ubuntu-latest}\n")
    result = runner.invoke(
        app,
        [
            "assert-required-contexts",
            "--workflows",
            str(tmp_path),
            "--context",
            "gate",
            "--context",
            "main-base",
        ],
    )
    assert result.exit_code == 1
    assert "::error::" in result.stderr
    assert "main-base" in result.stderr
    # The satisfied context is not reported as a problem.
    assert "'gate'" not in result.stderr


def test_the_cli_reports_candidates_without_failing(tmp_path: Path) -> None:
    """A candidate is advice, not a gate: the maintainer is asking whether the
    next step is safe, and the answer must not exit non-zero either way."""
    _workflow(tmp_path, "ci.yml", "on: [pull_request]\njobs:\n  gate: {runs-on: ubuntu-latest}\n")
    result = runner.invoke(
        app,
        [
            "assert-required-contexts",
            "--workflows",
            str(tmp_path),
            "--context",
            "gate",
            "--candidate",
            "main-base",
        ],
    )
    assert result.exit_code == 0
    assert "NOT yet requireable: 'main-base'" in result.stdout


def test_main_currently_requires_only_contexts_it_can_produce() -> None:
    """The live invariant, against this branch's own workflows: nothing already
    required may lack a producer. A promotion that renamed or deleted one of
    these jobs would hang every PR into `main`, and this fails first."""
    workflows = Path(".github") / "workflows"
    assert unproduced_contexts(["gate", "paths", "promotion-gate"], workflows) == []


def test_odd_shapes_degrade_rather_than_raise(tmp_path: Path) -> None:
    """Every parse path is tolerant, because this runs against another branch's
    files: a null job body, a `jobs:` key that is not a mapping, and a non-YAML
    neighbour must each yield a usable answer instead of an exception."""
    _workflow(tmp_path, "null-job.yml", "on: [pull_request]\njobs:\n  bare:\n")
    _workflow(tmp_path, "odd-jobs.yml", "on: [pull_request]\njobs: not-a-mapping\n")
    _workflow(tmp_path, "notes.txt", "not a workflow at all\n")
    _workflow(tmp_path, "ci.yml", "on: [pull_request]\njobs:\n  gate: {runs-on: ubuntu-latest}\n")
    # A null body carries no name and no matrix, so the id is the honest answer.
    assert produced_contexts(tmp_path) == {"bare", "gate"}


def test_the_cli_reports_a_landed_candidate_as_ready(tmp_path: Path) -> None:
    _workflow(
        tmp_path,
        "ci.yml",
        "on: [pull_request]\njobs:\n"
        "  gate: {runs-on: ubuntu-latest}\n"
        "  main-base: {runs-on: ubuntu-latest}\n",
    )
    result = runner.invoke(
        app,
        [
            "assert-required-contexts",
            "--workflows",
            str(tmp_path),
            "--context",
            "gate",
            "--candidate",
            "main-base",
        ],
    )
    assert result.exit_code == 0
    assert "ready to require: 'main-base'" in result.stdout
    assert "NOT yet" not in result.stdout
