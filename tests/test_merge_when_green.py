"""The unattended data-lane merge, driven against a stand-in for `gh`.

`scripts/merge-when-green.sh` lands the collect and big-case-board PRs because
armed auto-merge never exercises the dev App's approval bypass. Its contract is
mostly about when it does *not* merge — a moved head, a failed check, a refusal
nothing is still running to clear, a deadline — so each of those is driven
here, along with the merge itself: pinned to the pushed commit, retried while
the platform refuses it with checks still running, and the check-run read sent
with the checks token rather than the App's.

The stand-in answers each endpoint from a per-test script of responses (the
last one repeats) and logs every call, so a test asserts both what the script
concluded and what it asked the API to do.
"""

import json
import os
import stat
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "merge-when-green.sh"
SHA = "a" * 40
OTHER_SHA = "b" * 40

FAKE_GH = r"""#!/usr/bin/env python3
import json, os, subprocess, sys
args = sys.argv[1:]
state_dir = os.environ["FAKE_GH_DIR"]
scenario = json.load(open(os.path.join(state_dir, "scenario.json")))
if args[:1] != ["api"]:
    sys.exit(f"unexpected gh call {args}")
method = args[args.index("-X") + 1] if "-X" in args else "GET"
path = next(a for a in args[1:] if a.startswith("repos/"))
if method == "PUT" and path.endswith("/merge"):
    kind = "merge"
elif "/check-runs" in path:
    kind = "checks"
elif "/pulls/" in path:
    kind = "pull"
else:
    sys.exit(f"unexpected path {path}")
with open(os.path.join(state_dir, "calls.jsonl"), "a") as log:
    log.write(json.dumps({"kind": kind, "args": args,
                          "token": os.environ.get("GH_TOKEN", "")}) + "\n")
counter = os.path.join(state_dir, f"{kind}.n")
n = int(open(counter).read()) if os.path.exists(counter) else 0
open(counter, "w").write(str(n + 1))
responses = scenario[kind]
resp = responses[min(n, len(responses) - 1)]
if "error" in resp:
    sys.stderr.write(resp["error"] + "\n")
    sys.exit(1)
# The script's own --jq filter runs over the API's JSON, as gh would run it, so
# the classification the filters do is exercised rather than stubbed.
body = json.dumps(resp["json"])
if "--jq" in args:
    flt = args[args.index("--jq") + 1]
    out = subprocess.run(["jq", "-r", flt], input=body, capture_output=True,
                         text=True, check=True).stdout
    sys.stdout.write(out)
else:
    sys.stdout.write(body + "\n")
"""


def _pull(
    state: str = "open",
    merged: bool = False,
    head: str = SHA,
    base: str = "main",
    head_repo: str | None = "owner/repo",
) -> dict[str, Any]:
    return {
        "json": {
            "state": state,
            "merged": merged,
            "head": {"sha": head, "repo": {"full_name": head_repo} if head_repo else None},
            "base": {"ref": base},
        }
    }


def _run_of(
    name: str, status: str = "completed", conclusion: str | None = "success", id_: int = 1
) -> dict[str, Any]:
    return {"name": name, "status": status, "conclusion": conclusion, "id": id_}


def _checks(*runs: dict[str, Any]) -> dict[str, Any]:
    return {"json": {"total_count": len(runs), "check_runs": list(runs)}}


GREEN = _checks(_run_of("gate"), _run_of("paths"), _run_of("analyze (python)"))
RUNNING = _checks(_run_of("gate", "in_progress", None), _run_of("paths"))
REFUSED = {"error": 'gh: Required status check "gate" is expected. (HTTP 405)'}
MERGED = {"json": {"sha": "c" * 40, "merged": True}}


