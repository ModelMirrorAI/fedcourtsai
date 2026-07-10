"""Per-engine MCP client configuration, emitted from the tool manifest (#525).

One manifest (``mcp_servers:`` in the actor registry), three client formats:
Claude Code reads an ``--mcp-config`` JSON file, Codex reads
``$CODEX_HOME/config.toml`` ``[mcp_servers.*]`` tables, and the Gemini CLI
reads ``mcpServers`` in ``.gemini/settings.json``. The tested emitters here
keep the three in lockstep so the workflow steps only plumb bytes to files
(the logic-in-tested-Python rule).

Every server launches as ``uvx --from <pinned package> <command>`` over stdio
— resolution is pinned by the manifest and needs no separate install step —
and its API token is injected as a **literal env value read from this
process's environment at emission time**. The emitting step runs on the
ephemeral cell runner with the token already in its env; the generated file is
workspace-local, gitignored, and never part of the uploaded artifact, so the
exposure equals the env var's own. Literal injection is the one shape all
three clients honor identically (env-expansion syntax support varies). An
unset token emits no env entry: the server runs at anonymous rate limits
rather than failing the cell (the degraded-upstream posture).
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


def _launch(server: McpServerConfig) -> tuple[str, list[str], dict[str, str]]:
    """(command, args, env) for one manifest entry's stdio launch."""
    env: dict[str, str] = {}
    if server.token_env:
        token = os.environ.get(server.token_env, "")
        if token:
            env[server.token_env] = token
    return "uvx", ["--from", server.package, server.command], env


def claude_mcp_config(servers: list[McpServerConfig]) -> str:
    """The ``--mcp-config`` JSON document for Claude Code."""
    doc = {
        "mcpServers": {
            server.id: {
                "command": command,
                "args": args,
                **({"env": env} if env else {}),
            }
            for server in servers
            for command, args, env in [_launch(server)]
        }
    }
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def codex_mcp_config(servers: list[McpServerConfig]) -> str:
    """The ``[mcp_servers.*]`` TOML tables for ``$CODEX_HOME/config.toml``.

    Rendered by hand (the shape is three flat keys per table) so the runtime
    needs no TOML writer dependency; ids and packages come from the validated
    manifest, and values are JSON-escaped, which is valid TOML for strings.
    """
    blocks: list[str] = []
    for server in servers:
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
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def gemini_mcp_settings(
    servers: list[McpServerConfig], base: dict[str, object] | None = None
) -> str:
    """The ``.gemini/settings.json`` document with ``mcpServers`` merged in.

    ``base`` carries the workflow's existing settings (the telemetry block the
    usage-capture step depends on) so this emitter composes rather than
    clobbers.
    """
    doc: dict[str, object] = dict(base or {})
    doc["mcpServers"] = {
        server.id: {
            "command": command,
            "args": args,
            **({"env": env} if env else {}),
        }
        for server in servers
        for command, args, env in [_launch(server)]
    }
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def manifest_labels(servers: list[McpServerConfig]) -> list[str]:
    """The attribution strings recorded per cell: ``<id>=<pinned package>``."""
    return [f"{server.id}={server.package}" for server in servers]
