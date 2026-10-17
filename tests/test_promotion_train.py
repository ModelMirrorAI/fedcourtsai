"""The promotion train's decision (:mod:`fedcourtsai.promotion_train`): one step
per tick, from what the workflow read, every branch of it fail-closed."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.promotion_train import (
    GATE_TITLE,
    OFFLINE_GATE_TITLE,
    READY_MARKER,
    WAIVER_LABEL,
    Observed,
    TrainAction,
    TrainConfig,
    TrainConfigError,
    decide,
    is_train_branch,
    load_train_config,
    next_branch_name,
)

ROOT = Path(__file__).resolve().parent.parent
REPO = "owner/repo"
STAGING = "a" * 40
HEAD = "c" * 40
OLD = "e" * 40
REF = "promote/2026-10-17"
NOW = datetime(2026, 10, 17, 5, 26, tzinfo=UTC)
MAINTAINER = "maintainer"
CONFIG = TrainConfig(
    approvers=(MAINTAINER,), required_checks=("gate", "paths", "promotion-gate", "main-base")
)


def _pull(
    *,
    number: int = 50,
    head: str = REF,
    sha: str = HEAD,
    draft: bool = True,
    repo: str = REPO,
    body: str = "",
    labels: tuple[str, ...] = (),
    state: str = "open",
) -> dict[str, Any]:
    return {
        "number": number,
        "state": state,
        "draft": draft,
        "body": body,
        "labels": [{"name": name} for name in labels],
        "base": {"ref": "main"},
        "head": {"ref": head, "sha": sha, "repo": {"full_name": repo}},
    }


def _run(
    title: str = GATE_TITLE,
    *,
    status: str = "completed",
    conclusion: str | None = "success",
    sha: str = HEAD,
    branch: str = REF,
    event: str = "workflow_dispatch",
    run_id: int = 900,
) -> dict[str, Any]:
    return {
        "id": run_id,
        "display_title": title,
        "status": status,
        "conclusion": conclusion,
        "head_sha": sha,
        "head_branch": branch,
        "event": event,
        "html_url": f"https://example.invalid/runs/{run_id}",
    }


def _review(
    state: str, *, login: str = MAINTAINER, sha: str = HEAD, at: str = "2026-10-17T06:00:00Z"
) -> dict[str, Any]:
    return {"state": state, "user": {"login": login}, "commit_id": sha, "submitted_at": at}


def _check(name: str, conclusion: str | None = "success", *, run_id: int = 1, **kw: Any) -> Any:
    return {
        "id": run_id,
        "name": name,
        "status": kw.get("status", "completed"),
        "conclusion": conclusion,
        "app": {"slug": kw.get("app", "github-actions")},
    }


GREEN = [
    _check("gate"),
    _check("paths"),
    _check("promotion-gate"),
    _check("main-base", "skipped"),
]


def _no_candidate(**overrides: Any) -> Observed:
    observed = Observed(
        repo=REPO,
        now=NOW,
        open_pulls=[],
        branches=[],
        staging_sha=STAGING,
        staging_contains_main=True,
        staging_differs_from_main=True,
    )
    return replace(observed, **overrides)


def _ready(**overrides: Any) -> Observed:
    """A ready candidate with every merge condition holding."""
    observed = Observed(
        repo=REPO,
        now=NOW,
        open_pulls=[_pull(draft=False, body=f"x\n{READY_MARKER}")],
        head_on_staging=True,
        runs=[_run()],
        reviews=[_review("APPROVED")],
        check_runs=GREEN,
        quiescent=True,
        registry_ok=True,
    )
    return replace(observed, **overrides)


# --- Cutting a candidate ------------------------------------------------------


def test_with_nothing_open_the_train_cuts_at_the_staging_tip() -> None:
    step = decide(_no_candidate(), CONFIG)
    assert step.action is TrainAction.CUT
    assert step.branch == "promote/2026-10-17"
    assert step.sha == STAGING


def test_a_taken_date_gets_the_next_free_suffix() -> None:
    step = decide(_no_candidate(branches=[(REF, OLD), (f"{REF}-2", OLD)]), CONFIG)
    assert step.action is TrainAction.CUT
    assert step.branch == f"{REF}-3"
    assert next_branch_name(NOW, []) == REF
    assert next_branch_name(NOW, [REF]) == f"{REF}-2"
    assert next_branch_name(NOW, ["promote/2026-10-16", f"{REF}-2"]) == REF


def test_an_unsynced_staging_waits_for_the_sync() -> None:
    step = decide(_no_candidate(staging_contains_main=False), CONFIG)
    assert step.action is TrainAction.WAIT
    assert "sync" in step.reason


def test_a_staging_that_carries_nothing_cuts_nothing() -> None:
    """A sync merge alone makes staging 'ahead' of main by a commit; the tree is
    what says whether there is anything to promote."""
    step = decide(_no_candidate(staging_differs_from_main=False), CONFIG)
    assert step.action is TrainAction.WAIT


@pytest.mark.parametrize(
    "unread",
    [
        {"open_pulls": None},
        {"branches": None},
        {"staging_contains_main": None},
        {"staging_differs_from_main": None},
        {"staging_sha": None},
        {"staging_sha": "not-a-sha"},
    ],
)
def test_an_unread_fact_never_cuts(unread: dict[str, Any]) -> None:
    assert decide(_no_candidate(**unread), CONFIG).action is TrainAction.WAIT


def test_a_closed_candidate_is_not_re_cut_at_the_same_tip() -> None:
    """Branches are never deleted, so one at the tip with no open PR is a
    candidate closed unmerged (or one whose PR never opened)."""
    step = decide(_no_candidate(branches=[("promote/2026-10-16", STAGING)]), CONFIG)
    assert step.action is TrainAction.WAIT
    assert "promote/2026-10-16 already sits at staging" in step.reason


def test_a_closed_candidate_lets_the_next_cut_through_once_staging_moved() -> None:
    step = decide(_no_candidate(branches=[("promote/2026-10-16", OLD)]), CONFIG)
    assert step.action is TrainAction.CUT
    assert step.branch == REF


def test_an_open_candidate_means_no_second_cut() -> None:
    observed = _no_candidate(open_pulls=[_pull()])
    step = decide(observed, CONFIG)
    assert step.action is not TrainAction.CUT
    assert step.pr == 50


def test_a_hand_opened_staging_promotion_makes_the_train_stand_aside() -> None:
    observed = _no_candidate(open_pulls=[_pull(head="staging", number=7)])
    step = decide(observed, CONFIG)
    assert step.action is TrainAction.WAIT
    assert "#7" in step.reason


@pytest.mark.parametrize(
    "pulls",
    [
        [_pull(number=50), _pull(number=51, head=f"{REF}-2")],
        [_pull(head="promote/anything")],
        [_pull(head="promote/2026-10-17/x")],
    ],
)
def test_more_than_one_candidate_or_a_foreign_name_stands_aside(
    pulls: list[dict[str, Any]],
) -> None:
    step = decide(_no_candidate(open_pulls=pulls), CONFIG)
    assert step.action is TrainAction.WAIT
    assert "stands aside" in step.reason


def test_a_fork_branch_named_like_a_candidate_is_not_one() -> None:
    observed = _no_candidate(open_pulls=[_pull(repo="someone/fork")])
    assert decide(observed, CONFIG).action is TrainAction.CUT


def test_train_branch_names_are_whole_and_case_sensitive() -> None:
    assert is_train_branch(REF)
    assert is_train_branch(f"{REF}-12")
    for name in (
        "promote/2026-10-17-1",
        "promote/2026-10-17-0",
        "Promote/2026-10-17",
        "promote/2026-10-17x",
        "xpromote/2026-10-17",
        "staging",
    ):
        assert not is_train_branch(name), name


# --- The integration gate -----------------------------------------------------


def _draft(**overrides: Any) -> Observed:
    observed = Observed(
        repo=REPO,
        now=NOW,
        open_pulls=[_pull()],
        head_on_staging=True,
        runs=[],
        registry_ok=True,
    )
    return replace(observed, **overrides)


def test_a_candidate_with_no_gate_run_dispatches_one() -> None:
    step = decide(_draft(), CONFIG)
    assert step.action is TrainAction.DISPATCH_GATE
    assert (step.pr, step.ref, step.sha) == (50, REF, HEAD)
    assert f"--ref {REF} -f scenario=gate" in step.reason


@pytest.mark.parametrize("status", ["queued", "in_progress", "waiting", "pending", "requested"])
def test_a_gate_run_in_flight_is_waited_for_never_re_dispatched(status: str) -> None:
    step = decide(_draft(runs=[_run(status=status, conclusion=None)]), CONFIG)
    assert step.action is TrainAction.WAIT


@pytest.mark.parametrize("conclusion", ["failure", "cancelled", "timed_out"])
def test_a_failed_gate_is_reported_and_not_re_dispatched(conclusion: str) -> None:
    step = decide(_draft(runs=[_run(conclusion=conclusion, run_id=77)]), CONFIG)
    assert step.action is TrainAction.REPORT
    assert conclusion in step.reason
    assert "gh run rerun 77 --failed" in step.reason


def test_a_failed_then_re_run_gate_counts_as_green() -> None:
    """A maintainer re-run turns the same run green in place."""
    runs = [_run(conclusion="failure", run_id=1), _run(run_id=2)]
    assert decide(_draft(runs=runs), CONFIG).action is TrainAction.MARK_READY


@pytest.mark.parametrize(
    "run",
    [
        _run(sha=OLD),
        _run(branch="staging"),
        _run(event="schedule"),
        _run(title="integration-test: all @ staging"),
        _run(title=OFFLINE_GATE_TITLE),
        _run(title="integration-test: gate @ prod"),
    ],
)
def test_runs_that_are_not_this_heads_gate_are_not_evidence(run: dict[str, Any]) -> None:
    """Another sha, another ref, a non-dispatch, a superset suite, the token-free
    suite without the waiver, or another environment: none counts, so the gate
    is dispatched as if none ran."""
    assert decide(_draft(runs=[run]), CONFIG).action is TrainAction.DISPATCH_GATE


def test_the_waiver_label_accepts_an_offline_gate_run() -> None:
    observed = _draft(
        open_pulls=[_pull(labels=(WAIVER_LABEL,))], runs=[_run(title=OFFLINE_GATE_TITLE)]
    )
    assert decide(observed, CONFIG).action is TrainAction.MARK_READY


def test_a_refused_registry_is_reported_before_any_spend() -> None:
    step = decide(_draft(registry_ok=False), CONFIG)
    assert step.action is TrainAction.REPORT
    assert "registry" in step.reason
    assert decide(_draft(registry_ok=None), CONFIG).action is TrainAction.WAIT


def test_a_head_off_stagings_first_parent_chain_is_never_acted_on() -> None:
    step = decide(_draft(head_on_staging=False), CONFIG)
    assert step.action is TrainAction.REPORT
    assert decide(_draft(head_on_staging=None), CONFIG).action is TrainAction.WAIT
    ready = _ready(head_on_staging=False)
    assert decide(ready, CONFIG).action is TrainAction.REPORT


def test_unread_runs_wait() -> None:
    assert decide(_draft(runs=None), CONFIG).action is TrainAction.WAIT


# --- Ready for review ---------------------------------------------------------


def test_a_green_gate_marks_the_draft_ready() -> None:
    step = decide(_draft(runs=[_run()]), CONFIG)
    assert step.action is TrainAction.MARK_READY
    assert step.reviewers == (MAINTAINER,)


def test_a_draft_the_train_already_marked_ready_is_left_a_draft() -> None:
    """A maintainer returning the candidate to draft is a decision the train keeps."""
    observed = _draft(open_pulls=[_pull(body=f"prose\n{READY_MARKER}")], runs=[_run()])
    step = decide(observed, CONFIG)
    assert step.action is TrainAction.WAIT
    assert "draft" in step.reason


# --- Approval and merge -------------------------------------------------------


def test_every_condition_holding_merges() -> None:
    step = decide(_ready(), CONFIG)
    assert step.action is TrainAction.MERGE
    assert (step.pr, step.sha) == (50, HEAD)


def test_no_approval_waits_for_the_maintainer() -> None:
    step = decide(_ready(reviews=[]), CONFIG)
    assert step.action is TrainAction.WAIT
    assert "awaiting approval" in step.reason


def test_an_approval_of_an_older_head_is_stale() -> None:
    step = decide(_ready(reviews=[_review("APPROVED", sha=OLD)]), CONFIG)
    assert step.action is TrainAction.WAIT
    assert "stale approval" in step.reason


def test_an_approval_by_someone_not_listed_does_not_count() -> None:
    reviews = [_review("APPROVED", login="modelmirror-agent")]
    assert decide(_ready(reviews=reviews), CONFIG).action is TrainAction.WAIT


def test_logins_compare_case_insensitively() -> None:
    reviews = [_review("APPROVED", login=MAINTAINER.upper())]
    assert decide(_ready(reviews=reviews), CONFIG).action is TrainAction.MERGE


def test_changes_requested_after_the_approval_blocks_the_merge() -> None:
    reviews = [
        _review("APPROVED", at="2026-10-17T06:00:00Z"),
        _review("CHANGES_REQUESTED", login="someone", at="2026-10-17T07:00:00Z"),
    ]
    step = decide(_ready(reviews=reviews), CONFIG)
    assert step.action is TrainAction.REPORT
    assert "changes requested by someone" in step.reason


def test_the_approvers_own_later_change_request_replaces_their_approval() -> None:
    reviews = [
        _review("CHANGES_REQUESTED", at="2026-10-17T07:00:00Z"),
        _review("APPROVED", at="2026-10-17T06:00:00Z"),
    ]
    assert decide(_ready(reviews=reviews), CONFIG).action is TrainAction.REPORT


def test_an_approval_after_a_change_request_clears_it() -> None:
    reviews = [
        _review("CHANGES_REQUESTED", at="2026-10-17T06:00:00Z"),
        _review("COMMENTED", at="2026-10-17T06:30:00Z"),
        _review("APPROVED", at="2026-10-17T07:00:00Z"),
    ]
    assert decide(_ready(reviews=reviews), CONFIG).action is TrainAction.MERGE


def test_a_dismissed_approval_does_not_count() -> None:
    reviews = [
        _review("APPROVED", at="2026-10-17T06:00:00Z"),
        _review("DISMISSED", at="2026-10-17T07:00:00Z"),
    ]
    assert decide(_ready(reviews=reviews), CONFIG).action is TrainAction.WAIT


@pytest.mark.parametrize("quiescent", [False, None])
def test_a_round_in_flight_waits_and_retries_next_tick(quiescent: bool | None) -> None:
    step = decide(_ready(quiescent=quiescent), CONFIG)
    assert step.action is TrainAction.WAIT
    assert "in flight" in step.reason


def test_a_registry_refusal_at_merge_time_is_reported() -> None:
    assert decide(_ready(registry_ok=False), CONFIG).action is TrainAction.REPORT
    assert decide(_ready(registry_ok=None), CONFIG).action is TrainAction.WAIT


def test_pending_required_checks_wait() -> None:
    checks = [*GREEN[:3], _check("main-base", None, status="in_progress")]
    assert decide(_ready(check_runs=checks), CONFIG).action is TrainAction.WAIT
    assert decide(_ready(check_runs=None), CONFIG).action is TrainAction.WAIT


def test_a_red_promotion_gate_alone_is_re_fired() -> None:
    checks = [*GREEN[:2], _check("promotion-gate", "failure"), GREEN[3]]
    assert decide(_ready(check_runs=checks), CONFIG).action is TrainAction.REFIRE_GATE
    # Missing, or merely skipped, is not green for the gate either.
    assert decide(_ready(check_runs=[*GREEN[:2], GREEN[3]]), CONFIG).action is (
        TrainAction.REFIRE_GATE
    )
    skipped = [*GREEN[:2], _check("promotion-gate", "skipped"), GREEN[3]]
    assert decide(_ready(check_runs=skipped), CONFIG).action is TrainAction.REFIRE_GATE


def test_any_other_red_required_check_is_reported() -> None:
    checks = [_check("gate", "failure"), *GREEN[1:]]
    step = decide(_ready(check_runs=checks), CONFIG)
    assert step.action is TrainAction.REPORT
    assert "gate (failure)" in step.reason
    missing = decide(_ready(check_runs=GREEN[1:]), CONFIG)
    assert missing.action is TrainAction.REPORT


def test_the_newest_check_run_per_name_decides() -> None:
    checks = [
        _check("promotion-gate", "failure", run_id=1),
        _check("promotion-gate", "success", run_id=2),
        *[c for c in GREEN if c["name"] != "promotion-gate"],
    ]
    assert decide(_ready(check_runs=checks), CONFIG).action is TrainAction.MERGE
    checks[1]["id"], checks[0]["id"] = 1, 2
    assert decide(_ready(check_runs=checks), CONFIG).action is TrainAction.REFIRE_GATE


def test_a_check_run_from_another_app_is_not_counted() -> None:
    checks = [
        *[c for c in GREEN if c["name"] != "promotion-gate"],
        _check("promotion-gate", "success", app="some-other-app"),
    ]
    assert decide(_ready(check_runs=checks), CONFIG).action is TrainAction.REFIRE_GATE


# --- Configuration ------------------------------------------------------------


def test_the_committed_config_loads_and_requires_the_gate() -> None:
    config = load_train_config(ROOT / "config" / "promotion-train.yaml")
    assert config.approvers
    assert "promotion-gate" in config.required_checks
    assert not config.is_approver("modelmirror-agent")


@pytest.mark.parametrize(
    "text",
    [
        "approvers: []\nrequired_checks: [promotion-gate]\n",
        "approvers: [a]\nrequired_checks: [gate]\n",
        "approvers: ['not a login']\nrequired_checks: [promotion-gate]\n",
        "approvers: [a, A]\nrequired_checks: [promotion-gate]\n",
        "approvers: [a]\nrequired_checks: [promotion-gate]\nextra: 1\n",
        "- a list\n",
        "approvers: [x[bot]]\nrequired_checks: [promotion-gate]\n",
    ],
)
def test_a_malformed_config_refuses(tmp_path: Path, text: str) -> None:
    path = tmp_path / "train.yaml"
    path.write_text(text)
    with pytest.raises(TrainConfigError):
        load_train_config(path)


def test_a_missing_config_refuses(tmp_path: Path) -> None:
    with pytest.raises(TrainConfigError):
        load_train_config(tmp_path / "absent.yaml")


# --- The command line ---------------------------------------------------------


def _write(path: Path, value: object) -> str:
    path.write_text(json.dumps(value))
    return str(path)


def test_the_step_command_merges_a_candidate_that_holds(tmp_path: Path) -> None:
    args = [
        "promotion-train-step",
        "--repo",
        REPO,
        "--open-prs-file",
        _write(tmp_path / "open.json", [_pull(draft=False)]),
        "--head-on-staging",
        "yes",
        "--runs-file",
        _write(tmp_path / "runs.json", {"workflow_runs": [_run()]}),
        "--reviews-file",
        _write(tmp_path / "reviews.json", [_review("APPROVED")]),
        "--check-runs-file",
        _write(tmp_path / "checks.json", {"check_runs": GREEN}),
        "--quiescent",
        "yes",
        "--registry-ok",
        "yes",
        "--config",
        _write(
            tmp_path / "train.json",
            {"approvers": [MAINTAINER], "required_checks": list(CONFIG.required_checks)},
        ),
    ]
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0, result.output
    step = json.loads(result.output)
    assert step["action"] == "merge"
    assert step["sha"] == HEAD


def test_the_step_command_cuts_with_the_date_it_is_told(tmp_path: Path) -> None:
    branches = tmp_path / "branches.txt"
    branches.write_text(f"promote/2026-11-02 {OLD}\n")
    result = CliRunner().invoke(
        app,
        [
            "promotion-train-step",
            "--repo",
            REPO,
            "--open-prs-file",
            _write(tmp_path / "open.json", []),
            "--branches-file",
            str(branches),
            "--staging-sha",
            STAGING,
            "--staging-contains-main",
            "yes",
            "--staging-differs",
            "yes",
            "--now",
            "2026-11-02T03:26:00+00:00",
        ],
    )
    assert result.exit_code == 0, result.output
    step = json.loads(result.output)
    assert step["action"] == "cut"
    assert step["branch"] == "promote/2026-11-02-2"


def test_a_malformed_branches_file_is_unknown(tmp_path: Path) -> None:
    branches = tmp_path / "branches.txt"
    branches.write_text("promote/2026-11-02\n")
    result = CliRunner().invoke(
        app,
        [
            "promotion-train-step",
            "--repo",
            REPO,
            "--open-prs-file",
            _write(tmp_path / "open.json", []),
            "--branches-file",
            str(branches),
            "--staging-sha",
            STAGING,
            "--staging-contains-main",
            "yes",
            "--staging-differs",
            "yes",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["action"] == "wait"


def test_the_step_command_treats_a_missing_file_as_unknown(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "promotion-train-step",
            "--repo",
            REPO,
            "--open-prs-file",
            str(tmp_path / "absent.json"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["action"] == "wait"


def test_the_candidate_command_names_the_one_candidate(tmp_path: Path) -> None:
    def run(pulls: list[dict[str, Any]]) -> Any:
        result = CliRunner().invoke(
            app,
            [
                "promotion-train-candidate",
                "--repo",
                REPO,
                "--open-prs-file",
                _write(tmp_path / "open.json", pulls),
            ],
        )
        assert result.exit_code == 0, result.output
        return json.loads(result.output)

    assert run([_pull()]) == {"number": 50, "ref": REF, "sha": HEAD}
    assert run([]) == {}
    assert run([_pull(), _pull(number=51, head=f"{REF}-2")]) == {}
    assert run([_pull(head="staging")]) == {}


def test_the_approval_command_exits_zero_only_at_the_head(tmp_path: Path) -> None:
    config = _write(
        tmp_path / "train.json",
        {"approvers": [MAINTAINER], "required_checks": ["promotion-gate"]},
    )

    def code(reviews: list[dict[str, Any]], head: str = HEAD) -> int:
        result = CliRunner().invoke(
            app,
            [
                "promotion-train-approval",
                "--reviews-file",
                _write(tmp_path / "reviews.json", reviews),
                "--head-sha",
                head,
                "--config",
                config,
            ],
        )
        return result.exit_code

    assert code([_review("APPROVED")]) == 0
    assert code([_review("APPROVED")], head=OLD) == 1
    assert code([]) == 1
    assert code([_review("APPROVED"), _review("CHANGES_REQUESTED", login="x", at="z")]) == 1
    unreadable = CliRunner().invoke(
        app,
        [
            "promotion-train-approval",
            "--reviews-file",
            str(tmp_path / "absent.json"),
            "--head-sha",
            HEAD,
            "--config",
            config,
        ],
    )
    assert unreadable.exit_code == 1
