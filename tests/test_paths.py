from pathlib import Path

from fedcourtsai.paths import CasePaths


def test_case_layout() -> None:
    cp = CasePaths(Path("data"), "ca9", 123)
    assert cp.case_file == Path("data/cases/ca9/123/case.yaml")
    assert cp.snapshot("2026-06-24") == Path("data/cases/ca9/123/record/snapshots/2026-06-24.json")


def test_event_layout() -> None:
    ep = CasePaths(Path("data"), "ca9", 123).event("evt-motion-stay")
    assert ep.prediction("claude-baseline", "20260624T000000Z") == Path(
        "data/cases/ca9/123/events/evt-motion-stay/predictions/"
        "claude-baseline/20260624T000000Z/prediction.json"
    )
    assert ep.evaluation("codex-judge", "claude-baseline", "r1") == Path(
        "data/cases/ca9/123/events/evt-motion-stay/evaluations/"
        "codex-judge/claude-baseline/r1/evaluation.json"
    )
