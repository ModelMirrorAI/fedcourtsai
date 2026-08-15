"""The harness-declared claim sets and their deterministic scoring.

``docs/outcome-decomposition.md`` is the design authority: what a claim is, why
the set is fixed and mandatory, the scoring rule (implemented once, in
:func:`fedcourtsai.pipeline.base_rates.claim_score`, and only *wired* here), and
the publishing rules a claim total travels under. This module holds the
mechanical family's moving parts:

- the **declaration table** — per event kind (and, for the minted merits
  event, per exact event id), exactly which claims a prediction carries,
  under a versioned set id;
- the **resolvers** — pure functions from committed artifacts (the prediction's
  frozen ``context``, the outcome's stage-appropriate signals block) to
  0 / 1 / ``None``,
  where ``None`` is the availability mask: the record does not disclose what
  the claim needs, a property of the record and never of the predictor;
- the **baselines** — strictly-prior-Term rates from the committed statpack,
  conditioned on the state the prediction's frozen context disclosed, never
  the predictor's number;
- :func:`score_claims`, the orchestrator that assembles one
  :class:`~fedcourtsai.schemas.ClaimScoreBlock` per prediction.

Everything is a pure function of committed artifacts, so re-scoring a cell
over the same committed inputs — the statpack revision included — reproduces
the same block byte for byte. Like the baselines it wires
(:mod:`fedcourtsai.pipeline.base_rates`), this module reads no config: the
baseline lookback arrives as an argument and resolves at the caller.

The semantic family is out of scope here: its claims need a reader and have no
harness-computable prior for :func:`claim_score` to consume, so they earn an
ordinal grade rather than a score. Nothing in this module touches it, and no
semantic grade is ever run through the rule wired here. Its own (declared,
graded, and alpha) home is :mod:`fedcourtsai.pipeline.semantic`.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping
from typing import Protocol

from ..ids import parse_event_kind
from ..schemas import (
    ClaimProbability,
    ClaimScore,
    ClaimScoreBlock,
    Disposition,
    EventKind,
    Judgment,
    Outcome,
    Prediction,
    PredictionContext,
    StatPack,
)
from . import moments
from .base_rates import (
    claim_score,
    interim_base_rate,
    merits_base_rate,
    prediction_base_rate,
    summary_route_base_rate,
)
from .judgment import judgment_disturbed

# The declared cert-stage claim ids, in the fixed order the block reports them.
CLAIM_DISPOSITION = "disposition"
CLAIM_RELIST_INCREMENT = "relist-increment"
CLAIM_CVSG_INCREMENT = "cvsg-increment"

# The two cert-stage claims `cert-v2` adds, each carrying forecast content the
# predict prompt elicits in prose beside the number, so the document and the
# claim say one thing (`docs/outcome-decomposition.md`, *Where each forecast
# content class goes*). Each is an
# **aggregate**: the route claim asks whether the grant disposed in the cert
# order at all, not by which of the two spellings, and the dissent claim asks
# whether any Justice noted a dissent, never which — the eight tests' volume
# condition rules the per-Justice form out (`docs/outcome-decomposition.md`).
CLAIM_SUMMARY_ROUTE = "summary-disposition-route"
CLAIM_DISSENT_FROM_DENIAL = "dissent-from-denial"

# The declared interim-stage claim ids, in reporting order. The disposition
# claim is `interim-disposition` rather than a second use of `disposition`, and
# the distinctness is load-bearing rather than cosmetic: baseline routing is
# keyed on the claim id, the two claims draw on different sections of the
# statpack over different populations resolving on different standards, and any
# aggregate that pooled them by id would be averaging a cert grant rate with an
# interim one.
CLAIM_INTERIM_DISPOSITION = "interim-disposition"
CLAIM_RESPONSE_REQUESTED_INCREMENT = "response-requested-increment"
CLAIM_REFERRAL_INCREMENT = "referral-increment"
CLAIM_AMICUS_INCREMENT = "amicus-increment"

# The declared merits-stage claim id: the binary disturbed projection of the
# judgment axis. The multi-class judgment form waits on a schema field carrying
# a per-label distribution, exactly as the cert disposition claim's does; the
# per-Justice vote, split, and writing claims are deliberately NOT declared —
# their committed resolution channel (a real vote record on the outcome) does
# not exist, no strictly-prior committed cut carries their baselines, and nine
# per-Justice claims re-encode one correlated insight ninefold
# (docs/outcome-decomposition.md, *What stays out*; docs/decision-model.md).
CLAIM_JUDGMENT_DISTURBED = "judgment-disturbed"

# The versioned set ids stamped into every block these declarations produce. A
# change to which claims a set carries is a NEW version, never an in-place
# edit — same discipline as the salience function's `sal-v1`.
CLAIM_SET_CERT_V1 = "cert-v1"
CLAIM_SET_CERT_V2 = "cert-v2"
CLAIM_SET_INTERIM_V1 = "interim-v1"
CLAIM_SET_MERITS_V1 = "merits-v1"

# Per event kind: the set id and the declared claims, in reporting order. The
# set is fixed and mandatory (docs/outcome-decomposition.md, *Why the set is
# mandatory*): a predictor answers every declared claim and adds none. Only
# petition-kind (cert-stage) events declare a kind-keyed set; the interim and
# merits sets below are reached through the declared-moment table instead,
# because a stage is not derivable from an event id's kind segment (a merits
# moment's kind is `order` or `brief`, and not every such event is merits).
#
# This kind-keyed table stays on `cert-v1` while the declared cert *moments*
# advance to `cert-v2`. It is the fallback for what is not a declared moment —
# an entry-pinned petition event, a legacy id minted before the moment table —
# and those were elicited under cert-v1's contract, so scoring them against a
# larger set would report claims their cells were never asked for as unstated.
# A version id is a claim about what was asked, not about when it is scored.
DECLARED_CLAIM_SETS: Mapping[EventKind, tuple[str, tuple[str, ...]]] = {
    EventKind.petition: (
        CLAIM_SET_CERT_V1,
        (CLAIM_DISPOSITION, CLAIM_RELIST_INCREMENT, CLAIM_CVSG_INCREMENT),
    ),
}

# The declared cert set: cert-v1's three claims, in their existing order, plus
# the two mechanical additions. Order is append-only across a version bump so a
# reader diffing two blocks reads down the same rows.
_CERT_V2_CLAIM_SET: tuple[str, tuple[str, ...]] = (
    CLAIM_SET_CERT_V2,
    (
        CLAIM_DISPOSITION,
        CLAIM_RELIST_INCREMENT,
        CLAIM_CVSG_INCREMENT,
        CLAIM_SUMMARY_ROUTE,
        CLAIM_DISSENT_FROM_DENIAL,
    ),
)

# The merits declaration. Reached through the declared-moment table rather than
# by event id: every merits moment carries it, because a forecast taken after
# briefing answers the same claims as one taken at the grant — only the evidence
# behind the answer differs, and that lives on the aggregation key.
_MERITS_CLAIM_SET: tuple[str, tuple[str, ...]] = (
    CLAIM_SET_MERITS_V1,
    (CLAIM_JUDGMENT_DISTURBED,),
)

# The interim declaration, reached the same way: every interim moment carries
# it, whether the forecast is taken on arrival, after the Court called for a
# response, or once one was filed. The three escalation claims are increments
# from both committed ends — the frozen context's as-at-prediction values
# against the outcome's `interim_signals` — which is what a monotone signal
# demands. Deliberately absent: a claim about a *response being filed*. A
# respondent may answer uninvited, so it is not a rung of the Court's own
# ladder of attention; its committed channel is a date column carrying the
# undated-entry undercount rather than a max-latched flag; and the moment named
# for it is the one whose keep-or-drop decision is still open, so declaring a
# claim on it would let the claim set decide that question by inertia.
_INTERIM_CLAIM_SET: tuple[str, tuple[str, ...]] = (
    CLAIM_SET_INTERIM_V1,
    (
        CLAIM_INTERIM_DISPOSITION,
        CLAIM_RESPONSE_REQUESTED_INCREMENT,
        CLAIM_REFERRAL_INCREMENT,
        CLAIM_AMICUS_INCREMENT,
    ),
)

#: Set version -> its declaration, the resolution the moment table names by
#: string. The table stays a leaf module; the claim ids stay here with their
#: resolvers.
_SETS_BY_VERSION: Mapping[str, tuple[str, tuple[str, ...]]] = {
    CLAIM_SET_CERT_V1: DECLARED_CLAIM_SETS[EventKind.petition],
    CLAIM_SET_CERT_V2: _CERT_V2_CLAIM_SET,
    CLAIM_SET_INTERIM_V1: _INTERIM_CLAIM_SET,
    CLAIM_SET_MERITS_V1: _MERITS_CLAIM_SET,
}

# The claims that restate the prediction's headline `probability` — one belief
# written twice so each set is self-describing (the cert disposition claim on a
# petition, the interim one on an application, the disturbed claim on the merits
# event). A pair that diverges is malformed and voids the block; see
# `score_claims`.
_HEADLINE_CLAIMS = (CLAIM_DISPOSITION, CLAIM_INTERIM_DISPOSITION, CLAIM_JUDGMENT_DISTURBED)


def declared_claim_set(event_id: str) -> tuple[str, tuple[str, ...]] | None:
    """The ``(set_version, claim_ids)`` an event declares, or ``None``.

    A **declared forecast moment** (:mod:`fedcourtsai.pipeline.moments`) declares
    whatever its stage declares — every cert moment carries the cert set, every
    interim moment the interim set, every merits moment the merits set. Only the
    cert stage also declares by *kind*, for the entry-pinned petition ids that
    predate the moment table; an interim or merits set is reachable through the
    table alone. The claims do not change because the forecast
    was taken later; only the information set does, and that lives on the
    aggregation key rather than in the declaration. Bumping a set version per
    moment would fragment every claim aggregate for no semantic gain.

    Everything else declares by kind, unchanged: an entry-pinned motion, a
    circuit appeal, a legacy id. ``None`` — no set, so no block — for a
    malformed event id and for every kind without a declaration.
    """
    spec = moments.spec_for(event_id)
    if spec is not None:
        return _SETS_BY_VERSION.get(spec.claim_set_version or "")
    kind_slug = parse_event_kind(event_id)
    if kind_slug is None:
        return None
    try:
        kind = EventKind(kind_slug)
    except ValueError:
        return None
    return DECLARED_CLAIM_SETS.get(kind)


def _resolve_disposition(context: PredictionContext, outcome: Outcome) -> int | None:
    """The disposition claim's resolution: the committed grant flag.

    The one claim resolvable on every outcome — ``actual_granted`` is required
    and immutable, so the mask never bites here.
    """
    return outcome.actual_granted


def _resolve_relist_increment(context: PredictionContext, outcome: Outcome) -> int | None:
    """Did the distribution count rise past its value as at prediction?

    An increment, resolved from both ends of the committed pair: the
    prediction-time count from the frozen context, the resolution-time count
    from the outcome's signals block. Masked (``None``) where either end is
    undisclosed — a context whose snapshot carried no proceedings fixes no
    prediction-time count, and an outcome without a signals block observed
    nothing at resolution. The count is max-latched and never falls, so the
    strict comparison reads any non-rise as no increment.
    """
    if (
        not context.signals_observable
        or context.distribution_count is None
        or outcome.signals is None
    ):
        return None
    return int(outcome.signals.distribution_count > context.distribution_count)


def _resolve_cvsg_increment(context: PredictionContext, outcome: Outcome) -> int | None:
    """Was a CVSG called for after prediction time, given none at prediction?

    Masked (``None``) three ways, all properties of the record: an outcome
    without a signals block observed nothing at resolution; a context whose
    signals were unobservable cannot distinguish "no CVSG yet" from "nobody
    looked", so its null ``cvsg_date`` fixes no prediction-time state; and a
    CVSG already on the docket at prediction time makes the increment vacuous —
    a ``cvsg_date``, once set, stays set, so there is nothing left to forecast.
    """
    if outcome.signals is None or not context.signals_observable:
        return None
    if context.cvsg_date is not None:
        return None
    return int(outcome.signals.cvsg_date is not None)


def _baseline_disposition(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The disposition claim's baseline: the frozen band's risk-set grant rate.

    Exactly the segment baseline the headline skill score already uses —
    :func:`fedcourtsai.pipeline.base_rates.prediction_base_rate`, reused rather
    than duplicated: the band's grant rate pooled over statpack Terms strictly
    before the case's Term, version-pinned, conditioned on the band frozen when
    the cell ran. ``None`` (claim unscored) where the context froze no band or
    no prior Term carries it — the block never falls back to the terminal band,
    because a terminal band is conditioning on the petition's own future.
    """
    return prediction_base_rate(context, statpack, lookback_terms=lookback_terms)


