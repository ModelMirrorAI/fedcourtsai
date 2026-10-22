"""run-seed's opinion-record sweep, read back out of the workflow and held to its shape.

The walker's daily window reads each issued opinion into the per-opinion record
through the same command run-repair's `opinion-record` pass dispatches, split at
the same credential boundary: a read-only projection job, a parse job that holds
no credential of any kind and reads at most the window's slice, and a writer
that applies the plan in `--sweep` mode under the read-write role and mints the
App token only after it has pushed the blob. Nothing at runtime ties the YAML
to that design, so these tests do:

* **the split** — the parse job can mint nothing and guards that it cannot; the
  projection reads only; the writer pushes the blob before the App token exists
  and commits the pointer alone;
* **the sweep** — every job runs `--sweep`, which picks the Terms and the slice,
  with no Term, docket or bound flag;
* **posture** — every job is non-blocking, each hand-off is a step output, it
  rides the daily window, and the writer follows the OCR sweep's writer, the
  run's other blob push;
* **parity** — every argv in the three jobs still parses against the CLI.

The sweep's semantics (the slice, the ceiling) are pinned at their unit seam,
`tests/test_opinion_record.py`.
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
JOBS = ("opinion-record-projection", "opinion-record-parse", "opinion-record")


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
    """The job's `backfill-opinion-record` invocations (the writer also pulls and pushes)."""
    return [
        argv
        for step in job["steps"]
        for argv in command_argv(str(step.get("run", "")), FEDCOURTS)
        if argv and argv[0] == "backfill-opinion-record"
    ]


def test_the_parse_job_holds_no_credential_of_any_kind() -> None:
    job = _job("opinion-record-parse")
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
    assert names.index("Read the opinions") > names.index("Assert no credential reaches the parse")
    setup = next(s for s in job["steps"] if s.get("uses") == "./.github/actions/setup-python-env")
    assert setup.get("with", {}).get("save-cache") == "false", "the parse job must not save a cache"


def test_the_projection_reads_only() -> None:
    projection = _job("opinion-record-projection")
    assert projection["permissions"] == {"contents": "read", "id-token": "write"}
    dumped = yaml.safe_dump(projection)
    assert "corpus-readonly" in dumped
    assert "AWS_ROLE_TO_ASSUME }}" not in dumped, "the projection reads only"
    assert "app-token" not in dumped and "secrets." not in dumped


def test_the_writer_pushes_the_blob_before_any_github_credential_exists() -> None:
    writer = _job("opinion-record")
    assert writer["environment"] == "corpus-write"
    assert writer["permissions"] == {"contents": "read", "id-token": "write"}
    names = _names(writer)
    insert = names.index("Insert the planned opinion record")
    assert (
        names.index("Download the plan")
        < names.index("Check the downloaded plan")
        < names.index("Configure AWS credentials (corpus S3 remote, read-write)")
        < names.index("Pull the current corpus from the remote")
        < insert
        < names.index("Mint app token")
    )
    body = str(writer["steps"][insert]["run"])
    assert body.index("backfill-opinion-record") < body.index("fedcourts corpus-push")
    holders = [
        name
        for name, step in zip(names, writer["steps"], strict=True)
        if "steps.app-token" in yaml.safe_dump(step)
    ]
    assert holders == ["Configure git identity", "Commit the opinion-record pointer"]
    commit_step = writer["steps"][names.index("Commit the opinion-record pointer")]
    assert commit_step["env"]["AWS_SESSION_TOKEN"] == ""
    commit = str(commit_step["run"])
    code = [line for line in commit.splitlines() if not line.lstrip().startswith("#")]
    assert [line.strip() for line in code if "git add" in line] == ["git add corpus/corpus.db.ref"]
    assert "push_with_retry.sh" in commit


def test_every_job_sweeps_with_no_term_docket_or_bound() -> None:
    """`--sweep` picks the current and previous Term and the slice; nothing overrides it."""
    for name in JOBS:
        for argv in _argvs(_job(name)):
            assert argv[:2] == ["backfill-opinion-record", "--sweep"], (name, argv)
            assert not {"--first-term", "--last-term", "--docket", "--max-rows"} & set(argv)
            assert "--cache-dir" not in argv
    (apply,) = _argvs(_job("opinion-record"))
    assert apply[2:] == ["--from-plan", "${HANDOFF_PLAN}", "--apply"]
    (parse,) = _argvs(_job("opinion-record-parse"))
    assert "--projection" in parse and "--plan-out" in parse and "--apply" not in parse
    (emit,) = _argvs(_job("opinion-record-projection"))
    assert emit[2] == "--emit-corpus-projection"


