"""Model token rates and per-run cost estimation — the single place to keep prices.

The dominant cost in this project is agentic model usage (see ``docs/budget.md``).
The planning assumption there (~$1-2 per predict/evaluate run) is a guess; the
``usage.json`` artifact records measured per-run tokens and applies the rates
below to turn them into an estimated USD cost. Keep these rates in sync with
``docs/budget.md`` — they are the one knob a maintainer updates when prices move.

Rates are USD per **one million** tokens, captured mid-2026; treat them as a
snapshot and re-check the budget doc's linked sources before relying on a figure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# Prompt-cache multipliers applied to the input rate. Cached *reads* bill at a
# deep discount; cache *creation* (writes) at a small premium. The numbers mirror
# the discounts noted in docs/budget.md and are close enough for a cost estimate.
CACHE_READ_MULTIPLIER: Final = 0.1
CACHE_CREATION_MULTIPLIER: Final = 1.25

_PER_MILLION: Final = 1_000_000


@dataclass(frozen=True)
class ModelRate:
    """On-demand USD rate per one million input / output tokens."""

    input_per_mtok: float
    output_per_mtok: float


# Keyed by the model id the engine actually ran. The two production models are
# claude-opus-4-8 and gpt-5.5; the cheaper Claude tiers are listed because the
# budget doc names them as competitor-model levers.
MODEL_RATES: Final[dict[str, ModelRate]] = {
    "claude-opus-4-8": ModelRate(5.0, 25.0),
    "claude-sonnet-4-6": ModelRate(3.0, 15.0),
    "claude-haiku-4-5": ModelRate(1.0, 5.0),
    "gpt-5.5": ModelRate(5.0, 30.0),
}

# The model each engine runs when a predictor/evaluator pins no explicit override
# (registry ``model: null``). Mirrors the ``--model`` defaults in the run-predict
# and run-evaluate workflows.
DEFAULT_MODELS: Final[dict[str, str]] = {
    "claude-code": "claude-opus-4-8",
    "codex": "gpt-5.5",
}


@dataclass(frozen=True)
class TokenCounts:
    """A run's token usage, split into the buckets that bill at different rates.

    ``input_tokens`` is fresh (uncached) input; ``cache_read_input_tokens`` is
    input served from the prompt cache (billed at ``CACHE_READ_MULTIPLIER``); and
    ``cache_creation_input_tokens`` is input written to the cache (billed at
    ``CACHE_CREATION_MULTIPLIER``). Engines report these under different names and
    conventions; the parsers in ``fedcourtsai.usage`` normalize to this shape so
    cost estimation is engine-agnostic.
    """

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_read_input_tokens
            + self.cache_creation_input_tokens
        )


def estimate_cost_usd(model: str, counts: TokenCounts) -> float:
    """Estimated on-demand USD cost of ``counts`` at ``model``'s rates.

    Raises ``KeyError`` if ``model`` has no entry in ``MODEL_RATES`` — callers
    decide whether an unknown model is fatal or merely skips cost capture.
    """
    rate = MODEL_RATES[model]
    return (
        counts.input_tokens * rate.input_per_mtok
        + counts.cache_read_input_tokens * rate.input_per_mtok * CACHE_READ_MULTIPLIER
        + counts.cache_creation_input_tokens * rate.input_per_mtok * CACHE_CREATION_MULTIPLIER
        + counts.output_tokens * rate.output_per_mtok
    ) / _PER_MILLION
