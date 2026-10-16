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

from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import datetime
from typing import Literal

from .integrity import FORWARD, PROCEDURAL, RETROSPECTIVE, StratifiedCell, evaluation_clock
from .leaderboard import kendall_tau_b, set_aside_moved
from .pipeline.base_rates import claim_score
from .pipeline.moments import first_moment
from .process_version import (
    Series,
    composition_of,
    frozen_process_record,
    pooled_windows,
    refuse_shared_labels,
    rubric_listing,
    rubric_of,
    series_sort_key,
    window_label,
)
from .schemas import (
    ClaimJudgeAgreement,
    ClaimMeanScore,
    ClaimScoreBlock,
    ClaimScoreBoard,
    ClaimScoreClaimSetAsideLine,
    ClaimScoreEntry,
    ClaimScoreSetAsideLine,
    ClaimScoreStratum,
    ClaimSetAsideRecord,
    CountingWindow,
    Evaluation,
    ForwardClaimRecord,
    LeakageExclusionRecord,
    SetAsideReason,
    Stage,
    Stratum,
    VoidedEventsRecord,
)
from .store import EvaluationKey, SetAsideCell, evaluation_key

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


def _agreement(
    evals: Sequence[Evaluation],
    cell_windows: Mapping[EvaluationKey, CountingWindow] | None = None,
) -> ClaimJudgeAgreement | None:
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

    The validation pools every predictor's cells by design — it validates the
    judge, not a forecaster — so it lists each (predictor, window) series and
    the count of its cells that formed a pair as ``windows``
    (:func:`fedcourtsai.process_version.pooled_windows`), a single series
    included, and the (evaluator, digest) rubrics those pairs' grades came from
    as ``rubrics``.
    """
    if not evals:
        return None
    points: list[tuple[float, float]] = []
    paired: list[Evaluation] = []
    pair_events: set[tuple[str, str]] = set()
    for ev in evals:
        if ev.claim_scores is None or ev.claim_scores.total is None or ev.reasoning_quality is None:
            continue
        points.append((ev.claim_scores.total, ev.reasoning_quality))
        paired.append(ev)
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
        windows=pooled_windows(_series_counts(paired, cell_windows or {})),
        rubrics=rubric_listing(Counter(rubric_of(ev) for ev in paired)),
    )


def _series_counts(
    evals: Iterable[Evaluation], cell_windows: Mapping[EvaluationKey, CountingWindow]
) -> dict[Series, int]:
    """How many of ``evals`` each (predictor, window) series contributes."""
    counts: dict[Series, int] = defaultdict(int)
    for ev in evals:
        counts[(ev.predictor_id, cell_windows.get(evaluation_key(ev)))] += 1
    return counts


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
    voided_events: VoidedEventsRecord | None = None,
    cell_windows: Mapping[EvaluationKey, CountingWindow] | None = None,
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
    was drawn from. ``cell_windows`` (``store.StratifiedRun.cell_windows``,
    from the same pass) names each cell's counting window. ``entries`` is the
    pooled default — one per predictor, over every counted cell in every
    non-revoked window, with ``windows`` listing each window and its grading
    count — and ``by_protocol`` is the per-(predictor, window) cut, ordered by
    ``predictor_id`` then the window's opening, with the label as
    ``process_window``. Both are computed over their own cells, never averaged
    from one another (``docs/process-version.md``, *Pooled by default*). The
    judge validation pools predictors and lists its series. Unsupplied — an
    all-versions build — entries key on the predictor, list no windows, and
    there is no cut.
    """
    by_stratum: dict[Stratum, list[Evaluation]] = {FORWARD: [], RETROSPECTIVE: [], PROCEDURAL: []}
    windows = cell_windows or {}
    by_predictor: dict[str, dict[Stratum, list[Evaluation]]] = defaultdict(
        lambda: {FORWARD: [], RETROSPECTIVE: [], PROCEDURAL: []}
    )
    by_series: dict[Series, dict[Stratum, list[Evaluation]]] = defaultdict(
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
        by_series[(ev.predictor_id, windows.get(evaluation_key(ev)))][stratum].append(ev)

    refuse_shared_labels(by_series, surface="claim scores")
    entries: list[ClaimScoreEntry] = []
    for predictor_id in sorted(by_predictor):
        entry = _entry(predictor_id, None, by_predictor[predictor_id], windows)
        if not _is_empty(entry):
            entries.append(entry)
    cut: list[ClaimScoreEntry] = []
    for series in sorted(by_series, key=series_sort_key):
        predictor_id, window = series
        if window is None:
            continue
        entry = _entry(predictor_id, window, by_series[series], windows)
        if not _is_empty(entry):
            cut.append(entry)
    return ClaimScoreBoard(
        process_scope=process_scope,
        forward_claim=forward_claim,
        leakage_exclusion=leakage_exclusion,
        voided_events=voided_events,
        # Recorded on every build, `all` scope included: it states what the
        # freeze constants were, not that the partition was applied.
        frozen_process=frozen_process_record(),
        evaluations_total=total,
        cells_with_claims=with_claims,
        forward_agreement=_agreement(by_stratum[FORWARD], windows),
        retrospective_agreement=_agreement(by_stratum[RETROSPECTIVE], windows),
        procedural_agreement=_agreement(by_stratum[PROCEDURAL], windows),
        entries=entries,
        by_protocol=cut,
    )


def _entry(
    predictor_id: str,
    window: CountingWindow | None,
    strata: Mapping[Stratum, list[Evaluation]],
    cell_windows: Mapping[EvaluationKey, CountingWindow],
) -> ClaimScoreEntry:
    """One entry: the pooled default where ``window`` is ``None``, else that window's cut.

    The pooled entry's ``windows`` counts the block-carrying gradings each
    window contributes — the population its aggregates are computed over.
    """
    carrying = [
        evaluation_key(ev)
        for stratum in (FORWARD, RETROSPECTIVE, PROCEDURAL)
        for ev in strata[stratum]
        if ev.claim_scores is not None
    ]
    return ClaimScoreEntry(
        predictor_id=predictor_id,
        process_window=window_label(window),
        windows=composition_of(carrying, cell_windows) if window is None else [],
        forward=_aggregate_stratum(strata[FORWARD]),
        retrospective=_aggregate_stratum(strata[RETROSPECTIVE]),
        procedural=_aggregate_stratum(strata[PROCEDURAL]),
    )


def _is_empty(entry: ClaimScoreEntry) -> bool:
    """Whether a predictor has no block-carrying cell in any stratum.

    An all-null row states nothing a count on the board does not, so it is
    dropped rather than rendered.
    """
    return entry.forward is None and entry.retrospective is None and entry.procedural is None


def claim_surface_set_aside(set_aside: Sequence[SetAsideCell]) -> list[SetAsideCell]:
    """The set-aside cells this surface's own population holds: cert's first moment.

    What the surface's ``set_aside`` record counts, so the count describes the
    cells its figures actually left — an interim cell set aside on the
    leaderboard's stage blocks was never in this surface's population.
    """
    population = (Stage.cert, first_moment(Stage.cert))
    return [held for held in set_aside if (held.cell[2], held.cell[3]) == population]


def claim_set_aside_sensitivity(
    set_aside: Sequence[SetAsideCell], including: ClaimScoreBoard
) -> list[ClaimScoreSetAsideLine]:
    """Each claim figure the set-aside moved, read off a surface built with them counted.

    ``including`` is :func:`build_claim_scores` over the same pass's
    :meth:`~fedcourtsai.store.StratifiedRun.sensitivity_cells`. Only the
    surface's own population — cert's first moment — has figures here, so a
    set-aside cell on any other block moves nothing and gets no line.

    A line's figure is null only where none of its counted-back gradings
    carries a claim block, since such a grading moves no claim figure; a
    missing figure for gradings that do carry one raises, exactly as the
    leaderboard's sensitivity does: the including surface is built from a
    superset of the default's cells, so a figure absent there is a construction
    error, and a board must never publish a set-aside without its reading.
    """
    entries = {entry.predictor_id: entry for entry in including.entries}
    carrying: dict[tuple[str, Stratum], int] = defaultdict(int)
    for (evaluation, stratum, _stage, _moment), _reason in claim_surface_set_aside(set_aside):
        if evaluation.claim_scores is not None:
            carrying[(evaluation.predictor_id, stratum)] += 1
    population = f"{Stage.cert}@{first_moment(Stage.cert)}"
    lines: list[ClaimScoreSetAsideLine] = []
    for (block, predictor_id, stratum), count in sorted(set_aside_moved(set_aside).items()):
        if block != population:
            continue
        entry = entries.get(predictor_id)
        figure = getattr(entry, stratum) if entry is not None else None
        if figure is None and carrying[(predictor_id, stratum)]:
            raise ValueError(
                f"the sensitivity surface holds no {stratum} claim figure for "
                f"{predictor_id}, though {carrying[(predictor_id, stratum)]} set-aside "
                f"grading(s) carrying a claim block sit there"
            )
        lines.append(
            ClaimScoreSetAsideLine(
                predictor_id=predictor_id,
                stratum=stratum,
                set_aside=count,
                including=figure,
            )
        )
    return lines


#: One pass's claim-grain set-asides: per graded cell, the claims set aside and why.
ClaimSetAsides = Mapping[EvaluationKey, Mapping[str, SetAsideReason]]


def _block_without(block: ClaimScoreBlock, drop: frozenset[str]) -> ClaimScoreBlock:
    """``block`` with the named claims' scores taken out and its totals re-summed.

    The resolution stays on the row — a set-aside claim is not unresolved — and
    only its score leaves, so every figure built from the block (the totals, the
    per-claim means, the judge validation's pairs) reads it as unscored.
    """
    rows = [
        row.model_copy(update={"score": None}) if row.claim_id in drop else row
        for row in block.claims
    ]
    scored = [row for row in rows if row.score is not None]
    if not scored:
        return block.model_copy(update={"claims": rows, "total": None, "floor": None, "lift": None})
    total = sum(row.score for row in scored if row.score is not None)
    floor = sum(
        claim_score(row.baseline, row.outcome, row.baseline)
        for row in scored
        if row.baseline is not None and row.outcome is not None
    )
    return block.model_copy(
        update={"claims": rows, "total": total, "floor": floor, "lift": total - floor}
    )


def without_set_aside_claims(
    cells: Iterable[StratifiedCell],
    claim_set_aside: ClaimSetAsides,
    *,
    counting_back: SetAsideReason | None = None,
) -> list[StratifiedCell]:
    """``cells`` with every claim-grain set-aside claim's score taken out of its block.

    The population every claim figure is built over: the default when
    ``counting_back`` is ``None``, and one reason's sensitivity reading when it
    names that reason — its claims keep their scores and every other reason's
    still leave, so a line counts one reason back and never stacks two.
    A cell with nothing to take out passes through unchanged.
    """
    out: list[StratifiedCell] = []
    for cell in cells:
        evaluation, stratum, stage, moment = cell
        held = claim_set_aside.get(evaluation_key(evaluation), {})
        drop = frozenset(cid for cid, reason in held.items() if reason != counting_back)
        if not drop or evaluation.claim_scores is None:
            out.append(cell)
            continue
        adjusted = evaluation.model_copy(
            update={"claim_scores": _block_without(evaluation.claim_scores, drop)}
        )
        out.append((adjusted, stratum, stage, moment))
    return out


def _surface_claim_set_asides(
    cells: Iterable[StratifiedCell], claim_set_aside: ClaimSetAsides
) -> list[tuple[Evaluation, Stratum, str, SetAsideReason]]:
    """``(grading, stratum, claim id, reason)`` per set-aside claim on this surface's population."""
    population = (Stage.cert, first_moment(Stage.cert))
    found: list[tuple[Evaluation, Stratum, str, SetAsideReason]] = []
    for evaluation, stratum, stage, moment in cells:
        if (stage, moment) != population:
            continue
        held = claim_set_aside.get(evaluation_key(evaluation), {})
        found.extend((evaluation, stratum, cid, reason) for cid, reason in sorted(held.items()))
    return found


def claim_set_aside_record(
    cells: Iterable[StratifiedCell], claim_set_aside: ClaimSetAsides
) -> ClaimSetAsideRecord | None:
    """The claim-grain set-aside over this surface's default cells, in claim units.

    A claim is a prediction's (case, event, predictor, claim id): every judge
    grading the cell carries the same row, so it is counted once, with the
    gradings carrying it beside. ``None`` where nothing is set aside.
    """
    found = _surface_claim_set_asides(cells, claim_set_aside)
    if not found:
        return None
    claims: dict[tuple[str, str, str, str], SetAsideReason] = {}
    scored: set[tuple[str, str, str, str]] = set()
    gradings: set[EvaluationKey] = set()
    for evaluation, _stratum, claim_id, reason in found:
        key = (evaluation.case_id, evaluation.event_id, evaluation.predictor_id, claim_id)
        claims[key] = reason
        gradings.add(evaluation_key(evaluation))
        block = evaluation.claim_scores
        if block is not None and any(
            row.claim_id == claim_id and row.score is not None for row in block.claims
        ):
            scored.add(key)
    by_reason: Counter[str] = Counter(claims.values())
    by_claim: Counter[str] = Counter(key[3] for key in claims)
    by_predictor: Counter[str] = Counter(key[2] for key in claims)
    return ClaimSetAsideRecord(
        claims=len(claims),
        scored_claims=len(scored),
        gradings=len(gradings),
        by_reason=dict(sorted(by_reason.items())),
        by_claim=dict(sorted(by_claim.items())),
        by_predictor=dict(sorted(by_predictor.items())),
        events=sorted({f"{k[0]} {k[1]} {k[3]} {reason}" for k, reason in claims.items()}),
    )


def claim_set_aside_sensitivity_lines(
    cells: Sequence[StratifiedCell],
    claim_set_aside: ClaimSetAsides,
    surface_over: Callable[[Sequence[StratifiedCell]], ClaimScoreBoard],
) -> list[ClaimScoreClaimSetAsideLine]:
    """Each claim figure a claim-grain reason moved, with that reason's claims counted back.

    ``cells`` are the default cells (the cell-grain set-aside already out) and
    ``surface_over`` builds the surface over a population. Per reason, the
    surface is rebuilt over :func:`without_set_aside_claims` counting that
    reason back, and each (predictor, stratum) the reason's claims sit in gets
    a line reading that rebuild's pooled entry — one reason per line, never two
    stacked, and never with the cell-grain set-aside's cells.
    """
    found = _surface_claim_set_asides(cells, claim_set_aside)
    held: dict[tuple[SetAsideReason, str, Stratum], set[tuple[str, str, str]]] = defaultdict(set)
    for evaluation, stratum, claim_id, reason in found:
        held[(reason, evaluation.predictor_id, stratum)].add(
            (evaluation.case_id, evaluation.event_id, claim_id)
        )
    lines: list[ClaimScoreClaimSetAsideLine] = []
    for reason in sorted({reason for reason, _pid, _stratum in held}):
        including = surface_over(
            without_set_aside_claims(cells, claim_set_aside, counting_back=reason)
        )
        entries = {entry.predictor_id: entry for entry in including.entries}
        for (line_reason, predictor_id, stratum), claims in sorted(held.items()):
            if line_reason != reason:
                continue
            entry = entries.get(predictor_id)
            lines.append(
                ClaimScoreClaimSetAsideLine(
                    reason=reason,
                    predictor_id=predictor_id,
                    stratum=stratum,
                    claims=len(claims),
                    including=getattr(entry, stratum) if entry is not None else None,
                )
            )
    return lines
