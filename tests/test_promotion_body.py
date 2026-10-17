"""The generated block of a draft promotion PR's body."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from fedcourtsai.cli import app
from fedcourtsai.promotion_body import (
    BEGIN,
    END,
    Batch,
    BatchPR,
    GateCheck,
    batch_prs,
    extract_effect_check,
    render,
    same_body,
    splice,
)

FOOTER = "🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nhttps://claude.ai/code/session_x"


# --- extracting a handover note ----------------------------------------------


def test_each_heading_phrasing_feature_prs_use_is_found() -> None:
    for heading in (
        "## Effect check, after the next promotion",
        "## Handover: effect check for the promotion",
        "## Post-promotion effect check",
        "## Effect check (for the promotion body)",
        "## Promotion and effect check",
        "### Effect checks",
    ):
        body = f"## What changed\n\nStuff.\n\n{heading}\n\n- run `x`, see `y`\n"
        assert extract_effect_check(body) == "- run `x`, see `y`", heading


def test_the_section_ends_at_a_heading_of_the_same_or_higher_level() -> None:
    body = (
        "## Effect check for the promotion body\n\n- one\n\n### detail\n\n- two\n\n"
        + "## Not self-merged\n\nwaits.\n"
    )
    assert extract_effect_check(body) == "- one\n\n### detail\n\n- two"


def test_the_section_ends_at_the_tool_footer() -> None:
    body = f"## Effect check\n\n- run `x`\n\n{FOOTER}\n"
    assert extract_effect_check(body) == "- run `x`"


def test_no_heading_or_an_empty_section_is_no_check() -> None:
    assert extract_effect_check("## What changed\n\nNothing about checks.\n") is None
    assert extract_effect_check("## Effect check\n\n## Next\n\ntext\n") is None
    # A heading that merely mentions a check in passing is not a handover note.
    assert extract_effect_check("## Checks run\n\n- lint\n") is None


def test_a_fenced_shell_comment_neither_ends_nor_starts_a_section() -> None:
    body = (
        "## Effect check\n\n```bash\n# pull first\nuv run fedcourts corpus-pull\n"
        + "# Effect check: not a heading\n```\n\n- prints 3\n\n## Next\n"
    )
    check = extract_effect_check(body)
    assert check is not None
    assert "uv run fedcourts corpus-pull" in check and check.endswith("- prints 3")
    # A heading-shaped line inside a fence before any real heading is not one.
    assert extract_effect_check("```\n# Effect check\n- x\n```\n") is None


def test_a_section_cut_inside_a_fence_is_closed() -> None:
    body = f"## Effect check\n\n```bash\nrun x\n{FOOTER}\n"
    check = extract_effect_check(body)
    assert check is not None and check.count("```") % 2 == 0


def test_a_thematic_break_inside_a_check_is_kept() -> None:
    assert extract_effect_check("## Effect check\n\n- a\n\n---\n\n- b\n") == "- a\n\n---\n\n- b"


def test_windows_line_endings_are_read() -> None:
    assert extract_effect_check("## Effect check\r\n\r\n- x\r\n") == "- x"


# --- the batch ----------------------------------------------------------------


def test_sync_prs_are_split_out_and_duplicates_dropped() -> None:
    features, sync = batch_prs(
        [
            BatchPR(number=12, title="fix: b"),
            BatchPR(number=10, title="chore: sync main into staging"),
            BatchPR(number=11, title="feat: a"),
            BatchPR(number=12, title="fix: b"),
        ]
    )
    assert [pr.number for pr in features] == [11, 12]
    assert sync == [10]


def _batch(**overrides: object) -> Batch:
    data: dict[str, object] = {
        "staging_sha": "a" * 40,
        "main_sha": "b" * 40,
        "prs": [
            BatchPR(number=1, title="feat: one", body="## Effect check\n\n- `cmd` prints 3\n"),
            BatchPR(number=2, title="docs: two", body="## What changed\n\nprose\n"),
        ],
        "sync_prs": [3],
        "gate": [
            GateCheck(name="quiescence", ok=True),
            GateCheck(name="freshness", ok=False, detail="missing gate run"),
        ],
        "owed_fills": ["<FILL: promotion tag>"],
    }
    data.update(overrides)
    return Batch.model_validate(data)


def test_the_block_carries_the_batch_checks_gate_and_owed_fills() -> None:
    block = render(_batch(), drafted_at="2026-10-11T12:00Z")
    assert block.startswith(BEGIN) and block.endswith(END)
    assert "- #1: feat: one" in block and "- Sync: #3" in block
    assert "### #1: feat: one\n\n> - `cmd` prints 3" in block
    assert "**No effect-check note found.**" in block and "- #2: docs: two" in block
    assert "- freshness: **not yet** — missing gate run" in block
    assert "integration-test.yml --ref staging -f scenario=gate" in block
    assert "`<FILL: promotion tag>`" in block


def test_a_clean_gate_says_to_merge_with_a_merge_commit() -> None:
    block = render(
        _batch(gate=[GateCheck(name="quiescence", ok=True), GateCheck(name="freshness", ok=True)]),
        drafted_at="t",
    )
    assert "merge with a **merge commit**" in block
    assert "scenario=gate" not in block


# --- splicing into an edited body --------------------------------------------


def test_a_refresh_keeps_everything_outside_the_markers() -> None:
    first = render(_batch(), drafted_at="t1")
    edited = f"My summary of the batch.\n\n{first}\n\nA note after."
    refreshed = splice(edited, render(_batch(), drafted_at="t2"))
    assert refreshed.startswith("My summary of the batch.")
    assert refreshed.endswith("A note after.")
    assert "t2" in refreshed and "t1" not in refreshed
    assert refreshed.count(BEGIN) == 1


def test_pr_text_cannot_forge_or_truncate_the_markers() -> None:
    hostile = _batch(
        prs=[
            BatchPR(
                number=9,
                title=f"docs: the `{END}` marker",
                body=f"## Effect check\n\n- quote {BEGIN} and {END}\n",
            )
        ]
    )
    body = "Prose."
    for stamp in ("t1", "t2", "t3"):
        body = splice(body, render(hostile, drafted_at=stamp))
    assert body.count(BEGIN) == 1 and body.count(END) == 1
    assert body.count("## After the merge") == 1
    assert body.endswith("Prose.")


def test_a_mention_in_a_title_does_not_notify_but_a_command_keeps_its_at() -> None:
    body = "## Effect check\n\n```\njq -r '.[] | @tsv'\n```\n"
    block = render(
        _batch(prs=[BatchPR(number=4, title="fix: thanks @someone", body=body)]),
        drafted_at="t",
    )
    assert "@someone" not in block
    assert "@tsv" in block


def test_the_two_fence_kinds_do_not_close_each_other() -> None:
    body = "## Effect check\n\n~~~\nx\n```\n# not a heading\n~~~\n\n- after\n\n## Next\n"
    assert extract_effect_check(body) == "~~~\nx\n```\n# not a heading\n~~~\n\n- after"
    cut = extract_effect_check(f"## Effect check\n\n~~~~\nrun\n{FOOTER}\n")
    assert cut is not None and cut.endswith("~~~~")


def test_the_next_step_puts_marking_ready_before_the_dispatch() -> None:
    block = render(_batch(), drafted_at="t")
    ready = block.index("mark this PR ready")
    assert ready < block.index("scenario=gate") < block.index("re-run `promotion-gate`")


def test_a_round_trip_through_the_api_is_stable() -> None:
    # GitHub returns the body without a trailing newline, the workflow's `jq -r`
    # adds one, and the command's echo adds another: none of that is a change.
    first = splice("Prose.", render(_batch(), drafted_at="t1"))
    again = splice(first + "\n", render(_batch(), drafted_at="t2"))
    assert same_body(first + "\n", again)
    assert not same_body(first, splice(first, render(_batch(owed_fills=[]), drafted_at="t2")))


def test_a_body_without_a_block_gets_one_first() -> None:
    assert splice("", "BLOCK") == "BLOCK"
    assert splice("existing", "BLOCK") == "BLOCK\n\nexisting"


def test_a_stray_begin_marker_loses_nothing() -> None:
    damaged = f"head\n{BEGIN}\ntail with no end"
    assert splice(damaged, "BLOCK").endswith(damaged)


# --- the command --------------------------------------------------------------


def test_the_command_renders_and_splices(tmp_path: Path) -> None:
    batch = tmp_path / "batch.json"
    batch.write_text(
        json.dumps(
            {
                "staging_sha": "c" * 40,
                "main_sha": "d" * 40,
                "prs": [
                    {"number": 5, "title": "chore: sync main into staging", "body": ""},
                    {"number": 4, "title": "feat: x", "body": "## Effect check\n\n- y\n"},
                ],
                "gate": [{"name": "quiescence", "ok": True, "detail": ""}],
                "owed_fills": [],
            }
        )
    )
    existing = tmp_path / "body.md"
    existing.write_text("Maintainer prose.")
    result = CliRunner().invoke(
        app,
        [
            "promotion-body",
            "--batch-file",
            str(batch),
            "--drafted-at",
            "now",
            "--existing-body-file",
            str(existing),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "- #4: feat: x" in result.stdout and "- Sync: #5" in result.stdout
    assert result.stdout.rstrip().endswith("Maintainer prose.")


def test_the_command_exits_3_when_only_the_stamp_would_change(tmp_path: Path) -> None:
    batch = tmp_path / "batch.json"
    batch.write_text(_batch().model_dump_json())
    existing = tmp_path / "body.md"
    existing.write_text("Prose.")
    base = ["promotion-body", "--batch-file", str(batch), "--existing-body-file", str(existing)]
    first = CliRunner().invoke(app, [*base, "--drafted-at", "t1"])
    assert first.exit_code == 0, first.output
    # As the workflow stores it: GitHub's body, read back with a trailing newline.
    existing.write_text(first.stdout)
    second = CliRunner().invoke(app, [*base, "--drafted-at", "t2", "--exit-unchanged"])
    assert second.exit_code == 3 and second.stdout == ""


def test_the_command_refuses_a_malformed_batch(tmp_path: Path) -> None:
    batch = tmp_path / "batch.json"
    batch.write_text(json.dumps({"prs": "nope"}))
    result = CliRunner().invoke(
        app, ["promotion-body", "--batch-file", str(batch), "--drafted-at", "now"]
    )
    assert result.exit_code == 1


# --- review follow-ups --------------------------------------------------------


def test_a_missing_note_is_never_asked_for_inside_the_block() -> None:
    # Text written inside the markers is lost at the next refresh, so the block
    # points at the feature PR or below the end marker, never "here".
    block = render(_batch(), drafted_at="t")
    assert "write one here" not in block
    assert "feature PR's description" in block and "below the end marker" in block


def test_an_open_sync_pr_is_named_before_the_dispatch() -> None:
    block = render(_batch(open_sync_prs=[77]), drafted_at="t")
    assert block.index("mark this PR ready") < block.index("#77") < block.index("scenario=gate")
    clean = render(
        _batch(
            open_sync_prs=[77],
            gate=[GateCheck(name="quiescence", ok=True), GateCheck(name="freshness", ok=True)],
        ),
        drafted_at="t",
    )
    assert "#77 land (or close it)" in clean
    assert "#77" not in render(_batch(), drafted_at="t")


def test_a_commit_pushed_without_a_pr_is_listed() -> None:
    block = render(_batch(unmapped_commits=["c" * 40]), drafted_at="t")
    assert "Pushed to staging with no PR" in block and "`ccccccccc`" in block


def test_a_note_is_quoted_so_a_comment_cannot_hide_the_block() -> None:
    body = "## Effect check\n\n- see <!-- unclosed\n- thanks @someone, run `jq '@csv'`\n"
    block = render(_batch(prs=[BatchPR(number=5, title="x", body=body)]), drafted_at="t")
    assert "> - see <!-- unclosed" in block
    assert "&#64;someone" in block and "`jq '@csv'`" in block
    # The rest of the block follows the quote, outside it.
    assert "\n## After the merge" in block


def test_an_oversized_batch_defers_notes_instead_of_overflowing() -> None:
    long_note = "## Effect check\n\n" + ("- line\n" * 3000)
    prs = [BatchPR(number=n, title=f"feat {n}", body=long_note) for n in range(10, 20)]
    block = render(_batch(prs=prs), drafted_at="t")
    assert len(block) < 65_536
    assert "more effect-check note(s)" in block and "#19" in block


def test_a_gate_count_change_alone_is_not_a_change() -> None:
    first = render(
        _batch(gate=[GateCheck(name="quiescence", ok=False, detail="2 run(s) in flight")]),
        drafted_at="t1",
    )
    second = render(
        _batch(gate=[GateCheck(name="quiescence", ok=False, detail="3 run(s) in flight")]),
        drafted_at="t2",
    )
    assert same_body(first, second)
    flipped = render(_batch(gate=[GateCheck(name="quiescence", ok=True)]), drafted_at="t3")
    assert not same_body(first, flipped)


# --- A promotion train candidate ----------------------------------------------


def _candidate(**overrides: object) -> Batch:
    data: dict[str, object] = {
        "head_ref": "promote/2026-10-17",
        "train_status": "awaiting approval",
    }
    data.update(overrides)
    return _batch(**data)


def test_a_candidate_block_names_its_frozen_head_and_the_train_step() -> None:
    block = render(_candidate(), drafted_at="2026-10-17T05:26Z")
    assert "_Drafted by the promotion train at 2026-10-17T05:26Z for `promote/2026-10-17`" in block
    assert "never moves" in block
    assert "**Train:** awaiting approval" in block
    assert "approve this PR at `aaaaaaaaa`" in block
    assert "**merge commit**" in block
    # The manual flow's steps belong to a hand-opened staging promotion only.
    assert "mark it ready" not in block
    assert "--ref staging" not in block
    # The batch, its notes and the owed fills render as for any promotion.
    assert "- #1: feat: one" in block
    assert "<FILL: promotion tag>" in block


def test_a_candidate_refresh_that_moves_only_the_stamp_is_not_a_change() -> None:
    first = splice("Prose.", render(_candidate(), drafted_at="t1"))
    again = splice(first, render(_candidate(), drafted_at="t2"))
    assert same_body(first, again)
    moved = splice(first, render(_candidate(train_status="gate running"), drafted_at="t3"))
    assert not same_body(first, moved)
    assert moved.endswith("Prose.")


def test_a_quoted_ready_marker_is_defused() -> None:
    """A feature PR's note carrying the train's ready marker is quoted with the
    marker defused, so the candidate's body never reads as marked by the train."""
    marker = "<!-- promotion-train:marked-ready -->"
    note = f"## Effect check\n\n- `cmd` prints 3 {marker}\n"
    block = render(_candidate(prs=[BatchPR(number=9, title="x", body=note)]), drafted_at="t")
    assert marker not in block
    assert "&lt;!-- promotion-train:marked-ready -->" in block
    status = render(_candidate(train_status=f"x {marker}"), drafted_at="t")
    assert marker not in status


def test_a_train_status_cannot_forge_or_cut_the_block() -> None:
    block = render(_candidate(train_status=f"x {END} y {BEGIN}"), drafted_at="t")
    assert block.count(END) == 1
    assert block.count(BEGIN) == 1


def test_the_cli_renders_a_candidate_from_its_batch_file(tmp_path: Path) -> None:
    batch = tmp_path / "batch.json"
    batch.write_text(
        json.dumps(
            {
                "staging_sha": "c" * 40,
                "main_sha": "d" * 40,
                "prs": [],
                "head_ref": "promote/2026-10-17-2",
                "train_status": "dispatched the integration gate",
            }
        )
    )
    result = CliRunner().invoke(
        app, ["promotion-body", "--batch-file", str(batch), "--drafted-at", "t"]
    )
    assert result.exit_code == 0, result.output
    assert "`promote/2026-10-17-2` at `ccccccccc`" in result.output
    assert "**Train:** dispatched the integration gate" in result.output
