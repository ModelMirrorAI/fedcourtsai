"""Aggregate the evaluations ledger into a ranked per-predictor leaderboard.

Deterministic and offline: a pure function of the committed artifacts under
``data/`` and the committed ``metrics/statpack.json`` — no network, no clock, no
randomness — so the same inputs always yield byte-identical output.
``fedcourts leaderboard`` writes the result to ``metrics/leaderboard.json``.

Every scored cell is stratified by the **pre-registration standard** before any
aggregation: a prediction committed while its event was still open is a true
*forward* forecast; a prediction over an event that had already resolved is
*retrospective* by construction — the outcome is public knowledge inside every
modern model's training data, so such a cell measures recall plus calibration,
never ex-ante forecasting skill. A cell whose outcome was mootness practice
(the outcome's ``disposition_basis``) is *procedural* regardless of timing —
its label tracks the Court's vacatur wording, not cert-worthiness. The strata
are aggregated separately and never blended into one headline number, and only
forward/retrospective enter the ranking. The board consumes that vocabulary
rather than defining it: the stratum names and
:func:`fedcourtsai.integrity.classify_stratum`, the single definition of the
timing split, live in :mod:`fedcourtsai.integrity` beside the harness clock the
split rests on (:func:`fedcourtsai.integrity.cell_clock`, vs the outcome's
``resolved_at`` — derivable offline from committed artifacts); the procedural
override lives with the join in ``store.stratify``.

Orthogonal to the strata runs the **stage/moment axis**: the ranked board is
cert's *first* forecast moment, and every other population — a different
decision standard (interim, merits), or the same standard forecast later in the
case's life (cert after a CVSG, merits after briefing) — aggregates into its own
unranked ``<stage>@<moment>`` block. Never pooled: ``granted`` answers a
different question at each stage, and a later moment answers the same question
with strictly more evidence.

Every figure counts one grading per cell per judge. A re-graded cell commits a
second ``evaluation.json`` beside the first, so the ledger reads collapse on
``(case, event, predictor, evaluator)`` — newest by harness clock
(:func:`fedcourtsai.integrity.latest_evaluation_runs`) — before any count, mean,
or correlation: the stratified join does it for the score aggregates, and
:func:`_scoped_evaluations` for the two agreement views, which read the ledger
directly. Never across evaluators, whose multiplicity is the panel the
``evaluators`` count and both agreement views measure. The board then publishes
how many gradings that collapse dropped (``superseded_gradings``), because a
survivor looks exactly like a cell that was only ever graded once: without the
count, a maintainer-reachable re-grade could move a standing and leave no mark
on any artifact.

Two exclusions run before any of that, both applied at the join
(``store.stratify``) and both published beside the standings so neither can be
silent: the forward-claim rule, and the evaluators' leakage bit. A cell whose
grading carries ``leakage_suspected`` may have read its own outcome, so it
enters no rank key and no scored aggregate — including the retrospective pair
that orders predictors with no forward cells, which is where near-perfect
leaked numbers would otherwise decide a standing. The bit changes membership
and never a value; ``leakage_exclusion`` carries the count and its
per-predictor split. Both exclusions reach exactly the cells the join yields,
which is **not** the two agreement views below: they read the ledger by their
own path (:func:`_scoped_evaluations`) and apply neither rule, deliberately —
they measure stakes reads and grader latitude rather than scored performance,
and ``metrics/README.md`` states the carve-out.

Coverage is published beside the ranking for the same reason. Grading is gated
at ``(evaluator, event)`` grain, so the scored set is selected rather than
sampled: a prediction committed after a judge graded its event is never scored
by that judge, and an engine whose cells backfill late is ranked over fewer
events than one that ran on time. Each entry carries its ``events_scored`` and
its population carries the union across entries, so unequal coverage is readable
off the artifact before any cross-engine comparison rests on it — nothing here
adjusts a rank or a mean for it. Equality is necessary and not sufficient: it
certifies the same event *set*, never the same stratum mix or panel depth, so
the check refuses a comparison rather than blessing one.

Skill is reported twice, against two baselines that answer different questions
and are never combined. The cell's recorded ``brier_skill_score`` scores
against the **strictly-prior** pooled rate: leakage-safe, the primary
outcome measure, and the only one that may rank.
:func:`skill_components` adds the ex-post complement — the same band scored
against the rate the case's own Term realized — computed at render rather than
carried on the cell, because a Term's own rate keeps moving until the Term
closes. Both are aggregated as a **ratio of sums** rather than a mean of
per-cell ratios; :class:`CellSkill` says why.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .integrity import (
    FORWARD,
    PROCEDURAL,
    RETROSPECTIVE,
    StratifiedCell,
    latest_evaluations,
)
from .pipeline.base_rates import realized_band_rate
from .pipeline.evaluate import is_correct
from .pipeline.moments import first_moment, scores_votes
from .process_version import frozen_process_record, graded_post_freeze, is_frozen
from .schemas import (
    GRANT_FAMILY_DISPOSITIONS,
    NO_BAND_KEY,
    BigCaseLeaderboard,
    Disposition,
    Evaluation,
    EvaluatorAgreement,
    ForwardClaimRecord,
    Leaderboard,
    LeaderboardEntry,
    LeaderboardStage,
    LeaderboardStageEntry,
    LeaderboardStratum,
    LeakageExclusionRecord,
    Moment,
    Outcome,
    Prediction,
    PredictionContext,
    Stage,
    StatPack,
    Stratum,
)
from .serialize import read_model
from .store import scored_prediction

#: One scored cell's identity — ``(case, event, predictor, evaluator, run)``.
#: The join key for per-cell figures the board computes at render rather than
#: reading off the record, since ``Evaluation`` is not hashable.
EvaluationKey = tuple[str, str, str, str, str]

# The `stages` key a stage-less cell shares (a null-stage event of a
# non-case-baseline kind — see `store.iter_stratified_evaluations`'s
# normalization): the GroupBy dimensions' `(none)` convention, so coverage is
# visible rather than silently dropped.
NO_STAGE_KEY = "(none)"


def stage_moment_key(stage: Stage | None, moment: Moment | None) -> str:
    """The unranked block a cell aggregates into: ``"<stage>@<moment>"``.

    Two moments of one stage are two populations — the later one answers the
    same question with strictly more evidence — so they must not share a mean.
    Keying the block on the pair is what keeps them apart, and it is the same
    rule the salience version and the claim-set version already carry.

    A cell with neither takes the ``(none)`` convention the GroupBy dimensions
    use, so coverage stays visible rather than silently dropped. A stage
    carrying no recorded moment is written bare (``"interim"``), which cannot
    collide with a keyed block and reads honestly as "stage known, moment not".
    """
    if stage is None:
        return NO_STAGE_KEY
    # str() yields the bare enum value — Stage/Moment are StrEnums, and a
    # validated model hands back the plain string.
    return f"{stage}@{moment}" if moment is not None else str(stage)


# Brier scores are bounded in [0, 1]; predictors that never reported one sort
# after every predictor that did, without colliding with a real worst score.
_NO_BRIER: float = 2.0
# Accuracies are bounded in [0, 1]; a predictor with no cells in a stratum — or
# none whose `correct` the stamp could compute — sorts after every predictor
# that has any, without colliding with a real worst score.
_NO_ACCURACY: float = -1.0


def _mean(values: Sequence[float]) -> float | None:
    """Mean of the present values, or ``None`` when none were reported."""
    return sum(values) / len(values) if values else None


def _evaluation_key(evaluation: Evaluation) -> EvaluationKey:
    """This evaluation's :data:`EvaluationKey`."""
    return (
        evaluation.case_id,
        evaluation.event_id,
        evaluation.predictor_id,
        evaluation.evaluator_id,
        evaluation.run_id,
    )


