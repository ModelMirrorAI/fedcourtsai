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
from datetime import UTC, datetime, timedelta
from typing import Literal

from .analytics import _GRANT_LABELS
from .collect import flags_table
from .leaderboard import FORWARD, RETROSPECTIVE, Stratum
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
# GitHub Actions standard runners are free on a public repository, so the
# per-minute rate is zero; minutes are still tracked as a runtime-health
# signal. Set a real rate here if the repo ever goes private or moves to
# larger runners.
_ACTIONS_USD_PER_MINUTE = 0.0
# Infra not metered per run: CourtListener Tier 3 ($50) + S3 (~$15), USD/month.
# The S3 line is dominated by internet egress, not storage — GitHub runners are
# Azure-hosted, so the scan-shaped writers' recurring full index pulls (~250-300
# GB/mo at today's ~1 GB blob) carry it just past the free tier. It scales with
# the blob, so revisit this alongside `docs/budget.md` when the index grows.
_FIXED_MONTHLY_USD = 65.0
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
    (success + the failure family — label-filter skips and other non-conclusive
    conclusions excluded), so the rate matches the rendered success fraction and
    the ~1s skip overhead never drags the percentiles.
    """
    by_workflow: dict[str, list[Mapping[str, object]]] = {}
    for run in runs:
        name = run.get("workflowName") or run.get("name") or "?"
        by_workflow.setdefault(str(name), []).append(run)

    health: list[WorkflowHealth] = []
    for workflow, workflow_runs in sorted(by_workflow.items()):
        completed = [r for r in workflow_runs if r.get("status") == "completed"]
        # A skipped run is not an execution: the label-triggered workflows
        # complete a skipped run for every unrelated `issues: labeled` event
        # (the job-level label filter, by design), so counting skips would
        # dilute the rate and drag the duration percentiles toward the ~1s
        # skip overhead. Health reads over the *conclusive* runs only — which
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
    accuracy = round(sum(ev.correct for ev in replay) / len(replay), 4) if replay else None
    briers = [ev.brier_score for ev in replay if ev.brier_score is not None]
    skills = [ev.brier_skill_score for ev in replay if ev.brier_skill_score is not None]
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
        cal_lines.append(f"Mean Brier **{brier}** · accuracy **{accuracy}** (n={cal.sample})")
    if cal.deny_base_rate is not None:
        lift = "—" if cal.lift_over_always_deny is None else f"{cal.lift_over_always_deny:+.1%}"
        cal_lines.append(
            f"Always-deny base rate **{cal.deny_base_rate:.0%}** "
            f"(est. over {cal.base_rate_cases:,} resolved modern-cert petitions, "
            "live/historical slice, denial-reweighted) · "
            f"lift **{lift}**"
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
        skill = (
            ""
            if cal.mean_brier_skill is None
            else f", Brier skill **{cal.mean_brier_skill:+.3f}** vs the segment base rate"
        )
        lines.append(
            f"- **Replay calibration on {cal.sample} scored cell(s): {lift}{skill} — "
            "do you believe it?**"
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
    return "\n".join(lines) + "\n"


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
    gen_dt = _parse_iso(generated_at)
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


def _parse_iso(value: str) -> datetime | None:
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

    starts = [t for r in run_list if (t := _parse_iso(str(r.get("createdAt") or ""))) is not None]
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
    grouped and scoped to a recent window, and a healthy data verdict collapses to a
    single line — the full breakdown appears only on a failing verdict (where
    :func:`render_data_health` is also the escalation-issue body).
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

    # Only surface stalled fan-outs when there are any (the empty case is the norm).
    if report.open_triggers:
        lines += ["", render_open_triggers(report.open_triggers, report.generated_at).rstrip("\n")]

    lines += _render_agent_signals(report)

    # A green verdict is one line; the full breakdown (and its detail table) appears
    # only when failing — the same body the data-validation escalation issue posts.
    dh = report.data_health
    if dh is not None:
        if dh.ok:
            lines += ["", "**Data health:** ✅ Healthy."]
        else:
            lines += ["", render_data_health(dh).rstrip("\n")]

    return "\n".join(lines) + "\n"
