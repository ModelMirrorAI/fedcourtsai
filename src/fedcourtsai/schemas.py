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
    """The realized-outcome vocabulary, with the mapping conventions for
    non-standard SCOTUS forms. A **grant/vacate/remand** is its own label,
    ``gvr`` — including the Munsingwear vacatur, whose mootness basis is *also*
    carried by ``Outcome.disposition_basis`` (``gvr`` + ``mootness`` = a
    Munsingwear vacatur, segmented into the procedural stratum; ``gvr`` +
    ``standard`` = a merits GVR). ``gvr`` counts as a grant on the **binary axis**
    (it joins the granted set for ``actual_granted``), so ``probability`` /
    Brier stay comparable across the label's introduction; only the
    disposition-label axis distinguishes it. The label is a **forward-convention**
    change: historical GVRs recorded as ``granted`` before it existed keep that
    label except the identifiable Munsingwear ones (``granted`` + ``mootness``),
    which a one-time backfill relabels; a plain-``granted`` merits GVR in history
    is an accepted residual (indistinguishable post-hoc without re-resolving the
    source, and immaterial on the binary axis). On mandatory-jurisdiction direct
    appeals the resolver latches only the vacatur-remand form (now ``gvr``); the
    other direct-appeal forms (probable jurisdiction noted, summary affirmance,
    dismissal for want of a substantial federal question) are deliberate resolver
    misses that reach maintainer triage, where the convention is: grant-side for
    probable jurisdiction, the denied/dismissed side for summary affirmance and
    want-of-a-question.
    """

    granted = "granted"
    denied = "denied"
    granted_in_part = "granted-in-part"
    gvr = "gvr"
    dismissed = "dismissed"
    withdrawn = "withdrawn"
    other = "other"


class EventKind(StrEnum):
    motion = "motion"
    petition = "petition"
    appeal = "appeal"
    order = "order"


class GroupBy(StrEnum):
    """A dimension the ``stats`` aggregation buckets base-rates by.

    ``judge`` is multi-valued — a case with a three-judge panel lands in each
    judge's bucket — so grouped case counts can exceed the ungrouped total; every
    other dimension is single-valued. ``term_year`` reads the October-Term year
    from a modern SCOTUS docket number (:func:`fedcourtsai.corpus.scotus_term_year`).
    ``originating_court`` groups by the lower court a docket came from (the
    circuit-scorecard cut for SCOTUS petitions); rows without the linkage share
    one ``(none)`` bucket, so coverage is visible rather than silently dropped.
    ``era`` buckets by decade (:func:`fedcourtsai.corpus.case_era` — Term year,
    else filing/decision date), so historical cases base-rate against their own
    period; rows with no date signal share one ``(none)`` bucket. The three
    cert-signal dimensions read the live-parsed columns: ``relist_bucket``
    groups by relists (`distribution_count` - 1, floored at 0) into 0 / 1 / 2 /
    3+ buckets, ``cvsg`` by whether the Court called for the views of the
    Solicitor General, and ``fee_class`` by the docket serial's numbering
    stream (paid / IFP); rows the live channel never parsed share one
    ``(unknown)`` bucket on the first two, so parse coverage stays visible.
    """

    court = "court"
    topic = "topic"
    judge = "judge"
    term_year = "term_year"
    disposition = "disposition"
    originating_court = "originating_court"
    era = "era"
    relist_bucket = "relist_bucket"
    cvsg = "cvsg"
    fee_class = "fee_class"


class UsageRole(StrEnum):
    """Which agentic stage a usage record belongs to."""

    predictor = "predictor"
    evaluator = "evaluator"


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
    model: str | None = Field(
        default=None,
        description="Model that produced this prediction (e.g. claude-fable-5); "
        "null only for offline outputs that called no model",
    )
    run_id: str
    created_at: datetime
    input_snapshot: str = Field(description="Repo-relative path to the snapshot used as input")
    granted: int = Field(ge=0, le=1, description="Binary outcome prediction, 1=granted")
    probability: float = Field(ge=0.0, le=1.0, description="P(granted)")
    predicted_disposition: Disposition
    votes: list[JudgeVote] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    big_case_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Pre-registered opinion of the case's stakes / significance / "
        "newsworthiness — *significance if decided*, decoupled from grant likelihood "
        "(a case can be denied yet high-stakes, or granted yet narrow). 0-1; judged "
        "later by an independent evaluator's agreement, never against a ground truth. "
        "Optional (defaults None) so records written before the field existed still "
        "validate. See docs/salience.md.",
    )
    big_case_rationale: str | None = Field(
        default=None,
        max_length=500,
        description="Optional one-line rationale for `big_case_score`; null if none",
    )
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
    disposition_basis: Literal["standard", "mootness"] = Field(
        default="standard",
        description="What drove the disposition's wording: 'mootness' when the "
        "order is mootness practice (a Munsingwear vacatur, a dismissal as "
        "moot) — the label then tracks vacatur practice rather than "
        "cert-worthiness, so scoring segments the cell into the leaderboard's "
        "procedural stratum instead of the headline strata",
    )


class LeakageAssessment(_Strict):
    """The cross-evaluator's leakage grading of one prediction (advisory, never a gate).

    The grading half of the leakage doctrine: rather than preventing retrieval,
    the evaluator assesses whether a **replay** predictor retrieved and used
    outcome-revealing material, reading the harness-captured
    ``retrieval_log.json`` (tool calls, query slices, retrieved-document dates)
    beside the predictor's own reasoning. A **forward** prediction was made
    before the outcome existed, so it grades ``not_applicable``. Contamination
    here taints iteration signal — backtest results are never claimable
    performance either way — so the assessment segments scores; it never
    changes them.
    """

    mode: str = Field(
        description="The prediction's mode as its retrieval_log.json recorded it: "
        "forward | replay | unknown (no log — assess from reasoning alone)"
    )
    retrieved_outcome_material: bool | None = Field(
        default=None,
        description="Whether the retrieval log/reasoning shows outcome-revealing "
        "material about this case was retrieved (post-event-date documents, the "
        "disposing order, queries for the result). Null when not assessable.",
    )
    influenced_prediction: Literal["not_applicable", "none", "possible", "likely"] = Field(
        description="Whether retrieved outcome material plausibly shaped the "
        "prediction. not_applicable for a forward prediction."
    )
    notes: str | None = Field(
        default=None, max_length=2000, description="The concrete evidence, briefly"
    )


class BigCaseAssessment(_Strict):
    """The evaluator's independent read of a case's stakes (the big-case dimension).

    The evaluator forms its **own** opinion of how big / significant the case is,
    **before** it is shown the predictor's ``big_case_score`` — so, under
    cross-evaluation, the panel's reads stay independent and the agreement is not
    circular. Unlike the blind grant forecast, this is a *judge's* read: the
    evaluator may use post-decision context available at evaluation time (the
    outcome, the immediate reaction). The predictor's pre-registered score is
    graded by its agreement with this read — **rank-agreement across the evaluated
    cohort** at leaderboard time, since bigness is comparative (a per-case
    absolute delta is a secondary diagnostic); this record stores only the
    independent read, never the grade. Optional on the evaluation so records
    written before the dimension existed still validate. See ``docs/salience.md``.
    """

    evaluator_score: float = Field(
        ge=0.0,
        le=1.0,
        description="The evaluator's own 0-1 stakes / significance read, formed "
        "before seeing the predictor's big_case_score",
    )
    notes: str | None = Field(
        default=None, max_length=2000, description="The basis for the read, briefly"
    )


