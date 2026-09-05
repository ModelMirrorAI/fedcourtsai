from pathlib import Path

import pytest

from fedcourtsai import casestore
from fedcourtsai.paths import (
    CASESTORE_SEGMENT,
    CasePaths,
    casestore_url,
    corpus_index_url,
)


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


def test_store_addresses_derive_from_one_base_url() -> None:
    # One address names an environment's whole corpus estate; the index remote
    # and the content store are fixed segments beneath it.
    assert corpus_index_url("s3://estate/pfx") == "s3://estate/pfx/store"
    assert casestore_url("s3://estate/pfx") == "s3://estate/pfx/casestore/v1"
    # A bare bucket is a base URL too.
    assert corpus_index_url("s3://estate") == "s3://estate/store"


def test_a_padded_or_slashed_base_lands_on_the_same_addresses() -> None:
    # The base arrives from a settings value, so a stray trailing slash or a
    # padded variable must not produce a second spelling of the same store.
    assert corpus_index_url("  s3://estate/pfx//  ") == "s3://estate/pfx/store"
    assert casestore_url("s3://estate/") == "s3://estate/casestore/v1"


def test_a_blank_base_is_refused_rather_than_relativized() -> None:
    # A blank base would otherwise yield "/store" — a string no URL parser
    # rejects for the reason it is wrong, so the missing configuration would
    # surface as a store that is simply not there.
    for blank in ("", "   "):
        with pytest.raises(ValueError, match="corpus base URL is empty"):
            corpus_index_url(blank)
        with pytest.raises(ValueError, match="corpus base URL is empty"):
            casestore_url(blank)


def test_the_content_store_segment_has_exactly_one_definition() -> None:
    # casestore's bare-bucket default and the base URL's derived address must
    # name the same objects, or the two spellings of a store address diverge.
    assert casestore.DEFAULT_PREFIX == CASESTORE_SEGMENT