def _run(
    tmp_path: Path,
    scenario: dict[str, list[dict[str, Any]]],
    *args: str,
    wait_s: str = "60",
    extra_env: dict[str, str] | None = None,
) -> tuple[subprocess.CompletedProcess[str], list[dict[str, Any]], str]:
    fake_dir = tmp_path / "fake"
    fake_dir.mkdir()
    gh = fake_dir / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    (fake_dir / "scenario.json").write_text(json.dumps(scenario))
    summary = tmp_path / "summary.md"
    env = {
        "PATH": f"{fake_dir}{os.pathsep}{os.environ['PATH']}",
        "FAKE_GH_DIR": str(fake_dir),
        "GH_TOKEN": "app-token",
        "CHECKS_TOKEN": "checks-token",
        "REPO": "owner/repo",
        "MERGE_WAIT_SECONDS": wait_s,
        "MERGE_POLL_SECONDS": "0",
        "GITHUB_STEP_SUMMARY": str(summary),
        **(extra_env or {}),
    }
    proc = subprocess.run(
        ["bash", str(SCRIPT), *(args or ("17", SHA))],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    log = fake_dir / "calls.jsonl"
    calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    return proc, calls, summary.read_text() if summary.exists() else ""


def _merges(calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [c for c in calls if c["kind"] == "merge"]


def test_merges_once_every_check_concluded_pinned_to_the_pushed_commit(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path,
        {"pull": [_pull()], "checks": [RUNNING, RUNNING, GREEN], "merge": [MERGED]},
    )
    assert proc.returncode == 0, proc.stderr
    merges = _merges(calls)
    # Not asked while a check was still running.
    assert len(merges) == 1
    assert "sha=" + SHA in merges[0]["args"]
    assert "merge_method=squash" in merges[0]["args"]
    assert merges[0]["token"] == "app-token"
    assert "Merged" in summary


def test_a_refusal_with_every_check_green_is_retried_once(tmp_path: Path) -> None:
    proc, calls, _ = _run(
        tmp_path, {"pull": [_pull()], "checks": [GREEN], "merge": [REFUSED, MERGED]}
    )
    assert proc.returncode == 0
    assert len(_merges(calls)) == 2


def test_check_runs_are_read_with_the_checks_token(tmp_path: Path) -> None:
    _, calls, _ = _run(tmp_path, {"pull": [_pull()], "checks": [GREEN], "merge": [MERGED]})
    assert [c["token"] for c in calls if c["kind"] == "checks"] == ["checks-token"]
    assert {c["token"] for c in calls if c["kind"] != "checks"} == {"app-token"}


def test_an_already_merged_pr_is_left_alone(tmp_path: Path) -> None:
    proc, calls, _ = _run(
        tmp_path,
        {"pull": [_pull(state="closed", merged=True)], "checks": [GREEN], "merge": [MERGED]},
    )
    assert proc.returncode == 0
    assert _merges(calls) == []


def test_a_closed_unmerged_pr_is_not_merged(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path, {"pull": [_pull(state="closed")], "checks": [GREEN], "merge": [MERGED]}
    )
    assert proc.returncode == 0
    assert _merges(calls) == []
    assert "closed unmerged" in summary


def test_a_pr_into_another_base_is_never_merged(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path, {"pull": [_pull(base="staging")], "checks": [GREEN], "merge": [MERGED]}
    )
    assert proc.returncode == 0
    assert _merges(calls) == []
    assert "not a owner/repo branch into main" in summary


def test_a_fork_head_is_never_merged(tmp_path: Path) -> None:
    for head_repo in ("someone/fork", None):
        sub = tmp_path / str(head_repo).replace("/", "_")
        sub.mkdir()
        proc, calls, _ = _run(
            sub, {"pull": [_pull(head_repo=head_repo)], "checks": [GREEN], "merge": [MERGED]}
        )
        assert proc.returncode == 0
        assert _merges(calls) == [], head_repo


def test_a_moved_head_is_left_for_review(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path, {"pull": [_pull(head=OTHER_SHA)], "checks": [GREEN], "merge": [MERGED]}
    )
    assert proc.returncode == 0
    assert _merges(calls) == []
    assert "head moved" in summary


def test_a_failed_check_stops_the_merge_required_or_not(tmp_path: Path) -> None:
    for failing in ("gate", "analyze (python)"):
        sub = tmp_path / failing.replace(" ", "_").strip("()")
        sub.mkdir()
        runs = _checks(
            _run_of("gate", conclusion="failure" if failing == "gate" else "success"),
            _run_of("paths"),
            _run_of("analyze (python)", conclusion="failure" if failing != "gate" else "success"),
        )
        proc, calls, summary = _run(sub, {"pull": [_pull()], "checks": [runs], "merge": [MERGED]})
        assert proc.returncode == 0
        assert _merges(calls) == []
        assert f"failed checks ({failing})" in summary


def test_a_superseded_cancelled_run_is_not_a_failure(tmp_path: Path) -> None:
    """`ci.yml` cancels a superseded run of the same ref, and the call sites'
    force-push and body edit fire two runs on one head: the newest run per
    name is the one that counts."""
    runs = _checks(
        _run_of("gate", conclusion="cancelled", id_=1),
        _run_of("gate", conclusion="success", id_=2),
        _run_of("paths"),
    )
    proc, calls, _ = _run(tmp_path, {"pull": [_pull()], "checks": [runs], "merge": [MERGED]})
    assert proc.returncode == 0, proc.stderr
    assert len(_merges(calls)) == 1


def test_a_newest_cancelled_run_is_waited_on_not_failed(tmp_path: Path) -> None:
    cancelled = _checks(_run_of("gate", conclusion="cancelled"), _run_of("paths"))
    proc, calls, summary = _run(
        tmp_path,
        {"pull": [_pull()], "checks": [cancelled, cancelled, GREEN], "merge": [MERGED]},
    )
    assert proc.returncode == 0
    assert len(_merges(calls)) == 1
    assert "failed checks" not in summary


def test_no_merge_is_asked_before_the_required_checks_report(tmp_path: Path) -> None:
    """A head with no check runs yet — or only some — looks quiet, but the
    required checks are still to come."""
    early = _checks(_run_of("paths"))
    proc, calls, summary = _run(
        tmp_path,
        {"pull": [_pull()], "checks": [_checks(), early], "merge": [MERGED]},
        wait_s="0",
    )
    assert proc.returncode == 0
    assert _merges(calls) == []
    assert "checks still running" in summary


def test_a_refusal_with_every_check_concluded_gives_up_with_the_platform_message(
    tmp_path: Path,
) -> None:
    approval = {"error": "gh: At least 1 approving review is required. (HTTP 405)"}
    proc, calls, summary = _run(
        tmp_path, {"pull": [_pull()], "checks": [GREEN], "merge": [approval]}
    )
    assert proc.returncode == 0
    assert len(_merges(calls)) == 2
    assert "approving review is required" in summary
    assert "every check concluded" in summary


def test_a_settled_refusal_resets_when_a_check_starts(tmp_path: Path) -> None:
    proc, calls, _ = _run(
        tmp_path,
        {
            "pull": [_pull()],
            "checks": [GREEN, RUNNING, GREEN, GREEN],
            "merge": [REFUSED, REFUSED, MERGED],
        },
    )
    assert proc.returncode == 0
    assert len(_merges(calls)) == 3


def test_the_deadline_bounds_the_wait(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path, {"pull": [_pull()], "checks": [RUNNING], "merge": [MERGED]}, wait_s="0"
    )
    assert proc.returncode == 0
    assert _merges(calls) == []
    assert "not merged within 0s" in summary


def test_a_failed_read_is_retried_not_read_as_closed(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path,
        {"pull": [{"error": "gh: HTTP 502"}, _pull()], "checks": [GREEN], "merge": [MERGED]},
    )
    assert proc.returncode == 0, proc.stderr
    assert len(_merges(calls)) == 1
    assert "closed unmerged" not in summary


def test_bad_arguments_and_a_missing_checks_token_are_refused_before_any_call(
    tmp_path: Path,
) -> None:
    cases: list[tuple[tuple[str, ...], dict[str, str]]] = [
        (("17",), {}),
        (("pr-17", SHA), {}),
        (("17", "abc"), {}),
        (("17", SHA.upper()), {}),
        (("17", SHA), {"CHECKS_TOKEN": ""}),
    ]
    for i, (args, extra) in enumerate(cases):
        sub = tmp_path / str(i)
        sub.mkdir()
        proc, calls, _ = _run(
            sub, {"pull": [_pull()], "checks": [GREEN], "merge": [MERGED]}, *args, extra_env=extra
        )
        assert proc.returncode != 0, args
        assert calls == []
