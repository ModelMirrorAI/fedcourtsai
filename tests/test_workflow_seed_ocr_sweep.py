"""run-seed's OCR sweep, read back out of the workflow and held to its shape.

Every walker window reads scanned filings by OCR through the command run-repair's
`ocr-recovery` pass dispatches, split at a credential boundary: a read-only
projection job that writes the window's slice, a parse job that holds no
credential of any kind and is the only job with the OCR binaries, and a writer
that re-checks the plan against a fresh pull, writes it, and mints the App token
only after it has. Nothing at runtime ties the YAML to that design, so these
tests do:

* **the split** — the parse job can mint nothing and guards that it cannot, and
  it alone installs the binaries; the projection reads only; the writer assumes
  the read-write role after the plan is checked and mints the App token after
  the write, on a commit step whose AWS session is blanked;
* **the sweep** — the writer runs `--from-plan --sweep --apply` with no bound;
* **posture** — every job is non-blocking, rides every window, and the chain
  hands each job the next one's go-ahead as a step output;
* **the artifacts** — one day, named per run;
* **parity** — every argv in the three jobs still parses against the CLI.

The sweep's semantics (the order, the slice, the plan checks) are pinned at
their unit seam, `tests/test_ocr_sweep.py`.
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
JOBS = ("ocr-sweep-projection", "ocr-sweep-parse", "ocr-sweep")


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
    """The job that fetches, renders and recognizes the Court's filings can mint nothing."""
    job = _job("ocr-sweep-parse")
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
    assert (
        names.index("Assert no credential reaches the parse")
        < names.index("Install the OCR binaries")
        < names.index("Read the scanned filings")
    )
    setup = next(s for s in job["steps"] if s.get("uses") == "./.github/actions/setup-python-env")
    assert setup.get("with", {}).get("save-cache") == "false", "the parse job must not save a cache"


def test_only_the_parse_job_installs_the_ocr_binaries() -> None:
    """A job holding a corpus credential never has a PDF renderer on a schedule."""
    for name, job in _jobs().items():
        installs = "tesseract-ocr" in yaml.safe_dump(job)
        assert installs == (name == "ocr-sweep-parse"), name


def test_the_projection_reads_only() -> None:
    projection = _job("ocr-sweep-projection")
    assert projection["permissions"] == {"contents": "read", "id-token": "write"}
    dumped = yaml.safe_dump(projection)
    assert "corpus-readonly" in dumped
    assert "AWS_ROLE_TO_ASSUME }}" not in dumped, "the projection reads only"
    assert "app-token" not in dumped and "secrets." not in dumped


def test_the_writer_writes_before_any_github_credential_exists() -> None:
    writer = _job("ocr-sweep")
    assert writer["permissions"] == {"contents": "read", "id-token": "write"}
    names = _names(writer)
    order = [
        "Download the plan",
        "Download the worklist",
        "Check the downloaded plan",
        "Configure AWS credentials (corpus S3 remote, read-write)",
        "Pull the current corpus from the remote",
        "Write the recovered filings",
        "Mint app token",
        "Configure git identity",
        "Commit the OCR pointer",
    ]
    assert [n for n in names if n in order] == order
    holders = [
        name
        for name, step in zip(names, writer["steps"], strict=True)
        if "steps.app-token" in yaml.safe_dump(step)
    ]
    assert holders == ["Configure git identity", "Commit the OCR pointer"]
    commit = writer["steps"][names.index("Commit the OCR pointer")]
    assert commit["env"]["AWS_ACCESS_KEY_ID"] == ""
    assert commit["env"]["AWS_SECRET_ACCESS_KEY"] == ""
    assert commit["env"]["AWS_SESSION_TOKEN"] == ""
    body = str(commit["run"])
    code = [line for line in body.splitlines() if not line.lstrip().startswith("#")]
    assert [line.strip() for line in code if "git add" in line] == ["git add corpus/corpus.db.ref"]
    assert "push_with_retry.sh" in body
    write = str(writer["steps"][names.index("Write the recovered filings")]["run"])
    assert write.index("ocr-recover-petitions") < write.index("corpus-push")
    assert "::stop-commands::" in write


def test_the_writer_sweeps_with_no_bound() -> None:
    (write, push) = _argvs(_job("ocr-sweep"))[1:]
    assert write == [
        "ocr-recover-petitions",
        "--from-plan",
        "${HANDOFF_PLAN}",
        "--bind-worklist",
        "${HANDOFF_WORKLIST}",
        "--sweep",
        "--apply",
    ]
    assert push == ["corpus-push"]
    for name in JOBS:
        for argv in _argvs(_job(name)):
            assert not any(arg.startswith("--max-") for arg in argv), name
    (parse,) = _argvs(_job("ocr-sweep-parse"))
    assert parse[:2] == ["ocr-recover-petitions", "--worklist"]
    assert "--plan-out" in parse and "--deadline-seconds" in parse
    (emit,) = _argvs(_job("ocr-sweep-projection"))
    assert emit[:3] == ["ocr-recover-petitions", "--sweep", "--emit-worklist"]


