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
forward/retrospective enter the ranking. :func:`classify_stratum` is the single
definition of the timing split, derivable offline from committed artifacts (the
prediction's ``created_at`` vs the outcome's ``resolved_at``); the procedural
override lives with the join in ``store.iter_stratified_evaluations``.

Orthogonal to the strata runs the **stage/moment axis**: the ranked board is
cert's *first* forecast moment, and every other population — a different
decision standard (interim, merits), or the same standard forecast later in the
case's life (cert after a CVSG, merits after briefing) — aggregates into its own
unranked ``<stage>@<moment>`` block. Never pooled: ``granted`` answers a
different question at each stage, and a later moment answers the same question
with strictly more evidence.

Skill is reported twice, against two baselines that answer different questions
and are never combined. The evaluator's recorded ``brier_skill_score`` scores
against the **strictly-prior** pooled band rate: leakage-safe, the primary
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
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Literal

from .pipeline.evaluate import realized_band_rate
from .pipeline.moments import first_moment
from .process_version import frozen_process_record, graded_post_freeze, is_frozen
from .schemas import (
    GRANT_FAMILY_DISPOSITIONS,
    BigCaseLeaderboard,
    Evaluation,
    EvaluatorAgreement,
    Leaderboard,
    LeaderboardEntry,
    LeaderboardStage,
    LeaderboardStageEntry,
    LeaderboardStratum,
    Moment,
    Outcome,
    Prediction,
    Stage,
    StatPack,
    Stratum,
)
from .serialize import read_model

#: One scored cell's identity — ``(case, event, predictor, evaluator, run)``.
#: The join key for per-cell figures the board computes at render rather than
#: reading off the record, since ``Evaluation`` is not hashable.
EvaluationKey = tuple[str, str, str, str, str]

#: One joined cell as ``store.iter_stratified_evaluations`` yields it:
#: ``(evaluation, stratum, stage, moment)``. The stage and the moment travel
#: together because neither alone identifies the population a cell belongs to —
#: the stage names the question, the moment names the information set that
#: answered it.
StratifiedCell = tuple["Evaluation", "Stratum", "Stage | None", "Moment | None"]

FORWARD: Stratum = "forward"
RETROSPECTIVE: Stratum = "retrospective"
# Cells whose outcome was mootness practice (the outcome's disposition_basis):
# the ground-truth label tracks the Court's vacatur wording rather than
# cert-worthiness, so these aggregate separately and never enter the ranking.
PROCEDURAL: Stratum = "procedural"

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
# Accuracies are bounded in [0, 1]; a predictor with no cells in a stratum sorts
# after every predictor that has any, without colliding with a real worst score.
_NO_ACCURACY: float = -1.0


