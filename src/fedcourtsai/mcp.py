"""Per-engine MCP client configuration, emitted from the tool manifest.

One manifest (``mcp_servers:`` in the actor registry), three client formats:
Claude Code reads an ``--mcp-config`` JSON file, Codex reads
``$CODEX_HOME/config.toml`` ``[mcp_servers.*]`` tables, and the Gemini CLI
reads ``mcpServers`` in ``.gemini/settings.json``. The tested emitters here
keep the three in lockstep so the workflow steps only plumb bytes to files
(the logic-in-tested-Python rule).

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

Either way an unset token only degrades the cell: on this pinned release the
server starts and its CourtListener tool calls error (the client refuses to
run tokenless), so the agent falls back to corpus tooling per the prompt
contract — a degraded upstream degrades the cell, never blocks it.
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


# WORKAROUND for two bugs in courtlistener-api-client 1.0.0 (its only
# release), both keyed to the exact broken release so bumping the manifest pin
# self-retires the shim back to the plain entry point — delete this block once
# a fixed release is pinned.
#
# 1. Missing assets: `create_mcp_server()` reads bundled icon files from
#    `courtlistener/mcp/assets/`, but neither the wheel nor the sdist ships
#    that directory, so the `courtlistener-mcp` entry point crashes on startup
#    with FileNotFoundError — on every engine ("MCP issues detected" in
#    Gemini, silently zero MCP tools in Claude/Codex). The shim writes
#    placeholder icon bytes (they are only base64-embedded into the server's
#    icon metadata) before calling the same `main()`.
# 2. Redis-only session store: the `search` and `call_endpoint` tools
#    unconditionally store pagination state (the query_id resume mechanism)
#    through `tools.utils.get_redis()`, which raises "REDIS_URL is not set;
#    cannot access session store." when no Redis is configured. HTTP mode
#    requires REDIS_URL at startup, but stdio mode — what the cells use —
#    starts cleanly and then fails on every retrieval call. The shim pre-seeds
#    the module-level client with an in-process fakeredis instance
#    (`--with` below), which is the right scope for a single-cell stdio
#    session: the store only ever holds this one session's resume state.
_BROKEN_COURTLISTENER_RELEASE = "courtlistener-api-client[mcp]==1.0.0"
_COURTLISTENER_FAKEREDIS_PIN = "fakeredis==2.36.2"
_COURTLISTENER_MCP_SHIM = (
    "import pathlib\n"
    "import courtlistener.mcp\n"
    "assets = pathlib.Path(courtlistener.mcp.__file__).parent / 'assets'\n"
    "assets.mkdir(exist_ok=True)\n"
    "for name, blob in (\n"
    "    ('favicon.svg', b\"<svg xmlns='http://www.w3.org/2000/svg'/>\"),\n"
    "    ('apple-touch-icon.png', b'\\x89PNG\\r\\n\\x1a\\n'),\n"
    "    ('favicon.ico', b''),\n"
    "):\n"
    "    path = assets / name\n"
    "    if not path.exists():\n"
    "        path.write_bytes(blob)\n"
    "import courtlistener.mcp.tools.utils as utils\n"
    "import fakeredis.aioredis\n"
    "utils.redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)\n"
    "from courtlistener.mcp.server import main\n"
    "main()\n"
)


# The HTTP-mode variant of the shim, for the tokenless sidecar (CI cells).
# Same asset placeholders and in-process fakeredis preseed (per-process state
# is the right scope for one cell's single session), but instead of the stdio
# entry point it builds the FastMCP server directly via
# ``create_mcp_server(auth=None)`` — which sidesteps ``create_http_app()``'s
# hard REDIS_URL requirement and its OAuth default (the sidecar authenticates
# to CourtListener with the token in its own env; localhost clients send no
# credential) — and serves streamable HTTP on a loopback port. The trailing
# ``{port}`` placeholder is formatted in by :func:`http_sidecar_launch`.
_COURTLISTENER_MCP_HTTP_SHIM_TEMPLATE = (
    "import pathlib\n"
    "import courtlistener.mcp\n"
    "assets = pathlib.Path(courtlistener.mcp.__file__).parent / 'assets'\n"
    "assets.mkdir(exist_ok=True)\n"
    "for name, blob in (\n"
    "    ('favicon.svg', b\"<svg xmlns='http://www.w3.org/2000/svg'/>\"),\n"
    "    ('apple-touch-icon.png', b'\\x89PNG\\r\\n\\x1a\\n'),\n"
    "    ('favicon.ico', b''),\n"
    "):\n"
    "    path = assets / name\n"
    "    if not path.exists():\n"
    "        path.write_bytes(blob)\n"
    "import courtlistener.mcp.tools.utils as utils\n"
    "import fakeredis.aioredis\n"
    "utils.redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)\n"
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
    if server.package == _BROKEN_COURTLISTENER_RELEASE:
        # The two-bug workaround above; same pinned package, same env.
        return (
            "uvx",
            [
                "--with",
                _COURTLISTENER_FAKEREDIS_PIN,
                "--from",
                server.package,
                "python",
                "-c",
                _COURTLISTENER_MCP_SHIM,
            ],
            env,
        )
    return "uvx", ["--from", server.package, server.command], env


def http_sidecar_launch(
    server: McpServerConfig, *, port: int = MCP_SIDECAR_DEFAULT_PORT
) -> tuple[str, list[str], dict[str, str]]:
    """(command, args, env) to run one manifest entry as the HTTP sidecar.

    The env carries the server's API token (read from this process's
    environment, exactly like the stdio launch) — the caller runs the sidecar
    in a step whose env holds it, and no client config ever does. Keyed to
    the pinned broken release like the shim above: the HTTP bypass is
    release-specific by construction, so a manifest bump must revisit it
    (a fixed release presumably serves HTTP through its own entry point).
    """
    if server.package != _BROKEN_COURTLISTENER_RELEASE:
        raise ValueError(
            f"the HTTP sidecar launch is built for {_BROKEN_COURTLISTENER_RELEASE}; "
            f"revisit it for {server.package} (a fixed release may serve HTTP natively)"
        )
    env: dict[str, str] = {}
    if server.token_env:
        token = os.environ.get(server.token_env, "")
        if token:
            env[server.token_env] = token
    # Not a secret: the release's HMAC key only namespaces this process's
    # in-process fakeredis keys, which never leave it. Setting it explicitly
    # quiets the release's insecure-default warning in every cell log.
    env["MCP_SECRET_KEY"] = "cell-local-fakeredis-namespace"
    return (
        "uvx",
        [
            "--with",
            _COURTLISTENER_FAKEREDIS_PIN,
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
    """The ``[mcp_servers.*]`` TOML tables for ``$CODEX_HOME/config.toml``.

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
    blocks: list[str] = []
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
    return "\n\n".join(blocks) + ("\n" if blocks else "")


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
