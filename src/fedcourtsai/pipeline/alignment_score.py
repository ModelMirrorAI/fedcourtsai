"""The coded merits alignment baselines: score outcome (3) and score votes (4).

``docs/merits-alignment-baseline.md`` specifies the four baselines; this module
is the two that read the side codes (:mod:`.alignment_side`). Each code names
the party arguing the conservative position and a score ``s`` in [0, 1], read
as P(the conservative side prevails).

**Baseline 3, score outcome.** P(the conservative side prevails) is ``s``, and
``s > 0.5`` is the implied call. It is Brier-scored against the coded side's
result (:func:`conservative_prevailed`), which reads the merits binary every
merits cell is scored on: the petitioner prevails exactly when the judgment
below is disturbed (:func:`~.judgment.judgment_disturbed`), so a dismissal as
improvidently granted and an affirmance by an equally divided Court count for
the respondent, as they count as undisturbed there. That keeps the baseline's
binary one sign flip from a model's P(disturbed), so the two can be paired on
the same decisions. A **calibrated** variant applies a monotone transform of
``s`` (:func:`fit_calibration`, isotonic by pool-adjacent-violators, each
block's rate Laplace-smoothed so no score maps to certainty).

**Baseline 4, score votes.** Each Justice carries a fixed position ``x`` on
one ideological line (:class:`JusticePositions`, larger is more
conservative; estimated from the merits lineups by
:mod:`.alignment_positions`, or read from a file), standardized over the
participating bench (:func:`standardize`).
One spread parameter ``k`` maps ``s`` to each Justice's vote:

    P(Justice j votes for the conservative side) = sigmoid(logit(s) + k * z_j)

``k = 0`` gives every Justice the same call, a 9-0, and a large ``k`` splits
the bench along the ordering at a cut ``s`` moves, so the splits fall between.
The predicted winner is the side a majority of the predicted votes takes, and
a Justice is predicted with the judgment exactly when on that side, so the
baseline is read on the same three readings as the coding-free baselines
(:func:`read_vote_decision`). ``k`` is chosen from :data:`K_GRID` to maximize
the vote log-likelihood of the fit's decisions (:func:`fit_spread`).

**Out of sample and in sample.** For a scored Term ``T``, out of sample fits
the transform and ``k`` on decisions of Terms before ``T`` only, and reads each
Justice's position from Term ``T - 1`` in a release published before Term
``T`` opened (:meth:`JusticePositions.prior_bench`): an ideal point estimated
with Term ``T``'s own votes would carry that Term's outcomes. In sample fits
both on Term ``T`` itself with Term ``T``'s positions in the latest release, a
labeled ceiling no forecast could have used. "Out of sample" governs the fits
only: a replay code's ``s`` was made after its case was decided, which the
contamination-risk counts disclose. A consolidated decision is read once, under
one code (:func:`consolidated_duplicates`). A fit with fewer than
:data:`MIN_FIT_DECISIONS` decisions is not made, and its reading is null rather
than a fit on noise.

Every code a fit reads is counted beside it by its contamination-risk flag and
its valence, so a fit resting on replay codes, or a ``k`` pulled toward 9-0 by
cases with no ideological content, shows in the readout.

Read-only, and a pure function of the codes, the corpus's merits judgments and
the merits lineups: nothing is stored, and no cell, score or board reads it.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from ..schemas import (
    AlignmentSide,
    AlignmentSideCode,
    AlignmentValence,
    Judgment,
    VoteValue,
)
from ..supremecourt import october_term_year
from .judgment import judgment_disturbed
from .merits_lineups import MeritsLineup

#: The fewest decisions a transform or a spread is fitted on. Below it the
#: reading is null: an isotonic step or a grid optimum on a handful of
#: decisions describes those decisions, not a Term's alignment.
MIN_FIT_DECISIONS: Final = 30

#: The spreads ``k`` the fit chooses among, in steps of 0.25 from 0 (every
#: Justice the same call) to 8, past which a standardized bench is already
#: split by the ordering at every score the codes give.
K_GRID: Final[tuple[float, ...]] = tuple(i / 4 for i in range(33))

#: Scores are clipped this far inside [0, 1] before the logit, so a code of
#: exactly 0 or 1 gives a finite vote probability.
_EPS: Final = 1e-6

_WITH_JUDGMENT: Final = frozenset({VoteValue.majority, VoteValue.concur_in_judgment})
_ABSENT: Final = frozenset({VoteValue.recused, VoteValue.did_not_participate})


def conservative_prevailed(code: AlignmentSideCode, judgment: Judgment) -> bool:
    """Whether the coded conservative side prevailed on the merits binary."""
    return judgment_disturbed(judgment) == (code.conservative_side == AlignmentSide.petitioner)


@dataclass(frozen=True)
class OutcomeCase:
    """One coded case joined to its merits judgment."""

    case_id: str
    term: int
    score: float
    conservative_prevailed: bool
    contamination_risk: bool
    valence: AlignmentValence
    conservative_side: AlignmentSide


def outcome_cases(
    codes: Iterable[AlignmentSideCode],
    judgments: Mapping[str, tuple[Judgment, date]],
) -> list[OutcomeCase]:
    """Every coded case with a merits judgment, keyed to its decision Term.

    ``judgments`` maps a case id to its corpus row's ``merits_judgment`` and
    ``merits_decided``. A coded case not yet decided, or ended by a termination
    that leaves the judgment null, has no outcome and is left out.
    """
    cases = []
    for code in codes:
        decided = judgments.get(code.case_id)
        if decided is None:
            continue
        judgment, on = decided
        cases.append(
            OutcomeCase(
                case_id=code.case_id,
                term=october_term_year(on),
                score=code.score,
                conservative_prevailed=conservative_prevailed(code, judgment),
                contamination_risk=code.contamination_risk,
                valence=code.valence,
                conservative_side=code.conservative_side,
            )
        )
    return sorted(cases, key=lambda c: (c.term, c.case_id))


def consolidated_duplicates(
    lineups: Iterable[MeritsLineup],
    codes: Iterable[AlignmentSideCode],
    decided: Iterable[str] = (),
) -> set[str]:
    """The coded cases a consolidated decision already reads under another code.

    A decision listed with several docket numbers is one decision, so each
    reading takes it once: under its case link's code where that is coded,
    else under the code of the first docket the listing prints, a ``decided``
    case (one with a merits judgment) before an undecided one. Every other
    coded docket of the listing is returned, to be left out, whatever side
    its code calls. Read over every lineup, complete or not, since baseline 3
    reads per curiams too.
    """
    by_docket = {c.docket_number: c.case_id for c in codes}
    coded = set(by_docket.values())
    done = set(decided)
    dropped: set[str] = set()
    for lineup in lineups:
        members = [by_docket[d] for d in lineup.dockets if d in by_docket]
        if lineup.case_id in coded:
            members = [lineup.case_id, *(m for m in members if m != lineup.case_id)]
        keep = next((m for m in members if m in done), next(iter(members), None))
        dropped.update(m for m in members if m != keep)
    return dropped


@dataclass(frozen=True)
class Calibration:
    """A monotone non-decreasing step transform of ``s``, fitted by isotonic regression.

    ``knots`` are the fitted blocks as (lowest score in the block, the block's
    rate), in increasing score order. A score maps to the rate of the last
    block starting at or below it, and a score below every block to the first
    block's rate.
    """

    knots: tuple[tuple[float, float], ...]
    decisions: int

    def apply(self, score: float) -> float:
        rate = self.knots[0][1]
        for start, value in self.knots:
            if start > score:
                break
            rate = value
        return rate


def fit_calibration(points: Sequence[tuple[float, bool]]) -> Calibration | None:
    """Isotonic regression of the outcome on ``s`` by pool-adjacent-violators.

    Ties in ``s`` are pooled into one block first, so the transform is a
    function of the score, and each block's rate is Laplace-smoothed. None
    below :data:`MIN_FIT_DECISIONS` points.
    """
    if len(points) < MIN_FIT_DECISIONS:
        return None
    by_score: dict[float, list[bool]] = {}
    for score, outcome in points:
        by_score.setdefault(score, []).append(outcome)

    # Each block's rate is shrunk one success and one failure toward a half
    # (Laplace), so no fitted rate is 0 or 1: a transform that maps a score to
    # certainty would make every Justice's vote probability in baseline 4
    # certain whatever ``k``, and a Brier on a handful of decisions would
    # reward a step that happened to be pure. The pooling compares the
    # smoothed rates themselves, since smoothing raw blocks of unequal size
    # after pooling can reorder them.
    def rate(block: list[float]) -> float:
        return (block[1] + 1) / (block[2] + 2)

    # Each block: [lowest score, sum of outcomes, count].
    blocks: list[list[float]] = []
    for score in sorted(by_score):
        outcomes = by_score[score]
        blocks.append([score, float(sum(outcomes)), float(len(outcomes))])
        while len(blocks) > 1 and rate(blocks[-2]) > rate(blocks[-1]):
            last = blocks.pop()
            blocks[-1][1] += last[1]
            blocks[-1][2] += last[2]
    return Calibration(
        knots=tuple((block[0], rate(block)) for block in blocks),
        decisions=len(points),
    )


def brier(pairs: Iterable[tuple[float, bool]]) -> float | None:
    """The mean squared error of probabilities against outcomes; None on no pairs."""
    errors = [(p - float(y)) ** 2 for p, y in pairs]
    return statistics.fmean(errors) if errors else None


class PositionsRelease(BaseModel):
    """One dated release of a set of Justice positions."""

    model_config = ConfigDict(extra="forbid")

    published: date = Field(description="The day the release was published")
    terms: dict[int, dict[str, float]] = Field(
        description="October Term to each sitting Justice's position in that Term, larger "
        "more conservative"
    )


class JusticePositions(BaseModel):
    """Justice positions on one ideological line, release by release.

    Releases are kept apart because a dynamic estimate is revised as later
    Terms are added: a release published after Term ``T`` opened may already
    carry Term ``T``'s votes in its Term ``T - 1`` positions, so an
    out-of-sample reading takes its positions only from a release published
    before its Term opened (:meth:`prior_bench`).
    """

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1, description="Where the positions come from")
    releases: list[PositionsRelease] = Field(min_length=1)

    def prior_bench(self, term: int) -> dict[str, float] | None:
        """Term ``term - 1``'s positions in the latest release published before ``term`` opened.

        A Term opens on the first Monday of October; 1 October is taken as its
        opening, which only ever excludes a release that was in time.
        """
        opened = date(term, 10, 1)
        prior = [r for r in self.releases if r.published < opened]
        if not prior:
            return None
        return max(prior, key=lambda r: r.published).terms.get(term - 1)

    def bench(self, term: int) -> dict[str, float] | None:
        """Term ``term``'s positions in the latest release: the in-sample ceiling's."""
        return max(self.releases, key=lambda r: r.published).terms.get(term)


def standardize(positions: Mapping[str, float]) -> dict[str, float]:
    """Positions centered on the bench's median and scaled by its standard deviation.

    The median Justice sits at 0, so at ``s = 0.5`` the cut falls at the median
    whatever the ordering's own origin. A bench whose positions are all equal
    standardizes to all zeros.
    """
    values = list(positions.values())
    center = statistics.median(values)
    spread = statistics.pstdev(values)
    if spread == 0:
        return dict.fromkeys(positions, 0.0)
    return {justice: (x - center) / spread for justice, x in positions.items()}


def vote_probability(score: float, z: float, k: float) -> float:
    """P(a Justice at standardized position ``z`` votes for the conservative side)."""
    s = min(max(score, _EPS), 1 - _EPS)
    t = math.log(s / (1 - s)) + k * z
    if t >= 0:
        return 1 / (1 + math.exp(-t))
    e = math.exp(t)
    return e / (1 + e)


def predicted_conservative(score: float, z: Mapping[str, float], k: float) -> dict[str, bool]:
    """Each Justice's predicted vote: True for the conservative side."""
    return {justice: vote_probability(score, zj, k) > 0.5 for justice, zj in z.items()}


