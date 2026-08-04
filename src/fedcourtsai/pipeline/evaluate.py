"""``run-evaluate`` helpers.

Each evaluator scores each predictor's prediction against the realized
``outcome.json``. The qualitative judgment (reasoning quality) is produced by an
agent; the quantitative pieces (correctness, Brier score, and the segment-baseline
skill score) are deterministic and provided here so every evaluator computes them
identically.

This module reads no config. Every tunable — today, the segment base rate's
lookback window — arrives as an argument, so the functions stay pure and a test,
a replay cell, and the cert back-test all get the same number from the same
inputs. Config resolves one level out, at the caller.
"""

from __future__ import annotations

from ..corpus import CorpusRow, scotus_term_year
from ..schemas import Outcome, Prediction, PredictionContext, StatPack
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
        if entry.salience_version != band_version:
            continue  # version pin: a band name only means something under its own scorer
        if entry.term >= term:
            continue  # leakage guard: the case's own and later Terms never contribute
        if oldest is not None and entry.term < oldest:
            continue  # outside the configured lookback window
        for seg in entry.segments:
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
    merits cell comes from: a GVR and a summary reversal terminate at the cert
    order and never mint one, so their near-certain vacaturs — a cert-stage
    fact the cert sections already carry — never anchor a merits forecast to a
    rate its own population does not face.

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
    carries no merits section, when no prior Term has a parsed judgment, or
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