def classify_stratum(prediction_created_at: datetime, resolved_at: date) -> Stratum:
    """Which pre-registration stratum a scored cell belongs to.

    Retrospective when the event's resolution predates the prediction's commit.
    A same-day tie also counts as retrospective — the conservative reading, so a
    cell whose ordering within the day is unknowable is never presented as a
    forward forecast.
    """
    return RETROSPECTIVE if resolved_at <= prediction_created_at.date() else FORWARD


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
    under-forecast the rare event: on the current pack's `baseline` band an
    always-deny forecaster means to about +0.94 while the honest level-only
    forecaster means to about +0.002. The ratio of sums prices the same
    always-deny forecaster at about -0.05 and gives the level-only forecaster
    exactly 0, and it is stable under band mix, which a mean of ratios is not.

    A baseline is ``None`` where that column does not score the cell, so the two
    columns keep independent populations and independent counts.
    """

    brier: float
    prior_term_baseline: float | None = None
    realized_term_baseline: float | None = None


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
    evals: Sequence[Evaluation], skills: Mapping[EvaluationKey, CellSkill]
) -> LeaderboardStratum | None:
    """One stratum's aggregates, or ``None`` when the stratum has no evaluations.

    ``skills`` is :func:`skill_components`' per-cell map. A cell absent from a
    column's population is left out of that column entirely rather than entered
    as a zero, and each column publishes its own ``*_scored`` denominator. The
    two are never combined — different baselines, different questions.
    """
    if not evals:
        return None
    # Each skill column's own denominator rides beside it: a cell scores a
    # column only where that column's baseline exists, so the gap between it and
    # `evaluations` must be visible rather than silent.
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
        accuracy=sum(ev.correct for ev in evals) / len(evals),
        mean_brier_score=_mean([ev.brier_score for ev in evals if ev.brier_score is not None]),
        population_brier_skill_score=_skill_of_means(prior),
        skill_scored=len(prior),
        population_realized_term_skill_score=_skill_of_means(realized),
        realized_term_skill_scored=len(realized),
        mean_vote_accuracy=_mean(
            [ev.vote_accuracy for ev in evals if ev.vote_accuracy is not None]
        ),
        mean_reasoning_quality=_mean(
            [ev.reasoning_quality for ev in evals if ev.reasoning_quality is not None]
        ),
    )


def _rank_key(entry: LeaderboardEntry) -> tuple[float, float, float, float, str]:
    """Total order: forward stratum first, retrospective as tie-break, then id.

    Forward accuracy (desc) then forward Brier (asc, missing last) lead because
    only the forward stratum measures forecasting skill; the retrospective pair
    orders predictors that have no forward cells yet. The procedural stratum
    never contributes — vacatur-practice calls buy no rank. ``predictor_id`` makes the
    ranking deterministic under full ties.

    No skill column is a rank key, and the realized-Term one could not be: it
    scores against a rate no predictor could have known in-season, so ranking on
    it would rank in-season on an ex-post fact.
    """

    def acc(stratum: LeaderboardStratum | None) -> float:
        return stratum.accuracy if stratum is not None else _NO_ACCURACY

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

    ``frozen_only`` (the default) keeps only events whose latest prediction was
    produced by a frozen process, and only reads whose evaluation carries a harness stamp at or
    after the freeze instant, so this section defaults to the frozen headline exactly like the
    score aggregates — a shakedown big-case read never rides alongside a
    frozen-only board, even where its event was later re-run frozen.
    """
    cases_dir = data_root / "cases"
    if not cases_dir.exists():
        return {}
    reads: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for path in sorted(cases_dir.glob("*/*/events/*/evaluations/*/*/*/evaluation.json")):
        evaluation = read_model(path, Evaluation)
        if evaluation.big_case is None:
            continue
        if frozen_only and not graded_post_freeze(evaluation.process_version):
            continue
        key = (evaluation.predictor_id, evaluation.case_id, evaluation.event_id)
        reads[key].append(evaluation.big_case.evaluator_score)

    # Collapsed to the CASE, not the event. Big-caseness is a property of the
    # case — the same dispute is the same size at cert and at merits — so a
    # case carrying several forecast moments would otherwise contribute several
    # *non-independent* points to a rank correlation that treats its inputs as
    # independent, and `cases` would count events while calling them cases.
    per_case: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for (predictor_id, case_id, event_id), evaluator_scores in reads.items():
        latest = _latest_prediction(cases_dir, case_id, event_id, predictor_id)
        if latest is None:
            continue
        if frozen_only and not is_frozen(latest.process_version):
            continue
        if latest.big_case_score is None:
            continue
        panel_mean = sum(evaluator_scores) / len(evaluator_scores)
        per_case[(predictor_id, case_id)].append((latest.big_case_score, panel_mean))

    points: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for (predictor_id, _case_id), moments_read in sorted(per_case.items()):
        predictor_mean = sum(own for own, _ in moments_read) / len(moments_read)
        panel_mean = sum(panel for _, panel in moments_read) / len(moments_read)
        points[predictor_id].append((predictor_mean, panel_mean))

    return {
        predictor_id: BigCaseLeaderboard(rank_agreement=kendall_tau_b(pairs), cases=len(pairs))
        for predictor_id, pairs in points.items()
    }


def _latest_prediction(
    cases_dir: Path, case_id: str, event_id: str, predictor_id: str
) -> Prediction | None:
    """The newest prediction a predictor wrote for an event, or ``None``."""
    files = sorted(
        (cases_dir / case_id / "events" / event_id).glob(
            f"predictions/{predictor_id}/*/prediction.json"
        )
    )
    predictions = [read_model(p, Prediction) for p in files]
    if not predictions:
        return None
    return max(predictions, key=lambda pr: pr.created_at)


