"""``run-evaluate`` helpers.

Each evaluator scores each predictor's prediction against the realized
``outcome.json``. The qualitative judgment (reasoning quality) is produced by an
agent; the quantitative pieces (correctness, Brier score, and the segment-baseline
skill score) are deterministic and provided here so every evaluator computes them
identically — and, where the harness owns a number rather than the evaluator, so
that it and the agents answer to one implementation: ``stamp-cell`` stamps the
merits and interim skill through :func:`brier_skill` here.

:func:`segment_base_rate` is the one baseline that lives here rather than in
:mod:`fedcourtsai.pipeline.base_rates`: it bands a corpus row, so it needs the
corpus and the salience scorer, and a leaf that reached for either would stop
being a leaf. It shares its pooler with the rest of them, and re-exports
:func:`merits_base_rate` so that the whole set an evaluator is told to match —
``.github/prompts/evaluate.md`` names this module for all of them — resolves
under the one name the prompt gives it.

This module reads no config. Every tunable — today, the segment base rate's
lookback window — arrives as an argument, so the functions stay pure and a test,
a replay cell, and the cert back-test all get the same number from the same
inputs. Config resolves one level out, at the caller.
"""

from __future__ import annotations

from ..corpus import CorpusRow, scotus_application_term_year, scotus_term_year
from ..schemas import Outcome, Prediction, StatPack

# `merits_base_rate` is re-exported, not used here — see the module docstring.
from .base_rates import _pooled_band_rate, interim_base_rate, merits_base_rate  # noqa: F401
from .moments import scores_votes
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


def segment_base_rate(
    row: CorpusRow, statpack: StatPack, *, lookback_terms: int = 0
) -> float | None:
    """The stage-appropriate prior-Term rate for a case, banded from the row **now**.

    Three arms, keyed on what the docket number is. An **application** docket
    (``YYAnnn``) takes the interim arm — the substantive slice's grant rate
    pooled over application-Terms strictly before its own
    (:func:`fedcourtsai.pipeline.base_rates.interim_base_rate`) — and it is
    tested first, because an A-form number carries no cert Term and would
    otherwise fall straight through to ``None``. It takes no band: the interim
    stage is not a salience-band product, so there is no band to read and none is
    invented. A cert docket takes the band arm below. Anything else — a bare
    sequential number, an original docket, a blank — carries no Term on either
    axis and yields ``None``.

    The cert arm: the band rate for a case whose band is read from the row
    **now**. For a resolved case that is its *terminal* band, so this pools
    ``est_grant_rate`` — the rate over rows that ended in the band. Baseline and
    grouping match, which is what makes the number meaningful.

    This is the fallback, not the preferred path. Prefer
    :func:`fedcourtsai.pipeline.base_rates.prediction_base_rate` wherever the
    cell froze its own conditioning;
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
    every published skill number — as the walker's coverage changes. It bounds
    the interim arm's pool identically.
    """
    application_term = scotus_application_term_year(row.docket_number)
    if application_term is not None:
        return interim_base_rate(application_term, statpack, lookback_terms=lookback_terms)
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


def vote_accuracy(prediction: Prediction, outcome: Outcome) -> float | None:
    """Fraction of predicted votes that matched, over the Justices both name.

    ``None`` on every event the moments table does not declare a **merits**
    moment — :func:`fedcourtsai.pipeline.moments.scores_votes` is the gate, and
    it is checked before the vote lists are so much as read. A cert vote is
    never scored however visible it is (``docs/decision-model.md``), and the
    guard is structural rather than a property of the record: an ingestion
    channel that starts writing ``Outcome.votes`` on a cert outcome changes
    nothing here. The vote block a non-merits cell submits is banked, unscored.

    Where the gate opens, scoring is intersection-only: over the Justices the
    outcome actually records, so a Justice whose vote was never observed costs a
    predictor nothing — the denominator is what the record discloses, never what
    the predictor attempted. ``Outcome.vote_provenance`` is what says whether a
    short list means "only these are public" or "nobody looked"; this function
    needs only the intersection either way.
    """
    if not scores_votes(prediction.event_id):
        return None
    if not prediction.votes or not outcome.votes:
        return None
    actual = {v.justice: v.vote for v in outcome.votes}
    scored = [v for v in prediction.votes if v.justice in actual]
    if not scored:
        return None
    hits = sum(1 for v in scored if actual[v.justice] == v.vote)
    return hits / len(scored)
