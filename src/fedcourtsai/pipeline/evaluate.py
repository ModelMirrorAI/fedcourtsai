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

from typing import Final

from ..corpus import CorpusRow, scotus_application_term_year, scotus_term_year
from ..process_version import scores_finer_interim_reading
from ..schemas import GRANTED_DISPOSITIONS, Outcome, Prediction, StatPack, VoteValue

# `merits_base_rate` is re-exported, not used here — see the module docstring
# and `__all__`, which is what states the re-export to both linters.
from .base_rates import (
    InterimPoolReading,
    _pooled_band_rate,
    interim_base_rate,
    merits_base_rate,
)
from .justices import normalize_justice_name
from .moments import scores_votes
from .salience import SALIENCE_VERSION, salience_band, scorer

# The module's public surface — including `merits_base_rate`, re-exported from
# `base_rates` so the whole set of names an evaluator is told to match resolves
# under the one module the prompt gives it (see the module docstring).
__all__ = [
    "bench_vote_accuracy",
    "brier_score",
    "brier_skill",
    "brier_skill_score",
    "interim_base_rate",
    "is_correct",
    "judgment_correct",
    "merits_base_rate",
    "scored_granted",
    "scores_finer_reading",
    "segment_base_rate",
    "stage_brier_score",
    "stage_correct",
    "vote_accuracy",
]


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


def scores_finer_reading(prediction: Prediction | None) -> bool:
    """Whether an interim cell's scored ``prediction`` takes the finer interim reading.

    Keyed on the label the prediction was stamped under
    (:func:`fedcourtsai.process_version.scores_finer_interim_reading`), never on
    the grading's: the predict prompt a cell answered states what its
    probability means, so a re-grade under a later label never moves a cell onto
    a target it was not asked about.
    """
    if prediction is None or prediction.process_version is None:
        return False
    return scores_finer_interim_reading(prediction.process_version.label)


def scored_granted(prediction: Prediction, outcome: Outcome, *, interim: bool) -> int | None:
    """The binary ``prediction`` is scored against, or ``None`` where it is unscored.

    ``outcome.actual_granted`` everywhere except an **interim** cell whose
    prediction takes the finer reading (:func:`scores_finer_reading`), which is
    scored against ``outcome.interim_granted``: a partial grant is a grant, and
    an application dismissed or denied as moot — or an outcome recorded before
    the finer reading was stored — is ``None``, unscored rather than scored on a
    reading the cell was not asked about. ``interim`` is the caller's: the
    event's stage, which neither artifact records.
    """
    if interim and scores_finer_reading(prediction):
        return outcome.interim_granted
    return outcome.actual_granted


def stage_correct(prediction: Prediction, outcome: Outcome, *, interim: bool) -> int | None:
    """:func:`is_correct`, unless the finer interim reading scores the cell.

    Under the finer reading ``correct`` follows the binary rather than the
    label: 1 iff the predicted disposition is on the same side of the
    granted/ungranted line as ``interim_granted`` (a predicted ``granted``
    against a ``granted-in-part`` reading is correct, a predicted ``dismissed``
    against a ``withdrawn`` one is too), so the accuracy column and the Brier
    score the same event. ``None`` where the cell is unscored.
    """
    if not (interim and scores_finer_reading(prediction)):
        return is_correct(prediction, outcome)
    target = outcome.interim_granted
    if target is None:
        return None
    return int((prediction.predicted_disposition in GRANTED_DISPOSITIONS) == bool(target))


def stage_brier_score(prediction: Prediction, outcome: Outcome, *, interim: bool) -> float | None:
    """:func:`brier_score` against :func:`scored_granted`, ``None`` where unscored."""
    target = scored_granted(prediction, outcome, interim=interim)
    if target is None:
        return None
    return (prediction.probability - target) ** 2


def brier_score(prediction: Prediction, outcome: Outcome) -> float:
    """Brier score for the stage's declared binary forecast (lower is better).

    ``actual_granted`` carries the stage's binary — granted on a cert/interim
    event, judgment-disturbed on a merits event — and ``probability`` states
    the matching P, so one formula scores every stage.
    """
    return (prediction.probability - outcome.actual_granted) ** 2


