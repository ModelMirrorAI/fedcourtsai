"""The two authorization decisions in :mod:`fedcourtsai.authz`.

The workflow shape — that the run gate is every gated workflow's first job and
every other job waits on it — is locked in ``test_workflow_auth_gate.py``; this
exercises the *decisions*. The run gate (``authorize-run``): a dispatch needs a
listed human or a bot listed for that workflow, a re-run needs a listed human,
an unchosen first attempt passes, and anything unreadable — the context or the
allow-list — refuses. The trigger gate (``authorize-trigger``): a Bot handoff
is trusted, write access is required otherwise, and anything else fails closed
— plus the default lookup's bounded retry, whose one non-negotiable is that no
failure path may manufacture a permission.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from fedcourtsai import agent_feedback
from fedcourtsai.authz import (
    _GH_ATTEMPTS,
    _GH_BACKOFF_SECONDS,
    _GH_TIMEOUT_SECONDS,
    DispatchersConfig,
    DispatchersConfigError,
    _gh_permission,
    authorize_trigger,
    decide_authorization,
    decide_run_authorization,
    load_dispatchers_config,
)
from fedcourtsai.cli import app


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


def test_the_pin_refuses_an_empty_bot_login() -> None:
    """An empty actor string (a malformed event payload) is just another
    non-matching login: refused outright, never rescued by the lookup."""
    decision = authorize_trigger(
        "Bot", "", "o/r", lookup=_const("admin"), bot_actor="pipeline[bot]"
    )
    assert not decision.authorized


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


# --- The run gate -----------------------------------------------------------

MAINTAINER = "maintainer"
AGENT = "agent-account"
DISPATCH_BOT = "pipeline-dispatch[bot]"

CONFIG = DispatchersConfig(
    humans=(MAINTAINER,),
    bots={"run-predict.yml": (DISPATCH_BOT,)},
)


def _decide(
    *,
    event: str = "workflow_dispatch",
    actor: str = MAINTAINER,
    triggering: str | None = None,
    attempt: str = "1",
    workflow: str = "run-predict.yml",
    config: DispatchersConfig = CONFIG,
) -> bool:
    return decide_run_authorization(
        event_name=event,
        actor=actor,
        triggering_actor=actor if triggering is None else triggering,
        run_attempt=attempt,
        workflow_file=workflow,
        config=config,
    ).authorized


def test_a_listed_human_may_dispatch_any_gated_workflow() -> None:
    assert _decide(workflow="run-predict.yml")
    assert _decide(workflow="run-pull.yml")


def test_an_unlisted_dispatcher_is_refused_and_named() -> None:
    decision = decide_run_authorization(
        event_name="workflow_dispatch",
        actor=AGENT,
        triggering_actor=AGENT,
        run_attempt="1",
        workflow_file="run-pull.yml",
        config=CONFIG,
    )
    assert not decision.authorized
    assert AGENT in decision.message
    assert "run-pull.yml" in decision.message


def test_logins_compare_case_insensitively() -> None:
    """GitHub logins are case-insensitive, and the context may carry either case."""
    assert _decide(actor=MAINTAINER.upper())
    assert _decide(actor=DISPATCH_BOT.upper())


def test_a_pipeline_bot_may_dispatch_only_the_workflow_listed_for_it() -> None:
    assert _decide(actor=DISPATCH_BOT, workflow="run-predict.yml")
    assert not _decide(actor=DISPATCH_BOT, workflow="run-evaluate.yml")
    assert not _decide(actor=DISPATCH_BOT, workflow="run-pull.yml")


def test_a_pipeline_bot_never_re_runs() -> None:
    """Even the workflow it may dispatch: a bot's re-run is refused."""
    assert not _decide(actor=DISPATCH_BOT, triggering=DISPATCH_BOT, attempt="2")


def test_a_maintainer_may_re_run_a_chained_round() -> None:
    assert _decide(actor=DISPATCH_BOT, triggering=MAINTAINER, attempt="2")


def test_the_agent_may_not_re_run_anything() -> None:
    for event in ("workflow_dispatch", "schedule", "push"):
        assert not _decide(event=event, actor=MAINTAINER, triggering=AGENT, attempt="2"), event


def test_a_re_run_does_not_launder_an_unlisted_dispatch() -> None:
    """The dispatch rule binds at every attempt: `actor` stays the dispatcher's,
    so a listed human re-running an unlisted login's dispatch is still refused."""
    assert not _decide(actor=AGENT, triggering=MAINTAINER, attempt="2")


def test_an_unchosen_first_attempt_passes_whoever_the_actor() -> None:
    for event in ("schedule", "push", "pull_request"):
        assert _decide(event=event, actor=AGENT, attempt="1"), event
        assert _decide(event=event, actor="", triggering="", attempt="1"), event


def test_a_re_run_of_a_scheduled_run_needs_a_listed_human() -> None:
    assert _decide(event="schedule", actor=AGENT, triggering=MAINTAINER, attempt="3")
    assert not _decide(event="schedule", actor=MAINTAINER, triggering=AGENT, attempt="3")


