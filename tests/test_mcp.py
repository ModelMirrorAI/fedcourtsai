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
    # The missing-assets shim: same pinned package, launched through python -c.
    assert server["args"][:4] == [
        "--from",
        "courtlistener-api-client[mcp]==1.0.0",
        "python",
        "-c",
    ]
    # Exact equality: the constant is the ONLY thing in the -c slot, so any
    # future interpolation into the payload fails here.
    assert server["args"][4] == _COURTLISTENER_MCP_SHIM
    assert server["env"] == {"COURTLISTENER_API_TOKEN": "tok-agent"}


def test_courtlistener_shim_writes_the_missing_assets_then_starts_main() -> None:
    # courtlistener-api-client 1.0.0 ships no mcp/assets directory, so the
    # upstream entry point crashes at startup; the shim must create the icon
    # files the server reads before handing over to the same main().
    shim = _COURTLISTENER_MCP_SHIM
    assert "favicon.svg" in shim
    assert "apple-touch-icon.png" in shim
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