@dataclass(frozen=True)
class CellSkill:
    """One scored cell's Brier and the baseline Brier each skill column uses.

    The terms, not the ratios, because a stratum's skill is aggregated as a
    **ratio of sums** — ``1 - sum(brier) / sum(baseline_brier)`` — and a mean of
    per-cell ratios is a different, worse estimator. The per-cell ratio caps at
    +1 but is unbounded below, so under cert's class imbalance a mean of ratios
    is dominated by the many low-baseline denial cells and pays a predictor to
    under-forecast the rare event: on the `baseline` band, scored against the
    band's own reached rate, an always-deny forecaster means to about +0.96
    while a forecaster reporting that rate itself means to exactly 0 (the
    leave-one-out attainable null sits near +0.002 at that band's n — a
    different construction, see `metrics/README.md`). The ratio of sums
    prices the same always-deny forecaster at about -0.04, and its sign is
    invariant in the band rate, which a mean of ratios's is not — re-derive
    both from the committed pack rather than quoting them.

    A baseline is ``None`` where that column does not score the cell, so the two
    columns keep independent populations and independent counts.
    """

    brier: float
    prior_term_baseline: float | None = None
    realized_term_baseline: float | None = None


@dataclass(frozen=True)
class CellFacts:
    """One cert cell's band key and the outcome facts its floor fields read.

    Resolved at render by :func:`cell_facts`, like :class:`CellSkill`, because
    neither the band the scored prediction froze nor the realized outcome rides
    on the ``Evaluation``. Only **cert** cells carry facts: the band is a
    salience product and ``denied`` is the null call only on the cert
    disposition axis, so a cell of any other stage is absent from the map and
    every figure built on it stays null.
    """

    band_key: str
    #: ``is_correct`` for a synthetic ``denied`` call against the committed outcome.
    always_deny_correct: int
    #: ``is_correct`` for the scored prediction against the committed outcome —
    #: what the grading's stamped ``correct`` should still read. A disagreement
    #: means the grading was paired with an outcome since superseded.
    recomputed_correct: int
    #: The outcome is in the grant family the band rates count.
    grant_family: bool


def band_key(context: PredictionContext | None) -> str:
    """The ``by_band`` key for a scored prediction's frozen context.

    ``"<salience_version>/<band>"``: a band name means something only under the
    scorer version that assigned it, so a band without a version — or no frozen
    band at all — files under :data:`fedcourtsai.schemas.NO_BAND_KEY` rather
    than being guessed from the corpus's current band.
    """
    if context is None or context.band is None or context.salience_version is None:
        return NO_BAND_KEY
    return f"{context.salience_version}/{context.band}"


def _skill_of_means(terms: Sequence[tuple[float, float]]) -> float | None:
    """Population Brier skill over ``(brier, baseline_brier)`` pairs, or ``None``.

    ``1 - sum(brier) / sum(baseline_brier)``. Every baseline term is strictly
    positive by construction (a zero baseline Brier is the undefined case its
    producer already dropped), so the denominator cannot vanish on a non-empty
    set. Bounded above by 1 like the per-cell score, and unbounded below.
    """
    if not terms:
        return None
    return 1.0 - sum(brier for brier, _ in terms) / sum(baseline for _, baseline in terms)


def _aggregate(
    evals: Sequence[Evaluation],
    skills: Mapping[EvaluationKey, CellSkill],
    facts: Mapping[EvaluationKey, CellFacts] | None = None,
) -> LeaderboardStratum | None:
    """One stratum's aggregates, or ``None`` when the stratum has no evaluations.

    ``skills`` is :func:`skill_components`' per-cell map. A cell absent from a
    column's population is left out of that column entirely rather than entered
    as a zero, and each column publishes its own ``*_scored`` denominator. The
    two are never combined — different baselines, different questions.

    ``accuracy`` takes the same rule as the rest: a cell whose ``correct`` the
    stamp could not compute — no readable prediction or no committed outcome —
    leaves the column's numerator *and* denominator, which is what
    ``accuracy_scored`` records. Entering it as a zero would score a missing
    artifact as a wrong call, and the board's first rank key is the last place
    that should happen.

    ``mean_vote_accuracy`` takes the same stage gate the per-cell figure does
    (:func:`fedcourtsai.pipeline.moments.scores_votes`), applied here to the
    cell's own event rather than inherited from the block it landed in. The
    aggregate is what the prohibition on scoring a cert vote actually bites on —
    a ranked total is the thing an unscored quantity must not reach — and this
    board reads committed ``Evaluation`` records, including any written before
    the per-cell gate existed or by an evaluator that computed the field itself.
    So the ranked cert board cannot publish a vote mean whatever its cells
    carry, and the recomputation is not a duplicate of the per-cell check but
    the only one that holds over records this module did not produce.

    The realized floor fields (:func:`_floor_fields`) run over the accuracy
    population itself and are filled only where ``facts`` covers every cell of
    it, so the floor and the lift are always paired with ``accuracy``.
    """
    if not evals:
        return None
    # Each skill column's own denominator rides beside it: a cell scores a
    # column only where that column's baseline exists, so the gap between it and
    # `evaluations` must be visible rather than silent.
    correct = [ev.correct for ev in evals if ev.correct is not None]
    cells = [skills.get(_evaluation_key(ev)) for ev in evals]
    prior = [
        (cell.brier, cell.prior_term_baseline)
        for cell in cells
        if cell is not None and cell.prior_term_baseline is not None
    ]
    realized = [
        (cell.brier, cell.realized_term_baseline)
        for cell in cells
        if cell is not None and cell.realized_term_baseline is not None
    ]
    return LeaderboardStratum(
        events_scored=len({(ev.case_id, ev.event_id) for ev in evals}),
        evaluations=len(evals),
        accuracy=_mean(correct),
        accuracy_scored=len(correct),
        mean_brier_score=_mean([ev.brier_score for ev in evals if ev.brier_score is not None]),
        population_brier_skill_score=_skill_of_means(prior),
        skill_scored=len(prior),
        population_realized_term_skill_score=_skill_of_means(realized),
        realized_term_skill_scored=len(realized),
        mean_vote_accuracy=_mean(
            [
                ev.vote_accuracy
                for ev in evals
                if ev.vote_accuracy is not None and scores_votes(ev.event_id)
            ]
        ),
        mean_reasoning_quality=_mean(
            [ev.reasoning_quality for ev in evals if ev.reasoning_quality is not None]
        ),
        **_floor_fields(evals, skills, facts),
    )


