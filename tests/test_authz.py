"""The label-trigger authorization gate (:mod:`fedcourtsai.authz`).

The security shape — that the gate runs before any privileged step — is locked in
``test_workflow_auth_gate.py``; this exercises the *decision* the workflow now
delegates to the ``authorize-trigger`` command: a Bot handoff is trusted, write
access is required otherwise, and anything else fails closed — plus the default
lookup's bounded retry, whose one non-negotiable is that no failure path may
manufacture a permission.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from typing import Any

import pytest

from fedcourtsai import agent_feedback
from fedcourtsai.authz import (
    _GH_ATTEMPTS,
    _GH_BACKOFF_SECONDS,
    _GH_TIMEOUT_SECONDS,
    _gh_permission,
    authorize_trigger,
    decide_authorization,
)


def test_bot_sender_is_authorized_without_a_lookup() -> None:
    seen: list[tuple[str, str]] = []

    def lookup(repo: str, actor: str) -> str:
        seen.append((repo, actor))
        return "none"

    decision = authorize_trigger("Bot", "pipeline[bot]", "o/r", lookup=lookup)
    assert decision.authorized
    assert "pipeline App handoff" in decision.message
    # A Bot sender must never trigger the (network) permission lookup.
    assert seen == []


def test_pinned_bot_actor_refuses_any_other_bot_without_a_lookup() -> None:
    """The pin turns "Bot" from "any installed App" into "the pipeline App".
    A mismatched bot is refused outright — no permission lookup, since an App is
    never a collaborator and a lookup could only delay the refusal."""
    seen: list[tuple[str, str]] = []

    def lookup(repo: str, actor: str) -> str:
        seen.append((repo, actor))
        return "admin"  # even a would-be-authorizing lookup must not rescue it

    decision = authorize_trigger(
        "Bot", "third-party-app[bot]", "o/r", lookup=lookup, bot_actor="pipeline[bot]"
    )
    assert not decision.authorized
    assert "not the pinned App handoff" in decision.message
    assert "pipeline[bot]" in decision.message
    assert seen == []


def test_pinned_bot_actor_authorizes_the_pinned_login() -> None:
    decision = authorize_trigger(
        "Bot", "pipeline[bot]", "o/r", lookup=_const("none"), bot_actor="pipeline[bot]"
    )
    assert decision.authorized
    assert "pipeline App handoff" in decision.message


def test_the_pin_never_touches_a_user_sender() -> None:
    """The pin narrows the Bot branch only: a human actor who happens to share
    the pinned string still goes through the permission lookup."""
    decision = authorize_trigger(
        "User", "alice", "o/r", lookup=_const("write"), bot_actor="pipeline[bot]"
    )
    assert decision.authorized
    assert "write access" in decision.message


def _const(permission: str) -> Callable[[str, str], str]:
    """A :data:`PermissionLookup` that always returns ``permission``."""
    return lambda repo, actor: permission


def test_write_collaborator_is_authorized() -> None:
    for perm in ("admin", "maintain", "write"):
        decision = authorize_trigger("User", "alice", "o/r", lookup=_const(perm))
        assert decision.authorized, perm
        assert perm in decision.message


def test_read_collaborator_is_refused() -> None:
    decision = authorize_trigger("User", "mallory", "o/r", lookup=_const("read"))
    assert not decision.authorized
    assert "lacks write access" in decision.message
    assert "read" in decision.message


def test_non_collaborator_default_none_is_refused() -> None:
    # The default lookup yields "none" on any API failure; that must fail closed.
    decision = decide_authorization("User", "stranger", "none")
    assert not decision.authorized
    assert "refusing to run" in decision.message


def test_lookup_receives_repo_and_actor() -> None:
    calls: list[tuple[str, str]] = []

    def lookup(repo: str, actor: str) -> str:
        calls.append((repo, actor))
        return "write"

    authorize_trigger("User", "alice", "owner/name", lookup=lookup)
    assert calls == [("owner/name", "alice")]


class FakeRun:
    """A scripted ``subprocess.run``: each element is stdout to return or an
    exception to raise, mirroring ``test_agent_feedback.py``'s seam-level fake."""

    def __init__(self, outcomes: list[Any]):
        self._outcomes = outcomes
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
    return subprocess.CalledProcessError(1, ["gh", "api"], output="", stderr="HTTP 502\n")