def test_the_chain_is_non_blocking_every_window_and_gated_on_step_outputs() -> None:
    jobs = _jobs()
    for name in JOBS:
        assert jobs[name].get("continue-on-error") is True, name
        assert isinstance(jobs[name].get("timeout-minutes"), int), name
        assert "!cancelled()" in _norm(jobs[name]["if"]), name
        assert "github.event.schedule" not in _norm(jobs[name]["if"]), "every window"
        assert "concurrency" not in jobs[name], name
    assert own_needs(jobs["ocr-sweep-parse"]) == ["ocr-sweep-projection"]
    assert "needs.ocr-sweep-projection.outputs.worklist == 'written'" in _norm(
        jobs["ocr-sweep-parse"]["if"]
    )
    assert own_needs(jobs["ocr-sweep"]) == ["seed", "ocr-sweep-projection", "ocr-sweep-parse"]
    assert "needs.ocr-sweep-parse.outputs.plan == 'written'" in _norm(jobs["ocr-sweep"]["if"])
    for job, output, step in (
        ("ocr-sweep-projection", "worklist", "Write the OCR worklist"),
        ("ocr-sweep-parse", "plan", "Read the scanned filings"),
    ):
        body = str(jobs[job]["steps"][_names(jobs[job]).index(step)]["run"])
        assert "set -euo pipefail" in body, job
        assert f'echo "{output}=written" >> "$GITHUB_OUTPUT"' in body, job
    assert own_needs(jobs["guard"]) == ["seed"]
    assert set(JOBS) <= set(own_needs(jobs["run-gate"]))


def test_the_parse_deadline_sits_under_its_step_cap() -> None:
    """The deadline is when work may last begin; a started document runs to its
    600-second budget past it, so the step cap must hold both."""
    job = _job("ocr-sweep-parse")
    step = job["steps"][_names(job).index("Read the scanned filings")]
    (argv,) = command_argv(str(step["run"]), FEDCOURTS)
    deadline = float(argv[argv.index("--deadline-seconds") + 1])
    assert deadline + 600 <= int(step["timeout-minutes"]) * 60
    assert int(step["timeout-minutes"]) < int(job["timeout-minutes"])


def test_the_handoff_artifacts_are_short_lived_and_named_per_run() -> None:
    uploads = [
        (name, step)
        for name in JOBS
        for step in _job(name)["steps"]
        if str(step.get("uses", "")).startswith("actions/upload-artifact@")
    ]
    assert {name for name, _ in uploads} == {"ocr-sweep-projection", "ocr-sweep-parse"}
    for name, step in uploads:
        with_ = step["with"]
        assert with_["retention-days"] == 1, name
        assert str(with_["name"]).endswith("-${{ github.run_id }}"), name
        assert str(with_["path"]).startswith("${{ runner.temp }}/handoff/"), name

    # Every download is by artifact id, read from the producing job's own
    # outputs: a parse in this run can replace an artifact by name, but cannot
    # forge another job's outputs.
    jobs = _jobs()
    for name, step in uploads:
        assert "id" in step, name
        outputs = jobs[name]["outputs"]
        assert f"${{{{ steps.{step['id']}.outputs.artifact-id }}}}" in outputs.values(), name
    downloads = [
        (name, step["with"])
        for name in JOBS
        for step in _job(name)["steps"]
        if str(step.get("uses", "")).startswith("actions/download-artifact@")
    ]
    assert sorted(str(with_["artifact-ids"]) for _, with_ in downloads) == sorted(
        [
            "${{ needs.ocr-sweep-projection.outputs.worklist-artifact }}",
            "${{ needs.ocr-sweep-projection.outputs.worklist-artifact }}",
            "${{ needs.ocr-sweep-parse.outputs.plan-artifact }}",
        ]
    )
    for name, with_ in downloads:
        assert "name" not in with_, name
        assert with_["merge-multiple"] is True, name


@pytest.mark.parametrize("name", JOBS)
def test_each_jobs_argv_still_parses_against_the_cli(name: str) -> None:
    """Exit 2 is a renamed or removed flag; `--help` parses every option first."""
    for argv in _argvs(_job(name)):
        result = CliRunner().invoke(app, [*argv, "--help"])
        assert result.exit_code == 0, f"`fedcourts {' '.join(argv)}`\n{result.output}"
