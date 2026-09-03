"""Operational analytics roll-up: pipeline health, spend, data health.

A *read-only* snapshot of authoritative sources — the GitHub Actions run history,
the recorded usage ledger, and the committed ``flags.json`` files agents leave
under ``data/`` — so no pipeline run has to write an ops record (which would
reintroduce the concurrent-writer problem the corpus already manages).
``fedcourts ops-report`` renders this to Markdown (the run-ops dashboard issue) and
optionally to JSON.

Unlike the deterministic leaderboard / back-test roll-ups, this is a point-in-time
view: it carries ``generated_at`` and run durations, so it is not byte-stable.

Two further surfaces live here beside the dashboard, both bounded issue bodies a
maintainer reads and then closes, and both prose from tested code posted by a
workflow that contributes no wording of its own. The **weekly performance
digest** (``ops-report --digest-out``) answers what the week produced and what
the committed boards say, each figure carrying the vintage of the artifact it
came from. The **daily prediction-reading digest** (``fedcourts daily-digest``)
answers what the models *said* about one event, so its input is the committed
ledger's cells (loaded by :mod:`fedcourtsai.store`) rather than the ops feeds.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Literal

from .agent_feedback import already_posted, marker_head
from .analytics import _GRANT_LABELS
from .collect import flags_table
from .integrity import FORWARD, RETROSPECTIVE
from .schemas import (
    AgentFlags,
    AgentToolingFeedback,
    Backtest,
    BacktestEntry,
    CertBacktest,
    ClaimScoreBoard,
    CostEstimate,
    DataHealth,
    Evaluation,
    FlagsDigest,
    FlagSeverity,
    ForwardClaimRecord,
    FrozenProcessRecord,
    Leaderboard,
    LeakageDigest,
    LeakageExclusionRecord,
    LiveFrontier,
    ModelUsage,
    OpenTriggerIssue,
    OpsReport,
    PredictableEvent,
    Prediction,
    PredictorScoreRow,
    SalienceReplay,
    SpendSummary,
    Stage,
    StatPack,
    Stratum,
    SubstanceCalibration,
    SubstanceCells,
    SubstanceDigest,
    ToolingCount,
    ToolingDigest,
    WorkflowHealth,
)
from .spend import SpendVerdict
from .store import (
    PredictedEvent,
    PredictedEventRef,
    PredictionCell,
    RecentCells,
    normalized_stage,
)

# Conclusions that count as a completed-but-not-successful run.
_FAILURE_CONCLUSIONS = frozenset({"failure", "timed_out", "cancelled", "startup_failure"})

# Workflows whose non-zero exit is a REPORT, not an incident. `promote` is
# level-triggered: each dispatch either names an unsatisfied gate and exits 1
# with the fix in its step summary, or hands back the promotion command. A
# promotion sequence therefore accumulates failures on the way to succeeding, so
# a low success rate here is the design working. The health table still shows the
# row — a genuinely broken gate must stay visible — and footnotes it, rather than
# hiding it or letting a reader take it for breakage.
_GATE_WORKFLOWS = frozenset({"promote"})

# Cost constants, kept in sync with docs/budget.md (the single source for rates).
# GitHub Actions standard runners are free on a public repository, so the
# per-minute rate is zero; minutes are still tracked as a runtime-health
# signal. Set a real rate here if the repo ever goes private or moves to
# larger runners.
_ACTIONS_USD_PER_MINUTE = 0.0
# Infra not metered per run: CourtListener Tier 4 (~$100) + S3 (~$15), USD/month.
# The pilot pays Tier 4 annually ($1,000/yr ~= $83/mo); the monthly list price
# is used here as deliberate round-up headroom (~$17/mo, ~$204/yr — about 4% of
# the annual non-inference floor), so the dashboard reads high rather than low.
# The S3 line is dominated by internet egress, not storage — GitHub runners are
# Azure-hosted, so the scan-shaped writers' recurring full index pulls (~250-300
# GB/mo at today's ~1 GB blob) carry it just past the free tier. It scales with
# the blob, so revisit this alongside `docs/budget.md` when the index grows.
_FIXED_MONTHLY_USD = 115.0
_DAYS_PER_MONTH = 30.0


def _percentile(values: Sequence[int], q: float) -> int | None:
    """Nearest-rank percentile of ``values`` (``q`` in [0, 1]), or None if empty."""
    if not values:
        return None
    ordered = sorted(values)
    rank = round(q * (len(ordered) - 1))
    return ordered[rank]


def _run_seconds(run: Mapping[str, object]) -> int | None:
    """Wall-clock seconds for a completed Actions run, or None if not derivable."""
    start = run.get("startedAt") or run.get("createdAt")
    end = run.get("updatedAt")
    if not isinstance(start, str) or not isinstance(end, str):
        return None
    try:
        began = datetime.fromisoformat(start.replace("Z", "+00:00"))
        ended = datetime.fromisoformat(end.replace("Z", "+00:00"))
    except ValueError:
        return None
    seconds = (ended - began).total_seconds()
    return int(seconds) if seconds >= 0 else None


def summarize_health(runs: Iterable[Mapping[str, object]]) -> list[WorkflowHealth]:
    """Per-workflow health from a list of Actions runs (``gh run list --json`` shape).

    Each run is expected to carry ``workflowName``, ``status``, ``conclusion``, and
    timestamps. Workflows are returned sorted by name; within each, the success
    rate and the duration percentiles are over *conclusive* completed runs only
    (success + the failure family — skips and other non-conclusive conclusions
    excluded), so the rate matches the rendered success fraction and the ~1s
    skip overhead never drags the percentiles.
    """
    by_workflow: dict[str, list[Mapping[str, object]]] = {}
    for run in runs:
        name = run.get("workflowName") or run.get("name") or "?"
        by_workflow.setdefault(str(name), []).append(run)

    health: list[WorkflowHealth] = []
    for workflow, workflow_runs in sorted(by_workflow.items()):
        completed = [r for r in workflow_runs if r.get("status") == "completed"]
        # A skipped run is not an execution: a workflow whose every job's `if`
        # declines completes in ~1s having done nothing, so counting skips would
        # dilute the rate and drag the duration percentiles toward that
        # overhead. Health reads over the *conclusive* runs only — which
        # also keeps the rare neutral/action_required conclusions out of the
        # rate and percentiles (they still surface as executions in "Last").
        conclusive = [
            r
            for r in completed
            if r.get("conclusion") == "success" or r.get("conclusion") in _FAILURE_CONCLUSIONS
        ]
        successes = sum(1 for r in conclusive if r.get("conclusion") == "success")
        failures = len(conclusive) - successes
        durations = [s for r in conclusive if (s := _run_seconds(r)) is not None]
        # "Most recent" by start time; createdAt is ISO-8601 so string order is
        # time order. Completed skips are ignored here too — "Last" should
        # answer "how did the last real execution end" (an in-progress run
        # still surfaces, as conclusion None).
        executions = [
            r
            for r in workflow_runs
            if not (r.get("status") == "completed" and r.get("conclusion") == "skipped")
        ]
        recent = max(executions or workflow_runs, key=lambda r: str(r.get("createdAt") or ""))
        health.append(
            WorkflowHealth(
                workflow=workflow,
                runs_considered=len(workflow_runs),
                successes=successes,
                failures=failures,
                success_rate=(successes / len(conclusive)) if conclusive else None,
                last_conclusion=(
                    str(recent.get("conclusion")) if recent.get("conclusion") else None
                ),
                last_run_at=(str(recent.get("createdAt")) if recent.get("createdAt") else None),
                median_seconds=_percentile(durations, 0.5),
                p95_seconds=_percentile(durations, 0.95),
            )
        )
    return health


def _quantile(values: Sequence[float], q: float) -> float | None:
    """Nearest-rank quantile of ``values`` (``q`` in [0, 1]), or None if empty."""
    if not values:
        return None
    ordered = sorted(values)
    rank = round(q * (len(ordered) - 1))
    return round(ordered[rank], 4)


def _deny_base_rate(statpack: StatPack | None) -> tuple[float | None, int | None]:
    """``(denied share, resolved cases)`` from the statpack's modern-cert section.

    The calibration anchor: the disposition breakdown restricted to modern
    Term-prefixed discretionary-cert dockets — matched by its **shape**
    (``cert_stage`` + disposition grouping), never its title, and computed
    upstream over the live/historical slice with denial-reweighted counts, so
    both numbers are estimates of the true population rather than raw ingested
    rows. ``(None, None)`` when the statpack or its cert-stage disposition
    section is absent — the render shows an explicit absence rather than
    anchoring against the wrong population.
    """
    if statpack is None:
        return (None, None)
    for section in statpack.sections:
        if not section.cert_stage or section.group_by != "disposition":
            continue
        resolved = sum(b.resolved for b in section.buckets)
        if not resolved:
            return (None, None)
        denied = sum(b.resolved for b in section.buckets if b.key == "denied")
        return (round(denied / resolved, 4), resolved)
    return (None, None)


def _segment_base_rate(statpack: StatPack | None) -> tuple[float | None, int | None]:
    """``(grant share, resolved cases)`` over the paid salience-scored segment.

    The base rate for the population the salience gate actually predicts on —
    read from the statpack's pack-wide salience-band section (matched by its
    ``salience_band`` grouping, denial-reweighted), grant family pooled across
    every band. This is the anchor a selected-segment prediction should beat, not
    the whole-docket rate: with a salience gate the predicted slice grants far
    more often than the ~few-percent full docket. ``(None, None)`` when the
    statpack or its salience-band section is absent or nothing resolved.

    Deliberately **version-blind**, unlike every other band-keyed read. Pooling
    across every band recovers the whole scored population, and every row falls
    in exactly one band under any scorer, so the figure is the same number
    whichever version banded it. That holds only because the pooling is total: a
    per-band figure taken from this section would need the version.
    """
    if statpack is None:
        return (None, None)
    for section in statpack.sections:
        if section.group_by != "salience_band":
            continue
        resolved = sum(b.resolved for b in section.buckets)
        if not resolved:
            return (None, None)
        grants = sum(
            d.count
            for b in section.buckets
            for d in b.dispositions
            if d.disposition in _GRANT_LABELS
        )
        return (round(grants / resolved, 4), resolved)
    return (None, None)


def _delta(current: int, previous: int | None) -> int | None:
    return None if previous is None else current - previous


def summarize_substance(
    *,
    cell_counts: tuple[int, int, int],
    stratified_evaluations: Sequence[tuple[Evaluation, Stratum]],
    statpack: StatPack | None = None,
    live_frontier: LiveFrontier | None = None,
    previous: OpsReport | None = None,
    process_scope: Literal["frozen", "all"] = "frozen",
    forward_claim: ForwardClaimRecord | None = None,
    leakage_exclusion: LeakageExclusionRecord | None = None,
) -> SubstanceDigest:
    """Roll the committed ledger + metrics artifacts into the substance section.

    Pure over its inputs (no filesystem): the caller supplies the ledger census
    (:func:`fedcourtsai.store.ledger_cell_counts`), the stratified evaluations,
    the committed statpack, the published live-frontier snapshot, and the two
    exclusion records its stratify pass produced — the forward-claim rule and
    the leakage bit, carried verbatim so the
    dashboard and the boards cannot disagree about what was excluded. Deltas
    compare against ``previous``'s substance counts and stay null without a
    comparable prior — a missing or pre-substance snapshot degrades the deltas,
    never the section.
    """
    predictions, events_predicted, predicted_resolved = cell_counts
    # Strictly the timing strata: a procedural (mootness-basis) cell counts in
    # neither — the leaderboard segments it out of the skill aggregates, and
    # this funnel mirrors that doctrine.
    forward = [ev for ev, stratum in stratified_evaluations if stratum == FORWARD]
    replay = [ev for ev, stratum in stratified_evaluations if stratum == RETROSPECTIVE]

    prior_cells = previous.substance.cells if previous is not None and previous.substance else None
    cells = SubstanceCells(
        predictions=predictions,
        events_predicted=events_predicted,
        predicted_resolved=predicted_resolved,
        evaluations_forward=len(forward),
        evaluations_retrospective=len(replay),
        predictions_delta=_delta(predictions, prior_cells.predictions if prior_cells else None),
        predicted_resolved_delta=_delta(
            predicted_resolved, prior_cells.predicted_resolved if prior_cells else None
        ),
        evaluations_forward_delta=_delta(
            len(forward), prior_cells.evaluations_forward if prior_cells else None
        ),
        evaluations_retrospective_delta=_delta(
            len(replay), prior_cells.evaluations_retrospective if prior_cells else None
        ),
    )

    deny_rate, base_cases = _deny_base_rate(statpack)
    segment_rate, segment_cases = _segment_base_rate(statpack)
    # A cell whose `correct` the stamp could not compute leaves both halves of
    # the fraction, exactly as the leaderboard's accuracy column treats it — a
    # missing artifact is not a wrong call.
    replay_correct = [ev.correct for ev in replay if ev.correct is not None]
    accuracy = round(sum(replay_correct) / len(replay_correct), 4) if replay_correct else None
    briers = [ev.brier_score for ev in replay if ev.brier_score is not None]
    skills = [ev.brier_skill_score for ev in replay if ev.brier_skill_score is not None]
    calibration = SubstanceCalibration(
        sample=len(replay),
        mean_brier=round(sum(briers) / len(briers), 4) if briers else None,
        accuracy=accuracy,
        accuracy_scored=len(replay_correct),
        deny_base_rate=deny_rate,
        base_rate_cases=base_cases,
        lift_over_always_deny=(
            round(accuracy - deny_rate, 4)
            if accuracy is not None and deny_rate is not None
            else None
        ),
        segment_grant_rate=segment_rate,
        segment_base_rate_cases=segment_cases,
        mean_brier_skill=round(sum(skills) / len(skills), 4) if skills else None,
    )

    by_predictor: dict[str, list[Evaluation]] = {}
    for ev, _stratum in stratified_evaluations:
        by_predictor.setdefault(ev.predictor_id, []).append(ev)
    scores = []
    for predictor_id in sorted(by_predictor):
        evals = by_predictor[predictor_id]
        quality = [ev.reasoning_quality for ev in evals if ev.reasoning_quality is not None]
        # Same rule as the calibration block above: a null `correct` is a
        # missing figure, not a zero, so it leaves the row's fraction entirely
        # and a predictor with no computable cell reports no accuracy at all.
        row_correct = [ev.correct for ev in evals if ev.correct is not None]
        scores.append(
            PredictorScoreRow(
                predictor_id=predictor_id,
                evaluations=len(evals),
                accuracy=(round(sum(row_correct) / len(row_correct), 4) if row_correct else None),
                accuracy_scored=len(row_correct),
                median=_quantile(quality, 0.5),
                p25=_quantile(quality, 0.25),
                p75=_quantile(quality, 0.75),
            )
        )

    return SubstanceDigest(
        cells=cells,
        calibration=calibration,
        predictor_scores=scores,
        forward_claim=forward_claim,
        leakage_exclusion=leakage_exclusion,
        live_frontier=live_frontier,
        process_scope=process_scope,
    )


def _fmt_delta(delta: int | None) -> str:
    """A signed week-over-week suffix, empty without a comparable prior."""
    return "" if delta is None else f" ({delta:+d})"


def render_substance(digest: SubstanceDigest) -> str:
    """Render the substantive-results section: is the machine producing?

    The headline cells line always renders (with each small number's sample size
    beside it); each sub-block — calibration, evaluation scores, live frontier —
    renders only when it has data, so an idle instrument reads as a short section
    rather than a stack of "not producing yet" placeholders.
    """
    c = digest.cells
    # The scored figures below cover `process_scope`; the prediction census does
    # not (it counts every committed prediction). Name the scope so a frozen
    # headline with predictions but zero frozen evaluations reads as the honest
    # shakedown state rather than a broken funnel.
    scored_scope = "" if digest.process_scope == "all" else " _(frozen process only)_"
    frozen_empty = (
        digest.process_scope == "frozen"
        and c.evaluations_forward == 0
        and c.evaluations_retrospective == 0
        # An exclusion-emptied headline is not the shakedown state: the cells
        # exist and were dropped, and the exclusion lines below say so. Both
        # rules count here — a headline emptied by leakage alone would
        # otherwise render as "nothing ran yet".
        and (digest.forward_claim is None or digest.forward_claim.excluded == 0)
        and (digest.leakage_exclusion is None or digest.leakage_exclusion.excluded == 0)
    )
    lines = [
        "## Substance (is it producing?)",
        "",
        f"Prediction cells committed: **{c.predictions}**{_fmt_delta(c.predictions_delta)} "
        f"over **{c.events_predicted}** event(s); predicted events resolved: "
        f"**{c.predicted_resolved}**{_fmt_delta(c.predicted_resolved_delta)}; scored cells"
        f"{scored_scope}: "
        f"**{c.evaluations_forward}** forward{_fmt_delta(c.evaluations_forward_delta)} · "
        f"**{c.evaluations_retrospective}** replay"
        f"{_fmt_delta(c.evaluations_retrospective_delta)}.",
    ]
    if digest.forward_claim is not None and digest.forward_claim.excluded:
        placement = (
            "excluded from the forward/replay counts above"
            if digest.forward_claim.policy == "exclude"
            else "counted inside the replay figure above"
        )
        lines.append(
            f"Forward-claim integrity: **{digest.forward_claim.excluded}** cell(s) "
            f"whose record contradicts its forward claim, {placement} per the "
            f"`{digest.forward_claim.policy}` policy (see the boards' "
            f"`forward_claim` block)."
        )
    if digest.leakage_exclusion is not None and digest.leakage_exclusion.excluded:
        # Its own line, never folded into the forward-claim count above: the two
        # rules are independent and a cell both caught is in both counts, so a
        # sum would be neither figure.
        leaked = digest.leakage_exclusion
        lines.append(
            f"Leakage exclusion: **{leaked.excluded}** of {leaked.assessed} "
            f"assessed cell(s) carry `leakage_suspected`, excluded from the "
            f"forward/replay counts above and from every scored figure on the "
            f"boards (see their `leakage_exclusion` block). Counted separately "
            f"from the forward-claim line — a cell caught by both appears in "
            f"both."
        )
    if frozen_empty:
        lines.append(
            "_No frozen-process evaluations yet — the headline is scoped to the "
            "frozen process; run with the all-versions view for the shakedown pool._"
        )

    cal = digest.calibration
    cal_lines: list[str] = []
    if cal.sample > 0:
        brier = "—" if cal.mean_brier is None else f"{cal.mean_brier:.3f}"
        accuracy = "—" if cal.accuracy is None else f"{cal.accuracy:.0%}"
        # Accuracy prints its own denominator, not the cell count: a cell whose
        # `correct` the stamp could not compute is out of the fraction, so
        # `sample` would overstate what the percentage was taken over.
        scored = (
            f"n={cal.accuracy_scored}"
            if cal.accuracy_scored == cal.sample
            else f"n={cal.accuracy_scored} of {cal.sample}"
        )
        cal_lines.append(f"Mean Brier **{brier}** · accuracy **{accuracy}** ({scored})")
    if cal.deny_base_rate is not None:
        lift = "—" if cal.lift_over_always_deny is None else f"{cal.lift_over_always_deny:+.1%}"
        cal_lines.append(
            f"Always-deny base rate **{cal.deny_base_rate:.0%}** "
            f"(est. over {cal.base_rate_cases:,} resolved modern-cert petitions, "
            "live/historical slice, denial-reweighted) · "
            f"lift **{lift}** — a difference of rates over different "
            "populations (the accuracy's scored cells vs the whole modern-cert "
            "slice), so an orientation rather than an effect size"
        )
    if cal.segment_grant_rate is not None:
        skill = "—" if cal.mean_brier_skill is None else f"{cal.mean_brier_skill:+.3f}"
        cal_lines.append(
            f"Salience-scored segment base grant rate **{cal.segment_grant_rate:.0%}** "
            f"(est. over {cal.segment_base_rate_cases:,} resolved paid-segment petitions, "
            "denial-reweighted) · replay Brier skill vs baseline "
            f"**{skill}**"
        )
    if cal_lines:
        lines += ["", "**Calibration (replay stratum, advisory)**", *cal_lines]

    if digest.predictor_scores:
        lines += [
            "",
            "**Evaluation scores by predictor** (reasoning quality, all strata pooled)",
            "| Predictor | Cells | Accuracy | Scored | Median | p25-p75 |",
            "|-----------|------:|---------:|-------:|-------:|---------|",
        ]
        for row in digest.predictor_scores:
            accuracy = "—" if row.accuracy is None else f"{row.accuracy:.0%}"
            median = "—" if row.median is None else f"{row.median:.2f}"
            spread = "—" if row.p25 is None or row.p75 is None else f"{row.p25:.2f}-{row.p75:.2f}"
            # `Scored` is accuracy's own denominator, beside the cell count
            # rather than replacing it: the gap is the cells the stamp could
            # not score, and a column that hid it would read as a full sample.
            lines.append(
                f"| {row.predictor_id} | {row.evaluations} | {accuracy} | "
                f"{row.accuracy_scored} | {median} | {spread} |"
            )

    frontier = digest.live_frontier
    if frontier is not None and not frontier.skipped:
        upcoming = (
            f"next conference **{frontier.next_conference}** "
            f"({frontier.next_conference_petitions} petition(s))"
            if frontier.next_conference is not None
            else "no upcoming conference scheduled"
        )
        lines += [
            "",
            "**Live frontier**",
            f"Watchlist **{frontier.watchlist}** petition(s) · {upcoming} · "
            f"documents provisioned on **{frontier.documents_provisioned}/{frontier.watchlist}**",
        ]
    return "\n".join(lines) + "\n"


def _health_questions(report: OpsReport) -> list[str]:
    """The digest's fixed interrogative bullets, with this week's answers.

    Deliberately short and interrogative — the numbers demand a reaction rather
    than sit available for inspection; the daily dashboard stays the reference
    view. Renders from whatever the report holds, with explicit absences.
    """
    substance = report.substance
    lines: list[str] = []

    # A frozen scope with no scored cells is the shakedown state (nothing blessed
    # yet), not a stalled machine — so the "what is blocking?" framing below would
    # misread. Detect it once and reframe those questions honestly.
    frozen_shakedown = (
        substance is not None
        and substance.process_scope == "frozen"
        and substance.cells.evaluations_forward == 0
        and substance.cells.evaluations_retrospective == 0
    )

    if substance is not None and substance.calibration.sample:
        cal = substance.calibration
        lift = (
            "lift unavailable (no base rate)"
            if cal.lift_over_always_deny is None
            else f"lift **{cal.lift_over_always_deny:+.1%}** over always-deny"
        )
        skill = (
            ""
            if cal.mean_brier_skill is None
            else f", Brier skill **{cal.mean_brier_skill:+.3f}** vs the segment base rate"
        )
        lines.append(
            f"- **Replay calibration on {cal.sample} scored cell(s): {lift}{skill} — "
            "do you believe it?**"
        )
    elif frozen_shakedown:
        lines.append(
            "- **No frozen-process cells yet — the headline is scoped to the frozen "
            "process; run `--all-versions` for the shakedown pool.**"
        )
    else:
        lines.append("- **No scored replay cells yet — what is blocking the first batch?**")

    if substance is not None:
        c = substance.cells
        weekly = (
            f"{c.evaluations_forward_delta:+d} this week, {c.evaluations_forward} total"
            if c.evaluations_forward_delta is not None
            else f"{c.evaluations_forward} total, no prior snapshot to diff"
        )
        question = (
            "still shakedown, none frozen yet"
            if frozen_shakedown
            else "is the live frontier producing?"
        )
        lines.append(
            f"- **Forward cells scored ({substance.process_scope}): {weekly} — {question}**"
        )
        frontier = substance.live_frontier
        if frontier is not None and not frontier.skipped:
            upcoming = (
                f"{frontier.next_conference_petitions} petition(s) distributed for "
                f"**{frontier.next_conference}**"
                if frontier.next_conference is not None
                else "no upcoming conference on the calendar"
            )
            lines.append(
                f"- **Watchlist vs next conference: {upcoming}; documents on "
                f"{frontier.documents_provisioned}/{frontier.watchlist} — ready?**"
            )
        else:
            lines.append("- **Watchlist vs next conference: no published snapshot — why not?**")

    if report.open_triggers:
        oldest = report.open_triggers[0]
        lines.append(
            f"- **Oldest stale fan-out label: `{oldest.label}` "
            f"({_age(oldest.created_at, report.generated_at)} old) — clear it?**"
        )
    else:
        lines.append("- **Stale fan-out labels: none.**")

    monthly = (
        "—"
        if report.cost.estimated_monthly_usd is None
        else f"${report.cost.estimated_monthly_usd:,.0f}/mo"
    )
    # Name the model rate here, not just the all-in total: the cumulative figure
    # next to a total that used to exclude it was the misreading this line invited.
    model_rate = (
        "unrated"
        if report.cost.model_monthly_usd is None
        else f"~${report.cost.model_monthly_usd:,.0f}/mo"
    )
    lines.append(
        f"- **Spend vs budget: ${report.spend.estimated_cost_usd:,.2f} model spend cumulative "
        f"({model_rate} while running), ~{monthly} projected all-in — within plan?**"
    )
    return lines


@dataclass(frozen=True)
class Vintaged[T]:
    """A committed metrics artifact and the vintage the figures in it carry.

    None of the boards stamps itself: they are byte-stable functions of their
    inputs, deliberately, so the vintage cannot come from inside the file. It is
    supplied by the caller — the commit that last wrote the artifact — and it
    rides beside the value rather than being folded into a rendered string, so a
    renderer cannot show a figure while forgetting when it was computed.
    ``value`` is None when the artifact has not landed at all, which is a
    different statement from a landed-but-empty one and must read differently.
    """

    value: T | None
    vintage: str | None


@dataclass(frozen=True)
class WeeklyAnalytics:
    """The committed metrics artifacts the weekly digest reports, each vintaged.

    ``salience_version_in_force`` is the scorer the pipeline runs **today**, not
    the one the replay was produced under: a per-band figure means something only
    under the function that assigned the band, so a replay from an older version
    is history rather than a current reading, and the digest has to say which it
    is looking at.
    """

    leaderboard: Vintaged[Leaderboard]
    claim_scores: Vintaged[ClaimScoreBoard]
    statpack: Vintaged[StatPack]
    backtest: Vintaged[Backtest]
    salience_replay: Vintaged[SalienceReplay]
    cert_backtest: Vintaged[CertBacktest]
    salience_version_in_force: str


@dataclass(frozen=True)
class WeeklyProduction:
    """What the ledger recorded this week: cells produced, and what they cost.

    ``census`` and ``spend_usd`` are taken over the *same* window and the same
    usage records, so the two numbers describe one set of cells. ``backstop`` is
    the ex-post spend gate's own verdict over its own (longer) window, carried
    whole rather than reduced to a fraction — an unenforced ceiling has no
    fraction, and a digest that printed one anyway would invent a budget.
    """

    census: RecentCells
    spend_usd: float
    backstop: SpendVerdict | None
    window_start: date | None = None
    window_end: date | None = None

    @property
    def window(self) -> str:
        """The window as dates, so two adjacent digests are comparable.

        "last 7d" alone is not recoverable by a reader: the Monday tick titles its
        issue for the ISO week that *starts* that morning while the census covers
        the seven days before it, so without the bounds the section silently
        describes the previous week under this week's heading.
        """
        if self.window_start is None or self.window_end is None:
            return f"last {self.census.window_days}d"
        return (
            f"{self.window_start.isoformat()} to {self.window_end.isoformat()}, "
            f"the {self.census.window_days}d before this digest"
        )


def _cell(value: str) -> str:
    """One table cell's text, with any pipe escaped.

    Predictor ids come off the ledger as free-form strings, and a `|` in one
    would silently shift every column to its right rather than failing.
    """
    return value.replace("|", r"\|")


def _sourced(filename: str, vintaged: Vintaged[object]) -> str:
    """``` `metrics/x.json`, vintage YYYY-MM-DD ``` — the artifact and when it moved.

    Every metrics-derived figure carries this, because none of these artifacts is
    refreshed on the digest's own schedule: a board is byte-stable and a statpack
    moves only when the corpus does, so a figure without its vintage silently
    claims to be this week's. An unknown vintage says so rather than being
    omitted — the reader still needs to know the number's age is unestablished.
    """
    vintage = f"vintage {vintaged.vintage}" if vintaged.vintage else "vintage unknown"
    return f"`metrics/{filename}`, {vintage}"


def _leaderboard_lines(vintaged: Vintaged[Leaderboard], generated_at: str) -> list[str]:
    """The standings, or the honest reason there are none."""
    board = vintaged.value
    where = _sourced("leaderboard.json", vintaged)
    if board is None:
        return ["- **Leaderboard**: `metrics/leaderboard.json` has never landed."]
    if not board.entries:
        return [
            f"- **Leaderboard** ({where}): **no predictor ranked** — "
            f"{_empty_headline_reason(board.frozen_process, generated_at)} "
            f"{board.evaluations_total} evaluation(s) in the `{board.process_scope}` "
            f"scope, {board.events_scored} event(s) scored; `--all-versions` is where "
            "the shakedown pool shows."
        ]
    versions = (
        f" · banded by {', '.join(f'`{v}`' for v in board.salience_versions)}"
        if board.salience_versions
        else ""
    )
    regrades = (
        f" · {board.superseded_gradings} superseded grading(s) collapsed away"
        if board.superseded_gradings
        else ""
    )
    rows = [
        f"- **Leaderboard** ({where}): {board.predictors_ranked} predictor(s) over "
        f"{board.events_scored} event(s), scope `{board.process_scope}`{versions}"
        f"{regrades}. Rank is forward accuracy, then forward Brier.",
        "",
        # `evaluators` is the panel depth — how many judges scored the predictor —
        # not a cell count. Labelling it "cells" would publish "2 cells over 37
        # events", which is not a thing the board says.
        "| Rank | Predictor | Judges | Events |",
        "| ---: | --- | ---: | ---: |",
    ]
    rows += [
        f"| {entry.rank} | {_cell(entry.predictor_id)} | {entry.evaluators} "
        f"| {entry.events_scored} |"
        for entry in board.entries
    ]
    return rows


def _empty_headline_reason(frozen: FrozenProcessRecord | None, generated_at: str) -> str:
    """Why an empty frozen board is empty — which is two different states.

    A freeze instant in the *future* means the counting window has not opened:
    the headline is empty by construction and no grading could have reached it
    however well the pipeline ran. Once the instant has passed, an empty board
    means the window is open and nothing has been graded into it — a fact about
    production. Collapsing the two into "nothing has been graded yet" reports the
    first as the second, which is the same bare-zero misreading the branch exists
    to avoid.
    """
    if frozen is None or frozen.since is None:
        return "the board records no freeze instant, so nothing is in scope to rank."
    since = frozen.since.date().isoformat()
    now = parse_iso(generated_at)
    if now is not None and _as_utc(now) < _as_utc(frozen.since):
        return f"the frozen counting window opens **{since}**, so it is empty by construction."
    return (
        f"the frozen counting window opened {since} and no stamped grading has "
        "reached the ranked population."
    )


def _claim_score_lines(vintaged: Vintaged[ClaimScoreBoard]) -> list[str]:
    """The claim-score board's state, empty or otherwise."""
    board = vintaged.value
    where = _sourced("claim-scores.json", vintaged)
    if board is None:
        return ["- **Claim scores**: `metrics/claim-scores.json` has never landed."]
    if not board.entries:
        return [
            f"- **Claim scores** ({where}): **suppressed** — "
            f"{board.cells_with_claims} cell(s) carry a claims block inside the "
            f"`{board.process_scope}` scope and this surface's population, so no "
            "coefficient is computed."
        ]
    return [
        f"- **Claim scores** ({where}): {len(board.entries)} predictor(s) over "
        f"{board.cells_with_claims} cell(s) carrying claims."
    ]