@dataclass(frozen=True)
class VoteCase:
    """One coded decision with a complete lineup and a position for every participant."""

    case_id: str
    term: int
    score: float
    conservative_prevailed: bool
    contamination_risk: bool
    valence: AlignmentValence
    conservative_side: AlignmentSide
    #: Each participating Justice's realized side: True with the judgment, False
    #: in dissent, None for a vote in part on each side.
    with_judgment: dict[str, bool | None]


def _side(vote: VoteValue) -> bool | None:
    if vote in _WITH_JUDGMENT:
        return True
    if vote == VoteValue.dissent:
        return False
    if vote == VoteValue.concur_in_part:
        return None
    raise ValueError(f"no merits side for {vote}")


def vote_cases(
    lineups: Iterable[MeritsLineup],
    outcomes: Iterable[OutcomeCase],
    codes: Iterable[AlignmentSideCode],
) -> list[VoteCase]:
    """Every complete lineup joined to its coded case's outcome.

    A lineup joins on its case link, or failing that on the first of its
    docket numbers a code carries, so a consolidated decision is read once,
    under one code. A lineup whose decision Term differs from the coded case's
    is not the coded decision and is left out.
    """
    by_case = {o.case_id: o for o in outcomes}
    by_docket = {c.docket_number: c.case_id for c in codes}
    cases: dict[str, VoteCase] = {}
    for lineup in lineups:
        if lineup.status != "complete":
            continue
        case_id = lineup.case_id if lineup.case_id in by_case else None
        if case_id is None:
            case_id = next(
                (by_docket[d] for d in lineup.dockets if by_docket.get(d) in by_case), None
            )
        if case_id is None:
            continue
        outcome = by_case[case_id]
        if october_term_year(lineup.decided) != outcome.term:
            continue
        sides = {
            v.justice: _side(VoteValue(v.vote))
            for v in lineup.votes
            if VoteValue(v.vote) not in _ABSENT
        }
        # The first lineup read for a case is the one kept, so a decision two
        # listing rows both resolve to is still read once.
        cases.setdefault(
            case_id,
            VoteCase(
                case_id=case_id,
                term=outcome.term,
                score=outcome.score,
                conservative_prevailed=outcome.conservative_prevailed,
                contamination_risk=outcome.contamination_risk,
                valence=outcome.valence,
                conservative_side=outcome.conservative_side,
                with_judgment=sides,
            ),
        )
    return sorted(cases.values(), key=lambda c: (c.term, c.case_id))


