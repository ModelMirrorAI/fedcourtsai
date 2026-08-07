"""Pydantic models defining the on-disk data contract for the pipeline.

Every artifact written under ``data/cases/`` validates against one of these
models. They are the single source of truth for the data shape and are also
exported to JSON Schema (see ``fedcourts export-schemas``) so that coding
agents and Codex ``--output-schema`` can target them directly.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Final, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    model_serializer,
    model_validator,
)

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
    summary_reversal = "summary-reversal"
    dismissed = "dismissed"
    withdrawn = "withdrawn"
    other = "other"


#: Dispositions that count as a granted (1) binary outcome — the single source
#: for every granted-side membership test (`actual_granted`, the live rotation's
#: granted-docket retention). A partial grant still granted relief, a GVR grants
#: the petition (it is a grant/vacate/remand), and a summary reversal is the
#: Court granting review and deciding the merits in one order — all land on the
#: granted side of the binary target, which keeps `actual_granted` and the Brier
#: score comparable across each label's introduction.
GRANTED_DISPOSITIONS: frozenset[Disposition] = frozenset(
    {
        Disposition.granted,
        Disposition.granted_in_part,
        Disposition.gvr,
        Disposition.summary_reversal,
    }
)

#: The **grant family** the statpack's published ``est_grant*rate`` figures
#: count: :data:`GRANTED_DISPOSITIONS` less ``granted-in-part``, which keeps its
#: own bucket so the published rate preserves its pre-``gvr`` definition. The
#: two membership tests are therefore *not* interchangeable, and anything that
#: reconstructs a published grant count from a published rate — the
#: leave-one-out in ``pipeline.evaluate.realized_band_rate`` — has to subtract a
#: case on exactly the terms the numerator counted it, not on the binary
#: scoring target.
GRANT_FAMILY_DISPOSITIONS: frozenset[Disposition] = GRANTED_DISPOSITIONS - {
    Disposition.granted_in_part
}

#: The granted dispositions that open a **merits proceeding** — the subset of
#: :data:`GRANTED_DISPOSITIONS` that is followed by briefing, argument, and a
#: separate judgment. A GVR is a grant/vacate/remand whose vacatur rides in the
#: same order that grants, and a summary reversal decides the merits in the
#: cert order itself, so neither leaves a merits decision to forecast or to
#: observe. One definition for every merits-population question: which grants
#: mint the open merits event, which rows the judgment backfill parses, and
#: which rows the statpack's merits section describes — so the population that
#: is predicted is the population the base rate is measured over.
MERITS_PROCEEDING_DISPOSITIONS: frozenset[Disposition] = frozenset(
    {Disposition.granted, Disposition.granted_in_part}
)


#: The Court's composition and the quorum it can act with — 28 U.S.C. § 1. The
#: only statutory numbers in the decision model; every vote threshold is Court
#: practice instead (``pipeline.aggregation``).
SEATS = 9
QUORUM = 6


class VoteValue(StrEnum):
    """How one Justice voted. Distinct from :class:`Disposition`, which is what the
    *Court* did — a vocabulary with no member for joining a majority or dissenting,
    and so unable to express a vote at all.

    Spans every stage, because the model does: ``grant``/``deny`` are the cert and
    interim vocabulary, the rest are merits. A vote that does not exist is not a
    vote — ``recused`` and ``did_not_participate`` are recorded so the aggregation
    denominator is legible, since a threshold counts *participating* Justices.
    """

    grant = "grant"
    deny = "deny"
    majority = "majority"
    concur_in_judgment = "concur-in-judgment"
    concur_in_part = "concur-in-part-dissent-in-part"
    dissent = "dissent"
    recused = "recused"
    did_not_participate = "did-not-participate"


class WritingRole(StrEnum):
    """What a Justice wrote, if anything.

    ``none`` is a real observation, not a gap: once an order list or an opinion is
    final, every participating Justice is observed either to have written or not
    to have. A record that simply does not address writing leaves the field null
    instead, so silence is never read as an observed absence.

    That asymmetry is what makes "does Justice j write here" forecastable where an
    individual cert *vote* is not — a cert vote becomes public only when a Justice
    chooses to note it, so the visible ones are selected on the outcome.

    ``statement`` covers a statement respecting the denial of certiorari, which is
    the commonest non-``none`` value at the cert stage.
    """

    none = "none"
    majority = "majority"
    plurality = "plurality"
    concurrence = "concurrence"
    concurrence_in_judgment = "concurrence-in-judgment"
    dissent = "dissent"
    statement = "statement"


class Judgment(StrEnum):
    """What the Court did to the judgment below — the **merits** axis.

    Deliberately not members of :class:`Disposition`. A dismissal as improvidently
    granted has no coherent value on the cert binary: certiorari *was* granted, and
    the merits event resolved to nothing. Forcing it onto that axis would corrupt
    the comparability anchor every grant-rate figure in this project rests on.

    On the merits **binary** — P(disturbed), the axis a merits cell's Brier is
    scored on — ``dig`` and ``equally_divided`` count as *undisturbed*, because
    both leave the judgment below standing (a DIG dissolves the writ, an
    equally divided Court affirms by operation of law). They stay in the scored
    pool rather than being routed out, because the pooled baseline's
    denominator (the statpack merits section's ``parsed``) includes them, and a
    scored population that dropped them would face a baseline computed over a
    different one. ``judgment_correct`` keeps them as their own labels, so the
    exact-match axis never confuses a DIG with an affirmance.
    """

    affirmed = "affirmed"
    reversed = "reversed"
    vacated = "vacated"
    affirmed_in_part = "affirmed-in-part-reversed-in-part"
    dig = "dismissed-as-improvidently-granted"
    equally_divided = "affirmed-by-an-equally-divided-court"


class EventKind(StrEnum):
    """The filing that *opened* an event — not what the event decides.

    Orthogonal to :class:`Stage` (the decision standard) and :class:`Moment`
    (when in the case's life the forecast was taken). Keeping the three apart is
    what lets one case carry several forecasts of one question: they share a
    stage, differ in moment, and each names the filing that made it forecastable.
    """

    motion = "motion"
    petition = "petition"
    appeal = "appeal"
    order = "order"
    brief = "brief"


class Stage(StrEnum):
    """Which decision standard governs an event — the parameter that selects an
    aggregation rule (:mod:`fedcourtsai.pipeline.aggregation`) and an observation
    mask (``docs/decision-model.md``).

    Orthogonal to :class:`EventKind`, which names the *filing that opened* an
    event. A merits decision is not a filing, so it is a stage rather than a
    kind. Stage is also the within-SCOTUS analogue of a caution
    ``metrics/README.md`` already carries across courts: ``granted`` denotes cert
    on a petition and relief on a stay application, and carrying the stage in the
    record says so where prose otherwise has to.

    Where an event declares no stage the rule lookup yields nothing rather than
    guessing — true of a circuit motion, which has no Supreme Court decision
    standard at all.
    """

    cert = "cert"
    interim = "interim"
    merits = "merits"


class Moment(StrEnum):
    """*When* in a case's life a forecast of its stage was taken.

    A stage asks one question — will cert be granted, will the application be
    granted, will the judgment below be disturbed — and the case passes several
    points at which that question can honestly be forecast, each with a
    different information set. A petition forecast the day it is first
    distributed and the same petition forecast after a CVSG are answering the
    same question from different evidence, so they are **two forecasts, not one
    forecast revised**: each freezes its own context and each is scored on its
    own.

    The consequence that makes this a vocabulary rather than a counter: two
    moments are two populations, and pooling them would publish a mean over a
    mixture of information sets. Aggregation therefore keys on
    ``(stage, moment)`` and never on stage alone — the same rule the salience
    version and the claim-set version already carry.

    Which moments exist, what each is minted from, and which claims each
    declares live in one table, :mod:`fedcourtsai.pipeline.moments`. Nothing
    reads a moment out of an event id.
    """

    #: cert — the petition is first distributed for conference.
    distribution = "distribution"
    #: cert — the Court calls for the Solicitor General's views.
    cvsg = "cvsg"
    #: interim — the application arrives on the docket.
    arrival = "arrival"
    #: interim — the Court (or a Circuit Justice) asks for a response.
    response_requested = "response-requested"
    #: interim — a response to the application is filed.
    response_filed = "response-filed"
    #: merits — the cert grant opens the proceeding.
    grant = "grant"
    #: merits — the respondent's brief on the merits is filed.
    briefed = "briefed"


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
    ``salience_band`` groups by the frozen ``sal-v1`` grant-likelihood band
    (high / elevated / baseline) over the paid modern-cert petitions — the
    predicted segment — so a case's base rate is its own salience tier's rate.
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
    salience_band = "salience_band"


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


class SemanticSupport(StrEnum):
    """How far the opinion supports one declared semantic claim — the ``semantic-v0`` grade.

    A small closed vocabulary on purpose: the grade is read by a human-or-model
    grader rather than resolved in code, so every level the vocabulary adds is a
    level graders can disagree on, and inter-grader agreement is the number this
    family is judged by. Contradiction folds into ``unsupported`` for that
    reason — separating "the opinion is silent on the point the claim makes" from
    "the opinion says the opposite" costs agreement to buy a distinction nothing
    scores today.

    Three of the four levels are **ordinal** (``unsupported`` <
    ``partial`` < ``supported``) and one is not: ``not_addressed`` is the
    **availability mask**, a property of the *record* and never of the
    predictor — the opinion body that would settle the claim does not exist, was
    never ingested, or says nothing on the claim's axis. It is reported and
    counted, never ranked and never scored, exactly as a masked mechanical claim
    is (``ClaimScore.outcome`` null).

    ``semantic-v0`` is **alpha** — provisional, unproven against opinion text,
    and explicitly not a pre-registered commitment in the sense ``cert-v1`` and
    ``merits-v1`` are. Nothing produces a grade today, so nothing published
    depends on this vocabulary; see ``docs/outcome-decomposition.md``, *The
    semantic family, alpha*.
    """

    supported = "supported"
    partial = "partially-supported"
    unsupported = "unsupported"
    not_addressed = "not-addressed"


# The pre-registration stratum a scored cell belongs to. Defined here, beside
# the models that carry it, so a field can be typed on the closed vocabulary
# rather than on a bare string; `fedcourtsai.leaderboard` re-exports it with the
# named constants and owns `classify_stratum`, the single definition of which
# cell lands where.
Stratum = Literal["forward", "retrospective", "procedural"]


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
    stage: Stage | None = Field(
        default=None,
        description="Which decision standard governs this event (cert / interim / "
        "merits) — see the Stage vocabulary. Null means no stage is recorded: "
        "either no Supreme Court decision standard applies (a circuit appeal), or "
        "the writer does not classify one for this event; consumers treat null as "
        "'no rule', never as a guess.",
    )
    moment: Moment | None = Field(
        default=None,
        description="Which forecast moment of the stage this event is (see the "
        "Moment vocabulary) — the point in the case's life the forecast was taken "
        "from, and therefore the information set it had. Null means unrecorded, "
        "in which case a consumer reads it as the stage's first moment; a stage "
        "carrying two events reads them as two populations and never pools them.",
    )
    title: str
    description: str | None = None
    docket_entry_id: int | None = None
    opened_at: date | None = None
    decision_target: str = "disposition"
    resolved: bool = False


class JusticeVote(_Strict):
    """One Justice's vote, and whether they wrote.

    The vote is a :class:`VoteValue`, not a :class:`Disposition`: a disposition is
    what the *Court* did, and has no member for joining a majority or dissenting.
    """

    justice: str = Field(description="The Justice's name, as the vote source spells it")
    vote: VoteValue
    writing: WritingRole | None = Field(
        default=None,
        description="What this Justice wrote. Null means not stated — the record "
        "was written without addressing writing at all. `none` is the opposite: an "
        "affirmative observation that this Justice wrote nothing, which is what a "
        "final order list or opinion discloses about every participating Justice. "
        "Defaulting to `none` would turn every silent record into that claim",
    )


class VoteProvenance(_Strict):
    """Where a vote list came from, and how much of it is there.

    **Presence carries meaning**, the discipline ``ResolutionSignals`` established.
    Absent, nobody looked. Present with ``complete=false`` and two votes beside it,
    exactly two are on the public record and the other seven genuinely are not —
    which is the ordinary state at the cert stage, where a vote surfaces only when
    a Justice notes it. Collapse that distinction and no import can restore it,
    and no evaluator can tell an unobserved vote from an unrecorded one.

    Scoped to the Supreme Court: the bounds below are its nine seats and its
    six-Justice quorum, so this does not describe a circuit panel, which has
    neither. Circuit events carry no vote record.

    It sits beside the votes rather than containing them: ``votes`` is a committed
    field on every outcome and these models reject unknown keys, so a block that
    swallowed the list would fail every artifact already written.
    """

    source: str = Field(
        description="Where the votes were read from, e.g. 'scdb:2024-001', "
        "'order-list:2025-03-10', 'opinion'. Free text, because the sources are "
        "not yet an enumerable set"
    )
    participating: int = Field(
        ge=QUORUM,
        le=SEATS,
        description="Justices who took part — the aggregation denominator a "
        "threshold counts against, which recusals move",
    )
    complete: bool = Field(
        description="Whether every participating Justice's vote is present. False "
        "means the rest are unobserved, NOT that they abstained"
    )


class ProcessVersion(_Strict):
    """Harness-written stamp of the process that produced a prediction/evaluation.

    Hybrid identity. ``digest`` is a content hash of the *actual* process inputs
    — the prompt-template bytes plus the resolved configuration for this actor
    (engine, resolved model, pinned MCP manifest, and the engine's retrieval
    surface) — so a silent prompt or config change is automatically a distinct
    version. ``label`` is human-readable sugar
    for a digest. The frozen/shakedown partition keys on ``digest``, never the
    label, so two different processes cannot hide behind one label.

    ``pipeline_sha`` is provenance only and is deliberately **not** folded into
    ``digest``: the checkout commit changes on every unrelated pipeline edit, and
    folding it in would break the frozen set every time predict/evaluate resume at
    a newer HEAD. The digest captures what defines the process; the sha records
    which commit ran it.

    Optional on the ledger models (defaults to absent), so shakedown cells written
    before the stamp existed still validate. The agent never writes this — a
    post-agent harness step (``fedcourts stamp-cell``) does, so a cell's version
    is the harness's word, not the agent's, exactly like ``usage.json``.
    """

    label: str = Field(description="Human process label, e.g. 'proc-v1'")
    digest: str = Field(description="Content digest of the process inputs, 'sha256:<hex>'")
    algo: Literal["sha256"] = "sha256"
    pipeline_sha: str | None = Field(
        default=None,
        description="Git commit of the pipeline checkout that stamped this cell; "
        "provenance only, NOT part of `digest`.",
    )
    stamped_at: datetime = Field(description="When the harness stamped the cell (UTC)")


class PredictionContext(_Strict):
    """The conditioning state a predict cell actually ran against.

    **Harness-owned.** Written by ``provision-snapshot`` and copied onto the
    prediction by ``stamp-cell``, exactly like ``process_version`` and
    ``usage.json`` — never the agent's word. That matters here more than
    elsewhere: ``input_snapshot`` is the agent's own string and is written four
    different ways across the committed set, with some cells naming no path at
    all, so it cannot carry a scoring input.

    It exists because the salience band moves. ``distribution_count`` is
    max-latched and a ``cvsg_date``, once set, stays set, so a petition's band
    only ever strengthens — and a band re-derived at evaluation is the band the
    petition *ended* at, not the one the cell faced. Scoring against that
    conditions a forecast's baseline on its own future. Freezing the band here is
    what lets the evaluator read the risk-set rate
    (``StatPackTermSegment.prefix_est_grant_rate``), which is the rate a petition
    at this band actually faces.

    Derived from the **provisioned snapshot payload**, not from the corpus row.
    The row holds current values; the payload is what the cell could read, which
    is the thing a baseline has to be conditioned on. It also makes the record
    reproducible — an auditor re-parses the dated snapshot and recovers the same
    band — and makes forward and replay cells identical by construction, since
    both go through the same derivation.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    mode: str = Field(description="The cell's mode: forward or replay")
    snapshot_date: date = Field(description="Date of the provisioned snapshot the cell read")
    snapshot_provenance: Literal["as-stored", "dated", "truncated", "blind"] = Field(
        default="as-stored",
        description="How the provisioned snapshot was obtained. 'as-stored' is the "
        "corpus payload unmodified, which is every forward cell. 'dated' is a "
        "snapshot the docket really served at or before the replay cutoff — the "
        "strongest point-in-time evidence, because it also reflects what had not "
        "yet been filed. 'truncated' is a later payload with its post-cutoff "
        "entries removed, which cannot know that a pre-cutoff entry was "
        "back-filled later. 'blind' is neither: no forward moment could be "
        "identified, so the proceedings were removed outright and the cell saw no "
        "trajectory at all. Recorded so the three can be separated; a figure "
        "pooling them is pooling three different information sets",
    )
    cutoff: date | None = Field(
        default=None,
        description="The instant this cell was placed at: entries filed strictly "
        "before it are what the snapshot carries. Null on a forward cell, whose "
        "snapshot is simply the latest. This is the date leakage is judged against "
        "— material about this case dated at or after it postdates what the cell "
        "was allowed to see, and no other recorded date stands in for it",
    )
    decided_before: str | None = Field(
        default=None,
        description="The replay clock: retrieval about this case must not postdate "
        "it. Null on a forward cell, whose outcome does not exist yet",
    )
    signals_observable: bool = Field(
        description="Whether the payload disclosed a proceedings list at all. False "
        "means the docket-progress signals below are UNOBSERVABLE from what the cell "
        "saw, not that they are zero — a redacted replay snapshot drops the "
        "proceedings wholesale, and reading that absence as 'never distributed' "
        "would invent a fact"
    )
    distribution_count: int | None = Field(
        default=None,
        ge=0,
        description="Distinct conferences the snapshot showed this petition distributed "
        "for, as at provisioning; None when unobservable",
    )
    cvsg_date: date | None = Field(
        default=None,
        description="CVSG invitation date the snapshot showed, or None for no CVSG — "
        "ambiguous unless signals_observable is true",
    )
    band: str | None = Field(
        default=None,
        description="The sal-v1 salience band as at prediction, derived from the "
        "signals above. None when they were unobservable, which is the honest "
        "answer for a cell whose snapshot carried no proceedings — the evaluator "
        "then falls back to the terminal band rather than guessing",
    )
    salience_version: str | None = Field(
        default=None, description="Version of the scorer that produced band"
    )
    term: int | None = Field(
        default=None, description="The case's October Term, the leakage guard's key"
    )


class ClaimProbability(_Strict):
    """One declared claim's stated probability, inside ``Prediction.claims``.

    The claim *set* is the harness's, never the predictor's: per event kind the
    declaration table in ``fedcourtsai.pipeline.claims`` fixes exactly which
    claims a prediction carries, and the predictor states a probability for
    every one of them — no additions, no declining (the mandatory-set rationale
    is in ``docs/outcome-decomposition.md``). This record carries only the
    predictor's number; the resolution, the baseline, and the score are
    harness-computed at evaluation time, never stated here.
    """

    claim_id: str = Field(
        description="The declared claim this probability answers, e.g. "
        "'disposition', 'relist-increment', 'cvsg-increment'"
    )
    probability: float = Field(
        ge=0.0,
        le=1.0,
        description="The predictor's probability that the claim resolves true",
    )


class SemanticClaim(_Strict):
    """One declared **semantic** claim's stated proposition, inside ``Prediction.semantic_claims``.

    The semantic counterpart of :class:`ClaimProbability`, and deliberately not
    its twin: it carries **no probability**. A semantic claim resolves by a
    reader matching a predicted proposition against what the Court actually
    wrote, and no harness-computed prior exists for a proposition like "the
    majority rests on textualist grounds" — so there is no ``b`` for
    ``(b - y)^2 - (p - y)^2`` to consume, and a number attached here would only
    invite the rule to be applied where its baseline requirement cannot be met.
    A grade, not a score, is what this claim earns
    (:class:`SemanticSupport`); ``docs/outcome-decomposition.md``, *The semantic
    family, alpha*, is the design authority.

    The set is the harness's exactly as the mechanical set is
    (``fedcourtsai.pipeline.semantic``). **No stage declares one today**, so no
    committed prediction carries this block; the field exists so that turning
    the family on is a declaration plus a prompt that asks for it, rather than
    a new shape. One piece is still owed on this side and named in
    ``docs/outcome-decomposition.md``, *What remains unbuilt*: unlike
    ``Prediction.claims``, nothing yet holds this list to the declared set, so
    the mandatory-set discipline binds graders and not predictors.
    """

    claim_id: str = Field(
        description="The declared semantic claim this proposition answers, e.g. "
        "'majority-ground' — the id the harness declared, never one the "
        "predictor invented"
    )
    proposition: str = Field(
        min_length=1,
        max_length=1000,
        description="The predicted proposition, stated so a grader can match it "
        "against the opinion: one specific, falsifiable assertion about what the "
        "Court's reasoning will be, not a hedged survey of possibilities",
    )


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
    granted: int = Field(
        ge=0,
        le=1,
        description="Binary outcome prediction on the stage's own axis: 1=granted "
        "on a cert or interim event, 1=the judgment below is disturbed on a merits "
        "event. The companion of `probability`, which states the same binary's P.",
    )
    probability: float = Field(
        ge=0.0,
        le=1.0,
        description="P(granted); on a merits-stage event the same field is "
        "P(disturbed) — the probability the judgment below is reversed, vacated, "
        "or reversed in part. The stage names the binary, exactly as it does for "
        "`granted` (the Stage vocabulary).",
    )
    predicted_disposition: Disposition
    votes: list[JusticeVote] = Field(default_factory=list)
    judgment: Judgment | None = Field(
        default=None,
        description="The predicted merits judgment — what the Court will do to "
        "the judgment below, the mirror of `Outcome.judgment`. Null on "
        "non-merits cells, which forecast no judgment. A merits-stage cell must "
        "set it (the `validate` gate holds the event's latest prediction to "
        "that), and setting it requires a non-empty `votes` block: a merits "
        "forecast is over per-Justice votes (docs/decision-model.md), so a "
        "judgment call with no vote block is malformed.",
    )
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
    reasoning_doc: str = Field(
        default="reasoning.md",
        description="Filename, beside this prediction, of the predictor's own "
        "rationale for its numbers: why this probability, what in the snapshot "
        "drove it, which base rates it consulted, where it is uncertain. "
        "Self-justification — it resolves against nothing.",
    )
    predicted_reasoning_doc: str | None = Field(
        default=None,
        description="Filename, beside this prediction, of the forecast of the "
        "*Court's* own reasoning — claims about the future that resolve against "
        "the docket (relists, a CVSG, which question presented is taken, a "
        "summary disposition). Distinct from `reasoning_doc`, which justifies the "
        "number rather than predicting the Court. Optional (defaults None) so "
        "records written before the field existed still validate.",
    )
    process_version: ProcessVersion | None = Field(
        default=None,
        description="Harness-stamped process version (absent on shakedown cells "
        "written before the stamp existed); the frozen-headline partition key.",
    )
    context: PredictionContext | None = Field(
        default=None,
        description="The conditioning state this cell ran against, frozen at "
        "provisioning. Harness-written like process_version — anything an agent "
        "puts here is overwritten. Absent on predictions written before the block "
        "existed, and on cells that ran without a provisioned snapshot.",
    )
    claims: list[ClaimProbability] | None = Field(
        default=None,
        description="Per-claim probabilities over the harness-declared claim set "
        "for this event (`fedcourtsai.pipeline.claims`; for a cert-stage "
        "petition: disposition, relist-increment, cvsg-increment; for the "
        "merits event: judgment-disturbed). The set is "
        "fixed and mandatory — the harness declares it, the predictor states a "
        "probability for every declared claim, and it can neither add claims nor "
        "skip them. Optional (defaults None) only so predictions written before "
        "the field existed still validate.",
    )
    semantic_claims: list[SemanticClaim] | None = Field(
        default=None,
        description="Per-claim propositions over the harness-declared **semantic** "
        "claim set for this event (`fedcourtsai.pipeline.semantic`). Graded "
        "against the opinion text by a reader, never scored by "
        "`claim_score` — a semantic claim has no harness-computable prior, so "
        "the mechanical rule's baseline requirement cannot be met and the family "
        "reports grades descriptively instead. Null on every committed "
        "prediction: the declaration tables are empty (`semantic-v0` is alpha, "
        "and no opinion body is ingested to ground a claim against), so no cell "
        "is asked for one.",
    )

    @model_validator(mode="after")
    def _judgment_requires_votes(self) -> Prediction:
        """A predicted judgment must carry its per-Justice vote block.

        The merits contract makes the vote block mandatory, and this is the
        half of it the schema can enforce self-contained: a prediction does not
        carry its event's stage, so "merits-stage cell => judgment set" lives
        in the ``validate`` gate (which reads the event definition), while
        "judgment set => votes non-empty" holds right here on every artifact.
        """
        if self.judgment is not None and not self.votes:
            raise ValueError(
                "a prediction carrying `judgment` must carry a non-empty `votes` block"
            )
        return self


class ResolutionSignals(_Strict):
    """The docket-progress signals as at resolution, frozen into the outcome.

    The corpus carries these as live-parsed columns, but a corpus column holds the
    *current* value, not the value at any fixed moment. A forecast about them —
    whether the petition would be relisted, whether the Court would call for the
    Solicitor General's views — therefore has nothing immutable to resolve
    against: re-scoring the same cell later reads a column that has moved on, and
    a pre-registration record cannot rest on that. Copying them onto the outcome
    at resolution fixes the *resolution* end of that comparison, and makes it
    reproducible.

    It is not sufficient on its own. These signals only ever grow, so a forecast
    about them is a forecast about an increment, and an increment needs both ends
    — the value as at prediction as well as as at resolution. The prediction end
    is ``Prediction.context`` (the harness-written ``PredictionContext``), so a
    claim resting on this block alone can only be specified as an absolute
    level, which is trivially true wherever the signal had already fired when
    the cell ran. See ``docs/outcome-decomposition.md``.

    The block is present only when the proceedings were live-parsed. That is the
    same coverage rule the corpus uses: ``CorpusRow.distribution_count`` is the
    sentinel for the whole live-signal family, so where it is absent nothing here
    was observed. Absent block means *not observed*; present block means observed,
    and inside it ``cvsg_date`` of ``None`` genuinely means no CVSG rather than no
    record — which is the distinction a claim has to be able to make.
    """

    distribution_count: int = Field(
        ge=0,
        description="Distinct conferences the petition was distributed for as at "
        "resolution; relists are this minus one, floored at 0",
    )
    cvsg_date: date | None = Field(
        default=None,
        description="Date the Court called for the Solicitor General's views, or "
        "None for no CVSG — unambiguous here, because the block exists only where "
        "the proceedings were parsed",
    )


class Outcome(_Strict):
    """``outcome.json`` — realized ground truth, written once an event resolves."""

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    event_id: str
    resolved_at: date
    actual_disposition: Disposition = Field(
        description="The realized disposition label. On a merits-stage outcome "
        "the cert/interim vocabulary has no member by design (Judgment values "
        "are deliberately not Dispositions), so the writer records `other` and "
        "`judgment` carries the result; the stage axis keeps such cells out of "
        "every cert-vocabulary figure.",
    )
    actual_granted: int = Field(
        ge=0,
        le=1,
        description="The stage's declared binary: 1 iff the disposition is in "
        "the granted set on a cert/interim event, and 1 iff the judgment below "
        "was disturbed (reversed / vacated / affirmed-in-part — "
        "`pipeline.judgment.judgment_disturbed`) on a merits event, so "
        "`(probability - actual_granted)^2` is the Brier score at every stage.",
    )
    votes: list[JusticeVote] = Field(default_factory=list)
    signals: ResolutionSignals | None = Field(
        default=None,
        description="Docket-progress signals frozen as at resolution, fixing the "
        "resolution end of a forecast about them rather than leaving it on a "
        "corpus column that keeps moving. These signals only grow, so resolving "
        "an increment also needs the value as at prediction — the "
        "`Prediction.context` block's half of the pair. Absent on outcomes "
        "written before the block existed, "
        "and on events whose proceedings were never live-parsed",
    )
    vote_provenance: VoteProvenance | None = Field(
        default=None,
        description="Where `votes` came from and how much of it is there. Absent "
        "means nobody looked, which is the state of every outcome today; present "
        "with complete=false means the missing votes are unobserved rather than "
        "absent. Without it a short vote list cannot be told from an unexamined one",
    )
    judgment: Judgment | None = Field(
        default=None,
        description="What the Court did to the judgment below — the merits axis, "
        "kept off the cert disposition vocabulary because a DIG has no coherent "
        "value on the grant binary. Null on a cert-stage outcome, which has no "
        "judgment to record",
    )
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


class ClaimScore(_Strict):
    """One declared claim's scored row inside ``Evaluation.claim_scores``.

    Everything here except ``probability`` is the harness's: the outcome is
    resolved in code from committed artifacts, and the baseline is computed
    from history strictly prior to the case's Term — never the predictor's
    word, never a corpus column that keeps moving. The scoring rule and its
    properties are pre-registered in ``docs/outcome-decomposition.md``.
    """

    claim_id: str = Field(description="The declared claim this row scores")
    probability: float = Field(
        ge=0.0,
        le=1.0,
        description="The predictor's stated probability, copied from the prediction's claims block",
    )
    baseline: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The harness-computed baseline: the claim's rate pooled over "
        "statpack Terms strictly before the case's Term, conditioned on the "
        "state the prediction's frozen context disclosed. None when the "
        "committed statpack publishes no cut that supports a strictly-prior, "
        "properly-conditioned rate for this claim — the claim then goes "
        "unscored rather than scored against an invented number",
    )
    outcome: int | None = Field(
        default=None,
        ge=0,
        le=1,
        description="How the claim resolved: 1 true, 0 false. None when the "
        "record does not disclose it — the availability mask, a property of the "
        "record and never of the predictor: an outcome without a signals block "
        "discloses no increment, a context whose signals were unobservable "
        "fixes no prediction-time value, and a CVSG already on the docket at "
        "prediction time makes the cvsg-increment claim vacuous",
    )
    score: float | None = Field(
        default=None,
        description="(baseline - outcome)^2 - (probability - outcome)^2 — the "
        "baseline's Brier minus the forecast's (`pipeline.evaluate.claim_score`). "
        "None when outcome or baseline is None",
    )


class ClaimScoreBlock(_Strict):
    """The harness-computed mechanical claim scores for one prediction.

    Advisory and segmented, exactly like the leakage assessment: the block
    describes a cell without changing the numbers it is ranked on, and it never
    alters ``correct``, ``brier_score``, ``vote_accuracy``, or
    ``brier_skill_score``. Computed end to end by
    ``fedcourtsai.pipeline.claims.score_claims`` from committed artifacts — the
    prediction's frozen context, the outcome's signals block, and the committed
    statpack — so re-scoring the same cell reproduces the same block. The
    publishing rules a total travels under (the floor beside it, the event
    count, never pooled across strata) are ``docs/outcome-decomposition.md``'s.
    """

    declared_set_version: str = Field(
        description="The claim-set declaration that produced this block's rows, "
        "e.g. 'cert-v1' — the versioned constant in `fedcourtsai.pipeline.claims`"
    )
    claims: list[ClaimScore] = Field(
        default_factory=list,
        description="One row per declared claim, in the declaration's order",
    )
    total: float | None = Field(
        default=None,
        description="Sum of `score` over the scored claims only (those with both "
        "an outcome and a baseline); None when no claim scored. Descriptive, "
        "never a rank key, and not evidence of case-level skill on its own — it "
        "travels with the floor and lift beside it",
    )
    floor: float | None = Field(
        default=None,
        description="The realized total of the control conditioned the way the "
        "predictor is conditioned: it reports, for every scored claim, the "
        "harness baseline itself, so it is identically 0 over the scored claims "
        "(restating the baseline is worth exactly nothing, by propriety) — "
        "computed per block rather than asserted, so definition and number "
        "cannot drift apart. It prices baseline-restating and nothing else: the "
        "information-free expectation from base-rate drift (~(b - pi)^2 per "
        "claim, the dominant term) and from baseline estimation error "
        "(~pi(1-pi)/n, small at the pooled denominators) is not bounded by this "
        "number — the comparison that carries a skill claim is head-to-head at "
        "equal coverage, which cancels the baseline term entirely "
        "(docs/outcome-decomposition.md). None when no claim scored",
    )
    lift: float | None = Field(
        default=None,
        description="`total` minus `floor` — identical to the total while the "
        "floor is identically 0. Descriptive like the total; see the floor's "
        "description for what remains unpriced and which comparison carries a "
        "skill claim. None when no claim scored",
    )


class SemanticGrade(_Strict):
    """One declared semantic claim's graded row inside ``Evaluation.semantic_grades``.

    The semantic counterpart of :class:`ClaimScore`, and structurally different
    in the one way that matters: there is no ``baseline`` and no ``score``. The
    mechanical rule needs a harness-computed prior from strictly-prior history,
    a semantic proposition has no such frequency, and manufacturing one would
    put a number where no evidence supports it — so this row carries an ordinal
    grade and stops there (``docs/outcome-decomposition.md``, *The semantic
    family, alpha*).

    Unlike every field of :class:`ClaimScore`, the grade **is** the grader's
    word — resolving it needs a reader, which is the definition of the semantic
    family. That is exactly why inter-grader agreement travels beside any
    published grade rather than as an optional diagnostic: with three evaluators
    grading each cell, agreement is measurable, and it is the only check on
    grader latitude this family has.
    """

    claim_id: str = Field(description="The declared semantic claim this row grades")
    grade: SemanticSupport = Field(
        description="How far the opinion supports the predicted proposition. "
        "`not-addressed` is the availability mask — the record does not put the "
        "claim in question (no opinion body of the required kind exists, none is "
        "ingested, or the opinion is silent on the claim's axis) — a property of "
        "the record and never of the predictor, so it is counted apart from the "
        "ordinal levels and never averaged with them"
    )
    basis: str | None = Field(
        default=None,
        max_length=2000,
        description="What in the opinion the grade rests on, briefly — the "
        "passage or holding the grader matched against. A grade whose basis "
        "restates the prediction rather than the opinion is a paraphrase graded "
        "against itself, which the grading protocol forbids; this field is what "
        "makes that visible in review. Null when the grader recorded none",
    )


class SemanticGradeBlock(_Strict):
    """One evaluator's grades over a prediction's declared semantic claim set.

    Advisory and segmented like :class:`ClaimScoreBlock`, and further out still:
    it carries no total, is never pooled with mechanical claim scores (the two
    are not in the same units and one is not a score at all), and is never a
    rank key. What may be read off it is fixed by ``metrics/README.md``; what it
    *is* is fixed by ``docs/outcome-decomposition.md``, *The semantic family,
    alpha*.

    **Alpha, and inert.** ``semantic-v0`` is provisional and unproven against
    opinion text — not a pre-registered commitment in the sense ``cert-v1`` and
    ``merits-v1`` are. No stage declares a semantic set, no prompt asks for one,
    and so no committed evaluation carries this block and no published number
    depends on it. The first set actually put to work arrives as ``semantic-v1``
    with its own review; supersession is the expected path, not an exception.
    """

    declared_set_version: str = Field(
        description="The semantic claim-set declaration these rows answer, e.g. "
        "'semantic-v0' — the versioned constant in `fedcourtsai.pipeline.semantic`"
    )
    grades: list[SemanticGrade] = Field(
        default_factory=list,
        description="One row per declared semantic claim, in the declaration's "
        "order. The set is mandatory exactly as the mechanical set is: a grader "
        "grades every declared claim and adds none, using `not-addressed` where "
        "the record settles nothing rather than skipping the row",
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
    correct: int = Field(
        ge=0,
        le=1,
        description="1 if the prediction named the right outcome label on the "
        "stage's own axis: the disposition on a cert/interim cell, the judgment "
        "on a merits cell (whose `actual_disposition` is always the "
        "off-vocabulary `other`, so a disposition comparison there would score "
        "every cell against a constant). Computed identically in code by "
        "`pipeline.evaluate.is_correct`; the leaderboard's accuracy column is "
        "its mean.",
    )
    brier_score: float | None = Field(default=None, ge=0.0, le=1.0)
    judgment_correct: int | None = Field(
        default=None,
        ge=0,
        le=1,
        description="1 iff the prediction's `judgment` exactly matches the "
        "outcome's — the merits-axis analogue of `correct`, on the full Judgment "
        "vocabulary (a `reversed` call against a `vacated` outcome is 0). Null "
        "wherever either side records no judgment: every non-merits cell, and "
        "records written before the field existed. The evaluator's field, like "
        "`correct` and `brier_score` — the harness stamps only `claim_scores` "
        "and the base-rate basis record — but computed identically in code by "
        "`pipeline.evaluate.judgment_correct`, which the offline engines use. "
        "Descriptive accuracy, never a "
        "proper score: `brier_score` on the disturbed binary is the scored axis, "
        "and `correct` already carries this same comparison on a merits cell.",
    )
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
    segment_base_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The leakage-safe segment base rate for this case, on the stage's "
        "own axis. On a cert cell that is its sal-v1 band's grant rate pooled over "
        "statpack Terms strictly before the case's Term, and which band — therefore "
        "which of the two published rates — is recorded in base_rate_basis below. On "
        "a merits cell it is instead the statpack merits section's disturbed rate "
        "pooled over grant Terms strictly before the case's "
        "(`pipeline.evaluate.merits_base_rate`), which is not a salience-band product, "
        "so base_rate_basis and base_rate_salience_version stay null there. An interim "
        "cell has no published rate and omits the field. The naive "
        "baseline the prediction's skill is scored against; null on offline evaluator "
        "outputs, when no prior-Term data exists for the stage's rate, and on records "
        "written before the field existed.",
    )
    base_rate_basis: Literal["risk_set", "terminal"] | None = Field(
        default=None,
        description="Which salience-band population segment_base_rate was taken over. "
        "Null wherever the rate is not a band product — a merits cell's Term-pooled "
        "disturbed rate, and an interim cell, which takes no rate at all. 'risk_set' "
        "pools across every petition that had REACHED the prediction's frozen band — "
        "the population a live cell was actually in, and the right basis wherever the "
        "prediction carries a frozen band. 'terminal' pools across petitions that "
        "ENDED in the band derived from the row now, the fallback where no frozen "
        "band exists (an older cell, or one whose snapshot disclosed no proceedings). "
        "The two differ several-fold in the weak bands, so a skill score is only "
        "comparable within one basis; absent on evaluations written before the "
        "distinction existed.",
    )
    base_rate_salience_version: str | None = Field(
        default=None,
        description="Harness-stamped record of which salience version the "
        "segment_base_rate's band was read under — the version half of the "
        "basis record, the parallel of `base_rate_basis`. Stamped by "
        "`stamp-cell --role evaluator` deterministically from the same inputs "
        "the basis names (never the evaluator's word, and an evaluator-written "
        "value does not survive the stamp): on the `risk_set` path it is the "
        "scored prediction's frozen `context.salience_version`, on the "
        "`terminal` path the live scorer's version. Null when no basis is "
        "recorded — which includes every merits cell, whose baseline is not a "
        "salience-band product and so has no scorer version to pin — and on "
        "records written before the field existed.",
    )
    brier_skill_score: float | None = Field(
        default=None,
        le=1.0,
        description="Brier skill score vs `segment_base_rate` "
        "(1 - brier / baseline_brier): ~0 when the prediction merely parrots the "
        "segment base rate, positive when it beats it, negative when worse. Null "
        "when `segment_base_rate` is null, when the baseline is already exact (the "
        "base rate matched the outcome), and on records written before the field "
        "existed.",
    )
    claim_scores: ClaimScoreBlock | None = Field(
        default=None,
        description="The harness-computed mechanical claim scores over the "
        "prediction's declared claim set (`fedcourtsai.pipeline.claims`). "
        "Advisory: it segments and describes, and never alters `correct`, "
        "`brier_score`, `vote_accuracy`, or `brier_skill_score`. Never the "
        "evaluator's word — the harness computes the block from committed "
        "artifacts. Null on records written before the block existed and on "
        "predictions carrying no claims block.",
    )
    semantic_grades: SemanticGradeBlock | None = Field(
        default=None,
        description="This evaluator's grades over the prediction's declared "
        "**semantic** claim set (`fedcourtsai.pipeline.semantic`). Advisory like "
        "`claim_scores`, and further out: it carries no total, is never pooled "
        "with mechanical claim scores, and is never a rank key. Unlike "
        "`claim_scores` it is the grader's word by construction — a semantic "
        "claim needs a reader — which is why inter-grader agreement travels "
        "beside any published grade. Null on every committed evaluation: no "
        "stage declares a semantic set and no prompt asks for one.",
    )
    notes_doc: str = "evaluation.md"
    process_version: ProcessVersion | None = Field(
        default=None,
        description="Harness-stamped process version of the *evaluator* (absent on "
        "shakedown cells). Provenance for the judge process; the leaderboard's "
        "frozen partition keys on the *prediction's* stamp, not this one.",
    )


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


class CellFailure(_Strict):
    """``attempt.json`` — one predict/evaluate cell's durable failure fact.

    The activation of the per-cell attempt cap. The ``collect`` job is the only
    observer of a cell that ran and produced no usable artifact, but it is
    corpus-blind (git-ledger write only), so it records the failure here, in the
    git ledger, rather than in the corpus. One file per failed cell, at a
    run-scoped path (``predictions/<predictor>/<run>/attempt.json`` for predict,
    ``evaluations/<evaluator>/<run>/attempt.json`` for evaluate), so a rerun of the
    same run overwrites its own fact (collect-side idempotency) while distinct
    failed runs accumulate distinct files. The deriver counts these files per
    ``(actor, event, seam)`` cell (:func:`fedcourtsai.matrix.cell_failure_count`)
    and stops re-queuing a cell that has failed the cap's worth of times — the
    poison-pill backstop the level-triggered re-derivation otherwise lacks.

    ``error_class`` is **coarse triage metadata only**; every fact counts equally
    toward the cap regardless of its class. No genuine transient/permanent signal
    is available at collect time — a cell's ``status.json`` carries only
    produced/validated/agent_ok booleans and a died cell carries nothing — so the
    class is derived from which collect bucket the cell fell in: ``no_output``
    (ran, produced nothing), ``partial`` (produced output that failed validation or
    stopped early), ``died`` (queued but never uploaded), overridden to ``quota``
    when the cell's whole engine produced zero cells this run.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    seam: Literal["predict", "evaluate"] = Field(
        description="Which stage's cell failed — matches the ledger subtree the fact lives under."
    )
    actor: str = Field(description="The predictor_id (predict) or evaluator_id (evaluate).")
    court: str
    docket: int
    event_id: str
    run_id: str = Field(description="The fan-out run that observed the failure.")
    error_class: Literal["no_output", "partial", "died", "quota"] = Field(
        description="Coarse triage class only; every fact counts equally toward the cap."
    )


class RetrievalCall(_Strict):
    """One tool invocation harvested from the engine's own transcript.

    Captured by the harness from the engine log — never the agent's word — so
    the evaluator's leakage grading can see what a cell actually
    retrieved. Long parameters and results are digested, not stored: the log
    is an audit trail, not a content mirror. A transcript records whatever a
    tool call carried, so every string captured here (``tool``, ``query``,
    ``timestamp``) is credential-redacted first: a run shaped like a token is
    replaced by a ``[redacted:rule]`` marker naming the shape. Read a marker as
    a redaction rather than as retrieved content — though nothing stops an
    agent typing the literal string into a tool call, so it is a reading aid,
    not provenance. The digests cover the payload before redaction.
    """

    tool: str = Field(
        description="Tool name as the engine logged it (redacted at capture), "
        "e.g. mcp__courtlistener__search"
    )
    query: str | None = Field(
        default=None,
        max_length=2000,
        description="The human-legible query/params slice, where extractable — "
        "credential-redacted at capture, then truncated",
    )
    params_digest: str | None = Field(
        default=None, description="SHA-256 (hex, 16 chars) of the full serialized params"
    )
    timestamp: str | None = Field(
        default=None,
        description="Engine-logged wall-clock time of the call, redacted at capture",
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
    mcp_tools: list[str] = Field(
        default_factory=list,
        description="Tool names those pinned servers advertise — the cell's OFFERED set, "
        "snapshotted from the manifest so an offered-vs-called comparison has a "
        "denominator. `mcp_servers` names servers, not tools, so it cannot supply one. "
        "Empty on records written before the field existed: offered-unknown, not "
        "nothing-offered.",
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

    Two skill columns sit here, and they are never blended either. ``population_brier_skill_score``
    scores against the strictly-prior pooled band rate — the leakage-safe
    baseline, and the primary outcome measure — while
    ``population_realized_term_skill_score`` holds the level at the rate the case's own
    Term actually realized. Together they decompose skill **per cell**: the
    first rewards knowing the level *and* discriminating within it, the second
    nets the level out and leaves discrimination alone. Different baselines
    answer different questions, so no figure combines them, only the first may
    rank, and — since the second qualifies a narrower, never-identical set of
    cells, which its own ``*_scored`` count records — the two are not a
    difference either.

    Both are **population** skills, ``1 - sum(brier) / sum(baseline_brier)``
    over the cells they score, rather than means of per-cell ratios — which is
    what the ``population_`` prefix records, against the plain ``mean_*``
    fields beside them. The ratio caps at +1 but is unbounded below, so a mean
    of ratios under cert's class imbalance rewards under-forecasting the rare
    event (``fedcourtsai.leaderboard.CellSkill``).
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
    population_brier_skill_score: float | None = Field(
        default=None,
        le=1.0,
        description="Brier skill vs the stage's own segment base rate over the "
        "cells that report one (higher is better; ~0 = no better than that "
        "baseline, negative = worse). Despite the name it is the **population** "
        "skill — `1 - sum(cell Brier) / sum(cell baseline Brier)` — not a mean "
        "of per-cell ratios, which under cert's class imbalance would be "
        "dominated by low-baseline denial cells and would pay a predictor to "
        "under-forecast the rare event. Distinct from raw Brier: it credits beating the biased "
        "predicted-segment base rate, not the whole-docket rate. On the cert board "
        "the baseline is the salience segment's grant rate; a merits cell reports "
        "no skill score at all while the merits pool's GVR guard is unbuilt "
        "(docs/decision-model.md), so a merits stage block's mean is null",
    )
    skill_scored: int = Field(
        default=0,
        ge=0,
        description="Evaluations contributing to population_brier_skill_score — the cells "
        "carrying a non-null skill score. The figure's true denominator, which "
        "can be far below `evaluations` (a cell scores skill only where a segment "
        "base rate exists), so the figure must be read beside this count",
    )
    population_realized_term_skill_score: float | None = Field(
        default=None,
        le=1.0,
        description="Brier skill against the **realized** rate of each "
        "case's own October Term, aggregated as the same population ratio "
        "population_brier_skill_score is — the same band and basis as "
        "population_brier_skill_score, with the baseline held at the level that "
        "actually obtained instead of the strictly-prior pool, and computed "
        "leave-one-out so a case never sits in the baseline that scores it. "
        "Holding the level fixed nets out level-knowledge and leaves "
        "discrimination: a predictor with the Term's level right but no ability "
        "to separate its cases reads positive on the prior-Term figure and ~0 "
        "here. Strictly **ex post** — no predictor could have known its Term's "
        "realized rate — so it never ranks and is never pooled or averaged with "
        "population_brier_skill_score, whose baseline answers a different question; "
        "the two are a per-cell decomposition and their board means, taken over "
        "different cell sets, must not be differenced. Cert stage only (no "
        "other stage has a salience band), and null wherever no cell scored",
    )
    realized_term_skill_scored: int = Field(
        default=0,
        ge=0,
        description="Evaluations contributing to population_realized_term_skill_score. "
        "Its own denominator, separate from `skill_scored`: this metric also "
        "needs the cell's own Term to carry the band under the matching salience "
        "version and to clear the stated minimum resolved count "
        "(`pipeline.evaluate.REALIZED_BAND_RATE_MIN_RESOLVED`) after the "
        "leave-one-out, so it is omitted — visibly, here — on a thin band rather "
        "than computed on a handful of cases",
    )
    mean_vote_accuracy: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Mean panel-vote accuracy where reported"
    )
    mean_reasoning_quality: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Mean evaluator reasoning-quality score"
    )


class EvaluatorAgreement(_Strict):
    """How far one evaluator's big-case reads track the rest of the panel's.

    The check on grader latitude. An evaluator with room to judge can be
    systematically generous or strict, and nothing in a per-predictor score would
    show it — the distortion is spread evenly across everyone that evaluator
    scored. Comparing each grader against its peers is what makes it visible.

    Computed **leave-one-out**: the evaluator's ordering against the mean of the
    *other* evaluators' reads on the events they share. Including the evaluator in
    the panel it is scored against would correlate it partly with itself, and with
    a three-judge panel that self-term is a third of the comparison.

    A rank correlation for the same reason the predictor-side agreement is one:
    bigness is comparative, so what matters is whether two graders order cases the
    same way, not whether they pick the same numbers. Read it with ``events``
    beside it — with a panel this small and few shared events, tau-b is noisy, and
    a single disagreement moves it far.
    """

    rank_agreement: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Kendall's tau-b between this evaluator's big-case ordering and "
        "the mean of the other evaluators' reads, over the events they share "
        "(+1 = same order, -1 = reversed); null with fewer than 2 shared events, "
        "or when every pair ties on one side",
    )
    events: int = Field(
        default=0,
        ge=0,
        description="Events this evaluator and at least one peer both read — the "
        "sample the correlation rests on, and small enough to matter",
    )


class BigCaseLeaderboard(_Strict):
    """A predictor's big-case-score agreement with the independent evaluator panel.

    A *second* skill dimension, orthogonal to the grant/deny ranking (a model can
    read a case's significance well while calling grant/deny only modestly, or the
    reverse). Bigness is comparative, so the agreement is a **rank** correlation —
    Kendall's tau-b between the predictor's ``big_case_score`` ordering and the
    panel's (the mean of the evaluators' independent reads), across the scored
    **cases** both sides rated. A case carrying several forecast moments
    contributes one point, both sides averaged over its moments: bigness is a
    property of the case, so a case's moments are not independent observations
    and a correlation that assumed they were would overstate its own evidence.
    Never enters the leaderboard ranking; reported alongside it.
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
        "evaluator big-case read — cases, not events: a case's forecast moments "
        "are averaged into one point",
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