def _floor_fields(
    evals: Sequence[Evaluation],
    skills: Mapping[EvaluationKey, CellSkill],
    facts: Mapping[EvaluationKey, CellFacts] | None,
) -> dict[str, float | int | None]:
    """The per-event accuracy, realized always-deny floor, lifts, and grant counts.

    All over the **accuracy population** — the cells with a non-null
    ``correct``. Three gates, each leaving fields null rather than computing
    them on a different population:

    - ``accuracy_events_scored`` and ``event_accuracy`` need no facts. Each
      event enters once, and ``event_accuracy`` (with every ``event_*`` field)
      is null where a block's gradings of one event disagree on ``correct``.
    - Everything else needs :class:`CellFacts` on **every** accuracy cell:
      partial coverage would run the floor over fewer cells than ``accuracy``.
      In practice coverage fails only on a non-cert stage, which carries none.
    - The floor and both lifts further need every accuracy cell's stamped
      ``correct`` to reproduce against the committed outcome
      (``CellFacts.recomputed_correct``). A grading stamped against an outcome
      since corrected would otherwise sit beside a floor read off the current
      one — an unpaired difference, which is not a lift.

    ``grants_expected`` sums one strictly-prior band rate per event: the
    ``segment_base_rate`` of the event's gradings the prior-Term skill column
    admits (a :class:`CellSkill` with a prior baseline), averaged over them, so
    a panel of three enters an event once. ``grants_realized_expected_scored``
    counts the grant-family events among exactly those events, so the expected
    and realized counts are quoted over one event set.
    """
    scored = [ev for ev in evals if ev.correct is not None]
    if not scored:
        return {}
    per_event: dict[tuple[str, str], set[int]] = defaultdict(set)
    for ev in scored:
        per_event[(ev.case_id, ev.event_id)].add(ev.correct or 0)
    event_consistent = all(len(values) == 1 for values in per_event.values())
    event_accuracy = (
        sum(next(iter(values)) for values in per_event.values()) / len(per_event)
        if event_consistent
        else None
    )
    fields: dict[str, float | int | None] = {
        "accuracy_events_scored": len(per_event),
        "event_accuracy": event_accuracy,
    }
    if facts is None:
        return fields
    present = [facts.get(_evaluation_key(ev)) for ev in scored]
    paired = [(ev, fact) for ev, fact in zip(scored, present, strict=True) if fact is not None]
    if len(paired) != len(scored):
        return fields

    event_facts = {(ev.case_id, ev.event_id): fact for ev, fact in paired}
    granted_events = {key for key, fact in event_facts.items() if fact.grant_family}
    rates: dict[tuple[str, str], list[float]] = defaultdict(list)
    for ev in scored:
        skill = skills.get(_evaluation_key(ev))
        if (
            skill is not None
            and skill.prior_term_baseline is not None
            and ev.segment_base_rate is not None
        ):
            rates[(ev.case_id, ev.event_id)].append(ev.segment_base_rate)
    fields.update(
        grants_realized=len(granted_events),
        grants_expected=(
            sum(sum(event_rates) / len(event_rates) for event_rates in rates.values())
            if rates
            else None
        ),
        grants_expected_scored=len(rates),
        grants_realized_expected_scored=len(granted_events & rates.keys()),
    )

    if any(fact.recomputed_correct != ev.correct for ev, fact in paired):
        return fields
    accuracy = sum(ev.correct or 0 for ev in scored) / len(scored)
    always_deny = sum(fact.always_deny_correct for _, fact in paired) / len(paired)
    fields.update(always_deny_accuracy=always_deny, accuracy_lift=accuracy - always_deny)
    if event_accuracy is not None:
        # The outcome is the event's, so every grading of it shares this bit.
        event_always_deny = sum(fact.always_deny_correct for fact in event_facts.values()) / len(
            event_facts
        )
        fields.update(
            event_always_deny_accuracy=event_always_deny,
            event_accuracy_lift=event_accuracy - event_always_deny,
        )
    return fields


def _complete_grid_by_band(
    cells: Sequence[tuple[Evaluation, Stratum]],
    predictors: Iterable[str],
    facts: Mapping[EvaluationKey, CellFacts] | None,
) -> dict[str, int]:
    """Per band key, the forward events every predictor has an accuracy-scored cell on.

    The per-band complete grid: an event counts under a band only where each
    predictor in the population carries an accuracy-scored forward grading of
    it filed under that same band, so an event whose predictors froze different
    bands is complete under none. Cert cells only (those carrying facts); empty
    without facts.
    """
    roster = set(predictors)
    if facts is None or not roster:
        return {}
    covered: dict[tuple[str, tuple[str, str]], set[str]] = defaultdict(set)
    for ev, stratum in cells:
        fact = facts.get(_evaluation_key(ev))
        if stratum != FORWARD or ev.correct is None or fact is None:
            continue
        covered[(fact.band_key, (ev.case_id, ev.event_id))].add(ev.predictor_id)
    grid: dict[str, int] = defaultdict(int)
    for (band, _event), who in covered.items():
        if who >= roster:
            grid[band] += 1
    return dict(sorted(grid.items()))


def _by_band(
    evals: Sequence[Evaluation],
    skills: Mapping[EvaluationKey, CellSkill],
    facts: Mapping[EvaluationKey, CellFacts] | None,
) -> dict[str, LeaderboardStratum] | None:
    """The forward stratum cut by frozen salience band, or ``None``.

    Built from the same cells and skill terms as the ``forward`` block it
    partitions, so each band is an ordinary :func:`_aggregate`. A cell with no
    facts files under :data:`fedcourtsai.schemas.NO_BAND_KEY` rather than
    dropping out, so the blocks' ``evaluations`` always sum to the stratum's.
    ``None`` without cells, or where none of them carries facts — a non-cert
    stage, which has no band, or a board built without facts at all.
    """
    if facts is None or not any(_evaluation_key(ev) in facts for ev in evals):
        return None
    groups: dict[str, list[Evaluation]] = defaultdict(list)
    for ev in evals:
        fact = facts.get(_evaluation_key(ev))
        groups[fact.band_key if fact is not None else NO_BAND_KEY].append(ev)
    return {
        key: stratum
        for key in sorted(groups)
        if (stratum := _aggregate(groups[key], skills, facts)) is not None
    }