def _base_rate_lines(vintaged: Vintaged[StatPack]) -> list[str]:
    """The statpack's two headline rates, each with its own denominator and its limit.

    **Neither anchors a scored cell**, and the line says so. A forward cert cell
    is scored against its own salience band's strictly-prior-Term risk-set rate;
    the pack-wide band rate here pools every band over the whole walked range with
    no own-Term exclusion, which ``docs/salience.md`` registers as a fit
    diagnostic for the ranking constant and *not* a scoring baseline — quoting it
    as a forecast anchor would breach the leakage guard registered there. The
    always-deny figure is the whole modern-cert slice's, not the predicted
    segment's, so it is an orientation for reading an accuracy, not a floor any
    scored cell is measured against.
    """
    pack = vintaged.value
    where = _sourced("statpack.json", vintaged)
    if pack is None:
        return ["- **Base rates**: `metrics/statpack.json` has never landed."]
    deny, deny_cases = _deny_base_rate(pack)
    grant, grant_cases = _segment_base_rate(pack)
    deny_text = (
        f"always-deny **{deny:.0%}** (est. over {deny_cases:,} resolved modern-cert "
        "petitions, denial-reweighted)"
        if deny is not None and deny_cases is not None
        else "always-deny **—** (no cert-stage disposition section)"
    )
    grant_text = (
        f"pooled salience-band grant **{grant:.0%}** (over {grant_cases:,} resolved "
        "petitions of the scored segment, every band pooled)"
        if grant is not None and grant_cases is not None
        else "pooled band grant **—** (no salience-band section)"
    )
    return [
        f"- **Base rates** ({where}): {deny_text}; {grant_text}. Pack coverage: "
        f"{pack.coverage.live_slice_resolved:,} resolved of "
        f"{pack.coverage.live_slice_rows:,} live-slice rows.",
        "  _Neither figure anchors a scored cell. A forward cert cell is scored "
        + "against its own band's strictly-prior-Term risk-set rate; the pooled band "
        + "rate is a fit diagnostic for the ranking constant, not a scoring baseline "
        + "(`docs/salience.md`), and the always-deny rate is taken over a different, "
        + "much wider population than the one the gate predicts — an orientation "
        + "rather than an effect size._",
    ]


