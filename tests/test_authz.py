"""The label-trigger authorization gate (:mod:`fedcourtsai.authz`).

The security shape — that the gate runs before any privileged step — is locked in
``test_workflow_auth_gate.py``; this exercises the *decision* the workflow now
delegates to the ``authorize-trigger`` command: a Bot handoff is trusted, write
access is required otherwise, and anything else fails closed.
"""

from __future__ import annotations

from collections.abc import Callable

from fedcourtsai.authz import authorize_trigger, decide_authorization


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