def conservative_votes(case: VoteCase) -> dict[str, bool]:
    """Each participant's realized party side, True for the conservative side; votes in part out."""
    return {
        justice: side == case.conservative_prevailed
        for justice, side in case.with_judgment.items()
        if side is not None
    }


def bench_z(case: VoteCase, positions: Mapping[str, float]) -> dict[str, float] | None:
    """The participating bench's standardized positions; None if any participant has none."""
    if any(justice not in positions for justice in case.with_judgment):
        return None
    return standardize({justice: positions[justice] for justice in case.with_judgment})


def fit_spread(
    cases: Sequence[tuple[float, dict[str, float], dict[str, bool]]],
) -> float | None:
    """The ``k`` in :data:`K_GRID` maximizing the vote log-likelihood; ties take the smaller.

    Each case is (the score the fit reads, the bench's standardized positions,
    each Justice's realized party side). None below :data:`MIN_FIT_DECISIONS`.
    """
    if len(cases) < MIN_FIT_DECISIONS:
        return None
    best_k, best_ll = K_GRID[0], -math.inf
    for k in K_GRID:
        ll = 0.0
        for score, z, votes in cases:
            for justice, conservative in votes.items():
                p = min(max(vote_probability(score, z[justice], k), _EPS), 1 - _EPS)
                ll += math.log(p if conservative else 1 - p)
        if ll > best_ll + 1e-12:
            best_k, best_ll = k, ll
    return best_k


