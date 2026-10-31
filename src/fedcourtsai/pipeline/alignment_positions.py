"""Justice positions estimated from the corpus's own merits lineups, for baseline 4.

``docs/merits-alignment-baseline.md`` places each Justice on one ideological
line for the score-votes baseline (:mod:`.alignment_score`). This module
estimates that line from the complete merits lineups (:mod:`.merits_lineups`)
rather than reading a published ordering:

- **Agreement.** Over the decisions of a window of Terms, each keyed to the
  Term it was decided in, two Justices agree on a decision when both took
  part and both sat with the judgment or both in dissent. Two dissents count
  as agreement even when they dissent from opposite directions, which pulls
  the ends of the line together. A vote in part on each side, and a Justice who did not take part,
  leave the decision out of that pair's count.
- **Scaling.** The disagreement rate is the distance between two Justices, and
  the positions are its one-dimensional classical scaling: the leading
  eigenvector of the double-centred squared distances, scaled by the root of
  its eigenvalue (:func:`classical_scaling`). Only the order and the spacing
  matter downstream, since baseline 4 standardizes over each bench.
- **Orientation.** The line's sign is arbitrary, so it is turned to put the
  conservative bloc's mean above the other bloc's
  (:data:`~.alignment_baseline.CONSERVATIVE_BLOC`). That fixes only which end
  is called conservative; where each Justice sits is the votes' own.
- **Which Justices, which Terms.** Term ``t``'s positions are fitted on the
  decisions of Terms ``t - WINDOW_TERMS + 1`` through ``t``, for the Justices
  who took part in at least :data:`MIN_JUSTICE_DECISIONS` of them and in some
  decision of Term ``t``, every pair of whom shares at least
  :data:`MIN_PAIR_DECISIONS` decisions. A Term with no such bench of two or
  more has no positions.
- **Release dating** (:func:`estimated_positions`). Each Term's positions are
  published as a release dated the day before the next Term opens, since
  they read only decisions of Terms up to their own. So an out-of-sample
  reading of Term ``T`` takes Term ``T - 1``'s positions, fitted on nothing
  decided in Term ``T``, and the in-sample ceiling takes Term ``T``'s own.

Read-only and a pure function of the lineups.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Iterable, Mapping, Sequence
from datetime import date
from typing import Final

from ..schemas import VoteValue
from ..supremecourt import october_term_year
from .alignment_baseline import CONSERVATIVE_BLOC
from .alignment_score import JusticePositions, PositionsRelease
from .merits_lineups import MeritsLineup

#: How many Terms, ending with its own, one Term's positions are fitted on.
#: One Term holds some fifty complete lineups, too few to place a Justice
#: near the middle of the bench; three hold enough without reaching back past
#: the bench's recent alignment.
WINDOW_TERMS: Final = 3

#: The fewest window decisions a Justice must have taken part in to be placed.
MIN_JUSTICE_DECISIONS: Final = 20

#: The fewest window decisions every pair on a bench must share.
MIN_PAIR_DECISIONS: Final = 10

#: The power iteration's step limit and convergence tolerance.
_ITERATIONS: Final = 1000
_TOLERANCE: Final = 1e-12

_WITH_JUDGMENT: Final = frozenset({VoteValue.majority, VoteValue.concur_in_judgment})

SOURCE: Final = (
    f"estimated from the corpus's complete merits lineups: one-dimensional classical scaling "
    f"of vote disagreement over a trailing {WINDOW_TERMS}-Term window"
)


def _sides(lineup: MeritsLineup) -> dict[str, bool]:
    """Each Justice's side on one decision: True with the judgment, False in dissent.

    A Justice who did not take part, or voted in part on each side, has none.
    """
    sides: dict[str, bool] = {}
    for vote in lineup.votes:
        value = VoteValue(vote.vote)
        if value in _WITH_JUDGMENT:
            sides[vote.justice] = True
        elif value == VoteValue.dissent:
            sides[vote.justice] = False
    return sides


def classical_scaling(distance: Sequence[Sequence[float]]) -> list[float]:
    """The one-dimensional classical scaling of a symmetric distance matrix.

    The leading eigenvector of ``-1/2 J D^2 J`` (``J`` the centring matrix),
    found by power iteration on the matrix shifted to be positive semidefinite,
    times the root of its eigenvalue. A matrix with no positive eigenvalue
    places every point at 0.
    """
    n = len(distance)
    squared = [[d * d for d in row] for row in distance]
    row_means = [statistics.fmean(row) for row in squared]
    grand = statistics.fmean(row_means)
    b = [
        [-0.5 * (squared[i][j] - row_means[i] - row_means[j] + grand) for j in range(n)]
        for i in range(n)
    ]
    # Shifting by the largest absolute row sum bounds every eigenvalue below
    # by zero, so the dominant eigenvector of the shifted matrix is the
    # leading one of the original.
    shift = max(sum(abs(x) for x in row) for row in b)
    vector = [1.0 + i / n for i in range(n)]
    for _ in range(_ITERATIONS):
        product = [sum(b[i][j] * vector[j] for j in range(n)) + shift * vector[i] for i in range(n)]
        norm = math.sqrt(sum(x * x for x in product))
        if norm == 0:
            return [0.0] * n
        vector = [x / norm for x in product]
        # Stop on the eigen-residual, not the step: a step shrinks slowly
        # when the leading eigenvalues are close, long before it is small.
        bv = [sum(b[i][j] * vector[j] for j in range(n)) for i in range(n)]
        rayleigh = sum(v * w for v, w in zip(vector, bv, strict=True))
        if sum((w - rayleigh * v) ** 2 for v, w in zip(vector, bv, strict=True)) < _TOLERANCE:
            break
    eigenvalue = sum(vector[i] * sum(b[i][j] * vector[j] for j in range(n)) for i in range(n))
    if eigenvalue <= 0:
        return [0.0] * n
    root = math.sqrt(eigenvalue)
    return [x * root for x in vector]


def term_positions(lineups: Iterable[MeritsLineup], term: int) -> dict[str, float]:
    """Term ``term``'s positions, fitted on its window of complete lineups."""
    # Keyed on the Term each decision was entered in, as the scoring keys it,
    # so no release carries a decision made after its date.
    decisions = [
        (october_term_year(lu.decided), _sides(lu))
        for lu in lineups
        if lu.status == "complete" and term - WINDOW_TERMS < october_term_year(lu.decided) <= term
    ]
    sat = {j for t, sides in decisions if t == term for j in sides}
    counts = {j: sum(j in sides for _, sides in decisions) for j in sat}
    bench = sorted(j for j in sat if counts[j] >= MIN_JUSTICE_DECISIONS)
    shared: dict[tuple[str, str], tuple[int, int]] = {}
    while len(bench) >= 2:
        shared = {}
        for a in bench:
            for b in bench:
                if a < b:
                    both = [s for _, s in decisions if a in s and b in s]
                    shared[(a, b)] = (len(both), sum(s[a] == s[b] for s in both))
        thin = {j for pair, (n, _) in shared.items() if n < MIN_PAIR_DECISIONS for j in pair}
        if not thin:
            break
        # Drop the thinly shared Justice with the fewest decisions and retry.
        bench.remove(min(thin, key=lambda j: (counts[j], j)))
    if len(bench) < 2:
        return {}
    index = {j: i for i, j in enumerate(bench)}
    distance = [[0.0] * len(bench) for _ in bench]
    for (a, b), (n, agree) in shared.items():
        distance[index[a]][index[b]] = distance[index[b]][index[a]] = 1 - agree / n
    placed = dict(zip(bench, classical_scaling(distance), strict=True))
    conservative = [x for j, x in placed.items() if j in CONSERVATIVE_BLOC]
    other = [x for j, x in placed.items() if j not in CONSERVATIVE_BLOC]
    if conservative and other and statistics.fmean(conservative) < statistics.fmean(other):
        placed = {j: -x for j, x in placed.items()}
    return placed


def estimated_positions(
    lineups: Sequence[MeritsLineup], *, first_term: int, last_term: int
) -> JusticePositions:
    """Positions for every Term from ``first_term`` to ``last_term``, release by release.

    Term ``t``'s release is dated 30 September of ``t + 1``, the day before
    the earliest the next Term could open, and carries every Term's positions
    through ``t``, so the latest release serves the in-sample ceiling and each
    earlier one only what was decided by its date.
    """
    terms: dict[int, dict[str, float]] = {}
    releases = []
    for term in range(first_term, last_term + 1):
        placed = term_positions(lineups, term)
        if placed:
            terms[term] = placed
        releases.append(PositionsRelease(published=date(term + 1, 9, 30), terms=dict(terms)))
    return JusticePositions(source=SOURCE, releases=releases)


def bench_order(positions: Mapping[str, float]) -> list[str]:
    """A Term's Justices from most to least conservative."""
    return sorted(positions, key=lambda j: (-positions[j], j))