def _render_analytics_state(analytics: WeeklyAnalytics, generated_at: str) -> list[str]:
    """Section 1: what the committed boards say, and what they honestly cannot."""
    return [
        "",
        "## Analytics state",
        "",
        *_leaderboard_lines(analytics.leaderboard, generated_at),
        *_claim_score_lines(analytics.claim_scores),
        *_base_rate_lines(analytics.statpack),
    ]


def _render_production(production: WeeklyProduction) -> list[str]:
    """Section 2: cells produced this week, and the measured cost of producing them."""
    census = production.census
    lines = [
        "",
        f"## Produced this week ({production.window})",
        "",
        f"**{census.cells}** cell(s) over **{census.events}** event(s), and "
        f"**${production.spend_usd:,.2f}** of measured model spend over the same "
        "records — the recorded `usage.json` ledger, which lags: a cell's usage "
        "reaches `data/` only when its run's collect PR merges, so this is a floor "
        "on what was spent, not a real-time figure.",
    ]
    if census.rows:
        lines += [
            "",
            "| Role | Stage | Cells |",
            "| --- | --- | ---: |",
            *[f"| {_cell(row.role)} | {_cell(row.stage)} | {row.cells} |" for row in census.rows],
        ]
    else:
        lines += ["", "_No cell landed in the window._"]

    backstop = production.backstop
    if backstop is None:
        lines += ["", "_Spend backstop: not evaluated this run._"]
    elif not backstop.enforced:
        lines += [
            "",
            "_Spend backstop: **no ceiling configured**, so nothing is measured "
            + "against one and nothing would be deferred._",
        ]
    else:
        share = backstop.spent_usd / backstop.ceiling_usd if backstop.ceiling_usd else 0.0
        verdict = (
            "**BREACHED** — a plan seam would defer its matrix" if backstop.breached else "clear"
        )
        lines += [
            "",
            f"Spend backstop: **${backstop.spent_usd:,.2f}** of "
            f"**${backstop.ceiling_usd:,.2f}** over the trailing "
            f"{backstop.window_days}d window (**{share:.0%}** consumed, "
            f"${backstop.remaining_usd:,.2f} left, {backstop.cells} cell(s)) — {verdict} "
            "on a lagging ledger, so the verdict is a floor too.",
        ]
    return lines


