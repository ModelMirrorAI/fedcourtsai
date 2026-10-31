"""The coding-free merits alignment baselines, scored over the corpus's merits lineups.

A lay reader's floor for a merits vote forecast: "the Court splits along its
usual ideological lines", or "the Court agrees". ``docs/merits-alignment-baseline.md``
specifies the four baselines and the reading rule; this module is the two that
need no per-case coding:

- **Majority alignment** places every participating Justice of the
  conservative bloc with the judgment and every other participating Justice in
  dissent, whichever side wins. The bloc is a fixed rule, not an estimate: the
  Justices appointed by a Republican president (:data:`CONSERVATIVE_BLOC`). On
  the OT2025 bench that is the six named by the rule Stillwell & Harrington
  score ("six conservatives in the majority"), and on the benches before
  Justice Barrett it is the five of their day (Kennedy among them through
  OT2017).
- **Unanimity** places every participating Justice with the judgment: 9-0.

Neither predicts the outcome (which side wins), so neither has a Brier score;
they make vote claims only, and are read only on the claims they make.

**Three readings per decision**, over the participating bench (everyone but
``recused`` and ``did-not-participate``), the denominator every predictor on a
decision shares:

- *Justice accuracy*: the fraction of participating Justices whose side the
  baseline called, a side being with the judgment (``majority`` or
  ``concur-in-judgment``) or in dissent. A vote in part on each side
  (``concur-in-part-dissent-in-part``) has neither side and is a miss for
  every baseline, since none of them predicts it.
- *Exact split*: whether the predicted count with the judgment and in dissent
  is the realized one, with no vote in part.
- *Full coalition*: whether the predicted set of Justices with the judgment is
  the realized set, with no vote in part.

**The population** is the complete lineups (:mod:`.merits_lineups`): signed
decisions whose writings seat the whole bench on a filled bench row. Per
curiams and decisions the grammar could not seat are left out, which is
selection rather than missing at random, so each Term's figure travels with its
document count.

Read-only, and a pure function of the lineups: nothing is stored, and no cell,
score or board reads it.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

from ..schemas import VoteValue
from .justices import SERVICE
from .merits_lineups import MeritsLineup

#: The Justices appointed by a Republican president, over every Justice in
#: :data:`~.justices.SERVICE`. A new appointment adds its name here or to
#: :data:`OTHER_BLOC`, and a test holds the two to partitioning the roster.
CONSERVATIVE_BLOC: Final[frozenset[str]] = frozenset(
    {"Kennedy", "Thomas", "Roberts", "Alito", "Gorsuch", "Kavanaugh", "Barrett"}
)
#: The Justices appointed by a Democratic president, over the same roster.
OTHER_BLOC: Final[frozenset[str]] = frozenset(
    {"Ginsburg", "Breyer", "Sotomayor", "Kagan", "Jackson"}
)

Baseline = Literal["majority-alignment", "unanimity"]
#: Every coding-free baseline, in the order the readout prints them.
BASELINES: Final[tuple[Baseline, ...]] = ("majority-alignment", "unanimity")

_WITH_JUDGMENT: Final = frozenset({VoteValue.majority, VoteValue.concur_in_judgment})
_ABSENT: Final = frozenset({VoteValue.recused, VoteValue.did_not_participate})


def roster_is_partitioned() -> bool:
    """Whether every Justice in the service roster sits in exactly one bloc."""
    roster = {s.justice for s in SERVICE}
    return roster == CONSERVATIVE_BLOC | OTHER_BLOC and not CONSERVATIVE_BLOC & OTHER_BLOC


def _side(vote: VoteValue) -> bool | None:
    """True with the judgment, False in dissent, None for a vote in part on each side."""
    if vote in _WITH_JUDGMENT:
        return True
    if vote == VoteValue.dissent:
        return False
    if vote == VoteValue.concur_in_part:
        return None
    raise ValueError(f"no merits side for {vote}")


def predicted_sides(baseline: Baseline, participants: Iterable[str]) -> dict[str, bool]:
    """Each participating Justice's predicted side: True with the judgment, False in dissent.

    Raises ``ValueError`` on a Justice neither bloc names, so a roster change
    that misses this module is refused rather than read as a dissent.
    """
    sides: dict[str, bool] = {}
    for justice in participants:
        if justice not in CONSERVATIVE_BLOC and justice not in OTHER_BLOC:
            raise ValueError(f"no bloc for {justice!r}")
        sides[justice] = baseline == "unanimity" or justice in CONSERVATIVE_BLOC
    return sides


@dataclass(frozen=True)
class DecisionReading:
    """One baseline's three readings of one complete lineup."""

    participating: int
    justice_hits: int
    exact_split: bool
    full_coalition: bool


