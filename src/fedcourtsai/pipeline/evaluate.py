"""``run-evaluate`` helpers.

Each evaluator scores each predictor's prediction against the realized
``outcome.json``. The qualitative judgment (reasoning quality) is produced by an
agent; the quantitative pieces (correctness, Brier score, and the segment-baseline
skill score) are deterministic and provided here so every evaluator computes them
identically.

One function here is deliberately **not** a cell's to compute:
:func:`realized_band_rate` reads the Term the case is in, whose rate keeps
moving until that Term closes, so a value frozen onto an ``evaluation.json``
would say when the cell was graded rather than what the Term did. It lives
beside its strictly-prior sibling because the two share a definition, and is
called from the leaderboard build over the current statpack instead.

This module reads no config. Every tunable — today, the segment base rate's
lookback window — arrives as an argument, so the functions stay pure and a test,
a replay cell, and the cert back-test all get the same number from the same
inputs. Config resolves one level out, at the caller.
"""

from __future__ import annotations

from ..corpus import CorpusRow, scotus_term_year
from ..schemas import (
    Outcome,
    Prediction,
    PredictionContext,
    StatPack,
    StatPackTerm,
    StatPackTermSegment,
)
from .salience import SALIENCE_VERSION, salience_band


def is_correct(prediction: Prediction, outcome: Outcome) -> int:
    """Did the prediction name the right outcome label — on the stage's own axis?

    The cert/interim axis is the disposition label. The **merits** axis is the
    judgment: a merits outcome's ``actual_disposition`` is always the
    off-vocabulary ``other`` (the cert vocabulary has no member for a judgment),
    so comparing dispositions there would score every merits cell against a
    constant — a number the predictor sets by choosing what to write in a field
    the merits contract does not define. The routing is on the **outcome**,
    which is the harness's word: a merits outcome takes the judgment
    comparison whatever the prediction carries, so a judgment-less prediction
    scores 0 rather than collecting the free ``other == other`` match that
    routing on both sides would hand it. (The ``validate`` gate refuses such a
    prediction, but ``correct`` is computed before validate runs.) This keeps
    the leaderboard's accuracy column meaningful at every stage instead of
    publishing a constant for one of them.
    """
    if outcome.judgment is not None:
        return int(prediction.judgment == outcome.judgment)
    return int(prediction.predicted_disposition == outcome.actual_disposition)


def brier_score(prediction: Prediction, outcome: Outcome) -> float:
    """Brier score for the stage's declared binary forecast (lower is better).

    ``actual_granted`` carries the stage's binary — granted on a cert/interim
    event, judgment-disturbed on a merits event — and ``probability`` states
    the matching P, so one formula scores every stage.
    """
    return (prediction.probability - outcome.actual_granted) ** 2


def _version_segments(entry: StatPackTerm, band_version: str) -> list[StatPackTermSegment] | None:
    """One Term's band slices under ``band_version``, or ``None`` if it has none.

    ``None`` rather than an empty list: arithmetically the two are the same to
    the pool, since an empty list adds nothing to either accumulator, but they
    are different facts. ``None`` says the Term never carried this version at
    all, which is what a caller reasoning about coverage needs to be able to
    ask, and what keeps a future caller from reading an empty band list as a
    measured zero.
    """
    if entry.salience_version == band_version:
        return entry.segments
    for block in entry.alt_segments:
        if block.salience_version == band_version:
            return block.segments
    return None


