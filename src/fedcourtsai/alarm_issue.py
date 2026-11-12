"""One long-lived alarm issue per check: opened on an alarm, closed on a clean read.

Each scheduled check that can find a hole keeps exactly one issue, under its own
non-triggering label, so that an open issue under the label means the hole
stands. `latch_issue` is the whole state machine: an alarming read opens the
issue or rewrites the open one's body in place, so a standing failure stays on
one thread; a clean read comments on the open issue and closes it; a clean
read with none open writes nothing.

Only an issue the workflow token opened under the check's title is the alarm:
a label can be put on any issue by anyone who can triage, and such an issue
decides nothing here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .agent_feedback import GhRunner, _gh

# The ambient workflow token's login: the only author whose issue is an alarm.
ALARM_AUTHOR: Final = "github-actions[bot]"


@dataclass(frozen=True)
class AlarmIssue:
    """What names one check's alarm issue: its title and its label."""

    title: str
    label: str
    label_description: str
    label_color: str = "b60205"


def open_alarm_issues(repo: str, spec: AlarmIssue, runner: GhRunner) -> list[int]:
    """Every open alarm issue for ``spec``: its title, opened by the workflow token.

    One in the ordinary case. A create that lands and is then cut at its
    timeout is re-sent by the runner's retry, so there can be two, and a clean
    read has to close both for an open issue to keep meaning a hole.
    """
    listing = json.loads(
        runner(["gh", "api", f"repos/{repo}/issues?labels={spec.label}&state=open&per_page=100"])
        or "[]"
    )
    found: list[int] = []
    for issue in listing if isinstance(listing, list) else []:
        if not isinstance(issue, dict) or "pull_request" in issue:
            continue
        user = issue.get("user")
        login = user.get("login") if isinstance(user, dict) else None
        number = issue.get("number")
        if issue.get("title") == spec.title and login == ALARM_AUTHOR and isinstance(number, int):
            found.append(number)
    return sorted(found)


def latch_issue(
    repo: str,
    spec: AlarmIssue,
    *,
    alarming: bool,
    body_path: Path,
    clear_comment: str,
    runner: GhRunner | None = None,
) -> str:
    """Open, refresh or close ``spec``'s one alarm issue; what was done.

    ``body_path`` is the issue body an alarming read carries; ``clear_comment``
    is what a clean read says on the issue before closing it.
    """
    runner = runner or _gh
    runner(
        [
            "gh",
            "label",
            "create",
            spec.label,
            "--repo",
            repo,
            "--force",
            "--color",
            spec.label_color,
            "--description",
            spec.label_description,
        ]
    )
    numbers = open_alarm_issues(repo, spec, runner)
    if alarming:
        if not numbers:
            url = runner(
                [
                    "gh",
                    "issue",
                    "create",
                    "--repo",
                    repo,
                    "--title",
                    spec.title,
                    "--label",
                    spec.label,
                    "--body-file",
                    str(body_path),
                ]
            )
            return f"opened {url.strip()}"
        number = numbers[0]
        runner(["gh", "issue", "edit", str(number), "--repo", repo, "--body-file", str(body_path)])
        return f"refreshed #{number}"
    if not numbers:
        return "no alarm, and no open issue"
    for number in numbers:
        runner(["gh", "issue", "comment", str(number), "--repo", repo, "--body", clear_comment])
        runner(["gh", "issue", "close", str(number), "--repo", repo, "--reason", "completed"])
    return "closed " + ", ".join(f"#{number}" for number in numbers)
