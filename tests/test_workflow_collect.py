"""`collect` is the single writer for a run's agent output, and it used to exist
as 250 lines duplicated verbatim in run-predict.yml and run-evaluate.yml — so a
durability fix had to land twice, and one copy could silently drift from the
other. It now lives in the `collect-run` composite action.

These tests lock that shape in. The action linters check syntax; only this checks
that both workflows still delegate, that the security posture stayed in the
caller where it is reviewable next to the trigger, and that the two call sites
differ by nothing but their role.
"""

from pathlib import Path
from typing import Any

import yaml

from fedcourtsai.collect import ExpectedCell, cell_artifact_name
from fedcourtsai.finalize import FinalizeRole

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
COLLECT_ACTION = ROOT / ".github" / "actions" / "collect-run" / "action.yml"

# Each fan-out workflow and the matrix job its collect job waits on.
FAN_OUTS = {"run-predict.yml": "predict", "run-evaluate.yml": "evaluate"}

# Work that must NOT reappear inline in a workflow: whoever re-adds it has
# forked the collect contract again.
COLLECT_INTERNALS = ("download-artifact", "gh pr create", "collect-plan")


def _load(path: Path) -> dict[Any, Any]:
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict)
    return data


def _collect_job(workflow: str) -> dict[str, Any]:
    job = _load(WORKFLOWS / workflow)["jobs"]["collect"]
    assert isinstance(job, dict)
    return job


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return list(job.get("steps", []))


def test_both_workflows_delegate_collect_to_the_shared_action() -> None:
    for workflow, role in FAN_OUTS.items():
        steps = _steps(_collect_job(workflow))
        delegations = [s for s in steps if s.get("uses") == "./.github/actions/collect-run"]
        assert len(delegations) == 1, f"{workflow} must delegate collect exactly once"
        assert delegations[0]["with"]["role"] == role


def test_no_workflow_reimplements_collect_inline() -> None:
    """The regression guard: re-inlining any of this forks the contract again."""
    for workflow in FAN_OUTS:
        body = (WORKFLOWS / workflow).read_text()
        collect_start = body.index("\n  collect:")
        collect_body = body[collect_start:]
        for marker in COLLECT_INTERNALS:
            assert marker not in collect_body, (
                f"{workflow}'s collect job contains {marker!r} inline; "
                "it belongs in .github/actions/collect-run"
            )


def test_the_two_call_sites_differ_only_by_role() -> None:
    """Anything else that diverges is drift the composite was meant to end."""
    predict, evaluate = (_collect_job(w) for w in FAN_OUTS)

    # The matrix job each waits on is legitimately per-workflow. Pop outside the
    # assert: a mutating expression inside one vanishes under `python -O`.
    predict_needs = predict.pop("needs")
    evaluate_needs = evaluate.pop("needs")
    assert predict_needs == ["plan", "predict"]
    assert evaluate_needs == ["plan", "evaluate"]

    # The delegating step differs only in `role`; normalize it out, then the two
    # jobs must be byte-equal — setup steps, permissions, timeout, everything.
    def _normalized(job: dict[str, Any]) -> dict[str, Any]:
        call = next(s for s in _steps(job) if s.get("uses", "").endswith("collect-run"))
        call["with"] = {k: v for k, v in call["with"].items() if k != "role"}
        return job

    assert _normalized(predict) == _normalized(evaluate), (
        "the two collect jobs diverge by more than their role — that drift is "
        "exactly what the composite extraction was meant to end"
    )


def test_the_caller_keeps_the_security_posture_visible() -> None:
    """`permissions`/`environment` must stay in the workflow, not move behind a
    `uses:` — they are the trust boundary and belong next to the trigger."""
    for workflow in FAN_OUTS:
        job = _collect_job(workflow)
        assert job["environment"] == "runner"
        assert job["permissions"] == {
            "contents": "write",
            "pull-requests": "write",
            "issues": "write",
            # Read-only, and only to list/fetch this run's own cell artifacts.
            "actions": "read",
        }


def _download_step() -> dict[str, Any]:
    action = _load(COLLECT_ACTION)
    return next(s for s in action["runs"]["steps"] if s["name"] == "Download cell artifacts")


