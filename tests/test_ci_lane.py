"""The CI lane classifier (`scripts/ci_lane.py`) fails closed.

`gate` is a required check and a skipped step reports success, so a change
wrongly called ``data`` or ``docs`` would merge with its Python stages never
run. Every doubt therefore has to land on ``code``; these tests pin both the
allow-lists and the doubts — mixed diffs, unknown paths, and diffs the script
cannot trust — against real git repositories where git is the input.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

from tests import lane_guard

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ci_lane.py"
CI = ROOT / ".github" / "workflows" / "ci.yml"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ci_lane", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ci_lane = _load()


# --- classify ---------------------------------------------------------------


@pytest.mark.parametrize(
    "paths",
    [
        ["data/cases/scotus/123/events/evt-cert-x/predictions/p/r/prediction.json"],
        ["corpus/corpus.db.ref"],
        ["corpus/corpus.db.ref", "data/scope/latch.json"],
        ["data/cases/scotus/1/events/e/predictions/p/r/reasoning.md"],
    ],
)
def test_data_only_diffs_take_the_data_lane(paths: list[str]) -> None:
    assert ci_lane.classify(paths)[0] == "data"


@pytest.mark.parametrize(
    "paths",
    [
        ["docs/freeze-record.md"],
        ["README.md", "CONTRIBUTING.md"],
        ["docs/img/diagram.PNG"],
        ["CITATION.cff"],
        ["metrics/README.md", "corpus/README.md", "docs/pipeline.md"],
        ["docs/img/diagram.svg"],
    ],
)
def test_prose_only_diffs_take_the_docs_lane(paths: list[str]) -> None:
    assert ci_lane.classify(paths)[0] == "docs"


@pytest.mark.parametrize(
    "paths",
    [
        # The case the issue names: one data file beside one source file.
        ["data/cases/scotus/1/x.json", "src/fedcourtsai/cli.py"],
        ["docs/pipeline.md", "src/fedcourtsai/cli.py"],
        # Data and prose together is not either lane.
        ["data/cases/scotus/1/x.json", "docs/pipeline.md"],
        # Markdown that code reads, or that configures an agent, is not prose.
        [".github/prompts/predict.md"],
        [".claude/agents/code-reviewer.md"],
        ["tests/fixtures/notes.md"],
        ["src/fedcourtsai/README.md"],
        # Top-level Markdown that agents read as instructions or policy, and
        # the names a gemini cell loads as context, are operative, not prose.
        ["AGENTS.md"],
        ["CLAUDE.md"],
        ["SECURITY.md"],
        ["GEMINI.md"],
        ["MEMORY.md"],
        ["README.md", "AGENTS.md"],
        # Under docs/, only Markdown and images are prose; tooling is code.
        ["docs/build.py"],
        ["docs/conf.toml"],
        ["docs/Makefile"],
        # Everything the gate's Python stages exist for.
        [".github/workflows/ci.yml"],
        ["scripts/ci_lane.py"],
        ["schemas/prediction.schema.json"],
        ["config/predictors.yaml"],
        ["pyproject.toml"],
        ["uv.lock"],
        # Generated artifacts beside the prose are not prose.
        ["metrics/leaderboard.json"],
        ["corpus/other.ref"],
        # A near-miss prefix is not the directory.
        ["database/x.json"],
        ["docsite/index.md"],
        # Nothing to classify, and paths git would never print.
        [],
        ["", "  "],
        ["/etc/passwd"],
        ["docs/../src/fedcourtsai/cli.py"],
    ],
)
def test_everything_else_is_code(paths: list[str]) -> None:
    assert ci_lane.classify(paths)[0] == "code"


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
    _commit(tmp_path, {"src/a.py": "x = 1\n", "docs/a.md": "a\n"}, "base")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _merge_ref(repo: Path, files: dict[str, str]) -> None:
    """Build a PR merge ref: HEAD is a merge whose first parent is the base tip."""
    _git(repo, "switch", "-q", "-c", "feature")
    _commit(repo, files, "feature")
    _git(repo, "switch", "-q", "main")
    # The base advances after the branch point, as main does between writer
    # pushes; its own change must not be attributed to the PR.
    _commit(repo, {"src/base_drift.py": "y = 2\n"}, "base drift")
    _git(repo, "merge", "-q", "--no-ff", "-m", "merge", "feature")


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> str:
    assert ci_lane.main(list(argv)) == 0
    out: str = capsys.readouterr().out
    return out.strip()


def test_pull_request_diffs_the_merge_ref_against_its_first_parent(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _merge_ref(repo, {"data/cases/x.json": "{}\n"})
    assert ci_lane.changed_paths("pull_request", None) == ["data/cases/x.json"]
    assert _run(capsys, "--event", "pull_request") == "lane=data"


def test_pull_request_whose_head_is_not_a_merge_is_code(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _commit(repo, {"data/cases/x.json": "{}\n"}, "data only, but no merge ref")
    assert _run(capsys, "--event", "pull_request") == "lane=code"


def test_single_commit_push_diffs_before_to_after(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    before = _git(repo, "rev-parse", "HEAD")
    _commit(repo, {"docs/freeze-record.md": "entry\n"}, "docs")
    assert _run(capsys, "--event", "push", "--before", before) == "lane=docs"


def test_merge_push_diffs_against_the_prior_tip(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    before_merge = _git(repo, "rev-parse", "HEAD")
    _merge_ref(repo, {"corpus/corpus.db.ref": "sha\n"})
    # The drift commit sits between before_merge and the merge's first parent,
    # so the prior tip the push reports is the drift commit itself.
    prior = _git(repo, "rev-parse", "HEAD^1")
    assert prior != before_merge
    assert _run(capsys, "--event", "push", "--before", prior) == "lane=data"


@pytest.mark.parametrize("before", ["", "0" * 40, "deadbeef"])
def test_push_without_a_trustworthy_prior_tip_is_code(
    repo: Path, capsys: pytest.CaptureFixture[str], before: str
) -> None:
    _commit(repo, {"data/cases/x.json": "{}\n"}, "data")
    assert _run(capsys, "--event", "push", "--before", before) == "lane=code"


def test_multi_commit_push_is_code(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    before = _git(repo, "rev-parse", "HEAD")
    _commit(repo, {"data/cases/x.json": "{}\n"}, "one")
    _commit(repo, {"data/cases/y.json": "{}\n"}, "two")
    assert _run(capsys, "--event", "push", "--before", before) == "lane=code"


def test_a_symlink_under_data_is_code(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    before = _git(repo, "rev-parse", "HEAD")
    (repo / "data").mkdir()
    (repo / "data" / "link.json").symlink_to("../src/a.py")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "symlink")
    assert _run(capsys, "--event", "push", "--before", before) == "lane=code"


_BLOB = "0" * 7
_SHA = "a" * 7


@pytest.mark.parametrize(
    ("record", "ok"),
    [
        (f":100644 100644 {_SHA} {_SHA} M\0data/x.json\0", True),
        (f":000000 100644 {_BLOB} {_SHA} A\0data/x.json\0", True),
        (f":100644 000000 {_SHA} {_BLOB} D\0docs/x.md\0", True),
        (f":000000 120000 {_BLOB} {_SHA} A\0data/link\0", False),
        (f":120000 100644 {_SHA} {_SHA} T\0data/link\0", False),
        (f":000000 160000 {_BLOB} {_SHA} A\0docs/sub\0", False),
        ("garbage\0data/x.json\0", False),
        (f":100644 100644 {_SHA} {_SHA} M\0", False),
    ],
)
def test_parse_raw_refuses_opaque_or_unparseable_records(record: str, ok: bool) -> None:
    if ok:
        assert len(ci_lane.parse_raw(record)) == 1
    else:
        with pytest.raises(ValueError):
            ci_lane.parse_raw(record)


def test_a_rename_out_of_code_counts_both_sides(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    before = _git(repo, "rev-parse", "HEAD")
    _git(repo, "mv", "src/a.py", "docs/a.py.md")
    _git(repo, "commit", "-q", "-m", "move")
    assert _run(capsys, "--event", "push", "--before", before) == "lane=code"


def test_unknown_event_and_missing_git_are_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)  # not a repository: every git call fails
    assert _run(capsys, "--event", "pull_request") == "lane=code"
    assert _run(capsys, "--event", "workflow_dispatch") == "lane=code"


def test_the_script_runs_standalone_on_the_system_interpreter(repo: Path) -> None:
    _merge_ref(repo, {"README.md": "hi\n"})
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--event", "pull_request"],
        check=True,
        capture_output=True,
        text=True,
        cwd=repo,
    )
    assert out.stdout.strip() == "lane=docs"


# --- the gate job's wiring --------------------------------------------------


def _gate_steps() -> list[dict[str, object]]:
    workflow = yaml.safe_load(CI.read_text())
    steps: list[dict[str, object]] = workflow["jobs"]["gate"]["steps"]
    return steps


def _step(name: str) -> dict[str, object]:
    return next(s for s in _gate_steps() if s.get("name") == name)


def test_gate_has_no_needs_so_a_classifier_failure_cannot_skip_it() -> None:
    # A job whose `needs` fails is *skipped*, and a skipped required check
    # passes: the classifier must be a step inside `gate`, never a job before it.
    workflow = yaml.safe_load(CI.read_text())
    assert "needs" not in workflow["jobs"]["gate"]


def test_every_lane_gated_step_runs_unless_a_lane_was_affirmatively_named() -> None:
    # An empty or missing output must run the step, so every condition is a
    # `!=` against a named lane — never `== 'code'`, which an empty output
    # would fail and so skip the step.
    # (`lane tests` is the exception by design: it only *adds* work in a lane.)
    for name in ("lint", "types", "test", "coverage summary"):
        cond = str(_step(name)["if"])
        assert "steps.lane.outputs.lane" in cond, name
        assert "==" not in cond, (name, cond)
        assert "!=" in cond, (name, cond)
    skipping = {
        str(s["name"])
        for s in _gate_steps()
        if "steps.lane.outputs.lane !=" in str(s.get("if", ""))
    }
    assert skipping == {"lint", "types", "test", "coverage summary"}


def test_the_lane_is_computed_before_anything_it_gates() -> None:
    names = [s.get("name") for s in _gate_steps()]
    assert names.index("lane") < names.index("lint")
    lane = _step("lane")
    assert lane.get("id") == "lane"
    assert "scripts/ci_lane.py" in str(lane["run"])


def test_the_lane_step_runs_the_bases_classifier_not_the_changes() -> None:
    # A change must not grade itself: the step extracts HEAD^1's copy and runs
    # that, and never invokes the checked-out scripts/ci_lane.py directly.
    run = str(_step("lane")["run"])
    assert "git show HEAD^1:scripts/ci_lane.py" in run
    assert "python3 scripts/ci_lane.py" not in run
    assert "lane=code" in run  # the base-has-no-classifier fallback


def _run_lane_step(repo: Path, tmp_path: Path) -> str:
    """Execute the lane step's own shell in `repo` as a pull_request run."""
    runner_temp = tmp_path / "runner-temp"
    runner_temp.mkdir(exist_ok=True)
    output = tmp_path / "github-output"
    output.write_text("")
    env = {
        "PATH": os.environ["PATH"],
        "HOME": str(tmp_path),
        "RUNNER_TEMP": str(runner_temp),
        "GITHUB_OUTPUT": str(output),
        "EVENT_NAME": "pull_request",
        "BEFORE": "",
    }
    subprocess.run(
        ["bash", "-c", str(_step("lane")["run"])],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
    )
    return output.read_text().strip()


