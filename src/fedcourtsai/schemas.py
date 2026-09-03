"""Pydantic models defining the on-disk data contract for the pipeline.

Every artifact committed under ``data/`` — the per-case tree, the scope
manifest, the qp-topic reference set — validates against one of these
models. They are the single source of truth for the data shape and are also
exported to JSON Schema (see ``fedcourts export-schemas``) so that coding
agents and Codex ``--output-schema`` can target them directly.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Final, Literal, get_args

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
    source, and immaterial on the binary axis). That residual covers a label
    normalized from the upstream record's own fields, never a resolution the
    disposition parser itself recorded off order text and got wrong — those
    disagree with their own order text and are converged against it. What
    separates the two is provenance, and the convergence sweep
    (:mod:`fedcourtsai.disposition_convergence`) establishes it two ways: a date
    boundary in code, so that widening snapshot coverage alone cannot reach the
    residual, and — where the docket itself shows that the entry a ``granted``
    was read off no longer parses as a grant at all — that entry, which dates
    the parse gap and so needs no calendar. On mandatory-jurisdiction direct
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
#: leave-one-out in ``pipeline.base_rates.realized_band_rate`` — has to subtract a
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

#: The granted dispositions whose **label alone** names the route the case took
#: out of the cert order: :data:`GRANTED_DISPOSITIONS` less the ones that open a
#: merits proceeding. Named rather than recomputed at each reader because two
#: readers need it — `pipeline.outcome.disposition_route`, which writes the
#: route marker (a GVR and a summary reversal both dispose in the order that
#: grants, while a plain `granted` needs the order text to separate a plenary
#: grant from a summary merits reversal recorded before the `summary-reversal`
#: label existed), and `pipeline.base_rates.summary_route_base_rate`, whose
#: numerator is this set's published count.
CERT_ORDER_DISPOSITIONS: frozenset[Disposition] = (
    GRANTED_DISPOSITIONS - MERITS_PROCEEDING_DISPOSITIONS
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


class MeritsTermination(StrEnum):
    """How a merits proceeding *ended without a disposition* of the judgment below.

    Deliberately not members of :class:`Judgment`, and the distinction is the
    whole point of the vocabulary: these entries say **that** the case is over,
    never **how** the judgment below fared. A voluntary Rule 46 dismissal after
    the grant leaves nothing decided; a case dismissed as moot or abated by the
    petitioner's death ends the same way, for a reason outside the Court; a
    grant the Court itself vacates returns the case to the cert stage; and the
    mandate-analog "Judgment issued." is a clerk's notation on a docket whose
    disposition entry the corpus never captured. Folding any of them into
    ``Judgment`` would fabricate merits ground
    truth twice over: ``judgment_disturbed`` would read it as *undisturbed*
    (a substantive claim about the lower court's judgment that nobody made),
    and the value would enter the predictor-emittable outcome vocabulary as
    something a cell could forecast.

    The members stay separate rather than collapsing into one "terminated"
    marker because they carry different evidence about the *record*: a
    voluntary dismissal, a mootness dismissal, an abatement, and a vacated
    grant are all things the docket says happened, while a rise in
    ``judgment_issued`` means the disposition parser missed an entry that
    exists — a gap to triage, not a docket trend.

    So a termination resolves the corpus row's merits *state* — the case is not
    pending, and the forward-forecast gates must refuse it — while leaving
    ``merits_judgment`` null, which keeps the row out of the statpack's
    ``parsed`` slice and out of the disturbed rate the merits baseline is
    pooled from. Stored in the ``merits_terminated`` column
    (``pipeline/judgment.py`` is the parser).
    """

    voluntary_dismissal = "voluntary-dismissal"
    dismissed_moot = "dismissed-moot"
    abated = "abated"
    grant_vacated = "grant-vacated"
    judgment_issued = "judgment-issued"


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
    #: interim — the application arrives on the docket; cert — the petition
    #: is docketed (the sal-v2 arrival cohort's moment).
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
    period; rows with no date signal share one ``(none)`` bucket. Three of the
    cert-signal dimensions read the live-parsed columns: ``relist_bucket``
    groups by relists (`distribution_count` - 1, floored at 0) into 0 / 1 / 2 /
    3+ buckets, ``cvsg`` by whether the Court called for the views of the
    Solicitor General, and ``fee_class`` by the docket serial's numbering
    stream (paid / IFP); rows the live channel never parsed share one
    ``(unknown)`` bucket on the first two, so parse coverage stays visible.
    ``capital_case`` groups by whether the Court's docket marks the case a
    capital one (``capital`` / ``unmarked``). The flag is latched from
    supremecourt.gov's ``bCapitalCase`` payload field OR-ed with the
    ``*** CAPITAL CASE ***`` annotation the same channel appends to the docket
    number, and no other channel serves either reading, so ``last_live_polled``
    is that column's coverage sentinel: a row the live channel never polled
    shares the same ``(unknown)`` bucket rather than reading as unmarked, which
    would let a coverage gap pass for an absence of capital cases. The
    positive needs no such guard — the column max-latches, so only a writer that
    saw the signal can have raised it.
    ``salience_band`` groups by the active scorer's frozen grant-likelihood band
    over the paid modern-cert petitions — the
    predicted segment — so a case's base rate is its own salience tier's rate.
    ``qp_topic`` groups by the ``qp-topic-v0`` primary label of a case's
    questions-presented text (``docs/qp-topic.md``) — distinct from ``topic``,
    which is the corpus's upstream nature-of-suit column and empty on SCOTUS
    rows. It is read from a labeler's artifact rather than off a corpus row, so
    a section supplies its own key function for it and ``stats`` does not offer
    it as a cut.
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
    capital_case = "capital_case"
    salience_band = "salience_band"
    qp_topic = "qp_topic"


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
    """How far the opinion supports one declared semantic claim — the ``semantic-v1`` grade.

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

    ``semantic-v1`` is **alpha** — provisional, unproven against opinion text,
    and explicitly not a pre-registered commitment in the sense ``cert-v1`` and
    ``merits-v1`` are. No opinion body is ingested, so every grade a cell writes
    today is the mask and nothing published depends on this vocabulary; see
    ``docs/outcome-decomposition.md``, *The semantic family, alpha*.
    """

    supported = "supported"
    partial = "partially-supported"
    unsupported = "unsupported"
    not_addressed = "not-addressed"


# The pre-registration stratum a scored cell belongs to. Defined here, beside
# the models that carry it, so a field can be typed on the closed vocabulary
# rather than on a bare string; `fedcourtsai.integrity` carries the named
# constants and owns `classify_stratum`, the single definition of which cell
# lands where.
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
    stamped_at: datetime = Field(
        description="When the harness stamped the cell (UTC, timezone-aware). "
        "Provenance, and — with the digest — the frozen/alpha partition key: "
        "the digest says which process ran, this stamp says whether it ran at "
        "or after the pre-registration instant. The runner clock is the "
        "witness, bounded independently by the workflow run's own timestamps "
        "and the data commit's date; a naive value reads as pre-freeze."
    )


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
        "corpus payload unmodified — the cell was placed at no cutoff, which is a "
        "case-baseline cell and any cell whose event declares no moment. 'dated' "
        "is a snapshot the docket really served before the cutoff — the strongest "
        "point-in-time evidence, because it also reflects what had not yet been "
        "filed. 'truncated' is a later payload with its post-cutoff entries "
        "removed, which cannot know that a pre-cutoff entry was back-filled "
        "later, and which cuts the dated proceedings only — undated top-level "
        "blocks (counsel, amici, the payload's own generation date) are as at "
        "the pull it was reconstructed from. 'blind' is neither: no moment could "
        "be identified, so the proceedings were removed outright and the cell "
        "saw no trajectory at all "
        "— reachable only from the replay provisioner, the one path that removes "
        "the proceedings key. Recorded so the four can be separated; a figure "
        "pooling them is pooling different information sets",
    )
    cutoff: date | None = Field(
        default=None,
        description="The instant this cell was placed at: entries filed strictly "
        "before it are what the snapshot carries. Non-null wherever a moment "
        "fixed one — a replay cell other than a 'blind' one, and a forward cell "
        "whose event declares a moment whose opening date is that moment's own "
        "trigger — and null where nothing did: a cell provisioned for no "
        "particular event, one whose event declares no moment or records no "
        "opening date, and the cert petition baseline, whose declared moment is "
        "the distribution rather than the docketing its opening date carries. "
        "That makes it the cohort marker those conditionings are separated on. "
        "What it means for retrieval is keyed on `mode`, not on this field: on a "
        "replay cell it is also the leakage clock, and material about the case "
        "dated at or after it postdates what the cell was allowed to see, while "
        "a forward cell may retrieve without restriction and the cutoff bounds "
        "only the baseline it was provisioned with",
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
        description="The active scorer's salience band as at prediction, derived from the "
        "signals above. None when they were unobservable, which is the honest "
        "answer for a cell whose snapshot carried no proceedings — the evaluator "
        "then scores against the terminal band it can derive rather than guessing "
        "a frozen one. A band is readable only beside the `salience_version` "
        "below, which is what the risk-set basis keys on: a band with no version "
        "names a population nothing pins down",
    )
    salience_version: str | None = Field(
        default=None,
        description="Version of the scorer that produced band, and the key the "
        "evaluator's `risk_set` base-rate basis is chosen on: a band name means "
        "something only under the version that assigned it, so a frozen band "
        "whose version is absent — or does not match the statpack's — yields no "
        "baseline rather than a terminal relabel",
    )
    response_requested: bool | None = Field(
        default=None,
        description="Whether the snapshot showed the Court (or a Circuit Justice) "
        "had already requested a response to this application, as at "
        "provisioning — the prediction end of the interim increment pair, whose "
        "resolution end is `Outcome.interim_signals`. Masked by "
        "`signals_observable` exactly as the cert signals above are: one mask "
        "covers both signal families, because a snapshot disclosing no "
        "proceedings discloses neither. Frozen only on an application docket — "
        "null on every cert cell, which declares no claim that reads it, and "
        "whose information set this block is part of",
    )
    referred_to_court: bool | None = Field(
        default=None,
        description="Whether the snapshot showed this application already "
        "referred to the full Court rather than left with a Circuit Justice, as "
        "at provisioning; masked by `signals_observable` like the rest",
    )
    amicus_briefs: int | None = Field(
        default=None,
        ge=0,
        description="Amicus briefs the snapshot's entries recorded as at "
        "provisioning; masked by `signals_observable` like the rest. Unbounded "
        "above, so the increment claim over it is a strict rise with no vacuous "
        "arm — unlike the two flags, which can only rise once",
    )
    term: int | None = Field(
        default=None,
        description="The case's October Term, the leakage guard's key — the cert "
        "Term parsed from a `YY-NNNN` petition number, or the application Term "
        "parsed from a `YYAnnn` application number. Both baselines pool Terms "
        "strictly before it; which pool is keyed on the stage, not on this field",
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
    (``fedcourtsai.pipeline.semantic``): the merits moments declare
    ``semantic-v1``, and the predict prompt asks a merits cell for one
    proposition per declared claim. ``validate`` holds a committed block to that
    declaration, so a block naming an undeclared claim, skipping a declared one,
    or stating one twice fails the cell rather than reaching a grader.
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
        "existed, and on any cell that ran without a provisioned snapshot — a "
        "state run-predict refuses outright, so on that path only older records "
        "carry the gap.",
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
        "reports grades descriptively instead. The merits moments declare "
        "`semantic-v1` and the predict prompt asks a merits cell for it; every "
        "other stage declares no semantic set, so the field stays null there. "
        "Null too on predictions written before the elicitation existed. The "
        "set is mandatory as the mechanical one is, and `validate` holds a "
        "committed block to the declaration.",
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
    distribution_parse: str | None = Field(
        default=None,
        description="The distribution parse the corpus column is declared to hold "
        "when this block freezes — the label a comparable prediction-time count "
        "must have been frozen under, which is what lets the relist-increment "
        "resolver refuse a cross-parse comparison. None on a block written before "
        "the stamp existed; such a block discloses no parse, so the resolver "
        "masks it rather than assigning one from its vintage — an outcome's only "
        "date is the docket's decision date, which says nothing about when the "
        "block was written or under which reading",
    )
    cvsg_date: date | None = Field(
        default=None,
        description="Date the Court called for the Solicitor General's views, or "
        "None for no CVSG — unambiguous here, because the block exists only where "
        "the proceedings were parsed",
    )


class InterimResolutionSignals(_Strict):
    """The interim docket's escalation signals as at resolution, frozen into the outcome.

    The interim twin of :class:`ResolutionSignals`, and a *different* block
    rather than an extension of it: the cert signals (a distribution count, a
    CVSG) are observations nobody makes on an application, and these three are
    observations nobody makes on a petition. Sharing one block would have every
    consumer branch on which half is populated.

    It carries the same two properties that make the cert block scoreable. All
    three signals are **monotone** over an application's life — the Court does
    not un-request a response, un-refer an application, or un-file an amicus
    brief — so a forecast about them is a forecast about an increment, which
    needs the value as at prediction as well: that end is
    ``Prediction.context`` (:class:`PredictionContext`), which carries the same
    three fields. And the corpus columns behind them hold the *current* value,
    not the value at any fixed moment, so copying them onto the outcome at
    resolution is what makes a re-score of the same cell reproduce the same
    number.

    **Deliberately no dates.** The corpus's ``*_at`` columns are moment-minting
    dates read from entry text, and an undated entry is skipped there by rule —
    so they carry a known undercount that the max-latched booleans do not. The
    resolution *value* is the flag; the date's job is opening an event, and it
    keeps it.
    """

    response_requested: bool = Field(
        description="Whether the Court (or a Circuit Justice) had requested a "
        "response by resolution — the interim analogue of a CVSG, and an "
        "affirmative act of attention rather than a rescheduling",
    )
    referred_to_court: bool = Field(
        description="Whether the application had been referred to the full Court "
        "rather than decided by a Circuit Justice alone — the signal the interim "
        "aggregation rule turns on",
    )
    amicus_briefs: int = Field(
        ge=0,
        description="How many amicus briefs the application's docket recorded as "
        "at resolution — a stakes proxy, counted per entry naming amicus or amici "
        "curiae (a multi-filer entry counts once)",
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
    interim_signals: InterimResolutionSignals | None = Field(
        default=None,
        description="The interim docket's escalation signals frozen as at "
        "resolution — the interim twin of `signals`, and never populated "
        "beside it: the two blocks describe different dockets. Present iff the "
        "application was application-parsed (`CorpusRow.application_kind` "
        "non-null is the coverage sentinel for the whole interim signal family, "
        "exactly as `distribution_count` is for the cert one) and every latched "
        "value was observed. Absent means not observed, never observed-as-false",
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
        "value on the grant binary. Null on any outcome off the merits stage, "
        "which has no judgment to record: the field's presence is what routes "
        "the accuracy comparison onto the merits axis, and that routing does "
        "not read the stage",
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
    disposition_route: Literal["plenary", "gvr", "summary-merits"] | None = Field(
        default=None,
        description="How a granted petition's review was routed — whether the "
        "grant resolved the case in the cert order itself rather than by plenary "
        "review. 'gvr' where the order granted, vacated and remanded without "
        "reaching the merits; 'summary-merits' where the judgment rode the grant "
        "order (granted and decided together, so no merits proceeding followed); "
        "'plenary' where review was set for briefing and argument. Null means not "
        "assessed — a denial, an interim outcome, a record disclosing no order "
        "text, or no cert-grant date to measure the gap against — so a committed "
        "outcome never asserts a route nobody read. Deliberately a separate "
        "marker rather than a relabel: `actual_disposition` stays as recorded, "
        "which is what keeps the merits population and every disposition figure "
        "fixed across the field's introduction",
    )
    noted_dissent_from_denial: bool | None = Field(
        default=None,
        description="Whether the denied petition's order text records any noted "
        "dissent from, or statement respecting, the denial — aggregated existence "
        "only, never which Justice. Null means no retained order text was "
        "assessed, which false has to stay distinguishable from: most of the "
        "ledger carries no payload, and reading absence as 'nobody dissented' "
        "would invent an observation, exactly as an absent `signals` block does",
    )


class LeakageAssessment(_Strict):
    """The cross-evaluator's leakage grading of one prediction (a gate on membership).

    The grading half of the leakage doctrine: rather than preventing retrieval,
    the evaluator assesses whether a **replay** predictor retrieved and used
    outcome-revealing material, reading the harness-captured
    ``retrieval_log.json`` (tool calls, query slices, retrieved-document dates)
    beside the predictor's own reasoning. A **forward** prediction was made
    before the outcome existed, so it grades ``not_applicable`` — a claim about
    the cell's design, which a mis-provisioned cell can falsify, and the reason
    the coarse bit is read as an exclusion rather than trusted as a mode label.

    What the grading decides is **membership, never value**: a
    possible/likely verdict sets ``leakage_suspected``, which keeps the cell out
    of every rank key and every scored aggregate
    (``fedcourtsai.integrity.leakage_excluded``; ``metrics/README.md``, *The
    leakage exclusion*), while no score on the record is altered by it.
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
        "baseline's Brier minus the forecast's (`pipeline.base_rates.claim_score`). "
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
        "e.g. 'cert-v2' — the versioned constant in `fedcourtsai.pipeline.claims`, "
        "resolved from the event at stamp time. Two totals are comparable only "
        "under the same version, a different one summing over a different set; "
        "nothing enforces that, so an aggregate reports the versions it pooled "
        "(`declared_set_versions`) and metrics/README.md governs the reading"
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

    **Alpha, and still producing nothing.** ``semantic-v1`` is provisional and
    unproven against opinion text — not a pre-registered commitment in the sense
    ``cert-v1`` and ``merits-v1`` are. The merits moments declare it and the
    evaluate prompt asks a grader for it, but no opinion body is ingested to
    grade against, so every declared claim masks (``not-addressed``) and no
    published number depends on it. Supersession by a set formed with text in
    hand is the expected path, not an exception.
    """

    declared_set_version: str = Field(
        description="The semantic claim-set declaration these rows answer, e.g. "
        "'semantic-v1' — the versioned constant in `fedcourtsai.pipeline.semantic`. "
        "Checked against the declaration and never overwritten: a block "
        "answering another declaration is refused rather than relabelled"
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
    prediction_run_id: str | None = Field(
        default=None,
        description="Run id of the prediction this evaluation graded. "
        "Harness-stamped by the ordinary `stamp-cell --role evaluator` from "
        "the prediction it resolves at stamp time — never the evaluator's "
        "word (an evaluator-written value is overwritten). A re-grade leaves "
        "it untouched, so a predictor re-run between the grading and a "
        "correction cannot re-point the record at a prediction it never "
        "judged; an ordinary re-stamp *does* re-resolve it, which is why a "
        "corrected outcome is routed to `--regrade` and the re-stamp is "
        "reserved for converging gradings that straddle a re-prediction. "
        "Null on records stamped before the field existed; every reader then "
        "falls back to the predictor's latest prediction for the event.",
    )
    created_at: datetime
    correct: int | None = Field(
        ge=0,
        le=1,
        description="1 if the prediction named the right outcome label on the "
        "stage's own axis: the disposition on a cert/interim cell, the judgment "
        "on a merits cell (whose `actual_disposition` is always the "
        "off-vocabulary `other`, so a disposition comparison there would score "
        "every cell against a constant). Harness-stamped **at stamp time** by "
        "`stamp-cell --role evaluator` on **every** stage — cert included, "
        "unlike the skill record beside it — from the scored prediction's "
        "committed label and the outcome's, through "
        "`pipeline.evaluate.is_correct`, and never the evaluator's word: the "
        "comparison needs no pooled baseline and so no salience band to choose, "
        "which is the whole of the cert stage's skill-record exemption. Cleared "
        "to null where either committed artifact is missing — no prediction "
        "from this predictor, or no outcome — so a hand-written bit never "
        "survives that refusal; an unstamped or pre-existing record keeps "
        "whatever it was written with. The leaderboard's accuracy column is its "
        "mean over the cells where it is non-null.",
    )
    brier_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="`(probability - actual_granted)**2` over the stage's declared "
        "binary — granted on a cert or interim cell, judgment-disturbed on a merits "
        "one — computed identically in code by `pipeline.evaluate.brier_score`. Who "
        "owns it splits by stage. On a **merits** or **interim** cell whose "
        "`event.yaml` names that stage it is harness-stamped **at stamp time** by "
        "`stamp-cell --role evaluator` from the scored prediction's committed "
        "`probability` and the outcome's `actual_granted`, never the evaluator's "
        "word, and cleared where either artifact is missing — so the "
        "`segment_base_rate` and `brier_skill_score` stamped beside it share "
        "one source and the skill ratio is verifiable rather than merely "
        "self-consistent. An unstamped cell keeps whatever it was written with. "
        "On a **cert** cell it is the evaluator's, and the "
        "leaderboard's coherence check holds it to the skill recorded against it. "
        "Null where the cell scored no probability and on records written before the "
        "field existed.",
    )
    judgment_correct: int | None = Field(
        default=None,
        ge=0,
        le=1,
        description="1 iff the prediction's `judgment` exactly matches the "
        "outcome's — the merits-axis analogue of `correct`, on the full Judgment "
        "vocabulary (a `reversed` call against a `vacated` outcome is 0). Null "
        "wherever either side records no judgment: every non-merits cell, and "
        "records written before the field existed. **The evaluator's field**, "
        "unlike `correct` beside it — on a merits cell the harness stamps that "
        "bit, the claim block, the base-rate basis record, and the whole skill "
        "record (`brier_score`, `segment_base_rate`, `brier_skill_score`), but "
        "never this one, which no published figure ranks on — computed "
        "identically in code by `pipeline.evaluate.judgment_correct`, which the "
        "offline engines use. Descriptive accuracy, never a "
        "proper score: `brier_score` on the disturbed binary is the scored axis, "
        "and `correct` already carries this same comparison on a merits cell.",
    )
    vote_accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    reasoning_quality: float | None = Field(default=None, ge=0.0, le=1.0)
    leakage_suspected: bool | None = Field(
        default=None,
        description="Coarse leakage bit, kept in step with `leakage`: true when "
        "`leakage.influenced_prediction` is possible/likely. It decides "
        "**membership, never value**: a true bit keeps the cell out of every "
        "rank key and every scored aggregate (`store.stratify` drops it, and "
        "the boards publish the count in their `leakage_exclusion` block), "
        "while no score on this record is altered by it. Null when not assessed "
        "(offline evaluators and records written before the field existed), "
        "which is not a false — an unassessed cell is scored",
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
        "own axis. On a cert cell that is its salience band's grant rate pooled over "
        "statpack Terms strictly before the case's Term, and which band — therefore "
        "which of the two published rates — is recorded in base_rate_basis below; "
        "that choice is a judgment about the scored prediction's frozen band, so the "
        "cert rate is the evaluator's to record. On a merits cell it is instead the "
        "statpack merits section's disturbed rate pooled over grant Terms strictly "
        "before the case's (`pipeline.base_rates.merits_base_rate`), keyed on the "
        "Term certiorari was granted in and harness-stamped by `stamp-cell --role "
        "evaluator` — never the evaluator's word, and cleared where the harness "
        "cannot compute one, so a hand-pooled number never survives the stamp. On an "
        "interim cell it is the statpack interim section's substantive grant rate "
        "pooled over application Terms strictly before the case's own, read off the "
        "scored prediction's frozen context (`pipeline.base_rates.interim_base_rate`) "
        "and harness-stamped the same way, null below that pool's own "
        "pre-registered floor. Neither pooled rate is a salience-band product, so the "
        "stamp clears base_rate_basis and base_rate_salience_version on both. The naive "
        "baseline the prediction's skill is scored against; null on a cert cell from an "
        "offline evaluator, when no prior-Term data exists for the stage's rate, and on "
        "records written before the field existed.",
    )
    base_rate_basis: Literal["risk_set", "terminal"] | None = Field(
        default=None,
        description="Which salience-band population segment_base_rate was taken over. "
        "Null wherever the rate is not a band product — a merits cell's Term-pooled "
        "disturbed rate, and an interim cell's application-Term-pooled grant rate: "
        "an application freezes no band by rule, so there is no band population for "
        "this field to name, and the event's stage axis carries the disambiguation "
        "instead. The stamp clears it on both of those stages, where the rate beside "
        "it is the harness's own pooled number, so the null is structural rather than "
        "a rule an evaluator has to honour. 'risk_set' "
        "pools across every petition that had REACHED the prediction's frozen band — "
        "the population a live cell was actually in, and the right basis wherever the "
        "prediction carries a frozen band under a resolvable salience version. "
        "'terminal' pools across petitions that "
        "ENDED in the band derived from the row now, the fallback where no frozen "
        "band exists (an older cell, or one whose snapshot disclosed no proceedings) "
        "— never a relabel of a frozen band whose version fails to resolve, which "
        "yields no baseline at all. "
        "The two differ several-fold in the weak bands, so a skill score is only "
        "comparable within one basis; absent on evaluations written before the "
        "distinction existed. A cert cell whose scored prediction froze a band "
        "but no resolvable salience version lands with both this field and "
        "segment_base_rate null — the enforced state rather than a permitted "
        "shorthand: `stamp-cell` and `validate` both fail a 'risk_set' basis "
        "that resolves no version, and both equally fail a 'terminal' basis "
        "recorded while the scored prediction froze a band at all — the "
        "fallback taken where a risk-set pairing existed to take.",
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
        "recorded, and cleared outright on every merits and every interim cell, "
        "whose harness-stamped baseline is not a salience-band product and so has "
        "no scorer version to pin; null too on records written before the field "
        "existed.",
    )
    brier_skill_score: float | None = Field(
        default=None,
        le=1.0,
        description="Brier skill score vs `segment_base_rate` "
        "(1 - brier / baseline_brier): ~0 when the prediction merely parrots the "
        "segment base rate, positive when it beats it, negative when worse. On a "
        "merits or interim cell it is harness-derived at stamp time from the "
        "*stamped* brier_score, the outcome, and the stamped `segment_base_rate` — "
        "all three off one set of committed artifacts, so the ratio is correct by "
        "construction rather than merely reproducible from the record; on a cert "
        "cell it is the evaluator's, computed against the band rate it recorded. Null "
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
        "beside any published grade. Written on merits cells, whose moments "
        "declare `semantic-v1`; null on every other stage, which declares no "
        "semantic set, and on evaluations written before the grading existed. "
        "No opinion body is ingested yet, so a written block grades every claim "
        "as `not-addressed` — the availability mask, a property of the record.",
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

    Written per ``run-predict`` / ``run-evaluate`` matrix cell (predictor x event
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
    tooling earns its keep and where to invest next; ``used_corpus_query`` alone is
    also read per run by the ``collect`` job, as the self-reported side of the run
    PR's prior-availability note (the field asks whether the cell *used* the CLI,
    which that note weighs against what capture saw rather than treating as a
    verdict on the corpus). It is the agent's own account —
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


#: What capture read *in* a call's result, decided at parse time from the
#: captured payload — the condition of the answer, beside `result_capture`'s
#: whether-there-was-one.
RetrievalResultStatus = Literal["ok", "throttled", "error", "unobserved"]

# An MCP tool call as the engines spell it: `mcp` then the server and tool,
# separated by either one or two underscores depending on the engine. The tool
# half may itself contain single underscores (`get_endpoint_schema`), so the
# separator is matched greedily-left and the remainder taken whole.
#
# The colon form is the blinding mask's engine-neutral respelling
# (`fedcourtsai.blinding.neutral_tool_class` writes `mcp:<server>:<tool>`,
# because the raw vocabularies are disjoint per engine and would name the
# candidate on the grader's own reading path). A staged log is still a
# `RetrievalLog`, and revalidating one re-derives `throttled_calls` from its
# rows — so a gate that did not know this spelling would silently null a staged
# cell's count and make the blinded view disagree with the committed one about
# a number neither is supposed to change.
_MCP_CALL = re.compile(
    r"^mcp(?:_{1,2}(?P<server>[a-z0-9]+)_{1,2}|:(?P<mserver>[a-z0-9]+):)(?P<tool>.+)$"
)


def normalize_call(tool: str) -> str | None:
    """An MCP call name as ``<server>.<tool>``, or ``None`` if it is not one.

    Engine built-ins (``Bash``, ``run_shell_command``, ``Read``, ``write_file``)
    return ``None``: they are real tool use but they are not what the manifest
    offers, so they are counted separately rather than mixed into the offered
    denominator.

    It lives beside the models rather than in the rollup that reports on them
    because three layers must agree on it and one of them is a model's own
    derivation: capture mints ``RetrievalCall.result_status`` behind this gate,
    :func:`_throttled_calls` denominates behind it, and the corpus rollup
    excludes behind it. Two copies of this predicate would be two definitions
    of what a manifest-tool call is, and the three surfaces would drift apart
    exactly where they are meant to agree.

    Both spellings a committed row can carry are recognized — the engines' own
    and the blinding mask's ``mcp:<server>:<tool>`` — so a staged log
    revalidates to the same count as the log it was masked from.
    """
    match = _MCP_CALL.match(tool)
    if match is None:
        return None
    return f"{match['server'] or match['mserver']}.{match['tool']}"


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
    # Two named states rather than a bool: `false` would read as "returned
    # nothing", which is the very conflation this field exists to end, and the
    # legacy null then sits one typo away from it in any `if not …` test. No
    # third `not_applicable` state, because no call class the parsers emit has
    # a structurally meaningless result — the provider-side ones have results
    # nobody captured, which is what `unobserved` says.
    result_capture: Literal["captured", "unobserved"] | None = Field(
        default=None,
        description="Whether capture saw this call's result at all. `captured` means the "
        "engine log carried the call's result, in a paired result item or on the call "
        "item itself for an engine that settles it there; it does NOT mean the result had "
        "content — an empty result, or a failed one, is still captured. `unobserved` "
        "means no result reached the log: the engine logs none (Gemini's telemetry), "
        "the call ran provider-side and echoed nothing back (a Codex hosted "
        "`web_search_call`), or capture found no result to pair with the call — "
        "the parsers derive the marker from a pairing rule, so a call the engine "
        "logged without a pairing id, and one whose result sits past a truncated "
        "transcript, both land here for a capture-side reason. A row lifted out of a "
        "code-mode program (`call_source` `code_mode_source`) is unobserved by "
        "construction, and on such a log it is the commonest reason of all: the one "
        "combined output belongs to the program, not to any call inside it. "
        "The digests cannot make that distinction on their own — `result_digest` is "
        "null both for a captured-empty result and for one never captured, and so is "
        "`retrieved_doc_date` — which is why a reader who treats a null digest as "
        "`returned nothing` silently mis-grades every unobserved call. Null on "
        "records written before the field existed: capture-unknown, not unobserved.",
    )
    result_status: RetrievalResultStatus | None = Field(
        default=None,
        description="What capture read IN this call's result — decided at parse time from "
        "the captured payload, never the agent's word, and never a judgment about whether "
        "the call was useful. `throttled` means the payload carries the shape the pinned "
        "CourtListener MCP server renders an upstream HTTP 429 as: its tool handler raises "
        "`Rate limit exceeded: HTTP 429: …`, and its citation tools append a `Rate limited "
        "by the upstream API` note to a result the throttle cut short. That is the shared "
        "daily quota turning the cell away rather than the corpus being empty, which is the "
        "one condition a starved run cannot otherwise be told apart from a well-fed one by. "
        "ONLY a manifest-tool (MCP) call can carry it: the text predicate is gated on the "
        "tool name, because the same phrases occur constantly in what a BUILTIN reads — a "
        "cell's own `reasoning.md` describing a throttle it hit, this repository's source, "
        "an evaluator reading the predictor's artifacts — and a builtin echoing prose about "
        "throttling is not the upstream refusing this cell. That gate narrows the text "
        "scanned; it does not make the rest of it safe, because a manifest search tool "
        "returns documents for a living and an opinion may discuss a rate limitation or too "
        "many requests for admission. So each phrase is quoted to something this server "
        "actually emits — the note to its subject (`…by the upstream API`), the reason "
        "phrase to its status code (`429 Too Many Requests`) — and none is a bare `429`, "
        "which inside a legal payload is an ordinary U.S. Reports volume and a docket "
        "number besides. Biased to miss a throttle rather than invent one, so read "
        "`throttled` as a floor. `error` is the engine's OWN structural marker on the "
        "result (a Claude `tool_result` `is_error`, a Codex MCP item's inline `error`) with "
        "no throttle shape. It is NOT gated on the tool name — it is a flag the engine set, "
        "not text a payload can forge, so a failed builtin is honestly an error — and it is "
        "a floor too, since only some engines set one. `ok` is the residual, and it is "
        "wide: captured, no engine error marker, and either not a manifest-tool call at all "
        "or a manifest result with no throttle shape. It is not proof the call succeeded. "
        "`unobserved` mirrors `result_capture` exactly: no result reached the log, so no "
        "condition could be read, which is every Gemini call. Null on records written "
        "before the field existed: condition-unknown, not `ok`. Every status is BAKED AT "
        "PARSE TIME and never recomputed, so a later recalibration of the predicate reaches "
        "only new logs; any rollup pools whatever predicate each log was minted under.",
    )

    call_source: Literal["transcript_item", "code_mode_source"] | None = Field(
        default=None,
        description="Where capture read the CALL itself from — the provenance of the row, "
        "not of its result. `transcript_item` is the ordinary case: the engine logged a "
        "tool-call item and this row is that item. `code_mode_source` means the row was "
        "lifted out of the SOURCE of a freeform code-mode call, which is how a code-mode "
        "engine reaches everything: the model emits one builtin freeform call and invokes "
        "the tools from inside the program it carries — the MCP manifest, and the engine's "
        "own builtins beside it, which is where such a program does most of its work — so "
        "those invocations "
        "never appear as items of their own and are invisible to any count that waits for "
        "one. A lifted MANIFEST row names the same `mcp__<server>__<tool>` spelling a "
        "direct item would, so it normalizes into the offered denominator identically; a "
        "lifted BUILTIN row names the builtin, so like any builtin it falls outside that "
        "denominator and is counted separately. Read every lifted row "
        "differently on the RESULT side: it is ALWAYS `unobserved`, and no "
        "result is read into it. The freeform call returns one combined output for its "
        "whole program and nothing says which part of it belongs to a given call inside "
        "— a single call SITE is not a single invocation (a site inside a loop runs as "
        "many times as the loop), and the output also holds whatever else the program did, "
        "so reading it under a manifest tool's name would put builtin text through the "
        "throttle predicate the tool gate exists to keep it out of. So the lift makes the "
        "CALL visible and claims nothing about its answer: manifest call counts gain a "
        "code-mode engine, the log's capture rate stops reporting a program-driven cell as "
        "fully seen, and the throttle denominator gains nothing. What is counted is CALL "
        "SITES IN PROGRAM TEXT, neither a floor nor a bound on invocations: a site inside "
        "a loop counts once however many times it ran, a site in an untaken branch or a "
        "comment counts though it never ran, and a call reached through an alias or a "
        "computed name is not counted at all. The claim it supports is `the program asked "
        "for these tools`, not an execution trace. "
        "The freeform call keeps its own row beside the lifted ones — a real builtin "
        "invocation, carrying the program and the combined output — so a total over all "
        "rows counts the wrapping call AND the calls it made; count with the MCP "
        "gate (`normalize_call`) to avoid conflating them. This field is also the one the "
        "blinding mask DROPS rather than staging, since naming a row as lifted names the "
        "engine that lifts it. Null on records written before the field existed: "
        "provenance-unknown — and on a code-mode engine's log a null also marks a record "
        "whose calls inside the program were never captured at all.",
    )

    @model_validator(mode="after")
    def _status_agrees_with_capture(self) -> RetrievalCall:
        """Reject a row whose two result markers disagree about capture.

        The states are one fact read twice — a condition can be read exactly
        when a result was captured — so `unobserved` must appear in both fields
        or in neither. Checked rather than derived, because each field is
        written by the same parser pass and a disagreement means that pass is
        broken, not that one field needs refreshing. Only when both are
        present: a null in either is the legacy record's capture-unknown, which
        constrains nothing.
        """
        if self.result_capture is None or self.result_status is None:
            return self
        if (self.result_capture == "unobserved") != (self.result_status == "unobserved"):
            raise ValueError(
                f"result_capture={self.result_capture!r} and "
                f"result_status={self.result_status!r} disagree about whether this call's "
                f"result was captured; `unobserved` belongs in both or neither"
            )
        return self


def _result_capture_coverage(calls: Sequence[RetrievalCall]) -> float | None:
    """The share of marker-carrying calls whose result capture saw a result.

    ``None`` when no call carries ``result_capture`` — an empty log, or one
    written before the marker existed — because zero-of-zero is not a rate and
    ``0.0`` would read as "captured nothing", which is a different claim.

    Over every marker-carrying row, whatever its ``call_source``: a row lifted
    from a code-mode program is unobserved by construction, so a cell that works
    inside programs reads lower here than one calling the same tools as items.
    That is the answer to the question the rate asks, so the denominator stays
    whole; what a reader must not do with it is the field's description's
    business.
    """
    marked = [call for call in calls if call.result_capture is not None]
    if not marked:
        return None
    return sum(1 for call in marked if call.result_capture == "captured") / len(marked)


def observed_mcp_conditions(calls: Sequence[RetrievalCall]) -> list[RetrievalCall]:
    """The manifest-tool calls whose result condition capture could actually read.

    The one denominator behind every throttle figure — this log's own
    ``throttled_calls``, the collect job's per-run note, and the corpus rollup's
    per-engine rate — so the three cannot mean different things by the same
    word. Two exclusions, and each drops calls that could never have shown a
    throttle: a **builtin**, because only a manifest tool talks to the upstream
    whose quota this is, and an **unobserved** result, because a condition
    nobody captured cannot be read. A call predating the marker is excluded on
    the same ground as the second.
    """
    return [
        call
        for call in calls
        if call.result_status is not None
        and call.result_status != "unobserved"
        and normalize_call(call.tool) is not None
    ]


def _throttled_calls(calls: Sequence[RetrievalCall]) -> int | None:
    """How many of this log's manifest-tool calls came back throttled.

    ``None`` when :func:`observed_mcp_conditions` is empty — an empty log, one
    written before the field existed, one whose every result was ``unobserved``
    (a whole Gemini cell), or one that called no manifest tool at all. A
    throttle is only countable where a manifest result reached the transcript,
    so a ``0`` from such a log would assert a clean run out of a blind one; the
    null says the question could not be asked instead.
    """
    observed = observed_mcp_conditions(calls)
    if not observed:
        return None
    return sum(1 for call in observed if call.result_status == "throttled")


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
    result_capture_coverage: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Share of this log's marker-carrying calls whose `result_capture` is "
        "`captured` — the log-level reading of what the grader could see. Derived from "
        "`calls`, never asserted independently, so the rate and the rows cannot "
        "disagree; its denominator is therefore the calls this log *retained*, after "
        "capture's head-cut at the schema's 500-call maximum and after the 16 KiB window "
        "the code-mode lift scans, not every call the cell made. Null when no call "
        "carries the marker: an empty log, or one written "
        "before the marker existed. A 0.0 is a real and different fact — every call ran "
        "with its result unobserved, which is the standing shape of a Gemini cell. "
        "A code-mode cell reads low here BY CONSTRUCTION: every row lifted from a "
        "program's source (`call_source` `code_mode_source`) is unobserved, because the "
        "freeform call returns one combined output for the whole program and nothing "
        "says which part of it belongs to a call inside. That is the honest answer to "
        "the question this field asks — what share of the cell's calls could a reader "
        "see an answer for — so the whole-log rate is the one to compare. What does NOT "
        "carry across engines is reading it as capture QUALITY: for a program-driven "
        "cell the rate is dominated by call shape, and the quantity that separates such "
        "a cell from one calling the same tools as items is its `transcript_item` "
        "SHARE, which belongs beside the rate rather than in place of its denominator. "
        "Restricting the rate to `transcript_item` rows measures something else "
        "entirely — whether the engine's own log paired an output to each item it "
        "emitted, a plumbing check that returns a code-mode cell to 1.0 over its "
        "program wrappers alone. Two more reasons it is not the restriction to make: "
        "`call_source` is null on every row predating the marker, so the filter reads "
        "unknown provenance as excluded; and the blinding mask drops `call_source` "
        "while passing this rate through, so on the one surface where the number "
        "reaches a grader the restriction cannot be performed at all.",
    )
    throttled_calls: int | None = Field(
        default=None,
        ge=0,
        description="How many of this log's MANIFEST-TOOL calls carry `result_status` "
        "`throttled` — the log-level reading of how often the shared upstream quota turned "
        "this cell away rather than answering it. Derived from `calls`, never asserted "
        "independently, so the count and the rows cannot disagree; like "
        "`result_capture_coverage` its denominator is the calls this log RETAINED, after "
        "capture's head-cut at the schema's 500-call maximum. Builtin calls are excluded "
        "on both sides — a `Read` of a document that discusses throttling is not this cell "
        "being throttled — which is the same exclusion the corpus-wide rollup and the "
        "per-run note apply, so the three figures mean one thing. Null when no manifest "
        "call's status records an observed condition: an empty log, one predating the "
        "field, one whose every result was `unobserved`, or one that called no manifest "
        "tool at all. A real 0 is the stronger claim: manifest results were legible and "
        "none of them was a throttle. Read any non-null count as a floor — the per-call "
        "predicate is biased against inventing a throttle, and calls the cell never got to "
        "make are not here at all.",
    )

    # Derives and replaces where `_check_coverage_denominator` raises, because
    # these are recomputable from the rows they summarize while a leaderboard's
    # covered-count is a union the entries alone cannot reconstruct — there, a
    # writer's number is evidence to check; here it is a copy to refresh.
    @model_validator(mode="after")
    def _summaries_follow_the_calls(self) -> RetrievalLog:
        """Derive the capture rate and throttle count from the rows, not a writer's copy.

        Any value supplied is replaced. Recomputing on load reproduces exactly
        what a committed record holds — a log whose calls carry no marker
        derives null, which is what such a record already stores — so this
        reads the ledger without ever rewriting it.
        """
        self.result_capture_coverage = _result_capture_coverage(self.calls)
        self.throttled_calls = _throttled_calls(self.calls)
        return self


class LeaderboardStratum(_Strict):
    """Aggregates over one stratum of a predictor's evaluations.

    A cell is *forward* when the event was still unresolved at the prediction's
    harness clock (`integrity.cell_clock` — the process stamp, else the
    unstamped cell's `created_at`) and *retrospective* when it had already
    resolved — in which case
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
    accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean `Evaluation.correct` over the evaluations that report "
        "one. A cell whose `correct` the stamp could not compute — no readable "
        "prediction, or no committed outcome — leaves both halves of this "
        "fraction rather than entering as a wrong call, so `accuracy_scored` "
        "beside it is the true denominator. Null when no cell in the stratum "
        "reports one, in which case the entry sorts last on this key",
    )
    accuracy_scored: int = Field(
        default=0,
        ge=0,
        description="Evaluations contributing to accuracy — the cells carrying "
        "a non-null `correct`. Below `evaluations` wherever a cell's committed "
        "prediction or outcome was unreadable at stamp time",
    )
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
        "the baseline is the salience segment's grant rate; a merits cell's is the "
        "statpack merits section's guarded disturbed rate pooled strictly "
        "prior (docs/decision-model.md), null below its stated minimum sample",
    )
    skill_scored: int = Field(
        default=0,
        ge=0,
        description="Evaluations contributing to population_brier_skill_score — the cells "
        "carrying a non-null skill score. The figure's true denominator, which "
        "can be far below `evaluations` (a cell scores skill only where a segment "
        "base rate exists), so the figure must be read beside this count. A cell "
        "is also excluded where its recorded skill does not reproduce from its "
        "own inputs, or where a merits cell's recorded rate contradicts the "
        "harness's own pooled merits baseline",
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
        "(`pipeline.base_rates.REALIZED_BAND_RATE_MIN_RESOLVED`) after the "
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
    events_scored: int = Field(
        ge=0,
        description="Distinct (case, event) pairs this predictor was scored on, "
        "pooled across its strata — the numerator of the coverage check the "
        "board-level `events_scored` denominates. Carried on the entry so the "
        "comparison against that denominator is one column read rather than a "
        "sum over three nullable stratum blocks (the sum does reproduce it: a "
        "predictor's strata partition its events). The check is needed because "
        "the scored set is *selected*, not sampled: grading is gated at "
        "`(evaluator, event)` grain, so a prediction committed after a judge "
        "graded its event is never scored by that judge, and an engine whose "
        "cells backfill late accumulates systematically fewer scored events. "
        "Two entries at unequal coverage rank over different populations, and "
        "no figure on this board adjusts for that. Equal coverage is necessary "
        "and not sufficient: it certifies the same event set, never the same "
        "stratum mix or panel depth — read each stratum's `evaluations` and "
        "this entry's `evaluators` beside it (metrics/README.md)",
    )
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
    events_scored: int = Field(
        ge=0,
        description="Distinct (case, event) pairs this predictor was scored on in "
        "this stage — read against the block's own `events_scored`, exactly as a "
        "ranked entry's is read against the board's",
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


def _check_coverage_denominator(
    covered: int, entries: Sequence[LeaderboardEntry | LeaderboardStageEntry]
) -> None:
    """Reject a coverage denominator smaller than an entry it denominates.

    The comparability check reads ``entry.events_scored < covered``, so a
    denominator left below its entries makes every entry look fully covered and
    the check reports "coverage even" — failing **open**, which is the one shape
    a comparability gate must not have. Each entry's events are a subset of the
    population's union, so ``covered`` is at least the largest entry by
    construction; a board that says otherwise was not built from its own cells.
    """
    for entry in entries:
        if entry.events_scored > covered:
            raise ValueError(
                f"events_scored {covered} is below {entry.predictor_id}'s "
                f"{entry.events_scored}: the population's figure is the union "
                "over its entries and cannot be smaller than one of them"
            )


class LeaderboardStage(_Strict):
    """One unranked ``stage@moment`` population, aggregated per predictor.

    A stage is a decision standard (cert / interim / merits — the event
    vocabulary) and a moment is the point in the case's life the forecast was
    taken from, so the pair — not the stage alone — identifies a population.
    Skill figures are only meaningful within one: `granted`
    answers a different question at each stage — the cert segment's is its
    salience band's grant rate, the merits stage's the guarded disturbed rate
    pooled strictly prior (docs/decision-model.md), and the interim stage has
    no published base rate, so its skill stays null. Each
    stage carries its own counts and entries,
    listed by ``predictor_id`` (never ranked), and nothing here blends into the
    cert board or another stage.
    """

    evaluations_total: int = Field(ge=0, description="Evaluations aggregated in this stage")
    events_scored: int = Field(
        default=0,
        ge=0,
        description="Distinct (case, event) pairs any predictor was scored on in "
        "this block — the coverage denominator its entries' own `events_scored` "
        "are read against. A union, never a sum: two predictors scored on the "
        "same event contribute one",
    )
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

    @model_validator(mode="after")
    def _coverage_denominates_its_entries(self) -> LeaderboardStage:
        _check_coverage_denominator(self.events_scored, self.entries)
        return self


class FrozenProcessRecord(_Strict):
    """The freeze constants in force when a board was built.

    ``process_scope: "frozen"`` names a partition whose membership lives in
    code (:mod:`fedcourtsai.process_version`), so without this block a reader
    would have to resolve the build's commit back to the source to see *which*
    digests were blessed and from which instant. Recording them on the board
    itself, the way ``salience_versions`` names the gate, states what was
    blessed at build time — on every build, an ``all``-scope one included, as
    the partition's definition and never a claim it was applied. It records the
    *blessed* set, not the *filter*: only the predictor subset is the enforced
    membership test (``process_version.is_frozen``), while the evaluator
    digests are record-only (timing alone enforced), and this flat list does
    not distinguish the two — that mapping lives in ``process_version``.
    """

    digests: list[str] = Field(
        description="The blessed digest set (`FROZEN_PROCESS_DIGESTS`), sorted — "
        "predictors and evaluators together, exactly as the freeze commit "
        "blessed them. Not a filter: the enforced membership test is the "
        "predictor subset alone, which this pooled list does not distinguish "
        "(see `process_version`)"
    )
    since: datetime | None = Field(
        description="The freeze instant (`FROZEN_SINCE`); null while no freeze is in force"
    )


class ForwardClaimRecord(_Strict):
    """The forward-claim integrity rule in force when a board was built.

    A cell whose harness-written record claims ``mode: forward`` while its
    event had already resolved when the harness ran it is not a forecast
    (:mod:`fedcourtsai.integrity`). This block states what the scoring funnel
    did with such cells and how many there were, so an exclusion can never be
    silent — the same reason ``frozen_process`` records the freeze constants.
    """

    policy: Literal["exclude", "retrospective"] = Field(
        description="What the funnel does with a breaching cell "
        "(`integrity.FORWARD_CLAIM_POLICY`): `exclude` drops it from every "
        "scored stratum; `retrospective` forces it into the retrospective "
        "stratum (procedural still wins for a mootness-basis outcome) while "
        "still counting it. Either way the cell is never a forward "
        "observation. Deliberately stage-blind, like `big_case`: the rule is "
        "a record-integrity property, not a stage-scoped skill figure, so its "
        "counts must never be subtracted from the cert-scoped totals."
    )
    excluded: int = Field(
        ge=0,
        description="How many in-scope cells breached the forward claim this "
        "build — listed under whichever policy applied, so the two variants "
        "publish the same count and a policy flip is visible as exactly that",
    )
    claimed_forward: int = Field(
        ge=0,
        description="The denominator: in-scope cells whose harness record "
        "carries a forward-claiming context at all. A context-null cell can "
        "never breach, so `excluded: 0` over a ledger of context-null cells "
        "means 'nothing recorded a claim to check', not 'every claim held' — "
        "this count is what tells the two apart",
    )
    by_predictor: dict[str, int] = Field(
        default_factory=dict,
        description="Excluded-cell counts keyed by predictor id (only "
        "predictors with a nonzero count appear) — exclusion falling "
        "differentially on one engine changes the scored population, which "
        "is the cross-engine comparability condition, so the split is "
        "published rather than pooled",
    )


class LeakageExclusionRecord(_Strict):
    """The leakage exclusion applied when a board was built, and its count.

    A grading that carries ``leakage_suspected`` says the prediction it scored
    may have read its own outcome, so the cell is not an observation of
    forecasting skill in **any** stratum
    (:func:`fedcourtsai.integrity.leakage_excluded`). This block states how many
    such cells the build dropped, so the exclusion can never be silent — the
    same reason ``forward_claim`` rides beside it. The rule is independent of
    that one and of the timing strata: it changes which cells are counted, never
    what any cell scored.
    """

    excluded: int = Field(
        ge=0,
        description="How many in-scope gradings the leakage bit dropped this "
        "build. Counted over the same collapsed, scope-gated pass that "
        "produced the board's cells, so it is always 'excluded within this "
        "scope' — a shakedown cell dropped from an `all`-scope board is "
        "counted there and on no frozen board. Deliberately stage-blind, like "
        "`forward_claim`: it spans the ranked cert board and every `stages` "
        "block at once, so it must never be subtracted from the cert-scoped "
        "totals beside it",
    )
    assessed: int = Field(
        ge=0,
        description="The denominator: in-scope gradings that recorded the "
        "bit at all (true or false). A null bit is 'not assessed', not 'clean', "
        "so `excluded: 0` over a ledger of null bits means 'nothing was checked' "
        "rather than 'nothing leaked' — this count is what tells the two apart. "
        "Stage-blind and taken before the exclusion, exactly like `excluded` "
        "above and `claimed_forward`, so it is not `evaluations_total`'s "
        "denominator and the two are never divided",
    )
    by_predictor: dict[str, int] = Field(
        default_factory=dict,
        description="Excluded-cell counts keyed by predictor id (only "
        "predictors with a nonzero count appear). Leakage falling "
        "differentially on one engine changes the scored population, which is "
        "the cross-engine comparability condition, so the split is published "
        "rather than pooled",
    )


class Leaderboard(_Strict):
    """``metrics/leaderboard.json`` — predictors ranked from the evaluations ledger.

    A deterministic, offline roll-up of the ``evaluation.json`` files under
    ``data/`` — the newest per (case, event, predictor, evaluator), since a
    re-graded cell commits a second file describing one observation:
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
        "process at or after the freeze instant, graded at or after it too) "
        "or `all` (every version, including the shakedown). A `frozen` "
        "board with zero predictors is the honest 'no frozen-process evaluations "
        "yet' state, not a regression.",
    )
    frozen_process: FrozenProcessRecord | None = Field(
        default=None,
        description="The freeze constants in force at build time — recorded on "
        "every build, an `all`-scope one included, as the partition's "
        "definition and never a claim it was applied; null on a board built "
        "before the record existed, or one constructed without it",
    )
    forward_claim: ForwardClaimRecord | None = Field(
        default=None,
        description="The forward-claim integrity rule applied to this build "
        "and the count of cells it caught (`integrity.forward_claim_breach`); "
        "null on a board built before the record existed, or one constructed "
        "without it",
    )
    leakage_exclusion: LeakageExclusionRecord | None = Field(
        default=None,
        description="The leakage exclusion applied to this build and the count "
        "of cells it dropped (`integrity.leakage_excluded`) — an independent "
        "rule from `forward_claim` beside it, so a cell caught by both is "
        "counted in both and the two counts must never be summed into an "
        "exclusion total; null on a board built before the record existed, or "
        "one constructed without it",
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
    events_scored: int = Field(
        default=0,
        ge=0,
        description="Distinct cert-stage (case, event) pairs any ranked predictor "
        "was scored on — the coverage denominator each entry's own "
        "`events_scored` is read against. A union, never a sum: two predictors "
        "scored on the same event contribute one, so an entry at the board's "
        "figure covers the whole scored set and one below it was ranked over a "
        "subset. Equal coverage certifies the same event set and nothing more — "
        "not stratum mix, not panel depth — so it can refuse a cross-engine "
        "comparison but never bless one (metrics/README.md). Cert-stage like "
        "the counts beside it; a `stages` block denominates its own",
    )
    superseded_gradings: int = Field(
        default=0,
        ge=0,
        description="How many committed `evaluation.json` files the run collapse "
        "dropped while building this board: gradings that passed the scope gate "
        "but lost to a newer grading of the same (case, event, predictor, "
        "evaluator). Re-grading is a maintainer-reachable operation, and with "
        "the collapse in place it leaves no other mark — every count, mean and "
        "correlation here is already post-collapse — so the number is published "
        "beside the standings it could have moved rather than inferred from a "
        "ledger scan. Never subtract it from any count on this board. Its "
        "population is the **scope gate's**, which is this board's process "
        "scope over a slightly wider set of cells: a `frozen` board counts only "
        "supersessions among frozen-scope cells and an `all` board counts them "
        "over every version, but the count is stage-blind (like "
        "`forward_claim` — a superseded grading shares its survivor's stage, so "
        "it spans the ranked board and every `stages` block at once, and must "
        "never be netted against a stage-scoped total) and is taken *before* "
        "the forward-claim exclusion, so a supersession of a cell the exclusion "
        "then drops is counted while the cell reaches no block. The two "
        "agreement views collapse separately, over their own scope, and are not "
        "in this figure. `0` is a measured zero on any board `fedcourts "
        "leaderboard` writes — the command always supplies the count — but a "
        "board built before this field existed also reads `0`, so read it "
        "beside `process_scope` and `evaluations_total`",
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

    @model_validator(mode="after")
    def _coverage_denominates_its_entries(self) -> Leaderboard:
        _check_coverage_denominator(self.events_scored, self.entries)
        return self

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
    frozen_process: FrozenProcessRecord | None = Field(
        default=None,
        description="The freeze constants in force at build time, exactly as "
        "the leaderboard records them — the partition's definition, never a "
        "claim it was applied; null on a surface built before the record "
        "existed, or one constructed without it",
    )
    forward_claim: ForwardClaimRecord | None = Field(
        default=None,
        description="The forward-claim integrity rule applied to this build, "
        "exactly as the leaderboard records it; null on a surface built "
        "before the record existed, or one constructed without it",
    )
    leakage_exclusion: LeakageExclusionRecord | None = Field(
        default=None,
        description="The leakage exclusion applied to this build, exactly as "
        "the leaderboard records it; null on a surface built before the record "
        "existed, or one constructed without it",
    )
    evaluations_total: int = Field(
        ge=0,
        description="Cert-stage evaluation cells in scope (after the "
        "forward-claim exclusion the `forward_claim` block records and the "
        "leakage exclusion the `leakage_exclusion` block records), with or "
        "without a claim block — the surface's population, cert-stage because only "
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

    :func:`fedcourtsai.pipeline.semantic.summarize_semantic_grades` builds it
    from graded units and nothing else — no baseline, no score, no total, and
    ``fedcourts semantic-summary`` is what publishes it. It publishes
    **conditionally**: an artifact is written under ``metrics/`` only where the
    pooled census clears the floor, so no committed artifact carries one today
    and none is required to.

    Two of the rules it publishes under it cannot enforce for itself, because a
    graded unit carries neither label: ``stratum`` and ``process_scope`` are
    the caller's word. Nothing marks a census unpublishable — a null is the
    only signal there is — and an undeclared census is not publishable.

    **Alpha.** ``semantic-v1`` is provisional and unproven against opinion text,
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
    cases: int = Field(
        default=0,
        ge=0,
        description="Distinct cases behind these counts — the **opinions** the "
        "census actually rests on, and the denominator that bounds it. One "
        "opinion backs a cell per predictor per moment, and every claim in the "
        "set is read off that same opinion in one pass, so `units` and even "
        "`cells` can clear a threshold on a single opinion. A reader who wants "
        "to know how much independent reading is behind a share reads this",
    )
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
    null_result_calls: dict[str, int] = Field(
        default_factory=dict,
        description="Calls whose `result_digest` is null, per engine, and ONLY for engines "
        "whose transcript capture records a result side at all (see "
        "`ToolUsageEngine.captures_results`) — an engine that never captures results would "
        "otherwise read as 100% dead ends. Even here a null conflates a genuinely empty "
        "result with one the transcript failed to pair to its call, so read the rate as an "
        "upper bound on the dead-end rate rather than as the rate itself",
    )


class ToolUsageEngine(_Strict):
    """One engine's retrieval profile: what it called, what came back, what it cost.

    The result-side fields exist because a rollup that counts only calls cannot
    see the difference between an engine whose retrieval is observable and one
    whose transcript records the request and drops the answer — and the second
    silently removes that engine's cells from every result-derived reading,
    including the evaluator's leakage grading.

    The throttle fields sit here for the same reason and inherit the same limit:
    a call the upstream quota turned away retrieved nothing, so a run starved of
    it is not comparable with a well-fed one — but only an engine whose results
    reach the transcript can be seen being starved, which is why the rate
    denominates on observed conditions rather than on calls. They are cut per
    engine because that is the grain the ledger has, not because throttling is
    an engine trait: the quota is one bucket every cell of a run draws from, so
    the cut says which cells met the wall, never which engine causes walls.
    """

    engine: str = Field(description="Engine id as the logs record it, e.g. `claude-code`")
    cells: int = Field(default=0, ge=0, description="Retrieval logs this engine produced")
    calls: int = Field(
        default=0, ge=0, description="Tool calls across those cells, MCP and builtin"
    )
    calls_with_result: int = Field(
        default=0,
        ge=0,
        description="Calls carrying a `result_digest` — the result side was captured AND "
        "non-empty. The committed `RetrievalCall` has no capture flag, so this is the only "
        "positive evidence of result capture there is",
    )
    result_observability_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="`calls_with_result / calls`, or null with no calls. TWO states, not "
        "three: a null digest means the result was empty OR was never captured, and the "
        "committed record cannot separate them per call. Read a rate of 0 across thousands "
        "of calls as a capture gap in that engine's transcript rather than as an engine "
        "whose every call came back empty. The denominator is EVERY call, builtins "
        "included, so an engine can score well here on shell output while its MCP results "
        "go uncaptured — `mcp_calls_with_result` is the one that speaks to the manifest",
    )
    mcp_calls_with_result: int = Field(
        default=0,
        ge=0,
        description="The manifest-tool subset of `calls_with_result` — result digests on "
        "normalized MCP calls only",
    )
    captures_results: bool = Field(
        default=False,
        description="Whether any **MCP** call from this engine carried a result digest. "
        "False is the engine-level reading the per-call record cannot give: with no positive "
        "instance the honest conclusion is that the result side is not observable, which is "
        "why the dead-end rows are withheld rather than reported as total. Gated on MCP "
        "calls rather than on any call, because a builtin's result pairing says nothing "
        "about whether the tool transcript this table is about carries results",
    )
    mcp_calls: int = Field(
        default=0,
        ge=0,
        description="Manifest-tool calls this engine made — the `calls` subset that "
        "excludes builtins. Separates the two reasons a result-side figure below can be "
        "empty: an engine that made no MCP call at all, and one that made them and "
        "captured nothing back",
    )
    mcp_calls_with_status: int = Field(
        default=0,
        ge=0,
        description="MCP calls whose per-call `result_status` records an observed "
        "condition — captured, and so legible as throttled or not. The throttle rate's "
        "denominator, and NOT `calls`: an engine whose transcript drops every result "
        "scores 0 here, which is what keeps its throttle count from reading as a "
        "throttle-free engine. 0 also on every log written before the field existed",
    )
    mcp_throttled_calls: int | None = Field(
        default=None,
        ge=0,
        description="The subset of `mcp_calls_with_status` whose result carried the "
        "upstream rate-limit shape — the shared daily quota turning a cell away. Null, not "
        "0, where `mcp_calls_with_status` is 0, matching `mcp_throttle_rate`: a 0 there "
        "would be a count of throttles in a transcript that could not have recorded one. A "
        "floor where it is non-null, twice over: the per-call predicate is biased against "
        "inventing a throttle, and a call whose result was never captured is not counted",
    )
    mcp_throttle_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="`mcp_throttled_calls / mcp_calls_with_status`, or null where no MCP "
        "result of this engine's was legible. Null rather than 0.0 on a capture-blind "
        "engine, because 0.0 there would claim a clean run from a transcript that could "
        "never have shown one. Descriptive of which cells were unlucky, NOT an engine "
        "property to compare across engines: the quota is one shared bucket consumed "
        "run-wide, so which engine's cells meet the wall is a fact about scheduling order "
        "and concurrency, not about the engine",
    )
    mean_calls_per_cell: float = Field(default=0.0, ge=0.0, description="calls / cells")
    median_calls_per_cell: float = Field(
        default=0.0, ge=0.0, description="Median calls per cell — the mean's skew check"
    )
    cells_with_cost: int = Field(
        default=0,
        ge=0,
        description="Cells whose retrieval log has a sibling `usage.json` to join a cost to; "
        "the denominator for the cost fields, which is not `cells`",
    )
    mean_cost_usd_per_cell: float | None = Field(
        default=None,
        ge=0.0,
        description="Mean `estimated_cost_usd` over `cells_with_cost`, or null when none "
        "joined. An estimate from published rates, not a billed figure",
    )
    median_cost_usd_per_cell: float | None = Field(
        default=None, ge=0.0, description="Median of the same joined cells, or null when none"
    )


class ToolUsageCut(_Strict):
    """Cells and calls under one value of a cut — a mode, a role, or an actor."""

    key: str = Field(description="The cut's value, e.g. `forward`, `predictor`, `claude-baseline`")
    cells: int = Field(default=0, ge=0, description="Retrieval logs with this value")
    calls: int = Field(default=0, ge=0, description="Tool calls from those cells, MCP and builtin")
    mcp_calls: int = Field(
        default=0, ge=0, description="The manifest-tool subset of `calls` — builtins excluded"
    )


class ToolUsageCell(_Strict):
    """One cell's call volume beside its cost — the scatter's raw points."""

    case_id: str
    event_id: str = Field(
        description="The forecast moment the cell ran on, from its path — the retrieval log "
        "names only the case, and without it two cells of one case and predictor on "
        "different events are indistinguishable rows"
    )
    run_id: str
    role: str = Field(description="predictor | evaluator")
    actor_id: str
    engine: str
    mode: str = Field(description="The cell's provisioned mode, or `unknown` where unrecorded")
    calls: int = Field(default=0, ge=0, description="Tool calls in this cell's log")
    mcp_calls: int = Field(default=0, ge=0, description="The manifest-tool subset")
    cost_usd: float | None = Field(
        default=None,
        ge=0.0,
        description="`estimated_cost_usd` from the sibling `usage.json`; null where the cell "
        "committed no usage record, which is missing data rather than a free cell",
    )


class ToolUsefulnessSegment(_Strict):
    """Call volume beside forecast skill for one (engine, mode, event kind) segment.

    Descriptive only. Every number carries its own ``cells`` so a reader cannot
    lift a mean off a segment of two.
    """

    engine: str
    mode: str = Field(
        description="The cell's provisioned mode as its own `retrieval_log.json` recorded "
        "it — forward | replay | unknown. The harness's field, not the evaluator's "
        "transcription of it in the leakage block, so the key is a fact rather than a "
        "grading. NOT the leaderboard's `Stratum`: that vocabulary is "
        "forward/retrospective/procedural and is derived from the harness clock against "
        "the outcome, and this surface does not apply the forward-claim exclusion the "
        "scored boards apply, so its `forward` set is the broader one"
    )
    stage: str = Field(
        description="The event's declared decision stage (cert | interim | merits), or "
        "`unknown` for an event the moment registry does not declare. Part of the key "
        "because a cert Brier and a merits Brier score different questions against "
        "different base rates, so pooling them would mix outcome vocabularies into one "
        "meaningless mean"
    )
    moment: str = Field(
        description="The declared forecast moment within that stage, or `unknown`. Keyed "
        "beside the stage rather than folded into it: two moments of one stage answered "
        "from different information sets are two populations, and the event id's kind slug "
        "is too coarse to separate either axis"
    )
    cells: int = Field(
        default=0, ge=0, description="Predicted cells in the segment — the n beside every mean"
    )
    evaluations: int = Field(
        default=0,
        ge=0,
        description="Evaluations behind those cells. Larger than `cells` under "
        "cross-evaluation: several judges score one prediction, and their scores are not "
        "independent observations of it",
    )
    brier_gradings: int = Field(
        default=0,
        ge=0,
        description="The subset of `evaluations` that actually recorded a Brier — the mean's "
        "true denominator, which can sit well below `evaluations`. Read the mean against "
        "this count, never against the evaluation total",
    )
    mean_calls: float = Field(
        default=0.0,
        ge=0.0,
        description="Mean tool calls per cell, MCP and builtin. The x axis the correlation "
        "uses, and neither axis is clean: total calls sweeps in shell and file work that "
        "retrieves nothing, while an MCP-only count would drop the open-web route, which "
        "every engine reaches through a builtin. Read it beside `mean_mcp_calls`. Counted "
        "off the cell's LATEST prediction run, while a grading names no run — so on a "
        "re-run cell these calls may not be the calls the Brier was earned with",
    )
    mean_mcp_calls: float = Field(
        default=0.0,
        ge=0.0,
        description="Mean manifest-tool calls per cell — how much of the volume was the "
        "configured retrieval surface rather than the engine's own builtins",
    )
    mean_brier_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean over cells of each cell's mean Brier across its judges, or null "
        "where no cell in the segment was scored",
    )


class ToolUsefulnessCorrelation(_Strict):
    """One population's call-volume/Brier coefficient, or the refusal to compute it.

    One row per (mode, stage, moment) — the population a coefficient may be taken
    over. There is deliberately **no pooled row**: a tau over forward and replay
    cells together, or over cert and merits together, would blend populations
    whose grades are not comparable, and the pooled number is the one a reader
    would quote.
    """

    mode: str = Field(description="The population's provisioned mode: forward | replay | unknown")
    stage: str = Field(description="The population's decision stage, or `unknown`")
    moment: str = Field(description="The population's declared forecast moment, or `unknown`")
    cells: int = Field(default=0, ge=0, description="Joined cells in this population — the n")
    published: bool = Field(
        default=False, description="Whether the floor was met and a coefficient computed"
    )
    calls_brier_tau: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Kendall's tau-b of (total calls, mean Brier) over this population. Null "
        "whenever `published` is false — withheld, not merely unreported, so no downstream "
        "reader can quote a coefficient the floor refused. Brier is a loss, so a NEGATIVE "
        "tau is the one that would mean more calls beside BETTER forecasts. Engines are "
        "pooled within the row, which confounds it with everything else that differs "
        "between them",
    )
    withheld_reason: str | None = Field(
        default=None,
        max_length=500,
        description="Why no coefficient was published, in prose, or null when one was",
    )


class ToolUsefulness(_Strict):
    """Does retrieval buy accuracy? The denominators, and the refusal to answer yet.

    The question the tool rollup exists to reach, and the one it is furthest from
    answering: whether cells that called more tools forecast better. This block
    publishes the join that would answer it — call volume against Brier, per
    engine, mode, and forecast moment — and, below a pre-declared cell floor,
    publishes no correlation at all. The floor is declared in code
    (``tool_usage.TOOL_USAGE_CORRELATION_MIN_CELLS``) rather than chosen once the
    numbers are in, because a coefficient over a handful of cells is noise that
    reads as a finding, and the reader who most needs the caveat is the one least
    likely to supply it.

    **This is an ops view, not a scored board.** It shares the boards' process
    scope and their one-grading-per-judge collapse, but it does not apply the
    forward-claim exclusion, and it keys its mode on the harness's own record
    rather than on the derived stratum. So its cell population is a superset of
    the leaderboard's and its means are not the board's numbers; a figure here
    that disagrees with a board figure is two populations, not an error in
    either. Nothing here is causal even at full power: engines differ in prompt,
    model, and sandbox as well as in retrieval, and a cell calls more tools
    partly *because* its case is hard.
    """

    process_scope: Literal["frozen", "all"] = Field(
        description="Which process versions the joined cells span. `frozen` (the default) "
        "keeps only cells whose prediction carries a blessed process digest and whose "
        "gradings were stamped at or after the freeze instant; `all` pools every version, "
        "including pre-freeze shakedown cells whose Brier is not comparable to anything. A "
        "grade with no process scope beside it is not readable, which is why this is not "
        "optional",
    )
    min_cells_for_correlation: int = Field(
        ge=1,
        description="The pre-declared floor: below this many cells in a population, that "
        "population publishes no correlation",
    )
    predicted_cells: int = Field(
        default=0,
        ge=0,
        description="Predicted cells the walk found at all — the coverage denominator, so "
        "`joined_cells` reads as a share rather than as a bare count",
    )
    joined_cells: int = Field(
        default=0,
        ge=0,
        description="Predicted cells in scope with both a retrieval log and at least one "
        "evaluation carrying a Brier — the correlations' would-be n",
    )
    joined_evaluations: int = Field(
        default=0, ge=0, description="Evaluations behind those cells, Brier-bearing or not"
    )
    brier_gradings: int = Field(
        default=0,
        ge=0,
        description="The subset of `joined_evaluations` that recorded a Brier — the figure's "
        "true denominator",
    )
    cells_at_call_cap: int = Field(
        default=0,
        ge=0,
        description="Joined cells whose log hit the per-log call cap. Their call volume is "
        "right-censored at the cap, which compresses the top of the correlation's x axis; a "
        "non-zero count means the coefficient understates the spread it was taken over",
    )
    segments: list[ToolUsefulnessSegment] = Field(
        default_factory=list,
        description="The denominator table, engine then mode then event kind",
    )
    correlations: list[ToolUsefulnessCorrelation] = Field(
        default_factory=list,
        description="One row per (mode, stage, moment) population, each gated on the floor "
        "independently. There is no pooled row on purpose",
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
    engine_profiles: list[ToolUsageEngine] = Field(
        default_factory=list,
        description="Per-engine result observability and cost-per-cell, engine-id ordered",
    )
    by_mode: list[ToolUsageCut] = Field(
        default_factory=list,
        description="Cells and calls per provisioned mode (forward | replay | unknown). A "
        "ledger of one mode is the expected reading early on; the cut exists so the "
        "comparison is available the moment the other mode lands",
    )
    by_role: list[ToolUsageCut] = Field(
        default_factory=list,
        description="Cells and calls per stage (predictor | evaluator) — the two roles run "
        "different prompts against the same manifest",
    )
    by_actor: list[ToolUsageCut] = Field(
        default_factory=list,
        description="Cells and calls per predictor/evaluator id, descending by calls",
    )
    cells: list[ToolUsageCell] = Field(
        default_factory=list,
        description="One row per retrieval log: call volume beside joined cost. The scatter "
        "the per-engine means summarize, kept so a reader can check the means against the "
        "spread rather than trust them",
    )
    usefulness: ToolUsefulness | None = Field(
        default=None,
        description="Call volume against forecast skill, with the pre-declared floor below "
        "which no correlation is published. Null on artifacts written before the block "
        "existed — not the same as a floor that was met and found nothing",
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
    reports the same, per salience band, over the paid scored segment (IFP
    petitions are outside it). ``segment_base_rate`` is the mean of the items'
    leakage-safe per-Term band rates (each computed over Terms strictly before its
    own), and ``mean_brier_skill`` the mean skill against them — null when no item
    in the band had a prior-Term base rate.
    """

    band: str = Field(description="The frozen band, in the assigning version's own vocabulary")
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
    human summary, e.g. the row count compared against the baseline. ``passed``
    with a non-zero ``failures`` is a defined state, not a contradiction: the
    count is held within an accepted baseline, or the check is advisory (its
    ``detail`` then leads with ``advisory:``) — a backlog only a data pass can
    clear, reported without holding the verdict red.
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
        description="Inverse inclusion probability the corpus derives for this row; null if none",
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


QpTopicLabel = Literal[
    "administrative-law-and-benefit-programs",
    "business-and-financial-regulation",
    "civil-procedure",
    "constitutional-rights",
    "criminal-law",
    "election-law",
    "employment-and-antidiscrimination",
    "environment-energy-and-property",
    "firearms",
    "first-amendment",
    "habeas-and-postconviction",
    "immigration",
    "intellectual-property",
    "sovereignty-and-foreign-relations",
    "tax",
    "unclassifiable",
]
"""A ``qp-topic-v0`` subject-matter label for a question presented.

The vocabulary is declared and bounded in ``docs/qp-topic.md`` — fifteen
subjects plus ``unclassifiable``, which is reserved for texts with no subject
or no cognizable question present, never for texts that are merely hard to
place.
"""

QP_TOPIC_LABELS: Final[tuple[QpTopicLabel, ...]] = get_args(QpTopicLabel)


class QpTopicReferenceEntry(_Strict):
    """One hand-labeled question-presented text: a case and its primary topic.

    The label is the single mandatory *primary* under the ``qp-topic-v0``
    contract, assigned from the stored ``questions-presented`` text alone — no
    docket context — so any text-only labeler can be scored against it on
    identical input.
    """

    case_id: str = Field(
        description="Canonical ``<court>/<docket>`` id — joins the corpus row and ``data/cases``"
    )
    docket_number: str = Field(
        description="The Court's own docket number (e.g. ``25-52``) — the "
        "human-readable key the labels were recorded against, kept so the set "
        "is reviewable in a diff"
    )
    label: QpTopicLabel = Field(
        description="The primary ``qp-topic-v0`` label; secondaries are not part "
        "of the reference set"
    )


class QpTopicReference(_Strict):
    """``data/qp-topics/qp-topic-reference.json`` — the hand-labeled topic reference set.

    The measurement baseline for any ``qp-topic-v0`` labeler: cases whose stored
    ``questions-presented`` texts were read and labeled by hand against the
    vocabulary in ``docs/qp-topic.md``. A labeler's agreement with this set is
    measured and recorded before anything it produces is published. The set is
    append-only in spirit — relabeling an entry is a judgment change that
    belongs in its own reviewed diff, not a side effect of another change — and
    each ``docket_number`` appears at most once, so the two keys stay a
    verifiable pair. Its selection frame is outcome-conditioned and disclosed
    in ``docs/qp-topic.md``: membership encodes cert outcomes, which is why the
    cell prompts forbid predict/evaluate cells from reading anything under
    ``data/qp-topics/``. Nothing frozen depends on it.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    vocabulary: Literal["qp-topic-v0"] = Field(
        default="qp-topic-v0",
        description="The label vocabulary every entry draws from",
    )
    cases: int = Field(
        default=0, ge=0, description="Number of hand-labeled cases (== len(entries))"
    )
    entries: list[QpTopicReferenceEntry] = Field(
        default_factory=list,
        description="One entry per hand-labeled case, in case_id order",
    )

    @model_validator(mode="after")
    def _canonical(self) -> QpTopicReference:
        if self.cases != len(self.entries):
            raise ValueError("cases must equal len(entries)")
        ids = [entry.case_id for entry in self.entries]
        if ids != sorted(ids) or len(set(ids)) != len(ids):
            raise ValueError("entries must be sorted by case_id and unique")
        return self


class QpTopicLabelEntry(_Strict):
    """One labeled question-presented text: a case, its primary topic, and its optional facets.

    ``secondary`` and ``vehicle`` are recorded but **unpublishable in v0**: the
    reference set carries primaries only, so neither facet has a measured
    agreement, and ``docs/qp-topic.md`` holds both out of every published cut
    until a reference block exercises them. They are written here so the
    judgment survives the run that made it, not so a cut can count them.
    """

    case_id: str = Field(
        min_length=1,
        description="Canonical ``<court>/<docket>`` id — joins the corpus row and ``data/cases``",
    )
    docket_number: str = Field(
        min_length=1,
        description="The Court's own docket number (e.g. ``25-52``) — the second half of the "
        "key pair the extract and reference joins are checked against",
    )
    label: QpTopicLabel = Field(
        description="The primary ``qp-topic-v0`` label: mandatory, single, and the only "
        "field any published count sums over"
    )
    secondary: QpTopicLabel | None = Field(
        default=None,
        description="An advisory second subject for a smuggled question — never counted, "
        "and unpublishable in v0",
    )
    vehicle: bool = Field(
        default=False,
        description="The petition asks for a GVR in light of a named decision; the label is "
        "the underlying subject. Recorded, unpublishable in v0",
    )


class QpTopicLabelAgreement(_Strict):
    """One label's agreement between a labeler and the v0 reference rater.

    Counted over the reference entries carrying this label, so ``n`` is the
    *reference* support, not the labeler's. ``rate`` is withheld below the
    per-label support floor: under it the count is reported and the ratio is
    not, because a single entry moves it by tens of points.
    """

    label: QpTopicLabel = Field(description="The reference label this row counts")
    agree: int = Field(ge=0, description="Compared entries where the labeler assigned this label")
    n: int = Field(ge=0, description="Compared reference entries carrying this label")
    rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="agree / n — agreement with the v0 reference rater, not accuracy. Null "
        "below the support floor, where the label is unmeasured in v0",
    )


class QpTopicTriangleRow(_Strict):
    """One row of the ``constitutional-rights`` / ``criminal-law`` / ``civil-procedure`` matrix.

    The row is a reference label; ``counts`` are the labeler's assignments over
    the same three labels in that fixed order, so ``counts[i]`` of the row for
    label *i* is the diagonal. A labeler label from outside the triangle lands
    in ``other``, which keeps every row summing to ``n`` without widening the
    matrix past the three labels whose boundaries are the error sink.
    """

    reference: QpTopicLabel = Field(description="The reference label this row counts")
    counts: list[int] = Field(
        min_length=3,
        max_length=3,
        description="Labeler assignments in the fixed order constitutional-rights, "
        "criminal-law, civil-procedure",
    )
    other: int = Field(
        ge=0, description="Compared entries the labeler placed outside the three triangle labels"
    )
    n: int = Field(ge=0, description="Compared reference entries carrying this row's label")


class QpTopicAgreement(_Strict):
    """A labeler's measured agreement with the ``qp-topic-v0`` reference raters.

    Every quantity here is **agreement with the reference raters**, never
    accuracy: reference error and labeler error cannot be separated, least of
    all on the boundary labels, and a labeler of the reference raters' own
    model family partly measures shared convention. The reference set's
    two-block, outcome-stratified frame is disclosed in ``docs/qp-topic.md``;
    the pooled rate here spans both streams, and the per-stream split is
    derived at measurement review by joining the reference to the corpus's
    dispositions — deliberately not carried in the committed artifacts. Only
    reference entries the labeler actually covered are compared; the rest are
    counted in ``uncovered``.
    """

    overall_agree: int = Field(ge=0, description="Compared entries where the two labels match")
    overall_n: int = Field(ge=0, description="Reference entries the labeler covered and compared")
    overall_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="overall_agree / overall_n — agreement with the v0 reference rater, not "
        "accuracy. Null when nothing was compared",
    )
    uncovered: int = Field(
        ge=0, description="Reference entries the labeler produced no label for, so unmeasured"
    )
    floor: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="What a constant labeler would score on the same compared entries — the "
        "largest reference class's share. An agreement rate is unreadable without it; the "
        "distance from it is the only part that is skill",
    )
    per_label: list[QpTopicLabelAgreement] = Field(
        default_factory=list,
        description="Per-reference-label agreement, floor-gated, in the vocabulary's own "
        "alphabetical order",
    )
    triangle: list[QpTopicTriangleRow] = Field(
        default_factory=list,
        description="The 3x3 confusion matrix on the constitutional-rights / criminal-law / "
        "civil-procedure triangle, one row per reference label",
    )
    gate_passed: bool = Field(
        description="Overall agreement reached the publication gate **and** the run covered "
        "enough of the reference set to have measured the stream; failing either, a "
        "labeler publishes nothing"
    )


class QpTopicShadow(_Strict):
    """The deterministic shadow rules' standing disagreement with the agent labeler.

    The rules publish nothing and pre-empt nothing: they are a regression
    trip-wire, so a drifting labeler shows up as a moving disagreement rate
    before it shows up in a published cut. **Only the movement is readable, not
    the level**: the rules' precision was measured on the reference set and is
    unmeasured on the labeled stream, which is denial-heavy where the reference
    set is grant-enriched — so a disagreement here is as likely a rule being
    wrong as a labeler being wrong. Compare a run only against another run of the
    same labeler over the same extract.

    ``texts`` is the denominator that makes ``fired`` readable: without it a run
    whose extract covered nothing reports the same clean zeros as a run no rule
    happened to fire on.
    """

    texts: int = Field(
        ge=0, description="Labeled cases the extract supplied a text for — the rules' denominator"
    )
    fired: int = Field(ge=0, description="Of those, texts exactly one shadow rule fired on")
    disagreements: int = Field(
        ge=0, description="Of those, texts where the agent label differs from the rule's label"
    )


class QpTopicLabels(_Strict):
    """``data/qp-topics/qp-topics.json`` — one labeler run's ``qp-topic-v0`` labels.

    The primary label for every question-presented text the labeler read,
    assigned from that text alone, carrying its own measurement: agreement with
    the hand reference set, the triangle confusion matrix, and the shadow rules'
    disagreement rate. The artifact is written only when the agreement gate
    passes, so a labels file on disk is one whose measurement is on the record
    beside it. Labels here are a corpus description, not a prediction claim, and
    nothing frozen reads them. Every published cut drawn from this file carries
    the coverage caveat in ``docs/qp-topic.md``, and neither ``secondary`` nor
    ``vehicle`` may appear in one while the reference set leaves them unmeasured.

    ``gate_passed`` is necessary and **not sufficient** for publication: the
    reference set's frame certifies the grant stream only, and ``docs/qp-topic.md``
    bars every cut until a denial- and GVR-stratified supplement block exists and
    is measured. A cut-builder that reads no further than this file will publish
    too early.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    vocabulary: Literal["qp-topic-v0"] = Field(
        default="qp-topic-v0",
        description="The label vocabulary every entry draws from",
    )
    labeler: str = Field(
        min_length=1,
        description="Who assigned the labels — a free-form actor string (engine and model), "
        "so a measured agreement is attributable to what produced it",
    )
    cases: int = Field(default=0, ge=0, description="Number of labeled cases (== len(entries))")
    agreement: QpTopicAgreement = Field(
        description="This run's measured agreement with the v0 reference rater"
    )
    shadow: QpTopicShadow = Field(
        description="The deterministic shadow rules' firing and disagreement counts"
    )
    entries: list[QpTopicLabelEntry] = Field(
        default_factory=list,
        description="One entry per labeled case, in case_id order",
    )

    @model_validator(mode="after")
    def _canonical(self) -> QpTopicLabels:
        if self.cases != len(self.entries):
            raise ValueError("cases must equal len(entries)")
        ids = [entry.case_id for entry in self.entries]
        if ids != sorted(ids) or len(set(ids)) != len(ids):
            raise ValueError("entries must be sorted by case_id and unique")
        return self


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
    scope_note: str | None = Field(
        default=None,
        description="Scope the boolean flags above cannot express, appended verbatim to "
        "the rendered scope line and carried here so a share quoted out of the JSON keeps "
        "it. Where a population caveat is mandatory for a cut — the `qp-topic-v0` coverage "
        "caveat, say — this is where it travels; None where the flags say everything",
    )
    buckets: list[BaseRateBucket] = Field(default_factory=list)


class TimingStats(_Strict):
    """Duration stats over the resolved cases carrying a usable date pair.

    The pack-level timing keys on ``date_filed`` → ``date_decided`` — docket
    *termination*, pooled across courts and both SCOTUS docket forms, so its
    mixture follows which rows carry a termination date at all; the per-Term
    statistics key on the cert-stage resolution date, which is the petition's own
    moment, and weight each row by its
    ``sample_weight`` (each use states which). The two keys agree on a denied
    petition and diverge on a granted one, whose termination is the merits
    judgment months later. Rows missing either date are
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
    frozen salience band gives each predicted case a base rate conditioned on its
    own grant-likelihood tier. Because the segment lives inside :class:`StatPackTerm`
    it inherits that surface's **per-Term self-selection contract** — a time-masked
    replay cell reads only Terms strictly before its clock, so the rate never leaks
    the current Term. Estimates are sample-weighted (each row counted
    ``sample_weight`` times), matching the Term's other weighted cuts.

    **Two rates, answering two different questions.** A band is monotone
    non-decreasing over a petition's life — the distribution count is max-latched
    and a CVSG date, once set, stays set — so a petition passes *through* the
    weaker bands **it can reach** on its way to the one it ends in. Which those
    are is the scorer's own
    (:meth:`fedcourtsai.pipeline.salience.SalienceScorer.reachable_bands`): under a
    vocabulary that interleaves a fixed-at-filing caption class among the
    trajectory tiers, a petition walks its class's ladder and never enters
    another class's bands.

    ``est_grant_rate`` conditions on the band a petition **ended** in. It is the
    descriptive cut: of the petitions that finished at one distribution, how many
    were granted.

    ``prefix_est_grant_rate`` conditions on having **reached** the band, which is
    the same event as "ended here or stronger *on this petition's own ladder*".
    That is the forecast baseline, because a cell is scored at the band it sat in
    when it ran, and from there the petition may still relist. Conditioning a live
    forecast on the terminal rate would ask it to beat a number computed with
    knowledge of its own future, and understates the honest baseline several-fold
    in the weaker bands (a band with nothing reachable above it has the two
    coinciding exactly).
    """

    band: str = Field(
        description="The frozen grant-likelihood band, in the vocabulary of "
        "the salience version stamped beside it"
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
        "Risk sets nest down one petition class's reachable ladder and partition "
        "across classes, so this contains every stronger band the same class can reach",
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
        "est_grant_rate for a band with nothing reachable above it; "
        "None when the risk set is empty",
    )


class StatPackTermVersionSegments(_Strict):
    """One Term's band slices under a **non-active** salience version.

    A band name means nothing on its own: a ``high`` under one scorer and a
    ``high`` under another are different populations that happen to share a
    label, so the base-rate pool is version-pinned
    (``pipeline.base_rates._pooled_band_rate``). A prediction freezes the version
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
    reweighted. This slice's own ``substantive_grant_rate`` stays **descriptive**
    — it describes the accumulated cohort and, at the pack level, contains every
    Term including a scored case's own. The *scored* interim baseline is built
    from the per-Term entries instead
    (:func:`fedcourtsai.pipeline.base_rates.interim_base_rate`): pooled over
    Terms strictly before the case's, and only where the pooled sample clears the
    pre-registered floor (``docs/salience.md``, *The interim docket*).
    Extensions are counted so the
    docket's administrative dominance is visible, but they never pool into any
    rate — an extension is granted as a matter of course, and admitting it would
    hand the rate the Court's calendar rather than its judgment
    (``docs/salience.md``, *The interim docket*).

    Two denominators, so read each figure against its own. The resolved/granted
    counts cover the machine-matched-resolved subset; the three escalation
    counters below cover **every** substantive application in the slice, pending
    ones included, which makes them right-censored rather than terminal — an
    application still open when the pack was built contributes a "no" it may yet
    reverse. That is one of the reasons no claim baseline is derived from them.
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
    counts with a per-application-Term breakdown; the per-Term entries are what
    the interim segment base rate pools strictly-prior, while the pack-level
    figures beside them stay descriptive. A stage section exists only once its
    corpus feed does: the pack
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
    case's (``pipeline.base_rates.merits_base_rate``), so a skill claim exists
    only once strictly-prior Terms carry parsed judgments — until then the
    figures stay descriptive, and ``metrics/README.md`` governs what may be
    claimed. ``parsed`` against ``granted`` is the
    backfill's own coverage statement, so a thin parse never masquerades as a
    thin docket — read the gap as an upper bound that blends still-pending
    cases (granted, not yet decided), genuine parse gaps, and the proceedings
    that ended with no disposition to parse (``merits_terminated``).
    """

    granted: int = Field(
        default=0,
        ge=0,
        description="SCOTUS cases in this slice whose grant opens a merits "
        "proceeding (a plain or partial grant with `date_cert_granted` set; a "
        "GVR or summary reversal decides in the cert order and is excluded, "
        "as is — label-independently — any row whose parsed judgment carries "
        "its grant's own date, whatever its label says: see "
        "cert_order_excluded). A parsed judgment with no date stays here as "
        "a visible coverage gap, outside the parsed slice, since the gap "
        "test cannot run on it, and so does a row carrying `merits_terminated` "
        "— either a proceeding that ended before anyone reached the merits (a "
        "post-grant Rule 46 dismissal, a dismissal as moot, an abatement on the "
        "petitioner's death, a grant the Court vacated), where there is no "
        "disposition to record, or a bare mandate notation, where the case was "
        "decided and the disposition entry was never captured. Parsed or not",
    )
    cert_order_excluded: int | None = Field(
        default=None,
        ge=0,
        description="Rows the label-independent pool guard removed from this "
        "slice: a parsed judgment dated on or before its own grant rode the "
        "cert order (docs/decision-model.md), so the row is outside granted, "
        "parsed, and the rate alike. Zero is only meaningful beside a "
        "healthy parse: a guard that stops firing and a guard with nothing "
        "to fire on render the same zero, which is why the count is "
        "published rather than implied. Null records a build the guard "
        "never ran on at all — a pack parsed from before the guard existed "
        "must not read as a measurement that it removed nothing, and the "
        "merits baseline refuses to pool from a Term carrying it.",
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
        "per-Term feed (`pipeline.base_rates.merits_base_rate` pools these "
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
    (``pipeline.base_rates.merits_base_rate`` pools them strictly-prior), so the
    ``terms`` array is a scoring input as well as a description. The population
    is the grants that open a merits proceeding — the same rule that mints the
    event a merits forecast is made on — minus, label-independently, any row
    whose parsed judgment is dated on or before its own grant
    (``docs/decision-model.md``'s pool guard), so a GVR, whose vacatur rides
    in the cert order itself, never contributes a near-certain disturbance to
    a rate that scores forecasts about argued cases, whatever its label says.
    Those removed rows are counted in ``cert_order_excluded`` *instead of* in
    ``granted``, so the two partition the merits-opening population and only
    ``parsed`` nests inside ``granted``; a parsed judgment carrying no date
    cannot be gap-tested at all and stays in ``granted`` as a coverage gap.
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


class DocketPackQpTopics(_Strict):
    """The question-presented topic distribution, inseparable from who labeled it.

    A topic share is only readable beside the labeler that produced it and that
    labeler's measured agreement with the ``qp-topic-v0`` reference rater, so the
    two travel in one object rather than as a section a quotation can lift alone.
    ``agree``/``n`` is **agreement, not accuracy**: with a single hand rater,
    reference error and labeler error cannot be separated, and the reference
    frame is grant-enriched, so the figure certifies the grant stream only
    (``docs/qp-topic.md``).

    Three fields exist because the headline rate alone is unreadable. ``floor``
    is what a constant labeler scores on the same entries — the distance from it
    is the only part that is skill. ``uncovered`` is the reference entries the
    labeler never labeled, so ``n`` is not mistaken for the whole reference set.
    ``unmeasured_labels`` names the buckets whose per-label agreement is
    unmeasured in v0 (under the reference support floor), so a row quoted from
    the table is not read as certified by the headline figure.

    ``section`` counts **primary labels only** — secondary labels and the vehicle
    flag are unmeasured in v0 and appear in no published cut — over the labeled
    cases alone, and its ``scope_note`` carries the coverage caveat every
    published share must render beside it.
    """

    labeler: str = Field(
        min_length=1,
        description="Who assigned the labels — the free-form actor string from the labels "
        "artifact, so a quoted share names what produced it",
    )
    agree: int = Field(
        ge=0,
        description="Reference entries where the labeler matched the v0 reference rater — "
        "agreement, not accuracy",
    )
    n: int = Field(
        ge=0,
        description="Reference entries the labeler covered and was compared on — the "
        "denominator of `agree`, which is agreement, not accuracy",
    )
    floor: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="What a constant labeler scores on the same compared entries. An "
        "agreement rate is unreadable without it: on a sixteen-label vocabulary most of "
        "the rate is the floor, and only the distance from it is skill",
    )
    uncovered: int = Field(
        default=0,
        ge=0,
        description="Reference entries the labeler produced no label for, so `n` is not "
        "read as the whole reference set",
    )
    labeled_cases: int = Field(
        default=0, ge=0, description="Cases the labels artifact carries a primary label for"
    )
    matched_cases: int = Field(
        default=0,
        ge=0,
        description="Of those, the ones that joined a row in this section's population — the "
        "cut's raw row count. Far below `labeled_cases` means the labels were produced "
        "against a different corpus vintage, which reads as thin coverage unless both are here",
    )
    unmeasured_labels: list[QpTopicLabel] = Field(
        default_factory=list,
        description="Buckets whose per-label agreement is unmeasured in v0 — fewer reference "
        "examples than the support floor, where one entry moves the ratio by tens of points. "
        "The headline agreement certifies none of these rows",
    )
    section: StatPackSection = Field(
        description="The distribution: labeled cases bucketed by primary `qp-topic-v0` label"
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
    qp_topics: DocketPackQpTopics | None = Field(
        default=None,
        description="The question-presented topic distribution with its labeler provenance, "
        "present only once a labels artifact exists; None while none has been produced, in "
        "which case the rendered document names it among the gaps instead",
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


class DecisionDateConvergenceResult(_Strict):
    """``converge-decision-dates`` result: what the decision-date sweep filled in.

    A denied SCOTUS petition terminates on the order that denies it, so its
    ``date_decided`` is its ``date_cert_denied``; the sweep fills that in on rows
    written before the ingest default carried the date across. Population is the
    denial side only — a granted docket's termination is its later merits
    judgment, which no column on the row holds. ``applied`` is False on a dry run
    (the write set is planned, nothing is written).
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    applied: bool = Field(default=False, description="False on a dry run (no corpus write)")
    candidates: int = Field(
        default=0,
        ge=0,
        description="Denied SCOTUS petitions carrying a denial date but no `date_decided` — "
        "the planned write set, on both a dry run and an apply",
    )
    converged: int = Field(
        default=0, ge=0, description="Rows whose `date_decided` was written; 0 on a dry run"
    )
    sample: list[str] = Field(
        default_factory=list, description="A bounded, id-ordered sample of the write set"
    )


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


class CaptionCensusClass(_Strict):
    """One petitioner class's cell in the caption census: n, grants, rate."""

    petitioner_class: Literal["federal", "state", "private"] = Field(
        description="The committed caption rule's class"
    )
    n: int = Field(ge=0, description="Resolved paid modern-cert petitions in the class")
    grant_family: int = Field(ge=0, description="Grant-family outcomes among them")
    rate: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="grant_family / n, or null on an empty cell — never a fabricated 0",
    )


class CaptionCensusTerm(_Strict):
    """One October Term's caption-class census cells."""

    term: int = Field(description="The October Term year")
    classes: list[CaptionCensusClass] = Field(default_factory=list)
    censored: bool = Field(
        default=False,
        description="True when the Term's frame carries unresolved rows — "
        "right-censored, reported per Term but never pooled; the caveat "
        "travels in the row, not a section away",
    )
    unresolved: int = Field(default=0, ge=0, description="Unresolved frame rows censoring the Term")


class CaptionCensus(_Strict):
    """``caption-census`` result: the artifact a caption carve-in freezes from.

    A deterministic, read-only census of the salience gate's scored segment
    (live-slice, paid, modern-cert, resolved) cut by the committed petitioner
    class rule — per Term and pooled, every cell with its ``n``. Selection
    constants derived from the caption may be frozen only from a statistically
    reviewed run of this artifact under the ``rule_version`` it names
    (``docs/salience.md``); the class is otherwise a reporting dimension.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    rule_version: str = Field(description="The committed rule, e.g. caption-v1")
    corpus_sha256: str = Field(
        default="",
        description="sha256 of the corpus database the census ran over — the "
        "artifact is re-derivable only against this exact corpus state, so a "
        "freeze record must carry it",
    )
    terms: list[CaptionCensusTerm] = Field(default_factory=list)
    pooled: list[CaptionCensusClass] = Field(default_factory=list)


class DistributionBandTransition(_Strict):
    """One cell of the band-transition matrix: how many cases moved from → to."""

    from_band: str = Field(description="The band the baseline parse's count implies")
    to_band: str = Field(description="The band the candidate parse's count implies")
    n: int = Field(ge=0, description="Cases making this transition (diagonal cells are unmoved)")


class DistributionCensusBand(_Strict):
    """One baseline band's distribution-parse deltas — the honest per-band cut.

    Keyed on the band the **baseline** parse's count implies, because that is
    the incumbent reading: the question a reader has is "what share of what this
    parse bands here would move", and the candidate band is the answer, not the
    key. It is the incumbent *reading* of the snapshot, not necessarily the
    label the case carries in the corpus — that comes off the max-latched
    ``distribution_count`` column, which neither side of the census reads. Every
    band of the census's salience version is reported, zero-filled, so an empty
    band reads as measured-empty rather than as a row someone forgot to emit.

    The cut covers the observable frame only: an ``unobservable`` case has no
    count and so no baseline band, and these ``cases`` therefore sum to the
    census's ``cases``, never to its frame. That missing mass is not
    band-random — an unobservable row is one whose proceedings were never
    live-read, the same population the corpus's never-parsed sentinel stands
    for, which bands weak — so the weak bands' denominators are the depleted
    ones and a per-band share is conditional on observability, not a population
    rate. Maturity rides here as it does per Term: a pending docket has had
    fewer conferences to accumulate the ancillary traffic the readings differ
    on, and the bands are built from the conference count, so band and maturity
    are correlated by construction.
    """

    band: str = Field(description="The band the baseline parse's count implies")
    cases: int = Field(
        default=0, ge=0, description="Observable frame cases the baseline parse bands here"
    )
    pending: int = Field(default=0, ge=0, description="Of those, cases carrying no disposition yet")
    count_changed: int = Field(
        default=0, ge=0, description="Of those, cases whose distribution count differs"
    )
    band_changed: int = Field(
        default=0, ge=0, description="Of those, cases whose implied salience band differs"
    )


class DistributionCensusTerm(_Strict):
    """One October Term's distribution-parse deltas, split by docket maturity.

    Maturity is carried per Term because it confounds the trend outright: a
    recent Term is mostly pending, and a pending docket has had fewer
    conferences to accumulate the ancillary traffic the readings differ on. The
    resolved figures are the totals less the pending ones.
    """

    term: int = Field(description="The October Term year")
    cases: int = Field(ge=0, description="Frame cases with an observable distribution count")
    pending: int = Field(default=0, ge=0, description="Of those, cases carrying no disposition yet")
    frame_pending: int = Field(
        default=0,
        ge=0,
        description="Pending cases across the Term's whole frame (`cases + unobservable`) — "
        "the denominator `pending` is not: maturity is a property of the docket and "
        "readability a property of the pull, so neither count may stand in for the other "
        "and which way they diverge is itself a finding",
    )
    unobservable: int = Field(
        default=0,
        ge=0,
        description="Frame cases of the Term with no live snapshot or no disclosed "
        "proceedings — outside `cases`, never counted as agreement; the Term's full "
        "frame is `cases + unobservable`",
    )
    count_changed: int = Field(ge=0, description="Cases whose distribution count differs")
    band_changed: int = Field(ge=0, description="Cases whose implied salience band differs")
    pending_count_changed: int = Field(
        default=0, ge=0, description="Of the count-changed cases, those still pending"
    )
    pending_band_changed: int = Field(
        default=0, ge=0, description="Of the band-changed cases, those still pending"
    )


class DistributionCensus(_Strict):
    """``distribution-census`` result: what re-reading the DISTRIBUTED phrase would move.

    A deterministic, read-only census of two registered distribution parses
    (``pipeline.cert_signals.DISTRIBUTION_PARSES``) over one frame, counted off
    each case's latest **live-shaped** snapshot and banded through one salience
    version's band function. The count is the band's primary feature, so a parse
    change is a change to what every band label means; this artifact is what a
    statistical review reads before any version pins a new parse
    (``docs/salience.md``). Read-only and count-only — it moves no band by
    itself.

    **Conditional, and only the input-level cut.** The corpus
    ``distribution_count`` column, the statpack's per-band base rates, and the
    relist-tier cutpoints were all fitted under the default parse, so this
    matrix holds only if the column is re-derived under the candidate parse;
    pinning a new parse also requires rebuilding the statpack and re-measuring
    the relist-tier rates. Who the gate would actually *fund* is a rank-and-cap
    question read from ``salience-replay``, never from this matrix.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    baseline_parse: str = Field(description="The parse counted as the incumbent, e.g. dist-v1")
    candidate_parse: str = Field(description="The parse counted against it, e.g. dist-v2")
    salience_version: str = Field(
        description="The salience version whose band function derived both bands"
    )
    corpus_sha256: str = Field(
        default="",
        description="sha256 of the corpus database the census ran over — the "
        "artifact is re-derivable only against this exact corpus state, so a "
        "freeze record must carry it",
    )
    cases: int = Field(
        default=0, ge=0, description="Frame cases whose live snapshot discloses a proceedings list"
    )
    unobservable: int = Field(
        default=0,
        ge=0,
        description="Frame cases with no live-shaped snapshot or no disclosed proceedings — "
        "the parses are unreadable there, which is not evidence that they agree",
    )
    frame_pending: int = Field(
        default=0,
        ge=0,
        description="Pending cases across the whole frame (`cases + unobservable`), counted "
        "before observability is decided — the per-Term `pending` counts only the observable "
        "rows, so the two denominators are published side by side rather than one being read "
        "as the other",
    )
    pending: int = Field(
        description="Pending dockets among the observable rows — the numerator the "
        "banner prints beside frame_pending, published so a JSON consumer reads "
        "it directly instead of summing terms[].pending"
    )
    count_changed: int = Field(
        ge=0,
        default=0,
        description="Of the `cases` rows and never of the frame: those whose counts differ",
    )
    band_changed: int = Field(
        ge=0, default=0, description="Of the `cases` rows: those whose implied bands differ"
    )
    count_increased: int = Field(
        ge=0,
        default=0,
        description="Of the count-changed cases, those the candidate parse counts HIGHER — "
        "with `count_decreased` it splits `count_changed` by direction. Zero here is the "
        "observation that the candidate's readings nested inside the baseline's ON THIS "
        "FRAME; that no case could move to a stronger band needs the band function's "
        "monotonicity in the count too, which is a property of the registered version",
    )
    count_decreased: int = Field(
        ge=0, default=0, description="Of the count-changed cases, those the candidate counts lower"
    )
    transitions: list[DistributionBandTransition] = Field(
        default_factory=list,
        description="The band-transition matrix as the FULL band-by-band square, zero-filled, "
        "in band order on both axes — so a zero is a measured zero and never an omitted row. "
        "Which cells a given parse pair can occupy at all is a property of that pair, not of "
        "this artifact: where the candidate's matches are a subset of the baseline's (the "
        "entry-anchored reading against the entry-anywhere one) the count can only fall, and "
        "every registered band function is monotone in the count, so every band-strengthening "
        "cell is zero by construction. `count_increased` observes the nesting on the frame "
        "read; the monotonicity is a property of the registered version. Emitting the square "
        "whole rather than as one triangle is what keeps that orientation-independent — it "
        "flips with the parse arguments",
    )
    bands: list[DistributionCensusBand] = Field(
        default_factory=list,
        description="The per-baseline-band cut, every band of `salience_version` zero-filled, "
        "in band order — the share of each band that moves, in the artifact rather than "
        "recoverable only by joining the changed case ids back against the corpus",
    )
    terms: list[DistributionCensusTerm] = Field(default_factory=list)
    count_changed_case_ids: list[str] = Field(
        default_factory=list,
        description="Every count-changed case, case_id-sorted — complete rather than "
        "sampled, because the review this artifact exists for checks the shifted "
        "dockets one by one",
    )
    band_changed_case_ids: list[str] = Field(
        default_factory=list, description="Every band-changed case, case_id-sorted"
    )


class SalienceUnlatchResult(_Strict):
    """``unlatch-overselected`` result: the one-time latch reconcile's ledger.

    The sticky latch is additive, so a capacity resize leaves every case
    latched under the old caps latched — a standing overhang the live pass can
    never shrink. This deliberate migration recomputes each pending conference
    cohort's selection from scratch under the shipped config and clears the
    latch on pending petitions that recomputation would not pick. ``applied``
    is False on a dry run.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    applied: bool = Field(default=False, description="False on a dry run (no corpus write)")
    version: str = Field(
        default="", description="The salience-function version recomputed under, e.g. sal-v1"
    )
    pending_cohorts: int = Field(
        default=0, ge=0, description="Pending conference cohorts recomputed"
    )
    latched_pending: int = Field(
        default=0, ge=0, description="Latched pending cohort petitions examined"
    )
    retained: int = Field(
        default=0,
        ge=0,
        description="Latched petitions the from-scratch selection keeps (top-N or carve-out)",
    )
    unlatched: int = Field(
        default=0, ge=0, description="Latched petitions cleared (would not be selected today)"
    )
    spared_out_of_scope: int = Field(
        default=0,
        ge=0,
        description="Latched pending petitions left alone because Tier-0 excludes them "
        "(inert under predict_excluded, deliberately not cleared here)",
    )
    spared_undistributed: int = Field(
        default=0,
        ge=0,
        description="Latched pending petitions left alone because they were never "
        "distributed — no cohort exists to recompute them against",
    )
    unlatched_case_ids: list[str] = Field(
        default_factory=list,
        description="Every cleared case id, untruncated — the 1->0 write erases the "
        "corpus's own record of the pre-resize sticky set, so this ledger is it",
    )


class SalienceReplayCell(_Strict):
    """One (Term, cutoff policy, salience version) cell of the salience-gate replay.

    One frozen salience version run over one past Term's resolved paid modern-cert
    petitions, each projected to the state its docket disclosed as at the policy's
    cutoff (see ``fedcourtsai.pipeline.asof``). Selection here is what that
    version's gate *would have* latched at that moment; precision/recall score
    that selection against the realized grant-family outcomes.

    The version is on the **cell**, not the report, so every registered scorer
    replays in a single run. Two versions are comparable because they scored the
    same reconstructed moment; what may differ between them is the scoring
    function and the ``distribution_parse`` the reconstruction's relist count was
    read under, which is why the parse is recorded here rather than inferred —
    versions sharing a parse share one projection, and a version pinning another
    gets its own.
    """

    term: int = Field(description="The October Term whose resolved petitions were replayed")
    salience_version: str = Field(
        default="",
        description="The frozen salience-function version whose scoring, banding, "
        "and selection produced this cell (e.g. sal-v1)",
    )
    distribution_parse: str = Field(
        default="",
        description="The registered DISTRIBUTED reading this cell's distribution "
        "counts were projected under (e.g. dist-v1) — the version's own pin, so a "
        "cross-version comparison can say whether the two saw one reading",
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
        description="Petitions per as-of band in the cell's own scorer vocabulary, "
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

    The visibility half of the leakage doctrine: replay cells run
    with the same tools as forward cells, so the dashboard must show — across
    runs — whether outcome material is reaching a graded cell. Counts are over
    committed ``evaluation.json`` files carrying a
    ``leakage`` block within ``window_days`` of generation; ``likely`` offenders
    are listed (capped) so a repeat pattern names its predictor.

    Deliberately **uncollapsed, all-versions and windowed** — shakedown
    contamination is exactly what it exists to surface, and recency is what
    makes it operational — so it is never the same population as a board's
    ``leakage_exclusion`` count, which is scoped, collapsed and all-time. A
    digest reading zero beside a nonzero board exclusion means the flagged
    gradings fell outside ``window_days``, not that the two disagree; the pair
    is read side by side and never subtracted.
    """

    assessed: int = Field(ge=0, description="Evaluations carrying a leakage assessment")
    not_applicable: int = Field(
        ge=0,
        description="Gradings whose prediction claimed `forward` — the outcome "
        "did not exist when it ran, so the grader had nothing to assess. A claim "
        "about the cell's design, not a finding: a mis-provisioned forward cell "
        "can carry it and still have read its outcome",
    )
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
    """One open issue wearing a ``run:*`` fan-out label, on the ops dashboard.

    Nothing keys on those labels — no workflow triggers on ``issues: labeled``,
    and a predict or evaluate round derives its cases from committed state — so
    an issue carrying one is a marker somebody left behind, never queued work.
    The dashboard lists them with their age so a reader clears them instead of
    reading them as a round in flight.
    """

    number: int = Field(ge=1, description="The issue number")
    label: str = Field(description="The run:* fan-out label, e.g. run:predict")
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
    is the cell count, printed beside every number so a small-N figure cannot
    masquerade as signal — but it is not every number's own denominator:
    ``accuracy`` is a mean over the cells reporting a ``correct``, which
    ``accuracy_scored`` carries and the rendered line prints beside it. ``sample``
    is the ceiling, that count the actual base.

    ``lift_over_always_deny`` is replay accuracy minus the modern-cert
    denial base rate (the accuracy an always-deny predictor would score); null
    until both halves exist. The two are **not** taken over the same set: the
    minuend runs over ``accuracy_scored`` replay cells, the subtrahend over the
    statpack's whole modern-cert slice, so where ``accuracy_scored`` sits below
    ``sample`` the lift is a difference of differently-populated rates — an
    orientation, never an effect size.
    """

    sample: int = Field(ge=0, description="Scored replay evaluations")
    mean_brier: float | None = Field(default=None, ge=0.0, le=1.0)
    accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    accuracy_scored: int = Field(
        default=0,
        ge=0,
        description="Replay evaluations contributing to accuracy — the cells "
        "carrying a non-null `correct`. Below `sample` wherever a cell's "
        "committed prediction or outcome was unreadable at stamp time",
    )
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
    ``reasoning_quality`` grades; ``accuracy`` is the share of correct calls
    over the cells reporting a ``correct`` at all — ``accuracy_scored``, which
    sits below ``evaluations`` wherever the stamp could not compute one — and
    null where none does.
    All strata pooled — the leaderboard remains the stratified reference.
    """

    predictor_id: str
    evaluations: int = Field(ge=0)
    accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    accuracy_scored: int = Field(
        default=0,
        ge=0,
        description="Evaluations contributing to accuracy — the cells carrying "
        "a non-null `correct`. Below `evaluations` wherever a cell's committed "
        "prediction or outcome was unreadable at stamp time",
    )
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
    forward_claim: ForwardClaimRecord | None = Field(
        default=None,
        description="The forward-claim integrity rule applied to the scored-cell "
        "figures, exactly as the boards record it — so the dashboard and the "
        "leaderboard cannot disagree about what was excluded; null on a report "
        "built before the record existed",
    )
    leakage_exclusion: LeakageExclusionRecord | None = Field(
        default=None,
        description="The leakage exclusion applied to the scored-cell figures, "
        "exactly as the boards record it. Distinct from the report's `leakage` "
        "digest, which is an uncollapsed, all-versions, recency-windowed "
        "diagnostic over every leakage grading rather than a count of what this "
        "scope dropped — so a digest reading zero beside a nonzero `excluded` "
        "is the window at work, not a disagreement, and the two are never "
        "equal and never subtracted from one another; null on a "
        "report built before the record existed",
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
        description="Open issues wearing a run:* fan-out label (stale markers), oldest "
        "first; null on a report built before the field existed or without the issue feed",
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
    "qp-topic-reference.json": QpTopicReference,
    "qp-topics.json": QpTopicLabels,
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
    "qp_topic_reference": QpTopicReference,
    "qp_topics": QpTopicLabels,
}