#: The court whose rows the digest publishes beside the pooled figure. Pooling
#: mixes outcome vocabularies — `granted` is cert on a SCOTUS row and a motion
#: granted on a court-of-appeals docket — and the pooled floor is a mixture of a
#: high SCOTUS floor and near-zero appellate ones, so a pooled lift can be
#: produced entirely by a court this pipeline does not predict. This is the one
#: it does.
_BACKTEST_HEADLINE_COURT = "scotus"


def _pct(value: float | None) -> str:
    """A percentage, or an em dash where the figure was never computed."""
    return "—" if value is None else f"{value:.1%}"


def _signed_pct(value: float | None) -> str:
    return "—" if value is None else f"{value:+.2%}"


def _brier(value: float | None) -> str:
    return "—" if value is None else f"{value:.4f}"


def _backtest_rows(entry: BacktestEntry) -> list[str]:
    """One predictor's rows: its predicted court first, then the pooled figure.

    The pooled row is labelled as a mixture rather than left to read as the
    predictor's score, because it is the row a reader quotes.
    """
    rows = [
        f"| {_cell(entry.predictor_id)} | {_cell(court.court)} | {court.events_scored:,} "
        f"| {_pct(court.accuracy)} | {_pct(court.always_denied_accuracy)} "
        f"| {_signed_pct(court.lift_over_always_denied)} | {_brier(court.mean_brier_score)} |"
        for court in entry.courts
        if court.court == _BACKTEST_HEADLINE_COURT
    ]
    rows.append(
        f"| {_cell(entry.predictor_id)} | _all courts pooled_ | {entry.events_scored:,} "
        f"| {_pct(entry.accuracy)} | {_pct(entry.always_denied_accuracy)} "
        f"| {_signed_pct(entry.lift_over_always_denied)} | {_brier(entry.mean_brier_score)} |"
    )
    return rows


