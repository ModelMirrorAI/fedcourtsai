"""The tool manifest + per-engine MCP config emission."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.mcp import (
    _COURTLISTENER_MCP_HTTP_SHIM_TEMPLATE,
    CODEX_CELL_PERMISSION_PROFILE,
    claude_mcp_config,
    codex_mcp_config,
    gemini_mcp_settings,
    http_sidecar_launch,
    manifest_labels,
)
from fedcourtsai.registry import load_mcp_servers, load_predictors, resolve_mcp_servers
from fedcourtsai.schemas import McpServerConfig

runner = CliRunner()

_SERVER = McpServerConfig(
    id="courtlistener",
    package="courtlistener-api-client[mcp]==1.1.0",
    command="courtlistener-mcp",
    token_env="COURTLISTENER_API_TOKEN",
)


def test_repo_registries_carry_the_manifest() -> None:
    for registry in (Path("config/predictors.yaml"), Path("config/evaluators.yaml")):
        manifest = load_mcp_servers(registry)
        assert [s.id for s in manifest] == ["courtlistener"]
        assert manifest[0].package.startswith("courtlistener-api-client[mcp]==")
    # Every enabled predictor references a resolvable manifest id.
    for predictor in load_predictors(Path("config/predictors.yaml")):
        resolved = resolve_mcp_servers(manifest, predictor.mcp_servers)
        assert [s.id for s in resolved] == ["courtlistener"]


def test_resolve_unknown_id_fails_loudly() -> None:
    with pytest.raises(KeyError):
        resolve_mcp_servers([_SERVER], ["typo-server"])


def test_claude_config_pins_uvx_launch_and_injects_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COURTLISTENER_API_TOKEN", "tok-agent")
    doc = json.loads(claude_mcp_config([_SERVER]))
    server = doc["mcpServers"]["courtlistener"]
    assert server["command"] == "uvx"
    # stdio runs the release's own entry point: exact-pinned package, no shim,
    # no extra dependency. Exact equality, so any future argv addition lands here.
    assert server["args"] == [
        "--from",
        "courtlistener-api-client[mcp]==1.1.0",
        "courtlistener-mcp",
    ]
    assert server["env"] == {"COURTLISTENER_API_TOKEN": "tok-agent"}


def test_the_http_bypass_is_the_only_shim_and_stays_minimal() -> None:
    # The pinned release's `create_http_app()` requires a Redis URL and forces
    # its OAuth provider, so the sidecar builds the server itself instead. That
    # bypass is the ONLY launch-time shim left: the stdio path runs the release's
    # entry point directly (asserted above), and nothing pre-seeds a session
    # store — the release falls back to an in-process TTL dict on its own.
    shim = _COURTLISTENER_MCP_HTTP_SHIM_TEMPLATE.format(port=8378)
    assert "create_mcp_server(auth=None)" in shim
    assert "transport='http'" in shim and "port=8378" in shim
    # No asset placeholders and no session-store patching: the release ships its
    # icons and handles a missing Redis URL itself.
    assert "favicon" not in shim
    assert "redis" not in shim.lower()
    compile(shim, "<shim>", "exec")  # stays valid python


def test_non_courtlistener_command_launches_directly() -> None:
    other = McpServerConfig(id="other", package="some-pkg==1.0", command="some-mcp")
    doc = json.loads(claude_mcp_config([other]))
    assert doc["mcpServers"]["other"]["args"] == ["--from", "some-pkg==1.0", "some-mcp"]


def test_unset_token_omits_env_for_anonymous_degradation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("COURTLISTENER_API_TOKEN", raising=False)
    doc = json.loads(claude_mcp_config([_SERVER]))
    assert "env" not in doc["mcpServers"]["courtlistener"]


def test_codex_config_is_valid_toml_tables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COURTLISTENER_API_TOKEN", "tok-agent")
    doc = tomllib.loads(codex_mcp_config([_SERVER]))
    table = doc["mcp_servers"]["courtlistener"]
    assert table["command"] == "uvx"
    # The pinned launch must round-trip through the JSON-escaped TOML string.
    assert table["args"] == [
        "--from",
        "courtlistener-api-client[mcp]==1.1.0",
        "courtlistener-mcp",
    ]
    assert table["env"] == {"COURTLISTENER_API_TOKEN": "tok-agent"}


def test_codex_config_declares_the_cell_permission_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # `$CODEX_HOME/config.toml` is codex's only trusted configuration layer —
    # codex-action rejects a `permissions` or `sandbox_workspace_write`
    # override arriving through `codex-args` — so the cell's filesystem and
    # network policy has to be declared here or nowhere.
    monkeypatch.delenv("COURTLISTENER_API_TOKEN", raising=False)
    # Rendered WITH a server, because the placement is what carries the meaning:
    # a bare key emitted after a table header belongs to that table, so
    # `default_permissions` appended below `[mcp_servers.*]` would parse fine
    # and select nothing — which is the startup refusal it exists to avoid.
    doc = tomllib.loads(codex_mcp_config([_SERVER]))
    # A config that declares profiles and selects none refuses to start unless
    # the invocation names a legacy sandbox mode, so the file selects its own.
    assert doc["default_permissions"] == CODEX_CELL_PERMISSION_PROFILE
    profile = doc["permissions"][CODEX_CELL_PERMISSION_PROFILE]
    # Workspace filesystem inherited verbatim; only the network half is added.
    assert profile["extends"] == ":workspace"
    # The grant that keeps codex's spawned commands able to reach the localhost
    # corpus and MCP sidecars the other engines reach unsandboxed.
    assert profile["network"] == {"enabled": True}
    # No proxy keys: codex's `network_proxy` feature layers domain/mode
    # restrictions on top, which would score codex on a smaller information set
    # than claude and gemini.
    assert set(profile["network"]) == {"enabled"}


def test_codex_config_carries_the_profile_even_with_no_servers() -> None:
    # An actor with an empty manifest still needs its permission policy: the
    # cell writes outputs into the checkout either way.
    assert CODEX_CELL_PERMISSION_PROFILE in tomllib.loads(codex_mcp_config([]))["permissions"]


def test_codex_config_holds_no_key_beyond_retrieval_and_permissions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # This emitter owns the whole trusted config document, which makes it the
    # natural place to add one more key — and the docstring's own invariant
    # (never `shell_environment_policy`, whose default strips credential-shaped
    # names from every command the agent spawns) had nothing enforcing it.
    monkeypatch.delenv("COURTLISTENER_API_TOKEN", raising=False)
    doc = tomllib.loads(codex_mcp_config([_SERVER]))
    assert set(doc) == {"default_permissions", "permissions", "mcp_servers"}


def test_gemini_settings_merge_preserves_telemetry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("COURTLISTENER_API_TOKEN", raising=False)
    base: dict[str, object] = {"telemetry": {"enabled": True, "outfile": ".gemini/telemetry.log"}}
    doc = json.loads(gemini_mcp_settings([_SERVER], base))
    assert doc["telemetry"]["enabled"] is True  # the usage capture's block survives
    assert doc["mcpServers"]["courtlistener"]["command"] == "uvx"


def test_manifest_labels_are_pinned_attribution_strings() -> None:
    assert manifest_labels([_SERVER]) == ["courtlistener=courtlistener-api-client[mcp]==1.1.0"]


def test_mcp_config_cli_unknown_actor_exits_nonzero() -> None:
    result = runner.invoke(
        app, ["mcp-config", "--engine", "claude-code", "--role", "predictor", "--actor", "nope"]
    )
    assert result.exit_code == 2


def test_mcp_config_cli_emits_for_repo_registry() -> None:
    result = runner.invoke(
        app,
        [
            "mcp-config",
            "--engine",
            "claude-code",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "courtlistener" in json.loads(result.output)["mcpServers"]


def test_http_urls_emit_remote_entries_with_no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # The tokenless-sidecar contract: an http entry carries only the URL — no
    # launch command and, even with the token set in this process's env, no
    # token anywhere in the emitted document.
    monkeypatch.setenv("COURTLISTENER_API_TOKEN", "tok-agent")
    urls = {"courtlistener": "http://127.0.0.1:8378/mcp"}

    claude = json.loads(claude_mcp_config([_SERVER], http_urls=urls))
    assert claude["mcpServers"]["courtlistener"] == {
        "type": "http",
        "url": "http://127.0.0.1:8378/mcp",
    }

    codex = codex_mcp_config([_SERVER], http_urls=urls)
    table = tomllib.loads(codex)
    assert table["mcp_servers"]["courtlistener"] == {"url": "http://127.0.0.1:8378/mcp"}

    gemini = json.loads(
        gemini_mcp_settings([_SERVER], {"telemetry": {"enabled": True}}, http_urls=urls)
    )
    assert gemini["mcpServers"]["courtlistener"] == {"httpUrl": "http://127.0.0.1:8378/mcp"}
    assert gemini["telemetry"] == {"enabled": True}  # base still composes

    for document in (json.dumps(claude), codex, json.dumps(gemini)):
        assert "tok-agent" not in document


def test_http_urls_leave_unlisted_servers_on_stdio(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COURTLISTENER_API_TOKEN", "tok-agent")
    claude = json.loads(claude_mcp_config([_SERVER], http_urls={"other": "http://x/mcp"}))
    entry = claude["mcpServers"]["courtlistener"]
    assert entry["command"] == "uvx"  # untouched: still the stdio launch
    assert entry["env"] == {"COURTLISTENER_API_TOKEN": "tok-agent"}


def test_http_sidecar_launch_builds_the_http_shim(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COURTLISTENER_API_TOKEN", "tok-agent")
    command, args, env = http_sidecar_launch(_SERVER, port=8378)
    assert command == "uvx"
    assert args[:2] == ["--from", _SERVER.package]  # no extra dependency
    shim = args[-1]
    compile(shim, "<mcp-http-shim>", "exec")  # the inline program must parse
    # The release-specific HTTP bypass: build the server directly, skipping
    # create_http_app's hard REDIS_URL requirement and its OAuth default, and
    # serve streamable HTTP on the loopback port.
    assert "create_mcp_server(auth=None)" in shim
    assert "transport='http'" in shim and "port=8378" in shim
    assert env["COURTLISTENER_API_TOKEN"] == "tok-agent"
    # The HMAC namespace key is set explicitly (a non-secret constant) to
    # quiet the release's insecure-default warning in the replayed cell log.
    assert env["MCP_SECRET_KEY"] == "cell-local-session-namespace"


def test_http_sidecar_launch_refuses_other_releases() -> None:
    # The bypass reaches into the pinned release's internals, so an unpinned bump
    # must fail loudly at launch rather than serve a server built the wrong way.
    other = McpServerConfig(
        id="courtlistener",
        package="courtlistener-api-client[mcp]==2.0.0",
        command="courtlistener-mcp",
        token_env="COURTLISTENER_API_TOKEN",
    )
    with pytest.raises(ValueError, match="revisit"):
        http_sidecar_launch(other)


def test_cli_mcp_serve_execs_the_http_sidecar_launch(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_execvpe(command: str, argv: list[str], env: dict[str, str]) -> None:
        captured["command"] = command
        captured["argv"] = argv
        captured["env"] = env
        raise SystemExit(0)  # exec never returns; the test must not either

    monkeypatch.setenv("COURTLISTENER_API_TOKEN", "tok-agent")
    monkeypatch.setattr("fedcourtsai.cli.os.execvpe", fake_execvpe)
    result = runner.invoke(
        app,
        ["mcp-serve", "--role", "predictor", "--actor", "claude-baseline", "--port", "8378"],
    )
    assert result.exit_code == 0, result.output
    assert captured["command"] == "uvx"
    argv = captured["argv"]
    assert isinstance(argv, list) and "port=8378" in argv[-1]
    env = captured["env"]
    assert isinstance(env, dict) and env["COURTLISTENER_API_TOKEN"] == "tok-agent"


def test_cli_mcp_config_http_url_rejects_malformed_entries() -> None:
    result = runner.invoke(
        app,
        [
            "mcp-config",
            "--engine",
            "claude-code",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
            "--http-url",
            "not-a-pair",
        ],
    )
    assert result.exit_code == 2
    assert "malformed --http-url" in result.stderr


def test_cli_mcp_config_http_url_rejects_unknown_server_id() -> None:
    # A typo'd id must not silently fall back to a per-client stdio spawn,
    # bypassing the sidecar the workflow meant to route through.
    result = runner.invoke(
        app,
        [
            "mcp-config",
            "--engine",
            "claude-code",
            "--role",
            "predictor",
            "--actor",
            "claude-baseline",
            "--http-url",
            "courtlistner=http://127.0.0.1:8378/mcp",
        ],
    )
    assert result.exit_code == 2
    assert "names no resolved manifest server" in result.stderr
