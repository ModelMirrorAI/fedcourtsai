"""run-seed's order-list vote sweep, read back out of the workflow and held to its shape.

The walker's daily window stamps settled order-list votes onto committed cert and
interim outcomes through the same command run-repair's `order-votes` pass
dispatches, split at the same credential boundary: a read-only projection job, a
parse job that holds no credential of any kind, and a writer that applies the
plan in `--sweep` mode and mints the App token only after it has. Nothing at
runtime ties the YAML to that design, so these tests do:

* **the split** — the parse job can mint nothing and guards that it cannot; the
  projection reads only; the writer holds no AWS role and mints the App token
  after the plan is applied;
* **the sweep** — the writer runs `--from-plan --sweep --apply` with no bound,
  and nothing in the sweep can replace a record;
* **posture** — every job is non-blocking, the chain hands each job the next one's
  go-ahead as a step output, and it rides the daily window;
* **parity** — every argv in the three jobs still parses against the CLI.

The sweep's semantics (the slice, the ceiling, convergence across windows) are
pinned at their unit seam, `tests/test_vote_writer.py`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai.cli import app
from tests.workflow_argv import command_argv
from tests.workflow_gate import own_needs

ROOT = Path(__file__).resolve().parent.parent
RUN_SEED = ROOT / ".github" / "workflows" / "run-seed.yml"
FEDCOURTS = ("uv", "run", "fedcourts")
DAILY = "github.event.schedule == '31 2 * * *'"
JOBS = ("order-votes-projection", "order-votes-parse", "order-votes")


def _jobs() -> dict[str, Any]:
    jobs = yaml.safe_load(RUN_SEED.read_text())["jobs"]
    assert isinstance(jobs, dict)
    return jobs


def _job(name: str) -> dict[str, Any]:
    job = _jobs()[name]
    assert isinstance(job, dict)
    return job


def _names(job: dict[str, Any]) -> list[str]:
    return [str(s.get("name", s.get("uses", ""))) for s in job["steps"]]


def _norm(text: object) -> str:
    return " ".join(str(text).split())


def _argvs(job: dict[str, Any]) -> list[list[str]]:
    return [
        argv
        for step in job["steps"]
        for argv in command_argv(str(step.get("run", "")), FEDCOURTS)
        if argv
    ]


def test_the_parse_job_holds_no_credential_of_any_kind() -> None:
    """The job that fetches and parses the Court's documents can mint nothing."""
    job = _job("order-votes-parse")
    assert job["permissions"] == {"contents": "read"}
    assert "environment" not in job
    assert "env" not in job
    text = yaml.safe_dump(job)
    for forbidden in (
        "secrets.",
        "vars.",
        "app-token",
        "configure-aws-credentials",
        "corpus-readonly",
    ):
        assert forbidden not in text, f"the parse job reaches {forbidden!r}"
    names = _names(job)
    guard = job["steps"][names.index("Assert no credential reaches the parse")]
    assert "OIDC token minting is reachable" in str(guard["run"])
    assert "AWS credential variables reached" in str(guard["run"])
    assert "env" not in guard, "the guard must read the job's own environment"
    assert names.index("Read the vote records") > names.index(
        "Assert no credential reaches the parse"
    )
    setup = next(s for s in job["steps"] if s.get("uses") == "./.github/actions/setup-python-env")
    assert setup.get("with", {}).get("save-cache") == "false", "the parse job must not save a cache"


def test_the_projection_reads_only_and_the_writer_holds_no_aws_role() -> None:
    projection = _job("order-votes-projection")
    assert projection["permissions"] == {"contents": "read", "id-token": "write"}
    dumped = yaml.safe_dump(projection)
    assert "corpus-readonly" in dumped
    assert "AWS_ROLE_TO_ASSUME }}" not in dumped, "the projection reads only"
    assert "app-token" not in dumped and "secrets." not in dumped

    writer = _job("order-votes")
    assert writer["permissions"] == {"contents": "read"}, "the writer needs no corpus at all"
    assert "AWS_" not in yaml.safe_dump(writer)


def test_the_writer_applies_the_plan_before_any_write_credential_exists() -> None:
    writer = _job("order-votes")
    names = _names(writer)
    download = names.index("Download the plan")
    stamp = names.index("Stamp the planned vote records")
    token = names.index("Mint app token")
    assert download < names.index("Check the downloaded plan") < stamp < token
    holders = [
        name
        for name, step in zip(names, writer["steps"], strict=True)
        if "steps.app-token" in yaml.safe_dump(step)
    ]
    assert holders == ["Configure git identity", "Commit the stamped outcomes"]
    commit = str(writer["steps"][names.index("Commit the stamped outcomes")]["run"])
    code = [line for line in commit.splitlines() if not line.lstrip().startswith("#")]
    adds = [line.strip() for line in code if "git add" in line]
    assert adds == ["git add -- ':(glob)data/cases/*/*/events/*/outcome.json'"]
    assert "push_with_retry.sh" in commit


