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


class CorpusRow(_Strict):
    """One normalized, labeled record in the packed historical corpus.

    Produced by ``seed`` from CourtListener bulk data and stored in bulk as
    Parquet shards under ``corpus/`` (DVC-tracked), **not** as per-row files —
    this model is the column contract for those shards. Each row carries its
    outcome label (``disposition``) so the corpus doubles as a back-test set, and
    the structured columns make it queryable for retrieval. See
    ``docs/data-pipeline.md`` and ``corpus/README.md``.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    court: str
    docket_number: str = ""
    date_filed: date | None = None
    date_decided: date | None = None
    disposition: Disposition | None = Field(
        default=None, description="Outcome label; None while the matter is unresolved"
    )
    judges: list[str] = Field(default_factory=list)
    nature_topic: str | None = Field(
        default=None, description="Nature of suit / topic classification"
    )
    citations: list[str] = Field(default_factory=list)
    opinion_summary: str | None = Field(
        default=None, description="Opinion text or a generated summary"
    )
    embedding: list[float] | None = Field(
        default=None, description="Optional semantic embedding; a later retrieval upgrade"
    )


class CourtCursor(_Strict):
    """Per-court backfill progress for one court in the seed cursor."""

    court: str
    rows_loaded: int = Field(default=0, ge=0)
    last_date_filed: date | None = Field(
        default=None, description="High-water mark: newest date_filed loaded so far"
    )
    complete: bool = False


class SeedProgress(_Strict):
    """``config/seed-progress.yaml`` — resumable cursor for the bulk backfill.

    Records what the corpus has loaded per court so the daily seed run resumes
    cleanly and the corpus is rebuildable after a fresh clone (pointer + cursor in
    git, blobs in the DVC remote).
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    bulk_snapshot: str | None = Field(
        default=None, description="Identifier of the quarterly bulk snapshot last processed"
    )
    courts: list[CourtCursor] = Field(default_factory=list)


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
}

EXPORTABLE_MODELS: dict[str, type[BaseModel]] = {
    "case": TrackedCase,
    "event": PredictableEvent,
    "prediction": Prediction,
    "outcome": Outcome,
    "evaluation": Evaluation,
    "predictor_config": PredictorConfig,
    "evaluator_config": EvaluatorConfig,
    "corpus_row": CorpusRow,
    "seed_progress": SeedProgress,
}