class LeaderboardStageEntry(_Strict):
    """One predictor's aggregates within a single non-cert stage.

    The same per-stratum aggregate shape as a ranked :class:`LeaderboardEntry`,
    minus the rank and the big-case dimension: a non-cert stage's cells resolve
    on a different decision standard than the cert board's, so they report
    separately and never rank — and never pool into any cert figure.
    """

    predictor_id: str
    evaluators: int = Field(
        ge=0, description="Distinct evaluators that scored this predictor in this stage"
    )
    forward: LeaderboardStratum | None = Field(
        default=None,
        description="This stage's true forward forecasts; null when this "
        "predictor has none in the stage.",
    )
    retrospective: LeaderboardStratum | None = Field(
        default=None,
        description="This stage's retrospective cells; null when this predictor "
        "has none in the stage.",
    )
    procedural: LeaderboardStratum | None = Field(
        default=None,
        description="This stage's mootness-basis cells; null when this predictor "
        "has none in the stage.",
    )


class LeaderboardStage(_Strict):
    """One unranked ``stage@moment`` population, aggregated per predictor.

    A stage is a decision standard (cert / interim / merits — the event
    vocabulary) and a moment is the point in the case's life the forecast was
    taken from, so the pair — not the stage alone — identifies a population.
    Skill figures are only meaningful within one: `granted`
    answers a different question at each stage, and only the cert segment
    reports a skill score today — the interim stage has no published base rate,
    and the merits stage has a registered one whose skill number is suppressed
    while the pool's GVR guard is unbuilt (docs/decision-model.md). So each
    stage carries its own counts and entries,
    listed by ``predictor_id`` (never ranked), and nothing here blends into the
    cert board or another stage.
    """

    evaluations_total: int = Field(ge=0, description="Evaluations aggregated in this stage")
    forward_evaluations: int = Field(
        default=0, ge=0, description="This stage's forward-forecast evaluations"
    )
    retrospective_evaluations: int = Field(
        default=0, ge=0, description="This stage's retrospective evaluations"
    )
    procedural_evaluations: int = Field(
        default=0, ge=0, description="This stage's mootness-basis evaluations"
    )
    entries: list[LeaderboardStageEntry] = Field(
        default_factory=list,
        description="Per-predictor aggregates, ordered by predictor_id — an "
        "ordering, not a ranking",
    )


