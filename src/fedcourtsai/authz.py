"""Who may start a run, as tested logic: the run gate and the trigger gate.

The trigger surface is the pipeline's trust boundary (see SECURITY.md ->
*Trigger surface*). Every workflow that does privileged work enters on a
``schedule``, which fires only from the default branch, a ``push``, or a
``workflow_dispatch``. The platform gates a dispatch, and a re-run of any run,
on repository write — and write is held by more than the people who should
start spend: the agent account interactive sessions act as holds it too. So
this module carries two decisions.

**The run gate** (:func:`decide_run_authorization`, CLI ``authorize-run``) is
the one every dispatchable workflow that binds a deployment environment runs as
its first job, before any other job may start. A ``workflow_dispatch`` proceeds
only when its ``actor`` is a human ``config/dispatchers.yaml`` names, or a
pipeline bot that file allows for that workflow file; a re-run (``run_attempt``
above 1, whatever the event) proceeds only when its ``triggering_actor`` is
such a human, because no pipeline bot re-runs anything. A ``schedule``,
``push`` or ``pull_request`` first attempt is chosen by no person at run time
and passes. Anything the gate cannot read — a blank actor on a dispatch, an
unparseable attempt, a missing or malformed allow-list — refuses.

Re-running *some* of a run's jobs does not re-run its authorize job: GitHub
keeps a succeeded job's result and outputs from the earlier attempt. So the
authorize job also publishes the attempt it judged and the listed humans
(:meth:`DispatchersConfig.rerunner_list`), and every other job's condition
admits it only at that attempt or for a re-runner on that list — the re-run
rule's in-job twin, one expression ``tests/test_workflow_auth_gate.py`` pins on
every job.

**The trigger gate** (:func:`authorize_trigger`, CLI ``authorize-trigger``) is
for a trigger class no workflow carries: an issue *form* applies its declared
labels on creation regardless of the submitter's permissions, so a workflow
keyed on ``issues: labeled`` — or on ``issue_comment``, or
``pull_request_target`` — could be fired by anyone, and would have to refuse a
non-write actor *before* any privileged work (mint a token, assume the S3 role,
run an agent). ``tests/test_workflow_auth_gate.py`` sweeps the directory so no
workflow takes such a trigger; this decision is here so that adding one is a
wiring change rather than a security design. The rule: a ``Bot`` sender
matching a pinned App login is the trusted App handoff (only a
maintainer-installed App can apply a label that triggers a workflow — the
default ``GITHUB_TOKEN`` cannot — and the pin refuses every other App), and any
other sender must hold ``write`` (or higher) collaborator access. Anything else
fails closed.
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

# Collaborator permission levels that may trigger a run.
WRITE_PERMISSIONS = frozenset({"admin", "maintain", "write"})

# The GitHub sender type that marks the trusted pipeline-App handoff.
_BOT_SENDER = "Bot"

# Looks up an actor's collaborator permission string (e.g. via the GitHub API).
# Injected so the decision can be tested without a network call.
PermissionLookup = Callable[[str, str], str]

# Sleeps between attempts. A parameter of :func:`_gh_permission` rather than a
# bare ``time.sleep`` call so the retry's timing is asserted, not waited out, in
# tests.
Sleeper = Callable[[float], None]

# The lookup's bounds, mirroring ``agent_feedback.py``'s default GhRunner and
# ``scripts/gh_retry.sh``: three attempts, each capped at 30s, with a
# 5s-per-attempt linear backoff, so one lookup costs at most 105s. Pinned equal
# to the ``agent_feedback`` constants by ``test_authz.py`` (which the workflow
# invariants test in turn pins against the shell wrapper), so every retried
# ``gh`` surface tolerates a degraded API for the same span.
_GH_ATTEMPTS = 3
_GH_TIMEOUT_SECONDS = 30
_GH_BACKOFF_SECONDS = 5


@dataclass(frozen=True)
class AuthDecision:
    """Whether a trigger is authorized, with the line to log either way."""

    authorized: bool
    message: str


def decide_authorization(
    sender_type: str, actor: str, permission: str, *, bot_actor: str | None = None
) -> AuthDecision:
    """Authorize a label trigger from the sender type and the actor's permission.

    Pure decision: a ``Bot`` sender is the trusted App handoff; any other sender
    needs a write-or-higher ``permission``. The ``permission`` is ignored for a
    ``Bot`` sender (the lookup is skipped upstream). ``bot_actor`` pins the
    handoff to one login: with it set, a ``Bot`` sender with any other login is
    refused outright — no permission lookup, because an App is never a
    collaborator and a lookup could only delay the refusal. Without the pin,
    "Bot" means "any admin-installed App"; every gate passes it so the branch
    means "the pipeline App". Returns the same human-facing text the workflow
    logs.
    """
    if sender_type == _BOT_SENDER:
        if bot_actor is not None and actor != bot_actor:
            return AuthDecision(
                False,
                f"{actor} is a Bot sender but not the pinned App handoff "
                + f"({bot_actor}); refusing to run.",
            )
        return AuthDecision(True, f"Authorized {actor} (pipeline App handoff).")
    if permission in WRITE_PERMISSIONS:
        return AuthDecision(True, f"Authorized {actor} ({permission} access).")
    return AuthDecision(
        False,
        f"{actor} lacks write access (permission: {permission}); refusing to run.",
    )


def _gh_permission(repo: str, actor: str, *, sleeper: Sleeper = time.sleep) -> str:
    """Default :data:`PermissionLookup`: the collaborator permission via ``gh api``.

    Mirrors the workflow's prior inline call, including its fail-closed default:
    any error (the actor is not a collaborator, the API call fails) yields
    ``"none"``, which is not a write permission, so the gate refuses.

    Bounded as ``agent_feedback.py``'s default GhRunner and ``scripts/gh_retry.sh``
    bound theirs — the same three attempts, the same 30s cap on each — because the
    fail-closed posture makes an unretried call worse than a reliability blip: a
    transient 5xx or a stalled connect at check time reads as ``"none"``, and
    ``"none"`` refuses, so an API blip costs a legitimate actor the round. The
    per-attempt timeout is what bounds the stall itself: ``gh`` sets no
    client-side request timeout, so an unbounded stalled connect hangs the gate
    to the job's own kill.

    Retrying never converts a refusal into an allow, because no failure path
    manufactures a permission: an allow requires a *successful* API response
    naming a write-level permission, and a successful attempt's answer — whatever
    it names — is returned immediately, never retried for a better one. Errors
    only ever become ``"none"``, exhaustion included. What the retry absorbs is
    the converse: a legitimate collaborator behind one blip is looked up again
    instead of refused. Two symmetric costs are accepted as the shell wrapper
    accepts its own: a *genuine* refusal reached through an error — a
    non-collaborator's 404 — is also retried, landing after ~15s of backoff
    rather than at once, and a hostile trigger from a non-collaborator
    on a public repo spends three API calls and those sleeps instead of one
    call — bounded amplification, cheaper than buying a transient/genuine
    classifier out of ``gh``'s exit codes, which would cost more in reviewable
    authorization surface than the sleeps are worth.

    An :class:`OSError` — ``gh`` itself missing or unexecutable — yields
    ``"none"`` on the first attempt, unretried: that fault is deterministic, and
    three attempts would only delay the refusal. It is annotated like an
    exhaustion, so the job log can tell "the lookup never ran" apart from "the
    actor is not a collaborator" — both refuse, but only one is about the actor.
    The annotations go to this process's stderr, naming only the first three
    argv words. That slice carries the repo and actor (they ride in the API
    path); the actor is already in the decision line the workflow logs, the repo
    is the workflow's own ``github.repository``, named throughout the job log,
    and no secret is ever in this argv.

    ``sleeper`` is a seam for tests; production never passes it, so the injected
    :data:`PermissionLookup` signature is unchanged.
    """
    # Both interpolations below are server-provided GitHub identifiers
    # (`github.repository` / `github.actor` at every workflow call site), whose
    # charsets admit no `::` and no newline — the precondition that keeps the
    # API path and the printed annotation inert. Re-check it before wiring
    # either value from anything user-authored (an issue body, a form field).
    argv: Sequence[str] = [
        "gh",
        "api",
        f"repos/{repo}/collaborators/{actor}/permission",
        "--jq",
        ".permission",
    ]
    what = " ".join(argv[:3])
    attempt = 1
    while True:
        try:
            result = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                check=True,
                timeout=_GH_TIMEOUT_SECONDS,
            )
        except OSError:
            print(f"::error::{what} could not be executed", file=sys.stderr)
            return "none"
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            if attempt >= _GH_ATTEMPTS:
                print(f"::error::{what} failed after {_GH_ATTEMPTS} attempts", file=sys.stderr)
                return "none"
            print(
                f"::warning::{what} failed (attempt {attempt}/{_GH_ATTEMPTS}) — retrying",
                file=sys.stderr,
            )
            sleeper(attempt * _GH_BACKOFF_SECONDS)
            attempt += 1
        else:
            return result.stdout.strip() or "none"


def authorize_trigger(
    sender_type: str,
    actor: str,
    repo: str,
    *,
    lookup: PermissionLookup = _gh_permission,
    bot_actor: str | None = None,
) -> AuthDecision:
    """Resolve the authorization decision, looking up the actor's permission if needed.

    A ``Bot`` sender resolves without a lookup — authorized as the App handoff,
    or refused outright when ``bot_actor`` pins the handoff to a different
    login; any other sender's collaborator permission is fetched via ``lookup``
    (default: the GitHub API) and fed to :func:`decide_authorization`. The
    ``lookup`` seam lets tests exercise the gate without a network call.
    """
    permission = "" if sender_type == _BOT_SENDER else lookup(repo, actor)
    return decide_authorization(sender_type, actor, permission, bot_actor=bot_actor)


# --- The run gate -----------------------------------------------------------

#: The allow-list the run gate reads, under the config root.
DISPATCHERS_FILENAME = "dispatchers.yaml"

#: The one event a person chooses to fire at run time.
DISPATCH_EVENT = "workflow_dispatch"

# A GitHub user login: alphanumerics and single hyphens, at most 39 characters,
# never leading with a hyphen. Checked so a typo cannot widen the gate and so
# no login carries the comma the published re-runner list delimits on.
_HUMAN_LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
# An App's bot account: the App slug plus the literal ``[bot]`` suffix, which no
# user login can carry — so a bot entry can never name a person.
_BOT_LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})\[bot\]$")
# A workflow file name under ``.github/workflows/``, as each workflow passes it.
_WORKFLOW_FILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.ya?ml$")


class DispatchersConfigError(ValueError):
    """The allow-list is missing or malformed; the run gate refuses on it."""


def _no_duplicates(logins: Sequence[str], what: str) -> None:
    folded = [login.casefold() for login in logins]
    if len(set(folded)) != len(folded):
        raise ValueError(f"{what} lists a login twice (logins compare case-insensitively)")


class DispatchersConfig(BaseModel):
    """Who may start a run by hand or re-run one (``config/dispatchers.yaml``).

    ``humans`` may dispatch any gated workflow and re-run any run of one;
    ``bots`` maps a workflow file to the pipeline bot logins that may dispatch
    *that* workflow, and never re-run anything. Unknown keys are refused, so a
    misspelled section cannot read as an empty one.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    humans: tuple[str, ...]
    bots: dict[str, tuple[str, ...]] = Field(default_factory=dict)

    @field_validator("humans")
    @classmethod
    def _humans_are_user_logins(cls, humans: tuple[str, ...]) -> tuple[str, ...]:
        for login in humans:
            if not _HUMAN_LOGIN.fullmatch(login):
                raise ValueError(f"humans: {login!r} is not a GitHub user login")
        _no_duplicates(humans, "humans")
        return humans

    @field_validator("bots")
    @classmethod
    def _bots_are_app_logins(cls, bots: dict[str, tuple[str, ...]]) -> dict[str, tuple[str, ...]]:
        for workflow, logins in bots.items():
            if not _WORKFLOW_FILE.fullmatch(workflow):
                raise ValueError(f"bots: {workflow!r} is not a workflow file name")
            for login in logins:
                if not _BOT_LOGIN.fullmatch(login):
                    raise ValueError(
                        f"bots.{workflow}: {login!r} is not an App bot login (<slug>[bot])"
                    )
            _no_duplicates(logins, f"bots.{workflow}")
        return bots

    def is_human(self, login: str) -> bool:
        """Whether ``login`` is a listed human (GitHub logins are case-insensitive)."""
        folded = login.casefold()
        return any(human.casefold() == folded for human in self.humans)

    def is_dispatch_bot(self, login: str, workflow_file: str) -> bool:
        """Whether ``login`` is a bot this file allows to dispatch ``workflow_file``."""
        folded = login.casefold()
        return any(bot.casefold() == folded for bot in self.bots.get(workflow_file, ()))

    def rerunner_list(self) -> str:
        """The humans as one comma-delimited string, delimiters at both ends.

        The authorize job publishes it as an output, so a job re-run alone — which
        does not re-run the authorize job — can test its own re-runner with
        ``contains(<list>, format(',{0},', github.triggering_actor))``. The
        leading and trailing comma make that an exact-login match (no login
        holds a comma), and an empty allow-list publishes the empty string,
        which contains no delimited login, rather than ``,,``.
        """
        return f",{','.join(self.humans)}," if self.humans else ""


