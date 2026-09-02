"""Per-engine MCP client configuration, emitted from the tool manifest.

One manifest (``mcp_servers:`` in the actor registry), three client formats:
Claude Code reads an ``--mcp-config`` JSON file, Codex reads
``$CODEX_HOME/config.toml`` ``[mcp_servers.*]`` tables, and the Gemini CLI
reads ``mcpServers`` in ``.gemini/settings.json``. The tested emitters here
keep the three in lockstep so the workflow steps only plumb bytes to files
(the logic-in-tested-Python rule). The codex emitter carries one thing beyond
retrieval — the cell's permission profile — because that file is codex's only
trusted configuration layer; see :func:`codex_mcp_config`.

Two transports, one manifest:

- **stdio** (the default; local runs): the client spawns the server via
  ``uvx --from <pinned package>`` — resolution is pinned by the manifest and
  needs no separate install step — and its API token is injected as a
  **literal env value read from this process's environment at emission
  time**. The emitting step runs on the ephemeral cell runner with the token
  already in its env; the generated file is workspace-local, gitignored, and
  never part of the uploaded artifact — but it *is* readable by the agent's
  file tools, which is why CI moved off this transport.
- **HTTP sidecar** (CI cells; a per-server URL passed to the emitters): the
  workflow launches the server once as a background localhost service
  (``fedcourts mcp-serve``) whose *own step env* holds the token, and the
  emitted configs carry only the localhost URL — no token in any file an
  agent can read, and one server per cell instead of one per client spawn.

Either way an unset token only degrades the cell: the server starts and its
CourtListener tool calls error (the client refuses to run tokenless), so the
agent falls back to corpus tooling per the prompt contract — a degraded
upstream degrades the cell, never blocks it.
"""

from __future__ import annotations

import json
import os

from .schemas import McpServerConfig

# The generated client-config filenames, referenced by the workflows and
# .gitignore. Grouped here so a rename stays one diff.
CLAUDE_MCP_CONFIG_FILENAME = "mcp-servers.json"
CODEX_CONFIG_FILENAME = "config.toml"
GEMINI_SETTINGS_FILENAME = "settings.json"

# The HTTP sidecar's default port; the corpus query sidecar holds 8377.
MCP_SIDECAR_DEFAULT_PORT = 8378

# The permission profile a codex cell runs under, named here because both ends
# of the invocation read it from this one constant: the emitted config.toml
# declares it, and the cell workflows select it through codex-action's
# `permission-profile:` input (which reaches the CLI as
# `--config default_permissions="<name>"`).
#
# Codex ships three built-in profiles — `:read-only`, `:workspace`,
# `:danger-full-access` — and none of them combines workspace writes with
# network. The cell needs both: it writes its outputs into the checkout and its
# spawned commands must reach the localhost corpus and MCP sidecars that claude
# and gemini reach unsandboxed. So the profile below extends `:workspace` (the
# filesystem half, verbatim) and turns the network half on.
CODEX_CELL_PERMISSION_PROFILE = "fedcourts-cell"

# `network.enabled = true` compiles to an unrestricted network policy for
# sandboxed commands. It is deliberately the only network key here: codex's
# `network_proxy` feature would layer domain/mode restrictions on top, which
# would put codex on a strictly smaller information set than the engines it is
# scored against — the cross-engine comparability the leaderboard rests on.
#
# The file-level `default_permissions` is not redundant with the workflows'
# `permission-profile:` input. A config that declares `[permissions]` profiles
# and selects none refuses to start unless the invocation names a legacy
# sandbox mode, so a codex process reading this home without `--sandbox` —
# `codex login`, an interactive local run — would die on a config it did not
# write. Naming the selection here makes the file valid on its own; the cell
# steps still pass the same name, and the runner's `--sandbox workspace-write`
# puts that invocation on the legacy path where this selection is inert.
#
# It also decides what a *local* codex run gets, which is the one place this
# reaches beyond CI: point `CODEX_HOME` at a generated config and an interactive
# codex works under the cell's policy — workspace writes plus network for
# spawned commands — where codex's own default for that home would restrict
# network. That is the cell's posture by design, and worth knowing before
# pointing a local session at it.
_CODEX_PERMISSION_PROFILE_TOML = f"""\
default_permissions = "{CODEX_CELL_PERMISSION_PROFILE}"

[permissions.{CODEX_CELL_PERMISSION_PROFILE}]
description = "fedcourtsai cell: workspace writes plus network for spawned commands"
extends = ":workspace"

[permissions.{CODEX_CELL_PERMISSION_PROFILE}.network]
enabled = true"""