def test_the_writer_sweeps_and_nothing_in_the_chain_replaces_a_record() -> None:
    """The cap and ceiling stand in for a bound; replacement stays a dispatched call."""
    (stamp,) = _argvs(_job("order-votes"))
    assert stamp == [
        "stamp-order-votes",
        "--from-plan",
        "${HANDOFF_PLAN}",
        "--sweep",
        "--apply",
    ]
    for name in JOBS:
        for argv in _argvs(_job(name)):
            assert argv[0] == "stamp-order-votes", (name, argv)
            assert "--replace-differing" not in argv, name
            assert not any(arg.startswith("--max-") for arg in argv), name
    (parse,) = _argvs(_job("order-votes-parse"))
    assert parse[:2] == ["stamp-order-votes", "--projection"] and "--plan-out" in parse
    (emit,) = _argvs(_job("order-votes-projection"))
    assert emit[:2] == ["stamp-order-votes", "--emit-corpus-projection"]


def test_the_chain_is_non_blocking_daily_and_gated_on_step_outputs() -> None:
    """continue-on-error reads a failed job as a success to `needs.*.result`, so each
    hand-off is a step output the producing step sets only after it succeeded."""
    jobs = _jobs()
    for name in JOBS:
        assert jobs[name].get("continue-on-error") is True, name
        assert isinstance(jobs[name].get("timeout-minutes"), int), name
        assert "!cancelled()" in _norm(jobs[name]["if"]), name
    assert DAILY in _norm(jobs["order-votes-projection"]["if"])
    assert own_needs(jobs["order-votes-parse"]) == ["order-votes-projection"]
    assert "needs.order-votes-projection.outputs.projection == 'written'" in _norm(
        jobs["order-votes-parse"]["if"]
    )
    assert own_needs(jobs["order-votes"]) == ["seed", "order-votes-parse"]
    assert "needs.order-votes-parse.outputs.plan == 'written'" in _norm(jobs["order-votes"]["if"])
    for job, output, step in (
        ("order-votes-projection", "projection", "Write the vote projection"),
        ("order-votes-parse", "plan", "Read the vote records"),
    ):
        names = _names(jobs[job])
        body = str(jobs[job]["steps"][names.index(step)]["run"])
        assert body.rstrip().endswith(f'echo "{output}=written" >> "$GITHUB_OUTPUT"'), job
        assert "set -euo pipefail" in body, job
    # The guard escalates the walk alone; the sweep converges on its own.
    assert own_needs(jobs["guard"]) == ["seed"]
    # No job-level lock: the workflow's own `corpus-write` group already covers
    # the run, and a job waiting on the group its run holds would never start.
    for name in JOBS:
        assert "concurrency" not in jobs[name], name


def test_the_handoff_artifacts_are_short_lived_and_named_per_run() -> None:
    uploads = [
        (name, step)
        for name in JOBS
        for step in _job(name)["steps"]
        if str(step.get("uses", "")).startswith("actions/upload-artifact@")
    ]
    assert {name for name, _ in uploads} == {"order-votes-projection", "order-votes-parse"}
    for name, step in uploads:
        with_ = step["with"]
        assert with_["retention-days"] == 1, name
        assert str(with_["name"]).endswith("-${{ github.run_id }}"), name
        assert str(with_["path"]).startswith("${{ runner.temp }}/handoff/"), name
    downloads = {
        str(step["with"].get("artifact-ids", step["with"].get("name")))
        for name in JOBS
        for step in _job(name)["steps"]
        if str(step.get("uses", "")).startswith("actions/download-artifact@")
    }
    # The projection crosses to the parse by name; the plan crosses to the
    # writer by the id the parse published, which no other job's upload can
    # take over.
    assert downloads == {
        "order-votes-projection-${{ github.run_id }}",
        "${{ needs.order-votes-parse.outputs.plan-artifact }}",
    }
    parse = _job("order-votes-parse")
    upload = next(s for s in parse["steps"] if s.get("name") == "Upload the plan")
    assert parse["outputs"]["plan-artifact"] == (
        f"${{{{ steps.{upload['id']}.outputs.artifact-id }}}}"
    )
    writer = _job("order-votes")
    download = next(s for s in writer["steps"] if s.get("name") == "Download the plan")
    assert download["with"]["merge-multiple"] is True
    # An empty id downloads every artifact of the run, so the writer never starts on one.
    assert "needs.order-votes-parse.outputs.plan-artifact != ''" in _norm(writer["if"])


@pytest.mark.parametrize("name", JOBS)
def test_each_jobs_argv_still_parses_against_the_cli(name: str) -> None:
    """Exit 2 is a renamed or removed flag; `--help` parses every option first."""
    for argv in _argvs(_job(name)):
        result = CliRunner().invoke(app, [*argv, "--help"])
        assert result.exit_code == 0, f"`fedcourts {' '.join(argv)}`\n{result.output}"
        assert "--sweep" in result.output
