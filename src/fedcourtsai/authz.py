"""The label-trigger authorization gate, as tested logic the workflow calls.

The label trigger is the pipeline's trust boundary (see SECURITY.md -> *Label
triggers*): an issue *form* applies its declared labels on creation regardless of
the submitter's permissions, so on a public repo anyone could fire an agent run by
filing a form that declares a ``run:*`` label. Every ``run:*`` workflow must
therefore refuse a non-write actor *before* it does any privileged work (mint a
token, assume the S3 role, run an agent).

This module is that gate, lifted out of inline workflow bash so the decision is
unit-tested rather than only lint-checked for shape. The rule: a ``Bot`` sender is
the trusted pipeline-App handoff (only a maintainer-installed App can apply a
``run:*`` label that triggers a workflow — the default ``GITHUB_TOKEN`` cannot), and
any other sender must hold ``write`` (or higher) collaborator access. Anything else
fails closed.
"""

from __future__ import annotations

import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass

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
    rather than at once, and a hostile ``run:*`` label from a non-collaborator
    on the public repo spends three API calls and those sleeps instead of one
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
