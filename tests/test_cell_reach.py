"""The cell-reach classifier (`scripts/cell_reach.py`) fails closed.

An ``inert`` verdict lets a promotion merge on the token-free ``offline-gate``
suite, with no evidence that a real engine still runs at the head. So every
doubt has to land on ``engine``: these tests pin the allow-list, the doubts —
mixed batches, unknown paths, agent instruction files, diffs the script cannot
trust — and the structural claim the ``src/`` allow-list rests on, that no
cell path imports a module it names.
"""

from __future__ import annotations

import ast
import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

from fedcourtsai import collect

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "cell_reach.py"
SOURCE = ROOT / "src" / "fedcourtsai"


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cell_reach = _load("cell_reach", SCRIPT)
ci_lane = _load("_ci_lane_for_cell_reach", ROOT / "scripts" / "ci_lane.py")


# --- classify ---------------------------------------------------------------


@pytest.mark.parametrize(
    "paths",
    [
        ["docs/freeze-record.md"],
        ["docs/pipeline.md", "README.md", "CITATION.cff", "metrics/README.md"],
        ["data/cases/scotus/1/events/e/outcome.json", "data/scope/latch.json"],
        ["metrics/leaderboard.json"],
        ["tests/test_promotion_train.py", "tests/fixtures/corpus/case.json"],
        ["src/fedcourtsai/promotion_train.py", "tests/test_promotion_train.py"],
        ["src/fedcourtsai/metrics_refresh.py", "src/fedcourtsai/public_update.py"],
        ["scripts/promotion-gate.sh", "scripts/ci_lane.py", "scripts/gate.sh"],
        ["scripts/checks/count_something.py"],
        ["config/promotion-train.yaml", "config/corpus-check.yaml"],
        ["src/fedcourtsai/dispatch_chain.py", "docs/budget.md"],
    ],
)
def test_batches_no_cell_runs_are_inert(paths: list[str]) -> None:
    assert cell_reach.classify(paths)[0] == "inert"


@pytest.mark.parametrize(
    "paths",
    [
        # A mixed batch: one prose file and one path that reaches a cell.
        ["docs/pipeline.md", "src/fedcourtsai/provision.py"],
        ["docs/pipeline.md", ".github/prompts/predict.md"],
        ["tests/test_x.py", "config/predictors.yaml"],
        ["config/evaluators.yaml"],
        ["src/fedcourtsai/pricing.py"],
        ["uv.lock"],
        ["pyproject.toml"],
        ["schemas/prediction.schema.json"],
        # cli.py imports everything and hosts the cell commands.
        ["src/fedcourtsai/cli.py"],
        # A module new to the tree is engine until someone lists it.
        ["src/fedcourtsai/brand_new_module.py"],
        # An inert stem is inert only at the package's top level.
        ["src/fedcourtsai/pipeline/promotion_train.py"],
        ["src/fedcourtsai/promotion_train.pyi"],
        # Any workflow, composite or pinned engine CLI.
        [".github/workflows/ci.yml"],
        [".github/actions/engine-cli/action.yml"],
        [".github/engines/codex/package.json"],
        ["scripts/gemini-cell.sh"],
        ["scripts/engine-watchdog.sh"],
        ["config/dispatchers.json"],
        # The round planners decide with these which cells exist.
        ["src/fedcourtsai/spend.py"],
        ["src/fedcourtsai/planning_rates.py"],
        ["config/review-hold.yaml"],
        # The engine legs read the corpus the pointer names.
        ["corpus/corpus.db.ref"],
        # Agent instruction files, which an engine in a cell may load, even
        # where the docs lane would otherwise call them prose.
        ["AGENTS.md"],
        ["CLAUDE.md"],
        ["docs/agents.md"],
        ["data/cases/scotus/1/CLAUDE.md"],
        ["tests/.claude/settings.json"],
        ["SECURITY.md"],
        # Not prose under docs/.
        ["docs/tool.py"],
    ],
)
def test_batches_that_can_reach_a_cell_are_engine(paths: list[str]) -> None:
    assert cell_reach.classify(paths)[0] == "engine"


