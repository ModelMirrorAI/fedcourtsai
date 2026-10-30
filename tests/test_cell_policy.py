"""The run-time install refusal reaches every cell engine in the form it enforces.

`fedcourtsai.cell_policy` is one prefix list; the cell workflows carry it three
ways (claude-code's settings deny list inline, codex's execpolicy rules and
gemini's policy file written from `fedcourts cell-policy`). Nothing at run time
compares those to the list, so a drifted copy would leave one engine free to
install while every gate stays green. These tests hold each to it.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

import pytest
import yaml
from typer.testing import CliRunner

from fedcourtsai import cell_policy
from fedcourtsai.cli import app

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
CELL_WORKFLOWS = ("run-predict.yml", "run-evaluate.yml", "integration-test.yml")

runner = CliRunner()


def _steps(name: str) -> list[dict[str, Any]]:
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    return [step for job in data["jobs"].values() for step in job.get("steps", []) or []]


def test_every_refused_prefix_is_rendered_for_every_engine() -> None:
    prefixes = [" ".join(p) for p in cell_policy.INSTALL_COMMAND_PREFIXES]
    assert len(set(prefixes)) == len(prefixes)
    assert cell_policy.claude_deny_rules() == [f"Bash({p} *)" for p in prefixes]
    gemini = tomllib.loads(cell_policy.gemini_policy_toml())
    (rule,) = gemini["rule"]
    assert rule["toolName"] == "run_shell_command"
    assert rule["decision"] == "deny"
    assert rule["commandPrefix"] == prefixes
    assert 0 <= rule["priority"] <= 999
    codex = cell_policy.codex_rules().splitlines()
    rules = [line for line in codex if line.startswith("prefix_rule(")]
    assert len(rules) == len(prefixes)
    for line, prefix in zip(rules, cell_policy.INSTALL_COMMAND_PREFIXES, strict=True):
        assert f"pattern={json.dumps(list(prefix))}" in line
        assert 'decision="forbidden"' in line


def test_no_refused_prefix_catches_the_cells_own_tooling() -> None:
    for allowed in (
        "uv run fedcourts query --help",
        "uv run fedcourts pdf-text record/documents/petition.pdf",
        "fedcourts validate data",
        "python3 -c 'print(1)'",
    ):
        tokens = allowed.split()
        for prefix in cell_policy.INSTALL_COMMAND_PREFIXES:
            assert tuple(tokens[: len(prefix)]) != prefix, (allowed, prefix)


@pytest.mark.parametrize("engine", ["claude-code", "codex", "gemini"])
def test_the_command_prints_the_rendering(engine: str) -> None:
    result = runner.invoke(app, ["cell-policy", "--engine", engine])
    assert result.exit_code == 0, result.output
    assert result.stdout == cell_policy.render(engine)


def test_the_command_refuses_an_unknown_engine() -> None:
    result = runner.invoke(app, ["cell-policy", "--engine", "cursor"])
    assert result.exit_code == 2


@pytest.mark.parametrize("name", CELL_WORKFLOWS)
def test_every_claude_cell_step_denies_the_prefix_list(name: str) -> None:
    steps = [
        s
        for s in _steps(name)
        if str(s.get("uses") or "").startswith("anthropics/claude-code-action@")
        and "--permission-mode bypassPermissions" in str((s.get("with") or {}).get("claude_args"))
    ]
    assert steps, f"{name}: no claude cell step"
    for step in steps:
        settings = json.loads(step["with"]["settings"])
        assert settings["permissions"]["deny"] == cell_policy.claude_deny_rules(), step.get("name")


@pytest.mark.parametrize("name", CELL_WORKFLOWS)
def test_every_codex_config_is_written_with_its_rules(name: str) -> None:
    runs = [str(s.get("run")) for s in _steps(name) if "> .codex/config.toml" in str(s.get("run"))]
    assert runs, f"{name}: no codex config is written"
    for run in runs:
        assert run.count("> .codex/config.toml") == run.count(
            "cell-policy --engine codex > .codex/rules/" + cell_policy.CODEX_RULES_FILENAME
        )


@pytest.mark.parametrize("name", CELL_WORKFLOWS)
def test_every_gemini_settings_file_names_the_policy(name: str) -> None:
    runs = [
        str(s.get("run"))
        for s in _steps(name)
        if "> .gemini/settings.json.new" in str(s.get("run"))
    ]
    if name == "integration-test.yml" and not runs:
        pytest.fail("the evaluate reproduction writes no gemini settings")
    assert runs, f"{name}: no gemini settings are written"
    policy = ".gemini/policies/" + cell_policy.GEMINI_POLICY_FILENAME
    for run in runs:
        written = run.index(f"cell-policy --engine gemini > {policy}")
        named = run.index(f"'.policyPaths = [$policy]'")
        assert f'"$GITHUB_WORKSPACE/{policy}"' in run
        assert written < named


def test_the_codex_account_reads_the_rules_from_a_root_owned_copy() -> None:
    action = (REPO_ROOT / ".github" / "actions" / "codex-user-setup" / "action.yml").read_text()
    assert 'sudo install -d -o root -g root -m 755 "$home/.codex/rules"' in action
    assert 'sudo install -o root -g root -m 644 "$rules" "$home/.codex/rules/"' in action