class Evaluation(_Strict):
    """``evaluation.json`` — one evaluator scoring one predictor's prediction."""

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    event_id: str
    predictor_id: str
    evaluator_id: str
    engine: Engine
    model: str | None = Field(
        default=None,
        description="Model that produced this evaluation (e.g. claude-fable-5); "
        "null only for offline outputs that called no model (and records "
        "written before the field existed)",
    )
    run_id: str
    created_at: datetime
    correct: int = Field(ge=0, le=1, description="1 if disposition matched outcome")
    brier_score: float | None = Field(default=None, ge=0.0, le=1.0)
    vote_accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    reasoning_quality: float | None = Field(default=None, ge=0.0, le=1.0)
    leakage_suspected: bool | None = Field(
        default=None,
        description="Coarse leakage bit, kept in step with `leakage`: true when "
        "`leakage.influenced_prediction` is possible/likely. Advisory: it segments "
        "scores, never changes them. Null when not assessed (offline evaluators "
        "and records written before the field existed)",
    )
    leakage: LeakageAssessment | None = Field(
        default=None,
        description="The structured leakage grading over the prediction's "
        "harness-captured retrieval log (see LeakageAssessment). Advisory and "
        "cross-only, like the rest of evaluation; null on records written before "
        "the field existed and on offline evaluator outputs",
    )
    big_case: BigCaseAssessment | None = Field(
        default=None,
        description="The evaluator's independent big-case read (see "
        "BigCaseAssessment); null when not assessed and on records written before "
        "the dimension existed. The predictor's big_case_score is graded against "
        "these reads by rank-agreement at leaderboard time.",
    )
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
    pipeline_sha: str | None = Field(
        default=None,
        description="Git commit of the pipeline checkout that ran this cell "
        "(GITHUB_SHA in CI, the local HEAD otherwise) — pins the prompt "
        "templates, harness, and registry in force at run time. Null on "
        "records written before the field existed or when unresolvable.",
    )
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

    A predict/evaluate cell writes this *only when it has something to
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
    actor_id: str = Field(description="The predictor_id (predict) or evaluator_id (evaluate)")
    flags: list[AgentFlag] = Field(
        min_length=1, description="The notes; write the file only when there is at least one"
    )


class AgentToolingFeedback(_Strict):
    """``tooling.json`` — a cell's self-report on the agent tooling it was given.

    Unlike :class:`AgentFlags` (exception-based — written only on a problem with the
    *data or task*), every predict/evaluate cell is *invited* to write this
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
    actor_id: str = Field(description="The predictor_id (predict) or evaluator_id (evaluate)")
    used_corpus_query: bool = Field(
        description="Whether the cell used the fedcourts corpus-query CLI (query/open-events/etc.)"
    )
    used_base_rates: bool = Field(
        default=False,
        description="Whether the cell used corpus base-rate context — the committed "
        "statpack roll-up, or `fedcourts stats` where a local corpus is present. "
        "Optional (defaults False) so reports written before the tool existed still validate.",
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
    tool_manifest: list[str] | None = Field(
        default=None,
        max_length=20,
        description="The MCP server ids the cell was configured with, echoed from the "
        "provisioned manifest. Advisory (the agent's echo); the authoritative "
        "pinned manifest is recorded harness-side in retrieval_log.json.",
    )


class RetrievalCall(_Strict):
    """One tool invocation harvested from the engine's own transcript.

    Captured by the harness from the engine log — never the agent's word — so
    the evaluator's leakage grading can see what a cell actually
    retrieved. Long parameters and results are digested, not stored: the log
    is an audit trail, not a content mirror.
    """

    tool: str = Field(
        description="Tool name as the engine logged it, e.g. mcp__courtlistener__search"
    )
    query: str | None = Field(
        default=None,
        max_length=2000,
        description="The human-legible query/params slice (truncated), where extractable",
    )
    params_digest: str | None = Field(
        default=None, description="SHA-256 (hex, 16 chars) of the full serialized params"
    )
    timestamp: str | None = Field(
        default=None, description="Engine-logged wall-clock time of the call, verbatim"
    )
    result_digest: str | None = Field(
        default=None, description="SHA-256 (hex, 16 chars) of the logged result payload"
    )
    retrieved_doc_date: str | None = Field(
        default=None,
        description="A document/decision date parsed from the result, where one is legible "
        "— the leakage grading's timing signal",
    )


class RetrievalLog(_Strict):
    """``retrieval_log.json`` — the cell's tool-call transcript, harness-captured.

    Rides to the collect job with the cell's output exactly as ``usage.json``
    does. Under the leakage doctrine, timing is the control: replay cells run
    with the same tools as forward cells, and this log (plus the cross-evaluator's
    leakage grading over it) replaces walls. ``mcp_servers`` snapshots the pinned tool
    manifest the cell was configured with — the pipeline-attribution record.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    run_id: str
    role: UsageRole = Field(description="Which stage produced the log")
    actor_id: str = Field(description="The predictor/evaluator id whose cell this was")
    engine: Engine
    mode: str | None = Field(
        default=None,
        description="The cell's provisioned mode: forward | replay; None on records "
        "written before the mode field existed",
    )
    mcp_servers: list[str] = Field(
        default_factory=list,
        description="Pinned manifest entries the cell was configured with (id==version strings)",
    )
    calls: list[RetrievalCall] = Field(
        default_factory=list,
        max_length=500,
        description="Tool invocations in transcript order (500 caps a runaway cell)",
    )


class LeaderboardStratum(_Strict):
    """Aggregates over one stratum of a predictor's evaluations.

    A cell is *forward* when the event was still unresolved at the prediction's
    commit time and *retrospective* when it had already resolved — in which case
    the outcome is public knowledge inside every modern model's training data, so
    the cell measures recall plus calibration, never ex-ante forecasting skill.
    The strata are therefore aggregated separately and never blended into one
    headline number.
    """

    events_scored: int = Field(ge=0, description="Distinct (case, event) pairs scored")
    evaluations: int = Field(ge=0, description="Evaluations counted in this stratum")
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


