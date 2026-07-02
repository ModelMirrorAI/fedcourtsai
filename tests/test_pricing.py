"""Per-run cost estimation from token counts."""

import pytest

from fedcourtsai.pricing import (
    CACHE_CREATION_MULTIPLIER,
    CACHE_READ_MULTIPLIER,
    DEFAULT_MODELS,
    MODEL_RATES,
    TokenCounts,
    estimate_cost_usd,
)


def test_default_models_have_rates() -> None:
    # Every engine's default model must be priceable, or capture would fail.
    for model in DEFAULT_MODELS.values():
        assert model in MODEL_RATES


def test_gemini_default_model_and_rate() -> None:
    assert DEFAULT_MODELS["gemini"] == "gemini-3.1-pro-preview"
    rate = MODEL_RATES["gemini-3.1-pro-preview"]
    assert (rate.input_per_mtok, rate.output_per_mtok) == (2.0, 12.0)


def test_claude_default_model_and_rate() -> None:
    # Predict/evaluate default to Fable 5; run-dev / run-reconcile stay pinned to
    # claude-opus-4-8 in their workflows, so its rate must stay priceable too.
    assert DEFAULT_MODELS["claude-code"] == "claude-fable-5"
    rate = MODEL_RATES["claude-fable-5"]
    assert (rate.input_per_mtok, rate.output_per_mtok) == (10.0, 50.0)
    assert "claude-opus-4-8" in MODEL_RATES


def test_plain_input_output_cost() -> None:
    # 1M input + 1M output on claude-opus-4-8 ($5 in / $25 out) = $30.
    counts = TokenCounts(input_tokens=1_000_000, output_tokens=1_000_000)
    assert estimate_cost_usd("claude-opus-4-8", counts) == pytest.approx(30.0)


def test_cache_buckets_apply_their_multipliers() -> None:
    counts = TokenCounts(cache_read_input_tokens=1_000_000, cache_creation_input_tokens=1_000_000)
    rate = MODEL_RATES["claude-opus-4-8"].input_per_mtok
    expected = rate * CACHE_READ_MULTIPLIER + rate * CACHE_CREATION_MULTIPLIER
    assert estimate_cost_usd("claude-opus-4-8", counts) == pytest.approx(expected)


def test_planning_assumption_lands_in_dollar_range() -> None:
    # ~200K input + 12K output (docs/budget.md) should land near the ~$1-2 guess.
    counts = TokenCounts(input_tokens=200_000, output_tokens=12_000)
    cost = estimate_cost_usd("claude-opus-4-8", counts)
    assert 1.0 <= cost <= 2.0


def test_unknown_model_raises() -> None:
    with pytest.raises(KeyError):
        estimate_cost_usd("no-such-model", TokenCounts(input_tokens=10))


def test_total_tokens_sums_all_buckets() -> None:
    counts = TokenCounts(
        input_tokens=1,
        output_tokens=2,
        cache_read_input_tokens=4,
        cache_creation_input_tokens=8,
    )
    assert counts.total_tokens == 15
