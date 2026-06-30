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
    gemini = "gemini"


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
    reconciler = "reconciler"


class FlagCategory(StrEnum):
    """What kind of thing an agent flag is about, for maintainer triage."""

    data_quality = "data-quality"
    scope = "scope"
    ambiguous_event = "ambiguous-event"
    blocked = "blocked"
    other = "other"


class FlagSeverity(StrEnum):
    """How loud an agent flag is. ``blocker`` means the cell could not finish cleanly."""

    info = "info"
    warning = "warning"
    blocker = "blocker"


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
    engine: Engine
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


class AgentFlag(_Strict):
    """One structured note a headless agent surfaces for maintainer triage.

    A typed alternative to burying a remark in ``reasoning.md`` or a trigger-issue
    comment: a ``category`` and ``severity`` so the roll-up can sort and filter, and
    a free-text ``message``. ``event_id`` narrows the flag to a single event when
    the cell spans more than one; left null it applies to the cell as a whole.
    """

    category: FlagCategory
    severity: FlagSeverity = FlagSeverity.info
    message: str = Field(
        min_length=1, max_length=2000, description="What the maintainer should know, in prose"
    )
    event_id: str | None = Field(
        default=None, description="The specific event this flag is about, if narrower than the cell"
    )


class AgentFlags(_Strict):
    """``flags.json`` — a cell's durable, structured feedback for maintainer triage.

    A predict/evaluate/reconcile cell writes this *only when it has something to
    surface* — a data-quality problem, a scope question, an ambiguous event, or the
    reason it was blocked. It rides the cell's artifact to the ``collect`` job, which
    rolls every cell's flags into the run PR body (and the Actions summary), so a
    note survives the trigger issue's closure and a maintainer sees it without
    reading every ``reasoning.md``. The agent token stays comment-only: the file is
    written locally and the trusted ``collect`` job does the surfacing.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    run_id: str
    role: UsageRole = Field(description="Which stage raised the flags")
    actor_id: str = Field(
        description="The predictor_id (predict), evaluator_id (evaluate), or reconcile agent id"
    )
    flags: list[AgentFlag] = Field(
        min_length=1, description="The notes; write the file only when there is at least one"
    )


class AgentToolingFeedback(_Strict):
    """``tooling.json`` — a cell's self-report on the agent tooling it was given.

    Unlike :class:`AgentFlags` (exception-based — written only on a problem with the
    *data or task*), every predict/evaluate/reconcile cell is *invited* to write this
    short, structured note about its *environment*: whether it used the ``fedcourts``
    corpus-query CLI, which abilities actually helped, and what was missing. Rolled up
    across runs on the run-ops dashboard, it tells maintainers whether the corpus
    tooling earns its keep and where to invest next. It is the agent's own account —
    subjective, advisory, and never a gate. The token stays comment-only: the file is
    written locally and the trusted ``collect`` job commits it with the cell's output.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    run_id: str
    role: UsageRole = Field(description="Which stage produced the report")
    actor_id: str = Field(
        description="The predictor_id (predict), evaluator_id (evaluate), or reconcile agent id"
    )
    used_corpus_query: bool = Field(
        description="Whether the cell used the fedcourts corpus-query CLI (query/open-events/etc.)"
    )
    tools_used: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Tools/abilities the agent reports using this run (e.g. fedcourts query, MCP)",
    )
    helpful: list[str] = Field(
        default_factory=list, max_length=50, description="What materially helped, shortest first"
    )
    gaps: list[str] = Field(
        default_factory=list,
        max_length=50,
        description="Missing or wished-for tools/abilities that would have helped",
    )
    notes: str | None = Field(
        default=None, max_length=2000, description="Free-text remarks about the tooling, optional"
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


class WorkflowHealth(_Strict):
    """Recent-run health for one workflow, rolled up from the Actions run history."""

    workflow: str
    runs_considered: int = Field(ge=0, description="Runs in the window examined")
    successes: int = Field(ge=0, description="Completed runs that concluded `success`")
    failures: int = Field(
        ge=0, description="Completed runs that failed / timed out / were cancelled"
    )
    success_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="successes / completed runs, or null when none completed",
    )
    last_conclusion: str | None = Field(
        default=None, description="Conclusion of the most recent run (success, failure, …)"
    )
    last_run_at: str | None = Field(
        default=None, description="ISO-8601 start of the most recent run in the window"
    )
    median_seconds: int | None = Field(
        default=None, ge=0, description="Median completed-run duration, where derivable"
    )
    p95_seconds: int | None = Field(
        default=None, ge=0, description="95th-percentile completed-run duration"
    )