@dataclass(frozen=True)
class VoteReading:
    """Baseline 4's three readings of one decision."""

    participating: int
    justice_hits: int
    exact_split: bool
    full_coalition: bool


def read_vote_decision(case: VoteCase, predicted: Mapping[str, bool]) -> VoteReading:
    """Read predicted party sides against the realized lineup, relative to the judgment.

    The predicted winner is the side most predicted votes take, and on an
    even bench's tie the respondent, since an equally divided Court leaves the
    judgment below standing. A Justice is predicted with the judgment exactly
    when predicted on the winner's side, so the readings are the coding-free
    baselines' own.
    """
    conservative_count = sum(predicted.values())
    winner = conservative_count * 2 > len(predicted) or (
        conservative_count * 2 == len(predicted)
        and case.conservative_side == AlignmentSide.respondent
    )
    predicted_with = {j for j, side in predicted.items() if side == winner}
    realized_with = {j for j, side in case.with_judgment.items() if side is True}
    in_part = any(side is None for side in case.with_judgment.values())
    return VoteReading(
        participating=len(case.with_judgment),
        justice_hits=sum(
            1
            for j, side in case.with_judgment.items()
            if side is not None and (j in predicted_with) == side
        ),
        exact_split=not in_part and len(predicted_with) == len(realized_with),
        full_coalition=not in_part and predicted_with == realized_with,
    )


