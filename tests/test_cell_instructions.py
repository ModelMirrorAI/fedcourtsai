"""A cell's instructions are exactly the bytes its process digest hashes.

The process digest (`fedcourtsai.process_version.compute_process_digest`)
hashes an actor's prompt template and its resolved config, so the stamp on a
cell records what it was told only while the template is the whole of what it
was told. Two routes would add instructions the digest never sees:

* a prompt template or a kickoff line that names another instruction file —
  the repository's development instructions (`AGENTS.md`, `CLAUDE.md`), any
  other agent context file an engine discovers by name, or another actor's
  template — for the cell to read;
* such a file left in the tree the agent works in, which Claude Code and Codex
  load on their own whether or not anything names it.

The first is pinned against every enabled actor's template, the labeler's, and
every kickoff the cell workflows and the local runner hand an engine; the
second against every job that starts an engine in a checkout, which must take
each tracked instruction file out of the tree, skip-worktree first, before its
first engine step. The name set is the path jail's own
(`fedcourtsai.collect.AGENT_CONTEXT_FILENAMES`), so an engine added to the
registry brings its discovery names to both checks at once.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from fedcourtsai.collect import AGENT_CONTEXT_FILENAMES
from fedcourtsai.pipeline.runner import RunRequest, _claude_instruction
from fedcourtsai.registry import load_evaluators, load_predictors
from fedcourtsai.schemas import UsageRole

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
LABELER_PROMPT = ".github/prompts/qp-topic-label.md"

#: Every workflow that starts an engine inside a repository checkout.
AGENT_WORKFLOWS = (
    "run-predict.yml",
    "run-evaluate.yml",
    "run-backtest.yml",
    "run-analytics.yml",
    "integration-test.yml",
)

#: The tracked development instructions every agent job removes.
DEVELOPMENT_INSTRUCTIONS = ("AGENTS.md", "CLAUDE.md")

_PROMPT_PATH = re.compile(r"\.github/prompts/[\w./-]+\.md")

#: The back-test commands that run engine cells through the local runner.
_BACKTEST_CELLS = re.compile(r"uv run fedcourts (cert|merits)-backtest(?![\w-])")


def _names_instruction_file(text: str) -> list[str]:
    """The agent context file names ``text`` mentions, case-insensitively."""
    found = []
    for name in sorted(AGENT_CONTEXT_FILENAMES):
        pattern = r"(?<![\w.-])" + re.escape(name) + r"(?![\w-])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            found.append(name)
    return found


def _actor_prompts() -> list[str]:
    config = REPO_ROOT / "config"
    prompts = {p.prompt for p in load_predictors(config / "predictors.yaml")}
    prompts |= {e.prompt for e in load_evaluators(config / "evaluators.yaml")}
    return sorted(prompts | {LABELER_PROMPT})


def _load(name: str) -> dict[Any, Any]:
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    assert isinstance(data, dict)
    return data


def _is_engine_step(step: dict[str, Any]) -> bool:
    uses = str(step.get("uses") or "")
    run = str(step.get("run") or "")
    return (
        uses.startswith("anthropics/claude-code-action@")
        or uses.startswith("openai/codex-action@")
        or "gemini-cell.sh" in run
        or _BACKTEST_CELLS.search(run) is not None
    )


def _kickoffs() -> list[tuple[str, str]]:
    """Every kickoff a cell workflow hands an engine step, by workflow and step."""
    found = []
    for name in AGENT_WORKFLOWS:
        for job in _load(name)["jobs"].values():
            for step in job.get("steps", []) or []:
                if not _is_engine_step(step):
                    continue
                for text in (
                    (step.get("with") or {}).get("prompt"),
                    (step.get("env") or {}).get("PROMPT"),
                ):
                    if isinstance(text, str):
                        found.append((f"{name}: {step.get('name') or step.get('id')}", text))
    return found


@pytest.mark.parametrize("prompt", _actor_prompts())
def test_no_cell_prompt_names_an_instruction_file_outside_its_digest(prompt: str) -> None:
    text = (REPO_ROOT / prompt).read_text(encoding="utf-8")
    assert _names_instruction_file(text) == [], (
        f"{prompt} names an agent instruction file no process digest hashes"
    )
    others = sorted(set(_PROMPT_PATH.findall(text)) - {prompt})
    assert others == [], f"{prompt} names another actor's prompt template: {others}"


def test_the_workflow_kickoffs_name_only_the_actors_own_template() -> None:
    kickoffs = _kickoffs()
    cells = 0
    for where, text in kickoffs:
        assert _names_instruction_file(text) == [], (
            f"{where}: the kickoff names an agent instruction file no process digest hashes"
        )
        first = text.strip().splitlines()[0]
        if not first.startswith("Read "):
            # An engine smoke's one-line probe, which names no file at all.
            assert _PROMPT_PATH.findall(text) == [], f"{where}: {first!r}"
            continue
        cells += 1
        named = _PROMPT_PATH.findall(text)
        # A matrix kickoff names the template the plan resolved from the
        # actor's registry entry, which is the template its digest hashes; the
        # one literal is the labeler's own.
        assert named in ([], [LABELER_PROMPT]), f"{where}: {named}"
        if not named:
            assert re.match(r"Read \$\{\{ (matrix|steps\.repro\.outputs)\.prompt \}\},", first), (
                f"{where}: {first!r}"
            )
    # Three predict and three evaluate engine steps, the evaluate repro, the
    # labeler and its smoke: a scan that found fewer would be reading a
    # different set of workflows than this test names.
    assert cells >= 9, kickoffs


@pytest.mark.parametrize("role", [UsageRole.predictor, UsageRole.evaluator])
def test_the_local_runner_kickoff_names_only_the_actors_own_template(
    tmp_path: Path, role: UsageRole
) -> None:
    prompt = (
        ".github/prompts/predict.md"
        if role == UsageRole.predictor
        else ".github/prompts/evaluate.md"
    )
    request = RunRequest(
        role=role,
        court_id="scotus",
        docket_id=1,
        event_id="evt-petition-disposition",
        actor_id="claude-baseline" if role == UsageRole.predictor else "claude-judge",
        run_id="20261030T000000Z",
        prompt=Path(prompt),
        data_root=tmp_path / "data",
    )
    text = _claude_instruction(request, "claude-opus-5-5")
    assert _names_instruction_file(text) == []
    assert _PROMPT_PATH.findall(text) == [prompt]


def _tracked_instruction_files() -> list[str]:
    skip = {".git", ".venv", "node_modules"}
    found = []
    for path in REPO_ROOT.rglob("*"):
        rel = path.relative_to(REPO_ROOT)
        if skip & set(rel.parts) or rel.parts[:2] == (".claude", "worktrees"):
            continue
        if path.is_file() and path.name.lower() in AGENT_CONTEXT_FILENAMES:
            found.append(rel.as_posix())
    return sorted(found)


# Walks the whole checkout, data/ and docs/ included, so it carries both lane
# marks; a change that adds such a file is `code` and runs the full suite.
@pytest.mark.reads_data
@pytest.mark.reads_docs
def test_the_only_instruction_files_in_the_checkout_are_the_ones_cells_remove() -> None:
    assert _tracked_instruction_files() == sorted(DEVELOPMENT_INSTRUCTIONS)


@pytest.mark.parametrize("name", AGENT_WORKFLOWS)
def test_every_agent_job_removes_the_development_instructions_first(name: str) -> None:
    jobs = 0
    for job_id, job in _load(name)["jobs"].items():
        steps = job.get("steps", []) or []
        engines = [i for i, step in enumerate(steps) if _is_engine_step(step)]
        if not engines:
            continue
        jobs += 1
        fences = [
            i
            for i, step in enumerate(steps)
            if all(f in str(step.get("run") or "") for f in DEVELOPMENT_INSTRUCTIONS)
            and "rm -f" in str(step.get("run") or "")
        ]
        assert fences, f"{name}:{job_id} starts an engine with AGENTS.md and CLAUDE.md in its tree"
        fence = fences[0]
        assert fence < engines[0], f"{name}:{job_id}: the removal runs after the first engine step"
        step = steps[fence]
        # Unconditional: a condition that evaluates false re-admits the files
        # with every check still green.
        assert "if" not in step, f"{name}:{job_id}: the removal must not carry an `if:`"
        run = str(step["run"])
        mark = run.index("--skip-worktree")
        assert mark < run.index("rm -f"), f"{name}:{job_id}: skip-worktree must precede the removal"
        for file in DEVELOPMENT_INSTRUCTIONS:
            assert run.index(file) < mark, f"{name}:{job_id}: {file} is not marked skip-worktree"
    assert jobs, f"{name}: no job starts an engine — the scan would pass vacuously"
