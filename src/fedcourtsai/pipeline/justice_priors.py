"""Per-Justice merits priors: how each Justice has voted, over strictly earlier Terms.

A merits cell forecasts nine votes, while the statpack's merits section carries
only the docket-wide disturbed rate, so each engine fills the per-Justice gap
from its own memory. This module computes the same priors for every predictor
from the corpus, off the merits lineups (:mod:`.merits_lineups`) and the
decided case rows' parsed judgments, and nothing else.

**The population** is the complete lineups: signed decisions whose writings
seat every Justice on a filled bench row. Per curiams, unobserved and refused
documents carry no whole-bench vote and are counted only in the per-Term
``documents`` total, so a Term's coverage is readable beside its rates. The
selection is not at random: per curiams (summary reversals among them, which
lean toward disturbing) and fractured decisions the grammar could not seat
are the ones left out.

**Three tables, per Term and Justice:**

- *Majority*: of the decisions the Justice took part in, those where they voted
  with the judgment: ``majority`` or ``concur-in-judgment``. A vote in part on
  each side (``concur-in-part-dissent-in-part``) is in ``sat`` and in neither
  side, the same rule the lineup census splits by, so the majority rate's
  denominator holds the votes in part while the other two tables' do not.
- *Disturb*: of the decisions with a whole-side vote and a parsed judgment that
  is a plain ``affirmed``, ``reversed`` or ``vacated``, those where the Justice
  voted to disturb the judgment below: with the judgment where it was reversed
  or vacated, in dissent where it was affirmed. A mixed judgment
  (affirmed in part) has no single side to disturb on, and a DIG or an equally
  divided Court is a non-merits exit, so all three are left out, as is a
  decision whose case row carries no parsed judgment. That makes this axis
  narrower than the scored merits binary, which counts a DIG and an equally
  divided Court as undisturbed, so its rates are not comparable with the
  statpack's disturbed rate.
- *Pairwise agreement*: for each pair of Justices both voting a whole side on a
  decision, whether they voted the same side.

**Strictly prior.** :func:`pool_before` sums the Terms strictly before the
Term it is given, which for a merits forecast is the case's **grant** Term. A
table's Term is the opinions listing's, the Term of the decision, and a case is
decided at or after the Term it was granted in, so the pooled Terms never hold
the forecast case's own decision.

Read-only, and a pure function of the lineups and the case rows: nothing is
stored. The per-Term tallies ride in the statpack as its ``justice_votes``
section (:func:`justice_votes_section`), which a merits cell pools itself.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..schemas import (
    Judgment,
    StatPackJusticeVotes,
    StatPackJusticeVotesJustice,
    StatPackJusticeVotesPair,
    StatPackJusticeVotesTerm,
    VoteValue,
)
from .merits_lineups import MeritsLineup, merits_lineups, recorded_terms

#: The votes that side with the judgment.
_WITH_JUDGMENT: Final = frozenset({VoteValue.majority, VoteValue.concur_in_judgment})

#: The votes of a Justice who took no part.
_ABSENT: Final = frozenset({VoteValue.recused, VoteValue.did_not_participate})

#: The judgments a whole-side vote disturbs or leaves standing without ambiguity.
_DISTURBED: Final = frozenset({Judgment.reversed, Judgment.vacated})
_UNDISTURBED: Final = frozenset({Judgment.affirmed})

# Case ids per lookup, inside SQLite's bound-parameter limit.
_CHUNK: Final = 500


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class JusticeRate(_Strict):
    """One Justice's pooled rates, with the counts they are read off."""

    justice: str
    sat: int = Field(ge=0)
    majority: int = Field(ge=0)
    in_part: int = Field(ge=0)
    majority_rate: float | None = Field(description="`majority / sat`; None where `sat` is 0")
    disturb_eligible: int = Field(ge=0)
    disturb: int = Field(ge=0)
    disturb_rate: float | None = Field(
        description="`disturb / disturb_eligible`; None where the denominator is 0"
    )


class PairRate(_Strict):
    """One pair's pooled agreement rate, with its denominator."""

    justices: tuple[str, str]
    both: int = Field(ge=0)
    agree: int = Field(ge=0)
    agreement: float | None = Field(description="`agree / both`; None where `both` is 0")


class PooledPriors(_Strict):
    """The priors a forecast in ``before_term`` may read: every Term strictly before it."""

    before_term: int = Field(description="The pooled Terms are those strictly before this one")
    terms: list[int] = Field(description="The Terms pooled, ascending")
    decisions: int = Field(ge=0, description="Complete-lineup decisions pooled")
    justices: list[JusticeRate] = Field(default_factory=list)
    pairs: list[PairRate] = Field(default_factory=list)


@dataclass
class _Acc:
    sat: int = 0
    majority: int = 0
    in_part: int = 0
    disturb_eligible: int = 0
    disturb: int = 0


def case_judgments(
    conn: corpus.ReadConnection, case_ids: Iterable[str]
) -> dict[str, Judgment | None]:
    """Each case row's parsed merits judgment; None where it carries none or an unknown label."""
    ids = sorted(set(case_ids))
    out: dict[str, Judgment | None] = {}
    for start in range(0, len(ids), _CHUNK):
        chunk = ids[start : start + _CHUNK]
        placeholders = ",".join("?" * len(chunk))
        rows = conn.execute(
            f"SELECT case_id, merits_judgment FROM cases WHERE case_id IN ({placeholders})",
            tuple(chunk),
        ).fetchall()
        for row in rows:
            raw = row["merits_judgment"]
            try:
                out[str(row["case_id"])] = Judgment(raw) if raw else None
            except ValueError:
                out[str(row["case_id"])] = None
    return out