class BigCaseLeaderboard(_Strict):
    """A predictor's big-case-score agreement with the independent evaluator panel.

    A *second* skill dimension, orthogonal to the grant/deny ranking (a model can
    read a case's significance well while calling grant/deny only modestly, or the
    reverse). Bigness is comparative, so the agreement is a **rank** correlation —
    Kendall's tau-b between the predictor's ``big_case_score`` ordering and the
    panel's (the mean of the evaluators' independent reads per event), across the
    scored events both sides rated (one per case in the current single-event
    model). Never enters the leaderboard ranking; reported alongside it.
    """

    rank_agreement: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Kendall's tau-b between the predictor's big_case_score ordering "
        "and the evaluator panel's read ordering, across the cases both scored "
        "(+1 = same order, -1 = reversed); null with fewer than 2 comparable cases "
        "or when every pair ties on one side",
    )
    cases: int = Field(
        default=0,
        ge=0,
        description="Cases with both a predictor big_case_score and at least one "
        "evaluator big-case read",
    )


class LeaderboardEntry(_Strict):
    """One predictor's standings, aggregated per stratum.

    Forward and retrospective are the pre-registration (timing) strata; the
    procedural block segments mootness-basis cells out of both.
    """

    predictor_id: str
    rank: int = Field(ge=1, description="1-based standing; 1 is best")
    evaluators: int = Field(ge=0, description="Distinct evaluators that scored this predictor")
    forward: LeaderboardStratum | None = Field(
        default=None,
        description="True forward forecasts — the event was unresolved when the "
        "prediction was committed. The only stratum that measures forecasting "
        "skill; null until this predictor has a scored forward cell.",
    )
    retrospective: LeaderboardStratum | None = Field(
        default=None,
        description="Events already resolved when the prediction was committed: "
        "measures calibration and label-mapping fit, not forecasting skill; "
        "null when this predictor has no scored retrospective cell.",
    )
    procedural: LeaderboardStratum | None = Field(
        default=None,
        description="Cells whose outcome was mootness practice (the outcome's "
        "disposition_basis) — the label tracks vacatur practice rather than "
        "cert-worthiness, so these aggregate separately and never enter the "
        "ranking; null when this predictor has none.",
    )
    big_case: BigCaseLeaderboard | None = Field(
        default=None,
        description="The predictor's big-case-score rank-agreement with the "
        "evaluator panel (see BigCaseLeaderboard); a second, orthogonal skill "
        "dimension that never affects the ranking. Null when no case carries both "
        "a predictor big_case_score and an evaluator read.",
    )


class Leaderboard(_Strict):
    """``metrics/leaderboard.json`` — predictors ranked from the evaluations ledger.

    A deterministic, offline roll-up of every ``evaluation.json`` under ``data/``:
    one entry per predictor, ranked best-first on the **forward** stratum (see
    :class:`LeaderboardStratum` — the strata are never blended into one number,
    and ``evaluations_total`` includes the procedural cells the ranking
    excludes). Computed by ``fedcourts leaderboard``; carries no
    timestamp so the same ledger always serializes identically.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    predictors_ranked: int = Field(
        ge=0,
        description="Number of predictors on the board (a procedural-only "
        "predictor still appears, sorted after every ranked one)",
    )
    evaluations_total: int = Field(ge=0, description="Total evaluations aggregated")
    procedural_evaluations: int = Field(
        default=0,
        ge=0,
        description="Evaluations segmented out for a mootness-basis outcome (never ranked)",
    )
    forward_evaluations: int = Field(
        default=0, ge=0, description="Evaluations of true forward forecasts"
    )
    retrospective_evaluations: int = Field(
        default=0, ge=0, description="Evaluations of retrospective (leakage-suspect) cells"
    )
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
    stratum: Literal["retrospective"] = Field(
        default="retrospective",
        description="Every replayed event resolved before any modern model's "
        "training cutoff, so the back-test is retrospective by construction: it "
        "measures recall, calibration, and label-mapping fit over known history, "
        "never ex-ante forecasting skill. Forward skill can only come from the "
        "live ledger's forward stratum (see Leaderboard).",
    )
    predictors_evaluated: int = Field(ge=0, description="Number of predictors on the board")
    events_scored: int = Field(ge=0, description="Size of the resolved-event back-test set")
    entries: list[BacktestEntry] = Field(default_factory=list)


class CalibrationBin(_Strict):
    """One probability bin of a calibration view: predicted vs observed grant rate."""

    lower: float = Field(ge=0.0, le=1.0, description="Bin lower bound on P(granted), inclusive")
    upper: float = Field(
        ge=0.0, le=1.0, description="Bin upper bound on P(granted); inclusive for the top bin"
    )
    predictions: int = Field(ge=0, description="Predictions whose P(granted) fell in this bin")
    mean_probability: float = Field(
        ge=0.0, le=1.0, description="Mean predicted P(granted) within the bin"
    )
    observed_granted_rate: float = Field(
        ge=0.0, le=1.0, description="Realized grant rate among the bin's cases"
    )


class CertBacktestEntry(_Strict):
    """One predictor's standings over the cert back-test set."""

    predictor_id: str
    rank: int = Field(ge=1, description="1-based standing; 1 is best")
    events_scored: int = Field(ge=0, description="Decided cert petitions replayed")
    accuracy: float = Field(
        ge=0.0, le=1.0, description="Fraction whose predicted disposition matched the known label"
    )
    granted_accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="Fraction whose binary granted/denied projection matched the outcome",
    )
    mean_brier_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Mean Brier score of P(granted) vs the realized outcome (lower is better)",
    )
    lift_over_always_denied: float = Field(
        ge=-1.0,
        le=1.0,
        description="Disposition accuracy minus the always-deny floor's — the honest "
        "signal under cert's structural denial skew, where raw accuracy is cheap",
    )
    calibration: list[CalibrationBin] = Field(
        default_factory=list,
        description="P(granted) decile bins: predicted probability vs observed grant rate",
    )


