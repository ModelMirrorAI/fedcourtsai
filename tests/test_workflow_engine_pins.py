"""The engine CLIs every cell runs are pinned once, and every workflow reads that pin.

`.github/engines/package.json` is the one place an engine version lives: the
`engine-cli` composite resolves it, the claude cells hand claude-code-action the
binary it installs, codex-action takes its `codex-version` from it, and
Dependabot bumps it one package per PR. These tests hold that shape, so a
literal version re-appearing in a workflow — the drift that left the smokes on
one Claude CLI while the cells ran another — fails here, not in production.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parent.parent
GITHUB = REPO / ".github"
PINS = GITHUB / "engines" / "package.json"
ENGINE_PACKAGES = ("@anthropic-ai/claude-code", "@google/gemini-cli", "@openai/codex")
ENGINE_CLI = "./.github/actions/engine-cli"


def _yaml_files() -> list[Path]:
    return sorted(
        [*(GITHUB / "workflows").glob("*.y*ml"), *(GITHUB / "actions").glob("*/action.y*ml")]
    )


def _steps(document: dict[str, Any]) -> list[dict[str, Any]]:
    jobs = document.get("jobs") or {}
    steps = [step for job in jobs.values() for step in (job.get("steps") or [])]
    return steps + list((document.get("runs") or {}).get("steps") or [])


def test_the_three_engines_are_pinned_to_exact_versions() -> None:
    pins = json.loads(PINS.read_text())
    assert pins.get("private") is True
    assert "scripts" not in pins, "the pin file is never installed from; it runs nothing"
    dependencies = pins["dependencies"]
    assert sorted(dependencies) == sorted(ENGINE_PACKAGES)
    for package, version in dependencies.items():
        assert re.fullmatch(r"\d+\.\d+\.\d+", version), f"{package} is not exactly pinned"


def test_no_workflow_or_action_carries_a_literal_engine_version() -> None:
    literal = re.compile(
        r"(@anthropic-ai/claude-code|@openai/codex|@google/gemini-cli)@\d"
        r"|codex-version:\s*[\"']?\d"
    )
    offenders = [
        f"{path.relative_to(REPO)}:{number}"
        for path in _yaml_files()
        for number, line in enumerate(path.read_text().splitlines(), start=1)
        if literal.search(line)
    ]
    assert not offenders, f"engine versions belong in .github/engines/package.json: {offenders}"


def test_codex_action_takes_its_version_from_the_engine_cli_step() -> None:
    uses = 0
    for path in _yaml_files():
        for step in _steps(yaml.safe_load(path.read_text())):
            if str(step.get("uses", "")).startswith("openai/codex-action@"):
                uses += 1
                assert step["with"]["codex-version"] == "${{ steps.engine-cli.outputs.version }}", (
                    f"{path.name}: {step.get('name')}"
                )
    assert uses, "no codex-action step found; the check would pass vacuously"


def test_every_claude_action_runs_the_pinned_cli() -> None:
    uses = 0
    for path in _yaml_files():
        document = yaml.safe_load(path.read_text())
        for job in (document.get("jobs") or {}).values():
            steps = job.get("steps") or []
            installers = {
                step["id"]: step
                for step in steps
                if step.get("uses") == ENGINE_CLI and "id" in step
            }
            for step in steps:
                if not str(step.get("uses", "")).startswith("anthropics/claude-code-action@"):
                    continue
                uses += 1
                where = f"{path.name}: {step.get('name')}"
                executable = step["with"].get("path_to_claude_code_executable", "")
                match = re.fullmatch(r"\$\{\{ steps\.([\w-]+)\.outputs\.path \}\}", executable)
                assert match, f"{where} runs the CLI the action bundles, not the pin"
                installer = installers.get(match.group(1))
                assert installer is not None, f"{where} names no engine-cli step"
                assert steps.index(installer) < steps.index(step), f"{where} installs too late"
    assert uses, "no claude-code-action step found; the check would pass vacuously"


def test_the_engine_cli_action_reads_the_pin_file_and_runs_no_secret() -> None:
    action = yaml.safe_load((GITHUB / "actions" / "engine-cli" / "action.yml").read_text())
    text = (GITHUB / "actions" / "engine-cli" / "action.yml").read_text()
    assert "engines/package.json" in text
    assert "secrets." not in text
    install = next(step for step in action["runs"]["steps"] if step.get("id") == "install")
    assert "--ignore-scripts" in install["run"]


def test_dependabot_proposes_each_engine_bump_on_its_own() -> None:
    config = yaml.safe_load((GITHUB / "dependabot.yml").read_text())
    entries = [
        entry
        for entry in config["updates"]
        if entry["package-ecosystem"] == "npm" and entry["directory"] == "/.github/engines"
    ]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["schedule"]["interval"] == "daily"
    assert entry["target-branch"] == "staging"
    assert "groups" not in entry, "one engine per PR keeps each engine change legible"