def _backtest_lines(vintaged: Vintaged[Backtest]) -> list[str]:
    """The broad replay board: accuracy is unreadable without its own court's floor.

    Published per court rather than as the ranked pooled row, because the pooled
    row is the one that misleads: a constant predictor scores its slice's base
    rate exactly, the pooled floor mixes an ~82% SCOTUS floor with ~1% appellate
    ones, and a pooled lift can therefore be bought entirely on a docket this
    pipeline never predicts. ``metrics/README.md`` says to read the per-court cut;
    pointing the reader at the artifact is not enough when the digest is the
    thing that gets quoted.
    """
    board = vintaged.value
    where = _sourced("backtest.json", vintaged)
    if board is None:
        return ["- **Historical replay**: `metrics/backtest.json` has never landed."]
    if not board.entries:
        return [
            f"- **Historical replay** ({where}): empty — no corpus with outcome labels "
            "has been replayed yet."
        ]
    lines = [
        f"- **Historical replay** ({where}): {board.predictors_evaluated} predictor(s) over "
        f"{board.events_scored:,} resolved event(s), `{board.stratum}` by construction — "
        "recall and calibration over known history, never foresight, and an **iteration "
        "instrument**: nothing here is a claimable performance figure "
        "(`metrics/README.md`).",
        "",
        "| Predictor | Court | Events | Accuracy | Always-deny floor | Lift | Mean Brier |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for entry in board.entries:
        lines += _backtest_rows(entry)
    lines += [
        "",
        "Read a lift only against its own court's floor. The pooled row mixes outcome "
        + "vocabularies — `granted` is cert on a SCOTUS row and a motion granted on a "
        + "court-of-appeals docket — and mixes an ~80% floor with near-zero ones, so a "
        + "pooled lift can be produced entirely by a court this pipeline does not predict.",
    ]
    return lines


def _salience_replay_lines(vintaged: Vintaged[SalienceReplay], in_force: str) -> list[str]:
    """The gate replay, with the scorer that produced it named beside every figure."""
    replay = vintaged.value
    where = _sourced("salience-replay.json", vintaged)
    if replay is None:
        return ["- **Salience-gate replay**: `metrics/salience-replay.json` has never landed."]
    stale = (
        ""
        if replay.salience_version == in_force
        else (
            f" — produced under `{replay.salience_version}` while **`{in_force}`** is the "
            "scorer in force, so these are that version's numbers and not a current "
            "reading of the gate"
        )
    )
    versions = ", ".join(f"`{v}`" for v in replay.salience_versions) or "—"
    terms = ", ".join(str(term) for term in replay.terms) or "—"
    return [
        f"- **Salience-gate replay** ({where}): {replay.cells_evaluated} cell(s) over "
        f"Term(s) {terms} and {len(replay.policies)} cutoff policy(ies), "
        f"version(s) {versions}{stale}."
    ]


def _cert_backtest_lines(vintaged: Vintaged[CertBacktest]) -> list[str]:
    """The cert back-test, whose absence is the honest thing to report."""
    report = vintaged.value
    if report is None:
        return [
            "- **Cert back-test**: **no report has landed yet.** "
            + "`metrics/cert-backtest.json` is off the scheduled refresh because a "
            + "real-engine replay spends tokens, so it exists only after a maintainer "
            + "dispatches `run-backtest` — there is no number here to be stale."
        ]
    return [
        f"- **Cert back-test** ({_sourced('cert-backtest.json', vintaged)}): "
        f"{report.predictors_evaluated} predictor(s) over {report.events_scored:,} "
        f"petition(s), banded by `{report.salience_version}`; always-deny floor "
        f"{report.always_denied_accuracy:.1%}."
    ]


def _render_backtests(analytics: WeeklyAnalytics) -> list[str]:
    """Section 3: what the replays say, and which replay has never been run."""
    return [
        "",
        "## Backtest results",
        "",
        *_backtest_lines(analytics.backtest),
        *_salience_replay_lines(analytics.salience_replay, analytics.salience_version_in_force),
        *_cert_backtest_lines(analytics.cert_backtest),
    ]


# The non-triggering label the weekly performance digest issues carry — the same
# discipline as `daily-digest` below: no `run:*` workflow keys on it, and it must
# never become one. Its reading state is the issue list too: the maintainer
# closes one once read.
WEEKLY_DIGEST_LABEL = "weekly-digest"

#: One digest an ISO week, and that is what the issue create is idempotent on.
_WEEKLY_DIGEST_MARKER = "<!-- weekly-digest: {week} -->"

#: The weekly body's marker block. One line: unlike the daily digest this body
#: inlines no agent prose, but the tests read the same way for both.
WEEKLY_DIGEST_MARKER_LINES = 1


def _iso_week(generated_at: str) -> str:
    """``YYYY-Www`` for a timestamp, or the timestamp itself if it does not parse."""
    parsed = parse_iso(generated_at)
    if parsed is None:
        return generated_at
    year, week, _ = parsed.isocalendar()
    return f"{year}-W{week:02d}"


def weekly_digest_marker(generated_at: str) -> str:
    """The HTML marker identifying which ISO week a weekly digest covers."""
    return _WEEKLY_DIGEST_MARKER.format(week=_iso_week(generated_at))


def weekly_digest_week(marker: str) -> str | None:
    """The ISO week a weekly-digest marker names, or ``None`` if it is not one.

    The inverse of :func:`weekly_digest_marker`, so a poster handed a rendered
    body can recover the week from the body's own first line rather than being
    told it a second time — and can refuse a file that is not a weekly digest
    instead of opening an issue titled from a guess.
    """
    prefix, suffix = _WEEKLY_DIGEST_MARKER.split("{week}")
    line = marker.strip()
    if not line.startswith(prefix) or not line.endswith(suffix):
        return None
    return line[len(prefix) : len(line) - len(suffix)] or None


def weekly_digest_title(generated_at: str) -> str:
    """The weekly digest issue's title, naming its week."""
    return weekly_digest_title_for_week(_iso_week(generated_at))


def weekly_digest_title_for_week(week: str) -> str:
    """The weekly digest issue's title for an already-resolved ISO week."""
    return f"Weekly performance digest — {week}"


def render_weekly_digest(
    report: OpsReport,
    *,
    analytics: WeeklyAnalytics | None = None,
    production: WeeklyProduction | None = None,
) -> str:
    """The weekly performance digest: the week's substance, on its own issue.

    Four blocks, in the order a reader needs them. The **health questions** are
    short and interrogative — numbers that demand a reaction rather than sit
    available for inspection. **Analytics state** says what the committed boards
    hold, with each empty one explaining *why* it is empty rather than showing a
    bare zero. **Produced this week** counts the cells that ran and what they
    cost, over one window and one set of records. **Backtest results** reports
    the replays, and says plainly that the cert back-test has never been run
    rather than leaving its absence to be inferred from a missing line.

    In the analytics and back-test blocks every figure carries the vintage of
    the artifact it came from, because none of those artifacts is refreshed on
    this schedule: a board is byte-stable and a statpack moves only when the
    corpus does, so a figure without its vintage silently claims to be this
    week's. The health questions keep the dashboard's un-vintaged framing — they
    are the same bullets that surface there, read as questions rather than as
    figures to quote.

    ``analytics`` and ``production`` are optional so the digest degrades to its
    questions rather than failing when a feed is absent.
    """
    lines = [
        weekly_digest_marker(report.generated_at),
        "# Weekly performance digest",
        "",
        f"_Generated {report.generated_at}. Close this issue once you have read it — the "
        "open `weekly-digest` issues are the unread backlog._",
        "",
        "## Health questions",
        "",
        *_health_questions(report),
    ]
    if analytics is not None:
        lines += _render_analytics_state(analytics, report.generated_at)
    if production is not None:
        lines += _render_production(production)
    if analytics is not None:
        lines += _render_backtests(analytics)
    # The marker line stays verbatim; everything below it is defused in one pass,
    # exactly as the daily digest's body is. Almost all of this document is
    # harness-computed figures, but the predictor ids threaded through the board
    # tables are free-form strings from the ledger, and a field added later would
    # otherwise arrive untreated.
    prose = _defuse_comments("\n".join(lines[WEEKLY_DIGEST_MARKER_LINES:]))
    document = "\n".join([*lines[:WEEKLY_DIGEST_MARKER_LINES], prose]) + "\n"
    if len(document) > _DIGEST_MAX_CHARS:
        document = document[: _DIGEST_MAX_CHARS - len(_DIGEST_TRUNCATED)] + _DIGEST_TRUNCATED
    return document


# The non-triggering label the daily prediction-reading digest issues carry (no
# `run:*` workflow keys on it, and it must never become one — an issue opened
# under a trigger label would start a spending run). The reading state is the
# issue list itself: an open digest issue is unread, and closing it is the only
# act the maintainer performs.
DAILY_DIGEST_LABEL = "daily-digest"

#: The idempotency marker, one per digest body. Stateless "have I featured this
#: event" derives from prior digest bodies alone (the ``already_posted``
#: substring check :mod:`fedcourtsai.agent_feedback` uses for the same purpose),
#: so no featured-events store has to be written, committed, or kept in sync.
_DAILY_DIGEST_MARKER = "<!-- daily-digest-event: {key} -->"

#: The *create* guard, which is a different question from the *featured* one and
#: so a different marker. The event marker cannot serve both: once every event
#: has been featured the digest rotates back to the least-recently-read one, and
#: a create guarded on that event's own marker would find it and post nothing —
#: the rotation would be dead on the one path it exists for. A digest is one a
#: day, so the day is what the create is idempotent on: a re-dispatch of a day
#: already digested is a no-op, and a re-read of an old event still opens today's
#: issue.
_DAILY_DIGEST_DAY_MARKER = "<!-- daily-digest-day: {day} -->"

#: How many leading lines of a digest body carry its markers. Both marker tests
#: read only this block, never the whole body: everything below it is text the
#: harness did not write, and a whole-body substring test would let a document
#: that quoted a marker mark some other event read for good.
DAILY_DIGEST_MARKER_LINES = 2

#: Per-document ceiling in the rendered body. Predictor prose runs a few
#: thousand characters, so this truncates only an outlier — and an outlier is
#: exactly what would otherwise push a three-predictor digest past the body
#: limit. A truncated document links to the committed file, which is the
#: complete text.
_DAILY_DIGEST_DOC_MAX_CHARS = 6_000

#: Every digest body's hard ceiling, under GitHub's 65,536-character issue-body
#: limit — refused with a 422 rather than truncated. Both digests are bounded by
#: construction (one event with capped documents; a fixed set of tables); the
#: clamp makes the bound a guarantee no matter how many predictors an event
#: accumulates or how long a board grows.
_DIGEST_MAX_CHARS = 60_000

_DIGEST_TRUNCATED = (
    "\n\n_Digest truncated at the issue-body ceiling; the linked paths and the committed "
    "artifacts carry the rest._\n"
)


def daily_digest_marker(case_id: str, event_id: str) -> str:
    """The HTML marker identifying which event a daily digest body featured."""
    return _DAILY_DIGEST_MARKER.format(key=f"{case_id}/{event_id}")


def daily_digest_day_marker(generated_at: str) -> str:
    """The HTML marker identifying which *day* a digest body was opened for.

    What the issue create is idempotent on — one digest a day — so a re-dispatch
    posts nothing while a rotation back to an already-read event still opens
    today's issue. An unparseable stamp falls back to itself rather than to a
    guessed date, which keeps the guard exact at the cost of being conservative.
    """
    parsed = parse_iso(generated_at)
    day = parsed.date().isoformat() if parsed is not None else generated_at
    return _DAILY_DIGEST_DAY_MARKER.format(day=day)


def _marker_block(body: str) -> str:
    """A digest body's leading marker lines, which is all a marker test may read."""
    return marker_head(body, DAILY_DIGEST_MARKER_LINES)


def _featured_rank(ref: PredictedEventRef, prior_bodies: Sequence[str]) -> int | None:
    """How recently ``ref`` was featured: 0 for the newest body, ``None`` for never.

    ``prior_bodies`` is newest-first, so a larger rank means featured longer ago.
    """
    marker = daily_digest_marker(ref.case_id, ref.event_id)
    return next((i for i, body in enumerate(prior_bodies) if marker in _marker_block(body)), None)


def select_daily_digest_event(
    candidates: Sequence[PredictedEventRef], prior_bodies: Sequence[str]
) -> PredictedEventRef | None:
    """Which predicted event today's digest features, or ``None`` with nothing to read.

    Newest not-yet-featured first — the point of the habit is to read what just
    landed. When every candidate has been featured (the steady state once the
    ledger stops growing daily), rotate to the **least recently featured** one
    rather than repeating yesterday's: a re-read of the oldest reading is worth
    more than a duplicate, and it keeps the digest producing something every day
    without inventing a backlog. What makes the rotation reach a reader is that
    the issue create is guarded on the *day* marker, not this one
    (:func:`daily_digest_day_marker`) — guarded on the event's own marker it
    would refuse every rotated re-read, which is the only case it exists for.

    ``prior_bodies`` are the bodies of previous digest issues, newest first
    (``gh issue list`` order), and are the only state: presence of an event's
    marker in a body's leading marker block is what "featured" means. A digest
    issue whose body a reader edited past recognition simply reads as never
    featured, which repeats one event rather than skipping one.
    """
    if not candidates:
        return None
    blocks = [_marker_block(body) for body in prior_bodies]
    unfeatured = [
        ref
        for ref in candidates
        if not already_posted(blocks, daily_digest_marker(ref.case_id, ref.event_id))
    ]
    if unfeatured:
        return max(unfeatured, key=lambda ref: (ref.latest_run_id, ref.case_id, ref.event_id))
    # Every candidate carries a rank here, since none survived the filter above.
    ranked = [
        (rank, ref) for ref in candidates if (rank := _featured_rank(ref, prior_bodies)) is not None
    ]
    return max(ranked, key=lambda pair: (pair[0], pair[1].case_id, pair[1].event_id))[1]


def daily_digest_cell_heading(predictor_id: str, run_id: str) -> str:
    """The heading of one predictor cell's section in a digest body.

    Public because it is the only handle on a section: the prose a section
    carries is agent-written and routinely contains its own ``##`` headings, so
    counting headings identifies nothing. A caller — including a test asserting
    the digest covered every cell — asks for this exact string instead.
    """
    return f"## {predictor_id} · run `{run_id}`"


def _repo_link(label: str, path: str, *, repo: str, ref: str) -> str:
    """A markdown link to a committed path, or bare backticks without a repo."""
    if not repo:
        return f"`{path}`"
    return f"[{label}](https://github.com/{repo}/blob/{ref}/{path})"


def _defuse_comments(text: str) -> str:
    """Neutralize HTML-comment openers without changing what the text says.

    The digest's whole state lives in HTML markers, and everything below the
    marker block is text the harness did not write: agent prose from cells that
    read docket text and, on a forward cell, the open web, plus the corpus's own
    case caption. ``&lt;!--`` renders as the literal characters and is *not* a
    comment, so a document that quotes a marker is shown exactly as written and
    cannot be mistaken for one. Applied once over the assembled document rather
    than per field, so a field added to the digest later cannot fall off an
    allowlist. The marker tests read only the leading block in any case
    (:func:`_marker_block`); this is the second of two independent controls,
    because a body reaching a reader who greps it should carry no forged marker
    either.
    """
    return text.replace("<!--", "&lt;!--")


def _digest_document(
    title: str, text: str | None, *, missing: str, link: str, filename: str
) -> list[str]:
    """One document block: the prose inline, truncated to the per-document cap.

    A truncated document says so and carries the link to the complete file, so
    the digest never presents a cut-off argument as the whole of one.
    """
    if text is None:
        return ["", f"**{title}**", "", f"_{missing}_"]
    body = text.strip()
    if len(body) > _DAILY_DIGEST_DOC_MAX_CHARS:
        body = (
            body[:_DAILY_DIGEST_DOC_MAX_CHARS].rstrip()
            + f"\n\n_…truncated at {_DAILY_DIGEST_DOC_MAX_CHARS:,} characters; "
            + f"the full `{filename}` is in {link}._"
        )
    return ["", f"**{title}**", "", body]


def _digest_context_line(prediction: Prediction) -> str:
    """The cell's leakage-relevant framing: mode, snapshot vintage, band."""
    context = prediction.context
    if context is None:
        return "mode — · snapshot — _(no context block recorded)_"
    snapshot = context.snapshot_date.isoformat() if context.snapshot_date is not None else "—"
    band = f" · band `{context.band}`" if context.band is not None else ""
    return f"mode `{context.mode}` · snapshot **{snapshot}** ({context.snapshot_provenance}){band}"


#: What ``Prediction.probability`` is the probability *of*, by stage. The field
#: is P(granted) on a cert or interim event and P(disturbed) on a merits one, so
#: a digest that labelled it with the predicted disposition would read "P(denied)
#: = 0.93" on a confident deny — the number inverted by its own caption.
_STAGE_BINARY_LABEL = {
    Stage.cert: "P(granted)",
    Stage.interim: "P(granted)",
    Stage.merits: "P(disturbed)",
}


def _probability_label(event: PredictableEvent | None) -> str:
    """The caption for ``Prediction.probability`` on this event's stage.

    Reads the stage through :func:`fedcourtsai.store.normalized_stage`, the rule
    the stratified boards use: most committed petition events record no stage at
    all, and declining to normalize would caption the digest's headline number —
    the one figure it exists to make readable — as an unnamed binary on the
    majority of the ledger.
    """
    if event is None:
        return "P(the stage's own binary — no event definition committed)"
    stage = normalized_stage(event.kind, event.stage)
    if stage is None:
        return "P(the stage's own binary — no stage recorded for this kind)"
    return _STAGE_BINARY_LABEL.get(stage, "P(the stage's own binary)")


def _digest_cell_lines(
    cell: PredictionCell, *, probability_label: str, repo: str, ref: str
) -> list[str]:
    """One predictor's section: its numbers, its two documents, its flags."""
    p = cell.prediction
    link = _repo_link("cell artifacts", cell.cell_path, repo=repo, ref=ref)
    lines = [
        "",
        # The run id belongs in the heading, not only the line under it: an event
        # a predictor ran twice contributes two sections, and two identically
        # titled ones would be indistinguishable to a reader — and to anything
        # that looks a section up by its heading.
        daily_digest_cell_heading(p.predictor_id, p.run_id),
        "",
        f"**{probability_label} = {p.probability:.2f}** · predicted disposition "
        f"`{p.predicted_disposition}` · engine `{p.engine}` · "
        f"model `{p.model or '—'}`",
        "",
        _digest_context_line(p),
    ]
    if p.big_case_score is not None:
        stated = " ".join((p.big_case_rationale or "").split())
        rationale = f" — {stated}" if stated else ""
        lines += ["", f"Big-case score **{p.big_case_score:.2f}**{rationale}"]
    if p.claims:
        lines += [
            "",
            "| Claim | P |",
            "| --- | ---: |",
            *[f"| `{c.claim_id}` | {c.probability:.2f} |" for c in p.claims],
        ]
    lines += _digest_document(
        "Predicted reasoning (what the Court will do)",
        cell.predicted_reasoning,
        missing="No predicted-reasoning document is committed for this cell.",
        link=link,
        filename=p.predicted_reasoning_doc or "predicted_reasoning.md",
    )
    lines += _digest_document(
        "Rationale (why this number)",
        cell.reasoning,
        missing="No rationale document is committed for this cell.",
        link=link,
        filename=p.reasoning_doc,
    )
    if cell.flags is not None and cell.flags.flags:
        lines += ["", "**Flags**", ""]
        lines += [
            f"- `{flag.severity}` `{flag.category}` — " + " ".join(flag.message.split())
            for flag in cell.flags.flags
        ]
    lines += ["", f"Full artifacts: {link}"]
    return lines


def render_daily_digest(
    event: PredictedEvent, *, generated_at: str, repo: str = "", ref: str = "main"
) -> str:
    """Render one predicted event, every predictor side by side, as an issue body.

    The reading surface: what the models actually said about one case, in one
    bounded document a maintainer reads and then closes. The first two lines are
    the markers a later run reads back — which event this featured, and which day
    it was opened for — so they must stay in the body; a reader who edits them
    out re-queues the event rather than breaking anything.

    ``repo`` (``owner/name``) turns the committed paths into links at ``ref``;
    without it the paths render as bare code spans, which is what a local
    dry-run wants.
    """
    definition = event.event
    title = definition.title if definition is not None else event.case_id
    court, _, docket = event.case_id.partition("/")
    lines = [
        daily_digest_marker(event.case_id, event.event_id),
        daily_digest_day_marker(generated_at),
        f"# {title}",
        "",
        f"_Generated {generated_at}. Close this issue once you have read it — the open "
        "`daily-digest` issues are the unread backlog._",
        "",
        f"- **Case** `{event.case_id}` — court `{court}`, docket `{docket}`",
    ]
    if definition is not None:
        moment = definition.moment or "—"
        stage = definition.stage or "—"
        lines.append(
            f"- **Event** `{event.event_id}` — kind `{definition.kind}`, stage `{stage}`, "
            f"moment `{moment}`, target `{definition.decision_target}`"
        )
        lines.append(f"- **Resolved** {'yes' if definition.resolved else 'not yet'}")
    else:
        lines.append(f"- **Event** `{event.event_id}` — _no `event.yaml` committed for this event_")
    contexts = {_digest_context_line(cell.prediction) for cell in event.cells}
    lines.append(
        f"- **Cells** {len(event.cells)} predictor cell(s) · "
        + (contexts.pop() if len(contexts) == 1 else "context varies by cell (see each section)")
    )
    ledger_link = _repo_link("event directory", event.event_path, repo=repo, ref=ref)
    lines.append(f"- **Ledger** {ledger_link}")
    label = _probability_label(definition)
    for cell in event.cells:
        lines += _digest_cell_lines(cell, probability_label=label, repo=repo, ref=ref)
    # The marker block is the harness's own two lines and stays verbatim;
    # everything below it — the corpus's case caption included — is defused in
    # one pass, so no field can be added to the digest and miss the treatment.
    prose = _defuse_comments("\n".join(lines[DAILY_DIGEST_MARKER_LINES:]))
    document = "\n".join([*lines[:DAILY_DIGEST_MARKER_LINES], prose]) + "\n"
    if len(document) > _DIGEST_MAX_CHARS:
        document = document[: _DIGEST_MAX_CHARS - len(_DIGEST_TRUNCATED)] + _DIGEST_TRUNCATED
    return document


def daily_digest_title(event: PredictedEvent) -> str:
    """The digest issue's title: the case, so the issue list reads as a reading queue.

    Defused like the body: the caption is the corpus's text, not the harness's.
    """
    definition = event.event
    subject = definition.title if definition is not None else event.case_id
    return _defuse_comments(f"Daily digest: {subject} ({event.case_id} {event.event_id})")


def _as_utc(stamp: datetime) -> datetime:
    """Treat a naive ``created_at`` as UTC so ledger stamps stay comparable.

    ``ModelUsage.created_at`` is an unconstrained ``datetime``, so a naive stamp
    is schema-valid. Mixing naive and aware stamps raises on comparison, which
    would take the whole ops report down over one malformed record — the ledger
    is written by agents, so tolerate the shape rather than trusting it.
    """
    return stamp.replace(tzinfo=UTC) if stamp.tzinfo is None else stamp


def summarize_spend(usage: Iterable[ModelUsage]) -> SpendSummary:
    """Roll the recorded usage ledger up into total tokens + estimated cost."""
    rows = list(usage)
    runs = len(rows)
    cost = sum(r.estimated_cost_usd for r in rows)
    tokens = sum(
        r.input_tokens + r.output_tokens + r.cache_read_input_tokens + r.cache_creation_input_tokens
        for r in rows
    )
    # The ledger's own span, so cumulative spend can be turned into a rate. A
    # single record — or a batch that all landed on one instant — spans nothing
    # and stays unrated rather than being divided by zero. Kept unrounded: this
    # is a divisor, and rounding it to a display precision would let the render
    # format move the reported rate (a sub-day span rounds to 0.1d or, on a
    # fresh ledger, to 0.0d — silently unrating a real rate).
    stamps = [_as_utc(r.created_at) for r in rows]
    span = (max(stamps) - min(stamps)).total_seconds() / 86400.0 if len(stamps) > 1 else 0.0
    return SpendSummary(
        runs=runs,
        total_tokens=tokens,
        estimated_cost_usd=round(cost, 6),
        mean_cost_usd_per_run=round(cost / runs, 6) if runs else 0.0,
        window_days=span if span > 0 else None,
    )


# The dashboard's agent digests (flags, leakage, tooling) count only runs within
# this many days of generation, so resolved-and-old signal stops dominating the
# summary. The raw flags.json ledger and the agent-feedback issue keep everything;
# this only scopes the roll-up.
_AGENT_DIGEST_WINDOW_DAYS = 14


def _parse_run_id(run_id: str) -> datetime | None:
    """A ``YYYYMMDDThhmmssZ`` run id as a UTC datetime, or None if it doesn't parse."""
    try:
        return datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return None


def _within_window(run_id: str, generated_at: str, window_days: int) -> bool:
    """Whether ``run_id`` falls within ``window_days`` before ``generated_at``.

    A run id or ``generated_at`` that does not parse counts as in-window, so a
    malformed stamp is surfaced rather than silently dropped from the summary.
    """
    run_dt = _parse_run_id(run_id)
    gen_dt = parse_iso(generated_at)
    if run_dt is None or gen_dt is None:
        return True
    # run_dt is always UTC-aware; a hand-passed naive `generated_at` would otherwise
    # crash the aware/naive comparison, so treat a bare timestamp as UTC.
    if gen_dt.tzinfo is None:
        gen_dt = gen_dt.replace(tzinfo=UTC)
    return run_dt >= gen_dt - timedelta(days=window_days)


# How many of the most recent flag-raising cells the dashboard table lists (within
# the window above); the severity counts cover every in-window flag, so the cap
# never hides volume inside the window.
_FLAGS_RECENT_LIMIT = 20

# How many `likely` leakage gradings the dashboard names individually.
_LEAKAGE_FLAGGED_LIMIT = 20


def summarize_leakage(
    evaluations: Iterable[Evaluation],
    *,
    generated_at: str,
    window_days: int = _AGENT_DIGEST_WINDOW_DAYS,
    limit: int = _LEAKAGE_FLAGGED_LIMIT,
) -> LeakageDigest:
    """Roll the evaluators' leakage gradings into the dashboard's leakage digest.

    The visibility half of the backtest-as-iteration doctrine: counts over every
    committed ``evaluation.json`` that carries a ``leakage`` block and lands within
    ``window_days`` of ``generated_at``, with the ``likely`` offenders named (newest
    first, capped) so a repeat pattern is attributable to its predictor rather than
    lost in a count.
    """
    assessed = not_applicable = none = possible = likely = 0
    flagged: list[tuple[str, str]] = []
    for evaluation in evaluations:
        if evaluation.leakage is None:
            continue
        if not _within_window(evaluation.run_id, generated_at, window_days):
            continue
        assessed += 1
        verdict = evaluation.leakage.influenced_prediction
        if verdict == "not_applicable":
            not_applicable += 1
        elif verdict == "none":
            none += 1
        elif verdict == "possible":
            possible += 1
        else:
            likely += 1
            flagged.append(
                (
                    evaluation.run_id,
                    f"{evaluation.case_id} {evaluation.event_id} "
                    f"{evaluation.predictor_id} (by {evaluation.evaluator_id})",
                )
            )
    flagged.sort(reverse=True)
    return LeakageDigest(
        assessed=assessed,
        not_applicable=not_applicable,
        none=none,
        possible=possible,
        likely=likely,
        flagged=[label for _, label in flagged[:limit]],
        window_days=window_days,
    )


def summarize_flags(
    flag_sets: Iterable[AgentFlags],
    *,
    generated_at: str,
    window_days: int = _AGENT_DIGEST_WINDOW_DAYS,
    limit: int = _FLAGS_RECENT_LIMIT,
) -> FlagsDigest:
    """Roll committed ``flags.json`` sets into the dashboard's open-flags digest.

    Only cells from runs within ``window_days`` of ``generated_at`` feed the counts
    and the ``recent`` table, so long-since-fixed flags stop dominating the summary;
    ``archived`` reports how many older flags remain in the ``flags.json`` ledger and
    the agent-feedback issue. ``recent`` keeps the most recent in-window flag-raising
    cells (by run id, newest first) capped at ``limit``.
    """
    all_sets = list(flag_sets)
    sets = [fs for fs in all_sets if _within_window(fs.run_id, generated_at, window_days)]
    counts = {FlagSeverity.blocker: 0, FlagSeverity.warning: 0, FlagSeverity.info: 0}
    for fs in sets:
        for flag in fs.flags:
            counts[FlagSeverity(flag.severity)] += 1
    archived = sum(len(fs.flags) for fs in all_sets) - sum(counts.values())
    # Run ids are UTC timestamps, so descending lexical order is newest-first.
    recent = sorted(sets, key=lambda fs: (fs.run_id, fs.case_id, fs.actor_id), reverse=True)[:limit]
    return FlagsDigest(
        total=sum(counts.values()),
        cells=len(sets),
        blockers=counts[FlagSeverity.blocker],
        warnings=counts[FlagSeverity.warning],
        infos=counts[FlagSeverity.info],
        recent=recent,
        window_days=window_days,
        archived=archived,
    )


# How many of the most recent full tooling reports the dashboard lists in detail;
# the aggregate counts still cover every committed report.
_TOOLING_RECENT_LIMIT = 8
# How many distinct helpful/gap items the dashboard ranks (the long tail is noise).
_TOOLING_ITEMS_LIMIT = 10


def _rank_items(items: Iterable[str], *, limit: int) -> list[ToolingCount]:
    """Count free-text items and return the most common first, ties stable by label."""
    counts = Counter(item.strip() for item in items if item.strip())
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]
    return [ToolingCount(label=label, count=count) for label, count in ranked]