class CertBacktest(_Strict):
    """``metrics/cert-backtest.json`` — predictors replayed over decided cert petitions.

    The standing instrument for vetting cert predictors and prompt changes:
    replay over a curated set of resolved modern discretionary-cert petitions
    (outcome hidden — the replay provisions a redacted snapshot), scored against
    the realized grant/deny. Produced by the maintainer-triggered
    ``run-backtest`` workflow via ``fedcourts cert-backtest``
    (it spends tokens when agentic engines are replayed), never by a schedule.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    stratum: Literal["retrospective"] = Field(
        default="retrospective",
        description="Every replayed petition resolved before any modern model's "
        "training cutoff, so this measures recall, calibration, and label-mapping "
        "fit over known history, never ex-ante forecasting skill (the same "
        "pre-registration rule the leaderboard stratifies on).",
    )
    events_scored: int = Field(ge=0, description="Size of the cert back-test set")
    predictors_evaluated: int = Field(ge=0, description="Number of predictors on the board")
    always_denied_accuracy: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="The always-deny floor's disposition accuracy over this set "
        "(the denial base rate every lift figure is measured against)",
    )
    entries: list[CertBacktestEntry] = Field(default_factory=list)


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
        description="successes / conclusive completed runs (success + failure family; "
        "label-filter skips excluded), or null when none concluded",
    )
    last_conclusion: str | None = Field(
        default=None,
        description="Conclusion of the most recent real execution (completed "
        "label-filter skips ignored when any real execution exists — an "
        "all-skip window reads as skipped; an in-progress run reads as null)",
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
    corpus pull. A pure function of its inputs — corpus, ledger, the
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

    reason: str = Field(description="The exclusion reason, e.g. 'stale unresolvable …'")
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


class ScopeUnclassified(_Strict):
    """Why an open SCOTUS event the scope did *not* exclude stays in scope (refinement signal).

    The refinement surface: buckets the open events no predicate caught by the reason
    each is still in scope — a recent/current Term (legitimately pending), a docket
    Term the parser cannot read (a format the predicate skips → a broadening
    candidate), a recorded disposition the event-state missed, or no docket number.
    """

    reason: str = Field(description="Why this open event was not excluded")
    open_events: int = Field(default=0, ge=0)
    sample_cases: list[str] = Field(default_factory=list)


class ScopeDocketShape(_Strict):
    """A docket-number *shape* and how many unparseable open events carry it.

    The shape masks digits→``9`` and letters→``A``/``a`` (punctuation/space kept), so
    ``01-7700`` → ``99-9999`` and ``22O141`` → ``99A999`` — every uppercase letter
    masks to ``A``, so a shape names a format class, not a specific docket letter.
    It tells us, concretely, which docket formats drive the "Term not parseable"
    bucket — i.e. exactly what the Term parser would need to handle to bring those
    events into scope. A shape carrying fewer than ~100 open events is an accepted
    fragment: it stays visible here by design, and no exclusion predicate is added
    for it.
    """

    shape: str = Field(description="Digit/letter-masked docket-number shape")
    count: int = Field(default=0, ge=0, description="Unparseable open events with this shape")


class CorpusScopeAudit(_Strict):
    """``corpus-scope-audit`` verdict: open events the predict scope excludes.

    A read-only census of the corpus's still-**open** events whose case an exclusion
    predicate drops at the matrix gate (pre-1925 mandatory jurisdiction, stale
    unresolvable old SCOTUS petitions). These sit open in the corpus forever
    because nothing resolves them, so they are the candidates for the corpus-side
    corpus reconcile (resolve if recoverable, else latch out of scope). The
    ``recoverable`` split is what tells those two paths apart. ``skipped`` is set
    (with empty exclusions) when the corpus is absent, so it is safe before a
    corpus pull. A pure function of the corpus, so it carries no timestamp.
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
    unclassified: list[ScopeUnclassified] = Field(
        default_factory=list,
        description="Open SCOTUS events no predicate excluded, bucketed by why",
    )
    unparseable_docket_shapes: list[ScopeDocketShape] = Field(
        default_factory=list,
        description="Top docket-number shapes in the 'Term not parseable' bucket — the "
        "concrete formats a parser broadening would target; shapes under ~100 "
        "open events are accepted fragments, left visible here by design with no "
        "predicate chased for them",
    )


class ScopeManifestEntry(_Strict):
    """The published prediction-scope decision for one already-public case.

    One row per docket that has a committed directory under ``data/cases`` *and*
    a corpus row — a subset of the git-visible public set (a public docket absent
    from the corpus is omitted), and never anything outside it. The fields mirror
    the corpus's
    scope columns for the case: whether it is in the prediction gate
    (``predict_eligible`` ≡ court is SCOTUS), whether the reconcile has latched it
    out (``predict_excluded``), the shared exclusion reason when it has, the
    inclusion weight the sampling channel asserted, and the salience gate's score /
    version / selection latch. ``sample_weight`` is null when no channel asserted
    one; ``out_of_scope_reason`` is null for an in-scope case; the salience fields
    are null / False until a salience pass has scored the row.
    """

    case_id: str = Field(description="``<court>/<docket>`` of an already-public case")
    predict_eligible: bool = Field(description="In the prediction gate (court is SCOTUS)")
    predict_excluded: bool = Field(description="Latched out of scope by the reconcile")
    out_of_scope_reason: str | None = Field(
        default=None, description="Shared exclusion reason when excluded; null when in scope"
    )
    sample_weight: int | None = Field(
        default=None,
        description="Inverse inclusion probability the sampling channel asserted; null if none",
    )
    salience_score: float | None = Field(
        default=None,
        description="The deterministic salience score; null when no salience pass has scored it",
    )
    salience_version: str | None = Field(
        default=None,
        description="The salience-function version that produced the score (e.g. sal-v1); "
        "null when unscored",
    )
    salience_selected: bool = Field(
        default=False,
        description="Whether the salience gate selected this petition into the fundable "
        "tournament slice (meaningful only when salience_version is set)",
    )


class ScopeManifest(_Strict):
    """``data/scope/scope.json`` — the published prediction-scope decision, public set only.

    A deterministic, offline census of the prediction-scope decision (eligible /
    excluded / reason / sample weight) for every docket **already public** under
    ``data/cases`` — enumerated from that committed directory tree alone, never
    from the corpus. So it publishes the scope call for the cases the repository
    already discloses, and by construction cannot enumerate the broader ingested
    corpus (a compilation-extent boundary held deliberately). ``skipped`` is set
    (with empty entries) when the corpus is absent, so it is safe to regenerate
    before a corpus pull. A pure function of the committed tree + corpus, so it
    carries no timestamp and reruns reproduce it byte for byte.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    skipped: bool = Field(
        default=False, description="True when no corpus was present; scope was not resolved"
    )
    cases: int = Field(default=0, ge=0, description="Public cases in the manifest")
    eligible: int = Field(default=0, ge=0, description="Of those, in the prediction gate")
    excluded: int = Field(default=0, ge=0, description="Of those, latched out of scope")
    entries: list[ScopeManifestEntry] = Field(
        default_factory=list,
        description="One entry per included public case (present in the corpus), in case_id order",
    )


class DispositionShare(_Strict):
    """One realized outcome's count and share of the resolved cases in a slice.

    ``share`` is ``count / resolved`` — the base rate for that disposition among the
    *decided* cases in the bucket (open cases carry no label, so they are excluded
    from the denominator). A bucket with no resolved cases carries no shares.
    """

    disposition: Disposition
    count: int = Field(ge=0, description="Resolved cases carrying this disposition")
    share: float = Field(
        ge=0.0, le=1.0, description="count / resolved — the base rate among decided cases"
    )


class BaseRateBucket(_Strict):
    """Disposition base-rates over one slice of the corpus (the whole set, or a group).

    Used both for the overall filtered set (``key`` empty) and for each value of the
    ``group_by`` dimension. ``cases`` counts every matched case in the slice,
    ``resolved`` those carrying a realized disposition, and ``open`` the remainder;
    ``dispositions`` is the base-rate breakdown over the resolved subset, most common
    first (ties broken by disposition for a deterministic order).
    """

    key: str = Field(default="", description="The group value (court id, topic, …); empty overall")
    cases: int = Field(default=0, ge=0, description="Matched cases in this slice")
    resolved: int = Field(default=0, ge=0, description="Matched cases carrying a disposition")
    open: int = Field(default=0, ge=0, description="Matched cases still unresolved")
    dispositions: list[DispositionShare] = Field(
        default_factory=list, description="Base-rate breakdown over the resolved cases"
    )


class AnalyticsReport(_Strict):
    """``fedcourts stats`` verdict: aggregate disposition base-rates over the corpus.

    A read-only roll-up of the corpus rows matching a structured query into base-rates
    — the aggregate counterpart of the per-case priors ``fedcourts query`` returns. A
    pure function of the corpus (no clock, no network), so it carries no timestamp and
    reruns over an unchanged corpus reproduce it byte for byte. ``total`` is the base
    rate over the whole matched set; when a ``group_by`` dimension is given, ``buckets``
    breaks it down per group value (most cases first). ``skipped`` is set (with an empty
    ``total``) when the corpus is absent, so it is safe to call before a corpus pull.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    skipped: bool = Field(
        default=False, description="True when no corpus was present; nothing was aggregated"
    )
    group_by: GroupBy | None = Field(
        default=None, description="The dimension buckets break down by; None for the total only"
    )
    total: BaseRateBucket = Field(
        default_factory=BaseRateBucket, description="Base rate over the whole matched set"
    )
    buckets: list[BaseRateBucket] = Field(
        default_factory=list, description="Per-group base-rate breakdown, most cases first"
    )