@pytest.mark.parametrize("attempt", ["", " ", "0", "-1", "two", "1.5", "²"])
def test_an_unparseable_attempt_refuses(attempt: str) -> None:
    assert not _decide(event="schedule", attempt=attempt)


def test_a_blank_dispatcher_refuses() -> None:
    assert not _decide(actor="", triggering=MAINTAINER)
    assert not _decide(actor="   ", triggering=MAINTAINER)


def test_a_blank_re_runner_refuses() -> None:
    assert not _decide(event="schedule", triggering="", attempt="2")


def test_a_blank_event_or_workflow_refuses() -> None:
    assert not _decide(event="")
    assert not _decide(workflow="")


def test_an_empty_allow_list_refuses_every_dispatch_and_re_run() -> None:
    empty = DispatchersConfig(humans=())
    assert not _decide(config=empty)
    assert not _decide(event="schedule", attempt="2", config=empty)
    assert _decide(event="schedule", config=empty)


def test_the_rerunner_list_is_comma_delimited_at_both_ends() -> None:
    """The re-run guard matches `,<login>,` against it, so each login must sit
    between delimiters, and an empty list must not read as `,,` (which a blank
    triggering actor would format to)."""
    assert DispatchersConfig(humans=("a", "b-c")).rerunner_list() == ",a,b-c,"
    assert DispatchersConfig(humans=()).rerunner_list() == ""
    rerunners = DispatchersConfig(humans=("modelmirror",)).rerunner_list()
    assert ",modelmirror-agent," not in rerunners
    assert ",mirror," not in rerunners


def _write(tmp_path: Path, text: str) -> Path:
    (tmp_path / "dispatchers.yaml").write_text(text)
    return tmp_path


def test_the_loader_reads_a_well_formed_file(tmp_path: Path) -> None:
    root = _write(
        tmp_path,
        "humans: [maintainer]\nbots:\n  run-predict.yml: ['pipeline-dispatch[bot]']\n",
    )
    assert load_dispatchers_config(root) == CONFIG


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("", id="empty file"),
        pytest.param("- maintainer\n", id="not a mapping"),
        pytest.param("bots: {}\n", id="no humans key"),
        pytest.param("humans: maintainer\n", id="humans not a list"),
        pytest.param("humans: [maintainer]\nhuman: [x]\n", id="unknown key"),
        pytest.param("humans: ['pipeline-dispatch[bot]']\n", id="bot listed as human"),
        pytest.param("humans: ['a,b']\n", id="comma in a login"),
        pytest.param("humans: ['-lead']\n", id="leading hyphen"),
        pytest.param("humans: ['']\n", id="blank login"),
        pytest.param("humans: [Maintainer, maintainer]\n", id="duplicate login"),
        pytest.param("humans: []\nbots:\n  run-predict.yml: [maintainer]\n", id="bot not [bot]"),
        pytest.param("humans: []\nbots:\n  run-predict: ['x[bot]']\n", id="bad workflow file"),
        pytest.param("humans: [maintainer\n", id="not YAML"),
    ],
)
def test_the_loader_refuses_a_malformed_file(tmp_path: Path, text: str) -> None:
    with pytest.raises(DispatchersConfigError):
        load_dispatchers_config(_write(tmp_path, text))


def test_the_loader_refuses_a_missing_file(tmp_path: Path) -> None:
    """No default allow-list: an unreadable file must refuse, never admit."""
    with pytest.raises(DispatchersConfigError, match="cannot read"):
        load_dispatchers_config(tmp_path)


def _invoke(root: Path, *, actor: str, attempt: str = "1", output: Path | None = None) -> Any:
    argv = [
        "authorize-run",
        *("--workflow", "run-predict.yml"),
        *("--event-name", "workflow_dispatch"),
        *("--actor", actor),
        *("--triggering-actor", actor),
        *("--run-attempt", attempt),
        *("--config-root", str(root)),
    ]
    if output is not None:
        argv += ["--github-output", str(output)]
    return CliRunner().invoke(app, argv)


def test_the_cli_authorizes_and_publishes_the_attempt_and_re_runners(tmp_path: Path) -> None:
    root = _write(tmp_path, "humans: [maintainer, deputy]\n")
    output = tmp_path / "github_output"
    output.write_text("earlier=kept\n")
    result = _invoke(root, actor="deputy", attempt="2", output=output)
    assert result.exit_code == 0, result.output
    assert "Authorized run-predict.yml" in result.output
    assert output.read_text() == "earlier=kept\nattempt=2\nrerunners=,maintainer,deputy,\n"


def test_the_cli_refuses_with_a_workflow_error_and_writes_no_outputs(tmp_path: Path) -> None:
    root = _write(tmp_path, "humans: [maintainer]\n")
    output = tmp_path / "github_output"
    result = _invoke(root, actor=AGENT, output=output)
    assert result.exit_code == 1
    assert "::error::" in result.output
    assert AGENT in result.output
    assert not output.exists()


def test_the_cli_refuses_on_a_missing_allow_list(tmp_path: Path) -> None:
    result = _invoke(tmp_path, actor=MAINTAINER)
    assert result.exit_code == 1
    assert "::error::" in result.output
    assert "refusing to run" in result.output