def _rank_key(entry: LeaderboardEntry) -> tuple[float, float, float, float, str]:
    """Total order: forward stratum first, retrospective as tie-break, then id.

    Forward accuracy (desc, missing last) then forward Brier (asc, missing last) lead because
    only the forward stratum measures forecasting skill; the retrospective pair
    orders predictors that have no forward cells yet. The procedural stratum
    never contributes — vacatur-practice calls buy no rank. ``predictor_id`` makes the
    ranking deterministic under full ties.

    No skill column is a rank key, and the realized-Term one could not be: it
    scores against a rate no predictor could have known in-season, so ranking on
    it would rank in-season on an ex-post fact.
    """

    def acc(stratum: LeaderboardStratum | None) -> float:
        if stratum is None or stratum.accuracy is None:
            return _NO_ACCURACY
        return stratum.accuracy

    def brier(stratum: LeaderboardStratum | None) -> float:
        if stratum is None or stratum.mean_brier_score is None:
            return _NO_BRIER
        return stratum.mean_brier_score

    return (
        -acc(entry.forward),
        brier(entry.forward),
        -acc(entry.retrospective),
        brier(entry.retrospective),
        entry.predictor_id,
    )


def kendall_tau_b(points: Sequence[tuple[float, float]]) -> float | None:
    """Kendall's tau-b rank correlation of the (x, y) points, or ``None``.

    Tau-b handles ties (big-case scores can repeat): the denominator excludes
    pairs tied on each axis, so a perfectly monotone relationship reads +1 even
    with ties. Returns ``None`` with fewer than two points or when every pair
    ties on one axis (the correlation is undefined). O(n^2), which is ample for a
    cohort-sized set.
    """
    n = len(points)
    if n < 2:
        return None
    n0 = n * (n - 1) // 2
    concordant = discordant = tie_x = tie_y = 0
    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            dx = xi - points[j][0]
            dy = yi - points[j][1]
            if dx == 0:
                tie_x += 1
            if dy == 0:
                tie_y += 1
            if dx != 0 and dy != 0:
                if (dx > 0) == (dy > 0):
                    concordant += 1
                else:
                    discordant += 1
    denominator = math.sqrt((n0 - tie_x) * (n0 - tie_y))
    if denominator == 0:
        return None
    return (concordant - discordant) / denominator


def _scoped_evaluations(
    cases_dir: Path, *, in_scope: Callable[[Evaluation], bool]
) -> list[Evaluation]:
    """The committed evaluations a scope admits, one run per cell per judge.

    The agreement views read the ledger directly rather than through the
    stratified join (they need every big-case read, scored cell or not), so the
    run collapse the join applies is applied here too: a re-graded cell commits
    a second ``evaluation.json`` describing one observation, and counting both
    would enter one judge's read of a case twice into a panel mean and a
    leave-one-out comparison.

    ``in_scope`` runs **first**, so the survivor of the collapse is the newest
    grading the scope admits rather than the newest grading that exists — the
    same ordering ``store.stratify`` uses, which is what keeps the frozen board
    and the frozen agreement views over one set of cells.

    The caller's big-case filter runs **after**, which is the deliberate
    reading of what a re-grade means: a judge that re-graded a cell without
    recording a stakes read has no current read of it, so the cell leaves the
    panel rather than falling back to the read the re-grade superseded.

    Reading the ledger here rather than through ``store.stratify`` means the
    join's two exclusions — the forward-claim rule and the leakage bit — do not
    apply, which is deliberate rather than an omission: both drop a cell from
    *scored performance*, and a stakes read is neither scored nor ranked, so
    excluding on them would shrink a panel to protect a figure they do not
    reach. ``metrics/README.md`` registers the carve-out, and a count here that
    differs from a board count is two populations rather than an error in
    either.
    """
    scoped: list[Evaluation] = []
    for path in sorted(cases_dir.glob("*/*/events/*/evaluations/*/*/*/evaluation.json")):
        evaluation = read_model(path, Evaluation)
        if in_scope(evaluation):
            scoped.append(evaluation)
    return latest_evaluations(scoped)