def _pooled_band_rate(
    band: str,
    band_version: str,
    term: int,
    statpack: StatPack,
    *,
    lookback_terms: int,
    risk_set: bool,
) -> float | None:
    """One band's grant rate pooled over Terms strictly before ``term``.

    ``risk_set`` picks which of the two published rates is pooled, and the choice
    has to match how ``band`` was obtained — see the two callers. Pooled as a
    resolved-weighted mean of the per-Term rates, which equals aggregate weighted
    grants over aggregate weighted resolved, so a Term contributes at the weight
    belonging to the rate being pooled.

    ``band_version`` is the frozen salience version that produced ``band``, and
    the pool is **version-pinned**: only Terms whose ``salience_version`` matches
    contribute. A band name is meaningful only under the function that assigned
    it — a sal-v2 ``high`` and a sal-v1 ``high`` are different populations that
    happen to share a label, and pooling them would publish a number no version
    ever defined. When no Term carries the band's version the pool is empty and
    the result is ``None``, the already-contracted no-baseline answer — a
    lagging statpack reads as "no honest baseline yet", never as a silently
    blended one.
    """
    # A Term-YEAR floor, not a row count — see the callers' docstrings. `0` means no
    # floor; `term - 0` would exclude every Term, so the sentinel must short-circuit.
    # A negative window would read as unbounded-plus-a-Term; `ge=0` guards the config
    # path, and clamping here guards a direct caller.
    oldest = term - lookback_terms if lookback_terms > 0 else None
    weighted_grants = 0.0
    weighted_resolved = 0.0
    for entry in statpack.terms:
        # Version pin: a band name only means something under its own scorer, so
        # take that scorer's slices — the Term's own `segments` when it is the
        # active version, else the matching `alt_segments` block, else nothing.
        segments = _version_segments(entry, band_version)
        if segments is None:
            continue
        if entry.term >= term:
            continue  # leakage guard: the case's own and later Terms never contribute
        if oldest is not None and entry.term < oldest:
            continue  # outside the configured lookback window
        for seg in segments:
            if seg.band != band:
                continue
            rate = seg.prefix_est_grant_rate if risk_set else seg.est_grant_rate
            denominator = seg.prefix_weighted_resolved if risk_set else seg.weighted_resolved
            if rate is not None:
                weighted_grants += rate * denominator
                weighted_resolved += denominator
    if weighted_resolved == 0:
        return None
    return weighted_grants / weighted_resolved


