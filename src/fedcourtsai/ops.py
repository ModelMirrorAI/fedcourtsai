"""Operational analytics roll-up: pipeline health, spend, data health.

A *read-only* snapshot of authoritative sources — the GitHub Actions run history,
the recorded usage ledger, and the committed ``flags.json`` files agents leave
under ``data/`` — so no pipeline run has to write an ops record (which would
reintroduce the concurrent-writer problem the corpus already manages).
``fedcourts ops-report`` renders this to Markdown (the run-ops dashboard issue) and
optionally to JSON.

Unlike the deterministic leaderboard / back-test roll-ups, this is a point-in-time
view: it carries ``generated_at`` and run durations, so it is not byte-stable.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from datetime import datetime

from .collect import flags_table
from .leaderboard import RETROSPECTIVE, Stratum
from .schemas import (
    AgentFlags,
    AgentToolingFeedback,
    CostEstimate,
    DataHealth,
    Evaluation,
    FlagsDigest,
    FlagSeverity,
    LeakageDigest,
    LiveFrontier,
    ModelUsage,
    OpenTriggerIssue,
    OpsReport,
    PredictorScoreRow,
    SpendSummary,
    StatPack,
    SubstanceCalibration,
    SubstanceCells,
    SubstanceDigest,
    ToolingCount,
    ToolingDigest,
    WorkflowHealth,
)

# Conclusions that count as a completed-but-not-successful run.
_FAILURE_CONCLUSIONS = frozenset({"failure", "timed_out", "cancelled", "startup_failure"})

# Cost constants, kept in sync with docs/budget.md (the single source for rates).
# GitHub Actions Linux 2-core beyond the included minutes, private repo, USD/min.
_ACTIONS_USD_PER_MINUTE = 0.006
# Infra not metered per run: CourtListener Tier 3 ($50) + S3/DVC (~$5), USD/month.
_FIXED_MONTHLY_USD = 55.0
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
    timestamps. Workflows are returned sorted by name; within each, the success rate
    is over *completed* runs only, and durations come from completed runs whose
    timestamps parse.
    """
    by_workflow: dict[str, list[Mapping[str, object]]] = {}
    for run in runs:
        name = run.get("workflowName") or run.get("name") or "?"
        by_workflow.setdefault(str(name), []).append(run)

    health: list[WorkflowHealth] = []
    for workflow, workflow_runs in sorted(by_workflow.items()):
        completed = [r for r in workflow_runs if r.get("status") == "completed"]
        successes = sum(1 for r in completed if r.get("conclusion") == "success")
        failures = sum(1 for r in completed if r.get("conclusion") in _FAILURE_CONCLUSIONS)
        durations = [s for r in completed if (s := _run_seconds(r)) is not None]
        # "Most recent" by start time; createdAt is ISO-8601 so string order is time order.
        recent = max(workflow_runs, key=lambda r: str(r.get("createdAt") or ""))
        health.append(
            WorkflowHealth(
                workflow=workflow,
                runs_considered=len(workflow_runs),
                successes=successes,
                failures=failures,
                success_rate=(successes / len(completed)) if completed else None,
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
    Term-prefixed discretionary-cert dockets. ``(None, None)`` when the statpack
    or its cert-stage disposition section is absent — the render shows an
    explicit absence rather than anchoring against the wrong population.
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


def _delta(current: int, previous: int | None) -> int | None:
    return None if previous is None else current - previous


def summarize_substance(
    *,
    cell_counts: tuple[int, int, int],
    stratified_evaluations: Sequence[tuple[Evaluation, Stratum]],
    statpack: StatPack | None = None,
    live_frontier: LiveFrontier | None = None,
    previous: OpsReport | None = None,
) -> SubstanceDigest:
    """Roll the committed ledger + metrics artifacts into the substance section.

    Pure over its inputs (no filesystem): the caller supplies the ledger census
    (:func:`fedcourtsai.store.ledger_cell_counts`), the stratified evaluations,
    the committed statpack, and the published live-frontier snapshot. Deltas
    compare against ``previous``'s substance counts and stay null without a
    comparable prior — a missing or pre-substance snapshot degrades the deltas,
    never the section.
    """
    predictions, events_predicted, predicted_resolved = cell_counts
    forward = [ev for ev, stratum in stratified_evaluations if stratum != RETROSPECTIVE]
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
    accuracy = round(sum(ev.correct for ev in replay) / len(replay), 4) if replay else None
    briers = [ev.brier_score for ev in replay if ev.brier_score is not None]
    calibration = SubstanceCalibration(
        sample=len(replay),
        mean_brier=round(sum(briers) / len(briers), 4) if briers else None,
        accuracy=accuracy,
        deny_base_rate=deny_rate,
        base_rate_cases=base_cases,
        lift_over_always_deny=(
            round(accuracy - deny_rate, 4)
            if accuracy is not None and deny_rate is not None
            else None
        ),
    )

    by_predictor: dict[str, list[Evaluation]] = {}
    for ev, _stratum in stratified_evaluations:
        by_predictor.setdefault(ev.predictor_id, []).append(ev)
    scores = []
    for predictor_id in sorted(by_predictor):
        evals = by_predictor[predictor_id]
        quality = [ev.reasoning_quality for ev in evals if ev.reasoning_quality is not None]
        scores.append(
            PredictorScoreRow(
                predictor_id=predictor_id,
                evaluations=len(evals),
                accuracy=round(sum(ev.correct for ev in evals) / len(evals), 4),
                median=_quantile(quality, 0.5),
                p25=_quantile(quality, 0.25),
                p75=_quantile(quality, 0.75),
            )
        )

    return SubstanceDigest(
        cells=cells,
        calibration=calibration,
        predictor_scores=scores,
        live_frontier=live_frontier,
    )


def _fmt_delta(delta: int | None) -> str:
    """A signed week-over-week suffix, empty without a comparable prior."""
    return "" if delta is None else f" ({delta:+d})"


def render_substance(digest: SubstanceDigest) -> str:
    """Render the substantive-results section: is the machine producing?

    Every number that can be small carries its sample size beside it, and a
    feed that has not landed renders as an explicit absence — an empty view is
    itself the signal the instrument is not producing yet.
    """
    c = digest.cells
    lines = [
        "## Substance (is it producing?)",
        "",
        f"Prediction cells committed: **{c.predictions}**{_fmt_delta(c.predictions_delta)} "
        f"over **{c.events_predicted}** event(s); predicted events resolved: "
        f"**{c.predicted_resolved}**{_fmt_delta(c.predicted_resolved_delta)}; scored cells: "
        f"**{c.evaluations_forward}** forward{_fmt_delta(c.evaluations_forward_delta)} · "
        f"**{c.evaluations_retrospective}** replay"
        f"{_fmt_delta(c.evaluations_retrospective_delta)}.",
    ]

    cal = digest.calibration
    lines += ["", "**Calibration (replay stratum, advisory)**"]
    if cal.sample == 0:
        lines.append("_No scored replay cells yet._")
    else:
        brier = "—" if cal.mean_brier is None else f"{cal.mean_brier:.3f}"
        accuracy = "—" if cal.accuracy is None else f"{cal.accuracy:.0%}"
        lines.append(f"Mean Brier **{brier}** · accuracy **{accuracy}** (n={cal.sample})")
    if cal.deny_base_rate is None:
        lines.append("_Deny base rate unavailable (no modern-cert statpack section yet)._")
    else:
        lift = "—" if cal.lift_over_always_deny is None else f"{cal.lift_over_always_deny:+.1%}"
        lines.append(
            f"Always-deny base rate **{cal.deny_base_rate:.0%}** "
            f"(over {cal.base_rate_cases:,} resolved modern-cert petitions) · "
            f"lift **{lift}**"
        )

    lines += ["", "**Evaluation scores by predictor** (reasoning quality, all strata pooled)"]
    if not digest.predictor_scores:
        lines.append("_No evaluations committed yet._")
    else:
        lines += [
            "| Predictor | Cells | Accuracy | Median | p25-p75 |",
            "|-----------|------:|---------:|-------:|---------|",
        ]
        for row in digest.predictor_scores:
            accuracy = "—" if row.accuracy is None else f"{row.accuracy:.0%}"
            median = "—" if row.median is None else f"{row.median:.2f}"
            spread = "—" if row.p25 is None or row.p75 is None else f"{row.p25:.2f}-{row.p75:.2f}"
            lines.append(
                f"| {row.predictor_id} | {row.evaluations} | {accuracy} | {median} | {spread} |"
            )

    lines += ["", "**Live frontier**"]
    frontier = digest.live_frontier
    if frontier is None or frontier.skipped:
        lines.append("_No published watchlist snapshot yet._")
    else:
        upcoming = (
            f"next conference **{frontier.next_conference}** "
            f"({frontier.next_conference_petitions} petition(s))"
            if frontier.next_conference is not None
            else "no upcoming conference scheduled"
        )
        lines.append(
            f"Watchlist **{frontier.watchlist}** petition(s) · {upcoming} · "
            f"documents provisioned on **{frontier.documents_provisioned}/{frontier.watchlist}**"
        )
    return "\n".join(lines) + "\n"


def render_weekly_digest(report: OpsReport) -> str:
    """The weekly maintainer digest: fixed questions with this week's answers.

    Deliberately short and interrogative — the numbers demand a reaction rather
    than sit available for inspection; the daily dashboard stays the reference
    view. Renders from whatever the report holds, with explicit absences.
    """
    substance = report.substance
    lines = ["### Weekly digest", ""]

    if substance is not None and substance.calibration.sample:
        cal = substance.calibration
        lift = (
            "lift unavailable (no base rate)"
            if cal.lift_over_always_deny is None
            else f"lift **{cal.lift_over_always_deny:+.1%}** over always-deny"
        )
        lines.append(
            f"- **Replay calibration on {cal.sample} scored cell(s): {lift} — do you believe it?**"
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
        lines.append(f"- **Forward cells scored: {weekly} — is the live frontier producing?**")
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
            f"- **Oldest stalled trigger: `{oldest.label}` "
            f"({_age(oldest.created_at, report.generated_at)} old) — why is it still open?**"
        )
    else:
        lines.append("- **Stalled triggers: none — every fan-out landed or closed.**")

    monthly = (
        "—"
        if report.cost.estimated_monthly_usd is None
        else f"${report.cost.estimated_monthly_usd:,.0f}/mo"
    )
    lines.append(
        f"- **Spend vs budget: ${report.spend.estimated_cost_usd:,.2f} model spend cumulative, "
        f"~{monthly} projected — within plan?**"
    )
    return "\n".join(lines) + "\n"


def summarize_spend(usage: Iterable[ModelUsage]) -> SpendSummary:
    """Roll the recorded usage ledger up into total tokens + estimated cost."""
    rows = list(usage)
    runs = len(rows)
    cost = sum(r.estimated_cost_usd for r in rows)
    tokens = sum(
        r.input_tokens + r.output_tokens + r.cache_read_input_tokens + r.cache_creation_input_tokens
        for r in rows
    )
    return SpendSummary(
        runs=runs,
        total_tokens=tokens,
        estimated_cost_usd=round(cost, 6),
        mean_cost_usd_per_run=round(cost / runs, 6) if runs else 0.0,
    )


# How many of the most recent flag-raising cells the dashboard table lists; the
# severity counts still cover every committed flag, so the cap never hides volume.
_FLAGS_RECENT_LIMIT = 20

# How many `likely` leakage gradings the dashboard names individually.
_LEAKAGE_FLAGGED_LIMIT = 20


def summarize_leakage(
    evaluations: Iterable[Evaluation], *, limit: int = _LEAKAGE_FLAGGED_LIMIT
) -> LeakageDigest:
    """Roll the evaluators' leakage gradings into the dashboard's leakage digest.

    The visibility half of the backtest-as-iteration doctrine: counts over every
    committed ``evaluation.json`` that carries a ``leakage`` block, with the
    ``likely`` offenders named (newest first, capped) so a repeat pattern is
    attributable to its predictor rather than lost in a count.
    """
    assessed = not_applicable = none = possible = likely = 0
    flagged: list[tuple[str, str]] = []
    for evaluation in evaluations:
        if evaluation.leakage is None:
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
    )


def summarize_flags(
    flag_sets: Iterable[AgentFlags], *, limit: int = _FLAGS_RECENT_LIMIT
) -> FlagsDigest:
    """Roll committed ``flags.json`` sets into the dashboard's open-flags digest.

    Severity counts are over *every* flag supplied; ``recent`` keeps the most recent
    flag-raising cells (by run id, newest first) capped at ``limit``, so a long
    history never bloats the dashboard while the counts still report the true volume.
    """
    sets = list(flag_sets)
    counts = {FlagSeverity.blocker: 0, FlagSeverity.warning: 0, FlagSeverity.info: 0}
    for fs in sets:
        for flag in fs.flags:
            counts[FlagSeverity(flag.severity)] += 1
    # Run ids are UTC timestamps, so descending lexical order is newest-first.
    recent = sorted(sets, key=lambda fs: (fs.run_id, fs.case_id, fs.actor_id), reverse=True)[:limit]
    return FlagsDigest(
        total=sum(counts.values()),
        cells=len(sets),
        blockers=counts[FlagSeverity.blocker],
        warnings=counts[FlagSeverity.warning],
        infos=counts[FlagSeverity.info],
        recent=recent,
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
    recent_limit: int = _TOOLING_RECENT_LIMIT,
    items_limit: int = _TOOLING_ITEMS_LIMIT,
) -> ToolingDigest:
    """Roll committed ``tooling.json`` self-reports into the dashboard's tooling digest.

    ``corpus_query_uses`` / ``base_rate_uses`` of ``reports`` cells used the query and
    base-rate ``stats`` CLIs; ``helpful`` /
    ``gaps`` rank the most-mentioned abilities and missing tools across every report;
    ``recent`` keeps the latest few full reports (by run id, newest first) for detail.
    """
    items = list(reports)
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
    )


