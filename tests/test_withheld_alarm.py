"""The withheld-round alarm: the ledger read, the rendered comment, and the post."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.secretscan import Finding, render_issue_comment
from fedcourtsai.withheld_alarm import (
    ISSUE_TITLE,
    LABEL,
    WithheldBranch,
    alarm_marker,
    parse_withheld,
    post_withheld_alarm,
    render_withheld_alarm,
)

RUN_URL = "https://github.com/o/r/actions/runs/45837587564"
REPORT = "🔒 This round tripped the **secret scan**\n\n| file | rule | line |"
LEDGER = json.dumps({"branch": "predict/run-20261126T141900Z", "run_id": "R1", "cells": 15})


BOT = "github-actions[bot]"


def _issue(number: int, *, title: str = ISSUE_TITLE, login: str = BOT) -> dict[str, object]:
    return {"number": number, "title": title, "user": {"login": login}}


def _comment(body: str, *, login: str = BOT) -> dict[str, object]:
    return {"body": body, "user": {"login": login}}


class FakeGh:
    """Canned replies per gh call, recording every call."""

    def __init__(
        self,
        *,
        issues: Sequence[dict[str, object]] = (),
        comments: Sequence[dict[str, object]] = (),
    ):
        self._issues = list(issues)
        self._comments = list(comments)
        self.calls: list[list[str]] = []

    def __call__(self, argv: Sequence[str]) -> str:
        self.calls.append(list(argv))
        if argv[1] == "api":
            return json.dumps(self._comments if "/comments?" in argv[2] else self._issues)
        if tuple(argv[1:3]) == ("issue", "create"):
            return "https://github.com/o/r/issues/41\n"
        return ""

    def verbs(self) -> list[str]:
        return [
            ("api comments" if "/comments?" in c[2] else "api issues")
            if c[1] == "api"
            else " ".join(c[1:3])
            for c in self.calls
        ]

    def commented(self) -> bool:
        return "issue comment" in self.verbs()

    def comment_body(self) -> str:
        call = next(c for c in self.calls if tuple(c[1:3]) == ("issue", "comment"))
        return call[call.index("--body") + 1]


def _post(gh: FakeGh, *, report: str = REPORT, withheld: str = LEDGER) -> str:
    return post_withheld_alarm(
        repo="o/r",
        workflow="run-predict",
        run_url=RUN_URL,
        github_run_id="45837587564",
        withheld=withheld,
        report=report,
        runner=gh,
    )


def test_a_withhold_opens_the_alarm_issue_and_comments_the_run_and_the_count() -> None:
    gh = FakeGh()
    status = _post(gh)

    assert status == "withheld-round alarm: posted to #41"
    assert gh.verbs() == [
        "label create",
        "api issues",
        "issue create",
        "api comments",
        "issue comment",
    ]
    create = gh.calls[2]
    assert create[create.index("--label") + 1] == LABEL
    assert create[create.index("--title") + 1] == ISSUE_TITLE
    body = gh.comment_body()
    assert "- Workflow: `run-predict`" in body
    assert RUN_URL in body
    assert "`R1`" in body
    assert "Cells withheld: 15" in body
    assert "`predict/run-20261126T141900Z`: 15 cell(s)" in body
    assert REPORT in body


def test_an_open_alarm_issue_is_reused() -> None:
    gh = FakeGh(issues=[_issue(7)])
    assert _post(gh) == "withheld-round alarm: posted to #7"
    assert "issue create" not in gh.verbs()


def test_a_labelled_issue_that_is_not_the_bots_own_is_not_the_alarm() -> None:
    """A label can be put on any issue by anyone who can triage; such an issue
    must not collect the reports, where its author could edit or close them."""
    decoys = [_issue(3, login="someone"), _issue(4, title="Some other title")]
    gh = FakeGh(issues=decoys)
    assert _post(gh) == "withheld-round alarm: posted to #41"
    assert "issue create" in gh.verbs()


def test_a_rerun_of_the_same_report_does_not_comment_twice() -> None:
    first = FakeGh(issues=[_issue(7)])
    _post(first)
    gh = FakeGh(issues=[_issue(7)], comments=[_comment(first.comment_body())])
    assert _post(gh) == "withheld-round alarm: already posted on #7"
    assert not gh.commented()


def test_someone_elses_comment_quoting_the_key_does_not_silence_the_report() -> None:
    first = FakeGh(issues=[_issue(7)])
    _post(first)
    forged = _comment(first.comment_body(), login="someone")
    gh = FakeGh(issues=[_issue(7)], comments=[forged])
    assert _post(gh) == "withheld-round alarm: posted to #7"


def test_a_rerun_that_withholds_something_else_still_reports() -> None:
    """The key carries the report's content, so a different hit is a new comment."""
    first = FakeGh(issues=[_issue(7)])
    _post(first)
    gh = FakeGh(issues=[_issue(7)], comments=[_comment(first.comment_body())])
    assert _post(gh, report=REPORT + "\n| `other` | x | 3 |").endswith("posted to #7")


