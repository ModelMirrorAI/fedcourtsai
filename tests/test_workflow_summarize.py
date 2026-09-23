"""The case-summary lane's workflow shape: credential separation and the spend hold.

`summarize.yml` touches two credentials — the read-only corpus role and the
environment's Anthropic API key — and the lane's security rests on no job
holding both: a step that could read the corpus and call the model could send the
corpus anywhere the model's output reaches. These tests pin that split, the
`review` hold in front of every spend, and the publication fence, so an edit
that merges two jobs or drops the hold fails here rather than in a run.
"""

from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"
NAME = "summarize.yml"
KEY_SECRET = "secrets.ANTHROPIC_API_KEY"


def _load(name: str = NAME) -> dict[Any, Any]:
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    assert isinstance(data, dict)
    return data


def _jobs() -> dict[str, dict[str, Any]]:
    jobs = _load()["jobs"]
    assert isinstance(jobs, dict)
    return jobs


def _needs(job: dict[str, Any]) -> set[str]:
    needs = job.get("needs", [])
    return {needs} if isinstance(needs, str) else set(needs)


def _holds_cloud_credential(job: dict[str, Any]) -> bool:
    permissions = job.get("permissions") or {}
    steps = job.get("steps") or []
    return permissions.get("id-token") == "write" or any(
        "corpus-readonly" in str(step.get("uses", ""))
        or "configure-aws-credentials" in str(step.get("uses", ""))
        for step in steps
    )


def test_no_job_holds_both_the_api_key_and_a_cloud_credential() -> None:
    holders = {name for name, job in _jobs().items() if KEY_SECRET in yaml.safe_dump(job)}
    assert holders == {"generate"}, f"only the generate job may hold the key, found {holders}"
    for name, job in _jobs().items():
        if name in holders:
            assert not _holds_cloud_credential(job), f"{name} holds the key and a cloud credential"


def test_the_generate_job_asserts_it_holds_no_cloud_credential_first() -> None:
    steps = _jobs()["generate"]["steps"]
    names = [str(step.get("name", "")) for step in steps]
    guard = names.index("Assert no cloud credential in this job")
    first_key = next(i for i, step in enumerate(steps) if KEY_SECRET in yaml.safe_dump(step))
    assert guard < first_key
    run = steps[guard]["run"]
    assert "^AWS_" in run
    assert "ACTIONS_ID_TOKEN_REQUEST_URL" in run
    assert "if" not in steps[guard], "the tripwire must be unconditional"
    assert _jobs()["generate"]["permissions"] == {"contents": "read"}


def test_the_key_reaches_only_the_two_generate_steps_that_need_it() -> None:
    """The key is shared with the other Claude lanes, so what this lane owns is
    how far it reaches here: the summarize call, and the scan that looks for it
    in what that call wrote — no other step, in any job."""
    holders = [
        (name, str(step.get("name", "")))
        for name, job in _jobs().items()
        for step in job.get("steps") or []
        if KEY_SECRET in yaml.safe_dump(step)
    ]
    assert holders == [
        ("generate", "Write the summaries"),
        ("generate", "Jail, validate and scan the written summaries"),
    ]
    for name, job in _jobs().items():
        assert KEY_SECRET not in yaml.safe_dump(job.get("env") or {}), f"{name} job-level env"
    assert KEY_SECRET not in yaml.safe_dump(_load().get("env") or {})
    text = (WORKFLOWS / NAME).read_text()
    assert "secrets[" not in text and "toJSON(secrets" not in text, "no indirect secret access"


def test_every_spending_job_waits_on_the_review_hold() -> None:
    jobs = _jobs()
    assert jobs["approval"]["environment"] == "review"
    assert jobs["approval"]["permissions"] == {}
    assert not any("uses" in step for step in jobs["approval"]["steps"])
    # stage reads the corpus for the planned cases, generate spends: both sit
    # behind the released hold, generate through stage.
    assert "approval" in _needs(jobs["stage"])
    assert "success" in jobs["stage"]["if"] and "approval" in jobs["stage"]["if"]
    assert "stage" in _needs(jobs["generate"])
    assert "generate" in _needs(jobs["publish"])
    rejected = " ".join(str(jobs["rejected"]["if"]).split())
    assert "needs.approval.result != 'success'" in rejected
    assert jobs["rejected"]["permissions"] == {}


def test_the_credential_jobs_bind_the_branch_resolved_environment() -> None:
    # Pinned here because the auth-gate sweep keys on action markers, and
    # neither the corpus-readonly composite nor a raw key reference is one.
    resolved = "${{ github.ref_name == 'main' && 'prod' || github.ref_name }}"
    for name in ("plan", "stage", "generate"):
        assert _jobs()[name]["environment"] == resolved, name


def test_publication_is_fenced_to_main() -> None:
    publish = _jobs()["publish"]
    assert "github.ref == 'refs/heads/main'" in " ".join(str(publish["if"]).split())
    assert publish["environment"] == "prod"
    assert publish["permissions"] == {"contents": "read"}
    assert not _holds_cloud_credential(publish)
    body = yaml.safe_dump(publish)
    assert "summary-paths --strict" in body
    assert "scan-diff-for-secrets" in body
    assert "fedcourts validate data" in body
    assert "gh pr merge" not in body and "--auto" not in body, "the refresh PR is reviewed"


def test_the_generate_job_gates_its_artifact_on_the_jail_and_the_scan() -> None:
    steps = _jobs()["generate"]["steps"]
    collect = next(step for step in steps if step.get("id") == "collect")
    run = collect["run"]
    assert "summary-paths --strict" in run
    assert "fedcourts validate data" in run
    assert "--known-secret-env ANTHROPIC_API_KEY" in run
    upload = next(step for step in steps if step.get("name") == "Upload the summaries")
    assert "steps.collect.outputs.written" in upload["if"]


def test_its_own_serializing_group_and_a_free_cron_minute() -> None:
    workflow = _load()
    assert workflow["concurrency"]["cancel-in-progress"] is False
    assert str(workflow["concurrency"]["group"]).startswith("summarize-")
    [cron] = [entry["cron"] for entry in workflow[True]["schedule"]]
    minute = cron.split()[0]
    for other in sorted(WORKFLOWS.glob("*.y*ml")):
        if other.name == NAME:
            continue
        on = _load(other.name).get(True) or {}
        for entry in (on.get("schedule") or []) if isinstance(on, dict) else []:
            assert entry["cron"].split()[0] != minute, f"{other.name} shares minute {minute}"


def test_the_staged_records_are_checked_before_they_leave_the_stage_job() -> None:
    steps = _jobs()["stage"]["steps"]
    names = [str(step.get("name", "")) for step in steps]
    stage = names.index("Stage each planned case's record")
    check = names.index("Check the staged records before they leave this job")
    upload = names.index("Upload the staged records")
    assert stage < check < upload
    assert "fedcourts summary-stage-check" in steps[check]["run"]
    assert "set -euo pipefail" in steps[check]["run"]
    assert "if" not in steps[check], "the check must be unconditional"
    # A failed check must stop the upload: no step-level override lets it run anyway.
    assert "if" not in steps[upload]
    assert "continue-on-error" not in steps[check]