def _latest_prediction_is_frozen(
    cases_dir: Path, case_id: str, event_id: str, predictor_id: str
) -> bool:
    """Whether that prediction ran a blessed process.

    One definition, shared by both agreement views, so a frozen-only big-case
    board and a frozen-only evaluator board always cover the same cells — the
    partition keys on the *prediction's* stamp because the predictor is the
    competitor being ranked.
    """
    latest = _latest_prediction(cases_dir, case_id, event_id, predictor_id)
    return latest is not None and is_frozen(latest.process_version)


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
    of them would silently break that.
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
    for path in sorted(cases_dir.glob("*/*/events/*/evaluations/*/*/*/evaluation.json")):
        evaluation = read_model(path, Evaluation)
        if evaluation.big_case is None:
            continue
        if frozen_only and not (
            graded_post_freeze(evaluation.process_version)
            and _latest_prediction_is_frozen(
                cases_dir, evaluation.case_id, evaluation.event_id, evaluation.predictor_id
            )
        ):
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

    **The prior-Term column** takes the baseline the evaluator recorded
    (``segment_base_rate``) over the population it already had: cells whose
    ``brier_skill_score`` is non-null, which the schema ties to a recorded rate
    and Brier. Only where its aggregation happens changes — plus the coherence
    check :func:`_prior_baseline` adds, which drops a cell whose recorded skill
    and recorded inputs disagree rather than publishing either.

    **The realized-Term column** re-reads the same band from the case's own Term
    (:func:`fedcourtsai.pipeline.evaluate.realized_band_rate`, leave-one-out)
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
    prediction — the predictor's **latest** for the event, the join every
    scoring surface uses — must carry the frozen band, version, and Term the
    pairing is keyed on.
    """
    cases_dir = data_root / "cases"
    outcomes: dict[tuple[str, str], Outcome] = {}
    components: dict[EvaluationKey, CellSkill] = {}
    for evaluation, _stratum, stage, _moment in cells:
        if evaluation.brier_score is None:
            continue
        event_key = (evaluation.case_id, evaluation.event_id)
        if event_key not in outcomes:
            event_dir = cases_dir / evaluation.case_id / "events" / evaluation.event_id
            outcomes[event_key] = read_model(event_dir / "outcome.json", Outcome)
        outcome = outcomes[event_key]
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
_SKILL_COHERENCE_TOLERANCE = 1e-2


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
    rather than published on a baseline it was never graded against. Harness
    output always agrees; a stale or hand-written record need not.
    """
    if evaluation.brier_skill_score is None or evaluation.brier_score is None:
        return None
    baseline = _baseline_brier(evaluation.segment_base_rate, actual_granted)
    if baseline is None:
        return None
    implied = 1.0 - evaluation.brier_score / baseline
    if not math.isclose(
        implied,
        evaluation.brier_skill_score,
        rel_tol=_SKILL_COHERENCE_TOLERANCE,
        abs_tol=_SKILL_COHERENCE_TOLERANCE,
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
    latest = _latest_prediction(
        cases_dir, evaluation.case_id, evaluation.event_id, evaluation.predictor_id
    )
    context = latest.context if latest is not None else None
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


def _stage_board(
    cells: Sequence[tuple[Evaluation, Stratum]], skills: Mapping[EvaluationKey, CellSkill]
) -> LeaderboardStage:
    """One non-cert stage's unranked block: per-predictor aggregates plus counts.

    The same per-stratum aggregation as the cert entries, but ordered by
    ``predictor_id`` and never ranked — a stage resolves on its own decision
    standard, so nothing here is comparable to the cert board or another stage.
    Only cert cells ever carry a realized-Term baseline, so a stage block's
    realized-Term figure is null and its count zero — the same shape the interim
    block's prior-Term skill already has, and for the same reason: no other
    stage publishes a band rate.
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
                forward=_aggregate(strata[FORWARD], skills),
                retrospective=_aggregate(strata[RETROSPECTIVE], skills),
                procedural=_aggregate(strata[PROCEDURAL], skills),
            )
        )
    return LeaderboardStage(
        evaluations_total=sum(
            _stratum_total(by_predictor, stratum)
            for stratum in (FORWARD, RETROSPECTIVE, PROCEDURAL)
        ),
        forward_evaluations=_stratum_total(by_predictor, FORWARD),
        retrospective_evaluations=_stratum_total(by_predictor, RETROSPECTIVE),
        procedural_evaluations=_stratum_total(by_predictor, PROCEDURAL),
        entries=entries,
    )


def build_leaderboard(
    cells: Iterable[StratifiedCell],
    big_case: Mapping[str, BigCaseLeaderboard] | None = None,
    *,
    evaluators: Mapping[str, EvaluatorAgreement] | None = None,
    process_scope: Literal["frozen", "all"] = "frozen",
    skills: Mapping[EvaluationKey, CellSkill] | None = None,
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
        into a blend). Entries rank by forward accuracy (desc), forward Brier (asc,
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
                forward=_aggregate(strata[FORWARD], cell_skills),
                retrospective=_aggregate(strata[RETROSPECTIVE], cell_skills),
                procedural=_aggregate(strata[PROCEDURAL], cell_skills),
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
        # The gate versions the ranked cells' baselines were read under. Taken
        # from the harness-stamped `base_rate_salience_version` rather than
        # re-derived, so the board reports the version each cell was actually
        # scored against — including a cell frozen at a version the live pass
        # has since moved off.
        salience_versions=sorted(
            {ev.base_rate_salience_version for ev, _ in cert_cells if ev.base_rate_salience_version}
        ),
        predictors_ranked=len(entries),
        evaluations_total=sum(
            _stratum_total(by_predictor, stratum)
            for stratum in (FORWARD, RETROSPECTIVE, PROCEDURAL)
        ),
        forward_evaluations=_stratum_total(by_predictor, FORWARD),
        retrospective_evaluations=_stratum_total(by_predictor, RETROSPECTIVE),
        procedural_evaluations=_stratum_total(by_predictor, PROCEDURAL),
        evaluator_agreement=dict(evaluators or {}),
        entries=entries,
        stages={key: _stage_board(stage_cells[key], cell_skills) for key in sorted(stage_cells)},
    )