def test_a_clean_scan_raises_nothing() -> None:
    gh = FakeGh()
    status = _post(gh, report=" \n", withheld="")
    assert status == "no secret-scan report and no withheld branch; no alarm"
    assert gh.calls == []


def test_a_report_with_no_branch_recorded_still_raises_the_alarm() -> None:
    """A roll-up-only hit, or a lost ledger: the report alone raises it, under a
    heading that does not claim a withhold, with the count unknown, not zero."""
    gh = FakeGh()
    _post(gh, withheld="")
    body = gh.comment_body()
    assert "### Secret scan did not pass, with no withheld branch recorded" in body
    assert "Run withheld by the secret scan" not in body
    assert "Cells withheld: not recorded" in body
    assert "Cells withheld: 0" not in body
    assert REPORT in body


def test_a_withheld_branch_whose_scan_wrote_no_report_still_raises_the_alarm() -> None:
    """The branch is withheld on any failing scan, a crashed one included."""
    gh = FakeGh()
    assert _post(gh, report="").endswith("posted to #41")
    body = gh.comment_body()
    assert "Cells withheld: 15" in body
    assert "ended without writing a report" in body


def test_branches_past_the_cap_are_counted_not_listed() -> None:
    branches = [WithheldBranch(f"predict/run-R{i}", "R", 1) for i in range(12)]
    body = render_withheld_alarm(
        workflow="run-predict", run_url=RUN_URL, branches=branches, report=REPORT
    )
    assert "Cells withheld: 12" in body
    assert "`predict/run-R9`" in body and "`predict/run-R10`" not in body
    assert "and 2 more branch(es)" in body


def test_the_ledger_read_drops_what_it_cannot_parse() -> None:
    text = "\n".join(
        [
            LEDGER,
            "not json",
            json.dumps(["a", "list"]),
            json.dumps({"branch": "b", "run_id": "R", "cells": -1}),
            json.dumps({"branch": "b", "run_id": "R", "cells": True}),
            json.dumps({"branch": 3, "run_id": "R", "cells": 1}),
            json.dumps({"branch": "predict/run-R1-partial", "run_id": "R1", "cells": 2}),
        ]
    )
    assert parse_withheld(text) == [
        WithheldBranch("predict/run-20261126T141900Z", "R1", 15),
        WithheldBranch("predict/run-R1-partial", "R1", 2),
    ]


def test_the_count_sums_every_withheld_branch() -> None:
    body = render_withheld_alarm(
        workflow="run-evaluate",
        run_url=RUN_URL,
        branches=[WithheldBranch("evaluate/run-R", "R", 4), WithheldBranch("x-partial", "R", 2)],
        report=REPORT,
    )
    assert body.startswith("### Run withheld by the secret scan")
    assert "- Workflow: `run-evaluate`" in body
    assert "Cells withheld: 6" in body
    assert body.count("`R`") == 1


def test_a_branch_name_cannot_break_out_of_its_code_span() -> None:
    body = render_withheld_alarm(
        workflow="run-predict",
        run_url=RUN_URL,
        branches=[WithheldBranch("a`b\n# heading\r@m\u2028" + "x" * 500, "", 1)],
        report=REPORT,
    )
    line = next(row for row in body.splitlines() if "cell(s)" in row)
    assert line.count("`") == 2
    assert len(line) < 200
    assert body.rstrip("\n").splitlines() == body.rstrip("\n").split("\n")
    assert "- Run id: (empty)" in body


def test_the_comment_carries_the_scan_report_as_rendered() -> None:
    """What reaches the issue is the scan's redacted report: file, rule and line."""
    finding = Finding(path="data/cases/scotus/1/reasoning.md", rule="model-provider-key", line=5)
    report = render_issue_comment([finding], RUN_URL)
    body = render_withheld_alarm(
        workflow="run-predict",
        run_url=RUN_URL,
        branches=[WithheldBranch("predict/run-R", "R", 15)],
        report=report,
    )
    assert report in body


def test_the_marker_is_keyed_on_the_run_and_the_content() -> None:
    assert alarm_marker("1", "a") != alarm_marker("2", "a")
    assert alarm_marker("1", "a") != alarm_marker("1", "b")
    assert alarm_marker("1", "a").startswith("<!-- withheld-round: 1-")


def test_the_command_posts_nothing_when_both_files_are_absent(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        [
            "post-withheld-alarm",
            "--workflow",
            "run-predict",
            "--repo",
            "o/r",
            "--run-url",
            RUN_URL,
            "--github-run-id",
            "1",
            "--report-file",
            str(tmp_path / "secret-scan-issue.md"),
            "--withheld-file",
            str(tmp_path / "withheld-branches.jsonl"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "no alarm" in result.output
