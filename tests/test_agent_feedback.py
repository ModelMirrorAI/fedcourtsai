"""The agent-feedback latch: pure decisions and the gh-driven post, off a fake seam."""

from __future__ import annotations

import json
from collections.abc import Sequence

from fedcourtsai.agent_feedback import (
    LABEL,
    already_posted,
    choose_feedback_issue,
    post_agent_feedback,
    post_once,
)

MARKER = "<!-- agent-feedback-run: predict/R -->"
COMMENT = f"{MARKER}\n### predict · run `R`\n\n## 🚩 Agent flags"


class FakeGh:
    """A :data:`GhRunner` that canned-replies per gh subcommand and records calls.

    Stands in for the network so the latch's find-or-create and once-only posting
    are asserted on the issued commands, mirroring the ``command_runner`` seam in
    :class:`fedcourtsai.pipeline.runner.AgenticRunner`.
    """

    def __init__(self, *, issues: list[dict[str, int]], comments: list[str], create_url: str = ""):
        self._issues = issues
        self._comments = comments
        self._create_url = create_url
        self.calls: list[list[str]] = []

    def __call__(self, argv: Sequence[str]) -> str:
        self.calls.append(list(argv))
        verb = tuple(argv[1:3])
        if verb == ("issue", "list"):
            return json.dumps(self._issues)
        if verb == ("issue", "create"):
            return self._create_url + "\n"
        if verb == ("issue", "view"):
            return json.dumps({"comments": [{"body": b} for b in self._comments]})
        return ""  # label create, issue comment

    def commented(self) -> bool:
        return any(tuple(c[1:3]) == ("issue", "comment") for c in self.calls)

    def created_issue(self) -> bool:
        return any(tuple(c[1:3]) == ("issue", "create") for c in self.calls)


def test_already_posted_is_substring_match() -> None:
    assert already_posted([f"old\n{MARKER}\nflags"], MARKER) is True
    assert already_posted(["unrelated", "another"], MARKER) is False
    assert already_posted([], MARKER) is False


def test_choose_feedback_issue_reuses_first_else_none() -> None:
    assert choose_feedback_issue([{"number": 7}, {"number": 9}]) == 7
    assert choose_feedback_issue([]) is None


def test_post_blank_comment_does_nothing() -> None:
    gh = FakeGh(issues=[], comments=[])
    assert post_agent_feedback("   \n  ", "o/r", runner=gh) == "no agent feedback to post"
    assert gh.calls == []  # not even a label create when there is nothing to post


def test_post_reuses_open_issue_and_comments_once() -> None:
    gh = FakeGh(issues=[{"number": 42}], comments=["a prior, unrelated note"])
    status = post_agent_feedback(COMMENT, "o/r", runner=gh)
    assert status == "posted agent feedback to #42"
    assert not gh.created_issue()  # reused, did not create
    assert gh.commented()
    # The label is ensured idempotently before anything else.
    assert gh.calls[0][:4] == ["gh", "label", "create", LABEL]


def test_post_is_idempotent_when_marker_present() -> None:
    # A collect re-run: this run's marker already rode in on an earlier comment.
    gh = FakeGh(issues=[{"number": 42}], comments=[f"### predict · run `R`\n{MARKER}"])
    status = post_agent_feedback(COMMENT, "o/r", runner=gh)
    assert status == "agent feedback already on #42"
    assert not gh.commented()


def test_post_creates_issue_when_none_open() -> None:
    gh = FakeGh(issues=[], comments=[], create_url="https://github.com/o/r/issues/123")
    status = post_agent_feedback(COMMENT, "o/r", runner=gh)
    assert status == "posted agent feedback to #123"
    assert gh.created_issue()
    # The comment lands on the freshly created issue number parsed from the URL.
    comment_call = next(c for c in gh.calls if tuple(c[1:3]) == ("issue", "comment"))
    assert "123" in comment_call


# --- post_once: the collect job's stall / secret-scan reports ----------------

_STALL_MARKER = "<!-- collect-stall: 12345 -->"


def test_post_once_comments_when_the_marker_is_absent() -> None:
    gh = FakeGh(issues=[], comments=["an unrelated comment"])
    result = post_once(repo="o/r", issue=7, marker=_STALL_MARKER, body="the run stalled", runner=gh)
    assert result == "posted to #7"
    (comment,) = [c for c in gh.calls if tuple(c[1:3]) == ("issue", "comment")]
    # The marker leads the body, so the next attempt can find it.
    assert comment[-1].startswith(_STALL_MARKER)
    assert "the run stalled" in comment[-1]


def test_post_once_is_silent_when_the_marker_is_already_there() -> None:
    """Rerunning collect is the documented recovery for a transfer failure, so
    without this every recovery attempt stacks another copy of the same warning
    on the trigger issue and buries the signal it exists to raise."""
    gh = FakeGh(issues=[], comments=[f"{_STALL_MARKER}\nthe run stalled"])
    assert post_once(repo="o/r", issue=7, marker=_STALL_MARKER, body="x", runner=gh) == (
        "already posted on #7"
    )
    assert not gh.commented()


def test_post_once_keys_on_the_run_so_a_different_run_still_reports() -> None:
    """Dedup must not silence a genuinely new stall on the same issue."""
    gh = FakeGh(issues=[], comments=["<!-- collect-stall: 99999 -->\nan earlier run"])
    assert post_once(repo="o/r", issue=7, marker=_STALL_MARKER, body="x", runner=gh).startswith(
        "posted"
    )
    assert gh.commented()


def test_post_once_distinguishes_the_two_report_kinds() -> None:
    """A stall already reported must not suppress that run's secret-scan hit."""
    gh = FakeGh(issues=[], comments=[f"{_STALL_MARKER}\nstalled"])
    scan_marker = "<!-- collect-secret-scan: 12345 -->"
    assert post_once(repo="o/r", issue=7, marker=scan_marker, body="hit", runner=gh).startswith(
        "posted"
    )
    assert gh.commented()