def test_the_chain_is_non_blocking_daily_and_gated_on_step_outputs() -> None:
    jobs = _jobs()
    for name in JOBS:
        assert jobs[name].get("continue-on-error") is True, name
        assert isinstance(jobs[name].get("timeout-minutes"), int), name
        assert "!cancelled()" in _norm(jobs[name]["if"]), name
        assert "concurrency" not in jobs[name], name
    assert DAILY in _norm(jobs["opinion-record-projection"]["if"])
    assert own_needs(jobs["opinion-record-parse"]) == ["opinion-record-projection"]
    assert "needs.opinion-record-projection.outputs.projection == 'written'" in _norm(
        jobs["opinion-record-parse"]["if"]
    )
    # After the walk; the OCR sweep's writer, the run's other post-walk blob
    # push, waits for this one, since the run-level lock orders no jobs.
    assert own_needs(jobs["opinion-record"]) == ["seed", "opinion-record-parse"]
    assert "opinion-record" in own_needs(jobs["ocr-sweep"])
    writer_if = _norm(jobs["opinion-record"]["if"])
    assert "needs.opinion-record-parse.outputs.plan == 'written'" in writer_if
    assert "needs.opinion-record-parse.outputs.plan-artifact != ''" in writer_if
    names = _names(jobs["opinion-record-projection"])
    body = str(
        jobs["opinion-record-projection"]["steps"][
            names.index("Write the recorded-documents projection")
        ]["run"]
    )
    assert body.rstrip().endswith('echo "projection=written" >> "$GITHUB_OUTPUT"')
    assert "set -euo pipefail" in body
    # The plan is handed on only when the parse read a document: a converged
    # day starts no writer and pulls no corpus.
    names = _names(jobs["opinion-record-parse"])
    body = str(jobs["opinion-record-parse"]["steps"][names.index("Read the opinions")]["run"])
    assert "set -euo pipefail" in body
    assert 'select(.status == "read")' in body
    assert body.rstrip().endswith("fi") and 'echo "plan=written" >> "$GITHUB_OUTPUT"' in body
    for name in JOBS:
        assert name in own_needs(jobs["run-gate"]), name


def test_the_handoff_artifacts_are_short_lived_and_named_per_run() -> None:
    uploads = [
        (name, step)
        for name in JOBS
        for step in _job(name)["steps"]
        if str(step.get("uses", "")).startswith("actions/upload-artifact@")
    ]
    assert {name for name, _ in uploads} == {"opinion-record-projection", "opinion-record-parse"}
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
    assert downloads == {
        "opinion-record-projection-${{ github.run_id }}",
        "${{ needs.opinion-record-parse.outputs.plan-artifact }}",
    }
    parse = _job("opinion-record-parse")
    upload = next(s for s in parse["steps"] if s.get("name") == "Upload the plan")
    assert parse["outputs"]["plan-artifact"] == (
        f"${{{{ steps.{upload['id']}.outputs.artifact-id }}}}"
    )


def test_fetched_text_never_reaches_workflow_commands() -> None:
    """The readings quote fetched PDFs, so the parse and the insert suspend
    workflow commands around the command and copy only ledger lines to the summary."""
    for job, step in (
        ("opinion-record-parse", "Read the opinions"),
        ("opinion-record", "Insert the planned opinion record"),
    ):
        names = _names(_job(job))
        body = str(_job(job)["steps"][names.index(step)]["run"])
        assert 'echo "::stop-commands::${stop_token}"' in body, job
        assert body.index("::stop-commands::") < body.index("backfill-opinion-record")
        assert "GITHUB_STEP_SUMMARY" in body and "tee -a" not in body, job


@pytest.mark.parametrize("name", JOBS)
def test_each_jobs_argv_still_parses_against_the_cli(name: str) -> None:
    for argv in _argvs(_job(name)):
        result = CliRunner().invoke(app, [*argv, "--help"])
        assert result.exit_code == 0, f"`fedcourts {' '.join(argv)}`\n{result.output}"
        assert "--sweep" in result.output