@pytest.mark.parametrize(
    "paths",
    [
        [],
        [""],
        ["/etc/passwd"],
        ["docs/../src/fedcourtsai/cli.py"],
        [" docs/pipeline.md"],
        ["docs/pipeline.md\n"],
    ],
)
def test_every_doubt_is_engine(paths: list[str]) -> None:
    assert cell_reach.classify(paths)[0] == "engine"


def test_the_reason_names_what_reaches_a_cell() -> None:
    verdict, reason = cell_reach.classify(["docs/a.md", "src/fedcourtsai/provision.py", "uv.lock"])
    assert verdict == "engine"
    assert "'src/fedcourtsai/provision.py'" in reason
    assert "1 more" in reason


def test_a_name_cannot_start_a_line_in_the_reason() -> None:
    # The reason is printed to a workflow log; a raw newline in a path would
    # let the batch start a line the runner reads as a workflow command.
    for paths in (["src/a\n::set-output name=skip::1"], [".github/x\n::add-mask::y"]):
        verdict, reason = cell_reach.classify(paths)
        assert verdict == "engine"
        assert "\n" not in reason


def test_the_agent_name_sets_are_the_path_jails() -> None:
    assert cell_reach.AGENT_CONTEXT_FILENAMES == collect.AGENT_CONTEXT_FILENAMES
    assert cell_reach.AGENT_CONFIG_DIRS == collect.AGENT_CONFIG_DIRS


@pytest.mark.parametrize(
    "path",
    [
        "docs/pipeline.md",
        "docs/img/flow.svg",
        "README.md",
        "SECURITY.md",
        "CITATION.cff",
        "corpus/README.md",
        "metrics/README.md",
        "docs/tool.py",
        ".github/prompts/README.md",
        "src/README.md",
    ],
)
def test_prose_is_the_ci_docs_lanes(path: str) -> None:
    # The prose half of the allow-list is the docs lane's, copied because both
    # scripts run with no environment.
    assert cell_reach._is_docs(path) == ci_lane._is_docs(path)


def test_every_listed_module_and_file_exists() -> None:
    # A listing that names nothing is a typo or a stale rename: harmless to the
    # verdict (it lists less), but it reads as coverage it does not give.
    for stem in cell_reach.INERT_SOURCE:
        assert (SOURCE / f"{stem}.py").is_file(), stem
    for rel in cell_reach.INERT_FILES:
        assert (ROOT / rel).exists(), rel


def _imported_modules(path: Path, src: Path) -> set[str]:
    """The top-level ``fedcourtsai`` modules ``path`` (under ``src``) imports, anywhere in it."""
    package = path.parent.relative_to(src).parts
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] == "fedcourtsai" and len(parts) > 1:
                    found.add(parts[1])
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                anchor = package[: len(package) - node.level + 1]
                parts = [*anchor, *(node.module or "").split(".")]
            else:
                parts = (node.module or "").split(".")
            parts = [p for p in parts if p]
            if not parts or parts[0] != "fedcourtsai":
                continue
            if len(parts) > 1:
                found.add(parts[1])
            else:
                found.update(alias.name for alias in node.names)
    return found


def test_no_cell_path_imports_an_inert_module() -> None:
    # The src/ allow-list's premise: a listed module is reached only through
    # cli.py, which is itself engine-relevant, and the other listed modules.
    # A module that is not listed — anything a cell may run — importing one
    # would make a change to it reach a cell while the verdict calls it inert.
    offenders = []
    for path in sorted(SOURCE.rglob("*.py")):
        rel = path.relative_to(SOURCE)
        if len(rel.parts) == 1 and (rel.stem in cell_reach.INERT_SOURCE or rel.stem == "cli"):
            continue
        hit = _imported_modules(path, ROOT / "src") & cell_reach.INERT_SOURCE
        if hit:
            offenders.append(f"{rel}: {sorted(hit)}")
    assert offenders == []


def test_the_import_reader_sees_every_spelling(tmp_path: Path) -> None:
    pkg = tmp_path / "src" / "fedcourtsai" / "sub"
    pkg.mkdir(parents=True)
    module = pkg / "m.py"
    module.write_text(
        "from .. import spend\n"
        + "from ..ops import x\n"
        + "import fedcourtsai.registry_gate\n"
        + "from fedcourtsai.public_update import y\n"
        + "def f():\n    from fedcourtsai import buttondown\n"
    )
    found = _imported_modules(module, tmp_path / "src")
    assert {"spend", "ops", "registry_gate", "public_update", "buttondown"} <= found