def _baseline_relist_increment(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The relist-increment baseline the published statpack cannot yet support.

    The honest baseline is a risk-set hazard conditioned on the disclosed
    state: among prior-Term petitions that reached the prediction-time count
    ``k``, the rate that reached ``k + 1`` — and the hazard moves steeply in
    ``k`` (roughly 26% at one distribution, 27% at two, 47% at three, 71% at
    four, denial-reweighted), so a coarser conditioning would misprice exactly
    the petitions the gate selects. The committed pack publishes no cut that
    supports it strictly-prior: its relist-bucket section pools every Term —
    the case's own included, which the leakage guard forbids — and its
    per-Term segments condition on the salience band, which collapses the
    distribution counts above two and admits CVSG petitions at any count. So
    the baseline is ``None`` and the claim goes unscored until the statpack
    carries a per-Term relist-bucket cut over the scored segment; the claim
    stays declared, because the set is fixed and scoring is keyed on a
    baseline existing, not on redeclaring the set.
    """
    return None


def _baseline_cvsg_increment(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The cvsg-increment baseline the published statpack cannot yet support.

    Same gap as the relist increment: the pack's CVSG cut pools every Term —
    the case's own included — so no strictly-prior rate is derivable from a
    published section, and the per-Term surface carries no CVSG cut at all.
    ``None`` until a cut lands that actually carries the claim's conditioning,
    which is stricter than a per-Term terminal CVSG share (that is still an
    unconditional level): the honest baseline is the arrival rate
    P(CVSG after prediction | no CVSG at prediction, at the disclosed
    distribution count), strictly-prior per Term, over the scored segment —
    and censoring-corrected, because a CVSG adds months to resolution, so a
    resolved-only rate in an open Term runs at a fraction of the true one
    (``docs/outcome-decomposition.md``, *A published rate was censored*).
    """
    return None


def _resolve_summary_route(context: PredictionContext, outcome: Outcome) -> int | None:
    """Did the grant dispose of the case in the cert order itself?

    1 for a GVR or a summary merits disposition, 0 for a grant set down for
    plenary review, read **only** from the outcome's committed
    ``disposition_route`` marker — written by the refresh channel from the order
    text it held (:func:`fedcourtsai.pipeline.outcome.disposition_route`), never
    re-derived here.

    That the marker is the only source matters, and reading a 1 off a
    ``gvr`` / ``summary-reversal`` label where the marker is absent would be the
    natural shortcut: it would recover a resolution on outcomes committed before
    the marker existed. It is refused because it would make **assessability
    depend on the answer** — the cases resolving 1 would always be assessable
    while the cases resolving 0 would be assessable only where a payload
    happened to be retained, so the assessed subpopulation's realized rate would
    sit above the baseline's and a predictor could bank the difference without
    forecasting anything. The marker's own writer applies the matching symmetric
    admission test.

    Masked (``None``) two ways, both properties of the record. **Vacuous** on
    every denial: there is no route to forecast where review was refused, and
    the conditioning is not cosmetic — unconditionally the summary class runs
    near one percent of resolved petitions, a baseline close enough to the
    boundary that the eight tests' volume condition rejects the claim, while
    conditioned on the grant family it is a coin-flip-scale question. **Not
    assessed** on any grant whose record carried no route marker: false and
    unread must stay apart, and a coverage sentinel is what says which.
    """
    if not outcome.actual_granted:
        return None
    if outcome.disposition_route is None:
        return None
    return int(outcome.disposition_route != "plenary")


def _resolve_dissent_from_denial(context: PredictionContext, outcome: Outcome) -> int | None:
    """Did any Justice note a dissent from — or a statement respecting — the denial?

    Aggregated existence, read straight off the outcome's committed
    ``noted_dissent_from_denial`` marker. **Nothing here or anywhere else in the
    mechanical family resolves a per-Justice form**: such notings sit near one
    percent of petitions and concentrate in two Justices, so the fine claim fails
    the eight tests' volume condition while the aggregate passes it, and the
    per-Justice channel would additionally need a vote record
    ``docs/decision-model.md`` pre-registers as never scored.

    Masked (``None``) **vacuously** on every disposition that is not a denial —
    a granted petition was never denied, and a dismissal or a withdrawal is not
    the Court refusing review, so neither has a denial to have dissented from —
    and on the **coverage** sentinel, a null marker meaning no retained order
    text was assessed. Most of the ledger carries no payload, so that mask is the
    common state, not an edge. The vacuity test keys on the disposition rather
    than on ``actual_granted`` so it names the same population the claim does
    and the marker's writer gates on: `P(some Justice noted a dissent | denied)`.
    """
    if outcome.actual_disposition != Disposition.denied:
        return None
    if outcome.noted_dissent_from_denial is None:
        return None
    return int(outcome.noted_dissent_from_denial)


def _resolve_response_requested_increment(
    context: PredictionContext, outcome: Outcome
) -> int | None:
    """Did the Court call for a response after prediction time, given none then?

    The interim analogue of the CVSG increment, and masked the same three ways,
    all properties of the record: an outcome without an ``interim_signals``
    block observed nothing at resolution; a context whose signals were
    unobservable cannot tell "no request yet" from "nobody looked", so its null
    flag fixes no prediction-time state; and a request already on the docket at
    prediction time makes the increment vacuous — the flag is max-latched and,
    once true, stays true, so there is nothing left to forecast.
    """
    if (
        outcome.interim_signals is None
        or not context.signals_observable
        or context.response_requested is None
    ):
        return None
    if context.response_requested:
        return None
    return int(outcome.interim_signals.response_requested)


def _resolve_referral_increment(context: PredictionContext, outcome: Outcome) -> int | None:
    """Was the application referred to the full Court after prediction time?

    The same three-way mask and the same vacuity arm as the response-requested
    increment, over the referral flag: a referral is never undone, so a context
    that already discloses one leaves nothing to forecast.
    """
    if (
        outcome.interim_signals is None
        or not context.signals_observable
        or context.referred_to_court is None
    ):
        return None
    if context.referred_to_court:
        return None
    return int(outcome.interim_signals.referred_to_court)


def _resolve_amicus_increment(context: PredictionContext, outcome: Outcome) -> int | None:
    """Did the amicus count rise past its value as at prediction?

    The relist increment's shape rather than the CVSG's: a count, not a flag, so
    it is resolved by strict comparison of both committed ends and there is no
    vacuity arm — the count is unbounded above, so a docket that already carries
    amicus briefs can always carry another. Masked (``None``) where either end
    is undisclosed. The count is monotone and never falls, so the strict
    comparison reads any non-rise as no increment.
    """
    if (
        outcome.interim_signals is None
        or not context.signals_observable
        or context.amicus_briefs is None
    ):
        return None
    return int(outcome.interim_signals.amicus_briefs > context.amicus_briefs)


def _baseline_summary_route(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The summary-route baseline: the prior Terms' cert-order share of grants.

    :func:`fedcourtsai.pipeline.base_rates.summary_route_base_rate` over the
    frozen context's Term — pooled cert-order dispositions over pooled grants,
    Terms strictly before it only. Conditioned on the grant family, matching the
    resolver's own conditioning; the function's docstring states why the
    published counts make the rate an **under**statement of the class it prices,
    and why nothing the pack publishes bounds the residual today.

    Keyed on ``context.term`` — the docket-number Term — rather than the grant
    Term, which is the cert stage's convention and the same axis
    :func:`_baseline_disposition` anchors on: a cert cell is not supplied a grant
    Term, and inventing one from the outcome would condition a baseline on the
    very fact the claim resolves against. It carries the convention's known
    residual: a petition docketed into the incoming Term but granted before that
    Term opens has a docket Term one *later* than its grant Term, so the pool can
    include the cohort it was granted alongside. That is the same **class** of
    exposure the disposition claim already carries, over the same small
    population — but not the same magnitude, and the difference is worth stating
    rather than glossing: a grant rate moves a couple of points between Terms
    while the cert-order share of grants moves across a 0.29-0.46 band, and the
    affected petitions are enriched in exactly the GVRs this claim resolves.

    ``None`` where the context froze no Term, or where the pooled prior grants do
    not clear the baseline's stated minimum.
    """
    if context.term is None:
        return None
    return summary_route_base_rate(context.term, statpack, lookback_terms=lookback_terms)


def _baseline_interim_disposition(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The interim disposition claim's baseline: the strictly-prior interim rate.

    :func:`fedcourtsai.pipeline.base_rates.interim_base_rate` over the frozen
    context's Term, which on an application cell is the **application** Term the
    interim statpack section is keyed on — read from the ``YYAnnn`` number at
    provisioning, so it needs no clock and cohort-mates share a pool. Version-free
    and band-free, because the interim section is neither: an application freezes
    no salience band by rule, so there is nothing here for the cert set's
    ``prediction_base_rate`` pairing to condition on.

    ``grant_term`` is unused — it addresses the merits section, which is keyed on
    a different Term of a different case population — but the parameter stays in
    the signature because :class:`_BaselineFn` is one shape for every claim.

    ``None`` — claim unscored, never an invented rate — where the context froze
    no Term, where no prior application-Term resolved anything substantive, or
    where the pooled strictly-prior sample is below the interim floor.

    Two limits are stated rather than guarded. The rate is the same at all three
    interim moments, so a forecast taken after the Court called for a response is
    scored against the arrival-time unconditional rate — the register's test 3
    again, and the reason a moment-conditioned pool is the estimator's registered
    next step. And ``context.term`` is whichever Term the docket number yielded:
    on the anomaly of an interim moment pinned to a *cert* docket it is the cert
    Term, and this would pool the interim section by it — the right time axis
    over the wrong population. No committed cell has that shape, and the claim
    board excludes interim cells today, so the exposure is a hand-pinned
    cross-stage event rather than a live path.
    """
    if context.term is None:
        return None
    return interim_base_rate(context.term, statpack, lookback_terms=lookback_terms)


def _baseline_dissent_from_denial(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The dissent-from-denial baseline no committed artifact yet supports.

    The honest baseline is the strictly-prior-Term share of *denied* petitions
    whose order text records a noted dissent, over the scored segment. The
    committed pack publishes no cut that carries it — no section counts order-list
    notations at all — and the record that would feed one
    (``Outcome.noted_dissent_from_denial``) starts empty and fills only as
    dockets refresh, so even a new cut would price a coverage-limited population
    until the retained-text gap closes. ``None`` until it lands; the claim stays
    declared, because the set is fixed and scoring is keyed on a baseline
    existing, not on redeclaring the set — the same standing the two increment
    claims have, and what the block banks meanwhile is the committed
    probabilities.
    """
    return None


def _baseline_response_requested_increment(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The response-requested-increment baseline the published statpack cannot support.

    The committed pack's interim section publishes ``response_requested`` as an
    unconditional count over the whole substantive slice — every application that
    had drawn a request as at the build, pending ones included. Two things are
    wrong with it as a baseline, and the second is the one that binds. It is an
    unconditional level rather than the arrival-conditioned hazard the claim
    needs (among prior-Term applications that had *not* yet drawn a request at
    the disclosed posture, the rate that went on to), which is test 3 of the
    outcome-decomposition register. And its denominator is the whole substantive
    slice while the resolved counts beside it are the machine-matched-resolved
    subset, so the column is **right-censored**: an application still pending
    when the pack was built contributes a "no" it may yet reverse, exactly the
    censoring failure test 5 asks about. ``None`` until a per-Term cut
    conditioned as the claim is lands; the claim stays declared, because scoring
    is keyed on a baseline existing rather than on redeclaring the set, and the
    probabilities bank from the first claiming cell so they are there to score
    when it does.
    """
    return None


def _baseline_referral_increment(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The referral-increment baseline the published statpack cannot support.

    The same two gaps, over ``referred_to_court``: the pack's count is
    unconditional across the substantive slice rather than the rate at which an
    unreferred application becomes a referred one, and it is censored by the
    pending tail the same way. ``None`` until a strictly-prior per-Term cut
    carries the claim's own conditioning.
    """
    return None


def _baseline_amicus_increment(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The amicus-increment baseline the published statpack cannot support.

    ``with_amicus`` is published per Term, so the gap is not coverage — it is
    that the column counts applications carrying *at least one* amicus brief,
    while the claim is a rise past the specific count the snapshot disclosed.
    Collapsing the count to a flag discards the conditioning variable itself,
    which is the register's test 3 at its sharpest, and the column carries the
    same pending-tail censoring as its two siblings. ``None`` until a per-Term
    amicus-*count* cut over the substantive slice lands.
    """
    return None


def _resolve_judgment_disturbed(context: PredictionContext, outcome: Outcome) -> int | None:
    """Did the Court disturb the judgment below — the merits declared binary.

    Resolved from the outcome's ``judgment`` through the single shared
    projection (:func:`fedcourtsai.pipeline.judgment.judgment_disturbed`): a
    DIG and an equally divided affirmance resolve 0 (undisturbed — both leave
    the judgment below standing). Masked (``None``) where the outcome records
    no judgment, a state no merits outcome writer produces but a malformed or
    foreign record could.
    """
    if outcome.judgment is None:
        return None
    return int(judgment_disturbed(Judgment(outcome.judgment)))


def _baseline_judgment_disturbed(
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None,
) -> float | None:
    """The disturbed claim's baseline: the strictly-prior pooled disturbed rate.

    :func:`fedcourtsai.pipeline.base_rates.merits_base_rate` over the **grant**
    Term — the axis the statpack merits section is keyed on, supplied by the
    caller from the merits event's ``opened_at`` (the grant date). The frozen
    context's docket-number Term is deliberately *not* used: the two disagree
    for a petition docketed into the incoming Term and granted before it opens,
    where the docket Term runs one later and would admit the case's own cohort
    into its own baseline, and keying on the grant Term is also what keeps two
    cases granted in the same Term scored against the same pool. ``None`` —
    claim unscored — where the caller supplied no grant Term, where the prior
    Terms' pooled sample does not clear the baseline's minimum, or where a
    Term inside the pooled window carries a null ``cert_order_excluded``
    (the baseline's provenance refusal).
    """
    if grant_term is None:
        return None
    return merits_base_rate(grant_term, statpack, lookback_terms=lookback_terms)


_RESOLVERS: Mapping[str, Callable[[PredictionContext, Outcome], int | None]] = {
    CLAIM_DISPOSITION: _resolve_disposition,
    CLAIM_RELIST_INCREMENT: _resolve_relist_increment,
    CLAIM_CVSG_INCREMENT: _resolve_cvsg_increment,
    CLAIM_SUMMARY_ROUTE: _resolve_summary_route,
    CLAIM_DISSENT_FROM_DENIAL: _resolve_dissent_from_denial,
    # The interim disposition resolves off the same committed field — an
    # application's `actual_granted` is the interim binary, written by the same
    # rule — so it reuses the resolver rather than restating it. What separates
    # the two claims is the baseline, and that is keyed on the id.
    CLAIM_INTERIM_DISPOSITION: _resolve_disposition,
    CLAIM_RESPONSE_REQUESTED_INCREMENT: _resolve_response_requested_increment,
    CLAIM_REFERRAL_INCREMENT: _resolve_referral_increment,
    CLAIM_AMICUS_INCREMENT: _resolve_amicus_increment,
    CLAIM_JUDGMENT_DISTURBED: _resolve_judgment_disturbed,
}


class _BaselineFn(Protocol):
    """A claim's baseline function: frozen conditioning + statpack -> rate | None."""

    def __call__(
        self,
        context: PredictionContext,
        statpack: StatPack,
        *,
        lookback_terms: int,
        grant_term: int | None,
    ) -> float | None: ...


_BASELINES: Mapping[str, _BaselineFn] = {
    CLAIM_DISPOSITION: _baseline_disposition,
    CLAIM_RELIST_INCREMENT: _baseline_relist_increment,
    CLAIM_CVSG_INCREMENT: _baseline_cvsg_increment,
    CLAIM_SUMMARY_ROUTE: _baseline_summary_route,
    CLAIM_DISSENT_FROM_DENIAL: _baseline_dissent_from_denial,
    CLAIM_INTERIM_DISPOSITION: _baseline_interim_disposition,
    CLAIM_RESPONSE_REQUESTED_INCREMENT: _baseline_response_requested_increment,
    CLAIM_REFERRAL_INCREMENT: _baseline_referral_increment,
    CLAIM_AMICUS_INCREMENT: _baseline_amicus_increment,
    CLAIM_JUDGMENT_DISTURBED: _baseline_judgment_disturbed,
}


def resolve_claim(claim_id: str, context: PredictionContext, outcome: Outcome) -> int | None:
    """One claim's resolution — 1 true, 0 false, ``None`` masked-unresolvable."""
    return _RESOLVERS[claim_id](context, outcome)


def claim_baseline(
    claim_id: str,
    context: PredictionContext,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None = None,
) -> float | None:
    """One claim's harness baseline, or ``None`` where no honest one exists."""
    return _BASELINES[claim_id](
        context, statpack, lookback_terms=lookback_terms, grant_term=grant_term
    )


def claim_block_problems(prediction: Prediction) -> list[str]:
    """Why this prediction's claims block would void at scoring, in words.

    Empty when there is nothing to say: no claims block, or an event with no
    declared set — absence is a legitimate state, not a defect. With a block
    present against a declared set, the *agent-authored* incoherences
    :func:`score_claims` silently voids on are named — a duplicated claim id,
    a declared claim left unstated, a headline diverging from the
    prediction's own ``probability`` — so ``validate`` can surface a block
    that will never score while the cell can still be fixed, instead of the
    claim board simply lacking it later. Two absences are deliberately *not*
    reported: a missing ``context`` (a harness stamp whose absence is a
    tolerated provisioning gap — see ``_read_cell_context``), and a missing
    claims block altogether — an omitted block is a legitimate state today
    (every committed cell predates the field), though once cells run under a
    claims-asking process it becomes the likelier agent failure, and flagging
    it would key on the process-version partition rather than this shape
    check. A test pins the enumerated shapes to the scorer's refusals; a new
    void condition in :func:`score_claims` needs a matching arm here.
    """
    declared = declared_claim_set(prediction.event_id)
    if declared is None or prediction.claims is None:
        return []
    problems: list[str] = []
    set_version, claim_ids = declared
    stated = _stated_probabilities(prediction.claims)
    if stated is None:
        counts = Counter(claim.claim_id for claim in prediction.claims)
        duplicated = sorted(claim_id for claim_id, n in counts.items() if n > 1)
        problems.append(
            f"claim id(s) stated twice — two numbers for one belief: {', '.join(duplicated)}"
        )
        return problems
    problems.extend(
        f"declared claim {claim_id!r} ({set_version}) is not stated"
        for claim_id in claim_ids
        if claim_id not in stated
    )
    problems.extend(
        f"headline claim {headline!r} states {stated[headline]!r} but the "
        f"prediction's probability is {prediction.probability!r} — one belief, "
        "two committed numbers"
        for headline in _HEADLINE_CLAIMS
        if headline in stated and stated[headline] != prediction.probability
    )
    return problems


def score_claims(
    prediction: Prediction,
    outcome: Outcome,
    statpack: StatPack,
    *,
    lookback_terms: int,
    grant_term: int | None = None,
) -> ClaimScoreBlock | None:
    """Assemble the claim-score block for one prediction, or ``None`` for none.

    ``None`` — no block, never a crash — wherever the inputs cannot carry one:
    an event kind with no declared set, a prediction without a ``claims`` block
    (every prediction written before the field existed), or one without the
    frozen ``context`` the resolvers and baselines condition on. The set is
    mandatory, so a claims block that skips a declared claim, or states one
    twice, also yields ``None``: a partial answer scores nothing rather than
    scoring the half the predictor chose. A disposition claim that diverges
    from the headline ``probability`` voids the block the same way — the two
    are one belief restated, and a divergent pair is malformed, not a choice.
    Stated claims outside the declared set are ignored — the declaration, not
    the census, fixes what is scored.

    Per claim: the outcome from its resolver (``None`` = the availability
    mask), the baseline from its baseline function, and the score from
    :func:`fedcourtsai.pipeline.base_rates.claim_score` where both exist. The
    ``total`` sums the scored claims only; the ``floor`` is the realized total
    of the control that reports every scored claim's baseline — identically
    zero, computed rather than asserted, because ``claim_score(b, y, b) == 0``
    exactly; ``lift`` is total minus floor.
    """
    declared = declared_claim_set(prediction.event_id)
    if declared is None or prediction.claims is None or prediction.context is None:
        return None
    set_version, claim_ids = declared
    stated = _stated_probabilities(prediction.claims)
    if stated is None or any(claim_id not in stated for claim_id in claim_ids):
        return None
    # A headline claim (the cert disposition claim, the merits disturbed claim)
    # restates the prediction's `probability` — the same belief, written twice
    # so the set is self-describing. A pair that diverges is two committed
    # numbers for one belief, the same class of malformed input as a
    # duplicate: no block, never a silent pick between them.
    for headline in _HEADLINE_CLAIMS:
        if headline in stated and stated[headline] != prediction.probability:
            return None

    rows: list[ClaimScore] = []
    total: float | None = None
    floor: float | None = None
    for claim_id in claim_ids:
        probability = stated[claim_id]
        resolved = resolve_claim(claim_id, prediction.context, outcome)
        baseline = claim_baseline(
            claim_id,
            prediction.context,
            statpack,
            lookback_terms=lookback_terms,
            grant_term=grant_term,
        )
        score: float | None = None
        if resolved is not None and baseline is not None:
            score = claim_score(probability, resolved, baseline)
            total = (total or 0.0) + score
            floor = (floor or 0.0) + claim_score(baseline, resolved, baseline)
        rows.append(
            ClaimScore(
                claim_id=claim_id,
                probability=probability,
                baseline=baseline,
                outcome=resolved,
                score=score,
            )
        )
    lift = total - floor if total is not None and floor is not None else None
    return ClaimScoreBlock(
        declared_set_version=set_version, claims=rows, total=total, floor=floor, lift=lift
    )


def _stated_probabilities(claims: list[ClaimProbability]) -> dict[str, float] | None:
    """The stated probabilities by claim id, or ``None`` on a duplicate.

    A duplicated claim id is ambiguous — two numbers for one belief — and the
    conservative resolution is no block, not a silent pick between them.
    """
    stated: dict[str, float] = {}
    for claim in claims:
        if claim.claim_id in stated:
            return None
        stated[claim.claim_id] = claim.probability
    return stated