class BackfillCourt(_Strict):
    """Per-court backfill progress, projected from the seed cursor."""

    court: str
    offset: int = Field(ge=0, description="Cases loaded for this court")
    total: int | None = Field(default=None, ge=0, description="Cases in the snapshot, once known")
    percent: float | None = Field(
        default=None, ge=0.0, le=100.0, description="offset / total, or 100 when complete"
    )
    complete: bool = False


class BackfillProgress(_Strict):
    """Whole-backfill progress across the tracked courts."""

    snapshot: str | None = Field(default=None, description="Bulk snapshot id being loaded")
    courts_total: int = Field(ge=0, description="Tracked courts")
    courts_complete: int = Field(ge=0, description="Courts whose backfill is finished")
    cases_loaded: int = Field(ge=0, description="Total cases loaded so far (sum of offsets)")
    cases_total: int | None = Field(
        default=None,
        ge=0,
        description="Total cases to load, only when every court's total is known",
    )
    percent: float | None = Field(
        default=None, ge=0.0, le=100.0, description="Overall %, only when cases_total is known"
    )
    cases_per_day: float | None = Field(
        default=None,
        ge=0.0,
        description="Load rate since the previous snapshot, when one is available",
    )
    eta_date: str | None = Field(
        default=None,
        description="Projected completion date (ISO), when the rate and total are both known",
    )
    entries: list[BackfillCourt] = Field(default_factory=list)


class SpendSummary(_Strict):
    """Model spend rolled up from the recorded ``usage.json`` ledger."""

    runs: int = Field(ge=0, description="usage.json records aggregated")
    total_tokens: int = Field(ge=0, description="All token classes summed across runs")
    estimated_cost_usd: float = Field(ge=0.0, description="Sum of per-run estimated cost")
    mean_cost_usd_per_run: float = Field(ge=0.0, description="estimated_cost_usd / runs")


class CostEstimate(_Strict):
    """A rough monthly cost run-rate, derived without billing-API access.

    GitHub Actions cost is estimated from observed run durations x the per-minute
    rate; model cost is the cumulative recorded usage ledger; fixed monthly captures
    the infra not metered per run (CourtListener membership, S3). All figures are
    estimates against the rates in ``docs/budget.md`` — check the provider billing
    dashboards for ground truth.
    """

    window_days: float | None = Field(
        default=None, ge=0.0, description="Span of the runs used for the Actions estimate"
    )
    actions_minutes: float = Field(
        ge=0.0, description="Summed completed-run wall-clock, in minutes"
    )
    actions_cost_usd: float = Field(ge=0.0, description="actions_minutes x the per-minute rate")
    actions_monthly_usd: float | None = Field(
        default=None, ge=0.0, description="Actions cost projected to 30 days from the window"
    )
    model_cost_usd: float = Field(ge=0.0, description="Cumulative recorded model spend")
    fixed_monthly_usd: float = Field(ge=0.0, description="Configured fixed monthly infra cost")
    estimated_monthly_usd: float | None = Field(
        default=None, ge=0.0, description="actions_monthly + fixed_monthly, when derivable"
    )


class CorpusCheck(_Strict):
    """One named corpus-integrity or referential check and its result.

    ``checked`` is how many items the check examined (rows, snapshots, or ledger
    artifacts) and ``failures`` how many violated the invariant; ``problems`` is a
    bounded sample of the specific violations (the full count is ``failures``, so a
    truncated sample never hides that there were more). ``detail`` is a one-line
    human summary, e.g. the row count compared against the baseline.
    """

    name: str = Field(description="Stable check identifier, e.g. `ledger_references_exist`")
    passed: bool
    checked: int = Field(default=0, ge=0, description="Items this check examined")
    failures: int = Field(default=0, ge=0, description="Items that violated the invariant")
    detail: str = Field(default="", description="One-line human summary of the result")
    problems: list[str] = Field(
        default_factory=list, description="Bounded sample of specific violations (capped)"
    )