# The HTTP sidecar cannot use the release's own HTTP entry point.
# ``create_http_app()`` hard-raises without ``REDIS_URL`` and forces its OAuth
# provider (``auth=build_auth()``), neither of which fits a loopback sidecar that
# authenticates to CourtListener with the token in its own env while localhost
# clients send no credential at all. So the sidecar builds the FastMCP server
# directly — ``create_mcp_server(auth=None)`` — and serves streamable HTTP on a
# loopback port itself, sidestepping both. Keyed to the pinned release, because
# it depends on that release's internals: a manifest bump must re-check whether
# the constructor still accepts this shape, and whether HTTP mode has grown a
# configuration that no longer needs the bypass.
#
# The *stdio* launch needs no such treatment: the ``courtlistener-mcp`` entry
# point starts cleanly and its session store falls back to an in-process
# TTL dict when ``REDIS_URL`` is unset, which is the right scope for one cell's
# single session.
_HTTP_BYPASS_RELEASE = "courtlistener-api-client[mcp]==1.1.0"
_COURTLISTENER_MCP_HTTP_SHIM_TEMPLATE = (
    "from courtlistener.mcp.server import create_mcp_server\n"
    "mcp = create_mcp_server(auth=None)\n"
    "mcp.run(transport='http', host='127.0.0.1', port={port}, stateless_http=True)\n"
)


def _launch(server: McpServerConfig) -> tuple[str, list[str], dict[str, str]]:
    """(command, args, env) for one manifest entry's stdio launch."""
    env: dict[str, str] = {}
    if server.token_env:
        token = os.environ.get(server.token_env, "")
        if token:
            env[server.token_env] = token
    return "uvx", ["--from", server.package, server.command], env


def http_sidecar_launch(
    server: McpServerConfig, *, port: int = MCP_SIDECAR_DEFAULT_PORT
) -> tuple[str, list[str], dict[str, str]]:
    """(command, args, env) to run one manifest entry as the HTTP sidecar.

    The env carries the server's API token (read from this process's
    environment, exactly like the stdio launch) — the caller runs the sidecar
    in a step whose env holds it, and no client config ever does. Keyed to the
    pinned release like the bypass above, because it reaches into that release's
    internals: a bump must re-check that the constructor still takes this shape
    and that HTTP mode still needs the bypass at all.
    """
    if server.package != _HTTP_BYPASS_RELEASE:
        raise ValueError(
            f"the HTTP sidecar launch is built for {_HTTP_BYPASS_RELEASE}; "
            f"revisit it for {server.package} — check whether create_http_app still "
            f"requires Redis and OAuth, and whether create_mcp_server still accepts auth=None"
        )
    env: dict[str, str] = {}
    if server.token_env:
        token = os.environ.get(server.token_env, "")
        if token:
            env[server.token_env] = token
    # Not a secret: the release's HMAC key only namespaces this process's
    # in-memory session keys, which never leave it. Setting it explicitly quiets
    # the release's insecure-default warning in every cell log.
    env["MCP_SECRET_KEY"] = "cell-local-session-namespace"
    return (
        "uvx",
        [
            "--from",
            server.package,
            "python",
            "-c",
            _COURTLISTENER_MCP_HTTP_SHIM_TEMPLATE.format(port=port),
        ],
        env,
    )


def _claude_entry(server: McpServerConfig, http_urls: dict[str, str]) -> dict[str, object]:
    url = http_urls.get(server.id)
    if url is not None:
        return {"type": "http", "url": url}
    command, args, env = _launch(server)
    return {"command": command, "args": args, **({"env": env} if env else {})}


