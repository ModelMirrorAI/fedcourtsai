"""The agent-feedback latch: pure decisions and the gh-driven post, off a fake seam."""

from __future__ import annotations

import json
import subprocess
import time
from collections.abc import Sequence
from typing import Any

import pytest

from fedcourtsai.agent_feedback import (
    _GH_ATTEMPTS,
    _GH_TIMEOUT_SECONDS,
    LABEL,
    _gh,
    already_posted,
    choose_feedback_issue,
    issue_bodies,
    open_issue_once,
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


# --- the default runner: bounded retry and a per-call timeout -----------------


class FakeRun:
    """Stands in for ``subprocess.run``, replaying one scripted outcome per attempt.

    Each outcome is either the stdout of a run that succeeded or the exception that
    attempt raises, so a test can script "a blip, then the answer" and assert on how
    many attempts it took and which attempt's output came back.
    """

    def __init__(self, outcomes: Sequence[str | BaseException]):
        self._outcomes = list(outcomes)
        self.calls: list[tuple[list[str], dict[str, Any]]] = []

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        assert len(self.calls) < len(self._outcomes), "more attempts than the test scripted"
        outcome = self._outcomes[len(self.calls)]
        self.calls.append((list(command), dict(kwargs)))
        if isinstance(outcome, BaseException):
            raise outcome
        return subprocess.CompletedProcess(command, 0, stdout=outcome, stderr="")


def _blip() -> subprocess.CalledProcessError:
    """One transient non-zero exit, shaped as ``check=True`` raises it."""
    return subprocess.CalledProcessError(
        1, ["gh", "issue", "comment"], output="", stderr="HTTP 502\n"
    )


def test_gh_returns_the_first_attempts_output_when_it_works(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = FakeRun(["ok\n"])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    assert _gh(["gh", "issue", "view", "7"], sleeper=slept.append) == "ok\n"
    assert len(run.calls) == 1
    assert slept == []  # a call that works is never delayed


def test_gh_retries_a_transient_failure_and_returns_the_final_attempts_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = FakeRun([_blip(), _blip(), '[{"number": 42}]'])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    assert _gh(["gh", "issue", "list"], sleeper=slept.append) == '[{"number": 42}]'
    assert len(run.calls) == 3  # two blips absorbed
    assert slept == [5, 10]  # linear backoff between attempts, none after the last


def test_gh_retries_a_stalled_attempt_too(monkeypatch: pytest.MonkeyPatch) -> None:
    """The timeout exists to cut a stalled connect short; cutting it short must retry."""
    stalled = subprocess.TimeoutExpired(["gh", "issue", "comment"], _GH_TIMEOUT_SECONDS)
    run = FakeRun([stalled, "ok\n"])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    assert _gh(["gh", "issue", "comment", "7"], sleeper=slept.append) == "ok\n"
    assert len(run.calls) == 2
    assert slept == [5]  # a stall backs off exactly as a non-zero exit does


def test_gh_exhaustion_still_raises_what_callers_expect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Retrying changes when a call fails, never what its failure means: a sustained
    outage still raises, so a report that never lands fails its step as loudly as an
    unretried call would."""
    run = FakeRun([_blip(), _blip(), _blip()])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    with pytest.raises(subprocess.CalledProcessError) as raised:
        _gh(["gh", "issue", "comment", "7"], sleeper=slept.append)
    assert raised.value.stderr == "HTTP 502\n"  # the captured streams still ride along
    assert len(run.calls) == _GH_ATTEMPTS  # bounded, not indefinite
    assert slept == [5, 10]


def test_gh_exhaustion_by_stall_raises_too(monkeypatch: pytest.MonkeyPatch) -> None:
    """The timeout adds a failure mode callers could not see before, so pin that it
    still ends in a raise rather than a silent empty return."""
    stalls = [
        subprocess.TimeoutExpired(["gh", "issue", "view"], _GH_TIMEOUT_SECONDS)
        for _ in range(_GH_ATTEMPTS)
    ]
    run = FakeRun(stalls)
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    with pytest.raises(subprocess.TimeoutExpired):
        _gh(["gh", "issue", "view", "7"], sleeper=slept.append)
    assert len(run.calls) == _GH_ATTEMPTS


def test_gh_bounds_every_attempt_with_a_client_side_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``gh`` sets none of its own, so an unbounded attempt would hang a stalled
    connect to the job's own kill with nothing written."""
    run = FakeRun([_blip(), "ok\n"])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    _gh(["gh", "issue", "view", "7"], sleeper=slept.append)
    for _, kwargs in run.calls:
        assert kwargs["timeout"] == _GH_TIMEOUT_SECONDS
        # The capture the callers rely on is unchanged: they parse stdout as JSON
        # or as a created issue's URL, and a non-zero exit must still raise.
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["check"] is True


def test_gh_annotates_a_retry_on_stderr_without_echoing_the_body(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The annotation names only the call, so an issue body passed as an argument
    never lands in the job log."""
    run = FakeRun([_blip(), "ok\n"])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    body = "a flag roll-up nobody wants pasted into an annotation"
    assert _gh(["gh", "issue", "comment", "7", "--body", body], sleeper=slept.append) == "ok\n"
    captured = capsys.readouterr()
    assert "::warning::gh issue comment failed (attempt 1/3)" in captured.err
    assert body not in captured.err
    assert captured.out == ""  # annotations never contaminate the command's own stdout


def test_gh_annotates_exhaustion_as_an_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    run = FakeRun([_blip(), _blip(), _blip()])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    with pytest.raises(subprocess.CalledProcessError):
        _gh(["gh", "label", "create", LABEL], sleeper=slept.append)
    assert "::error::gh label create failed after 3 attempts" in capsys.readouterr().err


def test_the_posting_entry_points_inherit_the_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    """The seam's whole point is that callers need no wrapper of their own, so pin
    that with no injected runner — a blip on the way to a post is absorbed rather
    than reaching the caller."""
    monkeypatch.setattr(time, "sleep", lambda _: None)
    run = FakeRun([_blip(), '{"comments": []}', ""])
    monkeypatch.setattr(subprocess, "run", run)
    assert post_once(repo="o/r", issue=7, marker=_STALL_MARKER, body="the run stalled") == (
        "posted to #7"
    )
    # Three subprocess calls for two gh calls: the comment read was retried once.
    assert [command[1:3] for command, _ in run.calls] == [
        ["issue", "view"],
        ["issue", "view"],
        ["issue", "comment"],
    ]


# --- open_issue_once: the run-ops digests' per-issue reading surfaces --------

_DIGEST_MARKER = "<!-- daily-digest-event: scotus/1/evt-petition-disposition -->"
_DIGEST_BODY = f"{_DIGEST_MARKER}\n# Some case\n"


class FakeIssueGh:
    """A :data:`GhRunner` whose ``issue list --json body`` returns canned bodies."""

    def __init__(self, *, bodies: list[str], create_url: str = "") -> None:
        self._bodies = bodies
        self._create_url = create_url
        self.calls: list[list[str]] = []

    def __call__(self, argv: Sequence[str]) -> str:
        self.calls.append(list(argv))
        verb = tuple(argv[1:3])
        if verb == ("issue", "list"):
            return json.dumps([{"body": body} for body in self._bodies])
        if verb == ("issue", "create"):
            return self._create_url + "\n"
        return ""  # label create

    def created_issue(self) -> bool:
        return any(tuple(c[1:3]) == ("issue", "create") for c in self.calls)


def test_issue_bodies_reads_both_states_newest_first() -> None:
    # A digest issue is closed once read, so an open-only listing would forget
    # everything already read and re-feature it tomorrow.
    gh = FakeIssueGh(bodies=["newest", "older"])

    assert issue_bodies("o/r", "daily-digest", runner=gh) == ["newest", "older"]
    listing = gh.calls[0]
    assert listing[:3] == ["gh", "issue", "list"]
    assert "--state" in listing
    assert listing[listing.index("--state") + 1] == "all"
    assert listing[listing.index("--json") + 1] == "body"


def test_open_issue_once_creates_the_label_then_the_issue() -> None:
    gh = FakeIssueGh(bodies=[], create_url="https://github.com/o/r/issues/7")

    status = open_issue_once(
        repo="o/r",
        label="daily-digest",
        label_color="1d76db",
        label_description="Daily prediction-reading digest",
        title="Daily digest: Some case",
        body=_DIGEST_BODY,
        marker=_DIGEST_MARKER,
        runner=gh,
    )

    assert status == "opened https://github.com/o/r/issues/7"
    # The label is ensured with --force first, so the first ever run cannot fail
    # on a label that does not exist yet.
    assert gh.calls[0][:4] == ["gh", "label", "create", "daily-digest"]
    assert "--force" in gh.calls[0]
    assert gh.created_issue()


def test_open_issue_once_is_idempotent_on_the_marker() -> None:
    # A re-dispatched schedule must not open a second issue for the event the
    # last run already featured.
    gh = FakeIssueGh(bodies=["unrelated", _DIGEST_BODY])

    status = open_issue_once(
        repo="o/r",
        label="daily-digest",
        label_color="1d76db",
        label_description="Daily prediction-reading digest",
        title="Daily digest: Some case",
        body=_DIGEST_BODY,
        marker=_DIGEST_MARKER,
        runner=gh,
    )

    assert status.startswith("digest already posted under `daily-digest`")
    assert not gh.created_issue()
