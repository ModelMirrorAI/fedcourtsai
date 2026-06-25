"""Pydantic models defining the on-disk data contract for the pipeline.

Every artifact written under ``data/cases/`` validates against one of these
models. They are the single source of truth for the data shape and are also
exported to JSON Schema (see ``fedcourts export-schemas``) so that coding
agents and Codex ``--output-schema`` can target them directly.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION: Final = "1.0"


class Engine(StrEnum):
    """Agentic coding engine that produced an artifact."""

    claude_code = "claude-code"
    codex = "codex"


class CaseStatus(StrEnum):
    active = "active"
    closed = "closed"
    paused = "paused"


class Disposition(StrEnum):
    granted = "granted"
    denied = "denied"
    granted_in_part = "granted-in-part"
    dismissed = "dismissed"
    withdrawn = "withdrawn"
    other = "other"


class EventKind(StrEnum):
    motion = "motion"
    petition = "petition"
    appeal = "appeal"
    order = "order"


class UsageRole(StrEnum):
    """Which agentic stage a usage record belongs to."""

    predictor = "predictor"
    evaluator = "evaluator"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class TrackedCase(_Strict):
    """``case.yaml`` — canonical metadata for one tracked docket."""

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    court_id: str
    docket_id: int
    docket_number: str = ""
    case_name: str = ""
    courtlistener_url: str | None = None
    status: CaseStatus = CaseStatus.active
    tracked_since: date
    last_pulled: datetime | None = None
    notes: str | None = None


class PredictableEvent(_Strict):
    """``event.yaml`` — one thing the system predicts about a case."""

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    event_id: str
    case_id: str
    kind: EventKind
    title: str
    description: str | None = None
    docket_entry_id: int | None = None
    opened_at: date | None = None
    decision_target: str = "disposition"
    resolved: bool = False


class JudgeVote(_Strict):
    judge: str
    vote: Disposition


class Prediction(_Strict):
    """``prediction.json`` — one predictor's quantitative output for an event."""

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    event_id: str
    predictor_id: str
    engine: Engine
    model: str | None = None
    run_id: str
    created_at: datetime
    input_snapshot: str = Field(description="Repo-relative path to the snapshot used as input")
    granted: int = Field(ge=0, le=1, description="Binary outcome prediction, 1=granted")
    probability: float = Field(ge=0.0, le=1.0, description="P(granted)")
    predicted_disposition: Disposition
    votes: list[JudgeVote] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    reasoning_doc: str = "reasoning.md"


class Outcome(_Strict):
    """``outcome.json`` — realized ground truth, written once an event resolves."""

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    event_id: str
    resolved_at: date
    actual_disposition: Disposition
    actual_granted: int = Field(ge=0, le=1)
    votes: list[JudgeVote] = Field(default_factory=list)
    source: str | None = Field(default=None, description="Docket entry id or citation")


class Evaluation(_Strict):
    """``evaluation.json`` — one evaluator scoring one predictor's prediction."""

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    event_id: str
    predictor_id: str
    evaluator_id: str
    run_id: str
    created_at: datetime
    correct: int = Field(ge=0, le=1, description="1 if disposition matched outcome")
    brier_score: float | None = Field(default=None, ge=0.0, le=1.0)
    vote_accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    reasoning_quality: float | None = Field(default=None, ge=0.0, le=1.0)
    notes_doc: str = "evaluation.md"


class ModelUsage(_Strict):
    """``usage.json`` — measured model token usage and estimated cost for one run.

    Written per ``run:predict`` / ``run:evaluate`` matrix cell (predictor x event
    for predict, evaluator x event for evaluate) alongside that cell's prediction
    or evaluation output. Token buckets follow the Claude convention:
    ``input_tokens`` is fresh input, with cached reads and cache writes counted
    separately so ``estimated_cost_usd`` can apply the right rate to each (see
    ``fedcourtsai.pricing``). Summing these across runs replaces the planning
    assumption in ``docs/budget.md`` with a measured \\$/run.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    event_id: str
    run_id: str
    role: UsageRole = Field(description="Which stage produced the usage")
    actor_id: str = Field(description="The predictor_id (predict) or evaluator_id (evaluate)")
    engine: Engine
    model: str = Field(description="Model the cost rates were applied to (resolved, never null)")
    created_at: datetime
    input_tokens: int = Field(ge=0, description="Fresh (uncached) input tokens")
    output_tokens: int = Field(ge=0)
    cache_read_input_tokens: int = Field(default=0, ge=0, description="Input served from cache")
    cache_creation_input_tokens: int = Field(default=0, ge=0, description="Input written to cache")
    estimated_cost_usd: float = Field(
        ge=0.0, description="On-demand USD estimate from the budget-doc rates"
    )


class LeaderboardEntry(_Strict):
    """One predictor's standings, aggregated across the evaluations ledger."""

    predictor_id: str
    rank: int = Field(ge=1, description="1-based standing; 1 is best")
    events_scored: int = Field(ge=0, description="Distinct (case, event) pairs scored")
    evaluations: int = Field(ge=0, description="Total evaluations counted for this predictor")
    evaluators: int = Field(ge=0, description="Distinct evaluators that scored this predictor")
    accuracy: float = Field(ge=0.0, le=1.0, description="Mean correctness across evaluations")
    mean_brier_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean Brier score where reported (lower is better)",
    )
    mean_vote_accuracy: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Mean panel-vote accuracy where reported"
    )
    mean_reasoning_quality: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Mean evaluator reasoning-quality score"
    )


