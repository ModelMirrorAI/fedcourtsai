"""How votes aggregate into a disposition, per stage.

The single definition of the vote thresholds the Court decides by. Cert,
interim relief, and merits are one decision model differing in exactly two
parameters — this module carries the first (how votes become an outcome); the
second (what an observer gets to see) is the observation mask in
``docs/decision-model.md``.

Nothing is scored on these numbers today, and they are the reason to be careful
anyway: a disposition probability derived from a vote forecast would be the sum
of the margin distribution's mass at or above the threshold, so a wrong
threshold rescales every such probability without failing anything. That is why
they live in one place and carry their sources here, and why no prompt,
docstring, or agent restates them. Cite :data:`AGGREGATION` rather than
repeating a count.

Every threshold here is **Court practice, not enacted law**, and the distinction
is recorded rather than smoothed over: the Rules contain no vote count for
certiorari anywhere, and no statute states the merits majority either. The only
statutory number in the module is the quorum. ``docs/decision-model.md`` pins
every citation; :attr:`AggregationRule.source` names the authority for each rule
and what kind of authority it is.

A leaf module by construction: it depends only on the shared schema, so no
consumer can form an import cycle around it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from ..schemas import Stage


@dataclass(frozen=True)
class AggregationRule:
    """The vote threshold that turns a margin into a disposition, for one stage.

    ``denominator`` says what ``votes_required`` is counted against.
    ``fixed`` is an absolute count that does not move with recusals — the cert
    custom is stated as four Justices, not as four ninths. ``participating`` is a
    strict majority of those who took part, which *does* move: an eight-Justice
    merits Court needs five, so a Court equally divided at 4-4 clears no
    threshold. That is not the absence of a judgment — an equally divided Court
    affirms, and the affirmance is the judgment of the entire Court (*Durant*).
    What it lacks is precedential weight (*Neil v. Biggers*).
    """

    votes_required: int | None
    denominator: Literal["fixed", "participating"]
    source: str

    def threshold(self, participating: int) -> int:
        """Votes needed for the relief, given how many Justices took part.

        Raises below the six-Justice quorum (28 U.S.C. § 1): with five sitting
        the Court cannot act, so there is no threshold to return and a clamped
        number would be a confident answer to an invalid question.
        """
        if participating < QUORUM:
            raise ValueError(f"below the quorum of {QUORUM}: {participating} participating")
        if self.denominator == "fixed":
            required = self.votes_required
            if required is None:  # pragma: no cover - unreachable by construction
                raise ValueError("a fixed rule must state votes_required")
            return required
        return participating // 2 + 1


# The six-Justice quorum, the one threshold here that *is* statutory.
QUORUM = 6

# Every rule below rests on Court practice rather than on an enacted vote count.
# That is not a gap in the sourcing, it is the finding: the Rules of the Court
# contain no vote count for certiorari anywhere, and no statute states the merits
# majority either. The citations name the best evidence for each practice and say
# what kind of authority it is, so a reader can weigh it rather than assume a code
# section stands behind it.
AGGREGATION: Mapping[Stage, AggregationRule] = {
    # Four votes, and the Rules do not say so — Rule 10 states only that review is
    # "not a matter of right, but of judicial discretion". Four is nonetheless a
    # hard floor for the modern Court: the FJC records that it "gradually adopted
    # the view that four votes should serve as a hard minimum ... irrespective of
    # the strength of feeling of those in the minority", durable "to the present
    # day". Van Devanter's testimony that the Court sometimes granted on three
    # describes the practice that view superseded, so it bears on the custom's
    # history and not on a petition being predicted now.
    Stage.cert: AggregationRule(
        votes_required=4,
        denominator="fixed",
        source="Court practice; FJC, The Supreme Court's Rule of Four. Sup. Ct. R. 10 is silent",
    ),
    # The Court acts by majority on an application once it is before the full
    # Court. A single Circuit Justice may act alone instead (Sup. Ct. R. 22;
    # 28 U.S.C. § 2101(f)), which this rule does not model — it describes the
    # referred posture only. Note what is NOT cited here: Hollingsworth states
    # what an applicant must *show*, not how many Justices must vote to grant, so
    # it is a standard rather than an aggregation rule and belongs in the doc's
    # discussion instead of in this field.
    Stage.interim: AggregationRule(
        votes_required=None,
        denominator="participating",
        source=(
            "Court practice (the only authority for the count); "
            "Sup. Ct. R. 22.5 (referral to the full Court), Sup. Ct. R. 23.1 and "
            "28 U.S.C. § 2101(f) (single-Justice stay authority) — none states a count"
        ),
    ),
    # A majority of those participating carries the judgment. Also practice: no
    # statute states it. 28 U.S.C. § 1 supplies only the nine seats and the
    # six-Justice quorum, and § 2109 governs the *absence* of a quorum, borrowing
    # the equally-divided phrase by reference rather than enacting it. That
    # doctrine is judge-made: Durant v. Essex Co., 74 U.S. (7 Wall.) 107 (1868)
    # holds the equally divided affirmance to be the judgment of the entire
    # Court; Neil v. Biggers, 409 U.S. 188, 192 (1972) is the authority for its
    # carrying no precedential weight. The
    # *opinion* is a separate function of the same votes and may command fewer
    # than the judgment — a plurality — which is not a threshold and is not
    # modelled here.
    Stage.merits: AggregationRule(
        votes_required=None,
        denominator="participating",
        source=(
            "Court practice (no statute states the majority); "
            "28 U.S.C. § 1 (quorum only); Durant v. Essex Co., 74 U.S. 107 "
            "(equally divided affirmance is a judgment); Neil v. Biggers, "
            "409 U.S. 188, 192 (no precedential weight)"
        ),
    ),
}


def rule_for(stage: Stage | None) -> AggregationRule | None:
    """The aggregation rule for ``stage``, or ``None`` where none is declared.

    Total by design. An event carrying no stage — a circuit motion, which has no
    Supreme Court decision standard — yields ``None`` rather than a guess, and
    the caller degrades to disposition-level scoring instead of deriving a margin
    threshold that means nothing.
    """
    if stage is None:
        return None
    return AGGREGATION.get(stage)


def disposition_probability(
    margin: Sequence[float], stage: Stage, *, participating: int = 9
) -> float:
    """P(the relief is granted), from a distribution over the vote margin.

    ``margin[k]`` is the probability that exactly ``k`` participating Justices
    vote for the relief. The answer is the mass at or above the stage's
    threshold.

    Summing the margin distribution is what keeps this exact. Deriving the same
    number from nine per-justice marginals would require assuming the votes
    independent, which is badly wrong for this Court; a margin distribution
    carries the dependence structure already. Note where that relocates the
    assumption rather than removing it: nothing here verifies the submitted
    margin is the law of any joint distribution over nine votes.

    Rejects rather than computes on a malformed input. Anything built on this
    would trust it, so returning a "probability" above 1 from an unnormalized
    vector, or reading mass at ``k`` above the bench that sat, would put a
    meaningless number where a probability is expected.

    **Binary by construction.** Every bin below the threshold falls into the
    complement, so this is the right instrument only for a single-question,
    two-outcome vote. It is not the right one where part of the mass belongs to a
    procedural outcome on its own axis — the equally divided Court at merits is
    exactly that case, and its bin is not a "denial" of anything.
    """
    if len(margin) != participating + 1:
        raise ValueError(f"margin has {len(margin)} bins, expected {participating + 1}")
    if any(p < 0 for p in margin):
        raise ValueError("margin carries negative mass")
    total = sum(margin)
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"margin sums to {total}, not 1")
    threshold = AGGREGATION[stage].threshold(participating)
    return sum(p for k, p in enumerate(margin) if k >= threshold)


def expected_votes(margin: Sequence[float]) -> float:
    """The mean number of votes for the relief, ``Σ k · margin[k]``.

    The right-hand side of the coherence identity a submitted forecast has to
    satisfy: by linearity of expectation the per-justice probabilities must sum
    to this, whatever the dependence between votes. A free consistency check on a
    forecast, and one that holds without any independence assumption.
    """
    return sum(k * p for k, p in enumerate(margin))