def segment_base_rate(
    row: CorpusRow, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The band rate for a case whose band is read from the row **now**.

    For a resolved case that is its *terminal* band, so this pools
    ``est_grant_rate`` — the rate over rows that ended in the band. Baseline and
    grouping match, which is what makes the number meaningful.

    This is the fallback, not the preferred path. Prefer
    :func:`prediction_base_rate` wherever the cell froze its own conditioning;
    use this only where it did not, and note that the cert back-test stays here
    deliberately rather than by omission: its replay is placed at the *last*
    distribution before resolution, so the band it freezes is the band the
    petition ended at, and the population of replay cells at a given band is the
    terminal population. The risk-set rate against that band would be the very
    mismatch this pairing exists to prevent. Also used by any prediction written
    before the frozen block existed.

    Leakage-safe by construction: only Terms preceding the case contribute, so
    the rate never sees the case's own — or any later — Term. ``None`` when the
    case has no Term, no band data precedes it, or nothing in the band resolved.

    ``lookback_terms`` bounds how far back the pool reaches; ``0`` (the
    argument default — the shipped config value is
    ``salience.base_rate_lookback_terms``, which callers pass) means unbounded,
    every prior Term. The bound is a **Term-year band**, ``term - lookback_terms <= entry
    < term``, not a slice of the pack's rows: a Term absent from the statpack, or
    present as a zero-row cursor entry, shortens the sample rather than pulling an
    older Term in to refill the slot. That keeps the window a claim about the
    recency of the Court's behaviour, and keeps it from shifting — silently, and in
    every published skill number — as the walker's coverage changes.
    """
    term = scotus_term_year(row.docket_number)
    if term is None:
        return None
    return _pooled_band_rate(
        salience_band(row),
        SALIENCE_VERSION,
        term,
        statpack,
        lookback_terms=lookback_terms,
        risk_set=False,
    )


def prediction_base_rate(
    context: PredictionContext | None, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The band rate a cell actually faced, from its frozen conditioning.

    Pools ``prefix_est_grant_rate`` — the **risk-set** rate over every petition
    that ever *reached* the band, not only those that ended in it. That is the
    right rate precisely because ``context.band`` is the band as at prediction: a
    band only ever strengthens, so a cell sitting at ``baseline`` may still relist,
    and the population it belongs to is everyone who has reached ``baseline``.

    The pairing is the whole point. Reading the risk-set rate against a *terminal*
    band would overstate the baseline for exactly the petitions whose band moved,
    and reading the terminal rate against a frozen band would understate it
    several-fold in the weak bands. Neither half is correct alone.

    ``None`` when there is no frozen context, when the snapshot disclosed no
    proceedings so no band could be derived, or when no prior Term carries the
    band **under the version that assigned it** (the harness stamps
    ``salience_version`` whenever it derives a band, so a versionless band never
    arrives from a cell) — the caller then falls back to
    :func:`segment_base_rate`, which is honest rather than invented.
    """
    if (
        context is None
        or context.band is None
        or context.term is None
        or context.salience_version is None
    ):
        return None
    return _pooled_band_rate(
        context.band,
        context.salience_version,
        context.term,
        statpack,
        lookback_terms=lookback_terms,
        risk_set=True,
    )


#: The smallest resolved sample a **realized-Term** band rate may rest on. It
#: binds twice, on the leave-one-out **weighted** denominator that scores the
#: case and on the **observed** row count behind it, because a Term walked under
#: denial sampling can carry a weighted 31 over some fourteen real petitions and
#: the standard error follows the rows. Below either, :func:`realized_band_rate`
#: returns ``None`` and the cell carries no realized-Term skill — a visible
#: omission (the aggregate's own ``*_scored`` count), never a zero folded into a
#: mean.
#:
#: Thirty, the figure :data:`MERITS_BASE_RATE_MIN_PARSED` states, for a sharper
#: version of the same reason. A rate over thirty observed rows carries a
#: standard error of at most ~0.09, and the skill ratio divides by
#: ``(rate - outcome)**2``, so noise in the rate lands on the denominator of
#: every cell in the band at once rather than averaging out across them. What
#: binds harder here than on the pooled prior-Term baseline is that this pool is
#: **one Term**: it cannot be widened by reaching further back, so a thin band
#: is not a sampling choice but a fact about how far the Term has got. The floor
#: is therefore a wait-for-the-Term rule — the `high` band clears it partway
#: through an October Term and the weaker bands almost at once, while a band
#: that never clears is omitted for that Term entirely. A stated
#: pre-registration choice, not a knob: only tests pass ``min_resolved``
#: anything else.
REALIZED_BAND_RATE_MIN_RESOLVED = 30


def realized_band_rate(
    band: str,
    band_version: str,
    term: int,
    statpack: StatPack,
    *,
    risk_set: bool,
    own_grant_family: int,
    min_resolved: int = REALIZED_BAND_RATE_MIN_RESOLVED,
) -> float | None:
    """One band's grant rate **in ``term`` itself**, leave-one-out for the scored case.

    The ex-post sibling of :func:`_pooled_band_rate`, and identical to it in
    every respect but one: it reads the case's **own** Term instead of every
    strictly-prior one. Same band, same version pin (a band name means something
    only under the scorer that assigned it), same ``risk_set`` pairing — a
    frozen-context band takes ``prefix_est_grant_rate``, a band derived from the
    row now takes ``est_grant_rate``.

    Because the level is held at the one that obtained, skill against this rate
    nets out level-knowledge and leaves **discrimination**: a predictor that has
    the Term's level right but cannot tell its cases apart scores positive
    against the prior-Term pool and ~0 here. It is **not** leakage-safe and no
    predictor could have known it in-season, so it never ranks and is never
    pooled or averaged with the prior-Term skill; ``metrics/README.md`` carries
    the claim contract.

    **Leave-one-out.** The scored case sits inside this rate, and in a thin band
    that bites — one case moves a band of seventy-odd by well over a point. The
    pack publishes no grant count, but the rate is a ratio of integer weighted
    counts, so ``rate * weighted_resolved`` rounds back to the numerator
    exactly; ``own_grant_family`` comes off it and one unit of weight off the
    denominator. The ``risk_set`` pairing is what makes that subtraction well
    defined: a band only ever strengthens, so a case frozen at a band ends at
    that band or a stronger one and is therefore in the band's **risk set**,
    while a case banded from the row now is in the band's **terminal**
    population. Against the wrong rate the case would be subtracted from a
    population it was never counted in.

    ``own_grant_family`` is 1 iff the case's disposition is in
    :data:`fedcourtsai.schemas.GRANT_FAMILY_DISPOSITIONS`, the numerator's own
    definition — **not** ``actual_granted``, which is the binary scoring target
    and additionally admits ``granted-in-part``. Subtracting the latter would
    remove a grant the published numerator never counted.

    **What the correction does to the scale**, exactly. Jackknifing moves the
    baseline away from the case's own outcome by a fixed factor, so
    ``skill = 1 - (1 - skill_uncorrected) * ((n - 1) / n)**2`` for a band of
    weighted ``n`` (exactly, wherever ``own_grant_family`` equals the case's
    ``actual_granted``, i.e. everywhere but a ``granted-in-part`` cert
    disposition). Two readings follow. It is monotone in the uncorrected score,
    so it never reorders cells within a band. And the attainable level-only
    null is **not** 0 but ``(2n - 1) / n**2`` — the score of a forecaster
    reporting the band's *published* rate, which contains its own case: about
    +0.03 at n = 72 and about +0.06 at the floor of n = 31. (A forecaster
    reporting the leave-one-out level itself would score exactly 0, but that
    level is ``(g - y) / (n - 1)``, so reporting it requires knowing the
    outcome — an oracle, not a null.) Read "~0" as that bound. Note the shift
    itself, ``(1 - skill_uncorrected) * (2n - 1) / n**2``, is bounded only at
    the null: Brier skill has no lower bound, so a badly negative cell shifts
    much further.

    Three bounded approximations, stated rather than corrected. The subtraction
    removes one unit of weight rather than the row's own ``sample_weight``,
    which the pack does not publish per row; the two coincide on a Term walked
    at weight 1 — every live Term, so every forward cell — while on a
    reweighted historical Term, where the retrospective cells sit, the
    correction falls short of a sampled denial's full weight. The case is
    assumed to be a row of the segment's population (the Term's live-slice paid
    modern-cert petitions), which the salience gate makes true of every cell it
    provisions but which an IFP or off-slice row would break. And the pack is a
    **vintage**: a case resolved after it was built is not yet in its own Term's
    counts, so the subtraction over-corrects by one unit until the next refresh
    — bounded by ``1 / min_resolved`` and self-correcting as the Term closes.

    ``None`` when the Term carries no segment for the band under that version,
    when the band holds a single resolved row (leaving it out leaves nothing),
    when either leave-one-out sample is below ``min_resolved``, or when the
    subtraction lands outside ``[0, loo_weighted]`` — which cannot happen for a
    case the counts contain, so it is proof that this vintage does not contain
    it and the honest answer is no baseline rather than a clamped certainty.
    """
    for entry in statpack.terms:
        # Version pin, resolved the same way the pooler resolves it — including
        # through `alt_segments`. An asymmetry here would drop the realized-Term
        # skill of every cell frozen at a non-active version while leaving its
        # prior-Term skill standing, so the board would print two skill columns
        # over two different populations, split on a version label rather than
        # on the resolved-count floor that is this field's only stated omission.
        segments = _version_segments(entry, band_version)
        if segments is None:
            continue
        if entry.term != term:
            continue  # the case's OWN Term, and only it — the whole difference from the pooler
        for seg in segments:
            if seg.band != band:
                continue
            rate = seg.prefix_est_grant_rate if risk_set else seg.est_grant_rate
            weighted = seg.prefix_weighted_resolved if risk_set else seg.weighted_resolved
            observed = seg.prefix_resolved if risk_set else seg.resolved
            if rate is None:
                continue
            loo_weighted = weighted - 1
            if loo_weighted <= 0:
                return None  # a single resolved row: leaving it out leaves no band at all
            if loo_weighted < min_resolved or observed - 1 < min_resolved:
                return None
            loo_grants = round(rate * weighted) - own_grant_family
            if not 0 <= loo_grants <= loo_weighted:
                return None  # the case is not in this vintage's counts; invent nothing
            return loo_grants / loo_weighted
    return None


#: The smallest parsed sample a merits baseline may rest on. Below it the
#: pooled rate is ``None`` (claim unscored, no skill score) rather than
#: published: ``docs/outcome-decomposition.md`` requires a stated minimum
#: observation count of any thin-history baseline before it ships, and the
#: merits section exists from its very first parsed judgment — so without a
#: floor a one-row prior Term would hand out a degenerate 0.0/1.0 baseline. In
#: `claim_score`'s difference form — the consumer today — such a baseline
#: produces a score of magnitude ~1 that swamps every other claim in a total;
#: and `brier_skill`, the consumer once merits cells fan out, masks exactly the
#: cells such a baseline got *right* (its Brier is 0 there), leaving a
#: published mean taken only over the ones it got wrong.
#: At a rate near 0.7 this bounds the standard error around 0.08, and the Court
#: decides roughly sixty argued cases a Term. The pool takes whole Terms
#: strictly prior, so within-Term accumulation never counts toward a case's own
#: baseline: the floor clears on one prior grant Term of parsed judgments, or
#: two thin ones. A stated pre-registration choice, not a knob.
MERITS_BASE_RATE_MIN_PARSED = 30


def merits_base_rate(
    grant_term: int, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The historical disturbed rate a merits cell's skill is scored against.

    Pools the statpack merits section's per-grant-Term counts — ``parsed`` and
    ``disturbed`` — over Terms **strictly before** ``grant_term``, as aggregate
    disturbed over aggregate parsed. The merits sibling of
    :func:`segment_base_rate`, under the identical leakage rule, but
    deliberately **version-free**: the section is not a salience-band product,
    so there is no scorer version to pin (``docs/decision-model.md``
    pre-registers this baseline).

    **The baseline's population is the scored population.** The merits section
    admits exactly the grants that open a merits proceeding
    (:func:`fedcourtsai.corpus.opens_merits_proceeding`), which is where a
    merits cell comes from — further guarded, label-independently, against
    parsed judgments dated on (or missing relative to) their own grant, the
    pre-convention cert-order class (``docs/decision-model.md``): a GVR and a
    summary reversal terminate at the cert
    order and never mint one, so their near-certain vacaturs — a cert-stage
    fact the cert sections already carry — never anchor a merits forecast to a
    rate its own population does not face, whatever the row's label says.

    ``grant_term`` is the October Term certiorari was **granted** in
    (:func:`fedcourtsai.pipeline.judgment.grant_term_year` over the merits
    event's ``opened_at``), the axis the statpack merits section is keyed on.
    It must not be substituted with the docket-number Term: the two disagree
    for a petition docketed into the incoming Term and granted before that Term
    opens, and there the docket Term is one *later* than the grant Term, which
    would admit the case's own cohort into its own baseline. Keying both on the
    grant Term also keeps cohort-mates comparable — two cases granted in the
    same Term are scored against the same pool.

    ``lookback_terms`` bounds the pool as a Term-year band exactly as
    :func:`segment_base_rate` does (``0`` = unbounded). ``None`` when the pack
    carries no merits section, when no prior Term has a parsed judgment, when
    any Term that would **contribute** to the pool carries a null
    ``cert_order_excluded`` — a build
    :func:`fedcourtsai.pipeline.judgment.judgment_rode_the_grant_order` never
    ran on, whose parsed counts may still contain the cert-order class the
    rate must exclude (``metrics/README.md`` rules such a section unquotable;
    this makes the rule structural for the harness-pooled baseline, while the
    evaluator-recorded ``segment_base_rate`` stays governed by the prompt's
    omit rule) — or
    when the pooled sample is below :data:`MERITS_BASE_RATE_MIN_PARSED` — the
    already-contracted no-baseline answer, never an invented or degenerate rate.
    """
    if statpack.merits is None:
        return None
    oldest = grant_term - lookback_terms if lookback_terms > 0 else None
    disturbed = 0
    parsed = 0
    for entry in statpack.merits.terms:
        if entry.term >= grant_term:
            continue  # leakage guard: the case's own and later Terms never contribute
        if oldest is not None and entry.term < oldest:
            continue  # outside the configured lookback window
        if entry.cert_order_excluded is None:
            # Null marks a build the cert-order pool guard never ran on, so
            # this Term's parsed counts may include the class the rate must
            # exclude — no honest baseline pools from it.
            return None
        disturbed += entry.disturbed
        parsed += entry.parsed
    if parsed < MERITS_BASE_RATE_MIN_PARSED:
        return None
    return disturbed / parsed


def judgment_correct(prediction: Prediction, outcome: Outcome) -> int | None:
    """Exact-match of the predicted merits judgment, or ``None`` off the axis.

    1 iff the prediction's ``judgment`` equals the outcome's on the full
    Judgment vocabulary (a ``reversed`` call against a ``vacated`` outcome is
    0); ``None`` wherever either side records no judgment — every non-merits
    cell. Descriptive accuracy beside the scored disturbed-binary Brier, never
    a proper score.
    """
    if prediction.judgment is None or outcome.judgment is None:
        return None
    return int(prediction.judgment == outcome.judgment)


def brier_skill(brier: float, actual_granted: int, base_rate: float | None) -> float | None:
    """Brier skill of a forecast's ``brier`` vs the naive ``base_rate`` baseline.

    ``1 - brier / baseline_brier``, where the baseline is the forecaster that
    always predicts ``base_rate``. ~0 when the forecast is no better than the base
    rate, positive (up to 1) when better, negative when worse. ``None`` when there
    is no base rate, or when the baseline is already perfect (its Brier is zero —
    ``base_rate`` matched the outcome exactly), where the ratio is undefined. The
    numeric core shared by the evaluate path and the cert back-test.
    """
    if base_rate is None:
        return None
    baseline_brier = (base_rate - actual_granted) ** 2
    if baseline_brier == 0:
        return None
    return 1.0 - brier / baseline_brier


def brier_skill_score(
    prediction: Prediction, outcome: Outcome, base_rate: float | None
) -> float | None:
    """Brier skill score of a prediction vs the segment base rate.

    Convenience wrapper over :func:`brier_skill` for schema objects: scores the
    prediction's Brier against the baseline that always predicts ``base_rate``, so
    parroting the segment's grant rate earns ~0 skill.
    """
    return brier_skill(brier_score(prediction, outcome), outcome.actual_granted, base_rate)


def claim_score(p: float, y: int, b: float) -> float:
    """One claim's score: the baseline's Brier minus the forecast's.

    ``(b - y)**2 - (p - y)**2``, for predicted probability ``p``, realized outcome
    ``y`` in {0, 1}, and harness-computed baseline ``b``. Positive when the forecast
    landed closer to the outcome than the baseline did, negative when a bold call
    missed.

    **Proper.** For a fixed ``b`` the score differs from ``-(p - y)**2`` by a term
    that depends on ``b`` and ``y`` but not on ``p``, so nothing done to ``p`` can
    move it; expected score is therefore maximized by reporting the probability
    actually held. (Not an affine transform in the usual sense — the added term
    varies with ``y`` — but the ``p``-independence is what propriety needs, and it is
    exact.)

    **Restating the baseline is worth nothing.** At ``p == b`` the score is
    identically 0 for *either* outcome, realized and not merely in expectation.

    The difference form rather than :func:`brier_skill`'s ratio, because per-claim
    scores are summed and a ratio does not compose — and because the ratio explodes
    near the endpoints where these baselines live.
    """
    return (b - y) ** 2 - (p - y) ** 2


def vote_accuracy(prediction: Prediction, outcome: Outcome) -> float | None:
    """Fraction of predicted votes that matched, over the Justices both name.

    Scored only where the outcome actually records a vote, so a Justice whose vote
    was never observed costs a predictor nothing — the denominator is what the
    record discloses, never what the predictor attempted. ``Outcome.vote_provenance``
    is what says whether a short list means "only these are public" or "nobody
    looked"; this function needs only the intersection either way.
    """
    if not prediction.votes or not outcome.votes:
        return None
    actual = {v.justice: v.vote for v in outcome.votes}
    scored = [v for v in prediction.votes if v.justice in actual]
    if not scored:
        return None
    hits = sum(1 for v in scored if actual[v.justice] == v.vote)
    return hits / len(scored)
