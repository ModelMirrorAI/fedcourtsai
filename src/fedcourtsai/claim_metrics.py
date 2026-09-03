"""Aggregate the ledger's mechanical claim-score blocks into ``metrics/claim-scores.json``.

Deterministic and offline: a pure function of the committed artifacts under
``data/`` — no network, no clock, no randomness — so the same ledger always
yields byte-identical output. (The leaderboard shares the discipline but takes
one input more, the committed statpack.) ``fedcourts claim-scores`` writes the
result.

The surface is **advisory beside the leaderboard, never inside it**: nothing
here alters or reorders the board, and the artifact carries no rank because a
claim total is never a rank key (its variance is unbounded above, so on
N-unweighted point estimates variance-seeking would buy rank). Aggregates are
per predictor per pre-registration stratum — the same stratification the
leaderboard uses, via the same ``store.iter_stratified_evaluations`` join and
the same frozen-scope default — and are never pooled across strata or across
process-version scope. The population is the **cert-stage** cells, because the
surface never blends stages: the interim moments and the minted merits event
declare sets of their own (``interim-v1``, ``merits-v1``) and their cells do
carry blocks, but a total pooled across two
stages' claim sets is not one quantity, so a non-cert cell belongs outside
this surface rather than inside its absence counts until a per-stage surface
exists.

The headline is the **judge validation**, pre-registered in
``docs/outcome-decomposition.md`` (*The mechanical↔semantic agreement*):
Kendall tau-b over per-cell pairs of (mechanical claim total,
``reasoning_quality``), per stratum, over the intersection population only,
with the intersection ``n`` printed beside the coefficient and the coefficient
**suppressed below n = 10**. Operational absences — a cell missing one of the
two numbers — are counted and published beside the intersection, because
differential absence selects the pair set; availability-mask exclusions (a
block whose every claim is masked or baseline-less) are a property of the
record and are counted separately. No inter-grader agreement is derived here:
``Leaderboard.evaluator_agreement`` publishes the panel's agreement on its
**big-case reads**, and the semantic claim family has its own per-grader number
in :mod:`fedcourtsai.pipeline.semantic` (declared and graded, but every grade
is the availability mask until opinion bodies accrue). Both correlate through the one
:func:`fedcourtsai.leaderboard.kendall_tau_b`, which is the part that must not
be duplicated.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import datetime
from typing import Literal

from .integrity import FORWARD, PROCEDURAL, RETROSPECTIVE, StratifiedCell, evaluation_clock
from .leaderboard import kendall_tau_b
from .pipeline.moments import first_moment
from .process_version import frozen_process_record
from .schemas import (
    ClaimJudgeAgreement,
    ClaimMeanScore,
    ClaimScoreBlock,
    ClaimScoreBoard,
    ClaimScoreEntry,
    ClaimScoreStratum,
    Evaluation,
    ForwardClaimRecord,
    LeakageExclusionRecord,
    Stage,
    Stratum,
)

# The pre-registered suppression threshold for the judge-validation tau-b: below
# this intersection size the coefficient is withheld and only the counts
# publish (docs/outcome-decomposition.md, *The mechanical↔semantic agreement*).
AGREEMENT_MIN_PAIRS = 10


def _mean(values: Sequence[float]) -> float | None:
    """Mean of the present values, or ``None`` when none were reported."""
    return sum(values) / len(values) if values else None


def _aggregate_stratum(evals: Sequence[Evaluation]) -> ClaimScoreStratum | None:
    """One predictor-stratum's claim aggregates, or ``None`` without any block.

    The reporting unit is the **event**, as the pre-registration fixes it: every
    evaluator of the same prediction carries an identical harness-computed
    block, so a cell-mean would weight an event by its evaluator count. Blocks
    are therefore deduplicated to one per (case, event) — where copies could
    ever differ (a statpack revision between evaluator stamps), the newest
    evaluation's block wins, deterministically, on the harness clock
    (:func:`fedcourtsai.integrity.evaluation_clock` — never the agent-written
    ``created_at``, and aware-normalized so a naive/aware mix cannot raise) —
    and ``cells`` is published beside ``events`` as the census of the collapsed
    multiplicity — one grading per judge, the join having already dropped a
    re-graded cell's superseded runs
    (:func:`fedcourtsai.integrity.latest_evaluation_runs`).
    """
    cells = 0
    latest: dict[tuple[str, str], tuple[tuple[datetime, str, str], ClaimScoreBlock]] = {}
    for ev in evals:
        if ev.claim_scores is None:
            continue
        cells += 1
        key = (ev.case_id, ev.event_id)
        order = (evaluation_clock(ev), ev.evaluator_id, ev.run_id)
        current = latest.get(key)
        if current is None or order > current[0]:
            latest[key] = (order, ev.claim_scores)
    if not latest:
        return None
    blocks = [latest[key][1] for key in sorted(latest)]
    # One denominator for the three means: the events whose block scored at
    # all. `score_claims` sets total/floor/lift jointly, so the inner
    # not-None filters are typing guards, never a second denominator.
    scored = [b for b in blocks if b.total is not None]
    totals = [b.total for b in scored if b.total is not None]
    floors = [b.floor for b in scored if b.floor is not None]
    lifts = [b.lift for b in scored if b.lift is not None]

    # Per-claim rows in first-seen (declaration) order; a never-scored claim
    # still appears with scored=0 so the coverage gap stays visible.
    per_claim: dict[str, list[float]] = {}
    largest_id: str | None = None
    largest_score: float | None = None
    for block in blocks:
        for row in block.claims:
            scores = per_claim.setdefault(row.claim_id, [])
            if row.score is not None:
                scores.append(row.score)
                # Strictly greater keeps the first-seen row on ties, so the
                # pick is deterministic over the stable input order.
                if largest_score is None or abs(row.score) > abs(largest_score):
                    largest_id, largest_score = row.claim_id, row.score
    return ClaimScoreStratum(
        events=len(blocks),
        cells=cells,
        scored_events=len(scored),
        declared_set_versions=sorted({b.declared_set_version for b in blocks}),
        mean_total=_mean(totals),
        mean_floor=_mean(floors),
        mean_lift=_mean(lifts),
        claims=[
            ClaimMeanScore(claim_id=claim_id, scored=len(scores), mean_score=_mean(scores))
            for claim_id, scores in per_claim.items()
        ],
        largest_claim_id=largest_id,
        largest_claim_score=largest_score,
    )


def _agreement(evals: Sequence[Evaluation]) -> ClaimJudgeAgreement | None:
    """One stratum's judge validation, or ``None`` when the stratum has no cells.

    The pair set is the intersection only: a cell enters where **both** the
    mechanical claim total and the ``reasoning_quality`` grade exist. The
    coefficient is computed only at or above :data:`AGREEMENT_MIN_PAIRS`; below
    it the record still publishes the ``n`` and the absence counts, so a
    selected intersection is visible even while the number is withheld.

    Two honesty limits travel with the record. The pairs are per **cell** (the
    pre-registered unit the threshold keys on), so evaluator multiplicity
    repeats an identical mechanical total against several grades —
    ``pair_events`` beside ``pairs`` is what exposes it. And the absence
    counts cover **committed** cells only: an evaluator cell that failed
    outright commits nothing and is invisible here, so differential cell
    failure still selects the pair set upstream of these counts.

    A cell is one grading per judge: the join that feeds this surface collapses
    a re-graded cell's runs before yielding it
    (:func:`fedcourtsai.integrity.latest_evaluation_runs`), which matters most
    here of anywhere on the surface — duplicate pairs inflate ``pairs`` against
    :data:`AGREEMENT_MIN_PAIRS`, so without the collapse a re-grade could
    publish a coefficient the suppression rule is holding back.
    """
    if not evals:
        return None
    points: list[tuple[float, float]] = []
    pair_events: set[tuple[str, str]] = set()
    for ev in evals:
        if ev.claim_scores is None or ev.claim_scores.total is None or ev.reasoning_quality is None:
            continue
        points.append((ev.claim_scores.total, ev.reasoning_quality))
        pair_events.add((ev.case_id, ev.event_id))
    suppressed = len(points) < AGREEMENT_MIN_PAIRS
    return ClaimJudgeAgreement(
        rank_agreement=None if suppressed else kendall_tau_b(points),
        pairs=len(points),
        pair_events=len(pair_events),
        suppressed=suppressed,
        missing_claim_block=sum(1 for ev in evals if ev.claim_scores is None),
        masked_claim_total=sum(
            1 for ev in evals if ev.claim_scores is not None and ev.claim_scores.total is None
        ),
        missing_reasoning_quality=sum(1 for ev in evals if ev.reasoning_quality is None),
    )


def agreement_summary(agreement: ClaimJudgeAgreement | None) -> str:
    """One human phrase for a stratum's judge validation, honest when withheld.

    Shared by the CLI echo and the refresh-PR headline so the two surfaces
    cannot describe the same artifact differently.
    """
    if agreement is None:
        return "no cells"
    if agreement.suppressed:
        return f"suppressed (n={agreement.pairs} < {AGREEMENT_MIN_PAIRS})"
    if agreement.rank_agreement is None:
        return f"undefined over n={agreement.pairs}"
    return f"tau-b {agreement.rank_agreement:+.2f} (n={agreement.pairs})"


def build_claim_scores(
    cells: Iterable[StratifiedCell],
    *,
    process_scope: Literal["frozen", "all"] = "frozen",
    forward_claim: ForwardClaimRecord | None = None,
    leakage_exclusion: LeakageExclusionRecord | None = None,
) -> ClaimScoreBoard:
    """Roll stratified evaluations up into the claim-score surface.

    ``cells`` is the same stratified stream the leaderboard consumes
    (``store.iter_stratified_evaluations``), so it arrives with the join's two
    exclusions already applied — the forward-claim rule and the leakage bit,
    whose counts the caller passes through as ``forward_claim`` and
    ``leakage_exclusion`` so this surface and the board publish the same
    population. It is filtered to
    ``process_scope`` by the same caller — recording the scope makes the empty
    frozen headline self-explaining rather than reading as a regression. The
    surface's population is the **cert-stage** cells only: stages are never
    blended, so an interim or merits cell's block (the ``interim-v1`` and
    ``merits-v1`` sets) sits outside
    this surface until a per-stage claim surface exists, and counting a
    non-cert cell here as an
    "absence" would dilute the operational-absence counts with cells drawn
    from a different population. One entry per predictor with at least one
    block-carrying cell, ordered by ``predictor_id``; the per-stratum judge
    validation is computed over every in-population cell, block-carrying or
    not, so the absence counts describe the whole population the intersection
    was drawn from.
    """
    by_stratum: dict[Stratum, list[Evaluation]] = {FORWARD: [], RETROSPECTIVE: [], PROCEDURAL: []}
    by_predictor: dict[str, dict[Stratum, list[Evaluation]]] = defaultdict(
        lambda: {FORWARD: [], RETROSPECTIVE: [], PROCEDURAL: []}
    )
    total = 0
    with_claims = 0
    for ev, stratum, stage, moment in cells:
        # Cert's FIRST moment only. A later cert moment carries the same
        # `cert-v2` block, so filtering on the stage alone would pool two
        # information sets into one claim mean — the thing this surface's own
        # per-stage rule exists to prevent, one axis further in.
        if (stage, moment) != (Stage.cert, first_moment(Stage.cert)):
            continue
        total += 1
        if ev.claim_scores is not None:
            with_claims += 1
        by_stratum[stratum].append(ev)
        by_predictor[ev.predictor_id][stratum].append(ev)

    entries: list[ClaimScoreEntry] = []
    for predictor_id in sorted(by_predictor):
        strata = by_predictor[predictor_id]
        entry = ClaimScoreEntry(
            predictor_id=predictor_id,
            forward=_aggregate_stratum(strata[FORWARD]),
            retrospective=_aggregate_stratum(strata[RETROSPECTIVE]),
            procedural=_aggregate_stratum(strata[PROCEDURAL]),
        )
        if not _is_empty(entry):
            entries.append(entry)
    return ClaimScoreBoard(
        process_scope=process_scope,
        forward_claim=forward_claim,
        leakage_exclusion=leakage_exclusion,
        # Recorded on every build, `all` scope included: it states what the
        # freeze constants were, not that the partition was applied.
        frozen_process=frozen_process_record(),
        evaluations_total=total,
        cells_with_claims=with_claims,
        forward_agreement=_agreement(by_stratum[FORWARD]),
        retrospective_agreement=_agreement(by_stratum[RETROSPECTIVE]),
        procedural_agreement=_agreement(by_stratum[PROCEDURAL]),
        entries=entries,
    )


def _is_empty(entry: ClaimScoreEntry) -> bool:
    """Whether a predictor has no block-carrying cell in any stratum.

    An all-null row states nothing a count on the board does not, so it is
    dropped rather than rendered.
    """
    return entry.forward is None and entry.retrospective is None and entry.procedural is None