def test_a_change_to_the_classifier_is_graded_by_the_bases_copy(repo: Path, tmp_path: Path) -> None:
    _commit(repo, {"scripts/ci_lane.py": SCRIPT.read_text()}, "base carries the classifier")
    # The change rewrites the classifier to call everything data, beside a
    # data file. Its own copy would say `data`; the base's copy sees a script.
    rigged = "print('lane=data')\n"
    _merge_ref(repo, {"scripts/ci_lane.py": rigged, "data/cases/x.json": "{}\n"})
    assert _run_lane_step(repo, tmp_path) == "lane=code"


def test_the_lane_step_uses_the_bases_classifier_for_a_data_change(
    repo: Path, tmp_path: Path
) -> None:
    _commit(repo, {"scripts/ci_lane.py": SCRIPT.read_text()}, "base carries the classifier")
    _merge_ref(repo, {"data/cases/x.json": "{}\n"})
    assert _run_lane_step(repo, tmp_path) == "lane=data"


def test_a_base_without_the_classifier_runs_the_full_gate(repo: Path, tmp_path: Path) -> None:
    _merge_ref(repo, {"data/cases/x.json": "{}\n"})
    assert _run_lane_step(repo, tmp_path) == "lane=code"


def test_the_stages_that_cover_data_run_in_every_lane() -> None:
    for name in ("data", "schemas"):
        assert "if" not in _step(name), name