def _parse_iso(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def estimate_cost(runs: Iterable[Mapping[str, object]], spend: SpendSummary) -> CostEstimate:
    """Rough monthly cost run-rate from run durations + recorded spend + fixed infra.

    GitHub Actions cost is estimated from completed-run wall-clock x the per-minute
    rate and projected to 30 days from the span of the observed runs (no billing-API
    access needed); the fixed monthly infra is added. Model token cost is reported
    cumulatively (not a rate), so it is shown but not added into the projection.
    """
    run_list = list(runs)
    seconds = [s for r in run_list if (s := _run_seconds(r)) is not None]
    actions_minutes = sum(seconds) / 60.0
    actions_cost = actions_minutes * _ACTIONS_USD_PER_MINUTE

    starts = [t for r in run_list if (t := _parse_iso(str(r.get("createdAt") or ""))) is not None]
    window_days = (max(starts) - min(starts)).total_seconds() / 86400.0 if len(starts) > 1 else None
    actions_monthly = (
        actions_cost / window_days * _DAYS_PER_MONTH if window_days and window_days > 0 else None
    )
    estimated_monthly = (
        round((actions_monthly or 0.0) + _FIXED_MONTHLY_USD, 2)
        if actions_monthly is not None
        else None
    )
    return CostEstimate(
        window_days=round(window_days, 1) if window_days is not None else None,
        actions_minutes=round(actions_minutes, 1),
        actions_cost_usd=round(actions_cost, 4),
        actions_monthly_usd=round(actions_monthly, 2) if actions_monthly is not None else None,
        model_cost_usd=spend.estimated_cost_usd,
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
        flags=summarize_flags(flags),
        leakage=summarize_leakage(evaluations),
        tooling=summarize_tooling(tooling),
        open_triggers=open_triggers,
    )


def _fmt_duration(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    minutes, secs = divmod(seconds, 60)
    return f"{minutes}m{secs:02d}s" if minutes else f"{secs}s"


# The run:* labels whose trigger issues are transient by design: the run's ready
# PR closes them on merge, and an empty matrix closes them with a note. (run:pull
# issues are long-lived logs, so they are not stall signals.)
TRIGGER_LABELS: tuple[str, ...] = ("run:predict", "run:evaluate")


def summarize_trigger_issues(raw: Iterable[Mapping[str, object]]) -> list[OpenTriggerIssue]:
    """Normalize a ``gh issue list --json number,title,labels,createdAt`` feed.

    Keeps only issues carrying one of :data:`TRIGGER_LABELS` (the transient
    fan-out triggers), oldest first — the ones that have sat longest lead. The
    feed shape is gh's: ``labels`` is a list of ``{"name": ...}`` objects.
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
    """Render the open-trigger-issues section: the stalled fan-outs, oldest first.

    An open trigger issue means a run that never landed — failed wholesale,
    produced nothing, or was never picked up. Empty gets a one-line all-clear so
    a healthy dashboard still shows the check ran.
    """
    if not issues:
        return "## Open trigger issues\n\n_None — every fan-out landed or closed._\n"
    lines = [
        "## Open trigger issues",
        "",
        f"**{len(issues)}** open `run:*` trigger issue(s) — a stalled fan-out until "
        "its run lands (re-fire by removing and re-applying the label).",
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

    # A check that passed but counted non-zero failures is a known condition held
    # within an accepted baseline (e.g. case_dates_ordered). Surface it so the
    # count stays visible — the verdict is green, but the monitor still reads it.
    monitored = (
        [c for c in corpus_v.checks if c.passed and c.failures]
        if corpus_v is not None and not corpus_v.skipped
        else []
    )
    if monitored:
        lines += ["", "_Monitored (within accepted baselines):_"]
        lines += [f"- {c.name}: {c.detail}" for c in monitored]

    return "\n".join(lines) + "\n"


def render_leakage_digest(digest: LeakageDigest) -> str:
    """The dashboard's leakage section: is outcome material tainting iteration signal?"""
    lines = [
        "## Leakage grading (evaluator, advisory)",
        f"{digest.assessed} assessed · {digest.not_applicable} forward (n/a) · "
        f"{digest.none} clean · {digest.possible} possible · **{digest.likely} likely**",
    ]
    if digest.flagged:
        lines.append("")
        lines += [f"- {label}" for label in digest.flagged]
    elif digest.assessed == 0:
        lines.append("")
        lines.append("_No leakage assessments committed yet._")
    return "\n".join(lines) + "\n"


def render_flags_digest(digest: FlagsDigest) -> str:
    """Render the dashboard's open-agent-flags section from the digest.

    Leads with the severity breakdown over every committed flag, then lists the most
    recent flag-raising cells using the same table the per-run roll-up renders
    (:func:`fedcourtsai.collect.flags_table`). A healthy ledger gets a one-line note
    instead of an empty table.
    """
    if digest.total == 0:
        return "## Agent flags\n\n_No agent flags on record._\n"
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
        "## Agent flags",
        "",
        f"**{digest.total}** flag(s) across **{digest.cells}** cell(s) — {breakdown}{note}.",
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
    if digest.reports == 0:
        return "## Agent tooling feedback\n\n_No tooling reports on record._\n"
    query_share = f"{digest.corpus_query_uses}/{digest.reports}"
    base_rate_share = f"{digest.base_rate_uses}/{digest.reports}"
    lines = [
        "## Agent tooling feedback",
        "",
        f"**{digest.reports}** self-report(s) — corpus-query CLI used by **{query_share}**, "
        f"base-rate `stats` by **{base_rate_share}**. "
        "What agents say helped and what they wished they had.",
    ]
    if digest.helpful:
        lines += ["", "**Most helpful**", *[_tooling_item_line(i) for i in digest.helpful]]
    if digest.gaps:
        lines += ["", "**Wished-for / missing**", *[_tooling_item_line(i) for i in digest.gaps]]
    return "\n".join(lines) + "\n"


def render_markdown(report: OpsReport) -> str:
    """Render the dashboard body posted to the run-ops issue / step summary."""
    lines: list[str] = [
        "# Ops dashboard",
        "",
        f"_Generated {report.generated_at}._",
        "",
        "## Pipeline health",
    ]
    if report.health:
        lines += [
            "| Workflow | Last | Success rate | Failures | Median | p95 |",
            "|----------|------|-------------:|---------:|-------:|----:|",
        ]
        for h in report.health:
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
    else:
        lines.append("_No runs in the window._")

    if report.substance is not None:
        lines += ["", render_substance(report.substance).rstrip("\n")]

    s = report.spend
    lines += [
        "",
        "## Spend (model usage)",
        f"**{s.runs}** run(s) · **{s.total_tokens:,}** tokens · "
        f"**${s.estimated_cost_usd:,.2f}** est. (~${s.mean_cost_usd_per_run:.4f}/run)",
    ]

    ce = report.cost
    monthly = "—" if ce.estimated_monthly_usd is None else f"${ce.estimated_monthly_usd:,.0f}/mo"
    actions_monthly = (
        "—" if ce.actions_monthly_usd is None else f"${ce.actions_monthly_usd:,.0f}/mo"
    )
    lines += [
        "",
        "## Cost run-rate (estimated)",
        f"**~{monthly}** projected · Actions {actions_monthly} "
        f"({ce.actions_minutes:,.0f} min ~ ${ce.actions_cost_usd:,.2f} over "
        f"{'—' if ce.window_days is None else f'{ce.window_days:g}d'}) · "
        f"fixed ${ce.fixed_monthly_usd:,.0f}/mo · model ${ce.model_cost_usd:,.2f} cumulative",
        "",
        "> Rough estimate at the `docs/budget.md` rates (Actions from run durations, "
        "no billing-API access); check the provider billing dashboards for ground truth.",
    ]

    if report.open_triggers is not None:
        lines += ["", render_open_triggers(report.open_triggers, report.generated_at).rstrip("\n")]

    if report.flags is not None:
        lines += ["", render_flags_digest(report.flags).rstrip("\n")]

    if report.leakage is not None:
        lines += ["", render_leakage_digest(report.leakage).rstrip("\n")]

    if report.tooling is not None:
        lines += ["", render_tooling_digest(report.tooling).rstrip("\n")]

    if report.data_health is not None:
        lines += ["", render_data_health(report.data_health).rstrip("\n")]

    return "\n".join(lines) + "\n"
