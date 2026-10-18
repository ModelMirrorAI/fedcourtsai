"""The promotion train's workflow (`promotion-prep.yml`): its schedule, the split
of its credentials across jobs, and the writes it may make.

The decision is tested in ``test_promotion_train.py``; this pins what the
workflow does with it. The plan job decides and renders holding no write
credential; the write job mints the dev App token only after re-reading the
merge's preconditions (the dev App bypasses `main`'s approval rule, so that
re-check is what binds an unattended merge to the maintainer); the dispatch
job is the dispatch App's alone (``test_workflow_dispatch_chain.py``). A
candidate branch is created once and never moved: nothing here updates,
force-pushes or deletes a ref.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from tests.workflow_gate import own_condition

WORKFLOWS = Path(__file__).resolve().parent.parent / ".github" / "workflows"
TRAIN = WORKFLOWS / "promotion-prep.yml"
DEV_KEY = "secrets.DEV_APP_PRIVATE_KEY"
DISPATCH_KEY = "secrets.DISPATCH_APP_PRIVATE_KEY"
MINT = "create-github-app-token"


def _workflow() -> dict[Any, Any]:
    data = yaml.safe_load(TRAIN.read_text())
    assert isinstance(data, dict)
    return data


def _job(name: str) -> dict[str, Any]:
    job: dict[str, Any] = _workflow()["jobs"][name]
    return job


def _runs(job: dict[str, Any]) -> str:
    return "\n".join(str(step.get("run", "")) for step in job.get("steps", []))


def test_the_train_ticks_hourly_on_a_minute_of_its_own() -> None:
    (entry,) = _workflow()[True]["schedule"]
    minute, hour, *rest = entry["cron"].split()
    assert (hour, rest) == ("*", ["*", "*", "*"])
    assert minute not in {"0", "30"}
    taken = set()
    for path in WORKFLOWS.glob("*.yml"):
        if path == TRAIN:
            continue
        triggers = yaml.safe_load(path.read_text()).get(True) or {}
        for other in (triggers.get("schedule") or []) if isinstance(triggers, dict) else []:
            taken.update(other["cron"].split()[0].split(","))
    assert minute not in taken


def test_only_a_dispatched_tick_asks_for_a_cut() -> None:
    """The maintainer closes a batch by dispatching; a scheduled tick never
    passes the request, so it cannot cut."""
    assert "workflow_dispatch" in _workflow()[True]
    (read,) = [s for s in _job("plan")["steps"] if s.get("id") == "read"]
    assert read["env"]["EVENT_NAME"] == "${{ github.event_name }}"
    run = read["run"]
    assert run.count("--cut-requested") == 1
    assert 'if [ "$EVENT_NAME" = workflow_dispatch ]; then\n  args+=(--cut-requested)\nfi' in run


def test_the_plan_job_holds_no_write_credential() -> None:
    job = _job("plan")
    assert "environment" not in job
    assert job["permissions"] == {
        "contents": "read",
        "actions": "read",
        "pull-requests": "read",
        "checks": "read",
    }
    text = yaml.safe_dump(job)
    assert "secrets." not in text
    assert MINT not in text


def test_the_plan_decides_through_the_tested_commands_with_the_gate_stages_live() -> None:
    runs = _runs(_job("plan"))
    assert "uv run fedcourts promotion-train-candidate" in runs
    assert 'uv run fedcourts promotion-train-step "${args[@]}"' in runs
    assert "uv run fedcourts promotion-body" in runs
    for stage in (
        'scripts/promotion-gate.sh provenance "$sha" "$ref"',
        "scripts/promotion-gate.sh quiesce",
        'scripts/promotion-gate.sh registry "$sha"',
        'scripts/promotion-gate.sh freshness "$sha" "$ref"',
    ):
        assert stage in runs, stage
    # Both sides against the merge-base: main's paths decide whether staging
    # is synced, staging's tree whether there is anything to promote.
    assert "base=$(git merge-base origin/main origin/staging)" in runs
    assert 'git diff --name-only "$base" origin/main > main-ahead.txt' in runs
    assert 'git diff --quiet "$base" origin/staging' in runs


def test_only_the_write_job_holds_the_dev_app_and_it_binds_prod() -> None:
    holders = [name for name, job in _workflow()["jobs"].items() if DEV_KEY in yaml.safe_dump(job)]
    assert holders == ["write"]
    job = _job("write")
    assert job["environment"] == "prod"
    assert job["permissions"] == {"contents": "read", "actions": "read", "pull-requests": "read"}
    (mint,) = [step for step in job["steps"] if MINT in step.get("uses", "")]
    grants = {k: v for k, v in mint["with"].items() if k.startswith("permission-")}
    assert grants == {"permission-contents": "write", "permission-pull-requests": "write"}
    assert DISPATCH_KEY not in yaml.safe_dump(job)


def test_the_write_job_runs_only_when_the_plan_owes_a_write() -> None:
    assert own_condition(_job("write")) == "needs.plan.outputs.write == 'true'"


def test_the_merge_is_re_checked_before_the_token_exists() -> None:
    """Approval at exactly the head (the dev App bypasses the approval rule, so
    this is the binding check), the PR unchanged, and quiescence read again,
    all on the ambient token, before the mint — whose condition needs it."""
    steps = _job("write")["steps"]
    names = [step.get("name", step.get("uses", "")) for step in steps]
    recheck = names.index("Re-check the merge")
    mint = next(i for i, step in enumerate(steps) if MINT in step.get("uses", ""))
    assert recheck < mint
    run = steps[recheck]["run"]
    assert steps[recheck]["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert (
        'uv run fedcourts promotion-train-approval --reviews-file reviews.json --head-sha "$SHA"'
        in run
    )
    assert "scripts/promotion-gate.sh quiesce" in run
    assert '"open|false|${SHA}|${REF}|main|${REPO}"' in run
    assert "steps.recheck.outputs.ok == 'true'" in steps[mint]["if"]


def test_the_merge_is_a_merge_commit_pinned_to_the_head() -> None:
    act = next(step for step in _job("write")["steps"] if step.get("name") == "Act")
    run = act["run"]
    assert 'gh api -X PUT "repos/${REPO}/pulls/${PR}/merge"' in run
    assert '-f merge_method=merge -f sha="$SHA"' in run
    assert "squash" not in run.replace("never a squash", "")
    assert "rebase" not in run


def test_a_candidate_is_created_once_and_never_moved() -> None:
    """The only ref write is the creation; no update, force push or deletion of
    any ref, and no git push at all."""
    text = TRAIN.read_text()
    assert len(re.findall(r'gh api -X POST "repos/\$\{REPO\}/git/refs"', text)) == 1
    assert "git push" not in text
    assert "-X PATCH" not in text
    assert "-X DELETE" not in text
    assert not re.search(r"--force|-F force|force=true", _runs(_job("write")))
    act = next(step for step in _job("write")["steps"] if step.get("name") == "Act")
    assert 'gh pr create --repo "$REPO" --base main --head "$BRANCH" --draft' in act["run"]


def test_the_write_job_re_validates_every_plan_output_it_uses() -> None:
    steps = _job("write")["steps"]
    validate = next(step for step in steps if step.get("name") == "Validate the plan's outputs")
    run = validate["run"]
    assert "^promote/[0-9]{4}-[0-9]{2}-[0-9]{2}(-([2-9]|[1-9][0-9]+))?$" in run
    assert "^[0-9a-f]{40}$" in run
    assert "^[1-9][0-9]*$" in run
    names = [step.get("name", "") for step in steps]
    assert names.index("Validate the plan's outputs") < names.index("Act")


def test_no_plan_output_is_interpolated_into_a_script() -> None:
    """Outputs reach shell only through `env:`, never `${{ }}` inside `run:`."""
    for name, job in _workflow()["jobs"].items():
        for step in job.get("steps", []):
            assert "${{" not in str(step.get("run", "")), (name, step.get("name"))


def test_the_render_never_lets_a_refire_be_skipped_as_unchanged() -> None:
    render = next(step for step in _job("plan")["steps"] if step.get("id") == "render")
    run = render["run"]
    assert 'if [ "$ACTION" = refire_gate ]; then' in run
    assert "mark_ready | refire_gate | merge) write=true" in run
    assert "<!-- promotion-train:marked-ready -->" in run


def test_the_dispatch_switch_off_names_the_command_for_the_maintainer() -> None:
    decide = next(step for step in _job("plan")["steps"] if step.get("id") == "step")
    assert decide["env"]["CHAIN_ENABLED"] == "${{ vars.DISPATCH_CHAIN_ENABLED }}"
    assert (
        "gh workflow run integration-test.yml --ref ${ref} -f scenario=${scenario}" in decide["run"]
    )


def test_every_list_read_is_whole() -> None:
    """A list cut at its first page could hide a change request, a run at the
    head or a promotion PR: the plan and the merge re-check read every page."""
    plan = _runs(_job("plan"))
    assert 'gh api --paginate --slurp "$url"' in plan
    for url in (
        "pulls?state=open&base=main&per_page=100",
        "pulls/${number}/reviews?per_page=100",
        "check-runs?filter=all&per_page=100",
        "runs?head_sha=${sha}&per_page=100",
    ):
        assert 'read_list "repos/${REPO}/' in plan
        assert url in plan, url
    recheck = next(s for s in _job("write")["steps"] if s.get("name") == "Re-check the merge")
    assert (
        'gh api --paginate --slurp "repos/${REPO}/pulls/${PR}/reviews?per_page=100"'
        in (recheck["run"])
    )


def test_the_merge_re_check_re_runs_the_registry_gate() -> None:
    recheck = next(s for s in _job("write")["steps"] if s.get("name") == "Re-check the merge")
    assert 'scripts/promotion-gate.sh registry "$SHA"' in recheck["run"]
    checkout = _job("write")["steps"][0]
    assert checkout["with"]["fetch-depth"] == 0


def test_the_plan_reads_what_the_new_rules_decide_on() -> None:
    plan = _runs(_job("plan"))
    for flag in (
        "--last-promotion-synced",
        "--recent-dispatches-file",
        "--pull-file",
        "--freshness-ok",
    ):
        assert flag in plan, flag
    assert 'PROMOTION_SKIP_SMOKE="$skip" scripts/promotion-gate.sh freshness' in plan
    assert 'git merge-base --is-ancestor "$merge" origin/staging' in plan