def read_decision(baseline: Baseline, lineup: MeritsLineup) -> DecisionReading:
    """Score ``baseline`` against one complete lineup's realized votes."""
    if lineup.status != "complete":
        raise ValueError(f"{lineup.term}/{lineup.listing_number}: not a complete lineup")
    actual: dict[str, bool | None] = {}
    for vote in lineup.votes:
        # The model stores enum values, so read the vote back into its enum.
        value = VoteValue(vote.vote)
        if value not in _ABSENT:
            actual[vote.justice] = _side(value)
    predicted = predicted_sides(baseline, actual)
    in_part = any(side is None for side in actual.values())
    realized_with = {j for j, side in actual.items() if side is True}
    predicted_with = {j for j, side in predicted.items() if side}
    return DecisionReading(
        participating=len(actual),
        justice_hits=sum(
            1 for j, side in actual.items() if side is not None and predicted[j] == side
        ),
        exact_split=not in_part and len(realized_with) == len(predicted_with),
        full_coalition=not in_part and realized_with == predicted_with,
    )


class BaselineReading(BaseModel):
    """One baseline's readings pooled over a set of decisions, counts beside each rate."""

    model_config = ConfigDict(extra="forbid")

    baseline: str
    justice_votes: int = Field(description="Participating Justice votes, the accuracy denominator")
    justice_hits: int
    justice_accuracy: float | None
    exact_split_hits: int
    exact_split_accuracy: float | None
    full_coalition_hits: int
    full_coalition_accuracy: float | None


class AlignmentTerm(BaseModel):
    """One October Term's realized vote shape and each baseline's readings over it."""

    model_config = ConfigDict(extra="forbid")

    term: int = Field(description="The October Term of the opinions listing")
    documents: int = Field(description="Every lineup the record derives for the Term")
    decisions: int = Field(description="Complete lineups: the scored population")
    unanimous: int = Field(description="Decisions with no vote in dissent, in full or in part")
    bloc_coalition: int = Field(
        description="Decisions whose with-the-judgment set is exactly the participating "
        "conservative bloc, with no vote in part: the shape majority alignment predicts"
    )
    with_other_bloc: int = Field(
        description="Decisions with at least one Justice outside the conservative bloc "
        "with the judgment"
    )
    readings: list[BaselineReading]


class AlignmentReadout(BaseModel):
    """The coding-free baselines over a range of Terms, per Term and pooled."""

    model_config = ConfigDict(extra="forbid")

    first_term: int
    last_term: int
    terms: list[AlignmentTerm] = Field(description="Most recent Term first")
    pooled: AlignmentTerm = Field(
        description="Every Term in the range summed; its `term` is the range's last Term"
    )


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _reading(baseline: Baseline, decisions: Sequence[MeritsLineup]) -> BaselineReading:
    readings = [read_decision(baseline, lu) for lu in decisions]
    votes = sum(r.participating for r in readings)
    hits = sum(r.justice_hits for r in readings)
    splits = sum(r.exact_split for r in readings)
    coalitions = sum(r.full_coalition for r in readings)
    return BaselineReading(
        baseline=baseline,
        justice_votes=votes,
        justice_hits=hits,
        justice_accuracy=_rate(hits, votes),
        exact_split_hits=splits,
        exact_split_accuracy=_rate(splits, len(readings)),
        full_coalition_hits=coalitions,
        full_coalition_accuracy=_rate(coalitions, len(readings)),
    )


def _term(term: int, members: Sequence[MeritsLineup]) -> AlignmentTerm:
    complete = [lu for lu in members if lu.status == "complete"]
    unanimous = 0
    with_other = 0
    for lu in complete:
        sides = {
            v.justice: _side(VoteValue(v.vote))
            for v in lu.votes
            if VoteValue(v.vote) not in _ABSENT
        }
        unanimous += all(side is True for side in sides.values())
        with_other += any(side is True and j in OTHER_BLOC for j, side in sides.items())
    readings = [_reading(baseline, complete) for baseline in BASELINES]
    return AlignmentTerm(
        term=term,
        documents=len(members),
        decisions=len(complete),
        unanimous=unanimous,
        # The decisions majority alignment calls in full are those whose coalition is the bloc.
        bloc_coalition=readings[BASELINES.index("majority-alignment")].full_coalition_hits,
        with_other_bloc=with_other,
        readings=readings,
    )


def alignment_readout(
    lineups: Sequence[MeritsLineup], *, first_term: int, last_term: int
) -> AlignmentReadout:
    """Score the coding-free baselines over ``lineups`` from ``first_term`` to ``last_term``."""
    in_range = [lu for lu in lineups if first_term <= lu.term <= last_term]
    by_term: Mapping[int, list[MeritsLineup]] = {
        term: [lu for lu in in_range if lu.term == term]
        for term in sorted({lu.term for lu in in_range}, reverse=True)
    }
    return AlignmentReadout(
        first_term=first_term,
        last_term=last_term,
        terms=[_term(term, members) for term, members in by_term.items()],
        pooled=_term(last_term, in_range),
    )
