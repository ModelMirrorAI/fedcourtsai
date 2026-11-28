"""The alarm a collect raises when its secret scan withholds a run's output.

A withheld branch is pushed nowhere and opens no PR, and the collect job that
withheld it still concludes green: withholding is the scan working, not the job
failing. So the run's conclusion says nothing, while every cell on the branch
has its output in the run's artifacts alone until a maintainer reviews the
flagged content, and on predict the stranded-run guard keeps later rounds from
re-minting those cells meanwhile. This module
is the durable notice of that state: one open issue under the ``withheld-round``
alarm label, with one comment per withholding report.

The issue is opened by the first report and reused while it is open; only an
issue the workflow token opened under the alarm's title counts as it. Nothing
closes it but a maintainer, once the withheld output is salvaged, deleted or
left to a re-spend: no later run can tell which of those happened, so an open
issue means exactly "a run's output is withheld and nobody has settled it".

What is posted is the scan's own redacted report (file, rule and line, never
the matched text) under harness-rendered counts and identifiers; no artifact
content reaches the issue. The collect job posts with the ambient
``GITHUB_TOKEN``, and the label triggers nothing.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from .agent_feedback import GhRunner, _gh, already_posted
from .alarm_issue import ALARM_AUTHOR, AlarmIssue, open_alarm_issues

LABEL: Final = "withheld-round"
ISSUE_TITLE: Final = "Run output withheld by the secret scan"
ALARM: Final = AlarmIssue(
    title=ISSUE_TITLE,
    label=LABEL,
    label_description="Alarm: a collect's secret scan withheld a run's output",
)
_ISSUE_BODY: Final = (
    "A predict or evaluate `collect` withheld a run's output because its secret "
    "scan did not pass, or left the run's flag roll-up unpublished for the same "
    "reason. The run itself concludes green, so this issue is the "
    "notice: each withholding run adds a comment below with the run, the number "
    "of cells withheld, and the scan's redacted report.\n\n"
    "A withheld branch's output sits only in the run's cell artifacts until the "
    "flagged content is reviewed, and on predict later rounds do not re-mint "
    "those cells while the stranded-run guard holds them. See the "
    "*secret scan did not pass* row of the collect recovery table in "
    "docs/pipeline.md for the review and the two remedies (salvage by hand "
    "while the cell artifacts are retained, or accept the re-spend). If the "
    "flagged line is a live credential, rotate it and delete the run's cell "
    "artifacts before anything else.\n\n"
    "Close this issue once every run below is settled. A later withhold opens "
    "a fresh one."
)

# Bounds on what one comment renders, so a malformed ledger cannot grow it.
_MAX_BRANCHES: Final = 10
_MAX_FIELD: Final = 120


@dataclass(frozen=True)
class WithheldBranch:
    """One branch a collect withheld: its name, its plan-time run id, its cells."""

    branch: str
    run_id: str
    cells: int


def parse_withheld(text: str) -> list[WithheldBranch]:
    """The withheld branches a collect recorded, one JSON object per line.

    Tolerant by design: the alarm must still be raised when the ledger is
    absent, empty or damaged, so a line that does not parse is dropped rather
    than raised on, and the report is posted with whatever could be read.
    """
    found: list[WithheldBranch] = []
    for line in text.splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue
        branch, run_id, cells = row.get("branch"), row.get("run_id"), row.get("cells")
        if not isinstance(branch, str) or not isinstance(run_id, str):
            continue
        if isinstance(cells, bool) or not isinstance(cells, int) or cells < 0:
            continue
        found.append(WithheldBranch(branch=branch, run_id=run_id, cells=cells))
    return found


def _code(value: str) -> str:
    """``value`` as an inline code span that cannot break out of one.

    Backticks would close the span and any control or separator character can
    end the line it sits on, so each becomes a space; a value left empty is
    said to be so, since an empty span renders as stray backticks.
    """
    cleaned = "".join(
        " " if ch == "`" or unicodedata.category(ch)[0] in {"C", "Z"} else ch for ch in value
    ).strip()[:_MAX_FIELD]
    return f"`{cleaned}`" if cleaned else "(empty)"


def render_withheld_alarm(
    *, workflow: str, run_url: str, branches: Sequence[WithheldBranch], report: str
) -> str:
    """The comment one withholding run adds to the alarm issue.

    ``report`` is the scan's own redacted report, carried as written. Three
    shapes, told apart in the text. A branch on the ledger was withheld, and
    the comment counts its cells. A report with no branch on the ledger means
    the scan fired on the run's roll-up text alone, which is suppressed while
    the run's PRs land as usual, or that the ledger was lost; the comment says
    so rather than counting zero. A branch with no report means the scan ended
    without writing one, a fault in the scan itself, and the comment says that.
    """
    heading = (
        "### Run withheld by the secret scan"
        if branches
        else "### Secret scan did not pass, with no withheld branch recorded"
    )
    lines = [
        heading,
        "",
        f"- Workflow: {_code(workflow)}",
        f"- Run: {run_url}",
    ]
    run_ids = sorted({b.run_id for b in branches})
    if run_ids:
        lines.append("- Run id: " + ", ".join(_code(r) for r in run_ids))
    if branches:
        total = sum(b.cells for b in branches)
        lines.append(f"- Cells withheld: {total}")
        for b in branches[:_MAX_BRANCHES]:
            lines.append(f"  - {_code(b.branch)}: {b.cells} cell(s), nothing pushed")
        if len(branches) > _MAX_BRANCHES:
            lines.append(f"  - and {len(branches) - _MAX_BRANCHES} more branch(es)")
    else:
        lines.append(
            "- Cells withheld: not recorded. Either the scan fired only on the "
            "run's roll-up text (its flag roll-up or stakes census, which is then "
            "left unpublished while the run's PRs land as usual), or the record of "
            "a withheld branch was lost. The report below names what it fired on; "
            "the run's log says whether a branch was withheld."
        )
    lines += [
        "",
        report.strip()
        or "The scan ended without writing a report, so the branch was withheld on a "
        "fault in the scan itself and not on a finding. The collect job's log has "
        "the error.",
        "",
    ]
    return "\n".join(lines)


def alarm_marker(github_run_id: str, body: str) -> str:
    """The once-only key for one report: the Actions run and the report's content.

    Keyed on content as well as the run, because a re-run of collect can gather
    a different artifact set and withhold something else, and that second
    report must not be deduplicated into silence.
    """
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    return f"<!-- withheld-round: {github_run_id}-{digest} -->"


def _own_comments(repo: str, number: int, runner: GhRunner) -> list[str]:
    """The bodies of the comments the workflow token itself left on the issue.

    Anyone can comment on a public issue, and a comment quoting a report's key
    must not pass for the report. One page of 100, newest first: a re-run's
    earlier comment is recent, and a miss costs one repeated comment.
    """
    listing = json.loads(
        runner(
            [
                "gh",
                "api",
                f"repos/{repo}/issues/{number}/comments?per_page=100&sort=created&direction=desc",
            ]
        )
        or "[]"
    )
    bodies: list[str] = []
    for comment in listing if isinstance(listing, list) else []:
        if not isinstance(comment, dict):
            continue
        user = comment.get("user")
        if isinstance(user, dict) and user.get("login") == ALARM_AUTHOR:
            bodies.append(str(comment.get("body", "")))
    return bodies


def post_withheld_alarm(
    *,
    repo: str,
    workflow: str,
    run_url: str,
    github_run_id: str,
    withheld: str,
    report: str,
    runner: GhRunner = _gh,
) -> str:
    """Raise the alarm for one withholding run; a one-line status for the log.

    A blank ``report`` with nothing on the ledger means the scan came back
    clean, and nothing is posted. Either one alone raises the alarm: a report
    whose ledger was lost, or a withheld branch whose scan wrote no report.
    Otherwise the open alarm issue is found, or opened, and the rendered
    comment is added once per :func:`alarm_marker`. Only an issue the workflow
    token opened under the alarm's title is the alarm, and only that token's
    comments count as posted, so neither a labelled issue of someone else's
    nor a comment quoting a key can take or silence a report.
    """
    branches = parse_withheld(withheld)
    if not report.strip() and not branches:
        return "no secret-scan report and no withheld branch; no alarm"
    body = render_withheld_alarm(
        workflow=workflow, run_url=run_url, branches=branches, report=report
    )
    runner(
        [
            "gh",
            "label",
            "create",
            ALARM.label,
            "--repo",
            repo,
            "--force",
            "--color",
            ALARM.label_color,
            "--description",
            ALARM.label_description,
        ]
    )
    numbers = open_alarm_issues(repo, ALARM, runner)
    if numbers:
        number = numbers[0]
    else:
        url = runner(
            [
                "gh",
                "issue",
                "create",
                "--repo",
                repo,
                "--title",
                ALARM.title,
                "--label",
                ALARM.label,
                "--body",
                _ISSUE_BODY,
            ]
        ).strip()
        number = int(url.rstrip("/").rsplit("/", 1)[-1])
    marker = alarm_marker(github_run_id, body)
    if already_posted(_own_comments(repo, number, runner), marker):
        return f"withheld-round alarm: already posted on #{number}"
    runner(["gh", "issue", "comment", str(number), "--repo", repo, "--body", f"{marker}\n{body}"])
    return f"withheld-round alarm: posted to #{number}"