class StatPackSection(_Strict):
    """One named base-rate breakdown in the statpack: a dimension and its buckets.

    ``court`` records the court filter the section was computed under (``None`` = all
    courts), so the artifact is self-describing — e.g. a SCOTUS-only Term breakdown vs
    an all-courts view. ``buckets`` is the per-group base-rate breakdown, most cases
    first (the same shape ``fedcourts stats --group-by`` produces).
    """

    title: str = Field(description="Human title of the breakdown, e.g. 'Cases by court'")
    court: str | None = Field(default=None, description="Court filter applied; None = all courts")
    cert_stage: bool = Field(
        default=False,
        description="True when the section is restricted to modern Term-prefixed "
        "discretionary-cert dockets (the population the cert model predicts), so "
        "its base rates are not diluted by historical merits-era labels",
    )
    live_slice: bool = Field(
        default=False,
        description="True when the section is computed over the live/historical "
        "provenance slice only (rows the supremecourt.gov channel wrote, whose "
        "dispositions come from parsed proceedings) rather than the whole corpus "
        "with its frozen bulk import",
    )
    weighted: bool = Field(
        default=False,
        description="True when the section's counts are sample-weighted estimates "
        "(each row counted `sample_weight` times, so the historical walker's "
        "denial sampling does not bias the base rates); raw ingested counts "
        "otherwise",
    )
    group_by: GroupBy = Field(description="The dimension the buckets break down by")
    buckets: list[BaseRateBucket] = Field(default_factory=list)


class TimingStats(_Strict):
    """Duration stats over the resolved cases carrying a usable date pair.

    The pack-level timing keys on ``date_filed`` → ``date_decided``; the per-Term
    statistics key on the cert-stage resolution date and weight each row by its
    ``sample_weight`` (each use states which). Rows missing either date are
    excluded rather than guessed, so ``cases`` doubles as the coverage
    denominator — a raw count in unweighted uses, the weighted estimate in
    weighted ones. Percentiles use the deterministic nearest-rank method, so the
    same corpus reproduces the same stats.
    """

    cases: int = Field(default=0, ge=0, description="Resolved cases with a usable date pair")
    mean_days: float | None = Field(default=None, ge=0.0, description="Mean days filed→decided")
    median_days: float | None = Field(default=None, ge=0.0, description="Nearest-rank median")
    p90_days: float | None = Field(default=None, ge=0.0, description="Nearest-rank 90th pctile")


class FeeClass(StrEnum):
    """A SCOTUS docket's fee class, read from its serial's numbering stream.

    Paid petitions number from 1, in-forma-pauperis petitions from 5001 — the
    two streams the live channel's discovery walks — so the class is exact from
    the docket number alone. The paid/IFP split is the coarsest predictive cut
    there is (IFP petitions are overwhelmingly pro se and granted at a far
    lower rate), so per-Term statistics carry one entry per class.
    """

    paid = "paid"
    ifp = "ifp"


class StatPackTermClass(_Strict):
    """One (Term, fee class) slice of the live-slice cert population.

    ``filings`` is the cursor-derived census — the count of docketed serials
    through the walked frontier, exact even for petitions the denial sample
    never ingested (a slight upper bound: withheld serial numbers still count).
    ``ingested``/``resolved`` are raw live-slice row counts; the estimates
    (``weighted_resolved``, ``est_grant_rate``, ``dispositions``) count each row
    ``sample_weight`` times so the walker's denial sampling does not bias them.
    """

    fee_class: FeeClass
    filings: int | None = Field(
        default=None,
        ge=0,
        description="Census of docketed serials for this Term x class from the "
        "discovery cursors; None when no walker has probed the stream",
    )
    complete: bool = Field(
        default=False,
        description="True when the stream's frontier was observed at its current "
        "cursor (`frontier_serial = last_serial`) — the walk covered every serial. "
        "False = partial: rates reflect the walked prefix only",
    )
    ingested: int = Field(default=0, ge=0, description="Live-slice rows present")
    resolved: int = Field(
        default=0, ge=0, description="Live-slice rows carrying a disposition (raw count)"
    )
    weighted_resolved: int = Field(
        default=0,
        ge=0,
        description="Sample-weighted resolved estimate — each row counted "
        "`sample_weight` times (an unweighted-capture row counts once)",
    )
    est_grant_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Weighted grant-family share (granted + gvr) of resolved; "
        "None when nothing resolved",
    )
    dispositions: list[DispositionShare] = Field(
        default_factory=list,
        description="Weighted disposition estimates over the resolved rows",
    )
    timing: TimingStats = Field(
        default_factory=TimingStats,
        description="Filing → cert-stage resolution timing (weighted nearest-rank), "
        "keyed on the petition-stage decision date, not docket termination",
    )


class StatPackTerm(_Strict):
    """One SCOTUS October Term's slice of the statpack: the live-slice cert population.

    The per-Term detail published stat packs devote one document per Term to; here
    every Term is an entry in a single artifact (recent first), so the statpack stays
    one deterministic committed metric with reviewable diffs and a single-Term view is a
    filter (``fedcourts stats --court scotus --term N``) rather than a separate file.
    Aggregates are computed over the live/historical provenance slice (weighted, so
    the denial sampling does not bias them); a Term known only from the discovery
    cursors still appears, carrying its census with zero ingested rows. **This is
    the replay self-selection surface**: a time-masked cell anchors only on Term
    entries strictly preceding its ``DECIDED_BEFORE`` clock.
    """

    term: int = Field(description="The October-Term year, e.g. 2024")
    ingested: int = Field(
        default=0,
        ge=0,
        description="Live-slice rows present for this Term — the raw ingested count, "
        "as opposed to the weighted estimates in `base_rates`",
    )
    base_rates: BaseRateBucket = Field(
        description="This Term's live-slice counts and weighted base rates"
    )
    timing: TimingStats = Field(
        default_factory=TimingStats,
        description="Filing → cert-stage resolution timing over this Term's live-slice "
        "resolved cases (weighted nearest-rank)",
    )
    classes: list[StatPackTermClass] = Field(
        default_factory=list,
        description="Per-fee-class detail (paid, then ifp): census, completeness, "
        "and weighted estimates",
    )
    grants: int = Field(
        default=0, ge=0, description="Cert grants observed in the live slice this Term"
    )
    median_days_to_grant: float | None = Field(
        default=None,
        ge=0.0,
        description="Nearest-rank median days filing → cert grant over this Term's "
        "granted petitions; None when none carry both dates",
    )