class CodeMix(BaseModel):
    """How many of a set's codes carry the contamination-risk flag, and their valence."""

    model_config = ConfigDict(extra="forbid")

    codes: int
    contamination_risk: int
    clear: int
    weak: int
    none: int


def code_mix(cases: Iterable[OutcomeCase | VoteCase]) -> CodeMix:
    """Count a set's codes by the contamination-risk flag and by valence."""
    members = list(cases)
    return CodeMix(
        codes=len(members),
        contamination_risk=sum(c.contamination_risk for c in members),
        clear=sum(c.valence == AlignmentValence.clear for c in members),
        weak=sum(c.valence == AlignmentValence.weak for c in members),
        none=sum(c.valence == AlignmentValence.none for c in members),
    )


class OutcomeReading(BaseModel):
    """Baseline 3 over one Term's decided codes."""

    model_config = ConfigDict(extra="forbid")

    decisions: int = Field(description="Coded cases decided in the Term")
    conservative_prevailed: int
    call_hits: int = Field(description="Decisions whose implied call, s > 0.5, was right")
    brier_raw: float | None = Field(description="Brier score of s itself")
    brier_calibrated_out_of_sample: float | None = Field(
        description="Brier score of s after the transform fitted on earlier Terms; null when "
        "the earlier Terms hold too few decided codes"
    )
    fit_out_of_sample: CodeMix | None = Field(
        description="The codes the out-of-sample transform was fitted on"
    )
    brier_calibrated_in_sample: float | None = Field(
        description="Brier score after a transform fitted on this Term itself: a labeled ceiling"
    )
    scored: CodeMix


class VoteBaselineReading(BaseModel):
    """Baseline 4 over one Term's coded complete lineups, under one fit."""

    model_config = ConfigDict(extra="forbid")

    k: float | None = Field(description="The spread fitted; null when the fit was not made")
    k_at_grid_edge: bool = Field(
        description="The fitted spread is the grid's largest, so the likelihood may peak beyond it"
    )
    decisions: int = Field(
        description="Decisions read: those with a position for every participant"
    )
    justice_votes: int
    justice_hits: int
    justice_accuracy: float | None
    exact_split_hits: int
    exact_split_accuracy: float | None
    full_coalition_hits: int
    full_coalition_accuracy: float | None
    fit: CodeMix | None = Field(description="The decisions the spread was fitted on")


class ScoreTerm(BaseModel):
    """Baselines 3 and 4 over one October Term."""

    model_config = ConfigDict(extra="forbid")

    term: int
    outcome: OutcomeReading
    lineups: int = Field(description="Coded decisions in the Term with a complete lineup")
    votes_out_of_sample: VoteBaselineReading | None = Field(
        description="Null when no positions were given"
    )
    votes_in_sample: VoteBaselineReading | None = Field(
        description="A labeled ceiling: the spread, the transform and the positions all from "
        "this Term. Null when no positions were given"
    )


class ScoreReadout(BaseModel):
    """The coded baselines over a range of decision Terms."""

    model_config = ConfigDict(extra="forbid")

    first_term: int
    last_term: int
    positions_source: str | None
    codes: int = Field(description="Side codes read")
    decided: int = Field(
        description="Codes whose case has a merits judgment, every Term, a consolidated "
        "decision counted once"
    )
    consolidated: int = Field(
        description="Coded cases left out because a consolidated decision reads another "
        "of its dockets' codes"
    )
    terms: list[ScoreTerm] = Field(description="Most recent Term first")


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _outcome_term(term: int, cases: Sequence[OutcomeCase]) -> OutcomeReading:
    scored = [c for c in cases if c.term == term]
    earlier = [c for c in cases if c.term < term]
    out = fit_calibration([(c.score, c.conservative_prevailed) for c in earlier])
    inside = fit_calibration([(c.score, c.conservative_prevailed) for c in scored])
    return OutcomeReading(
        decisions=len(scored),
        conservative_prevailed=sum(c.conservative_prevailed for c in scored),
        call_hits=sum((c.score > 0.5) == c.conservative_prevailed for c in scored),
        brier_raw=brier((c.score, c.conservative_prevailed) for c in scored),
        brier_calibrated_out_of_sample=None
        if out is None
        else brier((out.apply(c.score), c.conservative_prevailed) for c in scored),
        fit_out_of_sample=None if out is None else code_mix(earlier),
        brier_calibrated_in_sample=None
        if inside is None
        else brier((inside.apply(c.score), c.conservative_prevailed) for c in scored),
        scored=code_mix(scored),
    )


