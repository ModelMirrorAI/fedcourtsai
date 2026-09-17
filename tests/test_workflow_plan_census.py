"""The `plan` job's stranded-run guard, pinned at the workflow shape.

A predict cell spends its tokens before `collect`, the run's single durability
step, so a collect that fails after a full-width fan-out leaves every prediction
in a cell artifact and nothing in the ledger — the ledger being what the
matrix's already-predicted gate reads. Without a guard the next live cycle
re-derives the same events and re-spends the identical run.

`collect` concluding success is not the same as the run having landed: its PR
may still be open, or it may have pushed no branch at all (the secret scan's
withhold). Both leave the ledger untouched, so the census carries the collect
PRs as well, and the same decision step tells the three apart.

The guard is split deliberately: a thin census step fetches and filters (the
runs, artifacts and pulls APIs), and the tested `predict-matrix` command
decides. These pins hold the wiring that no Python test can see — that the
census exists, runs before the matrix step, reaches the matrix step by filename,
degrades open rather than failing the job, and that the run's own summary can
tell a fully-superseded run from a drained backlog.
"""

from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"

CENSUS_FILE = "stranded-artifacts.json"
PR_FILE = "collect-prs.json"
NOTE_FILE = "stranded-note.md"


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
        # assume the AWS role for the corpus pull (read-only)
        "id-token": "write",
        # list recent runs and their cell artifacts for the stranded-run guard
        "actions": "read",
        # read whether this lane's collect PR has merged — metadata only, and
        # no write: the plan job opens, comments on and reviews nothing.
        "pull-requests": "read",
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
    assert f"> {PR_FILE}" in census

    matrix = _joined(_step("Build predictor x case"))
    assert f"--stranded-file {CENSUS_FILE}" in matrix
    assert f"--collect-prs-file {PR_FILE}" in matrix
    assert f"--stranded-note-file {NOTE_FILE}" in matrix
    # The plan report the hold is judged on must see the same withholds, or a
    # maintainer approves a fan-out the matrix step already narrowed.
    report = _joined(_step("Report the plan"))
    assert f"--stranded-file {CENSUS_FILE}" in report
    assert f"--collect-prs-file {PR_FILE}" in report


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
        if line.strip().startswith(("api ", "if ! api ", "if api "))  # the retrying fetch helper
    ]
    assert len(fetches) == 4, "pulls, runs, jobs, artifacts"
    # Either the whole-guard degrade inline, or a per-grain one in the `if` body.
    assert all(
        ("|| degraded" in line or line.strip().startswith(("if ! api", "if api")))
        for line in fetches
    )
    assert "for attempt in 1 2 3" in body
    # The third grain: a PR listing the step could not read disarms only the arm
    # that judges a collected run, and does it by DELETING the file — an empty
    # list is a claim (this lane has no collect PR) that would read every
    # collected run as having pushed nothing and withhold every cell it produced.
    assert "::warning::stranded-run guard's collect-PR arm is off" in body
    assert f"rm -f {PR_FILE}" in body
    assert f"echo '[]' > {PR_FILE}" not in body


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
    # A collected run is no longer skipped: its artifacts are censused too, and
    # whether it landed is decided from its collect PR. The run's own window
    # rides along, because that is the only join between a run and the PR its
    # `plan` job's run id named.
    assert "collect_succeeded" in body
    assert "run_started_at" in body
    assert "run_updated_at" in body
    # The PR listing: this lane's branches, to `main`, open and settled alike.
    assert 'startswith("predict/run-")' in body
    assert "base=main&state=all" in body
    # Same-repo heads only. The listing includes fork PRs, whose head ref is the
    # fork's own branch name with no owner in it, so on a public repo a branch
    # named `predict/run-<stamp>` on anyone's fork would read as a run's open
    # collect PR and withhold a legitimate round — the one direction this guard
    # must never take. `ci.yml`'s `main-base` jail requires the same conjunct
    # before believing a head's name.
    assert 'select((.head.repo.full_name // "") == env.REPO)' in body
    # One page of 100 is trusted only when it reaches back past the window: a
    # page that stopped short would report a censused run's PR as absent and
    # convict it of a withheld collect. Read as a `min` rather than off the last
    # row, so it does not rest on the API having honoured the sort.
    assert "([.[].created_at] | min)" in body
    assert "could not establish that the PR listing reaches back" in body
    # The window's lower bound must not move under a re-run: `run_started_at`
    # resets to the latest attempt, and rerunning `collect` is this guard's own
    # remedy, so a window opening there would begin after the first attempt's
    # plan minted the run id — and the recovered run would read as having pushed
    # no branch at all, the one verdict that sends a maintainer to hand salvage.
    assert "[.created_at, (.run_started_at // .created_at)] | min" in body
    # Projected in the fetch, so the PR bodies — which carry rolled-up agent flag
    # text on this lane — never land in the plan job's workspace.
    assert "head_repo: .head.repo.full_name" in body
    # Paginated: a full-width run's cell jobs push `collect` off page one.
    assert "--paginate" in body
    # The self-releasing property rests on this, so it is explicit rather than
    # inherited from an API default.
    assert "filter=latest" in body


def test_the_collect_job_keeps_the_name_the_census_matches_on() -> None:
    """The census asks the jobs API for `collect` by name. Giving that job a
    display `name:` would make every run read as uncollected — the matrix would
    empty and run-predict would stop predicting while every round reported a
    recovery note."""
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


def test_a_fully_superseded_run_reports_the_recovery_note_not_a_drained_queue() -> None:
    """`has_jobs=false` has several causes and the summary cannot tell most of
    them apart — but this one it must, because the honest instruction is the
    opposite of "wait for the next cycle": recover the uncollected run. The
    guard writes the note file only when it withheld every cell, so the file's
    presence is the marker; the run's whole record is its step summary, so the
    two readings must not be reported as one."""
    body = _joined(_step("Build predictor x case"))
    assert f"[ -s {NOTE_FILE} ]" in body
    # The drained-backlog line is the other branch, never the shared one.
    drained = "The predict backlog is drained"
    assert drained in body
    note_idx = body.index(f"[ -s {NOTE_FILE} ]")
    assert body.index(drained) > note_idx, "the drained line must sit in the else branch"
    assert "stranded-run guard withheld every cell" in body
