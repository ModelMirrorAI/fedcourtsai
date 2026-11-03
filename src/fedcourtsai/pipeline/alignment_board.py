"""The coded score baselines, read on the leaderboard's merits cells from the frozen fits.

``docs/merits-alignment-baseline.md`` (*The coded baselines on the board*)
specifies them. The leaderboard reads only committed records, so baselines 3
and 4 reach a merits cell through two committed artifacts: the side codes
(``data/merits-alignment/alignment-side-codes.json``) and the frozen per-Term
fits (``data/merits-alignment/alignment-fits.json``, :mod:`.alignment_fits`).

A cell is read only where the reading is **pre-registered**: its case carries
a clean code (:func:`.alignment_side.is_clean`, read without the argument
date, which the committed record does not carry, so the board's clean set
holds the clean check's and any expedited case coded after an argument held
inside the lag) made before the decision, and its decision Term has a fit with
a transform, made before the decision. Baseline 4 needs the transform too: its
vote model reads the transformed score, as its spread was fitted at it.
Every other cell has no reading; a backtest is the readout's
(``fedcourts alignment-score-baseline``), never the board's.

- **Baseline 3** is the Brier of the transformed score on the cell's own
  binary, P(disturbed): the transformed P(the conservative side prevails)
  where the conservative side is the petitioner, and its complement where it
  is the respondent.
- **Baseline 4** is the exact-vote accuracy of the vote model's calls on the
  cell's outcome, under the leaderboard's rule
  (:func:`.evaluate.bench_vote_accuracy`): every Justice the outcome shows
  sitting is in the denominator, and a Justice is called ``majority`` when
  predicted on the predicted winner's side and ``dissent`` otherwise, so a
  realized ``concur-in-judgment`` or vote in part is a miss.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ..schemas import (
    AlignmentFits,
    AlignmentSide,
    AlignmentSideCode,
    AlignmentSideCodes,
    AlignmentTermFit,
    Outcome,
    VoteValue,
)
from ..serialize import read_model
from ..supremecourt import october_term_year
from .alignment_fits import calibration_of, fits_path
from .alignment_score import predicted_conservative, standardize
from .alignment_side import codes_path, is_clean
from .evaluate import NOT_SITTING
from .justices import normalize_justice_name


@dataclass(frozen=True)
class AlignmentInputs:
    """The committed side codes by case and the frozen fits by Term."""

    codes: dict[str, AlignmentSideCode]
    fits: dict[int, AlignmentTermFit]


def load_inputs(data_root: Path) -> AlignmentInputs | None:
    """The committed codes and fits, or None where either file is absent."""
    codes_file, fits_file = codes_path(data_root), fits_path(data_root)
    if not codes_file.is_file() or not fits_file.is_file():
        return None
    return AlignmentInputs(
        codes={c.case_id: c for c in read_model(codes_file, AlignmentSideCodes).entries},
        fits={f.term: f for f in read_model(fits_file, AlignmentFits).entries},
    )


@dataclass(frozen=True)
class AlignmentReading:
    """Baselines 3 and 4 on one merits cell's outcome, and the fit they were read under."""

    #: Baseline 3's Brier on the cell's disturbed binary.
    brier: float
    #: Baseline 4's exact-vote accuracy, or None where the fit has no spread or
    #: the outcome seats a Justice the fit's positions do not place.
    vote_accuracy: float | None
    term: int
    #: The fit's contamination-risk share: of the codes its transform read,
    #: the fraction made after their own decisions.
    fit_replay_share: float


def _pre_registered(
    inputs: AlignmentInputs, case_id: str, decided: date
) -> tuple[AlignmentSideCode, AlignmentTermFit] | None:
    code = inputs.codes.get(case_id)
    fit = inputs.fits.get(october_term_year(decided))
    if code is None or fit is None or fit.transform is None:
        return None
    if not (is_clean(code, argued=None) and code.coded_at < decided and fit.frozen_on < decided):
        return None
    return code, fit


def _conservative_prevails_probability(code: AlignmentSideCode, fit: AlignmentTermFit) -> float:
    calibration = calibration_of(fit)
    assert calibration is not None  # _pre_registered requires a transform
    return calibration.apply(code.score)


def _vote_accuracy(
    code: AlignmentSideCode, fit: AlignmentTermFit, score: float, outcome: Outcome
) -> float | None:
    if fit.k is None or fit.positions is None:
        return None
    sitting: dict[str, VoteValue] = {}
    for vote in outcome.votes:
        if vote.vote in NOT_SITTING:
            continue
        justice = normalize_justice_name(vote.justice)
        # A duplicate is refused, not merged: the forecasts' figure counts each row.
        if justice is None or justice not in fit.positions or justice in sitting:
            return None
        sitting[justice] = vote.vote
    if not sitting:
        return None
    z = standardize({j: fit.positions[j] for j in sitting})
    predicted = predicted_conservative(score, z, fit.k)
    conservative_count = sum(predicted.values())
    # As the readout reads a decision: the side most calls take, and on an even
    # bench's tie the respondent, since an equally divided Court affirms.
    conservative_wins = conservative_count * 2 > len(predicted) or (
        conservative_count * 2 == len(predicted)
        and code.conservative_side == AlignmentSide.respondent
    )
    hits = sum(
        vote == (VoteValue.majority if predicted[j] == conservative_wins else VoteValue.dissent)
        for j, vote in sitting.items()
    )
    return hits / len(sitting)


def read_cell(
    inputs: AlignmentInputs, outcome: Outcome, *, votes_complete: bool
) -> AlignmentReading | None:
    """Baselines 3 and 4 on one merits outcome, or None where the reading is not pre-registered.

    ``votes_complete`` says whether the leaderboard vote-scores the outcome;
    baseline 4 is read only where it does, so it is paired with
    ``mean_vote_accuracy``'s own population.
    """
    joined = _pre_registered(inputs, outcome.case_id, outcome.resolved_at)
    if joined is None:
        return None
    code, fit = joined
    conservative = _conservative_prevails_probability(code, fit)
    disturbed = (
        conservative if code.conservative_side == AlignmentSide.petitioner else 1 - conservative
    )
    return AlignmentReading(
        brier=(disturbed - outcome.actual_granted) ** 2,
        vote_accuracy=_vote_accuracy(code, fit, conservative, outcome) if votes_complete else None,
        term=fit.term,
        fit_replay_share=fit.contamination_risk / fit.transform_decisions,
    )