# --- the lane guard (tests/lane_guard.py) -------------------------------------


class _FakeItem:
    def __init__(self, nodeid: str, marks: set[str]) -> None:
        self.nodeid = nodeid
        self._marks = marks

    def get_closest_marker(self, name: str) -> object | None:
        return name if name in self._marks else None


def test_the_guard_maps_files_to_lanes_with_the_classifier() -> None:
    assert lane_guard.lane_of("docs/testing.md") == "docs"
    assert lane_guard.lane_of("README.md") == "docs"
    assert lane_guard.lane_of("AGENTS.md") is None
    assert lane_guard.lane_of("data/scope/x.json") == "data"
    assert lane_guard.lane_of("corpus/corpus.db.ref") == "data"
    assert lane_guard.lane_of("src/fedcourtsai/cli.py") is None
    assert lane_guard.lane_of(".github/prompts/predict.md") is None


@pytest.mark.reads_docs
@pytest.mark.reads_data
def test_the_guard_sees_a_read_of_a_lane_file() -> None:
    lane_guard._take()
    (ROOT / "docs" / "testing.md").read_text()
    (ROOT / "corpus" / "corpus.db.ref").read_bytes()
    (ROOT / "pyproject.toml").read_text()  # not a lane file
    seen = lane_guard._take()
    assert seen == {"docs": {"docs/testing.md"}, "data": {"corpus/corpus.db.ref"}}


