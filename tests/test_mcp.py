"""The tool manifest + per-engine MCP config emission."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.mcp import (
    _COURTLISTENER_MCP_SHIM,
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
    package="courtlistener-api-client[mcp]==1.0.0",
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
    # The broken-release shim: same pinned package, launched through python -c,
    # with an exact-pinned fakeredis for the in-process session store.
    assert server["args"][:6] == [
        "--with",
        "fakeredis==2.36.2",
        "--from",
        "courtlistener-api-client[mcp]==1.0.0",
        "python",
        "-c",
    ]
    # Exact equality: the constant is the ONLY thing in the -c slot, so any
    # future interpolation into the payload fails here.
    assert server["args"][6] == _COURTLISTENER_MCP_SHIM
    assert server["env"] == {"COURTLISTENER_API_TOKEN": "tok-agent"}


def test_courtlistener_shim_works_around_both_release_bugs() -> None:
    # courtlistener-api-client 1.0.0 ships no mcp/assets directory (the entry
    # point crashes at startup) and its search/call_endpoint tools require a
    # Redis session store that stdio mode never configures (every retrieval
    # call fails with "REDIS_URL is not set"). The shim must create the icon
    # files and pre-seed the module-level redis client with fakeredis before
    # handing over to the same main().
    shim = _COURTLISTENER_MCP_SHIM
    assert "favicon.svg" in shim
    assert "apple-touch-icon.png" in shim
    # The fakeredis pre-seed must land on the module global get_redis() reads,
    # and must come before the server starts.
    assert "utils.redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)" in shim
    assert shim.index("redis_client") < shim.index("from courtlistener.mcp.server import main")
    assert shim.rstrip().endswith("main()")
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
    # The multi-line shim must round-trip byte-exact through the JSON-escaped
    # TOML string (quotes, \x/\r\n byte escapes and all).
    assert table["args"][-1] == _COURTLISTENER_MCP_SHIM
    assert table["env"] == {"COURTLISTENER_API_TOKEN": "tok-agent"}


def test_gemini_settings_merge_preserves_telemetry(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("COURTLISTENER_API_TOKEN", raising=False)
    base: dict[str, object] = {"telemetry": {"enabled": True, "outfile": ".gemini/telemetry.log"}}
    doc = json.loads(gemini_mcp_settings([_SERVER], base))
    assert doc["telemetry"]["enabled"] is True  # the usage capture's block survives
    assert doc["mcpServers"]["courtlistener"]["command"] == "uvx"


def test_manifest_labels_are_pinned_attribution_strings() -> None:
    assert manifest_labels([_SERVER]) == ["courtlistener=courtlistener-api-client[mcp]==1.0.0"]


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
    assert args[:4] == ["--with", "fakeredis==2.36.2", "--from", _SERVER.package]
    shim = args[-1]
    compile(shim, "<mcp-http-shim>", "exec")  # the inline program must parse
    # The release-specific HTTP bypass: build the server directly (skipping
    # create_http_app's hard REDIS_URL/OAuth requirements), preseed fakeredis,
    # serve streamable HTTP on the loopback port.
    assert "create_mcp_server(auth=None)" in shim
    assert "transport='http'" in shim and "port=8378" in shim
    assert shim.index("fakeredis") < shim.index("create_mcp_server")
    assert env["COURTLISTENER_API_TOKEN"] == "tok-agent"
    # The HMAC namespace key is set explicitly (a non-secret constant) to
    # quiet the release's insecure-default warning in the replayed cell log.
    assert env["MCP_SECRET_KEY"] == "cell-local-fakeredis-namespace"


def test_http_sidecar_launch_refuses_other_releases() -> None:
    other = McpServerConfig(
        id="courtlistener",
        package="courtlistener-api-client[mcp]==1.1.0",
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
