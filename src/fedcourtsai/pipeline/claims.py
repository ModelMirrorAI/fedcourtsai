"""The harness-declared claim sets and their deterministic scoring.

``docs/outcome-decomposition.md`` is the design authority: what a claim is, why
the set is fixed and mandatory, the scoring rule (implemented once, in
:func:`fedcourtsai.pipeline.evaluate.claim_score`, and only *wired* here), and
the publishing rules a claim total travels under. This module holds the
mechanical family's moving parts:

- the **declaration table** — per event kind, exactly which claims a prediction
  carries, under a versioned set id;
- the **resolvers** — pure functions from committed artifacts (the prediction's
  frozen ``context``, the outcome's ``signals`` block) to 0 / 1 / ``None``,
  where ``None`` is the availability mask: the record does not disclose what
  the claim needs, a property of the record and never of the predictor;
- the **baselines** — strictly-prior-Term rates from the committed statpack,
  conditioned on the state the prediction's frozen context disclosed, never
  the predictor's number;
- :func:`score_claims`, the orchestrator that assembles one
  :class:`~fedcourtsai.schemas.ClaimScoreBlock` per prediction.

Everything is a pure function of committed artifacts, so re-scoring a cell
over the same committed inputs — the statpack revision included — reproduces
the same block byte for byte. Like the rest of
:mod:`fedcourtsai.pipeline.evaluate`, this module reads no config: the
baseline lookback arrives as an argument and resolves at the caller.

The semantic family is out of scope by pre-registration: its claims need a
reader, and the blinding precondition ``docs/outcome-decomposition.md`` states
is not met. Nothing here touches it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Protocol

from ..ids import parse_event_kind
from ..schemas import (
    ClaimProbability,
    ClaimScore,
    ClaimScoreBlock,
    EventKind,
    Outcome,
    Prediction,
    PredictionContext,
    StatPack,
)
from .evaluate import claim_score, prediction_base_rate

# The declared cert-stage claim ids, in the fixed order the block reports them.
CLAIM_DISPOSITION = "disposition"
CLAIM_RELIST_INCREMENT = "relist-increment"
CLAIM_CVSG_INCREMENT = "cvsg-increment"

# The versioned set id stamped into every block this declaration produces. A
# change to which claims the cert set carries is a NEW version, never an
# in-place edit — same discipline as the salience function's `sal-v1`.
CLAIM_SET_CERT_V1 = "cert-v1"

# Per event kind: the set id and the declared claims, in reporting order. The
# set is fixed and mandatory (docs/outcome-decomposition.md, *Why the set is
# mandatory*): a predictor answers every declared claim and adds none. Only
# petition-kind (cert-stage) events declare a set; the merits set arrives with
# the merits stage, against data the pipeline does not yet produce.
DECLARED_CLAIM_SETS: Mapping[EventKind, tuple[str, tuple[str, ...]]] = {
    EventKind.petition: (
        CLAIM_SET_CERT_V1,
        (CLAIM_DISPOSITION, CLAIM_RELIST_INCREMENT, CLAIM_CVSG_INCREMENT),
    ),
}


def declared_claim_set(event_id: str) -> tuple[str, tuple[str, ...]] | None:
    """The ``(set_version, claim_ids)`` an event's kind declares, or ``None``.

    ``None`` — no set, so no block — for a malformed event id and for every
    kind without a declaration (a motion or order has no declared claims).
    """
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
    context: PredictionContext, statpack: StatPack, *, lookback_terms: int
) -> float | None:
    """The disposition claim's baseline: the frozen band's risk-set grant rate.

    Exactly the segment baseline the headline skill score already uses —
    :func:`fedcourtsai.pipeline.evaluate.prediction_base_rate`, reused rather
    than duplicated: the band's grant rate pooled over statpack Terms strictly
    before the case's Term, version-pinned, conditioned on the band frozen when
    the cell ran. ``None`` (claim unscored) where the context froze no band or
    no prior Term carries it — the block never falls back to the terminal band,
    because a terminal band is conditioning on the petition's own future.
    """
    return prediction_base_rate(context, statpack, lookback_terms=lookback_terms)


def _baseline_relist_increment(
    context: PredictionContext, statpack: StatPack, *, lookback_terms: int
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
    context: PredictionContext, statpack: StatPack, *, lookback_terms: int
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


_RESOLVERS: Mapping[str, Callable[[PredictionContext, Outcome], int | None]] = {
    CLAIM_DISPOSITION: _resolve_disposition,
    CLAIM_RELIST_INCREMENT: _resolve_relist_increment,
    CLAIM_CVSG_INCREMENT: _resolve_cvsg_increment,
}


class _BaselineFn(Protocol):
    """A claim's baseline function: frozen conditioning + statpack -> rate | None."""

    def __call__(
        self, context: PredictionContext, statpack: StatPack, *, lookback_terms: int
    ) -> float | None: ...


_BASELINES: Mapping[str, _BaselineFn] = {
    CLAIM_DISPOSITION: _baseline_disposition,
    CLAIM_RELIST_INCREMENT: _baseline_relist_increment,
    CLAIM_CVSG_INCREMENT: _baseline_cvsg_increment,
}


def resolve_claim(claim_id: str, context: PredictionContext, outcome: Outcome) -> int | None:
    """One claim's resolution — 1 true, 0 false, ``None`` masked-unresolvable."""
    return _RESOLVERS[claim_id](context, outcome)


def claim_baseline(
    claim_id: str, context: PredictionContext, statpack: StatPack, *, lookback_terms: int
) -> float | None:
    """One claim's harness baseline, or ``None`` where no honest one exists."""
    return _BASELINES[claim_id](context, statpack, lookback_terms=lookback_terms)


def score_claims(
    prediction: Prediction, outcome: Outcome, statpack: StatPack, *, lookback_terms: int
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
    :func:`fedcourtsai.pipeline.evaluate.claim_score` where both exist. The
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
    # The disposition claim restates the headline `probability` — the same
    # belief, written twice so the set is self-describing. A pair that diverges
    # is two committed numbers for one belief, the same class of malformed
    # input as a duplicate: no block, never a silent pick between them.
    if CLAIM_DISPOSITION in stated and stated[CLAIM_DISPOSITION] != prediction.probability:
        return None

    rows: list[ClaimScore] = []
    total: float | None = None
    floor: float | None = None
    for claim_id in claim_ids:
        probability = stated[claim_id]
        resolved = resolve_claim(claim_id, prediction.context, outcome)
        baseline = claim_baseline(
            claim_id, prediction.context, statpack, lookback_terms=lookback_terms
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