class Leaderboard(_Strict):
    """``metrics/leaderboard.json`` — predictors ranked from the evaluations ledger.

    A deterministic, offline roll-up of every ``evaluation.json`` under ``data/``:
    one entry per predictor, ranked best-first on the **forward** stratum (see
    :class:`LeaderboardStratum` — the strata are never blended into one number,
    and ``evaluations_total`` includes the procedural cells the ranking
    excludes). The ranked board is the **cert stage**: the entries and the
    evaluation counts cover cert-stage cells only (the big-case and
    evaluator-agreement blocks are stage-blind — they describe stakes reads,
    not stage-scoped skill), while any non-cert stage reports its own
    unranked block under ``stages`` (omitted entirely while none exist — see the
    serializer). Computed by ``fedcourts leaderboard`` from the ledger and the
    committed ``metrics/statpack.json`` (the vintage the realized-Term skill
    column is scored on); carries no timestamp, so the same two inputs always
    serialize identically.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    process_scope: Literal["frozen", "all"] = Field(
        default="frozen",
        description="Which process versions this board covers: `frozen` (the "
        "default headline — only cells whose predictor ran the blessed frozen "
        "process) or `all` (every version, including the shakedown). A `frozen` "
        "board with zero predictors is the honest 'no frozen-process evaluations "
        "yet' state, not a regression.",
    )
    salience_versions: list[str] = Field(
        default_factory=list,
        description="The distinct salience versions the ranked cells' baselines "
        "were read under, sorted. The gate decides WHICH petitions earn cells at "
        "all, so it partitions the population rather than the process — and "
        "unlike a process change it does not move any digest. More than one "
        "entry therefore means the aggregates pool two differently-gated "
        "populations and are coverage figures, not a ranking (the rule "
        "`declared_set_versions` states for a claim total). Empty on a board with "
        "no salience-banded baseline, which includes an all-merits board.",
    )
    predictors_ranked: int = Field(
        ge=0,
        description="Number of predictors on the cert board (a procedural-only "
        "predictor still appears, sorted after every ranked one)",
    )
    evaluations_total: int = Field(
        ge=0,
        description="Total cert-stage evaluations aggregated; each `stages` block "
        "carries its own counts, never pooled into these",
    )
    procedural_evaluations: int = Field(
        default=0,
        ge=0,
        description="Cert-stage evaluations segmented out for a mootness-basis "
        "outcome (never ranked)",
    )
    forward_evaluations: int = Field(
        default=0, ge=0, description="Cert-stage evaluations of true forward forecasts"
    )
    retrospective_evaluations: int = Field(
        default=0,
        ge=0,
        description="Cert-stage evaluations of retrospective (leakage-suspect) cells",
    )
    evaluator_agreement: dict[str, EvaluatorAgreement] = Field(
        default_factory=dict,
        description="Per evaluator, how far its big-case reads track the rest of "
        "the panel's — the check on grader latitude, keyed by evaluator_id. "
        "Orthogonal to the ranking and never part of it: it describes the judges, "
        "not the competitors",
    )
    entries: list[LeaderboardEntry] = Field(
        default_factory=list,
        description="The ranked cert-stage board — one entry per predictor with a "
        "cert-stage evaluation",
    )
    stages: dict[str, LeaderboardStage] = Field(
        default_factory=dict,
        description="Unranked blocks for every population outside the ranked "
        "board, keyed `<stage>@<moment>` (`interim@arrival`, `merits@briefed`) — "
        "a later forecast moment of a stage answers the same question with more "
        "evidence, so it is a separate population and never shares a mean with "
        "an earlier one. A stage with no recorded moment keys bare (`interim`), "
        "and a cell with no stage at all shares one `(none)` bucket, so coverage "
        "stays visible rather than guessed. Nothing here pools across blocks or "
        "into the cert board, and the key is omitted entirely while no such "
        "cell exists.",
    )

    @model_serializer(mode="wrap")
    def _omit_empty_optional_axes(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop the ``stages`` and ``salience_versions`` blocks while each is empty.

        The StatPack stage sections' rule, applied here: an axis is shown only
        once its cells do, and serializing an empty placeholder would both
        misstate that contract and add byte noise to every board that does not
        have it — an all-cert ledger carries no ``stages`` key, and a ledger
        whose cells record no banded baseline carries no ``salience_versions``.
        """
        payload = handler(self)
        if isinstance(payload, dict):
            if not self.stages:
                payload.pop("stages", None)
            if not self.salience_versions:
                payload.pop("salience_versions", None)
        return payload


