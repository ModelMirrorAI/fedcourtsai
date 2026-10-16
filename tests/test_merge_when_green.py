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
import json, os, sys
args = sys.argv[1:]
state_dir = os.environ["FAKE_GH_DIR"]
scenario = json.load(open(os.path.join(state_dir, "scenario.json")))
if args[:1] != ["api"]:
    sys.exit(f"unexpected gh call {args}")
method = "GET"
if "-X" in args:
    method = args[args.index("-X") + 1]
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
if resp.get("rc", 0):
    sys.stderr.write(resp.get("out", "") + "\n")
    sys.exit(resp["rc"])
sys.stdout.write(resp.get("out", "") + "\n")
"""


def _pull(state: str = "open", merged: bool = False, head: str = SHA) -> dict[str, Any]:
    return {"out": f"{state}\t{str(merged).lower()}\t{head}"}


def _checks(pending: int = 0, failed: str = "") -> dict[str, Any]:
    return {"out": f"{pending}\t{failed}"}


REFUSED = {"rc": 1, "out": 'gh: Required status check "gate" is expected. (HTTP 405)'}
MERGED = {"out": "c" * 40}


def _run(
    tmp_path: Path,
    scenario: dict[str, list[dict[str, Any]]],
    *args: str,
    wait_s: str = "60",
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


def test_merges_once_checks_clear_pinned_to_the_pushed_commit(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path,
        {
            "pull": [_pull()],
            "checks": [_checks(pending=2), _checks(pending=1), _checks()],
            "merge": [REFUSED, REFUSED, MERGED],
        },
    )
    assert proc.returncode == 0, proc.stderr
    merges = _merges(calls)
    assert len(merges) == 3
    assert all("sha=" + SHA in m["args"] for m in merges)
    assert all("merge_method=squash" in m["args"] for m in merges)
    assert all(m["token"] == "app-token" for m in merges)
    assert "Merged" in summary


def test_check_runs_are_read_with_the_checks_token(tmp_path: Path) -> None:
    _, calls, _ = _run(tmp_path, {"pull": [_pull()], "checks": [_checks()], "merge": [MERGED]})
    assert [c["token"] for c in calls if c["kind"] == "checks"] == ["checks-token"]
    assert {c["token"] for c in calls if c["kind"] != "checks"} == {"app-token"}


def test_an_already_merged_pr_is_left_alone(tmp_path: Path) -> None:
    proc, calls, _ = _run(
        tmp_path,
        {"pull": [_pull(state="closed", merged=True)], "checks": [_checks()], "merge": [MERGED]},
    )
    assert proc.returncode == 0
    assert _merges(calls) == []


def test_a_closed_unmerged_pr_is_not_merged(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path, {"pull": [_pull(state="closed")], "checks": [_checks()], "merge": [MERGED]}
    )
    assert proc.returncode == 0
    assert _merges(calls) == []
    assert "closed unmerged" in summary


def test_a_moved_head_is_left_for_review(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path, {"pull": [_pull(head=OTHER_SHA)], "checks": [_checks()], "merge": [MERGED]}
    )
    assert proc.returncode == 0
    assert _merges(calls) == []
    assert "head moved" in summary


def test_a_failed_check_stops_the_merge(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path,
        {"pull": [_pull()], "checks": [_checks(pending=1, failed="gate")], "merge": [MERGED]},
    )
    assert proc.returncode == 0
    assert _merges(calls) == []
    assert "failed checks (gate)" in summary


def test_a_refusal_with_nothing_running_gives_up_with_the_platform_message(
    tmp_path: Path,
) -> None:
    approval = {"rc": 1, "out": "gh: At least 1 approving review is required. (HTTP 405)"}
    proc, calls, summary = _run(
        tmp_path, {"pull": [_pull()], "checks": [_checks()], "merge": [approval]}
    )
    assert proc.returncode == 0
    # Twice, so a check run that has not been created yet cannot pass for a
    # settled head.
    assert len(_merges(calls)) == 2
    assert "approving review is required" in summary
    assert "no check still running" in summary


def test_a_settled_refusal_resets_when_a_check_starts(tmp_path: Path) -> None:
    proc, calls, _ = _run(
        tmp_path,
        {
            "pull": [_pull()],
            "checks": [_checks(), _checks(pending=1), _checks(), _checks()],
            "merge": [REFUSED, REFUSED, REFUSED, MERGED],
        },
    )
    assert proc.returncode == 0
    assert len(_merges(calls)) == 4


def test_the_deadline_bounds_the_wait(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path,
        {"pull": [_pull()], "checks": [_checks(pending=1)], "merge": [REFUSED]},
        wait_s="0",
    )
    assert proc.returncode == 0
    assert len(_merges(calls)) == 1
    assert "auto-merge stays armed" in summary


def test_a_failed_read_is_retried_not_read_as_closed(tmp_path: Path) -> None:
    proc, calls, summary = _run(
        tmp_path,
        {
            "pull": [{"rc": 1, "out": "gh: HTTP 502"}, _pull()],
            "checks": [_checks()],
            "merge": [MERGED],
        },
    )
    assert proc.returncode == 0, proc.stderr
    assert len(_merges(calls)) == 1
    assert "closed unmerged" not in summary


def test_bad_arguments_are_refused_before_any_call(tmp_path: Path) -> None:
    for args in (("17",), ("pr-17", SHA), ("17", "abc"), ("17", SHA.upper())):
        sub = tmp_path / str(abs(hash(args)))
        sub.mkdir()
        proc, calls, _ = _run(
            sub, {"pull": [_pull()], "checks": [_checks()], "merge": [MERGED]}, *args
        )
        assert proc.returncode == 2, args
        assert calls == []