class Leaderboard(_Strict):
    """``metrics/leaderboard.json`` — predictors ranked from the evaluations ledger.

    A deterministic, offline roll-up of every ``evaluation.json`` under ``data/``:
    one entry per predictor, ranked best-first. Computed by ``fedcourts
    leaderboard``; carries no timestamp so the same ledger always serializes
    identically.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    predictors_ranked: int = Field(ge=0, description="Number of predictors on the board")
    evaluations_total: int = Field(ge=0, description="Total evaluations aggregated")
    entries: list[LeaderboardEntry] = Field(default_factory=list)


class BacktestEntry(_Strict):
    """One predictor's standings over the historical back-test set."""

    predictor_id: str
    rank: int = Field(ge=1, description="1-based standing; 1 is best")
    events_scored: int = Field(
        ge=0, description="Resolved corpus events replayed for this predictor"
    )
    accuracy: float = Field(
        ge=0.0, le=1.0, description="Fraction whose predicted disposition matched the known label"
    )
    granted_accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="Fraction whose binary granted/denied projection matched the outcome",
    )
    mean_brier_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean Brier score of P(granted) vs the realized outcome (lower is better)",
    )


class Backtest(_Strict):
    """``metrics/backtest.json`` — predictors replayed against resolved corpus events.

    The back-test harness hides each resolved event's ``disposition``, replays
    every predictor against the remaining facts, and scores the prediction
    against the known label. Deterministic and offline — a pure function of the
    corpus, with no clock or randomness — so the same corpus always serializes
    identically. Computed by ``fedcourts backtest``; empty (zero counts) until a
    corpus with outcome labels is present.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    predictors_evaluated: int = Field(ge=0, description="Number of predictors on the board")
    events_scored: int = Field(ge=0, description="Size of the resolved-event back-test set")
    entries: list[BacktestEntry] = Field(default_factory=list)


class CourtProgress(_Strict):
    """Per-court entry in the seed cursor — how far the backfill has loaded."""

    offset: int = Field(default=0, ge=0, description="Rows consumed from this court's bulk stream")
    total: int | None = Field(
        default=None, ge=0, description="Rows for this court in the snapshot, once the stream ends"
    )
    complete: bool = False


class SeedProgress(_Strict):
    """``config/seed-progress.yaml`` — the resumable seed-backfill cursor.

    Git-tracked so the historical backfill is rebuildable after a fresh clone and
    a maintainer can read progress in a diff. ``seed-backfill`` reads it at the
    start of each run and writes the bumped cursor at the end.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    snapshot: str | None = Field(
        default=None, description="Bulk snapshot id currently being loaded, e.g. `2026-Q2`"
    )
    courts: dict[str, CourtProgress] = Field(default_factory=dict)
    completed: bool = Field(
        default=False,
        description=(
            "Human sign-off that this snapshot's backfill is finished. The backfill "
            "never sets it; run-seed opens a completion PR that flips it true, and "
            "merging that PR (which closes the tracking issue) is the acknowledgement. "
            "Distinct from the per-court `complete` flags, which the backfill sets "
            "automatically as each court's stream is exhausted."
        ),
    )


class PredictorConfig(_Strict):
    """An entry in ``config/predictors.yaml``."""

    id: str
    engine: Engine
    model: str | None = None
    prompt: str = Field(description="Repo-relative path to the prompt template")
    enabled: bool = True
    description: str | None = None


class EvaluatorConfig(_Strict):
    """An entry in ``config/evaluators.yaml``."""

    id: str
    engine: Engine
    model: str | None = None
    prompt: str
    enabled: bool = True
    description: str | None = None


# Maps on-disk filename -> the model that validates it. Used by `fedcourts validate`.
FILENAME_MODELS: dict[str, type[_Strict]] = {
    "case.yaml": TrackedCase,
    "event.yaml": PredictableEvent,
    "prediction.json": Prediction,
    "outcome.json": Outcome,
    "evaluation.json": Evaluation,
    "seed-progress.yaml": SeedProgress,
    "leaderboard.json": Leaderboard,
    "backtest.json": Backtest,
    "usage.json": ModelUsage,
}

EXPORTABLE_MODELS: dict[str, type[BaseModel]] = {
    "case": TrackedCase,
    "event": PredictableEvent,
    "prediction": Prediction,
    "outcome": Outcome,
    "evaluation": Evaluation,
    "predictor_config": PredictorConfig,
    "evaluator_config": EvaluatorConfig,
    "seed_progress": SeedProgress,
    "leaderboard": Leaderboard,
    "backtest": Backtest,
    "usage": ModelUsage,
}