class ClaimMeanScore(_Strict):
    """One declared claim's mean score over a claim-score stratum's events.

    A per-claim mean is **diagnostic**, never a headline: the reported unit is
    the total over the declared set, and a claim singled out afterwards
    describes that claim rather than the predictor
    (``docs/outcome-decomposition.md``, *Reading a total honestly*). A claim
    with ``scored == 0`` still appears — the declaration, not the data, fixes
    the rows, so an unscored claim is a visible coverage gap rather than an
    absent one.
    """

    claim_id: str = Field(description="The declared claim this row averages")
    scored: int = Field(
        ge=0,
        description="Events whose block carries a score for this claim — the "
        "mean's denominator. 0 wherever the availability mask or a missing "
        "baseline left the claim unscored on every event",
    )
    mean_score: float | None = Field(
        default=None,
        description="Mean of the claim's per-event scores over the `scored` "
        "events; null when none scored",
    )


class ClaimScoreStratum(_Strict):
    """One predictor's claim-score aggregates over one pre-registration stratum.

    Never pooled across strata and never a rank key: a claim total's variance
    is unbounded above and a bold uninformed spray has a fat right tail, so
    the defensible comparison is head-to-head at equal coverage — these
    aggregates are descriptive (``docs/outcome-decomposition.md``). The
    reporting unit is the **event**, as the pre-registration fixes it: every
    evaluator of the same prediction carries an identical harness-computed
    block, so blocks are deduplicated to one per (case, event) before
    averaging (the newest evaluation's block wins where a statpack revision
    between evaluator stamps ever made copies differ) and ``cells`` beside
    ``events`` is the raw census of the collapsed multiplicity.
    """

    events: int = Field(
        ge=0,
        description="Distinct (case, event) pairs carrying a block — the "
        "reporting unit, and the event count the publishing rules require "
        "beside a total",
    )
    cells: int = Field(
        ge=0, description="Evaluation cells carrying a claim-score block in this stratum"
    )
    scored_events: int = Field(
        ge=0,
        description="Events whose block total is non-null (at least one claim "
        "scored) — the one denominator of the three means",
    )
    declared_set_versions: list[str] = Field(
        default_factory=list,
        description="Distinct claim-set declarations behind the blocks, sorted. "
        "A total is never comparable across declarations, so more than one "
        "entry here means the means pool incomparable sets and must be read "
        "as coverage only",
    )
    mean_total: float | None = Field(
        default=None,
        description="Mean per-event claim total (Brier units, never bits) over "
        "the scored events; null when none scored. Not evidence of case-level "
        "skill on its own — it travels with the floor and lift beside it",
    )
    mean_floor: float | None = Field(
        default=None,
        description="Mean per-event floor over the scored events — identically "
        "0 by propriety, computed rather than asserted so definition and number "
        "cannot drift apart (see ClaimScoreBlock.floor for what stays unpriced)",
    )
    mean_lift: float | None = Field(
        default=None,
        description="Mean per-event lift (total minus floor) over the scored "
        "events — identical to mean_total while the floor is identically 0",
    )
    claims: list[ClaimMeanScore] = Field(
        default_factory=list,
        description="Per-claim mean scores, in the declarations' reporting order",
    )
    largest_claim_id: str | None = Field(
        default=None,
        description="The claim behind largest_claim_score; null when no claim scored",
    )
    largest_claim_score: float | None = Field(
        default=None,
        description="The largest-magnitude single-claim score across the "
        "stratum's events — reported beside the means because extreme baselines "
        "pay asymmetrically, so one lucky surprise can swamp dozens of honest "
        "calls; a total that is one claim in disguise must be visible in the "
        "same breath. Null when no claim scored",
    )