def load_dispatchers_config(config_root: Path) -> DispatchersConfig:
    """Read and validate ``config_root/dispatchers.yaml``.

    Raises :class:`DispatchersConfigError` when the file is absent, is not
    YAML, or does not validate. There is no default: an allow-list that cannot
    be read must refuse every gated start, never admit one.
    """
    path = config_root / DISPATCHERS_FILENAME
    try:
        text = path.read_text()
    except OSError as exc:
        raise DispatchersConfigError(f"cannot read {path}: {exc.strerror or exc}") from exc
    try:
        data: Any = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise DispatchersConfigError(f"{path} is not valid YAML: {exc}") from exc
    if not isinstance(data, Mapping):
        raise DispatchersConfigError(f"{path} must be a mapping with a `humans` list")
    try:
        return DispatchersConfig.model_validate(data)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
        raise DispatchersConfigError(f"{path} is malformed: {problems}") from exc


def _parse_attempt(run_attempt: str) -> int | None:
    text = run_attempt.strip()
    if not text.isascii() or not text.isdigit():
        return None
    attempt = int(text)
    return attempt if attempt >= 1 else None


def _dispatch_grant(actor: str, workflow_file: str, config: DispatchersConfig) -> tuple[bool, str]:
    """The dispatch rule: ``(allowed, reason-or-refusal)`` for a dispatch's actor."""
    if not actor.strip():
        return False, "a dispatch with no actor; refusing to run."
    if config.is_human(actor):
        return True, f"dispatched by {actor}, a listed dispatcher"
    if config.is_dispatch_bot(actor, workflow_file):
        return True, f"dispatched by {actor}, a pipeline bot allowed for {workflow_file}"
    return False, (
        f"{actor} may not dispatch {workflow_file}: not a human in "
        + f"config/{DISPATCHERS_FILENAME}, nor a bot it allows for this "
        + "workflow; refusing to run."
    )


