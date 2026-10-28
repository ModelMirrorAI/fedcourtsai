"""Parsing token usage out of the engines' own run logs."""

import json
import subprocess
from pathlib import Path

import pytest

from fedcourtsai.pricing import TokenCounts
from fedcourtsai.usage import (
    codex_cell_rollouts,
    engine_version_from_output,
    parse_claude_usage,
    parse_codex_usage,
    parse_gemini_usage,
    resolve_engine_version,
    resolve_pipeline_sha,
)


def _write_claude(path: Path, events: list[dict[str, object]]) -> Path:
    path.write_text(json.dumps(events))
    return path


def test_claude_prefers_final_result_usage(tmp_path: Path) -> None:
    log = _write_claude(
        tmp_path / "execution.json",
        [
            {"type": "assistant", "usage": {"input_tokens": 1, "output_tokens": 1}},
            {
                "type": "result",
                "total_cost_usd": 1.23,
                "usage": {
                    "input_tokens": 150_000,
                    "output_tokens": 8_000,
                    "cache_read_input_tokens": 50_000,
                    "cache_creation_input_tokens": 2_000,
                },
            },
        ],
    )
    counts = parse_claude_usage(log)
    assert counts is not None
    assert counts.input_tokens == 150_000
    assert counts.output_tokens == 8_000
    assert counts.cache_read_input_tokens == 50_000
    assert counts.cache_creation_input_tokens == 2_000


def test_claude_falls_back_to_any_usage(tmp_path: Path) -> None:
    log = _write_claude(
        tmp_path / "execution.json",
        [{"type": "assistant", "usage": {"input_tokens": 42, "output_tokens": 7}}],
    )
    counts = parse_claude_usage(log)
    assert counts is not None
    assert counts.input_tokens == 42
    assert counts.output_tokens == 7


def test_claude_missing_or_empty_returns_none(tmp_path: Path) -> None:
    assert parse_claude_usage(tmp_path / "absent.json") is None
    empty = tmp_path / "empty.json"
    empty.write_text("[]")
    assert parse_claude_usage(empty) is None


def _codex_event(usage: dict[str, int]) -> str:
    return json.dumps(
        {
            "type": "event_msg",
            "payload": {"type": "token_count", "info": {"total_token_usage": usage}},
        }
    )


def test_codex_uses_last_cumulative_event_and_splits_cache(tmp_path: Path) -> None:
    day = tmp_path / "sessions" / "2026" / "06" / "25"
    day.mkdir(parents=True)
    (day / "rollout-2026-06-25T10-00-00-abc.jsonl").write_text(
        "\n".join(
            [
                "not json, ignore me",
                _codex_event(
                    {"input_tokens": 50_000, "cached_input_tokens": 10_000, "output_tokens": 3_000}
                ),
                _codex_event(
                    {"input_tokens": 120_000, "cached_input_tokens": 40_000, "output_tokens": 9_000}
                ),
            ]
        )
    )
    counts = parse_codex_usage(tmp_path / "sessions")
    assert counts is not None
    # Codex input includes the cached portion; it is split out and subtracted.
    assert counts.input_tokens == 80_000
    assert counts.cache_read_input_tokens == 40_000
    assert counts.output_tokens == 9_000
    assert counts.cache_creation_input_tokens == 0