def test_artifacts_are_fetched_one_at_a_time_not_as_one_fail_fast_unit() -> None:
    """The 2026-07-18 regression: `actions/download-artifact` fetches every
    artifact as a single unit, so one transient failure after its five internal
    retries discarded a whole run's 46 successful cells."""
    step = _download_step()
    assert "uses" not in step, (
        "collect is back on a bulk download action; one bad artifact would again "
        "cost the entire run's output"
    )
    body = step["run"]
    assert "gh run download" in body and "--name" in body, "fetch per artifact, by name"
    # merge-multiple would collapse every cell's data/ into one tree, destroying
    # the per-cell attribution the ready/salvage split and path jail depend on.
    assert "merge-multiple" not in body


def test_a_lost_artifact_warns_and_keeps_going_but_a_total_loss_fails_loudly() -> None:
    """Partial collection must commit what arrived; a total transfer failure must
    NOT fall through to the stall path, which tells a maintainer to re-run the
    whole matrix and would burn a full run of agent spend on a transfer bug."""
    body = _download_step()["run"]
    assert "::warning::artifact" in body, "a lost artifact must be named, not silent"
    assert "::error::" in body and "exit 1" in body, "a total transfer failure must fail the step"
    # The distinguishing guard: artifacts exist but none of them landed.
    assert '"$expected" -gt 0' in body and '"$collected" -eq 0' in body


def test_lost_artifacts_are_reported_downstream_not_just_logged() -> None:
    """A lost artifact leaves no status.json, so `collect-plan`'s cell census
    cannot see it. If the downloader's list is not threaded in, a partial
    transfer failure auto-merges a PR that presents itself as the whole run —
    turning a loud total loss into a quiet partial one."""
    body = _download_step()["run"]
    assert "missing-artifacts.txt" in body, "the downloader must record what it lost"

    action = _load(COLLECT_ACTION)
    aggregate = next(s for s in action["runs"]["steps"] if s["name"].startswith("Aggregate"))
    assert "--missing-file missing-artifacts.txt" in aggregate["run"], (
        "collect-plan must be told what failed to transfer, or the loss is invisible"
    )


def test_uncovered_cells_are_warned_in_step_not_only_in_the_pr_body() -> None:
    """The PR body is rendered under the ready PR. On a run where most cells died
    — exactly what the census exists for — there may be no ready PR at all, so a
    body-only disclosure would drop the named cells entirely."""
    aggregate = next(
        s for s in _load(COLLECT_ACTION)["runs"]["steps"] if s["name"].startswith("Aggregate")
    )
    assert ".uncovered_cells[]" in aggregate["run"], (
        "warn per uncovered cell in-step, or a no-ready-PR run reports none of them"
    )
    assert "needs a re-queue" in aggregate["run"], "name the remedy, which a rerun cannot supply"


def test_a_truncated_download_is_cleared_before_retry() -> None:
    """A half-written data/ subtree would otherwise be unioned into the PR as if
    it were a complete cell."""
    body = _download_step()["run"]
    assert body.count('rm -rf "cell-artifacts/${name}"') >= 2, (
        "clear the partial extraction both before a retry and after giving up"
    )


def test_the_composite_derives_every_role_dependent_string() -> None:
    """A hardcoded role in the shared body would make one workflow silently wrong."""
    body = COLLECT_ACTION.read_text()
    _, run_block = body.split("runs:", 1)
    for stray in ("--role predict", "--role evaluate", "pattern: predict-", "pattern: evaluate-"):
        assert stray not in run_block, f"{stray!r} is hardcoded; derive it from `role`"
    # The judgment noun comes off the plan, not a second mapping in shell, so the
    # warning text cannot drift from the PR title `_JUDGMENT_NOUN` names.
    assert "noun=prediction" not in run_block
    assert ".noun as $noun" in run_block


def test_the_reporting_steps_stay_job_level_so_cancellation_still_reports() -> None:
    """A cancelled or timed-out collect must still leave a trace.

    Job-level `always()` steps run on cancellation; a composite step's remaining
    inner steps are not guaranteed to. These three exist so a dead collect does
    not leave a silently orphaned trigger issue, so they belong in the caller.
    """
    for workflow in FAN_OUTS:
        steps = _steps(_collect_job(workflow))
        reporting = [
            s
            for s in steps
            if "post-issue-comment" in s.get("run", "") or "post-agent-feedback" in s.get("run", "")
        ]
        assert len(reporting) == 3, f"{workflow}: expected stall, secret-scan, and feedback steps"
        for step in reporting:
            assert "always()" in step["if"]
            # Least privilege: commenting triggers nothing, so issue-write stays
            # off the contents-write App token.
            assert step["env"]["GH_TOKEN"] == "${{ github.token }}"

    action_body = COLLECT_ACTION.read_text()
    for poster in ("post-issue-comment", "post-agent-feedback"):
        assert poster not in action_body, (
            "a reporting step moved into the composite; it would stop firing on cancellation"
        )