def summarize_tooling(
    reports: Iterable[AgentToolingFeedback],
    *,
    generated_at: str,
    window_days: int = _AGENT_DIGEST_WINDOW_DAYS,
    recent_limit: int = _TOOLING_RECENT_LIMIT,
    items_limit: int = _TOOLING_ITEMS_LIMIT,
) -> ToolingDigest:
    """Roll committed ``tooling.json`` self-reports into the dashboard's tooling digest.

    Only reports within ``window_days`` of ``generated_at`` feed the digest, so the
    signal tracks current tooling rather than the whole history. ``corpus_query_uses``
    / ``base_rate_uses`` of ``reports`` cells used the query and base-rate ``stats``
    CLIs; ``helpful`` / ``gaps`` rank the most-mentioned abilities and missing tools
    across the in-window reports; ``recent`` keeps the latest few full reports (by run
    id, newest first) for detail.

    ``corpus_query_uses`` is denominated over **every** in-window report, which is
    not what the run PR's prior-availability note counts: that one denominates over
    the cells whose corpus attempt the harness could see in their retrieval log,
    and reads the same boolean as one side of a two-channel comparison. Same
    field, different questions — "how many cells report using the tool" here,
    "does a cell that demonstrably ran it also report using it" there.
    """
    items = [r for r in reports if _within_window(r.run_id, generated_at, window_days)]
    recent = sorted(items, key=lambda r: (r.run_id, r.case_id, r.actor_id), reverse=True)[
        :recent_limit
    ]
    return ToolingDigest(
        reports=len(items),
        corpus_query_uses=sum(1 for r in items if r.used_corpus_query),
        base_rate_uses=sum(1 for r in items if r.used_base_rates),
        helpful=_rank_items((h for r in items for h in r.helpful), limit=items_limit),
        gaps=_rank_items((g for r in items for g in r.gaps), limit=items_limit),
        recent=recent,
        window_days=window_days,
    )