def test_the_lookup_bounds_match_the_other_gh_retry_surfaces() -> None:
    """One span for a degraded API everywhere: the workflow invariants test pins
    ``agent_feedback``'s constants against ``scripts/gh_retry.sh``, and this pins
    the lookup's against ``agent_feedback``'s, so all three move together."""
    assert (_GH_ATTEMPTS, _GH_TIMEOUT_SECONDS, _GH_BACKOFF_SECONDS) == (
        agent_feedback._GH_ATTEMPTS,
        agent_feedback._GH_TIMEOUT_SECONDS,
        agent_feedback._GH_BACKOFF_SECONDS,
    )


def test_lookup_returns_the_first_attempts_answer_undelayed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = FakeRun(["write\n"])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    assert _gh_permission("o/r", "alice", sleeper=slept.append) == "write"
    assert len(run.calls) == 1
    assert slept == []  # a lookup that works is never delayed
    (argv, kwargs) = run.calls[0]
    assert argv[:3] == ["gh", "api", "repos/o/r/collaborators/alice/permission"]
    assert kwargs["timeout"] == _GH_TIMEOUT_SECONDS


def test_lookup_absorbs_a_blip_instead_of_refusing_a_legitimate_actor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The fail-closed default made an unretried blip a refused legitimate run;
    the retry is what removes that cost."""
    run = FakeRun([_blip(), "admin\n"])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    assert _gh_permission("o/r", "alice", sleeper=slept.append) == "admin"
    assert len(run.calls) == 2
    assert slept == [_GH_BACKOFF_SECONDS]


def test_lookup_never_retries_a_successful_answer_for_a_better_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The security direction: a successful response is final, whatever it names.
    A ``read`` answer must come back after one attempt — retrying it would be a
    machine hunting for an allow."""
    run = FakeRun(["read\n"])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    assert _gh_permission("o/r", "mallory", sleeper=slept.append) == "read"
    assert len(run.calls) == 1
    assert slept == []


def test_lookup_exhaustion_still_fails_closed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A sustained outage ends where the unretried call ended: ``"none"``, which
    refuses — bounded, annotated, and never an exception the workflow step would
    turn into an unreadable failure instead of a logged refusal."""
    run = FakeRun([_blip() for _ in range(_GH_ATTEMPTS)])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    assert _gh_permission("o/r", "alice", sleeper=slept.append) == "none"
    assert len(run.calls) == _GH_ATTEMPTS  # bounded, not indefinite
    assert slept == [_GH_BACKOFF_SECONDS, 2 * _GH_BACKOFF_SECONDS]
    assert "::error::gh api repos/o/r/collaborators/alice/permission failed" in (
        capsys.readouterr().err
    )


def test_lookup_retries_a_stalled_attempt_and_a_stalled_exhaustion_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The per-attempt timeout cuts a stalled connect short; the cut must retry,
    and stalling every attempt must end in a refusal, not a hang or a raise."""
    stalled = subprocess.TimeoutExpired(["gh", "api"], _GH_TIMEOUT_SECONDS)
    run = FakeRun([stalled, "write\n"])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    assert _gh_permission("o/r", "alice", sleeper=slept.append) == "write"
    assert len(run.calls) == 2

    all_stalled = FakeRun(
        [subprocess.TimeoutExpired(["gh", "api"], _GH_TIMEOUT_SECONDS) for _ in range(_GH_ATTEMPTS)]
    )
    monkeypatch.setattr(subprocess, "run", all_stalled)
    assert _gh_permission("o/r", "alice", sleeper=slept.append) == "none"
    assert len(all_stalled.calls) == _GH_ATTEMPTS


def test_lookup_does_not_retry_a_missing_gh_but_annotates_it(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """``gh`` itself missing is deterministic: three attempts would only delay the
    refusal it already is. But the refusal must be attributable — without the
    annotation the job log shows only "lacks write access (permission: none)",
    which misreads a lookup that never ran as a non-collaborator."""
    run = FakeRun([OSError("gh not found")])
    monkeypatch.setattr(subprocess, "run", run)
    slept: list[float] = []
    assert _gh_permission("o/r", "alice", sleeper=slept.append) == "none"
    assert len(run.calls) == 1
    assert slept == []
    captured = capsys.readouterr()
    assert "::error::gh api repos/o/r/collaborators/alice/permission could not be executed" in (
        captured.err
    )
    assert captured.out == ""


def test_lookup_treats_a_successful_empty_answer_as_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run = FakeRun(["\n"])
    monkeypatch.setattr(subprocess, "run", run)
    assert _gh_permission("o/r", "alice", sleeper=lambda _: None) == "none"