def claude_mcp_config(
    servers: list[McpServerConfig], *, http_urls: dict[str, str] | None = None
) -> str:
    """The ``--mcp-config`` JSON document for Claude Code.

    A server whose id appears in ``http_urls`` is emitted as a remote
    streamable-HTTP entry — a localhost URL, no launch command, **no token**;
    the rest keep the stdio launch.
    """
    doc = {"mcpServers": {server.id: _claude_entry(server, http_urls or {}) for server in servers}}
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def codex_mcp_config(
    servers: list[McpServerConfig], *, http_urls: dict[str, str] | None = None
) -> str:
    """The whole ``$CODEX_HOME/config.toml`` document a codex cell reads.

    Two halves: the ``[mcp_servers.*]`` retrieval entries, and the
    ``[permissions.*]`` profile the cell runs under
    (:data:`CODEX_CELL_PERMISSION_PROFILE`) with the ``default_permissions``
    key that selects it. The profile lives here rather than
    in the workflows because ``$CODEX_HOME/config.toml`` is the only *trusted*
    codex configuration layer — codex-action rejects a ``permissions`` or
    ``sandbox_workspace_write`` override arriving through ``codex-args`` — so
    the file this emitter writes is where a cell's filesystem and network
    policy has to be declared, and one tested emitter keeps every workflow that
    writes it identical.

    Rendered by hand (the shape is a few flat keys per table) so the runtime
    needs no TOML writer dependency; ids and packages come from the validated
    manifest, and values are JSON-escaped, which is valid TOML for strings.
    A server whose id appears in ``http_urls`` is emitted as a remote
    streamable-HTTP entry (``url`` only — no launch command, no token).

    This document must never set ``shell_environment_policy``: codex's default
    strips credential-shaped names from the env of every command the agent
    spawns, and the cell workflows' subprocess-network grant leans on that
    default — overriding it is a security-review decision, not a config tweak.
    """
    urls = http_urls or {}
    blocks: list[str] = [_CODEX_PERMISSION_PROFILE_TOML]
    for server in servers:
        url = urls.get(server.id)
        if url is not None:
            # `url` selects codex's streamable-HTTP client transport (native
            # at current CLI releases; the action installs latest — confirm
            # on the first real run after a CLI jump).
            blocks.append(f"[mcp_servers.{server.id}]\nurl = {json.dumps(url)}")
            continue
        command, args, env = _launch(server)
        lines = [
            f"[mcp_servers.{server.id}]",
            f"command = {json.dumps(command)}",
            f"args = {json.dumps(args)}",
        ]
        if env:
            pairs = ", ".join(f"{key} = {json.dumps(value)}" for key, value in env.items())
            lines.append(f"env = {{ {pairs} }}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def _gemini_entry(server: McpServerConfig, http_urls: dict[str, str]) -> dict[str, object]:
    url = http_urls.get(server.id)
    if url is not None:
        # `httpUrl` selects the streamable-HTTP client transport (`url` would
        # mean SSE), verified live against the pinned CLI release.
        return {"httpUrl": url}
    command, args, env = _launch(server)
    return {"command": command, "args": args, **({"env": env} if env else {})}


def gemini_mcp_settings(
    servers: list[McpServerConfig],
    base: dict[str, object] | None = None,
    *,
    http_urls: dict[str, str] | None = None,
) -> str:
    """The ``.gemini/settings.json`` document with ``mcpServers`` merged in.

    ``base`` carries the workflow's existing settings (the telemetry block the
    usage-capture step depends on) so this emitter composes rather than
    clobbers. A server whose id appears in ``http_urls`` is emitted as a
    remote streamable-HTTP entry (no launch command, no token).
    """
    doc: dict[str, object] = dict(base or {})
    doc["mcpServers"] = {server.id: _gemini_entry(server, http_urls or {}) for server in servers}
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def manifest_labels(servers: list[McpServerConfig]) -> list[str]:
    """The attribution strings recorded per cell: ``<id>=<pinned package>``."""
    return [f"{server.id}={server.package}" for server in servers]


def manifest_tools(servers: list[McpServerConfig]) -> list[str]:
    """The tool names those pinned servers advertise — a cell's OFFERED set.

    Qualified ``<server id>.<tool>`` so two servers advertising the same bare
    name stay distinct, and sorted for a stable record. Servers whose ``tools``
    is unrecorded contribute nothing, which reads as offered-unknown rather than
    nothing-offered — the caller cannot tell the two apart from this list alone,
    which is why the manifest records the list rather than deriving it.
    """
    return sorted(f"{server.id}.{tool}" for server in servers for tool in server.tools)
