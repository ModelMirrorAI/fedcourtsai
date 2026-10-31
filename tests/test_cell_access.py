"""The predict cell's lane audit over its logged tool calls (`fedcourtsai.cell_access`)."""

from __future__ import annotations

import json

import pytest

from fedcourtsai.cell_access import AccessHit, AccessKind, audit_cell_access
from fedcourtsai.schemas import RetrievalCall

ACTOR = "gemini-baseline"
RUN = "20261014T174020Z"
CASE_DIR = "data/cases/scotus/73500219"
EVENT = "evt-petition-disposition"
OWN = f"{CASE_DIR}/events/{EVENT}/predictions/{ACTOR}/{RUN}"


def _audit(*calls: tuple[str, str]) -> list[AccessHit]:
    return audit_cell_access(
        [RetrievalCall(tool=tool, query=query) for tool, query in calls],
        case_id="scotus/73500219",
        event_id=EVENT,
        actor_id=ACTOR,
        run_id=RUN,
    )


def _kinds(*calls: tuple[str, str]) -> list[AccessKind]:
    return [hit.kind for hit in _audit(*calls)]


def test_a_restore_of_the_oracle_is_caught() -> None:
    """The shape the audit exists for: an engine tidying the deletion back."""
    hits = _audit(("run_shell_command", "git restore data/qp-topics/qp-topic-reference.json"))
    assert hits == [
        AccessHit(
            kind=AccessKind.oracle,
            tool="run_shell_command",
            path="data/qp-topics/qp-topic-reference.json",
        )
    ]


@pytest.mark.parametrize(
    "command",
    [
        "find data -name AGENTS.md -not -path 'data/qp-topics/*'",
        "find data ! -path data/qp-topics/x -type f",
        "find data -path data/qp-topics -prune -o -print",
        "rg -n foo --glob '!data/qp-topics/**'",
        "rg -n foo -g !data/qp-topics/**",
        "grep -r foo data --exclude-dir=qp-topics",
        "git ls-files -- data ':(exclude)data/qp-topics'",
        "git ls-files -- data ':!data/qp-topics'",
    ],
)
def test_a_path_named_only_to_exclude_it_is_no_access(command: str) -> None:
    assert _audit(("Bash", command)) == []


def test_reads_of_this_cells_own_run_directory_are_its_lane() -> None:
    assert (
        _audit(("Bash", f"cat {OWN}/prediction.json"), ("Read", f'{{"file_path": "{OWN}"}}')) == []
    )


@pytest.mark.parametrize(
    "path",
    [
        f"{CASE_DIR}/events/evt-x/predictions/claude-baseline/{RUN}/prediction.json",
        f"{CASE_DIR}/events/evt-x/predictions/{ACTOR}/20260816T173750Z/prediction.json",
        f"data/cases/scotus/*/events/*/predictions/{ACTOR}/*/prediction.json",
        "data/cases/scotus/*/events/*/predictions/*/*/prediction.json",
        f"{CASE_DIR}/events/evt-x/evaluations/claude-judge/{RUN}/evaluation.json",
    ],
)
def test_another_cells_committed_output_is_a_cell_record_hit(path: str) -> None:
    assert _kinds(("Bash", f"ls {path} | head -1")) == [AccessKind.cell_record]


def test_a_slice_cut_inside_a_predictions_path_is_not_read_as_another_run() -> None:
    """The capture cut can end mid-segment; that prefix is not evidence."""
    target = OWN[: OWN.index(ACTOR) + 5]
    head, tail = '{"content": "', '", "file_path": "'
    cut = head + "x" * (500 - len(head) - len(tail) - len(target)) + tail + target
    assert _audit(("write_file", cut)) == []


@pytest.mark.parametrize(
    ("tool", "query"),
    [
        (
            "run_shell_command",
            f"grep -n split {CASE_DIR}/record/documents/petition.txt > "
            + f"{CASE_DIR}/record/documents/petition.txt.grep",
        ),
        ("run_shell_command", f"echo x | tee -a {CASE_DIR}/record/priors_granted.txt"),
        (
            "write_file",
            json.dumps(
                {"file_path": f"{CASE_DIR}/events/evt-petition-disposition/prediction.json"}
            ),
        ),
        ("apply_patch", f"*** Begin Patch\n*** Add File: {CASE_DIR}/record/notes.md\n+x"),
    ],
)
def test_a_write_outside_the_run_directory_is_a_write_hit(tool: str, query: str) -> None:
    assert AccessKind.write in _kinds((tool, query))