def big_case_agreement(
    data_root: Path, *, frozen_only: bool = True
) -> dict[str, BigCaseLeaderboard]:
    """Each predictor's big-case rank-agreement with the evaluator panel.

    Deterministic and offline over the committed ledger. For every
    ``(predictor, case, event)`` an evaluator gave a big-case read on, pairs the
    predictor's latest ``big_case_score`` with the **mean** of the panel's
    independent reads for that event, then correlates the predictor's ordering
    against the panel's with Kendall's tau-b (:func:`kendall_tau_b`) across the
    scored **cases**. A case carrying several forecast moments contributes one
    point, both sides averaged over its moments: big-caseness is a property of
    the case, so several points from one case would be non-independent
    observations in a correlation that assumes independence, and the count would
    be events wearing the name of cases. Predictors with no comparable case are
    absent from the map (their ``big_case`` stays null).

    ``frozen_only`` (the default) keeps only cells whose **scored** prediction —
    the run each evaluation's harness stamp names, latest as the legacy
    fallback — was produced by a frozen process, and only reads whose
    evaluation carries a harness stamp at or after the freeze instant, so this
    section defaults to the frozen headline exactly like the score aggregates —
    a shakedown big-case read never rides alongside a frozen-only board, even
    where its event was later re-run frozen. Within
    that scope each judge contributes one read per cell
    (:func:`_scoped_evaluations`), so a re-graded cell cannot weight its own
    judge twice inside the panel mean.
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return {}
    # Panel reads keyed per graded prediction run, not per event alone:
    # gradings that straddle a re-prediction judged different artifacts, so
    # each named run pairs with its own panel rather than folding two
    # questions into one mean. On an un-straddled ledger the grouping is
    # identical to a per-event one.
    reads: dict[tuple[str, str, str, str], tuple[float, list[float]]] = {}
    for evaluation in _scoped_evaluations(
        cases_dir,
        in_scope=lambda evaluation: (
            not frozen_only or graded_post_freeze(evaluation.process_version)
        ),
    ):
        if evaluation.big_case is None:
            continue
        scored = _scored_prediction(cases_dir, evaluation)
        if scored is None or scored.big_case_score is None:
            continue
        if frozen_only and not is_frozen(scored.process_version):
            continue
        key = (evaluation.predictor_id, evaluation.case_id, evaluation.event_id, scored.run_id)
        _, scores = reads.setdefault(key, (scored.big_case_score, []))
        scores.append(evaluation.big_case.evaluator_score)

    # Collapsed to the CASE, not the event. Big-caseness is a property of the
    # case — the same dispute is the same size at cert and at merits — so a
    # case carrying several forecast moments would otherwise contribute several
    # *non-independent* points to a rank correlation that treats its inputs as
    # independent, and `cases` would count events while calling them cases.
    per_case: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for (predictor_id, case_id, _event_id, _run_id), (own_score, evaluator_scores) in reads.items():
        panel_mean = sum(evaluator_scores) / len(evaluator_scores)
        per_case[(predictor_id, case_id)].append((own_score, panel_mean))

    points: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for (predictor_id, _case_id), moments_read in sorted(per_case.items()):
        predictor_mean = sum(own for own, _ in moments_read) / len(moments_read)
        panel_mean = sum(panel for _, panel in moments_read) / len(moments_read)
        points[predictor_id].append((predictor_mean, panel_mean))

    return {
        predictor_id: BigCaseLeaderboard(rank_agreement=kendall_tau_b(pairs), cases=len(pairs))
        for predictor_id, pairs in points.items()
    }


def _scored_prediction(cases_dir: Path, evaluation: Evaluation) -> Prediction | None:
    """The prediction this evaluation graded, or ``None``.

    :func:`fedcourtsai.store.scored_prediction` over the record's own fields —
    the same named-run-first join the stratified boards and the stamp use
    (latest by harness clock only as the legacy fallback), so the agreement
    views and the score aggregates read one graded artifact per cell.
    """
    return scored_prediction(
        cases_dir / evaluation.case_id / "events" / evaluation.event_id,
        evaluation.predictor_id,
        evaluation.prediction_run_id,
    )


def _scored_prediction_is_frozen(cases_dir: Path, evaluation: Evaluation) -> bool:
    """Whether the graded prediction ran a blessed process.

    One definition, shared by both agreement views, so a frozen-only big-case
    board and a frozen-only evaluator board always cover the same cells — the
    partition keys on the *scored prediction's* stamp because the predictor is
    the competitor being ranked, and on the scored run rather than the latest
    so a shakedown grading cannot enter a frozen view when its predictor
    later re-runs the event frozen.
    """
    scored = _scored_prediction(cases_dir, evaluation)
    return scored is not None and is_frozen(scored.process_version)


def evaluator_agreement(
    data_root: Path, *, frozen_only: bool = True
) -> dict[str, EvaluatorAgreement]:
    """Each evaluator's big-case rank-agreement with the rest of the panel.

    The grader-side counterpart to :func:`big_case_agreement`, and the check that
    function cannot make: it pairs each *predictor* against the panel mean, which
    is blind to a grader that is uniformly generous or strict, because such a bias
    lands on every predictor that grader scored and cancels out of the ordering.
    Comparing graders to each other is what surfaces it.

    **Leave-one-out.** An evaluator is scored against the mean of the *other*
    evaluators' reads on the events they share — never a panel mean including
    itself, which would correlate it partly with its own read and, on a
    three-judge panel, by a third.

    Shares :func:`big_case_agreement`'s ``frozen_only`` semantics, keyed on the
    *prediction's* stamp, **and its collapse to the case**, so both agreement
    views cover the same cells and can be read side by side. Collapsing only one
    of them would silently break that. It shares the run collapse for the same
    reason and one of its own: a re-graded cell would otherwise enter one
    judge's read twice into its own mean *and* into every peer's leave-one-out
    comparison.
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return {}
    # case -> evaluator_id -> every read that evaluator gave on it. One
    # evaluator scores every predictor for an event, and a case may carry
    # several forecast moments, so its read of the *case's* stakes is the mean
    # over both — the quantity a peer's read is comparable to. Keyed on the case
    # rather than the (case, event) pair for the same reason
    # `big_case_agreement` collapses: stakes are a property of the case, so two
    # moments would put two non-independent points into one correlation.
    reads: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for evaluation in _scoped_evaluations(
        cases_dir,
        in_scope=lambda evaluation: (
            not frozen_only
            or (
                graded_post_freeze(evaluation.process_version)
                and _scored_prediction_is_frozen(cases_dir, evaluation)
            )
        ),
    ):
        if evaluation.big_case is None:
            continue
        reads[evaluation.case_id][evaluation.evaluator_id].append(
            evaluation.big_case.evaluator_score
        )

    points: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for _case_id, panel in sorted(reads.items()):
        per_evaluator = {
            evaluator: sum(scores) / len(scores) for evaluator, scores in panel.items()
        }
        if len(per_evaluator) < 2:
            continue  # nothing to agree with on this case
        for evaluator, own in per_evaluator.items():
            peers = [v for other, v in per_evaluator.items() if other != evaluator]
            points[evaluator].append((own, sum(peers) / len(peers)))

    return {
        evaluator: EvaluatorAgreement(rank_agreement=kendall_tau_b(pairs), events=len(pairs))
        for evaluator, pairs in points.items()
    }