class CorpusValidation(_Strict):
    """``validate-corpus`` verdict: corpus integrity + cross-store referential checks.

    The producer half of data validation: a deterministic correctness verdict over
    the packed corpus and the git ledger under ``data/`` — the complement to
    ``validate``, which only checks each ledger artifact against its schema. ``ok``
    is the conjunction of every check; ``skipped`` is set (with ``ok`` true and no
    checks) when the corpus is absent, so the command is safe to call before a
    ``dvc pull``. A pure function of its inputs — corpus, ledger, seed cursor, the
    supplied baseline, and the as-of date — so it carries no timestamp and the same
    inputs always serialize identically. Surfaced (and escalated) by a separate
    wiring layer, not committed; a failed verdict is loud-not-fatal by contract.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    ok: bool = Field(description="True when every check passed (or the corpus was absent)")
    skipped: bool = Field(
        default=False, description="True when no corpus was present; no checks were run"
    )
    corpus_rows: int = Field(default=0, ge=0, description="Case rows in the corpus")
    corpus_events: int = Field(default=0, ge=0, description="Predictable-event rows in the corpus")
    checks: list[CorpusCheck] = Field(default_factory=list)


class ScopeExclusion(_Strict):
    """One exclusion predicate's footprint among the corpus's open events."""

    reason: str = Field(description="The exclusion reason, e.g. 'stale unresolvable … (#333)'")
    cases: int = Field(default=0, ge=0, description="Distinct cases matched")
    open_events: int = Field(default=0, ge=0, description="Open (unresolved) events on those cases")
    recoverable: int = Field(
        default=0,
        ge=0,
        description="Of those open events, how many sit on a case carrying an opinion / "
        "citation / decision-date signal — a hint the disposition may be recoverable "
        "(an ingestion gap) rather than genuinely absent",
    )
    sample_cases: list[str] = Field(
        default_factory=list, description="A bounded sample of matched case ids, for triage"
    )


class CorpusScopeAudit(_Strict):
    """``corpus-scope-audit`` verdict: open events the predict scope excludes (issue #343).

    A read-only census of the corpus's still-**open** events whose case an exclusion
    predicate drops at the matrix gate (pre-1925 mandatory jurisdiction #309, stale
    unresolvable old SCOTUS petitions #333). These sit open in the corpus forever
    because nothing resolves them, so they are the candidates for the seed-side
    corpus reconcile (resolve if recoverable, else latch out of scope). The
    ``recoverable`` split is what tells those two paths apart. ``skipped`` is set
    (with empty exclusions) when the corpus is absent, so it is safe before a
    ``dvc pull``. A pure function of the corpus, so it carries no timestamp.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    skipped: bool = Field(
        default=False, description="True when no corpus was present; nothing was audited"
    )
    corpus_rows: int = Field(default=0, ge=0, description="Case rows in the corpus")
    scotus_open_events: int = Field(
        default=0,
        ge=0,
        description="Total open (unresolved) SCOTUS events — the audit's denominator",
    )
    exclusions: list[ScopeExclusion] = Field(
        default_factory=list, description="One entry per exclusion predicate that matched"
    )


class LedgerValidation(_Strict):
    """``validate`` result over the git ledger under ``data/`` — schema conformance only.

    The git-only, corpus-free half of data health: every artifact under ``data/``
    parsed and validated against its schema model. ``run-ops`` runs this on its
    schedule (no corpus needed), catching anything that reached the default branch
    without the local gate, plus model/data bit-rot over time. ``problems`` is a
    bounded sample of the specific failures; the true total is ``invalid``.
    """

    ok: bool = Field(description="True when every checked artifact validated")
    checked: int = Field(default=0, ge=0, description="Artifacts examined")
    invalid: int = Field(default=0, ge=0, description="Artifacts that failed schema validation")
    problems: list[str] = Field(
        default_factory=list, description="Bounded sample of validation failures (capped)"
    )


class DataHealth(_Strict):
    """The data-validation verdict surfaced on the ops dashboard: ledger + corpus.

    Pairs the two complementary checks the dashboard presents — the git-only
    ``validate`` over ``data/`` (:class:`LedgerValidation`) and the corpus-dependent
    ``validate-corpus`` verdict (:class:`CorpusValidation`, produced where the corpus
    is already pulled and read back from the ``ops-metrics`` branch). Either half may
    be absent (the corpus verdict before the first producer run); ``ok`` is the
    conjunction of whichever halves are present, so a missing half never reads as a
    pass that did not happen.
    """

    ok: bool = Field(description="True when every present half passed")
    ledger: LedgerValidation | None = Field(
        default=None, description="Schema conformance over data/ (git-only)"
    )
    corpus: CorpusValidation | None = Field(
        default=None, description="Latest corpus-integrity + referential verdict"
    )


class FlagsDigest(_Strict):
    """Open agent flags scanned from the committed ``flags.json`` files under ``data/``.

    A read-only roll-up the run-ops dashboard presents so agent-surfaced feedback is
    visible alongside the other operational analytics — not only in the run PR that
    produced it. The severity counts are over *every* committed flag; ``recent`` keeps
    the most recent flag-raising cells (newest first, capped), so a long history never
    bloats the dashboard while the counts still report the true volume.
    """

    total: int = Field(ge=0, description="Individual flags across all committed flags.json")
    cells: int = Field(ge=0, description="Cells (flags.json files) that raised at least one flag")
    blockers: int = Field(ge=0, description="Flags at blocker severity")
    warnings: int = Field(ge=0, description="Flags at warning severity")
    infos: int = Field(ge=0, description="Flags at info severity")
    recent: list[AgentFlags] = Field(
        default_factory=list, description="Most recent flag-raising cells, newest first (capped)"
    )


class ToolingCount(_Strict):
    """One free-text tooling item with how many reports mentioned it."""

    label: str = Field(min_length=1, description="The helpful ability or wished-for gap, verbatim")
    count: int = Field(ge=1, description="Reports that mentioned it")


class ToolingDigest(_Strict):
    """Agent tooling self-reports (`tooling.json`) rolled up for the run-ops dashboard.

    A read-only roll-up of the committed :class:`AgentToolingFeedback` records so a
    maintainer can see, across runs, whether the corpus tooling earns its keep:
    ``corpus_query_uses`` of ``reports`` cells used the query CLI, and ``helpful`` /
    ``gaps`` are the most-mentioned abilities and missing tools (most common first,
    capped). ``recent`` keeps the latest few full reports for detail; like
    :class:`FlagsDigest` the aggregate counts always cover every committed report.
    """

    reports: int = Field(ge=0, description="Committed tooling.json reports scanned")
    corpus_query_uses: int = Field(ge=0, description="Reports that used the corpus-query CLI")
    helpful: list[ToolingCount] = Field(
        default_factory=list, description="Most-mentioned helpful abilities, most common first"
    )
    gaps: list[ToolingCount] = Field(
        default_factory=list,
        description="Most-mentioned missing/wished-for tools, most common first",
    )
    recent: list[AgentToolingFeedback] = Field(
        default_factory=list, description="Most recent full reports, newest first (capped)"
    )


class OpsReport(_Strict):
    """``metrics/ops.json`` — an operational snapshot: health, backfill, spend, cost.

    A read-only roll-up of authoritative sources (the Actions run history, the seed
    cursor, the usage ledger), so no pipeline run writes an ops record. Unlike the
    deterministic leaderboard / back-test roll-ups this is a **point-in-time** view —
    it carries ``generated_at`` and run durations, so it is not byte-stable and is
    surfaced via the run-ops dashboard issue (and persisted to the ``ops-metrics``
    branch) rather than committed to the default branch.

    ``data_health`` carries the data-validation verdict the dashboard also presents —
    null until the wiring supplies it, kept separate from the run-health analytics
    above. ``flags`` is the open-agent-flags digest scanned from ``data/`` and
    ``tooling`` the agent tooling-feedback digest scanned the same way; both are null
    on a report built before the field existed (so an older snapshot read back as
    ``previous`` still validates).
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    generated_at: str = Field(description="ISO-8601 UTC time the report was built")
    health: list[WorkflowHealth] = Field(default_factory=list)
    backfill: BackfillProgress
    spend: SpendSummary
    cost: CostEstimate
    data_health: DataHealth | None = Field(
        default=None, description="Data-validation verdict (schema + corpus), when available"
    )
    flags: FlagsDigest | None = Field(
        default=None, description="Open agent flags scanned from committed flags.json under data/"
    )
    tooling: ToolingDigest | None = Field(
        default=None, description="Agent tooling self-reports scanned from tooling.json under data/"
    )


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
        default=None,
        description="Bulk snapshot id currently being loaded, e.g. `2026-03-31` (an "
        "auto-resolved file date) or `2026-Q2` (a manually pinned quarter)",
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
    "ops.json": OpsReport,
    "flags.json": AgentFlags,
    "tooling.json": AgentToolingFeedback,
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
    "ops_report": OpsReport,
    "corpus_validation": CorpusValidation,
    "corpus_scope_audit": CorpusScopeAudit,
    "agent_flags": AgentFlags,
    "agent_tooling": AgentToolingFeedback,
}