class ClaimJudgeAgreement(_Strict):
    """The mechanical↔semantic agreement over one stratum — the judge validation.

    The pre-registered estimator (``docs/outcome-decomposition.md``, *The
    mechanical↔semantic agreement*): Kendall tau-b over per-cell pairs of
    (mechanical claim total, ``reasoning_quality``). It validates the semantic
    grader against the mechanical record, not the other way round — agreement
    says the judge tracks something the ground truth also sees; disagreement
    says it grades prose. Either result publishes. It says nothing about
    which predictor is better, and it is never a rank key.

    The absence counts cover **committed** evaluation cells only: an evaluator
    cell that never ran or failed outright commits nothing, so it is invisible
    here and differential cell failure still selects the pair set upstream of
    these counts.
    """

    rank_agreement: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Kendall's tau-b between the cells' mechanical claim totals "
        "and their reasoning_quality grades. Null while suppressed (see "
        "`suppressed`), and null when undefined (fewer than 2 pairs, or every "
        "pair tied on one axis)",
    )
    pairs: int = Field(
        ge=0,
        description="The intersection population: cells carrying BOTH a scored "
        "claim total and a reasoning_quality grade — printed beside the "
        "coefficient because a tau over 4 cells is a different fact from a tau "
        "over 400. A per-CELL count, as the pre-registration fixes it, so the "
        "suppression rule keys on it; pair_events beside it exposes evaluator "
        "multiplicity",
    )
    pair_events: int = Field(
        ge=0,
        description="Distinct (case, event) pairs behind `pairs`. Every "
        "evaluator of the same prediction contributes a pair with an identical "
        "mechanical total, so evaluator multiplicity inflates `pairs` with "
        "tied-x replicates — this count is what makes that visible",
    )
    suppressed: bool = Field(
        description="True when `pairs` is below the pre-registered minimum of "
        "10 — the coefficient is withheld (null) and only the counts publish",
    )
    missing_claim_block: int = Field(
        ge=0,
        description="Cells in this stratum with no claim-score block at all — "
        "the operational absences (a prediction predating the claims contract, "
        "a malformed claims block), counted because differential absence "
        "selects the pair set and a selected intersection must be visible",
    )
    masked_claim_total: int = Field(
        ge=0,
        description="Cells whose block is present but whose total is null — "
        "every claim masked or baseline-less, a property of the record and "
        "never of the predictor (the availability mask)",
    )
    missing_reasoning_quality: int = Field(
        ge=0,
        description="Cells without a reasoning_quality grade — the semantic "
        "side's operational absences, counted for the same selection reason",
    )


class ClaimScoreEntry(_Strict):
    """One predictor's claim-score aggregates, per stratum, in id order.

    Entries carry no rank on purpose: a claim total is never a rank key, so
    the artifact orders predictors alphabetically and assigns no standings.
    """

    predictor_id: str
    forward: ClaimScoreStratum | None = Field(
        default=None,
        description="Aggregates over true forward forecasts; null until this "
        "predictor has a forward cell carrying a block",
    )
    retrospective: ClaimScoreStratum | None = Field(
        default=None,
        description="Aggregates over retrospective cells — iteration signal "
        "only, never claimable (a resolved case's claims are retrievable, not "
        "forecastable); null when none carry a block",
    )
    procedural: ClaimScoreStratum | None = Field(
        default=None,
        description="Aggregates over mootness-basis cells, segmented out of "
        "both timing strata exactly as the leaderboard segments them; null "
        "when none carry a block",
    )


class ClaimScoreBoard(_Strict):
    """``metrics/claim-scores.json`` — the mechanical claim-score surface.

    A deterministic, offline roll-up of every ``claim_scores`` block in the
    evaluations ledger, advisory beside the leaderboard rather than inside it:
    nothing here alters or reorders the board. Aggregates live per predictor
    per pre-registration stratum, never pooled; the headline is the per-stratum
    judge validation (:class:`ClaimJudgeAgreement`). Computed by ``fedcourts
    claim-scores``; carries no timestamp so the same ledger always serializes
    identically. Interpretation contract: ``metrics/README.md`` and
    ``docs/outcome-decomposition.md``.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    process_scope: Literal["frozen", "all"] = Field(
        default="frozen",
        description="Which process versions this surface covers, keyed on the "
        "prediction's stamp exactly like the leaderboard: `frozen` (the default "
        "headline) or `all` (every version, including the shakedown). A claim "
        "total is never comparable across the scope boundary — nor across "
        "process versions within a scope: a scope holding more than one "
        "claims-carrying process version must not be read as one population "
        "(docs/outcome-decomposition.md)",
    )
    evaluations_total: int = Field(
        ge=0,
        description="Cert-stage evaluation cells in scope, with or without a "
        "claim block — the surface's whole population, cert-stage because only "
        "the cert-stage event kinds declare a claim set, so a cell on any "
        "other stage is never owed a block and belongs outside the absence "
        "counts",
    )
    cells_with_claims: int = Field(
        ge=0,
        description="Evaluation cells carrying a claim-score block — 0 is the "
        "honest state while every committed evaluation predates the claims "
        "contract's first scored run, not a regression",
    )
    forward_agreement: ClaimJudgeAgreement | None = Field(
        default=None,
        description="The judge validation over the forward stratum — the only "
        "stratum whose mechanical totals are forecasts; null when the stratum "
        "has no cells in scope",
    )
    retrospective_agreement: ClaimJudgeAgreement | None = Field(
        default=None,
        description="The judge validation over the retrospective stratum "
        "(iteration signal); null when the stratum has no cells in scope",
    )
    procedural_agreement: ClaimJudgeAgreement | None = Field(
        default=None,
        description="The judge validation over the procedural stratum; null "
        "when the stratum has no cells in scope",
    )
    entries: list[ClaimScoreEntry] = Field(
        default_factory=list,
        description="One entry per predictor with at least one block-carrying "
        "cell, ordered by predictor_id — never ranked",
    )


class SemanticClaimSummary(_Strict):
    """The grade census for one semantic claim — counts, and nothing derived from them.

    Descriptive by construction. The three ordinal levels are counted, the
    availability mask is counted apart from them, and the one derived figure —
    ``supported_share`` — is withheld below the minimum graded count, because a
    share over three grades describes three grades rather than a predictor.
    Nothing here is a score, nothing is pooled with a mechanical claim total,
    and nothing is a rank key (``metrics/README.md``).
    """

    claim_id: str | None = Field(
        default=None,
        description="The declared semantic claim these counts cover; null on "
        "the pooled `overall` census, which is a coverage figure rather than a "
        "claim's own",
    )
    supported: int = Field(default=0, ge=0, description="Grades of `supported`")
    partial: int = Field(default=0, ge=0, description="Grades of `partially-supported`")
    unsupported: int = Field(default=0, ge=0, description="Grades of `unsupported`")
    not_addressed: int = Field(
        default=0,
        ge=0,
        description="Grades of `not-addressed` — the availability mask, a "
        "property of the record and never of the predictor. Counted apart from "
        "the ordinal levels and never inside `graded`, so a claim the record "
        "could not settle never reads as a claim the predictor got wrong",
    )
    mask_disputed: int = Field(
        default=0,
        ge=0,
        description="Units where graders split on the mask itself — some read "
        "`not-addressed`, some graded on the ordinal scale. Excluded from the "
        "ordinal counts and from the agreement coefficient: the disagreement is "
        "about what the record discloses, so it measures the record's adequacy "
        "rather than the predictor or the panel",
    )
    graded: int = Field(
        default=0,
        ge=0,
        description="Units resolved on the ordinal scale — supported + partial "
        "+ unsupported. The denominator for `supported_share`, and the count a "
        "reader must see beside it",
    )
    cells: int = Field(
        default=0,
        ge=0,
        description="Distinct cells behind every unit counted here, masked ones "
        "included. On a per-claim census it equals the unit total (one cell "
        "contributes one unit to a given claim) and states the identity rather "
        "than adding to it. On the pooled `overall` census it is the count that "
        "bounds the evidence: that census reaches the minimum on `graded` "
        "units, which a multi-claim set can accumulate from a couple of cells",
    )
    supported_share: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="`supported` over `graded` — descriptive only, never a rank "
        "key and never comparable across claim-set versions or strata. Null "
        "when `graded` sits below the published minimum, where the counts still "
        "publish and only this figure is withheld",
    )


class SemanticGraderAgreement(_Strict):
    """How far one grader's semantic grades track the rest of the panel's.

    The semantic family's only check on grader latitude, and mandatory beside
    any published grade rather than optional: the grade is a reader's word by
    construction, so a uniformly generous or strict grader is invisible in the
    grades themselves and visible only against its peers.

    Computed **leave-one-out**, the same shape as
    :class:`EvaluatorAgreement`: the grader's ordering of the shared units
    against the mean of the *other* graders' ordinals, correlated with Kendall's
    tau-b. A rank correlation because the vocabulary is ordinal with heavy ties,
    which is exactly what tau-b is for; leave-one-out because a panel mean
    containing the grader correlates it partly with itself, and on a three-judge
    panel that self-term is a third of the comparison.

    Read it as a property of the **panel**, not of one judge — with three
    graders a single dissenter sits inside both peers' comparison and can turn
    all three negative.
    """

    rank_agreement: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Kendall's tau-b between this grader's ordinal grades and "
        "the mean of the other graders' on the units they share (+1 = same "
        "order, -1 = reversed). Null three ways, and **all three bar "
        "publication**: below the published minimum unit count; with fewer "
        "than 2 shared units; and when one axis has no variation across units, "
        "so every pair ties on it. The third is *undefined*, never 'the panel "
        "agreed' — a panel that agrees on grades that differ across units "
        "reads +1, not null. What produces a tied axis is a **constant** one: "
        "a record so uniform every unit graded alike, or a uniformly generous "
        "grader whose own axis never moves. The coefficient cannot tell those "
        "apart, and the second is the exact pathology this number exists to "
        "catch, so an undefined coefficient is never read as agreement",
    )
    paired_units: int = Field(
        default=0,
        ge=0,
        description="Shared (cell, claim) units behind the coefficient — "
        "published whether or not the coefficient is, so a withheld number is "
        "visibly withheld rather than absent. Named apart from "
        "`SemanticGradeSummary.units`, which counts a different population "
        "(every unit, masked ones included)",
    )
    cells: int = Field(
        default=0,
        ge=0,
        description="Distinct cells those units came from, and the count that "
        "actually bounds the evidence: the units of one cell share a "
        "prediction, an opinion, and a single reading pass, so they are "
        "strongly correlated and the effective sample is nearer this number "
        "than `paired_units`. The minimum threshold keys on `paired_units` — "
        "unlike the mechanical judge validation's, which keys on cells — so "
        "this count is what stops a published coefficient over one claim set "
        "on two cells from reading like one over ten",
    )
    claims_pooled: int = Field(
        default=0,
        ge=0,
        description="Distinct declared claims the coefficient pools, and the "
        "integer that bounds its pooling caveat. The coefficient is one number "
        "per grader across every claim, so a stable *between-claim* contrast — "
        "this claim type is easy, that one is hard — can carry a tau-b near +1 "
        "while within-claim agreement is zero. At 1 there is no such contrast "
        "available to do the work; the higher this runs, the more of the "
        "coefficient it could be. Splitting the coefficient per claim is left "
        "to a version with the per-claim sample to spare",
    )
    suppressed: bool = Field(
        default=False,
        description="Whether `rank_agreement` was withheld for sitting below "
        "the minimum unit count. False with a null coefficient means the "
        "coefficient is *undefined* rather than withheld — one axis had no "
        "variation to correlate. It bars publication either way; the flag "
        "separates a thin sample from a degenerate one, which are different "
        "things to fix. (At any threshold of 2 or more — the published one is "
        "10 — a grader with fewer than two shared units is below the minimum "
        "too, so that case is recorded as withheld rather than undefined.)",
    )


class SemanticGradeSummary(_Strict):
    """The descriptive roll-up of a set of semantic grades, with agreement beside it.

    What the ``semantic-v0`` seam produces:
    :func:`fedcourtsai.pipeline.semantic.summarize_semantic_grades` builds it
    from graded units and nothing else — no baseline, no score, no total. There
    is no such artifact under ``metrics/`` and no cell produces a grade to feed
    one; this is the shape a future surface would publish, exercised now
    against synthetic grades so the plumbing is proven before real ones exist.

    Two of the rules it publishes under it cannot enforce for itself, because a
    graded unit carries neither label: ``stratum`` and ``process_scope`` are
    the caller's word. Nothing marks a census unpublishable — a null is the
    only signal there is — and an undeclared census is not publishable.

    **Alpha.** ``semantic-v0`` is provisional and unproven against opinion text,
    explicitly not a pre-registered commitment in the sense ``cert-v1`` and
    ``merits-v1`` are (``docs/outcome-decomposition.md``, *The semantic family,
    alpha*). What may and may not be read off a grade is ``metrics/README.md``'s.
    """

    stratum: Stratum | None = Field(
        default=None,
        description="The pre-registration stratum this census covers, stated by "
        "the caller and never inferred. Typed on the closed vocabulary because "
        "the label is all there is here — the roll-up cannot check it against "
        "the cells, so nothing else would stop a caller naming a stratum the "
        "project does not have. Null means undeclared, and an undeclared census "
        "is not publishable: strata are never pooled, and a summary that pooled "
        "forward and retrospective cells would otherwise be indistinguishable "
        "from one that did not",
    )
    process_scope: Literal["frozen", "all"] | None = Field(
        default=None,
        description="The process-version scope this census covers, stated by "
        "the caller and never inferred, and closed for the same reason as "
        "`stratum`. Null means undeclared, and carries the same bar: a grade is "
        "never comparable across the scope boundary",
    )
    declared_set_versions: list[str] = Field(
        default_factory=list,
        description="The semantic claim-set declarations these counts pool, "
        "sorted. More than one entry demotes every figure here to coverage: a "
        "grade is never comparable across declarations, exactly as a mechanical "
        "total is never comparable across claim-set versions. A defensive "
        "disclosure — `pipeline.semantic.graded_units` refuses a block whose "
        "version disagrees with the declaration, so units drawn from the ledger "
        "always share one, and a mixed value says the units were assembled some "
        "other way",
    )
    cells: int = Field(default=0, ge=0, description="Distinct graded cells behind these counts")
    units: int = Field(
        default=0,
        ge=0,
        description="Distinct (cell, claim) units, masked ones included. Not "
        "what any threshold keys on: the share keys on a claim's `graded` "
        "count and the agreement coefficient on that grader's `paired_units`",
    )
    graders: int = Field(default=0, ge=0, description="Distinct graders contributing grades")
    min_graded: int = Field(
        default=0,
        ge=0,
        description="The suppression threshold these figures were built under, "
        "published with them so a withheld share cannot be mistaken for a "
        "missing one",
    )
    claims: list[SemanticClaimSummary] = Field(
        default_factory=list,
        description="One census per declared semantic claim, ordered by claim_id",
    )
    overall: SemanticClaimSummary | None = Field(
        default=None,
        description="The census pooled over claims — a coverage figure, not a "
        "headline: different claims are different propositions of different "
        "difficulty, so their pooled share describes the claim mix as much as "
        "the predictor. Null when there is nothing to pool",
    )
    agreement: dict[str, SemanticGraderAgreement] = Field(
        default_factory=dict,
        description="Per grader, leave-one-out rank agreement with the rest of "
        "the panel, **pooled across claims** — the per-claim unit counts are "
        "too thin to correlate separately, at the cost that graders who merely "
        "order the claim *types* alike read as agreeing, so a per-claim share "
        "travels with a panel-level figure rather than its own. Empty when no "
        "unit carried two graders on the ordinal scale (a unit graders split on "
        "the mask contributes to neither side) — the state in which no grade "
        "may be published at all, since agreement is the family's only check on "
        "grader latitude",
    )


class BacktestCourtScore(_Strict):
    """One predictor's standings over a single court's slice of the back-test set.

    The per-court cut exists because the pooled figure is not interpretable on its
    own: ``granted`` means cert granted on a SCOTUS row and a motion granted on a
    court-of-appeals docket, and each court carries its own outcome skew. Reading
    accuracy against the court's own always-deny floor is what separates skill from
    the base rate — a constant predictor scores the floor exactly, so a lift of zero
    is the signal that it learned nothing.
    """

    court: str
    events_scored: int = Field(ge=0, description="Events replayed for this predictor in this court")
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
    always_denied_accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="This court's always-deny floor — the fraction of its scored events whose "
        "disposition is `denied`. The base rate that makes the accuracy above readable",
    )
    lift_over_always_denied: float = Field(
        ge=-1.0,
        le=1.0,
        description="Disposition accuracy minus this court's always-deny floor. Zero means the "
        "predictor matched the base rate and added nothing; the same convention the cert "
        "back-test uses, so the two instruments are read the same way",
    )


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
    always_denied_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The always-deny floor over the whole scored set. Reported for context only: "
        "the set spans courts whose `denied` labels are different acts, so this is a reference "
        "point rather than a comparable skill baseline — read the per-court cut for that. `null` "
        "on an artifact written before the floor was computed, like `mean_brier_score`",
    )
    lift_over_always_denied: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Disposition accuracy minus the pooled always-deny floor. Presentational: "
        "entries rank on raw accuracy and Brier, not on this, because the pooled floor mixes "
        "outcome vocabularies. `null` when the floor was not computed",
    )
    courts: list[BacktestCourtScore] = Field(
        default_factory=list,
        description="Per-court breakdown, court-id ordered — the grain at which the floor and "
        "the lift are actually comparable",
    )


class ToolUsageEntry(_Strict):
    """One MCP tool's offered-vs-called record, qualified ``<server>.<tool>``."""

    tool: str = Field(description="Server-qualified tool name, e.g. `courtlistener.search`")
    offered_cells: int = Field(
        default=0,
        ge=0,
        description="Cells whose manifest advertised this tool — the denominator. 0 means "
        "no cell recorded it as offered, which on logs predating the offered-tools "
        "record means unknown rather than not-offered",
    )
    called_cells: int = Field(
        default=0, ge=0, description="Cells that called it at least once (not total calls)"
    )
    calls: int = Field(default=0, ge=0, description="Total invocations across every cell")
    engines: dict[str, int] = Field(
        default_factory=dict,
        description="Calls per engine — a tool used by one engine and not another is "
        "usually a prompt or sandbox difference, not a tool problem",
    )
    actors: dict[str, int] = Field(
        default_factory=dict, description="Calls per predictor/evaluator id"
    )