def skill_components(
    cells: Iterable[StratifiedCell],
    data_root: Path,
    statpack: StatPack | None,
) -> dict[EvaluationKey, CellSkill]:
    """Each scored cell's Brier and the baseline Brier of each skill column.

    The terms both columns aggregate from, resolved in one pass because both
    need the cell's realized outcome: a baseline Brier is
    ``(base_rate - actual_granted) ** 2``, and neither ``Evaluation`` carries
    ``actual_granted`` nor can the ratio recover it. See :class:`CellSkill` for
    why the terms travel rather than the ratios.

    **The prior-Term column** takes the baseline the cell records
    (``segment_base_rate``) over the population it already had: cells whose
    ``brier_skill_score`` is non-null, which the schema ties to a recorded rate
    and Brier. Only where its aggregation happens changes — plus the one drop
    :func:`_prior_baseline` adds: a cell whose recorded skill and recorded
    inputs disagree. An omission from ``skill_scored``, never a substituted
    value.

    **The realized-Term column** re-reads the same band from the case's own Term
    (:func:`fedcourtsai.pipeline.base_rates.realized_band_rate`, leave-one-out)
    instead of the strictly-prior pool. Holding the level at what obtained nets
    out level-knowledge and leaves **discrimination** — a predictor with the
    Term's level right but no ability to separate its cases scores positive on
    the prior-Term column and ~0 here — which is why the two are published side
    by side and never combined.

    **A per-cell decomposition, not a difference of the two columns.** The
    realized column's qualifying rules are narrower in practice and never the
    same set (``base_rate_basis`` is the evaluator's own field, so inclusion is
    a convention rather than a construction), so the two published figures run
    over different cells with different denominators and must not be subtracted
    from one another.

    **Computed here rather than carried on the cell.** A Term's own rate is
    term-to-date and keeps moving until the Term closes, so a value frozen onto
    an ``evaluation.json`` would record when the cell was graded, not what the
    Term did. Built from the ``statpack`` handed in, every cell on a board
    therefore shares one vintage, and the figure converges as the Term closes. A
    missing pack drops the realized column wholesale — the prior-Term column,
    which needs no pack, is unaffected.

    A cell qualifies for the realized column on four counts, each of which is an
    omission rather than a substitute where it fails. It must be **cert stage**:
    no other stage has a salience band, so none has a band rate to realize. It
    must carry a ``brier_score`` to score. Its recorded ``base_rate_basis`` must
    be ``risk_set``, so this number and the prior-Term number beside it describe
    the same band population — the ``terminal`` basis re-derives the band from
    the corpus row, which the committed ledger does not carry, so those cells
    are omitted rather than scored on a mismatched pairing. And the scored
    prediction — the run the evaluation's stamped ``prediction_run_id`` names,
    the join every scoring surface uses (latest as the legacy fallback) — must
    carry the frozen band, version, and Term the pairing is keyed on, so the
    realized rate and the ``brier_score`` it sits beside describe one
    prediction.
    """
    cases_dir = data_root / "cases"
    outcomes: dict[tuple[str, str], Outcome] = {}
    components: dict[EvaluationKey, CellSkill] = {}
    for evaluation, _stratum, stage, _moment in cells:
        if evaluation.brier_score is None:
            continue
        outcome = _read_outcome(cases_dir, evaluation, outcomes)
        prior = _prior_baseline(evaluation, outcome.actual_granted)
        realized = _baseline_brier(
            _realized_rate(cases_dir, evaluation, stage, outcome, statpack), outcome.actual_granted
        )
        if prior is None and realized is None:
            continue
        components[_evaluation_key(evaluation)] = CellSkill(
            brier=evaluation.brier_score,
            prior_term_baseline=prior,
            realized_term_baseline=realized,
        )
    return components


def _read_outcome(
    cases_dir: Path, evaluation: Evaluation, cache: dict[tuple[str, str], Outcome]
) -> Outcome:
    """The committed ``outcome.json`` a cell resolves against, read once per event."""
    event_key = (evaluation.case_id, evaluation.event_id)
    if event_key not in cache:
        event_dir = cases_dir / evaluation.case_id / "events" / evaluation.event_id
        cache[event_key] = read_model(event_dir / "outcome.json", Outcome)
    return cache[event_key]


def cell_facts(cells: Iterable[StratifiedCell], data_root: Path) -> dict[EvaluationKey, CellFacts]:
    """Each cert cell's frozen band key and realized-outcome facts.

    The inputs of ``by_band`` and of the realized floor fields on every stratum
    (:class:`CellFacts`). The band is read off the **scored** prediction — the
    run the evaluation's stamped ``prediction_run_id`` names, the join every
    scoring surface uses — so a cell sorts by the band its forecast was made
    under, never the corpus's current one. The always-deny figure is
    :func:`fedcourtsai.pipeline.evaluate.is_correct` itself, applied to the
    scored prediction with its call replaced by ``denied``, so the floor and
    ``Evaluation.correct`` answer to one exact-match rule; the scored
    prediction is re-scored too, so a grading whose stamped ``correct`` no
    longer reproduces against the committed outcome is detectable. A cell with no
    readable scored prediction is left out, which leaves its stratum's floor
    fields null rather than computing them over fewer cells than accuracy.
    """
    cases_dir = data_root / "cases"
    outcomes: dict[tuple[str, str], Outcome] = {}
    facts: dict[EvaluationKey, CellFacts] = {}
    for evaluation, _stratum, stage, _moment in cells:
        if stage != Stage.cert:
            continue
        scored = _scored_prediction(cases_dir, evaluation)
        if scored is None:
            continue
        outcome = _read_outcome(cases_dir, evaluation, outcomes)
        always_deny = scored.model_copy(
            update={"predicted_disposition": Disposition.denied, "judgment": None}
        )
        facts[_evaluation_key(evaluation)] = CellFacts(
            band_key=band_key(scored.context),
            always_deny_correct=is_correct(always_deny, outcome),
            recomputed_correct=is_correct(scored, outcome),
            grant_family=outcome.actual_disposition in GRANT_FAMILY_DISPOSITIONS,
        )
    return facts


def _baseline_brier(base_rate: float | None, actual_granted: int) -> float | None:
    """The Brier a constant ``base_rate`` forecaster scored on this outcome.

    ``None`` without a rate, and ``None`` when the baseline is already exact —
    the skill ratio's undefined case, dropped here exactly as
    :func:`fedcourtsai.pipeline.evaluate.brier_skill` drops it per cell, so a
    zero can never reach the aggregate's denominator. That exclusion is not
    neutral and is worth knowing when reading the column: an exact baseline is
    the baseline's *best* cell, one the forecast could only lose against, so
    dropping it nudges the published figure up. Both floors make it near
    unreachable — a band rate of exactly 0.0 or 1.0 has to survive the minimum
    resolved count — but the direction is fixed rather than random.
    """
    if base_rate is None:
        return None
    baseline = (base_rate - actual_granted) ** 2
    return baseline if baseline > 0 else None


#: How far a recorded ``brier_skill_score`` may sit from the value its own
#: recorded inputs imply before :func:`_prior_baseline` drops the cell. Loose
#: enough for an evaluator that rounded its own arithmetic (committed records
#: carry three decimals), tight enough that a skill taken against a different
#: band cannot pass — band rates differ several-fold, so a mismatch moves the
#: score far further than this.
#:
#: On the stages where ``stamp-cell`` writes the whole skill record (merits and
#: interim: the Brier, the base rate, and the ratio over them) the check passes
#: by construction — all three come from one set of inputs — so what it guards
#: in practice is the **cert** cell, whose three are the evaluator's own
#: arithmetic.
SKILL_COHERENCE_TOLERANCE = 1e-2