def test_the_artifact_name_derivation_matches_what_the_cells_upload() -> None:
    """`cell_artifact_name` rebuilds a cell's artifact name to tell a
    transfer-lost cell from one that never uploaded. The upload name is a
    workflow expression and cannot call the helper, so the coupling is real and
    checked here rather than left to drift into a silent misclassification."""
    for workflow, role in FAN_OUTS.items():
        body = (WORKFLOWS / workflow).read_text()
        actor_key = "predictor_id" if role == "predict" else "evaluator_id"
        expected = (
            f"name: {role}-${{{{ matrix.{actor_key} }}}}-${{{{ matrix.court }}}}"
            f"-${{{{ matrix.docket }}}}-${{{{ matrix.event_id }}}}"
        )
        assert expected in body, (
            f"{workflow}'s upload name no longer matches cell_artifact_name's "
            "reconstruction; a lost cell would be misreported as never-uploaded"
        )

    # And the helper agrees with that template for both roles.
    assert (
        cell_artifact_name(
            FinalizeRole.predict,
            ExpectedCell(actor="p", court="scotus", docket=7, event_id="evt-x"),
        )
        == "predict-p-scotus-7-evt-x"
    )
    assert (
        cell_artifact_name(
            FinalizeRole.evaluate, ExpectedCell(actor="e", court="ca9", docket=3, event_id="evt-y")
        )
        == "evaluate-e-ca9-3-evt-y"
    )


def test_the_plan_matrix_is_threaded_into_collect() -> None:
    """Without it, a queued cell that uploaded nothing is indistinguishable from
    one that was never queued."""
    for workflow in FAN_OUTS:
        call = next(
            s for s in _steps(_collect_job(workflow)) if s.get("uses", "").endswith("collect-run")
        )
        assert call["with"]["matrix"] == "${{ needs.plan.outputs.matrix }}"

    aggregate = next(
        s for s in _load(COLLECT_ACTION)["runs"]["steps"] if s["name"].startswith("Aggregate")
    )
    # Via env, never interpolated into the shell body: the matrix carries ids
    # parsed from the trigger issue.
    assert aggregate["env"]["PLAN_MATRIX"] == "${{ inputs.matrix }}"
    assert "${{ inputs.matrix }}" not in aggregate["run"]
    assert "--matrix-file" in aggregate["run"]


def test_the_run_pr_loop_is_safe_to_repeat() -> None:
    """`gh run rerun --failed` is the documented recovery for a transfer failure
    — A3's own PR notes tell operators to use it — so the loop that pushes and
    opens the run PR has to be repeatable. Each of these aborts the step under
    `set -euo pipefail` on a second attempt if dropped."""
    aggregate = next(
        s for s in _load(COLLECT_ACTION)["runs"]["steps"] if s["name"].startswith("Aggregate")
    )
    body = aggregate["run"]

    # A plain push non-fast-forward rejects against the prior attempt's branch.
    assert "push --force" in body
    # But force must never touch settled work, so a merged PR short-circuits.
    assert "--state merged" in body
    # `gh pr create` errors on an existing open PR for the same head.
    assert "--state open" in body and "gh pr edit" in body
    # A rerun that clears an earlier gate must promote the draft, or the run's
    # output stays a draft forever and never merges.
    assert "gh pr ready" in body


def test_the_trigger_issue_reports_are_marker_deduped() -> None:
    """Both reports are posted by steps that rerun with the job, so a plain
    comment would stack one copy per recovery attempt."""
    for workflow in FAN_OUTS:
        body = (WORKFLOWS / workflow).read_text()
        assert body.count("post-issue-comment") == 2, f"{workflow}: stall and secret-scan"
        assert "<!-- collect-stall: ${GITHUB_RUN_ID} -->" in body
        assert "<!-- collect-secret-scan: ${GITHUB_RUN_ID} -->" in body
        # The old unconditional form must not come back.
        assert "gh issue comment" not in body


def test_a_rerun_cannot_race_the_first_attempt_on_the_same_branch() -> None:
    """Force-push turns a concurrent second attempt from a reject into a silent
    clobber, so the two are serialized. Keyed on the run, so it never blocks a
    different run's collect."""
    for workflow in FAN_OUTS:
        concurrency = _collect_job(workflow)["concurrency"]
        assert "github.run_id" in concurrency["group"]
        assert concurrency["cancel-in-progress"] is False
