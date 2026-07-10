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


def test_usage_layout() -> None:
    ep = CasePaths(Path("data"), "ca9", 123).event("evt-motion-stay")
    assert ep.prediction_usage("claude-baseline", "r1") == Path(
        "data/cases/ca9/123/events/evt-motion-stay/predictions/claude-baseline/r1/usage.json"
    )
    # Evaluate usage is keyed by evaluator x run, a level above the predictor dirs.
    assert ep.evaluation_usage("codex-judge", "r1") == Path(
        "data/cases/ca9/123/events/evt-motion-stay/evaluations/codex-judge/r1/usage.json"
    )


def test_flags_layout() -> None:
    ep = CasePaths(Path("data"), "ca9", 123).event("evt-motion-stay")
    # A predict cell's flags.json sits beside its prediction.
    assert ep.prediction_flags("claude-baseline", "r1") == Path(
        "data/cases/ca9/123/events/evt-motion-stay/predictions/claude-baseline/r1/flags.json"
    )
    # An evaluate cell's flags.json is keyed by evaluator x run, like its usage.
    assert ep.evaluation_flags("codex-judge", "r1") == Path(
        "data/cases/ca9/123/events/evt-motion-stay/evaluations/codex-judge/r1/flags.json"
    )


def test_tooling_layout() -> None:
    ep = CasePaths(Path("data"), "ca9", 123).event("evt-motion-stay")
    # tooling.json sits beside its stage's flags.json.
    assert ep.prediction_tooling("claude-baseline", "r1") == Path(
        "data/cases/ca9/123/events/evt-motion-stay/predictions/claude-baseline/r1/tooling.json"
    )
    assert ep.evaluation_tooling("codex-judge", "r1") == Path(
        "data/cases/ca9/123/events/evt-motion-stay/evaluations/codex-judge/r1/tooling.json"
    )


def test_reconcile_layout_is_case_level() -> None:
    # Reconcile fans out per case, so its flags/tooling live at the case root, above
    # the per-event outcomes.
    cp = CasePaths(Path("data"), "ca9", 123)
    assert cp.reconcile_flags("r1") == Path("data/cases/ca9/123/reconcile/r1/flags.json")
    assert cp.reconcile_tooling("r1") == Path("data/cases/ca9/123/reconcile/r1/tooling.json")
