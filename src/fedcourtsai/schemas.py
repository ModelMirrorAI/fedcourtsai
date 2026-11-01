"""Pydantic models defining the on-disk data contract for the pipeline.

Every artifact committed under ``data/`` — the per-case tree, the scope
manifest, the qp-topic reference set — validates against one of these
models. They are the single source of truth for the data shape and are also
exported to JSON Schema (see ``fedcourts export-schemas``) so that coding
agents and Codex ``--output-schema`` can target them directly.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from datetime import date, datetime, timedelta
from enum import StrEnum
from typing import Annotated, Any, Final, Literal, get_args

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    model_serializer,
    model_validator,
)

from .ids import CASE_ID_PATTERN, EVENT_ID_PATTERN

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
    appeals the convention is grant-side for plenary review, and the
    denied/dismissed side for summary affirmance and dismissal for want of a
    substantial federal question. The resolver reads both sides: the
    vacatur-remand form as ``gvr``, and probable jurisdiction noted — or further
    consideration of jurisdiction postponed to the hearing on the merits, which
    sets the appeal for the same briefing and argument — as ``granted``, which
    opens the merits proceeding a cert grant does; a summary affirmance as
    ``denied``, since the Court declines plenary review and the judgment below
    stands, as on a cert denial; and a dismissal for want of a substantial
    federal question, for want of jurisdiction or as moot as ``dismissed``, the
    Court's own word for an appeal it disposes of without reaching the merits. A
    summary affirmance opens no merits proceeding and latches no merits
    judgment.
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


class MeritsDecisionMethod(StrEnum):
    """**How** the Court decided a granted case — the decision record's form axis.

    Orthogonal to :class:`Judgment`, which says *what* happened to the judgment
    below: the same reversal can arrive as a signed opinion after argument, a
    per curiam after argument, or a summary per curiam in the order that grants
    the petition. The two together carry the stat-pack labels without a second
    disposition vocabulary — a GVR is ``summary-order`` (or ``summary-opinion``)
    beside ``vacated``, a GRR or summary reversal is ``summary-opinion`` beside
    ``reversed``.

    - ``argued-signed``: argued, and decided by an opinion of the Court a named
      Justice delivered.
    - ``argued-per-curiam``: argued, and decided per curiam — including an
      affirmance by an equally divided Court, which the Court issues per curiam.
    - ``summary-opinion``: decided without argument, with an opinion (in
      practice per curiam): a summary reversal, a GRR, a GVR the Court explains.
    - ``summary-order``: decided without argument and without an opinion — the
      ordinary GVR, whose vacatur rides in the order granting the petition.
    - ``dig``: the writ dismissed as improvidently granted, whether before or
      after argument; the argued date beside it says which.

    Read deterministically from the stored docket by
    ``pipeline/decision_record.py``, and stored in the corpus row's
    ``merits_decision_method`` column. None there means unclassified (pending,
    terminated without a disposition, or a decision entry this reader cannot
    place), never an observed absence.
    """

    argued_signed = "argued-signed"
    argued_per_curiam = "argued-per-curiam"
    summary_opinion = "summary-opinion"
    summary_order = "summary-order"
    dig = "dig"


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
    argument = "argument"


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
    #: cert — the Court first relists the petition after a conference considered it.
    relist = "relist"
    #: cert — the Court calls for the Solicitor General's views.
    cvsg = "cvsg"
    #: cert — the Solicitor General files the brief the Court invited.
    sg_brief = "sg-brief"
    #: interim — the application arrives on the docket; cert — the petition
    #: is docketed (the sal-v2 arrival cohort's moment).
    arrival = "arrival"
    #: interim — the Court (or a Circuit Justice) asks for a response to the
    #: application; cert — the Court calls for a response to the petition.
    response_requested = "response-requested"
    #: interim — a response to the application is filed.
    response_filed = "response-filed"
    #: merits — the cert grant opens the proceeding.
    grant = "grant"
    #: merits — the respondent's brief on the merits is filed.
    briefed = "briefed"
    #: merits — the Court posts the transcript of the oral argument.
    argued = "argued"


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
    ``cert_amicus`` groups a cert petition by how many amicus briefs its docket
    recorded before the Court disposed of it (``0`` / ``1`` / ``2+``, from the
    corpus ``cert_amicus_briefs`` column); a row the live channel has not read
    since that column existed shares the ``(unknown)`` bucket. A section supplies
    its key function, and ``stats`` does not offer it as a cut: the column is
    withheld from what a cell retrieves, and ``stats`` is a cell's tool too.
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
    cert_amicus = "cert_amicus"
    salience_band = "salience_band"
    qp_topic = "qp_topic"


class UsageRole(StrEnum):
    """Which agentic stage a usage record belongs to."""

    predictor = "predictor"
    evaluator = "evaluator"


class FlagCategory(StrEnum):
    """What kind of thing an agent flag is about, for maintainer triage.

    ``provisioning`` is a cell's record that lacks something the pipeline should
    have staged; ``capture-gap`` an outcome or docket record that cannot show
    what a forecast or grading needed; ``leakage-disclosure`` a note that
    outcome material about the case reached the cell or a candidate it grades
    (on a replay cell, material postdating its ``context.cutoff``).
    ``blocked`` stays valid for every file that carries it; severity ``blocker``
    is what says a cell could not finish, under whatever category.
    """

    data_quality = "data-quality"
    scope = "scope"
    ambiguous_event = "ambiguous-event"
    provisioning = "provisioning"
    capture_gap = "capture-gap"
    leakage_disclosure = "leakage-disclosure"
    blocked = "blocked"
    other = "other"


class FlagSeverity(StrEnum):
    """How loud an agent flag is. ``blocker`` means the cell could not finish cleanly."""

    info = "info"
    warning = "warning"
    blocker = "blocker"


class FlagSource(StrEnum):
    """Who wrote an agent flag: the cell's agent, or a post-agent harness step.

    A triage label, not an authentication: ``flags.json`` is the agent's own
    file, so nothing stops an agent writing ``harness`` itself. What only the
    harness can say is stamped where no agent writes (``context`` on
    ``prediction.json``, the ``::warning::`` lines in the run log).
    """

    agent = "agent"
    harness = "harness"


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


# Which of the availability mask's three grounds a `not-addressed` grade rests
# on. The grading protocol already requires a grader to say which one applied;
# typing it here makes the answer a counted field rather than a sentence inside
# `SemanticGrade.basis` that only a person auditing a cell can read. The three
# are three different *kinds* of fact, which is the whole reason to separate
# them: `no-judgment` is the case's posture (no body of the required kind was
# ever filed, so the unit could never have been graded and nothing can be
# fetched to change that), `not-ingested` is pipeline debt (a body exists and
# the record does not carry it), and `silent-on-axis` is a finding about what
# the Court wrote. Closed, because a grader that could name a fourth ground
# would be defining the population the census measures.
MaskGround = Literal["no-judgment", "not-ingested", "silent-on-axis"]

# The census bucket for a masked unit whose grades name no ground at all — the
# state of every block graded before the field existed. Named rather than
# spelled at each call site, and deliberately *not* a fourth `MaskGround`: a
# grader may not write it, and a census that folded it into one of the three
# would report a ground nobody asserted.
MASK_GROUND_UNSTATED = "unstated"

# What became of one claim a judge treated as central to a predicted-reasoning
# document (`Evaluation.predicted_reasoning_review`). Three values and closed:
# a claim the outcome bore out, one it did not, and one the staged record
# cannot settle either way — the last never read as a miss.
CentralClaimStatus = Literal["borne-out", "not-borne-out", "unresolved"]


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
        description="What this Justice wrote — where the record's authorship "
        "lives, the opinion's author included. Null means not stated — the record "
        "was written without addressing writing at all, or what the Justice wrote "
        "has no single role (a writing concurring or dissenting only in part, or "
        "two writings of different roles). `none` is the opposite: an "
        "affirmative observation that this Justice wrote nothing, which is what a "
        "final order list or opinion discloses about every participating Justice. "
        "Defaulting to `none` would turn every silent record into that claim",
    )


class GrammarStamp(_Strict):
    """The grammar, and its version, that read a vote record's text."""

    grammar: str = Field(
        description="The grammar's name, e.g. 'scotus-syllabus' "
        "(`pipeline.syllabus_lineup`) or 'scotus-order-notations' "
        "(`pipeline.order_grammars`)"
    )
    version: int = Field(
        ge=1,
        description="The version of `grammar` that produced the reading. A grammar "
        "bumps it whenever it could read the same text differently, so a stored "
        "record says which reading it is and can be re-read after a fix",
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
        description="The registered vote source the list was read from, e.g. "
        "'supremecourt-opinions' (`pipeline.vote_sources`). A string rather than "
        "an enum so the schema holds any record, but `validate` refuses a committed "
        "outcome naming a source that is not registered"
    )
    documents: list[str] = Field(
        default_factory=list,
        description="Every document the record was read from, each a "
        "supremecourt.gov URL: for 'supremecourt-opinions', the one opinion PDF "
        "whose syllabus lineup was read; for 'supremecourt-orders', every order "
        "list, miscellaneous order and opinion relating to orders the Court lists "
        "for the order's date that names the docket. Empty only where a source "
        "reads no document; `validate` refuses a registered source's record "
        "naming none, or one the source does not read",
    )
    grammars: list[GrammarStamp] = Field(
        default_factory=list,
        description="One stamp per grammar that read the record's text, each "
        "with its own version — the syllabus grammar alone for an opinion, the "
        "order-notation and writing-header grammars for an order. Empty only for "
        "a source not read by a grammar; no grammar is stamped twice",
    )
    participating: int = Field(
        ge=QUORUM,
        le=SEATS,
        description="Justices who took part — the aggregation denominator a "
        "threshold counts against, which recusals move. On a partial record it "
        "is the bench the roster seats on the record's date less every Justice "
        "the record observes not taking part",
    )
    complete: bool = Field(
        description="Whether every participating Justice's vote is present. False "
        "means the rest are unobserved, NOT that they abstained. Only a complete "
        "record is scored: `vote_accuracy` is null against any other"
    )

    @model_validator(mode="after")
    def _grammar_stamps_cohere(self) -> VoteProvenance:
        """One stamp per grammar: two versions of one grammar name no one reading."""
        names = [stamp.grammar for stamp in self.grammars]
        if len(set(names)) != len(names):
            raise ValueError("`grammars` stamps a grammar more than once")
        return self


class JusticeWriting(_Strict):
    """One Justice's observed writing role, apart from any vote.

    The unit of :attr:`Outcome.writing_roles`: at the cert and interim stages
    what a Justice wrote is observable for the whole bench while their vote is
    not, so the role cannot ride on a :class:`JusticeVote`, which needs one.
    """

    justice: str = Field(description="The Justice's name, as the roster spells it")
    writing: WritingRole | None = Field(
        description="What this Justice wrote. `none` is the observation that they "
        "wrote nothing; null means they wrote but no single role says what (a "
        "writing concurring or dissenting only in part, or two writings of "
        "different roles)"
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

    ``pipeline_sha`` is deliberately **not** folded into ``digest``: the
    checkout commit changes on every unrelated pipeline edit, and folding it in
    would break the frozen set every time predict/evaluate resume at a newer
    HEAD. The digest captures what defines the process; the sha records which
    commit ran it — provenance, and the side test of every harness boundary
    (``process_version.boundary_side``), which asks whether a change's carrying
    commit is an ancestor of it.

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
        description="Git commit of the pipeline checkout that stamped this cell; NOT part "
        "of `digest`. Provenance, and the side test of every harness boundary: a cell is "
        "after a boundary whose carrying commit is an ancestor of, or equal to, this sha",
    )
    stamped_at: datetime = Field(
        description="When the harness stamped the cell (UTC, timezone-aware). "
        "Provenance, and — with the digest — the frozen/alpha partition key: "
        "the digest says which process ran, this stamp says whether it ran at "
        "or after the pre-registration instant. The runner clock is the "
        "witness, bounded independently by the workflow run's own timestamps "
        "and the data commit's date; a naive value reads as pre-freeze."
    )


class SnapshotContactScrub(_Strict):
    """What the contact scrub withheld from the cell's staged snapshot.

    **Harness-owned.** The staged snapshot carries the scrub only as inline
    placeholders, and a snapshot with none reads the same whether the scrub ran
    and found nothing or never ran. This record is the difference: ``sides``
    names the counsel-block lists the docket was read as self-represented on,
    which is the scrub's trigger, so an empty list says it did not run and a
    non-empty one with zero counts says it ran and withheld nothing. Counts
    only, never a withheld value.
    """

    sides: list[Literal["Petitioner", "Respondent", "Other"]] = Field(
        description="The counsel-block lists on which some served block names "
        "nobody to write to but the filer itself, in petitioner, respondent, "
        "`Other` order. The scrub runs over the snapshot exactly where this is "
        "non-empty; empty means the docket was read as represented throughout "
        "and the staged snapshot is the payload as served"
    )
    blocks: int = Field(
        ge=0,
        description="Counsel blocks that had at least one value withheld. Zero "
        "where `sides` is empty",
    )
    fields: int = Field(
        ge=0,
        description="Values withheld across those blocks, each replaced by "
        "`[contact detail withheld]` or, for a party's prison register number, "
        "`[register number withheld]`. Zero where `sides` is empty",
    )

    @model_validator(mode="after")
    def _counts_follow_the_trigger(self) -> SnapshotContactScrub:
        """A scrub that did not run withheld nothing, and a block counts its values."""
        if not self.sides and (self.blocks or self.fields):
            raise ValueError("`blocks` and `fields` are zero where `sides` is empty")
        if self.blocks > self.fields:
            raise ValueError("`blocks` cannot exceed `fields`: a counted block withheld a value")
        return self


class CertAnchor(_Strict):
    """The cert skill anchor frozen at provisioning: one pool of one statpack build.

    **Harness-owned.** ``provision-snapshot`` pools it for a cert cell whose
    context froze a band, with the scorer's own pooler
    (:func:`fedcourtsai.pipeline.base_rates.prediction_base_rate`) over the
    frozen ``(band, salience_version, term)`` and the ``metrics/statpack.json``
    checked out when the cell was placed. The evaluator stamp reads it in place
    of re-pooling, so a statpack refresh landing between forecast and grading
    does not move the baseline the forecast is scored against — once it has
    checked the record against harness-side inputs, since the file is reachable
    from the cell's workspace: ``statpack_digest`` must name the newest build
    committed by the predict cell's run id, ``lookback_terms`` the window
    configured at that commit, and ``rate`` what that build pools to.
    """

    rate: float | None = Field(
        ge=0.0,
        le=1.0,
        description="The risk-set band rate pooled at provisioning. Null where no "
        "strictly-prior Term inside the window carries the frozen band under its "
        "version, or the context froze no version or Term beside the band: the "
        "cell then has no baseline, which the stamp records as a null rate",
    )
    statpack_digest: str = Field(
        description="`pipeline.base_rates.statpack_digest` of the statpack build "
        "the rate was pooled from (`sha256:` over the parsed pack's canonical JSON)"
    )
    lookback_terms: int = Field(
        ge=0,
        description="The `salience.base_rate_lookback_terms` window the rate was "
        "pooled under (0 = no window)",
    )


class PredictionContext(_Strict):
    """The conditioning state a predict cell actually ran against.

    **Harness-owned.** Written by ``provision-snapshot`` and copied onto the
    prediction by ``stamp-cell``, exactly like ``process_version`` and
    ``usage.json`` — never the agent's word. That matters here more than
    elsewhere: ``input_snapshot`` is the agent's own string and is written
    several ways across the committed set, with some cells naming no path at
    all, so it cannot carry a scoring input.

    The agent's string is not *nothing*, though: it is the cell's own account of
    which snapshot it read, and where it disagrees with the file the harness
    provisioned, the block and the cell are describing different information
    sets. ``stamp-cell`` compares them — both sides normalized to the provisioned
    file's day — and records the answer in ``snapshot_uptake``, which is the only
    field here the cell's word decides.

    That one field reports; it does not mask. What the rest of the block records
    is what **provisioning** derived and offered, which is a fact about the
    record whether or not a given cell took it up — so a reader wanting the
    cell's own information set reads the two together, and every scoring surface
    reads the conditioning exactly as it did before the field existed.

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
    snapshot_date: date = Field(
        description="Date of the snapshot the harness provisioned for this cell, "
        "and the day its file is named for. Whether the cell went on to read it "
        "is `snapshot_uptake`, not this field"
    )
    snapshot_provenance: Literal["as-stored", "dated", "truncated", "blind"] = Field(
        default="as-stored",
        description="How the provisioned snapshot was obtained. 'as-stored' is the "
        "corpus payload unmodified — the cell was placed at no cutoff, which is a "
        "case-baseline cell and any cell whose event declares no moment. 'dated' "
        "is a snapshot the docket really served before the cutoff — the strongest "
        "point-in-time evidence, because it also reflects what had not yet been "
        "filed — with one exception, recorded in `cut_kind`: an arrival-position "
        "cut is taken on a 'dated' payload too, because a snapshot the docket "
        "served on the opening day itself can carry that day's later entries. "
        "'truncated' is a later payload with its post-cutoff entries "
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
    snapshot_uptake: Literal["read", "unread"] | None = Field(
        default=None,
        description="Whether the cell's own `input_snapshot` named the snapshot the "
        "harness provisioned. Judged by `stamp-cell`, which normalizes both sides to "
        "the provisioned file's day, so the several spellings the field carries "
        "across the committed set all read as agreement. 'read' is agreement — the "
        "cell's SELF-REPORT that it read that file, never verified uptake. 'unread' "
        "is a cell that reported no snapshot, or named a different one, while the "
        "provisioned file sat on disk: it says the forecast may have been formed "
        "without the baseline every predictor is supposed to share, which is the one "
        "thing the rest of this block cannot say. Null where the stamp could not "
        "judge: a record stamped before the comparison existed, or a context with no "
        "provisioned snapshot file beside it to compare against. **It masks "
        "nothing.** The fields beside it stay as provisioning derived them, because "
        "they are not all payload-uptake facts — `band` and `salience_version` reach "
        "the cell through `record/context.json`, a different file, and are the "
        "population label the evaluator prices the cell against rather than an input "
        "it conditions on; nulling them would move the cell to the `terminal` basis, "
        "which is the band re-derived at evaluation. So this field reports, and "
        "every scoring surface goes on reading the same conditioning it did before",
    )
    cutoff: date | None = Field(
        default=None,
        description="The day this cell was placed at. It is the snapshot's outer "
        "bound, not on its own the boundary: entries filed strictly before it "
        "are what the date rule admits, and `cut_kind` says whether a second, "
        "tighter rule ran inside that — on an arrival-position cut the snapshot "
        "stops at the opening entry, so the opening day's own later entries are "
        "outside the cell's information set although this date admits them. "
        "Non-null wherever a moment "
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
    cut_kind: Literal["date", "arrival-position"] | None = Field(
        default=None,
        description="Which rule bounded the provisioned snapshot's entries. 'date' "
        "keeps every entry filed strictly before `cutoff`, which is the whole of "
        "the boundary for every moment whose trigger is not itself a docket entry. "
        "'arrival-position' is that rule and an anchor bound: the snapshot is the "
        "docket as of the entry that opened the event, so the opening day's own "
        "later entries — a same-day referral, response request, amicus filing or "
        "disposition — are outside the cell's information set even though "
        "`cutoff` admits their date. Taken on the interim arrival moment, where a "
        "whole application can be submitted and disposed of inside one day, and "
        "on both snapshot provenances. Null where no moment fixed a cutoff. This "
        "field, not `cutoff` alone, is the leakage clock's boundary on a replay "
        "cell: material dated on the cutoff's own eve is inside the set under "
        "'date' and may be outside it under 'arrival-position', which "
        "`cut_anchor_index` locates",
    )
    cut_anchor_index: int | None = Field(
        default=None,
        ge=0,
        description="Where the opening entry sat in the proceedings list the cut was "
        "taken over — a 0-based position in the PRE-cut list, so it is a record of "
        "the boundary rather than an index into the provisioned snapshot. Non-null "
        "exactly where `cut_kind` is 'arrival-position'; a cell whose opening entry "
        "could not be located there is refused rather than provisioned on the date "
        "rule, so there is no arm carrying the kind without the index",
    )
    decided_before: str | None = Field(
        default=None,
        description="This cell's **docket-number Term**, and the one anchoring "
        "clock: the statpack's and docket pack's per-Term rows may be read only "
        "for Terms strictly preceding it. Those rows are keyed on the "
        "docket-number Term, so this case's own Term row already contains its "
        "disposition — which is why the clock is the docket Term and not the "
        "Term the cutoff falls in, deliberately conservative for a petition held "
        "over into a later Term. This is also what the cell was handed as "
        "DECIDED_BEFORE, and what it passed to `fedcourts query`. The day-level "
        "retrieval boundary is `cutoff` beside it, which is what REPLAY_CUTOFF "
        "carries on a dated or truncated cell and what narrows that query further. Null on a "
        "forward cell, whose outcome does not exist yet",
    )
    signals_observable: bool = Field(
        description="Whether the payload disclosed a proceedings list at all. False "
        "means the docket-progress signals below are UNOBSERVABLE from what the cell "
        "saw, not that they are zero — a redacted replay snapshot drops the "
        "proceedings wholesale, and reading that absence as 'never distributed' "
        "would invent a fact. A property of the PAYLOAD: a cell that did not report "
        "reading the payload leaves this alone, since what the payload disclosed is "
        "unchanged by that — `snapshot_uptake` is where the uptake is recorded"
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
    band_refused: Literal["outside-segment"] | None = Field(
        default=None,
        description="Why the band freeze refused a band the signals could otherwise "
        "have given. 'outside-segment' is a cert row the scorer active at "
        "provisioning leaves out of its segment (a Rule 20 writ under a version "
        "that excludes them, read off the payload's opening petition entry): "
        "that version neither scores nor selects the row, so `band` and "
        "`salience_version` are null while `signals_observable` stays true and "
        "the signals above are frozen as usual. Null wherever no such refusal "
        "happened: a frozen band, an unobservable docket (`signals_observable` "
        "false), an application docket (which takes no band by rule), and every "
        "context written before the field existed",
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
        "provisioning — the interim reading (accepted-form entries plus each "
        "distinct lead filer still docketed as submitted), over "
        "the entries this cell's own `cut_kind` rule kept. Under `date` that is "
        "everything filed strictly before `cutoff`, so the opening day is "
        "included and this end agrees with the outcome's end-of-disposition-day "
        "bound about it; under `arrival-position` the opening day's later entries "
        "are excluded here and counted there, which biases the increment claim "
        "upward. Masked by `signals_observable` like the rest. Unbounded above, "
        "so the increment claim over it is a strict rise with no vacuous arm — "
        "unlike the two flags, which can only rise once. **Frozen once written, "
        "and never re-derived**, so it may carry an older reading than the "
        "`Outcome.interim_signals` end it is compared against: a corpus "
        "re-derivation moves the resolution end alone, and neither end carries a "
        "reading stamp, so the record does not disclose whether an "
        "`amicus-increment` pair is comparable. Where the two ends may straddle a "
        "re-derivation, read a rise as a forecast hit only once the entry that "
        "moved the count is shown to postdate this cell's own anchor; "
        "`docs/freeze-record.md` dates the re-derivations",
    )
    term: int | None = Field(
        default=None,
        description="The case's October Term, the leakage guard's key — the cert "
        "Term parsed from a `YY-NNNN` petition number, or the application Term "
        "parsed from a `YYAnnn` application number. Both baselines pool Terms "
        "strictly before it; which pool is keyed on the stage, not on this field",
    )
    vide_links: list[str] | None = Field(
        default=None,
        description="The docket numbers the provisioned payload links as `Vide` in "
        "its `RelatedCaseNumber` list — a cross-petition, a companion, or the "
        "petition this one is held for — normalized, in the Court's order, the "
        "docket's own number dropped and the list stopped at the provisioner's "
        "staging bound. Read off the payload the cell was placed on, so it names "
        "only the links that payload carries; the list is undated, so a "
        "`truncated` payload carries the latest one. Empty where the payload "
        "carries the live channel's `CaseNumber` and links nothing; null where it "
        "carries none, the REST shape, which serves no such list. What a board's "
        "`by_link` cut files the cell under",
    )
    paper_only_filings: bool | None = Field(
        default=None,
        description="Whether the provisioned payload puts the docket's party filings "
        "on paper only: it carries the Court's Rule 34.6 / Paragraph 9 entry "
        "(filings 'submitted in paper form only'), with no later entry quoting the "
        "rule to call for electronic versions once briefing and argument are "
        "scheduled. The Court posts nothing behind such filings, so the cell's "
        "`record/documents/` lacks them for a reason no fetch reaches, and their "
        "absence is not a provisioning failure. Read in docket order off the payload "
        "the cell was placed on, so a `truncated` payload answers as at its cut. "
        "False where the proceedings carry neither entry or the lift follows; null "
        "where the payload carries no live `ProceedingsandOrder` list (the REST "
        "shape, or a cut that dropped it)",
    )
    snapshot_contact_scrub: SnapshotContactScrub | None = Field(
        default=None,
        description="What the contact scrub withheld from the staged snapshot "
        "this cell reads: the self-represented sides it keyed on and the blocks "
        "and values it replaced with placeholders. A placeholder in "
        "`record/snapshot` is the pipeline's, not the docket's. Null where the "
        "provisioner runs no snapshot contact scrub (the cert back-test, which "
        "redacts its snapshot by its own rule) or the cell predates the record",
    )
    cert_anchor: CertAnchor | None = Field(
        default=None,
        description="The cert skill anchor pooled when the cell was placed: the "
        "risk-set rate over the frozen band, version and Term, and the statpack "
        "build and lookback window it was pooled under. A cert grading stamped from "
        "proc-v15 on takes its segment_base_rate, base_rate_statpack_digest and "
        "base_rate_lookback_terms from here rather than from the statpack checked "
        "out at grading, so a metrics refresh between forecast and grading leaves "
        "the anchor where it was. Null on a cell of any other stage, on a cert cell "
        "that froze no band, where no statpack was readable at provisioning, and "
        "on cells placed before the record",
    )

    @model_validator(mode="after")
    def _cut_fields_cohere(self) -> PredictionContext:
        """The boundary fields travel together or not at all.

        `cut_kind` names the rule that bounded the snapshot at `cutoff`, so a
        kind over a null cutoff asserts a bound no moment fixed; and the anchor
        index is the record of exactly the `arrival-position` rule, per its own
        no-arm-without-the-index contract. Both directions are producer bugs a
        grader would otherwise be sent to read as a boundary.
        """
        if self.cut_kind is not None and self.cutoff is None:
            raise ValueError("`cut_kind` names a bounding rule but `cutoff` is null")
        if (self.cut_kind == "arrival-position") != (self.cut_anchor_index is not None):
            raise ValueError(
                "`cut_anchor_index` is non-null exactly where `cut_kind` is 'arrival-position'"
            )
        return self


class StagedOpinion(_Strict):
    """The manifest beside a staged majority opinion — ``record/opinion/opinion.json``.

    **Harness-owned and evaluate-only.** Written by ``provision-opinion``, never
    by an agent, and never by the provisioner the predict lane calls: the body it
    describes postdates every predict moment's cutoff, so the slot exists at all
    only because a judge needs to grade a semantic claim against the text the
    Court actually wrote.

    Written **only alongside a body**, so its presence is itself the answer to
    "is there an opinion to grade against?". A case whose row carries no opinion
    gets no file rather than a file saying so — a manifest asserting absence
    would be a second place for the answer to live, and the two could disagree
    after a later enrichment pass fills the row.

    The digest and length are the provenance a grader's basis can be audited
    against: a quote checked later resolves against a body identified by content,
    not by the path it happened to be written to.
    """

    case_id: str = Field(description="The case whose opinion is staged, `<court_id>/<docket_id>`")
    has_opinion: bool = Field(
        description="Always true on a written manifest — the corpus row's "
        "retained presence bit, restated here so the file is readable on its "
        "own. Absence of the file, not a false here, is how 'no opinion' is "
        "recorded"
    )
    sha256: str = Field(
        description="Hex SHA-256 of the staged text, UTF-8 encoded, so a "
        "grade's basis can later be resolved against the body it was formed "
        "from rather than against whatever that path holds now"
    )
    length: int = Field(
        ge=0,
        description="Characters of staged text. Beside the digest it is the "
        "cheap sanity read: a body of a few hundred characters is an order "
        "stub rather than an opinion, and a grader that masked on it should say "
        "so rather than grade a fragment",
    )
    source: dict[str, object] = Field(
        default_factory=dict,
        description="Where the body came from, as the corpus records it — the "
        "court, the case name, the decision date, the reporter citations and "
        "the precedential status the row carries. Open-shaped because it is a "
        "citation for a reader rather than a field anything computes on; keys "
        "whose corpus value is null are omitted rather than carried as nulls",
    )


class StagedWriting(_Strict):
    """One writing of a decision, as staged under ``record/opinion/writings/``."""

    position: int = Field(ge=1, description="Its order in the decision, from 1")
    kind: str = Field(description="The `WritingKind` vocabulary: opinion-of-the-court, dissent, …")
    author: str | None = Field(description="The signing Justice; null for a per curiam")
    header: str = Field(description="The writing's header sentence as printed (normalized)")
    words: int = Field(ge=0, description="Words under the per-opinion record's counting rule")
    file: str = Field(description="The staged file, relative to `record/opinion/`")
    sha256: str = Field(description="Hex SHA-256 of the staged file's UTF-8 bytes")
    length: int = Field(ge=0, description="Characters in the staged file")


class StagedDecision(_Strict):
    """One decision whose writings are staged: a document of the Court's opinions listing."""

    term: int = Field(description="The October Term (four-digit year)")
    listing_number: str = Field(description="The listing row's number: the document")
    name: str = Field(description="The case name as the listing prints it")
    decided: date = Field(description="The listing's decision date")
    document_url: str = Field(description="The supremecourt.gov PDF the text was read from")
    object_digest: str = Field(
        description="Hex SHA-256 of the stored text object the files were written from"
    )
    text_rule: str = Field(description="`<rule>/<version>` the text was cut under")
    writings: list[StagedWriting] = Field(description="Every writing, in the order printed")


class StagedWritings(_Strict):
    """The manifest beside the staged writings — ``record/opinion/writings.json``.

    **Harness-owned and evaluate-only**, on the majority opinion's terms
    (:class:`StagedOpinion`): written by ``provision-opinion --writings``, never by
    an agent or by the provisioner the predict lane calls, and written only
    beside the files it describes, so its presence is the answer to "are the
    writings staged?". Each decision is one document of the Court's opinions
    listing that names the case's docket, read from the per-opinion record's
    stored text and taken only where that text's bytes match the digest its
    pointer row records.
    """

    case_id: str = Field(
        description="The case whose decisions are staged, `<court_id>/<docket_id>`"
    )
    decisions: list[StagedDecision] = Field(
        min_length=1, description="Each decision staged, oldest first"
    )


#: Which side an argument segment's advocate stood for, as its header names it:
#: a party (``petitioner``, an appellant read as one; ``respondent``, an appellee
#: read as one), or an amicus — the United States or any other — keyed with the
#: party it supported. ``*-supporting-neither`` is a header that supported
#: vacatur or neither party; an amicus header naming no support has no side.
ArgumentSide = Literal[
    "petitioner",
    "respondent",
    "united-states-supporting-petitioner",
    "united-states-supporting-respondent",
    "united-states-supporting-neither",
    "amicus-supporting-petitioner",
    "amicus-supporting-respondent",
    "amicus-supporting-neither",
]

#: Whom an argument segment's advocate appeared for: a party (an appellant read
#: as petitioner, an appellee as respondent), the United States as amicus
#: curiae, or another amicus, court-appointed ones included.
ArgumentRole = Literal["petitioner", "respondent", "united-states-amicus", "amicus"]

#: Which party's position a segment argued for, whatever its advocate's role:
#: a respondent's counsel "in support of the petitioner" argues the petitioner's
#: position, and a court-appointed amicus "in support of the judgment below"
#: argues the respondent's.
ArgumentAlignment = Literal["petitioner", "respondent", "neither"]


class ArgumentTurnCount(_Strict):
    """Turns and words, one count pair of :class:`ArgumentFeatures`."""

    turns: int = Field(ge=0, description="Speaker turns: one per printed speaker label")
    words: int = Field(
        ge=0,
        description="Words spoken in those turns: whitespace-separated tokens carrying a "
        "letter or digit, the speaker label and the reporter's parentheticals excluded",
    )


class ArgumentSegment(_Strict):
    """One advocate's argument or rebuttal, as its header in the transcript names it."""

    index: int = Field(ge=0, description="Position in the argument, from 0")
    kind: Literal["argument", "rebuttal"] = Field(
        description="'rebuttal' for a 'REBUTTAL ARGUMENT OF' header, else 'argument'"
    )
    header: str = Field(
        description="The header as printed, its lines joined by single spaces: the "
        "text the side was read from"
    )
    role: ArgumentRole | None = Field(
        description="Whom the advocate appeared for: a party (an appellant read as "
        "petitioner, an appellee as respondent), the United States as amicus curiae, "
        "or another amicus. Null where the header names none"
    )
    supports: ArgumentAlignment | None = Field(
        description="The position the header says the advocate supported ('supporting "
        "the petitioner', 'in support of the judgment below', 'supporting vacatur'); a "
        "party header naming none supports its own party. Null for an amicus header "
        "naming no support, and wherever role is null; a rebuttal whose header names no "
        "side is read as the petitioner's, so its role is never null"
    )
    side: ArgumentSide | None = Field(
        description="The key this segment's Justice turns are counted under: the role, "
        "and for an amicus the position it supported. Null where either is unread, and "
        "the segment's Justice turns are then counted unattributed"
    )
    case_number: str | None = Field(
        description="The docket number an 'IN CASE <number>' header names, which is how "
        "a consolidated argument marks whose counsel is speaking. Null otherwise"
    )
    justice: ArgumentTurnCount = Field(
        description="Turns and words of every Justice in the segment, resolved or not"
    )
    advocate: ArgumentTurnCount = Field(
        description="Turns and words of the advocate the header names: a label whose "
        "surname appears in the header"
    )
    other_turns: int = Field(
        ge=0,
        description="Turns of any other speaker label: counsel the header does not name",
    )


def _turn_sum(counts: Iterable[ArgumentTurnCount]) -> ArgumentTurnCount:
    turns = words = 0
    for count in counts:
        turns += count.turns
        words += count.words
    return ArgumentTurnCount(turns=turns, words=words)


def _keyed_sum[K: str](rows: Iterable[dict[K, ArgumentTurnCount]]) -> dict[K, ArgumentTurnCount]:
    parts: dict[K, list[ArgumentTurnCount]] = {}
    for row in rows:
        for key, count in row.items():
            parts.setdefault(key, []).append(count)
    return {key: _turn_sum(counts) for key, counts in parts.items()}


class JusticeArgumentFeatures(_Strict):
    """One Justice's questioning, split by the side of the segment each turn fell in."""

    justice: str = Field(description="The roster surname the label resolved to, e.g. 'Kagan'")
    total: ArgumentTurnCount = Field(
        description="Every attributed turn: the sum over by_side, and over by_alignment"
    )
    by_side: dict[ArgumentSide, ArgumentTurnCount] = Field(
        description="Attributed turns by segment side; a side the Justice never spoke in is absent"
    )
    by_alignment: dict[ArgumentAlignment, ArgumentTurnCount] = Field(
        description="The same turns by the position the segment argued for"
    )
    unattributed: ArgumentTurnCount = Field(
        description="Turns in segments whose side is unread. Never folded into a side"
    )

    @model_validator(mode="after")
    def _sums(self) -> JusticeArgumentFeatures:
        if _turn_sum(self.by_side.values()) != self.total:
            raise ValueError(f"{self.justice}: total is not the sum over by_side")
        if _turn_sum(self.by_alignment.values()) != self.total:
            raise ValueError(f"{self.justice}: total is not the sum over by_alignment")
        return self


class ArgumentParseCoverage(_Strict):
    """How much of a transcript :class:`ArgumentFeatures` attributed, and how much not.

    Every Justice turn lands in exactly one of the four counts below
    ``justice_turns``, checked on construction: the parse states what it could
    not read rather than spreading it over the sides.
    """

    segments: int = Field(ge=0, description="Argument and rebuttal headers read")
    segments_attributed: int = Field(ge=0, description="Segments with a side")
    segments_unattributed: int = Field(ge=0, description="Segments whose side is null")
    justice_turns: int = Field(ge=0, description="Every Justice-labelled turn in the text")
    justice_turns_attributed: int = Field(
        ge=0, description="Turns of a resolved Justice in a segment with a side"
    )
    justice_turns_outside_segments: int = Field(
        ge=0,
        description="Turns before the first segment header: the Chief Justice calling "
        "the case, or every turn of a text where no header was read",
    )
    justice_turns_unresolved: int = Field(
        ge=0,
        description="Turns inside a segment under a Justice label whose surname the "
        "roster does not carry (a misprint, or a Justice outside the roster)",
    )
    justice_turns_unattributed_segment: int = Field(
        ge=0, description="Turns of a resolved Justice in a segment whose side is null"
    )
    unresolved_labels: list[str] = Field(
        description="The distinct Justice labels the roster did not resolve, as printed"
    )
    unrecognized_label_lines: int = Field(
        ge=0,
        description="Lines that open like a speaker label (capitals, then a colon) under "
        "a title the parse does not read as one; their words are counted with the turn "
        "they fall in, so this is how many such lines a reader may want to look at",
    )
    unrecognized_labels: list[str] = Field(
        description="The distinct label-like prefixes those lines open with, as printed"
    )
    closing_line: bool = Field(
        description="Whether the reporter's closing '(Whereupon … submitted.)' line was "
        "found. Without it the parse ran to the end of the text, which may then end "
        "inside the argument (a head-cut row) or run on into the word index"
    )
    notes: list[str] = Field(description="One line for each segment or read worth a reader's eye")

    @model_validator(mode="after")
    def _partitions(self) -> ArgumentParseCoverage:
        if self.segments_attributed + self.segments_unattributed != self.segments:
            raise ValueError("segments_attributed + segments_unattributed != segments")
        parts = (
            self.justice_turns_attributed
            + self.justice_turns_outside_segments
            + self.justice_turns_unresolved
            + self.justice_turns_unattributed_segment
        )
        if parts != self.justice_turns:
            raise ValueError("the four justice-turn counts do not sum to justice_turns")
        return self


class ArgumentFeatures(_Strict):
    """Per-Justice questioning by side, read from one cleaned argument transcript.

    Computed by :func:`fedcourtsai.pipeline.argument_features.parse_argument_features`
    from the text :func:`fedcourtsai.pipeline.documents.extract_transcript_text`
    stores, deterministically and with no model in the loop, so one transcript
    always yields one count. ``assignment`` states the reading that turns a
    speaker label into a side. The totals are checked on construction against
    the rows and the coverage against the segments.
    """

    parser_version: Literal["1"] = Field(
        description="The parse rules' version; a change to what a given text yields moves it"
    )
    assignment: str = Field(description="How a speaker turn was assigned to a side, in one line")
    segments: list[ArgumentSegment] = Field(description="Every segment, in argument order")
    justices: list[JusticeArgumentFeatures] = Field(
        description="One row per resolved Justice who spoke, by surname"
    )
    side_totals: dict[ArgumentSide, ArgumentTurnCount] = Field(
        description="Every resolved Justice's attributed turns, summed by segment side"
    )
    alignment_totals: dict[ArgumentAlignment, ArgumentTurnCount] = Field(
        description="The same turns summed by the position the segment argued for"
    )
    coverage: ArgumentParseCoverage = Field(description="What was and was not attributed")

    @model_validator(mode="after")
    def _consistent(self) -> ArgumentFeatures:
        if self.side_totals != _keyed_sum(row.by_side for row in self.justices):
            raise ValueError("side_totals are not the sum of the rows' by_side")
        if self.alignment_totals != _keyed_sum(row.by_alignment for row in self.justices):
            raise ValueError("alignment_totals are not the sum of the rows' by_alignment")
        if self.coverage.segments != len(self.segments):
            raise ValueError("coverage.segments is not the number of segments")
        attributed = sum(1 for segment in self.segments if segment.side is not None)
        if self.coverage.segments_attributed != attributed:
            raise ValueError("coverage.segments_attributed is not the segments with a side")
        return self


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


class ClaimDistribution(_Strict):
    """One declared distribution claim's probabilities, in ``Prediction.claim_distributions``.

    The form a claim over the bench takes, where one probability cannot carry
    the forecast: a label per Justice (the roster's spelling), and for the
    majority-author claim the ``per-curiam`` label beside them. Whether the
    probabilities are one distribution summing to 1 or an independent
    probability per Justice is the declared claim's kind, fixed by the harness
    in ``fedcourtsai.pipeline.claims`` and checked there; this record carries
    only the predictor's numbers, as :class:`ClaimProbability` does.
    """

    claim_id: str = Field(
        description="The declared distribution claim these probabilities answer, "
        "e.g. 'majority-author', 'separate-writers', 'order-writers'"
    )
    probabilities: dict[str, Annotated[float, Field(ge=0.0, le=1.0)]] = Field(
        min_length=1,
        description="Label -> the predictor's probability. A label is a Justice's "
        "name as the roster spells it, or 'per-curiam' on the majority-author "
        "claim. On a categorical claim (majority-author) the values sum to 1 over "
        "the labels; on a per-Justice claim (separate-writers, order-writers) "
        "each is that Justice's own probability and there is no sum",
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
    input_snapshot: str = Field(
        description="Which provisioned snapshot the cell read — the file under "
        "`data/cases/<court>/<docket>/record/snapshots/`, named for a day. The "
        "agent's own word. The prompt contracts one spelling — the file's bare "
        "basename `YYYY-MM-DD.json`, or the literal `missing` where the cell "
        "found none — but the committed ledger predates that contract and "
        "spells one file several ways (a repo-rooted path, commonest by far; a "
        "`record/`-relative one; the bare basename; the bare day). Validation "
        "accepts any string: the ledger is the ledger, and refusing a spelling "
        "the contract never asked of those cells would fail records that are "
        "not wrong. So the harness "
        "normalizes instead of requiring: `stamp-cell` reduces both this field "
        "and the provisioned filename to that file's **day** and compares them, "
        "which makes every spelling above agreement, and records the answer in "
        "`context.snapshot_uptake`. That comparison is the only thing this field "
        "decides; nothing scored conditions on it."
    )
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
        "later by its rank-agreement with the evaluator panel's own reads, never "
        "against a ground truth. "
        "The prompt contracts a number or an explicit null carrying a one-line "
        "`big_case_rationale`; the rationale is what separates a considered no-view "
        "from silence, since `stamp-cell` rewrites the record through this model and an "
        "omitted score lands as the same null. The schema stays permissive (defaults "
        "None) because records written before the field existed still validate. See "
        "docs/salience.md.",
    )
    big_case_rationale: str | None = Field(
        default=None,
        max_length=500,
        description="One-line rationale for `big_case_score`: required by the prompt "
        "contract where that score is an explicit null — it is the only thing that "
        "distinguishes a considered no-view from a cell that answered nothing — "
        "optional beside a number, and null if none",
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
        "carry the gap. A cell that WAS provisioned one and did not report "
        "reading it keeps the block unchanged, with `context.snapshot_uptake` "
        "recording the disagreement — the honest record, and not a gap.",
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
    claim_distributions: list[ClaimDistribution] | None = Field(
        default=None,
        description="Per-claim probability distributions over the harness-declared "
        "distribution claims for this event (`fedcourtsai.pipeline.claims`): the "
        "authorship forecasts, one label per Justice. Mandatory where the "
        "event's set declares any, exactly as `claims` is. Null on events whose "
        "set declares none, and on predictions written before the field existed; "
        "omitted from the file while null",
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

    @model_serializer(mode="wrap")
    def _omit_unstated_distributions(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``claim_distributions`` while null, so an older record reads as before."""
        payload = handler(self)
        if isinstance(payload, dict) and self.claim_distributions is None:
            payload.pop("claim_distributions", None)
        return payload


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
        "at resolution — a stakes proxy. Counted per entry naming amicus or amici "
        "curiae (a multi-filer entry counts once), plus each distinct lead filer "
        "whose brief the docket shows as submitted and not yet accepted. 'As at "
        "resolution' is end of the disposition day: an entry sharing that date is "
        "counted whatever its position on the docket, and one filed after it is "
        "not",
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
    writing_roles: list[JusticeWriting] | None = Field(
        default=None,
        description="What every participating Justice wrote, observed apart from "
        "how they voted: present only where the source observed the whole "
        "participating bench's writings — every writing the Court published for "
        "the act read without a problem — so a Justice listed as `none` is "
        "observed to have written nothing. Absent means not observed, never "
        "observed-as-none. Kept off `votes` because at the cert and interim "
        "stages the roles are observable for every Justice while the votes are "
        "not, and a vote entry needs a vote. Vote scoring and its completeness "
        "gate read `votes` and `vote_provenance` only; the `separate-writers` and "
        "`order-writers` claims resolve from these roles, and `majority-author` "
        "reads its labels off them beside `merits_author`. Read beside "
        "`vote_provenance`, which it requires",
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
    merits_decision_method: MeritsDecisionMethod | None = Field(
        default=None,
        description="How the Court decided the case, beside what it did to the "
        "judgment (`MeritsDecisionMethod`): a signed opinion after argument, a "
        "per curiam after argument, a summary opinion or order, or a DIG. Read "
        "from the corpus row's decision record when the merits outcome is "
        "written; the majority-author claim resolves only where it is "
        "classified and agrees with `merits_author`. Null off the merits stage "
        "and where the record left the method unclassified, never an observed "
        "absence; omitted from the file while null",
    )
    merits_author: str | None = Field(
        default=None,
        description="Who delivered the opinion deciding the merits, as the Court's "
        "opinions listing prints it: a Justice's name as the roster spells it, or "
        "`per-curiam` for an unsigned opinion. Stamped by the opinions-source "
        "writer off the listing row for every decision it finds, signed or per "
        "curiam, whether or not the lineup was read, so which outcomes carry it "
        "never depends on who wrote: what resolves the majority-author claim. "
        "Null off the merits stage and where no listing row was matched, never "
        "an observed absence; omitted from the file while null",
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

    @model_validator(mode="after")
    def _decision_method_is_merits_only(self) -> Outcome:
        """How the Court decided is a merits fact: no judgment, no method."""
        if self.merits_decision_method is not None and self.judgment is None:
            raise ValueError("`merits_decision_method` is set off the merits stage")
        if self.merits_author is not None and self.judgment is None:
            raise ValueError("`merits_author` is set off the merits stage")
        return self

    @model_validator(mode="after")
    def _vote_record_coheres(self) -> Outcome:
        """A provenance block must describe the lists it sits beside.

        Only a provenanced record is checked, so a record written before the
        block existed is unaffected. A block states a source for something: a
        vote list, or the whole bench's observed writing roles (an order read
        in full where no Justice noted a vote). A Justice named twice in
        either list is two readings of one fact. A complete record's
        `participating` must be the count of its votes that are neither
        `recused` nor `did-not-participate`, because that count is the
        denominator a vote threshold is taken against; observed writing roles
        cover exactly the participating Justices, none of them recorded as not
        taking part, and a vote's own `writing` may not contradict its
        Justice's role.
        """
        provenance = self.vote_provenance
        roles = self.writing_roles
        if provenance is None:
            if roles is not None:
                raise ValueError("`writing_roles` is set but `vote_provenance` is not")
            return self
        if not self.votes and not roles:
            raise ValueError("`vote_provenance` is set but `votes` and `writing_roles` are empty")
        names = [vote.justice for vote in self.votes]
        if len(set(names)) != len(names):
            raise ValueError("`votes` names a Justice more than once")
        absent = {
            vote.justice
            for vote in self.votes
            if vote.vote in (VoteValue.recused, VoteValue.did_not_participate)
        }
        if provenance.complete:
            sitting = len(self.votes) - len(absent)
            if sitting != provenance.participating:
                raise ValueError(
                    f"a complete vote record counts {sitting} participating votes "
                    f"but `vote_provenance.participating` is {provenance.participating}"
                )
        if roles is not None:
            role_of = {role.justice: role.writing for role in roles}
            if len(role_of) != len(roles):
                raise ValueError("`writing_roles` names a Justice more than once")
            if len(roles) != provenance.participating:
                raise ValueError(
                    f"`writing_roles` names {len(roles)} Justices but "
                    f"`vote_provenance.participating` is {provenance.participating}"
                )
            if absent & role_of.keys():
                raise ValueError("`writing_roles` names a Justice the votes record as not sitting")
            for vote in self.votes:
                if vote.justice in role_of and vote.writing != role_of[vote.justice]:
                    raise ValueError(
                        f"{vote.justice}'s vote records writing {vote.writing!r} but "
                        f"`writing_roles` records {role_of[vote.justice]!r}"
                    )
        return self

    @model_serializer(mode="wrap")
    def _omit_unclassified_method(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop the decision fields while null, so an older outcome reads as before."""
        payload = handler(self)
        if isinstance(payload, dict):
            if self.merits_decision_method is None:
                payload.pop("merits_decision_method", None)
            if self.merits_author is None:
                payload.pop("merits_author", None)
        return payload


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
    """The evaluator's own read of a case's stakes (the big-case dimension).

    The evaluator forms its **own** opinion of how big / significant the case is.
    It is not blind: the predictions it grades carry the predictors'
    ``big_case_score`` and ``big_case_rationale``, so the read is formed with
    them in view and the prompt asks only that it not anchor on them — which is
    why the agreement it grades is read as an upper bound (``metrics/README.md``,
    the ``big_case`` reading rule). Unlike the blind grant forecast, this is a *judge's* read: the
    evaluator may use post-decision context available at evaluation time (the
    outcome, the immediate reaction). The predictor's pre-registered score is
    graded by its agreement with this read — **rank-agreement across the evaluated
    cohort** at leaderboard time, since bigness is comparative (a per-case
    absolute delta is a secondary diagnostic); this record stores only the
    evaluator's read, never the grade. Optional on the evaluation so records
    written before the dimension existed still validate. See ``docs/salience.md``.
    """

    evaluator_score: float = Field(
        ge=0.0,
        le=1.0,
        description="The evaluator's own 0-1 stakes / significance read, formed "
        "from the case itself without anchoring on the predictors' big_case_score, "
        "which is in view",
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
        "prediction time, or a federal party named in the case's caption, makes "
        "the cvsg-increment claim vacuous; on the cert call-for-response moment, "
        "whose petition is all but certain to be distributed again, the "
        "relist-increment claim is vacuous. Also None, with `mask_reason` saying so, "
        "where the run-timing mask applies",
    )
    mask_reason: Literal["signal-before-run"] | None = Field(
        default=None,
        description="Set where the claim is masked for a reason the frozen record alone "
        "does not carry, which every other mask does. `signal-before-run`: an increment "
        "claim (`response-requested-increment`, `referral-increment`, `cvsg-increment`) "
        "on a forward cell whose signal was already on the docket before the cell ran — "
        "the cell's pre-mint poll read it present, or, with no usable poll (or one that "
        "recorded no reading of that signal), its docket date is strictly before the "
        "cell's run day in Court time (`set_aside.increment_timing`). Conditioned on when "
        "the cell ran rather than on what it was provisioned, so it is not the vacuous "
        "mask. Omitted otherwise",
    )
    score: float | None = Field(
        default=None,
        description="(baseline - outcome)^2 - (probability - outcome)^2 — the "
        "baseline's Brier minus the forecast's (`pipeline.base_rates.claim_score`). "
        "None when outcome or baseline is None",
    )

    @model_serializer(mode="wrap")
    def _omit_unset_mask_reason(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``mask_reason`` while unset, so a row it does not reach reads as before."""
        payload = handler(self)
        if isinstance(payload, dict) and self.mask_reason is None:
            payload.pop("mask_reason", None)
        return payload


class DistributionScore(_Strict):
    """One declared distribution claim's row inside ``ClaimScoreBlock.distributions``.

    The bench-shaped counterpart of :class:`ClaimScore`, under the same
    discipline: everything except ``probabilities`` is the harness's. The
    registered rule is applied once per label, ``(b - y)^2 - (p - y)^2``, and
    the claim's declared weighting combines the label terms: a categorical
    claim adds them (bounded by 2), a per-Justice claim averages them over the
    Justices it resolves (bounded by 1), so a bench of nine weighs as one
    claim (`docs/outcome-decomposition.md`, *The authorship claims*). A claim
    the declaration marks collected-only is resolved and never scored.
    """

    claim_id: str = Field(description="The declared distribution claim this row scores")
    probabilities: dict[str, float] = Field(
        description="The predictor's stated probabilities by label, copied from "
        "the prediction's `claim_distributions` block"
    )
    baseline: dict[str, float] | None = Field(
        default=None,
        description="The harness-computed baseline by label, from Terms strictly "
        "before the October Term of the cell's snapshot. None where the committed "
        "statpack publishes no cut supporting one; the claim then goes unscored",
    )
    outcome: dict[str, int] | None = Field(
        default=None,
        description="How each label resolved, 1 or 0, over the labels the record "
        "settles. None when the record does not disclose the claim — the "
        "availability mask: no observed writing roles, an unclassified decision "
        "method, or (for majority-author) no deciding opinion",
    )
    scored: bool = Field(
        description="Whether the declaration scores this claim. False for a "
        "collected-only claim (order-writers), whose row carries its resolution "
        "and never a score"
    )
    score: float | None = Field(
        default=None,
        description="The per-label rule combined by the claim's declared "
        "weighting. None when unscored, or when outcome or baseline is None",
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
    distributions: list[DistributionScore] = Field(
        default_factory=list,
        description="One row per declared distribution claim (the authorship "
        "claims), in the declaration's order. Reported beside the claims and "
        "never added into `total`, `floor` or `lift`: the authorship block "
        "stands on its own until the criterion registered for joining it is "
        "met. Omitted from the file while empty",
    )

    @model_serializer(mode="wrap")
    def _omit_undeclared_distributions(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``distributions`` while empty, so a block it does not reach reads as before."""
        return _omit_empty(handler(self), distributions=self.distributions)


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
    mask_ground: MaskGround | None = Field(
        default=None,
        description="Which of the mask's three grounds this grade rests on, "
        "where the grade is `not-addressed`: `no-judgment` (no opinion body of "
        "the kind the claim requires was filed — the case's posture, which "
        "bounds what could ever have been graded), `not-ingested` (one exists "
        "and the record does not carry it — work the pipeline still owes), or "
        "`silent-on-axis` (the body is in hand and says nothing on the claim's "
        "axis — a finding about what the Court wrote). Counted rather than left "
        "to `basis`, because those are three different kinds of fact and an "
        "undifferentiated mask total lets any of them be read as another. Null "
        "on every grade that is not a mask, and on a mask whose grader named no "
        "ground — the census counts those as `unstated` rather than assuming one",
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
    ``cert-v1`` and ``merits-v1`` are. The merits moments declare it, the
    evaluate prompt asks a grader for it, and the evaluate cell is handed its
    case's majority opinion wherever the corpus holds one — but opinion coverage
    is a rounding error against the granted slice, so essentially every declared
    claim masks (``not-addressed``) and no published number depends on it.
    Supersession by a set formed with text in hand is the expected path, not an
    exception.
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


class CentralClaim(_Strict):
    """One claim a judge treated as central to a predicted-reasoning document.

    The audit trail beside ``Evaluation.predicted_reasoning_quality``: it shows
    which claims the grade rests on, so a reviewer can see whether the judge
    graded the claims the document led with or hunted for a detail to dock.
    Never scored and never aggregated (``docs/outcome-decomposition.md``,
    *Grading the forecast document, design*).
    """

    claim: str = Field(
        max_length=500,
        description="The claim as the document committed to it, in a sentence",
    )
    status: CentralClaimStatus = Field(
        description="Whether the outcome bore the claim out. `unresolved` is the "
        "staged record failing to settle it — conditional content an outcome "
        "never tested, or a writing the record does not carry — and is never "
        "read as a miss"
    )
    basis: str | None = Field(
        default=None,
        max_length=1000,
        description="What in the staged record the status rests on, briefly. "
        "Null when the judge recorded none",
    )


class PredictedReasoningReview(_Strict):
    """A judge's review of one prediction's ``predicted_reasoning.md``.

    Carries what stands behind ``Evaluation.predicted_reasoning_quality``: the
    claims the judge treated as central, or, where the judge returned no
    grade, the record's ground for that. The evaluate prompt's *Grading the
    forecast document* section asks for it on every stage
    (``docs/outcome-decomposition.md``, *Grading the forecast document,
    design*).
    """

    central_claims: list[CentralClaim] = Field(
        default_factory=list,
        max_length=5,
        description="The claims, at most five, the judge treated as central to "
        "the document, in the order the document gives them weight. Required "
        "beside a grade; may be empty beside a null one",
    )
    not_gradeable: str | None = Field(
        default=None,
        max_length=1000,
        description="Where the grade is null, the record's ground for that: the "
        "staged record is silent on everything the document's central claims "
        "turn on. Never a ground about the predictor — a vague, hedged or "
        "all-conditional document is gradeable, and graded low. Null beside a "
        "grade",
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
        "On a **cert** grading stamped under proc-v9 or later whose scored prediction "
        "froze a band it is harness-stamped the same way, beside the stamped cert "
        "anchor; on any other cert cell it is the evaluator's, and the "
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
    vote_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Fraction of the prediction's per-Justice votes that match the "
        "outcome's, over the Justices both name. Merits-stage cells only, and only "
        "against a vote record whose `vote_provenance` says `complete: true`; null "
        "everywhere else (`pipeline.evaluate.vote_accuracy`). Descriptive: the "
        "leaderboard does not average it, but recomputes each cell's "
        "participating-bench accuracy (`pipeline.evaluate.bench_vote_accuracy`)",
    )
    reasoning_quality: float | None = Field(default=None, ge=0.0, le=1.0)
    predicted_reasoning_quality: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The judge's 0-1 grade of the prediction's "
        "`predicted_reasoning.md` alone — how well its forecast of what the Court "
        "would do and say held up — on the anchored rubric in "
        "`docs/outcome-decomposition.md` (*Grading the forecast document, "
        "design*). Not a grade of the prediction as a whole, and never folded "
        "into `reasoning_quality`, which grades `reasoning.md`. Null where the "
        "record cannot grade it (`predicted_reasoning_review.not_gradeable` says "
        "why), where the prediction names no forecast document, and on every "
        "evaluation whose prompt did not ask for it",
    )
    predicted_reasoning_review: PredictedReasoningReview | None = Field(
        default=None,
        description="What stands behind `predicted_reasoning_quality`: the "
        "central claims the grade rests on, or the record's ground for a null "
        "grade. Null wherever the grade was not asked for, and where the "
        "prediction names no forecast document",
    )
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
        description="The evaluator's own big-case read (see "
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
        "which of the two published rates — is recorded in base_rate_basis below. On a "
        "cert grading stamped under proc-v9 or later whose scored prediction froze a "
        "band, the rate is harness-stamped by `stamp-cell --role evaluator`: the "
        "risk-set rate pooled through the scorer's own pooler over the prediction's "
        "frozen band, salience version, and Term, from the statpack build named in "
        "base_rate_statpack_digest, and cleared where that pool is empty. On an "
        "earlier label's cert grading, and on a cert cell whose prediction froze no "
        "band (the terminal fallback, which re-derives a band from the corpus row), "
        "the rate is the evaluator's to record. On a merits cell it is instead the "
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
    base_rate_statpack_digest: str | None = Field(
        default=None,
        description="Harness-stamped digest (`pipeline.base_rates.statpack_digest`, "
        "`sha256:` over the parsed statpack's canonical JSON) of the statpack build a "
        "harness-stamped cert segment_base_rate was pooled from. Written by "
        "`stamp-cell --role evaluator` beside every cert anchor it stamps (proc-v9 "
        "and later, where the scored prediction froze a band). From proc-v15, where "
        "the scored prediction's context carries a cert_anchor, it is that anchor's "
        "build — the statpack in force when the forecast was placed — and the "
        "leaderboard drops a cell that does not record its pin; otherwise the "
        "leaderboard re-pools the anchor wherever its own statpack carries the same "
        "digest and drops a cell whose recorded rate does not reproduce. Null wherever the rate "
        "is not a harness-stamped cert anchor — every merits and interim cell, an "
        "earlier label's cert grading, a cert cell on the terminal fallback — and "
        "on records written before the field existed.",
    )
    base_rate_lookback_terms: int | None = Field(
        default=None,
        ge=0,
        description="Harness-stamped `salience.base_rate_lookback_terms` a "
        "harness-stamped cert segment_base_rate was pooled under (0 = no window), "
        "written beside base_rate_statpack_digest so the build and the window "
        "together name the pool; the leaderboard re-pools under this recorded "
        "window rather than the one in config at build time. Null wherever "
        "base_rate_statpack_digest is.",
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
        "construction rather than merely reproducible from the record — and so is a "
        "cert cell's wherever segment_base_rate is the harness-stamped anchor "
        "(proc-v9 and later, frozen band); on any other cert cell it is the "
        "evaluator's, computed against the band rate it recorded. Null "
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

    @model_validator(mode="after")
    def _predicted_reasoning_review_coheres(self) -> Evaluation:
        """A grade stands on central claims; a null beside a review states the record's ground."""
        review = self.predicted_reasoning_review
        if self.predicted_reasoning_quality is not None:
            if review is None or not review.central_claims:
                raise ValueError(
                    "`predicted_reasoning_quality` needs a `predicted_reasoning_review` "
                    "listing the central claims it rests on"
                )
            if review.not_gradeable is not None:
                raise ValueError(
                    "`predicted_reasoning_review.not_gradeable` is the ground for a null "
                    "grade and cannot stand beside a grade"
                )
        elif review is not None and review.not_gradeable is None:
            raise ValueError(
                "a `predicted_reasoning_review` beside a null grade must say in "
                "`not_gradeable` why the record cannot grade the document"
            )
        return self


class PolledSignal(_Strict):
    """One increment signal as a harness docket poll's served docket showed it."""

    present: bool = Field(
        description="Whether the served docket carried the signal's entry, by the reading "
        "that sets its ingest flag"
    )
    entry_date: date | None = Field(
        default=None,
        description="The signal entry's date, by the parser that dates it at ingest; null "
        "where the signal is absent or its entry carries no full date",
    )


class PolledIncrementSignals(_Strict):
    """The increment signals a harness docket poll read off the served docket.

    Record-only: the poll's verdict is the outcome scan's alone, and the payload
    stays read-and-discard, never the cell's input. An application docket fills
    `response_requested` and `referred_to_court`, a petition docket `cvsg`; a
    signal the docket's form cannot carry is null, never absent.
    """

    response_requested: PolledSignal | None = Field(
        default=None,
        description="Whether the Court (or a Circuit Justice) had requested a response "
        "to the application (`interim_signals.response_requested` / "
        "`response_requested_date`); null on a petition docket",
    )
    referred_to_court: PolledSignal | None = Field(
        default=None,
        description="Whether the application had been referred to the full Court "
        "(`interim_signals.referral_posture` / `referral_date`); null on a petition docket",
    )
    cvsg: PolledSignal | None = Field(
        default=None,
        description="Whether the Solicitor General had been invited to file "
        "(`cert_signals.CVSG_RE` / `snapshot_cvsg_date`); null on an application docket",
    )


class DocketPollRecord(_Strict):
    """One harness poll of a forward cell's docket, as the cell's usage record carries it.

    A poll reads the Court's docket JSON as served and runs the forward outcome scan
    on it. ``open`` is narrower than it sounds: it means that JSON carried no
    disposition the scan recognises at ``polled_at``, not that the event was
    undecided — the JSON can lag the order or come from a cache, the scan's recall
    is not perfect, and a disposition can land after the poll.
    """

    polled_at: datetime = Field(description="When the poll's fetch began, in UTC")
    docket_number: str = Field(
        description="The docket number polled, as the provisioned snapshot names it"
    )
    state: Literal["open", "decided", "unavailable"] = Field(
        description="open: the docket JSON as served carried no disposition the forward "
        "outcome scan recognises; decided: it did; unavailable: the poll could not answer "
        "(no docket served, a body that is not JSON, a timeout, an error)"
    )
    reason: str | None = Field(
        default=None,
        description="Why the poll read decided or unavailable; null when open",
    )
    signals: PolledIncrementSignals | None = Field(
        default=None,
        description="Record-only: what the served docket showed at `polled_at` of each "
        "increment signal the cell's claims forecast, with the entry date the ingest "
        "parser reads. The claim scorer reads a pre-mint poll's reading to mask an "
        "increment claim whose signal was already on the docket before the cell ran, and "
        "the boards' `stratify` pass reads a post-run poll's to set aside one whose signal "
        "the pre-mint poll read absent and the post-run poll present "
        "(`set_aside.increment_timing`). Omitted where the poll read no proceedings list "
        "(an `unavailable` poll, a payload without one) or its signal reading failed; a "
        "poll carrying no `signals` reads as one that recorded no signal",
    )

    @model_serializer(mode="wrap")
    def _omit_unread_signals(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``signals`` while the poll read none, so such a record reads as before."""
        payload = handler(self)
        if isinstance(payload, dict) and self.signals is None:
            payload.pop("signals", None)
        return payload


class ModelUsage(_Strict):
    """``usage.json`` — measured model token usage and estimated cost for one run.

    Written per ``run-predict`` / ``run-evaluate`` matrix cell (predictor x event
    for predict, evaluator x event for evaluate) alongside that cell's prediction
    or evaluation output. Token buckets follow the Claude convention:
    ``input_tokens`` is fresh input, with cached reads and cache writes counted
    separately so ``estimated_cost_usd`` can apply the right rate to each (see
    ``fedcourtsai.pricing``). Summing these across runs replaces the planning
    assumption with a measured \\$/run.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    event_id: str
    run_id: str
    role: UsageRole = Field(description="Which stage produced the usage")
    actor_id: str = Field(description="The predictor_id (predict) or evaluator_id (evaluate)")
    engine: Engine
    model: str = Field(description="Model the cost rates were applied to (resolved, never null)")
    served_models: list[str] | None = Field(
        default=None,
        description="The models the engine's own log names for the cell's main-agent "
        "calls, distinct and in first-seen order — harness-read from the log, never the "
        "agent's word, and kept beside the requested `model` so a cell that ran on "
        "something else shows in the record. How close each engine's value sits to the "
        "provider differs, and that is the reading: claude-code's is the model each "
        "main-thread API response named; gemini's is each main-role response's own "
        "`modelVersion` where the API sent one, else the model the CLI requested, so it "
        "shows the CLI's own fallback too and spells a version the way the provider does; "
        "codex's is the model each turn context addressed, which shows a client-side "
        "switch and never a provider substitution, since Codex does not persist a reroute "
        "to its rollout. Subagent and utility calls are left out on every engine: they run "
        "on helper models by design. Pricing stays on `model`. Null when the log names "
        "no model, or on a record written before the field existed: unknown, not a match.",
    )
    created_at: datetime
    pipeline_sha: str | None = Field(
        default=None,
        description="Git commit of the pipeline checkout that ran this cell "
        "(GITHUB_SHA in CI, the local HEAD otherwise) — pins the prompt "
        "templates, harness, and registry in force at run time. Null on "
        "records written before the field existed or when unresolvable.",
    )
    engine_version: str | None = Field(
        default=None,
        pattern=r"^\d+\.\d+\.\d+$",
        description="The engine CLI's version as its own binary reported it "
        "(`claude --version`, `codex --version`, `gemini --version`), read by the "
        "harness — never the agent's word. For the CLIs the harness installs "
        "(claude-code, gemini) the read is taken at install, before any agent ran; "
        "codex is installed by its action, so its read follows the run. An engine "
        "update under an unchanged process digest is composition, and this field is "
        "how a reading cuts by it. Null on records written before the field existed "
        "or when the binary's output named no version.",
    )
    engine_version_discrepancy: str | None = Field(
        default=None,
        description="Set when the engine's version reads disagree: the binary reported "
        "a different version after the run than at install, or a version other than "
        "the pin the workflow installed from. The recorded `engine_version` is kept "
        "as read; this says the cell's engine is in doubt, and a reading cutting by "
        "engine version treats such a cell as unknown. Null when every read agrees, "
        "and on records written before the field existed.",
    )
    pre_mint_poll: DocketPollRecord | None = Field(
        default=None,
        description="The harness's poll of a forward predict cell's docket just before "
        "its record was written. A cell whose poll reads `decided` is refused and writes "
        "no usage record, so a recorded poll is `open` or `unavailable`. `open` bounds "
        "the cell's exposure to a disposition to the window from `polled_at` to the "
        "end of the run; it is not proof the event was undecided (see "
        "DocketPollRecord). Null on evaluate cells, on cells minted before the poll "
        "existed, and wherever no poll ran.",
    )
    post_run_poll: DocketPollRecord | None = Field(
        default=None,
        description="The same poll taken after the cell's engine step ended. Record "
        "only: it never refuses or removes a cell. `pre_mint_poll` and `post_run_poll` "
        "both `open` say the whole run ended before the served docket showed a "
        "decision, not that the order was unpublished (an order list or a press account "
        "can precede the docket JSON); a `decided` post-run poll leaves the ordering "
        "inside the run unresolved. Either way leakage is read from the retrieval log's "
        "content. Null where no post-run poll ran.",
    )
    input_tokens: int = Field(ge=0, description="Fresh (uncached) input tokens")
    output_tokens: int = Field(ge=0)
    cache_read_input_tokens: int = Field(default=0, ge=0, description="Input served from cache")
    cache_creation_input_tokens: int = Field(default=0, ge=0, description="Input written to cache")
    estimated_cost_usd: float = Field(
        ge=0.0, description="On-demand USD estimate from the rates in fedcourtsai.pricing"
    )


class BlindingCount(_Strict):
    """One term's occurrences in one file of an evaluate cell's output."""

    file: str = Field(
        description="The file, relative to the evaluator's own directory for the event "
        "(`<predictor_id>/<run_id>/evaluation.md`, `<run_id>/flags.json`)"
    )
    term: str = Field(
        description="What was counted, lowercase: the predictor id an alias resolved to "
        "(`replaced`), or the identity text as the judge wrote it (`names_present`)"
    )
    count: int = Field(ge=1)


class BlindingRecord(_Strict):
    """``blinding.json`` — what un-aliasing did to one evaluate cell's output.

    Written by the harness beside the cell's ``usage.json`` when it renames the
    judge's alias-keyed output onto the real predictor ids
    (:func:`fedcourtsai.blinding.unblind_evaluations`). The rewrite resolves
    every alias the judge wrote to a predictor id, so the committed text names
    predictors; this record is what tells a name the harness substituted from
    one the judge wrote itself.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    case_id: str
    event_id: str
    run_id: str
    evaluator_id: str
    scanned_files: list[str] = Field(
        description="Every file of the judge's own output the counts were taken over, "
        "relative to the evaluator's directory: the renamed per-candidate directories and "
        "the cell's own run-keyed directory, less the harness-written files "
        "(`usage.json`, `retrieval_log.json`, `blinding.json`), which carry the "
        "evaluator's own id and engine by construction. A file not listed was not read"
    )
    replaced: list[BlindingCount] = Field(
        description="Alias occurrences the harness rewrote, per file, keyed by the "
        "predictor id each resolved to — counted over every file it rewrites, the "
        "harness-written retrieval log included"
    )
    names_present: list[BlindingCount] = Field(
        description="Identity terms already in the judge's own text BEFORE un-aliasing: predictor "
        "and evaluator ids, engine names, model ids and the bare family words the "
        "staging scrub masks (`fedcourtsai.blinding.identity_terms`), less the "
        "evaluator's own id, engine and model, which its `evaluation.json` carries "
        "about itself — so a candidate that shares the judge's engine or model is not "
        "counted under that shared term, only under its own id. The judge was staged "
        "text with every such term redacted, so one here is a name the judge wrote "
        "itself — recognising a candidate's style, or breaking the blind through a "
        "route the scrub cannot close. Empty is the expected case. A count is a match "
        "of the same case-insensitive pattern the scrub uses, so a family word used in "
        "its ordinary sense (`codex` for a manuscript) counts too: read the term and "
        "file before reading it as a broken blind"
    )


class AgentFlag(_Strict):
    """One structured note a headless agent surfaces for maintainer triage.

    A typed alternative to burying a remark in ``reasoning.md`` or a run log:
    a ``category`` and ``severity`` so the roll-up can sort and filter, and
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
    issue: int | None = Field(
        default=None,
        gt=0,
        description="The repository issue that already tracks this problem, when the agent "
        "cites one instead of re-describing it; the roll-up counts a cited tracked theme "
        "against its issue",
    )
    source: FlagSource = Field(
        default=FlagSource.agent,
        description="Who wrote the note: `agent` (the cell's own, the default) or `harness` "
        "(a post-agent step's finding about the cell). A triage label the roll-up filters and "
        "counts on, not an authentication",
    )
    normalised: bool = Field(
        default=False,
        description="Set by the harness when it coerced this flag to fit the schema (an "
        "off-vocabulary severity or category, an over-long message, an unknown key); the "
        "`harness` note beside it says what changed. A flag never fails a predict or evaluate cell",
    )


class AgentFlags(_Strict):
    """``flags.json`` — a cell's durable, structured feedback for maintainer triage.

    A predict/evaluate cell writes this *only when it has something to
    surface* — a data-quality problem, a scope question, an ambiguous event, or the
    reason it was blocked. Mostly the agent's own word, but not exclusively: a
    post-agent harness step appends its own findings about the cell to the same
    file (``stamp-cell``, where a cell reports not having read its provisioned
    snapshot, and the normalisation note when the agent's file did not validate),
    marked ``source: harness`` so the roll-up lists and counts them apart. A
    mis-shaped file never fails its cell: the stamp normalises it before
    ``validate`` (:func:`fedcourtsai.agent_flags.normalise_flags`). It rides the
    cell's artifact to the ``collect`` job, which rolls every cell's flags into
    the run PR body (and the Actions summary), so a note outlives the run that
    raised it and a maintainer sees it without reading every ``reasoning.md``.
    The agent token stays comment-only: the file is written locally and the
    trusted ``collect`` job does the surfacing.
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
    across runs on the run-ops report, it tells maintainers whether the corpus
    tooling earns its keep and where to invest next; ``used_corpus_query`` alone is
    also read per run by the ``collect`` job, as the self-reported side of the run
    PR's prior-availability note (the field asks whether the cell *used* the CLI,
    which that note weighs against what capture saw rather than treating as a
    verdict on the corpus). It is the agent's own account —
    subjective, advisory, and never a gate. The stamp normalises a mis-shaped report
    before ``validate`` (:func:`fedcourtsai.agent_tooling.normalise_tooling`), short
    of supplying a ``used_corpus_query`` the cell did not answer or reading a file
    that is not a JSON object. The token stays comment-only: the
    file is written locally and the trusted ``collect`` job commits it with the cell's
    output.
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
    # Named states rather than a bool: `false` would read as "returned
    # nothing", which is the very conflation this field exists to end, and the
    # legacy null then sits one typo away from it in any `if not …` test. No
    # `not_applicable` state, because no call class the parsers emit has a
    # structurally meaningless result — the provider-side ones have results
    # nobody captured, which is what `unobserved` says. `outcome_only` is the
    # one in-between an engine log produces: how the call ended, without what
    # it returned.
    result_capture: Literal["captured", "outcome_only", "unobserved"] | None = Field(
        default=None,
        description="Whether capture saw this call's result at all. `captured` means the "
        "engine log carried the call's result, in a paired result item or on the call "
        "item itself for an engine that settles it there; it does NOT mean the result had "
        "content — an empty result, or a failed one, is still captured. `outcome_only` "
        "means the engine logged how the call ENDED but not what it returned: Gemini's "
        "telemetry records each call's success bit and a failed call's error message, "
        "so `result_status` is legible on such a row while `result_digest` and "
        "`retrieved_doc_date` are null by construction — grade the call on its query, "
        "as for an unobserved one, but a `result_status` of `error` there is the engine "
        "saying the call failed. `unobserved` means no result reached the log: the call "
        "ran provider-side and echoed nothing back (a Codex hosted `web_search_call`), "
        "or capture found no result to pair with the call — "
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
        "no throttle shape, or on an `outcome_only` row the engine's logged failure (Gemini's "
        "`success` false, or a shell command's non-zero exit in its `metadata`). It is "
        "NOT gated on the tool name — it is a flag the engine set, "
        "not text a payload can forge, so a failed builtin is honestly an error — and it is "
        "a floor too, since only some engines set one. `ok` is the residual, and it is "
        "wide: captured, no engine error marker, and either not a manifest-tool call at all "
        "or a manifest result with no throttle shape. It is not proof the call succeeded. "
        "On an `outcome_only` row `throttled` reads the logged error message alone, so it "
        "sees a 429 the server raised as a tool error and never the citation tools' note "
        "on a successful result: a narrower floor than a captured row's. "
        "`unobserved` mirrors `result_capture` exactly: no result or outcome reached the "
        "log, so no condition could be read. Null on records written "
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
        "whose calls inside the program have no rows of their own (row-blind: only the "
        "wrapping call's head slice of program text and combined output were captured).",
    )

    @model_validator(mode="after")
    def _status_agrees_with_capture(self) -> RetrievalCall:
        """Reject a row whose result markers disagree about capture.

        The states are one fact read twice — a condition can be read exactly
        when a result or an outcome was captured — so `unobserved` must appear in both fields
        or in neither. Checked rather than derived, because each field is
        written by the same parser pass and a disagreement means that pass is
        broken, not that one field needs refreshing. Only when both are
        present: a null in either is the legacy record's capture-unknown, which
        constrains nothing. An ``outcome_only`` row is held to its name as well:
        no result reached the log, so nothing can have been digested or dated.
        """
        if self.result_capture is None or self.result_status is None:
            return self
        if (self.result_capture == "unobserved") != (self.result_status == "unobserved"):
            raise ValueError(
                f"result_capture={self.result_capture!r} and "
                f"result_status={self.result_status!r} disagree about whether this call's "
                f"result was captured; `unobserved` belongs in both or neither"
            )
        if self.result_capture == "outcome_only" and (
            self.result_digest is not None or self.retrieved_doc_date is not None
        ):
            raise ValueError(
                "an `outcome_only` row carries no result, so it can carry neither a "
                "result_digest nor a retrieved_doc_date"
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
    (a Gemini cell captured before its rows carried the logged outcome), or one
    that called no manifest tool at all. A throttle is only countable where a
    manifest result or outcome reached the log,
    so a ``0`` from such a log would assert a clean run out of a blind one; the
    null says the question could not be asked instead.
    """
    observed = observed_mcp_conditions(calls)
    if not observed:
        return None
    return sum(1 for call in observed if call.result_status == "throttled")


# Tool spellings that can carry a filing URL in their query slice without the
# call having fetched anything — a web *search* whose query happens to be a URL,
# a file write whose body quotes the link the cell recorded, a file read or
# search over text that names it. Each is listed in **both** spellings a
# committed row can carry: the engines' own names, and the engine-neutral class
# `fedcourtsai.blinding.neutral_tool_class` respells them as on a blinded log.
# The pair lets :func:`self_provisioned_fetches` answer the same over a staged
# log as over the log it was masked from, exactly as :func:`normalize_call`'s
# two MCP spellings do. Nothing depends on that today — the mask drops the
# log-level count, and no caller runs this predicate over staged rows — so read
# it as the cheap version of a property that would otherwise have to be
# rediscovered, not as a load-bearing mechanism. Two entries deliberately break
# it, and say so where they sit.
# `test_the_non_fetch_tools_carry_both_spellings` pins the set against that map
# in both directions, so a rename there fails a test rather than silently
# admitting a row, and a stale entry here fails rather than lingering.
#
# Everything absent from this set reaches :func:`_fetched_with`'s remaining
# tests rather than being screened here, the unclassified `other` included, and
# that direction is deliberate. A blinded row spells every unmapped builtin
# `other`, so screening `other` would drop exactly the code-mode
# command-running builtins (`exec_command`, `write_stdin`) through which one
# engine does most of its fetching — and would drop them on the blinded side
# only, making the two views of one log disagree about a number neither is
# supposed to change. What keeps that admission honest is the HTTP-client test
# those rows then face (:data:`_HTTP_CLIENT`), not this set.
_NON_FETCH_TOOLS: Final[frozenset[str]] = frozenset(
    {
        "websearch",
        "web_search",
        "web_search_call",
        "google_web_search",
        "web-search",
        "read",
        "read_file",
        "read_many_files",
        "file-read",
        "write",
        "write_file",
        "edit",
        "replace",
        "apply_patch",
        "file-write",
        "glob",
        "grep",
        "grep_search",
        "list_directory",
        "search_file_content",
        "file-search",
        # The code-mode lift's two PROSE builtins, beside the `apply_patch`
        # above. A code-mode program's plan step and image reference carry the
        # program's own writing as their argument text, and that text becomes
        # the row's query slice verbatim — so a plan step reading "curl the
        # opposition brief at <url>" names both a filing URL and an HTTP
        # client, and would be counted as the fetch it describes. The
        # command-running pair beside them (`exec_command`, `write_stdin`) is
        # deliberately NOT here: that is where a code-mode engine does its
        # fetching.
        #
        # These two are the one place the raw and masked spellings disagree,
        # because the neutral map has no entry for either and both stage as
        # `other`, which must stay fetch-capable for the command-running pair.
        # The disagreement is affordable precisely here: the log-level count
        # never reaches a blinded log (the mask drops it), and no caller runs
        # this predicate over staged rows. State it rather than trade a
        # standing false positive for it.
        "update_plan",
        "view_image",
    }
)

# A URL naming a **filed document** — the thing a provisioned
# `record/documents/` carries, and the thing a cell reaches past the record to
# get when that set is short one.
#
# Two trees, and the narrowness is the point. `supremecourt.gov/DocketPDF/` is
# where the Court serves the parties' filings themselves (petition, brief in
# opposition, reply, appendix, amicus), and it is the tree the cells' own flags
# name when they report recovering a brief the record lacked. The Court's other
# trees are deliberately outside it: `/opinions/` and `/orders/` are the Court's
# own output rather than a party filing, `/ctrules/` and `/filingandrules/` are
# the rulebook, and `/docket/` is the docket sheet the record already provides —
# a cell reading any of them retrieved something, but not a filing its document
# set was short of. `storage.courtlistener.com/recap/` is the same class of
# object served by RECAP's document store.
#
# Matched against the row's query slice, which capture caps at 500 characters,
# so a URL sitting past that cut is not seen: the count is a floor.
_FILING_DOCUMENT_URL = re.compile(
    r"https?://(?:www\.)?(?:supremecourt\.gov/DocketPDF/|storage\.courtlistener\.com/recap/)",
    re.IGNORECASE,
)

# The engines' dedicated open-web fetch tools, in both spellings a committed row
# can carry (the engines' own, and the blinding mask's neutral class). Such a
# call *is* the retrieval, so a filing URL in its params is a fetch on its own.
_FETCH_TOOLS: Final[frozenset[str]] = frozenset({"webfetch", "web_fetch", "web-fetch"})

# An HTTP client named in a command line — the evidence a **shell** row asks
# for before it is read as a fetch.
#
# A shell row is the commonest way a cell actually pulls a filing (`curl` into
# `pdftotext`, a `python` heredoc around `httpx`), so it cannot be excluded; but
# a shell row is also how a cell *writes prose about* a filing, and one command
# in particular — the patch builtin applying a diff to the cell's own
# `retrieval.md` — carries whole paragraphs naming the URL it tried and failed
# to fetch. Counting that would record a cell that obtained nothing as one that
# self-provisioned, which is the reading this exists to get right. So a shell
# row must name a client in the same slice. The screen is on the command text
# rather than on the tool, because the patch builtin arrives under the same
# shell-running name a real `curl` does, and it errs toward missing a fetch
# (a client past the 500-character cut, or one spelled some other way) rather
# than inventing one.
_HTTP_CLIENT = re.compile(
    r"""\b(?:
          curl | wget | httpx | urllib | urllib2 | urllib3 | requests | aiohttp
        | http\.client | pycurl | invoke-webrequest
    )\b""",
    re.IGNORECASE | re.VERBOSE,
)

# Where one command in a captured line ends and the next begins — the same cut
# :func:`~fedcourtsai.collect.attempted_corpus_query` makes, because the
# question is the same: only the segment the match sits in decides what ran.
# Newlines are separators here, which is why the client is looked for across
# the whole slice and only the *reader* screen below is segmented: a program
# that imports `httpx` on one line and names the URL on another is one command,
# and segmenting the client test would miss every such fetch.
_SHELL_SEGMENT = re.compile(r"[\n;|&]+")
# Commands that take a URL as *text to read* rather than as somewhere to go. A
# cell grepping its own notes for the brief it failed to fetch names both the
# URL and `curl`, which is the residual the client test alone leaves; the
# sibling corpus-query predicate closes the same shape the same way.
_READS_TEXT = re.compile(
    r"\b(?:rg|ripgrep|grep|egrep|fgrep|sed|awk|less|head|tail|cat|echo|printf)\b",
    re.IGNORECASE,
)


def _fetched_with(call: RetrievalCall, query: str) -> bool:
    """Whether this row is one a filing could have been *fetched* through.

    Three classes, and the third is the one that needs evidence:

    * a :data:`_NON_FETCH_TOOLS` row never is — it can only have searched for
      the URL or written it down;
    * a dedicated fetch tool (:data:`_FETCH_TOOLS`) or a **manifest** tool
      always is, because the call is itself a retrieval channel — except a
      manifest *search*, held out on the same ground as an engine's own: a
      search asks a question and a fetch takes a document, and the same
      ``search`` in either vocabulary means the same thing. The held-out set is
      decided by an underscore-delimited **token**, not a substring, so a tool
      whose name merely contains the letters (``research_document``) is not
      swept out with the searches;
    * anything else — a shell call, a code-mode command-running builtin, an
      unclassified builtin a blinded log spells ``other`` — is one only where
      its command text names an HTTP client (:data:`_HTTP_CLIENT`) and the URL
      does not sit in the arguments of a command that only *reads text*
      (:data:`_READS_TEXT`), because both shapes carry a cell's own prose about
      a fetch rather than the fetch.
    """
    lowered = call.tool.lower()
    if lowered in _NON_FETCH_TOOLS:
        return False
    if lowered in _FETCH_TOOLS:
        return True
    normalized = normalize_call(call.tool)
    if normalized is not None:
        return "search" not in normalized.split(".", 1)[1].split("_")
    if _HTTP_CLIENT.search(query) is None:
        return False
    match = _FILING_DOCUMENT_URL.search(query)
    segment = _SHELL_SEGMENT.split(query[: match.start()])[-1] if match else query
    return _READS_TEXT.search(segment) is None


def self_provisioned_fetches(calls: Sequence[RetrievalCall]) -> list[RetrievalCall]:
    """The calls through which this cell reached outside its record for a filing.

    The provisioned snapshot is every predictor's guaranteed-common input, and
    `record/documents/` is the filed text inside it. Where that set is short a
    filing, some cells reach past the record and fetch it from the Court's own
    document tree while others do not — so a fan-out that reads as one
    comparison was run over two different information sets. Nothing else records
    that: the fetch leaves a row in the cell's log and no mark on the
    prediction. This is the predicate that finds those rows. No score or rank
    reads it; the leaderboard only describes with it — each figure's cells by
    reading, and a paired reading over the events on which no engine's log
    shows such a fetch (:func:`fedcourtsai.leaderboard.cell_provisioning`). It
    records a
    *reach*, not an acquisition: the row is the call, and whether anything came
    back is ``result_status``'s business, so a refused fetch counts here and
    moved no information set.

    Two conditions, both on the row, and neither consults the record:

    * the row's ``query`` slice carries a **filing-document URL**
      (:data:`_FILING_DOCUMENT_URL`) — the Court's ``DocketPDF`` tree or
      RECAP's document store, and not the opinion, order, rules or docket-sheet
      trees beside them, which are not the filings a cell's document set is
      short of;
    * and the row is one the filing could have been **fetched through**
      (:func:`_fetched_with`) — a dedicated fetch tool or a manifest tool on
      its own, a shell call only where its command names an HTTP client, and a
      web search, file read, file write or file search never.

    What it does **not** do is ask whether the record already carried that
    filing, and the reason is that nothing here can. The manifest that would
    answer it, ``record/documents/documents.json``, lives in the cell's
    workspace and is thrown away with the runner; it names document *kinds*
    where a row names a URL, so even with both in hand the join is a guess. So
    this counts any filing fetch rather than only a repairing one, and a cell
    that fetched a filing it had been given counts alongside one that fetched a
    filing it had not. Read a non-zero count as *this cell reached past the
    provisioned set for filing text* and read the cell's own ``flags.json``
    beside it, which is where a predictor that noticed a gap says so.

    A floor, and unevenly so across engines, which is the limit that matters
    most since the very reading this supports is a comparison between them.
    Only a call that left a row can be seen. The row keeps 500 characters of
    its params, so a URL — or the client name a shell row is read against —
    past that cut is invisible. One engine's hosted web search carries a bare
    URL as its query, which this declines to count, because a search is not a
    fetch and such a row records no result either way. A fetch tool called
    with a prompt beside its URL keeps the URL at the head of its slice, so
    its target is legible; a log captured before that slice rule held its
    prompt alone (``docs/freeze-record.md`` dates the change), and on such a
    log a prompted fetch is one this cannot see at all — so read a zero as
    *no filing fetch was legible here*, and read two engines' counts side by
    side only with that in view. Nor does it claim the fetch **succeeded**: a row is evidence
    that the cell reached for the filing, and the result it came back with is
    ``result_status``'s business, which on a shell call is the engine's own
    marker rather than a reading of the payload.
    """
    return [
        call
        for call in calls
        if call.query is not None
        and _FILING_DOCUMENT_URL.search(call.query) is not None
        and _fetched_with(call, call.query)
    ]


# Any web address in a row's query slice: what makes a fetch's target legible.
_ANY_URL = re.compile(r"https?://", re.IGNORECASE)


def target_blind_fetches(calls: Sequence[RetrievalCall]) -> list[RetrievalCall]:
    """The dedicated-fetch calls whose query slice names no web address at all.

    The complement :func:`self_provisioned_fetches` cannot see: a row from an
    engine's own fetch tool (:data:`_FETCH_TOOLS`) whose slice carries no
    ``http(s)://`` anywhere, so whatever it fetched is unknown — it may have
    been a filing the record lacked. A prompted fetch on a log captured before
    the URL-first slice rule is the common case (its slice kept the prompt
    alone); a fetch whose prompt simply omits the address is the other. A
    cell holding any such row has a self-provisioning reading that is a floor:
    its zero means *no filing fetch was legible*, not *none happened*.
    """
    return [
        call
        for call in calls
        if call.tool.lower() in _FETCH_TOOLS
        and (call.query is None or _ANY_URL.search(call.query) is None)
    ]


CellMode = Literal["forward", "replay"]
"""The declared vocabulary of cell modes: a cell either forecasts a pending
outcome (``forward``) or replays a decided one (``replay``).

There is no third value and no ``unknown`` member: a record that cannot say
which it was carries ``None`` instead, so absence stays distinguishable from a
mode. Written here rather than restated at each read site, because the modes are
what the leakage rules key on — an out-of-vocabulary string reaching a grader as
if it were a mode is the failure this alias exists to make impossible.

One field stays a free ``str`` deliberately: :class:`PredictionContext`'s own
``mode``. That file is written into the agent's workspace, so its value is
checked at the read site — which can then say *which* value was refused, and
keep the rest of the cell's frozen conditioning — rather than failing the whole
record to a parse error.
"""


class CorpusServiceRequests(_Strict):
    """What the cell's corpus sidecar logged answering, read off its request log.

    The engine-agnostic half of the corpus-prior channel. Every other reading of
    whether a cell reached the corpus comes from the engine's own transcript
    (an attempt) or the cell's own ``tooling.json`` (a report), and both differ
    by engine in what they can see. The sidecar sits behind every engine's
    ``fedcourts query`` alike, so a count of the requests it answered says
    whether a query arrived, whatever the transcript shows.
    """

    queries: int = Field(ge=0, description="`/v1/query` requests the sidecar logged")
    queries_ok: int = Field(
        ge=0, description="Of `queries`, those answered 200: a query that returned rows or none"
    )
    open_events: int = Field(ge=0, description="`/v1/open-events` requests the sidecar logged")
    open_events_ok: int = Field(ge=0, description="Of `open_events`, those answered 200")

    @model_validator(mode="after")
    def _answered_within_asked(self) -> CorpusServiceRequests:
        """An answered count is a subset of the requests it counts."""
        if self.queries_ok > self.queries or self.open_events_ok > self.open_events:
            raise ValueError("an `_ok` count cannot exceed the requests it is a subset of")
        return self


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
    mode: CellMode | None = Field(
        default=None,
        description="The cell's provisioned mode: forward | replay; None where the "
        "harness could not establish one — an unprovisioned cell, a context "
        "carrying a value outside the vocabulary, or a record written before the "
        "field existed. The vocabulary is enforced here rather than trusted from "
        "the caller, because this field keys the leakage and tool-usage cuts",
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
        "with its result unseen, which is the standing shape of a Gemini cell, whose rows "
        "are `outcome_only`: an outcome is not a result, so it does not count here. "
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

    self_provisioned_fetches: int | None = Field(
        default=None,
        ge=0,
        description="How many of this log's calls **reached outside the provisioned "
        "document set for a court filing** — a row whose query slice carries a "
        "filing-document URL (the Court's own `DocketPDF` tree, or RECAP's document store) "
        "through a tool that could have fetched with it. The provisioned "
        "`record/documents/` set is every "
        "predictor's guaranteed-common input, so a cell that repairs a gap in it by live "
        "fetch and a cell that cannot are not running on one information set, and nothing "
        "else records the difference: the call marks the log and not the prediction. "
        "DESCRIPTIVE ONLY — no score or rank key reads it and no cell leaves a headline "
        "figure because of it; the leaderboard "
        "counts each figure's cells by it and reads a paired figure over the events on which "
        "no engine's log shows such a fetch, both registered in the freeze record. "
        "A REACH, NOT AN ACQUISITION: the row is the call, and "
        "whether anything came back is `result_status`'s business — on a shell row the "
        "engine's own failure marker rather than a read of the payload — so a refused or "
        "404'd fetch counts here and moved no information set. Condition on "
        "`result_status` before reading a count as filing text the cell actually got. It "
        "also does NOT say the record lacked what was fetched: "
        "the manifest that could answer that is thrown away with the runner and names "
        "document KINDS where a row names a URL, so a cell that re-fetched a filing it "
        "already had counts the same as one that recovered a filing it never got. Read a "
        "non-zero count as `this cell reached past the record for filing text` and "
        "read its `flags.json` beside it. A floor, and UNEVENLY SO ACROSS ENGINES, which "
        "bites exactly where the reading is a comparison between them: a call that left no "
        "row is not here; a URL past the row's 500-character query cut is not seen; one "
        "engine's hosted web search carries a bare URL as its query and is deliberately "
        "not counted, since a search is not a fetch and such a row captures no result "
        "either way; and on a log captured before a prompted fetch kept its URL (the "
        "freeze record dates the slice rule) a fetch tool called with a prompt beside its "
        "URL kept the prompt alone, so its fetch is invisible there however plainly it "
        "fetched. A 0 means `no filing fetch was legible`, never `none happened`. "
        "Excluded on a different ground are the tools that can only have written the URL "
        "down — a file write, read or search, and the code-mode lift's prose builtins "
        "(a patch, a plan step, an image reference), whose argument text is the cell's "
        "own writing about a fetch rather than the fetch — and a shell row whose command "
        "either names no HTTP client or reads the URL as text (a `grep` of the cell's own "
        "notes names both the client and the URL). Two residual doors are NOT closed: a "
        "manifest tool that takes arbitrary text rather than an address (the citation "
        "tools) counts if a pasted brief quotes a filing URL, and a search-paginating "
        "tool is read as a fetch channel. Unlike `result_capture_coverage` and `throttled_calls` "
        "this is BAKED AT CAPTURE and never re-derived on load, so a committed log reads "
        "back exactly as written and a LEDGER-WIDE cut over these fields pools whatever "
        "predicate each log was minted under. The collect job's per-run note is the other "
        "case and reads the other way: it re-derives over the committed rows, so it "
        "always speaks today's predicate and agrees with this field for any run captured "
        "under the same one. The blinding mask DROPS this field rather than staging it, "
        "so it never reaches an evaluator — what a reach leaves in a query slice depends "
        "on how an engine spells its tools, and the grading reads the rows. Null on "
        "records written before the field existed: "
        "unasked, not zero — a real 0 is the stronger claim that the rows were read and "
        "carried no such call.",
    )
    corpus_service: CorpusServiceRequests | None = Field(
        default=None,
        description="The requests the cell's corpus sidecar logged, counted off its "
        "request log after the agent finished. The sidecar answers every engine's "
        "`fedcourts query` and `open-events` alike, so this is the one corpus-use "
        "reading that does not depend on what an engine's transcript shows: a cell "
        "whose transcript holds a well-formed query and whose count is zero sent "
        "nothing the service received. DESCRIPTIVE ONLY: no score or rank key reads "
        "it. The log sits in the cell's workspace, so like `record/context.json` it "
        "is a file the agent could have altered. A request line carries only the "
        "route constant and the status, and only a line in that shape counts. Counts "
        "the whole job, which is one cell. Dropped by the blinding mask, since how "
        "often a cell queries is engine-shaped. Null where no sidecar log was read: "
        "a job with no sidecar, a log that was missing, or a record written before "
        "the field existed",
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

    Two skill columns form a pair here, and they are never blended either.
    ``population_brier_skill_score`` scores against the strictly-prior pooled
    band rate — the leakage-safe baseline, and the primary outcome measure — while
    ``population_realized_term_skill_score`` holds the level at the rate the case's own
    Term actually realized. Together they decompose skill **per cell**: the
    first rewards knowing the level *and* discriminating within it, the second
    nets the level out and leaves discrimination alone. Different baselines
    answer different questions, so no figure combines them, only the first may
    rank, and — since the second qualifies a narrower, never-identical set of
    cells, which its own ``*_scored`` count records — the two are not a
    difference either.

    A third, ``population_in_sample_skill_score``, is a post-hoc descriptive
    benchmark rather than a member of that pair: it scores against the block's
    own in-sample grant rate (``in_sample_grant_rate``), which contains every
    scored case's outcome, so it is hindsight by construction and never ranks.

    All three are **population** skills, ``1 - sum(brier) / sum(baseline_brier)``
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
        "beside it is the true denominator. Averaged over **gradings** — one "
        "per cell per judge, so weighted by panel depth — whereas "
        "`events_scored` counts events. Null when no cell in the stratum "
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
    population_in_sample_skill_score: float | None = Field(
        default=None,
        le=1.0,
        description="A **post-hoc descriptive benchmark**: Brier skill against "
        "the constant `in_sample_grant_rate` — the sample climatology of this "
        "very block's scored events, the case being scored included — "
        "aggregated as the same population ratio as the other skill columns, "
        "`1 - sum(cell Brier) / sum((c - y)^2)`, over the "
        "`in_sample_skill_scored` gradings. Its baseline nets out the block's "
        "level and nothing finer, the scored case's own outcome included, so it "
        "measures discrimination within the block — between-band separation "
        "included wherever the block pools bands; `by_band` is the within-band "
        "reading — net of miscalibration against the block's own base rate: at "
        "uniform panel depth, with forecasts grouped at their distinct values, "
        "it equals (resolution - reliability) / uncertainty in the Murphy "
        "decomposition, and only approximately where depth varies by event. "
        "Hindsight by construction — the rate exists only once every scored "
        "event has resolved — so it never ranks, is never a headline, and is "
        "never pooled or differenced with population_brier_skill_score (the "
        "strictly-prior band rate, the primary outcome measure) or "
        "population_realized_term_skill_score (a Term-wide band rate, "
        "leave-one-out, at the pack's term-to-date vintage). Cert cells only "
        "(the cells carrying outcome facts); null where the rate is 0 or 1, "
        "since every reference Brier is then 0",
    )
    in_sample_skill_scored: int = Field(
        default=0,
        ge=0,
        description="Gradings contributing to population_in_sample_skill_score: "
        "every grading in the block carrying a Brier score and cert outcome "
        "facts. 0 wherever the figure is null — including where "
        "`in_sample_grant_rate` is 0 or 1, and where any such grading's "
        "stamped Brier no longer reproduces from the scored prediction against "
        "the committed outcome (a Brier taken against a superseded outcome, "
        "which no baseline read off the current one may be paired with)",
    )
    in_sample_grant_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The in-sample constant population_in_sample_skill_score "
        "scores against: the mean binary target `Outcome.actual_granted` over "
        "the `in_sample_events_scored` distinct events of the gradings that "
        "column scores, each event counted once however many judges graded "
        "it. On the binary target rather than the grant family, so a "
        "`granted-in-part` outcome counts as a grant here, as it does in "
        "every Brier score; elsewhere the two coincide. Published even where "
        "it is 0 or 1 and the skill is null. Null where no grading qualifies",
    )
    in_sample_events_scored: int = Field(
        default=0,
        ge=0,
        description="Distinct (case, event) pairs in `in_sample_grant_rate`'s "
        "denominator — the events of the `in_sample_skill_scored` gradings "
        "(or, where the skill is null, of the gradings that would have been)",
    )
    always_deny_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="What a constant `denied` call would have scored on the "
        "**same gradings** `accuracy` averages — every cell counted in "
        "`accuracy_scored`, one per judge, so like `accuracy` it is weighted by "
        "panel depth; `event_always_deny_accuracy` is the per-petition "
        "reading. Each cell applies the exact-match rule `Evaluation.correct` "
        "uses (`pipeline.evaluate.is_correct`) to a synthetic `denied` "
        "prediction against the cell's committed outcome, so any non-`denied` "
        "outcome — a GVR included — is a miss. This is the floor **realized** "
        "on these cells. It is not comparable with the registered per-band "
        "figures in metrics/README.md, which are complements of grant-family "
        "rates rather than exact-match floors; those rates stay the skill "
        "anchor. Cert stage only (the one stage whose disposition axis "
        "`denied` is the null call on). Null elsewhere; null wherever any "
        "accuracy-scored cell lacks band/outcome facts; and null where any "
        "accuracy-scored cell's stamped `correct` no longer reproduces "
        "against the committed outcome — a grading paired with a superseded "
        "outcome, beside which a floor read off the current one would be an "
        "unpaired comparison",
    )
    accuracy_lift: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="`accuracy - always_deny_accuracy`: the paired difference "
        "over the identical gradings, so it is null exactly where "
        "`always_deny_accuracy` is. Grading-weighted like both terms; "
        "`event_accuracy_lift` is the per-petition reading. Never a rank key",
    )
    accuracy_events_scored: int = Field(
        default=0,
        ge=0,
        description="Distinct (case, event) pairs carrying at least one "
        "accuracy-scored grading — the per-petition denominator of the "
        "`event_*` fields, against the grading count `accuracy_scored`",
    )
    event_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Accuracy with each event counted once: the mean, over "
        "the `accuracy_events_scored` events, of the event's `correct`. A "
        "grading's `correct` is a function of the scored prediction and the "
        "outcome, so a block's gradings of one event agree on it; where they "
        "do not (gradings of different prediction runs, or one stamped "
        "against a superseded outcome), this field and the other `event_*` "
        "fields are null rather than picking one. The per-petition reading, "
        "free of the panel-depth weighting `accuracy` carries",
    )
    event_always_deny_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="`always_deny_accuracy` with each event counted once, "
        "over the same `accuracy_events_scored` events as `event_accuracy`. "
        "Null wherever `always_deny_accuracy` or `event_accuracy` is",
    )
    event_accuracy_lift: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="`event_accuracy - event_always_deny_accuracy`: the "
        "per-petition lift over the realized floor, paired over the same "
        "events. The published per-band reading. Never a rank key",
    )
    grants_realized: int | None = Field(
        default=None,
        ge=0,
        description="Distinct (case, event) pairs among the accuracy-scored "
        "cells whose outcome is in the **grant family** the band rates count "
        "(`GRANT_FAMILY_DISPOSITIONS`: granted, GVR, summary reversal — "
        "`granted-in-part` keeps its own statpack bucket and is excluded). An "
        "unrestricted audit count over every accuracy-scored event: compare "
        "`grants_expected` with `grants_realized_expected_scored`, not with "
        "this. Counts events, not gradings. Cert stage only; null wherever "
        "any accuracy-scored cell lacks band/outcome facts",
    )
    grants_expected: float | None = Field(
        default=None,
        ge=0.0,
        description="Sum, over the distinct (case, event) pairs among the "
        "accuracy-scored cells that carry one, of the event's registered "
        "strictly-prior segment base rate — the `Evaluation.segment_base_rate` "
        "the prior-Term skill column scores against, taken only from gradings "
        "that column admits and averaged over an event's gradings, so each "
        "event enters once. The grant count a forecaster at the registered "
        "band rate would have expected over the `grants_expected_scored` "
        "events; the realized count over exactly those events is "
        "`grants_realized_expected_scored`, and those two are the pair to "
        "compare. Cert stage only; null where no event carries a rate",
    )
    grants_expected_scored: int | None = Field(
        default=None,
        ge=0,
        description="Distinct (case, event) pairs contributing to "
        "`grants_expected` — its true denominator. Below "
        "`accuracy_events_scored` wherever an event carries no admitted base "
        "rate; null where `grants_realized` is",
    )
    grants_realized_expected_scored: int | None = Field(
        default=None,
        ge=0,
        description="Grant-family events (as `grants_realized` counts them) "
        "among exactly the `grants_expected_scored` events — the realized "
        "side of the expected-vs-realized pair, over the same events as "
        "`grants_expected`. Null where `grants_realized` is",
    )
    mean_vote_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean, over the `vote_cells_scored` cells, of each cell's "
        "participating-bench vote accuracy: the fraction of the Justices the "
        "outcome's complete vote record shows sitting whose vote the scored "
        "prediction called, an omitted Justice a miss "
        "(`pipeline.evaluate.bench_vote_accuracy`), recomputed from the committed "
        "prediction and outcome rather than read off `Evaluation.vote_accuracy`. "
        "Merits-moment cells whose outcome carries a complete vote record "
        "(`vote_provenance.complete`) only, so it covers the decisions a vote "
        "source read completely — signed opinions whose lineup parsed — not every "
        "merits decision. Averaged over **gradings**, like `accuracy`: the "
        "figure does not depend on the judge, so a prediction graded by three "
        "evaluators enters three times with one value and the mean is weighted "
        "by panel depth. Null where no cell qualifies. Never a rank key",
    )
    vote_cells_scored: int = Field(
        default=0,
        ge=0,
        description="Gradings that entered `mean_vote_accuracy` — its denominator, "
        "counted per evaluation as `accuracy_scored` is, so it exceeds the number "
        "of distinct predictions scored wherever a panel graded one more than "
        "once. Below `evaluations` wherever a cell is off a merits moment, has no "
        "readable scored prediction, or resolves against a vote record that is "
        "absent or incomplete",
    )
    mean_reasoning_quality: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean evaluator reasoning-quality score, pooled over every judge rubric "
        "in `reasoning_quality_rubrics`. Spanning more than one digest of one evaluator, it "
        "is coverage; the per-rubric reading is the claimable figure",
    )
    reasoning_quality_rubrics: list[RubricReading] = Field(
        default_factory=list,
        description="`mean_reasoning_quality` read per (evaluator, evaluate digest): each "
        "rubric the mean draws on, with its `n` in graded gradings and the mean over those "
        "alone. Omitted while no grading carries a grade",
    )

    @model_serializer(mode="wrap")
    def _omit_ungraded(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``reasoning_quality_rubrics`` while it lists nothing."""
        return _omit_empty(handler(self), reasoning_quality_rubrics=self.reasoning_quality_rubrics)


class WindowCount(_Strict):
    """One (predictor, counting window) series inside a figure that pools across predictors.

    A frozen-scope figure keyed on something other than the forecaster — a
    judge-validation coefficient, a grader-agreement read, a calibration over
    every engine's cells — pools whatever series its cells come from. It is
    the **record across those series**: it lists each series and its ``n``
    beside the pooled value, a single series included, and is never a rank key
    (``docs/process-version.md``, *Pooled by default*). It names its predictor
    because such a figure pools several; :class:`WindowShare` is the
    one-predictor form a predictor's own pooled figure lists.
    """

    predictor_id: str
    process_window: str = Field(description="The counting window's label (e.g. `proc-v8`)")
    n: int = Field(
        ge=0,
        description="This series' share of the pooled figure's population, in the unit the "
        "containing `windows` field names (cells or reads) — not necessarily the unit of the "
        "figure's own count, so the n need not sum to it",
    )


_POOLED_WINDOWS_DESCRIPTION = (
    "Listed whenever the figure is a frozen-scope pool, a single label included — "
    "the figure is the record across those series, never one series and never a "
    "rank key. Empty on an all-versions build, whose cells carry no window"
)


_RUBRIC_COVERAGE = (
    "A figure spanning more than one digest of one evaluator mixes judge rubrics, so it "
    "is coverage, never a claimable figure, until the per-rubric reading is built"
)

_RUBRIC_COVERAGE_READ = (
    "A figure spanning more than one digest of one evaluator mixes judge rubrics, so it "
    "is coverage, never a claimable figure; `by_signature` carries the claimable per-rubric "
    "readings"
)

_BY_SIGNATURE_DESCRIPTION = (
    "The figure read per rubric signature: one reading per maximal set of (evaluator, "
    "evaluate digest) pairs some point's reads carry, over every point whose own pairs it "
    "holds. A point may sit in two readings, so readings sharing points are not independent "
    "and are never differenced as if they were, and their `cases` need not sum to the "
    "pooled count. Check each pair's `n` before quoting a reading: a single point read "
    "under a new digest can form a maximal signature whose distinguishing pair has n=1. "
    "The per-rubric reading is the claimable figure; the pooled value is coverage wherever "
    "it spans more than one digest of one evaluator"
)

_MIXED_SIGNATURE_DESCRIPTION = (
    "Points whose reads carry one evaluator under two digests, so they span two signatures "
    "and enter no reading in `by_signature`; they still count in the pooled value. Such "
    "points concentrate in cases read at several moments, the granted ones, so after a "
    "digest move a reading covers a population short of exactly the higher-stakes cases; "
    "compare each reading's `cases` with the figure's own count. Omitted at zero"
)


def _omit_empty(payload: Any, **fields: object) -> Any:
    """Drop each named field from a serialized payload while its value is empty."""
    if isinstance(payload, dict):
        for name, value in fields.items():
            if not value:
                payload.pop(name, None)
    return payload


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
        description="Cases this evaluator and at least one peer both read, one "
        "leave-one-out point per case (its moments averaged) despite the name — the sample "
        "the correlation rests on, and small enough to matter",
    )
    windows: list[WindowCount] = Field(
        default_factory=list,
        description="The predictor windows whose graded cells this evaluator's reads came "
        "from, each with its count of the reads that entered a point — a case some peer "
        "also read. The view compares graders, so it pools the predictors' windows by "
        "design and states them here instead. " + _POOLED_WINDOWS_DESCRIPTION,
    )
    rubrics: list[RubricCount] = Field(
        default_factory=list,
        description="The (evaluator, evaluate digest) pairs of every read behind this "
        "evaluator's points — its own and its peers', since a leave-one-out point compares "
        "the two — each with its `n` in reads. " + _RUBRIC_COVERAGE_READ,
    )
    by_signature: list[SignatureReading] = Field(
        default_factory=list,
        description=_BY_SIGNATURE_DESCRIPTION + ". A leave-one-out point's reads are the "
        "evaluator's and its peers' on the case. Each reading's `cases` compares to this "
        "figure's `events`, its pooled count of cases",
    )
    mixed_signature_points: int = Field(default=0, ge=0, description=_MIXED_SIGNATURE_DESCRIPTION)

    @model_serializer(mode="wrap")
    def _omit_single_label(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop the composition and per-rubric fields while they list nothing."""
        return _omit_empty(
            handler(self),
            windows=self.windows,
            rubrics=self.rubrics,
            by_signature=self.by_signature,
            mixed_signature_points=self.mixed_signature_points,
        )


class BigCaseLeaderboard(_Strict):
    """A predictor's big-case-score agreement with the evaluator panel's stakes reads.

    A *second* skill dimension, orthogonal to the grant/deny ranking (a model can
    read a case's significance well while calling grant/deny only modestly, or the
    reverse). Bigness is comparative, so the agreement is a **rank** correlation —
    Kendall's tau-b between the predictor's ``big_case_score`` ordering and the
    panel's (the mean of the evaluators' own reads), across the scored
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
    windows: list[WindowShare] = Field(
        default_factory=list,
        description="On a pooled reading, the counting windows the predictor's read cells "
        "come from, each with its `n` in panel reads; empty on a by-protocol cut, which is "
        "one window, and on an all-versions build",
    )
    rubrics: list[RubricCount] = Field(
        default_factory=list,
        description="The (evaluator, evaluate digest) pairs whose reads the panel mean draws "
        "on, each with its `n` in reads. " + _RUBRIC_COVERAGE_READ,
    )
    by_signature: list[SignatureReading] = Field(
        default_factory=list,
        description=_BY_SIGNATURE_DESCRIPTION + ". A case's point's reads are every panel "
        "read across its moments. Each reading's `cases` compares to this figure's `cases`",
    )
    mixed_signature_points: int = Field(default=0, ge=0, description=_MIXED_SIGNATURE_DESCRIPTION)

    @model_serializer(mode="wrap")
    def _omit_empty_composition(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop the composition and per-rubric fields while empty."""
        return _omit_empty(
            handler(self),
            windows=self.windows,
            rubrics=self.rubrics,
            by_signature=self.by_signature,
            mixed_signature_points=self.mixed_signature_points,
        )


class RubricCount(_Strict):
    """One judge rubric a judge-dependent figure draws on: an evaluator and its digest.

    A figure computed from an evaluator's judgment depends on the evaluate
    prompt, so it lists the (evaluator, digest) pairs its reads come from. A
    grading's rubric is its ``evaluator_id`` with the ``process_version.digest``
    on its harness stamp.
    """

    evaluator_id: str
    digest: str | None = Field(
        description="The evaluate process digest on the grading's harness stamp; null for an "
        "unstamped grading"
    )
    n: int = Field(ge=0, description="Reads or gradings drawn from this rubric")


_RUBRIC_LABELS_DESCRIPTION = (
    "The evaluate labels that blessed these digests, sorted, from the registry "
    "(`process_version.EVALUATE_BLESSING_LABELS`); an unstamped or never-blessed digest "
    "names none. A name only; a label never partitions a reading"
)


class RubricReading(_Strict):
    """A per-judge figure read over one judge rubric's gradings alone.

    A per-judge figure averages one evaluator's grades, so a pool across
    evaluator digests mixes judge rubrics. Its per-rubric reading — the figure
    over the gradings of one (evaluator, digest) pair — is the claimable figure,
    and the pooled value beside it is coverage wherever it spans more than one
    digest of one evaluator.
    """

    evaluator_id: str
    digest: str | None = Field(
        description="The evaluate process digest on the gradings' harness stamps; null for "
        "unstamped gradings"
    )
    labels: list[str] = Field(default_factory=list, description=_RUBRIC_LABELS_DESCRIPTION)
    n: int = Field(ge=0, description="Gradings under this rubric that carry a grade")
    mean_reasoning_quality: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean reasoning-quality grade over this rubric's gradings alone",
    )


class SignatureReading(_Strict):
    """A panel figure read over the points of one rubric signature.

    A panel figure combines several judges' reads, so its rubric is a
    *signature*: a sorted set of (evaluator, digest) pairs, one digest per
    evaluator. The signatures read are the maximal sets the points' own pairs
    form, so a case only part of a panel read is not split off from the panel
    it was read under. A point belongs to every signature holding all of its
    pairs; one whose reads hold an evaluator under two digests belongs to none.
    The correlation over one signature's points is the claimable figure.
    """

    signature: list[RubricCount] = Field(
        description="The signature's (evaluator, evaluate digest) pairs, each with its `n` in "
        "reads behind this reading's points"
    )
    labels: list[str] = Field(default_factory=list, description=_RUBRIC_LABELS_DESCRIPTION)
    rank_agreement: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Kendall's tau-b over this signature's points alone; null with fewer than "
        "2 points or when every pair ties on one side",
    )
    cases: int = Field(
        ge=0,
        description="Cases the reading rests on, one point each; against the figure's pooled "
        "count (`cases` on a big-case figure, `events` on an evaluator agreement) it shows "
        "how many points this signature leaves out",
    )


class WindowShare(_Strict):
    """One counting window's share of a pooled figure: its label, opening, and ``n``.

    A pooled figure is computed over every counted cell its predictor holds in
    every non-revoked window, and states its composition beside the value. The
    window is the one the cell's digest and harness stamp fall in, named by its
    own label and opening instant, never by the label on the cell's stamp: a
    cell of a carried-forward window stamped under a later label lists under
    the window it counts in.
    """

    process_window: str = Field(description="The counting window's label (e.g. `proc-v8`)")
    opens: datetime = Field(description="The instant the window opened")
    n: int = Field(
        ge=0,
        description="Gradings of this figure's population drawn from cells in this window",
    )


class BoundaryCount(_Strict):
    """A harness boundary inside a pooled figure's span: its cells on each side.

    A dated change to what a predict cell reads under an unchanged digest cuts
    nothing out of a pooled figure; it is listed as composition instead. A
    cell's side is read by ancestry — after where the carrying commit is an
    ancestor of, or equal to, its ``process_version.pipeline_sha`` — and a cell
    without one sits on neither side.
    """

    boundary: str = Field(description="The boundary's registered name")
    at: datetime = Field(
        description="The carrying commit's committer time — for display only; the side test "
        "is ancestry"
    )
    scope: str = Field(
        description="The cells the change can reach (`all`, `replay cells`, `self-represented "
        "dockets`, `granted dockets`), printed as scope and never used as a filter: whether a "
        "docket was self-represented or granted at a cell's moment lives only in the corpus. "
        "So for a docket-scoped boundary `after` is the cells that could have read the "
        "change, an upper bound on exposure"
    )
    gradual: bool = Field(
        default=False,
        description="The change reached the corpus through a back-fill pass, so a cell after "
        "it may still read the earlier document set: `after` is an upper bound on exposure "
        "whatever the scope. Omitted while false",
    )
    before: int = Field(ge=0, description="Cells of this figure built before the change")
    after: int = Field(
        ge=0,
        description="Cells of this figure built at or after the change; an upper bound on "
        "exposure wherever the change is docket-scoped or reached the corpus by back-fill",
    )
    unstamped: int = Field(
        default=0,
        ge=0,
        description="Cells the boundary admits that carry no `pipeline_sha`, so sit on neither "
        "side",
    )

    @model_serializer(mode="wrap")
    def _omit_not_gradual(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``gradual`` while false."""
        return _omit_empty(handler(self), gradual=self.gradual)


_BOUNDARIES_DESCRIPTION = (
    "Every registered harness boundary that falls inside this figure's cells' span — its "
    "carrying commit's time between their earliest and latest harness clock — and has "
    "cells on both sides or any cell with no `pipeline_sha`, with the counts on each side, "
    "over every cell the boundary's predictors and mode admit (a replay-only boundary counts "
    "replay cells alone). Cells, not gradings: one per (case, event). A boundary outside the "
    "span cuts nothing and is not listed; omitted while none is"
)


class SelfProvisioningCount(_Strict):
    """A figure's cells by whether their logs show a fetch of a court filing.

    Descriptive, never a filter and never a rank key. The provisioned
    `record/documents/` set is every predictor's guaranteed-common input; a cell
    whose log shows a legible fetch of a court filing outside it may have run on
    a different information set from a cell whose log does not. The reading is
    about filings only: other retrieval a forward cell may do without
    restriction is not counted. Counted in cells, one per (case, event,
    predictor), over the figure's cells, each read off its scored prediction's
    own retrieval log.
    """

    cells: int = Field(ge=0, description="Cells behind this figure")
    reached: int = Field(
        ge=0,
        description="Cells whose log holds at least one filing fetch "
        "(`self_provisioned_fetches` > 0): a reach, not an acquisition — a refused fetch "
        "counts — and not proof the record lacked the filing",
    )
    target_blind: int = Field(
        ge=0,
        description="Cells that did not reach legibly but hold a fetch-tool row whose slice "
        "names no web address, so a filing fetch could be hidden there. ENGINE-ASYMMETRIC: on "
        "a log captured before the URL-first slice rule every prompted fetch is such a row, "
        "so a cell of an engine whose fetch tool takes a prompt reads here whatever it "
        "fetched, while another engine's cell leaves `none` only on a legible filing fetch. "
        "Until such cells are gone, that engine's `reached` is a floor",
    )
    unlogged: int = Field(
        ge=0,
        description="Cells whose scored prediction or retrieval log could not be read, so "
        "nothing is known about what they fetched",
    )


_SELF_PROVISIONING_DESCRIPTION = (
    "This figure's cells by whether their logs show a fetch of a court filing outside the "
    "provisioned document set (see SelfProvisioningCount). Descriptive only: no rank key, "
    "headline figure or filter reads it. Omitted while no retrieval-log reading was supplied"
)


class CommonRecordEngine(_Strict):
    """One engine's figure over the common-record paired events."""

    predictor_id: str
    forward: LeaderboardStratum | None = Field(
        default=None,
        description="This engine's forward aggregate over its paired gradings on the "
        "common-record events, carrying that subset's own `always_deny_accuracy` and "
        "`in_sample_grant_rate` to be read against; null while there are none",
    )


class CommonRecordReading(_Strict):
    """The paired figure over the events no engine's log shows a filing fetch on.

    An event enters only where every engine's cell on it has a legible log with
    no filing fetch and no fetch-tool row naming no address
    (:class:`SelfProvisioningCount`): the paired events on which no engine's log
    shows a legible fetch of a court filing outside the provisioned set. It
    says nothing about other retrieval, which a forward cell may do without
    restriction.

    A **selected** subset, and not neutrally: a cell reaches past the record
    where the record is short and the case contested, so the selection runs on
    behaviour that tracks the outcome and the forecast's uncertainty — on
    granted and close petitions — and it drops an event for one engine's reach
    whatever the others did. Read each engine's figure against this subset's own
    always-deny floor and in-sample grant rate, never the full paired set's;
    never rank it, and never difference it against the paired figure.
    """

    events: int = Field(
        ge=0,
        description="Paired events on which no engine's log shows a legible fetch of a "
        "court filing outside the provisioned set, and every engine's log was read and "
        "names every fetch's target",
    )
    entries: list[CommonRecordEngine] = Field(
        default_factory=list,
        description="Per engine, in the paired figure's order",
    )


_COMPOSITION_DESCRIPTION = (
    "The windows this figure pools, each with its `n` in gradings, ordered by "
    "opening. Listed whenever the figure is a frozen-scope pool, a single window "
    "included; empty on an all-versions build, whose cells carry no window"
)


class PairedEngine(_Strict):
    """One engine's standing over a population's paired events.

    The aggregate over the engine's qualifying gradings on the events every
    engine in the paired set holds a qualifying cell on — the same events for
    every engine, whichever windows its cells come from — which is the only
    figure a cross-engine comparison or a rank is read off.
    """

    predictor_id: str
    rank: int | None = Field(
        default=None,
        ge=1,
        description="1-based standing over the paired events; 1 is best. Forward accuracy "
        "(highest first), then forward mean Brier (lowest first), then `predictor_id`. Null "
        "on an unranked block, and on every engine while the paired set is empty",
    )
    forward: LeaderboardStratum | None = Field(
        default=None,
        description="This engine's forward aggregate over its qualifying gradings on the "
        "paired events; null while the paired set is empty",
    )
    windows: list[WindowShare] = Field(
        default_factory=list,
        description="The windows this engine's paired gradings come from, each with its `n` "
        "in gradings",
    )
    by_band: dict[str, LeaderboardStratum] = Field(
        default_factory=dict,
        description="This engine's aggregate over its paired gradings, per band key — each "
        "paired event filed under the band `PairedEvents.by_band` assigns it (its earliest "
        "qualifying cell's), the same filing for every engine. The per-band reading: a "
        "per-band ordering is read off these, which share their events across engines by "
        "construction. Cert populations only; omitted while empty",
    )
    boundaries: list[BoundaryCount] = Field(
        default_factory=list,
        description=_BOUNDARIES_DESCRIPTION + ". Over this engine's cells on the paired events",
    )
    unpaired_events: int = Field(
        ge=0,
        description="This engine's qualifying events that are not paired, because some "
        "other engine in the set holds no qualifying cell on them: its pairing loss",
    )
    self_provisioning: SelfProvisioningCount | None = Field(
        default=None,
        description=_SELF_PROVISIONING_DESCRIPTION + ". Over this engine's cells on the paired "
        "events",
    )

    @model_serializer(mode="wrap")
    def _omit_empty_boundaries(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``boundaries``, ``by_band`` and ``self_provisioning`` while empty."""
        return _omit_empty(
            handler(self),
            boundaries=self.boundaries,
            by_band=self.by_band,
            self_provisioning=self.self_provisioning,
        )


class PairedEvents(_Strict):
    """A population's paired-event figure: the events every compared engine holds.

    A cross-engine comparison is read only over events on which every engine in
    the set holds a counted forward cell carrying both an accuracy and a Brier
    score, from any window. Pooling lets each engine's event set drift with its
    own history, so pooled entries side by side are not a comparison; this
    figure is. Adding or retiring an engine moves the set, and the figure names
    the engines it pairs.
    """

    predictors: list[str] = Field(
        default_factory=list,
        description="The engines paired, sorted: every predictor with a counting window "
        "neither closed nor revoked and at least one qualifying cell (on an all-versions "
        "build, every predictor with a qualifying cell)",
    )
    events: int = Field(
        default=0,
        ge=0,
        description="Events every listed engine holds a qualifying cell on — the paired `n` "
        "every rank is read over",
    )
    by_band: dict[str, int] = Field(
        default_factory=dict,
        description="The paired events per band key, each assigned the band of its earliest "
        "counted qualifying cell by harness clock. Cert populations only; omitted while empty",
    )
    band_mismatches: int = Field(
        default=0,
        ge=0,
        description="Paired events whose engines' cells carry different band keys. Expected "
        "to cluster where a band rose between engines' runs (relists, CVSGs) — the "
        "higher-grant events",
    )
    entries: list[PairedEngine] = Field(
        default_factory=list,
        description="Per engine, its standing over the paired events: in rank order on the "
        "ranked board, by `predictor_id` on an unranked block",
    )
    common_record: CommonRecordReading | None = Field(
        default=None,
        description="The paired figure restricted to the paired events on which no "
        "engine's log shows a legible fetch of a court filing outside the provisioned set "
        "(see CommonRecordReading). A selected subset — the selection tracks outcome and "
        "uncertainty — read against its own always-deny floor, never ranked and never "
        "differenced against the paired figure; omitted while no retrieval-log reading was "
        "supplied",
    )

    @model_serializer(mode="wrap")
    def _omit_empty_by_band(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``by_band`` and ``common_record`` while empty."""
        return _omit_empty(handler(self), by_band=self.by_band, common_record=self.common_record)


#: The key :attr:`LeaderboardEntry.by_band` files a cell under when its scored
#: prediction froze no band, or a band with no salience version to read it by.
NO_BAND_KEY: Final = "(none)"

_BY_BAND_DESCRIPTION = (
    "The **forward** stratum cut by salience band: one LeaderboardStratum "
    "per band, aggregated exactly as `forward` is — the same cells, after the "
    "run collapse and both exclusions, with the same skill terms. Keyed "
    "`<salience_version>/<band>` from the scored prediction's frozen "
    "`context`, never the corpus's current band, which only strengthens as a "
    "petition is relisted or a CVSG lands and so would sort a forecast by its "
    "own future. A cell whose context froze no band, or a band with no "
    "version, or that carries no band facts at all, files under the single "
    "`(none)` key, so the blocks' "
    "`evaluations` sum to `forward.evaluations`. Cert stage only — no other "
    "stage is a salience-band product — and omitted while there is no "
    "forward cert cell or no band facts were supplied. Never a rank key"
)


#: The :attr:`LeaderboardEntry.by_link` keys: the scored prediction froze a
#: ``Vide`` link, froze none, or froze no list at all (a payload not of the live
#: shape, or a prediction made before the context carried the list).
LINKED_KEY: Final = "linked"
UNLINKED_KEY: Final = "unlinked"
NO_LINK_KEY: Final = "(none)"

_BY_LINK_DESCRIPTION = (
    "The **forward** stratum cut by whether the docket was tied to another: one "
    "LeaderboardStratum per key, aggregated exactly as `forward` is — the same "
    "cells, after the run collapse and both exclusions, with the same skill "
    "terms. Keyed off the scored prediction's frozen `context.vide_links`: "
    "`linked` where it names at least one `Vide` link (a cross-petition, a "
    "companion, or the petition the docket is held for), `unlinked` where it "
    "names none, and `(none)` where it froze no list, so the blocks' "
    "`evaluations` sum to `forward.evaluations`. Cert stage only, and omitted "
    "while there is no forward cert cell or no cell facts were supplied. "
    "Descriptive: never a rank key"
)


_BY_PROTOCOL_DESCRIPTION = (
    "The by-protocol cut: one entry per (predictor, counting window), each over that "
    "window's counted cells alone, listed by predictor_id then the window's opening and "
    "never ranked. Two windows of one predictor share no event, and a successor's events "
    "are those the closed window did not reach — a selected population — so a move from "
    "one window's entry to the next is a comparison over different events, never a "
    "measurement of improvement. Frozen builds only; omitted while empty"
)


def _drop_empty_by_band(payload: Any, by_band: dict[str, LeaderboardStratum] | None) -> Any:
    """Drop an empty ``by_band`` from a serialized entry.

    The board's rule for optional axes (``Leaderboard.stages``): an axis is
    shown once its cells exist, so a stage or predictor with no forward cert
    cell carries no ``by_band`` key rather than a null placeholder.
    """
    if isinstance(payload, dict) and not by_band:
        payload.pop("by_band", None)
    return payload


class LeaderboardEntry(_Strict):
    """One predictor's standings, aggregated per stratum.

    Forward and retrospective are the pre-registration (timing) strata; the
    procedural block segments mootness-basis cells out of both.
    """

    predictor_id: str
    process_window: str | None = Field(
        default=None,
        description="On a `by_protocol` cut entry, the label of the counting window every "
        "cell behind it comes from (e.g. `proc-v8`). Null on a pooled entry, which spans "
        "the windows `windows` lists, and on every all-versions entry",
    )
    windows: list[WindowShare] = Field(default_factory=list, description=_COMPOSITION_DESCRIPTION)
    boundaries: list[BoundaryCount] = Field(
        default_factory=list,
        description=_BOUNDARIES_DESCRIPTION + ". On a pooled entry; never on a cut entry",
    )
    self_provisioning: SelfProvisioningCount | None = Field(
        default=None,
        description=_SELF_PROVISIONING_DESCRIPTION + ". On a pooled entry, over its "
        "`forward` stratum's cells, the stratum its figures beside it read; never on a cut "
        "entry",
    )
    rank: int | None = Field(
        default=None,
        ge=1,
        description="1-based standing; 1 is best — this predictor's rank over the board's "
        "paired events (`paired`), never read off this entry's own figures, which span an "
        "event set of their own. Null on a predictor outside the paired set (a retired one, "
        "or one with no qualifying forward cell), on every entry while the paired set is "
        "empty, and on every `by_protocol` cut entry",
    )
    paired_events: int | None = Field(
        default=None,
        ge=0,
        description="The paired `n` the rank is read over, printed beside it; null wherever "
        "`rank` is",
    )
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
    by_band: dict[str, LeaderboardStratum] | None = Field(
        default=None,
        description=_BY_BAND_DESCRIPTION,
    )
    by_link: dict[str, LeaderboardStratum] | None = Field(
        default=None,
        description=_BY_LINK_DESCRIPTION,
    )
    big_case: BigCaseLeaderboard | None = Field(
        default=None,
        description="The predictor's big-case-score rank-agreement with the "
        "evaluator panel (see BigCaseLeaderboard); a second, orthogonal skill "
        "dimension that never affects the ranking. Null when no case carries both "
        "a predictor big_case_score and an evaluator read.",
    )

    @model_serializer(mode="wrap")
    def _omit_empty_by_band(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``by_band`` and an empty ``windows`` — see :func:`_drop_empty_by_band`."""
        return _omit_empty(
            _drop_empty_by_band(handler(self), self.by_band),
            by_link=self.by_link,
            windows=self.windows,
            boundaries=self.boundaries,
            self_provisioning=self.self_provisioning,
        )


class LeaderboardStageEntry(_Strict):
    """One predictor's aggregates within a single non-cert stage.

    The same per-stratum aggregate shape as a ranked :class:`LeaderboardEntry`,
    minus the rank and the big-case dimension: a non-cert stage's cells resolve
    on a different decision standard than the cert board's, so they report
    separately and never rank — and never pool into any cert figure.
    """

    predictor_id: str
    process_window: str | None = Field(
        default=None,
        description="On a `by_protocol` cut entry, the label of the counting window every "
        "cell behind it comes from (e.g. `proc-v8`). Null on a pooled entry, which spans "
        "the windows `windows` lists, and on every all-versions entry",
    )
    windows: list[WindowShare] = Field(default_factory=list, description=_COMPOSITION_DESCRIPTION)
    boundaries: list[BoundaryCount] = Field(
        default_factory=list,
        description=_BOUNDARIES_DESCRIPTION + ". On a pooled entry; never on a cut entry",
    )
    self_provisioning: SelfProvisioningCount | None = Field(
        default=None,
        description=_SELF_PROVISIONING_DESCRIPTION + ". On a pooled entry, over its "
        "`forward` stratum's cells, the stratum its figures beside it read; never on a cut "
        "entry",
    )
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
    by_band: dict[str, LeaderboardStratum] | None = Field(
        default=None,
        description=_BY_BAND_DESCRIPTION,
    )
    by_link: dict[str, LeaderboardStratum] | None = Field(
        default=None,
        description=_BY_LINK_DESCRIPTION,
    )

    @model_serializer(mode="wrap")
    def _omit_empty_by_band(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``by_band`` and an empty ``windows`` — see :func:`_drop_empty_by_band`."""
        return _omit_empty(
            _drop_empty_by_band(handler(self), self.by_band),
            by_link=self.by_link,
            windows=self.windows,
            boundaries=self.boundaries,
            self_provisioning=self.self_provisioning,
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
        description="Per-predictor aggregates, each pooled over every counted cell in every "
        "non-revoked window with its composition in `windows`, ordered by predictor_id: an "
        "ordering, not a ranking",
    )
    by_protocol: list[LeaderboardStageEntry] = Field(
        default_factory=list,
        description=_BY_PROTOCOL_DESCRIPTION,
    )
    paired: PairedEvents | None = Field(
        default=None,
        description="The paired-event figure over this block's own events, unranked: the "
        "only figure an engine comparison in this block is read off. Null while no engine "
        "holds a qualifying cell",
    )

    @model_validator(mode="after")
    def _coverage_denominates_its_entries(self) -> LeaderboardStage:
        _check_coverage_denominator(self.events_scored, self.entries)
        return self

    @model_serializer(mode="wrap")
    def _omit_empty_cut(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``by_protocol`` and ``paired`` while empty, as ``by_band`` is."""
        return _omit_empty(handler(self), by_protocol=self.by_protocol, paired=self.paired)


class CountingWindow(_Strict):
    """One blessing of one predictor digest: the span its cells count in.

    The counting rule's unit (:data:`fedcourtsai.process_version.COUNTING_WINDOWS`).
    A window opens at the counting instant of the label that blessed the digest
    and closes at the counting instant of the successor that stops blessing it,
    each as its ``prereg/`` tag records it. A **closed** window's cells keep
    counting; a **revoked** one's are de-counted, which only a dated
    freeze-record entry stating a defect licenses. A digest carried forward
    byte-identical keeps one unbroken window; a digest blessed again after its
    window closed opens a new one.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True, frozen=True)

    label: str = Field(
        description="The process label whose blessing opened the window (e.g. `proc-v8`); "
        "the label every figure over the window is reported under"
    )
    digest: str = Field(description="The blessed predictor process digest (`sha256:<hex>`)")
    opens: datetime = Field(
        description="The counting instant that opened the window: a cell stamped at or "
        "after it (and before `closes`) is in the window"
    )
    closes: datetime | None = Field(
        default=None,
        description="The successor's counting instant that closed the window, exclusive; "
        "null while the window is open. Closing de-counts nothing",
    )
    revoked_at: datetime | None = Field(
        default=None,
        description="When a dated revocation de-counted the window's cells for a defect — "
        "at or after the merge of the promotion that carried it, and only on a closed "
        "window; null for a window that counts",
    )
    predictor_id: str | None = Field(
        default=None,
        description="The predictor whose process the digest is — a fact about the digest, "
        "recorded so a reader can tell which predictors still hold an open window (the "
        "ranked set's condition) without recomputing digests. Omitted where unrecorded",
    )

    @model_serializer(mode="wrap")
    def _omit_unrecorded_predictor(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``predictor_id`` while it is unrecorded, so older records round-trip."""
        payload = handler(self)
        if isinstance(payload, dict) and self.predictor_id is None:
            payload.pop("predictor_id", None)
        return payload

    @model_validator(mode="after")
    def _revocation_follows_a_close(self) -> CountingWindow:
        """A revoked window is a closed one, revoked at or after it opened.

        Revoking a window still open would leave its digest blessed, so the
        backlog would re-mint the re-owed events under the very process the
        revocation found defective; a successor must close it first.
        """
        if self.closes is not None and self.closes <= self.opens:
            raise ValueError("a window closes after it opens")
        if self.revoked_at is not None:
            if self.closes is None:
                raise ValueError("only a closed window can be revoked: set `closes` first")
            if self.revoked_at < self.opens:
                raise ValueError("a window is revoked at or after it opens")
        return self

    def contains(self, moment: datetime) -> bool:
        """Whether ``moment`` falls in ``[opens, closes)``; a naive moment never does."""
        if moment.tzinfo is None:
            return False
        return self.opens <= moment and (self.closes is None or moment < self.closes)


class FrozenProcessRecord(_Strict):
    """The freeze constants in force when a board was built.

    ``process_scope: "frozen"`` names a partition whose membership lives in
    code (:mod:`fedcourtsai.process_version`), so without this block a reader
    would have to resolve the build's commit back to the source to see *which*
    digests were blessed and from which instant. Recording them on the board
    itself, the way ``salience_versions`` names the gate, states what was
    blessed at build time — on every build, an ``all``-scope one included, as
    the partition's definition and never a claim it was applied. ``digests`` is
    the *blessed* set, not the *filter*: the enforced membership rule is
    ``windows`` (``process_version.is_frozen`` and ``counted_on_event``), one
    per blessing of a predictor digest, so a closed window's digest keeps
    counting after it leaves the blessed set; evaluator digests are
    record-only (timing alone enforced).
    """

    digests: list[str] = Field(
        description="The blessed digest set (`FROZEN_PROCESS_DIGESTS`), sorted — "
        "predictors and evaluators together, exactly as the registration "
        "blessed them. Not a filter: the enforced membership rule is `windows`, "
        "which keeps a closed window's digest counting after it leaves this set"
    )
    since: datetime | None = Field(
        description="The current label's counting instant (`FROZEN_SINCE`); null while no "
        "freeze is in force. The counting rule itself is `windows`"
    )
    windows: list[CountingWindow] = Field(
        default_factory=list,
        description="The counting windows (`COUNTING_WINDOWS`), in registry order: a "
        "prediction counts where its digest has a window containing its stamp that no "
        "revocation de-counted, and where it holds cells from several windows on one "
        "event only the earliest window's counts. Every figure over a window is "
        "reported under that window's `label`",
    )
    pending: list[str] = Field(
        default_factory=list,
        description="Each registration the build's registry held as pending — written by "
        "the PR that registers it, not yet stamped by the merge that carries it — as "
        "`<kind> <ident>` (`label proc-vN`, `blessing <digest>`, `window-opens <label> "
        "<digest>`, `window-closes <label> <digest>`, `boundary <name>`). Nothing pending "
        "counts, opens, closes or splits, so a board built while any is pending reads them "
        "here. Omitted while empty",
    )

    @model_serializer(mode="wrap")
    def _omit_empty_windows(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``windows`` and ``pending`` while empty, so such a record reads as before."""
        payload = handler(self)
        if isinstance(payload, dict):
            if not self.windows:
                payload.pop("windows", None)
            if not self.pending:
                payload.pop("pending", None)
        return payload


#: A full 40-hex commit SHA.
_FULL_SHA = r"^[0-9a-f]{40}$"

#: Which cells a harness boundary's change can reach; see
#: :class:`fedcourtsai.process_version.HarnessBoundary`.
RegistryBoundaryReach = Literal[
    "self-represented dockets", "granted dockets", "all", "replay cells"
]


def _registry_utc(moment: datetime | None, what: str) -> None:
    """Refuse a registry datetime that is naive or off UTC."""
    if moment is not None and (moment.tzinfo is None or moment.utcoffset() != timedelta(0)):
        raise ValueError(f"a registry {what} is UTC")


class RegistryInstant(_Strict):
    """One registered instant of the process registry, with where it came from.

    Every counting instant, bless moment and window edge is one of these, so a
    reader can tell an instant set by hand from one a carrying merge stamped,
    and audit either against git. A **pending** instant — ``at`` and ``merge``
    both null — is a registration no promotion has carried yet: the PR that
    registers a label writes it, and the merge that carries that PR to
    ``main`` stamps it with its own SHA and committer time.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True, frozen=True)

    at: datetime | None = Field(
        description="The instant, in UTC (`YYYY-MM-DDTHH:MM:SSZ`); null while pending"
    )
    merge: str | None = Field(
        pattern=_FULL_SHA,
        description="The full SHA of the carrying promotion merge — the promotion merge "
        "that carried the registration and made the blessed bytes immutable on `main` "
        "— and so the "
        "commit the instant is audited against: a bless moment equals its committer time, "
        "a counting instant is at or after it. Not the merge that carried a later "
        "correction of the instant. A label that holds its predecessor's counting "
        "instant (an evaluator-only label) copies that instant whole, so its `merge` names "
        "the predecessor's carrying merge, not its own. Null, with `at`, marks a "
        "registration no merge has carried yet",
    )
    source: Literal["hand", "merge"] = Field(
        description="`merge` where `at` equals `merge`'s committer time, so git re-derives "
        "it; `hand` where a maintainer set `at` at or after that committer time (a "
        "counting instant set by hand under the rule before merge-stamped instants, "
        "verified against the merge). "
        "A pending instant is `merge`: its carrying merge stamps it"
    )

    @model_validator(mode="after")
    def _utc(self) -> RegistryInstant:
        """An instant is UTC, and pending exactly when it names no merge."""
        _registry_utc(self.at, "instant")
        if (self.at is None) != (self.merge is None):
            raise ValueError("a registry instant sets `at` and `merge` together, or neither")
        if self.at is None and self.source != "merge":
            raise ValueError("a pending registry instant is stamped by its merge (`merge`)")
        return self

    @property
    def pending(self) -> bool:
        """Whether no promotion has carried this registration yet."""
        return self.merge is None


class RegistryLabel(_Strict):
    """A process label and the counting instant from which its cells count.

    The labels before ``proc-v8`` are deliberately absent: their digests were
    de-counted when each was superseded, so they open no window.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True, frozen=True)

    label: str = Field(description="The process label (`proc-vN`)")
    since: RegistryInstant = Field(
        description="The label's counting instant: it opens every window the label newly "
        "blesses and closes every window it stops blessing"
    )


class RegistryBlessing(_Strict):
    """One digest the current process blesses, with its bless moment."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True, frozen=True)

    digest: str = Field(description="The blessed process digest (`sha256:<hex>`)")
    role: Literal["predictor", "evaluator"] = Field(description="The actor's role")
    actor_id: str = Field(description="The predictor or evaluator the digest is the process of")
    label: str = Field(
        description="The label that first blessed the digest; a digest carried forward "
        "byte-identical keeps it"
    )
    blessed: RegistryInstant = Field(
        description="The bless moment: when the digest's bytes became immutable on `main`, "
        "the retroactivity boundary no counted cell may predate"
    )


class RegistryWindow(_Strict):
    """One counting window: a blessing of one predictor digest and its span."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True, frozen=True)

    label: str = Field(description="The label whose blessing opened the window")
    digest: str = Field(description="The blessed predictor process digest (`sha256:<hex>`)")
    predictor_id: str | None = Field(description="The predictor whose process the digest is")
    opens: RegistryInstant = Field(description="The counting instant that opened the window")
    closes: RegistryInstant | None = Field(
        description="The successor's counting instant that closed the window; null while open"
    )
    revoked_at: datetime | None = Field(
        description="When a dated revocation de-counted the window's cells; null for a "
        "window that counts"
    )

    @model_validator(mode="after")
    def _utc(self) -> RegistryWindow:
        """A revocation instant reads the registry's one clock."""
        _registry_utc(self.revoked_at, "revocation")
        return self


class RegistryBoundary(_Strict):
    """A dated change to what a predict cell reads under an unchanged predictor digest."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True, frozen=True)

    name: str = Field(description="The boundary's stable name")
    merge: str | None = Field(
        pattern=_FULL_SHA,
        description="The full SHA of the commit that carried the change to `main`; a cell's "
        "side is read by ancestry against it. Null, with `at`, while no promotion has "
        "carried the registration",
    )
    at: datetime | None = Field(
        description="That commit's committer time; display only. Null while pending"
    )
    predictors: list[str] | None = Field(
        description="The predictors the boundary splits; null for every predictor"
    )
    reach: RegistryBoundaryReach = Field(description="The cells the change can reach")
    gradual: bool = Field(
        description="Whether the change reached the corpus through a back-fill pass, so a "
        "cell after it may still read the earlier document set"
    )

    @model_validator(mode="after")
    def _utc(self) -> RegistryBoundary:
        """A boundary's display time reads the registry's one clock; pending sets neither."""
        _registry_utc(self.at, "boundary time")
        if (self.at is None) != (self.merge is None):
            raise ValueError("a registry boundary sets `merge` and `at` together, or neither")
        return self

    @property
    def pending(self) -> bool:
        """Whether no promotion has carried this boundary yet."""
        return self.merge is None


class ProcessRegistry(_Strict):
    """``process_registry.json`` — the frozen-process registry, as committed data.

    The single source of the counting partition's definition:
    :mod:`fedcourtsai.process_version` builds its freeze constants from it at
    import (``FROZEN_PROCESS_DIGESTS`` from ``blessings``, ``FROZEN_SINCE``
    from the current label's ``since``, ``COUNTING_WINDOWS`` from
    ``windows``, ``EVALUATE_BLESSING_LABELS`` and ``HARNESS_BOUNDARIES``), so
    every reader keeps reading those names. Append-only in the same sense as
    the freeze record: a successor closes and adds windows, and appends
    labels, blessing labels and boundaries, but never rewrites a landed
    instant. A pending instant is the one field written twice: null in the PR
    that registers it, then stamped once by the merge that carries it.
    """

    model_config = ConfigDict(extra="forbid", use_enum_values=True, frozen=True)

    schema_version: Literal[1] = Field(description="The registry format's version")
    merge_stamping_declared: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="The date of the freeze-record entry that declares counting instants "
        "and bless moments stamped by the carrying merge's committer time. Until it is set, "
        "`register-process` writes no pending label: a merge may stamp a label's instants "
        "only under a rule the freeze record already holds on `main`",
    )
    labels: list[RegistryLabel] = Field(description="Every label with a counting window, in order")
    blessings: list[RegistryBlessing] = Field(
        description="The digests the current process blesses, one per actor, in order"
    )
    windows: list[RegistryWindow] = Field(
        description="Every counting window, in the order the registry opened them"
    )
    evaluate_blessing_labels: dict[str, list[str]] = Field(
        description="Every evaluate label that blessed each evaluator digest, in blessing "
        "order, kept after those labels are superseded"
    )
    harness_boundaries: list[RegistryBoundary] = Field(
        description="Every harness boundary dated since the earliest window opened, in the "
        "order their carrying commits reached `main`"
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


class VoidedEvent(_Strict):
    """One voided event: its key, the ground it was voided on, and how it was found.

    A void de-counts every grading of one event whose committed outcome records a
    different petition than the one the event was opened on. The ground is a
    closed vocabulary, so nothing but that defect can be entered here, and the
    entry naming it is a dated ``docs/freeze-record.md`` entry that publishes the
    voided gradings' scores (``docs/process-version.md``, *Voiding an event*).
    """

    case_id: str = Field(pattern=CASE_ID_PATTERN, description="The voided event's case id")
    event_id: str = Field(pattern=EVENT_ID_PATTERN, description="The voided event's id")
    ground: Literal["redocketed"] = Field(
        description="Why the event is voided. `redocketed`: its outcome records a "
        "different petition than the one it was opened on, shown from stored docket "
        "payloads alone (docketed date, parties, lower-court number)"
    )
    detection: Literal["outcome-triggered", "scan"] = Field(
        description="How the defect was found: `outcome-triggered` (a grading or "
        "flag on the resolved event surfaced it) or `scan` (a systematic sweep of "
        "stored docket identities, outcome-blind by construction)"
    )
    declared: date = Field(description="The date of the freeze-record entry that voids it")
    defect: str = Field(description="The defect, as the entry states it")


class VoidedEventsRegistry(_Strict):
    """``src/fedcourtsai/voided_events.json`` — every voided event, append-only.

    Data rather than code, so a void is a reviewed, maintainer-merged edit to one
    file, and a row is never removed: removing one would re-count gradings a dated
    entry withdrew.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    events: list[VoidedEvent] = Field(description="The voided events, in the order declared")


class VoidedEventsRecord(_Strict):
    """The voided events a board's build dropped, and what their gradings scored.

    An event whose committed outcome describes another petition is voided by a
    dated freeze-record entry (``voids.VOIDED_EVENTS``). Its gradings leave
    every stratum, rank key and composition count, so this block states how many
    the shared stratify pass dropped, which events, and what those gradings had
    scored, and the de-count is never silent. Omitted where nothing in scope is
    voided. It changes which cells are counted, never what any cell scored.
    """

    excluded: int = Field(
        ge=0,
        description="How many in-scope gradings of voided events the shared "
        "`store.stratify` pass dropped — the pass every scored surface reads, so the "
        "count is the pass's, not this surface's own — counted after the run "
        "collapse and before any stratum; never subtracted from a total beside it",
    )
    events: list[str] = Field(
        default_factory=list,
        description="The voided events among those gradings, as '<case_id> <event_id>', sorted",
    )
    by_predictor: dict[str, int] = Field(
        default_factory=dict,
        description="Dropped gradings keyed by predictor id (only predictors "
        "with a nonzero count appear)",
    )
    correct_by_predictor: dict[str, int] = Field(
        default_factory=dict,
        description="How many of each predictor's dropped gradings recorded "
        "`correct: 1`, so a void is seen to remove hits and misses alike",
    )
    mean_brier_by_predictor: dict[str, float] = Field(
        default_factory=dict,
        description="The mean Brier score of each predictor's dropped gradings "
        "(predictors whose dropped gradings carry no Brier score are absent)",
    )


#: Why a scored cell is set aside from a board's default figures
#: (:mod:`fedcourtsai.set_aside`). A closed vocabulary, so each reason is one
#: reviewed edit with its own dated freeze-record entry. `increment-run-day` is the
#: one claim-grain reason: it sets aside a claim inside a cell, never the cell.
SetAsideReason = Literal[
    "interim-decision-day",
    "post-conference-first-forecast",
    "increment-run-day",
    "pre-distribution-mint",
]


class SetAsideEvent(_Strict):
    """One event whose cells are set aside from the default figures, and the census row behind it.

    The reasons a committed artifact alone cannot decide sit here — the
    post-conference reason reads the petition's docket entries, which live in
    the corpus — so the set-aside is a committed fact every offline board reads
    the same way. A reason the committed ledger decides by itself is computed
    instead and never listed.
    """

    case_id: str = Field(pattern=CASE_ID_PATTERN, description="The event's case id")
    event_id: str = Field(pattern=EVENT_ID_PATTERN, description="The event's id")
    reason: Literal["post-conference-first-forecast"] = Field(
        description="Why its cells are set aside. `post-conference-first-forecast`: the "
        "event's first forward frozen-scope cell (by harness run id) ran on or after the "
        "day the conference that actually considered the petition sat "
        "(`cert_signals.considering_conference` reads `sat`)"
    )
    conference: date = Field(description="The conference that considered the petition")
    first_forward_run_id: str = Field(
        description="The harness run id of the event's first forward frozen-scope cell"
    )
    declared: date = Field(description="The date of the freeze-record entry that sets it aside")


class PreDistributionSetAsideEvent(_Strict):
    """One cert distribution event set aside because its cells were minted before the petition was.

    The distribution moment's cells forecast from the petition's own
    distribution for a conference; a cell minted while only an ancillary paper
    (a sealing motion, a motion for leave under a linked M-number) had been
    distributed forecast from a moment the petition never reached, so the
    record cannot show what moment it stands at. Whether the petition was
    distributed in its own right reads the docket entries, which live in the
    corpus, so the event is listed rather than computed.
    """

    case_id: str = Field(pattern=CASE_ID_PATTERN, description="The event's case id")
    event_id: str = Field(pattern=EVENT_ID_PATTERN, description="The event's id")
    reason: Literal["pre-distribution-mint"] = Field(
        description="Why its cells are set aside. `pre-distribution-mint`: the event's "
        "forward frozen-scope distribution-moment cells were minted when the docket carried "
        "a distribution by their run day but none of the petition itself "
        "(`store.petition_distributed` reads false)"
    )
    minted_run_id: str = Field(
        description="The harness run id of the event's forward frozen-scope cells minted "
        "before the petition was distributed"
    )
    declared: date = Field(description="The date of the freeze-record entry that sets it aside")


#: One row of the listed set-aside registry, its shape chosen by its reason.
ListedSetAsideEvent = Annotated[
    SetAsideEvent | PreDistributionSetAsideEvent, Field(discriminator="reason")
]


class SetAsideEventsRegistry(_Strict):
    """``src/fedcourtsai/set_aside_events.json`` — the listed set-aside events, append-only.

    Data rather than code, so a listed set-aside is a reviewed edit to one file,
    and a row is never removed: removing one would move a default figure across
    a dated entry's boundary.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    events: list[ListedSetAsideEvent] = Field(
        description="The listed events, in the order declared"
    )


#: A release slug: lower-case words joined by single hyphens, so it is a URL path
#: segment as written.
RELEASE_SLUG_PATTERN: Final = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
#: A DOI as the release documents cite it (``10.<registrant>/<suffix>``), never a URL.
DOI_PATTERN: Final = r"^10\.[0-9]{4,9}/[^\s]+$"
#: A repository path to a release document: relative, Markdown, under ``docs/``.
RELEASE_DOC_PATTERN: Final = r"^docs/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_-][A-Za-z0-9_.-]*\.md$"


class ReleaseEntry(_Strict):
    """One results release in the release manifest (``docs/releases.json``).

    The fedcourts.ai site reads the manifest from ``main`` and each release's
    documents from the release's own tag, so the list can grow while every
    published page stays fixed to its tagged text. An entry whose tag does not
    exist yet is shown there as upcoming.
    """

    slug: str = Field(
        pattern=RELEASE_SLUG_PATTERN,
        description="The release's URL path segment on the site (`/results/<slug>`)",
    )
    label: str = Field(min_length=1, description='The release\'s short name, e.g. "Release 1"')
    tag: str = Field(
        pattern=r"^results/[A-Za-z0-9._-]+$",
        description="The git tag the release is published from, in the `results/` namespace",
    )
    published: date = Field(description="The release's publication date")
    covers: str = Field(
        min_length=1, description="One line, for a lay reader, on what the release covers"
    )
    summary: str = Field(
        pattern=RELEASE_DOC_PATTERN,
        description="Repository path of the release's public summary, read at `tag`",
    )
    audit: str = Field(
        pattern=RELEASE_DOC_PATTERN,
        description="Repository path of the release's audit write-up, read at `tag`",
    )
    data_doi: str | None = Field(
        default=None,
        pattern=DOI_PATTERN,
        description="The DOI of the release's Zenodo dataset record; null until reserved",
    )
    code_doi: str | None = Field(
        default=None,
        pattern=DOI_PATTERN,
        description="The concept DOI of the project's Zenodo software record, which "
        "resolves to its newest archived version; the release cites it beside its tag, "
        "which pins the exact code. Null until the record exists",
    )


class ReleaseManifest(_Strict):
    """``docs/releases.json`` — every results release, newest first.

    Committed beside the releases it describes and promoted with them, so
    publishing a release needs no change to the site that lists it.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    releases: list[ReleaseEntry] = Field(description="The releases, newest first")

    @model_validator(mode="after")
    def _releases_cohere(self) -> ReleaseManifest:
        """One page per slug, one entry per tag and label, tags named for slugs, newest first.

        The site builds ``/results/<slug>`` and reads that page's documents at
        ``tag``, so a tag that is not ``results/<slug>`` would put one release's
        text under another's address.
        """
        for entry in self.releases:
            if entry.tag != f"results/{entry.slug}":
                raise ValueError(
                    f"release {entry.slug}: tag {entry.tag} is not results/{entry.slug}"
                )
        for field in ("slug", "tag", "label"):
            values = [getattr(entry, field) for entry in self.releases]
            repeated = sorted({v for v in values if values.count(v) > 1})
            if repeated:
                raise ValueError(f"release {field} listed more than once: {', '.join(repeated)}")
        dates = [entry.published for entry in self.releases]
        if dates != sorted(dates, reverse=True):
            raise ValueError("releases must be listed newest first by `published`")
        return self


class SetAsideRecord(_Strict):
    """The cells a board's build set aside from its default figures, and why.

    A set-aside cell is one the record cannot show to be forward
    (:mod:`fedcourtsai.set_aside`): it leaves the default figures — every
    stratum, rank key and composition count — and is put back in the
    sensitivity figures beside them, so the default and the reading with the
    cell counted are both published and the set-aside is never silent. It
    changes which cells the default figure counts, never what any cell scored.
    Omitted where nothing in scope is set aside.
    """

    excluded: int = Field(
        ge=0,
        description="How many in-scope gradings the shared `store.stratify` pass set "
        "aside — counted after the run collapse, the void, the forward-claim rule and "
        "the leakage bit, so a grading those rules already dropped is never counted "
        "here. On the leaderboard it is stage-blind, so never subtracted from a "
        "stage-scoped total beside it; on the claim-score board it covers cert's "
        "first moment only, the board's own population",
    )
    by_reason: dict[str, int] = Field(
        default_factory=dict,
        description="Set-aside gradings keyed by reason (`SetAsideReason`; only "
        "reasons with a nonzero count appear)",
    )
    by_predictor: dict[str, int] = Field(
        default_factory=dict,
        description="Set-aside gradings keyed by predictor id (only predictors with a "
        "nonzero count appear)",
    )
    events: list[str] = Field(
        default_factory=list,
        description="The events holding set-aside gradings, as "
        "'<case_id> <event_id> <reason>', sorted",
    )


class LeaderboardSetAsideLine(_Strict):
    """One board figure recomputed with its set-aside gradings counted.

    The sensitivity reading beside a default figure: the same pooled entry's
    stratum, built by the same code over the default cells plus the cells the
    set-aside removed from it. Only the (population, predictor, stratum)
    figures a set-aside actually moved get a line. A disclosure, never a
    result: the default figure stays the headline, and a line is never ranked.
    """

    population: str = Field(
        description="The board population: `cert@distribution` for the ranked board's "
        "entries, otherwise the `stages` key the figure sits under"
    )
    predictor_id: str
    stratum: Stratum = Field(description="The stratum the set-aside gradings sit in")
    set_aside: int = Field(ge=1, description="Set-aside gradings this line counts back in")
    including: LeaderboardStratum = Field(
        description="The pooled entry's stratum with the set-aside gradings counted"
    )


class LeaderboardSetAsideSensitivity(_Strict):
    """Every leaderboard figure a set-aside moved, recomputed with the set-aside cells counted."""

    lines: list[LeaderboardSetAsideLine] = Field(
        default_factory=list,
        description="One line per moved (population, predictor, stratum) figure, sorted",
    )
    paired: PairedEvents | None = Field(
        default=None,
        description="The ranked board's paired figure — what its ranks are read off — "
        "with the set-aside gradings counted; null unless a ranked-board grading was "
        "set aside",
    )


class Leaderboard(_Strict):
    """``metrics/leaderboard.json`` — predictors ranked from the evaluations ledger.

    A deterministic, offline roll-up of the ``evaluation.json`` files under
    ``data/`` — the newest per (case, event, predictor, evaluator), since a
    re-graded cell commits a second file describing one observation:
    one entry per predictor, pooled over every counted cell in every
    non-revoked window, with the per-window entries beside it as the
    ``by_protocol`` cut. Ranked best-first on the **forward** stratum over the
    **paired** events every ranked engine holds (see :class:`PairedEvents` and
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
        "default headline — only cells whose prediction is its predictor's counted "
        "forecast inside a counting window, graded at or after that window opened) "
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
    voided_events: VoidedEventsRecord | None = Field(
        default=None,
        description="The voided events this build dropped (`voids.VOIDED_EVENTS`) "
        "and how many gradings they held; omitted where no in-scope grading sits "
        "on a voided event",
    )
    set_aside: SetAsideRecord | None = Field(
        default=None,
        description="The gradings this build set aside from its default figures "
        "(`set_aside.set_aside_reason`) and why; omitted where nothing in scope is set "
        "aside. Every figure above and below is the default, without them",
    )
    set_aside_sensitivity: LeaderboardSetAsideSensitivity | None = Field(
        default=None,
        description="Each figure the set-aside moved, recomputed with the set-aside "
        "gradings counted — the sensitivity reading beside the default; omitted where "
        "nothing in scope is set aside",
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
        description="Number of entries on the cert board that carry a rank — the engines of "
        "`paired` while its events are non-empty, else 0. Every predictor with a cert-stage "
        "evaluation has an entry, ranked or not",
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
        description="The cert-stage board — one entry per predictor with a cert-stage "
        "evaluation, pooled over every counted cell in every non-revoked window, its "
        "composition in `windows`. Ranked entries first in rank order, then the unranked by "
        "predictor_id. A pooled entry is the predictor's forward track record; two pooled "
        "entries cover different events and are never compared side by side — `paired` is",
    )
    by_protocol: list[LeaderboardEntry] = Field(
        default_factory=list,
        description=_BY_PROTOCOL_DESCRIPTION,
    )
    paired: PairedEvents | None = Field(
        default=None,
        description="The paired-event figure the ranks are read off: the events every "
        "ranked engine holds a qualifying forward cell on, from any window. Null while no "
        "engine holds a qualifying cell",
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
        """Drop each optional axis block (``stages``, ``salience_versions``, the cut) while empty.

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
            if not self.by_protocol:
                payload.pop("by_protocol", None)
            if self.paired is None:
                payload.pop("paired", None)
            if self.voided_events is None:
                payload.pop("voided_events", None)
            if self.set_aside is None:
                payload.pop("set_aside", None)
            if self.set_aside_sensitivity is None:
                payload.pop("set_aside_sensitivity", None)
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
    windows: list[WindowCount] = Field(
        default_factory=list,
        description="The (predictor, window) series behind this stratum's pairs, each with "
        "its count of the cells that formed a pair: the validation pools predictors by "
        "design. " + _POOLED_WINDOWS_DESCRIPTION,
    )
    rubrics: list[RubricCount] = Field(
        default_factory=list,
        description="The (evaluator, evaluate digest) pairs whose `reasoning_quality` "
        "grades formed this stratum's pairs, each with its `n` in pairs. " + _RUBRIC_COVERAGE,
    )

    @model_serializer(mode="wrap")
    def _omit_single_label(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``windows`` and ``rubrics`` while they list nothing."""
        return _omit_empty(handler(self), windows=self.windows, rubrics=self.rubrics)


class ClaimScoreEntry(_Strict):
    """One predictor's claim-score aggregates, per stratum, in id order.

    Entries carry no rank on purpose: a claim total is never a rank key, so
    the artifact orders predictors alphabetically and assigns no standings. A
    board's ``entries`` are the pooled default — one per predictor, over every
    counted cell in every non-revoked window, with ``windows`` stating the
    makeup — and its ``by_protocol`` list carries the per-window cut.
    """

    predictor_id: str
    process_window: str | None = Field(
        default=None,
        description="On a `by_protocol` cut entry, the label of the counting window every "
        "cell behind it comes from (e.g. `proc-v8`). Null on a pooled entry, which spans "
        "the windows `windows` lists, and on every all-versions entry",
    )
    windows: list[WindowShare] = Field(default_factory=list, description=_COMPOSITION_DESCRIPTION)
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

    @model_serializer(mode="wrap")
    def _omit_empty_windows(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``windows`` while it lists nothing (a cut entry, or an all-versions build)."""
        return _omit_empty(handler(self), windows=self.windows)


class ClaimScoreSetAsideLine(_Strict):
    """One claim-score figure recomputed with its set-aside gradings counted.

    The claim surface's sensitivity reading, built exactly as
    :class:`LeaderboardSetAsideLine` is: the same pooled entry's stratum over
    the default cells plus the set-aside ones, for each (predictor, stratum)
    figure the set-aside moved. Never a headline and never a rank key.
    """

    predictor_id: str
    stratum: Stratum = Field(description="The stratum the set-aside gradings sit in")
    set_aside: int = Field(ge=1, description="Set-aside gradings this line counts back in")
    including: ClaimScoreStratum | None = Field(
        description="The pooled entry's stratum with the set-aside gradings counted; null "
        "where none of the counted-back gradings carries a claim block, so the entry's "
        "default figure is unmoved by them"
    )


class ClaimSetAsideRecord(_Strict):
    """The claims a claim-score build set aside inside its default cells, and why.

    The claim grain of :class:`SetAsideRecord`: a claim-grain reason
    (`increment-run-day`) takes one claim's score out of the default figures and
    leaves the cell, and its other claims, counted. Counted in **claim units** —
    a prediction's claim once, however many judges graded the cell — with the
    gradings they sit in beside them, because a cell count would misstate how
    much of a total moved. Omitted where nothing in scope is set aside.
    """

    claims: int = Field(
        ge=0,
        description="Distinct (case, event, predictor, claim) rows set aside, over this "
        "surface's own population (cert's first moment) and its default cells only",
    )
    scored_claims: int = Field(
        ge=0,
        description="Of `claims`, those carrying a score — the ones that move a total; a "
        "claim with no baseline is set aside but moves no figure",
    )
    gradings: int = Field(ge=0, description="In-scope gradings carrying a set-aside claim")
    by_reason: dict[str, int] = Field(
        default_factory=dict, description="Set-aside claims keyed by reason (`SetAsideReason`)"
    )
    by_claim: dict[str, int] = Field(
        default_factory=dict, description="Set-aside claims keyed by claim id"
    )
    by_predictor: dict[str, int] = Field(
        default_factory=dict, description="Set-aside claims keyed by predictor id"
    )
    events: list[str] = Field(
        default_factory=list,
        description="The set-aside claims, as '<case_id> <event_id> <claim_id> <reason>', "
        "sorted and deduplicated",
    )


class ClaimScoreClaimSetAsideLine(_Strict):
    """One claim-score figure recomputed with one claim-grain reason's claims counted back.

    Per reason and never stacked: the default cells with that reason's claims
    scored again, every other set-aside and departure left as the default
    applies it. Never a headline and never a rank key.
    """

    reason: SetAsideReason = Field(description="The claim-grain reason counted back")
    predictor_id: str
    stratum: Stratum = Field(description="The stratum the set-aside claims sit in")
    claims: int = Field(ge=1, description="Set-aside claims this line counts back in")
    scored_claims: int = Field(
        ge=0,
        description="Of `claims`, those carrying a score — the ones that move a figure. "
        "Zero means the line's `including` equals the default figure: the claims are set "
        "aside, and none of them moved anything",
    )
    including: ClaimScoreStratum | None = Field(
        description="The pooled entry's stratum with the reason's claims counted back; null "
        "only where the entry has no figure in that stratum and none of the line's claims "
        "carries a score, so nothing it counts back could give it one"
    )


class ClaimScoreBoard(_Strict):
    """``metrics/claim-scores.json`` — the mechanical claim-score surface.

    A deterministic, offline roll-up of every ``claim_scores`` block in the
    evaluations ledger, advisory beside the leaderboard rather than inside it:
    nothing here alters or reorders the board. Aggregates live per predictor
    per pre-registration stratum, never pooled across strata; the headline is the per-stratum
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
    voided_events: VoidedEventsRecord | None = Field(
        default=None,
        description="The voided events this build dropped, exactly as the "
        "leaderboard records them; omitted where no in-scope grading sits on a "
        "voided event",
    )
    set_aside: SetAsideRecord | None = Field(
        default=None,
        description="The gradings this build set aside from its default figures, "
        "counted over this surface's own population (cert's first moment) — so a "
        "set-aside the leaderboard's stage blocks carry is not counted here; omitted "
        "where nothing in that population is set aside",
    )
    set_aside_sensitivity: list[ClaimScoreSetAsideLine] = Field(
        default_factory=list,
        description="Each cert-stage claim figure the set-aside moved, recomputed with "
        "the set-aside gradings counted, sorted by predictor then stratum; omitted while "
        "it lists nothing",
    )
    claim_set_aside: ClaimSetAsideRecord | None = Field(
        default=None,
        description="The claims this build set aside inside its default cells by a "
        "claim-grain reason, in claim units (`set_aside.claim_set_aside_reason`); omitted "
        "where nothing in scope is set aside",
    )
    claim_set_aside_sensitivity: list[ClaimScoreClaimSetAsideLine] = Field(
        default_factory=list,
        description="Each claim figure a claim-grain set-aside moved, recomputed with that "
        "reason's claims counted back and nothing else, sorted by reason, predictor, then "
        "stratum; omitted while it lists nothing",
    )
    evaluations_total: int = Field(
        ge=0,
        description="Cert-stage evaluation cells in scope (after the "
        "forward-claim exclusion the `forward_claim` block records, the "
        "leakage exclusion the `leakage_exclusion` block records and the "
        "set-aside the `set_aside` block records), with or "
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
        description="The pooled default: one entry per predictor with at least one "
        "block-carrying cell, over every counted cell in every non-revoked window, ordered "
        "by predictor_id — never ranked",
    )
    by_protocol: list[ClaimScoreEntry] = Field(
        default_factory=list,
        description="The by-protocol cut: one entry per (predictor, counting window) with at "
        "least one block-carrying cell, ordered by predictor_id then the window's opening. "
        "Two windows of one predictor share no event, so a move between them is a "
        "comparison over different events, never a measurement of improvement. Empty on "
        "an all-versions build",
    )

    @model_serializer(mode="wrap")
    def _omit_empty_cut(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``by_protocol`` while it lists nothing (an all-versions build), and
        ``voided_events``, the cell-grain set-aside pair (``set_aside`` /
        ``set_aside_sensitivity``) and the claim-grain pair (``claim_set_aside`` /
        ``claim_set_aside_sensitivity``) while nothing in scope is voided or set
        aside."""
        return _omit_empty(
            handler(self),
            by_protocol=self.by_protocol,
            voided_events=self.voided_events,
            set_aside=self.set_aside,
            set_aside_sensitivity=self.set_aside_sensitivity,
            claim_set_aside=self.claim_set_aside,
            claim_set_aside_sensitivity=self.claim_set_aside_sensitivity,
        )


class SemanticClaimSummary(_Strict):
    """The grade census for one semantic claim — counts, and nothing derived from them.

    Descriptive by construction. The three ordinal levels are counted, the
    availability mask is counted apart from them **and split by the ground it
    rests on**, and the one derived figure — ``supported_share`` — is withheld
    below the minimum graded count, because a share over three grades describes
    three grades rather than a predictor. Nothing here is a score, nothing is
    pooled with a mechanical claim total, and nothing is a rank key
    (``metrics/README.md``).

    While every unit masks, ``not_addressed_by_ground`` is the only thing this
    census says that varies — which is why the mask is split rather than left as
    one total: ``no-judgment`` bounds what could ever have been graded,
    ``not-ingested`` names work the pipeline owes, and ``silent-on-axis`` names
    a fact about the opinion. Three different kinds of fact, none substitutable
    for another.
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
    not_addressed_by_ground: dict[str, int] = Field(
        default_factory=dict,
        description="`not_addressed` split by ground — the three "
        "`SemanticGrade.mask_ground` values, plus `unstated` for a unit whose "
        "grades name none. Sums to `not_addressed` exactly, and carries only "
        "the grounds with a non-zero count. Read each count as *units resolved "
        "to that ground*, not as units the panel agreed on: where graders name "
        "different grounds a stated precedence settles the unit, and nothing "
        "here bounds how many were resolved rather than agreed. The split is "
        "the signal, not a detail of it — the case's posture, work the pipeline "
        "owes, and a finding about the Court are three different facts, and one "
        "total lets any of them be read as another",
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

    @model_validator(mode="after")
    def _ground_split_accounts_for_every_mask(self) -> SemanticClaimSummary:
        """The split is a partition of `not_addressed`, not a sample of it.

        Enforced rather than documented because the whole reason to separate the
        grounds is that they are not tradeable: a split that dropped units, or
        that carried a bucket outside the closed vocabulary, would let a reader
        subtract one ground from the total and get a number describing nothing.
        Every producer here is the harness, so this can only fire on a bug.
        """
        allowed = {*get_args(MaskGround), MASK_GROUND_UNSTATED}
        if unknown := sorted(set(self.not_addressed_by_ground) - allowed):
            raise ValueError(f"mask grounds outside the vocabulary: {', '.join(unknown)}")
        counted = sum(self.not_addressed_by_ground.values())
        if self.not_addressed_by_ground and counted != self.not_addressed:
            raise ValueError(
                f"the mask's ground split totals {counted}, "
                f"not `not_addressed` ({self.not_addressed})"
            )
        return self


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
    windows: list[WindowCount] = Field(
        default_factory=list,
        description="The (predictor, window) series whose gradings these counts pool, each "
        "with its count of block-carrying gradings — the composition of the pool, stated by "
        "the caller, a single series included. Empty on an all-versions census",
    )
    rubrics: list[RubricCount] = Field(
        default_factory=list,
        description="The (evaluator, digest) rubrics whose gradings these counts pool, each "
        "with its count of block-carrying gradings, stated by the caller. A census spanning "
        "more than one digest of an evaluator is coverage, not a claimable figure, until the "
        "per-rubric reading is built",
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


#: The SCOTUS docket classes the historical replay scores apart. A cert petition
#: (the Term-prefixed ``YY-NNNN`` form), an interim application (``YYAnnn`` in any
#: spelling), and every other SCOTUS docket (original, miscellaneous, pre-1925,
#: unparseable) carry
#: different outcome vocabularies — `granted` is cert on a petition and the relief
#: asked on an application — so one SCOTUS floor over all three moves with the mix
#: rather than with anything a predictor did.
BacktestDocketClass = Literal["cert", "application", "other"]


class BacktestDocketClassScore(BacktestCourtScore):
    """One predictor's standings over one docket class of one court's slice.

    The same scores as the court row it refines, over the events of that court
    whose docket is of ``docket_class``. Emitted for SCOTUS only, the one court
    whose slice mixes classes with different outcome vocabularies; the classes
    partition the court's events, so their counts sum to its row's.
    """

    events_scored: int = Field(
        ge=0, description="Events replayed for this predictor in this docket class"
    )
    always_denied_accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="This docket class's always-deny floor — the fraction of its scored "
        "events whose disposition is `denied`. The base rate that makes the accuracy readable",
    )

    docket_class: BacktestDocketClass = Field(
        description="`cert` — a modern discretionary-cert petition (the population the "
        "cert stage predicts); `application` — an interim application; `other` — any other "
        "docket of the court (original, miscellaneous, pre-1925 or unparseable numbers)"
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
    docket_classes: list[BacktestDocketClassScore] = Field(
        default_factory=list,
        description="The SCOTUS row split by docket class, in `cert`, `application`, `other` "
        "order, classes with no events omitted. The SCOTUS slice mixes cert petitions with "
        "interim applications, whose `denied` share differs several-fold, so the cert floor "
        "and lift are read on the `cert` row, not the court row. Empty where no SCOTUS "
        "event was scored",
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
    or call outcomes reach its log can be seen being starved, which is why the rate
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
        "condition — a captured result or a logged outcome, and so legible as throttled "
        "or not. The throttle rate's denominator, and NOT `calls`: an engine whose log "
        "carries neither scores 0 here, which is what keeps its throttle count from "
        "reading as a throttle-free engine. 0 also on every log written before the field "
        "existed",
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
    process_window: str | None = Field(
        default=None,
        description="On a `segments_by_protocol` cut segment, the label of the counting "
        "window its cells come from — part of that cut's key, so one engine's cells from two "
        "windows are two cut segments. Null on a pooled segment, which spans the series "
        "`windows` lists, and on every all-versions segment",
    )
    windows: list[WindowCount] = Field(
        default_factory=list,
        description="On a pooled segment, the (predictor, window) series behind its cells, "
        "each with its cell count, a single series included. Empty on a cut segment and on an "
        "all-versions build",
    )
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

    @model_serializer(mode="wrap")
    def _omit_empty_windows(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``windows`` while it lists nothing (a cut segment, or an all-versions build)."""
        return _omit_empty(handler(self), windows=self.windows)


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
    windows: list[WindowCount] = Field(
        default_factory=list,
        description="The (predictor, window) series behind this population's cells, each "
        "with its cell count: the row pools engines by design. " + _POOLED_WINDOWS_DESCRIPTION,
    )

    @model_serializer(mode="wrap")
    def _omit_single_label(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``windows`` while it lists nothing."""
        return _omit_empty(handler(self), windows=self.windows)


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
        "keeps only cells whose prediction is its predictor's counted forecast inside a "
        "counting window and whose gradings were stamped at or after that window opened; "
        "`all` pools every version, "
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
        description="The denominator table, engine then mode then event kind — the pooled "
        "default: each segment pools its engine's counted cells across every non-revoked "
        "window and lists the series it pools",
    )
    segments_by_protocol: list[ToolUsefulnessSegment] = Field(
        default_factory=list,
        description="The by-protocol cut: one segment per engine, counting window, mode, "
        "stage and moment, ordered engine then the window's opening. Two windows share no "
        "event, so a move between them compares different events. Empty on an all-versions "
        "build",
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
    own). Skill against them is given two ways, over the same items.
    ``pooled_brier_skill`` is the ratio of sums, ``1 - sum(Brier) / sum(reference
    Brier)`` — the band's skill as one forecaster, the estimator the forward
    stratum's population skill uses, and the figure to read.
    ``mean_brier_skill`` is the mean of the per-item ratios, kept so the band
    reading stays continuous with reports written before the pooled figure; it
    is the estimator the forward stratum rejects, because a denied petition in
    a low-rate band has a reference Brier near zero, so one such item's ratio
    can run to large negatives and the mean can sit below zero while the
    pooled skill is positive. Both null when no item in the band had a
    prior-Term base rate.
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
        description="Mean of the per-item Brier skills vs each item's segment base "
        "rate (positive beats the base rate, ~0 parrots it, negative is worse), kept "
        "for continuity with reports written before `pooled_brier_skill`. Not "
        "comparable with the forward stratum's population skill, which is a ratio "
        "of sums: a denied item in a low-rate band has a reference Brier near zero, "
        "so its ratio can run to large negatives and dominate the mean. Read "
        "`pooled_brier_skill` for the band's skill. Null when no item had a base rate",
    )
    pooled_brier_skill: float | None = Field(
        default=None,
        le=1.0,
        description="Ratio-of-sums Brier skill over the band: one minus the summed "
        "Brier over the summed reference Brier (each item's base rate as its "
        "forecast), over the items `mean_brier_skill` covers — the band's skill as "
        "one forecaster, not swayed by a single near-zero reference, and the same "
        "estimator as the forward stratum's population skill. Null when no item had "
        "a base rate with a non-zero reference Brier, and on reports written before "
        "the figure existed",
    )


#: The cert back-test's provisioning arms in reading order — the arm that
#: shows the least first — shared by the report's per-entry `arms` and every
#: surface that renders the mix, so the two cannot list them differently.
CERT_BACKTEST_ARMS: tuple[Literal["blind", "truncated", "dated"], ...] = (
    "blind",
    "truncated",
    "dated",
)


class CertBacktestArm(_Strict):
    """One predictor's scores over one provisioning arm of the cert back-test set.

    The arms (`blind`, `truncated`, `dated`) are three information sets, and
    which arm a petition lands in correlates with its outcome — in either
    direction, so a pooled lift can be carried by one arm. This splits an
    entry's disposition score by arm so that is read off the report rather
    than reconstructed. Counts, not only rates: at the pinned draw an arm holds
    one to a handful of petitions, so read `correct` against `denied` over
    `events_scored` (the arm's lift **in petitions** is ``correct - denied``),
    never a percentage without its n.
    """

    arm: Literal["blind", "truncated", "dated"] = Field(
        description="The snapshot provenance the petitions were provisioned under"
    )
    events_scored: int = Field(ge=1, description="Petitions of this arm the entry was scored on")
    correct: int = Field(
        ge=0, description="Of those, the petitions whose disposition the entry called"
    )
    denied: int = Field(
        ge=0,
        description="Of those, the realized denials — what always-deny gets right "
        "on this arm, so the arm's floor is this over `events_scored`",
    )
    granted: int = Field(
        ge=0,
        description="Of those, the realized grant-family outcomes (granted, "
        "granted-in-part, GVR, summary reversal); the remainder after `denied` "
        "and this is dismissed or withdrawn (the replay takes only machine-readable "
        "dispositions)",
    )
    accuracy: float = Field(ge=0.0, le=1.0, description="`correct` over `events_scored`")
    lift_over_always_denied: float = Field(
        ge=-1.0,
        le=1.0,
        description="`accuracy` minus this arm's own always-deny floor "
        "(`denied` over `events_scored`) — the per-petition share of "
        "``correct - denied``",
    )
    granted_correct: int | None = Field(
        default=None,
        ge=0,
        description="Of those, the petitions whose granted-or-not projection the entry "
        "called — the headline axis. Always-deny gets ``events_scored - granted`` right "
        "here, so the arm's headline lift **in petitions** is ``granted_correct - "
        "(events_scored - granted)``. Null on reports written before the granted-axis "
        "headline",
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


class CertBacktestDispatch(_Strict):
    """The ``fedcourts cert-backtest`` parameters one report was produced under.

    Recorded because these options *are* the population definition and the engine
    routing, and neither is recoverable from the scores. ``scope``/``spread``/
    ``limit`` choose which decided petitions were replayed — and the always-deny
    floor a ``lift_over_always_denied`` is measured against moves with them, so
    two reports dispatched differently are two different samples whose top
    lines are not comparable. ``engine``/``skip_engines`` say which backends were
    asked for, which is what makes a board's absences legible as a dispatch
    choice rather than a config gap.
    """

    engine: str = Field(
        default="",
        description="``--engine`` as given: empty means only the offline reference "
        "baselines ran (no cell, no spend); 'auto' routes each enabled predictor "
        "through its own configured engine; a concrete backend name forces every "
        "predictor through that one, which is how the offline 'stub'/'replay' "
        "sweeps run. What was **asked for** — each entry's own `engine` says what "
        "actually ran it",
    )
    skip_engines: list[str] = Field(
        default_factory=list,
        description="``--skip-engines``, sorted: engines opted out of the replay by "
        "the predictor's own configured engine, so a predictor missing from the "
        "board is legible as a deliberate opt-out. Empty where no replay ran — an "
        "opt-out has no meaning without one — and it is not the only reason a "
        "predictor can be absent: `dropped_predictors` carries the run-time ones",
    )
    scope: str = Field(
        default="all",
        description="``--scope``: 'all' every modern-cert petition, 'paid' the paid "
        "segment the salience gate scores (an IFP-based proxy for it, the dominant "
        "but not the only Tier-0 exclusion), 'selected' the gate's **carve-out "
        "core** — CVSG or at/above `salience_floor`, which is the N-independent "
        "core of the live selected slice and not that slice, since the live one "
        "also fills to N by rank. Three different populations with three different "
        "denial base rates",
    )
    spread: bool = Field(
        default=False,
        description="``--spread``: drawn by the salted-hash rule (`provenance.draw`) — "
        "a pseudo-random sample spread over the eligible population's conferences "
        "and Terms in proportion to their size (on an engine replay, the replayable "
        "population's, which reaches back only a few Terms) — instead of the most "
        "recently decided N, "
        "which collapses onto the grant-heavy last order lists. A different grant "
        "mix, so the floor and every lift move with it",
    )
    limit: int = Field(
        default=0,
        ge=0,
        description="``--limit``: the size of the drawn set. On an engine replay "
        "the draw passes over petitions it cannot replay and keeps walking "
        "(`provenance.draw.passed_over`), so the set's size falls short of it only "
        "where the eligible population is smaller than the limit",
    )


#: The rule that drew a cert back-test set from its population. ``recency-head``
#: takes the most recently decided petitions in order; ``vintage-keyed-hash-v1``
#: takes them in the order of a salted SHA-256 of the case id keyed by the
#: corpus vintage — a pseudo-random order no outcome, date or conference feeds.
CertBacktestDrawRule = Literal["recency-head", "vintage-keyed-hash-v1"]


class CertBacktestDraw(_Strict):
    """How a cert back-test set was drawn from its population.

    Recorded because the draw rule decides the set's grant mix, and so the
    always-deny floor every lift is measured against, while the dispatch alone
    does not say which rule ran. ``vintage-keyed-hash-v1`` (``--spread``) ranks
    every petition in the population by
    ``sha256("<salt>|<key>|<case_id>")`` and walks that order, taking each
    eligible petition until ``limit``: a simple random sample without
    replacement, so the set's expected outcome mix is the eligible
    population's (on an engine replay, the replayable population's) and each of
    that population's conferences and Terms holds a share in proportion to its
    size. The key is the corpus vintage, so the same corpus and the same
    dispatch draw the same set while snapshot coverage holds still, and a newer
    corpus draws afresh.
    """

    rule: CertBacktestDrawRule = Field(
        default="recency-head",
        description="'recency-head': the most recently decided petitions in order "
        "(`--no-spread`), which lands a small limit on the last order lists. "
        "'vintage-keyed-hash-v1' (`--spread`): the salted-hash order described "
        "on this block, independent of outcome, decision date and conference",
    )
    salt: str | None = Field(
        default=None,
        description="The fixed salt the hash rule mixes in, recorded so the walk "
        "order can be recomputed from the report; the set also needs the blob and, "
        "on a replay, the snapshot coverage at run time. Null under 'recency-head'",
    )
    key: str | None = Field(
        default=None,
        description="The corpus vintage the hash rule was keyed by: the blob's "
        "newest `last_pulled` stamp (ISO date), or 'undated' where no row carries "
        "one. Two reports with the same key and dispatch over the same blob drew "
        "the same set, provided the content store's snapshot coverage did not move "
        "between them. Null under 'recency-head'",
    )
    passed_over: int = Field(
        default=0,
        ge=0,
        description="Petitions the walk reached and passed over because an engine "
        "replay could not run them (no held snapshot or petition event) before "
        "the set filled. The set is drawn from the replayable population, so this "
        "is coverage, not sampling — and replayable coverage is not "
        "outcome-neutral, so the replayable population's floor, not the whole "
        "population's, is what the drawn set estimates. 0 where no engine replay "
        "ran: the offline baselines need no snapshot",
    )


#: Why a replayed back-test cell produced no score. A named alias rather than an
#: inline ``Literal`` because the replay code classifies a loss before it builds
#: one, and a second spelling of the vocabulary is a second thing to keep in step.
CertBacktestLossReason = Literal[
    "missing",
    "wrote-outside-work-root",
    "invalid",
    "engine-failed",
    "quota-exhausted",
    "harness-error",
]


class CertBacktestCellLoss(_Strict):
    """One back-test cell that produced no score, and why.

    A replay cell is a model call that was paid for; when it fails, or the file
    the runner reads back is missing or does not validate, the petition is
    simply absent from that predictor's scores. Recording it keeps the absence
    legible: the entry's own ``events_scored`` already differs, and this says
    which petitions are behind the difference and what went wrong, rather than
    leaving a board whose predictors were scored over silently unequal sets. A
    cell the campaign declined to attempt is recorded the same way and for the
    same reason — it is absent from the scores either way.

    ``reason`` is a closed vocabulary, not prose — the run log carries the
    detail (a validation error's text, the path that was read, the engine's own
    stderr):

    - ``missing`` — nothing readable at the cell's path under the replay's work
      root: the file is absent, or the filesystem refused it.
    - ``wrote-outside-work-root`` — nothing there either, but the same cell's
      directory **did** appear under the repository ledger: the engine followed
      the prompt template's ``data/cases/...`` path instead of the work root it
      was given.
    - ``invalid`` — a file was there and is not a valid ``Prediction``.
    - ``engine-failed`` — the engine failed for the cell — a non-zero exit, or
      a zero-exit turn whose result reported a fault — and wrote nothing to read
      back: a deterministic fault, or a transient one that outlasted the
      runner's retry budget.
    - ``quota-exhausted`` — the engine's own quota is spent, so the cell failed
      and no retry could have cleared it. Every later cell on that engine in
      the same campaign carries this reason without being attempted, since the
      attempt is a paid-for certainty of the same failure.
    - ``harness-error`` — the harness itself raised something no engine fault
      explains while running or reading this cell, or an earlier cell of the
      same engine's lane. The cause is unknown and may be systemic, so the lane
      stops there: that cell and every later one of its engine carry this
      reason, the later ones without being attempted, while the other engines'
      lanes run on. The run log names the exception.

    ``engine-failed`` and ``quota-exhausted`` are distinct because they say
    different things about the run: one cell hit a fault, against one engine
    being finished for the day.
    """

    predictor_id: str = Field(description="The predictor whose cell was lost")
    case_id: str = Field(description="The petition the lost cell was replaying")
    reason: CertBacktestLossReason = Field(
        description="Why the cell produced no score, from the closed vocabulary above"
    )


class CertBacktestFlag(_Strict):
    """One note a replay cell raised in its ``flags.json``, as the report keeps it.

    The note's category and severity — never its message. A replay cell's note
    about outcome-revealing material names what it saw next to the case it is
    about, and this report is committed under ``metrics/``, which later replay
    cells run beside and are pointed into; so the free text goes to the run log
    (credential-shaped runs redacted) and the report keeps only what a reader
    needs to find and weigh it.
    """

    category: FlagCategory
    severity: FlagSeverity
    outcome_exposure_candidate: bool = Field(
        description="True where the note is filed under `leakage-disclosure`, or where a "
        "deliberately simple text rule "
        "(`fedcourtsai.cert_backtest.outcome_exposure_candidate`) reads the note's "
        "message as possibly disclosing that the cell saw its own petition's outcome. "
        "A triage highlighter, not a judgment: it over-calls on some "
        "shapes (a retrieved prior's GVR, a disclosure note reporting nothing) and "
        "misses others, so an unmarked note "
        "is not a cleared one — and it never changes which cells are scored"
    )


class CertBacktestDisclosure(_Strict):
    """What one replayed cell disclosed in its ``flags.json``, kept past the runner.

    The work root a replay cell writes into is scratch and is discarded with the
    runner, and the back-test runs no evaluator and writes no retrieval log — so
    without this record a cell's note that it saw outcome-revealing material
    would survive only in an expiring run log. One entry per cell that left a
    ``flags.json`` at all, scored or lost; a cell that wrote none disclosed
    nothing, which is silence rather than a clean bill.
    """

    predictor_id: str = Field(description="The predictor whose cell raised the notes")
    case_id: str = Field(description="The petition the cell was replaying")
    scored: bool = Field(
        description="Whether this cell's prediction is in its predictor's figures. "
        "False for a lost cell, whose notes are kept because they can explain the loss — "
        "and can matter to the other predictors' cells on the same petition, which read "
        "the same provisioned inputs — and for every cell of a predictor that left the board"
    )
    unreadable: bool = Field(
        default=False,
        description="The cell wrote a `flags.json` with nothing to recover: it cannot be "
        "read, does not parse as a JSON object or list, or none of its flags survives the "
        "normalisation the cell workflows apply (an off-vocabulary severity or category is "
        "coerced and read, not unreadable). What it disclosed is unknown and `flags` is "
        "empty. The cell stays scored: "
        "a formatting fault is not evidence of exposure, and an unread note may still "
        "have been one",
    )
    flags: list[CertBacktestFlag] = Field(
        default_factory=list, description="The cell's notes, in the order it wrote them"
    )


class CertBacktestDisclosureTally(_Strict):
    """One predictor's disclosure counts over its **scored** replay cells.

    Nothing is excluded on a disclosure: the back-test has no evaluator to grade
    one, and a text rule deciding who stays in the scored set would demote a
    predictor for its candour. So these counts are the reading aid instead — a
    disclosed exposure left in the scores inflates that predictor's accuracy and
    lift, and an undisclosed one is invisible here.
    """

    cells_read: int = Field(
        ge=0,
        description="The denominator: this predictor's cells that came back scoreable "
        "and were read for a `flags.json`",
    )
    cells_flagged: int = Field(
        ge=0, description="Of those, the cells that left a readable `flags.json`"
    )
    flags_unreadable: int = Field(
        ge=0,
        description="Of those, the cells whose `flags.json` had nothing to recover "
        "(`unreadable` on the disclosure)",
    )
    candidates: int = Field(
        ge=0,
        description="Of those, the cells carrying at least one note the text rule marks "
        "`outcome_exposure_candidate` — cells to read the run log for, not a leak count",
    )


class CertBacktestCellClock(_Strict):
    """The replay clock one petition's cells were exported, and the arm it sat in.

    Every predictor's cell on a petition is provisioned from the same case tree
    and handed the same clock, so the record is per petition, not per
    (petition, predictor). It is kept because the clock's width is an
    information-set axis the arm counts do not capture: two dated cells with
    the same Term and different cutoff days could retrieve different priors,
    and a blind cell, having no day, is screened on its Term alone.
    """

    case_id: str = Field(description="The replayed petition")
    snapshot_provenance: Literal["dated", "truncated", "blind"] = Field(
        description="The arm the petition was provisioned under — the key it is "
        "counted under in the report's `provisioning` and `provisioning_denied`"
    )
    decided_before: int = Field(
        description="The Term half of the clock, exported to every cell on the "
        "petition as `DECIDED_BEFORE`: the petition's own docket October-Term year, "
        "which a prior must resolve strictly before to be retrieved"
    )
    replay_cutoff: date | None = Field(
        default=None,
        description="The day half, exported as `REPLAY_CUTOFF`: the day the cells were "
        "provisioned at, which `fedcourts query` applies as a second, removal-only "
        "screen (a prior resolved on or after it is dropped; an undated one stays). "
        "Null on the blind arm, which was given no cutoff, so its cells were "
        "screened on the Term alone",
    )


class CertBacktestProvenance(_Strict):
    """What produced a cert back-test report: the run, its dispatch, and its config.

    The report's self-identification, and the reason it exists: predictor ids are
    identical under every backend — a ``--engine stub`` replay of
    ``claude-baseline`` writes entries named ``claude-baseline`` — so without this
    block an offline mechanics rehearsal and a token-spending real-engine replay
    are the same document, and a reader would render stub numbers under real
    predictor names. It records what ran; refusing or labelling a rehearsal is
    the reader's own job, and each reader has to do it.

    The **authority on what ran** is each entry's own ``engine``/``model`` pair;
    this block records the invocation and the resolved config around them. It is
    deliberately not only the CLI options: ``salience_floor`` and
    ``base_rate_lookback_terms`` move the population and the segment baselines
    under an identical dispatch string, so a decomposition that had only the
    dispatch would be comparing samples it could not tell apart.
    """

    run_id: str | None = Field(
        default=None,
        description="The replay's own run id (a UTC timestamp): the id its "
        "provisioned cells were written under in the scratch tree, which is "
        "discarded with the runner — so this is the replay's as-of stamp and a "
        "non-null 'an engine replay happened' mark, not a handle on surviving "
        "artifacts. Null when no engine replay ran: the offline reference "
        "baselines are pure functions of the corpus and have no run",
    )
    dispatch: CertBacktestDispatch = Field(
        default_factory=CertBacktestDispatch,
        description="The parameters the run was dispatched with — the population "
        "definition and the engine routing behind these scores",
    )
    draw: CertBacktestDraw | None = Field(
        default=None,
        description="How the set was drawn from its population — the rule, and the "
        "salt and corpus-vintage key a hash draw used. Null on the empty report "
        "and on reports written before the draw was recorded, whose draw rule the "
        "artifact cannot say",
    )
    salience_floor: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The frozen salience floor the run resolved (config, not a "
        "constant). It is what `--scope selected` *means*, so two reports both "
        "stamped 'selected' under different floors are two populations; null only "
        "where no selection was run at all (the empty report)",
    )
    base_rate_lookback_terms: int | None = Field(
        default=None,
        ge=0,
        description="The base-rate lookback window the run resolved (config; 0 is "
        "unbounded). It sets every entry's `segment_base_rate` and so every "
        "`mean_brier_skill`, and it rides in no process digest — so without it "
        "here, per-band skill across two reports is not a comparison. Null only "
        "where no segment context was built (the empty report)",
    )
    dropped_predictors: list[str] = Field(
        default_factory=list,
        description="Enabled predictors that produced no entry for a **run-time** "
        "reason, sorted: their engine had no registered runner, its CLI binary "
        "turned out to be missing mid-run, or every one of its cells was lost "
        "(`lost_cells`). The ids carry no cause — the run log names "
        "which. The deliberate opt-out is "
        "`dispatch.skip_engines` instead. Recorded because a board silently short "
        "one engine is a different comparison from the three-engine one it looks "
        "like, and stderr does not survive the runner",
    )
    lost_cells: list[CertBacktestCellLoss] = Field(
        default_factory=list,
        description="Individual (petition, predictor) cells that produced no "
        "score, sorted — the cell failed, was declined once its engine's "
        "quota was spent, or came back unreadable. The per-cell counterpart of "
        "`dropped_predictors`, which loses a predictor whole: a predictor short "
        "**some** of its cells is still on the board, scored over the petitions "
        "that did come back — so its `events_scored` is smaller than the set, "
        "and its top line is not measured over the same sample as a predictor "
        "that lost none. One short every cell has nothing to be scored over: it "
        "has no entry and is in `dropped_predictors`, while its cells stay "
        "here. Read this before comparing two entries. Empty on a run where "
        "every cell came back, and on an offline baseline-only run, which has "
        "no cells",
    )
    disclosures: list[CertBacktestDisclosure] = Field(
        default_factory=list,
        description="Every replayed cell that left a `flags.json`, sorted by predictor "
        "then petition — the cells' own notes, kept as category, severity and the text "
        "rule's exposure-candidate reading, never the message. **Nothing here changes "
        "a score**: the back-test runs no evaluator, so a cell that disclosed seeing its "
        "own outcome is still in its predictor's figures, where it biases accuracy and "
        "lift upward. Empty on an offline run, and on a replay where no cell wrote one — "
        "which is silence, not a clean bill",
    )
    disclosure_tally: dict[str, CertBacktestDisclosureTally] = Field(
        default_factory=dict,
        description="Per-predictor disclosure counts over the scored cells, keyed by "
        "predictor id, for every replayed predictor on the board. Engines differ "
        "in how often and how they write notes, so a count is read within one predictor, "
        "never as a cross-engine leakage comparison",
    )
    clocks: list[CertBacktestCellClock] = Field(
        default_factory=list,
        description="The replay clock every replayed petition's cells ran under, one "
        "entry per petition, sorted by case id: its arm, its Term (`DECIDED_BEFORE`) "
        "and, on the dated and truncated arms, its cutoff day (`REPLAY_CUTOFF`). The "
        "day narrows what a cell could retrieve, so two runs over the same petitions "
        "on different days are different information sets even where `provisioning` "
        "matches. Empty on an offline run, which provisions no cell, and on reports "
        "written before the clock was recorded",
    )


class CertBacktestEntry(_Strict):
    """One predictor's standings over the cert back-test set.

    ``predictor_id`` names the registry entry whose prompt and configuration were
    replayed; it says nothing about what executed it, which is why the entry also
    carries the ``engine``/``model`` pair that did.
    """

    predictor_id: str
    rank: int = Field(
        ge=1,
        description="1-based standing; 1 is best. Ordered by the headline "
        "`granted_lift_over_always_denied`, then Brier, then id — **among entries scored over "
        "the whole set**. An entry short some cells (`provenance.lost_cells`) "
        "sorts below every full one whatever its number, because lift is a "
        "per-petition mean and a lost petition the predictor would have got "
        "wrong both rescales and shifts it upward; the ordering among short "
        "entries is the same key over unequal samples, which is a listing "
        "rather than a comparison",
    )
    events_scored: int = Field(
        ge=0,
        description="Decided cert petitions this entry was **scored over**, "
        "which is the whole set unless cells were lost: a predictor short some "
        "of `provenance.lost_cells` is scored, and its lift measured against the "
        "always-deny floor, over the petitions that came back rather than over "
        "the set. Compare two entries with different values here only through "
        "that block",
    )
    accuracy: float = Field(
        ge=0.0, le=1.0, description="Fraction whose predicted disposition matched the known label"
    )
    granted_accuracy: float = Field(
        ge=0.0,
        le=1.0,
        description="Fraction whose binary granted-or-not projection matched the outcome "
        "(a GVR is granted; a dismissal or withdrawal is not) — the headline accuracy, "
        "the target the Brier score scores",
    )
    mean_brier_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Mean Brier score of P(granted) vs the realized outcome (lower is better)",
    )
    granted_lift_over_always_denied: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="The headline: `granted_accuracy` minus always-deny's over the "
        "petitions **this entry was scored on**, which is their not-granted share — the "
        "honest signal under cert's structural denial skew, where raw accuracy is cheap, "
        "and what the board ranks by. That floor is the report's "
        "`always_not_granted_accuracy` whenever `events_scored` is the whole set, and the "
        "scored subset's own not-granted share where cells were lost. Null on reports "
        "written before the granted-axis headline, which ranked by "
        "`lift_over_always_denied`",
    )
    lift_over_always_denied: float = Field(
        ge=-1.0,
        le=1.0,
        description="Exact-disposition accuracy minus the always-deny floor's over the "
        "petitions **this entry was scored on** — a secondary reading beside the "
        "headline, which counts a dismissal or withdrawal as a miss for every "
        "forecaster, always-deny included. That floor is the "
        "report's `always_denied_accuracy` whenever `events_scored` is the whole "
        "set, and the scored subset's own denial rate where cells were lost",
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
    arms: list[CertBacktestArm] = Field(
        default_factory=list,
        description="The entry's disposition score split by provisioning arm "
        "(blind, truncated, dated, in that order; an arm the entry scored nothing on omitted), "
        "each against that arm's own always-deny floor. The arms' `correct` sum "
        "to this entry's correct count and their `events_scored` to its own, so "
        "a pooled lift reads as the sum of the arms' lifts in petitions. Empty "
        "where no clock recorded the arms (a run with no replay), and on reports "
        "written before the split existed",
    )
    big_case: CertBacktestBigCase | None = Field(
        default=None,
        description="The predictor's pre-registered big-case-score distribution over "
        "the set (stakes, not grade — the replay has no evaluator to grade against); "
        "null when the predictor produced no big_case_score (the offline baselines). "
        "Not a backend tell: the offline stub writes a big_case_score like a real "
        "cell does, so a populated block says the dimension was exercised, never "
        "that a model exercised it — `engine`/`model` are what answer that",
    )
    engine: str | None = Field(
        default=None,
        description="The runner backend that actually produced this entry's "
        "predictions — the backend that ran, not the predictor's configured engine, "
        "so a `--engine stub` sweep of `codex-baseline` reads 'stub' here. Null for "
        "the offline reference baselines, which run no engine at all",
    )
    model: str | None = Field(
        default=None,
        description="The model that backend was invoked with, taken from the "
        "runner's own resolved model (the shared pricing default table the usage "
        "ledger prices against, so this cannot drift from what a cell was billed "
        "at). Null whenever no model ran **in this run**: the offline baselines, "
        "and the offline 'stub'/'replay' backends. Read it with `engine` — 'stub' "
        "means canned numbers, while 'replay' re-emits one captured real forecast "
        "verbatim across every petition, which is an inference that happened in "
        "some other run and is a constant predictor here",
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
    pooled comparison regardless. Produced by the ``run-backtest`` workflow via
    ``fedcourts cert-backtest``, which spends tokens when agentic engines are
    replayed — so its fortnightly schedule only ever *asks*: the run derives its
    plan under pinned parameters and waits on a manual release, and no report is
    written unless a maintainer released it. A gap between reports says only that
    no report landed, and the artifact does not distinguish the reasons (a
    fortnight nobody released, a cron GitHub never delivered, a run that found no
    replayable petition, a review PR nobody merged); ``provenance.run_id``
    identifies the sample that is standing, not why there is no newer one.
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
        description="The always-deny floor's exact-disposition accuracy over this set: "
        "the denial base rate the secondary `lift_over_always_denied` is measured "
        "against, and exactly the one every entry that scored the whole set is measured "
        "against. An entry short some cells (`provenance.lost_cells`) is floored over its "
        "own scored subset instead, which this figure does not give",
    )
    always_not_granted_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The headline floor: always-deny's `granted_accuracy` over this set, "
        "its not-granted share (denied, dismissed and withdrawn) — what every entry's "
        "`granted_lift_over_always_denied` is measured against where it scored the whole "
        "set. Null on an empty set and on reports written before the granted-axis headline",
    )
    provisioning: dict[str, int] = Field(
        default_factory=dict,
        description="How many replayed petitions were provisioned under each "
        "snapshot_provenance — 'dated' (a snapshot the docket really served before "
        "the cutoff), 'truncated' (a later payload with its post-cutoff entries "
        "removed), 'blind' (no trajectory shown at all, from either cause: no "
        "forward moment fixed a cutoff, or truncation left a disposition visible "
        "and the fail-closed leakage guard withdrew the trajectory). These are "
        "three different information sets, and a figure over their union is a "
        "figure over a mixture: a blind petition cannot observe its own relist "
        "history at all, which is most of what a cert forecast turns on. The "
        "mixture is not neutral either — the blind arm is selected on "
        "outcome-correlated features (a docket with no distribution to show, or "
        "one whose kept entries already showed a disposition), so it can come out "
        "denial-pure or grant-pure and can depress or carry a pooled lift. Read "
        "it as a count, beside each entry's `arms`, before reading the scores. "
        "Empty on reports written before the split existed",
    )
    provisioning_denied: dict[str, int] = Field(
        default_factory=dict,
        description="Of the petitions counted under each key of `provisioning`, how "
        "many were realized denials — keyed the same, a zero stated rather than "
        "omitted. Each arm's own always-deny floor is its count here over its count "
        "there, which undoes the mixture in the floor: the pooled "
        "`always_denied_accuracy` is those floors weighted by the arm sizes. The "
        "scores are split the same way in each entry's `arms`. Beside "
        "`provenance.clocks`, which names each "
        "petition's arm, it states a named petition's outcome wherever its arm is "
        "pure, which includes every arm of one. Over the whole replayed "
        "set, like the pooled floor, so an entry short some cells "
        "(`provenance.lost_cells`) is not floored by these either. A floor over an "
        "arm of one to three petitions is a count, not a rate: read it as denials "
        "over n, never as a percentage without its n. Empty where no "
        "replay provisioned a petition, and on reports written before the per-arm "
        "count existed",
    )
    provenance: CertBacktestProvenance | None = Field(
        default=None,
        description="What produced this report: the replay's run id, the dispatch "
        "parameters, and the resolved config behind them. Read it before reading "
        "any score — the entries are named for predictors, not for the backends "
        "that ran them, so this block plus each entry's `engine`/`model` is the "
        "only thing separating a token-spending real-engine replay from an "
        "offline stub rehearsal of the same machinery. Null means **unknown**, "
        "never 'offline': a report written before provenance was recorded says "
        "nothing about what produced it, and a reader should refuse it rather "
        "than read a default into it. Every report the pipeline writes carries "
        "the block",
    )
    entries: list[CertBacktestEntry] = Field(default_factory=list)


class MeritsBacktestTermCount(_Strict):
    """One October Term's share of the merits back-test population."""

    term: int = Field(description="The October Term the cases were argued in")
    cases: int = Field(ge=0, description="Lead dockets kept for replay")
    argued_unjudged: int = Field(
        ge=0,
        description="Argued plenary dockets with no parsed merits judgment: a parse "
        "gap the population cannot keep, counted so it is not silent",
    )
    excluded: dict[str, int] = Field(
        default_factory=dict,
        description="Decided argued dockets set aside, by reason (`fedcourts "
        "merits-backtest-plan` names each)",
    )
    excluded_disturbed: int = Field(
        default=0,
        ge=0,
        description="Of the set-aside dockets, those whose judgment disturbed the "
        "decision below: how far the kept cases, and the baseline pool drawn from "
        "them, are a selected population",
    )


class MeritsBacktestBaseline(_Strict):
    """The as-of base rate each replay cell's skill is measured against."""

    rule: Literal["as-of-cutoff-v1"] = Field(
        default="as-of-cutoff-v1",
        description="The disturbed share of the population's lead dockets argued "
        "in the cell's own Term or the `lookback_terms` before it and decided "
        "strictly before the cell's cutoff. Keyed on the cutoff rather than on "
        "the grant Term, so no judgment the cell could not have known reaches "
        "its baseline. It is not the forward channel's `merits_base_rate`, so a "
        "skill figure here is never comparable with a forward one",
    )
    lookback_terms: int = Field(ge=0, description="Argued Terms pooled before the cell's own")
    min_decided: int = Field(
        ge=1, description="Below this many pooled judgments a cell carries no baseline"
    )


class MeritsBacktestMomentScore(_Strict):
    """One predictor's scores over one merits moment's replay cells."""

    moment: Moment
    events_scored: int = Field(ge=0, description="Cells that returned a valid prediction")
    lost: int = Field(
        ge=0, description="Cells provisioned at this moment that returned no scorable prediction"
    )
    terms: dict[str, int] = Field(
        default_factory=dict, description="Cells scored per argued Term, a zero stated"
    )
    accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Share of scored cells whose call, disturbed where P(disturbed) "
        "is at least 0.5, matched the judgment. Null when nothing was scored",
    )
    disturbed_share: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The disturbed share of the same scored cells",
    )
    majority_accuracy: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The floor `accuracy` is read against: the larger of "
        "`disturbed_share` and its complement, what always calling the majority "
        "outcome scores on these cells",
    )
    mean_brier_score: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Mean Brier of P(disturbed)"
    )
    baselined: int = Field(
        ge=0, description="Scored cells that carry an as-of baseline (`baseline`)"
    )
    cells_flagged: int = Field(
        default=0,
        ge=0,
        description="Scored cells that left a `flags.json`. Nothing is excluded on a "
        "note: a disclosed exposure left in the scores inflates them",
    )
    exposure_candidates: int = Field(
        default=0,
        ge=0,
        description="Of the flagged cells, those carrying a note the cert back-test's "
        "text rule marks as a possible outcome exposure",
    )
    baselined_brier_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The predictor's mean Brier over the baselined cells only: the "
        "figure `brier_skill` compares, which differs from `mean_brier_score` "
        "wherever some scored cells carry no baseline",
    )
    baseline_brier_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Mean Brier of the as-of base rate over the baselined cells",
    )
    brier_skill: float | None = Field(
        default=None,
        description="1 - (the predictor's summed Brier / the baseline's), both over "
        "the baselined cells: a ratio of sums, so a cell whose baseline happened to "
        "be exact does not drop out. Null with no baselined cell",
    )


class MeritsBacktestCellLoss(_Strict):
    """A provisioned replay cell that produced no score, and why."""

    predictor_id: str
    case_id: str
    moment: Moment
    reason: CertBacktestLossReason


class MeritsBacktestPaired(_Strict):
    """What the briefed moment adds over the grant moment, on the same cases."""

    cases: int = Field(
        ge=0,
        description="Cases this predictor scored at both moments; the only set the "
        "moments are compared on, since the fences drop cells per moment. It fixes "
        "the case mix between the moments, not the selection: a fence can track the "
        "outcome, so this set is selected too",
    )
    disturbed: int = Field(
        default=0, ge=0, description="Of `cases`, those whose judgment disturbed the decision below"
    )
    grant_mean_brier: float | None = Field(default=None, ge=0.0, le=1.0)
    briefed_mean_brier: float | None = Field(default=None, ge=0.0, le=1.0)
    brier_change: float | None = Field(
        default=None,
        description="Briefed minus grant mean Brier over `cases`; negative means the briefs helped",
    )


class MeritsBacktestEntry(_Strict):
    """One predictor's merits back-test record."""

    predictor_id: str
    engine: str | None = Field(
        default=None, description="The backend that ran the cells, `stub` offline"
    )
    model: str | None = Field(
        default=None, description="The model the backend invoked; null for offline backends"
    )
    moments: list[MeritsBacktestMomentScore] = Field(default_factory=list)
    paired: MeritsBacktestPaired


class MeritsBacktestDispatch(_Strict):
    """The parameters a merits back-test was run under, as dispatched."""

    engine: str = Field(
        description="'auto' (each predictor's own engine), a single backend, or empty "
        "when no engine ran"
    )
    skip_engines: list[str] = Field(default_factory=list)
    terms: list[int] = Field(description="The argued Terms the population was drawn from")
    limit: int = Field(
        ge=0,
        description="Cases drawn from the population, 0 for all of them. A draw "
        "walks the cases in `draw_key`'s hash order, so a reader can recompute it",
    )
    draw_key: str = Field(
        description="The corpus vintage the draw order is keyed by (its newest pull "
        "stamp), so the same blob draws the same cases"
    )


class MeritsBacktest(_Strict):
    """``metrics/merits-backtest.json`` — predictors replayed over decided argued cases.

    Each kept case is replayed at the merits stage's grant and briefed moments
    from the record as it stood at each cutoff, outcome redacted, and scored on
    P(disturbed) against the realized judgment. Produced by
    ``fedcourts merits-backtest``.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    stratum: Literal["retrospective"] = Field(
        default="retrospective",
        description="Every replayed judgment was public before the run, and most "
        "predate the models' training cutoffs, so a cell can recall the outcome it "
        "is asked to forecast. This measures recall, calibration and reading of a "
        "known docket, never ex-ante forecasting skill, and no figure here is "
        "claimable as one (the leaderboard's pre-registration rule)",
    )
    unit: Literal["lead-docket"] = Field(
        default="lead-docket",
        description="One case per docket the filings are on: a consolidated member "
        "is set aside and its lead stands for both, in the scores and in the baseline "
        "pool alike",
    )
    pulled_through: date | None = Field(
        default=None,
        description="The corpus vintage the population and cells were read from: "
        "its newest pull stamp",
    )
    run_id: str | None = Field(
        default=None, description="The replay's run id; null when no engine ran"
    )
    dispatch: MeritsBacktestDispatch | None = Field(
        default=None, description="The parameters the run was dispatched with"
    )
    terms: list[MeritsBacktestTermCount] = Field(default_factory=list)
    cells: dict[str, int] = Field(
        default_factory=dict, description="Replay cells written per moment"
    )
    fenced: dict[str, dict[str, int]] = Field(
        default_factory=dict,
        description="Cells the provisioner refused per moment, by reason: no "
        "snapshot, a kept entry still showing the judgment, the respondent's merits "
        "brief not staged, or a document kind the record cannot name",
    )
    paired_cases: int = Field(ge=0, default=0, description="Cases written at both moments")
    baseline: MeritsBacktestBaseline
    unavailable: list[str] = Field(
        default_factory=list,
        description="Predictors dropped whole because their engine was not installed",
    )
    lost_cells: list[MeritsBacktestCellLoss] = Field(default_factory=list)
    entries: list[MeritsBacktestEntry] = Field(default_factory=list)


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
    against the rates in ``fedcourtsai.pricing`` and ``fedcourtsai.ops`` — check
    the provider billing dashboards for ground truth.

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


ScheduleStaleReason = Literal["conference_passed"]
ScheduledDayStaleReason = Literal["passed"]


class ScheduledDay(_Strict):
    """One date the Court has set on a docket, as the live channel last read it.

    `upcoming` carries the date only while it falls on or after the schedule's
    `as_of`; once it has passed, the row keeps the date as read in `set_for`
    and says why it is no longer scheduled, so a past date is never shown as
    upcoming.
    """

    set_for: date = Field(description="The date the docket names, whether or not it has passed")
    upcoming: date | None = Field(
        description="`set_for`, when it falls on or after `as_of`; null exactly when "
        "`stale_reason` is set"
    )
    stale_reason: ScheduledDayStaleReason | None = Field(
        default=None,
        description="Why the day carries no `upcoming` date: `passed` (`set_for` is before "
        "`as_of`, and the docket shows no newer setting yet). Null while the date is ahead",
    )

    @model_validator(mode="after")
    def _stale_exactly_when_not_upcoming(self) -> ScheduledDay:
        """A day is either upcoming or says why it is not."""
        if (self.upcoming is None) == (self.stale_reason is None):
            raise ValueError("stale_reason is set exactly when upcoming is null")
        return self


class ScheduleEntry(_Strict):
    """One pending, already-public docket's next dates at the Court.

    A row exists for every docket on the public set that has at least one of
    three dates in play: the conference an undecided petition is distributed
    for, the day a granted case awaiting its merits decision is set for
    argument, and the deadline for a response that is still owed. Each date is
    published only while it falls on or after the schedule's `as_of`; once it
    has passed and the docket has not moved, the row keeps the date as read and
    says why it is no longer a scheduled date, so a past date is never shown as
    upcoming.
    """

    case_id: str = Field(description="``<court>/<docket>`` of an already-public case")
    next_conference: date | None = Field(
        default=None,
        description="The conference the docket is distributed for, when it falls on or "
        "after `as_of`; null when `stale_reason` is set, and when the row names no "
        "conference (`distributed_for_conference` null)",
    )
    distributed_for_conference: date | None = Field(
        default=None,
        description="The corpus `distributed_for_conference`: the date named by the "
        "docket's newest 'DISTRIBUTED for Conference of …' entry, as the live channel "
        "last read it, whether or not it has passed. Null on an undecided docket never "
        "distributed, and on a granted case, whose conference is behind it",
    )
    stale_reason: ScheduleStaleReason | None = Field(
        default=None,
        description="Why the row carries no `next_conference` although it names a "
        "conference: `conference_passed` (the conference is before `as_of` and the "
        "docket shows no newer distribution or a decision yet). Null while the date is "
        "still ahead, and on a row that names no conference",
    )
    argument: ScheduledDay | None = Field(
        default=None,
        description="The day the docket's newest 'SET FOR ARGUMENT on …' entry names, on "
        "a granted case the Court has not yet decided. Null when the case is not set for "
        "argument, or has been argued on or after that day",
    )
    response_due: ScheduledDay | None = Field(
        default=None,
        description="The newest stated deadline for a response to the petition or "
        "application, while the docket is undecided and the response is still owed. Null "
        "when no deadline is stated, or a response or waiver followed it",
    )
    last_live_polled: date | None = Field(
        default=None,
        description="When the live channel last read this docket — the per-case vintage of "
        "every date on the row, which `as_of` is not",
    )

    @model_validator(mode="after")
    def _stale_exactly_when_unscheduled(self) -> ScheduleEntry:
        """A conference is either scheduled or says why it is not; a row holds a date."""
        if self.distributed_for_conference is None:
            if self.next_conference is not None or self.stale_reason is not None:
                raise ValueError("next_conference and stale_reason need distributed_for_conference")
        elif (self.next_conference is None) == (self.stale_reason is None):
            raise ValueError("stale_reason is set exactly when next_conference is null")
        if (
            self.distributed_for_conference is None
            and self.argument is None
            and self.response_due is None
        ):
            raise ValueError("a schedule row carries a conference, an argument or a deadline")
        return self


class Schedule(_Strict):
    """``data/schedule/schedule.json`` — the Court's next dates, public set only.

    Written by the live poll from the corpus it already holds, after each cycle,
    for the dockets the repository already discloses under ``data/cases``: it is
    enumerated from that committed tree alone and never from a corpus scan, the
    same compilation-extent boundary as the scope manifest. Display data for
    the public site: it is not a prediction-ledger record (a schedule moves on
    every relist), nothing predicts, evaluates or scores on it, and no cell is
    provisioned with it. ``skipped`` is set, with no entries, when no corpus was
    present.
    """

    schema_version: Literal["1.0", "1.1"] = Field(
        default="1.1",
        description="The artifact's schema version. A reader keys on it: a `1.1` row adds "
        "`argument` and `response_due`, and may name no conference",
    )
    skipped: bool = Field(
        default=False, description="True when no corpus was present; nothing was read"
    )
    as_of: date | None = Field(
        default=None,
        description="The UTC day the schedule was built on, which decides whether a "
        "date has passed; null on a skipped build",
    )
    entries: list[ScheduleEntry] = Field(
        default_factory=list,
        description="One entry per pending public docket with a conference, an argument "
        "day or a response deadline in play, in case_id order",
    )

    @model_validator(mode="after")
    def _a_1_0_row_is_a_conference(self) -> Schedule:
        """A `1.0` schedule carries conferences only: the other dates need `1.1`."""
        if self.schema_version == "1.0" and any(
            entry.distributed_for_conference is None
            or entry.argument is not None
            or entry.response_due is not None
            for entry in self.entries
        ):
            raise ValueError("argument, response_due and conference-less rows need 1.1")
        return self


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


class QpTopicApplicationReferenceEntry(_Strict):
    """One hand-labeled emergency application: a case, its input shape and its primary topic.

    Labeled under the ``qp-topic-v1`` application contract from the
    ``application-extract-v1`` row a labeler reads (``docs/qp-topic.md``,
    *Applications*), so a labeler can be scored against it on identical input.
    """

    case_id: str = Field(
        description="Canonical ``<court>/<docket>`` id — joins the corpus row and the extract"
    )
    docket_number: str = Field(
        description="The application's docket number (e.g. ``24A949``) — the second "
        "half of the key pair the reference join is checked on"
    )
    input_kind: Literal["application-text", "docket-only"] = Field(
        description="Which extract shape the label was read from: with the stored "
        "application text, or from the caption, court below and docket entries alone"
    )
    label: QpTopicLabel = Field(description="The adjudicated primary label")


class QpTopicApplicationReference(_Strict):
    """``data/qp-topics/qp-topic-reference-applications.json`` — the application reference block.

    The measurement baseline for a ``qp-topic-v1`` labeler on application rows,
    kept apart from the petition reference set so that set stays byte-identical
    and an application gate's floors can bind apart from the petition gate's.
    Its sample is stratified on disposition, among other things, so membership
    is outcome-conditioned in the same way the petition set's is, which is why
    the cell prompts forbid predict/evaluate cells from reading anything under
    ``data/qp-topics/``. Nothing frozen depends on it.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    vocabulary: Literal["qp-topic-v1"] = Field(
        default="qp-topic-v1",
        description="The label vocabulary every entry draws from",
    )
    extract_rule: Literal["application-extract-v1"] = Field(
        default="application-extract-v1",
        description="The extract rule whose rows the labels were read from",
    )
    cases: int = Field(
        default=0, ge=0, description="Number of hand-labeled applications (== len(entries))"
    )
    entries: list[QpTopicApplicationReferenceEntry] = Field(
        default_factory=list,
        description="One entry per hand-labeled application, in case_id order",
    )

    @model_validator(mode="after")
    def _canonical(self) -> QpTopicApplicationReference:
        if self.cases != len(self.entries):
            raise ValueError("cases must equal len(entries)")
        ids = [entry.case_id for entry in self.entries]
        if ids != sorted(ids) or len(set(ids)) != len(ids):
            raise ValueError("entries must be sorted by case_id and unique")
        return self


class AlignmentSide(StrEnum):
    """Which party argues the conservative position in a granted merits case."""

    petitioner = "petitioner"
    respondent = "respondent"


class AlignmentValence(StrEnum):
    """How clearly a case divides on ideological lines, in the coder's reading.

    Recorded for analytics; the score baselines read only the side and the score.
    ``none`` is a real reading (a technical question with no ideological
    valence), not a gap: the side is still called, as the side whose position
    the coding guide's conservative priorities favor.
    """

    clear = "clear"
    weak = "weak"
    none = "none"


class AlignmentCodeMode(StrEnum):
    """Whether the case was still undecided (forward) or already decided (replay) when coded."""

    forward = "forward"
    replay = "replay"


class AlignmentSideCode(_Strict):
    """One granted merits case's side coding: its conservative side and alignment score.

    The input the score baselines read (``docs/merits-alignment-baseline.md``),
    made once by an agent pass that reads the case's grant-time text and never
    revised. ``contamination_risk`` is true exactly on a ``replay`` code: the
    case was decided before it was coded, so the coder may know the outcome
    from training, and any fit on such codes is labeled possibly optimistic.
    """

    case_id: str = Field(
        min_length=1,
        description="Canonical ``<court>/<docket>`` id — joins the corpus row and ``data/cases``",
    )
    docket_number: str = Field(
        min_length=1,
        description="The Court's own docket number — the second half of the extract join key",
    )
    granted: date = Field(description="The cert grant date the coded text stood at")
    conservative_side: AlignmentSide = Field(
        description="The party whose position is the conservative one"
    )
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="The alignment score `s`: how conservative the outcome will be, read as "
        "P(the conservative side prevails)",
    )
    valence: AlignmentValence = Field(
        description="How clearly the case divides on ideological lines; analytics only"
    )
    note: str = Field(
        min_length=1,
        max_length=400,
        description="The coder's one-sentence reason for the side, in its own words",
    )
    mode: AlignmentCodeMode = Field(
        description="`forward` if the case was undecided when coded, `replay` if decided"
    )
    contamination_risk: bool = Field(
        description="True exactly on a `replay` code: the coder may know the outcome from "
        "training, so a fit on it may be optimistic"
    )
    model: str = Field(min_length=1, description="The model that made the code")
    run_id: str = Field(min_length=1, description="The workflow run that made the code")
    coded_at: date = Field(description="The day the code was made")

    @model_validator(mode="after")
    def _contamination_follows_mode(self) -> AlignmentSideCode:
        if self.contamination_risk != (self.mode == AlignmentCodeMode.replay):
            raise ValueError("`contamination_risk` must be true exactly on a `replay` code")
        if self.coded_at < self.granted:
            raise ValueError("a code cannot predate the grant it was made at")
        return self


class AlignmentSideCodes(_Strict):
    """``data/merits-alignment/alignment-side-codes.json`` — every side code made so far.

    **Append-only**: a case is coded once and its code is never revised, so a
    publish that would replace an entry is refused (``fedcourts
    alignment-side-codes``). Entries are sorted by ``case_id``, one per case.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    scheme: Literal["alignment-side-v1"] = Field(
        default="alignment-side-v1",
        description="The coding guide every entry was made under",
    )
    entries: list[AlignmentSideCode] = Field(default_factory=list)

    @model_validator(mode="after")
    def _one_per_case_in_order(self) -> AlignmentSideCodes:
        ids = [entry.case_id for entry in self.entries]
        if ids != sorted(set(ids)):
            raise ValueError("entries must be one per case, sorted by `case_id`")
        return self


PolicyAreaLabel = Literal[
    "immigration",
    "federal-executions",
    "foreign-affairs",
    "elections-census",
    "personnel-removal",
    "education",
    "health",
    "environment-energy",
    "firearms",
    "other",
]
"""The executive policy-area vocabulary (``policy-area-v1``), in reporting order.

Defined here so the application labels artifact can carry a policy area;
:mod:`fedcourtsai.pipeline.policy_area` documents what each area covers.
"""


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


class QpTopicApplicationLabelEntry(QpTopicLabelEntry):
    """One line of the labeler's JSONL on the application frame.

    The topic line plus the executive policy area, which the labeler gives on
    a row the extract marks ``policy_row`` and on no other (``docs/qp-topic.md``,
    *Policy areas*).
    """

    policy_area: PolicyAreaLabel | None = Field(
        default=None,
        description="The executive policy area the application is about, under the "
        "policy-area-v1 vocabulary; given only on a row the extract marks policy_row",
    )


class QpTopicPublishedEntry(QpTopicLabelEntry):
    """One row of the accumulating labels artifact: a label plus where it came from.

    The labeler's own line (:class:`QpTopicLabelEntry`) plus the two provenance
    stamps the artifact needs and the labeler must never write — which is why
    they live on a subclass rather than on the line format: the base model
    forbids extra keys, so a labeler that emitted ``source`` or ``batch`` fails
    validation instead of stamping its own provenance.

    ``source`` is the split the batching design turns on. A row inside the hand
    reference set publishes the reference's **adjudicated** label, never the
    labeler's — the labeler's call on those rows is a measurement input, scored
    into the agreement rate and discarded — so a labeler flip on a reference
    case moves that run's measured rate and can never change a published row.
    Every other row publishes the labeler's own call, once: later batches
    exclude what is already here, so no second labeling of the same row exists
    to disagree with the first.

    ``batch`` is the labeling run that first published the row, indexed from 1
    and joined to :class:`QpTopicBatchEntry` for that run's labeler and measured
    agreement. It is *first* published rather than most recently written because
    reference rows are re-read every run and would otherwise all carry the
    newest batch, erasing when the row entered the artifact.
    """

    source: Literal["labeler", "reference"] = Field(
        description="Where this row's published label came from: the labeler's own call, or "
        "the hand reference set's adjudicated label for a reference member"
    )
    batch: int = Field(
        ge=1, description="The labeling batch that first published this row (1-indexed)"
    )


class QpTopicBatchEntry(_Strict):
    """One labeling run's contribution to the accumulating labels artifact.

    The artifact is the union of every batch, so without this ledger a reader
    could not tell which run produced which row, what it was measured at, or how
    many runs the file took. Each row records both counts because they answer
    different questions: ``published`` is what the batch added to the file, while
    ``measured`` is what its labeler actually read — larger by the reference rows
    it re-graded, which are the per-run cost of the measurement and publish
    nothing new.

    The measurement fields are kept per batch rather than only at the top level
    so a drifting labeler is visible as a series rather than as a single current
    number — with two readings the series will not support. Every batch is
    scored over the **same** reference entries, so the differences between rows
    are labeler-side re-labeling of identical items, not independent samples of
    anything: a few points of movement on ``n`` this size is noise, and only a
    sustained move reads. And ``agree``/``n`` never read without ``floor``, which
    is why it is carried here rather than recomputed: on a sixteen-label
    vocabulary most of any rate is the floor.
    """

    batch: int = Field(ge=1, description="1-indexed labeling run, ascending and gapless")
    labeler: str = Field(
        min_length=1, description="Who assigned this batch's labels — engine and model"
    )
    published: int = Field(ge=0, description="Rows this batch first published into the artifact")
    labeler_rows: int = Field(
        default=0,
        ge=0,
        description="Of those, rows carrying this labeler's own call. The remainder are "
        "reference members entering the artifact from the hand set's adjudicated labels, "
        "which no labeler assigned — so this, not `published`, is what a batch labeled",
    )
    measured: int = Field(
        ge=0,
        description="Extract rows this batch's labeler read — its new rows plus every "
        "reference row in the frame, re-graded for the measurement",
    )
    agree: int = Field(ge=0, description="Compared reference entries this batch matched")
    n: int = Field(ge=0, description="Reference entries this batch covered and compared")
    floor: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="What a constant labeler scores on this batch's compared entries — the "
        "rate is unreadable without it, and only the distance above it is skill",
    )
    fired: int = Field(
        default=0, ge=0, description="Texts in this batch exactly one shadow rule fired on"
    )
    disagreements: int = Field(
        default=0,
        ge=0,
        description="Of those, texts where this batch's labeler differed from the rule. The "
        "shadow rules are the only instrument that touches rows the batch publishes, so the "
        "series is the regression trip-wire; its level is uninterpretable",
    )
    superseded: int = Field(
        default=0,
        ge=0,
        description="Rows already in the artifact whose published label this batch changed. "
        "Only ever rows whose published label became the hand set's: a reference entry "
        "relabeled by hand, or a row the reference set has since taken in",
    )
    frame_rows: int | None = Field(
        default=None,
        ge=1,
        description="QP-bearing rows in the labeling frame when this batch was cut, as the "
        "extract counted them. The denominator that turns the labeled share of the frame "
        "from a bound into a measurement, at this batch's corpus vintage and no other's. "
        "None where the extract reported no count",
    )
    policy_agree: int | None = Field(
        default=None,
        ge=0,
        description="Application frame: hand-labeled rows whose policy area the labeler "
        "matched; null where the batch measured no policy area",
    )
    policy_n: int | None = Field(
        default=None, ge=0, description="Hand-labeled rows compared on policy area"
    )
    policy_published: int | None = Field(
        default=None,
        ge=0,
        description="Policy areas this batch published; 0 when its policy measurement was refused",
    )

    @model_validator(mode="after")
    def _frame_holds_the_batch(self) -> QpTopicBatchEntry:
        # The batch is cut from the frame, so a frame smaller than the rows the
        # labeler read is not a thin frame but a wrong number — most likely one
        # measured against a different scope or a different blob. Refuse it here
        # rather than let the docket pack divide by it.
        if self.frame_rows is not None and self.frame_rows < self.measured:
            raise ValueError(
                f"frame_rows ({self.frame_rows}) is under the {self.measured} row(s) batch "
                f"{self.batch} measured; the batch is drawn from the frame"
            )
        return self


class QpTopicLabelAgreement(_Strict):
    """One label's agreement between a labeler and the frame's reference rater.

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
        description="agree / n — agreement with the frame's reference rater, not accuracy. Null "
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
        description="overall_agree / overall_n — agreement with the frame's reference rater, not "
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
    """``data/qp-topics/qp-topics.json`` — the accumulating ``qp-topic-v0`` labels.

    The primary label for every question-presented text labeled so far, each
    assigned from that text alone. The file **accrues**: the labeling frame runs
    well past what one dispatch can finish, so each run labels a derived batch
    and the artifact is the union of every batch to date (``docs/qp-topic.md``).
    ``entries`` and ``cases`` are therefore cumulative, while ``agreement`` and
    ``shadow`` describe the **most recent run only** — they are measured over
    that run's extract, and ``batches`` keeps every run's figures so the series
    is readable rather than just the latest point.

    The artifact is written only when the agreement gate passes, so a labels file
    on disk is one whose measurement is on the record beside it. Labels here are
    a corpus description, not a prediction claim, and nothing frozen reads them.
    Every published cut drawn from this file carries the coverage caveat in
    ``docs/qp-topic.md``, and neither ``secondary`` nor ``vehicle`` may appear in
    one while the reference set leaves them unmeasured.

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
        description="Who assigned the most recent batch's labels — a free-form actor string "
        "(engine and model), so a measured agreement is attributable to what produced it. "
        "Earlier batches carry their own labeler in `batches`",
    )
    cases: int = Field(
        default=0, ge=0, description="Labeled cases across every batch (== len(entries))"
    )
    agreement: QpTopicAgreement = Field(
        description="The most recent run's measured agreement with the v0 reference rater"
    )
    shadow: QpTopicShadow = Field(
        description="The most recent run's shadow-rule firing and disagreement counts"
    )
    batches: list[QpTopicBatchEntry] = Field(
        default_factory=list,
        description="One row per labeling run that contributed, in batch order",
    )
    entries: list[QpTopicPublishedEntry] = Field(
        default_factory=list,
        description="One entry per labeled case, in case_id order, across every batch",
    )

    @model_validator(mode="after")
    def _canonical(self) -> QpTopicLabels:
        _check_labels_accrual(self.cases, self.entries, self.batches)
        return self


def _check_labels_accrual(
    cases: int, entries: Sequence[QpTopicPublishedEntry], batches: Sequence[QpTopicBatchEntry]
) -> None:
    """The accrual invariants every labels artifact holds, whichever frame it labels."""
    if cases != len(entries):
        raise ValueError("cases must equal len(entries)")
    ids = [entry.case_id for entry in entries]
    if ids != sorted(ids) or len(set(ids)) != len(ids):
        raise ValueError("entries must be sorted by case_id and unique")
    numbers = [row.batch for row in batches]
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("batches must be numbered 1..n in order")
    if sum(row.published for row in batches) != cases:
        raise ValueError("the batch ledger's published counts must sum to cases")
    unknown = sorted({entry.batch for entry in entries} - set(numbers))
    if unknown:
        raise ValueError(f"entries cite batches with no ledger row: {unknown}")


class QpTopicApplicationPublishedEntry(QpTopicPublishedEntry):
    """One row of the accumulating application labels artifact.

    A published label plus the extract shape it was read from, stamped by the
    builder from the extract row and never by the labeler: a label read from a
    caption and a stay request is weaker than one read from the application's
    own text, and a cut reports the two apart (``docs/qp-topic.md``,
    *Applications*).
    """

    input_kind: Literal["application-text", "docket-only"] = Field(
        description="Which extract shape the label was read from: with the stored "
        "application text, or from the caption, court below and docket entries alone"
    )
    policy_area: PolicyAreaLabel | None = Field(
        default=None,
        description="The executive policy area (policy-area-v2), set once by the first batch "
        "whose policy measurement passed its gate; null on a row with none",
    )
    policy_source: Literal["labeler", "reference"] | None = Field(
        default=None,
        description="Where the policy area came from: the labeler, or the policy-area-v1 hand "
        "label for a row the hand set covers",
    )
    policy_batch: int | None = Field(
        default=None, ge=1, description="The batch that published the policy area"
    )

    @model_validator(mode="after")
    def _policy_fields_travel_together(self) -> QpTopicApplicationPublishedEntry:
        present = [
            field is not None for field in (self.policy_area, self.policy_source, self.policy_batch)
        ]
        if any(present) and not all(present):
            raise ValueError(
                f"{self.case_id}: policy_area, policy_source and policy_batch are set together"
            )
        return self


class QpTopicPolicyAreaShare(_Strict):
    """One hand-labeled policy area's agreement between the labeler and the hand labels."""

    area: PolicyAreaLabel = Field(description="The hand label's area")
    agree: int = Field(ge=0, description="Hand-labeled rows of this area the labeler matched")
    n: int = Field(ge=0, description="Hand-labeled rows of this area compared")


class QpTopicPolicyAgreement(_Strict):
    """One batch's policy-area measurement against the ``policy-area-v1`` hand labels.

    Agreement with hand labels whose raters were not blind to the outcome and
    read their own knowledge of a public case, which the labeler may not, so
    it is agreement with that reference and not accuracy.
    """

    reference_rule: Literal["policy-area-v1"] = Field(
        default="policy-area-v1", description="The hand labels measured against"
    )
    reference_rows: int = Field(
        ge=0, description="Hand-labeled rows in the batch, each a policy row"
    )
    reference_total: int = Field(ge=0, description="Hand-labeled rows in the committed set")
    agree: int = Field(ge=0, description="Compared rows whose policy area matches the hand label")
    n: int = Field(ge=0, description="Hand-labeled rows the labeler gave a policy area")
    rate: float | None = Field(
        default=None, ge=0, le=1, description="agree / n; null when nothing was compared"
    )
    floor: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="The rate a constant labeler would score: the commonest hand area's share",
    )
    uncovered: int = Field(
        ge=0, description="Hand-labeled rows in the batch the labeler gave no policy area"
    )
    off_frame: int = Field(
        default=0,
        ge=0,
        description="Lines that gave a policy area on a row not marked policy_row; dropped",
    )
    per_area: list[QpTopicPolicyAreaShare] = Field(
        default_factory=list, description="Agreement per hand area, in vocabulary order"
    )
    gate_passed: bool = Field(
        description="Whether the rate cleared the agreement gate with the hand rows covered"
    )

    @model_validator(mode="after")
    def _counts_hold(self) -> QpTopicPolicyAgreement:
        if self.agree > self.n or self.n + self.uncovered != self.reference_rows:
            raise ValueError(
                "policy agreement counts do not hold: agree <= n and n + uncovered == "
                "reference_rows"
            )
        if sum(share.n for share in self.per_area) != self.n:
            raise ValueError("per-area n does not sum to the compared rows")
        return self


class QpTopicApplicationLabels(_Strict):
    """``data/qp-topics/qp-topics-applications.json`` — the ``qp-topic-v1`` application labels.

    The application frame's counterpart to :class:`QpTopicLabels`, kept in a file
    of its own so the petition artifact and every reader of it are untouched and
    the application gate binds apart from the petition gate. It accrues the same
    way, batch by batch, and a reference member publishes the application
    reference block's adjudicated label rather than the labeler's. ``agreement``
    and ``shadow`` describe the most recent run only, measured against the
    application reference block; ``batches`` keeps every run's figures, and each
    ledger row's ``frame_rows`` counts the application frame.

    Written only when the application gate passes. Agreement here is with the
    block's adjudicated labels, not accuracy, and the block's raters and fitted
    rules are disclosed in ``docs/qp-topic.md``. Labels here are a corpus
    description, not a prediction claim, and nothing frozen reads them.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    vocabulary: Literal["qp-topic-v1"] = Field(
        default="qp-topic-v1",
        description="The label vocabulary every entry draws from",
    )
    extract_rule: Literal["application-extract-v1"] = Field(
        default="application-extract-v1",
        description="The extract rule whose rows every label was read from",
    )
    labeler: str = Field(
        min_length=1,
        description="Who assigned the most recent batch's labels — engine and model. Earlier "
        "batches carry their own labeler in `batches`",
    )
    cases: int = Field(
        default=0, ge=0, description="Labeled applications across every batch (== len(entries))"
    )
    agreement: QpTopicAgreement = Field(
        description="The most recent run's measured agreement with the application reference block"
    )
    shadow: QpTopicShadow = Field(
        description="The most recent run's shadow-rule counts over the stored application text"
    )
    policy_agreement: QpTopicPolicyAgreement | None = Field(
        default=None,
        description="The most recent policy-area measurement that passed its gate, which the "
        "standing policy areas were published under; null until one has. A refused policy "
        "measurement is recorded on its batch's ledger row and leaves this unchanged",
    )
    batches: list[QpTopicBatchEntry] = Field(
        default_factory=list,
        description="One row per labeling run that contributed, in batch order",
    )
    entries: list[QpTopicApplicationPublishedEntry] = Field(
        default_factory=list,
        description="One entry per labeled application, in case_id order, across every batch",
    )

    @model_validator(mode="after")
    def _canonical(self) -> QpTopicApplicationLabels:
        _check_labels_accrual(self.cases, self.entries, self.batches)
        return self


AiActivityKind = Literal[
    "opinion", "judgment", "ruling", "motion", "complaint", "appeal", "resolution"
]


class AiCaseActivityEntry(_Strict):
    """One significant docket entry an AI watchlist case gained."""

    case: str = Field(
        min_length=1, description="The watchlist case's name, as the watchlist gives it."
    )
    category: str = Field(
        min_length=1, description="The case's category in the watchlist's closed vocabulary."
    )
    court: str = Field(min_length=1, description="CourtListener court id of the docket.")
    docket_id: int = Field(gt=0, description="CourtListener docket id.")
    docket_number: str = Field(min_length=1, description="The court's own docket number.")
    entry_id: int = Field(gt=0, description="CourtListener's id for the docket entry.")
    entry_number: int | None = Field(
        default=None, description="The entry's number on the docket; unnumbered entries carry none."
    )
    date_filed: date = Field(description="The day the entry was filed.")
    kind: AiActivityKind = Field(description="What the entry is, under the record's rule.")
    url: str = Field(
        pattern=r"^https://www\.courtlistener\.com/[A-Za-z0-9/_.~%#-]*$",
        description="The entry on CourtListener: its main document's page, else the docket.",
    )


class AiCaseActivity(_Strict):
    """``data/ai-cases/activity/<YYYY-MM-DD>.json`` — a day's significant AI-case docket entries.

    Written by ``watchlist-refresh`` for the entries a refresh found that the
    stored docket lacked and that the rule (:data:`fedcourtsai.ai_activity.ACTIVITY_RULE`)
    keeps. Identifiers, dates, kinds and links only: no docket text is copied.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    day: date = Field(description="The UTC day the refresh found these entries.")
    rule: str = Field(min_length=1, description="The significance rule's label.")
    entries: list[AiCaseActivityEntry] = Field(
        min_length=1, description="The day's entries, oldest filing first; a quiet day has no file."
    )

    @model_validator(mode="after")
    def _distinct(self) -> AiCaseActivity:
        ids = [e.entry_id for e in self.entries]
        if len(set(ids)) != len(ids):
            raise ValueError("an entry appears twice")
        return self


QpTopicFrame = Literal["petitions", "applications", "alignment-sides"]
QpTopicRunOutcome = Literal["published", "refused", "incomplete", "replicate"]


class QpTopicKindAgreement(_Strict):
    """A replicate's agreement on one application ``input_kind`` of the reference block."""

    input_kind: Literal["application-text", "docket-only"] = Field(
        description="Which input shape the reference rows were read from"
    )
    agree: int = Field(ge=0, description="Reference rows of this kind where the two labels match")
    n: int = Field(ge=0, description="Reference rows of this kind the replicate compared")

    @model_validator(mode="after")
    def _bounded(self) -> QpTopicKindAgreement:
        if self.agree > self.n:
            raise ValueError("agree cannot exceed n")
        return self


class QpTopicReplicate(_Strict):
    """One reference-only replicate's item-level measurement (``docs/qp-topic.md``).

    A replicate labels the frame's reference block alone and publishes nothing:
    it exists to measure how far one labeler's agreement moves between runs on
    identical inputs. The pooled figures sit on the run record beside this; what
    this adds is what separates a run-level component from item-level noise —
    which reference rows this run matched, as one character per reference entry
    in ``case_id`` order — and the shares the gate candidates are cut by. The
    reference entries are committed already, so the string discloses nothing a
    reader of the reference file does not hold. ``reference_sha256`` pins which
    reference the string indexes and ``prompt_sha256`` which labeling prompt was
    read: replicates that differ on either are not pooled, since a reference
    revision or a prompt edit would land in the run-level component.
    """

    reference_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$",
        description="sha256 of the committed reference file the replicate was measured against",
    )
    prompt_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$",
        description="sha256 of the labeling prompt the replicate's labeler read; replicates "
        "under different prompts are not pooled",
    )
    reference_entries: int = Field(ge=1, description="Entries in that reference file")
    matches: str = Field(
        pattern=r"^[01-]+$",
        description="One character per reference entry in case_id order: 1 the labeler "
        "matched the reference label, 0 it did not, - the entry was not in the replicate's "
        "extract",
    )
    unclassifiable: int = Field(
        ge=0,
        description="Compared reference entries the labeler labeled `unclassifiable`",
    )
    per_input_kind: list[QpTopicKindAgreement] = Field(
        default_factory=list,
        description="Agreement per application input kind; empty on the petition frame, "
        "whose reference rows are all questions-presented text",
    )

    @model_validator(mode="after")
    def _consistent(self) -> QpTopicReplicate:
        if len(self.matches) != self.reference_entries:
            raise ValueError("matches carries one character per reference entry")
        kinds = [row.input_kind for row in self.per_input_kind]
        if len(set(kinds)) != len(kinds):
            raise ValueError("an input kind appears twice")
        compared = len(self.matches) - self.matches.count("-")
        if self.unclassifiable > compared:
            raise ValueError("unclassifiable cannot exceed the compared entries")
        if self.per_input_kind and sum(row.n for row in self.per_input_kind) != compared:
            raise ValueError("the per-kind n sum to the compared entries")
        if self.per_input_kind and sum(row.agree for row in self.per_input_kind) != (
            self.matches.count("1")
        ):
            raise ValueError("the per-kind agreements sum to the matched entries")
        return self


class QpTopicRunSpend(_Strict):
    """``data/qp-topics/spend/<run_id>-<run_attempt>.json`` — one labeling run's spend.

    One record per attempt of the labeling job whose engine left an execution
    file, whatever became of the batch: a run refused at the reference gate
    spends as much as one that publishes and writes no labels file, so the
    spend lives here rather than on the labels artifact's batch ledger. The
    token counts are the engine log's, read and priced by the rule every
    cell's ``usage.json`` is (:func:`fedcourtsai.usage.parse_claude_usage`,
    :func:`fedcourtsai.pricing.estimate_cost_usd`), so a labeler dollar and a
    cell dollar are the same dollar, and the measured spend total
    (:func:`fedcourtsai.spend.measured_spend`) sums these by ``recorded_at``.

    The gate figures are carried for the same reason: a refused attempt is on
    file with its measured agreement, and the label seam's review hold reads
    the newest gated outcome per frame (:mod:`fedcourtsai.review_hold`).
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    lane: Literal["qp-topic-label"] = Field(
        default="qp-topic-label", description="The spend lane this run belongs to"
    )
    frame: QpTopicFrame = Field(
        description="Which labeling frame the run labeled: a topic-label frame, or "
        "`alignment-sides` for the merits side coder, which has no reference gate"
    )
    run_id: str = Field(pattern=r"^[0-9]+$", description="The Actions run id of the labeling run")
    run_attempt: int = Field(ge=1, description="The labeling job's run attempt")
    labeler: str = Field(min_length=1, description="Who labeled — engine and model")
    model: str = Field(min_length=1, description="The model the cost rates were applied to")
    outcome: QpTopicRunOutcome = Field(
        description="published: the batch cleared the reference gate (a side-coding run: "
        "coded every row) and its labels were handed to the publish job; refused: it was "
        "measured and fell below the gate; "
        "incomplete: it reached neither (a labels file short of the batch, a check ahead of "
        "the measurement that failed, or a measurement that cleared the gate but did not "
        "reach publication), its gate figures carried wherever it was measured; "
        "replicate: a reference-only replicate that labeled the reference block alone, "
        "measured it, and published nothing by design, so it is neither a pass nor a refusal"
    )
    batch_rows: int = Field(ge=0, description="Rows in the extract the labeler was handed")
    label_lines: int = Field(ge=0, description="Label lines the run left behind")
    agree: int | None = Field(
        default=None, ge=0, description="Compared reference entries matched; null unmeasured"
    )
    n: int | None = Field(
        default=None, ge=0, description="Reference entries compared; null unmeasured"
    )
    rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="agree / n — agreement with the frame's reference, not accuracy; null "
        "when unmeasured or nothing was compared",
    )
    floor: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="What a constant labeler scores on the same compared entries; null "
        "when unmeasured",
    )
    recorded_at: datetime = Field(
        description="When the record was written, timezone-aware; the spend window reads it"
    )
    input_tokens: int = Field(ge=0, description="Fresh input tokens")
    output_tokens: int = Field(ge=0, description="Output tokens")
    cache_read_input_tokens: int = Field(ge=0, description="Cached input tokens read")
    cache_creation_input_tokens: int = Field(ge=0, description="Cache-write tokens")
    estimated_cost_usd: float = Field(
        ge=0.0,
        allow_inf_nan=False,
        description="The run's on-demand cost at `pricing.MODEL_RATES` for `model`, or for "
        "`priced_as` where `model` has no rate",
    )
    priced_as: str | None = Field(
        default=None,
        min_length=1,
        description="The `pricing.MODEL_RATES` entry the run was priced at when `model` has "
        "none: the one that prices these token counts dearest, so an unpriced model's spend "
        "is still counted and never under-counted; null when priced at `model`'s own rate",
    )
    replicate: QpTopicReplicate | None = Field(
        default=None,
        description="A replicate run's item-level measurement; present exactly when the "
        "outcome is `replicate`",
    )

    def _check_replicate(self) -> None:
        if (self.outcome == "replicate") != (self.replicate is not None):
            raise ValueError("a replicate run, and only one, carries its replicate measurement")
        if self.replicate is not None and self.agree is not None and self.n is not None:
            matches = self.replicate.matches
            if self.agree != matches.count("1") or self.n != len(matches) - matches.count("-"):
                raise ValueError("agree and n are the replicate's matched and compared entries")

    @model_validator(mode="after")
    def _consistent(self) -> QpTopicRunSpend:
        if self.recorded_at.tzinfo is None:
            raise ValueError("recorded_at must be timezone-aware")
        measured = self.agree is not None and self.n is not None
        if (self.agree is None) != (self.n is None):
            raise ValueError("agree and n are recorded together or not at all")
        if measured and self.agree is not None and self.n is not None and self.agree > self.n:
            raise ValueError("agree cannot exceed n")
        if self.frame == "alignment-sides":
            # The merits side coder has no reference set, so no gate: a run is
            # published or incomplete, and never carries gate figures.
            if self.outcome in ("refused", "replicate"):
                raise ValueError(f"a side-coding run has no gate, so it is never {self.outcome}")
            if measured or self.rate is not None or self.floor is not None:
                raise ValueError("a side-coding run carries no gate figures")
        elif self.outcome != "incomplete" and not measured:
            raise ValueError(f"a {self.outcome} run carries its gate figures")
        self._check_replicate()
        if self.outcome == "published" and self.label_lines != self.batch_rows:
            raise ValueError("a published run labeled every row of its batch")
        if self.rate is not None and not measured:
            raise ValueError("a rate is recorded only beside its agree and n")
        if self.agree is not None and self.n is not None:
            if self.n == 0 and self.rate is not None:
                raise ValueError("nothing was compared, so there is no rate")
            if self.n > 0 and (self.rate is None or abs(self.rate - self.agree / self.n) > 1e-9):
                raise ValueError("rate is agree / n")
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
    entries strictly preceding ``record/context.json``'s ``decided_before`` —
    its own **docket-number** Term, which is what these entries are keyed on and
    what the cell is handed as ``DECIDED_BEFORE``, so its own entry (which
    already holds its disposition) is always behind the bar. The cell's
    day-level *retrieval* boundary is a different field, ``cutoff``, which it
    reads as ``REPLAY_CUTOFF``; no anchoring Term is ever derived from it,
    because for a petition held over past its Term that day falls in a later
    Term than the docket and a Term read off it would hand the cell its own row.
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
    reweighted. The unit is the application number, not the corpus row: a
    number stored under two case ids counts once
    (:func:`fedcourtsai.corpus.duplicate_application_case_ids`). This slice's
    own ``substantive_grant_rate`` stays **descriptive** — it describes the
    accumulated cohort and, at the pack level, contains every Term including a
    scored case's own. The *scored* interim baseline is built
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
        "addressable population) in this slice, each number counted once: a number "
        "the corpus stores under two case ids counts one row only (see "
        "`duplicate_rows`), here and in every count below",
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
    duplicate_rows: int | None = Field(
        default=None,
        ge=0,
        description="Corpus rows left out of every count here because another row "
        "carries the same application number (`corpus.duplicate_application_case_ids`: "
        "one row per number, an observed row before a stub, then the lowest docket "
        "id). Absent from a pack built before the one-row-per-number rule, which "
        "counted rows, so absent reads as unknown, never as zero",
    )

    @model_serializer(mode="wrap")
    def _omit_unset_duplicate_rows(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``duplicate_rows`` while unset, so a pack built before it reads as before."""
        payload = handler(self)
        if isinstance(payload, dict) and self.duplicate_rows is None:
            payload.pop("duplicate_rows", None)
        return payload


class StatPackInterimTerm(_StatPackInterimCounts):
    """One application-Term's slice of the interim docket.

    The Term is read from the application's own docket number (``24A1099`` ->
    OT2024), so the split needs no dates. Like the cert Term entries, the array
    is a replay self-selection surface: a time-masked cell anchors only on Term
    rows strictly preceding ``record/context.json``'s ``decided_before`` — the
    cell's own docket Term, never a Term derived from its retrieval boundary.
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
    ``record/context.json``'s ``decided_before`` — the cell's own docket Term,
    never a Term derived from its retrieval boundary.
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


class StatPackAuthorshipJustice(_Strict):
    """One Justice's writings over one Term of the per-opinion record.

    Two denominators, because the two authorship claims resolve over different
    populations. ``decisions`` counts the Term's deciding documents decided
    while the Justice served, the population ``majority-author`` resolves over;
    ``sat`` counts the signed decisions whose bench was observed with the
    Justice taking part, the population ``separate-writers`` resolves over.
    """

    justice: str = Field(description="The Justice's name as the roster spells it")
    decisions: int = Field(
        ge=0,
        description="Argued decisions (signed or per curiam) decided while the Justice served",
    )
    majority: int = Field(
        ge=0,
        description="Of `decisions`, those whose lead opinion (of the Court, or a "
        "plurality) the Justice delivered",
    )
    sat: int = Field(
        ge=0,
        description="Signed decisions whose observed bench has the Justice taking part",
    )
    separate: int = Field(
        ge=0,
        description="Of `sat`, those the Justice wrote or co-wrote anything in but "
        "the lead opinion: a concurrence, a dissent, either in part",
    )


class StatPackAuthorshipTerm(_Strict):
    """One October Term of the per-opinion record, keyed by the listing's Term."""

    term: int = Field(
        description="The October-Term year the opinions listing files the decisions under"
    )
    decisions: int = Field(
        ge=0, description="Argued decisions: one per listing row, signed or per curiam"
    )
    per_curiam: int = Field(ge=0, description="Of `decisions`, those decided per curiam")
    observed: int = Field(
        ge=0, description="Signed decisions whose bench the record observed (a filled bench row)"
    )
    justices: list[StatPackAuthorshipJustice] = Field(
        default_factory=list,
        description="Every Justice seated on a counted decision's date, in roster order",
    )


class StatPackJusticeVotesJustice(_Strict):
    """One Justice's merits votes over one Term, or over a pooled span of Terms."""

    justice: str = Field(description="The Justice's name as the vote source spells it")
    sat: int = Field(ge=0, description="Complete-lineup decisions the Justice took part in")
    majority: int = Field(
        ge=0, description="Of `sat`, those voting with the judgment (majority or concurring in it)"
    )
    in_part: int = Field(ge=0, description="Of `sat`, those voting in part on each side")
    disturb_eligible: int = Field(
        ge=0,
        description="Of `sat`, whole-side votes on a plain affirmed, reversed or vacated judgment",
    )
    disturb: int = Field(
        ge=0, description="Of `disturb_eligible`, those voting to disturb the judgment below"
    )


class StatPackJusticeVotesPair(_Strict):
    """Two Justices' agreement over the decisions both voted a whole side on."""

    justices: tuple[str, str] = Field(description="The pair, in name order")
    both: int = Field(ge=0, description="Decisions both Justices voted a whole side on")
    agree: int = Field(ge=0, description="Of `both`, those where they voted the same side")


class StatPackJusticeVotesTerm(_Strict):
    """One October Term of per-Justice merits votes."""

    term: int = Field(description="The October Term of the opinions listing")
    documents: int = Field(ge=0, description="Listing rows the per-opinion record holds")
    complete: int = Field(ge=0, description="Of `documents`, those with a complete lineup")
    judged: int = Field(
        ge=0,
        description="Of `complete`, those whose case row carries a plain affirmed, "
        "reversed or vacated judgment",
    )
    justices: list[StatPackJusticeVotesJustice] = Field(default_factory=list)
    pairs: list[StatPackJusticeVotesPair] = Field(default_factory=list)


class StatPackJusticeVotes(_Strict):
    """The statpack's per-Justice merits votes, per Term, most recent Term first.

    Rolled up by ``pipeline.justice_priors`` from the merits lineups (the
    ``opinions`` and ``opinion_benches`` corpus tables) and each decided case
    row's parsed judgment, over complete lineups only. A merits cell pools the
    Terms strictly before its case's grant Term. Present only once the record
    holds a complete lineup.
    """

    terms: list[StatPackJusticeVotesTerm] = Field(default_factory=list)


class StatPackAuthorship(_Strict):
    """The statpack's authorship section: who wrote the Court's decisions, per Term.

    Read off the per-opinion record (the `opinions` and `opinion_benches`
    corpus tables), the committed feed of the authorship claims' baselines
    (``pipeline.base_rates.majority_author_base_rate`` and
    ``separate_writing_base_rate``), which pool it strictly-prior. Present only
    once the record holds an argued decision, as the other stage sections join on
    their feeds.
    """

    terms: list[StatPackAuthorshipTerm] = Field(
        default_factory=list, description="Per-Term detail, most recent Term first"
    )


class AuthorshipTallyCase(_Strict):
    """One case of an argument sitting in a cell's authorship tally."""

    key: str = Field(
        description="The corpus case id, or `docket:<number>` where the per-opinion "
        "record links the opinion to no corpus row"
    )
    docket: str = Field(description="The docket number as the record prints it")
    argued: date = Field(description="The day the case was argued")
    decided: date | None = Field(
        description="The day the case was decided, on or before the tally's `as_of`; "
        "null while undecided as of that day"
    )
    author: str | None = Field(
        description="The lead opinion's author (the opinion of the Court or a "
        "plurality), as the roster spells the Justice; null while undecided, for a "
        "decision no opinion names an author for (a per curiam, a dismissal), and "
        "for one the per-opinion record does not hold (`recorded` false)"
    )
    recorded: bool = Field(
        description="Whether the per-opinion record holds the case's lead opinion; "
        "a decided case it does not hold has an unknown author, not a missing one"
    )


class AuthorshipTallySitting(_Strict):
    """One argument sitting of a cell's authorship tally."""

    start: date = Field(description="The sitting's first day, as the Court heads it")
    end: date = Field(description="The sitting's last day, as the Court heads it")
    bench: list[str] = Field(
        description="The Justices serving on the sitting's first day, oldest oath first"
    )
    yet_to_write: list[str] = Field(
        description="The bench's Justices with no lead opinion recorded for the "
        "sitting as of the tally's day, oldest oath first"
    )
    cases: list[AuthorshipTallyCase] = Field(
        description="The sitting's cases, by argument day then key"
    )


class SameQuestionEntry(_Strict):
    """One petition on a same-question list: identifiers and status, no text."""

    docket_number: str
    case_id: str
    score: float = Field(ge=0, le=1, description="The TF-IDF cosine with the listing petition")
    docketed: date | None
    status: str = Field(
        description="`pending` as of the cutoff, or the disposition once resolved before it"
    )


class SameQuestionList(_Strict):
    """One cell's same-question petitions, staged as its ``record/same-question.json``."""

    case_id: str = Field(description="The listing petition's case id")
    event_id: str = Field(description="The cell's event, whose moment set the cutoff")
    cutoff: date = Field(
        description="Exclusive: only petitions docketed before this day are listed or "
        "weighted, and a status reads resolved only where its date falls before it"
    )
    threshold: float = Field(
        ge=0, le=1, description="The least score a petition had to reach to be listed"
    )
    indexed: int = Field(
        ge=0, description="Petitions docketed before the cutoff with a stored questions presented"
    )
    petitions: list[SameQuestionEntry] | None = Field(
        description="Best first, at most the match limit; `null` where the listing petition has no "
        "stored questions presented docketed before the cutoff to match on"
    )


class SameQuestionLists(_Strict):
    """A round's same-question lists, one per cert-stage cell, as the plan job writes them."""

    lists: list[SameQuestionList]


class AuthorshipTally(_Strict):
    """Who has written from each argument sitting of a Term, as of one day.

    Written by ``fedcourts authorship-tally`` and, for a post-argument merits
    predict cell in forward mode once released (``provision.AUTHORSHIP_TALLY_WITHHELD``),
    into its ``record/authorship-tally.json`` (``pipeline.authorship``): the tally
    as of the day before the cell's cutoff, so the cell reads no decision its
    moment postdates.
    """

    term: int = Field(description="The October Term tallied")
    as_of: date = Field(description="The last day whose decisions are read, inclusive")
    sittings: list[AuthorshipTallySitting] = Field(
        default_factory=list,
        description="The Term's sittings that opened by `as_of`, earliest first; "
        "empty where the corpus stores none",
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
    authorship: StatPackAuthorship | None = Field(
        default=None,
        description="Who wrote the Court's decisions per Term, off the per-opinion "
        "record — the authorship claims' baseline feed; None — and omitted from "
        "the serialized pack — while the record holds no argued decision",
    )
    justice_votes: StatPackJusticeVotes | None = Field(
        default=None,
        description="Each Justice's merits votes per Term, off the complete merits "
        "lineups — the per-Justice priors a merits cell pools strictly before its "
        "grant Term; None — and omitted from the serialized pack — while the record "
        "holds no complete lineup",
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
            if self.authorship is None:
                payload.pop("authorship", None)
            if self.justice_votes is None:
                payload.pop("justice_votes", None)
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


class QpTopicSupport(_Strict):
    """The raw rows behind one bucket of the published topic distribution.

    Every count in the topic table is denial-reweighted, so a bucket's `est. n=`
    is a population estimate and not the number of petitions anyone read. On a
    frame that is still accruing, the gap between the two can be an order of
    magnitude — one sampled denial stands for ten — so the smallest buckets
    publish a disposition split over a handful of rows. This is the raw view a
    reweighted bucket otherwise has none of, and the reason it is per label
    rather than pooled: the thin buckets are not the ones a reader would guess.

    ``reference_rows`` is carried beside it because the two populations enter on
    different terms: a reference-set member rides in every batch, so a bucket
    that is mostly reference rows is the block's mix rather than the frame's.
    """

    label: QpTopicLabel = Field(description="The primary `qp-topic-v0` label this bucket counts")
    rows: int = Field(ge=0, description="Labeled cases in this bucket — rows on hand, unweighted")
    reference_rows: int = Field(
        default=0,
        ge=0,
        description="Of those, rows published from the hand reference set, which is in every "
        "batch and so over-represented while the frame is still accruing",
    )


class DocketPackQpTopics(_Strict):
    """The question-presented topic distribution, inseparable from how it was labeled.

    A topic share is only readable beside the labeling that produced it and its
    measured agreement with the ``qp-topic-v0`` reference rater, so the two
    travel in one object rather than as a section a quotation can lift alone.
    ``agree``/``n`` is **agreement, not accuracy**: with a single hand rater,
    reference error and labeler error cannot be separated, and the reference
    frame is grant-enriched, so the figure certifies the grant stream only
    (``docs/qp-topic.md``).

    The labels artifact **accrues across dispatches**, so the pairing is looser
    than one run's: ``labeler`` and ``agree``/``n`` are the most recent batch's,
    while the rows counted in ``section`` come from ``batches`` runs that may
    have had different labelers. The rate therefore certifies the batch that
    produced it, not every row beside it, and ``batches`` is carried so a reader
    can see that rather than infer one run. Per-batch labelers and rates are in
    the labels artifact's own ledger.

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
        description="Who assigned the most recent batch's labels — the free-form actor string "
        "from the labels artifact. Earlier batches may name a different one, so this attributes "
        "the measurement below, not every row in the table",
    )
    batches: int = Field(
        default=1,
        ge=1,
        description="Labeling runs the artifact accrued over. Above 1, the table's rows come "
        "from several runs while `labeler` and `agree`/`n` are the latest run's alone",
    )
    reference_rows: int = Field(
        default=0,
        ge=0,
        description="Labeled cases whose published label is the hand reference set's "
        "adjudicated one. They are in **every** batch by construction, so while the frame is "
        "still accruing they enter the table at a far higher inclusion rate than a drawn row "
        "and the mix is not the frame's — the section's scope note states it",
    )
    frame_rows: int | None = Field(
        default=None,
        ge=1,
        description="QP-bearing rows in the labeling frame the newest batch was cut from, as "
        "that batch's extract counted them. The denominator behind the scope note's labeled "
        "share of the frame, carried as a field so the share is recomputable without parsing "
        "the prose. At the **batch's** corpus vintage, not this pack's, so it pairs with "
        "`labeled_cases` and never with `matched_cases`. None where the newest batch recorded "
        "no count, which is the state the note bounds instead of measuring",
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
        "cut's raw row count. A gap is expected once the artifact spans several batches, since "
        "those span corpus vintages; a large one still means labels produced against a "
        "different vintage rather than thin coverage, which is why both counts are here",
    )
    unmeasured_labels: list[QpTopicLabel] = Field(
        default_factory=list,
        description="Buckets whose per-label agreement is unmeasured in v0 — fewer reference "
        "examples than the support floor, where one entry moves the ratio by tens of points. "
        "The headline agreement certifies none of these rows",
    )
    support: list[QpTopicSupport] = Field(
        default_factory=list,
        description="The raw, unweighted rows behind each bucket, with the reference-sourced "
        "share of them — the view a denial-reweighted `est. n=` does not give, and the one a "
        "small bucket's disposition split cannot be read without",
    )
    section: StatPackSection = Field(
        description="The distribution: labeled cases bucketed by primary `qp-topic-v0` label"
    )


class DocketPackApplicationTopics(_Strict):
    """The emergency-application topic distribution, inseparable from how it was labeled.

    The application frame's counterpart to :class:`DocketPackQpTopics`, read from
    the ``qp-topic-v1`` application labels artifact and measured against the
    application reference block rather than the petition one. The two frames are
    read from different inputs — an application carries no questions presented,
    so a labeler reads its caption, court below, pre-decision docket entries and,
    where the store holds it, the application's own text — which is why the two
    cuts are published apart and never pooled into one row.

    The same pairing caveat holds as for the petition cut: ``labeler`` and
    ``agree``/``n`` are the most recent batch's, while the rows in ``section``
    come from every batch. ``docket_only_cases`` is carried because the input
    shape decides how much a label can say: a docket-only row whose caption and
    entries name no subject is ``unclassifiable`` by rule, so that bucket is
    mostly a measure of how thin the docket is rather than of what the
    applications are about.
    """

    labeler: str = Field(
        min_length=1,
        description="Who assigned the most recent batch's labels — the free-form actor string "
        "from the labels artifact. Earlier batches may name a different one",
    )
    batches: int = Field(
        default=1, ge=1, description="Labeling runs the application artifact accrued over"
    )
    reference_rows: int = Field(
        default=0,
        ge=0,
        description="Labeled applications whose published label is the application reference "
        "block's adjudicated one, carried in every batch and so over-represented while the "
        "frame is still accruing",
    )
    frame_rows: int | None = Field(
        default=None,
        ge=1,
        description="Applications in the labeling frame the newest batch was cut from, as that "
        "batch's extract counted them, at the batch's corpus vintage rather than this pack's. "
        "None where the newest batch recorded no count",
    )
    agree: int = Field(
        ge=0,
        description="Reference entries where the labeler matched the application block's "
        "adjudicated label — agreement, not accuracy",
    )
    n: int = Field(ge=0, description="Reference entries compared — the denominator of `agree`")
    floor: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="What a constant labeler scores on the same compared entries",
    )
    uncovered: int = Field(
        default=0, ge=0, description="Reference entries the labeler produced no label for"
    )
    labeled_cases: int = Field(
        default=0, ge=0, description="Applications the labels artifact carries a primary label for"
    )
    matched_cases: int = Field(
        default=0,
        ge=0,
        description="Of those, the ones that joined a row in this section's population — the "
        "cut's raw row count",
    )
    docket_only_cases: int = Field(
        default=0,
        ge=0,
        description="Of the labeled applications, those read from caption, court below and "
        "docket entries alone, with no stored application text",
    )
    unmeasured_labels: list[QpTopicLabel] = Field(
        default_factory=list,
        description="Buckets whose per-label agreement the application block cannot measure — "
        "fewer reference examples than the support floor. The headline agreement certifies "
        "none of these rows",
    )
    support: list[QpTopicSupport] = Field(
        default_factory=list,
        description="The raw rows behind each bucket, with the reference-sourced share of them",
    )
    section: StatPackSection = Field(
        description="The distribution: labeled applications bucketed by primary `qp-topic-v1` label"
    )


class TopicMixShare(_Strict):
    """One topic's share of one stage's labeled cases."""

    label: QpTopicLabel = Field(description="The primary topic label")
    cases: int = Field(
        ge=0,
        description="Labeled cases at this stage under the label, as the stage's own section "
        "counts them (denial-reweighted where that section is)",
    )
    share: float = Field(
        ge=0.0,
        le=1.0,
        description="`cases` over the stage's `cases` — a share of this stage's labeled cases, "
        "never of the docket",
    )
    classified_share: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="`cases` over the stage's cases outside `unclassifiable`; None on "
        "`unclassifiable` itself. A companion to `share`, never a replacement: whether a row "
        "names a subject depends on what the labeler had to read",
    )
    rows: int = Field(ge=0, description="Rows on hand behind `cases`, unweighted")


class TopicMixStage(_Strict):
    """What share of one stage's labeled cases falls under each topic."""

    stage: Literal["cert", "merits", "interim"] = Field(
        description="`cert`: labeled cert-form petitions, whatever their disposition. "
        "`merits`: those of them the Court granted. `interim`: labeled emergency applications"
    )
    vocabulary: Literal["qp-topic-v0", "qp-topic-v1"] = Field(
        description="The labels artifact the stage is read from: the petitions' `qp-topic-v0` "
        "labels, or the applications' `qp-topic-v1` ones. v1 keeps every v0 label and petition "
        "boundary, so the two share one label set"
    )
    cases: int = Field(ge=0, description="The stage's labeled cases, the shares' denominator")
    rows: int = Field(ge=0, description="Rows on hand behind `cases`, unweighted")
    shares: list[TopicMixShare] = Field(
        default_factory=list,
        description="One entry per label the stage holds, `unclassifiable` included, largest "
        "first. The shares sum to 1 up to rounding",
    )
    scope_note: str = Field(
        min_length=1,
        description="The coverage caveat that must travel with any share quoted from this "
        "stage (`docs/qp-topic.md`, *The coverage caveat*)",
    )


class DocketPackTopicMix(_Strict):
    """The share of labeled cases in each topic, stage by stage.

    A summary view over the topic cuts this pack already carries, for a reader
    who asks what the cases are about at each stage of the docket rather than
    how each topic is disposed of. Each stage is read from one labels artifact
    and one section, never pooled across frames, and each carries its own scope
    string, because the stages are labeled from different inputs and covered to
    very different depths.
    """

    stages: list[TopicMixStage] = Field(
        default_factory=list,
        description="The stages a gate-passing labels artifact backs, in docket order: cert, "
        "merits, interim",
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
    application_topics: DocketPackApplicationTopics | None = Field(
        default=None,
        description="The emergency-application topic distribution with its labeler provenance, "
        "present only once a gate-passing application labels artifact exists",
    )
    topic_mix: DocketPackTopicMix | None = Field(
        default=None,
        description="The share of labeled cases in each topic at each stage (cert, merits, "
        "interim), read off the topic cuts above; None when neither labels artifact backs a cut",
    )


class BigCaseRead(_Strict):
    """One predictor's newest prediction on one event, with its stakes read.

    The unit the board is assembled from. It carries the headline forecast
    beside the stakes score deliberately: the two answer different questions —
    `probability` is a forecast that resolves against the docket, while
    `big_case_score` resolves against nothing — and a reader who sees only the
    stakes number is one step from reading it as an odds number.
    """

    predictor_id: str
    run_id: str
    mode: str | None = Field(
        default=None,
        description="The cell's mode (`forward` / `replay`) from its harness-written "
        "`context` block; None on a cell written before that block existed",
    )
    probability: float = Field(
        ge=0.0,
        le=1.0,
        description="The cell's headline forecast, `Prediction.probability`: P(granted) "
        "on a cert/interim event, P(disturbed) on a merits one. Carried so the stakes "
        "score is never read alone as though it were an odds number",
    )
    predicted_disposition: Disposition
    granted: int = Field(ge=0, le=1, description="The cell's binary call on the stage's axis")
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The cell's self-reported confidence, where it gave one",
    )
    big_case_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The cell's stakes read, 0-1, verbatim from the prediction. None where "
        "the cell declared no view — never imputed, and excluded from the case mean rather "
        "than counted as a zero",
    )
    big_case_rationale: str | None = Field(
        default=None,
        description="The cell's one-line rationale for the score, or for the declared null. "
        "The only agent prose the board republishes",
    )
    cell_path: str = Field(
        description="Repo-relative path of the run directory the numbers were read from"
    )
    cell_url: str | None = Field(
        default=None,
        description="`cell_path` under the configured repository URL. None when the command "
        "was run without one, and also when the data root is absolute — a build machine's "
        "filesystem path has no business in a published link",
    )
    leakage_suspected: bool = Field(
        default=False,
        description="Whether any committed grading of this run recorded `leakage_suspected`. "
        "It matters more here than on a scored board: a stakes read is partly a read of the "
        "disposition, so a cell that saw its own outcome may have read the stakes off it — and "
        "here that cell is not one point inside a coefficient, it is the published number",
    )


class BigCaseEvent(_Strict):
    """One event of a case, with every predictor's newest read of it.

    Present for every event carrying at least one prediction, whether or not it
    is the case's current moment — an earlier moment is history a reader can see,
    not a number the row's mean counts. A distinct collapse from the row's, and
    the two are never differenced: this one is newest-run-per-predictor **on this
    event**, and it is where a predictor lagging the case's moment keeps its read.
    """

    event_id: str
    title: str | None = Field(
        default=None,
        description="The event's `event.yaml` title, None where the ledger carries "
        "predictions under an event whose definition is absent",
    )
    actual_disposition: Disposition | None = Field(
        default=None, description="The realized disposition, present iff the event has resolved"
    )
    resolved_at: date | None = Field(
        default=None, description="When the event resolved; None while it is pending"
    )
    reads: list[BigCaseRead] = Field(
        default_factory=list,
        description="Each predictor's newest prediction on this event, ordered by predictor id",
    )


#: Why a big-case board row carries no asking side: one value per branch of the
#: rule in :mod:`fedcourtsai.asking_party`.
AskingDeclineReason = Literal[
    "no_caption",
    "not_scotus",
    "in_re",
    "not_two_sided",
    "docket_labels",
    "short_form",
    "original_jurisdiction",
    "cross_petition",
    "stage",
]


class BigCaseOutcomeLine(_Strict):
    """What one action open at a row's moment does for the named sides."""

    action: Literal["granted", "denied", "reversed", "affirmed", "vacated"] = Field(
        description="The action, spelled as the outcome vocabulary spells it — `granted` / "
        "`denied` for a petition or an application, `reversed` / `affirmed` / `vacated` for "
        "a merits case. Pair a line with the forecast by `side`, not by `action`: a merits "
        "forecast has no per-action label"
    )
    side: Literal["granted", "not-granted", "disturbed", "undisturbed"] = Field(
        description="The side of the stage's forecast binary the action falls on. For a "
        "petition or an application, `granted` pairs with the headline probability and "
        "`not-granted` with its complement. For a merits case the headline is "
        "P(judgment below disturbed), which pools reversal, vacatur and the mixed in-part "
        "outcome: `reversed` and `vacated` are both `disturbed` and pair with it together, "
        "`affirmed` is `undisturbed` and pairs with its complement — never one line to the "
        "whole number"
    )
    line: str = Field(
        description="One fixed plain-language sentence saying what the action does for the "
        "sides, by name. Consequences only, never likelihood"
    )


class BigCaseCurrentRead(_Strict):
    """A predictor's current read of a case, and where it came from.

    The collapse the mean is taken over: one read per predictor, from that
    predictor's newest run on the **case's current moment** (`BigCaseRow.moment`)
    — never carried over from an older moment, which is history under its own
    event. The event and run travel with the number anyway, because a case can be
    read at several moments and "which moment is this" is not recoverable from
    the score; on a published row the event is always the row's `moment`.
    """

    predictor_id: str
    event_id: str
    run_id: str
    process_window: str | None = Field(
        default=None,
        description="The label of the counting window this read's run sits in, on a frozen "
        "build; null on the all-versions census. The row's mean pools predictors, so it can "
        "pool reads from different windows — each read names its own rather than the row "
        "naming one",
    )
    big_case_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="The current read, or None where the newest run declared no view — in "
        "which case the predictor is absent from `n` and from the mean",
    )
    big_case_rationale: str | None = Field(
        default=None,
        description="The rationale the current read carried. A null score *with* a rationale is "
        "a declared no view; a null score *without* one predates the prompt amendment that made "
        "the field required, and pools 'weighed the stakes and could not place them' with 'never "
        "engaged the question' (`docs/freeze-record.md`)",
    )
    leakage_suspected: bool = Field(
        default=False,
        description="Whether any committed grading of this run recorded `leakage_suspected`",
    )


# `BigCaseScheduled` names a field `date`, which would shadow the type inside its
# own class body; its annotation spells the type through this alias instead.
_Day = date


class BigCaseScheduled(_Strict):
    """A date ahead that the Court has set for a case, as the committed schedule carries it."""

    kind: Literal["conference", "argument", "response_due"] = Field(
        description="What is scheduled: `conference`, the conference the docket is "
        "distributed for; `argument`, the day a granted case is set for argument; "
        "`response_due`, the deadline for a response to the petition or application"
    )
    date: _Day = Field(
        description="The scheduled day, on or after the day the schedule was last built. A "
        "reader rendering later drops a date that has since passed rather than show it "
        "as upcoming"
    )


class BigCaseRow(_Strict):
    """One case on the board: the panel's current stakes reads and their mean.

    One **moment** per row, and every read on it: the case is collapsed to the
    newest moment its docket has reached (`moment`), and each predictor's read is
    its newest run on that moment. A predictor with no run there is absent from
    the row rather than pooled into it from an older moment, so the reads the
    mean is taken over are answers to the same question — at the cost of a
    smaller `n` where a fresh moment has been minted for only some of the panel.
    """

    case_id: str
    court_id: str
    docket_id: int
    moment: str | None = Field(
        default=None,
        description="The event id of the case's current moment — the moment every read on "
        "this row sits on. Chosen from the docket rather than from run times: the newest "
        "predicted event by `opened_at`, ties broken by the stage progression then by event "
        "id, so a re-predict of an older moment cannot move it. None only on a row written "
        "before the field existed",
    )
    moment_opened_at: date | None = Field(
        default=None,
        description="`moment`'s `opened_at` — the docket date the row was collapsed on, "
        "which is the *event's* date and not always the day the moment it declares "
        "arrived: on a cert petition baseline it is docketing, while the moment is the "
        "distribution (`docs/freeze-record.md`). None where the event definition records "
        "no date, and None where the ledger carries no definition for that event at all "
        "(as `caption` then is); in either case the moment was ordered by the day of its "
        "first prediction's harness clock instead",
    )
    caption: str | None = Field(
        default=None,
        description="The case's display name: the `event.yaml` title of `moment`. `case_id` "
        "is the identifier; the caption and, where committed data carries one, "
        "`docket_number` are the human handles",
    )
    caption_event_id: str | None = Field(
        default=None,
        description="The event the caption was read from — `moment`, repeated here so the "
        "rule is checkable against the row without a join",
    )
    short_caption: str | None = Field(
        default=None,
        description='The conventional short form of `caption` ("Trump v. California"), '
        "derived deterministically by the `short_caption_rule` provenance string. None where "
        "the rule cannot produce a confident one — a reader falls back to `caption`. "
        "Display-only: nothing predicts, evaluates or scores on it",
    )
    docket_number: str | None = Field(
        default=None,
        description='The Court\'s own docket number ("26-239", "26A124"), read from '
        "committed data by the `docket_rule` provenance string; None where no committed "
        "source carries it. Display-only",
    )
    docket_number_source: Literal["case_id", "qp-topics"] | None = Field(
        default=None,
        description="Where `docket_number` came from, so the rule is checkable against the "
        "row: `case_id` (a live-first reserved-range id, which packs the docket number "
        "losslessly) or `qp-topics` (the committed labels artifact's docket number for the "
        "case). None exactly when `docket_number` is",
    )
    docket_url: str | None = Field(
        default=None,
        description="The Court's supremecourt.gov docket page for `docket_number`; None "
        "where there is no docket number or it is not a Term-form or application number",
    )
    asking_party: str | None = Field(
        default=None,
        description="The short name of the side asking the Court to act at `moment` — the "
        "petitioner, applicant, appellant, plaintiff or movant, named first in the "
        "caption — by the `asking_rule` "
        "provenance string, with the short-caption rule's party names. None exactly when "
        "`asking_declined` is set. Display-only",
    )
    other_party: str | None = Field(
        default=None,
        description="The short name of the other side, named second in the caption. None "
        "exactly when `asking_party` is. Display-only",
    )
    outcome_lines: list[BigCaseOutcomeLine] | None = Field(
        default=None,
        description="One fixed plain-language line per action open at `moment`'s stage, "
        "filled with `asking_party` and `other_party`: granted and denied for a petition or "
        "an application, reversed, affirmed and vacated for a merits case. Consequences "
        "only, never likelihood — shown beside the forecast, paired by each line's `side`, "
        "so a reader can tell whom each action helps. None exactly when `asking_party` is. "
        "Display-only",
    )
    asking_declined: AskingDeclineReason | None = Field(
        default=None,
        description="Why the row carries no asking side, one value per branch of the "
        "`asking_rule` provenance string (`no_caption`, `not_scotus`, `in_re`, "
        "`not_two_sided`, `docket_labels`, `short_form`, `original_jurisdiction`, "
        "`cross_petition`, `stage`); None exactly when `asking_party` is set",
    )
    scheduled: BigCaseScheduled | None = Field(
        default=None,
        description="The case's next scheduled date, joined from the committed "
        "`data/schedule/schedule.json` by the `schedule_rule` provenance string; None where "
        "the schedule carries no upcoming conference for the case. Always the `conference` "
        "entry of `schedule`, kept for `1.3` readers. Carries no `as_of`, so the board moves "
        "only when a case's date does. Display-only",
    )
    schedule: list[BigCaseScheduled] = Field(
        default_factory=list,
        description="Every upcoming date the committed schedule carries for the case — its "
        "conference, its argument day, its response deadline — earliest first, joined by "
        "the `schedule_rule` provenance string. Empty where none is ahead. Display-only",
    )
    status: Literal["pending", "partly_resolved", "resolved"] = Field(
        description="Resolution state across **all** the case's predicted events, derived "
        "from `outcome.json` presence: none resolved, some resolved, all resolved. The one "
        "case-grain figure on an otherwise moment-scoped row — a case can read `resolved` "
        "on an earlier event while `moment` is still pending, so it is never read as the "
        "moment's own state"
    )
    mean_big_case_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Mean of the current reads that carry a score, rounded to four places. "
        "A panel opinion about stakes, never a measurement and never a skill figure",
    )
    n: int = Field(
        ge=1,
        description="How many predictors the mean is over. Always beside the mean: with "
        "three predictors on the roster a mean over one is a single model's opinion",
    )
    score_min: float = Field(
        ge=0.0, le=1.0, description="Lowest current read on the case's current moment"
    )
    score_max: float = Field(
        ge=0.0, le=1.0, description="Highest current read on the case's current moment"
    )
    score_range: float = Field(
        ge=0.0,
        le=1.0,
        description="`score_max - score_min`, rounded to four places: panel disagreement, "
        "shown rather than hidden inside the mean",
    )
    leakage_suspected: bool = Field(
        default=False,
        description="Whether any of the case's current reads is leakage-flagged. Where it is "
        "true the mean rests partly on a cell that may have read the stakes off an outcome it "
        "should not have seen, and the row is not evidence about the case's stakes",
    )
    current_reads: list[BigCaseCurrentRead] = Field(
        default_factory=list,
        description="Every predictor with a run on the case's current moment, ordered by "
        "predictor id — including one whose newest run there carries no score, which the "
        "mean excludes. A predictor that read only an earlier moment is absent: its read is "
        "history, under that event in `events`",
    )
    events: list[BigCaseEvent] = Field(
        default_factory=list,
        description="The case's predicted events, ordered by event id, each with every "
        "predictor's newest read of it",
    )

    @model_validator(mode="after")
    def _docket_fields_travel_together(self) -> BigCaseRow:
        """A docket number names its source, and a docket link has a number behind it."""
        if (self.docket_number is None) != (self.docket_number_source is None):
            raise ValueError("docket_number_source is set exactly when docket_number is")
        if self.docket_url is not None and self.docket_number is None:
            raise ValueError("docket_url requires a docket_number")
        return self

    @model_validator(mode="after")
    def _asking_fields_travel_together(self) -> BigCaseRow:
        """The asking side, the other side and the lines are all set, or a decline says why."""
        present = [
            self.asking_party is not None,
            self.other_party is not None,
            self.outcome_lines is not None,
        ]
        if any(present) and not all(present):
            raise ValueError("asking_party, other_party and outcome_lines are set together")
        if all(present) == (self.asking_declined is not None):
            raise ValueError("asking_declined is set exactly when asking_party is not")
        return self

    @model_validator(mode="after")
    def _scheduled_is_the_conference(self) -> BigCaseRow:
        """`scheduled` keeps its `1.3` meaning: the conference entry, when there is one."""
        if self.scheduled is not None and self.scheduled.kind != "conference":
            raise ValueError("scheduled carries the conference only; see schedule")
        if self.schedule != sorted(self.schedule, key=lambda day: (day.date, day.kind)):
            raise ValueError("schedule is ordered earliest first")
        if self.scheduled is not None and self.schedule and self.scheduled not in self.schedule:
            raise ValueError("scheduled is the conference entry of schedule")
        return self


class BigCaseCoverage(_Strict):
    """How many cases the board ranks on `n` reads — the denominator distribution."""

    n: int = Field(ge=0, description="Number of scoring predictors")
    cases: int = Field(ge=0, description="Cases whose mean is over that many reads")


class BigCaseProvenance(_Strict):
    """The board's reading rules, carried inside the artifact.

    Registered prose rather than a free-text note: the board is published to a
    public site, where the figure travels without the document that explains it,
    so the caveats travel inside the artifact instead.
    """

    reading_rule: str
    collapse_rule: str
    leakage_note: str = Field(
        description="Why a leakage-flagged read is worse here than on a scored board, and "
        "what the row-level mark means"
    )
    leaderboard_divergence: str = Field(
        description="The three collapses of a case these artifacts take — the leaderboard's "
        "`big_case` mean over a case's moments, this board's row, and this board's per-event "
        "history — and that no figure from one is differenced against a figure from another. "
        "The key keeps its name because it is published: renaming it breaks a reader"
    )
    population: str
    version_scope: str = Field(
        description="What `process_scope` covers on **this** build, and what the other "
        "scope would cost: version-blind by default, with the `frozen` comparison build's "
        "selected hold-out stated rather than left to be inferred. Scope-aware prose — a "
        "build states its own population, never both"
    )
    rank_resolution: str = Field(
        description="What the `#` column may be read as, given how close adjacent means are "
        "against the spread inside a single row's own panel"
    )
    no_time_series: str
    caption_rule: str
    short_caption_rule: str = Field(
        description="How `short_caption` is derived from `caption`, and when it is null"
    )
    docket_rule: str = Field(
        description="Where `docket_number` is read from, in precedence order, what "
        "`docket_url` links to, and why a row can carry neither"
    )
    asking_rule: str = Field(
        description="How `asking_party`, `other_party` and `outcome_lines` are derived, "
        "where each `asking_declined` value comes from, and what the lines cannot see"
    )
    schedule_rule: str | None = Field(
        default=None,
        description="Where `schedule` and `scheduled` come from and when each is empty or null",
    )
    process_label: str = Field(
        description="The process label in force when the board was built — what a "
        "prediction minted today stamps, not a scope filter on the rows (see `version_scope`)"
    )


class BigCaseBoard(_Strict):
    """``metrics/big-cases.json`` — the case-centric big-case board.

    One row per predicted case, carrying each predictor's current stakes read
    (`Prediction.big_case_score`) and the mean across the predictors that gave
    one, ranked mean-first. It answers "which cases does the panel think matter,
    and where do the models disagree" — a question none of the existing
    big-case surfaces answers, because each of those measures something *about
    the models* rather than listing the cases.

    **It is not a performance surface, and its numbers are never ranked as
    skill.** A stakes read is neither scored nor ranked: it resolves against
    nothing, so no accuracy, calibration or ordering claim can be made from any
    *stakes* figure here. The per-cell ``probability`` carried beside it is a
    forecast — the cell's raw value, unstratified, unexcluded and unscored — and
    it is not a claimable one either; scored forecast performance lives on the
    leaderboard and nowhere else. The same carve-out is why the board reads the
    committed ledger directly, applying neither the forward-claim exclusion nor
    the leakage exclusion and reading ungraded cells besides — a wider population
    than the scored boards, deliberately, and a caveat that has to travel with a
    quoted number. How wide depends on ``process_scope``, which the artifact
    states on itself: ``all``, the default, adds every process version, while the
    ``frozen`` comparison build narrows current reads to the blessed partition
    and publishes what that hold-out costs. Where the leakage bit is set
    on a read, the row carries the mark: a stakes read is partly a read of the
    disposition, so a contaminated cell is not one point inside a coefficient
    here, it is the number.

    A pure function of the committed `data/` ledger — no corpus, no credentials,
    no clock — so reruns over an unchanged ledger reproduce both files byte for
    byte. That is also why it carries no timestamp and no commit hash: the
    artifact's vintage is the commit that wrote it.
    """

    schema_version: Literal["1.3", "1.4"] = Field(
        default="1.4",
        description="The artifact's schema version. A reader keys on it: a `1.1` row "
        "carries the display fields `short_caption`, `docket_number`, "
        "`docket_number_source` and `docket_url`, a `1.2` row adds `asking_party`, "
        "`other_party`, `outcome_lines` and `asking_declined`, a `1.3` row adds "
        "`scheduled`, and a `1.4` row adds `schedule`",
    )
    process_scope: Literal["frozen", "all"] = Field(
        default="all",
        description="Which process versions a **current read** may come from: `all` (the "
        "default — every committed run, shakedown, pre-freeze and unstamped included, "
        "which is what a census means) or `frozen` (the comparison build: only runs whose "
        "harness stamp is in the blessed digest set and was written at or after the freeze "
        "instant, the predicate the performance boards scope on). Never a filter on "
        "`events`, which carries the case's whole history either way: an out-of-scope run "
        "is relegated to history, not hidden. The `frozen` build is **not this board with "
        "fewer rows** — its hold-out is selected, not sampled (`cases_out_of_scope`, and "
        "the `population` provenance string) — so no count, mean, rate or spread statistic "
        "is differenced across a scope change. A `frozen` board with no rows is the honest "
        "'no frozen-process stakes reads yet' state and says nothing about the ledger, "
        "which may hold plenty",
    )
    frozen_process: FrozenProcessRecord | None = Field(
        default=None,
        description="The freeze constants in force at build time, recorded on every build "
        "(an `all`-scope one included) so `process_scope` is answerable from the artifact "
        "alone rather than by resolving the build commit back to the source",
    )
    cases: int = Field(default=0, ge=0, description="Rows on the board")
    cases_without_score: int = Field(
        default=0,
        ge=0,
        description="Cases the ledger holds **in-scope** predictions for whose every current "
        "read carries no score, and which are therefore off the board — a panel that "
        "declined. Published so `cases` is read against the predicted population rather "
        "than as the whole of it",
    )
    cases_out_of_scope: int = Field(
        default=0,
        ge=0,
        description="Cases held off the board because no run of theirs is in "
        "`process_scope` — zero on an `all` build. Kept apart from "
        "`cases_without_score` because the two are different facts: that one is a panel "
        "that declined to score, this one is a panel this build refused to read. The test "
        "is **ordered**: where both would hold, out of scope wins, since a case with no "
        "in-scope run cannot be observed to have declined — so a filtered build's "
        "`cases_without_score` counts in-scope decliners alone and is not comparable to the "
        "`all` build's. The held-out set is selected rather than sampled (a resolved case "
        "is never re-predicted, so one whose reads predate the freeze can never be refilled "
        "into scope; and the re-predict rule re-owes no cert arrival, sg-brief or relist "
        "moment and no merits moment), so it is never read as a random thinning",
    )
    predictors: list[str] = Field(
        default_factory=list,
        description="Predictor ids with at least one **in-scope** run, sorted — the roster "
        "the per-case columns are drawn from, read off the cells rather than off config and "
        "therefore scope-dependent: a predictor whose every run falls outside "
        "`process_scope` is absent rather than rendering as a column of blanks",
    )
    current_reads: int = Field(
        default=0,
        ge=0,
        description="Current reads on the board — one per (case, predictor) — scored or not. "
        "The denominator the three counts below partition",
    )
    scored_reads: int = Field(
        default=0,
        ge=0,
        description="Current reads carrying a score; the means are taken over these",
    )
    declared_no_view: int = Field(
        default=0,
        ge=0,
        description="Unscored current reads that carry a rationale — a cell that weighed the "
        "stakes and said it could not place them. Only observable from the prompt amendment "
        "that made the field required with an explicit null escape onward",
    )
    missing_reads: int = Field(
        default=0,
        ge=0,
        description="Unscored current reads with no rationale — a missing-data figure, and "
        "never a declaration. Mostly elicited under the earlier prompt, where the field was "
        "optional and an absent value pooled 'could not place the stakes' with 'never "
        "engaged the question' (`docs/freeze-record.md`); a post-amendment cell that simply "
        "omitted the rationale lands here too and **this count does not separate the two**. "
        "On a `frozen` build the first cause cannot arise, since every current read there "
        "post-dates the amendment",
    )
    rows_with_leakage_flag: int = Field(
        default=0,
        ge=0,
        description="Rows whose mean rests partly on a leakage-flagged read. Not netted against "
        "anything: it is an audit line about the board's own contents",
    )
    median_adjacent_gap: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Median difference in mean between neighbouring rows. Beside "
        "`median_score_range` it is what says whether the `#` column can be read as an ordering; "
        "None with fewer than two rows",
    )
    median_score_range: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Median `score_range` across the rows — how far a row's own panel typically "
        "spreads, against which the gap between two ranks should be read; None with no rows",
    )
    coverage: list[BigCaseCoverage] = Field(
        default_factory=list, description="Cases by number of scoring predictors, `n` descending"
    )
    rows: list[BigCaseRow] = Field(
        default_factory=list,
        description="The board, mean descending, then `n` descending, then `case_id`",
    )
    provenance: BigCaseProvenance | None = Field(
        default=None, description="The reading rules that travel with the figures"
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


class ReserveOccupant(_Strict):
    """One latched, still-pending application the interim reserve weighed.

    ``holds_slot`` is False when the application's newest stored snapshot
    already reads as an interim disposal
    (:func:`fedcourtsai.pipeline.outcome.interim_disposal_signal`), or when it
    was filed more than ``interim_reserve_age_out_days`` before the pass
    (``aged_out``): the row is still unresolved in the corpus, but the pass no
    longer counts it against ``interim_reserve_slots``. ``date_filed`` and
    ``age_days`` date the occupancy, so a slot held for months is visible in
    the ledger.
    """

    case_id: str
    docket_number: str = ""
    date_filed: date | None = None
    snapshot_date: date | None = Field(
        default=None, description="The newest stored snapshot read; None when none is stored"
    )
    age_days: int | None = Field(
        default=None,
        description=(
            "Days from date_filed to the selection pass's date; None when the "
            "filing date is unknown"
        ),
    )
    aged_out: bool = Field(
        default=False,
        description=(
            "True when age_days exceeds the reserve's age-out horizon, which frees "
            "the slot while the row stays latched"
        ),
    )
    holds_slot: bool = Field(
        default=True,
        description=(
            "False when the stored snapshot already reads as an interim disposal, "
            "or the occupant has aged out, which frees the slot while the row "
            "awaits a resolver"
        ),
    )
    snapshot_read_failed: bool = Field(
        default=False,
        description=(
            "True when the snapshot read raised, as distinct from no snapshot being "
            "stored; the occupant then holds its slot"
        ),
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
    reserve_occupants: list[ReserveOccupant] = Field(
        default_factory=list,
        description=(
            "Every latched, still-pending application the interim reserve weighed, "
            "with whether it still holds a slot"
        ),
    )


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


class CountedConferenceCell(_Strict):
    """One counted cell in the conference cut: the conference as at its cut."""

    predictor_id: str = Field(description="The predictor whose staged cell this is")
    run_id: str = Field(description="The staged run: the newest run, the one graded")
    process_digest: str | None = Field(description="The frozen process digest it was stamped under")
    bound: date | None = Field(
        description="The exclusive day bound of what the provisioned snapshot could show: "
        "the moment's `cutoff` where provisioning fixed one, else the day after "
        "`snapshot_date`. Null where the prediction carries no context"
    )
    band: str | None = Field(description="The salience band frozen on the cell's context")
    salience_version: str | None = Field(description="The scorer version that assigned `band`")
    conference: date | None = Field(
        description="The conference the petition was distributed for as at `bound` — the "
        "last DISTRIBUTED entry filed strictly before it — or, where "
        "`conference_source` is 'current', the corpus column as it stands now. Null "
        "where neither shows a distribution"
    )
    conference_source: Literal["asof", "current"] = Field(
        description="'asof' when reconstructed from the case's latest live payload at "
        "`bound`; 'current' when that could not be done — no live payload was "
        "readable, or the cell carries no context to bound it — and the current "
        "`distributed_for_conference` column stands in. The current column moves on "
        "relist and reschedule, so a 'current' value may postdate the cell"
    )


class CountedConferenceEvent(_Strict):
    """One counted event: its conference at the cut, band, predictors and resolution."""

    case_id: str
    docket_number: str | None = Field(description="From the corpus; null if absent")
    event_id: str
    caption: str | None = Field(description="The event's title")
    stage: str | None = Field(description="The normalized decision stage")
    moment: str | None = Field(description="The normalized forecast moment")
    conference: str = Field(
        description="The grouping key: the ISO conference date every counted cell was "
        "cut at; 'mixed' where the cells disagree (one provisioned before a relist, "
        "another after); 'none' where no cell shows a distribution"
    )
    current_conference: date | None = Field(
        description="The corpus `distributed_for_conference` as it stands now, for "
        "comparison: it moves on relist, which is why it is not the grouping key"
    )
    payload_date: date | None = Field(
        description="The date of the live payload both conferences were reconstructed "
        "from. A reconstruction can see no entry filed after it, so a payload older "
        "than a bound is a per-case freshness limit the corpus-wide vintage hides"
    )
    band: str | None = Field(
        description="The band every counted cell froze; null where they differ"
    )
    bands: list[str] = Field(description="Every distinct band the counted cells froze")
    predictors: list[str] = Field(
        description="Predictors with a counted cell: the run a counted grading names, "
        "else the staged (newest resolvable) run when it is its predictor's counted "
        "forecast of the event. Empty only on "
        "a registered event with no counted cell"
    )
    scored_predictors: list[str] = Field(
        description="The subset with at least one counted grading, from the same "
        "`stratify` pass the leaderboard aggregates"
    )
    reowed: bool = Field(
        description="Whether a de-counted or unstamped cell predates the earliest counted "
        "cell: a re-forecast of an earlier round's event rather than one the frozen "
        "process forecast first. Not the registered-membership test; `registered` is"
    )
    registered: bool | None = Field(
        description="The registered rule's membership as at `registered_at`, "
        "reconstructed: a re-predict moment, a de-counted cell whose harness clock falls "
        "on or before that day, no outcome before it, and — at the distribution "
        "moment — `conference_at_registration` on or after it. Null without "
        "`--registered-at`. Fixed at registration, so a later reschedule never "
        "removes an event"
    )
    conference_at_registration: date | None = Field(
        description="The conference the petition was distributed for as at "
        "`registered_at` (entries filed strictly before it); null without "
        "`--registered-at` or where none was shown"
    )
    resolved: bool = Field(description="Whether the event has a committed outcome")
    resolved_at: date | None = Field(description="The outcome's resolution date")
    actual_disposition: str | None = Field(description="The outcome's disposition")
    status: Literal["scored", "resolved_unscored", "pending", "unforecast"] = Field(
        description="'unforecast' when the event has no counted cell at all — a "
        "registered event no engine produced a counted forecast for, attrition rather "
        "than a forecast; otherwise 'scored' when resolved and every counted predictor "
        "has a counted grading, 'resolved_unscored' when resolved with a grading not "
        "yet landed or excluded, and 'pending' with no committed outcome"
    )
    cells: list[CountedConferenceCell] = Field(description="The counted cells, by predictor")


class CountedConferenceTotal(_Strict):
    """Events in one (registered, conference, stage, moment, band) cell of the cut."""

    registered: bool | None = Field(description="As on the events")
    conference: str = Field(description="The grouping key, as on the events")
    stage: str | None
    moment: str | None
    band: str | None = Field(description="Null groups the events whose cells froze no single band")
    events: int = Field(ge=0, description="scored + resolved_unscored + pending + unforecast")
    scored: int = Field(ge=0)
    resolved_unscored: int = Field(ge=0)
    pending: int = Field(ge=0)
    unforecast: int = Field(ge=0)


class CountedConferenceCut(_Strict):
    """``conference-set --counted`` result: the counted events by conference at their cut.

    The frozen-scope counted population joined to the conference each counted
    cell's provisioned snapshot showed and, with ``--registered-at``, the
    registered rule's reconstructed membership. Read against the corpus vintage
    it names, since both reconstructions read the corpus's latest live payloads.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    corpus: ExportCorpusVintage = Field(
        description="The blob's freshness, as `corpus-info` reads it"
    )
    corpus_sha256: str = Field(description="sha256 of the corpus database the cut ran over")
    registered_at: date | None = Field(
        description="The registration day `registered` is reconstructed at; null without "
        "`--registered-at`"
    )
    conference_fallbacks: int = Field(
        ge=0,
        description="Conference readings that fell back to the current column, cells and "
        "registration readings together — every event's registration reading counts, "
        "whatever its moment, so the count is strict. Nonzero means the cut's "
        "conferences are not all reconstructions and no figure is quoted from it",
    )
    events: list[CountedConferenceEvent] = Field(default_factory=list)
    totals: list[CountedConferenceTotal] = Field(default_factory=list)


class PartySideCell(_Strict):
    """How many frame rows put a sovereign class on which side of the caption."""

    side: Literal["both", "petitioner", "respondent", "none"] = Field(
        description="Which side(s) of the caption the class occupies"
    )
    n: int = Field(ge=0, description="Live-slice rows in the cell")


class PartyAdministrationCell(_Strict):
    """One federal-party x administration x stratum cell of the party census.

    ``administration`` is null where the row's ``as_of`` date is missing or
    predates the committed calendar — reported as its own cell rather than
    folded into an administration, because "we cannot say" is a different fact
    from any president's count. The ``stratum`` key is not optional detail: the
    windows hold different mixes of paid cert, IFP cert and applications, and
    the class rates differ between them, so a cell is comparable across windows
    only against its own stratum's denominator.
    """

    federal_party: Literal["both", "petitioner", "respondent"] = Field(
        description="Which side(s) the federal government occupies"
    )
    administration: str | None = Field(
        default=None, description="Administration label (e.g. trump-47), or null where unattributed"
    )
    stratum: Literal["paid-cert", "ifp-cert", "application", "other"] = Field(
        description="Docket stratum the cell is keyed on"
    )
    n: int = Field(ge=0, description="Live-slice docket rows in the cell — rows, not disputes")


class PartyFrameCell(_Strict):
    """One administration x stratum slice of the frame: the denominator, and its gap.

    A federal-party count is uninterpretable without its matching cell here. The
    live slice's coverage is uneven across the windows in two ways that a raw
    count silently mixes: the windows differ in *size* (the newest is truncated
    by today, the oldest by the slice's own start), and they differ in
    *composition* — the live channel's coverage of the IFP and application
    streams grew over the slice's span, and the excluded sampled block is
    entirely IFP, so the earlier windows lose IFP mass the newest one keeps.
    Dividing by window size corrects only the first. A share is therefore
    comparable across windows **within a stratum** and not otherwise; the
    paid-cert stratum is the one captured whole in every window and is the
    natural cut for a cross-administration reading.
    """

    administration: str | None = Field(
        default=None, description="Administration label, or null where unattributed"
    )
    stratum: Literal["paid-cert", "ifp-cert", "application", "other"] = Field(
        description="Docket stratum the cell is keyed on"
    )
    rows: int = Field(ge=0, description="Frame rows in this administration x stratum cell")
    sampled_excluded: int = Field(
        ge=0, description="Sampled-block rows in the same cell, outside the frame"
    )


class PartyPresidentCell(_Strict):
    """How often a president's surname names a party, by side.

    A **name** match on the caption, not an identification of the person: the
    caption cannot distinguish a president from a private litigant of the same
    surname, so this is a screening count and is never read as an
    official-capacity class (which the federal-party fields carry). It fires on
    both capacities — an official-capacity caption names the president too — so
    the personal-capacity family is this flag together with `federal_party`
    `none`, not this flag alone. Two undercounts ride in it: only the leading
    name segment of each caption half is tested, and only the first matching
    side is reported, so a president named second on a side, or on the
    respondent side of a caption whose petitioner already matched, never
    appears here.
    """

    president: str = Field(description="The calendar president's surname the caption matched")
    side: Literal["petitioner", "respondent"] = Field(description="Which side carried the name")
    n: int = Field(ge=0, description="Live-slice docket rows in the cell — rows, not disputes")


class PartyCensus(_Strict):
    """``party-census`` result: the live-slice party annotation counts.

    Counts only, under one annotation rule and one date convention — both
    stamped, because a cell is comparable to another only where the pair
    agrees. Grant rates by government-party status are `party-rates`
    (`PartyRates`), which carries its own population rules and denial
    reweighting, not a field here.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    rule_version: str = Field(description="The committed annotation rule, e.g. party-v1")
    caption_rule_version: str = Field(
        default="",
        description="The caption rule the annotation rule composes over both "
        "halves (e.g. caption-v2) — stamped so the artifact says which class "
        "predicate produced its cells rather than leaving the pairing to be "
        "recovered from the source",
    )
    as_of_field: str = Field(
        description="Which date drove the administration attribution: filed | resolved"
    )
    corpus_sha256: str = Field(
        default="",
        description="sha256 of the corpus database the census ran over — the "
        "artifact is re-derivable only against this exact corpus state",
    )
    latest_pull: date | None = Field(
        default=None, description="Corpus vintage: newest `last_pulled` across the blob"
    )
    latest_snapshot: date | None = Field(
        default=None, description="Corpus vintage: newest stored snapshot date across the blob"
    )
    rows: int = Field(
        default=0,
        ge=0,
        description="Unweighted live-slice SCOTUS rows annotated (the frame)",
    )
    sampled_excluded: int = Field(
        default=0,
        ge=0,
        description="Live-slice rows carrying a sampling weight (the legacy "
        "one-in-ten denial block) — outside the frame, counted here so the "
        "coverage gap is visible rather than silently mixed in at a tenth of "
        "its true stratum size",
    )
    single_party: int = Field(
        default=0,
        ge=0,
        description="Of those, captions with no ` v. ` half — In re / Ex parte, "
        "plus the rare caption whose separator is malformed — annotated from one "
        "party, so no respondent class exists to count",
    )
    undated: int = Field(
        default=0,
        ge=0,
        description="Of those, rows carrying no date under `as_of_field` — their "
        "administration is null by construction, never imputed",
    )
    pending: int = Field(
        default=0,
        ge=0,
        description="Of those, rows carrying no disposition yet. A pending "
        "petition ordinarily carries no resolution date either, so under the "
        "`resolved` convention this sizes the newest window's "
        "**right-censoring**: that window's count is a floor, not a total. The "
        "two counters are kept separate rather than assumed equal — where a "
        "dated row carries no label, `undated` and `pending` part company and "
        "say so. Under `filed` these rows sit in their filing window with their "
        "outcomes unobserved.",
    )
    frame_by_administration: list[PartyFrameCell] = Field(
        default_factory=list,
        description="The per-administration, per-stratum denominator every federal "
        "cell is read against",
    )
    federal_party: list[PartySideCell] = Field(default_factory=list)
    state_party: list[PartySideCell] = Field(default_factory=list)
    federal_by_administration: list[PartyAdministrationCell] = Field(
        default_factory=list, description="Non-empty cells only; zero cells are omitted, not zeroed"
    )
    named_president: list[PartyPresidentCell] = Field(default_factory=list)


class PartyRateCell(_Strict):
    """One administration x stratum x federal-side cell of the party rates cut.

    Every share here is published beside its numerator and denominator, raw and
    weighted: ``granted``/``resolved`` count docket rows once each, and
    ``weighted_granted``/``weighted_resolved`` count each row ``sample_weight``
    times, which is what restores the legacy one-in-ten sampled denial block to
    full strength. ``grant_rate`` is the weighted pair's quotient; where the cell
    holds no sampled row the two pairs are equal and so is the rate. On the
    application stratum the population is the **substantive** asks only — the
    extension, unreadable-ask and never-parsed rows are counted beside the cell,
    never inside its rate.
    """

    administration: str | None = Field(
        default=None,
        description="Administration label (e.g. trump-47), or null where the row "
        "carries no date under the cut's convention",
    )
    stratum: Literal["paid-cert", "ifp-cert", "application"] = Field(
        description="Docket stratum the cell is keyed on"
    )
    federal_party: Literal["both", "petitioner", "respondent", "none"] = Field(
        description="Which side(s) of the caption the federal government occupies; "
        "`none` is the comparison cell — no federal party the caption names"
    )
    sg_counsel: Literal["both", "petitioner", "respondent", "none", "unknown"] | None = Field(
        default=None,
        description="Which side(s) the Solicitor General's office is counsel for under "
        "the cut's `counsel_rule_version`, read from the petitioner and respondent "
        "counsel entries only; `unknown` = the row carries no petitioner or respondent "
        "entry at all (nearly every resolved IFP row, in the index today) or a roster name on "
        "it cannot be dated. Null "
        "when the cut was taken without a counsel rule",
    )
    rows: int = Field(ge=0, description="Docket rows in the cell's population")
    sampled_rows: int = Field(
        default=0,
        ge=0,
        description="Of those, rows from the legacy sampled denial block (weight > 1)",
    )
    pending: int = Field(
        default=0,
        ge=0,
        description="Of those, rows with no disposition as of the cut's `through` "
        "date (or, without one, in the blob at its vintage) — outside the rate, "
        "so a window with many is censored",
    )
    unreadable: int = Field(
        default=0,
        ge=0,
        description="Of those, rows whose disposition is `other` (decided, label "
        "unreadable) — outside the rate rather than read as a denial",
    )
    resolved: int = Field(
        default=0, ge=0, description="Rows with a machine-readable disposition (raw)"
    )
    granted: int = Field(
        default=0,
        ge=0,
        description="Of those, rows on the granted side of the binary outcome "
        "(`granted_labels`), raw",
    )
    weighted_resolved: int = Field(
        default=0, ge=0, description="`resolved` with each row counted `sample_weight` times"
    )
    weighted_granted: int = Field(
        default=0, ge=0, description="`granted` with each row counted `sample_weight` times"
    )
    grant_rate: float | None = Field(
        default=None,
        description="weighted_granted / weighted_resolved; null where nothing resolved",
    )
    dispositions: dict[str, int] = Field(
        default_factory=dict,
        description="Raw row count per machine-readable disposition label, so a "
        "reader can recompute the rate under another convention (plenary grants "
        "only, withdrawals dropped)",
    )
    excluded_extension: int = Field(
        default=0,
        ge=0,
        description="Application stratum only: extension-of-time asks in the same "
        "key, outside the population",
    )
    excluded_unknown_ask: int = Field(
        default=0,
        ge=0,
        description="Application stratum only: parsed asks whose kind could not be read",
    )
    excluded_unparsed: int = Field(
        default=0,
        ge=0,
        description="Application stratum only: applications never application-parsed",
    )


class PartyRates(_Strict):
    """``party-rates`` result: grant rates by government-party status and administration.

    An analytics artifact, not a prediction input: nothing a predict or evaluate
    cell reads is derived from it. Cut under one annotation rule and one date
    convention, both stamped, and optionally at a past moment (``through``) so a
    published tally can be replicated as of its own date.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    rule_version: str = Field(description="The committed annotation rule, e.g. party-v2")
    caption_rule_version: str = Field(
        description="The caption rule the annotation rule composes over both halves"
    )
    counsel_rule_version: str | None = Field(
        default=None,
        description="The counsel annotation rule keying `sg_counsel` on every cell "
        "(e.g. sg-office-v1, its dated roster included), or null for a caption-only cut",
    )
    as_of_field: str = Field(
        description="Which date drove the administration attribution: filed | resolved"
    )
    through: date | None = Field(
        default=None,
        description="The cut's moment: rows filed after it are left out and "
        "dispositions dated after it read as pending. Null = the whole blob",
    )
    since: date | None = Field(
        default=None,
        description="The cut's lower bound: rows filed before it are left out. "
        "Null = from the start of the live slice",
    )
    granted_labels: list[str] = Field(
        description="The disposition labels counted as granted (the binary outcome's granted side)"
    )
    corpus_sha256: str = Field(
        default="",
        description="sha256 of the corpus database the cut ran over — re-derivable "
        "only against this exact corpus state",
    )
    latest_pull: date | None = Field(
        default=None, description="Corpus vintage: newest `last_pulled` across the blob"
    )
    latest_snapshot: date | None = Field(
        default=None, description="Corpus vintage: newest stored snapshot date across the blob"
    )
    rows: int = Field(
        default=0,
        ge=0,
        description="Rows counted into some cell's rate population (application "
        "exclusions, tallied on their cells, are not included)",
    )
    duplicate_rows: int = Field(
        default=0,
        ge=0,
        description="Live-slice rows dropped as a second corpus row for a docket "
        "number already counted — one docket, one vote in a rate",
    )
    other_stratum: int = Field(
        default=0,
        ge=0,
        description="Rows outside the three rated strata (original, miscellaneous, "
        "unparseable docket numbers), left out",
    )
    filed_after_through: int = Field(
        default=0,
        ge=0,
        description="Rows left out as later than `through`: filed after it, or — "
        "carrying no filing date — resolved after it or not at all",
    )
    filed_before_since: int = Field(
        default=0,
        ge=0,
        description="Rows left out as earlier than `since`: filed before it, or — "
        "carrying no filing date — resolved before it, or carrying no date at "
        "all (a row that cannot be placed after the bound is not admitted)",
    )
    undated: int = Field(
        default=0,
        ge=0,
        description="Counted rows carrying no date under `as_of_field` — in the "
        "unattributed cells, never imputed",
    )
    resolution_undated: int = Field(
        default=0,
        ge=0,
        description="Resolved rows carrying no resolution date. Under `through` "
        "they cannot be placed before or after the cut and are read as resolved; "
        "this counts them so the assumption has a size",
    )
    counsel_private_practice: int = Field(
        default=0,
        ge=0,
        description="Counted rows on which the counsel rule's dated roster set aside "
        "a roster name on the petitioner or respondent side as private practice — "
        "a name an undated roster would have read as the office. 0 without a "
        "counsel rule",
    )
    cells: list[PartyRateCell] = Field(
        default_factory=list, description="Non-empty cells only; an absent cell is not a zero"
    )


class ExecutiveSuccessCell(_Strict):
    """One administration x filer cell of the executive success cut.

    ``wins`` / ``decided`` is the executive's record over the in-scope
    applications the Court decided substantively: a government applicant wins
    a grant, in whole or in part, and a government respondent wins a denial.
    Withdrawn applications and those dismissed or denied as moot are counted
    beside the rate, never in it, and so are pending and unreadable ones.
    ``filer`` ``all`` pools the administration's government and challenger cells.
    """

    administration: str | None = Field(
        default=None,
        description="Administration label (e.g. trump-47), or null where the row "
        "carries no date under the cut's convention",
    )
    filer: Literal["government", "challenger", "all"] = Field(
        description="Who filed the application: the federal government, a challenger "
        "to federal executive action, or both cells pooled"
    )
    rows: int = Field(
        ge=0, description="In-scope applications in the cell, extensions of time left out"
    )
    unknown_ask: int = Field(
        default=0,
        ge=0,
        description="Of those, rows whose ask the application parser could not read "
        "(granted federal applications among them), counted like any other",
    )
    pending: int = Field(
        default=0,
        ge=0,
        description="Of those, rows with no disposition as of the cut — outside the rate",
    )
    unreadable: int = Field(
        default=0,
        ge=0,
        description="Of those, rows whose disposition is `other` — outside the rate",
    )
    withdrawn: int = Field(
        default=0, ge=0, description="Of those, withdrawn applications — outside the rate"
    )
    dismissed: int = Field(
        default=0,
        ge=0,
        description="Of those, applications dismissed, including those dismissed or denied "
        "as moot — outside the rate",
    )
    decided: int = Field(
        default=0,
        ge=0,
        description="Rows substantively decided: granted in whole or in part, or denied",
    )
    wins: int = Field(
        default=0,
        ge=0,
        description="Of those, rows the executive won: the granted side (in whole or in "
        "part) for a government applicant, denied for a challenger's application",
    )
    success_rate: float | None = Field(
        default=None, description="wins / decided; null where nothing was decided"
    )
    dispositions: dict[str, int] = Field(
        default_factory=dict,
        description="Row count per reading label (`reading` on the result) among the "
        "cell's resolved rows, so a reader can recompute the rate under another convention",
    )
    excluded_unparsed: int = Field(
        default=0,
        ge=0,
        description="In-scope applications never application-parsed, which cannot be "
        "told from an extension — outside the population",
    )


class ExecutiveControversyCell(_Strict):
    """One administration x filer cell of the executive success cut, counted by controversy.

    Each controversy (``controversy_rule_version``) counts once, with the
    executive's result in its last substantively decided application; one with
    no decided application is indeterminate, beside the rate.
    """

    administration: str | None = Field(
        default=None,
        description="The administration of the controversy's first-filed application that "
        "carries a date under the cut's convention, or null where none does",
    )
    filer: Literal["government", "challenger", "both", "all"] = Field(
        description="Who filed the controversy's applications: one side throughout, both "
        "sides, or every controversy of the administration pooled"
    )
    controversies: int = Field(ge=0, description="Controversies in the cell")
    applications: int = Field(
        ge=0, description="In-scope applications in those controversies, never-parsed ones aside"
    )
    indeterminate: int = Field(
        default=0,
        ge=0,
        description="Of the controversies, those with no substantively decided application "
        "— outside the rate",
    )
    determinate: int = Field(
        default=0, ge=0, description="Controversies with a substantively decided application"
    )
    wins: int = Field(
        default=0,
        ge=0,
        description="Of those, controversies whose last substantively decided application "
        "the executive won",
    )
    success_rate: float | None = Field(
        default=None, description="wins / determinate; null where none is determinate"
    )


class ExecutivePolicyCell(_Strict):
    """One administration x filer x policy area cell of the executive success cut.

    Applications, not controversies, under the policy-area vocabulary
    (``policy_rule_version``); the rate reads as the cut's own cells do.
    """

    administration: str | None = Field(
        default=None, description="Administration under the cut's date convention"
    )
    filer: Literal["government", "challenger"] = Field(
        description="government: the federal government filed; challenger: it responded"
    )
    area: str = Field(description="The policy area")
    rows: int = Field(ge=0, description="In-scope applications in the cell, never-parsed aside")
    decided: int = Field(default=0, ge=0, description="Of those, substantively decided")
    wins: int = Field(default=0, ge=0, description="Of those decided, the executive's wins")
    success_rate: float | None = Field(
        default=None, description="wins / decided; null where none is decided"
    )


class ExecutiveSuccessRow(_Strict):
    """One application the scope rule kept or could not place, for hand review."""

    docket_number: str = Field(description="The application's docket number")
    administration: str | None = Field(
        default=None, description="Administration under the cut's date convention"
    )
    date_filed: date | None = Field(
        default=None,
        description="The row's filing date: the docketed date, else its first proceeding's",
    )
    date_source: Literal["docketed", "first-entry"] | None = Field(
        default=None,
        description="Where `date_filed` came from: the docket's docketed date, or the "
        "first proceeding entry where the docketed date is empty; null = neither",
    )
    in_scope: bool | None = Field(description="The scope rule's reading; null = unknown")
    reason: str = Field(description="The scope rule's reason code")
    government_side: Literal["applicant", "respondent"] = Field(
        description="Which side of the application the federal government is on"
    )
    application_kind: str | None = Field(
        default=None, description="The parsed ask: substantive, unknown, or null if unparsed"
    )
    stored_disposition: str | None = Field(
        default=None, description="The disposition the corpus stores, as of the cut"
    )
    reading: str | None = Field(
        default=None,
        description="The label the cut read the row under: the finer interim reading "
        "where the stored label was re-read, else the stored label; null = pending",
    )
    executive_won: bool | None = Field(
        default=None,
        description="Whether the executive won, where the row was substantively decided",
    )
    controversy_id: str | None = Field(
        default=None,
        description="The controversy the row belongs to (its first-docketed application's "
        "number, as spelled); null for an unknown-scope or never-parsed row, which is "
        "grouped with nothing",
    )
    policy_area: str | None = Field(
        default=None, description="The row's policy area; null where it is unlabeled"
    )
    policy_uncertain: bool = Field(
        default=False,
        description=(
            "Whether the label's subject is in doubt: a rater was unsure of it "
            "or the raters differed"
        ),
    )


class ExecutiveSuccess(_Strict):
    """``executive-success`` result: how often the executive prevails on the emergency docket.

    An analytics artifact, not a prediction input. Cut over the applications the
    scope rule reads as challenging or defending a general federal executive
    action, under one date convention, optionally at a past moment
    (``through``) so a published tally can be replicated as of its own date.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    scope_rule_version: str = Field(description="The committed scope rule, e.g. exec-action-v2")
    party_rule_version: str = Field(description="The party rule the scope rule composes")
    counsel_rule_version: str = Field(description="The counsel rule the scope rule composes")
    reading: Literal["finer", "registered"] = Field(
        description="How a stored `denied` was read: `finer` re-reads it from the row's "
        "latest snapshot under the finer interim reading, which names a partial grant "
        "and a denial as moot; `registered` keeps the stored label"
    )
    as_of_field: str = Field(
        description="Which date drove the administration attribution: filed | resolved"
    )
    through: date | None = Field(
        default=None,
        description="The cut's moment: rows filed after it are left out and "
        "dispositions dated after it read as pending. Null = the whole blob",
    )
    since: date | None = Field(
        default=None,
        description="The cut's lower bound: rows filed before it are left out. "
        "Null = from the start of the live slice",
    )
    corpus_sha256: str = Field(
        default="",
        description="sha256 of the corpus database the cut ran over",
    )
    latest_pull: date | None = Field(
        default=None, description="Corpus vintage: newest `last_pulled` across the blob"
    )
    latest_snapshot: date | None = Field(
        default=None, description="Corpus vintage: newest stored snapshot date across the blob"
    )
    applications: int = Field(
        default=0,
        ge=0,
        description="Applications in the window, extensions of time left out, one per "
        "docket number",
    )
    filed_from_first_entry: int = Field(
        default=0,
        ge=0,
        description="Of those, rows with no docketed date that took their first "
        "proceeding entry's date as their filing date",
    )
    duplicate_rows: int = Field(
        default=0,
        ge=0,
        description="Rows dropped as a second corpus row for a docket number already counted",
    )
    extension_rows: int = Field(
        default=0, ge=0, description="Extension-of-time applications, left out before scope"
    )
    filed_after_through: int = Field(
        default=0, ge=0, description="Rows left out as later than `through`"
    )
    filed_before_since: int = Field(
        default=0, ge=0, description="Rows left out as earlier than `since`"
    )
    reread_rows: int = Field(
        default=0,
        ge=0,
        description="In-scope and unknown-scope rows stored `denied`, never-parsed ones "
        "included, that the finer reading re-read; 0 under `registered`",
    )
    reread_changed: int = Field(
        default=0,
        ge=0,
        description="Of those, rows the finer reading labels other than `denied` "
        "(granted in part and denied as moot, chiefly)",
    )
    reread_unobservable: int = Field(
        default=0,
        ge=0,
        description="Of those, rows with no live-shaped snapshot or no entry the finer "
        "reading matches, which keep the stored label",
    )
    reread_after_through: int = Field(
        default=0,
        ge=0,
        description="Of those, rows whose re-read entry is dated after `through`, which "
        "keep the stored label: the cut's moment had not reached that entry",
    )
    scope_reasons: dict[str, int] = Field(
        default_factory=dict,
        description="Applications per scope reason code, in scope, unknown and out alike",
    )
    unknown_scope: dict[str, int] = Field(
        default_factory=dict,
        description="Applications the scope rule could not place, per administration "
        "(key `unattributed` for an undated row) — beside every cell, never in one",
    )
    cells: list[ExecutiveSuccessCell] = Field(
        default_factory=list, description="Non-empty cells only; an absent cell is not a zero"
    )
    controversy_rule_version: str = Field(
        description="The grouping rule the controversy cells are counted under, e.g. controversy-v2"
    )
    controversy_cells: list[ExecutiveControversyCell] = Field(
        default_factory=list,
        description="The same population counted by controversy; non-empty cells only",
    )
    controversy_unlinked: int = Field(
        default=0,
        description="Grouped applications with no live snapshot, so no case-below or "
        "decided-together link; they join on the caption alone",
    )
    policy_rule_version: str = Field(
        description="The vocabulary the policy cells are labeled under, e.g. policy-area-v1"
    )
    policy_cells: list[ExecutivePolicyCell] = Field(
        default_factory=list,
        description="The in-scope applications by policy area; non-empty cells only",
    )
    policy_unlabeled: int = Field(
        default=0,
        ge=0,
        description="In-scope applications with no policy-area label, never-parsed aside, "
        "outside every policy cell",
    )
    review_rows: list[ExecutiveSuccessRow] = Field(
        default_factory=list,
        description="Every in-scope and unknown-scope application, in docket order, "
        "so the scope reading can be hand-checked row by row",
    )


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
    """The data-validation verdict surfaced on the ops report: ledger + corpus.

    Pairs the two complementary checks the report presents — the git-only
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
    """The evaluators' leakage grading rolled up for the run-ops report.

    The visibility half of the leakage doctrine: replay cells run
    with the same tools as forward cells, so the report must show — across
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

    A read-only roll-up the run-ops report presents so agent-surfaced feedback is
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
    harness: int = Field(
        default=0, ge=0, description="Of the in-window flags, those marked `source: harness`"
    )
    normalised_cells: int = Field(
        default=0,
        ge=0,
        description="In-window cells whose flags.json did not validate and the harness "
        "normalised rather than let fail the cell: one per file, however many flags it "
        "produced. Overlaps `harness`, since a file carried verbatim is carried in harness flags",
    )
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
    """Agent tooling self-reports (`tooling.json`) rolled up for the run-ops report.

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
    """One open issue wearing a ``run:*`` fan-out label, on the ops report.

    Nothing keys on those labels — no workflow triggers on ``issues: labeled``,
    and a predict or evaluate round derives its cases from committed state — so
    an issue carrying one is a marker somebody left behind, never queued work.
    The report lists them with their age so a reader clears them instead of
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
    windows: list[WindowCount] = Field(
        default_factory=list,
        description="The (predictor, window) series behind `sample`, each with its cell "
        "count: the calibration pools every engine's replay cells. " + _POOLED_WINDOWS_DESCRIPTION,
    )

    @model_serializer(mode="wrap")
    def _omit_single_label(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``windows`` while it lists nothing."""
        return _omit_empty(handler(self), windows=self.windows)


class PredictorScoreRow(_Strict):
    """One predictor's evaluation-score distribution (the at-a-glance view).

    ``median`` / ``p25`` / ``p75`` summarize the cross-evaluator
    ``reasoning_quality`` grades; ``accuracy`` is the share of correct calls
    over the cells reporting a ``correct`` at all — ``accuracy_scored``, which
    sits below ``evaluations`` wherever the stamp could not compute one — and
    null where none does.
    All strata pooled — the leaderboard remains the stratified reference.
    ``predictor_scores`` carries one pooled row per predictor, over every
    counted cell in every non-revoked window with ``windows`` stating the
    makeup; ``predictor_scores_by_protocol`` carries one row per predictor and
    counting window.
    """

    predictor_id: str
    process_window: str | None = Field(
        default=None,
        description="On a by-protocol row, the label of the counting window its cells come "
        "from. Null on a pooled row, which spans the windows `windows` lists, and on every "
        "all-versions row",
    )
    windows: list[WindowShare] = Field(default_factory=list, description=_COMPOSITION_DESCRIPTION)
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
    rubrics: list[RubricCount] = Field(
        default_factory=list,
        description="The (evaluator, evaluate digest) pairs whose `reasoning_quality` grades "
        "the quantiles are taken over, each with its `n` in grades. " + _RUBRIC_COVERAGE,
    )

    @model_serializer(mode="wrap")
    def _omit_empty_windows(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``windows`` and ``rubrics`` while they list nothing."""
        return _omit_empty(handler(self), windows=self.windows, rubrics=self.rubrics)


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
    """The report's substantive-results section: is the machine producing?

    Complements run-health (is the machine running): scored-cell counts by
    stratum, replay calibration vs the deny base rate, per-predictor score
    distributions, and live-frontier readiness. Every input is a committed or
    published artifact, keeping run-ops a read-only presenter.
    """

    cells: SubstanceCells
    calibration: SubstanceCalibration
    predictor_scores: list[PredictorScoreRow] = Field(
        default_factory=list,
        description="The pooled default: one row per predictor over every counted cell in "
        "every non-revoked window, ordered by predictor_id",
    )
    predictor_scores_by_protocol: list[PredictorScoreRow] = Field(
        default_factory=list,
        description="The by-protocol cut: one row per (predictor, counting window), ordered "
        "by predictor_id then the window's opening. Two windows of one predictor share no "
        "event, so a move between them is a comparison over different events. Empty on an "
        "all-versions build",
    )
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
        "figures, exactly as the boards record it — so the report and the "
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
    voided_events: VoidedEventsRecord | None = Field(
        default=None,
        description="The voided events the shared stratify pass dropped from the "
        "scored-cell figures, exactly as the boards record them; omitted where "
        "nothing in scope is voided",
    )
    set_aside: SetAsideRecord | None = Field(
        default=None,
        description="The gradings the shared stratify pass set aside from the "
        "scored-cell figures, exactly as the leaderboard records them; the counts "
        "above are the default, without them, and the boards carry the reading "
        "with them counted. Omitted where nothing in scope is set aside",
    )

    @model_serializer(mode="wrap")
    def _omit_empty_voided(self, handler: SerializerFunctionWrapHandler) -> Any:
        """Drop ``voided_events`` / ``set_aside`` while nothing in scope is voided / set aside."""
        return _omit_empty(
            handler(self), voided_events=self.voided_events, set_aside=self.set_aside
        )


class OpsReport(_Strict):
    """``metrics/ops.json`` — an operational snapshot: health, substance, spend, cost.

    A read-only roll-up of authoritative sources (the Actions run history, the
    usage ledger), so no pipeline run writes an ops record. Unlike the
    deterministic leaderboard / back-test roll-ups this is a **point-in-time** view —
    it carries ``generated_at`` and run durations, so it is not byte-stable and is
    surfaced on the run-ops job's Actions run summary (and persisted to the
    ``ops-metrics`` branch) rather than committed to the default branch.

    ``data_health`` carries the data-validation verdict the report also presents —
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


LaneState = Literal["up", "late", "failing", "no-runs"]


class StatusLane(_Strict):
    """One scheduled pipeline lane on the public status page.

    ``state`` answers "is this lane running" from two separate signals. A lane is
    **late** when no run of it started on the default branch since the most recent
    tick its schedule declares (taken a grace period before the snapshot, because
    GitHub starts scheduled runs late), and **failing** when its most recent
    conclusive run ended in failure. Late wins over failing: a lane that has
    stopped starting is the stronger signal. **no-runs** means the run history
    the snapshot read holds no run of the lane at all.
    """

    lane: str = Field(description="The workflow's file stem, e.g. `run-predict`")
    label: str = Field(description="The lane's public name")
    what: str = Field(description="One sentence on what the lane does")
    schedule: str = Field(description="The lane's declared schedule, in words (UTC)")
    state: LaneState
    last_started_at: datetime | None = Field(
        default=None,
        description="When the newest run of the lane on the default branch was created, "
        "whatever it concluded",
    )
    last_conclusion: str | None = Field(
        default=None,
        description="How the newest conclusive run ended (`success`, `failure`, "
        "`timed_out` or `startup_failure`); a skipped or superseded run is not one",
    )
    last_concluded_at: datetime | None = Field(
        default=None, description="When that conclusive run was created"
    )
    expected_since: datetime | None = Field(
        default=None,
        description="The schedule tick a run should have started after for the lane to "
        "count as on time; null when the lane declares no schedule",
    )
    runs_7d: int = Field(
        ge=0, default=0, description="Conclusive runs created in the 7 days before the snapshot"
    )
    successes_7d: int = Field(ge=0, default=0, description="Of `runs_7d`, those that succeeded")


class StatusStageCells(_Strict):
    """One (role, stage) row of a production window's cell census."""

    role: str
    stage: str
    cells: int = Field(ge=0)


class StatusProduction(_Strict):
    """What the ledger recorded over one trailing window: the cells that ran.

    Counted over the committed ``usage.json`` ledger, which lags: a cell's usage
    reaches ``data/`` only when its run's collect PR merges, so each count is a
    floor on what ran, not a real-time figure.
    """

    window: Literal["7d", "30d", "term"]
    start: date
    end: date
    days: int = Field(ge=0)
    term: int | None = Field(
        default=None, description="The October Term the window covers, on the term window"
    )
    cells: int = Field(ge=0)
    events: int = Field(ge=0, description="Distinct events those cells covered")
    by_stage: list[StatusStageCells] = Field(default_factory=list)


class StatusCoverage(_Strict):
    """How much of the docket the pipeline is following, and with what documents.

    Ledger figures are read from the committed tree at the snapshot's commit; the
    watchlist figures from the newest published live-frontier snapshot, whose own
    date is ``frontier_as_of`` (null fields when none was published).
    """

    public_cases: int = Field(ge=0, description="Dockets with a committed case directory")
    events_predicted: int = Field(ge=0, description="Events holding at least one prediction")
    predicted_resolved: int = Field(ge=0, description="Of those, events whose outcome is recorded")
    predictions: int = Field(ge=0, description="Committed prediction cells")
    evaluations_forward: int = Field(ge=0, description="Committed forward gradings")
    frontier_as_of: date | None = None
    watchlist: int | None = Field(
        default=None, ge=0, description="Pending petitions distributed for a conference"
    )
    documents_provisioned: int | None = Field(
        default=None, ge=0, description="Watchlist petitions with at least one stored filing"
    )
    next_conference: date | None = None
    next_conference_petitions: int | None = Field(default=None, ge=0)
    corpus_dockets: int | None = Field(
        default=None, ge=0, description="Dockets in the corpus, from its newest validation"
    )


class StatusTable(_Strict):
    """A table already formatted for display: the page renders it as it stands."""

    columns: list[str]
    rows: list[list[str]]


class StatusBacktest(_Strict):
    """One back-test's committed headline, with the artifact and vintage behind it."""

    key: Literal["historical-replay", "cert", "merits", "salience-replay"]
    name: str
    artifact: str = Field(description="Repository path of the committed artifact")
    vintage: date | None = Field(
        default=None,
        description="The date of the commit that last wrote the artifact; null when unknown",
    )
    summary: str = Field(description="What was replayed, in one or two sentences")
    table: StatusTable | None = None
    reading: str = Field(description="How to read the figures, and what they are not")


class PublicStatus(_Strict):
    """``status.json`` — the public status page's daily snapshot.

    Rendered by ``fedcourts ops-report --status-out`` on the run-ops schedule and
    published to the ``ops-metrics`` branch, where the public site reads it. A
    point-in-time view, like :class:`OpsReport`: it carries ``generated_at`` and so
    is never committed to the default branch. It carries no spend figure and no
    agent prose; every figure is a count, a date, or a committed artifact's
    headline.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    generated_at: datetime
    source_sha: str | None = Field(
        default=None, description="The default-branch commit the snapshot read"
    )
    data_ok: bool | None = Field(
        default=None,
        description="The data-validation verdict (ledger schema and corpus checks); "
        "null when it could not be read",
    )
    lanes: list[StatusLane] = Field(default_factory=list)
    production: list[StatusProduction] = Field(default_factory=list)
    coverage: StatusCoverage
    backtests: list[StatusBacktest] = Field(default_factory=list)


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


_SHA256_DIGEST = r"^sha256:[0-9a-f]{64}$"


class CaseSummaryUsage(_Strict):
    """The token usage of the calls that wrote a case summary.

    One call, or two when the first response was rejected on a mechanical rule
    of the body contract and retried; the figures sum both.
    """

    input_tokens: int = Field(ge=0, description="Uncached input tokens billed")
    output_tokens: int = Field(ge=0, description="Output tokens billed")
    estimated_cost_usd: float = Field(
        ge=0,
        description="The calls' on-demand cost at `pricing.MODEL_RATES` for `model` — "
        + "an estimate at the rate table's snapshot, like every figure it prices",
    )


class CaseSummaryFrontMatter(_Strict):
    """The YAML front matter of ``data/cases/<court>/<docket>/summaries/<day>.md``.

    Written by the harness, never by the model: provenance a reader can check
    the body against. ``record_digest`` is what makes the selection rule
    content-keyed — a case needs a new summary exactly when the digest of its
    newest record differs from the one its newest summary carries
    (``docs/case-summaries.md``).
    """

    case_id: str = Field(description="The case the summary describes, `<court>/<docket>`")
    snapshot: date = Field(
        description="The corpus snapshot day the summary was generated from; the "
        + "file is named for it"
    )
    record_digest: str = Field(
        pattern=_SHA256_DIGEST,
        description="sha256 over the canonical newest snapshot payload (generation "
        + "stamps removed) and the sorted (kind, text sha256) pairs of the case's "
        + "stored documents — the record the summary was written from",
    )
    model: str = Field(description="The Messages API model id that wrote the body")
    prompt_digest: str = Field(
        pattern=_SHA256_DIGEST,
        description="sha256 of `.github/prompts/summarize.md` as sent",
    )
    body_version: Literal[1, 2] = Field(
        default=1,
        description="The body contract the summary was written to, which fixes the "
        + "sections the validator holds it to (`summaries.SECTION_HEADINGS_BY_VERSION`): "
        + "1, the three sections — what happened, what the Court is being asked, "
        + "where it stands; 2, those three between a one-sentence `In brief` headline "
        + "and a closing `What each outcome would mean`. Absent means 1. The harness "
        + "stamps the current version on every summary it writes, and a case whose "
        + "newest summary is older is owed a new one",
    )
    generated_at: datetime = Field(description="When the harness wrote the file (UTC)")
    usage: CaseSummaryUsage | None = Field(
        default=None,
        description="The token usage of the calls that wrote the summary (a rejected first "
        + "response's included), where the responses carried it",
    )


class SummaryPlanCase(_Strict):
    """One case a summary run would write, with the record it would read."""

    case_id: str
    court_id: str
    docket_id: int
    snapshot: date = Field(description="The newest snapshot day; the summary's filename")
    record_digest: str = Field(pattern=_SHA256_DIGEST)
    reason: Literal["new", "record-changed", "body-outdated"] = Field(
        description="new: the case has no committed summary; record-changed: its "
        + "newest summary was written from a different record; body-outdated: its "
        + "newest summary matches the record but was written to an earlier body "
        + "contract (`body_version`)"
    )
    documents: int = Field(ge=0, description="Stored documents the record carries")
    input_chars: int = Field(
        ge=0,
        description="Characters the model would read: the snapshot plus each "
        + "document up to the per-document cap",
    )

    @model_validator(mode="after")
    def _ids_agree(self) -> SummaryPlanCase:
        """The case id, court and docket name one case, since the summary's path
        is built from the latter two and its front matter from the first."""
        if self.case_id != f"{self.court_id}/{self.docket_id}":
            raise ValueError(
                f"case_id {self.case_id!r} does not match {self.court_id}/{self.docket_id}"
            )
        return self


class SummaryWithdrawal(_Strict):
    """One committed summary a summary run withdraws: written before the petition
    the docket number now holds was docketed, so it describes another petition."""

    case_id: str
    path: str = Field(description="The summary file's repository-relative path")
    snapshot: date = Field(description="The snapshot day the summary was written from")
    docketed: date = Field(
        description="The docketed date the case's newest record carries, which the "
        + "summary's snapshot day precedes"
    )


class SummaryPlan(_Strict):
    """``fedcourts summarize-plan`` output — what a summary run would write and cost.

    The plan-and-hold document: rendered before the review hold so the release
    is judged on it, and handed to ``fedcourts summarize`` so the run writes
    exactly what was approved.
    """

    schema_version: Literal["1.0"] = SCHEMA_VERSION
    model: str
    eligible: int = Field(ge=0, description="Cases with at least one committed prediction")
    up_to_date: int = Field(
        ge=0, description="Eligible cases whose newest summary matches their newest record"
    )
    no_snapshot: list[str] = Field(
        default_factory=list, description="Eligible cases the corpus holds no snapshot for"
    )
    not_live_shaped: list[str] = Field(
        default_factory=list,
        description="Eligible cases whose newest snapshot is a CourtListener REST docket "
        + "rather than the supremecourt.gov docket JSON; not summarized, because the "
        + "lane stages and publishes only public-record Court content",
    )
    deferred: int = Field(ge=0, description="Cases owed a summary that the limit held back")
    cases: list[SummaryPlanCase]
    withdrawn: list[SummaryWithdrawal] = Field(
        default_factory=list,
        description="Committed summaries of another petition than the docket number now "
        + "holds (a re-docketed number), which the run's review PR deletes; free, so "
        + "never deferred by the limit",
    )
    estimated_cost_usd_low: float = Field(ge=0)
    estimated_cost_usd_high: float = Field(ge=0)


# --- The release dataset export (`fedcourts export`) -------------------------
#
# One model per exported row, so the Parquet types, the CSV header, the JSON
# Schemas and the bundle's data dictionary are all read off the same fields and
# cannot drift from one another.

#: Why an exported grading does not count toward any scored figure.
ExportExclusionReason = Literal[
    "voided", "forward_claim", "leakage", "forward_claim_and_leakage", "superseded", "out_of_scope"
]


class ExportPredictionRow(_Strict):
    """One row of the release dataset's ``predictions`` table: one committed prediction.

    Keyed on ``(case_id, event_id, predictor_id, run_id)``, the ledger path the
    prediction was committed at. The population is every prediction in the
    export's process scope, graded or not; the flags say which of them the
    scored figures count and which were set aside.
    """

    case_id: str = Field(
        description="The case id, `<court>/<docket_id>`: a CourtListener docket id, or a "
        "project-minted reserved-range id for a petition the Court's own site reached first"
    )
    court: str = Field(description="The court id half of `case_id` (e.g. `scotus`)")
    docket_id: int = Field(description="The numeric docket-id half of `case_id`")
    docket_number: str | None = Field(
        description="The docket number the Court itself assigned (e.g. `25-1234`), the one "
        "field read from the corpus; null where the corpus holds none for the case or the "
        "export was built without it (see the manifest's `docket_numbers`)"
    )
    caption: str | None = Field(
        description="The event's title from its committed `event.yaml`, which names the "
        "case; null where the event definition is absent"
    )
    event_id: str = Field(description="The event id, `evt-<kind>-<slug>`")
    event_kind: EventKind | None = Field(
        description="The event's kind from `event.yaml`; null where the definition is absent"
    )
    stage: Stage | None = Field(
        description="The decision stage, normalized as the scored figures read it: a "
        "petition or appeal event with no recorded stage reads as `cert`; null means no stage"
    )
    moment: Moment | None = Field(
        description="The forecast moment within the stage, normalized as the scored figures "
        "read it (an unrecorded moment reads as the stage's first); null where no stage"
    )
    predictor_id: str = Field(description="The predictor that wrote the prediction")
    engine: Engine = Field(description="The agentic engine the predictor ran on")
    model: str | None = Field(
        description="The model the prediction records as having run; null where it "
        "recorded none (an offline run, or a record written before the field existed). "
        "Not back-filled from the engine's default, which can move after a run"
    )
    run_id: str = Field(
        description="The prediction's run id (a UTC timestamp), as its ledger path spells it"
    )
    created_at: datetime = Field(
        description="When the harness ran the cell: the process stamp's `stamped_at`, or "
        "the record's own `created_at` on a shakedown cell the harness never stamped "
        "(`fedcourtsai.integrity.cell_clock`)"
    )
    probability: float = Field(
        description="The forecast probability of the positive outcome (a grant, at the cert stage)"
    )
    granted: int = Field(description="The binary call the prediction makes: 1 positive, 0 not")
    predicted_disposition: Disposition = Field(description="The predicted disposition label")
    mode: str | None = Field(
        description="The harness's claim about the cell: `forward` (provisioned as a "
        "pending case) or `replay`; null where no context was recorded. A claim, not the "
        "split: `stratum` alone decides forward vs retrospective, and a `forward` cell "
        "resolved on its harness clock day (a same-day tie) is retrospective"
    )
    salience_version: str | None = Field(
        description="The salience scorer version that assigned `band`; null where unrecorded"
    )
    band: str | None = Field(
        description="The case's salience band as at prediction, readable only beside "
        "`salience_version`; null where the signals were unobservable or unrecorded"
    )
    term: int | None = Field(description="The case's October Term; null where unrecorded")
    process_label: str | None = Field(
        description="The harness process label (e.g. `proc-v8`); null on an unstamped cell"
    )
    process_digest: str | None = Field(
        description="The harness process digest (`sha256:<hex>`) that identifies the prompt "
        "and configuration that ran; null on an unstamped cell"
    )
    process_frozen: bool = Field(
        description="Whether the prediction counts: its digest has a counting window "
        "containing its stamp that no revocation de-counted, and no earlier window holds "
        "this predictor's counted cell on the event (the manifest's `frozen_process`)"
    )
    process_window: str | None = Field(
        description="The label of the counting window containing the stamp (e.g. `proc-v8`), "
        "the label its figures are reported under — set on a cell the tie-break or a "
        "revocation leaves uncounted too, so `process_frozen` is the counting bit; null "
        "where no window contains the stamp. No figure pools two values of this column"
    )
    stamped_at: datetime | None = Field(
        description="When the harness stamped the cell (UTC): the clock the forward / "
        "retrospective split uses; null on an unstamped cell, where the split falls back "
        "to `created_at`"
    )
    pipeline_sha: str | None = Field(
        description="The pipeline commit that stamped the cell; null where unrecorded"
    )
    ledger_commit: str | None = Field(
        description="The first-parent commit of the checked-out history that added this "
        "`prediction.json`: its landing on `main` when the manifest's "
        "`source_on_main_first_parent` is true, and on any other checkout when the file "
        "reached that line; null where the export was built without git history or the "
        "file is uncommitted"
    )
    ledger_committed_at: datetime | None = Field(
        description="The committer date of `ledger_commit` (UTC); null with it. GitHub's "
        "own clock only where `ledger_committed_by_github` is true; otherwise the "
        "committing machine's clock, and the landing pull request's `merged_at` is the "
        "witness. Like `ledger_commit`, it dates the file reaching the checked-out line"
    )
    ledger_committed_by_github: bool | None = Field(
        description="Whether `ledger_commit`'s committer is GitHub (`GitHub`, "
        "`noreply@github.com`), as a web merge or auto-merge records it, so "
        "`ledger_committed_at` is GitHub's clock. Necessary, not sufficient: a commit made "
        "in a GitHub Codespace carries the same committer with the Codespace's clock, so "
        "the landing pull request's `merged_at` is what settles a timing claim. Null with "
        "`ledger_commit`; no committer identity is exported beyond this bit"
    )
    resolved_at: date | None = Field(
        description="When the event resolved, from its `outcome.json`; null while "
        "unresolved, and null on a `voided` row"
    )
    actual_disposition: Disposition | None = Field(
        description="The realized disposition label; null while unresolved, and null on a "
        "`voided` row"
    )
    actual_granted: int | None = Field(
        description="The realized binary outcome: 1 positive, 0 not; null while "
        "unresolved, and null on a `voided` row"
    )
    disposition_basis: Literal["standard", "mootness"] | None = Field(
        description="Whether the disposition rests on the ordinary standard or on "
        "mootness (which routes the cell to the procedural stratum); null while "
        "unresolved, and null on a `voided` row"
    )
    stratum: Stratum | None = Field(
        description="The stratum the scored figures place the prediction in (`forward`, "
        "`retrospective` or `procedural`); null unless `scored`"
    )
    scored: bool = Field(
        description="Whether at least one counted grading names this prediction, i.e. it "
        "enters the scored figures"
    )
    staged: bool = Field(
        description="Whether this is the predictor's newest run for the event, the one "
        "provisioning stages for grading"
    )
    forward_claim_excluded: bool = Field(
        description="Whether the harness record claims a forward cell but the event resolved "
        "before the cell's harness clock day, which sets the prediction aside"
    )
    voided: bool = Field(
        default=False,
        description="Whether the prediction's event is voided: its committed outcome "
        "records a different petition than the one the event was opened on, so the "
        "outcome columns are nulled rather than exported beside a forecast of another case "
        "(`docs/process-version.md`, *Voiding an event*)",
    )
    gradings_total: int = Field(
        ge=0,
        description="How many in-scope gradings of this prediction survive the re-grade "
        "collapse: at most one per evaluator, whose newest grading of this predictor on "
        "this event may name a different run, leaving this one with none",
    )
    gradings_leakage_flagged: int = Field(
        ge=0, description="How many of those gradings record `leakage_suspected: true`"
    )
    set_aside: bool = Field(
        description="Whether the prediction is set aside from the scored figures: "
        "`voided`, `forward_claim_excluded`, or graded with every in-scope grading "
        "leakage-flagged"
    )


class ExportGradingRow(_Strict):
    """One row of the release dataset's ``gradings`` table: one judge's grading.

    Long form: a prediction graded by three evaluators has three rows, joined to
    its ``predictions`` row on ``(case_id, event_id, predictor_id,
    prediction_run_id)``. Every grading of an exported prediction is a row,
    re-grades and out-of-scope gradings included; ``counted`` and
    ``excluded_reason`` say which ones the scored figures read.
    """

    case_id: str = Field(description="The graded prediction's case id")
    event_id: str = Field(description="The graded prediction's event id")
    predictor_id: str = Field(description="The graded prediction's predictor")
    prediction_run_id: str = Field(
        description="The graded prediction's run id: `run_id` in the predictions table"
    )
    evaluator_id: str = Field(description="The evaluator (judge) that wrote the grading")
    evaluator_engine: Engine = Field(description="The engine the evaluator ran on")
    evaluator_model: str | None = Field(
        description="The model the grading records as having run; null where it recorded "
        "none. Not back-filled from the engine's default, which can move after a run"
    )
    run_id: str = Field(description="The grading's own run id (a UTC timestamp)")
    correct: int | None = Field(
        description="Whether the prediction's binary call matched the outcome: 1 yes, 0 no; "
        "null where not graded on it"
    )
    brier_score: float | None = Field(
        description="The Brier score of `probability` against the outcome; null where not computed"
    )
    brier_skill_score: float | None = Field(
        description="The Brier skill score against `segment_base_rate`; null without a baseline"
    )
    segment_base_rate: float | None = Field(
        description="The registered base rate the skill score is measured against; null without one"
    )
    base_rate_salience_version: str | None = Field(
        description="The salience version the base rate's band population is keyed on; null "
        "where the baseline is not banded"
    )
    leakage_suspected: bool | None = Field(
        description="The judge's verdict on whether the prediction may have read its own "
        "outcome; null where not assessed"
    )
    counted: bool = Field(description="Whether the scored figures count this grading")
    excluded_reason: ExportExclusionReason | None = Field(
        description="Why an uncounted grading is not counted: `voided` (its event "
        "is voided by a dated freeze-record entry, because the event's outcome "
        "describes another petition), `forward_claim` (the "
        "prediction's forward claim is contradicted by its own record), `leakage` "
        "(`leakage_suspected` is true), `forward_claim_and_leakage` (both), `superseded` "
        "(a newer grading by the same judge of the same predictor on this event replaced "
        "it, possibly one of a different prediction run) or "
        "`out_of_scope` (the grading's harness stamp is absent or predates the freeze "
        "instant); null when counted"
    )
    process_digest: str | None = Field(
        description="The evaluator's harness process digest; null on an unstamped grading"
    )
    stamped_at: datetime | None = Field(
        description="When the harness stamped the grading (UTC); null on an unstamped grading"
    )


class ExportReasoningRecord(_Strict):
    """One line of the release dataset's ``reasoning.jsonl``: a prediction's two documents.

    Keyed on the same ``(case_id, event_id, predictor_id, run_id)`` as the
    predictions table. ``predicted_reasoning`` forecasts what the court will do;
    ``reasoning`` justifies the predictor's own number.
    """

    case_id: str = Field(description="The prediction's case id")
    event_id: str = Field(description="The prediction's event id")
    predictor_id: str = Field(description="The prediction's predictor")
    run_id: str = Field(description="The prediction's run id")
    predicted_reasoning: str | None = Field(
        description="The text of the prediction's `predicted_reasoning.md`, its forecast of "
        "the court's reasoning; null where the prediction names none"
    )
    reasoning: str | None = Field(
        description="The text of the prediction's `reasoning.md`, the predictor's "
        "justification of its number; null where the document is absent"
    )


class ExportCorpusVintage(_Strict):
    """The corpus blob the export's docket numbers were read from, and how fresh it was."""

    backend: str = Field(description="The corpus read backend (`local` or `ranged`)")
    latest_pull: date | None = Field(
        description="The newest `last_pulled` across the blob's cases; null if never pulled"
    )
    latest_snapshot: date | None = Field(
        description="The newest dated snapshot the blob itself stores; null where it stores none"
    )


class ExportFile(_Strict):
    """One file of the release dataset bundle, with its checksum."""

    path: str = Field(description="The file's path inside the bundle")
    sha256: str = Field(description="The file's SHA-256, lowercase hex")
    size: int = Field(ge=0, description="The file's size in bytes")


class ExportManifest(_Strict):
    """``MANIFEST.json`` — what built the release dataset bundle, and from which ledger.

    Holds no build timestamp: a rebuild from the same commit, against the same
    corpus blob, with the same package and pyarrow versions, reproduces the
    bundle byte for byte, and ``source_commit`` dates it.
    """

    dataset: Literal["fedcourtsai-ledger-export"] = "fedcourtsai-ledger-export"
    source_commit: str | None = Field(
        description="The commit checked out when the bundle was built; null where the "
        "export was built without git"
    )
    source_dirty: bool | None = Field(
        description="Whether the checkout had uncommitted changes (tracked files anywhere, or "
        "untracked files under the ledger); a bundle for release is built clean; null "
        "without git"
    )
    source_on_main_first_parent: bool | None = Field(
        description="Whether `source_commit` is on `origin/main`'s first-parent line as "
        "the checkout knew it (nothing is fetched), which is when `ledger_commit` dates "
        "each prediction's landing on `main`; a release bundle requires true. Null "
        "without git or where the checkout has no `origin/main`"
    )
    build_command: str = Field(description="The command that built the bundle")
    package_version: str = Field(description="The fedcourtsai package version that built it")
    process_scope: Literal["frozen", "all"] = Field(
        description="`frozen`: predictions from the pre-registered process only; `all`: every "
        "process version (a diagnostic scope, never the release)"
    )
    frozen_process: FrozenProcessRecord | None = Field(
        description="The freeze constants the frozen scope applied; null under `all`"
    )
    forward_claim_policy: str = Field(
        description="The forward-claim policy the scored population was built under"
    )
    ledger_commits: Literal["git", "omitted"] = Field(
        description="`git`: `ledger_commit` was read from the source history; `omitted`: "
        "built without git history, so the column is null throughout"
    )
    docket_numbers: Literal["corpus", "omitted"] = Field(
        description="`corpus`: `docket_number` was read from the corpus; `omitted`: built "
        "without a corpus, so the column is null throughout"
    )
    corpus_vintage: ExportCorpusVintage | None = Field(
        description="The corpus blob the docket numbers came from; null when omitted"
    )
    counts: dict[str, int] = Field(
        description="Row counts per table and the population's headline tallies"
    )
    files: list[ExportFile] = Field(
        description="Every other file in the bundle with its checksum, in path order"
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
    "blinding.json": BlindingRecord,
    "scope.json": ScopeManifest,
    "schedule.json": Schedule,
    "qp-topic-reference.json": QpTopicReference,
    "qp-topic-reference-applications.json": QpTopicApplicationReference,
    "qp-topics.json": QpTopicLabels,
    "qp-topics-applications.json": QpTopicApplicationLabels,
    "alignment-side-codes.json": AlignmentSideCodes,
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
    "merits_backtest": MeritsBacktest,
    "salience_replay": SalienceReplay,
    "usage": ModelUsage,
    "ops_report": OpsReport,
    "public_status": PublicStatus,
    "corpus_validation": CorpusValidation,
    "corpus_scope_audit": CorpusScopeAudit,
    "scope_manifest": ScopeManifest,
    "schedule": Schedule,
    "live_frontier": LiveFrontier,
    "analytics_report": AnalyticsReport,
    "statpack": StatPack,
    "authorship_tally": AuthorshipTally,
    "same_question_list": SameQuestionList,
    "argument_features": ArgumentFeatures,
    "docket": DocketPack,
    "big_case_board": BigCaseBoard,
    "agent_flags": AgentFlags,
    "agent_tooling": AgentToolingFeedback,
    "cell_failure": CellFailure,
    "mcp_server_config": McpServerConfig,
    "retrieval_log": RetrievalLog,
    "blinding_record": BlindingRecord,
    "qp_topic_reference": QpTopicReference,
    "qp_topic_application_reference": QpTopicApplicationReference,
    "qp_topics": QpTopicLabels,
    "qp_topics_applications": QpTopicApplicationLabels,
    "qp_topic_run_spend": QpTopicRunSpend,
    "alignment_side_codes": AlignmentSideCodes,
    "ai_case_activity": AiCaseActivity,
    "case_summary_front_matter": CaseSummaryFrontMatter,
    "summary_plan": SummaryPlan,
    "export_prediction_row": ExportPredictionRow,
    "export_grading_row": ExportGradingRow,
    "export_reasoning_record": ExportReasoningRecord,
    "export_manifest": ExportManifest,
    "process_registry": ProcessRegistry,
    "voided_events": VoidedEventsRegistry,
    "set_aside_events": SetAsideEventsRegistry,
    "release_manifest": ReleaseManifest,
}