class ToolUsage(_Strict):
    """The offered-vs-called tool rollup over every committed retrieval log.

    Answers which configured tools are actually earning their place. A zero in
    ``calls`` means **never called** — not useless: the prompt may never mention
    the tool, or a sandbox may have blocked it, and this data cannot separate
    those from genuine uselessness. Read it beside ``offered_cells``.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    logs: int = Field(default=0, ge=0, description="Retrieval logs rolled up")
    logs_without_offered_record: int = Field(
        default=0,
        ge=0,
        description="Logs carrying no `mcp_tools` (written before the field existed), so "
        "they contribute calls but no offered denominator",
    )
    pins: dict[str, int] = Field(
        default_factory=dict,
        description="Logs per `<id>=<pinned package>` the cells actually ran under. Read it "
        "beside `offered_now`: when they name different versions, the offered set is "
        "today's and the calls are from an older server",
    )
    offered_now: list[str] = Field(
        default_factory=list,
        description="What the CURRENT manifest advertises, server-qualified. Supplies a "
        "denominator for logs written before per-cell `mcp_tools` existed; a tool listed "
        "here with no calls is genuinely never-called, while one called but absent here "
        "ran under an older pin",
    )
    web_calls: dict[str, int] = Field(
        default_factory=dict,
        description="Calls to each engine's open-web tools, counted under that engine's own "
        "tool names; a zero is not by itself evidence a cell chose not to search — check the "
        "retrieval surface its process version records",
    )
    cells_with_mcp: int = Field(
        default=0, ge=0, description="Cells that called at least one MCP tool"
    )
    cells_with_web: int = Field(
        default=0, ge=0, description="Cells that reached the open web at least once"
    )
    web_without_mcp_by_engine: dict[str, int] = Field(
        default_factory=dict,
        description="Cells that searched the web and called NO MCP tool, per engine — the "
        "MCP-gap signal. Suggestive, not proof: forward cells are explicitly allowed to "
        "use public context, so this flags candidates to inspect, not failures",
    )
    entries: list[ToolUsageEntry] = Field(
        default_factory=list,
        description="Offered-but-never-called first, then by descending calls — the "
        "actionable rows lead",
    )
    builtin_calls: dict[str, int] = Field(
        default_factory=dict,
        description="Calls to engine built-ins (shell, file IO, web search), counted "
        "separately because they are not what the manifest offers",
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


class CertBacktestSegment(_Strict):
    """One salience-band slice of a predictor's cert back-test standings.

    Reconciles the offline cert back-test with the live prediction process: the
    forward tournament now scores skill against the **segment base rate** (the
    predicted slice's own grant rate, not the whole-docket rate), so the back-test
    reports the same, per ``sal-v1`` band, over the paid scored segment (IFP
    petitions are outside it). ``segment_base_rate`` is the mean of the items'
    leakage-safe per-Term band rates (each computed over Terms strictly before its
    own), and ``mean_brier_skill`` the mean skill against them — null when no item
    in the band had a prior-Term base rate.
    """

    band: str = Field(description="The frozen sal-v1 band: high / elevated / baseline")
    events_scored: int = Field(ge=0, description="Paid-segment petitions in this band")
    accuracy: float = Field(
        ge=0.0, le=1.0, description="Disposition accuracy over the band's petitions"
    )
    mean_brier_score: float = Field(
        ge=0.0, le=1.0, description="Mean Brier score of P(granted) over the band"
    )
    segment_base_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean leakage-safe segment base rate over the band's items "
        "(each item's own prior-Term band grant rate); null when none had one",
    )
    mean_brier_skill: float | None = Field(
        default=None,
        le=1.0,
        description="Mean Brier skill vs the segment base rate over the band "
        "(positive beats the base rate, ~0 parrots it, negative is worse); null "
        "when no item had a base rate",
    )


class CertBacktestBigCase(_Strict):
    """A predictor's big-case-score distribution over the cert back-test set.

    The replay has no independent evaluator, so — unlike the live leaderboard's
    rank-agreement dimension — it cannot *grade* the score; it reports the
    predicted stakes distribution, which confirms the predictor exercised the
    dimension in replay and gives a calibration eyeball (is the 0-1 scale used, or
    clustered?). Deliberately **not** correlated with the realized grant: bigness
    is stakes, not grant likelihood (see ``docs/salience.md``), and conflating the
    two is the very thing the pre-registered score exists to avoid.
    """

    scored: int = Field(ge=0, description="Replayed petitions that carried a big_case_score")
    mean: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Mean predicted stakes over the scored petitions"
    )
    minimum: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Lowest big_case_score in the set"
    )
    maximum: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Highest big_case_score in the set"
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
    segments: list[CertBacktestSegment] = Field(
        default_factory=list,
        description="Per-salience-band skill breakdown over the paid scored segment "
        "(high, elevated, baseline; bands with no petition omitted) — the segment-"
        "baseline skill the forward stratum measures. Empty when no statpack was "
        "supplied (offline runs) or no paid-segment petition was scored",
    )
    big_case: CertBacktestBigCase | None = Field(
        default=None,
        description="The predictor's pre-registered big-case-score distribution over "
        "the set (stakes, not grade — the replay has no evaluator to grade against); "
        "null when the predictor produced no big_case_score (the offline baselines)",
    )


class CertBacktest(_Strict):
    """``metrics/cert-backtest.json`` — predictors replayed over decided cert petitions.

    The standing instrument for vetting cert predictors and prompt changes:
    replay over a curated set of resolved modern discretionary-cert petitions
    (outcome hidden — the replay provisions the docket as it stood before a
    cutoff, with the decision-only fields redacted), scored against the realized
    grant/deny.

    **Its band mix is not the forward channel's.** One cell per petition, placed
    at the *last* distribution before resolution, so the replay population sits in
    stronger bands than the forward trigger produces — that fires on any
    distribution transition, most often the first. So the always-deny floor here
    is lower than the forward stratum's, and neither the top line nor the band mix
    estimates forward performance. ``metrics/README.md``'s stratum rule bars the
    pooled comparison regardless. Produced by the maintainer-triggered
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
    salience_version: str = Field(
        default="",
        description="The frozen salience function whose bands segment this "
        "board. A band name means something only under the scorer that assigned "
        "it, so a per-band figure here is not comparable with one produced under "
        "another version; default empty only on a board built before the stamp "
        "existed.",
    )
    always_denied_accuracy: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="The always-deny floor's disposition accuracy over this set "
        "(the denial base rate every lift figure is measured against)",
    )
    provisioning: dict[str, int] = Field(
        default_factory=dict,
        description="How many replayed cells were provisioned under each "
        "snapshot_provenance — 'dated' (a snapshot the docket really served before "
        "the cutoff), 'truncated' (a later payload with its post-cutoff entries "
        "removed), 'blind' (no forward moment identifiable, so no trajectory was "
        "shown). These are three different information sets, and a figure over "
        "their union is a figure over a mixture: a blind cell cannot observe its "
        "own relist history at all, which is most of what a cert forecast turns "
        "on. Read the mix before reading the scores. Empty on reports written "
        "before the split existed",
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
    window_days: float | None = Field(
        default=None,
        ge=0.0,
        description="Unrounded span of the ledger's own created_at stamps, which "
        "turns the cumulative spend into a rate; None when fewer than two records "
        "or all records share one instant (no span to divide by). Carried at full "
        "precision because it is a divisor — rounding happens at the render sites, "
        "so display precision never moves the reported rate",
    )


class CostEstimate(_Strict):
    """A rough monthly cost run-rate, derived without billing-API access.

    GitHub Actions cost is estimated from observed run durations x the per-minute
    rate; model cost is the recorded usage ledger, both cumulatively and projected
    to 30 days from the ledger's own span; fixed monthly captures the infra not
    metered per run (CourtListener membership, S3). All figures are estimates
    against the rates in ``docs/budget.md`` — check the provider billing dashboards
    for ground truth.

    The model projection averages the ledger's full span, first record to last.
    A trailing idle tail (a paused tournament, an exhausted cap) falls outside
    the span and does not deflate it, but an interior gap or a low-volume early
    era falls inside it and does — so the figure trends toward a lifetime average
    as history accumulates. It answers "what has this cost per day while
    running", not "what will this month's invoice be".
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
    model_monthly_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="Model spend projected to 30 days from the usage ledger's span; "
        "None when the ledger has no span to rate against",
    )
    fixed_monthly_usd: float = Field(ge=0.0, description="Configured fixed monthly infra cost")
    estimated_monthly_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="actions_monthly + model_monthly + fixed_monthly. None when a "
        "known-nonzero component cannot be rated — a partial total that silently "
        "omits the dominant cost is worse than no total",
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
    """One named base-rate breakdown: a dimension, its population, and its buckets.

    The section shape both published base-rate artifacts are built from —
    :class:`StatPack` and :class:`DocketPack` — so a cut computed for both carries
    identical scope flags in each. ``court`` records the court filter the section
    was computed under (``None`` = all courts), so the artifact is self-describing
    — e.g. a SCOTUS-only Term breakdown vs an all-courts view. ``buckets`` is the
    per-group base-rate breakdown, most cases first (the same shape ``fedcourts
    stats --group-by`` produces).
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
        description="Weighted grant-family (granted + gvr pooled) share of "
        "resolved — pooled, so comparable across Terms where the `dispositions` "
        "split is not; None when nothing resolved",
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


class StatPackTermSegment(_Strict):
    """One salience-band slice of a Term's live-slice paid modern-cert petitions.

    The **segment base rate** the salience program turns on: with a salience gate
    the predicted population is a biased subsample (relist-2 petitions grant ~39%,
    relist-0 ~0.8%), so the whole-docket cert rate is the wrong yardstick both as
    the predict agent's prior and as the evaluator's naive baseline. Keying on the
    frozen ``sal-v1`` band gives each predicted case a base rate conditioned on its
    own grant-likelihood tier. Because the segment lives inside :class:`StatPackTerm`
    it inherits that surface's **per-Term self-selection contract** — a time-masked
    replay cell reads only Terms strictly before its clock, so the rate never leaks
    the current Term. Estimates are sample-weighted (each row counted
    ``sample_weight`` times), matching the Term's other weighted cuts.

    **Two rates, answering two different questions.** A band is monotone
    non-decreasing over a petition's life — the distribution count is max-latched
    and a CVSG date, once set, stays set — so a petition passes *through* the
    weaker bands on its way to the one it ends in.

    ``est_grant_rate`` conditions on the band a petition **ended** in. It is the
    descriptive cut: of the petitions that finished at one distribution, how many
    were granted.

    ``prefix_est_grant_rate`` conditions on having **reached** the band, which is
    the same event as "ended here or stronger". That is the forecast baseline,
    because a cell is scored at the band it sat in when it ran, and from there the
    petition may still relist. Conditioning a live forecast on the terminal rate
    would ask it to beat a number computed with knowledge of its own future, and
    understates the honest baseline several-fold in the weaker bands (the
    strongest band has nothing above it, so the two coincide there exactly).
    """

    band: str = Field(
        description="The frozen sal-v1 grant-likelihood band: high / elevated / baseline"
    )
    ingested: int = Field(default=0, ge=0, description="Live-slice paid-cert rows in this band")
    resolved: int = Field(
        default=0, ge=0, description="Rows in this band carrying a disposition (raw count)"
    )
    weighted_resolved: int = Field(
        default=0,
        ge=0,
        description="Sample-weighted resolved estimate for the band — the base rate's denominator",
    )
    est_grant_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Weighted grant-family (granted + gvr pooled) share of the "
        "rows that ENDED in this band — a descriptive rate, not a forecast "
        "baseline; None when nothing in the band resolved",
    )
    prefix_resolved: int = Field(
        default=0,
        ge=0,
        description="Rows in the band's risk set carrying a disposition (raw count) — "
        "the observed rows behind the weighted estimate beside it",
    )
    prefix_weighted_resolved: int = Field(
        default=0,
        ge=0,
        description="Sample-weighted resolved estimate over the band's risk set — "
        "every row that ever reached this band, not only those that ended in it. "
        "Risk sets are nested, so this contains every stronger band's",
    )
    prefix_est_grant_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Weighted grant-family (granted + gvr pooled) share over the "
        "band's risk set: "
        "P(grant | the petition has REACHED this band). The forecast baseline — "
        "this is what a predictor is asked to beat, because a cell is scored at "
        "the band it sat in when it ran, not the one it ended in. Identical to "
        "est_grant_rate for the strongest band, which has nothing above it; "
        "None when the risk set is empty",
    )