def test_no_script_or_workflow_names_an_inert_module() -> None:
    # A step or script a cell runs could import a listed module directly,
    # around cli.py; none may name one. The gate and lane scripts on the
    # allow-list, and the corpus-check lane's, are themselves inert.
    names = {f"fedcourtsai.{stem}" for stem in cell_reach.INERT_SOURCE}
    surfaces = [
        *(ROOT / "scripts").glob("*"),
        *(ROOT / ".github" / "workflows").glob("*.yml"),
        *(ROOT / ".github" / "actions").glob("*/action.yml"),
    ]
    offenders = []
    for path in sorted(p for p in surfaces if p.is_file()):
        rel = path.relative_to(ROOT).as_posix()
        if rel in cell_reach.INERT_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        offenders += [f"{rel}: {name}" for name in sorted(names) if name in text]
    assert offenders == []


# --- changed_paths / main against real git ------------------------------------


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _commit(repo: Path, files: dict[str, str], message: str) -> str:
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "ci@example.invalid")
    _git(tmp_path, "config", "user.name", "ci")
    _git(tmp_path, "config", "commit.gpgsign", "false")
    _commit(tmp_path, {"src/fedcourtsai/cli.py": "x = 1\n", "docs/a.md": "a\n"}, "base")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _candidate(repo: Path, files: dict[str, str]) -> str:
    """Cut a branch, commit ``files`` on it, and move main on independently."""
    _git(repo, "switch", "-q", "-c", "staging")
    head = _commit(repo, files, "batch")
    _git(repo, "switch", "-q", "main")
    # main moves after the branch point, as the writer lanes move it; its own
    # change must never be read as the batch's.
    _commit(repo, {"src/fedcourtsai/pricing.py": "DEFAULT_MODELS = {}\n"}, "main drift")
    return head


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> str:
    assert cell_reach.main(list(argv)) == 0
    out: str = capsys.readouterr().out
    return out.strip()


def test_the_batch_is_the_three_dot_diff(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    head = _candidate(repo, {"docs/freeze-record.md": "entry\n"})
    assert cell_reach.changed_paths("main", head) == ["docs/freeze-record.md"]
    assert _run(capsys, "--base", "main", "--head", head) == "reach=inert"


def test_a_mixed_batch_in_git_is_engine(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    head = _candidate(
        repo, {"docs/freeze-record.md": "entry\n", ".github/prompts/predict.md": "p\n"}
    )
    assert _run(capsys, "--base", "main", "--head", head) == "reach=engine"


def test_a_batch_that_changes_nothing_is_engine(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _run(capsys, "--base", "main", "--head", "main") == "reach=engine"


@pytest.mark.parametrize("head", ["0" * 40, "no-such-branch", "--output=x", "main..main", "a b"])
def test_an_unreadable_or_odd_head_is_engine(
    repo: Path, capsys: pytest.CaptureFixture[str], head: str
) -> None:
    _candidate(repo, {"docs/a.md": "b\n"})
    assert _run(capsys, "--base", "main", f"--head={head}") == "reach=engine"
    assert not (repo / "x").exists()


def test_a_symlink_in_an_inert_tree_is_engine(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _git(repo, "switch", "-q", "-c", "staging")
    (repo / "tests").mkdir()
    (repo / "tests" / "link.py").symlink_to("../src/fedcourtsai/cli.py")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "symlink")
    assert _run(capsys, "--base", "main", "--head", "staging") == "reach=engine"


def test_the_reason_goes_to_stderr(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    head = _candidate(repo, {"src/fedcourtsai/provision.py": "p = 1\n"})
    assert cell_reach.main(["--base", "main", "--head", head]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "reach=engine"
    assert "'src/fedcourtsai/provision.py' can reach a cell" in captured.err


def test_the_script_runs_isolated_with_no_environment(repo: Path) -> None:
    # The workflows run it as `python3 -I <copy>`: standard library only.
    head = _candidate(repo, {"docs/a.md": "b\n"})
    result = subprocess.run(
        ["python3", "-I", "-S", str(SCRIPT), "--base", "main", "--head", head],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "reach=inert"