def _rerun_grant(
    triggering_actor: str, attempt: int, config: DispatchersConfig
) -> tuple[bool, str]:
    """The re-run rule: ``(allowed, reason-or-refusal)`` for a re-run's starter."""
    if not triggering_actor.strip():
        return False, f"re-run attempt {attempt} names no triggering actor; refusing to run."
    if config.is_human(triggering_actor):
        return True, f"re-run (attempt {attempt}) by {triggering_actor}, a listed re-runner"
    return False, (
        f"{triggering_actor} may not re-run this run (attempt {attempt}): not a "
        + f"human in config/{DISPATCHERS_FILENAME}; refusing to run."
    )


def decide_run_authorization(
    *,
    event_name: str,
    actor: str,
    triggering_actor: str,
    run_attempt: str,
    workflow_file: str,
    config: DispatchersConfig,
) -> AuthDecision:
    """Whether a run (or a re-run of one) may proceed past its authorize job.

    Pure decision over the GitHub context the authorize job passes in. Both
    rules apply cumulatively, so a re-run of a hand-started run needs a listed
    dispatcher *and* a listed re-runner:

    - a ``workflow_dispatch`` — at every attempt, since ``actor`` stays the
      dispatcher's across re-runs — needs ``actor`` among the humans, or among
      the bots allowed for ``workflow_file``;
    - any attempt above the first needs ``triggering_actor`` among the humans.

    Any other first attempt passes: a schedule, a push or a pull request is not
    chosen by a person at run time. A blank event, workflow file or needed
    login, or an attempt that is not a positive integer, refuses.
    """
    attempt = _parse_attempt(run_attempt)
    if attempt is None:
        return AuthDecision(
            False, f"run attempt {run_attempt!r} is not a positive integer; refusing to run."
        )
    if not event_name.strip() or not workflow_file.strip():
        return AuthDecision(
            False, "the run names no triggering event or no workflow file; refusing to run."
        )
    grants: list[tuple[bool, str]] = []
    if event_name == DISPATCH_EVENT:
        grants.append(_dispatch_grant(actor, workflow_file, config))
    if attempt > 1:
        grants.append(_rerun_grant(triggering_actor, attempt, config))
    for allowed, text in grants:
        if not allowed:
            return AuthDecision(False, text)
    reasons = [text for _, text in grants] or [
        f"{event_name} first attempt, chosen by no person at run time"
    ]
    return AuthDecision(True, f"Authorized {workflow_file}: " + "; ".join(reasons) + ".")