def _prior_baseline(evaluation: Evaluation, actual_granted: int) -> float | None:
    """The prior-Term baseline Brier this cell aggregates on, or ``None``.

    The column's **population** stays the recorded ``brier_skill_score``'s, so
    ``skill_scored`` keeps its documented meaning. Its **value** is derived from
    the cell's own recorded inputs — ``segment_base_rate`` against the realized
    outcome — because the aggregate needs the baseline term rather than the
    ratio, and a ratio cannot yield the term back on a cell whose Brier is zero.

    The two are one quantity computed two ways, and ``Evaluation`` enforces no
    relation between its fields, so the derivation is **checked against the
    record**: a cell whose recorded skill does not reproduce from its own
    recorded base rate and Brier is omitted — visibly, in ``skill_scored`` —
    rather than published on a baseline it was never graded against. The
    harness does not always *agree* — it declines to emit a disagreeing record:
    on the stages it pools itself the three come off one set of committed
    inputs, and on the stages where the trio stays the evaluator's,
    ``stamp-cell --regrade`` refuses a cell whose recorded Brier no longer
    reproduces against a corrected outcome rather than moving ``correct`` out
    from under it. A stale or hand-written record still need not agree.

    That check is the only one, and it is enough because the numbers are the
    evaluator's word only where a judgment had to be made: on merits and interim
    cells ``stamp-cell`` writes all three together — the Brier from the scored
    prediction and the outcome, the rate from the statpack
    (:func:`fedcourtsai.cli._skill_record_for`) — so no hand-computed number can
    reach the board to be caught, and the check passes trivially. On a **cert**
    cell all three are the evaluator's arithmetic against its own frozen band,
    and this is what stands between that arithmetic and the published column.
    """
    recorded_rate = evaluation.segment_base_rate
    if (
        recorded_rate is None
        or evaluation.brier_skill_score is None
        or evaluation.brier_score is None
    ):
        return None
    baseline = _baseline_brier(recorded_rate, actual_granted)
    if baseline is None:
        return None
    implied = 1.0 - evaluation.brier_score / baseline
    if not math.isclose(
        implied,
        evaluation.brier_skill_score,
        rel_tol=SKILL_COHERENCE_TOLERANCE,
        abs_tol=SKILL_COHERENCE_TOLERANCE,
    ):
        return None
    return baseline


def _realized_rate(
    cases_dir: Path,
    evaluation: Evaluation,
    stage: Stage | None,
    outcome: Outcome,
    statpack: StatPack | None,
) -> float | None:
    """This cell's realized-Term band rate, or ``None`` where it does not qualify."""
    if statpack is None or stage != Stage.cert or evaluation.base_rate_basis != "risk_set":
        return None
    scored = _scored_prediction(cases_dir, evaluation)
    context = scored.context if scored is not None else None
    if context is None or context.band is None:
        return None
    if context.salience_version is None or context.term is None:
        return None
    return realized_band_rate(
        context.band,
        context.salience_version,
        context.term,
        statpack,
        risk_set=True,
        # The pack's numerator, not the binary target: `granted-in-part` is a
        # granted outcome that keeps its own statpack bucket, so subtracting
        # `actual_granted` would remove a grant the published rate never counted.
        own_grant_family=int(outcome.actual_disposition in GRANT_FAMILY_DISPOSITIONS),
    )


def _group_by_predictor(
    cells: Sequence[tuple[Evaluation, Stratum]],
) -> dict[str, dict[Stratum, list[Evaluation]]]:
    """Group one stage's cells by predictor, keeping the strata apart."""
    by_predictor: dict[str, dict[Stratum, list[Evaluation]]] = defaultdict(
        lambda: {FORWARD: [], RETROSPECTIVE: [], PROCEDURAL: []}
    )
    for ev, stratum in cells:
        by_predictor[ev.predictor_id][stratum].append(ev)
    return by_predictor


def _stratum_total(
    by_predictor: Mapping[str, Mapping[Stratum, list[Evaluation]]], stratum: Stratum
) -> int:
    return sum(len(strata[stratum]) for strata in by_predictor.values())


def _events_scored(evals: Iterable[Evaluation]) -> int:
    """Distinct ``(case, event)`` pairs a set of evaluations covers.

    A **union**, which is why a board-level coverage figure can never be summed
    out of its entries: two predictors scored on one event are one event. That
    union is exactly the denominator the per-predictor count has to be read
    against — the grading gate works at ``(evaluator, event)`` grain, so a
    predictor whose cells landed after its events were graded is ranked over a
    subset of the board's scored set, and nothing else on the board shows it.
    """
    return len({(ev.case_id, ev.event_id) for ev in evals})


def _stage_board(
    cells: Sequence[tuple[Evaluation, Stratum]],
    skills: Mapping[EvaluationKey, CellSkill],
    facts: Mapping[EvaluationKey, CellFacts] | None,
) -> LeaderboardStage:
    """One non-cert stage's unranked block: per-predictor aggregates plus counts.

    The same per-stratum aggregation as the cert entries, but ordered by
    ``predictor_id`` and never ranked — a stage resolves on its own decision
    standard, so nothing here is comparable to the cert board or another stage.
    Only cert cells ever carry a realized-Term baseline, so a stage block's
    realized-Term figure is null and its count zero: the realized-Term rate is a
    *band* rate, and no other stage is a salience-band product. Their
    prior-Term skill is a separate question — the interim and merits stages both
    have a registered strictly-prior baseline of their own, each with its own
    floor.

    A later cert moment (``cert@cvsg``) is still a salience-band product, so
    its forward stratum carries ``by_band`` and the realized floor fields like
    the ranked board's; every other stage's cells carry no :class:`CellFacts`,
    so those stay null there.
    """
    by_predictor = _group_by_predictor(cells)
    entries: list[LeaderboardStageEntry] = []
    for predictor_id in sorted(by_predictor):
        strata = by_predictor[predictor_id]
        evals = strata[FORWARD] + strata[RETROSPECTIVE] + strata[PROCEDURAL]
        entries.append(
            LeaderboardStageEntry(
                predictor_id=predictor_id,
                evaluators=len({ev.evaluator_id for ev in evals}),
                events_scored=_events_scored(evals),
                forward=_aggregate(strata[FORWARD], skills, facts),
                retrospective=_aggregate(strata[RETROSPECTIVE], skills, facts),
                procedural=_aggregate(strata[PROCEDURAL], skills, facts),
                by_band=_by_band(strata[FORWARD], skills, facts),
            )
        )
    return LeaderboardStage(
        evaluations_total=sum(
            _stratum_total(by_predictor, stratum)
            for stratum in (FORWARD, RETROSPECTIVE, PROCEDURAL)
        ),
        events_scored=_events_scored(ev for ev, _ in cells),
        forward_evaluations=_stratum_total(by_predictor, FORWARD),
        retrospective_evaluations=_stratum_total(by_predictor, RETROSPECTIVE),
        procedural_evaluations=_stratum_total(by_predictor, PROCEDURAL),
        entries=entries,
        complete_grid_by_band=_complete_grid_by_band(cells, by_predictor, facts),
    )