def _fit_rows(
    cases: Sequence[VoteCase],
    bench_for: Callable[[int], Mapping[str, float] | None],
    calibration: Calibration | None,
) -> tuple[list[tuple[float, dict[str, float], dict[str, bool]]], list[VoteCase]]:
    """The spread fit's rows over ``cases``, each read at the positions ``bench_for`` its Term."""
    rows = []
    used = []
    for case in cases:
        bench = bench_for(case.term)
        if bench is None:
            continue
        z = bench_z(case, bench)
        if z is None:
            continue
        score = case.score if calibration is None else calibration.apply(case.score)
        rows.append((score, z, conservative_votes(case)))
        used.append(case)
    return rows, used


def _vote_reading(
    scored: Sequence[VoteCase],
    bench: Mapping[str, float] | None,
    k: float | None,
    calibration: Calibration | None,
    fit_cases: Sequence[VoteCase],
) -> VoteBaselineReading:
    readings = []
    if k is not None and bench is not None:
        for case in scored:
            z = bench_z(case, bench)
            if z is None:
                continue
            score = case.score if calibration is None else calibration.apply(case.score)
            readings.append(read_vote_decision(case, predicted_conservative(score, z, k)))
    votes = sum(r.participating for r in readings)
    hits = sum(r.justice_hits for r in readings)
    splits = sum(r.exact_split for r in readings)
    coalitions = sum(r.full_coalition for r in readings)
    return VoteBaselineReading(
        k=k,
        k_at_grid_edge=k == K_GRID[-1],
        decisions=len(readings),
        justice_votes=votes,
        justice_hits=hits,
        justice_accuracy=_rate(hits, votes),
        exact_split_hits=splits,
        exact_split_accuracy=_rate(splits, len(readings)),
        full_coalition_hits=coalitions,
        full_coalition_accuracy=_rate(coalitions, len(readings)),
        fit=None if k is None else code_mix(fit_cases),
    )


def score_readout(
    codes: Sequence[AlignmentSideCode],
    judgments: Mapping[str, tuple[Judgment, date]],
    lineups: Sequence[MeritsLineup],
    *,
    first_term: int,
    last_term: int,
    positions: JusticePositions | None = None,
) -> ScoreReadout:
    """Score baselines 3 and, given positions, 4 over decision Terms ``first_term``..``last_term``.

    Out-of-sample fits read every earlier decided code and every earlier
    lineup handed in, not only those in the range, so the range chooses what
    is scored and never what is fitted on; the caller hands in every lineup
    from the first coded decision Term, and none earlier.
    """
    dropped = consolidated_duplicates(lineups, codes, judgments)
    outcomes = [c for c in outcome_cases(codes, judgments) if c.case_id not in dropped]
    votes = vote_cases(lineups, outcomes, codes)
    terms = []
    for term in range(last_term, first_term - 1, -1):
        scored_votes = [c for c in votes if c.term == term]
        out_vote = in_vote = None
        if positions is not None:
            earlier = [c for c in outcomes if c.term < term]
            out_cal = fit_calibration([(c.score, c.conservative_prevailed) for c in earlier])
            rows, used = _fit_rows(
                [c for c in votes if c.term < term], positions.prior_bench, out_cal
            )
            out_vote = _vote_reading(
                scored_votes, positions.prior_bench(term), fit_spread(rows), out_cal, used
            )
            scored_outcomes = [c for c in outcomes if c.term == term]
            in_cal = fit_calibration([(c.score, c.conservative_prevailed) for c in scored_outcomes])
            rows, used = _fit_rows(scored_votes, positions.bench, in_cal)
            in_vote = _vote_reading(
                scored_votes, positions.bench(term), fit_spread(rows), in_cal, used
            )
        terms.append(
            ScoreTerm(
                term=term,
                outcome=_outcome_term(term, outcomes),
                lineups=len(scored_votes),
                votes_out_of_sample=out_vote,
                votes_in_sample=in_vote,
            )
        )
    return ScoreReadout(
        first_term=first_term,
        last_term=last_term,
        positions_source=None if positions is None else positions.source,
        codes=len(codes),
        decided=len(outcomes),
        consolidated=len(dropped),
        terms=terms,
    )