def _side(vote: VoteValue) -> bool | None:
    """True with the judgment, False in dissent, None for anything else."""
    if vote in _WITH_JUDGMENT:
        return True
    if vote == VoteValue.dissent:
        return False
    return None


def _participated(vote: VoteValue) -> bool:
    return vote not in _ABSENT


def justice_priors(
    lineups: Sequence[MeritsLineup], judgments: Mapping[str, Judgment | None]
) -> StatPackJusticeVotes:
    """Roll ``lineups`` into per-Term per-Justice tallies, most recent Term first."""
    terms = []
    for term in sorted({lu.term for lu in lineups}, reverse=True):
        members = [lu for lu in lineups if lu.term == term]
        complete = [lu for lu in members if lu.status == "complete"]
        accs: dict[str, _Acc] = {}
        pairs: Counter[tuple[str, str]] = Counter()
        agrees: Counter[tuple[str, str]] = Counter()
        judged = 0
        for lu in complete:
            judgment = judgments.get(lu.case_id) if lu.case_id else None
            disturbed = (
                True if judgment in _DISTURBED else False if judgment in _UNDISTURBED else None
            )
            if disturbed is not None:
                judged += 1
            sides: dict[str, bool] = {}
            for vote in lu.votes:
                # The model stores enum values, so read the vote back into its enum.
                value = VoteValue(vote.vote)
                if not _participated(value):
                    continue
                acc = accs.setdefault(vote.justice, _Acc())
                acc.sat += 1
                side = _side(value)
                if side is None:
                    if value != VoteValue.concur_in_part:
                        raise ValueError(
                            f"{lu.term}/{lu.listing_number}: no merits side for {value}"
                        )
                    acc.in_part += 1
                    continue
                sides[vote.justice] = side
                acc.majority += side
                if disturbed is not None:
                    acc.disturb_eligible += 1
                    acc.disturb += side == disturbed
            for a, b in combinations(sorted(sides), 2):
                pairs[(a, b)] += 1
                agrees[(a, b)] += sides[a] == sides[b]
        terms.append(
            StatPackJusticeVotesTerm(
                term=term,
                documents=len(members),
                complete=len(complete),
                judged=judged,
                justices=[
                    StatPackJusticeVotesJustice(justice=name, **vars(acc))
                    for name, acc in sorted(accs.items())
                ],
                pairs=[
                    StatPackJusticeVotesPair(justices=pair, both=n, agree=agrees[pair])
                    for pair, n in sorted(pairs.items())
                ],
            )
        )
    return StatPackJusticeVotes(terms=terms)


def justice_votes_section(conn: corpus.ReadConnection) -> StatPackJusticeVotes | None:
    """The statpack's per-Justice votes section, over every Term the record holds.

    ``None`` while the record holds no complete lineup, so the pack carries no
    ``justice_votes`` key.
    """
    span = recorded_terms(conn)
    if span is None:
        return None
    lineups = merits_lineups(conn, first_term=span[0], last_term=span[1])
    complete = [lu.case_id for lu in lineups if lu.status == "complete" and lu.case_id]
    # A complete lineup with no case id still tallies its votes, so test the
    # statuses rather than the judgment lookups.
    if not any(lu.status == "complete" for lu in lineups):
        return None
    return justice_priors(lineups, case_judgments(conn, complete))


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def pool_before(
    priors: StatPackJusticeVotes, before_term: int, *, justices: Iterable[str] | None = None
) -> PooledPriors:
    """Sum every Term strictly before ``before_term`` into rates.

    ``justices`` limits the rows to a bench (a cell's sitting Justices) and the
    pairs to pairs within it; None keeps every Justice the pooled Terms carry.
    """
    keep = None if justices is None else set(justices)
    pooled = [t for t in priors.terms if t.term < before_term]
    accs: dict[str, _Acc] = {}
    both: Counter[tuple[str, str]] = Counter()
    agree: Counter[tuple[str, str]] = Counter()
    for term in pooled:
        for row in term.justices:
            if keep is not None and row.justice not in keep:
                continue
            acc = accs.setdefault(row.justice, _Acc())
            acc.sat += row.sat
            acc.majority += row.majority
            acc.in_part += row.in_part
            acc.disturb_eligible += row.disturb_eligible
            acc.disturb += row.disturb
        for pair in term.pairs:
            if keep is not None and not set(pair.justices) <= keep:
                continue
            both[pair.justices] += pair.both
            agree[pair.justices] += pair.agree
    return PooledPriors(
        before_term=before_term,
        terms=sorted(t.term for t in pooled),
        decisions=sum(t.complete for t in pooled),
        justices=[
            JusticeRate(
                justice=name,
                sat=acc.sat,
                majority=acc.majority,
                in_part=acc.in_part,
                majority_rate=_rate(acc.majority, acc.sat),
                disturb_eligible=acc.disturb_eligible,
                disturb=acc.disturb,
                disturb_rate=_rate(acc.disturb, acc.disturb_eligible),
            )
            for name, acc in sorted(accs.items())
        ],
        pairs=[
            PairRate(justices=pair, both=n, agree=agree[pair], agreement=_rate(agree[pair], n))
            for pair, n in sorted(both.items())
        ],
    )