class StatPackCoverage(_Strict):
    """The statpack's own denominators: how much trustworthy data backs it.

    Published so the artifact states its own coverage instead of implying the
    headline corpus counts (dominated by the frozen bulk import) back the
    predictor-facing sections. ``census_filings`` totals the cursor-derived
    per-Term censuses, so live-slice ingestion can be read against the true
    filing volume.
    """

    live_slice_rows: int = Field(
        default=0, ge=0, description="Rows the live/historical channel has written"
    )
    live_slice_resolved: int = Field(
        default=0, ge=0, description="Live-slice rows carrying a disposition (raw count)"
    )
    census_filings: int | None = Field(
        default=None,
        ge=0,
        description="Total docketed filings across every Term x class census the "
        "discovery cursors cover; None before any walker has probed",
    )


class StatPack(_Strict):
    """``metrics/statpack.json`` — a corpus base-rate statpack (an independent artifact).

    A deterministic, offline roll-up of the corpus into headline counts plus a curated
    set of base-rate breakdowns (:class:`StatPackSection`) — the project's analogue of a
    published court "statpack". A pure function of the corpus (no clock, no network), so
    reruns over an unchanged corpus reproduce it byte for byte; git-tracked as a
    metric alongside ``leaderboard.json`` / ``backtest.json``. Starts empty (zero counts,
    no sections) until a corpus is present — mirroring the other metrics artifacts, an
    absent corpus yields the empty pack rather than an error.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    corpus_rows: int = Field(default=0, ge=0, description="Case rows in the corpus")
    resolved: int = Field(default=0, ge=0, description="Cases carrying a realized disposition")
    open: int = Field(default=0, ge=0, description="Cases still unresolved")
    machine_readable_resolved: int = Field(
        default=0,
        ge=0,
        description="Resolved cases with a machine-readable disposition — the back-testable slice",
    )
    dated_resolved: int = Field(
        default=0,
        ge=0,
        description="Machine-readable resolved cases carrying a resolution date — the "
        "share the time-masked replay clock can anchor",
    )
    overall: BaseRateBucket = Field(
        default_factory=BaseRateBucket, description="Base rate over the whole corpus"
    )
    timing: TimingStats = Field(
        default_factory=TimingStats,
        description="Filing → decision timing over every resolved case with both dates",
    )
    coverage: StatPackCoverage = Field(
        default_factory=StatPackCoverage,
        description="The pack's own denominators: live-slice rows/resolved and the "
        "cursor-derived filings census backing the predictor-facing sections",
    )
    sections: list[StatPackSection] = Field(
        default_factory=list, description="Curated base-rate breakdowns"
    )
    terms: list[StatPackTerm] = Field(
        default_factory=list,
        description="Per-SCOTUS-Term live-slice detail (weighted base rates, timing, "
        "per-fee-class census), most recent Term first",
    )


class ScopeReconcileResult(_Strict):
    """``reconcile-scope`` result: what the corpus scope reconcile changed.

    The write counterpart of :class:`CorpusScopeAudit`: it sets the ``predict_excluded``
    latch on cases an exclusion predicate now matches and clears it on cases that have
    returned to scope. ``applied`` is False on a dry run (counts only, no write).
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    applied: bool = Field(default=False, description="False on a dry run (no corpus write)")
    skipped: bool = Field(default=False, description="True when no corpus was present")
    eligible_cases: int = Field(default=0, ge=0, description="SCOTUS dockets weighed")
    excluded: int = Field(default=0, ge=0, description="Cases newly latched out of scope")
    released: int = Field(
        default=0, ge=0, description="Cases whose latch was cleared (back in scope)"
    )
    normalized: int = Field(
        default=0,
        ge=0,
        description="Rows whose derived scope columns were converged to the court "
        "predicate (hygiene, not a scope decision); 0 on a dry run",
    )
    sample_excluded: list[str] = Field(default_factory=list)
    sample_released: list[str] = Field(default_factory=list)