class StatPackTermVersionSegments(_Strict):
    """One Term's band slices under a **non-active** salience version.

    A band name means nothing on its own: a ``high`` under one scorer and a
    ``high`` under another are different populations that happen to share a
    label, so the base-rate pool is version-pinned
    (``pipeline.evaluate._pooled_band_rate``). A prediction freezes the version
    that banded it and keeps that version for life — which would leave it
    without a baseline the moment the live pass moved on. This block is where a
    non-active scorer's slices stay published, so the pin has something to match.
    """

    salience_version: str = Field(
        description="The frozen salience function whose bands these slices segment"
    )
    segments: list[StatPackTermSegment] = Field(
        default_factory=list,
        description="Per-band grant-rate slices under that version — same shape and "
        "same leakage contract as the active version's `segments`",
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
    est_grant_family_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Weighted grant-family share of this Term's resolved "
        "live-slice rows — granted + gvr today, and the vocabulary's "
        "`summary-reversal` label pools in too if a resolver ever produces it. "
        "The only disposition series comparable "
        "across Terms. The `gvr` label is a forward convention: a Term resolved "
        "into the corpus before it existed carries its GVRs as plain `granted` "
        "(OT2023-24 carry zero), so the split inside `base_rates.dispositions` is "
        "safe within a Term and meaningless between them — anchor any cross-Term "
        "comparison on this field. None when nothing resolved",
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
    salience_version: str = Field(
        default="",
        description="The frozen salience function whose bands segment this Term (e.g. sal-v1); "
        "default empty only on the pre-enrichment committed pack",
    )
    segments: list[StatPackTermSegment] = Field(
        default_factory=list,
        description="Per-salience-band grant-rate slices over this Term's paid modern-cert "
        "petitions (high, elevated, baseline), leakage-safe by construction — the segment "
        "base rate the predict prompt is designed to anchor on and the evaluator will score "
        "skill against, under the ACTIVE salience version named above",
    )
    alt_segments: list[StatPackTermVersionSegments] = Field(
        default_factory=list,
        description="The same per-band slices under every OTHER registered salience "
        "version, so a prediction frozen at a version the live pass no longer scores "
        "with still finds its own scorer's base rate. Empty — and absent from the "
        "serialized payload — while only one version is registered",
    )
    median_days_to_grant: float | None = Field(
        default=None,
        ge=0.0,
        description="Nearest-rank median days filing → cert grant over this Term's "
        "granted petitions; None when none carry both dates",
    )

    @model_validator(mode="after")
    def _alt_segments_name_distinct_non_active_versions(self) -> StatPackTerm:
        """No alt block may shadow the active version or another alt block.

        A duplicate would not blend — the reader takes the Term's own
        ``segments`` first and then the first matching block — it would silently
        shadow, which is the harder failure to notice: the pool would quote one
        scorer's rate under another's label and nothing would say so.
        """
        labels = [block.salience_version for block in self.alt_segments]
        if self.salience_version and self.salience_version in labels:
            raise ValueError(
                f"alt_segments repeats the active salience version {self.salience_version!r}; "
                "the active version's slices belong in `segments`"
            )
        if len(set(labels)) != len(labels):
            raise ValueError(f"alt_segments carries duplicate salience versions: {labels}")
        return self

    @model_serializer(mode="wrap")
    def _omit_empty_alt_segments(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``alt_segments`` from the payload while only one version is registered.

        A band rate is meaningful only under the scorer that assigned it, so the
        block exists to hold the non-active versions' slices. With a single
        registered version there are none, and serializing an empty list would
        add a key to every Term of every pack to say so.
        """
        payload = handler(self)
        if isinstance(payload, dict) and not self.alt_segments:
            payload.pop("alt_segments", None)
        return payload


class _StatPackInterimCounts(_Strict):
    """The count block one interim-docket slice carries (the pack, or one Term).

    Raw counts throughout: the live channel polls every application it discovers
    (no denial sampling, so every row stands only for itself) and nothing here is
    reweighted. Descriptive only — the substantive grant rate describes the
    accumulated cohort, and is **not** a segment base rate: the interim stage's
    scored base rate publishes only at the pre-registered resolved-count floor
    (``docs/salience.md``, *The interim docket*), so until then no skill or
    calibration claim rests on these figures. Extensions are counted so the
    docket's administrative dominance is visible, but they never pool into any
    rate — an extension is granted as a matter of course, and admitting it would
    hand the rate the Court's calendar rather than its judgment
    (``docs/salience.md``, *The interim docket*).
    """

    applications: int = Field(
        default=0,
        ge=0,
        description="Application dockets (strict `YYAnnn` form — the live channel's "
        "addressable population) in this slice",
    )
    extension: int = Field(
        default=0,
        ge=0,
        description="Applications whose parsed ask is an extension of time — the "
        "administrative majority, counted but never pooled into a rate",
    )
    substantive: int = Field(
        default=0,
        ge=0,
        description="Applications whose parsed ask is substantive (a stay, an "
        "injunction, a vacatur) — the interim docket proper, and the only slice "
        "any rate here is computed over",
    )
    unknown: int = Field(
        default=0,
        ge=0,
        description="Applications whose proceedings were parsed but whose ask "
        "could not be read — a parser gap, folded into neither kind. Also "
        "absorbs any out-of-vocabulary kind value, so the four kind counts "
        "always sum to `applications`",
    )
    unparsed: int = Field(
        default=0,
        ge=0,
        description="Applications never application-parsed at all (a NULL "
        "`application_kind`) — a coverage gap, distinct from `unknown`, which "
        "asserts a parse happened",
    )
    substantive_resolved: int = Field(
        default=0,
        ge=0,
        description="Substantive applications carrying a machine-readable interim "
        "disposition — the raw denominator behind `substantive_grant_rate`. An "
        "application whose disposing entry the interim vocabulary never matched "
        "stays out of the denominator, visibly unresolved, so the resolved set "
        "is selected for machine-matchable resolution text",
    )
    substantive_granted: int = Field(
        default=0,
        ge=0,
        description="Resolved substantive applications whose disposition lands on "
        "the granted side of the binary outcome mapping",
    )
    substantive_grant_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="substantive_granted / substantive_resolved — a descriptive "
        "rate over the resolved substantive slice only, never over extensions; "
        "withdrawn/dismissed resolutions count as ungranted. None when nothing "
        "substantive has resolved (no rate, not 0%)",
    )
    response_requested: int = Field(
        default=0,
        ge=0,
        description="Substantive applications where the Court (or a Circuit "
        "Justice) requested a response — the interim analogue of a CVSG",
    )
    referred_to_court: int = Field(
        default=0,
        ge=0,
        description="Substantive applications referred to the full Court rather "
        "than decided by a Circuit Justice alone",
    )
    with_amicus: int = Field(
        default=0,
        ge=0,
        description="Substantive applications whose docket records at least one "
        "amicus brief — a stakes proxy, flagged here rather than summed",
    )


class StatPackInterimTerm(_StatPackInterimCounts):
    """One application-Term's slice of the interim docket.

    The Term is read from the application's own docket number (``24A1099`` ->
    OT2024), so the split needs no dates. Like the cert Term entries, the array
    is a replay self-selection surface: a time-masked cell anchors only on Term
    rows strictly preceding its clock.
    """

    term: int = Field(description="The October-Term year the application was docketed in")


class StatPackInterim(_StatPackInterimCounts):
    """The statpack's interim-docket stage section: SCOTUS applications, by ask.

    The stage axis beside the cert sections: applications (stays, injunctions,
    vacaturs — and the extension requests that dominate the docket) are a
    different population resolving on a different standard, so they get their own
    section rather than a salience band — this section deliberately carries no
    ``salience_version``, because it is not a salience-band product. Pack-level
    counts with a per-application-Term breakdown; the accumulating cohort that
    will eventually ground an interim segment base rate, published descriptively
    until then. A stage section exists only once its corpus feed does: the pack
    omits it entirely while the corpus holds no application rows — the same
    joining rule the merits sibling (:class:`StatPackMerits`) follows on the
    ``merits_judgment`` column.
    """

    terms: list[StatPackInterimTerm] = Field(
        default_factory=list,
        description="Per-application-Term detail, most recent Term first",
    )


class _StatPackMeritsCounts(_Strict):
    """The count block one merits slice carries (the pack, or one grant Term).

    Raw counts throughout: every case whose grant opened a merits proceeding
    is walked, none stands in for
    another, and nothing here is reweighted (the denial-sampling frame covers
    the cert stage, and a grant is always ingested with certainty). The
    disturbed rate is the anchor of the pre-registered merits Brier baseline
    (``docs/decision-model.md``): a merits cell's skill is scored against the
    per-grant-Term disturbed rates pooled over Terms strictly before the
    case's (``pipeline.evaluate.merits_base_rate``), so a skill claim exists
    only once strictly-prior Terms carry parsed judgments — until then the
    figures stay descriptive, and ``metrics/README.md`` governs what may be
    claimed. ``parsed`` against ``granted`` is the
    backfill's own coverage statement, so a thin parse never masquerades as a
    thin docket — read the gap as an upper bound that blends still-pending
    cases (granted, not yet decided) with genuine parse gaps.
    """

    granted: int = Field(
        default=0,
        ge=0,
        description="SCOTUS cases in this slice whose grant opens a merits "
        "proceeding (a plain or partial grant with `date_cert_granted` set; a "
        "GVR or summary reversal decides in the cert order and is excluded) — "
        "the cohort the merits backfill walks, parsed or not",
    )
    parsed: int = Field(
        default=0,
        ge=0,
        description="Granted cases carrying a parsed `merits_judgment` — the "
        "denominator of every figure here, and the coverage numerator against "
        "`granted`",
    )
    affirmed: int = Field(default=0, ge=0, description="Judgments affirmed outright")
    reversed: int = Field(default=0, ge=0, description="Judgments reversed")
    vacated: int = Field(
        default=0,
        ge=0,
        description="Judgments vacated — a vacate-and-remand after argument "
        "disturbs the judgment below (a GVR's vacatur is a cert-order "
        "disposition and is not in this population)",
    )
    affirmed_in_part: int = Field(
        default=0,
        ge=0,
        description="Mixed outcomes: affirmed in part and reversed (or vacated) in part",
    )
    dig: int = Field(
        default=0,
        ge=0,
        description="Writs dismissed as improvidently granted — a non-merits exit "
        "that leaves the judgment below standing (undisturbed)",
    )
    equally_divided: int = Field(
        default=0,
        ge=0,
        description="Affirmances by an equally divided Court — affirmed by "
        "operation of law, undisturbed, and precedent-free",
    )
    disturbed: int = Field(
        default=0,
        ge=0,
        description="Parsed judgments that disturbed the decision below "
        "(reversed + vacated + affirmed-in-part)",
    )
    disturbed_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="disturbed / parsed — the **scored** merits base rate's "
        "per-Term feed (`pipeline.evaluate.merits_base_rate` pools these "
        "strictly-prior), conditioned on exactly the population a merits cell "
        "is drawn from. The two non-merits exits (DIG, equally divided) sit in "
        "the denominator as undisturbed, since both leave the judgment below "
        "intact. None when nothing has parsed (no rate, not 0%)",
    )


class StatPackMeritsTerm(_StatPackMeritsCounts):
    """One grant-Term's slice of the merits docket.

    The Term is the October Term certiorari was **granted** in, read from
    `date_cert_granted` (October pivot) — the one date every eligible row
    carries by construction, where the judgment's own `merits_decided` date is
    nullable (a judgment parsed from an undated entry) and so cannot key the
    split. This grant-date axis does **not** align with the cert tables'
    docket-number Terms: a petition docketed in Term T is routinely granted in
    T+1, so identically labeled rows across the two tables cover different
    cohorts. Like the cert Term entries, the array is a replay self-selection
    surface: a time-masked cell anchors only on Term rows strictly preceding
    its clock.
    """

    term: int = Field(description="The October-Term year certiorari was granted in")


class StatPackMerits(_StatPackMeritsCounts):
    """The statpack's merits stage section: what happened to granted cases' judgments.

    The second stage axis beside the cert sections, joining exactly as
    :class:`StatPackInterim` did: a stage section exists only once its corpus
    feed does, so the pack omits this one entirely while no row carries a
    parsed `merits_judgment`, and it carries no ``salience_version`` because it
    is not a salience-band product. Pack-level counts with a per-grant-Term
    breakdown; the per-Term disturbed rates are the committed feed of the
    pre-registered merits Brier baseline
    (``pipeline.evaluate.merits_base_rate`` pools them strictly-prior), so the
    ``terms`` array is a scoring input as well as a description. The population
    is the grants that open a merits proceeding — the same rule that mints the
    event a merits forecast is made on — so a GVR, whose vacatur rides in the
    cert order itself, never contributes a near-certain disturbance to a rate
    that scores forecasts about argued cases.
    """

    terms: list[StatPackMeritsTerm] = Field(
        default_factory=list,
        description="Per-grant-Term detail (Terms with at least one parsed "
        "judgment), most recent Term first",
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
    interim: StatPackInterim | None = Field(
        default=None,
        description="The interim-docket stage section (SCOTUS applications by ask, "
        "with the substantive slice's descriptive grant rate); None — and omitted "
        "from the serialized pack — while the corpus holds no application rows",
    )
    merits: StatPackMerits | None = Field(
        default=None,
        description="The merits stage section (granted cases' judgment "
        "distribution and descriptive disturbed rate); None — and omitted from "
        "the serialized pack — while no row carries a parsed merits judgment",
    )

    @model_serializer(mode="wrap")
    def _omit_absent_stage_sections(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop a stage section from the payload while its feed does not exist.

        A stage section is shown only once its corpus feed exists; serializing a
        ``null`` placeholder would both misstate that contract and add byte
        noise to every pack built from a corpus that does not feed the section,
        whose serialized form must carry no key for it at all.
        """
        payload = handler(self)
        if isinstance(payload, dict):
            if self.interim is None:
                payload.pop("interim", None)
            if self.merits is None:
                payload.pop("merits", None)
        return payload


class DocketPackTerm(_Strict):
    """One October Term's census in the court-facing docket pack.

    The whole-docket view of a Term: how many petitions were docketed, how many
    of them this project has ingested, and how the ingested ones came out. It
    pools the paid and IFP streams that :class:`StatPackTerm` keeps apart, and
    carries no salience segmentation — which petitions a model was pointed at is
    a fact about the project, not about the Court.
    """

    term: int = Field(description="The October-Term year, e.g. 2024")
    filings: int | None = Field(
        default=None,
        ge=0,
        description="Docketed serials this Term across both fee streams, from the "
        "discovery cursors; None when no stream has been probed",
    )
    complete: bool = Field(
        default=False,
        description="True when every probed stream was walked to its observed "
        "frontier; False = the counts describe the walked prefix only",
    )
    ingested: int = Field(default=0, ge=0, description="Petitions present in the corpus")
    resolved: int = Field(
        default=0, ge=0, description="Ingested petitions carrying a disposition (raw count)"
    )
    weighted_resolved: int = Field(
        default=0,
        ge=0,
        description="Denial-reweighted resolved estimate — the sample size behind "
        "`est_grant_rate` and `dispositions`",
    )
    est_grant_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Denial-reweighted grant-family (granted + gvr pooled) share "
        "of the resolved petitions — always equal to `est_grant_family_rate`, "
        "which carries the same series under the name the statpack's per-Term "
        "entries share; None when nothing resolved",
    )
    est_grant_family_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Denial-reweighted grant-family share of the resolved "
        "petitions — granted + gvr today, and the vocabulary's `summary-reversal` "
        "label pools in too if a resolver ever produces it. The only disposition "
        "series comparable "
        "across Terms, under the one field name both packs' per-Term entries "
        "share. The `gvr` label is a forward convention: a Term resolved into the "
        "corpus before it existed carries its GVRs as plain `granted` (OT2023-24 "
        "carry zero), so the split inside `dispositions` is safe within a Term "
        "and meaningless between them — anchor any cross-Term comparison here. "
        "None when nothing resolved",
    )
    dispositions: list[DispositionShare] = Field(
        default_factory=list,
        description="Denial-reweighted disposition estimates over the resolved petitions",
    )
    grants: int = Field(
        default=0, ge=0, description="Cert grants observed this Term (raw, not reweighted)"
    )
    median_days_to_grant: float | None = Field(
        default=None,
        ge=0.0,
        description="Nearest-rank median days filing → cert grant over this Term's "
        "granted petitions; None when none carry both dates",
    )
    dated_grants: int = Field(
        default=0,
        ge=0,
        description="Granted petitions carrying both a filing and a cert-grant date — "
        "the denominator `median_days_to_grant` is computed over, which is a subset "
        "of `grants`",
    )