def test_the_guard_ignores_reads_outside_the_repository(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "x.md").write_text("x")
    lane_guard._take()
    (tmp_path / "docs" / "x.md").read_text()
    assert lane_guard._take() == {}


def test_the_guard_fails_an_unmarked_reader_and_passes_a_marked_one() -> None:
    lane_guard._seen["docs"] = {"docs/testing.md"}
    with pytest.raises(pytest.fail.Exception, match="reads_docs"):
        lane_guard.pytest_runtest_teardown(_FakeItem("t::unmarked", set()))  # type: ignore[arg-type]
    lane_guard._seen["docs"] = {"docs/testing.md"}
    lane_guard.pytest_runtest_teardown(_FakeItem("t::marked", {"reads_docs"}))  # type: ignore[arg-type]
    # A mark for the other lane is not the mark this read needs.
    lane_guard._seen["data"] = {"data/x.json"}
    with pytest.raises(pytest.fail.Exception, match="reads_data"):
        lane_guard.pytest_runtest_teardown(_FakeItem("t::wrong", {"reads_docs"}))  # type: ignore[arg-type]


def test_the_guard_fails_collection_when_an_import_time_read_is_unmarked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reads = {"tests/test_x.py": {"docs": {"README.md"}}}
    monkeypatch.setattr(lane_guard, "_module_reads", reads)
    marked = _FakeItem("tests/test_x.py::a", {"reads_docs"})
    unmarked = _FakeItem("tests/test_x.py::b", set())
    elsewhere = _FakeItem("tests/test_y.py::c", set())
    lane_guard.pytest_collection_modifyitems([marked, elsewhere])  # type: ignore[list-item]
    with pytest.raises(pytest.UsageError, match=r"tests/test_x\.py"):
        lane_guard.pytest_collection_modifyitems([marked, unmarked])  # type: ignore[list-item]