class SalienceSelectionResult(_Strict):
    """``reconcile-salience-selection`` result: what the salience pass scored and picked.

    The salience gate's write pass (see ``docs/salience.md``): it scores every
    in-scope cert petition with the frozen salience function and latches
    ``salience_selected`` on the per-conference top-N slice plus the always-include
    carve-outs. The latch is one-way, so ``newly_selected`` counts only cases the
    run added — never any it removed. ``applied`` is False on a dry run.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    applied: bool = Field(default=False, description="False on a dry run (no corpus write)")
    version: str = Field(
        default="", description="The salience-function version applied, e.g. sal-v1"
    )
    eligible_cases: int = Field(
        default=0, ge=0, description="In-scope SCOTUS cert petitions weighed"
    )
    scored: int = Field(default=0, ge=0, description="Cases given a salience score this run")
    conferences: int = Field(
        default=0, ge=0, description="Distinct conference cohorts the cap was applied within"
    )
    newly_selected: int = Field(
        default=0,
        ge=0,
        description="Cases newly latched selected (the one-way latch never removes)",
    )
    sample_selected: list[str] = Field(default_factory=list)


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


class LeakageDigest(_Strict):
    """The evaluators' leakage grading rolled up for the run-ops dashboard.

    The visibility half of the backtest-as-iteration doctrine: replay cells run
    with the same tools as forward cells, so the dashboard must show — across
    runs — whether outcome material is contaminating the backtest's iteration
    signal. Counts are over committed ``evaluation.json`` files carrying a
    ``leakage`` block within ``window_days`` of generation; ``likely`` offenders
    are listed (capped) so a repeat pattern names its predictor.
    """

    assessed: int = Field(ge=0, description="Evaluations carrying a leakage assessment")
    not_applicable: int = Field(ge=0, description="Forward predictions (leakage cannot apply)")
    none: int = Field(ge=0, description="Replay cells graded clean")
    possible: int = Field(ge=0, description="Replay cells where influence is possible")
    likely: int = Field(ge=0, description="Replay cells where influence is likely")
    flagged: list[str] = Field(
        default_factory=list,
        description="`case_id event_id predictor (by evaluator)` for each `likely` "
        "grading, newest first (capped)",
    )
    window_days: int = Field(
        default=0, ge=0, description="Recency window (days) the counts cover; 0 = all-time"
    )


class FlagsDigest(_Strict):
    """Open agent flags scanned from the committed ``flags.json`` files under ``data/``.

    A read-only roll-up the run-ops dashboard presents so agent-surfaced feedback is
    visible alongside the other operational analytics — not only in the run PR that
    produced it. The severity counts and ``recent`` cover only flags from runs within
    ``window_days`` of generation, so long-since-fixed flags stop dominating the
    summary; ``archived`` reports how many older flags remain in the committed
    ``flags.json`` ledger (and the agent-feedback issue), which keep everything.
    """

    total: int = Field(ge=0, description="Individual flags across all committed flags.json")
    cells: int = Field(ge=0, description="Cells (flags.json files) that raised at least one flag")
    blockers: int = Field(ge=0, description="Flags at blocker severity")
    warnings: int = Field(ge=0, description="Flags at warning severity")
    infos: int = Field(ge=0, description="Flags at info severity")
    recent: list[AgentFlags] = Field(
        default_factory=list, description="Most recent flag-raising cells, newest first (capped)"
    )
    window_days: int = Field(
        default=0, ge=0, description="Recency window (days) the counts cover; 0 = all-time"
    )
    archived: int = Field(
        default=0,
        ge=0,
        description="Flags older than the window, still kept in the flags.json ledger "
        "and the agent-feedback issue",
    )


class ToolingCount(_Strict):
    """One free-text tooling item with how many reports mentioned it."""

    label: str = Field(min_length=1, description="The helpful ability or wished-for gap, verbatim")
    count: int = Field(ge=1, description="Reports that mentioned it")


class ToolingDigest(_Strict):
    """Agent tooling self-reports (`tooling.json`) rolled up for the run-ops dashboard.

    A read-only roll-up of the committed :class:`AgentToolingFeedback` records so a
    maintainer can see, across runs, whether the corpus tooling earns its keep:
    ``corpus_query_uses`` / ``base_rate_uses`` of ``reports`` cells used the query and
    base-rate ``stats`` CLIs, and ``helpful`` /
    ``gaps`` are the most-mentioned abilities and missing tools (most common first,
    capped). ``recent`` keeps the latest few full reports for detail; like
    :class:`FlagsDigest` the counts cover only reports within ``window_days`` of
    generation, so the signal tracks current tooling rather than the whole history.
    """

    reports: int = Field(ge=0, description="Committed tooling.json reports scanned")
    corpus_query_uses: int = Field(ge=0, description="Reports that used the corpus-query CLI")
    base_rate_uses: int = Field(
        default=0, ge=0, description="Reports that used the base-rate `stats` CLI"
    )
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
    window_days: int = Field(
        default=0, ge=0, description="Recency window (days) the counts cover; 0 = all-time"
    )


class OpenTriggerIssue(_Strict):
    """One still-open ``run:*`` trigger issue, surfaced on the ops dashboard.

    Trigger issues (predict / evaluate fan-outs) are transient by
    design: the run's ready PR closes them on merge, and an empty matrix closes
    them with a note. One that stays open means its run stalled — failed
    wholesale, produced nothing, or was never picked up — so the dashboard lists
    them with their age instead of letting them sit invisible.
    """

    number: int = Field(ge=1, description="The issue number")
    label: str = Field(description="The run:* trigger label, e.g. run:predict")
    title: str = ""
    created_at: str = Field(description="ISO-8601 creation time (age derives from this)")


class SubstanceCells(_Strict):
    """Scored-cell counts across the pipeline funnel, forward vs replay.

    The funnel: prediction cells committed → events with at least one prediction
    → predicted events whose ground truth landed → evaluations, counted per
    timing stratum (the leaderboard's forward/retrospective doctrine — never
    blended; a procedural mootness-basis cell counts in neither, mirroring its
    segmentation out of the skill aggregates). ``*_delta`` fields carry the
    change against the prior ops-metrics snapshot when a comparable one was
    supplied, else null.
    """

    predictions: int = Field(ge=0, description="prediction.json cells committed under data/")
    events_predicted: int = Field(ge=0, description="Distinct events with >= 1 prediction")
    predicted_resolved: int = Field(
        ge=0, description="Predicted events whose outcome.json has landed"
    )
    evaluations_forward: int = Field(ge=0, description="Scored cells in the forward stratum")
    evaluations_retrospective: int = Field(
        ge=0, description="Scored cells in the retrospective (replay) stratum"
    )
    predictions_delta: int | None = Field(
        default=None, description="Change vs the prior snapshot, when comparable"
    )
    predicted_resolved_delta: int | None = None
    evaluations_forward_delta: int | None = None
    evaluations_retrospective_delta: int | None = None


class SubstanceCalibration(_Strict):
    """Calibration on the scored replay sample, anchored to the deny base rate.

    Replay (retrospective) cells only — the iteration-signal stratum. ``sample``
    is printed beside every number so a small-N figure cannot masquerade as
    signal. ``lift_over_always_deny`` is replay accuracy minus the modern-cert
    denial base rate (the accuracy an always-deny predictor would score); null
    until both halves exist.
    """

    sample: int = Field(ge=0, description="Scored replay evaluations")
    mean_brier: float | None = Field(default=None, ge=0.0, le=1.0)
    accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    deny_base_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Denied share of resolved modern discretionary-cert petitions "
        "(from the committed statpack's live-slice, denial-reweighted section), "
        "when present",
    )
    base_rate_cases: int | None = Field(
        default=None,
        ge=0,
        description="Estimated resolved petitions behind the base rate (weighted)",
    )
    lift_over_always_deny: float | None = Field(
        default=None, description="accuracy - deny_base_rate; null until both exist"
    )


class PredictorScoreRow(_Strict):
    """One predictor's evaluation-score distribution (the at-a-glance view).

    ``median`` / ``p25`` / ``p75`` summarize the cross-evaluator
    ``reasoning_quality`` grades; ``accuracy`` is the share of correct calls.
    All strata pooled — the leaderboard remains the stratified reference.
    """

    predictor_id: str
    evaluations: int = Field(ge=0)
    accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    median: float | None = Field(default=None, ge=0.0, le=1.0)
    p25: float | None = Field(default=None, ge=0.0, le=1.0)
    p75: float | None = Field(default=None, ge=0.0, le=1.0)


class ConferenceBucket(_Strict):
    """One conference date's slice of the live cert watchlist."""

    conference: date
    petitions: int = Field(ge=0)


