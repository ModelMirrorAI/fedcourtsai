"""The `plan` job's stranded-run guard, pinned at the workflow shape.

A predict cell spends its tokens before `collect`, the run's single durability
step, so a collect that fails after a full-width fan-out leaves every prediction
in a cell artifact and nothing in the ledger — the ledger being what the
matrix's already-predicted gate reads. Without a guard the next live cycle
re-derives the same events and re-spends the identical run.

The guard is split deliberately: a thin census step fetches and filters (the
runs and artifacts APIs), and the tested `predict-matrix` command decides. These
pins hold the wiring that no Python test can see — that the census exists, runs
before the matrix step, reaches the matrix step by filename, degrades open
rather than failing the job, and that the trigger-issue close can tell a
fully-superseded run from an out-of-scope one.
"""

from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"

CENSUS_FILE = "stranded-artifacts.json"
CLOSE_NOTE_FILE = "stranded-close.md"


def _load(name: str) -> dict[Any, Any]:
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    assert isinstance(data, dict)
    return data


def _plan_steps() -> list[dict[str, Any]]:
    return list(_load("run-predict.yml")["jobs"]["plan"]["steps"])


def _step(name_prefix: str) -> dict[str, Any]:
    return next(s for s in _plan_steps() if str(s.get("name", "")).startswith(name_prefix))


def _joined(step: dict[str, Any]) -> str:
    """A step's shell with continuations joined, so a re-wrap cannot split a flag
    off its command."""
    return str(step.get("run", "")).replace("\\\n", " ")


def test_the_plan_job_can_read_run_metadata_and_nothing_more() -> None:
    """The guard's only new privilege: repo-wide *read* of runs and artifact
    names. The plan job runs no agent code and downloads no artifact, so the
    scope buys the census and nothing else."""
    job = _load("run-predict.yml")["jobs"]["plan"]
    assert job["environment"] == "prod"
    assert job["permissions"] == {
        "contents": "read",
        # assume the AWS role for ranged corpus reads (scope gating)
        "id-token": "write",
        # close the trigger issue when the matrix is empty
        "issues": "write",
        # list recent runs and their cell artifacts for the stranded-run guard
        "actions": "read",
    }


def test_the_census_runs_before_the_matrix_and_feeds_it() -> None:
    """A census the matrix step does not read is decoration. Pin the thread:
    same filename out of the census step and into `predict-matrix`."""
    names = [str(s.get("name", "")) for s in _plan_steps()]
    census_idx = next(i for i, n in enumerate(names) if n.startswith("Census the cell artifacts"))
    matrix_idx = next(i for i, n in enumerate(names) if n.startswith("Build predictor x case"))
    assert census_idx < matrix_idx

    census = _joined(_step("Census the cell artifacts"))
    assert f"> {CENSUS_FILE}" in census

    matrix = _joined(_step("Build predictor x case"))
    assert f"--stranded-file {CENSUS_FILE}" in matrix
    assert f"--stranded-note-file {CLOSE_NOTE_FILE}" in matrix


def test_the_census_degrades_open_and_says_so() -> None:
    """The failure this guard prevents is expensive, not dangerous: an API error
    must write an empty census, warn, and let the run proceed — never fail the
    plan job and block a legitimate run."""
    census = _step("Census the cell artifacts")
    body = str(census["run"])
    assert "set -euo pipefail" in body
    # The whole-guard degradation empties the census and exits clean.
    assert f"echo '[]' > {CENSUS_FILE}" in body
    assert "::warning::stranded-run guard degraded" in body
    assert "exit 0" in body
    # The per-run one keeps the rest of the census: a flake on one candidate must
    # not discard every other run's cells and re-spend them.
    assert "::warning::stranded-run guard skipped a run" in body
    # Every fetch routes its failure to one of the two rather than tripping
    # errexit, and retries first — a single transient 502 would otherwise turn
    # the guard off for a whole fan-out.
    joined = _joined(census)
    fetches = [
        line
        for line in joined.splitlines()
        if line.strip().startswith(("api ", "if ! api "))  # the retrying fetch helper
    ]
    assert len(fetches) == 3, "runs, jobs, artifacts"
    # Either the whole-guard degrade inline, or the per-run one in the `if` body.
    assert all(("|| degraded" in line or line.strip().startswith("if ! api")) for line in fetches)
    assert "for attempt in 1 2 3" in body


def test_the_census_is_bounded_and_filters_to_uncollected_cell_artifacts() -> None:
    """Three filters make the census cheap and correct: a candidate window that
    outlasts a day of predict cycles, runs whose `collect` did not conclude
    success, and cell artifacts only."""
    body = _joined(_step("Census the cell artifacts"))
    # The window is the real bound; the page must not cut it short — a day of
    # predict cycles must not push a stranded run out of view before the
    # re-queue it exists to catch.
    assert "48 hours ago" in body
    assert "per_page=50" in body
    assert 'select(.name == "collect") | .conclusion' in body
    assert "grep -qx success" in body
    assert 'startswith("predict-")' in body
    # Paginated: a full-width run's cell jobs push `collect` off page one.
    assert "--paginate" in body
    # The self-releasing property rests on this, so it is explicit rather than
    # inherited from an API default.
    assert "filter=latest" in body


def test_the_collect_job_keeps_the_name_the_census_matches_on() -> None:
    """The census asks the jobs API for `collect` by name. Giving that job a
    display `name:` would make every run read as uncollected — the matrix would
    empty and run-predict would stop predicting while closing trigger issues
    with a recovery note."""
    assert "name" not in _load("run-predict.yml")["jobs"]["collect"]


def test_the_census_takes_no_expression_into_its_shell() -> None:
    """The ambient token and the repo travel as env, like every other API step
    here; the shell body interpolates no workflow expression."""
    census = _step("Census the cell artifacts")
    assert census["env"] == {
        "GH_TOKEN": "${{ github.token }}",
        "REPO": "${{ github.repository }}",
    }
    assert "${{" not in str(census["run"])


def test_a_fully_superseded_run_closes_with_the_recovery_note() -> None:
    """`has_jobs=false` has several causes and the close step cannot tell most of
    them apart — but this one it must, because the honest instruction is the
    opposite of a re-queue: recover the uncollected run. The note comes from the
    tested matrix command; the step only posts it."""
    close = _step("Close the trigger issue")
    body = str(close["run"])
    assert f"[ -s {CLOSE_NOTE_FILE} ]" in body
    assert f"comment=$(cat {CLOSE_NOTE_FILE})" in body
    # The generic out-of-scope note survives for every other empty matrix.
    assert "every queued case was dropped by the predict-scope gate" in body
    assert 'gh issue close "$ISSUE" --repo "$REPO" --comment "$comment"' in body
