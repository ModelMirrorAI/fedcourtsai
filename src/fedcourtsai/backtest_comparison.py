"""Back-test comparison: one predictor's candidate against its incumbent, and the pooled record.

Two things the standing back-tests cannot do on their own, both built on their
replays rather than beside them:

- **A paired comparison.** One predictor is replayed twice over the same drawn
  cases, at the same moments, from identically provisioned records under the
  same replay clock: once as the registry configures it (the incumbent) and
  once with the one change under test (the candidate: another model, or
  another prompt). The report is the per-cell Brier difference, its mean, a
  paired interval, and which way the binary call moved. Pairing is the point:
  the case-to-case variation both arms share cancels in the difference, so a
  set far too small to rank two predictors can still separate two versions of
  one.
- **A pooled record.** Every scored replay cell a model ran is appended to
  ``metrics/backtest-record/`` as one file per run, and
  :func:`pool_record` reads them back per (predictor, model, process digest)
  and population, never across them, so the handfuls of cells that recorded
  replays score accumulate into a sample.

Everything here is retrospective. A comparison is evidence for a re-bless
decision between two configurations; it is never a claimable performance
figure, and no replay cell counts toward a forward board.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date
from pathlib import Path
from typing import Final, Literal

from . import corpus
from .backtest import BacktestItem
from .cert_backtest import (
    ReplayArm,
    ReplayedBacktester,
    ReplayOutcome,
    cert_stratum,
    replay_predictors,
)
from .merits_backtest import MeritsReplayCase, MeritsReplayOutcome, replay_merits_predictors
from .pipeline import moments
from .pipeline.outcome import granted_flag
from .schemas import (
    BacktestArmRole,
    BacktestComparisonArm,
    BacktestComparisonKind,
    BacktestComparisonMoment,
    BacktestComparisonPair,
    BacktestComparisonStratum,
    BacktestComparisonStratumFigures,
    BacktestPairedFigures,
    BacktestPooled,
    BacktestPooledEntry,
    BacktestPooledStratum,
    BacktestRecordRow,
    Moment,
    Stage,
)

#: The coverage every paired interval is stated at.
INTERVAL_LEVEL: Final = 0.95

#: The stratum weight above which a stratified figure carries no interval. One
#: class then supplies nearly all of the estimate and of its variance, and that
#: class's differences are near-constant with rare large moves: a handful of
#: pairs usually draws none of the large ones, so the sample variance
#: understates the spread and a t interval built on it covers far less often
#: than its level says. No resampling interval repairs that, since none can see
#: a move the sample did not draw. The estimate is still reported.
DOMINANT_STRATUM_WEIGHT: Final = 0.8

#: Vendor-stated training data cutoffs (each vendor's model documentation
#: states a month), as the last day of the stated month: a case decided inside
#: the month is treated as inside the training data. A stated month is
#: approximate, so a pair just after it is only probably unseen. Only models
#: with a published cutoff are listed. A model absent here has no
#: recorded cutoff, and a comparison naming it reports that rather than
#: assuming one.
MODEL_TRAINING_CUTOFFS: Final[dict[str, date]] = {
    "claude-opus-5-5": date(2026, 6, 30),
    "claude-fable-5-2": date(2026, 6, 30),
}

#: Where the pooled record's per-run files live, under the metrics root.
RECORD_DIRNAME: Final = "backtest-record"

#: Where comparison reports live, under the metrics root.
COMPARISONS_DIRNAME: Final = "backtest-comparisons"


def training_cutoff(model: str | None) -> date | None:
    """The recorded training data cutoff of ``model``, or ``None`` where none is recorded."""
    return MODEL_TRAINING_CUTOFFS.get(model) if model is not None else None


# --------------------------------------------------------------------------
# The Student-t quantile, which the interval needs and the standard library
# does not carry.
# --------------------------------------------------------------------------


def _betacf(a: float, b: float, x: float) -> float:
    """The continued fraction of the incomplete beta function (modified Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h


def _regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    front = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def _student_t_cdf(t: float, df: float) -> float:
    tail = 0.5 * _regularized_incomplete_beta(df / 2.0, 0.5, df / (df + t * t))
    return 1.0 - tail if t >= 0 else tail


def student_t_quantile(probability: float, df: float) -> float:
    """The ``probability`` quantile of Student's t with ``df`` degrees of freedom.

    ``df`` may be fractional (the Satterthwaite approximation gives one).
    Solved by bisection on the CDF, which is exact to the tolerance and needs
    no table.
    """
    if not 0.0 < probability < 1.0:
        raise ValueError(f"probability must be in (0, 1), not {probability}")
    if df <= 0:
        raise ValueError(f"degrees of freedom must be positive, not {df}")
    if probability == 0.5:
        return 0.0
    if probability < 0.5:
        return -student_t_quantile(1.0 - probability, df)
    low, high = 0.0, 1.0
    while _student_t_cdf(high, df) < probability:
        high *= 2.0
    for _ in range(200):
        mid = (low + high) / 2.0
        if _student_t_cdf(mid, df) < probability:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


# --------------------------------------------------------------------------
# The paired figures.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ArmForecast:
    """What one arm said on one cell: its probability and its binary call."""

    probability: float
    positive_call: bool


@dataclass(frozen=True)
class PairedCell:
    """One replayed cell and what each arm returned for it; ``None`` is a lost cell."""

    case_id: str
    moment: str
    outcome: int
    decided: date | None
    stratum: str | None
    provisioning: str | None
    incumbent: ArmForecast | None
    candidate: ArmForecast | None

    @property
    def paired(self) -> bool:
        return self.incumbent is not None and self.candidate is not None


def _brier(forecast: ArmForecast, outcome: int) -> float:
    return (forecast.probability - outcome) ** 2


def _difference(cell: PairedCell) -> float:
    assert cell.incumbent is not None and cell.candidate is not None
    return _brier(cell.candidate, cell.outcome) - _brier(cell.incumbent, cell.outcome)


def _call(cell: PairedCell) -> Literal["same", "to-correct", "to-wrong"]:
    assert cell.incumbent is not None and cell.candidate is not None
    truth = bool(cell.outcome)
    incumbent_right = cell.incumbent.positive_call == truth
    candidate_right = cell.candidate.positive_call == truth
    if incumbent_right == candidate_right:
        return "same"
    return "to-correct" if candidate_right else "to-wrong"


def _mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _variance(values: Sequence[float]) -> float:
    """The sample variance (n - 1); zero below two values."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def _call_counts(cells: Sequence[PairedCell]) -> dict[str, int]:
    calls = [_call(cell) for cell in cells]
    return {
        "calls_changed": sum(1 for call in calls if call != "same"),
        "changed_to_correct": calls.count("to-correct"),
        "changed_to_wrong": calls.count("to-wrong"),
    }


def paired_figures(
    cells: Iterable[PairedCell], *, level: float = INTERVAL_LEVEL
) -> BacktestPairedFigures:
    """The unweighted paired difference over the cells both arms scored.

    Every pair counts once, so the figure describes the set as drawn. The
    interval is the Student-t interval on the per-cell differences, with
    ``pairs - 1`` degrees of freedom; it is null below two pairs and where
    every difference is the same.
    """
    both = [cell for cell in cells if cell.paired]
    differences = [_difference(cell) for cell in both]
    mean = _mean(differences)
    low = high = df = None
    variance = _variance(differences)
    # Identical differences give no spread to build an interval from: a
    # zero-width interval would state a certainty the sample cannot support.
    if mean is not None and len(differences) >= 2 and variance > 0:
        df = float(len(differences) - 1)
        half = student_t_quantile(1.0 - (1.0 - level) / 2.0, df) * math.sqrt(
            variance / len(differences)
        )
        low, high = mean - half, mean + half
    return BacktestPairedFigures(
        pairs=len(both),
        positives=sum(cell.outcome for cell in both),
        incumbent_mean_brier=_mean([_brier(c.incumbent, c.outcome) for c in both if c.incumbent]),
        candidate_mean_brier=_mean([_brier(c.candidate, c.outcome) for c in both if c.candidate]),
        mean_brier_difference=mean,
        interval_low=low,
        interval_high=high,
        degrees_of_freedom=df,
        level=level,
        estimator="unweighted",
        **_call_counts(both),
    )


def stratified_figures(
    cells: Iterable[PairedCell],
    weights: Mapping[str, float],
    *,
    level: float = INTERVAL_LEVEL,
) -> BacktestPairedFigures | None:
    """The paired difference with each stratum's mean weighted by its population share.

    The standard stratified estimator: the estimate is ``sum(W_h * mean_h)``
    and its variance ``sum(W_h^2 * s_h^2 / n_h)``, with the Satterthwaite
    degrees of freedom for the t interval. No finite-population correction is
    taken, which only widens the interval. ``None`` where a stratum with a
    positive weight holds no pair, since there is then nothing to weight. The
    interval alone is null where such a stratum holds one pair, where the
    differences show no spread, and where one stratum's weight exceeds
    :data:`DOMINANT_STRATUM_WEIGHT`. The call counts are plain counts of
    pairs, not reweighted.
    """
    both = [cell for cell in cells if cell.paired]
    by_stratum: dict[str, list[PairedCell]] = defaultdict(list)
    for cell in both:
        if cell.stratum is not None:
            by_stratum[cell.stratum].append(cell)
    weighted = {stratum: weight for stratum, weight in weights.items() if weight > 0}
    total = sum(weighted.values())
    if not weighted or total <= 0 or any(not by_stratum.get(stratum) for stratum in weighted):
        return None
    shares = {stratum: weight / total for stratum, weight in weighted.items()}
    counted = [cell for stratum in shares for cell in by_stratum[stratum]]
    estimate = 0.0
    terms: list[tuple[float, int]] = []  # each stratum's variance term and its pair count
    for stratum, share in shares.items():
        differences = [_difference(cell) for cell in by_stratum[stratum]]
        estimate += share * sum(differences) / len(differences)
        terms.append((share**2 * _variance(differences) / len(differences), len(differences)))
    # The two arm means are share-weighted means of stratum means too.
    incumbent_mean = sum(
        share * (_mean([_brier(c.incumbent, c.outcome) for c in by_stratum[s] if c.incumbent]) or 0)
        for s, share in shares.items()
    )
    candidate_mean = sum(
        share * (_mean([_brier(c.candidate, c.outcome) for c in by_stratum[s] if c.candidate]) or 0)
        for s, share in shares.items()
    )
    low = high = df = None
    variance = sum(term for term, _ in terms)
    if (
        all(count >= 2 for _, count in terms)
        and variance > 0
        and max(shares.values()) <= DOMINANT_STRATUM_WEIGHT
    ):
        denominator = sum(term**2 / (count - 1) for term, count in terms)
        df = (
            variance**2 / denominator
            if denominator > 0
            else float(sum(count - 1 for _, count in terms))
        )
        half = student_t_quantile(1.0 - (1.0 - level) / 2.0, df) * math.sqrt(variance)
        low, high = estimate - half, estimate + half
    return BacktestPairedFigures(
        pairs=len(counted),
        positives=sum(cell.outcome for cell in counted),
        incumbent_mean_brier=incumbent_mean,
        candidate_mean_brier=candidate_mean,
        mean_brier_difference=estimate,
        interval_low=low,
        interval_high=high,
        degrees_of_freedom=df,
        level=level,
        estimator="stratified",
        **_call_counts(counted),
    )


def stratum_figures(cells: Iterable[PairedCell]) -> list[BacktestComparisonStratumFigures]:
    """The paired difference within each stratum, in stratum order.

    The reading a dominated population figure rests on: how many pairs each
    class holds, their mean difference, and the largest single move seen.
    """
    by_stratum: dict[str, list[float]] = defaultdict(list)
    for cell in cells:
        if cell.paired and cell.stratum is not None:
            by_stratum[cell.stratum].append(_difference(cell))
    return [
        BacktestComparisonStratumFigures(
            stratum=stratum,
            pairs=len(differences),
            mean_brier_difference=sum(differences) / len(differences),
            largest_absolute_difference=max(abs(d) for d in differences),
        )
        for stratum, differences in sorted(by_stratum.items())
    ]


def _after_both(cell: PairedCell, cutoffs: Sequence[date | None]) -> bool | None:
    """Whether the cell's outcome postdates every arm's training cutoff, if that is known."""
    known = [cutoff for cutoff in cutoffs if cutoff is not None]
    if cell.decided is None or len(known) != len(cutoffs) or not known:
        return None
    return cell.decided > max(known)


def comparison_pairs(
    cells: Iterable[PairedCell], cutoffs: Sequence[date | None]
) -> list[BacktestComparisonPair]:
    """The report's per-cell rows, in (moment, case) order."""
    return [
        BacktestComparisonPair(
            case_id=cell.case_id,
            moment=cell.moment,
            outcome=cell.outcome,
            decided=cell.decided,
            stratum=cell.stratum,
            provisioning=cell.provisioning,
            incumbent_probability=cell.incumbent.probability if cell.incumbent else None,
            candidate_probability=cell.candidate.probability if cell.candidate else None,
            brier_difference=_difference(cell) if cell.paired else None,
            call=_call(cell) if cell.paired else None,
            after_both_cutoffs=_after_both(cell, cutoffs),
        )
        for cell in sorted(cells, key=lambda c: (c.moment, c.case_id))
    ]


def comparison_moments(
    cells: Sequence[PairedCell],
    moments: Sequence[str],
    strata: Sequence[BacktestComparisonStratum],
    cutoffs: Sequence[date | None],
) -> list[BacktestComparisonMoment]:
    """The paired figures per moment: as drawn, reweighted, and after both cutoffs."""
    weights = {stratum.stratum: stratum.weight for stratum in strata}
    cutoffs_known = bool(cutoffs) and all(cutoff is not None for cutoff in cutoffs)
    out = []
    for moment in moments:
        at = [cell for cell in cells if cell.moment == moment]
        out.append(
            BacktestComparisonMoment(
                moment=moment,
                cells=len(at),
                drawn_set=paired_figures(at),
                population=stratified_figures(at, weights) if weights else None,
                by_stratum=stratum_figures(at),
                after_both_cutoffs=(
                    paired_figures([cell for cell in at if _after_both(cell, cutoffs)])
                    if cutoffs_known
                    else None
                ),
            )
        )
    return out


def exposure_note(
    pairs: Sequence[BacktestComparisonPair], arms: Sequence[BacktestComparisonArm]
) -> str:
    """One sentence on what the recorded cutoffs let the report say about recall."""
    unrecorded = sorted({arm.requested_model for arm in arms if arm.training_cutoff is None})
    if unrecorded:
        return (
            f"No training cutoff is recorded for {', '.join(unrecorded)}, so no pair can be "
            "placed after both arms' cutoffs: every difference here may include recall of "
            "the outcome, which favours whichever model was trained later."
        )
    latest = max(arm.training_cutoff for arm in arms if arm.training_cutoff is not None)
    scored = [pair for pair in pairs if pair.brier_difference is not None]
    clean = sum(1 for pair in scored if pair.after_both_cutoffs)
    if clean == 0:
        return (
            f"No scored pair was decided after both arms' training cutoffs (the later is "
            f"{latest.isoformat()}), so every difference here may include recall of the "
            "outcome and none isolates forecasting."
        )
    return (
        f"{clean} of {len(scored)} scored pair(s) were decided after both arms' training "
        f"cutoffs (the later is {latest.isoformat()}); the `after_both_cutoffs` figures "
        "are over those alone, and the rest may include recall of the outcome."
    )


def arm_record(
    role: Literal["incumbent", "candidate"],
    *,
    engine: str | None,
    model: str | None,
    requested_model: str,
    prompt: str,
    process_digest: str,
    cells: Sequence[PairedCell],
) -> BacktestComparisonArm:
    """One arm's block of the report, its counts read off the paired cells."""
    scored = sum(1 for cell in cells if (cell.incumbent if role == "incumbent" else cell.candidate))
    return BacktestComparisonArm(
        role=role,
        engine=engine,
        model=model,
        requested_model=requested_model,
        prompt=prompt,
        process_digest=process_digest,
        training_cutoff=training_cutoff(requested_model),
        cells_scored=scored,
        cells_lost=len(cells) - scored,
    )


# --------------------------------------------------------------------------
# The pooled record.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ScoredCell:
    """One scored replay cell, as the record keeps it."""

    case_id: str
    stage: str
    moment: str
    probability: float
    outcome: int
    decided: date | None
    provisioning: str | None
    stratum: str
    stratum_share: float | None


def record_rows(  # noqa: PLR0913 - one field of the row per argument
    cells: Iterable[ScoredCell],
    *,
    kind: BacktestComparisonKind,
    population: str,
    run_id: str,
    predictor_id: str,
    arm: BacktestArmRole,
    engine: str | None,
    model: str | None,
    process_digest: str,
    draw_rule: str,
) -> list[BacktestRecordRow]:
    """The record rows of one predictor's scored cells, or none for an offline backend.

    A backend that invoked no model (the ``stub`` rehearsal) produced no
    forecast worth pooling, so its cells are never recorded.
    """
    if engine is None or model is None:
        return []
    return [
        BacktestRecordRow(
            kind=kind,
            population=population,
            run_id=run_id,
            predictor_id=predictor_id,
            arm=arm,
            engine=engine,
            model=model,
            process_digest=process_digest,
            case_id=cell.case_id,
            stage=cell.stage,
            moment=cell.moment,
            probability=cell.probability,
            outcome=cell.outcome,
            decided=cell.decided,
            provisioning=cell.provisioning,
            draw_rule=draw_rule,
            stratum=cell.stratum,
            stratum_share=cell.stratum_share,
        )
        for cell in cells
    ]


def record_path(metrics_root: Path, kind: str, run_id: str) -> Path:
    """The record file of one replay run."""
    return metrics_root / RECORD_DIRNAME / f"{kind}-{run_id}.jsonl"


def write_record(path: Path, rows: Sequence[BacktestRecordRow]) -> bool:
    """Write one run's rows to its own record file; ``False`` (nothing written) with no rows.

    Append-only at the level of the record: a run adds a file and no file is
    ever rewritten, so an existing path is refused rather than replaced.
    """
    if not rows:
        return False
    if path.exists():
        raise FileExistsError(f"{path} already exists; a record file is never rewritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows, key=lambda r: (r.predictor_id, r.arm, r.moment, r.case_id))
    path.write_text(
        "".join(
            json.dumps(row.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"
            for row in ordered
        ),
        encoding="utf-8",
    )
    return True


def read_record(root: Path) -> tuple[int, list[BacktestRecordRow]]:
    """Every row under the record directory ``root``, with the number of files read."""
    files = sorted(root.glob("*.jsonl")) if root.is_dir() else []
    rows = [
        BacktestRecordRow.model_validate_json(line)
        for file in files
        for line in file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return len(files), rows


#: How far the pooled strata's shares may sum from one and still count as the
#: whole population: room for the mix moving between vintages, none for a
#: missing class.
_SHARE_TOLERANCE: Final = 0.02


def _pooled_entry(
    key: tuple[str, str, str, str, str, str, str], rows: Sequence[BacktestRecordRow]
) -> BacktestPooledEntry:
    predictor_id, model, digest, kind, population, stage, moment = key
    weighted = [row for row in rows if row.stratum_share is not None]
    by_stratum: dict[str, list[BacktestRecordRow]] = defaultdict(list)
    for row in weighted:
        by_stratum[row.stratum].append(row)
    # A stratum's share is the mean over the runs that recorded it, each run
    # counted once however many rows it holds: the runs drew from one named
    # population at different vintages, and its outcome mix moves a little
    # between them.
    raw = {}
    for stratum, members in by_stratum.items():
        per_run = {row.run_id: row.stratum_share or 0.0 for row in members}
        raw[stratum] = sum(per_run.values()) / len(per_run)
    total = sum(raw.values())
    strata = []
    # The shares of a population's strata sum to one. Where the strata present
    # fall short of that, a class with weight in the population holds no cell,
    # and a mean over the rest would be that class-less figure passed off as
    # the population's: the combined figure is withheld and the class means
    # stand alone.
    complete = bool(raw) and abs(total - 1.0) <= _SHARE_TOLERANCE
    combined: float | None = 0.0 if complete else None
    for stratum in sorted(by_stratum):
        members = by_stratum[stratum]
        per_case: dict[str, list[float]] = defaultdict(list)
        for row in members:
            per_case[row.case_id].append((row.probability - row.outcome) ** 2)
        # A case replayed in several runs is averaged first, so it counts once.
        mean = sum(sum(v) / len(v) for v in per_case.values()) / len(per_case)
        share = raw[stratum] / total if total > 0 else 0.0
        if combined is not None:
            combined += share * mean
        strata.append(
            BacktestPooledStratum(
                stratum=stratum,
                rows=len(members),
                cases=len(per_case),
                share=share,
                mean_brier_score=mean,
            )
        )
    return BacktestPooledEntry(
        predictor_id=predictor_id,
        model=model,
        process_digest=digest,
        kind=kind,
        population=population,
        stage=stage,
        moment=moment,
        runs=len({row.run_id for row in rows}),
        rows=len(rows),
        cases=len({row.case_id for row in rows}),
        unweighted_rows=len(rows) - len(weighted),
        strata=strata,
        mean_brier_score=combined,
    )


def pool_record(files: int, rows: Sequence[BacktestRecordRow]) -> BacktestPooled:
    """Pool the record per (predictor, model, process digest, population, moment).

    Never across them: two models, two prompts, or two populations are
    different measurements, and a mean over them describes neither. Within
    one key the figure is post-stratified on the outcome class: each
    stratum's mean Brier over its distinct cases, combined at the population
    share the rows recorded. A simple random run and an outcome-stratified
    run sample at random within an outcome class alike, so both feed the same
    stratum means, and the combination returns the population figure whatever
    mix of runs supplied the cells.

    The combination is exact only as far as replayable coverage is ignorable
    within an outcome class, which it is not known to be; a row with no
    recorded share (a ``recency-head`` draw, which is not a probability
    sample) is counted and left out of every figure.
    """
    grouped: dict[tuple[str, str, str, str, str, str, str], list[BacktestRecordRow]] = defaultdict(
        list
    )
    for row in rows:
        grouped[
            (
                row.predictor_id,
                row.model,
                row.process_digest,
                row.kind,
                row.population,
                row.stage,
                row.moment,
            )
        ].append(row)
    return BacktestPooled(
        files=files,
        rows=len(rows),
        entries=[_pooled_entry(key, grouped[key]) for key in sorted(grouped)],
    )


# --------------------------------------------------------------------------
# The two replays a comparison is built on.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class CertComparisonReplay:
    """Both arms' cert replay outcomes over one set of petitions."""

    incumbent: ReplayOutcome
    candidate: ReplayOutcome


def replay_cert_comparison(
    items: list[BacktestItem],
    *,
    corpus_db_path: Path,
    config_root: Path,
    work_root: Path,
    run_id: str,
    incumbent: ReplayArm,
    candidate: ReplayArm,
    engine_override: str | None = None,
) -> CertComparisonReplay:
    """Replay one predictor over ``items`` under each arm, the candidate first.

    Two ordinary cert replay campaigns (:func:`.cert_backtest.replay_predictors`)
    over the same items, each under its own sub-root of ``work_root`` so neither
    arm's cells sit beside the other's forecasts. The provisioner is
    deterministic over one corpus, so both arms read byte-identical case trees
    and carry the same replay clock, and that is checked rather than assumed:
    differing clocks raise, because a difference between the arms would then
    not be the configuration's alone.

    The arms run one after the other, never at once: one engine's cells must
    not overlap (the codex runner's per-process sign-in is the binding case),
    and both arms run on one engine. The candidate runs first because it is
    the arm that can be misconfigured: where it scores no cell at all, the
    incumbent is not run, since its cells would be paid for with nothing to
    pair them against, and the report shows every incumbent cell unscored.
    """

    def run(role: str, arm: ReplayArm) -> ReplayOutcome:
        return replay_predictors(
            items,
            corpus_db_path=corpus_db_path,
            config_root=config_root,
            work_root=work_root / role,
            run_id=run_id,
            engine_override=engine_override,
            arm=arm,
        )

    ran = run("candidate", candidate)
    if items and not ran.backtesters:
        # Nothing to pair against: a candidate that scored no cell (a model id
        # its engine refuses fails every cell at once) makes the incumbent's
        # campaign spend with nothing to compare it to.
        return CertComparisonReplay(incumbent=replace(ran, backtesters=[]), candidate=ran)
    held = run("incumbent", incumbent)
    if held.clocks != ran.clocks:
        raise RuntimeError("the two arms were provisioned under different replay clocks")
    return CertComparisonReplay(incumbent=held, candidate=ran)


def _cert_forecasts(outcome: ReplayOutcome, predictor_id: str) -> dict[str, ArmForecast]:
    for backtester in outcome.backtesters:
        if isinstance(backtester, ReplayedBacktester) and backtester.id == predictor_id:
            return {
                case_id: ArmForecast(
                    probability=prediction.probability_granted,
                    positive_call=bool(granted_flag(prediction.predicted_disposition)),
                )
                for case_id, prediction in backtester.predictions.items()
            }
    return {}  # every cell of this arm was lost


def cert_ran_on(outcome: ReplayOutcome, predictor_id: str) -> tuple[str | None, str | None]:
    """The backend and model behind an arm's scored cells; nulls where none scored."""
    for backtester in outcome.backtesters:
        if isinstance(backtester, ReplayedBacktester) and backtester.id == predictor_id:
            return backtester.engine, backtester.model
    return None, None


#: The moment a cert replay forecasts at: the stage's registered baseline.
CERT_REPLAY_MOMENT: Final = str(moments.moments_for(Stage.cert)[0].moment)


def cert_paired_cells(
    items: Sequence[BacktestItem],
    replay: CertComparisonReplay,
    predictor_id: str,
    *,
    decided: Mapping[str, date | None],
    stratified: bool,
) -> list[PairedCell]:
    """Each replayed petition with what the two arms returned for it.

    ``stratified`` says whether the set was drawn by outcome class; only then
    does a pair carry its stratum, since an unstratified set has no strata to
    reweight.
    """
    incumbent = _cert_forecasts(replay.incumbent, predictor_id)
    candidate = _cert_forecasts(replay.candidate, predictor_id)
    arm_of = {clock.case_id: clock.snapshot_provenance for clock in replay.incumbent.clocks}
    return [
        PairedCell(
            case_id=item.features.case_id,
            moment=CERT_REPLAY_MOMENT,
            outcome=granted_flag(item.actual_disposition),
            decided=decided.get(item.features.case_id),
            stratum=cert_stratum(item.actual_disposition) if stratified else None,
            provisioning=arm_of.get(item.features.case_id),
            incumbent=incumbent.get(item.features.case_id),
            candidate=candidate.get(item.features.case_id),
        )
        for item in items
    ]


def cert_scored_cells(
    items: Sequence[BacktestItem],
    forecasts: Mapping[str, float],
    *,
    decided: Mapping[str, date | None],
    provisioning: Mapping[str, str],
    shares: Mapping[str, float] | None,
) -> list[ScoredCell]:
    """The record's view of one predictor's scored cert cells.

    ``shares`` maps each outcome class to its share of the eligible population,
    or is ``None`` under a draw that is not a probability sample.
    """
    cells = []
    for item in items:
        case_id = item.features.case_id
        if case_id not in forecasts:
            continue
        stratum = cert_stratum(item.actual_disposition)
        cells.append(
            ScoredCell(
                case_id=case_id,
                stage=Stage.cert.value,
                moment=CERT_REPLAY_MOMENT,
                probability=forecasts[case_id],
                outcome=granted_flag(item.actual_disposition),
                decided=decided.get(case_id),
                provisioning=provisioning.get(case_id),
                stratum=stratum,
                stratum_share=shares.get(stratum) if shares is not None else None,
            )
        )
    return cells


#: The rule a merits replay draws its cases by (:func:`.merits_backtest.draw_cases`),
#: and the name its population is recorded under.
MERITS_DRAW_RULE: Final = "vintage-keyed-hash-v1"
MERITS_POPULATION: Final = "merits:argued"


def merits_population_name(terms: Sequence[int]) -> str:
    """The name a merits replay's population is recorded under: its argued Terms.

    The outcome-class shares are computed over the Terms a run names, so two
    runs over different Terms drew from two populations and never pool.
    """
    return MERITS_POPULATION + ":" + "+".join(f"OT{term}" for term in sorted(set(terms)))


def cert_population_name(scope: str, salience_floor: float) -> str:
    """The name a cert replay's population is recorded under.

    The scope, and under ``selected`` the salience floor that defines it: a
    moved floor selects a different population, which never pools with the old.
    """
    return f"cert:{scope}@{salience_floor:g}" if scope == "selected" else f"cert:{scope}"


#: The two merits outcome classes.
MERITS_STRATA: Final = ("disturbed", "not-disturbed")


def merits_stratum(disturbed: bool) -> str:
    return MERITS_STRATA[0] if disturbed else MERITS_STRATA[1]


def merits_shares(cases: Sequence[MeritsReplayCase]) -> dict[str, float]:
    """Each merits outcome class's share of ``cases``, the population drawn from."""
    if not cases:
        return {}
    disturbed = sum(case.disturbed for case in cases) / len(cases)
    return {MERITS_STRATA[0]: disturbed, MERITS_STRATA[1]: 1.0 - disturbed}


@dataclass(frozen=True)
class MeritsComparisonReplay:
    """Both arms' merits replay outcomes over one set of cases."""

    incumbent: MeritsReplayOutcome
    candidate: MeritsReplayOutcome


def replay_merits_comparison(
    conn: corpus.ReadConnection,
    cases: Sequence[MeritsReplayCase],
    *,
    config_root: Path,
    work_root: Path,
    run_id: str,
    incumbent: ReplayArm,
    candidate: ReplayArm,
    engine_override: str | None = None,
) -> MeritsComparisonReplay:
    """Replay one predictor over ``cases`` under each arm, the candidate first.

    Two ordinary merits campaigns
    (:func:`.merits_backtest.replay_merits_predictors`), each under its own
    sub-root. Both provision the same cells from the same corpus; an arm whose
    written cells differ from the other's raises, and a candidate that scores
    nothing ends the comparison before the incumbent runs, both for the
    reasons :func:`replay_cert_comparison` gives.
    """

    def run(role: str, arm: ReplayArm) -> MeritsReplayOutcome:
        return replay_merits_predictors(
            conn,
            cases,
            config_root=config_root,
            work_root=work_root / role,
            run_id=run_id,
            engine_override=engine_override,
            arm=arm,
        )

    ran = run("candidate", candidate)
    if ran.sweep.cells and not any(
        by_moment for found in ran.predictions.values() for by_moment in found.values()
    ):
        # The incumbent never ran: it has no engine, no model and no losses of its own.
        return MeritsComparisonReplay(
            incumbent=replace(ran, predictions={}, ran_on={}, lost_cells=[], disclosures=[]),
            candidate=ran,
        )
    held = run("incumbent", incumbent)
    if held.sweep.cells != ran.sweep.cells:
        raise RuntimeError("the two arms were provisioned with different replay cells")
    return MeritsComparisonReplay(incumbent=held, candidate=ran)


def _merits_forecast(
    outcome: MeritsReplayOutcome, predictor_id: str, moment: Moment, case_id: str
) -> ArmForecast | None:
    found = outcome.predictions.get(predictor_id, {}).get(moment, {}).get(case_id)
    if found is None:
        return None
    return ArmForecast(
        probability=found.probability_granted, positive_call=found.probability_granted >= 0.5
    )


def merits_paired_cells(
    cases: Sequence[MeritsReplayCase], replay: MeritsComparisonReplay, predictor_id: str
) -> list[PairedCell]:
    """Each written merits cell with what the two arms returned for it.

    The probability is P(disturbed) and the call is its side of one half, as
    the merits back-test scores it. The draw is unstratified, so no pair
    carries a stratum.
    """
    by_case = {case.case_id: case for case in cases}
    return [
        PairedCell(
            case_id=cell.case_id,
            moment=Moment(cell.moment).value,
            outcome=int(by_case[cell.case_id].disturbed),
            decided=by_case[cell.case_id].decided,
            stratum=None,
            provisioning=cell.provenance,
            incumbent=_merits_forecast(
                replay.incumbent, predictor_id, Moment(cell.moment), cell.case_id
            ),
            candidate=_merits_forecast(
                replay.candidate, predictor_id, Moment(cell.moment), cell.case_id
            ),
        )
        for cell in replay.incumbent.sweep.cells
    ]


def merits_scored_cells(
    cases: Sequence[MeritsReplayCase],
    outcome: MeritsReplayOutcome,
    predictor_id: str,
    shares: Mapping[str, float],
) -> list[ScoredCell]:
    """The record's view of one predictor's scored merits cells."""
    by_case = {case.case_id: case for case in cases}
    cells = []
    for cell in outcome.sweep.cells:
        forecast = _merits_forecast(outcome, predictor_id, Moment(cell.moment), cell.case_id)
        if forecast is None:
            continue
        case = by_case[cell.case_id]
        stratum = merits_stratum(case.disturbed)
        cells.append(
            ScoredCell(
                case_id=cell.case_id,
                stage=Stage.merits.value,
                moment=Moment(cell.moment).value,
                probability=forecast.probability,
                outcome=int(case.disturbed),
                decided=case.decided,
                provisioning=cell.provenance,
                stratum=stratum,
                stratum_share=shares.get(stratum),
            )
        )
    return cells