class LiveFrontier(_Strict):
    """``live-frontier.json`` — the live cert watchlist's readiness snapshot.

    Produced where the corpus is already pulled (``fedcourts live-frontier``,
    published by the corpus-writer path like the validation verdict) and
    rendered corpus-free by ``run-ops``: watchlist size, the distribution
    calendar, and how many watchlist petitions carry provisioned filed-document
    text. ``next_conference`` is relative to the supplied as-of date.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    skipped: bool = Field(
        default=False, description="True when no corpus was present; nothing was read"
    )
    generated_on: date | None = Field(default=None, description="As-of date supplied by the caller")
    watchlist: int = Field(
        ge=0, default=0, description="Pending petitions distributed for a conference"
    )
    next_conference: date | None = Field(
        default=None, description="Earliest conference on/after the as-of date, when any"
    )
    next_conference_petitions: int | None = Field(default=None, ge=0)
    conferences: list[ConferenceBucket] = Field(default_factory=list)
    documents_provisioned: int = Field(
        ge=0, default=0, description="Watchlist petitions with >= 1 stored filed document"
    )


class SubstanceDigest(_Strict):
    """The dashboard's substantive-results section: is the machine producing?

    Complements run-health (is the machine running): scored-cell counts by
    stratum, replay calibration vs the deny base rate, per-predictor score
    distributions, and live-frontier readiness. Every input is a committed or
    published artifact, keeping run-ops a read-only presenter.
    """

    cells: SubstanceCells
    calibration: SubstanceCalibration
    predictor_scores: list[PredictorScoreRow] = Field(default_factory=list)
    live_frontier: LiveFrontier | None = Field(
        default=None, description="Published watchlist readiness, when available"
    )


class OpsReport(_Strict):
    """``metrics/ops.json`` — an operational snapshot: health, substance, spend, cost.

    A read-only roll-up of authoritative sources (the Actions run history, the
    usage ledger), so no pipeline run writes an ops record. Unlike the
    deterministic leaderboard / back-test roll-ups this is a **point-in-time** view —
    it carries ``generated_at`` and run durations, so it is not byte-stable and is
    surfaced via the run-ops dashboard issue (and persisted to the ``ops-metrics``
    branch) rather than committed to the default branch.

    ``data_health`` carries the data-validation verdict the dashboard also presents —
    null until the wiring supplies it, kept separate from the run-health analytics
    above. ``flags`` is the open-agent-flags digest scanned from ``data/`` and
    ``tooling`` the agent tooling-feedback digest scanned the same way; both are null
    on a report built before the field existed (so an older snapshot read back as
    a prior still validates). ``substance`` is the substantive-results section —
    null on older snapshots the same way.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    generated_at: str = Field(description="ISO-8601 UTC time the report was built")
    health: list[WorkflowHealth] = Field(default_factory=list)
    spend: SpendSummary
    cost: CostEstimate
    substance: SubstanceDigest | None = Field(
        default=None,
        description="Substantive results (scored cells, calibration, readiness); "
        "null on a report built before the field existed",
    )
    data_health: DataHealth | None = Field(
        default=None, description="Data-validation verdict (schema + corpus), when available"
    )
    flags: FlagsDigest | None = Field(
        default=None, description="Open agent flags scanned from committed flags.json under data/"
    )
    leakage: LeakageDigest | None = Field(
        default=None,
        description="The evaluators' leakage grading rolled up across committed "
        "evaluation.json files; null on a report built before the field existed",
    )
    tooling: ToolingDigest | None = Field(
        default=None, description="Agent tooling self-reports scanned from tooling.json under data/"
    )
    open_triggers: list[OpenTriggerIssue] | None = Field(
        default=None,
        description="Still-open run:* trigger issues (stalled fan-outs), oldest first; "
        "null on a report built before the field existed or without the issue feed",
    )


# A registry model override must be a bare model id: it is interpolated into the
# whitespace-split `claude_args` of the engine step, so rejecting whitespace (and
# anything else outside a model id's alphabet) here makes argument smuggling via a
# config edit structurally impossible and catches a typo at plan time.
_MODEL_ID_PATTERN = r"^[A-Za-z0-9._:-]+$"


class McpServerConfig(_Strict):
    """One MCP server in the tool manifest (``mcp_servers:`` in the registry).

    The manifest is the pipeline-attribution record once cells' retrieval
    varies: it pins exactly which retrieval tooling a cell was configured with
    (echoed into each cell's ``retrieval_log.json``), and is frozen before the
    September prediction freeze. Local-install stdio only — the hosted
    endpoint's OAuth flow does not fit headless CI.
    """

    id: str = Field(description="Manifest key, e.g. `courtlistener`")
    package: str = Field(
        description="Pinned installable, e.g. `courtlistener-api-client[mcp]==1.0.0` — "
        "launched via `uvx --from <package> <command>` so no separate install step runs"
    )
    command: str = Field(description="The stdio server entrypoint, e.g. `courtlistener-mcp`")
    token_env: str | None = Field(
        default=None,
        description="Environment variable carrying the server's API token. Unset/empty "
        "at runtime degrades to anonymous rate limits rather than failing the cell.",
    )
    description: str | None = None


class PredictorConfig(_Strict):
    """An entry in ``config/predictors.yaml``."""

    id: str
    engine: Engine
    model: str | None = Field(default=None, pattern=_MODEL_ID_PATTERN)
    prompt: str = Field(description="Repo-relative path to the prompt template")
    enabled: bool = True
    description: str | None = None
    mcp_servers: list[str] = Field(
        default_factory=list,
        description="Manifest ids (see `mcp_servers:` in the same file) this predictor's "
        "cells are configured with. Explicit per predictor — attribution, not a default.",
    )


class EvaluatorConfig(_Strict):
    """An entry in ``config/evaluators.yaml``."""

    id: str
    engine: Engine
    model: str | None = Field(default=None, pattern=_MODEL_ID_PATTERN)
    prompt: str
    enabled: bool = True
    description: str | None = None
    mcp_servers: list[str] = Field(
        default_factory=list,
        description="Manifest ids this evaluator's cells are configured with.",
    )


# Maps on-disk filename -> the model that validates it. Used by `fedcourts validate`.
FILENAME_MODELS: dict[str, type[_Strict]] = {
    "case.yaml": TrackedCase,
    "event.yaml": PredictableEvent,
    "prediction.json": Prediction,
    "outcome.json": Outcome,
    "evaluation.json": Evaluation,
    "leaderboard.json": Leaderboard,
    "backtest.json": Backtest,
    "usage.json": ModelUsage,
    "ops.json": OpsReport,
    "flags.json": AgentFlags,
    "tooling.json": AgentToolingFeedback,
    "retrieval_log.json": RetrievalLog,
    "scope.json": ScopeManifest,
}

EXPORTABLE_MODELS: dict[str, type[BaseModel]] = {
    "case": TrackedCase,
    "event": PredictableEvent,
    "prediction": Prediction,
    "outcome": Outcome,
    "evaluation": Evaluation,
    "predictor_config": PredictorConfig,
    "evaluator_config": EvaluatorConfig,
    "leaderboard": Leaderboard,
    "backtest": Backtest,
    "cert_backtest": CertBacktest,
    "usage": ModelUsage,
    "ops_report": OpsReport,
    "corpus_validation": CorpusValidation,
    "corpus_scope_audit": CorpusScopeAudit,
    "scope_manifest": ScopeManifest,
    "live_frontier": LiveFrontier,
    "analytics_report": AnalyticsReport,
    "statpack": StatPack,
    "agent_flags": AgentFlags,
    "agent_tooling": AgentToolingFeedback,
    "mcp_server_config": McpServerConfig,
    "retrieval_log": RetrievalLog,
}
