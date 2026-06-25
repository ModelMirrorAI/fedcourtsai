"""Parsing token usage out of the engines' own run logs."""

import json
from pathlib import Path

from fedcourtsai.usage import parse_claude_usage, parse_codex_usage


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