def parse_iso(value: str) -> datetime | None:
    """An ISO-8601 stamp as a datetime, or ``None`` when it does not parse.

    Public because every surface that reads a report's free-string
    ``generated_at`` has to agree about what fails to parse: two parsers would
    let one of them fall back while the other carried the raw string, which is
    how a report ends up pairing a clock-anchored window with a marker naming
    no week.
    """
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def estimate_cost(runs: Iterable[Mapping[str, object]], spend: SpendSummary) -> CostEstimate:
    """Rough monthly cost run-rate from run durations + recorded spend + fixed infra.

    GitHub Actions minutes are summed from completed-run wall-clock and priced
    at the configured per-minute rate — zero on this public repository, where
    standard runners are free, so the minutes ride along as a runtime-health
    signal rather than a dollar figure.

    Model token cost is the dominant variable cost of the tournament, so it is
    rated (over the usage ledger's own span, which is not the Actions window) and
    added into the projection. It used to be reported cumulatively and left out,
    which made the headline run-rate the fixed infra alone — reassuring, and wrong
    by the entire model bill.

    The projection is None whenever a component that is known to be nonzero cannot
    be rated. A total that silently drops the biggest line item reads as authoritative
    and understates; no number at all prompts a look at the provider dashboard.
    """
    run_list = list(runs)
    seconds = [s for r in run_list if (s := _run_seconds(r)) is not None]
    actions_minutes = sum(seconds) / 60.0
    actions_cost = actions_minutes * _ACTIONS_USD_PER_MINUTE

    starts = [t for r in run_list if (t := parse_iso(str(r.get("createdAt") or ""))) is not None]
    window_days = (max(starts) - min(starts)).total_seconds() / 86400.0 if len(starts) > 1 else None
    actions_monthly = (
        actions_cost / window_days * _DAYS_PER_MONTH if window_days and window_days > 0 else None
    )
    model_window = spend.window_days
    model_monthly = (
        spend.estimated_cost_usd / model_window * _DAYS_PER_MONTH
        if model_window is not None and model_window > 0
        else None
    )
    # A component suppresses the total only when it is known-nonzero *and*
    # unrateable — that is when a total would understate. An unrateable
    # known-zero component costs nothing to omit, so it must not blank the
    # headline: on this public repo Actions is always $0, and a quiet week (too
    # few dated runs to span a window) would otherwise erase a fully-rated model
    # figure. Degrade the component, not the number the dashboard exists to show.
    unrated_actions = actions_cost > 0 and actions_monthly is None
    unrated_spend = spend.estimated_cost_usd > 0 and model_monthly is None
    estimated_monthly = (
        None
        if unrated_actions or unrated_spend
        else round((actions_monthly or 0.0) + (model_monthly or 0.0) + _FIXED_MONTHLY_USD, 2)
    )
    return CostEstimate(
        window_days=round(window_days, 1) if window_days is not None else None,
        actions_minutes=round(actions_minutes, 1),
        actions_cost_usd=round(actions_cost, 4),
        actions_monthly_usd=round(actions_monthly, 2) if actions_monthly is not None else None,
        model_cost_usd=spend.estimated_cost_usd,
        model_monthly_usd=round(model_monthly, 2) if model_monthly is not None else None,
        fixed_monthly_usd=_FIXED_MONTHLY_USD,
        estimated_monthly_usd=estimated_monthly,
    )


def build_ops_report(  # noqa: PLR0913 - aggregates independent read-only sources, one arg each
    *,
    generated_at: str,
    runs: Iterable[Mapping[str, object]],
    usage: Iterable[ModelUsage],
    flags: Iterable[AgentFlags] = (),
    tooling: Iterable[AgentToolingFeedback] = (),
    evaluations: Iterable[Evaluation] = (),
    substance: SubstanceDigest | None = None,
    data_health: DataHealth | None = None,
    open_triggers: list[OpenTriggerIssue] | None = None,
) -> OpsReport:
    """Assemble the full operational snapshot. ``generated_at`` is passed in (no clock).

    ``data_health`` is the data-validation verdict the dashboard presents alongside
    run health; it is surfaced as supplied (the wiring layer owns producing it),
    null when absent. ``substance`` is the substantive-results digest
    (:func:`summarize_substance`), surfaced the same way. ``flags`` is the committed
    ``flags.json`` ledger the dashboard rolls into its open-flags digest and
    ``tooling`` the committed ``tooling.json`` self-reports it rolls into the
    tooling-feedback digest (each empty when none are committed).
    """
    run_list = list(runs)
    spend = summarize_spend(usage)
    return OpsReport(
        generated_at=generated_at,
        health=summarize_health(run_list),
        spend=spend,
        cost=estimate_cost(run_list, spend),
        substance=substance,
        data_health=data_health,
        flags=summarize_flags(flags, generated_at=generated_at),
        leakage=summarize_leakage(evaluations, generated_at=generated_at),
        tooling=summarize_tooling(tooling, generated_at=generated_at),
        open_triggers=open_triggers,
    )


def _fmt_duration(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}m{secs:02d}s" if minutes else f"{secs}s"


# The fan-out labels an issue may still be wearing. Nothing keys on them — no
# workflow triggers on ``issues: labeled`` at all — so an open issue carrying one
# is a leftover marker rather than queued work, and the dashboard surfaces it so
# a reader does not mistake it for a round in flight.
TRIGGER_LABELS: tuple[str, ...] = ("run:predict", "run:evaluate")


def summarize_trigger_issues(raw: Iterable[Mapping[str, object]]) -> list[OpenTriggerIssue]:
    """Normalize a ``gh issue list --json number,title,labels,createdAt`` feed.

    Keeps only issues carrying one of :data:`TRIGGER_LABELS`, oldest first — the
    ones that have sat longest lead. The feed shape is gh's: ``labels`` is a list
    of ``{"name": ...}`` objects.
    """
    issues: list[OpenTriggerIssue] = []
    for entry in raw:
        labels = entry.get("labels")
        if not isinstance(labels, list):
            continue
        names = {str(label.get("name", "")) for label in labels if isinstance(label, Mapping)}
        trigger = next((label for label in TRIGGER_LABELS if label in names), None)
        if trigger is None:
            continue
        issues.append(
            OpenTriggerIssue(
                number=int(str(entry.get("number", 0))),
                label=trigger,
                title=str(entry.get("title", "")),
                created_at=str(entry.get("createdAt", "")),
            )
        )
    issues.sort(key=lambda issue: (issue.created_at, issue.number))
    return issues


def _age(created_at: str, generated_at: str) -> str:
    """A compact ``3d`` / ``7h`` / ``25m`` age, or a dash when either time is unparseable."""
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        now = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except ValueError:
        return "—"
    seconds = max(0, int((now - created).total_seconds()))
    if seconds >= 86_400:
        return f"{seconds // 86_400}d"
    if seconds >= 3_600:
        return f"{seconds // 3_600}h"
    return f"{seconds // 60}m"


def render_open_triggers(issues: list[OpenTriggerIssue], generated_at: str) -> str:
    """Render the stale-fan-out-label section, oldest first.

    An open issue wearing one is a marker somebody left behind, not queued work —
    a round derives its cases from committed state, so nothing is waiting on it.
    Empty gets a one-line all-clear so a healthy dashboard still shows the check
    ran. Deleting the two labels from the repository retires the section for
    good: nothing creates them, so an empty scan is the resting state and a
    cleared backlog of markers is a permanent one.
    """
    if not issues:
        return "## Stale fan-out labels\n\n_None — no stale fan-out label is open._\n"
    lines = [
        "## Stale fan-out labels",
        "",
        f"**{len(issues)}** open issue(s) carrying a fan-out label. The label starts "
        "nothing — a predict or evaluate round derives its own backlog on its own "
        "schedule — so this is a stale marker to clear, not a run to re-fire.",
        "",
        "| issue | label | age | title |",
        "|-------|-------|----:|-------|",
    ]
    for issue in issues:
        lines.append(
            f"| #{issue.number} | `{issue.label}` | {_age(issue.created_at, generated_at)} "
            f"| {issue.title} |"
        )
    return "\n".join(lines) + "\n"


def render_data_health(health: DataHealth) -> str:
    """Render the data-health section: the ledger + corpus verdict, with failing detail.

    Used both as a section of the dashboard and, on a failing verdict, as the body of
    the long-lived data-validation escalation issue — so it stands on its own.
    """
    lines = ["## Data health", "", f"**{'✅ Healthy' if health.ok else '❌ Failing'}**", ""]

    ledger = health.ledger
    if ledger is None:
        lines.append("- **Ledger schema** (`validate` over `data/`): _not run_")
    else:
        summary = (
            f"{ledger.checked:,} artifact(s) valid"
            if ledger.ok
            else f"{ledger.invalid} invalid / {ledger.checked} checked"
        )
        lines.append(
            f"- {'✅' if ledger.ok else '❌'} **Ledger schema** "
            f"(`validate` over `data/`): {summary}"
        )

    corpus_v = health.corpus
    if corpus_v is None:
        lines.append("- **Corpus integrity** (`validate-corpus`): _no verdict yet_")
    elif corpus_v.skipped:
        lines.append("- **Corpus integrity** (`validate-corpus`): _skipped (no corpus pulled)_")
    else:
        passed = sum(1 for c in corpus_v.checks if c.passed)
        lines.append(
            f"- {'✅' if corpus_v.ok else '❌'} **Corpus integrity** (`validate-corpus`): "
            f"{passed}/{len(corpus_v.checks)} check(s) over {corpus_v.corpus_rows:,} row(s)"
        )

    rows: list[tuple[str, int, str]] = []
    if ledger is not None and not ledger.ok:
        rows.append(
            ("ledger schema", ledger.invalid, ledger.problems[0] if ledger.problems else "")
        )
    if corpus_v is not None and not corpus_v.skipped:
        rows += [
            (c.name, c.failures, c.problems[0] if c.problems else c.detail)
            for c in corpus_v.checks
            if not c.passed
        ]
    if rows:
        lines += ["", "| Check | Failures | Sample |", "|-------|---------:|--------|"]
        lines += [f"| {name} | {n} | {sample.replace('|', '\\|')} |" for name, n, sample in rows]

    lines += _monitored_lines(health)

    return "\n".join(lines) + "\n"


