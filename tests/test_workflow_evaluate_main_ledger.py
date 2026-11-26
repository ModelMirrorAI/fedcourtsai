"""run-evaluate's listing of what `main` gained, pinned at the workflow shape.

A run checks out the commit it was created at, and the serializing group
starts a queued round the moment the round ahead of it ends, so a round that
waited plans on a ledger from before that round's gradings merged. The plan job
lists the files `main` holds and its checkout lacks, and the tested
`evaluate-matrix` command withholds the cells that listing names a grading for.

These pins hold the wiring no Python test can see: that the listing exists,
runs before the matrix step, reaches both the matrix and the plan report by
filename, degrades open rather than failing the job, and asks for no privilege
the plan job did not already hold.
"""

from pathlib import Path
from typing import Any

import yaml

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "run-evaluate.yml"

LISTING = "main-gained.txt"


def _plan_job() -> dict[str, Any]:
    data = yaml.safe_load(WORKFLOW.read_text())
    assert isinstance(data, dict)
    job = data["jobs"]["plan"]
    assert isinstance(job, dict)
    return job


def _steps() -> list[dict[str, Any]]:
    return list(_plan_job()["steps"])


def _step(name_prefix: str) -> dict[str, Any]:
    return next(s for s in _steps() if str(s.get("name", "")).startswith(name_prefix))


def _joined(step: dict[str, Any]) -> str:
    """A step's shell with continuations joined, so a re-wrap cannot split a flag
    off its command."""
    return str(step.get("run", "")).replace("\\\n", " ")


def test_the_listing_runs_before_the_matrix_and_feeds_it() -> None:
    """A listing the matrix step does not read is decoration. Pin the thread:
    same filename out of the listing step and into `evaluate-matrix`."""
    names = [str(s.get("name", "")) for s in _steps()]
    listing_idx = next(i for i, n in enumerate(names) if n.startswith("List the files main gained"))
    matrix_idx = next(i for i, n in enumerate(names) if n.startswith("Build evaluator x case"))
    assert listing_idx < matrix_idx
    assert f"mv main-gained.partial {LISTING}" in _joined(_step("List the files main gained"))
    assert f"--graded-on-main-file {LISTING}" in _joined(_step("Build evaluator x case"))


def test_the_plan_report_prices_the_fan_out_the_matrix_step_minted() -> None:
    """The hold decision refuses a matrix that is not the plan's cells, so the
    report must be handed the same listing. It rides in the argument file the
    matrix step writes and the report step reads back."""
    matrix = _joined(_step("Build evaluator x case"))
    assert "args=(--graded-on-main-file" in matrix
    assert "printf '%s\\n' \"${args[@]}\" > plan-args.txt" in matrix
    report = _joined(_step("Report the plan for approval"))
    assert "mapfile -t args < plan-args.txt" in report
    assert 'evaluate-plan --run-id "$PLAN_RUN_ID" "${args[@]}"' in " ".join(report.split())


def test_the_listing_compares_the_checkout_with_main_by_path_alone() -> None:
    """Tree to tree, additions only, names only: nothing `main` holds is checked
    out into the plan job's tree, and a record whose shape moved under a
    promotion cannot break a round created before it."""
    body = _joined(_step("List the files main gained"))
    # Bounded inside the conditional, so a hung fetch degrades like a failed one.
    assert "if timeout 120 git fetch --no-tags --quiet --depth=1 origin main" in body
    assert "git diff --no-renames --name-only --diff-filter=A HEAD FETCH_HEAD -- data/cases" in body
    assert "git checkout" not in body
    assert "git merge" not in body


def test_a_listing_that_could_not_be_made_leaves_no_file_and_does_not_fail() -> None:
    """Fail-open. The file's absence is what switches the check off, so the
    failure branch removes the partial listing, warns, and lets the round plan;
    a half-written listing must never be read as the whole answer."""
    body = _joined(_step("List the files main gained"))
    assert f"rm -f {LISTING}" in body
    assert "else" in body
    failure = body[body.index("else") :]
    assert "rm -f main-gained.partial" in failure
    assert "::warning::" in failure
    assert "exit 1" not in body
    # Present only where the listing answered.
    assert f"[ -f {LISTING} ]" in _joined(_step("Build evaluator x case"))


def test_the_listing_takes_no_token_no_expression_and_no_new_permission() -> None:
    """The fetch is anonymous and the shell interpolates nothing, so the step
    adds no privilege to the plan job."""
    step = _step("List the files main gained")
    assert "env" not in step
    assert "${{" not in str(step["run"])
    assert _plan_job()["permissions"] == {
        "contents": "read",
        "id-token": "write",
        "deployments": "read",
        "actions": "read",
    }


def test_a_pilot_round_skips_the_listing() -> None:
    """A pilot re-grades graded events by design and commits nothing."""
    condition = str(_step("List the files main gained")["if"])
    assert "reasoning-pilot" in condition
    assert condition.replace(" ", "").startswith("${{!(")