def build_leaderboard(  # noqa: PLR0913 - one keyword per stratify-pass input the board publishes
    cells: Iterable[StratifiedCell],
    big_case: Mapping[str, BigCaseLeaderboard] | None = None,
    *,
    evaluators: Mapping[str, EvaluatorAgreement] | None = None,
    process_scope: Literal["frozen", "all"] = "frozen",
    skills: Mapping[EvaluationKey, CellSkill] | None = None,
    forward_claim: ForwardClaimRecord | None = None,
    leakage_exclusion: LeakageExclusionRecord | None = None,
    superseded_gradings: int = 0,
    facts: Mapping[EvaluationKey, CellFacts] | None = None,
) -> Leaderboard:
    """Roll stratified evaluations up into a best-first leaderboard.

        The ranked board is the **cert stage**: only cells whose event's stage is
        cert (as the join normalizes it — see
        :func:`fedcourtsai.store.iter_stratified_evaluations`) enter the top-level
        entries and counts. Any other stage aggregates alone into an unranked
        ``stages`` block keyed by the stage value (:data:`NO_STAGE_KEY` for a
        stage-less cell), because ``granted`` answers a different question at each
        stage — no skill or count figure is ever pooled across stages. (The
        ``big_case`` and ``evaluators`` maps the caller supplies are stage-blind by
        contract: they describe stakes reads, not stage-scoped skill.)

        One entry per predictor, each carrying its **forward** and **retrospective**
        aggregates separately (a stratum with no cells is null, never zero-filled
        into a blend). Entries rank by forward accuracy (desc, missing last),
        forward Brier (asc,
        missing last), the retrospective pair as tie-break, then ``predictor_id`` —
        a total order, so the ranking is deterministic even under ties. ``big_case``
        (from :func:`big_case_agreement`) attaches each predictor's big-case
        rank-agreement as a second, orthogonal dimension that never affects the rank;
        absent from the map (or unsupplied) leaves the entry's ``big_case`` null.

    ``skills`` (from :func:`skill_components` over the same cells) supplies both
        skill columns' terms — the cell's Brier and each baseline's — which are
        aggregated as a ratio of sums, never a mean of per-cell ratios
        (:class:`CellSkill`). The two columns keep separate populations and separate
        ``*_scored`` counts, are never combined, and neither reaches
        :func:`_rank_key`. Unsupplied, both columns are null everywhere with zero
        counts — the board still carries accuracy, Brier, and every count.

        ``process_scope`` only labels the board — the caller has already filtered
        ``cells`` and ``big_case`` to that scope (both via the shared ``frozen_only``
        seam). Recording it makes the empty frozen headline self-explaining rather
        than reading as a regression.

    ``forward_claim`` and ``leakage_exclusion`` are the caller's stratify pass's
        two exclusion records, carried verbatim. They are independent rules over
        one population — a cell both caught appears in both counts — so they are
        published side by side and never summed into an exclusion total.

    ``superseded_gradings`` is likewise the caller's to supply
        (``store.StratifiedRun.superseded``): ``cells`` holds only survivors of the
        run collapse, so by the time the board sees them a re-graded cell is
        indistinguishable from a once-graded one. Publishing the count beside the
        standings is what keeps a maintainer-reachable re-grade from moving a rank
        with nothing on any artifact recording that it happened. It must be the
        count from the same scoped pass that produced ``cells``; the default
        states "no collapse information supplied", which is also the truth for a
        board built from hand-made cells.

    ``facts`` (from :func:`cell_facts` over the same cells) supplies each cert
        cell's frozen band key and realized outcome: the forward stratum's
        ``by_band`` cut, every cert stratum's realized always-deny floor,
        lifts, and grant counts, and each population's
        ``complete_grid_by_band``. None of them reaches :func:`_rank_key`.
        Unsupplied, no entry carries ``by_band`` and those fields are null.
    """
    cell_skills = skills or {}
    cert_cells: list[tuple[Evaluation, Stratum]] = []
    stage_cells: dict[str, list[tuple[Evaluation, Stratum]]] = defaultdict(list)
    ranked = (Stage.cert, first_moment(Stage.cert))
    for ev, stratum, stage, moment in cells:
        if (stage, moment) == ranked:
            cert_cells.append((ev, stratum))
        else:
            stage_cells[stage_moment_key(stage, moment)].append((ev, stratum))

    by_predictor = _group_by_predictor(cert_cells)
    entries: list[LeaderboardEntry] = []
    for predictor_id, strata in by_predictor.items():
        evals = strata[FORWARD] + strata[RETROSPECTIVE] + strata[PROCEDURAL]
        entries.append(
            LeaderboardEntry(
                predictor_id=predictor_id,
                rank=1,  # provisional; assigned after sorting
                evaluators=len({ev.evaluator_id for ev in evals}),
                events_scored=_events_scored(evals),
                forward=_aggregate(strata[FORWARD], cell_skills, facts),
                retrospective=_aggregate(strata[RETROSPECTIVE], cell_skills, facts),
                procedural=_aggregate(strata[PROCEDURAL], cell_skills, facts),
                by_band=_by_band(strata[FORWARD], cell_skills, facts),
                big_case=(big_case or {}).get(predictor_id),
            )
        )

    entries.sort(key=_rank_key)
    for position, entry in enumerate(entries, start=1):
        entry.rank = position

    return Leaderboard(
        process_scope=process_scope,
        # Recorded on every build, `all` scope included: it states what the
        # freeze constants were, not that the partition was applied.
        frozen_process=frozen_process_record(),
        # The forward-claim rule and count the caller's stratify pass applied
        # (null only on a board constructed without the ledger in hand).
        forward_claim=forward_claim,
        # The same pass's leakage exclusion. An independent rule, so it rides
        # as its own block rather than folding into the count above.
        leakage_exclusion=leakage_exclusion,
        # The same pass's run-collapse count. The cells below are survivors, so
        # this is the only surface on which a re-grade is visible at all.
        superseded_gradings=superseded_gradings,
        # The gate versions the ranked cells' baselines were read under. Taken
        # from the harness-stamped `base_rate_salience_version` rather than
        # re-derived, so the board reports the version each cell was actually
        # scored against — including a cell frozen at a version the live pass
        # has since moved off.
        salience_versions=sorted(
            {ev.base_rate_salience_version for ev, _ in cert_cells if ev.base_rate_salience_version}
        ),
        predictors_ranked=len(entries),
        events_scored=_events_scored(ev for ev, _ in cert_cells),
        evaluations_total=sum(
            _stratum_total(by_predictor, stratum)
            for stratum in (FORWARD, RETROSPECTIVE, PROCEDURAL)
        ),
        forward_evaluations=_stratum_total(by_predictor, FORWARD),
        retrospective_evaluations=_stratum_total(by_predictor, RETROSPECTIVE),
        procedural_evaluations=_stratum_total(by_predictor, PROCEDURAL),
        evaluator_agreement=dict(evaluators or {}),
        entries=entries,
        complete_grid_by_band=_complete_grid_by_band(cert_cells, by_predictor, facts),
        stages={
            key: _stage_board(stage_cells[key], cell_skills, facts) for key in sorted(stage_cells)
        },
    )