def _monitored_lines(health: DataHealth) -> list[str]:
    """The _Monitored_ block: checks that passed while counting failures.

    Two shapes qualify, and neither is a defect: held within an accepted
    baseline (``case_dates_ordered``), or advisory, where the count is a
    backlog only a data pass can clear
    (``docket_numbers_carry_no_capital_marking``). Both keep the verdict green,
    which is exactly why the block has to render on a **green** dashboard as
    well as a failing one — a count that only ever appears beside a failure is
    invisible in the only state it actually occurs in.
    """
    corpus_v = health.corpus
    monitored = (
        [c for c in corpus_v.checks if c.passed and c.failures]
        if corpus_v is not None and not corpus_v.skipped
        else []
    )
    if not monitored:
        return []
    return ["", "_Monitored (a known condition, not a defect):_"] + [
        f"- {c.name}: {c.detail}" for c in monitored
    ]


def render_leakage_digest(digest: LeakageDigest) -> str:
    """The dashboard's leakage subsection: is outcome material tainting iteration signal?"""
    window = f"last {digest.window_days}d" if digest.window_days else "all time"
    lines = [
        "### Leakage (advisory)",
        f"{digest.assessed} assessed · {digest.not_applicable} forward (n/a) · "
        f"{digest.none} clean · {digest.possible} possible · **{digest.likely} likely** "
        f"({window})",
    ]
    if digest.flagged:
        lines.append("")
        lines += [f"- {label}" for label in digest.flagged]
    elif digest.assessed == 0:
        lines.append("")
        lines.append(f"_No leakage assessments in the {window}._")
    return "\n".join(lines) + "\n"


def render_flags_digest(digest: FlagsDigest) -> str:
    """Render the dashboard's agent-flags subsection from the digest.

    Scoped to the digest's recency window, so long-since-fixed flags do not dominate;
    leads with the in-window severity breakdown (older flags noted as archived in the
    ledger), then the most recent flag-raising cells using the same table the per-run
    roll-up renders (:func:`fedcourtsai.collect.flags_table`).
    """
    window = f"last {digest.window_days}d" if digest.window_days else "all time"
    archived = f" · {digest.archived} older archived in the ledger" if digest.archived else ""
    if digest.total == 0:
        tail = (
            f" {digest.archived} older flag(s) archived in the ledger." if digest.archived else ""
        )
        return f"### Flags\n\n_No flags in the {window}._{tail}\n"
    breakdown = " · ".join(
        part
        for part in (
            f"🛑 {digest.blockers} blocker" if digest.blockers else "",
            f"⚠️ {digest.warnings} warning" if digest.warnings else "",
            f"{digest.infos} info" if digest.infos else "",
        )
        if part
    )
    shown = sum(len(fs.flags) for fs in digest.recent)
    note = f" · showing the {shown} most recent" if shown < digest.total else ""
    lines = [
        "### Flags",
        "",
        f"**{digest.total}** flag(s) across **{digest.cells}** cell(s) in the {window} — "
        f"{breakdown}{note}{archived}.",
        "",
        "Notes agents surfaced from committed `flags.json`, for triage.",
        "",
        flags_table(digest.recent),
    ]
    return "\n".join(lines) + "\n"


def _tooling_item_line(item: ToolingCount) -> str:
    label = " ".join(item.label.split()).replace("|", "\\|")
    suffix = f" ({item.count})" if item.count > 1 else ""
    return f"- {label}{suffix}"


def render_tooling_digest(digest: ToolingDigest) -> str:
    """Render the dashboard's agent tooling-feedback section from the digest.

    Leads with how many cells used the corpus-query and base-rate CLIs, then the
    most-mentioned helpful abilities and missing tools — the across-runs signal on
    whether the tooling earns its keep and where to invest. An empty ledger gets a
    one-line note.
    """
    window = f"last {digest.window_days}d" if digest.window_days else "all time"
    if digest.reports == 0:
        return f"### Tooling feedback\n\n_No tooling reports in the {window}._\n"
    query_share = f"{digest.corpus_query_uses}/{digest.reports}"
    base_rate_share = f"{digest.base_rate_uses}/{digest.reports}"
    lines = [
        "### Tooling feedback",
        "",
        (
            f"**{digest.reports}** self-report(s) ({window}) — corpus-query CLI used by "
            f"**{query_share}**, base-rate `stats` by **{base_rate_share}**. "
            "What agents say helped and what they wished they had."
        ),
    ]
    if digest.helpful:
        lines += ["", "**Most helpful**", *[_tooling_item_line(i) for i in digest.helpful]]
    if digest.gaps:
        lines += ["", "**Wished-for / missing**", *[_tooling_item_line(i) for i in digest.gaps]]
    return "\n".join(lines) + "\n"


def _render_agent_signals(report: OpsReport) -> list[str]:
    """The grouped 'Agent signals' section lines, or ``[]`` when no digests are present.

    Flags, leakage, and tooling are all scoped to the same recency window, so they read
    as one current-state block rather than three drifting all-time sections.
    """
    blocks: list[str] = []
    if report.flags is not None:
        blocks.append(render_flags_digest(report.flags).rstrip("\n"))
    if report.leakage is not None:
        blocks.append(render_leakage_digest(report.leakage).rstrip("\n"))
    if report.tooling is not None:
        blocks.append(render_tooling_digest(report.tooling).rstrip("\n"))
    if not blocks:
        return []
    window_days = next(
        (d.window_days for d in (report.flags, report.leakage, report.tooling) if d is not None),
        0,
    )
    heading = f"## Agent signals (last {window_days}d)" if window_days else "## Agent signals"
    out = ["", heading]
    for block in blocks:
        out += ["", block]
    return out


def render_markdown(report: OpsReport) -> str:
    """Render the dashboard body posted to the run-ops issue / step summary.

    A consolidated view: dormant workflows drop out of the health table, spend and
    cost share one section, the agent-surfaced signals (flags, leakage, tooling) are
    grouped and scoped to a recent window, and a healthy data verdict collapses to
    its one-line summary plus any monitored counts — the full breakdown appears
    only on a failing verdict (where :func:`render_data_health` is also the
    escalation-issue body). The monitored block is a standing part of the green
    dashboard, not an exception: a check that passes while counting failures
    never reddens a verdict, so this is the only state it is ever seen in.
    """
    lines: list[str] = [
        "# Ops dashboard",
        "",
        f"_Generated {report.generated_at}._",
        "",
        "## Pipeline health",
    ]
    # Only workflows that actually ran in the window; a wall of dormant/retired
    # "skipped 0% (0/0)" rows is the clutter, so summarize them in one line instead.
    active = [h for h in report.health if h.successes + h.failures > 0]
    if active:
        lines += [
            "| Workflow | Last | Success rate | Failures | Median | p95 |",
            "|----------|------|-------------:|---------:|-------:|----:|",
        ]
        for h in active:
            rate = (
                "—"
                if h.success_rate is None
                else f"{round(100 * h.success_rate)}% ({h.successes}/{h.successes + h.failures})"
            )
            last = h.last_conclusion or "—"
            lines.append(
                f"| {h.workflow} | {last} | {rate} | {h.failures} | "
                f"{_fmt_duration(h.median_seconds)} | {_fmt_duration(h.p95_seconds)} |"
            )
        gates = sorted(h.workflow for h in active if h.workflow in _GATE_WORKFLOWS)
        if gates:
            lines += [
                "",
                f"_{', '.join(gates)} is level-triggered: a failure there reports an "
                "unsatisfied gate (with the fix in its own run summary), not a broken "
                "workflow — read its rate as promotion attempts, not incidents._",
            ]
        dormant = len(report.health) - len(active)
        if dormant:
            lines += ["", f"_{dormant} dormant workflow(s) with no runs in the window hidden._"]
    else:
        lines.append("_No runs in the window._")

    if report.substance is not None:
        lines += ["", render_substance(report.substance).rstrip("\n")]

    # Spend and cost run-rate are one money story — one section.
    s = report.spend
    ce = report.cost
    monthly = "—" if ce.estimated_monthly_usd is None else f"${ce.estimated_monthly_usd:,.0f}/mo"
    actions_monthly = (
        "—" if ce.actions_monthly_usd is None else f"${ce.actions_monthly_usd:,.0f}/mo"
    )
    model_monthly = "—" if ce.model_monthly_usd is None else f"${ce.model_monthly_usd:,.0f}/mo"
    lines += [
        "",
        "## Spend & cost",
        f"**{s.runs}** run(s) · **{s.total_tokens:,}** tokens · "
        f"**${s.estimated_cost_usd:,.2f}** est. (~${s.mean_cost_usd_per_run:.4f}/run).",
        "",
        f"Run-rate **~{monthly}** projected · model {model_monthly} "
        f"(${ce.model_cost_usd:,.2f} cumulative over "
        f"{'—' if s.window_days is None else f'{s.window_days:.1f}d'} of ledger) · "
        f"Actions {actions_monthly} ({ce.actions_minutes:,.0f} min ~ "
        f"${ce.actions_cost_usd:,.2f} over "
        f"{'—' if ce.window_days is None else f'{ce.window_days:g}d'} of run history) · "
        f"fixed ${ce.fixed_monthly_usd:,.0f}/mo.",
        "",
        "> Rough estimate at the `docs/budget.md` rates (Actions from run durations, "
        + "no billing-API access); check the provider billing dashboards for ground truth. "
        + "The model rate averages the usage ledger's **full span**, first record to "
        + "last — a trailing pause does not deflate it, but an interior gap or a "
        + "low-volume early era does, so it trends toward a lifetime average as "
        + "history accumulates.",
    ]

    # Only surface stale fan-out labels when there are any (the empty case is the norm).
    if report.open_triggers:
        lines += ["", render_open_triggers(report.open_triggers, report.generated_at).rstrip("\n")]

    lines += _render_agent_signals(report)

    # A green verdict is one line; the full breakdown (and its detail table)
    # appears only when failing — the same body the data-validation escalation
    # issue posts. The monitored counts ride along on the green line too: they
    # never redden a verdict, so a green dashboard is the only place they are
    # ever seen, and gating them behind the failing branch would hide them
    # permanently.
    dh = report.data_health
    if dh is not None:
        if dh.ok:
            lines += ["", "**Data health:** ✅ Healthy."]
            lines += _monitored_lines(dh)
        else:
            lines += ["", render_data_health(dh).rstrip("\n")]

    return "\n".join(lines) + "\n"