def test_codex_picks_newest_rollout(tmp_path: Path) -> None:
    sessions = tmp_path / "sessions"
    older = sessions / "2026" / "06" / "24"
    newer = sessions / "2026" / "06" / "25"
    older.mkdir(parents=True)
    newer.mkdir(parents=True)
    (older / "rollout-2026-06-24T09-00-00-old.jsonl").write_text(
        _codex_event({"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 1})
    )
    (newer / "rollout-2026-06-25T09-00-00-new.jsonl").write_text(
        _codex_event({"input_tokens": 200_000, "cached_input_tokens": 0, "output_tokens": 5_000})
    )
    counts = parse_codex_usage(sessions)
    assert counts is not None
    assert counts.input_tokens == 200_000
    assert counts.output_tokens == 5_000


def test_codex_missing_dir_returns_none(tmp_path: Path) -> None:
    assert parse_codex_usage(tmp_path / "nope") is None


def _gemini_event(
    input_tokens: int, cached: int, output_tokens: int, thoughts: int
) -> dict[str, object]:
    return {
        "name": "gemini_cli.api_response",
        "model": "gemini-3.1-pro-preview",
        "input_token_count": input_tokens,
        "cached_content_token_count": cached,
        "output_token_count": output_tokens,
        "thoughts_token_count": thoughts,
    }


def test_gemini_sums_per_call_events_and_normalizes(tmp_path: Path) -> None:
    log = tmp_path / "telemetry.log"
    # The local OTEL exporter concatenates pretty-printed records, not one-per-line.
    log.write_text(
        "\n".join(
            json.dumps(e, indent=2)
            for e in [
                _gemini_event(50_000, 10_000, 3_000, 500),
                _gemini_event(120_000, 40_000, 9_000, 1_500),
            ]
        )
    )
    counts = parse_gemini_usage(log)
    assert counts is not None
    # input_token_count includes cached; cached is split out and subtracted.
    assert counts.input_tokens == 120_000  # (50k+120k) - (10k+40k)
    assert counts.cache_read_input_tokens == 50_000
    # Thinking tokens bill as output, so they fold into output_tokens.
    assert counts.output_tokens == 14_000  # (3k+9k) + (500+1500)
    assert counts.cache_creation_input_tokens == 0


def test_gemini_handles_otlp_nested_attributes(tmp_path: Path) -> None:
    log = tmp_path / "telemetry.log"
    log.write_text(
        json.dumps(
            {
                "body": "gemini_cli.api_response",
                "attributes": [
                    {"key": "input_token_count", "value": {"intValue": "100"}},
                    {"key": "output_token_count", "value": {"intValue": "20"}},
                ],
            }
        )
    )
    counts = parse_gemini_usage(log)
    assert counts is not None
    assert counts.input_tokens == 100
    assert counts.output_tokens == 20
    assert counts.cache_read_input_tokens == 0


def test_gemini_missing_empty_or_tokenless_returns_none(tmp_path: Path) -> None:
    assert parse_gemini_usage(tmp_path / "absent.log") is None
    empty = tmp_path / "empty.log"
    empty.write_text("")
    assert parse_gemini_usage(empty) is None
    tokenless = tmp_path / "tokenless.log"
    tokenless.write_text(json.dumps({"name": "gemini_cli.tool_call", "function": "read_file"}))
    assert parse_gemini_usage(tokenless) is None


# --- engine version provenance ---------------------------------------------------


@pytest.mark.parametrize(
    ("output", "expected"),
    [
        ("2.1.289 (Claude Code)\n", "2.1.289"),
        ("codex-cli 0.144.1", "0.144.1"),
        ("0.49.0\n", "0.49.0"),
        ("", None),
        ("unknown", None),
        # A longer dotted string is not a version: neither an address nor a
        # four-part build number may be cut down to three parts.
        ("listening on 10.0.0.1", None),
        ("build 1.2.3.4", None),
    ],
)
def test_the_engine_version_is_the_first_standalone_three_part_version(
    output: str, expected: str | None
) -> None:
    assert engine_version_from_output(output) == expected


@pytest.mark.parametrize(
    ("at_install", "after_run", "pin", "recorded", "discrepancy"),
    [
        # Every read agrees: the install-time read is recorded, nothing flagged.
        ("2.1.289 (Claude Code)", "2.1.289 (Claude Code)", "2.1.289", "2.1.289", None),
        # The binary changed during the cell: the install-time read stands.
        (
            "2.1.289 (Claude Code)",
            "2.1.300 (Claude Code)",
            "2.1.289",
            "2.1.289",
            "the binary reported 2.1.300 after the run but 2.1.289 at install",
        ),
        # codex has no install-time read: the after-run read is recorded and
        # checked against the pin its action was told to install.
        ("", "codex-cli 0.144.1", "0.144.1", "0.144.1", None),
        (
            "",
            "codex-cli 0.145.0",
            "0.144.1",
            "0.145.0",
            "the binary reported 0.145.0 but the pin is 0.144.1",
        ),
        # No read at all records nothing and flags nothing.
        ("", "", "0.49.0", None, None),
    ],
)
def test_the_recorded_engine_version_keeps_the_install_read_and_flags_disagreement(
    at_install: str, after_run: str, pin: str, recorded: str | None, discrepancy: str | None
) -> None:
    assert resolve_engine_version(at_install, after_run, pin) == (recorded, discrepancy)


# --- pipeline provenance ---------------------------------------------------------


def test_pipeline_sha_explicit_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_SHA", "env-sha")
    assert resolve_pipeline_sha("explicit-sha") == "explicit-sha"


def test_pipeline_sha_prefers_the_actions_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # In CI, GITHUB_SHA is the exact workflow checkout — never shell out for it.
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    assert resolve_pipeline_sha() == "abc123"


def test_pipeline_sha_falls_back_to_the_local_head(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert resolve_pipeline_sha() == head


def test_pipeline_sha_unresolvable_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    # Provenance is best-effort: no env and no git must not fail the capture.
    monkeypatch.delenv("GITHUB_SHA", raising=False)

    def boom(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", boom)
    assert resolve_pipeline_sha() is None


def _codex_session(path: Path, meta: dict[str, object], usage: dict[str, int]) -> None:
    """One rollout: its ``session_meta`` line, then a cumulative token event."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"type": "session_meta", "payload": meta}) + "\n" + _codex_event(usage)
    )


def test_a_subagent_rollout_newer_than_its_parent_is_not_taken_for_the_cell(
    tmp_path: Path,
) -> None:
    day = tmp_path / "sessions" / "2026" / "10" / "16"
    parent = day / "rollout-2026-10-16T09-00-00-parent.jsonl"
    child = day / "rollout-2026-10-16T09-05-00-child.jsonl"
    _codex_session(
        parent,
        {"id": "p", "source": "exec"},
        {"input_tokens": 1_000, "cached_input_tokens": 400, "output_tokens": 100},
    )
    _codex_session(
        child,
        {
            "id": "c",
            "source": {"subagent": {"thread_spawn": {"parent_thread_id": "p", "depth": 1}}},
        },
        {"input_tokens": 50, "cached_input_tokens": 10, "output_tokens": 5},
    )
    assert codex_cell_rollouts(tmp_path / "sessions") == [parent, child]
    counts = parse_codex_usage(tmp_path / "sessions")
    # Parent and subagent bill side by side, so both sum into the cell.
    assert counts == TokenCounts(
        input_tokens=640, output_tokens=105, cache_read_input_tokens=410
    )


def test_cell_rollouts_follow_the_parent_chain_and_skip_another_top_level_session(
    tmp_path: Path,
) -> None:
    day = tmp_path / "sessions" / "2026" / "10" / "16"
    usage = {"input_tokens": 1, "cached_input_tokens": 0, "output_tokens": 1}
    earlier = day / "rollout-2026-10-16T08-00-00-earlier.jsonl"
    parent = day / "rollout-2026-10-16T09-00-00-parent.jsonl"
    grandchild = day / "rollout-2026-10-16T09-01-00-grandchild.jsonl"
    child = day / "rollout-2026-10-16T09-02-00-child.jsonl"
    orphan = day / "rollout-2026-10-16T09-03-00-compact.jsonl"
    _codex_session(earlier, {"id": "e", "source": "exec"}, usage)
    _codex_session(parent, {"id": "p", "source": "exec"}, usage)
    _codex_session(grandchild, {"id": "g", "parent_thread_id": "c", "source": "exec"}, usage)
    _codex_session(child, {"id": "c", "parent_thread_id": "p", "source": "exec"}, usage)
    _codex_session(orphan, {"id": "o", "source": {"subagent": "compact"}}, usage)
    assert codex_cell_rollouts(tmp_path / "sessions") == [parent, grandchild, child, orphan]