class DocketPack(_Strict):
    """``metrics/docket.json`` — court-facing docket statistics (an independent artifact).

    Facts about the dockets themselves: what the Supreme Court is asked to take,
    from which court below, on what fee stream, after how many relists, and how it
    disposes of the petitions. Deliberately **free of any claim about this
    project's predictions** — no accuracy, no leaderboard, no salience — so it is
    readable and citable by someone with no interest in whether the models are any
    good. That exclusion is the artifact's contract, not a coincidence of what has
    been built.

    A pure function of the corpus (no clock, no network), so reruns over an
    unchanged corpus reproduce it byte for byte; git-tracked and rendered to a
    companion Markdown document. Every rate carries its scope and its denominator,
    and each section states whether its counts are denial-reweighted: the
    historical walk samples denials on a committed frame, so every cert cut is
    reweighted and its counts are population *estimates* rather than rows on
    hand. That distinction is why a reweighted denominator is not a sample size:
    the observed row count behind it is smaller. A breakdown bucket carries no
    raw view of its own; the per-Term entries carry both, so the gap between the
    two is legible there. Starts empty (zero counts, scaffolded sections) until a
    corpus is present.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    corpus_through: date | None = Field(
        default=None,
        description="The newest `last_pulled` date in the corpus — the vintage of "
        "the rows behind every figure here, so a citation can name what it read. "
        "Derived from the corpus rather than a clock, which keeps the artifact a "
        "pure function of its input; None when no row carries the date",
    )
    corpus_rows: int = Field(default=0, ge=0, description="Case rows in the corpus")
    resolved: int = Field(default=0, ge=0, description="Cases carrying a realized disposition")
    open: int = Field(default=0, ge=0, description="Cases still unresolved")
    coverage: StatPackCoverage = Field(
        default_factory=StatPackCoverage,
        description="The pack's own denominators: live-slice rows/resolved and the "
        "cursor-derived filings census backing the cert sections",
    )
    sections: list[StatPackSection] = Field(
        default_factory=list, description="Curated docket-composition breakdowns"
    )
    terms: list[DocketPackTerm] = Field(
        default_factory=list,
        description="Per-SCOTUS-Term census (filings, ingested, resolved, grant rate), "
        "most recent Term first",
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


class SalienceReplayCell(_Strict):
    """One (Term, cutoff policy, salience version) cell of the salience-gate replay.

    One frozen salience version run over one past Term's resolved paid modern-cert
    petitions, each projected to the state its docket disclosed as at the policy's
    cutoff (see ``fedcourtsai.pipeline.asof``). Selection here is what that
    version's gate *would have* latched at that moment; precision/recall score
    that selection against the realized grant-family outcomes.

    The version is on the **cell**, not the report, so every registered scorer
    replays over one common projection of the docket in a single run. That is
    what makes two versions comparable at all: they differ only in the scoring
    function, never in the reconstructed moment they scored.
    """

    term: int = Field(description="The October Term whose resolved petitions were replayed")
    salience_version: str = Field(
        default="",
        description="The frozen salience-function version whose scoring, banding, "
        "and selection produced this cell (e.g. sal-v1)",
    )
    policy: str = Field(
        description="The reconstruction moment: 'arrival' (day after the earliest "
        "dated docket entry), 'distribution-1' (day after the first DISTRIBUTED "
        "entry), or 'resolution' (the last distribution before the realized "
        "resolution — the latest posture a forward cell would have seen)"
    )
    eligible: int = Field(
        ge=0,
        description="Resolved, live-slice, paid modern-cert petitions of the Term "
        "(the time-invariant eligibility bar; a Tier-0 predicate that depends on "
        "post-arrival state is deliberately not applied)",
    )
    skipped_no_snapshot: int = Field(
        ge=0,
        description="Eligible petitions with no held snapshot to reconstruct from; "
        "outside every count below",
    )
    cohorts: int = Field(
        ge=0, description="Distinct as-of conference cohorts the capacity was applied within"
    )
    selected: int = Field(
        ge=0, description="Petitions the gate would have latched selected at this moment"
    )
    selected_carve_out: int = Field(
        ge=0,
        description="Selected via the always-include carve-outs (a CVSG on file, or a "
        "score at/above the salience floor) — the capacity-independent core",
    )
    selected_rank_fill: int = Field(
        ge=0,
        description="Selected by the rank-to-N capacity fill; with capacity above "
        "every cohort's size this equals every non-carve-out cohort member",
    )
    capacity_bound_cohorts: int = Field(
        ge=0,
        description="Cohorts whose non-carve-out membership exceeded the capacity, "
        "so the rank fill actually cut (elsewhere N is inert). Counted over the "
        "walked sample's cohorts: under legacy denial weights a replayed cohort "
        "holds ~1/weight of the real cohort's non-carve-out members, so capacity "
        "that would have bound over the Term's real cohort can read as inert here "
        "— compare largest_weighted_cohort against the capacity before trusting "
        "the rank-fill figures",
    )
    largest_weighted_cohort: float = Field(
        default=0.0,
        ge=0.0,
        description="The largest cohort's sample_weight-weighted non-carve-out "
        "mass — the reader's check on the rank fill: a value above the "
        "per-conference capacity where the raw cohort size sat below it means "
        "the real cohort could have been cut where the replayed sample was not, "
        "and the rank-fill and capacity figures are then sample statistics, not "
        "population estimates. 0 when the cell formed no cohort",
    )
    bands: dict[str, int] = Field(
        default_factory=dict,
        description="Petitions per as-of sal-v1 band (high / elevated / baseline), "
        "plus 'unobservable' for a projection whose payload disclosed no "
        "proceedings — unknown posture, never banded, never selected",
    )
    provenance: dict[str, int] = Field(
        default_factory=dict,
        description="Projections per snapshot provenance: 'dated' (a snapshot the "
        "docket really served before the cutoff), 'truncated' (a later payload "
        "with post-cutoff entries removed — it cannot detect an entry back-filled "
        "later but dated earlier, an accepted residual), and the two blind cases, "
        "proceedings removed outright: 'blind-no-moment' (no cutoff exists — the "
        "live gate would also never have cohorted this petition, a faithful gate "
        "miss) vs 'blind-untrusted-cutoff' (a disposition survived truncation, so "
        "a really-distributed petition is unselectable here only because its "
        "reconstruction could not be trusted). Different information sets; read "
        "the mix before the counts",
    )
    selected_granted: int = Field(
        ge=0,
        description="Raw count of selected petitions whose realized disposition is "
        "in the grant family (granted / granted-in-part / GVR / summary reversal)",
    )
    realized_granted: int = Field(
        ge=0,
        description="Raw count of grant-family outcomes over every projected "
        "petition — recall's raw denominator",
    )
    weighted_selected: float = Field(
        ge=0.0,
        description="Selected petitions weighted by sample_weight (inverse "
        "inclusion probability, 1 where unasserted), so the figure estimates the "
        "Term's population rather than counting the walked sample's rows",
    )
    weighted_selected_granted: float = Field(
        ge=0.0, description="Grant-family selected petitions, sample_weight-weighted"
    )
    weighted_granted: float = Field(
        ge=0.0,
        description="Grant-family outcomes over every projected petition, "
        "sample_weight-weighted — recall's weighted denominator",
    )
    weighted_population: float = Field(
        ge=0.0, description="Every projected petition, sample_weight-weighted"
    )
    precision: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="weighted_selected_granted / weighted_selected — the realized "
        "grant rate inside the would-have-been-selected slice; null when nothing "
        "was selected (an undefined rate, not zero)",
    )
    recall: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="weighted_selected_granted / weighted_granted — the share of "
        "the Term's realized grants (among projected petitions) the selection "
        "would have covered; null when the projected petitions show no weighted "
        "grant. The denominator includes blind projections, which can never be "
        "selected — for a 'blind-untrusted-cutoff' row that is a reconstruction "
        "failure, not a gate miss, so read the provenance mix beside a low recall",
    )


class SalienceReplay(_Strict):
    """``metrics/salience-replay.json`` — the salience gate replayed over past Terms.

    The current frozen selection code (``salience_version``) run over
    point-in-time reconstructed dockets at successive moments, one cell per
    (Term, cutoff policy). It answers "what would the gate have done then" —
    e.g. that at petition arrival every projected row sits in the baseline band
    and nothing is selected (the gate is degenerate before the docket moves) —
    and gives a full predict/evaluate backtest its population frame. Numbers
    here describe the *gate*, never a predictor: no model ran, so nothing in
    this report is forecasting skill, and the retrospective stratum rule
    applies on top (see ``metrics/README.md``).
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    stratum: Literal["retrospective"] = Field(
        default="retrospective",
        description="Every replayed petition had already resolved when the replay "
        "ran, so the figures measure how the gate would have behaved over known "
        "history, never ex-ante selection quality",
    )
    salience_version: str = Field(
        default="",
        description="The ACTIVE salience-function version — the one the live gate "
        "scores with (e.g. sal-v1). Which version produced any given figure is on "
        "the cell, since the replay runs every registered version",
    )
    salience_versions: list[str] = Field(
        default_factory=list,
        description="Every salience version replayed, active first — the report's "
        "third cell axis beside terms and policies",
    )
    terms: list[int] = Field(default_factory=list, description="The October Terms replayed")
    policies: list[str] = Field(
        default_factory=list, description="The cutoff policies replayed, one cell per Term each"
    )
    cells_evaluated: int = Field(
        default=0, ge=0, description="(Term, policy) cells the replay produced"
    )
    cells: list[SalienceReplayCell] = Field(default_factory=list)


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
    segment_grant_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Grant share of the paid salience-scored segment — the base rate "
        "the predicted slice is judged against (from the statpack's salience-band "
        "section, denial-reweighted); null when that section is absent. With a "
        "salience gate the predicted slice grants far above the whole-docket rate, "
        "so this, not deny_base_rate, is the honest anchor",
    )
    segment_base_rate_cases: int | None = Field(
        default=None,
        ge=0,
        description="Estimated resolved petitions behind segment_grant_rate (weighted)",
    )
    mean_brier_skill: float | None = Field(
        default=None,
        le=1.0,
        description="Mean Brier skill score over the replay stratum's scored cells "
        "(skill vs each case's segment base rate; positive beats the base rate, ~0 "
        "parrots it, negative is worse); null until any replay cell reports one",
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
    process_scope: Literal["frozen", "all"] = Field(
        default="frozen",
        description="Which process versions the scored-cell figures (evaluations, "
        "calibration, per-predictor scores) cover — `frozen` headline by default. "
        "The prediction *census* (`cells.predictions` / `events_predicted`) is "
        "always version-blind, so a frozen scope with many predictions but zero "
        "frozen evaluations is the honest shakedown state, not a mismatch.",
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
    September prediction freeze. Local-install only — the hosted endpoint's
    OAuth flow does not fit headless CI. The transport is a deployment
    concern, not a manifest property: the same pinned package runs over stdio
    (local runs) or as the cells' tokenless localhost HTTP sidecar
    (``fedcourts mcp-serve`` + ``mcp-config --http-url``).
    """

    id: str = Field(
        pattern=r"^[a-z0-9]+$",
        description="Manifest key, e.g. `courtlistener`. Lowercase alphanumeric: the "
        "tool-usage normalizer splits engine-spelled call names (`mcp__<id>__<tool>`) "
        "on this, and an id carrying an underscore or a capital would be mis-split "
        "or missed entirely.",
    )
    package: str = Field(
        description="Pinned installable, e.g. `courtlistener-api-client[mcp]==1.1.0` — "
        "launched via `uvx --from <package> <command>` so no separate install step runs"
    )
    command: str = Field(description="The stdio server entrypoint, e.g. `courtlistener-mcp`")
    token_env: str | None = Field(
        default=None,
        description="Environment variable carrying the server's API token. Unset/empty "
        "at runtime degrades to anonymous rate limits rather than failing the cell.",
    )
    tools: list[str] = Field(
        default_factory=list,
        description="Tool names this pinned version advertises over `tools/list` — the "
        "OFFERED set, recorded because a cell's log can only show what it called. "
        "Belongs with `package` because it is a property of the pin: a version bump "
        "may add or drop tools, so the two move together. Empty means unrecorded, "
        "never 'offers nothing'.",
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
    "claim-scores.json": ClaimScoreBoard,
    "backtest.json": Backtest,
    "usage.json": ModelUsage,
    "ops.json": OpsReport,
    "flags.json": AgentFlags,
    "tooling.json": AgentToolingFeedback,
    "attempt.json": CellFailure,
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
    "claim_score_board": ClaimScoreBoard,
    "backtest": Backtest,
    "tool_usage": ToolUsage,
    "cert_backtest": CertBacktest,
    "salience_replay": SalienceReplay,
    "usage": ModelUsage,
    "ops_report": OpsReport,
    "corpus_validation": CorpusValidation,
    "corpus_scope_audit": CorpusScopeAudit,
    "scope_manifest": ScopeManifest,
    "live_frontier": LiveFrontier,
    "analytics_report": AnalyticsReport,
    "statpack": StatPack,
    "docket": DocketPack,
    "agent_flags": AgentFlags,
    "agent_tooling": AgentToolingFeedback,
    "cell_failure": CellFailure,
    "mcp_server_config": McpServerConfig,
    "retrieval_log": RetrievalLog,
}
