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
from collections.abc import Callable, Sequence
from dataclasses import dataclass

# Collaborator permission levels that may trigger a run.
WRITE_PERMISSIONS = frozenset({"admin", "maintain", "write"})

# The GitHub sender type that marks the trusted pipeline-App handoff.
_BOT_SENDER = "Bot"

# Looks up an actor's collaborator permission string (e.g. via the GitHub API).
# Injected so the decision can be tested without a network call.
PermissionLookup = Callable[[str, str], str]


@dataclass(frozen=True)
class AuthDecision:
    """Whether a trigger is authorized, with the line to log either way."""

    authorized: bool
    message: str


def decide_authorization(sender_type: str, actor: str, permission: str) -> AuthDecision:
    """Authorize a label trigger from the sender type and the actor's permission.

    Pure decision: a ``Bot`` sender is the trusted App handoff; any other sender
    needs a write-or-higher ``permission``. The ``permission`` is ignored for a
    ``Bot`` sender (the lookup is skipped upstream). Returns the same human-facing
    text the workflow logs.
    """
    if sender_type == _BOT_SENDER:
        return AuthDecision(True, f"Authorized {actor} (pipeline App handoff).")
    if permission in WRITE_PERMISSIONS:
        return AuthDecision(True, f"Authorized {actor} ({permission} access).")
    return AuthDecision(
        False,
        f"{actor} lacks write access (permission: {permission}); refusing to run.",
    )


def _gh_permission(repo: str, actor: str) -> str:
    """Default :data:`PermissionLookup`: the collaborator permission via ``gh api``.

    Mirrors the workflow's prior inline call, including its fail-closed default:
    any error (the actor is not a collaborator, the API call fails) yields
    ``"none"``, which is not a write permission, so the gate refuses.
    """
    argv: Sequence[str] = [
        "gh",
        "api",
        f"repos/{repo}/collaborators/{actor}/permission",
        "--jq",
        ".permission",
    ]
    try:
        result = subprocess.run(argv, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return "none"
    return result.stdout.strip() or "none"


def authorize_trigger(
    sender_type: str,
    actor: str,
    repo: str,
    *,
    lookup: PermissionLookup = _gh_permission,
) -> AuthDecision:
    """Resolve the authorization decision, looking up the actor's permission if needed.

    A ``Bot`` sender authorizes without a lookup; any other sender's collaborator
    permission is fetched via ``lookup`` (default: the GitHub API) and fed to
    :func:`decide_authorization`. The ``lookup`` seam lets tests exercise the gate
    without a network call.
    """
    permission = "" if sender_type == _BOT_SENDER else lookup(repo, actor)
    return decide_authorization(sender_type, actor, permission)