@pytest.mark.parametrize(
    ("tool", "query"),
    [
        ("Write", json.dumps({"file_path": f"{OWN}/prediction.json", "content": "{}"})),
        ("Bash", f"python3 build.py > {OWN}/reasoning.md 2>&1"),
        ("Bash", "uv run fedcourts validate data > /tmp/validate.log 2>&1"),
        ("Bash", "uv run fedcourts query --court scotus >/dev/null"),
    ],
)
def test_writes_inside_the_lane_or_off_the_tree_are_not_hits(tool: str, query: str) -> None:
    assert _audit((tool, query)) == []


@pytest.mark.parametrize(
    "tool",
    [
        "mcp__courtlistener__search",
        "WebSearch",
        "web_fetch",
        "Agent",
        "spawn_agent",
        "send_input",
        "send_message",
    ],
)
def test_calls_that_cannot_touch_the_tree_are_not_audited(tool: str) -> None:
    """A search query, a fetched page or a subagent's instructions may name the
    oracle; none of them reads the cell's tree."""
    assert _audit((tool, "do not read data/qp-topics or predictions/*/*")) == []


def test_one_hit_per_call_kind_and_path() -> None:
    query = "cat data/qp-topics/a.json; cat data/qp-topics/a.json"
    assert len(_audit(("Bash", query), ("Bash", query))) == 2


@pytest.mark.parametrize(
    "command",
    [
        "git show HEAD^:data/qp-topics/labels.json",
        "git show abc123^:data/qp-topics/labels.json",
        "grep -rn foo data | grep -v qp-topics",
    ],
)
def test_a_revision_or_an_output_filter_is_not_an_exclusion(command: str) -> None:
    """`^` in a revision is not pathspec magic, and filtering output a command
    already opened is a read, as the evaluate prompt grades it."""
    assert AccessKind.oracle in _kinds(("Bash", command))


@pytest.mark.parametrize(
    "command",
    [
        f"ls {CASE_DIR}/events/evt-x/predictions/*/",
        f"ls {CASE_DIR}/events/evt-x/predictions/codex-baseline",
        f"ls {CASE_DIR}/events/evt-x/evaluations",
        f"git log -p -- {CASE_DIR}/events/evt-x/predictions/",
    ],
)
def test_a_short_command_ending_in_a_cell_path_is_still_read(command: str) -> None:
    """Only a slice the capture cut is spared at its end; a history read of the
    bare directory reaches every predictor's output."""
    assert _kinds(("Bash", command)) == [AccessKind.cell_record]


def test_another_case_under_the_same_run_is_not_this_cells_own() -> None:
    """Every cell of a run shares its run id, so the case and event decide."""
    other = f"data/cases/scotus/1/events/{EVENT}/predictions/{ACTOR}/{RUN}/prediction.json"
    assert _kinds(("Write", json.dumps({"file_path": other}))) == [AccessKind.write]


@pytest.mark.parametrize(
    "command",
    [
        "echo x > 'data/cases/scotus/1/notes.json'",
        "echo x > /tmp/../data/cases/scotus/1/notes.json",
    ],
)
def test_a_quoted_or_dotted_write_target_is_still_seen(command: str) -> None:
    assert _kinds(("Bash", command)) == [AccessKind.write]


def test_a_codex_subagent_brief_forbidding_the_hidden_paths_is_not_a_hit() -> None:
    """The shape codex's read-only reviewers are briefed in: the prohibition names
    every hidden path, and the subagent's own calls are audited as calls."""
    brief = json.dumps(
        {
            "agent_type": "default",
            "message": "Read-only task. Do NOT read any predictions/evaluations/outcomes "
            + "or data/qp-topics.",
        }
    )
    assert _audit(("spawn_agent", brief)) == []
    assert _kinds(("exec_command", "cat data/qp-topics/a.json")) == [AccessKind.oracle]


def test_a_path_first_write_slice_is_caught_however_long_its_content() -> None:
    """Capture leads a file tool's slice with its target, so the cut takes content."""
    query = json.dumps({"file_path": f"{CASE_DIR}/events/{EVENT}/predictions/{ACTOR}/flags.json"})
    query = query[:-1] + ', "content": "' + "x" * 600
    assert AccessKind.write in _kinds(("write_file", query[:500]))
    # The same write in sorted key order, content first, leaves no target to see.
    sorted_order = json.dumps({"content": "x" * 600, "file_path": "data/x.json"})[:500]
    assert _kinds(("write_file", sorted_order)) == []
