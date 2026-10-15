"""The engine CLIs every cell runs are pinned once each, and every workflow reads that pin.

`.github/engines/<engine>/` is the one place an engine version lives — an exact
version in package.json and the lockfile beside it: the `engine-cli` composite
installs from it, the claude cells hand claude-code-action the binary it
installs, codex-action takes its `codex-version` from it, and Dependabot bumps
it one engine per PR. These tests hold that shape, so a literal version
re-appearing in a workflow — the drift that left the smokes on one Claude CLI
while the cells ran another — fails here, not in production.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parent.parent
GITHUB = REPO / ".github"
ENGINES = GITHUB / "engines"
ENGINE_PACKAGES = {
    "claude-code": "@anthropic-ai/claude-code",
    "codex": "@openai/codex",
    "gemini": "@google/gemini-cli",
}
ENGINE_CLI = "./.github/actions/engine-cli"


def _yaml_files() -> list[Path]:
    return sorted(
        [*(GITHUB / "workflows").glob("*.y*ml"), *(GITHUB / "actions").glob("*/action.y*ml")]
    )


def _jobs(path: Path) -> list[dict[str, Any]]:
    return list((yaml.safe_load(path.read_text()).get("jobs") or {}).values())


def _terms(condition: object, separator: str) -> list[str]:
    text = str(condition).replace("${{", "").replace("}}", "")
    return [" ".join(term.split()) for term in text.split(separator) if term.strip()]


def _covers(installer_if: object, step_if: object) -> bool:
    """Whether a step that runs under `step_if` always finds the installer ran.

    The installer's condition is read as a disjunction of conjunctions; it
    covers the step when it is unconditional, or when one of its disjuncts is
    implied by the step's own conjunction (every term of that disjunct is a
    term of the step's condition).
    """
    if installer_if is None:
        return True
    if step_if is None:
        return False
    step_terms = set(_terms(step_if, "&&"))
    return any(set(_terms(disjunct, "&&")) <= step_terms for disjunct in _terms(installer_if, "||"))


def test_each_engine_is_pinned_to_an_exact_version_its_lockfile_agrees_with() -> None:
    assert sorted(path.name for path in ENGINES.iterdir()) == sorted(ENGINE_PACKAGES)
    for engine, package in ENGINE_PACKAGES.items():
        manifest = json.loads((ENGINES / engine / "package.json").read_text())
        assert manifest.get("private") is True
        assert "scripts" not in manifest, f"{engine}: the pin runs nothing of its own"
        assert manifest["dependencies"] == {package: manifest["dependencies"][package]}
        version = manifest["dependencies"][package]
        assert re.fullmatch(r"\d+\.\d+\.\d+", version), f"{engine} is not exactly pinned"
        lock = json.loads((ENGINES / engine / "package-lock.json").read_text())
        assert lock["packages"][f"node_modules/{package}"]["version"] == version, (
            f"{engine}: the lockfile resolves a different version than the pin"
        )


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
    assert not offenders, f"engine versions belong in .github/engines/<engine>/: {offenders}"


def test_every_codex_action_runs_the_pinned_codex() -> None:
    """codex-action installs whatever `codex-version` names, and the latest on an empty one.

    So each codex-action step must read the version from an engine-cli step
    that runs earlier in the same job under a condition covering the codex
    step's own — a skipped installer leaves the output empty and the action
    silently installs the newest codex.
    """
    uses = 0
    for path in _yaml_files():
        for job in _jobs(path):
            steps = job.get("steps") or []
            installers = {s["id"]: s for s in steps if s.get("uses") == ENGINE_CLI and "id" in s}
            for step in steps:
                if not str(step.get("uses", "")).startswith("openai/codex-action@"):
                    continue
                uses += 1
                where = f"{path.name}: {step.get('name')}"
                match = re.fullmatch(
                    r"\$\{\{ steps\.([\w-]+)\.outputs\.version \}\}",
                    str(step["with"].get("codex-version", "")),
                )
                assert match, f"{where} does not take codex-version from an engine-cli step"
                installer = installers.get(match.group(1))
                assert installer is not None, f"{where} names no engine-cli step"
                assert steps.index(installer) < steps.index(step), f"{where} resolves too late"
                assert _covers(installer.get("if"), step.get("if")), (
                    f"{where} can run when its engine-cli step was skipped"
                )
    assert uses, "no codex-action step found; the check would pass vacuously"


def test_the_codex_repro_leg_resolves_its_codex_version() -> None:
    job = yaml.safe_load((GITHUB / "workflows" / "integration-test.yml").read_text())["jobs"][
        "scenario"
    ]
    installer = next(s for s in job["steps"] if s.get("id") == "engine-cli")
    assert "matrix.scenario == 'codex-application-repro'" in _terms(installer["if"], "||")


def test_every_claude_action_runs_the_pinned_cli() -> None:
    uses = 0
    for path in _yaml_files():
        for job in _jobs(path):
            steps = job.get("steps") or []
            installers = {s["id"]: s for s in steps if s.get("uses") == ENGINE_CLI and "id" in s}
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
                assert _covers(installer.get("if"), step.get("if")), (
                    f"{where} can run when its engine-cli step was skipped"
                )
    assert uses, "no claude-code-action step found; the check would pass vacuously"


def test_the_engine_cli_action_installs_from_the_lockfile_outside_the_checkout() -> None:
    path = GITHUB / "actions" / "engine-cli" / "action.yml"
    text = path.read_text()
    assert "secrets." not in text
    install = next(s for s in yaml.safe_load(text)["runs"]["steps"] if s.get("id") == "install")
    assert "npm ci" in install["run"]
    assert "--ignore-scripts" in install["run"]
    assert "npm install" not in install["run"], "an install that ignores the lockfile"
    assert '"$RUNNER_TEMP/engines/' in install["run"], "the install must not dirty the checkout"


def test_every_engine_cli_caller_holds_no_secret() -> None:
    """Claude Code's own installer runs in the composite, so its caller's env must be clean.

    A step's environment is its own `env:` over the job's over the workflow's,
    and a composite sees all three; `with:` inputs reach it too.
    """
    callers = 0
    for path in sorted((GITHUB / "workflows").glob("*.y*ml")):
        document = yaml.safe_load(path.read_text())
        workflow_env = str(document.get("env") or {})
        for name, job in (document.get("jobs") or {}).items():
            for step in job.get("steps") or []:
                if step.get("uses") != ENGINE_CLI:
                    continue
                callers += 1
                where = f"{path.name}: {name}: {step.get('name')}"
                assert "env" not in step, f"{where} hands the installer an environment"
                assert "secrets." not in str(step.get("with") or {}), where
                assert "secrets." not in str(job.get("env") or {}), f"{where} (job env)"
                assert "secrets." not in workflow_env, f"{where} (workflow env)"
    assert callers, "no engine-cli caller found; the check would pass vacuously"


def test_dependabot_proposes_each_engine_bump_on_its_own_after_a_cooldown() -> None:
    config = yaml.safe_load((GITHUB / "dependabot.yml").read_text())
    entries = [entry for entry in config["updates"] if entry["package-ecosystem"] == "npm"]
    assert len(entries) == 1
    entry = entries[0]
    assert sorted(entry["directories"]) == sorted(
        f"/.github/engines/{engine}" for engine in ENGINE_PACKAGES
    )
    assert entry["schedule"]["interval"] == "daily"
    assert entry["cooldown"]["default-days"] == 3
    assert entry["target-branch"] == "staging"
    assert "groups" not in entry, "one engine per PR keeps each engine change legible"