def segment_base_rate(
    row: CorpusRow,
    statpack: StatPack,
    *,
    lookback_terms: int = 0,
    reading: InterimPoolReading = "registered",
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
    **now**, and ``None`` for a row outside the active version's segment
    (:meth:`~fedcourtsai.pipeline.salience.SalienceScorer.in_segment`). For a
    resolved case that is its *terminal* band, so this pools ``est_grant_rate`` —
    the rate over rows that ended in the band. Baseline and grouping match, which
    is what makes the number meaningful.

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

    ``reading`` reaches the interim arm alone: ``"finer"`` is the pool for a
    cell whose scored prediction takes the finer interim reading
    (:func:`scores_finer_reading`), and the cert and merits arms ignore it.
    """
    application_term = scotus_application_term_year(row.docket_number)
    if application_term is not None:
        return interim_base_rate(
            application_term, statpack, lookback_terms=lookback_terms, reading=reading
        )
    term = scotus_term_year(row.docket_number)
    if term is None:
        return None
    # A row outside the active version's segment has no band under it, so no
    # band rate: the frozen cell band refuses the same row
    # (`cell_context.build`).
    if not scorer().in_segment(row):
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


#: The vote values that record a Justice as not sitting.
NOT_SITTING: Final = frozenset({VoteValue.recused, VoteValue.did_not_participate})


def bench_vote_accuracy(prediction: Prediction, outcome: Outcome) -> float | None:
    """Fraction of the participating bench whose vote the prediction called.

    The figure ``mean_vote_accuracy`` averages, recomputed from the scored
    prediction and the committed outcome rather than read off the evaluator's
    ``vote_accuracy``. Null unless the event is a declared merits moment
    (:func:`fedcourtsai.pipeline.moments.scores_votes`) **and** the outcome's
    ``vote_provenance`` says ``complete: true``.

    The denominator is every Justice the complete record shows sitting —
    everyone but ``recused`` and ``did-not-participate`` — so it is the same
    for every predictor on the event and no predictor can choose it: a sitting
    Justice the prediction omits, or names in a way no roster surname can be
    read from, is a miss, and a prediction entry for a Justice who did not sit
    scores nothing either way. Predicted names are read through
    :func:`fedcourtsai.pipeline.justices.normalize_justice_name`, so "Samuel A.
    Alito, Jr." and "Alito" are one Justice; a Justice the prediction names
    twice with different votes has no single call and counts as a miss.
    """
    if not scores_votes(prediction.event_id):
        return None
    provenance = outcome.vote_provenance
    if provenance is None or not provenance.complete:
        return None
    sitting = {v.justice: v.vote for v in outcome.votes if v.vote not in NOT_SITTING}
    if not sitting:
        return None
    calls: dict[str, VoteValue | None] = {}
    for vote in prediction.votes:
        name = normalize_justice_name(vote.justice)
        if name is None:
            continue
        calls[name] = vote.vote if calls.get(name, vote.vote) == vote.vote else None
    hits = sum(1 for justice, vote in sitting.items() if calls.get(justice) == vote)
    return hits / len(sitting)


def vote_accuracy(prediction: Prediction, outcome: Outcome) -> float | None:
    """Fraction of predicted votes that matched, over the Justices both name.

    ``None`` on every event the moments table does not declare a **merits**
    moment — :func:`fedcourtsai.pipeline.moments.scores_votes` is the gate, and
    it is checked before the vote lists are so much as read. A cert vote is
    never scored however visible it is (``docs/decision-model.md``), and the
    guard is structural rather than a property of the record: an ingestion
    channel that starts writing ``Outcome.votes`` on a cert outcome changes
    nothing here. The vote block a non-merits cell submits is banked, unscored.

    The second gate is **completeness**: only an outcome whose
    ``vote_provenance`` says ``complete: true`` is scored, so every scored cell
    is scored against the whole participating bench. A partial list — the
    Justices a source happened to show — would score a predictor over a subset
    chosen by the source rather than by the case, and a one-of-one match would
    weigh the same in the mean as nine of nine; an unprovenanced list says
    nothing about how much of the bench it holds. Either is null here.

    Where both gates open, scoring is over the Justices both lists name, as the
    evaluate prompt defines the field. That leaves the denominator partly the
    predictor's choice, which is why the leaderboard does not average this
    field: it recomputes :func:`bench_vote_accuracy`, whose denominator is the
    participating bench.
    """
    if not scores_votes(prediction.event_id):
        return None
    if outcome.vote_provenance is None or not outcome.vote_provenance.complete:
        return None
    if not prediction.votes or not outcome.votes:
        return None
    actual = {v.justice: v.vote for v in outcome.votes}
    scored = [v for v in prediction.votes if v.justice in actual]
    if not scored:
        return None
    hits = sum(1 for v in scored if actual[v.justice] == v.vote)
    return hits / len(scored)
