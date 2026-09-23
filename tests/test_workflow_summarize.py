"""The case-summary lane's workflow shape: credential separation and the spend hold.

`summarize.yml` touches two credentials — the read-only corpus role and a
dedicated model API key — and the lane's security rests on no job holding
both: a step that could read the corpus and call the model could send the
corpus anywhere the model's output reaches. These tests pin that split, the
`review` hold in front of every spend, and the publication fence, so an edit
that merges two jobs or drops the hold fails here rather than in a run.
"""

from pathlib import Path
from typing import Any

import yaml

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"
NAME = "summarize.yml"
KEY_SECRET = "secrets.SUMMARIES_ANTHROPIC_API_KEY"


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


def test_the_lane_uses_its_own_key_not_the_cells() -> None:
    text = (WORKFLOWS / NAME).read_text()
    assert "secrets.ANTHROPIC_API_KEY" not in text
    for other in sorted(WORKFLOWS.glob("*.y*ml")):
        if other.name != NAME:
            assert KEY_SECRET not in other.read_text(), f"{other.name} reaches the summaries key"


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
    assert "--known-secret-env SUMMARIES_ANTHROPIC_API_KEY" in run
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
